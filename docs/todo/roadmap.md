# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

## Missing Roadmap Items

## Existing Items That Need Tightening

- [ ] Keep the async/resumable-runtime roadmap wording scoped to compatible
  full-runtime restore versus full replay.
  - Spec evidence: AlphaEvolve-scale runs need reproducible resumed
    experiments, not just terminal snapshots; provider outputs, controller
    queues, pending evaluations, migration ordering, and lineage semantics must
    be replayable or explicitly bounded.
  - Current evidence: the roadmap now recognizes that
    `--restore-runtime-from-manifest` composes the current compatible
    synchronous restore surfaces into a checked full-runtime bundle: runtime
    RNG, LLM scheduler, archive restore, runtime budget, controller-budget
    replay, and lineage-boundary validation. It also keeps full replay and
    end-to-end resumed-trace proof open.
  - Required result: when provider/plugin output replay, ordered
    migration-event replay, async controller queues, pending-work restore, or
    resumed-trace lineage proof lands, update the roadmap, README, papers
    index, and code/paper TODO entries together so they neither underclaim the
    current compatible restore bundle nor overclaim AlphaEvolve-style replay.

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
