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
    `papers/README.md`, `docs/todo/`, and `AGENTS.md`, and says setup belongs
    in the root README, operational details in `docs/`, paper-derived evidence
    in `papers/`, active/completed gap tracking in `docs/todo/` plus
    `ROADMAP.md`, tracked `old/` material is archival, and AGENTS.md is the
    agent-facing operating contract. The committed
    `papers/readme_documentation_map_boundary.json` records a README
    Documentation Map route inventory with 11 route records, target-existence
    checks, route summary marker checks, target heading marker checks,
    docs-index delegation, archival `old/` routing, and AGENTS.md routing, with
    zero missing route records.
  - Current gap: the sidecar is a bounded route inventory, not a semantic
    purpose verifier. It does not prove that each route summary fully matches
    the target document's purpose, detect newly added major docs that need
    routing, or detect content placed in the wrong surface such as paper-
    derived claims outside `papers/` or implementation priorities outside
    ROADMAP/TODO ledgers.
  - Required result: add semantic route-purpose verification, a new-major-doc
    detector, misplaced-claim detection across README/docs/papers/ROADMAP/TODO
    surfaces, and owner review signoff before treating the README
    Documentation Map as fully synchronized.

- [ ] Add README routing for `AGENTS.md` as an agent-facing operating contract.
  - Spec evidence: AlphaEvolve-alignment work in this repository is performed
    by agents as well as humans, and the tracked `AGENTS.md` file is the
    repository-local operating contract for agent runs. Because it repeats
    runtime, testing, backend, artifact, and AlphaEvolve-diff conventions, the
    root README should route it explicitly or declare why it is excluded from
    the reader-facing documentation map.
  - Current evidence: the README Documentation Map now links `AGENTS.md` as
    the agent-facing operating contract for local coding agents, `docs/README.md`
    routes contributors and coding agents to it, and `docs/development.md`
    names `AGENTS.md` inside the path-scoped CI boundary. `AGENTS.md` links
    back to `docs/development.md`, `docs/backends.md`,
    `docs/run-artifacts.md`, and `papers/README.md`.
    `papers/readme_agent_routing_boundary.json` records the README route,
    docs-index route, development-guide CI path scope, AGENTS surface,
    `tests/test_agents_docs.py` coverage, GitHub Actions `AGENTS.md` path
    filter, and bounded command/test/backend/artifact/AlphaEvolve instruction
    links.
  - Current gap: the sidecar is a routing and bounded-link inventory, not a
    complete AGENTS instruction-drift map. It does not prove that every
    overlapping command, backend, artifact, test, API, and TODO convention in
    AGENTS.md is semantically synchronized with README, docs, ROADMAP, papers,
    and code.
  - Required result: add a complete AGENTS instruction-drift map with stable
    instruction ids, source-of-truth links, per-instruction semantic checks,
    TODO-owner links for stale or intentionally divergent instructions, and
    owner review signoff before treating AGENTS.md as fully synchronized with
    the human-facing documentation set.

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
    `papers/readme_install_smoke_boundary.json` now records the exact README
    editable-install command `py -3.12 -m pip install -e ".[dev]"`, README
    Python launcher guidance, pyproject Python/dev-extra markers, GitHub
    Actions Python 3.12 setup, CI editable-install commands, and the
    development-guide editable-install command.
  - Current gap: the sidecar is a bounded marker inventory, not a clean
    environment transcript. It does not prove the documented Windows launcher
    command succeeded from a clean environment, record Python, pip, and package
    versions for that command, import-smoke dev dependencies after install, or
    classify install failures separately from provider quick-start failures.
  - Required result: add a clean-environment README install transcript or CI
    job that runs the documented editable-install command, records Python, pip,
    and package versions, smoke-imports dev dependencies, classifies install
    failures distinctly from provider/runtime failures, and records owner
    review signoff.

- [ ] Add `.env.example` provider-auth setup drift evidence.
  - Spec evidence: provider-backed AlphaEvolve-style runs depend on repeatable,
    secret-safe credential setup before model calls, benchmark attempts, or
    integration tests can be interpreted. The README, backend docs, and
    example environment file should agree on which provider environment
    variables exist, which providers require them, which values are
    placeholders, and which secrets must never be committed.
  - Current evidence: README says optional provider credentials live in
    `.env`, provider-backed runs can fail when credentials, model ids, local
    Ollama state, or account access are unavailable, and integration tests
    require provider credentials. `docs/backends.md` and
    `docs/configuration.md` document `.env` loading with `override=True`,
    provider credential names, non-secret dotenv provenance, and credential
    preflight for OpenAI and Anthropic. `.env.example` currently lists
    `OPENAI_API_KEY=sk-your-openai-key-here`,
    `ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here`, and
    `OLLAMA_HOST=http://localhost:11434`. Separate TODOs already cover broad
    provider smoke wording, backend-guide drift, contributor secret-scan
    mapping, and CLI-authenticated provider overclaiming.
    `papers/readme_provider_auth_boundary.json` now records the `.env.example`
    provider variables, placeholder safety, README provider-auth guidance,
    backend/configuration/development dotenv markers, CLI dotenv override and
    credential-preflight markers, integration-test credential skip markers,
    GitHub Actions Anthropic secret markers, and the secret-scan baseline
    marker.
  - Current gap: the sidecar is a bounded static marker inventory, not a
    semantic provider-auth drift gate. It does not parse the backend registry
    to prove every supported auth lane is represented, perform live
    provider-account probes, enforce a CI gate for provider-auth drift, or
    record owner review signoff. A provider can still be added, removed,
    renamed, or moved to a different authentication lane while `.env.example`,
    README quick-start guidance, backend docs, and secret-scan expectations
    drift independently outside the recorded marker set.
  - Required result: add a provider-auth setup evidence map or test that parses
    `.env.example`, verifies each variable against backend/config docs and
    credential preflight code, rejects real-looking committed secrets while
    allowing documented placeholders, links integration-test credential needs,
    and requires README/docs/TODO updates whenever provider auth, dotenv
    loading, placeholder policy, or secret-scan handling changes.

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
    `papers/related_work_taxonomy_boundary.json` now records bounded
    AlphaEvolve Section 5 Related Work taxonomy rows and scoped README/ROADMAP
    claim gates. `papers/readme_paper_cache_topic_boundary.json` now records
    the README paper-cache topic sentence, download-manifest row count, papers-
    index implementation-status row count, papers-index role inventory, and
    bounded heuristic topic-family signals for LLM-guided evolution, program
    synthesis, quality-diversity optimization, and related benchmarks.
  - Current gap: the sidecar is a bounded marker and heuristic-signal
    inventory, not a reviewed topic taxonomy. There is still no committed
    row-level topic taxonomy proving which cached papers belong to the
    README-listed topic families, no semantic validator checking README topic
    wording against paper-index categories, and no drift report when new papers
    fall outside those categories or when the README topic sentence changes.
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
    `papers/readme_paper_cache_rehydrate_boundary.json` now records the README
    and papers-index rehydrate commands, manifest row count, paper-manifest CLI
    flags, rehydrate report fields, missing-PDF download test, existing-PDF
    skip test, force-redownload test, and redacted network-failure test.
  - Current gap: the sidecar is a bounded command and test-marker inventory,
    not a clean-checkout transcript. No committed README-owned CI/manual run
    artifact proves the exact README `--rehydrate` command from a clean
    checkout with an absent PDF cache, records a live network outcome matrix,
    confirms all downloaded files match manifest hashes in one retained
    transcript, or separates rehydrate drift from ordinary local-cache
    validation with owner signoff.
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

