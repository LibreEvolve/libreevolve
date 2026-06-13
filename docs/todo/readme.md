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
    registry coverage, and focused boundary tests.
  - Current gap: there is still no semantic claim verifier, machine-readable
    implementation-evidence mapping for every README claim, stale completed-
    entry detector, generated alignment report, or full proof that every
    AlphaEvolve-facing README claim is current.
  - Required result: add a README claim inventory that links each feature,
    limit, research-source, and paper-derived statement to code/tests/docs/
    sidecars/TODO evidence, then validate stale or unsupported claims in CI.

## Architecture Description
