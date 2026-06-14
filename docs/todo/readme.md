# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

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