- [ ] Add docs-index reader-path and boundary drift evidence.
  - Spec evidence: `docs/README.md` is the documentation directory's routing
    contract for new users, operators, contributors, and paper/spec reviewers.
    It also defines which claims belong in the root README, operational
    guides, `docs/status.md`, ROADMAP, TODO ledgers, `papers/README.md`, and
    paper sidecars. AlphaEvolve-alignment work depends on this routing page
    staying current so implementation, roadmap, and paper-boundary claims do
    not move to the wrong surface.
  - Current evidence: `docs/README.md` links the root README, problem format,
    run artifacts, configuration, backends, development, status, ROADMAP,
    `papers/README.md`, and `docs/todo/`, and it states that
    AlphaEvolve-alignment cleanup is a whole-documentation task. The active
    README documentation-map TODO covers the root README's `Documentation Map`,
    while `papers/documentation_truthfulness_boundary.json` records
    docs/README routing as broad boundary evidence.
    `papers/docs_index_reader_path_boundary.json` now records `docs/README.md`
    reader paths, operational-guide routes, documentation-boundary markers,
    route target existence checks, target heading marker checks, and the
    whole-documentation AlphaEvolve-alignment cleanup marker.
  - Current gap: the sidecar is a page-specific route and marker inventory,
    not a semantic drift validator. It does not prove that route descriptions
    match target document scope, flag newly added major docs that need index
    placement, detect paper-derived claims outside `papers/`, or detect
    long-term roadmap work outside ROADMAP/TODO ledgers.
  - Required result: add a docs-index evidence map and validation gate that
    inventories reader paths, operational guide entries, and documentation
    boundary bullets; verifies link existence and target-scope agreement; and
    requires README/docs/TODO updates whenever documentation surfaces, route
    ownership, or AlphaEvolve-facing claim boundaries change.

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
    tracks selected README/ROADMAP/papers-index claims plus a structural
    `docs/status.md` ledger inventory for implemented/limit bullet spans,
    hashes, status-signal terms, and local backtick-path existence records.
    `papers/docs_status_ledger_boundary.json` now adds a narrower
    status-ledger freshness boundary that checks the status heading,
    implemented/limit bullet counts, local path refs, README/docs-index/
    papers-index/TODO route markers, documentation-claim status fields, and
    `papers/status_claim_inventory.json` summary fields.
    Existing paper status-claim inventory validation checks
    `papers/README.md` row claims in much more detail than the larger
    `docs/status.md` ledger.
  - Current gap: the structural inventory does not yet map each implemented
    and missing-status bullet to source modules, tests, ROADMAP entries, paper
    sidecars, active/completed TODO anchors, and `papers/README.md` rows, or
    detect stale status prose when code, ROADMAP, paper status rows, or TODO
    coverage changes. The new status-ledger sidecar catches structural drift
    and route/count freshness, but the README's "full implemented-versus-
    missing ledger" claim is still weaker than the paper-index row-level
    status inventory.
    A resolved narrow drift example is embedded-evaluator status wording:
    after the embedded-evaluator TODOs were tightened, active code/paper TODOs
    named the missing generated/interactive task-input replay contract for
    `evaluate(eval_inputs)` and external validators, while `docs/status.md`
    summarized the embedded evaluator boundary only as default loading, Figure
    3 fixture identity, typed eval-input contracts beyond JSON-safe config,
    build/runtime isolation, and non-static/external-validator causal linkage.
    The status ledger now includes the generated/interactive task-input replay
    policy gap shared across embedded and external-validator stages, but the
    broader semantic freshness matrix is still missing.
    A resolved narrow drift example is the top-level `docs/status.md` run-
    artifact bullet: it previously summarized `runs/` outputs only as
    manifests, histories, prompts, failures, best candidates, and
    plugin/evaluator artifacts, while active code/paper TODOs identified
    generated `prompt_current_binding_table.jsonl`,
    `prompt_prior_score_table.jsonl`, and `paper_artifacts/...` as documented
    or emitted run artifacts whose collision/overwrite lifecycle is not yet
    unified. The status ledger now names the prompt-table artifacts and keeps
    the unified collision/overwrite, artifact-hash, schema, restore, and
    `show` inspection proof as an explicit open paper-facing lifecycle
    boundary.
    A resolved narrow drift example is backend support: `docs/status.md`
    previously listed only OpenAI, Anthropic, and Ollama under "Implemented
    today", while the root README and `docs/backends.md` described custom
    import-path backends as supported. The status ledger now includes
    configured custom import-path backend support in the implemented list,
    while the provider-limit paragraph still preserves the missing
    first-class Gemini and CLI/Codex-authenticated provider-lane boundary.
    A resolved narrow drift example is generated-inventory count freshness:
    after the paper-index TODO coverage update, the current
    `papers/status_claim_inventory.json` recorded `950` row-specific TODO
    block records and `291` TODO content artifact mention records while
    `docs/status.md` still reported `1048` and `404`. The paper-manifest gate
    now checks matching `docs/status.md` summaries for those generated
    sidecar counts, and the documentation-claim inventory now records
    status-ledger bullet structure, but this is only structural/count coverage;
    the broader status-ledger evidence mapping and cross-surface freshness
    matrix are still missing.
  - Required result: extend the status-ledger freshness artifact into a
    semantic validator that links each `docs/status.md` claim to current
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
    `papers/readme_repository_layout_boundary.json` now records 13 README
    layout entries, path-existence checks, summary-marker checks, module
    evidence paths, the `llm/` custom-backend marker, archival `old/` scope,
    and gitignored `runs/` scope.
  - Current gap: the committed layout inventory still does not semantically
    validate that each role summary is accurate, flag new top-level packages
    or docs that should be mentioned, or distinguish implemented module roles
    from AlphaEvolve-parity placeholders.
    Current drift evidence: the README `Runnable today` list says LibreEvolve
    supports OpenAI, Anthropic, Ollama, and custom import-path backends, and
    the docs map links `docs/backends.md` for "provider adapters and custom
    backends"; the repository-layout block previously described `llm/` as
    only "OpenAI, Anthropic, Ollama, and ensemble routing." That narrow drift
    is fixed: the layout now names custom backends, and the sidecar fails if
    the marker disappears.
  - Required result: extend the README layout/schema drift check into a
    semantic role verifier that maps each role summary to concrete
    modules/docs/tests, flags new top-level packages or major docs, classifies
    AlphaEvolve-parity placeholders, and updates README/TODO evidence whenever
    module ownership or layout changes.

