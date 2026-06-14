# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Documentation Map

- [ ] Add README documentation-map routing and drift evidence.
  - Spec evidence: the README's `Documentation Map` is a reader-routing
    contract for where setup, operational details, implementation status,
    roadmap priorities, paper-derived evidence, and TODO ledgers belong. For
    AlphaEvolve-alignment work, those route descriptions should stay
    synchronized with the actual documentation tree and should prevent claims
    from being hidden in the wrong surface.
  - Current evidence: README links `docs/README.md`, architecture,
    configuration, backends, plugins, run artifacts, status, ROADMAP,
    `papers/README.md`, and `docs/todo/`, and says setup belongs in the root
    README, operational details in `docs/`, paper-derived evidence in
    `papers/`, and active/completed gap tracking in `docs/todo/` plus
    `ROADMAP.md`. The broad README semantic-claim TODO and
    `papers/documentation_truthfulness_boundary.json` already track
    cross-document truthfulness and docs-routing at a high level.
  - Current gap: no README-owned validator or sidecar parses the Documentation
    Map, verifies every linked target exists, checks that each route summary
    matches the target document's purpose, flags newly added major docs that
    need routing, or detects content placed in the wrong surface such as
    paper-derived claims outside `papers/` or implementation priorities
    outside ROADMAP/TODO ledgers.
  - Required result: add README documentation-map evidence that inventories
    each routed document, validates link existence and purpose text, compares
    route summaries with target headings/front matter or declared scope, flags
    missing major docs, and checks that README/docs/papers/ROADMAP/TODO content
    boundaries remain synchronized whenever documentation structure changes.

## Requirements

- [ ] Add durable README install and requirements smoke evidence.
  - Spec evidence: the README is the onboarding contract for the supported
    local runtime. Its Python-version and editable-install requirements should
    be protected by committed smoke evidence, because AlphaEvolve-alignment
    work depends on reproducible local setup before any benchmark claims can be
    trusted.
  - Current evidence: `pyproject.toml` declares `requires-python = ">=3.11"`
    and dependency ranges, the README tells this Windows machine to use
    `py -3.12`, and CI/release checks cover package metadata, wheel/sdist
    smoke, and environment provenance at broader runtime/release boundaries.
  - Current gap: no committed README-specific install transcript, CI
    assertion, or sidecar proves the exact
    `py -3.12 -m pip install -e ".[dev]"` onboarding command succeeds with the
    documented Python version, that dev dependencies are available after
    install, or that failures are reported distinctly from later
    quick-start/provider smoke failures.
  - Required result: add a README install smoke proof or CI job that runs the
    documented editable-install command in a clean environment, records
    Python/pip/package versions and expected command success, and updates
    README/TODO evidence whenever the requirements or install command change.

## Research References and Bundled Papers

- [ ] Add README paper-cache topical classification evidence.
  - Spec evidence: the README says the local paper cache contains 53 PDFs on
    LLM-guided evolution, program synthesis, quality-diversity optimization,
    and related benchmarks. That topical scope should be backed by row-level
    paper taxonomy or source-role labels, not only by local PDF availability.
  - Current evidence: `paper_manifest` validates manifest shape, README
    documented count, local PDF existence, source rows, and the local paper
    cache badge/count. `papers/README.md` provides paper-facing titles,
    implementation status, and benchmark coverage decisions, while
    `papers/related_work_taxonomy_boundary.json` records that AlphaEvolve
    Related Work positioning taxonomy and README/ROADMAP claim gates are not
    yet ready.
  - Current gap: there is no committed row-level topic taxonomy proving which
    cached papers belong to the README-listed topic families, no validator
    checking README topic wording against paper-index categories, and no drift
    report when new papers fall outside those categories or when the README
    topic sentence changes.
  - Required result: add paper-cache topic/category fields or a sidecar
    taxonomy, validate README topic wording from those records, and update
    README/TODO/paper docs when the cache scope changes.

- [ ] Add README fresh-checkout paper-cache rehydrate evidence.
  - Spec evidence: the README tells users they can rehydrate the gitignored
    PDF cache on a fresh checkout. That is a reproducibility and source-access
    claim, so it should be backed by evidence distinct from a local machine
    already having all PDFs present.
  - Current evidence: `libreevolve.tools.paper_manifest` implements
    `--rehydrate`, validates byte counts and SHA-256 hashes, and has unit
    tests for missing-file downloads, matching-file skips, forced redownloads,
    and redacted network failures. The local `--require-local-pdfs` check
    currently proves that this workstation has 53 present PDFs, and
    `papers/README.md` also documents the rehydrate command.
  - Current gap: no committed README-owned transcript, sidecar, or CI/manual
    run artifact proves the exact README `--rehydrate` command from a clean
    checkout with an absent PDF cache, records expected network failure/skip
    modes, confirms all downloaded files match manifest hashes, or separates
    rehydrate drift from ordinary local-cache validation.
  - Required result: add a fresh-checkout rehydrate proof that runs or
    faithfully simulates the README command from an empty ignored PDF cache,
    records row counts, downloaded/skipped/failure states, byte-count/hash
    verification, and safe redaction behavior, then updates README/TODO
    evidence whenever paper-cache commands or manifest semantics change.

## Feature Claims

