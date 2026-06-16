# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

- [ ] Add semantic evidence mapping for ROADMAP current-state and priority
      claims.
  - Spec evidence: the ROADMAP is the main planning bridge between the code
    audit, README status, paper-index evidence, and AlphaEvolve-alignment TODOs.
    Its current-state bullets and follow-up priorities should therefore remain
    synchronized with implemented behavior and missing evidence.
  - Current evidence: ROADMAP now states that its current-state bullets are a
    maintained planning summary, not a machine-verified proof ledger. The
    committed `papers/documentation_truthfulness_boundary.json` records ROADMAP
    status scoping plus cross-document guardrails, while keeping semantic
    documentation-claim verification and complete implementation-evidence
    mapping absent. `papers/documentation_claim_inventory.json` now assigns
    stable claim ids and evidence anchors with file-offset source spans to
    top-level README, ROADMAP, and papers-index scope claims, records local
    evidence-ref existence plus Markdown fragment-anchor resolution for those
    anchors, and includes ROADMAP current-state, documentation-truthfulness,
    and AlphaEvolve-gap claims. It also records audited README, ROADMAP, and
    papers-index Markdown headings plus uncovered heading-to-claim gaps with
    active TODO-owner links.
    `papers/roadmap_claim_evidence_boundary.json` now records a ROADMAP-
    specific current-state and priority claim evidence map with parsed
    current-state bullet and good-first item counts, sidecar refs, active TODO
    refs, validation-gate labels, and explicit missing semantic-proof fields.
  - Current gap: the ROADMAP-specific sidecar is a bounded structural evidence
    map, not a semantic verifier. There is still no complete machine-readable
    claim inventory for every ROADMAP current-state bullet, no per-bullet
    code/test/runtime-artifact sufficiency proof, no stale current-state or
    stale-priority detector, and no generated alignment report that proves
    each ROADMAP statement is current.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: complete current-state claim inventory, per-bullet
    code/test/runtime evidence map, semantic evidence-sufficiency verifier,
    stale current-state detector, stale-priority detector, cross-document
    claim freshness report, generated alignment report, CI semantic claim
    gate, and owner review signoff before treating ROADMAP as semantically
    complete AlphaEvolve-alignment proof.

- [ ] Add ROADMAP readiness taxonomy and weighted completion evidence.
  - Spec evidence: the active project goal is not simply to accumulate TODO
    entries; it is to bring LibreEvolve toward the AlphaEvolve specification
    across code, ROADMAP, README, and papers. A project-completion percentage
    should therefore distinguish technical implementation parity, benchmark
    reproduction, operational/release maturity, documentation truthfulness,
    paper-source metadata, and source-only fixture evidence.
  - Current evidence: raw TODO counting reports a useful ledger ratio, and
    `papers/roadmap_readiness_boundary.json` now records a machine-readable
    readiness taxonomy with stable categories, weights summing to 100,
    per-category active/completed TODO counts, raw TODO-ledger completion, and
    weighted TODO-ledger completion. The paper-manifest gate validates that the
    sidecar matches the current TODO files. Source-publication metadata
    boundaries such as title-page affiliation and system-contribution
    provenance can be claim-ready for narrow fixture facts, while many
    technical AlphaEvolve boundaries remain explicitly false for async
    topology, Gemini Flash/Pro parity, realistic codebase benchmarks,
    sandbox/resource enforcement, representative benchmark reproduction, and
    full resume/replay proof. README and `docs/status.md` correctly say this
    is not a full AlphaEvolve reproduction.
    `papers/roadmap_readiness_publication_boundary.json` now records a
    bounded eight-criterion publication/certification gate for semantic
    requirement source mapping, canonical gap completion policy, per-category
    evidence gates, benchmark reproduction certification, operational release
    readiness, uncertainty/percentage labels, stale-count detection, and
    publication-claim scoping.
  - Current gap: the weighted readiness sidecar is still TODO-ledger evidence,
    and the new publication sidecar is still a bounded certification map, not
    semantic AlphaEvolve implementation parity. There is no requirement-level
    source-span mapping, canonical underlying-gap deduplication, per-category
    code/test/runtime-artifact proof map, benchmark reproduction
    certification, operational release-readiness gate, uncertainty model, or
    stale-count detector preventing paper-source metadata readiness,
    documentation-routing work, or fixture-level provenance from inflating
    technical implementation completion.
  - Required result: add a ROADMAP readiness model with stable categories,
    weights, source requirements, TODO/sidecar/test evidence links,
    per-category completion counts, uncertainty labels, and a validator that
    reports raw TODO completion separately from weighted AlphaEvolve
    implementation readiness before publishing project-completion percentages
    as more than a ledger statistic.

