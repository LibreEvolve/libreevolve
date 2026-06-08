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

- [ ] Keep multi-evaluator roadmap wording scoped until evaluator-oracle
      composition evidence exists.
  - Spec evidence: AlphaEvolve's abstract describes feedback from one or more
    evaluators, and Section 2.4 distinguishes the core evaluation function
    from optional cascades and LLM-generated feedback.
  - Current evidence: ROADMAP and README can describe one local cascade
    evaluator with configured stages/samples/thresholds plus optional LLM
    feedback graders. They do not yet require independent evaluator/oracle
    identities, task authority, metric ownership, merge/conflict rules, or
    evidence for how evaluator disagreements affect validity, reporting,
    archive admission, and prompt feedback.
  - Required result: when evaluator-oracle composition metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODOs together
    so roadmap wording separates local staged validation and post-hoc graders
    from AlphaEvolve-style multi-evaluator feedback.

- [ ] Keep execution-grounding roadmap wording scoped until incorrect-
      suggestion filtering evidence exists.
  - Spec evidence: AlphaEvolve's introduction says LLM-directed evolution is
    grounded by code execution and automatic evaluation, and that this
    mechanism avoids incorrect suggestions from the base LLM while letting
    feedback drive candidates far from the initial pool.
  - Current evidence: `ROADMAP.md`, README, and paper TODOs can cite local
    evaluator execution, structured result validation, `is_valid` admission,
    rejected-candidate diagnostics, malformed-output failures, and bounded
    failure feedback. They do not yet require roadmap-level proposal-lifecycle
    evidence that proves incorrect generated suggestions are filtered by
    execution/evaluation before they can support accepted discovery claims.
  - Required result: when execution-grounding reports land, update ROADMAP,
    README, papers index, and code/paper TODOs with proposal id, backend/model
    id, mutation payload hash, execution/evaluator outcome, validity/admission/
    retention status, rejection reason, evaluator-oracle sufficiency,
    feedback/failure-memory linkage, and aggregate false-acceptance/false-
    rejection review fields before claiming AlphaEvolve-style filtering of
    incorrect base-LLM suggestions.

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

- [ ] Keep Figure 1/Figure 2 roadmap wording scoped until process-diagram
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 1 shows the high-level architecture from
    human-defined problem inputs through LLM ensemble, prompt sampler,
    evaluator pool, and program database to an improved solution. Figure 2
    expands the loop with database sampling, prompt construction, LLM diff
    generation, diff application, evaluator execution, and database admission.
  - Current evidence: ROADMAP and README describe local components and
    synchronous workflow behavior, while other TODOs track specific gaps for
    prompt sampling, LLM scheduling, evaluators, database memory, and async
    controller state. They do not require Figure 1/Figure 2 exhibit IDs,
    node/edge-to-component mappings, implemented versus unsupported status per
    diagram node, source PDF/caption locations, rendered diagram artifacts and
    hashes, or links from each displayed process step to current run artifacts.
  - Required result: when Figure 1/Figure 2 architecture/process provenance
    lands, update ROADMAP, README, papers index, and code/paper TODOs with
    diagram-level metadata and validators so roadmap wording distinguishes
    local workflow documentation from reproduced AlphaEvolve process-diagram
    evidence.

- [ ] Keep evaluator-workload roadmap wording scoped until inner-search and
      ML-training provenance exists.
  - Spec evidence: AlphaEvolve Section 2.1 says the evaluator can perform a
    simple property check, run an evolved search algorithm, or train and
    evaluate a machine-learning model before returning scalar metrics.
  - Current evidence: ROADMAP and README can cite local subprocess validators,
    configured stages, samples, retries, seeds, budgets, artifact copy-out,
    problem-local dependency provenance, and environment audit records. They do
    not yet require workload-type declarations, dataset/split hashes,
    training/search budget records, checkpoint/artifact policy, randomized
    initialization semantics, or score-field linkage for model-training or
    inner-search evaluators.
  - Required result: when evaluator-workload metadata and reports land, update
    ROADMAP, README, papers index, and code/paper TODOs together so roadmap
    wording distinguishes quick validators from AlphaEvolve-style evaluator
    workloads that perform substantial search or model training.

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

- [ ] Keep evolve-block integration roadmap wording scoped until
      minimal-marker evidence exists.
  - Spec evidence: AlphaEvolve Section 2.1 says special comment markers let the
    system evolve multiple components in existing codebases while requiring
    only minimal changes.
  - Current evidence: ROADMAP, README, and papers-index wording can cite
    Python evolve-block markers, marker validation, unsupported non-Python
    marker diagnostics, workspace materialization, and file topology support.
    They do not yet require evidence for a pre-existing codebase integration
    workflow: marker-only setup diff, preserved skeleton hashes, language
    comment syntax, evolved-block span inventory, evaluator-call continuity,
    or setup-change counts.
  - Required result: when existing-codebase integration metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODO entries
    together so roadmap wording separates marker parser support from
    AlphaEvolve-style minimal-change integration evidence.

- [ ] Keep marker roadmap wording scoped until Figure 3 marker-variant
      metadata exists.
  - Spec evidence: AlphaEvolve Section 2.1 names the marker comments as
    `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END`, while PDF text extraction
    from Figure 3(a) shows one opening marker as `# EVOLVE-BLOCK START` and
    another as `# EVOLVE-BLOCK-START`.
  - Current evidence: ROADMAP can point to local Python evolve-block marker
    parsing, validation, and unsupported marker diagnostics. It does not yet
    require source-location metadata that classifies the Figure 3 marker-text
    variant before roadmap wording treats it as canonical paper prose, rendered
    figure text, extraction/OCR uncertainty, or paper typo.
  - Required result: when Figure 3 marker source metadata lands, update
    ROADMAP, README, papers index, and code/paper TODO entries together so
    roadmap language separates local marker grammar work from any deliberate
    compatibility or documentation decision about the space variant.

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
    a policy that selects the prompt/output mode per candidate size, workspace
    shape, edit scope, prompt arm, or prior failure mode, or records why a
    candidate received a diff versus full-rewrite contract.
  - Required result: when adaptive mutation-mode policy, telemetry, and tests
    land, update roadmap, README, papers index, and code/paper TODO entries so
    roadmap wording includes candidate/task-shape thresholds, per-candidate
    mode telemetry, fallback/critique behavior, and examples proving large
    codebase diff prompts and short-code/full-rewrite prompts are selected
    under documented AlphaEvolve-style conditions without overclaiming current
    configured `diff`/`full` support.

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

- [ ] Keep robustness and versatility roadmap wording scoped until early-user
      feedback provenance exists.
  - Spec evidence: AlphaEvolve's Acknowledgements say early users and
    collaborators supplied diverse use cases and insightful feedback that
    shaped AlphaEvolve into a more robust and versatile tool.
  - Current evidence: ROADMAP and README/code evidence track implemented
    surfaces, benchmark examples, expert formulation gaps, and systems
    owner/reviewer gaps. They do not require roadmap milestones or report
    schemas for early-user/collaborator feedback event IDs, use-case taxonomy,
    affected workflow areas, resulting changes, validation outcomes, or
    privacy/redaction policy.
  - Required result: when feedback-provenance metadata or report evidence
    lands, update roadmap, README, papers index, and code/paper TODO entries
    together so roadmap wording neither underclaims local breadth nor
    overclaims AlphaEvolve-style robustness or versatility shaped by broad
    collaborator feedback.

- [ ] Keep acknowledgement-role roadmap wording scoped until review/support/
      advice provenance exists.
  - Spec evidence: AlphaEvolve's Acknowledgements separately thank named people
    for white-paper review, early explorations and discussions, support and
    advice, practical-application management advice, and reviewing
    application-specific work.
  - Current evidence: ROADMAP and README/code evidence track expert
    formulation, early-user feedback, systems owner/reviewer gaps, and
    contribution-role gaps. They do not require acknowledgement-role metadata
    for paper-process review/support/advice records or docs wording that
    separates those roles from implementation authorship, benchmark
    formulation, domain validation, deployment signoff, or broad collaborator
    feedback.
  - Required result: when acknowledgement-role metadata lands, update ROADMAP,
    README, papers index, and code/paper TODOs with role categories, affected
    paper/application scope, source page/section, and privacy/redaction policy
    so roadmap wording does not treat acknowledgement-process roles as
    technical validation or system-development provenance.

- [ ] Keep paper-author roadmap wording scoped until publication-author
      metadata exists.
  - Spec evidence: AlphaEvolve's Author information names equal contributors
    and corresponding authors, while the Contributions section identifies
    manuscript writers and paper-input contributors.
  - Current evidence: ROADMAP and README/code evidence track contribution-role
    gaps, paper-artifact creator roles, acknowledgement-role gaps, and
    application owner/reviewer gaps. They do not require publication-author
    metadata for equal-contributor status, manuscript-writing roles,
    paper-input roles, or correspondence, nor docs wording that separates those
    metadata from technical implementation, artifact creation, validation, or
    acknowledgement evidence.
  - Required result: when paper-author metadata lands, update ROADMAP, README,
    papers index, and code/paper TODOs with safe contributor labels, author
    role categories, source page/section, publication scope, and contact/
    privacy redaction policy so roadmap wording does not conflate publication
    metadata with AlphaEvolve technical capability provenance.

- [ ] Keep source-affiliation roadmap wording scoped until title-page
      affiliation metadata exists.
  - Spec evidence: page 1 of the AlphaEvolve PDF gives the title-page
    affiliation line `Google DeepMind1` plus footnotes `1See Acknowledgments
    and Author information section.` and `*Equal contributions.`
  - Current evidence: ROADMAP and README can cite LibreEvolve's independent
    non-affiliation statement, source-PDF version/rights TODOs, and
    publication-author metadata gaps. They do not require roadmap evidence for
    title-page affiliation/organization text, footnote marker definitions,
    author-to-marker mapping, source page/span, or docs wording that separates
    source-paper affiliation evidence from local project ownership,
    endorsement, author metadata, and system-development provenance.
  - Required result: when title-page affiliation provenance lands, update
    ROADMAP, README, papers index, and code/paper TODOs with affiliation text,
    marker ids, footnote text, author-marker mappings, source locator, and
    privacy/redaction policy so roadmap wording distinguishes source-paper
    organization metadata from LibreEvolve's affiliation and endorsement
    boundaries.

- [ ] Keep system-development roadmap wording scoped until contribution-role
      provenance exists.
  - Spec evidence: AlphaEvolve's Contributions section attributes core system
    development work across initial implementation, project vision and problem
    scoping, first benchmark iteration, final system development,
    infrastructure maintenance, code reviews, team coordination, and
    supervision.
  - Current evidence: ROADMAP and README can cite local implementation status,
    source provenance, tests, and open contribution guidance. They do not
    require roadmap evidence for contribution-role records, development-phase
    attribution, infrastructure ownership, benchmark-iteration ownership,
    review responsibility, or coordination/supervision scope.
  - Required result: when contribution-role metadata lands, update ROADMAP,
    README, papers index, and code/paper TODOs with role labels, development
    phase, artifact/module linkage, source page/section, and review/approval
    scope so roadmap wording separates local implementation plans from
    AlphaEvolve-style paper-attributed system-development provenance.

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

