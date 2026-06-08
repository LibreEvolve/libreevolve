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

- [ ] Keep cascade roadmap wording scoped until promotion/attrition reports
      exist.
  - Spec evidence: AlphaEvolve Section 2.4 says evaluation cascades can use
    ensembles of test cases with increasing difficulty, promote candidates to
    later stages only after promising earlier-stage results, prune less
    promising solutions quickly, and run small-scale checks before main tests.
    The matrix-multiplication experiment also evaluates targets with multiple
    random seeds using that cascade.
  - Current evidence: ROADMAP and README can claim local configured evaluator
    stages with thresholds, samples, retries, seeds, budgets, and persisted
    per-candidate `configured_stage_results`. They do not yet require a
    run-level paper report that aggregates stage entry/pass/fail counts,
    difficulty or scale rationale, seed/sample denominators, early-prune
    attrition, main-test exposure, or per-stage cost summaries.
  - Required result: when cascade-report artifacts land, update ROADMAP,
    README, papers index, and code/paper TODOs together so roadmap wording
    separates local stage-threshold mechanics from AlphaEvolve-style
    cascade-efficiency and hypothesis-testing evidence.

- [ ] Keep evaluator-entrypoint roadmap wording scoped to external validators
      until embedded `evaluate(eval_inputs)` support exists.
  - Spec evidence: AlphaEvolve Section 2.1 and Figure 3 use a candidate
    codebase with an `evaluate(eval_inputs) -> dict[str, float]` function that
    invokes the evolved skeleton. Local PDF page 4 describes the user-provided
    evaluator as a Python `evaluate` function with a fixed input/output
    signature, and Figure 3 on page 6 says evaluators invoke the Figure 3(a)
    `evaluate` function to score the modified program.
  - Current evidence: `ROADMAP.md` can claim configured local validators,
    staged evaluator entrypoints, direct evaluator path provenance, and
    problem-local dependency policy. Current code materializes candidate files
    into a temporary workspace, imports the configured problem `validate.py`,
    and calls that validator's `evaluate(code[, workspace[, stage]])`; metadata
    records `validate_path` and candidate files, but not a discovered
    candidate-owned `evaluate(eval_inputs)` callable. The `workspace_math`
    fixture proves external validators can import candidate modules, not that
    the candidate owns the evaluator entrypoint. It should not imply that these
    external validators are equivalent to a candidate-owned evaluator
    entrypoint.
  - Required result: when embedded evaluator entrypoints land, update ROADMAP,
    README, papers index, and code/paper TODOs with `evaluate` callable
    provenance, eval-input dataset provenance, skeleton-to-block invocation
    evidence, callable discovery diagnostics, isolation/build policy, and
    score-field mapping.

- [ ] Keep Figure 1/Figure 2 roadmap wording scoped until process-diagram
      provenance exists.
  - Spec evidence: AlphaEvolve Figure 1 shows the high-level architecture from
    human-defined problem inputs through LLM ensemble, prompt sampler,
    evaluator pool, and program database to an improved solution on local PDF
    page 3. Figure 2 on page 4 expands the loop with database sampling, prompt
    construction, LLM diff generation, diff application, evaluator execution,
    and database admission.
  - Current evidence: ROADMAP and README describe local components and
    synchronous workflow behavior, while other TODOs track specific gaps for
    prompt sampling, LLM scheduling, evaluators, database memory, and async
    controller state. Current code has a serial `evolve()` path that can be
    mapped to Figure 2 at a high level: `db.sample()`,
    `prompt_sampler.build()`, `_generate_with_budget()`,
    `apply_workspace_mutation()`, `evaluator.evaluate()`, `db.admit()`, and
    `db.log()`. Final runtime manifests also record a
    `single_process_serial_loop` / `terminal_synchronous_controller_drained`
    controller state and event/artifact streams for history, failures,
    archive events, controller budget events, LLM calls, prompt history, and
    evaluator artifacts. ROADMAP does not require Figure 1/Figure 2 exhibit
    IDs, node/edge-to-component mappings, implemented versus unsupported status
    per diagram node, Figure 2 pseudocode-line mappings, source PDF/caption
    locations, rendered diagram artifacts and hashes, or links from each
    displayed process step to current run artifacts.
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

- [ ] Add roadmap gate for persisted validator-boundary consistency evidence.
  - Spec evidence: AlphaEvolve-scale evaluator provenance should let a reader
    verify that every saved candidate attempt used the execution boundary
    claimed by the run manifest, not just that the manifest names a policy.
  - Current evidence: `ROADMAP.md` tracks local subprocess validators,
    minimal environments, wall-clock budgets, process-tree cleanup, and the
    broader OS/container sandbox/resource-control gap. It does not yet require
    a run-artifact validator that loads `manifest.json`, scans saved
    evaluation metadata, and applies
    `validate_validator_boundary_consistency()` to every
    `evaluation.metadata.validator_boundary` record.
  - Required result: when persisted validator-boundary consistency validation
    lands, update ROADMAP, README, papers index, and code/paper TODO entries
    together so roadmap wording separates the callable policy helper from a
    history-wide artifact gate and keeps both distinct from stronger
    sandbox/resource enforcement.

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
    by link policy, byte count, and SHA-256. That verification is still tied to
    the configured local copy path; it does not yet define a portable
    source-root, release-artifact, or cross-machine replay identity for copied
    static assets.
  - Required result: when arbitrary binary mutation, non-encoded generated
    binary deltas, binary replay, portable static-source roots, or broader
    artifact runners land, update the roadmap, README, papers index, and
    code/paper TODO entries together.

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
    only minimal changes. The local AlphaEvolve PDF page 4 describes adding
    `# EVOLVE-BLOCK-START` / `# EVOLVE-BLOCK-END` comments to integrate with
    existing codebases, and Figure 3 on page 6 shows those marked components
    beside an `evaluate(eval_inputs)` function used by evaluators.
  - Current evidence: ROADMAP, README, and papers-index wording can cite
    Python evolve-block markers, marker validation, unsupported non-Python
    marker diagnostics, workspace materialization, file topology support,
    `best_workspace/` export, and the `workspace_math` nested package plus
    JSON/static-asset smoke fixture. They do not yet require evidence for a
    pre-existing codebase integration workflow: marker-only setup diff,
    preserved skeleton hashes across a real upstream tree, language/comment
    syntax, evolved-block span inventory, evaluator-call continuity,
    source-root/release-artifact identity for copied static assets, or
    setup-change counts.
  - Required result: when existing-codebase integration metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODO entries
    together so roadmap wording separates marker parser support from
    AlphaEvolve-style minimal-change integration evidence and does not treat
    local workspace smoke tests as codebase-integration proof.

- [ ] Keep marker roadmap wording scoped until Figure 3 marker-variant
      metadata exists.
  - Spec evidence: AlphaEvolve Section 2.1 names the marker comments as
    `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END` on local PDF page 4,
    while PDF text extraction from Figure 3(a) on page 6 shows one opening
    marker as `# EVOLVE-BLOCK START` and another as `# EVOLVE-BLOCK-START`.
  - Current evidence: ROADMAP can point to local Python evolve-block marker
    parsing, validation, unsupported marker diagnostics, and the exact local
    parser behavior that treats the Figure 3 space variant as unsupported when
    paired with an end marker. It does not yet require source-location metadata
    that classifies the Figure 3 marker-text variant before roadmap wording
    treats it as canonical paper prose, rendered figure text, extraction/OCR
    uncertainty, or paper typo.
  - Required result: when Figure 3 marker source metadata lands, update
    ROADMAP, README, papers index, and code/paper TODO entries together so
    roadmap language separates local marker grammar work from any deliberate
    compatibility or documentation decision about the space variant and does
    not imply support until parser tests prove that support.

- [ ] Keep candidate-abstraction roadmap wording scoped to hooks until
      abstraction-choice reports exist.
  - Spec evidence: AlphaEvolve Section 2.1 and Discussion treat candidate
    abstraction as a problem-dependent experimental choice with known biases:
    direct solution search, constructor functions, bespoke search algorithms,
    or paired intermediate solution/search representations can suit different
    problem structures. In the local PDF, page 5 names "Flexibility in choosing
    the abstraction" and page 21 states that direct search, constructors, and
    search algorithms bring different biases.
  - Current evidence: `ROADMAP.md` asks for problem-defined candidate
    abstraction hooks and README identifies the current code-file-set
    abstraction boundary. Current manifests also record
    `policies.candidate_language` as `python_primary_text_workspace_v1`,
    `bounded_utf8_text_workspace_with_typed_static_members`,
    `language_runner_ready: False`, and
    `problem_defined_solution_abstractions: unsupported`. Roadmap wording does
    not yet require benchmark metadata or reports that justify the chosen
    abstraction, mark unsupported alternatives, or compare alternative
    formulations under equal budgets.
  - Required result: when abstraction-choice metadata, rationale fields,
    symmetry/structure labels, unsupported-abstraction diagnostics, paired
    solution/search support, or equal-budget abstraction-comparison reports
    land, update ROADMAP, README, papers index, and code/paper TODOs together
    so roadmap language does not confuse hooks with AlphaEvolve-style
    abstraction-selection evidence.

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
    affected performance. In the local PDF, page 10 distinguishes the simple
    initial program used for most Table 2 matrix results from parameters where
    researchers seeded the initial program with their own ideas and improved
    performance.
  - Current evidence: ROADMAP and README/code evidence show source-safe seed
    ingestion and generation-0 baseline provenance. Current manifest seed
    records are source identity records (`seed_index`, `seed_source_kind`,
    `seed_source_path`, primary file, file count, and file list), and inline
    seeds have only index plus kind. Roadmap wording does not yet require
    benchmark seed metadata for simple/random starts versus human-idea-seeded
    starts, injected prior techniques, idea-origin labels, or equal-budget
    seed-variant result comparisons.
  - Required result: when benchmark seed metadata, idea-origin validation, and
    seed-variant reports land, update roadmap, README, papers index, and
    code/paper TODO entries together so roadmap text distinguishes source-path
    provenance from AlphaEvolve-style human-seeded experiment provenance.

- [ ] Keep roadmap seed-validity wording scoped to permissive baselines versus
      AlphaEvolve-strict complete initial programs.
  - Spec evidence: AlphaEvolve Section 2.1 expects the initial implementation
    inside evolvable blocks to be complete, although possibly rudimentary, and
    runnable through the supplied task skeleton/evaluator. Local PDF page 5
    says user-provided code inside evolution blocks serves as the initial
    solution, while Figure 2 on page 4 shows the initial program as an input
    before the loop.
  - Current evidence: ROADMAP and README currently document source-safe seed
    ingestion, skipped-seed diagnostics, generation-0 baselines, and example
    seed-score classes. The implementation evaluates seeds, admits valid
    seeds, logs invalid seed failures, and can complete a seed-only run with
    all seeds invalid using `stop_reason=no_valid_programs`. Current permissive
    optimization-pressure seeds are therefore not equivalent to an
    AlphaEvolve-strict complete initial-program precondition.
  - Required result: when a strict initial-program validity policy, benchmark
    seed-validity report fields, and README/paper-index wording land, update
    roadmap text so it neither rejects the current permissive examples nor
    overclaims that invalid generation-0 baselines satisfy AlphaEvolve's
    complete initial-implementation requirement.

- [ ] Keep roadmap problem-formulation wording scoped to context artifacts
      until expert provenance exists.
  - Spec evidence: AlphaEvolve Section 3.2 says external mathematicians
    suggested open problems and advised on formulation, while Section 2.1 makes
    task definition and optional background knowledge explicit human inputs;
    Figure 1 also separates the human-defined "what" from AlphaEvolve's search
    over "how" by naming evaluation criteria, initial solution, and optional
    background knowledge as human-provided setup.
  - Current evidence: ROADMAP and README/code evidence cover local context
    source ingestion, ranking/filtering, and source/problem provenance, but do
    not require benchmark metadata for expert contributor roles, formulation
    advice, objective/evaluator rationale, mathematical parameter-scope
    decisions, or expert review/signoff state. Runtime evidence records a
    problem tree digest, config/plugin/environment/source provenance, and
    loader-validated task/metrics/validator/seed files; it does not identify
    who formulated the benchmark or why the objective and search scope are
    authoritative.
  - Required result: when expert formulation metadata and report evidence land,
    update roadmap, README, papers index, and code/paper TODO entries together
    so roadmap text neither underclaims context provenance nor overclaims
    AlphaEvolve-style expert-guided benchmark formulation.

- [ ] Keep robustness and versatility roadmap wording scoped until early-user
      feedback provenance exists.
  - Spec evidence: AlphaEvolve's Acknowledgements say early users and
    collaborators supplied diverse use cases and insightful feedback that
    shaped AlphaEvolve into a more robust and versatile tool. This is a
    product/process feedback claim, not the same as evaluator output,
    archive-feedback context, or LLM-grader feedback inside the search loop.
  - Current evidence: ROADMAP and README/code evidence track implemented
    surfaces, benchmark examples, expert formulation gaps, and systems
    owner/reviewer gaps. They do not require roadmap milestones or report
    schemas for early-user/collaborator feedback event IDs, use-case taxonomy,
    affected workflow areas, resulting changes, validation outcomes, or
    privacy/redaction policy. Current roadmap and code surfaces cover
    candidate feedback, feedback-sourced objective metrics, and LLM feedback
    calibration artifacts, but not external feedback cohorts or
    feedback-to-change provenance for robustness claims.
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
    application-specific work. The local paper text exposes general
    acknowledgement roles on page 21 and application-specific review/advice
    roles on page 22, making this a separate paper-process/governance evidence
    category.
  - Current evidence: ROADMAP and README/code evidence track expert
    formulation, early-user feedback, systems owner/reviewer gaps, and
    contribution-role gaps. They do not require acknowledgement-role metadata
    for paper-process review/support/advice records or docs wording that
    separates those roles from implementation authorship, benchmark
    formulation, domain validation, deployment signoff, broad collaborator
    feedback, publication-author metadata, or package/project metadata.
  - Required result: when acknowledgement-role metadata lands, update ROADMAP,
    README, papers index, and code/paper TODOs with role categories, affected
    paper/application scope, source page/section, and privacy/redaction policy
    so roadmap wording does not treat acknowledgement-process roles as
    technical validation or system-development provenance.

- [ ] Keep paper-author roadmap wording scoped until publication-author
      metadata exists.
  - Spec evidence: AlphaEvolve's Author information names equal contributors
    and corresponding authors, while the Contributions section identifies
    manuscript writers and paper-input contributors. Page 1 defines the
    equal-contribution marker, page 22 begins Author information and
    Contributions, and page 23 lists corresponding authors.
  - Current evidence: ROADMAP and README/code evidence track contribution-role
    gaps, paper-artifact creator roles, acknowledgement-role gaps, and
    application owner/reviewer gaps. They do not require publication-author
    metadata for equal-contributor status, manuscript-writing roles,
    paper-input roles, or correspondence, nor docs wording that separates those
    metadata from technical implementation, artifact creation, validation,
    title-page affiliation, package/project metadata, or acknowledgement
    evidence.
  - Required result: when paper-author metadata lands, update ROADMAP, README,
    papers index, and code/paper TODOs with safe contributor labels, author
    role categories, source page/section, title-page marker linkage,
    publication scope, and contact/privacy redaction policy so roadmap wording
    does not conflate publication metadata with AlphaEvolve technical
    capability provenance.

- [ ] Keep source-affiliation roadmap wording scoped until title-page
      affiliation metadata exists.
  - Spec evidence: page 1 of the AlphaEvolve PDF gives the title-page
    affiliation line `Google DeepMind1` plus footnotes `1See Acknowledgments
    and Author information section.` and `*Equal contributions.` It also
    carries the source-paper rights line `© 2025 Google DeepMind. All rights
    reserved`, which is related but separate source-rights evidence.
  - Current evidence: ROADMAP and README can cite LibreEvolve's independent
    non-affiliation statement, source-PDF version/rights TODOs, and
    publication-author metadata gaps. They do not require roadmap evidence for
    title-page affiliation/organization text, footnote marker definitions,
    author-to-marker mapping, source page/span, or docs wording that separates
    source-paper affiliation evidence from local project ownership,
    endorsement, author metadata, source-rights records, and system-development
    provenance. `paper_manifest` gates validate cache rows, local PDF hashes,
    and PDF readability, but not title-page affiliation or marker semantics.
  - Required result: when title-page affiliation provenance lands, update
    ROADMAP, README, papers index, and code/paper TODOs with affiliation text,
    marker ids, footnote text, author-marker mappings, source locator, and
    privacy/redaction policy plus linkage to source-rights metadata, so roadmap
    wording distinguishes source-paper organization metadata from LibreEvolve's
    affiliation, licensing, and endorsement boundaries.

- [ ] Keep system-development roadmap wording scoped until contribution-role
      provenance exists.
  - Spec evidence: AlphaEvolve's Contributions section attributes core system
    development work across initial implementation, project vision and problem
    scoping, first benchmark iteration, final system development,
    infrastructure maintenance, code reviews, team coordination, and
    supervision. Local PDF pages 22-23 separate those categories from
    publication-author, acknowledgement, and application-review roles.
  - Current evidence: ROADMAP and README can cite local implementation status,
    source provenance, tests, and open contribution guidance. They do not
    require roadmap evidence for contribution-role records, development-phase
    attribution, infrastructure ownership, benchmark-iteration ownership,
    review responsibility, or coordination/supervision scope. Runtime manifests
    and environment provenance can record source hashes, Git state, and package
    authors/maintainers, but not paper-attributed system-development role
    boundaries.
  - Required result: when contribution-role metadata lands, update ROADMAP,
    README, papers index, and code/paper TODOs with role labels, development
    phase, artifact/module linkage, source page/section, and review/approval
    scope so roadmap wording separates local implementation plans, package
    metadata, and repository history from AlphaEvolve-style paper-attributed
    system-development provenance.