- [ ] Add architecture-guide runtime-flow drift evidence.
  - Spec evidence: `docs/architecture.md` is the detailed end-to-end runtime
    contract for CLI setup, problem loading, candidate representation,
    mutation application, evolution-loop ordering, prompt sampling,
    evaluation, plugins, MAP-Elites, persistence, restore, and known
    limitations. For AlphaEvolve-alignment work, that architecture guide must
    stay synchronized with the actual implementation and keep local candidate-
    async behavior separate from AlphaEvolve async/distributed parity.
  - Current evidence: the root README and `docs/README.md` route readers to
    `docs/architecture.md` for runtime architecture. The guide contains many
    code-specific claims, including `.env` loading boundaries, configured
    plugin resolution, candidate path safety, proposal-loop ordering,
    critique/feedback sequencing, prompt-context behavior, evaluator
    preflight, archive restore, controller-state snapshots, and scoped local
    candidate-async limitation bullets. Active TODOs already cover README repository-layout
    drift, `docs/status.md` ledger freshness, ROADMAP readiness criteria, and
    paper-facing async/topology boundaries, but not the architecture guide as
    a standalone operational contract.
    `papers/docs_architecture_runtime_flow_boundary.json` now records ten
    architecture sections, runtime-flow markers, source path checks,
    README/docs-index route markers, the active TODO owner anchor, known-gap
    markers, the local candidate-async runtime boundary, and the AlphaEvolve provider-
    parity boundary.
  - Current gap: the committed architecture inventory still does not map each
    `docs/architecture.md` flow step, limitation, and component-role statement
    to concrete source functions, tests, runtime manifest fields, sidecars, and
    active TODO owners. Hook order, restore semantics, prompt/evaluator
    surfaces, archive behavior, plugin behavior, or runtime-budget claims can
    still drift without semantic flow-order or field-level source-offset proof.
  - Required result: extend the architecture-guide evidence map into a
    semantic validation gate that inventories each major architecture claim
    with code/test/runtime anchors, flags unsupported or AlphaEvolve-facing
    parity claims separately, and requires README/docs/TODO updates when
    implementation flow, persistence semantics, or architecture limitations
    change.

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
    `Best fitness: 1.000000`. `papers/readme_quick_start_smoke_boundary.json`
    now records the README command markers, expected run name/problem path,
    `max_llm_calls` stop reason, `Best fitness` output, provider-preflight
    skip policy, and focused smoke-test markers. The focused test executes the
    documented no-provider path and validates the manifest plus `show` output.
  - Current gap: the successful run artifacts still live under gitignored
    `runs/`, and the focused smoke test is not yet wired into a CI job or
    retained as a cross-platform/fresh-checkout shell transcript.
  - Required result: extend the committed smoke proof into CI or transcript
    evidence that runs the README no-provider quick-start path in a fresh
    checkout, validates expected stop reason and `show` output fields, and
    updates README/TODO evidence when the command changes.

- [ ] Add provider-backed README example smoke matrix.
  - Spec evidence: AlphaEvolve depends on a managed model mix and provider
    capability, while LibreEvolve's README shows provider-backed run examples
    for OpenAI, Anthropic, and Ollama. Those examples should be kept honest
    with provider-specific availability evidence rather than only placeholder
    model ids.
  - Current evidence: the README explicitly tells users to replace
    `<openai-model-id>`, `<anthropic-model-id>`, and
    `<installed-ollama-model>` with models available to their account or local
    install, and warns that provider-backed runs may fail.
    `papers/readme_provider_example_matrix_boundary.json` now records those
    README command markers, account/local-model guidance, provider
    failure-scope wording, `.env.example` provider placeholders, CLI
    `type:model` shorthand construction, built-in OpenAI/Anthropic credential
    preflight markers, custom-backend `class_path`/`kwargs` contract markers,
    configuration-guide shorthand markers, and the Anthropic-only
    credential-gated integration-test skip marker.
  - Current gap: the committed provider-example matrix is static boundary
    evidence only. It does not prove live OpenAI model availability, live
    Anthropic model availability, local Ollama inventory, a credential-safe
    provider smoke matrix, account-specific model-id provenance, a CI provider
    matrix, or Google/Gemini AlphaEvolve provider parity. The current
    `tests/integration/test_hello_world.py` coverage remains credential-gated
    on `ANTHROPIC_API_KEY`; it does not prove the README OpenAI example,
    Ollama example, account-specific model ids, or equal provider-command
    parity.
  - Required result: extend the static provider-example matrix into
    provider-family smoke evidence with safe credential handling,
    account/local model id provenance, expected skip/failure modes, CI/report
    artifacts, and README/TODO updates whenever provider example commands or
    supported backend families change.

