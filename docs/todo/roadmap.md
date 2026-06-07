# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

- [ ] Keep roadmap current-state framing tied to ongoing evidence rather than
      stale snapshot dates.
  - Spec evidence: the roadmap is part of the AlphaEvolve-alignment evidence
    surface, so its "current codebase" framing should remain true as code,
    README, paper-index, and TODO-ledger slices continue to change.
  - Current evidence: `ROADMAP.md` no longer claims to reflect only the
    codebase as of `2026-05-26`; it now describes ongoing alignment passes
    against the AlphaEvolve paper, local docs, paper index, and checked-in
    tests.
  - Required result: when future roadmap passes add or retire current-state
    claims, keep the intro and matching README/papers/TODO evidence aligned
    with the current worktree rather than a stale dated audit snapshot.

- [ ] Keep documentation-truthfulness roadmap wording scoped to partial
      cross-document guards.
  - Spec evidence: AlphaEvolve-alignment documentation should keep README,
    ROADMAP, paper-index, and TODO-ledger claims synchronized with implemented
    behavior, but path coverage and local consistency checks are not a full
    semantic proof that every claim is current.
  - Current evidence: `ROADMAP.md` says to keep README, docs, paper index, and
    `docs/todo/*` aligned with implemented behavior. Current tests check that
    the GitHub Actions workflow runs on README, ROADMAP, docs, papers, TODO,
    source, and test path changes; paper-manifest validation checks README and
    `papers/README.md` paper-count/status-table consistency; and
    `tests/test_paper_manifest.py` verifies each manifest id has exactly one
    TODO-coverage row. These guards do not prove every README, ROADMAP,
    paper-index, and TODO statement has matching code evidence, nor do they
    detect all stale completed TODO references, all missing active TODO links,
    or all semantic mismatches between implemented behavior and prose.
  - Required result: when stronger cross-document claim verification,
    implementation-evidence mapping, stale completed-entry detection,
    README/ROADMAP/paper/TODO semantic diffing, or generated alignment reports
    land, update the roadmap, README, papers index, and TODO ledgers together
    so they neither underclaim current path/test guards nor overclaim complete
    documentation truthfulness.

- [ ] Keep roadmap current-state budget bullets aligned with implemented LLM
      budget surfaces.
  - Spec evidence: AlphaEvolve-style fixed-budget comparisons require docs to
    distinguish current stop/accounting surfaces from still-open accelerator,
    async-queue, and pending-work budget gaps.
  - Current evidence: `ROADMAP.md` now lists current run-budget stops for
    generations, evaluations, evaluator-seconds, wall-clock runtime, logical
    LLM calls, provider attempts, provider-reported tokens, configured
    estimated cost, and retained LLM latency. Its evaluation-cascade follow-up
    now scopes remaining budget work to accelerator and async queue budgets
    rather than implying provider-attempt/token/configured-cost/latency stops
    are absent.
  - Required result: when new budget surfaces land, update the roadmap,
    README, papers index, and code/paper TODO entries together so they neither
    underclaim current LLM budget stops nor overclaim AlphaEvolve-grade
    accelerator/async budgeted search.

- [ ] Keep roadmap evaluator-contract wording scoped to local validity gating
      versus paper-facing scalar metrics.
  - Spec evidence: AlphaEvolve Section 2.1 frames evaluator outputs as scalar
    metrics maximized by convention, while the paper's example evaluator
    returns a `dict[str, float]`.
  - Current evidence: `ROADMAP.md` current state can accurately claim strict
    scalar evaluator-output validation against `metrics.yaml`, but
    LibreEvolve also requires reserved boolean `is_valid`, permits separate
    non-scalar attachments, and supports local metric direction/bounds
    normalization. The roadmap does not yet call out the missing
    paper-facing report/export boundary that proves only scalar objectives are
    counted as AlphaEvolve metrics.
  - Required result: when paper-facing evaluator metric reports and validators
    land, update the roadmap, README, papers index, and code/paper TODOs
    together so roadmap wording neither underclaims current strict local
    evaluator validation nor overclaims AlphaEvolve-comparable metric evidence.

- [ ] Keep evaluator-entrypoint roadmap wording scoped to external validators
      until embedded `evaluate(eval_inputs)` support exists.
  - Spec evidence: AlphaEvolve Section 2.1 and Figure 3 use a candidate
    codebase with an `evaluate(eval_inputs) -> dict[str, float]` function that
    invokes the evolved skeleton.
  - Current evidence: `ROADMAP.md` can claim configured local validators,
    staged evaluator entrypoints, direct evaluator path provenance, and
    problem-local dependency policy. It should not imply that these external
    validators are equivalent to a candidate-owned evaluator entrypoint.
  - Required result: when embedded evaluator entrypoints land, update ROADMAP,
    README, papers index, and code/paper TODOs with `evaluate` callable
    provenance, eval-input dataset provenance, skeleton-to-block invocation
    evidence, isolation/build policy, and score-field mapping.

- [ ] Keep binary/static roadmap scope aligned with implemented static-member
      support.
  - Spec evidence: AlphaEvolve can operate over broader codebase and artifact
    surfaces, while LibreEvolve's current boundary is a Python-primary text
    workspace plus typed static metadata.
  - Current evidence: `ROADMAP.md` now distinguishes implemented bounded
    encoded static members, verified copy-only static assets, and raw
    direct-workspace byte normalization from the still-open richer binary
    mutation/replay policy. The code path normalizes raw direct workspace bytes
    into immutable static members and verifies `source_copy_path` materialization
    by link policy, byte count, and SHA-256.
  - Required result: when arbitrary binary mutation, non-encoded generated
    binary deltas, binary replay, or broader artifact runners land, update the
    roadmap, README, papers index, and code/paper TODO entries together.

- [ ] Keep candidate-language roadmap scope aligned with the Python-primary
      policy boundary.
  - Spec evidence: AlphaEvolve tasks can define language/build/evaluator
    contracts over codebases and task-specific solution representations, so
    roadmap wording should keep the current manifest-visible boundary separate
    from real non-Python or build-system runner support.
  - Current evidence: `ROADMAP.md` current state now lists manifest-visible
    `libreevolve.candidate_language_policy.v1` records declaring the current
    Python-primary text-workspace boundary and unsupported arbitrary-language
    and build-system runners. Its near-term workspace section asks to extend
    that policy into real language/runner declarations, add problem-defined
    candidate abstraction hooks, add language-aware evolve-block marker
    grammars, and preserve topology diagnostics as language/build-runner edge
    cases are introduced.
  - Required result: when configured language runners, build-system runner
    contracts, language-aware marker grammars, or problem-defined candidate
    abstraction hooks land, update the roadmap, README, papers index, and
    code/paper TODO entries together so roadmap wording neither underclaims
    the current honest Python-primary policy record nor overclaims
    AlphaEvolve-grade arbitrary-language/codebase support.

- [ ] Keep candidate-abstraction roadmap wording scoped to hooks until
      abstraction-choice reports exist.
  - Spec evidence: AlphaEvolve Section 2.1 and Discussion treat candidate
    abstraction as a problem-dependent experimental choice with known biases:
    direct solution search, constructor functions, bespoke search algorithms,
    or paired intermediate solution/search representations can suit different
    problem structures.
  - Current evidence: `ROADMAP.md` asks for problem-defined candidate
    abstraction hooks and README identifies the current code-file-set
    abstraction boundary, but roadmap wording does not yet require benchmark
    metadata or reports that justify the chosen abstraction or compare
    alternative formulations under equal budgets.
  - Required result: when abstraction-choice metadata, rationale fields,
    symmetry/structure labels, paired solution/search support, or
    equal-budget abstraction-comparison reports land, update ROADMAP, README,
    papers index, and code/paper TODOs together so roadmap language does not
    confuse hooks with AlphaEvolve-style abstraction-selection evidence.

- [ ] Keep roadmap mutation-mode wording scoped to configured modes versus
      adaptive AlphaEvolve-style output contracts.
  - Spec evidence: AlphaEvolve Section 2.3 chooses SEARCH/REPLACE diffs for
    larger codebases and direct full-code output when short code or rewrite
    conditions make that more appropriate.
  - Current evidence: ROADMAP and README can accurately claim implemented
    `diff` and configured `full` mutation modes, including full-file,
    file-section, and full-block replacement semantics. They do not yet require
    a policy that selects the prompt/output mode per candidate or records why a
    candidate received a diff versus full-rewrite contract.
  - Required result: when adaptive mutation-mode policy, telemetry, and tests
    land, update roadmap, README, papers index, and code/paper TODO entries so
    roadmap wording neither underclaims current configured `diff`/`full`
    support nor overclaims AlphaEvolve-style adaptive mutation prompting.

- [ ] Keep roadmap seed-provenance wording scoped to source identity versus
      experiment idea provenance.
  - Spec evidence: AlphaEvolve Section 2.1 treats the initial program and
    optional background knowledge as user-provided inputs, and Section 3.1
    reports matrix runs where researcher-supplied ideas in the initial program
    affected performance.
  - Current evidence: ROADMAP and README/code evidence show source-safe seed
    ingestion and generation-0 baseline provenance, but roadmap wording does
    not yet require benchmark seed metadata for simple/random starts versus
    human-idea-seeded starts, injected prior techniques, or seed-variant
    result comparisons.
  - Required result: when benchmark seed metadata, idea-origin validation, and
    seed-variant reports land, update roadmap, README, papers index, and
    code/paper TODO entries together so roadmap text distinguishes source-path
    provenance from AlphaEvolve-style human-seeded experiment provenance.

- [ ] Keep roadmap seed-validity wording scoped to permissive baselines versus
      AlphaEvolve-strict complete initial programs.
  - Spec evidence: AlphaEvolve Section 2.1 expects the initial implementation
    inside evolvable blocks to be complete, although possibly rudimentary, and
    runnable through the supplied task skeleton/evaluator.
  - Current evidence: ROADMAP and README currently document source-safe seed
    ingestion, skipped-seed diagnostics, generation-0 baselines, and example
    seed-score classes. The implementation evaluates seeds and logs invalid
    seed failures, so current permissive optimization-pressure seeds are not
    equivalent to an AlphaEvolve-strict complete initial-program precondition.
  - Required result: when a strict initial-program validity policy, benchmark
    seed-validity report fields, and README/paper-index wording land, update
    roadmap text so it neither rejects the current permissive examples nor
    overclaims that invalid generation-0 baselines satisfy AlphaEvolve's
    complete initial-implementation requirement.

- [ ] Keep roadmap problem-formulation wording scoped to context artifacts
      until expert provenance exists.
  - Spec evidence: AlphaEvolve Section 3.2 says external mathematicians
    suggested open problems and advised on formulation, while Section 2.1 makes
    task definition and optional background knowledge explicit human inputs.
  - Current evidence: ROADMAP and README/code evidence cover local context
    source ingestion, ranking/filtering, and source/problem provenance, but do
    not require benchmark metadata for expert contributor roles, formulation
    advice, objective/evaluator rationale, or mathematical parameter-scope
    decisions.
  - Required result: when expert formulation metadata and report evidence land,
    update roadmap, README, papers index, and code/paper TODO entries together
    so roadmap text neither underclaims context provenance nor overclaims
    AlphaEvolve-style expert-guided benchmark formulation.