- [ ] Add TODO-ledger canonical ownership and duplicate-gap audit.
  - Spec evidence: the active project goal spans code, ROADMAP, README, and
    papers, so the same AlphaEvolve gap often needs implementation, planning,
    user-facing documentation, and paper-boundary entries. That cross-linking
    is useful, but the project-completion percentage and audit workflow need
    to distinguish one underlying missing capability from several document-
    specific TODOs about that capability.
  - Current evidence: `docs/todo/code.md`, `docs/todo/roadmap.md`,
    `docs/todo/readme.md`, and `docs/todo/papers.md` all carry legitimate
    open items, and the paper-manifest gate validates selected active and
    completed TODO evidence paths for paper-index rows.
    `papers/todo_ledger_ownership_boundary.json` now records the four owner
    ledgers, active/completed counts, active-versus-completed marker drift,
    raw checklist completion, and an exact normalized-title duplicate scan.
    `papers/roadmap_readiness_boundary.json` separately records the weighted
    TODO-ledger readiness model. The current raw and weighted percentages are
    still derived from checklist counts only, while active TODOs can
    intentionally overlap around provider parity, benchmark evidence,
    documentation drift, readiness criteria, and paper-source boundaries.
    `papers/todo_canonical_gap_boundary.json` now records a nine-criterion
    canonical-gap readiness matrix over the current raw owner-ledger counts
    and exact duplicate-title groups, with sidecar refs, active TODO refs,
    validation-gate labels, readiness labels, and explicit missing rollup
    fields.
    `papers/todo_canonical_gap_rollup_boundary.json` now records a bounded
    eight-criterion rollup/publication gate for canonical gap registry,
    canonical owner policy, derivative relationships, source and
    implementation evidence links, cross-document rollup policy,
    duplicate/orphan detection, canonical completion reporting, and
    owner-reviewed publication scoping.
  - Current gap: the canonical-gap sidecar is a bounded readiness matrix, not a
    canonical underlying-gap registry, and the rollup sidecar is a bounded
    publication gate rather than a canonical completion model. There is still
    no canonical underlying-gap id, duplicate/derivative relationship registry,
    consolidation report, semantic duplicate detector, or stale-duplicate
    detector across active and completed TODO ledgers. A newly identified
    problem can be counted multiple times, a completed document-specific TODO
    can leave its implementation owner ambiguous, and repeated audit slices
    can inflate the denominator without proving that a distinct AlphaEvolve
    requirement was discovered.
  - Required result: implement the missing readiness fields recorded by the
    rollup sidecar: canonical gap ids, canonical owner assignments, derivative
    documentation relationships, source/paper anchor mapping, implementation
    evidence links, cross-document rollup rules, semantic duplicate detection,
    stale completed duplicate detection, orphaned derivative detection,
    canonical gap completion percent, raw-count inflation report, and owner
    review signoff; then publish raw checklist completion separately from
    canonical underlying-gap completion.

## Missing Roadmap Items

- [ ] Add ROADMAP AlphaEvolve source-span disposition coverage.
  - Spec evidence: the objective is to bring LibreEvolve toward the
    AlphaEvolve specification, which means the ROADMAP should account for the
    paper's requirements, figures, tables, appendices, and application-result
    claims as source-backed work items or explicit non-goals. A handful of
    core requirement anchors is useful, but it is not enough to prove that the
    roadmap has considered every relevant AlphaEvolve source span.
  - Current evidence: ROADMAP's documentation-truthfulness section references
    `papers/implementation_evidence_map_boundary.json`, which records core
    AlphaEvolve anchors for markers, evaluator cascades, LLM prompting,
    evolutionary database behavior, async/distributed topology, and published
    benchmarks. `papers/roadmap_source_span_disposition_boundary.json` now
    maps those six core anchors to ROADMAP section ids, phase buckets, local
    status, sidecars, and TODO links, and records that only the AlphaEvolve
    source row is dispositioned while the broader paper-index rows are not.
    `papers/README.md` and the Appendix A/B registries provide many
    source-specific status rows, but those records are not an exhaustive
    ROADMAP coverage proof.
    `papers/roadmap_source_span_coverage_boundary.json` now records a
    ROADMAP-level coverage readiness matrix for main-text sections, figures,
    tables, Appendix A, Appendix B, application-result claims, paper-status
    rows, and TODO/non-goal/phase proof.
    `papers/roadmap_source_span_exhaustiveness_boundary.json` now records a
    bounded eight-criterion exhaustiveness gate for PDF section walk,
    figure/table/appendix matrix, application-result claim matrix,
    status-row disposition map, span status classification, missing/partial
    TODO proof, phase-priority map, and CI/owner signoff.
  - Current gap: the coverage sidecar is a bounded readiness matrix, not an
    exhaustive ROADMAP-level matrix, and the exhaustiveness sidecar is a
    bounded gate rather than a retained-PDF walk. There is still no matrix
    that walks the retained AlphaEvolve source PDF by section, figure, table,
    appendix, benchmark family, and application-result claim. It does not
    classify each span as implemented, partially implemented, missing,
    background-only, or non-goal, and it does not prove that every missing or
    partial span has a linked code/paper/README TODO or ROADMAP priority.
    There is also no detector for AlphaEvolve source spans beyond the current
    six core anchors, or for all paper/status sidecar rows, that have no
    roadmap disposition.
  - Required result: implement the missing readiness fields recorded by the
    exhaustiveness sidecar: exhaustive PDF section walk, figure/table/appendix matrix,
    application-result claim matrix, status-row to ROADMAP disposition map,
    missing/partial TODO proof, non-goal decision map, phase-priority map, CI
    source-span exhaustiveness gate, and owner review signoff.

## Existing Items That Need Tightening