- [ ] Keep README guardrails for experimental subprocess/CLI-authenticated LLM
      providers.
  - Spec evidence: AlphaEvolve-style experiments rely on auditable provider
    calls and model-mix claims. A README feature bullet for backend support
    should distinguish built-in SDK adapters, generic custom import-path
    backends, and any future local authenticated CLI provider before readers
    use README commands or benchmark prompts as evidence of first-class
    provider support.
  - Current evidence: the README currently lists OpenAI, Anthropic, Ollama,
    experimental Codex CLI, and custom import-path backend support; the
    quick-start provider examples show only OpenAI, Anthropic, and Ollama
    placeholders. The README now states that `type: codex` is an experimental
    authenticated `codex exec` lane with redacted auth/session provenance and
    optional transcripts, while credential-safe live smoke evidence, model
    availability preflight, manifest/report integration, provider-native
    token/cost accounting, and parity diagnostics remain open work in
    `docs/todo/code.md`. It also keeps custom import-path backends framed as
    extension points. `papers/readme_cli_provider_guardrail_boundary.json`
    records that README wording, the code TODO contract markers, backend-doc
    built-in/custom/Codex lane markers, and a narrow scan for unsupported
    positive Codex/local CLI benchmark-parity claims in README, ROADMAP, and
    papers/README.
  - Current gap: the guardrail now reflects a real experimental Codex adapter,
    but it does not prove benchmark-claim-ready provider parity. The remaining
    gaps are credential-safe live smoke evidence, CLI backend manifest/report
    integration, provider budget accounting for CLI backends, model
    availability preflight, and provider diagnostics for CLI backends. A user
    can still create an ad hoc custom wrapper around another local CLI, but
    that remains outside supported, reproducible provider parity until it has a
    documented lane and telemetry.
  - Required result: keep README, ROADMAP, benchmark, and paper-facing wording
    limited to experimental Codex CLI plumbing until the subprocess/CLI
    provider contract has live smoke evidence, auth/session provenance,
    transcript retention, diagnostics, budget/cancellation semantics,
    CI/report artifacts, and manifest validation.

- [ ] Keep backend-doc guardrails for experimental CLI-authenticated provider
      support.
  - Spec evidence: `docs/backends.md` is the detailed provider contract that
    users will follow when choosing between built-in SDK adapters and custom
    extension points. It should make the current backend boundary clear before
    benchmark prompts or local experiments rely on Codex-authenticated or other
    local CLI sessions as if they were first-class supported providers.
  - Current evidence: `docs/backends.md` now has a provider-lane taxonomy that
    separates built-in SDK adapters, the experimental built-in Codex CLI
    adapter, custom import-path backends, and unsupported local CLI wrappers.
    It documents `CodexCLIBackend` constructor fields, auth/session provenance,
    stdin/`--output-last-message` transport, transcript schema, timeout
    behavior, JSON-output extraction, and the current lack of live smoke,
    model preflight, provider-native token/cost accounting, manifest/report
    integration, and parity diagnostics. `papers/backend_cli_provider_guardrail_boundary.json`
    records that taxonomy, the Codex limitation wording, the code TODO link,
    README TODO ownership, and a narrow scan for unsupported positive
    Codex/local CLI benchmark-parity claims across backend, configuration,
    README, ROADMAP, and papers-index claim surfaces.
  - Current gap: the backend-doc guardrail now describes a real adapter, but it
    remains boundary evidence rather than claim-ready benchmark evidence. The
    guide still cannot make Codex-authenticated or other local CLI providers
    part of paper-facing model-mix parity until live smoke fixtures, manifest
    fields, model availability preflight, provider-attempt accounting, and
    provider diagnostics exist.
  - Required result: complete the subprocess/CLI backend contract with
    manifest fields, diagnostics, provider-attempt accounting,
    timeout/cancellation behavior, auth/session provenance, transcript policy,
    model availability preflight, and credential-safe smoke fixtures; keep
    backend docs, README, ROADMAP, benchmark prompts, and paper-facing
    materials from claiming benchmark-ready support until that evidence exists.

