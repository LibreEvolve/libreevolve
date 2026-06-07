# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

- [ ] Keep roadmap current-state framing tied to ongoing evidence rather than
      stale snapshot dates.
  - Spec evidence: the roadmap is part of the AlphaEvolve-alignment evidence
    surface, so its "current codebase" framing should remain true as code,
    README, paper-index, and TODO-ledger slices continue to change.
  - Current evidence: `ROADMAP.md` no longer claims to reflect only the
    codebase as of `2026-05-26`; it now describes ongoing alignment passes
    against the AlphaEvolve paper, local docs, paper index, and checked-in
    tests.
  - Required result: when future roadmap passes add or retire current-state
    claims, keep the intro and matching README/papers/TODO evidence aligned
    with the current worktree rather than a stale dated audit snapshot.

- [ ] Keep binary/static roadmap scope aligned with implemented static-member
      support.
  - Spec evidence: AlphaEvolve can operate over broader codebase and artifact
    surfaces, while LibreEvolve's current boundary is a Python-primary text
    workspace plus typed static metadata.
  - Current evidence: `ROADMAP.md` now distinguishes implemented bounded
    encoded static members, verified copy-only static assets, and raw
    direct-workspace byte normalization from the still-open richer binary
    mutation/replay policy. The code path normalizes raw direct workspace bytes
    into immutable static members and verifies `source_copy_path` materialization
    by link policy, byte count, and SHA-256.
  - Required result: when arbitrary binary mutation, non-encoded generated
    binary deltas, binary replay, or broader artifact runners land, update the
    roadmap, README, papers index, and code/paper TODO entries together.

## Missing Roadmap Items

## Existing Items That Need Tightening

- [ ] Keep the multi-objective roadmap item scoped to primary archive policy
      versus retained diagnostic overlays.
  - Spec evidence: AlphaEvolve-style multi-objective search should make
    tradeoff-aware retention and inspiration part of the durable optimization
    policy, not only a diagnostic view.
  - Current evidence: `ROADMAP.md` now distinguishes the current scalar primary
    MAP-Elites grid plus bounded Pareto and metric-cell retained overlays from
    the still-open Pareto/frontier primary archive replacement and durable
    cross-run metric-specific optimization work. Code evidence includes
    bounded `pareto_frontier_archive()` retention, `metric_cell_archive()`
    overlays, persisted/restored `pareto_frontier_program_ids` and
    `metric_cell_archives`, and policy validation that rejects primary Pareto
    replacement overclaims.
  - Required result: when Pareto/frontier replacement becomes the primary
    archive policy, or durable cross-run metric-specific optimization lands,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so they neither underclaim the retained overlays nor overclaim
    AlphaEvolve-grade multi-objective optimization.

- [ ] Keep `show`/metric archive roadmap wording scoped to selected-row CLI
      output versus manifest-level summary records.
  - Spec evidence: AlphaEvolve-scale run inspection should support
    whole-run archive and metric-specific drill-downs, not just the selected
    best row.
  - Current evidence: `libreevolve show` prints selected-row
    archive/objective-vector diagnostics, while final manifests already expose
    `runtime.history.objective_metric_leaders` and
    `runtime.history.objective_metric_archives` summary records. `ROADMAP.md`
    now asks for CLI/report drill-downs over those metric-specific archives
    instead of implying the manifest-level summaries are absent.
  - Required result: when metric-specific archive drill-downs, whole-run CLI
    views, or durable artifact query reports land, update the roadmap, README,
    papers index, and code/paper TODO entries together so they neither
    underclaim current manifest summaries nor overclaim the selected-row
    `show` command.