- [ ] Add ROADMAP non-goal contradiction checks.
  - Spec evidence: ROADMAP non-goals are overclaim guardrails. If the project
    says it is not requiring a service database, not claiming arbitrary-
    language/codebase support before runners and validators exist, and not
    advertising paper-inspired plugins as faithful implementations, those
    claims should be protected against drift across README, papers, plugin
    docs, and implementation metadata.
  - Current evidence: `ROADMAP.md` lists the three current non-goals, README
    limits already scope arbitrary-language runners, Google/Gemini parity,
    smoke examples, and paper-inspired claims, and active code/paper TODOs keep
    plugin behavior scoped to approximation/background metadata.
    `papers/roadmap_non_goal_contradiction_boundary.json` now assigns stable
    ids to the three ROADMAP non-goals, maps nine constrained documentation
    surfaces, validates required safe-scope phrases, and records zero exact
    forbidden support-claim phrase matches for the bounded surface set.
    `papers/roadmap_non_goal_drift_boundary.json` now records a seven-
    criterion non-goal drift and promotion readiness matrix for runtime
    metadata scans, plugin docstring scans, exhaustive Markdown corpus scans,
    CI promotion gates, intentional-promotion workflow, contradiction
    remediation, and runtime/plugin/docs/paper scope joins.
  - Current gap: the sidecars are bounded documentation and readiness
    inventories, not a full cross-document contradiction detector or promotion
    gate. There is still no implemented runtime metadata scan, plugin
    docstring scan, exhaustive Markdown corpus scan, CI promotion gate,
    intentional-promotion workflow, contradiction-remediation report,
    runtime/plugin/docs/paper scope join, or owner review signoff proving
    future ROADMAP edits cannot accidentally promote a non-goal into a
    supported AlphaEvolve-parity claim.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: runtime metadata scan, plugin docstring scan, exhaustive Markdown
    corpus scan, CI promotion gate, intentional promotion workflow,
    contradiction-remediation report that rejects contradictory support
    claims, code/docs/paper surfaces plus runtime/plugin scope join, and owner
    review signoff. The workflow must update ROADMAP/TODO evidence whenever a
    non-goal is completed, removed, or intentionally promoted into active
    implementation work.

- [ ] Add ROADMAP Good First Follow-Ups priority freshness evidence.
  - Spec evidence: the `Good First Follow-Ups` section is a prioritization
    claim. If it tells contributors that database query indexes, one non-toy
    benchmark fixture, workspace resume coverage, and feedback-calibration
    reports are the next approachable steps, that ordering should be tied to
    current implementation state, dependency readiness, and AlphaEvolve-gap
    impact rather than remaining a static list.
  - Current evidence: ROADMAP lists four good first follow-ups, and active
    code/paper TODOs already track the underlying implementation gaps for
    durable query indexes, benchmark fixtures, workspace resume, and
    feedback-calibration reports.
    `papers/roadmap_good_first_followups_boundary.json` now records those four
    priority items with stable ids, active TODO refs, priority rationale,
    dependency-readiness labels, validation gates, and AlphaEvolve impact
    labels.
    `papers/roadmap_good_first_freshness_boundary.json` now records a six-
    criterion freshness readiness matrix for dependency-state refresh
    automation, stale-priority detection, calibrated priority scoring, CI
    freshness gating, validation-artifact refresh, and owner review signoff.
  - Current gap: the sidecars are bounded static-priority and freshness
    readiness maps, not an implemented freshness model. There is still no
    dependency-state refresh automation, stale-priority detector, calibrated
    priority score model, CI freshness gate, validation-artifact freshness
    report, or owner review signoff proving these four items remain the best
    first follow-ups after new ROADMAP, code, README, or paper-sidecar work
    lands.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: dependency-state refresh automation, stale-priority detector,
    calibrated priority score model, CI freshness gate, validation-artifact
    freshness report for expected validation artifacts, current blockers, and
    owner review signoff. The drift check must force the section to be
    refreshed when dependencies or implementation states change.

- [ ] Add ROADMAP phase-boundary and sequencing evidence.
  - Spec evidence: the `Near Term`, `Mid Term`, and `Longer Term` headings are
    not neutral labels; they tell readers which AlphaEvolve-alignment work is
    nearer, which depends on more infrastructure, and which is deliberately
    deferred. That phase taxonomy should stay tied to dependency readiness and
    implementation prerequisites.
  - Current evidence: ROADMAP groups candidate-workspace fidelity,
    multi-objective search, evaluation cascades, prompt/context, documentation,
    async runtime, backend scheduling, plugin extensibility, representative
    benchmarks, and operational maturity into staged sections. Active code and
    paper TODOs cover many underlying features, and the documentation claim
    inventory records the phase headings as uncovered claim surfaces.
    `papers/roadmap_phase_sequence_boundary.json` now records the current
    Near Term, Mid Term, and Longer Term sequence for ten major ROADMAP
    sections, links each section to an active blocker TODO, and records
    validation-gate labels plus promotion criteria.
    `papers/roadmap_phase_freshness_boundary.json` now records a six-
    criterion phase freshness readiness matrix for the dependency graph,
    stale-phase detector, promotion/demotion workflow, CI phase freshness
    gate, evidence-status refresh, and owner review signoff.
  - Current gap: the sidecars are bounded static-sequence and freshness
    readiness maps, not a full dependency graph or freshness model. There is
    still no implemented dependency graph, stale-phase detector,
    promotion/demotion workflow, CI phase freshness gate, evidence-status
    refresh report, or owner review signoff proving that a ROADMAP item still
    belongs in Near Term, Mid Term, or Longer Term after related code, papers,
    README, or sidecar evidence changes.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: dependency graph, stale-phase detector, promotion/demotion
    workflow, CI phase freshness gate, evidence-status refresh report, and
    owner review signoff. The verifier must keep each major section linked to
    prerequisites, blocking TODOs, validation gates, and promotion criteria,
    then validate that phase labels and item ordering are refreshed when
    implementation or evidence status changes.