- [ ] Add backend-guide provider contract drift evidence.
  - Spec evidence: `docs/backends.md` is the detailed operational contract for
    provider selection, scheduler/reward accounting, retry/fallback behavior,
    provider failure telemetry, prompt and response caps, role routing,
    OpenAI API-mode policy, Anthropic/Ollama adapter behavior, custom backend
    construction, credential preflight, client-context provenance, and
    Google/Gemini partial-readiness boundaries. AlphaEvolve-alignment work depends on
    this page staying synchronized with actual backend/runtime behavior before
    any model-mix, provider, or scheduling claim is treated as evidence.
  - Current evidence: the guide documents `LLMEnsemble` accounting, bounded
    call-history retention, durable `llm_calls.jsonl` replay, scheduler
    restore, prompt validation, built-in adapter defaults, role-scoped
    backend routing, failure quarantine, retries, timeouts, prompt-token
    limits, OpenAI Chat/Responses routing, request-parameter surfaces,
    `llm_prompt_roles`, custom backend `class_path` specs, `.env` credential
    behavior, Gemini provider partial-readiness records, and the backend
    CLI-provider guardrail. `papers/backend_guide_contract_drift_boundary.json`
    now records backend-guide section and claim markers for those surfaces and
    maps them to source-module, focused-test, sidecar, and active TODO anchors.
    A current cross-doc drift example remains backend role routing:
    `docs/backends.md` says `llm_role_backend_indices` can route call roles to
    explicit backend-index lanes and that roles without explicit routes can
    still use backend metadata `role` lanes, while `docs/configuration.md`
    still says the backend `role` field is descriptive metadata only and "not
    yet used for quotas, escalation, or role-specific routing." The code and
    tests now validate `llm_role_backend_indices` and metadata fallback
    routing, so the configuration prose can understate implemented routing and
    confuse the remaining gap, which is richer quotas/escalation and stronger
    AlphaEvolve model-mix evidence.
  - Current gap: the committed backend-guide map is structural evidence only.
    It does not semantically verify every backend-guide claim, constructor
    field, allowed parameter, telemetry field, timeout/retry rule, scheduler
    policy, OpenAI route rule, custom-backend limitation, environment/preflight
    statement, or AlphaEvolve-facing provider boundary. It also is not a
    backend-docs CI drift gate or owner review signoff.
  - Required result: extend the backend-guide map into semantic and per-field
    validation that parses provider sections and practical guidance, verifies
    code/test/artifact anchors for each documented claim, separates built-in
    SDK support from custom-extension and missing Gemini/Codex-provider parity,
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
    It also documents external plugin entry points under the
    `libreevolve.plugins` group, constructor option schemas, captured
    constructor options, distribution name/version hashes, hash-only
    `RECORD` / `WHEEL` summaries, and the direct-plugin policy distinction
    between entry-point packages and explicit direct plugin instances.
    `papers/plugin_guide_contract_drift_boundary.json` now records a
    structural map of guide section, hook, execution-order, score/admission,
    artifact, fatal-failure, built-in plugin, entry-point, constructor-schema,
    package-provenance, and direct-plugin policy markers to `PluginBase`, the
    registry, loop, config, built-in plugin modules, focused tests, sidecars,
    and active TODO anchors.
  - Current gap: the committed sidecar is structural evidence only. There is
    still no semantic verifier for every plugin-guide claim, no per-hook
    executable trace proving exact runtime order and manifest payloads, no
    per-built-in plugin capability matrix, no CI drift gate scoped to plugin
    docs, and no owner review signoff. Future hook-order, plugin config schema,
    score/admission, entry-point provenance, direct-plugin policy, or built-in
    plugin capability changes can be detected by the marker map only when their
    documented/code anchors move or disappear.
  - Required result: add semantic plugin-guide claim verification, per-hook
    executable trace artifacts, and a plugin-docs CI drift gate that requires
    README/TODO updates when plugin runtime behavior or built-in plugin evidence
    changes.

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
    `papers/readme_problem_layout_boundary.json` now records a structural map
    from the README problem-layout block to required/optional file markers,
    `docs/problem-format.md`, loader/config/evaluator anchors, example problem
    path checks, focused loader/example test anchors, AlphaEvolve
    problem-surface sidecars, and active TODO ownership. The README now also
    names `seed_policy.yaml` primary selection and provides a provider-free
    `candidate_runner_expression` run/show smoke command and a compiler-gated
    `candidate_runner_c` run/show command with explicit replay limits.
  - Current gap: the committed sidecar is structural evidence only. It does not
    prove every loader branch or problem-format claim semantically, does not
    add a dedicated minimal-problem smoke fixture, does not validate the full
    long-form `docs/problem-format.md` contract, and does not detect every new
    problem surface that should be mentioned or explicitly scoped out in the
    root README.
  - Required result: add semantic loader-contract verification, a dedicated
    minimal-problem smoke fixture, a problem-format long-contract drift gate,
    and a new problem-surface detector that requires README/TODO updates when
    problem-loading, evaluator, context, metrics, config, candidate-workspace,
    or example layout semantics change.

- [ ] Add problem-format guide loader-contract drift evidence.
  - Spec evidence: `docs/problem-format.md` is the full problem-authoring
    contract that readers are sent to after the root README. It specifies the
    required layout, context manifest semantics, codebase-integration metadata,
    task and metrics files, validator signatures, configured evaluator stages,
    language/build-runner declarations and executable stage bindings, seed
    workspaces, seed policies, and the remaining AlphaEvolve-facing limits.
  - Current evidence: `papers/problem_format_loader_contract_boundary.json`
    now records `docs/problem-format.md` section and claim markers for required
    layout, context manifests, codebase-integration metadata, task and metrics
    files, validator signatures, configured evaluator stages, candidate runner
    declarations, evaluation semantics, seed workspaces, seed policy, mutation
    modes, and the local-runner security/parity scope. It also records loader/config/
    evaluator anchors, focused loader/evaluator/example test anchors, example
    path anchors, related sidecar anchors, and TODO owner anchors.
  - Current gap: the new boundary is still structural evidence. It does not
    semantically execute every problem-format claim, does not trace every
    manifest key to executable coverage, does not run as a dedicated docs CI
    drift gate, does not detect every newly introduced problem surface, and
    does not include owner review signoff. Changes to `context.yaml`,
    `seed_policy.yaml`, embedded evaluator stages, metrics semantics, or
    candidate-language/build execution can therefore still require manual
    interpretation beyond the structural marker checks. The checked expression,
    host C, and digest-pinned OCI Python fixtures cover three bounded paths, not
    every declared command, platform, daemon, package manager, or toolchain.
  - Required result: add a semantic problem-format claim verifier,
    per-manifest-key executable traces, docs CI drift gating, new
    problem-surface detection, and owner review signoff that require
    README/docs/TODO updates when problem-loading or evaluator semantics
    change.

## Example Scope