- [ ] Keep workspace-topology roadmap scope aligned with current
      materialization diagnostics.
  - Spec evidence: AlphaEvolve-style codebase evolution should turn invalid
    generated artifacts into stable evaluator feedback instead of opaque local
    filesystem failures, especially as program artifacts and runners become
    broader than the current local workspace.
  - Current evidence: `ROADMAP.md` currently names workspace file topology
    mutations for create/edit/delete/move/rename and primary-file changes, and
    its near-term workspace section asks to keep topology-operation collision
    policy and structured materialization-failure diagnostics complete as new
    workspace, language, and build-runner edge cases are introduced. Code and
    paper TODO evidence already scope the implemented coverage to current
    `CandidateMaterializationError` reason/path diagnostics, bounded
    `materialization_error` metadata, link/junction rejection, static
    source-copy verification, and topology command prevalidation.
  - Required result: when future topology surfaces such as bulk directory
    operations, language/build-runner generated artifacts, external
    materialization paths, or richer artifact runners land, update the roadmap,
    README, papers index, and code/paper TODO entries together so roadmap
    wording neither underclaims current structured invalid-workspace feedback
    nor overclaims AlphaEvolve-grade codebase-scale diagnostics.

- [ ] Keep roadmap code-scale wording scoped to benchmark-backed evidence.
  - Spec evidence: AlphaEvolve Table 1 says AlphaEvolve evolves entire code
    files, hundreds of lines of code, arbitrary languages, and complex
    algorithms with multiple functions/components.
  - Current evidence: ROADMAP correctly lists current workspace mechanics:
    Python seed workspaces, file topology mutations, materialization
    diagnostics, and the small `workspace_math` fixture. Those features do not
    yet prove large multi-component generated-code performance.
  - Required result: when large-codebase benchmarks or reports land, update
    roadmap, README, papers index, and code/paper TODO entries together so the
    roadmap separates current workspace mechanics from AlphaEvolve Table 1
    code-scale parity.

## Missing Roadmap Items

## Existing Items That Need Tightening

- [ ] Keep release-packaging roadmap wording scoped to editable/local use
  versus verified wheel/sdist artifacts.
  - Spec evidence: AlphaEvolve-style long-running experiments should be
    reproducible from the code and dependency environment users install; local
    editable development metadata is not the same as release-artifact
    validation.
  - Current evidence: `ROADMAP.md` currently asks to extend `pyproject.toml`
    metadata, dev extras, and console-script packaging beyond editable/local
    use with wheel/sdist build checks, package-data validation,
    install-from-wheel smoke tests, and release-artifact provenance. Code
    evidence shows `pyproject.toml` declares setuptools metadata, runtime
    dependencies, dev extras, package discovery, and the `libreevolve` console
    script, while runtime manifests record bounded package/build and installed
    distribution provenance; the code TODO still records that wheel/sdist
    build checks, install-from-wheel CLI smoke tests, package-data inclusion
    validation, release checklist, and release-artifact provenance are missing.
  - Required result: when release-distribution checks land, update the roadmap,
    README, papers index, and code TODO entries together so roadmap wording
    neither underclaims current editable/local package metadata nor overclaims
    verified release-distribution reproducibility.

- [ ] Keep GitHub Actions roadmap wording scoped to the current path-scoped
      Linux workflow.
  - Spec evidence: AlphaEvolve-scale engineering claims should be backed by
    repeatable validation that covers code, docs, paper evidence, packaging,
    and relevant supported runtime environments without surprising maintainers
    with noisy or unsafe triggers.
  - Current evidence: `ROADMAP.md` asks to extend the current path-scoped
    GitHub Actions workflow beyond secret scan, Python 3.11/3.12
    non-integration tests, optional integration tests, and documented
    paper-manifest commands. README documents the current manual-dispatch and
    path-scoped `push`/`pull_request` triggers. `.github/workflows/tests.yml`
    has `secrets`, `unit`, and optional `integration` jobs on Ubuntu only, and
    `tests/test_agents_docs.py` verifies the required path filters and job
    names, but it does not make CI run every docs/paper-specific verifier,
    wheel/sdist smoke, cross-platform jobs, or richer branch/notification
    policy.
  - Required result: when broader docs/paper validation, release-artifact
    checks, interpreter/platform matrices, branch policy, or notification-safe
    trigger policy lands, update the roadmap, README, papers index, and
    code/paper TODO entries together so roadmap wording neither underclaims the
    current workflow nor overclaims full AlphaEvolve-grade CI coverage.

- [ ] Keep operational config-validation roadmap wording scoped to local
      effective-config checks.
  - Spec evidence: AlphaEvolve-scale experiments need configuration validation
    that catches invalid local run policy before artifacts are written while
    keeping live provider/model API compatibility as a separate evidence
    surface.
  - Current evidence: `ROADMAP.md` asks to extend current config validation to
    plugin-specific schemas and provider/model API compatibility. README and
    code evidence show the current local boundary: CLI overrides are applied
    before config validation, plugin labels/options and backend specs are
    validated locally, and `ProgramDatabase` revalidates the full mutable
    `Config` before strict manifest serialization and run-directory
    preparation. Existing roadmap TODOs already track plugin
    configuration-schema scope and static provider capability lookup, but live
    provider model-registry, service/API-version, account availability, and
    broader provider/model compatibility checks remain future work.
  - Required result: when plugin-specific schemas expand, live provider/model
    API compatibility checks land, or config validation gains external service
    evidence, update the roadmap, README, papers index, and code/paper TODO
    entries together so roadmap wording neither underclaims current local
    effective-config validation nor overclaims live provider/API compatibility.

- [ ] Keep the multi-objective roadmap item scoped to primary archive policy
      versus retained diagnostic overlays.
  - Spec evidence: AlphaEvolve-style multi-objective search should make
    tradeoff-aware retention and inspiration part of the durable optimization
    policy, not only a diagnostic view.
  - Current evidence: `ROADMAP.md` now distinguishes the current scalar primary
    MAP-Elites grid plus bounded Pareto and metric-cell retained overlays from
    the still-open Pareto/frontier primary archive replacement and durable
    cross-run metric-specific optimization work. Code evidence includes
    bounded `pareto_frontier_archive()` retention, `metric_cell_archive()`
    overlays, persisted/restored `pareto_frontier_program_ids` and
    `metric_cell_archives`, and policy validation that rejects primary Pareto
    replacement overclaims.
  - Required result: when Pareto/frontier replacement becomes the primary
    archive policy, or durable cross-run metric-specific optimization lands,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so they neither underclaim the retained overlays nor overclaim
    AlphaEvolve-grade multi-objective optimization.

- [ ] Keep `show`/metric archive roadmap wording scoped to selected-row CLI
      output versus manifest-level summary records.
  - Spec evidence: AlphaEvolve-scale run inspection should support
    whole-run archive and metric-specific drill-downs, not just the selected
    best row.
  - Current evidence: `libreevolve show` prints selected-row
    archive/objective-vector diagnostics, while final manifests already expose
    `runtime.history.objective_metric_leaders` and
    `runtime.history.objective_metric_archives` summary records. `ROADMAP.md`
    now asks for CLI/report drill-downs over those metric-specific archives
    instead of implying the manifest-level summaries are absent.
  - Required result: when metric-specific archive drill-downs, whole-run CLI
    views, or durable artifact query reports land, update the roadmap, README,
    papers index, and code/paper TODO entries together so they neither
    underclaim current manifest summaries nor overclaim the selected-row
    `show` command.

- [ ] Keep `show`/source-integrity roadmap wording scoped to compact
      selected-row display plus streamed-row validation.
  - Spec evidence: AlphaEvolve-scale generated-program databases need
    whole-run source/workspace integrity summaries and durable query/report
    surfaces, not only a best-candidate terminal display.
  - Current evidence: `ROADMAP.md` asks to improve `show` beyond the current
    validity/archive-aware selected-row view with runtime status,
    lineage/prompt/evaluation/feedback/failure summaries, bounded
    objective-vector metrics, and workspace-file display toward whole-run
    source integrity reports, richer archive/prompt/failure drill-downs, and
    durable query views. README and code evidence show that current `show`
    validates streamed current and legacy source/workspace payloads for every
    row and prints selected-row workspace files, but does not emit whole-run
    source-hash or workspace-integrity reports.
  - Required result: when whole-run source/workspace integrity summaries,
    durable query/report views, richer archive/prompt/failure drill-downs, or
    every-candidate source-hash reports land, update the roadmap, README,
    papers index, and code/paper TODO entries together so roadmap wording
    neither underclaims current selected-row/streamed-row validation nor
    overclaims AlphaEvolve-grade run inspection.

- [ ] Keep artifact-content/provider-token roadmap wording scoped to bounded
  artifact rendering plus mutation/final-prompt caps.
  - Spec evidence: AlphaEvolve-style prompt construction can use execution
    results, diagnostics, and artifact evidence from previous attempts, but
    prompt packing should respect the selected model's context window across
    all prompt roles and context surfaces.
  - Current evidence: `ROADMAP.md` asks to integrate evaluator-output prompt
    summaries, aggregate syntax diagnostics, and bounded run-local artifact
    content retrieval with selected-backend provider-token section packing.
    README and paper TODO evidence show copied UTF-8 evaluator artifact content
    can be rendered from stored excerpts or reopened under bounded-file policy,
    binary/non-UTF-8 artifacts are explicitly non-renderable, mutation prompts
    have deterministic section budgets, and final prompts get role-scoped
    prompt-token cap checks. The remaining gap is automatic provider-token
    section-priority packing outside mutation prompts and exact counters across
    non-OpenAI/custom provider families, not bounded artifact-content rendering
    itself.
  - Required result: when selected-backend provider-token section packing covers
    critique, feedback, meta-prompt, retrieval/context/plugin/failure-memory,
    and artifact-content sections across provider families, update the roadmap,
    README, papers index, and code/paper TODO entries together so roadmap
    wording neither underclaims current bounded artifact rendering nor
    overclaims AlphaEvolve-grade prompt fitting.

- [ ] Keep strict finite JSONL roadmap wording scoped to current writer
      coverage.
  - Spec evidence: AlphaEvolve-scale run artifacts should remain replayable
    and diagnosable as new JSON/JSONL streams are added, with finite numeric
    values, duplicate-key-safe reads where applicable, and bounded diagnostics
    for malformed records.
  - Current evidence: `ROADMAP.md` asks to extend strict finite JSONL coverage
    and diagnostics beyond current candidate, prompt, manifest, and GRPO-export
    writers as new run artifacts are added. README and code evidence show
    strict finite JSON helpers for history, failure, prompt, and plugin JSONL
    streams; strict manifest JSON serialization before destructive overwrite
    cleanup; duplicate-key-free JSON loading for manifest-like inputs; bounded
    secret-redacted JSONL/quarantine diagnostics; and paper-manifest
    duplicate-key-free JSON validation. README also keeps a dedicated finite
    rejected-candidate stream open for hook-mutated or restored non-finite
    top-level fitness/metric values.
  - Required result: when new run-artifact JSON/JSONL streams,
    rejected-candidate finite streams, or broader strict-read/write diagnostics
    land, update the roadmap, README, papers index, and code/paper TODO
    entries together so roadmap wording neither underclaims current strict
    writer coverage nor overclaims complete AlphaEvolve-grade run-artifact
    serialization.