- [ ] Add ROADMAP operational-maturity acceptance criteria.
  - Spec evidence: the `10. Operational maturity` section groups config
    validation, strict JSONL diagnostics, run inspection, packaging/release
    provenance, and CI workflow coverage. As written, it is a roadmap category,
    but it does not define what evidence would make LibreEvolve operationally
    mature enough for AlphaEvolve-style experiments rather than only more
    locally smoke-tested.
  - Current evidence: ROADMAP names the current config, JSONL, run-inspection,
    release-artifact, and CI boundaries, and active code/paper TODOs track
    missing plugin-specific config schemas, provider/model compatibility,
    signed release provenance, local-PDF CI checks, semantic docs verification,
    branch policy, and notification policy. ROADMAP also lists structured
    `manifest.json`, `history.jsonl`, `best.py`/`best_workspace/`, v1
    run-artifact schema metadata, standalone `task_specification.json`, and
    `prompt_prior_score_table.jsonl`, while newer code/README TODOs identify
    lifecycle drift for generated prompt-table artifacts and
    `paper_artifacts/` directories that are documented or emitted but not yet
    consistently represented in collision/overwrite cleanup policy.
    `papers/roadmap_operational_maturity_boundary.json` now records six
    section-level criteria with risk classes, current sidecar refs, active TODO
    refs, and acceptance-gate labels.
    `papers/roadmap_operational_readiness_boundary.json` now records a six-
    criterion readiness matrix for the global acceptance threshold, unified
    generated-artifact lifecycle inventory, semantic docs verification, signed
    release provenance, cross-platform CI policy, and owner review signoff.
  - Current gap: the sidecars are bounded criteria and readiness maps, not an
    operational readiness gate. There is still no implemented global
    acceptance threshold, unified generated-artifact lifecycle inventory,
    semantic docs verification, signed release provenance, cross-platform CI
    policy, or owner signoff preventing one green release/CI boundary from
    being mistaken for overall operational readiness.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: global acceptance threshold, unified generated-artifact lifecycle
    inventory, semantic docs verification, signed release provenance,
    cross-platform CI policy, and owner review signoff. The gate must classify
    required validation, packaging, observability, reproducibility, CI, release,
    run-artifact lifecycle, and policy evidence; map each criterion to
    code/tests/sidecars/TODOs; and reject claims that the project is
    operationally mature until the full checklist is satisfied.

- [ ] Add ROADMAP representative-benchmark portfolio readiness criteria.
  - Spec evidence: the `9. Representative benchmarks` section is more than a
    feature list; it defines the benchmark portfolio needed before
    LibreEvolve can claim meaningful AlphaEvolve-alignment progress. It should
    specify what mix of domains, validation strength, baseline evidence,
    repeated-run evidence, anti-gaming checks, and certification artifacts make
    the portfolio representative rather than just a set of smoke examples.
  - Current evidence: ROADMAP names stronger AlphaEvolve-style fixtures,
    bounded sorting-network candidates, smoke-versus-benchmark separation,
    anti-gaming validators, fixture-emitted artifacts, SOTA/target baselines,
    repeated-seed runs, benchmark-hardening reports, and constructive-math
    verifier exports. Active code/paper TODOs already track many
    implementation gaps for sorting networks, matrix results, circle/geometry,
    constructive math, and systems/kernel candidates, and
    `papers/example_benchmark_scope.json` plus
    `runtime.history.benchmark_fixture_readiness_report` preserve the current
    smoke-boundary evidence. The bounded
    `papers/roadmap_representative_benchmark_portfolio_boundary.json` sidecar
    now records five portfolio families, domains, validator-strength labels,
    current sidecar refs, active TODO refs, baseline/SOTA target labels,
    artifact-output requirements, and readiness-status labels.
    `papers/roadmap_benchmark_portfolio_readiness_boundary.json` now records
    a six-criterion readiness matrix for the domain-coverage matrix,
    benchmark admission checklist, repeated-seed run matrix, anti-gaming
    certification, SOTA/baseline citation sufficiency proof, and portfolio-
    balance/CI freshness gate.
  - Current gap: the sidecars are bounded portfolio and readiness maps, not a
    representative-readiness gate. There is still no implemented
    domain-coverage matrix, benchmark admission checklist, repeated-seed run
    matrix, anti-gaming certification, SOTA/baseline citation sufficiency
    proof, portfolio-balance score, stale-coverage detector, CI freshness
    gate, or owner signoff proving the representative-benchmark list is
    balanced, feasible, non-duplicative, and strong enough to support
    AlphaEvolve-style claims once individual fixtures improve.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: domain-coverage matrix, benchmark admission checklist,
    repeated-seed run matrix, anti-gaming certification, SOTA/baseline
    citation sufficiency proof, portfolio-balance score, stale-coverage
    detector, CI freshness gate, and owner review signoff. The verifier must
    classify candidate benchmark families by domain, validator strength,
    baseline/SOTA target, repeated-run/certification needs, anti-gaming
    evidence, artifact outputs, and current readiness, and validate that
    README/papers/ROADMAP wording cannot promote smoke fixtures or one narrow
    benchmark family as representative coverage.