- [ ] Add semantic README claim verification and evidence mapping.
  - Spec evidence: AlphaEvolve-alignment documentation should keep top-level
    project claims synchronized with implemented behavior and cited evidence,
    especially because the README is the first reader-facing claim surface.
  - Current evidence: the README is scoped as alpha-stage, Python-first,
    local/synchronous, and not a full AlphaEvolve reproduction. The committed
    `papers/documentation_truthfulness_boundary.json` records README status
    scoping, ROADMAP and papers-index scoping, TODO ledgers, docs routing,
    paper-manifest checks, stale source-specific wording checks, sidecar
    registry coverage, and focused boundary tests. `docs/README.md` now states
    that AlphaEvolve-alignment cleanup is a whole-documentation task spanning
    the root README, operational guides, status, ROADMAP, papers index,
    sidecars, and active/completed TODO ledgers.
    `papers/documentation_claim_inventory.json` now assigns stable claim ids
    and evidence anchors with file-offset source spans to top-level README
    status, runnable-today, limit, ROADMAP, and papers-index scope claims,
    and records local evidence-ref existence plus Markdown fragment-anchor
    resolution for those anchors. It also records audited README, ROADMAP,
    and papers-index Markdown headings plus uncovered heading-to-claim gaps
    with active TODO-owner links while marking complete README coverage and
    semantic verification as absent.
  - Current gap: there is still no semantic claim verifier, machine-readable
    implementation-evidence mapping for every README claim, complete
    cross-document claim inventory, stale completed-entry detector, generated
    alignment report, or full proof that every AlphaEvolve-facing README or
    docs claim is current.
  - Required result: add a README claim inventory that links each feature,
    limit, research-source, and paper-derived statement to code/tests/docs/
    sidecars/TODO evidence, extend it to the linked documentation surfaces,
    then validate stale or unsupported claims in CI.

- [ ] Add `docs/status.md` ledger freshness and coverage evidence.
  - Spec evidence: the README tells readers that `docs/status.md` is the full
    implemented-versus-missing ledger. For AlphaEvolve-alignment work, that is
    a strong documentation claim: the status ledger should remain synchronized
    with implementation code, ROADMAP priorities, `papers/README.md` status
    rows, sidecar absence boundaries, and active TODO entries rather than
    becoming a stale hand-maintained summary.
  - Current evidence: `docs/status.md` contains the detailed implementation
    and absence-boundary inventory moved out of the root README; `docs/README.md`
    routes paper/spec reviewers to `docs/status.md`, ROADMAP, and
    `papers/README.md`; and `papers/documentation_claim_inventory.json`
    tracks selected README/ROADMAP/papers-index claims. Existing paper
    status-claim inventory validation checks `papers/README.md` row claims,
    not the much larger `docs/status.md` ledger.
  - Current gap: there is no structured inventory, sidecar, or CI check that
    parses `docs/status.md`, maps each implemented and missing-status bullet to
    source modules, tests, ROADMAP entries, paper sidecars, active/completed
    TODO anchors, and `papers/README.md` rows, or detects stale status prose
    when code, ROADMAP, paper status rows, or TODO coverage changes. This
    leaves the README's "full implemented-versus-missing ledger" claim weaker
    than the paper-index status inventory.
  - Required result: add a status-ledger freshness artifact and validator that
    inventories `docs/status.md` bullets, links each claim to current
    implementation/sidecar/TODO evidence or explicit absence scope, compares
    overlapping claims with README, ROADMAP, `papers/README.md`, and paper
    sidecars, and fails when status wording drifts from authoritative current
    evidence.

## Architecture Description

- [ ] Add README repository-layout drift and module-role evidence.
  - Spec evidence: a README repository-layout block is an architecture claim
    surface. For AlphaEvolve-alignment work, high-level module roles should
    stay tied to the actual code tree and supporting docs so readers can tell
    which runtime components exist, which are only planned, and where
    paper-facing boundaries live.
  - Current evidence: the README lists `libreevolve/core`, `llm`,
    `population`, `plugins`, `problems`, and `tools`, plus `docs/`, `papers/`,
    `runs/`, and `tests/`. Those directories currently exist, and
    `docs/architecture.md` provides a fuller runtime overview. The broader
    documentation-claim inventory records the README headings and selected
    evidence refs, but it does not validate the repository-layout code block
    as a structured architecture claim.
  - Current gap: no committed layout inventory, test, or sidecar compares the
    README repository-layout entries against the current source/docs tree,
    validates that each role summary is still accurate, flags new top-level
    packages or docs that should be mentioned, or distinguishes implemented
    module roles from AlphaEvolve-parity placeholders.
  - Required result: add a README layout/schema drift check or generated
    sidecar that parses the layout block, compares it with the package and
    documentation tree, maps each role summary to concrete modules/docs/tests,
    and updates README/TODO evidence whenever module ownership or layout
    changes.

