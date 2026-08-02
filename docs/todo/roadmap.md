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
    raw checklist completion, an exact normalized-title duplicate scan, and a
    bounded exact-title raw-count inflation report. That report records 123
    exact-title duplicate groups, 246 duplicate records, 123 inflated raw
    checklist rows, and a 5186 collapsed exact-title total estimate. It also
    records an exact owner/status profile: all 123 exact-title duplicate
    groups are completed-only, 122 groups are cross-owner duplicates, one
    group is same-owner, and zero exact-title duplicate groups involve active
    TODO rows. It also records an exact same-owner completed duplicate report
    identifying the duplicate "Add bounded ROADMAP evaluation-cascade
    readiness matrix." entries in `docs/todo/Completed/roadmap.md` at lines
    15471 and 15789. It also records a bounded exact stale-completed duplicate
    detector with zero active/completed title twins.
    `papers/roadmap_readiness_boundary.json` separately records the weighted
    TODO-ledger readiness model. The current raw and weighted percentages are
    still derived from checklist counts only, while active TODOs can
    intentionally overlap around provider parity, benchmark evidence,
    documentation drift, readiness criteria, and paper-source boundaries.
    `papers/todo_canonical_gap_boundary.json` now records a nine-criterion
    canonical-gap readiness matrix over the current raw owner-ledger counts
    and exact duplicate-title groups, with sidecar refs, active TODO refs,
    validation-gate labels, readiness labels, explicit missing rollup fields,
    and active TODO coverage for all 12 missing evidence keys.
    `papers/todo_canonical_gap_rollup_boundary.json` now records a bounded
    eight-criterion rollup/publication gate for canonical gap registry,
    canonical owner policy, derivative relationships, source and
    implementation evidence links, cross-document rollup policy,
    duplicate/orphan detection, canonical completion reporting, and
    owner-reviewed publication scoping. It also records that all 12 missing
    rollup evidence keys have active TODO coverage in this roadmap TODO,
    while keeping each field marked `not_recorded_locally`.
  - Current gap: the canonical-gap sidecar is a bounded readiness matrix, not a
    canonical underlying-gap registry, and the rollup sidecar is a bounded
    publication gate rather than a canonical completion model. There is still
    no canonical underlying-gap id, duplicate/derivative relationship registry,
    semantic duplicate detector, semantic stale-duplicate detector beyond
    exact title matches, same-owner duplicate cleanup beyond exact title
    matches, or orphaned-derivative detector across active and completed TODO
    ledgers. A newly identified
    problem can be counted multiple times, a completed document-specific TODO
    can leave its implementation owner ambiguous, and repeated audit slices
    can inflate the denominator without proving that a distinct AlphaEvolve
    requirement was discovered.
  - Required result: implement the missing readiness fields recorded by the
    rollup sidecar: canonical gap ids, canonical owner assignments, derivative
    documentation relationships, source/paper anchor mapping, implementation
    evidence links, cross-document rollup rules, semantic duplicate detection,
    stale completed duplicate detection beyond exact title matches, orphaned
    derivative detection, canonical gap completion percent, canonical
    raw-count inflation report beyond exact-title duplicates, and owner review
    signoff; then publish raw checklist completion separately from canonical
    underlying-gap completion.

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
    benchmarks. `papers/alphaevolve_source_inventory_boundary.json` now
    verifies the pinned 44-page PDF and all 55 named spans using 57 page-local
    anchors: 38 structural spans, 14 numbered figures, and 3 numbered tables.
    `papers/alphaevolve_system_requirement_inventory_boundary.json` now adds
    claim-level dispositions for 55 implementation-bearing requirements across
    all eight Table 1 rows, Sections 2.1-2.6, and Figures 1-3. It records 14
    locally implemented, 31 partial, 4 not-implemented, and 6 undemonstrated
    requirements, with live domain TODO ownership for all 41 incomplete rows.
    `papers/alphaevolve_context_claim_inventory_boundary.json` now adds 45
    exact-page Abstract, Introduction, Discussion, and collaborator-context
    dispositions: 6 locally implemented, 11 partial, 4 not implemented, and 24
    not demonstrated, with live TODO ownership for all 39 gaps.
    `papers/alphaevolve_matrix_result_claim_inventory_boundary.json` now adds
    44 exact-page Section 3.1, Table 2, Figure 4, and footnote 3 dispositions:
    none locally implemented, 8 partial, 3 not implemented, and 33 not
    demonstrated, with live TODO ownership for all 44 gaps. These inventories
    include the Introduction's 4x4 complex rank-48, roughly 75-percent best-
    known-match, and dimension-11 Kissing Numbers statements plus Section
    3.1's unknown minimum rank for 3x3 multiplication. The
    `papers/alphaevolve_math_result_claim_inventory_boundary.json` now adds 63
    exact-page Section 3.2 and Figure 5 dispositions: 2 locally implemented,
    16 partial, 4 not implemented, and 41 not demonstrated, with live TODO
    ownership for all 61 gaps and a checked source-fidelity correction. The
    `papers/alphaevolve_scheduling_claim_inventory_boundary.json` now adds 45
    exact-page Section 3.3 opening, Section 3.3.1, and Figure 6 dispositions:
    none locally implemented, 19 partial, 14 not implemented, and 12 not
    demonstrated, with live TODO ownership for all 45 gaps. The
    `papers/alphaevolve_kernel_claim_inventory_boundary.json` now adds 59
    exact-page Section 3.3.2 and Figure 7 dispositions: none locally
    implemented, 6 partial, 37 not implemented, and 16 not demonstrated, with
    live TODO ownership for all 59 gaps. The
    `papers/alphaevolve_hardware_claim_inventory_boundary.json` now adds 35
    exact-page Section 3.3.3 dispositions: none locally implemented, 12
    partial, 4 not implemented, and 19 not demonstrated, with live TODO
    ownership for all 35 gaps. The
    `papers/alphaevolve_compiler_claim_inventory_boundary.json` now adds 44
    exact-page Section 3.3.4 dispositions: none locally implemented, 22
    partial, 6 not implemented, and 16 not demonstrated, with live TODO
    ownership for all 44 gaps. The
    `papers/alphaevolve_ablation_claim_inventory_boundary.json` now adds 51
    exact-page Section 4 and Figure 8 dispositions: 2 locally implemented, 36
    partial, 6 not implemented, and 7 not demonstrated, with live TODO
    ownership for all 49 gaps and source-faithful 6-series/3-series panel
    coverage. The
    `papers/alphaevolve_related_work_claim_inventory_boundary.json` adds 85
    exact-page Section 5 claims: 6 locally implemented, 9 partial, 4 not
    implemented, 7 not demonstrated, and 59 source-context-only, with active
    ownership for all 20 implementation gaps. The
    `papers/alphaevolve_appendix_a_claim_inventory_boundary.json` adds 131
    exact-page Appendix A, Table 3, and Figure 9 dispositions: 13 partial and
    118 not demonstrated, with ownership for all 131 gaps. The
    `papers/alphaevolve_appendix_b_claim_inventory_boundary.json` adds 188
    exact-page and visible-panel Appendix B/Figures 10-14 dispositions: 95
    partial, 24 not implemented, and 69 not demonstrated, with code and paper
    TODO ownership for all 188 gaps. The bounded claim-level ROADMAP surface
    therefore covers 845 claims: 30 locally implemented, 278 partial, 110 not
    implemented, 368 not demonstrated, and 59
    source-context-only. The supplemental
    `papers/alphaevolve_citation_use_inventory_boundary.json` adds lexical
    coverage for all 195 retained-TeX citation uses, 240 key links, all 120
    compiled references, and 52 unused BibTeX entries. It does not add claims
    to the 845-row implementation aggregate because citation semantics and
    implementation relevance remain unclassified under active TODO ownership.
    `papers/alphaevolve_tex_source_detail_inventory_boundary.json` separately
    dispositions all 30 retained-source constructs: 22 captions, 5 equation
    environments, and 3 semantic footnotes. Twenty-four map through 80 resolved
    references to existing bounded claim ids, one maps to publication metadata,
    two are named-span locators, and three are decorative markers; this adds no
    claims or parity credit. The supplemental
    `papers/alphaevolve_tex_table_cell_inventory_boundary.json` dispositions
    all 83 rows and 240 top-level cells across Tables 1-3. All 78 data rows map
    to 78 existing bounded claim ids; 218 cells are bounded-claim components,
    8 are FunSearch baseline context, and 14 are structural headers. There are
    no unmapped units or unresolved references, and no claims or parity credit
    are added. The supplemental
    `papers/alphaevolve_tex_code_listing_inventory_boundary.json` dispositions
    all 8 retained listing environments and 305 physical source lines. It maps
    214 bounded-claim-component lines through 344 line-level references to 60
    existing claims and dispositions the remaining baseline, abbreviation,
    diff-marker, and structural lines, with no unmapped or unresolved units and
    no new claims or parity credit.
    `papers/alphaevolve_tex_math_inventory_boundary.json` dispositions all 309
    explicit TeX math constructs: 291 inline and 18 display constructs. It
    inherits 34 source-detail and 75 table-cell dispositions and maps the
    remaining 200 constructs directly to existing bounded claim ids, with no
    unmapped or unresolved references and no new claims or parity credit.
    `papers/roadmap_source_span_disposition_boundary.json` now maps all 55
    named spans to ROADMAP section ids, phase buckets, local status, sidecars,
    and audit TODO links, and records that only the AlphaEvolve
    source row is dispositioned while the broader paper-index rows are not.
    `papers/README.md` and the Appendix A/B registries provide many
    source-specific status rows, but those records are not an exhaustive
    ROADMAP coverage proof.
    `papers/roadmap_source_span_coverage_boundary.json` now records a
    ROADMAP-level coverage readiness matrix for main-text sections, figures,
    tables, Appendix A, Appendix B, application-result claims, paper-status
    rows, and TODO/non-goal/phase proof.
    `papers/roadmap_source_span_exhaustiveness_boundary.json` now records a
    bounded eight-criterion exhaustiveness gate that credits the named PDF
    structure walk and all twelve bounded claim inventories while preserving
    remaining whole-paper and joined-semantic work for the figure/table/appendix matrix,
    application-result reproduction/non-goal proof beyond the bounded Section
    3.3/Section 4/Section 5 claim matrices,
    status-row disposition map, span status classification, missing/partial
    TODO proof, phase-priority map, and CI/owner signoff.
  - Current gap: the retained PDF's named sections, figures, tables, and
    appendices now have verified dispositions, local status classes, ROADMAP
    sections, and phases, and 845 bounded system/context/matrix-result/
    constructive-math/scheduling/kernel-engineering/hardware/compiler/ablation/
    related-work/Appendix-A/Table-3/Figure-9/Appendix-B/Figures-10-14 claims have
    claim-level mappings, citation syntax plus bibliography-key linkage is
    exhaustive for the retained TeX, and all caption/equation-environment/
    footnote constructs have dispositions, all 83 table rows and 240 cells have
    row/cell dispositions, all 8 code listings and 305 source lines have
    line-level dispositions; all 309 math constructs and 402 prose sentences
    have dispositions; 93 propositions in 37 Abstract/Introduction sentences
    are reviewed. The matrix remains incomplete
    across the rest of the paper: 365 sentences
    still lack proposition review; it cannot prove
    local math/image/citation correctness and result reproduction;
    show TODO ownership for every gap and add an application matrix;
    disposition every paper/status row;
    finish independent review;
    keep owner signoff.
  - Required result: implement the missing readiness fields recorded by the
    exhaustiveness sidecar: whole-paper requirement, citation-semantic, and joined semantic
    figure/table/appendix matrices, application-result claim matrix, status-row to ROADMAP
    disposition map, domain-specific missing/partial TODO proof, non-goal
    decision map, claim-level phase-priority map, CI
    source-span exhaustiveness gate, and owner review signoff.