- [ ] Keep paper-inspired roadmap labels scoped to implemented behavior.
  - Spec evidence: roadmap references to paper-inspired systems should remain
    clear about whether LibreEvolve implements the cited paper behavior or only
    borrows a prompt/plugin idea.
  - Current evidence: the roadmap already says to continue labeling
    CausalEvolve, DeepEvolve, ImprovEvolve, ThetaEvolve, GigaEvo, CodeEvolve,
    and MadEvolve features as inspired unless paper behavior is actually
    implemented.
  - Required result: when faithful paper-specific behavior lands, update the
    roadmap, README, papers index, and code/paper TODO entries together. Until
    then, keep roadmap wording from promoting token-pattern causal guidance,
    clipped JSONL export, static modular prompting, retrieval context, or
    generic prompt-program mutation into the cited papers' full systems.

- [ ] Keep custom-plugin roadmap wording scoped to entry-point provenance
  versus direct-instance value attribution.
  - Spec evidence: AlphaEvolve-style extension points need reproducible plugin
    code/configuration boundaries so paper-inspired hooks can be audited across
    runs.
  - Current evidence: the roadmap now distinguishes entry-point distribution
    metadata and declared/manifest-safe constructor options from direct custom
    plugin instances, where current provenance records module/file/version and
    constructor signature shape while explicitly excluding constructor values.
  - Required result: when direct custom plugin constructor-value/schema
    attribution, versioned custom registries, or richer package policy lands,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so they neither underclaim entry-point plugin provenance nor
    overclaim direct-instance replayability.

- [ ] Keep proposal-memory roadmap wording scoped to bounded hypothesis
  summaries versus semantic proposal retrieval.
  - Spec evidence: AlphaEvolve-style idea memory should be able to score and
    retrieve prior proposal ideas and hypotheses by quality, novelty, and
    semantic relation to the current task.
  - Current evidence: the roadmap now distinguishes optional
    `IDEA`/`RATIONALE`/`HYPOTHESIS` proposal metadata and bounded manifest
    `runtime.history.hypothesis_index` evidence from still-open proposal
    scoring, semantic proposal-index retrieval, hypothesis-refinement loops,
    and field-influence policy for retrieval, prompting, and archive
    resurfacing.
  - Required result: when proposal scoring or semantic proposal-index
    retrieval lands, update the roadmap, README, papers index, and code/paper
    TODO entries together so they neither underclaim current bounded
    hypothesis summaries nor overclaim AlphaEvolve-grade idea memory.

- [ ] Keep MAP-Elites descriptor roadmap wording scoped to insertion-time
  TF-IDF coordinates versus stable learned descriptors.
  - Spec evidence: AlphaEvolve-style quality-diversity search needs
    task-meaningful behavior descriptors or stable descriptor models with
    tested compatibility when descriptors change.
  - Current evidence: the roadmap now names evaluator-provided behavior
    descriptors, fixed descriptor models, or explicit rebin/snapshot semantics
    as the remaining work. Current archive snapshots already record descriptor
    axes, current diversity reference ids, descriptor-model revision, dynamic
    TF-IDF reference status, and the no-rebin insertion-time coordinate policy.
  - Required result: when learned/evaluator-provided descriptor models or
    archive rebin semantics land, update the roadmap, README, papers index,
    and code/paper TODO entries together so they neither underclaim current
    descriptor-policy snapshots nor overclaim stable AlphaEvolve-grade
    behavior descriptors.

- [ ] Keep island-count roadmap wording scoped to configurable defaults.
  - Spec evidence: AlphaEvolve's paper names MAP-Elites and island-based
    population models at a high level; local roadmap wording should not turn
    LibreEvolve's default island count into an unsupported fixed fidelity
    claim.
  - Current evidence: the roadmap now says MAP-Elites plus configurable
    ring-topology island migration, defaulting to five islands. That matches
    `Config.n_islands`, validation for positive configured island counts, and
    tests with non-default island counts.
  - Required result: when adaptive island counts, non-ring topologies, or
    AlphaEvolve-specific migration policies land, update the roadmap, README,
    papers index, and code/paper TODO entries together so they do not
    underclaim current configurability or overclaim fixed five-island policy.