- [ ] Keep paper-manifest diagnostics roadmap wording scoped to shareable
      cache/index validation.
  - Spec evidence: paper-index evidence used for an AlphaEvolve-alignment
    audit should be reproducible and safe to share, but manifest diagnostics
    are not the same as semantic verification that a cited paper's behavior is
    implemented.
  - Current evidence: `ROADMAP.md` asks to keep paper-manifest validation
    diagnostics shareable with repository-relative labels and secret-redacted
    exception text in text and JSON output. README, `papers/README.md`, and
    `libreevolve.tools.paper_manifest` evidence show the current validator
    checks manifest/index shape, README/status-table consistency, safe
    manifest paths, duplicate-key-free JSON rows, optional local PDF
    availability/header/page/hash checks, Appendix B and ablation registries,
    rehydrate download/hash results, row-attributed issues, repository-relative
    labels, and redacted exception/download/read diagnostics. That makes the
    cache/index diagnostics shareable, but it does not prove every paper was
    semantically reviewed, that implementation-status rows are complete, or
    that ignored local PDFs are present unless `--require-local-pdfs` is used.
  - Required result: when paper-manifest diagnostics expand into semantic
    paper-claim verification, full implementation-status proof, stronger
    citation extraction, or mandatory local-PDF proof in CI, update the
    roadmap, README, papers index, and code/paper TODO entries together so
    roadmap wording neither underclaims current safe diagnostics nor overclaims
    paper-implementation verification.

- [ ] Keep DeepEvolve retrieval roadmap wording scoped to bounded provenance
  versus audit-grade source integrity.
  - Spec evidence: retrieval-augmented AlphaEvolve-style runs should preserve
    enough source, transport, ranking, and failure evidence to audit what
    external context was available and why it entered the prompt.
  - Current evidence: `ROADMAP.md` asks to extend DeepEvolve-inspired retrieval
    from bounded provenance into audit-grade source integrity with unbounded
    provider/source payload artifacts, learned or external ranking evidence
    beyond provider order, replayable transport/failure decisions, and explicit
    default-provider plus custom-provider provenance tests. README, code TODOs,
    and paper TODOs already document bounded provider-result/source-content
    snapshots, retention-budgeted redacted sidecars, deterministic query-overlap
    ranking, transport-policy classification, and run-level coverage validation,
    while preserving the open raw-payload, semantic-verification,
    learned-ranking, TLS/transport-replay, and full-source replay gaps.
  - Required result: when unbounded retrieval payload/source artifacts,
    learned/external ranking provenance, replayable transport/failure decision
    trees, or default/custom provider provenance tests land, update the
    roadmap, README, papers index, and code/paper TODO entries together so the
    roadmap neither underclaims current bounded retrieval provenance nor
    overclaims DeepEvolve-grade source integrity.

- [ ] Keep paper-inspired roadmap labels scoped to implemented behavior.
  - Spec evidence: roadmap references to paper-inspired systems should remain
    clear about whether LibreEvolve implements the cited paper behavior or only
    borrows a prompt/plugin idea.
  - Current evidence: the roadmap already says to continue labeling
    CausalEvolve, DeepEvolve, ImprovEvolve, ThetaEvolve, GigaEvo, CodeEvolve,
    and MadEvolve features as inspired unless paper behavior is actually
    implemented.
  - Required result: when faithful paper-specific behavior lands, update the
    roadmap, README, papers index, and code/paper TODO entries together. Until
    then, keep roadmap wording from promoting token-pattern causal guidance,
    clipped JSONL export, static modular prompting, retrieval context, or
    generic prompt-program mutation into the cited papers' full systems.

- [ ] Keep custom-plugin roadmap wording scoped to entry-point provenance
  versus direct-instance value attribution.
  - Spec evidence: AlphaEvolve-style extension points need reproducible plugin
    code/configuration boundaries so paper-inspired hooks can be audited across
    runs.
  - Current evidence: the roadmap now distinguishes entry-point distribution
    metadata and declared/manifest-safe constructor options from direct custom
    plugin instances, where current provenance records module/file/version and
    constructor signature shape while explicitly excluding constructor values.
  - Required result: when direct custom plugin constructor-value/schema
    attribution, versioned custom registries, or richer package policy lands,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so they neither underclaim entry-point plugin provenance nor
    overclaim direct-instance replayability.

- [ ] Keep plugin paper-inspiration/package-version roadmap wording scoped to
      configured entry-point records.
  - Spec evidence: AlphaEvolve-style paper-inspired extensions need clear
    attribution for which paper behavior a plugin claims, which package or
    distribution supplied it, and whether that scope is reproducible across
    runs.
  - Current evidence: `ROADMAP.md` asks to extend paper-inspiration scope and
    package-version attribution beyond current configured entry-point plugin
    labels/distribution records to direct custom plugins and versioned custom
    registries. README, papers index, and code evidence show current
    entry-point plugin specs persist a configured `paper_inspiration` label,
    entry-point group/name/value, distribution name/version, hash-only
    `RECORD`/`WHEEL` metadata when available, constructor-option policy, and
    loaded state. Direct custom plugins only record module/file/version
    identity plus constructor signature shape and explicitly exclude
    constructor values, arbitrary instance state, and richer package policy.
  - Required result: when direct custom plugin paper-scope declarations,
    versioned custom plugin registries, direct package/distribution source
    attribution, or richer paper-inspired plugin package policy lands, update
    the roadmap, README, papers index, and code/paper TODO entries together so
    roadmap wording neither underclaims current entry-point attribution nor
    overclaims direct-custom-plugin reproducibility.

- [ ] Keep plugin configuration-schema roadmap wording scoped to built-in and
      entry-point constructor validation.
  - Spec evidence: AlphaEvolve-style extension hooks need explicit,
    reproducible configuration contracts before plugin behavior can be treated
    as part of a comparable evolutionary system.
  - Current evidence: `ROADMAP.md` asks to broaden plugin configuration schemas
    beyond built-in scalar/path options and entry-point declared constructor
    schemas to cover direct custom constructor policy. README and code evidence
    show that configured built-in plugin specs are validated against declared
    option schemas, entry-point specs can validate manifest-safe
    `constructor_options` against a plugin-provided
    `libreevolve_constructor_option_schema`, and config validation calls the
    registry before destructive run setup. Direct custom plugin instances still
    record constructor signature shape only and explicitly exclude constructor
    values and arbitrary instance state.
  - Required result: when direct custom plugin constructor schemas, safe
    constructor-value declarations, richer option types, or versioned plugin
    registry policies land, update the roadmap, README, papers index, and
    code/paper TODO entries together so roadmap wording neither underclaims
    current built-in/entry-point validation nor overclaims complete
    AlphaEvolve-grade plugin configuration contracts.

- [ ] Keep plugin artifact-provenance roadmap wording scoped to manifest-safe
      summaries versus lifecycle evidence.
  - Spec evidence: AlphaEvolve-style extensibility needs plugin-generated
    artifacts to be attributable, replayable, and lifecycle-aware enough that
    prompt, score, artifact, and strategy effects can be audited across runs.
  - Current evidence: `ROADMAP.md` asks to extend plugin provenance beyond
    prompt-context/configuration/artifact records and manifest-safe emitted
    artifact summaries toward stronger artifact lifecycle hashes, versioned
    custom registry entries, and richer strategy choices. README and code
    evidence show current `run_artifacts_metadata()` summaries are wrapped with
    runtime-derived plugin identity, validated as bounded JSON-safe metadata,
    recorded under `runtime.plugin_artifacts[]`, and converted into
    `runtime.plugin_artifact_failures[]` during aborted-run finalization when
    the hook or schema fails. Current run manifests also classify and hash the
    known `plugin_artifacts/` directory, but plugin-specific lifecycle phases,
    produced-file declarations, strategy decisions, and versioned custom
    registry records are not yet a durable contract.
  - Required result: when plugin artifact lifecycle events, per-plugin
    produced-file manifests, strategy-choice provenance, versioned custom
    registry entries, or replay/restore policy for plugin artifacts land,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so roadmap wording neither underclaims current manifest-safe
    summaries nor overclaims AlphaEvolve-grade plugin artifact provenance.

- [ ] Keep proposal-memory roadmap wording scoped to bounded hypothesis
  summaries versus semantic proposal retrieval.
  - Spec evidence: AlphaEvolve-style idea memory should be able to score and
    retrieve prior proposal ideas and hypotheses by quality, novelty, and
    semantic relation to the current task.
  - Current evidence: the roadmap now distinguishes optional
    `IDEA`/`RATIONALE`/`HYPOTHESIS` proposal metadata and bounded manifest
    `runtime.history.hypothesis_index` evidence from still-open proposal
    scoring, semantic proposal-index retrieval, hypothesis-refinement loops,
    and field-influence policy for retrieval, prompting, and archive
    resurfacing.
  - Required result: when proposal scoring or semantic proposal-index
    retrieval lands, update the roadmap, README, papers index, and code/paper
    TODO entries together so they neither underclaim current bounded
    hypothesis summaries nor overclaim AlphaEvolve-grade idea memory.

- [ ] Keep scientific-discovery roadmap wording scoped to automated evaluators
      versus manual-experiment or LLM-only idea-review workflows.
  - Spec evidence: AlphaEvolve's Discussion says its main limitation is that
    it handles problems where an automated evaluator can be devised; domains
    requiring manual experimentation are out of scope, and LLM-provided
    high-level idea evaluation is a possible but not optimized bridge toward
    an implementation stage with machine feedback through code execution.
  - Current evidence: the roadmap tracks executable validators, staged
    evaluator feedback, optional LLM feedback graders, proposal metadata,
    retrieval, and hypothesis-memory follow-ups. It does not yet require
    roadmap-level scope metadata or workflow wording that separates
    machine-gradeable evolution from manual-experiment scientific workflows or
    AI-Co-Scientist-style pre-implementation idea review.
  - Required result: when problem/run/report scope metadata lands, update
    ROADMAP, README, papers index, and code/paper TODO entries together so the
    project neither underclaims executable evaluator support nor overclaims
    AlphaEvolve coverage for manual-experiment or LLM-only idea-feedback
    workflows.

- [ ] Keep self-improvement roadmap wording scoped until infrastructure and
      distillation evidence exists.
  - Spec evidence: AlphaEvolve's Discussion says practical discoveries can
    improve its own infrastructure and future base LLMs, and suggests
    distilling AlphaEvolve-augmented base-model performance into future models.
  - Current evidence: ROADMAP.md tracks provider/runtime budgets, systems
    benchmarks, and benchmark/report contracts, but it does not yet require
    report evidence for optimizing LibreEvolve's own runtime or provider
    infrastructure, nor does it define distillation data/export/training
    evidence derived from evolved candidates.
  - Required result: when roadmap items cover self-improving infrastructure or
    base-model uplift, require target-component identity, before/after
    measurements, deployment/adoption status, rollback/safety evidence,
    provenance linking the optimized component to LibreEvolve's own execution,
    and distillation dataset/training/evaluation artifacts where relevant.
    Update ROADMAP, README, papers index, and code/paper TODO entries together
    so roadmap wording treats those claims as future evidence requirements,
    not current AlphaEvolve parity.

- [ ] Keep evaluation-cascade roadmap wording scoped to staged thresholds until
      statistical hypothesis-test promotion evidence lands.
  - Spec evidence: AlphaEvolve Section 2.4 calls the cascade "hypothesis
    testing", with small-scale evaluations filtering candidates before harder
    main test cases, and Section 3.1 evaluates randomized tensor-decomposition
    runs where seed-dependent evidence matters.
  - Current evidence: `ROADMAP.md` accurately tracks configurable staged
    validators, thresholds, samples, retries, budgets, and the need to expand
    evaluation cascades. Current code and tests cover deterministic threshold
    gates, per-seed samples, and budget diagnostics, but not statistical
    promotion policies, confidence/p-value records, sequential stopping, or
    explicit small-scale-versus-main-test stage roles.
  - Required result: when hypothesis-test cascade policies, promotion reports,
    and noisy repeated-seed validation land, update ROADMAP, README, papers
    index, and code/paper TODO entries together so roadmap wording neither
    underclaims current staged validators nor overclaims AlphaEvolve-style
    hypothesis-testing cascades.