- [ ] Add README example-scope drift and benchmark-claim evidence.
  - Spec evidence: the README's `Example Scope` section is the first guardrail
    separating smoke fixtures, benchmark candidates, and paper-comparable
    evidence. That distinction is central to AlphaEvolve-alignment truthfulness
    because examples can otherwise be mistaken for reproduced benchmark
    results.
  - Current evidence: `papers/readme_example_scope_boundary.json` now records
    README section markers, the shipped-example scope registry, the committed
    `papers/example_benchmark_scope.json` sidecar, example path existence,
    smoke and benchmark-candidate classifications, the non-comparable
    `candidate_runner_expression`, `candidate_runner_c`, and
    `candidate_runner_python_oci` contract fixtures,
    sorting-network boundary
    anchors, benchmark fixture-readiness anchors, hardening and validator test
    anchors, status/papers index anchors, and active TODO ownership. It
    preserves the current split between nine smoke fixtures and two
    non-comparable benchmark candidates, with zero shipped examples marked as
    paper-comparable.
  - Current gap: the new boundary is structural evidence only. It does not
    semantically verify every scope sentence, compare runtime
    `benchmark_fixture_readiness_report` records against README wording,
    enforce paper-comparable certification gates, detect every newly added
    example surface, or include owner review signoff. A smoke fixture,
    benchmark candidate, or paper-comparable claim can therefore still require
    manual review beyond marker/registry/path checks.
  - Required result: add semantic scope-claim verification, runtime metadata
    comparison, paper-comparable certification gating, new example-surface
    detection, and owner review signoff so README, problem docs, ROADMAP,
    papers, and runtime metadata cannot promote smoke examples or benchmark
    candidates into paper-comparable claims until the mapped evidence exists.

- [ ] Add example-runs README fixture-claim drift evidence.
  - Spec evidence: `examples/runs/README.md` is a reader-facing evidence
    surface for curated run fixtures. Its per-run record counts, behavior
    summaries, and `libreevolve show` inspection commands should stay true
    while remaining clearly scoped away from full current run-artifact or
    AlphaEvolve-comparable result evidence.
  - Current evidence: `papers/readme_example_runs_boundary.json` now records
    `examples/runs/README.md` markers, checked-in fixture history row counts,
    best-program markers, legacy artifact presence, modern artifact absence,
    documented `show` commands, CLI legacy-show anchors, run-artifacts guide
    anchors, focused CLI show test anchors, and active TODO ownership. The
    focused test invokes both documented `py -3.12 -m libreevolve show
    examples/runs/...` commands and checks legacy history-only status plus
    selected best-program output.
  - Current gap: the new boundary still does not retain show-command execution
    transcripts as committed artifacts, semantically verify every fixture
    behavior narrative, compare these directories with the current complete
    run-artifact schema, prove AlphaEvolve-level reproducibility, or include
    owner review signoff. The neutral-drift and immediate-improvement claims
    therefore remain structurally anchored but not semantically certified.
  - Required result: add retained show-command transcripts, per-fixture
    behavior semantic verification, current run-artifact parity checks,
    explicit AlphaEvolve-reproducibility boundaries, and owner review signoff
    for the checked-in example histories.

## Run Artifacts