- [ ] Keep per-role scheduler roadmap wording scoped to role-scoped backend
  eligibility and role budget maps versus independent live scheduler state.
  - Spec evidence: AlphaEvolve-scale LLM orchestration needs role-specific
    model-selection behavior for mutation generation, critique, feedback, and
    prompt-improvement calls, with budgets and rewards that can be evaluated
    independently.
  - Current evidence: the roadmap now distinguishes configured
    reward-accounted roles, role-scoped backend eligibility, logical call caps,
    and role budget maps from still-open independent per-role live scheduler
    state, calibrated reward signals, quota ownership, and budget policy.
  - Required result: when independent per-role scheduler state lands, update
    the roadmap, README, papers index, and code/paper TODO entries together so
    they neither underclaim current role routing and budget maps nor overclaim
    AlphaEvolve-style per-role scheduling.

- [ ] Keep the async/resumable-runtime roadmap wording scoped to compatible
  full-runtime restore versus full replay.
  - Spec evidence: AlphaEvolve-scale runs need reproducible resumed
    experiments, not just terminal snapshots; provider outputs, controller
    queues, pending evaluations, migration ordering, and lineage semantics must
    be replayable or explicitly bounded.
  - Current evidence: the roadmap now recognizes that
    `--restore-runtime-from-manifest` composes the current compatible
    synchronous restore surfaces into a checked full-runtime bundle: runtime
    RNG, LLM scheduler, archive restore, runtime budget, controller-budget
    replay, and lineage-boundary validation. The near-term workspace section
    now scopes resume work to ordered migration-event replay, controller
    queues, and pending-work resume beyond the current archive-content restore
    bundle. It also keeps full replay and end-to-end resumed-trace proof open.
  - Required result: when provider/plugin output replay, ordered
    migration-event replay, async controller queues, pending-work restore, or
    resumed-trace lineage proof lands, update the roadmap, README, papers
    index, and code/paper TODO entries together so they neither underclaim the
    current compatible restore bundle nor overclaim AlphaEvolve-style replay.

- [ ] Keep environment-provenance roadmap wording scoped to bounded audit
  evidence versus replayable build/package/accelerator state.
  - Spec evidence: AlphaEvolve-scale experiments need environment evidence
    strong enough to reproduce evaluator execution, package resolution,
    accelerator runtime, and compute-budget accounting across long runs.
  - Current evidence: the roadmap now says current bounded environment
    provenance should be extended into complete install-source interpretation,
    external build execution/options/environment records, non-project build
    metadata policy, private package-source resolution, live provider
    service/default capture, and accelerator budget/accounting semantics.
  - Required result: when external-build/package-source/accelerator replay
    evidence lands, update the roadmap, README, papers index, and code/paper
    TODO entries together so they neither underclaim the current audit-only
    manifest records nor overclaim replayable AlphaEvolve-grade environment
    reproduction.

- [ ] Keep the provider cancellation roadmap item aligned with current timeout
  policy coverage.
  - Spec evidence: AlphaEvolve-scale provider orchestration needs bounded model
    calls, stop/quarantine behavior, and audit evidence for timeout and
    cancellation outcomes across model roles.
  - Current evidence: the roadmap now recognizes the implemented
    `libreevolve.provider_cancellation_policy.v1` policy contract,
    runtime scheduler observations, configured in-run role/backend quarantine
    evidence, strict provider-failure ledger summaries, restorable scheduler
    failure-policy state, and mutation timeout failure-history rows before
    naming the open live SDK hard-cancellation, timeout-stop, raw provider
    output replay, and cross-run quarantine/resume gaps.
  - Required result: when live provider SDK cancellation, runtime
    timeout-driven stop policy, cross-run provider-failure quarantine/resume
    behavior beyond restorable scheduler failure-policy state, raw provider
    output replay, or richer role-specific timeout artifacts land, update the
    roadmap, README, papers index, and code/paper TODO entries together so they
    neither underclaim current timeout policy evidence nor overclaim provider
    hard-cancel enforcement.