- [ ] Keep mutation-response roadmap wording scoped to structured proposal
      metadata versus natural-language preambles.
  - Spec evidence: AlphaEvolve Figure 3(c) includes explanatory prose before a
    SEARCH/REPLACE diff example, while Section 2.3 still defines the edit
    payload through structured diff blocks.
  - Current evidence: LibreEvolve roadmap claims should distinguish supported
    structured proposal metadata from ordinary explanatory prose. Current code
    accepts bounded `IDEA`/`RATIONALE`/`HYPOTHESIS` fields but rejects prose
    around valid mutation sections.
  - Required result: when response parsing supports safe explanatory
    preambles, or when strict structured-metadata divergence is documented as
    policy, update ROADMAP, README, papers index, and code/paper TODOs
    together so they do not imply AlphaEvolve-style freeform rationale parsing
    already exists.

- [ ] Keep prompt-example roadmap wording scoped until example-copy
      diagnostics exist.
  - Spec evidence: AlphaEvolve Figure 3(b,c) uses concrete current-program
    context and concrete SEARCH/REPLACE examples; the system should apply
    model edits to the sampled program rather than accept copied illustrative
    placeholders as real candidate changes.
  - Current evidence: README says concrete diff examples reduce observed
    placeholder-copying mistakes, while current roadmap/code evidence covers
    parser syntax, canonical diff compatibility, and strict unconsumed-text
    rejection. It does not yet include a versioned prompt-example inventory,
    copied-example sentinel detection, or acceptance/report diagnostics.
  - Required result: when example-copy diagnostics and tests land, update
    ROADMAP, README, papers index, and code/paper TODOs together so roadmap
    wording separates concrete prompt examples from evidence that accepted
    mutations are genuine edits to the current program.

- [ ] Keep mutation-operator roadmap wording scoped to fixed edit surfaces
      until operator-construction evidence lands.
  - Spec evidence: AlphaEvolve Section 2.3 uses structured edit outputs, while
    Related Work contrasts the system with evolutionary approaches that rely
    on a pre-defined handwritten mutation/crossover operator set.
  - Current evidence: `ROADMAP.md` current state lists SEARCH/REPLACE diff
    mutation, configurable full replacement, and workspace topology mutations.
    That is accurate for the local edit grammar, but it does not prove that
    LibreEvolve can declare, generate, select, score, or report higher-level
    LLM-constructed mutation-operator families independent of the fixed local
    parser surfaces.
  - Required result: when mutation-operator construction or adaptive
    operator-family selection lands, update ROADMAP, README, papers index, and
    code/paper TODOs together so roadmap wording separates implemented
    edit-payload support from AlphaEvolve's broader claim that LLMs replace
    handwritten mutation-operator sets.

- [ ] Keep database-query-index follow-up wording scoped to run-local
      resurfacing versus durable cross-run indexes.
  - Spec evidence: AlphaEvolve's program database should support durable
    resurfacing of previously explored programs and ideas across score,
    metric, diversity/novelty, feedback, lineage, failure, hypothesis, and
    artifact evidence, with reproducible sampling policies rather than only
    live in-memory archive views.
  - Current evidence: `ROADMAP.md` lists "Persist database query indexes
    beyond run-local metric/novelty/lineage/feedback resurfacing" as a good
    first follow-up. Code and paper TODO evidence now show bounded
    current-run `runtime.history.resurfacing_index` support plus defensive
    `ProgramDatabase.resurface_candidates(target_metric=...)`,
    `resurface_by_metric()`, `resurface_by_lineage()`,
    `resurface_by_descriptor()`, `resurface_by_novelty()`, and
    `resurface_by_feedback()` APIs over score, metric, frontier, lineage,
    descriptor/novelty, hypothesis, artifact, and feedback views. These
    records preserve `durable_database_ready: false` and remain append-only
    logs, an in-memory archive, and manifest-visible bounded summaries rather
    than persisted cross-run query/index tables, full metric-vector and
    feedback/artifact-content ranking, program-output value/schema ranking,
    semantic/cross-run hypothesis retrieval, learned/cross-run novelty, schema
    migrations, or replayable durable sampling policies.
  - Required result: when persisted database tables, cross-run query indexes,
    replayable ranked sampling policies, schema migration support, or
    durable full-content/semantic resurfacing lands, update the roadmap,
    README, papers index, and code/paper TODO entries together so roadmap
    wording neither underclaims current run-local resurfacing nor overclaims
    AlphaEvolve-grade queryable database support. Treat evaluator
    program-output indexes as part of that durable database surface, not merely
    prompt feedback or artifact excerpts.

- [ ] Keep database-memory roadmap wording scoped until duplicate-work policy
      lands.
  - Spec evidence: AlphaEvolve's program database is a memory of generated
    solutions with attached evaluation evidence, used to resurface previously
    explored ideas under fixed budgets.
  - Current evidence: `ROADMAP.md` can claim deterministic candidate ids,
    unique program-id validation, workspace-hash identity components, current
    JSONL history, and bounded current-run resurfacing. It does not yet claim,
    and should not imply, that identical source/workspace proposals are
    detected before evaluation, served from a cache, or deliberately
    re-evaluated under a stochastic sample policy.
  - Required result: when duplicate-work policy, source/workspace hash indexes,
    evaluation-cache reuse, or documented stochastic re-evaluation lands,
    update ROADMAP, README, papers index, and code/paper TODOs together so
    roadmap wording separates current identity provenance from AlphaEvolve-grade
    fixed-budget memory over previously explored programs.

- [ ] Keep discovery-distance roadmap wording scoped until initial-pool
      divergence reports exist.
  - Spec evidence: AlphaEvolve's introduction says feedback-driven evolution
    can produce candidates substantially different from the initial candidate
    pool in syntax and function.
  - Current evidence: `ROADMAP.md` can claim candidate lineage, workspace
    hashes, changed files, archive descriptor/novelty views, and proposal
    metadata. It does not yet promise or evidence initial-pool syntactic or
    functional-distance reports.
  - Required result: when initial-pool divergence reports land, update ROADMAP,
    README, papers index, and code/paper TODOs with seed-pool comparison
    baselines, syntax/code distance, changed-component summaries,
    metric/behavioral distance, and functional-difference artifacts before
    using AlphaEvolve-style discovery-distance claims.

- [ ] Keep meta-prompt context-policy roadmap wording scoped to validated
  current fields.
  - Spec evidence: AlphaEvolve-style meta-prompt evolution should improve both
    prompt instructions and prompt context policy, not only mutate whole prompt
    template strings or a fixed subset of locally known rendering controls.
  - Current evidence: `ROADMAP.md` currently documents prompt-program
    selection, scoring, lineage, optional interval-based LLM template mutation,
    prompt-template validation, bounded prompt/context retention surfaces, and
    the need for richer context-policy ownership. Code, README, and paper TODO
    evidence now also show that prompt programs persist validated
    `libreevolve.prompt_context_policy.v1` state, meta-prompt evidence exposes
    a checked `libreevolve.meta_prompt_context_policy_capabilities.v1`
    capability map, and the current tunable fields include optional channel
    controls, section priorities, mutation-instruction variants, parent metric
    selection/caps, parent-code selection/filtering/order/limits/caps/
    truncation, proposal metadata enablement, feedback subsection controls, and
    inspiration sampling controls.
  - Required result: when prompt-program policy can control retrieval or
    summarization behavior, learned/semantic context selection, arbitrary
    instruction channels, broader per-role retention, or other prompt surfaces
    beyond the currently validated field set, update `ROADMAP.md`, README,
    papers index, and code/paper TODO entries together so roadmap wording
    neither underclaims current structured policy mutation nor overclaims full
    AlphaEvolve-grade prompt evolution.

- [ ] Keep prompt-template compatibility roadmap wording scoped to current
  mutation-template validation and duplicate-arm audit.
  - Spec evidence: AlphaEvolve-style prompt evolution needs compatibility
    policy for the concrete model-call roles that consume prompt text, plus a
    clear duplicate-template policy for experiments and prompt-program lineage.
  - Current evidence: `ROADMAP.md` says prompt templates are currently
    validated for known placeholders, compatible format specs, and
    parent-placeholder retention, then names role-specific compatibility and
    prompt-program deduplication as future work. README and code evidence show
    configured AlphaEvolve-style mutation-channel validation and stochastic
    `prompt_format_options`, while duplicate configured/evolved template text
    is intentionally retained as separate prompt arms with deterministic ids and
    `template_sha256` audit identity, not deduplicated.
  - Required result: when role-specific prompt-template compatibility,
    prompt-program text deduplication, or an explicit validated no-dedup policy
    lands, update the roadmap, README, papers index, and code/paper TODO entries
    together so they neither underclaim current validation nor imply
    implemented prompt-program deduplication.

- [ ] Keep meta-prompt scoring roadmap wording scoped to current child-score
  rewards and prompt-arm UCB selection.
  - Spec evidence: AlphaEvolve-style meta-prompt evolution should have
    calibrated reward signals and ablation evidence that can attribute outcomes
    to prompt-program lineages.
  - Current evidence: `ROADMAP.md` already says the current state is
    absolute/improvement child score reward modes plus UCB-style prompt-arm
    selection. README and code evidence show finite reward bounds, normalized
    prompt reward metadata, reward-policy-compatible history replay, and
    bounded prompt-performance evidence for meta-prompt calls, but no calibrated
    prompt reward model or prompt-lineage ablation report.
  - Required result: when calibrated meta-prompt reward signals,
    prompt-lineage ablation reports, or stronger prompt-policy attribution
    land, update the roadmap, README, papers index, and code/paper TODO entries
    together so the roadmap neither underclaims current prompt scoring nor
    overclaims AlphaEvolve-grade meta-prompt reward calibration.

- [ ] Keep prompt-database roadmap wording scoped to local prompt-arm history
  versus a solution-database analogue.
  - Spec evidence: AlphaEvolve Section 2.2 describes meta-prompt evolution as
    co-evolving prompt instructions/context in a separate database analogous to
    the solution programs.
  - Current evidence: `ROADMAP.md` accurately lists a local prompt-program
    database with prompt selection, scoring, lineage, and optional
    interval-based LLM template mutation. Code evidence shows a deterministic
    `PromptDatabase` backed by prompt history and UCB-style prompt-arm
    selection, not prompt-side MAP-Elites/island retention, prompt archive
    events, descriptor/objective indexes, or controller-resumable prompt work.
  - Required result: when prompt-side archive/retention policy, prompt
    descriptors/objectives, replay/migration semantics, and benchmark evidence
    land, update ROADMAP, README, papers index, and code/paper TODOs together
    so roadmap wording neither underclaims the current prompt-history store nor
    overclaims an AlphaEvolve-grade co-evolved prompt database.

- [ ] Keep MAP-Elites descriptor roadmap wording scoped to insertion-time
  TF-IDF coordinates versus stable learned descriptors.
  - Spec evidence: AlphaEvolve-style quality-diversity search needs
    task-meaningful behavior descriptors or stable descriptor models with
    tested compatibility when descriptors change.
  - Current evidence: the roadmap now names evaluator-provided behavior
    descriptors, fixed descriptor models, or explicit rebin/snapshot semantics
    as the remaining work. Current archive snapshots already record descriptor
    axes, current diversity reference ids, descriptor-model revision, dynamic
    TF-IDF reference status, and the no-rebin insertion-time coordinate policy.
  - Required result: when learned/evaluator-provided descriptor models or
    archive rebin semantics land, update the roadmap, README, papers index,
    and code/paper TODO entries together so they neither underclaim current
    descriptor-policy snapshots nor overclaim stable AlphaEvolve-grade
    behavior descriptors.