- [ ] Add architecture-guide runtime-flow drift evidence.
  - Spec evidence: `docs/architecture.md` is the detailed end-to-end runtime
    contract for CLI setup, problem loading, candidate representation,
    mutation application, evolution-loop ordering, prompt sampling,
    evaluation, plugins, MAP-Elites, persistence, restore, and known
    limitations. For AlphaEvolve-alignment work, that architecture guide must
    stay synchronized with the actual implementation and keep local
    synchronous behavior separate from AlphaEvolve async/distributed parity.
  - Current evidence: the root README and `docs/README.md` route readers to
    `docs/architecture.md` for runtime architecture. The guide contains many
    code-specific claims, including `.env` loading boundaries, configured
    plugin resolution, candidate path safety, proposal-loop ordering,
    critique/feedback sequencing, prompt-context behavior, evaluator
    preflight, archive restore, controller-state snapshots, and synchronous
    limitation bullets. Active TODOs already cover README repository-layout
    drift, `docs/status.md` ledger freshness, ROADMAP readiness criteria, and
    paper-facing async/topology boundaries, but not the architecture guide as
    a standalone operational contract.
  - Current gap: there is no committed architecture-claim inventory or drift
    validator that maps each `docs/architecture.md` flow step, limitation, and
    component-role statement to concrete source functions, tests, runtime
    manifest fields, sidecars, and active TODO owners. Hook order, restore
    semantics, prompt/evaluator surfaces, archive behavior, plugin behavior,
    or runtime-budget claims can drift without a page-specific failure or
    source-offset evidence update.
  - Required result: add an architecture-guide evidence map and validation
    gate that inventories each major architecture claim with code/test/runtime
    anchors, flags unsupported or AlphaEvolve-facing parity claims separately,
    and requires README/docs/TODO updates when implementation flow,
    persistence semantics, or architecture limitations change.

## Quick Start

- [ ] Add durable README quick-start smoke-run evidence.
  - Spec evidence: the root README is the primary onboarding claim surface, so
    its no-provider quick-start commands should be protected by committed
    evidence or CI rather than relying on ad hoc local runs.
  - Current evidence: on 2026-06-14, the documented commands
    `py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --run-name readme_smoke_sorting --max-llm-calls 0 --overwrite`
    and `py -3.12 -m libreevolve show runs/readme_smoke_sorting` both
    completed locally. The run stopped with `stop_reason: max_llm_calls`,
    selected an archive-retained valid seed program, and reported
    `Best fitness: 1.000000`.
  - Current gap: the successful run artifacts live under gitignored `runs/`;
    there is no committed README quick-start smoke transcript, sidecar, or CI
    check proving that the exact README commands keep working across future
    changes.
  - Required result: add a committed smoke-proof artifact or CI job that runs
    the README no-provider quick-start path, validates expected stop reason and
    `show` output fields, and updates README/TODO evidence when the command
    changes.

- [ ] Add provider-backed README example smoke matrix.
  - Spec evidence: AlphaEvolve depends on a managed model mix and provider
    capability, while LibreEvolve's README shows provider-backed run examples
    for OpenAI, Anthropic, and Ollama. Those examples should be kept honest
    with provider-specific availability evidence rather than only placeholder
    model ids.
  - Current evidence: the README explicitly tells users to replace
    `<openai-model-id>`, `<anthropic-model-id>`, and
    `<installed-ollama-model>` with models available to their account or local
    install, and warns that provider-backed runs may fail. The current
    `tests/integration/test_hello_world.py` coverage is credential-gated on
    `ANTHROPIC_API_KEY`; it does not prove the README OpenAI example, Ollama
    example, account-specific model ids, or provider-command parity.
  - Current gap: there is no committed provider smoke matrix, redacted model
    availability record, local Ollama inventory, or CI/report artifact that
    proves each provider-backed README command family remains runnable. This
    also keeps Google/Gemini AlphaEvolve provider parity separate from the
    README's generic backend examples.
  - Required result: add provider-family smoke evidence with safe credential
    handling, account/local model id provenance, expected skip/failure modes,
    and README/TODO updates whenever provider example commands or supported
    backend families change.

- [ ] Add README guardrail for subprocess/CLI-authenticated LLM providers.
  - Spec evidence: AlphaEvolve-style experiments rely on auditable provider
    calls and model-mix claims. A README feature bullet for backend support
    should distinguish built-in SDK adapters, generic custom import-path
    backends, and any future local authenticated CLI provider before readers
    use README commands or benchmark prompts as evidence of first-class
    provider support.
  - Current evidence: the README currently lists OpenAI, Anthropic, Ollama,
    and custom import-path backend support; the quick-start provider examples
    show only OpenAI, Anthropic, and Ollama placeholders. `docs/backends.md`
    documents custom backends as Python `class_path` implementations with
    JSON-safe kwargs, while the active code TODO now tracks the missing
    subprocess/CLI backend contract for command discovery, auth/session
    provenance, transcript retention, diagnostics, and budget/cancellation
    semantics.
  - Current gap: no README-owned wording, evidence map, or drift check states
    that custom import-path support is not the same thing as first-class
    Codex-authenticated or other local CLI provider support. A user could add
    an ad hoc CLI wrapper through `type: custom` and mistake the README's
    generic backend claim for supported, reproducible provider parity.
  - Required result: update README provider/support wording and validation so
    built-in SDK adapters, custom import-path wrappers, and any future
    subprocess/CLI-authenticated provider lane are separated; link to the
    subprocess/CLI backend contract TODO; and prevent README, ROADMAP,
    benchmark, or paper-facing examples from claiming Codex-authenticated or
    local CLI providers until the tracked backend contract and smoke evidence
    exist.

