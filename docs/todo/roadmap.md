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
    and AlphaEvolve-gap claims.
  - Current gap: there is no complete machine-readable claim inventory for
    every ROADMAP current-state bullet, no per-bullet code/test/runtime-
    artifact/sidecar/TODO evidence map, no stale-priority detector, and no
    generated alignment report that proves each ROADMAP statement is current.
  - Required result: add ROADMAP claim ids, evidence links, freshness checks,
    and CI validation before treating ROADMAP as semantically complete
    AlphaEvolve-alignment proof.

## Missing Roadmap Items

## Existing Items That Need Tightening
