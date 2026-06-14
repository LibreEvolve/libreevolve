# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

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