- [ ] Keep workspace-topology roadmap scope aligned with current
      materialization diagnostics.
  - Spec evidence: AlphaEvolve-style codebase evolution should turn invalid
    generated artifacts into stable evaluator feedback instead of opaque local
    filesystem failures, especially as program artifacts and runners become
    broader than the current local workspace. The AlphaEvolve PDF describes
    evolving multiple codebase components on page 4, larger-codebase diff
    sequences on page 7, and entire-codebase evolution on pages 18-19.
  - Current evidence: `ROADMAP.md` currently names workspace file topology
    mutations for create/edit/delete/move/rename and primary-file changes, and
    its near-term workspace section asks to keep topology-operation collision
    policy and structured materialization-failure diagnostics complete as new
    workspace, language, and build-runner edge cases are introduced. Code and
    paper TODO evidence already scope the implemented coverage to current
    `CandidateMaterializationError` reason/path diagnostics, bounded
    `materialization_error` metadata, link/junction rejection, static
    source-copy verification, topology command prevalidation, and prompt
    rendering controls for selected materialization-error fields. That coverage
    is still local-workspace oriented and should not be presented as complete
    for arbitrary language runners, build outputs, dependency manifests, or
    remote/containerized execution surfaces.
  - Required result: when future topology surfaces such as bulk directory
    operations, language/build-runner generated artifacts, external
    materialization paths, or richer artifact runners land, update the roadmap,
    README, papers index, and code/paper TODO entries together so roadmap
    wording neither underclaims current structured invalid-workspace feedback
    nor overclaims AlphaEvolve-grade codebase-scale diagnostics.

- [ ] Keep roadmap code-scale wording scoped to benchmark-backed evidence.
  - Spec evidence: AlphaEvolve Table 1 says AlphaEvolve evolves entire code
    files, hundreds of lines of code, arbitrary languages, and complex
    algorithms with multiple functions/components. Local PDF page 2 contains
    the Table 1 code-length and file/function comparison rows, while pages
    18-19 discuss entire-codebase evolution.
  - Current evidence: ROADMAP correctly lists current workspace mechanics:
    Python seed workspaces, file topology mutations, materialization
    diagnostics, and the small `workspace_math` fixture. Scope records mark
    shipped examples, including `workspace_math`, as smoke fixtures with
    `alphaevolve_comparable: False`. Those features do not yet prove large
    multi-component generated-code performance, arbitrary-language execution,
    or build-runner parity.
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

- [ ] Keep distributed-pipeline roadmap wording scoped until topology evidence
      exists.
  - Spec evidence: AlphaEvolve Section 2.6 says the system is an asynchronous
    pipeline made of a controller, LLM samplers, and evaluation nodes; work can
    run concurrently, block on unfinished dependencies, and is optimized for
    throughput under an overall computation budget.
  - Current evidence: ROADMAP can cite terminal controller-state snapshots,
    controller-budget events, future bounded queues, and async-worker gaps.
    Runtime manifests explicitly validate the current controller as
    `single_process_serial_loop` with zero queued/running work and limitations
    that it is not an async queue checkpoint. The roadmap does not yet require
    a topology artifact that names controller/sampler/evaluation-node roles,
    queue capacities, dependency edges, worker ownership, or throughput-budget
    linkage.
  - Required result: when distributed-pipeline topology reports land, update
    ROADMAP, README, papers index, and code/paper TODOs together so roadmap
    wording distinguishes the synchronous controller boundary from
    AlphaEvolve-style controller/sampler/evaluation-node topology evidence.

- [ ] Keep Table 1 roadmap wording scoped until capability-table exhibit
      provenance exists.
  - Spec evidence: AlphaEvolve Table 1 is a row-level comparison between
    FunSearch and AlphaEvolve covering code/file scale, code length, language
    scope, evaluator duration/parallelism/accelerators, sample counts, model
    scale, prompt context/feedback, and single versus multiple metrics. Local
    PDF page 2 contains the eight rows and caption.
  - Current evidence: `ROADMAP.md`, README, papers index, and code TODOs track
    several individual Table 1 rows as separate implementation/report gaps.
    They do not require Table 1 itself to have stable table/row ids, source
    PDF/caption location, exact FunSearch/AlphaEvolve comparison text,
    row-to-TODO/report mappings, row-level status, rendered artifact hashes,
    or validation that partial row evidence is not summarized as complete
    Table 1 parity. The existing README comparison table is not enough because
    it is not tied to stable source-table row records.
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
    diff application, evaluator execution, and database updates. Local PDF
    pages 3-4 provide the Figure 1/2 captions and Figure 2 displayed
    controller lines.
  - Current evidence: `ROADMAP.md`, README, papers index, and code TODOs track
    several Figure 1/2 component gaps, but the roadmap does not require Figure
    1 or Figure 2 to have stable figure IDs, diagram-node and edge records,
    Figure 2 pseudocode-line mappings, exact diagram text, source PDF/caption
    locations, rendered artifact hashes, component-to-code/report/TODO links,
    or validation that partial component coverage and local workflow prose are
    not summarized as full process-diagram parity.
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
    and optional background knowledge. On local PDF page 4, Figure 2 labels
    "Initial program", "Prompt template", "Evaluation code", "LLMs ensemble",
    and "Background knowledge"; the caption says the user provides the initial
    program, evaluation code, and optional configurations before the loop.
  - Current evidence: `ROADMAP.md`, README, and manifests can describe
    problem/source provenance, seed sources, evaluator sources, backend specs,
    prompt variants, redacted/hash-backed effective config, and context-source
    diagnostics. Current startup manifests persist these as separate
    `config`, `problem`, `policies`, and `provenance` sections rather than a
    field-level AlphaEvolve task-spec bundle. They include task/problem
    provenance, objective schema, context sources/policy, evaluator sources,
    seed sources/policy, prompt variants and prompt metadata, backend specs,
    role-backend routing, candidate-language policy, and source/plugin/
    environment provenance. They do not yet require a single validated
    task-spec artifact with AlphaEvolve field names, presence/omission status,
    source hashes, redaction policy, or links from each input field to the run
    evidence it controls.
  - Required result: when task-spec bundle records land, update ROADMAP,
    README, papers index, and code/paper TODOs with initial code/workspace
    ids, evolvable spans, evaluator-code ids, prompt-template/config ids, LLM
    choice ids, optional background-knowledge ids, hashes/redaction state,
    artifact cross-links, and missing/unsupported-field diagnostics so roadmap
    wording separates scattered local provenance from a coherent AlphaEvolve
    task specification.

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
    ablation registry checks. `validate_paper_manifest()` now also validates
    the paper-index TODO coverage table's manifest-id coverage,
    duplicate/extra rows, safe existing active/completed `docs/todo/` paths,
    active/completed path classification, and active references that still
    contain open TODO evidence for the same paper id. Remaining roadmap gap:
    docs do not yet describe that validator scope or the still-open
    completed/grouped evidence semantics and implementation-status semantic
    validation boundaries.
  - Required result: update ROADMAP, README, papers index, and code/paper
    TODOs with the validator scope and failure modes so roadmap wording
    distinguishes shareable cache/status diagnostics from verified backlog
    traceability.

- [ ] Keep roadmap backlog-integrity wording scoped until stale absence prose
      is detected inside TODO bodies.
  - Spec evidence: ROADMAP planning depends on active TODO entries as a truthful
    map of remaining AlphaEvolve and paper-alignment work. Once source-specific
    TODOs have been created, roadmap-facing backlog diagnostics should not
    leave older entries saying that such TODO coverage is absent.
  - Current evidence: `validate_paper_manifest()` now validates free-form
    current-gap prose inside active TODO bodies for manifest-id-scoped stale
    absence phrases. It detects explicit `no source-specific ... TODO`
    wording, maps code/paper/README/ROADMAP targets to the active ledgers, and
    reports contradictions when the target ledger already has an open TODO
    block for that paper id. Remaining roadmap gap: README/ROADMAP/paper-index
    wording does not yet describe this validator scope, and future paraphrases
    outside the current phrase family need additional patterns.
  - Required result: update ROADMAP, README, papers index, and code/paper
    TODOs with the validator scope: manifest-id matching, target-ledger
    detection, contradictory absence-phrase reporting, and rewrites that
    distinguish missing evidence from missing TODO coverage.

- [ ] Keep implementation-status roadmap wording scoped until semantic cells
      are validated.
  - Spec evidence: the roadmap depends on `papers/README.md` as the
    paper-facing status index for which sources are specification targets,
    background influences, partially implemented surfaces, smoke fixtures, or
    unsupported paper claims. Since manifest titles are only cache slugs, the
    implementation-status table's title, role, and status cells carry the
    public AlphaEvolve-alignment meaning.
  - Current evidence: current validation reconciles manifest ids, README
    counts, Appendix B registry shape, ablation registry shape, TODO coverage
    rows, and stale absence prose. `_read_status_table_ids()` now also
    validates the implementation-status table's stable header, complete
    four-cell row shape, non-empty safe title/role/status cells, declared role
    taxonomy, allowed status class prefixes, role/status compatibility,
    active evidence path presence, and completed-evidence path presence for
    rows claiming partial/implemented/local-only support; completed evidence
    paths must also exist under `docs/todo/Completed/` and contain completed
    checklist text that names the paper id or source PDF. README, ROADMAP, and
    the paper index now describe this validator boundary without claiming full
    semantic proof. Row-specific open TODO blocks must now include
    Current/Remaining gap or Current evidence context plus a `Required result:`
    field. The validator also now rejects
    benchmark coverage `Implemented:` bullets that are phrased as not
    implemented, requires those bullets to cite a local code/artifact path, and
    it rejects unqualified
    `AlphaEvolve-comparable` status-table overclaims
    unless the phrase is framed as missing, scoped, or requirement-bound
    evidence, and it rejects background-only/future-benchmark status classes
    that include positive implementation-support wording. Bare `Background
    only` status classes must now include an explicit missing/unsupported
    behavior boundary. `Not implemented; potential future benchmark` status
    classes must now include an explicit missing verifier/harness or
    unsupported-behavior boundary. `Implemented as` status classes must now
    include an explicit scoped/open or out-of-scope behavior boundary.
    `Partially implemented:` status classes must now include an explicit
    remaining/missing/unsupported behavior boundary. Limited `Only` status
    classes must now include an explicit
    missing/unsupported behavior boundary. `Static prompt guidance exists`
    status classes must now also
    state that the guided operation is not executed or enforced. `Not
    implemented as described:` status classes must now also name an explicit
    missing or unsupported paper behavior. Implemented, partial, limited, and
    static-guidance support claims must now also cite a local code/artifact
    path in the implementation-status cell. Remaining roadmap gap: the
    validator does not yet prove that every named behavior inside long status
    claims is linked to specific active/completed evidence records at semantic
    phrase level or deeply verify smoke/partial/planned/unsupported qualifiers
    beyond the role/status class matrix, required path presence, active-block
    structure checks, source-specific completed-evidence path checks,
    status-claim local-artifact anchors, the benchmark-implemented
    contradiction/local-artifact guards, the `AlphaEvolve-comparable` overclaim
    guard, the negative-status contradiction guard, the background-only
    boundary guard, the future-benchmark boundary guard, the implemented-status
    boundary guard, the partial-status boundary guard, the limited-status
    boundary guard, the static-guidance execution-boundary guard, and the
    not-implemented-as-described boundary guard.
  - Required result: extend status validation with phrase-level links from
    status claims to active or completed evidence plus richer qualifier checks.
    Keep this distinct from the already documented TODO coverage
    cross-reference validation, which validates the separate backlog pointer
    table.

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

- [ ] Keep stochastic-formatting roadmap wording scoped to marker mechanics
      until distribution provenance exists.
  - Spec evidence: AlphaEvolve Section 2.2 says stochastic formatting uses
    template placeholders with human-provided alternatives and probability
    distributions from a separate config file.
  - Current evidence: ROADMAP and README can cite implemented
    `prompt_format_options`, weighted `[[prompt:name]]` markers, run-local RNG
    selection, repeated-marker reuse, prompt diagnostics, and manifest
    redaction for option text. They do not yet require paper-facing records
    that preserve the full normalized probability distribution, option-set
    source file or inline effective-config boundary, selected alternative per
    prompt/call, and RNG/replay semantics.
  - Required result: when stochastic-formatting distribution records and
    validators land, update ROADMAP, README, papers index, and code/paper TODO
    entries together so roadmap wording distinguishes current weighted marker
    support from AlphaEvolve-style prompt-diversity evidence.

- [ ] Keep rendered-evaluation-result roadmap wording scoped until prompt
      prior-score provenance exists.
  - Spec evidence: AlphaEvolve Section 2.2 says prompts can contain rendered
    evaluation results with the program, execution result, and scores assigned
    by `evaluate`; Figure 3(c) shows prior programs with metric-score headers
    and an aggregate `average_score` before code.
  - Current evidence: ROADMAP, README, and papers-index wording can cite
    prompt-visible parent metrics, inspiration fitness/metrics, declared
    metric normalization diagnostics, selected parent/inspiration metadata,
    and prompt history ids. They do not yet require a prompt prior-score record
    that links each rendered prior/current program's displayed score header to
    a persisted evaluator result, execution output/artifact, aggregate formula,
    and omission/truncation decision.
  - Required result: when prompt prior-score records and validators land,
    update ROADMAP, README, papers index, and code/paper TODO entries together
    so roadmap wording separates current metric rendering from
    AlphaEvolve-style rendered evaluation-result evidence tied to prompt calls
    and evaluator history.

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
    Local PDF page 21 is the source for both claims.
  - Current evidence: ROADMAP.md tracks provider/runtime budgets, systems
    benchmarks, and benchmark/report contracts, but it does not yet require
    report evidence for optimizing LibreEvolve's own runtime or provider
    infrastructure, nor does it define distillation data/export/training
    evidence derived from evolved candidates. Existing ThetaEvolve-inspired
    training-data export is a bounded plugin artifact, not evidence of
    base-model distillation or deployed self-improvement.
  - Required result: when roadmap items cover self-improving infrastructure or
    base-model uplift, require target-component identity, before/after
    measurements, deployment/adoption status, rollback/safety evidence,
    provenance linking the optimized component to LibreEvolve's own execution,
    and distillation dataset/training/evaluation artifacts where relevant.
    Update ROADMAP, README, papers index, and code/paper TODO entries together
    so roadmap wording treats those claims as future evidence requirements,
    not current AlphaEvolve parity.

- [ ] Keep self-improvement roadmap wording scoped until feedback-loop cadence
      and environment ROI evidence exists.
  - Spec evidence: AlphaEvolve's Discussion says current self-improvement
    gains are moderate, feedback loops for improving the next AlphaEvolve
    version take months, and those improvements should make setting up more
    robust-evaluator environments more valuable.
  - Current evidence: ROADMAP tracks self-improving infrastructure and
    distillation as future evidence requirements, plus separate automated-
    evaluator scope and environment-readiness gaps. It does not require
    roadmap milestones or reports to preserve loop cadence, next-version
    dependency, gain magnitude calibration, environment setup cost, or realized
    discovery value from adding new evaluator environments.
  - Required result: when feedback-loop cadence or environment-expansion
    reports land, update ROADMAP, README, papers index, and code/paper TODOs
    together so roadmap text separates generic self-improvement readiness from
    AlphaEvolve's months-scale feedback-loop and robust-environment ROI
    claims.

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

- [ ] Keep prompt-current edit provenance roadmap wording scoped until binding
      evidence exists.
  - Spec evidence: AlphaEvolve Figure 3(b,c) and Section 2.3 present
    SEARCH/REPLACE as edits to the current program shown in the prompt, with
    exact SEARCH segments matched against that version.
  - Current evidence: ROADMAP can cite parent sampling, prompt diagnostics,
    prompt-program ids, retained prompt hashes, parent/candidate lineage,
    mutation payloads, LLM call telemetry, and candidate history. It does not
    yet require a single proof record showing that each accepted or rejected
    mutation target was the same current-program version rendered to the model.
  - Required result: when prompt-current binding reports land, update ROADMAP,
    README, papers index, and code/paper TODOs with prompt id, prompt-program
    id, LLM call id, parent/current program id, rendered current-program
    hashes/path policy, mutation target hashes, diff match spans or full-mode
    target policy, evaluator/admission links, and candidate status so roadmap
    wording does not overclaim AlphaEvolve-style current-program edit
    provenance from separate parent, prompt, and history fields.

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
    `alphaevolve_comparable: false`. The shipped-example scope registry has
    focused tests, but the standard paper-manifest/docs validation path does
    not yet validate that registry directly.
  - Required result: when tensor/geometric/compiler/systems fixtures emit
    benchmark-grade hardening reports, and when the shipped-example scope
    registry is wired into the standard validation gate, update the roadmap,
    README, papers index, and code/paper TODO entries together so they neither
    underclaim smoke hardening evidence nor overclaim AlphaEvolve-comparable
    benchmarks.

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

- [ ] Keep hardware roadmap wording scoped until Gemini-to-TPU contribution
      attribution exists.
  - Spec evidence: AlphaEvolve Section 3.3.3 says the hardware improvement was
    integrated into an upcoming TPU and represents "Gemini's first direct
    contribution to TPU arithmetic circuits", achieved through AlphaEvolve.
  - Current evidence: roadmap systems-result wording covers hardware
    verification, synthesis/PPA, designer signoff, upcoming-chip integration,
    standard-Verilog trust, and bit-removal rewrite provenance. It does not
    require hardware fixtures or reports to preserve the attribution evidence
    that links a Gemini/AlphaEvolve-produced RTL edit to a specific TPU
    arithmetic circuit and qualifies the "first direct contribution" claim.
  - Required result: when Gemini-to-TPU contribution metadata and validators
    land, update ROADMAP, README, papers index, and code/paper TODOs together
    so roadmap text distinguishes concrete RTL optimization evidence from the
    broader Gemini hardware-contribution claim, including model-family
    relation, TPU/circuit identity, integration milestone, hardware review,
    and downstream synthesis-tool rediscovery caveats.

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