- [ ] Add backend-doc guardrail for CLI-authenticated provider support.
  - Spec evidence: `docs/backends.md` is the detailed provider contract that
    users will follow when choosing between built-in SDK adapters and custom
    extension points. It should make the current backend boundary clear before
    benchmark prompts or local experiments rely on Codex-authenticated or other
    local CLI sessions as if they were first-class supported providers.
  - Current evidence: `docs/backends.md` lists OpenAI, Anthropic, Ollama, and
    custom import-path backends, then documents custom backends as Python
    `class_path` implementations with JSON-safe kwargs and the common
    `generate(prompt, **kwargs) -> str` protocol. The active code TODO tracks
    the missing subprocess/CLI backend contract, and the README TODO tracks
    top-level provider wording, but the backend docs page itself does not yet
    separate SDK adapters, extension-owned wrappers, and any future
    CLI-authenticated provider lane.
  - Current gap: a reader can treat a custom import-path wrapper around a local
    CLI as equivalent to supported provider integration, even though
    `docs/backends.md` currently has no command-discovery, auth-session,
    transcript-retention, provider-attempt accounting, timeout/cancellation,
    or diagnostics contract for that lane. There is also no backend-doc drift
    check preventing examples, configuration snippets, or model-selection
    guidance from implying Codex-authenticated or local CLI provider support
    before the tracked backend contract and smoke evidence exist.
  - Required result: update `docs/backends.md` with an explicit provider-lane
    taxonomy, custom-wrapper limitation wording, and links to the
    subprocess/CLI backend contract TODO; add a docs/test guard that rejects
    CLI-authenticated provider examples or supported-provider claims until the
    first-class contract, manifest fields, diagnostics, and smoke fixtures are
    implemented.

- [ ] Add backend-guide provider contract drift evidence.
  - Spec evidence: `docs/backends.md` is the detailed operational contract for
    provider selection, scheduler/reward accounting, retry/fallback behavior,
    provider failure telemetry, prompt and response caps, role routing,
    OpenAI API-mode policy, Anthropic/Ollama adapter behavior, custom backend
    construction, credential preflight, client-context provenance, and
    Google/Gemini absence boundaries. AlphaEvolve-alignment work depends on
    this page staying synchronized with actual backend/runtime behavior before
    any model-mix, provider, or scheduling claim is treated as evidence.
  - Current evidence: the guide documents `LLMEnsemble` accounting, bounded
    call-history retention, durable `llm_calls.jsonl` replay, scheduler
    restore, prompt validation, built-in adapter defaults, role-scoped
    backend routing, failure quarantine, retries, timeouts, prompt-token
    limits, OpenAI Chat/Responses routing, request-parameter surfaces,
    `llm_prompt_roles`, custom backend `class_path` specs, `.env` credential
    behavior, and Gemini provider-parity absence records. Many individual
    backend behaviors have focused tests and completed TODOs, but the active
    backend-doc TODO covers only CLI-authenticated provider overclaiming.
  - Current gap: there is no page-specific inventory or drift validator that
    maps each `docs/backends.md` claim, constructor field, allowed parameter,
    telemetry field, timeout/retry rule, scheduler policy, OpenAI route rule,
    custom-backend limitation, environment/preflight statement, and
    AlphaEvolve-facing provider boundary to source modules, tests, run
    artifacts, paper sidecars, and active TODO owners. Backend behavior can
    change in `llm/`, `core/config.py`, `cli.py`, ledger replay, or runtime
    manifest code without a backend-guide failure.
  - Required result: add a backend-guide evidence map and validation gate that
    parses provider sections and practical guidance, verifies code/test/
    artifact anchors for each documented claim, separates built-in SDK
    support from custom-extension and missing Gemini/Codex-provider parity,
    and requires README/docs/TODO updates whenever provider adapters,
    scheduler policy, telemetry, timeout/retry, credential, or custom-backend
    behavior changes.

## Plugin Docs

- [ ] Add plugin-guide hook contract drift evidence.
  - Spec evidence: `docs/plugins.md` is the detailed user-facing contract for
    lifecycle hooks, configured plugin specs, execution order, score
    adjustment, prompt context, run-artifact metadata, and fatal plugin
    failures. For AlphaEvolve-alignment work, plugin behavior must stay
    clearly scoped as synchronous local hooks and paper-inspired approximations
    rather than faithful multi-agent, distributed, or external-plugin parity.
  - Current evidence: `docs/plugins.md` documents alias/spec validation,
    direct plugin-object validation, hook ordering, prompt-context metadata,
    score-composition behavior, artifact metadata, fatal hook failures, and
    built-in `causal`, `deep_research`, `modular`, and `ttt_rl` limitations.
    Active roadmap and code TODOs cover broader plugin extensibility and
    paper-inspired plugin overclaiming, but there is no plugin-guide-specific
    drift check comparable to the README, backend-doc, development-doc, and
    AGENTS.md documentation guardrails.
  - Current gap: there is no committed inventory that maps each
    `docs/plugins.md` hook, validation rule, failure policy, built-in option,
    and limitation statement to `PluginBase`, the registry, loop call sites,
    tests, runtime metadata, and paper-boundary TODOs. There is also no guard
    that fails when hook order, plugin config schemas, score/admission
    semantics, or built-in plugin capabilities change without updating the
    plugin guide and its AlphaEvolve scope wording.
  - Required result: add a plugin-guide contract map and drift validator that
    links each documented hook and built-in plugin claim to code/tests/runtime
    artifacts, separates local synchronous hook support from AlphaEvolve-style
    plugin/agent parity, and requires README/TODO updates when plugin runtime
    behavior or built-in plugin evidence changes.

