# Papers Todo: Reference and Specification Gaps

This list tracks mismatches discovered while reviewing the local `papers/`
directory and using the AlphaEvolve paper as the primary specification.

## AlphaEvolve Paper Requirements Not Yet Implemented

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
    Completed manifests also embed
    `libreevolve.controller_state_validation.v1` to verify the current
    controller boundary is terminal, synchronous, and drained rather than an
    async queue checkpoint.
  - Current gap: `evolve()` is still synchronous and evaluates one candidate at
    a time; there are no async LLM sampler queues, parallel evaluator nodes, or
    explicit mutation-chain-depth policy for expensive/slow-feedback
    evaluations. Sequential sibling proposal batches are accounting evidence,
    not AlphaEvolve-style throughput depth.

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
    roles, scheduler-policy telemetry, and restorable per-role scheduler audit
    records.
  - Current gap: the live selection state is still the shared ensemble bandit;
    role routing only narrows eligible backend indices, and
    `role_scheduler_state` is audit/restore evidence rather than independent
    per-role scheduler ownership with calibrated rewards and quotas.
  - Required result: add independent per-role scheduler policies for mutation,
    critique, feedback, and meta-prompt calls, plus restore validation and
    experiment reports proving role-specific selection and budget behavior.

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
    surfaces are ready.
  - Current gap: this is an honest boundary record, not non-Python or
    arbitrary-codebase support. There are no configured language runners,
    build-system contracts, language-aware marker grammars, or task-defined
    candidate abstraction hooks.

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
    service/default capture, and accelerator budget/accounting semantics.
  - Current gap: these records do not form a replayable environment contract:
    external build commands/options/environment, non-project build metadata,
    transitive package-source resolution, private-index policy, remote package
    artifact hashes, accelerator lease/accounting state, and restore/check
    validation remain absent.
  - Required result: add versioned external-build/package-source/accelerator
    provenance schemas plus restore/check validators and paper-facing evidence
    that clearly separates bounded audit hints from reproducible evaluator
    environment proof.

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
    revision, dynamic-reference status, and explicit no-rebin policy.
  - Current gap: existing cell coordinates are insertion-time snapshots under
    a local adaptive TF-IDF novelty heuristic. There is no learned descriptor
    model, evaluator-provided descriptor contract with compatibility rules, or
    tested archive rebin engine.
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
    islands.
  - Current gap: this is a truthful local topology boundary, not proof of a
    paper-identical AlphaEvolve evolutionary database. Adaptive island counts,
    non-ring topologies, topology-specific ablations, and paper-facing
    migration-policy reports remain absent.
  - Required result: if future work adds adaptive island topology or
    AlphaEvolve-specific migration policy fidelity, update the papers index,
    README, ROADMAP, and code TODO entries together so they neither underclaim
    current configurability nor overclaim fixed five-island policy.