- [ ] Add README run-artifact list drift and scope evidence.
  - Spec evidence: the README's `Run Artifacts` section is an onboarding and
    inspection contract for the local evolutionary runtime. Its list of common
    files and directories should stay synchronized with actual run writers,
    `docs/run-artifacts.md`, artifact schemas, restore behavior, and
    AlphaEvolve-facing boundaries for what those artifacts do and do not prove.
  - Current evidence: `papers/readme_run_artifacts_boundary.json` now records
    README section markers, the 14 common-output entries, run-artifacts guide
    anchors, the `RUN_ARTIFACT_NAMES` cleanup set from
    `libreevolve/core/database.py`, README-vs-cleanup mismatch lists,
    documented scope omissions for `task_specification.json`, invalid/
    quarantine streams, and `paper_artifacts/`, overwrite-cleanup test anchors,
    quick-start smoke artifact anchors, sidecar anchors, and active TODO
    ownership. It now records an empty README-common-without-cleanup list after
    `prompt_current_binding_table.jsonl` and
    `prompt_prior_score_table.jsonl` were added to cleanup ownership, and it
    records `paper_artifacts` as cleanup-owned while still documented outside
    the README common-output list. Task-specification and invalid/quarantine
    streams remain detailed-guide or cleanup-owned surfaces outside the README
    common-output list.
  - Current gap: the new boundary is still structural. It does not run a fresh
    smoke-run artifact presence matrix, map every artifact to writer/reader
    code and schema validators, prove restore/show lifecycle behavior,
    classify every optional artifact family, or include owner review signoff.
    The README can therefore stay synchronized at the short-list level while
    deeper writer/schema/restore semantics still need page-specific proof.
  - Required result: add fresh smoke-run artifact presence evidence, complete
    artifact writer/reader/schema mapping, restore/show lifecycle proof,
    optional artifact classification gates, and owner review signoff; require
    README/docs/TODO updates whenever run writers, artifact schemas, restore
    behavior, or common-output wording changes.

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
    `papers/documentation_claim_inventory.json` now structurally records the
    guide's top-level documented artifact names, the current
    `RUN_ARTIFACT_NAMES` overwrite-cleanup set, and the documented-without-
    cleanup inventory. The prompt-table cleanup mismatch for
    `prompt_current_binding_table.jsonl` and
    `prompt_prior_score_table.jsonl` is now resolved in
    `RUN_ARTIFACT_NAMES`, and `paper_artifacts` is also cleanup-owned.
    Its artifact tree includes `task_specification.json`,
    `prompt_current_binding_table.jsonl`, and
    `prompt_prior_score_table.jsonl`, and later sections document
    `paper_artifacts/...` source/exhibit outputs. The guide's run-directory
    reuse section now lists the known artifacts checked for collision/
    overwrite cleanup, including task specification, prompt-table exports,
    invalid/quarantine streams, controller/LLM streams, and `paper_artifacts`.
    It also documents `manifest.json.artifact_schema.quarantine_jsonl_records`
    for invalid/quarantine stream schema mapping. The active README
    run-artifact TODO covers only the short README output list and smoke
    presence, not the full run-artifacts guide.
    The previous prompt-table cleanup mismatch and collision-list omission are
    resolved, but the guide still needs a page-specific semantic evidence map
    for all writers, readers, schemas, restore behavior, and inspection
    behavior.
  - Current gap: the committed structural inventory does not yet map each
    documented artifact, schema field, invalid stream, restore command,
    overwrite rule, show behavior, and AlphaEvolve-facing limitation to
    writer/reader code, tests, manifest sidecars, and active TODO owners. New
    runtime reports, artifact streams,
    restore semantics, quarantine policies, collision/overwrite cleanup lists,
    or inspection behavior can drift without a page-specific semantic
    validation failure.
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
    `papers/readme_testing_boundary.json` now records the README command
    markers, pytest testpaths and integration marker registration, GitHub
    Actions non-integration and credential-gated integration commands,
    Anthropic-key skip wiring, integration-test skip decorators, AGENTS.md
    command anchors, CI workflow sidecar anchors, and this active TODO owner.
  - Current gap: the README-owned sidecar is structural evidence, not a smoke
    transcript. It does not record Python and pytest versions, selected or
    skipped test counts for the documented commands, credential-skip
    transcript proof, a failure-attribution matrix that separates pytest
    failures from paper-manifest/source-boundary validation, or owner review
    signoff.
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
    `papers/readme_agents_operational_boundary.json` now records the current
    AGENTS.md example-directory and run-artifact-list drift, plus README,
    run-artifacts guide, backend/configuration/paper-doc, focused-test,
    GitHub Actions path-filter, and active TODO anchors.
  - Current gap: the structured AGENTS.md inventory is a bounded static drift
    record, not a complete instruction-to-source map or semantic drift check
    comparing its architecture tree, example problem list, dependency list,
    run-artifact list, provider/backend guidance, AlphaEvolve limitation
    wording, and TODO/paper-routing guidance against README, ROADMAP,
    `docs/status.md`, `docs/configuration.md`, `docs/backends.md`,
    `papers/README.md`, the package tree, and active TODO ledgers. The
    recorded drift currently shows that the actual
    `libreevolve/problems/examples/` directory includes
    `embedded_evaluate_math`, `sorting_network_8`, and `sorting_network_9`,
    while AGENTS.md's architecture block still lists only `hello_world`,
    `circle_packing`, `sorting`, `matrix_multiplication`, and
    `workspace_math`. Its `runs/` summary also omits current run artifacts
    such as `controller_budget_events.jsonl`, `evaluator_results.jsonl`,
    `prompt_current_binding_table.jsonl`, `prompt_prior_score_table.jsonl`,
    and `task_specification.json`, even though README and
    `docs/run-artifacts.md` now document those surfaces. Dependency-list
    semantic checking, provider-guidance semantic checking, full AlphaEvolve-
    scope semantic checking, and owner review signoff remain missing.
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
    `hello_world` with `openai:<openai-model-id>` and `circle_packing` with
    `anthropic:<anthropic-model-id>` using explicit development run names,
    overwrite cleanup, and paired `show` commands for both run directories. It
    also tells readers to replace placeholders with currently available
    provider/account model ids. The active README provider-smoke TODO covers
    the root README examples, while the AGENTS.md drift TODO covers
    agent-facing instructions.
    `papers/development_provider_example_boundary.json` now records a
    development-guide-specific static inventory for those two commands,
    placeholder model-id guidance, README provider model/failure wording,
    docs-index/backend/status/paper anchors, provider-matrix/auth/Gemini
    sidecar references, active TODO ownership, explicit run-name/overwrite
    markers, and paired show-command coverage for both provider examples.
  - Current gap: the committed sidecar is a static documentation inventory, not
    a live provider smoke matrix, redacted model-availability record, expected
    skip/failure policy, or CI drift check proving that the exact
    `docs/development.md` example commands are current, internally consistent,
    and safely separated from AlphaEvolve Gemini/model-mix parity. There is
    also no live check that development docs update when supported provider
    families, placeholder syntax, example run names, or provider-backed smoke
    policy changes.
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
    run commands. `papers/development_workflow_boundary.json` now records a
    page-specific static inventory for Python launcher guidance, editable
    install, pre-commit setup, `.env` behavior, test/pre-commit/diff/paper-
    manifest commands, CI scope, release-checklist routing, dependency lists,
    repository conventions, suggested contributor docs, `pyproject.toml`,
    `.pre-commit-config.yaml`, GitHub Actions, focused agent-doc tests, and
    this active TODO owner.
  - Current gap: the page-specific inventory is a static marker drift record,
    not a semantic validator or executable transcript suite. It does not map
    each `docs/development.md` setup command, dependency list, CI claim,
    paper-manifest instruction, release-smoke statement, secret-scan policy,
    repository convention, and suggested-reading link to a command transcript,
    dependency-version semantic map, CI path-filter semantic proof, fresh-
    checkout paper-manifest transcript, release-smoke transcript, repository-
    convention source map, or owner review signoff. Changes to tooling,
    dependencies, workflow path filters, paper-cache semantics, or repository
    conventions can still leave the development guide semantically stale
    without a complete focused failure.
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
    claim surface. `papers/configuration_guide_boundary.json` now records a
    page-specific static inventory for precedence, `config.yaml` provenance,
    `.env` behavior, validator environment/network policy, representative
    `Config` fields, CLI override markers, backend/provider capability policy,
    OpenAI API-mode policy, focused agent-doc tests, status/paper sidecar
    anchors, this active TODO owner, resolved CLI-option records for the
    current `run` command surface, and resolved `runtime.llm_accounting`
    wording that routes live cooperative stop enforcement to the top-level
    `runtime.budget` snapshot.
  - Current gap: the page-specific inventory is a static marker record, not a
    semantic configuration verifier. It does not parse `docs/configuration.md`
    into a complete field/default map, complete CLI option-to-config map,
    YAML-key validation semantic map, manifest/provenance field map, restore-
    capability semantic map, CI configuration-doc drift gate, or owner review
    signoff. A new `Config` field, changed default, renamed CLI flag, altered
    validation behavior, or restored-runtime capability can still drift
    without a complete configuration-guide failure.
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
    `papers/release_checklist_documentation_boundary.json` now records the
    checklist's required local evidence bullets, out-of-scope release-proof
    bullets, release-artifact workflow markers, release-provenance tool
    markers, release reproducibility and CI sidecar anchors, development/run-
    artifact/ROADMAP/papers-index anchors, focused tests, and this active TODO
    owner. It also maps each checklist bullet to the matching release-artifact
    workflow markers and maps the release-provenance JSON fields to the local
    provenance writer.
  - Current gap: the page-specific inventory is a static marker drift record,
    not an executed release transcript or semantic release-readiness proof. It
    maps local checklist bullets to workflow/tool markers, but does not prove
    the workflow was run for a specific release version, sign the provenance,
    verify a published or private package index, record a maintainer release
    event, or capture owner review signoff. A future release workflow, artifact
    name, provenance schema, local command, or signed/published-release
    boundary could still drift unless this validator and the broader release
    boundaries are updated together.
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
    `papers/readme_contributor_gate_boundary.json` now records README
    Contributing markers, docs/papers/ROADMAP/TODO routing markers, focused-
    test and paper-manifest guidance, secret-scan baseline policy, allowlist-
    pragma policy, baseline-staging policy, development-guide secret-scan
    anchors, the pre-commit detect-secrets hook, `.secrets.baseline` detector
    inventory markers, GitHub Actions secret-scan and paper/docs jobs,
    existing agent-doc drift assertions, CI workflow sidecar anchors, and this
    active TODO owner. It also maps the README Contributing guidance sentences
    to the concrete docs, hook, workflow, baseline, sidecar, and focused-test
    artifacts that currently support them.
  - Current gap: the README-owned sidecar is a static marker map, not a
    complete contributor-policy verifier. It maps README contributing
    sentences to marker-level artifacts, but does not prove that pre-commit
    hook changes force README/TODO updates, detect source-boundary file changes
    that need paper-manifest guidance updates, semantically verify
    secret-policy wording, or record owner review signoff.
  - Required result: add a README contributing-policy evidence map or test
    that links each contributing sentence to concrete hook/workflow/validator
    artifacts, checks secret-scan allowlist and baseline regeneration guidance
    against current configuration, and updates README/TODO evidence whenever
    contributor gates or source-boundary validation policy changes.