- [ ] Add ROADMAP plugin-extensibility readiness criteria.
  - Spec evidence: the `8. Plugin extensibility` section describes a framework
    surface, not just a set of plugin TODOs. To support AlphaEvolve-style
    extensible research workflows, ROADMAP should define when plugin loading,
    configuration, provenance, artifacts, and paper-inspiration metadata are
    mature enough for external plugins rather than only trusted in-repo
    examples.
  - Current evidence: ROADMAP distinguishes the current entry-point registry,
    direct-instance signature-only policy, built-in scalar/path configuration,
    configured entry-point plugin distribution records, prompt/context/config
    provenance, and manifest-safe artifact summaries from planned richer
    package policy, direct custom constructor schemas, versioned custom
    registries, constructor-value provenance, package-version attribution,
    artifact lifecycle hashes, and strategy-choice evidence. Active code and
    paper TODOs already track direct custom plugin provenance, custom plugin
    package-registry attribution, constructor-value/schema evidence, and
    paper-inspired plugin scope boundaries. The bounded
    `papers/roadmap_plugin_extensibility_boundary.json` sidecar now records
    six plugin surfaces: built-in catalog, entry-point plugins, direct
    instances, future custom registries, hook isolation, and plugin artifact
    lifecycle, with configuration shape, package/source identity, constructor
    provenance, artifact hashing, trust-boundary, paper-scope attribution,
    validation-gate, code-ref, sidecar-ref, active-TODO, and readiness labels.
    `papers/roadmap_plugin_readiness_boundary.json` now records a seven-
    criterion readiness matrix for the plugin trust-boundary matrix, plugin
    admission checklist, direct constructor value/schema registry, versioned
    custom plugin registry, artifact lifecycle hash policy, runtime isolation
    policy, and paper-scope attribution/stale-readiness guard.
  - Current gap: the sidecars are bounded plugin-surface and readiness maps,
    not an external plugin readiness gate. There is still no implemented
    plugin trust-boundary matrix, plugin admission checklist, direct
    constructor value/schema registry, versioned custom plugin registry,
    artifact lifecycle hash policy, runtime isolation policy, paper-scope
    attribution policy, stale-readiness detector, or owner signoff tying those
    plugin subfeatures together, so a partial entry-point or provenance
    improvement could be mistaken for broad custom-plugin support.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: plugin trust-boundary matrix, plugin admission checklist, direct
    constructor value/schema registry, versioned custom plugin registry,
    artifact lifecycle hash policy, runtime isolation policy, paper-scope
    attribution policy, stale-readiness detector, and owner review signoff. The
    verifier must classify built-in, entry-point, direct-instance, and future
    custom-registry plugins by supported configuration shape, package/source
    identity, constructor provenance, artifact hashing, runtime
    isolation/trust assumptions, paper-scope attribution, and validation
    gates, and add checks that README, papers, runtime metadata, and plugin
    docs cannot overclaim external plugin readiness until the full matrix is
    satisfied.

- [ ] Add ROADMAP backend-scheduling and critique readiness criteria.
  - Spec evidence: the `7. Backend scheduling and critique` section combines
    reward assumptions, role-scoped backend routing, provider diagnostics,
    pricing, cancellation, fast/strong model-mix scheduling, sample-efficiency
    evidence, repeated-sampling comparators, Gemini parity, and critique
    reviewer pools. Those are separate implementation tracks, but together
    they define whether LibreEvolve has a reliable AlphaEvolve-style
    backend/critique control plane rather than a collection of local
    heuristics.
  - Current evidence: ROADMAP already distinguishes current heuristic UCB
    routing, opt-in role-scoped scheduler state, configured cost estimates,
    scalar provider diagnostics, retry/fallback quarantine, policy-only
    cancellation evidence, `throughput_depth` metadata tests,
    sample-efficiency reports, repeated-sampling boundaries,
    Gemini-provider-parity absence records, and synchronous first/last-valid
    critique reviewer aggregation from missing calibrated rewards, quotas,
    live provider/default pricing, raw replay, hard cancellation, equal-budget
    scheduler comparisons, first-class Gemini lanes, async reviewer overlap,
    reviewer isolation, and critique-to-revision attribution. Active code and
    paper TODOs track those individual gaps. The bounded
    `papers/roadmap_backend_scheduling_critique_boundary.json` sidecar now
    records nine tracks: heuristic UCB rewards, role-scoped routing, provider
    diagnostics/pricing, cancellation/quarantine, fast/strong model mix,
    sample efficiency, repeated-sampling baselines, Gemini provider parity, and
    critique reviewer pools, with selection-policy, reward-assumption,
    budget/quota, pricing/default-rate, diagnostics/replay, cancellation,
    resume, equal-budget, reviewer-isolation, Gemini-substitution,
    sidecar-ref, active-TODO, validation-gate, and readiness labels.
    The bounded
    `papers/roadmap_backend_control_plane_readiness_boundary.json` sidecar now
    records eight readiness criteria for backend-role capability, calibrated
    reward/quota policy, live pricing/default and raw replay, hard
    cancellation/resume, equal-budget scheduler comparison, Gemini
    lane/substitution, critique reviewer isolation, and stale readiness/owner
    signoff.
  - Current gap: there is no backend-role capability matrix,
    critique-control checklist, calibrated reward policy, role quota ownership,
    live provider pricing/default evidence, raw provider replay, live hard
    cancellation, equal-budget scheduler comparator, first-class Gemini lane
    evidence, async reviewer isolation, stale-readiness detector, or owner
    signoff proving when these scheduler/provider/critique pieces are coherent
    enough to support AlphaEvolve-style claims, nor a guard that prevents one
    completed subfeature from implying full backend scheduling maturity. The
    sidecars are bounded track/readiness maps, not a backend control-plane gate.
  - Required result: add ROADMAP backend-scheduling criteria that classify each
    role and provider lane by selection policy, reward assumptions, budget and
    quota ownership, pricing/default-rate evidence, diagnostics/replay support,
    cancellation behavior, resume semantics, equal-budget comparator evidence,
    critique/reviewer isolation, Gemini substitution status, and validation
    gates, then implement the missing readiness fields recorded by the
    control-plane sidecar and enforce README/papers/ROADMAP wording against
    overclaiming backend-scheduler or critique parity until the matrix is
    complete.