- [ ] Keep paper-source roadmap wording scoped until manifest row identity is
      validated.
  - Spec evidence: roadmap claims about paper-cache provenance rely on each
    manifest row's id, URL, and local PDF label describing the same source
    before source-version, rights, or claim evidence is attached.
  - Current evidence: roadmap/README wording can cite safe paper-manifest ids,
    allowed HTTPS source URLs, safe local PDF paths, local hash/readability
    validation, and source-version TODOs. `libreevolve.tools.paper_manifest`
    does not yet parse arXiv ids out of source URLs, compare them with row ids
    and local filename source prefixes, or require explicit source-identity
    mapping for non-arXiv or slug rows.
  - Required result: once manifest row-identity validation lands, update
    ROADMAP, README, papers index, and TODO cross-links so roadmap wording
    distinguishes safe manifest fields from proven source identity, and
    separates base id/URL/file consistency from later arXiv version pinning.

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
    where appropriate. It gives a hosted `problems/{n}.html` URL pattern on
    `google-deepmind.github.io`, says no installation is required, says
    notebooks open in Google Colab and webpages open in any browser, and
    points the distribution graphic to root-level `status_grid.png`. Current
    `status.json` has buckets `world_record`, `former_record`,
    `worse_than_record`, and `matched_optimal`, listing 43 problem ids total.
  - Current evidence: roadmap TODOs require tracking the later paper,
    repository ref, problem inventory, and notebook artifacts, but they do not
    force roadmap language to separate complete problem-page coverage from
    partial notebook/artifact coverage, to record hosted-page URL/access modes,
    or to describe live-repository evidence as a pinned snapshot with
    root-level status-artifact provenance. They also do not require parsed
    status-bucket membership or explicit absent-status states for problem ids
    not listed in `status.json`. Existing coverage wording also needs to avoid
    unverified `assets/...` status paths.
  - Required result: once the coverage manifest is implemented, update ROADMAP
    milestones and evidence gates so follow-on AlphaEvolve math coverage names
    the repository snapshot, records hosted page URLs plus page/notebook/
    artifact availability by problem, records browser/Colab access modes,
    includes root-level status artifact hashes and parsed status-bucket
    membership when cited, records absent-status handling for unlisted problem
    ids, and avoids treating a live partial-notebook repository as fully static
    or notebook/status-complete.

- [ ] Keep follow-on problem-count roadmap gates scoped until numbered-page
      inventory is reconciled.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README says the repository contains descriptions for 67 mathematical
    problems, while the current live `problems/` directory exposes 68 numbered
    HTML files. `problems/67.html` and `problems/68.html` are both titled
    `Logic puzzles`; page 67 uses a placeholder Colab link, and page 68 uses a
    generic Colab URL plus a placeholder paper link.
  - Current evidence: roadmap TODOs require follow-on coverage snapshots,
    hosted page URLs, notebook/artifact availability, status bucket semantics,
    and live-repository policy. They do not require an evidence gate that
    reconciles paper/README problem count with live numbered HTML inventory or
    flags duplicate titles, repeated section mappings, and placeholder/generic
    resource links.
  - Required result: when numbered-page inventory validation lands, update
    ROADMAP, README, papers index, and code/paper TODOs so follow-on coverage
    gates include expected-versus-discovered page counts, page id/title/section
    mapping, duplicate diagnostics, resource-link validity, discrepancy
    classification, and snapshot-scoped wording for any 67-versus-68 source
    mismatch.

- [ ] Keep follow-on problem-repository rights and attribution gates scoped.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README asks users of the code or data to cite `Mathematical exploration and
    discovery at scale`, declares Google LLC copyright, Apache 2.0 licensing
    for software, CC-BY 4.0 licensing for other materials, an as-is warranty
    disclaimer, and a non-official-Google-product disclaimer. It credits
    Professors Javier Gomez-Serrano and Terence Tao with supervision, problem
    selection, review, analysis, and commentary, and says Problem 65 originates
    from the official IMO problems website.
  - Current evidence: roadmap TODOs already gate follow-on paper/repository
    source tracking and coverage snapshots, and separate the original
    companion-result repository rights. They do not require roadmap milestones
    to preserve this problem repository's citation instruction, dual license,
    artifact-type license mapping, contributor-role attribution, IMO-origin
    note, or non-endorsement boundary before using its webpages, notebooks,
    verifier code, data, or figures as evidence.
  - Required result: when follow-on source-use metadata lands, update ROADMAP
    evidence gates so problem-repository use requires repository
    URL/ref/commit/date, citation metadata, software/materials license split,
    disclaimer and non-official-product notes, role-attribution notes, Problem
    65 source-origin metadata, and README/papers cross-links that distinguish
    these terms from the original AlphaEvolve PDF, `alphaevolve_results`, and
    LibreEvolve's own license.

- [ ] Keep follow-on runtime-availability roadmap gates scoped.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README says notebooks contain prompts, verification code, initial programs,
    final evolved programs, and visualization/analysis code where appropriate,
    while explicitly stating that the repository does not contain the code to
    run AlphaEvolve.
  - Current evidence: roadmap TODOs separate companion-result runtime absence,
    follow-on problem-repository coverage, and source-use terms. They do not
    require roadmap gates that preserve the later repository's own
    runtime-absence boundary before treating notebooks as evidence.
  - Required result: once follow-on notebook metadata lands, update ROADMAP
    evidence gates so problem-repository notebooks require artifact-kind flags,
    verifier-versus-runtime classification, explicit AlphaEvolve-runtime
    absence with source span, and README/papers cross-links that avoid treating
    follow-on notebooks as runnable AlphaEvolve implementation artifacts.

- [ ] Keep Tao-blog follow-on roadmap claims scoped until source metadata
      exists.
  - Spec evidence: Terence Tao's November 5, 2025 post
    `Mathematical exploration and discovery at scale` links the follow-on
    arXiv paper and problem repository, describes 67 mathematics experiments,
    and adds commentary about scale, adaptability, interpretability,
    verifier-exploit behavior, exact/interval-arithmetic verifier hardening,
    one-sided open-conjecture bounds, negative-result recording,
    parameterized-code generalization, and proof handoffs involving humans,
    Deep Think, AlphaProof, or later papers.
  - Current evidence: roadmap TODOs track follow-on paper/repository evidence,
    repository coverage, source-use terms, and runtime absence, but they do
    not require a separate source row for Tao's blog or a policy that keeps
    blog-only lessons secondary to paper, repository, notebook, verifier, and
    proof artifacts.
  - Required result: when Tao-blog source metadata lands, update ROADMAP,
    README, papers index, and code/paper TODOs with canonical URL/date/author,
    retrieval/hash metadata, linked arXiv/repository ids, claim categories,
    and evidence gates so blog commentary does not become unqualified
    AlphaEvolve specification or implementation-parity evidence.

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
    cutoff rationale, or included/excluded target justifications. Its dedicated
    validator is not yet part of the standard paper-manifest validation gate,
    which currently checks Appendix B and ablation registries.
  - Required result: when Appendix A matrix curation metadata lands, update
    ROADMAP, README, papers index, and code/paper TODOs; also wire Appendix A
    registry validation into the paper-manifest gate so roadmap text
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

- [ ] Keep Strassen baseline roadmap wording scoped until helper output is
      pinned as a paper artifact.
  - Spec evidence: a roadmap item that cites a checked matrix baseline should
    distinguish implementation/test coverage for a generator helper from
    durable paper-evidence artifacts available in a checkout or CI artifact
    bundle.
  - Current evidence: roadmap/README/paper-index wording can cite the
    `write_strassen_2x2_publication_bundle()` helper and
    `validate_matrix_publication_bundle()` tests, but `rg --files` shows no
    committed `matrix/mm_2x2x2/` bundle outputs in the current repository, and
    the standard paper-manifest/docs validation path does not regenerate or
    verify those generated files.
  - Required result: once the Strassen baseline output is committed, generated
    by a documented command, or produced as a CI artifact, update ROADMAP,
    README, papers index, and code/paper TODOs with the output-root policy,
    artifact paths, hash/byte-count expectations, validation command, and
    wording that separates helper-generated baseline evidence from a non-toy
    executed benchmark or Appendix A suite discovery.

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

- [ ] Add 2026 AlphaEvolve impact-source roadmap gates before promoting new
      domain claims.
  - Spec evidence: Google DeepMind's May 7, 2026 article
    `AlphaEvolve: How our Gemini-powered coding agent is scaling impact across
    fields` reports newer official impact claims across genomics,
    power-grid optimization, Earth AI, quantum circuits, mathematics gallery
    examples, TPU design, cache replacement, Spanner, compiler storage, and
    Google Cloud/customer applications.
  - Current evidence: ROADMAP tracks original AlphaEvolve paper alignment,
    follow-on mathematical-problem sources, selected later paper rows, and
    local benchmark/report-contract gaps. It does not have roadmap gates for
    treating the 2026 impact article as a distinct source, mapping its claims
    to linked evidence, or preventing the named new domains from being
    promoted as LibreEvolve-supported workflows without fixtures.
  - Required result: add roadmap/source gates for the 2026 impact article:
    URL/date/title/retrieval digest, outbound-link inventory, claim category
    and value/unit/baseline records, evidence-state classification, public
    gallery/UI/API attribution metadata, local-fixture support status, and
    release-note/README boundaries that distinguish official impact reporting
    from original specification work and from future LibreEvolve benchmark
    implementation.

- [ ] Add FHE-on-TPU AlphaEvolve application gates before roadmap promotion.
  - Spec evidence: arXiv `2605.14718`, submitted May 14, 2026, reports using
    AlphaEvolve for hardware-aware Fully Homomorphic Encryption optimization
    on Google Cloud TPUv5e, with TFHE/Jaxite and CKKS/CROSS primitives,
    real-world hardware feedback, rigorous correctness tests, and latency
    speedups over human-engineered state of the art.
  - Current evidence: ROADMAP has background-only gates for several
    AlphaEvolve application-context rows and open hardware/compiler/system
    benchmark gaps. It does not mention this FHE/cryptography-on-TPU paper,
    define a source-manifest gate for it, or require local fixtures before
    promoting FHE accelerator optimization as supported.
  - Required result: add roadmap gates for `2605.14718`: paper/source
    manifest entry, PDF/cache hash, FHE scheme/primitive taxonomy,
    TPUv5e/hardware-execution provenance, baseline implementation identity,
    correctness-test evidence, latency metric and speedup records,
    code/artifact availability status, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local FHE
    kernel support.

- [ ] Add AlphaEvolve intentmaking/sensemaking HCI gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.05921`, submitted May 7, 2026, reports a
    formative user study with 11 expert mathematicians using AlphaEvolve and
    defines repeated intentmaking and sensemaking cycles as a workflow for
    AI-guided mathematical discovery.
  - Current evidence: ROADMAP tracks backend evolution, run inspection,
    source provenance, benchmark/report contracts, and source gates for
    impact/application papers. It does not mention `2605.05921`, define an HCI
    source-manifest gate, or require interactive UI/session evidence before
    promoting AlphaEvolve-style collaborative discovery workflows.
  - Required result: add roadmap gates for `2605.05921`: paper/source
    manifest entry, PDF/cache hash, study metadata, participant/problem
    taxonomy, intentmaking and sensemaking event schema, UI/session artifact
    status, goal-revision and human-intervention boundaries, privacy/redaction
    policy, and a background-only or future-interactive-feature status rule so
    roadmap claims do not outpace local HCI workflow support.

- [ ] Add AlphaEvolve radar power-allocation application gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.01794`, submitted May 3, 2026, reports using
    AlphaEvolve Evolution to discover a closed-form radar power-allocation
    solution for multi-target tracking, with physically inspired state
    features, deterministic feasibility transformation, generalization across
    scenarios and target counts, 1.51% average relative performance loss, and
    more than three orders of magnitude speedup over iterative solvers.
  - Current evidence: ROADMAP tracks original AlphaEvolve alignment, local
    benchmark/report contracts, and source gates for several later
    application papers. It does not mention `2605.01794`, define a radar
    source-manifest gate, or require fixtures before promoting radar resource
    allocation as a supported LibreEvolve workflow.
  - Required result: add roadmap gates for `2605.01794`: paper/source manifest
    entry, PDF/cache hash, radar task/scenario/target taxonomy, state-feature
    schema, evolved scoring function, feasibility transform and constraints,
    iterative-solver baseline, tracking-accuracy and speedup metrics,
    generalization split evidence, code/artifact availability status, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local radar benchmark support.

- [ ] Add EvoX adaptive meta-evolution gates before roadmap promotion.
  - Spec evidence: arXiv `2602.23413`, submitted February 26, 2026 and last
    revised March 16, 2026, introduces EvoX as an adaptive evolution method
    that optimizes its own evolution process. The abstract positions
    AlphaEvolve and related systems as using prior evaluated solutions to
    guide candidate generation, says fixed search strategies with static
    explore/exploit knobs can fail to adapt, and reports EvoX outperforming
    AlphaEvolve, OpenEvolve, GEPA, and ShinkaEvolve on the majority of nearly
    200 real-world optimization tasks.
  - Current evidence: ROADMAP tracks fixed parent-selection, run manifests,
    migration/replay gaps, benchmark/report contracts, and later
    AlphaEvolve-related source gates. It does not mention `2602.23413`, define
    an adaptive-search source gate, or require local evidence before promoting
    strategy self-optimization beyond the current fixed mixed 30/70
    explore/exploit policy and explicit strategy switches.
  - Required result: add roadmap gates for `2602.23413`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, adaptive
    strategy representation, controller-state and strategy-provenance
    artifacts, task-suite and baseline-method taxonomy, metric definitions,
    ablation and token-efficiency reports, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    EvoX-style strategy evolution support.

- [ ] Add DeltaEvolve semantic-delta context gates before roadmap promotion.
  - Spec evidence: arXiv `2602.02919`, submitted February 2, 2026, introduces
    DeltaEvolve as a momentum-driven evolutionary framework. The abstract says
    AlphaEvolve relies on full-code histories that are context-inefficient and
    can dilute useful algorithmic ideas; DeltaEvolve instead stores structured
    semantic deltas describing how and why successive modifications affect
    performance, then organizes those deltas through a multi-level database
    and progressive disclosure to reduce input tokens.
  - Current evidence: ROADMAP tracks prompt/context construction, prompt
    history artifacts, failure memory, benchmark/report contracts, and several
    AlphaEvolve-adjacent paper gates. It does not mention `2602.02919`, define
    a semantic-delta source gate, or require evidence before promoting
    momentum-guided delta memory beyond current parent-program and SEARCH/
    REPLACE diff handling.
  - Required result: add roadmap gates for `2602.02919`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, semantic-delta
    record schema, node-transition and performance-effect provenance,
    multi-level memory/index artifacts, progressive-disclosure policy traces,
    token-accounting metrics, scientific-task benchmark taxonomy, baseline
    method identities, and a background-only or benchmark-fixture status rule
    so roadmap claims do not outpace local DeltaEvolve-style context support.

- [ ] Add MLEvolve long-horizon ML-engineering gates before roadmap promotion.
  - Spec evidence: arXiv `2606.06473`, submitted June 4, 2026, introduces
    MLEvolve as a self-evolving multi-agent framework for end-to-end machine
    learning algorithm discovery. The abstract identifies inter-branch
    information isolation, memoryless search, and lack of hierarchical control
    as long-horizon MLE blockers, then proposes Progressive MCGS,
    graph-based reference edges, entropy-inspired exploration-to-exploitation
    scheduling, Retrospective Memory, and adaptive coding modes. It reports
    MLE-Bench state-of-the-art results under a 12-hour budget and stronger
    mathematical algorithm optimization than AlphaEvolve.
  - Current evidence: ROADMAP tracks AlphaEvolve alignment, MAP-Elites/islands
    behavior, prompt/run provenance, benchmark-report contracts, and several
    paper-source gates. It does not mention `2606.06473`, define an MLE-Bench
    or Progressive MCGS source gate, or require local evidence before
    promoting long-horizon ML engineering beyond the current pure-Python
    problem/evaluator workflow.
  - Required result: add roadmap gates for `2606.06473`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    Progressive MCGS graph schema, cross-branch reference-edge provenance,
    entropy-schedule metrics, retrospective-memory artifacts, adaptive coding
    mode traces, MLE-Bench task/submission metadata, budget and metric
    definitions, AlphaEvolve comparison boundary, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    MLEvolve-style harness support.

- [ ] Add LEVI cost-aware search-architecture gates before roadmap promotion.
  - Spec evidence: arXiv `2605.09764`, submitted May 10, 2026, introduces
    LEVI as a harness-first evolutionary framework arguing that stronger
    search architectures can substitute for larger LLMs. The abstract says
    AlphaEvolve-style systems incur unnecessary cost when archives fail to
    preserve diversity, frontier models are used blindly for local edits, and
    full-set evaluation spends rollouts on redundant examples. LEVI adds a
    diversity-preserving solution database, smarter mutation routing between
    large and small LLMs, and rank-preserving proxy benchmarks, reporting
    3.3x-6.7x lower-budget systems results, one 35x lower-cost match, and
    prompt-optimization results at less than half GEPA's rollout budget.
  - Current evidence: ROADMAP tracks MAP-Elites/islands behavior, heuristic
    LLM ensemble selection, evaluator artifacts, benchmark-report contracts,
    and newer adaptive-search source gates. It does not mention
    `2605.09764`, define a LEVI cost/source gate, or require local cost and
    diversity evidence before promoting claims about cheaper-than-frontier
    AlphaEvolve-style search.
  - Required result: add roadmap gates for `2605.09764`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    diversity-preserving solution-database invariants, mutation-router schema,
    large/small model routing traces, proxy-benchmark calibration and
    rank-correlation reports, rollout-budget and provider-cost metrics,
    systems/prompt benchmark taxonomy, baseline identities, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local LEVI-style cost-aware search support.