## Repository Policy

- [ ] Add repository ignore-policy evidence-retention drift check.
  - Spec evidence: `.gitignore` is part of the repository's truthfulness
    boundary because it decides which run artifacts, paper caches, release
    outputs, local secrets, worktrees, preview files, and paper sidecars are
    committed versus kept local. AlphaEvolve-alignment evidence should not
    depend on an untracked policy file whose changes can silently alter what
    validators, papers, and README claims are able to prove.
  - Current evidence: `.gitignore` excludes Python caches, virtual
    environments, build outputs, `runs/`, `.env`, `.claude/`, `.worktrees/`,
    preview/superpowers paths, and `papers/*` while allowlisting
    `papers/README.md`, download manifests, benchmark coverage inventory, and
    status-claim inventory. README and `papers/README.md` state that run
    outputs and cached paper PDFs are intentionally gitignored, and completed
    TODOs already cover the local-PDF allowlist boundary. GitHub Actions
    `push`/`pull_request` path filters cover docs, papers, tests, package
    metadata, `.gitignore`, and the workflow file itself.
    `papers/readme_ignore_policy_boundary.json` now records `.gitignore`
    ignore rules, paper-manifest allowlist rules, run-artifact local-only
    policy, paper-PDF local-only policy, README Repository Layout ignore
    markers, papers-index ignore-policy markers, GitHub Actions
    README/docs/papers/tests/pyproject/`.gitignore` path filters, existing agent-doc
    workflow assertions, this active TODO owner, a rationale map for every
    expected ignore and allowlist rule, and resolved `.gitignore` workflow
    path-filter coverage.
  - Current gap: the README-owned sidecar is a static inventory, not a full
    retention-policy verifier. It maps expected ignore and negation rules to
    artifact classes, retention rationales, and existing documentation anchors,
    but it does not inventory tracked sidecars versus ignored sidecars; it does
    not enforce a retention-policy drift gate or owner review signoff when
    ignore policy changes.
  - Required result: add an ignore-policy evidence map and validation gate
    that parses `.gitignore`, verifies ignored and allowlisted surfaces
    against README/docs/papers/TODO boundaries, checks workflow path filters
    include policy-critical files, proves allowlisted paper sidecars and
    manifests remain reachable, and requires README/TODO updates whenever
    ignore policy or CI trigger coverage changes.

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
    `papers/readme_license_boundary.json` now records the README License
    heading and MIT sentence, `LICENSE` file MIT text markers, pyproject
    license metadata, `papers/source_rights.json` policy markers, paper-source-
    rights module validators, paper-source-rights tests, and this active TODO
    owner while keeping third-party paper/source rights separate from
    LibreEvolve's MIT repository license. It also maps source-rights
    reproduction policy, artifact classes, and claim surfaces from
    `papers/source_rights.json`.
  - Current gap: the README-owned sidecar is a static consistency map, not a
    full rights or packaging verifier. It does not prove packaged license-file
    inclusion in wheel/sdist metadata, enforce a drift gate when project
    license metadata changes, enforce a drift gate when paper-rights policy
    changes, or record owner review signoff.
  - Required result: add a README license consistency check or evidence map
    that validates the README link, license identifier, package metadata,
    included license file, and explicit separation from third-party paper and
    companion-source rights, then update README/TODO evidence whenever license
    or source-rights policy changes.
