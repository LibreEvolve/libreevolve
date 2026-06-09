# Completed Roadmap Todo Items

Moved from `docs/todo/roadmap.md`. Keep this file as the archive for completed backlog items from that source; leave open items in `docs/todo/roadmap.md`.

## ROADMAP Todo: AlphaEvolve Alignment Corrections

- [x] Document companion notebook selection-scope provenance.
  - Spec evidence: the companion repository README limits
    `mathematical_results.ipynb` to outperformed-SOTA results, excludes
    matched-only results, and says AlphaEvolve runtime code is absent.
  - Status: ROADMAP now documents companion selection-scope rows for included
    improved results and intentionally absent matched-only results, including
    verifier-code availability, runtime-code absence, and matrix report
    validation for the `mm_4x4x4` companion claim.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document committed AlphaEvolve companion Colab source manifest.
  - Spec evidence: AlphaEvolve footnote 2 and Table 2 cite the accompanying
    `google-deepmind/alphaevolve_results` Colab notebook for discovered
    algorithms, mathematical results, and matrix decompositions.
  - Status: ROADMAP now documents `papers/companion_sources.json` as the
    committed external companion-source manifest with docs/TODO claim-surface
    links, local-cache policy, and paper-manifest validation.
  - Remaining gap: none for this bounded roadmap wording slice; local
    generated result-export artifacts and deeper per-cell claim spans remain
    active roadmap work.

- [x] Document normalized AlphaEvolve References bibliography manifest.
  - Spec evidence: the AlphaEvolve PDF includes a numbered References section
    after Author information, with entries through `[120]`.
  - Status: ROADMAP now documents `papers/references.json` as the committed
    normalized bibliography companion manifest, including source page,
    bibliographic fields, detected DOI/URL/arXiv fields, local-cache linkage,
    and citation-use categories.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document AlphaEvolve source-PDF rights companion manifest.
  - Spec evidence: page 1 of the local AlphaEvolve PDF states
    `© 2025 Google DeepMind. All rights reserved`.
  - Status: ROADMAP now documents `papers/source_rights.json` as the committed
    source-rights companion manifest validated by the paper-manifest gate,
    including row-identity linkage and reproduction-policy requirements.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document paper-cache row identity companion manifest.
  - Spec evidence: roadmap paper-cache provenance depends on each row's id,
    URL, and local PDF label describing the same source before version or
    rights evidence attaches.
  - Status: ROADMAP now documents `papers/row_identity.json` as the committed
    companion manifest that emits derived source identities for all 24 cache
    rows and links the AlphaEvolve row to `papers/source_versions.json`.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document AlphaEvolve source-PDF version companion manifest.
  - Spec evidence: page 1 of the local AlphaEvolve PDF identifies the source as
    `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`.
  - Status: ROADMAP now says the paper-manifest gate validates both the
    built-in source-version record and `papers/source_versions.json`, which
    emits the `2506.13131v1` row and links it to docs/TODO claim surfaces.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Remove prompt-current cross-run binding table from roadmap future work.
  - Spec evidence: AlphaEvolve Figure 3(b,c) treats generated edits as changes
    to the current program in the prompt.
  - Status: ROADMAP no longer lists prompt-current cross-run binding tables as
    future work because completed manifests now export
    `prompt_current_binding_table.jsonl`.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document full-mode target span and block-id records in prompt-current
      binding evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) treats generated edits as changes
    to the current program in the prompt.
  - Status: ROADMAP now includes full-mode whole-file and evolve-block target
    span records in `runtime.history.prompt_current_binding_report` and leaves
    cross-run tables as future work.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document prompt-history row joins in prompt-current binding evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) treats generated edits as changes
    to the current program in the prompt.
  - Status: ROADMAP now includes prompt-history row joins in
    `runtime.history.prompt_current_binding_report` and leaves cross-run tables
    as future work.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document workspace file-section span records in prompt-current binding
      evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) treats generated edits as changes
    to the current program in the prompt.
  - Status: ROADMAP now includes workspace file-section target/full-file span
    records in `runtime.history.prompt_current_binding_report` and leaves
    cross-run tables as future work.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document evolve-block inner span mapping in prompt-current binding
      evidence.
  - Spec evidence: AlphaEvolve Figure 3(b,c) treats SEARCH/REPLACE as edits to
    the current program in the prompt.
  - Status: ROADMAP now includes evolve-block inner span mapping in
    `runtime.history.prompt_current_binding_report` and leaves cross-run tables
    as future work.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Document normalized and skeleton prompt-example copy diagnostics in the
      roadmap.
  - Spec evidence: AlphaEvolve Figure 3(b,c) shows concrete examples that
    should guide format without becoming copied candidate payloads.
  - Status: ROADMAP now scopes `runtime.history.prompt_example_copy_report` to
    built-in exact, normalized-region, and example-format skeleton diagnostics.
  - Remaining gap: configurable acceptance policy, broader semantic/renamed
    example-copy detection, and custom prompt-template inventories remain
    future work.

- [x] Document current-run multi-edit consistency diagnostics in the roadmap.
  - Spec evidence: AlphaEvolve Figure 3(b) instructs same-response edits to be
    internally consistent.
  - Status: ROADMAP now lists
    `runtime.history.mutation_consistency_report` as current diagnostic
    evidence for multi-edit inventories, changed edit units, Python
    introduced/reference symbols, unresolved references, evaluator taxonomy,
    and admission links.
  - Remaining gap: language-aware scope/import resolution, config/resource
    dependency models, required companion-edit inference, cross-file dataflow,
    and benchmark-calibrated consistency gates remain future work.

- [x] Document bounded explanatory preambles in the roadmap.
  - Spec evidence: AlphaEvolve Figure 3(c) includes explanatory prose before a
    SEARCH/REPLACE payload while Section 2.3 keeps edits in structured blocks.
  - Status: ROADMAP now cites
    `runtime.history.natural_language_preamble_report` as bounded leading
    explanatory-preamble capture and keeps semantic proposal memory,
    configurable preamble policy, full-replacement disambiguation, rationale
    scoring, and cross-run tables as remaining work.
  - Remaining gap: none for this bounded roadmap wording slice.

- [x] Keep diff-format roadmap wording scoped until canonical AlphaEvolve
      fence guidance is primary.
  - Spec evidence: AlphaEvolve Section 2.3 and Figure 3 define SEARCH/REPLACE
    blocks with canonical fences: `<<<<<<< SEARCH`, `=======`, and
    `>>>>>>> REPLACE`.
  - Status: ROADMAP already lists SEARCH/REPLACE mutation with canonical
    AlphaEvolve fences, the parser accepts canonical and compact spellings,
    and `AGENTS.md` now makes the same paper-aligned versus compatibility
    distinction for future agents.
  - Remaining gap: none for diff-format roadmap wording; broader mutation
    response, prompt-example, and cross-edit consistency work remains active.
  - Verification: validation for this slice reran the paper manifest, secret
    scan, and diff checks before commit.

- [x] Require systems roadmap ready gates to have matching artifacts.
  - Evidence: roadmap systems work needs held-out/reference gates to be backed
    by concrete report artifacts, not only status fields.
  - Status: `libreevolve.systems_result_report.v1` now requires
    `alphaevolve_ready` reports to include matching artifact kinds for passed
    optimization, held-out, and reference-correctness gates.
  - Remaining roadmap gap: real systems fixtures still need to emit reports
    from actual held-out and randomized/reference-correctness checks.
  - Verification: focused systems-result tests cover missing gate artifacts.

- [x] Link benchmark roadmap anti-gaming threats to protected signals.
  - Evidence: roadmap benchmark work required explicit anti-gaming criteria,
    but the hardening contract did not prove which protected signal each
    shortcut threat defended.
  - Status: `libreevolve.benchmark_hardening.v1` now requires
    `protected_signal_ids` on shortcut threats and validates that they point to
    known protected signals.
  - Remaining roadmap gap: real benchmark fixtures still need to emit
    hardening reports from actual randomized/exhaustive validators and
    anti-gaming fixtures.
  - Verification: focused benchmark-hardening tests cover linked, missing,
    unknown, duplicate, and malformed protected-signal references.

- [x] Make LLM scheduler roadmap evidence explicit about shared routing.
  - Evidence: roadmap LLM budget/accounting work mentions role-specific
    accounting, but the call policy evidence did not state whether selection
    itself was per-role.
  - Status: per-call `scheduler_policy` now records the shared
    `global_backend_bandit` selection scope, shared role-selection boundary,
    and sorted reward-accounted roles.
  - Remaining roadmap gap: independent per-role routing, quotas, and budget
    stop policies remain open.
  - Verification: focused ensemble scheduler-policy tests cover the new
    telemetry fields.

- [x] Link timeout/cancellation roadmap policy rules to artifact kinds.
  - Evidence: roadmap timeout work requires persisted timeout artifacts, but
    the previous policy contract did not prove that artifact-required rules had
    matching declared artifact kinds.
  - Status: `libreevolve.provider_cancellation_policy.v1` now validates
    `artifact_kinds` on artifact-required rules, rejects missing required
    artifact kinds, and runtime manifests link timeout rules to `timeout_log`
    and runtime-deadline rules to `budget_stop_record`.
  - Remaining roadmap gap: live provider SDK cancellation and role-specific
    timeout-driven stop/quarantine behavior are still open.
  - Verification: focused cancellation-policy and loop manifest tests cover the
    artifact-kind linkage.

- [x] Scope provider-timeout roadmap policy rules by LLM role.
  - Evidence: roadmap timeout work asks for role-specific timeout artifacts,
    but the runtime policy previously declared provider timeout and ensemble
    deadline rules only as global `role: "*"` rules.
  - Status: runtime provider-cancellation manifests now declare timeout rules
    for `mutation`, `critique`, `feedback:*`, and `meta_prompt`, and retain the
    active role scope under `role_scope`.
  - Remaining roadmap gap: live provider SDK cancellation and timeout-driven
    stop/quarantine behavior are still open.
  - Verification: focused cancellation-policy and loop manifest tests cover
    safe role-prefix validation and role-scoped timeout rules.

## Staleness and Scope

- [x] Add retrieval transport/integrity requirements to prompt-context work.
  - Status: ROADMAP prompt/context work now requires unbounded provider-payload
    and source-content artifacts, learned/external ranking evidence beyond
    provider order, replayable transport/failure decision trees, and explicit
    default/custom-provider provenance tests.
  - Remaining roadmap gap: current DeepResearch records bounded transport,
    payload, cache, active-context, ranking-hash, source-content, and query-term
    evidence, but full audit-grade retrieval source integrity remains open.
  - Verification: focused DeepResearch tests cover default transport policy,
    provider payload snapshots, active context links, query-term/hypothesis
    inputs, source-content snapshots, and custom-provider provenance limits.

- [x] Add role-specific and provider-internal retry accounting to LLM budgets.
  - Status: ROADMAP evaluation-budget work now explicitly connects
    `libreevolve.llm_budget_report.v1` to future live enforcement for
    adapter-internal attempts, tokens, costs, provider wall-clock use, and
    restored retry-budget consumption.
  - Remaining roadmap gap: current runtime manifests emit the audit report and
    observed role/provider retry details, but live token/cost/time/adapter
    budget stops and retry-budget restore remain open.
  - Verification: focused budget-report, ensemble, feedback, loop, and config
    tests cover report validation, role accounting, provider retry telemetry,
    scheduler-state persistence, restored scheduler snapshots, and configured
    reward-accounted feedback roles.

- [x] Connect provider timeout/cancellation policy to live backend runtime
  enforcement.
  - Status: ROADMAP backend-scheduling work now requires connecting
    `libreevolve.provider_cancellation_policy.v1` to live provider SDK
    cancellation, role-scoped timeout/cancellation stop or quarantine behavior,
    and persisted role-specific timeout artifacts.
  - Remaining roadmap gap: current timeout support forwards provider request
    timeouts, adds ensemble wait deadlines, and emits role-scoped policy
    reports with `hard_cancel_ready: false`, but hard SDK cancellation and
    role-specific timeout quarantine/stop behavior remain open.
  - Verification: focused cancellation-policy, ensemble timeout, backend
    timeout, and loop manifest tests cover policy validation, role-scoped rules,
    request-timeout forwarding, local ensemble deadlines, and runtime
    deadline clamping.

- [x] Define remaining environment provenance/reproducibility policy.
  - Status: ROADMAP evaluation/provenance work now lists the remaining
    reproducibility policy explicitly: complete install-source semantics,
    external build execution/options/environment records, non-project build
    metadata policy, live provider service/API-version capture, provider cost
    and remote-default capture, accelerator budget/accounting semantics, and
    remaining private package-source resolution.
  - Remaining roadmap gap: current manifests provide bounded selected
    pyproject, build-system, installed package, wheel, direct-url/install,
    lockfile, pip-freeze, pip-config, NumPy, provider SDK-version, accelerator,
    and package-source-policy evidence, not a full reproducible environment
    snapshot.
  - Verification: focused provenance tests cover package metadata,
    build-system metadata, pip freeze/config snapshots, WHEEL/direct-url/RECORD
    metadata, accelerator probe degradation, and package-source policy records.

- [x] Connect real benchmark fixtures to anti-gaming hardening reports.
  - Status: ROADMAP representative-benchmark work now requires real benchmark
    fixtures to emit `libreevolve.benchmark_hardening.v1` reports from actual
    randomized/exhaustive validators and anti-gaming fixtures, including
    protected signals, shortcut threats, operation/rank instrumentation, and
    construction artifacts.
  - Remaining roadmap gap: shipped examples remain smoke-only/non-comparable
    unless upgraded to real benchmark fixtures that emit those reports.
  - Verification: focused benchmark-hardening, example-scope, matrix-example,
    and appendix/result tests cover hardening report validation, protected
    signal linkage, smoke-scope records, and current matrix smoke shortcut
    rejection.

- [x] Connect real systems fixtures to held-out/reference report gates.
  - Status: ROADMAP representative-benchmark work now requires real
    compiler/hardware/kernel/scheduling fixtures to emit
    `libreevolve.systems_result_report.v1` records with separate optimization,
    held-out/generalization, and reference-correctness gates plus matching
    artifacts.
  - Remaining roadmap gap: no real systems fixture currently emits those
    reports from live held-out/reference checks.
  - Verification: focused systems-result and result-certification tests cover
    gate validation, artifact linkage, alphaevolve-ready gating, and
    certification artifact contracts.

- [x] Wire explicit island round-robin cursor restore into database resumability.
  - Status: ROADMAP resume work now distinguishes implemented cursor-only and
    full archive cell/elite restore from remaining descriptor-value replay
    semantics, ordered migration-event replay, controller queues, and
    pending-work restore.
  - Remaining roadmap gap: migration events are still audit/replay-planning
    data, not an ordered restore engine; controller/pending-work resume and
    broader resumed experiment traces remain open.
  - Verification: focused island/database/CLI/loop archive-restore tests cover
    cursor restore, full archive cell/elite restore from manifest/history
    bundles, mutually exclusive archive-restore flags, and direct loop restore.

- [x] Update ROADMAP metric and feedback-normalization status.
  - Status: ROADMAP current-state and evaluation sections now treat declared
    metric normalization and normalized bounded LLM feedback score composition
    as implemented rather than future work.
  - Remaining roadmap gap: Pareto/frontier policies, configurable metric
    weighting, metric-specific archives/views, feedback calibration/ablation
    reporting, and broader multi-objective resurfacing remain open.
  - Verification: focused loop, feedback, loader, and config tests cover
    normalized metric selection scores, feedback-filled objective metrics,
    objective-metric schema validation, bounded maximize/minimize feedback
    scores, and out-of-bounds feedback rejection.

- [x] Update ROADMAP prompt-budget diagnostics wording.
  - Status: ROADMAP prompt/context work now distinguishes implemented rendered
    prompt character caps and deterministic section-budget diagnostics from the
    remaining backend-token-aware context-window packer.
  - Remaining roadmap gap: provider tokenizer/context-window integration,
    required-section fit behavior, backend-token-aware section packing, and
    live token/cost/provider-attempt budget stops remain open.
  - Verification: focused prompt, loop, config, and ensemble tests cover
    section-budget shape, required/optional section accounting, prompt
    diagnostics persistence, manifest-visible `prompt_max_chars`, config
    validation, and pre-backend rejection of oversized ensemble prompts.

- [x] Update ROADMAP proposal-rationale capture wording.
  - Status: ROADMAP prompt/context work now treats optional
    `IDEA`/`RATIONALE`/`HYPOTHESIS` proposal metadata preamble capture as
    implemented, while keeping richer versioned proposal objects and proposal
    scoring/indexed retrieval as future work.
  - Remaining roadmap gap: proposal scoring, indexed retrieval,
    hypothesis-refinement loops, and stricter policy for which proposal fields
    may influence retrieval/prompting/archive resurfacing remain open.
  - Verification: focused diff, prompt, loop, database, and DeepResearch tests
    cover extraction, stripping, prompt rendering, critique-updated provenance,
    bounded retrieval hypothesis context, and query-term metadata.

- [x] Add package-source policy semantics to environment roadmap evidence.
  - Evidence: environment provenance retained lockfile, installed-package,
    `pip freeze`, and `pip config` evidence, but did not state how to interpret
    private package-source lines after redaction.
  - Status: `runtime.environment.package_source_policy` now summarizes those
    evidence sources, records retention modes, unsupported private-source
    resolution surfaces, and hashes the policy evidence under
    `package_source_policy_evidence_v1`.
  - Remaining roadmap gap: full remote package artifact verification,
    private-index identity resolution, live package-source/auth checks, and
    non-pip package manager source interpretation remain open.
  - Verification: focused provenance tests cover normal and degraded
    package-source evidence.

- [x] Emit LLM budget-report instances from runtime manifests.
  - Previous evidence: `libreevolve.llm_budget_report.v1` existed as a
    validator contract, but final manifests only exposed compact
    `runtime.llm_accounting` summaries.
  - Status: runtime summaries now include `runtime.llm_budget_report`, a
    self-validated non-paper-ready budget report with observed per-role calls,
    ensemble retries, provider-internal attempt totals, token totals, and
    scheduler-state resume hashes.
  - Remaining roadmap gap: live token/cost/wall-clock/provider-attempt budget
    stops and resumed retry-budget consumption are still open.
  - Verification: focused runtime-manifest and budget-report tests pass.

- [x] Wire final LLM scheduler snapshots into restore semantics.
  - Previous evidence: runtime manifests persisted `runtime.llm_scheduler`, but
    the restore status said the snapshot was not wired into `evolve()`.
  - Status: direct `evolve()` and CLI runs can now restore validated
    `runtime.llm_scheduler` snapshots before run-directory preparation, and
    final manifests distinguish fresh from restored scheduler state.
  - Remaining roadmap gap: provider-output replay, controller queues,
    token/cost budget enforcement, and independent per-role routing remain
    open.
  - Verification: focused loop and CLI tests cover restore and mismatch
    rejection.

- [x] Correct archive-identity resume policy wording in manifest evidence.
  - Previous evidence: `policies.archive_identity.resume_status` still said
    snapshot restore was not implemented even after full archive cells/elites
    became restorable from manifest plus history.
  - Status: the policy now advertises
    `manifest_archive_state_restore_supported`, lists the restored archive
    surfaces, and keeps migration-event replay explicitly marked as not applied
    as a restore engine.
  - Remaining roadmap gap: migration replay and controller/pending-work resume
    state remain open.
  - Verification: focused database tests cover the policy record and the next
    admission after full archive restore.

- [x] Add prompt section-budget accounting to prompt-context roadmap work.
  - Previous evidence: `prompt_max_chars` only recorded final rendered-prompt
    truncation diagnostics.
  - Status: prompt diagnostics now include `section_budget` with section
    priorities, hashes, character/token estimates, required/optional totals,
    template overhead, and required-section fit status.
  - Remaining roadmap gap: true token-aware provider context packing remains
    open.
  - Verification: focused prompt and loop tests pass.

- [x] Add per-role scheduler-state evidence to LLM budget roadmap work.
  - Previous evidence: manifests summarized role accounting, but did not keep
    per-role backend counts/wins and pending/rewarded call ids separately from
    the global scheduler state.
  - Status: `role_scheduler_state` is now persisted in scheduler snapshots and
    copied into `runtime.llm_accounting` with aggregate scheduler totals.
  - Remaining roadmap gap: live token/cost budget enforcement, independent
    per-role routing/quotas, and resumed `evolve()` scheduler state remain
    open.
  - Verification: focused LLM ensemble and runtime manifest tests pass.

- [x] Add replayable archive-content restore to database resumability.
  - Previous evidence: runtime manifests persisted island cursor/counter
    state, but full MAP-Elites cells and elite archives were not restorable.
  - Status: manifest `runtime.history.archive_state.archive_contents` now
    records per-island MAP-Elites cells, elite-program ids, descriptor policy,
    and archive configuration. `load_archive_restore_bundle()` combines that
    state with accepted history records, and `ProgramDatabase` can restore the
    live cells/elites during construction.
  - Remaining roadmap gap: migration-event replay, controller queues, pending
    evaluations, and end-to-end resumed experiment traces remain open.
  - Verification: focused population/database tests cover archive restore from
    the manifest/history bundle.

- [x] Add redacted mutation prompt persistence evidence.
  - Previous evidence: generated candidate history rows persisted the rendered
    mutation prompt but did not explicitly record the persistence policy or raw
    prompt hash/count metadata.
  - Status: generated candidates now persist `metadata.prompt` according to
    `mutation_prompt_retention_mode` (`full`, `redacted`, `hash_only`, or
    `off`) plus `metadata.prompt_retention` with mode/policy and raw
    rendered-prompt hash/count metadata when retained by policy.
  - Remaining roadmap gap: configurable prompt/provider-response retention
    modes for critique, feedback, plugin/context, and replay surfaces remain
    open.
  - Verification: focused loop tests cover LLM-visible context secrets being
    absent from persisted prompts while retention metadata is present.

- [x] Add bounded pip configuration provenance for private-index evidence.
  - Previous evidence: manifests retained pip-freeze and lockfile hashes, but
    did not capture configured pip indexes/options except when they appeared in
    freeze output.
  - Status: runtime environment provenance now records `pip_config` with policy
    `pip_config_list_redacted_bounded_v1`, a raw stdout hash, bounded retained
    line hashes, timeout/error diagnostics, and secret/control-character
    sanitization.
  - Remaining roadmap gap: private package-source semantics, full install
    options, accelerator budget/accounting metadata, non-project build provenance,
    and live provider service/API-version evidence remain open.
  - Verification: focused provenance tests cover capture, bounds, redaction,
    and command failures.

- [x] Wire compact archive cursor restore into run entrypoints.
  - Previous evidence: archive cursor snapshots were validated and restorable
    through `ProgramDatabase`, but `evolve()` and the CLI did not expose that
    path for resumed experiment traces.
  - Status: `evolve(..., runtime_archive_state_snapshot=...)` and
    `libreevolve run --restore-archive-cursor-from-manifest` now load the
    compact `runtime.history.archive_state` cursor/counter subset into run
    initialization.
  - Remaining roadmap gap: full archive cells, elite lists,
    descriptor-normalization state, migration replay, and controller resume are
    still open.
  - Verification: focused loop/database/CLI tests cover cursor continuation
    and snapshot propagation.

- [x] Add runtime-visible LLM accounting evidence for budget planning.
  - Previous evidence: role accounting existed in scheduler snapshots and
    ledger replay, but runtime manifests lacked a compact field for auditing
    role totals and configured LLM limits together.
  - Status: final runtime manifests now write `runtime.llm_accounting` with
    schema `libreevolve.llm_accounting.v1`, policy
    `audit_summary_not_budget_enforced`, role-accounting copies, aggregate
    totals, and active logical-call, retry/fallback, timeout, prompt, and
    accepted-output caps.
  - Remaining roadmap gap: per-role retry budgets, token/cost/time coupling,
    and persisted/restored retry consumption are still open.
  - Verification: focused runtime loop tests cover no-LLM and ensemble
    snapshot accounting manifests.

- [x] Add safe provider status-code evidence to backend runtime work.
  - Previous evidence: provider failures were categorized, but concrete
    HTTP-style status codes exposed by SDK exceptions were discarded.
  - Status: failed LLM call telemetry now records nullable
    `provider_status_code`, and durable ledger replay validates it.
  - Remaining roadmap gap: raw provider diagnostics, provider penalties,
    quarantine, costs, and budget-stop policy remain open.
  - Verification: focused ensemble tests cover status-code capture and replay
    validation.

- [x] Add role-level provider-failure summaries to backend runtime evidence.
  - Previous evidence: provider failures were categorized per call, but there
    was no role-level summary to support roadmap work on role-specific
    penalties, quarantine, or budget stops.
  - Status: scheduler snapshots and durable LLM-call replay now aggregate
    normalized provider-failure categories by call role.
  - Remaining roadmap gap: those counters are not yet enforcement policy.
    Quarantine, provider penalties, budget-stop behavior, and resumed
    failure-policy state remain open.
  - Verification: focused ensemble tests cover category-to-counter mapping and
    retry/fallback aggregation.

- [x] Add role-accounting evidence to LLM scheduler roadmap work.
  - Previous evidence: roadmap/backend runtime gaps needed role-specific
    accounting, but the runtime only exposed mutation reward counters plus raw
    call rows.
  - Status: `LLMEnsemble.scheduler_state` and strict `llm_calls.jsonl` replay
    now provide validated role-level accounting summaries for successes,
    failures, reward-accounted calls, telemetry-only calls, ensemble
    retry/fallback attempts, adapter-internal provider attempts, and
    provider-reported token totals. Later work also added provider-failure
    category counts by role.
  - Remaining roadmap gap: configurable role-specific reward policy, quotas,
    provider-cost accounting, token-budget stop policy, and full restored
    scheduler state remain open.
  - Verification: focused ensemble tests cover live role accounting, malformed
    restored state, retry/fallback counters, and replay summaries.

- [x] Narrow restored/custom backend-spec work to future restore/registry surfaces.
  - Previous evidence: the roadmap still mentioned custom backend-spec
    validation as future work even though configured custom backends now exist.
  - Status: configured custom backend specs are implemented and revalidated at
    construction. Later completed slices added restored backend-spec and
    backend-registry validation surfaces.
  - Verification: focused config and ensemble tests cover custom spec
    validation, construction, post-validation mutations, role propagation, and
    non-protocol backend rejection.

- [x] Narrow custom backend prompt-policy work to future restore/registry and
  oversized/secret-like surfaces.
  - Previous evidence: roadmap wording could imply configured custom backends
    bypassed the ensemble prompt-validation boundary.
  - Status: configured custom backends are invoked through
    `LLMEnsemble.generate()`, and invalid prompt payloads are rejected before
    the backend object is called or scheduler/call-history state mutates.
  - Remaining roadmap gap: oversized/secret-like prompt policy remains open.
  - Verification: focused ensemble tests cover the configured custom backend
    invalid-prompt boundary.

- [x] Close the LLM call-id replay-policy roadmap gap.
  - Evidence: ROADMAP reproducibility work needs durable call identifiers for
    mutation, critique, feedback, and meta-prompt call streams.
  - Status: call ids are no longer UUID telemetry identities. They are
    deterministic ordered-call-stream identities derived from call sequence,
    backend/role/attempt coordinates, and prompt hash, with distinct ids for
    repeated identical calls inside a stream.
  - Remaining roadmap gap: broader replay work still needs RNG restore,
    archive sampling replay, and provider nondeterminism boundaries.
  - Verification: focused ensemble tests prove deterministic matching-stream
    call ids and distinct same-stream repeated-call ids.

- [x] Add prompt-program archive restore to resumability work.
  - Evidence: prompt-program history needs a reloadable archive boundary
    because prompt ids, reward sums, invalid-mutation penalties, lineage, and
    selection state drive future prompt sampling.
  - Status: implemented for the prompt archive boundary. `PromptDatabase`
    replays accepted prompt-history rows when a non-empty
    `prompt_history.jsonl` exists and validates schema, lineage, immutable
    prompt fields, hashes, counters, and reward-policy compatibility.
  - Remaining roadmap gap: broader run resumability still lacks
    archive/controller restore, RNG-state restore, archive sampling replay, and
    provider-output boundaries.
  - Verification: focused meta-prompt tests cover scored-arm restore,
    invalid-mutation penalty restore, unknown-id corruption rejection, and
    reward-policy mismatch rejection.

- [x] Narrow seeded replay work by fixing prompt-variant order.
  - Evidence: configured prompt variants previously entered
    `PromptDatabase` as untried UUID prompt programs and were selected by
    sorted UUID rather than configuration order.
  - Status: configured prompt variants are now selected in config order for
    untried arms, and restored prompt archives preserve replayed event order.
  - Remaining roadmap gap: run-local RNG restore, archive sampling restore, and
    provider nondeterminism boundaries remain open.
  - Verification: focused meta-prompt tests cover config-order selection
    across independent databases.

- [x] Add provider request-timeout configuration to built-in backend specs.
  - Previous evidence: backend runtime work had no LibreEvolve-controlled
    request timeout for built-in OpenAI, Anthropic, or Ollama clients.
  - Status: implemented as a partial backend-runtime step. Built-in backend
    specs accept positive `timeout_sec`; adapters forward it to provider client
    construction, and custom backends use their own JSON-safe `kwargs` surface.
  - Remaining roadmap gap: hard provider cancellation tokens, timeout-driven
    stop/quarantine policy, and role-specific timeout artifacts remain open.
  - Verification: focused config/backend/ensemble tests cover invalid timeout
    rejection, custom-spec rejection, direct client-constructor forwarding, and
    `build_llm()` forwarding.

- [x] Add Unicode format-control hardening for program metadata values.
  - Previous evidence: program metadata/evaluation keys were display-safe, but
    free-form string values could still persist invisible or bidirectional
    Unicode format controls.
  - Status: implemented. `Program` metadata and evaluation string values now
    reject Unicode `Cf` format controls while preserving ordinary Unicode and
    multiline prompt/diff text.
  - Remaining roadmap gap: newly identified durable labels or free-form
    provenance text still need an explicit reject/escape/hash policy.
  - Verification: focused program tests cover ordinary Unicode metadata,
    multiline values, metadata-value U+202E rejection, and evaluation-value
    zero-width joiner rejection.

- [x] Add explicit Unicode format-control tests for provider response metadata.
  - Previous evidence: provider response metadata labels were validator-guarded,
    but the Unicode-format-control contract was not directly covered by tests.
  - Status: implemented as test evidence. LLM-call telemetry sanitizes provider
    metadata labels containing zero-width joiner, and ledger replay rejects
    provider label fields containing right-to-left override.
  - Remaining roadmap gap: provider token/cost budget accounting, adapter retry
    accounting, and role-specific scheduler accounting remain open.
  - Verification: focused ensemble tests cover live-call sanitization and
    replay rejection for provider response metadata labels.

- [x] Narrow seed hidden-file roadmap gap after skipped diagnostics landed.
  - Previous evidence: hidden/cache seed entries could be omitted from loaded
    workspaces without an explicit run-visible trail.
  - Status: implemented for default omission diagnostics. Seed loading records
    skipped hidden/cache entries in `initial_workspace_skipped` and run
    manifests under `problem.seed_skipped`; top-level hidden/cache seed
    directories no longer load as normal workspaces.
  - Remaining roadmap gap: configurable seed include/exclude policy for
    intentional dotfile/cache retention remains open.
  - Verification: focused loader and loop tests cover top-level hidden seed
    files/directories, cache directories, fully skipped roots, and manifest
    persistence.

- [x] Add provider endpoint/client-context provenance to backend hardening.
  - Previous evidence: backend behavior could change when SDK/environment
    defaults pointed OpenAI, Anthropic, or Ollama calls at different API hosts,
    proxy gateways, organizations, projects, or local servers, while config
    rejected explicit `base_url`, `host`, `organization`, and `project`
    fields.
  - Status: implemented as validated built-in backend client-context
    configuration. OpenAI accepts `base_url`, `organization`, and `project`;
    Anthropic accepts `base_url`; Ollama accepts `host` and uses a configured
    `ollama.Client`. Accepted values are manifest config and LLM-call
    `client_context` provenance. Omitted fields still intentionally use
    provider SDK/environment defaults.
  - Verification: focused config/backend/ensemble tests prove valid
    forwarding, unsafe rejection/sanitization, call telemetry, and replay
    validation. README, backend/configuration, run-artifact, architecture, and
    paper-index docs describe the implemented boundary.

- [x] Add model-specific OpenAI reasoning-parameter compatibility to backend
  hardening.
  - Previous evidence: `Config.validate()` accepted only `low`, `medium`,
    `high`, and `xhigh` for every OpenAI model. It rejected
    provider-supported `none` and `minimal` values for newer models while
    accepting `xhigh` without checking model-family eligibility.
  - Status: implemented as a conservative local compatibility policy. A
    2026-06-03 official OpenAI docs/schema check confirmed current effort
    values `none`, `minimal`, `low`, `medium`, `high`, and `xhigh` plus
    documented restrictions for `gpt-5.1`, pre-`gpt-5.1`, `gpt-5-pro`, and
    model-dependent `xhigh`. `Config`, direct `OpenAIBackend` construction,
    and `build_llm(config)` now validate those known combinations before
    provider calls.
  - Verification: focused config/backend tests cover accepted `none`,
    `minimal`, `high`, and `xhigh` combinations plus rejected `none` on known
    pre-`gpt-5.1` families, `minimal`/`xhigh` on `gpt-5.1`, non-`high` on
    `gpt-5-pro`, and `xhigh` on ineligible models. API routing remains open in
    `docs/todo/code.md`.

- [x] Add direct backend adapter parameter validation to backend hardening.
  - Previous evidence: backend-spec validation covered config-created
    providers, but direct adapter constructors previously forwarded invalid
    values such as blank model ids and non-positive token limits into provider
    SDK calls.
  - Status: implemented for bundled direct adapters. `OpenAIBackend`,
    `AnthropicBackend`, and `OllamaBackend` now validate manifest-safe model
    ids and positive integer token limits before provider calls; OpenAI also
    validates direct `reasoning_effort` values.
  - Verification: `tests/llm/test_backends.py` proves invalid direct
    constructor parameters are rejected before mocked SDK calls, and
    `docs/backends.md` documents the constructor boundary. Future custom
    backend registry and restored backend-spec validation remains open in
    `docs/todo/roadmap.md` under a separate item.

- [x] Add direct backend prompt validation to backend hardening.
  - Previous evidence: ensemble-created calls validated prompt type before
    scheduler state changes, but direct OpenAI, Anthropic, and Ollama adapter
    calls could otherwise be used as the library boundary.
  - Status: implemented for bundled direct adapters. All three bundled
    adapters call the shared non-empty text prompt validator before SDK payload
    construction.
  - Verification: `tests/llm/test_backends.py` covers OpenAI non-string,
    Anthropic empty, and Ollama whitespace-only direct calls before mocked
    provider SDK calls. Future restored/custom backend prompt validation and
    oversized/secret-like prompt policy remains open in `docs/todo/roadmap.md`
    under a separate item.

- [x] Extend duplicate-key rejection beyond `show` history inspection.
  - Previous evidence: `libreevolve show` rejected duplicate object names in
    `history.jsonl`, but failure-history, prompt-history, plugin-artifact, and
    other replay/query readers still used plain JSON parsing or lacked a
    duplicate-key-safe entry point.
  - Status: implemented for current reader surfaces. `core.jsonl` now provides
    duplicate-name-rejecting JSON object and JSONL object readers with
    line-numbered diagnostics. Accepted-history restore, failure-history
    replay, prompt-history replay, best-artifact manifest reporting, TTT/RL
    plugin export restore, and DeepResearch disk-cache loading use or expose
    strict duplicate-key-safe parsing.
  - Verification: focused tests cover nested duplicate-name rejection in the
    shared JSONL reader, accepted-history restore, failure-history replay,
    prompt-history replay, duplicate-key TTT/RL plugin export restore,
    duplicate-key DeepResearch disk cache rejection, and duplicate-key
    best-artifact manifest reporting.

- [x] Add best-artifact export failure accounting to runtime finalization.
  - Previous evidence: the core loop finalized the manifest before the CLI
    exported `best.py` and `best_workspace/`. A patched local proof forced
    `_write_best_artifacts()` to raise after a valid seed-only run; the CLI
    failed, no best artifacts existed, and the manifest still reported
    `runtime.status="completed"` with no export-failure diagnostic.
  - Status: implemented. Core `evolve()` finalization now attempts best export
    when a selected best program exists, records
    `runtime.best_artifact_export.status` as `completed` or `failed`, keeps
    `runtime.status` scoped to the evolution result, and stores current
    best-artifact path/hash/error diagnostics in the completed manifest. The
    CLI consumes that record instead of owning the export sequence.
  - Verification: focused direct-loop tests cover successful artifact
    materialization and redacted export-failure accounting; focused CLI tests
    cover success/failure reporting from the manifest.

- [x] Add prompt-program identity/deduplication policy.
  - Status: implemented and documented. Prompt-program identity remains
    UUID4-arm identity for compatibility, duplicate template text is modeled as
    independent configured/evolved prompt arms, and accepted prompt-history
    records include `template_sha256` for content identity.
  - Verification: duplicate configured-variant and duplicate mutated-template
    tests cover shared hashes with independent prompt ids.

- [x] Add manifest-bound archive-cell range validation to run-inspection
  roadmap work.
  - Status: implemented and documented. `libreevolve show` uses
    `manifest.json.config.map_elites_bins` as the expected MAP-Elites cell
    upper bound when present, rejects coordinates outside that range with
    line-numbered diagnostics, and keeps legacy behavior when bounds are
    absent.
  - Verification: CLI tests cover out-of-range cells, absent-bin compatibility,
    and malformed manifest bin metadata.

- [x] Add schema validation for ThetaEvolve prompt/response export examples.
  - Evidence: `TTTRLPlugin` describes GRPO export rows as prompt/response/
    reward triples, but `on_evaluated()` accepted any truthy metadata values
    for `prompt` and `diff`.
  - Status: implemented. Training examples are queued only for non-empty
    string prompt and diff metadata, malformed prompt/response examples are
    skipped with diagnostic counters, and docs define the stable export schema.
  - Verification: plugin tests cover non-string, empty, whitespace, and valid
    text prompt/response metadata.

- [x] Add score/reward type validation to ThetaEvolve export examples.
  - Evidence: ThetaEvolve/GRPO export examples need numeric rewards, but
    `TTTRLPlugin.on_evaluated()` accepted the hook score without validating it.
  - Status: implemented. Export scores must be finite non-boolean numbers,
    accepted raw/reward fields are floats, and invalid scores increment a
    diagnostic counter before raising.
  - Verification: plugin tests cover bool, nonnumeric, non-finite, negative,
    zero, and positive scores before export.

- [x] Add finalization semantics for pending ThetaEvolve export examples.
  - Evidence: `TTTRLPlugin` kept examples in memory until a `train_every`
    generation boundary.
  - Status: implemented. Artifact metadata collection performs a final pending
    export before manifest metadata is returned and records the chosen
    finalization policy.
  - Verification: plugin and loop tests cover direct final flush and short
    non-multiple generation runs.

- [x] Add invalid-record progress semantics to ThetaEvolve export work.
  - Evidence: strict JSONL protects `grpo_data.jsonl`, but malformed queued
    rows previously could park the exporter cursor.
  - Status: implemented by preventing malformed examples from entering the
    export cursor. Invalid prompt/response fields are skipped, invalid scores
    raise with diagnostics, and later valid examples remain exportable.
  - Verification: plugin tests cover invalid-score then valid-export batches
    and repeated valid flushes.

- [x] Add artifact-root containment policy for ThetaEvolve export plugins.
  - Evidence: current CLI wiring scopes `ttt_rl` exports under
    `plugin_artifacts/ttt_rl/`, but the plugin constructor itself accepts any
    `log_dir`.
  - Status: documented policy. CLI-loaded `ttt_rl` exports are run-contained;
    direct `TTTRLPlugin(log_dir=...)` exports are allowed external,
    user-managed artifacts whose provenance is the manifest `log_dir`, path,
    count, hash, and byte metadata.
  - Verification: README, plugin docs, and run-artifact docs define the
    containment boundary; CLI tests cover run-scoped built-in wiring.

- [x] Add redaction and size budgets to ThetaEvolve export examples.
  - Evidence: prompt/response export rows are durable prompt-bearing artifacts
    and potential future training inputs, but the current exporter only relies
    on strict JSONL serialization.
  - Status: implemented. TTTRL exports pass prompt and response text through
    shared secret-pattern redaction, enforce per-field and combined
    prompt/response character budgets, and report redaction/truncation counters
    plus payload caps in artifact metadata.
  - Verification: plugin tests cover clean payloads, prompt and diff secrets,
    oversized field truncation, aggregate truncation, and metadata counters;
    README, plugin docs, and run-artifact docs state the enforced payload
    policy.

- [x] Add immutable plugin snapshot APIs to provenance hardening.
  - Roadmap evidence: plugin roadmap items cover retrieval, guidance,
    training-data export, artifact metadata, and prompt-context provenance, but
    they did not yet require plugin snapshot APIs to sever mutable aliases to
    live plugin state.
  - Status: implemented. `DeepResearchPlugin.prompt_context_metadata()` returns
    deep-copied retrieval events, and `TTTRLPlugin.get_training_data()` returns
    deep-copied training rows.
  - Verification: plugin tests mutate returned nested retrieval sources and
    returned training rows, then verify fresh plugin snapshots still expose the
    original internal state; plugin docs state the defensive snapshot contract.

- [x] Define archive-selection semantics for plugin-adjusted scores.
  - Roadmap evidence: plugin score composition and archive `selection_score`
    must have an explicit relationship.
  - Status: documented. Plugin score hooks can alter top-level fitness for
    threshold/prompt/backend reward paths, but archive selection continues to
    use declared evaluator metrics through `metadata.selection_score`.
  - Verification: loop tests cover score-composition divergence from archive
    selection score.

- [x] Add unambiguous context include-pattern match accounting.
  - Evidence: context selection metadata is reproducibility evidence for which
    local files were considered, selected, or skipped.
  - Status: implemented. `include_patterns[].matches` remains the pre-filter
    supported-file count, while `selected_matches` records files that survived
    hidden, exclude, stat, and resource filters.
  - Verification: loader tests cover include, exclude, hidden, nested,
    recursive, and unmatched-source accounting.

- [x] Add exact-output-shape validation to representative geometry benchmarks.
  - Evidence: fixed-`n` geometry benchmarks must score the materialized output
    shape, not a spoofable protocol.
  - Status: implemented for the current circle-packing smoke fixture. The
    validator canonicalizes to plain circle triples and rejects subclass/count
    mismatches before scoring.
  - Verification: example tests cover the previously accepted spoofed-list
    output.

- [x] Add benchmark metric-bound calibration to representative benchmark work.
  - Evidence: benchmark hardening should include normalization behavior, not
    only validators and artifact schemas.
  - Status: added and partially implemented. ROADMAP now calls out reachable
    metric ranges, target/SOTA values, and normalization behavior as
    representative-benchmark requirements; the matrix smoke fixture's primary
    bounds now cover the reachable `1.0 / count` range.
  - Verification: example tests confirm counted matrix-multiplication
    improvements remain ordered without clamped metric diagnostics.

- [x] Apply evaluator path-boundary checks to direct evaluator API usage.
  - Roadmap evidence: evaluator hardening and sandbox/isolation work should
    apply consistently to CLI/evolution runs and direct library evaluation.
  - Status: implemented. Direct default validators now flow through
    `preflight_evaluator_contracts()` before subprocess execution.
  - Verification: evaluator tests cover direct default-validator outside,
    missing, directory, non-Python, and symlink escape cases.

- [x] Add required-problem-file link tests to problem/provenance hardening.
  - Evidence: seed and context paths have explicit link rejection, and required
    problem files are task-defining provenance inputs.
  - Status: implemented. Problem root links are rejected before path
    resolution; linked required setup files continue to fail before reads.
    README and problem-format docs now state both policies.
  - Verification: platform-aware loader tests cover symlink/junction roots and
    required setup-file paths; a CLI test verifies a linked root is rejected
    before `evolve()` runs.

- [x] Add synthetic-failure metric-vector policy to evaluation roadmap.
  - Evidence: real validator JSON must include every declared metric, but
    internal evaluator failures do not yet preserve that shape.
  - Status: documented. ROADMAP now calls for a complete synthetic evaluator
    failure metric-vector policy and explicitly notes that current
    framework-generated failures can omit declared secondary metrics and rely on
    error/stage metadata.

- [x] Add diff-error schema and redaction policy to evaluation roadmap.
  - Evidence: synthetic diff/mutation failures should be prompt-safe and
    history-safe because they become evaluator stage errors, top-level errors,
    and future failure-memory evidence.
  - Status: implemented. The evaluator now uses canonical known reason codes,
    explicit `unknown_diff_error` and `malformed_diff_error` policies, and
    bounded/redacted `diff_error_v1` detail metadata.
  - Verification: focused evaluator tests cover parser-style known reasons,
    secret-like unknown strings, non-string direct values, and long/control
    string diagnostics.

- [x] Add foreign run-directory listing diagnostics to runtime hardening.
  - Roadmap evidence: run-directory reuse is not resume, but startup manifests
    still summarize unknown preserved entries so mixed directories remain
    visible without exposing raw names.
  - Status: implemented. Existing run-directory listing failures now become
    structured redacted manifest diagnostics instead of raw startup exceptions.
    The diagnostic keeps explicit unknown-entry semantics and preserves
    overwrite cleanup safety.
  - Verification: database tests cover unreadable listing, secret-like error
    redaction, and overwrite with known artifact cleanup.

- [x] Add typed CausalPlugin mutation-evidence validation to plugin hardening.
  - Roadmap evidence: paper-inspired plugin work already scopes the causal
    plugin as heuristic and tracks hook exception policy, but causal factor
    attribution should not depend on unvalidated candidate metadata.
  - Status: implemented. The causal plugin now validates mutation evidence
    before parsing, records `text` / `missing` / `non_text` evidence statuses,
    counts malformed non-text evidence, and avoids raw parser crashes.
  - Verification: causal plugin tests cover malformed non-text values, missing
    evidence, text diff evidence, fallback factors, and artifact metadata
    counters.

- [x] Add identity validation to lower-level archive API hardening.
  - Roadmap evidence: queryable evolutionary databases, migration, resume, and
    archive diagnostics rely on candidate ids as safe join keys across live and
    persisted state.
  - Status: implemented. Raw MAP-Elites and island insertion enforce
    manifest-safe program id, parent id, and lineage validation before mutating
    archive state.
  - Verification: focused MAP-Elites and island tests cover mutated unsafe ids,
    parent ids, and lineage, including no retained best/cell/elite state and no
    island sequence/current advancement.

- [x] Add direct prompt-program add quarantine to prompt archive hardening.
  - Roadmap evidence: prompt-program evolution, prompt lineage, prompt DB
    replay, and resumability depend on rejected prompt-program state being
    visible in durable history streams.
  - Status: implemented. Direct `PromptDatabase.add()` duplicate ids and
    unknown parents now use the same `prompt_reference_error` invalid-history
    stream as prompt scoring and mutation reference failures.
  - Verification: meta-prompt tests cover duplicate direct add ids,
    unknown-parent direct adds, preserved `prompt_history.jsonl` add events,
    and unchanged prompt database state.

- [x] Add duplicate accepted-history id quarantine to database hardening.
  - Roadmap evidence: resumable archives, queryable program databases, lineage
    replay, and failure diagnostics require rejected history records to be
    observable after the run aborts or continues.
  - Status: implemented. Accepted-history duplicate id failures now produce
    durable `history_invalid.jsonl` diagnostics without appending to
    `history.jsonl` or advancing accepted in-memory identity/program state.
  - Verification: database regression tests cover the duplicate row,
    quarantine message, preserved accepted stream, and unchanged `_ids` /
    accepted-program list.

- [x] Add plugin state-retention limits to runtime/plugin hardening.
  - Roadmap evidence: runtime and plugin work tracks resumability, artifact
    manifests, retrieval retention, and ThetaEvolve-style export semantics, but
    long-running plugin state needs an explicit memory/offload policy.
  - Status: implemented. Causal guidance and TTT export plugins now have
    positive-integer retention caps, manifest-visible retention counters, and
    overflow export/prune behavior for TTT examples. Docs state the remaining
    non-resumable training-checkpoint boundary.
  - Verification: plugin tests cover bounded causal history, TTT overflow
    export, retained/drop/pending/exported counts, constructor validation, and
    repeated flush behavior.

- [x] Add local PDF stat/read diagnostics to paper-index hardening.
  - Roadmap evidence: local paper-cache validation is part of the evidence
    pipeline for AlphaEvolve-alignment audits and should fail as structured
    validator output.
  - Status: implemented. Paper manifest validation now emits structured,
    redacted local-PDF stat/read issues with relative file labels and row ids,
    and reports directory-shaped PDF paths as non-regular local cache entries.
  - Verification: paper-manifest tests cover matching, missing, mismatched,
    unreadable/stat-error, unreadable/read-error, and directory-shaped local
    PDFs, including CLI text and JSON output.

- [x] Add required problem-file read/stat failure handling to setup hardening.
  - Roadmap evidence: task-package setup hardening requires deterministic
    diagnostics for `task_description.txt`, `metrics.yaml`, and `validate.py`
    before run artifacts, preflight, or evaluator behavior are trusted.
  - Status: implemented. Required-file read/stat failures now become redacted
    setup diagnostics while preserving missing-file, directory, link, invalid
    UTF-8, and YAML behavior.
  - Verification: loader tests cover all three required files with secret-like
    error text.

- [x] Add seed-file read-failure handling to candidate setup hardening.
  - Roadmap evidence: multi-file/codebase candidate fidelity depends on
    path-aware seed setup diagnostics for both legacy `.py` seeds and workspace
    seed files.
  - Status: implemented. Top-level and workspace seed read failures now become
    redacted file-scoped setup diagnostics, with an explicit fatal setup policy.
  - Verification: loader tests cover top-level seeds, workspace seeds, decode
    failures, read failures, malformed evolve-block markers, and normal
    workspace seed loading.

- [x] Add seed-root enumeration failure handling to candidate setup hardening.
  - Roadmap evidence: codebase candidate fidelity depends on robust,
    inspectable seed ingestion before initial evaluations and run manifests.
  - Status: implemented. Seed-root listing failures become redacted setup
    diagnostics instead of raw host exceptions, while missing and linked roots
    retain their existing semantics.
  - Verification: focused loader tests cover unreadable, missing, linked, and
    normally readable seed roots.

- [x] Add context source stat-failure handling to ingestion hardening.
  - Roadmap evidence: context byte budgets and skipped diagnostics are part of
    reproducible prompt-context selection.
  - Status: implemented. Context source stat failures from traversal,
    classification, and byte-budget checks become redacted skipped
    `stat_error` diagnostics with unknown-size/omitted-hash semantics.
  - Verification: focused loader tests cover selected and preclassification
    source stat failures while preserving other context sources.

- [x] Add context directory-enumeration failure handling to ingestion
  hardening.
  - Roadmap evidence: deterministic local context selection should keep
    prompt/literature provenance robust under partial filesystem failures.
  - Status: implemented. Context traversal records root and nested directory
    listing failures as redacted `directory_listing_error` skipped diagnostics
    and preserves readable sibling context.
  - Verification: focused loader tests cover root and nested context directory
    enumeration failures with secret-like error text.

- [x] Add selected context-source read-failure handling to ingestion hardening.
  - Roadmap evidence: first-class literature/context ingestion depends on
    deterministic local source selection, extraction metadata, and skipped
    diagnostics that survive partial local filesystem failures.
  - Status: implemented. Selected source `read_bytes()` failures become
    skipped `read_error` diagnostics with redacted text while other usable
    context sources continue loading.
  - Verification: focused loader tests cover unreadable `.txt`, `.md`, `.py`,
    and `.pdf` selected sources.

- [x] Add skipped context-source read-failure handling to ingestion hardening.
  - Roadmap evidence: context-selection diagnostics are part of reproducible
    prompt/literature provenance, including sources deliberately excluded from
    prompt rendering.
  - Status: implemented. Skipped-source read failures retain the original skip
    reason and persist omitted-hash semantics via `sha256: None`,
    `bytes: None`, `read_status: read_error`, error type, and redacted text.
  - Verification: focused loader tests cover unsupported, excluded,
    hidden-not-included, and not-included skipped sources.

- [x] Add context-manifest read-failure handling to ingestion hardening.
  - Roadmap evidence: prompt/context ingestion work calls for deterministic
    local context selection, source hashes, skipped diagnostics, and
    reproducibility metadata.
  - Status: implemented. Context manifest `read_bytes()` failures are
    converted into path-aware redacted `ValueError` setup diagnostics instead
    of propagating raw `OSError` text.
  - Verification: focused loader tests cover unreadable manifests alongside
    invalid UTF-8, malformed YAML, duplicate keys, and directory-shaped
    manifests.

- [x] Add directory-enumeration failure handling to provenance hardening.
  - Roadmap evidence: runtime manifests and provenance hardening require
    robust, redacted source/problem tree evidence for expensive evolutionary
    runs, including partial-failure diagnostics.
  - Status: implemented. Source/problem tree provenance records directory
    enumeration failures as skipped `directory_listing_error` entries with
    redacted diagnostics instead of propagating raw host exceptions.
  - Verification: focused provenance tests cover root and nested directory
    enumeration failures, secret-like diagnostics, skipped hashes, and
    readable-subtree preservation.

- [x] Add collision-resistant failure fingerprints to database/failure-memory
  work.
  - Roadmap evidence: database and search work calls for resurfacing programs
    by feedback, novelty, lineage, and failure diagnostics. Approximate
    repetition grouping can distort that resurfacing.
  - Status: implemented. Generated and seed failure records now persist a
    `failure_fingerprint` with schema `failure_fingerprint_v1`; repetition
    counts are keyed by the fingerprint SHA-256 rather than a bounded mutation
    display snippet. The fingerprint incorporates parent id, diff/evaluator
    error hashes, full mutation payload hash, changed files, and file-delta
    hash.
  - Verification: focused database tests cover ordinary repetitions, distinct
    long mutations with the same 500-character prefix, parent changes,
    evaluator-error changes, changed-file changes, failed appends, redaction,
    and seed-failure fingerprints.

- [x] Add context-tree count/depth limits to prompt/context ingestion work.
  - Roadmap evidence: prompt/context work calls for deterministic local
    context selection, PDF/text extraction, source hashes, skipped diagnostics,
    and resource limits, so traversal and provenance size need explicit bounds.
  - Status: implemented. Context manifests accept `max_context_entries`,
    `max_context_depth`, `max_skipped_diagnostics`, and
    `max_context_provenance_chars`; loader diagnostics record deterministic
    `max_context_entries` and `max_context_depth` skips, retained skipped
    record counts, omitted counts/reasons, and provenance truncation status.
  - Verification: focused loader tests cover large source counts, deep nesting,
    skipped-diagnostic caps, provenance-size trimming, and invalid limit
    validation.

- [x] Add LLM call-history retention limits to runtime/backend hardening.
  - Roadmap evidence: runtime and backend roadmap work calls for LLM-call,
    token, cost, retry, async-queue, and resume accounting, but previously did
    not require a scalable retention boundary for the ensemble's in-memory call
    telemetry.
  - Status: implemented. `LLMEnsemble.call_history` is capped by
    `llm_call_history_max` / `--llm-call-history-max`, defaulting to `500`, and
    `call_history_retention` exposes retained, total, and dropped counts. The
    loop reconstructs current call spans against total/dropped counters when
    older records have been evicted.
  - Remaining gap: durable append-only LLM call-artifact work is still open in
    `docs/todo/roadmap.md`.

- [x] Record the effective metric schema in run manifests.
  - Evidence: `Problem.__post_init__` marks the effective primary metric in
    `Problem.metrics`, including implicit and direct-construction primaries.
  - Status: implemented. Startup manifests now persist
    `problem.objective_schema` with normalized metric names, directions,
    bounds, effective primary flags, `primary_metric`, `primary_bounds`, and
    `metric_count`. Tests cover explicit primary/minimize metrics in the loop
    manifest path and direct database objective-schema persistence.

- [x] Refresh the roadmap date and status.
  - Evidence: `ROADMAP.md:3` says it reflects the codebase as of
    `2026-03-26`, while the current checkout has papers downloaded and newer
    docs/tests than that snapshot.
  - Required result: update the roadmap date and state which current code/docs
    were audited.

- [x] Refresh the roadmap date/status after the 2026-05-26 audit additions.
  - Evidence: `ROADMAP.md:3` now says it reflects the codebase as of
    `2026-05-25`, but the current audit has added further AlphaEvolve-fidelity
    TODO evidence on 2026-05-26, including direct ensemble metadata cardinality
    and direct program metric-vector validation gaps.
  - Required result: update the roadmap snapshot date and status text only
    after the code, roadmap, README, and paper-index audits for the current
    pass are complete, so the date reflects a verified current-state review
    rather than partial in-progress work.
  - Status: ROADMAP now uses `2026-05-26` and says the pass covered local docs,
    the paper index, and checked-in tests.

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

## Missing Roadmap Items

- [x] Add configuration/schema validation to runtime hardening.
  - Evidence: AlphaEvolve-style task setup depends on configuration for
    prompts, evaluators, LLMs, and mutation behavior.
  - Current status: `Config.validate()` and `_build_config()` now reject
    unknown problem config keys, invalid mutation/ensemble enums, malformed
    backend specs, invalid evaluator-stage numbers, and invalid top-level
    runtime/population ranges. LLM feedback grader schemas are also validated.
    Malformed YAML and non-mapping top-level `config.yaml` files are now
    normalized into clear path-aware `ConfigError` startup diagnostics.
    Remaining runtime hardening is focused on plugin-specific config schemas
    and any future live provider/model capability lookup beyond the current
    local OpenAI API-mode and reasoning-effort compatibility policy.

- [x] Add invalid-encoding diagnostics to config hardening.
  - Evidence: config-file readability is part of experiment setup. Decode
    failures should identify the offending file just like malformed YAML and
    non-mapping top-level documents.
  - Current evidence: `_build_config()` reads `config.yaml` as UTF-8 before the
    `yaml.YAMLError` handling path. A local temp CLI proof with byte `0xff` in
    `config.yaml` produced a user-facing codec error but did not include the
    config file path.
  - Required result: catch config-file decode failures, report path-aware
    startup diagnostics, and add regression tests ordered before provider
    construction and run-directory cleanup.
  - Status: implemented. `_build_config()` catches `UnicodeDecodeError` while
    reading problem-local `config.yaml` and reports a path-aware UTF-8 startup
    diagnostic; CLI regression coverage proves the config path appears in the
    error.

- [x] Add missing boolean-field validation to config hardening.
  - Evidence: AlphaEvolve-style experiments need explicit configuration
    switches for critique and meta-prompt evolution; stringly typed booleans
    can silently enable expensive or behavior-changing LLM paths.
  - Current evidence: `Config.validate()` now checks booleans for
    `evaluator_artifact_redact_secrets`, `llm_fallback`,
    `capture_proposal_metadata`, `meta_prompt_evolution`, and
    `critique_enabled`. Tests cover direct `Config` construction and a
    problem-local YAML string rejected before the CLI calls `evolve()`.
  - Required result: validate all boolean config fields, cover YAML/CLI paths
    with tests, and update configuration docs so the completed schema
    validation claim is bounded to what is actually enforced.
  - Status: implemented.

- [x] Add prompt-text field validation to config hardening.
  - Evidence: critique/revision prompts are part of the configured
    AlphaEvolve-inspired review path and should be auditable text, not
    arbitrary YAML/programmatic objects.
  - Current evidence: `Config.validate()` now requires `critique_prompt` to be
    a string and keeps the empty-string default as the built-in critique
    instruction path.
  - Required result: validate configured prompt-text fields as strings across
    direct `Config` construction and `config.yaml`; add tests and documentation
    that distinguish empty/default prompt behavior from malformed prompt data.
  - Status: implemented for `critique_prompt`.

- [x] Add scalar run-field validation to config hardening.
  - Evidence: reproducible AlphaEvolve-style experiments need unambiguous
    seeds and artifact roots. `Config.validate()` currently accepts
    `seed="42"`, `log_dir=7`, and `problem_name=""`. Those values can alter
    replay behavior, fail later during path construction, or write artifacts
    directly into the log root instead of a named run subdirectory.
  - Required result: validate `seed` as an integer, `log_dir` as a non-empty
    path string or `PathLike` normalized to a path, and `problem_name` as a
    non-empty safe run-name component before path-confinement checks; cover
    direct `Config`, YAML, and CLI override paths with tests.
  - Current evidence: `Config.validate()` now requires integer `seed`,
    normalizes non-empty string/path-like `log_dir` to a string, and rejects
    empty, nested, parent-relative, and host-invalid `problem_name` values.
    A CLI test rejects unsafe `--run-name ../escape` before `evolve()`.
  - Status: implemented for scalar field validation. Final resolved
    run-directory confinement under symlinks/junctions is implemented under the
    runtime-hardening item below.

- [x] Add task-description validation to problem-contract hardening.
  - Evidence: AlphaEvolve-style task setup requires a concrete natural-language
    task/objective to drive prompt construction and make runs auditable.
  - Current roadmap gap: configuration validation work covers `config.yaml`,
    metrics, evaluator stages, and runtime fields, but not the required problem
    task file.
  - Current evidence: `load_problem()` strips `task_description.txt` and now
    rejects the empty string with a path-aware problem-load error. Loader tests
    cover whitespace-only task files.
  - Required result: treat empty or whitespace-only task descriptions as
    problem-load errors with clear path diagnostics; add loader/CLI tests and
    update problem-format docs so the task objective is a required contract,
    not merely an optional prompt string.
  - Status: implemented for loader validation and docs. CLI error
    normalization remains tracked separately.

- [x] Preserve exact task-description text in problem-contract hardening.
  - Evidence: task-description validation now rejects whitespace-only files,
    but the loader stores `task_path.read_text(...).strip()` as the task text.
    That silently removes leading/trailing spaces and blank lines before prompt
    construction, unlike the current context-file path which preserves decoded
    text whitespace exactly.
  - Required result: keep non-empty validation while preserving the exact task
    file contents used for prompts/provenance, document the policy in
    problem-format docs, and test Markdown/fenced/indented task descriptions.
  - Status: implemented. The loader preserves decoded task text exactly and
    validates non-empty content separately; problem-format docs and loader
    tests cover the policy.

- [x] Add invalid task-description encoding diagnostics to operational
  maturity.
  - Evidence: invalid task objective files are task-setup failures and should
    report the offending path through the same startup diagnostics path as
    empty tasks, missing validators, no seeds, and semantic metrics errors.
  - Current evidence: a local CLI proof with invalid UTF-8 in
    `task_description.txt` exited with a raw codec message and no path; a
    direct loader proof raised raw `UnicodeDecodeError`.
  - Required result: catch task-description UTF-8 decode failures, convert them
    to path-aware problem-load diagnostics before artifact/provider/evaluator
    work, and add CLI plus loader regression tests.
  - Status: implemented. Invalid UTF-8 in `task_description.txt` now produces a
    path-aware problem-load diagnostic and is covered by loader and CLI tests.

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

- [x] Add syntactically invalid metrics-file diagnostics to operational
  maturity.
  - Evidence: invalid metric files are task-setup failures and should be
    reported with the same user-facing startup diagnostics as missing
    validators, empty tasks, no seeds, semantic metric-schema errors, and
    context-manifest schema errors.
  - Current roadmap gap: the implemented CLI problem-load normalization covers
    `FileNotFoundError` and `ValueError` loader failures, but not PyYAML parse
    exceptions from `metrics.yaml`. A local temp CLI proof with `metrics.yaml`
    set to `metrics: [` produced no command output and surfaced raw
    `ParserError`.
  - Required result: add parser/decode diagnostics for metric files, keep them
    ordered before run-directory cleanup/provider construction/evolution, and
    add CLI regression coverage for syntactically invalid and invalidly encoded
    `metrics.yaml`.
  - Status: implemented. Metrics-file UTF-8 decode and YAML parser failures now
    become path-aware loader errors, and CLI regression coverage proves they
    are normalized before `evolve()` is called.

- [x] Add duplicate-YAML-key diagnostics to setup hardening.
  - Evidence: task setup and runtime configuration need deterministic,
    reproducible semantics before any AlphaEvolve-style run begins.
  - Current roadmap gap: config, metrics, and context diagnostics track
    malformed YAML, invalid encodings, and schema errors, but not duplicate
    mapping keys that PyYAML silently resolves with last-value-wins behavior.
    Local proofs showed duplicate `metrics.yaml` bounds changed the primary
    metric range, duplicate `config.yaml` `max_generations` changed the run
    budget, and duplicate `context.yaml` `include` keys changed which context
    file entered prompts.
  - Required result: reject duplicate mapping keys in problem-local YAML setup
    files with path-aware diagnostics and tests ordered before run artifacts,
    provider construction, evaluator work, or prompt-context rendering.
  - Status: implemented. Metrics, config, and context manifest YAML now share a
    duplicate-key rejecting loader, with tests proving path-aware startup or
    problem-load diagnostics.

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

- [x] Define validation order for CLI overrides versus invalid config files.
  - Previous evidence: `docs/configuration.md` said configuration is assembled
    from defaults, optional `config.yaml`, then CLI overrides. In code,
    `_build_config()` validated `Config(**cfg)` before applying CLI arguments.
    Local proofs showed `config.yaml` `max_generations: -1` still failed even
    when `--max-generations 5` was supplied, and `backends: []` still failed
    even when `--backends ollama:llama3` was supplied.
  - Roadmap gap: precedence tests proved selected valid config values could be
    overridden, but not whether higher-precedence CLI values were allowed to
    correct lower-precedence invalid fields.
  - Required result: either assemble raw defaults/config/CLI into one effective
    config and validate once, or document and test fail-fast validation of
    lower-precedence config files before CLI overrides are considered.
  - Status: implemented. `_build_config()` now validates the final merged
    effective config after CLI overrides. CLI tests cover replacing invalid
    `max_generations` and `backends` values from `config.yaml`.

- [x] Add evaluator metric-contract validation to the backlog.
  - Evidence: AlphaEvolve Section 2.1 treats `evaluate` as returning scalar
    metrics, while LibreEvolve currently validates only enough of the result to
    compute primary fitness.
  - Current roadmap gap: evaluation hardening covered cascades and artifacts
    but not schema enforcement against `metrics.yaml`.
  - Required result: keep metric schema validation on the roadmap because
    multi-objective search depends on trustworthy metric vectors.

- [x] Narrow roadmap "strict scalar validation" around reserved validity.
  - Roadmap evidence: `ROADMAP.md` current-state text says LibreEvolve has
    "strict scalar evaluator-output validation against `metrics.yaml`" in the
    Current State section.
  - Previous evidence: scalar numeric validation was strict for declared
    non-`is_valid` metrics, but `is_valid` could still be declared as the
    primary `metrics.yaml` metric and used as normalized fitness. A local proof
    loaded a problem whose only metric was
    `{"name": "is_valid", "primary": true, "bounds": [0, 1]}`; the loader
    accepted `primary_metric == "is_valid"` and
    `fitness_from_metrics({"is_valid": True}) == 1.0`.
  - Required result: either implement the reserved `is_valid` policy first, or
    update roadmap wording so strict scalar validation does not imply validity
    and optimization metrics are fully separated.
  - Status: implemented in code. The loader now reserves `is_valid` outside
    `metrics.yaml`, bundled examples declare only scalar optimization metrics,
    and evaluator output still requires boolean `is_valid`.

- [x] Add metric primary-flag type validation to schema hardening.
  - Evidence: the primary metric controls normalized fitness and archive
    performance. `_validate_metric_schema()` currently treats
    `metric.get("primary")` by truthiness instead of requiring a boolean. A
    local proof accepted `primary: "false"` and selected that metric as
    primary; `primary: 1` was also accepted.
  - Current roadmap gap: metric schema validation work covers names,
    directions, duplicate names, multiple primaries, unsupported fields, and
    bound ordering, but not the type of the `primary` flag itself.
  - Required result: reject non-boolean `primary` values in `metrics.yaml`,
    document absent-as-false behavior, and test string/integer primary values
    before claiming strict metric schema validation.
  - Status: implemented. `load_problem()` schema validation now requires a
    present `primary` field to be boolean, leaves absent values false by
    convention, and regression tests cover string/integer rejection.

- [x] Add evaluator-output range enforcement or explicit clamp diagnostics.
  - Evidence: `metrics.yaml` bounds are now strictly validated as schema, and
    `Problem.normalize_metric()` uses those bounds for primary fitness and
    archive performance. `_validate_metrics()` still accepts any finite numeric
    evaluator value for a declared metric, even if it is outside the declared
    range. A local proof with `bounds: [0, 1]` and validator output
    `{"score": 999, "is_valid": True}` returned a valid result with
    `metrics.score == 999.0`, no error, and clamped normalized fitness `1.0`.
  - Current roadmap gap: roadmap wording about metric direction/bounds can be
    read as bound-honoring end to end, but current code only validates bound
    shape and clamps fitness; it does not diagnose out-of-range measurements or
    preserve clamp provenance for selection/search analysis.
  - Required result: decide whether declared bounds are hard validity
    constraints or normalization hints, then implement and document that policy
    across evaluator diagnostics, MAP-Elites/archive scoring, multi-objective
    policy, and tests for primary/secondary/minimize metrics.
  - Status: implemented as normalization-hint diagnostics. Evaluator results
    retain raw out-of-range metrics and add
    `metadata.metric_bound_diagnostics`; docs now describe the policy, and
    evaluator tests cover primary, secondary, minimize, and staged sample
    cases.

- [x] Add degenerate metric-bound validation to the backlog.
  - Evidence: `metrics.yaml` bounds drive primary fitness normalization and
    MAP-Elites performance coordinates, and `_validate_metric_schema()`
    previously accepted finite zero-width or inverted ranges.
  - Current roadmap gap: current-state bullets said strict scalar validation
    and metric direction/bounds normalization, but did not call out invalid
    bound ordering.
  - Status: implemented. Problem loading now rejects zero-width and inverted
    metric bounds with strict `[lo, hi]` ordering before metrics feed archive
    or multi-objective policy.

- [x] Add full-workspace export and resume coverage to candidate fidelity.
  - Evidence: AlphaEvolve evolves full files/codebases, while a primary-file
    `best.py` artifact is insufficient for a multi-file candidate. The CLI now
    also writes `best_workspace/` with the complete best candidate file set.
  - Current roadmap gap: candidate workspace work now explicitly includes
    preserving full workspace artifacts and migration/resume coverage.
  - Required result: keep export/resume as part of workspace fidelity, not only
    runtime hardening.

- [x] Add run-directory collision policy to resumability work.
  - Evidence: `ProgramDatabase.log()` appends `history.jsonl` and
    `PromptDatabase` appends `prompt_history.jsonl`, while `manifest.json` is
    overwritten for the same run directory.
  - Status: implemented for fresh-run collision safety. The default policy
    fails if the target directory already contains known run artifacts;
    explicit `overwrite` removes only known run artifacts before a new run.
    `manifest.json` records `run_id` and the effective collision policy.
  - Remaining roadmap gap: this is not resume; saved archive/controller state,
    parent-run relationships, deterministic replay ids, and evaluator-code
    provenance remain tracked under resumability/reproducibility.

- [x] Add safe run-id grammar to reproducibility/provenance work.
  - Status: implemented. Configured `run_id` values must match
    `[A-Za-z0-9][A-Za-z0-9_.-]{0,127}`. Direct `Config` and CLI/YAML startup
    reject control characters, assignment syntax, leading punctuation, and
    overlong ids before `evolve()` or manifest writes; docs describe the
    manifest-safe identifier policy.

- [x] Define unknown-file policy for fresh run directories.
  - Status: implemented. Runtime startup preserves unknown immediate entries
    under both `fail` and `overwrite`, treats them as outside the run-owned
    artifact contract, and records `run_directory.foreign_entries` in
    `manifest.json` with entry type plus SHA-256 of the entry name. Tests cover
    unknown files/directories and overwrite with preserved foreign entries.

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

- [x] Add reserved/ambiguous run-name validation to runtime hardening.
  - Evidence: current path confinement prevents directory traversal, but the
    scalar run-name grammar is not yet fully host-safe. A local proof showed
    `Config(problem_name="CON")`, `"NUL"`, `"COM1"`, `" run"`, `"run "`, and
    `"run."` all validate successfully.
  - Status: implemented. The enforced run-name grammar now rejects Windows
    reserved device names with or without extensions, leading/trailing
    whitespace, trailing dots, path separators, invalid filename characters,
    control characters, and non-NFC Unicode spellings across direct config and
    CLI `--run-name`; docs describe the boundary before claiming portable
    run-directory identity.

- [x] Add per-artifact link checks to overwrite cleanup hardening.
  - Status: implemented. Overwrite startup now checks every known artifact
    targeted by cleanup and rejects symlinks or Windows junctions before
    deleting any artifact. Tests cover symlink-capable platforms and Windows
    junctions, and docs state that linked known artifacts are rejected rather
    than followed, unlinked, or cleaned.

- [x] Add seeded replay determinism to reproducibility work.
  - Evidence: `Config.seed` seeds Python `random`, database-created prompt ids
    are deterministic, initial prompt variants are selected in config order,
    and loop-created candidate ids are deterministic. The remaining
    seeded-replay gaps are RNG restore, archive sampling replay, and provider
    nondeterminism.
  - Current roadmap gap: reproducibility work covered manifests, hashes,
    budgets, and resume state, but not stable seeded identifiers or RNG
    replay.
  - Required result: track deterministic run/candidate/prompt id policy, RNG
    state capture, provider nondeterminism boundaries, and tests proving
    stable local replay metadata.

- [x] Add evolve-block and skeleton/codebase support to near-term architecture
  alignment.
  - Evidence: AlphaEvolve Section 2.1 defines an input API with marked
    evolvable blocks inside a larger code skeleton.
  - Current roadmap gap: near-term item 1 only mentions `primary_bounds`,
    README audit, and tests (`ROADMAP.md:25-32`).

- [x] Add malformed evolve-block marker validation to candidate fidelity.
  - Evidence: malformed evolve-block layouts can weaken skeleton preservation
    unless mutation rejects them before deciding whether a file is fully
    evolvable. `validate_evolve_blocks()` now fails closed during mutation for
    missing end markers, orphan end markers, nested blocks, invalid names, and
    duplicate block names.
  - Current roadmap gap: candidate fidelity listed marker support but not
    marker-structure validation, even though skeleton preservation depends on
    rejecting malformed task specifications.
  - Required result: keep marker validation on the roadmap alongside
    workspace/codebase fidelity.

- [x] Add seed-time evolve-block marker prevalidation to candidate fidelity.
  - Evidence: ROADMAP near-term candidate work says seed evolve-block markers
    should be prevalidated during problem load, but the loader still accepts
    malformed seed markers.
  - Current evidence: a local proof created `initial_programs/seed.py` with
    `# EVOLVE-BLOCK-START core` and no matching end marker; `load_problem()`
    loaded it as a normal initial workspace.
  - Required result: move evolve-block marker validation into seed loading for
    both single `.py` seeds and workspace seed files, and keep mutation-time
    validation as a defense-in-depth check.
  - Status: implemented and reflected in ROADMAP current state. Seed loading
    now validates marker structure for top-level `.py` seeds and files inside
    seed workspaces, while mutation-time validation remains in place.

- [x] Add exact evolve-block marker grammar to candidate fidelity.
  - Evidence: skeleton preservation depends on task markers being exact
    declarations, not prefix matches.
  - Current evidence: `_parse_evolve_blocks()` uses prefix matching for start
    markers. A local proof with `# EVOLVE-BLOCK-STARTED` plus a normal end
    marker produced a valid block named `ED` instead of an invalid-marker
    diagnostic.
  - Required result: define the evolve-block marker grammar in the roadmap,
    reject marker-looking prefixes, and cover exact/no-name/named markers plus
    typo prefixes in tests.
  - Status: implemented and documented for mutation validation. Start markers
    now require the exact token with no suffix or a whitespace-separated name;
    prefix typos return `invalid_start_marker`, with focused candidate tests.
    Load-time seed marker validation remains open separately.

- [x] Add source-aware evolve-block marker parsing to candidate fidelity.
  - Evidence: exact marker tokens still do not prove source-aware task
    boundaries. `_parse_evolve_blocks()` scans stripped source lines, so a
    Python triple-quoted string containing `# EVOLVE-BLOCK-START literal` and
    `# EVOLVE-BLOCK-END` was treated as a real evolvable block. A local proof
    then rejected a diff against code outside the string and allowed mutation
    of the string body.
  - Required result: make marker parsing Python-comment aware, provide an
    escape/literal mechanism, or document marker-like strings/docstrings as an
    unsupported candidate shape. Add loader and mutation tests for comments,
    module docstrings, triple-quoted literals, and workspace files.
  - Status: implemented and tested. Evolve-block parsing now considers only
    Python comment tokens that appear as standalone comment lines, preserving
    marker-like strings and docstrings as ordinary candidate text. Regression
    tests cover triple-quoted literals, module docstrings, full-mode behavior
    when all markers are literal text, and workspace seed loading.

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

- [x] Add POSIX absolute-path rejection to candidate path hardening.
  - Roadmap evidence: path grammar hardening now says unsafe paths are
    rejected, but the implementation accepts leading-slash paths by stripping
    the slash.
  - Current evidence: `/abs.py` normalizes to `abs.py`, `//pkg/mod.py`
    normalizes to `pkg/mod.py`, and `<<<FILE /new.py ... >>>FILE` creates
    `new.py` without an error.
  - Required result: keep the candidate path grammar strictly relative across
    loader, mutation envelopes, topology commands, and materialization helpers.
  - Status: implemented and tested. Leading-slash POSIX absolute paths and
    UNC-style leading-backslash paths are rejected by the shared candidate path
    normalizer, with tests covering direct normalization, file-section edits,
    move targets, and primary-file topology commands.

- [x] Add control-character and host-invalid path rejection to candidate path
  hardening.
  - Evidence: `normalize_candidate_path()` accepts strings containing ASCII
    control characters. A local proof with `CandidateWorkspace({"bad\nname.py":
    "x=1\n"}, "bad\nname.py")` passed construction and failed later in
    `materialize()` with `OSError: [Errno 22] Invalid argument` on Windows.
  - Required result: make path validation reject control characters and
    host-invalid/reserved components before workspace construction, mutation
    application, evaluation, or best-artifact export; add platform-aware tests
    and diagnostics so invalid generated codebase paths become structured
    candidate failures.
  - Status: implemented and tested. Candidate path normalization now rejects
    ASCII control characters, DEL, host-invalid wildcard/quote/pipe characters,
    Windows reserved device names, leading/trailing spaces, and trailing dots
    before workspace construction or mutation application. Tests cover direct
    normalization plus mutation-envelope diagnostics without partial apply.

- [x] Add candidate path-collision handling to candidate fidelity.
  - Evidence: path grammar hardening rejects unsafe paths, and
    `CandidateWorkspace` now rejects distinct raw inputs that normalize to the
    same candidate path. Materialization now preflights case-folded host paths
    before writing, so case-only variants fail closed on case-insensitive
    filesystems. Duplicate file edit sections now fail before partial
    application.
  - Current roadmap gap: workspace fidelity covered safe path grammar but not
    whether the candidate file set remains one-to-one after normalization and
    host filesystem materialization.
  - Required result: continue tracking Unicode normalization and
    topology-operation collision policy with tests for loader and mutation.

- [x] Add mutation-envelope diagnostics for partial parses.
  - Evidence: file and block mutation envelopes now validate unmatched,
    orphaned, nested, empty-name, invalid-name, and unsafe-path sections before
    partial edits are applied.
  - Current roadmap gap: path grammar hardening covered valid filename support,
    but not detection of unmatched `<<<FILE`/`<<<BLOCK` spans that represent
    intended edits.
  - Required result: parse envelopes as a full document, reject or log
    malformed sections, and test mixed valid plus malformed file/block
    responses.

- [x] Add duplicate block-section detection to mutation-envelope work.
  - Evidence: `_apply_full_replacement()` previously stored named block
    sections in a dict, so duplicate `<<<BLOCK a ... >>>BLOCK` sections
    silently overwrote earlier bodies. A local proof returned no error and
    applied only the later duplicate block body.
  - Current roadmap gap: envelope diagnostics covered malformed spans but not
    ambiguous duplicate target sections inside an otherwise well-formed
    multi-block full replacement.
  - Status: implemented. Duplicate block-section names now return
    `malformed_block_sections:duplicate_name` before replacement, with tests
    covering duplicate names in full-block replacements.

- [x] Add workspace file-topology mutation support to candidate fidelity.
  - Evidence: `apply_workspace_mutation()` can edit existing files and create
    unknown files in `full` mode; command file sections now support deleting,
    renaming, moving, and changing the primary file in a candidate workspace.
  - Current roadmap gap: workspace fidelity covered file sets, path grammar,
    and exports, but not normal codebase topology changes.
  - Status: implemented with path validation, history/export persistence through
    `Program.files` and `primary_file`, mutation tests, and backward
    compatibility for current file-section edits.

- [x] Add strict primary-file identity validation to candidate fidelity.
  - Evidence: workspace candidates now persist `primary_file`, and that field
    controls the compatibility `code` view used by prompts, legacy validators,
    history, and `best.py`.
  - Current evidence: constructing
    `CandidateWorkspace(files={"helper.py": "x=1\n"}, primary_file="missing.py")`
    silently rewrites `primary_file` to `helper.py`. Mutation-time
    `PRIMARY missing.py` is rejected, so constructor/deserialization semantics
    are looser than topology mutation semantics.
  - Required result: reject missing explicit primary files at load/deserialize
    boundaries or require a documented fallback mode; test current seed
    directories, empty defaults, and future resume/history replay paths.
  - Status: implemented and tested. `CandidateWorkspace` now rejects non-empty
    file sets whose declared `primary_file` is absent. Empty workspace defaults
    still create `main.py`, and `from_dict()` applies the same validation.

- [x] Add strict serialized-workspace schema validation to candidate fidelity.
  - Evidence: workspace candidates are persisted as `files` plus
    `primary_file`, and future resume/history replay depends on those records
    reconstructing the same source tree.
  - Current evidence: `CandidateWorkspace.from_dict()` stringifies file keys,
    file contents, and `primary_file` instead of validating their types. A
    local proof accepted list-valued file content as the source text
    `"['not', 'text']"` and integer path data as `"1"`; a non-mapping `files`
    value raised an unstructured `AttributeError`. Direct
    `CandidateWorkspace(files={"main.py": 123})` stores an integer content
    value and only fails later during materialization with raw `TypeError`.
  - Required result: define and enforce the serialized workspace schema before
    claiming codebase-candidate resumability, and apply the same typed
    workspace invariants to direct constructors, with tests for malformed
    paths, contents, primary file values, and history/resume replay records.
  - Status: implemented and tested. Workspace records must be mappings with
    string file paths, string file contents, and string primary files;
    malformed records are rejected instead of coerced.

- [x] Add `Program.code` / workspace consistency to candidate fidelity.
  - Evidence: workspace candidates have both a legacy `Program.code` field and
    a `files`/`primary_file` file-set representation. They can currently
    disagree. A local proof created
    `Program(code='x = "legacy"\n', files={"main.py": 'x = "workspace"\n'},
    primary_file="main.py")`; `program.code` and `program.workspace().code`
    returned different text. The CLI best-artifact writer then wrote `best.py`
    from the legacy code field and `best_workspace/main.py` from the workspace
    field set, producing contradictory artifacts for one candidate.
  - Status: implemented. The file set is canonical for workspace-backed
    `Program` objects, and the primary-file compatibility view is normalized
    before logging, prompt rendering, compact `show`, and best-artifact export.
    Focused tests cover those boundaries.

- [x] Add workspace execution import/cwd fidelity to candidate fidelity.
  - Evidence: `CascadeEvaluator._run_subprocess()` now materializes the
    candidate workspace, runs the validator with that root as `cwd`, adds the
    candidate root to `sys.path`, and passes it as `workspace_path`.
  - Current roadmap gap: workspace fidelity covered file sets, fixtures, and
    exports, but not whether validators can execute evolved codebases with
    normal local imports and relative paths.
  - Required result: define/test evaluator workspace execution semantics for
    `cwd`, import path, environment, package/module entrypoints, and relative
    artifacts.

- [x] Add problem-local evaluator import semantics to evaluation hardening.
  - Evidence: `_RUNNER` still loads `validate.py` by file path from a temporary
    runner, but now adds `validate_path.parent` to `sys.path`, so sibling
    validator helper modules are supported by default.
  - Current roadmap gap: workspace execution work covered candidate-root
    imports, but not problem-local evaluator-code imports and relative data.
  - Required result: define validator module/package loading, problem-dir
    `cwd` or `PYTHONPATH` policy, evaluator helper/data provenance, and tests
    for sibling imports and package validators.

- [x] Add validator contract preflight before artifact mutation.
  - Previous evidence: `load_problem()` required `validate.py` to exist but did
    not verify that it imported cleanly or exposed a callable `evaluate` with a
    supported signature before the CLI prepared the run directory. A local
    proof with a missing `evaluate` function and `--overwrite` replaced the
    old `history.jsonl`, wrote a new manifest/history row, recorded
    `subprocess_error` / `returncode_1`, and only then failed with
    `Evolution produced no valid programs`.
  - Required result: validate direct and staged evaluator entrypoints during
    startup, before overwrite cleanup or manifest/history writes; provide
    user-facing diagnostics for missing `evaluate`, import errors, syntax
    errors, and signatures that cannot bind to the current positional dispatch,
    with regression tests for existing run artifact preservation.
  - Status: implemented. CLI startup now preflights default and staged
    evaluator contracts before overwrite cleanup, with tests for missing
    `evaluate`, import errors, syntax errors, unbindable signatures, staged
    validators, and artifact preservation under `--overwrite`. Fixed-shape
    rejection for variadic, async, generator, and extra-parameter validators is
    tracked separately.

- [x] Add multi-objective evaluation and metric-vector storage.
  - Evidence: AlphaEvolve Section 2.4 explicitly supports optimizing multiple
    user-provided scores.
  - Current roadmap gap: evaluator metadata is only a mid-term item
    (`ROADMAP.md:68-74`) and does not call out multi-objective archive,
    sampling, prompt, or logging behavior.

- [x] Add configurable evaluation cascades.
  - Evidence: AlphaEvolve Section 2.4 describes user-specified ensembles of
    test cases with increasing difficulty.
  - Current roadmap gap: `ROADMAP.md:68-74` mentions diagnostics and metadata,
    but not staged evaluator definitions, thresholds, budgets, or parallel
    stages.

- [x] Add evaluator seed semantics to cascade reproducibility work.
  - Evidence: roadmap and docs describe staged validators with seeded samples,
    but current seeds are only passed through `stage["seed"]`. A local proof
    configured two samples with identical `seeds: [123, 123]`; a validator that
    returned `random.random()` produced different scores while both sample
    metadata still showed `seed=123`.
  - Required result: decide whether stage seeds should control validator
    process RNG/environment state or remain validator-managed metadata, then
    document the boundary and add reproducibility tests for repeated seeded
    samples and retries.
  - Status: implemented as operational stage seeding. For non-null stage
    seeds, LibreEvolve records a deterministic `stage["rng_seed"]`, sets
    subprocess `PYTHONHASHSEED`, and seeds Python `random` plus NumPy before
    validator import. README, configuration docs, and run-artifact docs
    describe the current contract.

- [x] Add evaluator artifact copy-out to evaluation hardening.
  - Evidence: `CascadeEvaluator._run_subprocess()` materializes the candidate
    in a `TemporaryDirectory`, runs the validator with that directory as `cwd`,
    and deletes the directory after returning metrics/stdout/stderr. Files
    written by validators are not copied into run artifacts.
  - Current roadmap gap: evaluation hardening mentioned artifacts broadly but
    did not identify the temporary-workspace data-loss mechanism or require
    stage/sample/attempt artifact provenance.
  - Status: implemented as opt-in artifact copy-out from the candidate
    workspace. Top-level and per-stage include/exclude patterns, size/count
    limits, text-artifact redaction policy, copied file hashes, skipped-file
    reasons, stage/sample/attempt provenance, and run-directory artifact paths
    are recorded, with tests proving files are retained after subprocess
    cleanup, stage overrides are honored, and secret-like text artifacts are
    redacted by default.
  - Remaining gap: files outside the candidate workspace are not retained.

- [x] Add evaluator-stage numeric validation to config hardening.
  - Evidence: `Config.validate()` now checks evaluator-stage `samples`,
    `retries`, `timeout_sec`, `min_score`, `seeds`, unsupported fields, and
    explicit sample/seed count mismatches before `CascadeEvaluator` is built.
  - Status: implemented with config tests.

- [x] Add evaluator-stage metadata type validation to config hardening.
  - Evidence: stage context is serialized to JSON before the validator
    subprocess starts. `Config.validate()` now requires configured stage names
    and `validate_path` entries to be non-empty strings and requires `seeds[]`
    to be JSON-safe scalar values.
  - Required result: normalize or reject non-JSON stage metadata at config
    construction/config-file load, document the accepted stage-context schema,
    and add tests for programmatic configs, YAML configs, manifests, and
    validator-visible stage context.
  - Status: implemented at config construction/startup with focused tests.

- [x] Add unique evaluator-stage identifiers to cascade hardening.
  - Evidence: configured stages currently use `stage.get("name",
    f"stage_{index}")` as the stage record name. `Config.validate()` now
    rejects blank and duplicate configured names before evaluator construction,
    with config tests covering both cases.
  - Current roadmap gap: cascade hardening covers numeric fields and JSON-safe
    metadata, but not uniqueness of the identifiers used by history records,
    prompt feedback, artifacts, and future per-stage accounting.
  - Required result: define stage identity separately from display labels or
    require non-empty unique normalized names, then test blank-name and
    duplicate-name rejection plus sampled-stage suffix behavior across
    evaluation history and artifacts.
  - Status: implemented by requiring non-empty unique configured names.
    Separate display labels/stage ids and richer artifact/budget identity
    remain future work.

- [x] Add top-level evolution/population numeric validation to config
  hardening.
  - Evidence: `Config.validate()` now checks generation counts, inspiration
    counts, timeouts, exploration ratios, island counts, migration settings,
    MAP-Elites bins, elite archive sizes, and ensemble coefficients before
    `evolve()` starts.
  - Status: implemented with config range tests.

- [x] Add zero-ratio migration semantics to population config work.
  - Evidence: `Config.validate()` accepts `migration_ratio=0.0`, while
    `IslandModel.migrate()` previously rounded migrant count with
    `max(1, ...)`, so zero still migrated one elite.
  - Current roadmap gap: numeric validation covered bounds checking but not the
    behavioral meaning of the lower bound for migration.
  - Status: implemented. Zero ratio selects no migrants; positive ratios still
    round up to one migrant per non-empty island when migration runs.

- [x] Add async/distributed controller and worker architecture.
  - Evidence: AlphaEvolve Section 2.6 describes an asynchronous pipeline with a
    controller, LLM samplers, and evaluation nodes optimized for throughput.
  - Current roadmap gap: the roadmap mentions resumable runs and benchmark
    scripts (`ROADMAP.md:76-81`) but not async sampling/evaluation or worker
    queues.

- [x] Add prompt-sampler work: templates, stochastic formatting, explicit
  context, rendered evaluator feedback, and meta-prompt evolution.
  - Evidence: AlphaEvolve Section 2.2 lists these as prompt sampling
    capabilities.
  - Current roadmap gap: prompt evolution is absent; documentation work
    (`ROADMAP.md:50-55`) and search improvements (`ROADMAP.md:83-88`) are too
    broad to cover it.

- [x] Add prompt-template validation and context summarization hardening.
  - Evidence: AlphaEvolve prompt customization includes stochastic formatting,
    explicit context, relevant literature, and co-evolved prompts.
  - Current roadmap gap: after the implementation pass, the roadmap now tracks
    stricter configured and mutated prompt-template placeholder validation,
    deterministic PDF/text context ingestion, and richer prompt-fitness/
    ablation reporting.
  - Required result: ensure prompt/context work covers malformed evolved
    templates, malformed configured variants, and large context sources, not
    only happy-path template selection.

- [x] Add semantic placeholder-retention rules to prompt-template validation.
  - Evidence: AlphaEvolve-style meta-prompt evolution should preserve the
    prompt channels required for candidate generation while improving wording
    or context policy.
  - Previous evidence: `PromptDatabase.mutate()` validated syntax and known
    placeholders, but the only required placeholder was `{task}`. A local proof
    accepted an evolved template of `Task only: {task}`, dropping
    `{parent_code}` and `{mutation_instructions}` despite the meta-prompt
    instruction asking the LLM to keep placeholders intact.
  - Required result: extend prompt validation with mode-specific required
    placeholder/channel sets, quarantine semantic regressions, and cover
    configured variants plus evolved templates in tests.
  - Status: implemented for evolved children by comparing parent and child
    placeholder sets in `PromptDatabase.mutate()`. A child may add placeholders,
    but it cannot drop placeholders used by its parent; rejected semantic
    regressions are quarantined and penalized through the same invalid-mutation
    path.

- [x] Add render-time format-spec validation to prompt-template hardening.
  - Evidence: previous prompt-template validation checked placeholder names but
    not whether format specs work with the actual render values. A local proof
    accepted `Task formatted numeric: {task:.2f}` in
    `validate_prompt_template()` and `PromptDatabase`, then
    `PromptSampler.build()` raised `ValueError: Unknown format code 'f' for
    object of type 'str'` at render time.
  - Previous roadmap gap: prompt-template validation work covered malformed
    fields, unknown placeholders, and semantic channel retention, but not
    type-compatible formatting for configured/evolved templates.
  - Required result: reject incompatible format specs at config/meta-prompt
    validation time through per-field rules or dry-run rendering, and test
    configured variants, prompt database seeds, and mutated templates.
  - Status: implemented with dry-run render validation. Tests cover
    incompatible string and numeric format specs, prompt database seed
    construction, and invalid mutated templates being quarantined before use.

- [x] Add atomic rejected-template persistence to prompt-archive hardening.
  - Evidence: invalid evolved prompt templates are supposed to be auditable in
    `prompt_history_invalid.jsonl`, but rejection persistence is not atomic
    with parent prompt-program state changes. A local proof called
    `PromptDatabase.mutate()` with an invalid template and metadata containing
    a Python `set`; `StrictJsonlError` was raised, no invalid-history record
    was written, and the parent prompt program still had `reward_sum == -1.0`.
  - Previous roadmap gap: prompt work covered template validation, rejection
    accounting, and strict JSONL writers, but not rollback/metadata validation
    for failed rejection-event persistence.
  - Required result: validate rejection metadata before state mutation, persist
    invalid-template events durably or roll back all parent penalties, and add
    tests for non-JSON meta-prompt rejection metadata.
  - Status: implemented. Invalid-template rejection records are persisted or
    diagnostically quarantined before parent prompt penalties are applied.
    Invalid rejection metadata leaves parent selection state unchanged, and
    parent state is rolled back if the penalty event write fails.

- [x] Add context-source manifest/provenance work.
  - Evidence: `_load_context_files()` reads only immediate files in `context/`
    into a filename-to-text dictionary and does not preserve hashes, recursive
    paths, PDF page spans, extraction metadata, or include/exclude selection.
  - Current roadmap gap: prompt/context work covered summarization and ranking
    but not source-selection provenance needed to reproduce AlphaEvolve-style
    task context.
  - Required result: track recursive source selection, context manifests,
    source hashes, extraction diagnostics, page/span citations, and prompt/run
    provenance.

- [x] Remove implemented context-source manifest work from open roadmap
  wording.
  - Previous roadmap evidence: `ROADMAP.md` said to "Add context-source
    manifests with recursive selection, include/exclude rules, source hashes,
    extraction diagnostics, and page/span citations" under prompt/context work.
  - Current evidence: `load_problem()` already supports recursive
    `.txt`/`.md`/`.py`/`.pdf` context ingestion, optional `context.yaml` /
    `context.yml` include/exclude rules, per-source SHA-256, extraction
    status, excerpt spans, and PDF page metadata for selected sources in
    `context_sources`. The remaining gap is not the existence of source
    records; it is recording the selection policy itself, skipped/excluded
    source diagnostics, better summarization/ranking, and prompt-budget
    packing. `_load_context_manifest()` now rejects unsupported typo keys such
    as `includes:` and simultaneous `context.yaml` / `context.yml` manifests
    before source selection, with loader/CLI coverage for those startup
    diagnostics. PDF citation spans were also imprecise: `_read_pdf_text()`
    stored full-document page ranges before first-character truncation, and
    `_render_context_header()` did not render page metadata in the prompt
    citation header.
  - Required result: update ROADMAP so the open item is narrowed to the real
    remaining work, such as context-manifest file provenance, effective
    include/exclude policy, skipped-source diagnostics, semantic ranking/summarization,
    global prompt budgets, artifact-content retrieval, exact PDF/page-span
    citations, and docs/tests for current context knobs.
  - Status: completed. `ROADMAP.md` current-state now mentions recursive
    context ingestion, context-manifest include/exclude rules, hashes,
    extraction spans, and bounded prompt rendering. The prompt/context
    near-term bullets now focus on effective context-selection manifests,
    skipped-source diagnostics, context-manifest file hashes, deterministic
    summarization/ranking, global prompt budgets, and exact PDF page/span
    citations. Subsequent implementation added `problem.context_policy` and
    PDF excerpt page-span citations, leaving semantic ranking/summarization,
    global prompt budgets, and artifact-content retrieval as the larger
    roadmap gaps.

- [x] Refresh ROADMAP prompt/context bullets after context-policy and PDF-span
  implementation.
  - Roadmap evidence: `ROADMAP.md` still says to "Persist effective
    context-selection manifests, skipped-source diagnostics, context-manifest
    file hashes, and exact page/span citations for PDF-derived context" under
    future prompt/context work.
  - Current evidence: `load_problem()` now persists `problem.context_policy`
    with manifest file hash/bytes, effective include/exclude/max-char policy,
    selected/skipped counts, and hashed skipped-source diagnostics. PDF context
    metadata records `excerpt_pages` and `excerpt_page_spans` for the actual
    rendered excerpt after first-character truncation, and loader tests cover
    context policy, skipped diagnostics, and PDF excerpt spans.
  - Required result: narrow the ROADMAP bullet to the remaining work only:
    semantic ranking/summarization, global prompt packing/accounting,
    artifact-content retrieval, and any citation precision gaps that are still
    actually missing. Avoid listing implemented context-policy provenance as
    future work.
  - Status: ROADMAP prompt/context work no longer lists context-policy
    manifests or persisted PDF page spans as future work. It now names
    ingestion resource limits. Prompt-visible citation precision, context
    source-label safety, hidden-source policy, extraction failure handling,
    unmatched include diagnostics, and context-manifest pattern grammar are
    tracked as completed items below.

- [x] Track prompt-visible PDF citation precision separately from persisted
  page-span metadata.
  - Roadmap evidence: ROADMAP current-state says PDF context ingestion has
    extraction spans, while future work still mentions exact page/span
    citations.
  - Current evidence: source metadata now records `excerpt_page_spans`, but
    `_render_context_header()` compresses `excerpt_pages` to a first-last page
    range and ignores the detailed spans. A local proof with non-contiguous
    `excerpt_pages=[1, 3]` rendered `pages=1-3`, so prompt-visible citations
    can be coarser than the persisted provenance.
  - Required result: make ROADMAP distinguish persisted PDF page-span
    provenance from prompt-visible citation rendering, and keep exact
    non-contiguous page/span rendering in the prompt/context roadmap until it
    is implemented and tested.
  - Status: ROADMAP current state keeps persisted extraction/page-span
    provenance in the implemented area, while near-term prompt/context work now
    specifically calls for exact prompt-visible non-contiguous page/span
    rendering.

- [x] Implement exact prompt-visible PDF page/span citations.
  - Roadmap evidence: prompt/context roadmap previously tracked exact
    non-contiguous page/span rendering as separate work after persisted PDF
    page-span provenance.
  - Status: prompt context headers now render exact `page:start-end` spans from
    `excerpt_page_spans`, non-contiguous excerpt pages as grouped page lists,
    and coarse document-level ranges only when excerpt-specific metadata is
    unavailable. ROADMAP no longer lists this as future prompt/context work.
  - Verification: focused prompt/loader tests cover per-page span citations,
    non-contiguous page lists, and document-level fallback behavior.

- [x] Add secret-safe retention for context manifest patterns.
  - Evidence: context include/exclude patterns are persisted as run-selection
    provenance and can contain local labels that users may not expect to share
    with manifests or prompt-history consumers.
  - Status: context manifest include/exclude patterns are now safe
    grammar-constrained inputs: secret-like patterns are rejected before
    context selection and before `context_policy` persistence.
  - Verification: focused loader tests cover secret-like include and exclude
    patterns.

- [x] Add context source-label safety to prompt/context hardening.
  - Evidence: selected context source labels are prompt-visible and persisted
    as run provenance.
  - Status: selected context source labels are now rejected when they look
    secret-like, before prompt rendering or manifest persistence. ROADMAP
    prompt/context work no longer lists source-label safety as future work.
  - Verification: focused loader tests cover rejected secret-like selected
    source labels.

- [x] Add hidden explicit-context file selection policy.
  - Evidence: hidden context sources should not be accidental prompt/literature
    inputs merely because their extensions are supported.
  - Status: hidden context sources are skipped by default with
    `hidden_not_included` diagnostics and may be selected only by include
    patterns that explicitly contain a dot-prefixed path component. ROADMAP
    prompt/context work no longer lists hidden-source policy as future work.
  - Verification: focused loader tests cover default skip behavior, explicit
    opt-in, and broad wildcard includes.

- [x] Add explicit extraction-failure policy to context ingestion.
  - Evidence: failed explicit-context extraction should be visible in setup
    provenance without being presented to the LLM as usable context.
  - Status: failed text/PDF extraction and no-text PDFs now become skipped
    context diagnostics with `failed_extraction_count`, while usable selected
    context is counted separately. ROADMAP prompt/context work no longer lists
    selected-source extraction failures as future work.
  - Verification: focused loader tests cover invalid UTF-8, broken PDF, and
    no-text PDF diagnostics.

- [x] Add context-ingestion resource limits to prompt/context work.
  - Evidence: prompt/context roadmap work needs local context ingestion to be
    bounded before prompt construction.
  - Status: context manifests now support source-byte, total-byte, PDF-page,
    and PDF extracted-character budgets, with over-budget sources retained as
    skipped diagnostics. ROADMAP no longer lists context-ingestion resource
    limits as future prompt/context work.
  - Verification: focused loader tests cover text and PDF budget enforcement.

- [x] Add unmatched context-include diagnostics to prompt/context roadmap.
  - Roadmap evidence: context work now covers recursive selection,
    include/exclude manifests, skipped-source diagnostics, and provenance, but
    it does not require proving that each declared include pattern matched a
    source.
  - Current evidence: a local proof with `context.yaml` containing
    `include: ["missing.md"]` loaded successfully with no selected context.
    If the context directory contained only the manifest, `skipped_count` was
    also zero; if another file existed, it was marked `not_included`, but the
    unmatched `missing.md` pattern itself was not reported.
  - Required result: track include-pattern match counts, persist unmatched
    include diagnostics, and decide whether typos should fail problem loading
    before claiming context manifests make prompt context selection fully
    auditable.
  - Status: implemented as permissive setup diagnostics. The run context policy
    records `include_patterns` with match counts and `unmatched_includes`.
    ROADMAP/docs now distinguish these diagnostics from strict load failures.

- [x] Add context-manifest pattern grammar to prompt/context hardening.
  - Roadmap evidence: context manifests are now persisted as task provenance,
    but roadmap context work does not require validating the pattern language
    itself.
  - Current evidence: a local proof with `include` values `../secret/*.md`,
    `/absolute/*.md`, and `api_key=sk-proj_secret_1234567890\n*.md` loaded
    successfully and persisted those raw strings in
    `problem.context_policy.include`.
  - Required result: define allowed problem-relative glob syntax, reject
    absolute/traversal-looking and control-character patterns for both include
    and exclude rules, and document how unsafe or unmatched patterns are
    reported before context provenance is treated as robust.
  - Status: implemented. Context manifest include/exclude rules now require
    non-empty problem-relative glob patterns with `/` separators and reject
    traversal, absolute/drive-style roots, backslashes, and ASCII control
    characters. Unmatched safe include patterns remain manifest diagnostics.

- [x] Remove implemented context include/pattern diagnostics from open ROADMAP
  bullets.
  - Roadmap evidence: `ROADMAP.md` still grouped unmatched include diagnostics
    and unsafe context selectors with future prompt/context work.
  - Current evidence: `problem.context_policy.include_patterns` records
    include-pattern match counts, `unmatched_includes` records unmatched safe
    include patterns, and `_validate_context_patterns()` rejects traversal,
    absolute/drive-style, backslash, empty, and control-character include/
    exclude patterns. Source-label safety was later completed by rejecting
    selected context filenames containing secret-like text.
  - Required result: narrow the ROADMAP future bullet to unimplemented context
    work only: extraction-failure semantics and ingestion resource limits.
  - Status: ROADMAP prompt/context work no longer lists unmatched include
    diagnostics or unsafe manifest selectors as future work.

- [x] Add invalid context-manifest parse diagnostics to prompt/context
  hardening.
  - Evidence: `_load_context_manifest()` handles unsupported keys and duplicate
    manifest files with path-aware `ValueError`s, but it does not catch YAML
    parser or UTF-8 decoder failures. Local proofs with malformed
    `context.yaml` and invalid UTF-8 bytes raised raw `ScannerError` and
    `UnicodeDecodeError`, respectively.
  - Current roadmap gap: context-manifest hardening covers selection
    provenance and unmatched includes, but not syntax/encoding diagnostics at
    the manifest boundary.
  - Required result: make malformed or invalidly encoded context manifests fail
    problem loading with path-scoped diagnostics, then document/test the
    startup ordering so bad context manifests cannot be confused with runtime
    evaluator or prompt failures.
  - Status: implemented at the problem-loader boundary. Malformed YAML and
    invalid UTF-8 context manifests fail with path-scoped `ValueError`s before
    context selection or runtime evaluation, and focused loader tests cover
    both cases.

- [x] Add exact text-context preservation to prompt/context hardening.
  - Evidence: non-PDF context ingestion currently strips text with `.strip()`
    before prompt rendering and character-count metadata. A local proof loaded
    `notes.txt` containing two leading spaces and trailing blank lines; the
    prompt-visible context became `leading\nbody`, while the raw hash/byte
    metadata still referred to the unstripped file.
  - Current roadmap gap: context provenance tracks selected source hashes and
    excerpt spans, but not whether the rendered context is a normalized view
    of the source.
  - Required result: either preserve decoded `.txt`/`.md`/`.py` context exactly
    or record normalization policy/status in context metadata and docs; test
    whitespace-sensitive code snippets and equations.
  - Status: implemented and tested. Non-PDF context is decoded as UTF-8 without
    trimming, preserving leading/trailing whitespace, blank lines, and fenced
    code blocks through prompt rendering and character-count metadata. README,
    problem-format, architecture, and run-artifact docs state the policy.

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
  - Required result: persist provider/query/result metadata for retrieval
    plugins, render citations in prompt context, and test successful, empty,
    malformed, and failed retrieval events.

- [x] Add redaction policy for retrieval provider errors.
  - Evidence: retrieval-plugin provider errors are recorded as metadata and can
    flow into candidate history and runtime retrieval summaries.
  - Current roadmap gap: prompt/history redaction work covers evaluator output,
    feedback prompts, and LLM provider errors, but not DeepResearch retrieval
    provider exceptions.
  - Current evidence: a local proof with a custom `DeepResearchPlugin`
    `search_fn` raising
    `RuntimeError("provider failed api_key=sk-proj_secret_1234567890")`
    preserved the full secret-like placeholder in `retrieval_events[].error`.
  - Required result: define bounded/redacted retrieval-error telemetry, keep
    error categories separate from raw messages, and test custom-provider plus
    default arXiv network/parse failures before persisting retrieval errors.
  - Status: implemented. Retrieval provider errors are redacted for common
    secret patterns and truncated before plugin metadata/runtime summaries can
    persist them, while structured error categories remain separate.

- [x] Add plugin prompt-context attribution to prompt/plugin work.
  - Evidence: plugin `build_extra_context()` outputs are concatenated into one
    prompt string, and `ModularPlugin` always returns static
    generate/improve/perturb guidance without recording a selected strategy.
  - Current roadmap gap: plugin provenance work covered config/artifacts and
    score composition, but not the prompt-context components and strategy
    choices that influence candidate generation before evaluation.
  - Required result: log per-plugin prompt-context records with rendered hashes
    and operation/strategy metadata, or explicitly keep plugins such as
    `modular` as static prompt-only guidance with tests and docs.

- [x] Add prompt budget/context-window accounting to prompt work.
  - Evidence: `PromptSampler.build()` concatenates rendered sections without a
    global budget, and only problem context files have a first-6000-character
    local truncation.
  - Current roadmap gap: prompt/context work covered richer sections and
    summarization but not deterministic packing of the final prompt into a
    backend context window.
  - Required result: track prompt budgets, section priorities, token/character
    accounting, prompt-size diagnostics, and oversized-section tests.

- [x] Add prompt/history redaction and data-retention policy to prompt/runtime
  work.
  - Evidence: mutation prompts and critique prompts can include explicit
    context, plugin context, parent/inspiration code, and evaluator summaries,
    and they are stored under program metadata in `history.jsonl`. Only the
    LLM feedback workspace prompt path applies basic secret redaction today.
    Strict JSONL quarantine records are also persisted raw:
    `append_quarantine_record()` stores `record_repr = repr(record)`, and a
    local proof with a non-finite history record containing provider-key-like
    placeholders in two metadata fields kept both values verbatim in
    `history_invalid.jsonl`. Feedback grader outputs are also persisted raw: a
    local proof returned a provider-key-like placeholder in a grader JSON
    `feedback` field, and the value was stored verbatim in
    `evaluation.metadata.llm_feedback` as both `raw_response` and parsed
    `feedback`. Failed feedback-provider messages follow the same raw path: a
    local proof raised
    `RuntimeError("feedback provider failed token=ghp_feedback_secret_1234567890")`,
    and `apply_llm_feedback()` stored the exact string in
    `evaluation.metadata.llm_feedback[].message`.
  - Current roadmap gap: safety work covered validator environment secrets, and
    prompt work covered context packing, but neither called out whether prompt
    content and provider responses sent to or received from LLMs and persisted
    in run artifacts should be full, redacted, hash-only, or omitted.
  - Required result: track shared redaction, prompt-log modes, data-retention
    defaults, redaction metadata/hashes, and tests for secret-like values in
    seeds/context/plugin text, quarantine snapshots, LLM response echoes, and
    feedback-provider failure messages.

- [x] Add provider-key pattern coverage to shared redaction hardening.
  - Roadmap evidence: prompt/history redaction, validator output redaction, and
    provider-error redaction are all tracked, but the current duplicated helper
    does not cover every provider-key form users are likely to paste into
    context, outputs, or exception messages.
  - Current evidence: evaluator, prompt, and feedback redaction helpers share
    the same `_SECRET_TOKEN` pattern. A local proof showed
    `sk-proj-abcdefghijklmnopqrstuvwxyz123456` passed through all three helpers
    unchanged, while `sk-proj_...`, `ghp_...`, and `github_pat_...` were
    redacted.
  - Required result: centralize the secret-pattern helper, add hyphenated
    `sk-proj-...` coverage and tests across persisted evaluator diagnostics,
    artifacts, prompts, feedback prompts, failure memory, provider-error
    telemetry, and quarantine snapshots before roadmap/docs describe the
    current redaction policy as covering provider keys broadly.
  - Status: implemented for shared evaluator/prompt/feedback redaction paths.
    `libreevolve.core.redaction` centralizes the provider-key pattern and
    covers hyphenated `sk-proj-...` plus existing underscore forms. Focused
    tests cover evaluator diagnostics, copied text artifacts, prompt summaries,
    feedback prompts, LLM failed-call telemetry, and retrieval provider-error
    telemetry. Failure-memory and quarantine redaction remain separate open
    hardening items.

- [x] Add seed/proposal source markers to prompt-history traceability.
  - Evidence: artifact docs said history records include
    `metadata.prompt_program_id`, but seed rows are logged before prompt
    selection. A local zero-generation run produced a seed history row with no
    `prompt_program_id`; `prompt_history.jsonl` contained only the initial
    prompt-template `add` event.
  - Current roadmap gap: prompt-history work covers prompt-program selection,
    scoring, mutation, and redaction, but not candidate-source provenance for
    non-prompt seed baselines.
  - Required result: mark candidate records as seed/generated/meta-derived
    where appropriate, define whether seed baselines have no prompt id or a
    synthetic baseline source, and update artifact docs/tests so
    prompt-history linkage is accurate for all history rows.
  - Status: implemented for seed versus generated candidates. Seed rows carry
    `metadata.candidate_type = "seed"` and no prompt id; generated rows carry
    `metadata.candidate_type = "generated"` and `metadata.prompt_program_id`.
    Artifact docs and tests cover the distinction. Meta-derived candidate
    source policy remains part of future richer prompt/context evolution.

- [x] Add richer evaluator-output prompt rendering to prompt/context work.
  - Evidence: AlphaEvolve prompts can include execution results and scores, but
    earlier prompt feedback rendering only included compact recent stage
    summaries.
  - Current roadmap gap: the roadmap said evaluator feedback without calling
    out stdout/stderr, artifacts, LLM grader summaries, or sample-level
    diagnostics.
  - Status: implemented as bounded, redacted parent-feedback summaries for
    recent stage status, stdout/stderr, retry/sample attempts, and LLM grader
    feedback, plus bounded/redacted artifact path/hash summaries and skipped
    artifact diagnostics. Failure-memory prompts now render compact stored
    evaluator error/stdout/stderr and recent stage summaries from failed
    attempts. Full artifact-content retrieval and global prompt-size budgeting
    remain open.
  - Required result: keep bounded execution-output and feedback rendering on
    the roadmap as a prompt fidelity item, including failed-trial summaries
    when failure memory is rendered into mutation prompts.

- [x] Add full-workspace rendering for LLM feedback graders.
  - Evidence: `_build_feedback_prompt()` passes only the primary-file content
    (`workspace.code`) to feedback graders, so multi-file candidates can be
    graded without helper files or other evolved components.
  - Current roadmap gap: feedback calibration and richer prompt rendering were
    tracked, but not the distinct issue that feedback-grader prompts are
    primary-file-only despite workspace candidates.
  - Status: implemented. Feedback prompts now render bounded candidate file
    sets and compact diagnostics with basic redaction and tests for non-primary
    files, oversized workspace truncation, and evaluator-output visibility.

- [x] Add LLM feedback failure isolation to evaluation hardening.
  - Evidence: `apply_llm_feedback()` lets provider exceptions, malformed
    `score` values and loose `discard` truthiness propagate or misclassify
    candidates outside the structured evaluation-stage contract. Invalid
    grader config fields are now rejected by `Config.validate()`.
  - Current roadmap gap: feedback calibration and config validation were
    tracked, but the roadmap did not call out failure isolation for optional
    feedback graders as an evaluation hardening item.
  - Status: implemented as an ignore-and-record policy. Provider failures,
    malformed response scores, non-finite response scores, and non-boolean
    discard values are recorded as `llm_feedback_failed` metadata and ignored
    for score/validity composition.

- [x] Add proposal idea/rationale capture to prompt/context work.
  - Evidence: AlphaEvolve Figure 3 asks the LLM to suggest a new idea and
    describe changes with SEARCH/REPLACE blocks.
  - Current roadmap gap: prompt work covered templates/context but not a
    structured proposal artifact separate from raw patch text.
  - Status: partially implemented. `capture_proposal_metadata` asks for and
    stores bounded idea/rationale/hypothesis fields, and selected parent/
    inspiration candidates render bounded proposal summaries into prompts.
    Indexed historical resurfacing and proposal scoring remain open. Proposal
    metadata is extracted before optional critique selection, so a critique-
    revised mutation can apply different code while keeping the original
    proposal fields. The proposal-stripper is also too broad for full-file
    replacements: a local proof with `capture_proposal_metadata` enabled
    returned a `<<<FILE main.py ... >>>FILE` section whose Python triple-quoted
    string contained a line beginning `IDEA:`; `strip_proposal_metadata()`
    removed that candidate-data line before mutation application.
  - Required result: track response formats that can preserve proposal
    rationale for critique, logging, selected-mutation provenance, and future
    resurfacing without corrupting full-file/full-block candidate content that
    contains proposal-marker-like literals.

- [x] Add flexible candidate abstraction modes to candidate fidelity.
  - Evidence: AlphaEvolve Section 2.1 allows user-chosen solution
    abstractions, not only code file sets.
  - Current roadmap gap: candidate workspace work covers files, blocks, and
    artifacts, but not problem-defined render/mutate/materialize abstractions
    such as raw solutions, constructor functions, or paired solution/search
    procedures.
  - Required result: either add abstraction hooks or explicitly keep
    code-file-set evolution as a documented divergence.

- [x] Add full-code/full-block mutation mode.
  - Evidence: AlphaEvolve Section 2.3 says the system can be configured to ask
    for a complete code block rather than diffs when appropriate.
  - Current roadmap gap: no item tracks non-diff mutation modes.

- [x] Add model scheduling by throughput, cost, and depth.
  - Evidence: AlphaEvolve uses a fast model for idea breadth and a stronger
    model for deeper suggestions.
  - Current roadmap gap: the roadmap only covers backend config validation
    (`ROADMAP.md:34-41`) and does not address scheduler strategy.

- [x] Add throughput/depth scheduler initialization semantics.
  - Evidence: AlphaEvolve-style breadth/depth routing should have a clear
    model-initialization policy before metadata-weighted scheduling dominates
    observed rewards.
  - Current evidence: `LLMEnsemble._ucb1_select()` now selects each
    non-excluded backend once before UCB or throughput/depth metadata scoring.
    Tests cover a two-backend `throughput_depth` setup with depth values `1`
    and `100`, proving both backends receive initial pulls before metadata
    priority takes over.
  - Required result: define and test that `throughput_depth` performs
    pull-once initialization before metadata-priority scoring.
  - Status: implemented as pull-once initialization with regression coverage.

- [x] Add custom LLM backend extensibility to backend work.
  - Evidence: AlphaEvolve's setup includes a choice of existing or custom LLMs,
    while LibreEvolve previously hard-coded three providers in `build_llm()`.
  - Current roadmap gap: backend work covered validation and scheduling but not
    config/plugin registration for custom providers.
  - Required result: track a backend registry or plugin interface with
    validation and manifest provenance.
  - Status: implemented as configured import-path custom backends. `type:
    custom` specs use manifest-safe `class_path`, JSON-safe `kwargs`, top-level
    `model`/`max_tokens`, and the existing ensemble prompt/role/telemetry
    boundary. Restored backend-spec replay remains tracked separately.
  - Verification: focused config and ensemble tests cover custom spec
    validation, construction, role propagation, metadata retention, mutation
    revalidation, and non-protocol backend rejection.

- [x] Add backend role semantics to scheduler work.
  - Evidence: config examples accept `role: breadth` and `role: depth`, and
    `build_llm()` carries role metadata into `LLMEnsemble`, but
    `_throughput_depth_select()` currently reads only numeric `cost`,
    `latency`, and `depth`.
  - Current roadmap gap: breadth/depth scheduling work covered cost/latency/
    depth tests but did not specify whether the role field is operational or
    descriptive. Role labels are not meaningfully validated either: a local
    proof accepted an empty string `role` in an Ollama backend config and
    persisted that empty label in `LLMEnsemble.backend_metadata`.
  - Required result: either implement per-role quotas, escalation, and
    role-specific routing/accounting, or document role as descriptive metadata
    only; define the accepted role-label grammar and test blank/custom labels
    for the chosen behavior.

- [x] Add role-specific LLM call accounting to backend scheduling work.
  - Evidence: AlphaEvolve's ensemble scheduling should reflect candidate
    generation quality/throughput, while LibreEvolve currently counts
    critique/feedback/meta-prompt calls as ordinary pulls.
  - Current roadmap gap: backend scheduling work mentioned UCB reward
    normalization and breadth/depth tests but not separation of call roles.
  - Status: implemented for normalized call telemetry and persisted call-role
    records on successful mutation, critique, feedback, and meta-prompt calls.
    Role-specific routing/reward policy remains open.
  - Required result: track and test mutation, critique, feedback, and
    meta-prompt accounting separately.

- [x] Add backend reward-state validation to scheduler hardening.
  - Evidence: UCB-style scheduling assumes rewards are valid comparable
    scalars; AlphaEvolve-style backend routing should not allow invalid reward
    state to survive into long-running selection or future resume checkpoints.
  - Current evidence: `LLMEnsemble.record_reward()` now rejects invalid backend
    indexes, non-numeric rewards, non-finite rewards, and negative rewards
    before state mutation. Valid rewards are capped to `1.0`.
  - Required result: validate and normalize scheduler rewards at the ensemble
    boundary, validate backend indexes before state mutation, define invalid
    reward/index diagnostics or quarantine behavior, and test direct updates
    plus any future persisted/resumed bandit state.
  - Status: implemented for direct scheduler updates with tests for non-finite,
    negative, non-numeric, capped, negative-index, and out-of-range-index
    rewards. Future persisted/resumed bandit state must pass through the same
    validation boundary when resume exists.

- [x] Add validity/admission-aware backend reward policy.
  - Evidence: the main loop now rewards mutation backends only after archive
    admission. Invalid, below-threshold, feedback-discarded, and other
    non-admitted candidates receive zero backend reward; admitted valid
    candidates receive non-negative improvement over the selected parent.
  - Required result: define whether scheduler rewards are based on evaluator
    fitness, composed fitness, archive admission, or validity-gated
    improvement; add tests for invalid, below-threshold, feedback-discarded,
    and plugin-adjusted candidates so backend routing does not learn from
    rejected proposals as if they were successful improvements.
  - Status: implemented with persisted `metadata.backend_reward` provenance and
    tests for admitted valid improvement, plugin-raised invalid candidates, and
    feedback-discarded candidates. Ensemble-boundary reward validation remains
    tracked separately.

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

- [x] Add redaction requirements to LLM failed-call telemetry.
  - Evidence: ensemble failed-call telemetry stores `error = str(exc)` today.
    A local proof backend raised an exception containing
    `api_key=sk-proj_secret_123`, and that secret-like placeholder remained
    verbatim in `LLMEnsemble.call_history[-1]["error"]`.
  - Current roadmap gap: backend scheduling work asks for a persisted
    run-scoped call log and provider diagnostics, but does not require
    redaction before exception text becomes durable telemetry.
  - Required result: define a bounded/redacted provider-error field, preserve
    structured error type/category separately, and test secret-like exception
    text for mutation, critique, feedback, and meta-prompt call logs.
  - Status: implemented for ensemble failed-call telemetry. Error text is
    redacted and bounded before storage in `LLMEnsemble.call_history`, with
    `error_type`, role, retry, and fallback fields preserved. Run-scoped call
    log persistence remains a separate open telemetry item.

- [x] Add LLM provider failure policy to backend/runtime work.
  - Evidence: `evolve()` calls `llm.generate()` for mutation, critique,
    feedback, and meta-prompt mutation without retries or exception handling,
    while `LLMEnsemble._ucb1_select()` advances the global attempt counter
    before the provider call and `LLMEnsemble.generate()` increments backend
    counts only after a successful return.
  - Current roadmap gap: backend scheduling and telemetry work covered
    throughput, usage, and failure metadata, but did not require deterministic
    retry/fallback/quarantine behavior for failed provider calls.
  - Status: partially implemented at the ensemble boundary. `llm_max_retries`
    retries the same backend, `llm_fallback` can route to another backend, and
    call telemetry records retry/fallback attempt indexes plus retry/fallback
    decisions. Later slices added `provider_max_retries`, `adapter_retry`, and
    normalized `provider_failure_category` telemetry, but configured retry
    budgets still do not control token/cost/time consumption. Role-specific
    quarantine and penalties remain open.
    Failed-call accounting is also not yet canonical: a failed backend
    selection increments ensemble `total` but not that backend's pull count,
    so UCB state after fallback does not correspond to either successful pulls
    or total provider attempts.
  - Required result: track per-role LLM retry budgets, fallback routing, failed
    attempt accounting, unified adapter/ensemble retry semantics, structured
    error logs, and tests for mutation, critique, feedback, and meta-prompt
    failures.

- [x] Add reviewer-pool critique fidelity to backend/critique work.
  - Evidence: AlphaEvolve describes using LLMs to generate, critique, and
    evolve a pool of algorithms, while LibreEvolve has only a single optional
    synchronous self-revision pass.
  - Current roadmap gap: critique work did not explicitly call out reviewer
    roles, agreement/disagreement logging, or policies beyond one revision.
  - Required result: extend critique/revision toward configurable reviewer
    pools with provenance and accounting.

- [x] Add deterministic critique-revision fallback behavior.
  - Evidence: a malformed synchronous critique response could previously
    replace an applicable mutation and be evaluated as a parser failure.
  - Status: implemented. Critique revisions are previewed before selection;
    malformed revisions fall back to the original mutation when it still
    applies cleanly, with parser diagnostics and selection metadata recorded in
    `metadata.critique`.
  - Remaining roadmap gap: reviewer pools, role routing, agreement policies,
    and async critique workers are still tracked separately.

- [x] Add rich evolutionary database work.
  - Evidence: AlphaEvolve's program database stores solutions with scores and
    outputs, then resurfaces ideas to balance exploration and exploitation.
  - Current roadmap gap: `ROADMAP.md:108-113` treats a database backend as a
    non-goal. That may remain true for services, but a stronger local
    evolutionary database is required for AlphaEvolve fidelity.

- [x] Add archive-state and migration-event persistence to database work.
  - Evidence: `ProgramDatabase.log()` writes candidate JSONL records, but
    `MAPElites` cell grids, elite lists, diversity/complexity normalization
    state, island assignment, and migration events remain in memory only.
  - Current roadmap gap: resumability and database work covered queryability
    and saved state broadly, but not the concrete MAP-Elites/island state
    needed to inspect or resume the actual archive used by sampling.
  - Required result: persist archive cell/event snapshots with island ids,
    descriptors, replacements, elite contents, migration events, and
    normalization state.

- [x] Add per-program archive admission outcomes to database work.
  - Evidence: `evolve()` logs a program before calling `db.add()`, and archive
    insertion does not return whether a candidate entered a cell, replaced an
    occupant, was ignored by MAP-Elites competition, or was rejected by
    threshold.
  - Current roadmap gap: archive-state persistence covered snapshots and
    migration events, but not a per-history-record admission status that lets
    users understand which evaluated programs actually affected the archive.
  - Status: implemented. `history.jsonl` records
    `metadata.archive_admission` with threshold reason, island id, cell
    descriptors, replacement status, previous occupant ids, elite-list effects,
    and displaced elite ids.

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

- [x] Add strict `ProgramDatabase.admit()` validity typing to database
  hardening.
  - Evidence: archive admission should be the live gate between evaluated
    candidates and MAP-Elites state, not a truthiness check over arbitrary
    metadata.
  - Current evidence: the former loose truthiness path has been replaced.
    `ProgramDatabase.admit()` and the loop validity helper now require
    `program.evaluation["is_valid"] is True`, and `libreevolve show` requires
    both exact archive admission and exact boolean evaluator validity for
    modern history selection.
  - Required result: require exact boolean `True` for live archive insertion,
    quarantine or reject non-boolean validity metadata before state mutation,
    and keep any legacy-history fallback explicit and separate from strict
    modern-history inspection.
  - Status: implemented for the validated database admission path.
    `ProgramDatabase.admit()` now admits only candidates
    with `program.evaluation["is_valid"] is True`; missing, string, or integer
    validity values are rejected as invalid evaluations. `libreevolve show`
    also requires `metadata.archive_admission.admitted is True` and
    `evaluation.is_valid is True` for modern archive-aware histories. Tests
    cover live admission and modern-history inspection. Public/raw lower-level
    insertion paths are tracked separately.

- [x] Add aggregate workspace syntax diagnostics to evaluator feedback work.
  - Evidence: `_syntax_errors()` now checks candidate `.py` files in sorted
    order and aggregates every `SyntaxError` into structured metadata.
  - Current roadmap gap: evaluator diagnostics covered structured results,
    stdout/stderr, retries, and artifacts, but not first-error-only syntax
    feedback in multi-file candidates.
  - Status: implemented for evaluation records/history. Python syntax failures
    across a candidate workspace now include file/line/offset/message details.
    Dedicated prompt rendering remains covered by the broader prompt-feedback
    gap.

- [x] Add strict JSONL serialization hardening to database work.
  - Evidence: `ProgramDatabase.log()`, `PromptDatabase._write()`, manifests,
    and `TTTRLPlugin._maybe_train()` now use strict finite JSON writers and
    quarantine invalid append records.
  - Current roadmap gap: database work covered queryability and sampling, but
    not the validity of persisted JSONL for strict downstream analysis.
  - Status: roadmap updated to treat strict finite JSONL as current coverage
    for candidate, prompt, manifest, and GRPO-export writers, while future
    artifact writers still need the same policy.

- [x] Add malformed-history read diagnostics to operational/database work.
  - Evidence: strict JSONL hardening currently covers write paths, but
    AlphaEvolve-scale run inspection also needs robust read paths for long
    append-only histories.
  - Current evidence: `cli.show()` now streams `history.jsonl` line by line,
    reports malformed JSON and non-object rows through line-numbered
    `ClickException` diagnostics, preserves empty-history diagnostics, and
    requires exact archive admission plus boolean evaluator validity for
    modern history selection.
  - Required result: define strict read behavior for current and legacy
    histories, report file/line parse errors through normalized CLI
    diagnostics, stream large histories where possible, require explicit
    validity evidence for current histories, and add tests for malformed,
    partially valid, missing-evaluation, and large-history inspection.
  - Status: implemented as a fail-fast read policy. Tests cover malformed JSON,
    non-object rows, empty history, strict modern validity, large legacy
    histories, and no-admitted-modern histories.

- [x] Add failure-history quarantine separation to database hardening.
  - Evidence: `ProgramDatabase.log_failure()` previously wrote invalid
    `failure_history.jsonl` records to the shared `history_invalid.jsonl`
    quarantine.
  - Current roadmap gap: strict JSONL work covered candidate, prompt,
    manifest, and GRPO append writers, but not whether failure-memory records
    have a stream-specific quarantine/audit path.
  - Status: implemented. Failure-history append failures now use
    `failure_history_invalid.jsonl`, with tests proving they do not mix with
    candidate-history quarantine records.

- [x] Add reproducibility hashes to run metadata work.
  - Evidence: AlphaEvolve-scale runs need exact problem, evaluator, prompt, and
    code-state provenance to support long-running comparisons.
  - Current roadmap gap: `manifest.json` existed, but the roadmap did not make
    code/problem/plugin/artifact hashes explicit.
  - Status: implemented for Git state, `libreevolve/` source-tree hashes,
    problem-tree hashes, direct evaluator entrypoint hashes, and plugin module
    file hashes in `manifest.json`. Aggregate hashes for artifacts emitted
    after startup and validated plugin constructor/config specs remain open.
  - Required result: track hashes/version metadata separately from basic config
    logging.

- [x] Add provenance exclusion policy to manifest hardening.
  - Evidence: generated run artifacts should not churn problem hashes, but
    problem fixtures/context should not disappear from provenance merely
    because a directory is named like an output directory.
  - Status: implemented. Problem provenance includes ordinary problem-owned
    directories named `runs`; tests prove changes under
    `problem/runs/fixture.txt` affect the problem tree hash. The effective
    active generated run root is passed into problem provenance and skipped
    only if it resolves inside the problem tree, with
    `reason: excluded_output_root`. Cache directories and links are also
    recorded in skipped-path diagnostics.

- [x] Add symlink policy to provenance manifest hardening.
  - Status: implemented as a no-follow policy. Source/problem provenance now
    skips symlinks and Windows junctions before descent or byte reads, records
    skipped entries with `reason: link_not_followed`, and excludes linked
    targets from the tree hash. README/run-artifact/architecture docs describe
    the policy. Tests cover file-symlink skipping where supported and Windows
    junction skipping.

- [x] Add runtime environment/package provenance to manifest hardening.
  - Status: implemented. Manifests now include `provenance.environment` with
    Python version/implementation, platform/system metadata, `pyproject.toml`
    hash, package name/version and `requires-python`, build backend metadata,
    and installed versions for declared runtime dependencies. Tests cover
    standalone environment provenance and manifest wiring. Remaining roadmap
    work is richer lockfile/accelerator/provider-runtime provenance.

- [x] Add package metadata parse diagnostics to manifest hardening.
  - Status: implemented as degraded package provenance records. Runtime
    provenance now records `package.pyproject.status: invalid_toml` for
    malformed TOML, `invalid_encoding` for non-UTF-8 bytes, and `unreadable`
    for file read failures, while retaining hash/size when bytes are readable.
    Tests cover malformed and non-UTF-8 `pyproject.toml`, and manifest docs now
    describe the degraded-record policy.

- [x] Add curated example artifact refresh to run-metadata work.
  - Evidence: `examples/runs/hello_world_ensemble` and
    `examples/runs/sorting_ttt_rl` contain `history.jsonl` and `best.py` only,
    while current CLI runs and artifact docs include `manifest.json`,
    `prompt_history.jsonl`, `failure_history.jsonl`, and `best_workspace/`.
  - Current roadmap gap: artifact work covered new run outputs but not whether
    committed examples still prove the documented artifact contract.
  - Required result: refresh curated examples to the current artifact schema,
    or clearly keep them as legacy history-only fixtures and test/document that
    boundary.

- [x] Add plugin registry/config/provenance work.
  - Evidence: built-in plugins are currently hard-coded CLI aliases with no
    per-plugin config schema, constructor options, or manifest provenance.
  - Current roadmap gap: plugin extensibility covered moving registration out of
    the CLI, but not config validation or run-provenance records for plugin
    parameters and emitted artifacts.
  - Required result: track plugin registry, configuration schema, constructor
    parameters, paper-inspiration scope, and artifact provenance.

- [x] Add plugin preflight ordering to runtime/artifact safety.
  - Previous evidence: CLI startup prepared the run directory before
    `_load_plugins()` resolved plugin names. A local proof with
    `--plugins missing --overwrite` failed on `Unknown plugin: 'missing'` after
    the existing run's `history.jsonl` had already been removed by overwrite
    cleanup. `Config.validate()` also accepted empty and whitespace-padded
    plugin names. Constructor-level plugin cadence fields were not validated
    either: `TTTRLPlugin(train_every=0).on_generation_end(1, None)` and
    `DeepResearchPlugin(search_every=0).on_generation_start(1, None)` both
    raised `ZeroDivisionError`.
  - Required result: resolve and validate plugin names/specs, including empty
    or whitespace-only identifiers and positive-integer cadence fields, before
    any destructive run-directory preparation or plugin hook execution; add
    regression tests proving invalid plugin configuration cannot delete
    existing run artifacts.
  - Status: implemented for current built-in plugin names and cadence fields.
    CLI startup validates plugin aliases before overwrite cleanup, config
    validation rejects empty/whitespace plugin identifiers, and TTTRL /
    DeepResearch constructors reject non-positive or non-integer cadence
    values. Regression tests cover existing artifact preservation.

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

- [x] Add evaluate-only/seed-baseline mode to runtime work.
  - Previous evidence: `evolve()` constructed the LLM ensemble before evaluating seeds.
    A local temp proof with `--max-generations 0 --backends
    openai:gpt-4o-mini` and no `OPENAI_API_KEY` failed during provider client
    construction, leaving only `manifest.json` and no seed `history.jsonl`,
    despite no scheduled LLM mutation calls.
  - Required result: support seed-only or evaluate-only runs that validate
    seeds, write history/manifest/best artifacts, and skip provider client
    construction when no LLM role can run; keep normal mutation runs covered by
    backend preflight before destructive setup.
  - Status: implemented for seed-only and budget-stopped-before-mutation runs.
    LLM backends are now constructed lazily at the first mutation call; CLI
    tests cover `--max-generations 0 --backends openai:gpt-4o-mini` without
    provider credentials.

- [x] Add plugin score-composition provenance to plugin extensibility work.
  - Evidence: `evolve()` lets each plugin return a modified score and stores
    only the final `program.fitness`, while `evaluation.fitness` remains the
    evaluator/feedback result.
  - Current roadmap gap: plugin work mentioned registration, configuration, and
    artifacts but not the provenance of score-changing hook chains.
  - Required result: track per-plugin before/after scores, reasons, validation,
    and the relationship between raw evaluator fitness and composed archive
    fitness.

- [x] Add finite top-level fitness checks to database/archive hardening.
  - Evidence: archive admission should reject invalid scalar scores before they
    affect parent selection, inspiration sampling, or best-program selection.
  - Current evidence: `ProgramDatabase.admit()` and `MAPElites.add()` now
    reject non-finite top-level `Program.fitness` before MAP-Elites insertion,
    even when `metadata.selection_score` is finite. `libreevolve show` rejects
    non-finite history fitness rows before selection.
  - Required result: reject or quarantine non-finite top-level fitness values
    before MAP-Elites insertion, distinguish this from metric-output
    validation, and test direct database, plugin side-effect, and future resume
    inputs.
  - Status: implemented for direct database/archive calls and history
    inspection; future resume inputs must reuse the same predicate when resume
    checkpoints exist.

- [x] Add canonical mutation parsing to plugin truthfulness work.
  - Evidence: the core mutation path accepts both canonical AlphaEvolve
    SEARCH/REPLACE fences and the compact local form. `CausalPlugin` now uses
    that shared `parse_diff_blocks()` path for mutation factor detection, and
    tests cover compact, canonical, and mixed diff blocks.
  - Current roadmap gap: plugin extensibility/truthfulness work covered
    registration, config, artifacts, provenance, and score composition, but not
    shared mutation parsing semantics for plugins that inspect LLM patches.
  - Required result: require plugin mutation analysis to use the shared diff
    parser or mutation AST, and add compact/canonical parser tests for the
    CausalEvolve-inspired plugin before treating its guidance as format-stable.

- [x] Add evaluator path validation/provenance to runtime hardening.
  - Evidence: `eval_stages[].validate_path` previously could resolve to
    arbitrary absolute paths and was not prevalidated or hashed before
    execution.
  - Current roadmap gap: evaluator hardening covered metric contracts,
    cascades, and artifacts but not validator-code path confinement and
    provenance.
  - Status: path confinement and direct entrypoint provenance are implemented.
    Stage validators must resolve to problem-local Python files; missing,
    directory, non-Python, outside-root, and symlink-escape paths are rejected.
    `manifest.json` records direct evaluator entrypoints with resolved path,
    problem-relative path, SHA-256 hash, byte count, source type, and stage
    usage metadata.
  - Remaining gap: transitive helper/data provenance and package-style
    evaluator semantics are not yet included in manifests.

- [x] Add validator environment/secret isolation to runtime hardening.
  - Evidence: `.env` is loaded into the parent process, and
    `CascadeEvaluator._run_subprocess()` calls `subprocess.run()` without an
    `env=` allowlist, so validators inherit provider keys and host environment
    variables by default.
  - Current roadmap gap: sandbox/resource-limit and evaluator-path work covered
    filesystem/process boundaries, but not inherited secrets, environment
    reproducibility, redaction, or network expectations.
  - Status: validator subprocesses now run with an explicit minimal
    environment plus `validator_env_allowlist`, metadata records environment
    keys without values, stdout/stderr is secret-redacted before persistence,
    and tests prove provider keys are hidden by default while opt-in variables
    are available.
  - Remaining gap: network egress policy and stronger sandbox/resource
    isolation remain open.

- [x] Add evaluator process-tree cleanup to runtime hardening.
  - Evidence: `CascadeEvaluator._run_subprocess()` relies on
    `subprocess.run(..., timeout=...)` and does not create a process group, Job
    Object, or descendant-cleanup policy. A validator-spawned child process can
    outlive a timed-out direct validator process.
  - Current roadmap gap: runtime hardening covered timeouts, sandbox/resource
    limits, and environment secrets, but not cleanup of subprocess descendants
    created by evaluator code.
  - Status: implemented for timeouts. Validators now run in a killable process
    tree, timeout results include cleanup metadata, and regression coverage
    exercises a simple spawned child. This remains best-effort rather than a
    deterministic guarantee that every descendant cannot outlive a timeout under
    repeated Windows/full-suite load.
  - Remaining gap: this is not full container/resource sandboxing or a general
    deterministic cleanup guarantee for detached work.

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
  - Required result: serialize first, atomically replace manifest files, keep
    the last valid manifest on failure, and add diagnostics/tests for
    non-serializable and non-finite manifest payloads.
  - Status: implemented. `strict_json_dump()` now serializes before writing a
    temporary file and atomically replacing `manifest.json`.
    `update_manifest_runtime()` quarantines rejected runtime updates in
    `manifest_invalid.jsonl` while preserving the prior valid manifest.
    Regression tests cover non-serializable and non-finite runtime payloads.

- [x] Add startup-manifest validation before overwrite cleanup.
  - Status: implemented. `ProgramDatabase` now builds and strictly serializes
    the full startup manifest payload before destructive cleanup. Tests prove
    non-serializable startup provenance and non-finite startup context payloads
    raise `StrictJsonlError` while preserving existing `history.jsonl` and
    writing no replacement manifest.

- [x] Add invalid-seed diagnostics to runtime/database hardening.
  - Roadmap evidence: current runtime/database work tracks candidate history,
    failure history, archive admission, and run stop reasons, but not the
    startup case where every initial seed evaluates invalid.
  - Previous evidence: `evolve()` logged invalid seeds to `history.jsonl` with
    archive-admission rejection, but did not call `log_failure()` for seeds.
    A run with no valid seed stopped at `no_parent` with no
    `failure_history.jsonl` and no prompt-visible failed-trial memory.
  - Required result: add a seed failure/diagnostic artifact or include invalid
    seeds in failure history, then update run accounting so all-invalid
    startup is explicit and queryable.
  - Status: implemented. Rejected seeds are recorded in `failure_history.jsonl`
    as `record_type: "seed"` records with evaluator summaries and admission
    reasons, mirrored into seed history metadata, and rendered into the first
    mutation prompt when a valid seed parent exists. All-invalid seed startup
    now stops at `no_valid_programs` without incrementing generation counters.

- [x] Add initial-seed post-processing policy to evaluation/plugin hardening.
  - Roadmap evidence: LLM feedback, plugin score composition, candidate
    history, and archive admission are tracked as candidate evaluation
    behavior, but the roadmap does not state whether the initial population
    uses the same post-evaluation pipeline.
  - Previous evidence: seeds were evaluated and logged before generation, but
    `evolve()` does not call LLM feedback graders or plugin `on_evaluated()`
    for seed programs. A local proof with configured LLM feedback and a
    score-boosting plugin produced a seed history row with no
    `evaluation.metadata.llm_feedback`, no `metadata.score_composition`, and no
    feedback LLM calls.
  - Required result: define initial seeds as either raw evaluator baselines or
    fully post-processed candidates; make that policy visible in history and
    docs, and test seed rows under LLM feedback and plugin configurations.
  - Status: implemented as raw evaluator baselines. Seed history rows now carry
    `metadata.candidate_type = "seed"` and explicit post-processing policy
    metadata; generated rows carry `candidate_type = "generated"`. The run
    manifest records the seed post-processing policy, and tests cover seed rows
    while feedback graders and plugins are configured.

- [x] Add workflow-enabled-state tracking to operational maturity.
  - Roadmap evidence: roadmap operational maturity depends on CI/interpreter
    coverage and docs/paper validation being meaningfully runnable.
  - Current evidence: GitHub currently reports the `Tests` workflow state as
    `disabled_manually`, and README/development docs now say local commands are
    the validation path until the workflow is intentionally re-enabled.
  - Required result: include workflow enabled/disabled state in the roadmap's
    validation boundary, or make local validation the explicit authoritative
    path until GitHub CI is re-enabled.
  - Status: ROADMAP operational maturity now explicitly includes re-enabling or
    tracking disabled GitHub workflow state, docs/paper validation, and broader
    CI/interpreter coverage without reintroducing notification noise.

- [x] Refresh current-state example list.
  - Evidence: `libreevolve/problems/examples/` includes `workspace_math`, but
    `ROADMAP.md` listed only `hello_world`, `sorting`, `circle_packing`, and
    `matrix_multiplication`.
  - Required result: include all checked-in examples when the roadmap describes
    current repository state.

- [x] Refresh current-state and near-term lists after workspace/evaluator
  implementation passes.
  - Evidence: `ROADMAP.md` still treated unified file-section path parsing,
    workspace topology mutation, workspace execution import/cwd semantics,
    full-workspace best export, strict scalar evaluator-output validation, and plugin
    score-composition provenance as near-term or open work after those local
    behaviors were implemented and documented.
  - Status: roadmap current-state bullets now include topology mutation,
    strict evaluator-output validation, archive admission events, and
    `best_workspace/`.
    Near-term bullets now focus on remaining gaps: load-time seed marker
    validation, binary/static artifacts, package-style validators, relative
    evaluator data, and workspace migration/resume.
  - Required result: keep roadmap work items phrased around the remaining
    AlphaEvolve divergences rather than stale already-implemented behavior.

- [x] Add seed-workspace symlink policy to candidate fidelity.
  - Roadmap evidence: current workspace/candidate fidelity work covers
    multi-file seed directories, path grammar, and candidate materialization
    safety, but does not state how symlinks inside `initial_programs/<seed>/`
    are handled.
  - Status: implemented as a reject policy. `_load_initial_workspaces()` rejects
    symlinks and Windows junctions at top-level seed entries and within seed
    workspace directories before reading candidate text. README,
    `docs/problem-format.md`, and architecture docs document the policy. Tests
    cover file-symlink rejection where supported and Windows junction rejection.

- [x] Add path-aware invalid-seed-encoding diagnostics to candidate fidelity.
  - Roadmap evidence: seed workspaces are now treated as declared problem-local
    UTF-8 text workspaces, while binary/static assets remain future work.
  - Current evidence: a CLI proof with invalid UTF-8 in
    `initial_programs/seed.py` exited with a raw codec error and no offending
    path; a loader proof with invalid UTF-8 in
    `initial_programs/seed_a/helper.py` raised raw `UnicodeDecodeError`.
  - Required result: normalize seed decode failures into problem-load setup
    diagnostics that name the top-level seed or nested workspace file, keep the
    check before artifact preparation, and test both CLI and loader paths.
  - Status: implemented for UTF-8 text seeds. Invalid top-level and workspace
    seed-file encodings now report the offending path through loader/CLI
    startup diagnostics.

- [x] Refresh stale evaluation/runtime roadmap bullets after artifact,
  retry-attempt, environment, and budget hardening landed.
  - Evidence: `ROADMAP.md` still listed evaluator artifact collection,
    run-wide wall-clock/evaluator-second/stop-reason accounting, retry-attempt
    preservation, validator environment allowlisting, and degenerate metric
    bound rejection as near-term missing work.
  - Current evidence: `CascadeEvaluator` now collects configured artifacts,
    records retry attempts, uses a minimal validator environment with an
    allowlist, redacts persisted validator output, and records timeout cleanup
    metadata. `RunBudget` and completed manifests record generation,
    evaluation, evaluator-second, wall-clock, and stop-reason accounting.
    `load_problem()` rejects zero-width or inverted metric bounds.
  - Status: roadmap current-state bullets now include these implemented local
    behaviors. Near-term/mid-term bullets now focus on the remaining gaps:
    outside-workspace artifacts, aggregate artifact hashes, provider
    token/cost budgets, stage sample/retry totals, network/container
    sandboxing, external/transitive evaluator environment provenance, and
    benchmark artifact schemas.
  - Required result: keep roadmap bullets scoped to missing behavior, not work
    already proven by code and tests.

- [x] Refresh operational roadmap bullets after config-error and `show`
  hardening landed.
  - Evidence: `ROADMAP.md` still listed malformed/non-mapping `config.yaml`
    path-aware errors and validity/archive-aware `show` selection as missing
    operational work.
  - Current evidence: `_build_config()` catches YAML parse errors with the
    config path, rejects non-mapping top-level YAML with a path-aware
    `ConfigError`, and has CLI tests for both cases. `cli.show()` detects
    modern archive-admission metadata, selects archive-admitted valid records,
    prints the selection mode, and emits archive/metric summaries while keeping
    legacy highest-fitness fallback for old histories.
  - Status: roadmap operational work now keeps plugin/provider validation as
    the remaining config gap and describes `show` work as richer inspection
    beyond the current compact archive-aware view.
  - Required result: avoid listing already implemented operational hardening as
    future AlphaEvolve-alignment work.

- [x] Add artifact-pattern schema validation to evaluator artifact hardening.
  - Evidence: evaluator artifact include/exclude settings are documented as
    glob patterns, while validator environment allowlists are environment
    variable names. Those are different schemas and should produce different
    diagnostics.
  - Current evidence: `Config.validate()` now uses separate validators for
    environment allowlists and artifact glob lists. Tests cover top-level and
    per-stage artifact patterns containing `=`.
  - Required result: add field-specific artifact glob validation and tests for
    top-level/stage include/exclude patterns, keeping environment allowlist
    validation separate.
  - Status: implemented.

## Existing Items That Need Tightening

- [x] Expand "better diversity measures" into measurable database/sampling
  requirements.
  - Evidence: `ROADMAP.md:85-88` is too vague to guide AlphaEvolve-compatible
    parent/inspiration sampling.
  - Required result: specify candidate features, metric-vector diversity,
    lineage diversity, recency, novelty, and score-conditioned inspiration
    sampling.

- [x] Add workspace-aware MAP-Elites descriptors to diversity/search work.
  - Evidence: `MAPElites._cell()` computes complexity and TF-IDF diversity from
    `Program.code`, which is only the primary-file view for workspace
    candidates.
  - Current roadmap gap: diversity work called for better measures generally,
    but not the distinct mismatch that multi-file candidates are archived by a
    single-file projection.
  - Required result: compute descriptors from canonical workspace contents or
    evaluator-provided behavior descriptors, persist descriptor values, and
    test non-primary file changes affecting cells and inspiration sampling.

- [x] Add stable MAP-Elites descriptor normalization/rebinning to diversity
  work.
  - Evidence: `MAPElites._norm_complexity()` mutates `_max_complexity` while
    assigning a candidate cell, and `_diversity()` uses the current capped
    elite list as its TF-IDF reference corpus. Existing grid occupants are not
    re-binned when either reference state changes. A local proof showed that a
    `not_improving_cell` candidate that was not retained by the grid or capped
    elite list still raised `_max_complexity` from `4` to `4000`, changing the
    next short candidate's complexity descriptor to `0.001`.
  - Current roadmap gap: workspace-aware descriptors were tracked, but not the
    separate issue that even primary-file descriptor coordinates are
    insertion-order dependent unless normalization bounds or rebinning
    semantics are defined.
  - Required result: track fixed descriptor bounds, evaluator-provided behavior
    descriptors, persisted normalization state, or explicit rebin/snapshot
    events with tests for insertion-order stability.

- [x] Expand "training-data export" into a concrete ThetaEvolve/GRPO boundary.
  - Evidence: `ROADMAP.md:98-99` mentions downstream RL fine-tuning around
    `ttt_rl`, while the current plugin only writes JSONL and does not train.
  - Required result: define whether LibreEvolve will implement training,
    export-only datasets, or integration hooks, and document the divergence.

- [x] Add reward/export provenance to the ThetaEvolve boundary.
  - Evidence: `TTTRLPlugin` exports raw score plus
    `reward = max(0.0, raw_score)`. CLI-loaded runs write under
    `plugin_artifacts/ttt_rl/` and completed manifests include path/hash/count
    metadata.
  - Current roadmap gap: the ThetaEvolve boundary distinguished export from
    training, but did not require explicit reward-shaping semantics, per-run
    dataset scoping, manifest linkage, or dataset hashes.
  - Required result: track raw score and shaped reward fields, document clipping
    or penalties, persist run-scoped dataset provenance, and add tests for
    negative rewards and repeated flush/resume behavior.

- [x] Move representative benchmarks earlier.
  - Evidence: `ROADMAP.md:92-95` keeps representative algorithmic benchmarks in
    longer term.
  - AlphaEvolve alignment need: benchmarks like matrix multiplication,
    circle/kissing packing, constructive math, or scheduling heuristics are
    needed to prove fidelity beyond toy examples.

- [x] Include compiler and hardware benchmark families in the roadmap.
  - ROADMAP evidence: the representative-benchmarks section named constructive
    math plus one scheduling/kernel microbenchmark, but did not mention local
    paper-cache applications such as compiler optimization or computer
    architecture discovery.
  - Paper evidence: `2601.21096__Magellan.pdf` evolves compiler optimization
    heuristics with AlphaEvolve, and `2602.22425__ArchAgent.pdf` applies
    agentic AI to computer-architecture discovery.
  - Required result: either include compiler/hardware/systems in the benchmark
    roadmap language or keep the paper rows explicitly background-only.
  - Status: `ROADMAP.md` now names compiler/hardware/systems/kernel/scheduling
    as the safe microbenchmark family boundary.

- [x] Add typed YAML-key validation to configuration preflight.
  - Evidence: configuration preflight should turn invalid user setup into
    deterministic `ConfigError`/Click diagnostics before any run artifacts,
    validator imports, or backend setup.
  - Current evidence: `_build_config()` sorted the unknown key set before
    proving all top-level `config.yaml` keys were strings. A local proof with
    mixed keys `1: bad` and `unknown: bad` raised raw
    `TypeError: '<' not supported between instances of 'str' and 'int'`
    instead of `Unknown config keys...` or a non-string-key diagnostic.
  - Required result: validate top-level YAML config keys immediately after
    load, keep duplicate-key checks, report non-string and unknown keys
    deterministically, and include this in runtime/config hardening tests.
  - Status: implemented. `_build_config()` now validates top-level YAML config
    key types before unknown-key sorting, and focused CLI tests prove both the
    non-string-only and mixed non-string/unknown-string cases use clean Click
    diagnostics instead of a raw Python exception.

- [x] Add startup-order hardening for plugin aliases versus validator
  preflight.
  - Roadmap evidence: plugin alias preflight and validator-contract preflight
    are both described as startup protections before run-artifact mutation, but
    their relative ordering matters because validator preflight imports user
    task code in the main process.
  - Current evidence: `libreevolve.cli.run()` preflighted validators before
    validating plugin names. A local CLI proof using an unknown plugin exited
    with `Unknown plugin`, yet module-level code in `validate.py` ran first and
    wrote a marker file.
  - Required result: make invalid plugin aliases fail before validator imports,
    or document and isolate validator preflight side effects; include the
    ordering in runtime/plugin hardening tests for default and staged
    validators.
  - Status: implemented. Plugin alias validation now runs before evaluator
    contract preflight, and CLI tests cover the ordering so unknown plugins do
    not import validator modules before failing.

- [x] Tighten safe run-name grammar to include DEL/control-class characters.
  - Roadmap evidence: runtime hardening says run names are portable safe path
    components and documentation says control characters are rejected.
  - Current evidence: `_require_run_name_component()` checked `ord(ch) < 32`,
    but accepted ASCII DEL (`0x7f`). A local direct proof created a run with
    `problem_name="bad\x7fname"` and persisted that value in
    `manifest.json.config.problem_name`.
  - Required result: make the roadmap's run-name hardening explicitly cover
    DEL and any platform/control character class the project treats as unsafe;
    test direct config construction, CLI `--run-name`, manifest writing, and
    run-directory path handling.
  - Status: implemented for ASCII controls. The shared run-name validator now
    rejects DEL, and focused tests cover direct `Config` construction plus CLI
    `--run-name` rejection before evolution starts.

- [x] Add manifest-safe retention rules for configured log roots.
  - Roadmap evidence: runtime/provenance hardening already tracks raw Git,
    source/problem, and plugin paths, but the effective configured `log_dir` is
    also part of the durable manifest.
  - Current evidence: a local proof created
    `Config(log_dir=<tmp>/api_key=sk-proj_LOGDIRSECRET_1234567890/runs,
    problem_name="demo")`, constructed `ProgramDatabase`, and observed
    `manifest.json.config.log_dir` containing the raw secret-like path
    component.
  - Required result: decide whether log roots are persisted raw, redacted,
    path-hashed, project-relative, or opt-in verbose; update run-artifact docs,
    resume design, and tests for absolute, relative, and sensitive path
    components.
  - Status: implemented for current startup manifests. Configured absolute log
    roots are represented by `<absolute-log-dir>` plus `log_dir_metadata`
    containing a SHA-256 digest and retention reason; safe relative roots stay
    readable, and tests cover absolute, relative, and secret-like components.

- [x] Add Unicode format-control hardening for run/candidate path labels.
  - Evidence: safe-name checks rejected many ASCII path hazards but accepted
    invisible and bidirectional Unicode format controls. A local proof accepted
    `Config(problem_name="rtl\u202egnp")` and candidate path
    `src/rtl\u202egnp.py`.
  - Status: implemented for run names and candidate file paths. These labels
    now reject Unicode `Cf` format controls while ordinary Unicode names remain
    allowed; later completed slices covered plugin, feedback, artifact, and
    context labels.

- [x] Add Unicode format-control hardening for metric/stage labels.
  - Evidence: metric names and configured evaluator stage names are durable
    experiment labels in manifests, history, prompts, and evaluation metadata.
  - Status: implemented for Unicode format controls. Metric names and
    configured stage names now reject Unicode `Cf` characters such as
    right-to-left override and zero-width joiner; later completed slices
    covered plugin, feedback, artifact, and context labels.

- [x] Add Unicode format-control hardening for plugin/feedback labels.
  - Evidence: configured plugin aliases and LLM feedback grader labels are
    durable experiment labels in manifests, call roles, evaluation metadata,
    and metric vectors.
  - Status: implemented for Unicode format controls. Configured plugin aliases
    and LLM feedback `name` / `metric` labels now reject Unicode `Cf`
    characters; later completed slices covered artifact/context labels and
    plugin-emitted metadata labels.

- [x] Add Unicode format-control hardening for artifact/context labels.
  - Evidence: artifact selector patterns and context manifest include/exclude
    patterns are persisted and rendered as experiment provenance.
  - Status: implemented for Unicode format controls. Artifact include/exclude
    globs and context manifest selection patterns now reject Unicode `Cf`
    characters while ordinary non-ASCII path text remains allowed; a later
    completed slice covered plugin-emitted metadata labels.

- [x] Add Unicode format-control hardening for plugin-emitted metadata labels.
  - Evidence: plugin prompt-context metadata and plugin run-artifact metadata
    can be persisted in history rows and manifests.
  - Status: implemented for metadata keys. Plugin-emitted metadata dictionaries
    now reject non-string keys and Unicode `Cf` controls recursively while
    ordinary non-ASCII key text remains allowed.

- [x] Add validator-environment allowlist label canonicalization.
  - Evidence: validator environment allowlists are persisted in manifests and
    evaluator metadata and should identify effective exposed parent variables
    reproducibly.
  - Status: implemented with canonical portable env labels. Config and direct
    evaluator construction now strip whitespace, uppercase, deduplicate, and
    validate names against `[A-Z_][A-Z0-9_]{0,127}` before manifest persistence
    or subprocess environment construction.

- [x] Add metric-name grammar to schema hardening.
  - Evidence: metric names are persisted in history, manifests, prompts, and
    archive/search metadata.
  - Status: implemented for problem schemas. `metrics.yaml` metric names now
    use a safe ASCII identifier grammar with optional dotted namespaces, and
    tests prove unsafe metric keys cannot enter loaded problem schemas.

- [x] Share problem-schema validation across loader and direct API paths.
  - Evidence: direct `Problem(...)` construction previously bypassed loader
    metric validation and could reach evaluators with duplicate or missing
    primary metric schemas.
  - Status: implemented for metric schemas. `Problem.__post_init__` applies the
    shared normalizer used by `load_problem()`, including primary membership,
    duplicate detection, safe metric names, directions, bounds, and effective
    primary marking.

- [x] Add async/generator-validator rejection to evaluator contract preflight.
  - Evidence: validator contract preflight previously verified importability,
    callable `evaluate`, and bindable signatures, but unsupported coroutine and
    generator callables still reached the synchronous subprocess runner.
  - Status: implemented. Default and staged preflight now reject coroutine,
    generator, and async-generator `evaluate` functions with setup diagnostics;
    CLI overwrite-preflight tests prove existing run artifacts are left intact.

- [x] Tighten validator signatures outside the fixed evaluator call shapes.
  - Evidence: validator contract preflight previously accepted bindable
    variadic and extra-parameter callables even though the documented contract
    listed fixed one-, two-, and three-argument forms.
  - Status: implemented. Default and staged preflight now rejects variadic,
    keyword-only, and extra-parameter `evaluate` signatures while preserving
    the documented fixed call shapes.

- [x] Extend startup preflight guarantees from the CLI to the core `evolve()`
  API.
  - Evidence: direct `evolve()` previously constructed `ProgramDatabase` before
    validator-contract preflight, so invalid validators could replace existing
    artifacts under overwrite policy.
  - Status: implemented for evaluator contracts. Direct `evolve()` now
    preflights default and staged validators before cleanup/manifest writes,
    and a direct API overwrite-preservation test covers the missing-evaluator
    case. Provider-readiness preflight remains separately tracked.

- [x] Add default evaluator and required problem-file shape validation to
  problem setup.
  - Evidence: problem loading previously accepted directory-shaped
    `validate.py` and raised raw filesystem errors for directory-shaped
    task/metric/context-manifest inputs.
  - Status: implemented. `load_problem()` validates required setup files and
    optional context manifests as regular non-link files before reading, with
    loader and CLI problem-load diagnostics tests covering directory-shaped
    inputs.

- [x] Add strict metric/context schema key validation to problem setup.
  - Evidence: top-level `metrics.yaml` fields beyond `metrics` were ignored,
    and mixed-type metric/context mapping keys could raise raw sorting errors.
  - Status: implemented. Problem loading rejects unsupported metric-schema root
    fields plus non-string keys in metric-schema and context-manifest mappings,
    with loader, direct `Problem`, and CLI diagnostics tests.

- [x] Add direct `Problem` setup validation to runtime hardening.
  - Evidence: direct `Problem(...)` objects previously bypassed empty-task and
    no-seed setup checks until `evolve()` could write zero-evaluation manifests.
  - Status: implemented at the public evolution boundary. `evolve()` rejects
    empty task text and missing seed programs/workspaces before cleanup or
    manifest writes; tests cover artifact preservation for these failures.

- [x] Add full-workspace evolve-block validation after mutations.
  - Evidence: mutation validation was target-local, so successful edits could
    leave malformed markers in untouched siblings or newly created files.
  - Status: implemented. `apply_workspace_mutation()` validates marker
    structure across the full resulting file set before success, and direct
    `Program` construction rejects malformed marker layouts before archive/log
    paths can persist them.

- [x] Add tokenizer-error handling to evolve-block marker parsing.
  - Evidence: marker parsing relies on Python tokenization to avoid treating
    marker-looking strings as comments, but tokenization failures previously
    erased raw marker visibility.
  - Status: implemented. Tokenization failures now become marker diagnostics
    when raw evolve-block marker lines are present, with tests for invalid
    Python before markers, valid marker-looking literals, and unmarked text.

- [x] Add always-on primary-file path validation to candidate-record hardening.
  - Evidence: workspace path validation applied when `Program` had files or
    non-empty code, but empty records bypassed it and could persist unsafe
    `primary_file` values before later workspace reconstruction failed.
  - Status: implemented. Every `Program` now canonicalizes through
    `CandidateWorkspace` at construction time, including empty records, so
    unsafe primary paths are rejected before history/archive/database use.

- [x] Align `Program` empty-file defaults with workspace defaults.
  - Evidence: `CandidateWorkspace()` created a default empty `main.py`, but
    `Program(fitness=0.0)` previously preserved `files == {}` and only
    reconstructed `{"main.py": ""}` through `program.workspace()`.
  - Status: implemented. Empty `Program` objects now store the same canonical
    default workspace as `CandidateWorkspace`, and tests cover direct
    construction, database logging, CLI show inspection, and workspace access.

- [x] Add objective-schema validation to manifest/database hardening.
  - Evidence: the loop recorded `problem.objective_schema()` in startup
    manifests, but the lower database boundary still accepted arbitrary or
    missing objective-schema payloads.
  - Status: implemented. `ProgramDatabase` now validates objective-schema
    payloads before startup manifest serialization, rejects missing or
    inconsistent schemas, and persists the canonical schema shape used by
    normal `evolve()` runs.

- [x] Add archive/log transaction semantics to database hardening.
  - Evidence: strict JSONL serialization rejected invalid candidate rows, but
    archive insertion could already have happened before the strict write
    failed.
  - Status: implemented for accepted archive admission. `ProgramDatabase.admit()`
    prevalidates the candidate history record before live archive insertion, so
    non-serializable accepted candidates cannot become best programs, parents,
    inspirations, or migration sources without a strict history representation.

- [x] Add admission-threshold type validation to archive hardening.
  - Evidence: admission thresholds are archive policy values, but the direct
    database boundary trusted caller-supplied values.
  - Status: implemented. `ProgramDatabase.admit()` rejects boolean, nonnumeric,
    and non-finite thresholds before archive mutation, with tests covering
    malformed direct values and preserving valid finite thresholds.

- [x] Add failure-history transaction semantics to database hardening.
  - Evidence: failure-memory records have a separate quarantine path, but
    in-memory failure state previously advanced before persistence succeeded.
  - Status: implemented. Generated and seed failure rows now append strict JSONL
    before mutating repetition counters or candidate `failure_record` metadata;
    invalid rows quarantine without advancing in-memory failed-trial state.

- [x] Harden failure-summary rendering for malformed evaluation payloads.
  - Evidence: failure-history rows summarize `evaluation.stages` for later
    prompt context and run inspection, but the summary builder trusted the raw
    shape before the strict JSONL/quarantine boundary.
  - Status: implemented. Failure-summary construction now accepts malformed
    stage containers and non-dict entries, preserves compact diagnostics in
    accepted failure rows, and covers generated plus seed failures in tests.

- [x] Add generated-failure archive admission provenance to database hardening.
  - Roadmap evidence: failure history and archive admission are both part of
    the run database, but generated-candidate failure rows did not previously
    join those two views.
  - Status: implemented. `evolve()` now computes archive admission before
    generated failure logging, and generated failure records include
    `admission_reason` plus `archive_admission` metadata like seed failure
    records.

- [x] Make run inspection workspace-aware before presenting codebase-candidate
  support as complete.
  - Evidence: `history.jsonl` can store `files` plus `primary_file`, and run
    completion can export `best_workspace/`, but `cli.show()` previously
    printed only the selected primary-file `code`.
  - Status: implemented. `libreevolve show` now renders the selected logged
    workspace with a primary-file marker, file manifest, and each file's
    content when history includes `files` plus `primary_file`. Tests cover
    non-primary helper files and legacy single-code histories.

- [x] Add field-level schema validation to run inspection.
  - Evidence: run inspection already had malformed JSON/non-object and
    finite-fitness checks, but not all fields it printed were validated.
  - Status: selected `show` records now receive a minimal display schema check
    before output. Malformed generation, missing/list-valued code, bad metrics,
    malformed workspace files, and malformed archive-summary fields all fail
    with line-numbered diagnostics, and tests prove bad generation values are
    not printed before the error.

- [x] Add mixed history-schema handling to run inspection.
  - Evidence: the compact inspector previously had a legacy fallback only when
    no row contained `metadata.archive_admission`.
  - Status: implemented a homogeneous-schema policy for `show`. Legacy-only
    and current-only histories keep their existing selection paths; mixed
    histories fail with a line-numbered diagnostic that names the first legacy
    row and first archive-admission row. CLI tests cover both mixed ordering
    cases.

- [x] Disambiguate archive admission from cell-grid changes in database and
  reporting work.
  - Evidence: MAP-Elites cell occupancy, auxiliary elite-list retention, and
    occupied-cell sampling eligibility are different archive states.
  - Status: implemented split admission-event booleans for cell admission,
    elite retention, search-state change, and sampling eligibility. `show`
    reports the distinction, README/run-artifact docs describe the sampling
    policy, and tests cover elite-only retention separately from cell entry.

- [x] Add primary-aware metric-leader ordering to parent/inspiration sampling.
  - Evidence: metric-leader sampling previously depended on alphabetical
    normalized-metric names.
  - Status: metric leader order now comes from objective schema: primary first,
    configured secondary metrics next, and unconfigured normalized metrics
    last alphabetically. Parent `metric` sampling and inspiration `metric` /
    `mixed` sampling use that order, with tests for small-`k` behavior.

- [x] Define whether mixed inspiration sampling is a priority cascade or a
  stochastic mixture.
  - Evidence: `mixed` previously returned deterministic prefixes under small
    inspiration budgets without naming that policy.
  - Status: documented and tested the current deterministic priority cascade:
    metric leaders, novelty-ranked candidates, selection-score leaders, then
    random fill. Weighted/stochastic mixing remains a future policy, not the
    current default.

- [x] Add insertion-order recency semantics to parent/inspiration sampling.
  - Evidence: recency previously used generation before score, so same-generation
    candidates were not ordered by actual archive update order.
  - Status: archive updates now receive a monotonic sequence that is persisted
    in accepted history records and used by recency parent/inspiration
    strategies before generation and score tie-breaks.

- [x] Add typed program-record validation before sampling restored/direct
  candidates.
  - Evidence: recency sampling assumes comparable candidate generation values.
  - Status: non-negative integer generations are now enforced at `Program`
    construction, raw island archive insertion, database admission, and
    normal/failure history persistence. Broader metric-vector validation remains
    separately tracked.

- [x] Add typed metric-vector validation for direct/restored program records.
  - Evidence: evaluator output validation already enforces declared scalar
    metrics, but direct/restored `Program.metrics` previously bypassed that
    type boundary.
  - Status: direct program metric vectors now require non-empty string keys,
    boolean only for `is_valid`, and finite numeric values everywhere else
    before archive insertion, sampling, admission, or accepted history
    persistence.

- [x] Close public raw archive insertion validity bypasses.
  - Evidence: public database and direct MAP-Elites insertion previously could
    bypass evaluator validity.
  - Status: raw MAP-Elites/island/database insertion now requires
    `evaluation.is_valid is True` before mutating archive state. Invalid direct
    inserts return rejected events and do not affect `best()` or sampling.

- [x] Add direct archive-constructor validation to population hardening.
  - Evidence: direct lower-level archive construction previously accepted
    invalid MAP-Elites bins, elite archive size, and performance bounds.
  - Status: `MAPElites.__init__()` now enforces positive integer bins, positive
    integer elite archive size, and finite ordered performance bounds, with
    direct-constructor tests.

- [x] Add atomic best-artifact export to operational durability work.
  - Evidence: the CLI best exporter previously wrote `best.py`, deleted
    `best_workspace/`, and only then materialized the workspace.
  - Status: the CLI now stages `best.py` plus `best_workspace/` together,
    replaces the visible pair only after workspace materialization succeeds,
    rolls back to the previous pair if replacement fails, and documents the
    behavior in the run-artifacts and architecture docs. Manifest-backed export
    status and hashes remain tracked as separate active durability work.

- [x] Add strict JSON object-key validation to run-artifact writers.
  - Evidence: strict finite JSON previously did not prove JSON object names
    were round-trip safe.
  - Status: the shared strict JSON helper now rejects non-string object keys
    recursively before any manifest, candidate, failure, prompt, plugin, GRPO,
    or quarantine record is written. Error messages identify the offending
    path, and tests cover integer, boolean, null-like, float, and nested
    duplicate-stringification cases.

- [x] Make strict JSONL diagnostics and quarantine snapshots robust.
  - Evidence: malformed direct/plugin records could previously escape the
    quarantine path through cycles, excessive nesting, or hostile `repr()`.
  - Status: strict JSON preflight now detects circular references and excessive
    nesting before serialization, and quarantine diagnostics use bounded,
    redacted, exception-safe record snapshots while preserving the original
    serialization error. Focused tests cover manifest preservation, accepted
    JSONL suppression, quarantine rows, hostile `repr()`, large reprs, and
    secret-like repr contents.

- [x] Preserve initial-seed source paths in run provenance.
  - Evidence: seed/proposal source markers distinguish raw seed baselines from
    prompt-generated candidates, but the run also needs the specific
    `initial_programs/` artifact that produced each seed row.
  - Status: loaded file and directory seeds now carry safe relative source
    identity from problem loading through seed evaluation, history rows,
    failure rows, and startup manifests. Direct in-memory seeds are marked as
    `inline`; loaded seeds include source path, source kind, index, primary
    file, file count, and file list.

- [x] Add exact workspace-snapshot materialization to runtime hardening.
  - Evidence: full-workspace artifacts should not accumulate stale files when a
    materialization target is reused.
  - Status: candidate workspace materialization now treats the target as an
    owned snapshot root, preserves it on preflight failures, rejects
    link/junction roots or children, and removes stale non-link entries before
    writing the current candidate file set. README, problem-format,
    architecture, and run-artifact docs describe the policy.

- [x] Add ambiguous SEARCH-match detection to mutation parsing work.
  - Evidence: repeated SEARCH text previously edited the first occurrence,
    which was an implicit ordering policy rather than an unambiguous target.
  - Status: diff parsing now surfaces deterministic `ambiguous_search_match`
    diagnostics for duplicate matches in whole-file and evolve-block-restricted
    scopes before partial application. Focused tests cover whole-file,
    single-block, and multi-block ambiguity.

- [x] Add command-section body validation to topology mutation hardening.
  - Evidence: topology command sections previously discarded body text.
  - Status: `DELETE`, `MOVE`/`RENAME`, and `PRIMARY` sections now require empty
    bodies and fail with `unexpected_command_body` before any topology change.

- [x] Add duplicate primary-topology rejection to candidate fidelity.
  - Roadmap evidence: workspace topology mutation support covers delete,
    move/rename, and primary-file reassignment, so duplicate primary commands
    need the same no-partial-apply semantics as duplicate edits.
  - Status: multiple `PRIMARY` sections now fail with
    `primary:duplicate_primary_section` before the workspace is changed.

- [x] Add order-independent topology validation for move-created primary files.
  - Evidence: logically equivalent topology mutations should not succeed or
    fail based only on whether `PRIMARY` appears before or after the `MOVE` that
    creates its target.
  - Status: primary reassignment is now deferred until after same-mutation
    file edits, deletes, and moves. Tests cover `PRIMARY` targets created by
    same-mutation moves and full-mode file creation.

- [x] Add delete-primary reassignment policy to candidate fidelity.
  - Roadmap evidence: workspace topology mutation support should define the
    entrypoint policy when the primary file itself is deleted.
  - Status: deleting the current primary now requires an explicit replacement
    `PRIMARY` command; otherwise the mutation fails with
    `primary_deleted_requires_primary` before changing the workspace.

- [x] Add configuration-reference completeness for sampling strategies.
  - Roadmap evidence: reproducible AlphaEvolve-style experiments depend on
    visible parent and inspiration sampling configuration.
  - Status: `docs/configuration.md` documents `parent_selection_strategy` and
    `inspiration_strategy`, including defaults, allowed values, mixed-policy
    behavior, metric ordering, and recency semantics. The fields are also
    exposed through `Config`, CLI overrides, README text, and run manifests.
  - Verification: `tests/test_agents_docs.py` includes
    `test_configuration_docs_track_sampling_strategy_fields`, which asserts the
    configuration reference contains both fields and their strategy sets.

- [x] Extend plugin metadata validation from labels to values.
  - Roadmap evidence: plugin provenance and artifact metadata are persisted in
    candidate history and runtime manifests.
  - Status: plugin metadata now has value-level validation and sanitization:
    display-safe strings, bounded string length, JSON-safe nested values,
    finite numeric values, and shared secret-pattern redaction.
  - Verification: focused loop tests cover prompt-context metadata and
    run-artifact metadata values in both reject and redaction paths.

- [x] Add mixed-type nested config key handling to configuration hardening.
  - Roadmap evidence: configuration validation is part of setup and
    reproducibility hardening.
  - Status: nested evaluator-stage, backend, and LLM-feedback mapping keys must
    be strings before unsupported-field checks run, so malformed mixed-key
    config now fails with `ConfigError` instead of raw Python `TypeError`.
  - Verification: direct `Config` tests and CLI `config.yaml` tests cover the
    three nested sections.

- [x] Add ambiguous candidate path spelling to path hardening.
  - Roadmap evidence: stable codebase-candidate file identities are part of
    reproducible mutation, evaluation, artifact export, and future resume.
  - Status: candidate path normalization now treats ambiguous raw spellings as
    unsafe. Empty components, `.` components, leading `./`, redundant
    separators, and trailing separators fail at workspace and mutation command
    boundaries instead of being rewritten to a different canonical spelling.
  - Verification: focused candidate tests cover the normalizer and full-mode
    file-section, move-target, and primary-target diagnostics.

- [x] Add generated hidden-file policy to candidate path hardening.
  - Roadmap evidence: generated codebase candidates should not silently add
    dot-prefixed files or directories that can carry secrets or repository
    control state.
  - Status: candidate path normalization now rejects dot-prefixed components,
    making generated `.env`, `.git/config`, and nested hidden files invalid
    across direct workspaces, mutation envelopes, topology commands,
    materialization, validation, and best-workspace export.
  - Verification: focused candidate tests cover direct and mutation-boundary
    hidden path diagnostics.

- [x] Add candidate path-length limits to workspace fidelity hardening.
  - Roadmap evidence: invalid generated workspaces should fail before
    evaluation/export rather than surfacing as host-filesystem write errors.
  - Status: candidate path hardening now includes a portable length policy:
    255 characters per component and 1024 characters for the normalized
    relative path. The same validation covers direct workspaces, restored
    workspaces, file sections, move targets, primary reassignment, evaluator
    materialization, and best export.
  - Verification: focused candidate tests cover direct and mutation-boundary
    length diagnostics.

- [x] Add unknown block-target rejection to mutation-envelope work.
  - Roadmap evidence: full-block replacement should not silently drop named
    sections that target no current evolve block.
  - Status: `_apply_full_replacement()` now checks parsed block-section names
    against the candidate's evolve-block names before applying replacements.
    Unknown names return `malformed_block_sections:unknown_name`.
  - Verification: focused candidate tests cover all-unknown and mixed
    known/unknown responses without partial apply.

- [x] Add empty-file creation semantics to workspace full-file mutations.
  - Roadmap evidence: workspace topology/full-file support should represent
    file membership independently from non-empty text content.
  - Status: full-mode unknown-file creation now treats a missing file as a new
    member even when the parsed body is empty, while existing empty files still
    use normal no-change detection.
  - Verification: focused candidate tests cover empty and blank creation plus
    existing-empty no-op behavior.

- [x] Add explicit missing-package-metadata status to provenance hardening.
  - Roadmap evidence: runtime-environment provenance is part of the
    manifest/reproducibility track.
  - Status: absent project metadata now produces typed
    `package.pyproject.status: missing` provenance instead of a null
    `package.pyproject` record. Runtime provenance also records the fallback
    package name used for installed-version lookup.
  - Verification: provenance tests cover present, missing, unreadable,
    invalid-TOML, and invalid-encoding package metadata states.

- [x] Add semantic `pyproject.toml` schema validation to environment
  provenance.
  - Roadmap evidence: runtime-environment provenance is treated as manifest
    evidence.
  - Status: semantically invalid dependency/build requirement metadata now
    degrades package provenance to `invalid_pyproject_schema` instead of
    emitting stringified dependency rows. Diagnostics include the malformed
    field path while preserving the `pyproject.toml` hash and byte count.
  - Verification: provenance tests cover valid, non-list, non-string,
    malformed, and redacted private-source requirement cases.

- [x] Anchor Git provenance to the source tree in run metadata.
  - Roadmap evidence: reproducible experiment metadata should identify the VCS
    state of the implementation source that produced the run.
  - Status: run manifests now resolve Git metadata from the hashed
    `libreevolve/` source root instead of `Path.cwd()`. README, architecture,
    and run-artifact docs describe the source-root interpretation.
  - Verification: a loop regression test covers launching a run from outside
    the repository while preserving source-root Git lookup.

- [x] Add secret-safe dirty Git status provenance.
  - Roadmap evidence: run manifests need dirty-state detail without retaining
    raw credential-like local path strings.
  - Status: dirty Git status now records counts, redacted porcelain entries,
    hashes of the original raw entries, and a redaction flag. Runtime docs
    describe this policy and keep source/problem tree path retention as a
    separate open gap.
  - Verification: a focused Git-state test covers secret-like untracked paths
    plus ordinary modified/renamed paths.

- [x] Add secret-safe source/problem provenance path policy.
  - Roadmap evidence: source/problem tree hashes are run-manifest
    reproducibility evidence, but path retention also needs a data-retention
    boundary.
  - Status: source/problem tree provenance now stores ordinary relative paths
    unchanged, redacts secret-like path text, and adds `path_hash` plus
    `path_redacted` when redaction occurs. Skipped path diagnostics use the same
    policy.
  - Verification: provenance tests cover secret-like included and skipped paths
    while existing ordinary path assertions continue to pass.

- [x] Add skipped-source diagnostics to provenance digest policy.
  - Roadmap evidence: provenance hardening tracks source/problem hashes,
    skipped paths, generated-root exclusion, and symlink traversal.
  - Status: `tree_hash` is documented and emitted as an included-file digest,
    `skipped_hash` covers skipped diagnostic records, and `provenance_hash`
    combines the included-file digest, skipped-diagnostics digest, and
    exclusion-directory policy without reading skipped file contents.
  - Verification: focused provenance tests prove excluded cache directories
    alter skipped/provenance digests but not `tree_hash`, and changing skipped
    file bytes does not affect any digest because skipped contents are not
    hashed.

- [x] Add secret-safe plugin module provenance path policy.
  - Roadmap evidence: plugin module hashes are part of run manifests, but raw
    absolute module paths leak local checkout or external plugin locations.
  - Status: plugin provenance now persists project-relative paths for files
    under the repository and basename-only external markers for files outside
    it. All file-backed plugin records include a raw-path hash and path scope;
    no-file plugin modules remain represented with `path: null`.
  - Verification: focused provenance tests cover ordinary project-local plugin
    modules, external secret-like plugin paths, and missing module files.

- [x] Add secret-safe evaluator metadata path policy.
  - Roadmap evidence: evaluator entrypoints are constrained and hashed in the
    manifest, but per-candidate evaluation metadata also needs a path-retention
    boundary.
  - Status: persisted evaluator metadata now records problem-relative
    validator paths plus hash/scope/redaction fields. Configured absolute
    stage paths are also rewritten in nested stage config and retry-attempt
    metadata before history persistence.
  - Verification: focused evaluator tests cover ordinary default validators,
    configured relative/absolute stage validators, and secret-like problem
    directory names.

- [x] Make active generated-root exclusion independent of invocation cwd.
  - Roadmap evidence: source/problem provenance is part of reproducibility
    hardening, so the active output-root skip must be tied to effective paths
    rather than the shell directory.
  - Status: direct `problem_provenance()` treats relative generated roots as
    problem-relative. `evolve()` passes the effective run directory as an
    absolute generated root, so manifest problem provenance no longer depends
    on `Path.cwd()` for output-root exclusion.
  - Verification: focused provenance and loop tests cover the problem-relative
    helper behavior and existing runtime manifest paths.

- [x] Add size/read-failure budgets to source and problem provenance hashing.
  - Roadmap evidence: manifest hardening needs bounded and diagnosable
    source/problem tree scans.
  - Status: source/problem provenance has a default `max_file_bytes` cap.
    Over-limit files are skipped before reading with byte diagnostics, read
    failures are recorded as skipped diagnostics, and binary fixtures under the
    cap remain hashable.
  - Verification: focused provenance tests cover large-file skips, binary
    inclusion, read failures, and cap persistence.

- [x] Add size/read-failure budgets to plugin module provenance hashing.
  - Roadmap evidence: plugin module hashing is a separate startup path that can
    involve arbitrary direct/custom plugin modules.
  - Status: plugin module provenance is bounded by `max_file_bytes`, records
    over-limit modules as `skipped_max_file_bytes`, records read failures as
    `read_error`, and preserves namespace/no-file modules as
    `missing_module_file`.
  - Verification: focused provenance tests cover ordinary project-local,
    external, over-limit, unreadable, and no-file plugin module records.

- [x] Add configured-plugin identifier grammar to plugin provenance hardening.
  - Roadmap evidence: plugin aliases are persisted in run manifests and will
    become registry/configuration keys for future plugin configuration.
  - Status: configured plugin names are now manifest-safe ASCII labels and are
    rejected if they match secret-like token or assignment patterns. The
    manifest writer revalidates the config boundary before persistence.
  - Verification: focused config, CLI, and database tests cover direct API,
    mutated-config manifest, and startup-preflight failure paths.

- [x] Add canonical paper-cache manifest hash validation.
  - Roadmap evidence: docs/papers validation needs paper-manifest count and
    hash checks before cache claims are treated as current.
  - Status: paper manifest hashes are now canonical lowercase SHA-256 digests
    in both CSV and JSON. The local validator rejects noncanonical hashes,
    mismatched CSV/JSON rows, documented count drift, and, when requested,
    missing or changed local PDFs.
  - Verification: focused paper-manifest tests plus a local
    `py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs` run
    validated the 24-row local cache.

- [x] Add paper-cache availability semantics to corpus tooling.
  - Roadmap evidence: the paper cache is intentionally split between committed
    manifests and ignored local PDFs.
  - Status: validator output separates historical manifest download metadata
    from machine-local availability with `local_status` and best-effort
    `git_tracked` fields per paper.
  - Verification: focused tests cover missing/present local cache states and
    tracked PDF detection in a temporary Git repository.

- [x] Add manifest-safe backend model-id validation to backend hardening.
  - Roadmap evidence: backend model strings are durable experiment metadata
    even when provider availability is intentionally not checked.
  - Status: config validation defines a manifest-safe model-id grammar and
    rejects control, whitespace, and secret-like values before startup;
    database manifest creation revalidates mutated configs.
  - Verification: focused config, database, and CLI tests cover direct config,
    mutated manifest boundaries, and startup-preflight failure ordering.

- [x] Add evaluator-boundary stage schema validation to cascade hardening.
  - Roadmap evidence: staged evaluation is a task/runtime contract, not only a
    CLI config feature.
  - Status: direct `CascadeEvaluator` construction now validates stage schemas
    with the same validator used by `Config`.
  - Verification: focused evaluator tests cover invalid samples, retries,
    timeouts, thresholds, seeds, and seed/sample cardinality.

- [x] Add safe stage-label grammar to cascade hardening.
  - Roadmap evidence: cascade stage names are persisted into evaluation
    records, prompt summaries, and artifact metadata.
  - Status: stage labels are explicit manifest-safe identifiers and reject
    secret-like values across both config and direct evaluator construction.
  - Verification: focused config/evaluator tests cover unsafe labels and
    direct-boundary failures.

- [x] Prevent configured stages from colliding with built-in stage labels.
  - Roadmap evidence: built-in and configured stage outcomes must remain
    distinguishable in artifacts and prompts.
  - Status: configured stages must be explicitly named, and `diff`, `syntax`,
    and `validate` are reserved for evaluator-generated stages.
  - Verification: focused config/evaluator tests reject reserved names and
    duplicate configured names.

- [x] Add mutable-config revalidation to runtime provenance hardening.
  - Roadmap evidence: mutable configs should not bypass validated experiment
    controls at lower-level database or manifest boundaries.
  - Status: `ProgramDatabase` now calls `config.validate()` before directory
    preparation and startup manifest writes.
  - Verification: direct database tests cover mutated path, identity, scalar
    budget, backend, plugin, and evaluator-stage fields.

- [x] Add safe candidate-id grammar to database and lineage hardening.
  - Roadmap evidence: candidate/program ids are durable database keys used in
    history, archive admission events, parent links, inspiration exclusion, and
    future resume.
  - Status: program ids, parent ids, and lineage entries now share a
    manifest-safe identifier grammar and reject secret-like strings. The
    database revalidates direct/mutated programs before persistence.
  - Verification: focused tests cover unsafe ids, parent ids, lineage entries,
    duplicate logged ids, and failure-history quarantine behavior.

- [x] Add safe LLM feedback label validation to config and telemetry hardening.
  - Roadmap evidence: feedback grader names become LLM call-role suffixes and
    evaluation metadata labels, while feedback metric labels become metric keys
    and persisted config values.
  - Status: feedback `name` and `metric` values now require manifest-safe
    labels and reject secret-like strings at config validation and direct
    `apply_llm_feedback()` boundaries before LLM calls or metric writes.
  - Verification: config and feedback tests cover blank, control-character,
    secret-like, and direct unsafe grader labels.

- [x] Add call-role label validation to LLM telemetry hardening.
  - Roadmap evidence: the per-call `role` passed to `LLMEnsemble.generate()`
    is persisted as scheduler telemetry.
  - Status: call roles and configured backend role metadata now use a
    manifest-safe role grammar and are rejected before scheduler selection when
    invalid.
  - Verification: ensemble/config tests cover blank, malformed, secret-like,
    and non-string role labels.

- [x] Add prompt-payload validation to LLM telemetry hardening.
  - Roadmap evidence: per-call prompt size and prompt hash are scheduler
    telemetry, so malformed prompt payloads should not mutate scheduler
    counters before hashing.
  - Status: non-string prompt payloads are rejected before `_ucb1_select()`,
    leaving `total`, backend counts, call history, and provider calls
    unchanged.
  - Verification: ensemble tests prove non-text prompts are rejected before
    scheduler state changes.

- [x] Make LLM call telemetry snapshots immutable from callers.
  - Roadmap evidence: call telemetry is attached to candidate metadata,
    feedback records, and prompt-history metadata, so returned call records
    should not be live mutable scheduler state.
  - Status: `LLMEnsemble.call_history` and `last_call` now return deep-copied
    telemetry snapshots.
  - Verification: ensemble tests mutate returned telemetry and prove stored
    history is unchanged.

- [x] Validate scheduler strategy names at the ensemble boundary.
  - Roadmap evidence: scheduler strategy choice affects breadth/depth/cost
    behavior and persisted telemetry.
  - Status: `LLMEnsemble` now rejects unsupported strategy names at
    construction.
  - Verification: focused ensemble tests cover unsupported direct strategies.

- [x] Validate direct ensemble exploration coefficients.
  - Roadmap evidence: exploration coefficients are scheduler policy and should
    remain finite and non-negative outside the config path.
  - Status: direct construction rejects negative, non-finite, boolean, and
    nonnumeric exploration coefficients.
  - Verification: focused ensemble tests cover invalid direct coefficients.

- [x] Add direct backend-metadata validation to ensemble scheduling hardening.
  - Roadmap evidence: malformed direct backend metadata can prevent or corrupt
    telemetry before a run-scoped call log exists.
  - Status: direct construction now requires JSON-safe metadata mappings with
    backend-count matching, positive cost/latency/depth values, and safe role
    labels.
  - Verification: focused ensemble tests cover malformed metadata and copied
    successful telemetry.

- [x] Validate retry/fallback scheduler controls outside the config path.
  - Roadmap evidence: retry/fallback controls are backend runtime policy and
    future resumable scheduler state.
  - Status: direct construction now rejects invalid retry counts and
    non-boolean fallback values instead of silently coercing them.
  - Verification: focused ensemble tests cover invalid controls and existing
    retry/fallback behavior.

- [x] Add direct prompt reward-policy validation to prompt database hardening.
  - Roadmap evidence: prompt-program reward normalization, reward modes, and
    exploration coefficients are scheduler policy and future resumable
    prompt-state fields.
  - Status: `PromptDatabase` now validates direct reward bounds, reward mode,
    and exploration coefficient at construction, matching the `Config` path
    before prompt scoring or prompt-history writes can happen.
  - Verification: focused prompt tests cover zero-width/inverted bounds,
    non-finite and boolean numeric inputs, unsupported reward modes, and
    negative exploration coefficients.

- [x] Add prompt-program state and id-collision validation to prompt archive
  hardening.
  - Roadmap evidence: prompt-history records and candidate `prompt_program_id`
    links rely on stable prompt-program identity and lineage.
  - Status: `PromptProgram` and `PromptDatabase.add()` now validate ids,
    parent ids, generation/use counters, reward sums, JSON-safe metadata,
    duplicate ids, and unknown parents before insertion or logging.
  - Verification: focused prompt tests cover malformed state at construction,
    revalidation of mutated prompt programs, duplicate ids before logging, and
    unknown parent ids.

- [x] Add dangling prompt-reference diagnostics to prompt archive hardening.
  - Roadmap evidence: prompt rewards, prompt mutations, and candidate history
    are connected by prompt-program ids; replay and resume need explicit
    diagnostics when a referenced prompt arm is missing or malformed.
  - Status: scoring and mutation lookups now emit bounded
    `prompt_reference_error` rows in `prompt_history_invalid.jsonl` and raise
    `StrictJsonlError` for missing or invalid prompt-program ids.
  - Verification: focused prompt tests cover missing score references,
    missing mutation references, unchanged accepted history, and redacted
    invalid-id diagnostics.

- [x] Condition meta-prompt mutations on prompt-performance evidence.
  - Roadmap evidence: prompt mutation should see prompt rewards, candidate
    outcomes, active reward policy, and failure/rejection evidence when it is
    asked to improve future prompt behavior.
  - Status: the loop now renders a bounded redacted meta-prompt mutation
    context containing reward policy, selected prompt statistics, latest
    candidate outcome, prompt-arm summaries, and recent failures, and stores
    context hash/provenance in prompt-child metadata.
  - Verification: focused loop tests cover evidence-conditioned prompt content,
    redaction of secret-like failed mutation text, and persisted context
    metadata.

- [x] Add explicit-template validation to prompt sampler hardening.
  - Roadmap evidence: prompt template choice is reproducible prompt provenance;
    an explicit template argument should not be discarded by truthiness.
  - Status: direct prompt rendering now distinguishes `template is None` from
    blank explicit strings. Only `None` triggers configured/default fallback;
    blank explicit strings are validation errors.
  - Verification: focused prompt tests cover direct blank-template rejection
    and configured-variant fallback preservation.

- [x] Add context-manifest glob semantics to prompt/context hardening.
  - Roadmap evidence: context provenance records include/exclude rules and
    match counts, so path-matching behavior must be stable before local context
    selection can be treated as auditable.
  - Status: context manifest globs are now path-segment aware. Single-star
    patterns stay within one `/`-separated component and `**` performs
    recursive matching, with README, problem-format, architecture,
    run-artifact, and paper-index docs updated.
  - Verification: focused loader tests cover single-star root matching,
    globstar recursion, nested excludes, and manifest pattern match counts.

- [x] Add cross-file dependency checks to workspace benchmark/examples.
  - Roadmap evidence: candidate-fidelity work includes multi-file/codebase
    candidates and workspace-aware validator behavior.
  - Status: implemented for the `workspace_math` smoke fixture.
    `workspace_math/validate.py` now requires `helpers.py` to expose
    `base_value()`, executes `main.py` with a fake `helpers.base_value()`,
    and reruns `solve()` with a perturbed helper value so a constant-only
    `main.py` cannot pass.
  - Verification: `tests/test_examples.py` covers the valid seed and rejects
    `main.py` returning `42` directly while `helpers.py` returns `41`.

- [x] Add quoted-assignment coverage to redaction hardening.
  - Roadmap evidence: runtime, prompt, evaluator, plugin, and manifest
    hardening all rely on the shared redaction helper to make artifacts
    collaboration-safe.
  - Status: implemented in `libreevolve.core.redaction`. Quoted assignments
    with whitespace are consumed as one secret value, while existing bare-token
    assignment redaction remains covered.
  - Verification: `py -3.12 -m pytest tests/core/test_redaction.py --tb=short`
    passes with quoted, whitespace-containing, and unclosed quoted assignment
    fixtures.

- [x] Add provider-token casing coverage to shared redaction hardening.
  - Evidence: runtime redaction should behave predictably across provider
    output, logs, paths, prompt histories, and artifacts.
  - Status: implemented by making the shared known-provider token pattern
    case-insensitive.
  - Verification: `py -3.12 -m pytest tests/core/test_redaction.py --tb=short`
    passes with lowercase, uppercase, mixed-case, and assignment-shaped
    provider-token examples.

- [x] Add stage-seed redaction/validation to evaluator cascade provenance.
  - Roadmap evidence: evaluation cascades expose stage names, samples, retries,
    seeds, artifacts, and retry/sample metadata as run evidence.
  - Status: implemented in the shared eval-stage validator. Secret-like seed
    strings are rejected at both config validation and direct evaluator-stage
    validation.
  - Verification: `py -3.12 -m pytest tests/core/test_config.py
    tests/core/test_redaction.py --tb=short` passes with stage-seed fixtures
    covering provider-token, uppercase-token, assignment-shaped, and bearer
    forms.
- [x] Add immutable evaluator-stage snapshots to cascade hardening.
  - Roadmap evidence: evaluation cascades, resumability, and run manifests
    require the stage definitions used by an evaluator to remain stable after
    validation.
  - Previous evidence: direct `CascadeEvaluator` stored the caller-supplied
    `stages` list by reference. A proof mutated a validated stage after
    construction, changing `samples` from `1` to `"not-an-int"`; the next
    evaluation failed with a raw `ValueError` during `int(...)` conversion.
  - Status: implemented. `CascadeEvaluator` now snapshots stage specs by deep
    copy before validation and stores the validated snapshot; regression tests
    cover post-construction mutation of nested fields.
- [x] Add immutable backend-arm snapshots to LLM scheduler hardening.
  - Roadmap evidence: backend scheduling, UCB-style state, and future
    resumability require the scheduler's arm list to stay consistent with
    counts, rewards, metadata, and call telemetry.
  - Previous evidence: `LLMEnsemble` retained the caller's mutable backend
    list. A proof appended a backend after construction and the next scheduler
    call raised `IndexError`; clearing the same list left stale scheduler
    arrays and raised `AssertionError`.
  - Status: implemented. The ensemble now snapshots backend arms at
    construction, and regression tests cover post-construction mutation of the
    caller-owned list.
- [x] Add immutable candidate-workspace snapshots to codebase-candidate
  hardening.
  - Roadmap evidence: multi-file/codebase candidates are roadmap-level search
    units, so their validated file-set topology should not change behind the
    evaluator, prompt sampler, archive, or run-artifact exporters.
  - Previous evidence: `CandidateWorkspace` validated at construction but kept
    mutable `files` and `primary_file`. A proof mutated those fields after
    construction and triggered raw `KeyError`, `ValueError`, and `TypeError`
    failures during `code` access and materialization.
  - Status: implemented as boundary revalidation. `CandidateWorkspace` now
    snapshots/revalidates state for `code`, `to_dict()`, and `materialize()`;
    regression tests cover mutated primary, path, content, and normalized path
    invariants.
- [x] Add immutable prompt-program records to meta-prompt hardening.
  - Roadmap evidence: meta-prompt evolution, prompt DB/archive replay, and
    prompt lineage require selected prompt arms to remain the validated records
    that were admitted and persisted.
  - Previous evidence: `PromptDatabase` kept live `PromptProgram` objects. A
    proof mutated an admitted prompt template after `add()` and `select()`
    returned the invalid template; another proof mutated the object returned by
    `all()` and changed selected seed state.
  - Status: implemented. The prompt database now snapshots prompt programs at
    archive admission and returns defensive copies from query/selection APIs;
    regression tests cover post-admission mutation of templates and metadata.
- [x] Add normalized-metric integrity checks to metric sampling.
  - Roadmap evidence: roadmap multi-objective search and parent/inspiration
    sampling depend on normalized metric vectors that faithfully reflect the
    declared objective schema.
  - Previous evidence: metric sampling trusted `metadata.normalized_metrics`
    directly. A proof used a candidate with `fitness=0.1` and
    `normalized_metrics.score=999.0`; metric parent and inspiration sampling
    selected it ahead of an honest `score=0.9` candidate.
  - Status: implemented. `IslandModel` metric leaders now require normalized
    metric values to be finite numbers in `[0, 1]` and use configured
    `metric_order` as a metric-name allowlist; tests cover parent and
    inspiration sampling.
- [x] Add direct inspiration-count validation to database/search hardening.
  - Roadmap evidence: configurable parent/inspiration sampling should have the
    same typed policy whether invoked by the synchronous loop, future async
    controller workers, resume loaders, or direct library calls.
  - Previous evidence: direct `MAPElites.sample_diverse(k=...)` and
    `IslandModel.sample_diverse(k=...)` bypassed `Config.num_inspirations`
    validation. String `k` values raised raw `TypeError`, while boolean and
    float values could be treated as a request for one sample.
  - Status: implemented. Direct `k` values are validated at all current public
    sampling boundaries; tests cover zero, oversized counts, strings, booleans,
    floats, and negative integers.

- [x] Add sampling exclusion-set validation to database/search hardening.
  - Roadmap evidence: parent/inspiration sampling should be reproducible across
    the synchronous loop, future async workers, and resume loaders; exclusion
    sets are part of that controller state.
  - Previous evidence: direct archive sampling accepted arbitrary
    `exclude_ids` containers. Strings, lists, mappings, and custom membership
    objects changed sampling behavior through Python membership semantics,
    while integers raised raw `TypeError`.
  - Status: implemented. `ProgramDatabase`, `IslandModel`, and `MAPElites`
    now validate and normalize exclusion-set schemas, reject malformed
    containers with stable diagnostics, and have regression coverage for
    duplicate ids, custom containers, and direct parent/inspiration exclusion.

- [x] Add backend-metadata key validation to LLM telemetry hardening.
  - Evidence: direct `LLMEnsemble` construction validated backend metadata
    values but not key labels, allowing secret-like and bidi/control labels to
    survive into `call_history[0].backend_metadata`.
  - Previous roadmap gap: backend hardening covered configured specs,
    object-derived telemetry fields, mutable metadata values, roles, and
    provider response shapes, but not key-label safety for custom/direct or
    restored backend metadata.
  - Status: implemented. Backend metadata keys are now validated recursively
    before ensemble construction completes; tests cover direct/custom metadata,
    nested keys, call-history telemetry, and no-call rejection for unsafe
    labels.

- [x] Add first-class `Program.metadata` schema validation.
  - Roadmap evidence: queryable evolutionary databases, resumable run state,
    prompt lineage, backend telemetry, and archive diagnostics all rely on
    candidate metadata being a structured mapping.
  - Previous evidence: `Program` accepted non-mapping metadata. Direct proofs
    logged `metadata=[]` as a JSON array and crashed archive admission with
    raw `dict(program.metadata)` conversion errors.
  - Status: implemented. Model-level and database-boundary validation now
    enforce JSON-safe mapping metadata, reject display-unsafe keys, redact
    secret-like string values, and prevent malformed metadata from mutating
    archive/history state. Legacy history migration and richer size-limit
    policy remain open roadmap work.

- [x] Add JSON-native direct metric validation to database hardening.
  - Evidence: direct or restored program records can bypass evaluator metric
    normalization and still enter the database boundary as `Program.metrics`.
  - Previous evidence: `validate_program_metrics()` accepted finite
    `numbers.Real` subclasses that strict JSON could not persist, including
    `Fraction`.
  - Status: implemented by rejecting unsupported numeric types. Program,
    database, island, and MAP-Elites boundaries now enforce JSON-native finite
    metric values before archive/log mutation; tests cover direct APIs,
    restored/mutated records, history logging, and archive insertion.

- [x] Add direct LLM feedback numeric-policy validation to evaluation
  hardening.
  - Roadmap evidence: LLM feedback/reviewer scoring is a roadmap-level
    evaluation feature, and score-composition rules need the same validated
    behavior whether graders come from `Config` or direct API calls.
  - Previous evidence: direct `apply_llm_feedback()` accepted malformed
    `weight` or `min_score`, called the LLM, parsed the score, and only then
    failed during `float(...)` conversion.
  - Status: implemented. Direct feedback numeric policy is validated early,
    `include_invalid` must be boolean, malformed graders produce structured
    diagnostics, and failed graders cannot mutate candidate metrics or
    fitness.

- [x] Require strict finite JSON for feedback-grader diagnostic prompts.
  - Evidence: `_render_feedback_diagnostics()` used default `json.dumps(...)`
    for evaluator diagnostics, allowing `NaN` and `Infinity` tokens inside LLM
    feedback prompts.
  - Previous roadmap gap: evaluation hardening tracked finite metrics and
    feedback score parsing, but did not require reviewer prompt diagnostics to
    be strict JSON.
  - Status: implemented. Non-finite diagnostic values are normalized at the
    feedback prompt boundary, strict JSON rendering is enforced, and tests
    cover top-level plus stage non-finite values.

- [x] Add failure-history redaction to database retention hardening.
  - Evidence: failure-memory records are durable JSONL artifacts and later
    prompt inputs, so truncation alone was not enough for retained mutation
    snippets and evaluator summaries.
  - Previous evidence: generated failure rows could preserve secret-like
    mutation text, evaluator error, stdout, and stderr values verbatim.
  - Status: implemented. Generated and seed failure records apply shared
    redaction before persistence and before attaching `metadata.failure_record`;
    tests cover mutation text, evaluator error/stdout/stderr, stage errors,
    string diff errors, seed failures, metadata mirrors, and prompt-rendered
    recent failures from persisted records.

- [x] Add structured failure mutation-snippet redaction to prompt hardening.
  - Roadmap evidence: failed-trial memory is now rendered into prompts, and
    evaluator summaries use bounded redaction helpers, so mutation snippets
    need the same safety boundary.
  - Previous evidence: `_render_failure_line()` inserted structured
    `failure["mutation_text"]` after only newline replacement and a
    160-character slice, preserving secret-like tokens.
  - Status: implemented. Structured dict failure mutation snippets, `error`,
    and `diff_error` fields now use shared prompt redaction/truncation, with
    regression coverage for structured dict failures.

- [x] Add failed-trial prompt score validation to prompt hardening.
  - Roadmap evidence: failed-trial memory is prompt-visible search evidence,
    and roadmap prompt hardening already tracks failure-record safety,
    redaction, and schema validation.
  - Previous evidence: `_render_failure_line()` treated any `int` or `float`
    score as prompt-safe, including booleans and non-finite floats.
  - Status: implemented. Failed-trial scores are validated at render time:
    finite non-boolean numbers render normally, while malformed structured and
    legacy tuple scores render as `unknown`.
- [x] Add recent-failure prompt-memory schema validation to prompt hardening.
  - Roadmap evidence: prompt hardening covers failed-trial memory, feedback,
    redaction, and context packing, so malformed failure-memory records should
    have deterministic diagnostics.
  - Implemented evidence: `PromptSampler` validates recent-failure containers,
    routes valid structured records through the structured renderer, adapts
    exactly two-item legacy tuple records, and emits bounded type-only
    diagnostics for malformed inputs.
  - Verification: `tests/core/test_prompt.py` includes malformed container,
    malformed tuple/list/object, malformed dict-field, valid legacy tuple, and
    valid structured record coverage.
- [x] Add blank-prompt validation to LLM boundary hardening.
  - Roadmap evidence: provider calls, scheduler telemetry, and future
    async/budget accounting should only record meaningful LLM samples.
  - Implemented evidence: `LLMEnsemble.generate()` now fails empty or
    whitespace-only prompts before provider calls, retries, fallback, scheduler
    updates, or call-history records.
  - Verification: `tests/llm/test_ensemble.py` covers direct blank prompts,
    prompt-template paths that render blank text, and valid prompt preservation.
- [x] Add failed-backend cooldown or accounting to scheduler hardening.
  - Roadmap evidence: backend work now includes retry/fallback telemetry and
    pull-once initialization, but not a policy for backends that fail before
    their first successful pull.
  - Implemented evidence: exhausted failed backend selections now increment
    `counts[idx]` once with no reward, removing the zero-count untried state
    that previously forced every recovered fallback call to start with the same
    dead backend.
  - Verification: ensemble tests include fallback/cooldown-equivalent behavior
    for repeated fail-then-fallback calls and disabled fallback accounting.
- [x] Add immutable or revalidated configured backend specs to backend
  hardening.
  - Evidence: `Config.validate()` validates backend specs, but `build_llm()`
    later consumed the mutable nested `config.backends` structure without
    revalidation.
  - Implemented evidence: `build_llm()` now performs construction-time
    validation and normalization of effective backend specs before creating
    adapter instances or scheduler metadata.
  - Verification: ensemble tests cover post-validation mutations of backend
    type/model/tokens, scheduler metadata, role labels, unsupported fields, and
    copied valid metadata.
- [x] Add provider response-shape validation to backend hardening.
  - Evidence: backend adapters assumed provider responses contained usable
    text, and malformed shapes could become parser-only failures or raw
    telemetry errors.
  - Implemented evidence: bundled OpenAI, Anthropic, and Ollama adapters now
    validate extracted provider response text and raise provider-labeled
    failures for missing, empty, whitespace-only, or non-text content.
  - Verification: backend tests cover malformed OpenAI Chat/Responses,
    Anthropic Messages, and Ollama Chat response shapes.

- [x] Add whitespace-only response validation to backend hardening.
  - Roadmap evidence: backend hardening should separate successful LLM samples
    from malformed provider outputs before scheduler rewards and parser
    failures are assigned.
  - Implemented evidence: response validation now rejects whitespace-only
    backend outputs and routes them through the same failed-call retry/fallback
    path as empty or non-text outputs.
  - Verification: ensemble tests prove whitespace-only outputs become failed
    call records rather than successful samples.
- [x] Add LLM response-size limits to backend hardening.
  - Roadmap evidence: budget/resumability work should make provider output
    size part of LLM-call accounting before responses enter mutation parsing,
    candidate metadata, or future call logs.
  - Status: backend hardening now includes a configurable accepted-response
    character cap. Over-limit outputs record failed ensemble attempts with
    output size left at zero, no output hash, normal retry/fallback flags, and
    failed-pull scheduler accounting instead of successful proposal sampling.
    ROADMAP current state now calls out the local accepted-response cap while
    broader token/cost/deadline budgets remain open.
  - Verification: focused scheduler/config/CLI tests passed with
    `py -3.12 -m pytest tests/llm/test_ensemble.py tests/core/test_config.py
    tests/test_cli.py --tb=short`.

- [x] Add immutable/validated LLM scheduler counters to ensemble hardening.
  - Roadmap evidence: LLM ensemble hardening already covers backend specs,
    backend metadata, reward-to-call accounting, and resumable bandit state, but
    not direct mutation of the counter lists that drive routing.
  - Status: `LLMEnsemble` live scheduler counters are private, public state
    reads are defensive copies, and `restore_scheduler_state()` validates
    restored count/reward/total shape and finite values before replacing state.
  - Verification: focused ensemble tests cover immutable read snapshots,
    malformed counts/wins/total inputs, valid restore, and continued generation
    after defensive-copy mutation attempts.

- [x] Add backend-interface call-role propagation to LLM scheduler work.
  - Roadmap evidence: breadth/depth scheduling, critique, feedback graders,
    and meta-prompt evolution all depend on distinguishing LLM call roles at
    scale, not only after-the-fact telemetry labels.
  - Status: the backend protocol already accepts keyword arguments, and
    `LLMEnsemble.generate()` now passes the validated role to backend
    implementations on original, retry, and fallback attempts. Bundled
    OpenAI/Anthropic/Ollama adapters accept and ignore the keyword for now.
  - Verification: focused ensemble tests prove custom role-aware backends
    receive `role`, fallback backends receive `role`, and every retry attempt
    receives `role`.

- [x] Add immutable backend-metadata snapshots to LLM scheduler hardening.
  - Roadmap evidence: backend cost/latency/depth/role metadata affects
    scheduling and telemetry, so validated scheduler controls should not become
    malformed after ensemble construction.
  - Status: `LLMEnsemble` stores backend metadata in a private validated
    snapshot and returns deep copies from the public accessor. Internal
    scheduler selection and call telemetry use the private snapshot.
  - Verification: focused ensemble tests cover post-construction mutation of
    numeric metadata and non-JSON telemetry values across UCB initialization and
    `throughput_depth` selection.

- [x] Add reward-to-call accounting to backend scheduling work.
  - Roadmap evidence: roadmap backend work calls for normalizing UCB rewards and
    persisting scheduler/budget state, so rewards need to be linked to the
    successful pull they score.
  - Status: `LLMEnsemble` now records reward status on successful call
    telemetry, persists rewarded and unrewarded call ids through
    `scheduler_state`, validates restored reward-ledger state, and rejects
    duplicate or invalid reward application. The synchronous loop rewards the
    mutation call id stored in candidate metadata.
  - Verification: focused scheduler tests cover duplicate, missing, delayed,
    malformed restored, and restored reward-ledger behavior; loop tests prove
    normal and discarded candidates pass the captured mutation call id.

- [x] Add recovered LLM failure spans to run-artifact logging.
  - Roadmap evidence: backend work now records retry/fallback telemetry at the
    ensemble boundary, and run artifacts embed role call records in
    candidate/prompt metadata.
  - Status: generated candidate history now embeds the full
    mutation/critique/feedback call span captured from `LLMEnsemble`
    `call_history`, including failed retry/fallback attempts recovered before a
    successful candidate was evaluated. Meta-prompt calls remain attached to
    prompt-history records; a separate run-scoped call log remains future work.
  - Verification: focused loop coverage proves a recovered fallback mutation
    persists both the failed attempt and the rewarded successful backend call in
    candidate `metadata.llm_calls`.

- [x] Add normalization policy for throughput/depth scheduler metadata.
  - Evidence: `throughput_depth` supports cost/latency/depth metadata, and the
    scheduler needs units, ranges, weights, and normalization to be
    reproducible across configs.
  - Status: `LLMEnsemble` normalizes selectable metadata per field with a
    fixed bounded scoring policy and records the effective policy in call
    telemetry. This keeps throughput/depth routing intentional without
    allowing extreme raw metadata to swamp empirical rewards.
  - Verification: focused scheduler tests cover comparable metadata, extreme
    metadata, reward-vs-depth tradeoff, and persisted scheduler-policy
    telemetry.

- [x] Add run-local RNG isolation to reproducibility work.
  - Evidence: seeded replay should not mutate the host Python process's global
    RNG state.
  - Status: `evolve()` now owns a run-local RNG seeded from `Config.seed` and
    passes it through loop, prompt, database/island, and MAP-Elites framework
    sampling. Direct archive/database constructors allocate private RNGs when
    no explicit RNG is supplied.
  - Verification: focused loop and database tests prove framework sampling does
    not reseed or advance caller global RNG state.

- [x] Add direct evaluation-kind validation to runtime budget accounting.
  - Roadmap evidence: runtime accounting splits seed and candidate evaluation
    counters in manifests and future resumability work, so malformed direct
    events should not silently change the accounting class.
  - Status: direct `RunBudget.record_evaluation()` validates exact boolean
    seed/candidate event kind before mutating counters.
  - Verification: focused budget tests prove valid direct events are counted
    correctly and malformed direct event kinds do not mutate counters.

- [x] Add direct finite consumed-budget validation to runtime accounting.
  - Roadmap evidence: runtime accounting tracks consumed evaluator seconds in
    manifests, so direct increments should be strict finite JSON before they
    can reach runtime summaries.
  - Status: direct `RunBudget.record_evaluation()` now rejects malformed
    elapsed-time inputs before counter mutation.
  - Verification: focused budget tests cover negative, non-finite,
    non-numeric, boolean, and valid elapsed-time increments.

- [x] Add current budget snapshot-state schema validation to runtime accounting.
  - Roadmap evidence: run manifests depend on budget snapshots that can be
    persisted and inspected.
  - Status: current `RunBudget` snapshots, limit checks, and finalization
    validate non-negative counters, finite consumed evaluator seconds, coherent
    seed/candidate totals, valid limits, and string-enum stop reasons.
  - Verification: focused budget tests prove malformed current budget state is
    rejected before snapshot, limit-check, or finish outputs are returned.

- [x] Add restored-budget state schema diagnostics to runtime accounting.
  - Roadmap evidence: resumability and run manifests depend on budget snapshots
    that can be persisted, inspected, and eventually restored by controller
    workers.
  - Status: restored budget snapshots now have a schema preflight helper with
    manifest-safe field diagnostics. It validates top-level shape, wall-clock
    metadata, resume segment indexes, limits, consumed counters, finite
    evaluator/runtime seconds, coherent seed/candidate and generation totals,
    and known stop reasons before returning a defensive copy.
  - Verification: focused budget tests cover valid restored snapshots and
    malformed restored budget state across limits, consumed counters,
    timestamps, resume segments, and stop reasons.

- [x] Add backend-object telemetry validation to backend hardening.
  - Evidence: backend specs are validated, but runtime/direct backend objects
    and restored call logs can originate outside `Config.backends`.
  - Status: direct runtime backend object telemetry is normalized before
    call-history and candidate-history persistence, and restored
    `llm_calls.jsonl` rows now validate backend names, API modes, backend
    metadata, and backend telemetry diagnostics before replay. Future
    plugin/registry backends remain covered by the separate plugin-registry
    roadmap gap because that construction surface does not exist yet.
  - Verification: focused ensemble tests cover unsafe live backend telemetry
    and restored call-ledger telemetry rejection.

- [x] Add docs/papers validation to CI and roadmap operational maturity.
  - Roadmap evidence: operational maturity requires documentation, paper-index,
    agent-facing instructions, and TODO status claims to be checked when they
    change, not only when a manual workflow is run.
  - Status: the Tests workflow now has path-scoped automatic triggers for
    `push` and `pull_request` events covering source, tests, docs, TODO
    ledgers, README, ROADMAP, AGENTS, workflow config, secret baseline,
    pyproject, and paper-index files. The existing jobs run secret scanning,
    non-integration tests across Python 3.11/3.12, and optional integration
    tests when credentials are configured. Development docs describe the
    boundary.
  - Verification: `tests/test_agents_docs.py` checks the workflow trigger
    paths and required jobs.

- [x] Add abort-message redaction to manifest hardening.
  - Roadmap evidence: runtime-manifest work preserves abort status, exception
    type, phase/role, and artifact pointers, so exception text needs a
    retention boundary before becoming durable run provenance.
  - Status: abort runtime records now use a redacted/truncated manifest helper
    that preserves structured exception type and phase/role while bounding the
    message field and safely handling broken exception stringification.
  - Verification: focused loop tests cover plugin, provider, and evaluator
    aborts with secret-like payloads plus oversized and unstringifiable
    messages.

- [x] Add completed-run artifact/history summaries to runtime manifests.
  - Roadmap evidence: manifest/runtime work treats manifests as the run's
    durable summary, so completed runs need the same artifact/history pointers
    as aborted runs.
  - Status: normal runtime finalization now records completed-run history
    counts and known artifact/quarantine path pointers, including explicit
    `best.py` / `best_workspace` pointers at core-loop finalization time.
  - Verification: focused loop tests cover seed-only baselines, normal
    generated failure history, and completed runs with plugin artifact roots.

- [x] Add link-aware artifact-pointer metadata to runtime manifest hardening.
  - Roadmap evidence: runtime manifests use `runtime.artifacts` as the compact
    record of generated history/quarantine/artifact streams.
  - Status: artifact pointers now include link/junction/broken-link fields,
    target containment scope, target hashes, and non-following size/type
    semantics for link-like entries.
  - Verification: focused loop tests cover normal files, symlink targets,
    broken symlinks, and Windows junctions where the platform permits them.

- [x] Add filesystem-error tolerance to runtime artifact-pointer collection.
  - Roadmap evidence: aborted-run runtime manifests should preserve phase,
    exception, budget, history, and artifact diagnostics even when the run
    directory is partially corrupt or inaccessible.
  - Status: pointer collection now records bounded, redacted per-artifact
    inspection errors instead of raising from artifact inspection.
  - Verification: focused loop tests cover lstat failures for history,
    quarantine, evaluator-artifact, and plugin-artifact records.

- [x] Add explicit zero-evaluation budget semantics to runtime accounting.
  - Evidence: `RunBudget` permits `max_evaluations=0`, which can complete
    before seed evaluation.
  - Status: zero-evaluation runs now manifest as first-class no-candidate dry
    budget points with explicit history absence diagnostics. Zero evaluator-
    second and zero runtime-second limits are invalid at config validation.
  - Verification: focused loop tests cover `max_evaluations=0`,
    `max_evaluator_seconds=0`, and `max_runtime_seconds=0` startup behavior.

- [x] Define manifest directory-sync crash durability.
  - Evidence: manifest writes used file fsync plus atomic replacement but did
    not sync the containing directory.
  - Status: manifest writes now attempt parent-directory fsync after
    `os.replace()`, and docs distinguish supported directory sync from
    process-visible atomic replacement where directory sync is unavailable.
  - Verification: focused JSON writer tests cover the parent-directory fsync
    path.

- [x] Add corrupt-manifest recovery diagnostics to runtime hardening.
  - Roadmap evidence: manifest durability work should handle current manifests
    that cannot be parsed before a runtime update is attached.
  - Status: runtime updates now quarantine unreadable current manifests and
    recover from the retained startup manifest when possible.
  - Verification: focused database tests cover malformed, empty, non-UTF-8, and
    invalid-replacement recovery cases.

- [x] Add invalid-candidate metric diagnostics to archive API hardening.
  - Evidence: invalid candidates should still produce structured archive or
    rejection diagnostics so they can inform future feedback, replay, and
    database analysis.
  - Status: archive APIs now return `invalid_evaluation` before validating
    malformed metrics for invalid candidates; failure-history helpers preserve
    invalid candidate evidence without crashing on unused malformed metrics.
  - Verification: focused MAP-Elites/database tests cover invalid candidates
    with malformed metric payloads.

- [x] Add raw archive event metadata consistency to database hardening.
  - Evidence: archive state should be reconstructable from persisted candidate
    records.
  - Status: public `ProgramDatabase.add()` now attaches the same
    `metadata.archive_admission` event as `admit()` before history persistence.
  - Verification: focused database tests cover public `add()` plus `log()`.

- [x] Add threshold parity for raw archive APIs to database hardening.
  - Evidence: threshold-ineligible programs should not become elites or parents
    through a public lower-level method.
  - Status: public `ProgramDatabase.add()` now routes through the default
    thresholded admission policy.
  - Verification: focused database tests cover valid negative-fitness rejection
    through `add()`.

- [x] Decide whether non-admitted MAP-Elites candidates may mutate descriptor
  normalization state.
  - Evidence: descriptor normalization should not be affected by candidates
    that do not affect the stored population.
  - Status: non-admitted candidates no longer commit complexity normalization
    state. Complexity descriptor state is updated only when a candidate changes
    archive search state by entering a cell or retained elite list.
  - Verification: focused MAP-Elites tests cover non-admitted long candidates
    and retained elite-only candidates.

- [x] Define short-candidate diversity semantics in MAP-Elites roadmap work.
  - Evidence: short non-empty candidate programs should not collapse to a
    single diversity fallback solely because fixed char 4-grams cannot build a
    vocabulary.
  - Status: MAP-Elites now uses adaptive TF-IDF character n-grams up to length
    4, with lower-order n-grams for short non-empty code and explicit fallback
    behavior for empty code.
  - Verification: focused MAP-Elites tests cover one-character programs and
    empty code.

- [x] Add atomic candidate-workspace materialization to codebase-candidate
  hardening.
  - Evidence: multi-file/codebase candidate work depends on reproducible
    materialized workspaces for validators, best-artifact exports, and future
    worker/controller execution.
  - Status: materialization now writes a complete temporary sibling workspace
    before installing it as the target root, preserving any existing visible
    root if a write fails.
  - Verification: focused candidate tests cover write failures, nested file
    sets, existing roots, and direct public API materialization; evaluator and
    CLI tests cover temp validator roots and exported `best_workspace`.

- [x] Add UTF-8-encodable content validation to codebase-candidate hardening.
  - Evidence: current multi-file candidates are text workspaces materialized
    through UTF-8 writes.
  - Status: direct workspace construction, revalidation, and accepted mutation
    outputs now reject non-UTF-8-encodable text before evaluator/export roots
    are changed.
  - Verification: focused candidate tests cover direct workspaces, mutated
    workspaces, full replacements, and LLM-created files.

- [x] Add linked-ancestor containment to candidate-workspace materialization
  hardening.
  - Evidence: materialized workspaces should be attributable to the configured
    run/evaluator/export root, including on filesystems with symlinks or
    junctions.
  - Status: `CandidateWorkspace.materialize()` rejects existing symlink and
    junction ancestors before resolving the target root.
  - Verification: focused candidate tests cover symlink and Windows junction
    ancestor rejection.

- [x] Add non-dict retrieval body redaction to prompt-context hardening.
  - Evidence: prompt-visible retrieval context should follow the same safety
    boundary whether it comes from structured provider results or custom
    provider objects.
  - Status: DeepResearch retrieval bodies now use a bounded/redacted text
    fallback for dict, string, and arbitrary-object results, with source kind,
    raw length/hash, and redaction/truncation metadata retained. Prompt headers
    label provider/source kind.
  - Verification: focused DeepResearch tests cover string, object, oversized,
    secret-like, and structured dict retrieval outputs.

- [x] Add direct prompt mutation-mode validation to prompt hardening.
  - Evidence: diff/full mutation modes are part of the prompt contract, parser
    contract, and benchmark comparability surface.
  - Status: config and direct prompt rendering now use the shared mutation-mode
    enum, and invalid direct prompt modes fail before rendering.
  - Verification: focused prompt/config tests cover invalid direct values and
    valid diff/full prompt output.

- [x] Add direct prompt-sampler variant validation to prompt hardening.
  - Evidence: prompt variants can come from config today and future
    prompt-program/runtime APIs later, so validation should not depend only on
    the `Config.prompt_variants` path.
  - Status: direct sampler construction and build-time state now share
    renderable-template-list validation with config variants.
  - Verification: focused prompt/config tests cover invalid containers,
    non-string items, invalid templates, mutated sampler state, and valid
    template lists.

- [x] Add direct proposal-metadata flag validation to prompt hardening.
  - Evidence: proposal metadata is part of the generated output envelope and
    downstream candidate metadata extraction.
  - Status: direct `PromptSampler.build()` now requires a real boolean before
    metadata instructions can alter the prompt/output envelope.
  - Verification: focused prompt/config tests cover true, false, and invalid
    string, numeric, container, and arbitrary-object values.

- [x] Add direct `extra_context` schema, redaction, and budget checks to prompt
  hardening.
  - Evidence: explicit context, retrieval snippets, and plugin guidance are
    prompt inputs that affect candidate generation and provider exposure.
  - Status: direct `extra_context` now has a text-only schema, shared secret
    redaction, and a prompt-visible character cap.
  - Verification: focused prompt tests cover malformed objects, valid text,
    oversized text, and secret-like text.

- [x] Add direct parent/inspiration schema validation to prompt hardening.
  - Evidence: prompt sampling, inspiration resurfacing, and future
    prompt-history replay depend on typed parent and inspiration records.
  - Status: direct prompt rendering now accepts only a `Program` parent and a
    list of `Program` inspirations.
  - Verification: focused prompt tests cover valid/invalid parent records,
    empty inspiration lists, invalid containers, and invalid items.

- [x] Disambiguate command-keyword path names in workspace mutation syntax.
  - Evidence: file-section paths support spaces, while topology command
    sections use `DELETE`, `MOVE`/`RENAME`, and `PRIMARY` headers.
  - Status: workspace mutation syntax now supports `PATH` as an explicit
    ordinary-file prefix for command-leading filenames without changing
    topology command behavior.
  - Verification: focused candidate tests cover creating and editing
    `DELETE helper.py`, `MOVE file.py`, and `PRIMARY config.py`, plus empty
    `PATH` rejection.

- [x] Add malformed same-line section-envelope rejection to mutation parsing.
  - Evidence: same-line `<<<FILE ...>>>FILE` and `<<<BLOCK ...>>>BLOCK`
    envelopes are balanced by raw marker counts but invalid under the section
    grammar.
  - Status: parser validation now rejects same-line file/block section
    envelopes with structured diagnostics before replacement.
  - Verification: focused candidate tests cover same-line file, same-line
    block, and mixed valid plus malformed envelope inputs.

- [x] Add exact payload preservation to full-replacement mutation work.
  - Evidence: full-mode candidate parsing previously stripped trailing newlines
    from single-file, file-section, and block-section payload bodies.
  - Status: accepted full-replacement payload bodies preserve final newlines
    and blank lines across full-file, file-section, and block-section modes.
  - Verification: focused candidate tests cover trailing newline and blank-line
    behavior for full-file, file-section, single-block, and multi-block
    replacements.

- [x] Add line-ending policy to mutation parser hardening.
  - Evidence: patch text was normalized before diff parsing, but candidate code
    was previously matched byte-for-byte.
  - Status: diff matching now uses an LF-normalized comparison view while
    preserving output line endings from the matched candidate span.
  - Verification: focused diff/candidate tests cover plain diff, evolve-block,
    workspace-section, CRLF, LF, and mixed-line-ending inputs.

- [x] Normalize single-block full-replacement grammar with multi-block
  `<<<BLOCK ...>>>` grammar.
  - Evidence: one-block candidates previously inserted named block envelopes as
    literal source while multi-block candidates parsed them.
  - Status: full replacement now parses named block envelopes consistently for
    any block count, with raw-body shorthand retained for one-block candidates.
  - Verification: focused candidate tests cover single-block named sections,
    unknown names, multi-block sections, and workspace file-section routing.

- [x] Clarify full-mode file-section semantics when evolve blocks are present.
  - Evidence: full-mode prompts previously asked for complete replacement file
    content even when target files contained evolve-block markers.
  - Status: full-mode prompts/docs now specify that blocked target files use
    block payloads inside file sections, while unblocked files use complete
    replacement file content.
  - Verification: focused prompt tests assert the instruction text, and
    candidate tests cover one-block and multi-block workspace target files.

- [x] Add whole-response accounting for file-section mutation parsing.
  - Evidence: file-section parsing previously extracted matching sections and
    ignored prose or stray edits around them.
  - Status: file-section responses now reject non-whitespace/non-metadata text
    outside recognized sections with `malformed_file_sections:unconsumed_text`.
  - Verification: focused candidate tests cover prose, stray diffs, mixed
    file/block payloads, and proposal metadata around valid sections.

- [x] Add whole-response accounting for plain SEARCH/REPLACE diff parsing.
  - Evidence: plain diff parsing previously applied recognized blocks without
    verifying the rest of the response was consumed.
  - Status: diff responses now reject non-whitespace/non-metadata text outside
    compact or canonical SEARCH/REPLACE blocks with
    `malformed_diff:unconsumed_text`.
  - Verification: focused diff tests cover prose, malformed trailing diffs,
    mixed canonical/compact blocks, and proposal metadata around valid blocks.

- [x] Add whole-response accounting for block-section full replacements.
  - Evidence: multi-block full replacement previously applied recognized
    `<<<BLOCK ...>>>BLOCK` sections without verifying the rest of the response
    was consumed.
  - Status: block-section full replacements now reject non-whitespace/
    non-metadata text outside recognized sections with
    `malformed_block_sections:unconsumed_text`.
  - Verification: focused candidate tests cover leading prose, trailing prose,
    stray diffs, proposal metadata, and preserved multi-block skeletons.

- [x] Add linked seed-root rejection to problem-package integrity work.
  - Evidence: linked `initial_programs/` roots could make externally resolved
    seeds appear problem-local in provenance.
  - Status: the loader now rejects linked seed roots before seed iteration, and
    README/problem-format document the seed-root boundary.
  - Verification: focused loader tests cover root-link rejection and
    platform-available directory symlink roots.

- [x] Add evolve-block name safety to candidate-label hardening.
  - Evidence: evolve-block names become mutation targets and prompt-visible
    skeleton labels.
  - Status: source marker names and named block-section targets now reject
    secret-like text and Unicode format controls with structured unsafe-name
    diagnostics, and docs describe the public-label boundary.
  - Verification: focused candidate and loader tests cover unsafe source names,
    unsafe mutation targets, seed rejection, safe names, and non-ASCII policy.

- [x] Tighten roadmap collision work around evaluator/export failure
  semantics.
  - Evidence: case-folded materialization collisions were detected only at
    materialization time and could escape evaluator failure handling.
  - Status: evaluator materialization failures now become invalid candidate
    evaluations with structured diagnostics; separate best-export manifest,
    link, and rollback hardening items remain open.
  - Verification: focused evaluator and loop tests prove direct invalid
    evaluation results, completed runs, failure-history persistence, and no
    colliding files written under the run directory.

- [x] Add direct evaluator contract-preflight parity to evaluation hardening.
  - Evidence: direct evaluator APIs are used by tests, notebooks, and future
    worker paths, but only `evolve()` previously called
    `preflight_evaluator_contracts()` before evaluation.
  - Status: `CascadeEvaluator.evaluate()` now preflights default and staged
    validator contracts once before subprocess evaluation for direct callers.
  - Verification: focused evaluator tests cover supported direct signatures,
    missing `evaluate`, variadic and keyword-only signatures, async/generator
    validators, and configured-stage contract rejection.

- [x] Add boundary-aware markdown-fence stripping to mutation parsing work.
  - Evidence: mutation parsing previously removed every triple-backtick token
    before diff/full replacement parsing, which could silently delete intended
    candidate string-literal content.
  - Status: mutation parsing now strips only one whole-response markdown fence
    wrapper and keeps fence-like text inside replacement payloads.
  - Verification: focused diff/candidate tests cover wrapped SEARCH/REPLACE
    output and preserved triple-backtick literals in SEARCH/REPLACE, full-file,
    file-section, and block-section replacements.

- [x] Add delimiter-safe payload parsing to mutation-envelope work.
  - Evidence: envelope validation previously scanned raw mutation text for
    `<<<FILE`/`>>>FILE` substrings before section parsing, so marker-looking
    strings inside code could be misclassified as section delimiters.
  - Status: file/block envelopes now use line-start marker recognition, which
    preserves marker-looking substrings inside ordinary replacement code lines.
  - Verification: focused diff/candidate tests cover `<<<FILE`, `>>>FILE`,
    `<<<BLOCK`, and `>>>BLOCK` literals across full-file, file-section, block,
    and SEARCH/REPLACE modes.

- [x] Add validator helper shadowing policy to evaluation hardening.
  - Evidence: evaluator import precedence was previously accidental, and
    candidate modules could shadow sibling evaluator helper modules.
  - Status: validator-directory imports now precede candidate-workspace imports
    in the subprocess runner, giving problem-local evaluator helpers stable
    same-name precedence while preserving candidate imports without collisions.
  - Verification: focused evaluator tests cover same-name helper collision
    precedence, candidate package imports, problem-local validator helper
    imports, and workspace-relative data reads.

- [x] Add side-effect-safe validator preflight to evaluation hardening.
  - Evidence: evaluator contract preflight previously imported validators in
    the parent CLI/runtime process before subprocess environment, cwd, and
    timeout policy applied.
  - Status: preflight import/signature checks now run in a bounded subprocess
    with a temporary working directory and validator env allowlist; CLI, direct
    `evolve()`, and direct `CascadeEvaluator` all pass allowlist policy into
    preflight.
  - Verification: focused evaluator tests cover parent env isolation,
    temporary-cwd import side effects, env allowlists, slow import timeout, and
    existing unsupported-signature diagnostics.

- [x] Add unambiguous evaluator result transport to evaluation roadmap.
  - Evidence: `_run_subprocess()` previously treated the last non-empty stdout
    line as the structured evaluator result, so diagnostic or inherited child
    stdout could replace the validator return value.
  - Status: evaluator return values now use a runner-owned JSON result file,
    separating authoritative metrics from stdout/stderr diagnostics.
  - Verification: focused evaluator tests cover regular validator prints,
    descendant-process stdout printed after return, and non-serializable return
    payload handling.

- [x] Add actionable metric-contract rejection diagnostics to evaluator
  roadmap.
  - Evidence: strict evaluator-output validation previously collapsed distinct
    contract failures into generic `malformed_metrics` status.
  - Status: malformed evaluator outputs now persist bounded,
    machine-readable `metadata.malformed_metrics` diagnostics with reason,
    exception type, and redacted message.
  - Verification: focused evaluator tests cover missing metrics, undeclared
    keys, nonnumeric metrics, non-finite/JSON-invalid values, bad `is_valid`,
    missing secondary metrics, and missing result-file transport.

- [x] Add non-serializable evaluator-result handling to evaluator roadmap.
  - Evidence: non-JSON-serializable validator returns previously surfaced as
    subprocess errors or generic malformed metrics without serializer detail.
  - Status: the runner catches result serialization failures through the
    result-file envelope and the parent records reason
    `not_json_serializable`.
  - Verification: focused evaluator tests cover object, set, bytes, NumPy
    scalar, NumPy array, and valid JSON-compatible metric returns.

- [x] Add evaluator-result key-safety validation to evaluation transport work.
  - Evidence: JSON transport could previously coerce non-string keys before
    metric validation.
  - Status: top-level evaluator result keys must be strings before
    serialization, and unsafe keys are rejected as malformed evaluator
    contracts.
  - Verification: focused evaluator tests cover direct returns, configured
    stages, retries, and sampled cascades.

- [x] Add persisted stdout/stderr size limits to evaluation roadmap.
  - Evidence: evaluator stdout/stderr were redacted but stored in full in
    `EvaluationResult`, stage, retry, and history records.
  - Status: persisted validator stdout/stderr now use a configurable
    `evaluator_output_max_chars` cap with redact-then-truncate policy and
    `metadata.diagnostic_output` truncation metadata. Multi-sample aggregate
    stdout/stderr is capped as well.
  - Verification: focused evaluator/config tests cover direct large streams,
    redaction ordering, sampled aggregate caps, default/override config, and
    invalid cap values.

- [x] Add metric-payload redaction/schema filtering to feedback prompt
  hardening.
  - Evidence: feedback prompt hardening tracks workspace redaction, evaluator
    diagnostics, and explicit problem context, but feedback metric payloads
    were a separate prompt input path.
  - Status: feedback prompt metrics now pass through bounded recursive
    redaction for string keys and values before strict JSON rendering, while
    normal numeric evaluator metrics remain visible.
  - Verification: focused feedback tests cover secret-like metric keys,
    secret-like values, nested metrics, long strings, plugin-style string
    metrics, and normal numeric metrics.

- [x] Add diagnostic redaction to LLM feedback-grader prompts.
  - Evidence: feedback prompt workspace rendering had redaction, but evaluator
    diagnostic fields needed the same policy.
  - Status: feedback prompt diagnostics now redact top-level and stage
    stdout/stderr/error fields before truncation and strict JSON rendering.
  - Verification: focused feedback tests cover top-level and stage evaluator
    diagnostics with secret-like stdout, stderr, and error values.

- [x] Add metric-payload redaction to mutation prompt hardening.
  - Evidence: parent and inspiration metrics rendered by `PromptSampler` are a
    separate prompt input path from feedback-prompt metrics.
  - Status: parent and inspiration metric keys/values now use shared
    redaction/truncation before mutation prompt rendering, declared metrics are
    ordered first, and non-finite metric values render as explicit typed
    markers instead of raw `nan`/`inf` strings.
  - Verification: focused prompt tests cover parent and inspiration metric
    redaction, bounded strings, nested string payloads, declared metric
    ordering, and non-finite markers.

- [x] Add metric-semantics rendering to prompt hardening.
  - Evidence: prompt-visible metrics need to communicate whether a value is
    primary or secondary, which direction is optimized, and how raw values map
    to normalized fitness.
  - Status: mutation prompts now render declared parent and inspiration metrics
    with primary/secondary role, maximize/minimize direction, bounds,
    normalized values, out-of-range diagnostics, separate validity status, and
    explicit feedback-adjusted-fitness labeling.
  - Verification: focused prompt tests cover maximize/minimize directions,
    bounds, normalized values, primary/secondary labels, out-of-range metrics,
    feedback-adjusted fitness, validity, and inspiration programs.

- [x] Add finite-score validation to parent/inspiration prompt rendering.
  - Evidence: top-level fitness rendered in prompt headers is a separate score
    channel from metric payloads and feedback diagnostics.
  - Status: prompt rendering now converts invalid parent and inspiration
    fitness values into typed markers instead of rendering `nan`/`inf`, boolean
    `1.0000`, or crashing on nonnumeric restored values.
  - Verification: focused prompt tests cover direct prompt inputs, restored
    post-construction values, booleans, strings, `None`, `nan`, `inf`, `-inf`,
    normal finite scores, inspirations, and custom `{parent_score:.4f}`
    templates.

- [x] Add explicit problem context to LLM feedback-grader prompts.
  - Evidence: feedback graders should see task constraints, explicit context
    files, candidate files, evaluation diagnostics, and metrics when scoring a
    candidate.
  - Status: feedback prompts now render bounded/redacted problem context with
    source provenance in a dedicated `[CONTEXT]` section, separate from
    workspace and diagnostic budgets.
  - Verification: focused feedback tests cover context visibility, source
    provenance, redaction, truncation, and feedback prompt budget omission.

- [x] Add tri-state evaluator-stage status to prompt-feedback work.
  - Evidence: prompt-context roadmap items treat stage feedback as useful
    evidence for later mutations, so unknown/restored status must stay truthful.
  - Status: parent feedback and retry/sample attempt summaries now render
    `passed`, `failed`, or `unknown` from strict boolean status; missing,
    `None`, and malformed values render as `unknown`.
  - Verification: focused prompt tests cover known failed stages, missing
    status, explicit `None`, malformed status values, and retry/sample attempt
    summaries.

- [x] Add selected-inspiration evaluator feedback to prompt-context work.
  - Evidence: AlphaEvolve's prompt sampler uses database programs as rich
    context with quality scores and other feedback, not only source text.
  - Status: selected inspiration blocks now include bounded/redacted feedback
    summaries when available, using the existing parent feedback renderer and
    budget/redaction rules.
  - Verification: focused prompt tests cover inspiration feedback visibility,
    truncation, redaction, and LLM grader feedback summaries.

- [x] Add safe prompt rendering for skipped evaluator-artifact diagnostics.
  - Evidence: artifact metadata records skipped files and prompt feedback should
    expose evaluator evidence and omissions without leaking sensitive paths.
  - Status: skipped artifact summaries are bounded, redacted, and visible even
    when no artifacts were copied. Copied artifact source/stored paths also use
    bounded prompt redaction, and skipped artifact lists are rendered as compact
    fields rather than raw `repr()` output.
  - Verification: focused prompt tests cover skipped-only artifacts,
    copied-plus-skipped artifacts, max-file/max-byte diagnostics, redaction, and
    raw-list suppression.

- [x] Add first run-level rendered prompt character budget.
  - Evidence: roadmap prompt/context work calls for bounded prompt construction
    before LLM calls as feedback, context, and failure memory grow.
  - Status: runs can configure `prompt_max_chars` to cap final rendered mutation
    prompts before provider calls. Generated program history records
    prompt-size diagnostics, and manifests preserve the configured cap. The
    truncation policy prefers keeping the `[TASK]` mutation section visible.
  - Verification: focused config, prompt, loop, and CLI tests cover validation,
    truncation metadata, pre-LLM prompt size, manifest persistence, and
    preserved mutation instructions.

- [x] Add legacy failure-record prompt redaction to prompt/runtime hardening.
  - Roadmap evidence: prompt/history redaction is tracked, and failure-memory
    prompts render evaluator summaries; compatibility input shapes need the
    same safety boundary.
  - Status: tuple-form `recent_failures` now render through bounded redaction,
    newline escaping, and truncation instead of raw code interpolation.
  - Verification: focused prompt tests cover secret-like tuple text, escaped
    newlines, truncation notices, and suppression of long repeated payloads.

- [x] Add delimiter-safe candidate workspace rendering to prompt hardening.
  - Roadmap evidence: prompt assembly should preserve candidate code boundaries
    even when source files contain marker-like or fence-like text.
  - Status: parent and inspiration programs now render as typed workspace file
    records with JSON-escaped content and character counts instead of markdown
    code fences. Single-file non-Python workspaces keep their real path metadata
    instead of being presented as Python.
  - Verification: focused prompt tests cover parent and inspiration programs,
    multi-file workspaces, single-file non-Python workspaces, embedded triple
    backticks, and fake file-header text inside candidate content.

- [x] Add delimiter-safe explicit context-body rendering to prompt hardening.
  - Roadmap evidence: prompt assembly should preserve context boundaries even
    when local context files contain marker-like or instruction-like text.
  - Status: explicit context bodies now render as `Content-JSON` strings with
    character counts, while source citation headers are preserved for
    provenance.
  - Verification: focused prompt tests cover context bodies containing triple
    backticks, fake `[TASK]` headers, and fake context source headers.

- [x] Add deterministic context-render ordering to prompt/context hardening.
  - Roadmap evidence: prompt-context work tracks context ingestion, citation
    metadata, prompt budgets, and replay, so equivalent context maps need a
    stable ordering contract.
  - Status: `_render_context()` now path-sorts context entries before prompt
    rendering.
  - Verification: focused prompt tests prove reversed direct context insertion
    order renders in canonical path order.

- [x] Add prompt-visible context citation validation to context-ingestion
  hardening.
  - Roadmap evidence: first-class literature/context ingestion includes prompt
    citations and source provenance, so rendered citation headers need their
    own display-safety boundary.
  - Status: citation headers now redact/bound source labels and metadata,
    normalize malformed SHA/status/character fields, display only valid
    non-negative ordered excerpt spans, and ignore invalid page spans.
  - Verification: focused prompt tests cover loader-style citation records plus
    direct/mutated records with secret-like metadata, newline status injection,
    negative offsets, and reversed/negative page spans.

- [x] Add rendered plugin-context validation to prompt/runtime hardening.
  - Roadmap evidence: plugin context can influence mutation prompts and is
    persisted in generated candidate metadata, so it needs an explicit
    hook-boundary contract.
  - Status: `build_extra_context()` returns are limited to `str` or `None`.
    Emitted text is redacted, capped, serialized as JSON-string plugin-context
    prompt evidence, and stored with exact persisted length/hash plus
    redaction/truncation diagnostics.
  - Verification: focused loop tests cover object-return rejection,
    secret-like payload redaction, oversized payload truncation, prompt
    rendering, metadata consistency, and aborted-run diagnostics.

- [x] Add delimiter-safe feedback rendering to prompt hardening.
  - Roadmap evidence: prompt assembly should preserve evidence boundaries even
    when evaluator output, proposal notes, artifact diagnostics, or LLM grader
    comments contain marker-like or instruction-like text.
  - Status: remaining dynamic feedback/proposal fields now render as JSON
    strings under typed prompt sections after redaction and truncation, so
    fake prompt headers, file headers, and markdown fences remain data.
  - Verification: focused prompt tests cover delimiter-like stage names,
    evaluator errors/stdout, retry attempts, skipped artifacts, proposal
    metadata, and LLM feedback.

- [x] Complete declared-schema filtering for mutation prompt metrics.
  - Roadmap evidence: parent and inspiration metric summaries are prompt-bound
    evolutionary-database context, so arbitrary direct/plugin/restored metrics
    should not enter mutation prompts by default.
  - Status: `PromptSampler` now renders only problem-declared metrics,
    `is_valid`, `feedback_adjusted_fitness`, and manifest-safe feedback metrics
    explicitly named in `evaluation.metadata.llm_feedback[].metric` when a
    problem schema is available. Unknown plugin/restored metrics remain in
    history/database records but are omitted from mutation prompt metrics.
  - Verification: focused prompt tests cover parent and inspiration filtering
    of secret-like, plugin, nested, long, and non-finite undeclared metrics
    while preserving declared metrics and explicit LLM feedback metrics. A loop
    regression proves persisted `history.jsonl` mutation prompts keep the
    feedback metric and omit plugin/secret metric names.

- [x] Extend metric-name safety beyond declared problem schemas to runtime
  program records.
  - Roadmap evidence: multi-metric storage, metric-aware sampling, prompt
    feedback, and future queryable databases all treat metric names as durable
    identifiers rather than arbitrary display text.
  - Status: runtime `Program.metrics` keys now share the metric-name grammar
    used by problem schemas, including dotted namespaces. Unsafe direct,
    mutated, or plugin-added keys are rejected or quarantined before prompt
    rendering, history persistence, or archive insertion; plugin metric side
    effects are reverted with explicit score-composition diagnostics.
  - Verification: focused program, database, and loop tests cover direct
    construction, history quarantine, archive rejection, and plugin-added
    unsafe metric names.

- [x] Add direct archive-id uniqueness to database hardening.
  - Roadmap evidence: queryable evolutionary databases and resumable archive
    state require candidate ids to identify one candidate body at direct
    archive insertion boundaries.
  - Status: `ProgramDatabase` keeps a separate archive id registry from the
    history id registry. Direct `add()` / `admit()` reject a duplicate archive
    id before island mutation, including a different object with an id already
    logged in the run. Migration/resume clone semantics remain separate open
    roadmap work.
  - Verification: focused database tests cover raw add duplicates, admitted
    duplicates across islands, logged-id conflicts, and the allowed
    log-then-admit-same-object workflow.

- [x] Add invalid-encoding history diagnostics to run-inspection hardening.
  - Roadmap evidence: history streams are treated as replayable experiment
    evidence, and run inspection should diagnose corrupted artifacts
    deterministically.
  - Status: `libreevolve show` now reads `history.jsonl` as bytes, decodes each
    row as UTF-8, and reports invalid bytes with
    `Malformed history.jsonl at line N: invalid UTF-8 (...)`. Resume/replay
    loader semantics remain an open roadmap item.
  - Verification: focused CLI tests cover invalid UTF-8 on line 1, invalid
    UTF-8 after a valid row, large legacy-history streaming, and mixed-schema
    rejection.

- [x] Add accepted-history id validation to run-inspection hardening.
  - Roadmap evidence: accepted candidate ids are join keys for lineage,
    archive admission, prompt context, resumed archives, and benchmark reports.
  - Status: `show` now enforces manifest-safe ids and duplicate-id rejection for
    every streamed `history.jsonl` row before selecting the displayed best
    candidate. Resume/database restore behavior remains open roadmap work.
  - Verification: focused CLI tests cover duplicate legacy ids, duplicate
    current archive ids, unsafe newline ids, secret-like ids, and Unicode
    format-control ids.

- [x] Add strict metric validation to run-inspection hardening.
  - Roadmap evidence: artifact hardening treats `history.jsonl` metrics as
    structured experiment evidence and the CLI `show` path as the compact
    reader for those records.
  - Status: `show` validates streamed history metric names and values with the
    runtime `Program.metrics` policy, rejects malformed rows with line-numbered
    diagnostics, and renders displayed metrics as strict JSON.
  - Verification: focused CLI tests cover invalid legacy/current metric values,
    unsafe metric keys, invalid unselected rows, and valid strict metric output.

- [x] Add `show` workspace-path validation to run-artifact hardening.
  - Evidence: `show` is the compact inspection command for history rows, and
    run-artifact docs say it validates workspace file records before printing
    selected candidate workspaces.
  - Status: displayed history workspaces are validated through
    `CandidateWorkspace`, including path normalization and unsafe path
    rejection, before any workspace file manifest is printed.
  - Verification: focused CLI tests cover traversal, absolute, hidden,
    bidi-control, overlong, duplicate-normalized, and valid Unicode workspace
    paths.

- [x] Add archive-admission object-shape and consistency validation to run
  inspection.
  - Evidence: current-history selection depends on
    `metadata.archive_admission` as a structured payload and uses multiple flags
    to separate cell admission, elite retention, search-state changes, and
    sampling eligibility.
  - Status: `show` now rejects non-object archive-admission payloads with
    line-numbered malformed-history diagnostics and rejects admitted rows whose
    explicit archive-state flags are all false.
  - Verification: focused CLI tests cover malformed payloads, contradictory
    admitted rows, coherent cell/elite rows, and explicit non-admitted rows.

- [x] Add current-history evaluation-shape validation to run inspection.
  - Evidence: current histories are selected by archive admission plus
    evaluator validity, so malformed evaluation payloads should be surfaced as
    corrupt history rather than folded into ordinary no-valid-program outcomes.
  - Status: `show` now rejects non-object current-history evaluation payloads
    and non-boolean `evaluation.is_valid` values with line-numbered diagnostics.
  - Verification: focused CLI tests cover malformed selected rows,
    missing-validity compatibility, and valid retained rows.

- [x] Add stream-level archive diagnostic validation to `show` run inspection.
  - Evidence: run inspection is becoming a primary way to audit history,
    archive diagnostics, and artifact truthfulness.
  - Status: `show` now validates archive diagnostic fields for every
    current-history row before selection, surfacing malformed lower-scoring
    retained rows with line-numbered diagnostics.
  - Verification: focused CLI tests cover malformed selected and unselected
    archive diagnostics.

- [x] Add archive-cell arity and non-negative shape validation to
  run-inspection roadmap work.
  - Evidence: MAP-Elites cell coordinates are persisted archive diagnostics.
  - Status: `show` requires current-history cells to be exactly three
    non-negative integers. Manifest-bound per-axis range validation remains
    open.
  - Verification: focused CLI tests cover negative, wrong-arity, non-integer,
    valid selected, and malformed unselected cells.

- [x] Add display-safe archive descriptor labels to run-inspection hardening.
  - Evidence: archive descriptors are part of MAP-Elites diagnostics and future
    resume/search state; descriptor names must not become an arbitrary
    unredacted output channel.
  - Status: `show` now validates archive descriptor labels before display with
    the shared manifest-safe metric-name grammar and rejects secret-like,
    control-character, malformed, and reserved labels. Descriptor count and
    rendered-length limits are covered by the follow-on completed
    archive-diagnostic display-budget item.
  - Verification: focused CLI tests cover valid descriptor diagnostics, unsafe
    selected descriptor labels, and unsafe unselected current-history labels.

- [x] Add archive-diagnostic display budgets to run-inspection roadmap work.
  - Evidence: `libreevolve show` display hardening should keep archive
    diagnostics compact enough for terminal inspection while preserving full
    machine-readable history.
  - Status: large descriptor maps and long descriptor labels are summarized by
    descriptor count, bounded preview, omitted count, and stable hash. Normal
    compact descriptor maps still print as JSON.
  - Verification: focused CLI tests cover descriptor count, label length,
    rendered-output bounds, normal compact output, and omission/hash metadata.

- [x] Add bounded run-inspection output to the roadmap.
  - Roadmap evidence: the AlphaEvolve-alignment plan needs terminal-safe
    rendering budgets for large candidate/codebase artifacts.
  - Status: `libreevolve show` now truncates oversized selected legacy source
    and workspace file bodies with source length, displayed count, omitted
    count, source hash, and a `history.jsonl` pointer. A configurable/full
    source mode remains open as a separate code follow-up.
  - Verification: focused CLI tests cover large single-file history and
    multi-file workspace history output.

- [x] Add bounded source display to run-inspection roadmap work.
  - Evidence: `show` is documented as a compact history inspector, so selected
    source rendering needs terminal/output-size limits.
  - Status: selected legacy code and workspace file contents now use fixed
    display limits with truncation notices, source hashes, omitted counts, and
    `history.jsonl` full-source pointers.
  - Verification: focused CLI tests cover large source rows, normal small
    workspace rows, and oversized primary/secondary workspace files.

- [x] Add secret-safe evaluator preflight diagnostics to runtime hardening.
  - Roadmap evidence: startup preflight and runtime artifact safety require the
    preflight exception surface to use the redacted/path-hashed diagnostic
    policy.
  - Status: evaluator preflight failures and evaluator-path validation errors
    now report problem-relative or outside-problem labels with path hashes
    instead of raw absolute roots. Run-directory containment errors remain open.
  - Verification: focused CLI/evaluator tests cover secret-like problem roots,
    configured-stage outside paths, and missing problem-local validator paths.

- [x] Add secret-safe run-directory containment errors to runtime hardening.
  - Roadmap evidence: runtime artifacts use redacted/hash metadata for
    `log_dir`, so containment and cleanup setup failures should not leak raw
    local absolute roots.
  - Status: run-directory containment failures, existing-artifact startup
    failures, and linked-artifact overwrite failures now use scoped path labels
    with stable path hashes. Containment still rejects escaping
    symlink/junction run directories before cleanup.
  - Verification: focused database and CLI tests cover direct containment
    failures, symlink/junction run-directory escapes, linked artifacts,
    existing artifacts, secret-like absolute log roots, and Click output.

- [x] Add seed-versus-generated generation semantics to database and resume
  planning.
  - Roadmap evidence: lineage, resumability, archive state, and reproducible
    run history need generation ids that distinguish baseline seeds from
    generated evolutionary rows.
  - Status: seed rows remain generation `0`, generated rows start at generation
    `1`, generated metadata keeps `loop_generation_index`, and prompt-result,
    migration, and plugin-hook code paths use the completed-generation count.
    Full resume/archive persistence remains a separate roadmap item.
  - Verification: focused loop tests cover seed-only and first-generated-child
    histories, prompt metadata, plugin hooks, and mutation-generation export
    cadence.

- [x] Define ThetaEvolve export cadence under completed-generation counts.
  - Evidence: plugin docs describe `ttt_rl` as exporting every `train_every`
    generations, so generation-boundary exports should use a clear completed
    generation count.
  - Status: the core loop now passes completed-generation counts starting at
    `1` to plugin hooks. `train_every=1` exports after the first completed
    mutation generation; `train_every=2` exports after the second, and shorter
    runs keep manifest-visible pending examples.
  - Verification: focused loop/plugin tests cover first-generation export,
    second-generation export, short non-multiple pending state, and manifest
    queued/pending/exported counts.

- [x] Add stale-context policy to live retrieval roadmap work.
  - Evidence: retrieval provenance/cache work must distinguish prompt-visible
    context from the latest attempted refresh.
  - Status: DeepResearch now clears prompt-visible synthesis on empty/error
    refreshes and records active successful context with generation, event
    index, status, and synthesis hash. Broader cache/replay and transport
    integrity requirements remain open.
  - Verification: focused DeepResearch tests cover ok-to-empty, ok-to-error,
    ok-to-new-result, and active-context metadata.

- [x] Add live retrieval event-retention policy to plugin/runtime hardening.
  - Evidence: DeepResearch prompt metadata exposes a bounded prompt-history
    view, and live plugin state should be bounded for long runs as well.
  - Status: `DeepResearchPlugin(max_events=100)` now bounds retained retrieval
    events by default, supports a validated custom cap, and emits retention
    diagnostics for limit, retained events, emitted events, total events, and
    dropped events. Artifact offload and resume semantics remain open.
  - Verification: focused DeepResearch tests prove bounded in-memory growth,
    invalid cap rejection, retained event indexes, active-context index, and
    truthful retention counters.

- [x] Add finite best-fitness validation to retrieval provenance work.
  - Evidence: retrieval queries and metadata should not include malformed
    best-program fitness values.
  - Status: DeepResearch now treats non-finite or nonnumeric best fitness as a
    malformed retrieval input, emits a structured skipped event, clears active
    context, avoids the provider call, and omits non-finite `best_fitness`.
    Finite fitness values are normalized to floats.
  - Verification: focused DeepResearch tests cover finite fitness plus `nan`,
    `inf`, `-inf`, string, bool, and `None` cases.

- [x] Add retrieval request-URL redaction to prompt-context provenance work.
  - Evidence: provider-error redaction covers exception text, and provider
    request URLs can carry credentials, private search text, or account-specific
    identifiers.
  - Status: DeepResearch now converts provider `query_url` fields into
    hash-backed `request_url` summaries and omits raw URL/query values from
    prompt-context metadata. Transport/final-URL/TLS provenance remains open.
  - Verification: focused DeepResearch and loop tests cover default arXiv URL
    summaries, custom secret-bearing URLs, candidate history, and manifest
    output.

- [x] Add direct retrieval-helper parameter validation to plugin hardening.
  - Evidence: retrieval/plugin context work includes structured live provider
    metadata, custom retrieval providers, and reproducibility boundaries, so
    helper-level provider parameters should be checked before network request
    construction.
  - Status: direct arXiv retrieval helpers now reject malformed query text,
    sensitive-looking query values, and non-integer/out-of-range `max_results`
    values. Default arXiv URLs use HTTPS, and provider responses record
    transport status plus payload hash metadata.
  - Verification: focused DeepResearch and loop tests cover malformed direct
    calls, normal plugin calls, provider URL provenance, custom-provider
    compatibility, and run-manifest transport summaries.

- [x] Add retrieval response-size budgets to prompt-context work.
  - Evidence: live retrieval results can be prompt inputs and provenance
    records, so default provider responses need byte budgets and
    oversized-payload diagnostics.
  - Status: the arXiv provider now reads responses through a fixed
    1,000,000-byte cap, permits exact-limit payloads, classifies oversized
    payloads as `oversized_response` errors before XML parsing, and records
    payload limit, observed bytes, truncation/oversize flags, bounded payload
    byte count, and payload hash in retrieval metadata and run summaries.
  - Verification: focused DeepResearch and loop tests cover byte-budgeted
    reads, exact-limit behavior, oversized-response rejection before parsing,
    and manifest payload-budget summaries.

- [x] Add untrusted-source isolation to live retrieval prompting.
  - Evidence: live retrieval summaries are external text and should not be
    rendered as ordinary mutation instructions.
  - Status: DeepResearch retrieval context now uses an
    `untrusted_evidence_v1` policy with explicit begin/end delimiters and a
    prompt note that retrieved text is non-authoritative evidence. Candidate
    metadata and compact run summaries persist the trust policy, prompt
    boundary, and `authoritative: false`.
  - Verification: focused DeepResearch and loop tests cover
    prompt-injection-like custom source text, normal provider context,
    redacted/truncated retrieved text, active-context metadata, and manifest
    trust-policy summaries.

- [x] Add code/metric-aware retrieval-query generation to prompt/context work.
  - Evidence: retrieval provenance records which query was used, and live
    retrieval should use available problem signals rather than only generic
    optimization text plus current fitness.
  - Status: DeepResearch now uses `best_program_code_metrics_v1` query
    construction: best fitness, manifest-safe metric names, and bounded
    best-program code/file identifier terms. Candidate history and compact run
    summaries persist query policy and selected query inputs. Task-description,
    failure, local-paper, and hypothesis-template query grounding remain open.
  - Verification: focused DeepResearch and loop tests cover domain-different
    query generation, persisted query inputs, and manifest query provenance.

- [x] Add retrieval source-metadata schema/redaction to prompt-context work.
  - Evidence: provider-error redaction covers exception text, but retrieval
    source records are a separate provenance channel.
  - Status: DeepResearch now normalizes provider `sources` into bounded,
    redacted source records with source-count retention diagnostics,
    per-source redaction/truncation flags, omitted-field accounting, and
    compact manifest source metadata summaries. Source-content trust, ranking,
    and replay/snapshot policy remain open.
  - Verification: focused DeepResearch and loop tests cover default arXiv
    source metadata, custom secret-bearing source titles/authors/URLs/excerpts,
    source truncation, dropped-source counts, prompt-context metadata, and
    runtime-summary metadata.

- [x] Add cache/replay semantics to live retrieval context.
  - Evidence: retrieval provenance records what happened after a provider call,
    and repeated identical queries should be able to reuse stable context
    without provider drift.
  - Status: DeepResearch now has cache keys, in-memory and optional disk JSON
    snapshots, explicit `cached`/`live`/`offline` modes, structured
    cache-miss diagnostics, no-expiry staleness metadata, and compact manifest
    cache summaries. CLI-loaded `deep_research` uses
    `plugin_artifacts/deep_research/` for snapshots. Full provider payloads,
    ranking provenance, source-content trust, and full run resume remain open.
  - Verification: focused DeepResearch and loop tests cover duplicate-query
    cache reuse, disk snapshots, offline replay without provider calls, offline
    misses, and runtime-summary cache fields.

- [x] Add plugin hook failure provenance to runtime/plugin hardening.
  - Evidence: the main loop invokes `on_generation_start`,
    `build_extra_context`, `prompt_context_metadata`, `on_evaluated`,
    `run_artifacts_metadata`, and `on_generation_end`; those failures should be
    attributable in long-running experiments.
  - Status: the chosen policy is fatal run abort for all current hook
    categories. The original exception is re-raised, and aborted manifests
    persist structured plugin-failure provenance under
    `runtime.abort.plugin_failure` and `runtime.plugin_failures[]`, including
    plugin identity, hook, policy, generation/parent/candidate ids where
    available, exception type/message, redaction/truncation flags, and
    `continued: false`.
  - Verification: focused loop tests cover all hook categories plus redacted
    bounded plugin abort messages. README, plugin docs, and run-artifact docs
    describe the policy and fields.

- [x] Add authoritative plugin artifact attribution and aborted-run summaries
  to runtime/plugin hardening.
  - Evidence: plugin artifact records are experiment evidence and need stable
    producer identity, schema enforcement, and partial-run visibility.
  - Status: `runtime.plugin_artifacts[]` now stores runtime-derived plugin
    identity (`plugin`, `module`, `index`) beside nested validated plugin
    `metadata`. Completed runs abort on malformed non-mapping artifact
    metadata; aborted manifests collect valid summaries and record
    `runtime.plugin_artifact_failures[]` diagnostics without masking the
    original abort.
  - Verification: focused loop tests cover spoofed artifact names, valid
    nested metadata, redaction, invalid values/labels, non-mapping returns,
    empty returns, TTTRL nested artifacts, aborted summaries, and aborted
    summary failures.

- [x] Add aborted-run plugin artifact summaries to runtime/plugin hardening.
  - Evidence: completed runtime manifests can include plugin artifact
    summaries, and partial plugin outputs from aborted runs can explain why a
    run failed.
  - Status: aborted runtime finalization now receives the plugin list, collects
    validated wrapped artifact summaries when hooks succeed, and records
    `runtime.plugin_artifact_failures[]` when summary hooks or schemas fail
    during abort finalization.
  - Verification: focused loop tests cover plugin aborts after artifact
    emission and malformed artifact metadata during abort finalization.

- [x] Add top-level plugin artifact metadata schema enforcement.
  - Roadmap evidence: runtime manifests summarize plugin artifacts in a
    queryable form, so artifact metadata needs stable top-level shape
    validation at the hook boundary.
  - Status: `run_artifacts_metadata()` accepts only mappings, `None`, or empty
    dictionaries. Non-mapping non-empty returns are no longer silently ignored:
    completed runs abort, while aborted finalization records diagnostics.
  - Verification: focused loop tests cover list, string, scalar, `None`, empty
    dict, and valid dict metadata.

- [x] Add stable plugin instance identity across provenance records.
  - Evidence: runtime provenance and score-composition records need to
    identify repeated same-class plugins as distinct configured instances.
  - Status: plugins now receive deterministic run-local instance ids in the
    form `plugin:{index}:{module}.{qualname}`. Startup provenance,
    prompt-context records, score composition, artifact manifests, and plugin
    failure records all carry this identity alongside class/module/index.
  - Verification: focused tests prove duplicate same-class plugins with
    different deltas are correlated by `instance_id` across manifest
    provenance, history prompt context, score composition, and artifact
    summaries.

- [x] Add plugin side-effect schema validation to database/plugin hardening.
  - Evidence: plugin score-return validation is not enough if plugins can also
    mutate `program.metrics` and `program.metadata` before archive admission
    and history logging.
  - Status: plugin score hooks now snapshot metrics and metadata, validate both
    after each hook, and roll back unsafe side effects before admission/logging.
    Invalid metric side effects are reported as `invalid_plugin_metrics`;
    invalid metadata side effects are reported as `invalid_plugin_metadata`.
    Valid metadata additions are retained after program-metadata redaction.
  - Verification: focused loop tests cover unsafe metric names, valid metadata
    additions, non-serializable metadata, non-finite metadata, score rollback,
    and no history quarantine for rejected plugin side effects.

- [x] Validate direct plugin instances before runtime side effects.
  - Evidence: direct library callers can pass arbitrary objects in the plugin
    list, so validation must happen before database setup and artifact
    mutation.
  - Status: explicit plugin objects are now validated against `PluginBase` or a
    documented callable hook protocol before `ProgramDatabase` creation.
    Mutation-capable runs require the hooks the loop will call; zero-generation
    runs can use artifact-only plugin objects. Invalid plugin setup raises
    before manifest/history writes or overwrite cleanup.
  - Verification: focused loop tests cover invalid objects in zero-generation
    and mutation-capable direct runs, artifact preservation, valid
    zero-generation artifact-only plugins, and rejection of artifact-only
    plugins in mutation-capable runs.

- [x] Add plugin prompt-context metadata schema enforcement to runtime/plugin
  hardening.
  - Evidence: plugin prompt-context metadata feeds candidate history and
    runtime retrieval summaries, so runtime/plugin hardening needs a
    hook-boundary schema before treating these records as resumable/searchable
    provenance.
  - Status: prompt-context metadata is now validated before mutation,
    evaluation, archive admission, and history logging. `None` and `{}` are
    accepted as empty returns; non-empty values must be mappings. Recursive
    metadata validation enforces display-safe labels, finite JSON-safe values,
    bounded strings, and redaction. Malformed returns are attributed to
    `prompt_context_metadata` in plugin-failure provenance.
  - Verification: focused loop tests cover dict validation, empty returns, and
    list/string/scalar/boolean malformed returns.

- [x] Clarify plugin prompt-context metadata phase and emitted-text semantics.
  - Evidence: prompt-context metadata can be useful provenance even when a
    plugin emits no prompt-visible text, but that distinction must be explicit
    in run records.
  - Status: the current API keeps metadata hooks independent from rendered
    context. Candidate plugin-context records now carry `context_visibility`
    and `metadata_visibility` values that distinguish prompt-visible context
    from provenance-only plugin state.
  - Verification: focused loop tests prove metadata-only empty-context records
    are accepted intentionally, omit the prompt-visible `context` field, use
    `metadata_visibility: "provenance_only"`, and can still feed retrieval
    manifest summaries without prompt injection.

- [x] Add direct evaluator artifact-option validation to cascade hardening.
  - Evidence: evaluator artifact options are now validated at the
    `CascadeEvaluator` boundary, not only by `Config`.
  - Status: direct construction rejects non-list/non-string artifact selectors,
    empty or display-unsafe selectors, negative/non-integer limits, boolean
    limits, and non-boolean redaction flags before any validator subprocess can
    run or artifact metadata can be written. README, configuration docs, and
    run-artifact docs state this direct API boundary.
  - Verification: focused evaluator tests cover the direct invalid inputs plus
    normal copy-out and configured-stage artifact overrides.

- [x] Add direct evaluator timeout validation to budget/control hardening.
  - Evidence: direct evaluator construction is used outside CLI/config-loaded
    runs and now enforces the same finite positive timeout contract.
  - Status: `CascadeEvaluator.__init__()` rejects zero, negative, boolean,
    nonnumeric, and non-finite `timeout_sec` values before diff/syntax handling
    or validator subprocess execution. Valid direct calls store the timeout as
    a float for subprocess use.
  - Verification: focused evaluator tests cover invalid direct timeout values
    and existing timeout behavior for valid positive timeouts.

- [x] Add evaluator artifact glob semantics to cascade hardening.
  - Evidence: artifact copy-out selectors now have explicit path-segment-aware
    semantics instead of relying on slash-crossing `fnmatch` over whole paths.
  - Status: `*.txt` matches root candidate files only, `nested/*.txt` matches
    one segment below `nested/`, and `**/*.txt` recursively matches root and
    nested candidate files. Include and exclude selectors share that matcher,
    and docs describe it before presenting artifact copy-out as auditable
    evaluation evidence.
  - Verification: focused evaluator tests cover root, nested, recursive,
    include, and exclude cases.

- [x] Add artifact copy-out confinement and streaming limits to evaluation
  hardening.
  - Evidence: evaluator artifact copy-out now has an explicit confinement and
    byte-budget boundary before artifact metadata is treated as reproducible
    evaluation evidence.
  - Status: matched symlinks are not followed, matched regular files are
    resolved under the candidate workspace, source sizes are checked before
    reads, and skipped records preserve `link_not_followed`, `path_escape`,
    `resolve_error`, `stat_error`, `read_error`, `max_bytes`, and
    `max_bytes_after_redaction` reasons. Artifact records define both the
    legacy parent-rooted path and the artifact-directory-relative path.
  - Verification: focused evaluator tests cover oversized files without
    reading, symlink-capable platforms, custom/nested artifact roots, and
    ordinary artifact copy-out.

- [x] Add secret-safe artifact selector retention to cascade/manifest
  hardening.
  - Evidence: artifact include/exclude selectors are manifest-retained
    configuration, so the policy is now grammar-constrained rejection rather
    than raw retention or post-hoc redaction.
  - Status: secret-like selector patterns are rejected by shared artifact glob
    validation before `ProgramDatabase` can write `manifest.json`. README,
    configuration docs, and run-artifact docs state that selector text must not
    contain secret-like values.
  - Verification: focused config, evaluator, and database tests cover
    sensitive-looking include/exclude selectors at config, stage, direct API,
    and manifest-boundary paths.

- [x] Add path-safety grammar to evaluator artifact selector hardening.
  - Evidence: evaluator artifacts are now selected by safe workspace-relative
    POSIX glob patterns rather than arbitrary persisted path strings.
  - Status: traversal, dot/empty components, absolute roots, drive-style roots,
    leading backslashes, Windows backslashes, and padded patterns are rejected
    before matching or manifest persistence. README, configuration docs, and
    run-artifact docs define the grammar.
  - Verification: focused config/evaluator/database tests cover config, stage
    override, direct evaluator, manifest-boundary, and valid retained-pattern
    cases.

- [x] Add per-stage metadata retention to cascade/run-artifact hardening.
  - Evidence: configured cascades previously flattened stage pass/fail rows but
    kept only the final stage's result metadata on successful multi-stage
    evaluation.
  - Status: evaluation records now retain
    `metadata.configured_stage_results[]` with per-stage attempts, sample
    aggregates, artifact-policy outcomes, thresholds, stop decisions,
    validator environment metadata, metrics, outputs, and elapsed time. README,
    configuration docs, and run-artifact docs describe the new field and the
    remaining top-level final-stage compatibility view.
  - Verification: focused evaluator tests cover successful multi-stage
    cascades, early-stop cascades, sampled stages, retries, and per-stage
    artifacts.

- [x] Add timeout-cleanup output limits to evaluation metadata hardening.
  - Evidence: timeout cleanup is persisted under `metadata.timeout_cleanup`,
    so its command output needs the same bounded-diagnostic policy as validator
    stdout/stderr.
  - Status: cleanup command stdout/stderr/error metadata now uses a dedicated
    redact-then-truncate policy capped at 2,000 characters, with per-field
    diagnostics and documentation in README/run-artifact docs.
  - Verification: focused evaluator tests cover normal cleanup, oversized
    cleanup output, taskkill failure fallback, non-Windows process-group
    cleanup, and the timeout evaluator path.

- [x] Add strict-JSON diagnostic-message redaction to artifact hardening.
  - Evidence: quarantine records redact `record_repr`, but strict-JSON error
    messages could still include raw `repr()` text.
  - Status: shared strict JSON/JSONL serialization diagnostics now bound and
    redact exception messages and quarantine messages, including inline object
    repr text from non-string keys. README and run-artifact docs describe the
    safer diagnostic contract while keeping quarantine artifacts scoped as
    sensitive diagnostics.
  - Verification: focused JSONL tests cover manifest serialization failures,
    history/quarantine failures, secret-like object reprs, oversized messages,
    cyclic records, deep records, and bounded record snapshots.

- [x] Add strict JSON type-normalization policy to database/resume hardening.
  - Evidence: run manifests, history streams, prompt history, and quarantine
    records are future replay inputs, so the roadmap needs a clear distinction
    between JSON-native values and Python containers accepted for convenience.
  - Status: tuple normalization is rejected rather than versioned. Shared
    strict JSON validation fails tuple values before `json.dumps()` can coerce
    them into arrays, and README/run-artifact docs state that producers must
    provide explicit lists for persisted sequence values.
  - Verification: focused JSONL tests cover manifests, history/quarantine,
    prompt-history quarantine, and strict serializer diagnostics for tuple
    values.

- [x] Add caps or budget coupling for evaluator stage retry counts.
  - Roadmap evidence: evaluation cascades, expensive-eval budgets, and
    resumability require retry attempts to be bounded and attributable.
  - Status: stage retries now have an explicit cap of `10` in shared
    evaluator-stage validation. Attempt multiplication is documented as
    `samples * (retries + 1)` before early success/stop; richer per-stage
    wall-clock and budget-stop semantics remain tracked separately.
  - Verification: focused config/evaluator tests cover config and direct
    evaluator rejection of oversized retries plus accepted cap-bound retries.

- [x] Add threshold-aware retry policy to cascade hardening.
  - Roadmap truthfulness evidence: ROADMAP and docs describe staged validators
    with thresholds and retries.
  - Status: configured-stage retries now support threshold-aware selection when
    `min_score` is configured. Retry attempts can continue after locally valid
    below-threshold attempts, and persisted attempt metadata records local
    validity, threshold value, threshold pass/fail, and final pass/fail.
  - Verification: focused evaluator tests cover below-threshold valid attempts,
    threshold-pass retries, threshold-exhaustion retries, and existing
    invalid-then-valid retries.

- [x] Correct stale threshold-pass evidence in sample-aggregation roadmap.
  - Status: the open aggregation-policy roadmap item no longer claims that a
    valid but below-threshold configured stage is marked `passed=True`.
    Current evaluator records preserve local validity, threshold value,
    `threshold_passed`, final `passed`, and `stage_threshold_not_met` stop
    reason separately.
  - Remaining roadmap gap: sample aggregation still uses fixed numeric means
    and does not expose configurable worst-case, quantile, all-samples-pass,
    or per-metric pass policies.
  - Verification: existing evaluator tests cover threshold stop metadata,
    threshold-aware retry success, and threshold-aware retry exhaustion.

- [x] Add structured evaluator-output attachments to evaluation roadmap.
  - Evidence: AlphaEvolve Section 2.5 says evaluated solutions have scores and
    program outputs attached.
  - Status: the evaluator/database roadmap no longer treats non-scalar
    validator outputs as only stdout/stderr evidence. Reserved `outputs` and
    `program_output` channels are now strict-JSON validated, bounded, redacted,
    hashed, persisted in evaluation metadata, and rendered into bounded prompt
    feedback summaries while preserving the strict scalar metric contract for
    optimization.
  - Verification: focused evaluator and prompt tests cover persistence,
    redaction, size omission, malformed output rejection, duplicate-channel
    rejection, and prompt rendering.

- [x] Add LLM feedback/reviewer outcomes to structured stage diagnostics.
  - Evidence: optional LLM feedback can change final candidate validity and
    fitness, so those decisions need the same audit surface as local
    validator stages.
  - Status: each applied feedback grader now appends an
    `llm_feedback:<name>` stage containing pass/fail, score, metric,
    error/discard state, elapsed time, record index, backend id, min score,
    weight, and LLM-call provenance metadata while preserving existing
    `evaluation.metadata.llm_feedback` records.
  - Verification: focused feedback tests cover successful reviewer stages,
    discard stages, and backend-failure stages; README and run-artifact docs
    distinguish validator stages from LLM feedback/reviewer stages.

- [x] Add feedback call-telemetry validation to evaluation hardening.
  - Evidence: feedback/reviewer provenance should use the same normalized,
    JSON-safe, redacted call telemetry expected for mutation, critique, and
    meta-prompt calls.
  - Status: direct/custom feedback `llm.last_call` records are now normalized
    before storage with strict-JSON-safe values, redaction, bounded strings and
    containers, oversized-record previews, and `telemetry_safety` diagnostics.
  - Verification: focused feedback tests cover unsafe object values, nested
    secret redaction, oversized strings, long arrays, whole-record size
    bounding, strict JSON serialization, and stage metadata parity.

- [x] Add strict LLM feedback response parsing to evaluation hardening.
  - Evidence: incidental numbers in prose/provider diagnostics should not
    become valid feedback scores.
  - Status: feedback score parsing now requires JSON or explicit
    `score: <number>` / `score=<number>` text, rejects percentages and
    incidental numeric prose, and bounds scores to finite `[0, 1]` values before
    fitness composition.
  - Verification: focused feedback tests cover HTTP/status-code text,
    percentages, multi-number prose, malformed score fields, non-finite scores,
    and out-of-bounds scores.

- [x] Add LLM feedback grader ordering/discard policy to evaluation hardening.
  - Evidence: feedback graders can discard candidates, so later graders need a
    defined relationship to the candidate's current validity.
  - Status: feedback graders are evaluated in configured order. After evaluator
    invalidity or a prior feedback discard, graders without
    `include_invalid: true` are skipped and recorded as
    `llm_feedback_skipped_invalid`; graders with `include_invalid: true` can
    run for post-discard review without restoring candidate validity.
  - Verification: focused feedback tests cover ordered discard, skip behavior,
    include-invalid post-discard review, provider call counts, records, stages,
    metrics, and final validity.

- [x] Add LLM feedback metric namespace/collision rules to evaluation and
  metrics work.
  - Evidence: feedback metrics are persisted in the same runtime metric vector
    as evaluator metrics, so collisions can corrupt declared metric values and
    archive-selection inputs.
  - Status: feedback metric labels now share the manifest-safe metric grammar,
    reserve `is_valid` and `feedback_adjusted_fitness`, reject collisions with
    existing evaluator metrics, and reject duplicate feedback metrics in one
    grader list before provider calls.
  - Verification: focused feedback tests cover primary/secondary evaluator
    metric collisions, reserved fields, duplicate feedback metrics, provider
    call suppression, feedback records, and stage diagnostics.

- [x] Add LLM feedback score/weight composition policy to evaluation
  hardening.
  - Evidence: feedback graders can alter top-level fitness, so reviewer scores
    and weights need bounded semantics.
  - Status: feedback parser and direct/config validation now require finite
    `[0, 1]` reviewer scores, `weight`, and `min_score`. Successful reviewer
    records store raw `score`, configured `weight`, and `weighted_delta`;
    feedback-adjusted fitness is documented as top-level/prompt-reward
    behavior while MAP-Elites selection remains declared-metric based.
  - Verification: focused config/feedback tests cover negative, zero,
    oversized, ordinary, malformed, non-finite, and out-of-range score/weight
    cases plus persisted composition fields.
- [x] Split candidate-count budgets from validator-attempt budgets.
  - Roadmap evidence: budget work advertises `max_evaluations` as part of the
    AlphaEvolve-style compute-budget path, while staged cascades also expose
    samples, retries, and thresholds.
  - Status: `max_evaluations` is now documented as a seed/candidate evaluation
    cap, and detailed evaluator work units are reported separately. Evaluation
    records persist `accounting` with subprocess attempts, configured-stage
    samples, retry attempts, validator timeouts, and sample/stage
    budget-exhaustion counts; `RunBudget` accumulates those counters into
    candidate budget metadata and runtime manifests. Independent stop policies
    for those counters remain open.
  - Verification: focused budget/evaluator/loop tests cover sampled/retried
    cascades, evaluation accounting, history budget metadata, and runtime
    manifest consumed counters.
- [x] Add per-attempt versus per-stage evaluator timeout policy.
  - Evidence: `eval_stages[].timeout_sec` is a per-validator-subprocess-attempt
    timeout. `eval_stages[].max_sample_seconds` provides a per-sample
    wall-clock budget across retries, and `eval_stages[].max_stage_seconds`
    provides a stage-level wall-clock budget across samples/retries. Both clip
    attempts and record `sample_budget_exhausted` or `stage_budget_exhausted`.
  - Status: implemented. Durable consumed attempt/sample/retry/timeout and
    sample/stage budget-exhaustion counters persist in evaluation accounting,
    candidate budget metadata, runtime manifests, and `RunBudget` consumed
    state. Run-wide `max_evaluator_subprocess_attempts`,
    `max_evaluator_stage_samples`, `max_evaluator_retry_attempts`,
    `max_evaluator_timeouts`, `max_evaluator_sample_budget_exhaustions`, and
    `max_evaluator_stage_budget_exhaustions` limits now stop the synchronous
    loop after the evaluation that consumes the configured counter budget.
  - Verification: focused config, budget, loop, and manifest tests cover
    validation, budget-limit stop reasons, persisted manifest config, and a
    staged cascade whose seed consumes the subprocess-attempt budget before any
    LLM mutation call is built.
- [x] Mark budget-exhausting candidate records explicitly.
  - Roadmap evidence: current-state budget language says LibreEvolve has local
    run-budget stop accounting and per-candidate budget metadata, which can
    imply the history row that consumes the final allowed budget also records
    the reason the run stopped.
  - Status: implemented. After `RunBudget.record_evaluation()` updates
    seed/candidate counters, the loop checks run limits before taking the
    candidate history `metadata.budget` snapshot. A terminal seed or generated
    candidate that consumes `max_evaluations` or a detailed evaluator-counter
    limit now records the exhausted `metadata.budget.stop_reason`.
  - Verification: focused loop tests cover a generated candidate that consumes
    `max_evaluations=2` and a staged seed that consumes
    `max_evaluator_subprocess_attempts`, and assert the terminal history row
    stop reason matches the completed manifest stop reason.
- [x] Harden provider credential validation beyond missing environment
  variables.
  - Evidence: CLI backend preflight caught absent OpenAI/Anthropic keys, but
    previously treated whitespace-only values as present.
  - Status: implemented for CLI mutation-run preflight. OpenAI and Anthropic
    credential environment variables are stripped before presence checks, so
    empty or whitespace-only values fail before backend construction,
    run-directory overwrite cleanup, or `evolve()`.
  - Verification: focused CLI tests cover whitespace-only OpenAI and Anthropic
    keys, existing-history preservation under `--overwrite`, and the
    provider-free `--max-generations 0` path. The remaining distinction between
    local syntactic preflight and live provider authentication stays documented
    as open paper/runtime fidelity work.
- [x] Extend LLM backend preflight guarantees from the CLI to direct runtime
  calls.
  - Evidence: direct callers could invoke `evolve()` with
    `run_collision_policy: overwrite` without the CLI's credential/backend
    preflight.
  - Status: implemented. Mutation-capable direct `evolve()` calls now construct
    configured backend clients before `ProgramDatabase` prepares the run
    directory. The preflighted ensemble is reused by the generation loop, and
    seed-only/evaluation-only runs still skip provider construction.
  - Verification: direct loop tests cover missing OpenAI credentials preserving
    existing `history.jsonl` and writing no replacement manifest under
    overwrite mode. Focused tests also cover provider-free zero-evaluation
    behavior.

- [x] Decide startup ordering for all-invalid seeds versus provider preflight.
  - Evidence: provider preflight protects artifacts before mutation runs, but
    it can prevent provider-free seed diagnostics for invalid seed populations
    that would never mutate.
  - Status: policy chosen and documented. Mutation-capable CLI and direct runs
    prioritize provider/backend readiness before seed evaluation. Seed-only and
    evaluation-budget-exhausted runs still skip provider construction.
  - Verification: CLI tests cover a mutation-capable all-invalid-seed problem
    with missing OpenAI credentials preserving existing history under
    `--overwrite` and never entering `evolve()`. Core loop tests cover
    all-invalid seeds with a preflighted fake backend producing
    `no_valid_programs` without a mutation call.
- [x] Extend runtime identity secret-safety to configured `run_id`.
  - Evidence: runtime identity hardening should cover every durable manifest
    identity field, not only filesystem path components.
  - Status: implemented. Configured `run_id` values are now validated by the
    shared manifest-safe identifier path with secret-pattern rejection before
    runtime manifests are written. Generated UUID4 ids remain normal safe
    provenance ids; user-supplied ids must be syntax-safe and secret-safe.
  - Verification: focused config, CLI, and database manifest tests cover
    regex-valid provider-token-shaped ids, unsafe control-character ids, and
    normal portable ids.
- [x] Add config-file source provenance and regular-file validation to runtime
  hardening.
  - Evidence: run manifests persist effective configuration and ROADMAP runtime
    work relies on those manifests for reproducibility and future resume, so
    the source of problem-local `config.yaml` must be tracked as setup
    provenance.
  - Status: implemented for CLI-loaded problem configuration. Non-regular,
    symlinked, or Windows-junction `config.yaml` paths fail before config
    parsing, provider preflight, overwrite cleanup, or manifest writes.
    Startup manifests record `provenance.config` with explicit absence or
    present file hash and byte count.
  - Verification: focused CLI tests cover absent config provenance,
    directory-shaped config rejection, YAML diagnostics, and a real manifest
    record for a present config file.
  - Remaining scoped gap: shared YAML parser diagnostic redaction for
    non-config setup files remains tracked separately.
- [x] Add secret-safe config-file diagnostics to configuration hardening.
  - Roadmap evidence: configuration validation is a startup safety boundary for
    reproducible AlphaEvolve-style runs, and its diagnostics may be copied into
    CI logs, issue reports, or audit notes.
  - Status: implemented for CLI-loaded `config.yaml`. Startup config errors
    display `config.yaml` as the path label and redact common secret-like
    patterns from parser/key text before Click output.
  - Verification: focused CLI tests cover secret-like problem roots for
    malformed YAML and invalid UTF-8, secret-like duplicate and unknown config
    keys, directory-shaped config rejection, and platform-tolerant symlink
    rejection.
  - Remaining scoped gap: raw path/root display remains tracked separately from
    YAML parser key-text redaction.
- [x] Add YAML diagnostic redaction to setup hardening.
  - Evidence: the duplicate-key YAML loader reports duplicate keys, but PyYAML
    diagnostics can include raw `repr(key)` text.
  - Status: implemented. A shared YAML diagnostic formatter redacts common
    secret-like patterns before config, metrics, and context manifest YAML
    parse errors are surfaced through loader or CLI startup diagnostics.
  - Verification: focused CLI and loader tests cover secret-like duplicate keys
    in `config.yaml`, `metrics.yaml`, and `context/context.yaml` while
    preserving duplicate-key error class context.
  - Remaining scoped gap: raw path/root display and non-parser setup-file
    diagnostics remain tracked separately.
- [x] Add output-type anti-gaming checks to representative examples and
  benchmarks.
  - Roadmap evidence: benchmark hardening requires validators that reject
    candidate-controlled shortcut objects, not only hard-coded numeric answers
    or fixed-case memorization.
  - Status: implemented for representative smoke examples. `hello_world`,
    `sorting`, and `workspace_math` now check exact return types before scoring
    equality, so equality-spoofing objects cannot pass as valid outputs.
  - Verification: focused example tests cover valid outputs plus
    equality-spoofing and wrong-type negative cases for the representative
    validators.
  - Remaining scoped gap: stronger benchmark fixtures still need their own
    task-specific type/shape contracts.
- [x] Add direct `Problem.primary_bounds` validation to problem-schema
  hardening.
  - Roadmap evidence: problem setup and objective-schema provenance should make
    metric bounds authoritative and reproducible across loaded problems,
    direct APIs, manifests, archives, and resumed runs.
  - Status: implemented. Direct `Problem(...)` construction validates
    `primary_bounds` for numeric finite non-boolean type, increasing order, and
    exact parity with the declared primary metric bounds before normalizing the
    problem schema.
  - Verification: focused loader and loop tests cover invalid direct bounds and
    manifest persistence for matching direct bounds.
- [x] Add unknown-metric rejection to objective helper hardening.
  - Roadmap evidence: multi-objective search, prompt feedback, MAP-Elites
    normalization, and future query/resume paths rely on metric names being
    declared objective-schema identifiers.
  - Status: implemented for the helper boundary. Unknown objective helper
    lookups now fail instead of receiving implicit maximize `[0.0, 1.0]`
    semantics, while prompt rendering keeps an explicit optional path for
    plugin/feedback metrics outside the declared objective schema.
  - Verification: focused loader, prompt, loop, and evaluator diagnostics tests
    cover helper rejection, optional prompt rendering, manifest objective
    schema persistence, and declared metric-bound diagnostics.
- [x] Add immutable effective metric schemas to problem/runtime hardening.
  - Roadmap evidence: multi-objective search, MAP-Elites normalization,
    benchmark reporting, and resumability all depend on stable metric direction
    and bounds after problem setup validation.
  - Status: implemented for problem schemas. Effective metric records are
    frozen read-only mappings with immutable bounds, and manifest snapshots are
    emitted through defensive JSON-friendly copies.
  - Verification: focused loader tests cover post-construction mutation
    attempts and source-mapping mutation; prompt, loop, and evaluator tests
    cover consumers of the frozen schema.
- [x] Add `log_dir` display/path safety to runtime identity hardening.
  - Roadmap evidence: run directories and manifests are now treated as durable
    experiment evidence, but runtime identity hardening previously focused on
    `problem_name`, `run_id`, and containment diagnostics rather than the
    configured log root itself.
  - Status: implemented for configured log roots. `Config.log_dir` now fails
    unsafe path/display labels before filesystem writes, and manifest retention
    remains redacted/hash-backed for absolute or secret-like roots.
  - Verification: focused config tests cover invalid components and valid
    path-like values; CLI tests cover unsafe `config.yaml` diagnostics before
    `evolve()`; manifest tests cover safe relative and secret-like roots.
- [x] Add migrated-program deduplication to island-state hardening.
  - Roadmap evidence: repeated migrated ids can inflate elite archives and
    distort migration counts unless migration has explicit copy/reference
    semantics.
  - Status: implemented with canonical-id reference placements. Migration
    skips target islands that already contain the id and records placement
    metadata separately from source admission metadata.
  - Verification: focused island tests cover repeated migration, target-id
    skips, placement events, ring topology, and sampling deduplication.
- [x] Define migration/resume archive-id identity semantics.
  - Roadmap evidence: queryable evolutionary databases, resumable archive
    state, lineage-aware sampling, and MAP-Elites/island diagnostics require
    candidate ids to identify one archived candidate state.
  - Status: implemented as a manifest policy and runtime migration behavior.
    Archive ids are run-local canonical ids; migrations are canonical-id
    references, not clone ids; duplicate target placements are skipped; resume
    snapshot restore remains explicitly not implemented.
  - Verification: focused database tests verify `policies.archive_identity` and
    migration event returns; island tests verify canonical-reference migration.
- [x] Add immutable/snapshot program-record semantics to database hardening.
  - Roadmap evidence: accepted archive and history records should not remain
    mutable object aliases after admission/logging.
  - Status: implemented with defensive `Program` snapshots for internal
    archive/log storage and public database accessors. Caller-side
    post-admission mutation no longer rewrites in-memory database facts.
  - Verification: focused database tests cover mutation of candidate files,
    metrics, metadata, evaluation, lineage, archive-admission events, and
    returned accessor snapshots.
- [x] Add evaluation-record shape validation to database hardening.
  - Roadmap evidence: transaction and immutable-record work should also guard
    the structured evaluator-result boundary entering the database.
  - Status: implemented for direct/current records. `Program.evaluation` must
    be a JSON-safe mapping at construction and is revalidated before archive,
    history, failure-memory, seed-failure, and snapshot use.
  - Verification: focused database tests cover non-dict and non-JSON mutated
    evaluation payloads, missing/non-boolean validity handling, and malformed
    stage compatibility diagnostics.
- [x] Add workspace-aware seed failure records to database hardening.
  - Roadmap evidence: multi-file/codebase candidates and failed-trial memory
    are both part of AlphaEvolve-alignment work, so invalid initial workspaces
    should be retained as file sets rather than primary-file-only snippets.
  - Status: implemented. Seed failure rows now persist deterministic all-file
    workspace failure memory through `mutation_text` plus structured
    `seed_workspace` file records with hashes, roles, byte counts, snippets,
    and truncation flags. Single-file legacy seeds continue to work through the
    same schema.
  - Verification: focused database tests cover workspace seed content,
    persisted `seed_workspace`, malformed metrics compatibility, failed append
    rollback, evaluation-shape revalidation, malformed stage diagnostics, and
    seed-code/helper-file redaction.
- [x] Add zero-generation no-valid-seed semantics to runtime hardening.
  - Roadmap evidence: runtime work treats seed-only/evaluation-only runs as
    provider-free baselines and all-invalid startup accounting should use
    `no_valid_programs`.
  - Status: implemented. Runtime finalization now reports
    `no_valid_programs` whenever no best program exists and no explicit budget
    cap already stopped the run, including `max_generations=0` invalid-only
    seed baselines. CLI no-best behavior, manifest stop reason, history and
    failure-history artifacts, and absent best-artifact pointers are covered.
  - Verification: focused loop tests cover zero-generation invalid-only and
    mixed seeds; a focused CLI test covers nonzero no-best exit plus manifest
    and artifact-pointer alignment.
- [x] Add prompt-program template state validation to prompt archive work.
  - Evidence: prompt-program archives should not admit invalid template state
    through direct object construction, later state revalidation, or database
    insertion.
  - Status: implemented. `PromptProgram.__post_init__()` reaches
    `validate_prompt_program()`, and that validator now enforces the shared
    renderable-template rules. Database add, mutation, selection snapshots, and
    future restore paths share the same invariant through prompt-program
    revalidation.
  - Verification: focused meta-prompt tests cover invalid non-string,
    unknown-placeholder, and incompatible-format templates at construction and
    revalidation boundaries.
- [x] Add rejected-template redaction and size limits to prompt archive work.
  - Evidence: invalid evolved templates are prompt-archive diagnostics and
    should not persist unbounded raw model output or secret-like text.
  - Status: implemented. `_reject_mutation()` now records rejected templates
    through a bounded/redacted artifact schema with raw character count,
    SHA-256, redaction, and truncation metadata before the parent prompt arm is
    penalized.
  - Verification: focused meta-prompt tests cover secret-like and oversized
    rejected templates plus existing invalid-template penalty paths.
- [x] Add atomic prompt-score metadata validation to prompt-archive hardening.
  - Evidence: prompt-program score events update selection statistics and
    prompt metadata, so invalid score metadata should fail before state changes
    or leave a durable quarantine record that explains the discarded update.
  - Status: implemented. Score metadata is validated before any in-memory
    prompt-arm mutation; invalid metadata is quarantined through
    `prompt_history_invalid.jsonl` and does not advance `uses`, `reward_sum`,
    metadata, or prompt selection.
  - Verification: focused meta-prompt tests cover invalid and repeated invalid
    score metadata, non-finite reward with metadata, quarantine diagnostics,
    and selection/log consistency after rejected score events.
- [x] Add redacted prompt-score metadata persistence to prompt-archive
  hardening.
  - Evidence: prompt-program score metadata is persisted in prompt history and
    can become future prompt-evolution evidence, so JSON safety is not enough
    for archive or shareability claims.
  - Status: implemented. Prompt score metadata now receives recursive
    key/value redaction, string-size limits, and hash-backed key labels before
    it reaches prompt-program state or `prompt_history.jsonl`.
  - Verification: focused meta-prompt tests cover secret-like prompt score
    metadata keys and values, nested metadata, list values, oversized strings,
    live prompt metadata, and prompt-history persistence.
- [x] Add current-template redaction and budgets to meta-prompt evolution.
  - Evidence: meta-prompt evolution has two prompt-bearing inputs: generated
    performance evidence and the selected current template.
  - Status: implemented. Current templates are no longer appended raw to
    meta-prompt calls. They are redacted, capped, and accompanied by
    placeholder and hash/length/redaction/truncation provenance.
  - Verification: focused loop tests cover a secret-like configured template
    with a large body and confirm the meta-prompt request and mutation-context
    metadata stay bounded and non-leaking.
- [x] Add meta-prompt evidence key redaction to prompt-evolution hardening.
  - Evidence: meta-prompt evolution uses bounded redacted run evidence as
    prompt input, and dictionary keys can carry sensitive caller labels.
  - Status: implemented. Dynamic meta-prompt evidence keys are redacted,
    bounded, hash-suffixed when changed, and metric labels use the same policy.
  - Verification: focused loop tests cover nested mappings, long keys,
    non-string keys, secret-like keys, and mixed metric key sorting.
- [x] Extend plugin metadata hardening to recursive key labels.
  - Evidence: plugin provenance is part of prompt context, candidate history,
    manifest artifact summaries, and paper-inspired plugin truthfulness.
  - Status: implemented. Recursive plugin metadata keys now have secret-safe
    redacted/hash-backed labels for prompt-context metadata and run-artifact
    metadata while preserving format-control rejection.
  - Verification: focused loop tests cover prompt-context and artifact
    metadata, nested keys, secret-like keys, long keys, and manifest/history
    rendering.
- [x] Add deterministic process-tree cleanup to evaluator safety hardening.
  - Evidence: evaluator timeout cleanup must hold under normal full-suite and
    CI-like execution, not only isolated timeout tests.
  - Status: implemented. Windows validator subprocesses are assigned to a
    kill-on-close Job Object when supported, with assignment/close diagnostics
    persisted in timeout cleanup metadata. If taskkill reports un-terminated
    child PIDs, direct per-PID cleanup is attempted and recorded; POSIX killpg
    behavior remains.
  - Verification: focused evaluator timeout cleanup tests pass, and the full
    non-integration suite passed after the process-tree hardening.
- [x] Add deterministic evaluator-output decoding to evaluation hardening.
  - Evidence: evaluation diagnostics, prompt feedback, and artifact-adjacent
    records should be reproducible across host encodings.
  - Status: implemented. Validator streams are captured as bytes and decoded
    through a documented UTF-8 replacement policy before redaction/truncation.
    Decode diagnostics are stored with each evaluation result.
  - Verification: focused evaluator tests cover malformed stdout and stderr
    bytes on success plus malformed stdout on timeout.
- [x] Add explicit validator stdin policy to evaluator isolation work.
  - Evidence: runtime hardening requires stronger evaluator isolation, resource
    controls, and deterministic accounting, including standard input behavior.
  - Status: implemented. Validator subprocess stdin is connected to
    `subprocess.DEVNULL`, and stdin policy metadata is persisted on each
    direct/configured evaluation result.
  - Verification: focused evaluator tests cover EOF behavior, empty stdin
    reads, and configured-stage sample diagnostics.
- [x] Add skipped-link target identity to provenance hardening.
  - Roadmap evidence: provenance hardening includes tree hashes, skipped-file
    diagnostics, and link/junction safety, but it did not require skipped link
    records to distinguish which external target was skipped.
  - Status: implemented. Provenance hardening now records hash-backed target
    identity, target scope, within-root status, and unresolved-target
    diagnostics for skipped symlinks/junctions, with v2 skipped/provenance hash
    scopes.
  - Verification: focused provenance tests cover file symlink and Windows
    junction target changes across the supported local platform behavior.
- [x] Add persistence parent-directory preflight to artifact hardening.
  - Roadmap evidence: artifact hardening covers strict JSON, quarantine streams,
    manifest writes, and crash/durability policy, but it did not require the
    persistence layer to handle missing parent directories coherently.
  - Status: implemented. Artifact persistence helpers create missing parent
    directories for valid strict JSON/JSONL/quarantine writes and convert
    invalid parent path types into bounded, secret-redacted `StrictJsonlError`
    diagnostics.
  - Verification: focused JSONL tests cover manifest, stream, quarantine, and
    invalid-parent paths; TTTRL plugin tests cover plugin export paths.
- [x] Add archive-admission identity checks to run-inspection and resume work.
  - Roadmap evidence: runtime/resume work treats history rows, archive
    admission metadata, and database restore as durable experiment provenance.
  - Status: implemented for current run inspection and documented for
    compatibility. `show` now requires present archive-admission `program_id`
    fields to be manifest-safe and equal to the row `id`; older rows without the
    field remain accepted. Snapshot resume restore and queryable database
    reconstruction are not current implementation paths and remain tracked by
    broader open resume/database work.
  - Verification: focused CLI tests cover matching, missing, mismatched,
    selected, unselected, and unsafe archive-admission program ids.
- [x] Add dependency-name redaction to runtime provenance hardening.
  - Roadmap evidence: runtime manifests are intended to be reproducibility and
    sharing evidence for AlphaEvolve-style experiments, and dependency specs
    are already partially redacted.
  - Status: implemented. Runtime dependency provenance now separates safe
    display names from raw identity hashes, redacts secret-like names, and
    records redacted/hash-backed installed-version lookup identity when unsafe
    names prevent raw lookup.
  - Verification: focused provenance tests cover public, private-source, and
    secret-like dependency names plus installed-version lookup behavior.
- [x] Add `__pycache__` path-policy parity to candidate workspace hardening.
  - Roadmap evidence: candidate workspace fidelity depends on one consistent
    source-file path grammar across seed loading, mutation, direct construction,
    prompts, evaluation workspaces, and exported artifacts.
  - Status: implemented. Candidate path normalization now forbids `__pycache__`
    components for generated/direct candidates while loader cache skipping
    remains the seed-ingestion policy.
  - Verification: focused candidate tests cover direct and mutation-created
    cache paths, and loader tests cover hidden/cache seed-directory behavior.
- [x] Add immutable archive-sequence state to recency sampling hardening.
  - Roadmap evidence: parent/inspiration sampling strategies are intended to
    resurface candidates by recency, novelty, metric leadership, and selection
    score.
  - Status: implemented for live search state. `IslandModel` maintains internal
    archive insertion order for recency sampling and treats persisted
    `archive_sequence` metadata as audit data rather than a sampling authority.
    Snapshot restore/queryable replay semantics remain part of broader open
    resume/database work.
  - Verification: focused island tests cover parent/inspiration recency after
    direct archive-sequence metadata mutation.
- [x] Add launcher-consistent CLI help to documentation hardening.
  - Roadmap evidence: operational maturity and docs truthfulness require the
    commands shown to Windows users and agents to match the supported local
    launcher contract.
  - Status: implemented. Module execution now supplies an explicit Click
    program name so root and subcommand help use
    `py -3.12 -m libreevolve`.
  - Verification: subprocess tests cover root and `run` help through
    `-m libreevolve`, and direct help checks confirmed the stale
    `python -m libreevolve` banner no longer appears.
- [x] Add portable paper-manifest path validation to documentation/CI work.
  - Status: implemented and documented. Paper-cache validation now rejects
    Windows-reserved, hidden, Unicode control/format, and ambiguous path
    spellings.
  - Verification: focused paper-manifest tests cover the unsafe path proof
    cases and the committed manifest validates cleanly.
- [x] Add unique-paper-artifact checks to paper-index validation.
  - Status: implemented. Validator now reports unique local file count and
    rejects duplicate normalized file targets and duplicate digests.
  - Verification: focused tests cover duplicate file target/digest rows.
- [x] Add duplicate CSV-id checks to paper-index validation.
  - Status: implemented. Duplicate CSV ids are diagnosed before CSV/JSON row
    comparison.
  - Verification: focused tests cover duplicate CSV ids directly.
- [x] Add paper-manifest row-id grammar validation to paper-index hardening.
  - Status: implemented. Paper ids are constrained to arXiv ids or lowercase
    foundational slugs and secret-like ids are rejected/redacted.
  - Verification: focused CLI JSON tests cover secret-like ids.
- [x] Add README badge-count checks to paper-index validation.
  - Status: implemented. README badge counts are included in documented-count
    validation and malformed badges are reported.
  - Verification: focused tests cover mismatched and malformed badge counts.
- [x] Add paper-manifest URL validation to paper-index hardening.
  - Status: implemented. Source URLs are restricted to known HTTPS paper source
    hosts and secret-like URL text fails validation.
  - Verification: focused CLI JSON tests cover unsafe local `file:` URLs.
- [x] Add paper-manifest message redaction and size limits.
  - Status: implemented. Download messages are bounded to 512 characters for
    validation/reporting and are redacted in availability output.
  - Verification: focused tests cover oversized secret-bearing messages.
- [x] Add paper-title display and secret-safety validation to the paper index.
  - Status: implemented. Manifest titles have display-safety, length, and
    secret-like text validation.
  - Verification: focused CLI JSON tests cover unsafe multiline titles.
- [x] Close the paper-manifest schema.
  - Status: implemented. Unsupported JSON fields and CSV headers now fail
    validation, giving the paper index a closed field contract.
  - Verification: focused tests reject secret-like extra fields/columns.
- [x] Add duplicate-key-safe JSON parsing to paper-index validation.
  - Status: implemented. JSON manifest loading detects duplicate object names
    instead of relying on last-key-wins parsing.
  - Verification: focused tests reject duplicate `url` keys.
- [x] Add duplicate-header diagnostics to CSV paper-index validation.
  - Status: implemented. CSV header validation detects duplicate headers before
    row normalization.
  - Verification: focused tests reject duplicate `url` headers.
- [x] Add empty-CSV header validation to paper-index hardening.
  - Status: implemented. CSV schema validation runs even when no data rows are
    present.
  - Verification: focused tests reject a zero-row CSV with wrong headers.
- [x] Add PDF-content integrity checks to paper-index validation.
  - Status: implemented. Required-local paper-cache validation now checks the
    `%PDF-` header before treating a local artifact as a present PDF.
  - Verification: focused tests reject matching plain-text bytes in a `.pdf`.
- [x] Add streaming local-PDF hashing to paper-index validation.
  - Status: implemented. SHA-256 verification streams local PDFs in bounded
    chunks and keeps structured read-error diagnostics.
  - Verification: focused tests prove `Path.read_bytes()` is not used for a
    large matching PDF.
- [x] Define strict handling for failed paper-download manifest rows.
  - Status: implemented. Failed historical download rows now emit
    `download_failed` issues.
  - Verification: focused tests cover `ok: false` with a matching local file.
- [x] Enforce the gitignored-local-PDF policy in paper-cache validation.
  - Status: implemented. Git-tracked manifest PDFs now produce validation
    issues.
  - Verification: focused tests cover staged local PDFs.
- [x] Add local-only PDF detection to paper-cache validation.
  - Status: implemented. Strict local validation scans `papers/*.pdf` for files
    not listed in the committed manifests.
  - Verification: focused tests cover unmanifested local PDFs under
    `--require-local-pdfs`.
- [x] Validate the paper implementation-status table against manifest IDs.
  - Status: implemented. Paper-index validation now parses the
    implementation-status section and reports missing, extra, or duplicate
    table IDs.
  - Verification: focused tests cover table/manifest mismatch scenarios and
    the current `papers/README.md` table validates against all 24 manifest IDs.
- [x] Add link-backed PDF detection to paper-cache validation hardening.
  - Status: implemented. Local paper-cache validation rejects symlink-backed
    and Windows reparse-point PDF entries before byte/hash validation.
  - Verification: focused tests cover both link-detection branches.
- [x] Add agent-instruction checks for archive-admission semantics.
  - Status: implemented. Agent-doc checks now require the threshold gate to be
    distinguished from MAP-Elites replacement, elite retention, and sampling
    eligibility.
  - Verification: focused AGENTS doc tests reject the old threshold-only
    `ProgramDatabase.admit()` archive-entry wording.
- [x] Add direct critique prompt input validation to prompt hardening.
  - Status: implemented. Direct critique prompt helper calls now validate
    text shape, reject empty required sections, and apply the local bounded
    redaction policy before rendering the provider prompt.
  - Verification: focused feedback tests cover malformed, oversized, and
    secret-like direct critique prompt inputs.
- [x] Add direct feedback-grader prompt validation to evaluation hardening.
  - Status: implemented. Direct feedback-grader validation now covers `prompt`
    fields before LLM calls and records malformed prompt specs through the
    existing `invalid_feedback_config` path.
  - Verification: focused tests cover config parity, default prompt behavior,
    non-string prompt rejection, redaction, and truncation.
- [x] Add direct feedback-grader schema validation to evaluation hardening.
  - Status: implemented. Direct feedback-grader specs now validate mapping
    shape, string keys, allowed fields, labels, metrics, prompt text, numeric
    policies, and failure policies before feedback LLM calls or invalid-candidate
    filtering.
  - Verification: focused feedback tests cover non-mapping graders on invalid
    candidates, unsupported fields, non-string keys, and invalid-config
    metadata without LLM calls.
- [x] Add aggregate size limits to plugin provenance hardening.
  - Status: implemented. Plugin provenance metadata now has deterministic
    nesting-depth, item-count, and serialized JSON character limits shared by
    prompt-context metadata and run-artifact metadata.
  - Verification: focused loop tests cover oversize aggregate JSON, too many
    metadata items, and excessive metadata nesting.
- [x] Add skipped-context read budgets to context-ingestion hardening.
  - Status: implemented. Skipped-file provenance now uses a bounded stat-first
    policy and omits hashes for skipped files over `max_bytes_per_source`.
  - Verification: focused loader tests cover unsupported, excluded,
    hidden-not-included, not-included, and selected oversized context files.
- [x] Add schema validation for persisted problem-context provenance.
  - Status: implemented. Startup manifests now receive validated/redacted
    problem context provenance from both loader and programmatic `Problem`
    construction paths.
  - Verification: focused tests cover direct database and `evolve()` paths for
    malformed context policy/source payloads, non-finite values, oversized
    context provenance, and secret redaction.
- [x] Add strict structured parsing to LLM feedback roadmap work.
  - Status: implemented. LLM feedback responses now use duplicate-key-aware JSON
    parsing and route ambiguous grader output through the existing
    `llm_feedback_failed` path.
  - Verification: focused feedback tests cover normal JSON, duplicate
    score/discard/feedback names, nested duplicates, fenced JSON, and failed
    grader outcomes.
- [x] Add duplicate-key rejection to manifest runtime-update hardening.
  - Status: implemented. `ProgramDatabase.update_manifest_runtime()` now fails
    ambiguous existing manifests instead of using Python's last-key-wins JSON
    semantics before writing completed/aborted runtime state.
  - Verification: focused database tests cover current manifests, top-level
    duplicates, nested duplicates, corrupt JSON recovery, and invalid runtime
    replacement payloads.
- [x] Add exact non-contiguous PDF page provenance to context roadmap work.
  - Status: implemented. PDF context ingestion now records exact extracted page
    lists separately from first/last page ranges.
  - Verification: focused loader tests cover skipped blank PDF pages and prove
    non-contiguous page provenance remains explicit.
- [x] Clarify PDF citation span coordinate systems in context roadmap work.
  - Status: implemented. PDF context metadata stores both global concatenated
    excerpt offsets and page-local excerpt offsets; prompt surfaces use
    page-local coordinates.
  - Verification: focused loader, prompt, and feedback tests cover multi-page
    excerpts where inserted separators change global offsets.
- [x] Add cached-PDF prose count checks to paper-index validation.
  - Status: implemented. Paper-index validation recognizes the cached-PDF count
    phrase used by `papers/README.md` and compares it to manifest rows.
  - Verification: focused paper-manifest tests cover cached-PDF prose wording
    that disagrees with the manifest count.
- [x] Add structured README count-surface read errors to paper-index
  validation.
  - Status: implemented. README count-source and papers README status-table
    read failures now surface as structured issues instead of uncaught
    exceptions.
  - Verification: focused paper-manifest tests cover invalid UTF-8 in both
    count-source files.
- [x] Add conflicting README count-source diagnostics to paper-index
  validation.
  - Status: implemented. Paper-index validation now retains per-source count
    records for README prose, README badges, and `papers/README.md` prose and
    reports disagreement as `documented_count_conflict` with paths, values, and
    matched phrases.
  - Verification: focused paper-manifest tests cover cross-file and same-file
    count disagreements plus matching count surfaces.
- [x] Add Unicode-normalized context-path collision handling to context work.
  - Status: implemented. Context selection now uses NFC-aware include/exclude
    matching, normalizes selected source display labels, preserves differing
    raw filesystem paths, and rejects duplicate normalized selected labels.
  - Verification: focused loader tests cover prompt-facing `context_files`,
    `context_sources`, skipped-source diagnostics, and duplicate selected
    composed/decomposed paths.
- [x] Add Unicode-normalized path collision handling to provenance hardening.
  - Status: implemented. Source/problem tree provenance now defines normalized
    path identity semantics for included and skipped file records, preserves
    raw filesystem spelling when it differs, and rejects duplicate included
    records after NFC normalization.
  - Verification: focused provenance tests cover problem provenance, shared
    source-tree provenance, skipped diagnostics, and manifest JSON
    serialization-compatible records.
- [x] Add plugin class/module label safety to plugin provenance hardening.
  - Status: implemented. Startup provenance, plugin artifacts, plugin failures,
    prompt-context metadata, score-composition records, and candidate history
    now share one redacted/hash-backed runtime plugin identity policy.
  - Verification: focused provenance and loop tests cover unsafe class/module
    labels across direct plugin instances, startup manifests, artifact
    attribution, prompt-context metadata, and candidate history.
- [x] Add pyproject metadata field safety to runtime provenance hardening.
  - Status: implemented. Runtime provenance now applies a validated,
    redacted/hash-backed package-source retention policy to project name,
    version, requires-python, build backend, and build requirements.
  - Verification: focused provenance tests cover clean and unsafe pyproject
    metadata plus installed-version lookup behavior for redacted project names.
- [x] Add pyproject diagnostic redaction to runtime provenance hardening.
  - Status: implemented. Runtime provenance now records pyproject read, decode,
    and parse failures with bounded, secret-redacted diagnostics and leaves
    schema diagnostics path-aware and value-free.
  - Verification: focused provenance and CLI tests cover manifest JSON safety,
    malformed TOML, invalid encoding, invalid requirement schemas, oversized
    exceptions, and current `show` output.
- [x] Add secret-safe paper-manifest validator diagnostics to docs/papers
  validation.
  - Status: implemented. The documentation-truthfulness roadmap now includes
    paper-manifest diagnostic shareability, and the validator reports
    repository-relative manifest/README labels with redacted exception text.
  - Verification: focused paper-manifest tests cover text and JSON CLI output
    for missing manifests, malformed JSON, and README/status-table read
    failures under a secret-like validation root.
- [x] Add secret-safe provenance root metadata to manifest hardening.
  - Status: implemented. Runtime manifest hardening now treats source/problem
    tree roots and Git roots as local display labels with stable root hashes
    and redaction metadata.
  - Verification: focused provenance and loop tests cover secret-like problem
    and Git roots, source-root redaction, and manifest Git lookup from the real
    source package root.
- [x] Add parent/lineage graph validation to database hardening.
  - Status: implemented. Program identity validation now includes lineage graph
    invariants for self-parenting, self-in-lineage, duplicate ancestors, and
    parent-tail consistency.
  - Verification: focused program, database, MAP-Elites, island, and CLI tests
    cover direct construction, persistence snapshots, archive/island validation,
    and legacy history inspection diagnostics.
- [x] Add failed-candidate id uniqueness to database/resume hardening.
  - Status: implemented. Failed-candidate records now use unique run-local
    program ids within `failure_history.jsonl`; duplicate failed ids are
    quarantined rather than appended.
  - Verification: focused database tests cover generated failures, seed
    failures, quarantine diagnostics, and repetition counts for distinct
    candidates with matching fingerprints.
- [x] Add boolean-bound rejection to metric-schema hardening.
  - Status: implemented. ROADMAP's strict metric-bound validation wording now
    explicitly includes non-boolean bounds, matching loader/direct `Problem`
    and database objective-schema validation.
  - Verification: focused loader and database tests distinguish boolean bounds
    from numeric `0/1` metric bounds and reject boolean primary bounds in
    objective schemas.
- [x] Keep ROADMAP's strict metric-bound validation claim accurate for
  boolean bounds.
  - Status: resolved. The roadmap no longer overclaims by implication: boolean
    metric bounds are now rejected, and the current-state wording names
    non-boolean metric bounds explicitly.
  - Verification: focused loader and database tests cover the validation paths
    that make the roadmap wording accurate.
- [x] Add secondary-metric parent selection to metric-aware search.
  - Status: implemented. Metric-aware parent selection now cycles through
    configured metric targets, primary first, then secondary metrics and
    unconfigured normalized metrics, with target-metric provenance persisted on
    generated candidates.
  - Verification: focused island/database tests cover primary and secondary
    metric parent selection, and focused loop tests cover persisted target
    metadata.
- [x] Add bounded invalid-prompt penalty semantics to prompt archive hardening.
  - Status: implemented. Rejected prompt children increment parent prompt uses
    and apply the configured lower-bound reward through prompt reward
    normalization, with policy metadata persisted in `last_prompt_penalty`.
  - Verification: focused meta-prompt tests cover rejected-template histories,
    configured reward bounds, and parent selection after invalid mutations.
- [x] Add prompt-mutation rejection accounting to prompt-archive hardening.
  - Status: implemented. Invalid evolved prompt templates now create explicit
    rejection records, update parent prompt-arm uses and reward statistics on
    the bounded prompt scale, and avoid mutating parent state when rejection
    metadata is not strict-JSON-safe.
  - Verification: focused meta-prompt tests cover never-used and already-used
    parent prompts plus invalid rejection metadata rollback.
- [x] Add YAML anchor/alias policy to setup and provenance hardening.
  - Status: implemented. Setup YAML now rejects anchors and aliases at the
    shared loader before config, metrics, context manifests, or provenance
    records are normalized.
  - Verification: focused loader and CLI tests cover anchor/alias diagnostics
    for metrics, context manifests, bare aliases, and CLI `config.yaml`.
- [x] Add secret-like run-name validation to runtime identity hardening.
  - Status: implemented. Runtime identity validation now rejects secret-like
    `problem_name` and CLI `--run-name` values before run-directory preparation
    or manifest persistence.
  - Verification: focused config tests cover direct run-name validation and
    focused CLI tests cover the user-facing override path before `evolve()`.
- [x] Add skipped context-path redaction/validation to context-ingestion
  hardening.
  - Status: implemented. Context ingestion now applies secret-like label
    rejection to skipped diagnostic paths before retaining them as context
    policy provenance.
  - Verification: focused loader tests cover unsupported, excluded, hidden,
    not-included, per-source-byte, and total-byte skipped-source paths.
- [x] Add candidate and seed path-label safety to multi-file candidate work.
  - Status: implemented. Candidate representation now rejects secret-like file
    labels at workspace normalization, mutation parsing, direct program
    construction, and loaded seed-source provenance boundaries.
  - Verification: focused candidate, loader, and program tests cover direct,
    mutation-created, top-level seed, workspace seed, and `Program(files=...)`
    paths.
- [x] Add compatibility-confusable Unicode path policy to codebase-candidate
  hardening.
  - Status: implemented. Codebase candidate file labels now use an NFC plus
    NFKC-stable policy, rejecting Unicode separator-space variants,
    compatibility aliases, and surrogate code points.
  - Verification: focused candidate tests cover representative separator
    spaces, fullwidth Latin, Kelvin sign, surrogate labels, and ordinary
    non-ASCII names.
- [x] Add direct seed-source provenance schema validation to runtime setup.
  - Status: implemented. Runtime setup now validates direct and loader-created
    seed provenance through one schema before manifest/database mutation.
  - Verification: focused database and loop tests cover schema errors,
    path-label safety, index/count consistency, and valid records.

- [x] Add direct problem-context file schema validation to prompt hardening.
  - Status: implemented. Prompt hardening now validates direct context mapping
    shape, path labels, Unicode stability, secret-like labels, and per-value
    length before prompt construction; runtime setup uses the same validator.
  - Verification: prompt and loop tests cover direct build/prompt diagnostics,
    pre-artifact `evolve()` failure, and source metadata redaction while
    preserving loader-compatible context labels.

- [x] Add direct task-description validation to prompt/setup hardening.
  - Status: implemented. Direct task text now has one prompt/setup validation
    path for non-empty text, size bounds, secret-like content rejection, unsafe
    control rejection, and exact retention of valid task text.
  - Verification: focused prompt and loop tests cover direct construction
    diagnostics before prompt rendering and before run artifacts are created or
    overwritten.

- [x] Move direct inline-seed validation before run-directory preparation.
  - Status: implemented. Runtime setup now validates direct inline seed
    container shape, per-entry text type, UTF-8 encodability, size bounds, and
    evolve-block markers before database/run-directory setup.
  - Verification: focused loop tests cover malformed direct inline seeds
    leaving existing artifacts untouched and valid direct inline seeds
    retaining inline seed provenance.

- [x] Move direct initial-workspace validation before run-directory
  preparation.
  - Status: implemented. Runtime setup now accepts only normalized
    `CandidateWorkspace` entries or workspace record mappings before
    database/run-directory setup, including revalidation of mutated workspace
    objects and evolve-block markers.
  - Verification: focused loop tests cover malformed direct workspaces leaving
    existing artifacts untouched and valid direct workspace records retaining
    workspace seed provenance.

- [x] Reconcile elite-only archive retention with resurfacing strategy.
  - Status: implemented. The roadmap policy now treats elite-only candidates
    as durable retained archive members rather than audit-only records; they
    can influence future search through explicit retained-archive strategies
    while still remaining outside occupied-cell explore/random pools.
  - Verification: `IslandModel` and public `ProgramDatabase` tests prove
    retained elite-only programs resurface through metric, novelty, recency,
    selection, and mixed sampling, and existing MAP-Elites coverage preserves
    the cell-eligibility distinction.

- [x] Add language-aware evolve-block markers to codebase-candidate roadmap
  boundaries.
  - Status: implemented as an explicit roadmap boundary. ROADMAP now states
    that language-aware evolve-block marker grammars remain future work if
    non-Python workspace files should preserve skeleton regions. The current
    implementation rejects marker-like declarations in non-`.py` files instead
    of treating them as unmarked full-file candidates.

- [x] Separate optimization-pressure examples from plateau/diversity examples.
  - Status: implemented. ROADMAP now records the current example seed-score
    classes: `hello_world`, `circle_packing`, and `matrix_multiplication` are
    optimization-pressure smoke fixtures, while `sorting` is a neutral
    plateau/diversity fixture. Broader benchmark-fixture hardening remains open.

- [x] Add durable LLM call-artifact work to runtime/backend hardening.
  - Status: implemented for config-created ensembles. Runs now write
    `llm_calls.jsonl` as an append-only strict JSONL stream with call rows,
    reward rows, sequence ids, prompt/output hashes, retry/fallback state,
    backend provenance, and scheduler counters. ROADMAP now keeps the remaining
    backend/runtime hardening focused on replay/readers and future resume or
    async accounting.

- [x] Add critique prompt budget/retention policy to reviewer hardening.
  - Status: implemented. Critique prompt construction now has explicit
    redaction/truncation boundaries for base prompt, mutation text, and custom
    critique instructions, while generated-candidate critique metadata retains
    bounded redacted prompt/original/revised mutation text plus hashes and
    truncation diagnostics. Reviewer-pool expansion remains separate roadmap
    work; no-valid-mutation selection policy is completed below.

- [x] Add no-valid-mutation critique-selection policy to prompt/evaluation
  hardening.
  - Status: implemented. Critique/self-revision selection is deterministic:
    valid revised mutations are selected, invalid revisions fall back to a
    valid original mutation, and invalid original plus invalid revised cases
    preserve the original generated mutation with
    `fallback_reason="no_valid_mutation"` and both parser diagnostics.
  - Verification: focused loop tests cover invalid original plus invalid
    revised candidates in `diff` and `full` mutation modes. README and
    run-artifact docs describe the persisted selection policy.

- [x] Add wall-clock timestamp provenance to run-manifest/resume work.
  - Status: implemented for current runs and documented as the resume schema
    boundary. Runtime manifests now carry UTC wall-clock start/update/finish
    timestamps, completed/aborted status-specific fields, monotonic elapsed
    budget linkage, and an initial process segment. Future resume support can
    retain the original `started_at` while appending resumed segments.
  - Verification: focused budget and loop tests cover timestamp schema,
    completed manifests, and aborted manifests. README/run-artifact docs
    describe monotonic versus wall-clock semantics.

- [x] Add manifest-runtime awareness to `show` and run inspection.
  - Status: implemented. `show` combines the selected history row with
    `manifest.json.runtime.status` when available, labels completed runs,
    aborted best-so-far runs, and partial manifests without runtime
    finalization, and rejects inconsistent manifest/history row counts.
  - Verification: CLI tests cover completed, aborted, missing-runtime,
    missing-manifest, and mismatched-history manifest cases.

- [x] Add generated-run exclusion/classification to problem provenance
  roadmap work.
  - Status: implemented. Problem provenance preserves ordinary fixture data
    under `runs/` but excludes generated run-artifact directories under
    `runs/` when they contain known LibreEvolve artifact markers. The active
    run root remains explicitly excluded through the generated-root path.
  - Verification: provenance tests cover stale generated run directories,
    active run directories, fixture data under `runs/`, and stable problem
    hashes when stale generated artifact contents change.

- [x] Add configured-vs-loaded plugin state to runtime/plugin roadmap.
  - Status: implemented. Runtime manifests now include `runtime.plugin_state`
    so configured plugin labels can be compared with loaded runtime plugin
    identities, including explicit mismatch diagnostics for direct API runs.
  - Verification: focused loop tests cover configured labels without loaded
    plugin instances and loaded plugin instances without configured labels.

- [x] Add best-artifact link/junction safety to runtime artifact work.
  - Status: implemented for CLI best export. The post-run exporter rejects
    symlink or Windows-junction visible, temporary, and backup best-artifact
    paths before replacement or cleanup, aligning selected-best outputs with
    the linked-artifact boundary used by run-directory startup cleanup.
  - Verification: focused CLI tests cover linked `best.py`,
    symlink-capable linked `best_workspace`, Windows-junction
    `best_workspace`, and normal replacement/preservation behavior.

- [x] Add best-artifact rollback failure accounting to runtime artifact work.
  - Status: implemented for CLI best export. Replacement recovery keeps the
    original export failure primary, records rollback and cleanup errors as
    secondary manifest/CLI diagnostics, and preserves unrestored backup paths
    for inspection instead of deleting them during cleanup.
  - Verification: focused CLI tests cover install failure rollback, rollback
    failure, cleanup failure, previous-artifact preservation, and manifest
    persistence of redacted recovery diagnostics.

- [x] Add recursive link preflight to candidate workspace materialization
  hardening.
  - Status: implemented. Existing materialization roots and cleanup targets are
    recursively scanned for symlinks and Windows junctions before any root
    replacement or stale-tree removal.
  - Verification: focused candidate tests cover normal stale-root replacement,
    nested symlink rejection where supported, Windows nested-junction
    rejection, and linked ancestor rejection.

- [x] Add CausalPlugin factor-bandit initialization policy to plugin
  truthfulness.
  - Status: implemented. The causal plugin now has a documented
    `pull_once_then_ucb1_like` factor-selection policy: each fixed factor is
    selected once in stable order before UCB-like reward scoring.
  - Verification: focused causal plugin tests cover first-untried selection,
    first positive reward behavior, all-factor-observed scoring, and reported
    artifact metadata.

- [x] Add secret-safe evaluator source path provenance to runtime hardening.
  - Status: implemented. Evaluator source records now separate reproducibility
    hashes from path disclosure by storing redacted problem-relative path labels
    with `path_hash` / `relative_path_hash` fields and configured-stage path
    hash/redaction metadata.
  - Verification: focused evaluator provenance tests cover default validators,
    configured validators, secret-like validator filenames, and absolute
    problem-local configured paths.

- [x] Add bounded/read-error handling for evaluator entrypoint hashing.
  - Status: implemented. Runtime evaluator source provenance now defines full
    source hashes as streamed full-file hashes with fixed chunk-size metadata
    and redacted structured read-error diagnostics for hash failures.
  - Verification: focused evaluator provenance tests cover large validator
    files, configured-stage read failures, and multi-stage validator records.

- [x] Add evaluator-result schema validation to cascade hardening.
  - Status: implemented. Evaluator result and stage dataclasses validate
    schema-safe fields both at construction and when `to_dict()` is called, so
    direct/plugin/feedback mutations cannot preserve arbitrary Python objects
    into history, prompts, artifacts, or resume-facing records.
  - Verification: focused evaluator tests cover rejected raw objects,
    non-finite numbers, unsafe metadata, and post-construction mutation before
    strict JSON persistence.

- [x] Add finite-fitness semantics to program-model hardening.
  - Status: implemented. Direct `Program` construction now uses an internal
    unevaluated sentinel for omitted fitness, preserves the legacy `-inf`
    default only for unevaluated programs, and rejects explicit boolean,
    nonnumeric, `nan`, `inf`, and `-inf` fitness values.
  - Verification: focused program/database/evaluator tests cover default
    unevaluated programs, rejected explicit non-finite fitness, finite
    evaluator outputs, archive/database rejection of invalid mutations, and
    show-time invalid-fitness diagnostics for legacy histories.

- [x] Add finite-score validation to CausalEvolve-inspired plugin hardening.
  - Status: implemented. `CausalPlugin.on_evaluated()` rejects boolean,
    nonnumeric, and non-finite score inputs before mutating causal history, and
    malformed restored history is quarantined before prompt guidance or future
    score deltas are computed.
  - Verification: focused causal plugin tests cover `nan`, `inf`, `-inf`,
    string, and boolean score rejection, unchanged history/counters after
    rejection, malformed restored-history quarantine, and prompt-context
    suppression of `delta=+nan`.

- [x] Add skipped/empty seed-workspace diagnostics to candidate fidelity.
  - Status: implemented. Seed loading records skipped hidden/cache seed paths,
    unsupported top-level files, empty seed directories, and all-skipped seed
    directories in `initial_workspace_skipped` and manifest
    `problem.seed_skipped`; no-seed errors include skipped path/reason previews.
  - Verification: focused loader, database, and loop tests cover hidden/cache
    entries, empty and fully skipped directories, unsupported-only roots, mixed
    roots, and manifest persistence.

- [x] Add unsupported top-level seed-file diagnostics to candidate fidelity.
  - Status: implemented. Non-`.py` top-level files under `initial_programs/`
    no longer disappear silently; they are recorded as skipped seed diagnostics
    and included in no-seed error previews when no loadable seed remains.
  - Verification: focused loader and loop tests cover unsupported-only and
    mixed supported/unsupported seed roots.

- [x] Scope PEP 621 package metadata in manifest provenance.
  - Status: implemented as a deliberately narrow execution-identity contract.
    Runtime manifests record selected package/build metadata and direct runtime
    dependency versions, while README and run-artifact docs explicitly exclude
    non-execution PEP 621 fields and dev/test optional dependency groups from
    package metadata.
  - Verification: focused runtime-environment provenance tests cover included
    package/build fields, dependency provenance, redaction/escaping, malformed
    pyproject diagnostics, and missing-pyproject behavior.

- [x] Add candidate workspace size budgets to multi-file candidate work.
  - Status: implemented as manifest-visible text workspace limits:
    file-count, per-file character, and total character budgets reject
    oversized workspaces before they flow into prompts, evaluator
    materialization, history rows, or best exports. Blob-store spillover remains
    explicitly not implemented in the manifest policy.
  - Verification: focused candidate/config/database/loop tests cover model
    limits, configured limits, manifest policy, and direct seed/workspace
    preflight.

- [x] Decide Python-primary policy for seed workspace fidelity.
  - Status: decided and implemented for the current Python code-file-set
    candidate model. Loaded seed workspaces must have a Python primary file;
    no-Python seed directories become skipped setup diagnostics rather than
    implicit non-Python candidate abstractions.
  - Verification: loader tests cover text-only directory diagnostics in both
    mixed and no-loadable-seed setups, and problem-format/run-artifact docs
    now state the policy.

- [x] Add multiline proposal metadata parsing policy to prompt hardening.
  - Status: implemented as an explicit prompt/parser contract. Built-in prompts
    now allow short one-line proposal fields or bounded multiline proposal
    blocks, and parser validation rejects ambiguous wrapped colon-style
    metadata before mutation application.
  - Verification: focused prompt, parser, and loop tests cover rendered
    instructions, bounded multiline metadata, malformed continuation rejection,
    and synthetic full-mode failure accounting.

- [x] Add mutation-mode coverage to causal/plugin roadmap work.
  - Status: implemented for CausalPlugin's fixed local factor set. Diff-mode
    mutations use the shared compact/canonical SEARCH/REPLACE parser, while
    full-mode replacement payloads are scanned directly for the same
    token-pattern factors and recorded with mutation-mode history metadata.
  - Verification: focused causal plugin tests cover full-mode algorithm and
    helper-function factors, and README/plugin/paper docs describe the boundary.

- [x] Add structured CSV parser coverage to paper-index validation.
  - Status: implemented. The paper-manifest CSV loader now uses strict CSV
    parsing, and CLI diagnostics report malformed quoting as
    `csv_manifest_unreadable` in both text and JSON output.
  - Verification: paper-manifest tests cover malformed quoting, invalid UTF-8,
    duplicate headers, missing and unsupported columns, row-schema failures,
    duplicate ids, and clean manifests.

- [x] Add complete structured JSON parse/schema coverage to paper-index
  validation.
  - Status: implemented. The paper-manifest JSON reader now has explicit
    CLI-facing coverage for malformed JSON, invalid UTF-8, wrong top-level
    schema, row-schema failures, missing fields, duplicate keys, and clean
    manifests.
  - Verification: paper-manifest tests cover the structured JSON parse/schema
    issue-code matrix in both validator and CLI JSON paths.

- [x] Add strict/degraded modes for explicit context extraction failures.
  - Status: implemented. `context.yaml` defaults
    `on_explicit_context_failure` to `error`, so selected sources matched by
    include patterns fail problem loading when text/PDF extraction fails,
    returns no usable text, or exceeds PDF extraction budgets. The explicit
    `warn` mode permits degraded loading and records compact
    `explicit_context_failures` diagnostics in `problem.context_policy`.
  - Verification: focused loader tests cover invalid UTF-8 explicit includes,
    mixed good/bad include sets, corrupt PDFs, no-text PDFs, PDF page/resource
    limits, invalid policy values, and the degraded warning path; README,
    problem-format, run-artifact, and paper-index docs describe the boundary.

- [x] Add pre-parent versus pre-prompt plugin phases to runtime/plugin
  hardening.
  - Status: current ordering is intentionally the documented plugin API rather
    than a split pre-parent/pre-prompt hook pair. `on_generation_start()` is
    post-parent and pre-prompt: it can affect inspiration sampling and prompt
    context, but not the active generation's already selected parent.
  - Verification: a focused loop regression covers a plugin that mutates the
    database in `on_generation_start()` by admitting a high-scoring program;
    the generated child keeps the pre-hook seed parent while the injected
    program becomes available for post-hook inspiration sampling.

- [x] Add blank and oversized mutation payload schema validation to parser
  hardening.
  - Status: implemented at the shared mutation-helper boundary. Direct
    candidate and workspace mutation helpers now reject non-text, blank or
    whitespace-only, and oversized mutation payloads before diff/full parsing.
    Blank fenced wrappers normalize to `blank_mutation_payload`, and payloads
    over `DEFAULT_MAX_MUTATION_PAYLOAD_CHARS` return
    `oversized_mutation_payload`.
  - Verification: focused candidate tests cover blank, fenced-blank, oversized,
    and non-text payloads across `diff` and `full` modes. Evaluator tests keep
    blank and oversized payload errors canonical diff-error reasons, and loop
    tests prove blank/oversized LLM outputs persist in failed-candidate history
    and prompt-visible recent-failure memory.

- [x] Add finite rejected-admission events to database/archive hardening.
  - Status: rejected candidate failure records now have explicit
    rejected-admission persistence semantics for non-finite top-level score
    values: records carrying a rejected archive-admission event normalize the
    failure score and evaluation fitness to JSON-safe `null` sentinels with
    diagnostics before strict history logging.
  - Verification: database tests prove an invalid-evaluation rejected
    candidate with mutated non-finite `fitness` and `metrics.score` persists in
    normal `failure_history.jsonl`; the existing no-admission strict failure
    path remains quarantined in `failure_history_invalid.jsonl`.

- [x] Add detect-secrets baseline hygiene to operational maturity.
  - Status: operational secret-scan validation is repeatable for the current
    staged tree. The baseline was regenerated with the configured
    `detect-secrets` hook detector set, all retained synthetic fixture findings
    were audited as non-secrets, and the regenerated `.secrets.baseline` was
    staged.
  - Verification: `py -3.12 -m pre_commit run detect-secrets --all-files`
    now passes. Documentation and docs tests keep the contributor policy
    explicit: use narrow inline allowlist pragmas where appropriate or stage a
    reviewed `.secrets.baseline` update when intentional synthetic fixtures
    make scanner output drift.

- [x] Add accepted-history id validation to resume hardening.
  - Status: accepted-history restore/query work now has a checked reader
    boundary. `load_accepted_history_index()` validates restored
    `history.jsonl` rows for manifest-safe ids and duplicate accepted ids
    before building an id-indexed map; it rejects repeated ids instead of
    silently repairing or versioning them.
  - Verification: database restore-reader tests cover selected and unselected
    style rows through full-stream validation, identical and divergent
    duplicate ids, unsafe ids, duplicate JSON object names, and restored index
    behavior. README and run-artifact docs document the new reader and keep
    full archive/prompt/controller resume as future work.

- [x] Add durable LLM call telemetry replay/readers to runtime/backend
  hardening.
  - Status: backend/runtime hardening now includes `load_llm_call_ledger()` for
    strict durable `llm_calls.jsonl` replay validation. The reader reconstructs
    call/reward summary metadata while rejecting non-contiguous call sequences,
    duplicate call ids, reward rows for unknown or failed calls, duplicate
    rewards, backend mismatches, malformed digests, unsafe labels, and
    inconsistent scheduler counter vectors.
  - Verification: ensemble replay-reader tests cover successful calls, rewards,
    failed-call reward rejection, retry/accounting counter consistency cases,
    backend range and reward-linkage failures, duplicate JSON names, and
    defensive returned metadata. Full async worker and scheduler-state resume
    remain tracked as separate future work.

- [x] Add manifest and run-database schema versioning to resumability work.
  - Status: current run artifacts now declare local v1 schemas. Startup
    manifests carry `schema_version` and an `artifact_schema` map for current
    JSONL streams, while accepted-history, failure-history, LLM call/reward,
    and prompt-history rows carry `schema_version` plus `record_schema`.
  - Verification: focused database, prompt-database, and LLM ledger tests cover
    current schema markers and legacy/unsupported-schema reader behavior. Docs
    now state that missing markers are legacy v0 rows on supported readers,
    while full schema migration and true resume branching remain future work.

- [x] Add defensive provider-exception formatting to LLM call logging.
  - Status: implemented in `LLMEnsemble.generate()` through
    `_provider_error_text()`. Failed-call telemetry records structured
    `error_type`, bounded/redacted provider-error text, retry/fallback flags,
    and scheduler counts even when a provider exception cannot be stringified.
  - Verification: ensemble tests cover provider exceptions with secret-like
    text, bounded truncation, broken `__str__()`, broken `__repr__()`, and
    continued failed-call accounting with `counts_after`, `will_retry`, and
    `will_fallback` preserved before the original exception is re-raised.

- [x] Add invalid-encoding history diagnostics to future resume loaders.
  - Status: implemented for the checked accepted-history restore/query reader.
    `load_accepted_history_index()` reads `history.jsonl` as bytes, decodes
    each row as UTF-8, and reports invalid bytes as line-numbered
    `Malformed history.jsonl at line N: invalid UTF-8 (...)` diagnostics before
    JSON parsing or index construction.
  - Verification: database restore-reader tests now cover invalid UTF-8 at the
    first row and after a valid accepted-history row, plus the existing JSON
    shape, duplicate-key, schema-version, finite-fitness, safe-id, duplicate-id,
    and metric validation cases.

- [x] Add JSONL append durability to database/resume hardening.
  - Status: defined the managed JSONL local durability policy in README and
    run-artifact docs, then implemented it in the shared append helper used by
    candidate history, failure history, LLM calls, prompt history, plugin
    exports, and quarantine streams. Appends now strict-serialize first,
    write a complete newline-terminated record, flush, fsync, and repair any
    prior unterminated final fragment before the next append.
  - Verification: focused JSONL tests cover fsync and torn-final-line repair
    without losing earlier valid records. The targeted shared-stream suite
    (`test_jsonl`, `test_meta_prompt`, population database tests,
    `test_ensemble`, and `test_ttt_rl`) passed after the helper change.

- [x] Add dotenv/provider-environment precedence to runtime hardening.
  - Status: `libreevolve.cli` no longer loads `.env` at module import, and
    `show` remains history-only. The `run` command loads `.env` during run
    setup with `override=True`, before provider backend preflight, and persists
    non-secret dotenv source metadata under `manifest.provenance.dotenv`.
  - Verification: CLI tests prove importing the CLI and invoking `show` leave
    an existing parent `LIBREEVOLVE_DOTENV_PROBE` unchanged despite a local
    `.env`, while `run` applies the dotenv override and records source path,
    status, hash/byte count, override policy, load phase, scope, and key names
    without secret values. Loop tests prove the dotenv provenance reaches
    `manifest.json`.

- [x] Add explicit ensemble caps for LLM retry/fallback multiplication.
  - Status: added `llm_max_call_attempts` as a validated config, CLI, manifest,
    and `LLMEnsemble` control. `llm_max_retries` still caps same-backend
    retries at `0..10`, while `llm_max_call_attempts` caps total original,
    retry, and fallback attempts per logical ensemble call at `1..32`.
    Telemetry records `attempt_index` and `max_call_attempts` so audit/replay
    can distinguish retry exhaustion from fallback exhaustion.
  - Verification: config, CLI, build-LLM, manifest, and ensemble tests cover
    validation, propagation, manifest persistence, and a failing backend where
    the total-attempt cap suppresses both same-backend retry and fallback.

- [x] Add failure-history replay/query policy for malformed mutation payloads.
  - Status: `load_failure_history_records()` now treats failure history as a
    checked replay/query stream. It validates restored rows for manifest-safe
    failed ids, duplicate failed ids, non-negative generation, safe
    changed-file and file-delta paths, mutation SHA-256 shape,
    mutation-payload text/type consistency, and `failure_fingerprint`
    consistency. Non-text mutation payload rows remain queryable instead of
    being filtered or quarantined solely for being non-text.
  - Policy: restored rows receive `mutation_payload_replay.policy =
    diagnostic_only_do_not_reapply`, making explicit that persisted
    `mutation_text` is a bounded/redacted diagnostic snippet rather than exact
    mutation text for resume-time reapplication.
  - Verification: focused database tests cover valid current rows, non-text
    payload rows, duplicate failed ids, unsafe restored ids, invalid
    generations, non-string mutation diagnostics, malformed payload flags,
    malformed digests, changed-path escapes, fingerprint mismatches, duplicate
    JSON object names, and defensive returned-record copies.

- [x] Add restored/controller finite consumed-budget validation to runtime accounting.
  - Status: future controller budget state now has an explicit schema boundary
    through `validate_controller_budget_state()`. The controller wrapper
    revalidates restored runtime budget snapshots, validates event lists, and
    requires evaluation events to carry finite non-negative elapsed seconds and
    checked evaluator accounting before `apply_controller_budget_event()` can
    mutate active budget counters.
  - Verification: budget tests cover malformed controller state, malformed
    restored consumed counters, malformed elapsed values, malformed evaluator
    accounting, defensive copies, and unchanged counters after invalid events.

- [x] Add restored/controller evaluation-kind validation to runtime budget accounting.
  - Status: controller event kinds are schema-validated before replay.
    `seed_evaluation` and `candidate_evaluation` are separate durable event
    kinds, with generation and stop events validated separately. Restored
    controller states require contiguous event sequences starting at zero.
  - Verification: budget tests cover valid seed/candidate event application,
    invalid event kinds, invalid sequence values, non-contiguous restored
    event sequences, stop-event validation, and malformed-event rejection
    before counter mutation.

- [x] Add parent-aware causal-factor reward attribution to plugin truthfulness.
  - Status: causal plugin reward attribution now uses selected-parent baseline
    metadata from the evolve loop when available, records the baseline score,
    source, and parent id in retained history, and reports the baseline policy
    in run artifact metadata. Direct plugin use can supply `parent_score`, while
    legacy no-baseline calls retain documented previous-history or zero
    fallback behavior.
  - Verification: tests cover unrelated order effects, parent regressions,
    direct metadata parent-score fallback, and evolve-loop propagation of the
    selected parent baseline.

- [x] Add prompt-bearing config retention to manifest hardening.
  - Status: manifest hardening now includes a prompt-config retention policy
    for `prompt_variants`, `prompt_format_options` alternative text,
    `critique_prompt`, and `llm_feedback[].prompt`. Prompt-bearing strings are
    redacted and bounded before manifest persistence, while stable hashes and
    redaction/length metadata preserve attribution.
  - Verification: manifest tests cover direct startup manifests and docs now
    describe the redacted/hash-backed policy instead of raw prompt-config
    persistence.

- [x] Add LLM request-parameter policy to backend roadmap.
  - Status: backend docs, configuration docs, README, run-artifact docs, and
    the paper index now describe validated built-in request parameters for
    temperature, top-p, provider-supported stop sequences, and
    provider-supported request seeds. Call telemetry records normalized
    effective values under `request_parameters`, and replay validation treats
    that field as a strict safe object. The remaining open roadmap item is
    structured prompt-role serialization.
  - Verification: focused backend/config/ensemble tests prove validation,
    provider/API-mode support checks, exact adapter payload forwarding,
    `build_llm()` propagation, defensive telemetry copies, and unsafe telemetry
    redaction.

- [x] Add final LLM scheduler snapshots to runtime-manifest reproducibility.
  - Status: the roadmap/documentation set now describes
    `runtime.llm_scheduler` as the final scheduler-state audit record for
    current runs. The manifest distinguishes real `snapshot` state from
    `not_initialized`, `unavailable`, and `invalid` diagnostics, validates
    snapshots against the `LLMEnsemble` restore contract before trusting them,
    and marks the snapshot as not yet wired into `evolve()` resume.
  - Remaining roadmap gap: full resumed runs still need scheduler-state
    restore wiring, role-specific scheduling policy, and replay tests that
    prove restored backend accounting continues correctly after interruption.
  - Verification: loop tests cover no-mutation-LLM, real `LLMEnsemble`
    snapshot, unavailable custom object, unvalidated custom dict, non-finite
    state, and malformed ensemble-state manifests; README, architecture,
    run-artifact docs, paper index notes, and open TODOs now separate
    implemented snapshot persistence from future restore/resume work.

- [x] Add compact island cursor snapshots to runtime-manifest reproducibility.
  - Status: runtime manifests now expose `runtime.history.archive_state` with
    the island round-robin cursor, archive sequence, migration sequence,
    metric-sampling cursor, archive sequence by program id, and compact
    per-island occupancy/elite counts. The snapshot is explicitly marked as
    not yet restored by resume.
  - Remaining roadmap gap: database resumability still needs restore wiring,
    full archive cell/elite state, migration event replay, and normalization
    state.
  - Verification: focused tests cover `IslandModel.state_snapshot()`,
    `ProgramDatabase.archive_state_snapshot()`, and manifest finalization.

- [x] Add migration event stream to run-artifact reproducibility.
  - Status: scheduled migration now appends versioned placement records to
    `archive_events.jsonl`, and manifests advertise the stream in
    `artifact_schema.jsonl_records`. Runtime artifact pointers include both
    `archive_events.jsonl` and `archive_events_invalid.jsonl`.
  - Remaining roadmap gap: full archive replay still needs cell/elite
    snapshots, descriptor-normalization state, and migration restore semantics.
  - Verification: database tests cover event persistence and schema metadata;
    loop tests cover artifact pointer handling for the new stream.

- [x] Retire stale bearer-header proof from redaction roadmap.
  - Status: runtime safety docs now treat bearer-header redaction as
    implemented in the shared redaction path rather than an active failure.
    Copied evaluator artifacts have a direct regression test for
    `Authorization: Bearer hf_...`, and direct redaction tests cover both
    `hf_...` and `xoxb-...` bearer-header examples.
  - Remaining roadmap gap: runtime redaction still needs a fully specified
    scanner or intentionally narrow contract with false-positive fixtures and
    coverage for quarantine, prompt/history, environment, and path-label
    surfaces.
  - Verification: focused redaction and evaluator tests cover the direct helper
    and default artifact-storage path.

- [x] Add persisted run-local RNG state to the reproducibility roadmap.
  - Status: completed and aborted manifests now expose `runtime.rng` with schema
    `python.random.mt19937.v1`, the configured seed, JSON-safe
    `random.Random.getstate()` state, `state_sha256`, and the
    `random.Random.setstate` restore entrypoint.
  - Remaining roadmap gap: resume still needs to restore the persisted snapshot
    into `evolve()`, define plugin/provider RNG boundaries, and prove replay of
    parent, inspiration, prompt, island, and MAP-Elites sampling.
  - Verification: focused loop tests cover RNG snapshot round-trip and runtime
    manifest persistence for completed and aborted runs.

- [x] Add checked RNG snapshot restore boundary to the reproducibility roadmap.
  - Status: persisted RNG state now has a checked manifest-reader and direct
    restore boundary through `load_runtime_rng_state_snapshot()` and
    `restore_runtime_rng_state_snapshot()`.
  - Remaining roadmap gap: resume still needs to feed the restored RNG into
    `evolve()` and prove deterministic sampling replay.
  - Verification: focused loop tests cover manifest loading, defensive
    validation, missing RNG snapshots, and state-hash mismatch.

- [x] Add checked compact archive-state reader to database resumability work.
  - Status: `load_runtime_archive_state_snapshot()` and
    `validate_archive_state_snapshot()` now validate the compact
    `runtime.history.archive_state` manifest snapshot.
  - Remaining roadmap gap: resume still needs full archive cell/elite snapshots
    and live `IslandModel` cursor restoration.
  - Verification: focused database/island tests cover valid manifest loading,
    defensive copies, missing archive state, invalid island order, and unsafe
    sequence-map ids.

- [x] Add checked migration-event reader to database resumability work.
  - Status: `load_archive_event_records()` now validates `archive_events.jsonl`
    as a checked migration audit stream.
  - Remaining roadmap gap: resume still needs to apply the event stream with
    full archive cell/elite snapshots and live cursor restoration.
  - Verification: focused database tests cover valid rows, duplicate JSON
    names, migration-sequence order, unsafe ids, and malformed cells.

- [x] Add direct compact island-cursor restore to database resumability work.
  - Status: `IslandModel.restore_cursor_state()` now applies compact cursor and
    sequence state from a validated island-state snapshot to a live island
    model.
  - Remaining roadmap gap: full resume still needs MAP-Elites cell/elite
    snapshots, descriptor-normalization state, migration replay, and `evolve()`
    integration.
  - Verification: focused island/database/loop tests cover restored next island
    assignment, sequence continuation, and mismatch rejection.

- [x] Wire compact island cursor restore through ProgramDatabase construction.
  - Status: `ProgramDatabase(..., archive_state_snapshot=...)` now accepts a
    validated `runtime.history.archive_state` snapshot, applies the compact
    cursor/counter subset through `IslandModel.restore_cursor_state()`, and
    records the cursor-only restore status in startup manifests.
  - Remaining roadmap gap: full archive resume still needs MAP-Elites cell and
    elite snapshots, descriptor-normalization state, and migration replay.
  - Verification: focused database tests cover next-island continuation,
    archive-sequence continuation, manifest policy recording, and mismatched
    island-count rejection.

- [x] Add provenance path and Git status Unicode-control policy to roadmap gap.
  - Spec evidence: AlphaEvolve-aligned replay/provenance claims need labels
    that cannot render differently from their stored values.
  - Status: the Unicode roadmap gap now records that source/problem tree paths,
    skipped path diagnostics, plugin module path labels, and Git dirty-status
    entries escape Unicode format controls as `[U+....]` while retaining raw
    comparison hashes.
  - Remaining scoped gap: the roadmap item still needs future durable label
    families to be classified as they are discovered.
  - Verification: focused provenance tests cover path, plugin-path, and Git
    status escaping plus ordinary Unicode preservation.

- [x] Add known-lockfile hash provenance to environment roadmap gap.
  - Roadmap evidence: reproducibility work needed a step beyond direct declared
    dependencies before manifests could support stronger environment claims.
  - Status: environment provenance now records hash-only metadata for known
    project-root lockfiles and documents that the remaining roadmap gap is full
    freeze/transitive/numerical/provider runtime provenance.
  - Verification: focused runtime-environment provenance tests cover lockfile
    hash records, aggregate hash changes, missing and oversized lockfiles, and
    unreadable diagnostics.

- [x] Add installed-package snapshot semantics to environment roadmap gap.
  - Roadmap evidence: environment provenance needed transitive/dev package
    version visibility beyond direct declared dependencies.
  - Status: environment provenance now records bounded installed distribution
    name/version snapshots with a full-record aggregate hash, and roadmap TODOs
    now scope the remaining work to freeze install-source interpretation,
    broader build provenance, numerical runtime metadata, and provider/source
    policy.
  - Verification: focused runtime-environment provenance tests cover snapshot
    inclusion, version-change hash movement, sanitization, cap behavior, and
    metadata-inspection failures.

- [x] Add explicit sample aggregation and per-metric stage pass policies to
  evaluation roadmap.
  - Evidence: configured stages needed explicit pass semantics for
    multi-sample, metric-specific, artifact, and output-dependent evaluation
    cascades rather than relying on a single primary-fitness threshold and
    implicit numeric means.
  - Status: stage policy now covers per-metric thresholds, aggregation
    policies, quantiles, retained-output requirements, artifact-count
    requirements, retained-output scalar equality checks, and copied artifact
    glob requirements. Docs now state the deliberate custom-code boundary:
    arbitrary task-specific predicates belong in validators, while stage config
    remains a manifest-safe policy layer.
  - Verification: focused config/evaluator tests cover stage policy validation,
    metric thresholds, aggregation policies, output/artifact checks, retries,
    configured-stage metadata, and pass/fail diagnostics.

- [x] Extend Unicode format-control label policy beyond run/candidate paths.
  - Evidence: the roadmap gap needed a consistent reject/escape/hash policy for
    durable labels beyond initial run names and candidate paths.
  - Status: the protected label set now covers metrics, evaluator stages,
    plugin aliases, feedback labels, artifact/context selectors, plugin and
    run-artifact metadata, prompt-program metadata, `Program` metadata and
    evaluation values, provider response metadata, source/problem tree
    provenance paths, skipped path diagnostics, plugin module path labels, Git
    dirty-status entries, evaluator `validate_path` displays, evaluator source
    provenance paths, and `pyproject.toml` dependency specs.
  - Verification: focused provenance and config tests cover ordinary Unicode
    preservation plus U+202E/zero-width-format rejection or escaping across the
    protected persisted-label families.

- [x] Add explicit hidden-file policy to seed workspace fidelity.
  - Evidence: full-codebase candidate support needs visible load-time
    inclusion/exclusion rules for project files that can affect build,
    packaging, validation, or generated artifacts.
  - Status: seed workspace loading now documents and persists a
    secret-safe-by-default hidden/cache policy. `seed_policy.yaml` can include
    selected dot-prefixed or `__pycache__` seed paths, exclude paths with
    precedence, and preserve allowed reserved paths through candidate
    workspaces, mutation, history, and manifest provenance.
  - Verification: focused tests cover dotfile and cache inclusion, exclusion
    precedence, broad include safety, run-manifest persistence, and CLI show
    reconstruction for history rows containing reserved seed paths.

- [x] Add semantic channel requirements for configured prompt seeds.
  - Evidence: AlphaEvolve-style prompt customization should preserve the core
    code-edit contract unless a run deliberately opts into a minimal or
    externally managed template.
  - Status: configured prompt seeds now use
    `prompt_variant_semantic_policy: alphaevolve` by default, requiring task,
    parent code/workspace, mutation instructions, evaluator feedback, and
    context/inspiration channels. Minimal templates require explicit
    `prompt_variant_semantic_policy: compatibility`, and the effective policy
    is recorded in manifests.
  - Verification: focused tests cover faithful default templates, rejected
    task-only templates, explicit compatibility mode, prompt-database seeding,
    and loop/runtime manifest behavior.

- [x] Add LLM prompt-role policy to backend roadmap.
  - Evidence: AlphaEvolve's prompt template/configuration and LLM choice are
    experiment inputs, so provider message boundaries need to be explicit
    runtime policy rather than implicit adapter behavior.
  - Status: backend roadmap docs now describe `llm_prompt_roles` as a
    run-level role-message policy. Configured roles add bounded
    system/developer instructions to OpenAI, Anthropic, and Ollama payloads in
    provider-supported forms; omitted roles preserve the default single-user
    prompt boundary. Manifests retain redacted/hash-backed configured
    instructions, and call telemetry stores prompt-role hashes, character
    counts, message roles, and matched role.
  - Verification: focused config, backend, ensemble, and database tests cover
    validation, provider payload serialization for mutation/critique/feedback/
    meta-prompt roles, hash-only telemetry, build-time revalidation, and
    manifest retention.

- [x] Add explicit redaction-grammar coverage to runtime safety work.
  - Evidence: runtime safety claims for artifacts, diagnostics, prompt/config
    retention, and quarantine records needed an explicit "redacted" contract
    rather than an implicit helper implementation.
  - Status: the active grammar is now `libreevolve.redaction.v2`, exported by
    `redaction_policy_record()` and persisted under
    `manifest.json.policies.redaction`. It is documented as a bounded ordered
    regex grammar covering PEM private keys, secret-like assignments, bearer
    headers, URL userinfo passwords, common provider token prefixes, and AWS
    access-key ids, with explicit caveats for binary/raw surfaces and arbitrary
    private data outside those patterns.
  - Verification: focused redaction and database tests cover rule export,
    provider/environment/path-like fixtures, false positives, and manifest
    policy persistence.

- [x] Decide remaining non-archive whole-history validation semantics for
  `show`.
  - Evidence: run inspection is becoming a primary way to audit history,
    archive diagnostics, and artifact truthfulness.
  - Status: resolved in favor of whole-history validation for source/workspace
    display payloads. `libreevolve show` validates generation, legacy source,
    workspace files, and primary-file payloads for every streamed history row,
    while still printing source content only for the selected best row.
  - Verification: CLI tests cover malformed unselected current and legacy
    source/workspace payloads.

- [x] Add Appendix B constructive-math coverage matrix to benchmark roadmap.
  - Evidence: ROADMAP calls for constructive math benchmarks, but AlphaEvolve
    Appendix B is a concrete set of families rather than an undifferentiated
    category.
  - Status: added a versioned Appendix B registry under
    `libreevolve/problems/benchmarks/` and wired it into paper-manifest
    validation. Each family now has implemented/planned/background/out-of-scope
    status, objective metric/direction, target-baseline status,
    construction/certificate artifact shape, certification need, rationale,
    fixture mapping when present, and AlphaEvolve citation metadata.
  - Verification: registry tests check exact family coverage and fixture
    honesty.

- [x] Add proposal-batch throughput to async/runtime roadmap work.
  - Evidence: the roadmap tracks a future async controller with LLM samplers
    and evaluator workers, and AlphaEvolve-scale sampling needs more than one
    candidate proposal per generation.
  - Status: ROADMAP now distinguishes the implemented sequential
    `proposals_per_generation` batch path from the still-missing concurrent
    proposal/evaluation queues. The runtime now persists sibling-candidate
    accounting in history rows and manifest config, while keeping migration and
    generation completion once per generation.
  - Remaining gap: bounded async queues, parallel evaluator workers, and
    distributed throughput remain open paper-level work.
  - Verification: focused loop tests prove a one-generation batch writes
    multiple generated candidate history rows with per-proposal metadata and
    coherent generation counters.

- [x] Wire persisted run-local RNG snapshots into direct `evolve()` replay.
  - Evidence: reproducible AlphaEvolve-style runs should be able to restore the
    framework RNG without using process-global Python randomness.
  - Status: direct callers can now pass a checked
    `runtime_rng_state_snapshot` to `evolve()`. The restore happens before run
    setup, mismatched seeds fail before manifest writes, and final manifests
    distinguish fresh seeded snapshots from restored RNG snapshots.
  - Remaining roadmap gap: full archive/controller resume, plugin/provider RNG
    policies, and replay tests across parent, inspiration, prompt, island, and
    MAP-Elites choices remain open.
  - Verification: focused loop tests cover restored and mismatched snapshots.

- [x] Add named AlphaEvolve ablation variants to benchmark roadmap work.
  - Evidence: AlphaEvolve Section 4/Figure 8 uses specific component-disabled
    variants before reporting equal-budget curves.
  - Status: ROADMAP now distinguishes the validated
    `alphaevolve_ablations.json` report contract from still-missing executed
    ablation reports. The registry defines full system, `No evolution`, `No
    context in the prompt`, `No meta prompt evolution`, `No full-file
    evolution`, and `Small base LLM only`, including component-disable
    assertions and three-seed/target/budget-fraction reporting semantics.
  - Remaining roadmap gap: running these variants, enforcing every assertion at
    runtime, and producing mean/variance curves remain open.
  - Verification: focused registry tests cover exact variant enumeration and
    report-contract validation.

- [x] Move MAP-Elites workspace-aware descriptors out of roadmap future work.
  - Evidence: the multi-objective roadmap previously tracked descriptors that
    only used the primary-file compatibility view, which was inconsistent with
    workspace/codebase candidates.
  - Status: local MAP-Elites complexity and diversity descriptor inputs now
    use a deterministic serialized full-workspace text view, including
    supporting files. ROADMAP now keeps only stable descriptor normalization,
    evaluator-provided behavior descriptors, and archive diagnostics as open
    follow-up work.
  - Remaining roadmap gap: stable bounds/rebinning, user/evaluator behavior
    descriptors, and richer archive diagnostics remain open.
  - Verification: focused MAP-Elites tests cover support-file descriptor
    effects.

- [x] Narrow MAP-Elites normalization roadmap work to the adaptive diversity model.
  - Evidence: the roadmap tracked descriptor normalization generally, while
    complexity normalization was still using an archive-history-dependent
    denominator.
  - Status: complexity normalization now has a fixed configured bound,
    `map_elites_complexity_max_chars`, persisted in manifests. ROADMAP now
    names the remaining adaptive diversity descriptor and behavior-descriptor
    model work instead of treating all descriptor normalization as open.
  - Remaining roadmap gap: evaluator-provided descriptors, a fixed diversity
    descriptor model, or explicit rebin/snapshot semantics.
  - Verification: focused tests cover config validation, island propagation,
    manifest persistence, and MAP-Elites clamping.

- [x] Expose provider-internal retry controls for bundled LLM adapters.
  - Evidence: backend-scheduling roadmap work needs provider attempts to be
    bounded and inspectable before they can be unified with larger runtime
    budgets.
  - Status: built-in backend specs now accept `provider_max_retries`, and
    `llm_calls.jsonl` call rows can carry validated `adapter_retry` telemetry
    for provider attempt counts and safe exception type labels.
  - Remaining roadmap gap: role-specific retry budgets, token/cost/time budget
    coupling, and restored retry-budget consumption remain open.
  - Verification: focused backend, ensemble, and config tests passed for this
    slice.

- [x] Move provider failure classification out of roadmap future work.
  - Evidence: ROADMAP previously grouped timeout/rate-limit classification with
    future role-specific provider-failure policy.
  - Status: LLM call telemetry now records normalized provider failure
    categories for timeout, rate limit, transport, provider status,
    provider-response, and unknown failures. ROADMAP now keeps the remaining
    open work on role-specific quarantine/penalty policy.
  - Remaining roadmap gap: categories are not budget-affecting and do not
    decide role-specific quarantine behavior.
  - Verification: focused ensemble tests cover the classification contract.

- [x] Add DeepResearch cache snapshot artifact summaries to plugin provenance.
  - Evidence: plugin extensibility and retrieval roadmap work needs emitted
    retrieval artifacts to be attributable in manifests, not only present in
    the generic `plugin_artifacts/` tree hash.
  - Status: cache-backed `DeepResearchPlugin` instances now expose snapshot
    file count, retained count, skipped/read-error counts, byte counts,
    per-file hashes, retention cap, and aggregate hash through plugin artifact
    metadata.
  - Remaining roadmap gap: audit-grade retrieval still needs full provider or
    source payload persistence, ranked-source provenance, and source-content
    trust policy.
  - Verification: focused DeepResearch plugin and loop tests cover the
    artifact-summary contract.

- [x] Attribute modular prompt guidance as a static strategy policy.
  - Evidence: plugin-extensibility roadmap work needs prompt-context strategy
    choices to be auditable without overclaiming paper behavior.
  - Status: `ModularPlugin` now emits prompt-context metadata that labels the
    guidance as static prompt-only, names `static_modular_guidance`, lists the
    described operations, and records that no operation was executed or
    interface enforced.
  - Remaining roadmap gap: real plugin version/config attribution and executed
    generate/improve/perturb operation policy remain open.
  - Verification: focused modular plugin and loop tests passed for this slice.

- [x] Move logical LLM-call caps out of the runtime-budget roadmap gap.
  - Evidence: the roadmap grouped LLM-call budgets with remaining token, cost,
    provider-attempt, accelerator, and async queue accounting.
  - Status: ROADMAP now treats logical LLM-call stop reasons as implemented
    local run-budget accounting through `max_llm_calls`.
  - Remaining roadmap gap: token/cost/provider-attempt budgets, accelerator
    resources, async queue accounting, and equal-budget reporting remain open.
  - Verification: focused budget/config/loop/CLI tests cover the implemented
    logical-call cap.

- [x] Move restored backend-spec validation out of backend-hardening roadmap
  future work.
  - Evidence: backend hardening tracked restored backend specs as a possible
    bypass around live `Config` and `build_llm()` validation.
  - Status: `validate_restored_backend_specs()` now gives future replay/resume
    code a checked restored-spec entrypoint backed by the same backend
    normalizer as live LLM construction.
  - Remaining roadmap gap: oversized/secret-like prompt policy remains open.
  - Verification: focused ensemble tests cover valid restored specs, defensive
    copies, and malformed restored model/token/retry/custom/OpenAI fields.

- [x] Move restored prompt validation out of backend-hardening roadmap future
  work.
  - Evidence: backend hardening tracked restored prompt payloads as a possible
    bypass around live ensemble prompt validation.
  - Status: `validate_restored_llm_prompt()` now gives future replay/resume
    code a checked restored-prompt entrypoint backed by the same non-empty text
    validator as live calls.
  - Remaining roadmap gap: oversized/secret-like prompt policy remains open.
  - Verification: focused ensemble tests cover valid restored prompts plus
    malformed non-string and blank prompts.

- [x] Add backend-registry validation to backend hardening.
  - Evidence: backend hardening still treated registry-created backend specs as
    future bypass surfaces after restored backend specs were covered.
  - Status: `libreevolve.llm.backend_registry` now validates registry-created
    backend specs through the shared backend normalizer and constructs built-in
    or custom backend objects from validated specs.
  - Remaining roadmap gap: oversized/secret-like prompt policy remains open.
  - Verification: focused ensemble tests cover registry validation and
    registry-created custom backend construction.

- [x] Add NumPy numerical-runtime metadata to environment provenance.
  - Evidence: roadmap environment provenance still lacked numerical-runtime
    metadata after package and lockfile snapshots were added.
  - Status: runtime environment provenance now records NumPy availability,
    version, bounded/redacted `show_config()` preview, and full config hash.
  - Remaining roadmap gap: freeze install-source interpretation, wheel/build
    tags, accelerator budget/accounting metadata, and package-source redaction
    policy remain open.
  - Verification: focused provenance tests cover successful capture,
    redaction, truncation, unavailable NumPy, and config-capture errors.

- [x] Add selected PEP 621 metadata to environment provenance.
  - Evidence: roadmap environment provenance still scoped project metadata to
    name/version/requires-python and build metadata.
  - Status: runtime environment provenance now records license,
    authors/maintainers, classifiers, project URLs, optional dependency
    groups, scripts, and gui-scripts with bounded/redacted/hash-backed fields.
  - Remaining roadmap gap: freeze install-source interpretation, wheel/build
    tags, accelerator budget/accounting metadata, non-project build metadata
    policy, and package-source redaction remain open.
  - Verification: focused provenance tests cover the expanded metadata schema.

- [x] Add keyword and arbitrary entry-point metadata to roadmap provenance.
  - Evidence: roadmap environment provenance still listed keyword and arbitrary
    entry-point metadata as uncaptured after selected PEP 621 metadata work.
  - Status: roadmap TODOs now treat PEP 621 `keywords` and arbitrary
    `[project.entry-points]` groups as implemented bounded/redacted package
    provenance.
  - Remaining roadmap gap: freeze install-source interpretation, wheel/build
    tags, accelerator budget/accounting metadata, non-project build metadata
    policy, and package-source redaction remain open.
  - Verification: focused provenance tests cover keyword and entry-point
    capture.

- [x] Narrow plugin extensibility roadmap to custom/entry-point provenance.
  - Evidence: roadmap plugin work still listed moving registration out of the
    hard-coded CLI registry and allowing config-file plugin options after those
    built-in paths were implemented.
  - Status: ROADMAP now treats built-in plugin registry/config schemas and
    constructor spec capture as current behavior, and scopes remaining roadmap
    work to custom/entry-point discovery, package/version attribution, richer
    custom schema policy, and stronger strategy/artifact provenance.
  - Remaining roadmap gap: custom plugin discovery and versioned provenance
    remain open.
  - Verification: focused config, CLI, and loop tests cover the implemented
    registry/config path.

- [x] Narrow backend runtime timeout roadmap to remaining-budget cancellation.
  - Evidence: roadmap TODOs still described all LLM backend calls as
    unbounded synchronous calls after built-in provider request timeouts.
  - Status: `llm_call_timeout_sec` now provides an ensemble-level backend
    attempt deadline for built-in and custom backends, with structured timeout
    telemetry and retry/fallback eligibility.
  - Remaining roadmap gap: pass remaining run deadlines into provider calls,
    define hard/soft cancellation semantics, and make timeout policy affect
    budgets/quarantine.
  - Verification: focused ensemble, config, and CLI tests cover the
    implemented timeout boundary.

- [x] Add `pip freeze` evidence to environment-provenance roadmap.
  - Evidence: roadmap runtime work still described environment provenance as
    bounded package/version only after lockfile and installed-distribution
    snapshots.
  - Status: ROADMAP and roadmap TODOs now treat bounded/redacted
    `pip_freeze` capture with a raw stdout hash as implemented environment
    evidence.
  - Remaining roadmap gap: broader build provenance,
    accelerator budget/accounting state, non-project build metadata policy,
    private package-source interpretation policy, live provider service/API
    versions, and provider cost or remote provider-side default capture remain open.
  - Verification: focused provenance tests cover freeze capture and degraded
    statuses.

- [x] Add installed-distribution `WHEEL` evidence to environment-provenance
  roadmap.
  - Evidence: roadmap runtime work still listed all wheel/build tag metadata as
    missing after bounded `pip_freeze` capture.
  - Status: ROADMAP-adjacent roadmap TODOs and README/run-artifact docs now
    treat bounded parsed installed-distribution `WHEEL` metadata as
    implemented environment evidence.
  - Remaining roadmap gap: broader build provenance beyond installed `WHEEL`
    metadata, accelerator budget/accounting state, non-project build metadata
    policy, private package-source interpretation policy, live provider
    service/API versions, and provider cost or remote provider-side default capture remain
    open.
  - Verification: focused provenance tests cover wheel metadata capture, tag
    and raw metadata size bounds, redaction, missing metadata, and degraded
    read-error statuses.

- [x] Add built-in LLM provider SDK evidence to environment-provenance roadmap.
  - Evidence: roadmap runtime work still listed provider/API versions as wholly
    missing after freeze and wheel metadata capture.
  - Status: roadmap TODOs and user docs now treat built-in OpenAI, Anthropic,
    and Ollama SDK package versions plus adapter module/API-mode labels as
    implemented environment evidence.
  - Remaining roadmap gap: live provider service/API versions, provider
    cost or remote provider-side default capture, provider-side authentication state, and
    nondeterminism/replay boundaries remain open.
  - Verification: focused provenance tests cover installed SDK records,
    hash movement when versions change, missing package statuses, redacted
    lookup errors, and unsafe version-label escaping.

- [x] Add bounded extra `[project]` metadata evidence to environment roadmap.
  - Evidence: roadmap environment work still listed arbitrary project metadata
    capture as open after selected PEP 621 metadata, freeze, wheel, and SDK
    provenance work.
  - Status: roadmap TODOs and user docs now treat bounded
    `extra_project_metadata` for unselected or unknown `[project]` keys as
    implemented environment evidence.
  - Remaining roadmap gap: broader non-project build provenance,
    install-source interpretation, accelerator budget/accounting state, live
    provider service/API versions, provider cost or remote provider-side default capture, and
    private package-source policy remain open.
  - Verification: focused provenance tests cover extra metadata capture,
    nested tables/lists, bounds, redaction, unsafe character escaping, and hash
    movement when extra metadata changes.

- [x] Add run-local RNG restore to reproducibility roadmap work.
  - Evidence: the roadmap previously treated RNG capture as separate from
    restored framework-owned RNG state.
  - Status: ROADMAP and user docs now state that final manifests persist
    `runtime.rng`, direct `evolve()` callers can restore a validated snapshot,
    and CLI runs can load the same checked state with
    `--restore-rng-from-manifest`.
  - Remaining roadmap gap: this remains framework-RNG-only; full
    archive/controller resume, plugin/provider RNG boundaries, lineage replay,
    and provider nondeterminism policy are still open.
  - Verification: focused CLI tests cover valid manifest restore wiring and
    seed-mismatch rejection before run-directory preparation.

- [x] Add oversized and registry backend prompt policy to backend hardening.
  - Evidence: roadmap/backend hardening still lacked an explicit oversized and
    secret-like prompt policy for registry-created/custom backend calls.
  - Status: `LLMEnsemble` now accepts an optional `max_prompt_chars`, rejects
    oversized prompts before scheduler/call-history/backend mutation, wires
    `Config.prompt_max_chars` into config-created ensembles, and documents that
    secret-like prompt text is allowed as private input but retained only as
    length/hash in LLM telemetry.
  - Remaining roadmap gap: token-aware prompt packing, role-specific prompt
    retention policy, and direct custom-backend calls outside `LLMEnsemble`
    remain separate work.
  - Verification: focused ensemble tests cover cap validation, build wiring,
    oversized prompt rejection, restored prompt validation, and hash-only
    secret-like prompt telemetry.

- [x] Propagate remaining runtime budget into LLM ensemble deadlines.
  - Evidence: backend runtime work still listed remaining-run-deadline
    propagation as missing after provider request timeouts and
    `llm_call_timeout_sec`.
  - Status: `RunBudget.remaining_runtime_seconds()` and `_generate_with_budget()`
    now clamp deadline-aware `LLMEnsemble` attempts to the remaining
    `max_runtime_seconds` budget, while preserving shorter configured
    `llm_call_timeout_sec` values and restoring the ensemble setting after
    each call.
  - Remaining roadmap gap: hard provider cancellation, role-specific timeout
    artifacts, timeout-driven stop/quarantine policy, and token/cost budget
    coupling remain open.
  - Verification: focused loop/budget tests cover runtime-budget clamping and
    configured timeout precedence; ensemble timeout tests still cover
    structured timeout telemetry and fallback.

- [x] Add plugin version labels to runtime plugin identity evidence.
  - Evidence: roadmap/plugin provenance work still lacked explicit version
    attribution for plugin identities that influence prompts and run artifacts.
  - Status: shared plugin identity records now include sanitized version
    metadata from plugin instance, class, or module `__version__` attributes
    when present, and the record flows into manifests and generated-candidate
    plugin-context metadata.
  - Remaining roadmap gap: custom plugin package registry provenance,
    constructor schema introspection, and real selected plugin strategy
    execution remain open.
  - Verification: focused provenance and loop tests cover missing, present,
    source-priority, secret-redacted, and prompt-context-propagated plugin
    version records.

- [x] Add bounded accelerator runtime evidence to environment roadmap.
  - Evidence: roadmap environment provenance still listed accelerator metadata
    as absent after package, lockfile, pip, NumPy, wheel, provider SDK, and
    project metadata evidence landed.
  - Status: runtime environment provenance now records bounded accelerator
    environment hints and degraded `nvidia-smi`/`rocm-smi` driver probe
    records under `accelerator_runtime`, and roadmap TODOs scope remaining
    accelerator work to budget/accounting semantics.
  - Remaining roadmap gap: complete install-source interpretation, broader
    build provenance, live provider service/API-version capture, provider
    cost or remote provider-side default capture, private package-source semantics, and
    accelerator budget accounting remain open.
  - Verification: focused provenance tests cover redacted environment hints,
    successful probes, missing executables, and redacted probe errors.

- [x] Add local adapter defaults to provider telemetry roadmap.
  - Evidence: roadmap/provider TODOs still grouped all provider default
    parameters with missing cost accounting after request-parameter telemetry
    had landed.
  - Status: built-in backend call telemetry now records validated
    `backend_defaults` for local output-token caps, provider internal retry
    caps, configured request timeouts, API modes, and OpenAI
    reasoning/API-mode policy.
  - Remaining roadmap gap: remote provider-side SDK defaults, provider cost
    accounting, token/cost budget-stop policy, and restored retry/budget
    consumption remain open.
  - Verification: focused backend and ensemble tests cover default recording,
    redaction, defensive copies, and replay validation.

- [x] Add configurable reward-accounted roles to the LLM accounting roadmap.
  - Evidence: roadmap and TODO text still described role accounting as
    mutation-only reward semantics rather than a configurable reward-accounted
    role policy.
  - Status: `llm_reward_accounted_roles` now defines which call roles advance
    ensemble scheduler counts and can receive rewards, while runtime
    accounting records the configured role list and
    `reward_accounting_policy`.
  - Remaining roadmap gap: per-role scheduler state, quota accounting,
    restored budget consumption, token/cost/time budget coupling, and
    role-specific retry/quarantine policy remain open.
  - Verification: focused config, ensemble, loop, and docs checks cover the
    new roadmap status.

- [x] Add auxiliary LLM failure isolation to backend/runtime roadmap.
  - Evidence: provider-failure roadmap text did not distinguish mutation
    failures from auxiliary critique/meta-prompt failures after useful
    candidate work had already completed.
  - Status: critique provider failures now fall back to the original mutation
    with bounded failure metadata, and meta-prompt provider failures now write
    rejected prompt-mutation records instead of aborting logged candidates.
  - Remaining roadmap gap: mutation-call quarantine, provider penalties,
    token/cost budget stops, role-specific retry/quarantine policy, and unified
    adapter/ensemble retry consumption remain open.
  - Verification: focused loop tests cover the new failure-isolation behavior.

- [x] Narrow the metric-policy roadmap gap for feedback objective metrics.
  - Evidence: roadmap/TODO text still treated feedback metrics as reviewer-side
    scores that could not enter declared objective-schema archive selection.
  - Status: declared metrics now have evaluator or feedback source labels.
    Feedback-sourced objective metrics are declared in the problem schema,
    omitted from validator output requirements, filled only by
    `objective_metric: true` graders, and included in normalized
    `selection_score` once present.
  - Remaining roadmap gap: the multi-objective policy still needs
    configurable weights/targets, Pareto/frontier behavior, metric-specific
    elite archives, and prompt-selection policies beyond the current scalar.
  - Verification: focused loop coverage proves a feedback-filled objective
    metric changes child normalized metrics, selection score, and archive
    admission score.

- [x] Add systems held-out/reference report contract to roadmap benchmark
      requirements.
  - Evidence: roadmap benchmark TODOs required future systems fixtures but did
    not require the AlphaEvolve Section 3.3 split between loop optimization,
    held-out/generalization checks, and randomized/reference-correctness
    evidence.
  - Status: roadmap TODOs now point to `libreevolve.systems_result_report.v1`
    as the report contract for named optimization, held-out, and
    reference-correctness gates with case-set hashes, sample counts/seeds,
    finite metrics, artifacts, and `alphaevolve_ready` gating.
  - Remaining roadmap gap: real compiler, hardware, kernel, scheduling, or
    systems fixtures still need to emit this evidence from actual held-out or
    randomized reference checks.
  - Verification: focused systems-result tests cover the report contract and
    readiness gate.

- [x] Add anti-gaming hardening report contract to roadmap benchmark
      requirements.
  - Evidence: roadmap benchmark TODOs required negative anti-gaming fixtures
    for advertised AlphaEvolve-style benchmarks but lacked a reusable report
    shape for protected signals, shortcut threats, detectors, and fixture
    results.
  - Status: roadmap TODOs now point to `libreevolve.benchmark_hardening.v1` as
    the hardening report contract. Benchmark-level records must include passed
    negative fixtures for every declared shortcut threat.
  - Remaining roadmap gap: real representative benchmark fixtures still need
    to emit the hardening reports from actual randomized/exhaustive validators
    and anti-gaming fixtures.
  - Verification: focused hardening tests cover the report contract and
    benchmark-readiness gate.

- [x] Add LLM role/retry budget report contract to roadmap budget work.
  - Evidence: roadmap budget TODOs required role-specific retry budgets,
    provider-adapter retry accounting, token/cost/time coupling, and
    persisted/restored retry consumption, but there was no paper-facing report
    shape for those fields.
  - Status: roadmap TODOs now point to `libreevolve.llm_budget_report.v1` as
    the audit contract for per-role logical-call, retry-attempt,
    adapter-attempt, token, cost, wall-clock, provider retry, and resume-state
    evidence.
  - Remaining roadmap gap: runtime enforcement and restored retry consumption
    still need to be connected to this report contract.
  - Verification: focused LLM budget report tests cover the report contract
    and paper-budget readiness gate.

- [x] Add provider timeout/cancellation policy contract to roadmap runtime
      work.
  - Evidence: roadmap timeout TODOs required hard/soft cancellation semantics,
    timeout/cancellation budget actions, and persisted timeout artifacts, but
    had no reusable report shape for those policies.
  - Status: roadmap TODOs now point to
    `libreevolve.provider_cancellation_policy.v1` as the policy contract for
    timeout/cancellation rules, role-scoped budget actions, artifacts, and
    hard-cancel readiness.
  - Remaining roadmap gap: live provider SDK cancellation and
    timeout-driven stop/quarantine enforcement still need runtime wiring.
  - Verification: focused cancellation-policy tests cover the report contract
    and hard-cancel readiness gate.

- [x] Add shipped-example scope contract to roadmap benchmark work.
  - Evidence: roadmap benchmark TODOs needed explicit anti-gaming and
    representative-benchmark criteria, but shipped examples could still be
    mistaken for AlphaEvolve-comparable benchmark coverage.
  - Status: `libreevolve.example_benchmark_scope.v1` now validates a
    smoke-only/non-comparable registry for `hello_world`, `sorting`,
    `workspace_math`, `matrix_multiplication`, and `circle_packing`, including
    explicit current roles and upgrade requirements.
  - Remaining roadmap gap: future representative benchmark fixtures still need
    to emit real hardening reports, repeated-seed result artifacts,
    held-out/generalization evidence, and paper-claim certification.
  - Verification: focused example-scope tests cover the contract and
    benchmark-boundary gating.

- [x] Add retrieval transport policy classification to roadmap provenance
      work.
  - Evidence: roadmap TODOs required redirect, failure, and TLS/certificate
    policy for retrieval context before DeepEvolve-style retrieval can be
    treated as audit-grade.
  - Status: `libreevolve.retrieval_transport_policy.v1` now appears on
    DeepResearch retrieval events with a query and classifies HTTPS request
    state, redirects, HTTP status class, payload hash presence, oversized
    responses, missing custom-provider transport, and TLS/certificate-looking
    failures.
  - Remaining roadmap gap: retrieval still needs replayable source-content or
    bounded provider-payload snapshots, richer ranking scores/selection
    rationale, and a replayable transport decision tree.
  - Verification: focused DeepResearch tests cover the policy classification
    paths.

- [x] Add validated migration replay boundary to archive resume roadmap work.
  - Evidence: roadmap resume TODOs required migration replay semantics instead
    of only cursor/cell restore claims.
  - Status: `libreevolve.island_migration_replay_policy.v1` is now persisted in
    archive-state snapshots and validated by both island and database restore
    paths. It records that migration events are not replayed as a restore
    engine and that `archive_contents` restore covers current placements.
  - Remaining roadmap gap: migration event-order replay and controller/pending
    work state still need one-command resumed trace support.
  - Verification: focused population restore tests cover policy propagation and
    overclaim rejection.

- [x] Add retained provider retry evidence to roadmap LLM budget reports.
  - Evidence: roadmap LLM budget work required provider-adapter retry
    accounting to be visible by role, not only as aggregate scheduler counters.
  - Status: runtime `libreevolve.llm_budget_report.v1` instances now attach
    retained per-call provider retry details to each matching role usage row
    when bounded LLM call history still contains those records.
  - Remaining roadmap gap: live token/cost/time budget stops and restored retry
    budget consumption still need runtime wiring.
  - Verification: focused loop and budget-report tests cover retained provider
    retry details in a self-validated runtime report.

- [x] Add installed-distribution source metadata to environment roadmap work.
  - Evidence: roadmap reproducibility work still needed stronger package-source
    provenance beyond lockfile hashes, `pip freeze`, and wheel tags.
  - Status: installed package provenance now records bounded `direct_url.json`,
    `INSTALLER`, and `RECORD` metadata with redaction, raw hashes, hash-only
    source objects, and degraded statuses.
  - Remaining roadmap gap: complete private-index/source resolution, package
    artifact verification, and broader build provenance remain open.
  - Verification: focused provenance tests cover the source metadata record and
    package-source policy retention summary.

- [x] Add run-artifact objective-vector diagnostics to multi-objective roadmap work.
  - Evidence: ROADMAP asked for metric-vector archive diagnostics in run
    artifacts and `show`, but archive admission evidence still exposed only the
    scalar `selection_score`.
  - Status: run artifacts now expose objective-vector audit records on archive
    admissions and migration rows when normalized metrics are available, and
    `show` validates current-history objective vectors while streaming and
    prints bounded selected-row objective metrics.
  - Remaining roadmap gap: Pareto/frontier archive replacement and
    plugin-objective integration remain open.
  - Verification: focused loop/database/island tests cover objective-vector
    emission and validation; focused CLI tests cover `show` display, bounded
    large-vector summaries, and malformed unselected objective-vector rejection.

- [x] Add configured feedback-role rewards to LLM scheduler roadmap evidence.
  - Evidence: roadmap LLM budget/accounting work tracks reward-accounted roles,
    but feedback grader outcomes still lacked a concrete scheduler reward
    signal.
  - Status: successful feedback grader calls now emit `scheduler_reward`
    metadata and apply the normalized feedback score through
    `LLMEnsemble.record_reward()` when the exact `feedback:<name>` role is
    configured as reward-accounted.
  - Remaining roadmap gap: independent per-role routing, role quotas, token/cost
    budget enforcement, and restored retry-budget consumption remain open.
  - Verification: focused feedback tests cover configured feedback-role rewards
    and telemetry-only default feedback roles.

- [x] Add active DeepResearch context hash links to retrieval roadmap evidence.
  - Evidence: roadmap retrieval work needed prompt-context provenance that
    identifies the exact retrieval event behind prompt-visible external
    context.
  - Status: `active_context` now uses
    `libreevolve.deep_research_active_context.v1` and records event index,
    synthesis/raw-result hashes, query hash, cache fields, retained-source
    ranking hash fields, and transport-policy status.
  - Remaining roadmap gap: full source-content/provider-payload artifacts,
    semantic ranking scores, and replayable transport/failure decisions remain
    open.
  - Verification: focused DeepResearch and loop tests cover the active-context
    hash links and secret-safe raw request URL omission.

- [x] Add bounded source-content snapshots to retrieval roadmap evidence.
  - Evidence: roadmap retrieval work needed source-content artifacts beyond
    source labels and hashes.
  - Status: retained DeepResearch source rows now include
    `libreevolve.retrieval_source_content_snapshot.v1` snapshots with
    bounded/redacted text, raw/stored hashes, count metadata, and
    redaction/truncation flags when source summary/content text is available.
  - Remaining roadmap gap: full provider payload artifacts, semantic ranking
    scores, source-content trust verification, and replayable transport/failure
    decisions remain open.
  - Verification: focused DeepResearch and loop tests cover source snapshots
    and history redaction.

- [x] Add query-overlap source relevance scores to retrieval roadmap evidence.
  - Evidence: roadmap retrieval work needed ranked-source rationale beyond
    provider order.
  - Status: retained DeepResearch source rows now include
    `query_term_overlap_audit_v1` relevance records, and `source_ranking`
    hashes those records while keeping provider-order retention explicit.
  - Remaining roadmap gap: learned/external semantic ranking, full provider
    payload artifacts, source-content trust verification, and replayable
    transport/failure decisions remain open.
  - Verification: focused DeepResearch and loop tests cover relevance scores
    and active-context score hashes.

- [x] Add task/context query grounding to retrieval roadmap evidence.
  - Evidence: roadmap retrieval work needed problem-context grounding beyond
    best-code and metric terms.
  - Status: DeepResearch query inputs now include bounded task-description and
    explicit-context terms, with counts and a context hash, and the real
    `evolve()` path wires `Problem` task/context data into the plugin through
    `ProgramDatabase`.
  - Remaining roadmap gap: failure-history, local-paper-corpus, and hypothesis
    query grounding remain open.
  - Verification: focused DeepResearch and loop tests cover task/context query
    terms and persisted metadata.

- [x] Add recent-failure query grounding to retrieval roadmap evidence.
  - Evidence: roadmap retrieval work needed failure-aware search context for
    later debugging-oriented generations.
  - Status: DeepResearch query inputs now include bounded recent
    failure-history terms from `ProgramDatabase.retrieval_failure_context`, with
    count and hash metadata.
  - Remaining roadmap gap: local-paper-corpus and hypothesis query grounding
    remain open.
  - Verification: focused DeepResearch and loop tests cover direct and
    `evolve()` failure-query wiring.

- [x] Add local-paper query grounding to retrieval roadmap evidence.
  - Evidence: roadmap retrieval work needed local literature corpus grounding
    beyond best-code, task, context, and failure terms.
  - Status: `evolve()` now passes bounded local paper manifest metadata through
    `ProgramDatabase.retrieval_query_context`, and DeepResearch query inputs
    record local-paper terms, policy, row counts, selected counts, and hashes.
  - Remaining roadmap gap: hypothesis query grounding, full provider payload
    artifacts, learned/external semantic ranking, and replayable
    transport/failure decisions remain open.
  - Verification: focused DeepResearch, loop, and database tests cover direct
    plugin query terms, real `evolve()` wiring, and strict row validation.

- [x] Add recent-hypothesis query grounding to retrieval roadmap evidence.
  - Evidence: roadmap retrieval work needed proposal-hypothesis grounding
    beyond best-code, task, context, failure, and local-paper terms.
  - Status: `ProgramDatabase.log()` now keeps bounded recent proposal
    hypotheses, and DeepResearch query inputs record hypothesis terms, policy,
    counts, considered characters, and hashes.
  - Remaining roadmap gap: full provider payload artifacts, learned/external
    semantic ranking, replayable transport/failure decisions, and full
    DeepEvolve-style debugging/refinement loops remain open.
  - Verification: focused DeepResearch, loop, and database tests cover direct
    plugin query terms, real `evolve()` wiring, and database hypothesis capture.

- [x] Add bounded provider-result snapshots to retrieval roadmap evidence.
  - Evidence: roadmap retrieval work needed provider-output artifact evidence
    beyond compact event hashes and cache file counts.
  - Status: DeepResearch retrieval events and cache snapshots now retain
    bounded/redacted provider-result snapshots, and plugin artifact metadata
    summarizes their counts and hashes.
  - Remaining roadmap gap: unbounded full provider payload artifacts,
    learned/external semantic ranking, replayable transport/failure decisions,
    and full DeepEvolve-style debugging/refinement loops remain open.
  - Verification: focused DeepResearch and loop tests cover provider snapshot
    cache persistence and manifest-visible artifact metadata.

- [x] Narrow plugin roadmap schema work to direct custom-plugin provenance.
  - Evidence: roadmap plugin extensibility still asked for custom plugin
    schemas even though configured entry-point plugins are the practical
    registry-backed external-plugin path.
  - Status: ROADMAP now scopes the remaining plugin registry work to richer
    package policy and direct custom-plugin schema/provenance, while code/docs
    support declared entry-point constructor schemas.
  - Remaining roadmap gap: package-registry policy and direct plugin object
    constructor-value/schema provenance remain open.
  - Verification: focused CLI/plugin registry and loop provenance tests cover
    declared schema validation and manifest retention.

- [x] Count ensemble retry/fallback attempts in live LLM-call budgets.
  - Evidence: roadmap budget work needed retry/fallback attempts to consume
    the active provider-call budget rather than only appearing in telemetry.
  - Status: `_generate_with_budget()` now clamps `LLMEnsemble.max_call_attempts`
    to the remaining `max_llm_calls` budget and records actual retained
    call-history attempt deltas into runtime/candidate budget snapshots.
  - Remaining roadmap gap: provider-adapter internal attempts, token/cost/time
    stops, and persisted/restored retry consumption remain open.
  - Verification: focused loop budget tests cover fallback consuming two budget
    units and fallback suppression when one budget unit remains.

- [x] Add mutation timeout artifact evidence to runtime cancellation work.
  - Evidence: roadmap timeout/cancellation work needed timeout failures to
    produce persisted role-specific artifacts, not just call telemetry.
  - Status: mutation LLM timeouts now persist generated failure-history rows
    with retained timeout call telemetry, while later generations can continue
    when budget remains.
  - Remaining roadmap gap: hard provider cancellation, budget-affecting
    timeout stop/quarantine behavior across LLM roles, and richer
    role-specific timeout artifacts remain open.
  - Verification: focused loop test covers mutation timeout failure-history and
    LLM-call artifact linkage plus later successful generation.

- [x] Retire stale retrieval transport classification roadmap gap.
  - Evidence: the open retrieval roadmap item still required
    redirect/TLS/transport failure classification even though current
    DeepResearch retrieval events already carry transport-policy records.
  - Status: the roadmap TODO now treats
    `libreevolve.retrieval_transport_policy.v1` classification as completed
    evidence and keeps the remaining requirement focused on unbounded provider
    payload artifacts, learned/external source ranking, replayable
    transport/failure decisions, and provider-boundary coverage.
  - Remaining roadmap gap: full provider payload artifacts, learned/external
    semantic ranking, replayable transport/failure decisions, and ongoing
    default/custom-provider provenance boundaries remain open.
  - Verification: focused DeepResearch tests cover audit-grade HTTPS/no
    redirect, cross-origin redirects, oversized payloads, TLS/certificate
    failures, and missing custom-provider transport metadata.

- [x] Narrow provider timeout/cancellation roadmap item to live enforcement.
  - Evidence: the roadmap timeout item still read like provider-call timeouts
    and the cancellation policy itself were missing, even though current
    runtime evidence covers provider request timeouts, ensemble wait
    deadlines, remaining-runtime clamping, policy validation, and role-scoped
    manifest rules.
  - Status: the roadmap item now names the actual remaining enforcement gap:
    connecting the existing policy contract to live provider SDK cancellation,
    budget-affecting timeout/cancellation stop or quarantine behavior, and
    persisted role-specific timeout artifacts beyond mutation.
  - Remaining roadmap gap: live hard cancellation and timeout-driven
    role-specific enforcement remain open.
  - Verification: focused cancellation-policy and loop/ensemble timeout tests
    cover the implemented timeout and policy surfaces.

- [x] Narrow environment provenance roadmap item to remaining policy gaps.
  - Evidence: the roadmap environment item still read like lockfile or
    package-snapshot semantics were missing even though current runtime
    provenance records known lockfiles, installed packages, pip freeze/config,
    WHEEL and source/install metadata, NumPy, provider SDKs, accelerator
    hints/probes, and audit-only package-source policy.
  - Status: the roadmap item now focuses on the remaining environment
    reproducibility policy needed for stronger run-manifest claims.
  - Remaining roadmap gap: complete install-source interpretation, broader
    build provenance, live provider service/API-version capture, provider cost
    or remote defaults, non-project build metadata, accelerator budget
    accounting, and package-source resolution policy remain open.
  - Verification: focused provenance tests cover the implemented environment
    provenance surfaces.

- [x] Narrow benchmark roadmap contract TODOs to real fixture integration.
  - Evidence: roadmap benchmark items still read like anti-gaming criteria and
    held-out/reference gates needed to be added, even though
    `libreevolve.benchmark_hardening.v1`,
    `libreevolve.example_benchmark_scope.v1`, and
    `libreevolve.systems_result_report.v1` already define those contracts and
    scope shipped examples as smoke-only.
  - Status: the active roadmap benchmark items now focus on connecting real
    benchmark and systems fixtures to the existing hardening and report
    contracts.
  - Remaining roadmap gap: real benchmark fixtures still need randomized or
    exhaustive validators, negative anti-gaming fixtures, saved construction
    artifacts, held-out/generalization cases, reference-correctness checks, and
    report artifacts.
  - Verification: focused benchmark hardening, example-scope, and systems
    report tests cover the implemented contracts.

- [x] Narrow AI-Co-Scientist roadmap wording to remaining measurement and
      bridge gaps.
  - Evidence: roadmap wording needed to recognize implemented structural
    representation-boundary evidence without turning it into hallucination or
    long-horizon claims.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.programmatic_representation_boundary_report` as current
    executable-code versus natural-language-proposal separation evidence.
  - Remaining roadmap gap: hallucination-risk controls, long-horizon
    step-count evidence, and a natural-language hypothesis bridge remain open.
  - Verification: focused loop tests cover the report and validator.

- [x] Narrow mutation-operator roadmap wording to remaining operator-family
      evidence.
  - Evidence: roadmap wording needed to recognize implemented fixed parser
    boundary reporting without implying AlphaEvolve-style constructed operator
    families.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.mutation_operator_boundary_report` for fixed edit grammar
    and payload-surface evidence.
  - Remaining roadmap gap: proposal-level operator-family provenance,
    task/failure-aware construction, adaptive selection, scoring, and
    benchmark telemetry remain open.
  - Verification: focused loop tests cover the report and validator.

- [x] Narrow creative-generation roadmap wording to remaining semantic
      diversity evidence.
  - Evidence: roadmap wording needed to recognize exact proposal duplicate
    telemetry without implying AlphaEvolve-style creative-generation proof.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.proposal_diversity_report` for exact proposal and idea
    hash uniqueness/duplicate counts.
  - Remaining roadmap gap: near-duplicate detection, semantic idea novelty,
    task-output/code-distance evidence, model-quality attribution, and
    benchmark linkage remain open.
  - Verification: focused loop tests cover the report and validator.

- [x] Narrow discovery-distance roadmap wording to remaining functional
      evidence.
  - Evidence: roadmap wording needed to recognize implemented seed-vs-generated
    syntactic/metric distance reporting without implying AlphaEvolve-style
    functional discovery-distance proof.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.initial_pool_divergence_report` for canonical workspace
    hash comparisons, bounded primary-file text distance, changed-file
    summaries, and numeric metric L1 evidence.
  - Remaining roadmap gap: task-specific functional artifacts,
    behavior/output-distance metrics, substantially-different thresholds, and
    benchmark-level discovery-distance telemetry remain open.
  - Verification: focused loop tests cover the report and validator.

- [x] Narrow duplicate-work roadmap wording to durable cache memory.
  - Evidence: roadmap wording needed to recognize implemented run-local
    exact-workspace evaluator-result reuse without implying durable
    AlphaEvolve-grade program-database memory.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.duplicate_work_policy_report` for cache stores/hits,
    canonical workspace plus evaluator-contract cache-key scope, and
    replayable cache-hit budget events.
  - Remaining roadmap gap: durable cross-run cache storage, resume-spanning
    replay, stochastic re-evaluation policy, semantic near-duplicate handling,
    and source/output-aware duplicate indexes remain open.
  - Verification: focused budget and loop tests cover the report, event
    validation, and evaluator-call budget savings.

- [x] Narrow proposal-memory roadmap wording to semantic retrieval gaps.
  - Evidence: roadmap wording needed to recognize implemented current-run
    proposal score records without implying AlphaEvolve-grade semantic idea
    memory.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.proposal_score_report` for bounded outcome/exact-novelty
    proposal scores.
  - Remaining roadmap gap: semantic proposal-index retrieval, calibrated
    quality models, cross-run proposal tables, hypothesis-refinement loops, and
    score/field influence policies remain open.
  - Verification: focused loop tests cover the report and validator.

- [x] Narrow backtracking roadmap wording to explicit policy gaps.
  - Evidence: roadmap wording needed to recognize observed current-run
    redirect evidence without implying AlphaEvolve-grade controller
    backtracking.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.controller_backtracking_report` for branch state
    transitions and observed fallback-parent or alternative-branch redirects.
  - Remaining roadmap gap: explicit controller-owned suppression/retry policy,
    fallback-target decision events, causal resumed-search replay, and
    cross-run branch tables remain open.
  - Verification: focused loop tests cover the report and validator.

- [x] Narrow prompt-current roadmap wording to full Figure 3 binding gaps.
  - Evidence: roadmap wording needed to recognize implemented current-run
    prompt-current mutation binding evidence without implying full Figure 3
    provenance.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.prompt_current_binding_report` for prompt/current-program
    hashes, parent/candidate workspace hashes, LLM call ids, diff SEARCH
    match counts/spans, evolve-block inner span mapping, workspace
    file-section target/full-file spans, full-mode target spans,
    prompt-history row joins, evaluator links, and archive admission.
  - Remaining roadmap gap: none for this bounded roadmap wording slice.
  - Verification: focused loop tests cover the report and validator.

- [x] Narrow prompt-example roadmap wording to stronger copy-policy gaps.
  - Evidence: roadmap wording needed to recognize implemented built-in
    example-sentinel diagnostics without implying full protection against
    copied prompt examples.
  - Status: `ROADMAP.md` and the roadmap TODO ledger now cite
    `runtime.history.prompt_example_copy_report` for built-in example-sentinel
    inventory and exact generated-payload copy diagnostics.
  - Remaining roadmap gap: configurable rejection, semantic/renamed copy
    detection, custom prompt-template inventories, and per-file-section
    normalized scanning remain open.
  - Verification: focused loop tests cover the report and validator.