- [ ] Keep parallel-evaluation roadmap wording scoped until compute-hour
      throughput evidence exists.
  - Spec evidence: AlphaEvolve Section 2.4 says candidate evaluation can spend
    on the order of 100 compute-hours and relies on parallelized evaluator
    work so wall-clock latency does not stall multiple consecutive mutations.
  - Current evidence: ROADMAP lists bounded queues for LLM proposals and
    evaluator workers as future work and notes current sequential
    `proposals_per_generation` batches. Code/paper TODO evidence already
    tracks local evaluator-second counters and expensive-evaluation budget
    gaps. The roadmap should not treat generic async queues as sufficient
    without compute-hour, wall-clock compression, worker fan-out, and
    mutation-depth evidence.
  - Required result: when parallel evaluator execution or reports land, update
    ROADMAP, README, papers index, and code/paper TODOs with per-candidate
    compute-hour budgets, evaluator-worker fan-out, randomized-initialization
    shard counts/seeds, queued/running/completed state, cluster/local execution
    identity, wall-clock versus compute-hour compression, mutation-chain-depth
    impact, pending-work resume behavior, and equal-budget report links.

- [ ] Keep Table 1 roadmap wording scoped until capability-table exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Table 1 is a row-level comparison between
    FunSearch and AlphaEvolve covering code/file scale, code length, language
    scope, evaluator duration/parallelism/accelerators, sample counts, model
    scale, prompt context/feedback, and single versus multiple metrics.
  - Current evidence: `ROADMAP.md`, README, papers index, and code TODOs track
    several individual Table 1 rows as separate implementation/report gaps.
    They do not require Table 1 itself to have stable table/row ids, source
    PDF/caption location, exact comparison text, row-to-TODO/report mappings,
    row-level status, rendered artifact hashes, or validation that partial row
    evidence is not summarized as complete Table 1 parity.
  - Required result: when Table 1 exhibit provenance lands, update ROADMAP,
    README, papers index, and code/paper TODO entries together with table
    metadata and validators so roadmap wording separates paper table
    reproduction from satisfying each underlying capability row.

- [ ] Keep Figure 1 and Figure 2 roadmap wording scoped until process-overview
      exhibit provenance exists.
  - Spec evidence: AlphaEvolve Figure 1 gives the process-level system view
    connecting human task inputs, LLM ensemble, prompt sampler, evaluator
    pool, program database, rich context, proposals, and feedback. Figure 2
    expands the discovery loop into initial-program/evaluation/config inputs
    and controller pseudocode for sampling, prompt building, diff generation,
    diff application, evaluator execution, and database updates.
  - Current evidence: `ROADMAP.md`, README, papers index, and code TODOs track
    several Figure 1/2 component gaps, but the roadmap does not require Figure
    1 or Figure 2 to have stable figure IDs, diagram-node and edge records,
    Figure 2 pseudocode-line mappings, source PDF/caption locations, rendered
    artifact hashes, component-to-code/report/TODO links, or validation that
    partial component coverage is not summarized as full process-diagram
    parity.
  - Required result: when Figure 1/2 process exhibit provenance lands, update
    ROADMAP, README, papers index, and code/paper TODO entries together with
    figure metadata, step-level status, evidence links, rendered artifact
    hashes, and validators so roadmap wording separates paper process-diagram
    reproduction from delivering each underlying AlphaEvolve workflow
    capability.

- [ ] Keep task-specification roadmap wording scoped until a unified
      AlphaEvolve input bundle exists.
  - Spec evidence: AlphaEvolve Section 2.1 and Figure 2 frame task
    specification as one user-provided input bundle: initial program/components
    to evolve, evaluation code, prompt template/configuration, LLM choices,
    and optional background knowledge.
  - Current evidence: `ROADMAP.md`, README, and manifests can describe
    problem/source provenance, seed sources, evaluator sources, backend specs,
    prompt variants, redacted/hash-backed effective config, and context-source
    diagnostics. They do not yet require a single validated task-spec artifact
    with AlphaEvolve field names, presence/omission status, source hashes,
    redaction policy, and links from each input field to the run evidence it
    controls.
  - Required result: when task-spec bundle records land, update ROADMAP,
    README, papers index, and code/paper TODOs with initial code/workspace
    ids, evolvable spans, evaluator-code ids, prompt-template/config ids, LLM
    choice ids, optional background-knowledge ids, hashes/redaction state, and
    missing/unsupported-field diagnostics so roadmap wording separates
    scattered local provenance from a coherent AlphaEvolve task specification.

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

- [ ] Keep multi-metric prompt-context roadmap wording scoped until
      metric-diverse inspiration evidence exists.
  - Spec evidence: AlphaEvolve Section 2.4 says multiple scores can improve
    search because prompts include examples of diverse high-performing
    programs, each representing a different definition of "good".
  - Current evidence: roadmap/README wording can cite declared metrics,
    normalized archive selection, objective-vector diagnostics, metric leaders,
    metric-cell overlays, metric/frontier retained pools, and metric-targeted
    resurfacing. They do not yet require inspiration selection policies,
    prompt-history linkage, or report validation proving prompts intentionally
    include different metric niches in the same rendered context.
  - Required result: when metric-diverse inspiration selection lands, update
    ROADMAP, README, papers index, and code/paper TODOs together so roadmap text
    distinguishes multi-metric bookkeeping/resurfacing from AlphaEvolve-style
    diverse-metric prompt context.

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

- [ ] Keep paper-index backlog-traceability roadmap wording scoped until TODO
      coverage cross-references are validated.
  - Spec evidence: AlphaEvolve-alignment planning depends on every paper
    status row being traceable to concrete active or completed backlog
    evidence. `papers/README.md` includes a TODO coverage cross-reference
    table for this purpose.
  - Current evidence: roadmap/README/papers-index wording can cite manifest
    validation, implementation-status table reconciliation, Appendix B and
    ablation registry checks, and a checked-in test that every manifest id has
    a cross-reference row mentioning `docs/todo/`. It does not require a
    reusable validation rule for cross-reference row coverage, referenced path
    existence, grouped-gap labels, active/completed target semantics, or
    whether active targets still contain open TODO evidence.
  - Required result: when paper-index TODO cross-reference validation lands,
    update ROADMAP, README, papers index, and code/paper TODOs with the
    validator scope and failure modes so roadmap wording distinguishes
    shareable cache/status diagnostics from verified backlog traceability.

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

- [ ] Keep explicit-context roadmap wording scoped until context-source roles
      exist.
  - Spec evidence: AlphaEvolve Section 2.2 names explicit prompt context
    categories: fixed human-written instructions, equations, code snippets,
    and relevant literature such as PDF files.
  - Current evidence: ROADMAP, README, and papers-index wording can cite local
    context ingestion, manifests, hashes, PDF extraction, prompt rendering,
    deterministic selection/ranking/filtering, and truncation. They do not yet
    require typed source-role metadata that proves whether a selected source is
    an instruction, equation/formula, code snippet, literature/PDF source, or
    other explicit problem-context artifact rather than generic local context,
    retrieval output, or plugin-supplied text.
  - Required result: when context-source role metadata and validators land,
    update ROADMAP, README, papers index, and code/paper TODO entries together
    so roadmap wording distinguishes file-ingestion mechanics from
    AlphaEvolve-style intentionally typed explicit-context evidence.

- [ ] Keep primary-prompt roadmap wording scoped until instruction/target
      provenance exists.
  - Spec evidence: AlphaEvolve Section 2.2 says the primary evolution prompt
    combines sampled previously discovered solutions with system instructions
    for proposing changes to a particular solution.
  - Current evidence: ROADMAP, README, and papers-index wording can cite
    prompt templates, prompt-program ids, selected parent/inspiration
    metadata, parent-code rendering policy, mutation-instruction variants, and
    prompt-size diagnostics. They do not yet require a prompt-core record that
    links instruction identity/version/hash, target solution id/source hash,
    sampled supporting-solution roles, provider message-role placement,
    edit-scope constraints, and required prompt-channel presence for each
    mutation call.
  - Required result: when primary-prompt ingredient metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODO entries
    together so roadmap wording separates generic prompt-template rendering
    from AlphaEvolve-style target-specific prompt instruction evidence,
    including whether provider calls used role-separated
    system/developer/user messages or a serialized single prompt.

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

- [ ] Keep backtracking roadmap wording scoped until abandoned-hypothesis
      branch evidence exists.
  - Spec evidence: AlphaEvolve's Introduction frames discovery as involving
    ideation, exploration, backtracking on unpromising hypotheses,
    experimentation, and validation, while Section 2.4 describes pruning less
    promising solutions through evaluation cascades.
  - Current evidence: `ROADMAP.md` can describe candidate failures,
    rejected-candidate diagnostics, bounded failure memory, proposal metadata,
    cascade stages, and run-local hypothesis summaries. Those are individual
    records, not branch-level evidence that a hypothesis was abandoned and the
    search deliberately backtracked or redirected.
  - Required result: when hypothesis-branch reports land, update ROADMAP,
    README, papers index, and code/paper TODOs with branch ids,
    proposal/idea-family labels, explored candidate ids, evaluator/cascade
    evidence, abandonment or backtrack decisions, fallback ancestor or
    alternative-branch targets, prompt/failure-memory linkage,
    suppression/retry policy, resumed-search outcomes, and claim-readiness
    checks so roadmap wording separates failure logging from
    AlphaEvolve-style backtracking on unpromising hypotheses.

- [ ] Keep scientific-discovery roadmap wording scoped to automated evaluators
      versus manual-experiment or LLM-only idea-review workflows.
  - Spec evidence: AlphaEvolve's Discussion says its main limitation is that
    it handles problems where an automated evaluator can be devised; domains
    requiring manual experimentation are out of scope, and LLM-provided
    high-level idea evaluation is a possible but not optimized bridge toward
    an implementation stage with machine feedback through code execution. The
    Discussion also says future progress depends on setting up more
    environments or problems with robust evaluation functions.
  - Current evidence: the roadmap tracks executable validators, staged
    evaluator feedback, optional LLM feedback graders, proposal metadata,
    retrieval, and hypothesis-memory follow-ups. It does not yet require
    roadmap-level scope metadata or workflow wording that separates
    machine-gradeable evolution from manual-experiment scientific workflows or
    AI-Co-Scientist-style pre-implementation idea review. It also does not
    require roadmap evidence for evaluator-environment setup readiness:
    robust-evaluator rationale, automatable-domain boundaries, setup effort,
    and expected high-value discovery scope.
  - Required result: when problem/run/report scope metadata lands, update
    ROADMAP, README, papers index, and code/paper TODO entries together so the
    project neither underclaims executable evaluator support nor overclaims
    AlphaEvolve coverage for environment-scaling, manual-experiment, or
    LLM-only idea-feedback workflows.