- [ ] Keep island-count roadmap wording scoped to configurable defaults.
  - Spec evidence: AlphaEvolve's paper names MAP-Elites and island-based
    population models at a high level; local roadmap wording should not turn
    LibreEvolve's default island count into an unsupported fixed fidelity
    claim.
  - Current evidence: the roadmap now says MAP-Elites plus configurable
    ring-topology island migration, defaulting to five islands. That matches
    `Config.n_islands`, validation for positive configured island counts, and
    tests with non-default island counts.
  - Required result: when adaptive island counts, non-ring topologies, or
    AlphaEvolve-specific migration policies land, update the roadmap, README,
    papers index, and code/paper TODO entries together so they do not
    underclaim current configurability or overclaim fixed five-island policy.

- [ ] Keep per-role scheduler roadmap wording scoped to role-scoped backend
  eligibility and role budget maps versus independent live scheduler state.
  - Spec evidence: AlphaEvolve-scale LLM orchestration needs role-specific
    model-selection behavior for mutation generation, critique, feedback, and
    prompt-improvement calls, with budgets and rewards that can be evaluated
    independently.
  - Current evidence: the roadmap now distinguishes configured
    reward-accounted roles, role-scoped backend eligibility, logical call caps,
    and role budget maps from still-open independent per-role live scheduler
    state, calibrated reward signals, quota ownership, and budget policy.
  - Required result: when independent per-role scheduler state lands, update
    the roadmap, README, papers index, and code/paper TODO entries together so
    they neither underclaim current role routing and budget maps nor overclaim
    AlphaEvolve-style per-role scheduling.

- [ ] Keep UCB scheduler roadmap wording scoped to heuristic backend routing.
  - Spec evidence: canonical UCB1 claims require bounded reward assumptions and
    regret-analysis conditions, while AlphaEvolve-style backend scheduling also
    needs experiment-level breadth/depth/cost/latency evidence before it can be
    treated as a faithful scheduler rather than a local routing heuristic.
  - Current evidence: `ROADMAP.md` asks to normalize/document UCB rewards
    against bounded assumptions or rename the current policy as a heuristic.
    Code and paper-index evidence already describe `LLMEnsemble` as a
    heuristic UCB-style router over caller-provided/archive-admitted valid
    fitness-improvement rewards, not a canonical regret-analyzed UCB1
    implementation or MadEvolve reproduction. README labels the ensemble as
    heuristic backend routing, and focused tests cover high-reward preference,
    superior-arm convergence, `throughput_depth` metadata selection,
    per-selection min/max metadata normalization, pull-once initialization, and
    call telemetry that marks selection scope as a global backend bandit with
    shared selection and configurable role reward accounting. These tests do
    not prove regret bounds, calibrated reward scaling across heterogeneous
    tasks, experiment-level scheduler traces, or equal-budget breadth/depth/
    cost/latency comparisons.
  - Required result: when canonical UCB1 assumptions, calibrated reward
    normalization, experiment-level scheduler reports, or AlphaEvolve-style
    breadth/depth/cost/latency validation lands, update the roadmap, README,
    papers index, and code/paper TODO entries together so wording neither
    underclaims current heuristic routing nor overclaims regret-analyzed or
    paper-faithful scheduler behavior.

- [ ] Keep `throughput_depth` roadmap wording scoped to metadata/unit tests
      versus scheduler-validation reports.
  - Spec evidence: AlphaEvolve-style fast/deep model scheduling needs
    experiment-level selection traces, budget-normalized comparisons, and
    breadth/depth/cost/latency evidence across real runs, not only deterministic
    backend metadata arithmetic. Section 2.4's concrete model mix uses a
    low-latency model for high-volume idea generation and a stronger model for
    occasional higher-quality suggestions.
  - Current evidence: `ROADMAP.md` asks to extend current focused
    `throughput_depth` metadata tests into AlphaEvolve-style scheduler
    validation. README and code evidence show the current policy is a
    heuristic global backend bandit with optional normalized metadata weights
    (`depth: 0.10`, `cost: -0.05`, `latency: -0.05`) after pull-once
    initialization. Focused ensemble tests cover metadata validation and
    defensive copying, secret-safe metadata retention, descriptive
    breadth/depth role metadata, per-selection min/max normalization against
    reward scale, metadata-priority selection after all backends are
    initialized, and call telemetry for the effective policy. They do not run
    benchmark workloads, emit experiment-level selection traces, compare
    equal-budget scheduler variants, or prove that breadth/depth/cost/latency
    choices improve AlphaEvolve-style search outcomes. They also do not prove
    a dedicated fast-breadth plus strong-depth model-mix policy analogous to
    AlphaEvolve's Flash/Pro scheduling.
  - Required result: when executable scheduler-validation fixtures,
    experiment-level selection trace artifacts, equal-budget scheduler reports,
    dedicated fast/strong lane policies, or calibrated breadth/depth/cost/
    latency policy evidence land, update the roadmap, README, papers index,
    and code/paper TODO entries together so roadmap wording neither
    underclaims current focused `throughput_depth` coverage nor overclaims
    AlphaEvolve-grade model-scheduling validation.

- [ ] Keep sample-efficiency roadmap wording scoped to budget accounting
      until proposal-count reports exist.
  - Spec evidence: AlphaEvolve Table 1 says AlphaEvolve can get useful results
    with thousands of LLM samples, unlike FunSearch's millions, and Section 4
    evaluates the impact of powerful models under fixed compute budgets.
  - Current evidence: `ROADMAP.md` discusses local LLM call/provider/token/
    configured-cost/latency budget accounting, equal-budget ablation report
    contracts, fast/deep scheduler validation, and small-base-model ablation
    labels. It does not require reports that plot target progress against
    generated/evaluated proposal counts or validate thousands-scale sample
    efficiency.
  - Required result: when proposal-count efficiency reports, sample-budget
    curves, model-size comparisons, or target-hit-per-sample summaries land,
    update ROADMAP, README, papers index, and code/paper TODOs together so
    roadmap language distinguishes budget stopping from AlphaEvolve-style
    "thousands of samples suffice" evidence.

- [ ] Keep provider-roadmap wording explicit about missing Google/Gemini
      first-class support.
  - Spec evidence: AlphaEvolve's concrete model ensemble uses Gemini 2.0 Flash
    and Gemini 2.0 Pro, not only an abstract fast/deep backend pair.
  - Current evidence: ROADMAP describes existing or custom LLM choices and
    fast/deep scheduler validation, while the code's built-in backend registry
    is OpenAI, Anthropic, and Ollama only. The `custom` backend escape hatch is
    not equivalent to a self-describing Google/Gemini provider surface.
  - Required result: when a Gemini backend, provider-plugin contract, or
    explicit paper-level substitute lands, update ROADMAP, README, papers
    index, and code/paper TODOs so roadmap language separates generic backend
    extensibility from AlphaEvolve's published Flash/Pro provider parity.

- [ ] Keep the async/resumable-runtime roadmap wording scoped to compatible
  full-runtime restore versus full replay.
  - Spec evidence: AlphaEvolve-scale runs need reproducible resumed
    experiments, not just terminal snapshots; provider outputs, controller
    queues, pending evaluations, migration ordering, lineage semantics, and
    any slow-feedback consecutive-mutation policy must be replayable or
    explicitly bounded.
  - Current evidence: the roadmap now recognizes that
    `--restore-runtime-from-manifest` composes the current compatible
    synchronous restore surfaces into a checked full-runtime bundle: runtime
    RNG, LLM scheduler, archive restore, runtime budget, controller-budget
    replay, and lineage-boundary validation. The near-term workspace section
    now scopes resume work to ordered migration-event replay, controller
    queues, and pending-work resume beyond the current archive-content restore
    bundle. It also keeps full replay and end-to-end resumed-trace proof open.
  - Required result: when provider/plugin output replay, ordered
    migration-event replay, async controller queues, pending-work restore,
    mutation-chain-depth policy, or resumed-trace lineage proof lands, update
    the roadmap, README, papers index, and code/paper TODO entries together so
    they neither underclaim the current compatible restore bundle nor overclaim
    AlphaEvolve-style replay.

- [ ] Keep controller-state roadmap wording scoped to terminal drained
      snapshots versus async queue checkpoints.
  - Spec evidence: AlphaEvolve-style long-running controllers need resumable
    queue, worker, pending-evaluation, and partially completed generation
    state; a terminal no-pending-work snapshot is useful audit evidence but is
    not a mid-generation or async controller checkpoint.
  - Current evidence: completed manifests now include
    `runtime.history.controller_state` with schema
    `libreevolve.controller_state.v1`, status
    `terminal_synchronous_controller_drained`, resume scope
    `terminal_drained_state_only`, zero queued/running proposals and
    evaluations, zero in-flight LLM calls, zero pending archive admissions, a
    `controller_budget_events.jsonl` stream summary, and embedded
    `libreevolve.controller_state_validation.v1` diagnostics that reject
    pending-work or async/full-replay overclaims. README, code TODO, and paper
    TODO evidence also show `controller_state_artifact_inventory()` verifies
    that terminal event stream against the manifest artifact record and disk
    file. This does not persist queued/running async workers, in-flight
    provider outputs, evaluator-worker state, pending archive admissions,
    partially completed generation state, or deterministic mid-generation
    controller resume ledgers.
  - Required result: when async controller queues, pending-work checkpoints,
    mid-generation resume, evaluator-worker state, provider-output replay, or
    deterministic controller resume ledgers land, update the roadmap, README,
    papers index, and code/paper TODO entries together so roadmap wording
    neither underclaims current terminal controller-state validation nor
    overclaims AlphaEvolve-grade controller resume.

- [ ] Keep workspace-resume follow-up wording scoped to export artifacts versus
      resumable candidate state.
  - Spec evidence: AlphaEvolve-style workspace/codebase resume should restore
    enough candidate workspace state to continue search, not only materialize a
    terminal best workspace for inspection or reuse outside the evolutionary
    controller.
  - Current evidence: `ROADMAP.md` lists workspace resume beyond current
    `best_workspace/` export as a good first follow-up. README and code
    evidence show the CLI writes `best.py` plus the complete
    `best_workspace/` file set, including static sidecar metadata and tree hash
    records, and final manifests record best-artifact export success/failure.
    Separate archive restore surfaces can rehydrate accepted history and
    per-island archive contents, but `best_workspace/` itself is an exported
    terminal artifact, not a workspace-candidate resume engine with build
    inputs, pending materialization state, evaluator artifacts, or continuation
    semantics.
  - Required result: when workspace-candidate resume, build/input restoration,
    materialization-state replay, or continuation from exported workspace
    artifacts lands, update the roadmap, README, papers index, and code/paper
    TODO entries together so they neither underclaim current complete
    `best_workspace/` export nor overclaim resumable AlphaEvolve-style
    workspace state.

- [ ] Keep environment-provenance roadmap wording scoped to bounded audit
  evidence versus replayable build/package/accelerator state.
  - Spec evidence: AlphaEvolve-scale experiments need environment evidence
    strong enough to reproduce evaluator execution, package resolution,
    accelerator runtime, and compute-budget accounting across long runs.
  - Current evidence: the roadmap now says current bounded environment
    provenance should be extended into complete install-source interpretation,
    external build execution/options/environment records, non-project build
    metadata policy, private package-source resolution, live provider
    service/default capture, and accelerator budget/accounting semantics.
  - Required result: when external-build/package-source/accelerator replay
    evidence lands, update the roadmap, README, papers index, and code/paper
    TODO entries together so they neither underclaim the current audit-only
    manifest records nor overclaim replayable AlphaEvolve-grade environment
    reproduction.

