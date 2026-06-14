# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

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