- [ ] Keep AI-Co-Scientist roadmap wording scoped until representation-
      boundary evidence exists.
  - Spec evidence: AlphaEvolve Related Work distinguishes AI Co-Scientist as
    representing hypotheses and evaluation criteria in natural language, while
    AlphaEvolve evolves code and directs search through programmatic
    evaluation functions. The paper says this programmatic choice helps
    sidestep hallucinations and sustain many evolution time steps, while a
    future method could combine natural-language and programmatic idioms.
  - Current evidence: roadmap/README/paper-index wording can cite executable
    validators, optional LLM feedback, structured proposal metadata, and
    automated-evaluator scope boundaries. It does not require roadmap evidence
    that classifies candidate representation, separates natural-language
    criteria from programmatic criteria, or supports hallucination-resistance
    and long-horizon evolution claims.
  - Required result: when representation-boundary metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs with representation
    mode, evaluation-criterion mode, executable-feedback linkage,
    hallucination-risk controls, long-horizon step-count evidence, and bridge
    status for any natural-language hypothesis stage before claiming
    AlphaEvolve-style distinction from AI-Co-Scientist.

- [ ] Keep Related Work roadmap wording scoped until taxonomy evidence exists.
  - Spec evidence: AlphaEvolve Related Work frames the system as
    execution-feedback code superoptimization, compares it with pre-LLM
    enumeration/genetic-search/Monte-Carlo/deep-RL approaches, AlphaTensor,
    GPU-kernel and LLM-agent optimizers, AI-for-science methods, and proof
    discovery, distinguishes programmatic hypothesis/evaluation and
    witness/counterexample discovery from other scientific-discovery stages,
    and discusses continuous LLM fine-tuning through reinforcement learning
    plus LLM-directed concept learning/summaries of high-performing programs
    as adjacent complementary ideas needing more investigation at
    AlphaEvolve scale.
  - Current evidence: roadmap/README/paper-index status can cite bundled
    papers and specific feature gaps, but it does not require a related-work
    taxonomy that records source ids, method family, task stage, candidate
    representation, evaluator/evidence mode, proof-versus-witness status,
    comparison claim, complementary-mechanism status, or local status for each
    AlphaEvolve Related Work category.
  - Required result: when related-work taxonomy metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap claims
    distinguish broad inspiration and paper availability from AlphaEvolve's
    specific positioning as execution-feedback superoptimization and
    programmatic scientific discovery, including adjacent fine-tuning and
    concept-learning mechanisms that are context rather than local capability.

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

- [ ] Keep multi-edit consistency roadmap wording scoped until checked
      consistency evidence exists.
  - Spec evidence: AlphaEvolve Figure 3(b) instructs the model to keep
    SEARCH/REPLACE edits consistent with each other, including adding a new
    config variable when another proposed edit uses it.
  - Current evidence: `ROADMAP.md`, README, and prompt instructions can
    describe coherent-edit guidance plus current parser, syntax, evaluator,
    and admission checks. They do not yet require a paper-facing consistency
    diagnostic that links multi-block edits, introduced symbols/config/imports/
    resources, missing companion edits, unresolved references, and
    evaluator-failure taxonomy to accepted/rejected candidate status.
  - Required result: when multi-edit consistency reports land, update ROADMAP,
    README, papers index, and code/paper TODOs with changed block/file ids,
    introduced/reference labels, companion-edit links, unresolved-reference
    diagnostics, evaluator-failure taxonomy linkage, proposal/prompt ids, and
    accepted/rejected status so roadmap wording separates prompt-only
    consistency instructions from checked AlphaEvolve-style coherent
    multi-edit mutation evidence.

- [ ] Keep Figure 3 roadmap wording scoped until supervised-learning example
      exhibit provenance exists.
  - Spec evidence: AlphaEvolve Figure 3 is a supervised-learning pipeline
    example with linked source, prompt, and LLM-output subfigures: a
    user-provided JAX/Jaxline file and `evaluate` function, an assembled prompt
    with prior/current program score values, and explanatory SEARCH/REPLACE
    edits.
  - Current evidence: roadmap/README/paper-index status can cite evolve-block
    parsing, prompt rendering, SEARCH/REPLACE mutation support, strict
    preamble handling, and prompt-example-copy gaps. They do not require
    Figure 3 exhibit IDs, subfigure labels, exact source/prompt/output excerpt
    artifacts and hashes, displayed metric values, ellipsis/skipped-line
    policy, source PDF/caption location, rendered artifact paths/hashes, or
    links from the displayed snippets to prompt-history, evaluator,
    candidate-history, and run artifacts.
  - Required result: when Figure 3 exhibit provenance lands, update ROADMAP,
    README, papers index, and code/paper TODOs with exhibit-level metadata and
    validators so roadmap wording distinguishes reproduced supervised-learning
    paper-example evidence from generic prompt, mutation, and evaluator
    support.

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

- [ ] Keep creative-generation roadmap wording scoped until proposal-diversity
      evidence exists.
  - Spec evidence: AlphaEvolve Section 2.3 says SOTA LLMs digest previously
    developed solutions and propose new, diverse ways to improve them, and its
    ablations connect stronger underlying LLMs to better performance.
  - Current evidence: `ROADMAP.md` can describe selected parent/inspiration
    context, proposal metadata, candidate outcomes, sampling strategy metadata,
    bounded hypothesis summaries, and backend/model telemetry. That does not
    yet prove proposal-level diversity or idea novelty across a call, batch,
    generation, prompt context, or backend/model comparison.
  - Required result: when proposal-diversity reports land, update ROADMAP,
    README, papers index, and code/paper TODOs with per-call or per-batch
    idea/operator-family labels, duplicate/near-duplicate diagnostics, code
    and semantic or task-output distances where available, parent/inspiration
    relations, prompt/backend model ids, accepted/rejected outcomes, novelty
    contribution, and equal-budget/model ablation linkage so roadmap wording
    separates current proposal metadata from AlphaEvolve-style SOTA LLM
    creative-generation evidence.

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

- [ ] Keep database-sampling roadmap wording scoped until exploration /
      exploitation balance evidence exists.
  - Spec evidence: AlphaEvolve's database balances exploration and exploitation
    while maintaining diversity across the search space.
  - Current evidence: `ROADMAP.md` can describe configurable `explore_ratio`,
    mixed parent selection, explicit parent/inspiration strategies, MAP-Elites
    cells, islands, metric/frontier sampling, lineage sampling, novelty
    sampling, recency sampling, and bounded current-run resurfacing. It should
    not imply that the current knobs are calibrated database-balance evidence
    or that a run report can explain the improvement/diversity tradeoff.
  - Required result: when sampling-balance reports land, update ROADMAP,
    README, papers index, and code/paper TODO entries with per-run and
    per-generation parent/inspiration decision counts, fallback and source-pool
    provenance, selected-program repetition, island/cell/metric/lineage/
    descriptor coverage, score-improvement versus diversity effects, and
    equal-budget comparisons across exploit, explore, mixed, metric, frontier,
    and lineage policies.

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

- [ ] Keep test-time-compute roadmap wording scoped until repeated-sampling
      baselines exist.
  - Spec evidence: AlphaEvolve's Discussion says the evolutionary procedure
    improves the base LLM compared with repeated sampling, using machine
    feedback to sustain useful test-time compute.
  - Current evidence: roadmap/README/paper-index status can point to LLM
    budget telemetry, generated candidate ids, archive admission records,
    sample-efficiency gaps, and an equal-budget ablation report contract with a
    `No evolution` variant. Those are not yet a controlled repeated-sampling
    comparator with matched prompt/model/seed/evaluator settings and disabled
    evolutionary feedback, parent/inspiration resurfacing, archive-driven
    selection, and meta-prompt updates.
  - Required result: when repeated-sampling baseline reports land, update
    ROADMAP, README, papers index, and code/paper TODOs together so roadmap
    language distinguishes ordinary budgeted LLM sampling and `No evolution`
    labels from AlphaEvolve-style test-time-compute uplift over repeated
    base-model sampling.

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

- [ ] Keep qualitative-feedback roadmap wording scoped until criterion
      provenance exists.
  - Spec evidence: AlphaEvolve Section 2.4 says LLM-generated feedback can
    grade desirable characteristics that are difficult to capture precisely in
    the evaluator, such as simplicity, and can use those grades as scores or
    discard gates.
  - Current evidence: ROADMAP and README can cite configured LLM feedback
    graders, bounded prompts, parsed scores, normalized deltas, discard
    policies, feedback-sourced objective metrics, feedback indexes, and
    calibration-report contracts. They do not yet require qualitative
    criterion declarations, evaluator-gap rationales, rubric/prompt artifact
    hashes, score-versus-discard intent, or report linkage proving that a
    grader represents a specific hard-to-code property.
  - Required result: when qualitative-feedback policy metadata and reports
    land, update ROADMAP, README, papers index, and code/paper TODOs together
    so roadmap wording distinguishes generic post-evaluation LLM scoring from
    AlphaEvolve-style qualitative feedback criteria.

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

- [ ] Keep systems roadmap wording scoped until application-owner and
      domain-review provenance exists.
  - Spec evidence: AlphaEvolve Section 3.3 presents the scheduling, kernel,
    TPU RTL, and XLA/FlashAttention IR systems results as practical
    applications, while the Acknowledgements and Contributions sections name
    application co-leads, domain advisors, reviewers, validation-infrastructure
    owners, TPU designers, and XLA modification reviewers connected to those
    results.
  - Current evidence: roadmap systems-result wording can point to generic
    report contracts, finite metrics, held-out/reference gates, deployment
    evidence, and artifact inventories. It does not yet require roadmap
    milestones or report schemas to preserve application-owner identity,
    domain-reviewer role, reviewer/signoff scope, validation or source-data
    ownership, production approval state, or links from calibrated metrics to
    responsible domain teams.
  - Required result: when report validators or certification metadata add
    owner/reviewer provenance for practical systems claims, update ROADMAP,
    README, papers index, and code/paper TODOs so roadmap wording distinguishes
    local systems benchmarks from AlphaEvolve-style domain-owner validated
    production evidence.

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

- [ ] Keep scheduling roadmap wording scoped until vector-bin-packing
      formulation evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.1 formulates Borg scheduling as an
    online vector bin-packing problem: machines are bins with CPU and memory
    capacity, pending jobs are items with CPU and memory requirements,
    stranded resources motivate the objective, and simulator feedback is based
    on historical workload and capacity snapshots.
  - Current evidence: roadmap systems-result wording covers generic held-out,
    deployment, metric-calibration, ranking-only feasibility, and Figure 6
    exhibit gaps. It does not require scheduling fixtures or report validators
    to declare the CPU/memory bin-item schema, resource units, workload and
    capacity snapshot identities, stranded-resource objective, simulator input
    hashes, or mapping to the heuristic's `required` and `free` features.
  - Required result: when Borg-style scheduling formulation metadata and
    validators land, update ROADMAP, README, papers index, and code/paper TODOs
    so roadmap text separates scheduling problem setup from later evidence for
    ranking-only safety, mission-critical deployment, and fleet-recovery
    metrics.

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