- [ ] Keep provider capability roadmap wording scoped to static backend
  validation versus live provider/account discovery.
  - Spec evidence: AlphaEvolve-scale backend comparisons need provider
    capability evidence that survives changing model registries, service API
    versions, and account entitlements; local static checks alone cannot prove
    a model/API mode was available to an account at run time.
  - Current evidence: the roadmap already names live provider service/default
    capture and provider pricing as open environment/backend gaps, while README
    and manifest policies make the narrower capability boundary explicit:
    LibreEvolve performs manifest-safe model-id validation and local OpenAI
    compatibility checks only, with no live model-registry,
    service/API-version, or account-availability lookup before a run. Code and
    paper TODO entries already track live authenticated provider
    request/model-registry evidence beyond credential-presence and local client
    construction.
  - Required result: when live provider model-registry discovery,
    service/API-version capture, account-availability validation, or
    provider-capability provenance lands, update the roadmap, README, papers
    index, and code/paper TODO entries together so they neither underclaim the
    current static capability policy nor overclaim live provider discovery.

- [ ] Keep provider-diagnostics roadmap wording scoped to retained scalar
      telemetry versus raw provider replay.
  - Spec evidence: AlphaEvolve-grade scheduler and budget evidence needs
    reliable per-call provider details, pricing/cost evidence, and replayable
    provenance for the model calls that produced proposals, critiques,
    feedback, and prompt mutations.
  - Current evidence: `ROADMAP.md` asks to extend run-scoped call telemetry
    beyond provider usage, configured cost estimates, request ids, finish
    reasons, adapter retry summaries, and token/cost/latency stops to raw
    provider diagnostics, live provider pricing/default-rate capture, and
    richer budget-event evidence. Code, README, and paper TODO evidence show
    the current boundary: adapters expose safe usage/id/finish metadata,
    `adapter_retry` records, bounded scalar `provider_diagnostics`, local
    `backend_defaults`, failure categories/status codes, configured
    `cost_estimate` and `cost_estimate_status` records, strict call/reward
    ledger replay, and final `runtime.llm_provider_diagnostics` summaries
    validated by `libreevolve.llm_provider_diagnostics.v1`. Those summaries
    aggregate retained call-history windows and explicitly limit themselves to
    bounded scalar diagnostics and configured pricing estimates, not full raw
    provider-native payload replay, live provider pricing/default-rate
    discovery, account/model default capture, or complete replay evidence for
    provider outputs.
  - Required result: when raw provider-payload replay, live pricing/default
    capture, provider account/model default evidence, or richer budget-event
    artifacts land, update the roadmap, README, papers index, and code/paper
    TODO entries together so roadmap wording neither underclaims current
    bounded diagnostics nor overclaims AlphaEvolve-grade provider-call replay.

- [ ] Keep the provider cancellation roadmap item aligned with current timeout
  policy coverage.
  - Spec evidence: AlphaEvolve-scale provider orchestration needs bounded model
    calls, stop/quarantine behavior, and audit evidence for timeout and
    cancellation outcomes across model roles.
  - Current evidence: the roadmap now recognizes the implemented
    `libreevolve.provider_cancellation_policy.v1` policy contract,
    runtime scheduler observations, configured in-run role/backend quarantine
    evidence, strict provider-failure ledger summaries, restorable scheduler
    failure-policy state, and mutation timeout failure-history rows before
    naming the open live SDK hard-cancellation, timeout-stop, raw provider
    output replay, and cross-run quarantine/resume gaps.
  - Required result: when live provider SDK cancellation, runtime
    timeout-driven stop policy, cross-run provider-failure quarantine/resume
    behavior beyond restorable scheduler failure-policy state, raw provider
    output replay, or richer role-specific timeout artifacts land, update the
    roadmap, README, papers index, and code/paper TODO entries together so they
    neither underclaim current timeout policy evidence nor overclaim provider
    hard-cancel enforcement.

- [ ] Keep provider-pricing roadmap wording scoped to configured estimates
  versus live/default-rate capture.
  - Spec evidence: AlphaEvolve-scale provider accounting needs cost evidence
    that survives provider, model, and default-rate changes; configured local
    rates are useful run policy but are not live provider pricing discovery.
  - Current evidence: backend specs can now set
    `cost_usd_per_million_tokens`, provider usage `total_tokens` feeds
    configured `cost_estimate` records, runtime accounting accumulates
    configured cost, and diagnostics explicitly mark live pricing as
    not fetched. The roadmap now names live provider pricing/default-rate
    capture beyond configured token-cost estimates as the remaining gap.
  - Required result: when live provider pricing discovery, provider default
    rate capture, or account/model-specific pricing evidence lands, update the
    roadmap, README, papers index, and code/paper TODO entries together so they
    neither underclaim configured cost accounting nor overclaim live pricing.

- [ ] Keep feedback-calibration roadmap wording scoped to report contracts
  versus executed calibration fixtures.
  - Spec evidence: AlphaEvolve-style feedback graders need calibration evidence
    from real reviewer/task suites, not only validators for declared reports.
  - Current evidence: `libreevolve.llm_feedback_calibration.v1` and its
    artifact-inventory contract validate declared multi-task calibration
    evidence and safe artifact references once a report exists. The roadmap
    now scopes the follow-up to emitting real reports and grader ablation
    fixtures.
  - Required result: when a runtime fixture or benchmark script emits real
    feedback-calibration reports, update the roadmap, README, papers index, and
    code/paper TODO entries together so they neither underclaim the report
    contract nor overclaim executed calibration evidence.

- [ ] Keep benchmark-hardening roadmap wording scoped to smoke evidence versus
  benchmark-grade fixtures.
  - Spec evidence: AlphaEvolve-style benchmark claims need repeated,
    target-family fixtures with anti-gaming evidence, not smoke-only examples.
  - Current evidence: the matrix smoke fixture now rejects known shortcuts and
    has a scope-checked hardening bundle helper that emits report, inventory,
    summary, and scope-validation files while preserving
    `alphaevolve_comparable: false`.
  - Required result: when tensor/geometric/compiler/systems fixtures emit
    benchmark-grade hardening reports, update the roadmap, README, papers index,
    and code/paper TODO entries together so they neither underclaim smoke
    hardening evidence nor overclaim AlphaEvolve-comparable benchmarks.

- [ ] Keep systems-result roadmap wording scoped to domain-agnostic report
      validation versus domain-specific readiness gates.
  - Spec evidence: AlphaEvolve Section 3.3 used different external evidence by
    domain: unseen workloads and deployment measurements for scheduling,
    held-out kernel-shape evaluation, randomized reference-code checks for
    FlashAttention IR edits, and expert confirmation for final changes.
  - Current evidence: `libreevolve.systems_result_report.v1` validates
    optimization, held-out, and reference-correctness gates plus artifact
    references, and can reject readiness when required passed-gate artifacts are
    missing. Its readiness rule still accepts documented `not_applicable`
    held-out or reference-correctness gates without domain-specific policy, so
    the report contract does not yet enforce when kernel/compiler/hardware/
    scheduling claims must include reference-code, held-out, deployment, or
    expert-confirmation evidence.
  - Required result: when systems fixtures or report validators add
    domain-specific readiness policies for `not_applicable` gates and required
    evidence types, update the roadmap, README, papers index, and code/paper
    TODO entries together so roadmap wording neither underclaims current report
    validation nor overclaims AlphaEvolve-style systems evidence.

- [ ] Keep systems-result roadmap wording scoped to finite metrics versus
      claim-calibrated result reports.
  - Spec evidence: AlphaEvolve Section 3.3 reports concrete result magnitudes
    with domain-specific units and baselines: Borg fleet-wide resource
    recovery, Gemini/Pallas kernel speedups and training-time reduction,
    hardware power/area objectives, and FlashAttention kernel plus
    pre/postprocessing speedups.
  - Current evidence: roadmap systems-result wording says
    `libreevolve.systems_result_report.v1` validates finite metrics and
    separates optimization, held-out, and reference-correctness gates. It does
    not yet require metric-unit, denominator, baseline, aggregation,
    before/after window, runtime/deployment/synthesis context, or a mapping
    from a report metric to a published AlphaEvolve Section 3.3 claim.
  - Required result: when systems fixtures or report validators add
    claim-calibrated metric records for scheduling, kernel, hardware, and
    compiler result magnitudes, update ROADMAP, README, papers index, and
    code/paper TODOs so roadmap text distinguishes generic finite metrics from
    reproducible AlphaEvolve result-claim evidence.

- [ ] Keep scheduling roadmap wording scoped to generic systems reports until
      ranking-only feasibility evidence exists.
  - Spec evidence: AlphaEvolve's Borg scheduling heuristic only scores
    machines that Borg already determined were available and capable of
    running the job, so the heuristic influences ranking without owning
    feasibility or admission decisions.
  - Current evidence: roadmap systems-result wording names unseen workload,
    deployment, and domain-specific readiness gaps, while current report
    validation allows scheduling reference correctness to be `not_applicable`
    with a rationale. It does not require scheduling-specific feasibility
    filter provenance or proof that evolved code is only a ranking heuristic
    over feasible machines.
  - Required result: when scheduling fixtures or report validators add
    feasible candidate-set provenance, ranking-only boundaries,
    resource/capacity invariant checks, and simulator/admission-boundary
    evidence, update ROADMAP, README, papers index, and code/paper TODOs so
    roadmap text distinguishes generic systems readiness from Borg-style
    correctness-by-construction scheduling evidence.

- [ ] Keep scheduling roadmap wording scoped to generic systems reports until
      interpretability/deployment-readiness evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.1 says the scheduling heuristic was
    preferred over deep reinforcement learning not just for performance, but
    because code-level interpretability, debuggability, predictability, and
    ease of deployment were essential for the mission-critical Borg setting.
  - Current evidence: roadmap systems-result wording covers generic held-out,
    reference, deployment, and domain-specific readiness gaps, and a separate
    scheduling item covers ranking-only feasibility. It does not yet require
    scheduling reports to prove interpretable heuristic structure, operator
    review, predictable behavior, deployment ergonomics, or comparison against
    black-box learned baselines.
  - Required result: when scheduling fixtures or systems report validators add
    interpretability/debuggability fields, predictability checks,
    operator-review artifacts, rollout-risk evidence, and baseline comparison
    against less interpretable policies, update ROADMAP, README, papers index,
    and code/paper TODOs so roadmap text distinguishes generic systems
    readiness from mission-critical Borg-style deployment evidence.

- [ ] Keep kernel roadmap wording scoped to generic systems reports until
      Pallas shape-split/runtime evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.2 optimizes Gemini Pallas tiling
    heuristics on real TPU runtime, using realistic user-collected input
    shapes split into training and evaluation halves, while preserving
    correctness by construction because only tiling strategy changes.
  - Current evidence: roadmap systems-result wording covers generic held-out
    and reference-correctness gaps, but it does not require kernel-specific
    shape-corpus provenance, deterministic train/eval split records, real TPU
    runtime measurement artifacts, expert-baseline comparison, or tiling-only
    correctness boundaries.
  - Required result: when kernel fixtures or systems report validators add
    shape-corpus, train/eval split, accelerator-runtime, baseline-heuristic,
    tiling-constraint, and unchanged-operation evidence, update ROADMAP,
    README, papers index, and code/paper TODOs so roadmap text distinguishes
    generic systems readiness from AlphaEvolve-style Pallas kernel-tiling
    evidence.