- [ ] Add PACEvolve long-horizon consistency gates before roadmap promotion.
  - Spec evidence: arXiv `2601.10657`, submitted January 15, 2026 and last
    revised January 16, 2026, introduces Progress-Aware Consistent Evolution
    for long-horizon LLM evolutionary search. The abstract names three
    failure modes: context pollution, mode collapse from poor exploration/
    exploitation balance, and weak collaboration from rigid crossover. It
    addresses them with hierarchical context management plus pruning,
    momentum-based backtracking, and a self-adaptive sampling policy that
    unifies backtracking and crossover, reporting state-of-the-art results on
    LLM-SR and KernelBench and record-surpassing Modded NanoGPT solutions.
  - Current evidence: ROADMAP tracks prompt provenance, failure snippets,
    parent selection, MAP-Elites/islands, migration/replay gaps, and newer
    search-source gates. It does not mention `2601.10657`, define PACEvolve
    gates, or require local evidence before promoting robust long-horizon
    consistency, context-pollution control, backtracking, or coordinated
    crossover beyond current fixed-policy evolution.
  - Required result: add roadmap gates for `2601.10657`: paper/source
    manifest entry, PDF/cache hash, source-license metadata,
    context-pollution and mode-collapse metrics, hierarchical context and
    pruning artifacts, momentum-backtracking traces, adaptive sampling and
    crossover/backtracking coordination records, parallel-trajectory
    collaboration diagnostics, LLM-SR/KernelBench/Modded-NanoGPT benchmark
    metadata, baseline identities, and a background-only or benchmark-fixture
    status rule so roadmap claims do not outpace local PACEvolve-style support.

- [ ] Add FlashEvolve asynchronous-stage gates before roadmap promotion.
  - Spec evidence: arXiv `2605.08520`, submitted May 8, 2026, introduces
    FlashEvolve for asynchronous stage orchestration in LLM-based evolution.
    The abstract identifies synchronized stage execution and LLM-heavy stage
    imbalance as wall-clock bottlenecks, then proposes asynchronous workers
    and queues, artifact-version tracking, staleness-aware update/discard/
    patch policies, speculative stage completion, and adaptive workflow
    control. It reports 3.5x local-vLLM and 4.9x API proposal-throughput gains
    over synchronous GEPA and says the design also applies to ACE and
    Meta-Harness.
  - Current evidence: ROADMAP tracks async reviewer gaps, archive restore,
    prompt/run provenance, benchmark-report contracts, and several
    long-horizon search gates. It does not mention `2605.08520`, define an
    asynchronous-stage source gate, or require evidence before promoting
    overlapping generation/evaluation/admission, artifact-version repair, or
    throughput gains beyond the current synchronous evolution loop.
  - Required result: add roadmap gates for `2605.08520`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, worker/queue
    architecture, stage-overlap and queue-depth traces, artifact-version
    lineage, stale-artifact update/discard/patch policy records, reflective
    stale-patch artifacts, speculative-completion metrics, adaptive workflow
    control telemetry, throughput/token-efficiency reports, GEPA/vLLM/API
    baseline identities, ACE/Meta-Harness applicability boundaries, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local FlashEvolve-style async orchestration support.

- [ ] Add evolutionary-agent trace-diagnostics gates before roadmap promotion.
  - Spec evidence: arXiv `2605.20086`, submitted May 25, 2026, asks what
    evolutionary coding agents actually evolve. Its abstract says final
    benchmark scores alone cannot reveal whether gains reflect structural
    innovation, overfitting, cycling, or task-specific constant tuning. It
    introduces EvoTrace for edit-type, dependency, and fitness-trajectory
    annotation plus EvoReplay for interventions on search traces, and studies
    AlphaEvolve-style agents including AlphaEvolve, OpenEvolve, and FunSearch.
  - Current evidence: ROADMAP tracks run manifests, history streams, archive
    events, prompt history, benchmark-report contracts, and many source gates.
    It does not mention `2605.20086`, define trace-diagnostic gates, or
    require evidence before promoting LibreEvolve outputs as genuine
    algorithmic discoveries rather than constant tuning, benchmark overfit, or
    cycling artifacts.
  - Required result: add roadmap gates for `2605.20086`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, edit-type
    annotation schema, dependency-graph extraction, fitness-trajectory
    classifiers, cycling/overfitting diagnostics, structural-innovation
    labels, prompt and population ablation records, replay-intervention tool
    support, counterfactual outcome reports, task/baseline-agent taxonomy, and
    a background-only or benchmark-fixture status rule so roadmap claims about
    discovery quality do not outpace local EvoTrace/EvoReplay-style evidence.

- [ ] Add Zarankiewicz reinforced-search application gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.01120`, submitted May 1, 2026 and revised May
    7, 2026, reports new bounds for Zarankiewicz numbers from reinforced LLM
    evolutionary search. The abstract says OpenEvolve produced three exact
    Zarankiewicz values, lower bounds for 41 more values, and four matched
    closed cases, with generated algorithms, implementation details, and costs
    under `$30` per parameter combination.
  - Current evidence: ROADMAP tracks AlphaEvolve alignment, selected
    follow-on math/problem sources, benchmark/report contracts, and
    cost-aware search gates. It does not mention `2605.01120`, define a
    Zarankiewicz source gate, or require local graph-construction/verifier
    evidence before promoting extremal combinatorics discovery support.
  - Required result: add roadmap gates for `2605.01120`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, relation to
    AlphaEvolve/OpenEvolve, Zarankiewicz parameter taxonomy, bipartite graph
    construction schema, `K_{s,t}`-free verifier, exact/lower-bound table,
    generated construction algorithms, proof/check status, upper-bound
    references, cost accounting, reproducibility metadata, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local Zarankiewicz benchmark support.

- [ ] Add CORAL autonomous multi-agent evolution gates before roadmap
      promotion.
  - Spec evidence: arXiv `2604.01658`, submitted April 2, 2026 and last
    revised May 17, 2026, introduces CORAL for autonomous multi-agent
    evolution on open-ended discovery tasks. The abstract says fixed
    heuristics and hard-coded exploration rules limit current LLM-based
    evolution, then proposes long-running collaborative agents with shared
    persistent memory, asynchronous execution, heartbeat-based interventions,
    isolated workspaces, evaluator separation, resource management, and agent
    session/health management. It reports state-of-the-art results on 10
    tasks, 3-10x higher improvement rates with fewer evaluations, and an
    Anthropic kernel-engineering improvement from 1363 to 1103 cycles.
  - Current evidence: ROADMAP tracks MAP-Elites islands, ring migration,
    async reviewer gaps, archive restore, benchmark/report contracts, and
    many search-source gates. It does not mention `2604.01658`, define CORAL
    gates, or require evidence before promoting autonomous multi-agent
    collaboration beyond the current island/migration abstraction.
  - Required result: add roadmap gates for `2604.01658`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    agent-session and shared-memory schemas, async execution and communication
    traces, heartbeat intervention logs, isolated-workspace policy,
    evaluator-separation contract, resource-management telemetry, session
    health events, knowledge-reuse/mechanistic analyses, benchmark taxonomy,
    kernel-engineering metric records, baseline identities, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local CORAL-style autonomous multi-agent support.

- [ ] Add AEvo harnessed meta-editing gates before roadmap promotion.
  - Spec evidence: arXiv `2605.13821`, submitted May 13, 2026, introduces
    AEvo as a harnessed meta-editing framework for agentic evolution. The
    abstract says fixed procedures are rigid, general-purpose agents can drift
    in long-horizon evolution, and both accumulate useful evidence that lacks
    a stable interface for revising the mechanism that drives future
    evolution. AEvo turns accumulated candidates, feedback, traces, and
    failures into process-level state and lets a meta-agent edit the procedure
    or agent context controlling future evolution, reporting a 26 relative
    improvement over the strongest baseline and state-of-the-art performance
    on three open-ended optimization tasks.
  - Current evidence: ROADMAP tracks static config, parent selection, prompt
    construction, run artifacts, benchmark contracts, and many search-source
    gates. It does not mention `2605.13821`, define an AEvo gate, or require
    local evidence before promoting adaptive controller self-modification or
    meta-editing of the evolution process beyond fixed CLI/config choices.
  - Required result: add roadmap gates for `2605.13821`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, process-level
    state schema, accumulated evidence inventory, meta-agent observation and
    action contracts, procedure/context patch records, control-edit
    provenance, rollback/versioning policy, drift/stability diagnostics,
    iteration-budget accounting, benchmark taxonomy, baseline identities, and
    a background-only or benchmark-fixture status rule so roadmap claims do
    not outpace local AEvo-style harnessed meta-editing support.

- [ ] Add G-Zero verifier-free co-evolution gates before roadmap promotion.
  - Spec evidence: arXiv `2605.09959`, submitted May 11, 2026, introduces
    G-Zero for open-ended generation from zero data. The abstract says
    self-evolving LLMs struggle outside verifiable domains because proxy LLM
    judges can cap capabilities and invite reward hacking. G-Zero replaces
    external judges with verifier-free co-evolution: `Hint-delta` measures the
    predictive shift from self-generated hints, a Proposer uses GRPO to target
    Generator blind spots with queries and hints, and the Generator uses DPO
    to internalize improvements.
  - Current evidence: ROADMAP tracks evaluator contracts, validator
    subprocesses, benchmark-report artifacts, reward/scoring gaps, and many
    self-evolution source gates. It does not mention `2605.09959`, define a
    verifier-free source gate, or require local evidence before promoting
    open-ended self-evolution without explicit validators.
  - Required result: add roadmap gates for `2605.09959`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, Generator/
    Proposer role schema, Hint-delta reward records, unassisted and
    hint-conditioned response pairs, query/hint artifact storage, GRPO/DPO
    training traces, intrinsic-reward calibration, exploration coverage
    reports, pseudo-label noise filtering, reward-hacking diagnostics,
    open-ended task taxonomy, theoretical-assumption records, baseline
    identities, and a background-only or benchmark-fixture status rule so
    roadmap claims do not outpace local G-Zero-style verifier-free support.

- [ ] Add GenEvolve multimodal trajectory-distillation gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.21605`, submitted May 20, 2026 and last revised
    May 22, 2026, introduces GenEvolve for self-evolving image-generation
    agents. The abstract models each generation attempt as a tool-orchestrated
    trajectory that gathers evidence, selects references, invokes generation
    skills, and creates a prompt-reference program. It compares multiple
    trajectories for the same request, abstracts best-worst differences into
    structured visual experience for a privileged teacher, and distills dense
    token-level supervision into a student.
  - Current evidence: ROADMAP tracks text-program evolution, prompt/run
    artifacts, evaluator contracts, benchmark reports, and many
    self-evolution source gates. It does not mention `2605.21605`, define a
    multimodal trajectory-distillation gate, or require evidence before
    promoting image-generation agents, tool-orchestrated visual trajectories,
    or teacher/student experience distillation.
  - Required result: add roadmap gates for `2605.21605`: paper/source
    manifest entry, PDF/cache hash, source-license and project URL status,
    multimodal tool-trajectory schema, reference/evidence selection logs,
    prompt-reference program artifacts, best-worst comparison records,
    structured visual experience taxonomy, privileged teacher and student
    distillation traces, token-supervision metadata, image artifact lineage,
    GenEvolve-Data/GenEvolve-Bench metadata, baseline identities, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local GenEvolve-style multimodal support.

- [ ] Add EvoRubric self-evolving reward-rubric gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.29847`, submitted May 28, 2026, introduces
    EvoRubric for rubric-driven RL in open-ended generation. The abstract says
    static human rubrics cause policy lag and external dynamic rubric
    generators are expensive; EvoRubric instead alternates a single policy
    between Reasoner and Rubric Generator roles, validates criteria with a
    meta-verifier, zero-variance pruning, and Leave-One-Out peer consensus,
    archives validated criteria into memory, and produces dense
    multi-objective rewards.
  - Current evidence: ROADMAP tracks explicit evaluator contracts, scoring
    artifacts, benchmark reports, verifier-free self-evolution gates, and
    multiple open-ended search sources. It does not mention `2605.29847`,
    define a self-evolving rubric gate, or require local evidence before
    promoting dynamic open-ended reward criteria beyond user-provided
    validators and evaluator scores.
  - Required result: add roadmap gates for `2605.29847`: paper/source
    manifest entry, PDF/cache hash, source-license metadata,
    Reasoner/Rubric-Generator role schema, generated-rubric provenance,
    meta-verifier and peer-consensus records, zero-variance pruning outcomes,
    criteria memory-pool artifacts, dense reward-vector definitions,
    reward-hacking diagnostics, expert-prior initialization records,
    medical/writing/science benchmark metadata, baseline identities, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local EvoRubric-style reward-rubric support.

- [ ] Add LLM-ALSO adaptive learning-signal gates before roadmap promotion.
  - Spec evidence: arXiv `2605.29293`, submitted May 28, 2026, introduces
    LLM-ALSO for LLM-driven adaptive learning-signal optimization in
    sparse-reward cooperative multi-agent reinforcement learning. The abstract
    says it decomposes reward adaptation into iterative diagnosis, proposal,
    and validation: a Critic LLM diagnoses stage-specific learning and
    coordination failures from sparse-return metrics and compact behavior
    evidence, a Generator LLM proposes reward-shaping configurations, and
    branch-validation feedback refines candidates before they affect the main
    training trajectory.
  - Current evidence: ROADMAP tracks evaluator contracts, reward/scoring gaps,
    plugins, verifier-free self-evolution, reward-rubric gates, and benchmark
    reports. It does not mention `2605.29293`, define a sparse-reward MARL
    learning-signal gate, or require local evidence before promoting adaptive
    reward shaping beyond fixed problem validators and evaluator outputs.
  - Required result: add roadmap gates for `2605.29293`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, Critic/Generator
    role schema, sparse-return and compact-behavior evidence records,
    stage-specific diagnosis artifacts, reward-shaping configuration records,
    branch-validation traces, update-promotion criteria, main-training
    trajectory provenance, sparse-reward cooperative MARL benchmark metadata,
    learning-efficiency metrics, baseline identities, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    LLM-ALSO-style learning-signal support.

- [ ] Add MemEvolve meta-evolving memory-architecture gates before roadmap
      promotion.
  - Spec evidence: arXiv `2512.18746`, submitted December 21, 2025, introduces
    MemEvolve for meta-evolution of agent memory systems. The abstract says
    memory enables agents to store trajectories, distill experience, and
    synthesize reusable tools, but existing systems keep the memory
    architecture itself static. MemEvolve jointly evolves experiential
    knowledge and memory architecture, and EvolveLab defines a modular
    encode/store/retrieve/manage design space distilled from twelve memory
    systems, with up to 17.06% framework improvements and cross-task/cross-LLM
    generalization.
  - Current evidence: ROADMAP tracks run artifacts, prompt history, failed
    proposals, archive restore, source provenance, and several memory/context
    source gates. It does not mention `2512.18746`, define a meta-memory
    architecture gate, or require local evidence before promoting adaptive
    memory beyond fixed JSONL streams and prompt-context policies.
  - Required result: add roadmap gates for `2512.18746`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    encode/store/retrieve/manage component schema, memory-architecture
    genotype, experiential-knowledge records, joint content/architecture
    evolution traces, memory mutation/evaluation policy, static-memory
    baseline identities, EvolveLab benchmark metadata, cross-task/cross-LLM
    transfer reports, performance-delta records, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    MemEvolve-style memory support.

- [ ] Add ANCHOR healthy-evolution oversight gates before roadmap promotion.
  - Spec evidence: arXiv `2606.06114`, submitted June 4, 2026, introduces
    Agent Norm Correction through Human-like Oversight and Review (ANCHOR) in
    `Towards Healthy Evolution: Exploring the Role and Mechanisms of
    Human-Agent Interaction in Self-Evolving Systems`. The abstract says
    autonomous self-evolving agents can suffer capability degradation and
    safety drift, and that simulated human supervision at different phases of
    self-evolution can mitigate safety degradation while preserving core
    evolutionary-objective performance. It also reports that supervising the
    output verification phase is most effective and that increasing
    supervision frequency yields diminishing returns.
  - Current evidence: ROADMAP tracks evaluator contracts, failure artifacts,
    safety-adjacent reward gates, trace diagnostics, and several open-ended
    self-evolution source gates. It does not mention `2606.06114`, define an
    ANCHOR gate, require human-like oversight records, track phase-specific
    norm-correction feedback, measure safety drift during evolution, or
    require supervision-cadence evidence before promoting healthy-evolution or
    human-aligned self-evolution claims.
  - Required result: add roadmap gates for `2606.06114`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, ANCHOR oversight
    role schema, phase-specific supervision taxonomy, norm-correction
    feedback artifacts, output-verification intervention logs, safety-drift
    and capability-degradation metrics, objective-preservation reports,
    supervision-frequency/cadence experiment records, coding/math/safety
    benchmark metadata, baseline identities, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    ANCHOR-style human-like oversight support.

- [ ] Add SIA harness-plus-weight self-improvement gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.27276`, submitted May 26, 2026, introduces
    `SIA: Self Improving AI with Harness & Weight Updates`. The abstract says
    previous self-improvement work often separates harness/scaffold updates
    from model-weight updates, then proposes a Feedback-Agent that updates
    both the harness and weights of a task-specific agent. It evaluates
    Chinese legal charge classification, low-level GPU kernel optimization,
    and single-cell RNA denoising, and reports that combining both levers
    outperforms scaffold iteration alone on all three benchmarks.
  - Current evidence: ROADMAP tracks fixed backend adapters, evaluator
    contracts, prompt/run artifacts, ThetaEvolve-style GRPO export, AEvo
    meta-editing gates, and adaptive reward-source gates. It does not mention
    `2605.27276`, define SIA gates, require a Feedback-Agent decision log,
    expose editable harness components for task-specific agents, perform
    online model-weight updates, retain adapter/checkpoint provenance, or
    require ablations separating harness-only, weight-only, and combined
    improvement loops before promoting self-improving AI claims.
  - Required result: add roadmap gates for `2605.27276`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    Meta-Agent/Target-Agent/Feedback-Agent schemas, editable harness
    component inventory, harness patch/version records, weight-update trigger
    and training records, adapter/checkpoint lifecycle, training-data
    lineage, verifier/reward sufficiency checks, rollback/resume policy,
    harness-only versus weight-only versus combined ablation metadata,
    LawBench/kernel/scRNA benchmark records, compute/cost telemetry, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local SIA-style harness-plus-weight self-improvement support.