## Problem Layout

- [ ] Add README problem-layout contract drift evidence.
  - Spec evidence: the README's `Problem Layout` section is the first
    problem-authoring contract most users see. Its list of required and
    optional files should stay synchronized with the loader, problem-format
    docs, bundled examples, and AlphaEvolve-alignment boundaries for validators,
    metrics, prompts, context, config, and candidate workspaces.
  - Current evidence: README lists `initial_programs/`, `validate.py`,
    `metrics.yaml`, `task_description.txt`, and optional `config.yaml`, and
    points to `docs/problem-format.md` for the full contract. The current
    examples exercise several layouts, including workspace examples and
    sorting-network candidates, while broader code/paper TODOs track
    non-Python runners, candidate abstractions, evaluator contracts, context
    manifests, validator metadata, and benchmark fixtures.
  - Current gap: no README-owned validator, sidecar, or smoke fixture parses
    the README problem-layout list, compares it with loader/preflight behavior
    and `docs/problem-format.md`, checks that at least one minimal example
    still satisfies the listed contract, or flags when new problem surfaces
    such as context manifests, artifact policies, candidate-language metadata,
    or benchmark-hardening helpers should be mentioned or explicitly scoped
    out.
  - Required result: add a README problem-layout evidence map or drift test
    that links each listed path to loader behavior, docs, examples, and
    validation coverage; records required versus optional status and known
    AlphaEvolve-facing omissions; and updates README/TODO evidence whenever
    problem-loading, evaluator, context, metrics, config, or example layout
    semantics change.

- [ ] Add problem-format guide loader-contract drift evidence.
  - Spec evidence: `docs/problem-format.md` is the full problem-authoring
    contract that readers are sent to after the root README. It specifies the
    required layout, context manifest semantics, codebase-integration metadata,
    task and metrics files, validator signatures, configured evaluator stages,
    language/build-runner declarations, seed workspaces, seed policies, and
    unsupported AlphaEvolve-facing surfaces.
  - Current evidence: `docs/problem-format.md` documents many loader and
    evaluator details that are implemented across
    `libreevolve/problems/loader.py`, `libreevolve/core/config.py`,
    `libreevolve/core/evaluator.py`, and tests such as
    `tests/core/test_loader.py`. The active README problem-layout TODO covers
    the short root README list and its link to the problem-format page, but it
    does not validate the problem-format guide's own long-form contract.
  - Current gap: there is no committed problem-format claim inventory or drift
    validator that maps each documented file, manifest key, signature,
    optional metadata block, validation rule, unsupported runner declaration,
    and example snippet to loader/config/evaluator code plus tests and
    AlphaEvolve-boundary TODOs. Changes to `context.yaml`, `seed_policy.yaml`,
    embedded evaluator stages, metrics semantics, or candidate-language/build
    declarations can therefore leave the full problem-authoring guide stale
    without a page-specific failure.
  - Required result: add a problem-format evidence map and validation gate
    that parses the guide's contract sections, links each claim to
    source/tests/examples/runtime metadata, distinguishes executable support
    from declared-unsupported AlphaEvolve surfaces, and requires
    README/docs/TODO updates when problem-loading or evaluator semantics
    change.

## Example Scope

- [ ] Add README example-scope drift and benchmark-claim evidence.
  - Spec evidence: the README's `Example Scope` section is the first guardrail
    separating smoke fixtures, benchmark candidates, and paper-comparable
    evidence. That distinction is central to AlphaEvolve-alignment truthfulness
    because examples can otherwise be mistaken for reproduced benchmark
    results.
  - Current evidence: README says bundled examples are intentionally small,
    distinguishes optimization-pressure seeds from neutral plateau/diversity
    fixtures, scopes `sorting_network_8` and `sorting_network_9` as bounded
    benchmark candidates rather than paper-comparable evidence, and points to
    `papers/sorting_network_rediscovery_boundary.json`. Code and paper TODOs
    already track stronger benchmark fixtures, benchmark-hardening reports,
    example-scope registries, sorting-network repeated-run/source-citation/
    certification evidence, matrix and constructive-math benchmark artifacts,
    and broader representative-benchmark readiness.
  - Current gap: no README-owned validator, sidecar, or drift check parses the
    example-scope wording, compares it with the example-scope registry,
    problem docs, runtime `benchmark_fixture_readiness_report` records,
    sorting-network boundary sidecars, and `papers/README.md` status rows, or
    detects when a smoke fixture, benchmark candidate, or paper-comparable
    claim changes without README/TODO updates.
  - Required result: add README example-scope evidence that maps each bundled
    example family to its scope classification, validator strength,
    benchmark-readiness artifacts, paper-comparability status, and required
    future certification gates; validate that README, problem docs, ROADMAP,
    papers, and runtime metadata cannot promote smoke examples or benchmark
    candidates into paper-comparable claims until the mapped evidence exists.

## Run Artifacts