- [ ] Add ROADMAP async/resumable-runtime readiness criteria.
  - Spec evidence: the `6. Async and resumable runtime` section is the main
    roadmap boundary for AlphaEvolve Section 2.6-style concurrent proposal and
    evaluation work. It should define what proves LibreEvolve has a real async
    and resumable runtime, not only synchronous batches, local sample-worker
    fan-out, terminal snapshots, and absence-boundary metadata.
  - Current evidence: ROADMAP records synchronous topology reporting,
    parallel-evaluation readiness reports, terminal controller-state restore
    evidence, MAP-Elites archive snapshots, cursor/full archive restore
    surfaces, run manifest hardening, framework RNG restore, synchronous
    budget counters, and validated sidecars for distributed-pipeline topology,
    parallel evaluation, controller pending-work resume, archive-event replay,
    lineage replay, and LLM budget policy. Active code and paper TODOs already
    track async evaluator workers, concurrent proposal control, ordered archive
    replay, pending-work controller resume, budget resume, provider replay,
    RNG/resumed-trace proof, and external environment replay. The bounded
    `papers/roadmap_async_resumable_runtime_boundary.json` sidecar now records
    nine criteria for topology, parallel evaluation, controller pending work,
    archive-event replay, RNG/lineage replay, provider/plugin nondeterminism,
    budget resume, environment replay, and resumed-trace proof, with current
    scope, missing-readiness, sidecar-ref, active-TODO, validation-gate, and
    readiness labels.
    The bounded `papers/roadmap_async_runtime_readiness_boundary.json`
    sidecar now records eight readiness criteria for async-state inventory,
    replay-resume acceptance, controller/sampler task checkpoints, evaluator
    pending work and merge order, archive/migration restore, provider/plugin
    replay, async budget/environment replay, and stale readiness/owner
    signoff.
  - Current gap: there is no async-state inventory, replay-resume acceptance
    checklist, controller queue checkpoint, LLM sampler task state, evaluator
    pending-work state, deterministic async merge/admission order, ordered
    migration restore engine, provider-output replay, plugin RNG replay, async
    budget accounting, external environment replay, end-to-end resumed trace
    proof, stale-readiness detector, or owner signoff tying those runtime
    pieces together, so partial synchronous restore or sample-worker fan-out
    could be mistaken for full async/resumable runtime parity. The sidecars are
    bounded criteria/readiness maps, not an async runtime control-plane gate.
  - Required result: add ROADMAP async/resumable-runtime criteria that classify
    controller queues, LLM sampler tasks, evaluator workers, pending-work
    checkpoints, deterministic merge/admission order, archive/event replay,
    RNG and lineage replay, provider/plugin nondeterminism, budget accounting,
    environment replay, and resumed-trace proof status; map each criterion to
    code/tests/runtime artifacts/sidecars/TODOs; implement the missing
    readiness fields recorded by the async runtime readiness sidecar; and
    reject README, ROADMAP, and paper wording that implies async or resumable
    parity before the full checklist is satisfied.

