# Completed Readme Todo Items

Moved from `docs/todo/readme.md`. Completed README backlog items live here so the active README todo file contains only open work.

## Recovered Completed Items

- [x] Keep README backlog-integrity wording scoped until stale source-specific
      absence prose is validated.
  - Spec evidence: README should describe the paper cache and TODO ledgers as
    evidence-backed only to the extent active TODO text is internally
    consistent.
  - Status: README now states that manifest-id-scoped `no source-specific ...
    TODO` claims fail when the referenced active ledger already has an open
    TODO block for that paper id, while broader paraphrases remain review or
    future-pattern work.
  - Remaining gap: none for this bounded README wording slice; broader
    implementation-status semantics remain active TODOs.

- [x] Keep README paper-index traceability wording scoped until TODO coverage
      cross-references are validated.
  - Spec evidence: `papers/README.md` presents a TODO coverage table that
    should be validated before README treats it as a backlog traceability map.
  - Status: README now describes the paper-manifest TODO coverage validator:
    one row per manifest id, active cells tied to open `docs/todo/*.md` blocks,
    completed cells tied to source-specific completed checklist evidence, and
    grouped labels rejected until a grouped-label taxonomy exists. README also
    keeps this separate from implementation-status semantic completeness.
  - Remaining gap: none for this bounded README wording slice; stale absence
    prose and broader status-cell semantics remain active TODOs.

- [x] Keep README DeepMind-blog wording scoped until official announcement
      source provenance exists.
  - Spec evidence: the May 14, 2025 Google DeepMind blog article is an
    official public AlphaEvolve announcement with white-paper/Colab links,
    systems summaries, Early Access plans, and blog-specific metric wording.
  - Status: README now documents `papers/official_deepmind_blog.json` as
    announcement-source evidence with URL/date/title/team, retrieval hash,
    outbound links, claim variants, availability statements, and role metadata,
    while separating it from audited white-paper specification and reproduced
    LibreEvolve evidence.
  - Remaining gap: none for this bounded README wording slice; claim-to-paper/
    Colab mappings and metric variant reconciliation remain active TODOs.

- [x] Keep README theoretical-CS AlphaEvolve wording scoped until
      proof-element source tracking exists.
  - Spec evidence: Google Research's September 30, 2025 article and arXiv
    `2509.18057v7` describe finite AlphaEvolve-discovered proof elements,
    lifting frameworks, verifier-speedup claims, and final brute-force
    verification.
  - Status: README now documents `papers/theoretical_cs_sources.json` as later
    theoretical-CS proof-element source evidence, separated from original
    AlphaEvolve spec parity, 67-problem constructive-math source coverage,
    formal theorem proving, and local graph/certification implementation.
  - Remaining gap: none for this bounded README wording slice; graph/gadget
    artifacts and certification benchmark wording remain active TODOs.

- [x] Keep README Tao-blog follow-on wording scoped until source metadata
      exists.
  - Spec evidence: the November 5, 2025 Tao blog post links the follow-on
    arXiv paper and problem repository and adds commentary on AlphaEvolve
    experiment lessons and proof handoffs.
  - Status: README now documents `papers/follow_on_tao_blog.json` as secondary
    source commentary with URL/date/metadata, claim categories, retrieval
    hashes, linked arXiv/repository/tool URLs, and the boundary that blog-only
    claims need backing artifacts before supporting implementation-parity
    claims.
  - Remaining gap: none for this bounded README wording slice; theoretical-CS
    wording and exact proof-handoff artifact wording remain active TODOs.

- [x] Keep README follow-on runtime-availability wording scoped.
  - Spec evidence: the follow-on repository README says notebooks contain
    prompts, verification code, initial programs, final evolved programs, and
    visualization/analysis code where appropriate, but do not contain the code
    to run AlphaEvolve.
  - Status: README now documents `papers/follow_on_runtime_absence.json` as
    the committed runtime-availability sidecar for the pinned problem
    repository, distinguishing prompt/verifier/final-program source artifacts
    from executable AlphaEvolve runtime code and naming the remaining
    per-problem, SHA-256, and cell-level inventory gaps.
  - Remaining gap: none for this bounded README wording slice; Tao-blog
    wording, full notebook inventory, and cached follow-on PDF wording remain
    separate active README TODOs.

- [x] Document follow-on problem-repository rights and attribution.
  - Spec evidence: the follow-on repository README records citation, dual
    license, disclaimer, role-attribution, and Problem 65 source-origin terms.
  - Status: README now documents `papers/follow_on_repository_rights.json` as
    the committed source-use sidecar for the pinned problem repository,
    separating repository terms from original AlphaEvolve PDF rights,
    `alphaevolve_results` companion rights, and LibreEvolve licensing.
  - Remaining gap: none for this bounded README wording slice; runtime
    availability and per-problem source/artifact inventory wording remain
    active TODOs.

- [x] Document committed follow-on AlphaEvolve math-source manifest.
  - Spec evidence: AlphaEvolve Section 3.2 points to a forthcoming
    constructive-math paper; current source evidence identifies arXiv
    `2511.02864v3`, `Mathematical exploration and discovery at scale`, and the
    `google-deepmind/alphaevolve_repository_of_problems` repository.
  - Status: README now documents `papers/follow_on_sources.json` as the
    committed follow-on source manifest with docs/TODO claim-surface links,
    pinned repository identity, explicit no-cache policy, and the boundary that
    this is later math-source evidence, not the original `2506.13131`
    specification or a cached PDF row.
  - Remaining gap: none for this bounded README wording slice; per-problem
    coverage, notebook artifact hashes, Appendix B mappings, rights rows, and
    cached PDF evidence remain separate active TODOs.

- [x] Document companion repository rights rows on generated artifacts.
  - Spec evidence: the companion repository README declares Apache-2.0 software
    licensing, CC-BY-4.0 materials licensing, AS-IS disclaimer, and
    non-official-product status.
  - Status: README now documents companion artifact-rights rows on generated
    matrix reports and inventories, including companion-source links, license
    split, local-generated versus copied/adapted source relationships, source-
    PDF rights separation, LibreEvolve MIT separation, AS-IS disclaimer,
    non-official-product, and non-endorsement boundaries.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document companion notebook selection-scope provenance.
  - Spec evidence: the companion repository README limits
    `mathematical_results.ipynb` to outperformed-SOTA results, excludes
    matched-only results, and says the repository does not contain AlphaEvolve
    runtime code.
  - Status: README now documents companion selection-scope rows for included
    improved results and intentionally absent matched-only results, including
    verifier-code availability, runtime-code absence, and matrix report
    validation for the `mm_4x4x4` companion claim.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document committed AlphaEvolve companion Colab source manifest.
  - Spec evidence: AlphaEvolve footnote 2 and Table 2 point readers to the
    accompanying `google-deepmind/alphaevolve_results` Colab notebook for
    discovered algorithms, mathematical results, and shown matrix
    decompositions.
  - Status: README now documents `papers/companion_sources.json` as the
    committed companion manifest that emits the external source row, docs/TODO
    claim-surface links, and local-cache policy, with paper-manifest
    validation.
  - Remaining gap: none for this bounded README wording slice; local generated
    notebooks/exports and per-claim absence rows remain open elsewhere.

- [x] Document normalized AlphaEvolve References bibliography evidence.
  - Spec evidence: the AlphaEvolve PDF has a numbered References section after
    Author information, with entries through `[120]`.
  - Status: README now documents `papers/references.json` as the committed
    companion manifest with normalized rows for all 120 references, including
    raw citation text, bibliographic fields, detected DOI/URL/arXiv fields,
    local-cache linkage, and citation-use categories.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document AlphaEvolve source-PDF rights manifest evidence.
  - Spec evidence: the local AlphaEvolve PDF header states
    `© 2025 Google DeepMind. All rights reserved`.
  - Status: README now documents `papers/source_rights.json` as the committed
    companion manifest that emits the AlphaEvolve source-rights row, links it
    to `papers/row_identity.json`, and records reproduction-policy
    requirements for excerpts, tables, figures, quotes, and appendix claims.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document paper-cache row identity artifact evidence.
  - Spec evidence: README points readers to the local paper cache as the source
    ledger for paper-facing implementation status and benchmark decisions.
  - Status: README now documents `papers/row_identity.json` as the committed
    companion manifest that emits derived source identities for all 24 cache
    rows, including URL source id, filename source prefix, validation booleans,
    and the AlphaEvolve row's source-version link.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document AlphaEvolve source-PDF version manifest evidence.
  - Spec evidence: the local AlphaEvolve PDF header says
    `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`.
  - Status: README now documents `papers/source_versions.json` as the
    committed companion manifest that emits the `2506.13131v1` source-version
    row, versioned URLs, expected header page/text, and docs/TODO claim-surface
    links validated by the paper-manifest gate.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document cross-run prompt-current binding table evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) shows edits to the current
    program rendered in the prompt.
  - Status: README now says completed manifests export
    `prompt_current_binding_table.jsonl` with schema-versioned rows carrying
    run ids for cross-run comparison.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document full-mode target span and block-id records in prompt-current
      binding evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) shows edits to the current
    program rendered in the prompt.
  - Status: README now says `runtime.history.prompt_current_binding_report`
    includes full-mode whole-file and evolve-block target span records.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document prompt-history row joins in prompt-current binding evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) shows edits to the current
    program rendered in the prompt.
  - Status: README now says `runtime.history.prompt_current_binding_report`
    includes prompt-history row joins to candidate history rows.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document workspace file-section span records in prompt-current binding
      evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) shows edits to the current
    program rendered in the prompt.
  - Status: README now says `runtime.history.prompt_current_binding_report`
    includes workspace file-section target records with parent/candidate
    full-file span and hash evidence.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document evolve-block inner span mapping in prompt-current binding
      evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) shows edits to the current
    program rendered in the prompt.
  - Status: README now says `runtime.history.prompt_current_binding_report`
    maps exact SEARCH matches inside parent evolve-block content to block
    names, block spans, and block-relative SEARCH spans.
  - Remaining gap: none for this bounded README wording slice.

- [x] Document normalized and skeleton prompt-example copy diagnostics.
  - Spec evidence: AlphaEvolve Figure 3(b,c) uses concrete examples to
    communicate the mutation format without making those examples valid
    candidate content.
  - Status: README now says `runtime.history.prompt_example_copy_report`
    records exact, normalized, and example-skeleton copy signals while keeping
    hard rejection and custom-template semantic detection open.
  - Remaining gap: configurable rejection, custom prompt-template inventories,
    and broader semantic/renamed copy detection remain active README TODOs.

- [x] Document current-run multi-edit consistency diagnostics.
  - Spec evidence: AlphaEvolve Figure 3(b) requires same-response edits to be
    consistent with each other.
  - Status: README now documents
    `runtime.history.mutation_consistency_report`, including multi-edit
    payload records, changed edit units, diagnostic co-change links,
    best-effort Python symbol/reference scans, unresolved-reference
    diagnostics, evaluator status, and archive admission.
  - Remaining gap: README keeps language-aware scope/import resolution,
    config/resource dependency models, required-link inference, benchmark
    calibration, and gating as future work.

- [x] Document bounded explanatory preambles before structured mutations.
  - Spec evidence: AlphaEvolve Figure 3(c) shows explanatory text before a
    SEARCH/REPLACE payload.
  - Status: README now documents
    `runtime.history.natural_language_preamble_report`, leading preamble
    redaction/provenance, accepted diff/block/file-section boundaries, and
    continued rejection of prose between or after mutation markers.
  - Remaining gap: README wording must be updated again if future work adds
    configurable preamble policy, full-replacement disambiguation, rationale
    scoring, or cross-run preamble tables.

- [x] Keep README/AGENTS diff-format wording scoped until canonical
      AlphaEvolve fence guidance is primary.
  - Spec evidence: AlphaEvolve Section 2.3 and Figure 3 show the
    SEARCH/REPLACE payload using canonical fences: `<<<<<<< SEARCH`,
    `=======`, and `>>>>>>> REPLACE`.
  - Status: README already documents both compact local fences and canonical
    AlphaEvolve fences, parser tests cover both forms, and `AGENTS.md` now
    names canonical fences as the paper-aligned format while keeping compact
    fences as compatibility input.
  - Remaining gap: none for README/AGENTS diff-format wording; natural-language
    preambles, prompt-example copy detection, and multi-edit consistency remain
    active TODOs.
  - Verification: validation for this slice reran the paper manifest, secret
    scan, and diff checks before commit.

- [x] Document declared final-fitness objective metrics.
  - Status: README, problem-format, configuration, plugin, architecture, and
    paper-index docs now describe non-primary `source: final_fitness` metrics,
    explain that validators must not return them, and state that they are
    synthesized from the candidate's final composed fitness after plugin score
    hooks run.
  - Remaining README gap: Pareto/frontier archive replacement and
    lineage-aware resurfacing remain open.
  - Verification: docs were updated alongside focused loader/loop tests for
    final-fitness objective metrics.

- [x] Document declared plugin-sourced objective metrics.
  - Status: README, problem-format, configuration, plugin, and architecture
    docs now describe non-primary `source: plugin` metrics, explain that
    validators must not return them, and state that plugin hooks can fill them
    as validated metric side effects that participate in declared objective
    normalization and `selection_score`.
  - Remaining README gap: Pareto/frontier archive replacement and
    lineage-aware resurfacing remain open.
  - Verification: docs were updated alongside focused loader/loop tests for
    plugin-sourced objective metrics.

- [x] Refresh or de-emphasize time-sensitive provider model examples.
  - Status: README, configuration, development, and AGENTS quick-run examples
    now use clearly marked provider/account placeholders instead of stale
    concrete model IDs. Configuration docs still show the actual code default
    backend, but explicitly label it as a code default rather than a live
    provider availability guarantee.
  - Remaining documentation scope: `Config.backends` still defaults to the
    current Anthropic model string and should be revisited separately if the
    project wants a placeholder-only default or live provider catalog lookup.
  - Verification: docs search confirms the old concrete example IDs are gone
    from README/configuration/development/AGENTS examples except where used as
    code defaults or validation fixtures.

- [x] Correct optional-review wording for critique versus feedback behavior.
  - Status: README feature-table and step-by-step wording now distinguish
    critique as the pre-evaluation mutation-revision path from post-evaluation
    feedback graders that add metrics, adjust fitness/reward evidence, or
    discard candidates.
  - Remaining documentation scope: richer critique reviewer pools and feedback
    aggregation policy remain open in the code backlog.
  - Verification: focused loop and feedback tests cover critique revision
    selection, selected proposal provenance, invalid revision fallback,
    feedback metric addition, weighted score adjustment, objective-metric fill,
    and feedback discard.

- [x] Update architecture evaluator-output retention wording.
  - Status: architecture docs now say persisted validator stdout/stderr is
    decoded, secret-redacted, and capped by `evaluator_output_max_chars`, while
    prompt feedback remains compact and does not perform full/live artifact
    retrieval or global section packing.
  - Remaining documentation scope: richer validator metadata rendering,
    full/live artifact-content retrieval, and global prompt section packing
    remain open.
  - Verification: focused evaluator and prompt tests cover stdout/stderr
    truncation metadata, default caps, redaction-before-truncation, invalid
    UTF-8 diagnostics, artifact content excerpts, binary artifact status, and
    prompt rendering of copied UTF-8 artifact excerpts.

- [x] Update prompt-retention wording in run-artifact and architecture docs.
  - Status: architecture and run-artifact docs now distinguish configurable
    mutation-prompt retention from fixed bounded/redacted critique and feedback
    retention metadata.
  - Remaining documentation scope: prompt history, plugin/provider/retrieval
    and meta-prompt surfaces, quarantine streams, and role-configurable
    retention modes beyond mutation prompts remain open.
  - Verification: focused config, loop, and manifest tests cover
    `mutation_prompt_retention_mode`, generated-row `metadata.prompt_retention`,
    redacted/hash/off modes, bounded redacted critique metadata, and
    `policies.prompt_data_retention`.

- [x] Update archive snapshot restore wording in the README run-artifact claims.
  - Status: README and run-artifact docs now distinguish implemented archive
    cursor/counter restore and full MAP-Elites cell/elite restore from the
    remaining full-run replay gaps.
  - Remaining documentation scope: ordered migration-event replay,
    controller/pending-work resume, lineage replay, and provider/plugin output
    replay remain open elsewhere in the backlog.
  - Verification: focused archive restore tests cover cursor restore, full
    archive cell/elite restore from manifest/history bundles, CLI restore flags,
    mutually exclusive archive-restore flags, and direct loop restore.

- [x] Refresh the README CLI reference for implemented run options.
  - Status: README CLI Reference now lists the implemented run options that
    were previously omitted from that block: `--proposals-per-generation`,
    `--max-llm-calls`, `--llm-call-history-max`,
    `--llm-call-timeout-sec`, `--restore-llm-scheduler-from-manifest`, and
    `--restore-archive-from-manifest`.
  - Remaining documentation scope: full controller resume, ordered migration
    replay, provider-output replay, and plugin-output replay remain open in
    the run-resume backlog.
  - Verification: `py -3.12 -m libreevolve run --help` showed the current
    Click surface, and focused CLI/loop tests cover runtime budget overrides,
    LLM retry/history/timeout overrides, RNG restore, LLM scheduler restore,
    compact archive cursor restore, full archive-cell/elite restore from a
    manifest/history bundle, mutually exclusive archive-restore flags, proposal
    batch metadata, and logical LLM-call budget behavior.

- [x] Document consistent budget units for executed ablation curves.
  - Status: README now says `libreevolve.alphaevolve_ablation_report.v1`
    requires a consistent budget unit and limit across each seed's
    equal-budget fraction curve.
  - Remaining documentation scope: real ablation runners and live
    token/cost/accelerator budgets remain open.
  - Verification: focused ablation-result tests cover the underlying
    validation.

- [x] Document systems ready-gate artifact linkage.
  - Status: README now says `libreevolve.systems_result_report.v1` requires
    artifacts matching passed optimization, held-out, and
    reference-correctness gates.
  - Remaining documentation scope: real systems fixtures still need to emit
    these reports from actual held-out/reference checks.
  - Verification: focused systems-result tests cover missing gate artifacts.

- [x] Document certification evidence-artifact linkage.
  - Status: README now says `libreevolve.paper_result_certification.v1`
    requires artifact kinds matching passed evidence kinds for paper-claim-ready
    records.
  - Remaining documentation scope: real independent certifiers and
    deployment/reviewer evidence remain open.
  - Verification: focused certification tests cover the underlying linkage.

- [x] Document matrix-result per-seed consistency validation.
  - Status: README now says `libreevolve.matrix_result_report.v1` validates
    per-seed best-rank records and rejects reports whose top-level best rank or
    hit fraction does not match the per-seed records.
  - Remaining documentation scope: real tensor-decomposition targets and
    algorithm/certificate artifacts remain open.
  - Verification: focused matrix-result tests cover the underlying validation.

- [x] Document protected-signal links in benchmark hardening metadata.
  - Status: README now says `libreevolve.benchmark_hardening.v1` requires
    shortcut threats to link to the protected score/correctness/artifact signal
    they defend.
  - Remaining documentation scope: real benchmark fixtures still need to emit
    hardening reports from actual anti-gaming fixtures.
  - Verification: focused benchmark-hardening tests cover the linked-signal
    validation.

- [x] Document manifest-level prompt data-retention policy.
  - Status: README now documents `policies.prompt_data_retention` and explains
    configurable mutation-prompt retention, fixed redacted-bounded critique and
    feedback surfaces, hash/count-only LLM call text telemetry, and remaining
    plugin/context/provider-response retention gaps.
  - Remaining documentation scope: configurable per-role retention modes beyond
    mutation prompts remain open at the code level.
  - Verification: focused manifest tests cover the underlying policy record.

- [x] Document prompt section-budget accounting.
  - Status: README, configuration docs, architecture docs, run-artifact docs,
    and paper notes now describe `section_budget` prompt diagnostics and the
    boundary between deterministic character accounting and true token-aware
    packing.
  - Remaining documentation scope: provider-token section packing and
    context-policy evolution remain open.
  - Verification: focused prompt and loop tests cover the documented metadata.

- [x] Document per-role LLM scheduler-state accounting.
  - Status: README, run-artifact docs, architecture docs, and paper notes now
    describe `role_scheduler_state`, its aggregate `scheduler_totals`, and the
    boundary that global ensemble selection remains authoritative.
  - Remaining documentation scope: independent per-role routing/quotas and
    live scheduler-state resume remain open.
  - Verification: focused LLM ensemble and runtime manifest tests cover the
    documented fields.

- [x] Document archive-content snapshot and restore semantics.
  - Status: README, run-artifact docs, architecture docs, and paper notes now
    distinguish cursor-only restore from full cell/elite archive restore using
    `archive_contents`, `load_archive_restore_bundle()`, and
    `archive_programs_by_id`.
  - Remaining documentation scope: one-command CLI full resume and
    migration-event replay remain open.
  - Verification: focused population/database tests cover the documented
    archive-content restore path.

- [x] Document persisted mutation prompt retention metadata.
  - Status: README and run-artifact docs now describe `metadata.prompt` as the
    configured persisted mutation prompt and `metadata.prompt_retention` as
    the mode/policy plus raw rendered-prompt hash/count/redaction record when
    retained by policy.
  - Remaining documentation scope: configurable full/redacted/hash-only/off
    logging modes across critique, feedback, plugin/context, and
    provider-response surfaces remain open.
  - Verification: docs tests cover the updated documentation surfaces.

- [x] Document configurable mutation prompt retention modes.
  - Status: README, configuration, run-artifact docs, and paper notes now state
    that `mutation_prompt_retention_mode` supports `full`, `redacted`,
    `hash_only`, and `off` for generated-candidate history persistence.
  - Remaining README gap: per-role prompt/provider-response retention controls
    beyond generated mutation prompts remain open.
  - Verification: focused config and loop tests cover mode validation and
    history behavior.

- [x] Document plugin version attribution in plugin provenance.
  - Status: README, plugin docs, and run-artifact docs now state that runtime
    plugin identities and prompt-context records include sanitized version
    metadata from plugin instance, class, or module `__version__` attributes
    when present.
  - Remaining README gap: custom plugin constructor schema and package-registry
    provenance beyond exposed version labels remain open.
  - Verification: focused provenance and loop tests cover version capture,
    redaction, and prompt-context/runtime propagation.

- [x] Document bounded pip configuration provenance.
  - Status: README, run-artifact docs, architecture docs, and TODO evidence now
    describe `runtime.environment.pip_config` as a bounded/redacted
    `python -m pip config list` hash/preview for private index/source
    configuration evidence.
  - Remaining documentation scope: private package-source interpretation,
    complete install options, accelerator budget/accounting metadata, and live
    provider service versions remain open gaps.
  - Verification: docs tests cover the updated documentation surfaces.

- [x] Document archive cursor restore entrypoints.
  - Status: README, run-artifact docs, architecture docs, and configuration
    docs now describe direct `runtime_archive_state_snapshot` and
    `--restore-archive-cursor-from-manifest` as cursor/counter-only restore
    paths.
  - Remaining documentation scope: full MAP-Elites cell/elite restoration,
    controller resume, and migration replay remain documented as open gaps.
  - Verification: docs tests cover the updated documentation surfaces.

- [x] Document runtime LLM accounting summaries.
  - Status: README, backend docs, configuration docs, run-artifact docs, and
    paper index notes now describe `runtime.llm_accounting` as a compact
    audit-only summary of role-accounting counters, totals, and active
    LLM-related limits.
  - Remaining documentation scope: token/cost/provider-attempt stop policy,
    role-specific quotas, and resumable budget consumption remain documented as
    open gaps.
  - Verification: docs tests cover the updated documentation surfaces.

- [x] Document provider status-code telemetry for failed LLM calls.
  - Status: README, backend docs, architecture docs, run-artifact docs, and
    paper index notes now describe nullable `provider_status_code` on failed
    SDK exceptions that expose safe HTTP-style status codes.
  - Remaining documentation scope: raw provider diagnostics, provider costs,
    quarantine/penalty policy, and budget-stop decisions are still documented
    as open gaps.
  - Verification: focused ensemble tests cover the documented field.

- [x] Document role-level provider-failure category summaries.
  - Status: README, backend docs, architecture docs, run-artifact docs, and
    paper index notes now state that role accounting aggregates normalized
    provider-failure categories by call role.
  - Remaining documentation scope: quarantine, provider penalties,
    budget-stop policy, and resumed failure-policy state are still documented
    as open gaps.
  - Verification: focused ensemble tests cover the documented counters.

- [x] Document LLM role-accounting summaries.
  - Status: README, backend docs, architecture docs, run-artifact docs, and
    paper index notes now state that scheduler snapshots and ledger replay
    expose per-role call, success, failure, reward-accounted,
    telemetry-only, retry/fallback, and adapter-internal provider-attempt
    counters plus provider-reported token totals and provider-failure category
    counts.
  - Remaining documentation scope: role-specific reward policy, quotas,
    provider-cost accounting, token-budget stop policy, and automatic
    scheduler-state resume are still documented as open gaps.
  - Verification: focused ensemble tests cover the behavior documented here.

- [x] Document built-in backend provider request timeout configuration.
  - Status: README now states that OpenAI, Anthropic, and Ollama backend specs
    accept positive `timeout_sec`, that the value is forwarded to provider
    client construction, and that hard provider cancellation remains separate
    from local wait deadlines.
  - Verification: focused config/backend/ensemble tests cover timeout
    validation and forwarding.

- [x] Document dotenv import-time override behavior.
  - README/config evidence: README and configuration docs said the CLI loads
    `.env` with `override=True` for provider clients, but did not warn that this
    happens when `libreevolve.cli` is imported rather than only when `run` needs
    providers.
  - Status: documented. README, backend docs, development docs, and
    configuration docs now say importing `libreevolve.cli` loads `.env`
    immediately with `override=True`, so `.env` values take precedence over
    same-named parent environment variables for CLI commands including `show`
    and for programmatic imports.
  - Remaining implementation gap: moving dotenv loading out of CLI import side
    effects remains tracked in code, roadmap, and paper TODOs.

- [x] Document multiline proposal metadata handling.
  - README-adjacent evidence: docs described optional `IDEA`, `RATIONALE`, and
    `HYPOTHESIS` sections as proposal metadata, which could imply wrapped
    rationale text is retained as metadata rather than becoming mutation
    payload.
  - Status: documented as a single-line policy. README, architecture, and
    run-artifact docs now say proposal metadata is a leading preamble of
    single-line fields; continuation lines are mutation payload, and diff/file/
    block responses reject those lines as unconsumed text before mutation
    application.
  - Verification: prompt tests cover the one-line instruction, and diff tests
    cover wrapped proposal continuation text being treated as payload plus
    rejected before a SEARCH/REPLACE envelope.

- [x] Document proposal-marker stripping limits for full-file replacements.
  - README-adjacent evidence: docs describe optional `IDEA`, `RATIONALE`, and
    `HYPOTHESIS` sections as metadata outside the patch, and full-file/full-
    block modes as returning replacement candidate content.
  - Status: fixed and documented. Proposal metadata extraction/stripping now
    treats only the leading contiguous preamble as metadata, and docs say
    marker-like proposal lines after the first payload line are preserved as
    candidate content.
  - Verification: diff tests cover marker literals after payload start, and loop
    tests cover a full-mode replacement preserving a triple-quoted `IDEA:`
    literal in candidate code.

- [x] Clarify proposal metadata semantics when critique revises mutations.
  - README-adjacent evidence: docs described optional proposal
    idea/rationale/hypothesis sections as stored under `metadata.proposal` and
    rendered for future parent/inspiration programs, but critique revision could
    previously make that metadata describe the rejected original mutation.
  - Status: fixed and documented. `metadata.proposal` is now extracted from the
    selected post-critique mutation, and `metadata.critique` records
    `original_proposal`, `revised_proposal`, and `proposal_source` when
    proposal capture is enabled.
  - Verification: loop tests cover differing original/revised critique
    proposals and assert that the selected candidate stores the revised
    proposal while retaining both provenance records.

- [x] Clarify README local-paper-cache table coverage.
  - README evidence: the README section is titled `Local Paper Cache (24)` and
    says LibreEvolve is informed by a local cache of 24 papers, while the
    visible tables under that heading list only the core system and foundational
    algorithm subset.
  - Status: corrected and guarded. README now states the visible paper tables
    are a curated subset and that `papers/README.md` is the complete
    implementation-status index for all 24 manifest rows. The paper-manifest
    validator now flags root README paper summaries that list only a subset of
    manifest ids without this curated-summary disclosure.
  - Verification: `tests/test_paper_manifest.py` covers accepted curated
    summaries and rejected incomplete unlabeled summaries; docs tests,
    paper-manifest validation, and full non-integration tests passed.

- [x] Clarify GigaEvo and CodeEvolve README roles as inspiration-only.
  - README evidence: the `Local Paper Cache (24)` core-system table formerly
    said GigaEvo provided `Open-source framework patterns` and CodeEvolve
    provided `Evolutionary coding agent design`, while the paper index already
    marked both as not implemented as described.
  - Status: corrected. The README table now labels both rows as inspiration
    only and names the missing GigaEvo Redis/async/insight/concurrency features
    plus the missing CodeEvolve crossover/refinement/orchestration/recombination
    mechanisms.
  - Verification: `tests/test_agents_docs.py`, `tests/test_paper_manifest.py`,
    and full non-integration tests passed after the documentation update.

- [x] Document or enforce ThetaEvolve export prompt/response field types.
  - README/plugin-doc evidence: the README and plugin docs describe the
    ThetaEvolve-inspired exporter as writing GRPO-style training examples,
    which implies text prompt/response rows rather than arbitrary JSON values.
  - Status: enforced and documented. `TTTRLPlugin.on_evaluated()` queues export
    examples only when both `metadata["prompt"]` and `metadata["diff"]` are
    non-empty strings. Malformed prompt/response metadata is skipped before
    queueing and counted in run-artifact metadata.
  - Verification: plugin tests cover list, dict, empty, whitespace, and valid
    text prompt/response metadata; README, plugin docs, and run-artifact docs
    describe the text-only export boundary and malformed-example counters.

- [x] Document or enforce ThetaEvolve export score/reward field types.
  - README/plugin-doc evidence: the exporter is described as writing
    GRPO-style training data with `raw_score`, clipped `reward`, and an
    explicit reward policy, which implies numeric reward fields.
  - Status: enforced and documented. Export scores must be finite non-boolean
    numbers, accepted `raw_score` and `reward` values are stored as floats, and
    malformed score values raise before a training example is queued while
    incrementing the `invalid_score` diagnostic counter.
  - Verification: plugin tests cover boolean, string, `None`, object,
    non-finite, negative, zero, and positive score paths; README, plugin docs,
    and run-artifact docs describe JSON-native float export fields.

- [x] Document pending ThetaEvolve export behavior at run completion.
  - README evidence: README says the ThetaEvolve-inspired export writes under
    the active run's `plugin_artifacts/ttt_rl/` directory and links export
    counts in the completed manifest, which can imply every queued example is
    durably exported by the time the run ends.
  - Status: implemented and documented. `run_artifacts_metadata()` flushes
    pending TTTRL examples before returning metadata, and exposes
    `finalization_policy: flush_pending_examples_before_artifact_metadata`.
    Completed manifests should not leave valid exportable examples only in
    memory.
  - Verification: plugin tests cover metadata-triggered final flush, and loop
    tests cover a short run whose final generation is not a `train_every`
    multiple.

- [x] Document invalid ThetaEvolve export-record behavior.
  - README evidence: README describes the `ttt_rl` plugin as writing
    GRPO-style training data under run artifacts with manifest-linked counts,
    but did not explain what happens when one queued example is invalid.
  - Status: implemented and documented. Invalid prompt/response metadata is
    skipped before queueing, invalid scores raise before queueing, and valid
    later examples remain exportable because malformed examples do not park the
    export cursor.
  - Verification: plugin tests cover invalid-score then valid-export behavior,
    and README/run-artifact docs describe the non-blocking queue policy.

- [x] Document or enforce direct TTTRL export path scope.
  - README/run-artifact evidence: README says CLI-loaded `ttt_rl` exports live
    under the active run's `plugin_artifacts/ttt_rl/` directory, which can imply
    plugin training data is always run-scoped.
  - Status: documented. CLI-loaded `ttt_rl` exports are run-scoped, while
    direct in-code `TTTRLPlugin(log_dir=...)` construction is explicitly
    user-managed and may point outside a run directory. Manifest `log_dir`,
    path, count, hash, and byte metadata are the provenance boundary for those
    external artifacts.
  - Verification: README, plugin docs, and run-artifact docs describe the
    split; existing CLI tests cover run-scoped built-in plugin wiring and
    plugin tests cover custom direct `log_dir` exports.

- [x] Document or enforce ThetaEvolve export payload redaction and budgets.
  - README/plugin-doc evidence: README and plugin docs present
    `grpo_data.jsonl` as a reusable training-data artifact, which can imply the
    exported prompt/response strings are safe to retain and inspect.
  - Status: enforced and documented. TTTRL prompt and response payloads pass
    through shared secret-pattern redaction and are capped by per-field and
    combined prompt/response character budgets before queueing.
  - Verification: README, plugin docs, and run-artifact docs state the
    redaction/budget policy and manifest counters; plugin tests cover prompt
    secrets, diff secrets, oversized fields, aggregate truncation, and clean
    payload accounting.

- [x] Document or fix mutable plugin snapshot API returns.
  - README/plugin evidence: README and plugin docs present retrieval provenance
    and training-data export as inspectable run facts. That implies returned
    metadata/training snapshots are safe to inspect without changing plugin
    state.
  - Status: fixed and documented. DeepResearch prompt-context metadata and
    TTTRL training-data accessors return defensive deep copies instead of
    nested aliases to live plugin state.
  - Verification: plugin tests mutate returned retrieval source dictionaries
    and returned training rows, then confirm fresh snapshots keep the original
    internal values; plugin docs state the snapshot contract.

- [x] Document plugin score-composition selection semantics.
  - README/plugin-doc evidence: plugin `on_evaluated()` hooks can modify final
    top-level fitness, but archive ranking uses a separate selection score.
  - Status: documented. README, plugin docs, and run-artifact docs now state
    that plugin-adjusted fitness affects threshold gating, logging, backend
    reward, and prompt reward, while MAP-Elites cell competition, elite
    ordering, and parent sampling use declared-metric `selection_score`
    computed before plugin hooks.
  - Verification: loop tests assert plugin score composition changes final
    fitness while `metadata.selection_score` and
    `archive_admission.selection_score` remain the declared-metric value.

- [x] Document ignored non-diff payload around SEARCH/REPLACE blocks or reject
  it.
  - README/problem-format evidence: SEARCH/REPLACE is the default mutation
    contract, so users need to know whether stray prose or partial malformed
    blocks are accepted.
  - Status: fixed and documented. Current diff parsing rejects non-whitespace
    text outside compact or canonical SEARCH/REPLACE blocks unless it is
    accepted proposal metadata, returning `malformed_diff:unconsumed_text`
    before applying edits.
  - Verification: diff tests cover leading prose around a valid diff block,
    malformed trailing diff text after a valid block, and allowed proposal
    metadata around valid diff blocks; README and problem-format docs state the
    strict boundary.

- [x] Document or fix context include-pattern match-count semantics.
  - README/problem-format evidence: context policy metadata is reproducibility
    evidence, so include-pattern counts must distinguish candidate matches from
    selected prompt context.
  - Status: fixed and documented. Include-pattern policy records now retain
    pre-filter `matches` and add post-filter `selected_matches`; README,
    problem-format, run-artifact, and architecture docs define both fields.
  - Verification: loader tests cover included, excluded, hidden, recursive,
    and unmatched include patterns with exact `selected_matches` values.

- [x] Document or report unsupported top-level seed files.
  - README/problem-format evidence: top-level `initial_programs/*.py` files and
    directories are seed entries, but other top-level files were undocumented.
  - Status: documented. README and problem-format docs now state that
    non-`.py` top-level files under `initial_programs/` are ignored unless
    placed inside a workspace seed directory.
  - Verification: docs grep confirms the unsupported top-level file boundary is
    documented; richer skipped-entry diagnostics remain tracked in code and
    roadmap todos.

- [x] Document or normalize hidden seed-directory handling.
  - README/problem-format evidence: seed hidden/cache policy must distinguish
    top-level seed entries from files inside visible workspace seeds.
  - Status: normalized and documented. Top-level `initial_programs/` entries
    whose names start with `.` or equal `__pycache__`, including hidden `.py`
    files and hidden/cache seed directories, are skipped before seed loading;
    visible seed workspaces still skip nested dot-prefixed and `__pycache__`
    components.
  - Verification: loader tests cover hidden top-level `.py` files, hidden seed
    directories, cache seed directories, and the no-seeds behavior when only
    hidden/cache seed directories are present.

- [x] Document or fix circle-packing exact-count validator bypass.
  - README/problem evidence: the circle-packing fixture promises exactly 26
    circles in the unit square.
  - Status: fixed. The validator now accepts only a plain list of 26 plain
    tuple/list circle triples, verifies the parsed count after iteration, and
    rejects subclass/protocol count tricks before scoring.
  - Verification: example tests include a spoofed `list` subclass that reports
    length 26 while yielding 100 circles and confirm it is invalid.

- [x] Document or fix matrix benchmark metric-bound saturation.
  - README/problem evidence: the matrix smoke fixture optimizes fewer counted
    scalar multiplications through `inverse_multiplications = 1.0 / count`.
  - Status: fixed and documented. The primary metric bounds now use
    `[0.0, 1.0]`, preserving ordering for one-through-many counted
    multiplications without clamping; README calls the fixture a 2x2 smoke
    benchmark rather than a tensor-rank benchmark.
  - Verification: example tests cover the seed and a 7-multiplication Strassen
    candidate, confirm the improved candidate has higher normalized fitness,
    and confirm neither result records metric-bound diagnostics.

- [x] Align quickstart run and inspection paths.
  - README evidence: the first "Run Your First Evolution" command runs
    `libreevolve/problems/examples/circle_packing`; run directories default to
    the loaded problem name unless `--run-name` is supplied.
  - Status: fixed. The adjacent "Inspect Results" command now points at
    `runs/circle_packing`, matching the first quickstart command.
  - Verification: focused docs grep confirms the quickstart run and inspection
    path now use the same run directory.

- [x] Document or fix direct `CascadeEvaluator` default-validator boundary.
  - README/evaluator evidence: validators are problem-package files and
    configured validators are constrained to problem-local Python files.
  - Status: enforced. Direct `CascadeEvaluator.evaluate()` now performs the
    same default-validator preflight before subprocess execution, including
    problem-local containment, file shape, and Python-file checks.
  - Verification: evaluator tests cover direct outside, missing, directory,
    non-Python, and symlink-to-outside default validator paths.

- [x] Document or enforce artifact-option validation at the evaluator API
  boundary.
  - README/config evidence: evaluator artifact count/byte limits are run
    settings, but direct `CascadeEvaluator` construction is also a library
    surface.
  - Status: enforced and documented. Direct `CascadeEvaluator` construction now
    validates top-level artifact include/exclude patterns, max-file/max-byte
    limits, and redaction flags using the same schema as config-loaded runs.
    README, configuration docs, and run-artifact docs state that boundary.
  - Verification: evaluator tests cover non-list patterns, empty or unsafe
    patterns, negative/non-integer/boolean limits, non-boolean redaction flags,
    normal artifact copy-out, and per-stage overrides.

- [x] Document or fix evaluator artifact glob directory semantics.
  - README/config evidence: evaluator artifact include/exclude settings are
    documented as glob patterns, so benchmark authors need predictable root,
    nested, and recursive behavior.
  - Status: implemented and documented. Artifact matching is now
    path-segment-aware over candidate-relative POSIX paths: `*.txt` matches
    root files, `nested/*.txt` matches one segment below `nested/`, and
    `**/*.txt` recursively matches root and nested files.
  - Verification: focused evaluator tests cover root-only, nested,
    recursive, include, and exclude artifact selector behavior.

- [x] Document or enforce direct `CascadeEvaluator.timeout_sec` validation.
  - README/evaluator evidence: evaluator timeouts are runtime safety controls,
    and direct evaluator construction is a library surface.
  - Status: enforced. Direct `CascadeEvaluator.timeout_sec` values now share
    the finite positive non-boolean validation policy used by config and stage
    timeout settings.
  - Verification: evaluator tests cover invalid direct values, NaN/infinity,
    and valid positive int/float values.

- [x] Document synthetic evaluator-failure metric-vector limits.
  - README/run-artifact evidence: history records carry structured evaluator
    metrics, which can imply every candidate row has a complete declared metric
    vector.
  - Status: documented. README, problem-format docs, and run-artifact docs now
    state that strict declared-metric validation applies to validator-returned
    JSON, while internal synthetic evaluator failures may include only the
    primary metric plus `is_valid` and must be interpreted through error/stage
    metadata until a full policy is implemented.

- [x] Document or fix raw diff-error reason persistence.
  - README/run-artifact evidence: docs describe failed candidate records and
    evaluator stage errors as structured diagnostics suitable for prompt
    feedback and run inspection.
  - Status: fixed and documented. Synthetic diff failures now persist
    `diff_error_v1` metadata; known parser/runtime mutation reasons stay
    canonical, unknown strings are stored as `unknown_diff_error` with
    bounded/redacted detail, and non-string direct evaluator inputs become
    `malformed_diff_error`.

- [x] Document or fix foreign run-directory enumeration failures.
  - README/run-artifact evidence: README and run-artifact docs say unknown
    files in an existing run directory are preserved and summarized with hashed
    names/types before the run proceeds or overwrite cleanup is applied.
  - Status: fixed and documented. Unreadable existing-run-directory listing now
    records a redacted `status: "unreadable"` /
    `policy: "preserved_unlisted"` manifest diagnostic; README and run-artifact
    docs describe the behavior.

- [x] Document or fix CausalPlugin non-text mutation metadata crashes.
  - README/plugin evidence: README and plugin docs say the causal plugin
    inspects `metadata["diff"]` through the shared diff parser to classify
    edit factors.
  - Status: fixed and documented. Non-text causal mutation evidence is counted
    as malformed and falls back to the default factor instead of crashing; README
    and plugin docs describe the missing/non-text evidence policy and manifest
    metadata counter.

- [x] Document or enforce manifest-safe ids at lower-level archive APIs.
  - README/search evidence: archive, island, migration, and MAP-Elites objects
    are described as live search state; candidate ids shown in archive events
    and histories should be safe, stable identifiers.
  - Status: enforced and documented. Raw MAP-Elites and island insertion now
    revalidate ids, parent ids, and lineage before live archive mutation; README
    and run-artifact docs state that lower-level archive insertion shares the
    manifest-safe identity contract.

- [x] Document or fix direct prompt-program add failures lacking invalid-log
  diagnostics.
  - README/meta-prompt evidence: prompt history and invalid prompt history are
    presented as run artifacts for prompt-program state and rejected prompt
    mutations.
  - Status: fixed and documented. Direct prompt add duplicate-id and
    unknown-parent failures now write bounded `prompt_reference_error` rows to
    `prompt_history_invalid.jsonl`; README and run-artifact docs describe the
    durable invalid-history behavior.

- [x] Document or fix duplicate accepted-history id quarantine behavior.
  - README/run-artifact evidence: README and run-artifact docs present
    `history_invalid.jsonl` as the diagnostic stream for rejected candidate
    history records.
  - Status: fixed and documented. Duplicate accepted program ids now write the
    rejected record to `history_invalid.jsonl` before `StrictJsonlError`; README
    and run-artifact docs document that accepted history and in-memory accepted
    program indexes remain unchanged.

- [x] Document or bound plugin in-memory retention for long runs.
  - README/plugin evidence: plugin docs describe causal guidance and
    ThetaEvolve-inspired training-data export as inspectable run behavior,
    which can imply retained plugin state is controlled and reproducible.
  - Status: implemented and documented. README, plugin docs, run-artifact docs,
    and the paper index now describe bounded causal history, bounded TTT
    retained examples, overflow export, retained/dropped/pending metadata, and
    the remaining lack of resumable RL checkpoints.

- [x] Document or fix local PDF stat/read failures in paper validation.
  - README/paper-cache evidence: README says `--require-local-pdfs` checks
    local PDF presence, byte counts, and digests for ignored cached PDFs.
  - Status: fixed and documented. Local PDF stat/read failures now produce
    structured row-attributed redacted issues, directory-shaped PDFs are
    reported as non-regular cache entries, and README plus
    `papers/README.md` document the behavior.

- [x] Document or fix required problem-file read/stat failures.
  - README/problem-format evidence: docs describe `task_description.txt`,
    `metrics.yaml`, and `validate.py` as regular problem-local setup files with
    path-aware validation.
  - Status: fixed and documented. Required problem-file read/stat failures now
    produce bounded redacted diagnostics, and README plus
    `docs/problem-format.md` document the policy.

- [x] Document or fix unreadable seed-file handling.
  - README/problem-format evidence: docs say loaded seed files are UTF-8 text
    and invalid encoding fails with path-aware diagnostics, which can imply
    seed read failures are similarly bounded.
  - Status: fixed and documented. Unreadable top-level and workspace seed files
    now fail problem loading with path-aware redacted diagnostics; README and
    `docs/problem-format.md` document the behavior.

- [x] Document or fix `initial_programs/` enumeration failures.
  - README/problem-format evidence: docs describe loaded seeds as
    problem-local starting population records with safe source provenance.
  - Status: fixed and documented. Unreadable `initial_programs/` roots now
    fail problem loading with a path-aware redacted diagnostic; missing roots
    continue to produce the generic no-seed setup error.

- [x] Document or fix context source `stat()` failures.
  - README/problem-format evidence: docs describe context byte limits and
    skipped diagnostics as part of deterministic context selection.
  - Status: fixed and documented. Context source stat failures now produce
    skipped `stat_error` diagnostics with null hash/byte fields and redacted
    error text; README and `docs/problem-format.md` describe that behavior.

- [x] Document or fix context directory-enumeration failures.
  - README/problem-format evidence: docs describe recursive `context/`
    selection as deterministic and backed by skipped diagnostics.
  - Status: fixed and documented. Unreadable context directories now produce
    skipped `directory_listing_error` diagnostics with redacted error text
    while readable sibling context remains available.

- [x] Document or fix unreadable selected context-source handling.
  - README/problem-format evidence: README and problem-format docs describe
    local context files as deterministic prompt sources with hashes, skipped
    diagnostics, and failed-extraction records.
  - Status: fixed and documented. Unreadable selected context sources now
    become skipped `read_error` diagnostics with redacted error text, and
    successful sibling sources remain selected.

- [x] Document or fix unreadable skipped context-source handling.
  - README/problem-format evidence: docs say unsupported, excluded,
    not-included, hidden, and over-budget context sources are represented as
    skipped diagnostics with bounded provenance.
  - Status: fixed and documented. Unreadable skipped sources preserve their
    original skip reason and record `read_status: read_error`, null hash/byte
    fields, and redacted error text.

- [x] Document or fix unreadable context manifest handling.
  - README/problem-format evidence: README and problem-format docs describe
    `context/context.yaml` as the manifest controlling deterministic local
    context selection and skipped diagnostics.
  - Status: fixed and documented. Unreadable context manifests now fail problem
    loading with a path-aware redacted diagnostic, and README plus
    `docs/problem-format.md` describe that boundary.

- [x] Document or fix directory-listing failures in tree provenance.
  - README/run-artifact evidence: README and run-artifact docs say
    source/problem tree read failures are recorded as skipped diagnostics,
    which can imply unreadable directories are handled the same way as
    unreadable files.
  - Status: fixed and documented. README, `docs/run-artifacts.md`, and
    `docs/architecture.md` now describe skipped
    `directory_listing_error` diagnostics with redacted error text while
    readable sibling subtrees remain hashable.

- [x] Document or fix failure repetition-key collisions.
  - README/run-artifact evidence: failure-history documentation describes
    repeated-failure accounting and `metadata.failure_record` mirrors, so the
    grouping key must not depend on bounded display snippets.
  - Status: fixed and documented. README and `docs/run-artifacts.md` now state
    that failure-history repetition counters use a persisted
    `failure_fingerprint` built from parent id, diff/evaluator error hashes,
    full mutation payload hash, changed files, and file-delta hash.

- [x] Document or fix unbounded context-entry/skipped-diagnostic counts.
  - README/context evidence: README describes resource-bounded local context
    ingestion with byte and PDF limits, source hashes, skipped diagnostics, and
    manifest provenance. That can imply the whole context tree is bounded, not
    only selected source bytes.
  - Status: fixed and documented. README, `docs/problem-format.md`, and
    `docs/run-artifacts.md` now describe `max_context_entries`,
    `max_context_depth`, `max_skipped_diagnostics`, and
    `max_context_provenance_chars`, including retained versus omitted skipped
    diagnostic counts and deterministic max-entry/max-depth diagnostics.

- [x] Document or fix unbounded LLM call-history retention.
  - README/backend evidence: README and backend docs describe normalized
    ensemble call telemetry with role, backend, API mode, hashes, latency,
    retry/fallback status, and scheduler counts, which can imply durable
    AlphaEvolve-style accounting for long backend runs.
  - Status: fixed and documented. `README.md`, `docs/backends.md`,
    `docs/configuration.md`, and `docs/run-artifacts.md` now state that
    `LLMEnsemble.call_history` is a bounded retained in-memory window governed
    by `llm_call_history_max` / `--llm-call-history-max`, defaulting to `500`,
    and that `call_history_retention` exposes retained, total, and dropped
    record counts.
  - Remaining gap: the docs also explicitly state that there is not yet a
    complete durable append-only per-call LLM telemetry artifact.

- [x] Document manifest metric-schema provenance accurately.
  - README/run-artifact evidence: README and run-artifact docs present
    manifests as reproducibility aids for effective run settings, while
    problem docs define implicit primary behavior when no metric has
    `primary: true`.
  - Status: implemented and documented. README, run-artifact docs, and problem
    format docs now state that `manifest.problem.objective_schema` records
    normalized metric names, directions, bounds, effective primary flags,
    `primary_metric`, `primary_bounds`, and `metric_count`.

- [x] Refresh `AGENTS.md` so agent-facing instructions match current code and
  docs.
  - Documentation evidence: `AGENTS.md` still stated the non-integration test
    command had `168 selected`, while current active validation selected 638
    tests and passed with `631 passed, 7 skipped, 2 deselected`;
    README/development docs no longer use a fixed selected count.
  - Current evidence: `AGENTS.md` described `runs/` as containing only
    `manifest.json`, `history.jsonl`, `prompt_history.jsonl`, and `best.py`,
    but current run artifacts also include failure/quarantine JSONL streams,
    `best_workspace/`, evaluator artifacts, plugin artifacts, and richer
    manifest runtime/provenance. It also described `loop.py` as owning
    `build_prompt`, while current prompt construction is centered on
    `PromptSampler` in `libreevolve/core/prompt.py` with a compatibility wrapper
    in `loop.py`. Its `VALID_THRESHOLD` sentence also omitted validity and
    finite-score archive-admission gates enforced by `ProgramDatabase.admit()`.
  - Required result: update stale counts, architecture shortcuts, and
    run-artifact summaries in `AGENTS.md`; keep it aligned with README,
    development, architecture, and run-artifact docs; and add a lightweight
    truthfulness check so future agent-facing instructions do not drift from
    code and tests.
  - Status: implemented and tested. `AGENTS.md` no longer pins a selected-test
    count, names `PromptSampler` as the prompt owner, lists current run
    artifact families, and scopes archive admission to valid finite programs
    through `ProgramDatabase.admit()`. `tests/test_agents_docs.py` prevents the
    stale selected-count and artifact/prompt-owner drift from returning.

- [x] Correct "Gemini only" in the AlphaEvolve column.
  - README evidence: `README.md:66` says AlphaEvolve uses "Gemini only."
  - Spec evidence: the AlphaEvolve paper says it is model-agnostic and shows a
    "Choice of existing or custom LLMs" in the task setup, while the published
    experiments use Gemini 2.0 Flash and Gemini 2.0 Pro.
  - Required result: change this to a precise statement such as "published
    experiments use Gemini Flash/Pro; system is described as model-agnostic."


- [x] Correct "Extensibility: None" for AlphaEvolve.
    `CandidateWorkspace(files={"main.py": 123})` also preserves the non-string
    `err=None`, changed only `main.py`, and silently dropped the extra diff and
    returned `err=None`, changed `x`, and ignored the rest of the response.
    `err=None`.
    `err=None` when `c` was mixed with a valid `a` section.
    `err=None` and stored the literal `<<<BLOCK core` / `>>>BLOCK` envelope
    returned `err=None` and changed the first line only. With two evolve blocks
    `PRIMARY helper.py` followed by `PRIMARY main.py` returned `err=None` and
    left the workspace unchanged; reversing the order returned `err=None` and
    `PRIMARY new.py` returned `err=None` and selected `new.py`; reversing the
    `a.py` and `z.py` and returned `err=None`, `primary_file == "a.py"`.
    and `PRIMARY` sections returned `err=None`, performed the topology
    `err=None` but inserted the entire replacement file inside the existing
    `build_extra_context()` returns `""` or `None`. The resulting candidate
    backends as returning mutation text into the ensemble, and README now
    Chat Completions mock with `message.content=None` returned `None`, and
    non-string content that fails later during mutation parsing or telemetry.
    stayed `None`; and zero-width or inverted `perf_bounds` constructed and
    numeric response scores, non-finite response scores, and string discard
    local proof with `TTTRLPlugin(train_every=0).on_generation_end(1, None)`
    and `DeepResearchPlugin(search_every=0).on_generation_start(1, None)`
    `history.jsonl`, and `best=None`, while still creating
    rejects non-string or blank `name` / `validate_path` fields and non-JSON

- [x] Qualify "Population model: Proprietary database."
    database with LibreEvolve's MAP-Elites and islands.
  - Spec evidence: the paper states AlphaEvolve's database is inspired by
  - Required result: say AlphaEvolve has a closed evolutionary database inspired
  - Current evidence: `papers/download_manifest.csv` has 24 downloaded entries
    curated 23-paper list, then update badges/text/manifest accordingly.
    PDFs and a manifest.
    includes a local paper cache/manifest.
  - Current evidence: `papers/download_manifest.csv` lists 24 downloads,
    `papers/README.md`, `papers/download_manifest.csv`, and
    `papers/download_manifest.json`. The local working tree has the 24 PDFs,
    but a fresh checkout receives only the manifests and paper index. No
    files and that the committed repository tracks manifests/indexes; track a
    manifests and points to `papers/README.md` for implementation status.

- [x] Qualify "Evaluation: Internal infrastructure" versus "Cascade evaluator."
    proving invalid direct or resumed reward state is rejected.
    metadata-aware strategy.
    backends and metadata depths `1` and `100` selected the high-depth backend
    metadata priors can dominate before every backend has been sampled.
    mutation, critique, feedback, or meta-prompt provider exceptions.
  - README evidence: README and `docs/run-artifacts.md` describe
    meta-prompt provider call can exceed `max_runtime_seconds` before the loop
    can stop or write a timeout-specific artifact.
    or update README/backends/run-artifact docs so users understand that the
    ImprovEvolve is a static prompt block, and ThetaEvolve writes JSONL without
    enforces that static set for every OpenAI model.
    a conservative static subset and does not verify provider capability until

- [x] Fix the references count.
  - README evidence: badges and text claim 23 references
    (`README.md:15`, `README.md:72`, `README.md:356`, `README.md:360`).
  - Current evidence: `papers/download_manifest.csv` has 24 downloaded entries
    excluding the header.
  - Required result: decide whether the source of truth is 24 local papers or a
    curated 23-paper list, then update badges/text/manifest accordingly.


- [x] Remove or revise "does not bundle them."
  - Required result: remove the hard-coded "current latest" claim or replace it
  - Current evidence: `strip_proposal_metadata()` removes marker-looking lines
    parent placeholders, so evolved prompts cannot silently remove existing
    parent program/workspace and no SEARCH/REPLACE or full-mode mutation
    database, full-code mutation mode, and language/workspace runners.
  - Current evidence: lower-level `CandidateWorkspace` accepts an explicit
  - Status: implemented and documented. `CandidateWorkspace` now rejects
  - Current evidence: the CLI best exporter removes `best_workspace/` before
    writing, but the underlying `CandidateWorkspace.materialize()` API does not
  - Required result: either move preflight into the same constrained

- [x] Expand the research table or explain why most downloaded papers are not
  - Current evidence: `papers/download_manifest.csv` lists 24 downloads,
    `papers/README.md`, `papers/download_manifest.csv`, and
    `papers/download_manifest.json`. The local working tree has the 24 PDFs,
    download/rehydration command exists in the repo.
    download manifests as the evidence base for implementation-status and
  - Current evidence: `papers/download_manifest.csv` and
    `papers/download_manifest.json` record each paper id, title, URL, local
    document that the current download manifests are inventory records rather
  - Status: `papers/download_manifest.csv` and
    `papers/download_manifest.json` now include SHA-256 hashes for all 24 local
    the current API contract and add tests proving invalid direct or resumed
    behavior and future resume/replay paths from duplicating rewards.
    line was stripped from the mutation payload before application.
    `PromptDatabase.mutate()` accepted arbitrary template text without semantic
    minimal. A local proof used `PromptDatabase(tmp, templates=["Task only:
    `validate_prompt_template()` and `PromptDatabase` construction, then
  - Current evidence: `PromptDatabase` admits identical template text as
    parent has not yet recorded a successful use. `PromptDatabase._reject_mutation()`
    written to `prompt_history_invalid.jsonl` with parent id, generation,
  - Previous evidence: `PromptDatabase._reject_mutation()` wrote that record
    `StrictJsonlError`, wrote no `prompt_history_invalid.jsonl`, and still left
    fallback behavior and its limits for future resume/history replay.

- [x] Replace "parallel populations" wording for islands.
  - README evidence: `README.md` described 5-island migration as "Parallel
    populations."
  - Current evidence: `IslandModel` keeps multiple MAP-Elites archives but runs
    synchronously in-process; no population worker concurrency exists.
  - Status: README now says "synchronous island archives" instead of implying
    parallel execution.
  - Required result: avoid using "parallel" for islands until there are actual
    concurrent island workers.


- [x] Clarify migration disable semantics.
  - README/config evidence: population docs describe `migration_ratio` as a
    fraction rounded up to at least one migrant, while validation accepts
    `0.0`.
  - Current evidence: `IslandModel.migrate()` uses `max(1, ceil(...))`, so a
    local proof with `migration_ratio=0.0` still copied one elite. Only
    `migration_interval=0` disables migration.
  - Required result: tell users to use `migration_interval=0` to disable
    migration until zero-ratio behavior is redefined or rejected.


- [x] Soften UCB1/backend-routing claims.
  - README evidence: README called the ensemble "UCB1" and said it
  - Current evidence: `LLMEnsemble` is a UCB-style heuristic over unnormalized
    fitness improvements, with known canonical-UCB gaps tracked in
    `docs/todo/papers.md`.
  - Status: README now uses "UCB-style" in the feature list, workflow text, and
    implementation unless canonical UCB1 is implemented and tested.
  - README/backend-doc evidence: README and backend docs describe UCB-style
    the current API contract and add tests proving invalid direct or resumed
    UCB-style heuristic and note that default initial exploration is driven by
  - README evidence: README and `docs/run-artifacts.md` describe
    can stop or write a timeout-specific artifact.
    or update README/backends/run-artifact docs so users understand that the
  - Spec evidence: the paper describes published experiments with Gemini
  - Status: README now says local model use is not discussed in the paper,
    when the paper only omits or does not discuss it.
  - README evidence: `README.md:298-302` names CausalEvolve, DeepEvolve,
    ImprovEvolve, and ThetaEvolve as built-in plugins.
    CausalEvolve is regex/UCB1 factor guidance, DeepEvolve is arXiv Atom search,
    ImprovEvolve is a static prompt block, and ThetaEvolve writes JSONL without
  - Required result: use names such as "CausalEvolve-inspired" and document
    what is missing from each paper.
    `docs/configuration.md`, and `docs/run-artifacts.md` describe optional
    prompt database.
    prompt-program database for selection, scoring, lineage, and optional
    metrics, evaluator result objects, async controller/workers, meta-prompt
    database, full-code mutation mode, and language/workspace runners.

- [x] Clarify LLM provider failure handling is not production-grade.
  - README evidence: README described OpenAI/Anthropic/Ollama support and
    backend routing, but did not warn that provider call failures are not
    retried, routed to fallback models, or recorded as structured failed
    attempts.
  - Current evidence: ensemble-level retry/fallback and failed-call telemetry
    now exist, and non-mutation LLM roles are telemetry-only by default.
    Remaining failure-isolation gaps are outside that accounting slice:
    `evolve()` still does not isolate exhausted mutation, critique, feedback,
    or meta-prompt provider exceptions into role-specific quarantine records.
  - Required result: warn readers that backend failure isolation, role-specific
    quarantine, and failed-call scheduler accounting remain open beyond the
    current ensemble retry/fallback telemetry.


- [x] Correct the AlphaEvolve local-model comparison row.
  - README evidence: the comparison table said AlphaEvolve local models:
  - Required result: avoid inventing a negative AlphaEvolve capability claim
  - README evidence: `README.md:298-302` names CausalEvolve, DeepEvolve,
    ImprovEvolve, and ThetaEvolve as built-in plugins.
    CausalEvolve is regex/UCB1 factor guidance, DeepEvolve is arXiv Atom search,
    ImprovEvolve is a static prompt block, and ThetaEvolve writes JSONL without
  - Required result: use names such as "CausalEvolve-inspired" and document
    AlphaEvolve features are still absent or represented only as narrow
  - Required result: remove the hard-coded "current latest" claim or replace it
    update README/config/backends docs to say LibreEvolve intentionally exposes
    LibreEvolve uses a static `low`/`medium`/`high`/`xhigh` validator and does
  - Current evidence: `strip_proposal_metadata()` removes marker-looking lines
    parent placeholders, so evolved prompts cannot silently remove existing
    parent program/workspace and no SEARCH/REPLACE or full-mode mutation
    mutation instructions unless the user opts into a stricter AlphaEvolve-like

- [x] Qualify "Feed it a problem, a seed program, and any LLM."
  - README evidence: `README.md:258-285` describes `validate.py`, seed files,
    and optional seed workspaces.
  - README/problem-format evidence: docs explain that workspace seeds choose
    `main.py`, `seed.py`, or the first `.py` file as the primary file, and
    `cand_root` before reading them. On platforms where symlinks are available,
    `Path.is_file()` and `read_bytes()` can follow symlink targets. The local
    Windows account could not create the proof symlink (`WinError 1314`), but
    the static code path lacks a symlink/path-escape guard and lacks skip
    seed workspaces but did not mention that `<<<FILE ... >>>FILE` parsing is

- [x] Qualify the plugin names as inspired approximations, not implementations
  - Required result: use names such as "CausalEvolve-inspired" and document
    `metadata.proposal` and rendered for future parent/inspiration programs.
    but does not guarantee evolved prompts retain code, feedback, inspiration,
    code, feedback, inspiration, or mutation-format channels. Configured seed
    that configured seeds may omit parent code, feedback, inspirations, and
    metrics, evaluator result objects, async controller/workers, meta-prompt
    create `task_description.txt`, `metrics.yaml`, `validate.py`, and
    tests cover malformed metrics, missing validators, empty task files, and no
  - README evidence: README says raw metrics and diagnostics are stored with
  - Required result: describe UCB1 as inspiration for backend routing, not as a
    `metadata.archive_admission` and `failure_history.jsonl` as durable views
    `archive_admission`, but generated failure rows do not. A local proof with
    `archive_admission.reason == "invalid_evaluation"` while the matching
    `archive_admission`.

- [x] Qualify "comprehensive test coverage."
  - README evidence: `README.md:59` claims comprehensive coverage across all
  - Current evidence: the local non-integration suite currently has 431 passed,
    `py -3.12 -m pytest tests/ -m "not integration" --tb=short`, but major
  - Required result: keep the count but change the coverage claim to the
  - README evidence: `README.md:327-331` uses `pytest`.
  - Project instructions: `AGENTS.md` says to use `py -3.12 -m pytest`.
    documentation now uses `py -3.12 -m pytest`.
  - Required result: document installation first and use `py -3.12 -m pytest`.
    codebase and can evaluate complex workflows.
    are shown in prompts, and the workflow section said failed mutations are
    commands while repository instructions and the main README use `py -3.12`.
  - Current evidence: this Windows workspace uses `py -3.12` for tests and CLI
  - Required result: use `py -3.12 -m libreevolve show ...` in curated example
  - README evidence: the workflow says the LLM proposes either a SEARCH/REPLACE
    warning, or are surfaced through a quarantine/repair workflow; state the
    `py -3.12 -m libreevolve run --help` shows them.
    isolation, and the current local non-integration gate passed once with

- [x] Correct test commands for this machine.
  - README evidence: `README.md:327-331` uses `pytest`.
  - Project instructions: `AGENTS.md` says to use `py -3.12 -m pytest`.
    documentation now uses `py -3.12 -m pytest`.
  - Required result: document installation first and use `py -3.12 -m pytest`.
  - Required result: state that Responses is selected by the current
    final mutation. A local fake-backend proof selected a revised critique
  - Required result: either extract proposal metadata from the selected
    prompt programs as selected, scored, logged, and optionally mutated, and
  - README/config evidence: prompt programs are described as selected, scored,
    `Broken {unknown}` from a seed prompt and then selected that same prompt
    control-character examples in path-safety tests/docs; until then, avoid
    selected candidate.
  - Current evidence: the loader reads and hashes/extracts the full selected
    with empty `context_files` and `selected_count: 0`; when the context
  - Current evidence: `manifest.json` persists only selected
    that current context provenance covers selected sources only until context
    run-artifact docs, and architecture docs now describe selected context
    include/exclude/max-char rules, selected/skipped counts, and hashed
    `primary: "false"` and selected that metric as `Problem.primary_metric`;
    selected `helper.py`. The final primary file is therefore controlled by
    and add tests/examples so README and problem-format path claims are not
    parent-aware baseline metadata when available, not only consecutive
    observation order
    arXiv/web-search context, which can imply retrieved papers are selected
    that it always injects the same block and does not log a selected
    with depths `1.0` and `1_000_000.0` selected the huge-depth backend five
    database selected a different UUID seed prompt with zero usage and appended
  - README/run-artifact evidence: README presents prompt programs as selected,
    "Improve this LibreEvolve prompt template" instruction plus the selected
    histories, prints the selection mode, and prints selected metrics when
    graders are selected once from the initial evaluator validity; if an
    files and basic secret redaction for selected validator and feedback paths,
  - Current evidence: `tests/test_examples.py` checks seed validity and simple
    `tests/test_cli.py::test_run_budget_cli_options_override_config` proves
    isolation, and the current local non-integration gate passed once with
    `566 passed, 6 skipped, 2 deselected`; users still should not read current
    contributors to run pre-commit plus non-integration pytest before
    non-integration pytest) and a manual paper-index/hash verification

- [x] Qualify model names as examples, not guaranteed current model IDs.
    not validate availability. README and configuration examples now avoid
  - Required result: say model names are examples and add validation or docs for
  - Current evidence: a 2026-05-25 check of the official OpenAI model docs at
    guidance instead of `gpt-5.5`; a 2026-05-26 re-check of
  - Current evidence: official OpenAI API docs checked on 2026-05-25 list
    config examples or hidden project files.
    implying full artifact-content retrieval or global prompt packing.
  - README-adjacent evidence: `examples/runs/README.md` used `python -m`
    examples.
  - Current evidence: `examples/runs/hello_world_ensemble/history.jsonl`
    the `.format()` or concatenation examples. `examples/runs/sorting_ttt_rl`
  - Current evidence: `libreevolve/problems/examples/` contains
    `hello_world`, `sorting`, `circle_packing`, `matrix_multiplication`, and
    control-character examples in path-safety tests/docs; until then, avoid
    than semantically ranked or summarized, and that prompt-visible PDF page
    ranking, and no global prompt packing.
    policy, not semantic ranking, global prompt packing, or exact PDF
  - README/config evidence: README examples show `primary: true` as the way to
    limitation and avoid examples/text that imply string/integer values are
    and add tests/examples so README and problem-format path claims are not
    examples and tests should cover both one-block and multi-block workspace
    prompt/diff pair produced `pending_examples: 1`, `exported_examples: 0`,
    examples, or implement final flush/snapshot behavior before presenting the
    examples every `train_every` generations, and README describes
    saw no JSONL file plus `pending_examples: 1`; only
    repeated flushes, left both examples pending, and never exported the valid
    candidate code referenced matrix-rank work; the query did not include task,
  - README/backend-doc evidence: backend examples can include descriptive role
  - README evidence: README points readers to `examples/runs/*` immediately
  - README/docs evidence: examples and docs describe seed programs, run

- [x] Clarify OpenAI Responses API routing.
    models use Responses API broadly.
    `err=None`, changed only `main.py`, and silently dropped the extra diff and
    returned `err=None`, changed `x`, and ignored the rest of the response.
    `err=None`.
    `err=None` when `c` was mixed with a valid `a` section.
    `err=None` and stored the literal `<<<BLOCK core` / `>>>BLOCK` envelope
    returned `err=None` and changed the first line only. With two evolve blocks
    `PRIMARY helper.py` followed by `PRIMARY main.py` returned `err=None` and
    left the workspace unchanged; reversing the order returned `err=None` and
    `PRIMARY new.py` returned `err=None` and selected `new.py`; reversing the
    `a.py` and `z.py` and returned `err=None`, `primary_file == "a.py"`.
    and `PRIMARY` sections returned `err=None`, performed the topology
    `err=None` but inserted the entire replacement file inside the existing
    token usage, adapter-internal retry counts, response ids, finish reasons,
    OpenAI Responses mock with no message `output_text` returned an empty
    Chat Completions mock with `message.content=None` returned `None`, and
    empty provider response payloads are not yet consistently classified as
    The code-level provider response validation todo remains open.
  - Current evidence: `Config.seed` seeds local Python `random` choices and
  - Required result: tell readers that seeded local choices are controlled but
    database selected a different UUID seed prompt with zero usage and appended
    local proof with `TTTRLPlugin(train_every=0).on_generation_end(1, None)`
    and `DeepResearchPlugin(search_every=0).on_generation_start(1, None)`
    `history.jsonl`, and `best=None`, while still creating

- [x] Correct prompt-evolution placeholder guarantee wording.
    meta-prompt mutation as preserving placeholders.
  - Previous evidence: `evolve()` asked the LLM to keep placeholders but
    placeholder-retention validation.
    children must retain placeholders used by their parent prompt program.
    placeholder-validation todo is implemented.
    prompt programs as selected, scored, logged, and optionally mutated, and
    placeholder schema.
  - Required result: either implement semantic placeholder-retention rules
    first, or document that current validation prevents malformed placeholders
    checked against their parent prompt program and rejected if they drop
    parent placeholders, so evolved prompts cannot silently remove existing
    Architecture and configuration docs now state the parent-placeholder
    described as validated against the `PromptSampler` placeholder schema
  - Previous evidence: validation accepted known placeholder names even when their

- [x] Add missing AlphaEvolve gap callouts to the README architecture section.
  - README evidence: `README.md:225-254` presents the package architecture.
  - Missing from README: evolve-block markers, prompt sampler, multi-objective
  - README evidence: `README.md:258-285` describes `validate.py`, seed files,
  - README/problem-format evidence: docs explain that workspace seeds choose
    applies the same check. README, problem-format docs, and architecture docs
  - README/problem-format evidence: the custom-problem docs describe
    workspace directories before reading file contents. README,
  - README/problem-format evidence: docs describe seed directories as
    `main.py`, with no README-visible policy or run diagnostic.
  - README/problem-format evidence: seed directories are documented as
  - README/problem-format evidence: docs say seed directories prefer `main.py`,
    `initial_programs/text_only/README.md` and `data.txt` loaded `README.md` as
  - README/problem-format evidence: docs say seed workspaces are UTF-8 text
  - README/problem-format/run-artifact evidence: docs describe multi-file
  - README/problem-format evidence: docs present `task_description.txt` as the
    cover the invalid case. README and problem-format docs now state that the
  - README/problem-format evidence: custom problem docs present
    prompt rendering. README/problem-format docs do not state this
  - README/problem-format evidence: custom problem docs require
  - README/problem-format evidence: custom problem docs tell users how to
  - README/problem-format evidence: problem-format guidance says problem-load
    README directs users to `metrics.yaml` as part of the custom problem
    encoded `metrics.yaml` as path-aware setup diagnostics, or narrow README
  - README/problem-format evidence: README teaches users to define
  - README evidence: `README.md:61-72`.
  - README evidence: the problem-format section said validators run in an
  - Required result: call it a temporary local subprocess in README/AGENTS
  - README evidence: README says validators run in a temporary local
    environment plus `validator_env_allowlist` to `subprocess.run()`. README
  - Required result: keep README aligned with the implemented allowlist policy
  - README evidence: README says provider keys are hidden from validators by
    shapes before using broad README language, or narrow the README claim to
  - README evidence: README explains that validators run in a temporary local
    subprocess boundary as evaluation, or update README/problem-format/runtime
  - README/config evidence: README and configuration docs say the CLI loads
  - README evidence: README discussed validator subprocess execution and
  - Required result: keep README aligned with timeout cleanup while preserving
  - README evidence: README described the cascade evaluator's syntax filter
  - Status: README now says the pre-validator syntax check covers `.py` files
  - README evidence: README says raw metrics and diagnostics are stored with
  - Status: README now tells users that configured matching artifacts are
  - Required result: keep README aligned with configured artifact collection
  - README evidence: README says matching files written under the candidate
    `read_bytes()`, so README/config docs should not imply that it bounds
    document the current caveats plainly in README and run-artifact docs,
  - README/config evidence: README and configuration docs describe evaluator
  - README/config evidence: README and `docs/configuration.md` describe
    update README/config/run-artifact docs to state the current restricted
  - README/config evidence: README and configuration docs describe
    code and update README/config docs with examples, or document that
  - README evidence: the references table described UCB1 as "Multi-armed bandit
  - README evidence: the feature table claimed the last five failed mutations
  - Required result: keep README aligned with the implemented local failure
  - README/run-artifact evidence: README describes `failure_history.jsonl` as
    README/run-artifact docs to state that failure-history records are bounded
  - README/run-artifact evidence: README describes `history.jsonl`
    records first, or update README/run-artifact docs to state that generated
  - README-adjacent evidence: `examples/runs/README.md` used `python -m`
    commands while repository instructions and the main README use `py -3.12`.

- [x] Clarify that the current problem format is Python-only and local-workspace.
  - README/problem-format evidence: docs explain that workspace seeds choose
    applies the same check. README, problem-format docs, and architecture docs
  - README/problem-format evidence: the custom-problem docs describe
    `docs/problem-format.md`, and architecture docs state that seed files and
  - README/problem-format evidence: docs describe seed directories as
  - README/problem-format evidence: seed directories are documented as
  - README/problem-format evidence: docs say seed directories prefer `main.py`,
  - README/problem-format evidence: docs say seed workspaces are UTF-8 text
  - README/problem-format/run-artifact evidence: docs describe multi-file
  - README/problem-format evidence: docs present `task_description.txt` as the
    cover the invalid case. README and problem-format docs now state that the
  - README/problem-format evidence: custom problem docs present
    prompt rendering. README/problem-format docs do not state this
  - README/problem-format evidence: custom problem docs require
  - README/problem-format evidence: custom problem docs tell users how to

- [x] Rework the "Comparison to AlphaEvolve" section so it does not overstate
    deliberate divergences and many missing AlphaEvolve features.
  - Required result: keep README aligned with the implemented allowlist policy
  - Status: implemented and noted in configuration docs.
  - Required result: keep README aligned with the implemented local failure
  - Status: implemented and documented. README, problem-format, and
  - Status: implemented and documented. `CandidateWorkspace.from_dict()` now
  - Status: implemented and documented. README's custom-problem tree now shows
  - Status: implemented and documented. README, problem-format docs,
  - Status: implemented and documented. Non-PDF text/code context is now
  - Required result: once the reserved-field policy is implemented or chosen,
  - Status: implemented. The README `metrics.yaml` example no longer declares
  - Status: implemented in code and problem-format docs. `primary` is now
    README now says canonical AlphaEvolve fences are visible to factor
    or misclassify implemented plugin behavior.
  - Status: README now distinguishes implemented ensemble-level call telemetry
    values such as `breadth` and `depth`, which can be read as AlphaEvolve-like
    top-level config validation is implemented.
  - Status: implemented and documented in configuration, README, and
    symlinks/junctions is also implemented and tracked in the dedicated
    before presenting metric inspiration as AlphaEvolve-style multi-score
  - Status: implemented and documented. Seed rows are explicitly marked as
    provenance limitation rather than an implemented replay guarantee.
    no longer become grader scores under the strict feedback parser.
  - Status: implemented for configured stage names and documented in
    document the current ambiguity until explicit stage ids are implemented;
    adjacent docs say broad top-level config validation is now implemented.
  - Status: implemented with direct `Config` tests and a problem-local
  - Status: implemented with direct `Config` tests and configuration docs.
  - Status: implemented and documented for current built-ins. `TTTRLPlugin`
  - Status: implemented and documented. CLI startup validates plugin names
  - Status: implemented and documented. README, backend docs, and run-artifact
  - Required result: once implemented, document a seed-only/evaluate-only path
  - Status: implemented and documented. README and run-artifact docs now state
    `docs/todo/papers.md` still tracks AlphaEvolve-scale benchmark hardening.
    requirement for current history records is now implemented and tested.
  - Status: implemented behavior is fail-fast with normalized diagnostics;
  - Current evidence: strict JSONL write validation is implemented, but
    consistency work is implemented.
    which AlphaEvolve-style run-budget controls can override `config.yaml`.
  - Status: implemented. `_build_config()` now merges config-file values and
  - Status: implemented and documented. Runs that abort after startup manifest
  - Status: implemented and documented in run-artifact docs.
  - Status: implemented and documented. Run manifests now include
  - Status: implemented and documented. Source/problem provenance traversal now
  - Status: implemented. If seed evaluation leaves no archive-admitted parent,
  - Status: implemented and documented. Seed history rows are explicit raw
    validator subprocess safety as implemented behavior.
    submitting PRs, while the repository's AlphaEvolve-alignment truthfulness
    now depends heavily on README, ROADMAP, docs, paper index, and
    non-integration pytest) and a manual paper-index/hash verification
  - Status: implemented and documented. README now states bounds are
    presenting staged cascades as budget-faithful AlphaEvolve-style evaluation.
    which can be read as covering AlphaEvolve's program-output attachments.
    persisted-output caps and truncation metadata are implemented.
  - Status: implemented and documented in configuration/problem-format docs.
  - Status: implemented and documented. README/problem-format/run-artifacts

- [x] Replace "isolated subprocess" wording for validators.
    isolated subprocess.
    subprocess using the current Python interpreter and local filesystem
    access; this is process separation, not sandbox isolation.
    guidance and keep real sandbox/resource-limit work in `docs/todo/code.md`.
    secret-redacted, and validator network access is not sandboxed.
  - Required result: keep README aligned with the implemented allowlist policy
    and continue pointing network/sandbox limits to the TODOs.
    the caveat that this is not a container or general resource sandbox.
    and the remaining raw-content/no-outside-workspace limits.
  - Required result: keep README aligned with the implemented local failure
  - Required result: list the full current example set when documenting the
    policy remain incomplete.
  - Required result: keep README aligned with current path parser behavior
    applying partial edits. README now describes that current behavior while
    noting the parser is not a complete mutation AST.
  - Required result: keep README aligned with current diagnostics and keep
  - Current evidence: `apply_workspace_mutation()` supports command file
  - Required result: keep README aligned with current workspace topology
  - Required result: keep README aligned with the current score-composition
    README now says canonical AlphaEvolve fences are visible to factor
  - Required result: keep README aligned with the current parser behavior and
    continue distinguishing parser compatibility from paper-faithful causal
    completed manifests link export counts, path, bytes, hash, and quarantine
  - Status: README now distinguishes implemented ensemble-level call telemetry

- [x] Clarify validator subprocess environment policy.
    subprocess and must state what environment boundary applies.
    `CascadeEvaluator._run_subprocess()` now passes an explicit minimal
    environment plus `validator_env_allowlist` to `subprocess.run()`. README
    subprocess with a minimal allowlisted environment, stdout/stderr redaction,
    the main CLI process with `spec.loader.exec_module(module)`, so import-time
    evaluator subprocess timeout, output capture, or evaluation record.
    subprocess boundary as evaluation, or update README/problem-format/runtime
    outside the validator subprocess policy and should be avoided.
  - README evidence: README discussed validator subprocess execution and
  - Current evidence: `CascadeEvaluator._run_subprocess()` now launches a
  - Current evidence: `CascadeEvaluator._run_subprocess()` can now copy files
    `workspace_path`, but did not explain that the evaluator does not
    automatically run with that path as `cwd` or `sys.path`.
  - Current evidence: `CascadeEvaluator._run_subprocess()` now runs with the
    materialized candidate root as `cwd`, adds that root to `sys.path`, and
    passes it as `workspace_path`. README now states that candidate-local
    from a temporary runner rather than as a normal problem-local package.
    now adds `validate_path.parent` to `sys.path`, allowing sibling helper
    candidate root and the validator directory are added to `sys.path`, but
  - Current evidence: the runner inserts the validator directory and then the
    candidate workspace at the front of `sys.path`, making candidate modules
    showed such a program became both `db.best()` and an exploit-sampled
    `sample_diverse()`, island `explore`, or inspiration sampling. Current
    fitness `0.1`; `sample("recency")` returned the older high-scoring program.
  - Current evidence: `sample_diverse(strategy="metric")` chooses metric
    validators with `samples`, `retries`, `timeout_sec`, and `min_score`; the
    evaluation. Previously, `_run_stage()` cast stage numeric fields during
    evaluation; `samples <= 0` can reach aggregation with no sample results,
    `Config.validate()`. A local proof with `samples: 0` raised raw
    before `prepare_run_directory()`, config validation rejects empty plugin
  - Current evidence: `prepare_run_directory()` ignores names outside
    construction both call this guard before `prepare_run_directory()`.
    `tests/test_cli.py::test_run_budget_cli_options_override_config` proves
    validator subprocess safety as implemented behavior.
    validation, or state that subprocess timeout cleanup is best-effort process
    the evaluator as only Tier 0/1/2 or diff/syntax/subprocess filtering.
    thresholds, samples, seeds, retries, stage context, and artifact policy.

- [x] Clarify validator timeout process-tree behavior.
    timeouts and must state whether a timed-out validator's descendant
    killable process tree, timeout results record cleanup metadata, and tests
    prove a spawned child cannot write a marker after timeout.
  - Required result: keep README aligned with timeout cleanup while preserving
    `CandidateWorkspace(files={"main.py": 123})` also preserves the non-string
    token usage, adapter-internal retry counts, response ids, finish reasons,
    and retry/fallback routing from missing provider-level telemetry and
  - README/backend-doc evidence: provider docs describe OpenAI/Anthropic/Ollama
    describes retry/fallback telemetry at the ensemble boundary.
  - Current evidence: adapter response-shape validation is incomplete. A local
    OpenAI Responses mock with no message `output_text` returned an empty
    Chat Completions mock with `message.content=None` returned `None`, and
    first, or document that malformed/empty provider payloads are not yet
    empty provider response payloads are not yet consistently classified as
    non-string content that fails later during mutation parsing or telemetry.
    database selected a different UUID seed prompt with zero usage and appended
  - Required result: warn readers that richer retry/penalty/discard policy and
    validators with `samples`, `retries`, `timeout_sec`, and `min_score`; the
    OpenAI/Anthropic/Ollama backends and describe `--overwrite` as intentional
    docs now state that OpenAI/Anthropic credentials and backend construction
  - README/backend-doc evidence: docs now say OpenAI/Anthropic credentials and
  - README/run-artifact evidence: docs say OpenAI/Anthropic credentials and

- [x] Clarify aggregate workspace syntax diagnostics.
    and reports all Python syntax errors across the workspace with file, line,
    workspace into `evaluator_artifacts/` with hashes and provenance metadata.
    workspace.
    and the remaining raw-content/no-outside-workspace limits.
    workspace are copied to `evaluator_artifacts/` and that non-matching files
    are discarded with the temporary workspace.
  - Current evidence: this Windows workspace uses `py -3.12` for tests and CLI
    `workspace_math`.
    `workspace_math`.
    seed workspaces but did not mention that `<<<FILE ... >>>FILE` parsing is
    candidate workspace construction rejects raw paths that normalize to the
    while warning that Unicode normalization and topology-operation collision
    while still warning separately about path-collision handling and partial
    materialized as relative `new.py`. It also accepts control-character paths
    through the direct workspace API: a local proof constructed
    successfully, then `materialize()` failed with `OSError: [Errno 22]

- [x] Clarify validator-generated artifact retention.
  - README evidence: README says raw metrics and diagnostics are stored with
    each candidate and should explain the configured artifact copy-out path.
  - Current evidence: `CascadeEvaluator._run_subprocess()` can now copy files
    matching `evaluator_artifact_include` from the temporary candidate
    workspace into `evaluator_artifacts/` with hashes and provenance metadata.
  - Status: README now tells users that configured matching artifacts are
    retained, while non-matching files are discarded with the temporary
    workspace.
  - Required result: keep README aligned with configured artifact collection
    and the remaining raw-content/no-outside-workspace limits.


- [x] Soften the UCB1 paper-table role.
    `metadata.archive_admission` and `failure_history.jsonl` as durable views
    rejection metadata; keep seed/generated schema differences explicit.
    citation-style metadata, and first-span character truncation; the
    The citation metadata has a PDF-specific caveat: page ranges are recorded
    can be read as bounding the cost of context ingestion.
    excerpt was short, but context metadata still recorded `bytes=100000` and
    metadata, but prompt headers render only `pages=<start>-<end>`. A local
    manifest/source metadata carries the detailed spans.
    source hash/byte metadata still referred to the raw file.
    non-section payload outside recognized sections except proposal metadata
    in `metadata.score_composition`, and archive admission remains gated by
    `metadata.score_composition`, and that archive admission is validity-gated.
    final fitness `100.0` and added `plugin_quality`; the final metadata still
    metadata while archive ranking uses declared evaluator metrics, or
    recorded under `metadata.score_composition`.
    and metadata are not validated before history logging. A local proof plugin
    document that plugins must currently keep added metrics/metadata finite and
    `on_generation_start`, `build_extra_context`, `prompt_context_metadata`,
    `on_evaluated`, `run_artifacts_metadata`, and `on_generation_end` can raise
  - Current evidence: `PluginBase` also defines `prompt_context_metadata()`
    and `run_artifacts_metadata()`. These hooks are behaviorally significant:
    `prompt_context_metadata()`, and completed manifests include plugin
    artifact summaries returned by `run_artifacts_metadata()`.
    plugin hooks, distinguish lifecycle hooks from metadata/provenance hooks,
  - Status: README now describes lifecycle plus metadata/artifact hooks, and
    `docs/plugins.md` lists `prompt_context_metadata()` plus
    `run_artifacts_metadata()` with their call points and manifest/history
    roles.

- [x] Update the failure-history feature claim.
  - README evidence: the feature table claimed the last five failed mutations
  - Required result: keep README aligned with the implemented local failure
  - README evidence: the greeting example claimed `.format()` and string
    concatenation variants with score `1.00`, and the sorting example claimed a
  - Required result: list the full current example set when documenting the
  - Required result: keep README aligned with current path parser behavior
    applying partial edits. README now describes that current behavior while
    noting the parser is not a complete mutation AST.
  - Required result: keep README aligned with current diagnostics and keep
  - Current evidence: `apply_workspace_mutation()` supports command file
  - Required result: keep README aligned with current workspace topology
  - Required result: keep README aligned with the current score-composition
    README now says canonical AlphaEvolve fences are visible to factor
  - Required result: keep README aligned with the current parser behavior and
  - Required result: keep README aligned with the current workspace execution
    contract and track remaining sandbox/build-system gaps separately.
  - Required result: keep README aligned with current sibling-helper import
  - Required result: warn readers that current run history is not a replayable
    best output as a completed run.
    after describing current run inspection and then says to use
    history fixtures, not complete current run-artifact directories.
  - Required result: warn readers that current quality-diversity descriptors
  - Required result: keep README caveats aligned with current feedback-grader

- [x] Fix stale example-run command style.
    commands while repository instructions and the main README use `py -3.12`.
    `normalize_candidate_path()`, and README documents that nested paths,
    hyphens, spaces, Unicode filename characters, and Windows-style
    backslashes are accepted when normalized safely. README now also says
    candidate workspace construction rejects raw paths that normalize to the
    same relative path and materialization preflights case-folded host paths,
    while warning that Unicode normalization and topology-operation collision
    while still warning separately about path-collision handling and partial

- [x] Correct stale README example-run snippets.
  - README evidence: the greeting example claimed `.format()` and string
    concatenation variants with score `1.00`, and the sorting example claimed a
    valid `lst.sort()` candidate at generation 0 plus early `sorted`/copy
    variants.
  - Current evidence: `examples/runs/hello_world_ensemble/history.jsonl`
    contains the solved generation 0 greeting plus rejected variants, but not
    the `.format()` or concatenation examples. `examples/runs/sorting_ttt_rl`
    has a malformed `lst.sort()` edit at generation 0, valid `lst.sort()` at
    generation 1, and later valid `sorted`/copy variants.
  - Required result: align README snippets with the checked-in JSONL histories
    or explicitly mark them as illustrative rather than curated-output
    excerpts.


- [x] Refresh README/AGENTS example directory lists.
  - README evidence: the package tree listed example problems but omitted
  - README evidence: the custom-problem section describes optional multi-file
    `normalize_candidate_path()`, and README documents that nested pa…3806 tokens truncated…ograms enter the archive and describes
    the README's archive-admission wording for the public API, or document that
  - README evidence: README presents MAP-Elites as the archive of valid evolved
    broad README wording if MAP-Elites is treated as a safe archive API.
    document `MAPElites.add()` as an internal primitive and keep README archive
  - README evidence: README describes MAP-Elites bins and elite archive size as
  - README/run-artifact evidence: README presents archive admission and
  - README/run-artifact evidence: README describes `history.jsonl` and
  - README/run-artifact evidence: README says `show` streams `history.jsonl`
    history rows, or update README/run-artifact docs to say `show` performs
  - README evidence: README says `show` selects the best
    README/run-artifact wording does not explain that this admitted flag can
  - Required result: update README and run-artifact docs after the runtime
  - README evidence: README describes parent and inspiration strategies
    README/configuration/run-artifact docs to state that current recency is a
  - README/API evidence: README documents parent and inspiration sampling
  - README evidence: the inspect-results section prints "Best fitness" and
  - Status: README now calls `show` a compact history view, documents the
  - Required result: keep the README distinction until `show` is made
  - README evidence: README can now mention metric-aware parent/inspiration
  - README/config evidence: README says parent and inspiration sampling include
  - Required result: update README/configuration wording after the code policy
  - README evidence: README points readers to `examples/runs/*` immediately
  - README/run-artifact evidence: README describes `best.py` and
    files `Readme.md` and `README.md` raised during workspace materialization,
  - README/run-artifact evidence: run-artifact docs say program records in
    or update README/run-artifact docs to say prompt-program linkage applies to
  - README/run-artifact evidence: README and run-artifact docs now correctly
  - Required result: update README/run-artifact/problem-format docs after the
  - README evidence: README advertises workspace candidates and a MAP-Elites
  - README evidence: README describes MAP-Elites archive cells and descriptor
    or document in README/run-artifact docs that current MAP-Elites descriptor
  - README evidence: the feature list says feedback graders can add metrics or
  - Required result: keep README caveats aligned with current feedback-grader
  - README evidence: README states feedback graders receive bounded
  - README evidence: optional feedback graders are described as able to add
  - README/run-artifact evidence: docs describe structured evaluator results
    update README/run-artifact/config docs to state that current `stages`
  - Status: documented. README, run-artifact docs, and configuration docs now
  - README/run-artifact evidence: docs describe history records as carrying
    first, or update README/problem-format/run-artifact docs to state that
  - README evidence: optional feedback graders are described as recording
  - Status: documented. README and configuration docs now state that non-JSON
  - README/config evidence: optional feedback graders are described as able to
  - Status: documented. README and configuration docs now state that feedback
  - README/run-artifact/config evidence: `docs/run-artifacts.md` and
    and non-empty grader identifiers first, or update README/run-artifact/
  - Status: documented. README, configuration docs, and run-artifact docs now
  - README evidence: README described basic secret redaction for LLM feedback
  - Status: README now warns that mutation/critique prompt history is persisted
  - README/run-artifact evidence: docs say LLM feedback grader prompts apply
  - Status: README, configuration, and run-artifact docs now state that feedback
  - README/run-artifact evidence: docs describe failed-trial memory and
    unsafe/internal, or route it through bounded redaction before README and
  - README/run-artifact evidence: failed-trial memory is documented as bounded
  - README/run-artifact evidence: README says malformed LLM feedback responses
  - README/run-artifact evidence: README says feedback prompt inputs apply basic
  - README/run-artifact evidence: README describes invalid JSONL quarantine
  - Status: README and run-artifact docs now describe `*_invalid.jsonl`
  - README/run-artifact evidence: README says future mutation prompts receive
  - README evidence: the evaluation and configuration docs show staged
  - Required result: keep README/config docs aligned with startup validation
  - README/config evidence: docs now describe evaluator-stage numeric and
  - README/config evidence: README and configuration docs present configured
  - README/config evidence: docs describe stage `name` values as identifiers in
  - README/config evidence: README and configuration docs present stage names
    Keep README/config/run-artifact docs clear that stage `name` is not yet a
  - README-adjacent evidence: architecture and configuration docs still said
  - README/config evidence: configuration docs say malformed YAML and
    errors, and README presents config as part of reproducible run setup.
  - README/config evidence: `docs/configuration.md` documents
    limitation clearly in README/configuration docs.
  - README/config evidence: `docs/configuration.md` documents
    README/configuration docs to state that the field is currently only
  - README-adjacent evidence: architecture/configuration caveats implied
  - README/docs evidence: plugin docs describe `deep_research` running every
  - README/docs evidence: CLI docs now describe `--plugins`, `--overwrite`, and
    identifiers, and README/run-artifact docs state that unknown plugin aliases
  - README/plugin evidence: docs describe plugins as configured run components,
  - README/docs evidence: README and backend docs tell users to configure
  - Status: implemented and documented. README, backend docs, and run-artifact
  - README/backend-doc evidence: docs now say OpenAI/Anthropic credentials and
  - README/run-artifact evidence: docs say histories, manifests, prompt logs,
    validation before writing run artifacts, or update README/run-artifact docs
  - README/run-artifact evidence: README describes history metrics as
  - README/run-artifact evidence: docs now describe manifests as recording
  - README/run-artifact evidence: docs say OpenAI/Anthropic credentials and
    `evolve()`, or narrow README/run-artifact wording to the CLI and warn
  - README/run-artifact evidence: docs now state that seed-only runs skip
  - README/docs evidence: examples and docs describe seed programs, run
  - Status: implemented and documented. README and run-artifact docs now state

- [x] Clarify multi-file mutation path limitations.
  - README evidence: the custom-problem section describes optional multi-file
    seed workspaces but did not mention that `<<<FILE ... >>>FILE` parsing is
    narrower than ordinary repository path handling.
  - Current evidence: file-section headers now pass through
    `normalize_candidate_path()`, and README documents that nested paths,
    hyphens, spaces, Unicode filename characters, and Windows-style
    backslashes are accepted when normalized safely. README now also says
    candidate workspace construction rejects raw paths that normalize to the
    same relative path and materialization preflights case-folded host paths,
    and that duplicate file edit sections fail before partial application,
    while warning that Unicode normalization and topology-operation collision
    policy remain incomplete.
  - Required result: keep README aligned with current path parser behavior
    while still warning separately about path-collision handling and partial
    whole-envelope diagnostics.


- [x] Clarify malformed mutation envelope diagnostics.
  - Required result: keep README aligned with current diagnostics and keep
  - Required result: either implement whole-response rejection/diagnostics
  - Required result: either implement unknown-block rejection/diagnostics, or
    run until a stricter plugin metadata schema exists.
    and raw provider diagnostics remain unavailable.
    outcomes, prompt-history summaries, rejected mutation diagnostics, or
    are fully schema-validated.
    line-numbered diagnostics.
    workspace-aware and richer stage/lineage/archive diagnostics exist.
    The result is deterministic but not documented as schema order,
    notices, basic secret redaction, and compact evaluator diagnostics.
    full-workspace context and evaluator diagnostics, while earlier prompt
    graders do not see problem-local context files unless the evaluator output
    structured evaluator metrics and all declared evaluator outputs, which can
    code-level feedback metric-schema and non-empty-name validation todo
    which can imply diagnostic quarantine records are similarly redacted.
    quarantine files as unsanitized diagnostic snapshots that store
    evaluation stages as named cascade steps with structured diagnostics.
    as structured diagnostics users can inspect.
    before normalized startup diagnostics.
    files now fail cleanly, while plugin-specific schemas and provider/model
    before claiming broad config-schema enforcement, or document the current
    truthiness-coerced/rendered and not schema-enforced.

- [x] Clarify multi-file topology mutation syntax.
  - README evidence: the custom-problem section describes multi-file seed
    workspaces and file-section edits, so it should state how topology changes
  - Current evidence: `apply_workspace_mutation()` supports command file
  - Required result: keep README aligned with current workspace topology
    `mutation_mode: full` uses `<<<FILE ... >>>FILE` sections for multi-file
    file that contains evolve blocks. `apply_workspace_mutation()` sends the
    examples and tests should cover both one-block and multi-block workspace
    workspace whose primary file was `notes.txt` rendered the candidate in a
    prompt rendering preserves file type faithfully for every workspace shape.

- [x] Clarify full mutation mode prompt behavior.
  - README evidence: the workflow says the LLM proposes either a SEARCH/REPLACE
    diff or configured full-block/full-code replacement.
  - Current evidence: `PromptSampler.DEFAULT_TEMPLATE` now renders
    mode-specific instructions. In `full` mode the prompt asks for full
    replacement content, including full-file `<<<FILE ... >>>FILE` sections
    and named `<<<BLOCK ... >>>BLOCK` sections where applicable. Custom prompt
    variants can still render or ignore `{mutation_mode}` and
    `{mutation_instructions}`.
  - Required result: keep README wording aligned with the active default prompt
    behavior and avoid warning that full mode is diff-oriented.


- [x] Clarify plugin score provenance limitations.
    top-level fitness, that score provenance is stored in
    behavior and track broader plugin provenance separately.
    per-plugin score provenance and plugin artifact/provenance hooks, which can
  - Current evidence: score-composition entries and manifest plugin provenance
    two entries named `DeltaPlugin`, and manifest provenance recorded two
    score, context, artifact, and manifest records, or document that duplicate
    score and maintain internal state, and README says score provenance is
    extensions with hook methods, which can imply that the runtime rejects
    plugin provenance; with one generation it aborted after seed history and
    manifest startup because the object lacked `on_generation_start`.
    caller-provided plugin list and may record non-plugin objects until runtime
    runtime policy exists.
    `prompt_context_metadata()`, and completed manifests include plugin
    plugin hooks, distinguish lifecycle hooks from metadata/provenance hooks,
    `run_artifacts_metadata()` with their call points and manifest/history
  as run provenance.
    can imply those records are safe, typed run provenance.
    invalid plugin provenance can quarantine the candidate record and abort the
  - README/run-artifact evidence: README says completed manifests summarize
    plugin artifacts, which can imply the `runtime.plugin_artifacts` entries
    are trusted provenance for the emitting plugin.
  - Current evidence: `_plugin_artifact_manifest()` stores whatever dictionary
    "external.jsonl", "count": 1}`; the manifest's artifact entry used the
    spoofed `TrustedPlugin` name while `provenance.plugins` identified the real
    runtime object as `__main__.SpoofArtifactPlugin`.
  - Required result: either wrap artifact metadata with runtime-derived plugin
    a stricter manifest schema exists.
    global output path, or missing manifest linkage.
    completed manifests link export counts, path, bytes, hash, and quarantine
    user-managed external artifacts whose provenance must be inspected in the
    manifest.
    counts in the completed manifest, which can imply every queued example is
    GRPO-style training data under run artifacts with manifest-linked counts,

- [x] Clarify causal plugin mutation-format behavior.
  - README evidence: the plugin section labels the causal plugin as
    CausalEvolve-inspired, but did not state that its factor detector is not
    using the same canonical diff parser as candidate mutation application.
  - Current evidence: `CausalPlugin._detect_factors()` now uses
    `parse_diff_blocks()`, matching the core compact/canonical diff parser.
    README now says canonical AlphaEvolve fences are visible to factor
    guidance while the plugin remains a lightweight token-pattern heuristic,
    not CausalEvolve's causal scratchpad.
  - Required result: keep README aligned with the current parser behavior and
    continue distinguishing parser compatibility from paper-faithful causal
    reasoning.


- [x] Clarify ThetaEvolve export reward and artifact limitations.
    writes under the active run's `plugin_artifacts/ttt_rl/` directory and
    artifact until real training/checkpoint semantics exist.
  - README/run-artifact evidence: README says CLI-loaded `ttt_rl` exports live
    under the active run's `plugin_artifacts/ttt_rl/` directory, which can imply
    and exposed that outside path in `run_artifacts_metadata()`.
    user-managed external artifacts whose provenance must be inspected in the
    the active run's `plugin_artifacts/ttt_rl/` directory and links export
    export artifact as complete.
    GRPO-style training data under run artifacts with manifest-linked counts,
    persistence, or update README/plugin/run-artifact docs to warn that
    message. Include the effective policy in run-artifact/call-telemetry docs.
    before telemetry persistence, or update README/backend/run-artifact docs to
  - README/run-artifact evidence: `prompt_history.jsonl` is described alongside
    run artifacts and prompt-program scoring, which can imply it is sufficient
  - README/run-artifact evidence: README presents prompt programs as selected,
    run-artifact docs. Final resolved run-directory confinement under
  - README/run-artifact evidence: README treats `run_id` as durable manifest
  - README/run-artifact evidence: README describes history, lineage, parent
  - README/run-artifact evidence: README describes configuration validation and
    materialized candidate root as `cwd`, adds that root to `sys.path`, and
  - README/problem-format evidence: the docs now say both the materialized
  - README/run-artifact evidence: README describes synchronous island archives
    island's `elite_archive()`. This is not visible in run artifacts because
  - README/run-artifact evidence: README describes synchronous island archives
    and run artifacts with archive-admission events, which can imply island
  - README/run-artifact evidence: README describes valid programs entering the
  - README/run-artifact evidence: README presents archive admission and
  - README/run-artifact evidence: README describes `history.jsonl` and
  - README/run-artifact evidence: README says `show` streams `history.jsonl`
    history rows, or update README/run-artifact docs to say `show` performs
    README/run-artifact wording does not explain that this admitted flag can
  - Required result: update README and run-artifact docs after the runtime
    The run artifacts do not persist an insertion/admission sequence that would
    README/configuration/run-artifact docs to state that current recency is a
    `best.py`/`best_workspace/` from the original run for exact archived output
    `best_workspace/` from the original run for archived best output.
    `history.jsonl` and `best.py`; they do not include `manifest.json`,
    `prompt_history.jsonl`, `failure_history.jsonl`, or `best_workspace/`.
    history fixtures, not complete current run-artifact directories.

- [x] Clarify DeepEvolve retrieval provenance limitations.
  - Status: README, plugin docs, run-artifact docs, and the paper index now
    describe bounded retrieval metadata, request URL summaries, finite
    best-fitness handling, retention counters, direct arXiv parameter
    validation, HTTPS default transport, payload hash/status metadata, and
    run-local retrieval cache snapshots. They also state that ranked-source
    provenance, full provider-payload persistence, source-content trust policy,
    full run resume, and DeepEvolve-style debugging loops remain open.
  - README/run-artifact evidence: README treats `run_id` as durable manifest
    startup manifest stored that exact value under `config.run_id`.
    manifests as run controls, but library callers can pass a mutated `Config`
    `max_generations=-99` in `manifest.json`.
    manifest/database writes, or document that validation guarantees apply to
    and island migration, but did not distinguish runtime archive state from
  - Required result: update README and run-artifact docs after the runtime
    `history.jsonl` and `best.py`; they do not include `manifest.json`,
  - Required result: either add explicit seed/source provenance to history rows
    source provenance.
    provenance limitation rather than an implemented replay guarantee.
  - Required result: either redact/hash feedback responses before persistence
  - Required result: either redact/hash/truncate quarantined record snapshots
    bounded, redacted evaluator artifact paths and hashes, which implies
    caveat previously warned that bad numeric values could fail at runtime.
    plugin registry/config/provenance todo remains open.
  - Current evidence: a local direct-runtime proof used
    `evolve(problem, config)` without plugin instances. The manifest stored
    `config.plugins == ["causal"]`, but `provenance.plugins` was empty and no
    manifests cannot imply a plugin ran when it did not.
    was already gone and `manifest.json` existed.
  - README/run-artifact evidence: docs say histories, manifests, prompt logs,

- [x] Clarify ImprovEvolve guidance is static and only context-attributed.
  - README evidence: the plugin section labels `modular` as
    ImprovEvolve-inspired modular decomposition prompting, but does not state
    not choose or log a real ImprovEvolve generate/improve/perturb operation.
  - Required result: document that modular guidance is static prompt-only until
    real ImprovEvolve operations exist.
  - Current evidence: `Config.validate()` only checks `plugins` is a list of
    strings, while `_load_plugins()` resolves those names through the CLI's
    constructors except for the run-scoped `ttt_rl` artifact path.
  - README/docs evidence: plugin docs describe `deep_research` running every
    `search_every` generations and `ttt_rl` exporting every `train_every`
    `docs/plugins.md` states both cadence fields must be positive integers.
  - README/docs evidence: CLI docs now describe `--plugins`, `--overwrite`, and
    plugin names. A local proof with `--plugins missing --overwrite` failed
    `runtime.plugin_artifacts` and the `ttt_rl` export path, but the top-level
  - Current evidence: the CLI scopes `ttt_rl` to
    `runs/<run-name>/plugin_artifacts/ttt_rl/`, `TTTRLPlugin` writes
    plugins expose `run_artifacts_metadata()`. This can imply partial plugin

- [x] Clarify missing per-call backend telemetry.
  - README evidence: the backend section says the router tracks observed
    `LLMEnsemble` now wraps calls with role, backend, API mode, prompt/output
    size and hash, latency, status, and scheduler-count telemetry. Provider
    token usage, adapter-internal retry counts, response ids, finish reasons,
    and retry/fallback routing from missing provider-level telemetry and
    role-specific quarantine policy.
  - Required result: note that deeper provider telemetry remains backend
  - README/backend-doc evidence: provider docs describe OpenAI/Anthropic/Ollama
    backends as returning mutation text into the ensemble, and README now
    describes retry/fallback telemetry at the ensemble boundary.
    legacy fallback for checked-in fixtures, and tells users to use
  - Required result: warn readers that richer retry/penalty/discard policy and

- [x] Clarify seed/replay limits.
    which could imply full replay stability.
    are not captured as a deterministic replay boundary.
    replay-stable yet.
  - Required result: warn readers that current run history is not a replayable
    and are not a faithful persisted population snapshot.
    while distinguishing them from full archive snapshots.
  - Required result: either require exact boolean `True` before live archive
    admission and history replay, or document that current archive safety
    The result is deterministic but not documented as schema order,
    live in metadata.
    state that feedback grader outcomes live under
  - Required result: either redact/hash/truncate quarantined record snapshots
    quarantine files as unsanitized diagnostic snapshots that store
    mistake mixed directories for clean reproducible runs.
    outside the clean-run reproducibility contract. Manifest/runtime diagnostics
  - Required result: keep README's compact CLI reference aligned with live
    precedence text include all live budget overrides, or clearly distinguish
    s…427 tokens truncated… tracked under resumability/reproducibility.

- [x] Clarify workspace validator import/cwd behavior.
  - README evidence: the custom-problem section said validators can accept
    whether plugin configuration is validated before cleanup of an existing run
    directory.
  - Previous evidence: the CLI prepared the run directory before resolving
    plugin names. A local proof with `--plugins missing --overwrite` failed
    with `Unknown plugin: 'missing'` after the existing `history.jsonl` in that
    run directory had already been removed. `Config.validate()` also accepted
    empty and whitespace-padded plugin strings because it validates only the
    list element type.
  - Required result: document that plugin names/specs are preflighted before
    any overwrite cleanup so invalid plugin configuration cannot fail after
    provider credentials are checked before cleanup starts.
  - Previous evidence: backend clients were built inside `evolve()` after CLI
    run directory preparation. A local proof cleared `OPENAI_API_KEY`, supplied
    `--backends openai:gpt-4o-mini --overwrite --max-generations 0`, and the
    command failed after printing the run banner; the existing `history.jsonl`
    was already gone and `manifest.json` existed.
  - Required result: after implementation, document that backend credentials
  - README/run-artifact evidence: README and run-artifact docs say startup
    fails on known artifacts and `--overwrite` deletes known artifacts, but do
    not say what happens when the target run directory already contains
    unrelated files.
  - Current evidence: `prepare_run_directory()` ignores names outside
    `RUN_ARTIFACT_NAMES`. A local proof created `runs/probe/foreign.txt`,
    constructed a `ProgramDatabase` for `problem_name="probe"`, and observed
    both `foreign.txt` and a new `manifest.json` in the same run directory.
  - Required result: either fail on non-empty unknown run directories or
    document that unknown files are preserved and outside the run contract;
    if preserved, surface them in manifest/runtime diagnostics so users do not
    mistake mixed directories for clean reproducible runs.
  - Status: README, configuration, and run-artifact docs now state that
    unknown files in a run directory are preserved under both `fail` and
    `overwrite`, are not run-owned manifest artifacts, and put the directory
    outside the clean-run reproducibility contract. Manifest/runtime diagnostics
    for foreign files remain an implementation hardening gap in
    `docs/todo/code.md` and `docs/todo/roadmap.md`.
    distinguish this from `manifest.json` atomic replacement.


- [x] Clarify problem-local validator helper imports.
    passing validator stage.
    `feedback_adjusted_fitness` while the raw primary validator metric remains
    files and basic secret redaction for selected validator and feedback paths,
    validators with `samples`, `retries`, `timeout_sec`, and `min_score`; the
    evaluation; `samples <= 0` can reach aggregation with no sample results,
    and `retries < 0` can skip all attempts before an assertion.
    whether plugin configuration is validated before cleanup of an existing run
    forwards configured provider model IDs and does not validate provider
    validator rejection behavior; `matrix_multiplication` validates a small 2x2

- [x] Clarify that MAP-Elites archive state is not persisted.
  - README evidence: the feature list and flow describe a MAP-Elites archive
    and island migration, but did not distinguish runtime archive state from
    `MAPElites._grid`, elite lists, island assignment, descriptor values, and
    archive checkpoint or migration event log.
  - README/run-artifact evidence: README describes synchronous island archives
    and ring migration, which can imply each island archive contains distinct
  - Current evidence: repeated migration can add the same `Program.id` to an
    island's elite archive multiple times. A local proof with one program, two
    islands, and three migrations produced four copies of the same id in each
    island's `elite_archive()`. This is not visible in run artifacts because
    migration events and elite lists are not persisted.
  - Required result: either deduplicate migration state first, or document that
    the current in-memory island elite lists can contain duplicate migrated ids

- [x] Clarify candidate archive admission status.
  - README evidence: the flow says valid programs enter the MAP-Elites archive
    and all programs are logged, so it should say what admission status is
    visible per row.
  - Current evidence: `ProgramDatabase.admit()` now stores
    `metadata.archive_admission` before `history.jsonl` rows are written.
  - Required result: keep README aligned with per-candidate admission events
    while distinguishing them from full archive snapshots.


- [x] Clarify `show` archive-aware selection and remaining compact-view limits.
    "Best program" from `libreevolve show`, which can imply the same archived
  - Current evidence: `cli.show()` now checks
  - Status: README now calls `show` a compact history view, documents the
    `best.py`/`best_workspace/` from the original run for exact archived output
    after describing current run inspection and then says to use
    `best_workspace/` from the original run for archived best output.
    `history.jsonl` and `best.py`; they do not include `manifest.json`,
    `prompt_history.jsonl`, `failure_history.jsonl`, or `best_workspace/`.
    `best_workspace/` as the archived best output from a run, which implies the
    materializing `best_workspace/`. A local proof with host-colliding best
    left the new `best.py` on disk, and removed the prior `best_workspace/`.
    `history.jsonl` include `metadata.prompt_program_id` so candidates can be
    `metadata.prompt_program_id`; `prompt_history.jsonl` contained only the
    and `initial_programs/seed_b/` workspaces wrote two seed `history.jsonl`
    notices, basic secret redaction, and compact evaluator diagnostics.
    verbatim to `history.jsonl`.
    with `Unknown plugin: 'missing'` after the existing `history.jsonl` in that
    command failed after printing the run banner; the existing `history.jsonl`
    `libreevolve show` as the compact inspection path for current and legacy
    `history.jsonl` files.
  - Current evidence: `show` now streams `history.jsonl`, fails malformed JSON
    `history.jsonl`, `failure_history.jsonl`, `prompt_history.jsonl`, and
  - README/run-artifact evidence: README presents `history.jsonl` and
    `db.all_programs()` was empty, and no accepted `history.jsonl` existed.
    raised `StrictJsonlError`, wrote no `failure_history.jsonl`, but left the
    outside `history.jsonl` during overwrite startup.
    directories and that linked `best_workspace/`, `evaluator_artifacts/`, or
  - Required result: keep README's compact CLI reference aligned with live
    logging; `history.jsonl` existed, but `manifest.json` still contained only
    `history.jsonl`, but `manifest.json.runtime` contained only `consumed`,
    `history.jsonl`, and `best=None`, while still creating
    `prompt_history.jsonl` and `manifest.json`.
    `history.jsonl`, `run_collision_policy="overwrite"`, and
    `<tmp>/problem` included `runs/demo/history.jsonl` in the problem file
    mutation LLM. Rejected seeds are also recorded in `failure_history.jsonl`.
    valid programs` and wrote no `best.py` or `best_workspace/`.
    `history.jsonl` was replaced, a new manifest/history row was written with
    `run_collision_policy="overwrite"`, an existing `history.jsonl`, and a

- [x] Clarify checked-in example runs are legacy history fixtures.
    `best_workspace/` from the original run for archived best output.
    `history.jsonl` and `best.py`; they do not include `manifest.json`,
    `prompt_history.jsonl`, `failure_history.jsonl`, or `best_workspace/`.
    `best_workspace/` as the archived best output from a run, which implies the
    materializing `best_workspace/`. A local proof with host-colliding best
    left the new `best.py` on disk, and removed the prior `best_workspace/`.
    was already gone and `manifest.json` existed.
    OpenAI backend replaced existing history, wrote an aborted runtime manifest,
    fail/overwrite semantics but listed only the older history/prompt/manifest
    both `foreign.txt` and a new `manifest.json` in the same run directory.
    if preserved, surface them in manifest/runtime diagnostics so users do not
    `overwrite`, are not run-owned manifest artifacts, and put the directory
    `libreevolve show` as the compact inspection path for current and legacy
    `metadata.archive_admission.admitted is True` and `evaluation.is_valid is
    that differs from the separate `manifest.json` atomic-write guarantee.
    distinguish this from `manifest.json` atomic replacement.
    `metadata.archive_admission` as durable views of candidate evaluation and
    manifest writes. Tests cover direct outside-path rejection and
    scoped path plus manifest summaries.
    `py -3.12 -m libreevolve run --help` shows them.

- [x] Clarify MAP-Elites descriptors use the primary-file view for workspaces.
  - README evidence: README advertises workspace candidates and a MAP-Elites
    archive, but did not state that archive complexity/diversity descriptors
    rejected.
  - Current evidence: duplicate configured names are rejected, but names are
    prove a quoted YAML string such as `critique_enabled: "false"` is rejected
    have rejected the missing credential before cleanup.
    primary fitness, MAP-Elites performance normalization, and strict
    out-of-range validator outputs are rejected.
    are superseded by bounded structured program-output metadata.

- [x] Clarify feedback grader workspace scope.
    workspace sections with file paths, primary-file marking, truncation
    full-workspace context and evaluator diagnostics, while earlier prompt
  - Current evidence: feedback workspace rendering calls
    raw and can echo sensitive data even though the workspace prompt input is
    secret redaction, but that is only true for the workspace source section.
    document that feedback-grader prompt redaction currently covers workspace
    `prepare_run_directory()` calls `shutil.rmtree()` on known directory
    overwrite startup raised raw `OSError: Cannot call rmtree on a symbolic
    directories and that linked `best_workspace/`, `evaluator_artifacts/`, or
    prompt/failure histories, and workspace artifacts. That reads like a stable
    valid programs` and wrote no `best.py` or `best_workspace/`.
    `evaluate(code: str, workspace_path: str) -> dict`.
    calls `evaluate(code, workspace, stage)` when the function has three or
    supported `evaluate(code, workspace_path, stage) -> dict` signature, define
    `evaluate(code)`, `evaluate(code, workspace_path)`, and
    `evaluate(code, workspace_path, stage)`.
    `workspace_path` and `stage` are supplied.

- [x] Clarify feedback grader failure-isolation limits.
  - README evidence: optional feedback graders are described as able to add
    metrics or discard candidates; the caveats previously said malformed
  - Current evidence: `Config.validate()` now rejects invalid feedback grader
    config, and `apply_llm_feedback()` now records provider failures, malformed
    numeric response scores, non-finite response scores, and string discard
  - Current status: richer retry/penalty/discard policy remains open, while
    feedback score/weight bounds and composition metadata are now implemented.
    with stage outcomes and also describe optional feedback graders that can
    add metrics or discard candidates.
  - Current evidence: `apply_llm_feedback()` records grader outcomes in
    `evaluation.metadata.llm_feedback`, and now also adds typed stage entries. A local
    `score=0.2` and `discard=true`; the final result was invalid with
    `error="llm_feedback_discard"`, and `stages` now include an
    `llm_feedback:<name>` reviewer stage.
  - Required result: either implement feedback/reviewer stage records first, or
    represent local evaluator stages only and LLM feedback/reviewer outcomes
    state that feedback grader outcomes live under
    `evaluation.metadata.llm_feedback`, can adjust metrics/fitness/validity,
  - README evidence: optional feedback graders are described as recording
  - Current status: the old permissive numeric fallback is superseded.
    Feedback scores now require JSON or explicit `score: <number>` /
    `score=<number>` text, reject incidental HTTP/status numbers and
    percentages, and must be finite values in `[0, 1]`.

- [x] Clarify prompt/history redaction limits.
    prompts, explicit context, plugin context, and persisted run history.
    verbatim to `history.jsonl`.
  - Status: README now warns that mutation/critique prompt history is persisted
    `record_repr = repr(record)`. A local proof wrote a non-finite history
    resulting `history_invalid.jsonl` kept both values verbatim in
    history, prompt summaries, artifact metadata, and future budget accounting.
    with `Unknown plugin: 'missing'` after the existing `history.jsonl` in that
    command failed after printing the run banner; the existing `history.jsonl`
    OpenAI backend replaced existing history, wrote an aborted runtime manifest,
    and `--max-generations 0` failed before seed history was written. This
    that writes seed history and best artifacts without requiring LLM provider
    fail/overwrite semantics but listed only the older history/prompt/manifest
    `history.jsonl` files.
  - Current evidence: `show` now streams `history.jsonl`, fails malformed JSON
    empty-history handling explicit, and requires exact modern validity via
    malformed history rows fail the whole inspection, are skipped with a
    requirement for current history records is now implemented and tested.
    `show` streams history rather than reading the whole file.
    `history.jsonl`, `failure_history.jsonl`, `prompt_history.jsonl`, and

- [x] Clarify evaluator-stage numeric config validation.
  - README evidence: the evaluation and configuration docs show staged
    validators with `samples`, `retries`, `timeout_sec`, and `min_score`; the
  - Current evidence: `Config.validate()` now checks stage numeric fields before
    evaluation. Previously, `_run_stage()` cast stage numeric fields during
    evaluation; `samples <= 0` can reach aggregation with no sample results,
    and `retries < 0` can skip all attempts before an assertion.
    supports configured validator stages with distinct entrypoints, timeouts,
    thresholds, samples, seeds, retries, stage context, and artifact policy.
  - Required result: describe the evaluator as a local staged cascade with
    configurable validator stages, while keeping distributed evaluator workers
  - README evidence: README describes configurable validator stages with
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    samples. A local proof using a minimize primary metric `runtime` with two
    seeded samples returning `0.0` and `10.0` produced aggregated
    cannot request worst-case, quantile, all-samples-pass, or per-metric
    samples returning `score=1.0` produced aggregate `fitness=-0.1` and

- [x] Remove stale malformed-config caveats from architecture/configuration
  - README-adjacent evidence: architecture and configuration docs still said
  - README/config evidence: `docs/configuration.md` documents
    limitation clearly in README/configuration docs.
  - README/config evidence: `docs/configuration.md` documents
    README/configuration docs to state that the field is currently only
  - README-adjacent evidence: architecture/configuration caveats implied
  - Current evidence: `Config.validate()` only checks `plugins` is a list of
    strings, while `_load_plugins()` resolves those names through the CLI's
    plugin registry/config/provenance todo remains open.
  - README/docs evidence: CLI docs now describe `--plugins`, `--overwrite`, and
    whether plugin configuration is validated before cleanup of an existing run
    plugin names. A local proof with `--plugins missing --overwrite` failed
    plugin configuration can fail after known run artifacts have already been
    OpenAI/Anthropic/Ollama backends and describe `--overwrite` as intentional
    `--backends openai:gpt-4o-mini --overwrite --max-generations 0`, and the
    cleanup; until then, warn that invalid provider configuration can fail
  - Current evidence: `evolve()` builds configured LLM backends before seed
    constructs configured backends even for zero-generation runs.
  - README evidence: the supported-backends table named "Claude Opus 4.6" as a
    (`https://platform.claude.com/docs/en/about-claude/models/overview`)
    `docs/todo/papers.md` still tracks AlphaEvolve-scale benchmark hardening.
    the paper todo for benchmark hardening.
  - README-adjacent evidence: configuration and run-artifact docs described
  - README/run-artifact evidence: README and `docs/run-artifacts.md` present
  - README/run-artifact evidence: README and `docs/run-artifacts.md` describe
  - README/docs evidence: README and `docs/run-artifacts.md` describe
    `docs/configuration.md` describes `problem_name` as the final run
  - README-adjacent evidence: `docs/run-artifacts.md` documented

- [x] Clarify plugin config schema validation boundary.
    plugin-specific schemas were partially validated.
  - Required result: document that plugin-specific schemas and constructor
    fields through plugin schemas/constructors, or warn that direct plugin
    extension code must avoid non-positive cadence values until schema support
    if preserved, surface them in manifest/runtime diagnostics so users do not
    outside the clean-run reproducibility contract. Manifest/runtime diagnostics
    and non-object rows with line-numbered `ClickException` diagnostics, keeps
  - Required result: after implementing read-path diagnostics, document whether
  - Status: implemented behavior is fail-fast with normalized diagnostics;
    README and run-artifact docs describe aborted-run diagnostics.
    payload diagnostics, or document the current durability limitation until it
    diagnostics to `manifest_invalid.jsonl`; tests cover non-serializable and
    invalid-sample and threshold-failure metric/fitness/stage-diagnostic
  diagnostics.
    docs describe `evaluation.metadata.metric_bound_diagnostics`.
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    `malformed_metrics`; the payload appeared only in raw stdout from the
    boolean `is_valid`; reserved non-scalar outputs such as `program_output`
    are now persisted as bounded structured program-output metadata.
  - README/run-artifact evidence: README says raw stdout/stderr diagnostics are
    contain full validator output and users should redirect large diagnostics
    docs direct large diagnostics to configured evaluator artifacts until
    schema for stage names, paths, and seed values; until then, avoid claiming
    `AttributeError`, not as a pre-artifact task-setup diagnostic.

- [x] Refresh README Anthropic model-name examples.
    current Anthropic model example.
  - Current evidence: Anthropic's model overview
    forwards configured provider model IDs and does not validate provider
  - Required result: avoid stale exhaustive-looking Anthropic model lists in
    README and present examples as provider-specific model IDs.
  - Required result: either fail on non-empty unknown run directories or
    empty-history handling explicit, and requires exact modern validity via
    `db.all_programs()` was empty, and no accepted `history.jsonl` existed.
    completed loop exits and may be absent after unhandled provider/plugin/
  - Current evidence: `_write_aborted_runtime()` passes an empty plugin list to
    run artifacts can contain sensitive prompts, code, metadata, or provider
    providers, and validators.
    environment variables, accelerator budget/accounting state, or provider/API
    seed-only/evaluation-only runs as provider-free baselines and describe

- [x] Clarify README benchmark-fixture wording.
    Testing" heading could imply a benchmark suite rather than smoke examples.
    `docs/todo/papers.md` still tracks AlphaEvolve-scale benchmark hardening.
    the paper todo for benchmark hardening.
  - Current evidence: `libreevolve/core/database.py::RUN_ARTIFACT_NAMES`
    whether large histories are streamed or fully loaded. The exact validity
    requirement for current history records is now implemented and tested.
  - Status: implemented behavior is fail-fast with normalized diagnostics;
    future resume/database work.
  - Current evidence: strict JSONL write validation is implemented, but
    crash-safe databases. They are not fsynced, checksummed, sequenced, spooled,
    or auto-repaired; after a killed process, complete earlier lines are the
    leave in-memory archive state ahead of accepted history until the database
    consistency work is implemented.
    which AlphaEvolve-style run-budget controls can override `config.yaml`.
  - Status: implemented. `_build_config()` now merges config-file values and
    completed loop exits and may be absent after unhandled provider/plugin/
  - Status: implemented and documented. Runs that abort after startup manifest
    pointers, and completed runs can include `runtime.plugin_artifacts` when
    artifacts written before an abort are summarized the same way as completed
  - Required result: either implement validated plugin artifact summaries for

- [x] Refresh documented run-artifact collision list.
  - README-adjacent evidence: configuration and run-artifact docs described
    fail/overwrite semantics but listed only the older history/prompt/manifest
  - Current evidence: `libreevolve/core/database.py::RUN_ARTIFACT_NAMES`
    includes candidate, failure, and prompt quarantine JSONL files plus
    `evaluator_artifacts/` and `plugin_artifacts/`.
  - Required result: keep docs aligned with the exact artifact set that
  - README/run-artifact evidence: README and run-artifact docs say startup
    fails on known artifacts and `--overwrite` deletes known artifacts, but do
    both `foreign.txt` and a new `manifest.json` in the same run directory.
    if preserved, surface them in manifest/runtime diagnostics so users do not
  - Status: README, configuration, and run-artifact docs now state that
    `overwrite`, are not run-owned manifest artifacts, and put the directory
  - README/run-artifact evidence: README and `docs/run-artifacts.md` present
  - README/run-artifact evidence: README and `docs/run-artifacts.md` describe
    `history.jsonl`, `failure_history.jsonl`, `prompt_history.jsonl`, and
    quarantine streams as durable run artifacts that support inspection and
    future resume/database work.
    that differs from the separate `manifest.json` atomic-write guarantee.
  - Status: README, run-artifact docs, and development docs now state that
    crash-safe databases. They are not fsynced, checksummed, sequenced, spooled,
    distinguish this from `manifest.json` atomic replacement.
  - README/run-artifact evidence: README presents `history.jsonl` and
    leave in-memory archive state ahead of accepted history until the database
  - README/run-artifact evidence: failure history is described as the durable
    failed-trial memory used for prompt feedback and inspection.
  - README/docs evidence: README and `docs/run-artifacts.md` describe
    `--run-name` values before artifact preparation, and runtime startup now
  - Status: README, configuration, and run-artifact docs now state that the
    manifest writes. Tests cover direct outside-path rejection and

- [x] Add plugin artifacts to the run-artifact layout.
  - README-adjacent evidence: `docs/run-artifacts.md` documented
    `runtime.plugin_artifacts` and the `ttt_rl` export path, but the top-level
    directory tree omitted `plugin_artifacts/`.
    `runs/<run-name>/plugin_artifacts/ttt_rl/`, `TTTRLPlugin` writes
  - Required result: show plugin artifact directories in the canonical run
    layout so docs match the runtime artifact surface.
    Click options that affect run budget accounting and artifact collision
  - README/run-artifact evidence: README and run-artifact docs describe
    stop reason, budget consumption, retrieval summaries, and plugin artifact
    README/run-artifact docs explicit that `runtime` is guaranteed only for
  - README/run-artifact evidence: README and run-artifact docs position
    artifact.
  - README/run-artifact evidence: README says each run manifest records
    manifest, or update README/run-artifact docs to state that current
  - README/run-artifact evidence: README and run-artifact docs describe
    artifacts from problem-owned input fixtures, or document that current
  - README/run-artifact evidence: README and run-artifact docs present manifest
    `read_bytes()` without a symlink-specific policy, resolved-target
    containment check, or skipped-path diagnostics. On platforms where symlinks
  - README-adjacent evidence: `docs/run-artifacts.md` lists
  - README/run-artifact evidence: README and run-artifact docs describe LLM
  - README/run-artifact evidence: docs describe timeout cleanup metadata and
    `431 passed, 1 skipped, 2 deselected`; users still should not read current
    A docs-only change can therefore skip the workflow's secret scan and unit
    imply docs-only validation when the workflow is skipped.
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    invalid-sample metric/fitness limits in README/run-artifact docs.
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    stored with each candidate and describes evaluator artifacts/stdout/stderr,
    artifacts while `evaluate()` itself must return scalar metrics only.
  - README/run-artifact evidence: README says raw stdout/stderr diagnostics are
  - Current evidence: evaluator stdout/stderr are redacted but stored in full
    to configured artifacts instead.
    `validate.py` as a required problem contract, while run-artifact docs say
    `--overwrite` intentionally replaces known artifacts for a fresh run.

- [x] Refresh README CLI reference for budget and overwrite options.
  - README evidence: the CLI reference listed core run options but omitted
  - Required result: keep README's compact CLI reference aligned with live
  - README-adjacent evidence: `docs/configuration.md` describes configuration
  - README-adjacent evidence: `docs/configuration.md` says configuration is
    overrides, and document that ordering in configuration docs.
  - README/run-artifact evidence: README and run-artifact docs describe
    README/run-artifact docs explicit that `runtime` is guaranteed only for
  - Status: implemented and documented. Runs that abort after startup manifest
    README and run-artifact docs describe aborted-run diagnostics.
  - README/run-artifact evidence: docs describe normal and aborted `runtime`
    first, or update README/run-artifact docs to state that only aborted
  - README/run-artifact evidence: README describes run history and manifests as
  - Required result: either make zero evaluation budgets invalid, or document
  - README/run-artifact evidence: README and run-artifact docs position
    payload diagnostics, or document the current durability limitation until it
  - Status: implemented and documented in run-artifact docs.
  - README/run-artifact evidence: docs describe `--overwrite` as intentional
    destructive cleanup and document that ordering, or warn that malformed
  - README/run-artifact evidence: README says each run manifest records
  - Status: implemented and documented. Run manifests now include
    declared runtime dependencies. README, architecture, and run-artifact docs
  - README/run-artifact evidence: README says each run manifest records Git
    README/run-artifact docs to state that current Git metadata describes the
  - README/run-artifact evidence: README and `docs/run-artifacts.md` describe
  - Required result: either redact/hash dirty status paths in code and document
    the safe fields, or update README/run-artifact docs to clearly state that
  - README/run-artifact evidence: README and run-artifact docs describe
  - Status: refined and documented. `problem_provenance()` no longer excludes
  - README/run-artifact evidence: README and run-artifact docs present manifest
  - Status: implemented and documented. Source/problem provenance traversal now
    provenance. README, architecture, and run-artifact docs describe the
  - README/run-artifact evidence: README and run-artifact docs present
    skipped/read-failure diagnostics first, or document that current manifest
  - README-adjacent evidence: `docs/run-artifacts.md` lists
    generation counters, or document the current `no_parent` semantics and
  - README/run-artifact evidence: README and run-artifact docs describe LLM
    document seed history rows as raw evaluator baselines so users do not
  - Status: implemented and documented. Seed history rows are explicit raw
  - README/run-artifact evidence: docs describe timeout cleanup metadata and
  - Status: README, problem-format, architecture, and run-artifact docs now
  - README evidence: README shows a GitHub Actions `Tests` badge and asks
    now depends heavily on README, ROADMAP, docs, paper index, and
    validation, or update README/development docs to state exactly which local
  - Status: README and development docs now state that the `Tests` workflow is
  - README evidence: the feature list and architecture tree still described
  - README evidence: README describes configurable validator stages with
    `runtime=5.0` and normalized `fitness=0.5`. README does not state that
    `is_valid=False` while aggregate `metrics.score` remained `1.0`, so README
    first, or document the current fixed mean/all-booleans behavior and its
    limits in README/run-artifact docs.
  - Status: README, configuration, architecture, and run-artifact docs now state
    last-value fallback for other values; they also document the invalid-sample
  - README/config evidence: README and configuration docs describe staged
    `eval_stages[].seeds[]`, or update README/config/run-artifact docs to say
  - README/config evidence: docs describe `eval_stages[].retries` and
    document clearly that current evaluator retries are validity/error retries
  - README evidence: README describes metric directions/bounds, normalized
    results, or document bounds as normalization hints and expose raw/clamped
    score provenance in run records so README users do not assume
  - Status: implemented and documented. README now states bounds are
  - README evidence: README describes configurable validator stages with
  - Required result: either document `timeout_sec` as a per-attempt validator
  - Status: README, configuration, architecture, and run-artifact docs now state
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    channel for evaluator-returned non-scalar data, or document that current
  - Status: README, problem-format, architecture, and run-artifact docs now
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    stored with each candidate, and problem docs say undeclared evaluator keys
    evaluation records and document them, or narrow README/run-artifact wording
  - README/run-artifact evidence: README and run-artifact docs describe
    channel and document stdout as diagnostics only, or document that trailing
  - README/run-artifact evidence: README says raw stdout/stderr diagnostics are
    with truncation metadata, or document that current history records can
  - Status: README, problem-format, architecture, and run-artifact docs now
  - README/run-artifact evidence: README and run-artifact docs describe staged
    update README/configuration/run-artifact docs to state that current stage
  - README/run-artifact evidence: README and run-artifact docs say manifests
    hashing with read-failure diagnostics first, or document that current
  - README/config evidence: README and configuration docs describe configured
  - Required result: after implementation, document the accepted scalar
  - Status: implemented and documented in configuration/problem-format docs.

- [x] Refresh evaluator labels beyond the original three-tier cascade.
    supports configured validator stages with distinct entrypoints, timeouts,
    thresholds, samples, seeds, retries, stage context, and artifact policy.
  - Required result: describe the evaluator as a local staged cascade with
    configurable validator stages, while keeping distributed evaluator workers
  - README evidence: README describes configurable validator stages with
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    threshold behavior. A second local proof with one invalid sample and both
    invalid sample sets. A third proof with `min_score: 0.5` and a validator
    `is_valid=False` and `stage_threshold_not_met` while `metrics.is_valid`
    stayed `True` and the stage row still showed `passed=True`.
    invalid-sample and threshold-failure metric/fitness/stage-diagnostic
    and `min_score` threshold cases where top-level validity/fitness can
    diverge from aggregate raw metrics or local stage rows. Configurable

- [x] Clarify that the current problem format is Python-only and single-workspace.
  - README evidence: `README.md:258-285` describes one `validate.py` and seed
    files.
  - AlphaEvolve contrast: AlphaEvolve evolves marked regions inside an existing
    codebase and can evaluate complex workflows.
  - Required result: explicitly state current scope and link to the planned
    evolve-block/multi-file work.


- [x] Soften the failure-history feature claim.
  - README evidence: the feature table claimed the last five failed mutations
    are shown in prompts, and the workflow section said failed mutations are
    tracked and shown in later prompts.
  - Current evidence: `evolve()` keeps only in-memory failure hints and skips
    malformed/no-op/search-miss diffs when no changed child code is produced.
    For workspace candidates, invalid non-primary-file changes can also be
    omitted because the check compares `child_workspace.code` to `parent.code`.
  - Required result: describe the current feature as recent failure hints and
    point persistent/queryable full-workspace failed-proposal memory to the
    code TODO.


- [x] Clarify workspace validator import/cwd limits.
  - README evidence: the custom-problem section said validators can accept
    `workspace_path`, but did not explain that the evaluator does not
    automatically run with that path as `cwd` or `sys.path`.
  - Current evidence: `CascadeEvaluator._run_subprocess()` passes the
    materialized candidate root as an argument only, and the `workspace_math`
    example manually inserts it into `sys.path`.
  - Required result: tell problem authors to use `workspace_path` explicitly for
    local imports/files until workspace execution semantics are hardened.


- [x] Clarify feedback graders are primary-file-only for workspaces.
  - README evidence: the feature list says feedback graders can add metrics or
    discard candidates, but did not mention the current prompt only includes
    the primary-file view.
  - Current evidence: `_build_feedback_prompt()` renders `workspace.primary_file`
    and `workspace.code` under `[CODE]`; non-primary workspace files are not
    included.
  - Required result: warn readers that multi-file feedback grading is not yet
    full-workspace aware.


- [x] Clarify multi-file mutations cannot delete or rename files yet.
  - README evidence: the custom-problem section describes multi-file seed
    workspaces and file-section edits, but did not state that workspace
    topology changes are not expressible.
  - Current evidence: `apply_workspace_mutation()` only updates a file's text
    or creates an unknown file in `full` mode; no delete, rename, move, or
    primary-file change syntax exists.
  - Required result: warn readers that current multi-file mutation supports
    edits and limited file creation, not full repository topology evolution.


- [x] Clarify causal plugin mutation-format limitations.
  - README evidence: the plugin section labels the causal plugin as
    CausalEvolve-inspired, but did not state that its factor detector is not
    using the same canonical diff parser as candidate mutation application.
  - Current evidence: `CausalPlugin._detect_factors()` parses only the compact
    local `DIFF_PATTERN`; canonical AlphaEvolve SEARCH/REPLACE fences can
    produce no factor matches and fall back to random guidance.
  - Required result: document that causal guidance is compact-diff-only until
    plugin mutation analysis is unified with the core parser.


- [x] Clarify malformed mutation envelopes can be ignored.
  - README evidence: the custom-problem section describes file-section edits,
    but did not explain that unmatched or malformed envelope spans are not
    diagnosed as a whole response.
  - Current evidence: `_parse_file_sections()` and multi-block full replacement
    use regex `findall()` calls. A response with one valid file/block section
    and one unsupported or malformed envelope can apply the valid section while
    ignoring the unmatched intended edit.
  - Required result: warn readers that current multi-file/block mutation
    parsing is partial and track full-envelope diagnostics in the code TODO.


- [x] Clarify evaluator-stage numeric config is not fully validated.
  - README evidence: the evaluation and configuration docs show staged
    validators with `samples`, `retries`, `timeout_sec`, and `min_score`, but
    did not warn that bad numeric values can fail at runtime.
  - Current evidence: `_run_stage()` casts stage numeric fields during

- [x] Clarify full mutation mode is not prompt-aware by default.
  - README evidence: the workflow says the LLM proposes either a SEARCH/REPLACE
    diff or configured full-block/full-code replacement.
  - Current evidence: `mutation_mode` changes the mutation application path,
    but `PromptSampler.DEFAULT_TEMPLATE` still instructs the model to return
    SEARCH/REPLACE fences and "Just the raw diff block"; `evolve()` does not
    pass `config.mutation_mode` into prompt construction.
  - Required result: tell users that full mode changes parser/application
    semantics today, while prompt wording remains diff-oriented unless they
    provide a custom prompt template.


- [x] Clarify problem-local validator helper imports are not automatic.
  - README evidence: the problem-format section says `validate.py` defines
    `evaluate(...)`, but did not warn that `validate.py` is loaded by file path
    from a temporary runner rather than as a normal problem-local package.
  - Current evidence: `_RUNNER` uses `spec_from_file_location()` and
    `subprocess.run()` does not set `cwd` to the problem directory or add the
    validator directory to `sys.path`.
  - Required result: warn authors that sibling validator helpers/package
    imports need manual path handling until evaluator import semantics are
    hardened.


- [x] Clarify validator subprocesses inherit environment until hardened.
  - README evidence: README says validators run in a temporary local
    subprocess but did not mention that the subprocess inherits the parent
    environment, including `.env`-loaded provider variables.
  - Current evidence: CLI import loads `.env` with `override=True`, and
    `CascadeEvaluator._run_subprocess()` does not pass an explicit `env` to
    `subprocess.run()`.
  - Required result: warn users that validator environment/secret isolation is
    not implemented and point the implementation gap to the TODOs.


- [x] Clarify candidate history lacks archive admission status.
  - README evidence: the flow says valid programs enter the MAP-Elites archive
    and all programs are logged, but did not say history records do not mark
    which logged programs were admitted, ignored, or displaced.
  - Current evidence: `evolve()` logs a `Program` before `db.add()`, and
    `MAPElites.add()` returns no insertion result. `history.jsonl` does not
    include threshold reason, island id, cell coordinates, replacement status,
    or previous occupant id.
  - Required result: warn readers that current candidate history is not an
    archive-admission event stream.


- [x] Clarify ImprovEvolve guidance is static and unattributed.
  - README evidence: the plugin section labels `modular` as
    ImprovEvolve-inspired modular decomposition prompting, but does not state
    that it always injects the same block and does not log a selected
    generate/improve/perturb operation.
  - Current evidence: `ModularPlugin.build_extra_context()` returns a constant
    prompt block, and `evolve()` concatenates plugin context into the prompt
    without a structured per-plugin context/provenance record.
  - Required result: document that modular guidance is static prompt-only until
    plugin prompt-context attribution or real ImprovEvolve operations exist.


- [x] Clarify validator-generated files are not retained.
  - README evidence: README says raw metrics and diagnostics are stored with
    each candidate, but did not explain that files written by `validate.py`
    inside the temporary candidate workspace are discarded.
  - Current evidence: `CascadeEvaluator._run_subprocess()` runs validators
    inside `tempfile.TemporaryDirectory()` and returns only metrics, stdout,
    stderr, errors, elapsed time, and metadata. There is no artifact copy-out
    path before the temporary directory is deleted.
  - Status: README now tells users that generated evaluator files are not
    collected and should be summarized through metrics/stdout/stderr until
    artifact collection is implemented.
  - Required result: keep this warning until evaluator artifact collection is
    implemented and documented in run artifacts.


- [x] Clarify validator timeout process-tree limits.
  - README evidence: README discussed validator subprocess execution and
    timeouts but did not state whether a timed-out validator's descendant
    processes are also terminated.
  - Current evidence: `CascadeEvaluator._run_subprocess()` uses
    `subprocess.run(..., timeout=...)` without a process group or Windows Job
    Object. A local proof showed a validator-spawned child process can write a
    marker after the evaluator has returned `timeout`.
  - Required result: warn users that validators should avoid long-lived child
    processes until process-tree cleanup is implemented.


- [x] Clarify `show` is not archive-best reconstruction.
  - README evidence: the inspect-results section prints "Best fitness" and
    "Best program" from `libreevolve show`, which can imply the same archived
    best output as a completed run.
  - Current evidence: `cli.show()` reads `history.jsonl` and selects
    `max(records, key=lambda r: r["fitness"])` without checking
    `evaluation.is_valid`, `metadata.archive_admission.admitted`, or full
    workspace artifacts. The command prints only `best["code"]`.
  - Status: README now calls `show` a compact history view and tells users to
    use `best.py`/`best_workspace/` from the original run for the archived best
    output.
  - Required result: keep the README distinction until `show` is made
    validity-aware, archive-aware, metric-aware, and workspace-aware.


- [x] Add candidate path-collision handling to candidate fidelity.
  - Evidence: path grammar hardening rejects unsafe paths, and
    `CandidateWorkspace` now rejects distinct raw inputs that normalize to the
    same candidate path. Materialization now preflights case-folded host paths
    only the primary file convenience view. Binary/static artifacts are not
    first-class candidate members yet. Validator subprocesses now run with the
    candidate root as `cwd` and import path, but there is still no arbitrary
    external repository/build-system runner. Candidate path collision handling
    is also incomplete: candidate construction rejects duplicate normalized
    paths and materialization rejects case-folded host-path collisions before
    writes, and duplicate file edit sections are rejected before partial
    application, but complex topology-operation collision policy remains
    incomplete.
    File/block envelope diagnostics now reject malformed sections before
    partial edits are applied. File-set topology changes such as delete, rename,
    move, and primary-file replacement are implemented with command file
    sections. POSIX-style absolute candidate paths remain a path-grammar gap:
    leading slashes are stripped, so `/new.py` is treated as relative
    `new.py` instead of rejected.


- [x] Add mutation-envelope diagnostics for partial parses.
  - Evidence: file and block mutation envelopes now validate unmatched,
    orphaned, nested, empty-name, invalid-name, and unsafe-path sections before
    partial edits are applied.
  - README evidence: the custom-problem section describes optional multi-file
    seed workspaces but did not mention that `<<<FILE ... >>>FILE` parsing is
    narrower than ordinary repository path handling.
  - Current evidence: file-section headers now pass through
    `normalize_candidate_path()`, and README documents that nested paths,
    hyphens, spaces, Unicode filename characters, and Windows-style
    backslashes are accepted when normalized safely. README now also warns that
    normalized-path collisions and host-filesystem case folding can still
    overwrite files.
  - Required result: keep README aligned with current path parser behavior
    while still warning separately about path-collision handling and partial
    whole-envelope diagnostics.


- [x] Clarify first-error-only workspace syntax diagnostics.
  - README evidence: README described the cascade evaluator's syntax filter
    but did not say whether multi-file syntax diagnostics are aggregated.
  - Current evidence: `_syntax_error()` returns immediately on the first
    Python `SyntaxError`. A local proof with invalid `a.py` and `b.py` reported
    only `a.py`, while result metadata still listed both files.
  - Required result: tell users the current pre-validator syntax check covers
    `.py` files but reports only the first syntax error until aggregate
    workspace diagnostics are implemented.


- [x] Add aggregate workspace syntax diagnostics to evaluator feedback work.
  - Evidence: `_syntax_error()` checks candidate `.py` files in sorted order
    and returns on the first `SyntaxError`; a local proof with invalid `a.py`
    and `b.py` reported only the `a.py` failure while metadata listed both
    files.
  - Current roadmap gap: evaluator diagnostics covered structured results,
    stdout/stderr, retries, and artifacts, but not first-error-only syntax
    feedback in multi-file candidates.
  - Required result: report all Python syntax failures across a candidate


- [x] Failed-trial and rejected-mutation memory.
  - Status: completed item archived from the split trace; detailed task body was not present in the available command output.

- [x] Define run-directory collision and append semantics.
  - Spec evidence: AlphaEvolve-style experiments need reproducible run identity,
    clean provenance, and intentional resume behavior for long-running runs.
  - Status: implemented. `Config` now has a UUID4 `run_id` and explicit
    `run_collision_policy` with validated `fail` and `overwrite` modes. CLI
    startup and `ProgramDatabase` both preflight known run artifacts; the
    default fails before appending to `history.jsonl`/`prompt_history.jsonl` or
    rewriting `manifest.json`, while `--overwrite` /
    `run_collision_policy: overwrite` removes only known run artifacts
    (`history*.jsonl`, `failure_history*.jsonl`, `prompt_history*.jsonl`,
    `manifest.json`, `best.py`, and `best_workspace/`) before the new run.
    `manifest.json` records `run_id` and the effective collision policy.
  - Verified by: `tests/test_cli.py`, `tests/population/test_database.py`, and
    `tests/core/test_config.py` cover CLI preflight, overwrite cleanup,
    manifest metadata, and config validation.
  - Remaining divergence: true resume, parent-run relationships, deterministic
    lineage ids, archive/controller reload, and evaluator-code provenance are
    tracked separately.


- [x] Add first-class literature/context ingestion.
  - Spec evidence: AlphaEvolve supports explicit context such as instructions,
    equations, code snippets, and relevant literature, including PDF files.
  - Current evidence: `load_problem()` reads problem-local `.txt`, `.md`,
    `.py`, and `.pdf` files from `context/`; text/code files are direct,
    PDFs are extracted with `pypdf`, long context is deterministically bounded,
    and `PromptSampler` renders source headers. `DeepResearchPlugin` remains a
    separate arXiv-search plugin, not the local literature ingestion path.
  - Status: implemented for deterministic local context ingestion and PDF text
    extraction with documented limits. Remaining hardening: semantic
    summarization/ranking for very large corpora.
  - Required result: allow problem-local context files, PDFs, equations, and
    code snippets to be selected, summarized, and rendered deterministically.


- [x] Add context-source manifests, recursive selection, and provenance.
  - Spec evidence: AlphaEvolve task setup can include explicit instructions,
    equations, code snippets, and literature; reproducible runs need to know
    exactly which context sources and excerpts were available to the prompt
    sampler.
  - Current evidence: `_load_context_files()` now walks `context/`
    recursively, honors optional `context.yaml` `include`, `exclude`, and
    `max_chars_per_source` fields, keys content by relative source path, and
    records per-source hashes, byte counts, original/rendered character counts,
    truncation spans, extraction status, and PDF page ranges where available.
    `PromptSampler` renders citation-style context headers with hash prefixes,
    excerpt spans, and extraction status. `ProgramDatabase._write_manifest()`
    persists `problem.context_sources` for run provenance. Tests cover nested
    context directories, duplicate basenames, changed source hashes, PDF
    no-text and extraction-failure metadata, manifest provenance, and prompt
    citation rendering.
  - Status: implemented for deterministic recursive local context provenance.
    Remaining context scale work is tracked separately under prompt budget and
    summarization/ranking tasks.


- [x] Persist live retrieval/plugin context provenance.
  - Spec evidence: AlphaEvolve-style prompt sampling can include relevant
    literature and external context, but reproducible experiments need the
    source, query, retrieval time, selected excerpts, and failures that shaped
    a prompt.
  - Current evidence: `DeepResearchPlugin.on_generation_start()` derives a live
    query from the current best fitness and records bounded retrieval events in
    `metadata.plugin_context[].metadata.retrieval_events`, including provider,
    query, generation, best id/fitness, timestamp, status, result length,
    synthesis hash, source IDs/URLs, source timestamps/authors, summary hashes,
    error text, and structured error types such as `network_error`,
    `parse_error`, and `provider_exception` when available.
    `arxiv_search_result()` preserves those source/error fields for the default
    arXiv provider, while `arxiv_search()` remains a string-only compatibility
    wrapper. Retrieval state still does not include full result payloads,
    source-content hashes, ranking provenance, prompt history entries, or
    plugin artifacts. Completed manifests now include `runtime.retrieval` with
    deduplicated event counts, per-plugin status/source counts, and compact
    event summaries.
  - Status: implemented for bounded retrieval-event provenance, prompt-visible
    URL citations, error classification, candidate history records, and
    run-manifest summaries. Full payload/ranking artifact retention remains a
    separate hardening gap.
  - Required result: store retrieval events with provider, query, generation,
    parent/best ids, result IDs/URLs, timestamps, selected snippets, failures,
    and hashes; render citations in prompt context; include plugin retrieval
    artifacts or summaries in run manifests; and test successful, empty,
    malformed, and failed retrieval paths.


- [x] Implement meta-prompt evolution.
  - Spec evidence: AlphaEvolve co-evolves prompt instructions/context in a
    separate database analogous to solution programs and ablates "No meta
    prompt evolution" as a reduced system.
  - Current evidence: `PromptDatabase` stores prompt templates as prompt
    programs with lineage, selection, scoring, mutation, and append-only
    `prompt_history.jsonl`. The loop records `prompt_program_id` per candidate
    and can optionally ask the active LLM to mutate the prompt template at
    `meta_prompt_interval`.
  - Status: implemented as a local prompt-program database and optional
    interval-based LLM template mutation. Remaining hardening: richer prompt
    fitness and ablation reporting.
  - Required result: create a prompt-program representation, mutation path,
    scoring/selection policy, and integration into `build_prompt()`.


- [x] Define prompt-program reward normalization and selection policy.
  - Spec evidence: AlphaEvolve treats meta-prompt evolution as a system
    component that can be ablated, so prompt-program fitness should be
    reproducible, comparable across runs, and separate enough from candidate
    scoring to support prompt-lineage analysis.
  - Current evidence: `Config` now exposes `prompt_reward_mode`
    (`absolute` final composed child score or `improvement` over parent score),
    `prompt_reward_bounds`, and `prompt_explore_coeff`. `PromptDatabase`
    normalizes raw prompt rewards to `0..1`, clamps out-of-range values, uses
    the configured exploration coefficient in selection, and records reward
    telemetry under `program.metadata.last_prompt_reward`. `evolve()` records
    parent score, final candidate score, and prompt reward policy in
    `prompt_history.jsonl`; `manifest.json` includes the effective policy.
    Tests cover negative/out-of-range rewards, plugin-adjusted scores,
    multiple metrics, deterministic selection with zero exploration, and
    improvement-mode telemetry.
  - Status: implemented for a documented bounded scalar prompt-reward policy.
    Broader experiment ablation reporting remains tracked with compute-budget
    and run-manifest work.


- [x] Validate configured and mutated prompt templates before use.
  - Spec evidence: AlphaEvolve's prompt evolution must keep prompts usable by
    the evolutionary loop; malformed seed or evolved instructions should not
    break future generations.
  - Current evidence: `validate_prompt_template()` defines the allowed
    `PromptSampler` placeholder schema and requires `{task}` as the minimal
    configured/evolved template anchor. `Config.validate()` rejects malformed
    configured `prompt_variants` at startup. `PromptDatabase.__init__()`
    validates seed prompt programs, and `PromptDatabase.mutate()` validates LLM
    meta-prompt outputs before insertion. Rejected prompt mutations are written
    to `prompt_history_invalid.jsonl`, the parent prompt program receives a
    penalty event in `prompt_history.jsonl`, and the invalid template is not
    added to the prompt population. `PromptSampler.build()` also validates the
    selected template before formatting as a final guard.
  - Status: implemented with tests for unknown placeholders, malformed braces,
    empty placeholders, attribute/index placeholders, missing required fields,
    invalid configured variants, invalid configured prompt database seeds, and
    invalid LLM-mutated prompt templates in the evolution loop.


- [x] Meta-prompt evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt instructions/context can be co-evolved in a separate
    database.
  - Current evidence: `PromptDatabase` stores prompt programs, logs
    `prompt_history.jsonl`, records prompt rewards/usages, and supports
    lineage-preserving mutation. `evolve()` uses prompt programs during prompt
    construction and can optionally ask the active LLM to mutate templates.
  - Status: implemented locally. Prompt-program reward now has an explicit
    absolute/improvement mode, bounded normalization, configurable exploration
    coefficient, and persisted reward telemetry. Initial configured prompt
    variants are now selected through untried prompt programs in config order.
    Prompt-program reward is still a scalar final-score/improvement policy rather than a
    multi-metric prompt-fitness model. Meta-prompt mutations are syntax-checked
    but can still drop essential channels: a local proof admitted
    `Task only: {task}` as an evolved child template, omitting `{parent_code}`
    and `{mutation_instructions}`. There is no full experiment
    AlphaEvolve-equivalent ablation harness.


- [x] Refresh the local paper index after implementation passes.
  - Evidence: `papers/README.md` still listed multi-file candidates, critique,
    LLM feedback, and meta-prompt evolution as open after those local
    implementations landed.
  - Status: refreshed the AlphaEvolve row to distinguish implemented local
    behavior from remaining async, multi-objective, database, full-workspace

- [x] Unify file-section path parsing with workspace path normalization.
  - Spec evidence: AlphaEvolve can evolve existing code files/codebases, where
    ordinary repository filenames may contain hyphens, spaces, generated-file
    suffixes, or other characters not represented by the current parser.
  - Current evidence: `_FILE_SECTION_PATTERN` captures the full file-section
    header line and `apply_workspace_mutation()` validates it through
    `normalize_candidate_path()`. File sections now accept nested paths,
    hyphens, spaces, Unicode filename characters, and Windows-style
    backslashes when the normalized path is safe; empty paths and unsafe
    normalized paths are rejected explicitly.
  - Status: implemented for current `<<<FILE ... >>>FILE` envelopes, with
    tests for hyphenated, spaced, nested, backslash-normalized, Unicode, colon,
    and empty file-section paths.
  - Required result: use one validated relative-path grammar for loader,
    prompt envelopes, mutation parsing, normalization, and diagnostics; reject
    unsafe paths explicitly; add tests for hyphenated, spaced, nested,
    backslash, Unicode/normalization, and malformed file-section paths.


- [x] Detect normalized-path and host-filesystem path collisions.
  - Spec evidence: AlphaEvolve-style codebase evolution needs a faithful
    candidate file set. Two logical candidate files should not silently collapse
    in memory or overwrite each other when validators materialize the
  - Required result: keep marker validation on the roadmap alongside
    workspace/codebase fidelity.


- [x] Add file-section path grammar hardening to candidate fidelity.
  - Evidence: `<<<FILE ... >>>FILE` headers now capture the full header line
    and pass through `normalize_candidate_path()`, so common repository
    filename shapes such as nested paths, hyphens, spaces, Unicode filename
    characters, and Windows-style backslashes are accepted when safe.
  - Current roadmap gap: workspace fidelity covered file sets and artifacts but
    not whether LLM file-section envelopes can address ordinary codebase
    filenames.
  - Required result: track unified path parsing, unsafe-path diagnostics, and
    tests for common repository filename shapes.


- [x] Add normalized LLM call telemetry to backend scheduling work.
  - Evidence: backend adapters return plain text and discard provider usage,
    latency, retry counts, request ids, finish reasons, API mode, and raw
    provider diagnostics.
  - Current roadmap gap: backend work covered scheduling and role accounting
    but not the per-call telemetry needed to prove cost/latency/budget claims.
  - Status: implemented at the ensemble boundary for role, backend, backend
    metadata, strategy, API mode, prompt/output sizes and hashes, latency,
    status/error fields, and scheduler counts. Provider token usage,
    request/response ids, finish reasons, adapter-internal retry counts, and a
    separate run-scoped call log remain open.
  - Required result: track call-result objects, provider usage, prompt/output
    size, retries, latency, API mode, request/response ids, failure metadata,
    and scheduler/budget updates from that telemetry.


- [x] Document the MAP-Elites boundary as fixed local quality-diversity search.
  - Paper evidence: canonical MAP-Elites illuminates a behavior space chosen
    for the problem domain.
  - Current evidence: `MAPElites`'s docstring, README, architecture docs,
    roadmap, code todo, and paper index describe LibreEvolve's archive as a
    fixed local 3D heuristic over normalized performance, primary-file code
    length, and primary-file TF-IDF diversity, not a canonical
    problem-defined behavior-descriptor implementation.
  - Required result: keep the documentation boundary explicit while the
    remaining descriptor implementation work stays open.


- [x] Reject duplicate block sections in multi-block full replacement.
  - Spec evidence: AlphaEvolve-style skeleton preservation needs every
    evolvable block edit to be unambiguous. Multiple edits for the same named
    block should either be rejected or represented explicitly in a typed
    mutation record.
  - Previous evidence: `_apply_full_replacement()` stored parsed
    `<<<BLOCK name ... >>>BLOCK` sections in a dict, so a duplicate name
    silently overwrites the earlier body. A local proof with two `<<<BLOCK a`
    sections returned `err=None` and applied only the later `x = 99` body.
  - Status: implemented. Duplicate block-section names now fail closed with
    `malformed_block_sections:duplicate_name` before applying a multi-block
    full replacement.
  - Validation: `tests/core/test_candidate.py` covers duplicate block-section
    rejection and proves the original candidate is unchanged.


- [x] Support file deletion and rename/move operations in workspace mutations.
  - Spec evidence: AlphaEvolve can evolve whole files/codebases, not only edit
    text inside a fixed set of files. Real codebase evolution may need removing
    obsolete files, renaming modules, or moving components while preserving
    POSIX-style absolute-looking paths such as `/new.py` are accepted and
    materialized as relative `new.py`. It also accepts control-character paths
    through the direct workspace API: a local proof constructed
    `CandidateWorkspace({"bad\nname.py": "x=1\n"}, "bad\nname.py")`
    successfully, then `materialize()` failed with `OSError: [Errno 22]
    Invalid argument` on Windows.
  - Required result: after implementation, document that candidate paths are a
    strictly relative, host-safe grammar and include leading-slash plus
    control-character examples in path-safety tests/docs; until then, avoid
    broad "all unsafe paths rejected" wording.


- [x] Document causal-plugin reward baseline limits.
  - README/plugin evidence: docs describe CausalEvolve-inspired outcome-factor
    guidance, which can imply factors are credited against the relevant parent
    or causal baseline.
  - Current evidence: `CausalPlugin.on_evaluated()` uses the immediately
    previous plugin history score as the baseline. A local proof evaluated an
    unrelated constant-change candidate at `0.9`, then an unrelated loop-change
    candidate at `0.8`; the loop factor received zero reward solely because it
    followed a higher-scoring unrelated candidate.
  - Required result: either implement parent/counterfactual factor-credit
    attribution, or document that current causal guidance is an order-dependent
    heuristic over consecutive evaluations.
  - Status: README and `docs/plugins.md` now document that causal-factor
    rewards use selected-parent baseline metadata when available, with legacy
    no-baseline calls falling back to previous plugin history or zero. The
    docs still identify this as a heuristic rather than a causal
    counterfactual baseline.


- [x] Fix stale causal-plugin fallback wording in plugin documentation.
  - Documentation evidence: `docs/plugins.md` says that when no causal factor
  - Required result: update plugin docs to describe deterministic no-match
  - Status: `docs/plugins.md` now says no-match detection falls back to the
    "4 lifecycle hooks," and `docs/plugins.md` lists only
  - Current evidence: `PluginBase` also defines `prompt_context_metadata()`
    and `run_artifacts_metadata()`. These hooks are behaviorally significant:
    `prompt_context_metadata()`, and completed manifests include plugin
    artifact summaries returned by `run_artifacts_metadata()`.
  - Required result: revise README and plugin docs to describe all current
    `docs/plugins.md` lists `prompt_context_metadata()` plus
    `run_artifacts_metadata()` with their call points and manifest/history
  - README/plugin-doc evidence: README and plugin docs describe candidate
    returned by `prompt_context_metadata()`. A local proof put a Python `set`

- [x] Clarify DeepEvolve retrieval query grounding limits.
  - README/plugin-doc evidence: README describes the `deep_research` plugin as
    arXiv/web-search context, which can imply retrieved papers are selected
    from the user's problem or code domain.
  - Status: README and `docs/plugins.md` now state that the default retrieval
    query uses best-program fitness, manifest-safe metric names, and bounded
    best-program code/file identifier terms. The docs also state that task
    text, failures, context files, local paper corpus, and hypothesis templates
    are not part of the query policy yet.
  - Verification: focused DeepResearch and loop tests cover domain-different
    query generation, persisted query inputs, and compact manifest query
    provenance.


- [x] Document admission-gated backend rewards.
  - Current evidence: backend rewards are now admission-gated. `evolve()`
    archive-admitted, and has finite parent/child fitness. Reward provenance is
  - Required result: either implement validity/admission-gated backend rewards,
    `LLMEnsemble.call_history`. A local proof with a provider exception
    `metadata.proposal` and rendered for future parent/inspiration programs.
    children must retain placeholders used by their parent prompt program.
    `{parent_code}` and `{mutation_instructions}` while still entering the
    prompt database.
    but does not guarantee evolved prompts retain code, feedback, inspiration,
    checked against their parent prompt program and rejected if they drop
    parent placeholders, so evolved prompts cannot silently remove existing
    code, feedback, inspiration, or mutation-format channels. Configured seed
    Architecture and configuration docs now state the parent-placeholder
    parent program/workspace and no SEARCH/REPLACE or full-mode mutation
    that configured seeds may omit parent code, feedback, inspirations, and
    configured variants, prompt database seeds, and evolved templates before
    prompt-program database for selection, scoring, lineage, and optional
    history.
    described as quarantined with a parent penalty.
  - Previous evidence: the parent penalty could be invisible to selection when the
    parent has not yet recorded a successful use. `PromptDatabase._reject_mutation()`
    `0.0` and the parent remains an untried prompt arm. A local proof rejected
    meta-prompt children now penalize the parent prompt arm as one use with
    Tests cover never-used and already-used prompt parents.
    written to `prompt_history_invalid.jsonl` with parent id, generation,
    after mutating the parent prompt program. A local proof supplied invalid
    `StrictJsonlError`, wrote no `prompt_history_invalid.jsonl`, and still left
    the in-memory parent with `reward_sum == -1.0`.
    history row exists.
    diagnostically quarantined before parent prompt state changes; invalid
    rejection metadata leaves the parent prompt selection statistics unchanged.
    metrics, evaluator result objects, async controller/workers, meta-prompt
    database, full-code mutation mode, and language/workspace runners.
    fallback behavior and its limits for future resume/history replay.
    create `task_description.txt`, `metrics.yaml`, `validate.py`, and
    tests cover malformed metrics, missing validators, empty task files, and no

- [x] Document or fix backend reward-state validation.
    scheduler mutates state, including backend-index validation, or document
    `llm_max_retries` as a non-negative integer and `llm_fallback` as a boolean
  - Required result: say model names are examples and add validation or docs for
    `reasoning_effort` configuration path and track model/API-mode validation
  - Required result: either implement model-specific validation first, or
    placeholder-retention validation.
    placeholder-validation todo is implemented.
  - Previous evidence: syntax/schema validation only required `{task}`. A local
    first, or document that current validation prevents malformed placeholders
    retention rule alongside schema and dry-run format validation.
    prompt-template validation, which can read as preserving the prompt channels

- [x] Refresh stale OpenAI latest-model wording in configuration docs.
    example and the configuration docs explicitly say provider model IDs must
  - README/config evidence: README and configuration docs present
  - Status: README, configuration docs, and backend docs now state that
  - README-adjacent evidence: architecture/configuration docs described
  - Status: architecture/configuration docs now state that evolved prompt
    Architecture and configuration docs now state the parent-placeholder
  - README/config evidence: README and configuration docs say the CLI loads
  - Status: implemented and noted in configuration docs.
    architecture and configuration docs describe that behavior more fully.
    update README/backends/configuration docs to say backend `role` is
  - Status: documented. README, backend docs, and configuration docs now state
    first, or update README/backends/configuration docs to state that
  - README/config evidence: configuration docs describe `seed`, `log_dir`, and
    mixed policies, and configuration docs say inspiration `mixed` combines
  - Status: documented. README, run-artifact docs, and configuration docs now
  - Status: documented. README and configuration docs now state that non-JSON
  - Status: documented. README and configuration docs now state that feedback
    configuration docs to avoid claiming raw declared metrics are preserved
  - Status: documented. README, configuration docs, and run-artifact docs now
  - README evidence: the evaluation and configuration docs show staged
  - README/config evidence: README and configuration docs present configured
  - README/config evidence: README and configuration docs present stage names
  - README-adjacent evidence: architecture and configuration docs still said
    limitation clearly in README/configuration docs.
    README/configuration docs to state that the field is currently only
  - Status: implemented with direct `Config` tests and configuration docs.
    `--max-evaluations`, `--max-evaluator-seconds`, `--max-runtime-seconds`,

- [x] Update plugin hook counts and hook-contract docs.
    `on_generation_end()` in its hook contract.
    user-managed external artifacts whose provenance must be inspected in the
    prompt reward-mode and exploration-coefficient contract.
    `workspace_path`, but did not explain that the evaluator does not
    passes it as `workspace_path`. README now states that candidate-local
    contract and track remaining sandbox/build-system gaps separately.
    history-inspection tests.
    fail accepted history logging and should be inspected through quarantine
    partial inspection validation rather than full history-schema validation.
  - README evidence: the inspect-results section prints "Best fitness" and
    after describing current run inspection and then says to use
    the evaluator contract generally.
    as structured diagnostics users can inspect.
    diagnostic path, or document the deliberate CLI contract that any
    document that unknown files are preserved and outside the run contract;
    outside the clean-run reproducibility contract. Manifest/runtime diagnostics
    `libreevolve show` as the compact inspection path for current and legacy
    malformed history rows fail the whole inspection, are skipped with a
    quarantine streams as durable run artifacts that support inspection and
    failed-trial memory used for prompt feedback and inspection.
    startup `config`, `problem`, and `provenance` keys. Users inspecting the run
    artifact inventory for inspection.
    the artifacts for inspected experiments, which can imply every completed
    current mixed contract: completed manifest, no best artifacts, and nonzero
  - Current evidence: the evaluator return contract accepts only declared
  - Required result: either persist bounded parse/contract failure details in
    so diagnostics do not imply metric-contract rejection reasons are
    as a complete, robust evaluator-code provenance contract.

- [x] Document archive-admission validity typing or harden it first.
  - README/run-artifact evidence: README describes valid programs entering the
    archive and modern `show` selection using `evaluation.is_valid`, which
    implies validity is a boolean gate.
  - Current evidence: `ProgramDatabase.admit()` and the loop validity helper
    now require `program.evaluation["is_valid"] is True`; missing,
    non-boolean, and false validity values do not enter MAP-Elites. Modern
    `libreevolve show` selection also requires `evaluation.is_valid is True`.
  - Required result: either require exact boolean `True` before live archive
    insertion, or document that current archive-admission records rely on
    truthiness outside the evaluator path and `show` should not be treated as a
    strict typed validity proof for malformed modern histories.
  - Status: hardened in code and covered by database, loop, and CLI tests.


- [x] Document the three-argument validator signature in README problem format.
  - README evidence: `README.md` says `validate.py` must define
  - Required result: update README's custom-problem section to include the
  - Status: README and `docs/problem-format.md` now list all three supported
  - README/problem-format evidence: README and problem-format docs present
  - Status: implemented and documented. README/problem-format/run-artifacts
  - README/problem-format evidence: docs describe validator signatures as
    validator execution path before README/problem-format wording can imply
  - README/problem-format evidence: validator examples and docs say
  - README/problem-format evidence: docs list fixed validator call shapes:
    keep README/problem-format docs fixed-arity, or document the exact
  - README/run-artifact evidence: docs now say validator contracts are
  - Required result: either move the preflight into `evolve()` and keep README
    docs broad, or narrow README/run-artifact wording to say the preflight
  - README/plugin evidence: README says full-block/full-code replacement is an
    README/docs to describe it, or state that the causal plugin only provides

- [x] Document boolean-only `primary` metric flags or enforce them first.
    select the optimization metric, which implies the field is a boolean schema
  - Current evidence: `_validate_metric_schema()` currently evaluates
    `metric.get("primary")` by truthiness. A local proof loaded
    `primary: "false"` and selected that metric as `Problem.primary_metric`;
    `primary: 1` was also accepted and persisted in the metric schema.
    README claims strict metric-schema enforcement, or document the current
    rendered parent programs, inspiration programs, context, and evaluator
  - Current evidence: prompt rendering currently wraps parent and inspiration
    and archived fitness.
    in `metadata.score_composition`, and archive admission remains gated by
    `metadata.score_composition`, and that archive admission is validity-gated.
    `DeltaPlugin` instances with different score adjustments; history recorded
  - Current evidence: score-return validation exists, but plugin-added metrics
    and metadata are not validated before history logging. A local proof plugin
    set `program.metrics["plugin_bad"] = inf`; `evolve()` raised
    `StrictJsonlError` during `history.jsonl` write and only quarantined the
    rejected record in `history_invalid.jsonl`.
    document that plugins must currently keep added metrics/metadata finite and
    guidance, which can imply factors are credited against the relevant parent
    previous plugin history score as the baseline. A local proof evaluated an
  - Required result: either implement parent/counterfactual factor-credit
    parent-aware baseline metadata when available, not only consecutive
    observation order
    `_history` is empty.
    `run_artifacts_metadata()` with their call points and manifest/history
    in that metadata; `ProgramDatabase.log()` raised `StrictJsonlError`, wrote
    only `history_invalid.jsonl`, and produced no accepted candidate history
    metric, code, context, or failure terms.
    candidate code, metrics, failures, context files, or the local paper corpus.
  - README/plugin-doc evidence: README says candidate history and completed
    metadata in candidate history and completed manifests, which can imply it is
    hashes, and parent/inspiration ids in candidate metadata, but it still does
    `reasoning_effort`, and scheduling metadata, but not provider sampling
    inside `_call_record()` before a call-history row was written; another with
  - Required result: either validate bounds at the prompt database/resume
    config-created prompt databases enforce prompt reward-bound validation.
  - Required result: either validate these fields at the prompt database/resume
    boundary, or document that only config-created prompt databases enforce the

- [x] Stop teaching `is_valid` as an ordinary `metrics.yaml` scoring metric.
  - Previous README evidence: the custom-problem `metrics.yaml` example declared
    `is_valid` alongside numeric scoring metrics, and the text says
  - Current evidence: `CascadeEvaluator._validate_metrics()` requires
    `metrics.yaml`, and `load_problem()` now rejects `is_valid` as a declared
    update README so `metrics.yaml` contains numeric optimization metrics and
  - Status: implemented. The README `metrics.yaml` example no longer declares
    required boolean validity gate returned alongside declared scalar metrics.
  - README/config evidence: README examples show `primary: true` as the way to
    substrings. A local proof showed a full-mode replacement file containing
  - README evidence: the multi-file mutation section shows `DELETE`, `MOVE`, and
  - Current evidence: score-return validation exists, but plugin-added metrics
    set `program.metrics["plugin_bad"] = inf`; `evolve()` raised
    `StrictJsonlError` during `history.jsonl` write and only quarantined the
    document that plugins must currently keep added metrics/metadata finite and
    `prompt_context_metadata()`, and completed manifests include plugin
    `run_artifacts_metadata()` with their call points and manifest/history
    global output path, or missing manifest linkage.
    completed manifests link export counts, path, bytes, hash, and quarantine
    manifest.
    counts in the completed manifest, which can imply every queued example is
    GRPO-style training data under run artifacts with manifest-linked counts,
    manifests now include bounded run-level retrieval summaries, but full
    candidate code, metrics, failures, context files, or the local paper corpus.
    manifests record retrieval metadata, which can imply the retrieval context
  - README/run-artifact evidence: `prompt_history.jsonl` is described alongside
    directory now replays `prompt_history.jsonl`; the prior proof that it did not was superseded.
    requires `problem_name` / `--run-name` to be a safe single path component.
    CLI tests prove unsafe `--run-name ../escape` is rejected before `evolve()`
    `problem/helper.py` and candidate `helper.py` showed `validate.py` imported
  - Current evidence: `history.jsonl` records candidates, while
    `metadata.archive_admission` before `history.jsonl` rows are written.
    archive and modern `show` selection using `evaluation.is_valid`, which
    `libreevolve show` selection also requires `evaluation.is_valid is True`.
    truthiness outside the evaluator path and `show` should not be treated as a
    showed such a program became both `db.best()` and an exploit-sampled
    `show`/best selection as score-based and validity-gated, which assumes the
    `libreevolve show` rejects non-fi…24326 tokens truncated…ory.jsonl").write_text("{}\n", encoding="utf-8")

- [x] Document that declared metric bounds are not evaluator-output range
  checks yet.
  - README evidence: README describes metric directions/bounds, normalized
    primary fitness, MAP-Elites performance normalization, and strict
    evaluator-output validation against `metrics.yaml`.
  - Current evidence: strict validation covers declared keys, `is_valid`,
    numeric type, and finiteness, but not whether returned values fall inside
    declared bounds. A local proof with `bounds: [0, 1]` and validator output
    `{"score": 999, "is_valid": True}` produced a valid evaluation with
    stored `metrics.score == 999.0`, no error, and normalized fitness clamped
    to `1.0`.
  - Required result: either enforce bound violations as invalid evaluator
    results, or document bounds as normalization hints and expose raw/clamped
    score provenance in run records so README users do not assume
    out-of-range validator outputs are rejected.
  - Status: implemented and documented. README now states bounds are
    normalization hints rather than hard validity constraints, and run-artifact
    docs describe `evaluation.metadata.metric_bound_diagnostics`.

- [x] Document paper-cache manifest integrity limits or add per-PDF hashes.
    download manifests as the evidence base for implementation-status and
  - Current evidence: `papers/download_manifest.csv` and
    `papers/download_manifest.json` record each paper id, title, URL, local
    The current manifest can confirm intended filenames and approximate size,
    document that the current download manifests are inventory records rather
    than integrity manifests.
  - Status: `papers/download_manifest.csv` and
    `papers/download_manifest.json` now include SHA-256 hashes for all 24 local
    cached PDFs, and `papers/README.md` states that the manifests record both
    the current API contract and add tests proving invalid direct or resumed
    behavior and future resume/replay paths from duplicating rewards.
    `PromptDatabase.mutate()` accepted arbitrary template text without semantic
    minimal. A local proof used `PromptDatabase(tmp, templates=["Task only:
    `validate_prompt_template()` and `PromptDatabase` construction, then
  - Current evidence: `PromptDatabase` admits identical template text as
    parent has not yet recorded a successful use. `PromptDatabase._reject_mutation()`
    written to `prompt_history_invalid.jsonl` with parent id, generation,
  - Previous evidence: `PromptDatabase._reject_mutation()` wrote that record
    `StrictJsonlError`, wrote no `prompt_history_invalid.jsonl`, and still left
    fallback behavior and its limits for future resume/history replay.
    documenting workspace records as replay/resume-ready, extend the same
    validated restore format.
    prompts/manifests.
    selection-policy manifest provenance, exact preservation for UTF-8 text
    manifest/source metadata carries the detailed spans.
    source hashes and that source records are persisted in `manifest.json` for
  - Current evidence: `manifest.json` persists only selected
    cannot be reconstructed from the manifest alone. The loader now rejects
    `context.yml` manifests before source selection.
    manifest policy and skipped-source diagnostics are persisted.
    records plus `problem.context_policy`, including manifest hash, effective
    manifests, and all recursive context entries before selection or reading.
    symlink rejection where supported, linked manifest rejection where
    `prompt_context_metadata()`, and completed manifests include plugin
    `run_artifacts_metadata()` with their call points and manifest/history
    global output path, or missing manifest linkage.
    completed manifests link export counts, path, bytes, hash, and quarantine
    artifact until real training/checkpoint semantics exist.
    counts in the completed manifest, which can imply every queued example is
    GRPO-style training data under run artifacts with manifest-linked counts,
    manifests now include bounded run-level retrieval summaries, but full
    manifests record retrieval metadata, which can imply the retrieval context
    through `PromptDatabase`. Untried prompt programs now follow config order,
    `prompt_reward_bounds`, but direct `PromptDatabase(...,
  - Required result: either validate bounds at the prompt database/resume
    archive checkpoint or migration event log.
    direct/resumed program records.
    let docs or future resume behavior define true same-generation recency.
    `history.jsonl` and `best.py`; they do not include `manifest.json`,
    `prompt_history.jsonl`, `failure_history.jsonl`, or `best_workspace/`.
    `history.jsonl` include `metadata.prompt_program_id` so candidates can be
    `metadata.prompt_program_id`; `prompt_history.jsonl` contained only the
    `metadata.prompt_program_id`. Run-artifact docs describe that distinction.
    was already gone and `manifest.json` existed.
    OpenAI backend replaced existing history, wrote an aborted runtime manifest,
    fail/overwrite semantics but listed only the older history/prompt/manifest
    both `foreign.txt` and a new `manifest.json` in the same run directory.
    if preserved, surface them in manifest/runtime diagnostics so users do not
    `overwrite`, are not run-owned manifest artifacts, and put the directory
    `history.jsonl`, `failure_history.jsonl`, `prompt_history.jsonl`, and
    future resume/database work.
    that differs from the separate `manifest.json` atomic-write guarantee.
    distinguish this from `manifest.json` atomic replacement.
    manifest writes. Tests cover direct outside-path rejection and
    scoped path plus manifest summaries.

- [x] Document validator-contract preflight and current overwrite caveat.
  - README/problem-format evidence: README and problem-format docs present
    `validate.py` as a required problem contract, while run-artifact docs say
    `--overwrite` intentionally replaces known artifacts for a fresh run.
  - Previous evidence: the CLI did not preflight the validator contract before
    preparing the run directory. A local proof with `validate.py` missing
    `evaluate()` and an existing run invoked `--overwrite`; the old
    `history.jsonl` was replaced, a new manifest/history row was written with
    `evaluation.error == "subprocess_error"` and stage error
    `returncode_1`, and the CLI then failed with
    `Evolution produced no valid programs`.
  - Required result: after implementation, document the startup preflight
    guarantees for validator importability, callable `evaluate`, supported
    signatures, and staged validator paths before overwrite cleanup or seed
    evaluation can begin.
  - Status: implemented and documented. README/problem-format/run-artifacts
    docs now state that validator contracts are preflighted before overwrite
    cleanup or manifest creation.


- [x] Allow seed-only and evaluation-only runs without constructing LLM
  providers.
  - Spec evidence: AlphaEvolve-style experiments need reliable baseline
    evaluation of seed programs and ablation fixtures; evaluating known seeds
    values. Regression tests cover existing artifact preservation.


- [x] Add evaluate-only/seed-baseline mode to runtime work.
  - Previous evidence: `evolve()` constructed the LLM ensemble before evaluating seeds.
    A local temp proof with `--max-generations 0 --backends
    openai:gpt-4o-mini` and no `OPENAI_API_KEY` failed during provider client
    construction, leaving only `manifest.json` and no seed `history.jsonl`,


- [x] Document seed-only/evaluate-only runs and current backend requirement.
    credentials.
  - Previous evidence: `evolve()` built configured LLM backends before seed
    evaluation. A local temp proof with no `OPENAI_API_KEY`, an OpenAI backend,
    meant users could not rely on zero-generation runs as provider-free
  - Required result: once implemented, document a seed-only/evaluate-only path
    credentials.
  - README evidence: the supported-backends table named "Claude Opus 4.6" as a
    preflight collision checks and overwrite cleanup use.
    document that unknown files are preserved and outside the run contract;
    outside the clean-run reproducibility contract. Manifest/runtime diagnostics
    the resolved `log_dir`. The CLI preflight path and `ProgramDatabase`
    lists `--max-generations`, `--plugins`, `--backends`, `--mutation-mode`,
    `backends: []` failed despite a `--backends ollama:llama3` override.
    `backends` values from `config.yaml`, and configuration docs state the
    after overwrite cleanup. A local direct-API proof with existing
    `requires-python`, build backend metadata, and installed versions for
    seed-only/evaluation-only runs as provider-free baselines and describe
    --max-generations 0 --backends ollama:llama3 --run-name audit_smoke_goal
    current mixed contract: completed manifest, no best artifacts, and nonzero
    CLI exit when all seed-only candidates are invalid.
  - Current evidence: the evaluator return contract accepts only declared
  - Required result: either persist bounded parse/contract failure details in
    so diagnostics do not imply metric-contract rejection reasons are
    as a complete, robust evaluator-code provenance contract.

- [x] Document config-validation order for CLI overrides or fix it first.
  - README-adjacent evidence: `docs/configuration.md` says configuration is
    assembled from defaults, problem-local `config.yaml`, and then CLI
  - Previous evidence: `_build_config()` constructed `Config(**cfg)` before
    applying CLI arguments, so invalid config-file values aborted before a
    higher precedence CLI value could replace them. Local proofs showed
    `backends: []` failed despite a `--backends ollama:llama3` override.
  - Required result: validate only the final effective config after CLI
    overrides, and document that ordering in configuration docs.
  - Status: implemented. `_build_config()` now merges config-file values and
    CLI overrides first, then validates the final effective `Config`.
    Regression tests cover CLI repair of invalid `max_generations` and
    `backends` values from `config.yaml`, and configuration docs state the
    `manifest.json` as the place for effective config, provenance, runtime
    startup `config`, `problem`, and `provenance` keys. Users inspecting the run
    completed loop exits and may be absent after unhandled provider/plugin/
    plugins expose `run_artifacts_metadata()`. This can imply partial plugin
  - Previous evidence: manifest writes were direct overwrite writes through
    `manifest.json` containing only `{"config": ` raised raw `JSONDecodeError`,
    run artifacts can contain sensitive prompts, code, metadata, or provider
    aborted-run manifests can contain raw exception text from plugins,
    providers, and validators.

- [x] Document manifest write durability or make writes atomic first.
  - README/run-artifact evidence: README and run-artifact docs position
    `manifest.json` as the authoritative run provenance and runtime summary
    artifact.
  - Previous evidence: manifest writes were direct overwrite writes through
    `strict_json_dump()`. A local proof started with a valid manifest and then
    attempted to dump a runtime payload containing `object()`; `json.dump()`
    raised `TypeError` after truncating the file to partial JSON. The docs do
    not warn that invalid runtime/plugin metadata can destroy the existing
    manifest instead of preserving the last valid provenance record.
  - Required result: either implement temp-file/atomic replacement with invalid
    payload diagnostics, or document the current durability limitation until it
    is fixed.
  - Status: implemented and documented in run-artifact docs.
    `strict_json_dump()` now serializes before writing a same-directory
    temporary file and atomically replacing the target. Invalid runtime
    manifest updates preserve the last valid `manifest.json` and append
    diagnostics to `manifest_invalid.jsonl`; tests cover non-serializable and
    non-finite payloads.


- [x] Clarify run stop-reason semantics for all-invalid seed populations.
  - README-adjacent evidence: `docs/run-artifacts.md` lists
    `no_parent` and `no_valid_programs` as current stop reasons, but does not
    explain which one applies when initial seed evaluation produces no
    archive-admitted parent.
  - Previous evidence: a local all-invalid-seed run stopped with
    `runtime.stop_reason == "no_parent"` and `generations_started == 1`; it
    does not use `no_valid_programs` and does not create failure history.
    `no_valid_programs` appears to be a fallback in `RunBudget.finish()` rather
    than the observed startup/no-parent path for normal loaded problems.
  - Required result: either change the runtime to emit a precise
    all-invalid-seed/no-valid-programs stop reason before incrementing
    generation counters, or document the current `no_parent` semantics and
    remove unreachable or misleading stop-reason descriptions.
  - Status: implemented. If seed evaluation leaves no archive-admitted parent,
    the loop now exits with `runtime.stop_reason == "no_valid_programs"`,
    keeps `generations_started == 0`, and does not instantiate or call the
    mutation LLM. Rejected seeds are also recorded in `failure_history.jsonl`.
    Regression coverage verifies all-invalid seed behavior.


- [x] Clarify prompt-template format-spec validation limits.
  - README/config evidence: prompt variants and evolved prompt templates are
    described as validated against the `PromptSampler` placeholder schema
  - Previous evidence: validation accepted known placeholder names even when their
    format specs are incompatible with render-time values. A local proof with
    `Task formatted numeric: {task:.2f}` passed
    `validate_prompt_template()` and `PromptDatabase` construction, then
    `PromptSampler.build()` raised `ValueError` while formatting the string
  - Required result: either implement render-time/dry-run format validation for
    configured and evolved templates, or document that current template
    validation does not catch incompatible format specs.
  - Status: implemented. Prompt-template validation now dry-runs rendering with
    representative prompt values, so incompatible format specs are rejected for
    configured variants, prompt database seeds, and evolved templates before
  - Current evidence: `PromptDatabase` admits identical template text as
    templates, and initial selection by UUID4 order.
  - Required result: either deduplicate configured/evolved prompt templates and
    document template identity, or tell users that duplicate configured
    logged, and optionally mutated, while invalid evolved templates are

- [x] Clarify evolved prompt templates can currently drop essential prompt
  channels.
  - README-adjacent evidence: README/configuration/architecture docs describe
    prompt programs as selected, scored, logged, and optionally mutated, and
    say configured/evolved prompt templates are validated against the
    placeholder schema.
  - Previous evidence: syntax/schema validation only required `{task}`. A local
    proof admitted a mutated prompt template `Task only: {task}`, which omitted
    `{parent_code}` and `{mutation_instructions}` while still entering the
    prompt database.
  - Required result: either implement semantic placeholder-retention rules
    first, or document that current validation prevents malformed placeholders
    but does not guarantee evolved prompts retain code, feedback, inspiration,
    or mutation-format sections.
  - Status: implemented. Mutated prompt templates are now checked against their
    parent prompt program and rejected if they drop parent placeholders, so
    evolved prompts cannot silently remove existing code, feedback,
    inspiration, or mutation-format channels. Configured seed templates remain
    intentionally flexible for backward compatibility.


- [x] Document throughput/depth scheduler initialization limits.
  - Current evidence: `LLMEnsemble._ucb1_select()` now performs pull-once
    quarantine, and failed-call scheduler accounting remain open beyond the
    pull-once initialization policy for the UCB-style scheduler, which can imply
    before every fallback until the scheduler policy is hardened.
    `LLMEnsemble.call_history`. A local proof with a provider exception
  - Current evidence: `LLMEnsemble.generate()` honors `llm_max_retries` at the
    switch, which can imply the scheduler itself enforces those semantics.
    by `LLMEnsemble.__init__()`. A local proof with direct
    ensemble boundary, or document that direct `LLMEnsemble` construction is an
    internal API expecting already-validated scheduler controls.
    `LLMEnsemble.generate()` makes synchronous provider calls and the
  - Current evidence: `LLMEnsemble` is a heuristic UCB-style router over
    `LLMEnsemble` now wraps calls with role, backend, API mode, prompt/output
    size and hash, latency, status, and scheduler-count telemetry. Provider
  - Current evidence: `LLMEnsemble` records call roles and backend metadata,
    the empty label in `LLMEnsemble.backend_metadata`.
    labels should not be treated as scheduler policy.
  - Current evidence: `LLMEnsemble.generate()` accepts arbitrary `role` values
    `throughput_depth` as using numeric `cost`, `latency`, and `depth`
  - Current evidence: the scheduler uses raw values directly. A local proof
    `throughput_depth` metadata is an unnormalized heuristic and extreme values
  - README/backend-doc evidence: scheduler strategy names are documented as
    meaningful modes (`ucb1` and `throughput_depth`), which implies unknown
    direct `LLMEnsemble(..., strategy="typo")` runs UCB-style selection while
    `ensemble_explore_coeff`, but direct `LLMEnsemble([a, b],
    scheduler state `counts == [2, 1]`, `total == 3`.
    config boundary, or document that UCB-style scheduler invariants are
    backend metadata and scheduler state, which implies that metadata is
  - Current evidence: direct `LLMEnsemble` construction does not validate
    `backend_metadata`. A local proof with `backend_metadata="bad"` failed
    `backend_metadata=[{"cost": object()}]` stored a non-JSON object in
    `last_call["backend_metadata"]`. A cardinality proof with two backends and
    `LLMEnsemble.generate()` crashed with `TypeError` while constructing
    non-negative scheduler coefficient.

- [x] Document OpenAI reasoning-effort compatibility as model-dependent.
    `--reasoning-effort` as `low/medium/high/xhigh`, and the config validator
    enforces that static set for every OpenAI model.
  - Current evidence: official OpenAI API docs checked on 2026-05-25 list
    `none`, `minimal`, `low`, `medium`, `high`, and `xhigh` as currently
    supported reasoning-effort values with model-specific restrictions. A
    local proof showed `Config(backends=[{"type": "openai", "model":
    "gpt-5.5", "reasoning_effort": "none"}])` and `"minimal"` are rejected,
    while `xhigh` is accepted without a model-family capability check.
  - Required result: either implement model-specific validation first, or
    LibreEvolve uses a static `low`/`medium`/`high`/`xhigh` validator and does
    not check OpenAI model-specific reasoning-effort support before runtime.
    default mutation contract and tells models not to return extra
  - README evidence: README says models can wrap diffs in markdown fences and
    provider backends and preserving call telemetry, which can imply that model
  - Current evidence: backend config supports model, max tokens, OpenAI
    `reasoning_effort`, and scheduling metadata, but not provider sampling
  - README/backend-doc evidence: provider docs describe OpenAI/Anthropic/Ollama
    OpenAI Responses mock with no message `output_text` returned an empty
    string, which would later look like a model-produced empty mutation. A
    Chat Completions mock with `message.content=None` returned `None`, and
  - Required result: either change the import model so evaluator helpers are
    files now fail cleanly, while plugin-specific schemas and provider/model
    OpenAI/Anthropic/Ollama backends and describe `--overwrite` as intentional
    docs now state that OpenAI/Anthropic credentials and backend construction
  - README/run-artifact evidence: docs say OpenAI/Anthropic credentials and
    OpenAI backend replaced existing history, wrote an aborted runtime manifest,
    and failed at `generation:0:llm_build` with `OpenAIError`. The CLI would
    evaluation. A local temp proof with no `OPENAI_API_KEY`, an OpenAI backend,

- [x] Clarify rejected meta-prompt mutation penalty semantics.
    described as quarantined with a parent penalty.
  - Previous evidence: the parent penalty could be invisible to selection when the
    parent has not yet recorded a successful use. `PromptDatabase._reject_mutation()`
  - Required result: document the intended penalty policy or implement it so
    meta-prompt children now penalize the parent prompt arm as one use with
    `-1.0` reward, making the penalty visible to prompt selection statistics.
    written to `prompt_history_invalid.jsonl` with parent id, generation,
  - Previous evidence: `PromptDatabase._reject_mutation()` wrote that record
    after mutating the parent prompt program. A local proof supplied invalid
    rejection metadata containing a Python `set`; the call raised
    `StrictJsonlError`, wrote no `prompt_history_invalid.jsonl`, and still left
    invalid rejection metadata can abort the meta-prompt path before an invalid
    diagnostically quarantined before parent prompt state changes; invalid
    rejection metadata leaves the parent prompt selection statistics unchanged.
    rejection metadata; keep seed/generated schema differences explicit.
  - Required result: warn readers that richer retry/penalty/discard policy and
    also needs to distinguish raw aggregate metrics from penalty fitness for

- [x] Document or fix failed rejected-template logging for meta-prompt
    written to `prompt_history_invalid.jsonl` with parent id, generation,
    rejected template, error, and metadata.
  - Previous evidence: `PromptDatabase._reject_mutation()` wrote that record
    `StrictJsonlError`, wrote no `prompt_history_invalid.jsonl`, and still left
  - Required result: either make rejected-template logging atomic and
  - Current evidence: `PromptSampler.DEFAULT_TEMPLATE` now renders
    `{mutation_instructions}`.
    `PromptSampler`'s RNG, but `evolve()` selects configured prompt variants
    through `PromptDatabase`. Untried prompt programs now follow config order,
    `prompt_reward_bounds`, but direct `PromptDatabase(...,
    reward_bounds=(1.0, 1.0))` still crashes in `record_result()` with
    `ZeroDivisionError`; `reward_bounds=(2.0, 1.0)` silently changes the
    `prompt_reward_mode` as an enum and `prompt_explore_coeff` as a
    `PromptDatabase` construction accepts them unchecked. A local proof with
    `last_prompt_reward.mode`.
  - README/run-artifact evidence: `prompt_history.jsonl` is described alongside
  - Current evidence: constructing `PromptDatabase` for an existing log
    directory now replays `prompt_history.jsonl`; the prior proof was superseded.
    "Improve this LibreEvolve prompt template" instruction plus the selected
    template. A local proof captured the meta-prompt LLM call after a prompt
    is template-only rewriting with selection/reward applied after the fact.
    `prompt_history.jsonl`, `failure_history.jsonl`, or `best_workspace/`.
    `history.jsonl` include `metadata.prompt_program_id` so candidates can be
    `metadata.prompt_program_id`; `prompt_history.jsonl` contained only the
    prompt-template `add` event.
    `metadata.prompt_program_id`. Run-artifact docs describe that distinction.
    `_redact_sensitive_text()`, while `PromptSampler` renders context and
    `meta_prompt_evolution` and `critique_enabled` as boolean switches, and
    `meta_prompt_evolution` and `critique_enabled` to be booleans. CLI tests
    `history.jsonl`, `failure_history.jsonl`, `prompt_history.jsonl`, and
    `prompt_history.jsonl` and `manifest.json`.

- [x] Document task-description validation or implement it first.
  - README/problem-format evidence: docs present `task_description.txt` as the
    optimization prompt and tell authors to keep it concrete and task-specific.
  - Current evidence: the implementation matches relative paths under
    `cand_root`, but it does not resolve artifact targets back inside
    `cand_root` before reading them. On platforms where symlinks are available,
    `Path.is_file()` and `read_bytes()` can follow symlink targets. The local
    Windows account could not create the proof symlink (`WinError 1314`), but
    the static code path lacks a symlink/path-escape guard and lacks skip
    metadata. `artifact_max_bytes` is also enforced after a full
    `read_bytes()`, so README/config docs should not imply that it bounds
    validator artifact I/O or memory until the collector is hardened. Artifact
    path metadata is also standard-layout-specific: the collector records
    their meaning once the implementation policy is decided.


- [x] Document problem-load CLI diagnostics after they are normalized.
  - Required result: either implement normalized CLI diagnostics first, or
    Windows account could not create the proof symlink (`WinError 1314`), but
  - Current evidence: this Windows workspace uses `py -3.12` for tests and CLI
    `normalize_candidate_path()`, and README documents that nested paths,
    hyphens, spaces, Unicode filename characters, and Windows-style
    backslashes are accepted when normalized safely. README no…120 tokens truncated… safely and unsafe paths are rejected.
  - Current evidence: `normalize_candidate_path()` rejects traversal,
    drive-letter, and colon-component paths, but silently strips leading `/`.
    Invalid argument` on Windows.
    rejected classes: traversal, drive-letter, colon-component, POSIX absolute,
    UNC-style leading-backslash, ASCII control characters, Windows-reserved
    device names, wildcard/quote/pipe characters, and trailing spaces or dots.
    reserved-name rejection.
    `[EXPLICIT CONTEXT]` and counted the source as selected with
  - Current evidence: `_read_text_context()` strips leading/trailing whitespace
    leading spaces and trailing blank lines rendered as `leading\nbody`, while
    decoded as UTF-8 and preserved without trimming. README, problem-format
    docs, architecture docs, and run-artifact docs state that leading/trailing
    whitespace and blank lines are preserved for `.txt`, `.md`, and `.py`
    and Windows junctions at `context/`, linked `context.yaml` / `context.yml`
    supported, and Windows junction rejection.
  - Required result: once the reserved-field policy is implemented or chosen,
    downstream-reserved names.
    valid compact diff for `x = 1`, and a malformed trailing diff for `y = 2`
    trailing edits without surfacing a mutation error.

- [x] Correct artifact include/exclude validation wording and behavior.
    `evaluator_artifact_include`, `evaluator_artifact_exclude`, and stage
    artifact include/exclude fields as glob patterns for validator-created
  - Current evidence: `Config.validate()` now validates artifact include/
    exclude fields with `_validate_artifact_glob_list()`, separately from
    per-stage artifact glob patterns.
  - Required result: either implement artifact-specific glob validation, or
    update README/config/run-artifact docs to state the current restricted
    implying full artifact-content retrieval or global prompt packing.
  - README/run-artifact evidence: README describes `failure_history.jsonl` as
    README/run-artifact docs to state that failure-history records are bounded
    but not sanitized and should be treated as sensitive run artifacts.
  - Status: documented in README and run-artifact docs. Both now state that
  - README/run-artifact evidence: README describes `history.jsonl`
    records first, or update README/run-artifact docs to state that generated
    writes artifacts under `Path(config.log_dir) / config.problem_name`.
    how `--run-name` changes the artifact path so quickstart users inspect the
    materialized as relative `new.py`. It also accepts control-character paths
    successfully, then `materialize()` failed with `OSError: [Errno 22]
  - README/run-artifact evidence: README presents `history.jsonl` file sets and
    workspace candidates as recoverable experiment artifacts, which implies the
    content until `materialize()` raises raw `TypeError`.
    history workspace records are write-side artifacts and not a fully
  - README/run-artifact evidence: README says `best.py` is the primary-file
    compatibility view and `best_workspace/` contains the complete best
    candidate file set. That implies both artifacts represent the same
    `Program.workspace().code` was `x = "workspace"`. The CLI artifact writer
    wrote `best.py` with the legacy text and `best_workspace/main.py` with the
    and README/run-artifact docs now describe `best.py` as a compatibility view
    derived from the same candidate file set as `best_workspace/`.
  - README/run-artifact evidence: docs describe history rows as carrying
    docs, or qualify README/problem-format/run-artifact wording so
  - Required result: update README/problem-format/run-artifact docs to state
    run-artifact docs, and architecture docs now describe selected context
    docs, architecture docs, and run-artifact docs state that leading/trailing
    per-plugin score provenance and plugin artifact/provenance hooks, which can
    score, context, artifact, and manifest records, or document that duplicate
    `on_evaluated`, `run_artifacts_metadata`, and `on_generation_end` can raise
    and `run_artifacts_metadata()`. These hooks are behaviorally significant:
    artifact summaries returned by `run_artifacts_metadata()`.
  - Status: README now describes lifecycle plus metadata/artifact hooks, and
    `run_artifacts_metadata()` with their call points and manifest/history
    the hook boundary, or update README/plugin/run-artifact docs to warn that

- [x] Correct config-validation claims for seed and run path scalar fields.
  - Required result: either implement scalar validation and path normalization
    archive and modern `show` selection using `evaluation.is_valid`, which
    implies validity is a boolean gate.
    now require `program.evaluation["is_valid"] is True`; missing,
    non-boolean, and false validity values do not enter MAP-Elites. Modern
    `libreevolve show` selection also requires `evaluation.is_valid is True`.
  - Required result: either require exact boolean `True` before live archive
    `evaluation.is_valid is False` programs into MAP-Elites. A local proof
    `Program(evaluation={"is_valid": False}, fitness=1.0)`, reports
    `fitness=float("inf")`, `evaluation.is_valid == False`, and
    `selection_score: inf`; `ProgramDatabase.log()` then raised
    `metadata.archive_admission.admitted` and `evaluation.is_valid` for modern
    performance-like descriptor from `_selection_score(program)`, which uses
    `metadata.selection_score` when finite and falls back to `Program.fitness`
    config, and `apply_llm_feedback()` now records provider failures, malformed
  - Current evidence: `apply_llm_feedback()` records grader outcomes in
    `evaluation.metadata.llm_feedback`, and now also adds typed stage entries. A local
    `error="llm_feedback_discard"`, and `stages` now include an
    `llm_feedback:<name>` reviewer stage.
    `evaluation.metadata.llm_feedback`, can adjust metrics/fitness/validity,
    syntax errors synthesize only the primary metric plus `is_valid`. A local
    `{"score": -0.4, "is_valid": False}` for `no_diff_blocks` and
    `{"score": -0.2, "is_valid": False}` for syntax failure.
    feedback `weight = 0.01`, `apply_llm_feedback()` changed fitness from
    `0.2` to `5.23` and did not record `llm_feedback_failed`.
    `feedback_adjusted_fitness` while the raw primary validator metric remains
  - Current evidence: `apply_llm_feedback()` accepts any configured grader
    `updated.metrics[""]` and `name: ""` creating role metadata like
  - Current evidence: `apply_llm_feedback()` stores the provider
    `evaluation.metadata.llm_feedback`. A local proof returned a
  - Current evidence: `apply_llm_feedback()` catches grader exceptions and
    stores `str(exc)` under `evaluation.metadata.llm_feedback[].message`. A
    malformed YAML or scalar/list top-level `config.yaml` files could fail

- [x] Document finite-fitness archive-admission requirements or enforce them
    top-level candidate fitness is a finite comparable number.
    reject non-finite top-level fitness before MAP-Elites insertion.
    `libreevolve show` rejects non-finite history fitness rows with
  - Required result: either enforce finite top-level fitness before archive
    non-finite fitness, but it accepts other malformed displayed fields. A
    `Best fitness: 1.000000 (generation bad)` and exited successfully. A modern
    large elite list showed a lower-fitness same-cell program reported as
    MAP-Elites grid occupant remained the earlier higher-fitness program.
    selection score and fitness. A local proof added an older generation-0
    program with fitness `0.9` and then a newer generation-0 program with
    fitness `0.1`; `sample("recency")` returned the older high-scoring program.
  - README evidence: the inspect-results section prints "Best fitness" and
    present. It falls back to highest-fitness selection for legacy histories
    `evaluation.metadata.llm_feedback`, can adjust metrics/fitness/validity,
    feedback `weight = 0.01`, `apply_llm_feedback()` changed fitness from
    `feedback_adjusted_fitness` while the raw primary validator metric remains
    `fitness` stayed `0.8`. A second proof showed `metric: ""` creating
    feedback graders and plugin score composition as part of candidate
    plugin `on_evaluated()` score composition. A local proof with both enabled
    post-processing policy metadata marking LLM feedback and plugin score
    `runtime=5.0` and normalized `fitness=0.5`. README does not state that
    samples returning `score=1.0` produced aggregate `fitness=-0.1` and
    also needs to distinguish raw aggregate metrics from penalty fitness for
    invalid-sample and threshold-failure metric/fitness/stage-diagnostic
    and `min_score` threshold cases where top-level validity/fitness can
    primary fitness, MAP-Elites performance normalization, and strict
    stored `metrics.score == 999.0`, no error, and normalized fitness clamped
    `fitness=-0.1`, `is_valid=False`, and `error="domain_invalid"`.

- [x] Document prompt-history linkage exception for seed rows.
  - README/run-artifact evidence: run-artifact docs say program records in
    `history.jsonl` include `metadata.prompt_program_id` so candidates can be
    traced back to prompt-program events.
  - Previous evidence: seed evaluations were history records but were not produced
    by a prompt program. A local zero-generation run wrote a seed row with no
    `metadata.prompt_program_id`; `prompt_history.jsonl` contained only the
    prompt-template `add` event.
  - Required result: either add explicit seed/source provenance to history rows
    or update README/run-artifact docs to say prompt-program linkage applies to
    generated child candidates, while seed rows are raw baselines with separate
    source provenance.
  - Status: implemented and documented. Seed rows are explicitly marked as
    raw baselines with `metadata.candidate_type = "seed"` and no prompt id;
    generated rows are marked `candidate_type = "generated"` and include
    `metadata.prompt_program_id`. Run-artifact docs describe that distinction.


- [x] Document or fix duplicate evaluator-stage names.
    configured stage names before evaluator construction, with tests for both
  - Required result: either reject blank/duplicate stage names before startup,
  - Status: implemented for configured stage names and documented in
  - README/config evidence: README and configuration docs present stage names
    A local proof configured a stage named `syntax` and got two `syntax` stage
    `eval_stages=[{}, {"name": "stage_0"}]`; config validation accepted it and
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    samples. A local proof using a minimize primary metric `runtime` with two
    seeded samples returning `0.0` and `10.0` produced aggregated
    cannot request worst-case, quantile, all-samples-pass, or per-metric
    samples returning `score=1.0` produced aggregate `fitness=-0.1` and
    invalid sample sets. A third proof with `min_score: 0.5` and a validator
    and `min_score` threshold cases where top-level validity/fitness can
    diverge from aggregate raw metrics or local stage rows. Configurable
    validators with `samples`, `seeds`, retries, and stage context, which can
    not seed the validator subprocess RNG. A local proof with two samples using
    `eval_stages[].seeds[]`, or update README/config/run-artifact docs to say

- [x] Correct boolean config-validation claims for critique and meta-prompt
    `meta_prompt_evolution` and `critique_enabled` as boolean switches, and
    `meta_prompt_evolution` and `critique_enabled` to be booleans. CLI tests
  - Required result: either implement boolean validation for these switches
    `search_every` values, tests cover zero/negative/float/boolean inputs, and
    `metadata.archive_admission.admitted is True` and `evaluation.is_valid is
    `metadata.budget.consumed.evaluations == 2` and now records
    `metadata.budget.stop_reason == "max_evaluations"` before the manifest records
    `evaluation.metadata.llm_feedback`, no `metadata.score_composition`, and no
    `is_valid=False` while aggregate `metrics.score` remained `1.0`, so README
    returning `{"score": 0.2, "is_valid": True}` produced top-level
    `is_valid=False` and `stage_threshold_not_met` while `metrics.is_valid`
    first, or document the current fixed mean/all-booleans behavior and its
    that multi-sample aggregation uses fixed numeric means, boolean `all`, and
    returns `is_valid=True`; `min_score` is applied after retry selection. A
  - Previous evidence: strict validation covered declared keys, `is_valid`,
    `{"score": 999, "is_valid": True}` produced a valid evaluation with
    scalar metrics plus boolean `is_valid`. A local proof returning
    channel for evaluator-returned non-scalar data, or document that current
    artifacts while `evaluate()` itself must return scalar metrics only.
    state that `evaluate()` may return declared scalar metrics plus reserved
    structured output channels such as `program_output`;
    `malformed_metrics`; the actionable reason from `_validate_metrics()` is
    `{"score": 1.0, "is_valid": true}` while a spawned child inherited stdout
    and later printed `{"score": 0.0, "is_valid": false}`. The recorded result
    `fitness=-0.1`, `is_valid=False`, and `error="domain_invalid"`.
    scalar `seeds` values such as `Path` objects, booleans, and non-finite
  - Required result: after implementation, document the accepted scalar
    the shape and JSON-scalar limits of the stage context, and keep the shorter
    `async def evaluate(code): return {"score": 1.0, "is_valid": True}`
    `def evaluate(code): yield {"score": 1.0, "is_valid": True}` passed

- [x] Correct critique-prompt config type claims.
  - README/config evidence: `docs/configuration.md` documents
    README/configuration docs to state that the field is currently only
  - README-adjacent evidence: architecture/configuration caveats implied
  - Required result: document that plugin-specific schemas and constructor
  - README/docs evidence: plugin docs describe `deep_research` running every
  - Required result: either validate and document positive-integer cadence
  - Status: implemented and documented for current built-ins. `TTTRLPlugin`
  - README/docs evidence: CLI docs now describe `--plugins`, `--overwrite`, and
  - Required result: document that plugin names/specs are preflighted before
  - Status: implemented and documented. CLI startup validates plugin names
    identifiers, and README/run-artifact docs state that unknown plugin aliases
  - README/docs evidence: README and backend docs tell users to configure
  - Required result: after implementation, document that backend credentials
  - Status: implemented and documented. README, backend docs, and run-artifact
  - README/run-artifact evidence: docs say OpenAI/Anthropic credentials and
    `evolve()`, or narrow README/run-artifact wording to the CLI and warn
  - README/docs evidence: examples and docs describe seed programs, run
  - Required result: once implemented, document a seed-only/evaluate-only path
  - Status: implemented and documented. README and run-artifact docs now state

- [x] Document plugin preflight ordering and overwrite safety.
  - README/docs evidence: CLI docs now describe `--plugins`, `--overwrite`, and
    fail/overwrite run-artifact collision behavior, but they do not state
    whether plugin configuration is validated before cleanup of an existing run
    directory.
  - Previous evidence: the CLI prepared the run directory before resolving
    plugin names. A local proof with `--plugins missing --overwrite` failed
    with `Unknown plugin: 'missing'` after the existing `history.jsonl` in that
    run directory had already been removed. `Config.validate()` also accepted
    empty and whitespace-padded plugin strings because it validates only the
    list element type.
  - Required result: document that plugin names/specs are preflighted before
    any overwrite cleanup so invalid plugin configuration cannot fail after
    known run artifacts have already been cleaned up.
  - Status: implemented and documented. CLI startup validates plugin names
    before `prepare_run_directory()`, config validation rejects empty plugin
    identifiers, and README/run-artifact docs state that unknown plugin aliases
    fail before overwrite cleanup.


- [x] Document LLM backend preflight ordering and overwrite safety.
    OpenAI/Anthropic/Ollama backends and describe `--overwrite` as intentional
    run directory preparation. A local proof cleared `OPENAI_API_KEY`, supplied
    `--backends openai:gpt-4o-mini --overwrite --max-generations 0`, and the
    and constructor/capability settings are preflighted before overwrite
    are preflighted before overwrite cleanup for runs where mutation LLM calls
    backend construction are preflighted before overwrite cleanup for runs where
    seed, `run_collision_policy="overwrite"`, `max_generations=1`, and an
    fail/overwrite semantics but listed only the older history/prompt/manifest
    preflight collision checks and overwrite cleanup use.
    fails on known artifacts and `--overwrite` deletes known artifacts, but do
    not say what happens when the target run directory already contains
    `RUN_ARTIFACT_NAMES`. A local proof created `runs/probe/foreign.txt`,
    both `foreign.txt` and a new `manifest.json` in the same run directory.
    document that unknown files are preserved and outside the run contract;
    if preserved, surface them in manifest/runtime diagnostics so users do not
    unknown files in a run directory are preserved under both `fail` and
    `overwrite`, are not run-owned manifest artifacts, and put the directory
    for foreign files remain an implementation hardening gap in
    `--run-name` as selecting a matching run directory under `runs/`, and
    resolves the final run directory and rejects it when it would land outside
    symlink/junction run-directory escapes fail before `--overwrite` cleanup or
    symlink-capable platforms prove a linked run directory cannot delete an
    outside `history.jsonl` during overwrite startup.

- [x] Document `show` behavior for malformed or partially corrupt histories.
    warning, or are surfaced through a quarantine/repair workflow; and document
    quarantine streams as durable run artifacts that support inspection and
    detected or quarantined, what can be trusted after a killed process, and how
    JSONL streams are strict finite JSON but best-effort append logs, not
    distinguish this from `manifest.json` atomic replacement.
  - Current evidence: invalid failure-history appends are quarantined in
    `plugin_artifacts/` entries can cause overwrite startup to fail.
    `runtime.plugin_artifacts` and the `ttt_rl` export path, but the top-level
    directory tree omitted `plugin_artifacts/`.
    `runs/<run-name>/plugin_artifacts/ttt_rl/`, `TTTRLPlugin` writes
    and artifact/quarantine pointers before re-raising the original exception.
    pointers, and completed runs can include `runtime.plugin_artifacts` when
    local proof plugin wrote `plugin_artifacts/proof/proof.txt` and then
    `runtime.artifacts.plugin_artifacts` as an existing directory and omitted
    `runtime.plugin_artifacts`.
    sections, and aborted runs explicitly include artifact/quarantine pointers.
  - Required result: either implement temp-file/atomic replacement with invalid
    diagnostics to `manifest_invalid.jsonl`; tests cover non-serializable and

- [x] Document or fix evaluator-stage context type validation.
    context, and startup validation, which can imply bad stage configs fail
    context, including the raw `config` mapping. `Config.validate()` now
    context.
    `evaluate(code: str, workspace_path: str) -> dict`.
    calls `evaluate(code, workspace, stage)` when the function has three or
    more parameters. Configured-stage tests exercise that stage-context path.
    supported `evaluate(code, workspace_path, stage) -> dict` signature, define
    the shape and JSON-scalar limits of the stage context, and keep the shorter
    active evaluation-stage context for staged cascades.
    `validate.py` as a required problem contract, while run-artifact docs say
    `--overwrite` intentionally replaces known artifacts for a fresh run.
    `history.jsonl` was replaced, a new manifest/history row was written with
  - Status: implemented and documented. README/problem-format/run-artifacts
    cleanup or manifest creation.
  - README/run-artifact evidence: docs now say validator contracts are
    preflighted before overwrite cleanup or manifest creation, but that claim is
    invalid seed row and wrote `manifest.json` runtime metadata. The missing
    `AttributeError`, not as a pre-artifact task-setup diagnostic.
    docs broad, or narrow README/run-artifact wording to say the preflight

- [x] Document plugin cadence validation limits.
  - README/docs evidence: plugin docs describe `deep_research` running every
    `search_every` generations and `ttt_rl` exporting every `train_every`
    generations, but do not state valid ranges or current failure behavior.
  - Previous evidence: direct constructors accepted invalid cadence values. A
    local proof with `TTTRLPlugin(train_every=0).on_generation_end(1, None)`
    and `DeepResearchPlugin(search_every=0).on_generation_start(1, None)`
    raised `ZeroDivisionError` from hook modulo checks.
  - Required result: either validate and document positive-integer cadence
    fields through plugin schemas/constructors, or warn that direct plugin
    extension code must avoid non-positive cadence values until schema support
    exists.
  - Status: implemented and documented for current built-ins. `TTTRLPlugin`
    rejects invalid `train_every` values, `DeepResearchPlugin` rejects invalid
    `search_every` values, tests cover zero/negative/float/boolean inputs, and
    `docs/plugins.md` states both cadence fields must be positive integers.


- [x] Document backend role-label semantics and validation limits.
  - README/backend-doc evidence: backend examples can include descriptive role
    values such as `breadth` and `depth`, which can be read as AlphaEvolve-like
  - Current evidence: `LLMEnsemble` records call roles and backend metadata,
    but the backend metadata field `role` does not route mutation, critique,
    feedback, or meta-prompt calls. `Config._validate_backends()` only checks
    that `role` is a string; a local proof accepted `role: ""` and preserved
  - Required result: either implement and document concrete role routing or
    update README/backends/configuration docs to say backend `role` is
    that backend `role` labels are descriptive metadata only; routing uses
    numeric cost/latency/depth metadata, not role quotas or role-specific
    validation boundary: `role` only has to be a string, so custom or blank
    backends as returning mutation text into the ensemble, and README now
    A local proof with one primary leader and one latency leader returned the
    latency leader for `k=1` because `"latency"` sorts before `"primary"`.
    proof with declared `score` and `latency` metrics returned
    `updated.metrics[""]` and `name: ""` creating role metadata like
    OpenAI/Anthropic/Ollama backends and describe `--overwrite` as intentional
    `--backends openai:gpt-4o-mini --overwrite --max-generations 0`, and the
  - Previous evidence: `evolve()` built configured LLM backends before seed
  - README evidence: the supported-backends table named "Claude Opus 4.6" as a
    `backends: []` failed despite a `--backends ollama:llama3` override.
    `backends` values from `config.yaml`, and configuration docs state the
    exception metadata, phase/role, budget snapshot, history-written status,

- [x] Document or fix malformed provider-response handling.
  - README/backend-doc evidence: provider docs describe OpenAI/Anthropic/Ollama
    backends as returning mutation text into the ensemble, and README now
    describes retry/fallback telemetry at the ensemble boundary.
  - Current evidence: adapter response-shape validation is incomplete. A local
    OpenAI Responses mock with no message `output_text` returned an empty
    string, which would later look like a model-produced empty mutation. A
    Chat Completions mock with `message.content=None` returned `None`, and
    `LLMEnsemble.generate()` crashed with `TypeError` while constructing
    success telemetry before appending a failed-call record.
  - Required result: either implement structured provider-output validation
    first, or document that malformed/empty provider payloads are not yet
    consistently classified, retried, or persisted as LLM-call failures.
  - Status: documented. README and backend docs now state that malformed or
    empty provider response payloads are not yet consistently classified as
    failed provider calls, and that some adapter paths can return empty text or
    non-string content that fails later during mutation parsing or telemetry.
    The code-level provider response validation todo remains open.


- [x] Document that LLM feedback decisions are metadata, not stage outcomes.
    `evaluation.metadata.llm_feedback`, and now also adds typed stage entries. A local
    live in metadata.
    `evaluation.metadata.llm_feedback`, can adjust metrics/fitness/validity,
    interpreted with their error/stage metadata until a policy exists.
    `updated.metrics[""]` and `name: ""` creating role metadata like
    program files directly, `evolve()` stores `metadata.prompt` and
    `metadata.critique.prompt`, and `ProgramDatabase.log()` writes metadata
    `evaluation.metadata.llm_feedback`. A local proof returned a
    record containing provider-key-like placeholders in two metadata fields; the
    may contain raw prompt, code, metadata, and provider-response content.
    `record_repr = repr(record)` and can include raw prompt, code, metadata, or
    history, prompt summaries, artifact metadata, and future budget accounting.
    `metadata.archive_admission.admitted is True` and `evaluation.is_valid is
    `metadata.archive_admission` as durable views of candidate evaluation and
    non-serializable metadata, then `ProgramDatabase.log()` raised
    mutates `_failure_counts` and candidate `metadata.failure_record` before
    in-memory repetition counter and child metadata changed.
    document that in-memory failed-trial counters/metadata are best-effort and
    exception metadata, phase/role, budget snapshot, history-written status,

- [x] Document permissive LLM feedback numeric fallback.
    malformed/provider failures, which can imply non-JSON prose is safely
    basic secret redaction and that malformed feedback responses/provider
  - Current evidence: `apply_llm_feedback()` stores the provider
    provider-key-like placeholder in the grader JSON feedback text, and that
    record containing provider-key-like placeholders in two metadata fields; the
    may contain raw prompt, code, metadata, and provider-response content.
    provider-response content. The code-level redaction/data-retention work
    validators with `samples`, `retries`, `timeout_sec`, and `min_score`; the
    files now fail cleanly, while plugin-specific schemas and provider/model
    provider credentials are checked before cleanup starts.
    can occur; seed-only runs skip provider construction.
    but they do not explain whether baseline seed evaluation needs provider
    meant users could not rely on zero-generation runs as provider-free
    that writes seed history and best artifacts without requiring LLM provider
    constructing configured LLM provider clients.
    forwards configured provider model IDs and does not validate provider
    README and present examples as provider-specific model IDs.
    completed loop exits and may be absent after unhandled provider/plugin/
    `no_valid_programs` appears to be a fallback in `RunBudget.finish()` rather

- [x] Document LLM feedback grader order and discard behavior.
  - README/config evidence: optional feedback graders are described as able to
    add metrics or discard candidates, and config docs expose
    `include_invalid` as a per-grader control.
  - Current status: the earlier run-all behavior is superseded. Feedback
    graders now run in configured order; once a candidate is invalid, later
    graders are skipped unless `include_invalid: true`, and skipped graders are
    recorded as `llm_feedback_skipped_invalid` feedback records and stages.
    `feedback_adjusted_fitness` while the raw primary validator metric remains
  - Current status: feedback metric collision and empty-label gaps are
    superseded. Feedback metrics now reject evaluator metric collisions,
    reserved fields, duplicate feedback metrics, and unsafe or empty labels
    before provider calls.
    graders, but did not distinguish that from mutation prompts, critique
    `metadata.critique.prompt`, and `ProgramDatabase.log()` writes metadata
  - Status: README now warns that mutation/critique prompt history is persisted
  - README/run-artifact evidence: docs say LLM feedback grader prompts apply
  - Current evidence: `apply_llm_feedback()` stores the provider
    `raw_response` and parsed `feedback` field verbatim in
    `evaluation.metadata.llm_feedback`. A local proof returned a
    provider-key-like placeholder in the grader JSON feedback text, and that
    prompt inputs are redacted but grader `raw_response` and parsed `feedback`

- [x] Correct LLM feedback metric-collision documentation.
  - Previous evidence: feedback metrics could collide with evaluator metrics,
    reserved fields, and empty/default labels.
  - Status: superseded by implementation. Feedback metric collisions with
    evaluator metrics, reserved fields, and duplicate feedback metrics now
    produce `invalid_feedback_config` records before provider calls; README and
    run-artifact docs describe the enforced policy. The broader
    score/weight-calibration todo remains open.
    mistake mixed directories for clean reproducible runs.
  - Current evidence: `_aggregate_metrics()` averages numeric metrics across
    samples. A local proof using a minimize primary metric `runtime` with two
    multi-sample numeric metrics currently use mean aggregation, nor that users
    cannot request worst-case, quantile, all-samples-pass, or per-metric
    `is_valid=False` while aggregate `metrics.score` remained `1.0`, so README
    also needs to distinguish raw aggregate metrics from penalty fitness for
    `is_valid=False` and `stage_threshold_not_met` while `metrics.is_valid`
    invalid-sample and threshold-failure metric/fitness/stage-diagnostic
    diverge from aggregate raw metrics or local stage rows. Configurable

- [x] Document unredacted LLM feedback response persistence.
  - README/run-artifact evidence: docs say LLM feedback grader prompts apply
    basic secret redaction and that malformed feedback responses/provider
    failures are recorded. This can imply feedback records are covered by the
    same redaction policy as feedback prompt inputs.
    Island assignment cursor semantics are also not explicit: a local proof
    using `ProgramDatabase.admit()` showed a threshold-passing valid
    `not_improving_cell` candidate returning `admitted=False` on island `0`
    while still advancing the island cursor, so the next accepted candidate was
    assigned to island `1`. Inspiration `mixed` sampling is likewise not yet
    a principled mixture: `sample_diverse(strategy="mixed")` concatenates
    metric leaders, novelty order, selection order, and a random tail before
    truncation. A local proof with three occupied candidates returned the same
    deterministic prefix across five repeated calls (`metric_a` for `k=1`, and
    `metric_a, novel` for `k=2`), while only explicit `random` sampling varied.
    Plugin side effects can also corrupt the history record after evaluation:
    a local proof added
    `program.metrics["plugin_bad"] = inf` in `on_evaluated()`, after which
    `evolve()` raised `StrictJsonlError` while writing `history.jsonl`.
    Feedback response persistence is not covered by the feedback prompt
    redaction path: a local proof returned a provider-key-like placeholder
    from an LLM feedback grader, and the value remained in
    `evaluation.metadata.llm_feedback[].raw_response` and parsed `feedback`.
    Feedback-provider failure messages are also raw: a local proof raised
    `RuntimeError("feedback provider failed token=ghp_feedback_secret_1234567890")`,
    and `apply_llm_feedback()` stored the exact string under
    `evaluation.metadata.llm_feedback[].message`.
    Plugin prompt-context provenance is also not schema-validated before it
    enters candidate metadata: a local proof stored a Python `set` under
    `metadata.plugin_context[].metadata`; `ProgramDatabase.log()` raised
    `StrictJsonlError`, quarantined the candidate record, and wrote no accepted
    `history.jsonl` row. Top-level program fitness is now finite-checked before
    archive insertion through direct database/archive paths, and `show` rejects
    non-finite history fitness rows; future resume/checkpoint loading still
    needs to reuse the same predicate.
  - Required result: split persisted database fields so later analysis can tell
    whether a candidate changed a MAP-Elites behavior cell, was retained only in
    a global/auxiliary elite list, or was merely evaluated and logged; validate
    plugin-added metrics/metadata before they enter persisted program records;
    validate plugin prompt-context metadata at the hook boundary;
    reuse finite top-level fitness checks during future resume/replay;
    persist a real candidate insertion/admission sequence for recency sampling;
    define whether island round-robin assignment advances on attempted
    candidates, admitted candidates, or actual archive-state changes;
    define mixed inspiration sampling as either a documented deterministic

- [x] Document strict JSONL quarantine redaction limits.
  - README/run-artifact evidence: README describes invalid JSONL quarantine
    which can imply diagnostic quarantine records are similarly redacted.
  - Current evidence: `append_quarantine_record()` persists
    `record_repr = repr(record)`. A local proof wrote a non-finite history
    resulting `history_invalid.jsonl` kept both values verbatim in
  - Required result: either redact/hash/truncate quarantined record snapshots
    before persistence, or document that current invalid-record quarantine files
  - Status: README and run-artifact docs now describe `*_invalid.jsonl`
    quarantine files as unsanitized diagnostic snapshots that store
    history, prompt summaries, artifact metadata, and future budget accounting.
    with `Unknown plugin: 'missing'` after the existing `history.jsonl` in that
    command failed after printing the run banner; the existing `history.jsonl`
    was already gone and `manifest.json` existed.
    OpenAI backend replaced existing history, wrote an aborted runtime manifest,
    and `--max-generations 0` failed before seed history was written. This
    that writes seed history and best artifacts without requiring LLM provider
    fail/overwrite semantics but listed only the older history/prompt/manifest
  - Current evidence: `libreevolve/core/database.py::RUN_ARTIFACT_NAMES`
    includes candidate, failure, and prompt quarantine JSONL files plus
    both `foreign.txt` and a new `manifest.json` in the same run directory.
    if preserved, surface them in manifest/runtime diagnostics so users do not
    `overwrite`, are not run-owned manifest artifacts, and put the directory
    `history.jsonl` files.
  - Current evidence: `show` now streams `history.jsonl`, fails malformed JSON
    empty-history handling explicit, and requires exact modern validity via
    malformed history rows fail the whole inspection, are skipped with a
    warning, or are surfaced through a quarantine/repair workflow; and document
    requirement for current history records is now implemented and tested.
    `show` streams history rather than reading the whole file.

- [x] Clarify `llm_max_retries` versus provider-adapter internal retries.
  - README/config evidence: README and configuration docs describe
    `--llm-max-retries` / `llm_max_retries` as retry attempts on the same
    selected LLM backend before fallback/failure.
  - Current evidence: `LLMEnsemble.generate()` honors `llm_max_retries` at the
    ensemble layer, but `OpenAIBackend.generate()`, `AnthropicBackend.generate()`,
    and `OllamaBackend.generate()` each perform their own hard-coded three
    attempts with exponential backoff before returning an error to the
    ensemble. Therefore `llm_max_retries: 0` does not mean a single provider
    API attempt, and adapter attempts are not counted in telemetry or budgets.
  - Required result: either unify provider-adapter retries under the configured
    ensemble retry policy, or document the two retry layers clearly in README,
    backend docs, and configuration docs.
  - Status: README, backend docs, and configuration docs now state that
    `llm_max_retries` is an ensemble-layer retry after a backend raises, while
    OpenAI, Anthropic, and Ollama adapters still perform hard-coded internal
    three-attempt retry loops before exposing failure to the ensemble.


- [x] Document that LLM provider calls are not yet bounded by run timeouts.
  - README evidence: README and `docs/run-artifacts.md` describe
    `--max-runtime-seconds` as a wall-clock run budget checked by the runtime.
    request timeout/deadline. A slow mutation, critique, feedback, or
    can stop or write a timeout-specific artifact.
  - Required result: either implement provider-call timeouts/cancellation first
    or update README/backends/run-artifact docs so users understand that the
    current wall-clock budget is not an interrupt for in-flight LLM API calls.
  - Status: README, backend docs, run-artifact docs, and configuration docs now
    synchronous SDK calls without LibreEvolve request timeouts or cancellation
    deadlines, and that wall-clock run budgets are checked after provider calls
    `docs/configuration.md`, and `docs/run-artifacts.md` describe optional
    configured variants, prompt database seeds, and evolved templates before
  - Status: implemented and documented in run-artifact docs. Invalid
  - README/run-artifact evidence: docs say rejected meta-prompt mutations are
  - Missing from README: evolve-block markers, prompt sampler, multi-objective
  - README/problem-format evidence: docs explain that workspace seeds choose
    startup diagnostics block as config and artifact-preflight errors. CLI
    seeds as user-facing command errors before evolution starts.
    and timeout cleanup. That describes actual evaluator execution, but not…29361 tokens truncated…689:    correctly but recorded `eval_artifacts/<id>/report.txt`, which did not

- [x] Document declared metric bounds as normalization hints with clamp
  diagnostics.
  - README evidence: README describes metric directions/bounds, normalized
    primary fitness, MAP-Elites performance normalization, and strict
    evaluator-output validation against `metrics.yaml`.
  - Previous evidence: strict validation covered declared keys, `is_valid`,
    numeric type, and finiteness, but not whether returned values fell inside
    declared bounds. A local proof with `bounds: [0, 1]` and validator output
    `{"score": 999, "is_valid": True}` produced a valid evaluation with
    stored `metrics.score == 999.0`, no error, and normalized fitness clamped
    to `1.0`.
  - Required result: either enforce bound violations as invalid evaluator
    results, or document bounds as normalization hints and expose raw/clamped
    score provenance in run records so README users do not assume
    out-of-range validator outputs are rejected.
  - Status: implemented and documented. README now states bounds are
    normalization hints rather than hard validity constraints, and run-artifact
    docs describe `evaluation.metadata.metric_bound_diagnostics`.


- [x] Document evaluator timeout semantics for staged samples and retries.
  - README evidence: README describes configurable validator stages with
    timeouts, samples, seeds, retries, and thresholds, which can read as a
    per-stage budget.
  - Current evidence: `timeout_sec` is enforced per subprocess attempt. A local
    proof configured `timeout_sec=0.05`, `samples=2`, and `retries=1`; the
    evaluator ran two timeout attempts for each of two samples before returning
    `timeout`, so total stage wall time exceeded the configured timeout.
  - Required result: either document `timeout_sec` as a per-attempt validator
    timeout, or implement distinct per-attempt/per-stage budget controls before
    presenting staged cascades as budget-faithful AlphaEvolve-style evaluation.
  - Status: README, configuration, architecture, and run-artifact docs now state
    that `eval_stages[].timeout_sec` is enforced per validator subprocess
    attempt, not as a total sample or stage wall-clock budget. Current status:
    per-sample and per-stage wall-clock budget controls are now implemented;
    run-wide evaluator budget accounting remains open in code/paper/roadmap
    todos.


- [x] Document multi-sample evaluator aggregation limits.
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    multi-sample numeric metrics currently use mean aggregation, nor that users
    limits in README/run-artifact docs.
  - Status: README, configuration, architecture, and run-artifact docs now state
    that multi-sample aggregation uses fixed numeric means, boolean `all`, and
    aggregation/pass policies remain open in code/paper/roadmap todos.
    validators with `samples`, `seeds`, retries, and stage context, which can
  - Current evidence: stage seeds are passed in the JSON stage context but do
    `eval_stages[].seeds[]`, or update README/config/run-artifact docs to say
    primary fitness, MAP-Elites performance normalization, and strict
    normalization hints rather than hard validity constraints, and run-artifact
    presenting staged cascades as budget-faithful AlphaEvolve-style evaluation.
  - Status: README, configuration, architecture, and run-artifact docs now state
    per-sample/per-stage wall-clock budget controls are implemented, while
    run-wide evaluator budget accounting remains open in code/paper/roadmap
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    stored with each candidate and describes evaluator artifacts/stdout/stderr,
    which can be read as covering AlphaEvolve's program-output attachments.
    artifacts while `evaluate()` itself must return scalar metrics only.
  - Status: README, problem-format, architecture, and run-artifact docs now
    limited to stdout/stderr or opt-in copied evaluator artifacts.
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    evaluation records and document them, or narrow README/run-artifact wording
  - README/run-artifact evidence: README and run-artifact docs describe
  - README/run-artifact evidence: README says raw stdout/stderr diagnostics are
    stored with each candidate and prompt-visible summaries are bounded, but it
    does not distinguish bounded prompt summaries from unbounded persisted
    to configured artifacts instead.
  - Status: README, problem-format, architecture, and run-artifact docs now
    size-capped, while prompt-visible summaries are truncated separately. The
    docs direct large diagnostics to configured evaluator artifacts until

- [x] Superseded: document that evaluator-returned program outputs were not
  first-class yet.
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    stored with each candidate and describes evaluator artifacts/stdout/stderr,
    which can be read as covering AlphaEvolve's program-output attachments.
  - Previous evidence: the evaluator return contract accepted only declared
    scalar metrics plus boolean `is_valid`. A local proof returning
    `program_output: {"answer": 42}` from `evaluate()` produced
    `malformed_metrics`; the payload appeared only in raw stdout from the
    runner, not as structured queryable output metadata.
  - Required result: either implement a separate structured output/feedback
    channel for evaluator-returned non-scalar data, or document that current
    program-output evidence is limited to stdout/stderr and opt-in copied
    artifacts while `evaluate()` itself must return scalar metrics only.
  - Status: this entry records the earlier documentation-only gap. It is now
    superseded by the structured evaluator-output implementation: README and
    run-artifact docs describe reserved `outputs` / `program_output` channels
    that are strict-JSON validated, redacted, size-bounded, hashed, persisted
    under `evaluation.metadata.program_outputs`, and rendered into bounded
    prompt feedback.

- [x] Document or enforce feedback `llm_call` telemetry safety.
  - README/run-artifact evidence: feedback metadata is structured run evidence,
    so feedback call records must be safe for history, prompt feedback, and
    resume state.
  - Status: implemented and documented. Feedback `llm_call` telemetry from
    direct/custom LLM objects is normalized at the hook boundary into
    strict-JSON-safe, secret-redacted, bounded records with
    `telemetry_safety` diagnostics. README and run-artifact docs describe this
    policy alongside `llm_feedback:<name>` stage records.
  - Verification: focused feedback tests cover unsafe direct/custom LLM
    telemetry, redaction, bounding, strict JSON serialization, and stage
    metadata parity.

- [x] Document or enforce LLM feedback score/weight composition limits.
  - README/config evidence: optional LLM feedback graders can add metrics or
    discard candidates, so their score contribution needs bounded semantics.
  - Status: implemented and documented. Feedback scores, `weight`, and
    `min_score` are finite `[0, 1]` values; successful records preserve raw
    `score`, configured `weight`, and `weighted_delta`; README and
    run-artifact docs state that feedback-adjusted fitness affects top-level
    fitness/prompt reward while MAP-Elites `selection_score` remains based on
    declared evaluator metrics.
  - Verification: focused config/feedback tests cover invalid and valid
    score/weight/min-score policies plus persisted composition fields.


- [x] Document persisted evaluator stdout/stderr size limits or add them first.
  - README/run-artifact evidence: README says raw stdout/stderr diagnostics are
    stored with each candidate and prompt-visible summaries are bounded, but it
    does not distinguish bounded prompt summaries from unbounded persisted
    history fields.
  - Current evidence: evaluator stdout/stderr are redacted but stored in full
    in `EvaluationResult` and stage records. A local proof with a validator
    printing 200,000 characters produced `result.stdout` and stage stdout of
    length 200,034.
  - Required result: either implement configurable persisted stdout/stderr caps
    with truncation metadata, or document that current history records can
    contain full validator output and users should redirect large diagnostics
    to configured artifacts instead.
  - Status: README, problem-format, architecture, and run-artifact docs now
    state that persisted evaluator stdout/stderr is secret-redacted but not
    size-capped, while prompt-visible summaries are truncated separately. The
    docs direct large diagnostics to configured evaluator artifacts until
    persisted-output caps and truncation metadata are implemented.


- [x] Document the CI coverage boundary for docs-only changes.
  - README evidence: README shows a GitHub Actions `Tests` badge and asks
    contributors to run pre-commit plus non-integration pytest before
    submitting PRs, while the repository's AlphaEvolve-alignment truthfulness
    now depends heavily on README, ROADMAP, docs, paper index, and
    `docs/todo/*` accuracy.
  - Current evidence: `.github/workflows/tests.yml` ignores `docs/**`,
    `papers/**`, `README.md`, and `ROADMAP.md` for normal push/PR triggers.
    A docs-only change can therefore skip the workflow's secret scan and unit
    test jobs while the badge remains green from the last code-triggered run.
  - Required result: either change CI so doc/paper changes run appropriate
    validation, or update README/development docs to state exactly which local
    checks are required for docs/papers changes and that the badge does not
    imply docs-only validation when the workflow is skipped.
  - Status: README and development docs now state that the `Tests` workflow
    ignores docs, papers, README, and ROADMAP changes on normal push/PR
    triggers; a green badge does not validate skipped docs-only changes.
    Development docs list required local checks (`git diff --check`,
    pre-commit, non-integration pytest) and a manual paper-index/hash
    verification procedure until automated docs/papers CI exists.


- [x] Document validator timeout cleanup as best-effort until the flake is
    validator subprocess safety as implemented behavior.
    `test_timeout_terminates_validator_child_process` because the validator's
    supports configured validator stages with distinct entrypoints, timeouts,
    configurable validator stages, while keeping distributed evaluator workers
  - README evidence: README describes configurable validator stages with
    invalid sample sets. A third proof with `min_score: 0.5` and a validator
    validators with `samples`, `seeds`, retries, and stage context, which can
    not seed the validator subprocess RNG. A local proof with two samples using
  - Required result: either seed validator process/RNG state from
    seeds are validator-managed metadata and validators must consume
    declared bounds. A local proof with `bounds: [0, 1]` and validator output
    out-of-range validator outputs are rejected.
  - README evidence: README describes configurable validator stages with
  - Required result: either document `timeout_sec` as a per-attempt validator
    that `eval_stages[].timeout_sec` is enforced per validator subprocess
    stdout from validators/descendants can affect metric parsing until the
    in `EvaluationResult` and stage records. A local proof with a validator
    contain full validator output and users should redirect large diagnostics
    artifact metadata, validator environment metadata, retry attempts, or stage
  - Current evidence: `_evaluator_source_record()` reads each validator file
    manifest evaluator hashes read default and configured stage validator files
    validator stages with `validate_path`, `samples`, `seeds`, retries, stage
  - Current evidence: the validator runner receives JSON-serialized stage
    evaluator-stage validation covers all metadata that reaches the validator

- [x] Document unknown-file behavior in run directories or harden it first.
  - README/run-artifact evidence: README and run-artifact docs say startup
    fails on known artifacts and `--overwrite` deletes known artifacts, but do
    not say what happens when the target run directory already contains
    unrelated files.
  - Current evidence: a candidate can enter the live archive before its history
    row is accepted. A local proof admitted a valid program with
    non-serializable metadata, then `ProgramDatabase.log()` raised
    `StrictJsonlError`; `db.best()` still returned that unlogged candidate,
    `db.all_programs()` was empty, and no accepted `history.jsonl` existed.
  - Required result: either make archive admission/history logging
    transactional, or document that direct/extension-created invalid records can
    leave in-memory archive state ahead of accepted history until the database
    consistency work is implemented.

    `failure_history_invalid.jsonl`, but `ProgramDatabase.log_failure()` still
    mutates `_failure_counts` and candidate `metadata.failure_record` before
    the append succeeds. A local proof with a non-serializable `diff_error`
    raised `StrictJsonlError`, wrote no `failure_history.jsonl`, but left the
    in-memory repetition counter and child metadata changed.
  - Required result: either make failure-history logging transactional, or
    document that in-memory failed-trial counters/metadata are best-effort and
    can briefly diverge from accepted failure history after serialization
    failures.

  - Status: hardened and documented. Overwrite startup rejects linked known
    artifacts, including linked `best_workspace/`, `evaluator_artifacts/`, and
    `plugin_artifacts/`, before deleting any ordinary artifact. README,
    configuration, and run-artifact docs describe the policy.


- [x] Document JSONL append durability and recovery semantics.
    `history.jsonl`, `failure_history.jsonl`, `prompt_history.jsonl`, and
    quarantine streams as durable run artifacts that support inspection and
  - Current evidence: strict JSONL write validation is implemented, but
    `append_strict_jsonl()` writes directly to append-only files without fsync,
    whether JSONL streams are fsynced/crash-safe, how partial final records are
    that differs from the separate `manifest.json` atomic-write guarantee.
    JSONL streams are strict finite JSON but best-effort append logs, not
    crash-safe databases. They are not fsynced, checksummed, sequenced, spooled,
    distinguish this from `manifest.json` atomic replacement.
  - README/run-artifact evidence: README presents `history.jsonl` and
    `metadata.archive_admission` as durable views of candidate evaluation and
    `db.all_programs()` was empty, and no accepted `history.jsonl` existed.
  - README/run-artifact evidence: failure history is described as the durable
    `failure_history_invalid.jsonl`, but `ProgramDatabase.log_failure()` still
    raised `StrictJsonlError`, wrote no `failure_history.jsonl`, but left the
    outside `history.jsonl` during overwrite startup.
    `grpo_data.jsonl` and `grpo_data_invalid.jsonl` there, and tests cover the
    logging; `history.jsonl` existed, but `manifest.json` still contained only
    manifests currently expose only generic plugin-artifact directory pointers,
    `history.jsonl`, but `manifest.json.runtime` contained only `consumed`,
    status, while completed manifests rely on the run directory layout and
    `history.jsonl`, and `best=None`, while still creating
    `prompt_history.jsonl` and `manifest.json`.

- [x] Document seed-workspace symlink limits or harden loading first.
    multi-file seed workspaces under `initial_programs/`, which implies those
    symlinks and Windows junctions at top-level seed paths and within seed
    `docs/problem-format.md`, and architecture docs state that seed files and
    seeds as user-facing command errors before evolution starts.
  - Current evidence: seed failure rows include `admission_reason` and
    rejection metadata; keep seed/generated schema differences explicit.
    seed workspaces but did not mention that `<<<FILE ... >>>FILE` parsing is
    deterministic context selection, PDF extraction through `pypdf`,
    keep the limits explicit: context selection is deterministic local file
  - README evidence: the custom-problem section describes multi-file seed
  - Current evidence: `CausalPlugin._detect_factors()` now uses
  - Current evidence: `CausalPlugin.on_evaluated()` uses the immediately
    `self.FACTORS[0]` as a deterministic default when parsing fails or no
    factor pattern matches. `_ucb1_factor()` can choose randomly only if called
  - Required result: update plugin docs to describe deterministic no-match
    deterministic first configured factor, `loop_structure`, while factor

- [x] Document source/problem provenance symlink limits or implement policy.
    source/problem tree hashes as reproducibility provenance for run inputs.
  - Status: implemented and documented. Source/problem provenance traversal now
    records skipped entries with `reason: link_not_followed` in manifest
    provenance. README, architecture, and run-artifact docs describe the
    `566 passed, 6 skipped, 2 deselected`; users still should not read current
    imply docs-only validation when the workflow is skipped.
    score provenance in run records so README users do not assume
    can read as preserving provenance for every configured stage.

- [x] Document problem-provenance exclusion limits or refine them first.
  - README/run-artifact evidence: README and run-artifact docs describe
    manifest problem-tree hashes as reproducibility provenance for the problem
    state.
  - Status: refined and documented. `problem_provenance()` no longer excludes
    ordinary problem-owned directories named `runs`; tests prove changes under
    `problem/runs/fixture.txt` change the problem tree hash. The active
    generated run directory is passed into problem provenance from the
    effective run config and, when it resolves inside the problem tree, only
    that run root is skipped with `reason: excluded_output_root`. Excluded cache
    directories and skipped links are also recorded with reasons.


- [x] Document abnormal-run manifest behavior or implement finalization first.
  - README/run-artifact evidence: README and run-artifact docs describe
    `manifest.json` as the place for effective config, provenance, runtime
    stop reason, budget consumption, retrieval summaries, and plugin artifact
    summaries.
  - Previous evidence: `runtime` was written only when `evolve()` reached normal
    completion. A local proof patched the mutation LLM call to raise after seed
    logging; `history.jsonl` existed, but `manifest.json` still contained only
    startup `config`, `problem`, and `provenance` keys. Users inspecting the run
    would not see the abort reason or consumed budget in the manifest.
  - Required result: either implement abnormal-run finalization first, or make
    README/run-artifact docs explicit that `runtime` is guaranteed only for
    completed loop exits and may be absent after unhandled provider/plugin/
    evaluator/serialization failures.
  - Status: implemented and documented. Runs that abort after startup manifest
    creation now preserve a runtime record with `status: "aborted"`,
    exception metadata, phase/role, budget snapshot, history-written status,
    and artifact/quarantine pointers before re-raising the original exception.
    README and run-artifact docs describe aborted-run diagnostics.


- [x] Document missing runtime environment/package provenance in manifests.
  - README/run-artifact evidence: README says each run manifest records
    source-tree, problem-tree, evaluator, and plugin-module hashes.
  - Status: implemented and documented. Run manifests now include
    declared runtime dependencies. README, architecture, and run-artifact docs
  - README/run-artifact evidence: README says each run manifest records Git
    directory, ran a zero-generation seed evaluation, and produced a manifest
    README/run-artifact docs to state that current Git metadata describes the
  - README/run-artifact evidence: README and `docs/run-artifacts.md` describe
    the safe fields, or update README/run-artifact docs to clearly state that
    verbose dirty status paths may be written to `manifest.json` and should be
  - README/run-artifact evidence: docs describe source-tree and problem-tree
    manifest provenance records raw relative filenames for every included file.
    path would be persisted in run manifests independently of Git dirty status.
    and document the safe fields, or update README/run-artifact docs to state
    that source/problem manifest paths can contain raw local filenames and
  - README/run-artifact evidence: README and run-artifact docs describe
    manifest problem-tree hashes as reproducibility provenance for the problem
  - README/run-artifact evidence: README and run-artifact docs present manifest
    records skipped entries with `reason: link_not_followed` in manifest
    provenance. README, architecture, and run-artifact docs describe the
  - README/run-artifact evidence: README and run-artifact docs present
    skipped/read-failure diagnostics first, or document that current manifest
  - README-adjacent evidence: `docs/run-artifacts.md` lists
    does not use `no_valid_programs` and does not create failure history.
    mutation LLM. Rejected seeds are also recorded in `failure_history.jsonl`.
  - README/run-artifact evidence: README and run-artifact docs describe
    `show`/best artifacts around valid archived output, but they do not explain
    --overwrite`. It wrote invalid seed history and failure-history rows plus a
    manifest with `runtime.status: "completed"` and `stop_reason:
    current mixed contract: completed manifest, no best artifacts, and nonzero
  - README/run-artifact evidence: README and run-artifact docs describe LLM
    feedback graders and plugin score composition as part of candidate
    evaluation history, but do not distinguish generated candidates from the
    plugin `on_evaluated()` score composition. A local proof with both enabled
    and `max_generations=0` produced a seed history row with no
  - Required result: either apply feedback/plugin post-processing to seeds, or
    document seed history rows as raw evaluator baselines so users do not
  - Status: implemented and documented. Seed history rows are explicit raw
    post-processing policy metadata marking LLM feedback and plugin score
    `candidate_type = "generated"`, and `manifest.json` records the seed policy.
  - README/run-artifact evidence: docs describe timeout cleanup metadata and
  - Status: README, problem-format, architecture, and run-artifact docs now
  - README evidence: README shows a GitHub Actions `Tests` badge and asks
    now depends heavily on README, ROADMAP, docs, paper index, and
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    thresholds, samples, seeds, retries, stage context, and artifact policy.
    stayed `True` and the stage row still showed `passed=True`.
    limits in README/run-artifact docs.
  - Status: README, configuration, architecture, and run-artifact docs now state
    `eval_stages[].seeds[]`, or update README/config/run-artifact docs to say
    primary fitness, MAP-Elites performance normalization, and strict
    normalization hints rather than hard validity constraints, and run-artifact
  - Status: README, configuration, architecture, and run-artifact docs now state
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    stored with each candidate and describes evaluator artifacts/stdout/stderr,
    artifacts while `evaluate()` itself must return scalar metrics only.
  - Status: README, problem-format, architecture, and run-artifact docs now
    limited to stdout/stderr or opt-in copied evaluator artifacts.
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    evaluation records and document them, or narrow README/run-artifact wording
  - README/run-artifact evidence: README and run-artifact docs describe
  - README/run-artifact evidence: README says raw stdout/stderr diagnostics are
    history fields.
    with truncation metadata, or document that current history records can
    to configured artifacts instead.
  - Status: README, problem-format, architecture, and run-artifact docs now
    docs direct large diagnostics to configured evaluator artifacts until
  - README/run-artifact evidence: README and run-artifact docs describe staged
    evaluators, per-stage artifacts, and structured evaluation records, which
    metadata listed only the final `hard` stage and its `hard.txt` artifact.
    artifact metadata, validator environment metadata, retry attempts, or stage
    update README/configuration/run-artifact docs to state that current stage
    artifact metadata is complete for the final returned stage or failed stop
  - README/run-artifact evidence: README and run-artifact docs say manifests
    manifest evaluator hashes read default and configured stage validator files
    `validate.py` as a required problem contract, while run-artifact docs say
    `--overwrite` intentionally replaces known artifacts for a fresh run.
    `history.jsonl` was replaced, a new manifest/history row was written with
  - Status: implemented and documented. README/problem-format/run-artifacts
    cleanup or manifest creation.
  - README/run-artifact evidence: docs now say validator contracts are
    preflighted before overwrite cleanup or manifest creation, but that claim is
    `run_collision_policy="overwrite"`, an existing `history.jsonl`, and a
    `validate.py` missing `evaluate()` replaced the old history with a new
    invalid seed row and wrote `manifest.json` runtime metadata. The missing
    `AttributeError`, not as a pre-artifact task-setup diagnostic.
    docs broad, or narrow README/run-artifact wording to say the preflight

- [x] Document context symlink/path-escape boundary or harden it first.
  - README evidence: README frames `context/` as optional problem-local prompt
    context, which can imply the rendered content is confined to that tree.
  - Status: hardened and documented. The context loader now rejects symlinks
    and Windows junctions at `context/`, linked `context.yaml` / `context.yml`
    manifests, and all recursive context entries before selection or reading.
    README, architecture, and problem-format docs state that prompt context
    symlink rejection where supported, linked manifest rejection where
    labels for manifests, history, prompts, and downstream analysis.
    best-effort extraction and can ignore surrounding prose or malformed
    also includes an explicit replacement `PRIMARY`, or document the sorted
    rendered parent programs, inspiration programs, context, and evaluator
    document that candidate/context text containing markdown fences and
  - Current evidence: score-composition entries and manifest plugin provenance
    two entries named `DeltaPlugin`, and manifest provenance recorded two
    score, context, artifact, and manifest records, or document that duplicate
    manifest startup because the object lacked `on_generation_start`.
    `on_generation_start`, `build_extra_context`, `prompt_context_metadata`,
    `build_extra_context()` raises `RuntimeError("plugin context failed")`
    with no observations, but `build_extra_context()` returns no guidance when
    `on_generation_start()`, `build_extra_context()`, `on_evaluated()`, and
  - Current evidence: `PluginBase` also defines `prompt_context_metadata()`
    the loop records prompt-context attribution from
    `prompt_context_metadata()`, and completed manifests include plugin
    artifact summaries returned by `run_artifacts_metadata()`.
    `docs/plugins.md` lists `prompt_context_metadata()` plus
    `run_artifacts_metadata()` with their call points and manifest/history

- [x] Document context provenance limits, not just supported context knobs.
  - README/docs evidence: `docs/problem-format.md` says the loader records
    source hashes and that source records are persisted in `manifest.json` for
    run provenance, while README does not yet explain the exact boundary.
  - Current evidence: `manifest.json` persists only selected
    `problem.context_sources`. It does not include the `context.yaml` file
    hash, effective include/exclude rules, skipped or excluded files, or
    unsupported-extension diagnostics, so the full context selection decision
    cannot be reconstructed from the manifest alone. The loader now rejects
    unsupported typo keys such as `includes:` and duplicate `context.yaml` /
    `context.yml` manifests before source selection.
  - Required result: update README/problem-format/run-artifact docs to state
    that current context provenance covers selected sources only until context
    manifest policy and skipped-source diagnostics are persisted.
  - Status: implemented and documented. README, problem-format docs,
    run-artifact docs, and architecture docs now describe selected context
    records plus `problem.context_policy`, including manifest hash, effective
    include/exclude/max-char rules, selected/skipped counts, and hashed
    diagnostics for unsupported, not-included, and excluded files. They also
    keep the limits explicit: context selection is deterministic local file
    policy, not semantic ranking, global prompt packing, or exact PDF
    page-span citation for truncated excerpts.


- [x] Document problem-local `context.yaml`, PDF context ingestion, and current
  context-selection limits in the README custom-problem section.
  - README evidence: the custom-problem tree shows only
    `context/optional_notes.md` and does not mention that `load_problem()` now
    accepts `.txt`, `.md`, `.py`, and `.pdf` files recursively, supports
    optional `context.yaml` / `context.yml` include/exclude patterns plus
    `max_chars_per_source`, and records source hashes/extraction spans for
    prompts/manifests.
  - Current evidence: `libreevolve/problems/loader.py` implements recursive
    deterministic context selection, PDF extraction through `pypdf`,
    citation-style metadata, and first-span character truncation; the
    architecture and configuration docs describe that behavior more fully.
    The citation metadata has a PDF-specific caveat: page ranges are recorded
    as full-document ranges from extraction, not the page span of the rendered
    first-character excerpt, and prompt headers currently omit page fields.
  - Required result: update README's custom-problem example and caveats to
    show the supported context file types and `context.yaml` knobs, while
    clearly stating that large PDFs/text are still first-span truncated rather
    than semantically ranked or summarized, and that prompt-visible PDF page
    citations are not exact until citation-span tracking is hardened.
  - Status: implemented and documented. README's custom-problem tree now shows
    optional `context.yaml` and PDF context. README states the context boundary,
    selection-policy manifest provenance, exact preservation for UTF-8 text
    context, extracted-PDF context behavior, prompt-visible PDF excerpt page
    spans, and the remaining limits: first-span extraction, no semantic
    ranking, and no global prompt packing.


- [x] Document primary-file identity fallback or enforce strict workspace
  primary validation first.
  - README/problem-format evidence: docs explain that workspace seeds choose
    `main.py`, `seed.py`, or the first `.py` file as the primary file, and
    `best.py`/legacy validators use that primary-file compatibility view.
  - Current evidence: lower-level `CandidateWorkspace` accepts an explicit
    missing `primary_file` and silently rewrites it to the first sorted file. A
    local proof passed `primary_file="missing.py"` with only `helper.py` in
    `files`; the resulting workspace used `helper.py` with no diagnostic.
  - Required result: either make constructor/deserialization strict before
    documenting primary-file identity as reliable, or document the current
    fallback behavior and its limits for future resume/history replay.
  - Status: implemented and documented. `CandidateWorkspace` now rejects
    explicit missing primary files for non-empty workspaces, and `from_dict()`
    applies the same check. README, problem-format docs, and architecture docs
    state that `primary_file` must name a present file.


- [x] Document serialized workspace schema limits or validate them first.
  - README/run-artifact evidence: README presents `history.jsonl` file sets and
    workspace candidates as recoverable experiment artifacts, which implies the
    persisted shape is a typed source-file record.
  - Current evidence: `CandidateWorkspace.from_dict()` coerces persisted keys,
    contents, and `primary_file` with `str()`. A local proof accepted
    list-valued file content and integer path data, producing source text and
    paths that did not exist in the original record shape; malformed
    non-mapping `files` raises `AttributeError`. Direct
    `CandidateWorkspace(files={"main.py": 123})` also preserves the non-string
    content until `materialize()` raises raw `TypeError`.
  - Required result: either implement strict deserialization diagnostics before
    documenting workspace records as replay/resume-ready, extend the same
    content typing to direct workspace construction, or document that current
    history workspace records are write-side artifacts and not a fully
    validated restore format.
  - Status: implemented and documented. `CandidateWorkspace.from_dict()` now
    rejects malformed records instead of coercing them with `str()`, and direct
    construction requires mapping-shaped string path/string content file sets.
    Docs describe the typed text-workspace invariant.


- [x] Clarify that the paper PDFs are local cache artifacts, not committed
  - README evidence: README and `docs/run-artifacts.md` describe
    `docs/configuration.md`, and `docs/run-artifacts.md` describe optional
    candidate workspaces and `best_workspace/` as complete recovered artifacts.
  - Current evidence: the CLI best exporter removes `best_workspace/` before
    the CLI-cleaned `best_workspace/` path currently provides a clean export.
    workspace into `evaluator_artifacts/` with hashes and provenance metadata.
  - Status: README now tells users that configured matching artifacts are
    workspace are copied to `evaluator_artifacts/` and that non-matching files
    artifact root `<tmp>/run/nested/eval_artifacts` copied the file but
    recorded `eval_artifacts/<id>/report.txt`, which did not resolve from the
    workspace candidates as recoverable experiment artifacts, which implies the
    history workspace records are write-side artifacts and not a fully
    compatibility view and `best_workspace/` contains the complete best
    candidate file set. That implies both artifacts represent the same
    wrote `best.py` with the legacy text and `best_workspace/main.py` with the
    derived from the same candidate file set as `best_workspace/`.
    `on_evaluated`, `run_artifacts_metadata`, and `on_generation_end` can raise
    and `run_artifacts_metadata()`. These hooks are behaviorally significant:
    artifact summaries returned by `run_artifacts_metadata()`.
    `run_artifacts_metadata()` with their call points and manifest/history
    plugin artifacts, which can imply the `runtime.plugin_artifacts` entries
    `run_artifacts_metadata()` returns. A local proof plugin class
    writes under the active run's `plugin_artifacts/ttt_rl/` directory and
    under the active run's `plugin_artifacts/ttt_rl/` directory, which can imply
    and exposed that outside path in `run_artifacts_metadata()`.
    user-managed external artifacts whose provenance must be inspected in the
    the active run's `plugin_artifacts/ttt_rl/` directory and links export
    GRPO-style training data under run artifacts with manifest-linked counts,
    run artifacts and prompt-program scoring, which can imply it is sufficient
    island's `elite_archive()`. This is not visible in run artifacts because
    and run artifacts with archive-admission events, which can imply island
    The run artifacts do not persist an insertion/admission sequence that would
    `best.py`/`best_workspace/` from the original run for exact archived output
    `best_workspace/` from the original run for archived best output.
    `prompt_history.jsonl`, `failure_history.jsonl`, or `best_workspace/`.
    `best_workspace/` as the archived best output from a run, which implies the
  - Current evidence: `_write_best_artifacts()` writes `best.py` before
    materializing `best_workspace/`. A local proof with host-colliding best
    left the new `best.py` on disk, and removed the prior `best_workspace/`.
    diagnostics, or document that current CLI best artifacts are best-effort
  - README/run-artifact/config evidence: `docs/run-artifacts.md` and
    skipped path in `skipped_files=[{'path': ...}]`. If all artifacts are
    skipped, `_render_artifacts()` returns no warning at all.
    known run artifacts have already been cleaned up.
    replacement of previous run artifacts, but they do not state whether
    that writes seed history and best artifacts without requiring LLM provider
    `evaluator_artifacts/` and `plugin_artifacts/`.
    fails on known artifacts and `--overwrite` deletes known artifacts, but do
    `overwrite`, are not run-owned manifest artifacts, and put the directory
  - README/run-artifact evidence: README and `docs/run-artifacts.md` present
  - README/run-artifact evidence: README and `docs/run-artifacts.md` describe
    quarantine streams as durable run artifacts that support inspection and
  - README/docs evidence: README and `docs/run-artifacts.md` describe
    LibreEvolve artifacts inside the selected run directory and already state
    artifacts by name. A local Windows junction proof made
    `runs/demo/evaluator_artifacts` point at a sibling `outside/` directory;
    the run directory. Docs do not warn that linked known artifacts are a
    directories and that linked `best_workspace/`, `evaluator_artifacts/`, or
    `plugin_artifacts/` entries can cause overwrite startup to fail.

- [x] Document text-context whitespace normalization or preserve it first.
  - Current evidence: `_read_text_context()` strips leading/trailing whitespace
    whitespace-sensitive snippets should be placed where trimming cannot alter
    whitespace and blank lines are preserved for `.txt`, `.md`, and `.py`
    `evaluate()` returns a dict with all metric names.
  - README/config evidence: prompt reward bounds are presented as a normal
    bounds are rejected before reward normalization.
    `prompt_reward_bounds`, but direct `PromptDatabase(...,
    reward_bounds=(1.0, 1.0))` still crashes in `record_result()` with
    `ZeroDivisionError`; `reward_bounds=(2.0, 1.0)` silently changes the
    normalization direction.
  - Required result: either validate bounds at the prompt database/resume
    imply every candidate row has a complete declared metric vector.
    syntax errors synthesize only the primary metric plus `is_valid`. A local
    feedback metric collision and empty-label concerns are superseded by
    boundary validation that records invalid feedback configs before provider
    calls.
    empty and whitespace-padded plugin strings because it validates only the
    samples. A local proof using a minimize primary metric `runtime` with two

- [x] Document or fix `Program.code` versus workspace-file divergence.
  - README/run-artifact evidence: README says `best.py` is the primary-file
    compatibility view and `best_workspace/` contains the complete best
    `Program.workspace().code` was `x = "workspace"`. The CLI artifact writer
    wrote `best.py` with the legacy text and `best_workspace/main.py` with the
    workspace text.
    and README/run-artifact docs now describe `best.py` as a compatibility view
    derived from the same candidate file set as `best_workspace/`.
    `files` plus `primary_file` for workspace candidates, which implies the
    shape to `history.jsonl`, even though `program.workspace()` would
  - Current evidence: `apply_workspace_mutation()` accepts responses that
    evolve-block markers for top-level `.py` seeds and seed workspace files,
  - README/problem-format evidence: README describes multi-file workspaces and
  - Current evidence: `apply_workspace_mutation()` currently accepts multiple
    left the workspace unchanged; reversing the order returned `err=None` and
    workspace therefore succeeds or fails based on section order.
  - Current evidence: `apply_workspace_mutation()` silently reassigns
    current primary. A local proof deleted `main.py` from a workspace with
    workspaces and file-section edits, so it should state how topology changes
  - Current evidence: `apply_workspace_mutation()` supports command file
  - Required result: keep README aligned with current workspace topology
  - Current evidence: `apply_workspace_mutation()` compares a missing file's
    files and document the exact syntax, or state that workspace candidates are
  - Current evidence: `apply_workspace_mutation()` silently ignores non-empty
    file that contains evolve blocks. `apply_workspace_mutation()` sends the
    examples and tests should cover both one-block and multi-block workspace
    workspace whose primary file was `notes.txt` rendered the candidate in a
    prompt rendering preserves file type faithfully for every workspace shape.

- [x] Clarify evolved prompt-template channel retention behavior.
  - README-adjacent evidence: README/configuration/architecture docs describe
    prompt programs as selected, scored, logged, and optionally mutated, and
    say configured/evolved prompt templates are validated against the
    placeholder schema.
  - Previous evidence: syntax/schema validation only required `{task}`. A local
    proof admitted a mutated prompt template `Task only: {task}`, which omitted
    `{parent_code}` and `{mutation_instructions}` while still entering the
    prompt database.
  - Required result: either implement semantic placeholder-retention rules
    first, or document that current validation prevents malformed placeholders
    but does not guarantee evolved prompts retain code, feedback, inspiration,
    or mutation-format sections.
  - Status: implemented and documented. Mutated prompt templates are now
    checked against their parent prompt program and rejected if they drop
    parent placeholders, so evolved prompts cannot silently remove existing
    code, feedback, inspiration, or mutation-format channels. Configured seed
    templates remain intentionally flexible for backward compatibility.
    Architecture and configuration docs now state the parent-placeholder
    retention rule alongside schema and dry-run format validation.


- [x] Document and enforce run-name path confinement.
    `--run-name` as selecting a matching run directory under `runs/`, and
    `docs/configuration.md` describes `problem_name` as the final run
  - Current evidence: `Config.validate()` rejects unsafe `problem_name` and
    `--run-name` values before artifact preparation, and runtime startup now
    resolves the final run directory and rejects it when it would land outside
    symlink-capable platforms prove a linked run directory cannot delete an
    LibreEvolve artifacts inside the selected run directory and already state
  - Current evidence: the resolved run directory itself is checked, but
    the run directory. Docs do not warn that linked known artifacts are a
    `runs/<run-name>/plugin_artifacts/ttt_rl/`, `TTTRLPlugin` writes
    `--run-name`, and `--overwrite`, but omits `--max-evaluations`,
    status, while completed manifests rely on the run directory layout and
    generated run directory is passed into problem provenance from the
    remove unreachable or misleading stop-reason descriptions.
    --max-generations 0 --backends ollama:llama3 --run-name audit_smoke_goal
    channel and document stdout as diagnostics only, or document that trailing
    preparing the run directory. A local proof with `validate.py` missing

- [x] Correct docs that imply all unsafe candidate paths are rejected.
  - README/docs evidence: README and problem-format docs say file-section
    paths are accepted when normalized safely and unsafe paths are rejected.
  - Current evidence: `normalize_candidate_path()` rejects traversal,
    drive-letter, and colon-component paths, but silently strips leading `/`.
    POSIX-style absolute-looking paths such as `/new.py` are accepted and
    materialized as relative `new.py`. It also accepts control-character paths
    through the direct workspace API: a local proof constructed
    `CandidateWorkspace({"bad\nname.py": "x=1\n"}, "bad\nname.py")`
    successfully, then `materialize()` failed with `OSError: [Errno 22]
    Invalid argument` on Windows.
  - Required result: after implementation, document that candidate paths are a
    strictly relative, host-safe grammar and include leading-slash plus
    control-character examples in path-safety tests/docs; until then, avoid
    broad "all unsafe paths rejected" wording.
  - Status: implemented and documented. README, problem-format, and
    architecture docs now state the accepted relative path grammar and the
    rejected classes: traversal, drive-letter, colon-component, POSIX absolute,
    UNC-style leading-backslash, ASCII control characters, Windows-reserved
    device names, wildcard/quote/pipe characters, and trailing spaces or dots.
    Candidate tests cover leading-slash, control-character, host-invalid, and
    reserved-name rejection.


- [x] Add live retrieval provenance to prompt/plugin context work.
  - Evidence: `DeepResearchPlugin` injects live arXiv search summaries into
    prompts. It now records bounded provider/query/status/timestamp/result
    length/synthesis-hash retrieval events plus arXiv source IDs/URLs,
    timestamps/authors, and summary hashes in candidate plugin-context
    metadata, while full result payloads, ranking provenance, source-content
    hashes, and richer artifact-level retrieval records remain open. Completed
    manifests include bounded `runtime.retrieval` summaries.
  - Current roadmap gap: context-source provenance covered problem-local files,
    while plugin-provided external context also needs reproducible query,
    result, citation, failure, and manifest records.
    summaries; and add tests for multi-stage passing runs, early stops, sampled
    stages, retries, and per-stage artifacts.


- [x] Capture validator-generated artifacts before temporary workspaces are
  deleted.
  - Spec evidence: AlphaEvolve stores programs with evaluation outputs, and
    benchmark-style tasks such as packing, scheduling, and kernels often need
    construction files, plots, traces, logs, or compiled artifacts to inspect
    and compare results.
  - Status: implemented as opt-in candidate-workspace artifact copy-out.
    `Config` now exposes `evaluator_artifact_include`,
    `evaluator_artifact_exclude`, `evaluator_artifact_max_files`, and
    `evaluator_artifact_max_bytes`, plus default-on
    `evaluator_artifact_redact_secrets`, with per-stage overrides via
    `artifact_include`, `artifact_exclude`, `artifact_max_files`, and
    `artifact_max_bytes`, and `artifact_redact_secrets`. Matching files are
    copied to `runs/<run>/evaluator_artifacts/<collection_id>/...` before the
    temporary workspace is deleted. Evaluation metadata records effective
    patterns, limits, skipped files, copied file paths, source/stored byte
    counts, SHA-256 hashes of stored content, redaction status, stage name,
    sample index, and attempt. Tests prove validator-created files are copied,
    bounded, hashed, retained after subprocess cleanup, can use stage-specific
    artifact policy, and redact secret-like text artifacts by default with an
    explicit stage opt-out.
  - Remaining gap: files outside the candidate workspace are not collected, and
    richer artifact schemas remain future work.


- [x] Validate task descriptions as non-empty problem contracts.
  - Spec evidence: AlphaEvolve-style task setup depends on a concrete problem
    statement and optimization objective being present in the prompt; an empty
    task makes candidate generation and later experiment provenance ambiguous.
  - Current evidence: `load_problem()` now reads and strips
    `task_description.txt`, then rejects empty content with a path-aware
    `ValueError`. A loader regression test covers whitespace-only task files.
  - Required result: reject missing or empty/whitespace-only task descriptions
    with a path-aware problem-load diagnostic before config construction or
    run-directory preparation; update problem-format docs and tests for valid,
    missing, and empty task files.
  - Status: implemented for empty/whitespace-only task files. Missing task
    files already fail through the file read path; CLI normalization for
    problem-load failures remains tracked separately.


- [x] Normalize CLI diagnostics for problem-load failures.
  - Spec evidence: AlphaEvolve-style task setup should fail early with
    actionable diagnostics before a run starts, especially for malformed
    metrics, missing seeds, invalid task files, or context-loading failures.
  - Current evidence: `libreevolve.cli.run()` now calls `load_problem()` inside
    the startup diagnostics block and converts `FileNotFoundError` /
    `ValueError` into `ClickException` messages. CLI tests cover malformed
    `metrics.yaml`, missing `validate.py`, empty `task_description.txt`, no
    seed programs, and invalid `context/context.yaml` schema before `evolve()`
    is called.
  - Required result: wrap problem loading in Click diagnostics that preserve
    path-aware loader messages, remove or make reachable duplicate no-seed
    checks, and add CLI tests for malformed metrics, missing/empty task
    descriptions, no seed programs, context manifest errors, and missing
    validator files.
  - Status: implemented for malformed metrics, missing validator, empty task,
    no seed programs, and context manifest schema errors.


- [x] Add run-wide compute-budget accounting to runtime work.
  - Evidence: AlphaEvolve Section 2.6 describes maximizing evaluated ideas
    under a total computation budget, and paper ablations compare progress by
    fraction of consumed budget.
  - Current roadmap gap: the roadmap mentioned per-stage budgets and
    deterministic accounting, but did not require whole-run wall-clock,
    LLM-call, token, cost, evaluator-second, sample/retry counters, stop
    reasons, or equal-budget ablation reporting.
  - Status: implemented for local synchronous generation/evaluation budgets:
    `max_evaluations`, `max_evaluator_seconds`, `max_runtime_seconds`,
    per-candidate `metadata.budget`, and completed-manifest `runtime` stop
    summaries. LLM-call/token/cost, stage-sample/retry, accelerator, async
    queue, and equal-budget benchmark reporting remain open. Startup
    no-valid-parent accounting is now fixed: all-invalid seed runs stop with
    `no_valid_programs`, leave generation counters at zero, and do not build a
    mutation LLM.
  - Required result: make budget schemas, counters, stop reasons, manifest
    summaries, and budget-fraction benchmark reporting explicit runtime work,
    including startup/no-parent accounting.


- [x] Persist archive admission outcomes per program.
  - Spec evidence: AlphaEvolve's database stores explored programs with scores
    and enough evolutionary state to resurface useful ideas; auditing a run
    now includes bounded structured `outputs` / `program_output` metadata
    alongside declared scalar metrics. Queryable persisted feedback and
    lineage-aware sampling remain open.
    `metadata.score_composition` stores per-plugin score adjustments, and
    archive admission is now gated by evaluator/feedback validity as well as
    final composed fitness. Full MAP-Elites cell/island snapshots plus
    migration events are not persisted. Population config semantics now define
    `migration_ratio=0.0` as selecting no migrants; positive migration ratios
    still round up to at least one migrant from a non-empty island. Repeated
    migration is not idempotent: a local proof with one program and two islands
    produced four copies of the same `Program.id` in each island's
    `elite_archive()` after three migrations, even though each island had only
    one occupied grid cell.
    Admission semantics still conflate MAP-Elites grid entry/replacement with
    auxiliary elite-list retention: a local proof with one cell and a large
    elite list produced `admitted=True`, `reason="elite_only"`, and
    `entered_cell=False` for a lower-scoring same-cell candidate while the grid
    occupant did not change. A follow-up proof showed that the `elite_only`
    candidate remains in `elite_archive()` but is absent from the occupied-cell
    pools used by parent/inspiration sampling, so the persisted admitted flag
    does not mean the candidate changed the behavior map or will be resurfaced
    by the current sampling policies. Recency sampling is also
    generation-based rather than true database insertion recency: a local proof
    added an older high-scoring generation-0 program and then a newer
    low-scoring generation-0 program, and
    `IslandModel.sample("recency")` returned the older candidate because score
    broke the generation tie. There is no persisted insertion/admission
    sequence for seeds, same-generation batches, or future replay/resume.
    Island assignment cursor semantics are also not explicit: a local proof
    using `ProgramDatabase.admit()` showed a threshold-passing valid
    `not_improving_cell` candidate returning `admitted=False` on island `0`
    while still advancing the island cursor, so the next accepted candidate was
    assigned to island `1`. Inspiration `mixed` sampling is likewise not yet
    a principled mixture: `sample_diverse(strategy="mixed")` concatenates
    metric leaders, novelty order, selection order, and a random tail before
    truncation. A local proof with three occupied candidates returned the same
    deterministic prefix across five repeated calls (`metric_a` for `k=1`, and
    `metric_a, novel` for `k=2`), while only explicit `random` sampling varied.
    Plugin side effects can also corrupt the history record after evaluation:
    a local proof added
    `program.metrics["plugin_bad"] = inf` in `on_evaluated()`, after which
    `evolve()` raised `StrictJsonlError` while writing `history.jsonl`.
    Feedback response persistence is not covered by the feedback prompt
    redaction path: a local proof returned a provider-key-like placeholder
    from an LLM feedback grader, and the value remained in
    `evaluation.metadata.llm_feedback[].raw_response` and parsed `feedback`.
    Plugin prompt-context provenance is also not schema-validated before it
    enters candidate metadata: a local proof stored a Python `set` under
    `metadata.plugin_context[].metadata`; `ProgramDatabase.log()` raised
    `StrictJsonlError`, quarantined the candidate record, and wrote no accepted
    `history.jsonl` row. Top-level program fitness is now finite-checked before
    archive insertion through direct database/archive paths, and `show` rejects
    non-finite history fitness rows; future resume/checkpoint loading still
    needs to reuse the same predicate.
  - Required result: split persisted database fields so later analysis can tell
    whether a candidate changed a MAP-Elites behavior cell, was retained only in
    a global/auxiliary elite list, or was merely evaluated and logged; validate
    plugin-added metrics/metadata before they enter persisted program records;
    validate plugin prompt-context metadata at the hook boundary;
    reuse finite top-level fitness checks during future resume/replay;
    persist a real candidate insertion/admission sequence for recency sampling;
    define whether island round-robin assignment advances on attempted
    candidates, admitted candidates, or actual archive-state changes;
    define mixed inspiration sampling as either a documented deterministic
    cascade or a seeded weighted/stochastic policy with replay diagnostics;
    add a validated structured-output attachment channel for evaluator-returned
    non-scalar data without weakening the scalar metric contract; and define
    redaction/hash/retention policy for raw LLM feedback responses before they
    become database records or future prompt context. Also cover invalid-record

- [x] Document seed rows as raw evaluator baselines or post-process them.
  - README/run-artifact evidence: README and run-artifact docs describe LLM
    feedback graders and plugin score composition as part of candidate
    evaluation history, but do not distinguish generated candidates from the
    initial seed population.
  - Previous evidence: seed evaluations did not receive LLM feedback graders or
    plugin `on_evaluated()` score composition. A local proof with both enabled
    and `max_generations=0` produced a seed history row with no
    `evaluation.metadata.llm_feedback`, no `metadata.score_composition`, and no
    feedback LLM calls.
  - Required result: either apply feedback/plugin post-processing to seeds, or
    document seed history rows as raw evaluator baselines so users do not
    compare them directly to post-processed generated candidates without that
    caveat.
  - Status: implemented and documented. Seed history rows are explicit raw
    evaluator baselines with `metadata.candidate_type = "seed"` and
    post-processing policy metadata marking LLM feedback and plugin score
    composition as not applied. Generated candidates carry
    `candidate_type = "generated"`, and `manifest.json` records the seed policy.


- [x] Add language-agnostic candidate support or narrow the claim to Python.
  - Spec evidence: AlphaEvolve is described as being able to evolve code in any
    language.
  - Current evidence: `CascadeEvaluator.evaluate()` calls Python `compile()`
    and imports Python `validate.py` (`libreevolve/core/evaluator.py:31-38`).
  - Status: README, architecture, problem format, and roadmap now state the
    current Python-only/local-workspace scope as a deliberate divergence.
  - Required result: either introduce pluggable language runners and validators
    or document Python-only scope as a deliberate divergence.


- [x] Add direct full-code/full-block replacement mode in addition to diffs.
  - Spec evidence: AlphaEvolve can be configured to ask for a complete code
  - Required result: either preserve exact task text while validating
    non-empty content, or document that task descriptions are stripped at load
    time and should not rely on leading/trailing whitespace.


- [x] Add CLI problem-load error normalization to operational maturity.
  - Evidence: invalid problem definitions are task-setup failures and should be
    reported before experiment startup with diagnostics users can act on.
  - Current roadmap gap: config validation and run-directory preflight work
    covers `config.yaml`, plugins, backends, and overwrite safety, but not the
    CLI boundary around `load_problem()` itself.
  - Current evidence: `libreevolve.cli.run()` now invokes `load_problem()`
    inside the startup diagnostics block and converts loader
    `FileNotFoundError` / `ValueError` failures into user-facing
    `ClickException` messages. CLI tests cover malformed metrics, no seeds,
    missing validator, empty task, and invalid context manifest failures before
    `evolve()` is called.
  - Required result: convert loader exceptions into `ClickException` messages,
    cover malformed metrics, no seeds, missing validator, empty task, and
    context-manifest errors, and keep the checks ordered before any artifact
    cleanup or provider/plugin construction.
  - Status: implemented for the named loader failures, including a dedicated
    context-manifest CLI regression.


- [x] Add CLI/config precedence semantics to runtime hardening.
  - Evidence: `_build_config()` overwrites `config.yaml` `problem_name` with
    the problem directory name unless `--run-name` is supplied. Previously,
    `--reasoning-effort` applied only to CLI-created backend specs.
  - Current roadmap gap: the roadmap mentioned config validation but did not
    call out field-by-field precedence and effective-config override tests.
  - Status: OpenAI reasoning-effort override behavior is now deterministic and
    tested for config-file and CLI backend specs. Superseded behavior:
    problem-local `config.yaml problem_name` now fails early instead of being
    ignored, and CLI `--run-name` is tested as the effective manifest
    `problem_name`.
  - Requirement: task definitions, metric schemas, validators, and seeds are
    part of experiment setup; invalid setup should fail before a run starts
    with inspectable diagnostics.
  - Current status: `libreevolve run` now calls `load_problem()` inside its
    startup diagnostics path and converts loader `FileNotFoundError` /
    `ValueError` failures into user-facing `ClickException` messages. CLI tests
    cover malformed metrics, empty tasks, missing validators, no seed programs,
    and invalid context manifests before `evolve()` is called.
  - Required result: report loader failures as structured/user-facing CLI
    setup diagnostics for malformed metrics, empty tasks, missing validators,
    no seeds, and context errors; test that these failures happen before
    artifact cleanup, provider construction, or evolutionary logging.
  - Status: implemented for the named task setup failures, including
    context-specific CLI coverage.


- [x] Rich prompt sampler.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompts may include previous solutions, system instructions,
    explicit context, stochastic formatting, rendered evaluation results, and
    meta-prompt evolution.
  - Status: implemented prompt templates, deterministic local context files
    including PDF extraction, whole-template stochastic variants, compact stage
    feedback summaries, and local prompt-program selection, scoring, lineage,
    optional LLM mutation, plus configured/evolved prompt-template validation

- [x] Enforce evaluator scalar outputs against declared metrics.
  - Spec evidence: AlphaEvolve task specification requires `evaluate` to
    return a dictionary of scalar evaluation metrics, and those metrics drive
    database selection, prompting, and multi-score optimization.
  - Current evidence: `load_problem()` now rejects missing metric names,
    duplicate names, invalid `direction` values, multiple primaries, and
    malformed/non-finite/non-increasing bounds for all declared metrics, and
    unsupported metric schema fields. `CascadeEvaluator._run_subprocess()`
    validates the last stdout JSON object against `metrics.yaml`: declared
    metrics must be present, undeclared metrics are rejected, `is_valid` must
    be boolean, and every non-`is_valid` metric must be finite numeric.
  - Status: implemented with loader and evaluator tests for unsupported schema
    fields, missing secondary outputs, non-scalar values, NaN/Infinity, and
    undeclared metrics. Multi-objective use of those metric vectors remains
    tracked separately.


- [x] Strict scalar metric contract for evaluator outputs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: `evaluate` maps a solution to a dictionary of scalar
    evaluation metrics.
  - Status: implemented. Basic `metrics.yaml` schema validation rejects
    missing/duplicate names, invalid directions, multiple primaries,
    unsupported fields, malformed/non-finite bounds, and zero-width or inverted
    bounds. Evaluator output must include all declared metrics plus boolean
    `is_valid`, cannot include undeclared metrics, and every non-`is_valid`
    metric must be finite numeric. Invalid evaluator outputs are quarantined as
    `malformed_metrics`.


- [x] Enforce typed validity at the validated database-admission boundary.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the evolutionary database should preserve evaluated programs
    and support archive/query decisions from faithful score and validity
    evidence.
  - Current status: `ProgramDatabase.admit()` and the loop validity helper now
    require `evaluation.is_valid is True` before archive insertion, and
    `libreevolve show` uses the same exact boolean validity requirement for
    modern history selection. Missing, string, integer, and false values are
    rejected as invalid evaluation evidence.
  - Required result: require exact boolean validity for live archive insertion,
    keep legacy-history read fallbacks separate from admission semantics, and
    test malformed validity values at database/plugin/resume/show boundaries.
  - Status: implemented for `ProgramDatabase.admit()`, plugin-corrupted loop
    records, and current `show` inspection. Raw lower-level archive insertion
    remains tracked separately below. Future resume loading must reuse the same
    typed predicate when archive checkpoints exist.


- [x] Use artifact glob validation and diagnostics instead of environment-name
  validation.
  - Spec evidence: evaluator artifacts are benchmark evidence, and
    AlphaEvolve-style tasks may emit files whose names encode parameters,
    equations, or key/value settings. Artifact copy-out config should validate
    glob patterns as artifact patterns, not as environment variables.
  - Current evidence: `Config.validate()` now uses
    `_validate_env_var_list()` for `validator_env_allowlist` and
    `_validate_artifact_glob_list()` for top-level and per-stage artifact
    include/exclude fields. Artifact glob tests cover patterns containing `=`
    at both levels while the environment allowlist still rejects `=`.
  - Required result: split environment allowlist validation from artifact glob
    validation, use field-specific error messages, decide whether `=` and other
    valid filename characters are allowed in artifact patterns, and add tests
    for top-level and per-stage include/exclude patterns.
  - Status: implemented with field-specific validators and tests.


- [x] Validate evaluator-stage numeric fields before running cascades.
  - Spec evidence: AlphaEvolve-style cascades are explicit experiment
    configuration; invalid stage budgets, sample counts, retry counts, and
    thresholds should fail before evaluation with reproducible diagnostics.
  - Current evidence: `Config.validate()` now rejects non-positive
    `eval_stages[].samples`, negative retries, non-positive timeouts,
    nonnumeric `min_score`, unsupported stage fields, non-list `seeds`, and
    explicit `samples`/`seeds` length mismatches. `evolve()` and the CLI call
    `config.validate()` before building the evaluator or archiving seeds.
  - Status: implemented with config tests proving bad stage configs fail at
    construction/startup rather than during candidate evaluation.

- [x] Add LLM-generated feedback as an optional evaluation signal.
  - Spec evidence: AlphaEvolve can grade hard-to-code properties, such as
    simplicity, using separate LLM calls and either add scores or discard
    solutions.
  - Current evidence: `Config.llm_feedback` runs optional LLM graders after
    local evaluation; `libreevolve/core/feedback.py` parses grader responses,
    logs backend provenance and raw responses, adds feedback metrics, composes
    weighted fitness, and supports discard rules.
  - Status: implemented as a synchronous optional feedback pass. Remaining
    limitations: no parallel reviewer workers, no calibrated grader ensemble,
    and no ablation harness.
  - Required result: add optional feedback graders with clear provenance,
    score-composition rules, and archive/log visibility.


- [x] Render full workspace context to LLM feedback graders.
  - Status: completed item archived from the split trace; detailed task body was not present in the available command output.

- [x] Constrain run artifact paths to the configured log root.
  - Spec evidence: AlphaEvolve-style long-running experiments need reliable
    run directories, overwrite boundaries, and provenance for all emitted
    artifacts. A run name should identify a subdirectory, not rewrite the
    artifact root.
  - Status: implemented. `Config.validate()` rejects empty, nested,
    parent-relative, and host-invalid `problem_name` / `--run-name` values
    before artifacts are prepared. Runtime startup also resolves the final run
    directory and rejects it if it escapes the resolved `log_dir`; the CLI
    preflight path and `ProgramDatabase` construction both call this guard
    before cleanup or writes. Symlink/junction run-directory escapes are
    rejected instead of followed. Tests cover direct outside-path rejection and,
    when directory symlinks are available, prove overwrite startup leaves an
    outside `history.jsonl` untouched.


- [x] Add run-directory path confinement to runtime hardening.
  - Roadmap evidence: run-directory collision policy now prevents accidental
    reuse of known artifacts, but roadmap/runtime docs do not require the final
    run directory to remain under `log_dir`.
  - Status: implemented and documented. `Config.validate()` rejects unsafe
    `problem_name` and `--run-name` values before artifact preparation, and
    runtime startup resolves the final run directory before cleanup or writes.
    Paths that resolve outside the resolved `log_dir`, including
    symlink/junction run-directory escapes, are rejected. Tests cover unsafe
    absolute/drive-style run names, direct outside-path rejection, and
    symlink-capable overwrite protection.


- [x] Correct boolean config-validation claims for critique and meta-promp…933 tokens truncated…p.md:1948:    but not whether graders see the explicit constraints/literature that the
  - Status: completed item archived from the split trace; detailed task body was not present in the available command output.

- [x] Add validity/archive-aware run inspection to operational work.
  - Evidence: `cli.show()` now filters modern histories by
    `metadata.archive_admission.admitted` and `evaluation.is_valid`, reports
    its selection mode, and prints selected metrics when present. Legacy
    histories without archive metadata still use highest-fitness fallback. It
    still prints only the selected primary-file `code` and not archived best
    workspace artifacts.
  - Current roadmap gap: run-inspection work mentioned summaries, lineage,
    metrics, and failure statistics, but not the correctness problem that
    "Best program" can mean highest logged row rather than best archived
    candidate.
  - Required result: keep the implemented validity/archive-aware best
    selection tests, then add full-workspace artifacts and richer admission,
    stage, lineage, archive, prompt, feedback, and failure diagnostics.


- [x] Robust history read/inspection path for long experiment stores.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Requirement: the program database is the durable substrate for selection,
    inspection, and future prompt context; long append-only experiment logs
    need controlled failure modes when a record is malformed.
  - Current status: `libreevolve show` now streams `history.jsonl`, fails
    malformed JSON and non-object rows with line-numbered `ClickException`
    diagnostics, preserves empty-history handling, and requires explicit
    archive admission plus boolean evaluator validity for modern history
    selection.
  - Status: implemented as a fail-fast inspection policy with tests for
    malformed JSON, non-object rows, empty histories, strict modern validity,
    large legacy histories, and no-admitted-modern histories.


- [x] Add structured run metadata.
  - Spec evidence: AlphaEvolve experiments depend on prompt templates, LLM
    choices, evaluator stages, compute budgets, and configurations.
  - Current evidence: `manifest.json` records effective local config, backend
    roster, Git state when available, `libreevolve/` source-tree hashes,
    problem-tree hashes, direct evaluator entrypoint hashes, and plugin module
    file hashes. It does not yet include validated plugin specs/constructor
    parameters, aggregate emitted-artifact hashes, or resumable controller
    state.
  - Status: implemented for run-start configuration and source/problem/plugin
    module provenance. Plugin spec schemas, emitted-artifact aggregation, and
    resume/controller state remain separate hardening.
  - Required result: write a manifest with effective config, code version,
    problem hash, evaluator stages, backend specs, plugin specs, seed, and
    budget.


- [x] Add abnormal-run finalization to runtime manifests.
  - Roadmap evidence: `ROADMAP.md` Current State lists structured
    `manifest.json` and local run-budget stop accounting, while the Mid Term
    section says manifest hardening now focuses on plugin specs and aggregate
    emitted-artifact hashes.
  - Previous evidence: `manifest.json` was initialized at run start but
    `runtime` is written only after normal loop exit. A local proof made the
    first mutation LLM call raise after a valid seed had been logged; the run
    directory contained `history.jsonl`, but `manifest.json` had no `runtime`,
    stop reason, exception metadata, or consumed-budget snapshot.
  - Required result: define an abort/finalization path for provider, plugin,
    evaluator, materialization, serialization, and interrupt failures; record
    partial-run status and budget consumption in the manifest; and test that
    manifests are useful even when runs fail mid-generation.
  - Status: implemented for post-startup loop failures. Aborted runs now write
    `runtime.status`, stop reason, exception metadata, phase/role, consumed
    budget, history-written status, and artifact/quarantine pointers before
    re-raising. Tests cover LLM mutation failure, plugin hook failure, final
    runtime serialization failure, and normal-completion status.


- [x] Add atomic manifest-write durability to runtime hardening.
  - Roadmap evidence: manifest work treats `manifest.json` as the run's
    durable provenance and budget summary, but does not specify write
    durability or invalid-payload behavior.
  - Previous evidence: `strict_json_dump()` wrote directly to the destination.
    A local proof attempted to dump a runtime dict containing `object()` after
    a valid manifest already existed; the raised `TypeError` left the manifest
    as truncated invalid JSON. `update_manifest_runtime()` would therefore be
    able to lose startup provenance while trying to add final runtime metadata.
    Regression tests cover CLI repair of invalid `max_generations` and
    `backends` values from `config.yaml`, and configuration docs state the
    validation order.


- [x] Refresh the roadmap date and status.
  - Evidence: `ROADMAP.md:3` says it reflects the codebase as of
    `2026-03-26`, while the current checkout has papers downloaded and newer
    docs/tests than that snapshot.
  - Required result: update the roadmap date and state which current code/docs
    were audited.


- [x] Reframe the roadmap from "mostly tightening contracts" to "closing major
  AlphaEvolve specification gaps."
  - Evidence: `ROADMAP.md:20-21` says the next phase is mostly about contracts,
    experiment control, and reproducibility.
  - Contradiction: the AlphaEvolve paper requires evolve-block APIs,
    multi-component/full-file evolution, multi-score optimization, rich prompt
    context, configurable evaluation cascades, asynchronous throughput, and
    meta-prompt evolution. Several local versions now exist, but they remain
    narrower than AlphaEvolve's flexible candidate API, async controller,
    full multi-objective search, and large-scale experiment loop.
  - Required result: add a top-level AlphaEvolve alignment milestone before or
    alongside the existing reliability milestones.


- [x] Add configuration/schema validation to runtime hardening.
  - Evidence: AlphaEvolve-style task setup depends on configuration for
    prompts, evaluators, LLMs, and mutation behavior.
  - Current status: `Config.validate()` and `_build_config()` now reject
    unknown problem config keys, invalid mutation/ensemble enums, malformed

- [x] Add LLM backend preflight ordering to runtime/artifact safety.
  - Previous evidence: the CLI prepared or overwrote the run directory before
    `evolve()` constructs provider clients through `build_llm(config)`. A local
    proof cleared `OPENAI_API_KEY`, created an existing
    `runs/provider_preflight_probe/history.jsonl`, then ran with
    `--overwrite --max-generations 0 --backends openai:gpt-4o-mini`; the run
    failed during OpenAI client construction after deleting the previous
    history and writing a replacement manifest.
  - Required result: validate backend specs, provider credentials, constructor
    options, and configured provider capability knobs before overwrite cleanup
    or manifest/history writes; add tests for missing credentials and invalid
    provider settings.
  - Status: implemented for current built-in credential-backed providers and
    backend client construction when a mutation LLM can run. Missing OpenAI /
    Anthropic credentials fail before overwrite cleanup, while seed-only runs
    skip provider construction.


- [x] Decide and document the paper corpus source of truth.
  - Evidence: `papers/download_manifest.csv` lists 24 downloaded papers, while
    the README claims 23 references.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: evaluation artifacts and their limits are part of the
    reproducible evidence trail for candidate assessment, so invalid artifact
    budgets should fail before evaluation instead of producing successful
    records with impossible settings.
  - Current evidence: `Config.validate()` rejects negative artifact limits, but
    direct `CascadeEvaluator` construction still accepts them. A local proof
    with `artifact_include=["*.txt"]` and `artifact_max_files=-1` completed
    successfully, recorded `max_files: -1`, and skipped the matched artifact
    as `max_files`; `artifact_max_bytes=-1` likewise completed successfully
    and skipped the artifact as `max_bytes`.
  - Required result: make artifact-limit schema validation a core evaluator
    invariant or clearly limit paper-index artifact claims to config-built
    evaluators; add direct evaluator tests for invalid global and per-stage
    artifact options.


- [x] Treat evaluator artifact pattern schemas as benchmark evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: evaluator-generated artifacts should be reproducibly selected
    by task configuration. Pattern schemas and diagnostics need to match file
    artifact semantics, not unrelated environment allowlist rules.
  - Current status: artifact include/exclude config is now validated as
    artifact glob lists, separately from environment allowlists. Tests cover
    top-level and per-stage artifact patterns containing `=`.
  - Required result: define artifact pattern grammar, validate it separately
    from environment variable names, and cover top-level/stage artifact
    patterns in tests before treating evaluator artifacts as robust benchmark
    evidence.
  - Status: implemented for non-empty glob-string schema validation.


- [x] Document disabled GitHub workflow state or re-enable manual CI first.
  - Current evidence: `gh workflow list --all --json id,name,path,state`
    `runtime=5.0` and normalized `fitness=0.5`. README does not state that
  - Status: README, configuration, architecture, and run-artifact docs now state
    aggregation/pass policies remain open in code/paper/roadmap todos.
  - Required result: either seed validator process/RNG state from
    `stage["seed"]` themselves for deterministic sampled tests.
  - Status: documentation path completed. README, configuration docs, and
    architecture docs now state that stage seeds are JSON stage-context values
    state automatically.
  - Status: implemented and documented. README now states bounds are
  - Status: README, configuration, architecture, and run-artifact docs now state
    per-sample/per-stage wall-clock budget controls are implemented, while
    run-wide evaluator budget accounting remains open in code/paper/roadmap
    state that `evaluate()` may return only declared scalar metrics plus
  - Current evidence: evaluator stdout/stderr are redacted but stored in full
    state that persisted evaluator stdout/stderr is secret-redacted but not
    persisted-output caps and truncation metadata are implemented.
    update README/configuration/run-artifact docs to state that current stage
    artifact metadata is complete for the final returned stage or failed stop
    as a complete, robust evaluator-code provenance contract.

- [x] Fix README/CLI `--max-evaluations` wording for staged cascades.
  - README/CLI evidence: the CLI reference and Click option help previously
    described `--max-evaluations` as the maximum number of validator
    evaluations, which was ambiguous for sampled/retried staged cascades.
  - Status: Click help, README CLI help, and configuration docs now describe
    `max_evaluations` as a seed/candidate evaluation cap. Evaluator
    subprocess attempts, configured-stage samples, retries, validator timeouts,
    and sample/stage budget-exhaustion counts are persisted separately in
    evaluation accounting, candidate budget metadata, and runtime manifests.
  - Verification: focused budget/evaluator/loop tests prove sampled and retried
    cascades persist the detailed evaluator counters while
    `max_evaluations` remains the top-level seed/candidate cap.
  - Status: implemented and documented in README/problem-format docs. The docs
    now state that configured stages expose validated stage fields plus
    validator signatures and state that three-argument validators receive the

- [x] Document or fix hidden-file omission from seed workspaces.
  - README/problem-format evidence: docs describe seed directories as
    multi-file candidate workspaces, which can imply that all project-local
    files in the seed directory participate in the initial candidate.
  - Current evidence: `_load_initial_workspaces()` silently skips seed files in
    any path component starting with `.` plus `__pycache__`. A local proof with

- [x] Document or fix empty/fully skipped seed workspace diagnostics.
  - README/problem-format evidence: seed directories are documented as
    multi-file candidate workspaces, so an empty seed directory or a directory
    containing only excluded files should produce an understandable setup
    diagnostic.
  - Current evidence: local CLI/loader proofs with
    `initial_programs/empty_seed/` and `initial_programs/hidden_only/.config.py`
    both collapsed into the generic `No seed programs (*.py) or seed
    directories found...` error, with no indication that a declared seed
    directory existed but yielded no candidate files.
  - Required result: either implement per-seed skipped/empty diagnostics, or
    document the current seed-directory inclusion rules and generic error
    boundary until loader diagnostics are improved.
  - Status: documented. README and problem-format docs now state that empty or
    fully skipped seed directories are ignored and can still produce only the
    generic no-seeds diagnostic.


- [x] Document or fix non-Python primary-file fallback for seed workspaces.
    primary for seed workspaces, or document a deliberate non-Python-primary
    non-Python candidate mode. README now advises keeping at least one `.py`
    seed encoding currently surfaces as a raw UTF-8 decode error until binary
    shapes before using broad README language, or narrow the README claim to
    atomic topology edit set or a sequential mini-language.
    single-file non-Python candidates can make prompt boundaries or file-type
    contract and track remaining sandbox/build-system gaps separately.
    from a temporary runner rather than as a normal problem-local package.
  - Current evidence: the runner inserts the validator directory and then the
    runner, not as structured queryable output metadata.
  - Current evidence: the validator runner receives JSON-serialized stage
  - Current evidence: the evaluator runner inspects the validator signature and
    because the runner did not await the validator.
    `subprocess_error` / `returncode_1` when the runner tried to serialize the
    fitness `1.0`; the runner counted `*args` as one parameter and called it

- [x] Document or fix hidden explicit-context file selection.
  - README/problem-format evidence: docs say problem-local `context/` files are
    selected and sent into prompts, but they do not state whether dot-prefixed
    context files are included by default.
  - Current evidence: a local proof created `context/.secret.md` containing
    `api_key=sk-proj_hidden_context_1234567890`; `load_problem()` selected it,
    preserved the content in `Problem.context_files`, recorded `.secret.md` in
    `context_sources`, and reported `selected_count == 1`.
  - Required result: either exclude hidden context files unless explicitly
    included, or document that hidden `.txt`/`.md`/`.py`/`.pdf` files under
    `context/` are ordinary prompt inputs and should not contain secrets.
  - Status: fixed and documented. Hidden supported context sources are skipped
    by default with `hidden_not_included` diagnostics, and they are selected
    only when an include pattern explicitly names a dot-prefixed path component.
    README, problem-format, architecture, and run-artifact docs describe the
    policy and selected hidden sources carry `hidden: true`.
  - Verification: focused loader tests cover default hidden-source skipping,
    explicit opt-in, and broad wildcard includes that do not opt hidden sources
    into prompts.


- [x] Document or fix prefix-matched evolve-block markers.
  - README/problem-format evidence: README and problem-format docs show exact
    `# EVOLVE-BLOCK-START name` / `# EVOLVE-BLOCK-END` markers as the task
    boundary for skeleton preservation.
  - Current evidence: marker parsing accepts start-marker prefixes. A local
    proof with `# EVOLVE-BLOCK-STARTED` and a normal end marker loaded as a
    valid block named `ED`, so a typo or marker-like comment can silently
    become an evolvable region even though docs imply exact marker syntax.
  - Required result: either make start-marker parsing exact and document the
    accepted grammar, or warn that current parsing treats any line starting
    with `# EVOLVE-BLOCK-START` as a marker plus optional name.
  - Status: fixed and documented. README and problem-format docs now state the
    exact start-marker grammar, and mutation validation rejects prefix typos
    with focused candidate tests.


- [x] Document or fix malformed seed evolve-block startup behavior.
  - README/problem-format evidence: README shows evolve-block markers as part
    of the problem seed format, and startup validation is described for other
    problem contracts. Users can reasonably expect malformed seed markers to
    fail at problem load rather than later during mutation.
  - Current evidence: a local proof with an unterminated
    `# EVOLVE-BLOCK-START core` in `initial_programs/seed.py` loaded
    successfully through `load_problem()`.
  - Required result: either prevalidate seed markers and document the startup
    diagnostic, or explicitly state that marker errors are detected only when
    the candidate is later mutated.
  - Status: fixed and documented. Problem loading now prevalidates seed
    evolve-block markers for top-level `.py` seeds and seed workspace files,
    and README/problem-format docs describe the load-time diagnostic boundary.


- [x] Document or fix unmatched `context.yaml` include patterns.
  - Required result: either fail or warn on unmatched include patterns and
    `unmatched_includes`; loader tests prove mixed and empty-context unmatched

- [x] Add seed/proposal source markers to prompt-history traceability.
  - Evidence: artifact docs said history records include
    `metadata.prompt_program_id`, but seed rows are logged before prompt
    selection. A local zero-generation run produced a seed history row with no
    until the implementation provides a stronger sandbox boundary.


- [x] Qualify "secret-pattern redaction" until provider-key patterns are fully
  covered.
  - README evidence: README says provider keys are hidden from validators by
    default and that persisted stdout/stderr plus text artifacts receive basic
    secret-pattern redaction.
  - Current evidence: the duplicated evaluator/prompt/feedback redaction regex
    redacts underscore-prefixed examples such as `sk-proj_...`, `ghp_...`, and
    `github_pat_...`, but a local proof showed the hyphenated
    `sk-proj-abcdefghijklmnopqrstuvwxyz123456` form is preserved unchanged by
    all three helpers.
  - Required result: either implement/test redaction for current provider-key
    shapes before using broad README language, or narrow the README claim to
    the exact tested patterns and warn that redaction is best-effort.
  - Status: implemented for the README's current local redaction claim.
    Evaluator, prompt, and feedback redaction now share a helper that covers
    hyphenated `sk-proj-...` keys plus existing underscore provider-key forms,
    and focused tests exercise stdout/stderr, text artifacts, prompt summaries,
    and feedback prompts.


- [x] Document or fix unredacted DeepResearch provider-error metadata.
  - README/plugin-doc evidence: README and plugin docs describe retrieval
    metadata in candidate history and completed manifests, which can imply it is
    safe to retain as run telemetry.
  - Current evidence: `DeepResearchPlugin` stores custom-provider exception
    text verbatim under `retrieval_events[].error`. A local proof with
    `RuntimeError("provider failed api_key=sk-proj_secret_1234567890")`
    preserved the secret-like placeholder in plugin metadata; completed runtime
    retrieval summaries can also include event errors.
  - Required result: either redact/bound retrieval error diagnostics before
    persistence, or document that current DeepResearch retrieval error metadata
    may contain raw provider exception text and should be treated as sensitive.
  - Status: fixed and documented. DeepResearch custom-provider and arXiv
    provider-error strings are redacted/truncated before retrieval metadata is
    persisted, while structured error types remain available in README/plugin
    docs.


- [x] Separate parent-selection explore/exploit wording from island migration.
    default `parent_selection_strategy == "mixed"` policy using
    describe island migration separately from parent explore/exploit sampling,
    and keep the 70/30 default only in the parent-selection explanation.
    migration, and the 70/30 mix remains only in parent-selection text.
    archive-admitted, and has finite parent/child fitness. Reward provenance is
    `metadata.proposal` and rendered for future parent/inspiration programs.
    children must retain placeholders used by their parent prompt program.
    `{parent_code}` and `{mutation_instructions}` while still entering the
    checked against their parent prompt program and rejected if they drop
    parent placeholders, so evolved prompts cannot silently remove existing
    Architecture and configuration docs now state the parent-placeholder
    parent program/workspace and no SEARCH/REPLACE or full-mode mutation
    that configured seeds may omit parent code, feedback, inspirations, and
    described as quarantined with a parent penalty.
  - Previous evidence: the parent penalty could be invisible to selection when the
    parent has not yet recorded a successful use. `PromptDatabase._reject_mutation()`
    `0.0` and the parent remains an untried prompt arm. A local proof rejected
    meta-prompt children now penalize the parent prompt arm as one use with
    Tests cover never-used and already-used prompt parents.
    written to `prompt_history_invalid.jsonl` with parent id, generation,
    after mutating the parent prompt program. A local proof supplied invalid
    the in-memory parent with `reward_sum == -1.0`.
    diagnostically quarantined before parent prompt state changes; invalid
    rejection metadata leaves the parent prompt selection statistics unchanged.
    validator code can run with the full parent environment and without the
    parent environment variable; importing `libreevolve.cli` changed the
    process value from the parent value to the dotenv value before any command
    or document import-time override semantics, parent-env precedence, and the
    `validator_env_allowlist` as the way to opt parent environment variables
    summaries, parent ids, and repetition counts. A bounded recent tail is
    rendered parent programs, inspiration programs, context, and evaluator
  - Current evidence: prompt rendering currently wraps parent and inspiration
    manifest startup because the object lacked `on_generation_start`.
    `on_generation_start`, `build_extra_context`, `prompt_context_metadata`,
    `build_extra_context()` raises `RuntimeError("plugin context failed")`

- [x] Document or fix provider preflight behavior for all-invalid seeds.
  - README/run-artifact evidence: docs now state that seed-only runs skip
    `no_valid_programs`, while backend docs state that mutation-capable CLI runs
    preflight provider readiness before cleanup.
    invalid seed, `--max-generations 3`, `--backends openai:gpt-4o-mini`, and
    no `OPENAI_API_KEY` failed at startup with `LLM backend preflight failed`
  - Status: documented. README and run-artifact docs now state that
    positive-generation CLI runs where a mutation LLM could execute preflight
  - Required result: once implemented, document a seed-only/evaluate-only path
  - Status: implemented and documented. README and run-artifact docs now state
  - Required result: keep docs aligned with the exact artifact set that
    preflight collision checks and overwrite cleanup use.
    mistake mixed directories for clean reproducible runs.
  - Status: README, configuration, and run-artifact docs now state that
    empty-history handling explicit, and requires exact modern validity via
    whether large histories are streamed or fully loaded. The exact validity
    requirement for current history records is now implemented and tested.
  - Status: implemented behavior is fail-fast with normalized diagnostics;
    future resume/database work.
  - Current evidence: strict JSONL write validation is implemented, but
    whether these streams are crash-safe or best-effort.
    whether JSONL streams are fsynced/crash-safe, how partial final records are
  - Status: README, run-artifact docs, and development docs now state that
    crash-safe databases. They are not fsynced, checksummed, sequenced, spooled,
    or auto-repaired; after a killed process, complete earlier lines are the
    archive state.
    leave in-memory archive state ahead of accepted history until the database
    consistency work is implemented.
  - Current evidence: `Config.validate()` rejects unsafe `problem_name` and
    the resolved `log_dir`. The CLI preflight path and `ProgramDatabase`
  - Status: README, configuration, and run-artifact docs now state that the
    safe run-name component, which can be read as cross-platform filesystem
    safety.
    README/configuration/run-artifact docs to state that current validation is
    path-confinement-oriented rather than a complete portable filename grammar.
    LibreEvolve artifacts inside the selected run directory and already state
    separate unsupported state.
    callers must preflight restored budget state.
    then, README/run-artifact docs should state that completed manifests are
  - Status: implemented. `_build_config()` now merges config-file values and
    `backends` values from `config.yaml`, and configuration docs state the
    completed loop exits and may be absent after unhandled provider/plugin/
  - Status: implemented and documented. Runs that abort after startup manifest
    pointers, and completed runs can include `runtime.plugin_artifacts` when
    artifacts written before an abort are summarized the same way as completed
  - Required result: either implement validated plugin artifact summaries for
    aborted runs, or update README/run-artifact docs to state that aborted

- [x] Add AlphaEvolve-style evolve-block markers.
  - Spec evidence: AlphaEvolve supports blocks marked with
    `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END`, while the surrounding
    code acts as a skeleton.
  - Current evidence: `libreevolve/core/candidate.py` parses evolve-block
    markers and constrains mutations to marked regions within single-file and
    workspace candidates.
  - Status: implemented in `libreevolve/core/candidate.py`; one or more marked
    regions are parsed and skeleton code is preserved during mutation when
    markers are well-formed.
  - Required result: problem loading should support one or more marked
    evolvable regions, preserve non-evolved skeleton code, and apply mutations
    only where configured.


- [x] Reject malformed evolve-block marker structures during mutation.
  - Spec evidence: AlphaEvolve's task API relies on marked evolvable blocks
    inside a skeleton; an invalid marker layout should not change which code is
    evolvable without an explicit diagnostic.
  - Current evidence: `validate_evolve_blocks()` checks marker pairing,
    nesting, block-name syntax, duplicate block names, orphan end markers, and
    malformed end markers before mutation. `apply_candidate_mutation()` fails
    closed with `malformed_evolve_blocks:<reason>`, and workspace mutation
    prefixes the target path in the diagnostic.
  - Status: implemented at mutation-application time, with tests for missing
    end markers, orphan end markers, nested blocks, duplicate names, invalid
    names, anonymous block naming, and malformed target files in workspaces.
    Problem loading still does not prevalidate seed files before the first
    evaluation/mutation path sees them.
  - Required result: validate marker pairing, nesting, names, and duplicate
    block identities during problem load or mutation application; reject or
    quarantine malformed candidates with explicit errors; add tests for missing
    end markers, orphan end markers, nested blocks, duplicate names, and mixed
    valid/invalid files in workspaces.


- [x] Prevalidate seed evolve-block markers during problem loading.
  - Spec evidence: AlphaEvolve-style task specifications should reject invalid
    evolvable-region declarations before evaluating or mutating a malformed
    starting point.
  - Current evidence: `_load_initial_workspaces()` reads seed files into
    `CandidateWorkspace` without calling `validate_evolve_blocks()`. A local
    proof created `initial_programs/seed.py` containing
    `# EVOLVE-BLOCK-START core` without an end marker; `load_problem()` still
    returned one initial workspace and preserved the malformed seed text.
  - Required result: validate every loaded seed file in top-level `.py` seeds
    and seed workspace directories; fail problem loading with file-scoped
    diagnostics for missing end markers, orphan ends, nested blocks, invalid
    names, and duplicate names; add loader tests for single-file and workspace
    seeds.
  - Status: implemented. `_load_initial_workspaces()` validates every loaded
    seed file with `validate_evolve_blocks()` and raises file-scoped setup
    diagnostics before returning a `Problem`. Loader tests cover malformed
    top-level `.py` seeds and malformed workspace seed files.


- [x] Make evolve-block marker matching exact rather than prefix-based.
  - Spec evidence: AlphaEvolve's task API relies on exact
    `# EVOLVE-BLOCK-START` / `# EVOLVE-BLOCK-END` declarations to define the
    skeleton boundary. Marker-looking comments or typos should not silently
    create evolvable regions.
  - Current evidence: `_parse_evolve_blocks()` uses
    `stripped.startswith(EVOLVE_BLOCK_START)`. A local proof with
    `# EVOLVE-BLOCK-STARTED` followed by `# EVOLVE-BLOCK-END` returned
    `validate_evolve_blocks(...) is None` and extracted one block named `ED`
    containing `x = 1`, so a misspelled marker was treated as a valid task
    boundary.
  - Required result: parse start markers as exact tokens with either no suffix
    or a whitespace-separated valid block name; reject marker prefixes such as
    `# EVOLVE-BLOCK-STARTED`, `# EVOLVE-BLOCK-START_name`, and similar
    comment text; add mutation and problem-loader tests after seed preflight is
    implemented.
  - Status: implemented in mutation-time marker validation. Start markers must
    be the exact token with no suffix or a whitespace-separated block name;
    prefix typos now return `malformed_evolve_blocks:invalid_start_marker`.
    Candidate tests cover tab-separated valid names and prefix typo rejection.
    Seed load-time prevalidation remains tracked separately.


- [x] Support multi-component and multi-file codebase evolution.
  - Spec evidence: AlphaEvolve evolves large code pieces spanning multiple
    functions and components and can evolve an entire code file/codebase.
  - Current evidence: `CandidateWorkspace` represents text file sets,
    `Program.files` stores candidate files, loader accepts seed directories,
    file-section mutations route edits across files, and the evaluator
    materializes the whole workspace for validators.
  - Status: basic local workspace evolution is implemented and covered by
    tests. Remaining limitations: Python syntax validation only, no arbitrary
    language runners/build systems, and `best.py` is still a primary-file
    convenience artifact. Candidate paths reject traversal, drive-letter, and
    colon-component paths before materialization.
  - Required result: represent a candidate as a project/file set, apply diffs
    across marked files/components, and pass the whole candidate workspace to
    `evaluate`.

  - README/problem-format evidence: the docs describe SEARCH/REPLACE as the
    default mutation mode and say evolve-block markers preserve surrounding
    skeleton code, which implies the replacement target is well-defined.
  - Current evidence: `apply_diff()` replaces only the first occurrence of a
    duplicated SEARCH string. A local proof with two identical `x = 1` lines
    returned `err=None` and changed the first line only. With two evolve blocks
    containing the same `x = 1` body, evolve-block diff mode also changed the
    first matching block.
  - Required result: either implement ambiguous-match rejection/explicit target
    syntax, or document that SEARCH text must be unique because the current
    engine applies the first matching occurrence.


- [x] Task specification API with evolve-block markers.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: users mark code blocks to evolve inside a larger skeleton.
  - Status: implemented for Python single-file and local workspace candidates
    in `libreevolve/core/candidate.py`; malformed marker structures are
    rejected during mutation application with explicit diagnostics.
  - Remaining divergence: arbitrary-language runners remain open; evolve
    blocks are still a text-file convention rather than a generalized
    problem-defined candidate API.


- [x] Prevalidate malformed evolve-block seeds before evaluation.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: task specifications define the valid evolvable regions before
    the evolutionary loop starts.
  - Current gap: malformed marker structures are rejected during mutation, but
    not during problem loading. A local proof with `initial_programs/seed.py`
    containing `# EVOLVE-BLOCK-START core` and no matching end marker loaded
    successfully as one initial workspace.
  - Required result: reject malformed seed evolve-block layouts at load time
    for single-file and workspace seeds, or mark delayed mutation-time
    validation as a deliberate divergence in the AlphaEvolve paper row.
  - Status: implemented. `load_problem()` rejects malformed top-level seed
    files and workspace seed files with file-scoped diagnostics before
    evaluation starts; loader tests cover both boundaries.


- [x] Reject marker-prefix typos in evolve-block task specifications.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: evolve-block markers define the exact boundary between
    skeleton code and code that AlphaEvolve may change.
  - Current gap: start-marker parsing is prefix-based. A local proof with
    `# EVOLVE-BLOCK-STARTED`, `x = 1`, and `# EVOLVE-BLOCK-END` returned no
    marker error and extracted a valid block named `ED`, so a typo or
    marker-like comment can silently change the task specification.
  - Required result: make marker parsing exact, or explicitly document this as
    a divergence from exact task-specification markers before claiming
    AlphaEvolve-style evolve-block fidelity.
  - Status: implemented for mutation validation and documented. Start markers
    must be exact with an optional whitespace-separated name, and prefix typos

- [x] Correct feedback-prompt input redaction claims for evaluator diagnostics.
  - README/run-artifact evidence: README says feedback prompt inputs apply basic
    secret redaction, but that is only true for the workspace source section.
  - Current evidence: `_render_feedback_diagnostics()` renders evaluator
    stdout/stderr without `_redact_sensitive_text()`. A local proof with
    `stdout="api_key=sk-proj_secret_1234567890"` and
    `stderr="token=ghp_abcdefghijklmnop"` sent both strings verbatim to the
    feedback grader prompt.
  - Required result: either redact evaluator diagnostics in feedback prompts or
    document that feedback-grader prompt redaction currently covers workspace
    file contents but not evaluator stdout/stderr diagnostics.
  - Status: documented in README and configuration docs. The feedback sections
    now say input redaction currently covers workspace file contents only,
    while evaluator diagnostics and metric payloads rendered into feedback
    prompts are truncated but not redacted yet. The implementation gap remains
    tracked in `docs/todo/code.md`.


- [x] Document or fix raw metric payloads in LLM feedback prompts.
  - README evidence: README says LLM feedback grader prompt inputs apply basic
    secret redaction, and separately warns that feedback outputs are not
    redacted. It does not call out that the `[METRICS]` input section is also
    rendered raw.
  - Current evidence: `_build_feedback_prompt()` appends
    `json.dumps(result.metrics, sort_keys=True)` under `[METRICS]` without
    redaction or schema filtering. A local proof with
    `metrics={"score": 0.4, "debug_label":
    "sk-proj-metricsecretabcdefghijklmnopqrstuvwxyz"}` sent that secret-like
    metric value verbatim to the feedback grader prompt.
  - Required result: either implement metric redaction/schema filtering before
    feedback prompt rendering, or update README/configuration/run-artifact docs
    so "feedback prompt input redaction" is scoped to workspace text until
    metrics and diagnostics share the same prompt-safe formatter.
  - Status: documented in README and configuration docs. Both now state that
    metric payloads rendered into feedback prompts are truncated but not
    redacted yet, and scope current feedback-prompt input redaction to
    workspace file contents. The code-level metric-redaction/schema-filtering
    gap remains open in `docs/todo/code.md`.


- [x] Document or fix failure-history redaction limits.
  - README/run-artifact evidence: README describes `failure_history.jsonl` as
    durable failed-trial memory and elsewhere says persisted diagnostics use
    basic secret-pattern redaction.
  - Current evidence: accepted failure-history records currently preserve raw
    mutation snippets, evaluator errors, and evaluator stdout/stderr summaries.
    A local proof wrote `sk-proj-abcdefghijklmnopqrstuvwxyz123456` in mutation
    text and evaluator error plus `ghp_abcdefghijklmnopqrstuvwxyz123456` in
    evaluator stdout; all appeared verbatim in `failure_history.jsonl`.
  - Required result: either redact these fields before persistence, or update
    README/run-artifact docs to state that failure-history records are bounded
    but not sanitized and should be treated as sensitive run artifacts.
  - Status: documented in README and run-artifact docs. Both now state that
    accepted `failure_history.jsonl` rows are bounded diagnostic records, not
    sanitized logs, and can retain raw mutation/seed snippets, evaluator
    summaries, paths, and error text. The implementation-level redaction gap
    remains open in `docs/todo/code.md`.


- [x] Document or fix evaluator-artifact path prompt redaction.
  - README/run-artifact evidence: README says future mutation prompts receive
    bounded, redacted evaluator artifact paths and hashes, which implies
    artifact path metadata and artifact-limit diagnostics are covered by the
  - Current evidence: copied artifact source/stored paths and skipped artifact
    `_render_artifacts()` inserts `path={source}` and `stored={stored}` without
    `repr()`. A local proof configured `artifact_max_files=1`; the validator

- [x] Correct documented plugin hook ordering around parent selection.
  - README/plugin-doc evidence: the plugin docs list `on_generation_start()` as
    `plugin.on_generation_start()`. The hook still runs before inspiration
  - Required result: either move the hook before parent selection, add a
    separate pre-parent hook, or update README/plugin/architecture docs to
    that parent selection happens before `on_generation_start()`, and that the

- [x] Correct documented `prompt_context_metadata()` call condition.
    `prompt_context_metadata()` runs "if extra prompt context is recorded",
    `prompt_context_metadata()` whenever the hook exists, even when
    metadata can contain plugin metadata with `emitted: false`.
    `prompt_context_metadata()` runs during plugin-context construction even
    `emitted: false`.
    `on_generation_start()`, `build_extra_context()`, `on_evaluated()`, and
  - Current evidence: `PluginBase` also defines `prompt_context_metadata()`
    `prompt_context_metadata()`, and completed manifests include plugin
    `docs/plugins.md` lists `prompt_context_metadata()` plus
    returned by `prompt_context_metadata()`. A local proof put a Python `set`
  - Current evidence: `DeepResearchPlugin.on_generation_start()` builds its
    raised during `on_generation_start()`; the aborted manifest showed only

- [x] Document LLM failed-call redaction limits before advertising call logs.
  - README/backend-doc evidence: README and backend docs now mention
    ensemble-level failed-call telemetry, and future work calls for persisted
    provider diagnostics.
  - Current evidence: failed-call telemetry stores raw `str(exc)` in
    `LLMEnsemble.call_history`. A local proof with a provider exception
    containing `api_key=sk-proj_secret_123` preserved that full placeholder in
    the telemetry record.
  - Required result: either implement redacted/bounded provider-error telemetry
    before persisting call logs, or document that current in-memory failed-call
    diagnostics are not yet safe to persist verbatim.
  - Status: implemented and documented. Ensemble failed-call telemetry now
    stores redacted/truncated provider exception text while preserving
    structured error type and retry/fallback metadata; README and backend docs
    describe the boundary.


- [x] Document evaluation-stage seed semantics or make seeds operational.
    validators with `samples`, `seeds`, retries, and stage context, which can
  - Current evidence: stage seeds are passed in the JSON stage context but do
    not seed the validator subprocess RNG. A local proof with two samples using
    identical `seeds: [123, 123]` produced different `random.random()` scores
    while preserving `stage.seed == 123` in both sample metadata.
  - Required result: either seed validator process/RNG state from
    `eval_stages[].seeds[]`, or update README/config/run-artifact docs to say
    seeds are validator-managed metadata and validators must consume
    `stage["seed"]` themselves for deterministic sampled tests.
    README, configuration docs, and run-artifact docs now state that stage
    seeds are operational: non-null seeds produce `stage["rng_seed"]`, set
    subprocess `PYTHONHASHSEED`, and seed Python `random` plus NumPy before
    validator import.
  - README/config evidence: docs describe `eval_stages[].retries` and
    normalization hints rather than hard validity constraints, and run-artifact
    timeouts, samples, seeds, retries, and thresholds, which can read as a
  - Status: README, configuration, architecture, and run-artifact docs now state
    that `eval_stages[].timeout_sec` is enforced per validator subprocess
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    stored with each candidate and describes evaluator artifacts/stdout/stderr,
    artifacts while `evaluate()` itself must return scalar metrics only.
  - Status: README, problem-format, architecture, and run-artifact docs now
    limited to stdout/stderr or opt-in copied evaluator artifacts.
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    `malformed_metrics`; the actionable reason from `_validate_metrics()` is
    evaluation records and document them, or narrow README/run-artifact wording
  - README/run-artifact evidence: README and run-artifact docs describe
  - README/run-artifact evidence: README says raw stdout/stderr diagnostics are
    to configured artifacts instead.
  - Status: README, problem-format, architecture, and run-artifact docs now
    docs direct large diagnostics to configured evaluator artifacts until
  - README/run-artifact evidence: README and run-artifact docs describe staged
    evaluators, per-stage artifacts, and structured evaluation records, which
    metadata listed only the final `hard` stage and its `hard.txt` artifact.
    artifact metadata, validator environment metadata, retry attempts, or stage
    update README/configuration/run-artifact docs to state that current stage
    artifact metadata is complete for the final returned stage or failed stop
  - README/run-artifact evidence: README and run-artifact docs say manifests
    validator stages with `validate_path`, `samples`, `seeds`, retries, stage
    context, including the raw `config` mapping. `Config.validate()` now
    scalar `seeds` values such as `Path` objects, booleans, and non-finite
    schema for stage names, paths, and seed values; until then, avoid claiming
    `validate.py` as a required problem contract, while run-artifact docs say
    `--overwrite` intentionally replaces known artifacts for a fresh run.
    signatures, and staged validator paths before overwrite cleanup or seed
  - Status: implemented and documented. README/problem-format/run-artifacts
  - README/run-artifact evidence: docs now say validator contracts are
    invalid seed row and wrote `manifest.json` runtime metadata. The missing
    `AttributeError`, not as a pre-artifact task-setup diagnostic.
    docs broad, or narrow README/run-artifact wording to say the preflight
    AlphaEvolve-style LLM-guided evolution, backend throughput/depth routing,
    records one backend/prompt reward before moving to the next generation.

- [x] Clarify MadEvolve is background context in the README paper table.
  - README evidence: the local paper cache row already says MadEvolve is
    background only, but the README paper table described its role as
    "Domain-specific evolution," which could be read as a current feature or
    implementation direction.
  - Paper evidence: `2602.15951__MadEvolve.pdf` emphasizes free-parameter
    extraction/optimization and generated evolution reports.
  - Current evidence: LibreEvolve has no free-parameter tracking,
    gradient/gradient-free parameter optimizer, or generated innovation report.
  - Required result: make the README citation table match the paper-index
    boundary unless those MadEvolve mechanisms are implemented.
  - Status: `README.md` now labels MadEvolve as background context with no
    MadEvolve implementation.

- [x] Clarify README MAP-Elites performance-axis wording.
  - Current evidence: `MAPElites._cell_with_descriptors()` computes the
    performance-like descriptor from `_selection_score(program)`, which uses

- [x] Document or fix invalidly encoded `config.yaml` diagnostics.
  - Current evidence: invalid UTF-8 in `config.yaml` is not normalized through
    YAML parser/schema failures after successful UTF-8 decoding only.
  - Status: fixed in the CLI. Invalid UTF-8 in `config.yaml` is now normalized
    into a path-aware startup error that names the config file and says UTF-8;
    any overwrite cleanup so invalid plugin configuration cannot fail after
  - Current evidence: malformed TOML or invalid UTF-8 in `pyproject.toml`
    applying CLI arguments, so invalid config-file values aborted before a

- [x] Document package metadata provenance failure behavior.
  - Status: completed item archived from the split trace; detailed task body was not present in the available command output.

- [x] Document or enforce reserved and ambiguous run-name components.
  - Status: completed item archived from the split trace; detailed task body was not present in the available command output.

- [x] Document or harden linked known-artifact directories during overwrite.
  - Status: completed item archived from the split trace; detailed task body was not present in the available command output.

- [x] Document or fix startup-manifest overwrite ordering.
  - Status: completed item archived from the split trace; detailed task body was not present in the available command output.

- [x] Refresh configuration-doc CLI override list for budget options.
  - README-adjacent evidence: `docs/configuration.md` describes configuration
    source precedence and lists CLI overrides, so users rely on it to know
    which AlphaEvolve-style run-budget controls can override `config.yaml`.
  - Previous evidence: `libreevolve/cli.py` exposes `--max-evaluations`,
    `--max-evaluator-seconds`, and `--max-runtime-seconds`, and
    `tests/test_cli.py::test_run_budget_cli_options_override_config` proves
    they override problem-local config. The `docs/configuration.md` CLI
    override list previously included `--max-generations` but omitted those
    three budget options.
  - Current evidence: `docs/configuration.md` now lists
    `--max-evaluations`, `--max-evaluator-seconds`, and
    `--max-runtime-seconds` alongside `--max-generations`.
  - Status: documentation fixed; the existing CLI test covers the override
    behavior.

- [x] Document or fix non-string `config.yaml` key diagnostics.
  - README/config evidence: docs describe problem-local `config.yaml` as a
    validated configuration layer with unknown-key diagnostics.
  - Current evidence: unknown-key diagnostics were not stable for mixed YAML
    key types. A local CLI proof with `config.yaml` containing `1: bad`,
    `unknown: bad`, and `max_generations: 0` exited with no Click error text
    and surfaced raw `TypeError: '<' not supported between instances of 'str'
    and 'int'` from `_build_config()` sorting mixed unknown keys.
  - Required result: either reject non-string top-level YAML keys with a clear
    config-file diagnostic before unknown-key sorting, or document that
    `config.yaml` keys must be strings and malformed key types may currently
    raise lower-level Python errors.
  - Status: fixed in the CLI. Non-string top-level `config.yaml` keys are now
    rejected before unknown-key sorting with a path-aware diagnostic, and CLI
    tests cover non-string-only plus mixed non-string/unknown string keys.

- [x] Document or fix plugin-alias validation ordering before validator
  preflight.
  - README/plugin/runtime evidence: README says unknown plugin aliases fail
    before run-directory overwrite cleanup, while problem-format docs describe
    validator-contract preflight as a startup step. Together these can imply
    invalid plugin config is rejected before user validator code is imported.
  - Current evidence: the CLI called evaluator preflight before
    `_validate_plugin_names()`. A local proof ran `libreevolve run` with
    `--plugins missing_plugin` and a `validate.py` module-level side effect;
    the command reported the unknown plugin, but the validator import side
    effect had already written a marker file.
  - Required result: either validate plugin aliases before validator preflight,
    or update README/problem-format/runtime docs to state that unknown plugins
    are caught before artifact cleanup but not before validator import-time
    side effects under the current CLI ordering.
  - Status: fixed in the CLI. Plugin aliases are now validated before
    evaluator-contract preflight imports validators, and a CLI regression test
    proves the unknown-plugin path leaves the validator import marker absent.

- [x] Correct run-name control-character documentation for ASCII DEL.
  - README/CLI evidence: README says `--run-name` rejects control characters
    before artifacts are prepared.
  - Current evidence: `Config(problem_name="bad\x7fname")` was accepted because
    `_require_run_name_component()` checked only `ord(ch) < 32`; a local proof
    then constructed `ProgramDatabase(cfg)` and persisted the same DEL-bearing
    `problem_name` in `manifest.json`.
  - Required result: either reject ASCII DEL and similar control-class
    characters in code, or narrow README/problem-format/run-artifact wording so
    the documented run-name grammar matches the actual accepted set.
  - Status: fixed in code. The safe run-name component grammar now rejects DEL
    as a control character, with direct config and CLI tests.

- [x] Document or make `log_dir` manifest retention secret-safe.
  - README/run-artifact evidence: README and run-artifact docs describe
    manifests as reproducibility artifacts and list the effective run
    configuration, which can imply persisted config paths are safe to share.
  - Current evidence: `ProgramDatabase` wrote the effective `config.log_dir`
    verbatim. A local proof used
    `log_dir=<tmp>/api_key=sk-proj_LOGDIRSECRET_1234567890/runs`; the completed
    startup manifest preserved the raw secret-like path component under
    `manifest.json.config.log_dir`.
  - Required result: either redact/hash/relativize `log_dir` in manifests and
    document the stable field, or warn that manifests currently retain raw log
    root paths and should be treated as sensitive when paths contain private
    usernames, scratch labels, or credential-like folder names.
  - Status: fixed for startup manifests. Absolute log roots are no longer
    written raw; `manifest.config.log_dir` records `<absolute-log-dir>` and
    `log_dir_metadata` records a hash and retention reason. Relative safe
    `runs` remains visible for local reproducibility.

- [x] Document or reject Unicode format controls in run and candidate labels.
  - README/problem-format evidence: docs describe run names and candidate paths
    as safe, normalized labels, which can imply prompt/history/manifest labels
    render plainly and cannot contain invisible direction-changing characters.
  - Current evidence: direct config accepted `problem_name="rtl\u202egnp"`, and
    candidate path normalization accepted `src/rtl\u202egnp.py`. A local proof
    wrote both labels into durable artifacts: `manifest.json.config.problem_name`
    and `history.jsonl` `primary_file` / `files`.
  - Required result: either reject or visibly escape Unicode `Cf`/bidi-control
    characters in persisted labels, or update README/problem-format/run-artifact
    docs to warn that current labels may contain invisible or direction-changing
    characters even when ASCII path hazards are rejected.
  - Status: fixed for run names and candidate paths. Config and candidate-path
    normalizers now reject Unicode format controls, while README,
    problem-format, configuration, and run-artifact docs explicitly distinguish
    ordinary non-ASCII names from bidi/invisible format controls.

- [x] Document or reject Unicode format controls in metric and stage labels.
  - README/config/problem-format evidence: docs describe metric names and
    evaluator stage names as structured identifiers in validator outputs,
    evaluation records, and run artifacts.
  - Status: fixed for Unicode format controls. Metric names and configured
    stage names now reject right-to-left override and zero-width joiner, and
    configuration/problem-format docs state that policy while leaving broader
    safe-label grammar work open.

- [x] Document or reject Unicode format controls in plugin and feedback labels.
  - README/config/plugin evidence: docs describe configured plugins and
    LLM-feedback grader specs as run configuration and evaluation metadata.
  - Status: fixed for Unicode format controls. Configured plugin aliases and
    LLM feedback `name` / `metric` labels now reject right-to-left override and
    zero-width joiner, and README/config/plugin docs state that boundary while
    leaving broader safe-label grammar work open.

- [x] Document or reject Unicode format controls in artifact/context patterns.
  - README/problem-format/run-artifact evidence: docs describe evaluator
    artifact selectors and context manifest include/exclude patterns as
    persisted manifest policy.
  - Status: fixed for Unicode format controls. Config validation rejects
    right-to-left override and zero-width joiner in top-level and staged
    artifact selectors, the problem loader rejects them in context manifest
    patterns, and README/config/problem-format/run-artifact docs state the
    display-safe boundary.

- [x] Document or reject Unicode format controls in plugin-emitted metadata keys.
  - README/plugin/run-artifact evidence: docs describe
    `prompt_context_metadata()` and `run_artifacts_metadata()` as persisted
    candidate-history and manifest provenance.
  - Status: fixed for metadata keys. Plugin prompt-context metadata and
    run-artifact metadata now reject non-string keys and Unicode format
    controls recursively, and README/plugin/run-artifact docs state the
    display-safe boundary.

- [x] Document and enforce canonical validator environment allowlists.
  - README/config/problem-format/run-artifact evidence: docs describe
    `validator_env_allowlist` as the way to opt parent environment variables
    into validator subprocesses and as persisted evaluator provenance.
  - Status: implemented and documented. Allowlist names are stripped,
    uppercased, deduplicated, and validated as manifest-safe env labels before
    persistence or evaluator use; docs state that values are not written to
    metadata.

- [x] Document and enforce safe metric-name syntax.
  - README/problem-format evidence: metric names are shown as validator-output
    keys and persisted task schema labels.
  - Status: implemented and documented. `metrics.yaml` names now use a safe
    ASCII identifier grammar with optional dotted namespaces; README and
    problem-format docs state the grammar and reserve `is_valid`.

- [x] Document and enforce direct `Problem` metric-schema validation.
  - README/API evidence: README lists `Problem` as an importable dataclass used
    by tests, integrations, and future resume/runtime code.
  - Status: implemented and documented. Direct `Problem(...)` construction now
    applies the same metric-schema normalization as file-loaded problems, and
    README/problem-format docs state that direct callers cannot bypass metric
    schema checks.

- [x] Document formerly single-proposal generation limits.
  - README evidence: the comparison and workflow sections describe
    AlphaEvolve-style LLM-guided evolution, backend throughput/depth routing,
    and asynchronous work as future runtime direction, but previously did not
    state that the current CLI loop emits only one candidate proposal per
    generation.
  - Current evidence: `evolve()` selects one parent, builds one prompt, calls
    `llm.generate()` once for the mutation role, evaluates one child, and
    records one backend/prompt reward before moving to the next generation.
  - Superseded status: this README correction was accurate for the earlier
    single-proposal loop. The current docs now describe sequential
    `proposals_per_generation` batches with sibling-candidate accounting, while
    keeping parallel LLM/evaluator workers as future runtime work.

- [x] Document detect-secrets baseline workflow for intentional fake secrets.
  - README/development evidence: the contributor workflow tells users to run
    `py -3.12 -m pre_commit run --all-files`, but previously did not explain
    how to handle intentional fake provider tokens in redaction tests and TODO
    evidence.
  - Current evidence: a local pre-commit run failed after `detect-secrets`
    regenerated `.secrets.baseline` for synthetic secret-like examples and then
    reported that the baseline file was unstaged. Staging the regenerated
    `.secrets.baseline` made the same pre-commit command pass.
  - Status: README and development docs now state that intentional fake tokens
    need either narrow fixture allowlists or a reviewed, staged
    `.secrets.baseline` update, and that an unstaged baseline update is a
    validation issue rather than a provider/API failure.

- [x] Clarify AGENTS.md parent-sampling default scope.
  - Documentation evidence: `AGENTS.md` listed "30% explore / 70% exploit
    parent sampling" as a key convention.
  - Current evidence: `evolve()` only uses `explore_ratio` when
    `config.parent_selection_strategy == "mixed"`; explicit strategies such as
    `explore`, `exploit`, `metric`, `novelty`, and `recency` bypass the 30/70
    draw entirely.
  - Status: `AGENTS.md` now states that 30% explore / 70% exploit is the
    default `mixed` parent-selection behavior and that explicit strategies
    bypass the ratio.

- [x] Clarify AGENTS.md validator subprocess wording with the preflight caveat.
  - Documentation evidence: `AGENTS.md` said all `validate.py` files run in
    temporary local subprocesses.
  - Current evidence: actual evaluation uses `_RUNNER` in a temporary local
    subprocess, but CLI startup calls `preflight_evaluator_contracts()` first.
    That preflight imports default and configured validator modules in the
    parent process with `spec.loader.exec_module(module)`, so validator
    import-time code can run before the subprocess environment, timeout,
    stdout/stderr capture, and evaluation-record boundaries apply.
  - Status: `AGENTS.md` now distinguishes validator execution from CLI
    contract preflight imports.

- [x] Document sampling strategy fields in the configuration reference.
  - README/config evidence: README says parent and inspiration sampling are
    configurable via `parent_selection_strategy` and `inspiration_strategy`,
    and the CLI reference exposes both options.
  - Current evidence: `docs/configuration.md` listed many `Config` fields but
    omitted `parent_selection_strategy` and `inspiration_strategy`; both fields
    exist in the `Config` dataclass and are validated against fixed allowed
    value sets.
  - Status: `docs/configuration.md` now documents both fields with defaults,
    allowed values, and the fact that `explore_ratio` only applies to the
    default `mixed` parent strategy.

- [x] Harden the `workspace_math` example as a true cross-file smoke test.
  - README/problem-format evidence: README lists `workspace_math` as a
    multi-file example, and problem-format docs show helper-file workspaces as
    the compatibility path toward codebase candidates.
  - Previous evidence: `workspace_math/validate.py` required `helpers.py` to
    exist but did not require `main.py` to import it or use its contents. A
    direct `solve() -> 42` with an unused helper file returned valid.
  - Status: `workspace_math` now requires `main.py` to depend on
    `helpers.base_value()` by checking the result under a perturbed helper
    module, its task description says that dependency is required, and
    `tests/test_examples.py` rejects the direct-constant shortcut.

- [x] Document and reject async/generator validator functions at startup.
  - README/problem-format evidence: docs describe validator signatures as
    synchronous `evaluate(...) -> dict` functions returning metrics.
  - Previous evidence: async and generator validators passed startup preflight
    and failed only during subprocess evaluation.
  - Status: evaluator preflight now rejects coroutine, generator, and
    async-generator `evaluate` functions for default and staged validators.
    README and problem-format docs state that boundary.

- [x] Document and reject validator signatures outside the fixed call shapes.
  - README/problem-format evidence: docs list fixed validator call shapes:
    `evaluate(code)`, `evaluate(code, workspace_path)`, and
    `evaluate(code, workspace_path, stage)`.
  - Previous evidence: variadic and extra-parameter validators passed startup
    preflight and received context through parameter-count heuristics.
  - Status: evaluator preflight now rejects variadic, keyword-only, and
    extra-parameter `evaluate` signatures. README and problem-format docs state
    the fixed call-shape boundary.

- [x] Fix the direct `evolve()` preflight boundary.
  - README/run-artifact evidence: docs say validator contracts are preflighted
    before overwrite cleanup or manifest creation.
  - Previous evidence: that guarantee was true for the CLI path but not direct
    `evolve()` calls.
  - Status: direct `evolve()` now preflights default and staged validators
    before `ProgramDatabase` cleanup/manifest writes. README-adjacent docs now
    describe the evaluator-contract preflight as applying to CLI and direct
    runtime calls.

- [x] Document and fix default setup-file shape validation.
  - README/problem-format evidence: the required problem layout shows
    `task_description.txt`, `metrics.yaml`, `validate.py`, and optional
    context manifests as files.
  - Previous evidence: directory-shaped setup-file paths could be accepted or
    could surface raw host filesystem exceptions during problem loading.
  - Status: loader validation now rejects directory-shaped, symlinked, or
    junction-backed required setup files and context manifests before reading.
    README and problem-format docs state the regular-file requirement.

- [x] Document and enforce strict metric/context schema keys.
  - README/problem-format evidence: docs present `metrics.yaml` and
    `context.yaml` as structured problem-format files with loader diagnostics.
  - Previous evidence: unsupported root `metrics.yaml` fields were ignored, and
    mixed-type metric-entry or context-manifest keys could surface raw Python
    `TypeError` exceptions.
  - Status: loader validation now rejects unsupported top-level metric-schema
    fields and non-string mapping keys in metrics and context manifests.
    README/problem-format docs state that unsupported root metric fields are
    rejected.

- [x] Document and enforce direct runtime `Problem` setup validation.
  - README/problem-format evidence: docs describe problem setup failures for
    malformed metrics, missing validators, empty tasks, and missing seeds before
    artifact preparation or evolution starts.
  - Previous evidence: direct `Problem(...)` objects could bypass empty-task
    and no-seed checks until `evolve()` wrote completed zero-evaluation
    manifests.
  - Status: `evolve()` now rechecks non-empty task text and seed presence
    before database writes, while docs explain that direct `Problem(...)`
    remains lightweight for tests/integrations.

- [x] Document and enforce full-workspace evolve-block validation after
  mutations.
  - README/problem-format evidence: docs describe evolve-block markers as a
    skeleton-preservation contract for candidate files.
  - Previous evidence: mutation success validated only the touched target file,
    allowing malformed untouched sibling markers and malformed newly created
    file markers to persist.
  - Status: successful workspace mutations now revalidate the full resulting
    file set, and README/problem-format docs state that marker structure is
    checked across newly created files and untouched siblings.

- [x] Document and fix evolve-block parsing after tokenizer failures.
  - README/problem-format evidence: docs describe evolve-block markers as a
    stable skeleton/evolvable-region contract while presenting LibreEvolve as
    Python-first.
  - Previous evidence: Python tokenization failures could make raw marker lines
    disappear from marker validation.
  - Status: marker parsing now fails closed with a tokenization diagnostic when
    raw marker lines are present but cannot be classified, and docs state that
    boundary.

- [x] Document and fix empty `Program.files` with declared `primary_file`.
  - README/run-artifact evidence: docs describe history rows as carrying
    `files` plus `primary_file` for workspace candidates, which implies the
    primary file can be found in the file set.
  - Previous evidence: `Program(fitness=0.0)` left `files == {}` while
    `primary_file == "main.py"`, and direct database logging preserved that
    shape even though `program.workspace()` would reconstruct an empty
    `main.py` file.
  - Status: `Program.__post_init__()` now canonicalizes empty records to
    `{"main.py": ""}` before persistence, and README/problem-format docs state
    the behavior.

- [x] Document and fix unsafe `primary_file` persistence on empty program rows.
  - README/run-artifact evidence: docs describe candidate paths as normalized
    and workspace-safe, which can imply `primary_file` is safe whenever it is
    persisted in history.
  - Previous evidence: `Program.__post_init__()` skipped path normalization
    when both `files` and `code` were empty, so unsafe primary paths could be
    written to `history.jsonl`.
  - Status: empty `Program` construction now validates `primary_file` through
    `CandidateWorkspace`, and the README scopes persisted empty records to a
    coherent default primary file.

- [x] Document and enforce objective-schema manifest validation at all run
  construction paths.
  - README/run-artifact evidence: README and `docs/run-artifacts.md` state that
    run manifests persist the effective problem objective schema under
    `manifest.problem.objective_schema`.
  - Previous evidence: that statement was true for normal `evolve()` runs, but
    direct `ProgramDatabase` construction accepted arbitrary objective-schema
    JSON or omitted the field entirely.
  - Status: the database manifest boundary now requires and validates the
    objective schema before writing startup artifacts, and README/run-artifacts
    docs state that direct callers are covered.

- [x] Document and validate direct archive-admission thresholds.
  - README/run-artifact evidence: archive-admission metadata includes the
    threshold that governed candidate insertion, which implies it is a
    validated finite search-policy value.
  - Previous evidence: direct `ProgramDatabase.admit()` accepted malformed
    thresholds; `threshold=nan` could enter the live archive before history
    serialization failed, and `threshold="0"` raised an unstructured
    comparison error.
  - Status: direct admission now rejects non-finite or non-numeric thresholds
    before archive mutation, and README/run-artifacts docs state that
    thresholds must be finite non-boolean numbers.

- [x] Document and fix failure-history side effects before strict persistence.
  - README/run-artifact evidence: failure history is described as durable
    failed-trial memory used for prompt feedback and inspection.
  - Previous evidence: invalid failure-history appends were quarantined, but
    `ProgramDatabase.log_failure()` still mutated `_failure_counts` and
    candidate `metadata.failure_record` before append success.
  - Status: failure-history repetition counters and `failure_record` metadata
    mirrors now update only after strict JSONL persistence succeeds, and
    README/run-artifacts docs state that boundary.

- [x] Document and fix malformed failure-summary evaluation handling.
  - README/run-artifact evidence: failure history is documented as durable
    failed-trial memory with compact evaluator diagnostics.
  - Previous evidence: malformed `evaluation.stages` payloads could crash
    before writing failure history or quarantine.
  - Status: malformed failure-stage containers and entries are now represented
    with compact `stages_diagnostic` metadata in accepted failure rows, and
    README/run-artifacts docs state that behavior.

- [x] Document and fix generated failure-history admission provenance limits.
  - README/run-artifact evidence: README describes `history.jsonl`
    `metadata.archive_admission` and `failure_history.jsonl` as durable views
    into rejected candidates.
  - Previous evidence: seed failure rows included `admission_reason` and
    `archive_admission`, but generated failure rows did not.
  - Status: generated and seed failure rows now include archive-admission
    reason/metadata when the candidate has been evaluated against the archive
    policy, and README/run-artifacts docs state that behavior.

- [x] Fix partial `show` history-schema validation for displayed fields.
  - README/run-artifact evidence: README says `show` streams `history.jsonl`
    and fails fast with line-numbered diagnostics for malformed rows, which
    should include fields it actually displays.
  - Status: `show` now validates selected display fields before printing:
    `id`, `generation`, legacy `code`, workspace `files`/`primary_file`,
    metrics shape, and archive summary fields. Tests cover malformed displayed
    rows and confirm a secret-like generation value is not echoed before
    failure.

- [x] Document and fix mixed legacy/current `show` history semantics.
  - README/run-artifact evidence: README presents `show` as a way to inspect a
    previous run and mentions both legacy history and archive-admitted modern
    selection.
  - Status: mixed legacy/current history files are now rejected with a
    line-numbered schema-mixing diagnostic. README and run-artifact docs state
    that mixed histories are unsupported by the compact view instead of
    implying that one modern row migrates the whole file.

- [x] Clarify archive-retained wording for MAP-Elites cell versus elite-list
  retention.
  - README evidence: README said `show` selected an "archive-admitted valid"
    record, which blurred behavior-cell admission and auxiliary elite-list
    retention.
  - Status: README and run-artifact docs now describe archive-retained records,
    explicit `cell_admitted`, `elite_retained`, `search_state_changed`, and
    `sampling_eligible` event fields, and the current sampling distinction:
    auxiliary elite-only retention can affect best/exploit/migration state but
    is not an occupied-cell inspiration/explore candidate.

- [x] Document metric inspiration ordering after fixing the policy.
  - README evidence: metric-aware parent/inspiration strategies need a stated
    ordering policy before they can be presented as multi-score resurfacing.
  - Status: README, configuration, and architecture docs now state that
    metric-leader sampling uses primary metric first, remaining `metrics.yaml`
    order next, and extra normalized metrics alphabetically. Tests prove the
    primary metric wins under `k=1` even when its name sorts after a secondary
    metric.

- [x] Clarify mixed inspiration sampling semantics.
  - README/config evidence: mixed inspiration wording needed to distinguish
    deterministic priority from stochastic balancing.
  - Status: README, configuration, and architecture docs now describe `mixed`
    as a deterministic priority cascade over metric leaders, novelty,
    selection-score leaders, and random fill. Tests cover repeated small-budget
    behavior and parent exclusion.

- [x] Document and fix recency sampling semantics.
  - README evidence: parent and inspiration strategies include `recency`.
  - Status: recency now uses monotonic archive update sequence before
    generation and score, and accepted history records persist that sequence.
    README, configuration, architecture, and run-artifact docs describe the
    policy.

- [x] Document and enforce typed generation requirements for direct and
  restored candidates.
  - README/API evidence: sampling docs need direct/restored program records to
    have typed generation metadata.
  - Status: `Program` construction and strict history persistence now require
    non-negative integer generations, and docs state that malformed records are
    rejected before recency sampling or accepted JSONL persistence.

- [x] Document and enforce numeric metric-vector requirements for direct
  program records.
  - README/run-artifact evidence: history metrics should not imply arbitrary
    direct JSON payloads are accepted as optimization metrics.
  - Status: README and run-artifact docs now state the direct metric-vector
    rule, and runtime validation enforces it before archive insertion or
    accepted history persistence.

- [x] Document and eliminate raw archive validity bypasses.
  - README evidence: archive wording says valid programs enter the archive and
    become search candidates.
  - Status: direct MAP-Elites/island/database archive insertion now enforces
    `evaluation.is_valid is True`, and README/run-artifact docs state that
    lower-level archive APIs cannot bypass validity-gated admission.

- [x] Document and fix direct MAP-Elites parameter validation.
  - README evidence: MAP-Elites bins, elite archive size, and performance bounds
    are archive-state controls.
  - Status: direct `MAPElites(...)` construction validates the same basic
    invariants now documented in README/run-artifacts: positive integer bins,
    positive integer elite archive size, and finite ordered performance bounds.

- [x] Document and fix best-artifact export atomicity.
  - README/run-artifact evidence: `best.py` and `best_workspace/` are the
    archived best output from a CLI run, so the pair should be complete and
    internally consistent after a successful export.
  - Status: `_write_best_artifacts()` now stages both artifacts under temporary
    paths, replaces the visible pair only after workspace materialization
    succeeds, rolls back to the previous pair on replacement failure, and is
    covered by CLI tests. README, architecture, and run-artifact docs now
    describe the staged paired export behavior.

- [x] Document and enforce strict JSON run-artifact safety beyond finite
  numbers.
  - README/run-artifact evidence: persisted histories, manifests, prompt logs,
    and plugin exports should be safe for lossless downstream JSON analysis.
  - Status: strict run-artifact writers now reject non-string JSON object keys,
    cyclic records, excessive nesting, and non-JSON-compatible values before
    writing. README and run-artifact docs describe the behavior.

- [x] Document and harden quarantine snapshot rendering.
  - README/run-artifact evidence: invalid history rows are inspectable through
    quarantine streams only if the quarantine writer survives malformed
    records.
  - Status: quarantine diagnostics now preserve the original serialization
    error and include bounded, secret-redacted, exception-safe record snapshots,
    including when `repr()` raises.

- [x] Document and persist initial seed source-artifact identity.
  - README/run-artifact evidence: seed history rows should be traceable to the
    exact `initial_programs/` file or directory that produced them.
  - Status: README, run-artifact, architecture, and problem-format docs now
    describe `seed_source_path`, `seed_source_kind`, `seed_index`, and
    `manifest.problem.seed_sources`; runtime tests prove loaded seed history
    and seed-failure rows carry those fields.

- [x] Document and implement exact workspace materialization/export snapshots.
  - README/problem-format/run-artifact evidence: multi-file candidate
    workspaces and `best_workspace/` are complete recovered artifacts only if
    stale files cannot survive target reuse.
  - Status: `CandidateWorkspace.materialize()` now removes stale non-link
    target entries after preflight, rejects link/junction roots or children,
    and writes only the current candidate file set. README, problem-format,
    architecture, and run-artifact docs describe the exact snapshot policy.

- [x] Document and reject ambiguous SEARCH/REPLACE target behavior.
  - README/problem-format evidence: SEARCH/REPLACE is the default mutation mode
    and evolve-block markers preserve skeleton code, so the replacement target
    must be well-defined.
  - Status: duplicate SEARCH matches now fail with `ambiguous_search_match`
    before partial application in whole-file and evolve-block-restricted diff
    modes. README, problem-format, architecture, and run-artifact docs describe
    the diagnostic.

- [x] Document and reject duplicate `PRIMARY` topology commands.
  - README/problem-format evidence: `PRIMARY` file-section commands choose the
    primary evolved file, so the entrypoint update should be unambiguous.
  - Status: multiple `PRIMARY` commands in one workspace mutation now fail with
    `primary:duplicate_primary_section`, and docs state that at most one
    `PRIMARY` command is allowed.

- [x] Document and reject ignored bodies in topology command file sections.
  - README evidence: topology command sections should not silently discard
    proposed body text.
  - Status: `DELETE`, `MOVE`/`RENAME`, and `PRIMARY` command sections now
    require empty bodies and fail with `unexpected_command_body`; README,
    problem-format, architecture, and run-artifact docs describe the behavior.

- [x] Document and fix `PRIMARY` commands that target files moved in the same
  mutation.
  - README/problem-format evidence: `MOVE` and `PRIMARY` topology commands
    should describe one coherent file-set mutation rather than an accidental
    sequential mini-language.
  - Status: `PRIMARY` is now validated against the final same-mutation file
    set, so it can target files created or moved by the same mutation
    independent of section order. README, problem-format, architecture, and
    tests describe the behavior.

- [x] Document and require explicit delete-primary replacement.
  - README/problem-format evidence: `PRIMARY` topology commands choose the
    primary evolved file, so deleting the current primary should not silently
    choose a replacement by sort order.
  - Status: deleting the current primary now requires an explicit replacement
    `PRIMARY`; otherwise the mutation fails with
    `primary_deleted_requires_primary` before changing the workspace.

- [x] Document and enforce plugin metadata value safety.
  - README/plugin/run-artifact evidence: docs describe plugin prompt-context
    metadata and plugin artifact metadata as useful run provenance.
  - Status: README, plugin docs, and run-artifact docs now state the value
    schema. Runtime validation enforces JSON-safe finite primitives/lists/dicts,
    rejects Unicode format controls in string values, bounds string length, and
    redacts secret-like strings before persistence.
  - Verification: focused loop tests cover unsafe value rejection and redaction
    for both `prompt_context_metadata()` and `run_artifacts_metadata()`.

- [x] Document and fix mixed-type nested config key failures.
  - README/config evidence: configuration docs say problem-local `config.yaml`
    keys and unsupported fields fail with startup diagnostics.
  - Status: nested mapping keys in configured evaluator stages, backend specs,
    and LLM feedback grader specs now reject non-string keys with path-aware
    `ConfigError` diagnostics. `docs/configuration.md` documents the direct
    `Config(...)` and `config.yaml` behavior.
  - Verification: focused config and CLI tests cover mixed non-string and
    unknown string keys.

- [x] Document and reject ambiguous candidate path spellings.
  - README/problem-format evidence: file-section paths should not imply that
    generated raw target text is silently preserved when it is actually
    rewritten by normalization.
  - Status: candidate paths with empty components, `.` components, leading
    `./`, redundant separators, or trailing separators are now rejected before
    mutation application or workspace construction. README, problem-format,
    architecture docs, and the paper index describe the stricter grammar.
  - Verification: focused candidate tests cover direct normalization and
    mutation-boundary diagnostics.

- [x] Document and restrict generated hidden candidate files.
  - README/problem-format evidence: seed workspace dotfile behavior and hidden
    context behavior should not leave generated candidate dotfiles undefined.
  - Status: README, problem-format, architecture docs, roadmap, and paper index
    now state that generated candidate paths reject dot-prefixed components.
    The implementation rejects `.env`, `.git/config`, and `pkg/.hidden.py`
    before mutation application, evaluation, or export.
  - Verification: focused candidate tests cover direct and full-mode mutation
    paths.

- [x] Document and reject overlong candidate path components.
  - README/problem-format evidence: candidate paths described as safe should be
    materializable during evaluation and best-workspace export.
  - Status: candidate path components are now limited to 255 characters and
    normalized relative paths to 1024 characters before workspace construction
    or mutation application. README, problem-format, architecture docs,
    ROADMAP, and the paper index describe the policy.
  - Verification: focused candidate tests cover boundary acceptance and
    overlong direct/mutation rejection.

- [x] Document and reject unknown full-block targets.
  - README/problem-format evidence: skeleton-preserving full-block replacement
    should make every named block target unambiguous.
  - Status: unknown named `<<<BLOCK ...>>>` sections now fail with
    `malformed_block_sections:unknown_name`, and README, architecture, and
    problem-format docs state that unknown block targets are rejected before
    partial edits.
  - Verification: focused candidate tests cover all-unknown and mixed
    known/unknown replacement payloads.

- [x] Document and fix empty-file creation in full-mode file sections.
  - README/problem-format evidence: multi-file mutation docs describe
    `<<<FILE ... >>>FILE` as the way to create or replace files in full mode.
  - Status: README, architecture, problem-format, and paper index now state
    that full-mode file sections can create intentionally empty files with
    empty or blank bodies. Runtime behavior implements that while preserving
    scoped `no_valid_changes` for existing empty files.
  - Verification: focused candidate tests cover the documented behavior.

- [x] Document missing `pyproject.toml` environment-provenance semantics.
  - README/run-artifact evidence: manifest docs describe runtime environment
    provenance, package metadata, and degraded package states.
  - Status: README, architecture, run-artifact docs, and the paper index now
    describe missing `pyproject.toml` as a typed degraded provenance state,
    including the fallback `installed_version_name` behavior.
  - Verification: focused provenance tests cover the documented missing
    package-metadata state.

- [x] Document and fix semantic `pyproject.toml` dependency schema handling.
  - README/run-artifact evidence: manifest docs describe degraded package
    provenance for invalid local package metadata.
  - Status: README, architecture, and run-artifact docs now describe
    `invalid_pyproject_schema` for syntactically valid `pyproject.toml` files
    with invalid dependency/build requirement schemas. Runtime behavior records
    that degraded state instead of manifest-ready stringified dependency rows.
  - Verification: focused provenance tests cover invalid dependency and
    build-system requirement schemas plus redacted valid direct-source specs.

- [x] Document and fix invocation-cwd Git provenance ambiguity.
  - README/run-artifact evidence: Git state and source-tree hashes should refer
    to the same implementation source when possible.
  - Status: README, architecture, and run-artifact docs now state that Git
    provenance is resolved from the hashed `libreevolve/` source tree. Runtime
    behavior calls `git_state()` with that source root rather than invocation
    `cwd`.
  - Verification: a focused loop test proves a run launched from a non-repo
    directory still resolves Git metadata from the hashed source root.

- [x] Document and fix raw dirty Git status path retention.
  - README/run-artifact evidence: Git dirty-state metadata is part of
    reproducibility provenance.
  - Status: README, architecture, and run-artifact docs now describe
    secret-redacted dirty Git `status_entries`, original-entry
    `status_entry_hashes`, `status_entry_count`, and
    `status_entries_redacted`.
  - Verification: a focused provenance test proves secret-like dirty filenames
    are redacted while ordinary path signal and raw-entry hashes remain.

- [x] Document and fix raw source/problem provenance path retention.
  - README/run-artifact evidence: source/problem tree hashes and file lists are
    reproducibility provenance.
  - Status: README, architecture, and run-artifact docs now describe
    source/problem path redaction. Secret-like source/problem paths are
    persisted as redacted text with `path_hash` / `path_redacted`, while
    ordinary relative paths remain visible.
  - Verification: focused provenance tests cover secret-like included files and
    skipped generated roots.

- [x] Document and fix skipped-source provenance hash semantics.
  - README/run-artifact evidence: source-tree and problem-tree hashes are
    reproducibility provenance, but skipped generated/cache/link inputs need a
    distinct manifest contract.
  - Status: README, architecture, run-artifact docs, and the paper index define
    `tree_hash` as included-files-only, document `skipped_hash` for skipped
    diagnostic records, and document `provenance_hash` as the combined digest
    over included-file and skipped-diagnostic state plus exclusion policy.
  - Verification: focused provenance tests cover cache-directory skipped
    diagnostics, changed skipped-source contents, and the emitted hash-scope
    fields.

- [x] Document and fix raw plugin module provenance path retention.
  - README/run-artifact evidence: manifest docs describe plugin module file
    hashes as reproducibility provenance.
  - Status: README, architecture, run-artifact docs, and the paper index now
    describe plugin path retention: project-local plugin paths are
    project-relative, external plugin paths are basename-only markers, and raw
    resolved paths are represented by `path_hash` plus `path_redacted`.
  - Verification: focused provenance tests cover project-relative and external
    secret-like plugin module paths plus missing module files.

- [x] Document and fix raw evaluator `validate_path` retention in candidate
  history.
  - README/run-artifact evidence: README and run-artifact docs describe
    evaluator hashes and problem-relative manifest provenance.
  - Status: README, architecture, run-artifact docs, and the paper index now
    describe persisted evaluator path metadata as problem-relative
    `validate_path` plus `validate_path_hash`, `validate_path_scope`, and
    `validate_path_redacted`. Runtime behavior also sanitizes nested
    configured-stage path metadata.
  - Verification: focused evaluator tests cover default, configured relative,
    configured absolute, and secret-like evaluator paths.

- [x] Document and fix cwd-dependent active generated-root exclusion.
  - README/run-artifact evidence: README and run-artifact docs describe the
    active generated run directory being skipped from problem provenance when
    it resolves inside the problem tree.
  - Status: README, architecture, run-artifact docs, and the paper index now
    state that direct helper calls resolve relative generated roots from the
    problem root and that the evolution loop passes its effective run directory
    as an absolute generated root.
  - Verification: focused provenance and loop tests cover the documented
    behavior.

- [x] Document source/problem provenance size and read-error limits.
  - README/run-artifact evidence: source/problem tree hashes are
    reproducibility evidence and need an explicit scan boundary.
  - Status: README, architecture, run-artifact docs, and the paper index now
    describe `max_file_bytes`, over-limit skipped diagnostics, read-error
    skipped diagnostics, and raw-byte hashing for binary files within the cap.
    Runtime behavior implements that policy.
  - Verification: focused provenance tests cover large, binary, and read-error
    cases.

- [x] Document plugin module provenance size/read limits.
  - README/run-artifact evidence: plugin module hashes are listed alongside
    source/problem/evaluator provenance.
  - Status: README, architecture, run-artifact docs, and the paper index now
    describe `max_file_bytes`, `skipped_max_file_bytes`, `read_error`, `ok`,
    and `missing_module_file` statuses for plugin module provenance. Runtime
    behavior implements those manifest states.
  - Verification: focused provenance tests cover successful, large, unreadable,
    external, and no-file plugin module cases.

- [x] Document or enforce safe configured plugin identifiers.
  - README/plugin-doc evidence: plugin names appear in configuration examples
    and run manifests, so they need stable, share-safe semantics.
  - Status: runtime behavior now enforces manifest-safe plugin labels and
    rejects secret-like labels at config and manifest boundaries. README,
    configuration, plugin, architecture, run-artifact, and paper-index docs
    now describe that policy while preserving the separate direct-runtime
    plugin-resolution limitation.
  - Verification: focused config, database, and CLI tests cover the enforced
    policy and docs/todo invariants remain clean.

- [x] Document or fix grouped SHA-256 values in paper download manifests.
  - README/paper-cache evidence: README and `papers/README.md` describe the
    CSV/JSON manifests as recording cached PDF SHA-256 hashes.
  - Status: both committed manifests now use canonical lowercase 64-hex digest
    strings, and README, development docs, and the paper index document
    `py -3.12 -m libreevolve.tools.paper_manifest` plus
    `--require-local-pdfs` for local byte/hash verification.
  - Verification: focused paper-manifest tests cover noncanonical grouped
    hashes, and the current 24-paper local cache validates successfully.

- [x] Document paper-manifest `ok` fields as historical, not fresh-checkout
  availability.
  - README/paper-cache evidence: README and `papers/README.md` say the PDFs are
    intentionally gitignored while committed manifests describe the cache.
  - Status: README, development docs, and `papers/README.md` now point to the
    validator report as the source for current availability. The JSON report
    distinguishes historical download metadata from local PDF presence and
    Git-tracked status.
  - Verification: focused paper-manifest tests cover present, missing, and
    tracked availability cases.

- [x] Document or enforce manifest-safe backend model identifiers.
  - README/backend-doc evidence: provider model names are examples and
    availability is not validated, but configured model strings are persisted.
  - Status: README, backend docs, configuration docs, run-artifact docs, and
    the paper index now describe the manifest-safe model-id policy. Runtime
    validation enforces that policy before manifests or call telemetry can
    persist unsafe configured model IDs.
  - Verification: focused config/database/CLI tests cover the documented
    accepted and rejected model-id shapes.

- [x] Document or fix lower-level evaluator-stage validation boundaries.
  - README/config evidence: evaluator-stage validation is documented as a
    startup guarantee.
  - Status: direct `CascadeEvaluator` construction now enforces the same stage
    schema validator used by `Config`, so invalid direct stage configs fail
    before evaluation.
  - Verification: focused evaluator tests cover numeric, seed, and cardinality
    validation at the direct evaluator boundary.

- [x] Document or enforce safe evaluator-stage label syntax.
  - README/config evidence: stage names are identifiers in structured cascade
    results and run artifacts.
  - Status: README, configuration, problem-format, run-artifact docs, and the
    paper index now describe explicit manifest-safe stage names. Runtime
    validation rejects unsafe names before persistence.
  - Verification: focused config/evaluator tests cover unsafe names.

- [x] Document or fix configured evaluator-stage collisions with built-in
  stage labels.
  - README/config evidence: stage names are user-visible diagnostics.
  - Status: configured stages are explicitly named, and `diff`, `syntax`, and
    `validate` are reserved built-in labels, eliminating the previous
    built-in/fallback collision cases.
  - Verification: focused config/evaluator tests cover reserved labels and
    missing stage names.

- [x] Document or fix mutable `Config` validation bypasses in direct APIs.
  - README/run-artifact evidence: configuration validation and manifests are
    documented as run controls, and direct API callers can mutate `Config`.
  - Status: the database manifest boundary revalidates mutable `Config`
    objects before directory preparation or manifest writes. README and
    run-artifact docs describe that direct-boundary protection.
  - Verification: database tests cover mutated run identity, scalar budgets,
    backend fields, plugin labels, and evaluator stages.

- [x] Document or enforce safe candidate/program identifiers.
  - README/run-artifact evidence: history, lineage, parent links, and archive
    admission metadata are durable run evidence.
  - Status: README and run-artifact docs now state the manifest-safe
    candidate-id policy. Runtime validation rejects unsafe direct IDs,
    `parent_id`, and lineage entries before persisted history or archive
    metadata can store them.
  - Verification: focused program/database tests cover safe IDs, unsafe IDs,
    mutation after construction, duplicate logged IDs, and failure-history
    quarantine.

- [x] Document or enforce LLM call-role label validation.
  - README/backend-doc evidence: docs describe call-role telemetry for
    mutation, critique, feedback, and meta-prompt calls.
  - Status: README, backend, architecture, and run-artifact docs now state that
    call roles are validated before scheduler selection. Runtime validation
    rejects blank, non-string, malformed, and secret-like role labels.
  - Verification: focused ensemble/config tests cover unsafe role labels.

- [x] Document or fix mutable `last_call` telemetry exposure.
  - README/backend-doc evidence: README and run-artifact docs describe LLM call
    telemetry as provenance attached to candidates, feedback, and prompt
    history.
  - Status: `LLMEnsemble.call_history` and `last_call` now expose deep-copied
    snapshots instead of live internal records.
  - Verification: focused ensemble tests prove caller mutation cannot alter
    stored call history.

- [x] Document or enforce safe feedback-grader labels.
  - README/config evidence: `llm_feedback` grader specs are run configuration
    and evaluation metadata.
  - Status: configuration docs now describe the manifest-safe feedback label
    grammar. Runtime validation rejects unsafe configured and direct feedback
    names/metrics before manifest persistence, LLM calls, or metric writes.
  - Verification: focused config/feedback tests cover blank, control-character,
    secret-like, and direct unsafe labels.

- [x] Document or fix direct ensemble retry/fallback coercion.
  - README/config evidence: README and configuration docs describe
    `llm_max_retries` as a non-negative integer and `llm_fallback` as a boolean
    switch.
  - Status: direct `LLMEnsemble` construction now enforces those same type and
    range constraints. README/backend/config docs state that direct scheduler
    construction validates retry/fallback controls.
  - Verification: focused ensemble tests cover invalid direct retry/fallback
    inputs.

- [x] Document or fix direct ensemble strategy validation.
  - README/backend-doc evidence: scheduler strategy names are documented as
    meaningful modes.
  - Status: direct `LLMEnsemble` construction now rejects unsupported strategy
    names, and docs describe constructor-level scheduler validation.
  - Verification: focused ensemble tests cover invalid direct strategies.

- [x] Document or fix direct ensemble exploration-coefficient validation.
  - README/backend-doc evidence: README describes UCB-style routing.
  - Status: direct `LLMEnsemble` construction now rejects invalid exploration
    coefficients, and docs describe constructor-level scheduler validation.
  - Verification: focused ensemble tests cover negative, non-finite, boolean,
    and nonnumeric coefficients.

- [x] Document or fix direct ensemble backend-metadata validation.
  - README/backend-doc evidence: per-call telemetry records backend metadata
    and scheduler state.
  - Status: direct `LLMEnsemble` construction now validates backend metadata
    cardinality and JSON safety, and docs describe constructor-level metadata
    validation.
  - Verification: focused ensemble tests cover malformed metadata and copied
    successful telemetry.

- [x] Document or fix direct prompt reward-policy validation.
  - README/config evidence: prompt reward bounds, reward mode, and prompt
    exploration are documented as normal prompt-program scoring controls.
  - Status: direct `PromptDatabase` construction now enforces strictly
    increasing reward bounds, supported reward modes, and finite non-negative
    exploration coefficients. README, configuration, architecture, and
    run-artifact docs describe the direct-boundary invariant.
  - Verification: focused prompt tests cover invalid direct reward-policy
    inputs and docs tests cover the documented artifact surfaces.

- [x] Document or fix invalid prompt-program state and duplicate id records.
  - README/run-artifact evidence: `prompt_history.jsonl` is documented as
    prompt-program selection, scoring, and lineage evidence.
  - Status: prompt programs now validate manifest-safe ids, parent ids,
    non-negative integer counters, finite reward sums, and JSON-safe metadata
    before archive writes. Duplicate ids and unknown parents are rejected
    before `prompt_history.jsonl` mutation.
  - Verification: focused prompt tests cover invalid direct prompt-program
    state, revalidation after caller mutation, duplicate id rejection before
    logging, and unknown parent rejection.

- [x] Document or fix dangling prompt-program id failures.
  - README/run-artifact evidence: generated candidates and prompt rewards are
    linked to prompt programs through prompt-program ids.
  - Status: README and run-artifact docs now describe bounded
    `prompt_reference_error` diagnostics, and runtime scoring/mutation paths
    raise `StrictJsonlError` instead of raw lookup errors for missing or
    invalid prompt ids.
  - Verification: focused prompt tests cover missing references and secret-safe
    invalid-id diagnostics; docs tests cover the updated documented surfaces.

- [x] Document or implement evidence-conditioned meta-prompt mutation.
  - README/run-artifact evidence: prompt programs are selected, scored, logged,
    and optionally mutated, so the mutation step should reflect recorded
    prompt-performance evidence.
  - Status: README and run-artifact docs describe the bounded redacted
    prompt-performance evidence block and persisted `mutation_context`
    provenance. Runtime meta-prompt calls now include reward policy, selected
    prompt statistics, latest candidate outcome, prompt-arm summaries, and
    recent failures.
  - Verification: focused loop tests prove evidence rendering, secret
    redaction, and prompt-history metadata persistence.

- [x] Document or fix blank explicit prompt-template fallback.
  - README/config evidence: configured prompt variants and prompt-program
    templates are documented as validated prompt inputs, which implies an
    explicit direct template is validated rather than ignored.
  - Status: direct `PromptSampler.build(..., template=...)` calls now reject
    blank explicit strings; docs state that only `template is None` means
    sample/fallback to configured or default templates.
  - Verification: focused prompt tests cover blank explicit templates and
    `None` fallback behavior.

- [x] Document and implement prompt-visible PDF page-span precision.
  - README evidence: README says prompt citations expose PDF page/span evidence
    for the rendered excerpt.
  - Status: prompt context headers now render exact `page:start-end` span
    citations when available, exact non-contiguous page lists when only excerpt
    pages are available, and document-level page ranges only as fallback.
    README, architecture, problem-format, run-artifact docs, and the paper
    index now describe exact prompt-visible PDF excerpt page/span citations.
  - Verification: focused prompt/loader tests cover span rendering,
    non-contiguous page-list rendering, and fallback page ranges; docs tests
    cover the updated documentation surfaces.

- [x] Document and enforce safe explicit-context source path labels.
  - README/problem-format evidence: selected context source labels are prompt
    context and run-manifest provenance.
  - Status: problem loading now rejects selected context source paths whose
    relative labels look secret-like. README, problem-format, architecture, and
    run-artifact docs describe that source labels are rejected before prompt
    rendering or manifest persistence.
  - Verification: focused loader tests cover rejected secret-like selected
    context source labels; docs tests cover the updated documentation surfaces.

- [x] Document and enforce safe explicit-context manifest pattern labels.
  - README/problem-format evidence: `context.yaml` include/exclude patterns are
    reproducible context-selection policy and are persisted in run artifacts.
  - Status: problem loading now rejects secret-like include/exclude pattern
    labels before `context_policy` persistence. README, problem-format,
    architecture, and run-artifact docs describe the safe-pattern boundary.
  - Verification: focused loader tests cover rejected secret-like include and
    exclude patterns; docs tests cover the updated documentation surfaces.

- [x] Document context excerpt limits as distinct from ingestion limits.
  - README/problem-format evidence: docs expose `max_chars_per_source`, which
    can be read as bounding local file reads and PDF extraction work.
  - Status: context ingestion now has separate resource limits:
    `max_bytes_per_source`, `max_total_bytes`, `max_pdf_pages`, and
    `max_pdf_chars`. README, problem-format, architecture, and run-artifact
    docs describe `max_chars_per_source` as a rendered prompt-excerpt limit and
    the new fields as load/extraction budgets.
  - Verification: focused loader tests cover configured byte and PDF extraction
    budgets; docs tests cover the updated documentation surfaces.

- [x] Document and implement context-manifest glob directory semantics.
  - README/problem-format evidence: context manifest include/exclude entries
    are documented as problem-relative globs using forward slashes, so root and
    recursive behavior must be predictable.
  - Status: context manifest matching is now path-segment aware. README and
    problem-format docs state that `*.md` matches only root context files,
    `nested/*.md` matches one segment under `nested/`, and `**/*.md` matches
    recursively.
  - Verification: focused loader tests cover root-only `*.md`, recursive
    `**/*.md`, and excluded nested matches.
- [x] Document or fix linked core problem-file behavior.
  - README/problem-format evidence: README documents link rejection for
    context and seed workspace inputs and says source/problem provenance skips
    links with `link_not_followed`, which can imply all problem-defining inputs
    share that boundary.
  - Previous evidence: the active todo still claimed `task_description.txt` and
    `metrics.yaml` were read by the loader without an `_is_link()` check.
  - Current status: implemented and documented. `load_problem()` now calls
    `_require_problem_file()` for `task_description.txt`, `metrics.yaml`, and
    `validate.py`, and that helper rejects linked paths before content reads.
    README and problem-format docs state that directory-shaped, symlinked, or
    junction-backed required setup files are rejected. Remaining dedicated
    symlink/junction regression tests stay tracked in code/roadmap/papers.

- [x] Correct plugin-doc alias-hardening wording.
  - README/docs evidence: `docs/plugins.md` previously said broader configured
    plugin alias hardening for whitespace and secret-like text remained open.
  - Status: plugin docs now state the current manifest-safe label contract:
    configured plugin aliases must be non-empty strings matching
    `[A-Za-z0-9][A-Za-z0-9_.-]{0,127}` and must not look like secrets. Direct
    configured-versus-loaded plugin state remains documented as open.
  - Verification: current-code proof and config tests show whitespace,
    secret-like, empty, and Unicode-format-control plugin labels are rejected,
    while `causal` is accepted.

- [x] Document or fix partial redaction of quoted secret assignments.
  - README/run-artifact evidence: docs describe redaction across diagnostics,
    evaluator output, histories, manifests, and plugin/runtime artifacts.
  - Status: fixed in the shared redaction helper. Whitespace-containing quoted
    secret assignments are fully redacted rather than leaving the quoted tail
    visible.
  - Verification: `py -3.12 -m pytest tests/core/test_redaction.py --tb=short`
    passes with cases for `api_key="abc def ghi"`,
    `password='hunter2 extra'`, and `token: "Bearer abc def"`.

- [x] Document or fix uppercase provider-token redaction behavior.
  - README/runtime-safety evidence: README describes redacted stdout/stderr,
    artifacts, provenance, and diagnostics, which can imply the shared redactor
    catches provider-key shapes consistently.
  - Status: fixed in `redact_sensitive_text()`. Known standalone provider-token
    prefixes are matched case-insensitively.
  - Verification: `py -3.12 -m pytest tests/core/test_redaction.py --tb=short`
    passes with `SK-PROJ-UPPERSECRET1234567890`,
    `GHP_UPPERSECRET1234567890`, and mixed-case GitHub-token fixtures.

- [x] Document the actual secret-redaction grammar or broaden it.
  - README/run-artifact evidence: README wording around redacted evaluator
    output and copied artifacts can be read as broad secret protection.
  - Status: broadened for the documented bearer-header examples.
    `Authorization: Bearer ...` and `authorization: Bearer ...` credential
    values are redacted before provider-token scanning.
  - Verification: `py -3.12 -m pytest tests/core/test_redaction.py --tb=short`
    passes with `hf_...` and `xoxb-...` bearer-header examples.

- [x] Document or enforce share-safe `eval_stages[].seeds[]` values.
  - README/config evidence: README and configuration docs present stage seeds
    as operational cascade inputs carried through structured cascade records,
    retries, samples, and run artifacts.
  - Status: enforced through shared eval-stage validation. Secret-like string
    seeds are rejected before evaluator metadata or retry-attempt records are
    created.
  - Verification: `py -3.12 -m pytest tests/core/test_config.py
    tests/core/test_redaction.py --tb=short` passes with the documented
    `sk-proj_stageseedsecret1234567890` shape and related redaction grammar.
- [x] Document or enforce immutable evaluator-stage definitions.
  - README/config evidence: README and configuration docs describe
    `eval_stages` as checked before a run starts, which implies the stage
    contract used by the evaluator is the validated one.
  - Previous evidence: `CascadeEvaluator` kept a reference to the caller's
    mutable stage list. A local proof mutated a previously valid stage after
    construction so `samples` became `"not-an-int"`; evaluation then raised a
    raw `ValueError` instead of using the originally validated sample count.
  - Status: enforced in code. `CascadeEvaluator` snapshots configured stages
    with a deep copy before validation and retains that validated copy, so
    post-construction mutations of caller-owned lists/dicts cannot affect the
    evaluator cascade.
- [x] Document or enforce immutable LLM backend lists.
  - README/backend-doc evidence: README and backend docs describe
    `LLMEnsemble` construction as validating scheduler controls and backend
    metadata, which can imply the backend arm set is stable after construction.
  - Previous evidence: direct `LLMEnsemble` kept the original backend list by
    reference. A local proof appended a backend after construction and produced
    `IndexError` on the next `generate()` because `counts`/`wins` still had the
    original length; clearing the list produced a raw `AssertionError`.
  - Status: enforced in code. `LLMEnsemble` copies the backend list at
    construction, so post-construction mutations of the caller-owned list do
    not change scheduler arms or telemetry indexing.
- [x] Document or enforce immutable `CandidateWorkspace` snapshots.
  - README/problem-format evidence: README and problem-format docs describe
    workspace candidates as validated local text file sets with safe paths,
    text contents, and a present primary file.
  - Previous evidence: direct callers could mutate `CandidateWorkspace.files`
    or `primary_file` after construction and bypass those invariants. A local
    proof produced raw `KeyError` for a missing mutated primary file, a
    materialization `ValueError` for a post-added unsafe path, and a raw
    `TypeError` for post-added non-string file contents.
  - Status: enforced at key workspace-use boundaries. `CandidateWorkspace`
    revalidates and snapshots state before `code`, `to_dict()`, and
    `materialize()` operations, so mutated workspaces fail through the normal
    candidate validation path.
- [x] Document or enforce immutable prompt-program archive records.
  - README/meta-prompt evidence: README and prompt docs describe prompt
    variants and meta-prompt evolution as archive/database-backed runtime
    state, which implies admitted prompt records remain validated after they
    enter selection and history.
  - Previous evidence: direct callers could mutate a `PromptProgram` after
    `PromptDatabase.add()` or mutate the live object returned by
    `PromptDatabase.all()`, changing selected archive templates after
    admission.
  - Status: enforced in code. `PromptDatabase` stores defensive copies and
    returns copied prompt-program snapshots from archive query/selection APIs,
    so caller-owned mutations no longer alter admitted prompt records.
- [x] Document or enforce normalized-metric validation for metric sampling.
  - README/search evidence: README and architecture docs describe metric-aware
    parent and inspiration sampling, which can imply sampled metric leaders are
    derived from declared metric directions and bounds.
  - Previous evidence: `IslandModel` trusted `Program.metadata.normalized_metrics`
    without range or schema checks. A direct proof made a low-score program
    with `normalized_metrics.score=999.0` the selected metric parent ahead of
    an honest `0.9` normalized-score candidate.
  - Status: enforced in code. Metric leader sampling filters normalized metric
    values to finite numbers within `[0, 1]` and honors configured metric order
    as the declared metric-name allowlist.
- [x] Document or validate direct inspiration sample-count arguments.
  - README/API evidence: docs describe configurable `num_inspirations` and
    parent/inspiration strategies as run controls, which can imply sample counts
    are validated wherever the archive/database API is used.
  - Previous evidence: direct archive calls bypassed config validation. A proof
    called `MAPElites.sample_diverse(k="2")` and
    `IslandModel.sample_diverse(k="2")`, producing raw `TypeError`s; `k=True`
    and `k=1.5` returned one sampled program.
  - Status: enforced in code. Direct sampling `k` arguments are validated as
    non-boolean non-negative integers at MAP-Elites, island, and program
    database boundaries; `k=0` returns no inspirations.

- [x] Document or validate direct sampling exclusion containers.
  - README/API evidence: parent and inspiration sampling docs describe
    deduplicated inspiration sets and parent exclusion, which can imply the
    underlying exclusion id inputs are typed and deterministic.
  - Previous evidence: direct `MAPElites.sample_diverse()` and
    `IslandModel.sample_diverse()` accepted arbitrary membership containers,
    so strings, mappings, and custom `__contains__` objects could alter
    sampling semantics.
  - Status: validated in code. Direct `exclude_ids` inputs are now normalized
    to immutable sets only when provided as set/frozenset/list/tuple
    collections of manifest-safe program ids; malformed containers and ids are
    rejected before archive sampling.

- [x] Document or fix backend metadata key-label validation.
  - README/backend-doc evidence: backend docs describe validated JSON-safe
    backend metadata in LLM telemetry, which can imply both keys and values are
    safe durable labels.
  - Previous evidence: direct `LLMEnsemble` metadata validation rejected
    secret-like values but not secret-like or display-confusing keys, allowing
    unsafe labels to be retained under `backend_metadata`.
  - Status: fixed in code. Backend metadata keys are now validated recursively
    as manifest-safe, secret-safe labels before call telemetry can be
    constructed or persisted by higher-level run history.

- [x] Document or enforce `Program.metadata` object requirements.
  - README/run-artifact evidence: README and run-artifact docs describe
    `history.jsonl` metadata as structured candidate provenance for prompts,
    archive admission, LLM calls, budget state, and plugin/evaluator feedback.
  - Previous evidence: the code did not require metadata to be an object:
    `Program(metadata=[])` could persist a JSON array, and
    `metadata=["bad"]` could crash archive admission with a raw Python
    conversion error.
  - Status: enforced in code. `Program.metadata` must now be a JSON-safe
    mapping at model construction and database mutation/log boundaries; direct
    malformed metadata is rejected before history, archive, or failure-record
    side effects.

- [x] Document or enforce JSON-native direct `Program.metrics` values.
  - README/run-artifact evidence: README describes persisted metrics as
    structured experiment evidence and `show`/history artifacts as inspectable
    outputs.
  - Previous evidence: direct string and boolean metrics were rejected, but
    finite `numbers.Real` subclasses such as `Fraction` could fail only at
    strict JSON persistence time.
  - Status: enforced in code. Direct/programmatic metric construction and
    database/archive boundaries now require JSON-native finite numeric metric
    values; unsupported numeric objects are rejected before search-state
    mutation, while log-time malformed metrics still use the strict history
    diagnostic/quarantine path.

- [x] Document or enforce direct LLM feedback numeric-policy validation.
  - README/config evidence: README describes configured feedback graders and
    validation, which can imply feedback score composition is consistently
    validated across the supported API surface.
  - Previous evidence: configured `llm_feedback` was validated through
    `Config`, but direct `apply_llm_feedback()` did not prevalidate `weight`
    or `min_score`, allowing raw conversion errors after the feedback score
    was parsed.
  - Status: enforced in code. Direct feedback graders now use the same finite
    numeric policy before prompt generation; malformed direct policy fields
    are reported as structured `invalid_feedback_config` records.

- [x] Document or fix non-finite evaluator diagnostics in feedback prompts.
  - README truthfulness evidence: README describes optional LLM feedback and
    structured diagnostics, which can imply reviewer prompt payloads are
    ordinary JSON.
  - Previous evidence: `_render_feedback_diagnostics()` emitted default
    `json.dumps(...)` output, so non-finite evaluator values appeared in
    prompts as `NaN` and `Infinity`.
  - Status: fixed in code. Feedback diagnostic prompt payloads now render as
    strict finite JSON with explicit non-finite diagnostic markers instead of
    non-standard JSON tokens.

- [x] Document or fix structured failure mutation-text redaction.
  - README/run-artifact evidence: failed-trial memory is documented as bounded
    prompt feedback, and evaluator summaries are described as redacted, which
    can imply the whole failed-trial prompt block follows that policy.
  - Previous evidence: structured failure records rendered `mutation_text`
    without redaction, so secret-like values could survive in the prompt's
    `mutation=` fragment.
  - Status: fixed in code. Structured failure mutation snippets and direct
    error fields now use the same bounded/redacted prompt helper as evaluator
    summaries before prompt rendering.

- [x] Document or fix failed-trial prompt score rendering.
  - README/run-artifact evidence: failed-trial memory is described as bounded
    prompt-visible feedback, so rendered score fields should not imply
    malformed records contain meaningful normalized fitness.
  - Previous evidence: structured recent-failure records with `score=True` and
    `score=float("nan")` rendered as `Score 1.00` and `Score nan` in mutation
    prompts.
  - Status: fixed in code. Failed-trial score rendering now marks malformed
    prompt-visible scores as `unknown` instead of formatting them as plausible
    fitness values.
- [x] Document or validate malformed recent-failure prompt-memory inputs.
  - README/run-artifact evidence: README describes failed-trial memory as
    persisted with error causes and bounded prompt-visible examples, which can
    imply direct prompt construction handles malformed failure-memory records
    predictably.
  - Implemented evidence: direct `PromptSampler.build()` calls now validate
    recent-failure container and item shape before rendering. Bad containers
    and malformed records render bounded diagnostics; valid structured records
    and exactly two-item legacy tuples continue to render.
  - Verification: focused prompt tests cover one-item tuples, overlong tuples,
    string containers, list records, object records, malformed structured
    fields, and the valid legacy tuple compatibility path.
- [x] Document or fix provider exceptions that cannot be stringified.
  - README/backend evidence: README says failed LLM calls are recorded as
    normalized telemetry with redacted/bounded provider errors.
  - Implemented evidence: `_provider_error_text()` now catches exception-message
    formatting failures and emits a bounded fallback diagnostic, so failed-call
    telemetry is appended even when a provider exception's `__str__()` raises.
  - Verification: ensemble tests assert call history, scheduler totals,
    counts, retry/fallback flags, and redacted error text for malformed
    provider exception objects.
- [x] Document or fix unredacted LLM feedback failure messages.
  - README/run-artifact evidence: README says malformed LLM feedback responses
    and provider failures are recorded as feedback-failure metadata, but it
    does not make clear that provider exception messages themselves are stored
    raw.
  - Implemented evidence: `apply_llm_feedback()` now records failed grader
    exception messages through a safe formatter that survives broken
    `__str__()`, redacts shared secret patterns, and bounds message length
    before storing `evaluation.metadata.llm_feedback[].message`.
  - Verification: `py -3.12 -m pytest tests/core/test_feedback.py --tb=short`
    passed with coverage for oversized secret-like provider messages and
    exceptions that cannot be stringified.
- [x] Document or enforce non-empty LLM prompts at the ensemble boundary.
  - README/backend-doc evidence: examples and backend sections describe task
    prompts, templates, and context-bearing mutation requests, which can imply
    the LLM boundary will not spend provider calls on blank prompts.
  - Implemented evidence: direct `LLMEnsemble.generate()` now rejects empty and
    whitespace-only prompts before provider calls and scheduler state changes.
  - Verification: ensemble tests prove blank prompt strings and blank
    template-rendered prompts do not call backends or mutate scheduler/call
    history state.
- [x] Document or fix direct backend adapter prompt validation.
  - README/backend-doc evidence: README describes LLM prompts as generated by
    LibreEvolve and call telemetry as prompt-size/hash evidence, which can
    imply adapter calls receive validated text prompts even when used through
    the library surface.
  - Implemented evidence: bundled OpenAI, Anthropic, and Ollama adapters now
    call the shared prompt validator before provider SDK payload construction;
    `docs/backends.md` documents direct adapter non-empty text prompt
    validation.
  - Verification: `tests/llm/test_backends.py` covers OpenAI non-string,
    Anthropic empty, and Ollama whitespace-only direct calls before provider
    SDK calls.
- [x] Document or fix direct backend adapter parameter validation.
  - README/backend-doc evidence: README and backend docs describe backend specs
    as validated model ids and token limits, which can imply the invariant
    applies to the adapters themselves rather than only `Config`/CLI creation.
  - Implemented evidence: bundled OpenAI, Anthropic, and Ollama adapter
    constructors now validate manifest-safe model ids and positive integer
    token limits before provider calls; OpenAI also validates direct
    `reasoning_effort` values. `docs/backends.md` documents this constructor
    boundary.
  - Verification: `tests/llm/test_backends.py` covers invalid direct
    model/token/reasoning parameters and valid manifest-safe direct parameters.
- [x] Document or fix perpetually untried failed-backend fallback behavior.
  - README/backend-doc evidence: README describes retry/fallback routing and a
    pull-once initialization policy for the UCB-style scheduler, which can imply
    the router eventually moves past unavailable backends.
  - Implemented evidence: exhausted failed backend selections now count as
    zero-reward pulls, so unavailable backends do not remain in the untried
    bucket forever after recovered fallback.
  - Verification: docs/backends.md describes the accounting rule and ensemble
    tests prove a rewarded fallback backend can be selected without repeatedly
    paying the same failed-backend tax.
- [x] Document or fix backend-object telemetry validation limits.
  - README/backend-doc evidence: backend docs describe normalized call
    telemetry with backend identity and API-mode fields, which can imply those
    fields are manifest-safe run metadata.
  - Implemented evidence: `LLMEnsemble._call_record()` now normalizes unsafe
    backend object `name` and `api_mode` attributes into safe telemetry fields
    plus structured diagnostics before call-history and candidate-history
    persistence. `docs/backends.md` documents this behavior.
  - Verification: tests cover secret-like backend names, non-JSON API modes,
    backend telemetry attribute errors, strict JSON serialization, and
    candidate history persistence.
- [x] Document or fix post-validation mutation of configured backend specs.
  - README/backend-doc evidence: README and backend docs describe configured
    backend specs as validated model/provider controls, which can imply the
    effective specs used by `build_llm()` remain the validated specs.
  - Implemented evidence: `build_llm(config)` revalidates and copies the
    effective backend specs before adapter construction; docs/backends.md now
    documents that post-validation mutation cannot silently alter backend
    type, model id, token limits, scheduler metadata, or role labels.
  - Verification: ensemble tests cover post-validation mutation and prove
    valid copied specs are isolated from later caller mutation.
- [x] Document or reject whitespace-only backend outputs.
  - README/backend-doc evidence: backend telemetry docs describe successful LLM
    calls as output-bearing provider samples, which can imply blank-looking
    responses are not counted as useful backend pulls.
  - Implemented evidence: `LLMEnsemble.generate()` now rejects whitespace-only
    backend responses before success accounting, and `docs/backends.md`
    documents empty/whitespace/non-text response handling.
  - Verification: ensemble tests cover whitespace-only direct backend outputs.
- [x] Document or enforce LLM response-size limits.
  - README/backend-doc evidence: README describes LLM calls, output hashes, and
    mutation parsing, which can imply generated responses are bounded by
    configured provider/run budgets.
  - Status: README, backend docs, and configuration docs now describe
    `llm_max_response_chars` / `--llm-max-response-chars`, its `100000`
    default, and the over-limit failure semantics before success accounting,
    output hashing, mutation parsing, prompt-history retention, and candidate
    metadata capture. Direct `LLMEnsemble` construction validates the same
    accepted-response size control.
  - Verification: focused scheduler/config/CLI tests passed with
    `py -3.12 -m pytest tests/llm/test_ensemble.py tests/core/test_config.py
    tests/test_cli.py --tb=short`.

- [x] Document or enforce bounded LLM retry counts.
  - README/config evidence: README and configuration docs expose
    `llm_max_retries` as a retry control, which can imply it is a bounded
    budget knob.
  - Status: `llm_max_retries` is now enforced as an ensemble-layer retry count
    in the inclusive range `0..10` at both `Config` validation and direct
    `LLMEnsemble` construction. README, backend docs, configuration docs, and
    architecture docs state the cap and preserve the caveat that built-in
    provider adapters still perform their own internal three-attempt retry
    loops, so this is not a complete provider API attempt budget.
  - Verification: focused scheduler/config/CLI tests passed with
    `py -3.12 -m pytest tests/llm/test_ensemble.py tests/core/test_config.py
    tests/test_cli.py --tb=short`.

- [x] Document or fix mutable LLM scheduler counter lists.
  - README/backend-doc evidence: backend docs describe UCB-style reward
    accounting, retry/fallback telemetry, and validated scheduler controls,
    which can imply scheduler state remains finite and coherent after
    construction.
  - Status: scheduler counter reads now return defensive copies and
    `restore_scheduler_state()` is documented as the validated direct
    restoration path. README, backend docs, configuration docs, and architecture
    docs describe the defensive-copy and restore-validation behavior.
  - Verification: focused ensemble tests cover direct mutation attempts and
    malformed restored scheduler-state inputs.

- [x] Document whether LLM call roles reach provider backends.
  - README/backend-doc evidence: README describes role-aware LLM call telemetry
    for mutation, critique, feedback, and meta-prompt calls, and backend docs
    discuss backend scheduling concepts. That can imply custom backends can
    react to the call role when generating provider requests.
  - Status: `LLMEnsemble.generate()` now passes the validated role to the
    selected backend as `generate(prompt, role=role)` for original, retry, and
    fallback attempts. README, backend docs, configuration docs, and
    architecture docs state that bundled adapters accept but ignore the keyword
    while custom protocol-compatible backends can consume it.
  - Verification: focused ensemble tests cover a role-aware custom backend and
    retry/fallback propagation for `role="critique"`.

- [x] Document or enforce immutable backend scheduler metadata.
  - README/backend-doc evidence: README and backend docs describe backend
    metadata as validated scheduler controls for cost, latency, depth, and
    role, which can imply those controls remain valid after construction.
  - Status: backend metadata reads now return defensive copies, and README,
    backend docs, configuration docs, and architecture docs state that
    scheduler metadata/state accessors are defensive snapshots. Live scheduler
    metadata remains private after construction.
  - Verification: focused ensemble tests cover post-construction mutation of
    returned backend metadata and prove selection/telemetry remain valid.

- [x] Document or fix duplicate backend reward updates per pull.
  - README/backend-doc evidence: docs say backend reward updates are capped to
    `1.0`, which can read as keeping UCB-style empirical rewards bounded.
  - Status: fixed and documented. Backend rewards are now one-shot successful
    call records, not independent repeated numeric updates. README, backend
    docs, and configuration docs state that reward state includes rewarded and
    unrewarded call ids for resume/replay safety.
  - Verification: focused ensemble and loop tests cover rejected duplicate
    reward updates and call-id propagation from `evolve()`.

- [x] Document or normalize throughput/depth metadata scale.
  - README/backend-doc evidence: README and backend docs describe
    `throughput_depth` as using numeric `cost`, `latency`, and `depth`
    metadata, but did not define their units, expected ranges, or how they
    trade off against observed rewards.
  - Status: implemented and documented. README, backend docs, configuration
    docs, and run-artifact docs now describe the min/max normalization policy,
    neutral equal-field value, fixed bounded weights, and telemetry retention.
  - Verification: focused ensemble tests prove extreme raw metadata no longer
    dominates a full reward advantage and call telemetry persists the effective
    scheduler policy.

- [x] Document or fix process-global RNG mutation during runs.
  - README evidence: seed/replay docs describe `--seed` as controlling local
    stochastic choices, which can imply the seed is scoped to the run.
  - Status: fixed and documented. `evolve()` no longer calls
    `random.seed(config.seed)` or uses process-global `random.random()` for
    framework parent-selection decisions. Framework-owned loop, prompt,
    database, island, and MAP-Elites random choices use a run-local
    `random.Random` instance seeded from `Config.seed`. README and
    configuration docs now state that process-global RNG state is not reseeded
    or advanced by LibreEvolve framework sampling.
  - Verification: focused loop and database tests prove `evolve()` and random
    database sampling leave caller global RNG state unchanged.

- [x] Document or enforce seed/candidate budget-event validation.
  - README/run-artifact evidence: README describes separate seed and candidate
    evaluation counters, which can imply those fields are typed runtime facts
    rather than truthiness-derived bookkeeping.
  - Status: enforced and documented. `RunBudget.record_evaluation()` now
    accepts only exact boolean seed/candidate event flags, and run-artifact docs
    state that malformed direct/controller calls fail before counters mutate.
  - Verification: focused budget tests cover valid and malformed direct
    evaluation-kind inputs.

- [x] Document or enforce finite run-budget counters.
  - README/run-artifact evidence: README says manifests record consumed
    evaluation/generation budgets, which implies those counters are reliable
    strict JSON accounting fields.
  - Status: direct elapsed-time accounting now enforces finite non-negative
    numeric values before counter mutation, and run-artifact docs state that
    malformed budget elapsed times fail before counters mutate.
  - Verification: focused budget tests cover malformed direct elapsed-time
    inputs and valid finite accounting.

- [x] Document or enforce run-budget stop-reason and generation-counter validation.
  - README/run-artifact evidence: README describes `manifest.json.runtime` as
    carrying consumed generation counters and a stop reason, which can imply
    those fields are safe typed status values.
  - Status: enforced and documented. Current budget snapshots validate
    non-negative counters, finite evaluator seconds, coherent seed/candidate
    totals, and enum stop reasons before values are returned for manifests or
    candidate metadata. Run-artifact docs state this boundary.
  - Verification: focused budget tests cover malformed counters and stop
    reasons across `snapshot()`, `check_before_generation()`, and `finish()`.

- [x] Document or fix raw aborted-run exception messages in manifests.
  - README/run-artifact evidence: docs describe `manifest.json` as durable run
    provenance with abort diagnostics, while safety docs warn that persisted
    run artifacts can contain sensitive prompts, code, metadata, or provider
    errors.
  - Status: fixed and documented. Aborted runtime manifests now persist
    redacted, bounded exception messages plus `message_chars`,
    `message_truncated`, and `message_unavailable` fields instead of raw
    `str(exc)` output.
  - Verification: run-artifact docs describe the abort-message policy, and
    focused loop tests cover provider, plugin, evaluator, long-message, and
    broken-`__str__` abort paths.

- [x] Document completed-runtime manifest artifact/history limits.
  - README/run-artifact evidence: docs describe normal and aborted `runtime`
    sections, and aborted runs explicitly include artifact/quarantine pointers.
    Users may reasonably expect completed manifests to provide the same
    artifact inventory for inspection.
  - Status: implemented and documented. Completed runtime manifests now include
    history summaries and artifact pointers, and README/run-artifact docs state
    that CLI best exports occur after core-loop manifest finalization.
  - Verification: focused loop tests cover seed-only, generated-failure, and
    plugin-artifact completed manifests.

- [x] Document or fix link-aware runtime artifact pointer semantics.
  - README/run-artifact evidence: README and run-artifact docs say linked known
    run artifacts are rejected before overwrite cleanup, and runtime manifests
    include artifact/quarantine pointers.
  - Status: fixed and documented. Runtime artifact pointers now report
    link/junction/broken-link fields, target containment diagnostics, target
    hashes, and avoid target size/type summaries for link-like artifacts.
  - Verification: README/run-artifact docs describe the pointer schema, and
    focused loop tests cover regular files, symlinks, broken links, and
    junctions on capable platforms.

- [x] Document or fix abort artifact-pointer filesystem failure handling.
  - README/run-artifact evidence: README and run-artifact docs present aborted
    runtime manifests as preserving the abort phase, exception, history-written
    status, and artifact/quarantine pointers.
  - Status: fixed and documented. Runtime artifact pointer collection now
    retains redacted per-artifact `inspection_errors` instead of replacing the
    original abort with a secondary filesystem exception.
  - Verification: focused loop tests cover stat-failing history, quarantine,
    evaluator-artifact, and plugin-artifact paths with secret-like error text.

- [x] Document or reject zero-evaluation completed runs.
  - README/run-artifact evidence: README describes run history and manifests as
    the artifacts for inspected experiments, which can imply every completed
    run has at least a candidate history or an explicit no-candidate marker.
  - Status: documented and made explicit in runtime manifests.
    `max_evaluations=0` is a dry budget point with no-candidate history
    diagnostics; zero-second evaluator/runtime limits are rejected by config
    validation.
  - Verification: focused loop tests cover the dry budget manifest and
    zero-second config rejection.

- [x] Document manifest atomic-write versus crash-durability limits.
  - README/run-artifact evidence: docs describe `manifest.json` writes as
    atomic, which may be read as a full crash-consistency guarantee.
  - Status: parent-directory fsync is now attempted after atomic replacement,
    and run-artifact docs describe the remaining platform/filesystem limit when
    directory sync is unsupported.
  - Verification: focused JSON writer tests prove parent-directory fsync is
    attempted.

- [x] Document corrupt-current-manifest runtime update behavior.
  - README/run-artifact evidence: docs state that rejected runtime manifest
    updates keep diagnostics in `manifest_invalid.jsonl`.
  - Status: implemented and documented. Unreadable current manifests are
    quarantined with a diagnostic and runtime updates recover from the in-memory
    startup manifest when the replacement payload is valid.
  - Verification: focused database tests cover malformed, empty, and non-UTF-8
    current manifests plus invalid replacement payloads.

- [x] Document or fix raw archive metric validation for invalid candidates.
  - README/API evidence: archive admission is validity-gated and run artifacts
    are structured diagnostics.
  - Status: fixed. Invalid candidates now receive structured
    `invalid_evaluation` archive events before metric-vector quality matters;
    valid archive candidates still validate metrics before archive mutation.
  - Verification: focused MAP-Elites and database tests cover malformed metrics
    on invalid and valid candidates.

- [x] Document or fix raw archive insertion without admission metadata.
  - README/API evidence: history records include `metadata.archive_admission`
    events with cell, descriptor, replacement, elite-retention, and
    sampling-eligibility details.
  - Status: fixed. Public `ProgramDatabase.add()` now routes through
    `admit()`, attaching archive-admission metadata before persistence.
  - Verification: focused database tests cover `add()` plus `log()` and assert
    persisted admission metadata.

- [x] Document or fix threshold bypass through raw archive insertion.
  - README/API evidence: archive admission thresholds should apply consistently
    at public database insertion boundaries.
  - Status: fixed. Public `ProgramDatabase.add()` now uses the default
    thresholded admission policy instead of bypassing `admit()`.
  - Verification: focused database tests prove a valid negative-fitness program
    is rejected as `below_threshold` through `add()`.

- [x] Document or fix MAP-Elites descriptor normalization side effects.
  - README evidence: README describes MAP-Elites archive cells and descriptor
    values as search-state evidence, which can imply descriptors are stable for
    retained candidates and unaffected by candidates that do not enter the
    archive.
  - Status: fixed and documented. MAP-Elites complexity normalization is now
    transactional for non-admitted candidates: rejected candidates can use a
    provisional descriptor for their own event, but `_max_complexity` is
    committed only when a candidate enters a cell or retained elite state.
    README/run-artifact docs still scope retained-candidate descriptor scales
    as dynamic in-memory state.
  - Verification: focused MAP-Elites tests prove a long `not_improving_cell`
    candidate does not affect the next short candidate's complexity descriptor,
    while a retained elite-only candidate does commit complexity state.

- [x] Document or fix short-code MAP-Elites diversity collapse.
  - README evidence: README presents MAP-Elites diversity cells as meaningful
    archive/search state, which can imply the diversity coordinate
    distinguishes different candidate implementations.
  - Status: fixed and documented. Diversity now uses adaptive TF-IDF
    character n-grams up to length 4, with lower-order n-grams for short
    non-empty code and a documented default fallback for empty code.
  - Verification: focused MAP-Elites tests cover distinct one-character
    programs and empty-code fallback behavior.

- [x] Document or fix partial candidate-workspace materialization on write
  failure.
  - README/problem-format evidence: README and problem-format docs present
    multi-file candidates as complete workspace snapshots that validators and
    exports consume.
  - Status: fixed and documented. Candidate workspace materialization now
    writes to a temporary sibling workspace before target-root swap, and docs
    describe failed-write preservation for visible roots.
  - Verification: focused candidate tests cover mid-write failure preservation;
    evaluator and CLI tests cover validator temp workspaces and
    `best_workspace` export surfaces.

- [x] Document or fix non-UTF-8-encodable candidate workspace contents.
  - README/problem-format evidence: README presents candidate workspaces as
    UTF-8 text file sets.
  - Status: fixed and documented. Candidate file contents must be UTF-8
    encodable before workspace construction, mutation acceptance, evaluation,
    or export.
  - Verification: focused candidate tests cover direct and mutation-generated
    non-UTF-8 content rejection before materialization.

- [x] Document or fix linked-ancestor candidate materialization.
  - README/run-artifact evidence: README describes candidate workspaces and
    best-workspace exports as run-owned artifacts.
  - Status: fixed and documented. Candidate workspace materialization rejects
    link/junction roots, ancestors, and children instead of following aliased
    paths.
  - Verification: focused candidate tests cover symlink and Windows junction
    ancestors.

- [x] Document or fix unredacted custom DeepResearch result bodies.
  - README/plugin evidence: README describes the DeepEvolve-inspired plugin as
    pluggable arXiv/web-search context with redacted provider errors and
    retrieval metadata.
  - Status: fixed and documented. Successful custom-provider retrieval bodies
    are redacted and bounded before prompt rendering, and metadata records raw
    length/hash plus redaction/truncation flags. Prompt headers label the
    provider/source kind.
  - Verification: focused DeepResearch tests cover string, arbitrary object,
    oversized secret-like text, and dict synthesis results.

- [x] Document or enforce direct prompt mutation-mode validation.
  - README/config evidence: mutation mode selects either SEARCH/REPLACE diff
    output or full-code/full-block replacement output.
  - Status: enforced and documented. Direct prompt construction validates
    mutation modes against the same `diff`/`full` enum before rendering labels
    or instructions.
  - Verification: focused prompt/config tests cover invalid direct values and
    valid `diff`/`full` prompt rendering.

- [x] Document or enforce direct `PromptSampler.variants` validation.
  - README/config evidence: docs describe prompt variants as validated
    templates.
  - Status: enforced and documented. Direct sampler variants use the same
    list-of-renderable-template validation as config variants before random
    selection.
  - Verification: focused prompt/config tests cover invalid containers,
    non-string items, invalid templates, mutated sampler state, and valid
    config variants.

- [x] Document or enforce direct `capture_proposal_metadata` validation.
  - README/config evidence: proposal metadata is an optional feature that
    changes the prompt/output envelope.
  - Status: enforced and documented. Direct prompt construction rejects
    non-boolean proposal-metadata flags before rendering metadata instructions.
  - Verification: focused prompt/config tests cover boolean true/false and
    invalid string, numeric, container, and object values.

- [x] Document or enforce direct prompt `extra_context` validation.
  - README/context evidence: docs describe context and plugin guidance as
    bounded, provenance-bearing prompt inputs.
  - Status: enforced and documented. Direct `extra_context` must be text and is
    redacted and capped before prompt rendering.
  - Verification: focused prompt tests cover invalid direct values, oversized
    context, secret-like text, and valid text.

- [x] Document or enforce direct parent/inspiration prompt input validation.
  - README/prompt evidence: README describes prompt construction as rendering
    the current program and inspiration programs.
  - Status: enforced and documented. Direct prompt parent/inspiration inputs
    must be `Program` objects, with inspirations supplied as a list.
  - Verification: focused prompt tests cover invalid parents, malformed
    inspiration containers/items, empty inspiration lists, and valid
    inspiration records.

- [x] Document or enforce text-only direct mutation helper inputs.
  - README/problem-format evidence: mutation docs describe LLM responses as
    text, and helper APIs are reusable in tests, notebooks, and runtime paths.
  - Status: enforced and documented. Direct candidate/workspace mutation
    helpers reject non-text payloads with `non_text_mutation_payload` instead
    of raw parser errors.
  - Verification: focused candidate tests cover `None`, numeric, and list
    payloads in both mutation modes; README and problem-format docs name the
    error code.

- [x] Document or validate non-text failure-history mutation payloads.
  - README/run-artifact evidence: failed-trial memory is persisted, bounded run
    evidence and prompt feedback.
  - Status: validated and documented. Failure-history rows store bounded
    representations of non-text mutation payloads with payload type,
    text/non-text flag, and hash evidence.
  - Verification: database tests cover `None`, numeric, list, and dict payloads;
    loop tests prove persisted non-text failures are rendered into recent
    failure prompt memory.

- [x] Document or fix command-keyword path collisions in file sections.
  - README/problem-format evidence: path docs accept safe space-containing
    paths while topology commands use command-like file-section headers.
  - Status: fixed and documented. Ordinary command-leading filenames can be
    edited with `<<<FILE PATH ...`; topology commands remain available through
    `DELETE`, `MOVE`/`RENAME`, and `PRIMARY` headers.
  - Verification: focused candidate tests cover command-leading ordinary
    filenames and empty `PATH` rejection; README and problem-format docs show
    the escape syntax.

- [x] Document or reject same-line file/block section envelopes.
  - README/problem-format evidence: mutation examples use header lines,
    payload bodies, and closing markers.
  - Status: rejected and documented. Same-line envelopes such as
    `<<<FILE main.py>>>FILE` and `<<<BLOCK core>>>BLOCK` are malformed because
    section headers must end with a newline.
  - Verification: focused candidate tests cover same-line file/block envelopes
    and mixed valid plus malformed sections; README/problem-format docs state
    the newline requirement.

- [x] Document or fix full-replacement trailing-newline normalization.
  - README evidence: full mutation mode is described as full-block/full-code
    replacement content.
  - Status: fixed and documented. Accepted full-mode bodies preserve final
    newlines and blank lines; an actually empty file-section body still creates
    an empty file.
  - Verification: focused candidate tests cover single-file, file-section,
    single-block, and multi-block full replacements with final newlines and
    blank lines.

- [x] Document or fix SEARCH/REPLACE line-ending sensitivity.
  - README/problem-format evidence: SEARCH/REPLACE is the default mutation
    contract.
  - Status: fixed and documented. Matching is LF-normalized, replacements are
    adapted to the matched candidate span's dominant line ending, and unrelated
    surrounding text is not globally normalized.
  - Verification: focused tests cover CRLF candidates, LF patches, mixed line
    endings, evolve-block matching, and workspace file sections.

- [x] Document or fix single-block full-block envelope behavior.
  - README/problem-format evidence: full-block replacement is a
    skeleton-preserving mutation mode.
  - Status: fixed and documented. Named `<<<BLOCK ...>>>BLOCK` envelopes work
    for both single-block and multi-block candidates; one-block raw-body
    shorthand remains available.
  - Verification: focused candidate tests cover one-block named sections,
    unknown block names, multi-block sections, and workspace file-section use.

- [x] Document or fix full-mode file sections that target evolve-blocked
  files.
  - README/problem-format evidence: full mode supports both full-code and
    full-block replacement.
  - Status: documented and reflected in prompts. Full-mode file sections are
    complete replacements for files without evolve blocks; for files with
    evolve blocks, bodies follow full-block replacement rules.
  - Verification: focused candidate tests cover one-block and multi-block
    workspace file sections; prompt tests assert the blocked-file instruction.

- [x] Document ignored non-section payload around file sections or reject it.
  - README/problem-format evidence: file sections are the multi-file mutation
    contract.
  - Status: rejected and documented. File-section responses must be fully
    consumed except for whitespace and proposal metadata.
  - Verification: focused candidate tests cover prose, stray diff blocks, stray
    block payloads, and metadata around valid file sections.

- [x] Document ignored non-section payload around block sections or reject it.
  - README/problem-format evidence: block sections are the full-mode
    multi-region mutation contract.
  - Status: rejected and documented. Block-section responses must be fully
    consumed except for whitespace and proposal metadata, otherwise they fail
    as `malformed_block_sections:unconsumed_text`.
  - Verification: focused candidate tests cover prose, stray diff payloads, and
    accepted metadata around valid block sections.

- [x] Document or fix linked `initial_programs` root ingestion.
  - README/problem-format evidence: setup documentation describes
    problem-local seed programs under `initial_programs/`.
  - Status: fixed and documented. The seed root itself, seed files, and
    workspace-seed entries must be real problem-local files/directories;
    symlinks and Windows junctions are rejected instead of followed.
  - Verification: focused loader tests cover root-link rejection and
    platform-available directory symlink roots.

- [x] Document or enforce secret-safe evolve-block names.
  - README/problem-format evidence: block names are skeleton labels and
    mutation targets.
  - Status: enforced and documented. Block names are public persisted labels
    with an ASCII manifest-safe grammar, Unicode format-control rejection, and
    secret-like string rejection.
  - Verification: focused candidate/loader tests cover marker validation,
    block-section target validation, seed loading, and the current non-ASCII
    rejection policy.

- [x] Document or enforce finite-score requirements for CausalPlugin hooks.
  - README/plugin evidence: causal guidance is prompt-visible outcome evidence.
  - Status: enforced and documented. CausalPlugin hook scores must be finite
    numbers, and malformed restored causal history is quarantined before prompt
    guidance is rendered.
  - Verification: focused causal-plugin tests cover malformed score rejection
    and restored-history quarantine; README and plugin docs state the contract.

- [x] Document or fix direct evaluator contract-preflight bypass.
  - README/evaluator evidence: README and run-artifact docs say evaluator
    contracts are preflighted before run artifacts are mutated, which can imply
    unsupported evaluator signatures are consistently rejected.
  - Status: fixed and documented. Direct `CascadeEvaluator.evaluate()` calls
    now run the same validator-contract preflight once before validator
    subprocess execution, while preserving diff/syntax failure behavior.
  - Verification: focused evaluator tests cover accepted direct signatures,
    unsupported default validators, and unsupported configured-stage
    validators; README, problem-format, and run-artifact docs describe the
    direct evaluator boundary.

- [x] Document markdown-fence stripping can alter replacement code literals.
  - README evidence: README says models can wrap diffs in markdown fences and
    that the diff engine strips them automatically, which can read as safe
    response-envelope normalization.
  - Status: fixed and documented. Mutation parsing now strips only a single
    outer markdown fence wrapper and preserves triple-backtick text inside
    replacement code; README/problem-format/development/AGENTS wording now
    reflects that boundary.
  - Verification: focused diff and candidate tests cover wrapped payloads and
    fence literals in SEARCH/REPLACE, full-file, file-section, and block-section
    replacements.

- [x] Document mutation-envelope delimiter collisions or fix them first.
  - README/problem-format evidence: full-file and file-section mutation docs
    teach `<<<FILE ... >>>FILE` and `<<<BLOCK ... >>>BLOCK` as payload
    envelopes for generated code.
  - Status: fixed and documented. File/block envelope markers are now line-start
    syntax, and marker-looking substrings inside ordinary replacement code
    lines are preserved as candidate content.
  - Verification: focused diff/candidate tests cover literal file and block
    marker strings in diff, full-file, file-section, and block-section mutation
    payloads; README and problem-format docs describe the boundary.

- [x] Document validator helper shadowing behavior or fix it first.
  - README/problem-format evidence: docs said both the materialized candidate
    root and validator directory were added to `sys.path`, but did not state
    which one won when both contained the same module name.
  - Status: fixed and documented. Validator helper modules now have import
    precedence over candidate modules on name collisions, while non-colliding
    candidate imports and relative file access still work.
  - Verification: focused evaluator tests cover same-name helper collisions,
    candidate package imports, problem-local helper imports, and workspace
    relative file access; README and problem-format docs state the policy.

- [x] Document validator preflight import side effects or isolate preflight
  first.
  - README evidence: README explains validator subprocess execution with
    minimal allowlisted environment and timeout cleanup; startup preflight now
    uses a matching subprocess boundary for import/signature checks.
  - Status: isolated and documented. Preflight runs in a bounded subprocess with
    a temporary working directory and validator env allowlist, does not import
    validator modules in the parent process, and still does not call
    `evaluate()`.
  - Verification: focused evaluator tests cover parent env isolation, temp-cwd
    import side effects, env allowlist behavior, and import timeout; README,
    problem-format, and run-artifact docs describe the boundary.

- [x] Document or fix evaluator result transport ambiguity.
  - README/run-artifact evidence: evaluator stdout/stderr are diagnostics and
    evaluator metrics are structured results, so diagnostic output must not be
    able to replace the returned metric object.
  - Status: fixed and documented. The validator runner writes returned metrics
    to a runner-owned result file, and stdout/stderr remain diagnostic-only.
    `docs/problem-format.md` now states that stdout is not the metrics
    transport.
  - Verification: focused evaluator tests cover printed fake JSON, descendant
    process fake JSON after validator return, and non-JSON-serializable
    validator returns.

- [x] Document or improve malformed metric diagnostics.
  - README/run-artifact evidence: README says raw metrics and diagnostics are
    stored with each candidate, and problem docs say malformed evaluator
    returns are rejected.
  - Status: fixed and documented. Malformed evaluator contracts now persist a
    bounded `evaluation.metadata.malformed_metrics` record with reason,
    exception type, and redacted message; README, problem-format, and
    run-artifact docs describe the behavior.
  - Verification: focused evaluator tests cover missing metrics, undeclared
    keys, type failures, non-finite/JSON-invalid values, bad `is_valid`, and
    missing secondary metrics.

- [x] Document or fix non-serializable evaluator-result classification.
  - README/problem-format evidence: validator docs describe
    `evaluate(...) -> dict` as returning structured metrics, and run-artifact
    docs distinguish evaluator diagnostics from subprocess failures.
  - Status: fixed and documented. Non-JSON-serializable validator returns are
    classified as `malformed_metrics` with reason `not_json_serializable`
    rather than `subprocess_error`.
  - Verification: focused evaluator tests cover object, set, bytes, NumPy
    scalar, and NumPy array payloads.

- [x] Document or fix evaluator-result key-collision transport behavior.
  - README/problem-format evidence: validator metric names and values should
    arrive unchanged at validation.
  - Status: fixed and documented. Top-level evaluator result keys must be
    strings before transport; non-string keys are rejected before JSON
    serialization can coerce them.
  - Verification: focused evaluator tests cover direct integer keys,
    boolean/null-like keys, and configured-stage samples/retries.

- [x] Implement and document feedback-prompt input redaction for diagnostics
  and metrics.
  - README/config evidence: earlier docs narrowed feedback prompt redaction to
    workspace file contents because evaluator diagnostics and metric payloads
    were not fully redacted before prompts.
  - Status: implemented and documented. Feedback prompts now redact and bound
    evaluator diagnostics plus metric keys/values before prompt rendering, and
    README/configuration docs state that provider `raw_response` / parsed
    feedback text remains a separate raw-output gap.
  - Verification: focused feedback tests cover evaluator stdout/stderr/errors,
    stage diagnostics, secret-like metric keys/values, nested metrics, long
    metric strings, and normal numeric metrics.

- [x] Document or fix raw `Program.metrics` rendering in mutation prompts.
  - README/run-artifact evidence: parent and inspiration metrics are rendered
    into mutation prompts and prompt history, so raw direct/plugin/restored
    metric payloads needed either explicit documentation or prompt-safe
    rendering.
  - Status: fixed and documented. Mutation prompts now render parent and
    inspiration metric keys/values through bounded redaction, declared metric
    ordering, and explicit non-finite markers. README and run-artifact docs
    distinguish this metric-specific hardening from the remaining lack of a
    general rendered-prompt redaction policy.
  - Verification: focused prompt tests cover secret-like parent and
    inspiration metric keys/values, nested metric payloads, long strings,
    declared metric ordering, and non-finite value markers.

- [x] Document or reject non-finite fitness in mutation prompt headers.
  - README prompt evidence: prompt sampling reuses parent and inspiration
    scores to guide future mutations, so score headers need to avoid apparent
    finite evidence for malformed direct/restored records.
  - Status: fixed and documented. Prompt-visible parent and inspiration
    fitness values now render finite scores normally and typed invalid markers
    for `nan`, `inf`, `-inf`, booleans, strings, and `None` without crashing,
    including custom templates that format `{parent_score:.4f}`.
  - Verification: focused prompt tests cover parent and inspiration score
    markers for non-finite values, bool, string, `None`, valid finite scores,
    and custom numeric format specs.

- [x] Document or add explicit problem context in feedback-grader prompts.
  - README evidence: feedback graders need the same explicit problem
    constraints and local context that shape mutation prompts.
  - Status: implemented and documented. Feedback graders now receive bounded
    explicit problem context with source provenance, redaction, truncation, and
    budget omission notices alongside workspace and evaluator diagnostics.
  - Verification: focused feedback tests cover context source names, hashes,
    page spans, context text, redaction, truncation, and omitted context
    notices.

- [x] Document or fix false failed-stage labels in mutation prompts.
  - README/run-artifact evidence: stage summaries reused in prompts should not
    imply failed evaluator outcomes when restored records only prove unknown
    state.
  - Status: fixed and documented. Prompt-visible evaluator stage summaries now
    use `passed`, `failed`, or `unknown`, with unknown covering missing,
    `None`, or malformed status values.
  - Verification: focused prompt tests cover explicit failed stages, missing
    status, `None`, malformed status values, and retry/sample attempt summaries.

- [x] Document or render evaluator feedback for inspiration programs.
  - README/prompt evidence: parent and inspiration programs are prior search
    evidence shown to the mutation LLM, so inspiration evaluator feedback
    should not be dropped when present.
  - Status: implemented and documented. Selected inspiration programs now
    render bounded/redacted evaluator feedback summaries using the same policy
    as parent feedback.
  - Verification: focused prompt tests cover inspiration stage diagnostics,
    stdout/stderr, LLM grader feedback, redaction, and truncation.

- [x] Document or fix legacy tuple recent-failure prompt rendering.
  - README/run-artifact evidence: docs describe failed-trial memory and
    prompt/history redaction limits, so compatibility failure-record formats
    should not imply broader prompt safety than exists.
  - Status: fixed. Legacy `(code, score)` recent-failure tuples now route the
    code snippet through bounded prompt redaction, newline escaping, and
    truncation before rendering.
  - Verification: focused prompt tests cover secret-like tuple text, escaped
    newlines, truncation notices, and suppression of long repeated snippets.

- [x] Document first rendered mutation-prompt character cap.
  - README/run-artifact evidence: mutation prompts can now be bounded before
    provider calls, and the cap should be visible to users inspecting run
    history and manifests.
  - Status: documented. README, run-artifact docs, configuration docs, and CLI
    option summaries now describe `prompt_max_chars` / `--prompt-max-chars` as
    a character-level cap with prompt diagnostics, while explicitly keeping
    token-aware context accounting and section-priority packing as open gaps.
  - Verification: focused config, prompt, loop, and CLI tests cover the actual
    behavior, and docs now match the command/config surface.

- [x] Document prompt-rendering delimiter limits or fix them first.
  - README/problem-format evidence: README and problem-format docs describe
    rendered parent programs and inspiration programs as the basis for LLM
    mutation prompts.
  - Status: fixed and documented. Candidate parent and inspiration workspaces
    now render as typed, length-counted, JSON-escaped file records rather than
    markdown code fences, so embedded triple backticks and fake file headers are
    ordinary file content. Single-file non-Python candidates keep their file
    path metadata instead of being shown as Python.
  - Verification: focused prompt tests cover candidate fence-like content,
    fake file headers, multi-file workspaces, inspiration workspaces, and
    single-file non-Python workspaces.

- [x] Document or fix explicit context-body delimiter limits.
  - README/problem-format evidence: explicit context is prompt-visible
    experiment input with citations/provenance.
  - Status: fixed and documented. Explicit context bodies now render as
    character-counted JSON strings, so embedded backticks, fake task headers,
    and fake context-source headers stay inside the context payload.
  - Verification: focused prompt tests cover delimiter-like explicit context
    bodies and preserve existing source citation metadata.

- [x] Document or fix prompt context ordering for direct context maps.
  - README/context evidence: README and problem-format docs describe explicit
    context as prompt-visible experiment input with citations/provenance, which
    implies stable prompt assembly for the same context set.
  - Status: fixed. `_render_context()` now path-sorts context entries before
    rendering.
  - Verification: focused prompt tests cover equivalent direct context maps
    rendering in deterministic path order.

- [x] Document or enforce prompt citation metadata validation.
  - README/context evidence: README describes selected context paths, hashes,
    excerpts, PDF page data, and extraction status as prompt provenance for
    local context ingestion.
  - Status: enforced before prompt rendering. Context citation headers now use
    bounded/redacted display values, safe fallback excerpt/character fields,
    positive ordered page spans only, and escaped single-line status text.
  - Verification: focused prompt tests cover normal citation records,
    secret-like labels and metadata, newline status injection, negative excerpt
    offsets, and invalid page spans.

- [x] Document or validate plugin-rendered prompt context itself.
  - README/plugin-doc evidence: README and plugin docs describe
    `build_extra_context()` as injecting plugin guidance into prompts, which
    can imply that the injected text has the same redaction, size, and
    provenance boundaries as other prompt sections.
  - Status: fixed and documented. `build_extra_context()` must return `str` or
    `None`; emitted plugin guidance is redacted, character-capped, rendered as
    a JSON-string prompt section, and persisted with size/hash/redaction
    diagnostics.
  - Verification: focused loop tests cover normal text guidance, unsupported
    object returns, secret-like content, oversized content, persisted metadata,
    and prompt redaction.

- [x] Document or enforce prompt-safe runtime metric names.
  - README/problem-format evidence: README says metric names from
    `metrics.yaml` are normalized and manifest-safe, and prompt examples show
    metric vectors as optimization evidence.
  - Status: enforced and documented. Runtime `Program.metrics` keys must match
    the manifest-safe metric-name grammar used by `metrics.yaml`, including
    optional dotted namespaces. Unsafe direct or mutated metric keys are
    rejected/quarantined before prompt, history, and archive use. Unsafe
    plugin-added metric side effects are reverted and logged under
    `invalid_plugin_metrics`.
  - Verification: focused program/database/loop tests cover direct unsafe
    keys, safe dotted names, history quarantine, archive rejection, and
    plugin-added unsafe metrics.

- [x] Document and enforce direct archive candidate-id uniqueness.
  - README/run-artifact evidence: README presents program ids, lineage,
    history, MAP-Elites cells, and island archives as inspectable experiment
    evidence.
  - Status: direct archive admission now rejects duplicate ids before live
    archive mutation, including different objects with ids already logged in
    the same run. README documents that migration still copies the same id
    across islands and is deduplicated during inspiration sampling until a
    persisted migration clone/version policy exists.
  - Verification: focused database tests cover raw `add()`, `admit()` across
    islands, logged-id conflicts, and same-object log-then-admit behavior.

- [x] Document and fix invalid-encoding `history.jsonl` inspection failures.
  - README/run-artifact evidence: README describes `libreevolve show` as the
    compact history inspection view for run artifacts.
  - Status: README now documents that `show` fails fast on invalid UTF-8 bytes
    in `history.jsonl`. The CLI decodes history rows line-by-line from bytes
    and reports invalid encodings through line-numbered malformed-history
    diagnostics.
  - Verification: focused CLI tests cover invalid UTF-8 at the first history
    line and after a valid row without leaking a raw `UnicodeDecodeError`.

- [x] Document and enforce run-inspection program-id validation.
  - README/run-artifact evidence: README and run-artifact docs present
    `history.jsonl` ids as inspectable candidate identity evidence.
  - Status: README and run-artifact docs now state that `show` requires every
    streamed history id to be manifest-safe and unique. The CLI applies the
    writer-side id grammar while streaming and reports duplicate ids with the
    first-seen line number.
  - Verification: focused CLI tests cover duplicate legacy/current ids and
    unsafe selected or unselected history ids.

- [x] Fix README claims that `show` validates displayed metrics.
  - README evidence: README and run-artifact docs say `show` fails on malformed
    history rows and validates metrics using the finite metric-value policy.
  - Status: README and run-artifact docs now state that every streamed
    `metrics` object must use manifest-safe metric names and JSON-native finite
    numeric values except boolean `is_valid`, and that printed metric summaries
    use strict JSON. Runtime `show` enforces that behavior before selection or
    display.
  - Verification: focused CLI tests cover invalid metric values, bad metric
    keys, invalid unselected rows, and valid strict metric JSON output.

- [x] Document and fix `show` validation for unsafe history workspace paths.
  - README/run-artifact evidence: README says `show` streams `history.jsonl`
    and validates display fields such as workspace files before printing them.
  - Status: README and run-artifact docs now state that `show` validates and
    normalizes workspace file paths with the runtime candidate path grammar
    before display. The CLI rejects unsafe path labels with line-numbered
    malformed-history diagnostics.
  - Verification: focused CLI tests cover traversal, absolute, hidden,
    bidi-control, overlong, duplicate-normalized, and valid Unicode workspace
    paths.

- [x] Document and fix `show` handling of malformed or contradictory
  archive-admission rows.
  - README/run-artifact evidence: README describes archive admission metadata as
    structured run-history evidence used by `show` to identify retained
    candidates.
  - Status: README and run-artifact docs now state that current-format
    archive-admission payloads must be objects and that admitted rows with
    explicit archive-state flags need at least one true retention/search-state
    flag before being presented as retained.
  - Verification: focused CLI tests cover malformed archive payloads,
    contradictory admitted rows, coherent cell/elite events, and non-admitted
    rows.

- [x] Document and fix `show` handling of malformed evaluation payloads.
  - README/run-artifact evidence: README describes current histories as
    structured evaluator-result records and `show` as a history inspection path
    with malformed-row diagnostics.
  - Status: README and run-artifact docs now state that present current-history
    `evaluation` payloads must be objects and `evaluation.is_valid`, when
    present, must be boolean.
  - Verification: focused CLI tests cover non-object evaluation payloads,
    non-boolean `is_valid`, missing validity, and valid retained rows.

- [x] Document and fix `show` ignoring malformed unselected archive rows.
  - README/run-artifact evidence: README positions `libreevolve show` as the
    compact inspection path for run histories and archive diagnostics.
  - Status: README and run-artifact docs now state that archive diagnostic
    fields are validated while streaming current histories, so malformed
    unselected retained archive rows cannot be hidden by a valid best row.
  - Verification: focused CLI tests cover a valid selected row plus a malformed
    lower-scoring retained row.

- [x] Document and validate malformed archive cell coordinate shapes in `show`.
  - README/run-artifact evidence: README and run-artifact docs describe
    MAP-Elites cell coordinates as archive diagnostics shown by
    `libreevolve show`.
  - Status: current-history cells are validated as three non-negative integer
    coordinates before display. Manifest-bound upper-range validation remains
    documented as open.
  - Verification: focused CLI tests cover malformed and valid current-history
    cell coordinates.

- [x] Document and fix unredacted archive descriptor labels in `show` output.
  - README/run-artifact evidence: README describes `libreevolve show` as the
    compact inspection path for run histories and archive diagnostics.
  - Status: README and run-artifact docs now state that archive descriptor
    labels are validated with the manifest-safe metric-name grammar before
    display. Unsafe labels, control characters, reserved `is_valid`, and
    non-identifier labels fail with line-numbered diagnostics instead of being
    echoed by `show`. Large descriptor maps are covered by the follow-on
    completed descriptor-budget item.
  - Verification: focused CLI tests cover safe descriptors, secret-like labels,
    corrupt labels, reserved labels, and unselected current-history rows.

- [x] Document and bound archive descriptor volume in `show` output.
  - README/run-artifact evidence: README describes `show` as compact
    run-history inspection and presents archive diagnostics as structured
    metadata.
  - Status: README and run-artifact docs now state that large descriptor maps
    or long descriptor labels are summarized with descriptor count, bounded
    preview, omitted count, and stable hash rather than printed in full.
  - Verification: focused CLI tests cover normal small descriptor JSON,
    500-entry descriptor maps, long descriptor labels, and omitted-count/hash
    diagnostics.

- [x] Document and bound full-source output from `libreevolve show`.
  - README/run-artifact evidence: README describes `show` as a compact way to
    inspect previous runs and workspace histories.
  - Status: README and run-artifact docs now state that large selected legacy
    source or workspace file bodies are truncated with source length, displayed
    length, omitted count, source hash, and `history.jsonl` full-source pointer.
    Fixed-cap configurability remains a code follow-up.
  - Verification: focused CLI tests cover oversized legacy code, oversized
    primary workspace files, oversized secondary workspace files, and normal
    small workspace output.

- [x] Document and fix evaluator preflight path redaction.
  - README evidence: README describes validator subprocess isolation and
    redacted evaluator diagnostics, and preflight failures are user-facing
    CLI/setup output.
  - Status: README and run-artifact docs now state that preflight diagnostics
    use problem-relative or outside-problem path labels with stable path hashes
    instead of raw absolute roots. Run-directory containment diagnostics remain
    separate setup hardening work.
  - Verification: focused CLI/evaluator tests cover secret-like problem roots,
    direct configured-stage escapes, missing problem-local validators, and
    hash-bearing diagnostics.

- [x] Document and fix run-directory containment path redaction.
  - README evidence: README says run-directory paths are confined under
    `log_dir` and manifests retain redacted/hash-only `log_dir` metadata, which
    can imply setup diagnostics share that safety policy.
  - Status: README and run-artifact docs now state that containment,
    existing-artifact, and linked-artifact startup diagnostics use scoped path
    labels plus stable path hashes rather than raw absolute roots.
  - Verification: focused database and CLI tests cover the redacted/path-hashed
    diagnostic surfaces and prove a secret-like `log_dir` component is not
    printed in these startup failures.

- [x] Document and fix seed/generated generation numbering.
  - README evidence: README examples and `show` output present generation
    numbers as run-inspection facts, so generation `0` should not identify both
    seeds and the first generated candidate.
  - Status: README and run-artifact docs now state that seed baselines use
    `generation: 0`, generated candidates start at generation `1`, and
    `metadata.loop_generation_index` keeps the zero-based loop index.
  - Verification: focused loop tests cover seed-only and first-generated-child
    histories, and `show` continues to validate generation values before
    display.

- [x] Document ThetaEvolve export cadence with completed-generation counts.
  - README/plugin-doc evidence: `docs/plugins.md` says `ttt_rl` writes pending
    examples every `train_every` generations, and README describes generation
    hooks as running after each generation.
  - Status: README and plugin docs now state that generation hook arguments are
    completed-generation counts starting at `1`, and `train_every=1` exports
    after the first completed mutation generation.
  - Verification: focused loop/plugin tests cover first-generation export,
    `train_every=2` export after the second completed generation, and
    non-multiple short-run pending counts.

- [x] Document and fix stale DeepResearch context after empty/error refreshes.
  - README/plugin-doc evidence: README and plugin docs describe
    DeepEvolve-inspired retrieval context and retrieval metadata, which can
    imply the latest recorded retrieval event describes the prompt text that was
    injected.
  - Status: README, plugin docs, and run-artifact docs now state that empty or
    error refreshes clear prompt-visible retrieval context. Active successful
    context is linked through `active_context` metadata with generation and
    synthesis hash.
  - Verification: focused DeepResearch tests cover ok-to-empty, ok-to-error,
    ok-to-new-result, and active-context metadata.

- [x] Document and bound DeepResearch in-memory retrieval history.
  - README/plugin-doc evidence: DeepResearch retrieval is presented as a
    reusable prompt-context/provenance feature for ongoing evolutionary runs,
    which implies bounded memory behavior and a documented retention policy.
  - Status: README, plugin docs, run-artifact docs, and the paper index now
    describe the `max_events` retention cap, default value, and
    `retrieval_retention` counters. Full artifact offload/cache/replay remains
    open.
  - Verification: focused DeepResearch tests cover invalid caps and long-run
    bounded retention with retained/emitted/total/dropped counters.

- [x] Document and reject non-finite best-fitness values in retrieval metadata.
  - README/plugin-doc evidence: README describes retrieval events as persisted
    candidate/run metadata, which implies JSON-safe finite scalar fields.
  - Status: README, plugin docs, run-artifact docs, and the paper index now
    state that non-finite or nonnumeric best fitness skips retrieval with
    `skip_reason: non_finite_best_fitness` instead of querying a provider or
    persisting non-finite `best_fitness`.
  - Verification: focused DeepResearch tests cover `nan`, `inf`, `-inf`,
    string, bool, `None`, and valid finite fitness metadata.

- [x] Document and fix raw DeepResearch query URL persistence.
  - README/plugin-doc evidence: README and plugin docs describe retrieval
    provenance as useful run/candidate metadata, which can imply provider
    request details are safe to persist.
  - Status: README, plugin docs, run-artifact docs, and paper index now state
    that provider request URLs are persisted as `request_url` summaries with
    public URL components plus hashes, not raw query strings. Transport/TLS
    integrity remains separate open work.
  - Verification: focused DeepResearch and loop tests prove secret-bearing
    custom `query_url` values do not appear in history or manifest output.

- [x] Document and validate direct arXiv retrieval helper parameters.
  - README/plugin-doc evidence: README and plugin docs describe the
    DeepEvolve-inspired arXiv retrieval helper as structured live retrieval,
    which implies provider query parameters should be validated at direct helper
    boundaries as well as through plugin cadence config.
  - Status: README, plugin docs, run-artifact docs, and the paper index now
    state that direct arXiv helper calls validate non-empty safe query text and
    bounded integer `max_results` values. The docs also state that the default
    arXiv provider uses HTTPS and records transport/payload metadata.
  - Verification: focused DeepResearch tests cover invalid direct helper calls,
    HTTPS URL construction, default plugin metadata, custom-provider
    compatibility, and run-manifest transport summaries.

- [x] Document and implement live-retrieval response-size limits.
  - README/plugin-doc evidence: README describes live arXiv/web-search context
    as optional prompt input and persisted retrieval metadata, which implies
    external provider responses should be bounded before they shape
    long-running experiments.
  - Status: README, plugin docs, run-artifact docs, and the paper index now
    document the 1,000,000-byte live arXiv response cap, exact-limit behavior,
    structured `oversized_response` failures, payload diagnostics, and the fact
    that oversized responses do not enter prompt context.
  - Verification: focused DeepResearch and loop tests cover small, exact-limit,
    and oversized arXiv responses plus compact run-manifest payload-budget
    summaries.

- [x] Document and implement untrusted live-retrieval prompt boundaries.
  - README/plugin-doc evidence: README and `docs/plugins.md` describe
    DeepEvolve-inspired retrieval context as prompt input, which implies
    retrieved text should be safely contextualized rather than mixed with task
    instructions.
  - Status: README, plugin docs, run-artifact docs, and the paper index now
    document the explicit untrusted-evidence wrapper, begin/end delimiters, and
    persisted `trust_policy` / `prompt_boundary` / `authoritative: false`
    fields for successful retrieval context.
  - Verification: focused DeepResearch and loop tests cover instruction-like
    custom provider text, ordinary context rendering, active-context metadata,
    and compact manifest trust-policy summaries.

- [x] Document and fix raw DeepResearch source metadata persistence.
  - README/plugin-doc evidence: README and plugin docs describe arXiv source
    IDs/URLs, timestamps/authors, and summary hashes as retrieval provenance,
    which implies retrieved source metadata should be bounded and prompt-safe.
  - Status: README, plugin docs, run-artifact docs, and the paper index now
    describe bounded/redacted source IDs/URLs/titles/authors/timestamps/excerpts,
    source metadata retention/redaction counters, and source summary hashes.
    Full source-content trust, ranking, and replayable snapshots remain open.
  - Verification: focused DeepResearch and loop tests cover custom
    secret-bearing source fields, oversized source fields, dropped sources,
    default arXiv source metadata, and manifest source-metadata summaries.

- [x] Document and implement live-retrieval cache/replay modes.
  - README/plugin-doc evidence: README says candidate history and completed
    manifests record retrieval metadata, which can imply retrieval context is
    reproducible enough for replay.
  - Status: README, plugin docs, run-artifact docs, and the paper index now
    document DeepResearch `cached`, `live`, and `offline` modes, run-local JSON
    cache snapshots under `plugin_artifacts/deep_research/` for CLI-loaded
    plugins, cache key/hit/source/staleness/snapshot-hash metadata, and the
    remaining lack of full provider-payload persistence, ranking,
    source-content trust, and full run resume.
  - Verification: focused DeepResearch and loop tests cover cached duplicate
    queries, disk snapshot creation, offline replay, cache misses, and manifest
    cache metadata.

- [x] Document plugin hook exception behavior with structured failure
  provenance.
  - README evidence: README presents plugins as optional paper-inspired
    extensions for guidance, retrieval, score adjustment, and training-data
    export, so faulty optional hooks need explicit runtime semantics.
  - Status: README, `docs/plugins.md`, and `docs/run-artifacts.md` now state
    that plugin hook exceptions are fatal run aborts. Aborted manifests record
    `runtime.abort.plugin_failure` and `runtime.plugin_failures[]` with the
    plugin class/module/index, hook name, fatal policy, generation and
    parent/candidate ids where available, exception type/message,
    redaction/truncation diagnostics, and `continued: false`.
  - Verification: focused loop tests cover fatal failures and manifest
    provenance for `on_generation_start`, `build_extra_context`,
    `prompt_context_metadata`, `on_evaluated`, `run_artifacts_metadata`, and
    `on_generation_end`.

- [x] Document and enforce authoritative plugin artifact metadata.
  - README/run-artifact evidence: completed and aborted manifests expose plugin
    artifact summaries as experiment provenance, so artifact attribution must
    identify the actual runtime plugin rather than trusting plugin-supplied
    names.
  - Status: README, plugin docs, and run-artifact docs now describe wrapped
    `runtime.plugin_artifacts[]` records with runtime-derived `plugin`,
    `module`, and `index`, nested validated plugin `metadata`, accepted empty
    returns (`None`/`{}`), completed-run aborts for malformed non-mapping
    returns, and `runtime.plugin_artifact_failures[]` diagnostics during
    aborted-run finalization.
  - Verification: focused loop tests cover spoofed metadata, malformed
    metadata, empty returns, valid summaries, TTTRL nested manifest fields, and
    aborted-run partial artifact summaries/failures.

- [x] Document aborted-run plugin artifact metadata behavior.
  - README/run-artifact evidence: docs say aborted runs include artifact
    pointers, and completed runs can include plugin artifact summaries; this
    can imply partial plugin artifacts written before an abort are summarized.
  - Status: README, plugin docs, and run-artifact docs now state that aborted
    manifests attempt validated plugin artifact summaries, preserve wrapped
    summaries when available, and record `runtime.plugin_artifact_failures[]`
    when summary collection fails without hiding the original abort.
  - Verification: focused loop tests cover valid partial artifact summaries
    after a plugin abort and malformed artifact-summary metadata during abort
    finalization.

- [x] Document and enforce top-level plugin artifact metadata shape.
  - README/plugin/run-artifact evidence: `run_artifacts_metadata()` is the hook
    that adds plugin artifact metadata to `runtime.plugin_artifacts`, so
    malformed hook returns need explicit behavior.
  - Status: docs now say `run_artifacts_metadata()` may return `None` or `{}`
    to emit no entry and must return a mapping for emitted metadata.
    Non-mapping non-empty returns abort completed runs or become
    `plugin_artifact_failures[]` diagnostics during aborted-run finalization.
  - Verification: focused loop tests cover list, string, scalar, `None`, empty
    dict, and valid nested mapping returns.

- [x] Document and implement stable identity for repeated plugin instances.
  - README/plugin-doc evidence: README and `docs/plugins.md` describe
    per-plugin score provenance and plugin artifact/provenance hooks, so
    repeated plugin instances must be distinguishable in run records.
  - Status: README, plugin docs, and run-artifact docs now describe the
    run-local `instance_id` format and where it appears. Runtime records now
    carry `plugin`, `module`, `class`, `index`, and `instance_id` in startup
    provenance, prompt-context records, score-composition entries, artifact
    summaries, and plugin-failure records.
  - Verification: focused provenance and loop tests cover repeated same-class
    plugin instances with different score deltas and matching ids across
    manifest and history surfaces.

- [x] Document and implement plugin side-effect validation.
  - README/plugin-doc evidence: plugin docs say plugins can modify effective
    score and maintain internal state, and README says score provenance is
    recorded under `metadata.score_composition`.
  - Status: README, plugin docs, and run-artifact docs now state that
    plugin-added metrics and metadata are validated before archive admission
    and history logging. Unsafe metric/metadata mutations are rolled back,
    score changes from that plugin are rejected, and score-composition records
    include bounded redacted diagnostics.
  - Verification: focused loop tests cover valid metadata side effects,
    non-serializable metadata, non-finite metadata, unsafe metrics, and
    successful history logging without quarantine after rollback.

- [x] Document and validate explicit plugin instance requirements.
  - README/plugin-doc evidence: plugin docs describe plugins as `PluginBase`
    extensions with hook methods, which can imply the runtime rejects values
    that are not plugin instances.
  - Status: README and plugin docs now document the direct plugin protocol.
    `evolve()` validates explicit plugin objects before run setup:
    `PluginBase` is accepted, duck-typed plugins must expose callable hooks for
    the selected run mode, zero-generation runs can use artifact-only hooks,
    and invalid objects are rejected before manifest/history creation or
    overwrite cleanup.
  - Verification: focused loop tests cover invalid direct objects for
    zero-generation and mutation-capable runs, artifact preservation under
    overwrite, valid artifact-only zero-generation plugins, and rejection of
    artifact-only plugins for mutation runs.

- [x] Document and enforce plugin prompt-context metadata schema.
  - README/plugin/run-artifact evidence: README and plugin docs describe
    candidate metadata recording per-plugin prompt context and retrieval
    summaries, which implies those records are safe typed provenance.
  - Status: README, plugin docs, and run-artifact docs now state that
    `prompt_context_metadata()` may return `None` or `{}` for no metadata and
    must return a mapping for emitted metadata. Non-mapping returns abort with
    plugin-failure provenance, and mapping contents are validated/redacted
    before candidate history logging.
  - Verification: focused loop tests cover unsafe labels/values, secret
    redaction, ordinary Unicode labels, empty returns, and list/string/scalar/
    boolean non-mapping returns.

- [x] Document evaluator artifact copy-out confinement and limit semantics.
  - README evidence: artifact copy-out is presented as retained evaluation
    evidence, so README and run-artifact docs must say what is bounded and
    where paths are rooted.
  - Status: README, configuration docs, and run-artifact docs now state that
    artifact globs are path-segment aware, matched symlinks are skipped with
    `link_not_followed`, regular source sizes are checked before reads, and
    copied artifact records include both parent-rooted and
    artifact-directory-relative path fields.
  - Verification: focused evaluator tests cover max-byte precheck, link skip
    where supported, nested custom artifact roots, and normal copy-out.

- [x] Document or enforce safe evaluator artifact selector labels.
  - README/config evidence: evaluator artifact selectors are persisted as
    effective run configuration.
  - Status: enforced and documented. Secret-like artifact include/exclude
    selector text is rejected before manifest writes, and README,
    configuration docs, and run-artifact docs state that selector patterns must
    be non-empty display-safe globs without secret-like text.
  - Verification: focused config/evaluator/database tests prove rejected
    secret-like selector values do not create manifest artifacts.

- [x] Document or reject path-unsafe evaluator artifact selectors.
  - README/config/run-artifact evidence: artifact selectors are documented as
    workspace-relative collection policy.
  - Status: rejected and documented. README, configuration docs, and
    run-artifact docs state that selector patterns must be workspace-relative
    POSIX globs and reject traversal components, dot/empty components,
    absolute or drive-style roots, leading backslashes, and Windows
    backslashes.
  - Verification: focused config/evaluator/database tests cover unsafe
    selectors and valid retained selectors.

- [x] Document or fix multi-stage metadata retention limits.
  - README/run-artifact evidence: README and run-artifact docs describe staged
    evaluators, per-stage artifacts, and structured evaluation records.
  - Status: fixed and documented. Successful multi-stage evaluations now retain
    every configured stage's selected result in
    `evaluation.metadata.configured_stage_results[]`, while README,
    configuration docs, and run-artifact docs explicitly state that the
    top-level `metadata.stage` and `metadata.artifacts` fields remain the
    final selected or stopped-stage compatibility view.
  - Verification: focused evaluator tests cover successful multi-stage
    metadata/artifact retention and early threshold-stop metadata retention.

- [x] Document or fix unbounded timeout-cleanup output metadata.
  - README/run-artifact evidence: README describes timeout cleanup and
    persisted evaluator diagnostics.
  - Status: fixed and documented. Timeout cleanup stdout/stderr/error fields
    are redacted and truncated before persistence at a separate 2,000-character
    cap, and run-artifact docs describe `timeout_cleanup.output_policy` and
    per-field diagnostics. README notes that cleanup diagnostics are bounded
    separately from validator stdout/stderr.
  - Verification: focused evaluator tests cover bounded cleanup output,
    redaction, truncation, fallback errors, and non-Windows cleanup metadata.

- [x] Document or fix strict-JSON diagnostic-message redaction limits.
  - README/run-artifact evidence: README describes invalid history and
    manifest streams as diagnostic artifacts.
  - Status: fixed and documented. Strict JSON exception and quarantine
    messages are now bounded and secret-redacted in addition to the existing
    bounded/redacted `record_repr` snapshot. README and run-artifact docs state
    that these are still sensitive diagnostic artifacts, not fully sanitized
    audit logs.
  - Verification: focused JSONL tests cover redacted raised exceptions,
    redacted quarantine messages, bounded oversized messages, cyclic/deep
    diagnostics, and record-repr redaction.

- [x] Document or fix tuple-to-array coercion in strict JSON artifacts.
  - README/run-artifact evidence: README describes manifest/history artifacts
    as strict JSON/JSONL run evidence.
  - Status: fixed and documented. Strict JSON writers reject tuple values
    instead of silently emitting JSON arrays, and README/run-artifact docs state
    that runtime tuples must be converted to explicit lists by producers.
  - Verification: focused JSONL tests cover tuple rejection for manifest,
    history/quarantine, and prompt-history persistence boundaries.

- [x] Document or enforce bounded evaluator stage retry counts.
  - README/config evidence: docs describe `eval_stages[].retries` as part of
    cascade evaluation.
  - Status: enforced and documented. Configured stage retries are capped at
    `10`, and README/configuration/run-artifact docs state how retry counts
    multiply with samples while keeping total per-stage wall-clock budgets as
    future work.
  - Verification: focused config/evaluator tests cover rejected oversized
    retries and accepted boundary retries.

- [x] Document evaluator retry scope for below-threshold valid samples.
  - README/config evidence: docs describe `eval_stages[].retries` and
    `min_score` together.
  - Status: implemented and documented. README, configuration docs, and
    run-artifact docs state that `min_score` makes retries threshold-aware and
    that attempt records distinguish local validity from threshold pass/fail.
  - Verification: focused evaluator tests cover threshold-aware retry success,
    threshold-aware retry exhaustion, and existing invalid/error retry behavior.
- [x] Document terminal candidate budget-stop metadata limits.
  - README/run-artifact evidence: README says `manifest.json` records runtime
    stop/budget accounting and run histories contain per-candidate budget
    metadata, which can imply the budget-exhausting candidate row itself
    carries the stop reason.
  - Status: implemented and documented. Candidate `metadata.budget` snapshots
    are now taken after the post-evaluation budget check, so terminal
    seed/generated rows that consume evaluation or detailed evaluator-counter
    limits record `metadata.budget.stop_reason`. Run-artifact docs also state
    that final manifests remain authoritative for completed and aborted run
    status.
  - Verification: focused loop tests cover terminal `max_evaluations=2` and
    `max_evaluator_subprocess_attempts` history-row stop reasons matching final
    manifest stop reasons.
- [x] Document or enforce non-blank provider credential preflight.
  - README/backend-doc evidence: docs say OpenAI/Anthropic credentials and
    backend construction are preflighted before overwrite cleanup for mutation
    runs, which implies unusable blank credentials fail before run setup.
  - Status: enforced and documented. CLI backend preflight now strips
    `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` before testing presence. README
    and backend docs state that mutation-capable CLI runs require non-blank
    credentials after trimming.
  - Verification: focused CLI tests cover whitespace-only OpenAI and Anthropic
    credentials failing before overwrite cleanup or `evolve()`, plus the
    zero-generation provider-free path.
- [x] Document or fix the direct `evolve()` backend-preflight boundary.
  - README/run-artifact evidence: docs say provider/backend construction is
    preflighted before overwrite cleanup for runs where mutation LLM calls can
    occur.
  - Status: implemented and documented. Core `evolve()` now constructs
    configured backend clients for mutation-capable runs before run-directory
    preparation. README and run-artifact docs describe provider setup preflight
    as runtime behavior, while noting that the CLI adds non-blank
    OpenAI/Anthropic credential checks.
  - Verification: direct loop tests cover missing OpenAI credentials preserving
    an existing history file under overwrite mode and writing no replacement
    manifest; CLI tests cover the stricter credential-presence path.
- [x] Document or reject secret-like configured `run_id` values.
  - README/run-artifact evidence: README and run-artifact docs describe
    `run_id` as manifest-safe provenance metadata, which can imply it is safe
    to share.
  - Status: enforced and documented. Configured `run_id` values must match the
    manifest-safe identifier regex and also pass the same secret-pattern
    redaction check used by other durable manifest labels. README,
    configuration docs, and run-artifact docs now state that secret-like token
    patterns are rejected.
  - Verification: focused config, database manifest, and CLI tests reject
    regex-valid provider-token-shaped `run_id` values before `evolve()` or
    manifest writes.
- [x] Document or fix `config.yaml` regular-file and provenance behavior.
  - README/config evidence: configuration docs describe problem-local
    `config.yaml` as part of effective run setup and list malformed YAML,
    invalid UTF-8, duplicate keys, and scalar/list top-level diagnostics.
  - Status: implemented and documented. CLI-loaded `config.yaml` must be absent
    or a regular file; symlinks, Windows junctions, and directories are
    rejected before reading. README, configuration docs, and run-artifact docs
    now state that config-source presence/absence and present-file hash/byte
    count are recorded under `manifest.provenance.config`.
  - Verification: focused CLI tests cover directory-shaped config rejection,
    absent config-source propagation, and manifest hash/byte-count persistence.
- [x] Document or enforce secret-safe `config.yaml` startup diagnostics.
  - README/config evidence: README and problem-format docs describe
    `config.yaml` validation errors as startup diagnostics users may paste into
    support threads or CI output.
  - Status: enforced and documented. Config loader diagnostics now use the
    stable `config.yaml` label plus secret-pattern redaction for parser/key
    text. README and configuration docs state that raw absolute problem roots
    are not printed by CLI config diagnostics.
  - Verification: focused CLI tests cover secret-like problem roots in
    malformed YAML and invalid UTF-8 diagnostics, plus secret-like duplicate
    and unknown config keys.
- [x] Document or fix secret-bearing YAML duplicate-key diagnostics.
  - README/config/problem-format evidence: setup-file validation errors are
    startup diagnostics users may paste into issue reports, CI logs, or audit
    notes.
  - Status: enforced and documented. Duplicate-key diagnostics for
    `config.yaml`, `metrics.yaml`, and context manifests pass through shared
    secret-pattern redaction before CLI display. README, configuration docs,
    and problem-format docs now state that duplicate-key diagnostics redact
    common secret-like key text.
  - Verification: focused CLI and loader tests cover secret-like duplicate keys
    in config, metrics, and context manifest YAML.
- [x] Document or fix equality-spoofing in smoke example validators.
  - README/example evidence: README examples are used as the first proof that
    LibreEvolve can evolve and validate programs, so their validators should be
    explicit about what behavior and output types are being checked.
  - Status: enforced and documented. README and problem-format docs state that
    the smoke validators enforce concrete output-type contracts:
    `hello_world` exact `str`, `sorting` exact `list`, and `workspace_math`
    exact `int` helper-dependent results.
  - Verification: focused example tests cover equality-spoofing rejections and
    wrong output-type rejections across the three representative fixtures.
- [x] Document or enforce direct `Problem.primary_bounds` semantics.
  - README/API evidence: README and problem-format docs present metric bounds
    as objective-schema inputs used for normalization, archive selection, and
    run provenance, while direct `Problem(...)` construction is also a
    supported API path.
  - Status: enforced and documented. Direct `Problem.primary_bounds` must be a
    finite numeric `[lo, hi]` pair matching the declared primary metric bounds.
    README and problem-format docs now state this instead of implying the field
    is ignored compatibility input.
  - Verification: focused loader tests cover malformed, boolean, non-finite,
    conflicting, descending, and matching direct bounds.
- [x] Document or reject unknown objective metric helper lookups.
  - README/API evidence: README and problem-format docs present metric names as
    declared objective-schema fields with direction and bounds.
  - Status: rejected and documented. Public objective helper methods now
    require declared metric names, and README/problem-format docs state that
    undeclared feedback or plugin metrics may be logged/rendered without being
    assigned declared objective semantics.
  - Verification: focused loader tests cover `KeyError` for unknown helper
    names, and focused prompt tests preserve undeclared extra-metric rendering.
- [x] Document or enforce immutability of effective problem metric schemas.
  - README/API evidence: docs describe loaded/direct problem metrics as the
    objective schema for scoring, normalization, and archive behavior.
  - Status: enforced and documented. Effective `Problem.metrics` records and
    nested bounds are frozen after validation, and README/problem-format docs
    state that caller-owned inputs and objective-schema snapshots cannot mutate
    runtime normalization semantics.
  - Verification: focused loader tests cover source mutation, attempted
    post-construction mutation, and defensive `objective_schema()` copies.
- [x] Document or enforce `log_dir` display/path safety.
  - README/run-artifact evidence: README describes `log_dir` as the root for
    run artifacts and manifests as retaining redacted/hash-backed log-dir
    metadata.
  - Status: enforced and documented. README/configuration docs now state that
    configured log roots reject path/display-unsafe components before run
    setup, while manifest retention keeps safe relative values readable and
    absolute/secret-like values redacted or hash-backed.
  - Verification: focused config, CLI, and manifest tests cover invalid
    path/display labels, valid path-like roots, and existing secret-safe
    retention.
- [x] Document or fix duplicate migrated elites.
  - README/run-artifact evidence: README describes synchronous island archives
    and ring migration, which can imply each island archive contains distinct
    candidate records.
  - Status: fixed and documented. Repeated migration now skips a target island
    that already contains the canonical program id, and README/run-artifact
    docs describe migration as canonical-id placement references rather than
    clone/version ids.
  - Verification: focused island tests cover repeated migration without elite
    duplicate inflation and show migrated occupants are the same canonical
    object with separate placement metadata.
- [x] Document migration/resume candidate-id semantics.
  - README/run-artifact evidence: README presents program ids, lineage,
    history, MAP-Elites cells, and island archives as inspectable experiment
    evidence.
  - Status: documented and manifest-recorded. Migrated candidates share one
    canonical id across island placements; clone ids are not created; duplicate
    target placements are skipped; manifests state that snapshot restore is not
    implemented yet.
  - Verification: README/run-artifact docs were updated, focused database tests
    verify `policies.archive_identity`, and focused migration tests verify the
    runtime placement semantics.
- [x] Document or fix mutable archived `Program` object aliasing.
  - README/run-artifact evidence: README and run-artifact docs describe history
    rows, archive admission, and `show` output as stable candidate evidence.
  - Status: fixed and documented. Accepted programs are snapshotted at
    archive/log boundaries, and public database accessors return defensive
    snapshots instead of live internal references.
  - Verification: focused database tests mutate the original accepted program
    and returned accessor snapshots, proving stored log/archive state remains
    stable.
- [x] Document or fix malformed direct `Program.evaluation` records.
  - README/run-artifact evidence: docs describe candidate history and failure
    history as structured evaluator-result records.
  - Status: fixed and documented. `Program.evaluation` now must be a JSON-safe
    mapping at construction and is revalidated before archive admission,
    accepted-history logging, failure-history logging, and seed-failure
    logging. README/run-artifact docs state this boundary.
  - Verification: focused database tests cover construction rejection and
    post-construction non-mapping/non-JSON evaluation mutation before admit,
    log, failure, and seed-failure operations.
- [x] Document or fix primary-only seed failure snippets for workspace seeds.
  - README/run-artifact evidence: README and run-artifact docs describe
    workspace candidates, seed failures, and failed-trial memory as persisted
    evidence that can be reused in prompts and inspected after a run.
  - Status: fixed and documented. Rejected workspace seed rows now render every
    seed file into bounded `mutation_text` and include `seed_workspace`
    metadata with per-file path, role, byte count, SHA-256, snippet, and
    truncation flags. README and `docs/run-artifacts.md` document the field.
  - Verification: focused seed-failure database tests passed and prove a
    `helper.py` seed file containing `value = 12345` appears in persisted
    failure memory instead of being lost behind primary-file-only
    `program.code`.
- [x] Document or fix zero-generation all-invalid seed run semantics.
  - README/run-artifact evidence: README and run-artifact docs describe
    seed-only/evaluation-only runs as provider-free baselines and describe
    `show`/best artifacts around valid archived output.
  - Status: fixed and documented. Invalid-only `max_generations=0` runs now
    record `runtime.stop_reason: "no_valid_programs"` with completed runtime
    status, persisted history/failure-history diagnostics, no best artifacts,
    and the existing nonzero CLI no-best error. README and
    `docs/run-artifacts.md` document this contract.
  - Verification: focused loop and CLI tests cover invalid-only and mixed
    zero-generation seed runs plus the CLI manifest/artifact state.
- [x] Document or fix `PromptProgram` template validation boundaries.
  - README/run-artifact evidence: README describes prompt programs as selected,
    scored, logged, and potentially evolved run state, which implies valid
    prompt-program records should contain renderable templates.
  - Status: fixed and documented. Prompt-program construction and revalidation
    now enforce the shared prompt-template validator, and README plus
    `docs/run-artifacts.md` state that selected/scored prompt-program records
    cannot carry non-string, unknown-placeholder, or incompatible-format
    templates as valid archive state.
  - Verification: focused meta-prompt tests cover invalid construction,
    mutated-state revalidation, database add revalidation, configured-template
    rejection, and invalid mutation quarantine.
- [x] Document or fix raw rejected prompt-template quarantine records.
  - README/run-artifact evidence: prompt-history invalid streams are run
    artifacts and should follow bounded diagnostic-retention policy for
    prompt-bearing records.
  - Status: fixed and documented. Rejected prompt-template quarantine records
    now store only a bounded/redacted template preview plus raw length, hash,
    redaction, and truncation metadata. README and `docs/run-artifacts.md`
    document the schema.
  - Verification: focused meta-prompt tests prove fake provider-key text and a
    long repeated tail are absent from `prompt_history_invalid.jsonl` while
    length/hash metadata remain.
- [x] Document or fix non-atomic prompt reward metadata failures.
  - README/run-artifact evidence: prompt history and prompt-program statistics
    are run artifacts for prompt selection, so failed score writes should not
    silently alter live selection state.
  - Status: fixed and documented. Invalid prompt score metadata now writes a
    bounded quarantine diagnostic and leaves prompt-arm `uses`, `reward_sum`,
    metadata, and selection state unchanged. README and `docs/run-artifacts.md`
    document the behavior.
  - Verification: focused meta-prompt tests cover invalid metadata, repeated
    invalid metadata, non-finite reward with metadata, unchanged score history,
    and stable prompt selection after rejected score metadata.
- [x] Document or fix raw prompt reward metadata persistence.
  - README/run-artifact evidence: prompt history is an auditable prompt-program
    artifact with validated metadata, which implies persisted prompt score
    metadata should be bounded and redacted like prompt-visible evidence.
  - Status: fixed and documented. Accepted score metadata is recursively
    normalized, redacted, and bounded before live state or prompt history
    persistence; unsafe keys are stored with redacted/truncated labels plus
    short SHA-256 suffixes. README and `docs/run-artifacts.md` document this
    schema.
  - Verification: focused meta-prompt tests prove fake provider-key text is
    absent from live/persisted score metadata while sanitized keys, values,
    nested records, lists, and bounded long strings remain inspectable.
- [x] Document and fix raw current-template exposure in meta-prompt evolution.
  - README/configuration evidence: prompt programs are selected, scored,
    logged, and optionally mutated, so meta-prompt input handling needs the
    same redaction/budget clarity as prompt-history artifacts.
  - Status: fixed and documented. README, architecture docs, and run-artifact
    docs now state that meta-prompt calls receive a redacted/capped current
    template section, a separate placeholder list, and template hash/length/
    redaction/truncation provenance in mutation context metadata.
  - Verification: focused loop tests cover secret-like and oversized current
    templates and assert raw secret text is absent from both the provider prompt
    and mutation-context metadata.
- [x] Document and fix raw meta-prompt evidence dictionary keys.
  - README/prompt evidence: README describes meta-prompt evolution as using
    redacted prompt-performance evidence, so dynamic evidence labels need to be
    covered as well as string values.
  - Status: fixed and documented. README, architecture docs, and run-artifact
    docs now state that meta-prompt evidence keys are redacted/bounded and
    hash-suffixed when changed.
  - Verification: focused loop tests prove fake provider-key text in
    top-level/nested evidence keys and metric keys is absent after sanitization.
- [x] Document and enforce secret-safe plugin metadata keys.
  - README/plugin evidence: plugin metadata from `prompt_context_metadata()` and
    `run_artifacts_metadata()` is persisted in history rows or manifests, so
    metadata labels need the same shareability boundary as values.
  - Status: fixed and documented. README, plugin docs, and run-artifact docs now
    state that secret-like or oversized plugin metadata keys are persisted as
    bounded hash-suffixed labels, with credential-shaped keys using a neutral
    redacted label.
  - Verification: focused loop tests prove fake provider-key text is absent
    from prompt-context history metadata and run-artifact manifest metadata.
- [x] Document and fix host-dependent evaluator stdout/stderr decoding.
  - README/evaluator evidence: evaluator stdout/stderr are persisted
    diagnostics and can later inform prompt feedback, so text transport must be
    deterministic.
  - Status: fixed and documented. README and run-artifact docs now describe
    byte capture, explicit UTF-8 replacement, stream-decoding diagnostics,
    secret redaction, and truncation ordering for validator stdout/stderr.
  - Verification: focused evaluator tests prove malformed validator bytes are
    replaced deterministically and reported through `diagnostic_output`.
- [x] Document and enforce validator stdin behavior.
  - README/evaluator evidence: validators are local subprocesses with timeouts,
    environment allowlists, and stdout/stderr capture, so standard input must
    have an explicit unattended-run policy.
  - Status: fixed and documented. README and run-artifact docs now state that
    validator stdin is `DEVNULL`, interactive prompts are unsupported,
    `input()` receives EOF, and direct stdin reads return empty input.
  - Verification: focused evaluator tests cover both `input()` and
    `sys.stdin.read()` behavior under the documented policy.
- [x] Document and fix skipped-link provenance hash limits.
  - README/run-artifact evidence: README and run-artifact docs present problem
    and source provenance hashes as reproducibility evidence for the files that
    shaped a run, including skipped diagnostics.
  - Status: fixed and documented. Skipped symlinks and junctions now record
    redacted/hash-backed target identity plus target scope and within-root
    status, and README/run-artifact docs name the v2 skipped/provenance hash
    scopes used for those diagnostic records.
  - Verification: focused provenance tests cover target-aware symlink and
    Windows junction skipped records; docs checks pass with the updated wording.
- [x] Document and fix missing-parent persistence helper failures.
  - README/run-artifact evidence: README describes manifests, history streams,
    failure streams, prompt history, and plugin artifacts as normal run
    artifacts under managed directories.
  - Status: fixed and documented. README and run-artifact docs now state that
    valid strict JSON/JSONL/quarantine writes create missing parent directories,
    while invalid parent paths fail with bounded, secret-redacted
    `StrictJsonlError` diagnostics.
  - Verification: focused JSONL and TTTRL plugin tests cover the documented
    helper and plugin-artifact behavior.
- [x] Document and fix `show` archive-admission program-id mismatches.
  - README/run-artifact evidence: README and run-artifact docs describe
    `history.jsonl` plus `metadata.archive_admission` as stable candidate
    evidence used by `libreevolve show` to identify the best archive-retained
    valid program.
  - Status: fixed and documented. `show` now rejects present
    `archive_admission.program_id` values that are unsafe or do not match the
    history row `id`, while preserving compatibility for current-format rows
    that lack the field.
  - Verification: focused CLI tests cover accepted matching/missing ids and
    rejected selected/unselected mismatches before display.
- [x] Document and fix raw dependency-name labels in runtime provenance.
  - README/manifest evidence: README-facing runtime provenance text says
    manifests record declared dependency versions and redacts private source
    details, which can imply both dependency specs and dependency labels are
    safe manifest fields.
  - Status: fixed and documented. README and run-artifact docs now describe
    redacted dependency names, `name_hash`, `name_redacted`, and redacted
    installed-version lookup labels for unsafe dependency names.
  - Verification: focused provenance tests prove secret-like dependency names
    are absent from rendered provenance while clean names and direct URL specs
    retain useful reproducibility fields.
- [x] Document and fix `__pycache__` handling for generated candidate paths.
  - README/problem-format evidence: README says seed workspaces skip
    `__pycache__` components and that workspace candidate paths are normalized
    for safe generated files.
  - Status: fixed and documented. README, problem-format docs, and architecture
    docs now state that generated candidate paths reject `__pycache__`
    components, matching seed-workspace cache skipping.
  - Verification: focused candidate tests cover direct and mutation-created
    cache paths; loader tests confirm cache seed directories are skipped.
- [x] Document and fix mutable archive-sequence recency sampling.
  - README/search evidence: README describes parent and inspiration sampling by
    recency as a way to resurface recent archive/search state.
  - Status: fixed and documented. Recency now uses a monotonic in-memory archive
    sequence, while persisted `metadata.archive_sequence` and
    `metadata.archive_admission.archive_sequence` are audit/provenance fields
    that do not control sampling after later metadata mutation.
  - Verification: focused island tests cover metadata mutation resistance for
    both parent recency and inspiration recency sampling.
- [x] Fix Click CLI usage text for Windows launcher consistency.
  - README/CLI evidence: README, AGENTS.md, and local developer instructions
    consistently tell Windows users to run LibreEvolve through `py -3.12`
    rather than `python`.
  - Status: fixed in the module entrypoint. Generated help for
    `py -3.12 -m libreevolve` now uses the same launcher text for root and
    `run` subcommand usage.
  - Verification: focused subprocess CLI tests and direct help invocations
    confirm the documented launcher appears and the stale
    `Usage: python -m libreevolve` banner is absent.
- [x] Document and enforce safe paper-cache manifest file names.
  - Status: implemented and documented. README and `papers/README.md` now
    describe the safe paper id/file-name rules enforced by the validator.
  - Verification: focused paper-manifest tests reject reserved, hidden, and
    Unicode format-control file names.
- [x] Document and enforce unique paper-cache file targets.
  - Status: implemented and documented. Validator reports unique local PDF
    artifact count separately and rejects duplicate normalized file targets.
  - Verification: focused tests reject duplicate `papers/shared.pdf` rows.
- [x] Document and enforce duplicate CSV-id handling in paper manifests.
  - Status: implemented. Duplicate CSV ids now produce a direct
    `duplicate_csv_id` validator issue instead of only indirect comparison
    failures.
  - Verification: focused tests cover duplicate CSV ids before JSON lookup.
- [x] Document and enforce paper-manifest row-id grammar.
  - Status: implemented and documented. Valid ids are arXiv ids or lowercase
    foundational-paper slugs; unsafe/secret-like ids fail validation.
  - Verification: focused CLI JSON tests confirm raw secret-like ids are not
    emitted.
- [x] Document and validate README paper-cache badge counts.
  - Status: implemented and documented. README badge counts are parsed with
    prose counts and compared to manifest row counts.
  - Verification: focused tests cover stale numeric and malformed badge counts.
- [x] Document and validate paper-manifest source URL safety.
  - Status: implemented and documented. Manifest source URLs are restricted to
    share-safe HTTPS URLs from known paper source hosts.
  - Verification: focused CLI JSON tests reject a local `file:` URL containing
    a secret-like token without leaking it.
- [x] Document and enforce paper-manifest message safety.
  - Status: implemented and documented. Manifest download messages are
    validated, redacted, and bounded before availability output.
  - Verification: focused tests reject oversized secret-bearing messages and
    confirm bounded redacted availability output.
- [x] Document and enforce paper-title display safety in manifests.
  - Status: implemented and documented. Titles are bounded display-safe fields
    and secret-like/multiline titles fail validation.
  - Verification: focused CLI JSON tests cover a secret-like multiline title.
- [x] Document and enforce closed paper-manifest schema semantics.
  - Status: implemented and documented. JSON and CSV manifests now reject
    unsupported fields/columns instead of silently ignoring them.
  - Verification: focused tests cover JSON and CSV extra `api_key` metadata.
- [x] Document and enforce duplicate-key rejection for JSON paper manifests.
  - Status: implemented and documented. Duplicate JSON object names are
    rejected during manifest loading.
  - Verification: focused tests reject duplicate `url` JSON keys.
- [x] Document and enforce duplicate-header rejection for CSV paper manifests.
  - Status: implemented and documented. CSV manifests require unique headers
    matching the canonical schema order.
  - Verification: focused tests reject duplicate `url` headers.
- [x] Document and enforce CSV paper-manifest header validation for empty
  manifests.
  - Status: implemented and documented. CSV header validation runs before row
    iteration, including zero-row manifests.
  - Verification: focused tests reject a wrong-header empty CSV.
- [x] Document and enforce local PDF content validation.
  - Status: implemented and documented. Required-local validation now requires
    listed PDFs to be regular files whose content starts with `%PDF-`.
  - Verification: focused tests reject hash-matching non-PDF bytes.
- [x] Document and fix eager local-PDF hash reads in paper-cache validation.
  - Status: implemented and documented. Local PDF SHA-256 verification now uses
    streaming chunked reads rather than `Path.read_bytes()`.
  - Verification: focused tests monkeypatch `Path.read_bytes()` to fail while
    a large matching local PDF still validates cleanly.
- [x] Document and enforce failed-download row semantics in paper manifests.
  - Status: implemented and documented. `ok: false` rows fail validation as
    historical failed-download records.
  - Verification: focused tests cover a failed-download row with a matching
    local PDF.
- [x] Document and enforce unmanifested local-PDF handling.
  - Status: implemented and documented. Strict local validation reports
    unmanifested local PDFs.
  - Verification: focused tests cover optional versus required local modes.
- [x] Document and enforce the local-PDF gitignore boundary.
  - Status: implemented and documented. Git-tracked local cache PDFs now fail
    validation with `tracked_pdf`.
  - Verification: focused tests cover a staged `papers/*.pdf` in a temp Git
    repository.
- [x] Document and enforce `papers/README.md` status-table validation.
  - Status: implemented and documented. The validator now reconciles
    implementation-status table IDs with manifest IDs.
  - Verification: focused tests cover missing, extra, duplicate, and exact
    status-table rows.
- [x] Document and reject link-backed local paper-cache PDFs.
  - Status: implemented and documented. Local cache PDFs must not be symlink or
    Windows reparse-point backed entries.
  - Verification: focused tests cover simulated symlink and reparse-point
    local PDFs.
- [x] Document the agent-instruction archive-admission shortcut precisely.
  - Status: fixed. Agent-facing docs now present threshold passing as
    pre-admission eligibility rather than guaranteed archive retention.
  - Verification: `tests/test_agents_docs.py` checks `AGENTS.md` for
    `not_improving_cell`, MAP-Elites retention wording, and
    `sampling_eligible`.
- [x] Enforce direct critique prompt-builder validation.
  - Status: implemented. Direct critique prompt construction now has the same
    text-only contract for custom instructions and rejects empty base/mutation
    payloads before provider-ready rendering.
  - Verification: feedback tests assert validation, redaction, truncation, and
    default-instruction behavior for `build_critique_prompt()`.
- [x] Enforce direct feedback-grader prompt validation.
  - Status: implemented. Direct feedback graders now apply prompt-field
    validation and redaction before provider calls, matching the configured
    string-only prompt contract.
  - Verification: focused feedback tests assert invalid-config diagnostics for
    non-string prompts and safe rendering for blank, secret-like, and oversized
    prompt text.
- [x] Fix direct LLM feedback grader schema failures.
  - Status: implemented. Malformed direct feedback graders now become
    structured `invalid_feedback_config` diagnostics instead of incidental
    runtime exceptions.
  - Verification: focused feedback tests cover invalid candidates with
    non-mapping graders plus unsupported fields and non-string keys.
- [x] Enforce aggregate plugin metadata limits.
  - Status: implemented. Plugin metadata remains inspectable but is bounded by
    total item count, nesting depth, and serialized JSON character limits.
  - Verification: focused loop tests cover prompt-context and run-artifact
    metadata payloads that exceed the aggregate budgets.
- [x] Document and fix skipped-context files bypassing byte read limits.
  - Status: implemented. Skipped context diagnostics now respect the source
    byte budget before content hashing while retaining small skipped-file hashes.
  - Verification: focused context-policy tests cover oversized unsupported,
    excluded, hidden, and not-included skipped files without `read_bytes()`.
- [x] Enforce problem-context provenance schema limits.
  - Status: implemented. Direct and loader-produced problem context provenance
    now passes through a manifest-boundary schema with redaction and aggregate
    limits before `manifest.json` is written.
  - Verification: focused database/loop tests cover malformed direct
    `context_policy`, malformed `context_sources`, oversized payloads, and
    secret-like context provenance text.
- [x] Enforce unambiguous JSON for LLM feedback graders.
  - Status: implemented. Feedback grader JSON with duplicate object names is
    rejected as malformed instead of being parsed with last-key-wins semantics.
  - Verification: focused feedback tests cover duplicate top-level, nested, and
    fenced JSON names plus failure metadata without changing candidate scores.
- [x] Reject duplicate JSON names in existing manifests during runtime updates.
  - Status: implemented. Existing `manifest.json` files with duplicate object
    names no longer get collapsed and rewritten during `runtime` updates.
  - Verification: focused database tests cover top-level and nested duplicate
    manifest names, structured quarantine diagnostics, unchanged manifest bytes,
    and existing unreadable-manifest recovery behavior.
- [x] Reject duplicate JSON names in inspected histories.
  - Status: implemented. The `show` command rejects ambiguous `history.jsonl`
    rows with duplicate object names instead of displaying parser-collapsed
    candidate, metric, or archive-selection values.
  - Verification: focused CLI tests cover duplicate top-level, nested metric,
    and nested archive metadata names with no summary output.
- [x] Fix invalid-encoding CSV/JSON paper-manifest failures.
  - Status: implemented. Invalid UTF-8 in committed paper manifest files now
    appears as structured validator issues rather than crashing the
    paper-manifest command.
  - Verification: focused paper-manifest tests cover invalid CSV and JSON
    encodings and assert structured issue codes.
- [x] Fix `extracted_pages` semantics for PDF context provenance.
  - Status: implemented. Loader PDF metadata distinguishes exact extracted
    pages from first/last page ranges with `extracted_pages` and
    `extracted_page_range`.
  - Verification: focused loader tests assert a PDF with extractable text on
    pages 1, 3, and 5 records `extracted_pages=[1, 3, 5]` and
    `extracted_page_range=[1, 5]`.
- [x] Clarify PDF `page:start-end` citations as page-local offsets.
  - Status: implemented. Prompt and feedback context headers now use
    page-local span fields for `page:start-end` citations, while the metadata
    still preserves concatenated global offsets for audit trails.
  - Verification: focused prompt/feedback tests assert rendered page-local
    spans instead of global offsets after inserted inter-page separators.
- [x] Validate cached-PDF prose count wording.
  - Status: implemented. The paper-manifest validator now checks
    `papers/README.md` wording such as `contains N locally cached PDFs` against
    the committed manifest row count.
  - Verification: focused paper-manifest tests cover stale cached-PDF count
    prose and structured count-mismatch diagnostics.
- [x] Fix README count-source read failures in paper validation.
  - Status: implemented. Invalid or unreadable README count sources are now
    reported as structured paper-manifest issues instead of crashing the
    validator.
  - Verification: focused paper-manifest tests cover invalid UTF-8 in both
    root README and `papers/README.md`.
- [x] Fix conflicting README count diagnostics.
  - Status: implemented. Conflicting README-facing paper-count claims now emit
    source-aware `documented_count_conflict` diagnostics that name the file,
    count surface kind, value, and matched phrase.
  - Verification: focused paper-manifest tests assert root README,
    `papers/README.md`, and badge conflicts are reported without a
    sentinel-style manifest-count mismatch.
- [x] Enforce Unicode-normalized context-path uniqueness.
  - Status: implemented. Context source labels are NFC-normalized for
    prompt-facing `context_files` and `context_sources`, with raw filesystem
    spellings retained when normalization changes the label. Normalized
    collisions are rejected before prompt construction.
  - Verification: focused loader tests cover composed/decomposed Unicode
    source paths, exact include/exclude behavior through normalization, and
    duplicate normalized context labels.
- [x] Document and enforce Unicode-normalized provenance-path uniqueness.
  - Status: implemented and documented. README and run-artifact docs now state
    that source/problem provenance uses NFC display paths, retains
    `filesystem_path` metadata when normalization changes the label, and rejects
    duplicate normalized included file paths.
  - Verification: focused provenance tests cover normalized file records,
    skipped diagnostics, collision rejection, and the shared tree-provenance
    path.
- [x] Document and enforce plugin class/module identity label safety.
  - Status: implemented and documented. README, plugin docs, and run-artifact
    docs now describe the runtime plugin identity policy: ordinary labels keep
    the existing instance-id format, while unsafe labels are normalized,
    redacted, bounded, and hash-backed before manifest or candidate-history
    persistence.
  - Verification: focused provenance and loop tests cover direct plugin
    provenance, runtime artifact attribution, and candidate plugin-context
    history with secret-like labels.
- [x] Document and enforce pyproject metadata field redaction.
  - Status: implemented and documented. README and run-artifact docs now
    describe package/build metadata as bounded, redacted/hash-backed manifest
    fields, including installed-version lookup suppression for unsafe project
    names.
  - Verification: focused provenance tests cover secret-like package name,
    version, requires-python, build backend, and build requirement metadata.
- [x] Document and enforce redaction for pyproject provenance diagnostics.
  - Status: implemented and documented. README and run-artifact docs now state
    that pyproject read, decode, and parse diagnostics are secret-redacted and
    bounded before manifest persistence.
  - Verification: focused provenance tests cover secret-bearing and oversized
    diagnostics, and CLI `show` coverage confirms runtime package diagnostics
    are not printed.
- [x] Document and enforce secret-safe paper-manifest validation diagnostics.
  - Status: implemented and documented. README and `papers/README.md` now state
    that paper-manifest diagnostics use repository-relative labels and
    secret-redacted exception text for text and JSON reports.
  - Verification: focused paper-manifest tests cover secret-like roots for
    missing manifest files, malformed JSON, and README/status-table read errors
    without preserving the raw root or token-shaped path component.
- [x] Document bounded `libreevolve show` output semantics.
  - Status: implemented and documented. README and run-artifact docs now state
    that selected legacy source and workspace file bodies are truncated at
    4,096 displayed characters per source body and include source length,
    displayed length, omitted count, source hash, and the `history.jsonl`
    full-source pointer.
  - Verification: focused CLI tests cover oversized legacy source and primary
    plus secondary workspace files without printing the omitted tail content.
- [x] Document and fix raw provenance root fields in manifests.
  - Status: implemented and documented. README and run-artifact docs now state
    that source, problem, and Git provenance roots are persisted as local labels
    with `root_hash`, `root_scope`, and `root_redacted` metadata instead of raw
    absolute paths.
  - Verification: focused provenance tests cover secret-like root labels for
    problem and Git provenance plus source-root redaction, and focused loop
    tests cover manifest/source Git lookup behavior.
- [x] Document and enforce coherent program lineage semantics.
  - Status: implemented and documented. README and run-artifact docs now state
    that program identity validation rejects self-parenting, duplicated lineage
    entries, self-in-lineage, and parent/lineage-tail mismatches.
  - Verification: focused program and CLI `show` tests cover direct object
    construction and malformed history diagnostics; database/archive/island
    focused tests cover persistence and mutation boundaries.
- [x] Document and enforce unique failed-candidate ids.
  - Status: implemented and documented. README and run-artifact docs now state
    that failure-history `program_id` values are run-local unique within
    `failure_history.jsonl`, while repeated failure patterns use shared
    fingerprints and repetition counts across distinct failed candidate ids.
  - Verification: focused database tests cover duplicate generated and seed
    failures and distinct-id repeated fingerprints.
- [x] Document finite evaluated `Program` fitness boundaries.
  - Status: documented. README and run-artifact docs now state that low-level
    direct `Program` objects can still carry non-finite numeric fitness,
    including the legacy `-inf` unevaluated sentinel, while archive admission,
    accepted-history persistence, `show`, and prompt rendering reject or mark
    those values before treating them as evaluated evidence.
  - Verification: existing focused tests cover non-finite archive rejection,
    non-finite history rejection in `show`, and invalid-fitness prompt markers.
- [x] Document and enforce boolean-free metric bounds.
  - Status: implemented and documented. README and run-artifact docs now state
    that metric bounds and primary bounds must be finite, strictly increasing,
    non-boolean numeric pairs, and that YAML/Python booleans are rejected
    instead of being coerced to `0.0/1.0`.
  - Verification: focused loader and database tests cover YAML/direct problem
    metric-bound booleans plus objective-schema primary-bound booleans.
- [x] Document and fix primary-only metric parent sampling.
  - Status: implemented and documented. README, architecture, and run-artifact
    docs now describe cyclic metric-target parent sampling and generated
    candidate `metadata.parent_selection` provenance.
  - Verification: focused island/database tests cover metric parent cycling,
    and focused loop tests cover target-metric provenance in history rows.
- [x] Document and fix rejected prompt-mutation penalty bounds.
  - Status: implemented and documented. Run-artifact docs now state that
    rejected prompt children use the configured lower-bound reward normalized
    through the same policy as score events, rather than an out-of-band
    negative reward.
  - Verification: focused meta-prompt tests cover rejection penalty metadata
    and prompt-arm selection behavior.
- [x] Document and enforce YAML anchor/alias semantics in setup files.
  - Status: implemented and documented. README, problem-format docs, and
    run-artifact docs now state that setup YAML rejects anchors and aliases, so
    loaded config, metric, and context records must be independent plain YAML
    structures.
  - Verification: focused loader and CLI tests cover anchor/alias rejection for
    `metrics.yaml`, context manifests, and `config.yaml`.
- [x] Document and reject secret-like run names.
  - Status: implemented and documented. README, configuration docs, and
    run-artifact docs now state that `problem_name` / `--run-name` must be
    secret-safe as well as portable path components.
  - Verification: focused config and CLI tests cover secret-like run-name
    rejection before run-directory setup or manifest writes.
- [x] Document and fix skipped context diagnostics preserving secret-like
  labels.
  - Status: implemented and documented. README, problem-format docs, and
    run-artifact docs now state that skipped context diagnostics use the same
    secret-like label rejection as selected context sources.
  - Verification: focused loader tests cover the documented skipped-source
    reasons that can otherwise retain path labels.
- [x] Document and enforce secret-like candidate and seed path-label handling.
  - Status: implemented and documented. README, problem-format docs, and
    run-artifact docs now state that candidate paths and loaded seed source
    labels reject secret-like values before prompt, history, manifest, or
    export surfaces.
  - Verification: focused candidate, loader, and program tests cover the
    enforcement paths and no-leak diagnostics.
- [x] Document and enforce compatibility-confusable Unicode candidate path
  labels.
  - Status: implemented and documented. README, problem-format docs, and
    run-artifact docs now state that candidate paths must be
    compatibility-normalization stable and reject non-ASCII separator spaces,
    surrogate code points, and NFKC-confusable forms.
  - Verification: focused candidate tests cover accepted ordinary non-ASCII
    names and rejected compatibility-confusable labels.
- [x] Document and validate direct `initial_workspace_sources` provenance.
  - Status: implemented and documented. Direct seed-source records now share
    the same schema as loader-created provenance before manifests or seed
    history rows are written.
  - Verification: focused database and loop tests cover malformed direct
    records, valid loader-compatible records, and pre-manifest rejection.

- [x] Document and validate direct `Problem.context_files` inputs.
  - Status: implemented and documented. README, problem-format, and
    run-artifacts docs now describe direct context as safe problem-relative
    labels mapped to bounded text, with JSON prompt rendering and pre-run
    validation.
  - Verification: prompt tests cover unsafe direct labels and oversized values;
    a loop test proves invalid direct context fails before database artifacts
    are created or overwritten.

- [x] Document and validate direct `Problem.task_description` inputs.
  - Status: implemented and documented. README, problem-format, and
    run-artifacts docs now state that direct task text is non-empty, bounded,
    secret-free, and exact-retained prompt/provenance material.
  - Verification: focused prompt tests cover invalid task values and exact
    preservation for valid multi-line text; loop tests cover pre-artifact
    rejection for malformed direct task descriptions.

- [x] Document and fix direct inline seed validation order.
  - Status: implemented and documented. README, problem-format, and
    run-artifacts docs now describe direct inline seeds as list-based,
    UTF-8-encodable, evolve-block-safe, and bounded before run preparation.
  - Verification: focused loop tests cover malformed direct inline seeds
    preserving existing artifacts and valid direct inline seeds still writing
    seed history plus `seed_source_kind: inline` provenance.

- [x] Document and fix direct `initial_workspaces` validation order.
  - Status: implemented and documented. README, problem-format, and
    run-artifacts docs now describe accepted direct workspace inputs as
    `CandidateWorkspace` objects or workspace record mappings that are
    normalized before run preparation.
  - Verification: focused loop tests cover malformed direct workspace entries
    preserving existing artifacts and valid mapping records still writing seed
    history plus workspace provenance.

- [x] Align top-level archive/sampling claims with elite-only retained
  archive semantics.
  - Status: implemented and documented. README feature, workflow, archive, and
    sampling wording now distinguish occupied-cell explore/random pools from
    retained-archive strategies that can resurface auxiliary elite-only
    candidates.
  - Verification: focused island and database tests prove elite-only programs
    are not cell `sampling_eligible` but do resurface through retained metric,
    novelty, recency, selection, mixed, best/exploit, and migration-aware
    archive paths.

- [x] Document or enforce Python-only evolve-block marker syntax.
  - Status: implemented and documented. README, problem-format docs, and
    run-artifact docs now state that skeleton-preserving evolve blocks are
    supported only in `.py` candidate files using Python
    `# EVOLVE-BLOCK-*` comments. Non-Python workspace files remain valid
    whole-file text artifacts, but JavaScript/C-style, HTML-style, or
    `# EVOLVE-BLOCK-*` marker-looking declarations in non-`.py` files are
    rejected with `unsupported_evolve_block_marker_syntax` instead of being
    silently treated as unmarked full-file replacement targets.

- [x] Document sorting as a plateau/diversity example or replace its seed.
  - Status: documented. README now identifies `sorting` as a neutral
    plateau/diversity smoke fixture whose bubble-sort seed already reaches
    `accuracy == 1.0`, and keeps seed-to-best optimization-pressure claims tied
    to `hello_world`, `circle_packing`, and `matrix_multiplication`.

- [x] Document durable LLM call-artifact semantics once implemented.
  - Status: documented. README and run-artifact docs now describe
    `llm_calls.jsonl` / `llm_calls_invalid.jsonl`, strict call rows with
    sequence ids, prompt/output digests, role/backend/retry/fallback telemetry,
    and append-only reward rows linked by `call_id`. The docs also state that
    future resume/replay readers for this stream remain open work.

- [x] Document or fix unbounded critique prompt construction and retention.
  - Status: fixed and documented. README and run-artifact docs now describe the
    critique retention policy: critique provider prompts are built from
    redacted/truncated base prompt, proposed mutation, and custom instructions;
    generated-candidate `metadata.critique` stores bounded redacted retained
    prompt/original/revised mutation text with hashes, character counts, and
    truncation flags.

- [x] Document or fix critique selection when no mutation candidate is valid.
  - Status: fixed and documented. README now states that malformed critique
    revisions fall back to a valid original mutation and that no-valid-mutation
    cases preserve the original generated mutation as the traceable failure
    payload. The run-artifact critique metadata documentation records the
    explicit `fallback_reason="no_valid_mutation"` policy.
  - Verification: focused loop tests cover invalid original plus invalid
    revised candidates in both supported mutation modes, and docs tests pass.

- [x] Document or add wall-clock timestamps in run manifests.
  - Status: added and documented. README and run-artifact docs now describe
    `runtime.wall_clock`, UTC start/update/finish timestamps, completed versus
    aborted timestamp fields, the link to monotonic
    `runtime.consumed.runtime_seconds`, and the current initial-process resume
    segment representation.
  - Verification: focused budget/loop tests cover timestamp fields in direct
    snapshots plus completed and aborted manifests; docs tests pass.

- [x] Document or fix `show` ignoring aborted manifest runtime status.
  - Status: implemented and documented. `libreevolve show` reads
    `manifest.json.runtime` when present and prints completed run status,
    aborted best-so-far status, or partial best-so-far status when runtime
    finalization is missing. Missing manifests remain legacy history-only, and
    manifest/history row-count mismatches fail inspection.
  - Verification: CLI tests cover completed manifests, aborted-after-seed
    manifests, aborted-after-candidate manifests, missing runtime sections,
    missing manifests, and mismatched `runtime.history.programs_logged` counts.

- [x] Document or fix stale generated runs affecting problem provenance.
  - Status: implemented and documented. Problem provenance now classifies
    directories under `runs/` that contain known LibreEvolve run-artifact
    markers as generated outputs and skips them with
    `reason: generated_run_artifacts`; ordinary fixture files under `runs/`
    remain included as problem inputs. Active generated run roots are still
    skipped with `reason: excluded_output_root`.
  - Verification: provenance tests cover ordinary fixtures under `runs/`,
    active generated roots, stale generated run directories, and problem
    `tree_hash` stability when stale generated run artifact contents change.

- [x] Document semantic requirements for configured prompt seeds.
  - Status: documented. README, configuration, architecture, and paper-index
    docs now state that configured prompt variants are renderability-checked
    compatibility inputs that may omit parent code/workspace, inspiration or
    failure context, feedback, proposal metadata, and mutation-format
    instructions. Those minimal seeds are user-responsibility prompt
    engineering rather than AlphaEvolve-fidelity guarantees until a stricter
    prompt-policy option is implemented.

- [x] Document duplicate prompt-program behavior or deduplicate prompt
  variants.
  - Status: implemented and documented as independent duplicate arms. Accepted
    prompt-history records now include `template_sha256`, while duplicate
    configured variants and duplicate evolved templates remain separate prompt
    programs with independent ids, rewards, usage counts, and lineage. README,
    configuration, architecture, and run-artifact docs describe that policy.
  - Verification: prompt-database tests cover duplicate configured variants
    and duplicate mutated templates sharing the same template hash while
    retaining separate prompt ids and reward state.

- [x] Document the former limited scope for non-archive `show` fields.
  - Status: documented. README, run-artifact docs, architecture docs, and the
    paper index now state that `libreevolve show` validates ids, metrics,
    current-history evaluation shape, and archive diagnostics while streaming,
    but non-archive source/workspace display fields were limited to the chosen
    best row at that point.
  - Superseded by implementation: `libreevolve show` now validates generation,
    legacy source, workspace files, and primary-file payloads while streaming
    every history row. The earlier selected-row caveat has been removed from
    README, run-artifact docs, and architecture docs.

- [x] Document or implement manifest-bound archive cell upper-bound
  validation.
  - Status: implemented and documented. `libreevolve show` now reads
    `manifest.json.config.map_elites_bins` when present and rejects
    out-of-range current-history MAP-Elites cell coordinates with
    line-numbered diagnostics. README, run-artifact docs, architecture docs,
    and the paper index document the manifest-bound check and the legacy
    fallback when manifest/bin metadata is absent.
  - Verification: CLI tests cover out-of-range cells, missing-bin legacy
    behavior, and malformed manifest `map_elites_bins` values.

- [x] Document live-retrieval transport and integrity limits.
  - Status: documented. README, plugin docs, run-artifact docs, and the paper
    index now state that DeepResearch retrieval provenance is best-effort, not
    audit-grade source integrity. The docs list the remaining gaps: full
    provider payload snapshots, replayable ranked-source provenance,
    source-content trust policy, detailed redirect/failure policy, and
    TLS/certificate failure classification.
  - Remaining implementation gap: making live retrieval audit-grade remains
    open in code, roadmap, and paper TODOs.

- [x] Document LLM request parameters and remaining prompt-role controls.
  - Status: documented. README, backend docs, configuration docs, run-artifact
    docs, architecture docs, and the paper index now state that the bundled
    adapters send one rendered prompt as a single user message/input item,
    while validated provider-supported request parameters are configured and
    persisted in LLM call telemetry. Call roles remain validated
    telemetry/backend-hook labels, not structured system/developer/user prompt
    serialization.
  - Remaining implementation gap: structured prompt-role serialization remains
    open in code, roadmap, and paper TODOs.

- [x] Document provider endpoint/client-context provenance.
  - Status: documented and superseded by implementation. README, backend docs,
    configuration docs, run-artifact docs, architecture docs, and the paper
    index now state the explicit built-in backend client-context fields:
    OpenAI `base_url`, `organization`, and `project`; Anthropic `base_url`;
    and Ollama `host`. They also note that omitted fields still inherit
    SDK/environment defaults.
  - Implementation follow-up: backend/config validation, adapter forwarding,
    call telemetry, replay validation, and focused tests now live under the
    completed code/roadmap/paper TODO ledgers.

- [x] Document LLM call-telemetry id replay limits.
  - Status: superseded by implementation. README, backend docs, run-artifact
    docs, architecture docs, and the paper index now state that LLM call `id`
    values are deterministic ordered-call-stream identities for in-run reward
    linkage. Matching deterministic call streams can compare call id equality;
    broader candidate lineage and provider-output replay remain open.

- [x] Document prompt-program history replay semantics.
  - Status: superseded by implementation. README, run-artifact docs,
    architecture docs, and the paper index now state that non-empty
    `prompt_history.jsonl` files are replayed into `PromptDatabase` before
    configured prompt templates are seeded.
  - Remaining implementation gap: whole-run resume still needs
    archive/controller, RNG, lineage-id, and provider-output restore work.

- [x] Fix island round-robin cursor effects from non-admitted candidates.
  - Status: fixed and documented. `IslandModel.add()` now advances the
    round-robin island cursor only when `search_state_changed` is true.
    Threshold-passing candidates that are not retained, such as
    `reason: "not_improving_cell"`, record the attempted island but do not
    consume the next island assignment.
  - Verification: direct `IslandModel` and public `ProgramDatabase.admit()`
    regression tests cover a non-improving candidate followed by a replacing
    candidate, proving the next retained update remains on the same island.
  - Remaining implementation gap: persisted/resumed island cursor state remains
    open in code, roadmap, and paper TODOs.

- [x] Document non-finite rejected-candidate history behavior.
  - Status: documented. README, run-artifact docs, architecture docs, and the
    paper index now state that rejected archive-admission metadata is kept
    finite/JSON-safe, but it does not normalize hook-mutated or restored
    top-level non-finite `fitness` or metric values into accepted
    `history.jsonl` rows. Such malformed rejected records fail strict history
    validation and should be inspected through `history_invalid.jsonl` until a
    dedicated finite rejected-candidate persistence policy exists.
  - Remaining implementation gap: finite rejected-candidate streams or
    normalization with explicit diagnostics remain open in code, roadmap, and
    paper TODOs.

- [x] Persist recovered LLM retry/fallback attempts on successful candidates.
  - Status: already implemented in current code and verified while closing the
    stale README item. `evolve()` captures the retained LLM call span from
    before mutation through feedback and stores it under
    `metadata.llm_calls`; `llm_calls.jsonl` also stores run-scoped call/reward
    rows for config-created ensembles.
  - Verification: `test_successful_candidate_persists_recovered_llm_fallback_span`
    proves a successful candidate keeps both the failed backend-0 error call
    and the successful backend-1 fallback call in `metadata.llm_calls`.
  - Remaining implementation gap: exhausted provider exceptions and
    meta-prompt-specific call-span/replay policy remain open in code-level LLM
    failure/quarantine TODOs.

- [x] Document and diagnose direct `evolve()` plugin configuration semantics.
  - Status: implemented and documented. Runtime manifests now include
    `runtime.plugin_state` with configured plugin labels, loaded runtime plugin
    identities, mismatch diagnostics for configured labels without loaded
    instances and loaded instances without configured labels, and
    `core_resolves_config_plugins: false`.
  - Verification: focused direct API tests cover
    `Config.plugins=["causal"]` without plugin instances and explicit plugin
    instances without configured labels.

- [x] Document manifest retention for configured prompt text.
  - Status: documented. README, run-artifact docs, configuration docs,
    architecture docs, and the paper index now state that current startup
    manifests retain `prompt_variants`, `critique_prompt`, and
    `llm_feedback[].prompt` as raw effective config. Runs whose prompt config
    includes private task instructions, copied source, or credentials should
    treat `manifest.json` as sensitive.
  - Remaining implementation gap: defining hash/redaction-only prompt-config
    provenance, truncation metadata, and opt-in raw retention remains open in
    code, roadmap, and paper TODOs.

- [x] Close stale README archive-admission/history consistency item.
  - Status: already fixed and documented in current code/docs. Accepted archive
    admissions prevalidate the strict candidate history record before
    MAP-Elites/island insertion, so malformed accepted records such as
    non-serializable metadata fail before becoming `db.best()` or a parent,
    inspiration, or migration source.
  - Verification: the completed code item
    "Validate candidate history records before live archive admission" records
    focused database tests proving non-serializable metadata fails before live
    archive mutation and leaves `db.best()` empty. README and run-artifact docs
    already describe this boundary.

- [x] Document restored run-budget counter schema boundary.
  - Status: documented. README, run-artifact docs, architecture docs, and the
    paper index now state that current runtime budget validation covers the
    active non-resumed `RunBudget` process state. A later slice added
    `validate_restored_budget_snapshot()` for restored snapshot preflight, but
    full resume/controller state application remains open.
  - Remaining implementation gap: controller budget-event schemas and live
    resumed-run state application remain open in roadmap and paper TODOs.

- [x] Document full environment-provenance limits in README-level wording.
  - Status: documented. README, architecture docs, run-artifact docs, and the
    paper index now state that environment provenance is a bounded
    direct-dependency summary: Python/platform metadata, `pyproject.toml`
    status/hash, package/build metadata, and installed versions for declared
    runtime dependencies.
  - Remaining implementation gap: lockfile/freeze provenance, transitive
    dependency snapshots, dev/test tool inventory, numerical backend/BLAS
    details, accelerator budget/accounting state, private package-source policy,
    live provider service/API-version capture, and provider
    cost or remote provider-side default capture remain open in code, roadmap, and paper
    TODOs.

- [x] Document run-artifact schema-version boundary before schema fields exist.
  - Status: documented. README, run-artifact docs, and the paper index now
    state that current `manifest.json` and JSONL run streams are evolving local
    machine-readable formats without `schema_version`, `artifact_schema`, or
    record-compatibility markers.
  - Remaining implementation gap: adding schema/version fields, migration
    rules, and legacy compatibility tests remains open in code, roadmap, and
    paper TODOs.

- [x] Record CLI best-artifact export success/failure after completed manifests.
  - Status: implemented and documented. After CLI best export succeeds or
    fails, `manifest.json.runtime.best_artifact_export` records completed or
    failed export status, refreshed `best.py` / `best_workspace` artifact
    records, hashes when available, and bounded/redacted failure diagnostics.
  - Verification: CLI tests cover a real zero-generation run with successful
    best export and a forced `_write_best_artifacts()` failure after core
    evolution completed; the failed run keeps `runtime.status: "completed"`
    while recording `best_artifact_export.status: "failed"`.

- [x] Document and harden linked existing best-artifact handling.
  - Status: implemented and documented. Direct CLI best export now rejects
    symlink or Windows-junction visible, temporary, and backup best-artifact
    paths before replacement or cleanup, and README/run-artifact documentation
    describes that post-run export boundary.
  - Verification: focused CLI tests cover linked `best.py`,
    symlink-capable linked `best_workspace`, Windows-junction
    `best_workspace`, and normal replacement/preservation cases.

- [x] Document and harden best-artifact rollback failure behavior.
  - Status: implemented and documented. Failed best export keeps the original
    export failure as the primary CLI/manifest diagnostic, records
    rollback/cleanup errors as secondary redacted fields, and preserves backup
    paths that could not be restored.
  - Verification: focused CLI tests cover install failure with successful
    rollback, rollback failure with preserved backup diagnostics, cleanup
    failure after successful install, and manifest persistence of structured
    redacted recovery errors.

- [x] Document and harden nested-link behavior during candidate workspace
  materialization cleanup.
  - Status: implemented and documented. Candidate materialization now rejects
    linked roots, linked ancestors, and linked nested entries in existing roots
    before cleanup, and README/run-artifact wording describes that recursive
    link boundary.
  - Verification: focused candidate materialization tests cover nested symlink
    rejection when available, Windows nested-junction rejection, normal stale
    directory replacement, and preservation of the old root on preflight
    failure.

- [x] Soften the prompt-example placeholder-prevention claim.
  - Status: documented. README now describes the concrete diff example as
    reducing observed placeholder-copying mistakes, not preventing them.
  - Remaining implementation gap: there is still no dedicated validator that
    rejects copied placeholder/example payloads before candidate mutation.

- [x] Clarify what "package metadata" means in environment provenance docs.
  - Status: documented. README, run-artifact docs, and development docs now
    name the exact retained pyproject fields: `project.name`,
    `project.version`, `project.requires-python`, `build-system.build-backend`,
    and `build-system.requires`.
  - Remaining scope: license, authors, keywords, classifiers, project URLs,
    optional dependency groups, console scripts, dev/test tools, transitive
    dependencies, and `pip freeze` output remain outside the current
    provenance contract.

- [x] Document current candidate workspace size-limit boundary.
  - Status: documented. README, problem-format docs, and run-artifact docs now
    state that candidate workspaces do not yet enforce file-count, per-file
    character, or total text-size budgets at the workspace model boundary.
  - Remaining implementation gap: code/roadmap/paper TODOs still track real
    configurable workspace budgets or spillover semantics for history, prompt,
    evaluator materialization, and best-workspace export.

- [x] Document and fix CausalPlugin factor exploration behavior.
  - Status: implemented and documented. The causal plugin now uses deterministic
    pull-once initialization across fixed factors before UCB-like scoring, and
    README/plugin docs name the `pull_once_then_ucb1_like` policy.
  - Verification: focused causal plugin tests cover pull-once order, positive
    reward behavior with untried factors, all-factor-observed UCB-like scoring,
    and artifact metadata.

- [x] Document and fix raw evaluator source paths in manifests.
  - Status: implemented and documented. README, architecture, and run-artifact
    docs now describe evaluator source path labels as problem-relative,
    redacted/hash-backed provenance rather than raw absolute paths.
  - Verification: focused evaluator provenance tests prove secret-like default
    and configured-stage validator filenames are redacted from serialized
    records while source hashes and path hashes remain.

- [x] Document evaluator-entrypoint hash size/read limits or fix them first.
  - Status: implemented and documented. Evaluator entrypoint source hashes now
    use a `streamed_full_file` policy with fixed `hash_chunk_bytes` metadata,
    and read failures produce structured redacted `read_error` records instead
    of unstructured provenance failures.
  - Verification: focused evaluator provenance tests cover default and
    configured validators, large validator streaming without `read_bytes()`,
    and configured-stage read-error diagnostics.

- [x] Document or enforce evaluator-result object schema guarantees.
  - Status: enforced and documented. `EvaluationResult` and
    `EvaluationStageResult` now validate finite numeric fields, manifest-safe
    stage names, string diagnostics, JSON-safe finite metrics, and JSON-safe
    metadata during construction and before `to_dict()` persistence.
  - Verification: focused evaluator tests reject direct non-string diagnostics,
    non-finite fitness/elapsed values, non-JSON metadata, and post-construction
    plugin-style result mutations before strict JSON persistence.

- [x] Document or fix causal-plugin behavior under full mutation mode.
  - Status: fixed and documented. `CausalPlugin` now uses the shared
    compact/canonical SEARCH/REPLACE parser for diff-mode mutations and scans
    full-mode replacement payload text directly for the same fixed
    token-pattern factors. README describes both paths and keeps the plugin
    scoped as CausalEvolve-inspired, not scratchpad-complete.
  - Verification: focused causal plugin tests cover full-mode
    `algorithm_choice` and helper-function detection plus mutation-mode
    history metadata.

- [x] Document or enforce the policy for failed explicit context extraction.
  - Status: enforced by default and documented. Files matched by explicit
    `context.yaml` include patterns must extract successfully unless
    `on_explicit_context_failure: warn` is configured; the degraded warning
    path records `explicit_context_failure_count`, matched include patterns,
    skipped-source diagnostics, and failed-extraction counts in
    `context_policy`.
  - Verification: focused loader tests cover invalid text context, mixed
    explicit failures before partial load, corrupt PDFs, no-text PDFs, PDF
    resource-limit failures, and the explicit warning/degraded-context path.

- [x] Document duplicate accepted-id restore semantics.
  - Status: documented as a current inspection and future restore boundary.
    `libreevolve show` rejects duplicate history ids with line-numbered
    diagnostics and first-seen line context. README/run-artifact docs now state
    that no history restore/resume reader exists yet, and any future restore
    path must reject or quarantine duplicate ids before mutating restored
    database/archive state rather than silently repairing or versioning them.
  - Verification: focused CLI tests cover duplicate legacy and current history
    ids before selection.

- [x] Document unsafe accepted-id restore semantics.
  - Status: documented as a current inspection and future restore boundary.
    `libreevolve show` validates every streamed history id with the writer-side
    manifest-safe program-id policy, including selected and unselected rows.
    README/run-artifact docs now require future restore paths to apply the same
    manifest-safe id policy before mutating restored state.
  - Verification: focused CLI tests cover unsafe selected and unselected
    history ids.

- [x] Document runtime RNG-state snapshot persistence.
  - Status: README and run-artifact docs now state that completed and aborted
    manifests include `runtime.rng`, a hash-backed
    `python.random.mt19937.v1` snapshot of the run-local RNG seeded from
    `Config.seed`. The docs explicitly keep resume restore open rather than
    implying full seeded replay.
  - Verification: focused loop tests cover RNG snapshot round-trip equivalence
    and completed/aborted manifest persistence.

- [x] Document checked runtime RNG restore helpers.
  - Status: README and run-artifact docs now name
    `load_runtime_rng_state_snapshot()` and
    `restore_runtime_rng_state_snapshot()` as the checked manifest-reader and
    direct restore boundary for `runtime.rng`. A later slice added direct
    `evolve(..., runtime_rng_state_snapshot=...)` integration; whole-run
    archive/controller resume and plugin/provider RNG boundaries remain open.
  - Verification: focused loop tests cover valid manifest loading and malformed
    RNG snapshots.

- [x] Document checked compact archive-state reader.
  - Status: README, architecture docs, and run-artifact docs now state that
    `load_runtime_archive_state_snapshot()` validates the compact
    `runtime.history.archive_state` manifest snapshot before future resume use,
    while full archive checkpoint restore remains open.
  - Verification: focused database/island tests cover valid and malformed
    compact archive-state snapshots.

- [x] Document checked migration archive-event reader.
  - Status: README, architecture docs, and run-artifact docs now state that
    `load_archive_event_records()` validates `archive_events.jsonl` as a
    checked migration audit stream while full migration replay remains open.
  - Verification: focused database tests cover valid and malformed archive
    event streams.

- [x] Document direct compact island-cursor restore.
  - Status: README, architecture docs, and run-artifact docs now state that
    `IslandModel.restore_cursor_state()` can apply the compact cursor/counter
    subset from `runtime.history.archive_state`, while full archive checkpoint
    restore remains open.
  - Verification: focused island/database/loop tests cover restored cursor
    assignment and invalid snapshot rejection.
- [x] Document provenance path and Git status Unicode-control escaping.
  - Status: README and run-artifact docs now describe `[U+....]` escaping,
    hash-backed raw identity, and unsafe-character flags for source/problem
    paths, skipped path diagnostics, plugin module paths, and Git dirty-status
    entries.
  - Verification: focused provenance tests cover the documented path/status
    behavior.

- [x] Document known-lockfile hash provenance.
  - Status: README, run-artifact docs, architecture docs, and the paper index
    now describe the `lockfiles` environment-provenance section, the known
    project-root lockfile candidate set, hash-only storage, degraded statuses,
    and remaining full-freeze/transitive/numerical/provider provenance gaps.
  - Verification: focused runtime-environment provenance tests cover the
    documented lockfile behavior.

- [x] Document installed-package snapshot provenance.
  - Status: README, run-artifact docs, architecture docs, and the paper index
    now describe the `installed_packages` environment-provenance section as a
    bounded installed distribution name/version snapshot with sanitization,
    capped retention metadata, and full-record aggregate hashing.
  - Verification: focused runtime-environment provenance tests cover the
    documented installed-package snapshot behavior.

- [x] Document fixed MAP-Elites complexity bounds.
  - Evidence: README previously said retained cell/elite candidates could
    still change the in-memory descriptor scale after workspace-aware
    descriptors were added.
  - Status: README now states that serialized-workspace complexity is clamped
    by `map_elites_complexity_max_chars` and that only the diversity dimension
    remains adaptive to the current capped elite list.
  - Remaining README gap: the broader behavior-descriptor and stable diversity
    model gaps remain documented.
  - Verification: focused archive/config tests and manifest persistence tests
    cover the documented behavior.

- [x] Document raw and normalized LLM feedback score semantics.
  - Evidence: README previously described feedback scores as simply bounded to
    `[0, 1]` and directly weighted.
  - Status: README now explains configured score bounds/direction, raw
    feedback metrics, normalized scores, normalized `min_score`, and
    `weighted_delta` composition.
  - Remaining README gap: feedback metrics remain scoped outside MAP-Elites
    `selection_score` and full multi-objective archive policy.
  - Verification: focused feedback/config tests cover the documented behavior.

- [x] Document provider-internal retry controls and telemetry.
  - Evidence: README previously described bundled adapter internal retries as
    hidden three-attempt loops and listed adapter retry counts as missing
    provider provenance.
  - Status: README now describes `provider_max_retries`, the default preserving
    three provider attempts, and `adapter_retry` summaries in LLM call
    telemetry.
  - Remaining README gap: raw provider diagnostics and token/cost budget
    accounting remain future work.
  - Verification: focused backend, ensemble, and config tests cover the
    documented retry knob and telemetry.

- [x] Document normalized provider failure categories.
  - Evidence: README previously said provider failures stored only
    redacted/truncated exception text.
  - Status: README now describes `provider_failure_category` values for
    provider-response, timeout, rate-limit, transport, provider status, and
    unknown failures.
  - Remaining README gap: role-specific quarantine and budget policy remain
    explicitly future work.
  - Verification: focused ensemble tests cover the documented categories.

- [x] Document DeepResearch cache snapshot artifact summaries.
  - Evidence: README described cache snapshots and offline replay but did not
    state that the actual snapshot files are summarized as plugin artifact
    metadata.
  - Status: README now describes DeepResearch cache snapshot counts, byte
    sizes, per-file hashes, retention/skipped counters, and aggregate hashes in
    plugin artifact metadata.
  - Remaining README gap: full provider/source payload persistence, ranked
    source provenance, and source-content trust policy remain future work.
  - Verification: focused DeepResearch plugin and loop tests cover the
    documented manifest behavior.

- [x] Document modular plugin static strategy metadata.
  - Evidence: README said the modular plugin did not log a real
    generate/improve/perturb operation, but it also did not describe a
    manifest-visible static-guidance policy.
  - Status: README now states that modular candidate metadata records
    `operation_selected: static_modular_guidance`, the described operation
    names, and false execution/enforcement flags.
  - Remaining README gap: custom plugin package-registry attribution,
    constructor-schema attribution beyond exposed `__version__` labels, and
    real strategy-operation choices are still future work.
  - Verification: focused modular plugin and loop tests cover the documented
    metadata.

- [x] Document LLM feedback output retention previews.
  - Evidence: README previously warned that feedback grader `raw_response` and
    parsed `feedback` text were persisted verbatim in run history.
  - Status: README now states that those compatibility fields are retained as
    redacted bounded previews, with SHA-256 hashes, original/stored character
    counts, caps, and redaction/truncation flags in companion retention
    metadata.
  - Remaining README gap: broader per-role full/redacted/hash-only/off prompt
    and response logging modes remain future work.
  - Verification: focused feedback tests cover successful and failed retained
    grader output.

- [x] Document built-in plugin specs in prompt-context records.
  - Evidence: README previously described prompt-context identity and metadata,
    while built-in constructor parameters were visible only in
    `runtime.plugin_state.loaded_specs`.
  - Status: README now states that each `metadata.plugin_context[]` record
    includes `plugin_spec`, reusing the manifest-level built-in
    constructor-parameter schema and marking custom direct plugins as
    `custom_plugin_spec_unavailable`.
  - Remaining README gap: custom plugin package-registry attribution and
    constructor-schema attribution beyond exposed `__version__` labels remain
    future work.
  - Verification: focused loop tests cover the documented history metadata.

- [x] Document logical LLM-call budget caps.
  - Evidence: README previously treated LLM budget accounting as future work
    even though run accounting already covered generations, evaluator work, and
    wall-clock limits.
  - Status: README now documents `max_llm_calls` / `--max-llm-calls`, the
    provider-free zero-call dry point, cooperative logical `generate()` call
    caps, persisted consumed `llm_calls`, and optional-role skip/failure
    behavior after exhaustion.
  - Remaining README gap: provider-adapter attempt budgets, token/cost stops,
    accelerator accounting, async worker budgets, and equal-budget benchmark
    reports remain future work.
  - Verification: focused budget/config/loop/CLI tests cover the documented
    behavior.

- [x] Document restored backend-spec validation.
  - Evidence: README and configuration docs described live backend validation
    and scheduler restore, but not the restored backend-spec preflight boundary.
  - Status: README and configuration docs now describe
    `validate_restored_backend_specs()` as the shared restored/replay backend
    spec validator backed by live `build_llm()` normalization.
  - Remaining README gap: full run resume still does not consume restored
    backend specs, and oversized/secret-like prompt policy remains separate
    future work.
  - Verification: focused ensemble tests cover the documented validator.

- [x] Document backend-registry spec validation.
  - Evidence: backend docs described live and restored backend validation, but
    not the new registry-created constructor path.
  - Status: README and backend docs now describe
    `libreevolve.llm.backend_registry`, `validate_backend_registry_specs()`,
    and registry construction through the shared backend normalizer.
  - Remaining README gap: full run resume still does not consume restored
    backend specs, and oversized/secret-like prompt policy remains separate
    future work.
  - Verification: focused ensemble tests cover the documented registry path.

- [x] Document restored LLM prompt validation.
  - Evidence: README and configuration docs described live prompt validation,
    but not the restored/replay prompt preflight helper.
  - Status: README and configuration docs now describe
    `validate_restored_llm_prompt()` as the restored prompt boundary backed by
    live non-empty prompt validation.
  - Remaining README gap: oversized and secret-like prompt policy remains
    future work.
  - Verification: focused ensemble tests cover the documented helper.

- [x] Document NumPy numerical-runtime provenance.
  - Evidence: README/run-artifact docs described package and lockfile
    environment provenance while still saying numerical backend/BLAS records
    were absent.
  - Status: README and run-artifact docs now describe
    `numerical_runtime.numpy` as a NumPy version plus bounded/redacted
    `show_config()` preview and full captured-config hash.
  - Remaining README gap: complete freeze interpretation, broader build
    provenance, accelerator, private package-source, live provider
    service/API-version capture, and provider cost or remote provider-side default capture
    remain future work.
  - Verification: focused provenance tests cover the documented field.

- [x] Document selected PEP 621 package metadata provenance.
  - Evidence: README/run-artifact docs previously said license, authors,
    classifiers, project URLs, optional dependency groups, and console scripts
    were not captured.
  - Status: README and run-artifact docs now describe those selected PEP 621
    fields as retained bounded/redacted package metadata.
  - Remaining README gap: freeze install-source interpretation, wheel/build
    tags, accelerator metadata, non-project build metadata policy, and
    package-source redaction remain future work.
  - Verification: focused provenance tests cover the documented metadata.

- [x] Document built-in plugin registry specs and core plugin resolution.
  - Evidence: README and plugin docs still said direct `evolve()` did not
    resolve `Config.plugins`, and configuration docs still described plugins as
    name-only CLI aliases.
  - Status: README, plugin docs, configuration docs, run-artifact docs, and
    architecture docs now describe built-in `{name, options}` plugin specs,
    pre-overwrite schema validation, and core resolution when explicit plugin
    objects are omitted.
  - Remaining README gap: custom plugin entry-point discovery, package/version
    attribution, and arbitrary custom schema policy remain future work.
  - Verification: focused config, CLI, and loop tests cover the documented
    behavior.

- [x] Document keyword and arbitrary entry-point environment provenance.
  - Evidence: README/run-artifact docs still described keyword and arbitrary
    entry-point metadata as missing after selected PEP 621 metadata capture.
  - Status: README, run-artifact docs, and development docs now describe
    `keywords` and arbitrary `[project.entry-points]` groups as retained
    bounded/redacted package metadata.
  - Remaining README gap: freeze install-source interpretation, wheel/build
    tags, accelerator metadata, non-project build metadata policy, and
    package-source redaction remain future work.
  - Verification: focused provenance tests cover the documented metadata.

- [x] Document ensemble-level LLM call timeout policy.
  - Evidence: README/config/backend docs still said provider calls had no
    LibreEvolve timeout beyond built-in provider SDK request settings.
  - Status: README, backend docs, and configuration docs now describe
    `llm_call_timeout_sec` as an ensemble deadline that records structured
    timeout telemetry and can retry/fall back, while leaving remaining-run
    deadline propagation and hard cancellation open.
  - Remaining README gap: runtime-budget propagation and role-specific
    timeout/quarantine policy remain future work.
  - Verification: focused ensemble, config, and CLI tests cover the documented
    behavior.

- [x] Document bounded `pip freeze` environment provenance.
  - Evidence: README and run-artifact docs still described environment
    provenance as lacking any `pip freeze` install-source/options evidence.
  - Status: README and run-artifact docs now describe `pip_freeze` as a
    bounded, redacted `python -m pip freeze --all` snapshot with retained line
    hashes, raw stdout hash, and degraded timeout/error statuses.
  - Remaining README gap: broader build provenance, accelerator/runtime-driver
    state, live provider service/API versions, provider cost or remote provider-side default
    capture, non-project build metadata policy, and private package-source
    interpretation policy remain future work.
  - Verification: focused provenance tests cover the documented freeze record.

- [x] Document installed-distribution `WHEEL` metadata provenance.
  - Evidence: README and run-artifact docs still described environment
    provenance as lacking wheel/build tag evidence after bounded freeze capture.
  - Status: README and run-artifact docs now describe `installed_packages` as
    retaining parsed `WHEEL` metadata, including wheel versions, generators,
    `Root-Is-Purelib`, bounded tags, oversized metadata skips, hashes, and
    redaction metadata.
  - Remaining README gap: broader build provenance, accelerator/runtime-driver
    state, live provider service/API versions, provider cost or remote provider-side default
    capture, non-project build metadata policy, and private package-source
    interpretation policy remain future work.
  - Verification: focused provenance tests cover the documented wheel metadata
    record, including tag and raw metadata size bounds.

- [x] Document built-in LLM provider SDK version provenance.
  - Evidence: README and run-artifact docs still scoped environment provenance
    as lacking provider/API-version evidence after package, freeze, NumPy, and
    wheel metadata capture.
  - Status: README, run-artifact docs, architecture docs, and paper index now
    describe `llm_provider_sdks` as built-in OpenAI, Anthropic, and Ollama SDK
    version evidence with adapter module/API-mode labels and degraded
    missing/lookup-error statuses.
  - Remaining README gap: live provider service/API versions, provider
    cost or remote provider-side default capture, provider-side authentication state, and
    provider nondeterminism/replay policy remain future work.
  - Verification: focused provenance tests cover the documented provider SDK
    record.

- [x] Document bounded extra `[project]` metadata provenance.
  - Evidence: README/run-artifact docs still said arbitrary project metadata
    was not captured after selected PEP 621 metadata, freeze, wheel, and SDK
    provenance work.
  - Status: README, run-artifact docs, architecture docs, and paper index now
    describe `extra_project_metadata` as bounded/redacted/hash-backed records
    for unselected or unknown `[project]` keys.
  - Remaining README gap: broader non-project build provenance,
    accelerator budget/accounting state, private package-source interpretation,
    live provider service/API versions, and provider cost or remote provider-side default
    capture remain future work.
  - Verification: focused provenance tests cover the documented extra
    metadata record.

- [x] Document CLI runtime RNG snapshot restore.
  - Evidence: user docs still described direct `evolve()` RNG restore but left
    the CLI run path unstated or stale.
  - Status: README, configuration, run-artifact, architecture, roadmap, and
    paper-index docs now state that CLI runs can use
    `--restore-rng-from-manifest` to load a checked `runtime.rng` snapshot
    before run-directory preparation.
  - Remaining README gap: this remains framework-RNG-only, not full run
    resume or provider/plugin nondeterminism capture.
  - Verification: focused CLI tests cover the documented option.

- [x] Document oversized and secret-like ensemble prompt policy.
  - Evidence: README/backend/configuration docs still described prompt
    validation and output caps without defining the prompt-input cap or
    secret-like prompt treatment for registry/custom backend calls.
  - Status: README, backend, configuration, architecture, and run-artifact docs
    now state that `prompt_max_chars` is enforced at the ensemble boundary and
    that raw prompt text is not retained in LLM call telemetry.
  - Remaining README gap: provider token-window accounting and section-priority
    prompt packing remain open.
  - Verification: focused ensemble tests cover the documented boundary.

- [x] Document bounded accelerator runtime provenance.
  - Evidence: README and run-artifact docs still described environment
    provenance as lacking accelerator/runtime-driver evidence.
  - Status: README, run-artifact docs, architecture docs, and the paper index
    now describe `accelerator_runtime` as bounded CUDA/NVIDIA/ROCm/HIP/oneAPI/
    SYCL/DirectML environment hints plus degraded `nvidia-smi`/`rocm-smi`
    probe records.
  - Remaining README gap: this is still not accelerator budget accounting,
    full build provenance, live provider service/API-version capture, provider
    cost or remote provider-side default capture, or complete private package-source
    interpretation.
  - Verification: docs checks and focused provenance tests cover the documented
    manifest section.

- [x] Document local adapter default-parameter telemetry.
  - Evidence: README/backend/run-artifact docs described request parameters and
    client context but did not state that local adapter generation defaults are
    retained in call telemetry.
  - Status: README, backend docs, architecture docs, run-artifact docs, and the
    paper index now describe `backend_defaults` as LibreEvolve's effective
    local output-token cap, provider internal retry cap, configured request
    timeout or `null`, API mode, and OpenAI reasoning/API-mode policy.
  - Remaining README gap: remote provider-side defaults, provider pricing/cost
    accounting, token/cost stop policy, and raw provider diagnostics remain
    open.
  - Verification: focused backend/ensemble tests and docs checks cover the
    documented telemetry field.

- [x] Document configurable reward-accounted LLM roles.
  - Evidence: README, backend, configuration, architecture, run-artifact, and
    paper-index docs still framed reward accounting as fixed mutation-only or
    did not name the persisted reward policy.
  - Status: docs now describe `llm_reward_accounted_roles`, the default
    `["mutation"]` policy, telemetry-only behavior for unlisted roles, and the
    scheduler/runtime `reward_accounting_policy` audit snapshot.
  - Remaining README gap: per-role scheduler state, quotas, token/cost budget
    enforcement, provider-cost accounting, default non-mutation reward
    signals, and automatic scheduler-state resume remain open.
  - Verification: focused docs scans and config/ensemble/loop tests cover the
    documented behavior.

- [x] Document critique/meta-prompt provider-failure isolation.
  - Evidence: README/backend/configuration/architecture docs still said
    exhausted auxiliary provider failures could abort the active role after
    useful work had completed.
  - Status: docs now state that mutation failures can still abort before
    candidate/evaluation logging, while exhausted critique calls fall back to
    the original mutation, feedback graders use their configured failure
    policy, and exhausted meta-prompt calls record rejected prompt mutations.
  - Remaining README gap: role-specific quarantine, provider penalties,
    token/cost budget stops, and unified retry-budget consumption remain open.
  - Verification: focused loop tests cover the documented critique and
    meta-prompt failure paths.

- [x] Document metric source labels and objective feedback metrics.
  - Evidence: README and problem/configuration docs described declared metrics
    and LLM feedback metrics separately, without explaining when feedback
    metrics can be objective-schema metrics.
  - Status: README, configuration, problem-format, architecture, plugin, and
    run-artifact docs now state that problem metrics default to
    `source: evaluator`, non-primary metrics can declare `source: feedback`
    or `source: plugin`, validators must not return those sourced names,
    `objective_metric: true` graders can fill feedback-sourced metrics, and
    plugin hooks can fill plugin-sourced metrics for normalization and archive
    `selection_score`.
  - Remaining README gap: Pareto/frontier archive replacement and
    lineage-aware resurfacing remain open.
  - Verification: docs scans plus focused loader/evaluator/feedback/config/loop
    tests cover the documented behavior.

- [x] Document prompt-visible validator diagnostics.
  - Evidence: README, architecture, run-artifact, and paper docs still treated
    aggregate syntax diagnostics and fuller validator metadata as prompt
    rendering gaps.
  - Status: docs now state that prompt feedback renders bounded aggregate
    syntax diagnostics, metric-bound clamp diagnostics, malformed metric
    diagnostics, and sample aggregation counts/policies, with diagnostic text
    escaped as JSON after redaction/truncation.
  - Remaining README gap: artifact-content retrieval, full validator metadata,
    and token-aware section-priority packing remain open.
  - Verification: focused prompt tests cover the documented diagnostic
    rendering behavior.

- [x] Document custom plugin signature-only provenance.
  - Evidence: README, plugin docs, run-artifact docs, and configuration docs
    still said custom direct plugins were marked
    `custom_plugin_spec_unavailable` or that arbitrary custom constructor
    introspection remained entirely open.
  - Status: docs now state that custom direct plugins record constructor
    signature shape only, with parameter names/kinds/flags and no constructor
    values or instance attributes. Remaining custom-plugin provenance gaps are
    package registry/entry-point discovery and value/schema capture beyond the
    safe signature summary.
  - Verification: focused loop tests cover the signature-only manifest and
    prompt-context records.

- [x] Document matrix-result publication metadata separately from the smoke
      example.
  - Evidence: README described the paper manifest and Appendix B registry but
    did not document the matrix-result report contract or clearly separate it
    from the checked-in 2x2 matrix smoke fixture.
  - Status: README now states that `libreevolve.matrix_result_report.v1`
    validates matrix target identity, dimensions, seed count, best rank, hit
    fraction, exactness certificate status, coefficient domain, and artifact
    path/hash metadata. It also states that the checked-in
    `matrix_multiplication` example remains smoke-only until a real
    tensor-decomposition suite emits reports in that schema.
  - Verification: docs scan confirms the README names the schema and keeps the
    tensor-suite gap explicit.

- [x] Document paper-result certification metadata separately from local
      validators.
  - Evidence: README did not describe any benchmark certification record that
    separates local evaluator acceptance from paper-level result confirmation.
  - Status: README now names `libreevolve.paper_result_certification.v1`,
    describes its claim scope, verifier identity/independence, verdict, passed
    evidence, and hashed artifact requirements, and states that the contract
    does not run independent verifiers or create deployment/reviewer evidence.
  - Verification: focused certification tests cover the documented readiness
    boundary and docs scan confirms the schema is named.

- [x] Document systems benchmark held-out/reference report metadata.
  - Evidence: README did not document a systems-benchmark report contract for
    separating optimization feedback from held-out/generalization and
    reference-correctness evidence.
  - Status: README now names `libreevolve.systems_result_report.v1`, describes
    required optimization, held-out, and reference-correctness gates, case-set
    hashes, sample counts/seeds, finite metrics, artifacts, not-applicable
    rationale, and the boundary that this is not a real systems benchmark
    implementation.
  - Verification: focused systems-result tests cover the documented readiness
    gate and docs scan confirms the schema is named.

- [x] Document benchmark anti-gaming hardening metadata.
  - Evidence: README described specific matrix smoke-validator shortcut
    rejections but not a reusable hardening contract for advertised benchmark
    readiness.
  - Status: README now names `libreevolve.benchmark_hardening.v1`, describes
    protected signals, shortcut categories, detector strategy, passed negative
    fixtures, hashed hardening artifacts, and the distinction between smoke
    records and benchmark/paper-claim records.
  - Verification: focused hardening tests cover the documented readiness
    boundary and docs scan confirms the schema is named.

- [x] Document executed equal-budget ablation result metadata.
  - Evidence: README documented the AlphaEvolve ablation registry definition
    but not the executed-result report shape for equal-budget curves.
  - Status: README now names `libreevolve.alphaevolve_ablation_report.v1`,
    describes all six Figure 8 variants, target/seed/fraction coverage,
    finite scores, consumed-budget consistency, passed component assertions,
    hashed curve artifacts, and the boundary that the contract does not run
    ablations or implement token/cost/accelerator budget stops.
  - Verification: focused ablation-result tests cover the documented contract
    and docs scan confirms the schema is named.

- [x] Document paper-facing LLM role/retry budget report metadata.
  - Evidence: README documented runtime LLM accounting summaries but not a
    standalone report contract for paper-level role and provider-internal retry
    budget audits.
  - Status: README now names `libreevolve.llm_budget_report.v1`, describes
    per-role logical-call, retry-attempt, adapter-attempt, token, cost, and
    wall-clock limits/usage, provider-internal retry caps, persisted
    resume-state hashes, and the boundary that the contract is not runtime
    enforcement.
  - Verification: focused LLM budget report tests cover the documented
    readiness boundary and docs scan confirms the schema is named.

- [x] Document provider timeout/cancellation policy metadata.
  - Evidence: README described request timeouts and ensemble wait deadlines but
    did not document a reusable policy contract for timeout/cancellation
    budget actions and evidence.
  - Status: README now names `libreevolve.provider_cancellation_policy.v1`,
    describes role-scoped timeout/cancellation rules, budget actions,
    hard-cancel readiness, artifact requirements, hashed cancellation
    artifacts, and the boundary that this is not live SDK cancellation
    enforcement.
  - Verification: focused cancellation-policy tests cover the documented
    readiness boundary and docs scan confirms the schema is named.

- [x] Document retained provider retry evidence in LLM budget reports.
  - Evidence: README documented the LLM budget report contract but did not say
    runtime manifest instances attach retained per-call provider retry details.
  - Status: README now states that runtime `llm_budget_report` records are
    self-validated from observed role accounting and include retained per-call
    provider retry details from LLM call history when available.
  - Verification: focused loop and budget-report tests cover the documented
    runtime report behavior.

- [x] Document installed-package source/install metadata.
  - Evidence: README described installed package provenance as name/version plus
    `WHEEL` metadata and did not mention source/install records.
  - Status: README now says `installed_packages` includes redacted/hash-backed
    `direct_url.json`, `INSTALLER`, and hash-only `RECORD` metadata alongside
    WHEEL tags and package names/versions.
  - Verification: focused provenance tests cover the documented metadata
    fields and source-policy retention wording.

- [x] Document archive-admission objective vectors.
  - Evidence: README described normalized metrics and scalar selection scores
    but did not state that archive decisions preserve the underlying objective
    vector.
  - Status: README now documents `metadata.archive_admission.objective_vector`
    and matching migration-row objective vectors as finite normalized metric
    and selection-policy audit records. README and run-artifact docs now also
    state that `show` validates and prints bounded selected-row objective-vector
    summaries.
  - Verification: focused loop/database/island/CLI tests cover the documented
    objective-vector evidence, selected `show` display, bounded summaries, and
    malformed unselected row rejection.

- [x] Document feedback scheduler reward semantics.
  - Evidence: README and configuration docs described configurable
    `llm_reward_accounted_roles` but did not document a concrete non-mutation
    reward signal for feedback graders.
  - Status: README and configuration docs now state that exact
    `feedback:<name>` roles can be reward-accounted and that successful
    feedback graders use their normalized score as the scheduler reward, while
    telemetry-only feedback records keep `scheduler_reward.applied: false`.
  - Verification: focused feedback tests cover the documented behavior.

- [x] Document active DeepResearch retrieval-context provenance links.
  - Evidence: README and plugin docs described active DeepResearch context only
    as source generation plus synthesis hash, while the implementation now
    exposes a richer compact provenance link.
  - Status: README, plugin docs, paper index, and TODO ledgers now describe
    `libreevolve.deep_research_active_context.v1` with event index,
    synthesis/raw-result hashes, query hash, cache fields, retained-source
    ranking hash fields, and transport-policy status.
  - Verification: focused DeepResearch and loop tests cover the documented
    active-context metadata and raw-URL omission.

- [x] Document bounded DeepResearch source-content snapshots.
  - Evidence: README, plugin docs, and the paper index still described
    source-content snapshots as fully missing even though retained source rows
    can now preserve bounded/redacted content.
  - Status: docs now describe
    `libreevolve.retrieval_source_content_snapshot.v1` snapshots with
    bounded/redacted source content, raw/stored hashes, and
    redaction/truncation metadata. Remaining docs scope the gap to full
    provider payloads, unbounded source artifacts, semantic ranking, and trust
    verification.
  - Verification: focused DeepResearch and loop tests cover the documented
    source snapshot fields.

- [x] Document DeepResearch query-overlap source relevance scores.
  - Evidence: README/plugin docs and the paper index still scoped all
    retrieval ranking beyond provider order as missing.
  - Status: docs now describe audit-only `query_term_overlap_audit_v1`
    relevance scores, the `source_ranking` score hash, and the fact that these
    scores do not reorder retained sources. Remaining docs scope the gap to
    learned/external semantic ranking and fuller query grounding.
  - Verification: focused DeepResearch and loop tests cover the documented
    score metadata.

- [x] Document task/context-aware DeepResearch queries.
  - Evidence: README, plugin docs, and the paper index described DeepResearch
    queries as code/metric-only and listed task descriptions or explicit
    context as missing.
  - Status: docs now state that default DeepResearch queries include bounded
    task-description and explicit-context terms. Remaining query-grounding
    limitations are scoped to local paper corpora and hypothesis templates
    after the later failure-history grounding slice.
  - Verification: focused DeepResearch and loop tests cover the documented
    query-input fields.

- [x] Document failure-history-aware DeepResearch queries.
  - Evidence: docs still listed failure history as missing from DeepResearch
    query grounding.
  - Status: README, plugin docs, paper status, and TODOs now state that later
    DeepResearch queries include bounded recent failure-history terms, while
    local paper and hypothesis grounding remain open.
  - Verification: focused DeepResearch and loop tests cover the documented
    failure query metadata.

- [x] Document local-paper-aware DeepResearch queries.
  - Evidence: README, plugin docs, paper status, and TODOs still listed local
    paper corpus query grounding as missing.
  - Status: docs now state that default DeepResearch queries include bounded
    local paper manifest title/id terms, while hypothesis query grounding and
    stronger semantic ranking/payload persistence remain open.
  - Verification: focused DeepResearch, loop, and database tests cover the
    documented local-paper query metadata.

- [x] Document hypothesis-aware DeepResearch queries.
  - Evidence: README, plugin docs, paper status, and TODOs still listed
    hypothesis query grounding as missing.
  - Status: docs now state that later DeepResearch queries include bounded
    terms from recent captured proposal hypotheses, while full
    hypothesis-refinement/debug loops and stronger semantic ranking/payload
    persistence remain open.
  - Verification: focused DeepResearch, loop, and database tests cover the
    documented hypothesis query metadata.

- [x] Document bounded DeepResearch provider-result snapshots.
  - Evidence: docs still described DeepResearch as lacking provider payload
    artifacts without distinguishing bounded redacted snapshots from unbounded
    full payload persistence.
  - Status: README, plugin docs, run-artifact docs, paper status, and TODOs now
    state that retrieval events and cache snapshots retain bounded/redacted
    provider-result snapshots and that plugin artifact summaries report their
    counts/hashes.
  - Verification: focused DeepResearch and loop tests cover the documented
    provider-result snapshot metadata.

- [x] Document declared entry-point plugin constructor schemas.
  - Evidence: README and plugin/configuration docs previously described
    entry-point `constructor_options` only as manifest-safe JSON values, leaving
    external-plugin schema enforcement as future work.
  - Status: README, `docs/plugins.md`, and `docs/configuration.md` now document
    `libreevolve_constructor_option_schema`, supported schema types,
    `required: true`, and manifest-visible declared schema/policy retention.
  - Remaining documentation gap: direct custom plugin objects still have
    signature-only provenance, not captured constructor values or schemas.
  - Verification: focused CLI/plugin registry and loop provenance tests cover
    the documented schema behavior.

- [x] Document role-scoped provider-timeout policy rules.
  - Evidence: README and run-artifact docs described the provider cancellation
    policy contract but not that runtime timeout rules are now scoped to the
    LLM roles used by the loop.
  - Status: README and `docs/run-artifacts.md` now state that runtime manifests
    scope provider-request-timeout and ensemble-deadline rules to `mutation`,
    `critique`, `feedback:*`, and `meta_prompt`.
  - Remaining documentation gap: the docs still correctly state that hard
    provider cancellation and timeout-driven stop/quarantine enforcement are
    not implemented.
  - Verification: focused cancellation-policy and loop manifest tests cover
    role-prefix validation and manifest rule scope.

- [x] Document lineage sampling and cursor provenance.
  - Evidence: README, configuration, architecture, and run-artifact docs needed
    to track the new `lineage` parent/inspiration strategy instead of listing
    only metric/frontier/novelty/recency sampling surfaces.
  - Status: docs now describe lineage as best-per-root retained sampling,
    lineage-root provenance in parent/inspiration metadata, and persisted
    `lineage_sample_index` in archive-state snapshots.
  - Remaining documentation gap: docs still correctly mark durable queryable
    lineage-index resurfacing as open.
  - Verification: docs tests check the sampling strategy list and runtime
    artifact docs are covered by focused test runs.

- [x] Document lineage-index runtime history.
  - Evidence: README, architecture, run-artifact, and todo docs needed to track
    that lineage now has a bounded manifest-visible index instead of only live
    sampling metadata.
  - Status: docs now describe `runtime.history.lineage_index`, the best-valid
    grouped-by-root policy, retained record fields, and its diagnostic-only
    limitations.
  - Remaining documentation gap: docs still correctly distinguish this from a
    full persisted database/replay engine.
  - Verification: focused docs and loop tests cover the new manifest field.

- [x] Document descriptor-index runtime history.
  - Evidence: README, architecture, run-artifact, and todo docs needed to track
    that finite archive-admission descriptor values now have a bounded
    manifest-visible index.
  - Status: docs now describe `runtime.history.descriptor_index`, retained
    descriptor record fields, and the insertion-time coordinate/replay
    limitation.
  - Remaining documentation gap: docs still correctly distinguish this from
    stable descriptor replay or a full persisted database.
  - Verification: focused database and loop tests cover the new manifest field.

- [x] Document feedback-index runtime history.
  - Evidence: README, architecture, run-artifact, and todo docs needed to track
    that LLM feedback records now have a bounded manifest-visible index.
  - Status: docs now describe `runtime.history.feedback_index`, retained
    feedback fields, retention summaries, bounded text evidence, and the
    diagnostic-only limitation.
  - Remaining documentation gap: docs still correctly distinguish this from
    feedback embeddings, full-text ranking, or replayable sampling.
  - Verification: focused database and loop tests cover the new manifest field.

- [x] Document score-index runtime history.
  - Evidence: README, architecture, run-artifact, and todo docs needed to track
    that ranked selection-score evidence now has a bounded manifest-visible
    view.
  - Status: docs now describe `runtime.history.score_index`, retained score
    record fields, and the diagnostic-only limitation.
  - Remaining documentation gap: docs still correctly distinguish this from a
    full database/replay behavior.
  - Verification: focused database and loop tests cover the new manifest field.

- [x] Document timeout quarantine policy evidence.
  - Evidence: backend, configuration, architecture, run-artifact, and todo docs
    needed to stop describing role/backend quarantine as wholly future work.
  - Status: docs now state that configured
    `llm_role_failure_quarantine_after` thresholds apply to exhausted timeout
    failures and are exposed by runtime cancellation-policy manifests.
  - Remaining documentation gap: docs still distinguish this from hard SDK
    cancellation and timeout-specific stop policies.
  - Verification: focused loop tests cover the manifest policy evidence.

- [x] Document archive-event replay audit.
  - Evidence: README, architecture, run-artifact, and todo docs needed to
    distinguish the new audit-only migration replay evidence from full archive
    restore behavior.
  - Status: docs now describe
    `runtime.history.archive_event_replay_audit`, its comparison against
    `archive_contents`, and its audit-only limitation.
  - Remaining documentation gap: docs still correctly leave full migration
    event restore and controller/pending-work replay open.
  - Verification: focused database and loop tests cover the manifest field.

- [x] Document terminal controller state.
  - Evidence: README, architecture, configuration, run-artifact, and todo docs
    needed to distinguish terminal synchronous drained-state evidence from
    async controller queue restore.
  - Status: docs now describe `runtime.history.controller_state`, its
    pending-work counters, controller-budget event-stream summary, and terminal
    resume scope.
  - Remaining documentation gap: docs still leave async queues, mid-generation
    resume, and provider-output replay open.
  - Verification: focused loop tests cover the manifest field.

- [x] Document programmatic representation-boundary evidence.
  - Evidence: README and run-artifact docs needed to distinguish executable
    code candidates from natural-language proposal metadata before making
    AI-Co-Scientist comparison claims.
  - Status: docs now describe
    `runtime.history.programmatic_representation_boundary_report`, generated
    executable-code candidates, proposal metadata as context rather than
    candidate representation, and declared evaluator metrics as programmatic
    criteria.
  - Remaining documentation gap: docs still leave hallucination measurement,
    long-horizon proof, and natural-language hypothesis bridge contracts open.
  - Verification: focused loop tests cover the manifest field and validator.

- [x] Document mutation-operator boundary evidence.
  - Evidence: README and run-artifact docs needed to separate fixed local edit
    grammar support from AlphaEvolve-style claims about replacing handwritten
    mutation/crossover operator sets.
  - Status: docs now describe
    `runtime.history.mutation_operator_boundary_report`, observed payload
    surfaces, fixed parser policy, and sample generated-candidate mutation
    records.
  - Remaining documentation gap: docs still leave operator-family provenance,
    adaptive selection, scoring, and benchmark telemetry open.
  - Verification: focused loop tests cover the manifest field and validator.

- [x] Document exact proposal-diversity evidence.
  - Evidence: README and run-artifact docs needed to distinguish exact
    duplicate proposal telemetry from semantic creative-generation claims.
  - Status: docs now describe `runtime.history.proposal_diversity_report`,
    exact proposal and idea hash uniqueness/duplicate counts, generation and
    batch summaries, and the exact-text-only analysis policy.
  - Remaining documentation gap: docs still leave near-duplicate detection,
    semantic novelty, model-quality attribution, and benchmark linkage open.
  - Verification: focused loop tests cover the manifest field and validator.

- [x] Document initial-pool divergence evidence.
  - Evidence: README needed to distinguish seed-vs-generated workspace/text/
    metric distance from AlphaEvolve-style functional discovery-distance
    claims.
  - Status: docs now describe
    `runtime.history.initial_pool_divergence_report`, canonical workspace hash
    comparisons, bounded primary-file text distance, changed-component
    summaries, and numeric metric L1 distance over shared metric names.
  - Remaining documentation gap: docs still leave task-specific functional
    artifacts, behavior/output-distance metrics, substantially-different
    thresholds, and benchmark telemetry open.
  - Verification: focused loop tests cover the manifest field and validator.

- [x] Document run-local duplicate-work cache evidence.
  - Evidence: README needed to distinguish current exact-workspace
    evaluator-result reuse from durable AlphaEvolve-grade database memory.
  - Status: docs now describe
    `runtime.history.duplicate_work_policy_report`, run-local canonical
    workspace plus evaluator-contract cache keys, cache-hit controller events,
    and evaluator-call budget savings.
  - Remaining documentation gap: durable cross-run cache storage,
    resume-spanning replay, semantic near-duplicate handling, stochastic
    re-evaluation policy, and source/output-aware indexes remain open.
  - Verification: focused budget and loop tests cover the manifest field,
    cache-hit event validation, and duplicate-work report counts.

- [x] Document bounded proposal-score evidence.
  - Evidence: README needed to distinguish current outcome/exact-novelty
    proposal scores from semantic or cross-run idea memory.
  - Status: docs now describe `runtime.history.proposal_score_report`,
    candidate-outcome quality, exact proposal-signature novelty, and the
    remaining calibrated/semantic/cross-run gaps.
  - Remaining documentation gap: semantic proposal retrieval, calibrated
    proposal-quality models, cross-run proposal tables, and score-driven
    prompt/archive policies remain open.
  - Verification: focused loop tests cover the manifest field and validator.

- [x] Document observed controller redirect evidence.
  - Evidence: README needed to distinguish branch-level rejection and observed
    fallback-parent redirects from explicit AlphaEvolve-style controller
    backtracking.
  - Status: README now describes
    `runtime.history.controller_backtracking_report`, branch state transitions,
    observed fallback-parent or alternative-branch redirects, and the lack of
    causal controller proof.
  - Remaining documentation gap: explicit suppression/retry policies,
    fallback-target decision events, resumed-search replay, and cross-run
    branch tables remain open.
  - Verification: focused loop tests cover the manifest field and validator.

- [x] Document prompt-current binding evidence.
  - Evidence: README needed to distinguish separate parent/prompt/history
    fields from a single current-run mutation-attempt binding report.
  - Status: README now describes
    `runtime.history.prompt_current_binding_report`, prompt/current-program
    hashes, parent/candidate workspace hashes, LLM call ids, diff SEARCH
    match counts/spans, evolve-block inner span mapping, workspace
    file-section target/full-file spans, full-mode target spans,
    prompt-history row joins, evaluator links, and archive admission.
  - Remaining documentation gap: none for this bounded README wording slice.
  - Verification: focused loop tests cover the manifest field and validator.

- [x] Document built-in prompt example-copy diagnostics.
  - Evidence: README needed to replace the stale statement that no
    placeholder/example-copy diagnostic exists.
  - Status: README now describes
    `runtime.history.prompt_example_copy_report`, built-in example-sentinel
    inventory, exact generated-payload copy diagnostics, and the remaining
    hard-rejection/semantic/custom-template gaps.
  - Remaining documentation gap: configurable acceptance policy,
    semantic/renamed copy detection, custom prompt-template inventories, and
    per-file-section normalized scanning remain open.
  - Verification: focused loop tests cover the manifest field and validator.
- [x] Keep README implementation-status wording scoped until table semantics
      are validated.
  - Spec evidence: README sends readers to `papers/README.md` for
    paper-facing titles, implementation status, and benchmark coverage because
    manifest titles are display slugs.
  - Status: README now says paper-index validation covers implementation-
    status table shape, role/status taxonomy compatibility, and local artifact
    paths named in status cells against linked active or completed TODO
    evidence. It explicitly scopes the claim to structural traceability and
    local-artifact claim linkage rather than arbitrary natural-language proof
    for every long status phrase or benchmark qualifier.
  - Verification: `py -3.12 -m pytest tests/test_paper_manifest.py -q`
    reports 123 passed.
- [x] Document the paper-artifact availability boundary in README.
  - Spec evidence: README needs to distinguish paper-attributed figure/Colab
    contributor roles from concrete rendered or notebook artifact availability.
  - Status: README now describes
    `libreevolve.alphaevolve_paper_artifact_linkage.v1`, including the current
    `not_yet_linked` status for paper figures and the companion notebook plus
    the digest/source-map fields required before concrete artifact claims.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.
- [x] Document the local Appendix A matrix resource-frontier absence boundary
      in README.
  - Spec evidence: README should separate paper-source OOM/resource-frontier
    evidence from local larger-target matrix scaling claims.
  - Status: README now names
    `libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1` and
    states that no local larger-target attempts, measured GPU memory profiles,
    OOM diagnostics, reduced-seed tradeoffs, or attempted-versus-excluded
    target policies have been recorded yet.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix near-integrality runtime boundary in README.
  - Spec evidence: README matrix wording needs to separate Section 3.1
    near-integral prompt/rounding evidence from actual local runner emission.
  - Status: README now names
    `libreevolve.matrix_near_integrality_runtime_boundary.v1`, scopes it to
    the current `not_emitted_by_local_runner` state, and lists the required
    future emitted-record fields for prompt hashes, coefficients,
    exactness-certificate links, matrix-result refs, artifact paths, and
    artifact hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix scalar-field runtime boundary in README.
  - Spec evidence: README matrix wording needs to separate declared
    scalar-field evidence validation from actual local runner emission for
    complex-valued and characteristic-specific claims.
  - Status: README now names
    `libreevolve.matrix_scalar_field_runtime_boundary.v1`, scopes it to the
    current `not_emitted_by_local_runner` state, and lists the required future
    emitted-record fields for scalar field, characteristic, applicability,
    coefficient representation, algorithm refs, certificate refs,
    matrix-result refs, artifact paths, and artifact hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix tensor-rank runtime boundary in README.
  - Spec evidence: README matrix wording needs to separate declared
    tensor-rank evidence validation from actual local runner emission for
    recursive-applicability and non-tensor caveat claims.
  - Status: README now names
    `libreevolve.matrix_tensor_rank_runtime_boundary.v1`, scopes it to the
    current `not_emitted_by_local_runner` state, and lists required future
    emitted-record fields for algorithm kind, rank, recursive applicability,
    certificate scope, tensor-identity status, target-tensor refs,
    exactness-certificate refs, matrix-result refs, artifact paths, and
    artifact hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix sweep-space runtime boundary in README.
  - Spec evidence: README matrix wording needs to separate declared
    sweep-space evidence validation from actual local runner emission for
    Figure 9-style `sweep()` program provenance.
  - Status: README now names
    `libreevolve.matrix_sweep_space_runtime_boundary.v1`, scopes it to the
    current `not_emitted_by_local_runner` state, and lists required future
    emitted-record fields for search-program refs, sweep function identity,
    hyper-library and hyperparameter declarations, sampled configurations,
    winning configuration, certificate/decomposition refs, matrix-result refs,
    artifact paths, and artifact hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix headline historicity runtime boundary in README.
  - Spec evidence: README matrix wording needs to separate declared headline
    historicity evidence validation from actual local runner emission for the
    4x4 complex rank-48 first-improvement claim.
  - Status: README now names
    `libreevolve.matrix_headline_historicity_runtime_boundary.v1`, scopes it
    to the current `not_emitted_by_local_runner` state, and lists required
    future emitted-record fields for headline target/rank/field values, source
    refs, prior comparisons, evidence links, matrix-result refs, artifact
    paths, and artifact hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix-rank table artifact boundary in README.
  - Spec evidence: README matrix wording needs to separate declared Table 2/
    Appendix A Table 3 exhibit validation from actual local report/export
    emission of rendered table, OCR, and source-excerpt artifacts.
  - Status: README now names
    `libreevolve.alphaevolve_matrix_rank_table_artifact_boundary.v1`, scopes it
    to the current `not_emitted_by_local_report_export` state, and lists
    required future emitted-artifact fields for table ids, source page/caption
    locations, rendered table files, OCR text, source excerpts, artifact
    paths/hashes, and nested matrix-rank table exhibit evidence.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix subset-scope artifact boundary in README.
  - Spec evidence: README matrix wording needs to separate declared named
    subset validation from actual local report/export emission of
    subset-scope artifacts for `appendix_a_full`, `main_text_mnp_le_5`, and
    `table_2_selected`.
  - Status: README now names
    `libreevolve.alphaevolve_matrix_subset_scope_artifact_boundary.v1`, scopes
    it to the current `not_emitted_by_local_report_export` state, and lists
    required future emitted-artifact fields for subset ids, inclusion
    predicates, source linkage, counts, fell-behind/out-of-scope ids, nested
    subset evidence, artifact paths, and hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the Appendix A matrix row-note artifact boundary in README.
  - Spec evidence: README matrix wording needs to separate declared
    `mm_4x5x6` concurrent-work caveat validation from actual local
    report/export emission of row-note artifacts.
  - Status: README now names
    `libreevolve.alphaevolve_appendix_a_matrix_row_note_artifact_boundary.v1`,
    scopes it to the current `not_emitted_by_local_report_export` state, and
    lists required future emitted-artifact fields for note identity, target/
    rank/reference values, source text, caveat flags, nested row-note evidence,
    artifact paths, and hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the Appendix A matrix baseline-citation boundary in README.
  - Spec evidence: README matrix wording needs to separate stored best-known
    rank values from traceable per-target prior-work citation evidence.
  - Status: README now names
    `libreevolve.alphaevolve_appendix_a_matrix_baseline_citation_boundary.v1`,
    scopes it to the current `not_recorded_locally` state, and lists required
    future per-target citation fields for reference id, source table/page,
    source artifact path/hash, applicability caveats, field/characteristic
    scope, and report-visible baseline-source refs.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix cascade-run runtime boundary in README.
  - Spec evidence: README matrix wording needs to distinguish declared
    per-seed result-report validation from executed AlphaEvolve Section
    3.1-style repeated-seed cascade traces.
  - Status: README now names
    `libreevolve.matrix_cascade_run_runtime_boundary.v1`, scopes it to the
    current `not_emitted_by_local_runner` state, and lists required future
    emitted-record fields for run/target/seed ids, cascade ids and versions,
    stage traces, accepted final rank, candidate/result refs, artifact paths,
    and hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the matrix baseline-component runtime boundary in README.
  - Spec evidence: README matrix wording needs to distinguish final matrix
    result-report validation from AlphaEvolve Section 3.1 starting-algorithm
    provenance.
  - Status: README now names
    `libreevolve.matrix_baseline_component_runtime_boundary.v1`, scopes it to
    the current `not_emitted_by_local_runner` state, and lists required future
    emitted-record fields for baseline components, Adam optimizer metadata,
    generation-0 metrics, mutation lineage, result refs, artifact paths, and
    hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the pinned Strassen baseline bundle in README.
  - Spec evidence: README-facing paper evidence should distinguish helper-only
    generation from durable artifact files that a reader can inspect or
    reproduce from a fresh checkout.
  - Status: README now points to
    `libreevolve/problems/benchmarks/artifacts/strassen_2x2_publication_bundle/`,
    names `validate_strassen_2x2_publication_bundle()`, and states that the
    paper manifest validates report/inventory hashes and regeneration parity
    while keeping the claim scoped to one baseline.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the Figure 9 matrix-diff artifact boundary in README.
  - Spec evidence: README Figure 9 wording needs to distinguish declared panel
    metadata from actual rendered/OCR/source-diff appendix panel artifacts.
  - Status: README now names
    `libreevolve.alphaevolve_figure9_matrix_diff_artifact_boundary.v1`, scopes
    it to the current `not_emitted_by_local_report_export` state, and lists
    required future artifact fields for Figure 9a-9c panel ids/order/pages,
    code line spans, source-diff excerpts, rendered images, OCR text,
    panel-set artifacts, artifact paths, and hashes.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Document the Figure 4 matrix-discovery artifact and lineage boundary in
      README.
  - Spec evidence: README Figure 4 wording needs to distinguish declared
    exhibit metadata from actual rendered/source artifacts and accepted
    mutation lineage.
  - Status: README now names
    `libreevolve.alphaevolve_figure4_matrix_discovery_artifact_boundary.v1`,
    scopes it to the current `not_emitted_by_local_report_export` state, and
    lists required future artifact/lineage fields for Figure 4 reproduction.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.