- [ ] Add HarnessFix trace-grounded harness repair gates before roadmap
      promotion.
  - Spec evidence: arXiv `2606.06324`, submitted June 4, 2026, introduces
    HarnessFix in `From Failed Trajectories to Reliable LLM Agents:
    Diagnosing and Repairing Harness Flaws`. The abstract frames harnesses as
    the substrate for execution environments, tool interfaces, context,
    lifecycle orchestration, observability, verification, and governance, then
    argues that final-outcome-only self-improvement can make broad or poorly
    scoped harness changes. HarnessFix normalizes failed trajectories and
    harness code into HTIR, attributes failures to responsible steps and
    harness layers, consolidates flaw records, maps them to scoped repair
    operators, and validates patches with regression constraints.
  - Current evidence: ROADMAP tracks failure/quarantine streams, prompt
    history, evaluator contracts, benchmark reports, AEvo meta-editing gates,
    and SIA harness-plus-weight gates. It does not mention `2606.06324`,
    define a trace-grounded harness repair gate, require HTIR-like trace
    normalization, attribute failures to harness layers, consolidate recurring
    flaw records, generate scoped harness repairs, or validate harness patches
    against target-flaw reduction and unacceptable-regression bounds before
    promoting agent reliability or harness self-repair claims.
  - Required result: add roadmap gates for `2606.06324`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, HTIR schema,
    raw-trace normalization, harness-code linkage, step-level provenance,
    harness-layer attribution taxonomy, recurring flaw records, repair
    operator definitions, harness patch/version artifacts, flaw-specific
    validation specs, regression-bound telemetry, held-out benchmark records,
    SWE-Bench/Terminal-Bench/GAIA/AppWorld metadata, baseline identities, and
    a background-only or benchmark-fixture status rule so roadmap claims do
    not outpace local HarnessFix-style trace-grounded harness repair support.

- [ ] Add RHO retrospective self-preference harness optimization gates before
      roadmap promotion.
  - Spec evidence: arXiv `2606.05922`, submitted June 4, 2026, introduces
    Retrospective Harness Optimization (RHO) in `Improving LLM Agents via
    Self-Preference over Trajectory Rollouts`. The abstract says RHO improves
    an agent harness without ground-truth validation labels by selecting a
    diverse coreset of challenging past-trajectory tasks, re-solving them in
    parallel, analyzing rollouts with self-validation and self-consistency,
    generating candidate harness updates, and selecting the most effective
    update through pairwise self-preference.
  - Current evidence: ROADMAP tracks run artifacts, failure/quarantine
    streams, evaluator contracts, benchmark reports, SIA gates, HarnessFix
    gates, and AEvo meta-editing gates. It does not mention `2606.05922`,
    define a retrospective label-free harness optimizer gate, require
    hard/diverse coreset selection from past trajectories, support parallel
    re-rollout batches for harness comparison, record self-validation or
    self-consistency analyses, rank candidate harness updates by pairwise
    self-preference, or require long-horizon behavior-pattern evidence before
    promoting self-supervised harness optimization claims.
  - Required result: add roadmap gates for `2606.05922`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, past-trajectory
    corpus schema, coreset difficulty/diversity criteria, retrospective
    rollout batch records, parallel re-solve provenance, self-validation and
    self-consistency evidence, candidate harness-update artifacts, pairwise
    self-preference ranking, label-free selection policy, deployment/
    rollback metadata, long-horizon behavior-pattern reports, SWE-Bench Pro
    benchmark records, baseline identities, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    RHO-style retrospective harness optimization support.

- [ ] Add harness-updating versus harness-benefit gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.30621`, submitted May 28, 2026, introduces
    `Harness Updating Is Not Harness Benefit: Disentangling Evolution
    Capabilities in Self-Evolving LLM Agents`. The abstract distinguishes
    generating useful persistent harness updates from actually benefiting
    from those updates during task solving. It reports flat harness-updating
    across base capability tiers, non-monotonic harness-benefit with mid-tier
    agents benefiting most, and weak-agent failure modes around harness
    artifact activation and faithful long-horizon following.
  - Current evidence: ROADMAP tracks backend capability, prompt context,
    failure artifacts, SIA, HarnessFix, RHO, and AEvo gates. It does not
    mention `2605.30621`, define separate harness-updating and harness-benefit
    readiness gates, require artifact activation metrics, measure adherence
    to updated harness instructions over long trajectories, compare model
    tiers for evolver versus task-solving roles, or require capability-budget
    evidence before promoting harness self-evolution gains.
  - Required result: add roadmap gates for `2605.30621`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    harness-updating metric schema, harness-benefit metric schema,
    evolver/task-agent pairing matrix, persistent harness update records,
    harness artifact activation/load telemetry, adherence/following traces,
    long-horizon instruction-following reports, model-tier taxonomy,
    weak/mid/strong baseline identities, capability-budget accounting,
    benchmark records for SWE-Bench Verified, MCP-Atlas, and SkillsBench if
    reproduced, and a background-only or benchmark-fixture status rule so
    roadmap claims do not conflate harness update generation with downstream
    harness benefit.

- [ ] Add AHE observability-driven harness evolution gates before roadmap
      promotion.
  - Spec evidence: arXiv `2604.25850`, submitted April 28, 2026, introduces
    `Agentic Harness Engineering: Observability-Driven Automatic Evolution of
    Coding-Agent Harnesses`. The abstract describes a closed loop with
    component observability, experience observability, and decision
    observability: editable harness components are file-level and revertible,
    raw trajectories are distilled into layered evidence, and each edit is
    paired with a prediction verified against later task outcomes.
  - Current evidence: ROADMAP tracks prompt/context surfaces, run artifacts,
    failures, SIA, HarnessFix, RHO, and harness-benefit gates. It does not
    mention `2604.25850`, define AHE readiness gates, require file-level
    harness component inventories, create layered trajectory evidence corpora,
    record edit predictions, verify edit predictions against next-round
    outcomes, attribute gains by component class, or require frozen-harness
    transfer reports before promoting autonomous harness evolution claims.
  - Required result: add roadmap gates for `2604.25850`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    editable component taxonomy, file-level harness component manifests,
    revertible edit records, experience-evidence distillation schema,
    drill-down trajectory corpus links, decision-observability records,
    edit-prediction and outcome-verification telemetry, falsifiable contract
    status, iteration traces, tool/middleware/memory attribution reports,
    frozen-harness transfer benchmark records, Terminal-Bench 2 and
    SWE-bench Verified metadata, baseline identities, token/cost accounting,
    and a background-only or benchmark-fixture status rule so roadmap claims
    do not outpace local AHE-style observability-driven harness evolution.

- [ ] Add AI Harness Engineering runtime-substrate gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.13357`, submitted May 13, 2026, introduces
    `AI Harness Engineering: A Runtime Substrate for Foundation-Model Software
    Agents`. The abstract reframes software-engineering capability as emerging
    from a model-harness-environment system and names eleven harness
    responsibilities: task specification, context selection, tool access,
    project memory, task state, observability, failure attribution,
    verification, permissions, entropy auditing, and intervention recording.
    It proposes an H0-H3 ladder and an auditable episode-package protocol.
  - Current evidence: ROADMAP tracks run artifacts, prompt/context, evaluator
    evidence, failure streams, AHE, HarnessFix, RHO, and harness-benefit
    gates. It does not mention `2605.13357`, define a general runtime-
    substrate gate, require all eleven harness responsibilities, distinguish
    H0-H3 maturity levels, require episode packages, audit maintenance
    entropy, log human interventions, or tie task completion to structured
    requirement-level verification evidence.
  - Required result: add roadmap gates for `2605.13357`: paper/source
    manifest entry, PDF/cache hash, source-license metadata,
    model-harness-environment schema, eleven responsibility records, H0-H3
    harness-level taxonomy, runtime-resource exposure matrix, task/context/
    tool/memory/state records, observability traces, failure-attribution logs,
    verification protocol/report artifacts, permission-boundary events,
    entropy audits, intervention logs, episode-package records, deterministic
    requirement-check evidence, maintenance-burden reports, controlled
    validation metadata, and a background-only or benchmark-fixture status
    rule so roadmap claims do not outpace local AI-harness runtime-substrate
    support.

- [ ] Add inference-time trajectory-alignment harness gates before roadmap
      promotion.
  - Spec evidence: arXiv `2605.21516`, submitted May 15, 2026, introduces
    `Harnesses for Inference-Time Alignment over Execution Trajectories`. The
    abstract says more decomposition or guidance can improve execution but can
    also reduce final task success. It separates harness design into task
    decomposition and guided execution, analyzes workflow granularity, retry
    budgets, and guidance-induced action reweighting, and identifies
    over-decomposition, over-pruning, hallucinated execution, and partial
    harnessing tradeoffs.
  - Current evidence: ROADMAP tracks prompt/context surfaces, evaluator
    retries/budgets, run artifacts, and several harness evolution gates. It
    does not mention `2605.21516`, define decomposition/guidance parameter
    gates, require pass-rate plus final-bias reporting, measure retry-budget
    sensitivity, identify over-structured workflow failure modes, compare
    partial versus fully structured harnesses, or require alignment evidence
    before promoting increasingly structured harness workflows.
  - Required result: add roadmap gates for `2605.21516`: paper/source
    manifest entry, PDF/cache hash, source-license metadata, harness
    parameter schema, decomposition-granularity records, guidance-strength and
    guidance-rule records, sub-goal sequence artifacts, trajectory/action
    distribution records, retry-budget sensitivity reports, pass-rate and
    final-bias metrics, granularity-capability alignment reports,
    guidance-evidence alignment reports, over-decomposition/over-pruning/
    hallucinated-execution diagnostics, partial-harness benchmark records,
    Terminal-Bench-2 and synthetic task metadata, baseline identities, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    treat more harness structure as automatically better.

- [ ] Add Adaptive Auto-Harness open-ended task-stream gates before roadmap
      promotion.
  - Spec evidence: arXiv `2606.01770`, submitted June 1, 2026, introduces
    `Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System
    Deployment on Open-Ended Task Streams`. The abstract says fixed offline
    benchmarks miss deployment conditions where histories grow, tasks are
    heterogeneous, and distributions shift. It warns that a single densely
    updated harness can become brittle, decomposes the oracle-harness gap into
    evolution loss and adaptation loss, and uses a stateful multi-agent
    evolver, harness tree, solve-time routing, and human-steering hooks for
    task-wise adaptation.
  - Current evidence: ROADMAP tracks fixed problem runs, archives, prompt
    history, evaluator contracts, islands, and several harness-evolution
    source gates. It does not mention `2606.01770`, define open-ended
    task-stream deployment gates, require history-growth or distribution-
    shift evidence, separate evolution loss from adaptation loss, support a
    harness tree, route tasks to harness variants at solve time, or record
    human steering when historical evidence is insufficient.
  - Required result: add roadmap gates for `2606.01770`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    open-ended task-stream schema, history-growth records, task-heterogeneity
    and distribution-shift telemetry, oracle-harness definition, evolution-
    loss/adaptation-loss metrics, stateful multi-agent evolver schemas,
    cross-cycle memory, harness tree records, solve-time routing telemetry,
    human-steering hook records, targeted-steering outcomes, sustained-
    performance and degradation curves, prediction-market/security-
    competition/event-forecasting benchmark records, baseline/ablation
    identities, and a background-only or benchmark-fixture status rule so
    roadmap claims do not outpace local Adaptive Auto-Harness-style sustained
    deployment support.

- [ ] Add Meta-Harness outer-loop harness-code search gates before roadmap
      promotion.
  - Spec evidence: arXiv `2603.28052`, submitted March 30, 2026, introduces
    `Meta-Harness: End-to-End Optimization of Model Harnesses`. The abstract
    frames harness code as the mechanism controlling what information an LLM
    system stores, retrieves, and presents, then searches over that harness
    code with an agentic proposer that inspects prior source code, scores, and
    execution traces through a filesystem.
  - Current evidence: ROADMAP tracks candidate program evolution, prompt
    context, run artifacts, AHE, AI Harness Engineering, Adaptive
    Auto-Harness, RHO, HarnessFix, and SIA gates. It does not mention
    `2603.28052` as a first-class roadmap gate, define harness-code candidate
    schemas, expose prior harness candidates through a filesystem corpus,
    record agentic proposer decisions, measure context-token efficiency,
    evaluate held-out model transfer, or compare discovered harnesses against
    hand-engineered TerminalBench-2 baselines.
  - Required result: add roadmap gates for `2603.28052`: paper/source
    manifest entry, PDF/cache hash, source-license and linked-code status,
    harness-code candidate schema, agentic proposer role records, filesystem
    source/score/trace corpus layout, prior-candidate retrieval policy,
    harness mutation/evaluation records, information storage/retrieval/
    presentation artifacts, context-token budget and efficiency telemetry,
    held-out model transfer reports, online text-classification/RAG-math/
    TerminalBench-2 benchmark records, hand-engineered baseline identities,
    and a background-only or benchmark-fixture status rule so roadmap claims
    do not outpace local Meta-Harness-style end-to-end harness optimization.

- [ ] Add AlphaEvolve MARL algorithm-discovery gates before roadmap
      promotion.
  - Spec evidence: arXiv `2602.16928`, submitted February 18, 2026 and last
    revised May 7, 2026, introduces `Discovering Multiagent Learning
    Algorithms with Large Language Models`. The abstract says AlphaEvolve is
    deployed over CFR and PSRO design spaces, producing VAD-CFR and SHOR-PSRO,
    evaluating them on an 18-game suite across Poker, Goofspiel, Liar's Dice,
    Blotto, and Battleship variants, and distilling them through systematic
    ablations into WOP-CFR and PM-PSRO minimal solvers with improved
    generalization and reduced complexity. The paper uses OpenSpiel, exact
    exploitability by full game-tree traversal, deterministic metrics, and
    separate CFR/PSRO Python class skeletons as the AlphaEvolve search space.
  - Current evidence: ROADMAP tracks AlphaEvolve alignment, local evaluator
    stages, systems benchmarks, mathematical benchmark gaps, and selected
    application-source gates. It does not promote `2602.16928` beyond the
    background-only paper-index row, define CFR or PSRO candidate schemas,
    require an imperfect-information game evaluator, preserve train/evaluation
    game splits, track VAD-CFR or SHOR-PSRO mechanism provenance, require
    mechanism-coupling ablations, or define distilled-solver handoff and
    generalization gates for WOP-CFR and PM-PSRO. It also lacks roadmap gates
    for exact-oracle PSRO, IQM log-improvement audit scores, random constant-
    sum normal-form validation, exact-exploitability scale limits, single-
    trajectory caveats, and tabular-baseline comparison scope.
  - Required result: add roadmap gates for `2602.16928`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    CFR and PSRO candidate schemas, game-suite taxonomy, train/evaluation
    split hashes, evaluator protocol and metric definitions, exact
    exploitability and exact best-response oracle records, random-seed and
    budget records, baseline solver identities, VAD-CFR and SHOR-PSRO result
    tables, mechanism-coupling IQM ablation records, structural-complexity
    metrics, distilled WOP-CFR/PM-PSRO solver records, random normal-form
    validation rows, limitation/caveat records for scale, LLM trajectory, and
    baseline scope, generalization reports, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    AlphaEvolve-style MARL algorithm-discovery support.

- [ ] Add AlphaEvolve Ramsey-number discovery gates before roadmap promotion.
  - Spec evidence: arXiv `2603.09172`, submitted March 10, 2026 and last
    revised April 21, 2026, introduces `Reinforced Generation of
    Combinatorial Structures: Ramsey Numbers`. The abstract says AlphaEvolve
    improved lower bounds for nine Ramsey numbers, recovered all exact known
    lower bounds, matched many other best-known lower bounds, and served as a
    single meta-algorithm yielding search algorithms across those cases. The
    paper body defines the roadmap target as constructive lower-bound
    witnesses: an `n`-vertex graph free of `r`-cliques and `s`-independent
    sets proves `R(r,s) >= n+1`; Algorithm 1 evolves programs from an empty
    baseline that emit `G1` and prospect `G2`, scoring size and low violations
    against an expected random-graph baseline; Table 1 covers 28 colored
    cells; Table 2 groups initialization families; and the PDF links public
    Google Research construction and search-code artifacts.
  - Current evidence: ROADMAP tracks AlphaEvolve Appendix B constructive-math
    gaps, broad benchmark-fixture gaps, graph/certification ideas, and the
    paper-index background rows. It does not promote `2603.09172` beyond
    potential-future-benchmark status, define Ramsey graph witness schemas,
    require `R(s,t)` lower-bound verifier artifacts, store exact-bound
    recovery records, compare matched best-known bounds, or require a result
    table that attributes the nine prior/current lower-bound improvements. It
    also lacks roadmap gates for off-by-one lower-bound normalization,
    Algorithm 1-compatible primary/prospect scoring, public-artifact ingestion
    or citation status, Table 1/Table 2 coverage checks, appendix-algorithm
    provenance for Algorithms 2-34, and baseline caveats distinguishing public
    computational references, graph-only evidence, and personal
    communications.
  - Required result: add roadmap gates for `2603.09172`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    Ramsey candidate representation, graph/witness artifact schema,
    verifier/certifier entrypoints, parameterized `R(s,t)` result rows,
    exact-bound recovery suite, best-known-bound comparison table,
    prior/current value provenance, search-algorithm provenance, seed/budget
    records, witness graph hashes, independent checker outputs, failure and
    negative-result records, and a background-only or benchmark-fixture status
    rule so roadmap claims do not outpace local AlphaEvolve-style Ramsey
    discovery support. Roadmap promotion should additionally require exact
    `R(r,s) >= n+1` witness semantics, primary/prospect graph run artifacts,
    expected-violation formula inputs, imported or reproducibly regenerated
    Google Research construction/code artifacts, 28-cell Table 1 and
    34-algorithm appendix traceability, initialization-family coverage, and
    comparison rows for Radziszowski 2024, Exoo/Tatarevic 2015, Exoo 2006,
    Tatarevic 2020, Exoo 2012, Harborth/Krause 2003, plus explicit
    graph-only/personal-communication limitations.