- [ ] Add ROADMAP prompt/context-system readiness criteria.
  - Spec evidence: the `4. Prompt and context work` section defines the
    prompt/control surface that makes AlphaEvolve-style program evolution more
    than isolated LLM calls. It should specify when prompt templates, context
    selection, token packing, proposal memory, retrieval evidence,
    meta-prompting, and prompt-database behavior are coherent enough to support
    AlphaEvolve-alignment claims.
  - Current evidence: ROADMAP records current prompt-template schema and
    dry-run checks, mutation-channel validation, parent-placeholder retention,
    first-N context truncation, mutation-path section packing, role-scoped
    token counting, backend context-window metadata, stochastic prompt-format
    distribution evidence, configurable retention surfaces, evaluator-artifact
    content retrieval, bounded DeepEvolve-style retrieval provenance, proposal
    score/diversity/hypothesis/backtracking reports, absolute/improvement
    meta-prompt rewards, and a local `PromptDatabase`.
    `papers/roadmap_prompt_context_system_boundary.json` now records a
    bounded nine-criterion ROADMAP matrix for role-template compatibility,
    context-source selection, token section packing, stochastic prompt-format
    provenance, retention/replay policy, retrieval integrity, proposal-memory
    semantics, meta-prompt reward evidence, and prompt-database lifecycle.
    `papers/roadmap_prompt_context_readiness_boundary.json` now records a
    bounded eight-criterion readiness matrix for prompt-role capability,
    context selection/summarization, all-role token section packing,
    prompt-format and replay retention, retrieval/proposal-memory integrity,
    meta-prompt and prompt-database lifecycle, prompt/context benchmark
    evidence, and stale readiness/owner signoff.
    Active code and paper TODOs already track role-specific template
    compatibility, all-role provider-token packing, separate stochastic format
    source provenance, structured prompt-context policy expansion,
    audit-grade retrieval integrity, semantic proposal retrieval, calibrated
    meta-prompt rewards, and prompt-database parity.
  - Current gap: there is no section-level prompt/context readiness rubric,
    capability matrix, or stale-readiness detector that proves these features
    compose into a safe AlphaEvolve-style prompt system, nor a guard preventing
    one bounded prompt feature from implying full prompt/context parity. The
    sidecars are bounded feature/readiness maps, not a full prompt-system gate.
  - Required result: implement the missing readiness fields recorded by the
    readiness sidecar: prompt-role capability matrix, deterministic context
    summarization, all-role provider-token section packing, separate
    prompt-format source provenance, full prompt replay-retention policy,
    audit-grade retrieval source integrity, semantic proposal memory,
    calibrated meta-prompt rewards, prompt-database archive lifecycle,
    prompt/context benchmark evidence, stale-readiness detector, and owner
    review signoff; then validate README, ROADMAP, papers, runtime metadata,
    and prompt docs against implying complete AlphaEvolve prompt/context
    readiness before those criteria are satisfied.

- [ ] Add ROADMAP evaluation-cascade readiness criteria.
  - Spec evidence: the `3. Expand evaluation cascades` section defines the
    validation layer that decides which candidate programs are trusted,
    promoted, rejected, or benchmark-worthy. To match AlphaEvolve-style
    evaluation, ROADMAP should define when cascades have sufficient artifact
    evidence, budget accounting, feedback calibration, statistical promotion
    policy, oracle independence, workload contracts, sandboxing, and
    environment reproducibility.
  - Current evidence: ROADMAP records candidate-workspace artifact copy-out,
    cooperative generation/evaluation/provider budget stops, LLM budget
    snapshots, feedback calibration report contracts, qualitative-feedback
    policy reports, lower-confidence/Wilson statistical gates, evaluator
    arbitration matrices, workload-provenance boundaries, automated evaluator
    scope reports, executable-code versus natural-language proposal boundaries,
    validator subprocess controls, dependency policy, package/version
    snapshots, release-smoke boundaries, and reproducibility sidecars.
    `papers/roadmap_evaluation_cascade_boundary.json` now records a bounded
    ten-criterion ROADMAP matrix for cascade transition artifacts, artifact
    schema/hash coverage, budget ownership, feedback calibration,
    statistical promotion policy, oracle independence, workload execution
    contracts, automated scope/programmatic boundaries, validator sandbox
    dependency boundaries, and environment/release reproducibility.
    `papers/roadmap_evaluation_cascade_readiness_boundary.json` now records a
    bounded eight-criterion readiness matrix for validator authority,
    artifact/budget sufficiency, feedback/statistical promotion,
    oracle/workload contracts, automated environment/sandbox policy,
    release/environment reproducibility, benchmark sufficiency, and stale
    readiness/owner signoff. Active code
    and paper TODOs already track cascade promotion/attrition evidence,
    statistical hypothesis-test semantics, qualitative feedback provenance,
    async/accelerator budgets, evaluator environment replay, validator
    sandbox/resource policy, release artifacts, matrix cascade runs, and
    workload-specific provenance.
  - Current gap: there is no section-level cascade-readiness rubric,
    evaluator/oracle capability matrix, artifact-and-budget sufficiency
    checklist, or stale-readiness detector tying those pieces together, so a
    green local evaluator, one statistical gate, or one report contract could
    be mistaken for a robust AlphaEvolve-style cascade. The sidecars are
    bounded cascade/readiness maps, not a full AlphaEvolve cascade gate.
  - Required result: implement the missing readiness fields recorded by the
    readiness sidecar: validator-authority matrix, complete artifact schema/hash
    coverage, accelerator/async budget ownership, executed feedback
    calibration, benchmark-calibrated statistical promotion, independent
    oracle disagreement records, workload-specific execution contracts, robust
    automated environment fixtures, OS/container resource sandbox,
    replayable environment/release bundle, benchmark-sufficiency signoff,
    stale-readiness detector, and owner review signoff; then validate README,
    ROADMAP, papers, evaluator docs, and runtime metadata against implying
    full cascade readiness before those criteria are satisfied.