- [ ] Keep hardware roadmap wording scoped to generic systems reports until
      RTL/EDA verification evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.3 reports Verilog RTL optimization
    for a TPU arithmetic circuit, with power/area objectives, robust
    functional verification, TPU-designer validation, and downstream synthesis
    confirmation.
  - Current evidence: roadmap systems-result wording covers generic
    optimization, held-out, reference-correctness, deployment, and
    domain-specific readiness gaps. It does not yet require hardware-specific
    HDL source boundaries, synthesis/PPA metric provenance, equivalence/formal
    verification artifacts, timing constraints, designer signoff, or synthesis
    tool confirmation.
  - Required result: when hardware fixtures or systems report validators add
    RTL/EDA source, synthesis, equivalence, PPA, timing, and review evidence,
    update ROADMAP, README, papers index, and code/paper TODOs so roadmap text
    distinguishes generic systems readiness from AlphaEvolve-style hardware
    circuit optimization evidence.

- [ ] Keep compiler-IR roadmap wording scoped to final reference gates until
      per-edit randomized checks exist.
  - Spec evidence: AlphaEvolve Section 3.3.4 checks each FlashAttention
    compiler-IR modification against reference code on randomized inputs, then
    separately reports final expert confirmation for all possible inputs.
  - Current evidence: roadmap systems-result wording covers generic
    reference-correctness and expert-confirmation gaps, but current report
    validation does not require per-edit randomized reference-check traces,
    input-generator provenance, numerical tolerance policy, or attribution of
    improvements to the kernel versus pre/postprocessing IR levels.
  - Required result: when compiler/kernel fixtures or report validators add
    edit-sequence reference-check artifacts, reference-code hashes,
    randomized-input coverage, tolerance/failure policy, abstraction-level
    attribution, and expert signoff scope, update ROADMAP, README, papers
    index, and code/paper TODOs so roadmap text distinguishes final
    correctness gates from AlphaEvolve-style compiler-IR optimization traces.

- [ ] Keep representative-fixture roadmap wording scoped to registries and
      smoke examples versus real target suites.
  - Spec evidence: AlphaEvolve-style benchmark coverage should include
    non-toy target suites for matrix multiplication, constructive math,
    geometric packing, and at least one safe compiler/hardware/kernel/
    scheduling-style systems domain, with validators, repeated seeds, target
    baselines, and artifacts.
  - Current evidence: `ROADMAP.md` asks for stronger fixtures beyond toy
    examples, including matrix-multiplication variants, kissing/circle-packing
    extensions, constructive math, and one safe systems-style microbenchmark.
    README, papers index, and code evidence show checked registries for the 54
    AlphaEvolve Appendix A matrix targets and thirteen Appendix B constructive
    math families, a checked Strassen 2x2 baseline bundle helper, example-scope
    records that mark shipped examples as `alphaevolve_comparable: false`, and
    a scope-checked matrix smoke hardening bundle. Those are coverage and
    report-contract surfaces. The Appendix A matrix registry records target
    identities, dimensions, and rank/outcome metadata, not target tensors,
    discovered decompositions, coefficient data, per-target certificates,
    notebook exports, or construction provenance. The Appendix B registry is
    likewise a family/status ledger: planned paper-result families keep null
    target-baseline values, and construction/certificate artifact-schema labels
    are not executable validators, reported constructions, SOTA thresholds, or
    verifier scripts. Appendix B says construction data and verification code
    for all reported constructions appear in an accompanying Google Colab, and
    the current registry has no equivalent construction-data export or runnable
    verifier-code artifact contract. Current surfaces are not implemented
    tensor-decomposition suites, kissing-number/circle-packing benchmark
    families, constructive-math validators, or
    compiler/hardware/kernel/scheduling fixtures.
  - Required result: when real target-suite fixtures, validators, repeated-seed
    runs, target/SOTA baselines, target tensors, coefficient/certificate
    artifacts, executable construction/certificate checks, Colab-equivalent
    construction-data and verifier-code exports, and artifact/report emitters
    land for matrix, constructive-math, geometric, or systems domains, update
    the roadmap, README, papers index, and code/paper TODO entries together so
    roadmap wording neither underclaims current registries/smoke fixtures nor
    overclaims AlphaEvolve-scale benchmark coverage.

- [ ] Keep Appendix A matrix-suite roadmap wording scoped to target identities
      versus curation provenance.
  - Spec evidence: AlphaEvolve Appendix A says the 54 reported matrix sizes
    were chosen roughly from dimensions with 2 <= m,n <= 5 and a reasonable
    cutoff for p, while tensor symmetries make axis permutations equivalent and
    motivate sorted target representatives.
  - Current evidence: roadmap/README/paper-index status points to the checked
    54-target Appendix A registry. That registry records target identities,
    dimensions, ranks, and outcomes, but not the selection rule,
    symmetry-class/canonical-representative policy, omitted equivalent targets,
    cutoff rationale, or included/excluded target justifications.
  - Required result: when Appendix A matrix curation metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap text
    distinguishes target-identity coverage from paper-faithful target-suite
    curation evidence.

- [ ] Keep matrix roadmap wording scoped to result-report validation versus
      search-time near-integrality evidence.
  - Spec evidence: AlphaEvolve Section 3.1 describes prompting for
    near-integral matrix solutions and rounding entries to the nearest integer
    or half-integer before exactness verification.
  - Current evidence: roadmap benchmark language points to stronger matrix
    fixtures, Appendix A registry coverage, and report contracts that validate
    coefficient-domain and exactness fields. Those are not yet a roadmap claim
    that LibreEvolve injects the near-integrality instruction into matrix
    prompts, records raw-versus-rounded coefficient diagnostics, or links those
    diagnostics to per-seed exactness certificates during evaluator runs.
  - Required result: when a matrix benchmark runner adds prompt/evaluator
    evidence for near-integral coefficient generation and rounding/exactness
    linkage, update roadmap, README, papers index, and code/paper TODO entries
    together so roadmap text distinguishes report validation from
    AlphaEvolve-style matrix search workflow parity.

- [ ] Keep matrix roadmap wording scoped to reported targets until scaling
      resource-frontier evidence exists.
  - Spec evidence: AlphaEvolve Appendix A reports that larger matrix sizes
    beyond the table often ran out of memory when evaluated with 1000 random
    seeds on a single GPU accelerator, making further optimization necessary
    for extending the target suite.
  - Current evidence: roadmap and report-contract language cover the reported
    Appendix A target registry, matrix result artifacts, generic runtime
    budget accounting, and accelerator-environment hints. They do not yet
    require matrix-specific attempted-target rows, GPU memory/resource
    diagnostics, seed-count tradeoff records, or a clear policy for target
    inclusion/exclusion beyond the reported suite.
  - Required result: when matrix scaling/resource-frontier report fields land,
    update ROADMAP, README, papers index, and code/paper TODOs together so
    roadmap text distinguishes AlphaEvolve-comparable reported-target evidence
    from unsupported claims about larger matrix target scalability.

- [ ] Keep matrix roadmap wording scoped to result artifacts until evolved
      sweep-space provenance exists.
  - Spec evidence: AlphaEvolve Figures 9a-9c show matrix search programs
    evolving a `sweep()` function over user-provided `hyper` ranges, not just
    a final tensor-decomposition artifact.
  - Current evidence: roadmap benchmark language points to matrix result
    contracts, Appendix A registry coverage, checked Strassen artifacts, and
    near-integrality/scalar-field follow-ups. It does not yet require
    candidate-produced sweep-space metadata, sampled sweep configuration
    records, per-sweep outcomes, or linkage from a selected sweep
    configuration to the final exact certificate.
  - Required result: when matrix benchmark runners persist evolved sweep
    functions, hyperparameter ranges, sampled configuration ids, per-sweep
    diagnostics, and certificate linkage, update ROADMAP, README, papers
    index, and code/paper TODO entries together so roadmap text distinguishes
    final result artifacts from AlphaEvolve-style matrix search-program
    provenance.

- [ ] Keep matrix roadmap wording scoped to final reports until
      baseline-component provenance exists.
  - Spec evidence: AlphaEvolve Section 3.1 starts matrix-decomposition search
    from a standard gradient-based algorithm including an initializer,
    reconstruction loss function, and Adam optimizer, then evolves the search
    program from that baseline.
  - Current evidence: roadmap benchmark language points to matrix result
    contracts, Appendix A registry coverage, checked Strassen artifacts, and
    follow-ups for near-integrality, sweep spaces, scalar fields, and scaling
    resource frontiers. It does not yet require run artifacts that inventory
    the generation-0 matrix solver components, record their hashes/config, mark
    fixed versus mutable scopes, or link accepted mutations to changed
    initializer/loss/optimizer/search-code components.
  - Required result: when matrix benchmark runners persist baseline component
    inventory, generation-0 outcomes, mutable-scope declarations, and mutation
    lineage, update ROADMAP, README, papers index, and code/paper TODO entries
    together so roadmap text distinguishes final result/report readiness from
    AlphaEvolve Section 3.1 baseline-to-evolved-program parity.

- [ ] Keep matrix roadmap wording scoped to coefficient-domain validation
      until scalar-field evidence exists.
  - Spec evidence: AlphaEvolve Table 2 and Section 3.1 distinguish
    complex-valued matrix multiplication algorithms, exact real/complex
    applicability, and characteristic-0 claims from finite-field-only results.
  - Current evidence: roadmap and report-contract language mention
    coefficient-domain and exactness validation, but current matrix metadata
    does not record scalar field, exact complex coefficient representation,
    characteristic, or certificate scope for real-versus-complex applicability.
  - Required result: when matrix reports gain scalar-field/domain declarations
    and certificate evidence for complex-valued and characteristic-specific
    claims, update roadmap, README, papers index, and code/paper TODO entries
    together so roadmap text distinguishes coefficient-domain validation from
    AlphaEvolve-style scalar-field result provenance.

- [ ] Keep the non-toy benchmark follow-up scoped to an executed fixture with
      expected artifacts.
  - Spec evidence: AlphaEvolve-style benchmark evidence needs repeatable
    target-family runs with saved outputs, validator/certifier artifacts,
    target/SOTA baselines, and expected report files, not only smoke examples
    or schema validators for reports that may exist later.
  - Current evidence: `ROADMAP.md` lists "Add one non-toy benchmark run
    fixture with expected artifacts" as a good first follow-up. Current code
    and docs provide smoke fixtures (`hello_world`, `sorting`,
    `workspace_math`, `matrix_multiplication`, and `circle_packing`),
    Appendix A/B registries, benchmark hardening/report contracts, systems and
    certification report contracts, ablation report contracts, and one checked
    Strassen baseline bundle. Those surfaces validate scope, schemas, and
    declared artifact availability, but they do not yet provide a non-toy
    benchmark run fixture whose command produces expected benchmark artifacts
    from an actual repeated-seed target run.
  - Required result: when the first non-toy benchmark fixture lands, update the
    roadmap, README, papers index, and code/paper TODO entries together with
    the runnable command, expected artifact paths, verifier/report contracts,
    target/SOTA baseline, seed/budget policy, and evidence that the fixture is
    not merely a smoke example or predeclared static artifact bundle.