- [ ] Keep Figure 6 roadmap wording scoped until scheduling-heuristic exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 6 presents the concrete Borg scheduling
    heuristic source plus a CPU/memory residual heatmap, and Section 3.3.1
    links that heuristic to simulator feedback, unseen recent workloads,
    deployment, and about 0.7% fleet-wide resource recovery.
  - Current evidence: roadmap systems-result wording covers generic held-out,
    reference, deployment, metric-calibration, ranking-only feasibility, and
    interpretability/deployment gaps. It does not require Figure 6 exhibit
    IDs, exact heuristic source hashes, residual-feature definitions, heatmap
    data/rendering parameters, visual artifact paths/hashes, baseline
    production heuristic identity, or links from the displayed exhibit to
    simulator/held-out/deployment evidence.
  - Required result: when scheduling-heuristic exhibit provenance lands,
    update ROADMAP, README, papers index, and code/paper TODO entries together
    with exhibit-level metadata and validators so roadmap text distinguishes
    generic scheduling readiness, Section 3.3 result claims, and reproduced
    Figure 6 visual/code evidence.

- [ ] Keep Figure 7 roadmap wording scoped until Pallas tiling-problem exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 7 visualizes the matrix-product tiling
    heuristic problem with dimensions `M`, `N`, and `P`, and Section 3.3.2
    frames tile-size selection as dependent on accelerator optimal shapes,
    memory capacity, fused operations, and compiler intricacies.
  - Current evidence: roadmap systems-result wording covers Pallas
    shape-corpus, train/eval split, accelerator-runtime, baseline-heuristic,
    tiling-constraint, and unchanged-operation evidence gaps. It does not
    require Figure 7 exhibit IDs, matrix-shape variable definitions,
    tile-parameter schema, accelerator/memory/fusion/compiler annotations,
    diagram source data, rendered visual artifact paths/hashes, rendering
    parameters, or links from the displayed tiling problem to Pallas runtime
    reports.
  - Required result: when Pallas tiling-problem exhibit provenance lands,
    update ROADMAP, README, papers index, and code/paper TODO entries together
    with exhibit-level metadata and validators so roadmap text distinguishes
    generic kernel readiness, executed Pallas runtime evidence, and reproduced
    Figure 7 visual/problem-definition evidence.

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
    correctness boundaries. It also does not require engineering-effort
    calibration for the paper's several-months-to-days optimization-turnaround
    claim or the deployment/research-velocity impact of the kernel heuristic.
  - Required result: when kernel fixtures or systems report validators add
    shape-corpus, train/eval split, accelerator-runtime, baseline-heuristic,
    tiling-constraint, unchanged-operation evidence, engineering-effort
    baseline, automated-experiment duration, and production/workflow adoption
    state, update ROADMAP, README, papers index, and code/paper TODOs so
    roadmap text distinguishes generic systems readiness from AlphaEvolve-style
    Pallas kernel-tiling evidence.

- [ ] Keep Pallas workflow roadmap wording scoped until autotuning/manual
      heuristic baseline evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.2 says traditional Pallas tiling work
    uses search-based autotuning or manually crafted heuristics. Search-based
    tuning interrupts research workflow and requires retuning for shape changes;
    manual heuristics are a major expert-engineering bottleneck. The paper
    frames AlphaEvolve as a path to automating manual tuning and improving
    ergonomics for Gemini kernel users and emerging hardware.
  - Current evidence: roadmap/README/paper-index wording can cite shape-corpus,
    train/eval split, real TPU runtime, expert-baseline comparison,
    months-to-days optimization turnaround, and production/workflow adoption
    gaps. It does not require kernel reports to classify baseline workflow
    type, record autotuning retune burden, preserve manual heuristic effort, or
    compare model-developer ergonomics across baseline workflow classes.
  - Required result: when Pallas workflow-baseline metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs together so roadmap
    wording distinguishes runtime/speedup evidence from AlphaEvolve-style
    automation of autotuning and manual-heuristic engineering workflows.

- [ ] Keep roadmap Gemini self-training wording scoped until Pallas deployment
      loop evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.2 says the AlphaEvolve-discovered
    Pallas tiling heuristic was deployed in production, enhanced Gemini
    training efficiency and team velocity, and marked a novel instance where
    Gemini, through AlphaEvolve, optimized its own training process.
  - Current evidence: roadmap/README/paper-index wording can cite Pallas
    shape-corpus, real-TPU runtime, expert-baseline, workflow-baseline, and
    production-adoption gaps, plus broad self-improvement boundaries. It does
    not require a Gemini-specific report tying the optimized kernel to the
    training workload of the Gemini model family, the AlphaEvolve/Gemini model
    relationship, before/after training-time evidence, and deployment or
    rollback state.
  - Required result: when Gemini self-training loop metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap claims
    distinguish ordinary production kernel deployment from AlphaEvolve-style
    self-optimization of Gemini's own training pipeline.

- [ ] Keep hardware roadmap wording scoped to generic systems reports until
      RTL/EDA verification evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.3 reports Verilog RTL optimization
    for a TPU arithmetic circuit, with power/area objectives, robust
    functional verification, TPU-designer validation, and downstream synthesis
    confirmation. It also claims value from refining source RTL early in the
    design flow, integrating the improvement into an upcoming TPU, and using
    Verilog as the standard hardware-engineer language to build trust,
    simplify adoption, and potentially reduce time to market.
  - Current evidence: roadmap systems-result wording covers generic
    optimization, held-out, reference-correctness, deployment, and
    domain-specific readiness gaps. It does not yet require hardware-specific
    HDL source boundaries, synthesis/PPA metric provenance, equivalence/formal
    verification artifacts, timing constraints, designer signoff, or synthesis
    tool confirmation. It also does not require RTL-flow placement,
    standard-language adoption evidence, upcoming-chip integration, or
    time-to-market impact.
  - Required result: when hardware fixtures or systems report validators add
    RTL/EDA source, synthesis, equivalence, PPA, timing, review,
    workflow-placement, adoption, integration, and deployment-impact evidence,
    update ROADMAP, README, papers index, and code/paper TODOs so roadmap text
    distinguishes generic systems readiness from AlphaEvolve-style hardware
    circuit optimization evidence.

- [ ] Keep hardware roadmap wording scoped until TPU bit-removal rewrite
      provenance exists.
  - Spec evidence: AlphaEvolve Section 3.3.3 says the hardware result was a
    simple code rewrite in Verilog for a key TPU arithmetic circuit in the
    matrix multiplication unit, and that it removed unnecessary bits while
    reducing area and power.
  - Current evidence: roadmap systems-result wording covers generic hardware
    readiness, RTL/EDA verification, PPA metrics, designer signoff, downstream
    synthesis, adoption, and deployment impact. It does not require hardware
    fixtures or report validators to preserve the concrete rewrite artifact:
    before/after Verilog hashes, changed spans, removed-bit or signal
    inventory, arithmetic-circuit and matrix-unit identifiers, semantic
    rewrite category, or linkage from removed bits to verification and PPA
    evidence.
  - Required result: when TPU arithmetic-circuit rewrite metadata and
    validators land, update ROADMAP, README, papers index, and code/paper TODOs
    so roadmap text separates a reproduced bit-removal rewrite from generic
    RTL verification, downstream synthesis, and hardware deployment evidence.

- [ ] Keep compiler-IR roadmap wording scoped to final reference gates until
      per-edit randomized checks exist.
  - Spec evidence: AlphaEvolve Section 3.3.4 checks each FlashAttention
    compiler-IR modification against reference code on randomized inputs, then
    separately reports final expert confirmation for all possible inputs. It
    also says the XLA-generated IR was designed for debugging rather than
    direct developer editing and was compiler-generated/already highly
    optimized.
  - Current evidence: roadmap systems-result wording covers generic
    reference-correctness and expert-confirmation gaps, but current report
    validation does not require per-edit randomized reference-check traces,
    input-generator provenance, IR-origin/editability constraints,
    compiler-generated baseline provenance, numerical tolerance policy, or
    attribution of improvements to the kernel versus pre/postprocessing IR
    levels.
  - Required result: when compiler/kernel fixtures or report validators add
    edit-sequence reference-check artifacts, reference-code hashes,
    randomized-input coverage, IR provenance/editability metadata,
    tolerance/failure policy, abstraction-level attribution, and expert
    signoff scope, update ROADMAP, README, papers index, and code/paper TODOs
    so roadmap text distinguishes final correctness gates from
    AlphaEvolve-style compiler-IR optimization traces.

- [ ] Keep compiler-stack roadmap wording scoped until FlashAttention context
      provenance exists.
  - Spec evidence: AlphaEvolve Section 3.3.4 describes a concrete compiler
    stack: FlashAttention implements Transformer attention as a Pallas
    accelerator kernel, higher-level JAX code performs input preparation and
    output postprocessing, XLA lowers the implementation through IR stages for
    particular hardware, and the optimized target is a high-impact inference
    configuration on GPUs.
  - Current evidence: roadmap systems-result wording covers generic compiler
    readiness, reference-correctness gaps, expert signoff, and runtime speedup
    calibration. It does not require compiler fixtures or report validators to
    record workload/model configuration, FlashAttention/Pallas kernel identity,
    JAX wrapper boundaries, XLA IR-stage identities, hardware target,
    lowered-IR artifact hashes, or the memory-access/scheduling decision class
    being optimized.
  - Required result: when FlashAttention compiler-stack metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODOs so roadmap
    text separates generic compiler-report support from the specific
    Pallas/JAX/XLA/FlashAttention stack context used for AlphaEvolve's
    compiler-generated IR result.

- [ ] Keep compiler-adoption roadmap wording scoped until integration-path
      evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.4 says discovered compiler
    optimizations may be incorporated into existing compilers for specific use
    cases, while the longer-term possibility is incorporating AlphaEvolve into
    the compiler workflow itself.
  - Current evidence: roadmap systems-result wording covers generic compiler
    readiness, reference-correctness, expert signoff, runtime speedups, and
    FlashAttention stack context. It does not require compiler fixtures or
    report validators to classify whether an optimization was adopted as a
    bounded existing-compiler change or as part of an AlphaEvolve-in-the-loop
    compiler workflow, nor does it require target compiler/pass identity,
    integration owner, use-case constraints, rollout/revert state, or workflow
    handoff evidence.
  - Required result: when compiler report metadata and validators add
    integration-path evidence, update ROADMAP, README, papers index, and
    code/paper TODOs so roadmap text distinguishes concrete optimization
    adoption in existing compilers from future AlphaEvolve compiler-workflow
    integration.

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

- [ ] Keep paper-source roadmap wording scoped until companion Colab artifacts
      are tracked.
  - Spec evidence: AlphaEvolve footnote 2 and Table 2 cite an accompanying
    `google-deepmind/alphaevolve_results` Colab notebook for discovered
    algorithms, mathematical results, and matrix decompositions.
  - Current evidence: roadmap and README text accurately describe the local
    paper manifest as PDF-oriented, and TODOs already require local
    Colab-equivalent Appendix A/B exports once LibreEvolve produces them. They
    do not require a companion source-artifact manifest for the actual
    AlphaEvolve notebook: canonical URL/repository/ref, digest/byte metadata,
    notebook readability, cache policy, or claim-to-cell mapping.
  - Required result: when companion paper-artifact tracking lands, update
    ROADMAP, README, papers index, and code/paper TODO entries together so
    roadmap wording distinguishes PDF manifest validation, external
    AlphaEvolve companion-source verification, and generated LibreEvolve
    result-export artifacts.