- [ ] Add ROADMAP multi-objective search readiness criteria.
  - Spec evidence: the `2. Strengthen multi-objective search` section defines
    whether LibreEvolve's search is genuinely multi-objective or still a
    scalar-primary archive with bounded diagnostic overlays. ROADMAP should
    state what evidence promotes metric reports, prompt-diverse inspiration,
    duplicate-work memory, descriptor models, and metric-specific reports into
    an AlphaEvolve-style multi-objective search system.
  - Current evidence: ROADMAP records cross-run paper metric reports, averaged
    normalized declared metrics, bounded Pareto and metric-cell retained
    overlays, `objective_archive_policy` readiness snapshots, metric-diverse
    inspiration reports, sampling-balance reports, run-local exact-workspace
    evaluator cache evidence, descriptor-model snapshots, selected-row `show`
    archive objective-vector summaries, manifest-level metric archive
    summaries, and sidecars for metric-diverse prompts, sampling balance,
    duplicate-work policy, descriptor readiness, MAP-Elites illumination, and
    objective-archive boundaries.
    `papers/roadmap_multi_objective_search_boundary.json` now records a
    bounded eight-criterion ROADMAP matrix for paper metric bundles,
    objective-archive policy, metric-diverse sampling balance, duplicate-work
    memory, descriptor authority, MAP-Elites illumination, metric-specific
    drill-downs, and benchmark comparison evidence. Active code and paper
    TODOs already track
    primary Pareto/frontier archive replacement, durable metric-specific
    optimization, durable resurfacing indexes, durable duplicate-work memory,
    behavior descriptor models, MAP-Elites parity, and benchmark prompt-policy
    evidence.
    `papers/roadmap_multi_objective_readiness_boundary.json` now records a
    bounded eight-criterion readiness matrix for primary archive policy,
    durable metric storage, sampling/metric policy, descriptor authority and
    rebin semantics, duplicate-work memory semantics, metric drill-down/CLI
    policy, equal-budget benchmark evidence, and stale readiness/owner signoff.
  - Current gap: there is no section-level multi-objective readiness rubric,
    archive-policy matrix, descriptor/memory capability checklist, or
    stale-readiness detector tying those pieces together, so bounded overlays,
    prompt-visible diversity reports, or run-local duplicate caches could be
    mistaken for full multi-objective search parity. The sidecars are bounded
    search/readiness maps, not a full multi-objective search gate.
  - Required result: implement the missing readiness fields recorded by the
    readiness sidecar: primary Pareto/frontier archive replacement, durable
    cross-run metric database, calibrated parent/inspiration balance, stable
    behavior descriptor contracts, learned or evaluator-provided descriptor
    models, tested archive rebin semantics, durable duplicate-work memory,
    semantic near-duplicate detection, metric-specific CLI drill-downs,
    equal-budget multi-objective benchmarks, stale-readiness detector, and
    owner review signoff; then validate README, ROADMAP, papers, archive
    reports, and runtime metadata against implying full multi-objective
    readiness before those criteria are satisfied.

- [ ] Add ROADMAP candidate-workspace fidelity readiness criteria.
  - Spec evidence: the `1. Finish candidate workspace fidelity` section is the
    first ROADMAP step toward AlphaEvolve-style candidate handling. It should
    define when workspace materialization, candidate abstraction, language and
    build runners, mutation application, artifact capture, topology
    diagnostics, and resume semantics are faithful enough to support
    AlphaEvolve-alignment claims rather than only Python-local workspace
    experiments.
  - Current evidence: ROADMAP records manifest-only candidate-language runner
    declarations, code-file-set divergence from AlphaEvolve's flexible
    solution-abstraction API, candidate-abstraction design matrices,
    Python-only evolve-block marker handling, `workspace_math` smoke fixtures,
    Table 1 codebase-scale absence reports, fixed diff/full/file/block/topology
    mutation parser evidence, prompt-example copy diagnostics,
    mutation-consistency reports, initial-pool divergence reports,
    binary/static candidate handling, topology materialization diagnostics, and
    archive-content restore boundaries. Active code and paper TODOs already
    track real language/build runners, candidate-embedded evaluators,
    abstraction-choice benchmark evidence, topology diagnostics, adaptive
    mutation modes, mutation-operator provenance, validator boundary checks,
    source/workspace integrity, binary/static replay policy, codebase-scale
    evidence, and ordered migration-event replay.
    `papers/roadmap_candidate_workspace_fidelity_boundary.json` now records a
    ten-criterion section-level readiness matrix with current scope,
    missing-readiness, sidecar-ref, active-TODO, validation-gate, and readiness
    labels.
    `papers/roadmap_candidate_workspace_readiness_boundary.json` now records a
    bounded eight-criterion readiness matrix for language/build runner and
    candidate API readiness, embedded evaluator and codebase-scale readiness,
    materialization/topology readiness, mutation-mode and operator provenance,
    prompt-copy and cross-file consistency, initial-pool/static-binary policy,
    resume replay and manifest/workspace-doc policy, and stale
    readiness/owner signoff.
  - Current gap: the section-level matrix and readiness sidecar are bounded
    readiness maps, not evidence that the missing candidate-workspace
    capabilities are implemented. A passing Python workspace fixture, fixed
    diff parser, snapshot restore, or materialization diagnostic still must
    not be mistaken for complete AlphaEvolve-style workspace support.
  - Required result: implement the missing readiness fields recorded by the
    readiness sidecar: configured language/build runners, flexible solution
    abstraction API, candidate-embedded evaluator contracts, realistic codebase
    fixtures, adaptive mutation-mode selection, mutation-operator family
    provenance, semantic prompt-example-copy detection, cross-file consistency
    benchmark evidence, initial-pool divergence benchmark evidence,
    static/binary replay policy, topology resume replay proof,
    stale-readiness detector, and owner review signoff; then validate README,
    ROADMAP, papers, run manifests, and workspace docs against implying full
    candidate-workspace fidelity before those criteria are satisfied.