- [ ] Add AlphaEvolve local-correction combinatorics gates before roadmap
      promotion.
  - Spec evidence: arXiv `2603.06692`, submitted March 4, 2026, introduces
    `Evolving Local Corrections for Global Constructions in Combinatorics`.
    The abstract uses AlphaEvolve to propose and refine finite correcting-step
    certificates for graph reconstruction, Latin-square Alon-Tarsi parity via
    local trades and sign-reversing involutions, and Rota's Basis Conjecture
    through local exchange policies. It reports experimental setups, scoring
    protocols, and outcomes that suggest conjectures, not completed proofs.
    The body defines fixed mathematical harnesses, short Python evolvable
    blocks, random symmetry-scramble robust scoring, hard constraints plus soft
    progress, hard-negative replay, and appendix evolved-code/Gemini-summary
    artifacts across the three case studies.
  - Current evidence: ROADMAP tracks broad constructive-math and benchmark
    fixture gaps plus selected source-specific result papers. It does not
    promote `2603.06692` beyond potential-future-benchmark status, define a
    local-correction certificate abstraction, require finite correcting-step
    traces, provide graph reconstruction, Latin-square trade, or Rota
    basis-exchange fixtures, preserve scoring protocols, or distinguish
    AlphaEvolve-suggested conjectures from verified/proved mathematical
    results. It also lacks promotion gates for the paper's exact result
    surfaces: bipartite `1420/1420` and planar `896/896` reconstruction
    ledgers, Alon-Tarsi validity/involution/sign-flip/locality/isotopy tables,
    Rota rank-5/rank-7/variable-rank `F2` circuit-rich pool benchmarks,
    appendix evolved-code traceability, AI-summary provenance, and explicit
    evaluator-hardening records for WL-surrogate-to-exact-isomorphism
    transitions.
  - Required result: add roadmap gates for `2603.06692`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    local-correction candidate schema, finite-step trace artifacts,
    graph-reconstruction benchmark records, vertex-deleted subgraph schemas,
    Latin-square local-trade and sign-reversing-involution records, Rota
    basis-family and local-exchange-policy records, scoring protocols,
    seed/budget records, generated-algorithm artifacts, structural-pattern
    summaries, conjecture/proof-status fields, independent checker hooks, and
    a background-only or benchmark-fixture status rule so roadmap claims do
    not outpace local AlphaEvolve-style local-correction combinatorics
    support. Roadmap promotion should additionally require Conjectures 4-11
    and Tables 1-6 to map to local benchmark schemas; exact graph deck
    equality, Latin-square involution/sign, and Rota circuit-oracle validators;
    result rows for experiment IDs `0_9751`, `0_9774`, and `0_7176`; majority
    rollout and symmetry-scramble robustness reports; appendix-code artifact
    hashes; and documentation gates that keep AI-generated summaries and
    experimental conjectures separate from proof-grade claims.

- [ ] Add AlphaEvolve bilateral-trade mechanism-design gates before roadmap
      promotion.
  - Spec evidence: arXiv `2603.08679`, submitted March 9, 2026, introduces
    `A New Lower Bound for the Random Offerer Mechanism in Bilateral Trade
    using AI-Guided Evolutionary Search`. The abstract uses AlphaEvolve to
    search value distributions for a worst-case Random-Offerer instance and
    reports `GFT_FB / GFT_RO >= 2.0749`, widening the known gap between
    first-best efficiency and Random-Offerer gains from trade. The body
    specifies the roadmap target as a discrete bilateral-trade witness:
    independent seller and buyer distributions, first-best `E[(b-s)+]`, RO as
    equal randomization between optimal seller-offering and buyer-offering
    prices, fixed Discrete Equal Revenue buyer, evolved seller CDF over
    `H=20000`, `1e-15` rounded integer arithmetic, exact GFT computation, and
    a modulated-power-law seller distribution yielding the reported component
    values and ratio.
  - Current evidence: ROADMAP tracks broad benchmark gaps, constructive-math
    result gaps, systems fixtures, and background paper-index rows. It does
    not promote `2603.08679` beyond background-only status, define a
    bilateral-trade distribution benchmark, compute first-best versus
    Random-Offerer GFT, preserve BIC/BB assumptions, compare prior
    counterexample baselines, or verify lower-bound witness distributions. It
    also lacks gates for fixed-buyer/evolved-seller search, equal-revenue buyer
    survival-function fixtures, CDF/SF/PMF rounding validation, SO/BO
    optimal-price records, appendix evaluator traceability, and the
    rounded-versus-unrounded result caveat.
  - Required result: add roadmap gates for `2603.08679`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    value-distribution candidate schema, buyer/seller support and probability
    constraints, FB and RO GFT evaluator records, BIC/BB assumption metadata,
    ratio objective and tolerance policy, witness distribution artifacts,
    prior lower-bound/counterexample baselines, seed/budget records,
    independent checker outputs, and a background-only or benchmark-fixture
    status rule so roadmap claims do not outpace local AlphaEvolve-style
    bilateral-trade lower-bound support. Roadmap promotion should additionally
    require the `H=20000` discrete evaluator, Discrete Equal Revenue buyer,
    evolved seller CDF formula and code artifact, exact FB/SO/BO/RO component
    rows, reserve-price witness logs, `1e-15` rounding policy, appendix
    evaluator hash, comparison to the `2` conjecture and Babaioff et al.
    `~2.02` baseline, source-scoped handling of the not-detailed `2.08`
    alternating-search result, and documentation that the verified claim is
    for the rounded distribution while the exact unrounded-mixture ratio is
    open.

- [ ] Add AlphaEvolve Magellan compiler-optimization gates before roadmap
      promotion.
  - Spec evidence: arXiv `2601.21096`, submitted January 28, 2026 and
    accepted to `C4ML@CGO'26`, introduces `Magellan: Autonomous Discovery of
    Novel Compiler Optimization Heuristics with AlphaEvolve`. The abstract
    says Magellan synthesizes executable C++ decision logic for compiler
    passes, couples an LLM coding agent with evolutionary search and
    autotuning, evaluates candidates on user-provided macro-benchmarks, and
    reports LLVM function-inlining, register-allocation, and preliminary XLA
    results. The design section specifies policy proposal, local evaluation,
    hyperparameter tuning, and feedback incorporation around compiler rebuilds
    and end-to-end macro-benchmark rewards.
  - Current evidence: ROADMAP tracks AlphaEvolve systems fixtures,
    FlashAttention/XLA IR provenance, and broad background paper-index rows,
    but it does not promote `2601.21096` beyond background-only status. It
    does not define a compiler-heuristic candidate schema, compiler pass
    runner, macro-benchmark dataset contract, LLVM inlining benchmark,
    register-allocation benchmark, XLA portability benchmark, autotuning loop
    report, expert-baseline comparison, or production-style metric report for
    binary size and end-to-end performance. It also lacks roadmap gates for
    feature-based versus full-API inlining search modes, EVOLVE-BLOCK compiler
    source insertion, compiler-flag hyperparameters, temporal/domain
    generalization, generated-policy maintainability, XLA e-graph extraction,
    auto-sharding contest-split evaluation, and explicit caveats for
    preliminary or not-yet-integrated XLA pipeline results.
  - Required result: add roadmap gates for `2601.21096`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    executable C++ decision-logic candidate schema, compiler-pass integration
    records, EVOLVE-BLOCK compiler-source provenance, compiler-flag
    hyperparameter schema, LLVM function-inlining benchmark with partial/full
    heuristic modes, register-allocation priority-rule benchmark, XLA graph-
    extraction and auto-sharding benchmarks, macro-benchmark provenance,
    binary-size and performance metric definitions, autotuning loop records
    including tuner identity, batch/round counts, and invalid-sample metrics,
    expert/neural baseline identities, temporal/domain generalization reports,
    generated-code maintainability caveats, seed/budget records, compiler
    environment hashes, independent checker outputs, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    AlphaEvolve-style Magellan compiler-optimization support.

- [ ] Add AlphaEvolve ArchAgent computer-architecture gates before roadmap
      promotion.
  - Spec evidence: arXiv `2602.22425`, submitted February 25, 2026,
    introduces `ArchAgent: Agentic AI-driven Computer Architecture Discovery`.
    The abstract says ArchAgent is built on AlphaEvolve to design and
    implement cache replacement policies, not merely tune parameters, and
    reports IPC speedup results on public multi-core Google Workload Traces
    and single-core SPEC06, post-silicon hyperspecialization gains, faster
    policy development than prior human SoTA, and simulator-escape behavior.
    The paper evaluates generated C++ policies in ChampSim under CRC-style
    single/multi-core cache configurations, short evolution simulations, and
    longer validation simulations.
  - Current evidence: ROADMAP tracks broad systems fixtures and background
    paper-index rows, but it does not promote `2602.22425` beyond background-
    only status. It does not define an architecture-design simulator gate,
    cache-policy candidate schema, ChampSim-style simulator integration,
    Google Workload Trace or SPEC06 benchmark provenance, IPC speedup metric,
    SoTA cache-policy baseline ledger, post-silicon specialization report, or
    simulator-escape detection/containment policy. It also lacks gates for the
    `48 KB` replacement-policy state limit, prefetch/no-prefetch tracks,
    evolution-versus-validation instruction counts, Policy31/61/62 mechanism
    reports, ablation studies, distributed-simulation failure handling, and
    optimized-away-assertion/write-bypass escape tests.
  - Required result: add roadmap gates for `2602.22425`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    cache replacement policy candidate schema, simulator integration records,
    ChampSim/CRC hardware configuration records, workload trace provenance,
    single-core and multi-core benchmark splits, prefetch/no-prefetch tracks,
    evolution and validation instruction-count protocols, IPC speedup metric
    definitions, prior-SoTA baseline identities including LRU, SHiP, Hawkeye,
    and Mockingjay where applicable, generated policy artifacts and mechanism
    labels, state-budget and hardware-realizability checks, ablation reports,
    post-silicon parameter-specialization records, simulator-escape evidence
    and quarantine rules, distributed-simulation failure records, seed/budget
    records, independent checker outputs, and a background-only or benchmark-
    fixture status rule so roadmap claims do not outpace local
    AlphaEvolve-style ArchAgent computer-architecture support.

- [ ] Add AlphaEvolve Fault2Flow workflow-automation gates before roadmap
      promotion.
  - Spec evidence: arXiv `2511.12916`, submitted November 17, 2025,
    introduces `Fault2Flow: An AlphaEvolve-Optimized Human-in-the-Loop
    Multi-Agent System for Fault-to-Workflow Automation`. The abstract says
    Fault2Flow extracts regulatory logic into PASTA-formatted fault trees,
    integrates expert verification, optimizes reasoning logic with an
    AlphaEvolve module, synthesizes n8n-executable workflows, and validates on
    transformer fault-diagnosis datasets with `100%` topological consistency
    and high semantic fidelity. The body specifies a frontend/backend
    architecture with Vue3/Element Plus/pdfjs/xlsx/ECharts, MinerU PDF
    extraction, MySQL/Milvus storage, LLM agents for PlantUML mind maps and
    PASTA fault trees, OpenEvolve-linked AlphaEvolve multi-island optimization,
    n8n workflow construction/activation, synthesized workflow verification
    tests, and a `DL/T 722-2014` transformer DGA case study over 16
    expert-designed cases.
  - Current evidence: ROADMAP tracks general plugins, systems benchmarks, and
    background paper-index rows, but it does not promote `2511.12916` beyond
    background-only status. It does not define a regulatory-text ingestion
    gate, PASTA fault-tree schema, expert-verification workflow, reasoning-
    logic optimization record, n8n workflow emitter, transformer fault-
    diagnosis dataset contract, topological-consistency metric, semantic-
    fidelity metric, or operational workflow artifact policy. It also lacks
    promotion gates for PlantUML intermediates, PASTA self-checks, n8n API
    activation evidence, synthesized test-case verification loops, GPT-5 judge
    usage, Table 1 model/baseline comparisons, average-token records, and
    placeholder ACM metadata caveats.
  - Required result: add roadmap gates for `2511.12916`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    regulatory-source provenance, PASTA fault-tree candidate schema,
    human-in-the-loop expert-review state records, reasoning-logic
    optimization candidate records, n8n workflow artifact schema, transformer
    fault-diagnosis dataset provenance, topological-consistency and semantic-
    fidelity metric definitions, seed/budget records, independent checker
    outputs, and a background-only or benchmark-fixture status rule so
    roadmap claims do not outpace local AlphaEvolve-style Fault2Flow
    automation support. Roadmap promotion should additionally require the
    three-stage document-understanding/knowledge-structuring/workflow-
    synthesis architecture, MinerU/MySQL/Milvus provenance, PlantUML and PASTA
    artifact hashes, OpenEvolve/AlphaEvolve optimization traces, n8n activation
    logs, synthesized verification samples and failure-refinement loops,
    DL/T 722-2014 dataset rows, Table 1 `16/0` Fault2Flow success and baseline
    failure rows, GPT-5 evaluator caveats, human-annotation/data-ethics
    records, and explicit documentation that Fault2Flow is not a supported
    LibreEvolve workflow until those local artifacts exist.

- [ ] Add TTT-Discover test-time-training gates before roadmap promotion.
  - Spec evidence: arXiv `2601.16175`, submitted January 22, 2026 and last
    revised February 5, 2026, introduces `Learning to Discover at Test Time`.
    The abstract contrasts AlphaEvolve's frozen-LLM prompting search with
    reinforcement learning at test time, where the model continues training
    on experience specific to the test problem. It reports continuous-reward
    discovery results across math, GPU kernels, algorithm design, and biology,
    including Erdos minimum overlap, autocorrelation, GPUMode, AtCoder, and
    single-cell denoising tasks, using open model `OpenAI gpt-oss-120b`,
    public code, Tinker runs, expert or organizer review, and low per-problem
    costs. The body specifies a mutable-policy loop with Algorithm 1,
    adaptive entropic objective, PUCT reuse, `50` training steps, `512`
    rollouts per step, LoRA rank `32`, Tinker `32768`-token context window,
    fixed Table 9 hyperparameters, and result tables for math, GPUMode
    kernels, AtCoder, denoising, ablations, and MLA Triton-filtered variants.
  - Current evidence: ROADMAP tracks AlphaEvolve frozen-search gaps, provider
    routing, feedback graders, budget accounting, and broad background paper
    rows, but it does not promote `2601.16175` beyond background-only status.
    It does not define a mutable model-policy state gate, test-time RL loop,
    Tinker/API training-run provenance, open-model checkpoint record,
    continuous-reward cross-domain benchmark suite, expert/organizer review
    artifact rule, or cost-per-problem accounting boundary. It also lacks
    promotion gates for public code/result URLs, LoRA/checkpoint lineage,
    adaptive-beta and PUCT traceability, OpenEvolve context-window truncation
    caveats, Modal/GPUMode/AtCoder/OpenProblems harness provenance, official
    submission IDs, Table 2-10 result rows, and the paper's sampling-budget
    inconsistency.
  - Required result: add roadmap gates for `2601.16175`: paper/source
    manifest entry, PDF/cache hash, source-license and public-code status,
    mutable policy/training-state schema, RL objective and rollout-selection
    metadata, training API and checkpoint provenance, open-model identity,
    continuous-reward task definitions, Erdos/autocorrelation/GPUMode/AtCoder/
    single-cell benchmark records, prior-art and AlphaEvolve/OpenEvolve
    baseline identities, expert/organizer review artifacts, seed/run records,
    cost and budget accounting, independent checker outputs, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local TTT-Discover-style test-time-training support. Roadmap
    promotion should additionally require Algorithm 1 event logs, per-step
    rollout batches, mutable checkpoint and LoRA artifact policies, adaptive-
    beta KL and PUCT archive records, benchmark resource-limit contracts,
    public result-link verification, table-level result reproduction, official
    leaderboard/submission artifacts, expert-review attestations, and explicit
    documentation that TTT-Discover is not supported by LibreEvolve until
    weight-updating test-time-training artifacts exist locally.