- [ ] Add README run-artifact list drift and scope evidence.
  - Spec evidence: the README's `Run Artifacts` section is an onboarding and
    inspection contract for the local evolutionary runtime. Its list of common
    files and directories should stay synchronized with actual run writers,
    `docs/run-artifacts.md`, artifact schemas, restore behavior, and
    AlphaEvolve-facing boundaries for what those artifacts do and do not prove.
  - Current evidence: README lists common outputs such as `manifest.json`,
    JSONL histories, prompt/LLM call tables, `best.py`, `best_workspace/`,
    `evaluator_artifacts/`, and `plugin_artifacts/`, and links to
    `docs/run-artifacts.md` for schemas and restore details. Active code and
    paper TODOs already track many artifact internals, including manifest
    schema metadata, history rows, prompt history, archive events, evaluator
    artifacts, plugin artifacts, resume/replay boundaries, budget reports, and
    validator-boundary consistency.
  - Current gap: no README-owned validator, sidecar, or smoke transcript
    parses the README artifact list, compares it with a current no-provider
    smoke run and `docs/run-artifacts.md`, detects newly added or removed run
    outputs, or distinguishes common onboarding outputs from optional,
    provider-specific, plugin-specific, benchmark-specific, or absence-boundary
    artifacts.
  - Required result: add README run-artifact evidence that maps each listed
    output to writer code, schema/docs coverage, required or optional status,
    smoke-run presence, restore/inspection relevance, and overclaim scope; add
    a drift check that updates README/TODO evidence whenever run writers,
    artifact schemas, restore behavior, or common-output wording changes.

- [ ] Add run-artifacts guide schema and restore drift evidence.
  - Spec evidence: `docs/run-artifacts.md` is the detailed operator contract
    for `runs/` outputs, strict JSON/JSONL behavior, quarantine streams,
    manifest runtime fields, task-spec reports, prompt and LLM ledgers,
    failure history, archive restore, best exports, overwrite policy, and
    `libreevolve show` inspection semantics. AlphaEvolve-alignment work depends
    on those artifacts being truthful about what can be replayed, restored,
    certified, or treated only as absence-boundary evidence.
  - Current evidence: the root README points to `docs/run-artifacts.md` for
    schemas, quarantine streams, restore behavior, and inspection details. The
    guide contains many implementation-specific claims tied to
    `libreevolve/core/jsonl.py`, `libreevolve/core/loop.py`,
    `libreevolve/core/best_artifacts.py`, `libreevolve/cli.py`,
    artifact-schema metadata, `tests/core/test_loop.py`, and paper sidecars.
    The active README run-artifact TODO covers only the short README output
    list and smoke presence, not the full run-artifacts guide.
  - Current gap: there is no committed run-artifacts guide claim inventory or
    drift validator that maps each documented artifact, schema field, invalid
    stream, restore command, overwrite rule, show behavior, and
    AlphaEvolve-facing limitation to writer/reader code, tests, manifest
    sidecars, and active TODO owners. New runtime reports, artifact streams,
    restore semantics, quarantine policies, or inspection behavior can drift
    without a page-specific validation failure.
  - Required result: add a run-artifacts evidence map and validation gate that
    inventories documented artifact files and runtime report claims, verifies
    code/test/schema anchors and optional-versus-required status, separates
    replayable restore support from audit-only evidence, and requires
    README/docs/TODO updates whenever run artifact writers, readers, restore
    behavior, or inspection semantics change.

## Testing

- [ ] Add README testing-command marker and environment evidence.
  - Spec evidence: the README's testing commands are an onboarding and
    contribution contract. For AlphaEvolve-alignment work, local verification
    instructions should prove the intended test scope, marker behavior, and
    credential-gated integration boundary rather than only listing commands.
  - Current evidence: the README documents the non-integration command
    `py -3.12 -m pytest tests/ -m "not integration" --tb=short` and the
    credential-gated integration command
    `py -3.12 -m pytest tests/integration/ -m integration --tb=short`.
    `tests/test_agents_docs.py` checks that AGENTS.md does not pin stale test
    counts and that the non-integration command string remains present there.
    Broader CI coverage is tracked separately by
    `papers/ci_workflow_coverage_boundary.json` and active code/paper TODOs.
  - Current gap: no README-owned smoke transcript, generated sidecar, or CI
    assertion proves that the README commands themselves select the intended
    test sets, that integration tests are skipped only for missing provider
    credentials, that marker registration has not drifted, or that test
    failures can be attributed separately from paper-manifest/source-boundary
    validation.
  - Required result: add README testing-command evidence that records Python
    and pytest versions, marker registration, selected/skipped test counts,
    credential-gated integration behavior, and a drift check that updates
    README/TODO evidence whenever the documented commands or marker policy
    change.

- [ ] Add AGENTS.md operational-instruction drift evidence.
  - Spec evidence: AGENTS.md is the repository-local operating contract for
    future coding agents. During AlphaEvolve-alignment work, stale agent
    instructions can cause agents to run the wrong commands, trust obsolete
    architecture summaries, miss active TODO surfaces, or overclaim provider,
    benchmark, and paper-readiness state.
  - Current evidence: `tests/test_agents_docs.py` checks that AGENTS.md does
    not pin stale selected-test counts, includes selected artifact stream
    names, distinguishes `VALID_THRESHOLD` from MAP-Elites retention, and
    mentions several configuration-doc sampling fields. AGENTS.md currently
    summarizes the tech stack, architecture tree, key conventions, test
    commands, provider-backed run example, and common pitfalls.
  - Current gap: there is no structured AGENTS.md inventory or drift check
    comparing its architecture tree, example problem list, dependency list,
    run-artifact list, provider/backend guidance, AlphaEvolve limitation
    wording, and TODO/paper-routing guidance against README, ROADMAP,
    `docs/status.md`, `docs/configuration.md`, `docs/backends.md`,
    `papers/README.md`, the package tree, and active TODO ledgers. For
    example, AGENTS.md has a manually maintained examples list while newer
    benchmark-candidate examples and related scope boundaries live elsewhere.
  - Required result: add an AGENTS.md evidence map or validator that links each
    operational instruction to authoritative code/docs/tests/sidecar sources,
    detects stale architecture/example/dependency/provider/test-command
    wording, and requires AGENTS.md or TODO updates whenever agent-facing
    project behavior or AlphaEvolve-scope boundaries change.

