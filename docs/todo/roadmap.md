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
  - Current gap: there is no complete machine-readable claim inventory for
    every ROADMAP current-state bullet, no per-bullet code/test/runtime-
    artifact/sidecar/TODO evidence map, no stale-priority detector, and no
    generated alignment report that proves each ROADMAP statement is current.
  - Required result: add ROADMAP claim ids, evidence links, freshness checks,
    and CI validation before treating ROADMAP as semantically complete
    AlphaEvolve-alignment proof.

## Missing Roadmap Items

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
    plugin behavior scoped to approximation/background metadata. The
    documentation claim inventory records the `Non-Goals For Now` heading but
    marks it as having no claim record.
  - Current gap: there is no machine-readable non-goal inventory, no
    cross-document contradiction detector, and no CI or sidecar check proving
    README, papers rows, plugin docstrings, runtime metadata, and future
    ROADMAP edits do not accidentally promote a non-goal into a supported
    AlphaEvolve-parity claim.
  - Required result: add stable ROADMAP non-goal claim ids and a verifier that
    maps each non-goal to the code/docs/paper surfaces it constrains, rejects
    contradictory support claims, and updates ROADMAP/TODO evidence whenever a
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
    feedback-calibration reports. The documentation claim inventory records
    the `Good First Follow-Ups` heading as uncovered, while the broad ROADMAP
    semantic-evidence TODO covers priority claims only at a whole-document
    level.
  - Current gap: there is no per-item priority rationale, dependency/readiness
    record, owner/scope label, estimated validation gate, or stale-priority
    detector proving these four items remain the best first follow-ups after
    new ROADMAP, code, README, or paper-sidecar work lands.
  - Required result: add a ROADMAP priority-evidence map for good-first items
    that links each follow-up to active implementation TODOs, current
    blockers, expected validation artifacts, and AlphaEvolve-alignment impact,
    and add a drift check that forces the section to be refreshed when those
    dependencies or implementation states change.

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
  - Current gap: there is no machine-readable phase map, dependency graph,
    promotion/demotion criterion, or stale-phase detector proving that a
    ROADMAP item still belongs in Near Term, Mid Term, or Longer Term after
    related code, papers, README, or sidecar evidence changes.
  - Required result: add ROADMAP phase metadata that links each major section
    to prerequisites, blocking TODOs, validation gates, and promotion criteria,
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
    branch policy, and notification policy.
  - Current gap: there is no section-level operational-maturity checklist,
    risk classification, acceptance threshold, or evidence map that ties those
    subitems together and prevents one green release/CI boundary from being
    mistaken for overall operational readiness.
  - Required result: add ROADMAP operational-maturity criteria that classify
    required validation, packaging, observability, reproducibility, CI, release,
    and policy evidence; map each criterion to code/tests/sidecars/TODOs; and
    reject claims that the project is operationally mature until the full
    checklist is satisfied.

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
    smoke-boundary evidence.
  - Current gap: there is no portfolio-level readiness rubric,
    domain-coverage matrix, benchmark admission checklist, or stale-coverage
    detector proving the representative-benchmark list is balanced, feasible,
    non-duplicative, and strong enough to support AlphaEvolve-style claims once
    individual fixtures improve.
  - Required result: add a ROADMAP benchmark-portfolio evidence map that
    classifies candidate benchmark families by domain, validator strength,
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
    paper-inspired plugin scope boundaries.
  - Current gap: there is no section-level plugin-extensibility rubric,
    trust-boundary matrix, admission checklist, or stale-readiness detector
    tying those plugin subfeatures together, so a partial entry-point or
    provenance improvement could be mistaken for broad custom-plugin support.
  - Required result: add ROADMAP plugin-extensibility criteria that classify
    built-in, entry-point, direct-instance, and future custom-registry plugins
    by supported configuration shape, package/source identity, constructor
    provenance, artifact hashing, runtime isolation/trust assumptions,
    paper-scope attribution, and validation gates, and add checks that README,
    papers, runtime metadata, and plugin docs cannot overclaim external plugin
    readiness until the full matrix is satisfied.

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
    paper TODOs track those individual gaps.
  - Current gap: there is no section-level readiness rubric, backend-role
    capability matrix, critique-control checklist, or stale-readiness detector
    proving when these scheduler/provider/critique pieces are coherent enough
    to support AlphaEvolve-style claims, nor a guard that prevents one
    completed subfeature from implying full backend scheduling maturity.
  - Required result: add ROADMAP backend-scheduling criteria that classify each
    role and provider lane by selection policy, reward assumptions, budget and
    quota ownership, pricing/default-rate evidence, diagnostics/replay support,
    cancellation behavior, resume semantics, equal-budget comparator evidence,
    critique/reviewer isolation, Gemini substitution status, and validation
    gates, then enforce README/papers/ROADMAP wording against overclaiming
    backend-scheduler or critique parity until the matrix is complete.

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
    RNG/resumed-trace proof, and external environment replay.
  - Current gap: there is no section-level readiness rubric, async-state
    inventory, replay-resume acceptance checklist, or stale-readiness detector
    tying those runtime pieces together, so partial synchronous restore or
    sample-worker fan-out could be mistaken for full async/resumable runtime
    parity.
  - Required result: add ROADMAP async/resumable-runtime criteria that classify
    controller queues, LLM sampler tasks, evaluator workers, pending-work
    checkpoints, deterministic merge/admission order, archive/event replay,
    RNG and lineage replay, provider/plugin nondeterminism, budget accounting,
    environment replay, and resumed-trace proof status; map each criterion to
    code/tests/runtime artifacts/sidecars/TODOs; and reject README, ROADMAP,
    and paper wording that implies async or resumable parity before the full
    checklist is satisfied.

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
    meta-prompt rewards, and a local `PromptDatabase`. Active code and paper
    TODOs already track role-specific template compatibility, all-role
    provider-token packing, separate stochastic format source provenance,
    structured prompt-context policy expansion, audit-grade retrieval
    integrity, semantic proposal retrieval, calibrated meta-prompt rewards,
    and prompt-database parity.
  - Current gap: there is no section-level prompt/context readiness rubric,
    capability matrix, or stale-readiness detector that proves these features
    compose into a safe AlphaEvolve-style prompt system, nor a guard preventing
    one bounded prompt feature from implying full prompt/context parity.
  - Required result: add ROADMAP prompt/context criteria that classify each
    prompt role and context source by template compatibility, source
    selection/summarization policy, token-counter authority, section-packing
    coverage, retention/replay policy, retrieval provenance, proposal-memory
    semantics, meta-prompt reward evidence, prompt-database lifecycle,
    benchmark evidence, and overclaim status, and validate README, ROADMAP,
    papers, runtime metadata, and prompt docs against implying complete
    AlphaEvolve prompt/context readiness before the matrix is satisfied.
