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
    and AlphaEvolve-gap claims. It also records audited README, ROADMAP, and
    papers-index Markdown headings plus uncovered heading-to-claim gaps with
    active TODO-owner links.
  - Current gap: there is no complete machine-readable claim inventory for
    every ROADMAP current-state bullet, no per-bullet code/test/runtime-
    artifact/sidecar/TODO evidence map, no stale-priority detector, and no
    generated alignment report that proves each ROADMAP statement is current.
  - Required result: add ROADMAP claim ids, evidence links, freshness checks,
    and CI validation before treating ROADMAP as semantically complete
    AlphaEvolve-alignment proof.

## Missing Roadmap Items

## Existing Items That Need Tightening

- [ ] Add ROADMAP non-goal contradiction checks.
  - Spec evidence: ROADMAP non-goals are overclaim guardrails. If the project
    says it is not requiring a service database, not claiming arbitrary-
    language/codebase support before runners and validators exist, and not
    advertising paper-inspired plugins as faithful implementations, those
    claims should be protected against drift across README, papers, plugin
    docs, and implementation metadata.
  - Current evidence: `ROADMAP.md` lists the three current non-goals, README
    limits already scope arbitrary-language runners, Google/Gemini parity,
    smoke examples, and paper-inspired claims, and active code/paper TODOs keep
    plugin behavior scoped to approximation/background metadata. The
    documentation claim inventory records the `Non-Goals For Now` heading but
    marks it as having no claim record.
  - Current gap: there is no machine-readable non-goal inventory, no
    cross-document contradiction detector, and no CI or sidecar check proving
    README, papers rows, plugin docstrings, runtime metadata, and future
    ROADMAP edits do not accidentally promote a non-goal into a supported
    AlphaEvolve-parity claim.
  - Required result: add stable ROADMAP non-goal claim ids and a verifier that
    maps each non-goal to the code/docs/paper surfaces it constrains, rejects
    contradictory support claims, and updates ROADMAP/TODO evidence whenever a
    non-goal is completed, removed, or intentionally promoted into active
    implementation work.

- [ ] Add ROADMAP Good First Follow-Ups priority freshness evidence.
  - Spec evidence: the `Good First Follow-Ups` section is a prioritization
    claim. If it tells contributors that database query indexes, one non-toy
    benchmark fixture, workspace resume coverage, and feedback-calibration
    reports are the next approachable steps, that ordering should be tied to
    current implementation state, dependency readiness, and AlphaEvolve-gap
    impact rather than remaining a static list.
  - Current evidence: ROADMAP lists four good first follow-ups, and active
    code/paper TODOs already track the underlying implementation gaps for
    durable query indexes, benchmark fixtures, workspace resume, and
    feedback-calibration reports. The documentation claim inventory records
    the `Good First Follow-Ups` heading as uncovered, while the broad ROADMAP
    semantic-evidence TODO covers priority claims only at a whole-document
    level.
  - Current gap: there is no per-item priority rationale, dependency/readiness
    record, owner/scope label, estimated validation gate, or stale-priority
    detector proving these four items remain the best first follow-ups after
    new ROADMAP, code, README, or paper-sidecar work lands.
  - Required result: add a ROADMAP priority-evidence map for good-first items
    that links each follow-up to active implementation TODOs, current
    blockers, expected validation artifacts, and AlphaEvolve-alignment impact,
    and add a drift check that forces the section to be refreshed when those
    dependencies or implementation states change.

- [ ] Add ROADMAP phase-boundary and sequencing evidence.
  - Spec evidence: the `Near Term`, `Mid Term`, and `Longer Term` headings are
    not neutral labels; they tell readers which AlphaEvolve-alignment work is
    nearer, which depends on more infrastructure, and which is deliberately
    deferred. That phase taxonomy should stay tied to dependency readiness and
    implementation prerequisites.
  - Current evidence: ROADMAP groups candidate-workspace fidelity,
    multi-objective search, evaluation cascades, prompt/context, documentation,
    async runtime, backend scheduling, plugin extensibility, representative
    benchmarks, and operational maturity into staged sections. Active code and
    paper TODOs cover many underlying features, and the documentation claim
    inventory records the phase headings as uncovered claim surfaces.
  - Current gap: there is no machine-readable phase map, dependency graph,
    promotion/demotion criterion, or stale-phase detector proving that a
    ROADMAP item still belongs in Near Term, Mid Term, or Longer Term after
    related code, papers, README, or sidecar evidence changes.
  - Required result: add ROADMAP phase metadata that links each major section
    to prerequisites, blocking TODOs, validation gates, and promotion criteria,
    then validate that phase labels and item ordering are refreshed when
    implementation or evidence status changes.

- [ ] Add ROADMAP operational-maturity acceptance criteria.
  - Spec evidence: the `10. Operational maturity` section groups config
    validation, strict JSONL diagnostics, run inspection, packaging/release
    provenance, and CI workflow coverage. As written, it is a roadmap category,
    but it does not define what evidence would make LibreEvolve operationally
    mature enough for AlphaEvolve-style experiments rather than only more
    locally smoke-tested.
  - Current evidence: ROADMAP names the current config, JSONL, run-inspection,
    release-artifact, and CI boundaries, and active code/paper TODOs track
    missing plugin-specific config schemas, provider/model compatibility,
    signed release provenance, local-PDF CI checks, semantic docs verification,
    branch policy, and notification policy.
  - Current gap: there is no section-level operational-maturity checklist,
    risk classification, acceptance threshold, or evidence map that ties those
    subitems together and prevents one green release/CI boundary from being
    mistaken for overall operational readiness.
  - Required result: add ROADMAP operational-maturity criteria that classify
    required validation, packaging, observability, reproducibility, CI, release,
    and policy evidence; map each criterion to code/tests/sidecars/TODOs; and
    reject claims that the project is operationally mature until the full
    checklist is satisfied.