- [ ] Add AlphaEvolve Bruhat-interval hypercube gates before roadmap
      promotion.
  - Spec evidence: arXiv `2601.01235`, submitted January 3, 2026, introduces
    `Bruhat intervals that are large hypercubes`. The abstract says
    AlphaEvolve-suggested permutations led to a pattern that worked for tested
    `n` and was then proved for general `n`; for powers of `2`, it exhibits
    `S_n` Bruhat intervals that are hypercubes of dimension `O(n log n)`,
    characterizes vertices as dyadically well-distributed permutations, and
    connects maximal Bruhat-hypercube dimension to Kazhdan-Lusztig
    `R`-polynomial coefficients, frozen variables in open Richardson cluster
    algebras, and embeddings of Bruhat graphs. The body proves this through
    dyadic basic intervals, bit-reversal endpoints `x_m` and `y_m`, Ehresmann
    Bruhat-order matrices, complementary blocks and flips, a poset isomorphism
    `phi: D_m -> S_2^{C_m}`, and Theorem 2.21's `D_m = [x_m, y_m]` rank
    `m * 2^(m-1)` hypercube.
  - Current evidence: ROADMAP tracks broad constructive-math and Appendix B
    fixture gaps plus background paper-index rows, but it does not promote
    `2601.01235` beyond potential-future-benchmark status. It does not define
    permutation candidate schemas, Bruhat order/interval verifiers, poset-
    hypercube isomorphism checks, dyadic well-distribution predicates, power-
    of-two `S_n` benchmark rows, Kazhdan-Lusztig coefficient linkage, cluster-
    algebra consequence records, or finite-pattern versus proof-status gates.
    It also lacks gates for the Section 4 search protocol: FunSearch
    deterministic program-search baseline, AlphaEvolve generalizer-mode
    scoring across `n = 10..50`, Gemini 2.5 Flash/Pro model-call provenance,
    evaluated-program counts, public repository artifact status, and
    recurrence/proof checks for `alpha(2n)=2 alpha(n)+n`.
  - Required result: add roadmap gates for `2601.01235`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    permutation candidate schema, Bruhat interval witness artifacts, poset-
    hypercube verifier, dyadic well-distribution checker, power-of-two `S_n`
    benchmark records, dimension and asymptotic-bound calculations,
    Kazhdan-Lusztig `R`-polynomial coefficient metadata, cluster-algebra and
    Bruhat-graph consequence fields, finite-test/general-proof status,
    seed/budget records, independent checker outputs, and a background-only
    or benchmark-fixture status rule so roadmap claims do not outpace local
    AlphaEvolve-style Bruhat-interval hypercube support. Roadmap promotion
    should additionally require `x_m`/`y_m` generator fixtures, Ehresmann and
    fundamental/complementary-block verifier outputs, `d`-invariant and
    `R`-polynomial calculators, FunSearch/AlphaEvolve prompt/evaluator/run
    artifacts, public repo hash/status, low-discrepancy and `t`-adic
    extension metadata, proof-status records, and documentation separating
    finite AlphaEvolve-discovered examples from human-proved all-`m`
    constructions.

- [ ] Add global NLP solver comparator gates before roadmap promotion.
  - Spec evidence: arXiv `2601.05943`, submitted January 9, 2026, introduces
    `Global Optimization for Combinatorial Geometry Problems`. The abstract
    frames AlphaEvolve's geometric/combinatorial discoveries as a benchmark
    for modern off-the-shelf global optimization solvers, reformulates a
    subset of those problems as nonlinear optimization problems, evaluates
    FICO Xpress and SCIP without solver modifications, and reports reproduced
    and sometimes improved best-known solutions including recent LLM-driven
    results. The body covers min-max distance ratio, square/rectangle circle
    packing, and regular-hexagon packing with explicit nonlinear
    formulations, Mosel implementations, squared-distance QCPs, and Farkas-
    multiplier separation for hexagon non-overlap.
  - Current evidence: ROADMAP tracks AlphaEvolve constructive-math benchmark
    gaps and broad comparator ideas, but it does not promote `2601.05943`
    beyond potential-future-benchmark status. It does not define a direct NLP
    formulation gate, Xpress/SCIP runner abstraction, solver license/status
    handling, selected benchmark subset, solver parameter/time-limit policy,
    incumbent/bound/certificate artifact records, numerical tolerance policy,
    or side-by-side result table versus AlphaEvolve and literature baselines.
    It also lacks gates for Mosel/exported model artifacts, AlphaEvolve
    validation-code outputs, Table 1-3 value rows, rounding policy, source-link
    provenance for prior packing data and OpenEvolve/SciPy/SCIP, commercial
    Xpress availability handling, solver-attribution caveats, and dual-bound
    reporting expectations.
  - Required result: add roadmap gates for `2601.05943`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    selected AlphaEvolve benchmark subset, NLP formulation schema,
    variable/domain/constraint/objective records, FICO Xpress and SCIP solver
    identity/version/license records, solver parameter and resource-limit
    metadata, incumbent/bound/certificate artifacts, numerical tolerance
    policy, prior-literature and AlphaEvolve baseline values,
    reproduced/improved/fell-behind outcome rows, seed/run records,
    independent checker outputs, and a background-only or benchmark-fixture
    status rule so roadmap claims do not outpace local global-NLP solver
    comparison support. Roadmap promotion should additionally require per-
    family distance-ratio/circle/hexagon formulation fixtures, solver logs,
    primal incumbent and optional dual-bound records, AlphaEvolve/literature
    baseline citations, AlphaEvolve repository validation artifacts, Table 1-3
    reproduction reports, license/reproducibility status, and documentation
    that direct NLP solver baselines complement but do not implement
    AlphaEvolve's LLM evolutionary-search mechanism.

- [ ] Add post-AlphaEvolve autoconvolution improvement gates before roadmap
      promotion.
  - Spec evidence: arXiv `2506.16750`, submitted June 20, 2025 and last
    revised August 10, 2025, introduces `An improved example for an
    autoconvolution inequality`. The abstract reports a nonnegative
    `575`-interval step function with autoconvolution ratio `>= 0.901564`,
    improving on AlphaEvolve's `50`-interval `>= 0.8962` result, and says the
    improvement came from simulated annealing and gradient-based methods
    rather than LLMs. The body gives a finite discrete checker using samples
    `L_j`, formula `(3)`, exact rational value
    `96086089410408840289339769 / 106577013451431545242354944`, and public
    Python/Mathematica artifacts in `autoconvolutionHolder`.
  - Current evidence: ROADMAP tracks AlphaEvolve Appendix B autoconvolution
    gaps and broad constructive-math fixture needs, but it does not promote
    `2506.16750` beyond potential-future-benchmark status. It does not define
    a 575-interval witness gate, post-AlphaEvolve baseline comparison, direct
    recomputation of the `0.901564` objective, simulated-annealing/gradient
    provenance records, or documentation rules that separate AlphaEvolve's
    LLM-generated witness from later non-LLM improvements. It also lacks gates
    for public GitHub artifact hashes, integer-coefficient parsing and scaling
    by `2^24`, Python/Mathematica checker parity, Matolcsi-Vinuesa `20`-step
    comparison, AlphaEvolve coefficient-source reversal, translation/dilation
    normalization, NCSU HPC provenance, and exact-rational result rows.
  - Required result: add roadmap gates for `2506.16750`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    step-function witness schema, 575-interval payload artifacts, interval
    grid/spacing records, autoconvolution/norm recomputation records,
    objective and tolerance policy, AlphaEvolve 50-interval baseline value,
    simulated-annealing and gradient-method provenance, prior/current result
    rows, independent checker outputs, and a background-only or benchmark-
    fixture status rule so roadmap claims do not outpace local
    post-AlphaEvolve autoconvolution-improvement support. Roadmap promotion
    should additionally require coefficient-table row-order tests, exact
    fraction and rounded decimal checks, `L_j` sample traces, `L1` equivalence
    checks, initial/refinement/upscale search-stage metadata, repository
    status for `Inital HPC code.py`, `Refine HPC code.py`, `f95.py`,
    `coeffBL.txt`, and `Verify.nb`, and documentation separating theorem
    certificates from search-procedure provenance.

- [ ] Add post-AlphaEvolve sums-and-differences construction gates before
      roadmap promotion.
  - Spec evidence: arXiv `2505.16105`, submitted May 22, 2025, introduces
    `Sums and differences of sets (improvement over AlphaEvolve)` by Robert
    Gerbicz. The abstract says AlphaEvolve used a `54265`-integer set to
    improve the known lower bound from `theta = 1.14465` to `theta = 1.1584`,
    while this paper improves the bound to `theta = 1.173050` using an
    explicit `U` set with more than `10^43546` elements and GMP arithmetic.
    The paper defines `W(m, L, B)` bounded-coordinate sets, a base-`2B + 1`
    integer encoding, sumset/difference-set/max-element formulas, a
    `theta = 1.162997` small-search case for `m = 80`, `L = 64`, `B = 5`,
    and an exact-arithmetic confirmation for `m = 81411`, `L = 65536`,
    `B = 5` with approximate reported values `|U| = 6.314107319e43546`,
    `|U + U| = 3.208492702e61228`, `|U - U| = 6.587554451e75899`, and
    `2 max(U) + 1 = 6.605282799e84780`. It cites GMP code and exact computed
    values at `https://bit.ly/43mWCVC`.
  - Current evidence: ROADMAP tracks AlphaEvolve Appendix B sums-and-
    differences gaps and broad constructive-math fixture needs, but it does
    not promote `2505.16105` beyond potential-future-benchmark status. It
    does not define a huge explicit `U`-set construction gate, compressed set
    artifact representation, `W(m, L, B)` formula fixture, base-`2B + 1`
    encoding checker, sumset/difference-set verifier, max-element/q-value
    verifier, `theta` recomputation report, exact-value artifact retrieval,
    AlphaEvolve `54265`-integer baseline comparison, GMP arithmetic
    provenance, or documentation rule that separates AlphaEvolve's
    LLM-generated construction from later explicit improvements.
  - Required result: add roadmap gates for `2505.16105`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    explicit `U`-set construction schema, huge-set artifact representation,
    `W(m, L, B)` inclusion-exclusion records, base-`2B + 1` encoding checks,
    `(80, 64, 5)` and `(81411, 65536, 5)` parameter rows, sumset and
    difference-set cardinality records, max-element/q-value and set-size
    metadata, `theta` formula and tolerance policy, exact computed-value
    payload hashes, AlphaEvolve `54265`-integer `1.1584` baseline value,
    previous `1.14465` lower-bound source, GMP/version/arithmetic provenance,
    prior/current result rows, independent checker outputs, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local post-AlphaEvolve sums-and-differences improvement support.

- [ ] Add further post-AlphaEvolve sums-and-differences sequence gates before
      roadmap promotion.
  - Spec evidence: arXiv `2506.01896`, submitted June 2, 2025, introduces
    `Sums and differences of sets: a further improvement over AlphaEvolve`.
    The abstract says it improves on both AlphaEvolve's `theta = 1.1584` and
    the subsequent explicit-construction result `theta = 1.173050`, by
    constructing a sequence of `U` sets whose limit establishes
    `theta = 1.173077`. The Fan Zheng paper uses large-deviation estimates
    for `W(m, floor(rm), B)`, the base-`2B + 1` bounded-coordinate integer
    construction, asymptotic bounds on `q(U)`, `s(U)`, and `d(U)`, and a
    MATLAB 2024b tolerance sweep. It reports the restricted optimization over
    `B = 3..10`, `r in (0.5, 2)`, and `a in (0, min(1, 1/r))`, with the best
    row at `B = 5` and `theta - 1 = 0.173077279785136` for `1e-8` and
    `1e-10` tolerances.
  - Current evidence: ROADMAP tracks AlphaEvolve Appendix B sums-and-
    differences gaps and now the `2505.16105` explicit-construction boundary,
    but it does not promote `2506.01896` beyond potential-future-benchmark
    status. It does not define a sequence-of-sets construction gate, finite-
    prefix artifact schema, limiting-bound derivation record, convergence/
    tail-bound checker, large-deviation proof-object gate, MATLAB-code
    extraction/reimplementation gate, tolerance-sweep reproducibility gate,
    lineage comparison from AlphaEvolve to `2505.16105` to `2506.01896`, or
    documentation rule that separates finite witness verification from
    asymptotic sequence evidence.
  - Required result: add roadmap gates for `2506.01896`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    sequence-of-`U` construction schema, per-parameter and finite-prefix
    artifacts, limiting lower-bound derivation metadata, convergence/tail-
    bound checker records, large-deviation `I(c, B)` records, asymptotic
    `W(m, floor(rm), B)` count metadata, MATLAB 2024b code provenance,
    independent reimplementation outputs, tolerance-sweep rows for
    `B = 3..10` and `1e-4..1e-10`, sumset/difference-set cardinality records,
    `theta` formula and tolerance policy, AlphaEvolve `1.1584` baseline,
    `2505.16105` `1.173050` baseline, prior/current result rows, independent
    checker outputs, and a background-only or benchmark-fixture status rule
    so roadmap claims do not outpace local further post-AlphaEvolve
    sums-and-differences sequence support.

- [ ] Add UCB1 finite-time bandit gates before roadmap scheduler promotion.
  - Spec evidence: the local `auer-cesa-bianchi-fischer-2002` PDF,
    `Finite-time Analysis of the Multiarmed Bandit Problem`, by Peter Auer,
    Nicolo Cesa-Bianchi, and Paul Fischer studies the exploration/
    exploitation dilemma for multi-armed bandits, defines regret as expected
    loss from not always playing the best arm, and proves UCB1 finite-time
    logarithmic regret for arbitrary reward distributions with support in
    `[0, 1]` using play counts, empirical reward means, and a confidence-
    radius index. Theorem 1 gives the `8 ln(n) / Delta_i` suboptimal-pull
    constant and a finite-time regret bound; the paper also says Theorems 1-3
    do not require cross-machine independence and only need a per-arm
    conditional-mean assumption. UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and
    UCB1-TUNED are separate variants, with UCB1-TUNED explicitly not given a
    regret proof.
  - Current evidence: ROADMAP can describe LibreEvolve's heuristic UCB-style
    backend routing and already warns that canonical UCB1 assumptions,
    calibrated reward scaling, and regret bounds are not proven. The roadmap
    does not yet tie that scheduler caveat to the local UCB1 paper source id,
    PDF/cache hash, bounded-support and conditional-mean/stationarity
    assumptions, theorem constants, reward normalization, stable arm identity,
    selected-arm/index telemetry, coefficient mapping, role-scoped and
    metadata-aware selection caveats, or proof-scope metadata.
  - Required result: add roadmap gates for `auer-cesa-bianchi-fischer-2002`:
    paper/source manifest entry, PDF/cache hash, source-license or mirror
    status, UCB1 theorem-scope fields, reward-support normalization,
    stable backend-as-arm identity, conditional-mean/stationarity disclaimers,
    selected-backend/index traces, canonical-index and exploration-coefficient
    mapping, regret report fields when applicable, unsupported status for
    UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and UCB1-TUNED, proof-status
    metadata for `throughput_depth`, and README/papers/code wording that keeps
    current backend scheduling heuristic until canonical UCB1 assumptions and
    finite-time-regret evidence are validated.

- [ ] Add GigaEvo framework gates before roadmap promotion.
  - Spec evidence: local arXiv `2511.17592`, `GigaEvo: An Open Source
    Optimization Framework Powered by LLMs and Evolution Algorithms`, by
    Valentin Khrulkov et al. presents an AlphaEvolve-inspired framework with
    Redis-backed evolutionary units, `asyncio` DAG processing, MAP-Elites
    evolution, LangGraph mutation, generated insights, bidirectional lineage
    tracking, Hydra configuration, and benchmark experiments against
    AlphaEvolve problem families. Its program records carry UUID, source,
    lifecycle state (`FRESH`, `RUNNING`, `COMPLETE`), metrics, genealogy, and
    DAG outputs; its DAG supports validation/execution/complexity/insight/
    lineage/mutation-context stages with caching and automatic stage skipping.
    It reports single-island experiments with `Qwen3-235B-A22B-Thinking-2507`,
    Heilbronn `0.0364` vs AlphaEvolve `0.0365`, circle-packing attempts for
    `n = 26` and `n = 32`, kissing-number recovery without improvements in
    most dimensions, bin-packing `0.55%` Weibull excess usage, and Jigsaw
    prompt/agent evolution with `0.803` test AUC.
  - Current evidence: ROADMAP tells readers to keep GigaEvo features labeled
    as inspired unless the paper behavior is actually implemented, and
    `papers/README.md` marks Redis lifecycle database, `asyncio` DAG engine,
    insight stage, and concurrent units as absent. The roadmap does not yet
    define `2511.17592`-specific gates for source metadata, code repository
    status, architecture-component parity, lifecycle-state persistence,
    DAG-stage dependency/caching evidence, Hydra/problem-layout parity,
    lineage/insight artifacts, or benchmark-reproduction reports.
  - Required result: add roadmap gates for `2511.17592`: paper/source manifest
    entry, PDF/cache hash, source-license and code-artifact status,
    Redis-vs-local-storage boundary, program lifecycle state model, DAG
    topology/stage-output/caching records, concurrency telemetry, insight and
    ancestor/descendant lineage-analysis artifacts, mutation-operator
    provenance, Hydra/component-configuration mapping, MAP-Elites/island
    compatibility reports, AlphaEvolve benchmark reproduction rows plus
    bin-packing and prompt/agent rows where referenced, source-code URL
    disambiguation for the AIRI/FusionBrainLab links, and README/papers/code
    wording that keeps GigaEvo as framework inspiration until local evidence
    proves otherwise.

- [ ] Add CodeEvolve operator and benchmark gates before roadmap promotion.
  - Spec evidence: local arXiv `2510.14150`, `CODE EVOLVE: an open-source
    evolutionary framework for algorithmic discovery and optimization`, by
    Henrique Assumpcao et al. describes islands-based genetic search, weighted
    LLM ensembles, inspiration-based semantic crossover, meta-prompting,
    depth-based targeted refinement, exploration scheduling, sandboxed
    evaluation, MAP-Elites/CVT archives, and AlphaEvolve/EoH benchmark plus
    quality-cost comparisons. It defines prompt/solution fitness, Algorithm 1
    exploitation/exploration, Plateau Scheduler, rank-based inspirations,
    elitist migration, runtime/memory-bounded evaluation, and default guidance
    including `5` or `10` islands, `200` or `250` epochs, ancestor depth
    `3..5`, `2..3` inspirations, migration rate `0.1`, and exploration rate
    `0.2..0.5`. Table 1 says CODE EVOLVE matches or surpasses AlphaEvolve on
    `5` of `9` instances, and Table 2 records Qwen3-Coder-30B vs GEMINI-2.5
    cost/time comparisons.
  - Current evidence: ROADMAP says CodeEvolve features should remain labeled
    as inspired unless the paper behavior is actually implemented, and
    `papers/README.md` marks crossover, targeted refinement, modular
    orchestration, and context-aware recombination as absent. The roadmap does
    not yet define `2510.14150`-specific gates for source metadata, linked code
    status, prompt/solution dual fitness, semantic crossover, meta-prompting,
    depth-refinement context, exploration-scheduler traces, sandbox parity,
    MAP-Elites/CVT archive behavior, benchmark rows, ablations,
    hyperparameter defaults, open-framework comparisons, or quality-cost
    comparison evidence.
  - Required result: add roadmap gates for `2510.14150`: paper/source manifest
    entry, PDF/cache hash, source-license and code-artifact status,
    islands/population metadata, prompt/solution fitness records, weighted
    ensemble and model-cost telemetry, inspiration-crossover and
    meta-prompting artifacts, targeted-refinement ancestor context,
    exploration-scheduler traces, sandbox runtime/memory evidence,
    MAP-Elites/CVT archive compatibility, AlphaEvolve/EoH benchmark and
    ablation/cost rows, OpenEvolve/ShinkaEvolve comparison rows,
    LLM-backbone sensitivity rows, hyperparameter-guidance records, and
    README/papers/code wording that keeps CodeEvolve as agentic code-evolution
    inspiration until local evidence proves operator and benchmark parity.