- [ ] Keep provider-pricing roadmap wording scoped to configured estimates
  versus live/default-rate capture.
  - Spec evidence: AlphaEvolve-scale provider accounting needs cost evidence
    that survives provider, model, and default-rate changes; configured local
    rates are useful run policy but are not live provider pricing discovery.
  - Current evidence: backend specs can now set
    `cost_usd_per_million_tokens`, provider usage `total_tokens` feeds
    configured `cost_estimate` records, runtime accounting accumulates
    configured cost, and diagnostics explicitly mark live pricing as
    not fetched. The roadmap now names live provider pricing/default-rate
    capture beyond configured token-cost estimates as the remaining gap.
  - Required result: when live provider pricing discovery, provider default
    rate capture, or account/model-specific pricing evidence lands, update the
    roadmap, README, papers index, and code/paper TODO entries together so they
    neither underclaim configured cost accounting nor overclaim live pricing.

- [ ] Keep feedback-calibration roadmap wording scoped to report contracts
  versus executed calibration fixtures.
  - Spec evidence: AlphaEvolve-style feedback graders need calibration evidence
    from real reviewer/task suites, not only validators for declared reports.
  - Current evidence: `libreevolve.llm_feedback_calibration.v1` and its
    artifact-inventory contract validate declared multi-task calibration
    evidence and safe artifact references once a report exists. The roadmap
    now scopes the follow-up to emitting real reports and grader ablation
    fixtures.
  - Required result: when a runtime fixture or benchmark script emits real
    feedback-calibration reports, update the roadmap, README, papers index, and
    code/paper TODO entries together so they neither underclaim the report
    contract nor overclaim executed calibration evidence.

- [ ] Keep benchmark-hardening roadmap wording scoped to smoke evidence versus
  benchmark-grade fixtures.
  - Spec evidence: AlphaEvolve-style benchmark claims need repeated,
    target-family fixtures with anti-gaming evidence, not smoke-only examples.
  - Current evidence: the matrix smoke fixture now rejects known shortcuts and
    has a scope-checked hardening bundle helper that emits report, inventory,
    summary, and scope-validation files while preserving
    `alphaevolve_comparable: false`.
  - Required result: when tensor/geometric/compiler/systems fixtures emit
    benchmark-grade hardening reports, update the roadmap, README, papers index,
    and code/paper TODO entries together so they neither underclaim smoke
    hardening evidence nor overclaim AlphaEvolve-comparable benchmarks.

- [ ] Keep ablation roadmap wording scoped to report validation versus executed
  experiment scripts.
  - Spec evidence: AlphaEvolve Figure 8 compares equal-budget ablation curves
    from actual runs, not only records that satisfy a result-report schema.
  - Current evidence: `libreevolve.alphaevolve_ablation_report.v1` validates
    reports for all six Figure 8 variants, three seeds, required budget
    fractions, finite scores, budget consistency, component assertions, and
    hashed curve artifacts, while README/TODO text still says no benchmark
    script emits those reports yet.
  - Required result: when benchmark scripts emit equal-budget ablation reports,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so they neither underclaim the report contract nor overclaim
    executed ablation experiments.

- [ ] Keep critique-reviewer roadmap wording scoped to synchronous reviewer
  pools versus AlphaEvolve-grade reviewer orchestration.
  - Spec evidence: AlphaEvolve-style critique/reviewer channels need calibrated
    signal, explicit budget policy, and robust provider isolation beyond a
    sequential mutation-replacement filter.
  - Current evidence: `critique_reviewers` configures bounded synchronous
    reviewer pools with manifest-safe roles, first/last-valid aggregation,
    retained reviewer-pool metadata, selected-reviewer provenance, and existing
    role routing/budget telemetry for reviewer roles such as
    `critique:correctness`.
  - Required result: when async reviewer overlap, calibrated reviewer scoring,
    per-reviewer provider isolation, or richer reviewer-specific failure
    artifacts land, update the roadmap, README, papers index, and code/paper
    TODO entries together so they neither underclaim current synchronous
    reviewer pools nor overclaim AlphaEvolve-grade critique orchestration.