## Development Docs

- [ ] Add development-guide provider example smoke evidence.
  - Spec evidence: `docs/development.md` is the contributor command contract
    for local setup, tests, and example runs. For AlphaEvolve-alignment work,
    contributor-facing provider examples should be evidence-backed just like
    README examples, because they can otherwise imply supported provider/model
    readiness or benchmark parity from placeholder commands.
  - Current evidence: `docs/development.md` tells contributors to run
    `hello_world` with `openai:<openai-model-id>`, run `circle_packing` with
    `anthropic:<anthropic-model-id>`, and then show `runs/hello_world`. It also
    tells readers to replace placeholders with currently available
    provider/account model ids. The active README provider-smoke TODO covers
    the root README examples, while the AGENTS.md drift TODO covers
    agent-facing instructions, but neither is a development-guide-specific
    check for these commands.
  - Current gap: there is no committed development-guide provider smoke
    matrix, redacted model-availability record, expected skip/failure policy,
    or docs drift check proving that the exact `docs/development.md` example
    commands are current, internally consistent, and safely separated from
    AlphaEvolve Gemini/model-mix parity. There is also no check that
    development docs update when supported provider families, placeholder
    syntax, example run names, or provider-backed smoke policy changes.
  - Required result: add a development-guide provider example inventory and
    validator or smoke artifact that maps each documented command to a
    provider family, placeholder/model-availability evidence, expected run
    directory, skip/failure mode, and README/backend-doc/paper-boundary links;
    require updates whenever provider examples or supported backend families
    change.

- [ ] Add development-guide workflow and convention drift evidence.
  - Spec evidence: `docs/development.md` is the contributor workflow contract
    for Python version expectations, editable install, pre-commit setup,
    dependency lists, `.env` behavior, unit/integration commands,
    secret-scan policy, CI coverage boundaries, paper-manifest commands,
    repository conventions, and first-read docs. AlphaEvolve-alignment work
    depends on those local verification and source-boundary instructions
    staying synchronized with actual tooling before changes are treated as
    benchmark or paper evidence.
  - Current evidence: the guide documents `py -3.12`, editable dev install,
    runtime and development dependencies, `.env` override behavior, common
    pytest and pre-commit commands, `.secrets.baseline` handling,
    path-scoped CI coverage, paper-manifest rehydrate/validation commands,
    release-smoke scope, and problem/mutation/logging/plugin conventions.
    Existing tests check selected secret-scan wording, CI workflow shape,
    release-smoke details, and a small configuration-doc subset. The active
    development-guide provider TODO covers only the provider-backed example
    run commands.
  - Current gap: there is no page-specific inventory or drift validator that
    maps each `docs/development.md` setup command, dependency list, CI claim,
    paper-manifest instruction, release-smoke statement, secret-scan policy,
    repository convention, and suggested-reading link to `pyproject.toml`,
    pre-commit config, GitHub Actions, tests, paper-manifest code, README,
    operational docs, sidecars, and active TODO owners. Changes to tooling,
    dependencies, workflow path filters, paper-cache semantics, or repository
    conventions can leave the development guide stale without a focused
    failure.
  - Required result: add a development-guide evidence map and validation gate
    that parses the guide's commands and convention bullets, verifies
    tool/config/workflow/doc anchors, separates local contributor workflow
    evidence from AlphaEvolve-grade benchmark proof, and requires
    README/docs/TODO updates whenever development setup, validation,
    paper-manifest, CI, release, or repository-convention behavior changes.

## Configuration Docs

- [ ] Add configuration-guide field and override drift evidence.
  - Spec evidence: `docs/configuration.md` is the user-facing contract for
    config precedence, problem-local `config.yaml`, `.env` loading,
    validator environment isolation, `Config` fields, CLI overrides, backend
    specs, environment variables, validation caveats, and restore limitations.
    AlphaEvolve-alignment work depends on reproducible experiment setup, so
    every documented setting should stay tied to code, tests, manifest fields,
    and explicit parity boundaries.
  - Current evidence: the guide documents defaults and semantics for many
    `Config` dataclass fields, lists CLI `run` overrides, describes backend
    spec behavior, and scopes cooperative budgets, prompt retention,
    validator isolation, archive/RNG/budget restore, and provider capability
    lookup limitations. `tests/test_agents_docs.py` currently checks only a
    small subset of configuration-doc claims, such as sampling strategy fields
    and archive-event cleanup stream wording. The active code TODO for an
    exhaustive CLI/configuration contract map covers the underlying
    code/config surface, but not the guide as a standalone documentation
    claim surface.
  - Current gap: there is no page-specific inventory or drift validator that
    parses `docs/configuration.md`, maps each documented field/default,
    allowed enum, CLI option, YAML key, manifest/provenance output,
    validation rule, restore limitation, and provider-boundary statement to
    `Config`, `cli.py`, source validators, tests, run artifacts, and active
    code/paper TODO owners. A new `Config` field, changed default, renamed
    CLI flag, altered validation behavior, or restored-runtime capability can
    drift without a configuration-guide failure.
  - Required result: add a configuration-guide evidence map and validation
    gate that checks documented fields/defaults/options against code and
    tests, links each runtime or AlphaEvolve-facing limitation to sidecars or
    TODO owners, and requires README/docs/TODO updates whenever configuration,
    CLI override, manifest, restore, provider, or validation behavior changes.

