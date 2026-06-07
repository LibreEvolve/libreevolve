# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

## Missing Roadmap Items

## Existing Items That Need Tightening

- [ ] Keep the provider cancellation roadmap item aligned with current timeout
  policy coverage.
  - Spec evidence: AlphaEvolve-scale provider orchestration needs bounded model
    calls, stop/quarantine behavior, and audit evidence for timeout and
    cancellation outcomes across model roles.
  - Current evidence: the roadmap now recognizes the implemented
    `libreevolve.provider_cancellation_policy.v1` policy contract,
    runtime scheduler observations, configured role/backend quarantine
    evidence, and mutation timeout failure-history rows before naming the open
    live SDK hard-cancellation and timeout-stop gap.
  - Required result: when live provider SDK cancellation, runtime
    timeout-driven stop policy, or richer role-specific timeout artifacts land,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so they neither underclaim current timeout policy evidence nor
    overclaim provider hard-cancel enforcement.