- [ ] Keep companion-notebook roadmap wording scoped until selection-scope
      metadata exists.
  - Spec evidence: the `google-deepmind/alphaevolve_results` README says the
    `mathematical_results.ipynb` notebook includes only instances where
    AlphaEvolve outperformed SOTA, excludes matched-but-not-outperformed
    constructions, and does not contain the code to run AlphaEvolve.
  - Current evidence: roadmap/README/paper-index wording can cite companion
    Colab source tracking and future local Colab-equivalent exports. It does
    not require a source-selection policy or per-claim absence reason that
    distinguishes paper-reported matched results from intentionally omitted
    companion-notebook cells.
  - Required result: when companion-notebook selection metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap language
    separates paper result coverage, official improved-result notebook
    coverage, matched-result omissions, verifier-code availability, and
    non-availability of AlphaEvolve runtime code in the companion repository.

- [ ] Keep companion-source rights roadmap wording scoped until repository
      license and disclaimer metadata exists.
  - Spec evidence: the `google-deepmind/alphaevolve_results` README declares
    Google LLC copyright, Apache 2.0 licensing for software, CC-BY 4.0
    licensing for other materials, an as-is disclaimer, and a statement that
    the repository is not an official Google product.
  - Current evidence: roadmap/README/paper-index wording can cite LibreEvolve's
    MIT license, source-PDF rights gaps, and companion Colab source tracking.
    It does not require the companion repository's dual license, artifact-type
    license mapping, disclaimer, or non-official-product boundary.
  - Required result: when companion-repository rights metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap language
    separates source-PDF rights, companion software/materials licensing,
    generated LibreEvolve artifacts, and local ownership or endorsement
    boundaries.

- [ ] Keep paper-source roadmap wording scoped until AlphaEvolve PDF version
      provenance is pinned.
  - Spec evidence: page 1 of the local AlphaEvolve PDF identifies the source as
    `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`.
  - Current evidence: roadmap/README wording can cite local PDF byte/hash
    validation and Appendix B result-version TODOs, while the committed
    manifests still use the floating `https://arxiv.org/pdf/2506.13131.pdf`
    source URL and do not store source arXiv version, category, posted date,
    expected header text, or URL-kind metadata. This leaves roadmap-level
    source-parity claims vulnerable to a future arXiv PDF refresh changing the
    audited source without a visible claim-ledger boundary.
  - Required result: once paper manifests record versioned source identity and
    validators check the expected header/page/hash, update ROADMAP, README,
    papers index, and TODO cross-links so AlphaEvolve audit claims identify
    whether they are based on the v1 PDF, a later arXiv revision, or another
    pinned source artifact.

- [ ] Keep paper-source roadmap wording scoped until source-PDF rights
      provenance is tracked.
  - Spec evidence: page 1 of the local AlphaEvolve PDF states
    `© 2025 Google DeepMind. All rights reserved`.
  - Current evidence: roadmap and README wording can describe LibreEvolve's own
    license, non-affiliation, local PDF hash validation, source-version TODOs,
    and companion-artifact gaps. They do not require roadmap-level evidence for
    cached paper-source rights: copyright holder/year, rights statement,
    arXiv/license terms, or the policy boundary for quoting, table extraction,
    figure reproduction, and paper-derived artifacts.
  - Required result: once paper manifests and validators record source-rights
    metadata, update ROADMAP, README, papers index, and TODO cross-links so
    paper-cache integrity, paper-derived exhibit generation, and publication
    readiness all distinguish third-party paper-source rights from the
    repository's own license.

- [ ] Keep bibliography roadmap wording scoped until AlphaEvolve References
      metadata is tracked.
  - Spec evidence: the AlphaEvolve PDF includes a numbered References section
    after Author information, with entries through `[120]`.
  - Current evidence: roadmap and README wording can cite the local paper cache,
    selected related-work rows, Appendix A/B citation gaps, source-PDF
    versioning, and source-rights TODOs. They do not require a complete
    AlphaEvolve bibliography map, local-cache linkage for cited works, or docs
    checks that distinguish authoritative reference metadata from manifest
    display slugs and narrower claim-level citation provenance.
  - Required result: once paper-source metadata records the full References
    section, update ROADMAP, README, papers index, and TODO cross-links with
    reference id, authors/title/venue/year, DOI/URL/arXiv fields, source
    page/span, citation-use categories, local-cache or absent-cache status, and
    validation that roadmap claims about cited papers are traceable to the
    source bibliography rather than inferred from local filenames.

- [ ] Keep roadmap wording scoped until the follow-on AlphaEvolve math paper
      and repository are tracked.
  - Spec evidence: AlphaEvolve Section 3.2 says an upcoming paper would provide
    more examples and details on the constructive-math problems and methods.
    Current primary-source evidence identifies that follow-on as arXiv
    `2511.02864`, `Mathematical exploration and discovery at scale`, and the
    `google-deepmind/alphaevolve_repository_of_problems` repository, which
    lists 67 mathematical problems and Colab notebooks for many problems with
    prompts, verification code, initial programs, final evolved programs, and
    visualization/analysis code.
  - Current evidence: roadmap/README/paper-index wording can cite the original
    AlphaEvolve paper, the original companion-Colab gap, and Appendix B
    family/status coverage. It does not require tracking the later paper's PDF
    version, repository ref/commit, problem inventory, notebook artifacts, or
    source mappings from original Section 3.2/Appendix B claims to the expanded
    math-discovery evidence.
  - Required result: when follow-on source tracking lands, update ROADMAP,
    README, papers index, and code/paper TODOs so roadmap claims distinguish
    original AlphaEvolve specification parity from later 67-problem
    mathematical-discovery source coverage.

- [ ] Scope roadmap follow-on problem-repository coverage to a pinned snapshot.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README describes a live repository that will expand and improve over time.
    It says there are problem pages for all 67 mathematical problems and Colab
    notebooks for many, but not all, problems, with prompts, verification code,
    initial programs, final evolved programs, and visualization/analysis code
    where appropriate. It also references status and area overview assets such
    as `assets/status_grid.png` and `assets/table_by_areas.png`.
  - Current evidence: roadmap TODOs require tracking the later paper,
    repository ref, problem inventory, and notebook artifacts, but they do not
    force roadmap language to separate complete problem-page coverage from
    partial notebook/artifact coverage or to describe live-repository evidence
    as a pinned snapshot with overview-image provenance.
  - Required result: once the coverage manifest is implemented, update ROADMAP
    milestones and evidence gates so follow-on AlphaEvolve math coverage names
    the repository snapshot, records page/notebook/artifact availability by
    problem, includes overview-image hashes when cited, and avoids treating a
    live partial-notebook repository as fully static or notebook-complete.

- [ ] Keep theoretical-CS roadmap wording scoped until AlphaEvolve
      proof-element source tracking exists.
  - Spec evidence: Google Research's September 30, 2025 AlphaEvolve
    theoretical-CS article and arXiv `2509.18057` use AlphaEvolve to discover
    finite combinatorial structures that serve as proof elements in complexity
    theory, including MAX-k-CUT gadget reductions and Ramanujan graph
    constructions. The sources describe lifting finite structures into
    universal statements, computer-verified proof elements, AlphaEvolve
    acceleration of expensive verifier code, and final brute-force
    verification of discovered gadgets.
  - Current evidence: roadmap/README/paper-index wording can cite the original
    AlphaEvolve paper, Appendix A/B coverage, the original companion-Colab
    gap, and the later 67-problem constructive-math source gap. It does not
    require tracking the separate theoretical-CS source article/paper,
    graph/gadget artifacts, lifting-framework boundary, verifier-speedup
    evidence, or independent final-verification policy.
  - Required result: when theoretical-CS proof-element source tracking lands,
    update ROADMAP, README, papers index, and code/paper TODOs so roadmap
    claims distinguish original AlphaEvolve specification parity, expanded
    constructive-math source coverage, and later proof-element/lifting
    applications rather than treating all mathematical-source evidence as one
    Appendix B or 67-problem bucket.

- [ ] Keep DeepMind-blog roadmap wording scoped until official announcement
      source provenance exists.
  - Spec evidence: the May 14, 2025 Google DeepMind blog announcement is an
    official AlphaEvolve source that describes the Gemini/evaluator/evolution
    loop, whole-codebase evolution, systems and math impacts, white-paper and
    Colab links, Early Access/user-interface plans, and blog-specific values
    or wording such as `up to a 32.5%` FlashAttention speedup and reducing
    kernel-optimization effort from `weeks` to days.
  - Current evidence: ROADMAP and README can cite the AlphaEvolve paper,
    systems metric gaps, source-PDF/Colab/follow-on source gaps, and broad
    public DeepMind description. They do not require source metadata for the
    blog itself, claim-to-paper mappings, blog-only availability claims,
    acknowledgement/illustration role records, or reconciliation where blog
    and white-paper values differ.
  - Required result: when official blog-source provenance lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap language
    distinguishes announcement evidence from white-paper specification,
    reproduced benchmark evidence, source availability claims, and
    blog-versus-paper metric/value variants.

- [ ] Keep paper-artifact roadmap wording scoped until creator/assembler role
      provenance exists.
  - Spec evidence: AlphaEvolve's Contributions section identifies the figure
    creators and the people who assembled the accompanying Google Colab.
  - Current evidence: roadmap/README/paper-index status can point to PDF
    manifest validation, planned companion Colab source tracking, and
    figure/exhibit artifact TODOs. They do not require artifact-role metadata
    for figure creation, table/figure assembly, notebook assembly, responsible
    initials/names, source section/page, or linkage from those roles to
    artifact ids and hashes.
  - Required result: when paper-artifact role provenance lands, update ROADMAP,
    README, papers index, and code/paper TODO entries together so roadmap
    wording distinguishes artifact presence/hash verification from
    paper-attributed creator or assembler provenance.

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

- [ ] Keep Appendix A matrix-baseline roadmap wording scoped until
      best-known-rank citation provenance exists.
  - Spec evidence: AlphaEvolve Table 2 includes a `best known [reference]`
    baseline-rank column for matrix targets, and Appendix A Table 3 extends
    best-known-rank comparisons across the reported matrix target suite.
  - Current evidence: roadmap/README/paper-index status points to the checked
    Appendix A registry and matrix report validation. That registry stores
    best-known rank values, AlphaEvolve ranks, outcomes, and exact-algorithm
    flags, but not per-target cited prior-work sources, bibliography reference
    ids, source page/table locations, finite-field or characteristic caveats,
    source digests, or report-visible baseline-source metadata.
  - Required result: when best-known-rank citation provenance lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap text
    distinguishes rank-value registry coverage from traceable prior-baseline
    evidence.