- [ ] Keep heuristic-search benchmark roadmap wording scoped to real
      incumbent-construction handoff support.
  - Spec evidence: AlphaEvolve Section 3.2 mathematical applications evolved
    search heuristics that were given a fixed budget and a previous best
    construction to improve, not just standalone final construction validators.
  - Current evidence: roadmap and TODO entries already ask for constructive
    math benchmarks, target/SOTA baselines, construction artifacts, and
    certificate validators. Current code supports static context files and
    evaluator artifact copy-out, but no roadmap-backed runtime or benchmark
    contract yet models the incumbent-construction input, candidate heuristic
    output, budget record, and improvement verification as a first-class loop.
  - Required result: when heuristic-search benchmark runners land, update
    roadmap, README, papers index, and code/paper TODO entries together with
    the incumbent-construction schema, budget policy, result-artifact paths,
    verifier/certificate hooks, and evidence that this is more than static
    context injection or smoke artifact export.

- [ ] Keep constructive-math coverage roadmap wording scoped to family
      registries until aggregate outcome reports exist.
  - Spec evidence: AlphaEvolve Section 3.2 claims breadth over a curated set
    of more than 50 mathematical problems spanning more than five branches,
    with best-known constructions matched in about 75% of cases and SOTA
    improved in about 20%.
  - Current evidence: `ROADMAP.md`, README, papers index, and code evidence
    describe Appendix B family/status coverage, smoke fixture boundaries,
    expected construction/certificate artifacts, and missing Colab-equivalent
    verifier data. They do not yet require per-problem/per-parameter outcome
    rows, branch labels, prior-best references, matched/improved/fell-behind
    status, or aggregate percentage validation for Section 3.2 claims.
  - Required result: when constructive-math outcome ledgers and validators
    land, update roadmap, README, papers index, and code/paper TODOs together
    so roadmap wording neither underclaims the current Appendix B family
    registry nor overclaims AlphaEvolve-style mathematical breadth evidence.

- [ ] Keep Appendix B roadmap wording scoped until revised-result provenance
      exists.
  - Spec evidence: AlphaEvolve Appendix B includes result-level revision
    history, most clearly in the uncertainty-inequality note where an initial
    `C4 <= 0.3521` result is superseded after the first manuscript version by
    an improved `0.3216` constant linked to a refined approach and the
    accompanying Google Colab.
  - Current evidence: `ROADMAP.md`, README, papers index, and the Appendix B
    registry describe family coverage, planned/smoke status, target-baseline
    placeholders, and missing verifier data. They do not require versioned
    per-result values, superseded/current status, update notes, source
    manuscript version, attribution, or artifact linkage for revised
    mathematical constants.
  - Required result: when Appendix B result-version provenance lands, update
    ROADMAP, README, papers index, and code/paper TODO entries together with
    revision-aware result rows and validation so roadmap wording cannot treat a
    family/status registry as current AlphaEvolve Appendix B result evidence.

- [ ] Keep benchmark metric-range roadmap wording scoped to documented smoke
      normalization versus real target/SOTA baselines.
  - Spec evidence: AlphaEvolve-style benchmark fixtures should make reachable
    metric ranges, target/SOTA values, and normalization behavior explicit so
    progress comparisons remain ordered and paper-facing claims are auditable.
  - Current evidence: `ROADMAP.md` asks to document reachable metric ranges,
    target/SOTA values, and normalization behavior for benchmark fixtures.
    README documents the checked-in `matrix_multiplication` example as a 2x2
    smoke fixture whose inverse-count metric is normalized over the full
    `1/count` range, while matrix and systems report contracts validate target
    identity, dimensions, comparable-claim flags, finite metrics, and artifact
    records for reports that already exist. The current example-scope registry
    still marks smoke examples as not AlphaEvolve-comparable, and no general
    benchmark-fixture contract yet records reachable ranges, target/SOTA
    thresholds, or normalization semantics for tensor, geometric, compiler,
    hardware, kernel, scheduling, or systems fixtures.
  - Required result: when real benchmark fixtures gain metric-range catalogs,
    target/SOTA baselines, normalization-policy records, or comparable
    report-generation scripts, update the roadmap, README, papers index, and
    code/paper TODO entries together so roadmap wording neither underclaims
    current smoke normalization evidence nor overclaims AlphaEvolve-grade
    benchmark calibration.

- [ ] Keep local domain-paper roadmap wording tied to explicit benchmark or
      background-only status.
  - Spec evidence: AlphaEvolve-related application-domain papers should not be
    implied as supported benchmark coverage unless a concrete fixture,
    evaluator, target baseline, artifact workflow, and report contract connect
    the paper row to runnable evidence.
  - Current evidence: `ROADMAP.md` requires each local domain paper to either
    gain a benchmark, link to an existing benchmark, or remain background-only
    in `papers/README.md`. The paper index currently marks Magellan,
    ArchAgent, Multiagent Learning, Hardness of Approximation, Bilateral
    Trade, and Fault2Flow as background-only application-context rows, and it
    keeps constructive-math and comparator rows as potential future benchmarks
    unless validators are added. The systems-result and benchmark-hardening
    contracts validate reports once concrete fixtures exist, but they do not
    create compiler, architecture, game-theoretic, graph-certification,
    mechanism-design, workflow, or constructive-math benchmark implementations.
  - Required result: when a local domain-paper row changes status, update
    `papers/README.md`, the roadmap, README, paper TODOs, and code TODOs
    together so each row remains either linked to runnable benchmark/report
    evidence or explicitly background-only/candidate-only without overclaiming
    AlphaEvolve application coverage.

- [ ] Keep ablation roadmap wording scoped to report validation versus executed
  experiment scripts.
  - Spec evidence: AlphaEvolve Figure 8 compares equal-budget ablation curves
    from actual runs, not only records that satisfy a result-report schema.
  - Current evidence: `libreevolve.alphaevolve_ablation_report.v1` validates
    reports for the Figure 8 full-system baseline plus five component
    ablations, three seeds, required budget fractions, finite scores, budget
    consistency, component assertions, and hashed curve artifacts, while
    README/TODO text still says no benchmark script emits those reports yet.
  - Required result: when benchmark scripts emit equal-budget ablation reports,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so they neither underclaim the report contract nor overclaim
    executed ablation experiments.

- [ ] Keep benchmark-script roadmap wording scoped to report contracts versus
      runnable ablation harnesses.
  - Spec evidence: AlphaEvolve-style ablations require repeatable benchmark
    scripts that run comparable backend, seed, prompt, and archive variants and
    report progress at equal compute-budget fractions, not only final
    generation counts or hand-authored report files.
  - Current evidence: `ROADMAP.md` separately asks to add repeatable benchmark
    scripts for backend, seed, prompt, and archive ablations and to report
    benchmark progress at comparable compute-budget fractions. README and code
    evidence show `libreevolve.alphaevolve_ablation_report.v1` validates
    declared Figure 8-style report shape, exactly three seeds, required
    equal-budget fractions, finite scores, consumed-budget consistency, and
    artifact references, while `alphaevolve_ablations.json` defines the named
    variants. Some registry `required_config_assertions` are currently
    declarative component labels rather than runnable `Config` fields, such as
    `candidate_source`, `archive_admission_enabled`,
    `candidate_workspace_mode`, `file_create_delete_enabled`,
    `ensemble_strategy: single_backend`, and `backend_capability_tier`. Those
    validators do not schedule runs, enforce backend/seed/prompt/archive
    variants, bind every component assertion to executable runtime controls,
    collect intermediate progress from real experiments, or generate
    equal-budget reports from executable benchmark scripts.
    For `No evolution`, the current registry does not prove that every prompt
    repeatedly feeds the same initial program with no database-selected parent,
    inspiration, previous-candidate feedback, or archive-feedback context.
    For `No context in the prompt`, the current registry does not prove that
    executed prompts omitted explicit context files, sampled prior-program or
    inspiration context, recent failure feedback, and plugin context; it only
    carries definition-only component labels and declarative config assertions.
    For `Small base LLM only`, the current registry does not prove every
    mutation-generation call used exactly one small/base-capable backend with
    no large-model routing, fallback, critique, or ensemble leakage.
    For `No meta prompt evolution`, the current registry does not prove that
    meta-prompt role calls, prompt-template mutations, and prompt-program
    lineage updates were absent in the ablation while present or eligible in
    the full-system comparator.
    For `No full-file evolution`, the current registry also does not encode
    AlphaEvolve's tensor-decomposition-specific loss-function-only restriction;
    broad single-file/diff/no-create-delete labels are not the same as proving
    only the loss function was mutable.
    The current report contract is also target-family generic: tests use a
    placeholder `hello_world` target, and neither the registry nor report
    validator requires Figure 8's matrix tensor-decomposition and
    kissing-number sphere-packing target families, per-target curve summaries,
    target-metric identity/direction/normalization, or intra-target
    standard-deviation evidence over three independent seeds.
  - Required result: when runnable ablation harnesses, backend/seed/prompt/
    archive script entrypoints, component-assertion-to-config binding,
    progress-at-budget-fraction exports, or generated report bundles land,
    update the roadmap, README, papers index, and code/paper TODO entries
    together so roadmap wording neither underclaims the current ablation
    report contract nor overclaims repeatable AlphaEvolve-grade benchmark
    execution. Ensure the `No evolution` harness records prompt/history
    evidence that the same initial program was used for every proposal and
    that evolutionary database feedback was absent. Ensure the
    `No context in the prompt` harness records prompt
    history or diagnostics proving absent explicit context, parent/inspiration
    context, recent failure feedback, and plugin context. Ensure the
    `Small base LLM only` harness records backend metadata, eligibility, and
    call-ledger evidence proving every relevant generation call used a single
    small/base model and no large-model route. Ensure the
    `No meta prompt evolution` harness records prompt-history, call-ledger, and
    prompt-program lineage evidence proving meta-prompt evolution was disabled
    for the ablation and enabled for the full-system comparator. Ensure the
    `No full-file evolution` harness records the
    loss-function target scope, fixed tensor-search components, and report
    evidence before claiming parity with Figure 8. Also require ablation
    reports to identify the matrix and kissing-number target families and
    validate target-metric identity/direction/normalization plus
    mean/standard-deviation curve summaries against per-target three-seed
    records before treating generic declared-target reports as
    Figure 8-equivalent.

- [ ] Keep critique-reviewer roadmap wording scoped to synchronous first/last
      valid mutation selection.
  - Spec evidence: AlphaEvolve-style critique/reviewer channels need calibrated
    reviewer signals, explicit budget/reliability evidence, async or parallel
    reviewer overlap where useful, and provider isolation strong enough to
    audit reviewer effects separately from ordinary mutation generation.
  - Current evidence: `ROADMAP.md` asks to extend synchronous configurable
    critique reviewer pools, role routing, and first/last-valid aggregation
    toward async overlap, calibrated scoring, stronger provider isolation, and
    reviewer-specific runtime artifacts. README and code TODO evidence show
    current `critique_reviewers` accepts manifest-safe reviewer specs with
    optional prompts and role labels such as `critique:correctness`; existing
    role backend routing, role budgets, and reward-accounting telemetry can
    apply to those roles; the loop runs a bounded synchronous reviewer pool;
    `critique_aggregation_policy` selects `first_valid` or `last_valid`
    revised mutations; and retained `metadata.critique.reviewer_pool` records
    reviewer status, parser diagnostics, backend indices, selected reviewer,
    and selection provenance. Reviewer calls are still sequential,
    replacement-only, and chosen by first/last valid mutation rather than
    calibrated reviewer score or benchmarked reviewer reliability.
  - Required result: when async reviewer overlap, calibrated reviewer scoring,
    reviewer-pool ablation reports, stronger per-reviewer provider isolation,
    or richer reviewer-specific timeout/failure artifacts land, update the
    roadmap, README, papers index, and code/paper TODO entries together so
    roadmap wording neither underclaims current synchronous reviewer-pool
    metadata nor overclaims AlphaEvolve-grade critique orchestration.