- [ ] Tighten remaining invalid-workspace topology diagnostics for codebase-scale
  artifact failures.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.2.
  - Requirement: AlphaEvolve-style tasks mutate program artifacts under
    automated evaluator feedback; generated invalid artifacts should leave
    stable, inspectable diagnostics that can steer future proposals.
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
    and future materialization filesystem paths must preserve the stable
    reason/path diagnostic contract before LibreEvolve can claim robust
    codebase-scale invalid-artifact feedback.

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
    Live global token and configured-cost stop
    criteria now exist, and full-runtime restore now pre-applies replayed
    provider-attempt/token/configured-cost/latency controller events to the
    restored `evolve()` budget snapshot. Accelerator budgets, async queue
    accounting, live provider pricing/default-rate capture beyond configured
    token-cost estimates, and executed equal-budget benchmark scripts are still
    missing.
    `libreevolve.alphaevolve_ablation_report.v1` now defines and tests an
    equal-budget ablation-result report contract for reports produced by
    executed runs: all six Figure 8 variants, declared targets, exactly three
    seeds, required equal-budget fractions, finite scores,
    consumed-budget/fraction consistency, consistent budget unit/limit per seed
    curve and across all variants/seeds for each target, passed component
    assertions, and hashed curve artifacts.
    `libreevolve.alphaevolve_ablation_artifact_inventory.v1` now verifies
    declared ablation report artifacts under an explicit artifact root,
    checking safe relative paths, existence, SHA-256 hashes, byte counts,
    per-artifact statuses, and aggregate missing/mismatch/invalid counts. No
    benchmark script emits those reports yet.
    `libreevolve.llm_feedback_calibration.v1` now defines and tests a feedback
    grader calibration-report contract with declared graders, at least two
    calibrated tasks for readiness, per-grader/task scored records, finite
    normalized expected and observed scores, exact absolute-error consistency,
    and declared calibration artifacts.
    `libreevolve.llm_feedback_calibration_artifact_inventory.v1` verifies those
    calibration report, raw-record, grader-config, and plot artifacts against a
    safe artifact root. No runtime feedback-calibration fixture emits those
    reports yet.
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
    `meta_prompt`. Rules for scopes with configured
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
    evidence. Ensemble-deadline timeout rows now also include a
    replay-validated `libreevolve.provider_cancellation_record.v1` with the
    role, backend, call id, timeout seconds, retry/fallback/telemetry budget
    action, and explicit `unsupported_daemon_worker_may_continue` hard-cancel
    gap. Remaining budget/runtime gaps are live hard cancellation handles,
    timeout-driven stop enforcement beyond audit observations, richer
    role-specific timeout/cancellation artifacts beyond configured in-run
    quarantine observations, accelerator/worker budget enforcement, live
    provider pricing/default-rate capture beyond configured token-cost
    estimates, provider-output/raw-payload replay beyond bounded retained
    diagnostics, and async/pending-work controller restore. The remaining gap
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
    calibration reports for real reviewer/task suites. The remaining ablation
    and calibration gap is executing and emitting real reports, not validating
    declared result or feedback-calibration artifacts once a report names them.
    The remaining provider cancellation gap is live cancellation/stop behavior,
    cross-run quarantine/resume behavior, and richer runtime artifact
    generation, not configured in-run role/backend quarantine observations or
    verifying declared cancellation evidence files once a policy names them.

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
    stale audit-only policy labels.
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
    scheduler-resume-hash evidence plus self-validation, and retained LLM
    call-history rows now provide per-call provider-internal retry records
    grouped by role plus configured-cost source metadata. Final
    manifests also emit `runtime.llm_provider_diagnostics` using
    `libreevolve.llm_provider_diagnostics.v1`, a retained-call-history
    aggregate that groups backend/API-mode usage, bounded provider diagnostic
    keys and omitted counts, provider response/error retention modes and
    policies, retained hash/text/character counts, redaction/truncation
    counts, configured cost-estimate evidence, not-estimated reasons, backend
    defaults, call-history retention, and a records hash while explicitly
    avoiding full raw provider-payload and live-pricing claims.
    `validate_provider_capability_lookup_policy()` now validates
    `libreevolve.provider_capability_lookup_policy.v1` records for static-only
    provider lookup boundaries, OpenAI API-mode policy linkage, offline
    compatibility, record count/hash integrity, and explicit non-use of live
    model-registry, service/API-version, or account-availability discovery.
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
    signature shape without parameter values. Captured direct-plugin
    constructor values, arbitrary direct-plugin schemas, and richer custom
    package policy beyond entry-point distribution records remain part of the
    broader plugin registry gap. Problem-local evaluator
    helper/data access is now governed by an enforced declared-dependency
    policy: validator imports and file reads may touch only the configured
    entrypoint, captured companion sources, or captured declared data sources.
    Seeded replay is still incomplete, but the identity gap is narrower than
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
    while keeping full replay, provider-output replay, and pending-work resume
    marked unavailable. But
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
  - Current gap: full run replay still lacks provider output replay,
    plugin-owned RNG capture, controller/pending-work state restore, and
    lineage replay.
  - Required result: compose persisted RNG restore with full resume/replay,
    define provider-output and plugin-owned RNG capture or exclusion semantics,
    and keep paper-index seeded-replay claims scoped so they do not imply full
    replayability until this is true.

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
    in the declared objective vector when desired. Metric-specific archive replacement and
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
    replaced the primary scalar MAP-Elites cell policy.
    `runtime.history.failure_index` now groups failure records by fingerprint
    with bounded repetition/latest-record evidence. `runtime.history.hypothesis_index`
    now exposes bounded redacted proposal idea/rationale/hypothesis evidence
    and feeds hypothesis records into `resurfacing_index`. This remains a
    heuristic rather than a paper-faithful multi-score database policy:
    primary MAP-Elites cell replacement is still scalar, Pareto/frontier
    dominance does not replace the primary grid, and durable queryable
    multi-objective resurfacing across persisted database tables, embeddings,
    cross-run failure and hypothesis indexes, full artifact-content indexes,
    full lineage subgraphs, learned/cross-run novelty indexes, and schema
    migrations remains open. `runtime.history.artifact_index`
    now exposes bounded evaluator-artifact path/hash, redaction, skipped-file,
    stage, and content-excerpt evidence, and valid artifact-bearing candidates
    feed into `resurfacing_index`.
  - Required result: add Pareto/frontier archive replacement and durable
    persisted lineage-aware resurfacing for programs that excel under different
    metrics.

