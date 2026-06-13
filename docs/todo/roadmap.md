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
    documentation-claim verification and implementation-evidence mapping
    absent.
  - Current gap: there is no machine-readable claim inventory for ROADMAP
    current-state bullets, no per-bullet code/test/runtime-artifact/sidecar/
    TODO evidence map, no stale-priority detector, and no generated alignment
    report that proves each ROADMAP statement is current.
  - Required result: add ROADMAP claim ids, evidence links, freshness checks,
    and CI validation before treating ROADMAP as semantically complete
    AlphaEvolve-alignment proof.

## Missing Roadmap Items

## Existing Items That Need Tightening
