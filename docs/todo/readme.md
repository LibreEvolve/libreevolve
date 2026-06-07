# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

## Feature Claims

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

- [ ] Keep README archive restore claims scoped to current archive-content
  restore.
  - Spec evidence: AlphaEvolve-style long-running evolutionary search needs
    reproducible population state and clear boundaries for migration-order
    replay versus snapshot restore.
  - Current evidence: README now says full archive cell/island contents can be
    restored from manifest snapshots plus checked accepted-history rows, while
    ordered migration-event replay remains audit-only rather than a MAP-Elites
    restore engine.
  - Required result: when ordered migration-event replay or async
    controller/pending-work resume lands, update README archive sections,
    roadmap, papers index, and code/paper TODO entries together so they do not
    underclaim archive-content restore or overclaim migration replay.

## Architecture Description