- [ ] Keep matrix per-seed roadmap wording scoped until cascade-run provenance
      exists.
  - Spec evidence: AlphaEvolve Section 3.1 says matrix experiments are run
    over multiple random seeds using the evaluation cascade, with performance
    reported as the best rank and the fraction of seeds that achieved it.
  - Current evidence: roadmap/README/paper-index status can point to generic
    evaluator cascades and declared matrix result reports with per-seed rank
    rows and hit-fraction checks. It does not yet require matrix-specific
    execution traces showing the cascade configuration, stage thresholds,
    per-stage rank/exactness diagnostics, pruning or early-stop reasons,
    target/seed lineage, and aggregation from executed traces into best-rank
    hit fractions.
  - Required result: when matrix cascade-run provenance lands, update ROADMAP,
    README, papers index, and code/paper TODOs together so roadmap text
    distinguishes declared per-seed report validation from executed
    AlphaEvolve-style matrix cascade evidence.

- [ ] Keep Table 2/Table 3 matrix-rank table roadmap wording scoped until
      table exhibit provenance exists.
  - Spec evidence: AlphaEvolve Table 2 presents selected matrix tensor-rank
    comparisons, and Appendix A Table 3 expands this to the full 54-target
    table with caption aggregate counts, outcome coloring, complex-valued row
    caveats, companion Colab decomposition links, and the concurrent-work note
    for `<4, 5, 6>`.
  - Current evidence: roadmap/README/paper-index status can point to the
    Appendix A registry, matrix report validation, baseline-citation TODOs,
    row-note TODOs, target-suite curation TODOs, Figure 4 exhibit TODOs,
    scalar-field evidence gaps, and tensor-rank caveats. It does not require
    Table 2/Table 3 exhibit ids, selected-row versus full-table membership,
    row ordering, caption aggregate validation, color/outcome encoding,
    source/caption locations, rendered table artifacts/hashes, or links from
    table rows to registry, report, certificate, and companion Colab evidence.
  - Required result: when Table 2/Table 3 matrix-rank table exhibit provenance
    lands, update ROADMAP, README, papers index, and code/paper TODOs together
    so roadmap wording distinguishes reproduced paper-table exhibits from
    general Appendix A registry and matrix result-report coverage.

- [ ] Keep matrix outcome roadmap wording scoped until target-subset evidence
      exists.
  - Spec evidence: AlphaEvolve Table 2 scopes its all-matched-or-surpassed
    statement to parameters `m, n, p <= 5`, while Appendix A Table 3 is a
    broader 54-target matrix table.
  - Current evidence: roadmap/README/paper-index status can cite the Appendix
    A registry and aggregate outcome counts, but that full registry includes
    larger-target `fell_behind` rows (`mm_4x4x9` and `mm_6x6x6`). There is no
    roadmap-facing evidence surface that ties prose claims to named target
    subsets and prevents mixing the `m,n,p <= 5` main-text subset with the
    full Appendix A table.
  - Required result: when matrix subset-scope metadata lands, update ROADMAP,
    README, papers index, and code/paper TODOs with named target subsets,
    inclusion predicates, row counts, outcome counts, out-of-scope row ids,
    source-caption/table linkage, and validation that keeps scoped Table 2
    outcome wording separate from full Appendix A aggregate outcomes.

- [ ] Keep matrix headline roadmap wording scoped until 4x4 rank-48
      historicity provenance exists.
  - Spec evidence: AlphaEvolve's abstract and Section 3.1 say AlphaEvolve
    found a procedure for multiplying two 4x4 complex-valued matrices using
    48 scalar multiplications. Section 3.1 calls it the first rank-below-49
    characteristic-zero result after 56 years, while separately describing
    recursive Strassen rank 49 over any field and Fawzi et al. rank 47 over
    the field with two elements.
  - Current evidence: roadmap/README/paper-index status can point to Appendix
    A registry rows, matrix report validation, best-known-rank citation gaps,
    scalar-field gaps, Table 2/Table 3 exhibit gaps, Figure 4/Figure 9
    provenance, and companion Colab gaps. Those do not create a
    roadmap-facing evidence surface for the stronger historicity claim, its
    prior-algorithm comparisons, or its field/characteristic caveats.
  - Required result: when matrix-headline provenance lands, update ROADMAP,
    README, papers index, and code/paper TODOs with target id, dimensions,
    scalar field/characteristic, reported rank, Strassen/Fawzi comparison
    scope, bibliography references, source page/span locations, certificate
    and companion Colab links, and validation that roadmap text distinguishes
    rank-row support from the "first improvement after 56 years" claim.

- [ ] Keep Figure 4 matrix-exhibit roadmap wording scoped until exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 4 presents the main-text matrix
    multiplication discovery exhibit, showing an evolved 4x4
    tensor-decomposition search-program diff and tying the displayed example
    to Section 3.1/Table 2 matrix rank-improvement evidence. The caption also
    states that the discovery required 15 mutations and included non-trivial
    changes to optimizer, weight initialization, loss function, and
    hyperparameter sweep code.
  - Current evidence: roadmap/README/paper-index status can point to Appendix A
    target identities, matrix result-report validation, checked Strassen
    bundle evidence, and separate TODOs for near-integrality, scalar-field,
    baseline, companion Colab, and Figure 9 sweep-space provenance. They do not
    require Figure 4 exhibit ids, exact source diff excerpt artifacts/hashes,
    selected target/result-row mappings, caption values, visual/text artifact
    paths/hashes, rendering/source parameters, the accepted 15-mutation
    lineage, component-change labels, or links from the displayed figure to
    decomposition reports, exactness certificates, notebooks, and paper-source
    evidence.
  - Required result: when Figure 4 matrix exhibit provenance lands, update
    ROADMAP, README, papers index, and code/paper TODOs with exhibit-level
    metadata and validators so roadmap wording distinguishes reproduced
    main-text matrix figure evidence, mutation-sequence evidence, general
    matrix benchmark coverage, and Appendix A Figure 9 sweep evidence.

- [ ] Keep Appendix A row-note roadmap wording scoped until concurrent-work
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix A Table 3 includes row-level notes,
    including the note that concurrent work [49] also found a rank-90 algorithm
    for the `<4, 5, 6>` matrix target.
  - Current evidence: roadmap/README/paper-index status points to the checked
    Appendix A registry and matrix report validation. That registry stores
    target ids, dimensions, best-known rank values, AlphaEvolve ranks,
    outcomes, and exact-algorithm flags, but not per-target result notes,
    concurrent-work attributions, independently matched result flags, note
    source locations, or report-visible caveats for rows such as `mm_4x5x6`.
  - Required result: when Appendix A row-note provenance lands, update ROADMAP,
    README, papers index, and code/paper TODOs together so roadmap text
    distinguishes rank/outcome registry coverage from paper-faithful
    row-note/concurrent-work evidence and avoids overclaiming exclusive SOTA
    priority.

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

- [ ] Keep Appendix A Figure 9 roadmap wording scoped until magnified-diff
      exhibit provenance exists.
  - Spec evidence: AlphaEvolve Appendix A Figures 9a-9c are a three-part
    magnified source/diff exhibit for the 4x4 matrix program from Figure 4,
    showing the ordered code changes that discover the rank-48 decomposition,
    including optimizer, initialization, noise, clipping,
    hallucination/discretization/loss-penalty, and named sweep-field
    components.
  - Current evidence: roadmap status can point to matrix result contracts,
    Appendix A registry coverage, Figure 4 exhibit gaps, and sweep-space
    provenance gaps. It does not require Figure 9a/9b/9c panel metadata,
    page/caption locations, exact line-span artifacts, source/diff hashes,
    rendered/OCR text validation, continuation ordering, semantic component
    labels for the displayed source changes, or links from each panel to matrix
    rows, sweep metadata, exactness certificates, and companion paper/source
    evidence.
  - Required result: when Appendix A Figure 9 exhibit provenance lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap wording
    distinguishes reproduced appendix magnified-diff panels from Figure 4
    main-text exhibit evidence, semantic change-component evidence, and generic
    sweep-space provenance.

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

- [ ] Keep matrix roadmap wording scoped until tensor-rank and recursive-use
      caveats exist.
  - Spec evidence: AlphaEvolve Section 3.1 reports matrix multiplication
    improvements as low-rank tensor decompositions, and footnote 3 says some
    fewer-than-49 multiplication algorithms do not correspond to decompositions
    of the matrix multiplication tensor and cannot be applied recursively to
    larger matrix multiplication.
  - Current evidence: roadmap/README/paper-index status points to the Appendix
    A target registry, matrix result reports, coefficient-domain/exactness
    fields, scalar-field follow-ups, and checked Strassen artifacts. It does
    not require algorithm-kind metadata, tensor-decomposition certificate
    scope, recursive applicability, or footnote/source-note provenance for
    rank comparisons against non-tensor or non-recursive algorithms.
  - Required result: when matrix reports or companion metadata capture
    tensor-rank applicability and recursive-use caveats, update ROADMAP,
    README, papers index, and code/paper TODO entries together so roadmap text
    distinguishes tensor-decomposition rank evidence from broader
    multiplication-count claims that are not AlphaEvolve-comparable baselines.

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

- [ ] Keep constructive-math roadmap wording scoped until heuristic-stage
      sequence provenance exists.
  - Spec evidence: AlphaEvolve Section 3.2 says constructive-math heuristics
    used fixed time budgets, for example `1000 seconds`, and final
    constructions often came from a sequence of specialized heuristics: early
    broad-gain heuristics from random/simple states and later fine-tuning
    heuristics near optimal configurations.
  - Current evidence: roadmap/README/paper-index wording can cite runtime
    budgets, simple/random starting-construction gaps, aggregate outcome gaps,
    and single-step incumbent handoff gaps. It does not require per-stage
    budget seconds, incumbent lineage, heuristic artifact identity, output
    construction, improvement delta, or stage-role classification.
  - Required result: when heuristic-stage sequence reports land, update
    ROADMAP, README, papers index, and code/paper TODOs together so roadmap
    wording distinguishes one-step incumbent handoff support from
    AlphaEvolve-style multi-stage adaptive constructive-math search.

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

- [ ] Keep constructive-math roadmap wording scoped until simple/random
      starting-construction provenance exists.
  - Spec evidence: AlphaEvolve Section 3.2 says the initial starting point in
    the constructive-math cases was a simple or random construction.
  - Current evidence: roadmap/README/paper-index wording covers seed
    provenance, strict seed-validity gaps, human-seeded matrix caveats,
    Appendix B family/status coverage, and aggregate constructive-math outcome
    gaps. It does not require constructive-math report metadata for starting
    construction class, random generator and seed, construction artifact/hash,
    baseline metric value, or prior-best visibility/seeding policy.
  - Required result: when constructive-math reports validate simple/random
    starting-construction provenance, update ROADMAP, README, papers index, and
    code/paper TODOs so roadmap wording distinguishes aggregate Appendix B
    outcome coverage from AlphaEvolve's claim that those runs began from
    simple or random constructions.