- [ ] Proposal scoring and semantic hypothesis retrieval.
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
  - Current gap: there is no versioned proposal score, calibrated hypothesis
    quality or novelty signal, embedding/semantic proposal index, cross-run
    persisted proposal table, or policy that fully governs which proposal
    fields can influence retrieval, prompting, and archive resurfacing.
  - Required result: add proposal scoring, semantic/cross-run
    proposal-hypothesis retrieval, persisted proposal-index tables, and
    prompt/retrieval/archive policy boundaries before treating proposal
    metadata as AlphaEvolve-grade idea memory.

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
    meta-prompt final-boundary-only roles explicit.
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
    limitations.
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
    overclaims as manifest validation failures.
  - Required result: apply or explicitly model migration-event replay, add
    controller/pending-work resume state, and add paper-visible resume/replay
    tests covering below-threshold, non-admitted, elite-only, and
    cell-replacement cases. The remaining paper gap is not terminal controller
    event-stream artifact verification or terminal drained-state validation.

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
    the bounded redacted prompt-performance evidence. Final manifests now
    include `runtime.prompt_context_policy_coverage` with schema
    `libreevolve.prompt_context_policy_coverage.v1` and embedded validation
    against the current policy schema/capability map, while keeping
    `alphaevolve_context_policy_complete` false and listing unsupported
    retrieval/summarization, learned ranking, and semantic context-selection
    surfaces. The AlphaEvolve table now scopes the remaining prompt-context
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
    benchmark claims. `validate_benchmark_evidence_scope()` now cross-checks
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
    false`.
  - Required result: distinguish smoke examples from benchmark fixtures in docs,
    add operation/rank-aware matrix benchmark validation beyond the current
    2x2 smoke checks, connect hardening reports and artifact schemas for
    geometric constructions, and create repeatable benchmark reports tied to
    AlphaEvolve target families. The remaining paper gap is generating those
    anti-gaming evidence files from benchmark-grade tensor/geometric fixtures,
    not emitting matrix smoke hardening evidence, verifying declared hardening
    files once a report names them, or preventing declared hardening evidence
    from overriding the smoke-only scope registry.

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
    mismatches. `libreevolve.matrix_result_artifact_inventory.v1` now verifies
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
  - Required result: connect real matrix target tensors, exact algorithm
    artifacts, certificate-generation artifacts, and generated export/notebook
    links to real report instances before treating LibreEvolve matrix results
    as AlphaEvolve-comparable evidence. The remaining gap is producing those
    discovered tensor artifacts for the suite, not verifying declared report
    artifacts, validating the checked bundle wrapper, or emitting one checked
    Strassen baseline once those files exist.

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
    documented as not applicable.
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
  - Required result: connect compiler, hardware, kernel, scheduling, or systems
    fixtures to this report format, implement real unseen evaluation cases and
    randomized/reference-correctness checks, and emit report artifacts that
    distinguish loop feedback from held-out, deployment, and certification
    evidence. The remaining paper gap is producing those evidence files from
    real fixture runs, not verifying the declared files, report/inventory
    consistency, or evidence-bundle consistency once a report names them.

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
    must be a safe path present in `files`. This prevents malformed unselected,
    invalid, or non-admitted rows from being hidden by the selected row.
  - Required result: add whole-run source/workspace integrity summaries and
    durable query/report surfaces over every candidate's source payloads,
    workspace paths, source hashes, primary-file coherence, and display/truncation
    policy. The remaining gap is not malformed unselected source-payload
    validation or selected-row workspace display.

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
    TLS certificate-chain retention, or authoritative prompt context.
    `runtime.retrieval.evidence_coverage` now records
    `libreevolve.retrieval_evidence_coverage.v1` run-level coverage counts for
    retained retrieval evidence surfaces and
    `libreevolve.retrieval_evidence_coverage_validation.v1` rejects raw
    provider/source payload, semantic-verification, learned-ranking,
    TLS-replay, and full-replay overclaims.
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
    validation, semantic-boundary overclaim auditing, run-level retrieval
    evidence coverage validation, or the core full-runtime restore bundle that
    deliberately excludes provider-output replay.