## Existing Items That Need Tightening

- [ ] Add ROADMAP non-goal contradiction checks.
  - Spec evidence: ROADMAP non-goals are overclaim guardrails. If the project
    says it is not requiring a service database, not claiming arbitrary-
    language/codebase parity before portable toolchains, language-aware
    mutation, and representative validators exist, and not
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
    `papers/roadmap_non_goal_markdown_scan_boundary.json` now scans the
    repository Markdown corpus against the stable ROADMAP non-goal ids, records
    the scanned Markdown file inventory, checks all configured forbidden
    support-claim phrases, and retains zero line-level contradiction hits.
    `papers/roadmap_non_goal_plugin_docstring_boundary.json` now scans built-in
    plugin Python source files, AST docstrings, registry labels, and
    paper-inspiration labels for faithful-implementation overclaims, with zero
    detected faithful-claim hits and no missing non-faithful disclaimers for
    the paper-inspired built-ins.
    `papers/roadmap_non_goal_runtime_metadata_boundary.json` now scans
    source-defined runtime metadata surfaces for startup manifest plugin/config
    fields, candidate-language runner policy, runtime plugin state, runtime
    plugin artifact metadata, and built-in plugin registry paper-inspiration
    labels, with zero contradictory support-claim hits.
    `papers/roadmap_non_goal_ci_promotion_gate_boundary.json` now records that
    GitHub Actions path filters cover ROADMAP/docs/papers/test/source changes,
    the `paper_docs` job runs the committed paper manifest, and the boundary
    verifier suite includes the ROADMAP non-goal contradiction, drift,
    Markdown, plugin docstring, and runtime metadata tests.
    `papers/roadmap_non_goal_promotion_workflow_boundary.json` now records the
    written intentional promotion workflow in
    `docs/roadmap-non-goal-promotion-workflow.md`, including required updates
    for ROADMAP, README, papers, status, TODO ledgers, non-goal sidecars, and
    the paper-manifest gate.
    `papers/roadmap_non_goal_remediation_boundary.json` now records a
    contradiction-remediation report that aggregates the bounded documentation
    inventory, Markdown corpus scan, plugin docstring scan, and runtime
    metadata scan, rejects contradictory support claims through a zero
    unresolved-hit requirement, and routes any future hit to TODO ownership
    and claim-update surfaces.
    `papers/roadmap_non_goal_scope_join_boundary.json` now joins the three
    stable ROADMAP non-goal ids across bounded documentation surfaces, the full
    Markdown corpus scan, runtime metadata source scans, built-in plugin
    docstring and registry scans, paper sidecar records, `docs/status.md`
    references, and remediation-route ownership with zero joined
    contradictions.
  - Current gap: the sidecars are bounded documentation and readiness
    inventories plus runtime, Markdown, plugin-source phrase scans, and CI
    workflow-shape promotion gating plus a written promotion workflow,
    contradiction-remediation report, and runtime/plugin/docs/paper scope
    join, not a full lifecycle gate. There is still no owner review signoff
    proving future ROADMAP edits cannot accidentally promote a non-goal into a
    supported AlphaEvolve-parity claim.
  - Required result: implement the missing readiness fields recorded by the
    sidecars: owner review signoff.

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
    `papers/roadmap_good_first_dependency_refresh_boundary.json` now refreshes
    the four current priority items against their live active TODO dependency
    refs, current blocker labels, validation gate expectations, and
    AlphaEvolve impact labels, with zero stale dependency refs.
    `papers/roadmap_good_first_stale_priority_boundary.json` now joins the
    static priority map to dependency-refresh records, ordinal order, live
    dependency refs, blocker labels, and ROADMAP phrase checks, with zero
    stale priority records.
    `papers/roadmap_good_first_priority_score_boundary.json` now records a
    bounded deterministic priority score model with feature weights,
    dependency-readiness scores, AlphaEvolve-impact scores, score records,
    ranked item ids, and zero rank mismatches.
    `papers/roadmap_good_first_ci_priority_gate_boundary.json` now records the
    committed sidecars, paper-manifest validators, and docs/paper/boundary
    GitHub Actions workflow markers that gate Good First priority freshness,
    with zero missing gate records.
    `papers/roadmap_good_first_validation_artifact_boundary.json` now records
    the expected validation artifacts for those four priority items by joining
    each validation gate to artifact-family labels, committed sidecar refs,
    active TODO anchors, and the CI priority freshness gate, with zero stale
    validation-artifact records.
  - Current gap: the sidecars are bounded static-priority, dependency-refresh,
    stale-priority, priority-score, CI-gate, validation-artifact, and
    freshness readiness maps, not owner-reviewed priority approval. There is
    still no owner review signoff proving these four items remain the best
    first follow-ups after new ROADMAP, code, README, or paper-sidecar work
    lands.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: owner review signoff. The drift check must force the section to
    be refreshed when dependencies or implementation states change.

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
    `papers/roadmap_phase_dependency_graph_boundary.json` now records a
    bounded dependency graph for the ten major ROADMAP sections, linking each
    section to prerequisite section edges, section evidence sidecars, and
    active blocker TODO refs, with zero stale dependency edges.
    `papers/roadmap_phase_staleness_boundary.json` now records a bounded
    stale-phase detector for the ten major ROADMAP sections by joining the
    phase sequence map, dependency graph, active blocker TODO refs, section
    sidecar presence, and dependency edge status, with zero stale phase
    records.
    `papers/roadmap_phase_promotion_workflow_boundary.json` now records the
    written ROADMAP phase promotion/demotion workflow in
    `docs/roadmap-phase-promotion-workflow.md`, including required updates for
    ROADMAP, README, papers, status, TODO ledgers, phase sidecars, dependency
    graph refresh, stale phase record resolution, and the paper-manifest gate.
    `papers/roadmap_phase_ci_freshness_gate_boundary.json` now records the
    bounded CI phase freshness gate for committed phase sidecars, paper-
    manifest validators, docs/libreevolve/papers/tests path filters, and
    docs/paper/boundary GitHub Actions workflow markers, with zero missing
    gate records.
    `papers/roadmap_phase_freshness_boundary.json` now records a six-
    criterion phase freshness readiness matrix for the dependency graph,
    stale-phase detector, promotion/demotion workflow, CI phase freshness
    gate, evidence-status refresh, and owner review signoff.
  - Current gap: the sidecars are bounded static-sequence, dependency-graph,
    stale-detector, promotion-workflow, CI-gate, and freshness readiness maps,
    not a full phase-lifecycle model. There is still no implemented
    evidence-status refresh report or owner review signoff
    proving that a ROADMAP item still belongs in Near Term, Mid Term, or
    Longer Term after related code, papers, README, or sidecar evidence
    changes.
  - Required result: implement the missing readiness fields recorded by the
    sidecar: evidence-status refresh report and owner review signoff. The
    verifier must keep each major section linked to prerequisites, blocking
    TODOs, validation gates, and promotion criteria, then validate that phase
    labels and item ordering are refreshed when implementation or evidence
    status changes.

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
    release provenance, cross-platform CI policy, and owner review signoff,
    plus a per-surface operational maturity claim guard.
  - Current gap: the per-surface operational maturity claim guard is a bounded
    allowed-scope map, not an operational readiness gate. There is still no
    implemented global acceptance threshold, unified generated-artifact
    lifecycle inventory, semantic docs verification, signed release
    provenance, cross-platform CI policy, or owner signoff preventing one
    green release/CI boundary from being mistaken for overall operational
    readiness.
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
    balance/CI freshness gate, plus a per-surface benchmark-portfolio claim
    guard.
  - Current gap: the per-surface benchmark-portfolio claim guard is a bounded
    allowed-scope map, not a representative-readiness gate. There is still no
    implemented domain-coverage matrix, benchmark admission checklist,
    repeated-seed run matrix, anti-gaming certification, SOTA/baseline citation
    sufficiency proof, portfolio-balance score, stale-coverage detector, CI
    freshness gate, or owner signoff proving the representative-benchmark list
    is balanced, feasible, non-duplicative, and strong enough to support
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
    policy, and paper-scope attribution/stale-readiness guard, plus a
    per-surface plugin claim guard.
  - Current gap: the per-surface plugin claim guard is a bounded allowed-scope
    map, not an external plugin readiness gate. There is still no implemented
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
    Gemini-provider partial-readiness records, and synchronous first/last-valid
    critique reviewer aggregation from missing calibrated rewards, quotas,
    live provider/default pricing, raw replay, hard cancellation, equal-budget
    scheduler comparisons, live Gemini Flash/Pro pair evidence, async reviewer overlap,
    reviewer isolation, and critique-to-revision attribution. Active code and
    paper TODOs track those individual gaps. The bounded
    `papers/roadmap_backend_scheduling_critique_boundary.json` sidecar now
    records nine tracks: heuristic UCB rewards, role-scoped routing, provider
    diagnostics/pricing, cancellation/quarantine, fast/strong model mix,
    sample efficiency, repeated-sampling baselines, Gemini provider parity, and
    critique reviewer pools, with selection-policy, reward-assumption,
    budget/quota, pricing/default-rate, diagnostics/replay, cancellation,
    resume, equal-budget, reviewer-isolation, Gemini-substitution,
    sidecar-ref, active-TODO, validation-gate, readiness labels, and an
    explicit backend-role capability matrix, reward-assumption policy, role
    budget/quota policy, provider pricing/default-rate evidence map, and
    diagnostics/replay policy, cancellation/resume policy, plus a
    bounded equal-budget comparator evidence map, Gemini substitution policy,
    plus a critique-control checklist derived from those track records.
    The bounded
    `papers/roadmap_backend_control_plane_readiness_boundary.json` sidecar now
    records eight readiness criteria for backend-role capability, calibrated
    reward/quota policy, live pricing/default and raw replay, hard
    cancellation/resume, equal-budget scheduler comparison, Gemini
    lane/substitution, critique reviewer isolation, and stale readiness/owner
    signoff, and records the backend-role capability matrix as resolved
    evidence from the scheduling/critique boundary. It also records the
    critique-control checklist as resolved structural evidence from the same
    source boundary, plus a per-surface backend control-plane claim guard.
  - Current gap: the backend-role capability matrix is structural inventory,
    not a control-plane readiness gate, the reward-assumption policy is a
    descriptive policy map rather than calibrated reward evidence, the role
    budget/quota policy is a descriptive ownership map rather than
    experiment-owned quota enforcement, the provider pricing/default-rate map
    is configured/default-bound evidence rather than live provider pricing
    capture, the diagnostics/replay policy is bounded scalar/metadata replay
    evidence rather than raw provider replay, the cancellation/resume policy is
    bounded policy/snapshot evidence rather than live hard cancellation or full
    resumed-trace proof, the equal-budget comparator evidence map is mostly
    absence evidence rather than an executable comparator, the Gemini
    substitution policy is a status map rather than live Gemini Flash/Pro pair
    evidence, and the critique-control checklist is a synchronous-reviewer
    structural checklist, not async reviewer-readiness evidence. There is still
    no calibrated reward policy, role quota ownership, live provider
    pricing/default evidence, raw provider replay, live hard cancellation,
    equal-budget scheduler comparator, live Gemini Flash/Pro pair evidence, async
    reviewer isolation, stale-readiness detector, or owner signoff proving when
    these scheduler/provider/critique pieces are coherent enough to support
    AlphaEvolve-style claims, nor a guard that prevents one completed
    subfeature from implying full backend scheduling maturity. The sidecars are
    bounded track/readiness/claim-guard maps, not a backend control-plane gate.
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
    and resumable runtime, not only bounded local sampler/evaluation overlap,
    sample-worker fan-out, terminal snapshots, and partial-boundary metadata.
  - Current evidence: ROADMAP now records opt-in bounded local Python `asyncio`
    queues for worker-owned LLM samplers and candidate evaluation, named workers,
    backpressure, out-of-order completion, deterministic proposal-result and
    candidate-admission ordering, owner-serialized reward updates, serial shared-
    state commit, and exact in-flight evaluation duplicate coalescing. It now
    also records `async_generation_window`: values above one allow bounded
    later-generation sampling from pre-drain archive, prompt-program/reward,
    and sampler-reward state while prior
    evaluation is in flight; process-local task intervals prove observed
    overlap, and generation-grouped drains preserve admission and lifecycle
    order. It also
    records parallel-evaluation readiness
    reports, terminal controller-state evidence, MAP-Elites archive snapshots,
    cursor/full archive restore surfaces, run manifest hardening, framework RNG
    restore, terminal budget counters, and validated sidecars for pipeline topology,
    parallel evaluation, controller pending-work resume, archive-event replay,
    lineage replay, and LLM budget policy. Active code and paper TODOs already
    track distributed evaluators, cross-generation proposal control, ordered archive
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
  - Current gap: there is no complete async-state inventory, replay-resume
    acceptance checklist, controller queue checkpoint, resumable LLM sampler
    task state, evaluator pending-work restore, distributed dependency scheduler
    or worker ownership, ordered migration restore engine, provider-output
    replay, plugin RNG replay, async worker/compute-hour budget
    accounting, external environment replay, end-to-end resumed trace proof,
    stale-readiness detector, or owner signoff. Local deterministic merge and
    terminal drain evidence must not be mistaken for full async/resumable
    runtime parity. The sidecars remain bounded criteria/readiness maps rather
    than an async runtime control-plane gate.
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
    evidence, and stale readiness/owner signoff, plus a per-surface
    prompt/context claim guard.
    Active code and paper TODOs already track role-specific template
    compatibility, all-role provider-token packing, separate stochastic format
    source provenance, structured prompt-context policy expansion,
    audit-grade retrieval integrity, semantic proposal retrieval, calibrated
    meta-prompt rewards, and prompt-database parity.
  - Current gap: the per-surface prompt/context claim guard is a bounded
    allowed-scope map, not a section-level prompt/context readiness rubric,
    capability matrix, or stale-readiness detector proving these features
    compose into a safe AlphaEvolve-style prompt system. The sidecars are
    bounded feature/readiness/claim-guard maps, not a full prompt-system gate.
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
    reconciled adjacent-stage promotion-linkage matrices, optional complete
    difficulty/scale and content-hashed test-set identity contracts,
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
    readiness/owner signoff, plus a per-surface evaluation-cascade claim
    guard. Active code and paper TODOs already track cascade
    promotion/attrition evidence, statistical hypothesis-test semantics,
    qualitative feedback provenance, async/accelerator budgets, evaluator
    environment replay, validator sandbox/resource policy, release artifacts,
    matrix cascade runs, and workload-specific provenance.
  - Current gap: the per-surface evaluation-cascade claim guard is a bounded
    allowed-scope map, not a section-level cascade-readiness rubric,
    evaluator/oracle capability matrix, artifact-and-budget sufficiency
    checklist, or stale-readiness detector tying those pieces together. The
    sidecars are bounded cascade/readiness/claim-guard maps, not a full
    AlphaEvolve cascade gate.
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
    policy, equal-budget benchmark evidence, and stale readiness/owner
    signoff, plus a per-surface multi-objective claim guard.
  - Current gap: the per-surface multi-objective claim guard is a bounded
    allowed-scope map, not a section-level multi-objective readiness rubric,
    archive-policy matrix, descriptor/memory capability checklist, or
    stale-readiness detector tying those pieces together. The sidecars are
    bounded search/readiness/claim-guard maps, not a full multi-objective
    search gate, and not full multi-objective search parity.
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
  - Current evidence: ROADMAP records metadata-only or executable
    candidate-language/build declarations, checked task-primary local expression
    and C compiler build/runner/scorer fixtures, code-file-set divergence from
    AlphaEvolve's flexible
    solution-abstraction API, candidate-abstraction design matrices,
    Python-only evolve-block marker handling, `workspace_math` smoke fixtures,
    Table 1 codebase-scale absence reports, fixed diff/full/file/block/topology
    mutation parser evidence, prompt-example copy diagnostics,
    mutation-consistency reports, initial-pool divergence reports,
    binary/static candidate handling, topology materialization diagnostics, and
    archive-content restore boundaries. Active code and paper TODOs already
    track portable and broader language/build runners, candidate-embedded evaluators,
    abstraction-choice benchmark evidence, topology diagnostics, adaptive
    mutation modes, mutation-operator provenance, validator boundary checks,
    source/workspace integrity, binary/static replay policy, codebase-scale
    evidence, and ordered migration-event replay.
    `papers/roadmap_candidate_workspace_fidelity_boundary.json` now records a
    ten-criterion section-level readiness matrix with current scope,
    missing-readiness, sidecar-ref, active-TODO, validation-gate, and readiness
    labels. The matrix now treats local command execution as partial capability
    rather than absent support.
    `papers/roadmap_candidate_workspace_readiness_boundary.json` now records a
    bounded eight-criterion readiness matrix for language/build runner and
    candidate API readiness, embedded evaluator and codebase-scale readiness,
    materialization/topology readiness, mutation-mode and operator provenance,
    prompt-copy and cross-file consistency, initial-pool/static-binary policy,
    resume replay and manifest/workspace-doc policy, and stale
    readiness/owner signoff, plus a per-surface candidate-workspace claim
    guard.
  - Current gap: the per-surface candidate-workspace claim guard is a bounded
    allowed-scope map, not evidence that the missing candidate-workspace
    capabilities are implemented. A passing Python workspace, local expression/
    C runner, or single digest-pinned OCI Python fixture, fixed diff parser,
    snapshot restore, or
    materialization diagnostic still must
    not be mistaken for complete AlphaEvolve-style workspace support.
  - Required result: implement the missing readiness fields recorded by the
    readiness sidecar: portable hermetic and broader language/build runners
    beyond the local expression, host C, and single-image OCI Python smoke
    fixtures, package lock restoration plus deterministic platform/daemon
    replay, flexible solution
    abstraction API, candidate-embedded evaluator contracts, realistic codebase
    fixtures, benchmark-calibrated adaptive mutation-mode policy, mutation-operator family
    provenance, semantic prompt-example-copy detection, cross-file consistency
    benchmark evidence, initial-pool divergence benchmark evidence,
    static/binary replay policy, topology resume replay proof,
    stale-readiness detector, and owner review signoff; then validate README,
    ROADMAP, papers, run manifests, and workspace docs against implying full
    candidate-workspace fidelity before those criteria are satisfied.