- [ ] Keep Figure 5 roadmap wording scoped until construction-exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 5 shows selected SOTA-breaking
    mathematical construction examples with branch labels, problem labels,
    before/after metric values, and rendered construction visuals.
  - Current evidence: `ROADMAP.md`, README, papers index, and code evidence
    describe Appendix B family/status coverage, smoke fixture boundaries,
    expected construction/certificate artifacts, aggregate outcome gaps, and
    result-version provenance gaps. They do not require Figure 5 exhibit IDs,
    selected result-row links, visual artifact paths/hashes, rendering
    parameters, previous-best sources, source Colab cells/artifacts, or verifier
    linkage for the paper's displayed examples.
  - Required result: when construction-exhibit provenance lands, update
    roadmap, README, papers index, and code/paper TODO entries together with
    exhibit-level metadata and validators so roadmap wording distinguishes
    Appendix B family coverage, aggregate constructive-math outcomes, and
    reproduced Figure 5 visual/result exhibits.

- [ ] Keep Figure 5 sum-of-radii roadmap wording scoped until source-specific
      precision provenance exists.
  - Spec evidence: AlphaEvolve Figure 5 displays the selected sum-of-radii
    improvement as `2.6340 -> 2.6358`, while Appendix B.12 and Figure 14 state
    the `n = 26` unit-square circle-packing improvement as `2.634` to `2.635`.
  - Current evidence: roadmap/README/paper-index wording can cite Figure 5
    exhibit gaps and B.12-B.13 packing gaps, but it does not require
    source-specific numeric strings, rounding policy, or a canonicalization
    decision for the Figure 5 versus appendix precision difference. Current
    wording can quote `2.635` without preserving the main-text Figure 5
    `2.6358` display.
  - Required result: when precision provenance lands, update ROADMAP, README,
    papers index, and code/paper TODOs with per-source value records for
    Figure 5, Appendix B.12, and Figure 14, including displayed strings,
    normalized values, rounding/canonicalization policy, and safeguards against
    conflating figure-display precision with appendix text precision.

- [ ] Keep Appendix B figure roadmap wording scoped until Figures 10-14
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B displays construction figures beyond
    the main-text Figure 5 summary: Figure 10 for Erdos minimum overlap,
    Figure 11 for regular-hexagon packings, Figure 12 for maximum/minimum
    distance point sets, Figure 13 for Heilbronn variants, and Figure 14 for
    circle/rectangle packing sum-of-radii improvements.
  - Current evidence: `ROADMAP.md`, README, papers index, and code evidence
    describe Appendix B family/status coverage, expected construction/
    certificate artifacts, aggregate outcome gaps, result-version gaps, and
    Figure 5 exhibit gaps. They do not require Appendix B figure/subfigure IDs,
    family/parameter links, figure-caption values, visual artifact paths/
    hashes, rendering parameters, construction payloads, previous-best
    sources, source Colab cells/artifacts, or verifier linkage for
    Figures 10-14.
  - Required result: when Appendix B figure-level provenance lands, update
    ROADMAP, README, papers index, and code/paper TODO entries together with
    exhibit-level metadata and validators so roadmap text distinguishes broad
    Appendix B family coverage, main-text Figure 5 exhibits, and reproduced
    Appendix B construction figures.

- [ ] Keep Appendix B roadmap wording scoped until per-result metric/value
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.13 reports individual
    mathematical values across different constants, geometric objectives,
    finite-set ratios, lower/upper bounds, prior references, parameter tuples,
    and section/figure/caption locations.
  - Current evidence: `ROADMAP.md`, README, papers index, and code evidence
    describe Appendix B family/status coverage, construction/verifier export
    gaps, aggregate constructive-math outcomes, result-version gaps, Figure 5
    exhibit gaps, Figures 10-14 visual provenance, and the kissing-number
    certificate gap. They do not require a normalized result-row layer that
    maps every Appendix B text-level numeric claim to an exact metric
    definition, parameter tuple, bound direction or optimization direction,
    previous-best value and source, AlphaEvolve reported value, source
    location, construction-representation schema, and construction/verifier
    artifact hash.
  - Required result: when Appendix B per-result metric/value provenance lands,
    update ROADMAP, README, papers index, and code/paper TODO entries together
    with result-row metadata and validators so roadmap text distinguishes
    family coverage, aggregate outcome claims, figure reproduction,
    revised-result history, construction-payload evidence, and text-level
    numeric claim evidence.

- [ ] Keep Appendix B.1-B.3 roadmap wording scoped until autocorrelation
      step-function provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.3 reports three distinct
    autocorrelation/autoconvolution step-function witnesses: `600`
    equally-spaced intervals on `[-1/4, 1/4]` for `C1 <= 1.5053`, `50`
    intervals on the same domain for `0.8962 <= C2`, and `400` intervals on
    the same domain for `C3 <= 1.4557`.
  - Current evidence: roadmap/README/paper-index wording can cite the broad
    Appendix B per-result metric/value gap, but it does not require B.1-B.3-
    specific interval counts, function sign policies, step-function payload
    hashes, prior bounds, bound directions, or recomputation evidence.
  - Required result: when Appendix B.1-B.3 autocorrelation metadata and
    validators land, update ROADMAP, README, papers index, and code/paper
    TODOs so roadmap claims distinguish the three constants, interval counts,
    domain, prior/current values, proof direction, payload hashes, and source
    links from aggregate Appendix B coverage.

- [ ] Keep Appendix B.1-B.3 roadmap wording scoped until paper-heading label
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.3 headings are `First
    autocorrelation inequality`, `Second autocorrelation inequality`, and
    `Third autocorrelation inequality`; the constants are `C1`, `C2`, and
    `C3`. The paper does not describe them with `k=3`, `k=4`, or `k=5`
    labels.
  - Current evidence: roadmap/README/paper-index wording can cite broad
    Appendix B family/status and step-function gaps, but the checked
    `alphaevolve_appendix_b.json` registry and `appendix_b_registry.py` still
    use internal `autocorrelation_bounds_k3/k4/k5` ids and `k=3/k=4/k=5`
    display names without paper-facing label provenance.
  - Required result: when Appendix B.1-B.3 paper-label metadata lands, update
    ROADMAP, README, papers index, registry validation, and tests so roadmap
    claims use B.1-B.3 headings and C1-C3 constants, and any internal ids are
    not presented as AlphaEvolve paper labels.

- [ ] Keep Appendix B.8 roadmap wording scoped until squared-ratio convention
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.8 reports min max/min-distance
    point-set results for 16 points in two dimensions and 14 points in three
    dimensions. The published values `12.889266112` and `4.165849767` are
    squared-ratio values, not direct max/min distance ratios.
  - Current evidence: roadmap/README/paper-index wording can cite the broad
    Appendix B per-result metric/value gap, but it does not require B.8-specific
    convention labels that keep raw squared values, square-root-derived ratios,
    dimensions, point counts, coordinate artifacts, and comparison units
    separate.
  - Required result: when Appendix B.8 metric-convention metadata and
    validators land, update ROADMAP, README, papers index, and code/paper TODOs
    so roadmap claims cannot compare or quote B.8 values in the wrong unit.

- [ ] Keep Appendix B.8 roadmap wording scoped until point-set distance
      certificates exist.
  - Spec evidence: AlphaEvolve Appendix B.8 and Figure 12 report two concrete
    max/min-distance point-set witnesses: 16 points in 2D with squared ratio
    `12.889266112` improving prior `12.890`, and 14 points in 3D with squared
    ratio `4.165849767` improving prior `4.168`.
  - Current evidence: roadmap/README/paper-index wording can cite broad
    Appendix B per-result gaps and the B.8 squared-ratio convention gap, but
    it does not require B.8-specific coordinate payloads, exact point-count and
    dimension validation, all-pairs min/max distance certificates, recomputed
    squared ratios, prior-best comparisons, or Figure 12 panel linkage.
  - Required result: when Appendix B.8 witness validators land, update ROADMAP,
    README, papers index, and code/paper TODOs together so roadmap claims
    separate convention-safe quoting from actual reproduced point-set
    certificates for the 2D and 3D Figure 12 constructions.

- [ ] Keep Appendix B.5 roadmap wording scoped until minimum-overlap
      step-function provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.5 improves the Erdos
    minimum-overlap upper bound from `C5 <= 0.380927` to `C5 <= 0.380924`.
    The Figure 10 construction is a step function on `[0, 2]` with values in
    `[0, 1]`, integral normalization `integral_0^2 h(x) dx = 1`, and an
    objective that minimizes the maximum shifted overlap integral.
  - Current evidence: roadmap/README/paper-index wording can cite the broad
    Appendix B per-result and Figure 10 visual gaps, but it does not require
    B.5-specific function-domain metadata, value-range and normalization
    certificates, shift-objective recomputation, prior lower/upper bounds,
    reported upper bound, or construction payload hash.
  - Required result: when Appendix B.5 minimum-overlap metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODOs so roadmap
    claims distinguish B.5's step-function domain, normalization, objective,
    prior/current bounds, Figure 10 link, payload hash, and source location
    from aggregate Appendix B coverage.

- [ ] Keep Appendix B.5 roadmap wording scoped until source-formulation
      equivalence exists.
  - Spec evidence: AlphaEvolve Appendix B.5 first defines `C5` through
    non-negative `f,g: [-1,1] -> [0,1]` with `f + g = 1`,
    `integral f = 1`, zero extension outside `[-1,1]`, and
    `sup_{x in [-2,2]} integral_{-1}^1 f(t) g(x+t) dt`. It then cites `[40]`
    for equality with the normalized step-function infimum on `[0,2]`.
  - Current evidence: roadmap/README/paper-index wording can cite the B.5
    step-function construction gap, but it does not separately require the
    source Erdos formulation, zero-extension convention, complement and
    normalization constraints, supremum domain, or `[40]` equivalence evidence.
  - Required result: when B.5 formulation/equivalence metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs so roadmap claims
    distinguish source-problem scope and reduction evidence from Figure 10
    construction-payload validation.

- [ ] Keep Appendix B.6 roadmap wording scoped until finite-set witness
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.6 improves the
    sums-and-differences lower bound using two finite sets: `U1` has size
    `2003` and yields `1.1479 <= C6`, while `U2` has size `54265` and yields
    `1.1584 <= C6`. The claim is tied to the Gyarmati et al. inequality and
    requires set-level checks for zero membership, `|U - U| <= 2 max(U) + 1`,
    `|U-U|`, `|U+U|`, and the denominator `2 max(U) + 1`.
  - Current evidence: roadmap/README/paper-index wording can cite the broad
    Appendix B per-result metric/value gap, but it does not require B.6-
    specific witness ids, cardinalities, integer-set payload hashes, condition
    checks, or separate lower-bound values for the two found sets.
  - Required result: when Appendix B.6 witness metadata and validators land,
    update ROADMAP, README, papers index, and code/paper TODOs so roadmap
    claims distinguish `U1` and `U2`, their sizes, feasibility evidence,
    derived lower-bound values, payload hashes, and source links from aggregate
    Appendix B coverage.

