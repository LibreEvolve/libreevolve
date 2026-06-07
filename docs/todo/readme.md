# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

## Feature Claims

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
    controller-budget event replay into restored budget snapshots.
  - Required result: when benchmark scripts emit executed equal-budget
    ablation reports, or when accelerator/async-worker budgets land, update
    README, ROADMAP, papers index, and code/paper TODO entries together so the
    README neither underclaims current token/configured-cost budget stops nor
    overclaims AlphaEvolve-style executed ablations.

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
    LibreEvolve discovered or exported the full Appendix A target suite.
    Matching paper TODO and paper-index entries now make the same distinction.
  - Required result: when real tensor-decomposition benchmark runs emit
    discovered algorithms, certificates, notebooks, or publication bundles
    across Appendix A targets, update README, ROADMAP, papers index, and
    code/paper TODO entries together so README neither underclaims the checked
    Strassen baseline nor overclaims AlphaEvolve-comparable discovery coverage.

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
    fixtures, held-out case sets, and randomized/reference-correctness checks.
  - Required result: when benchmark runs emit real certification reports,
    deployment/reviewer evidence, held-out systems reports, or reference-code
    checks, update README, ROADMAP, papers index, and code/paper TODO entries
    together so README neither underclaims the current report and inventory
    contracts nor overclaims AlphaEvolve-style confirmed result evidence.

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
    with real randomized or exhaustive anti-gaming evidence.
  - Required result: when real target-family benchmark runners emit
    benchmark-grade hardening reports, negative fixtures, detector logs, and
    artifact inventories, update README, ROADMAP, papers index, and code/paper
    TODO entries together so README neither underclaims the checked smoke
    hardening evidence nor overclaims AlphaEvolve-comparable benchmark
    hardening.

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
  - Current evidence: README now says `role_scheduler_state` is an
    audit/restoration record, while role routing can narrow eligible backends
    and role budget maps can stop matching roles before later calls. It also
    states that the global ensemble state remains authoritative and that
    independent per-role scheduler configuration, reward calibration, and
    quota/budget ownership remain open.
  - Required result: once independent per-role live scheduler state, calibrated
    reward semantics, and quota/budget ownership land, update the README and
    matching code/paper TODO entries together so the README neither underclaims
    current role-scoped backend eligibility nor overclaims AlphaEvolve-style
    role scheduling.

- [ ] Keep README LLM budget/replay claims scoped to current synchronous
  restore boundaries.
  - Spec evidence: AlphaEvolve-scale reproduction needs compute-budgeted model
    scheduling, replayable run accounting, and enough provider evidence to
    distinguish resumed controller state from replayed provider outputs.
  - Current evidence: README now documents live synchronous
    provider-attempt/token/configured-cost/latency stops, restorable runtime
    budget snapshots, `controller_budget_events.jsonl` replay, and
    full-runtime restore validation. It also documents strict call-ledger
    provider-failure summaries and restorable scheduler failure-policy state,
    while still marking live provider pricing/default-rate capture beyond
    configured estimates, provider-output/raw-payload replay, cross-run
    provider-failure policy proof, and async/pending-work budget composition as
    open.
  - Required result: once provider-output replay, async/pending-work budget
    composition, live pricing/default-rate capture beyond configured
    estimates, or cross-run provider-failure quarantine/resume proof lands,
    update the README and matching code/paper TODO entries together so the
    README neither underclaims current synchronous budget replay and provider
    failure-policy evidence nor overclaims full AlphaEvolve-style replay.

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
    `libreevolve.retrieval_evidence_boundary_policy.v1`, and
    `libreevolve.retrieval_context_audit_policy.v1`. It states that retained
    under-budget payloads can be checked through secret-redacted sidecar
    artifacts and inventory hashes, while unbounded raw payload availability,
    semantic source correctness, and replayable transport/TLS decision evidence
    remain open.
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