## Release Docs

- [ ] Add release-checklist documentation drift evidence.
  - Spec evidence: `docs/release-checklist.md` is a local release-smoke
    contract for build, package-content, install-from-wheel, CLI-smoke,
    provenance-file, and artifact-preservation evidence. AlphaEvolve-alignment
    work depends on keeping release and reproducibility wording separate from
    unverifiable signed-release, published-index, or maintainer-approved
    release claims.
  - Current evidence: `docs/development.md`, `docs/run-artifacts.md`,
    ROADMAP, `papers/README.md`, `papers/ci_workflow_coverage_boundary.json`,
    and `papers/release_artifact_reproducibility_boundary.json` all refer to
    the release-smoke checklist and its unsigned/unpublished scope. Tests in
    `tests/test_agents_docs.py` assert that the GitHub Actions
    `release_artifact` job builds wheel/sdist artifacts, writes
    `dist/release_artifact_provenance.json`, uploads
    `libreevolve-release-smoke-artifacts`, and that the checklist names the
    local smoke requirements.
  - Current gap: there is no page-specific inventory or drift validator that
    maps each `docs/release-checklist.md` bullet to the workflow step,
    release-provenance tool, package-content check, CLI smoke, uploaded
    artifact name, paper boundary sidecar, and active code/paper TODO owner.
    A future release workflow, artifact name, provenance schema, local command,
    or signed/published-release boundary could drift while the checklist still
    reads as authoritative.
  - Required result: add a release-checklist evidence map and validation gate
    that parses the checklist bullets, verifies workflow/tool/test/sidecar
    anchors, distinguishes local smoke evidence from signed or index-published
    release proof, and requires README/docs/TODO updates whenever release
    artifact generation, provenance schema, upload policy, or release-boundary
    wording changes.

## Contributing

- [ ] Add README contributor-gate and secret-scan evidence mapping.
  - Spec evidence: the README's contributing guidance is a workflow contract
    for changes that affect AlphaEvolve-facing source boundaries. It should be
    tied to the actual local hooks, CI jobs, source-boundary validators, and
    secret-baseline regeneration policy rather than relying on prose alone.
  - Current evidence: the README tells contributors to run focused tests, run
    the paper-manifest check when source-boundary files change, use
    `.secrets.baseline` for secret scanning, mark intentional synthetic
    provider/API failure examples with `# pragma: allowlist secret`, and stage
    regenerated baselines with the code that needs them. Existing tests check
    development docs, pre-commit config, and GitHub workflow references for
    `.secrets.baseline` and the allowlist pragma, while broader CI coverage is
    tracked separately by `papers/ci_workflow_coverage_boundary.json`.
  - Current gap: no README-owned contributor-gate inventory or validator maps
    each README contributing instruction to the specific hook, workflow, test,
    paper-manifest command, or source-boundary file it depends on. There is no
    drift check proving that README guidance changes when pre-commit hooks,
    CI path filters, detect-secrets baseline policy, or source-boundary
    validation commands change.
  - Required result: add a README contributing-policy evidence map or test
    that links each contributing sentence to concrete hook/workflow/validator
    artifacts, checks secret-scan allowlist and baseline regeneration guidance
    against current configuration, and updates README/TODO evidence whenever
    contributor gates or source-boundary validation policy changes.

## License

- [ ] Add README license and third-party rights boundary evidence.
  - Spec evidence: the README's license statement is a distribution and reuse
    claim. Because this project also caches and cites third-party AlphaEvolve
    papers, companion sources, and generated evidence artifacts, the README
    license surface should be tied to project package metadata while keeping
    third-party paper/source rights explicitly separate.
  - Current evidence: README says `MIT. See [LICENSE](LICENSE).`,
    `LICENSE` contains the MIT License text, and `pyproject.toml` declares
    `license = "MIT"`. Paper/source rights are tracked separately by records
    such as `papers/source_rights.json`, which distinguish cached
    AlphaEvolve source-PDF rights from LibreEvolve repository licensing.
  - Current gap: no README-owned validator or sidecar proves that the README
    license sentence, `LICENSE` file, package metadata, and third-party
    paper/source-rights boundaries remain consistent. There is also no drift
    check proving README license wording changes when project metadata,
    packaged license files, or paper-derived rights policies change.
  - Required result: add a README license consistency check or evidence map
    that validates the README link, license identifier, package metadata,
    included license file, and explicit separation from third-party paper and
    companion-source rights, then update README/TODO evidence whenever license
    or source-rights policy changes.