- [ ] Keep Appendix B.6 roadmap wording scoped until theorem-condition
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.6 defines the `C6` problem through
    arbitrarily large finite integer sets `A` and `B`, explicit
    sumset/difference-set definitions, asymptotic `<<`/`>>` notation whose
    constants are independent of sufficiently large sets, and source anchors
    `[39, Corollary 3]` for `C6 <= 4/3` and `[39, Theorem 1]` for the
    Gyarmati lower-bound theorem. The finite-set theorem applies only to
    non-negative integer `U` containing zero and satisfying
    `|U - U| <= 2 max(U) + 1`.
  - Current evidence: roadmap/README/paper-index wording can cite B.6 witness
    provenance, but it does not separately require the theorem definitions,
    asymptotic-notation scope, cited source theorem/corollary ids, or
    admissible-`U` preconditions that make finite-set witnesses meaningful.
  - Required result: when B.6 theorem-condition metadata lands, update ROADMAP,
    README, papers index, and code/paper TODOs so roadmap claims distinguish
    theorem scope and admissibility evidence from `U1`/`U2` witness payloads,
    arithmetic counts, and derived lower-bound values.

- [ ] Keep Appendix B.7 roadmap wording scoped until regular-hexagon packing
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.7 reports two regular-hexagon
    packing improvements: for `n = 11`, the outer side length improves from
    `3.943` to `3.931`, and for `n = 12`, it improves from `4.0` to `3.942`.
    Figure 11 shows the two constructions as left/right panels.
  - Current evidence: roadmap/README/paper-index wording can cite the broad
    Appendix B per-result and Figure 11 visual gaps, but it does not require
    B.7-specific parameter rows, unit-hexagon convention, outer side-length
    convention, placement artifact hashes, containment/non-overlap
    certificates, prior/current values, or Figure 11 panel linkage.
  - Required result: when Appendix B.7 regular-hexagon metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODOs so roadmap
    claims distinguish both `n` values, geometry conventions, side-length
    improvements, certificate evidence, Figure 11 links, payload hashes, and
    source locations from aggregate Appendix B coverage.

- [ ] Keep Appendix B.9-B.10 roadmap wording scoped until Heilbronn
      minimum-area provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.9-B.10 reports three Heilbronn
    minimum-area improvements: `n = 11` points in a unit-area triangle improve
    the prior `0.036` bound to greater than `0.0365`; `n = 13` points in a
    unit-area convex region improve `0.0306` to `0.0309`; and `n = 14` points
    in a unit-area convex region improve `0.0277` to `0.0278`.
  - Current evidence: roadmap/README/paper-index wording can cite the broad
    Appendix B per-result and Figure 13 visual gaps, but it does not require
    B.9-B.10-specific parameter rows, domain type, unit-area normalization,
    point/region artifact hashes, all-triples minimum-area certificates,
    prior/current values, or strict inequality/rounding policy.
  - Required result: when Appendix B.9-B.10 Heilbronn metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODOs so roadmap
    claims distinguish the three `n` values, domains, certificate evidence,
    prior/current values, Figure 13 panel links, payload hashes, and source
    locations from aggregate Appendix B coverage.

- [ ] Keep kissing-number roadmap wording scoped until Lemma 1 certificate
      evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.11 proves the dimension-11 kissing
    lower bound by checking 593 nonzero integral-coordinate points with a
    maximum-norm versus minimum-pairwise-distance condition, then applying
    Lemma 1 to obtain a valid kissing configuration.
  - Current evidence: roadmap/README/paper-index wording can cite Appendix B
    family/status coverage, construction/verifier export gaps, aggregate
    outcome gaps, and Figure 10-14 visual exhibit gaps. It does not require a
    kissing-specific proof certificate for cardinality, dimension, coordinate
    domain, exact norm/distance inequalities, Lemma 1 applicability, transformed
    sphere centers, tangency/non-overlap checks, or lower-bound claim linkage.
  - Required result: when Appendix B.11 proof-certificate records and
    validators land, update ROADMAP, README, papers index, and code/paper TODOs
    so roadmap wording distinguishes rendered construction/figure evidence
    from proof-grade kissing-number lower-bound verification.

- [ ] Keep Appendix B.12-B.13 roadmap wording scoped until circle/rectangle
      sum-of-radii provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.12-B.13 reports three packing
    improvements: `n = 26` circles in a unit square improve the prior `2.634`
    sum of radii to `2.635`; `n = 32` circles in a unit square improve
    `2.936` to `2.937`; and `n = 21` circles in a perimeter-4 rectangle
    improve `2.364` to `2.3658`.
  - Current evidence: roadmap/README/paper-index wording can cite the checked-in
    fixed-26 smoke fixture, the broad Appendix B per-result gap, and Figure 14
    visual gap, but it does not require B.12-B.13-specific parameter rows,
    container geometry/perimeter metadata, exact count, placement payload
    hashes, containment/non-overlap certificates, prior/current values, or
    Figure 14 panel linkage.
  - Required result: when Appendix B.12-B.13 packing metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODOs so roadmap
    claims distinguish all three `n`/container rows, certificates,
    sum-of-radii values, Figure 14 links, payload hashes, and source locations
    from the existing 26-circle smoke fixture.

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

- [ ] Keep Appendix B.4 roadmap wording scoped until prior-bound rounding
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.4 reports the known uncertainty
    inequality range as `0.2025 <= C4 <= 0.3523`, with a parenthetical note
    that reference `[33]` states the upper bound as `0.353` but rounding that
    solution to the fourth digit gives `0.3523`. The first-version
    AlphaEvolve value `C4 <= 0.3521` is positioned as an improvement over that
    rounded prior bound.
  - Current evidence: `ROADMAP.md`, README, papers index, and Appendix B TODOs
    can cite broad Appendix B numeric-result rows, revised-result provenance,
    Hermite certificate gaps, and construction/verifier gaps. They do not
    require source-linked evidence for the prior paper's stated value versus
    rounded comparison value, lower-bound context, rounding policy, or the
    precise baseline used for the `0.3521` improvement claim.
  - Required result: when Appendix B.4 prior-bound rounding evidence lands,
    update ROADMAP, README, papers index, and code/paper TODOs so roadmap
    claims distinguish the `[33]` stated `0.353` value, the rounded `0.3523`
    baseline, AlphaEvolve's `0.3521` first-version result, the later `0.3216`
    revision, and the separate Hermite-polynomial certificate.

- [ ] Keep Appendix B.4 roadmap wording scoped until Hermite-polynomial
      certificate evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.4 derives the `C4 <= 0.3521`
    uncertainty-inequality bound from a Hermite-polynomial test function
    `f(x) = P(x) exp(-pi x^2)`, approximate coefficients
    `[0.32925, -0.01159, -8.9216e-5]`, the largest positive root of
    `P(x)/x^2`, and the formula `r_max^2 / (2*pi)`.
  - Current evidence: roadmap/README/paper-index wording can cite broad
    Appendix B numeric-result rows, construction/verifier gaps, revised-result
    provenance, and B.4 prior-construction similarity gaps. It does not require
    B.4-specific Hermite basis terms, coefficient precision, sign/condition
    checks, root-calculation artifacts, bound recomputation, or certificate
    payload hashes.
  - Required result: when B.4 Hermite-polynomial certificate metadata and
    validators land, update ROADMAP, README, papers index, and code/paper TODOs
    so roadmap claims separate the quoted `C4` value, the polynomial/root
    certificate, revised-result history, and qualitative near-optimality
    interpretation.

- [ ] Keep Appendix B.4 roadmap wording scoped until prior-construction
      similarity evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.4 reports that the
    uncertainty-inequality linear combination found by AlphaEvolve is
    qualitatively very similar to the construction in reference `[33]`, and
    uses that similarity as empirical support for the hypothesis that the
    construction is nearly optimal.
  - Current evidence: roadmap/README/paper-index wording can cite Appendix B
    numeric-result rows, coefficient/construction payload gaps,
    construction/verifier exports, and revised-result provenance. It does not
    require a separate B.4 comparison record that ties the AlphaEvolve
    construction to the prior `[33]` construction and labels the
    near-optimality hypothesis evidence.
  - Required result: when Appendix B.4 prior-construction comparison metadata
    and validators land, update ROADMAP, README, papers index, and code/paper
    TODOs so roadmap claims distinguish value improvement, method similarity,
    and empirical support for near-optimality.

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
    For `No context in the prompt`, the current registry is too broad for the
    paper definition: AlphaEvolve describes removing explicit problem-specific
    context, not removing the current program or evolutionary prior-program
    context. It does not prove that executed prompts omitted explicit context
    sources, nor does it classify local plugin/retrieval/failure sections as
    explicit context versus core evolutionary prompt ingredients; it only
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
    history or diagnostics proving absent explicit context sources, a
    paper-facing classification of local context-like sections, and separate
    evidence for whether current-program, parent/inspiration, and
    rendered-result sections stayed present as normal evolutionary prompt
    ingredients. Ensure the
    `Small base LLM only` harness records backend metadata, eligibility, and
    call-ledger evidence proving every relevant generation call used a single
    small/base model and no large-model route. Ensure the
    `No meta prompt evolution` harness records prompt-history, call-ledger, and
    prompt-program lineage evidence proving meta-prompt evolution was disabled
    for the ablation and enabled for the full-system comparator, plus the
    frozen human-authored prompt identity, source, revision, and context policy
    used for the human-prompter comparator. Ensure the
    `No full-file evolution` harness records the
    loss-function target scope, fixed tensor-search components, and report
    evidence before claiming parity with Figure 8. Also require ablation
    reports to identify the matrix and kissing-number target families and
    validate target-metric identity/direction/normalization plus
    mean/standard-deviation curve summaries against per-target three-seed
    records before treating generic declared-target reports as
    Figure 8-equivalent.

- [ ] Keep Figure 8 roadmap visual wording scoped until ablation-curve exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 8 presents a two-panel visual comparison
    of ablation curves for matrix tensor decomposition and kissing-number
    sphere packing, with compute-budget fraction on the x-axis, aggregated
    target metric on the y-axis, named method curves, and shaded intra-target
    standard-deviation bands over three independent seeded runs.
  - Current evidence: roadmap/README/paper-index status can cite the ablation
    report contract, hashed curve artifacts, and open executable-harness,
    target-family, and aggregation gaps. They do not require a Figure 8 exhibit
    ID, panel IDs, series/legend mappings, exact paper legend labels, axis
    labels/scales, plot style and standard-deviation band metadata, source
    PDF/caption location, rendered plot artifact hashes, or links from the
    displayed visual to report rows and raw seed traces. The checked-in
    ablation registry currently labels the baseline `Full`, while Figure 8
    labels the curve `Full method`, so roadmap status should not treat current
    registry labels as exact paper-legend evidence.
  - Required result: when Figure 8 visual exhibit provenance lands, update
    ROADMAP, README, papers index, and code/paper TODOs with plot-level
    metadata and validators so roadmap wording distinguishes generic
    equal-budget curve artifacts from reproduced AlphaEvolve Figure 8 visual
    evidence, including exact legend labels such as `Full method`.

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