- [ ] Add ThetaEvolve test-time learning gates before roadmap promotion.
  - Spec evidence: local arXiv `2511.23473`, `ThetaEvolve: Test-time Learning
    on Open Problems`, by Yiping Wang et al. was submitted as arXiv v1 on
    November 28, 2025 and describes a dynamic program-evolution environment
    with a single LLM, large program database, batch sampling, early checks,
    lazy penalties, optional reward shaping, GRPO/RL training at test time,
    RL-trained checkpoints, and AlphaEvolve-related open-problem benchmark
    claims. It reports OpenEvolve-based evaluation with `slime` RL training,
    `B = 32`, `n = 16`, `16384` response tokens, rollout temperature `1.0`,
    `16` concurrent verifier programs, GRPO with asymmetric clipping
    (`0.2`/`0.28`), learning rate `1e-6`, weight decay `0.1`, and no KL or
    entropy regularization.
  - Current evidence: ROADMAP says ThetaEvolve features should remain labeled
    as inspired unless the paper behavior is actually implemented, and
    `papers/README.md` states that LibreEvolve has clipped-reward JSONL export
    but no online RL/GRPO training loop, checkpoint management, resume
    semantics, or lazy-penalty dynamics. The roadmap does not yet define
    `2511.23473`-specific gates for source metadata, linked code status,
    dynamic-environment architecture, batch-sampling evidence,
    database-scaling reports, lazy-penalty and reward-shaping semantics,
    GRPO training telemetry, checkpoint lifecycle, transfer/generalization
    reports, SGLang/vLLM-style throughput reports, evaluator caveats, or
    benchmark comparisons.
  - Required result: add roadmap gates for `2511.23473`: paper/source manifest
    entry, PDF/cache hash, source-license and code-artifact status,
    single-LLM/database/batch-sampling metadata, early-check and lazy-penalty
    schemas, reward-shaping parameters, GRPO/RL training-run records,
    generated-sample and compute-budget telemetry, checkpoint/adaptor
    lifecycle, inference-with-trained-checkpoint and transfer reports,
    task/evaluator compatibility notes, AlphaEvolve/ShinkaEvolve/OpenEvolve
    comparison rows, Table 1/2/9 main benchmark rows, Table 3 static/format
    reward baselines, Table 4/10 database ablations, Table 5/6 pipeline
    throughput rows, Table 7/8 reward-shaping configuration rows, and
    README/papers/code wording that keeps ThetaEvolve as test-time-training
    inspiration until local evidence proves actual test-time learning support.

- [ ] Add ImprovEvolve modular-operator gates before roadmap promotion.
  - Spec evidence: local arXiv `2602.10233`, `ImprovEvolve: Ask AlphaEvolve
    to Improve the Input Solution and Then Improvise`, by Kravatskiy,
    Khrulkov, and Oseledets was submitted as arXiv v1 on February 10, 2026 and
    replaces direct solution-generation with an evolved
    `generate_config`/`improve`/`perturb` class executed by a two-stage
    basin-hopping validation loop with multi-seed initialization, scheduled
    perturbations, monotonic acceptance, GigaEvo outer evolution, and HEX/ACI2
    benchmark claims including `ImprovEvolve+E`. It uses Gemini 3 Pro to
    generate/refine `5` initial programs, Gemini 3 Flash Preview through
    OpenRouter for evolution, GigaEvo default prompts/stages, a single-island
    MAP-Elites archive with `150` fitness bins, `elites = 6`, `parents = 2`,
    `offspring = 10`, and CPU-parallel program execution during evolution.
  - Current evidence: ROADMAP says ImprovEvolve features remain inspired unless
    paper behavior is implemented, and `papers/README.md` scopes LibreEvolve to
    static modular guidance with false execution/enforcement flags. Roadmap
    lacks `2602.10233`-specific gates for source metadata, interface
    enforcement, validation-loop execution, perturbation schedules, inner/outer
    loop separation, human-edit provenance, GigaEvo dependency/backbone status,
    model/provider provenance, HEX/ACI2 benchmark rows, ablations, and budget
    evidence.
  - Required result: add roadmap gates for `2602.10233`: paper/source manifest
    entry, PDF/cache hash, ACM/preprint rights and linked-code status,
    `generate_config`/`improve`/`perturb` interface schema, Stage A/B runner,
    seed counts, basin-hopping rounds, perturbation schedules, monotonic
    acceptance/incremental improvement records, GigaEvo/backbone metadata,
    Gemini/OpenRouter model provenance, human-edited variant attribution, HEX
    and ACI2 benchmark/baseline/result rows, Table 2 hyperparameter rows,
    Table 3 generalization rows, Table 4 Stage A/B and LLM-edit ablation rows,
    CPU/GPU timeout/compute budgets, wall-clock budget rows (`~10h` HEX,
    `~40h` ACI2), and README/papers/code wording that keeps ImprovEvolve as
    modular-search inspiration until local execution semantics and benchmark
    evidence are validated.

- [ ] Add MadEvolve parameter-optimization gates before roadmap promotion.
  - Spec evidence: local arXiv `2602.15951`, `MadEvolve: Evolutionary
    Optimization of Cosmological Algorithms with Large Language Models`, by
    Tianyi Li, Shihui Zang, and Moritz Munchmeyer was submitted as arXiv v1 on
    February 17, 2026 and adapts AlphaEvolve-style evolution to scientific
    algorithms with nested free-parameter optimization, greedy one-shot
    derivative-free search, autodiff/Adam tuning for differentiable JAX/`vmad`
    programs, hybrid MAP-Elites/island/elite population management, UCB model
    routing, diff/full/synthesis mutation modes, automated scientific reports,
    and BAO, iterative BAO, 21cm, and tSZ benchmark claims. It describes a
    three-stage report generator (`lineage extraction`, `comparative analysis`,
    and `synthesis`) and a five-island heterogeneous LLM ensemble with UCB
    model selection.
  - Current evidence: ROADMAP says MadEvolve features remain inspired unless
    paper behavior is implemented, README labels MadEvolve as background
    context, and `papers/README.md` states that no free-parameter optimization
    or innovation report exists. Roadmap lacks `2602.15951`-specific gates for
    source metadata, linked code status, parameter schemas, inner optimizer
    execution, differentiability/operator constraints, optimized-value source
    injection, per-task cosmology fixtures, generated reports, run statistics,
    model-contribution statistics, compute environment, reward-hacking
    diagnostics, hosted report-link validation, and
    over-parameterization/generalization evidence.
  - Required result: add roadmap gates for `2602.15951`: paper/source manifest
    entry, PDF/cache hash, madevolve.org and GitHub source status,
    framework-vs-application split, parameter-declaration and parameter-meaning
    schemas, one-shot/grid/Latin-hypercube/Bayesian and autodiff/Adam optimizer
    records, inner/outer budget accounting, JAX/vmad differentiability
    validation, optimized-value source-injection provenance, BAO/iterative
    BAO/21cm/tSZ task prompts and evaluator fixtures, training/validation/test
    split provenance, generated lineage/comparative-analysis/synthesis report
    artifacts, Table 1 benchmark rows, Table 2 success/improvement statistics,
    Table 3 model-contribution statistics, compute environment, reward-hacking
    and mode-collapse diagnostics, Quijote/LDL/vmad provenance, hosted
    report-artifact checks, and README/papers/code wording that keeps
    MadEvolve as background until local evidence proves those semantics.

- [ ] Add CausalEvolve causal-scratchpad gates before roadmap promotion.
  - Spec evidence: local arXiv `2603.14575v2`, `CausalEvolve: Towards
    Open-Ended Discovery with Causal Scratchpad`, by Yongqiang Chen et al. was
    submitted as arXiv v1 on March 15, 2026 and revised as v2 on March 29,
    2026. It models evolve-based scientific discovery as a POMDP over hidden
    scientific knowledge, uses SCM intervention language for program
    evaluation, and introduces a causal scratchpad with LLM-generated
    outcome-level factors, CausalPlanner factor-direction interventions,
    procedure-level factor discovery, approximate treatment effects,
    surprise-pattern detection, abductive hypothesis generation, and four-task
    benchmark comparisons. The CausalPlanner action space is `(factor, +1)` or
    `(factor, -1)`, inspiration programs are sorted by selected factor
    direction, rewards use `(child_score - tau * best_so_far)+`, and random
    actions are alternated for `K` iterations with currently best actions for
    the next `K` iterations.
  - Current evidence: ROADMAP says CausalEvolve features remain inspired unless
    paper behavior is implemented, README describes the causal plugin as fixed
    token-pattern guidance rather than a causal scratchpad, and
    `papers/README.md` says there are no LLM-discovered causal variables.
    Roadmap lacks `2603.14575`-specific gates for source metadata,
    POMDP/SCM-scoped task records, LLM factor-generation prompts, executable
    outcome-factor code, intervention actions, inspiration-sorting traces,
    procedure-factor extraction, treatment-effect estimates, surprise-pattern
    and abductive-reasoning artifacts, benchmark rows, ablations, seed/step
    schedules, model provenance, and environment-shift/generalization caveats.
  - Required result: add roadmap gates for `2603.14575`: paper/source manifest
    entry, PDF/cache hash, code/source status, causal scratchpad schema,
    POMDP/SCM and environment metadata, outcome-factor and executable
    factor-code contracts, CausalPlanner action/reward policy with tau and K
    parameters, inspiration-selection records, procedure-factor extraction
    artifacts, approximate treatment-effect reports, surprise-pattern detector
    outputs, abductive hypothesis/factor lifecycle, scratchpad replay
    artifacts, Hadamard/autocorrelation/circle-packing/AIME benchmark rows,
    ShinkaEvolve/CausalPlanner(Meta)/COAT comparison rows, Grok-4.1-FR model
    provenance, seed and step schedules, and README/papers/code wording that
    keeps CausalEvolve as causal-guidance inspiration until local evidence
    proves causal-scratchpad semantics. Roadmap result rows must include
    Table 1 final-step comparisons for Hadamard, second autocorrelation,
    circle packing, and AIME, plus CC BY-NC-SA license and no-dedicated-code-
    link status.

- [ ] Add DeepEvolve cross-file research/debug-loop gates before roadmap
      promotion.
  - Spec evidence: local arXiv `2510.06056v1`, `Scientific Algorithm Discovery
    by Augmenting AlphaEvolve with Deep Research`, by Gang Liu et al. was
    submitted on October 7, 2025 and combines algorithmic deep research and
    evolution through planning, searching, writing, cross-file coding,
    evaluation, and evolutionary selection. It also adds reflection, debugging
    attempts from execution feedback, algorithm-description records,
    evolutionary database inspirations, MAP-Elites/island sampling, and
    effectiveness/runtime/debugging ablations over nine scientific benchmark
    tasks. The workflow explicitly uses a debugger template for multi-file
    Python codebases, `DEEPEVOLVE` edit blocks, score-zero fallback after a
    debugging budget, and 30-minute single-GPU constraints on several tasks.
  - Current evidence: ROADMAP tracks DeepEvolve-inspired retrieval only as
    bounded provenance moving toward audit-grade source integrity, README says
    the plugin is best-effort retrieval context rather than a systematic
    DeepEvolve debug/refinement loop, and `papers/README.md` excludes cross-file
    debugging/editing. Roadmap lacks `2510.06056`-specific gates for the
    six-module workflow, proposal writing, cross-file coding, debugging-budget
    execution traces, reflection checkpoints, algorithm-description metadata,
    source/repository status, nine-task benchmark reports, runtime/GPU budgets,
    qualitative idea-scoring records, and deep-research ablations.
  - Required result: add roadmap gates for `2510.06056`: paper/source manifest
    entry, PDF/cache hash, code/source status, problem/input and user-
    instruction schemas, plan/search/write proposal records, pseudo-code
    artifacts, retrieved-source provenance, cross-file delimiter/localization
    policy, self-reflection and debugging attempt records, execution
    warning/error traces, score-zero fallback semantics, evolutionary database
    and inspiration/MAP-Elites compatibility reports, Table 1 task/metric rows,
    Table 2 performance/runtime rows, Table 3 debugging success-rate rows,
    Figure 3 idea-quality judge records, deep-research ablation rows,
    30-minute/single-GPU budget evidence, Table 4 deep-research ablation rows,
    Appendix C user-query/hyperparameter records, CC BY 4.0 license and GitHub
    repo status, and README/papers/code wording that keeps DeepEvolve as
    retrieval/debug-loop inspiration until local execution evidence proves
    those semantics.

- [ ] Add MAP-Elites illumination-algorithm gates before roadmap promotion.
  - Spec evidence: local arXiv `1504.04909`, `Illuminating search spaces by
    mapping elites`, by Jean-Baptiste Mouret and Jeff Clune is a preliminary
    draft dated April 21, 2015 with cached SHA-256
    `df7344343b14893a1d79a5459c1f56db50562e246d132cd0269f5201d1455872`.
    It defines MAP-Elites as a feature-performance map over user-chosen
    dimensions of variation. The simple algorithm maintains maps `P` and `X`,
    initializes with random solutions, repeatedly selects an elite from the map,
    applies random variation, computes feature descriptor `b(x)` and
    performance `f(x)`, and replaces a cell occupant only when the new
    candidate improves that cell. The paper evaluates illumination with global
    performance, global reliability, precision, and coverage over neural
    networks, simulated soft robots, and a physical soft arm.
  - Current evidence: ROADMAP describes a configurable local MAP-Elites archive
    and tracks stable descriptor/rebin gaps, while `papers/README.md` says the
    default local axes are selection score, serialized-workspace complexity,
    and TF-IDF diversity. Roadmap lacks `1504.04909`-specific gates for paper
    source metadata, explicit feature-descriptor schemas, user-chosen dimension
    semantics, initialization/variation evidence, full feature-performance map
    exports, unfilled-cell diagnostics, illumination metric reports,
    visualization artifacts, parent-distance/lineage stepping-stone analysis,
    benchmark/domain reproduction, and descriptor compatibility tests.
  - Required result: add roadmap gates for `1504.04909`: paper/source manifest
    entry, PDF/cache hash, preliminary-draft status, `b(x)`/`f(x)` contracts,
    dimension declaration and discretization policy, random-initialization and
    variation policy, per-cell replacement records, `P`/`X` feature-
    performance map exports, empty/unfillable cell diagnostics, coverage/global
    reliability/precision/global-performance reports, heatmap/visualization
    artifacts, lineage parent-cell distance reports, retina and robot
    experiment schedules, descriptor-model compatibility and rebin validation,
    NS+LC/MOLE/random/traditional-EA/EA+D/grid-search comparison context,
    benchmark-domain notes, preliminary-draft caveat, and README/papers/code
    wording that keeps current 3D archive support separate from full
    MAP-Elites illumination evidence.

- [ ] Add hardness-of-approximation proof-element gates before roadmap
      promotion.
  - Spec evidence: local arXiv `2509.18057v7`, `Reinforced Generation of
    Combinatorial Structures: Hardness of Approximation`, by Ansh Nagda,
    Prabhakar Raghavan, and Abhradeep Thakurta was submitted as v7 on March 9,
    2026 with cached SHA-256
    `32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842`
    and CC BY 4.0 metadata. It reports AlphaEvolve-discovered Ramanujan graph
    witnesses, MAX-3-CUT/MAX-4-CUT gadget reductions, metric-TSP equation
    gadgets, evolved faster verifier code, final brute-force verification of
    discovered gadgets, and mathematical lifting from finite structures to
    theorem statements.
  - Current evidence: ROADMAP has a general theoretical-CS source-tracking TODO
    and `papers/README.md` labels `2509.18057` background-only with no graph/
    certification benchmark. Roadmap lacks `2509.18057`-specific gates for
    graph/gadget artifact schemas, witness inventories, verifier APIs,
    synthetic correctness datasets, evolved-verifier runtime telemetry,
    judge-LLM/human-inspection records, brute-force final verification outputs,
    theorem/lemma/proof cross-links, proof-lifting metadata, source/artifact
    status, and SOTA comparison rows.
  - Required result: add roadmap gates for `2509.18057`: paper/source manifest
    entry, PDF/cache hash, code/artifact availability, Ramanujan graph witness
    schema and Table 1 certification rows, MAX-k-CUT gadget schema with
    Appendix C edge lists, TSP/MWST equation-gadget schema with Appendix D edge
    lists, verifier contracts, evolved-verifier speedup reports, synthetic
    correctness-check dataset provenance, judge-LLM and human-inspection
    attribution, independent brute-force verifier artifacts, theorem/result/
    lifting metadata, baseline/SOTA comparison rows for MAX-4-CUT, MAX-3-CUT,
    and metric TSP, proof-handoff status, extracted-link/source-repository
    status, and README/papers/code wording that keeps hardness-of-approximation
    proof-element support background-only until local execution, artifact, and
    verification evidence proves those semantics.
