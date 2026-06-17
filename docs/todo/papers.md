# Papers Todo: Reference and Specification Gaps

This list tracks mismatches discovered while reviewing the local `papers/`
directory and using the AlphaEvolve paper as the primary specification.

## AlphaEvolve Paper Requirements Not Yet Implemented

- [ ] Add semantic evidence mapping for every paper-index status row.
  - Paper evidence: `papers/README.md` is the paper-facing implementation
    status index for the local cache, and AlphaEvolve-alignment work depends on
    each source row separating implemented behavior, background context, and
    missing reproduction evidence.
  - Current evidence: `libreevolve.tools.paper_manifest` validates manifest
    row identity, status-table shape, role/status taxonomy, local path
    references, TODO coverage rows, completed-evidence paths, and stale
    source-specific absence wording for a narrow phrase family. The papers
    README now warns that the implementation-status table is a maintained
    index, not a proof ledger for every long status-cell sentence. The same
    validator also catches one narrow benchmark-coverage contradiction: an
    `Implemented` benchmark bullet phrased as not implemented. The committed
    `papers/status_claim_inventory.json` now records one checked row per
    implementation-status table row with row ids, role/status class, status
    text hashes, row source lines, manifest-file links, local artifact mention
    source offsets, active/completed TODO evidence path source offsets, and
    143 status-cell phrase hashes with source-line and character offsets plus
    candidate evidence-link lists. It now records 60 unique status-row local artifact
    paths, 60 row-level artifact mention records, 60 phrase-level artifact
    mention records, and zero missing referenced status-row local artifacts,
    plus 6 unique status-row TODO evidence paths, 289 TODO evidence path
    mention records, and zero missing referenced TODO evidence paths. It also
    records row-specific TODO content evidence with 175 matched source tokens,
    950 row-specific TODO block hashes/source offsets, 291 artifact mention
    source-offset records, zero status-row local artifact paths, and zero
    status-phrase local artifact paths missing from linked TODO evidence, plus
    286 phrase-level TODO block records. It now structurally classifies 87 status-cell
    absence-signal phrases with 99 source-offset records without claiming
    freshness verification.
    `papers/benchmark_coverage_inventory.json` now records 83 implemented
    benchmark coverage bullets with source lines, file character offsets,
    summary/body hashes, local artifact mention source offsets, local artifact
    existence records, 116
    unique local artifact paths, zero missing referenced local artifacts,
    source-token match file offsets for 3 manifest source IDs across 15
    records, limitation-signal term file offsets/counts, and contradiction flags.
    The committed
    `papers/implementation_evidence_map_boundary.json` now explicitly preserves
    missing evidence for status-cell semantic verifier, implemented-benchmark
    bullet semantic verifier, and absence-sentence freshness matrix.
    `papers/documentation_claim_inventory.json` now adds top-level papers-index
    claim anchors with file-offset source spans for the local paper-cache
    manifest scope and the implementation-status table scope, records local
    evidence-ref existence plus Markdown fragment-anchor resolution for those
    anchors, and records audited README, ROADMAP, and papers-index Markdown
    headings plus uncovered heading-to-claim gaps with active TODO-owner links,
    while explicitly keeping row-level semantic proof out of scope.
  - Current gap: each status phrase now has a stable hash and source offset,
    candidate links to phrase-local artifacts plus row-level TODO and completed
    evidence, referenced local artifact/TODO path existence checks, local
    artifact mention source offsets, TODO evidence path source offsets,
    matched TODO content source tokens, row-specific TODO block hashes/source
    offsets, phrase-level TODO block records, absence-signal source offsets,
    and row-local and phrase-local artifact mention source offsets in linked
    TODO evidence, but
    there is no proof that those links are sufficient for each implemented or
    missing clause, no semantic verifier for
    `Implemented` benchmark coverage bullets beyond referenced source-token
    match offsets, artifact mention/existence/source-offset records, no absence-sentence freshness
    matrix beyond structural signal source-offset classification, and no
    semantic verifier that checks benchmark qualifiers, implemented-bullet
    scope/limitation semantics beyond structural signal terms and source
    offsets, or absence sentences against the current code and paper evidence.
  - Required result: extend the phrase-level inventory with evidence-sufficiency
    checks, freshness checks, and benchmark-coverage semantic checks, then add
    CI validation before treating `papers/README.md` as semantically complete
    implementation-status or benchmark-coverage proof.

- [ ] Add anchor-level semantic validation for paper-index TODO coverage rows.
  - Paper evidence: `papers/README.md` uses the TODO coverage cross-reference
    table as backlog traceability between every local paper-cache row and the
    active or completed work that keeps implementation-status claims honest.
    For AlphaEvolve-alignment work, that table should prove row-specific
    disposition, not merely that a broad TODO file contains some related open
    work.
  - Current evidence: `validate_paper_manifest()` checks the TODO coverage
    table shape, manifest-id row coverage, duplicate rows, active TODO file
    paths, completed-ledger paths with checklist evidence, and a narrow stale
    source-specific absence phrase family. The prose explicitly says grouped
    labels are intentionally not accepted until a grouped-label taxonomy
    exists, and that the table is backlog traceability evidence rather than
    semantic proof.
  - Current gap: active coverage cells still cite only broad files such as
    `docs/todo/code.md` and `docs/todo/papers.md`, not exact row-specific TODO
    anchors, gap categories, status classes, or source-span dispositions. The
    validator does not prove that each cited active ledger contains a current
    open block specifically about that paper row, that completed evidence
    addresses the same status-cell clauses, that broad file-level coverage is
    not hiding missing source-specific work, or that a changed paper role,
    implementation status, benchmark qualifier, or source-span claim forces a
    row-specific TODO coverage refresh.
  - Required result: extend the paper-index TODO coverage map with stable
    active/completed anchor ids, source-specific gap categories, role/status
    expectations, and optional grouped-label taxonomy; validate that every
    paper row's cited TODO anchors are live, row-specific, semantically aligned
    with its implementation-status clauses, and refreshed when paper status,
    benchmark coverage, or source-span evidence changes.

- [ ] Track independent evaluator-oracle evidence beyond local arbitration
      metadata.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` states that AlphaEvolve
    iteratively improves algorithms by continuously receiving feedback from one
    or more evaluators, then Section 2.4 distinguishes the user-provided
    evaluation function from optional cascades and LLM-generated feedback.
  - Partial status: completed manifests now include
    `runtime.history.evaluator_oracle_registry` with evaluator ids, oracle
    type, authority, input/output schema, metric ownership, failure policy,
    prompt-feedback linkage, runtime counts, merge-policy metadata, and an
    `arbitration_policy` authority matrix for the default validator or
    configured cascade stages plus optional LLM feedback graders. The matrix
    labels each oracle's benchmark sufficiency, conflict role, failure effect,
    independent-evidence flag, and reference/statistical-oracle status.
    `oracle_source_evidence` now validates local evaluator source refs and
    hashes when available while keeping benchmark sufficiency and independence
    false.
    `disagreement_outcomes` now records bounded local
    validator-versus-feedback outcomes, including feedback discards after an
    evaluator pass, final local validity effects, and an explicit
    post-evaluator/non-independent authority boundary. The committed
    `papers/evaluator_oracle_boundary.json` sidecar now preserves the
    paper-manifest-validated independent-oracle absence boundary, including
    missing candidate-level oracle lineage, per-generation feedback traces,
    primary evaluator contract proof, and explicit separation between the
    primary evaluator contract and optional post-evaluator LLM feedback.
  - Current gap: the registry preserves current composition and local source
    reference evidence, but it does not prove multiple independent evaluator/
    oracle sources, reference/statistical oracle support, candidate-level
    oracle lineage through the evolutionary loop, per-benchmark sufficiency
    evidence, or independent disagreement outcomes that affect validity, score
    reporting, database admission, and prompt-visible feedback.
  - Required result: add independent evaluator-oracle evidence before claiming
    AlphaEvolve-style "one or more evaluators" feedback: reference/statistical
    oracle support, per-benchmark sufficiency labels, candidate-generation
    oracle lineage, primary evaluator contract proof, disagreement outcome
    records, and wording that separates independent evaluator composition from
    local cascade stages or post-evaluation LLM graders.

- [ ] Track independent audit rates for execution-grounded filtering of
      incorrect base-LLM suggestions.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Introduction and Table 1 context.
  - Requirement: AlphaEvolve says code execution and automatic evaluation
    ground the LLM-directed evolution process, allowing the system to avoid
    incorrect suggestions from the base LLM and use feedback to move beyond
    the initial candidate pool.
  - Partial status: completed manifests now include
    `runtime.history.proposal_lifecycle_report` with schema
    `libreevolve.proposal_lifecycle_report.v1`. Completed manifests also
    include `runtime.history.incorrect_suggestion_audit_report` with schema
    `libreevolve.incorrect_suggestion_audit_report.v1`. The reports connect
    generated proposals through backend/call summaries, mutation hashes,
    execution/evaluator validity, archive admission or rejection, rejection
    reasons, execution-filtered counts, invalid-evaluation and
    archive-rejected counts, local filter rates, failure-memory linkage,
    aggregate zero-coverage independent-rejudge summaries,
    false-acceptance/false-rejection audit absence, and claim-readiness
    checks. The committed
    `papers/proposal_lifecycle_audit_boundary.json` sidecar preserves the
    paper-manifest-validated independent-audit absence boundary, including
    missing sampled audit-denominator policy, candidate-family filter rates,
    and beyond-initial-pool novelty audit. The committed
    `papers/incorrect_suggestion_audit_boundary.json` sidecar now preserves
    the more specific local-execution-grounding boundary for the incorrect-
    suggestion audit report with the same audit-denominator and novelty
    boundary.
  - Current gap: these reports are local run evidence with explicit zero
    independent-rejudge coverage. They do not independently rejudge accepted
    or rejected proposals, prove
    benchmark-specific evaluator-oracle sufficiency, aggregate cross-run
    proposal tables, stratify false-filter rates by candidate family, audit
    movement beyond the initial pool, define a sampled audit denominator, or
    report audited false-acceptance/false-rejection rates.
  - Required result: add independent rejudge/reference-checker or statistical
    oracle evidence for accepted and rejected proposals, cross-run proposal
    lifecycle tables, semantic failed-proposal retrieval, benchmark-specific
    oracle sufficiency labels, candidate-family false-filter rates,
    beyond-initial-pool novelty audit, sampled audit denominator policy, and
    audited false-acceptance/false-rejection rates before describing
    LibreEvolve as publication-strength
    AlphaEvolve-style grounded against incorrect base-LLM suggestions.

- [ ] Track evaluation-cascade promotion and attrition evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4 and the matrix-
    multiplication experiment.
  - Requirement: AlphaEvolve's cascade lets users specify test-case ensembles
    of increasing difficulty, promotes candidates only after sufficiently
    promising earlier-stage results, prunes less promising candidates quickly,
    applies small-scale checks before main tests, and uses multiple random
    seeds for matrix-multiplication evaluation.
  - Partial status: LibreEvolve supports local staged validators with
    thresholds, metric thresholds, samples, retries, seeds, budgets,
    artifact/output checks, per-candidate
    `evaluation.metadata.configured_stage_results`, and a runtime
    `libreevolve.evaluation_cascade_report.v1` summary under
    `runtime.history.evaluation_cascade_report`. The report aggregates
    configured candidate count, per-stage entry/pass/fail/threshold-fail
    counts, failure reasons, sample/retry/subprocess/timeout totals, elapsed
    seconds, promotion rates, main-test exposure, early-prune counts, and
    claim-readiness limitations. It now also records bounded
    `candidate_stage_records` with `history.jsonl` metadata paths, evaluator
    source refs when available, a denominator policy for runtime candidate,
    stage-entry, main-test exposure, and early-prune populations, and explicit
    denominator overclaim validation. It also records a
    `stage_evidence_summary` with role/source/hash/sample/exposure counts and
    explicit absent-evidence statuses. The committed
    `papers/evaluation_cascade_boundary.json` sidecar now preserves the
    paper-manifest-validated cascade-efficiency absence boundary, including
    missing candidate transition matrix, promotion-decision rule attribution,
    next-stage exposure linkage, and transition-denominator reconciliation.
  - Current gap: paper-facing evidence still lacks stage difficulty or scale
    rationale, evaluator/test-set identities and hashes, benchmark seed/sample
    policy, candidate-by-candidate transition proof from each small-filter
    decision to next-stage exposure or prune outcome, transition denominator
    reconciliation, and counterfactual cost/wall-clock savings; the new summary
    records those absences explicitly. The report therefore remains
    `claim_ready: false` for AlphaEvolve cascade-efficiency claims.
  - Required result: finish cascade-report artifacts and validators with stage
    difficulty/test-set metadata, random-seed/sample coverage beyond the
    runtime denominator policy, candidate transition matrix with
    promotion/prune rule attribution and next-stage linkage, cost summaries,
    and claim-readiness checks.

- [ ] Track explicit controller backtracking policy beyond observed redirect
      evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Introduction and Section 2.4.
  - Requirement: AlphaEvolve frames scientific/program discovery as ideation,
    exploration, backtracking on unpromising hypotheses, experimentation, and
    validation, with cascades pruning less-promising solutions before larger
    budget is spent.
  - Partial status: completed manifests now include
    `runtime.history.hypothesis_branch_report` with schema
    `libreevolve.hypothesis_branch_report.v1`. The report groups generated
    candidates by captured proposal text hashes and records branch ids,
    proposal-field summaries, explored candidate ids, accepted/rejected/
    execution-filtered counts, evaluator/cascade evidence, abandonment reason,
    inferred fallback parent targets, prompt/failure-memory linkage,
    suppression/retry policy status, resumed-search outcome status, and
    claim-readiness validation.
    Completed manifests also include
    `runtime.history.controller_backtracking_report` with schema
    `libreevolve.controller_backtracking_report.v1`, which records current-run
    branch state transitions and observed redirects from abandoned-looking
    branches to a later fallback parent or alternative branch. The committed
    `papers/controller_backtracking_boundary.json` sidecar now preserves the
    paper-manifest-validated controller-policy absence boundary, including
    missing unpromising-decision rules/thresholds, controller branch-state
    machine, and prompt-sampling suppression effects.
  - Current gap: these reports are evidence of abandoned-looking branches and
    observed redirects, not proof that the controller deliberately backtracked
    under a configured policy. They still lack suppression/retry events,
    unpromising-branch decision thresholds, explicit fallback-target
    selection, prompt-visible sampling suppression, causal resumed-search
    proof, and cross-run branch tables.
  - Required result: add controller-owned backtracking policy reports with
    configured suppression/retry behavior, unpromising decision rules and
    thresholds, explicit fallback target selection, prompt-sampling suppression
    effects, causal resumed-search outcomes, and replayable validation before
    using AlphaEvolve-style backtracking wording without qualification.

- [ ] Extend candidate-embedded evaluator reports into full Figure 3 parity.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and Figure 3.
  - Requirement: AlphaEvolve's example codebase contains an
    `evaluate(eval_inputs) -> dict[str, float]` function that invokes the
    evolved skeleton and returns the scores for the generated program. In the
    local PDF, page 4 describes the evaluator as a Python `evaluate` function
    with a fixed input/output signature, and Figure 3 on page 6 says the
    evaluators invoke the Figure 3(a) `evaluate` function to score the modified
    program.
  - Partial status: LibreEvolve records structured results from problem-local
    validators, validates direct evaluator entrypoint provenance, enforces
    problem-local validator dependency policy, can import candidate modules
    from external validators, and supports an opt-in
    `eval_stages[].mode: embedded_evaluate` path. Embedded stages import the
    materialized candidate primary file, discover a one-argument
    `evaluate(eval_inputs)` callable, invoke it with JSON-safe configured
    inputs, validate returned metrics, and record candidate callable plus
    eval-input provenance. Embedded candidate-local reads/imports are now
    runtime-enforced against the materialized candidate file manifest.
    Completed manifests now include
    `runtime.history.embedded_evaluator_entrypoint_report` with schema
    `libreevolve.embedded_evaluator_entrypoint_report.v1`, summarizing executed
    embedded entrypoints, dependency scope, eval-input provenance, metric
    names, static primary-file invocation traces from `evaluate()` through
    EVOLVE-block-backed local functions when AST evidence is present, and
    readiness gaps. Mixed-stage manifests also summarize external-validator
    stage metric visibility under a non-causal score-linkage policy.
  - Current gap: paper-facing evidence now covers embedded-only problem
    loading, static score-field mapping back to specific evolved code paths
    for supported candidate-owned `evaluate` returns, and static local
    skeleton-to-evolved-block invocation paths for direct-name function calls.
    It still lacks default candidate-owned evaluator loading as the primary
    problem contract, Figure 3 codebase fixture identity, typed eval-input
    contracts beyond JSON-safe config provenance, build/runtime isolation
    beyond the local subprocess plus workspace guard, non-static score
    causality, and external-validator causal score linkage. External
    `validate.py` remains the default problem format outside all-embedded
    configs. The committed `papers/embedded_evaluator_boundary.json` sidecar
    now preserves missing default candidate-owned evaluator loading, Figure 3
    codebase fixture identity, eval-input type contracts, build isolation,
    non-static score causality, external-validator causal score linkage, and
    prompt/response exhibit artifacts.
    The task-input surface is narrower than this Figure 3 wording can imply:
    embedded stages only receive JSON-safe configured `eval_inputs` whose raw
    value is hashed/not retained, while external validator stdin provenance
    still marks generated input as unsupported and interactive input as either
    unsupported or a configured fixture-text hash. There is no generated-input
    stream, replayable generated-input artifact, interactive task-input capture
    policy, or typed input schema that unifies embedded and external evaluator
    stages.
  - Required result: make candidate-owned `evaluate(eval_inputs)` the
    first-class/default Figure 3 problem contract, or add a paper-facing
    all-embedded fixture with source identity, typed eval-input schema,
    generated/interactive task-input replay policy,
    skeleton-to-evolved-block invocation proof, per-score causal attribution,
    build/runtime isolation, and prompt/response exhibit artifacts before
    treating local validator execution as AlphaEvolve Figure 3 evaluator
    parity.

- [ ] Parallelized evaluation and asynchronous throughput.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: expensive evaluations can be parallelized, and the whole
    pipeline runs as an async controller with LLM samplers and evaluation
    nodes. Section 2.4 also frames parallel evaluation as a way to keep
    generation feedback fast enough for several consecutive mutations rather
    than stalling evolutionary depth behind slow evaluator wall-clock time.
  - Partial status: `proposals_per_generation` can now create, evaluate,
    reward, and log multiple sequential sibling candidates inside one
    generation with per-proposal batch metadata and deterministic ids.
    Configured evaluator stages can also set `sample_workers` above `1` to run
    planned stage samples through a local thread pool with deterministic
    sample-index result order and manifest topology evidence scoped to
    configured-stage sample workers. Candidate evaluation metadata and the
    process-exhibit evaluator-pool record now preserve observed local
    wall-clock compression from those sample workers when present.
    Completed manifests also include
    `libreevolve.parallel_evaluation_readiness_report.v1`, which aggregates
    configured local sample-worker fan-out, observed sample-execution
    compression, topology linkage, and explicit false readiness for
    100-compute-hour candidate budgets, generation-cadence preservation under
    slow feedback, per-candidate compute-hour budgets, async evaluator queues,
    distributed evaluator nodes, mutation-chain-depth impact, and pending-work
    resume.
    `papers/parallel_evaluation_readiness_boundary.json` now preserves the
    same paper-facing absence boundary for manifest validation, including the
    paper's explicit order-of-100-compute-hours evaluator budget and
    consecutive-mutation cadence requirement.
    Completed manifests also embed
    `libreevolve.controller_state_validation.v1` to verify the current
    controller boundary is terminal, synchronous, and drained rather than an
    async queue checkpoint.
  - Current gap: `evolve()` is still synchronous and evaluates one candidate at
    a time; local stage sample workers are not async LLM sampler queues,
    candidate-level async evaluator queues, queue-capacity/backpressure
    policy, distributed evaluator nodes, deterministic async result merge and
    archive-admission order, concurrency-safe database/archive/prompt/plugin/
    budget mutation, or explicit mutation-chain-depth policy for
    expensive/slow-feedback evaluations. Sequential sibling proposal batches
    are accounting evidence, not AlphaEvolve-style throughput depth.
  - Required result: add paper-visible parallel-evaluation reports and
    validators that record per-candidate compute-hour budget, wall-clock
    duration, evaluator-worker fan-out, explicit order-of-100-compute-hours
    budget capability, generation cadence under slow feedback, randomized-
    initialization shard counts/seeds, queued/running/completed evaluator-node
    state, concurrent LLM sampler queue state, queue capacity/backpressure
    decisions, deterministic result merge/admission order, concurrency-safe
    shared-state mutation evidence, cluster or local fallback identity,
    mutation-chain-depth impact, and resumed pending-work behavior before
    treating LibreEvolve's
    synchronous evaluator loop or sequential sibling batches as
    AlphaEvolve-style parallelized evaluation evidence.

- [ ] Track distributed-pipeline topology evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: AlphaEvolve's implementation is an asynchronous pipeline made
    of a controller, LLM samplers, and evaluation nodes; computations can run
    concurrently, block on unfinished dependencies, and the pipeline is
    optimized for throughput rather than individual-operation latency.
  - Partial status: LibreEvolve persists terminal controller-state summaries
    and controller-budget events. The current manifest state explicitly says
    `terminal_synchronous_controller_drained`,
    `single_process_serial_loop`, zero queued/running proposals and
    evaluations, zero in-flight LLM calls, and limitations including
    `synchronous_terminal_snapshot_not_async_queue_checkpoint`. Completed
    manifests now also include
    `runtime.history.distributed_pipeline_topology_report` with schema
    `libreevolve.distributed_pipeline_topology_report.v1`, current
    controller/database/LLM-sampler/evaluation-node ids, zero queues, blocking
    dependency edges, synchronous dispatch/admission policy, runtime-budget
    linkage, pending-work checkpoint unsupported status, and validator-backed
    overclaim checks. `papers/distributed_pipeline_topology_boundary.json` now
    preserves the same single-process synchronous-topology absence boundary for
    paper-manifest validation.
  - Current gap: this is paper-facing negative boundary evidence, not Section
    2.6 topology parity. It does not implement or preserve async queues,
    queue capacities/backpressure, async task/coroutine identities,
    nonblocking dependency graphs, dependency wait-event telemetry, real
    sampler/evaluator worker fan-out, worker lifecycle/liveness records,
    async scheduler state snapshots, deterministic async completion/admission
    order, cluster-local execution ownership beyond the current
    process/subprocess boundary, throughput dispatch telemetry, or resumable
    pending-work checkpoints.
  - Required result: implement real async runtime topology artifacts and
    validators for controller/sampler/evaluation-node worker ids, queue
    capacities/backpressure policy, task/coroutine identities, nonblocking/
    blocking dependency graphs, dependency wait-event telemetry, worker role
    ownership and liveness, scheduler-state snapshots, deterministic
    completion/admission order, throughput-budget dispatch telemetry,
    pending-work checkpoint state, and claim-readiness checks.

- [ ] Extend Figure 1/Figure 2 architecture-process exhibit provenance into
      full paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 1 shows the
    high-level AlphaEvolve overview from human-defined problem inputs through
    LLMs, prompt sampler, evaluator pool, and program database to an improved
    solution on local PDF page 3. Figure 2 on page 4 expands the discovery
    loop with `database.sample()`, `prompt_sampler.build(...)`,
    `llm.generate(...)`, `apply_diff(...)`, `evaluator.execute(...)`, and
    `database.add(...)`.
  - Partial status: paper-facing TODOs cover individual behavior gaps for
    evaluators, prompt context, LLM scheduling, async throughput, and the
    program database. Completed manifests now preserve a partial Figure 1/2
    process-exhibit mapping under
    `runtime.history.alphaevolve_process_exhibit_report`: stable figure IDs,
    node/edge mappings to LibreEvolve components, implemented/unsupported
    status per node, Figure 2 pseudocode-step mappings, source PDF page and
    caption locations, artifact cross-links, and validation that keeps
    `claim_ready: false`. The report now also writes generated Mermaid source
    and text accessibility artifacts under `paper_artifacts/process_exhibit/`
    with SHA-256 hashes, validates each displayed Figure 2 step against the
    artifact-inventory paths it cites, records strict JSONL row summaries for
    cited streams, records bounded generated-candidate semantic traces with
    durable LLM and archive-admission stream rows, records hashed source-PDF
    page text extracts for Figure 1/Figure 2, records a validated current
    synchronous topology boundary linked to
    `runtime.history.distributed_pipeline_topology_report`, records a
    validated current inline evaluator-pool parallelism boundary, and records
    component-to-TODO links for the remaining process gaps.
  - Current gap: paper-facing evidence still lacks exact source-diagram
    layout reproduction, source figure image/crop hashes, visual node
    coordinates, source edge geometry/routing, Figure 2 line-level pseudocode
    alignment, visual diff/fidelity checks against the source figures,
    AlphaEvolve-style async controller/sampler/evaluator implementation with
    Python `asyncio` runtime identity, and independent evaluator-pool
    implementation strong enough to treat the local mapping as full reproduced
    AlphaEvolve architecture evidence.
  - Required result: add exact source diagram layout reproduction, source
    figure image/crop artifacts and hashes, visual coordinate and edge-routing
    maps, Figure 2 line-level pseudocode alignment, visual fidelity checks,
    async topology implementation evidence including Python `asyncio` runtime
    identity, independent evaluator-pool implementation evidence, and
    README/ROADMAP wording that separates local workflow diagrams, generated
    Mermaid artifacts, artifact-link records, row summaries, semantic
    candidate traces, source-text evidence, and current-topology/evaluator-pool
    boundaries from full reproduced AlphaEvolve architecture evidence.

- [ ] Extend unified task-specification provenance beyond field-level artifact
      resolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and Figure 2.
  - Requirement: AlphaEvolve's task specification is a coherent user-provided
    input bundle: initial program/components to evolve, evaluation code,
    prompt template and configuration, choice of existing or custom LLMs, and
    optional background knowledge. In the local PDF, Figure 2 on page 4 labels
    those inputs and its caption says the user provides an initial program,
    evaluation code, and optional configurations before the evolutionary loop.
  - Partial status: LibreEvolve now emits
    `manifest.json.task_specification` with schema
    `libreevolve.alphaevolve_task_specification_bundle.v1`. The record
    cross-links initial programs, evaluator code or embedded evaluator stages,
    prompt template/config metadata, backend choices, optional background
    context, candidate representation, and objective metrics to manifest paths,
    with field statuses, ids/hashes/counts, explicit unsupported/incomplete
    labels, a deterministic `task_spec_id`, and embedded validation.
    Completed manifests now also include
    `runtime.history.task_spec_artifact_resolution_report`, validating the
    task-spec manifest paths and linking each field to runtime artifact paths
    for candidate history, prompt history, LLM calls, controller-budget events,
    evaluator artifacts, best exports, initial evolvable component spans when
    markers are present, embedded score-field candidate-path links with static
    AST causal attribution when supported candidate-owned evaluation ran, and
    the hashed standalone
    `task_specification.json` run artifact. It also includes bounded candidate
    prompt, and evaluator JSONL row joins, plus the checked
    `docs/examples/task_specification.embedded_evaluate_math.json` standalone
    example. The paper-facing sidecar
    `papers/task_specification_boundary.json` now preserves this
    runtime-artifact-resolution-only boundary.
  - Current gap: paper-facing evidence still lacks full task-spec parity for
    standalone schema completeness for the full user-provided Figure 2
    contract, user-authored source identity, prompt-template content identity,
    config artifact identity, cross-field consistency validation, task-spec
    replay preflight, external validators, arbitrary language/build runners,
    and user-authored standalone task specs beyond the checked example.
  - Required result: extend the current bundle plus artifact-resolution report
    beyond generated manifest linkage and the embedded static score-field
    attribution path before treating it as full AlphaEvolve task-spec evidence:
    require a complete standalone task-spec schema, source-authored package
    identity, prompt/config content hashes, consistency validation, replay
    preflight, external-validator score causality, arbitrary language/build
    runner task specs, and user-authored task-spec parity.

- [ ] Independent per-role LLM scheduler state and reward policy.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: AlphaEvolve-style model orchestration should be able to
    schedule proposal generation, critique, feedback, and prompt-improvement
    calls as distinct work classes with separately auditable budgets, reward
    semantics, and model-selection behavior.
  - Partial status: LibreEvolve now has configured role-backend indices,
    backend-metadata role matching, configured reward-accounted roles,
    per-role logical call limits, role-scoped provider/token/configured-cost/
    latency budget maps, feedback reward wiring for exact configured feedback
    roles, scheduler-policy telemetry, restorable per-role scheduler records,
    and opt-in `llm_role_scheduler_scope="role_scoped"` live selection that
    uses reward-accounted roles' own counts, wins, and total pulls. Startup
    manifests, scheduler snapshots, runtime accounting, and per-call policy
    telemetry expose the effective scheduler scope. Per-call scheduler policy
    telemetry now also records reward-accounted versus telemetry-only role
    status, the bounded local reward contract, matching pre-selection logical
    call quota scopes, and whether selection reads global, role-owned, or no
    reward state. The committed `papers/llm_role_scheduler_boundary.json`
    sidecar now preserves this local role-scoped UCB/runtime evidence boundary
    for paper-manifest validation.
  - Current gap: role-scoped selection and per-call policy telemetry are local
    UCB/runtime contracts, not a calibrated AlphaEvolve scheduler:
    role-specific backend-pool policy, role-specific exploration parameters,
    reward normalization reports, outcome-attribution datasets, async role work
    queues, cross-role interference analysis, role-specific reward
    calibration, experiment-owned quota policy, fast/strong model-mix evidence,
    and experiment reports proving role-specific selection and budget behavior
    remain absent.
  - Required result: add calibrated per-role scheduler policies for mutation,
    critique, feedback, and meta-prompt calls, including role-specific backend
    pools, exploration parameters, normalized reward contracts, outcome
    attribution datasets, async role queues, cross-role interference checks,
    restore validation across real run resumes, and experiment reports proving
    role-specific selection and budget behavior.

- [ ] Validate fast/strong model-mix scheduling beyond local metadata tests.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3, "Models used".
  - Requirement: AlphaEvolve's LLM ensemble mixes Gemini Flash for low-latency,
    high-volume candidate generation with Gemini Pro for occasional stronger
    suggestions that can advance search depth. A faithful implementation needs
    evidence for that throughput/quality tradeoff under a fixed compute
    budget, not only a generic list of interchangeable backends.
  - Partial status: `LLMEnsemble` supports multiple providers, backend
    metadata, role-backend eligibility, UCB-style selection, and a
    `throughput_depth` strategy with focused metadata/unit coverage for
    normalized depth/cost/latency contribution and breadth/depth role labels.
    Per-call scheduler policy now emits
    `throughput_depth_lane_evidence`, including eligible backend lanes,
    normalized cost/latency/depth inputs, missing metadata defaults,
    recognized fast-breadth/strong-depth labels from `model_lane` or `role`
    metadata, and explicit `claim_ready: false` limitations. The committed
    `papers/fast_strong_model_mix_boundary.json` sidecar now preserves this
    metadata-trace-only boundary for paper-manifest validation.
  - Current gap: there is no runtime scheduler policy or experiment report
    proving an experiment-owned fast-breadth lane plus occasional strong-depth
    lane, no equal-budget comparison against single-model or generic UCB
    routing, and no paper-level evidence that the configured mix increases
    evaluated idea volume while preserving breakthrough-quality proposals.
    The current sidecar also records missing fixed-budget identity, matched
    problem/seed/evaluator controls, provider-model identity for the fast and
    strong lanes, lane quota schedules, per-lane token/cost/latency accounting,
    lane switching traces, breadth-volume attribution, and
    breakthrough-quality attribution.
  - Required result: add scheduler-validation fixtures and reports that record
    fixed budget identity, model lane roles, provider-model identity, lane
    quota schedules, selection and lane-switching traces, per-lane consumed
    token/cost/latency budget, candidate throughput, quality/depth outcomes,
    breadth-volume and breakthrough-quality attribution, and equal-budget
    comparisons for fast/strong model mixes before treating LibreEvolve's
    ensemble as AlphaEvolve-style Flash/Pro scheduling evidence.

- [ ] Validate critique reviewer pools beyond synchronous replacement filters.
  - Paper: `2506.13131__AlphaEvolve.pdf`, front overview plus Sections 2.4
    and 2.6.
  - Requirement: AlphaEvolve-style critique and feedback channels should
    provide attributable, budgeted model-review signal rather than only a
    sequential mutation-replacement filter.
  - Partial status: `critique_reviewers` accepts manifest-safe reviewer specs
    with optional prompts and role labels, `critique_aggregation_policy`
    selects `first_valid` or `last_valid`, and retained
    `metadata.critique.reviewer_pool` records the
    `libreevolve.critique_reviewer_pool.v1` schema, reviewer parser status,
    valid revision counts, selected-reviewer provenance, reviewer elapsed
    seconds, outcome status, and inline runtime-artifact policy. Existing role
    backend routing, role budgets, and timeout/cancellation policy records can
    route/account for reviewer roles such as `critique:correctness`. The
    committed `papers/critique_reviewer_pool_boundary.json` sidecar preserves
    this synchronous first/last-valid reviewer boundary for paper-manifest
    validation.
  - Current gap: reviewer calls are sequential, replacement-only, and selected
    by first/last valid mutation rather than calibrated reviewer score or
    benchmarked reviewer reliability. There is no async reviewer overlap,
    independent reviewer task definition, reviewer/generator role-separation
    proof, critique-to-revision attribution, reviewer score-to-selection
    policy, reviewer budget quota policy, reviewer failure-isolation report,
    equal-budget no-reviewer comparison, calibrated reviewer-score report,
    reviewer-pool reliability ablation, stronger per-reviewer provider
    isolation, or external reviewer timeout artifact bundle.
  - Required result: add async/parallel reviewer execution where useful,
    independent reviewer task definitions, explicit reviewer/generator role
    separation, critique-to-revision attribution, calibrated reviewer scoring
    and score-to-selection policy, reviewer budget quotas, reviewer reliability
    reports, equal-budget no-reviewer comparisons, per-reviewer provider
    isolation/budget policy, and external reviewer timeout/failure artifacts
    before treating reviewer pools as AlphaEvolve-grade critique orchestration.

- [ ] Track Google/Gemini provider-parity evidence separately from generic
      custom-backend extensibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3, "Models used".
  - Requirement: the concrete AlphaEvolve implementation used Gemini 2.0 Flash
    and Gemini 2.0 Pro. Paper-facing provider parity therefore needs a
    self-describing Google/Gemini provider surface, or an explicit substitute
    policy, not only a generic custom backend slot.
  - Partial status: LibreEvolve has built-in OpenAI, Anthropic, and Ollama
    adapters, configured custom import-path backends, role-backend eligibility,
    provider usage/default telemetry for supported adapters, and backend
    metadata that can label breadth/depth behavior. Runtime histories now
    include `libreevolve.gemini_provider_parity_report.v1`, which records the
    built-in provider list, configured Gemini-like custom backends,
    Flash/Pro-shaped lane counts, and a `claim_ready: false` first-class-provider
    absence boundary. `papers/gemini_provider_parity_boundary.json` now
    preserves the same first-class-provider absence boundary for
    paper-manifest validation.
  - Current gap: a custom backend can wrap Gemini externally, but the paper
    ledger has no first-class evidence for Gemini credential preflight,
    Gemini client-context configuration, request-parameter mapping,
    provider-native usage/default/capability/error telemetry, safe provider
    diagnostics, model-registry snapshots, account/model availability checks,
    model-family labels, Flash/Pro lane identity, scheduler Flash/Pro lane
    integration, paper-level substitution rules, or substitution-equivalence
    justification that keeps Gemini absence distinct from fast/strong
    scheduling experiments.
  - Required result: add a built-in Google/Gemini adapter or versioned
    provider-plugin/substitution contract with model-family capability
    metadata, credential/client preflight, safe client-context and
    request-parameter mapping, request/usage/default/error telemetry,
    model-registry and account/model availability evidence, diagnostic
    retention policy, scheduler lane integration, and report fields proving
    whether a run reproduced or intentionally substituted AlphaEvolve's
    Flash/Pro provider mix before claiming provider-parity evidence.

- [ ] Track AlphaEvolve sample-efficiency evidence separately from call caps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 4.
  - Requirement: AlphaEvolve contrasts FunSearch-scale millions of LLM samples
    with AlphaEvolve-style thousands of samples that benefit from SOTA LLMs.
    Paper-facing reproduction claims need evidence for useful search progress
    under bounded candidate counts, not only configurable LLM call limits or
    provider budget telemetry.
  - Partial status: LibreEvolve records logical LLM calls, provider attempts,
    provider-reported token totals, configured estimated cost, latency,
    generated candidate ids, sequential sibling proposal batches, and
    equal-budget ablation report shapes. Runtime histories now include
    `libreevolve.sample_efficiency_report.v1`, a single-run report that counts
    generated proposals, evaluated/valid/admitted candidates, retained elites,
    sampling-eligible candidates, logical LLM samples, and a bounded cumulative
    best-score curve. `papers/sample_efficiency_boundary.json` now records the
    benchmark-level absence boundary for target-hit sample indices,
    thousands-scale curves, repeated-sampling comparators, model-size
    comparisons, cross-run tables, and FunSearch-versus-AlphaEvolve budget
    reproduction.
  - Current gap: no benchmark report ties target attainment to the number of
    generated/evaluated LLM proposals, compares thousands-scale runs against
    much larger or smaller sample budgets, or separates sample-efficiency
    gains from generic budget stopping, fast/strong routing, and the
    `Small base LLM only` ablation label. The current report also lacks fixed
    run seed/evaluator identity, fixed compute-budget definitions,
    target-definition provenance, score-direction and normalization policy,
    target-attainment curves by logical sample and generated candidate,
    target-hit indexes, replicate seed sets, variance/confidence reports,
    matched-budget run groups, and cost/latency budget curves.
  - Required result: add sample-efficiency report fields and validation for
    target attainment versus sample count, fixed seed/evaluator identity,
    fixed compute-budget definitions, target-definition provenance,
    score-direction and normalization policy, thousands-scale budget curves,
    replicate statistics, matched-budget run groups, cost/latency budget
    curves, and equal-budget model-size comparisons before claiming
    AlphaEvolve-style "thousands of samples suffice" behavior.

- [ ] Track repeated-sampling baselines for test-time-compute uplift claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Discussion.
  - Requirement: AlphaEvolve is described as a test-time-compute agent that
    enhances base-LLM capability compared with repeated sampling by using
    machine feedback inside an evolutionary loop.
  - Partial status: LibreEvolve has LLM budget telemetry, generated candidate
    ids, admission/failure records, equal-budget ablation report schemas, and a
    `No evolution` ablation variant label. Runtime histories now include
    `libreevolve.repeated_sampling_baseline_report.v1`, which records the
    current absence of a controlled comparator, links observed generated/
    accepted/rejected/execution-filtered sample counts, and lists the missing
    comparator controls. `papers/repeated_sampling_baseline_boundary.json` now
    preserves that controlled-comparator absence boundary for paper-manifest
    validation.
  - Current gap: paper-facing reports do not define an equal-budget repeated
    base-model sampling comparator with fixed prompt/model/backend-request/
    seed/candidate-budget/evaluator conditions, generated/evaluated sample
    counts, disabled archive feedback, fixed LLM-call budgets, candidate-
    validation parity, disabled MAP-Elites selection, disabled parent/
    inspiration resurfacing, disabled failure feedback, disabled critique/
    feedback, disabled meta-prompt updates, sample-index alignment, target
    metric/threshold linkage, comparator artifact hashes, and target-progress
    curves linked to the matching evolutionary run.
  - Required result: add repeated-sampling baseline report fields and
    validation for controlled base-model sampling runs, sample counts,
    validity/admission outcomes, target attainment, fixed request parameters
    and LLM budgets, candidate-validation parity, disabled evolutionary
    feedback proof, sample-index alignment, target metric/threshold linkage,
    budget parity, comparator artifact hashes, and links to evolutionary
    comparator runs before claiming AlphaEvolve-style test-time-compute uplift
    over repeated sampling.

- [ ] Preserve AlphaEvolve arXiv abstract-page metadata beyond cached-PDF
      source-version evidence.
  - Paper/source evidence: the current arXiv page for `2506.13131` reports
    the submitted date, full author list, abstract, subject classes
    `cs.AI`, `cs.LG`, and `cs.NE`, DOI `10.48550/arXiv.2506.13131`,
    submission-history timestamp, TeX source link, and CC BY-NC-ND 4.0
    license link. These are source-bibliography facts adjacent to, but not
    identical with, the cached PDF first-page header.
  - Current gap: `papers/source_versions.json` now extends the AlphaEvolve
    source-version row with DOI, subject classes, submitted timestamp, author
    count, TeX source URL, arXiv license URL, and an explicit
    `manual_current_as_of_2026-06-13_with_html_snapshot` status. Its audit
    policy links DataCite, TeX-source archive, and license-page evidence to
    companion sidecars while still keeping raw/live source refresh evidence,
    license-page refresh gating, and submission-history refresh checks open.
    This is still a manually recorded source-version boundary, not a live
    refresh verifier.
    `papers/arxiv_abstract_snapshot.json` now pins the current
    `2506.13131v1` abstract HTML byte count, SHA-256 digest, retained HTML
    artifact path, normalized title/authors/subjects/DOI/submission-history
    metadata, and a validator-supported live snapshot comparison path, while
    paired with the reusable offline extraction-script boundary.
    `papers/alphaevolve_datacite_doi_boundary.json` now pins a bounded
    2026-06-14 DataCite API snapshot for `10.48550/arxiv.2506.13131`,
    including response byte count, SHA-256 digest, DOI, landing URL, title,
    creator count, publisher, publication year, resource type, schema version,
    registered timestamp, and version, while keeping full raw response
    retention and automated refresh gating open.
    `papers/alphaevolve_tex_source_boundary.json` now pins a bounded
    2026-06-14 arXiv e-print snapshot for `2506.13131`, including HTTP status,
    gzip content type, content-disposition filename, byte count, SHA-256
    digest, and `2506.13131v1` source-version linkage, while keeping full
    archive retention and automated refresh gating open.
    `papers/alphaevolve_license_page_boundary.json` now pins a bounded
    2026-06-14 Creative Commons BY-NC-ND 4.0 license-page snapshot, including
    HTTP status, content type, byte count, SHA-256 digest, title, license
    family, license version, and normalized URL, while keeping automated
    refresh gating open.
    `papers/alphaevolve_current_version_boundary.json` now records the
    2026-06-14 arXiv floating abstract status/content/digest, resolves current
    version `2506.13131v1`, and confirms the retained floating PDF artifact
    bytes/hash match the cached PDF.
    `papers/alphaevolve_cached_pdf_header_consistency_boundary.json` now pins
    cached-PDF first-page header extraction hashes and arXiv/title/rights
    markers for the retained AlphaEvolve PDF.
    `papers/alphaevolve_metadata_extraction_script_boundary.json` now pins the
    reusable offline extraction script path, byte count, SHA-256 digest,
    import entrypoint, CLI command, and retained source artifact coverage for
    abstract HTML, cached PDF, DataCite full response, license HTML, and TeX
    archive inputs.
    `papers/alphaevolve_raw_http_headers_boundary.json` now records pinned raw
    HTTP response header lines for the versioned abstract, floating abstract,
    floating PDF, DataCite API, e-print archive, and license page.
    `papers/alphaevolve_doi_landing_resolution_boundary.json` now records the
    DOI resolver `302` status, redirect location, raw DOI resolver headers, and
    final arXiv landing-page headers.
    `papers/alphaevolve_datacite_full_response_boundary.json` now retains the
    complete 15,905-byte raw DataCite API response body and validates parsed
    DOI metadata fields.
    `papers/alphaevolve_tex_archive_retention_boundary.json` now retains the
    2,635,462-byte TeX/e-print archive and validates its 58-entry member
    inventory.
    `papers/alphaevolve_license_page_html_retention_boundary.json` now retains
    the Creative Commons license-page HTML artifact and validates its byte
    count, SHA-256 digest, and key content markers.
    `papers/alphaevolve_source_refresh_gate_boundary.json` now records the
    deterministic/live refresh-gate script and the scheduled/manual GitHub
    Actions job that compares live arXiv/DataCite/e-print/license responses
    against committed source boundaries; the paper manifest requires and
    validates that sidecar at the real repo root.
    `papers/alphaevolve_source_refresh_run_2026-06-14.json` now archives one
    successful manual live-network refresh run with six matched source
    responses and a canonical run-report hash.
    The scheduled/manual GitHub Actions job now writes
    `alphaevolve_source_refresh_report.json` and uploads it as the
    `alphaevolve-source-refresh-report` artifact.
    `papers/alphaevolve_source_refresh_promotion_boundary.json` now records
    the decision not to relabel older per-source snapshot sidecars as
    standalone refresh-ready evidence; it maps each central-gate source id to
    the sidecars covered by the gate.
  - Required result: before using arXiv abstract-page metadata as
    publication-grade freshness evidence, retain scheduled CI refresh-run
    history.

- [ ] Track Google/Gemini provider parity separately from generic backend
      configurability.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3, "Models used".
  - Requirement: the published AlphaEvolve ensemble used Gemini 2.0 Flash and
    Gemini 2.0 Pro; a reproduction-oriented implementation should either
    provide a first-class Google/Gemini backend surface or explicitly document
    an equivalent substitute with comparable capability and telemetry evidence.
  - Partial status: LibreEvolve supports multiple built-in providers through
    OpenAI, Anthropic, and Ollama, plus custom backend class paths. Runtime
    histories now include `libreevolve.gemini_provider_parity_report.v1`, which
    detects Gemini-like custom model ids and Flash/Pro-shaped lanes while
    preserving the missing first-class provider boundary.
    `papers/gemini_provider_parity_boundary.json` now records that paper-facing
    absence boundary for manifest validation.
  - Current gap: no built-in Google/Gemini backend exists, and `custom`
    backends do not by themselves supply provider-native usage/default
    telemetry, account/model capability evidence, credential preflight, Gemini
    client-context configuration, request-parameter mapping, provider-native
    error diagnostics, model-registry snapshots, substitution-equivalence
    justification, or Flash/Pro lane labels for scheduler-validation reports.
  - Required result: add a Gemini backend or provider-plugin contract with
    safe request metadata, client-context and request-parameter mapping,
    usage/default/error diagnostics, model-family capability policy,
    credential/client preflight, account/model availability evidence, scheduler
    lane integration, and paper-facing evidence that the fast/strong model mix
    is reproduced or intentionally substituted.

- [ ] Add AlphaEvolve-grade candidate language, build, and runner contracts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.2.
  - Requirement: tasks define the program artifact and evaluator interface; a
    faithful system should be able to operate on codebases and task-specific
    solution representations rather than only one Python-primary workspace
    shape.
  - Partial status: startup manifests now include
    `libreevolve.candidate_language_policy.v1`, declaring the current
    `python_primary_text_workspace_v1` boundary, bounded UTF-8 workspace plus
    typed static members, fail-closed non-Python marker handling, Python
    subprocess validator runner, and unsupported arbitrary-language,
    build-system, and problem-defined solution-abstraction surfaces.
    `validate_candidate_language_policy()` rejects overclaims that those
    surfaces are ready. Completed manifests now also include
    `runtime.history.candidate_language_runner_contract_report`, a checked
    negative-boundary contract report that records the current Python runner,
    non-Python text members as workspace-only/no-runner records, unsupported
    arbitrary-language and build-system runner contracts, metadata-only
    `candidate_language_runners` and `candidate_build_systems` declarations
    when configured, `runner_declaration_evidence` counts/status records,
    bounded retained-workspace path-match records under
    `runner_declaration_workspace_evidence`, current-Python-runner
    environment linkage under `runner_environment_provenance`, unsupported
    task candidate-abstraction hooks, and the remaining executable contract
    gaps for AlphaEvolve-style language/build parity. The committed
    `papers/candidate_language_runner_boundary.json` sidecar now preserves the
    paper-manifest-validated arbitrary-language/build-runner execution absence
    boundary.
  - Current gap: this is an honest boundary record, not non-Python or
    arbitrary-codebase support. Metadata-only language/build declarations can
    now be recorded and matched to retained workspace paths, but there are no
    executable non-Python language runners, build-system execution contracts,
    arbitrary-runner environment artifacts, language-aware marker grammars, or
    task-defined candidate abstraction hooks.
  - Required result: add executable configured language runners, build-system
    contracts, language-aware marker grammars, and task-defined candidate
    abstraction hooks before treating the current Python-primary workspace
    policy as AlphaEvolve-grade arbitrary-codebase or arbitrary-language
    support.

- [ ] Extend existing-codebase minimal-marker integration evidence beyond
      runtime workspace inventory.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.1 says the input
    API facilitates integration with existing codebases while requiring only
    minimal changes, simply by adding special markers as comments into the
    code. In the local PDF, this appears on page 4; Figure 3 on page 6 shows
    the marked blocks together with the special `evaluate(eval_inputs) ->
    dict[str, float]` function that the evaluators invoke.
  - Partial status: paper/status records can show Python evolve-block marker
    parsing, unsupported non-Python marker diagnostics, workspace
    materialization, seed workspace source paths, static-file hashes, and
    candidate-language boundaries. Completed manifests now include
    `runtime.history.existing_codebase_integration_report`, which records
    runtime candidate workspace marker spans, stable span ids,
    skeleton-preservation hashes, language/comment syntax, unmarked-file
    hashes, seed-source references, and claim-readiness gaps. The checked-in
    `workspace_math` fixture now includes `codebase_integration.yaml` plus
    `source_setup/fixture_lib_v1/` pre-marker Python sources and a
    source-setup manifest, so completed manifests can expose smoke
    source-setup metadata. The committed
    `papers/existing_codebase_integration_boundary.json` sidecar now preserves
    the source-setup-level
    `smoke_source_setup_fixture_recorded_missing_real_upstream` boundary, and
    the paper manifest requires and validates it at the real repo root.
    Problem fixtures and direct callers now also support optional
    `codebase_integration.yaml` / `Problem.codebase_integration_metadata`,
    normalized `problem.codebase_integration_metadata`, and
    `source_setup_metadata` in the runtime report for source/upstream identity,
    pre-marker hashes, marker-only setup diff status, evaluator-call
    continuity, copied static-asset identity, and source-setup completeness.
  - Current gap: paper-facing evidence still does not prove that a real
    pre-existing external or release-like codebase was integrated with a
    marker-only or minimal setup diff, that pre-marker source artifacts are
    independently preserved, that evaluator invocation actually worked through
    the existing codebase structure before and after marker insertion, or that
    copied static assets have portable source-root/release identities outside a
    smoke fixture.
  - Required result: add a populated paper-facing codebase-scale fixture and
    evidence bundle with original codebase id, pre-marker source artifacts and
    hashes, independently checkable marker-added setup diff summary, evaluator
    invocation proof before/after marker insertion, setup-change counts,
    portable source-root/release identity, and wording that distinguishes smoke
    source-setup metadata from AlphaEvolve-style minimal-change integration
    evidence.

- [ ] Track candidate-abstraction choice and bias evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and Discussion.
  - Requirement: AlphaEvolve treats the candidate representation as a
    problem-dependent choice: direct solution search, constructor functions,
    bespoke search algorithms, or co-evolved intermediate solution/search
    pairs. The paper says these choices carry different biases, including
    constructor functions being advantageous for highly symmetric solutions and
    customized search algorithms for non-symmetric solutions. In the local PDF,
    page 5 describes flexibility in choosing the abstraction and page 21 says
    direct search, constructor functions, and search algorithms come with
    different biases.
  - Partial status: the papers index and README state that LibreEvolve's
    current boundary is a Python-primary code-file-set abstraction and that
    flexible non-code or paired solution/search abstractions are unsupported.
    Current manifests record this through
    `libreevolve.candidate_language_policy.v1`: `python_primary_text_workspace_v1`,
    bounded UTF-8 text workspace plus typed static members, primary language
    `python`, `problem_defined_solution_abstractions: unsupported`, and
    `language_runner_ready: False`. Completed manifests also include
    `runtime.history.candidate_abstraction_choice_report`, which records the
    selected code-file-set abstraction, serializer/runner linkage, runtime
    workspace shape, unsupported constructor/search/paired alternatives, and
    a claim-readiness check that keeps AlphaEvolve abstraction-selection
    fidelity false. The committed `papers/candidate_abstraction_boundary.json`
    sidecar now preserves the paper-manifest-validated current absence
    boundary for typed abstraction APIs and bias/equal-budget evidence.
    `papers/candidate_abstraction_bias_matrix.json` now preserves a
    design-level comparison matrix for the four paper abstraction families,
    expected symmetry/bias directions, representation/runner contract status,
    and equal-budget comparison fields.
  - Current gap: paper-facing evidence still lacks problem structure
    rationale populated for actual benchmarks, a problem-declared abstraction
    schema, typed problem-defined abstraction APIs for direct-solution,
    constructor-function, bespoke-search, and paired solution/search
    formulations, abstraction-specific prompt templates, validator contracts,
    archive descriptor mappings, migration policy, paired solution/search
    support, or executed equal-budget comparisons across abstraction
    formulations.
  - Required result: add benchmark metadata for candidate abstraction family,
    rationale, expected problem bias, prompt/validator/archive descriptor
    contracts, paired solution/search linkage, migration rules, and comparable
    results for alternative abstractions before claiming AlphaEvolve-style
    abstraction-selection evidence.

- [ ] Populate early-user and collaborator feedback provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Acknowledgements thank early
    users and collaborators for diverse use cases and insightful feedback,
    stating that this feedback shaped AlphaEvolve into a more robust and
    versatile tool. This is a broad external-feedback and system-shaping claim,
    separate from AlphaEvolve's machine feedback/evaluator loop.
  - Current evidence: paper/status records track local problem/source
    provenance, expert mathematical formulation gaps, application
    owner/reviewer gaps, benchmark/report artifacts, optional
    `collaborator_feedback.yaml` /
    `Problem.collaborator_feedback_metadata`, normalized
    `problem.collaborator_feedback_metadata`, and
    `runtime.history.collaborator_feedback_provenance_report`. The report
    records safe cohort/role labels, feedback event IDs, use-case areas,
    affected workflows, change-artifact links, validation outcomes,
    privacy/redaction policy, review/signoff state, and robustness/versatility
    claim readiness. Current paper-facing implementation notes can also
    describe LLM-grader feedback retention, feedback indexes,
    feedback-sourced metrics, and calibration-report contracts as separate
    search/evaluation telemetry.
    `papers/collaborator_feedback_provenance_boundary.json` preserves this
    metadata-contract-only boundary as manifest-validated paper evidence.
    Existing fixtures still lack real populated broad collaborator-feedback
    records, cohort-coverage policy, source feedback artifacts, linked
    code/docs/report diffs, validation rerun artifacts, privacy/redaction
    artifacts, review/signoff versions, longitudinal follow-up,
    claim-to-feedback traces, and paper-facing certification examples.
  - Required result: populate representative fixtures with reviewed use-case
    feedback records, link events to actual workflow/artifact changes and
    validation outcomes, add source/redaction artifacts, review/signoff
    versions, follow-up, traceability, paper-facing examples or certification
    rows, and keep documented local breadth separate from AlphaEvolve-style
    broad collaborator-feedback evidence until those records exist.

- [ ] Add replayable evaluator environment, package-source, and accelerator
  provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.4, 2.6, and 4.
  - Requirement: AlphaEvolve-style evaluator results should be attributable to
    a reproducible runtime environment, including build execution, package
    source resolution, accelerator/runtime state, and budget-accounting
    evidence for hardware-backed or distributed evaluation.
  - Partial status: LibreEvolve manifests record selected project/build
    metadata, declared dependency and installed-distribution snapshots,
    bounded `WHEEL`/`direct_url.json`/`INSTALLER`/`RECORD` evidence,
    known-lockfile hashes, bounded/redacted `pip freeze` and `pip config`
    snapshots, NumPy config hashes, provider SDK versions, and bounded
    accelerator environment/driver probe hints. The
    `environment_reproducibility_policy` is explicitly audit-only and lists
    unsupported complete install-source interpretation, broader non-project
    build provenance, private package-source identity/authentication
    resolution, remote package artifact verification, live provider
    service/default capture, and accelerator budget/accounting semantics. The
    paper-facing sidecar
    `papers/release_artifact_reproducibility_boundary.json` now records the
    CI-release-smoke boundary for wheel/sdist and install-from-wheel checks.
  - Current gap: these records do not form a replayable environment contract:
    external build commands/options/environment, non-project build metadata,
    transitive package-source resolution, private-index policy, remote package
    artifact hashes, accelerator lease/accounting state, and restore/check
    validation remain absent.
  - Required result: add versioned external-build/package-source/accelerator
    provenance schemas plus restore/check validators and paper-facing evidence
    that clearly separates bounded audit hints from reproducible evaluator
    environment proof.

- [ ] Track CI workflow coverage separately from local validation commands.
  - Paper evidence: AlphaEvolve-scale experimental claims require repeatable
    validation over source, documentation, paper evidence, packaging, and the
    supported runtime environments used to produce results.
  - Partial status: `.github/workflows/tests.yml` provides manual dispatch,
    path-scoped `push` and `pull_request` triggers, secret scanning, Python
    3.11/3.12 non-integration tests on Ubuntu, Windows, and macOS, and an
    optional credential-gated Ubuntu integration job. It now also has a dedicated paper/docs
    job that runs `python -m libreevolve.tools.paper_manifest --root .` and
    paper-source, manifest, docs, and boundary verifier tests without requiring
    ignored local PDFs, plus a
    release-artifact smoke job that builds one wheel and one sdist, checks
    every `libreevolve/` package-tree file in the wheel and sdist, writes artifact hash
    provenance, uploads release smoke artifacts, installs the wheel into an
    isolated virtual environment, and smokes the CLI.
    `tests/test_agents_docs.py` verifies the path filters, job names, and
    paper/docs/release commands. The committed
    `papers/ci_workflow_coverage_boundary.json` sidecar preserves this
    path-scoped cross-platform unit workflow boundary for paper-manifest
    validation.
  - Current gap: CI still does not run paper-manifest local-PDF checks, does
    not perform fully semantic documentation-claim verification beyond the
    committed verifier suite, does not certify signed release provenance, does
    not cover paper/docs, release, or integration jobs across non-Ubuntu
    platforms, and does not encode richer branch or notification policy.
  - Required result: add local-PDF manifest validation where appropriate,
    fully semantic docs-claim verification, release-artifact signed provenance,
    cross-platform paper/docs, release, and integration coverage, branch policy,
    and notification-safe trigger policy before treating the workflow as full
    AlphaEvolve-grade validation coverage.

- [ ] Track stochastic LLM-generation reproducibility separately from request
      parameter telemetry.
  - Paper evidence: AlphaEvolve ablations and repeated experiments require
    controlled model calls, seeds, and budgets to support comparable claims.
    Reproducibility claims must separate request-parameter logging from proof
    that provider sampling behavior is replayable.
  - Current evidence: built-in backend specs validate and forward supported
    `temperature`, `top_p`, stop-sequence, and request-seed parameters, and
    `llm_calls.jsonl` records normalized effective request parameters with
    backend/model/API-mode telemetry. Provider diagnostics sidecars preserve
    bounded scalar/id telemetry while explicitly keeping raw provider-payload
    replay and complete provider-call replay absent.
  - Current gap: paper-facing evidence does not classify seed determinism by
    backend/API mode, record provider model-revision stability requirements,
    validate repeated identical prompt/parameter calls, or prove that logged
    sampling controls reproduce the same proposal stream.
    `papers/llm_stochastic_reproducibility_boundary.json` now keeps this as a
    paper-facing request-telemetry versus deterministic-replay boundary.
  - Required result: add stochastic-generation reproducibility reports and
    paper-facing boundaries that distinguish best-effort provider request
    controls from deterministic provider-output replay before using logged
    request parameters as AlphaEvolve-style reproducibility evidence.

- [ ] Stable behavior descriptor models and archive rebin semantics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3 and 2.4.
  - Requirement: a quality-diversity archive should use task-meaningful
    behavior descriptors or explicitly stable descriptor models; adaptive
    descriptors need clear compatibility and rebin semantics.
  - Partial status: MAP-Elites defaults to selection score, serialized
    workspace complexity, and TF-IDF char-ngram diversity against the current
    capped elite list. `map_elites_descriptor_axes` can select normalized
    evaluator metrics, numeric evaluator metadata, or numeric candidate
    metadata as descriptor axes. Archive snapshots persist descriptor policy
    and descriptor-model records with axes, bounds, diversity reference ids,
    revision, dynamic-reference status, and explicit no-rebin policy. The
    descriptor model now carries
    `libreevolve.map_elites_descriptor_readiness.v1` with false readiness for
    stable task behavior descriptor contracts, learned/evaluator-provided
    descriptor models, descriptor training inputs, restore-compatible
    descriptor revisioning, and full/partial archive rebin engines; restore
    validation rejects forged readiness overclaims.
  - Current gap: existing cell coordinates are insertion-time snapshots under
    a local adaptive TF-IDF novelty heuristic. The readiness guard is not a
    learned descriptor model, evaluator-provided descriptor contract with
    compatibility rules, or tested archive rebin engine.
    `papers/map_elites_descriptor_boundary.json` now validates that local
    descriptor/rebin absence boundary.
  - Required result: add stable task behavior descriptor contracts or learned
    descriptor models, tested rebin/snapshot compatibility semantics, restore
    validation across descriptor revisions, and paper-facing reports that do
    not confuse insertion-time TF-IDF coordinates with AlphaEvolve-grade
    behavior descriptors.

- [ ] Keep island-count and topology claims scoped to configurable defaults.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: AlphaEvolve describes an evolutionary database inspired by
    MAP-Elites and island-based population models; paper-facing LibreEvolve
    claims should state the local island topology honestly without implying an
    unsupported fixed or paper-identical island policy.
  - Partial status: LibreEvolve's island count is configurable through
    `Config.n_islands`, defaults to five, and migration uses the configured
    island count in a synchronous ring topology. README, ROADMAP, AGENTS, and
    the `IslandModel` docstring now describe configurable island migration
    with a five-island default instead of hardcoding all claims to five
    islands. Runtime archive-state snapshots now include `topology_policy`
    schema `libreevolve.island_topology_policy.v1`, recording configured
    synchronous ring migration, configurable island count, the five-island
    default, and explicit false readiness for adaptive island counts, non-ring
    topologies, and AlphaEvolve-identical island policy; validators reject
    forged topology overclaims.
  - Current gap: this is a validated local topology boundary, not proof of a
    paper-identical AlphaEvolve evolutionary database. Adaptive island counts,
    non-ring topologies, topology-specific ablations, and a richer
    paper-facing migration-policy report remain absent.
  - Required result: if future work adds adaptive island topology or
    AlphaEvolve-specific migration policy fidelity, update the papers index,
    README, ROADMAP, and code TODO entries together so they neither underclaim
    current configurability nor overclaim fixed five-island policy.

- [ ] Tighten remaining invalid-workspace topology diagnostics for codebase-scale
  artifact failures.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.2.
  - Requirement: AlphaEvolve-style tasks mutate program artifacts under
    automated evaluator feedback; generated invalid artifacts should leave
    stable, inspectable diagnostics that can steer future proposals. The local
    PDF describes multi-component codebase evolution on page 4,
    larger-codebase diff-block sequences on page 7, and entire-codebase
    evolution on pages 18-19.
  - Partial status: typed `CandidateMaterializationError` records now cover
    materialized candidate-path collisions, linked target roots or ancestors,
    linked nested root entries, file target roots, parent/temp root creation,
    candidate text/static write failures, existing-root backup failures, final
    swap failures, backup restore failures, cleanup deletion failures, and
    static source-copy link/read/not-file/hash/byte-count failures. Evaluations
    persist `materialization_error` metadata with bounded message text plus
    structured `reason` and relevant bounded `paths`, and prompt context policy
    can select/cap those fields for failure-memory feedback. Topology sections
    are prevalidated for duplicate source/target operations, host/case-folded
    file or move-target collisions, non-empty command bodies, and primary-file
    deletion without replacement.
  - Current gap: future topology surfaces such as bulk directory operations or
    language/build-runner generated artifacts must preserve stable diagnostics,
    copied static assets still need portable source-root or release-artifact
    identity beyond local `source_copy_path` labels, and future materialization
    filesystem paths must preserve the stable reason/path diagnostic contract
    before LibreEvolve can claim robust codebase-scale invalid-artifact
    feedback across arbitrary-language runners, build-system outputs,
    dependency manifests, or remote/containerized execution roots. The
    committed `papers/workspace_materialization_boundary.json` sidecar now
    preserves that local-file-workspace-only boundary for paper-manifest
    validation.
  - Required result: add diagnostics and paper-facing validation for future
    bulk directory operations, build-runner generated artifacts, portable static
    asset source identities, dependency manifests, remote/containerized
    materialization roots, and invalid-workspace fixture rows while preserving
    stable reason/path metadata.

- [ ] Track Table 1 code-scale benchmark evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 2.1.
  - Requirement: AlphaEvolve reports evolving entire code files, hundreds of
    lines of code, any language, and complex algorithms spanning multiple
    functions and components. Local PDF page 2 contains the Table 1 code-scale
    rows; pages 18-19 discuss entire-codebase evolution.
  - Partial status: LibreEvolve has Python-primary workspaces, multi-file seed
    loading, file-topology mutations, materialization diagnostics,
    full-workspace prompt/export paths, and a small multi-file smoke fixture.
    Completed manifests now include
    `runtime.history.codebase_scale_benchmark_report`, which records
    generated/changed line counts, component/file counts, static-file
    references, and multi-file/hundreds-line threshold evidence for retained
    programs. The example scope registry still marks `workspace_math` as
    `alphaevolve_comparable: False` with current role
    `workspace_packaging_fixture`, so it is evidence for mechanics rather than
    Table 1-scale performance. The committed
    `papers/codebase_scale_benchmark_boundary.json` sidecar preserves this
    absence boundary for paper-manifest validation.
  - Current gap: there is no realistic benchmark fixture that demonstrates
    hundreds-line generated programs, coupled multi-component edits,
    dependency-graph validation, non-Python or build-runner execution,
    realistic codebase dependency edits, evaluator workload budgets, retained
    best-workspace artifact hashes, reproducibility bundles, smoke-fixture
    scope separation, valid/admitted/retained-rate curves, or quality progress
    on a large codebase-scale task.
  - Required result: add codebase-scale benchmark fixtures with dependency-edit
    evidence, evaluator/runtime budgets, valid/admitted/retained-rate curves,
    retained artifact hashes, reproducibility bundles, and score progress
    before treating current workspace support as AlphaEvolve Table 1 code-scale
    parity. The remaining gap is benchmark-backed evidence, not manifest
    telemetry for current run scale.

- [ ] Keep Table 1 capability-comparison exhibit evidence scoped to table
      provenance rather than row parity.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 1 compares FunSearch
    and AlphaEvolve across capability and behavior rows: function/file
    evolution, code length, programming language scope, evaluator duration and
    accelerator/parallelism support, LLM sample counts, model scale, prompt
    context and feedback, and single versus multiple metrics. Local PDF page 2
    contains the eight-row table and caption.
  - Current evidence: paper TODOs already split out several Table 1 row claims
    such as code-scale behavior, sample efficiency, model mix, rich context,
    evaluator workload, and multi-metric optimization. Completed manifests now
    include `runtime.history.alphaevolve_table1_capability_exhibit_report`,
    preserving Table 1 as a table exhibit with stable table/row ids, source
    page/caption location, FunSearch and AlphaEvolve cell text, row ordering,
    row-to-implementation status, row-to-TODO/report mappings, rendered table
    artifact hashes, and validation that full Table 1 parity remains false.
    The committed `papers/table1_capability_exhibit_boundary.json` sidecar
    keeps this table-provenance-only scope manifest-validated.
  - Required result: satisfy the individual behavioral capability rows with
    benchmark-backed evidence. The remaining gap is not reproducing the
    comparison artifact; it is proving code scale, arbitrary-language,
    evaluator-workload, sample-efficiency, model-scale, rich-context, and
    multi-metric capabilities under paper-faithful conditions.

- [ ] Extend Figure 1 and Figure 2 process-overview exhibit provenance as
      paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 1 shows the
    high-level AlphaEvolve workflow: human-provided evaluation criteria,
    initial solution, optional background knowledge, LLM ensemble, prompt
    sampler, evaluator pool, program database, rich context, proposals, and
    quality scores/feedback. Figure 2 expands the discovery process with
    user-provided initial program, evaluation code, optional configuration,
    parent/inspiration sampling, prompt construction, diff generation, diff
    application, evaluator execution, and database registration of promising
    solutions. Local PDF page 3 contains Figure 1 and its caption; page 4
    contains Figure 2, its caption, and the displayed controller pseudocode
    lines.
  - Partial status: paper TODOs track Table 1 and Figure 3+ exhibit provenance
    plus many individual Figure 1/2 component behaviors. Completed manifests
    now preserve Figures 1 and 2 as process-exhibit metadata under
    `runtime.history.alphaevolve_process_exhibit_report`, with stable figure
    IDs, diagram-node labels, edge/process-flow ordering, Figure 2
    pseudocode-step mappings, source/caption locations, artifact cross-links,
    generated Mermaid/text artifacts and hashes, per-step artifact-stream
    validation records, strict JSONL row summaries, generated candidate
    semantic traces, component-to-TODO links, and row/linkage from each
    displayed process step to implementation status.
    The committed `papers/process_exhibit_boundary.json` sidecar now records
    the manifest-validated absence boundary for full process-diagram parity
    evidence.
  - Current gap: paper-facing evidence still lacks exact diagram/pseudocode
    source caption/text identity, source diagram text identity, diagram
    node-label source alignment, source figure image/crop hashes, visual node
    coordinates, source edge geometry/routing, Figure 2 pseudocode line-number
    maps, line-level pseudocode alignment, visual diff/fidelity checks, async
    topology evidence, and independent evaluator-pool evidence. Existing
    component-level implementation evidence is still not a complete reproduced
    paper process exhibit.
  - Required result: add source-faithful diagram/caption text identity,
    source image/crop and coordinate maps, Figure 2 line-level pseudocode
    alignment, visual fidelity checks, async topology evidence, independent
    evaluator-pool evidence, and
    README/ROADMAP wording that separates reproducing the paper process
    diagrams from implementing each underlying AlphaEvolve workflow
    capability.

- [ ] Track evaluator workload provenance for inner-search and ML-training
      evaluators.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: AlphaEvolve's evaluation function may run a simple property
    check, an evolved search algorithm, or train and evaluate a
    machine-learning model before returning scalar metrics.
  - Partial status: LibreEvolve records evaluator entrypoint paths, configured
    stages, samples, retries, seeds, subprocess attempts, budgets, problem-local
    dependency provenance, copied evaluator artifacts, and bounded environment
    evidence. Configured stages can now declare validated `workload` metadata
    for `simple_check`, `inner_search`, `ml_training`, or `custom`, including
    optional dataset/split hashes, budget fields, checkpoint/artifact policy,
    and score-field names. Runtime manifests summarize executed stage workload
    evidence under `runtime.history.evaluator_workload_report`, including
    dataset-digest completeness, score-field-to-returned-metric linkage,
    observed artifact file evidence, protocol-readiness counts, and validation
    that rejects workload protocol overclaims.
  - Current gap: paper-facing evidence still does not enforce the protocol
    needed for search/training-style evaluators: managed model-training or
    search-loop execution, checkpoint or construction-artifact completeness
    beyond observed files, randomized initialization policy, stochastic
    re-evaluation/replay policy, and causal linkage from produced artifacts to
    returned scores.
  - Required result: extend report/manifest evidence into executable evaluator
    workload contracts for `inner_search` and `ml_training`, with managed
    training/search loop records, checkpoint/artifact linkage, seed/retry
    and re-evaluation semantics, score-field-to-artifact causality, and
    examples that keep quick validators distinct from AlphaEvolve-style
    evaluator workloads that train models or run search.

- [ ] Complete accelerator/async budgets and executed ablation support.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.6 and 4.
  - Requirement: AlphaEvolve optimizes throughput under a fixed computation
    budget, and ablations compare performance as a function of consumed budget.
  - Partial status: LibreEvolve now has a local `RunBudget` for
    `max_generations`, optional total evaluation count, optional cumulative
    evaluator seconds, optional detailed evaluator counter limits, and optional
    wall-clock seconds. It also has an optional `max_llm_calls` cap on logical
    LLM `generate()` calls plus an optional `max_llm_provider_attempts` cap on
    recorded provider adapter attempts, `max_llm_tokens` for provider-reported
    token totals, `max_llm_cost_microusd` for configured estimated cost, and
    `max_llm_seconds` for retained LLM call latency.
    Candidate history records include budget snapshots, and completed
    manifests include consumed budgets plus structured stop reason.
  - Current gap: provider-reported token totals are now audit telemetry, and
    configured `cost_usd_per_million_tokens` rates can estimate provider cost
    from those token totals. Per-call cost estimates now declare configured
    backend metadata as the pricing source, provider usage metadata as the
    token-count source, and explicitly avoid claiming live provider pricing.
    Per-call `cost_estimate_status` records now preserve not-estimated reasons
    for missing configured rates or missing/invalid provider token totals.
    Provider diagnostics now reject configured-pricing count drift and
    cost-status reason drift so aggregate summaries cannot imply pricing
    evidence unsupported by retained call rows. They also reject raw provider-
    payload replay overclaims at the summary, totals, and backend-record
    scopes, remote provider-default/default-rate capture claims, and backend-
    default record counts that exceed retained calls. Diagnostics now also
    expose false pricing-readiness flags for live provider pricing, provider
    default-rate capture, and account/model-specific pricing. The committed
    `papers/provider_pricing_boundary.json` sidecar now preserves this
    configured-cost-estimate boundary for paper-manifest validation.
    Live global token and configured-cost stop
    criteria now exist, and full-runtime restore now pre-applies replayed
    provider-attempt/token/configured-cost/latency controller events to the
    restored `evolve()` budget snapshot. Accelerator budgets, async queue
    accounting, live provider pricing/default-rate capture beyond configured
    token-cost estimates, and executed equal-budget benchmark scripts are still
    missing. The committed
    `papers/provider_diagnostics_replay_boundary.json` sidecar now preserves
    the bounded-diagnostics versus raw-provider-replay boundary for paper-
    manifest validation.
    `libreevolve.alphaevolve_ablation_report.v1` now defines and tests an
    equal-budget ablation-result report contract for reports produced by
    executed runs: the Figure 8 full-system baseline plus five component
    ablations, declared targets, exactly three seeds, required equal-budget
    fractions, finite scores,
    consumed-budget/fraction consistency, consistent budget unit/limit per seed
    curve and across all variants/seeds for each target, passed component
    assertions, and hashed curve artifacts.
    That report contract now requires the two Figure 8 task families, low-rank
    matrix tensor decomposition and kissing-number sphere packing, and
    validates per-target mean/standard-deviation curve summaries against the
    underlying three independent seed traces.
    `libreevolve.alphaevolve_ablation_artifact_inventory.v1` now verifies
    declared ablation report artifacts under an explicit artifact root,
    checking safe relative paths, existence, SHA-256 hashes, byte counts,
    per-artifact statuses, and aggregate missing/mismatch/invalid counts. No
    benchmark script emits those reports yet.
    `alphaevolve_ablations.json` defines the Figure 8 variant names and
    intended component assertions, but the registry is still
    `definition_only`: several assertion fields are declarative labels rather
    than executable `Config` switches, including `candidate_source`,
    `archive_admission_enabled`, `prompt_context_sections`,
    `candidate_workspace_mode`, `file_create_delete_enabled`,
    `ensemble_strategy: single_backend`, and `backend_capability_tier`.
    The `No full-file evolution` variant now carries a validated
    `paper_scope_boundary` that records AlphaEvolve's tensor-decomposition
    loss-function-only setup and marks the current localized single-file
    diff/no-topology scope as `not_equivalent`. That boundary still does not
    bind a target file, evolve block, symbol, or report field proving
    loss-function-only mutation.
    `libreevolve.llm_feedback_calibration.v1` now defines and tests a feedback
    grader calibration-report contract with declared graders, at least two
    calibrated tasks for readiness, per-grader/task scored records, finite
    normalized expected and observed scores, exact absolute-error consistency,
    and declared calibration artifacts.
    `libreevolve.llm_feedback_calibration_artifact_inventory.v1` verifies those
    calibration report, raw-record, grader-config, and plot artifacts against a
    safe artifact root. No runtime feedback-calibration fixture emits those
    reports yet. The committed `papers/feedback_calibration_boundary.json`
    sidecar now preserves this report-contract boundary for paper-manifest
    validation.

    Evaluator subprocess-attempt, configured-stage sample, retry, timeout, and
    sample/stage budget-exhaustion counters now persist in evaluation
    accounting and runtime manifests, and optional run-wide limits can stop on
    those detailed evaluator counters. Provider adapters now expose configured
    internal retry caps and per-call adapter retry telemetry, and
    `max_llm_provider_attempts` can stop before the next LLM call after those
    provider-internal attempts are recorded. `max_llm_tokens` and
    `max_llm_cost_microusd` can also stop before the next LLM call after
    provider usage or configured cost telemetry consumes those caps. LLM provider
    calls now have configured request timeouts/deadlines, and deadline-aware
    `LLMEnsemble` calls are clamped to the remaining `max_runtime_seconds`
    wall-clock budget before each attempt starts. Aborted runs
    after startup manifest creation now write runtime status, exception
    metadata, phase/role, budget snapshot, history-written status, and
    artifact/quarantine pointers before re-raising. Manifest writes are also
    serialization-safe and atomic for normal manifest creation/final runtime
    updates: rejected runtime payloads preserve the last valid `manifest.json`
    and append diagnostics to `manifest_invalid.jsonl`. Terminal
    seed/generated rows that consume evaluation or detailed evaluator-counter
    budgets now record the exhausted `metadata.budget.stop_reason`. Exhausted
    mutation-provider failures now write generated failure-history rows with
    bounded/redacted provider-failure metadata and retained LLM call telemetry,
    then continue later generations when budget remains. Built-in provider
    clients now accept configured request timeouts.
    `libreevolve.provider_cancellation_policy.v1` now defines and tests a
    policy/report contract for provider request timeouts, ensemble wait
    deadlines, runtime deadlines, hard cancellation rules, role-scoped budget
    actions, artifact requirements, required artifact-kind linkage,
    hard-cancel readiness gated on `cancellation_record` artifact evidence, and
    hashed cancellation artifacts. Runtime manifests now scope provider-timeout
    and ensemble-deadline rules to `mutation`, `critique`, `feedback:*`, and
    `meta_prompt`, while policy `runtime_readiness` keeps live provider SDK
    cancellation, timeout-driven stop enforcement, and cross-run provider
    quarantine resume false with overclaim validation. Rules for scopes with configured
    `llm_role_failure_quarantine_after` now declare timeout-driven
    `quarantine` actions and `quarantine_record` evidence, matching the
    ensemble's role/backend failure-threshold quarantine state. Runtime
    cancellation-policy records now also include
    `libreevolve.provider_cancellation_observations.v1`, derived from the
    validated LLM scheduler snapshot, with timeout-failure counts by role,
    configured quarantine thresholds, and quarantined backend counts when
    observed. `libreevolve.provider_cancellation_artifact_inventory.v1` now
    verifies declared timeout, cancellation, budget-stop, and quarantine
    artifacts against concrete files under an explicit artifact root, checking
    safe relative paths, existence, SHA-256 hashes, byte counts, per-artifact
    status, and aggregate missing/mismatch/invalid counts. Exhausted
    mutation timeout failures now write generated failure-history rows with
    retained timeout telemetry and can continue later generations when budget
    remains. Failed LLM call rows now record
    `provider_failure_policy` with retry/fallback decisions plus explicit
    quarantine/penalty decisions; configured
    `llm_role_failure_quarantine_after` roles can now quarantine exhausted
    failing role/backend pairs and apply zero-reward scheduler penalties to
    reward-accounted failures. Strict ledger replay now derives
    `provider_failure_policy_summary` for audit-only role/category/decision
    evidence, including role-specific remaining-gap counts for quarantine and
    cross-run-resume policy gaps. Ensemble-deadline timeout rows now also
    include a
    replay-validated `libreevolve.provider_cancellation_record.v1` with the
    role, backend, call id, timeout seconds, retry/fallback/telemetry budget
    action, and explicit `unsupported_daemon_worker_may_continue` hard-cancel
    gap. Remaining budget/runtime gaps are live hard cancellation handles,
    timeout-driven stop enforcement beyond audit observations, richer
    role-specific timeout/cancellation artifacts beyond configured in-run
    quarantine observations, accelerator/worker budget enforcement, live
    provider pricing/default-rate capture beyond configured token-cost
    estimates, provider-output/raw-payload replay beyond bounded retained
    diagnostics, and async/pending-work controller restore.
    `papers/provider_cancellation_boundary.json` now validates that this is
    policy/audit evidence, not live provider SDK hard cancellation,
    timeout-driven stop enforcement, cross-run provider quarantine resume,
    richer role-specific timeout artifacts, or provider-output raw-payload
    replay.
    `papers/expensive_evaluation_budget_boundary.json` now validates that the
    current compute-budget scope is local cooperative counters, not
    per-candidate compute-hour accounting, accelerator/worker lease
    accounting, async queue budgets, partial long-evaluation resume, or
    equal-budget benchmark execution reports. The remaining gap
    is not in-run role/backend failure quarantine state, strict
    provider-failure ledger summaries, restorable scheduler failure-policy
    state, remaining-runtime wait-deadline propagation, timeout call telemetry,
    mutation timeout failure-history logging, or one-command restoration of
    replayable provider-attempt/token/configured-cost/latency controller events
    for the current synchronous runtime bundle.
  - Required result: unify retry accounting across provider adapters and the
    ensemble, add accelerator/async-worker budget counters,
    connect hard cancellation semantics to runtime behavior beyond the current
    configured provider request timeout, ensemble `llm_call_timeout_sec`, and
    remaining-runtime wait deadlines, and add benchmark scripts that emit
    equal-budget ablation reports for real targets plus feedback-grader
    calibration reports for real reviewer/task suites. Those scripts must bind
    Figure 8 component assertions to actual supported config/runtime controls
    or fail when a named assertion is only declarative. For the `No full-file
    evolution` variant, keep the registry's non-equivalence boundary until a
    runner emits loss-function-only tensor-decomposition scope evidence rather
    than treating generic single-file/diff/no-topology settings as equivalent.
    For the `No evolution` variant, keep the registry's validated
    prompt-history-unproven boundary until executed prompt and history proof
    shows that each candidate is generated from the same initial program with
    no database-selected parent/inspiration programs, archive admission
    feedback, or previous-candidate resurfacing, rather than relying on
    declarative `candidate_source` or `archive_admission_enabled` labels.
    For the `No context in the prompt` variant, keep the registry's validated
    over-broad non-equivalence boundary until executed prompt-history and
    prompt-diagnostic proof shows explicit context sources were absent, require
    a paper-facing classification of local plugin/retrieval/failure sections
    as explicit context or core prompt ingredients, and separately record which
    current-program, parent, inspiration, and rendered-result sections remained
    present so this ablation is not conflated with `No evolution`. For the
    `Small base LLM only` variant, keep the registry's validated
    telemetry-unproven boundary until executed backend telemetry proves that
    every mutation-generation call used one configured small/base-capable model
    with no large-model backend eligibility, fallback, critique, or router
    leakage, rather than relying on declarative `single_backend`,
    `backend_count`, or `backend_capability_tier` labels. For the
    `No meta prompt evolution` variant, keep the registry's validated
    lineage-unproven boundary until executed prompt-history and call-ledger
    proof shows that meta-prompt calls, prompt-template mutations, and
    prompt-program lineage updates were disabled for the ablation while the
    full-system baseline had meta-prompt evolution enabled and mutable prompt
    variants. Also require the paper-facing result bundle to identify the
    frozen human-authored prompt source, revision, and context policy used for
    the human-prompter comparator, because Figure 8 motivates the ablation as
    testing whether meta prompts can surpass a human prompter rather than only
    whether a local meta-prompt role was toggled off. The
    remaining ablation and calibration gap is executing and
    emitting real reports from runnable variants over the Figure 8 matrix and
    kissing-number target families, linking those reports to matching
    evolutionary run artifacts, and rendering Figure 8-equivalent curve
    exhibits. The gap is not validating declared result or
    feedback-calibration artifacts once a report names them.
    The remaining provider cancellation gap is live cancellation/stop behavior,
    cross-run quarantine/resume behavior, and richer runtime artifact
    generation, not configured in-run role/backend quarantine observations or
    verifying declared cancellation evidence files once a policy names them.

- [ ] Track Figure 8 ablation-curve exhibit provenance as paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 8 shows two ablation
    plots: matrix multiplication tensor decomposition and the kissing-number
    problem. Each plot uses compute-budget fraction on the x-axis, aggregated
    target metric on the y-axis, named full/ablated method curves, and shaded
    intra-target standard deviation averaged over three independent seeded runs.
  - Current gap: paper-facing ablation TODOs require executable benchmark
    scripts, component-assertion bindings, target-family coverage,
    per-target aggregation, and three-seed traces.
    `libreevolve.alphaevolve_figure8_exhibit.v1` now preserves the Figure 8
    visual as its own paper exhibit metadata with stable exhibit/panel IDs,
    matrix/kissing panel mappings, series-to-variant legend mappings, exact
    paper legend labels including `Full method`, axis labels/scales,
    color/style/shading metadata, source caption references, rendered plot
    artifact hashes, and links from plotted curves to report, raw seed trace,
    and curve-summary artifacts. `figure8_exhibit_from_ablation_report()` now
    builds the two-panel exhibit from a validated equal-budget ablation report
    plus declared rendered/source artifacts, rejecting invalid reports and
    missing curve/raw trace links. It does not render a plot, verify named
    files exist, or prove the linked artifacts came from real ablation runs.
    The committed `papers/figure8_ablation_artifacts.json` sidecar now emits
    the current rendered-artifact absence boundary for paper-manifest
    validation.
  - Required result: emit Figure 8 exhibit records and rendered visual artifacts
    from runnable matrix/kissing ablation scripts, with source PDF page/caption
    location, concrete report/raw-trace/curve artifact hashes, rendering
    parameters, and run links so reproduced Figure 8 visual evidence remains
    separate from generic ablation-report validation.

- [ ] Connect LLM budget reports to async/pending-work resume and
  provider-output replay.
  - Paper evidence: AlphaEvolve-style systems use large but explicit compute
    budgets; provider retry settings should be bounded, attributable, and
    resumable rather than open-ended integers.
  - Current evidence: ensemble-layer retry counts are now capped at `10`, total
    original/retry/fallback attempts per logical ensemble call are capped by
    `llm_max_call_attempts`, and call telemetry records attempt index plus the
    configured cap. Live `max_llm_calls` accounting now clamps
    `LLMEnsemble.max_call_attempts` to the remaining call budget and records
    actual retry/fallback call-history attempt deltas into runtime/candidate
    budget snapshots. Provider adapters now expose `provider_max_retries` and
    `adapter_retry` telemetry for internal attempts, and role accounting now
    aggregates provider-reported token totals. `max_llm_provider_attempts` now
    consumes recorded adapter attempts as a live after-call stop input, while
    `max_llm_tokens`, `max_llm_cost_microusd`, and `max_llm_seconds` do the
    same for token, configured-cost, and retained LLM call-latency consumption.
    Per-role seconds limits use `llm_role_seconds_limits` and are surfaced in
    runtime budget snapshots and LLM budget-report rows. Role-budget limit maps
    now accept manifest-safe prefix scopes such as `feedback:*`, and shared
    scoped caps are enforced by summing matching exact-role logical calls,
    provider attempts, tokens, configured cost, and retained call latency while
    keeping consumed counters concrete. Runtime manifests now persist a
    compact `runtime.llm_accounting` summary with role totals plus active
    logical-call, retry/fallback, timeout, prompt, and accepted-output caps,
    `libreevolve.llm_budget_report.v1` now defines and tests paper-index-visible
    retry-budget report semantics for mutation, critique, and feedback roles,
    adapter-internal attempts, token/cost/wall-clock limits and usage, and
    persisted resume-state hashes. Current reports use status
    `cooperative_enforcement_snapshot` and policy
    `runtime_cooperative_budget_enforcement_v1`, and the validator rejects
    stale audit-only policy labels plus invalid `role_scheduler_scope` values.
    `libreevolve.llm_budget_resume_artifact_inventory.v1` now verifies
    optional LLM budget `resume_state.artifacts[]` records against an artifact
    root, including safe relative paths, file existence, SHA-256 hashes, byte
    counts, per-record statuses, aggregate missing/mismatch/invalid counts, and
    a stable records hash. `validate_llm_budget_evidence_bundle()` now checks
    LLM budget reports together with resume artifact inventory, requiring
    matching run id, report schema, resume-state hash, inventory status,
    aggregate counts, zero missing/mismatch/invalid records, and inventory
    record-hash consistency before accepting bundled paper-budget readiness.
    Final manifests now emit `runtime.llm_budget_report`
    instances with observed per-role logical-call, retry, provider-attempt,
    usage counters, configured estimated cost, retained LLM latency, and
    scheduler-resume-hash evidence, role scheduler scope, and self-validation,
    and retained LLM call-history rows now provide per-call provider-internal
    retry records grouped by role plus configured-cost source metadata. Final
    manifests also emit `runtime.llm_provider_diagnostics` using
    `libreevolve.llm_provider_diagnostics.v1`, a retained-call-history
    aggregate that groups backend/API-mode usage, bounded provider diagnostic
    keys and omitted counts, provider response/error retention modes and
    policies, retained hash/text/character counts, redaction/truncation
    counts, configured cost-estimate evidence, not-estimated reasons, backend
    defaults, call-history retention, and a records hash while explicitly
    avoiding full raw provider-payload and live-pricing claims.
    `papers/llm_budget_policy_boundary.json` now keeps role-level LLM budget
    reporting scoped to cooperative snapshots rather than async pending-work
    budget accounting or provider-output replay for budget resume.
    `validate_provider_capability_lookup_policy()` now validates
    `libreevolve.provider_capability_lookup_policy.v1` records for static-only
    provider lookup boundaries, OpenAI API-mode policy linkage, offline
    compatibility, record count/hash integrity, and explicit non-use of live
    model-registry, service/API-version, or account-availability discovery,
    including false capability-readiness flags for those surfaces.
    The committed `papers/config_validation_boundary.json` sidecar now records
    the paper-facing local-effective-config-only boundary while keeping live
    provider/model API compatibility, provider service/API-version capture,
    account availability, provider default discovery, and complete plugin-
    specific schemas as missing evidence.
    `validate_llm_provider_diagnostics_summary()` now validates the provider
    diagnostics summary contract, including record-hash integrity,
    non-negative counters, backend-count, total/backend aggregate count and
    retention-counter consistency, required limitation statements, and the
    no-live-pricing/no-raw-payload replay boundary. The budget report contract
    now rejects restored-state claims that lack persisted resume-state
    evidence. Focused ensemble tests now cover fake provider usage counts and
    adapter retry diagnostics for mutation, critique, feedback, and
    meta-prompt roles. Controller budget `llm_call` events now validate and
    replay role-tagged provider attempts, tokens, configured cost, and latency
    seconds into `RunBudget`, and full-runtime restore now replays contiguous
    controller budget events, verifies non-wall-clock consumed counters against
    the manifest budget snapshot, and passes that checked budget snapshot into
    `evolve()`. `validate_controller_budget_replay_state()` now exposes that
    provider-attempt/token/configured-cost/latency replay proof as a reusable
    budget contract and rejects snapshot drift before restored consumption is
    trusted.
  - Current gap: runtime enforcement is still incomplete for full restored
    controller state. LLM budget reports now describe cooperative live
    enforcement snapshots rather than audit-only evidence. LLM budget deltas
    are replayable through validated
    controller events, and prior manifest runtime budget snapshots can now be
    restored through direct `evolve()` calls or CLI
    `--restore-budget-from-manifest` before new work. Exhausted restored
    provider-attempt, token, configured-cost, latency, or wall-clock usage can
    therefore trip the same live stop checks in the resumed run. However,
    restored controller state is not yet connected to pending-work queues,
    async worker state, or provider-output replay. The remaining gap is not
    LLM budget resume artifact inventory, bundle-consistency verification, or
    current-report policy/status validation.
  - Required result: connect restored LLM budget state to async controller
    queues, pending-work restore, provider-output replay boundaries, and
    executed equal-budget ablation runs before treating local LLM ensemble
    scheduling as AlphaEvolve-grade budgeted search. The remaining gap is not
    provider-attempt/token/configured-cost/latency replay through the current
    synchronous controller budget stream.

- [ ] Add remaining full-run replay, lineage, provider, and custom-plugin
  provenance policy.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: task setup and evaluation code define what a run means, and
    long-running experiments need reproducible accounting for the code,
    evaluators, and generated program database.
  - Partial status: run identity and collision semantics are implemented.
    `manifest.json` records a UUID4 `run_id` and effective collision policy.
    Existing known run artifacts now fail startup by default; explicit
    `overwrite` removes only known run artifacts before the new run. Configured
    `validate_path` entries are constrained to problem-local Python files, and
    direct evaluator entrypoints are recorded in `manifest.json` with redacted
    problem-relative path labels, path hashes, streamed SHA-256 source hashes,
    byte counts, source type, source-hash policy/status, and stage usage
    metadata, plus bounded sibling helper/data `companion_sources` under each
    evaluator directory with streamed hashes, byte/count caps, skipped-file
    diagnostics, and a deterministic aggregate hash. Package-style evaluator
    directories containing `__init__.py` are imported as packages and hashed as
    package entrypoints. Declared evaluator data globs are hashed under
    `declared_data_sources` and passed to validators through
    `stage["evaluator_data"]`. The manifest also records Git state when
    available, `libreevolve/` source-tree hashes, problem-tree hashes, and
    plugin module file hashes. Runtime finalization now records aggregate
    emitted-artifact hashes for known artifact files/directories and
    `runtime.plugin_state.loaded_specs` records validated constructor
    parameters for built-in loaded plugin instances. Built-in plugin config
    specs now validate supported constructor options before construction, and
    configured entry-point plugin classes can publish declared constructor
    option schemas that reject unknown or malformed options before
    instantiation. Entry-point plugin specs also record configured paper-
    inspiration labels and distribution name/version plus hash-only RECORD/WHEEL
    metadata when available. Custom direct plugin specs record constructor
    signature shape without parameter values, while direct-plugin policy
    readiness keeps direct constructor values/schemas, direct custom registries,
    and arbitrary instance-state capture false. Captured direct-plugin
    constructor values, arbitrary direct-plugin schemas, and richer custom
    package policy beyond entry-point distribution records remain part of the
    broader plugin registry gap. Problem-local evaluator
    helper/data access is now governed by an enforced declared-dependency
    policy: validator imports and file reads may touch only the configured
    entrypoint, captured companion sources, or captured declared data sources.
  - Current gap: seeded replay is still incomplete, but the identity gap is narrower than
    the older paper-audit wording: loop-created seed and generated candidate
    ids are deterministic, and `PromptDatabase` creates deterministic ids for
    configured seed templates and prompt mutations. Direct `Program()` and
    direct `PromptProgram()` construction still default to UUID4 values unless
    callers provide ids, and the deterministic ids are not yet composed with a
    full run-resume/replay contract across provider outputs, archive restore,
    controller state, and migration ordering. Runtime manifests now declare
    `runtime.lineage_replay_policy`, and full-runtime restore validates and
    packages that provider-output non-replay boundary as checked metadata.
    Full-runtime restore now also emits
    `libreevolve.full_resume_bundle_validation.v1`, validating the composed
    runtime RNG, LLM scheduler, archive restore, runtime budget,
    controller-budget replay, lineage boundary, and unsupported-surface list
    while keeping full replay, provider-output replay, pending-work resume, and
    resumed-trace proof marked unavailable. It also emits
    `libreevolve.full_resume_restore_certification.v1`, certifying compatible
    local manifest restore inputs and the accepted/quarantine boundary without
    claiming provider-output replay, pending-work resume, or end-to-end resumed
    trace proof; resumed runs now persist that certification under
    `runtime.restore_certification`, with `libreevolve show`, CLI restore
    preflight, direct runtime loaders, and direct archive restore loaders
    validating the persisted record and rejecting forged certification
    overclaims before trusting the manifest.
    The paper manifest now requires
    `papers/lineage_replay_boundary.json` to preserve the deterministic
    lineage-id policy, direct UUID exclusions, and provider-output non-replay
    boundary. But
    this still stops short of an end-to-end replay trace that proves identical
    provider outputs or resumed lineage. Validator subprocesses now use an
    explicit
    minimal environment plus `validator_env_allowlist`, so `.env` provider
    credentials are hidden by default and persisted stdout/stderr is
    secret-redacted. Network egress policy and stronger sandboxing remain
    incomplete. Validator timeouts now attempt process-tree cleanup and record
    cleanup metadata, but this is not a full resource sandbox.
    `validate_validator_execution_policy()` now validates startup
    `libreevolve.validator_execution_policy.v1` records for honest local
    subprocess execution, unsupported sandbox/container claims,
    filesystem-capability structure, network mode and denial scope,
    wall-clock-only limits, unsupported CPU/memory/GPU/disk/process-count
    quotas, and the required per-evaluation boundary pointer.
    `validate_validator_boundary_consistency.v1` now checks that attempt-level
    `evaluation.metadata.validator_boundary` records match the startup policy
    across execution, filesystem-capability, network, resource-limit, and
    secret-boundary claims while still marking the full sandbox unavailable.
    The paper manifest now requires `papers/validator_execution_boundary.json`
    to preserve the local-subprocess policy boundary separately from
    OS/container sandbox and resource-quota enforcement.
    Problem-local
    evaluator helper modules are imported as sibling modules beside a
    configured validator file or through package-relative imports for package
    validators; declared evaluator data files are hashed and exposed through
    stage context. Undeclared or over-budget problem-local helper/data access
    now fails during preflight or evaluation instead of running outside
    manifest provenance.
    Validator helper import precedence is now explicit: the validator directory
    precedes the materialized candidate workspace on `sys.path`, so
    problem-local evaluator helpers win same-name import collisions while
    candidate-local imports still work when they do not collide.
    Run artifact path confinement now rejects unsafe scalar run names and
    validates the resolved run directory before cleanup or writes, so
    symlink/junction escapes outside the resolved `log_dir` fail instead of
    being followed during overwrite startup.
    Known artifact directories inside a valid run directory are now
    individually link-checked before overwrite cleanup: `ProgramDatabase(...,
    overwrite)` rejects symlink or Windows-junction entries such as
    `best_workspace/`, `evaluator_artifacts/`, or `plugin_artifacts/` before
    deleting any artifact, with tests for symlink-capable platforms and Windows
    junctions.
    Unknown run-directory entries are now an explicit preserve-and-diagnose
    policy. Startup preserves unknown immediate files/directories under both
    `fail` and `overwrite`, treats them as outside the run-owned artifact set,
    and records count, entry type, and hashed immediate names in
    `manifest.json` without exposing raw filenames.
    Paper-facing generated-artifact lifecycle evidence now has a unified
    inventory for standalone `task_specification.json`, generated prompt
    tables, quarantine streams, non-JSONL artifacts, and `paper_artifacts/...`
    source/exhibit directories. The inventory is tied to collision/overwrite
    cleanup, schema pointers, runtime pointers, restore/show handling
    boundaries, source-level writer/runtime-pointer/show-restore anchors,
    docs anchors into `docs/run-artifacts.md`, and behavior-test anchors for
    the shared cleanup contract, quarantine stream show-time diagnostics,
    prompt-table emitted rows, non-JSONL show/restore policy, and
    `paper_artifacts/...` emitted-path/show/restore lifecycle tests.
    `libreevolve show` also emits a bounded run-artifact bundle summary that
    reconciles present accepted JSONL streams, validated quarantine
    diagnostics, non-JSONL policy checks, and paper-artifact lifecycle checks
    for manifest-backed runs. Completed and aborted manifests persist
    `runtime.run_artifact_bundle_report` with the same audit boundary,
    including explicit false provider-output replay, pending-controller replay,
    quarantine-replay-as-state, and full restore certification fields.
    New persisted reports include a promotion gate recording manifest
    finalization-time schema/overclaim validation without claiming restored-run
    replay certification.
    `libreevolve show`, CLI restore flags, and direct runtime/archive restore
    loaders validate that persisted report and reject overclaims before
    accepting the manifest. CLI and direct restore loaders also validate
    manifest-advertised quarantine streams before consuming restored runtime,
    scheduler, budget, lineage, or archive state, preserving quarantine rows as
    diagnostics rather than accepted replay state.
    Paper-facing generated-artifact lifecycle evidence is still incomplete:
    those anchors prove source/docs text presence plus current behavior-test
    coverage, show-time bundle reconciliation, persisted and reader-validated
    audit reporting, promotion-gate status, and restore-side diagnostic guards,
    not end-to-end replay of prompt-table and `paper_artifacts/...` evidence
    across restored runs.
    Run names now share the runtime identity secret-safety policy: assignment-
    style secret strings and provider-token-shaped values are rejected before
    filesystem or manifest writes, while ordinary portable run names remain
    valid.
    CLI plugin preflight now validates built-in plugin aliases before
    run-directory preparation, rejects empty and whitespace-only plugin
    identifiers in config, and validates TTTRL/DeepResearch cadence constructor
    values before hook execution. Built-in OpenAI/Anthropic credential checks
    and backend client construction now run before destructive cleanup when a
    mutation LLM can execute. Zero-generation baseline runs are provider-free:
    LLM backends are constructed lazily only when a mutation LLM call is needed,
    and CLI tests cover `--max-generations 0` with an OpenAI backend and no
    provider credentials.
    Dotenv/provider environment precedence is now isolated from import:
    `libreevolve.cli` imports do not load `.env`, `show` remains provider-free
    while selecting candidates from streamed history and reading bounded
    manifest runtime/export status, and the `run` command loads `.env` with
    `override=True` during provider setup while recording non-secret source
    metadata in the run manifest.
    The backend preflight guarantee is now a core runtime invariant for
    mutation-capable runs: direct `evolve()` constructs configured backend
    clients before run-directory preparation, and tests prove missing OpenAI
    credentials preserve existing overwrite-mode history and write no
    replacement manifest.
  - Required result: add true full-run resume/replay semantics, deterministic
    lineage-id behavior or an explicit UUID identity exclusion from the replay
    contract, provider-output replay boundaries, arbitrary direct-plugin
    constructor value/schema policy, richer custom plugin package provenance
    beyond entry-point distribution records, and live authenticated provider
    request/model-registry evidence beyond credential-presence and local client
    construction.
    The remaining paper gap is not deterministic loop-created ids, direct UUID
    exclusion, the runtime lineage policy validator, or the lineage sidecar; it
    is full resumed lineage proof across provider output, archive/controller
    resume, migration ordering, plugin state, and validator subprocess
    boundaries, plus restored-run replay/certification evidence for paper-cited
    prompt-table and `paper_artifacts/...` artifacts beyond the current unified
    inventory, source-anchor checks, docs-anchor checks, and behavior-test
    anchors plus show-time bundle reconciliation, persisted audit reporting,
    and restore-side diagnostic guards.
    Startup ordering for positive-generation all-invalid seeds is now
    documented and tested as a conservative provider-readiness contract: if a
    mutation LLM could execute, provider preflight runs before seed evaluation
    in both CLI and direct runtime. This protects artifacts but intentionally
    prevents provider-free startup diagnostics for all-invalid seeds in
    mutation-capable runs.
    Credential presence now requires non-blank OpenAI/Anthropic environment
    variables after trimming before CLI mutation runs can reach overwrite
    cleanup or `evolve()`. Remaining provider-readiness gaps are that local
    preflight still does not prove live provider authentication, and the
    explicit non-blank credential trim check is CLI-scoped while core runtime
    preflight relies on backend client construction. The AlphaEvolve table now
    scopes the open provider-auth gap to live authenticated request/model-registry
    validation rather than implying credential-presence and client-construction
    preflight are absent.

- [ ] Extend paper-facing validator-boundary consistency evidence beyond CLI
      inspection.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: run artifacts that support generated-program evaluation
    claims should preserve and verify the validator execution boundary used by
    each candidate attempt.
  - Partial status: `manifest.json` records
    `policies.validator_execution`; evaluator metadata records include
    `evaluation.metadata.validator_boundary`; failure-history summaries retain
    selected validator-boundary metadata; and
    `validate_validator_boundary_consistency()` can compare the manifest policy
    with an attempt boundary across execution, filesystem-capability, network,
    resource-limit, and secret-boundary claims. Direct validator-policy tests
    cover matching and mismatched records.
    `validate_run_artifact_validator_boundary_consistency()` now applies the
    contract across manifest-backed `history.jsonl` and
    `failure_history.jsonl` rows; `libreevolve show` invokes the gate and
    reports stream/line diagnostics for missing, legacy, or drifting boundary
    metadata. The paper manifest now requires
    `papers/validator_artifact_promotion_boundary.json` to preserve this
    CLI-inspection gate separately from run-finalization, CI, or release-
    artifact promotion enforcement.
  - Current gap: the paper-facing artifact surface has a CLI inspection gate,
    but no run-finalization, CI, or release-artifact promotion gate that
    requires persisted policy-to-attempt boundary consistency before archiving
    benchmark evidence. The remaining gap is not the CLI/show artifact gate or
    its paper sidecar; it is promotion-time enforcement.
  - Required result: add promotion-time validation/report evidence for
    policy-to-attempt boundary consistency while keeping this artifact gate
    separate from the broader missing OS/container sandbox and resource-quota
    enforcement.

- [ ] Integrate restored run-local RNG with full AlphaEvolve replay claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: long-running AlphaEvolve-style experiments should own and
    persist their stochastic state without resetting an embedding application's
    process-global Python RNG.
  - Current evidence: framework-owned parent selection, inspiration sampling,
    prompt-template sampling, island sampling, and MAP-Elites random sampling
    use an explicit run-local RNG without perturbing caller process-global RNG
    state. Completed and aborted runtime manifests persist checked
    `runtime.rng` snapshots with schema `python.random.mt19937.v1`, configured
    seed, JSON-safe `random.Random.getstate()` state, `state_sha256`, and the
    `random.Random.setstate` restore entrypoint.
    `load_runtime_rng_state_snapshot()` and
    `restore_runtime_rng_state_snapshot()` validate persisted snapshots; direct
    `evolve()` callers can pass `runtime_rng_state_snapshot`; CLI runs can pass
    `--restore-rng-from-manifest`; and seed mismatches are rejected before
    `evolve()`. `runtime.rng.replay_boundary` records the framework-owned RNG
    surfaces covered by restore plus explicit exclusions for LLM provider
    outputs, plugin internal randomness, and validator subprocess randomness,
    while validation normalizes older boundaryless snapshots.
    `load_full_resume_bundle()` now surfaces the validated replay boundary as
    explicit restore metadata beside the RNG snapshot and lineage replay policy.
    The paper manifest now requires
    `papers/runtime_rng_replay_boundary.json` to preserve that framework RNG
    restore boundary separately from full resumed sampling replay.
  - Current gap: full run replay still lacks provider output replay,
    plugin-owned RNG capture, controller/pending-work state restore, and
    lineage replay.
  - Required result: compose persisted RNG restore with full resume/replay,
    define provider-output and plugin-owned RNG capture or exclusion semantics,
    and keep paper-index seeded-replay claims scoped so they do not imply full
    replayability until this is true. The remaining paper gap is not the
    runtime RNG snapshot validator or paper sidecar; it is the resumed trace
    composition across external stochastic surfaces.

- [ ] Promote multiple-score overlays to primary archive optimization.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: optimize multiple user-provided scores and use programs that
    excel under different criteria as varied inspirations.
  - Partial status: metric vectors are stored, normalized primary fitness
    honors direction/bounds, and declared numeric metrics are normalized into
    a configurable archive `selection_score` used for MAP-Elites replacement,
    elite ordering, and exploit/best sampling. The default selection score is
    an equal-weight normalized-metric mean, and optional finite non-negative
    `metrics.yaml` metric `weight` values switch it to a weighted normalized
    declared-metric policy. Archive admission metadata and migration event rows
    now carry an `objective_vector` audit record with the finite normalized
    metric vector plus selection policy when available, and `show`
    validates/prints bounded selected objective-vector summaries.
    Runtime manifests now include `runtime.history.objective_frontier`, a
    bounded diagnostic Pareto frontier over complete declared normalized metric
    vectors, plus `runtime.history.objective_metric_leaders`, a diagnostic
    best-program view for each declared normalized metric, and
    `runtime.history.objective_metric_archives`, a bounded top-program view for
    each declared normalized metric. Runtime manifests now also include
    `runtime.history.lineage_index`, a bounded diagnostic best-valid-programs
    view grouped by root lineage, and `runtime.history.descriptor_index`, a
    bounded diagnostic top-program view for finite archive-admission descriptor
    values. Runtime manifests now also include `runtime.history.score_index`, a
    bounded diagnostic top-valid-program view ranked by selection score and
    final fitness. Runtime manifests now also include `runtime.history.feedback_index`,
    a bounded diagnostic feedback-record view grouped by LLM feedback grader.
    LLM
    feedback graders now support
    bounded raw scores, maximize/minimize direction, normalized fitness-delta
    composition, and `objective_metric: true` filling for declared non-primary
    `source: feedback` objective metrics. Declared non-primary
    `source: plugin` metrics can be filled by plugin hooks through validated
    metric side effects and then participate in normalized objective selection
    and metric-specific views. Declared non-primary `source: final_fitness`
    metrics are synthesized from the candidate's final composed fitness after
    plugin score hooks run, so plugin-adjusted top-level fitness can be included
    in the declared objective vector when desired.
  - Current gap: metric-specific archive replacement and
    Pareto/frontier optimization remain open because the frontier and
    metric-specific views are diagnostic and not archive replacement policies.
    Parent and inspiration sampling can now use
    metric-leader, frontier, lineage, novelty, recency, selection-score, random, and mixed
    strategies while excluding the selected parent and deduplicating migrated
    copies by program id. Bounded score-ranked manifest evidence is now
    available. Durable persisted feedback ranking and full cross-run
    database resurfacing remain open. Metric bounds are now strictly ordered before they
    can be used as policy inputs. Metric-leader parent sampling now cycles
    through primary and secondary metric targets in configured order and
    persists target-metric provenance. Metric-leader inspiration sampling now
    persists selected ids plus metric target/program pairs in generated
    candidate metadata. Frontier parent/inspiration sampling uses complete
    declared normalized metric vectors to surface non-dominated retained
    programs and persists frontier size/metric-order provenance. Lineage
    parent/inspiration sampling uses root lineage metadata to surface the best
    retained representative per root, persists lineage-root provenance, and
    exposes bounded lineage-index evidence in final manifests. Descriptor-index
    evidence makes insertion-time diversity/complexity/performance coordinates
    inspectable from run artifacts, and feedback-index evidence makes
    grader-specific scores, deltas, retention summaries, and failure/discard
    status inspectable. MAP-Elites archives now retain a bounded
    non-dominated Pareto archive over complete declared normalized metric
    vectors, persist/restore Pareto frontier program ids and the objective
    archive policy, and allow island metric/frontier retained pools to sample
    Pareto-only programs that lost scalar cell/elite placement. MAP-Elites
    archives now also persist/restore `metric_cell_archives`, per-declared
    objective metric descriptor-cell overlays that retain best programs by each
    normalized metric and feed metric/frontier retained pools, so programs can
    survive for excelling in a specific metric even when they lose scalar
    primary-cell placement. The AlphaEvolve table now scopes the open
    multi-objective search gap to Pareto/frontier primary archive replacement
    and durable cross-run metric-specific optimization rather than claiming all
    frontier or metric-specific search remains absent. Runtime
    manifests now include `runtime.history.resurfacing_index`, a bounded
    deterministic rank-fusion view over score, metric, frontier, lineage,
    descriptor, and feedback indexes, and `ProgramDatabase.resurface_candidates()`
    returns defensive ranked snapshots from that same source mix.
    `ProgramDatabase.resurface_candidates(target_metric=...)` now exposes
    declared-metric-targeted resurfacing over the objective metric archives and
    rejects undeclared metric targets. `ProgramDatabase.resurface_by_metric()`,
    `resurface_by_lineage()`, `resurface_by_descriptor()`,
    `resurface_by_novelty()`, and `resurface_by_feedback()` now expose
    defensive run-local query results from the bounded metric, lineage,
    descriptor/novelty, and feedback views.
    `validate_resurfacing_index_summary()` now validates that
    `libreevolve.resurfacing_index.v1` record for schema/policy, required
    limitations, counts, source contributions, source records, normalized
    objective evidence, and deterministic rank order while preserving
    `durable_database_ready: false`.
    The paper index now includes a dedicated database-resurfacing note that
    lists the bounded current-run resurfacing APIs and narrows the remaining
    AlphaEvolve gap to durable cross-run query/index tables, full
    metric-vector and feedback/artifact-content ranking, semantic/cross-run
    novelty or hypothesis retrieval, schema migrations, and replayable
    sampling policies.
    `validate_objective_history_summary()` now validates the runtime
    multi-objective diagnostic history bundle across objective frontier,
    metric leaders, and metric archives, including schema/policy values,
    shared metric order, non-negative counters, retained-count and
    retention-limit consistency, normalized metric ranges, non-dominated
    retained frontier records, and explicit diagnostic-not-primary-archive
    limitation statements.
    `validate_map_elites_objective_archive_policy()` now validates
    `libreevolve.map_elites_objective_archive_policy.v1` snapshot policy
    records and rejects overclaims that bounded Pareto/frontier retention has
    replaced the primary scalar MAP-Elites cell policy. Objective archive
    policies now also carry
    `libreevolve.map_elites_objective_archive_readiness.v1` with false
    readiness for primary Pareto/frontier replacement, durable cross-run
    metric databases, metric-target persistence tables, and runtime
    feedback-calibration runners; validation rejects forged readiness
    overclaims. `papers/objective_archive_boundary.json` now validates this
    retained-overlay and diagnostic-frontier boundary.
    `runtime.history.failure_index` now groups failure records by fingerprint
    with bounded repetition/latest-record evidence, and
    `papers/failure_memory_boundary.json` validates this run-local diagnostic
    boundary rather than durable cross-run failure tables, semantic
    failed-proposal retrieval, learned repetition avoidance, replayable
    failed-mutation payloads, failure-aware sampling policy, or cross-run
    failure-index migrations. `runtime.history.hypothesis_index`
    now exposes bounded redacted proposal idea/rationale/hypothesis evidence
    and feeds hypothesis records into `resurfacing_index`. This remains a
    heuristic rather than a paper-faithful multi-score database policy:
    primary MAP-Elites cell replacement is still scalar, Pareto/frontier
    dominance does not replace the primary grid, and durable queryable
    multi-objective resurfacing across persisted database tables, embeddings,
    cross-run failure and hypothesis indexes, semantic failed-proposal
    retrieval, learned repetition avoidance, replayable failed-mutation
    payloads, failure-aware sampling policy, cross-run failure-index
    migrations, full artifact-content indexes, output-similarity or
    schema-aware program-output indexes, full lineage subgraphs, learned/
    cross-run novelty indexes, and schema migrations remains open.
    Current evaluator outputs/program outputs can be captured, redacted,
    checked, rendered to prompts, indexed under
    `runtime.history.program_output_index`, and fed into current-run
    `resurfacing_index`; `resurface_by_program_output()` can query them by
    exact source key and/or output hash. They are still not a durable or
    semantic resurfacing dimension despite AlphaEvolve's database storing
    solutions with attached evaluation results and program outputs.
    `papers/program_output_boundary.json` now validates this exact current-run
    output lookup boundary.
    `runtime.history.artifact_index`
    now exposes bounded evaluator-artifact path/hash, redaction, skipped-file,
    stage, and content-excerpt evidence, and valid artifact-bearing candidates
    feed into `resurfacing_index`.
    `papers/artifact_index_boundary.json` now validates that this remains
    bounded current-run artifact metadata/content-excerpt evidence, not durable
    full-content or semantic artifact search.
  - Required result: add Pareto/frontier archive replacement and durable
    persisted lineage-aware resurfacing for programs that excel under different
    metrics, including durable output-aware indexes and similarity/schema
    retrieval for attached program outputs beyond exact current-run source/hash
    filtering.

- [ ] Extend multiple-score prompt-diversity evidence into benchmark policy.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: AlphaEvolve says multiple scores can help even when one target
    metric matters because prompts include programs with different structures
    and logic that excel under different evaluation criteria, each representing
    a different definition of "good".
  - Partial status: LibreEvolve records declared metric vectors, metric leaders,
    objective frontiers, metric-cell overlays, metric-targeted resurfacing, and
    selected parent/inspiration target-metric provenance. Prompt context policy
    can filter and rank inspirations by metric. Generated candidate metadata
    now records `metadata.inspiration_selection.metric_diversity`, including
    prompt-visible inspiration ids, metric-niche labels, raw/normalized metric
    values, prompt hash linkage, and whether a rendered prompt spans at least
    two metric niches. Completed manifests summarize this at
    `runtime.history.metric_diverse_inspiration_report`, whose
    `libreevolve.metric_diverse_prompt_benchmark_boundary.v1`
    `benchmark_policy` keeps benchmark-required policy, cross-run fixture,
    scalar/single-metric comparison, and AlphaEvolve Section 2.4 readiness
    false. The report also carries
    `libreevolve.metric_diverse_benchmark_comparison_readiness.v1`, keeping
    benchmark prompt-policy enforcement, cross-run fixtures, scalar-only
    baselines, single-metric baselines, and equal-budget comparison reports
    false with overclaim validation.
    `papers/metric_diverse_prompt_boundary.json` now validates this
    prompt-visible-evidence-only boundary.
  - Current gap: the paper/status surfaces still do not require benchmark runs
    to use metric-diverse prompt slates, compare those runs with scalar archive
    sampling, or provide cross-run fixtures for different definitions of
    "good" in one prompt.
  - Required result: add benchmark policy/report validation that multi-score
    benchmark runs can distinguish scalar archive sampling from prompts that
    show different definitions of "good" at once.

- [ ] Extend proposal scoring into semantic hypothesis retrieval.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.4.
  - Requirement: prior ideas and hypotheses should be reusable as searchable
    evolutionary evidence, with proposal quality and novelty reflected in
    future selection rather than only attached as candidate metadata.
  - Partial status: mutation outputs can include bounded `IDEA`, `RATIONALE`,
    and `HYPOTHESIS` proposal metadata. `runtime.history.hypothesis_index`
    exposes bounded redacted proposal idea/rationale/hypothesis summaries for
    valid programs, sorted by scalar selection score/final fitness/generation,
    and feeds hypothesis evidence into the run-local resurfacing index. Recent
    proposal-hypothesis terms can also feed DeepResearch retrieval queries.
    Completed manifests now include `runtime.history.proposal_score_report`,
    which records current-run proposal scores from candidate outcome quality
    and exact proposal-signature first-occurrence novelty.
  - Current gap: proposal scores are bounded heuristic records, not calibrated
    hypothesis-quality models, embedding/semantic proposal indexes, cross-run
    persisted proposal tables, or a policy that lets proposal scores influence
    retrieval, prompting, and archive resurfacing.
    `papers/proposal_score_boundary.json` now validates this bounded
    current-run proposal-score boundary.
  - Required result: add semantic/cross-run proposal-hypothesis retrieval,
    calibrated proposal-quality and novelty models, persisted proposal-index
    tables, and prompt/retrieval/archive policy boundaries before treating
    proposal metadata as AlphaEvolve-grade idea memory.

- [ ] Extend initial-pool divergence evidence beyond bounded syntactic and
      metric reports.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Introduction.
  - Requirement: AlphaEvolve says LLMs responding to feedback can discover
    candidates substantially different from the initial candidate pool in both
    syntax and function.
  - Partial status: completed manifests now include
    `runtime.history.initial_pool_divergence_report`, which compares generated
    candidates against generation-0 seed programs with canonical workspace
    hashes, bounded primary-file text distance, changed-component summaries,
    and numeric metric L1 distance over shared metric names.
    `papers/initial_pool_divergence_boundary.json` now validates this as
    telemetry-only evidence, not functional discovery-distance proof.
  - Current gap: paper-facing evidence still does not include evaluator-output
    distance, task-specific functional-difference artifacts, behavior/output
    distance, or thresholds proving that accepted candidates moved
    substantially away from the starting pool in function. It also lacks
    cross-run discovery-distance tables and a syntax/function joint claim gate.
  - Required result: add functional-difference artifacts, behavior/output-
    distance metrics, evaluator-output distance metrics, thresholds for
    "substantially different" claims, benchmark-level discovery-distance
    telemetry, cross-run discovery-distance tables, and a syntax/function joint
    claim gate before using AlphaEvolve-style functional discovery-distance
    wording.

- [ ] Extend run-local duplicate-work cache into durable paper-visible memory.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: AlphaEvolve's generated-program database stores previously
    explored programs with evaluation results and program outputs under fixed
    search budgets, so repeated identical programs need an explicit
    resurfacing/reuse/re-evaluation policy.
  - Partial status: generated candidate ids include a workspace hash, and
    database/history restore paths validate unique program ids. Completed
    manifests now include `runtime.history.duplicate_work_policy_report`, which
    groups identical runtime workspaces, records cache stores/hits, and states
    that diff-error-free exact workspace matches reuse a run-local evaluator
    result keyed by canonical workspace hash plus evaluator-contract hash.
    Cache hits emit replayable `candidate_evaluation_cache_hit` controller
    events and do not consume evaluator-call budget.
    `papers/duplicate_work_policy_boundary.json` now validates this as
    run-local exact-cache evidence only.
  - Current gap: the cache is still run-local and exact-match only. The paper
    index has no evidence for durable cross-run lookup, resume-spanning cache
    replay, cache invalidation/migration policy, stochastic re-evaluation
    policy, semantic near-duplicate handling, source/output-aware duplicate
    indexes, or an AlphaEvolve-grade fixed-budget memory claim gate.
  - Required result: add paper-visible durable cache/reuse policy proving how
    repeated source/workspace proposals are skipped, reused, replayed across
    runs/resumes, or intentionally re-evaluated as stochastic samples with
    documented invalidation/migration semantics and budget effects.

- [ ] Extend exploration/exploitation sampling-balance evidence into calibrated
      strategy comparisons.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: AlphaEvolve's evolutionary database balances exploration and
    exploitation, improving the best programs while maintaining enough
    diversity to explore the search space.
  - Partial status: LibreEvolve exposes `explore_ratio`, `mixed` parent
    selection, explicit parent and inspiration strategies, MAP-Elites cells,
    island pools, metric/frontier/lineage/novelty/recency sampling paths, and
    selected parent/inspiration metadata in candidate history. Completed
    manifests now include `runtime.history.sampling_balance_report`, with
    per-run and per-generation parent/inspiration decision counts, mixed
    explore/exploit counts, inspiration strategy source counts, metric target
    counts, frontier/lineage indicators, validators, and the committed
    `papers/sampling_balance_boundary.json` local-counts-only sidecar.
  - Current gap: paper-facing reports still do not connect sampling decisions
    to fallback source-pool provenance, selected-program repetition,
    island/cell/metric/lineage/descriptor coverage, score improvement,
    diversity coverage, budget impact, equal-budget strategy comparisons, or
    calibrated AlphaEvolve-grade database-balance policy. The paper index
    therefore cannot yet claim measured AlphaEvolve-style balance under equal
    budgets.
  - Required result: add calibrated sampling-balance evidence with selected-
    program provenance, fallback source-pool accounting, diversity and
    exploitation metrics, budget impact, and equal-budget comparisons of pure
    exploit, pure explore, default mixed, and metric/frontier/lineage variants.

- [ ] Extend AlphaEvolve's automated-evaluator scope boundary into robust
      environment fixtures.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 context, Related Work, and
    Discussion.
  - Requirement: AlphaEvolve explicitly scopes its main capability to problems
    with automated evaluators; it treats manual-experiment-heavy domains as
    out of scope and says LLM-provided idea evaluation is possible but not its
    optimized setting. The future bridge to AI Co-Scientist-style workflows is
    high-level idea feedback followed by an implementation stage where code
    execution provides machine feedback. The Discussion also says future
    progress depends on setting up more environments or problems with robust
    evaluation functions, making evaluator-environment readiness a paper-facing
    scope claim.
  - Current gap: the paper index and TODOs describe local validators,
    cascades, optional LLM feedback graders, proposal metadata, and
    DeepEvolve-style retrieval. Completed manifests now include
    `runtime.history.automated_evaluator_scope_report`, which separates
    machine-gradeable executable evaluation from manual experimentation and
    pre-code natural-language idea review, labels optional LLM feedback as
    post-evaluator rather than a primary validity gate, and requires transition
    into executable candidate evaluation. The committed
    `papers/automated_evaluator_scope_boundary.json` sidecar preserves this
    machine-gradeable local-scope boundary. The paper-facing gap is now robust
    environment-setup evidence for evaluator design, automatable-domain
    boundaries, setup effort, and expected discovery value.
  - Required result: add benchmark/report metadata and documentation checks for
    robust-evaluator environment readiness, LLM-only idea-feedback stage
    contracts, manual-to-code transition criteria, and environment-scaling
    evidence before broad scientific-discovery, environment-scaling, or
    AI-Co-Scientist-style claims appear in paper-facing docs.

- [ ] Extend AI-Co-Scientist representation-boundary tracking beyond the
      current structural report.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Related Work.
  - Requirement: AlphaEvolve contrasts AI Co-Scientist's natural-language
    hypotheses and natural-language evaluation criteria with AlphaEvolve's
    code evolution and programmatic evaluation functions. The paper says this
    code/programmatic choice lets AlphaEvolve substantially sidestep LLM
    hallucinations and continue evolution for many time steps, while noting
    that the two approaches could be combined in future systems.
  - Current evidence: paper-facing docs now describe
    `runtime.history.programmatic_representation_boundary_report`, which labels
    generated candidates as executable code workspaces, captured proposal
    `idea`/`rationale`/`hypothesis` fields as natural-language context
    metadata rather than candidates, and declared evaluator metrics plus
    deterministic evaluator validity as programmatic criteria. The report keeps
    `claim_ready: false` for hallucination resistance, long-horizon evolution,
    and full natural-language hypothesis-stage bridge claims. The committed
    `papers/programmatic_representation_boundary.json` sidecar preserves this
    structural code/programmatic-evaluation boundary.
  - Required result: add measured hallucination-risk controls, long-horizon
    step counts, natural-language-to-programmatic bridge status, and
    README/ROADMAP wording that does not conflate generic idea metadata or LLM
    feedback graders with AlphaEvolve's Related Work distinction from
    AI-Co-Scientist.

- [ ] Track AlphaEvolve Section 5 Related Work taxonomy and positioning evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 5 Related Work.
  - Requirement: AlphaEvolve positions itself as execution-feedback code
    superoptimization and algorithm discovery, contrasts with pre-LLM
    enumeration/genetic-search/Monte-Carlo/deep-RL approaches, AlphaTensor,
    GPU-kernel and other LLM-agent optimizers, and broader AI-for-science
    systems. It says AlphaEvolve differs from most scientific-discovery
    methods by using programmatic hypothesis representations and evaluation
    metrics, calls continuous LLM fine-tuning through reinforcement learning
    and LLM-directed concept learning over high-performing programs adjacent
    ideas needing more investigation at AlphaEvolve scale, and frames
    mathematical witness/counterexample discovery as complementary to formal
    and informal proof discovery.
  - Current gap: the local paper index lists PDFs and selected inspiration
    relationships, while TODOs cover individual gaps such as FunSearch,
    AI-Co-Scientist, CodeEvolve, DeepEvolve, and domain benchmarks. It does
    not preserve the paper's Related Work taxonomy as evidence. The committed
    `papers/related_work_taxonomy_boundary.json` sidecar records this absence
    for source reference ids, method family, task stage, candidate
    representation, evaluator/evidence mode, proof-versus-witness status,
    comparison claim, complementary-mechanism status, and whether LibreEvolve
    implements, partially implements, or only cites the related approach as
    background.
  - Required result: add paper-facing related-work taxonomy records and
    validation for each relevant source/category, including method family,
    representation mode, evaluation/evidence mode, discovery stage, comparison
    text, complementary-mechanism status, local status, source page/section,
    and README/ROADMAP claim checks so the papers index distinguishes
    AlphaEvolve positioning evidence from flat bundled-paper availability.

- [ ] Track statistical hypothesis-testing semantics for evaluation cascades.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 3.1.
  - Requirement: the evaluation cascade is described as hypothesis testing:
    candidates should pass small-scale filters before main test cases only
    when earlier results are sufficiently promising, and repeated randomized
    initializations should provide evidence for noisy benchmark decisions.
  - Partial status: LibreEvolve has ordered staged validators with scalar and
    metric thresholds, samples, explicit seeds, retries, stage/sample budgets,
    and prompt-visible diagnostics. Completed manifests now include
    `runtime.history.cascade_hypothesis_test_policy_report` with schema
    `libreevolve.cascade_hypothesis_test_policy_report.v1`, configured or
    fallback-inferred small-scale-filter/intermediate/main-test roles, observed
    entry/pass/fail/sample/promotion summaries, configured sample/seed counts,
    and validation that current promotion remains deterministic
    threshold/artifact checking unless an opt-in
    `one_sided_lower_confidence_bound` gate is configured. Configured gates
    retain per-sample observations, confidence-bound evidence, p-values, and
    promotion/rejection linkage. `sequential_stopping: true` records early
    sample-stop diagnostics once the lower-bound gate passes after
    `min_samples`. Configured `error_budget` fields record confidence-derived
    false-promotion and normal-approximation false-rejection budget evidence.
    `binomial_success_rate` gates now record Wilson lower-bound pass/fail
    repeated-seed evidence and exact binomial diagnostics.
  - Current gap: paper-facing evidence still lacks benchmark-calibrated
    thresholds and repeated-seed benchmark fixtures.
    `papers/cascade_hypothesis_test_boundary.json` now validates the current
    runtime policy-gate scope without claiming benchmark-calibrated cascade
    readiness.
  - Required result: add paper-facing benchmark promotion/rejection linkage
    from small-scale filters to main test cases.

- [ ] Track qualitative LLM-feedback criterion provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: LLM-generated feedback can grade solution characteristics that
    are difficult to capture precisely in the user-provided evaluator, such as
    simplicity, and can either add those grades to the score dictionary or
    discard candidates that fail the criterion.
  - Partial status: LibreEvolve has optional LLM feedback graders with bounded
    prompts, parsed scores, normalized bounds/direction, weighted fitness
    deltas, discard/min-score behavior, failure policies, objective
    feedback-sourced metrics, feedback-index summaries, and calibration-report
    validators. Grader configs can now declare qualitative policy fields, and
    runtime records retain `qualitative_policy` with criterion metadata,
    evaluator-gap rationale, rubric/prompt hashes, score-or-discard intent,
    metric linkage, optional calibration report id, and prompt-feedback
    linkage. Completed manifests summarize configured and observed criteria in
    `runtime.history.qualitative_feedback_policy_report`. Runtime manifests
    now also include
    `runtime.history.qualitative_feedback_prompt_history_audit_report`, which
    joins feedback-bearing candidates to prompt-history add/score rows when
    prompt-program history exists.
  - Current gap: paper-facing status still lacks executed calibration/task-suite
    linkage and ablation evidence that the declared criterion improves search
    or filtering quality. `papers/qualitative_feedback_boundary.json` now
    validates that current evidence remains declared-policy and prompt-history
    audit scope, not executed qualitative-feedback calibration.
  - Required result: add calibration/task-suite linkage and validation
    examples for hard-to-code properties such as simplicity.

- [ ] Track natural-language proposal preambles beyond bounded leading capture.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 3(c) and Section 2.3.
  - Requirement: AlphaEvolve examples can include explanatory natural-language
    reasoning before the SEARCH/REPLACE edit payload, while the edit itself is
    still carried by structured diff blocks.
  - Partial status: LibreEvolve captures bounded structured `IDEA`,
    `RATIONALE`, and `HYPOTHESIS` proposal metadata before mutation payloads
    and now also captures bounded/redacted leading explanatory text before the
    first structured diff/file/block mutation marker. The paper index lists
    this as partial AlphaEvolve support, not complete proposal-memory parity.
    The committed `papers/natural_language_preamble_boundary.json` sidecar
    preserves this bounded-leading-capture-only boundary.
  - Current gap: the preamble contract remains narrower than arbitrary
    AlphaEvolve-style rationale handling. Prose between or after mutation
    sections is still rejected, raw full replacements without structured
    markers are not disambiguated, preamble/rationale quality is not scored,
    and no cross-run preamble table exists.
  - Required result: add paper-facing evidence for configurable preamble
    policy, raw-full-replacement disambiguation if used, semantic
    rationale-quality scoring, and cross-run preamble/proposal joins before
    presenting natural-language proposal preambles as complete.

- [ ] Track prompt example-copy diagnostics beyond built-in normalized and
      skeleton signals.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 3(b,c) and Section 2.3.
  - Requirement: AlphaEvolve prompts can include concrete current-program
    context and concrete SEARCH/REPLACE demonstrations, but accepted proposals
    should be edits to the sampled current program rather than copied
    illustrative prompt examples.
  - Partial status: LibreEvolve supports canonical SEARCH/REPLACE blocks,
    concrete prompt examples, and strict malformed-diff diagnostics. Completed
    manifests now include `runtime.history.prompt_example_copy_report` with
    schema `libreevolve.prompt_example_copy_report.v1`, which inventories
    built-in mutation-format example sentinels and records exact,
    normalized file-section-region, and simple example-format skeleton copy
    signals with candidate status/admission metadata.
    `papers/prompt_example_copy_boundary.json` now validates that this remains
    a built-in-diagnostics-only evidence boundary.
  - Current gap: the report is diagnostic-only and remains scoped to built-in
    examples. It does not provide hard rejection, configurable acceptance
    policy, custom prompt-template example inventories, or broader
    semantic/renamed example-copy detection beyond the current skeleton.
  - Required result: add paper-facing evidence for configurable
    acceptance/rejection policy, broader semantic or renamed example-copy
    detection, and custom prompt-template inventories before treating
    prompt-example compatibility as AlphaEvolve-style current-program editing
    fidelity.

- [ ] Track multi-edit semantic consistency beyond current diagnostic scan.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 3(b).
  - Requirement: the assembled AlphaEvolve prompt tells the model to make
    proposed SEARCH/REPLACE edits consistent with each other, including adding
    a newly referenced config variable when another edit uses it.
  - Partial status: LibreEvolve prompt instructions include comparable
    consistency guidance, and completed manifests now include
    `runtime.history.mutation_consistency_report` with proposal/prompt ids,
    changed file/block/search edit units, diagnostic co-change links,
    best-effort Python introduced/reference symbol labels,
    unresolved-reference diagnostics, evaluator-failure taxonomy linkage, and
    accepted/rejected status. `papers/mutation_consistency_boundary.json` now
    validates this as current-run diagnostic evidence only.
  - Current gap: this is current-run diagnostic evidence, not complete
    semantic proof. It does not infer required companion edits, model config or
    resource dependencies, resolve Python scopes/imports across files, classify
    benchmark-calibrated consistency failures, or gate admission.
  - Required result: add paper-facing evidence for required companion-edit
    inference, language-aware scope/import/resource models, calibrated
    consistency-failure taxonomy, and optional acceptance policy before
    presenting multi-edit consistency as complete.

- [ ] Join provider prompt-role telemetry into primary-prompt paper evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: the primary prompt includes system instructions and sampled
    prior solutions, so paper evidence should connect generated prompt
    ingredients to the provider-message role placement used for the LLM call.
  - Partial status: LibreEvolve supports configured `llm_prompt_roles` for
    built-in backend calls and retains hash-only `prompt_role_policy` telemetry
    in LLM call records. The primary-prompt instruction report separately
    records generated prompt ids/hashes, target solution hashes, sampled
    inspiration roles, instruction hashes, required channels, and telemetry
    call joins.
  - Current gap: the primary-prompt report does not yet join each generated
    prompt to its retained `prompt_role_policy` telemetry, so paper-facing
    AlphaEvolve prompt-role placement evidence remains incomplete even though
    backend prompt-role payload support exists.
  - Required result: add paper-visible records and validators that link
    generated prompt ids/call ids to role-policy metadata, distinguish
    single-user-message versus configured structured-message provider payloads,
    keep raw instruction text out of artifacts, and update the AlphaEvolve
    paper-status row after validation proves the join.

- [ ] Track Figure 3 supervised-learning example exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 3 presents a
    supervised-learning pipeline example with three abbreviated subfigures: a
    user-provided JAX/Jaxline file with evolve blocks and `evaluate`, an
    assembled prompt showing prior/current programs and scores, and an LLM
    response containing explanatory prose plus SEARCH/REPLACE edits.
  - Current gap: paper-facing TODOs track mutation parsing, prompt-context
    policy, preamble handling, and prompt-example-copy diagnostics.
    `papers/figure3_supervised_exhibit_boundary.json` now preserves Figure 3
    as a manifest-checked missing-exhibit boundary with stable figure/subfigure
    IDs and required future source/prompt/output excerpt artifacts and hashes,
    displayed metric values, omitted-line/ellipsis policy, source PDF
    page/caption location, rendering/text artifact paths, and links from the
    displayed snippets to prompt-history, evaluator, candidate-history, and run
    artifacts. It does not produce those exhibit artifacts.
  - Required result: add paper-facing Figure 3 exhibit records and validation:
    figure/subfigure IDs, source file and `evaluate` excerpt artifacts,
    rendered prompt excerpt artifact, LLM-output excerpt artifact, prompt score
    values, candidate/evaluator/run links, ellipsis/skipped-content policy,
    source/rendered artifact hashes, and README/ROADMAP wording that separates
    reproduced supervised-learning example evidence from generic prompt,
    mutation, and evaluator support.

- [ ] Track adaptive diff-versus-full mutation prompting.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: AlphaEvolve asks for SEARCH/REPLACE blocks for larger
    codebases, but for very short code or cases where a complete rewrite is
    more appropriate it can ask the model to output the full code block.
  - Partial status: LibreEvolve supports canonical diff parsing and a
    configured `full` mutation mode with full-file, file-section, and
    full-block replacement semantics.
    `papers/adaptive_mutation_mode_boundary.json` now records the paper-facing
    boundary for run-wide configured-mode support versus adaptive
    diff-versus-full selection.
  - Current gap: `Config.mutation_mode` is still a run-wide enum. The prompt
    and parser contract do not adapt per candidate, code size, workspace shape,
    or observed failure mode, and paper-facing telemetry does not explain why a
    given proposal was requested as a diff or a full rewrite.
  - Required result: add paper-visible mutation-mode policy evidence for
    candidate-shape or task-shape selection, per-candidate prompt/output mode
    records, fallback/critique behavior, and benchmark examples proving the
    diff/full choice follows documented AlphaEvolve-style conditions rather
    than a fixed run configuration.

- [ ] Extend LLM-constructed mutation-operator evidence beyond the current
      fixed-edit boundary report.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Section 5 Related
    Work.
  - Requirement: AlphaEvolve uses structured edit payloads, but the paper
    contrasts its LLM-guided mutation with evolutionary systems that depend on
    handwritten mutation/crossover operator sets.
  - Partial status: LibreEvolve supports canonical SEARCH/REPLACE diffs,
    configured full replacement modes, workspace file sections, and bounded
    topology commands. Paper-facing docs now cite
    `runtime.history.mutation_operator_boundary_report`, which records
    configured run-wide mutation mode, observed fixed parser payload surfaces,
    sample generated-candidate mutation records, and `claim_ready: false` for
    LLM-constructed operator families and adaptive selection.
    `papers/mutation_operator_boundary.json` now records this as a
    manifest-checked paper-facing boundary.
  - Current gap: the report still shows those are fixed local edit surfaces
    selected by configuration and parser grammar. The paper index has no
    evidence that LibreEvolve declares, generates, selects, scores, or reports
    higher-level LLM-constructed operator families such as decomposition,
    algorithmic reformulation, recombination, multi-component refactoring, or
    benchmark-specific edit strategies.
  - Required result: add proposal-level operator-family provenance, adaptive
    operator construction or selection evidence, operator-family scoring, and
    benchmark telemetry before claiming AlphaEvolve parity for replacing
    handwritten mutation operators with LLM-generated program mutations.

- [ ] Extend creative-generation proposal diversity evidence beyond exact
      duplicate counts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Section 4
    ablations.
  - Requirement: AlphaEvolve says SOTA LLMs digest previous solutions and
    propose new, diverse ways to improve them, and reports that stronger
    underlying LLMs improve system performance.
  - Partial status: LibreEvolve records selected parents and inspirations,
    prompt/call ids, proposal `idea`/`rationale`/`hypothesis` metadata,
    candidate outcomes, sampling strategies, bounded hypothesis summaries, and
    backend/model telemetry. Paper-facing docs now cite
    `runtime.history.proposal_diversity_report`, which records exact proposal
    and idea hash uniqueness/duplicate counts by generation and proposal batch,
    with `papers/proposal_diversity_boundary.json` preserving the exact-text
    analysis boundary as a manifest-required sidecar.
  - Current gap: the paper index still has no evidence that generated proposals
    are semantically diverse improvement approaches within a call, generation,
    batch, prompt context, or model/backend comparison. Existing
    proposal-scoring, initial-pool divergence, and mutation-operator TODOs do
    not require near-duplicate proposal detection, idea-family diversity,
    semantic/task-output distances, or ablation linkage between proposal
    diversity and model quality.
  - Required result: extend paper-visible proposal-diversity reports with
    proposal id, prompt/call id, parent/inspiration ids, backend model id,
    idea/operator-family labels, near-duplicate status, code and semantic/
    task-output distance measures where available, accepted/rejected outcome,
    novelty contribution, and equal-budget/model ablation linkage before
    claiming AlphaEvolve-style creative generation from SOTA LLMs.

- [ ] Track stochastic prompt-format separate config-file provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: stochastic formatting uses template placeholders with
    human-provided alternatives for increased diversity, instantiated using
    probability distributions provided in a separate config file.
  - Partial status: LibreEvolve supports weighted `prompt_format_options` and
    prompt-template markers such as `[[prompt:name]]`. Completed manifests now
    include `runtime.history.stochastic_prompt_format_distribution_report`
    with prompt ids, marker names, option-set ids, normalized probabilities,
    selected alternative hashes/indexes, weight override source, prompt/call
    linkage, inline/effective config source boundary, and run-local RNG replay
    boundary. `papers/stochastic_prompt_format_boundary.json` now preserves
    the effective-config distribution versus separate-source parity boundary
    in the paper manifest.
  - Current gap: this is probability/selection provenance for effective
    configuration, not paper-faithful source provenance. There is no distinct
    separate config-file identity for the stochastic formatting distribution,
    no source-file hash/byte/count precedence record, no certified
    human-authored alternative provenance, no author/reviewer or revision
    metadata, and no paper-facing validator that distinguishes inline
    `prompt_format_options` from an AlphaEvolve-style separate distribution
    file.
  - Required result: add paper-visible stochastic-format distribution
    source-file records and validation, including safe source path, source
    hash, config precedence, author/reviewer or declared human-authorship
    metadata when present, selected alternative linkage, and overclaim checks
    that keep inline/effective-config reports from being treated as full
    AlphaEvolve stochastic-formatting parity.

- [ ] Complete full validator-metadata rendering and provider-token prompt
  packing.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompt context can include program execution results, outputs,
    and scores from previous attempts.
  - Partial status: history records preserve stdout/stderr, retry-attempt
    records, aggregate syntax diagnostics, artifact metadata, and LLM feedback
    provenance. Prompt construction now renders bounded, redacted parent
    summaries for recent stage status, execution output, retry/sample attempts,
    and LLM grader feedback, plus bounded/redacted evaluator artifact path/hash
    summaries, skipped-artifact diagnostics, bounded stored-content excerpts
    for copied UTF-8 evaluator artifacts, opt-in bounded-file prompt rendering
    for copied UTF-8 artifact contents under the run directory, aggregate syntax
    diagnostics, metric-bound clamp diagnostics, malformed metric diagnostics,
    sample aggregation counts/policies, bounded general JSON-safe validator
    metadata fields not already covered by specialized renderers, and selected
    persisted LLM-grader failure-memory provenance. Binary and non-UTF-8
    artifacts are explicitly marked as having no prompt excerpt or renderable
    artifact content.
  - Current gap: prompt construction still renders only bounded selected
    validator metadata rather than full validator metadata and does not enforce
    provider-token section-priority prompt packing across all feedback/context
    sections. A
    run-level `prompt_max_chars` cap and heuristic
    `prompt_max_estimated_tokens` cap now bound final rendered mutation prompts
    and ensemble prompts before backend selection, and record prompt-size
    diagnostics. Those diagnostics now include
    `section_budget` with deterministic per-placeholder priorities, hashes,
    character counts, estimated tokens, required/optional totals, template
    overhead, required-section fit status, and heuristic character/token-budget
    packing decisions for omitted optional sections. Direct `PromptSampler`
    callers can now provide a manifest-safe provider token counter so the
    packer uses exact counts under `max_prompt_estimated_tokens` and records
    provider-token totals/counter provenance. The normal mutation path now
    discovers a common eligible-backend counter before constructing
    `PromptSampler`; this currently enables automatic exact counting only when
    every eligible mutation backend can use a locally installed OpenAI
    `tiktoken` counter, and otherwise persists
    `libreevolve.prompt_token_counter_capability.v1` diagnostics with the
    precise unavailable reason. The ensemble boundary now repeats that
    role-scoped common-counter discovery for mutation, critique, feedback,
    meta-prompt, registry-created, and custom role labels; when all eligible
    backends for a role share the local counter, the final prompt cap is
    enforced with exact provider-token counts and call telemetry records
    `prompt_token_count_policy`, `prompt_provider_tokens`,
    `prompt_token_limit_count`, and the role-specific capability record.
    `validate_prompt_section_budget_report()` now validates persisted
    `libreevolve.prompt_section_budget.v1` records for schema/policy shape,
    section counts, required/optional totals, section hash shape, packing
    decisions, cap-fit claims, and provider-counter boundary fields, but full
    provider-token section packing across all provider families and prompt
    roles is still absent from the normal evolution path. The AlphaEvolve table
    now scopes the prompt-token gap to selected-backend
    provider-token section packing outside mutation prompts plus exact counters
    across non-OpenAI provider families, rather than implying all tokenizer-aware
    fitting is absent. Backend specs and
    backend metadata can now carry
    `context_window_tokens` plus optional `reserved_output_tokens`; the
    ensemble subtracts the reserve, applies the derived heuristic prompt-token
    capacity before provider calls, and records the window, reserve, and
    derived capacity in call telemetry. Final manifests now record
    `runtime.prompt_section_packing` with schema
    `libreevolve.prompt_section_packing_coverage.v1` and embedded validation,
    making the mutation-only section-packing boundary and critique/feedback/
    meta-prompt final-boundary-only roles explicit. Validation rejects complete
    provider-token section-packing overclaims and role-level overclaims that
    mark critique, feedback, or meta-prompt as section-packed, while keeping
    exact non-OpenAI/custom counters, registry/custom role packing, and
    retrieval/context/plugin/failure-memory packing readiness false. The
    committed `papers/prompt_section_packing_boundary.json` sidecar now
    preserves this mutation-section-packing and bounded-validator-metadata
    boundary for paper-manifest validation.
  - Required result: add configurable/full validator-metadata prompt policy
    and automatic selected-backend provider-token section-priority packing
    across evaluator, feedback, artifact, and context prompt sections. The
    remaining paper gap is not persisted section-budget validation or
    role-scoped final-prompt exact token counting, and not manifest validation
    of current prompt section-packing role coverage.

- [ ] Model migration replay and async/pending-work controller resume for
  one-command archive resume.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: island-model population state should be reproducible enough
    that resumed AlphaEvolve-style searches continue from the same assignment
    policy, not only from the same retained programs.
  - Current evidence: live island assignment now advances only when
    `search_state_changed` is true, and the paper index documents that
    non-admitted `not_improving_cell` attempts do not consume island slots.
    Final manifests persist a compact `runtime.history.archive_state` snapshot
    with the current round-robin cursor, sequence counters, and per-island
    occupancy/elite counts, and `load_runtime_archive_state_snapshot()`
    validates that compact manifest field before future resume use.
    `load_archive_event_records()` now validates persisted migration event rows
    as checked audit data.
    `IslandModel.restore_cursor_state()` now applies the compact cursor/counter
    subset to a live island model. `ProgramDatabase(...,
    archive_state_snapshot=...)` now applies that validated cursor/counter
    subset during database construction and records a cursor-only restore
    policy in the startup manifest.
    Direct `evolve()` calls now accept `runtime_archive_state_snapshot`, and
    CLI runs can load the same compact cursor/counter snapshot with
    `--restore-archive-cursor-from-manifest`.
    Manifest snapshots now also persist `archive_contents` with per-island
    MAP-Elites cells, elite-program ids, descriptor policy metadata, and archive
    configuration. `load_archive_restore_bundle()` combines that manifest state
    with accepted `history.jsonl` records, and `ProgramDatabase(...,
    archive_state_snapshot=..., archive_programs_by_id=...)` restores live
    cells and elite archives from the resulting bundle.
    New archive-state snapshots now advertise
    `snapshot_persisted_cursor_and_full_archive_restore_supported`, while
    validators still accept the earlier cursor-only status for legacy manifest
    restore.
    The paper index now reflects that CLI full-runtime restore composes the
    compatible archive restore bundle with runtime RNG, LLM scheduler, budget,
    and controller-budget replay surfaces; it no longer treats generic
    full-resume wiring as open for these synchronous checked surfaces.
    `policies.archive_identity.resume_status` now advertises
    `manifest_archive_state_restore_supported`, lists restored archive
    surfaces, and explicitly marks migration-event replay as
    `audit_only_not_restore_engine`. Focused database tests prove full archive
    restore uses the restored round-robin cursor for the next admission.
    Archive snapshots now include validated `migration_replay` metadata that
    states migration events are not replayed as a restore engine, archive
    contents cover current migrated placements, and controller pending work is
    not restored. Final manifests now include
    `runtime.history.archive_event_replay_audit`, which validates migration
    rows, replays final admitted migration placements, and compares that
    audit-only partial event view with `archive_contents`. The validators
    reject replay-engine overclaims.
    `validate_archive_event_replay_audit()` now validates the audit result,
    including schema/status, audit-only and no-restore-engine flags, event and
    placement count consistency, retained mismatch shape, mismatch retention
    limits, verified/absent status invariants, and required audit-boundary
    limitations. The paper manifest now requires
    `papers/archive_event_replay_boundary.json` to preserve the current
    snapshot-restore plus audit-only archive-event reconciliation scope.
  - Current gap: cursor and archive-content restore are implemented, but
    migration placement rows are reconciled only as audit evidence rather than
    replayed as an ordered restore engine. Completed manifests now include
    `runtime.history.controller_state`, a terminal drained-state snapshot for
    the synchronous controller with zero queued/running proposals, evaluations,
    in-flight LLM calls, and pending archive admissions at finalization plus a
    compact controller-budget event-stream summary. Async or mid-generation
    controller/pending-work state is still absent from one-command resumed
    experiment traces.
    `libreevolve.controller_state_artifact_inventory.v1` now verifies the
    terminal synchronous controller event stream against the manifest artifact
    record and disk file, including safe relative path checks, file existence,
    SHA-256, byte count, strict JSONL event count, last sequence/kind,
    per-record status, and a stable records hash.
    `libreevolve.controller_state_validation.v1` now verifies the terminal
    drained synchronous boundary and reports pending-work or async/full-replay
    overclaims as manifest validation failures. The paper manifest now requires
    `papers/controller_pending_work_resume_boundary.json`, which preserves that
    terminal controller-state boundary separately from real queue checkpoint
    and pending-work resume support.
  - Required result: apply or explicitly model migration-event replay, add
    controller/pending-work resume state, and add paper-visible resume/replay
    tests covering below-threshold, non-admitted, elite-only, and
    cell-replacement cases. The remaining paper gap is not terminal controller
    event-stream artifact verification, terminal drained-state validation, or
    preserving the current pending-work absence boundary.

- [ ] Extend meta-prompt context policy beyond validated current fields.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt instructions and prompt context can be improved through
    meta-prompt evolution.
  - Current evidence: prompt programs now persist validated
    `libreevolve.prompt_context_policy.v1` state separate from template text.
    The policy can disable optional prompt channels and override deterministic
    prompt-packing section priorities, and it can select safe enum-valued
    mutation-instruction variants for rendered mutation-format guidance.
    `mutation_instruction_include_example` can keep or remove the built-in
    mutation-format example block while preserving the core format rules. It
    can select safe parent metric names for the `{parent_metrics}` channel and
    cap or suppress individual parent metric entries by metric name before
    rendering. It
    now validates the meta-prompt-visible
    `libreevolve.meta_prompt_context_policy_capabilities.v1` map against the
    actual `libreevolve.prompt_context_policy.v1` keys before rendering
    evidence, rejecting duplicate, missing, malformed, or unsupported
    advertised fields. It
    can also set `parent_code_paths` to select/order safe mutable
    parent-workspace files, `parent_code_required_terms` and
    `parent_code_excluded_terms` to filter them by safe path/content terms, and
    `parent_code_order_policy` with optional `parent_code_ranking_terms` to
    rank selected parent files by deterministic term overlap before rendering.
    `parent_code_limit` can cap how many ordered mutable parent files render,
    including `0` to suppress mutable parent file bodies while retaining
    diagnostics. `parent_code_max_chars_by_path` can cap individual rendered
    parent file bodies by safe candidate-relative path before the aggregate
    parent-code cap applies.
    `parent_code_max_chars` to cap or suppress the
    required parent-code channel while retaining an explicit omission marker and
    `libreevolve.parent_code_policy.v1` diagnostics for source,
    requested/rendered/omitted/missing path policy, term-filter policy,
    order policy, render-count limit policy, per-file content cap policy, cap,
    truncation mode (`head` or `head_tail`), character counts, and hashes. It
    can also set `proposal_metadata_enabled` to override whether proposal
    metadata instructions and parsing run for the selected prompt arm while
    preserving run-level defaults when unset. It
    can also select which parent-feedback subsections render, including stage
    summaries, execution output, validator diagnostics/artifacts, program
    outputs, proposal metadata, and LLM grader feedback, and
    `feedback_section_order` can deterministically reorder those
    selected/rendered parent-feedback subsections while appending unspecified
    sections in default order. `feedback_section_max_chars_by_name` can suppress
    or cap individual feedback subsections before the aggregate feedback cap.
    `llm_feedback_fields`
    can further select rendered safe LLM-grader fields within that section, and
    `llm_feedback_max_chars_by_field` can cap or suppress those selected
    LLM-grader fields before rendering.
    `inspiration_strategy` can override upstream inspiration sampling strategy
    for that prompt program using the same safe strategy enum as config.
    `inspiration_sample_count` can override the upstream sampled inspiration
    count before plugin context and prompt rendering, separately from the
    rendered inspiration cap. `inspiration_required_metric` can filter the
    upstream inspiration pool to programs carrying a manifest-safe metric name
    before plugin context and prompt rendering. `inspiration_excluded_metrics`
    can filter out upstream inspirations carrying any listed manifest-safe
    metric names before plugin context and prompt rendering.
    `inspiration_fitness_threshold` can filter upstream inspirations by finite
    fitness min/max bounds before plugin context and prompt rendering.
    `inspiration_metric_thresholds` can filter upstream inspirations to programs whose numeric metric values
    satisfy safe min/max bounds before plugin context and prompt rendering.
    `inspiration_metric_ranking` can rank the upstream inspiration pool by a
    numeric metric in maximize/minimize order before final selection.
    `validator_diagnostic_groups` can select rendered bounded validator
    diagnostic groups inside validator diagnostics, and `proposal_fields` can
    select rendered safe proposal metadata fields, and
    `proposal_max_chars_by_field` can cap or suppress those proposal fields
    before rendering, and `stage_summary_fields`
    can select rendered safe stage-summary fields within stage-summary
    feedback, and `stage_summary_max_chars_by_field` can cap or suppress those
    stage-summary fields before rendering, and `execution_output_fields` can select rendered safe
    execution-output fields within execution-output feedback and stage-summary
    IO lines, and `execution_output_max_chars_by_field` can cap or suppress
    rendered `stdout`, `stderr`, and `error` text independently before those
    fields are included, and `sample_retry_fields` can select rendered safe sample/retry
    diagnostic fields, and `sample_retry_max_chars_by_field` can cap or
    suppress selected sample/retry diagnostic text fields before rendering, and `program_output_fields`
    can select rendered safe program-output fields within program-output
    feedback, and `program_output_max_chars_by_field` can cap or suppress
    selected program-output text fields before rendering, and `validator_artifact_fields` can select rendered safe
    validator-artifact fields, and `validator_artifact_max_chars_by_field` can
    cap or suppress selected validator-artifact text fields before rendering, and `validator_artifact_content_fields` can
    select nested bounded artifact-content fields, and
    `validator_artifact_content_mode`,
    `validator_artifact_content_max_bytes`, and
    `validator_artifact_content_max_chars` can override artifact-content
    rendering policy and caps, and
    `validator_skipped_artifact_fields` can select rendered safe
    skipped-artifact fields, and
    `validator_skipped_artifact_max_chars_by_field` can cap or suppress selected
    skipped-artifact text fields before rendering, and
    `validator_metadata_keys` can select safe keys inside the validator
    metadata summary. `validator_metadata_limit` can cap or suppress the
    number of metadata-summary items before rendering.
    `validator_metadata_max_chars_by_key` can cap or
    suppress selected validator metadata summary values before rendering.
    `evaluator_path_fields` can select safe validator path provenance fields,
    and `evaluator_path_max_chars_by_field` can cap or suppress selected path
    fields before rendering.
    `evaluator_dependency_fields` can select safe validator dependency-policy
    fields, including derived file paths, hashes, and redaction flags, and
    `evaluator_dependency_max_chars_by_field` can cap or suppress selected
    dependency fields before rendering.
    `evaluator_stage_fields` can select safe derived stage-context fields, and
    `evaluator_stage_max_chars_by_field` can cap or suppress selected stage
    fields before rendering.
    `evaluator_workspace_fields` can select safe evaluated workspace
    provenance fields, including primary file, file count, and bounded file
    list, and `evaluator_workspace_max_chars_by_field` can cap or suppress
    selected workspace fields before rendering.
    `syntax_error_fields` can select safe fields inside
    syntax-error diagnostics, and `syntax_error_max_chars_by_field` can cap or
    suppress selected syntax-error text fields before rendering, and
    `metric_bound_fields` can select safe fields
    inside metric-bound diagnostics, and `metric_bound_max_chars_by_field` can
    cap or suppress selected metric-bound text fields before rendering.
    `configured_stage_check_fields` can select
    safe fields inside configured-stage check diagnostics, and
    `configured_stage_check_max_chars_by_field` can cap or suppress selected
    configured-stage text fields before rendering.
    `stage_metric_threshold_fields` and `artifact_output_check_fields` can
    select nested safe fields inside configured-stage metric-threshold and
    artifact-output checks, and `stage_metric_threshold_max_chars_by_field` can
    cap or suppress selected nested metric-threshold text fields before
    rendering. `artifact_output_check_max_chars_by_field` can cap or suppress
    selected nested artifact-output check text fields before rendering.
    `malformed_metric_fields` can select safe fields inside malformed-metric
    diagnostics, and `malformed_metric_max_chars_by_field` can cap or suppress
    selected malformed-metric text fields before rendering.
    `metric_aggregation_fields` can select safe fields inside
    metric-aggregation diagnostics, and
    `metric_aggregation_max_chars_by_field` can cap or suppress selected
    metric-aggregation text fields before rendering.
    `synthetic_metric_fields` can select safe fields inside synthetic
    failure-metric diagnostics, and `synthetic_metric_max_chars_by_field` can
    cap or suppress selected synthetic metric text fields before rendering.
    `materialization_error_fields` can select safe fields inside
    materialization-error diagnostics, and
    `materialization_error_max_chars_by_field` can cap or suppress selected
    materialization-error text fields, including typed reason/path fields,
    before rendering.
    `validator_boundary_fields` can select
    safe fields inside validator-boundary diagnostics.
    `validator_boundary_max_chars_by_field` can cap or suppress selected
    validator-boundary text fields before rendering.
    `validator_resource_limit_fields` can select nested safe resource-limit
    fields inside validator-boundary diagnostics, and
    `validator_resource_limit_max_chars_by_field` can cap or suppress selected
    nested resource-limit text fields before rendering.
    `validator_budget_fields` can select stage/sample budget diagnostic fields
    inside execution diagnostics, and
    `validator_budget_max_chars_by_field` can cap or suppress selected budget
    fields before rendering.
    `validator_env_fields` can select value-free validator environment
    diagnostic fields, and `validator_env_max_chars_by_field` can cap or
    suppress selected environment fields before rendering.
    `execution_diagnostic_groups` can select safe execution-diagnostic
    subgroups before subgroup field allowlists are applied.
    `validator_stdin_fields`
    can select safe fields inside validator-stdin diagnostics, and
    `validator_stdin_max_chars_by_field` can cap or suppress selected
    validator-stdin text fields before rendering.
    `diagnostic_output_fields` can select safe fields inside diagnostic-output
    diagnostics, and `diagnostic_output_max_chars_by_field` can cap or
    suppress selected diagnostic-output text fields before rendering.
    `timeout_cleanup_fields` can select safe fields inside
    timeout-cleanup diagnostics, and
    `timeout_cleanup_max_chars_by_field` can cap or suppress selected
    timeout-cleanup text fields before rendering.
    `prompt_format_weights` can override configured stochastic prompt-format
    alternative weights for safe configured markers, and `context_source_paths` can select and order
    loaded local context sources by safe problem-relative path.
    `context_source_max_chars` can cap rendered text for each selected local
    context source and records original, rendered, and omitted character counts
    per source. `context_source_truncation` can choose deterministic `head` or
    `head_tail` retention under that per-source cap.
    `context_source_order_policy` can keep selected source order or rank
    selected local context sources by deterministic task-term overlap against
    rendered source text while recording scores, query source, query-term
    hash/count, configured query terms when present, and a ranking hash.
    `context_source_ranking_terms` can provide explicit safe ranking terms
    instead of deriving them from the task description.
    `context_source_required_terms` can keep only sources whose
    loaded content contains every listed safe term, and
    `context_source_excluded_terms` can omit sources whose loaded content
    contains any listed safe term before ranking and limiting; diagnostics
    record required/excluded terms, omitted paths, match/filter counts, and a
    selection hash. `context_source_limit` can cap how many ordered local
    context sources render after path selection and ranking, including
    suppressing them with a zero limit, and records pre-limit order, omitted
    paths, selected count, omitted count, and a selection hash.
    `recent_failure_limit` can cap rendered recent failure-memory records,
    including suppressing that block with a zero limit, and records available,
    rendered, and omitted counts. `recent_failure_selection_policy` can choose
    `recent`, `oldest`, `lowest_score`, or `highest_repetition` retained
    failure-memory records before that render cap is applied, and records selector/selection
    semantics. `recent_failure_required_errors` can filter retained
    failure-memory records by exact safe `error` or `diff_error` labels before
    selection and limiting, and records required labels, match count, filtered
    count, and policy. `recent_failure_excluded_errors` can omit retained
    failure-memory records carrying exact safe `error` or `diff_error` labels
    before score filtering, selection, and limiting, and records excluded
    labels, filtered count, and policy. `recent_failure_required_changed_files`
    can filter retained failure-memory by safe exact `changed_files` paths
    before score filtering, selection, and limiting, and records required
    paths, match count, filtered count, and policy.
    `recent_failure_excluded_changed_files` can omit retained failure-memory
    carrying safe exact `changed_files` paths before score filtering,
    selection, and limiting, and records excluded paths, filtered count, and
    policy. `recent_failure_required_stage_names` can filter retained
    failure-memory by safe exact evaluation stage names, and
    `recent_failure_excluded_stage_names` can omit retained failure-memory
    carrying safe exact evaluation stage names before repetition/score
    filtering, selection, and limiting; diagnostics record required/excluded
    stage names, match counts, filtered counts, and policies.
    `recent_failure_required_terms` and `recent_failure_excluded_terms` can
    filter retained failure-memory by safe text terms in the failure evidence
    before repetition/score filtering, selection, and limiting, recording
    configured terms, match/filter counts, and policies when configured.
    `recent_failure_repetition_threshold` can filter retained
    failure-memory by integer `repetition_count` `min`/`max` bounds before
    score filtering, selection, and limiting, and records normalized bounds,
    match count, filtered count, and policy. `recent_failure_score_threshold` can filter retained
    failure-memory by finite score `min`/`max` bounds before selection and
    limiting, and records normalized bounds, match count, filtered count, and
    policy. `recent_failure_max_chars_by_field` can cap or suppress selected
    recent failure-memory fields before rendering.
    `inspiration_limit` can cap rendered selected
    inspirations, including suppressing all inspiration rendering with a zero
    limit, and records available, rendered, and omitted counts.
    `extra_context_max_chars` can cap already validated/redacted plugin
    `extra_context` text and records input, rendered, and omitted character
    counts. `plugin_context_enabled: false` can suppress plugin
    `build_extra_context()` and `prompt_context_metadata()` calls for a selected
    prompt arm while recording disabled per-plugin provenance.
    `plugin_context_allowlist` can select which plugin identity labels may run
    prompt-context hooks for that prompt arm, while non-selected plugins are
    skipped with deterministic provenance before hook execution.
    `plugin_context_excluded_labels` can omit selected plugin identity labels
    before prompt-context hooks run, recording
    `excluded_by_prompt_context_labels` visibility and the configured label
    policy.
    `plugin_context_order` can reorder selected plugin prompt-context sections
    by safe plugin identity labels before aggregate prompt packing.
    `plugin_context_required_terms` and `plugin_context_excluded_terms` can
    filter bounded plugin context text by safe terms before prompt visibility,
    recording selected status, missing required terms, matched excluded terms,
    and a selection hash.
    `plugin_context_ranking_terms` can rank prompt-visible plugin context
    sections by deterministic term overlap before render-count limiting,
    recording configured ranking terms, term hash/count, score, rank, previous
    rank, candidate count, and ranking hash.
    `plugin_context_limit` can cap how many ordered plugin context sections
    become prompt-visible after allowlist, term filtering, and ordering,
    recording source limit, pre-limit count, selected/omitted counts, rank,
    selected status, and a selection hash.
    `plugin_context_max_chars` can globally cap each plugin context section
    before prompt visibility, recording the global policy cap, per-label cap,
    effective cap, original character count, and prompt truncation status.
    `plugin_context_truncation` can choose deterministic `head` or
    `head_tail` retention under those plugin-context caps, and plugin-context
    records persist the applied content policy.
    `plugin_context_max_chars_by_label` can cap rendered plugin prompt-context
    text by plugin identity label before aggregate prompt packing applies.
    Generated prompt diagnostics record the applied policy hash, selected
    instruction variant, selected inspiration strategy and sample-count
    overrides, selected feedback sections, selected LLM-grader
    feedback fields, selected proposal fields, selected stage-summary fields, selected execution-output
    fields, selected sample/retry
    diagnostic fields and caps, selected program-output fields and caps, selected
    validator-artifact fields and caps, selected artifact-content nested fields,
    selected artifact-content policy overrides,
    selected skipped-artifact fields,
    selected validator diagnostic groups, selected validator
    metadata keys, selected parent metric names/caps, selected syntax-error fields, selected metric-bound fields,
    selected configured-stage check fields, selected configured-stage nested
    fields, selected malformed-metric fields,
    selected metric-aggregation fields, selected synthetic metric fields,
    selected materialization error reason/path fields,
    selected validator-boundary fields,
    selected validator budget fields, selected validator resource-limit fields,
    selected execution-diagnostic subgroups, selected validator-stdin fields,
    selected diagnostic-output fields,
    selected timeout-cleanup fields, prompt-format weight
    overrides, context source selection, term filters, render-count caps,
    content caps, truncation policy, and ordering policy,
    recent failure-memory selection and text-term filtering, and inspiration selection, plugin extra-context
    cap diagnostics, plugin-context generation, excluded-label policy, term filters, ranking terms, render-count limits, global plugin caps, truncation policy, and ordering policy, and replacement hashes;
    generated-candidate metadata records required-metric inspiration filtering
    plus metric-threshold inspiration filtering with pool, matching, filtered,
    threshold-bound, ranking-policy, ranked, and selected counts;
    `prompt_history.jsonl` persists `context_policy` plus `context_policy_sha256`; replay validates
    immutable policy state; meta-prompt provider output can return a strict
    JSON object with a revised `template` plus optional `context_policy`; and
    meta-prompt mutation requests now include a compact context-policy
    capability manifest plus per-prompt non-default context-policy previews in
    the bounded redacted prompt-performance evidence. Meta-prompt mutation
    metadata also records a compact capability summary with schema, field
    count, field hash, and per-section hashes for the policy surface shown to
    the model, with validation rejecting forged count/hash/section and
    unsupported-field overclaims. Final manifests now
    include `runtime.prompt_context_policy_coverage` with schema
    `libreevolve.prompt_context_policy_coverage.v1` and embedded validation
    against the current policy schema/capability map, while keeping
    `alphaevolve_context_policy_complete` false, listing unsupported
    retrieval/summarization, learned ranking, and semantic context-selection
    surfaces, and rejecting forged readiness flags for retrieval/summarization
    policy, semantic source selection, non-`PromptSampler` role policy, and
    DeepEvolve-style debug/refinement context-policy control. The AlphaEvolve table now scopes the remaining prompt-context
    gap to live/retrieval/semantic context selection and deeper per-field policy
    beyond the current validated structured context-policy surface rather than
    implying that structured prompt-context policy is absent.
    Remaining context rendering is still mostly fixed in `PromptSampler` and related
    code: plugin context shaping beyond enable/disable, allowlist/excluded-label
    selection, ordering, safe term filtering, deterministic term ranking,
    render-count limiting, global/per-label caps, truncation, parent-metric selection/caps, and required parent-code file selection/term filtering/deterministic ordering/render-count limiting/per-file content capping/character capping/truncation-mode selection,
    retrieval/summarization beyond deterministic source selection/ranking/count caps, and deeper
    per-field policy inside selected validator diagnostic groups beyond
    metadata-summary key selection, parent-metric selection/caps, syntax-error field selection, and
    proposal field selection, and
    stage-summary field selection, and
    execution-output field selection, and
    sample/retry diagnostic field selection, and
    program-output field selection, and
    validator-artifact field selection, and
    artifact-content nested field selection, and
    artifact-content policy override selection, and
    skipped-artifact field selection, and
    metric-bound field selection, configured-stage check field selection, and
    configured-stage nested field selection, and malformed-metric field
    selection, and materialization-error field selection, and
    metric-aggregation field selection, and synthetic metric
    field selection
    and execution-diagnostic subgroup selection, and validator-boundary field
    selection, and validator budget field selection, and validator resource-limit field
    selection, and validator-stdin field selection, diagnostic-output field
    selection, execution-output, sample/retry, program-output, and validator-artifact field caps,
    and timeout-cleanup field selection are
    not yet owned by prompt-program policy. Prompt-program policy can override
    upstream inspiration strategy, sampled inspiration count, safe
    required/excluded-metric filtering, fitness-threshold filtering, metric-threshold filtering, metric ranking, and rendered
    inspiration count, but not richer upstream inspiration selection policy.
  - Required result: extend prompt-program context policy beyond optional
    channel disabling, packing-priority overrides, current character caps,
    parent-code file selection, term filtering, deterministic ordering, render-count limiting, and per-file content capping, and truncation-mode selection so meta-prompt evolution
    can safely alter source selection, retrieval/summarization, inspiration and
    feedback field policy, and additional instruction/context controls while preserving
    safe template rendering and auditability. The remaining paper gap is not
    manifest-visible validation of the current meta-prompt-tunable context
    policy surface.

- [ ] Extend prompt-template compatibility evidence beyond mutation-template
      validation and duplicate-arm audit.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2 and Section 2.6.
  - Requirement: AlphaEvolve-style prompt evolution should make prompt
    templates compatible with each model-call role and context channel that
    consumes them, while preserving clear prompt-program lineage semantics.
  - Partial status: LibreEvolve validates known placeholders, dry-run
    formatting, configured mutation-channel requirements, prompt-format option
    markers, and parent-placeholder retention for evolved prompt children.
    Duplicate configured or evolved template text is intentionally retained as
    separate prompt arms with deterministic ids and shared `template_sha256`
    audit identity.
  - Current gap: paper-facing evidence still lacks role-specific compatibility
    policy for critique, feedback grading, and meta-prompt surfaces, plus
    benchmark evidence that the current explicit no-dedup prompt-arm policy is
    preferable to prompt-program text deduplication.
  - Required result: add role-specific prompt-template compatibility checks and
    paper-visible prompt-arm lineage/no-dedup or deduplication policy evidence
    before treating prompt-template validation as AlphaEvolve-grade prompt
    policy management.

- [ ] Calibrate meta-prompt rewards and add prompt-lineage ablation evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.6, and 4.
  - Requirement: prompt-improvement claims should be backed by reward signals
    and ablation evidence that separate prompt-program lineage effects from
    candidate, evaluator, model, and stochastic search noise.
  - Current evidence: prompt programs have deterministic ids, lineage, usage
    counts, reward sums, normalized mean rewards, `absolute` and `improvement`
    child-score reward modes, reward-policy compatibility checks during
    history replay, and UCB-style prompt-arm selection. Meta-prompt mutation
    requests include bounded prompt-performance evidence with reward policy,
    selected prompt statistics, latest candidate outcome, prompt-arm summaries,
    and recent failure summaries.
  - Required result: add calibrated prompt-specific reward signals,
    prompt-lineage ablation/report artifacts, and tests showing prompt-policy
    attribution across comparable runs before claiming AlphaEvolve-grade
    meta-prompt scoring or prompt-improvement evidence.

- [ ] Separate prompt-database parity from local prompt-arm selection.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 describes meta
    prompt evolution as an additional prompt-generation step whose
    instructions/context are co-evolved in a separate database analogous to the
    solution programs.
  - Current evidence: LibreEvolve has `PromptDatabase`, `prompt_history.jsonl`,
    lineage-bearing prompt programs, UCB-style prompt selection, prompt-score
    replay checks, and optional LLM template/context-policy mutation. The
    current prompt database does not share the solution database's MAP-Elites
    archive semantics, island/migration policy, descriptor/objective indexes,
    archive-event stream, or async/pending-work resume surface.
  - Required result: add paper-facing evidence for a prompt database policy
    that is explicitly solution-database-equivalent, or keep prompt-program
    claims scoped to local prompt-arm selection plus history/reward tracking
    rather than AlphaEvolve's separate co-evolved prompt database.

## Local Paper Corpus Issues

- [ ] Harden benchmark implementations beyond smoke-example fidelity.
  - Paper evidence: the AlphaEvolve paper's matrix task searches low-rank tensor
    decompositions with randomized initializations and exact verification;
    Appendix B.12 reports circle packing in the unit square for `n = 26` and
    `n = 32`; Figure 8 compares ablations by compute-budget fraction.
  - Current evidence: the checked-in matrix example validates only a 2x2 Python
    `matmul2` function and counts AST multiplication nodes inside that
    function. It now rejects known import/library delegation, module-level
    dead-code counters, and fixed-three-case lookup shortcuts, but it remains a
    smoke fixture rather than an operation/rank-faithful tensor benchmark. The
    circle example matches the fixed-26 unit-square objective family, but there
    is no benchmark harness for repeated seeds, SOTA thresholds, saved
    construction artifacts, visual/JSON outputs, or equal-budget ablation
    curves. `libreevolve.benchmark_hardening.v1` now defines a hardening
    contract for protected signals, shortcut threats linked to protected
    signals, detector strategies, passed negative fixtures, and hashed
    hardening artifacts.
    `libreevolve.benchmark_hardening_artifact_inventory.v1` now verifies
    negative fixture and hardening artifact records against concrete files
    under an explicit artifact root, checking safe relative paths, existence,
    SHA-256 hashes, byte counts, per-record statuses, and aggregate
    missing/mismatch/invalid counts, but no real benchmark runner emits those
    reports yet.
    `libreevolve.example_benchmark_scope.v1` now validates a shipped-example
    scope registry that labels `hello_world`, `sorting`, `workspace_math`,
    `matrix_multiplication`, and `circle_packing` as smoke-only and not
    AlphaEvolve-comparable, but it is an exclusion boundary rather than a real
    benchmark harness. The `workspace_math` smoke fixture now covers a nested
    package, declared JSON data, and a binary static seed asset without making
    benchmark claims. The scope registry is validated in focused tests, by
    smoke hardening evidence, through `papers/example_benchmark_scope.json`,
    and by the routine paper-manifest validation gate that reviewers run for
    paper-facing evidence.
    `validate_benchmark_evidence_scope()` now cross-checks
    hardening reports against the matching scope record and optional hardening
    artifact inventory, rejecting smoke-only example promotion, paper-claim
    scope mismatches, and inconsistent inventory evidence.
    The AlphaEvolve paper-index row now describes the checked-in circle task as
    a circle-packing smoke fixture, matching the Appendix B registry's
    `implemented_smoke` status rather than treating it as a benchmark-grade
    packing result.
    `write_matrix_smoke_hardening_bundle()` now emits real hardening files for
    the shipped `matrix_multiplication` smoke fixture: negative-fixture JSON,
    detector log, hardening report, artifact inventory, summary, and
    smoke-scope validation, all while preserving `alphaevolve_comparable:
    false`. `alphaevolve_appendix_b.json` enumerates the thirteen Appendix B
    constructive-math families, but it is still a coverage/status registry:
    twelve families are `planned`, every paper-result family keeps
    `target_baseline.value` null, and its construction/certificate artifact
    schemas are labels for expected evidence rather than executable validators,
    reported construction payloads, SOTA numeric thresholds, or verification
    scripts. Appendix B says the data and verification code for all reported
    constructions appear in the accompanying Google Colab, so a status ledger
    without construction-data exports and runnable verifier-code artifacts is
    still below the paper's publication-evidence surface.
  - Required result: distinguish smoke examples from benchmark fixtures in docs,
    add operation/rank-aware matrix benchmark validation beyond the current
    2x2 smoke checks, connect hardening reports and executable artifact/
    certificate validators for geometric and constructive-math constructions,
    add Colab-equivalent construction-data and verifier-code exports for the
    Appendix B families, and create repeatable benchmark reports tied to
    AlphaEvolve target families. The remaining paper gap is generating those
    anti-gaming and verification-data evidence files from benchmark-grade
    tensor/geometric/constructive-math fixtures, not validating the
    shipped-example scope registry, emitting matrix smoke hardening evidence,
    verifying declared hardening files once a report names them, or preventing
    declared hardening evidence from overriding the smoke-only scope registry.

- [ ] Add paper-facing sorting-network rediscovery evidence as a realistic
      benchmark target.
  - Paper evidence: AlphaEvolve's core claim is not limited to its named
    matrix and constructive-math tasks; it is an evolutionary coding agent
    that improves algorithmic programs under automated verification and scalar
    scoring. Sorting networks are a feasible calibration target for that
    claim because correctness can be verified exhaustively through the
    zero-one principle, and known optimal-size results give clear 8- and
    9-input targets.
  - Current evidence: `libreevolve/problems/examples/sorting` is deliberately
    scoped as a solved smoke/plateau fixture and is listed in the example-scope
    registry as not AlphaEvolve-comparable. `sorting_network_8` now exists as
    a non-comparable benchmark candidate with an exhaustive zero-one
    verifier, comparator-count/depth metrics, 28-comparator valid seed, and a
    checked known 19-comparator target. `sorting_network_9` now mirrors that
    fixture with exhaustive 9-input zero-one validation, a 36-comparator valid
    seed, and a checked known 25-comparator target. A helper now emits
    generic hardening reports, negative-fixture descriptors, inventories, and
    scope validation for both sorting-network candidates. `sorting_network_9`
    also has a tracked clean-checkout run contract for the intended
    `gpt-5.3-codex-spark` Codex CLI lane, including auth expectations,
    validator budget, expected artifacts, manifest assertions, skip/failure
    modes, and post-run evidence bundle names. The paired
    `benchmark_goal_prompt.json` records the bounded external-agent handoff
    prompt for that protocol, is linked from the run contract, and has reusable
    validator coverage for prompt size, model/auth linkage, secret-like text,
    overclaim boundaries, and an emitted runtime prompt-id provenance pointer.
    A paired `benchmark_provider_profile.json` now records the experimental
    Codex provider lane, local-auth support status, budget,
    transcript/redaction policy, expected artifacts, and non-evidence
    result-linkage boundary, with validator coverage against the config, run
    contract, and prompt artifact.
    The paper ledger still has no source-citation sidecar for the zero-one
    verifier or known comparator targets, repeated-run evidence, committed
    run-tied hardening certification, best-candidate artifact hashes,
    failure/invalid-candidate summaries, target-hit-rate summaries, or
    certification row proving rediscovery under fixed evaluator/model/seed
    conditions. The committed
    `papers/sorting_network_rediscovery_boundary.json` sidecar preserves that
    absence boundary for paper-manifest validation.
  - Required result: add a paper-visible benchmark record for
    `sorting_network_8` and `sorting_network_9`, including source citations
    for the zero-one verifier and known comparator targets, fixture scope,
    evaluator artifact hashes, seed-network provenance, repeated-run result
    tables, comparator-count/depth metrics, target-hit-rate summaries,
    best-candidate artifact hashes, failure/invalid-candidate summaries,
    negative-fixture hardening evidence tied to the repeated runs, and
    certification that any claimed rediscovery is calibrated against known
    targets rather than presented as a novel SOTA result.

- [ ] Track Figure 5 construction-exhibit provenance as paper evidence.
  - Paper evidence: AlphaEvolve Figure 5 presents selected SOTA-breaking
    mathematical construction examples with branch labels, problem labels,
    before/after metric values, and rendered construction visuals such as
    hexagon outer-edge, max-distance/min-distance, and sum-of-radii examples.
  - Current gap: the paper-facing Appendix B registry is family/status
    coverage, and existing TODOs ask for construction-data/verifier exports,
    aggregate outcome reports, benchmark hardening, and result-version
    provenance. There is no paper-evidence row or report schema that maps
    Figure 5 exhibits to selected Appendix B results, previous-best/result
    values, branch/problem labels, visual artifact paths/hashes, rendering
    parameters, source Colab cells/artifacts, or verifier links.
  - Required result: add Figure 5-style exhibit metadata with stable exhibit
    IDs, Appendix B family/parameter links, previous/current metric values with
    direction/unit, previous-best source, construction payload, rendered
    visual/JSON artifacts with hashes, verifier/certificate links, and
    documentation that separates reproduced paper exhibits from broader
    Appendix B family coverage.

- [ ] Track Figure 5 versus Appendix B.12 sum-of-radii precision evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 5 displays the
    sum-of-radii improvement as `2.6340 -> 2.6358`. Appendix B.12 and
    Figure 14 describe the `n = 26` unit-square circle-packing improvement as
    `2.634` to `2.635`.
  - Current evidence: `figure5_b12_precision_boundary` now forces the registry
    and docs to preserve the Figure 5 `2.6340 -> 2.6358` strings separately
    from the Appendix B.12/Figure 14 `2.634` to `2.635` strings.
  - Remaining gap: there are still no source-section locators, Figure 5 panel
    artifact, per-source value-extraction certificates, normalized numeric
    values, rounding or truncation policy, chosen canonical claim value,
    value-reconciliation certificate, recomputed sum, or companion Colab
    artifact link.
  - Required result: add those paper/report evidence fields and certificates,
    and keep README and ROADMAP wording from treating Figure 5 display
    precision as interchangeable with Appendix B.12/Figure 14 wording.

- [ ] Track Appendix B figure-level construction provenance for Figures 10-14.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B presents
    displayed construction figures beyond Figure 5: Figure 10 for Erdos
    minimum overlap, Figure 11 for regular-hexagon packings, Figure 12 for
    maximum/minimum-distance point sets, Figure 13 for Heilbronn variants, and
    Figure 14 for circle and rectangle packing sum-of-radii improvements.
  - Current gap: paper-facing Appendix B status now includes a validated
    `figure_exhibit_boundary` for Figures 10-14. It records the required
    future figure/subfigure labels, family/result links, previous/current
    values, figure-caption values, construction payload hashes, visual artifact
    paths/hashes, rendering parameters, source Colab cells/artifacts, and
    verifier/certificate links, but keeps all corresponding rows and artifacts
    `not_recorded_locally`.
  - Required result: add Appendix B figure-exhibit metadata with stable
    figure/subfigure IDs, family and parameter links, previous/current metric
    values with direction/unit, previous-best source, construction payload,
    rendered visual/JSON artifacts with hashes, verifier/certificate links,
    and documentation that separates appendix figure reproduction from broad
    Appendix B family coverage and main-text Figure 5 exhibit coverage.

- [ ] Track Appendix B per-result metric and value evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.1-B.13 reports
    heterogeneous result claims: autocorrelation constants, the uncertainty
    constant `C4`, Erdos minimum overlap, finite-set sum/difference ratios,
    regular-hexagon outer side lengths, max/min-distance ratios, Heilbronn
    minimum areas, the dimension-11 kissing lower bound, and circle/rectangle
    sum-of-radii values. These claims use different parameter tuples, metric
    definitions, inequality directions, previous bounds, reported values, and
    source citations or figure/caption links. They also require different
    construction representations, including step functions, polynomial or
    coefficient lists, finite integer sets, point coordinates, kissing
    configurations, and geometric packing placements.
  - Current gap: paper-facing Appendix B status now includes a validated
    `result_row_boundary` in `alphaevolve_appendix_b.json`. It records the
    `19` expected future result ids, including the B.4 revision row, and the
    required future fields for stable result ids, family/source locations,
    metric definitions, parameter tuples, upper/lower or maximize/minimize
    semantics, previous-best value/source, reported AlphaEvolve value,
    displayed relation, result-version status, construction representation
    schema, construction/verifier artifact hashes, and recomputed values.
    The normalized result rows, metric definitions, parameter rows,
    previous-best attribution, construction payloads, verifier artifacts,
    recomputed values, source-location mapping, and result-version rows remain
    `not_recorded_locally`.
  - Required result: add paper/report evidence for Appendix B.1-B.13 result
    rows with stable result ids, family and parameter metadata, exact metric
    names/formulas, units or bound semantics, optimization direction,
    previous-best citations and values, AlphaEvolve reported values, source
    section/figure/caption links, construction-type schemas and payload hashes
    for step functions, coefficients, finite sets, coordinates, and packing
    placements, verifier artifact hashes, and README/ROADMAP wording that
    separates text-level numeric claim provenance from aggregate coverage and
    figure reproduction.

- [ ] Track Appendix B.1-B.3 autocorrelation step-function evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.1-B.3 gives
    three separate autocorrelation/autoconvolution claims with different
    constants and proof directions: a `600`-interval step function on
    `[-1/4, 1/4]` proving `C1 <= 1.5053`, a `50`-interval step function on the
    same domain proving `0.8962 <= C2`, and a `400`-interval step function on
    the same domain proving `C3 <= 1.4557`.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows
    and step-function payloads in general. The Appendix B registry now retains
    B.1-B.3 summary evidence for source section, constant id, `[-1/4, 1/4]`
    domain, interval counts `600`/`50`/`400`, equal spacing, non-negative
    versus signed function assumptions, prior bound/source, upper/lower-bound
    direction, reported bound, and an explicit `not_recorded_locally`
    construction-payload status. It now also retains a validated
    `step_function_payload_boundary` for each autocorrelation witness,
    enumerating required future metric-formula id, step-function payload
    hash/schema, interval count, domain/spacing/sign-policy certificates,
    verifier artifact, and recomputed-bound fields. The actual payloads,
    certificates, verifier artifacts, and recomputation evidence remain
    `not_recorded_locally`.
  - Required result: add paper/report evidence for Appendix B.1-B.3 rows:
    result id, metric formula id, step-function payload hash, verifier
    artifact, reported/recomputed value, and README/ROADMAP text that keeps
    the three autocorrelation claims distinct from broad Appendix B family
    coverage.

- [ ] Track Appendix B.8 point-set distance-certificate evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.8 and Figure 12
    report two distance-ratio point-set witnesses: 16 points in 2D with
    squared ratio `12.889266112`, improving the best known squared bound
    `12.890`, and 14 points in 3D with squared ratio `4.165849767`, improving
    the best known squared bound `4.168`.
  - Current gap: paper-facing Appendix B TODOs now preserve the B.8
    squared-ratio convention, point count, dimension, prior value/source, and
    left/right Figure 12 panel linkage. A validated
    `witness_certificate_boundary` now records required future fields for
    coordinate artifacts, point-count/dimension certificates, pairwise
    distance matrix artifacts, distance certificates, min/max distances,
    min/max pair-witness certificates, squared-ratio recomputation
    certificates, figure panel ids, and Figure 12 panel artifact path/hash
    fields. It also validates both missing-witness rows:
    the 16-point 2D/Figure 12 left row with squared ratio `12.889266112`
    versus prior `12.890`, and the 14-point 3D/Figure 12 right row with
    squared ratio `4.165849767` versus prior `4.168`, while keeping both
    witnesses explicitly `not_recorded_locally`. The registry still does not
    prove the actual coordinate witnesses: finite coordinate payload hash,
    point-count/dimension certificates, pairwise distance matrix artifact,
    all-pairs minimum/maximum distance certificate, min/max pair-witness
    certificates, recomputed squared ratio from coordinates, or rendered
    Figure 12 panel artifacts.
  - Required result: add paper/report evidence for Appendix B.8 witness rows:
    coordinate artifact hash, point-count/dimension certificates, pairwise
    distance matrix hash, pairwise-distance certificate hash, recomputed min
    and max distances, min/max pair-witness certificates, squared ratio from
    coordinates, and Figure 12 panel artifact hashes.

- [ ] Track Appendix B.5 minimum-overlap step-function evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.5 reports that
    the Erdos minimum-overlap constant has known bounds
    `0.379005 <= C5 <= 0.380927`, and that the Figure 10 step function
    slightly improves the upper bound to `C5 <= 0.380924`. The step-function
    formulation uses `h: [0, 2] -> [0, 1]`, requires
    `integral_0^2 h(x) dx = 1`, and minimizes
    `max_k integral h(x) * (1 - h(x + k)) dx`.
  - Current gap: paper-facing Appendix B coverage now retains the B.5
    normalized `[0, 2]` step-function formulation, source section, Figure 10
    result id, prior lower/upper values, and improved `C5 <= 0.380924`
    upper-bound comparison through a validated
    `step_function_result_boundary`. The boundary now explicitly requires
    future step-function artifact path/hash/schema, original-formulation
    mapping certificate, `[40]` equivalence-reference artifact, shift-domain
    certificate, value-range certificate, integral-normalization certificate,
    shift-objective recomputation certificate, recomputed upper bound, and
    rendered Figure 10 panel artifact fields, while keeping those statuses
    `not_recorded_locally`.
  - Required result: add paper/report evidence for the missing Appendix B.5
    Figure 10 witness artifacts: step-function payload hash, value-range
    certificate, original-formulation mapping certificate, `[40]`
    equivalence-reference artifact, shift-domain certificate,
    integral-normalization certificate, shift/objective recomputation,
    recomputed upper bound, rendered Figure 10 panel artifact, source section
    location, and README/ROADMAP text that keeps the minimum-overlap witness
    distinct from broad Appendix B family coverage.

- [ ] Track Appendix B.6 finite-set witness evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.6 improves the
    sums-and-differences lower bound using two finite integer-set witnesses:
    a set `U1` of size `2003` giving `1.1479 <= C6`, and a set `U2` of size
    `54265` giving `1.1584 <= C6`. The paper cites the Gyarmati et al.
    inequality, requiring `U` to contain zero and satisfy
    `|U - U| <= 2 max(U) + 1`, with the lower bound derived from
    `|U-U|`, `|U+U|`, and `2 max(U) + 1`.
  - Current gap: paper-facing Appendix B coverage now retains both B.6
    witness identities, set cardinalities, reported lower bounds, source
    section, theorem linkage, and required future finite-set witness fields
    through a validated `finite_set_witness_boundary`. The required fields now
    separate contains-zero, non-negative, sumset-cardinality, difference-set-
    cardinality, max-element, and lower-bound formula-substitution certificate
    hashes, and each missing witness has explicit `not_recorded_locally`
    statuses for those categories. It still does not retain real `U1`/`U2`
    payloads, `|U-U|`/`|U+U|` cardinalities, max elements, formula
    substitutions, or recomputed lower bounds.
  - Required result: add paper/report evidence for the missing Appendix B.6
    witness artifacts: sorted integer payload hashes, max elements,
    contains-zero and non-negativity certificates, sumset/difference-set
    cardinality certificates, max-element certificates, feasibility checks,
    `|U-U|`, `|U+U|`, denominator, formula-substitution certificate, derived
    lower-bound value, source section linkage, and README/ROADMAP text that
    separates the two finite-set witnesses from broad Appendix B family
    coverage.

- [ ] Track Appendix B.7 regular-hexagon packing evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.7 improves two
    regular-hexagon packing bounds: for `n = 11`, the outer regular-hexagon
    side length improves from `3.943` to `3.931`; for `n = 12`, it improves
    from `4.0` to `3.942`. Figure 11 maps these to left and right
    construction panels.
  - Current gap: paper-facing Appendix B coverage now retains the two B.7
    `n` rows, unit-hexagon side convention, outer side-length objective,
    prior/current values, comparison policy, source section, and Figure 11
    panel linkage through a validated `packing_result_boundary`. It still
    does not retain real placement payloads, placement hashes,
    pose/orientation schemas, regular-hexagon geometry certificates,
    containment certificates, pairwise-disjointness certificates, side-length
    recomputation certificates, recomputed outer side lengths, or rendered
    Figure 11 panel artifacts. The boundary now includes explicit
    pose/orientation, geometry-certificate, side-length recomputation, and
    Figure 11 panel artifact path/hash fields and keeps each panel artifact
    `not_recorded_locally`.
  - Required result: add paper/report evidence for the missing Appendix B.7
    witness artifacts: placement artifact hashes, pose/orientation schemas,
    regular-hexagon geometry certificates, containment certificates,
    non-overlap certificates, side-length recomputation certificates,
    recomputed side lengths, rendered Figure 11 panel artifacts, source
    section location, and README/ROADMAP text that separates the two hexagon
    witnesses from broad Appendix B family coverage.

- [ ] Track Appendix B.9-B.10 Heilbronn minimum-area evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.9-B.10 gives
    three Heilbronn construction claims: `n = 11` points in a unit-area
    triangle with minimum formed-triangle area greater than `0.0365` versus
    prior `0.036`; `n = 13` points in a unit-area convex region improving
    `0.0306` to `0.0309`; and `n = 14` points in a unit-area convex region
    improving `0.0277` to `0.0278`. Figure 13 maps these to left, middle, and
    right panels.
  - Current gap: paper-facing Appendix B coverage now retains the three
    B.9-B.10 parameter/domain rows, unit-area normalization requirement,
    prior/current values, comparison policy, source section, and Figure 13
    panel linkage plus required future panel artifact path/hash fields through
    validated `heilbronn_result_boundary` entries. It still marks
    `figure_panel_artifact_status` as `not_recorded_locally` and does not
    retain real point-coordinate payloads, domain artifacts, unit-area proofs,
    convexity proofs for B.10, triple-count enumeration certificates,
    all-triples minimum-area certificates, minimum-witness-triangle
    certificates, reported-value comparison certificates, recomputed minimum
    areas, or rendered Figure 13 artifacts.
  - Required result: add paper/report evidence for the missing Appendix
    B.9-B.10 witness artifacts: point and region artifact hashes, domain
    membership proofs, unit-area normalization proof, convexity proof,
    triple-count enumeration certificate, minimum triangle area certificate
    over all triples, minimum-witness-triangle certificate, reported-value
    comparison certificate, recomputed minimum area, source section location,
    and README/ROADMAP text that separates the three Heilbronn witnesses from
    broad Appendix B family coverage.

- [ ] Track kissing-number lemma certificate evidence for Appendix B.11.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.11 reports 593
    nonzero integral-coordinate points in dimension 11, with maximum norm
    smaller than minimum pairwise distance, and uses Lemma 1 to derive a valid
    kissing configuration and lower bound of at least 593.
  - Current gap: paper-facing Appendix B coverage now retains the B.11
    dimension, prior/reported lower bounds, 593-vector witness count,
    integral-coordinate and nonzero requirements, exact max-norm versus
    minimum-pairwise-distance condition, Lemma 1 input condition, and
    transformed-center formula through
    a validated `kissing_result_boundary`. It still does not retain a real
    593-vector payload, payload hash, count/dimension certificates,
    integral-coordinate certificate, nonzero certificate, norm/distance matrix
    artifacts, separate max-norm certificate, max-norm witness vector,
    separate minimum-pairwise-distance certificate, minimum-pair witness,
    strict norm-distance inequality certificate, Lemma 1 applicability
    certificate, transformed sphere-center and unit-sphere verification,
    kissing-angle certificate, or recomputed lower bound.
  - Required result: add paper/report evidence for the missing Appendix B.11
    witness artifacts: point-set artifact hash, exact coordinate and dimension
    metadata, cardinality check, norm/distance matrix artifacts, max-norm
    certificate, max-norm witness vector, minimum-pairwise-distance
    certificate, minimum-pair witness, strict norm-distance inequality
    certificate, Lemma 1 proof-step record, transformed sphere-center and
    unit-sphere verification, kissing-angle certificate, lower-bound claim id,
    and README/ROADMAP wording that distinguishes visual construction evidence
    from proof-grade kissing-configuration certification.

- [ ] Track Appendix B.12-B.13 circle/rectangle sum-of-radii evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.12-B.13 gives
    three packing claims: for `n = 26` circles in a unit square, the sum of
    radii improves from `2.634` to `2.635`; for `n = 32` circles in a unit
    square, it improves from `2.936` to `2.937`; and for `n = 21` circles in a
    rectangle of perimeter `4`, it improves from `2.364` to `2.3658`.
    Figure 14 maps these to left, middle, and right panels.
  - Current gap: paper-facing Appendix B coverage now preserves all three
    B.12-B.13 parameter/container rows, rectangle perimeter convention,
    prior/current values, Figure 14 panel linkage, B.13 caption display, and
    the smoke-only boundary for the checked-in 26-circle fixture through
    validated `sum_of_radii_result_boundary` entries. It still does not retain
    real container artifacts, circle-center/radius payloads, payload hashes,
    exact-count checks, payload-schema validation certificates,
    positive-radius certificates, containment certificates, pairwise
    non-overlap certificates, rectangle dimensions, rectangle-perimeter proof,
    sum-of-radii formula certificates, recomputed sums of radii, or rendered
    Figure 14 artifacts.
  - Required result: add paper/report evidence for the missing Appendix
    B.12-B.13 witness artifacts: container artifact hashes, circle
    center/radius artifact hashes, exact-count checks, payload-schema
    validation, positive-radius certificates, containment certificates,
    pairwise non-overlap certificates, rectangle dimensions,
    rectangle-perimeter proof, sum-of-radii formula certificates, recomputed
    sums of radii, Figure 14 panel artifacts, source section location, and
    README/ROADMAP text that keeps the smoke fixture distinct from full
    Appendix B packing evidence.

- [ ] Track initial-program idea provenance for human-seeded benchmark claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.1 identifies the
    initial solution and optional background knowledge as user inputs, and
    Section 3.1 says some matrix-multiplication runs were seeded with
    researchers' own ideas, including adding stochasticity to the evaluation
    function or using evolutionary approaches, which boosted performance for
    some parameters. In the local PDF, this appears on page 10, which also
    says most Table 2 results used a simple initial program.
  - Current evidence: paper-facing status already distinguishes seed baselines
    from generated candidates and preserves safe seed source paths/kinds in
    manifests and history. Seed-source records now allow optional idea
    metadata for initial-program idea class, seed variant id, contribution
    roles, prior-technique labels, and background references. Completed
    manifests include `runtime.history.initial_program_idea_provenance_report`,
    which links those fields to generation-0 history rows and declared metric
    names while keeping equal-budget result evidence and human-seeded parity
    false. `papers/initial_program_idea_provenance_boundary.json` now
    preserves this metadata-contract-only boundary as paper-manifest evidence.
    `papers/initial_program_seed_variant_matrix.json` now records the design-
    level comparison axes for simple, random, researcher-idea, stochastic-
    evaluation, and evolutionary-approach seed variants while marking prompt
    context linkage, rendered prompt digests, prompt-history spans, seed
    workspace hash linkage, replicate protocols, equal-budget outcomes,
    benchmark tables, and human review as not recorded locally.
  - Required result: add paper/report evidence for prompt/context linkage,
    exact rendered prompt digests, prompt-history span refs, seed workspace
    hashes, per-variant run-artifact manifests, replicate protocols, executed
    equal-budget seed-variant outcomes, simple/random/researcher-idea seed
    comparisons, matrix and constructive-math seed-variant result tables,
    matrix-parameter seed-idea attribution, and contribution review/signoff
    before claiming AlphaEvolve-style scientific-collaboration or
    human-seeded matrix result parity.

- [ ] Track strict completeness of initial programs separately from
      optimization-pressure seeds.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.1 describes the
    initial implementation inside code blocks as complete, even if
    rudimentary, with the broader skeleton used by the evaluator to run the
    evolving solution. In the local PDF, page 5 says user-provided code inside
    evolution blocks serves as the initial solution, and Figure 2 on page 4
    places the initial program before the discovery loop.
  - Current evidence: LibreEvolve can evaluate and record invalid generation-0
    seeds as failed baselines, and README explicitly names examples such as
    `hello_world` as invalid greeting seeds used for seed-to-best optimization
    pressure. Current seed provenance and evaluator-contract records prove
    where a seed came from and how it evaluated; the runtime can also log an
    all-invalid seed-only run as completed with `no_valid_programs`. Code now
    provides `initial_program_validity_policy: alphaevolve_strict` and
    `runtime.history.initial_program_validity_report`, which distinguishes
    permissive baseline runs from strict runs where all selected seeds must be
    evaluator-valid and metric-complete before mutation. The
    `embedded_evaluate_math` smoke fixture now opts into strict mode, and the
    CLI regression records a claim-ready single-seed strict report for that
    loaded embedded-evaluator fixture. The paper-facing sidecar
    `papers/initial_program_validity_boundary.json` now records this
    strict-policy-available boundary and keeps default permissive runs outside
    complete initial-program parity claims.
  - Required result: require strict-seed validity for AlphaEvolve-parity
    benchmark fixtures, add paper-facing fixture evidence for complete/runnable
    starts across matrix and constructive-math benchmarks, add multi-seed and
    provider-startup strict evidence, record selected-seed counts and per-seed
    failure diagnostics in strict certification rows, and enforce that seed
    failure logs from permissive optimization-pressure examples are not treated
    as paper-ready initial-solution evidence.

- [ ] Populate expert-reviewed problem-formulation evidence for mathematical
      benchmarks.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 1 separates
    human-defined problem setup from AlphaEvolve's search, naming evaluation
    criteria, initial solution, and optional background knowledge as human
    inputs. Section 3.2 says most mathematical discoveries came from open
    problems suggested by external mathematicians Javier Gomez Serrano and
    Terence Tao, who advised on how to best formulate them as AlphaEvolve
    inputs.
  - Current evidence: paper-facing status records problem/source provenance,
    local context-source selection, local paper context, retrieval grounding,
    seed source identity, optional `formulation.yaml` /
    `Problem.formulation_metadata`, normalized `problem.formulation_metadata`,
    a task-spec `human_problem_formulation` field, and
    `runtime.history.problem_formulation_provenance_report`. The report records
    contributor roles, problem-origin and formulation notes,
    objective/evaluator rationale, parameter-scope decisions,
    background-knowledge refs, and review/signoff readiness. Current
    paper-facing status now includes
    `papers/problem_formulation_provenance_boundary.json` as the committed
    metadata-contract-only sidecar for expert-guided formulation claims. It also includes
    `runtime.history.benchmark_fixture_readiness_report` for run-level
    smoke-only scope, missing AlphaEvolve-comparable benchmark scope,
    hardening references, and explicit false readiness for repeated-seed
    protocols, SOTA/target baselines, fixture-emitted result artifacts, and
    anti-gaming negative-fixture evidence. The committed
    `papers/benchmark_fixture_readiness_boundary.json` sidecar now preserves
    this smoke-fixture readiness boundary for paper-manifest validation.
    Current mathematical benchmark fixtures still lack real populated
    expert/owner identity records, evaluator/report artifact links,
    parameter-scope signoff, background-reference artifact links, review
    timestamps or versions, anti-gaming review evidence, paper-facing
    certification examples, and paper-claim-ready benchmark evidence.
  - Required result: populate matrix and constructive-math benchmark fixtures
    with reviewed formulation records, external expert and problem-owner
    identity evidence, evaluator/report artifact links, parameter-scope
    signoff, background-reference artifact links, review timestamps or
    versions, anti-gaming review evidence, and paper-facing examples or
    certification rows, and require review/signoff state before claiming
    AlphaEvolve-style expert-guided mathematical discovery setup.

- [ ] Track Section 3.2 incumbent-construction handoff evidence separately
      from generic benchmark artifacts.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says many
    mathematical applications evolved search heuristics that receive a time
    budget and a strong previously found construction, then search for an
    improved construction. This differs from only validating a final
    construction artifact after the fact.
  - Current evidence: paper-facing coverage now includes a Section 3.2
    heuristic-handoff absence boundary in
    `libreevolve.problems.benchmarks.math_outcomes`. It preserves the
    search-heuristic-not-direct-construction method, fixed-budget example,
    previous-best construction input, and better-construction selection target,
    while marking heuristic programs, incumbent/produced construction
    artifacts, before/after metrics, scores, and verifier evidence absent. The
    committed `papers/math_heuristic_handoff_boundary.json` sidecar now emits
    this boundary for paper-manifest validation alongside the related Section
    3.2 outcome, starting-construction, and stage-sequence boundary sidecars.
  - Required result: before claiming Section 3.2-style constructive-math
    alignment, add paper/report evidence for incumbent identity, budget,
    heuristic output construction, verifier/certificate inputs, and improvement
    status for at least one constructive-math benchmark family.

- [ ] Track Section 3.2 heuristic-stage sequence evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says the evolved
    heuristic receives a fixed time budget, for example `1000 seconds`, and the
    best construction from the previous best heuristic. It then says final
    constructions were often produced by a sequence of different specialized
    heuristics, with early stages making large gains from random/simple initial
    states and later stages fine-tuning near-optimal configurations.
  - Current gap: paper-facing coverage now includes a Section 3.2
    stage-sequence absence boundary in
    `libreevolve.problems.benchmarks.math_outcomes`. It preserves the
    specialized-heuristic sequence statement, early broad-gain role, and later
    fine-tuning role, while marking per-stage rows, ordering, heuristic
    artifacts, input/output constructions, improvement deltas, and verifier
    evidence absent. The committed
    `papers/math_heuristic_stage_sequence_boundary.json` sidecar now emits
    this boundary for paper-manifest validation alongside the related Section
    3.2 outcome, starting-construction, and heuristic-handoff boundary
    sidecars.
  - Required result: add paper/report evidence for heuristic stage index,
    allotted budget seconds, previous-best construction id, candidate heuristic
    id, produced construction id, score before/after, improvement delta, stage
    role (`early_broad_gain` or `late_fine_tuning`), and verifier links before
    describing LibreEvolve results as AlphaEvolve-style multi-stage adaptive
    search.

- [ ] Track aggregate constructive-math breadth and outcome-rate evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says
    AlphaEvolve was applied to a curated set of over 50 mathematical problems
    spanning more than five branches, rediscovered the best known
    constructions in about 75% of cases, and improved the SOTA in about 20%.
  - Current evidence: paper-facing coverage now includes a Section 3.2
    aggregate-outcome absence boundary in
    `libreevolve.problems.benchmarks.math_outcomes`. It preserves the
    over-50-problem, more-than-five-branch, roughly 75% best-known
    rediscovery, roughly 20% SOTA-improvement, and verification-claim source
    facts plus the required future per-instance and aggregate fields. It does
    not yet provide the per-problem/per-parameter outcome ledger whose branch
    labels and matched/improved/failed counts reproduce the aggregate claims.
    The committed `papers/math_outcome_boundary.json` sidecar now emits this
    boundary for paper-manifest validation alongside the related Section 3.2
    starting-construction, heuristic-handoff, and stage-sequence boundary
    sidecars.
  - Required result: add paper/report evidence for constructive-math problem
    instances, branch taxonomy, parameter settings, previous-best references,
    AlphaEvolve/LibreEvolve result status, construction/verifier links, and
    validated aggregate percentages before claiming Section 3.2-style
    mathematical breadth or SOTA-improvement rates.

- [ ] Track simple/random starting-construction evidence for constructive math.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says that in
    the constructive-math cases summarized by the best-known rediscovery and
    SOTA-improvement percentages, "the initial starting point was a simple or a
    random construction."
  - Current gap: paper-facing coverage now includes a Section 3.2
    starting-construction absence boundary in
    `libreevolve.problems.benchmarks.math_outcomes`. It preserves the
    simple-or-random source statement and required future fields for
    per-instance starting class, artifact hash, generator/random seed,
    baseline metric, and prior-best visibility/seeding policy. It does not yet
    provide those rows or artifacts. The committed
    `papers/math_starting_construction_boundary.json` sidecar now emits this
    boundary for paper-manifest validation alongside the related Section 3.2
    outcome, heuristic-handoff, and stage-sequence boundary sidecars.
  - Required result: add paper/report evidence for each constructive-math
    problem instance: starting-construction class (`simple`, `random`,
    `human_seeded`, or `prior_art_seeded`), construction artifact/hash,
    generator and random seed where relevant, baseline value, prior-best
    visibility/seeding policy, and aggregate validation that Section 3.2-style
    breadth claims are supported by simple/random starts unless explicitly
    labeled otherwise.

- [ ] Track Appendix B result-version provenance for revised constants.
  - Paper evidence: Appendix B.4 reports an uncertainty-inequality construction
    with `C4 <= 0.3521`, then adds a note that after the first manuscript
    version Henry Cohn identified a refined approach and AlphaEvolve improved
    the reported constant further to `0.3216`, with details delegated to the
    accompanying Google Colab.
  - Current gap: paper-facing Appendix B coverage now distinguishes the B.4
    first-version `C4 <= 0.3521` result, Henry Cohn's pointer to `[18]`, the
    external refined `0.3284`, and AlphaEvolve's revised `0.3216` through a
    validated `revision_result_boundary`. It still does not include the
    revision artifact, Colab/verifier reference, source manuscript date,
    comparison-to-`0.3284` certificate, or recomputed revised constant.
  - Required result: add paper/report evidence for the missing result revision
    artifacts: manuscript/source version, superseded/current status,
    verifier/Colab linkage, comparison-to-`0.3284` certificate, recomputed
    revised constants, and artifact hashes before claiming Appendix B result
    parity. README, ROADMAP, papers index, and code TODOs should keep Appendix
    B wording scoped until versioned artifacts prevent mixing stale and current
    mathematical claims.

- [ ] Track Appendix B.4 prior-bound rounding evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.4 gives the known
    uncertainty-inequality range as `0.2025 <= C4 <= 0.3523`. It notes that
    reference `[33]` states the prior upper bound as `0.353`, but that rounding
    the referenced solution to the fourth digit gives `0.3523`, which is the
    comparison baseline for AlphaEvolve's first-version `C4 <= 0.3521` result.
  - Current gap: paper-facing Appendix B coverage now preserves the prior
    source's stated value versus rounded value, lower-bound context, rounding
    policy, and comparison baseline through validated B.4
    `source_formulation_evidence` and `prior_bound_rounding_evidence`. It does
    not yet retain a `[33]` page/section locator, source-solution artifact, or
    rounding-audit certificate that would independently audit the rounding
    statement.
  - Required result: add B.4 paper-evidence records for the prior `[33]`
    source locator/artifact status, rounded-solution artifact, and
    rounding-audit certificate needed to audit the stated `0.353` versus
    rounded `0.3523` distinction, while keeping README/ROADMAP wording
    separate from the later `0.3216` revision and from Hermite-polynomial
    certificate evidence.

- [ ] Track Appendix B.4 Hermite-polynomial certificate evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.4 derives
    `C4 <= 0.3521` from a Fourier test function
    `f(x) = P(x) exp(-pi x^2)`, with `P` an even linear combination of Hermite
    polynomials `H_{4k}`. The paper reports approximate coefficients
    `[0.32925, -0.01159, -8.9216e-5]` for `H0`, `H4`, and `H8`, then computes
    the upper bound from the largest positive root of `P(x)/x^2` using
    `r_max^2 / (2*pi)`.
  - Current gap: paper-facing Appendix B coverage now records a validated B.4
    `hermite_result_boundary` for the Hermite basis terms, approximate
    coefficients, `P(0)=0`/`x^2` factor step, largest-root computation, and
    `r_max^2 / (2*pi)` formula. It still does not contain coefficient payload
    hashes, verifier artifacts, Hermite-basis certificates, Fourier-transform
    certificates, origin-condition certificates, eventual-nonnegative
    certificates, root certificates, or recomputed-bound evidence.
  - Required result: add paper/report evidence for the missing B.4 coefficient
    payload, Hermite-basis and Fourier/test-function certificates,
    origin-condition and eventual-nonnegative certificates,
    largest-positive-root calculation, bound recomputation, verifier artifacts,
    and documentation that separates this certificate from B.4 revision-history
    and near-optimality interpretation evidence.

- [ ] Track Appendix B.4 prior-construction similarity and hypothesis evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.4 reports the
    uncertainty-inequality construction and then says the AlphaEvolve linear
    combination is qualitatively very similar to the construction in reference
    `[33]`, which the paper presents as empirical confirmation of the
    hypothesis that the construction is nearly optimal.
  - Current gap: paper-facing Appendix B coverage now preserves the qualitative
    construction-to-prior comparison and near-optimality hypothesis as a
    distinct validated B.4 `prior_construction_similarity_evidence` claim. It
    still does not include the actual prior construction identifier,
    coefficient payloads, basis-alignment evidence, coefficient-similarity
    metric, or near-optimality hypothesis source artifact.
  - Required result: add B.4 paper-evidence records for the missing comparison
    artifacts to reference `[33]`: prior construction identifier, comparable
    structure or coefficient fields, source page/section, evidence-strength
    label, and README/ROADMAP wording that does not conflate numerical
    improvement with qualitative hypothesis support.

- [ ] Generate AlphaEvolve-suite matrix-result publication artifacts.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 and Appendix A
    report matrix multiplication over 54 target sizes, measure both the best
    rank and the fraction of random seeds achieving that rank, provide exact
    algorithms with integer or half-integer entries, and point readers to an
    accompanying Google Colab for the constructions.
  - Current evidence: the active benchmark-hardening TODOs require stronger
    matrix validation, repeated seeds, exact verification, target/SOTA
    thresholds, and benchmark reports. A new
    `libreevolve.matrix_result_report.v1` contract validates target identity,
    dimensions, best rank, seed count, fraction of seeds achieving the best
    rank, exact coefficient domain, exactness certificate status, per-seed
    results, artifact paths/hashes, top-level best-rank and hit-fraction
    consistency against per-seed ranks/flags, summary rendering, and an
    explicit `alphaevolve_comparable` policy. Exploratory `rational` and
    `float` coefficient-domain reports remain valid only when
    `alphaevolve_comparable` is false; AlphaEvolve-comparable claims require
    integer or half-integer coefficients, verified exactness, exact per-seed
    rows, and algorithm/certificate/notebook artifacts. The report contract
    now uses `libreevolve.alphaevolve_appendix_a_matrix_registry.v1` to record
    the 54 Appendix A Table 3 target identities, dimensions, best-known ranks,
    AlphaEvolve ranks, and matched/surpassed/fell-behind outcomes; reports for
    `alphaevolve_appendix_a` reject unknown target ids and dimension
    mismatches. The registry is not itself construction evidence: it does not
    store target tensors, discovered tensor decompositions, coefficient lists,
    per-target exactness certificates, notebook exports, or construction
    provenance for reproducing Appendix A algorithms. The standard
    `paper_manifest` command now also validates Appendix A registry integrity
    when the checked-in registry is present, using the same routine gate that
    validates Appendix B and ablation registries.
    `libreevolve.matrix_result_artifact_inventory.v1` now verifies
    declared algorithm/certificate/notebook artifact paths against concrete
    files under an explicit artifact root, checking safe relative paths,
    existence, SHA-256 hashes, and byte counts.
    `write_strassen_2x2_publication_bundle()` now provides a concrete checked
    Strassen baseline for the registered `mm_2x2x2` target, with canonical
    algorithm, certificate, notebook, report, and artifact-inventory files and
    exact rank-7 per-seed rows. `validate_matrix_publication_bundle()` now
    checks the `libreevolve.matrix_publication_bundle.v1` wrapper, embedded
    report, target identity, report-file hash/byte evidence, and inventory
    consistency for that baseline. The paper index now distinguishes that one
    checked Strassen baseline from the still-missing generated notebook/export
    equivalents for reproducing discovered algorithms across the full Appendix
    A suite.
    `libreevolve.matrix_suite_publication_artifact_boundary.v1` now records
    the current `not_generated_locally` boundary and validates required future
    fields for one generated artifact record per registered Appendix A target:
    target tensor, algorithm, coefficient data, exactness certificate,
    notebook, per-seed report, embedded matrix-result report, artifact
    inventory, publication-bundle refs, artifact paths, and hashes. The
    paper-manifest gate validates this boundary.
    `papers/matrix_suite_publication_artifacts.json` now emits that
    absence/readiness boundary as a committed sidecar.
    `matrix_suite_publication_artifact_boundary_from_artifacts()` can build the
    generated boundary from one record per registered target and validation
    checks nested matrix-result report linkage, but no paper-facing exporter
    produces the full suite artifact set yet.
  - Required result: connect real matrix target tensors, exact algorithm
    artifacts, coefficient-domain data, certificate-generation artifacts, and
    generated export/notebook links to real report instances. The remaining
    gap is producing those discovered tensor artifacts for the suite and adding
    target-suite curation provenance, not validating Appendix A registry
    integrity, verifying declared report artifacts, validating the checked
    bundle wrapper, emitting one checked Strassen baseline once those files
    exist, or declaring the suite-wide publication artifact boundary.

- [ ] Wire best-known-rank citation provenance into Appendix A exports.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 presents matrix
    targets with a `best known [reference]` column, and Appendix A Table 3
    extends the matrix target-suite rank comparisons.
  - Current evidence: the checked Appendix A matrix registry records
    best-known rank numbers, AlphaEvolve ranks, outcomes, and exact-algorithm
    flags, and matrix reports can validate target identities and dimensions
    against that registry.
    `papers/appendix_a_matrix_baseline_citations.json` now preserves the
    cited prior-work source for each best-known baseline rank, source
    page/table, reference id, source artifact digest, finite-field or
    characteristic caveat, and baseline-source field.
    `libreevolve.alphaevolve_appendix_a_matrix_baseline_citation_boundary.v1`
    validates the emitted sidecar and per-target citation fields.
  - Required result: wire the paper-facing baseline-rank provenance into
    exports before using Appendix A best-known-rank comparisons as fully
    traceable generated evidence: report-visible baseline-source fields and
    docs that distinguish cited prior baselines from LibreEvolve-generated
    constructions.

- [ ] Track matrix cascade-run evidence behind repeated-seed rank claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 says the matrix
    experiments run over multiple random seeds using the evaluation cascade,
    and paper-visible performance is the best rank plus the fraction of seeds
    that reached it.
  - Current gap: the paper-facing matrix report contract validates declared
    seed rows and aggregate hit fractions, while generic cascade TODOs track
    cascade semantics.
    `libreevolve.matrix_cascade_run_runtime_boundary.v1` now validates the
    current `not_emitted_by_local_runner` boundary and emitted target/seed,
    cascade, stage-trace, final-rank, candidate/result reference,
    artifact-path, and hash fields.
    `papers/matrix_cascade_run_runtime_boundary.json` now emits that
    absence/readiness boundary as committed paper-facing evidence.
    `matrix_cascade_run_runtime_boundary_from_matrix_result()` builds one
    emitted record per seed row from per-seed stage traces and checks final
    stage/result-row linkage plus best-rank/hit-fraction aggregation. It does
    not yet require local matrix runners to preserve emitted matrix-specific
    executed cascade traces behind the published Table 2/Appendix A rank and
    hit-fraction rows.
  - Required result: connect actual matrix runners to emitted cascade records
    before treating per-seed matrix result reports as AlphaEvolve Section 3.1
    search evidence.

- [ ] Wire Table 2/Table 3 matrix-rank table artifacts into paper exports.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 is the main-text
    selected matrix-rank comparison table, and Appendix A Table 3 is the full
    54-target version with best-known ranks, AlphaEvolve ranks, outcome
    coloring/summary counts, complex-valued row caveats, Colab decomposition
    links, and the concurrent-work note for `<4, 5, 6>`.
  - Current gap: `libreevolve.alphaevolve_matrix_rank_table_exhibit.v1` now
    preserves Table 2/Table 3 as declared table exhibits with stable ids,
    selected-row versus full-table relation, row ordering, caption aggregate
    checks, color/outcome encoding, complex-valued annotations, note linkage,
    source PDF/caption locations, rendered table artifact hashes, and
    row-to-registry/report/Colab mappings.
    `papers/matrix_rank_table_artifacts.json` now emits paper-facing Table 2
    and Appendix A Table 3 artifact records, and
    `libreevolve.alphaevolve_matrix_rank_table_artifact_boundary.v1` validates
    that emitted sidecar plus nested table linkage. No paper-facing table
    export currently attaches those rendered/source/OCR files automatically.
  - Required result: wire the emitted paper-table artifacts into report/table
    export outputs with source PDF page/caption locations, table ids, row
    ids/order, selected/full-table membership, rank values, outcome classes and
    aggregate count validation, complex-valued and concurrent-work annotations,
    rendered table artifact hashes, and links to Appendix A registry rows,
    matrix reports/certificates, and companion source evidence.

- [ ] Track matrix result subset-scope evidence for Table 2 versus Appendix A
      outcome claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 states that for all
    parameters `m, n, p <= 5`, AlphaEvolve matched or surpassed the best-known
    solutions. Appendix A Table 3 is the full 54-target table and includes
    rows outside that main-text subset.
  - Current gap: `libreevolve.alphaevolve_matrix_subset_scope.v1` now provides
    paper-facing subset summaries for `main_text_mnp_le_5`, `table_2_selected`,
    and `appendix_a_full`, proving which rows belong to the `m,n,p <= 5`
    main-text claim, which rows are selected for Table 2, and why the
    larger-target `fell_behind` rows do not contradict the scoped Table 2
    statement. It validates inclusion predicates, row counts, outcome counts,
    out-of-scope row ids, and source-caption/table linkage.
    `papers/appendix_a_matrix_subset_scope_artifacts.json` now carries the
    three subset-scope artifacts as paper-facing records with nested subset
    evidence, artifact path, and SHA-256 digests.
    `libreevolve.alphaevolve_matrix_subset_scope_artifact_boundary.v1` now
    validates the emitted sidecar and emitted-artifact fields for subset
    identity, inclusion predicates, source linkage, counts, fell-behind/
    out-of-scope ids, nested subset evidence, paths, and hashes.
    `appendix_a_matrix_subset_scope_artifact_boundary_from_records()` builds
    emitted artifacts from validated subset evidence and checks nested linkage,
    but rendered table/report exports still do not attach the subset-scope
    records automatically.
  - Required result: connect rendered table/report exports to the committed
    subset-scope artifacts so scoped main-text claims remain distinct from
    full Appendix A aggregate outcomes wherever matrix rank rows are
    published.

- [ ] Wire matrix headline historicity artifacts into paper exports.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` abstract reports a procedure
    for multiplying two 4x4 complex-valued matrices using 48 scalar
    multiplications. Section 3.1 adds that recursive Strassen gives rank 49
    over any field, Fawzi et al. found rank 47 only over the field with two
    elements, and AlphaEvolve is the first method in 56 years to find rank
    below 49 over a characteristic-zero field.
  - Current gap: `libreevolve.matrix_headline_historicity_evidence.v1` now
    validates declared paper-facing matrix-headline provenance: target id,
    dimensions, scalar field/characteristic, reported rank, 56-year
    first-below-49 flags, Strassen/Fawzi prior comparisons, bibliography-style
    reference ids, source refs, and links to result, scalar-field, tensor-rank,
    Figure 4, Figure 9, and companion Colab evidence.
    `papers/matrix_headline_historicity_artifacts.json` now emits the
    paper-facing rank-48 headline historicity sidecar, and
    `libreevolve.matrix_headline_historicity_runtime_boundary.v1` validates
    that emitted sidecar plus emitted records for run/target/candidate ids,
    dimensions, headline rank/field values, source refs, prior comparisons,
    evidence links, matrix-result refs, artifact paths, and artifact hashes.
    `matrix_headline_historicity_runtime_boundary_from_evidence()` builds a
    runtime row from validated headline evidence and validation checks linkage
    to nested target, dimensions, headline claim, source refs, prior
    comparisons, evidence links, and matrix-result provenance. A table row or
    scalar-field record alone still would not prove the "first improvement
    after 56 years" claim, and paper-facing exports still do not automatically
    attach the committed source-span/decomposition/certificate/Colab evidence.
  - Required result: wire the paper-facing matrix-headline provenance artifact
    into export outputs with target id, dimensions, scalar field/
    characteristic, reported rank, Strassen baseline rank and scope,
    finite-field Fawzi caveat, bibliography reference ids, abstract and
    Section 3.1 page/span locations, decomposition/certificate/Colab links,
    and validation that docs distinguish rank/certificate evidence from
    historicity and field-scope claims.

- [ ] Track Appendix A matrix row-note and concurrent-work provenance.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A Table 3 includes
    a note that concurrent work [49] also found a rank-90 algorithm for the
    `<4, 5, 6>` target.
  - Current gap: `libreevolve.alphaevolve_appendix_a_matrix_row_notes.v1` now
    preserves row-level notes, concurrent-work attribution, independently
    matched result flags, note source location, and docs caveats for
    `mm_4x5x6`. It records that reference `[49]` also found a rank-90
    algorithm for `<4, 5, 6>`, independently matching AlphaEvolve's rank.
    `papers/appendix_a_matrix_row_note_artifacts.json` now carries this
    row-note caveat as a paper-facing artifact with nested row-note evidence,
    artifact path, and SHA-256 digest.
    `libreevolve.alphaevolve_appendix_a_matrix_row_note_artifact_boundary.v1`
    now validates the emitted sidecar and emitted-artifact fields for note
    identity, target/rank/reference values, source text, caveat flags, nested
    row-note evidence, paths, and hashes.
    `appendix_a_matrix_row_note_artifact_boundary_from_records()` builds
    emitted artifacts from validated row-note evidence and checks nested
    linkage, but rendered table/report exports still do not attach the caveat
    automatically.
  - Required result: connect rendered table/report exports to the committed
    row-note artifact so Appendix A matrix claims carry the concurrent-work
    caveat wherever rank/outcome rows are published.

- [ ] Track follow-on mathematical-discovery result rows from `2511.02864`.
  - Paper/source evidence: arXiv `2511.02864v3`, `Mathematical exploration
    and discovery at scale`, is the follow-on source named by the AlphaEvolve
    Section 3.2 mathematical-discovery handoff. The local cache now includes
    `papers/2511.02864__Mathematical_exploration_and_discovery_at_scale.pdf`
    and `papers/follow_on_sources.json` validates the paper/repository source
    row.
  - Current gap: the cached PDF and source manifest prove source identity and
    provenance only. LibreEvolve still does not normalize this follow-on
    paper's result rows, construction payloads, verifier artifacts, recomputed
    values, or full notebook cell inventory into paper-facing benchmark
    evidence.
  - Required result: add scoped follow-on result evidence before claiming
    implementation, benchmark parity, verifier coverage, or recomputed
    mathematical results from `2511.02864`.

- [ ] Track paper-artifact creator and assembler roles for figures and Colab.
  - Paper evidence: the Contributions section of
    `2506.13131__AlphaEvolve.pdf` states that N.V., E.D., M.E., S.C., A.N.,
    and A.Z.W. created the figures, while F.J.R.R., A.M., and A.Z.W. assembled
    the accompanying Google Colab.
  - Current gap: paper-facing TODOs require exhibit ids, source/caption
    locations, rendered artifact hashes, companion Colab URL/ref/digest
    records, and claim-to-cell mappings.
    `libreevolve.alphaevolve_paper_artifact_roles.v1` now records and validates
    the required paper-artifact role attribution for the figure set and
    companion notebook: artifact id/type, creator or assembler role,
    responsible initials/names, source section/page, and source phrases.
    `papers/paper_artifact_roles.json` now commits those records as
    paper-facing evidence. It does not yet bind those role records to concrete
    rendered figure files, companion notebook URLs, retrieval digests, artifact
    hashes, or notebook cell/source maps.
    `libreevolve.alphaevolve_paper_artifact_linkage.v1` now machine-validates
    that absence as a `not_yet_linked` availability boundary with expected
    digest/link/source-map fields for future concrete artifacts, and
    `papers/paper_artifact_linkage.json` commits that boundary. The companion
    Colab source mapping now preserves the Appendix B `result_row_boundary`
    inventory of `19` expected result ids. The paper-manifest gate validates
    both committed sidecars at the real repo root.
  - Required result: connect paper-facing artifact-role records to rendered
    figures and companion notebook source artifacts with digest/link metadata
    and README/ROADMAP wording that separates artifact availability from
    paper-attributed artifact authorship.

- [ ] Track Appendix A matrix target-suite curation provenance.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A says the 54
    matrix sizes were chosen roughly from dimensions with 2 <= m,n <= 5 and a
    reasonable cutoff for p, and that symmetries of the matrix multiplication
    tensor make axis permutations equivalent, so the reported suite focuses on
    sorted sizes m <= n <= p.
  - Current gap: the Appendix A registry records the 54 reported target ids,
    dimensions, ranks, and outcomes.
    `libreevolve.alphaevolve_appendix_a_matrix_curation.v1` now preserves the
    paper-facing target-suite selection rule, canonical sorted-representative
    policy, omitted symmetry-equivalent target ledger, unspecified p-cutoff
    source wording, and included-target rationales for the reported suite. It
    does not justify every possible excluded non-equivalent target outside the
    rough rank/size heuristic. `papers/appendix_a_matrix_curation.json` now
    emits that reported-suite curation record as committed paper-facing
    evidence.
    `libreevolve.alphaevolve_appendix_a_matrix_excluded_target_curation_boundary.v1`
    now records the current `not_recorded_locally` boundary and validates
    required future excluded-target justification fields for excluded target
    ids, dimensions, exclusion class/reason, source basis, rough-rule and
    `p`-cutoff relations, symmetry-equivalence status, local attempt/resource
    frontier refs, artifact paths, and hashes.
    `papers/appendix_a_matrix_excluded_target_curation.json` now emits that
    absence boundary as committed paper-facing evidence. The paper-manifest
    gate validates both sidecars.
    `appendix_a_matrix_excluded_target_curation_boundary_from_records()` builds
    a recorded boundary from supplied excluded-target justifications and a
    declared coverage scope, but no paper-facing broad excluded-target
    justification corpus is emitted yet.
  - Required result: add paper-facing excluded-target justifications for
    non-equivalent matrix sizes outside the reported suite. Keep this separate
    from construction artifacts and from larger-target resource-frontier/OOM
    evidence.

- [ ] Track matrix target-scaling resource frontier and OOM evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A says the authors
    often ran out of memory when trying discovered programs on sizes beyond
    the reported table with 1000 random seeds on evaluators with a single GPU
    accelerator, and that extending to larger matrix sizes requires further
    optimization.
  - Current evidence: matrix registries and result reports cover the reported
    Appendix A target identities, rank outcomes, per-seed hit fractions, and
    artifact links once present. Generic runtime docs also track evaluator
    seconds, LLM budgets, accelerator environment hints, and unsupported
    CPU/memory/GPU quota enforcement.
    `libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1` now
    preserves the paper-only larger-target boundary for sizes beyond `<5,5,5>`,
    1000 random seeds, single-GPU evaluators, frequent OOM, and
    further-optimization need. `papers/appendix_a_matrix_resource_frontier.json`
    now emits that paper-only boundary as committed paper-facing evidence.
    `libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1`
    now validates that local matrix-specific resource-frontier attempts are
    absent and records the fields required before such evidence can be
    claimed: target identities, dimensions, seed counts, accelerator/GPU
    memory, OOM diagnostics, reduced-seed policy, artifacts, and
    attempted-versus-excluded target policy.
    `papers/appendix_a_matrix_local_resource_frontier.json` now emits that
    absence/readiness boundary as committed paper-facing evidence.
    `appendix_a_matrix_local_resource_frontier_from_attempts()` can build an
    `attempts_recorded` boundary from supplied local attempt diagnostics, but
    no paper-facing larger-target attempt corpus is emitted yet.
  - Required result: add local paper/report evidence from attempted larger
    matrix targets, measured accelerator/memory profile, resource exhaustion or
    OOM diagnostics, reduced-seed tradeoffs if used, and explicit
    inclusion/exclusion policy before claiming LibreEvolve can extend
    AlphaEvolve-style matrix search beyond the Appendix A target suite.

- [ ] Track matrix near-integrality prompt/evaluator evidence separately from
      publication-result validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 states that the
    natural-language prompt asked AlphaEvolve to generate near-integral matrix
    solutions, then the reported tensor-decomposition entries were rounded to
    the nearest integer or half-integer to verify exactness. Paper-visible
    evidence should show that this instruction and rounding/evaluation policy
    were part of the search workflow.
  - Current evidence: the matrix-result report contract validates declared
    coefficient-domain fields, exactness certificates, per-seed results,
    artifact hashes, Appendix A target identities, and the checked Strassen
    baseline bundle. Those checks prove that a report is internally
    consistent once produced. `libreevolve.matrix_near_integrality_evidence.v1`
    now validates paper/report evidence fields for the matrix prompt
    instruction, rounding policy, raw and rounded coefficient diagnostics,
    rounding-error consistency, and exactness-certificate links.
    `libreevolve.matrix_near_integrality_runtime_boundary.v1` now validates
    the current `not_emitted_by_local_runner` boundary and emitted records for
    run/target/candidate ids, seeds, prompt hashes/instructions, raw and
    rounded coefficients, rounding error, exactness-certificate links,
    matrix-result refs, artifact paths, and artifact hashes.
    `papers/matrix_near_integrality_runtime_boundary.json` now emits that
    absence/readiness boundary as committed paper-facing evidence.
    `matrix_near_integrality_runtime_boundary_from_evidence()` builds runtime
    rows from validated near-integrality evidence and validation checks linkage
    to nested target, prompt, candidate, rounding, and certificate evidence. It
    does not prove that current local matrix benchmark prompts/evaluators emit
    those records during search.
  - Required result: emit near-integrality evidence records from real matrix
    search runs, including prompt/run provenance and per-seed exactness linkage,
    before claiming AlphaEvolve Section 3.1 matrix-search parity.

- [ ] Track matrix sweep-space provenance for AlphaEvolve Figure 9 workflows.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figures 9a-9c show the
    matrix-search program evolving not only tensor update code but also a
    `sweep()` function with `hyper.uniform(...)` ranges for optimizer,
    discretization, noise, clipping, and related search parameters.
  - Current evidence: the matrix-result report contract validates finished
    result metadata and artifact references, and
    `libreevolve.matrix_sweep_space_evidence.v1` now validates declared
    sweep-space declarations, user-provided hyper-library identity, sampled
    configuration records, per-sweep losses/ranks, selected winner identity,
    and linkage from selected sweep configurations to final decomposition and
    exactness-certificate artifacts.
    `libreevolve.matrix_sweep_space_runtime_boundary.v1` now validates the
    current `not_emitted_by_local_runner` boundary and emitted records for
    run/target/candidate ids, seeds, search-program refs, sweep function
    identity, hyper-library and hyperparameter declarations, sampled
    configurations, winning configuration, certificate/decomposition refs,
    matrix-result refs, artifact paths, and artifact hashes.
    `papers/matrix_sweep_space_runtime_boundary.json` now emits that
    absence/readiness boundary as a committed sidecar.
    `matrix_sweep_space_runtime_boundary_from_evidence()` builds a runtime row
    from validated sweep-space evidence and validation checks linkage to nested
    target, search program, `sweep` function, hyper-library, hyperparameters,
    sampled configurations, winner, and selected certificate/decomposition
    evidence. Local matrix benchmark runners still do not emit those records
    from candidate-produced search programs.
  - Required result: add paper-facing emitted matrix benchmark artifacts for
    evolved sweep functions, hyperparameter range provenance, sampled sweep
    ids, per-sweep/per-seed outcomes, and final certificate linkage before
    treating LibreEvolve matrix runs as faithful to AlphaEvolve's Figure
    4/Figure 9 tensor-decomposition search workflow.

- [ ] Track Appendix A Figure 9a-9c magnified matrix-diff exhibits as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A says Figures 9a
    to 9c are the magnified version of Figure 4's left panel and show the
    program that discovers a rank-48 decomposition for multiplying two 4x4
    matrices, split across three source/diff panels. The panels show concrete
    code-change components: Adam to AdamW, scaled complex initialization,
    gradient/decomposition/target noise, soft clipping, hallucination and
    discretization losses, large-value penalties, and named `hyper` sweep
    fields.
  - Current gap: paper-facing TODOs cover the main Figure 4 exhibit and the
    Figure 9 sweep-space workflow, and
    `libreevolve.alphaevolve_figure9_matrix_diff_exhibit.v1` now validates
    Figure 9a/9b/9c exhibit records: panel IDs, PDF page/caption locations,
    exact code line spans, source/diff excerpt artifacts and hashes,
    rendered/OCR text hashes, ordered continuity across the three panels,
    semantic component labels for the source changes, and links from each
    panel to matrix target rows, sweep metadata, certificates, and companion
    notebook/source evidence.
    `libreevolve.alphaevolve_figure9_matrix_diff_artifact_boundary.v1` now
    validates the current `not_emitted_by_local_report_export` boundary and
    emitted panel, source-diff, rendered image, OCR, aggregate panel, artifact
    path/hash, and nested exhibit fields.
    `papers/figure9_matrix_diff_artifacts.json` now emits that
    absence/readiness boundary as a committed sidecar.
    `figure9_matrix_diff_artifact_boundary_from_exhibit()` builds emitted
    artifacts from validated Figure 9 exhibit metadata and checks nested panel
    linkage, but it does not render or commit those appendix panel artifacts.
  - Required result: add concrete paper-facing Figure 9 panel artifacts for
    each panel, including source PDF/source-diff excerpts, rendered visual/text
    artifacts, hashes, target/result-row linkage, sweep-field linkage,
    certificate/notebook links, and README/ROADMAP wording that separates
    reproduced Appendix A magnified-diff exhibits from Figure 4 main-text
    evidence and generic sweep-space provenance.

- [ ] Track Figure 4 matrix-discovery exhibit provenance as paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 4 presents the
    main-text matrix multiplication discovery exhibit, including a concrete
    4x4 tensor-decomposition search-program diff and the surrounding
    Section 3.1/Table 2 matrix rank-improvement context. Its caption says the
    displayed discovery required 15 mutations and made non-trivial changes to
    the optimizer, weight initialization, loss function, and hyperparameter
    sweep.
  - Current gap: matrix paper evidence tracks Appendix A target identities,
    report validation, companion Colab TODOs, near-integrality, scalar-field,
    baseline, and Figure 9 sweep-space gaps.
    `libreevolve.alphaevolve_figure4_matrix_discovery_exhibit.v1` now validates
    the paper-facing Figure 4 exhibit as its own evidence object with stable
    exhibit id, source PDF page/caption location, selected matrix target and
    result-row links, caption values, exact source diff excerpt artifact/hash,
    rendered visual/text artifact hashes, rendering/source parameters,
    15-mutation caption count, component labels for
    optimizer/initialization/loss/sweep changes, and links from the displayed
    figure to report, certificate, notebook, Figure 9, and source-paper
    artifacts.
    `libreevolve.alphaevolve_figure4_matrix_discovery_artifact_boundary.v1`
    now validates the current `not_emitted_by_local_report_export` boundary
    and emitted fields for rendered/source artifacts, accepted
    15-mutation lineage, artifact paths/hashes, and nested Figure 4 metadata.
    `papers/figure4_matrix_discovery_artifacts.json` now emits that
    absence/readiness boundary as a committed sidecar.
    `figure4_matrix_discovery_artifact_boundary_from_exhibit()` builds emitted
    artifacts from validated Figure 4 exhibit metadata plus supplied accepted
    mutation lineage and checks nested exhibit linkage. It does not render or
    commit those Figure 4 artifacts, and it does not
    prove the accepted 15-mutation sequence.
  - Required result: add concrete paper-facing Figure 4 rendered/source-diff
    artifacts and accepted-mutation lineage records with component labels,
    Table 2/Appendix A row mappings, rank/baseline values, decomposition
    report links, exactness certificates, companion notebook/source evidence,
    and README/ROADMAP wording that separates main-text exhibit reproduction
    from general matrix benchmark coverage.

- [ ] Track matrix baseline-component provenance for Section 3.1 workflows.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 says the
    matrix-decomposition work starts from the problem description and a
    standard gradient-based algorithm including an initializer, reconstruction
    loss function, and Adam optimizer, then evolves increasingly sophisticated
    tensor-decomposition algorithms.
  - Current evidence: the paper-facing matrix TODOs track result reports,
    Appendix A target curation, near-integrality prompt/evaluator evidence,
    sweep-space provenance, scalar-field evidence, resource-frontier records,
    and final artifact/certificate availability.
    `libreevolve.matrix_baseline_component_runtime_boundary.v1` now validates
    the current `not_emitted_by_local_runner` boundary and required future
    baseline component, optimizer, generation-0, lineage, result, artifact, and
    hash fields. `papers/matrix_baseline_component_runtime_boundary.json` now
    emits that absence/readiness boundary as committed paper-facing evidence.
    The builder can create emitted records from a component
    inventory and validate ref/scope/hash linkage, but local runs still do not
    provide a paper-facing emitted record for the generation-0 matrix solver
    components or mutation lineage showing how later accepted candidates
    changed the initializer, loss, optimizer, or surrounding search program.
  - Required result: add paper-facing matrix run artifacts that inventory the
    initial gradient-based algorithm, record initializer/loss/optimizer
    configuration and hashes, declare mutable and fixed scopes, include
    generation-0 baseline outcomes, and link accepted mutations to changed
    baseline components before claiming Section 3.1 workflow parity.

- [ ] Track matrix scalar-field evidence for complex-valued Appendix A claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 says some improved
    matrix algorithms, including selected Appendix A targets, use
    complex-valued multiplications and can be used for exact multiplication of
    complex or real-valued matrices. Section 3.1 also contrasts the
    characteristic-0 rank-48 result with finite-field-only prior work.
  - Current evidence: the matrix-result report contract validates target
    identity, dimensions, best rank, seed hit fraction, exactness status,
    coefficient domain, and algorithm/certificate/notebook artifacts.
    `libreevolve.matrix_scalar_field_evidence.v1` now validates declared scalar
    field, exact complex coefficient representation, field characteristic,
    real-versus-complex applicability, finite-field caveats, and certificate
    scope for those claims. `libreevolve.matrix_scalar_field_runtime_boundary.v1`
    now validates the current `not_emitted_by_local_runner` boundary and
    emitted records for run/target/candidate ids, seeds, scalar field,
    characteristic, applicability, coefficient representation, algorithm refs,
    certificate refs, matrix-result refs, artifact paths, and artifact hashes.
    `papers/matrix_scalar_field_runtime_boundary.json` now emits that
    absence/readiness boundary as a committed sidecar.
    `matrix_scalar_field_runtime_boundary_from_evidence()` builds a runtime row
    from validated scalar-field evidence and validation checks linkage to
    nested target, field claim, applicability, coefficient representation,
    algorithm, and certificate evidence. It does not emit exact complex
    decomposition/certificate artifacts.
  - Required result: add concrete paper/report artifacts for scalar field,
    exact complex coefficient data, characteristic/applicability claims, and
    certificate verification scope before claiming AlphaEvolve-comparable
    complex-valued matrix results.

- [ ] Track matrix tensor-rank applicability and recursive-use caveats.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 reports matrix
    results as low-rank tensor decompositions and footnote 3 says that some
    algorithms use fewer than 49 multiplications but do not correspond to
    decompositions of the matrix multiplication tensor and cannot be applied
    recursively to larger matrix multiplication.
  - Current gap: the paper-facing Appendix A registry/status and matrix result
    contract store target ids, dimensions, rank values, outcomes, exactness,
    coefficient domain, and artifacts. `libreevolve.matrix_tensor_rank_evidence.v1`
    now validates whether an algorithm is a tensor decomposition versus another
    multiplication algorithm, whether the construction is recursively
    applicable, whether the certificate proves the target tensor identity, and
    source-note caveats for comparisons against non-tensor or finite-field-only
    prior algorithms. `libreevolve.matrix_tensor_rank_runtime_boundary.v1` now
    validates the current `not_emitted_by_local_runner` boundary and emitted
    records for run/target/candidate ids, seeds, algorithm kind, rank,
    recursive applicability, certificate scope, tensor-identity status,
    target-tensor refs, exactness-certificate refs, matrix-result refs,
    artifact paths, and artifact hashes.
    `papers/matrix_tensor_rank_runtime_boundary.json` now emits that
    absence/readiness boundary as a committed sidecar.
    `matrix_tensor_rank_runtime_boundary_from_evidence()` builds a runtime row
    from validated tensor-rank evidence and validation checks linkage to nested
    target, rank claim, recursive-applicability, tensor-identity, target-tensor,
    and certificate evidence. It does not emit target-tensor/certificate
    artifacts.
  - Required result: add concrete paper-facing artifacts for matrix rank
    claims: algorithm kind, tensor-decomposition certificate scope, recursive
    applicability, source note/page or footnote locator, target tensor identity
    evidence, and docs validation that rank/outcome wording does not treat
    non-recursive multiplication algorithms as comparable tensor-rank
    baselines.

- [ ] Generate independent certification evidence for paper-level result
  claims.
  - Paper evidence: the AlphaEvolve paper distinguishes evaluator scores from
    stronger confirmation for deployed or claimed discoveries. Section 3.3.1
    reports post-deployment fleet measurements confirming a scheduling
    heuristic, and Section 3.3.4 states that the final FlashAttention changes
    were confirmed by human experts for all possible inputs.
  - Current evidence: `papers/README.md` correctly scopes the checked-in
    `circle_packing` and `matrix_multiplication` examples as smoke fixtures,
    and the active benchmark TODOs require harder validators, SOTA thresholds,
    artifacts, and equal-budget reports.
    `libreevolve.paper_result_certification.v1` now defines and tests a
    certification-report contract that separates local-validator records from
    paper-claim-ready independent certifications, requires verifier
    identity/independence, claim scope, verdict, passed evidence,
    evidence-kind-specific artifact requirements, and hashed artifact records,
    and renders summary readiness.
    `libreevolve.paper_result_certification_artifact_inventory.v1` now
    verifies the certification report's evidence and artifact records against
    concrete files under an explicit artifact root, checking safe relative
    paths, existence, SHA-256 hashes, byte counts, per-record status, and
    aggregate missing/mismatch/invalid counts. `validate_certification_evidence_bundle()`
    now validates certification reports together with their artifact inventory,
    requiring matching claim, benchmark, candidate, report schema, record hash,
    and zero missing/mismatch/invalid evidence before paper-claim readiness is
    accepted as a bundle. It still does not provide independent verifier
    scripts, external/human-review records,
    deployment/simulator confirmation records, or generated signed/exact
    certificate artifacts for actual benchmark claims.
  - Required result: connect benchmark outputs to real independent verifier
    scripts, exact certificate generation, reviewer/deployment provenance, and
    external confirmation artifacts before treating local evaluator validity as
    AlphaEvolve-style confirmed result evidence. The remaining gap is
    producing those independent evidence files from real verification
    workflows, not checking declared files or bundle consistency once a
    certification report names them.

- [ ] Connect systems-style benchmarks to held-out and reference-correctness
  evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3 evaluates
    production-oriented discoveries beyond the optimization loop: the Borg
    scheduling heuristic is optimized with historical simulator feedback, then
    measured on unseen recent workloads and post-deployment fleet data; the
    Gemini kernel heuristic is trained on collected input shapes and evaluated
    on held-out shapes; the FlashAttention IR task checks each modification
    against reference code on randomized inputs before expert confirmation.
  - Current evidence: the active benchmark and certification TODOs require
    stronger validators, artifacts, SOTA thresholds, and independent
    certification. `libreevolve.systems_result_report.v1` now defines and
    tests a report contract that separates optimization inputs from
    held-out/generalization gates and reference-correctness gates, persists
    case-set hashes, sample counts/seeds, finite metrics, artifact hashes,
    passed-gate artifact-kind requirements, and optional certification linkage
    that cannot contradict readiness claims. It rejects `alphaevolve_ready`
    claims unless held-out and reference gates passed or are explicitly
    documented as not applicable. Ready-report validation now also rejects
    generic `not_applicable` bypasses for domain-required gates:
    scheduling/kernel held-out, compiler/hardware reference-correctness, and
    generic systems held-out plus reference-correctness. This enforces the
    report contract; it does not create the real held-out or reference-check
    artifacts.
    `libreevolve.systems_result_artifact_inventory.v1` now verifies declared
    systems report artifacts against concrete files under an explicit artifact
    root, checking safe relative paths, existence, SHA-256 hashes, and byte
    counts for the metrics, heldout-report, reference-report, and summary
    evidence files. `validate_systems_evidence_bundle()` now validates systems
    reports together with their artifact inventory, requiring matching
    benchmark, candidate, domain, report schema, inventory status, record hash,
    and zero missing/mismatch/invalid evidence before accepting bundled
    AlphaEvolve readiness. `libreevolve.systems_evidence_bundle.v1` now wraps
    embedded systems report and inventory records with stable embedded-record
    hashes, inventory-record hash linkage, benchmark/candidate/domain identity
    checks, and readiness consistency validation.
    `papers/systems_result_readiness_boundary.json` now preserves a
    manifest-checked paper-facing boundary for these report, inventory, and
    bundle contracts without claiming real scheduling, kernel, compiler, or
    hardware fixture runs, deployment measurements, expert confirmations, or
    domain-specific result artifacts.
  - Required result: connect compiler, hardware, kernel, scheduling, or systems
    fixtures to this report format, implement real unseen evaluation cases and
    randomized/reference-correctness checks, and emit report artifacts that
    distinguish loop feedback from held-out, deployment, and certification
    evidence. The remaining paper gap is producing those evidence files from
    real fixture runs, not verifying the declared files, report/inventory
    consistency, or evidence-bundle consistency once a report names them.

- [ ] Record Section 3.3 result-claim metric calibration for systems reports.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3 reports specific
    claim magnitudes and units for engineering outcomes: Borg scheduling
    recovered about 0.7% fleet-wide compute resources, Gemini/Pallas kernels
    achieved 23% average kernel speedup and 1% Gemini training-time reduction,
    hardware RTL optimization targeted power and area, and FlashAttention IR
    changes delivered 32% kernel and 15% pre/postprocessing speedups. The
    Gemini/Pallas section also reports reducing kernel optimization time from
    several months of dedicated engineering effort to days of automated
    experimentation, plus deployment and research/engineering-velocity impact.
  - Current gap: `libreevolve.systems_result_report.v1` now requires
    `claim_calibration` before accepting `alphaevolve_ready` systems claims.
    It validates paper-facing records that identify which finite metric is the
    published-style claim, what unit and denominator it uses, which baseline and
    before/after window it compares against, how repeated measurements are
    aggregated, and what deployment/runtime/synthesis context makes the value
    comparable to the AlphaEvolve claim. Existing fixtures still lack real
    populated calibrated systems-result records and paper-facing certification
    examples.
  - Required result: populate paper-facing claim calibration records for
    systems results before treating finite metrics as reproduced Section 3.3
    outcomes: scheduling resource-recovery denominator/window; kernel speedup
    and training-time reduction baseline/runtime/shape-split aggregation; RTL
    power/area/PPA units and synthesis flow; and compiler kernel versus
    pre/postprocessing speedup attribution with randomized-reference and
    tolerance provenance. Also capture engineering-effort and
    deployment-velocity calibration for kernel claims, including manual-tuning
    baseline duration, automated-experiment duration, workflow affected, and
    production adoption status.

- [ ] Populate practical-application owner and reviewer provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3 presents
    practical systems discoveries as production-facing work in Borg scheduling,
    Gemini/Pallas kernels, TPU RTL, and XLA/FlashAttention IR. The
    Acknowledgements and Contributions sections also identify application
    co-leads, domain advisors, reviewers, validation infrastructure owners,
    TPU designers, and XLA modification reviewers tied to those systems
    results.
  - Current gap: `libreevolve.systems_result_report.v1` now requires
    `application_provenance` before accepting `alphaevolve_ready` systems
    claims. It validates owner/advisor, reviewer, validation/data-owner, and
    production-approver role coverage; domain, responsible team or role labels,
    review/signoff scope, validation/source ownership, approval/deployment
    state, claim links, artifact refs, and boundary wording that separates
    local benchmark evidence from domain-owner validated production claims.
    Existing fixtures still lack real populated reviewed owner/reviewer records
    and paper-facing certification examples.
  - Required result: populate practical systems fixtures with reviewed
    owner/reviewer provenance records linked to calibrated Section 3.3 claims,
    source evidence, and concrete artifacts; add paper-facing examples or
    certification rows; and keep docs from treating the schema alone as
    AlphaEvolve-style practical-application validation evidence.

- [ ] Track self-improvement and distillation evidence for Discussion claims.
  - Paper evidence: AlphaEvolve's Discussion says practical discoveries can
    improve its own infrastructure and future base LLMs, while distilling
    AlphaEvolve-augmented performance into the next generation of base models
    is a natural next step. Local PDF page 21 contains these Discussion claims.
  - Current gap: `papers/README.md`, benchmark reports, and runtime manifests
    do not yet identify any LibreEvolve infrastructure component as an evolved
    optimization target, do not connect an evolved candidate to measured
    improvements in the tool's own runtime/provider/compiler/benchmark
    infrastructure, and do not define distillation datasets, training runs, or
    model-evaluation artifacts derived from evolved programs. The
    ThetaEvolve-inspired `grpo_data.jsonl` export path is a bounded
    prompt/response/reward artifact and is explicitly not online RL training or
    base-model distillation evidence. The committed
    `papers/self_improvement_distillation_boundary.json` sidecar preserves
    this Discussion-context-only absence boundary for paper-manifest
    validation.
  - Required result: add paper-facing evidence boundaries for self-improving
    infrastructure and model-uplift claims: component identity, optimization
    objective, before/after measurements, deployment or adoption status,
    rollback/safety review, provenance linking the candidate to LibreEvolve's
    own execution path, production or self-hosted runtime evidence, base-LLM
    uplift target identity, and any distillation dataset/training/evaluation
    artifacts. Until then, keep Discussion-style self-improvement and
    distillation wording scoped as AlphaEvolve context rather than LibreEvolve
    capability.

- [ ] Track self-improvement feedback-loop cadence and environment-expansion
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Discussion says current
    gains from improving AlphaEvolve's own infrastructure and future base LLMs
    are moderate, that feedback loops for improving the next AlphaEvolve
    version are on the order of months, and that these improvements should
    make the value of setting up more robust-evaluator environments more
    widely recognized.
  - Current gap: paper-facing self-improvement TODOs require component
    identity, before/after measurements, deployment/adoption, rollback/safety,
    and distillation artifacts. They do not preserve cadence or return-on-
    environment evidence: which improvement loop affected a next version, how
    long that loop took, how moderate the gain was, or how the gain changed
    the expected value of creating more robust evaluation environments. The
    committed `papers/self_improvement_cadence_boundary.json` sidecar
    preserves this absence boundary for paper-manifest validation.
  - Required result: add paper/report evidence for self-improvement loop
    cadence and environment expansion with loop ids, optimized component,
    next-version target, start/end dates or elapsed months, measured gain,
    environment setup/maintenance cost, expected and realized discovery value,
    robust-evaluator environment identity, environment-expansion decision
    records, robust-evaluator readiness, and README/ROADMAP wording that
    separates months-scale feedback-loop economics from generic
    self-improvement or distillation capability.

- [ ] Populate Borg scheduling problem-formulation evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.1 frames Google
    Borg scheduling as an online vector bin-packing problem: machines are bins
    with CPU and memory capacity, pending jobs are items with CPU and memory
    requirements, stranded resources motivate the objective, and AlphaEvolve
    receives simulator feedback from historical workload and capacity
    snapshots.
  - Current gap: `libreevolve.systems_result_report.v1` now requires
    `scheduling_formulation` before accepting `alphaevolve_ready` scheduling
    claims. It validates the vector-bin-packing domain label, machine/bin and
    job/item roles, CPU/memory unit definitions and denominators, workload/
    capacity snapshot provenance, stranded-resource objective linkage,
    simulator input hashes, artifact refs, and mapping from those inputs to the
    heuristic's `required` and `free` CPU/memory features. Existing scheduling
    fixtures still lack real populated formulation records and paper-facing
    certification examples.
  - Required result: populate scheduling fixtures with reviewed
    vector-bin-packing formulation evidence, source/page linkage, simulator
    input artifacts, and paper-facing examples or certification rows; keep
    problem formulation separate from ranking-only safety, deployment metrics,
    and Figure 6 exhibit reproduction.

- [ ] Populate scheduling feasibility-boundary evidence for Borg-style results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.1 states that
    AlphaEvolve's scheduling heuristic scores machines after Borg has already
    determined that they are available and capable of running the pending job;
    the heuristic only influences ranking among feasible machines, so
    decisions are effectively correct by construction.
  - Current gap: `libreevolve.systems_result_report.v1` now requires
    `scheduling_safety` before accepting `alphaevolve_ready` scheduling claims.
    It validates paper-facing evidence for the external feasibility filter,
    ranking-only scope, resource/capacity invariants, simulator/admission/
    placement boundaries, direct authority flags, and safety artifact refs.
    Existing scheduling fixtures still lack real populated safety records and
    paper-facing certification examples.
  - Required result: populate scheduling fixtures with feasible candidate-set
    provenance, ranking-only function boundaries, resource invariant checks,
    simulator/admission-boundary artifacts, and deployment/simulator
    confirmation before claiming AlphaEvolve-comparable Borg-style scheduling
    evidence.

- [ ] Populate scheduling interpretability and mission-critical deployment
      evidence for Borg-style results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.1 says
    AlphaEvolve was chosen over deep reinforcement learning for scheduling
    because its code solution performed better and had advantages in
    interpretability, debuggability, predictability, and ease of deployment,
    which the paper calls essential for a mission-critical system.
  - Current gap: `libreevolve.systems_result_report.v1` now requires
    `scheduling_deployment_readiness` before accepting `alphaevolve_ready`
    scheduling claims. It validates paper-facing evidence for interpretable
    code/rule structure, debuggability and operator-review notes,
    predictability checks, deployment ergonomics, rollout/deployment-risk
    controls, learned-policy comparison, review flags, and artifact refs.
    Existing scheduling fixtures still lack real populated deployment-readiness
    records and paper-facing certification examples.
  - Required result: populate scheduling fixtures with reviewed interpretable
    code/rule structure, debuggability and operator-review artifacts,
    predictability or monotonicity checks, rollout/deployment-risk evidence,
    and black-box-baseline comparison before claiming AlphaEvolve-comparable
    mission-critical scheduling readiness.

- [ ] Track Figure 6 scheduling-heuristic exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 6 shows the concrete
    Borg scheduling heuristic `alpha_evolve_score(required, free)` with
    CPU/memory residual terms and a rendered residual heatmap. Section 3.3.1
    connects that heuristic to historical simulator feedback, unseen recent
    workload measurements, deployment, and about 0.7% fleet-wide compute
    resource recovery.
  - Current gap: paper-facing systems TODOs require claim-calibrated metrics,
    ranking-only scheduling safety, and interpretability/deployment evidence,
    and `papers/systems_result_readiness_boundary.json` now machine-records
    that Figure 6 scheduling-exhibit records, heatmap artifacts, and held-out/
    deployment links are required evidence.
    `papers/figure6_scheduling_exhibit_boundary.json` now keeps the
    exhibit-specific contract machine-checked. The paper-facing record still
    lacks real Figure 6 exhibit rows mapping exact heuristic code, residual-
    feature definitions and units, heatmap data, rendering parameters, visual
    artifact paths/hashes, baseline production heuristic identity, simulator/
    held-out/deployment reports, or a Section 3.3 claim-calibration record.
  - Required result: add Figure 6-style exhibit metadata with a stable exhibit
    ID, scheduling benchmark/candidate link, exact heuristic source artifact
    and hash, residual grid/units, baseline heuristic provenance, heatmap data
    and rendered visual artifacts with hashes, rendering parameters,
    simulator/held-out/deployment report links, and documentation that
    separates reproduced systems figures from generic scheduling readiness.

- [ ] Track Figure 7 Pallas tiling-problem exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 7 visualizes the
    tiling heuristic problem for a matrix product `A B = C`, with dimensions
    `M`, `N`, and `P`. Section 3.3.2 says the heuristic must choose tile sizes
    while accounting for accelerator optimal shapes, memory capacity, fused
    operations, and compiler intricacies.
  - Current gap: paper-facing Pallas/kernel TODOs require shape-corpus
    provenance, train/evaluation split evidence, real TPU runtime artifacts,
    baseline heuristic identity, tiling-only boundaries, and
    correctness-by-construction scope. They do not map Figure 7 to an exhibit
    record with matrix-shape variable definitions, tile-parameter schema,
    accelerator/memory/fusion/compiler-context annotations, diagram source
    data, visual artifact paths/hashes, rendering parameters, or links to the
    runtime/shape-corpus reports.
    `papers/systems_result_readiness_boundary.json` now machine-records those
    Figure 7 exhibit records, diagram artifacts, and shape-corpus/runtime
    links as missing required evidence.
    `papers/figure7_pallas_tiling_exhibit_boundary.json` now keeps the
    exhibit-specific contract machine-checked.
  - Required result: add Figure 7-style exhibit metadata with a stable exhibit
    ID, kernel benchmark/candidate link, matrix dimension and tile-parameter
    definitions, accelerator and shape-corpus context links, diagram/JSON data
    plus rendered visual artifacts with hashes, rendering parameters, baseline
    heuristic relation, and documentation that separates reproduced Pallas
    figures from executed kernel-runtime evidence.

- [ ] Record kernel-tiling shape-corpus evidence for Gemini/Pallas results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.2 says
    AlphaEvolve optimized Pallas matrix-multiplication tiling heuristics by
    minimizing actual runtime on real TPU accelerators. It collected realistic
    input shapes from kernel users, split them into training and evaluation
    halves, compared against an expert-designed heuristic, and preserved
    correctness by construction by changing tiling strategy rather than the
    underlying mathematical operation.
  - Current gap: current systems report contracts can name a `kernel` domain
    and final held-out gate, but they do not require paper-facing input-shape
    corpus provenance, deterministic train/eval split evidence, real
    accelerator runtime artifacts, baseline heuristic identity, tiling-only
    output constraints, or correctness-by-construction scope.
    `papers/kernel_tiling_shape_corpus_boundary.json` now keeps the generic
    kernel-gates versus Pallas shape-corpus/runtime boundary machine-checked.
  - Required result: add kernel report fields and validation for collected
    input-shape corpora, train/eval split hashes, real accelerator runtime
    measurements, expert-baseline comparison, tiling-parameter constraints,
    unchanged-kernel-math evidence, and deployment/readiness provenance before
    claiming AlphaEvolve-comparable Gemini/Pallas kernel optimization results.

- [ ] Record Pallas autotuning/manual-heuristic baseline workflow evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.2 says
    traditional kernel engineers use search-based autotuning or manually
    crafted heuristics for tiling. Search-based tuning interrupts research
    workflows and must be repeated when input shapes change; manual heuristic
    design is a major bottleneck requiring deep understanding of kernel
    behavior and hardware intricacies. The paper says AlphaEvolve offers a path
    toward automating manual tuning and improving Gemini kernel ergonomics.
  - Current gap: paper-facing Pallas TODOs require input-shape corpus evidence,
    train/eval split hashes, real TPU runtime artifacts, expert-baseline
    comparison, tiling-only correctness, speedup and training-time calibration,
    and production adoption state. They do not require paper/report evidence
    that distinguishes search-based autotuning from manually crafted heuristic
    baselines, records retuning burden for changed shapes, or captures the
    manual-engineering bottleneck and model-developer ergonomics comparison.
    `papers/pallas_workflow_baseline_boundary.json` now keeps the
    workflow-baseline evidence boundary machine-checked.
  - Required result: add paper/report fields for baseline workflow class
    (`search_autotuning`, `manual_heuristic`, or `hybrid_expert`), autotuning
    search-space and retuning policy, manual authoring/review effort, input
    shape-change sensitivity, hardware-expertise assumptions, ergonomics impact,
    and comparison evidence before describing LibreEvolve kernel reports as
    AlphaEvolve-style automation of Pallas tiling-heuristic work.

- [ ] Record Gemini self-training optimization loop evidence for Pallas
      deployment claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.2 states that
    the AlphaEvolve-discovered Pallas tiling heuristic was deployed in
    production, directly enhanced Gemini training efficiency and the Gemini
    team's research and engineering velocity, and was a novel instance where
    Gemini, through AlphaEvolve, optimized its own training process.
  - Current gap: paper-facing Pallas TODOs require runtime speedups, train/eval
    shape evidence, workflow baselines, and production adoption state, while
    a broader Discussion TODO covers generic self-improvement and distillation.
    They do not require a Gemini-specific evidence row tying the evolved kernel
    heuristic to the training workload of the Gemini model family, the
    AlphaEvolve/Gemini relationship, deployment state, before/after training
    metrics, and the self-optimization interpretation.
    `papers/gemini_self_training_loop_boundary.json` now keeps the Pallas
    deployment versus Gemini self-training loop boundary machine-checked.
  - Required result: add paper/report evidence for Gemini self-training loop
    claims: Gemini model/training workload id, AlphaEvolve backend/model-family
    relation, optimized Pallas kernel id, production deployment or rollout
    state, before/after training-time and kernel-runtime measurements,
    engineering-velocity evidence, rollback/safety status, and README/ROADMAP
    wording that distinguishes regular kernel deployment evidence from
    AlphaEvolve-style self-optimization of Gemini's training pipeline.

- [ ] Record RTL/EDA verification evidence for hardware-circuit results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.3 describes
    optimizing Verilog RTL for a TPU arithmetic circuit, reducing power and
    area while preserving functionality. It says the final proposal must pass
    robust verification, was validated by TPU designers, and was also found by
    downstream synthesis tools. It also says the contribution was useful at
    the RTL stage before downstream synthesis, was integrated into an upcoming
    TPU, communicated changes directly in Verilog, fostered trust and simpler
    adoption, and could reduce time to market.
  - Current gap: current systems report contracts do not distinguish generic
    hardware metrics from RTL/EDA evidence. Ready hardware reports now require
    `hardware_rtl_eda_provenance` with HDL language identity, RTL source
    boundary, synthesis or place-and-route tool provenance, PPA metric
    provenance, equivalence/formal verification evidence, timing/power/area
    constraints, designer validation, downstream synthesis confirmation,
    RTL-stage versus synthesis workflow placement, standard-language adoption
    evidence, integration target, time-to-market impact, hashes,
    confirmation flags, and artifact refs.
    `papers/hardware_rtl_eda_evidence_boundary.json` now keeps this as a
    paper-facing metadata-versus-real-artifact boundary.
  - Required result: add real hardware-domain paper/report artifacts for
    Verilog/RTL source, synthesis/PPA outputs, functional equivalence or
    formal verification logs, timing/power/area constraints, designer or
    independent review signoff, synthesis-tool confirmation, RTL-flow
    contribution timing, hardware-engineer trust/adoption rationale,
    integration target, and deployment/time-to-market evidence before making
    AlphaEvolve-comparable TPU-circuit optimization claims beyond metadata.

- [ ] Record TPU arithmetic-circuit rewrite artifact evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.3 says
    AlphaEvolve optimized an already highly optimized Verilog implementation of
    a key TPU arithmetic circuit within the matrix multiplication unit, and
    found a simple code rewrite that removed unnecessary bits while reducing
    area and power.
  - Current gap: paper-facing hardware TODOs require RTL source boundaries,
    synthesis/PPA provenance, equivalence/formal verification, TPU-designer
    signoff, downstream synthesis confirmation, adoption/integration evidence,
    and now `hardware_rewrite_provenance`. Ready hardware reports preserve the
    concrete rewrite artifact metadata behind the claim: before/after Verilog
    hashes, rewrite diff hash, changed spans, eliminated bit or signal
    identities, arithmetic-circuit component context, matrix-multiplication-
    unit context, semantic rewrite category, and links from removed bits to PPA
    and verification records.
    `papers/hardware_rewrite_artifact_boundary.json` now keeps this as a
    paper-facing rewrite-metadata versus concrete-artifact boundary.
  - Required result: add real paper/report artifacts for the TPU arithmetic-
    circuit rewrite: source and modified Verilog files, exact diff or AST span
    records, removed-bit inventory, component and matrix-unit identifiers,
    rewrite-category labels, and linkage from eliminated bits to functional
    verification and PPA outputs.

- [ ] Record Gemini-to-TPU self-contribution evidence for hardware results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.3 says the
    hardware improvement was integrated into an upcoming TPU and represents
    "Gemini's first direct contribution to TPU arithmetic circuits", achieved
    via AlphaEvolve.
  - Current gap: paper-facing hardware TODOs track RTL/EDA verification,
    designer and synthesis-tool signoff, upcoming-TPU integration, Verilog
    adoption, concrete bit-removal artifacts, and now
    `hardware_contribution_provenance`. Ready hardware reports separately
    preserve attribution evidence for the Gemini-to-TPU contribution claim:
    which Gemini/AlphaEvolve model-family produced the edit, which TPU
    arithmetic circuit and TPU generation received it, why it qualifies as a
    first direct contribution, integration milestone, review scope, and how it
    differs from the downstream synthesis-tool rediscovery note.
    `papers/hardware_contribution_attribution_boundary.json` now keeps this
    as a paper-facing attribution-metadata versus artifact boundary.
  - Required result: add real paper/report artifacts for Gemini hardware
    self-contribution claims: model-family/backend records, TPU and
    arithmetic-circuit identifiers, integration milestone records,
    novelty/firstness review evidence, hardware review/signoff files,
    synthesis-tool rediscovery audit artifacts, and README/ROADMAP wording that
    separates RTL optimization evidence from the broader claim that Gemini
    directly contributed to TPU arithmetic circuits through AlphaEvolve.

- [ ] Record per-edit reference checks for compiler-generated IR results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.4 says
    AlphaEvolve optimized XLA-generated IR for FlashAttention and surrounding
    pre/postprocessing code; the IR was designed for debugging rather than
    direct developer editing, was compiler-generated and already highly
    optimized, every modification was checked against the reference unmodified
    code on randomized inputs, and the final code was confirmed by human
    experts for all possible inputs.
  - Current gap: systems result contracts now require ready compiler reports to
    include `compiler_ir_provenance` with per-edit randomized reference-check
    records, randomized input generator provenance, reference implementation
    identity, IR-origin/debug-only versus direct-edit boundary metadata,
    compiler-generated/already-optimized baseline provenance, numerical
    tolerance policy, kernel/pre/postprocessing attribution, and final expert
    confirmation scope. They still do not emit real compiler edit artifacts,
    randomized input coverage records, reference-check outputs, or expert
    all-input confirmation files.
    `papers/compiler_ir_reference_check_boundary.json` now keeps this as a
    paper-facing compiler-IR metadata versus reference-check artifact boundary.
  - Required result: connect compiler/kernel fixtures to real edit-by-edit
    randomized reference checks, reference-code hashes, input-generator seeds
    and coverage, tolerance/failure-policy outputs, abstraction-level
    attribution artifacts, and final expert/all-input confirmation before
    claiming AlphaEvolve-comparable compiler-generated IR evidence.

- [ ] Record FlashAttention compiler-stack context evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.4 explains that
    Transformer attention is implemented using FlashAttention; FlashAttention
    is an accelerator kernel in Pallas; higher-level JAX code handles input
    preparation and output postprocessing; XLA translates the implementation
    through multiple IR stages for particular hardware; and AlphaEvolve
    optimizes memory access orchestration or computation scheduling for a
    high-impact inference configuration on GPUs.
  - Current gap: paper-facing compiler TODOs require per-edit randomized
    reference checks, IR-origin/editability metadata, expert signoff, and
    kernel-versus-pre/postprocessing speedup attribution. Paper-facing TODOs
    and validators now require `compiler_stack_provenance` with
    workload/model configuration, FlashAttention/Pallas kernel identity, JAX
    pre/postprocessing boundaries, XLA lowering stage, hardware target,
    lowered-IR hash, optimization decision category, and artifact refs.
    `papers/compiler_stack_context_boundary.json` now keeps this as a
    paper-facing stack-metadata versus artifact boundary.
  - Required result: add real paper/report artifacts for FlashAttention
    compiler stack context: Transformer/model or inference configuration
    records, FlashAttention/Pallas kernel source files, JAX pre/postprocessing
    wrapper artifacts, XLA IR-stage and hardware-target records, lowered-IR
    artifacts, and memory-orchestration versus scheduling decision evidence
    that remains separate from per-edit reference checks and final
    runtime-speedup claims.

- [ ] Record compiler-adoption path evidence for discovered optimizations.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.4 says future
    compiler use could involve incorporating discovered optimizations into
    existing compilers for specific use cases, or, longer term, incorporating
    AlphaEvolve into the compiler workflow itself.
  - Current gap: paper-facing compiler TODOs require per-edit reference checks,
    IR provenance, expert signoff, FlashAttention stack context, adoption-path
    metadata, and speedup attribution. Ready compiler reports now distinguish
    the paper's two adoption paths: a discovered optimization transferred into
    a conventional compiler/pass for a bounded use case versus AlphaEvolve
    becoming part of the compiler workflow. The report records target
    compiler/pass/version, use-case boundary, optimization artifact hash,
    integration owner, reviewer signoff, rollout/revert state, workflow handoff,
    and artifact refs.
    `papers/compiler_adoption_path_boundary.json` now keeps this as a
    paper-facing adoption-metadata versus integration-artifact boundary.
  - Required result: add real paper/report artifacts for compiler adoption
    paths: compiler patch or pass artifacts, workload/use-case integration
    records, integration-review files, deployment or rollback logs, and
    workflow-handoff evidence that separates concrete compiler optimization
    adoption from longer-term AlphaEvolve workflow integration.

- [ ] Keep named AlphaEvolve application-context rows background-only until
  benchmark fixtures exist.
  - Paper evidence: the local paper index includes AlphaEvolve application
    context rows for compiler optimization, computer architecture, multi-agent
    learning, complexity-theory/graph certification, mechanism design, and
    workflow optimization.
  - Current evidence: `papers/README.md` marks Magellan, ArchAgent,
    Multiagent Learning, Hardness of Approximation, Bilateral Trade, and
    Fault2Flow as background-only, with no compiler-heuristic runner,
    architecture-design simulator, CFR/PSRO/game-theoretic evaluator,
    graph/certification benchmark, bilateral-trade distribution benchmark, or
    fault-to-workflow/human-in-the-loop multi-agent benchmark. The roadmap
    requires each local domain paper to either gain a benchmark, link to an
    existing benchmark, or remain background-only, and the systems report
    contracts only validate declared reports once real fixtures emit them.
  - Current gap: the named rows are honest inventory boundaries, not
    AlphaEvolve-style application coverage. There are no runnable fixtures,
    evaluator protocols, target baselines, held-out/reference gates, artifact
    emission workflows, or report instances for those application domains.
  - Required result: either implement and validate concrete fixtures for each
    named application-context row, linking them to benchmark-hardening,
    systems-result, certification, and artifact-inventory reports as
    appropriate, or keep the rows explicitly background-only in
    `papers/README.md` and avoid promoting them in README/ROADMAP claims.

## Paper-Inspired Feature Claims Needing Correction

- [ ] Keep framework and plugin inspiration rows scoped to partial or
  background status.
  - Paper evidence: the local paper index includes GigaEvo, CodeEvolve,
    ThetaEvolve, ImprovEvolve, MadEvolve, CausalEvolve, and DeepEvolve as
    framework/plugin inspiration rows adjacent to the AlphaEvolve target.
  - Current evidence: `papers/README.md` says GigaEvo lacks Redis lifecycle
    database, asyncio DAG engine, insight stage, and concurrent units;
    CodeEvolve lacks crossover, targeted refinement, modular orchestration,
    and context-aware recombination; ThetaEvolve has clipped-reward export but
    no online RL/GRPO training loop, checkpointing, resume, or lazy-penalty
    dynamics; ImprovEvolve has static prompt guidance with false
    execution/enforcement flags; MadEvolve is background only; CausalEvolve is
    fixed token-pattern guidance rather than LLM-discovered causal variables;
    and DeepEvolve remains bounded retrieval context rather than a full
    cross-file debugging loop.
  - Current gap: these rows are honest implementation-status boundaries, not
    completed paper reproductions. The missing systems are paper-specific
    orchestration, training, interface execution, causal reasoning,
    recombination/refinement, domain-evolution reporting, and debug-loop
    behavior.
  - Required result: either implement the paper-specific behavior with
    matching tests/artifacts/metadata for each row, or keep `papers/README.md`,
    README, ROADMAP, and code TODO wording explicit that the current features
    are inspiration-only, approximation, or background-only references.

- [ ] Add whole-run source/workspace integrity reports for run inspection.
  - Paper evidence: AlphaEvolve-scale runs need auditable generated program
    databases, not only a selected best-program display.
  - Current evidence: `libreevolve show` now streams current and legacy
    `history.jsonl` rows and validates source/workspace payload shape for every
    row before printing a best-looking candidate: legacy `code` must be text,
    workspace `files` must map safe candidate paths to text, and `primary_file`
    must be a safe path present in `files`. Completed manifests now include
    `runtime.history.whole_run_source_workspace_integrity_report`, which
    summarizes retained-program workspace hashes, source-payload shape,
    primary-file coherence, static-file references, startup provenance
    presence, and selected runtime artifact hashes.
    `papers/whole_run_source_workspace_integrity_boundary.json` now preserves
    the same bounded retained-program integrity absence boundary for
    paper-manifest validation.
  - Required result: add durable query/report surfaces over every candidate's
    source payloads, workspace paths, source hashes, primary-file coherence,
    and display/truncation policy. The remaining gap is not malformed
    unselected source-payload validation, selected-row workspace display, or
    bounded retained-program integrity-report evidence.

- [ ] Make DeepEvolve-inspired live retrieval transport audit-grade.
  - Paper evidence: retrieval-driven debugging/refinement treats external
    knowledge as part of the experimental input; the paper-aligned record
    should identify and protect the actual source content used.
  - Current evidence: the local DeepResearch default now uses HTTPS and records
    bounded transport status plus provider payload byte/hash metadata.
    Cache-backed runs can write replay snapshots under
    `plugin_artifacts/deep_research/`, and plugin artifact metadata now
    summarizes those snapshot files with counts, sizes, per-file hashes,
    retention/skipped counters, and an aggregate hash. Candidate/run metadata
    now records retained source rank, provider rank, source identity/content
    hashes, redacted URL transport expectations, and an aggregate selected
    source hash linked to the prompt-visible synthesis. Retained source rows
    with summary/content text now include bounded/redacted
    `libreevolve.retrieval_source_content_snapshot.v1` snapshots with raw and
    stored hashes. Retained source rows also include
    `query_term_overlap_audit_v1` relevance scores derived from deterministic
    query term/source text overlap. Provider order remains the default
    retained-source order, while opt-in
    `source_ranking_policy="query_overlap_score_desc_v1"` reorders retained
    sources by query-overlap score with provider rank as a tie-breaker. Events,
    active prompt context, and cache snapshots record the policy, ranking hash,
    score hash, and whether relevance affected ordering. Active prompt-visible
    DeepResearch context now records
    `libreevolve.deep_research_active_context.v1` metadata with the exact event
    index, synthesis/raw-result hashes, query hash, cache fields,
    retained-source ranking hash fields, and transport-policy status. It still
    lacks unbounded raw provider/source payload persistence, unbounded
    source-content artifacts, and learned or externally scored ranked-source
    scoring/selection rationale beyond deterministic query-overlap ranking.
    Retrieval events and cache snapshots now retain bounded/redacted
    provider-result snapshots with raw and stored hashes. When a cache directory
    is configured and retention allows text, live retrieval also writes
    `libreevolve.retrieval_payload_artifact.v1` sidecars for full
    secret-redacted provider payloads and retained source-content payloads that
    fit a 64,000-byte per-artifact budget; oversized payloads become
    metadata-only omitted artifacts, and plugin artifact metadata reports
    provider-result snapshot and payload-artifact counts and hashes.
    `libreevolve.retrieval_payload_artifact_inventory.v1` now verifies event
    or plugin-metadata sidecar references against an artifact root, including
    safe relative paths, file existence, SHA-256 hashes, byte counts, artifact
    schema, selected sidecar metadata, aggregate missing/mismatch/invalid
    counts, and a stable records hash.
    `libreevolve.retrieval_source_ranking_provenance.v1` now verifies event,
    metadata, or cache-snapshot retained-source ranking records by recomputing
    selected-source and query-relevance hashes, checking retained-rank
    sequence and source counts, and comparing synthesis hashes when retained
    synthesis text is available. Retained sources and event metadata now
    include `libreevolve.retrieval_source_content_trust_policy.v1`, which
    classifies redacted sidecar, metadata-only oversized sidecar, bounded
    snapshot, hash-only, and missing content evidence, plus replayable-evidence
    counts and record hashes. Query events now also include
    `libreevolve.retrieval_evidence_boundary_policy.v1`, which explicitly
    records that raw provider/source payloads, TLS certificate chains, and
    semantic verification are outside the current retained-evidence boundary,
    while linking the retained payload, source-content, and transport evidence
    states.
    `libreevolve.retrieval_transport_policy.v1` now classifies HTTPS request
    state, redirects, HTTP status class, payload hash presence, oversized
    responses, missing custom-provider transport, and TLS/certificate-looking
    failures as audit-grade, degraded, or unauditable, but it is still a
    bounded event policy rather than a replayable transport decision tree.
    Retained source rows now include
    `libreevolve.retrieval_source_grounding_policy.v1` lexical grounding
    records, and event/cache snapshots include an aggregate
    `source_grounding_policy` with source counts, lexically grounded source
    counts, and a records hash. Active prompt context links to the same
    grounding aggregate. This is deterministic lexical provenance, not semantic
    source verification. Query events now also include
    `libreevolve.retrieval_context_audit_policy.v1`, which ties the exact
    prompt-visible retrieval context to the retained transport,
    source-content, evidence-boundary, and grounding states and classifies it
    as audit-grade bounded replay evidence, audit-grade bounded snapshot
    evidence, degraded evidence, or unauditable evidence while still marking it
    as untrusted, non-authoritative prompt context. Focused tests cover default
    arXiv bounded-snapshot evidence, unauditable custom string retrieval, and a
    custom HTTPS provider with replayable redacted source payload artifacts.
    `libreevolve.retrieval_semantic_boundary_audit.v1` now verifies event,
    plugin-metadata, or cache-snapshot records preserve the current bounded,
    non-semantic evidence boundary and reports overclaims of semantic
    verification, full replay readiness, raw provider/source payload retention,
    TLS certificate-chain retention, authoritative prompt context, and semantic,
    learned, or external source-ranking evidence.
    `runtime.retrieval.evidence_coverage` now records
    `libreevolve.retrieval_evidence_coverage.v1` run-level coverage counts for
    retained retrieval evidence surfaces and
    `libreevolve.retrieval_evidence_coverage_validation.v1` rejects raw
    provider/source payload, semantic-verification, semantic-source-ranking,
    learned-ranking, external-source-scoring, TLS-replay, and full-replay
    overclaims.
    Retrieval query inputs now include bounded task-description,
    explicit-context, recent failure-history, local paper manifest title/id, and
    recent proposal-hypothesis terms as well as best-program fitness, metrics,
    and code/file terms. The remaining replay gap is DeepResearch-specific
    provider-output/transport replay integrated with resumed runtime state, not
    the current core full-runtime restore bundle for compatible RNG,
    scheduler, archive, and budget surfaces.
  - Required result: persist unbounded raw provider payload snapshots or a
    stronger raw-evidence preservation model, define
    learned or externally scored ranked-source scoring/selection checks beyond
    deterministic query-overlap ranking, semantic source-content verification
    beyond lexical grounding, and
    replayable redirect/TLS decision evidence before
    claiming DeepEvolve-style retrieval is reproducible and audit-grade. The
    remaining paper gap is not retrieval payload sidecar inventory
    verification, deterministic retained-source ranking-provenance
    validation, semantic-boundary/source-ranking overclaim auditing, run-level
    retrieval evidence coverage validation, or the core full-runtime restore
    bundle that deliberately excludes provider-output replay.

- [ ] Reproduce official 2026 AlphaEvolve impact claims beyond the separate
      source surface.
  - Paper/source evidence: Google DeepMind published
    `AlphaEvolve: How our Gemini-powered coding agent is scaling impact across
    fields` on May 7, 2026. The article describes AlphaEvolve impact after the
    original 2025 launch and names domains and claims not covered by the
    original white paper alone: DeepConsensus error reduction, AC Optimal Power
    Flow feasibility improvement, Earth AI accuracy gain, Willow
    quantum-circuit optimization, public gallery examples, next-generation TPU
    design, cache replacement policies, Spanner write amplification, compiler
    storage footprint, Google Cloud/customer deployments, and UI/API scaling
    contributors. It also makes an operational-lifecycle claim: AlphaEvolve has
    moved from pilot testing to a core infrastructure component, is a regular
    tool for next-generation TPU design, and is being brought to commercial
    enterprises through Google Cloud.
  - Current gap: `papers/alphaevolve_2026_impact_boundary.json` now preserves
    this 2026 official impact article as a source surface, claim registry,
    outbound-link subset, customer/deployment boundary, UI/API attribution
    record, missing-evidence list, and paper-manifest-required sidecar. It now
    also records the Google Cloud private-preview launch post, the AlphaEvolve
    Service API Early Access Program surface, the Gemini Enterprise
    Co-Scientist/AlphaEvolve Pre-GA restricted-access docs, and the Google
    Keyword one-year update as product/source surfaces rather than local
    LibreEvolve evidence. It does not provide linked source snapshots, runnable
    fixtures, reproduced benchmark rows, customer verification, service-access
    artifacts, or independent checks for the named claims.
  - Required result: add evidence beyond the source boundary: linked
    paper/repository/customer snapshots, public-gallery inventories, local
    DeepConsensus/AC OPF/Earth AI/Willow/TPU/cache/Spanner/compiler/customer
    fixtures, benchmark reports, claim-value normalization, and independent
    verification outputs before the impact claims are treated as reproduced
    benchmark evidence or LibreEvolve feature support. Add lifecycle/adoption
    proof for the article's operational claims, including pilot-to-core status,
    regular-tool usage, Google Cloud/commercial scope, UI/API artifact
    inventory, rollout/owner evidence, and release-note claim gates. Add
    product-boundary evidence for Google Cloud AlphaEvolve and Gemini
    Enterprise before making service claims: launch/source snapshots, Pre-GA
    terms status, private-preview or Early Access eligibility, account-team
    access boundaries, unavailable detailed-product-documentation notes,
    console/API/billing artifacts, customer availability, and managed-agent
    workflow semantics.

- [ ] Reproduce Google Cloud AlphaEvolve private-preview and Service API
      access evidence beyond the generic 2026 impact boundary.
  - Paper/source evidence: the Google Cloud blog post `AlphaEvolve on Google
    Cloud`, linked from the May 7, 2026 DeepMind impact article, says
    AlphaEvolve is being released to Google Cloud in private preview and that
    the AlphaEvolve Service API is available through an Early Access Program.
    The post directs interested users with suitable optimization problems to
    contact their Google Cloud representative. The linked Gemini Enterprise
    documentation, `Accelerate R&D with Co-Scientist and AlphaEvolve agents`,
    marks the Co-Scientist and AlphaEvolve agent feature as preview/Pre-GA,
    says access is restricted, and states that account teams provide detailed
    product documentation after access is granted.
  - Current gap: `papers/alphaevolve_cloud_access_boundary.json` now records
    the Google Cloud private-preview post, AlphaEvolve Service API Early Access
    surface, Gemini Enterprise Pre-GA docs, restricted account-team access,
    account-team documentation boundary, and Google Keyword customer-impact
    context with source byte counts and SHA-256 hashes. Service API endpoint/
    schema inventory, auth model, Early Access eligibility evidence, private-
    preview terms record, account-team access handoff artifact, console/API/
    billing screenshot inventory, customer availability matrix, managed-agent
    execution transcript/workflow semantics, security/data-use terms, external
    account availability check, and a local Cloud AlphaEvolve provider adapter
    remain missing for the product/access claims.
  - Required result: add product-surface evidence before any README, ROADMAP,
    paper index, or release-note wording treats Cloud AlphaEvolve as locally
    usable or implemented: Cloud blog URL/date/authors, DeepMind impact
    linkage, Gemini Enterprise docs URL/last-updated date, retrieval hashes,
    launch/private-preview status, Service API access model, endpoint/schema
    documentation status, Early Access eligibility path, Google Cloud
    representative/account-team requirement, Pre-GA terms and support boundary,
    detailed-product-documentation availability after access, console/API/
    billing artifact status, customer/source availability snapshots, managed
    Co-Scientist versus AlphaEvolve workflow semantics, integration/security/
    data-use boundaries, unavailable-artifact notes, independent external
    availability assessment, and code TODOs for any future provider or managed
    service adapter before LibreEvolve claims Google Cloud AlphaEvolve,
    AlphaEvolve Service API, or Gemini Enterprise AlphaEvolve support.

- [ ] Reproduce Google Keyword one-year AlphaEvolve customer-availability
      evidence beyond the generic 2026 impact boundary.
  - Paper/source evidence: the Google Keyword article `AlphaEvolve, 1 year
    later: Impact on science, technology`, linked from
    `papers/alphaevolve_2026_impact_boundary.json` as
    `google_keyword_alphaevolve_one_year_update`, says AlphaEvolve has gone
    from research to solving real-life problems. It reports that AlphaEvolve
    helped improve DNA sequencing error correction, increase disaster-
    prediction accuracy, demonstrate potential grid-stabilization simulations,
    accelerate molecular simulations, unlock neuroscience insights, improve
    Google infrastructure, and help Google Cloud customers improve ML models,
    accelerate drug discovery, improve supply chains, and optimize warehouse
    design. The article is attributed to Pushmeet Kohli, Chief Scientist,
    Google Cloud and Vice President, Google DeepMind, and Amin Vahdat, SVP and
    Chief Technologist, Google Cloud.
  - Current gap: `papers/alphaevolve_keyword_customer_boundary.json` now
    records the Keyword article URL/authors, retrieval byte count and SHA-256
    hash, relation to the DeepMind impact article and Cloud private-preview
    post, ten source-reported science/infrastructure/customer domain claims,
    Google infrastructure versus customer-impact separation, and four
    source-reported Google Cloud customer-impact rows for ML models, drug
    discovery, supply chains, and warehouse design. Customer-availability
    matrix, customer/source crosswalk, named customer links, Cloud account
    access evidence, UI/API/console/billing artifact inventory, availability
    geography/access-tier notes, rollout/owner metadata, claim-value
    normalization, independent availability assessment, local customer-case
    fixtures, and local managed-service support remain missing for the Keyword
    update.
  - Required result: add source-specific evidence for the Keyword update:
    article URL/date/authors, retrieval hash, relation to the DeepMind impact
    article and Cloud private-preview post, customer and domain claim table,
    customer-source links or explicit absence records, ML-model/drug-
    discovery/supply-chain/warehouse-design availability rows, Google
    infrastructure claim separation, UI/API/product artifact inventory,
    account-access and billing/console status, rollout/owner metadata,
    availability geography or access-tier notes, claim-value normalization,
    independent external availability assessment, README/ROADMAP/paper-index
    wording that keeps the article as source-reported Google/Google Cloud
    customer impact evidence only, and code TODOs for any future managed
    service or customer-case fixture before LibreEvolve claims comparable
    Google Cloud customer availability or product support.

- [ ] Reproduce AlphaEvolve UI/API attribution and artifact-inventory evidence
      beyond the generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, includes an acknowledgements section that separates
    the original AlphaEvolve development team, later impact-scaling
    contributors, AlphaEvolve UI collaborators, AlphaEvolve API and Google
    Cloud customer-engagement collaborators, application collaborators, and
    partner teams across Google DeepMind, Google Cloud, Google Labs, Google
    Research, and other product areas. The article specifically says Adam
    Connors, Alex Bäuerle, Anna Trostanetski, Fernanda Viegas, Gabi Cardoso,
    Jonathan Caton, Lucas Dixon, Mariana Felix, Martin Wattenberg, Matin
    Akhlaghinia, Richard Green, Yosuke Ushigome, and Yunhan Xu collaborated on
    the UI, and separately names Anant Nawalgaria, Diego Ballesteros, Gemma
    Jennings, Jakob Oesinghaus, Kartik Sanu, Laurynas Tamulevičius, Nicolas
    Stroppa, Nishta Dhawan, Oliver Hilsenbeck, Puneet Jagralapudi, Reah
    Miyara, Skander Hannachi, Tom Beyer, and Vishal Agarwal as API and Google
    Cloud customer collaborators.
  - Current gap: `papers/alphaevolve_ui_api_attribution_boundary.json` now
    records the impact article URL/date/team, retrieval byte count and SHA-256
    hash, role-category definitions, the 13-person AlphaEvolve UI collaborator
    roster, the 14-person API and Google Cloud customer-engagement
    collaborator roster, and artifact-policy boundaries. UI screenshot/source
    snapshot, interaction-flow inventory, API endpoint/schema inventory, Cloud
    customer-engagement artifact, role-to-artifact link table, public/private
    artifact access status, privacy/contact redaction policy, independent
    artifact verification, local UI support, managed API support, and local
    customer-engagement adapter evidence remain missing for the article's
    UI/API claims.
  - Required result: add source-specific evidence for the UI/API attribution
    claims: impact article URL/date/authors, retrieval hash, UI collaborator
    roster, API/Cloud-customer collaborator roster, role-category definitions,
    artifact availability policy, UI screenshot or source-snapshot inventory,
    public/private artifact access status, API endpoint/schema documentation
    status, Cloud customer-engagement evidence status, role-to-artifact links,
    privacy/contact-redaction policy, product-team attribution separation from
    local LibreEvolve authorship, README/ROADMAP/paper-index wording that keeps
    UI/API claims source-reported only, and code TODOs for any future local UI,
    managed API, or customer-engagement adapter before LibreEvolve claims
    comparable AlphaEvolve UI/API support.

- [ ] Reproduce DeepMind AlphaEvolve product-page evidence beyond the generic
      2026 impact boundary.
  - Paper/source evidence: `papers/alphaevolve_2026_impact_boundary.json`
    records `https://deepmind.google/science/alphaevolve/` as
    `alphaevolve_product_page` with category `product_context` and status
    `outbound_reference_only`. Current Google DeepMind science-page search
    snippets position AlphaEvolve as a coding agent built with Gemini for
    designing advanced algorithms for math and practical computing
    applications by combining large language model creativity with automated
    evaluators. The same DeepMind site navigation surfaces AlphaEvolve under
    Science alongside AlphaFold, AlphaGenome, WeatherNext, and AlphaEarth.
  - Current gap: the boundary records the product page only as an outbound
    reference. No dedicated TODO, product-page HTML snapshot, page hash,
    title/subtitle/source-card inventory, navigation placement record,
    source-update timestamp, product-versus-white-paper claim separation,
    relation to the 2025 announcement and 2026 impact article, access/status
    statement, public artifact links, image/video asset inventory, or
    independent availability check exists for the DeepMind product-page
    evidence.
  - Required result: add source-specific evidence for the product page:
    canonical URL, retrieval date, page title/subtitle, HTML byte count and
    hash, DeepMind science-navigation placement, all outbound links and media
    assets, wording that describes AlphaEvolve as Gemini-built algorithm
    design context, explicit distinction between product/science page,
    original white paper, announcement blog, 2026 impact article, Google Cloud
    private preview, and local LibreEvolve support, access/product availability
    notes, README/ROADMAP/paper-index wording that keeps this page as
    source-reported product context only, and code TODOs for any future product
    page snapshot verifier or managed AlphaEvolve compatibility claim before
    LibreEvolve treats the DeepMind product page as implementation evidence.

- [ ] Add AlphaEvolve 2026 impact claim-value normalization and release-note
      promotion gates.
  - Paper/source evidence: `papers/alphaevolve_2026_impact_boundary.json`
    records heterogeneous official 2026 impact claims from the DeepMind impact
    article, Google Cloud/private-preview sources, Google Keyword update,
    customer cases, linked scientific papers, public gallery links, and
    product/context pages. The claim registry mixes percentages, speedups,
    qualitative descriptions, deployment/access statements, customer-reported
    business outcomes, and source-only outbound links. The same boundary lists
    `claim_value_normalization_policy` as not recorded and
    `release_note_claim_gate` as not implemented.
  - Current gap: existing README, ROADMAP, paper-index, and TODO wording keeps
    the claims source-scoped, but there is no dedicated normalization policy
    explaining how to compare or promote values such as `30%` error reduction,
    `14% to over 88%` feasibility, `5%` accuracy gain, `10x` lower error,
    `20%` write-amplification reduction, `nearly 9%` storage-footprint
    reduction, `2x` training speed, `10.4%` routing efficiency, `4x` MLFF
    speedup, `two days vs months`, public-gallery qualitative claims, private-
    preview access claims, or customer-availability claims. There is also no
    release-note gate requiring source snapshot, local fixture status,
    independent verification, customer confirmation, and overclaim checks
    before any impact value is described as implemented, reproduced, or
    LibreEvolve-supported.
  - Required result: add a machine-checkable claim-normalization and promotion
    policy for the 2026 impact source set: canonical claim ids, source URL and
    retrieval hash, value type, unit, denominator, baseline identity,
    comparison direction, uncertainty/approximation wording, customer-reported
    versus measured result class, local fixture availability, reproduction
    artifact links, independent verification status, release-note eligibility,
    README/ROADMAP/paper-index wording constraints, required downgrade wording
    when evidence is missing, and tests that fail if a source-reported impact
    claim is promoted without source snapshots, normalized value rows,
    benchmark or customer evidence, and explicit unsupported-local-evidence
    flags.

- [ ] Add AlphaEvolve 2026 impact linked-source independent-verification and
      local-benchmark report matrix.
  - Paper/source evidence: `papers/alphaevolve_2026_impact_boundary.json`
    records `linked_source_independent_verification` as not recorded locally
    and `local_benchmark_reports` as not implemented locally. The same
    boundary requires `local_fixture_status`, `local_benchmark_report_status`,
    `unsupported_local_benchmark_flags`, and `independent_verification_status`
    for the official 2026 impact source set covering DeepConsensus, AC OPF,
    Earth AI, Willow, public gallery/math, TPU design, cache policies, Spanner,
    compiler storage, customer cases, product surfaces, UI/API surfaces, and
    linked scientific sources.
  - Current gap: individual TODO blocks mention independent reproduction or
    benchmark gaps for many sources, but no aggregate matrix proves each
    impact claim has a source snapshot, artifact/source availability status,
    fixture status, local benchmark-report status, external verification
    attempt, failure reason, unsupported-local-benchmark flag, and docs
    downgrade wording. Without that matrix, green paper-manifest tests can
    prove the boundary file exists but cannot prove every linked impact source
    has a current independent-verification row or a machine-checkable local
    benchmark absence row.
  - Required result: add a versioned impact-verification matrix and validator:
    one row per 2026 impact claim and outbound source, canonical claim id,
    source URL, retrieval hash, source artifact status, fixture/report path,
    local benchmark implemented/not-implemented status, benchmark report hash
    when present, independent verifier identity or external-check method,
    verification date, verification outcome, blocker/failure reason, customer
    confirmation status where relevant, unsupported-local-benchmark flag,
    release-note eligibility, README/ROADMAP/paper-index downgrade wording,
    and tests that fail when a claim has no verification/report row or when a
    missing local benchmark is described as reproduced.

- [ ] Reproduce DeepConsensus/PacBio AlphaEvolve genomics evidence beyond the
      generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, says AlphaEvolve improved DeepConsensus, a Google
    Research model for correcting DNA sequencing errors, with a 30% reduction
    in variant detection errors and PacBio downstream benefit. PacBio's
    `Improving HiFi sequencing accuracy with Google DeepConsensus and
    AlphaEvolve` source separately describes DeepConsensus as a transformer
    model that combines raw base calls with a draft HMM consensus, notes the
    original DeepConsensus reduced HiFi read errors by about 42%, reports
    Revio throughput changes from about 12 Gb/hour at launch to about
    16 Gb/hour after engineering work and about 18 Gb/hour in the upcoming
    2026 release, and explains that AlphaEvolve work focused on improving the
    DeepConsensus loss function. The DeepConsensus Nature Biotechnology paper
    and Google repository provide older baseline context, including gap-aware
    sequence transformers, AlignmentLoss, PacBio HiFi data, DeepVariant/
    assembly downstream checks, and non-clinical/non-medical-device caveats.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    DeepConsensus claim only as a generic impact item. No dedicated TODO,
    PacBio article snapshot, DeepConsensus paper/repository snapshot, HiFi
    sequencing fixture, read/alignment data schema, loss-function mutation
    record, variant-calling benchmark contract, DeepVariant/assembly
    downstream evaluation harness, Revio hardware/runtime provenance,
    throughput-vs-accuracy separation note, clinical-use boundary, PacBio
    verification artifact, or independent reproduction output exists for the
    AlphaEvolve DeepConsensus evidence.
  - Required result: add reproduction-grade evidence for the DeepConsensus
    source set: DeepMind impact URL/date/authors, PacBio article URL/date/
    authors, DeepConsensus paper DOI, repository snapshot/license/non-product
    disclaimer, retrieval hashes, source license/terms status, PacBio and
    Google collaborator identities, model/version and Revio release identity,
    AlphaEvolve access status, HiFi read/input data boundaries, draft HMM
    consensus and raw-base-call schemas, seed loss/evaluator definitions,
    AlignmentLoss or evolved-loss provenance, candidate-program archive,
    variant-detection-error metric definition, 30% reduction calculation,
    separation from older 42% read-error and 12/16/18 Gb/hour throughput
    claims, DeepVariant/assembly downstream validation requirements, hardware/
    accelerator/runtime metadata, privacy and clinical-use constraints,
    customer-verification snapshots, independent reproduction feasibility
    assessment, README/ROADMAP/paper-index wording that keeps DeepConsensus
    as source-reported genomics evidence only, and code TODOs for any future
    sequencing-error or variant-calling benchmark fixture before LibreEvolve
    claims comparable genomics support.

- [ ] Reproduce AC-OPF/CANOS AlphaEvolve grid-optimization evidence beyond
      the generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, says AlphaEvolve was applied to the AC Optimal
    Power Flow problem and increased a trained Graph Neural Network model's
    feasible-solution rate from 14% to over 88%, reducing the need for costly
    post-processing in electricity-grid workflows. The linked source is arXiv
    `2403.17660`, `CANOS: A Fast and Scalable Neural AC-OPF Solver Robust To
    N-1 Perturbations`, which presents a Constraint-Augmented Neural OPF
    Solver using GNNs, PGLib-OPF cases, PowerModels.jl plus Ipopt reference
    solutions, 500/2,000/10,000-bus grids, FullTop and TopDrop datasets with
    300k examples each, 90/5/5 train/validation/test splits, N-1 topology
    perturbations, JAX/Haiku/Jraph/Optax training, 8 A100 40GB GPUs, and
    evaluation against AC-IPOPT and DC-IPOPT baselines with speed,
    optimality, solution-accuracy, and feasibility metrics.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    AC-OPF claim only as a generic impact item. No dedicated TODO, CANOS paper
    snapshot, PGLib/PowerModels/Ipopt data pipeline, graph-schema fixture,
    bus/branch/generator/load/shunt feature contract, topology-perturbation
    generator, GNN seed-program identity, constraint-augmented loss mutation
    record, feasibility metric definition, 14%-to-over-88% calculation,
    power-flow post-processing harness, baseline solver provenance,
    accelerator/runtime record, electricity-grid safety boundary, or
    independent reproduction output exists for the AlphaEvolve AC-OPF claim.
  - Required result: add reproduction-grade evidence for the AC-OPF source
    set: DeepMind impact URL/date/authors, arXiv `2403.17660` URL/version/
    authors, retrieval hashes, source license/terms status, relation between
    CANOS and the AlphaEvolve-improved model, dataset identities and access
    status, PGLib/PowerModels.jl/Ipopt/pandapower/JAX dependency provenance,
    graph input/output schemas, FullTop/TopDrop and N-1 perturbation
    generation records, train/validation/test split hashes, seed architecture
    and evolved-code regions, constraint-loss/evaluator definitions,
    feasibility and post-processing metrics, 14%-to-over-88% claim
    normalization, AC-IPOPT/DC-IPOPT baseline rows, GPU/runtime/cost metadata,
    power-grid operational-safety and non-deployment boundary wording,
    independent reproduction feasibility assessment, README/ROADMAP/
    paper-index wording that keeps AC-OPF as source-reported grid evidence
    only, and code TODOs for any future power-grid or constrained-optimization
    benchmark fixture before LibreEvolve claims comparable electricity-grid
    optimization support.

- [ ] Reproduce Earth AI disaster-risk AlphaEvolve evidence beyond the
      generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, says AlphaEvolve helped automate optimization of
    Earth AI models and increased the overall accuracy of predicting natural
    disaster risk by 5% aggregated across 20 categories such as wildfires,
    floods, and tornadoes. The linked paper is arXiv `2510.18318`, `Earth AI:
    Unlocking Geospatial Insights with Foundation Models and Cross-Modal
    Reasoning`, which describes Earth AI as a family of geospatial foundation
    models spanning planet-scale imagery, population, and environment, plus a
    Gemini-powered reasoning engine over foundation models, geospatial data
    sources, and tools. The Google Earth AI product page separately positions
    Earth AI for enterprises, nonprofits, and cities across environmental
    monitoring, disaster response, Google Earth, Google Maps Platform, and
    Google Cloud, with examples covering cyclone prediction, cholera-risk
    queries, mangrove similarity, and partner geospatial workflows.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    Earth AI claim only as a generic impact item. No dedicated TODO, Earth AI
    paper snapshot, product-page snapshot, disaster-category inventory,
    geospatial dataset provenance, imagery/population/environment model
    identity, cross-modal reasoning trace, AlphaEvolve optimization target,
    seed-model or prompt/program mutation record, 5% aggregate-accuracy
    calculation, per-category metric table, disaster-response safety boundary,
    partner/product-access boundary, or independent reproduction output exists
    for the AlphaEvolve Earth AI claim.
  - Required result: add reproduction-grade evidence for the Earth AI source
    set: DeepMind impact URL/date/authors, arXiv `2510.18318` URL/version/
    authors, Google Earth AI product-page URL/date, retrieval hashes, source
    license/terms status, relation between Earth AI foundation models and the
    AlphaEvolve-optimized component, AlphaEvolve access status, 20 disaster
    category names, data-source identities and privacy/licensing boundaries,
    imagery/population/environment model-version records, reasoning-engine
    and tool-call schemas, seed model/program or prompt contract, evaluator
    metric definitions, aggregate and per-category accuracy calculations,
    baseline and ablation rows, geospatial split/leakage controls, cyclone/
    wildfire/flood/tornado/cholera example boundaries, product and partner
    availability notes, humanitarian/disaster-response safety constraints,
    independent reproduction feasibility assessment, README/ROADMAP/
    paper-index wording that keeps Earth AI as source-reported geospatial
    evidence only, and code TODOs for any future geospatial or disaster-risk
    benchmark fixture before LibreEvolve claims comparable Earth-science
    optimization support.

- [ ] Reproduce Willow quantum-circuit AlphaEvolve evidence beyond the
      generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, says AlphaEvolve optimized quantum circuits for
    complex molecular simulations on Google's Willow quantum processor,
    suggesting quantum circuits with 10x lower error than previous
    conventionally optimized baselines. The linked paper is arXiv `2510.19550`,
    `Quantum computation of molecular geometry via many-body nuclear spin
    echoes`. It describes AlphaEvolve runs over Python programs implementing a
    first-order Trotter formula with a swap network for 15 qubits, fixed
    function signatures carrying total time, Trotter steps, couplings, on-site
    terms, butterfly/measurement indices, landscape parameters, and CZ-gate
    caps, prompts covering quantum simulation/Trotterization/NMR/OTOCs plus
    focus prompts for simplification, lightcone, THRIFT, and commutator
    scaling, evaluation by averaging OTOCs over 250 sampled initial states,
    exact OTOC reference checks with sparse GPU unitary computations, root
    mean square OTOC error as the optimization metric, Cirq/KAK CZ-counting
    bottleneck mitigation, multi-run AlphaEvolve re-seeding, and Willow
    hardware execution on selected 9- and 15-qubit sub-grids.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    Willow claim only as a generic impact item. No dedicated TODO, paper
    snapshot, Willow source snapshot, quantum-circuit benchmark fixture,
    Hamiltonian/molecule/problem-instance inventory, seed Trotter/swap-network
    program, AlphaEvolve prompt and focus-prompt record, OTOC reference-data
    artifact, sampled-state determinism contract, CZ-gate cap enforcement,
    Cirq/KAK decomposition provenance, generated-circuit archive,
    10x-error-reduction calculation, Willow calibration/runtime metadata,
    hardware-access boundary, or independent reproduction output exists for
    the AlphaEvolve Willow evidence.
  - Required result: add reproduction-grade evidence for the Willow source
    set: DeepMind impact URL/date/authors, arXiv `2510.19550` URL/version/
    authors, Willow Keyword article URL/date/authors, retrieval hashes, source
    license/terms status, relation between the molecular-geometry paper and
    the impact-article 10x claim, AlphaEvolve and Willow access status,
    molecule identities and Hamiltonian schemas, seed program semantics,
    Trotter/swap-network/CZ-gate-budget definitions, prompt/focus-prompt
    provenance, multi-run re-seeding policy, evaluator metric definitions,
    sampled/exact OTOC reference records, Cirq/KAK and sparse-GPU unitary
    provenance, generated circuit/program archive, hardware sub-grid,
    calibration, gate/readout/coherence metadata, 10x lower-error calculation,
    conventionally optimized baseline identity, quantum-hardware safety and
    non-reproducibility boundary, independent reproduction feasibility
    assessment, README/ROADMAP/paper-index wording that keeps Willow as
    source-reported quantum evidence only, and code TODOs for any future
    quantum-circuit or molecular-simulation benchmark fixture before
    LibreEvolve claims comparable quantum-computing support.

- [ ] Reproduce AlphaEvolve public-gallery/Tammes evidence beyond the generic
      2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, links to an AlphaEvolve public experiment page for
    optimizing an instance of the Tammes problem and to a broader public
    gallery of additional AlphaEvolve-generated potential solutions. The
    current web-visible gallery and experiment routes are JavaScript-rendered
    `alphaevolve-examples.web.app` pages, so source-faithful coverage needs
    rendered-page capture rather than relying on static article text alone.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    public-gallery and Tammes URLs only as source links. No dedicated TODO,
    rendered gallery snapshot, experiment-page snapshot, route inventory,
    gallery item manifest, Tammes problem-instance definition, candidate
    solution artifact, visualization/media artifact, scoring metric, best-
    program provenance, AlphaEvolve run metadata, license/terms boundary,
    screenshot/hash evidence, or independent reproduction output exists for
    the public gallery evidence.
  - Required result: add reproduction-grade evidence for the gallery source:
    DeepMind impact URL/date/authors, public experiment URL, gallery URL,
    rendered-page retrieval method, HTML/screenshot/media hashes, source
    license/terms status, route and item inventory, Tammes problem parameters,
    objective/evaluator definition, candidate program/solution payload,
    visualization artifact identities, selected-program metadata, run/generation
    history if exposed, links to any downloadable code/data, gallery item
    stability/versioning checks, accessibility of the JS-rendered content,
    independent reproduction feasibility assessment, README/ROADMAP/
    paper-index wording that keeps the public gallery as source-reported
    demonstration evidence only, and code TODOs for any future gallery import,
    Tammes benchmark fixture, or rendered-source archiver before LibreEvolve
    claims comparable public AlphaEvolve example coverage.

- [ ] Reproduce TSP lower-bound AlphaEvolve impact evidence beyond the generic
      2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, lists improved lower bounds for the Traveling
    Salesman Problem as one of the public AlphaEvolve mathematics advances.
    The existing theoretical-CS source sidecar records `2509.18057`,
    `Hardness of Approximation`, as AlphaEvolve complexity-theory context,
    including a metric Traveling Salesman Problem application with reported
    TSP hardness factor `111/110`, MAX-k-CUT gadget rows, random-graph/
    Ramanujan graph evidence, proof-element boundaries, and missing verifier
    or graph/gadget artifact gates. That sidecar is background/source
    coverage, not reproduced evidence for the official impact article's
    broad TSP lower-bound claim.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    traveling-salesman claim only as a generic impact item and marks the
    `traveling_salesman_lower_bound_checker` as not implemented locally. No
    dedicated TODO, source snapshot, exact TSP claim mapping, problem-variant
    taxonomy, lower-bound theorem statement, gadget construction payload,
    verifier code, graph/equation artifact hashes, independent checker,
    baseline-prior comparison ledger, proof-lifting metadata, artifact license
    boundary, or independent reproduction output exists for the official
    TSP impact claim.
  - Required result: add reproduction-grade evidence for the TSP source set:
    DeepMind impact URL/date/authors, `2509.18057` arXiv/PDF URL/version/
    authors, retrieval hashes, source license/terms status, relation between
    the impact article's TSP wording and the Hardness-of-Approximation metric-
    TSP row, exact problem variant and theorem identity, baseline lower-bound
    history, gadget/equation schema, graph or construction artifacts, evolved
    verifier/proof code provenance, independent brute-force or formal checker
    outputs, Table 1 LB/UB values where relevant, theorem-lifting assumptions,
    artifact/repository availability, independent reproduction feasibility
    assessment, README/ROADMAP/paper-index wording that keeps TSP as source-
    reported theoretical-CS evidence only, and code TODOs for any future TSP
    lower-bound checker or graph/gadget benchmark fixture before LibreEvolve
    claims comparable TSP or approximation-hardness support.

- [ ] Reproduce neuroscience interpretable-model impact evidence beyond the
      generic 2026 AlphaEvolve boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, lists discovering interpretable models in
    neuroscience as a linked scientific-source impact area. The linked Google
    DeepMind publication page, `Automated Discovery of Interpretable Cognitive
    Programs underlying Reward-guided behavior`, dated February 6, 2025,
    points to a bioRxiv source and describes CogFunSearch: an automated
    LLM-based program discovery tool based on FunSearch, used to discover
    symbolic programs for rodent reward-guided choice behavior. The abstract
    says the discovered programs outperform state-of-the-art cognitive models
    for predicting rat choices in a two-armed drifting-bandit task, while a
    simple unconstrained neural network still outperforms both classic and
    discovered symbolic models.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    neuroscience claim only as a generic impact item and marks the
    `neuroscience_model_fixture` as not implemented locally. No dedicated
    TODO, publication-page snapshot, bioRxiv/PDF snapshot, relation-to-
    AlphaEvolve/CogFunSearch mapping, rodent choice dataset fixture,
    two-armed drifting-bandit task schema, symbolic-program candidate schema,
    state-of-the-art cognitive-model baseline, neural-network baseline,
    prompt-semantics experiment record, prediction metric definition, model
    interpretability rubric, animal-behavior ethics/data boundary, or
    independent reproduction output exists for the neuroscience evidence.
  - Required result: add reproduction-grade evidence for the neuroscience
    source set: DeepMind impact URL/date/authors, DeepMind publication-page
    URL/date/authors, bioRxiv URL/version/authors, retrieval hashes, source
    license/terms status, explicit relation between FunSearch/CogFunSearch and
    AlphaEvolve impact wording, dataset identity and access status, rodent
    reward-guided choice task schema, train/test split records, seed program
    and candidate-program grammar, prompt variants and semantic-information
    ablations, evaluator metric definitions, classic cognitive-model baseline
    rows, unconstrained-neural-network baseline rows, discovered-program
    artifacts, interpretability criteria, statistical significance checks,
    ethics/privacy/data-use boundary, independent reproduction feasibility
    assessment, README/ROADMAP/paper-index wording that keeps the claim as
    source-reported neuroscience evidence only, and code TODOs for any future
    cognitive-model or neuroscience benchmark fixture before LibreEvolve
    claims comparable interpretable-neuroscience modeling support.

- [ ] Reproduce neural-network building-block AlphaEvolve impact evidence
      beyond the generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, lists rapidly advancing neural network building
    blocks as a linked scientific-source impact area. The linked arXiv source
    is `2602.05688`, `Mining Generalizable Activation Functions`, submitted
    February 5, 2026 by Alex Vitvitskyi, Michael Boratko, Matej Grcic, Razvan
    Pascanu, Deep Shah, and Petar Velickovic. Its abstract says activation
    functions affect optimization, expressivity, and implicit inductive bias;
    argues that AlphaEvolve-style frontier-LLM mutation enables a wider search
    space over Python functions within a FLOP budget; and reports small-scale
    synthetic datasets as sufficient for AlphaEvolve to discover meaningful
    activations.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    `neural_network_building_blocks` claim only as a generic linked-source
    item and marks the `neural_network_building_block_fixture` as not
    implemented locally. No dedicated TODO, arXiv/PDF snapshot, activation-
    function search-space schema, FLOP-budget contract, synthetic-dataset
    fixture, out-of-distribution fitness definition, baseline activation rows,
    Python-function safety/validity constraints, inductive-bias measurement,
    training/evaluation split records, model architecture identities,
    reproduced discovered activation artifacts, or independent reproduction
    output exists for the activation-function evidence.
  - Required result: add reproduction-grade evidence for arXiv `2602.05688`:
    DeepMind impact URL/date/authors, arXiv URL/version/authors, PDF retrieval
    hash and license metadata, source relation to the broader AlphaEvolve
    impact wording, activation-function candidate grammar, allowed Python
    operation/FLOP budget, architecture and optimizer definitions, small-scale
    synthetic dataset generator and seeds, OOD evaluation split records,
    fitness metric definitions, baseline activation-function rows, discovered
    activation artifacts, training curves and compute budget, robustness and
    generalization checks, inductive-bias interpretation rubric, code/source
    availability status, README/ROADMAP/paper-index wording that keeps the
    claim as source-reported neural-network-building-block evidence only, and
    code TODOs for any future activation-function or neural-architecture
    benchmark fixture before LibreEvolve claims comparable neural-network
    building-block discovery support.

- [ ] Reproduce frontier-AI safety-mitigation AlphaEvolve impact evidence
      beyond the generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, lists critical safety mitigations for frontier AI
    models as a linked scientific-source impact area. The linked arXiv source
    is `2601.11516`, `Building Production-Ready Probes For Gemini`, submitted
    January 16, 2026 and revised January 19, 2026 by Janos Kramar, Joshua
    Engels, Zheng Wang, Bilal Chughtai, Rohin Shah, Neel Nanda, and Arthur
    Conmy. Its abstract describes activation probes for misuse mitigation,
    production distribution shifts including long-context inputs, multi-turn
    conversations, and adaptive red teaming, successful deployment of misuse
    mitigation probes in user-facing Gemini instances, and early positive
    AlphaEvolve results for automating probe architecture search and adaptive
    red teaming.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    `frontier_ai_safety_mitigations` claim only as a generic linked-source
    item and marks the `safety_mitigation_fixture` as not implemented locally.
    No dedicated TODO, arXiv/PDF snapshot, probe-architecture search schema,
    cyber-offensive-domain evaluation fixture, production distribution-shift
    taxonomy, long-context/multi-turn/adaptive-red-team test set, prompted-
    classifier baseline, probe-compute/accuracy tradeoff record, Gemini
    deployment evidence, AlphaEvolve automated-red-team artifact, safety-review
    boundary, or independent reproduction output exists for this safety
    mitigation evidence.
  - Required result: add reproduction-grade evidence for arXiv `2601.11516`:
    DeepMind impact URL/date/authors, arXiv URL/version/authors, PDF retrieval
    hash and license metadata, source relation to the broader AlphaEvolve
    impact wording, misuse-probe candidate schema, architecture-search
    parameters, cyber-offensive evaluation taxonomy, long-context and
    multi-turn split definitions, adaptive red-team protocol, prompted-
    classifier comparator rows, probe accuracy/latency/cost metrics, training
    distribution diversity records, deployment-status evidence boundaries,
    AlphaEvolve search-run provenance, discovered probe/red-team artifacts,
    safety and dual-use handling policy, privacy/redaction status, independent
    reproduction feasibility assessment, README/ROADMAP/paper-index wording
    that keeps the claim as source-reported frontier-AI-safety evidence only,
    and code TODOs for any future misuse-probe or adaptive-red-team benchmark
    fixture before LibreEvolve claims comparable safety-mitigation support.

- [ ] Reproduce synthetic-persona generation AlphaEvolve impact evidence
      beyond the generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, lists synthetic data generation as a linked
    scientific-source impact area. The linked arXiv source is `2602.03545`,
    `Persona Generators: Generating Diverse Synthetic Personas for Arbitrary
    Contexts`, submitted February 3, 2026 and revised May 25, 2026 by Davide
    Paglieri, Logan Cross, William A. Cunningham, Joel Z. Leibo, and Alexander
    Sasha Vezhnevets. Its abstract says evaluating AI systems that interact
    with humans requires behavior coverage across diverse user populations,
    introduces Persona Generators as functions that produce diverse synthetic
    populations tailored to arbitrary contexts, applies an AlphaEvolve-based
    iterative improvement loop over hundreds of iterations, and reports
    improved six-metric diversity on held-out contexts including rare trait
    combinations.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    `synthetic_data_generation` claim only as a generic linked-source item and
    marks the `synthetic_data_generation_fixture` as not implemented locally.
    No dedicated TODO, arXiv/PDF snapshot, persona-generator candidate schema,
    arbitrary-context prompt schema, diversity-axis definition, six-metric
    evaluation fixture, held-out-context split, baseline generator rows,
    long-tail/rare-trait coverage checker, privacy/consent boundary,
    synthetic-population artifact policy, hundreds-iteration run provenance,
    or independent reproduction output exists for the synthetic-persona
    evidence.
  - Required result: add reproduction-grade evidence for arXiv `2602.03545`:
    DeepMind impact URL/date/authors, arXiv URL/version/authors, PDF retrieval
    hash and license metadata, source relation to the broader AlphaEvolve
    impact wording, persona-generator code grammar, arbitrary-context input
    schema, small-description expansion contract, opinion/preference diversity
    axes, six diversity metric definitions, held-out-context split records,
    rare-trait-combination coverage checks, baseline generator rows,
    AlphaEvolve mutation/run configuration, generated persona artifacts,
    privacy/consent and synthetic-data-use boundaries, evaluation-cost and
    compute records, independent reproduction feasibility assessment,
    README/ROADMAP/paper-index wording that keeps the claim as source-reported
    synthetic-data-generation evidence only, and code TODOs for any future
    synthetic-persona benchmark fixture before LibreEvolve claims comparable
    synthetic data generation support.

- [ ] Reproduce cryptography-for-user-privacy AlphaEvolve impact evidence
      beyond the generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, lists cryptography for user privacy as a linked
    scientific-source impact area. The linked arXiv source is `2605.14718`,
    `Adapting AlphaEvolve to Optimize Fully Homomorphic Encryption on TPUs`,
    submitted May 14, 2026 by Shruthi Gorantala, Jianming Tong, Asra Ali,
    Baiyu Li, Jonathan Katz, Jeremy Kun, Thomas Steinke, Abhradeep Thakurta,
    Julian Walker, and Amir Yazdanbakhsh. Its abstract frames FHE deployment as
    limited by computational overhead, uses AlphaEvolve for hardware-aware
    cryptographic-kernel optimizations, relies on real TPUv5e hardware
    execution plus correctness testing, and reports TFHE/Jaxite and CKKS/CROSS
    speedups of 2.5x, 1.31x, and 1.18x relative to human-engineered
    state-of-the-art baselines.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    `cryptography_user_privacy` claim only as a generic linked-source item and
    marks the `cryptography_privacy_fixture` as not implemented locally. The
    existing FHE-on-TPU TODO covers the paper as application context, but no
    dedicated impact-claim TODO, user-privacy threat model, FHE scheme-to-
    privacy mapping, local cryptography/privacy benchmark fixture, TPUv5e
    execution record, generated cryptographic-kernel artifact, FHE correctness
    proof/test boundary, baseline implementation identity, latency table, or
    independent reproduction output exists for the impact article's
    cryptography-for-user-privacy evidence.
  - Required result: add reproduction-grade evidence for the DeepMind impact
    claim and arXiv `2605.14718`: DeepMind impact URL/date/authors, arXiv
    URL/version/authors, PDF retrieval hash and license metadata, explicit
    relation between `cryptography for user privacy` wording and FHE-on-TPU
    optimization, FHE privacy/threat-model statement, TFHE/Jaxite and CKKS/
    CROSS primitive taxonomy, candidate kernel schema, TPUv5e hardware-
    execution provenance, correctness-test definitions, baseline implementation
    identity, latency benchmark rows for bootstrap/rotation/multiplication,
    generated-kernel artifacts and hashes, AlphaEvolve run/model/provider
    provenance, cryptographic-safety review status, deployment and data-use
    boundaries, independent reproduction feasibility assessment, README/
    ROADMAP/paper-index wording that keeps the claim as source-reported
    cryptography/privacy evidence only, and code TODOs for any future FHE or
    cryptographic-kernel benchmark fixture before LibreEvolve claims comparable
    privacy-preserving cryptography optimization support.

- [ ] Reproduce Spanner LSM-compaction AlphaEvolve evidence beyond the generic
      2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, reports that AlphaEvolve improved Google Spanner
    efficiency by refining Log-Structured Merge-tree compaction heuristics.
    The article defines write amplification as the ratio of data written to
    storage versus the original request and reports a 20% reduction in write
    amplification. The same paragraph groups this with compiler-optimization
    storage-footprint results, but does not expose the Spanner workload,
    heuristic, candidate code, or measurement harness.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    Spanner claim only as a generic impact item and marks the
    `spanner_lsm_compaction_fixture` as not implemented locally. No dedicated
    TODO, source snapshot, Spanner storage-engine fixture, LSM-tree model,
    compaction-policy candidate schema, write/read/space-amplification metric
    contract, workload trace, baseline heuristic identity, generated heuristic
    archive, production-safety review artifact, storage-device cost or wear
    model, 20% reduction calculation, Google-internal deployment boundary, or
    independent reproduction output exists for the AlphaEvolve Spanner claim.
  - Required result: add reproduction-grade evidence for the Spanner source:
    DeepMind impact URL/date/authors, retrieval hash, source license/terms
    status, Spanner/LSM component identity, AlphaEvolve access status,
    candidate compaction-heuristic code shape, baseline heuristic semantics,
    workload and key-distribution definitions, write-amplification formula,
    read/space-amplification guard metrics, simulator or benchmark fixture,
    generated-candidate archive, admission and rollback safety policy,
    production-vs-simulation boundary, storage hardware/cost/wear metadata,
    20% reduction calculation, comparison against known LSM compaction
    literature where relevant, independent reproduction feasibility assessment,
    README/ROADMAP/paper-index wording that keeps Spanner as source-reported
    Google-internal infrastructure evidence only, and code TODOs for any
    future LSM-tree or database-compaction benchmark fixture before
    LibreEvolve claims comparable database-infrastructure optimization
    support.

- [ ] Reproduce compiler storage-footprint AlphaEvolve evidence beyond the
      generic 2026 impact boundary.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, reports that AlphaEvolve provided insights for new
    compiler optimization strategies that reduced the storage footprint of
    software by nearly 9%. The claim appears alongside the Spanner LSM
    compaction result, but the impact article does not expose the compiler
    target, storage-footprint metric, workload corpus, generated strategy, or
    deployment/review artifacts. The related Magellan paper and boundary in
    this repo cover AlphaEvolve-style compiler-pass evolution as background
    context, including LLVM/XLA tasks and code-size/runtime optimization, but
    they do not prove the specific 2026 DeepMind nearly-9% storage-footprint
    claim.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    compiler-storage claim only as a generic impact item. No dedicated TODO,
    source snapshot, compiler target identity, code-size/storage-footprint
    metric contract, benchmark corpus, baseline compiler strategy, generated
    heuristic/policy archive, compiler rebuild or integration proof,
    correctness/regression suite, binary/package artifact hashes, production
    review/deployment boundary, nearly-9% calculation, relation-to-Magellan
    mapping, or independent reproduction output exists for the AlphaEvolve
    compiler-storage evidence.
  - Required result: add reproduction-grade evidence for the compiler-storage
    source: DeepMind impact URL/date/authors, retrieval hash, source
    license/terms status, compiler stack identity, relation to Magellan/LLVM/
    XLA or other compiler systems, AlphaEvolve access status, target programs
    and workload corpus, baseline compiler strategy and artifact hashes,
    storage-footprint metric definition, runtime/correctness guard metrics,
    generated strategy/code provenance, compiler integration and rebuild
    evidence, binary/package size tables, nearly-9% calculation, deployment
    and rollback policy, maintainer-review evidence, production-vs-benchmark
    boundary, independent reproduction feasibility assessment, README/
    ROADMAP/paper-index wording that keeps the claim as source-reported
    Google-internal compiler evidence only, and code TODOs for any future
    compiler-storage benchmark fixture before LibreEvolve claims comparable
    compiler storage-footprint optimization support.

- [ ] Reproduce cache-replacement policy AlphaEvolve impact evidence beyond
      ArchAgent background coverage.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, says AlphaEvolve found more efficient cache
    replacement policies in two days where previous approaches required
    months of concerted human-intensive effort. The related ArchAgent paper
    and local `papers/archagent_boundary.json` cover AlphaEvolve-style
    computer-architecture discovery as background context, including generated
    C++ cache-policy logic, ChampSim `policy.h` integration, SPEC06
    single-core and Google Workload Trace multi-core rows, Policy31/
    Policy31-Tuned/Policy61/Policy62 artifacts, IPC-over-LRU metrics, and
    hardware-realizability/state-budget checks. That background does not prove
    the specific DeepMind 2026 impact article's two-days-versus-months claim.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    cache-replacement claim only as a generic impact item. No dedicated TODO,
    official-source snapshot, linked ArchAgent source mapping, cache hierarchy
    fixture, ChampSim/runtime repository snapshot, workload-trace access
    record, generated C++ policy archive, baseline human-effort record,
    two-day run telemetry, months-of-human-effort comparison evidence,
    simulator-escape guard, state-budget verification, hardware-review
    artifact, production/post-silicon boundary, or independent reproduction
    output exists for the AlphaEvolve cache-policy impact claim.
  - Required result: add reproduction-grade evidence for the cache-policy
    source set: DeepMind impact URL/date/authors, ArchAgent arXiv/PDF
    URL/version/authors, retrieval hashes, source license/terms status,
    relation between ArchAgent and the official impact claim, AlphaEvolve
    access status, cache hierarchy and replacement-policy schemas, generated
    C++ policy artifacts, ChampSim integration details, SPEC06 and Google
    Workload Trace access/provenance, IPC-over-LRU metric definitions,
    Policy31/Policy31-Tuned/Policy61/Policy62 result tables, state-budget and
    hardware-realizability checks, two-day run telemetry, months-of-effort
    baseline evidence, simulator-escape and write-bypass controls,
    production/post-silicon boundary, independent reproduction feasibility
    assessment, README/ROADMAP/paper-index wording that keeps the claim as
    source-reported computer-architecture evidence only, and code TODOs for
    any future cache-replacement benchmark fixture before LibreEvolve claims
    comparable architecture-policy optimization support.

- [ ] Reproduce next-generation TPU-design AlphaEvolve lifecycle evidence
      beyond original RTL/EDA boundaries.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, says AlphaEvolve graduated from pilot testing to a
    core infrastructure component and has been used as a regular tool to
    optimize the design of the next generation of TPUs. The Google Cloud
    private-preview launch post separately says AlphaEvolve accelerated
    next-generation TPU design by discovering more efficient arithmetic
    circuits, while Ironwood/TPU7x Google Cloud materials identify the
    seventh-generation TPU family and product surface without tying public
    artifact-level design provenance to the AlphaEvolve claim. Existing local
    hardware RTL/EDA boundaries preserve the original AlphaEvolve paper's
    specific Verilog rewrite and upcoming-TPU contribution claims, not this
    newer regular-tool lifecycle claim.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records the
    next-generation TPU-design claim only as a generic impact item. No
    dedicated TODO, source snapshot, TPU generation identity, regular-tool
    adoption record, pilot-to-core lifecycle proof, AlphaEvolve usage cadence,
    arithmetic-circuit inventory, design-review signoff, RTL/EDA artifact
    linkage, Ironwood/TPU7x relation analysis, Google Cloud product-surface
    separation note, owner/rollout evidence, or independent verification
    output exists for the 2026 next-generation TPU-design claim.
  - Required result: add reproduction-grade evidence for the TPU-design
    lifecycle source set: DeepMind impact URL/date/authors, Google Cloud
    AlphaEvolve private-preview URL/date/authors, Ironwood/TPU7x public URL/
    date, retrieval hashes, source license/terms status, relation to the
    original AlphaEvolve RTL/EDA claim, exact TPU generation or target
    identity if public, AlphaEvolve access status, regular-tool usage cadence,
    pilot/core-infrastructure transition evidence, candidate arithmetic
    circuit/problem schemas, RTL/EDA artifact references or redaction
    boundary, synthesis/PPA/equivalence/formal-verification records,
    designer-review and rollout signoff, integration/deployment milestone,
    product-surface separation from Google Cloud TPU availability, independent
    verification feasibility assessment, README/ROADMAP/paper-index wording
    that keeps the claim as source-reported Google-internal hardware-design
    lifecycle evidence only, and code TODOs for any future TPU-design or
    hardware-codesign benchmark fixture before LibreEvolve claims comparable
    next-generation accelerator-design support.

- [ ] Reproduce Klarna transformer-training AlphaEvolve evidence beyond
      generic customer-claim coverage.
  - Paper/source evidence: Klarna Engineering published `Beyond Prompting:
    How Algorithmic Evolution Doubled our Training Speed` in 2026. The source
    describes applying Google DeepMind AlphaEvolve with Google Cloud to one of
    Klarna's largest transformer models, moving from prompt-level tuning to
    algorithmic code evolution. Current search snippets for the primary
    article report that the work ran over three weeks and nearly 6,000
    candidate programs, improved throughput from 49 to about 72 samples per
    second before combined changes brought throughput to roughly 97 samples
    per second under deterministic production constraints, doubled training
    speed, and improved model quality rather than trading quality away.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records Klarna
    only as a generic customer case from the broader DeepMind impact article
    and marks customer snapshots as missing. No dedicated TODO, source
    snapshot, transformer-training benchmark fixture, model/training-workload
    identity, production-constraint contract, candidate-program archive,
    code-mutation provenance, sample/sec measurement harness, quality-metric
    guard, deterministic audit/reproducibility record, cloud/runtime
    provenance, customer verification artifact, or independent reproduction
    output exists for the Klarna Engineering source.
  - Required result: add reproduction-grade evidence for the Klarna source:
    article URL/date/authors, retrieval hash, source license/terms status,
    customer and Google collaborator identities, AlphaEvolve-on-Google-Cloud
    access status, model-family and training workload identity, seed-code
    baseline semantics, candidate-program generation and selection protocol,
    program-count records, deterministic production constraints, throughput
    measurement definition, 49-to-72-to-97 sample/sec calculations,
    quality-metric preservation/improvement evidence, mutation/provenance
    artifacts, cloud/runtime/training-cost metadata, customer-verification
    snapshots, independent reproduction feasibility assessment, README/
    ROADMAP/paper-index wording that keeps Klarna as source-reported
    deployment evidence only, and code TODOs for any future transformer-
    training optimization benchmark fixture before LibreEvolve claims
    comparable financial-services model-training support.

- [ ] Reproduce BASF supply-chain AlphaEvolve deployment evidence beyond
      official Google Cloud customer-source coverage.
  - Paper/source evidence: Google Cloud published `How BASF manages thousands
    of supply chain decisions with AlphaEvolve's agentic algorithms` on
    May 7, 2026. The article says BASF Agricultural Solutions used
    AlphaEvolve on Google Cloud to build a digital twin for a production
    network spanning 180 production sites and more than 5,000 value chains.
    It describes a foundational seed program that translated demand forecasts
    into production schedules, three years of historical data including
    inventory, demand, and production outputs, AlphaEvolve code mutations that
    tried to match historical supply-chain behavior, an evaluator metric based
    on matching simulated inventory and production decisions to historical
    reality, more than 80% relative accuracy improvement over the seed model,
    and discovered planning rules for production consolidation, dynamic safety
    stocks, and network-wide coordination. The source also names BASF,
    prognostica GmbH, Google Cloud, and Google DeepMind collaborators.
  - Current gap: no source-scoped TODO, paper/customer manifest row, source
    snapshot, local fixture, benchmark report, customer-verification artifact,
    or boundary update exists for this BASF customer article. Existing
    AlphaEvolve 2026 impact TODOs and sidecars track the May 2026 DeepMind
    impact article, Google Cloud private preview, Gemini Enterprise docs, and
    the earlier customer list of Klarna, Substrate, FM Logistic, WPP, and
    Schrodinger, but not this newer BASF supply-chain planning deployment.
    LibreEvolve has no BASF-like supply-chain graph/data schema, demand-
    forecast-to-production-schedule seed-program contract, historical
    inventory/demand/production-data ingestion fixture, digital-twin evaluator,
    production-tier dependency model, safety-stock rule extraction, customer
    collaboration provenance, cloud deployment evidence, or independent
    reproduction output.
  - Required result: add reproduction-grade evidence for the BASF source:
    article URL/date/authors, retrieval hash, source license/terms status,
    customer and collaborator identities, AlphaEvolve-on-Google-Cloud access
    status, supply-chain network dimensions, seed-program baseline semantics,
    historical-data schema and privacy boundary, evaluator metric definition,
    mutation/evaluation protocol, reported accuracy-improvement value and
    baseline, discovered-rule taxonomy, digital-twin artifact requirements,
    cloud/runtime/deployment provenance, customer-verification source
    snapshots, independent reproduction feasibility assessment, README/
    ROADMAP/paper-index wording that keeps BASF as source-reported deployment
    evidence only, and code TODOs for any future supply-chain benchmark
    fixture before LibreEvolve claims comparable customer-deployment support.

- [ ] Reproduce FM Logistic warehouse-scale AlphaEvolve routing evidence beyond
      generic customer-claim coverage.
  - Paper/source evidence: Google Cloud published `How FM Logistic tackled the
    traveling salesman problem at warehouse scale with AlphaEvolve` on
    March 27, 2026. The article says FM Logistic used AlphaEvolve on Google
    Cloud for a warehouse-routing problem in Poland, with a facility spanning
    eight football fields, over 17,700 picking locations, and up to several
    dozen operators on ride-on electric trucks per shift. It describes an
    existing fast cost-prioritized routing algorithm as the seed program,
    AlphaEvolve/Gemini mutation of that code, candidate scoring against
    route-quality objectives, and a reported 10.4% routing-efficiency
    improvement that would reduce travel by over 15,000 km annually.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records FM
    Logistic only as one customer case from the broader DeepMind impact
    article and marks customer snapshots as missing. No dedicated TODO,
    source snapshot, warehouse-routing fixture, TSP/vehicle-routing candidate
    schema, route-cost evaluator, warehouse map/input artifact, seed-program
    baseline record, operator/shift workload model, real-time-responsiveness
    constraint, annual-distance calculation, customer verification artifact,
    Google Cloud deployment evidence, or independent reproduction output
    exists for the March 2026 FM Logistic source.
  - Required result: add reproduction-grade evidence for the FM Logistic
    source: article URL/date/authors, retrieval hash, source license/terms
    status, customer and collaborator identities, AlphaEvolve-on-Google-Cloud
    access status, warehouse/facility and picking-location dimensions, seed
    algorithm identity and baseline semantics, route/input data privacy
    boundary, objective/evaluator metric definitions, mutation/evaluation
    protocol, reported 10.4% improvement and 15,000 km/year calculation,
    annualization assumptions, generated routing-rule/code artifact
    requirements, cloud/runtime/deployment provenance, customer-verification
    snapshots, independent reproduction feasibility assessment, README/
    ROADMAP/paper-index wording that keeps FM Logistic as source-reported
    deployment evidence only, and code TODOs for any future warehouse-routing
    benchmark fixture before LibreEvolve claims comparable logistics support.

- [ ] Reproduce Substrate computational-lithography AlphaEvolve evidence
      beyond generic customer-claim coverage.
  - Paper/source evidence: Substrate published `Information to Atoms` on
    April 7, 2026. The article says Google DeepMind's AlphaEvolve improved
    Substrate's computational-lithography stack by 680% runtime speed and
    reduced compute costs by 97%, enabling simulation and printing of advanced
    semiconductor layers. It describes X-ray lithography, ILT/OPC-style
    computational lithography, simulations of trillions of photons, GPU/TPU
    accelerated differentiable simulation, M1-layer P24/12 nm half-pitch
    examples, and AlphaEvolve/Gemini generation of algorithmic hypotheses,
    code mutations, and autonomous evaluator-scored experiments against
    ground-truth samples. The source reports 256 program evaluations for a
    single objective, 1,853 evaluations across multiple evolved strategies,
    lossless-compression discoveries, lower-precision numerical representation
    switches, 74% lower equivalent memory usage, 680% runtime improvement, and
    97% compute-cost reduction after a month of co-design.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records
    Substrate only as a generic customer case from the broader DeepMind impact
    article and marks customer snapshots as missing. No dedicated TODO,
    source snapshot, computational-lithography benchmark fixture, optical/
    X-ray physics simulation schema, mask/pattern artifact inventory,
    ground-truth sample set, evaluator scoring contract, TPU/GPU runtime
    provenance, compression/numerical-precision mutation record, memory/cost/
    runtime calculation, printed-silicon validation artifact, customer
    verification snapshot, or independent reproduction output exists for the
    April 2026 Substrate source.
  - Required result: add reproduction-grade evidence for the Substrate source:
    article URL/date/authors, retrieval hash, source license/terms status,
    customer and Google collaborator identities, AlphaEvolve-on-Google-Cloud
    access status, computational-lithography problem statement, ILT/OPC/X-ray
    modeling scope, simulation input/output schemas, M1/P24/12 nm artifact
    identities, seed algorithm and baseline semantics, evaluator and
    ground-truth sample definitions, mutation/evaluation protocol, program-
    evaluation counts, compression and precision-change provenance, GPU/TPU
    runtime environment, 97% cost, 74% memory, and 680% runtime calculations,
    printed-silicon validation evidence, cloud/deployment provenance,
    customer-verification snapshots, independent reproduction feasibility
    assessment, README/ROADMAP/paper-index wording that keeps Substrate as
    source-reported deployment evidence only, and code TODOs for any future
    computational-lithography benchmark fixture before LibreEvolve claims
    comparable semiconductor support.

- [ ] Reproduce WPP campaign-model AlphaEvolve evidence beyond generic
      customer-claim coverage.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, reports that WPP used AlphaEvolve in advertising
    and marketing to refine AI model components over complex, high-dimensional
    campaign data, achieving 10% accuracy gains over competitive manual model
    optimizations. WPP Research's `AlphaEvolve Pod` report, `Harnessing Google
    AlphaEvolve for semi-supervised model improvement`, gives source-specific
    details: AlphaEvolve evolved prediction and recommendation model
    components for a campaign-intelligence pipeline, improved prediction
    accuracy by up to 10% and recommendation scores by up to 7% over
    baselines, used macro-average F1 as the prediction target, evaluated
    synthetic datasets V15/V16/V17/V25/V26 plus real data, ran sessions up to
    1,000 evolutionary iterations with four concurrent candidate evaluations,
    and attributes the collaboration to WPP Research, Google Cloud AI for
    Science, and Google DeepMind contributors.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records WPP
    only as a generic customer case from the broader DeepMind impact article
    and marks customer snapshots as missing. No dedicated TODO, source
    snapshot, campaign-intelligence benchmark fixture, synthetic/real dataset
    schema, feature-embedding contract, prediction/recommendation model seed
    code, macro-F1 or normalized-score evaluator, train/validation split
    provenance, class-imbalance handling, candidate-program archive, iteration
    telemetry, Google Cloud/Gemini model access record, WPP collaboration
    verification artifact, privacy/compliance boundary for campaign data, or
    independent reproduction output exists for the WPP evidence.
  - Required result: add reproduction-grade evidence for the WPP source:
    DeepMind impact URL/date/authors, WPP Research pod URL/date/authors,
    retrieval hashes, source license/terms status, customer and Google
    collaborator identities, AlphaEvolve-on-Google-Cloud access status,
    campaign-model problem statement, prediction and recommendation baseline
    semantics, dataset identities and privacy boundaries, feature/modality
    schema, class labels and imbalance policy, evaluator metric definitions,
    macro-F1 and normalized-score calculations, V15/V16/V17/V25/V26/real-data
    result tables, seed-program and evolution-block definitions, model/loss/
    hyperparameter mutation provenance, iteration and concurrency telemetry,
    failure/overfitting checks, manual-review requirements, cloud/runtime cost
    metadata, customer-verification snapshots, independent reproduction
    feasibility assessment, README/ROADMAP/paper-index wording that keeps WPP
    as source-reported deployment evidence only, and code TODOs for any future
    campaign-modeling benchmark fixture before LibreEvolve claims comparable
    advertising or marketing optimization support.

- [ ] Reproduce Schrodinger MLFF AlphaEvolve evidence beyond generic
      customer-claim coverage.
  - Paper/source evidence: the Google DeepMind impact article `AlphaEvolve:
    How our Gemini-powered coding agent is scaling impact across fields`,
    published May 7, 2026, reports that Schrodinger applied AlphaEvolve in
    computational material and life sciences and achieved roughly 4x speedup
    in both Machine Learned Force Fields (MLFF) training and inference. The
    same article includes a Schrodinger technical-lead quote tying faster
    MLFF inference to larger chemical-space exploration and shorter R&D
    cycles. A separate Google Cloud Schrodinger customer case study describes
    the non-AlphaEvolve cloud-computing context: 70% faster therapeutic drug
    development, 97% fewer physically built molecules, 4,000x larger lymphoma
    research datasets, computations moving from weeks to hours on Compute
    Engine and Cloud GPUs, and one program narrowing eight billion molecules
    to 78 candidates.
  - Current gap: the existing AlphaEvolve 2026 impact boundary records
    Schrodinger only as a generic customer case from the broader DeepMind
    impact article and marks customer snapshots as missing. No dedicated TODO,
    source snapshot, MLFF benchmark fixture, molecular-system or materials
    workload identity, training/inference baseline implementation, force-field
    quality metric, speedup calculation, hardware/runtime provenance,
    chemistry-data privacy boundary, molecule-screening pipeline link,
    Google Cloud case-study separation note, customer verification artifact,
    or independent reproduction output exists for the Schrodinger evidence.
  - Required result: add reproduction-grade evidence for the Schrodinger
    source: DeepMind impact URL/date/authors, Google Cloud case-study URL/date,
    retrieval hashes, source license/terms status, customer and Google
    collaborator identities, AlphaEvolve-on-Google-Cloud access status, MLFF
    training and inference workload definitions, baseline semantics, molecular
    dataset/model-family boundaries, evaluator metric definitions, quality and
    physical-validity guards, mutation/evaluation protocol, 4x speedup
    calculation, accelerator/cloud/runtime provenance, chemistry-data privacy
    and customer-verification snapshots, explicit separation between
    AlphaEvolve MLFF claims and older Google Cloud infrastructure results,
    independent reproduction feasibility assessment, README/ROADMAP/
    paper-index wording that keeps Schrodinger as source-reported deployment
    evidence only, and code TODOs for any future MLFF/materials-science
    benchmark fixture before LibreEvolve claims comparable drug-discovery or
    materials-design support.

- [ ] Reproduce AlphaEvolve FHE-on-TPU application evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2605.14718`, submitted May 14, 2026, is
    titled `Adapting AlphaEvolve to Optimize Fully Homomorphic Encryption on
    TPUs`. Its abstract says FHE deployment is limited by computational
    overhead; AlphaEvolve is used to automate hardware-aware cryptographic
    kernel optimization; real-world hardware execution and correctness tests
    guide the search; and TFHE/Jaxite plus CKKS/CROSS primitives are evaluated
    on Google Cloud TPUv5e with reported 2.5x, 1.31x, and 1.18x latency
    improvements over human-engineered state of the art.
  - Current gap: `papers/download_manifest.*` and `papers/README.md` now
    include `2605.14718`, cached locally as
    `papers/2605.14718__FHE_on_TPU.pdf` with byte count and SHA-256 digest,
    and paper-index/TODO coverage treats it as a background-only application
    context. Existing AlphaEvolve application rows include compiler,
    architecture, systems, mechanism-design, workflow, and theoretical-CS
    contexts, but there is still no FHE/cryptography-on-accelerator benchmark
    boundary for TPU-executed cryptographic kernels.
  - Required result: add source-license metadata, relation-to-AlphaEvolve
    details, FHE scheme and primitive taxonomy, TPUv5e hardware-execution
    evidence, correctness-test and benchmark metadata, reported latency-
    speedup claim records, linked code/artifact availability if any, and
    docs wording that treats it as a missing application benchmark rather than
    existing LibreEvolve support.

- [ ] Reproduce AlphaEvolve intentmaking/sensemaking HCI evidence beyond
      paper coverage.
  - Paper/source evidence: arXiv `2605.05921`, submitted May 7, 2026, is
    titled `Intentmaking and Sensemaking: Human Interaction with AI-Guided
    Mathematical Discovery`. Its abstract reports a formative user study with
    11 expert mathematicians who used AlphaEvolve to tackle advanced problems,
    introduces intentmaking as iterative discovery/refinement of experimental
    goals through active system interaction, pairs it with sensemaking over
    results, and argues for AI scientific-discovery tools as collaborative
    instruments.
  - Current gap: `papers/download_manifest.*`, `papers/row_identity.json`, and
    `papers/README.md` now include `2605.05921`, cached locally as
    `papers/2605.05921__Intentmaking_and_Sensemaking.pdf` with byte count and
    SHA-256 digest, and paper-index/TODO coverage treats it as background-only
    HCI/user-study context. Existing source rows cover the original
    AlphaEvolve specification, follow-on math repositories, impact articles,
    and application-domain papers, but not the human-interaction/user-study
    evidence surface, intentmaking taxonomy, session-trace requirements,
    dashboard/UI artifacts, or privacy/redaction boundaries for study data.
  - Required result: add evidence beyond paper coverage: source license,
    relation to AlphaEvolve, study-design metadata, participant-count and
    problem-domain records, intentmaking/sensemaking taxonomy, UI/session
    artifact availability, privacy/redaction policy, and docs wording that
    treats it as HCI/source evidence rather than implemented LibreEvolve
    interaction support.

- [ ] Reproduce AlphaEvolve radar power-allocation evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2605.01794`, submitted May 3, 2026, is
    titled `Discover Fast Power Allocation Solution for Multi-Target Tracking
    via AlphaEvolve Evolution`. Its abstract proposes an AlphaEvolve-driven
    paradigm for efficient radar resource allocation, evolving an
    interpretable scoring function from physically inspired features and
    converting it into feasible power allocations through a deterministic
    constraint-satisfying transformation. It reports 1.51% average relative
    performance loss, generalization across diverse scenarios and target
    counts, and more than three orders of magnitude speedup over conventional
    iterative solvers.
  - Current gap: the paper manifest, paper index, row-identity manifest, and
    TODO coverage now include `2605.01794`, cached locally as
    `papers/2605.01794__Radar_Power_Allocation.pdf` with byte count `959569`
    and SHA-256
    `f5a249cb6b0f4b5c4f04487e8b6b236d3bd6be4d498f849892cd85926adb9fa7`.
    Existing AlphaEvolve application-source rows still do not capture radar
    tracking, real-time resource allocation, power-allocation constraints,
    physically inspired feature encodings, symbolic closed-form policy
    artifacts, generalization splits, or iterative-solver baselines.
  - Required result: add reproduction-grade evidence for `2605.01794`:
    source-license metadata, relation to AlphaEvolve, radar task taxonomy,
    scenario and target-count metadata, evolved scoring-function and
    feasibility-transform artifacts, baseline solver identities,
    tracking-performance and speedup metrics, code/artifact availability if
    any, and independent verification outputs.

- [ ] Reproduce EvoX adaptive meta-evolution evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2602.23413`, submitted February 26, 2026 and
    last revised March 16, 2026, is titled `EvoX: Meta-Evolution for
    Automated Discovery`. Its abstract says AlphaEvolve and related
    LLM-driven evolutionary systems depend on search strategy choices over
    prior evaluated solutions; fixed strategies with predefined knobs such as
    explore/exploit ratios may fail to adapt; and EvoX jointly evolves
    candidate solutions and the search strategies used to generate them,
    reporting majority-task wins over AlphaEvolve, OpenEvolve, GEPA, and
    ShinkaEvolve across nearly 200 real-world optimization tasks.
  - Current gap: the paper manifest, paper index, row-identity manifest, and
    TODO coverage now include `2602.23413`, cached locally as
    `papers/2602.23413__EvoX.pdf` with byte count `4626948` and SHA-256
    `df9c3c8149c650112c1b034f874a458c6ae65bcac05421d1790c3cac7e9d2622`.
    Existing source rows still do not capture adaptive meta-evolution,
    strategy self-optimization, strategy-state traces, cross-task dynamic
    search-policy adaptation, or benchmark comparisons against EvoX.
  - Required result: add reproduction-grade evidence for `2602.23413`:
    source-license metadata, relation to AlphaEvolve and LibreEvolve fixed
    mixed parent selection, adaptive strategy representation,
    controller/provenance artifacts, task taxonomy, baseline method
    identities, metric definitions, win-rate and token-efficiency claims,
    ablation evidence, code/artifact availability if any, and independent
    verification outputs.

- [ ] Reproduce DeltaEvolve semantic-delta context evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2602.02919`, submitted February 2, 2026, is
    titled `DeltaEvolve: Accelerating Scientific Discovery through
    Momentum-Driven Evolution`. Its abstract says AlphaEvolve and similar
    LLM-driven evolutionary systems use full-code histories that are
    context-inefficient and may dilute core algorithmic ideas; DeltaEvolve
    replaces that context with structured semantic deltas explaining how and
    why modifications between successive nodes affect performance, organized
    through a multi-level database and progressive disclosure mechanism.
  - Current gap: the paper manifest, paper index, row-identity manifest, and
    TODO coverage now include `2602.02919`, cached locally as
    `papers/2602.02919__DeltaEvolve.pdf` with byte count `3764777` and
    SHA-256
    `d4726d81fe96ddb4b370c4a37c06510394597f640187d6ba8e615b5952c3a4d8`.
    Existing source rows still do not capture semantic-delta memory,
    node-transition effect attribution, progressive context disclosure, or
    token-efficiency comparisons against full-code histories.
  - Required result: add reproduction-grade evidence for `2602.02919`:
    source-license metadata, relation to AlphaEvolve and LibreEvolve
    prompt/context policy, semantic-delta schema, node-transition provenance,
    performance-effect attribution, multi-level database/index metadata,
    progressive-disclosure policy, token-accounting metrics,
    scientific-task benchmark taxonomy, baseline method identities,
    code/artifact availability if any, and independent verification outputs.

- [ ] Reproduce MLEvolve long-horizon ML-engineering evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2606.06473`, submitted June 4, 2026, is
    titled `MLEvolve: A Self-Evolving Framework for Automated Machine
    Learning Algorithm Discovery`. Its abstract says long-horizon MLE agents
    suffer from inter-branch information isolation, memoryless search, and
    lack of hierarchical control; MLEvolve addresses this with Progressive
    MCGS, graph-based reference edges, entropy-inspired progressive
    scheduling, Retrospective Memory, and adaptive coding modes; and it
    reports MLE-Bench state-of-the-art performance under a 12-hour budget plus
    outperformance of AlphaEvolve on mathematical algorithm optimization
    tasks. The arXiv page links code at `https://github.com/InternScience/MLEvolve`.
  - Current gap: the paper manifest, paper index, row-identity manifest, and
    TODO coverage now include `2606.06473`, cached locally as
    `papers/2606.06473__MLEvolve.pdf` with byte count `2661825` and SHA-256
    `db5a1709ee78cd3d979c47b8734d8449427b6f69787fdb0d5e6f8e43951e9bde`.
    Existing rows still do not capture MLE-Bench, Progressive MCGS,
    cross-branch graph references, retrospective MLE memory, adaptive coding
    modes, or long-horizon ML-engineering evaluation budgets.
  - Required result: add reproduction-grade evidence for `2606.06473`:
    source-license metadata, linked-code URL/status, relation to AlphaEvolve
    and LibreEvolve, Progressive MCGS and graph-reference schema,
    entropy-schedule metadata, retrospective-memory taxonomy, adaptive
    coding-mode artifacts, MLE-Bench task/submission records, 12-hour budget
    and metric definitions, mathematical-algorithm baseline identities,
    code/artifact reproducibility status, and independent verification outputs.

- [ ] Reproduce deletion-correcting-code FunSearch evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2504.00613`, submitted April 1, 2025 and
    last revised June 5, 2026, is titled `LLM-Guided Search for
    Deletion-Correcting Codes`. Its abstract adapts FunSearch-style
    LLM-guided evolutionary search to construct deletion-correcting codes at
    short code lengths, finds a function that is proved to construct the
    conjectured-optimal Varshamov-Tenengolts code for a single deletion,
    reports improved empirical constructions for multiple deletions and
    quaternary edit codes, and studies design choices for LLM-guided
    evolutionary search. The paper reports that, for this problem, compute is
    better spent sampling more functions than producing longer reasoning
    traces, that co-evolving natural-language descriptions with code hurts
    search quality, and that deduplicating logically identical functions is
    critical for search diversity. It also notes that evaluation scales
    exponentially with code length, limiting the formulation to short codes.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2504.00613`. Existing LibreEvolve duplicate-work and
    distributed-pipeline TODOs cover exact workspace hashes, current-run
    duplicate caches, semantic near-duplicate absence, and async topology
    boundaries, but they do not reproduce deletion-code candidate schemas,
    greedy code-construction priority functions, Varshamov-Tenengolts proof
    artifacts, multiple-deletion or quaternary edit-code benchmark rows,
    sampling-versus-reasoning budget ablations, natural-language-description
    co-evolution ablations, logical-function-equivalence deduplication, or
    exponential evaluation-scaling diagnostics.
  - Required result: add reproduction-grade evidence for `2504.00613`:
    title/authors/arXiv version/date, source license, linked code/artifact
    availability, relation to FunSearch, AlphaEvolve, and LibreEvolve,
    deletion-code candidate representation, priority-function interface,
    greedy construction evaluator, single-deletion Varshamov-Tenengolts proof
    linkage, multiple-deletion and quaternary edit-code benchmark metadata,
    baseline identities, sampling-count versus reasoning-trace ablation
    records, natural-language-description co-evolution ablation records,
    logical-equivalence deduplication policy and verifier, distributed or
    batched inference/runtime provenance if reproduced, evaluation-scaling
    measurements, independent verification outputs, and README/ROADMAP wording
    that treats deletion-correcting-code search as missing benchmark evidence
    rather than implemented LibreEvolve support.

- [ ] Reproduce bivariate-bicycle quantum-code discovery evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.02418`, submitted June 1, 2026, is
    titled `Evolutionary Discovery of Bivariate Bicycle Codes with LLM-Guided
    Search`. Its abstract says quantum LDPC code discovery requires searching
    large algebraic design spaces while certifying both candidate parameters
    and equivalence classes. The workflow mutates Python programs that
    generate bivariate-bicycle and perturbed bivariate-bicycle code ansatze;
    across five campaigns it performed approximately `1,650` evolutionary
    iterations, screened about `2 x 10^5` candidate codes, and used roughly
    `140` hours plus about `US$400` of LLM inference. Candidate evaluation
    combines `GF(2)` rank computation, distance estimation and certification,
    mixed-integer linear programming, BLISS Tanner-graph deduplication,
    decomposability analysis, and local-Clifford equivalence checks. At block
    length `n <= 360`, it reports `465` distinct candidate codes: `97` CSS
    bivariate-bicycle codes and `368` non-CSS perturbed variants, including
    an indecomposable `[[288,16,12]]` code, higher-weight codes up to `k = 50`
    at `d = 8`, and non-CSS perturbed codes matching the gross-code figure of
    merit at `[[144,12,12]]`. The linked `qiskit-community/qcode-discovery`
    repository is Apache-2.0 and includes campaign results, verification
    scripts, ablations, MILP/BP-OSD result files, JSON/JSONL run logs, and
    W&B tracking hooks.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.02418`. Existing LibreEvolve constructive-math,
    deletion-code, Zarankiewicz, FHE/TPU, and duplicate-work TODOs do not
    reproduce quantum LDPC candidate schemas, BB/PBB polynomial tuple
    generation, CSS and non-CSS code-family distinction, staged quantum-code
    validation cascades, `GF(2)` rank evidence, BP-OSD distance-estimation
    diagnostics, MILP exact-distance certification, BLISS Tanner-graph
    deduplication, decomposability analysis, local-Clifford equivalence
    checks, gross-code baselines, campaign-level cost/runtime telemetry, or
    code-capacity simulation result provenance.
  - Required result: add reproduction-grade evidence for `2606.02418`:
    title/authors/arXiv version/date, source license, linked-code snapshot,
    relation to FunSearch, AlphaEvolve, OpenEvolve, and LibreEvolve, BB/PBB
    candidate schema, polynomial-ring/lattice metadata, CSS/non-CSS
    validation contracts, staged evaluation cascade records, `GF(2)` rank
    and distance-estimation artifacts, MILP solver configuration and
    optimality status, BLISS deduplication records, Tanner-graph and
    decomposability evidence, local-Clifford equivalence audit, gross-code and
    Bravyi-baseline identities, campaign model/population/iteration/cost
    telemetry, result-file hash inventory, ablation records, threshold or
    code-capacity simulation provenance, independent verification outputs,
    and README/ROADMAP wording that treats BB/PBB quantum-code discovery as
    missing benchmark evidence rather than implemented LibreEvolve support.

- [ ] Reproduce EvoDiverse parallel-tempered hypothesis-search evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.10587`, submitted June 9, 2026, is
    titled `Towards Diverse Scientific Hypothesis Search with Large Language
    Models`. Its abstract frames scientific discovery as needing a set of
    high-quality alternative hypotheses under noisy and expensive validation,
    not only a single best hypothesis. It argues that common evolutionary
    search recipes prioritize optimization over exploration, causing diversity
    collapse, and formulates hypothesis search as efficiently producing
    diverse, high-quality hypotheses under a fixed validation budget.
    EvoDiverse is presented as a parallel-tempered evolutionary framework that
    searches at multiple temperature levels and exchanges information across
    temperatures to improve exploration without disrupting convergence. The
    paper reports quality and diversity improvements under the same validation
    budget across molecular discovery, equation discovery, and algorithm
    discovery, with candidates remaining robust under more expensive downstream
    computational validations. Its appendix gives a generic template with
    initial temperature-indexed pools, LLM evolutionary operators, objective
    scores, offspring and parent sizes, swap size/period, total iterations,
    a powering factor, Metropolis-Hastings swap dynamics, and adaptive power
    adjustment.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.10587`. Existing LibreEvolve MAP-Elites, proposal-
    diversity, hypothesis-index, hypothesis-branch, cascade hypothesis-test,
    and LEVI diversity-preserving TODOs do not reproduce a fixed-validation-
    budget hypothesis-sampling objective, multiple temperature-indexed pools,
    Boltzmann-style score-to-weight conversion, Metropolis-Hastings cross-pool
    swaps, adaptive powering factors, swap-rate diagnostics, same-budget
    quality-and-diversity comparisons, molecular/equation/algorithm discovery
    task coverage, or downstream expensive-validation robustness checks.
  - Required result: add reproduction-grade evidence for `2606.10587`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, FunSearch, MAP-Elites,
    LibreEvolve's prompt/database/archive behavior, and current proposal-
    diversity reports, temperature-pool schema, objective and validation-
    budget definitions, score-to-weight/powering-factor formulas, parent and
    survivor sampling policy, cross-temperature swap contract,
    Metropolis-Hastings acceptance evidence, adaptive swap-rate/power records,
    quality and diversity metrics, same-budget baseline identities,
    molecular/equation/algorithm discovery task metadata, downstream
    validation records, ablation outputs for swaps and temperature levels,
    independent verification outputs, and README/ROADMAP wording that treats
    EvoDiverse-style parallel-tempered hypothesis search as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Reproduce medical-decision-pipeline evolution evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.07342`, submitted June 5, 2026, is
    titled `LLM-Guided Evolution for Medical Decision Pipelines`. Its abstract
    studies LLM-guided MAP-Elites evolution as an inference-time alternative
    to fine-tuning or manual clinical pipeline engineering and provides an
    implementation repository. It formulates urgency triage, interactive
    consultation, and medical image classification as evolutionary searches
    over executable artifacts optimized by task-specific fitness functions.
    The paper uses GigaEvo with MAP-Elites search, asynchronous evaluation,
    rewrite-based mutation, and lineage tracking; candidates include
    standalone Python decision programs, consultation policies, and
    prompt-producing modules. Reported evidence covers safety-weighted
    Semigran and MIMIC-ESI triage, MEDIQ/iMEDQA interactive consultation with
    iCRAFTMD held-out transfer, and PneumoniaMNIST prompt-only evolution for
    fixed MedGemma VLMs while preserving strict JSON outputs. It emphasizes
    practical clinical constraints such as emergency recall, undertriage,
    interaction-token cost, cross-model transfer, held-out evaluation,
    structured-output validity, and interpretable program-level mechanisms.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.07342`. Existing LibreEvolve GigaEvo, MAP-Elites,
    EvoRubric, proposal-diversity, evaluator-output, and benchmark-hardening
    TODOs do not reproduce safety-sensitive clinical candidate schemas,
    Semigran/Levine/MIMIC-ESI triage splits, MEDIQ/iMEDQA/iCRAFTMD
    interactive-consultation protocols, PneumoniaMNIST/MedGemma prompt-only
    VLM evaluation, emergency-recall and undertriage metrics, token-cost
    frontiers, strict clinical JSON-output validation, medical cross-model
    transfer, held-out clinical generalization, or ethics/data-access
    provenance.
  - Required result: add reproduction-grade evidence for `2606.07342`:
    title/authors/arXiv version/date, source license, implementation-
    repository snapshot, relation to AlphaEvolve, GigaEvo, MAP-Elites, and
    LibreEvolve, clinical task definitions, dataset access and ethics
    constraints, candidate-artifact schemas for triage programs,
    consultation policies, and prompt-producing VLM modules, fitness formulas,
    safety-weighted objective records, emergency-recall/undertriage metrics,
    Semigran/Levine/MIMIC-ESI/iMEDQA/iCRAFTMD/PneumoniaMNIST metadata,
    MedGemma/model-backbone identities, structured-output parser contracts,
    interaction-cost accounting, cross-model and held-out transfer records,
    ablation outputs, qualitative mechanism annotations, benchmark baseline
    identities, independent verification outputs, and README/ROADMAP wording
    that treats medical decision-pipeline evolution as missing application
    benchmark evidence rather than implemented LibreEvolve support.

- [ ] Reproduce tensor-network contraction-order optimization evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.01975`, submitted June 1, 2026, is
    titled `Algorithmic algorithm development with LLMs: A Case Study on
    LLM-Usage for Contraction Order Optimization in Tensor Networks`. The
    arXiv HTML lists a CC BY 4.0 license. Its abstract studies LLM-based
    algorithm development through contraction-order optimization for tensor
    networks with OpenEvolve, focusing on model choice, evaluation metric
    design, and test-instance selection. The paper positions verifier-guided
    evolutionary coding agents as promising for algorithm development and
    improvement, but emphasizes that human scientists still need to define,
    validate, interpret, and audit the evaluation setup and resulting
    algorithms. It situates the case study against FunSearch, AlphaEvolve,
    OpenEvolve, GigaEvo, CodeEvolve, ShinkaEvolve, DeepEvolve, LLM4AD,
    ThetaEvolve, Escher-Loop, AlgoTuner, and related heuristic-evolution
    systems.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.01975`. Existing LibreEvolve matrix/tensor TODOs cover
    AlphaEvolve matrix-multiplication tensor-decomposition artifacts,
    tensor-rank certificates, and loss-function-only scope boundaries, but
    they do not reproduce tensor-network contraction-order candidate schemas,
    contraction-tree or elimination-order representations, tensor-network
    test-instance suites, contraction-cost metrics, OpenEvolve run
    configuration, model-choice comparisons, evaluation-metric sensitivity,
    test-instance sensitivity, baseline planner identities, human
    interpretation and validation records, or contraction-order correctness
    and performance certification.
  - Required result: add reproduction-grade evidence for `2606.01975`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, OpenEvolve, and LibreEvolve,
    tensor-network problem schema, contraction-order candidate representation,
    evaluator contract, contraction-cost metric definitions, correctness
    checks, test-instance inventory, baseline planner and library identities,
    LLM/model-selection records, OpenEvolve configuration and budget telemetry,
    metric/test-instance ablation records, generated algorithm artifacts,
    human scientist validation and interpretation notes, independent
    verification outputs, and README/ROADMAP wording that treats tensor-network
    contraction-order optimization as missing application benchmark evidence
    rather than implemented LibreEvolve support.

- [ ] Reproduce UH-NAS physical-neural-network co-design evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.10294`, submitted June 9, 2026, is
    titled `LLM-Guided Neural Architecture Search for Robust Co-Design of
    Physical Neural Networks`. The arXiv HTML lists an arXiv.org perpetual
    non-exclusive license. Its abstract says unconventional hardware deployment
    requires neural architectures that co-optimize task accuracy with
    platform-specific energy cost, physical non-idealities, and numerical
    precision. UH-NAS is presented as a hardware-agnostic, LLM-guided neural
    architecture search framework that uses language models as evolutionary
    operators to co-optimize accuracy and inference energy. It exposes hardware
    as a swappable backend with per-platform energy models, physical
    constraints, and non-ideality simulators, enabling system-level comparison
    across hardware backends without changing the search algorithm. The paper
    tests optical MZI hardware, reports more diverse and robust architectures
    than conventional baselines, compares against existing LLM-to-NAS
    approaches, and includes ablations on robustness under non-idealities and
    system-prompt effects.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.10294`. Existing LibreEvolve FHE-on-TPU, TPU/compiler,
    systems, matrix/tensor, MAP-Elites, and hardware-aware application TODOs
    do not reproduce neural-architecture candidate schemas, hardware-backend
    abstraction, per-platform energy models, optical MZI constraints,
    non-ideality simulators, numerical-precision policies, inference-energy
    objective records, NAS baseline comparisons, architecture-diversity and
    robustness metrics, or system-prompt ablations for architecture-hardware
    co-design.
  - Required result: add reproduction-grade evidence for `2606.10294`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, FunSearch, MAP-Elites, and
    LibreEvolve, neural architecture candidate schema, LLM evolutionary
    operator prompt/mutation contract, hardware-backend interface, energy-model
    definitions, optical MZI simulator and physical-constraint metadata,
    numerical precision and non-ideality policies, accuracy/energy objective
    normalization, archive/diversity metrics, baseline NAS and LLM-to-NAS
    identities, robustness-ablation records, system-prompt ablation records,
    hardware-generalization comparison records, independent verification
    outputs, and README/ROADMAP wording that treats UH-NAS physical-neural-
    network co-design as missing application benchmark evidence rather than
    implemented LibreEvolve support.

- [ ] Reproduce LLM-evolved pattern-generator planning evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.02438`, submitted June 1, 2026, is
    titled `LLM-Evolved Pattern Generators for Optimal Classical Planning`.
    Its abstract says learned heuristics are competitive for satisficing
    planning, but existing learned approaches usually improve search guidance
    rather than guarantee admissibility, making them unsuitable for optimal
    classical planning. The paper presents a method for learning
    domain-dependent heuristics that are admissible by design and preserve
    A* optimality guarantees by learning programs that construct abstractions,
    not direct state-to-heuristic mappings. It uses an LLM-driven evolutionary
    program-synthesis framework to obtain, for each planning domain, a program
    that produces a pattern collection for any task in that domain, then
    combines the resulting patterns admissibly via saturated cost partitioning.
    The paper reports interpretable domain-specific insights, negligible
    test-time overhead, coverage matching state-of-the-art domain-independent
    baselines on several domains, and substantially faster per-state heuristic
    evaluation.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.02438`. Existing LibreEvolve OpenEvolve, GigaEvo,
    MAP-Elites, benchmark-hardening, tensor/matrix, and constructive-math
    TODOs do not reproduce optimal-classical-planning task schemas, PDDL or
    transition-system problem fixtures, pattern-generator candidate programs,
    abstraction admissibility proofs, saturated-cost-partitioning evidence,
    A* optimality-preservation records, planning-domain train/test splits,
    coverage/per-state-evaluation-time metrics, state-of-the-art
    domain-independent baseline comparisons, or interpretability artifacts for
    evolved planning heuristics.
  - Required result: add reproduction-grade evidence for `2606.02438`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to FunSearch, AlphaEvolve, OpenEvolve, and
    LibreEvolve, classical-planning domain schema, PDDL/transition-system
    fixture inventory, pattern-collection generator interface, abstraction
    construction records, admissibility and consistency proof artifacts,
    saturated-cost-partitioning configuration, A* optimality-preservation
    checks, OpenEvolve run configuration and budget telemetry, planning-domain
    train/test split metadata, coverage and node-expansion metrics,
    per-state heuristic-evaluation-time records, baseline planner/heuristic
    identities, evolved-program interpretability notes, independent
    verification outputs, and README/ROADMAP wording that treats LLM-evolved
    pattern generators for optimal planning as missing benchmark evidence
    rather than implemented LibreEvolve support.

- [ ] Reproduce FunctionEvolve structure-guided symbolic-regression evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.07704`, submitted June 5, 2026, is
    titled `FunctionEvolve: Structure-Guided Symbolic Regression with LLMs`.
    Its abstract frames symbolic regression as recovering explicit scientific
    laws from data and argues that recent LLM-guided mutation methods are more
    directed than random genetic programming but remain structure-blind. The
    paper says exact symbolic recovery needs both semantic guidance and
    explicit valid symbolic structure, so search should operate over
    domain-informed symbolic representations rather than vague candidates.
    FunctionEvolve organizes search around expression trees: structure
    summaries support diverse parent selection, local tree edits preserve
    useful subexpressions, and structure-aware coefficient fitting decomposes,
    constrains, and simplifies coefficients so scoring does not reject a
    correct expression skeleton. The paper evaluates on LLM-SRBench synthetic
    tasks, reports large exact-form recovery gains over same-backbone
    baselines, and audits benchmark identifiability issues in the materials-
    science subset.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.07704`. Existing LibreEvolve PACEvolve, EvoDiverse,
    CausalEvolve, proposal-hypothesis, and benchmark-hardening TODOs do not
    reproduce symbolic-regression candidate schemas, expression-tree
    canonicalization, local tree-edit mutation operators, structure-summary
    parent selection, elementary-function-family constraints, coefficient-
    fitting decomposition/simplification, exact-symbolic-recovery metrics,
    LLM-SRBench task metadata, same-backbone symbolic-regression baselines, or
    benchmark non-identifiability audits for materials-science tasks.
  - Required result: add reproduction-grade evidence for `2606.07704`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, FunSearch, LLM-SR, PACEvolve, and
    LibreEvolve, symbolic-regression task schema, expression-tree candidate
    representation, structural canonicalization rules, local tree-edit
    mutation contract, structure-summary/diversity parent-selection records,
    elementary-function-family policy, coefficient-fitting and simplification
    artifacts, scoring and exact-recovery metric definitions, LLM-SRBench
    synthetic-task metadata, same-backbone baseline identities, ablation rows
    for structure visibility and coefficient optimization, materials-science
    identifiability audit records, independent verification outputs, and
    README/ROADMAP wording that treats FunctionEvolve-style structure-guided
    symbolic regression as missing benchmark evidence rather than implemented
    LibreEvolve support.

- [ ] Reproduce diffuse-AI-control fuzzy-task prompt-optimization evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.08892`, submitted June 8, 2026, is
    titled `Diffuse AI Control on Fuzzy Tasks` and the arXiv HTML lists a
    CC BY 4.0 license. Its abstract frames diffuse AI control as mitigating
    long-horizon sabotage on fuzzy, hard-to-grade tasks. The paper defines a
    red-team/blue-team adversarial game: the blue team uses a weaker trusted
    model to construct a weak score for training or selection, while the red
    team searches for model behaviors that receive high weak scores but low
    ground-truth-proxy scores. It evaluates experimental-proposal generation
    from recent ML papers using Opus 4.6 as the untrusted generator, Sonnet
    4.6 with paper access as the ground-truth proxy scorer, and Haiku 4.5 as
    the weak trusted scorer. The red team uses multi-objective evolutionary
    prompt optimization adapted from MO-ASHA and AlphaEvolve design ideas to
    map weak-score versus ground-truth-proxy Pareto frontiers; the paper also
    uses OpenEvolve as a single-objective AlphaEvolve baseline and reports a
    blue-team adversarial optimization procedure that discovers a more robust
    weak-scorer prompt.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.08892`. Existing LibreEvolve objective-frontier,
    proposal-diversity, critique, feedback-grader, benchmark-hardening, and
    OpenEvolve TODOs do not reproduce fuzzy-task research-question extraction,
    proposal-generation task fixtures, weak-versus-ground-truth scorer
    separation, red-team/blue-team strategy schemas, MO-ASHA-style
    multi-objective prompt optimization, subversion and Goodharting Pareto
    frontier records, weak-score slack/lower-confidence-bound policy,
    rubric-access ablations, sandbagging-detector prompts, or adversarial
    blue-team prompt optimization.
  - Required result: add reproduction-grade evidence for `2606.08892`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, OpenEvolve, MO-ASHA, and
    LibreEvolve, fuzzy-task dataset and paper-processing pipeline metadata,
    research-question extraction records, generator/weak-scorer/ground-truth-
    proxy model identities, scorer rubric and paper-access policy, red-team
    prompt schema, blue-team prompt schema, weak-score and ground-truth-score
    normalization, subversion and Goodharting Pareto frontier artifacts,
    slack/lower-confidence-bound calculations, MO-ASHA scheduler configuration,
    OpenEvolve baseline configuration, rubric-access and scorer ablation rows,
    sandbagging-detector evidence, adversarial blue-team optimization records,
    qualitative attack/defense examples, independent verification outputs, and
    README/ROADMAP wording that treats diffuse-AI-control fuzzy-task prompt
    optimization as missing safety benchmark evidence rather than implemented
    LibreEvolve support.

- [ ] Reproduce DMCI program-and-parameter co-search evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.09930`, submitted June 7, 2026, is
    titled `Compile Once, Differentiate Everywhere: A Differentiable
    Meta-Circular Interpreter`. Its abstract presents differentiable
    meta-circular interpretation (DMCI): a self-hosting Scheme subset is
    compiled into differentiable computation graphs so a compiled Scheme
    interpreter executes programs supplied as data while reverse-mode autodiff
    propagates gradients into continuous constants embedded in those programs.
    The interpreter is compiled once, then new programs inherit
    differentiability without recompilation or custom gradient code while
    retaining closures, recursion, and data structures. The paper proves
    gradients through the compiled interpreter are correct almost everywhere,
    validates them against direct compilation across `171` recursive and
    higher-order program-seed pairs, and uses DMCI for program-and-parameter
    co-search: an LLM proposes Scheme program structures while exact gradients
    calibrate each candidate's continuous parameters through a frozen
    interpreter. It applies this OpenEvolve-style search to battery
    capacity-fade modeling and a high-dimensional El Nino inverse problem.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.09930`. Existing LibreEvolve FunctionEvolve,
    symbolic-regression, matrix/tensor, gradient-method, evaluator-contract,
    and arbitrary-language-runner TODOs do not reproduce Scheme candidate
    programs, differentiable interpreter compilation, autograd backend
    provenance, continuous-parameter extraction and calibration, gradient
    correctness tests, direct-compilation comparison records, frozen-
    interpreter reuse, battery degradation fixtures, El Nino inverse-problem
    likelihood evaluation, or combined discrete-structure plus continuous-
    parameter search telemetry.
  - Required result: add reproduction-grade evidence for `2606.09930`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, OpenEvolve, symbolic regression,
    and LibreEvolve, Scheme subset and interpreter semantics, candidate
    program schema, continuous-parameter annotation policy, compiler/autograd
    backend metadata, gradient-correctness theorem/proof scope, recursive and
    higher-order validation-pair inventory, direct-compilation comparison
    artifacts, optimizer and parameter-calibration traces, OpenEvolve outer-
    loop configuration, MAP-Elites/island metadata if reproduced, battery
    capacity-fade split definitions and baselines, El Nino inverse-problem
    likelihood records, gradient-free baseline failures, held-out forecast
    metrics, independent verification outputs, and README/ROADMAP wording that
    treats DMCI program-and-parameter co-search as missing benchmark evidence
    rather than implemented LibreEvolve support.

- [ ] Reproduce OpenEvolve combinatorial-bijection discovery evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2511.20987`, submitted November 26, 2025,
    is titled `Even with AI, Bijection Discovery is Still Hard: The
    Opportunities and Challenges of OpenEvolve for Novel Bijection
    Construction`. Its abstract says AlphaEvolve, OpenEvolve, and
    ShinkaEvolve use LLM teams to generate and evolve human-readable code
    candidates beyond one-shot LLM outputs, and argues that explicit
    construction problems are natural targets beyond bound-establishing
    applications such as sphere packing. The paper applies OpenEvolve to three
    combinatorial bijection-construction problems involving Dyck paths, two
    known and one open, and concludes that OpenEvolve is promising for
    combinatorialists but current frontier systems still struggle to find
    novel research-level bijections, reinforcing the need for human
    mathematicians in the loop.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2511.20987`. Existing LibreEvolve constructive-math,
    Bruhat-interval, Ramsey, Zarankiewicz, sphere-packing, and OpenEvolve
    TODOs do not reproduce combinatorial-bijection candidate schemas,
    Dyck-path object encodings, bijection/inverse contracts, known-bijection
    recovery tasks, open-bijection construction attempts, proof obligation
    tracking, human mathematician review states, failure-mode taxonomy for
    research-level construction, or lessons-learned evidence about where
    LLM-guided program evolution needs expert intervention.
  - Required result: add reproduction-grade evidence for `2511.20987`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, OpenEvolve, ShinkaEvolve, and
    LibreEvolve, Dyck-path representation schema, three problem definitions,
    candidate bijection program interface, inverse/checker contracts,
    exactness and domain/codomain coverage tests, known-bijection baseline
    identities, open-problem attempt logs, OpenEvolve run configuration and
    budget telemetry, generated program artifacts, proof and explanation
    records, human-review and intervention notes, negative-result/failure
    taxonomy, independent verification outputs, and README/ROADMAP wording
    that treats combinatorial-bijection discovery as missing constructive-math
    benchmark evidence rather than implemented LibreEvolve support.

- [ ] Reproduce SeaEvo strategy-space evolution evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2604.24372`, submitted April 27, 2026 and
    last revised May 8, 2026, is titled `SeaEvo: Advancing Algorithm Discovery
    with Strategy Space Evolution`. Its abstract says LLM-guided evolutionary
    search is increasingly used for automated algorithm discovery, but current
    methods usually track progress through executable programs and scalar
    fitness. Even when natural-language reasoning appears in heuristic
    descriptions or reflection, it often remains transient mutation context or
    unstructured memory instead of persistent population-level state over
    strategic directions. SeaEvo adds a modular strategy-space layer: each
    candidate program receives an explicit natural-language strategy, the
    archive is clustered by strategy semantics, behaviorally complementary
    inspirations are retrieved, and the strategy landscape is periodically
    navigated to avoid saturated directions. The paper reports improvements
    over existing evolutionary backbones across algorithm discovery, systems
    optimization, and agent-scaffold design tasks, including a `20.6%` average
    relative improvement across four systems benchmarks and a `3x` higher best
    single Prism run.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2604.24372`. Existing LibreEvolve proposal-hypothesis,
    proposal-diversity, failure-memory, DeepResearch, LEVI, PACEvolve, and
    MAP-Elites TODOs do not reproduce candidate-level strategy descriptions as
    first-class population state, semantic strategy clustering, stratified
    experience retrieval, strategy-complementarity inspiration selection,
    periodic strategic landscape navigation, saturated/underexplored strategy
    family detection, strategy-level lineage, or same-backbone SeaEvo versus
    OpenEvolve/ShinkaEvolve benchmark comparisons.
  - Required result: add reproduction-grade evidence for `2604.24372`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, OpenEvolve, ShinkaEvolve, LEVI,
    PACEvolve, and LibreEvolve, strategy-description schema, candidate-to-
    strategy linkage, semantic clustering method, strategy-cluster archive
    records, behaviorally complementary inspiration retrieval policy,
    strategic landscape summary artifacts, saturated and underexplored family
    diagnostics, mutation prompt integration, per-backbone configuration and
    budget telemetry, algorithm-discovery/systems/agent-scaffold benchmark
    metadata, cost-efficiency records, ablation outputs for strategy
    articulation/retrieval/navigation, independent verification outputs, and
    README/ROADMAP wording that treats SeaEvo strategy-space evolution as
    missing search-memory architecture evidence rather than implemented
    LibreEvolve support.

- [ ] Reproduce EMO-STA multi-task program-discovery evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2605.22613`, submitted May 21, 2026, is
    titled `Evolutionary Multi-Task Optimization for LLM-Guided Program
    Discovery` and the arXiv page links a Creative Commons license. Its
    abstract says recent LLM-guided evolutionary search usually optimizes each
    task independently even when related tasks share reusable structure. It
    introduces Evolutionary Multi-Task Optimization (EMO) and EMO-STA
    (Shared-Then-Adapt), a two-stage framework that first evolves a shared
    archive of executable programs across a task family, then adapts selected
    shared candidates to each target task. It compares warm-starting from the
    shared archive, adapting the best average shared program, and adapting the
    best shared program per target task. Across eight task families spanning
    continuous optimization, geometric construction, modeling, and algorithmic
    optimization, it reports improvement over matched-compute single-task
    evolution in most settings, with STA Best-Local strongest in-distribution
    and STA Best-Shared robust for unseen-task transfer. It also reports that
    roughly balanced shared/adaptation budgets are often optimal and that
    shared evolution can reduce low-evidence overfitting on ARC and time-series
    feature-engineering tasks.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2605.22613`. Existing LibreEvolve island, MAP-Elites,
    archive-restore, parent-sampling, LEVI, SeaEvo, PACEvolve, benchmark-
    hardening, and transfer TODOs do not reproduce family-level task schemas,
    shared executable-program archives, shared-then-adapt control flow,
    warm-start adaptation policies, Best-Average/Best-Local/Best-Shared
    selection rules, matched-compute single-task baselines, shared-versus-
    adaptation budget sweeps, unseen-task transfer metrics, or low-evidence
    overfitting mitigation for ARC and time-series feature-engineering tasks.
  - Required result: add reproduction-grade evidence for `2605.22613`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, FunSearch, OpenEvolve, LEVI,
    SeaEvo, and LibreEvolve, task-family schema, shared-archive data model,
    executable-program compatibility contract across tasks, shared-evolution
    stage telemetry, adaptation-stage telemetry, warm-start and selected-
    candidate adaptation policies, Best-Average/Best-Local/Best-Shared
    selection records, budget-allocation schedules, matched-compute
    single-task baseline identities, eight task-family benchmark metadata,
    in-distribution and unseen-task transfer metrics, low-evidence overfitting
    diagnostics, ARC and time-series feature-engineering records, independent
    verification outputs, and README/ROADMAP wording that treats EMO-STA
    multi-task program discovery as missing shared-evolution evidence rather
    than implemented LibreEvolve support.

- [ ] Reproduce RankEvolve retrieval-algorithm discovery evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2602.16932`, submitted February 18, 2026, is
    titled `RankEvolve: Automating the Discovery of Retrieval Algorithms via
    LLM-Driven Evolution`. Its abstract says BM25 and query likelihood with
    Dirichlet smoothing remain strong lexical first-stage rankers, but
    improvements often rely on parameter tuning and human intuition.
    RankEvolve is described as a program-evolution setup based on AlphaEvolve
    where candidate ranking algorithms are executable code that is mutated,
    recombined, and selected by retrieval performance across 12 IR datasets
    from BEIR and BRIGHT. It starts from BM25 and query-likelihood seed
    programs and reports novel algorithms with transfer to the full BEIR and
    BRIGHT benchmarks plus TREC DL 2019 and 2020.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2602.16932`. Existing LibreEvolve DeepResearch retrieval,
    proposal retrieval, archive ranking, systems-result ranking-only safety,
    benchmark-hardening, and AlphaEvolve paper TODOs do not reproduce
    executable lexical retrieval algorithm candidates, first-stage ranker
    evaluator contracts, BM25/query-likelihood seed programs, BEIR/BRIGHT
    training and transfer splits, TREC DL transfer checks, IR metric suites,
    per-query ranking traces, or retrieval-specific recombination and
    selection evidence.
  - Required result: add reproduction-grade evidence for `2602.16932`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, FunSearch, OpenEvolve, and
    LibreEvolve, executable ranker interface, BM25 and query-likelihood seed
    program records, evaluator integration for lexical retrieval, BEIR and
    BRIGHT dataset identities/splits, TREC DL 2019/2020 transfer metadata,
    ranking metric definitions, per-candidate validation and performance
    traces, mutation/recombination prompt records, train-versus-transfer
    result tables, baseline comparison identities, independent verification
    outputs, and README/ROADMAP wording that treats RankEvolve-style retrieval
    algorithm discovery as missing IR benchmark evidence rather than
    implemented LibreEvolve support.

- [ ] Reproduce AdaEvolve adaptive scheduler evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2602.20133`, submitted February 23, 2026, is
    titled `AdaEvolve: Adaptive LLM Driven Zeroth-Order Optimization`. Its
    abstract says automated program generation is shifting from one-shot
    generation to inference-time search where LLMs act as semantic mutation
    operators inside evolutionary loops, but current systems rely on static
    schedules that miss non-stationary search dynamics and waste compute on
    stagnating populations. AdaEvolve reformulates LLM-driven evolution as a
    hierarchical adaptive optimization problem using an accumulated
    improvement signal across Local Adaptation, Global Adaptation, and
    Meta-Guidance. The source says Local Adaptation changes exploration
    intensity within a candidate population, Global Adaptation routes global
    budget through bandit-based scheduling across populations, and
    Meta-Guidance generates new tactics when progress stalls. It reports
    outperforming open-source baselines across 185 open-ended optimization
    problems spanning combinatorial, systems-optimization, and algorithm-design
    tasks.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2602.20133`. Existing LibreEvolve UCB-style LLM ensemble,
    parent sampling, island migration, archive restore, LEVI cost-routing,
    SeaEvo strategy-space, PACEvolve consistency, EvoX meta-evolution, and
    runtime budget TODOs do not reproduce accumulated-improvement signals,
    dynamic exploration-intensity control within populations, bandit-routed
    global compute allocation across solution populations, stalled-progress
    tactic generation, identical-hyperparameter cross-task claims, or the
    185-problem benchmark matrix.
  - Required result: add reproduction-grade evidence for `2602.20133`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, OpenEvolve, EvoX, LEVI, SeaEvo,
    PACEvolve, and LibreEvolve, accumulated-improvement signal definition,
    per-population progress telemetry, Local Adaptation exploration-intensity
    policy, Global Adaptation bandit scheduler, Meta-Guidance tactic-generation
    prompts and outputs, stagnation detectors, global budget-routing traces,
    same-hyperparameter configuration records, 185-task benchmark metadata,
    combinatorial/systems/algorithm-design task-family results, baseline
    identities, ablation outputs for each adaptation level, independent
    verification outputs, and README/ROADMAP wording that treats AdaEvolve-
    style adaptive scheduling as missing controller evidence rather than
    implemented LibreEvolve support.

- [ ] Reproduce runtime-enriched CodeEvolve multi-language optimization evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2605.04677`, submitted May 6, 2026, is
    titled `CodeEvolve: LLM-Driven Evolutionary Optimization with
    Runtime-Enriched Target Selection for Multi-Language Code Enhancement`.
    Its abstract says this CodeEvolve extends OpenEvolve with runtime-guided
    target selection, Monte Carlo Tree Search (MCTS), automated code
    refinement, and language-specific evaluation pipelines for Java and
    Salesforce Apex. It uses Java Flight Recorder (JFR) profiles to build
    weighted component graphs and pick optimization targets that account for
    most execution cost, then evaluates candidate edits with build validation,
    unit tests, performance checks, static analysis, and LLM-based review while
    retaining only functionality-preserving variants. It reports a 15.22x
    average speedup across seven hotspot functions in a large enterprise Java
    codebase and an Apex ablation where the full MCTS-augmented configuration
    produces 19.5 valid programs out of 20 on average.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2605.04677`. Existing LibreEvolve CodeEvolve coverage is for
    arXiv `2510.14150` and its islands/crossover/meta-prompting benchmark
    boundary; it does not reproduce runtime-profile target selection, JFR
    weighted component graphs, hotspot-function prioritization, MCTS search
    over edits, automated refinement loops, Java or Salesforce Apex evaluation
    pipelines, LLM-based review gates, multi-language build/static/performance
    validation, enterprise Java speedup evidence, or Apex valid-program
    ablation rows.
  - Required result: add reproduction-grade evidence for `2605.04677`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, OpenEvolve, the `2510.14150`
    CodeEvolve paper, and LibreEvolve, runtime-profile ingestion schema, JFR
    profile metadata, weighted component graph construction, hotspot target
    selection policy, MCTS state/action/reward records, automated refinement
    loop telemetry, Java and Salesforce Apex runner contracts, build/unit/
    performance/static-analysis/LLM-review gate outputs, functionality-
    preservation evidence, enterprise Java benchmark metadata, seven-hotspot
    speedup tables, Apex optimization benchmark metadata, ablation outputs for
    search/filtering/refinement, independent verification outputs, and README/
    ROADMAP wording that treats runtime-enriched multi-language CodeEvolve
    support as missing systems-optimization evidence rather than implemented
    LibreEvolve support.

- [ ] Reproduce MappingEvolve technology-mapping code-evolution evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2604.26591`, submitted April 29, 2026, is
    titled `MappingEvolve: LLM-Driven Code Evolution for Technology Mapping`.
    Its abstract says technology mapping is a critical stage in logic
    synthesis and that MappingEvolve directly evolves technology-mapping code
    rather than only generating optimization scripts. The method abstracts the
    mapping process into distinct optimization operators and uses a
    hierarchical agent architecture with a Planner, Evolver, and Evaluator to
    guide evolutionary search. It reports 10.04% area reduction versus ABC and
    7.93% versus mockturtle, 46.6%-96.0% `S_overall` improvement on EPFL
    benchmarks, explicit area-delay trade-off navigation, and linked code/data
    at `https://github.com/Flians/MappingEvolve`.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2604.26591`. Existing LibreEvolve AlphaEvolve, CodeEvolve,
    runtime-CodeEvolve, systems-result, benchmark-hardening, multi-objective,
    and evaluator-contract TODOs do not reproduce technology-mapping problem
    schemas, logic-synthesis toolchain integration, planner/evolver/evaluator
    agent roles, optimization-operator abstractions, area-delay trade-off
    objectives, ABC or mockturtle baselines, EPFL benchmark fixtures, cec
    equivalence-check evidence, or linked MappingEvolve code/data
    reproducibility.
  - Required result: add reproduction-grade evidence for `2604.26591`:
    title/authors/arXiv version/date, source license, related DOI,
    code/data URL status and license, relation to AlphaEvolve, OpenEvolve,
    CodeEvolve, runtime-CodeEvolve, and LibreEvolve, technology-mapping task
    schema, optimization-operator taxonomy, Planner/Evolver/Evaluator
    contracts, prompt and edit traces, logic-synthesis runner environment,
    ABC and mockturtle baseline command records, EPFL benchmark metadata,
    area/delay/`S_overall` metric definitions, cec equivalence-check outputs,
    area-delay trade-off records, model-generalization runs, direct-evolution
    baseline comparisons, linked-code audit, independent verification outputs,
    and README/ROADMAP wording that treats MappingEvolve-style
    technology-mapping code evolution as missing logic-synthesis evidence
    rather than implemented LibreEvolve support.

- [ ] Reproduce EvoControl interpretable control-policy evolution evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2601.06845`, submitted January 11, 2026, is
    titled `Code Evolution for Control: Synthesizing Policies via LLM-Driven
    Evolutionary Search`. Its abstract says reinforcement-learning control
    policies can have high sample complexity, reward-shaping difficulties, and
    opaque neural network policies that are hard to interpret or verify. The
    paper treats policy synthesis as code evolution, uses EvoToolkit to combine
    LLM-driven evolution with customizable fitness evaluation, and evolves
    populations of executable candidate policy programs. The HTML paper reports
    LunarLander-v3 experiments comparing FunSearch, EoH, and EvoEngineer
    strategies against random and PPO baselines; EvoEngineer+ reaches a 70%
    landing success rate versus PPO's 60% at roughly equivalent environment
    interactions, produces a 59-line inspectable Python policy, and preserves a
    lower average-reward trade-off that the paper frames as relevant to
    safety-critical success-rate objectives. The arXiv page links code at
    `https://github.com/pgg3/EvoControl`.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2601.06845`. Existing LibreEvolve AlphaEvolve, FunSearch,
    EoH, EvoEngineer, systems-result, benchmark-hardening, policy, and
    evaluator-contract TODOs do not reproduce executable control-policy
    candidate schemas, Gymnasium LunarLander-v3 fixtures, state/action/reward
    contracts, sandboxed policy execution, episode-statistics feedback,
    failure-mode prompt context, PPO/random baselines, equivalent environment
    interaction budgets, landing-success metrics, policy-size/complexity
    interpretability metrics, or formal-verification readiness for evolved
    autonomous-system policies.
  - Required result: add reproduction-grade evidence for `2601.06845`:
    title/authors/arXiv version/date, source license, linked-code URL/status
    and license, relation to AlphaEvolve, FunSearch, EoH, EvoEngineer,
    EvoToolkit, and LibreEvolve, executable policy interface, Gymnasium
    LunarLander-v3 environment metadata, state/action/reward schema,
    sandboxed policy-runner constraints, population and generation settings,
    LLM call and environment-step budgets, mutation/crossover/operator prompt
    records, episode-statistics and failure-mode feedback artifacts, PPO and
    random baseline identities, average-reward and landing-success metric
    definitions, policy LoC/cyclomatic-complexity records, 59-line policy
    artifact, cost and sample-efficiency comparisons, safety-critical
    interpretability/verification criteria, independent verification outputs,
    and README/ROADMAP wording that treats EvoControl-style interpretable
    control-policy evolution as missing autonomous-systems benchmark evidence
    rather than implemented LibreEvolve support.

- [ ] Reproduce AutoICE verifiable C-code evolution evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2512.07501`, submitted December 8, 2025, is
    titled `AutoICE: Automatically Synthesizing Verifiable C Code via
    LLM-driven Evolution`. Its abstract says verifiable-code synthesis from
    natural-language requirements can lower the barrier to formal methods, but
    existing approaches suffer from syntactic/semantic errors and often miss
    implicit knowledge. AutoICE is described as an LLM-driven evolutionary
    search system for synthesizing verifiable C code. It introduces diverse
    individual initialization and collaborative crossover to support diverse
    iterative updates and reduce single-agent error propagation, plus
    self-reflective mutation to discover implicit knowledge. The paper reports
    90.36% verification success, and 88.33% verification success on a
    developer-friendly dataset variant versus a 65% SOTA baseline.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2512.07501`. Existing LibreEvolve AlphaEvolve, FunSearch,
    CodeEvolve, EvoControl, benchmark-hardening, evaluator-contract,
    systems-verification, and formal-verification-adjacent TODOs do not
    reproduce natural-language-to-verifiable-C problem schemas, logical
    verifier integration, candidate C population records, diverse individual
    initialization, collaborative crossover, self-reflective mutation, implicit
    knowledge discovery traces, syntax/semantic error propagation diagnostics,
    verification-success metrics, developer-friendly dataset variants, or
    SOTA verifiable-code synthesis baselines.
  - Required result: add reproduction-grade evidence for `2512.07501`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, FunSearch, CodeEvolve, EvoControl,
    AutoICE, and LibreEvolve, natural-language requirement schema,
    verifiable-C candidate interface, verifier toolchain identity, logical
    specification format, candidate-population and generation telemetry,
    diverse-initialization records, collaborative-crossover prompts and
    outputs, self-reflective mutation prompts and outputs, implicit-knowledge
    evidence, syntax/semantic error diagnostics, verification result logs,
    benchmark and developer-friendly dataset metadata, SOTA baseline identities,
    90.36% and 88.33% verification-success reproduction tables, failure-case
    taxonomy, independent verification outputs, and README/ROADMAP wording that
    treats AutoICE-style verifier-integrated C-code evolution as missing
    formal-methods evidence rather than implemented LibreEvolve support.

- [ ] Reproduce CogAlpha financial-alpha code-evolution evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2511.18850`, submitted November 24, 2025 and
    last revised April 20, 2026, is titled `Cognitive Alpha Mining via
    LLM-Driven Code-Based Evolution`. Its abstract says discovering predictive
    financial alphas from high-dimensional, low-signal data remains difficult:
    neural models can be opaque and fragile, and symbolic/formula methods can
    become redundant, economically ungrounded, and weakly generalizing.
    CogAlpha combines code-level alpha representation with LLM-driven reasoning
    and evolutionary search. It treats LLMs as adaptive cognitive agents that
    refine, mutate, and recombine alpha candidates through multi-stage prompts
    and financial feedback, reporting experiments on five stock datasets from
    three stock markets with stronger predictive accuracy, robustness, and
    generalization than existing methods.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2511.18850`. Existing LibreEvolve AlphaEvolve, FunSearch,
    DeepResearch, proposal-hypothesis, finance-impact, benchmark-portfolio,
    evaluator-contract, and multi-objective TODOs do not reproduce financial
    alpha candidate code schemas, OHLCV/data-market fixtures, multi-stage
    reasoning prompts, financial-feedback loops, alpha mutation/recombination
    operators, economic-grounding checks, alpha quality metrics, robustness and
    generalization tests across stock markets, or source-code availability
    tracking for CogAlpha.
  - Required result: add reproduction-grade evidence for `2511.18850`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, FunSearch, DeepResearch, and
    LibreEvolve, financial-alpha candidate interface, code-level alpha schema,
    stock-market and dataset metadata, OHLCV/feature input contract,
    multi-stage prompt templates, financial-feedback records, mutation and
    recombination traces, quality-checker outputs, economic-interpretability
    criteria, alpha metric definitions, predictive-accuracy/robustness/
    generalization tables, baseline identities, leakage and backtest-safety
    checks, source-code release status, independent verification outputs, and
    README/ROADMAP wording that treats CogAlpha-style financial alpha mining as
    missing domain-benchmark evidence rather than implemented LibreEvolve
    support.

- [ ] Reproduce EvolVE Verilog-generation and optimization evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2601.18067`, submitted January 26, 2026, is
    titled `EvolVE: Evolutionary Search for LLM-based Verilog Generation and
    Optimization`. Its abstract says Verilog design requires domain expertise
    and that LLMs struggle with hardware formal logic and concurrency. EvolVE
    analyzes multiple evolution strategies on chip-design tasks, reporting that
    Monte Carlo Tree Search (MCTS) is strongest for functional correctness and
    Idea-Guided Refinement (IGR) is strongest for optimization, while
    Structured Testbench Generation (STG) accelerates the evolutionary process.
    The paper introduces IC-RTL from National Integrated Circuit Contest
    industry-scale problems, reports 98.1% on VerilogEval v2 and 92% on RTLLM
    v2, and says IC-RTL reduces Power, Performance, Area (PPA) product by up
    to 66% on Huffman Coding and 17% geometric mean across all problems versus
    contest-participant references. The IC-RTL benchmark source is linked at
    `https://github.com/weiber2002/ICRTL`.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2601.18067`. Existing LibreEvolve hardware RTL/EDA TODOs cover
    AlphaEvolve TPU rewrite artifact boundaries and do not reproduce
    specification-to-Verilog candidate schemas, VerilogEval v2 or RTLLM v2
    fixtures, IC-RTL benchmark records, National Integrated Circuit Contest
    provenance, MCTS versus IGR evolution-strategy comparisons, Structured
    Testbench Generation, hardware-concurrency correctness checks, PPA-product
    optimization, Huffman Coding benchmark details, or source-linked IC-RTL
    independent verification.
  - Required result: add reproduction-grade evidence for `2601.18067`:
    title/authors/arXiv version/date, source license, IC-RTL code URL/status
    and license, relation to AlphaEvolve, OpenEvolve, hardware RTL/EDA
    AlphaEvolve boundary records, and LibreEvolve, Verilog candidate interface,
    HDL runner and simulator/synthesis toolchain identity, MCTS state/action/
    reward records, IGR prompt and refinement traces, STG testbench-generation
    artifacts, VerilogEval v2 and RTLLM v2 benchmark metadata, IC-RTL task
    metadata and contest provenance, functional-correctness metrics,
    concurrency/formal-logic checks, PPA metric definitions and tool outputs,
    Huffman Coding and geometric-mean result tables, reference-implementation
    identities, independent verification outputs, and README/ROADMAP wording
    that treats EvolVE-style Verilog generation and optimization as missing
    hardware benchmark evidence rather than implemented LibreEvolve support.

- [ ] Reproduce TurboEvolve sample-efficiency and robustness evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2604.18607`, submitted April 12, 2026, is
    titled `TurboEvolve: Towards Fast and Robust LLM-Driven Program
    Evolution`. Its abstract says LLM-driven program evolution can discover
    high-quality programs, but cost and run-to-run variance hinder reliable
    progress. TurboEvolve is described as a multi-island evolutionary framework
    that improves sample efficiency and robustness under fixed evaluation
    budgets. It introduces verbalized Sampling, where an LLM emits `K` diverse
    candidates with explicit self-assigned sampling weights, plus an online
    scheduler that adapts `K` to expand exploration under stagnation and reduce
    overhead during steady progress. It also introduces seed-pool injection,
    clustering seeds and assigning them across islands with controlled
    perturbations and elitist preservation to balance diversity and refinement.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2604.18607`. Existing LibreEvolve island, parent-sampling,
    sample-efficiency, initial-pool-divergence, AdaEvolve, LEVI, PACEvolve,
    SeaEvo, and MLEvolve TODOs do not reproduce verbalized multi-offspring
    generation, self-assigned sampling weights, adaptive offspring-count `K`
    scheduling, stagnation-triggered exploration expansion, overhead-reducing
    steady-progress policies, clustered seed-pool injection, controlled seed
    perturbation, elitist seed preservation, run-to-run robustness metrics, or
    fixed-evaluation-budget comparisons for TurboEvolve.
  - Required result: add reproduction-grade evidence for `2604.18607`:
    title/authors/arXiv version/date, source license, code/artifact
    availability, relation to AlphaEvolve, OpenEvolve, AdaEvolve, LEVI,
    PACEvolve, SeaEvo, MLEvolve, and LibreEvolve, multi-island configuration,
    verbalized Sampling prompt schema, candidate-weight output parser,
    per-offspring lineage and weight records, adaptive-`K` scheduler state,
    stagnation and steady-progress detectors, scheduler ablation traces,
    seed-clustering method, seed-to-island assignment records, controlled
    perturbation prompts, elitist-preservation policy, fixed-budget benchmark
    metadata, sample-efficiency and robustness metric definitions, run-to-run
    variance tables, best-known-solution improvement records, independent
    verification outputs, and README/ROADMAP wording that treats
    TurboEvolve-style adaptive multi-offspring island search as missing
    robustness evidence rather than implemented LibreEvolve support.

- [ ] Reproduce DBPlanBench physical-query-plan optimization evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2602.10387`, submitted February 11, 2026 and
    last revised June 2, 2026, is titled `Test-Time Optimization of Physical
    Query Plans with LLMs`. Its abstract says cost-based query optimizers
    estimate runtime, memory, and I/O with heuristics and statistical models
    that can miss semantic correlations in queries and schemas. The paper
    introduces DBPlanBench, a DataFusion harness that serializes physical plans
    compactly and applies LLM-proposed edits as JSON patches. It instantiates a
    test-time optimization workflow where an LLM proposes localized physical
    plan edits and evolutionary search refines candidates across iterations,
    focusing on OLAP join reordering and join-side selection. It reports median
    speedups of 1.10x-1.12x on TPC-H and 1.05x-1.07x on TPC-DS, with some
    plans reaching 4.78x, and shows small-scale optimizations transferring to
    larger scale factors. The arXiv page links code on GitHub.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2602.10387`. Existing LibreEvolve database, process-exhibit,
    systems-result, optimizer, sample-efficiency, AlphaEvolve, LEVI,
    TurboEvolve, and benchmark-hardening TODOs do not reproduce physical
    query-plan candidates, DataFusion plan serialization, JSON-patch edit
    contracts, plan validity checks, OLAP execution harnesses, join reordering
    and join-side selection operators, TPC-H/TPC-DS fixtures, small-to-large
    transfer experiments, or database-cost-model comparison evidence.
  - Required result: add reproduction-grade evidence for `2602.10387`:
    title/authors/arXiv version/date, source license, linked-code URL/status
    and license, relation to AlphaEvolve, LEVI, TurboEvolve, and LibreEvolve,
    DataFusion version and patching surface, physical-plan serialization
    schema, JSON-patch candidate interface, plan validity and rollback policy,
    OLAP query fixture metadata, TPC-H and TPC-DS scale factors, join reorder
    and join-side selection operator taxonomy, execution-cost measurement
    protocol, runtime/memory/I/O metric records, evolutionary search settings,
    small-to-large transfer records, industrial optimizer baseline identities,
    speedup tables including medians and outliers, independent verification
    outputs, and README/ROADMAP wording that treats DBPlanBench-style physical
    query-plan evolution as missing database-systems benchmark evidence rather
    than implemented LibreEvolve support.

- [ ] Reproduce mutation-convergence diagnostics beyond paper coverage.
  - Paper/source evidence: arXiv `2606.05408`, submitted June 3, 2026, is
    titled `Mutation Without Variation: Convergence Dynamics in LLM-Driven
    Program Evolution`. Its abstract asks whether repeated LLM mutation explores
    new forms or circles back to the same ones. The study analyzes LLM-driven
    mutation chains without selection pressure in a domain-specific language
    while varying prompt design, model family, and stochastic replication. It
    reports that LLM mutations converge toward restricted attractor regions:
    structurally, 87% of chains have more than 93% of mutations revisiting a
    previously seen structural form, with short cycles and self-loops
    dominating the transition graph. It contrasts this with a classical GP
    subtree mutation operator and frames structural homogeneity as a risk for
    open-ended LLM-driven program evolution. The arXiv page links source code
    on GitHub.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.05408`. Existing LibreEvolve diversity, MAP-Elites,
    mutation-mode, parent-sampling, proposal-hypothesis, SeaEvo, TurboEvolve,
    and sample-efficiency TODOs do not reproduce mutation-chain experiments
    without selection pressure, structural-form canonicalization, attractor
    region detection, transition-graph cycle analysis, short-cycle/self-loop
    metrics, prompt/model/stochastic replication sweeps, classical GP subtree
    mutation baselines, or open-ended-exploration homogeneity diagnostics.
  - Required result: add reproduction-grade evidence for `2606.05408`:
    title/authors/arXiv version/date, source license, linked-code URL/status
    and license, relation to AlphaEvolve, MAP-Elites, SeaEvo, TurboEvolve, and
    LibreEvolve, domain-specific language grammar, mutation-chain generation
    protocol, no-selection-pressure run configuration, prompt and model-family
    sweep metadata, stochastic replication seeds, structural-form
    canonicalization method, terminal-substitution versus structural-change
    metrics, attractor-region records, transition-graph and cycle-analysis
    outputs, short-cycle/self-loop statistics, classical GP subtree mutation
    baseline implementation, structural-homogeneity thresholds, open-ended
    exploration risk criteria, independent verification outputs, and README/
    ROADMAP wording that treats mutation-convergence diagnostics as missing
    diversity evidence rather than implemented LibreEvolve support.

- [ ] Reproduce LEVI cost-aware search-architecture evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2605.09764`, submitted May 10, 2026, is
    titled `LEVI: Stronger Search Architectures Can Substitute for Larger LLMs
    in Evolutionary Search`. Its abstract says AlphaEvolve-style LLM-guided
    evolutionary methods work across math, systems research, and algorithmic
    discovery but are expensive because search allocation often fails to
    preserve solution diversity, uses frontier models blindly for local edits,
    and evaluates redundant examples. LEVI proposes a harness-first framework
    with a diversity-preserving solution database, smarter mutation routing
    between large and small LLMs, and rank-preserving proxy benchmarks; it
    reports systems-research wins at 3.3x-6.7x lower budget, one 35x
    lower-cost match, and prompt-optimization results at less than half GEPA's
    rollout budget. The arXiv page links code at `https://github.com/ttanv/levi`.
  - Current gap: the paper manifest, paper index, row-identity manifest, and
    TODO coverage now include `2605.09764`, cached locally as
    `papers/2605.09764__LEVI.pdf` with byte count `1568204` and SHA-256
    `66cb851e38702e08213cc455f3c457289b2297be9b413be6372d21da5f0cfc58`.
    Existing rows still do not capture LEVI-style diversity preservation,
    cost-aware mutation routing, proxy-benchmark rank preservation,
    provider-budget accounting, or systems/prompt optimization cost
    comparisons.
  - Required result: add reproduction-grade evidence for `2605.09764`:
    source-license metadata, linked-code URL/status, relation to AlphaEvolve
    and LibreEvolve archive/ensemble behavior, diversity metrics,
    solution-database invariants, mutation-router policy, large/small model
    assignment traces, proxy-benchmark construction and rank-correlation
    evidence, rollout and provider-cost accounting, systems/prompt benchmark
    taxonomy, baseline method identities, code/artifact reproducibility status,
    and independent verification outputs.

- [ ] Reproduce PACEvolve long-horizon consistency evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2601.10657`, submitted January 15, 2026 and
    last revised January 16, 2026, is titled `PACEvolve: Enabling Long-Horizon
    Progress-Aware Consistent Evolution`. Its abstract says LLM-in-the-loop
    evolutionary systems lack systematic process management and identifies
    context pollution, mode collapse, and weak collaboration as failure
    modes. PACEvolve combines hierarchical context management with pruning,
    momentum-based backtracking, and a self-adaptive sampling policy that
    unifies backtracking and crossover, reporting state-of-the-art LLM-SR and
    KernelBench results plus record-surpassing Modded NanoGPT solutions.
  - Current gap: the paper manifest, paper index, row-identity manifest, and
    TODO coverage now include `2601.10657`, cached locally as
    `papers/2601.10657__PACEvolve.pdf` with byte count `2691222` and
    SHA-256
    `fdf49e2e18905a5a836faabd43a57391faf30b4650ac6569c77f7a2469e92d61`.
    Existing rows still do not capture PACEvolve's context-pollution controls,
    hierarchical pruning, momentum-backtracking state, crossover/backtracking
    coordination, or LLM-SR/KernelBench/Modded-NanoGPT evidence.
  - Required result: add reproduction-grade evidence for `2601.10657`:
    source-license metadata, relation to AlphaEvolve and LibreEvolve
    prompt/search policy, context-pollution and mode-collapse metrics,
    hierarchical context schema, pruning and momentum-backtracking artifacts,
    adaptive sampling and crossover/backtracking coordination records,
    trajectory-collaboration diagnostics, LLM-SR/KernelBench/Modded-NanoGPT
    benchmark metadata, baseline method identities, code/artifact availability
    if any, and independent verification outputs.

- [ ] Reproduce FlashEvolve asynchronous-stage evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2605.08520`, submitted May 8, 2026, is
    titled `FlashEvolve: Accelerating Agent Self-Evolution with Asynchronous
    Stage Orchestration`. Its abstract says synchronized stage execution and
    imbalance inside LLM-heavy stages create wall-clock bottlenecks in
    LLM-based evolution. FlashEvolve replaces synchronized execution with
    asynchronous workers and queues so different stages and evolution steps
    overlap; tracks artifact versions; updates, discards, or patches stale
    artifacts; treats language-space staleness as inspectable and repairable;
    adds speculative stage completion and adaptive workflow control; and
    reports 3.5x local-vLLM and 4.9x API proposal-throughput gains over
    synchronous GEPA, with the design also applying to ACE and Meta-Harness.
  - Current gap: the paper cache, paper index, row identity, and TODO coverage
    now include `2605.08520`, cached locally as
    `papers/2605.08520__FlashEvolve.pdf` with byte count `627860` and SHA-256
    `668cb80b2c72e1e2c9a296df9c35f4965f79f03b095310e738c012b6106b0e08`.
    Existing evidence still does not reproduce asynchronous stage
    orchestration, queue overlap, artifact versioning, stale-language-artifact
    repair, speculative completion, or throughput/token-efficiency
    measurements.
  - Required result: add reproduction-grade evidence beyond paper coverage for
    `2605.08520`: title/authors/arXiv version/date, source license, relation
    to AlphaEvolve and LibreEvolve's synchronous loop, worker/queue schema,
    stage-overlap traces, artifact-version lineage, stale-artifact
    update/discard/patch policies, reflective patch artifacts,
    speculative-completion metrics, adaptive workflow telemetry,
    throughput/token-efficiency records, GEPA/vLLM/API baseline identities,
    ACE/Meta-Harness applicability status, code/artifact availability if any,
    and README/ROADMAP wording that treats FlashEvolve as missing
    implementation evidence rather than implemented LibreEvolve support.

- [ ] Reproduce evolutionary-agent trace-diagnostics evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2605.20086`, submitted May 25, 2026, is
    titled `What Do Evolutionary Coding Agents Evolve?`. Its abstract says
    aggregate benchmark scores hide how evolutionary coding agents improve
    programs, whether improvements reflect structural innovation or
    overfitting, and how search behavior changes across tasks. It introduces
    EvoTrace for annotation of edit types, dependencies, and fitness
    trajectories, and EvoReplay for interventions on search traces, reporting
    recurring cycling and overfitting, task-dependent constant tuning versus
    new logic, and sensitivity to population structure and prompt content
    across AlphaEvolve-style agents such as AlphaEvolve, OpenEvolve, and
    FunSearch.
  - Current gap: the paper cache, paper index, row identity, and TODO coverage
    now include `2605.20086`, cached locally as
    `papers/2605.20086__Evolutionary_Coding_Agents.pdf` with byte count
    `2273394` and SHA-256
    `b8f592bd68429b4c5f7cee2878a316941acf3cdf80215a0d78c08c25a73722f3`.
    Existing evidence still does not reproduce mechanistic trace annotation,
    replay interventions, cycling/overfitting diagnostics, structural-
    innovation labels, or prompt/population sensitivity evidence.
  - Required result: add reproduction-grade evidence beyond paper coverage for
    `2605.20086`: title/authors/arXiv version/date, source license, relation
    to AlphaEvolve and LibreEvolve run artifacts, EvoTrace edit-type taxonomy,
    dependency extraction, fitness-trajectory labels, EvoReplay-intervention
    schema, cycling and overfitting diagnostics, constant-tuning versus
    new-logic classification, prompt/population sensitivity metadata,
    benchmark/task taxonomy, baseline-agent identities, code/artifact
    availability if any, and README/ROADMAP wording that treats mechanistic
    trace diagnostics as missing implementation evidence rather than
    implemented LibreEvolve support.

- [ ] Reproduce Zarankiewicz reinforced-search evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2605.01120`, submitted May 1, 2026 and last
    revised May 7, 2026, is titled `New Bounds for Zarankiewicz Numbers via
    Reinforced LLM Evolutionary Search`. Its abstract says OpenEvolve, an
    open-source evolutionary algorithm based on LLMs, produced the first exact
    values for `Z(11,21,3,3)=116`, `Z(11,22,3,3)=121`, and
    `Z(12,22,3,3)=132`; lower bounds for 41 more Zarankiewicz numbers; and
    four matched closed cases. The paper also reports generated construction
    algorithms, implementation details, and computational costs under `$30`
    per Zarankiewicz parameter combination.
  - Current gap: the paper cache, paper index, row identity, and TODO coverage
    now include `2605.01120`, cached locally as
    `papers/2605.01120__Zarankiewicz_Reinforced_Search.pdf` with byte count
    `784207` and SHA-256
    `bebb4ec9e8a114800515c1018b76d9a19c4467edcc1f168bc10be68b0d0ad4f0`.
    Existing evidence still does not reproduce Zarankiewicz parameter
    manifests, bipartite-graph construction artifacts, `K_{s,t}`-free
    validation, exact/lower-bound tables, generated construction algorithms,
    cost records, or OpenEvolve-to-LibreEvolve application boundaries.
  - Required result: add reproduction-grade evidence beyond paper coverage for
    `2605.01120`: title/authors/arXiv version/date, source license, relation
    to AlphaEvolve/OpenEvolve and LibreEvolve, Zarankiewicz parameter schema,
    graph representation, `K_{s,t}`-free verifier metadata, exact-value and
    lower-bound records, generated construction algorithm artifacts,
    proof/check status, computational-cost records, upper-bound and baseline
    references, code/artifact availability if any, reproducibility status, and
    README/ROADMAP wording that treats the paper as missing application
    evidence rather than implemented LibreEvolve support.

- [ ] Reproduce EinsteinArena collective-discovery evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.10402`, submitted June 9, 2026, is
    titled `Harnessing the Collective Intelligence of AI Agents in the Wild
    for New Discoveries`. Its abstract presents EinsteinArena as an
    agent-native platform for open distributed research and discovery where
    agents work on live open problems with solid verifiers, public
    leaderboards, and problem-specific discussion forums. It reports 12 new
    state-of-the-art results as of May 2026, including improving the
    dimension-11 kissing-number lower bound from 593 to 604 through a sequence
    of submissions, public discussion, verifier refinement, and subsequent
    agent-to-agent borrowing of ideas. The paper positions AlphaEvolve as a
    prior system for evolving programs on mathematics and algorithm-design
    problems, but moves the evidence boundary from isolated search runs to
    decentralized collective agent interaction.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.10402`. Existing CORAL and evolutionary-agent diagnostic
    rows do not capture EinsteinArena's public leaderboard semantics,
    problem-specific discussion traces, verifier-refinement history,
    cross-agent idea-borrowing lineage, open-platform governance, or live
    collective-discovery result provenance.
  - Required result: add reproduction-grade evidence for `2606.10402`:
    title/authors/arXiv version/date, source license, relation to
    AlphaEvolve, TTT-Discover, CORAL, and LibreEvolve's current isolated run
    model, open-problem registry schema, verifier-audit and refinement
    records, leaderboard submission/event schema, discussion-thread artifact
    provenance, agent identity and permission boundaries, idea-borrowing and
    lineage/fingerprint metadata, kissing-number and second-autocorrelation
    task records, 12-SOTA-result table provenance, invalid-submission checks,
    code/platform availability status, independent verification outputs, and
    README/ROADMAP wording that treats EinsteinArena-style open collective
    discovery as missing paper evidence rather than implemented LibreEvolve
    support.

- [ ] Reproduce EurekAgent environment-engineering evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.13662`, submitted June 11, 2026, is
    titled `EurekAgent: Agent Environment Engineering is All You Need For
    Autonomous Scientific Discovery`. Its abstract argues that the bottleneck
    for autonomous scientific discovery is shifting from prescribed agent
    workflows to engineered environments: resources, constraints, and
    interfaces that amplify open-ended exploration, systematic artifact
    management, and inter-agent collaboration while suppressing reward
    hacking and high-friction human oversight. EurekAgent engineers
    permissions for bounded execution and isolated evaluation, filesystem and
    Git-based artifact collaboration, budget-aware exploration, and
    human-in-the-loop supervision. It reports new state-of-the-art results on
    mathematics, kernel engineering, and machine-learning tasks, including a
    new 26-circle-packing result discovered for less than `$11` in total API
    cost. The paper's related-work framing explicitly contrasts this
    environment-first approach with evolutionary systems such as AlphaEvolve
    that prescribe population, mutation, and selection workflows.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.13662`. Existing 26-circle TODOs only preserve the
    checked-in smoke fixture and AlphaEvolve Appendix B claim boundary, and
    existing human-in-the-loop/Fault2Flow rows do not cover EurekAgent's
    permission sandboxing, isolated-evaluation environment, Git collaboration
    substrate, budget-aware exploration controls, environment-mediated
    artifact management, or cross-domain math/kernel/MLE benchmark evidence.
  - Required result: add reproduction-grade evidence for `2606.13662`:
    title/authors/arXiv version/date, source license, linked code/results
    availability, relation to AlphaEvolve, TTT-Discover, CORAL, and
    LibreEvolve's current workflow-centered loop, permission and execution
    boundary schemas, isolated-evaluation records, filesystem/Git artifact
    lineage, collaboration traces, budget and API-cost ledgers, human
    supervision/intervention logs, reward-hacking and artifact-tampering
    safeguards, 26-circle-packing task records, kernel-engineering benchmark
    metadata, MLE-Bench Lite task/submission evidence, baseline identities,
    independent verification outputs, and README/ROADMAP wording that treats
    EurekAgent-style environment engineering as missing paper evidence rather
    than implemented LibreEvolve support.

- [ ] Reproduce CORAL autonomous multi-agent evolution evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2604.01658`, submitted April 2, 2026 and
    last revised May 17, 2026, is titled `CORAL: Towards Autonomous
    Multi-Agent Evolution for Open-Ended Discovery`. Its abstract says
    LLM-based evolution for open-ended discovery needs sustained search and
    knowledge accumulation, but existing methods rely on fixed heuristics and
    hard-coded exploration rules. CORAL replaces rigid control with
    long-running agents that explore, reflect, and collaborate through shared
    persistent memory, asynchronous multi-agent execution, and heartbeat-based
    interventions, plus safeguards for isolated workspaces, evaluator
    separation, resource management, and agent session and health management.
    It reports state-of-the-art results on 10 mathematical, algorithmic, and
    systems optimization tasks, 3-10x higher improvement rates with fewer
    evaluations, and a kernel-engineering score improvement from 1363 to 1103
    cycles. The current arXiv page links code at
    `https://github.com/Human-Agent-Society/CORAL`.
  - Current gap: the paper cache, paper index, row identity, and TODO coverage
    now include `2604.01658`, cached locally as
    `papers/2604.01658__CORAL.pdf` with byte count `3096184` and SHA-256
    `6baf82f122d884380dea1ce2a20a92fd4e75216f430f652819d56bb2b893085c`.
    Existing evidence still does not reproduce CORAL-style long-running agent
    sessions, shared persistent memory, asynchronous agent collaboration,
    heartbeat interventions, isolated workspaces, evaluator separation,
    resource and health management, or multi-agent benchmark/mechanism
    evidence.
  - Required result: add reproduction-grade evidence beyond paper coverage for
    `2604.01658`: title/authors/arXiv version/date, source license,
    linked-code URL/status, relation to AlphaEvolve and LibreEvolve islands,
    agent-session schema, shared-memory/index metadata, asynchronous execution
    and communication traces, heartbeat intervention records,
    workspace-isolation and evaluator-separation policies, resource and health
    telemetry, knowledge-reuse/mechanistic analysis artifacts, mathematical/
    algorithmic/systems benchmark taxonomy, kernel-engineering metric records,
    baseline identities, code/artifact reproducibility status, and
    README/ROADMAP wording that treats CORAL as missing implementation
    evidence rather than implemented LibreEvolve support.

- [ ] Reproduce AEvo harnessed meta-editing evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2605.13821`, submitted May 13, 2026, is
    titled `Harnessing Agentic Evolution`. Its abstract says agentic evolution
    improves programs, workflows, and scientific solutions by iteratively
    generating candidates, evaluating them, and using feedback to guide future
    search, but existing systems are either fixed modular procedures that are
    rigid or general-purpose agents that can drift in long-horizon evolution.
    AEvo treats accumulated candidates, feedback, traces, and failures as
    process-level state and uses a meta-agent to edit the procedure or agent
    context controlling future evolution, reporting a 26 relative improvement
    over the strongest of five baselines and state-of-the-art results on three
    open-ended optimization tasks under the same iteration budget.
  - Current gap: the paper cache, paper index, row identity, and TODO coverage
    now include `2605.13821`, cached locally as
    `papers/2605.13821__AEvo.pdf` with byte count `1450611` and SHA-256
    `40b5c2cde5b1886488a67b511d7dd780756304a5714d8b3261b8fe35e47beba0`.
    Existing evidence still does not reproduce AEvo-style process-level state,
    meta-agent procedure/context edits, controller self-modification,
    control-edit rollback/versioning, drift diagnostics, or benchmark
    boundaries separating candidate generation from mechanism edits.
  - Required result: add reproduction-grade evidence beyond paper coverage for
    `2605.13821`: title/authors/arXiv version/date, source license, relation
    to AlphaEvolve and LibreEvolve, process-state schema, accumulated-evidence
    inventory, meta-agent observation/action schema, procedure/context patch
    artifacts, control-edit provenance, rollback/versioning metadata,
    drift/stability diagnostics, iteration-budget accounting,
    agentic/reasoning/open-ended benchmark taxonomy, baseline identities,
    code/artifact availability if any, reproducibility status, and
    README/ROADMAP wording that treats AEvo as missing implementation evidence
    rather than implemented LibreEvolve support.

- [ ] Reproduce G-Zero verifier-free co-evolution evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2605.09959`, submitted May 11, 2026, is
    titled `G-Zero: Self-Play for Open-Ended Generation from Zero Data`. Its
    abstract says self-evolving LLMs struggle on open-ended tasks because
    proxy LLM judges introduce capability bottlenecks and reward hacking.
    G-Zero introduces a verifier-free co-evolutionary framework with
    `Hint-delta`, an intrinsic reward measuring predictive shift between a
    Generator model's unassisted response and its response conditioned on a
    self-generated hint. A Proposer is trained with GRPO to target Generator
    blind spots by generating queries and hints, while the Generator is
    trained with DPO to internalize improvements. The paper also states a
    best-iterate suboptimality guarantee under sufficient exploration coverage
    and low pseudo-label score noise.
  - Current gap: the paper cache, paper index, row identity, and TODO coverage
    now include `2605.09959`, cached locally as
    `papers/2605.09959__G_Zero.pdf` with byte count `1980993` and SHA-256
    `97ba152b7208e1d8d2f0f1bcf4fe293419e485a568217a6ed8ea50214f5357c9`.
    Existing evidence still does not reproduce verifier-free co-evolution,
    Hint-delta intrinsic rewards, self-generated query/hint data, GRPO/DPO
    self-training, exploration coverage guarantees, or pseudo-label noise
    filtering for open-ended domains.
  - Required result: add reproduction-grade evidence beyond paper coverage for
    `2605.09959`: title/authors/arXiv version/date, source license, relation
    to AlphaEvolve and LibreEvolve evaluator assumptions, Generator/Proposer
    role schema, Hint-delta reward definition, unassisted vs hint-conditioned
    response artifacts, self-generated query/hint records, GRPO/DPO training
    metadata, intrinsic-reward calibration, exploration coverage evidence,
    pseudo-label score-noise filters, reward-hacking diagnostics, open-ended
    task taxonomy, theoretical guarantee assumptions, baseline identities,
    code/artifact availability if any, reproducibility status, and
    README/ROADMAP wording that treats G-Zero as missing implementation
    evidence rather than implemented LibreEvolve support.

- [ ] Reproduce GenEvolve multimodal trajectory-distillation evidence beyond
      paper coverage.
  - Paper/source evidence: arXiv `2605.21605`, submitted May 20, 2026 and
    last revised May 22, 2026, is titled `GenEvolve: Self-Evolving Image
    Generation Agents via Tool-Orchestrated Visual Experience Distillation`.
    Its abstract says open-ended image generation is no longer a simple
    prompt-to-image problem and often requires agents to combine internal
    generative ability with external resources. GenEvolve models each
    generation attempt as a tool-orchestrated trajectory in which the agent
    gathers evidence, selects references, invokes generation skills, and
    composes them into a prompt-reference program. It compares multiple
    trajectories for the same request, abstracts best-worst differences into
    structured visual experience for a privileged teacher branch, and uses
    Visual Experience Distillation to provide dense token-level supervision
    so the student internalizes better search, knowledge activation, reference
    selection, and prompt construction.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2605.21605`, cached locally as
    `papers/2605.21605__GenEvolve.pdf` with byte count `23833361` and
    SHA-256
    `2e38145ffd81f1c2f67b9fe4ee9adeec6284796739616d2778c89600b4455d5c`.
    Reproduction evidence remains absent: no source-license details,
    project/demo URL status, linked-code audit, tool-orchestrated visual
    trajectory schema, evidence/reference selection metadata,
    prompt-reference program representation, best-worst comparison records,
    structured visual experience taxonomy, privileged teacher/student
    distillation traces, token-level supervision artifacts, image artifact
    provenance, GenEvolve-Data/GenEvolve-Bench metadata, baseline identities,
    code/artifact availability status, reproducibility status, or independent
    reproduction output exists.
  - Required result: add reproduction-grade GenEvolve evidence: source
    license, project/demo URL status, linked-code status, relation to
    AlphaEvolve and LibreEvolve, tool-orchestrated visual trajectory schema,
    evidence/reference selection metadata, prompt-reference program
    representation, best-worst comparison records, structured visual
    experience taxonomy, privileged teacher/student distillation traces,
    token-level supervision artifacts, image artifact provenance,
    GenEvolve-Data/GenEvolve-Bench metadata, baseline identities,
    code/artifact reproducibility status, independent reproduction outputs,
    and README/ROADMAP wording that treats GenEvolve as background context
    until those artifacts exist.

- [ ] Reproduce EvoRubric self-evolving reward-rubric evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2605.29847`, submitted May 28, 2026, is
    titled `EvoRubric: Self-Evolving Rubric-Driven RL for Open-Ended
    Generation`. Its abstract says RL has advanced LLMs in verifiable domains,
    but open-ended generation lacks definitive rewards. Existing rubric-based
    RL uses static human annotations, which can cause policy lag, or expensive
    external proprietary rubric generators. EvoRubric unifies response and
    rubric generation under a single policy that alternates between Reasoner
    and Rubric Generator roles; validates generated criteria through a
    meta-verifier, zero-variance pruning, and Leave-One-Out peer consensus;
    stores validated criteria in memory; and yields dense multi-objective
    rewards across medical, writing, and science domains.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2605.29847`, cached locally as
    `papers/2605.29847__EvoRubric.pdf` with byte count `1089746` and
    SHA-256
    `3579085619610d97a03019d495a584c6dfce76f4ea951dda3103f02395bec1d5`.
    Reproduction evidence remains absent: no source-license details,
    linked-code or project/demo URL status, Reasoner/Rubric-Generator role
    schema, generated-rubric provenance, meta-verifier artifacts,
    zero-variance pruning records, Leave-One-Out peer-consensus traces,
    criteria memory-pool metadata, dense reward-vector definitions,
    reward-hacking diagnostics, expert-prior initialization status,
    medical/writing/science benchmark taxonomy, baseline identities,
    code/artifact availability status, reproducibility status, or independent
    reproduction output exists.
  - Required result: add reproduction-grade EvoRubric evidence: source
    license, project/demo URL status, linked-code status, relation to
    AlphaEvolve and LibreEvolve evaluator assumptions, Reasoner/Rubric-
    Generator role schema, generated-rubric provenance, meta-verifier
    artifacts, zero-variance pruning records, Leave-One-Out peer-consensus
    traces, criteria memory-pool metadata, dense reward-vector definitions,
    reward-hacking diagnostics, expert-prior initialization status,
    medical/writing/science benchmark taxonomy, baseline identities,
    code/artifact reproducibility status, independent reproduction outputs,
    and README/ROADMAP wording that treats EvoRubric as background context
    until those artifacts exist.

- [ ] Reproduce LLM-ALSO adaptive learning-signal evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2605.29293`, submitted May 28, 2026, is
    titled `LLM-ALSO: LLM-Driven Adaptive Learning-Signal Optimization for
    Multi-Agent Reinforcement Learning`. Its abstract says effective
    training-time guidance is difficult in sparse-reward MARL, while existing
    LLM-based learning-signal design is largely single-agent-oriented,
    one-shot, or weakly validated for evolving cooperative training dynamics.
    LLM-ALSO decomposes adaptation into iterative diagnosis, proposal, and
    validation: a Critic LLM diagnoses stage-specific learning and
    coordination failures from sparse-return metrics and compact behavior
    evidence, a Generator LLM proposes reward-shaping configurations
    conditioned on the diagnosis, and branch-validation feedback refines
    candidates before updates affect the main training trajectory.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2605.29293`, cached locally as
    `papers/2605.29293__LLM_ALSO.pdf` with byte count `712323` and SHA-256
    `06b9bcb459f40437119f2c95153985a0e8682e0509ca12be9bd5f32147c888f5`.
    Reproduction evidence remains absent: no source-license details,
    linked-code or project/demo URL status, Critic/Generator role schema,
    sparse-return and compact-behavior evidence metadata, stage-specific
    diagnosis artifacts, reward-shaping configuration schema,
    branch-validation records, promotion criteria, main-training trajectory
    provenance, sparse-reward cooperative MARL task taxonomy,
    learning-efficiency metrics, baseline identities, code/artifact
    availability status, reproducibility status, or independent reproduction
    output exists.
  - Required result: add reproduction-grade LLM-ALSO evidence: source license,
    project/demo URL status, linked-code status, relation to AlphaEvolve and
    LibreEvolve reward/evaluator assumptions, Critic/Generator role schema,
    sparse-return and compact-behavior evidence metadata, stage-specific
    diagnosis artifacts, reward-shaping configuration schema,
    branch-validation records, promotion criteria, main-training trajectory
    provenance, sparse-reward cooperative MARL task taxonomy,
    learning-efficiency metrics, baseline identities, code/artifact
    reproducibility status, independent reproduction outputs, and README/
    ROADMAP wording that treats LLM-ALSO as background context until those
    artifacts exist.

- [ ] Reproduce MemEvolve meta-evolving memory-architecture evidence beyond
      paper coverage.
  - Paper/source evidence: arXiv `2512.18746`, submitted December 21, 2025, is
    titled `MemEvolve: Meta-Evolution of Agent Memory Systems`. Its abstract
    says self-evolving memory systems are reshaping LLM-agent evolution, but
    prior work relies on manually engineered memory architectures to store
    trajectories, distill experience, and synthesize reusable tools. MemEvolve
    jointly evolves experiential knowledge and memory architecture, allowing
    agents to refine how they learn from experience. It introduces EvolveLab,
    a unified self-evolving memory codebase that distills twelve memory
    systems into a modular encode/store/retrieve/manage design space, and
    reports up to 17.06% improvements for frameworks such as SmolAgent and
    Flash-Searcher plus cross-task and cross-LLM generalization.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2512.18746`, cached locally as
    `papers/2512.18746__MemEvolve.pdf` with byte count `10951239` and
    SHA-256
    `51ca8a0ca349b7ad111b5380148c6dd34fa4d16f933ac58677fc2246b1566dd5`.
    Reproduction evidence remains absent: no source-license details,
    linked-code or project/demo URL status, memory-component taxonomy,
    encode/store/retrieve/manage schema, memory-architecture mutation records,
    experiential-knowledge artifacts, joint content/architecture evolution
    traces, static-memory baseline identities, EvolveLab benchmark metadata,
    cross-task and cross-LLM transfer metrics, performance-delta records,
    code/artifact availability status, reproducibility status, or independent
    reproduction output exists.
  - Required result: add reproduction-grade MemEvolve evidence: source
    license, project/demo URL status, linked-code status, relation to
    AlphaEvolve and LibreEvolve run memory, memory-component taxonomy,
    encode/store/retrieve/manage schema, memory-architecture mutation records,
    experiential-knowledge artifacts, joint content/architecture evolution
    traces, static-memory baseline identities, EvolveLab benchmark metadata,
    cross-task and cross-LLM transfer metrics, performance-delta records,
    code/artifact reproducibility status, independent reproduction outputs,
    and README/ROADMAP wording that treats MemEvolve as background context
    until those artifacts exist.

- [ ] Reproduce ANCHOR healthy-evolution oversight evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2606.06114`, submitted June 4, 2026, is
    titled `Towards Healthy Evolution: Exploring the Role and Mechanisms of
    Human-Agent Interaction in Self-Evolving Systems`. Its abstract says
    autonomous self-evolution can cause capability degradation and safety
    drift, and introduces Agent Norm Correction through Human-like Oversight
    and Review (ANCHOR), an LLM-based framework that simulates human
    supervision across phases of self-evolution. It evaluates two
    representative open-source self-evolving agent systems across coding,
    mathematical reasoning, and safety, reports that limited supervision
    mitigates safety degradation while preserving core performance, identifies
    output-verification supervision as the strongest intervention point, and
    finds diminishing returns from increasing supervision frequency.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2606.06114`, cached locally as
    `papers/2606.06114__ANCHOR_Healthy_Evolution.pdf` with byte count
    `2711376` and SHA-256
    `0d54f3a598c56fa69137ed4f35d8527734dff851de4a5248a777b5abfb822414`.
    Reproduction evidence remains absent: no source-license details,
    linked-code or project/demo URL status, ANCHOR role and feedback schema,
    supervised phase taxonomy, norm-correction artifact records,
    output-verification intervention evidence, safety degradation metrics,
    coding/math/safety benchmark taxonomy, supervision-frequency experiment
    records, objective-preservation measurements, baseline identities,
    code/artifact availability status, reproducibility status, or independent
    reproduction output exists.
  - Required result: add reproduction-grade ANCHOR evidence: source license,
    project/demo URL status, linked-code status, relation to AlphaEvolve and
    LibreEvolve safety assumptions, ANCHOR role and feedback schema,
    supervised phase taxonomy, norm-correction artifact records,
    output-verification intervention evidence, safety degradation metrics,
    coding/math/safety benchmark taxonomy, supervision-frequency experiment
    records, objective-preservation measurements, baseline identities,
    code/artifact reproducibility status, independent reproduction outputs,
    and README/ROADMAP wording that treats ANCHOR as background context until
    those artifacts exist.

- [ ] Reproduce SIA harness-plus-weight self-improvement evidence beyond
      paper coverage.
  - Paper/source evidence: arXiv `2605.27276`, submitted May 26, 2026, is
    titled `SIA: Self Improving AI with Harness & Weight Updates`. Its
    abstract says AI improvement remains bottlenecked by humans who write,
    tune, and correct both models and agent wrappers. It contrasts a
    harness-update line, where a meta-agent rewrites tools, prompts, retry
    logic, and search procedures while weights remain fixed, with a test-time
    training line, where model weights are updated from task feedback while
    the harness remains fixed. SIA proposes a Feedback-Agent loop that
    updates both the harness and weights of a task-specific agent, evaluated
    on Chinese legal charge classification, low-level GPU kernel
    optimization, and single-cell RNA denoising. The abstract reports 25.1%
    over prior SOTA on LawBench, 12.4% faster GPU kernels than prior SOTA, and
    20.4% over prior SOTA on denoising; later kernel text also reports a
    91.9% runtime reduction from the harness-only peak.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2605.27276`, cached locally as
    `papers/2605.27276__SIA.pdf` with byte count `993538` and SHA-256
    `3f75a62487a5fb3fc2db8d06b78e6f6d598fc46b446cdfa9e205c33fb41de265`.
    Reproduction evidence remains absent: no source-license details,
    linked-code or project/demo URL status, Meta-Agent/Target-Agent/
    Feedback-Agent role schema, editable-harness taxonomy, harness patch
    records, weight-update records, training-data provenance,
    RL/fine-tuning configuration, adapter/checkpoint artifacts,
    verifier/reward definitions, harness-only, weight-only, and combined-loop
    ablation records, LawBench/kernel/scRNA benchmark metadata, compute/cost
    accounting, performance-delta records, code/artifact availability status,
    reproducibility status, or independent reproduction output exists.
  - Required result: add reproduction-grade SIA evidence: source license,
    project/demo URL status, linked-code status, relation to AlphaEvolve and
    LibreEvolve training assumptions, Meta-Agent/Target-Agent/Feedback-Agent
    role schema, editable-harness taxonomy, harness patch records,
    weight-update records, training-data provenance, RL/fine-tuning
    configuration, adapter/checkpoint artifacts, verifier/reward definitions,
    harness-only, weight-only, and combined-loop ablation records,
    LawBench/kernel/scRNA benchmark metadata, compute/cost accounting,
    performance-delta records, code/artifact reproducibility status,
    independent reproduction outputs, and README/ROADMAP wording that treats
    SIA as background context until those artifacts exist.

- [ ] Reproduce Darwin Godel Machine self-improving-agent evidence beyond
      broad self-improvement boundaries.
  - Paper/source evidence: arXiv `2505.22954`, submitted May 29, 2025 and
    last revised March 12, 2026, is titled `Darwin Godel Machine:
    Open-Ended Evolution of Self-Improving Agents`. Its abstract introduces
    DGM as a self-improving system that iteratively modifies its own code and
    empirically validates each change using coding benchmarks. It maintains
    an archive of generated coding agents, grows the archive by sampling an
    agent and using a foundation model to create a new version, and frames the
    resulting search as open-ended exploration over a growing tree of diverse,
    high-quality agents. The abstract reports SWE-bench improvement from
    20.0% to 50.0% and Polyglot improvement from 14.2% to 30.7%, with
    safety precautions including sandboxing and human oversight. The arXiv
    page links source code at `https://github.com/jennyzzt/dgm`; the GitHub
    page identifies the repository as Apache-2.0 licensed and shows DGM
    runner, coding-agent, SWE-bench, Polyglot, prompt, tool, and analysis
    files.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, source-scoped TODO, or code TODO
    exists for `2505.22954`. Existing LibreEvolve self-improvement,
    self-improvement-cadence, SIA, HarnessFix, RHO, Adaptive Auto-Harness,
    Meta-Harness, AHE, and AlphaEvolve Discussion TODOs do not reproduce DGM's
    self-modifying coding-agent archive, generated-agent tree, archive-growth
    policy, agent-code mutation/evaluation protocol, coding-benchmark
    validation loop, SWE-bench and Polyglot setup, benchmark-result deltas,
    open-ended stepping-stone analysis, sandbox/human-oversight safety
    controls, experiment logs, linked-code audit, or independent reproduction
    outputs.
  - Required result: add reproduction-grade evidence for `2505.22954`:
    title/authors/arXiv version/date, arXiv license, GitHub URL/status and
    Apache-2.0 license, relation to AlphaEvolve, LibreEvolve, DGM, SIA, and
    harness-evolution papers, generated-agent archive schema, agent-lineage
    tree export, archive sampling and growth policy, self-modification prompt
    and tool contract, coding-agent file inventory, code-edit provenance,
    empirical-validation gate, SWE-bench fixture and pinned checkout metadata,
    Polyglot dataset preparation metadata, baseline identities, per-generation
    benchmark scores, open-ended exploration and stepping-stone metrics,
    sandboxing/human-oversight safety records, experiment-log provenance,
    linked-code snapshot audit, independent reproduction outputs, and README/
    ROADMAP wording that treats DGM-style self-improving coding-agent archives
    as missing evidence rather than implemented LibreEvolve support.

- [ ] Reproduce HarnessFix trace-grounded harness repair evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2606.06324`, submitted June 4, 2026, is
    titled `From Failed Trajectories to Reliable LLM Agents: Diagnosing and
    Repairing Harness Flaws`. Its abstract says agent harnesses provide
    execution environments, tool interfaces, context, lifecycle
    orchestration, observability, verification, and governance, but existing
    self-improvement and automatic harness-evolution methods often make broad
    changes from final outcomes instead of diagnosing the responsible
    evidence in failed trajectories. HarnessFix compiles raw traces and
    harness code into a Harness-aware Trace Intermediate Representation
    (HTIR), attributes failures to responsible trajectory steps and harness
    layers, consolidates recurring flaw records, maps them to scoped repair
    operators, and validates harness patches under flaw-specific repair specs.
    It reports 15.2% to 50.0% held-out improvements on SWE-Bench Verified,
    Terminal-Bench 2.0 Verified, GAIA, and AppWorld.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2606.06324`, cached locally as
    `papers/2606.06324__HarnessFix.pdf` with byte count `2363715` and
    SHA-256
    `00a4236ba8ab24925e3b0409b4c003bd22c57d76faabc888f20734fba5e4cafd`.
    Reproduction evidence remains absent: no source-license details, linked-
    code or project/demo URL status, HTIR schema, trace-to-harness-code
    linkage, step-level provenance, harness-layer taxonomy, failure-
    attribution records, recurring flaw consolidation, repair-operator
    definitions, harness patch artifacts, flaw-specific validation
    specifications, unacceptable-regression thresholds, held-out benchmark
    results, SWE-Bench/Terminal-Bench/GAIA/AppWorld metadata, baseline
    identities, code/artifact availability status, reproducibility status, or
    independent reproduction output exists.
  - Required result: add reproduction-grade HarnessFix evidence: source
    license, project/demo URL status, linked-code status, relation to
    AlphaEvolve and LibreEvolve harness/failure assumptions, HTIR schema,
    trace-to-harness-code linkage, step-level provenance, harness-layer
    taxonomy, failure-attribution records, recurring flaw consolidation,
    repair-operator definitions, harness patch artifacts, flaw-specific
    validation specifications, unacceptable-regression thresholds, held-out
    benchmark results, SWE-Bench/Terminal-Bench/GAIA/AppWorld metadata,
    baseline identities, code/artifact reproducibility status, independent
    reproduction outputs, and README/ROADMAP wording that treats HarnessFix as
    background context until those artifacts exist.

- [ ] Reproduce RHO retrospective self-preference harness optimization
      evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.05922`, submitted June 4, 2026, is
    titled `Retrospective Harness Optimization: Improving LLM Agents via
    Self-Preference over Trajectory Rollouts`. Its abstract says continually
    improving an agent harness is essential for adapting to new tasks, but
    ground-truth validation labels are often unavailable in practical
    deployments. RHO optimizes a harness using only past trajectories by
    selecting a diverse coreset of challenging tasks, re-solving them in
    parallel, analyzing rollouts with self-validation and self-consistency,
    generating candidate harness updates, and selecting the best update via
    pairwise self-preference. It reports a single optimization round improving
    SWE-Bench Pro pass rate from 59% to 78% without external grading, and says
    the optimized harness sustains higher accuracy in long-horizon sessions.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2606.05922`, cached locally as
    `papers/2606.05922__RHO.pdf` with byte count `1267774` and SHA-256
    `75b126a2a6350e8ff58c0e6c7f3366894e23f0610f533ac533fc3e3214aa7cd4`.
    Reproduction evidence remains absent: no source-license details,
    linked-code or project URL status, past-trajectory corpus metadata, hard-
    task/diversity coreset selection, DPP coreset record, retrospective
    rollout batch records, parallel re-solve provenance, self-validation or
    self-consistency artifacts, candidate harness-update records, pairwise
    self-preference comparisons, label-free selection policy, deployment and
    rollback metadata, behavior-pattern shift reports, long-horizon accuracy
    records, SWE-Bench Pro benchmark metadata, baseline identities,
    code/artifact reproducibility status, or independent reproduction output
    exists.
  - Required result: add reproduction-grade RHO evidence: source license,
    project URL status, linked-code status, relation to AlphaEvolve and
    LibreEvolve evaluator assumptions, past-trajectory corpus metadata, hard-
    task/diversity coreset selection, DPP coreset record, retrospective
    rollout batch records, parallel re-solve provenance, self-validation and
    self-consistency artifacts, candidate harness-update records, pairwise
    self-preference comparisons, label-free selection policy, deployment and
    rollback metadata, behavior-pattern shift reports, long-horizon accuracy
    records, SWE-Bench Pro benchmark metadata, baseline identities,
    code/artifact reproducibility status, independent reproduction outputs,
    and README/ROADMAP wording that treats RHO as background context until
    those artifacts exist.

- [ ] Reproduce harness-updating versus harness-benefit paper evidence beyond
      paper coverage.
  - Paper/source evidence: arXiv `2605.30621`, submitted May 28, 2026, is
    titled `Harness Updating Is Not Harness Benefit: Disentangling Evolution
    Capabilities in Self-Evolving LLM Agents`. Its abstract says LLM agents
    are increasingly built around editable external harnesses such as prompts,
    skills, memories, and tools. It analyzes two separable capabilities:
    harness-updating, the ability to produce useful persistent harness updates
    from execution evidence, and harness-benefit, the ability to benefit from
    updated harnesses during task solving. The abstract reports that
    harness-updating is flat across model capability tiers, while
    harness-benefit is non-monotonic: weak-tier models benefit little,
    mid-tier models benefit most, and strong-tier models benefit less than
    mid-tier. It traces weak-tier failures to failing to activate relevant
    harness artifacts or failing to follow them faithfully.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2605.30621`, cached locally as
    `papers/2605.30621__Harness_Updating_Is_Not_Harness_Benefit.pdf` with
    byte count `2463998` and SHA-256
    `a3a09f90dc278f1c6ceee5a3f7bf807b5a92b642cbcb0123d20b824a0e880d6b`.
    Reproduction evidence remains absent: no source-license details,
    linked-code URL/status, relation to AlphaEvolve and LibreEvolve harness
    assumptions, harness-updating and harness-benefit metric definitions,
    evolver/task-agent pairing records, persistent harness update artifacts,
    activation telemetry, adherence and instruction-following traces,
    model-tier taxonomy, weak/mid/strong baseline identities, capability-
    budget analysis, post-evolution performance deltas, SWE-Bench Verified/
    MCP-Atlas/SkillsBench metadata if used, code/artifact availability,
    reproducibility status, or independent reproduction output exists.
  - Required result: add reproduction-grade evidence for `2605.30621`: source
    license, project URL status, linked-code status, relation to AlphaEvolve
    and LibreEvolve harness assumptions, harness-updating and harness-benefit
    metric definitions, evolver/task-agent pairing records, persistent
    harness update artifacts, activation telemetry, adherence and instruction-
    following traces, model-tier taxonomy, weak/mid/strong baseline
    identities, capability-budget analysis, post-evolution performance
    deltas, SWE-Bench Verified/MCP-Atlas/SkillsBench metadata if used,
    code/artifact reproducibility status, independent reproduction outputs,
    and README/ROADMAP wording that treats harness-update benefit as
    background context until those artifacts exist.

- [ ] Reproduce AHE observability-driven harness evolution evidence beyond
      paper coverage.
  - Paper/source evidence: arXiv `2604.25850`, submitted April 28, 2026, is
    titled `Agentic Harness Engineering: Observability-Driven Automatic
    Evolution of Coding-Agent Harnesses`. Its abstract says harnesses mediate
    how models interact with tools and execution environments, but automating
    harness engineering is hard because of heterogeneous editable components,
    very large trajectories, sparse/noisy signals, and edits whose effects are
    hard to attribute. AHE adds component observability through explicit
    file-level editable components, experience observability through layered
    drill-down trajectory evidence, and decision observability by pairing each
    edit with a self-declared prediction that is later checked against
    task-level outcomes. It reports ten iterations improving Terminal-Bench 2
    pass@1 from 69.7% to 77.0%, surpassing Codex-CLI and self-evolving
    baselines, plus frozen-harness transfer to SWE-bench Verified and cross-
    family Terminal-Bench gains.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2604.25850`, cached locally as
    `papers/2604.25850__AHE.pdf` with byte count `1432986` and SHA-256
    `299f2633b4c13db7bed52434b4db7c48ea621993581014d30e7bcd036d3464df`.
    Reproduction evidence remains absent: no source-license details,
    linked-code URL/status, relation to AlphaEvolve and LibreEvolve harness
    assumptions, editable component taxonomy, file-level component manifests,
    component edit/revert records, trajectory-evidence corpus schema, drill-
    down evidence links, edit-prediction records, task-outcome verification
    records, falsifiable edit-contract status, iteration traces, component-
    attribution reports, frozen-harness transfer results, Terminal-Bench 2 and
    SWE-bench Verified metadata, baseline identities, token/cost accounting,
    code/artifact reproducibility status, or independent reproduction output
    exists.
  - Required result: add reproduction-grade AHE evidence: source license,
    project URL status, linked-code status, relation to AlphaEvolve and
    LibreEvolve harness assumptions, editable component taxonomy, file-level
    component manifests, component edit/revert records, trajectory-evidence
    corpus schema, drill-down evidence links, edit-prediction records, task-
    outcome verification records, falsifiable edit-contract status, iteration
    traces, component-attribution reports, frozen-harness transfer results,
    Terminal-Bench 2 and SWE-bench Verified metadata, baseline identities,
    token/cost accounting, code/artifact reproducibility status, independent
    reproduction outputs, and README/ROADMAP wording that treats AHE as
    background context until those artifacts exist.

- [ ] Reproduce AI Harness Engineering runtime-substrate evidence beyond paper
      coverage.
  - Paper/source evidence: arXiv `2605.13357`, submitted May 13, 2026, is
    titled `AI Harness Engineering: A Runtime Substrate for Foundation-Model
    Software Agents`. Its abstract says autonomous software-engineering
    reliability should be explained through a model-harness-environment
    system, where the harness mediates how a foundation-model agent observes a
    project, acts on it, receives feedback, and establishes that a change is
    complete. The paper identifies eleven component responsibilities: task
    specification, context selection, tool access, project memory, task state,
    observability, failure attribution, verification, permissions, entropy
    auditing, and intervention recording. It operationalizes the harness
    through an H0-H3 ladder and converts each run into an auditable episode
    package; higher levels produce reproduction logs, failure attributions,
    deterministic requirement checks, and structured verification reports.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2605.13357`, cached locally as
    `papers/2605.13357__AI_Harness_Engineering.pdf` with byte count `263956`
    and SHA-256
    `a1e2d7ce307c662411ca6bd5f833d7dae7f122ce6ef1ddd6d2370e82575b2fb9`.
    Reproduction evidence remains absent: no source-license details,
    relation to AlphaEvolve and LibreEvolve harness assumptions, model-
    harness-environment schema, eleven responsibility taxonomy, H0-H3
    harness-level records, runtime-resource exposure matrix, task/context/
    tool/memory/state artifact records, observability traces, failure-
    attribution logs, verification protocol and report records, permission
    events, entropy audits, intervention logs, episode package schema,
    deterministic requirement-check metadata, controlled validation task
    evidence, maintenance-burden analysis, code/artifact reproducibility
    status, or independent reproduction output exists.
  - Required result: add reproduction-grade AI Harness Engineering evidence:
    source license, relation to AlphaEvolve and LibreEvolve harness
    assumptions, model-harness-environment schema, eleven responsibility
    taxonomy, H0-H3 harness-level records, runtime-resource exposure matrix,
    task/context/tool/memory/state artifact records, observability traces,
    failure-attribution logs, verification protocol and report records,
    permission events, entropy audits, intervention logs, episode package
    schema, deterministic requirement-check metadata, controlled validation
    task evidence, maintenance-burden analysis, code/artifact reproducibility
    status, independent reproduction outputs, and README/ROADMAP wording that
    treats AI Harness Engineering as background context until those artifacts
    exist.

- [ ] Reproduce HarnessBridge learnable-controller evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.12882`, submitted June 11, 2026, is
    titled `HarnessBridge: Learnable Bidirectional Controller for LLM Agent
    Harness`. Its abstract says long-horizon agent performance depends on the
    harness that mediates agent-environment interaction, not only on model
    capability or environment design. HarnessBridge is a lightweight
    learnable plug-in controller that parameterizes the agent-environment
    interface as two bidirectional projections: an observation projection that
    distills raw trajectories into compact decision-relevant states, and an
    action projection that converts proposed actions into executable
    transitions or trajectory-grounded rejections. It is trained on a harness
    supervision dataset through unified instruction tuning and reports
    matching or surpassing strong specialized harnesses on Terminal-Bench 2.0
    and SWE-bench Verified while reducing token usage and trajectory length.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.12882`. Existing harness TODOs cover runtime-substrate
    taxonomies, trace-grounded repair, retrospective harness optimization,
    observability-driven harness evolution, partial-harness trajectory
    alignment, and open-ended auto-harness deployment, but they do not capture
    a learnable bidirectional controller, observation/action projection
    schemas, harness-supervision training data, unified instruction-tuning
    evidence, token/trajectory compression metrics, or small-to-commercial
    model transfer.
  - Required result: add reproduction-grade evidence for `2606.12882`:
    title/authors/arXiv version/date, source license, code/model/dataset
    availability, relation to AlphaEvolve and LibreEvolve harness assumptions,
    learnable-controller architecture schema, observation-projection and
    action-projection records, executable-transition and rejection semantics,
    harness-supervision dataset provenance, unified instruction-tuning
    configuration, generator/model-transfer records, Terminal-Bench 2.0 and
    SWE-bench Verified task metadata, specialized-harness baseline identities,
    token-usage and trajectory-length metrics, ablation and generalization
    evidence, independent verification outputs, and README/ROADMAP wording
    that treats HarnessBridge-style learned harness mediation as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Reproduce TRACE correction-to-enforcement evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.13174`, submitted June 11, 2026, is
    titled `Getting Better at Working With You: Compiling User Corrections
    into Runtime Enforcement for Coding Agents`. Its abstract defines the
    gap between preference access and preference compliance: an agent may
    retrieve a remembered correction but still violate it. TRACE, Test-time
    Rule Acquisition and Compiled Enforcement, is presented as a drop-in
    skill-layer pipeline that mines user chat corrections, rewrites them as
    atomic rules, and compiles them into runtime checks that must pass before
    future tasks complete. The paper reports that Mem0 memory still leaves
    `57.5%` of applicable preference checks violated, while TRACE reduces
    held-out ClawArena preference violations from `100.0%` to `37.6%`
    in-distribution and to `2.0%` out-of-distribution, and reduces
    MemoryArena-derived in-distribution violations from `100.0%` to `60.5%`
    while matching or exceeding the strongest memory baseline on task pass.
    The arXiv page links experiment code at
    `https://github.com/YujunZhou/TRACE_exp` and a deployable skill at
    `https://github.com/YujunZhou/tellonce`.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.13174`. Existing LibreEvolve failure-memory,
    collaborator-feedback, qualitative-feedback, and harness TODOs do not
    capture correction extraction from user chat, atomic rule rewriting,
    rule-library conflict resolution, compiled completion-time runtime checks,
    preference access-versus-compliance diagnostics, ClawArena/MemoryArena
    violation metrics, or deployable skill-layer enforcement.
  - Required result: add reproduction-grade evidence for `2606.13174`:
    title/authors/arXiv version/date, source license, linked-code and
    deployable-skill availability, relation to AlphaEvolve, LibreEvolve
    failure memory, prompt-history feedback, and runtime harness assumptions,
    correction-mining schema, atomic-rule representation, applicability and
    conflict-resolution policy, completion-gate runtime-check contract,
    rule-library persistence and versioning records, privacy/redaction policy
    for user corrections, ClawArena and MemoryArena-derived task metadata,
    preference-access and preference-compliance metrics, violation-rate
    tables, Mem0/Hindsight/ReMe/no-memory baseline identities, latency and
    task-pass tradeoff records, independent verification outputs, and
    README/ROADMAP wording that treats TRACE-style compiled user-correction
    enforcement as missing paper evidence rather than implemented LibreEvolve
    support.

- [ ] Reproduce Evoflux executable-tool-workflow evolution evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.12674`, submitted June 10, 2026, is
    titled `Evoflux: Inference-Time Evolution of Executable Tool Workflows
    for Compact Agents`. Its abstract says compact language models can reduce
    cost, latency, and deployment risk for tool agents, but MCP-style tool use
    requires live tool discovery, schema satisfaction, dependency preservation
    across intermediate outputs, and final answers grounded in executed
    evidence. Evoflux treats compact tool use as inference-time repair of
    executable tool workflows: it evolves typed workflow graphs through
    structured edits, execution feedback, adaptive intensity, meta-guided
    redesign, and diversity pruning. The paper reports held-out MCP-Bench
    tasks spanning live MCP servers and `250` tools, raising execution
    feasibility from roughly `3%` to `17-24%` across small planners while
    SFT and SFT+DPO on the same search-mined data match, underperform, or
    collapse below zero-shot performance, and ReAct reaches higher peaks with
    higher variance and token cost.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.12674`. Existing LibreEvolve harness, tool-use,
    failure-memory, and meta-harness TODOs do not capture executable tool
    workflow graph candidates, MCP/tool catalog schemas, dependency-validated
    workflow evolution, adaptive mutation intensity, meta-guided redesign,
    diversity pruning, execution-grounded repair, invalid-tool-use diagnostics,
    or MCP-Bench benchmark provenance.
  - Required result: add reproduction-grade evidence for `2606.12674`:
    title/authors/arXiv version/date, source license, linked code or artifact
    availability, relation to AlphaEvolve, LibreEvolve plugins/tool
    assumptions, and current candidate-workspace loop, typed workflow graph
    schema, tool catalog and MCP server metadata, schema/dependency validation
    records, mutation-operator taxonomy, adaptive-intensity policy,
    meta-guided redesign records, diversity-pruning policy, executable
    workflow artifacts, benchmark/task metadata, baseline identities,
    token/cost/latency telemetry, invalid-tool-use and execution-error
    diagnostics, independent verification outputs, and README/ROADMAP wording
    that treats Evoflux-style executable tool-workflow evolution as missing
    paper evidence rather than implemented LibreEvolve support.

- [ ] Reproduce inference-time trajectory-alignment harness evidence beyond
      paper coverage.
  - Paper/source evidence: arXiv `2605.21516`, submitted May 15, 2026, is
    titled `Harnesses for Inference-Time Alignment over Execution
    Trajectories`. Its abstract says harness engineering improves agent
    performance through task decomposition and guided execution, but more
    elaborate harnesses can reduce final task success. It separates harness
    mechanisms into decomposition and guided execution, then quantifies how
    workflow granularity, retry budgets, and guidance-induced action
    reweighting affect performance limits. It identifies over-decomposition,
    over-pruning, and hallucinated execution as failure modes, validates the
    predictions with controlled synthetic experiments and real terminal-agent
    benchmarks, and shows that partial harnesses can outperform fully
    structured workflows.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2605.21516`, cached locally as
    `papers/2605.21516__Inference_Time_Trajectory_Alignment.pdf` with byte
    count `2323632` and SHA-256
    `5458d316fd5edbfda5cf7355592d41e0c5f3f889e31c92855728c47452f6ca32`.
    Reproduction evidence remains absent: no source-license details, relation
    to AlphaEvolve and LibreEvolve harness assumptions, harness parameter
    schema, decomposition-granularity records, guidance-strength and guidance-
    rule records, sub-goal and trajectory records, retry-budget experiment
    metadata, pass-rate/final-bias metrics, granularity-capability alignment
    evidence, guidance-evidence alignment evidence, over-decomposition/over-
    pruning/hallucinated-execution diagnostics, partial-harness prefix
    experiment records, Terminal-Bench-2 and controlled synthetic benchmark
    metadata, baseline identities, code/artifact reproducibility status, or
    independent reproduction output exists.
  - Required result: add reproduction-grade inference-time trajectory-
    alignment evidence: source license, relation to AlphaEvolve and
    LibreEvolve harness assumptions, harness parameter schema,
    decomposition-granularity records, guidance-strength and guidance-rule
    records, sub-goal and trajectory records, retry-budget experiment
    metadata, pass-rate/final-bias metrics, granularity-capability alignment
    evidence, guidance-evidence alignment evidence, over-decomposition/over-
    pruning/hallucinated-execution diagnostics, partial-harness prefix
    experiment records, Terminal-Bench-2 and controlled synthetic benchmark
    metadata, baseline identities, code/artifact reproducibility status,
    independent reproduction outputs, and README/ROADMAP wording that treats
    inference-time trajectory alignment as background context until those
    artifacts exist.

- [ ] Reproduce Adaptive Auto-Harness open-ended task-stream evidence beyond
      paper coverage.
  - Paper/source evidence: arXiv `2606.01770`, submitted June 1, 2026, is
    titled `Adaptive Auto-Harness: Sustained Self-Improvement for Agentic
    System Deployment on Open-Ended Task Streams`. Its abstract says
    auto-harness systems such as A-Evolve, GEPA, and Meta-Harness improve
    agents by optimizing prompts, skills, tools, memories, and infrastructure
    from execution feedback, but are usually tested on fixed offline
    benchmarks. Open-ended deployments have growing histories, heterogeneous
    tasks, and shifting distributions; a single densely updated harness can
    become brittle as accuracy peaks and declines. Adaptive Auto-Harness
    decomposes the gap to an oracle harness into evolution loss and adaptation
    loss, and addresses those losses with a stateful multi-agent evolver, a
    harness tree with solve-time routing, and human-steering hooks. It reports
    gains across prediction-market, security-competition, and event-
    forecasting streams over five auto-harness baselines.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2606.01770`, cached locally as
    `papers/2606.01770__Adaptive_Auto_Harness.pdf` with byte count `1895729`
    and SHA-256
    `50454c1eec069b668b515c6d322e4c5ac55f24655298b3381f91f461a9c39b3e`.
    Reproduction evidence remains absent: no source-license details, linked-
    code URL/status, relation to AlphaEvolve and LibreEvolve deployment
    assumptions, open-ended task-stream schema, history-growth records, task-
    heterogeneity metadata, distribution-shift metrics, oracle-harness
    definition, evolution-loss and adaptation-loss records, stateful multi-
    agent evolver roles, cross-cycle memory, harness tree artifacts, solve-
    time routing records, human-steering hook provenance, targeted steering
    outcomes, sustained-performance/degradation curves, prediction-market/
    security-competition/event-forecasting benchmark metadata, baseline
    identities, ablation records, code/artifact reproducibility status, or
    independent reproduction output exists.
  - Required result: add reproduction-grade Adaptive Auto-Harness evidence:
    source license, project URL status, linked-code status, relation to
    AlphaEvolve and LibreEvolve deployment assumptions, open-ended task-stream
    schema, history-growth records, task-heterogeneity metadata,
    distribution-shift metrics, oracle-harness definition, evolution-loss and
    adaptation-loss records, stateful multi-agent evolver roles, cross-cycle
    memory, harness tree artifacts, solve-time routing records, human-steering
    hook provenance, targeted steering outcomes, sustained-performance/
    degradation curves, prediction-market/security-competition/event-
    forecasting benchmark metadata, baseline identities, ablation records,
    code/artifact reproducibility status, independent reproduction outputs,
    and README/ROADMAP wording that treats Adaptive Auto-Harness as background
    context until those artifacts exist.

- [ ] Reproduce Meta-Harness outer-loop harness-code search evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2603.28052`, submitted March 30, 2026, is
    titled `Meta-Harness: End-to-End Optimization of Model Harnesses`. Its
    abstract says LLM systems depend on harness code that decides what
    information to store, retrieve, and present to the model, and that text
    optimizers are poorly matched to harness optimization because they
    compress feedback too aggressively. Meta-Harness searches over harness
    code with an agentic proposer that accesses source code, scores, and
    execution traces for prior candidates through a filesystem. The abstract
    reports a 7.7 point online text-classification gain using 4x fewer context
    tokens, a 4.7 point average gain on 200 IMO-level retrieval-augmented math
    problems across five held-out models, and harnesses that surpass hand-
    engineered baselines on TerminalBench-2.
  - Current gap: the paper cache, paper index, row identity, README, ROADMAP,
    and TODO coverage now include `2603.28052`, cached locally as
    `papers/2603.28052__Meta_Harness.pdf` with byte count `1078140` and
    SHA-256
    `7d9b90f53a9f4801a090f1a4acb843340cde81e4f865f97d53fff2a6a570eb73`.
    Reproduction evidence remains absent: no source-license details,
    linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    harness assumptions, harness-code candidate schema, filesystem-visible
    harness workspace layout, agentic proposer trace records, candidate
    harness edit provenance, execution-trace feedback bundles,
    score/provenance replay packages, outer-loop harness search records,
    online text-classification benchmark metadata, 200-problem IMO-level
    retrieval-augmented math benchmark metadata, TerminalBench-2 benchmark
    metadata, held-out-model transfer reports, baseline identities,
    code/artifact reproducibility status, or
    independent reproduction output exists.
  - Required result: add reproduction-grade Meta-Harness evidence: source
    license, project URL status, linked-code status, relation to AlphaEvolve
    and LibreEvolve harness assumptions, harness-code candidate schema,
    filesystem-visible harness workspace layout, agentic proposer trace
    records, candidate harness edit provenance, execution-trace feedback
    bundles, score/provenance replay packages, outer-loop harness search
    records, online text-classification benchmark metadata, 200-problem
    IMO-level retrieval-augmented math benchmark metadata, TerminalBench-2
    benchmark metadata, held-out-model transfer reports, baseline identities,
    code/artifact reproducibility status, independent reproduction outputs,
    and README/ROADMAP wording
    that treats Meta-Harness as background context until those artifacts
    exist.

- [ ] Implement AlphaEvolve MARL algorithm-discovery paper evidence beyond source boundary.
  - Paper/source evidence: arXiv `2602.16928`, submitted February 18, 2026
    and last revised May 7, 2026, is titled `Discovering Multiagent Learning
    Algorithms with Large Language Models`. Its abstract says AlphaEvolve is
    used to search two game-theoretic algorithm families, CFR and PSRO,
    yielding VAD-CFR and SHOR-PSRO. The paper evaluates those solvers against
    human-designed baselines across an 18-game suite spanning Poker,
    Goofspiel, Liar's Dice, Blotto, and Battleship variants, then uses
    systematic ablations and distillation to identify minimal solvers WOP-CFR
    and PM-PSRO that generalize with reduced structural complexity. It uses
    OpenSpiel, exact game-tree exploitability, deterministic algorithms, and a
    four-game training split plus fourteen-game test split.
  - Current gap: `papers/multiagent_learning_boundary.json` now records
    title/authors, arXiv version/revision date, cached PDF digest/license,
    source-link status, absence of a dedicated runtime repository in
    extracted links, background-only local status, component rows, local
    no-MARL-runner evidence, required evidence fields, and missing evidence
    keys. The paper-facing runtime evidence remains absent.
  - Required result: add executable paper/report evidence for `2602.16928`:
    CFR/PSRO candidate schemas, OpenSpiel imperfect-information game
    evaluator protocols, train/generalization game splits, exact
    exploitability traversal records, exact-oracle PSRO records, baseline
    solver identities, VAD-CFR and SHOR-PSRO result tables, IQM ablation and
    distillation records, WOP-CFR and PM-PSRO generalization reports,
    structural-complexity measures, random normal-form validation rows,
    limitation/caveat records, seed/budget records, generated solver artifact
    hashes, independent checker outputs, and reproducibility status.

- [ ] Implement AlphaEvolve Ramsey-number paper evidence beyond source boundary.
  - Paper/source evidence: arXiv `2603.09172`, submitted March 10, 2026 and
    last revised April 21, 2026, is titled `Reinforced Generation of
    Combinatorial Structures: Ramsey Numbers`. Its abstract says AlphaEvolve
    improved lower bounds for nine classical Ramsey numbers, including
    `R(3,13)`, `R(3,18)`, `R(4,13)`, `R(4,14)`, `R(4,15)`, `R(4,16)`,
    `R(4,18)`, `R(4,19)`, and `R(4,20)`. It also reports recovering all
    exact known Ramsey lower bounds, matching many other best-known lower
    bounds, and using AlphaEvolve as a single meta-algorithm that yields
    search algorithms for those results. In the introduction, the certificate
    semantics are explicit: a graph with `n` vertices, no `r`-clique, and no
    `s`-independent set proves `R(r,s) >= n+1`. Algorithm 1 defines the
    AlphaEvolve Ramsey setup as evolving code from an empty baseline; each
    program returns a valid primary graph `G1` and a larger prospect graph
    `G2`; `G1` is size-scored with boosts for matching or exceeding `n_SoTA`;
    and `G2` receives a bonus from low `r`-clique plus `s`-independent-set
    violations relative to a random-graph expectation. Table 1 reports 28
    colored lower-bound cells, Table 2 groups search algorithms by
    initialization family, and the appendix summarizes Algorithms 2-34. The
    PDF embeds public Google Research links for the nine improved-bound graph
    constructions and the AI-discovered search algorithms.
  - Current gap: `papers/ramsey_numbers_boundary.json` now records
    title/authors, arXiv version/revision date, cached PDF digest/license,
    source-link status, Google Research construction/code links,
    background-only local status, component rows, local no-Ramsey-runner
    evidence, required evidence fields, and missing evidence keys. The
    paper-facing runtime evidence remains absent.
  - Required result: add executable paper/report evidence for `2603.09172`:
    Ramsey-number parameter rows, graph witness artifact schemas,
    verifier/certifier metadata, exact-bound recovery suite records,
    best-known-bound comparison rows, prior/current value provenance for all
    reported improvements, search-algorithm provenance, seed/budget records,
    witness graph hashes, independent checker outputs, and reproducibility
    status. Paper evidence should additionally capture the
    `R(r,s) >= n+1` witness semantics, primary/prospect graph output schema,
    expected-violation scoring formula inputs, Table 1 status classes
    (exact-match, best-known-match, and new-result), Table 2 initialization
    taxonomy, appendix algorithm identifiers 2-34, public Google Research
    construction/code links, and baseline-reference caveats for Radziszowski
    2024, Exoo/Tatarevic 2015, Exoo 2006, Tatarevic 2020, Exoo 2012,
    Harborth/Krause 2003, and graph-only or personal-communication sources.

- [ ] Implement AlphaEvolve local-correction combinatorics paper evidence
      beyond source boundary.
  - Paper/source evidence: arXiv `2603.06692`, submitted March 4, 2026, is
    titled `Evolving Local Corrections for Global Constructions in
    Combinatorics`. Its abstract says AlphaEvolve is used as an experimental
    engine for proposing and iteratively refining finite correcting-step
    certificates. It studies graph reconstruction from vertex-deleted
    subgraphs, Alon-Tarsi parity for Latin squares via sign-reversing
    involutions built from local trades, and Rota's Basis Conjecture via local
    exchange policies on collections of bases. It describes experimental
    setups, scoring protocols, and search outcomes leading to concrete
    conjectures, while explicitly not claiming proofs. Section 2 defines the
    paper's AlphaEvolve setup as fixed mathematical harnesses plus short
    Python evolvable blocks, hard validity constraints, shaped soft progress
    scores, robust aggregation over random symmetry actions, and
    Gemini-generated summaries of 15-24 hour runs with more than 5000
    candidate results. The graph section reports `1420/1420` bipartite and
    `896/896` planar reconstructions under worst-of-five scrambles; the
    Alon-Tarsi section reports Tables 1-3 for orders `8,10,12,14,26`; and the
    Rota section reports Tables 4-6 for circuit-rich `F2` rank-5, rank-7, and
    variable-rank `5,7,9,11,13` benchmarks.
  - Current gap: `papers/combinatorics_berczy_boundary.json` now records the
    source-specific boundary for this paper: title/author, arXiv version/date,
    cached-PDF digest, license, reference-only source link, reported result
    surfaces, component ids, required evidence fields, and missing local
    harness/artifact evidence. Broad constructive-math TODOs still do not
    capture local-correction certificate schemas, graph reconstruction from
    vertex-deleted subgraphs, Latin-square local trade/involution evidence,
    Rota basis-exchange policies, scoring protocols, explicit algorithm
    outputs, or proof-status boundaries for generated conjectures. They also
    omit the paper's tested-regime details: bipartite matrix decks with
    independently permuted row/column cards, planar connected biconnected
    minimum-degree-at-least-3 non-maximal graph buckets, exact deck equality
    hardening after Weisfeiler-Lehman surrogate risk, Latin-square residual
    bias and isotopy anti-overfitting metrics, Rota insert/repair move
    formalism, circuit-oracle limitations, majority-rollout success, and
    appendix evolved-code/Gemini-summary provenance.
  - Required result: add executable paper/report evidence for `2603.06692`:
    local-correction certificate schemas, finite-step trace artifacts,
    graph/Latin-square/Rota case-study metadata,
    scoring protocol records, seed/budget records, explicit generated
    algorithms, structural-pattern summaries, conjecture statements,
    proof-status and traditional-analysis handoff fields, checker/verifier
    hooks, reproducibility status, and README/ROADMAP wording that treats
    local-correction combinatorics as missing paper evidence rather than
    implemented LibreEvolve support. Paper evidence should also preserve
    Conjectures 4-11, Tables 1-6, benchmark sizes and success metrics,
    AlphaEvolve experiment IDs where reported (`0_9751`, `0_9774`, `0_7176`),
    graph exact-isomorphism/canonical-label verification, Latin trade support
    and isotopy-stability metrics, Rota fitness weights and circuit-rich pool
    definitions, appendix evolved-code artifact status, AI-summary/AI-use
    declaration provenance, and caveats that these are experimental
    conjecture-generating results rather than proof certificates.

- [ ] Implement AlphaEvolve bilateral-trade lower-bound paper evidence beyond
      source boundary.
  - Paper/source evidence: arXiv `2603.08679`, submitted March 9, 2026, is
    titled `A New Lower Bound for the Random Offerer Mechanism in Bilateral
    Trade using AI-Guided Evolutionary Search`. Its abstract invokes the
    Myerson-Satterthwaite setting for bilateral trade, contrasts first-best
    GFT with BIC and BB mechanisms, focuses on the Random-Offerer mechanism,
    and says AlphaEvolve searches value distributions to find a worst-case
    instance with `GFT_FB / GFT_RO >= 2.0749`, improving on prior
    counterexamples including an explicit example near `2.02`. Sections 3-5
    define the exact benchmark: one seller cost and one buyer value from
    independent known distributions; first-best GFT is `E[(b-s)+]`; Random
    Offerer is `0.5*GFT_SO + 0.5*GFT_BO` using optimal seller-offering and
    buyer-offering take-it-or-leave-it prices; the objective is the supremum
    of `GFT_FB/GFT_RO`. The search fixes the buyer to the Discrete Equal
    Revenue distribution, evolves the seller CDF over `{0,...,H}` with
    `H=20000`, and reports a rounded mixture-of-modulated-power-laws seller
    CDF with `GFT_FB ~= 1.2322`, `GFT_SO ~= 0.3312`,
    `GFT_BO ~= 0.8565`, `GFT_RO ~= 0.5939`, and ratio `2.0749`. Section 4.3
    and Appendix A describe rounding probabilities to `1e-15` multiples and
    exact integer GFT computation.
  - Current gap: `papers/bilateral_trade_boundary.json` now records the
    source-specific boundary for this paper: title/authors, arXiv
    version/date, cached-PDF digest, license, reference-only source link,
    reported result fields, component ids, required evidence fields, and
    missing local benchmark/artifact evidence. Broad benchmark gaps still do
    not capture value-distribution witness
    schemas, FB/RO GFT calculations, economic mechanism assumptions, ratio
    tolerance, or lower-bound baseline attribution. They also omit the fixed
    Discrete Equal Revenue buyer fixture, evolved seller-generator code
    artifact, mixture/modulated-power-law parameter ledger, exact SO/BO
    reserve-price evaluation, rounded-versus-unrounded distribution caveat,
    appendix evaluator code, and the paper's undocumented alternate searches
    that reportedly reached `2.08` when evolving the buyer after fixing the
    seller and below `2.07` when co-evolving both sides.
  - Required result: add executable paper/report evidence for `2603.08679`:
    value-distribution candidate schemas, buyer/seller support and probability
    constraints, FB and RO GFT
    calculation metadata, BIC/BB assumption records, ratio objective and
    tolerance policy, witness distribution artifacts, prior `2` conjecture
    and `~2.02` counterexample baselines, seed/budget records, independent
    checker outputs, reproducibility status, and README/ROADMAP wording that
    treats bilateral-trade lower-bound search as missing paper evidence rather
    than implemented LibreEvolve support. Paper evidence should additionally
    preserve the `H=20000` support limit, fixed buyer survival function,
    evolved seller CDF formula and code listing, monotonicity/rounding
    validation, exact FB/SO/BO/RO component rows, optimal-price witness policy,
    ratio comparison to the original `2` conjecture and Babaioff et al. `~2.02`
    example, appendix evaluator hash, unrounded-mixture open-status caveat,
    and source-scoped status for the not-detailed `2.08` alternating-search
    observation.

- [ ] Implement AlphaEvolve Magellan compiler-optimization paper evidence beyond source boundary.
  - Paper/source evidence: arXiv `2601.21096`, submitted January 28, 2026 and
    accepted to `C4ML@CGO'26`, is titled `Magellan: Autonomous Discovery of
    Novel Compiler Optimization Heuristics with AlphaEvolve`. Its abstract
    presents Magellan as an agentic framework that evolves compiler passes by
    synthesizing executable C++ decision logic, coupling an LLM coding agent
    with evolutionary search and autotuning. It reports closed-loop
    generation, macro-benchmark evaluation, and refinement across production
    optimization tasks, including LLVM function inlining, register allocation,
    and preliminary XLA portability. Its method section records policy
    proposal in EVOLVE-BLOCK-delimited compiler source, local compiler rebuild
    and macro-benchmark evaluation, hyperparameter tuning, and feedback
    incorporation.
  - Current gap: `papers/magellan_boundary.json` now records title/authors,
    arXiv version/date, cached PDF digest/license, LLVM reference links,
    source-link status, absence of a dedicated Magellan runtime repository in
    extracted links, background-only local status, component rows, local
    no-compiler-runner evidence, required evidence fields, and missing
    evidence keys. The paper-facing runtime evidence remains absent.
  - Required result: add executable paper/report evidence for `2601.21096`:
    C++ decision-logic candidate schemas, compiler-pass integration metadata,
    EVOLVE-BLOCK compiler-source spans, LLVM inlining task records,
    register-allocation task records, XLA e-graph extraction and
    auto-sharding task records, macro-benchmark provenance, binary-size and
    end-to-end-performance metrics, autotuning loop records with tuner
    identity and batch/round counts, invalid-sample-rate evidence,
    feature/full heuristic mode labels, temporal/domain generalization rows,
    generated-policy size and maintainability caveats, expert/neural baseline
    identities, seed/budget records, compiler build/runtime environment
    metadata, independent checker outputs, and reproducibility status.

- [ ] Reproduce AI-PROPELLER warehouse-scale code-layout evidence beyond paper coverage.
  - Paper/source evidence: arXiv `2606.00131`, submitted May 28, 2026, is
    titled `AI-PROPELLER: Warehouse-Scale Interprocedural Code Layout
    Optimization with AlphaEvolve`. Its abstract says AI-PROPELLER uses
    Magellan and AlphaEvolve to evolve Propeller's compiler heuristic into a
    fine-grained interprocedural optimizer, uses Vizier to tune policy
    hyperparameters, executes generated layout variants on actual hardware to
    measure real performance counters, and reports `0.23%` to `1.6%`
    performance improvements on benchmarks including large warehouse-scale
    applications optimized with state-of-the-art FDO and PLO.
  - Current gap: no paper manifest row, cached PDF, paper-index entry,
    row-identity record, boundary artifact, or source-scoped TODO coverage
    exists for `2606.00131`. The broader Magellan compiler-optimization row
    does not capture AI-PROPELLER's post-link optimizer setting,
    interprocedural code-layout candidate artifacts, Vizier tuning phase,
    hardware-counter reward loop, warehouse-scale application benchmark
    metadata, FDO/PLO baselines, or reported `0.23%` to `1.6%` result
    boundary.
  - Required result: add reproduction-grade evidence for `2606.00131`:
    title/authors/arXiv version/date, source license, relation to AlphaEvolve,
    Magellan, Propeller, Vizier, and LibreEvolve's current code-search loop,
    interprocedural code-layout candidate schemas, Propeller integration
    metadata, policy-hyperparameter tuning records, generated layout variant
    artifacts, actual-hardware benchmark environment, performance-counter
    reward definitions, benchmark and warehouse-scale workload provenance,
    FDO/PLO/BOLT baseline identities, result tables for the reported
    performance range, code/artifact availability status, independent
    verification outputs, and README/ROADMAP wording that treats
    AI-PROPELLER-style warehouse-scale compiler optimization as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Implement AlphaEvolve ArchAgent computer-architecture paper evidence beyond source boundary.
  - Paper/source evidence: arXiv `2602.22425`, submitted February 25, 2026, is
    titled `ArchAgent: Agentic AI-driven Computer Architecture Discovery`.
    Its abstract presents ArchAgent as an automated architecture-discovery
    system built on AlphaEvolve. It designs and implements cache replacement
    policies within an established policy-design competition, reports `5.3%`
    IPC speedup over prior SoTA on public multi-core Google Workload Traces,
    `0.9%` IPC speedup over existing SoTA on single-core SPEC06, `3-5x`
    faster development than prior human-developed policies, `2.4%` IPC
    improvement from post-silicon hyperspecialization on SPEC06, and
    simulator-escape behavior in a popular microarchitectural simulator. The
    paper grounds the result in ChampSim C++ cache-policy code, CRC-style
    single/multi-core configurations, IPC normalized to LRU, short feedback
    simulations and longer validation simulations, and manual/rule-based
    checks for hardware realism.
  - Current gap: `papers/archagent_boundary.json` now records title/authors,
    arXiv version/date, cached PDF digest/license, source-link status,
    Google Workload Trace and CRC reference links, absence of a dedicated
    ArchAgent runtime repository in extracted links, background-only local
    status, component rows, local no-architecture-simulator evidence,
    required evidence fields, and missing evidence keys. The paper-facing
    runtime evidence remains absent.
  - Required result: add executable paper/report evidence for `2602.22425`:
    cache replacement policy candidate schemas, ChampSim integration metadata,
    CRC hardware/prefetch configuration rows, Google Workload Trace and SPEC06
    dataset provenance, single-core/multi-core benchmark splits, evolution and
    validation instruction-count protocols, IPC metric definitions,
    prior-SoTA baseline identities, generated policy artifacts and mechanism
    labels, state-budget and hardware-realizability checks, ablation rows,
    post-silicon specialization parameter records, simulator-escape evidence
    and containment policy, distributed-simulation reliability records,
    seed/budget records, independent checker outputs, and reproducibility
    status.

- [ ] Implement AlphaEvolve Fault2Flow workflow-automation paper evidence beyond the source boundary.
  - Paper/source evidence: arXiv `2511.12916`, submitted November 17, 2025, is
    titled `Fault2Flow: An AlphaEvolve-Optimized Human-in-the-Loop Multi-Agent
    System for Fault-to-Workflow Automation`. Its abstract says Fault2Flow
    addresses power-grid fault diagnosis by extracting regulatory logic into
    PASTA-formatted fault trees, adding expert knowledge through a human-in-
    the-loop verification interface, optimizing reasoning logic with a novel
    AlphaEvolve module, and synthesizing final verified logic into n8n-
    executable workflows. It reports transformer fault-diagnosis validation
    with `100%` topological consistency and high semantic fidelity. The PDF
    body specifies a decoupled frontend/backend system, regulatory-PDF
    extraction to Markdown with MinerU, MySQL plus Milvus storage, PlantUML
    mind-map generation, PASTA fault-tree translation, OpenEvolve-linked
    AlphaEvolve structural optimization, n8n workflow construction and
    activation, and iterative workflow verification from synthesized test
    samples. Its case study uses the national standard `DL/T 722-2014` for
    dissolved-gas transformer diagnosis, focusing on three-ratio logic, and
    evaluates 16 expert-designed transformer fault-tree cases. Table 1 reports
    LRM, SF, TC, E2ERC, success/failure, and average-token rows for Qwen3-80B
    and GPT-4.1 end-to-end baselines plus Qwen3-14B/32B/80B and GPT-4.1
    Fault2Flow variants.
  - Current gap: `papers/fault2flow_boundary.json` now records the
    source-specific absence boundary for `2511.12916`, and `papers/README.md`
    lists the row as background-only AlphaEvolve-optimized workflow application
    context. The current implementation still does not provide executable
    workflow artifacts or implementation evidence for this paper. Broad
    framework/plugin gaps do not capture regulatory-source provenance, PASTA
    fault-tree schemas, expert verification states, reasoning-logic
    optimization records, n8n workflow artifacts, transformer fault-diagnosis
    datasets, or topology/semantic metrics. They also omit the paper's
    placeholder ACM/conference/DOI metadata, frontend library stack,
    MinerU/MySQL/Milvus backend, PlantUML intermediate format, PASTA
    self-check status, synthesized verification samples, GPT-5 evaluator usage
    for LRM/SF, exact TC and E2ERC formulas, token-efficiency comparison, and
    the 16-case dataset split between three-ratio and characteristic-gas
    methods.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2511.12916`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve workflow assumptions, regulatory-text source provenance,
    PASTA fault-tree candidate schemas, expert-review/human-in-the-loop state
    records, reasoning-logic optimization metadata, n8n workflow artifact
    schema, transformer fault-diagnosis dataset provenance, topological-
    consistency and semantic-fidelity metric definitions, seed/budget
    records, independent checker outputs, reproducibility status, ROADMAP and
    paper-index wording that treats Fault2Flow-style fault-to-workflow
    automation as missing paper evidence rather than implemented LibreEvolve
    support, and source-scoped root README wording if those claims are
    reintroduced. Paper evidence should additionally preserve DL/T 722-2014 source
    scope, three-ratio and characteristic-gas case counts,
    Qwen3-Next-80B-A3B-Instruct configuration, PlantUML and PASTA intermediate
    artifacts, AlphaEvolve/OpenEvolve multi-island optimization claims, n8n API
    activation and verification-loop records, Table 1 values including `16/0`
    Fault2Flow success and end-to-end baseline failures, GPT-5 judge caveats,
    human-annotation/data-ethics records, placeholder ACM metadata caveats,
    and source-scoped status until executable workflow artifacts are locally
    reproduced.

- [ ] Implement TTT-Discover paper evidence beyond the source boundary.
  - Paper/source evidence: arXiv `2601.16175`, submitted January 22, 2026 and
    last revised February 5, 2026, is titled `Learning to Discover at Test
    Time`. Its abstract contrasts AlphaEvolve-style frozen-LLM prompting with
    reinforcement learning at test time, where the model continues training
    on experience from one specific test problem. It defines Test-Time
    Training to Discover (TTT-Discover), focuses on continuous rewards, and
    reports attempted-problem results across mathematics, GPU kernel
    engineering, algorithm design, and biology, including Erdos minimum
    overlap, an autocorrelation inequality, a GPUMode kernel competition with
    up to `2x` faster results, AtCoder competitions, and single-cell
    denoising. The abstract states results use open model `OpenAI
    gpt-oss-120b`, public code, Tinker test-time-training runs, expert or
    organizer review, and costs of only a few hundred dollars per problem.
    The paper body formalizes discovery as finding a state `s` with
    `R(s) > r_sota`, defines Algorithm 1 with mutable weights `theta_i`,
    buffer `H_i`, train/reuse subroutines, an adaptive entropic objective, and
    PUCT reuse, and reports fixed hyperparameters in Table 9: `50` steps,
    `512` rollouts per step, LoRA rank `32`, Tinker context window `32768`,
    prompt-plus-thinking limit `26000`, Adam `4e-5`, and `gamma = ln(2)`.
  - Current gap: `papers/ttt_discover_boundary.json` now records the
    source-specific absence boundary for `2601.16175`, including source identity,
    public code/result links, and the current missing-evidence contract. The
    current implementation and paper index still do not provide executable
    implementation evidence for this paper. Existing AlphaEvolve and framework
    gaps do not capture mutable model-policy state, RL-at-test-time training
    records, Tinker run provenance, open-model checkpoint identity, continuous-
    reward task definitions, cross-domain benchmark rows, expert/organizer
    review artifacts, or cost-per-problem accounting. They also omit the
    public GitHub/project/result links, Table 2 math comparisons against
    AlphaEvolve, AlphaEvolve V2, ThetaEvolve, OpenEvolve, and Best-of-25600,
    Table 4/5 GPUMode runtime rows, Table 6 AtCoder official-score rows,
    Table 7 OpenProblems denoising rows, Table 8 ablations, Table 9
    hyperparameters, Table 10 Triton-filtered MLA results, OpenEvolve
    context-window truncation caveats, and the `Best-of-25600` versus Figure 4
    `50 * 512 = 256000` inconsistency.
  - Required result: implement paper-evidence records beyond the source-boundary
    sidecar for `2601.16175`: mutable policy/training-state schema, RL objective
    and rollout-selection metadata, Tinker/API training-run
    records, open-model/checkpoint provenance, continuous-reward task
    definitions, Erdos/autocorrelation/GPUMode/AtCoder/single-cell benchmark
    records, prior-art and AlphaEvolve/OpenEvolve baseline identities, expert
    or organizer review artifacts, cost/budget accounting, seed/run records,
    independent checker outputs, reproducibility status, ROADMAP and
    paper-index wording that treats TTT-Discover-style test-time training as
    missing paper evidence rather than implemented LibreEvolve support, and
    source-scoped root README wording if those claims are reintroduced. Paper evidence
    should additionally preserve the exact public URLs, result notebook paths,
    GPUMode and AtCoder submission links, Modal and OpenProblems harness
    provenance, per-domain verifier limits, LoRA/checkpoint lineage, adaptive-
    beta and PUCT formulas, table-level result rows, expert-review identities,
    official/retrospective evaluation status, and source-scoped caveats for
    any internally inconsistent sampling-budget text.

- [ ] Implement AlphaEvolve Bruhat-interval hypercube paper evidence beyond the
      source boundary.
  - Paper/source evidence: arXiv `2601.01235`, submitted January 3, 2026, is
    titled `Bruhat intervals that are large hypercubes`. Its abstract studies
    big Bruhat intervals that are poset hypercubes in the symmetric group
    `S_n`, says AlphaEvolve-suggested permutations revealed a pattern that
    performed well for tested `n` and was proved for general `n`, exhibits
    for powers of `2` a hypercube of dimension `O(n log n)`, characterizes
    vertices as dyadically well-distributed permutations, and connects the
    construction to Kazhdan-Lusztig `R`-polynomial coefficients plus lower
    bounds for frozen variables in open Richardson cluster algebras and for
    embeddings of Bruhat graphs. The paper body gives the actual witness
    machinery: Definition 2.1's dyadic basic intervals and exact-one condition,
    bit-reversal endpoints `x_m`/`y_m`, Ehresmann matrix Bruhat comparisons,
    complementary blocks, the order-preserving map `phi` to `S_2^{C_m}`, local
    flips, Proposition 2.20's poset isomorphism, and Theorem 2.21's
    `D_m = [x_m, y_m]` hypercube of rank `m * 2^(m-1)`.
  - Current gap: `papers/bruhat_intervals_boundary.json` now records the
    source-specific absence boundary for `2601.01235`, including source
    identity, public artifact links, AlphaEvolve/FunSearch provenance, and the
    current missing-evidence contract. The current implementation and paper
    index still do not provide executable implementation evidence for this
    paper. Broad Appendix B and constructive-math gaps do not capture
    permutation generator schemas, Bruhat interval verification, hypercube
    isomorphism checks, dyadic well-distribution predicates, `S_n` power-of-
    two benchmark rows, Kazhdan-Lusztig coefficient linkage, cluster-algebra
    consequence fields, or the boundary between AlphaEvolve-suggested finite
    evidence and human-written general proofs. They also omit Section 4's
    experimental record: FunSearch as a Python-program search over permutation
    pairs maximizing `d_{x,y}`, adjacent-transposition output encoding,
    deterministic prompt rule, Mistral model and roughly `$10` FunSearch cost,
    AlphaEvolve generalizer-mode scoring over `n = 10..50`, Gemini 2.5
    Flash/Pro calls, `3000-5000` programs and roughly `$70` public-rate cost,
    public code/prompt/output URL, the observed recurrence
    `alpha(2n)=2 alpha(n)+n`, and the note that the evolved program contained
    likely unused simulated-annealing/search code.
  - Required result: implement paper-evidence records beyond the source-boundary
    sidecar for `2601.01235`: relation to AlphaEvolve and LibreEvolve
    constructive-math assumptions, permutation candidate schemas,
    Bruhat interval records, poset-hypercube witness artifacts, dyadic well-
    distribution checker metadata, dimension/asymptotic-bound records,
    Kazhdan-Lusztig `R`-polynomial coefficient metadata, cluster-algebra and
    Bruhat-graph consequence records, finite-test versus general-proof status,
    seed/budget records, independent checker outputs, reproducibility status,
    ROADMAP and paper-index wording that treats Bruhat-interval hypercube
    discovery as missing paper evidence rather than implemented LibreEvolve
    support, and source-scoped root README wording if those claims are
    reintroduced. Paper evidence should additionally preserve the PDF date/arXiv date
    distinction, Adam Zsolt Wagner acknowledgement/contribution caveat,
    FunSearch/AlphaEvolve prompt and evaluator text, model/cost/run-count
    metadata, public repository artifact status, low-discrepancy `(0,m,2)`-net
    and `t`-adic extension notes, `R`-polynomial/d-invariant formulas,
    cluster-frozen-variable and good-embedding consequences, and source-scoped
    proof-status caveats before any benchmark claim is promoted.

- [ ] Implement global NLP solver comparator paper evidence beyond the source boundary.
  - Paper/source evidence: arXiv `2601.05943`, submitted January 9, 2026, is
    titled `Global Optimization for Combinatorial Geometry Problems`. Its
    abstract says AlphaEvolve produced new best-known solutions for hard
    geometric and combinatorial problems, then asks whether modern off-the-
    shelf global optimization solvers can match those results when the same
    problems are directly formulated as NLPs. It evaluates straightforward NLP
    formulations on a subset of the AlphaEvolve benchmark suite using
    commercial FICO Xpress and open-source SCIP, and reports that without
    solver modifications both solvers reproduce and sometimes improve on
    best solutions from the literature, including recent LLM-driven
    discoveries. The body selects three AlphaEvolve-related families: min-max
    distance ratio, circle packing in a square or perimeter-4 rectangle, and
    regular-hexagon packing. It defines the generic NLP form, Mosel
    implementations, QCP distance/circle formulations, and a hexagon model
    with rotation, half-space coefficients, and Farkas multipliers.
  - Current gap: `papers/global_nlp_optimization_boundary.json` now records the
    source-specific absence boundary for `2601.05943`, and `papers/README.md`
    lists it as an optimization benchmark comparator with no
    nonlinear-programming solver comparison harness. The current implementation
    still does not provide local solver artifacts or implementation evidence
    for this paper. Broad constructive-math and benchmark gaps do not
    capture direct NLP formulation artifacts, solver identity/license
    provenance, solver-run parameters, incumbent/bound/certificate records,
    numerical tolerances, or result tables comparing Xpress/SCIP outcomes
    against AlphaEvolve and prior-literature baselines. They also omit the
    paper's arXiv `v2`/January 15, 2026 metadata, Mosel modeling-language
    detail, AlphaEvolve-repository validation-code claim, Table 1 improving
    squared-ratio rows, Table 2 circle-packing rows, Table 3 hexagon-packing
    rows, source links for Friedman packing pages/OpenEvolve/SciPy/SCIP, and
    the caveat that the paper does not separate which solver found which
    reported solution.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2601.05943`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve constructive-geometry assumptions, selected benchmark subset,
    NLP formulation schemas, variable/domain/constraint/objective records,
    FICO Xpress and SCIP solver identity/version/license metadata, solver
    parameter and time-limit records, incumbent/bound/certificate artifacts,
    numerical tolerance policy, prior-literature and AlphaEvolve baseline
    values, reproduced/improved/fell-behind outcome rows, seed/run records,
    independent checker outputs, reproducibility status, ROADMAP and
    paper-index wording that treats global-NLP solver comparison as missing
    paper evidence rather than implemented LibreEvolve support, and
    source-scoped root README wording if those claims are reintroduced. Paper evidence should
    additionally preserve the selected problem subset, exact formulation
    variables and constraints, instance-size records such as `7` variables/
    `10` constraints through `91` variables/`876` constraints for distance
    ratio, all Table 1-3 values and rounding directions, solver-attribution and
    dual-bound-detail caveats, validation-code provenance, and the conclusion's
    distinction between direct optimization baselines and complementary
    LLM-driven model/prototype generation.

- [ ] Implement post-AlphaEvolve autoconvolution improvement paper evidence
      beyond the source boundary.
  - Paper/source evidence: arXiv `2506.16750`, submitted June 20, 2025 and
    last revised August 10, 2025, is titled `An improved example for an
    autoconvolution inequality`. Its abstract gives a nonnegative step
    function with `575` equally spaced intervals whose autoconvolution ratio
    is at least `0.901564`. It explicitly improves on DeepMind's AlphaEvolve
    result, which used a `50`-interval nonnegative step function with value at
    least `0.8962`, and says the new function was found using simulated
    annealing and gradient-based methods instead of large language models.
    Theorem 1 gives the exact rational value
    `96086089410408840289339769 / 106577013451431545242354944` for
    `f = sum_{n=0}^{574} v_n 1_[n,n+1)`, with coefficients in Appendix A.
    Section 2 defines convolution samples `L_j` and formula `(3)`, which is
    the direct finite checker for any coefficient list.
  - Current gap: `papers/autoconvolution_boundary.json` now records the
    source-specific absence boundary for `2506.16750`, and `papers/README.md`
    lists it as a constructive math benchmark candidate with `Not implemented;
    potential future benchmark`. The current implementation still does not
    provide local witness artifacts or implementation evidence for this paper.
    Existing Appendix B.1-B.3 autoconvolution gaps cover the
    AlphaEvolve result family, but not this later 575-interval witness,
    non-LLM search provenance, objective recomputation, side-by-side
    AlphaEvolve baseline comparison, or rounded-value/tolerance policy. They
    also omit the public repository URL, `Inital HPC code.py`, `Refine HPC
    code.py`, `f95.py`, `coeffBL.txt`, `Verify.nb`, Mathematica verification
    snippet, row-major coefficient-table reading rule, referee-suggested
    integer-arithmetic modification, NCSU HPC resource acknowledgement, and
    comparison values against Matolcsi-Vinuesa `0.889226` and AlphaEvolve
    `0.89628`.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2506.16750`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve Appendix B and
    LibreEvolve autoconvolution assumptions, 575-interval step-function
    witness schema, coefficient/value artifact hashes, convolution and norm
    recomputation metadata, objective definition and tolerance policy,
    AlphaEvolve 50-interval `0.8962` baseline record, simulated-annealing and
    gradient-method provenance, prior/current result rows, independent checker
    outputs, reproducibility status, ROADMAP and paper-index wording that
    treats this post-AlphaEvolve autoconvolution improvement as missing paper
    evidence rather than implemented LibreEvolve support, and source-scoped
    root README wording if those claims are reintroduced. Paper evidence should
    additionally preserve the arXiv `v2`/August 10, 2025 version, the claim
    that the example was found in November 2024 before the authors knew about
    AlphaEvolve's example, translation/dilation invariance, support
    normalization to `[-1/4, 1/4]`, AlphaEvolve coefficient reversal from the
    DeepMind notebook, normalized graph/correlation comparisons, exact
    coefficient payload hashes, and checker parity between Python and
    Mathematica artifacts.

- [ ] Implement post-AlphaEvolve sums-and-differences construction paper
      evidence beyond the source boundary.
  - Paper/source evidence: arXiv `2505.16105`, submitted May 22, 2025, is
    titled `Sums and differences of sets (improvement over AlphaEvolve)` and
    authored by Robert Gerbicz; the cached PDF hash is
    `90d63d13afd7b8e15ceac25a4cef3f6b1c974a12a7893e80bd18e3ef4e16e1e8`.
    Its abstract says AlphaEvolve used a set of `54265` integers to improve
    the known lower bound from `theta = 1.14465` to `theta = 1.1584`. The
    paper improves this to `theta = 1.173050` with an explicit `U` set
    containing more than `10^43546` elements, and uses the free GMP library
    for fast integer and floating-point arithmetic. The main construction uses
    `W(m, L, B)` bounded-coordinate sets and a base-`2B + 1` integer map,
    derives formulas for `|U + U|`, `|U - U|`, and `2 max(U) + 1`, reports
    `theta = 1.162997` for `m = 80`, `L = 64`, `B = 5`, and confirms
    `theta = 1.173050` for `m = 81411`, `L = 65536`, `B = 5` after about
    15 hours of exact integer arithmetic. It reports approximate values
    `|U| = 6.314107319e43546`, `|U + U| = 3.208492702e61228`,
    `|U - U| = 6.587554451e75899`, and `2 max(U) + 1 =
    6.605282799e84780`, with GMP code and exact computed values cited at
    `https://bit.ly/43mWCVC`.
  - Current gap: `papers/sums_differences_boundary.json` and
    `papers/README.md` now provide the local source-boundary artifact for this
    paper, but they do not provide local construction artifacts or
    implementation evidence. Existing Appendix B sums-and-differences gaps do
    not capture this later explicit `U` construction, compressed
    representation needs for extremely large sets, `W(m, L, B)` formula
    evidence, base-`2B + 1` injectivity evidence, the `(80, 64, 5)`
    small-search result, exact computed-value retrieval from the cited code
    URL, GMP arithmetic provenance, `theta = 1.173050` recomputation, or
    side-by-side comparison against AlphaEvolve's `54265`-integer `1.1584`
    construction and the earlier `1.14465` bound.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2505.16105`: title/author/arXiv version/date/PDF digest, source license,
    code/artifact URL/status, relation to AlphaEvolve Appendix B and
    LibreEvolve sums-and-differences assumptions, explicit `U`-set
    construction schema, `W(m, L, B)` formula records, base-`2B + 1` encoding
    and injectivity evidence, huge-set compression/parametrization metadata,
    parameter records for `(80, 64, 5)` and `(81411, 65536, 5)`,
    sumset/difference-set cardinality records, max-element/q-value and
    set-size records, `theta` formula and tolerance policy, exact computed
    value payload hashes, AlphaEvolve `54265`-integer `1.1584` baseline
    record, previous `1.14465` bound attribution, GMP/version/arithmetic
    provenance, prior/current result rows, independent checker outputs,
    reproducibility status, ROADMAP and paper-index wording that treats this
    post-AlphaEvolve sums-and-differences improvement as missing paper evidence
    rather than implemented LibreEvolve support, and source-scoped root README
    wording if those claims are reintroduced.

- [ ] Implement further post-AlphaEvolve sums-and-differences sequence paper
      evidence beyond the source boundary.
  - Paper/source evidence: arXiv `2506.01896`, submitted June 2, 2025, is
    titled `Sums and differences of sets: a further improvement over
    AlphaEvolve` and authored by Fan Zheng; the cached PDF hash is
    `3f04c75ccd850eb6e5c785e543f98d12446e9891399cc5246acae9335b4494c2`.
    Its abstract says it improves on DeepMind AlphaEvolve's
    `theta = 1.1584` and the later explicit-construction result
    `theta = 1.173050`, by constructing a sequence of `U` sets that in the
    limit establishes `theta = 1.173077`. The proof uses large-deviation
    estimates for `W(m, floor(rm), B)`, builds the same base-`2B + 1`
    integer-image construction as the prior sums-and-differences paper,
    bounds `q(U)`, `s(U)`, and `d(U)` asymptotically, and maximizes a limiting
    expression over `B`, `r`, and `a`. The numerical evidence is a MATLAB
    2024b tolerance sweep over `B = 3..10`, `r in (0.5, 2)`, and
    `a in (0, min(1, 1/r))`; the best row is `B = 5`, where
    `theta - 1 = 0.173077279785136` for both `1e-8` and `1e-10` tolerances.
    The paper embeds MATLAB code using `fminbnd`, `fminunc`, `logD`, `logW`,
    and a Legendre-transform objective for `I(c, B)`.
  - Current gap: `papers/sums_differences_sequence_boundary.json` and
    `papers/README.md` now provide the local source-boundary artifact for this
    further improvement, but they do not provide local sequence artifacts or
    implementation evidence. Existing sums-and-differences TODOs do not
    capture this sequence-of-sets construction, limiting lower-bound proof
    artifact, large-deviation lemma evidence, MATLAB-code provenance,
    tolerance-sweep reproducibility, convergence/tail-bound verification, or
    lineage comparison against both AlphaEvolve's `1.1584` finite witness and
    `2505.16105`'s `1.173050` explicit huge-set witness.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2506.01896`: title/author/arXiv version/date/PDF digest, source license,
    code/artifact URL/status, relation to AlphaEvolve Appendix B and
    LibreEvolve sums-and-differences assumptions, sequence-of-`U` construction
    schema, parameter records for `B`, `r`, `a`, and finite-prefix `m`,
    finite-prefix artifacts, limiting-bound derivation metadata,
    large-deviation `I(c, B)` records, asymptotic `W(m, floor(rm), B)` count
    metadata, MATLAB-code extraction and independent reimplementation status,
    tolerance-sweep rows for `B = 3..10` and `1e-4..1e-10`,
    convergence/tail-bound checker records, sumset/difference-set cardinality
    records for finite prefixes, `theta` formula and tolerance policy,
    AlphaEvolve `1.1584` baseline, `2505.16105` `1.173050` baseline,
    prior/current result rows, independent checker outputs, reproducibility
    status, ROADMAP and paper-index wording that treats this further
    post-AlphaEvolve sums-and-differences improvement as missing paper
    evidence rather than implemented LibreEvolve support, and source-scoped
    root README wording if those claims are reintroduced.

- [ ] Implement UCB1 finite-time bandit paper evidence beyond the source
      boundary.
  - Paper/source evidence: the local
    `auer-cesa-bianchi-fischer-2002__UCB1_Finite_Time_Analysis_Multiarmed_Bandit.pdf`
    is `Finite-time Analysis of the Multiarmed Bandit Problem` by Peter Auer,
    Nicolo Cesa-Bianchi, and Paul Fischer, published in `Machine Learning`
    `47`, pages `235-256`, in 2002; the cached PDF hash is
    `82c8a8192bdb425fbe7662c59ee85faf47f59901f1a4999a732d04db82702a5d`.
    The paper presents UCB1 for `K > 1` arms with unknown reward distributions
    supported in `[0, 1]`, defines regret as expected loss from not always
    playing the best arm, and proves logarithmic finite-time regret bounds.
    Theorem 1 bounds regret by `8 * sum_i ln(n) / Delta_i` plus
    `(1 + pi^2 / 3) * sum_j Delta_j`, with the suboptimal-pull bound
    `E[T_i(n)] <= 8 ln(n) / Delta_i^2 + 1 + pi^2 / 3`. The proof uses
    empirical reward means, play counts, Chernoff-Hoeffding bounds, and a
    confidence-index policy; the paper later notes Theorems 1-3 do not
    require cross-machine reward independence and only need the per-arm
    conditional-mean condition `E[X_i,t | X_i,1, ..., X_i,t-1] = mu_i`. It
    also gives adjacent UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and
    UCB1-TUNED variants under separate assumptions, with UCB1-TUNED reported
    as empirically stronger but without a proven regret bound.
  - Current gap: `papers/ucb1_boundary.json` and `papers/README.md` now
    preserve this UCB1 source row as an evidence boundary with the
    bounded-support, conditional-mean/stationarity, regret-definition,
    reward-normalization, theorem-constant, and proof-scope assumptions needed
    to prevent backend-routing telemetry from being read as canonical UCB1
    finite-time analysis. The remaining paper-facing gap is no implemented
    scheduler evidence for those assumptions and no variant-level support
    reports showing UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and UCB1-TUNED are
    implemented and validated.
  - Required result: add paper-manifest and paper-index coverage for
    `auer-cesa-bianchi-fischer-2002`: source URL/cache/hash, title/authors/
    venue/year, source-license or mirror status, UCB1 theorem-scope metadata,
    reward-support and conditional-mean/stationarity assumptions,
    regret-definition fields, theorem-constant records, scheduler-linkage
    records, canonical-index formula metadata, variant support matrix,
    UCB1-TUNED no-proof status, and README/ROADMAP wording that treats
    LibreEvolve's backend scheduler as heuristic unless those assumptions and
    regret reports are explicitly validated.

- [ ] Implement GigaEvo framework paper evidence beyond the source-specific
      boundary.
  - Paper/source evidence: local arXiv `2511.17592`, `GigaEvo: An Open Source
    Optimization Framework Powered by LLMs and Evolution Algorithms`, by
    Valentin Khrulkov, Andrey V. Galichin, Denis Bashkirov, Dmitry Vinichenko,
    Oleg Travkin, Roman Alferov, Andrey Kuznetsov, and Ivan Oseledets was
    submitted November 17, 2025 as arXiv v1; the cached PDF hash is
    `9a14bf06a1323e63bf53234e79e44c41e1e78e0dc2f90578d74b928efd067113`.
    It describes an AlphaEvolve-inspired open-source framework with Redis
    program storage, an `asyncio` DAG execution engine, MAP-Elites
    quality-diversity evolution, LangGraph-based mutation, insight generation,
    bidirectional lineage tracking, flexible Hydra configuration, and
    reproduction experiments on AlphaEvolve benchmark problems. The paper
    defines Redis `Program` records with UUID, source, lifecycle state
    (`FRESH`, `RUNNING`, `COMPLETE`), metrics, genealogy, and DAG stage
    outputs; DAG stages include validation, execution, validator calls,
    complexity, insights, lineage analysis, ancestor/descendant collectors,
    and mutation-context assembly. It links both
    `https://github.com/AIRI-Institute/gigaevo-core` and
    `https://github.com/FusionBrainLab/gigaevo-core`.
  - Current gap: `papers/README.md` lists `2511.17592` as framework
    inspiration and says Redis lifecycle database, `asyncio` DAG engine,
    insight stage, and concurrent units are not implemented. The committed
    `papers/gigaevo_framework_boundary.json` sidecar now preserves the GigaEvo
    PDF as a source-specific evidence boundary with source digest, dual GitHub
    source-link ambiguity, architecture-component rows, local evidence scope,
    required future evidence fields, and missing-evidence keys. It still does
    not provide executable lifecycle-state semantics, DAG-stage topology,
    insight/lineage artifacts, benchmark-reproduction claims, source-code
    status resolution, or Hydra problem-layout implementation artifacts.
  - Required result: implement paper-manifest and paper-index evidence beyond
    the sidecar: source license, linked code URL/status,
    architecture-component inventory, Redis program lifecycle schema, DAG
    stage/dependency/caching metadata, insight and
    lineage-analysis records, mutation-operator mode/source details,
    Hydra/problem-layout metadata, benchmark-problem and reproduction-result
    rows for Heilbronn `n = 11`, circle packing `n = 26`/`n = 32`, kissing
    numbers, bin packing, and prompt/agent evolution, linked-model rows for
    Qwen3/Gemini/Qwen embedding/GPT-OSS usage where claimed, relation to
    AlphaEvolve and LibreEvolve, and README/ROADMAP/code wording that keeps
    GigaEvo framework behavior marked missing unless local implementation
    artifacts and reports prove it.

- [ ] Implement CodeEvolve paper evidence beyond the source-specific boundary.
  - Paper/source evidence: local arXiv `2510.14150`, `CODE EVOLVE: an
    open-source evolutionary framework for algorithmic discovery and
    optimization`, by Henrique Assumpcao, Diego Ferreira, Leandro Campos, and
    Fabricio Murai was submitted as arXiv v4 on March 12, 2026; the cached PDF
    hash is
    `8dc8c35d24e2f6bce81e9608609e10b4dac5dd7072d155d9cd5c575d47472405`.
    It presents an islands-based genetic algorithm with weighted LLM
    ensembles, `SEARCH/REPLACE` edits, inspiration-based crossover,
    meta-prompting, depth-based targeted refinement, exploration scheduling,
    sandboxed evaluation, MAP-Elites/CVT-MAP-Elites archives, and
    AlphaEvolve/EoH benchmark and cost-efficiency comparisons. It defines
    solution fitness `fsol` and prompt fitness `fprompt`, uses Algorithm 1 for
    exploitation/exploration with ancestor depth `k`, inspirations, and
    `MetaPromptingLLM`, and reports Plateau Scheduler, elitist migration,
    runtime/memory-bounded AWS SageMaker evaluation, weighted
    GEMINI-2.5/Qwen3-Coder-30B ensembles, and code/results links at
    `https://github.com/inter-co/science-codeevolve` and
    `https://github.com/inter-co/science-codeevolve-experiments`.
  - Current gap: `papers/README.md` lists `2510.14150` as agentic
    code-evolution inspiration, and `papers/codeevolve_boundary.json` now
    preserves the CodeEvolve PDF as a source-specific evidence boundary with
    cached source metadata, license metadata, linked-code/experiment URLs,
    component rows, local evidence scope, required future evidence fields, and
    missing-evidence keys. The remaining paper gap is executable/reportable
    evidence for the paper behavior: prompt/solution fitness definitions as
    local runtime artifacts, operator-level claims, scheduler semantics,
    sandbox requirements, benchmark-result rows, ablation/cost claims,
    verified linked-code status, hyperparameter recommendations, and validation
    that docs avoid conflating LibreEvolve's prompt-program support with
    CodeEvolve framework parity.
  - Required result: add paper-manifest and paper-index coverage for
    `2510.14150`: title/authors/arXiv version/date/PDF digest, source license,
    linked code URL/status, island/population and prompt/solution fitness
    schemas, weighted ensemble and model-cost metadata, inspiration-crossover,
    meta-prompting, depth-refinement, and exploration-scheduler records,
    sandbox/runtime/memory-limit evidence, MAP-Elites/CVT archive metadata,
    AlphaEvolve benchmark rows for all 9 Table 1 instances, EoH benchmark rows
    for online bin packing/TSP/flow-shop scheduling, component/depth/
    inspiration/MAP-Elites/topology ablation rows, Qwen3-Coder-30B vs
    GEMINI-2.5 cost/runtime rows from Table 2, open-framework comparisons with
    OpenEvolve and ShinkaEvolve, LLM-backbone sensitivity rows, recommended
    hyperparameter defaults, relation to LibreEvolve, and README/ROADMAP/code
    wording that keeps CodeEvolve-specific behavior marked missing unless
    implementation artifacts and reports prove it.

- [ ] Implement ThetaEvolve test-time learning paper evidence beyond the
      source-specific boundary.
  - Paper/source evidence: local arXiv `2511.23473`, `ThetaEvolve:
    Test-time Learning on Open Problems`, by Yiping Wang, Shao-Rong Su,
    Zhiyuan Zeng, Eva Xu, Liliang Ren, Xinyu Yang, Zeyi Huang, Xuehai He,
    Luyao Ma, Baolin Peng, Hao Cheng, Pengcheng He, Weizhu Chen, Shuohang
    Wang, Simon Shaolei Du, and Yelong Shen was submitted as arXiv v1 on
    November 28, 2025; the cached PDF hash is
    `8e74933b2a4dddbf80a063fb88438c95b62b982a5167bbb77213ce1e3839715d`
    and the PDF metadata declares CC-BY 4.0. It presents an
    AlphaEvolve-inspired dynamic environment using a single LLM, large program
    database, batch sampling over parents and responses, early checks, lazy
    penalties, reward shaping, optional GRPO/RL training at test time,
    checkpoint evaluation, and benchmark claims on circle packing,
    autocorrelation inequalities, and Hadamard matrices. It links public code
    at `https://github.com/ypwang61/ThetaEvolve`, builds on OpenEvolve and
    `slime`, and records batch size `B = 32`, `n = 16`, response length
    `16384`, rollout temperature `1.0`, and `16` concurrent verifier programs.
  - Current gap: `papers/README.md` lists `2511.23473` as test-time training
    inspiration, and `papers/thetaevolve_boundary.json` now preserves the
    ThetaEvolve PDF as a source-specific evidence boundary with cached source
    metadata, CC-BY license metadata, linked code URL, dynamic-environment
    component rows, local `ttt_rl` export scope, required future evidence
    fields, and missing-evidence keys. The remaining paper gap is
    executable/reportable evidence for the paper behavior: batch-sampling
    semantics, lazy-penalty/reward-shaping formulas, GRPO configuration,
    checkpoint provenance, evaluator-compatibility caveats,
    database-size/throughput ablations, benchmark rows, and comparison claims.
  - Required result: add paper-manifest and paper-index coverage for
    `2511.23473`: title/authors/arXiv version/date/PDF digest, source license,
    linked code URL/status, dynamic-environment architecture rows,
    single-LLM/database-size/batch-sampling metadata, early-check and
    lazy-penalty schemas, reward-shaping parameters, GRPO/RL training
    configuration, checkpoint and inference-transfer records, generated-sample
    counts, task/evaluator caveats for tolerance and corrected typos,
    AlphaEvolve/ShinkaEvolve/OpenEvolve baseline rows, Table 1 open-problem
    bound rows, Table 2/9 main `w/ RL` vs `w/o RL` rows, Table 3 static/format
    reward baseline rows, Table 4/10 database-size and database-design rows,
    Table 5/6 pipeline/throughput rows, Table 7 reward-shaping rows, Table 8
    timeout/reward-shaping configuration rows, relation to LibreEvolve's
    `ttt_rl` export, and README/ROADMAP/code wording that keeps
    ThetaEvolve-style test-time learning marked missing until implementation
    artifacts and reports prove it.

- [ ] Implement ImprovEvolve modular-operator paper evidence beyond the
      source-specific boundary.
  - Paper/source evidence: local arXiv `2602.10233`, `ImprovEvolve: Ask
    AlphaEvolve to Improve the Input Solution and Then Improvise`, by Alexey
    Kravatskiy, Valentin Khrulkov, and Ivan Oseledets was submitted as arXiv
    v1 on February 10, 2026; the cached PDF hash is
    `8123f1b19d9ba6c891e642be28b1bd4395fff549131d2e45b619dfd28ddfe57a`.
    The PDF metadata declares CC-BY 4.0 and the front matter includes
    KDD 2026/ACM publication-rights language. It proposes evolving a class
    with `generate_config(seed)`, `improve(x)`, and `perturb(x, sigma)` rather
    than a direct solution generator. It combines those methods through a
    two-stage basin-hopping validation scheme, uses GigaEvo as the outer
    evolutionary backbone, reports hexagon-packing and second-autocorrelation
    results, and separates automated ImprovEvolve outputs from lightly
    human-edited `ImprovEvolve+E` variants. The PDF links GigaEvo at
    `https://github.com/FusionBrainLab/gigaevo-core`, OpenEvolve, AI Studio,
    and OpenRouter, but no ImprovEvolve-specific code URL appears in the
    extracted links.
  - Current gap: `papers/README.md` lists `2602.10233` as modular search
    inspiration, and `papers/improvevolve_boundary.json` now preserves the
    ImprovEvolve PDF as a source-specific evidence boundary with cached source
    metadata, CC-BY plus ACM front-matter rights caveat, linked-code status,
    component rows, local static-guidance scope, required future evidence
    fields, and missing-evidence keys. The remaining paper gap is
    executable/reportable evidence for interface semantics, basin-hopping
    validation parameters, GigaEvo dependency/backbone status, human-edit
    provenance, benchmark rows, ablations, model/provider provenance, compute
    budgets, and result-comparison claims.
  - Required result: add paper-manifest and paper-index coverage for
    `2602.10233`: title/authors/arXiv version/date/PDF digest, ACM/preprint
    rights metadata, linked code URL/status, class-interface schema,
    validation-scheme parameters, seed and perturbation schedules,
    monotonic-acceptance and basin-hopping records, GigaEvo relation, HEX and
    ACI2 benchmark/baseline/result rows, Gemini 3 Pro initial-program and
    Gemini 3 Flash Preview evolution provenance, common evolution parameters
    (`elites = 6`, `parents = 2`, `offspring = 10`, temperature `1`), human-
    edited variant attribution, CPU/GPU timeout budgets, Table 1/2/3 result
    and hyperparameter rows, Table 4 validation-scheme ablation rows,
    relation to LibreEvolve's `ModularPlugin`, and README/ROADMAP/code wording
    that keeps ImprovEvolve-style execution marked missing unless
    implementation artifacts and reports prove it.

- [ ] Implement MadEvolve parameter-optimization paper evidence beyond the
      source-specific boundary.
  - Paper/source evidence: local arXiv `2602.15951`, `MadEvolve:
    Evolutionary Optimization of Cosmological Algorithms with Large Language
    Models`, by Tianyi Li, Shihui Zang, and Moritz Munchmeyer was submitted as
    arXiv v1 on February 17, 2026; the cached PDF hash is
    `ec47332c9b20ca391b8aedb6b8696c42aad20c976906d1e43f13490163daea19`
    and the PDF metadata uses the arXiv nonexclusive distribution license. It
    describes a framework similar to AlphaEvolve but focused on scientific
    algorithms with explicit free-parameter tracking and nested parameter
    optimization. It reports greedy one-shot derivative-free tuning,
    autodiff/Adam tuning for differentiable JAX/`vmad` programs, hybrid
    MAP-Elites/island/elite population management, UCB-style model selection,
    diff/full/synthesis mutation modes, automated lineage/comparison/report
    generation, and cosmology applications for BAO reconstruction, 21cm tidal
    reconstruction, and tSZ prediction. The PDF links `madevolve.org`,
    `tianyi-stack/MadEvolve`, `tianyi-stack/MadEvolve-Cosmo`, `biweidai/LDL`,
    `rainwoodman/vmad`, and four generated report PDFs.
  - Current gap: `papers/README.md` lists `2602.15951` as background only, and
    `papers/madevolve_boundary.json` now preserves the MadEvolve PDF evidence
    as a source-specific boundary with cached source metadata, public
    framework/application links, component rows, local generic-evolution
    scope, required future evidence fields, and missing-evidence keys. The
    remaining paper gap is executable/reportable evidence for parameter
    schemas, optimization budgets, differentiability requirements, per-task
    prompts/evaluators, report sections, run statistics, model contribution
    table, compute environment, reward-hacking caveats, generalization claims,
    framework-vs-application repository status, and hosted report artifacts.
  - Required result: add paper-manifest and paper-index coverage for
    `2602.15951`: title/authors/arXiv version/date/PDF digest, source/license
    and public code status for madevolve.org, `tianyi-stack/MadEvolve`, and
    `tianyi-stack/MadEvolve-Cosmo`, parameter-declaration schema, free-parameter
    meaning/function records, one-shot and autodiff optimizer descriptions,
    JAX/vmad operator constraints, outer-loop population and LLM-scheduler
    details, diff/full/synthesis mutation-mode rows, generated-report section
    schema, BAO/iterative-BAO/21cm/tSZ benchmark rows, Table 1 result values,
    Table 2 success/improvement statistics, Table 3 model-contribution
    statistics, compute environment, prompt/evaluator artifact links,
    reward-hacking and over-parameterization caveats, Quijote/LDL/vmad dataset
    and dependency provenance, training/validation/test split records,
    madevolve.org report-link checks, and README/ROADMAP/code wording that
    keeps MadEvolve behavior marked missing unless local artifacts prove it.

- [ ] Implement CausalEvolve causal-scratchpad paper evidence beyond the
      source-specific boundary.
  - Paper/source evidence: local arXiv `2603.14575v2`, `CausalEvolve: Towards
    Open-Ended Discovery with Causal Scratchpad`, by Yongqiang Chen, Chenxi
    Liu, Zhenhao Chen, Tongliang Liu, Bo Han, and Kun Zhang was submitted as
    arXiv v1 on March 15, 2026 and revised as v2 on March 29, 2026; the cached
    PDF hash is
    `b3190d25d802f5b9913e4e266b7dda1b76d2211d2d4cad68e1a5d0a3d03fc4d2`
    and the PDF metadata declares CC BY-NC-SA 4.0. It argues that
    evolve-based AI scientists need causal knowledge to avoid inefficient or
    oscillatory search. It formulates scientific discovery as a POMDP over
    hidden scientific knowledge, models evaluation as intervention on an SCM,
    defines outcome-level factors generated by LLMs from task/output
    descriptions, introduces CausalPlanner actions over factor direction, adds
    procedure-level factors from trial histories, estimates treatment effects,
    detects surprise patterns, and uses abductive reasoning to create new
    factors/hypotheses during evolution. Extracted PDF links include the arXiv
    v2 URL, OpenEvolve, Grok-4.1-fast, and causality/COAT references, but no
    dedicated CausalEvolve code repository URL.
  - Current gap: `papers/README.md` says LibreEvolve only has token-pattern
    outcome-factor guidance, and `papers/causalevolve_boundary.json` now
    preserves the CausalEvolve PDF as a source-specific evidence boundary with
    cached source metadata, CC BY-NC-SA license metadata, no-dedicated-code
    status, component rows, local token-pattern guidance scope, required
    future evidence fields, and missing-evidence keys. The remaining paper gap
    is executable/reportable evidence for theoretical claims,
    factor-generation prompts, executable outcome metrics, CausalPlanner
    intervention policy, procedure-factor extraction, treatment effects,
    surprise-pattern/abduction artifacts, benchmark tasks, seeds, step
    schedules, baseline/ablation rows, and result tables.
  - Required result: add paper-manifest and paper-index coverage for
    `2603.14575`: title/authors/arXiv version/date/PDF digest, code/source
    status, POMDP/SCM notation and theorem boundary, outcome-level factor
    schema, Appendix D metric definitions for Hadamard, second autocorrelation,
    circle packing, and AIME, executable factor-code provenance,
    CausalPlanner action/reward schedule, procedure-factor/COAT relation,
    approximate treatment-effect records, surprise-pattern definitions,
    abductive reasoning outputs, scratchpad memory update semantics, Table 1
    result rows, seed and step schedules, baseline/ablation method rows,
    Grok-4.1-fast-reasoning model provenance, environment-shift/generalization
    caveats, CC BY-NC-SA license metadata, no-code-link status, and
    README/ROADMAP/code wording that keeps local fixed regex factor guidance
    marked missing for CausalEvolve causal-scratchpad claims.

- [ ] Implement DeepEvolve deep-research/debug-loop paper evidence beyond the
      source-specific boundary.
  - Paper/source evidence: local arXiv `2510.06056v1`, `Scientific Algorithm
    Discovery by Augmenting AlphaEvolve with Deep Research`, by Gang Liu,
    Yihan Zhu, Jie Chen, and Meng Jiang was submitted on October 7, 2025; the
    cached PDF hash is
    `e2f578c3b7979eb72857b1545b244405cf0fa8792bab82645e58c97cf3681f86`
    and the PDF metadata declares CC BY 4.0. It presents DeepEvolve as a
    workflow that combines algorithmic deep research with AlphaEvolve-style
    selection. It defines a plan/search/write/code/evaluation/
    evolutionary-selection loop, uses external online research to generate
    proposals with pseudo-code, implements them through cross-file code edits,
    performs automatic debugging from execution feedback, stores algorithms in
    an evolutionary database for next/inspiration sampling, and evaluates nine
    tasks spanning molecular prediction, molecular translation, circle packing,
    Burgers equation, Parkinson's disease, nuclei image segmentation, Open
    Vaccine, polymer prediction, and USP P2P. The public code URL is
    `https://github.com/liugangcode/deepevolve`.
  - Current gap: `papers/README.md` describes LibreEvolve's DeepResearch row as
    bounded retrieval context with cache/provenance surfaces, while explicitly
    excluding a DeepEvolve-style cross-file debugging/editing loop.
    `papers/deepevolve_boundary.json` now preserves the source-specific
    boundary with title/authors/arXiv version/date/PDF digest, CC BY 4.0
    license metadata, GitHub source-link status, component rows, the nine task
    labels, local bounded-retrieval scope, required evidence fields, and
    missing-evidence keys.
  - Required result: add executable paper/report coverage for `2510.06056`:
    task/input schema, textualization function, user-instruction fields,
    plan/search/write proposal artifacts, retrieved-source provenance,
    pseudo-code proposal schema, cross-file code delimiter/localization
    records, reflection and debugging policies, score-zero fallback semantics,
    evolutionary database and inspiration/MAP-Elites relation, Table 1
    task/metric rows, Table 2 performance/runtime rows, Table 3 debugging
    success-rate rows, Figure 3 originality/future-potential/difficulty judge
    records, deep-research ablation rows, 30-minute/single-GPU budget evidence,
    Table 4 ablation rows (`Molecule` best `0.797` without deep research vs
    `0.815` with deep research; `Circle Packing` `2.735` vs `2.981`),
    Appendix C user-query/hyperparameter rows, and README/ROADMAP/code wording
    that keeps current DeepResearch retrieval context marked missing for
    DeepEvolve execution claims.

- [ ] Implement MAP-Elites illumination-algorithm paper evidence beyond the
      source-specific boundary.
  - Paper/source evidence: local arXiv `1504.04909`, `Illuminating search
    spaces by mapping elites`, by Jean-Baptiste Mouret and Jeff Clune is a
    preliminary draft dated April 21, 2015; the local cache row points to
    `https://arxiv.org/pdf/1504.04909.pdf`, byte count `3221283`, and SHA-256
    `df7344343b14893a1d79a5459c1f56db50562e246d132cd0269f5201d1455872`.
    It introduces the Multi-dimensional Archive of Phenotypic Elites as an
    illumination algorithm. It searches a high-dimensional genotype/search
    space while filling a low-dimensional, user-chosen feature space with the
    best elite found per cell, using feature descriptors, performance scores,
    random initialization, mutation or crossover variation from existing elites,
    and per-cell replacement by local performance.
  - Current gap: `papers/README.md` lists `1504.04909` as foundational and
    describes LibreEvolve's current configurable 3D archive plus open stable
    descriptor/rebin/diagnostic gaps. The committed
    `papers/map_elites_illumination_boundary.json` sidecar now preserves the
    MAP-Elites PDF as a source-specific evidence boundary with the local cache
    digest, paper pseudocode variables, algorithm assumptions, current local
    archive evidence, and false readiness for `P`/`X` map exports,
    illumination metrics, visualization/lineage reports, and paper-domain
    reproduction. It does not yet provide executable feature-space
    discretization policy, illumination metrics, visualization outputs,
    lineage/stepping-stone analysis, benchmark-domain rows, or
    experiment-parameter schedules.
  - Required result: implement the paper-manifest evidence named by
    `papers/map_elites_illumination_boundary.json`: executable feature
    descriptor `b(x)`, performance function `f(x)`, map variables `P`/`X`,
    initialization count `G`, iteration budget `I`, random selection and
    variation policy, cell replacement condition, user-chosen dimension and
    discretization records, empty/unfillable cell notes, global performance,
    global reliability, precision, and coverage metric definitions, feature-
    performance visualization requirements, parent/lineage stepping-stone
    evidence, retina feature axes and resolution schedule, simulated soft-robot
    feature axes and resolution schedule, physical soft-arm MAP-Elites/grid-
    search/random-sampling evaluation counts, modular-neural-network and soft-
    robot benchmark context, relation to NS+LC/MOLE/novelty search/EA+D/grid
    search, and README/ROADMAP/code wording that keeps current local archive
    support distinct from full illumination-algorithm reproduction.

- [ ] Implement hardness-of-approximation proof-element paper evidence beyond
      the source-specific boundary.
  - Paper/source evidence: local arXiv `2509.18057v7`, `Reinforced Generation
    of Combinatorial Structures: Hardness of Approximation`, by Ansh Nagda,
    Prabhakar Raghavan, and Abhradeep Thakurta was submitted as v7 on March 9,
    2026; the local cache row points to
    `https://arxiv.org/pdf/2509.18057.pdf`, byte count `7719868`, SHA-256
    `32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842`,
    and the PDF metadata declares CC BY 4.0. It reports AlphaEvolve-discovered
    finite proof elements for three complexity-theory settings: average-case
    certification lower bounds for random regular graph MAX-CUT/MAX-
    Independent-Set, gadget-based NP-hardness improvements for MAX-3-CUT and
    MAX-4-CUT, and metric-TSP hardness via a new equation gadget. It
    distinguishes proxy scores from theorem constants, uses evolved fast
    verifiers to search larger gadgets, and requires final brute-force
    verification plus human/proof arguments before theorem claims.
  - Current gap: the paper index labels `2509.18057` as AlphaEvolve
    complexity-theory result context and background-only. The committed
    `papers/theoretical_cs_sources.json` sidecar preserves arXiv/article/PDF
    source metadata and now includes a nested
    `proof_element_artifact_boundary` for required graph/gadget inventories,
    verifier code, synthetic correctness datasets, judge-LLM/human-inspection
    records, independent brute-force outputs, theorem-lifting metadata,
    baseline/SOTA rows, and source-repository status. It still does not provide
    the actual result ids, graph/gadget artifact inventories, verifier-speedup
    evidence, correctness-check records, final brute-force verification,
    proof-lifting metadata, extracted-link/source-repository status, or claim
    boundaries between finite constructions and universal theorem statements as
    local executable/reproducible artifacts.
  - Required result: implement paper-manifest evidence beyond the
    `proof_element_artifact_boundary`: source/artifact availability and rights,
    result table for MAX-CUT, MAX-Independent-Set,
    MAX-k-CUT, and metric TSP, Table 1 LB/UB values, Ramanujan graph witness
    metadata for graphs up to 163 vertices, MAX-k-CUT gadget schemas and
    Appendix C edge lists, TSP equation-gadget schemas and Appendix D edge
    lists, verifier API and runtime records, synthetic correctness dataset
    provenance from 20 random MAX-k-CUT models, judge-LLM and human-inspection
    attribution, final brute-force verification outputs, theorem/lemma/proof
    appendix cross-links, baseline/SOTA comparison values, extracted links plus
    absence/presence of code-repository URLs, lifting-framework statements, and
    README/ROADMAP/code wording that keeps complexity-theory proof-element
    support missing unless those artifacts are locally represented and verified.

- [ ] Add row-specific anchors for repeated broad paper-index TODO coverage
      cells.
  - Paper evidence: the `papers/README.md` TODO coverage cross-reference
    table is treated as backlog traceability for each paper-cache row, so
    repeated active cells should not hide distinct source-specific gaps.
  - Current evidence: source rows with very different status claims, including
    `2511.17592` GigaEvo framework-parity absence, `2510.14150` CodeEvolve
    prompt/solution-fitness absence, and `2605.08520` FlashEvolve
    asynchronous-stage orchestration absence, currently use the same active
    coverage cell: `docs/todo/code.md`; `docs/todo/papers.md`.
  - Current gap: the current table proves that broad active ledgers exist, but
    it does not provide row-specific active anchors, source-span dispositions,
    or claim-refresh triggers for those materially different paper rows.
  - Required result: give repeated broad TODO coverage cells stable
    row-specific anchors or grouped-label records, validate that each anchor
    points to a live source-specific open gap, and require coverage refreshes
    when the paper row's role, implementation status, benchmark qualifier, or
    source-span evidence changes.
