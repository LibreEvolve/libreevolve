# Code Todo: AlphaEvolve Specification Gaps

This list tracks implementation gaps found by auditing the current code against
the AlphaEvolve paper and public DeepMind description. The goal is to move
LibreEvolve from a small AlphaEvolve-inspired prototype toward behavior that is
truthful to the AlphaEvolve specification.

Primary evidence:

- AlphaEvolve paper `papers/2506.13131__AlphaEvolve.pdf`, especially Sections
  2.1-2.6 and 4.
- DeepMind blog: AlphaEvolve pairs LLMs, automated evaluators, and an
  evolutionary framework; it can evolve entire codebases, not just a single
  function or small program.
- Current implementation in `libreevolve/core`, `libreevolve/population`,
  `libreevolve/problems`, `libreevolve/llm`, and `libreevolve/plugins`.

## Candidate Workspace Fidelity

- [ ] Extend the Python-primary candidate-language policy to real language and
  runner declarations.
  - Spec evidence: AlphaEvolve describes evolving code in existing codebases
    with task-defined evaluators; a faithful implementation needs explicit
    candidate language/build/runner boundaries instead of treating every
    candidate as a Python-primary file set.
  - Current evidence: startup manifests now include
    `policies.candidate_language` with schema
    `libreevolve.candidate_language_policy.v1`. The record declares
    `python_primary_text_workspace_v1`, bounded UTF-8 text workspace plus typed
    static members, Python-primary seed and `best.py` compatibility policy,
    fail-closed marker handling for non-Python marker-like files, Python
    subprocess validator entrypoints, and explicit unsupported status for
    arbitrary-language runners, build-system runners, and problem-defined
    solution abstractions. `validate_candidate_language_policy()` rejects
    overclaims that those runner surfaces are supported or language-runner
    ready.
  - Required result: add configured candidate language/runner declarations,
    language-aware evolve-block grammars, build-system runner contracts, and
    problem-defined candidate abstraction hooks before claiming non-Python or
    arbitrary-codebase AlphaEvolve fidelity. The remaining gap is implementing
    those runners and abstractions, not making the current Python-only
    divergence manifest-visible.

- [ ] Add existing-codebase minimal-marker integration provenance.
  - Spec evidence: AlphaEvolve Section 2.1 says its input API supports evolving
    multiple components across existing codebases with minimal changes, by
    adding special comment markers around blocks to be evolved. The local
    AlphaEvolve PDF page 4 states that the API annotates blocks to be evolved
    across a codebase and integrates with existing codebases by adding only
    `# EVOLVE-BLOCK-START` / `# EVOLVE-BLOCK-END` comments; Figure 3 on page 6
    shows those marked blocks alongside the special `evaluate(eval_inputs) ->
    dict[str, float]` function that invokes the marked code.
  - Current evidence: LibreEvolve validates Python `# EVOLVE-BLOCK-START/END`
    markers, rejects malformed or unsupported non-Python marker-like syntax,
    materializes bounded workspaces, and records candidate-language policy
    boundaries. `libreevolve/core/candidate.py` restricts skeleton-preserving
    markers to Python files and falls back to whole-file/full-workspace
    semantics for other files; `libreevolve/problems/loader.py` records seed
    workspace source paths and static-file hashes, and the `workspace_math`
    fixture proves nested Python files plus JSON/binary resources can be loaded
    and validated. Those mechanics prove marker parsing and local workspace
    preservation for seed workspaces, but they do not prove an AlphaEvolve-style
    integration workflow for a pre-existing codebase: baseline codebase
    identity, marker-only setup diff, untouched skeleton preservation across a
    real upstream tree, language/comment syntax, component span inventory,
    evaluator entrypoint continuity, or measured setup burden.
  - Required result: add integration metadata and validators for existing
    codebases: original codebase/artifact id, pre-marker source hashes,
    marker-added diff summary, evolved-block span ids, unchanged skeleton
    hashes, language/comment grammar, evaluator-call path before/after marker
    insertion, setup-change counts, source-root/release-artifact identity for
    copied static assets, a codebase-scale fixture with multiple marked
    components and preserved unmarked files, and README/ROADMAP wording that
    separates local evolve-block parsing from paper-faithful minimal-change
    codebase integration evidence.

- [ ] Add Figure 3 evolve-block marker spelling provenance.
  - Spec evidence: AlphaEvolve Section 2.1 names the special marker comments
    as `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END` on local PDF page 4,
    while PDF text extraction from Figure 3(a) on page 6 shows one opening
    marker as `# EVOLVE-BLOCK START` and another as `# EVOLVE-BLOCK-START`.
    The same Figure 3 caption says the user-provided file has blocks marked
    for evolution plus a special `evaluate` function invoked by evaluators.
  - Current evidence: LibreEvolve deliberately enforces the local exact
    Python marker grammar `# EVOLVE-BLOCK-START/END` and rejects malformed or
    unsupported marker-like syntax. A direct parser check accepts canonical
    `# EVOLVE-BLOCK-START a` but does not recognize `# EVOLVE-BLOCK START` as
    a start marker; when that space variant is paired with
    `# EVOLVE-BLOCK-END`, validation reports `orphan_end`. Existing Figure 3
    exhibit TODOs require source/prompt/output excerpt artifacts, but they do
    not explicitly classify this marker-text variant as canonical section
    prose, rendered figure text, extraction/OCR uncertainty, or paper typo.
  - Required result: record marker text per paper source location and
    subfigure, preserve source artifact hashes or screenshots for the variant,
    classify the discrepancy before using it in docs, add tests or a
    compatibility decision record if the space variant should ever be accepted,
    and keep parser/support claims scoped to the implemented local grammar
    unless a deliberate compatibility mode for the space variant is added.

- [ ] Add candidate-embedded `evaluate(eval_inputs)` entrypoint support and
      evidence.
  - Spec evidence: AlphaEvolve Section 2.1 and Figure 3 present a
    user-provided `evaluate(eval_inputs) -> dict[str, float]` function inside
    the codebase skeleton, with evolved blocks tied together so the evaluator
    can invoke the candidate program directly.
  - Current evidence: LibreEvolve runs problem-local validator entrypoints,
    usually external `validate.py` files, and records direct evaluator
    entrypoint provenance, problem-local dependency provenance, validator
    boundary metadata, and candidate imports in local validators. This is useful
    local validation, but it is not a first-class candidate-embedded evaluator
    API.
  - Required result: add a mode or report contract for candidate-owned
    `evaluate(eval_inputs)` functions, eval-input provenance, skeleton-to-block
    coupling, callable import/build isolation, and paper-facing evidence that
    distinguishes embedded AlphaEvolve-style evaluation from external
    problem-validator execution.

- [ ] Add Figure 1/Figure 2 architecture-process exhibit provenance.
  - Spec evidence: AlphaEvolve Figure 1 presents the high-level loop from human
    "What?" inputs through LLM ensemble, prompt sampler, evaluator pool, and
    program database to an improved solution. Figure 2 expands this into the
    controller loop: `database.sample()`, `prompt_sampler.build(...)`,
    `llm.generate(...)`, `apply_diff(...)`, `evaluator.execute(...)`, and
    `database.add(...)`.
  - Current evidence: LibreEvolve has implementation components and README
    workflow diagrams for seed programs, prompt construction, mutation,
    evaluation, MAP-Elites, island migration, and backend reward. Existing
    TODOs track many underlying behavior gaps, but no code/report schema maps
    the paper's Figure 1/Figure 2 nodes and edge labels to local components,
    run artifacts, controller-state records, prompt/evaluator/database events,
    source diagram locations, rendered diagram artifacts, or diagram hashes.
  - Required result: add architecture/process exhibit metadata with stable
    Figure 1/Figure 2 IDs, node/edge-to-component mappings, implemented versus
    unsupported status for controller, LLM, evaluator, prompt, and database
    surfaces, links to run artifacts that evidence each step, source/rendered
    diagram artifact hashes, and docs validation so local workflow diagrams are
    not mistaken for reproduced AlphaEvolve process-diagram evidence.

- [ ] Add unified AlphaEvolve task-specification bundle provenance.
  - Spec evidence: AlphaEvolve Section 2.1 is explicitly a task
    specification: the user provides the initial program/components to evolve,
    evaluation code, prompt template/configuration, choice of existing or
    custom LLMs, and optional background knowledge before the controller loop
    begins.
  - Current evidence: LibreEvolve manifests already record many pieces
    separately: problem/source provenance, seed source records, evaluator
    source hashes, redacted/hash-backed effective config fields, backend specs,
    prompt variants, context-source diagnostics, and source-root provenance.
    Those records are useful, but they do not form one paper-facing task-spec
    contract that proves which exact user-provided inputs jointly defined a
    run and how each maps to AlphaEvolve's task-spec fields.
  - Required result: add a versioned task-spec bundle with initial program or
    workspace ids, evolvable component spans, evaluator code/entrypoint ids,
    prompt template/config ids, LLM choice/backend ids, optional background
    knowledge/context ids, source hashes/redaction states, missing/unsupported
    field diagnostics, and README/ROADMAP wording that distinguishes scattered
    local provenance from an AlphaEvolve-style task specification artifact.

- [ ] Add abstraction-choice metadata and benchmark evidence for candidate
      representations.
  - Spec evidence: AlphaEvolve Section 2.1 and Discussion say the same problem
    can be approached by searching for solutions directly, evolving constructor
    functions, evolving bespoke search algorithms, or co-evolving intermediate
    solutions and search algorithms. The paper explicitly notes that these
    abstraction choices introduce biases, such as constructor functions
    favoring highly symmetric solutions while customized search algorithms may
    suit non-symmetric solutions.
  - Current evidence: LibreEvolve documents its current code-file-set
    candidate boundary and records unsupported problem-defined candidate
    abstraction hooks through `libreevolve.candidate_language_policy.v1`. It
    does not define an experiment/report schema that records which abstraction
    was selected for a benchmark, why that abstraction matches the problem's
    symmetry or search structure, or how alternative abstractions performed
    under comparable budgets.
  - Required result: add problem/run metadata for candidate abstraction choice,
    abstraction rationale, symmetry/structure assumptions, serializer/runner
    linkage, paired solution/search representations when supported, and
    benchmark reports comparing direct-solution, constructor, and
    search-algorithm approaches before claiming AlphaEvolve-style abstraction
    selection fidelity.

- [ ] Add structured initial-program idea provenance for benchmark seeds.
  - Spec evidence: AlphaEvolve Section 2.1 says the human provides the initial
    program and optional background knowledge, while Section 3.1 reports that
    some matrix targets improved when the initial program was seeded with
    researcher ideas such as stochastic evaluation or evolutionary approaches.
    That makes the seed's idea origin part of the experiment, not merely a
    filesystem source artifact.
  - Current evidence: LibreEvolve records safe initial-seed source provenance
    such as `seed_source_path`, `seed_source_kind`, `seed_index`, primary file,
    file counts, skipped seed diagnostics, and generation-0 baseline rows.
    Those records do not classify a seed as simple, random, researcher-idea
    seeded, prior-art-derived, or collaboration-enhanced; they do not record
    which human idea was embedded in the initial program; and benchmark reports
    do not compare simple versus idea-seeded starts for matrix or constructive
    math tasks.
  - Required result: add benchmark seed metadata and validation for initial
    program idea origin, human/background-knowledge contribution labels,
    declared prior technique or injected idea, prompt/run linkage, and
    seed-variant result evidence before claiming AlphaEvolve-style
    collaboration or human-seeded matrix benchmark parity.

- [ ] Add an AlphaEvolve-strict seed validity policy for complete initial
      programs.
  - Spec evidence: AlphaEvolve Section 2.1 says the initial implementation
    inside the evolvable code blocks should be complete, although it may be
    rudimentary, and the surrounding skeleton should let the evaluator invoke
    it as a working program before evolution.
  - Current evidence: LibreEvolve validates seed source safety, UTF-8/text
    limits, workspace shape, Python-primary marker structure, and evaluator
    return contracts. It then evaluates each seed, admits valid seeds, and logs
    invalid generation-0 seeds through `log_seed_failure()`. The shipped
    examples intentionally include optimization-pressure starts such as
    `hello_world`, whose seed is evaluator-invalid, and a run can record that
    every evaluated seed was invalid instead of failing task setup as an
    AlphaEvolve-strict initial-program contract violation.
  - Required result: add an explicit problem/run policy for strict
    AlphaEvolve-style initial-program validation, including seed evaluation
    before mutation, required validity/declared metric presence for every
    selected seed, manifest/report evidence distinguishing permissive
    optimization-pressure seeds from strict complete seeds, and docs that do
    not present invalid generation-0 baselines as faithful AlphaEvolve initial
    implementations.

- [ ] Add expert problem-formulation provenance for benchmark definitions.
  - Spec evidence: AlphaEvolve Section 2.1 frames the task definition,
    evaluator, initial solution, and optional background knowledge as
    human-provided inputs, and Section 3.2 says many open mathematical
    problems were suggested by external mathematicians who advised on how to
    formulate them for AlphaEvolve. That contribution is distinct from local
    context-file selection or seed source identity.
  - Current evidence: LibreEvolve records problem/source provenance, safe local
    context source labels, context-source selection/ranking/filter metadata,
    bounded prompt context hashes, and local paper/retrieval evidence. It does
    not define a benchmark metadata schema for expert contributor roles,
    problem-origin records, formulation advice, mathematical parameter-scope
    decisions, evaluator/objective rationale, or contribution visibility in
    benchmark reports.
  - Required result: add problem-definition metadata and validation for expert
    advisor/contributor roles, formulation notes, objective/evaluator
    rationale, parameter-scope decisions, background-knowledge linkage, and
    report/run provenance before claiming AlphaEvolve-style expert-guided
    mathematical benchmark formulation.

- [ ] Add early-user and collaborator feedback provenance for robustness
      claims.
  - Spec evidence: AlphaEvolve's Acknowledgements thank early users and
    collaborators for diverse use cases and insightful feedback that shaped
    the system into a more robust and versatile tool. That is a
    use-case-feedback evidence claim, distinct from expert mathematical
    problem formulation and from production-domain owner signoff.
  - Current evidence: LibreEvolve records problem/source provenance, local
    context sources, benchmark status rows, systems owner/reviewer TODOs, and
    expert formulation TODOs. It does not define a report schema that records
    early-user or collaborator feedback events, use-case taxonomy, affected
    feature or benchmark area, resulting product/code/documentation changes,
    validation evidence, privacy/redaction policy, or links from feedback to
    robustness or versatility claims.
  - Required result: add feedback-provenance metadata for use-case cohorts,
    collaborator role labels, feedback event IDs, affected workflow areas,
    change/artifact links, validation outcomes, and redaction policy before
    README, ROADMAP, or papers-index wording claims AlphaEvolve-style
    robustness or versatility shaped by broad collaborator feedback.

- [ ] Add acknowledgement-role provenance for review, support, and practical
      application management advice.
  - Spec evidence: AlphaEvolve's Acknowledgements separately thank named
    contributors for reviewing the white paper, early explorations and
    insightful discussions, support and advice, helpful advice on managing
    practical applications, and reviewing application-specific work. These are
    paper-process and governance roles distinct from early-user feedback,
    expert benchmark formulation, application owner signoff, and core
    implementation contributions.
  - Current evidence: LibreEvolve TODOs track early-user feedback, expert
    formulation, systems application owner/reviewer evidence, and core
    system-development contribution roles. They do not define a schema for
    paper-review, support/advice, practical-application management advice, or
    application-review acknowledgement records, nor a docs check that keeps
    these softer paper-process roles separate from technical validation or
    implementation authorship.
  - Required result: add acknowledgement-role metadata with safe contributor
    labels, role category (`white_paper_review`, `early_exploration`,
    `support_advice`, `practical_application_management_advice`,
    `application_review`), affected paper/application scope, source
    page/section, privacy/redaction policy, and README/ROADMAP wording that
    separates paper-process acknowledgement evidence from benchmark,
    deployment, validation, or system-development provenance.

- [ ] Add paper author-metadata provenance for equal contributors and
      correspondence roles.
  - Spec evidence: AlphaEvolve's Author information section names equal
    contributors, identifies manuscript-writing contributors and paper-input
    contributors in the Contributions section, and lists corresponding
    authors. These author metadata claims are distinct from technical system
    contributions, figure/Colab artifact authorship, and acknowledgement
    review/support roles.
  - Current evidence: LibreEvolve TODOs track core system-development roles,
    paper-artifact creator/assembler roles, and acknowledgement-role
    provenance, but no schema preserves paper author metadata such as equal
    contributor groups, manuscript-writing roles, paper-input roles, or
    corresponding-author records. Local docs could therefore cite the paper
    source without distinguishing artifact authorship, system authorship, and
    publication-author/contact metadata.
  - Required result: add paper-author metadata records with safe contributor
    labels, role category (`equal_contributor`, `manuscript_writer`,
    `paper_input`, `corresponding_author`), source page/section, applicable
    artifact or publication scope, privacy/contact redaction policy, and
    README/ROADMAP wording that separates publication metadata from technical
    implementation, validation, artifact-creation, and acknowledgement roles.

- [ ] Add AlphaEvolve title-page affiliation and footnote provenance.
  - Spec evidence: page 1 of `2506.13131__AlphaEvolve.pdf` presents the author
    list followed by `Google DeepMind1`, and the title-page footnotes state
    `1See Acknowledgments and Author information section.` and `*Equal
    contributions.`
  - Current evidence: existing TODOs require publication-author metadata for
    equal contributors, manuscript writers, paper-input contributors, and
    corresponding authors. They do not separately preserve the title-page
    affiliation/organization line, affiliation footnote, footnote marker
    mapping from author names to equal-contribution status, or docs wording
    that distinguishes source-paper affiliation from LibreEvolve's independent
    non-affiliation statement.
  - Required result: add publication-source metadata and validators for
    title-page affiliation evidence: affiliation/organization text, marker id,
    footnote text and page, author-to-marker mapping, source-page locator,
    privacy/redaction policy, and README/ROADMAP wording that separates
    paper-source affiliation/footnote provenance from local project ownership,
    endorsement, publication-author roles, and technical implementation
    provenance.

- [ ] Add core system-development contribution provenance.
  - Spec evidence: AlphaEvolve's Contributions section attributes the initial
    system design/implementation, project vision and problem scoping, first
    benchmark used for iterating on the system, final AlphaEvolve version,
    infrastructure maintenance, majority code reviews, team coordination, and
    research-program supervision to specific contributors and roles.
  - Current evidence: LibreEvolve records source/build provenance, run
    manifests, selected artifact roles for figures/notebooks, practical
    application owner/reviewer gaps, and early-user feedback gaps. It does not
    define a provenance layer for core system-development roles, implementation
    phases, review ownership, infrastructure ownership, benchmark-iteration
    ownership, or coordination/supervision boundaries.
  - Required result: add project/system contribution metadata and validators
    with safe role labels, development phase (`initial_design`,
    `first_benchmark_iteration`, `final_system`, `infrastructure`,
    `code_review`, `coordination`, `supervision`), artifact or module links,
    source section/page, review/approval scope, and README/ROADMAP checks so
    local docs do not imply AlphaEvolve-style development provenance from
    generic git history or contributor listings alone.

- [ ] Tighten remaining workspace topology collision diagnostics and keep
  materialization diagnostics complete for future edge cases.
  - Spec evidence: AlphaEvolve operates on task-defined program artifacts and
    codebases; invalid generated workspaces should produce inspectable
    evaluator feedback rather than opaque local filesystem exceptions.
  - Current evidence: `CandidateWorkspace.materialize()` now raises
    `CandidateMaterializationError` for materialized candidate-path collisions,
    linked target roots or ancestors, linked nested entries, file target roots,
    parent/temp root creation failures, candidate text/static write failures,
    existing-root backup failures, final swap failures, backup restore
    failures, cleanup deletion failures, and static source-copy link/read/
    not-file/hash/byte-count failures. `CascadeEvaluator` records bounded
    `evaluation.metadata.materialization_error` fields including
    `exception_type: "CandidateMaterializationError"`, stable `reason`, and
    bounded relevant `paths`. Prompt context policy can select and cap
    `reason`, `paths`, `exception_type`, and `message` for
    materialization-error feedback. File topology mutations are also
    prevalidated for duplicate topology sections, duplicate move targets,
    chained/conflicting operations, host/case-folded file or move-target
    collisions, non-empty command bodies, and primary deletion without
    replacement. Static `source_copy_path` members are checked at
    materialization time for links, byte count, and SHA-256, but their source
    identity is still a local path label rather than a portable manifest-rooted
    artifact reference.
  - Required result: extend topology diagnostics for future topology surfaces
    such as bulk directory operations or language/build-runner generated
    artifacts; add a portable source-root/release-artifact policy for copied
    static members; and preserve the stable `CandidateMaterializationError`
    reason/path contract whenever new materialization filesystem paths are
    added.

- [ ] Add codebase-scale benchmark evidence for multi-component generated
      programs.
  - Spec evidence: AlphaEvolve Table 1 contrasts prior FunSearch-style systems
    with AlphaEvolve's ability to evolve entire code files, hundreds of lines
    of code, arbitrary languages, and complex algorithms spanning multiple
    functions and components.
  - Current evidence: LibreEvolve supports Python-primary text workspaces,
    multi-file seed loading, topology mutations, full-workspace prompt
    rendering/materialization, complete `best_workspace/` export, and a small
    `workspace_math` smoke fixture. The current examples and tests do not
    constitute a codebase-scale benchmark: they do not exercise hundreds of
    generated lines, multiple coupled components, language/build runners, or
    long-horizon automated evaluation over a realistic multi-component
    codebase.
  - Required result: add a benchmark/report contract and fixtures that track
    generated line counts, changed component counts, cross-file dependency
    edits, evaluator runtime, validity/admission rates, and quality progress
    for a large multi-function or multi-file codebase before README, ROADMAP,
    or paper-index wording claims AlphaEvolve Table 1 code-scale parity.

- [ ] Add Table 1 capability-comparison exhibit provenance.
  - Spec evidence: AlphaEvolve Table 1 is a compact comparison of FunSearch
    and AlphaEvolve capabilities and typical behavior, with rows for function
    versus file/codebase evolution, code length, programming languages,
    evaluation duration/parallelism/accelerators, LLM sample counts, model
    scale, prompt context/feedback, and single versus multiple metrics.
  - Current evidence: code TODOs already track many individual Table 1 row
    gaps, including codebase-scale benchmarks, arbitrary-language runners,
    evaluator workload/budget provenance, sample-efficiency reports,
    Google/Gemini model-mix parity, rich prompt context, and multi-objective
    archive policy. They do not require Table 1 itself to be represented as a
    paper-facing exhibit with stable row ids, source PDF/caption location,
    row-to-gap mappings, implemented/partial/missing status per row, rendered
    table artifact hashes, or validation that README/ROADMAP summaries do not
    flatten the comparison into one broad capability claim.
  - Required result: add Table 1 exhibit metadata and validators with a stable
    table id, row ids/order, FunSearch/AlphaEvolve comparison text, source
    page/caption location, row-to-code/report/TODO mappings, implementation
    status for each capability row, rendered artifact paths/hashes, and docs
    that distinguish table-exhibit reproduction from satisfying each Table 1
    behavioral capability.

- [ ] Add Figure 1 and Figure 2 process-overview exhibit provenance.
  - Spec evidence: AlphaEvolve Figure 1 presents the high-level discovery loop
    from human-defined task, evaluation criteria, initial solution, and
    optional background knowledge through the LLM ensemble, prompt sampler,
    evaluator pool, and program database. Figure 2 expands that loop into the
    user-provided initial program/evaluation/config inputs and the controller
    steps that sample parent programs and inspirations, build prompts, generate
    diffs, apply diffs, execute evaluators, and register promising solutions.
  - Current evidence: LibreEvolve has implementation and TODO coverage for
    several individual Figure 1/2 components, including prompt construction,
    LLM ensembles, evaluator cascades, database admission, SEARCH/REPLACE
    diffs, and run manifests. No code/report schema preserves Figure 1 or
    Figure 2 as paper-facing process exhibits with stable figure IDs,
    diagram-node and edge labels, pseudocode-line mappings, source/caption
    locations, rendered diagram artifact hashes, or links from each displayed
    process step to concrete code, reports, and remaining TODO entries.
  - Required result: add Figure 1/2 exhibit metadata and validators with
    figure IDs, diagram node/edge records, pseudocode step IDs, source PDF and
    caption locations, rendered/text artifact paths and hashes,
    component-to-code/report/TODO mappings, and docs checks that prevent
    README, ROADMAP, or papers-index wording from treating component-level
    support as full reproduction of the AlphaEvolve process diagrams.

- [ ] Add self-improvement and distillation evidence boundaries for
      infrastructure-facing claims.
  - Spec evidence: AlphaEvolve's Discussion says the system made practical
    discoveries that increase the efficiency of its own infrastructure and
    future base LLMs, and identifies distilling AlphaEvolve-augmented
    performance into next-generation base models as a natural next step.
  - Current evidence: LibreEvolve records provider budgets, systems report
    schemas, benchmark/certification artifact inventories, and paper-facing
    background rows, but it does not model infrastructure components as
    versioned optimization targets for its own runtime, does not link an
    evolved optimization to a measured improvement in LibreEvolve's own
    execution path, and has no model-distillation or training-data export
    evidence tied to evolved candidates.
  - Required result: add explicit scope metadata and report contracts before
    claiming AlphaEvolve-style self-improving infrastructure or base-model
    uplift: target component identity, before/after runtime or cost metrics,
    deployment/adoption status, rollback/safety evidence, relation to the
    running LibreEvolve system, and, for distillation claims, dataset/export
    provenance plus training/evaluation evidence.

- [ ] Add self-improvement feedback-loop cadence and environment ROI
      provenance.
  - Spec evidence: AlphaEvolve's Discussion says current gains from improving
    its own infrastructure and future base LLMs are moderate, that feedback
    loops for improving the next AlphaEvolve version take months, and that
    those improvements should increase the recognized value of setting up more
    problems/environments with robust evaluation functions.
  - Current evidence: existing self-improvement TODOs require optimized
    component identity, before/after measurements, deployment/adoption,
    rollback/safety, and distillation artifacts. They do not require evidence
    for feedback-loop cadence, compounding improvement timelines, environment
    setup cost/value, or which new robust-evaluator environments became worth
    creating because prior AlphaEvolve-style improvements changed the
    economics.
  - Required result: add report metadata for self-improvement loop cadence and
    environment expansion: loop id, source optimization, affected next-version
    component, start/end dates or elapsed months, measured gain magnitude,
    setup and maintenance cost for new evaluator environments, expected and
    realized discovery value, gating assumptions, and docs checks that keep
    moderate/months-scale feedback-loop claims separate from generic
    self-improvement or distillation readiness.

## Prompt Sampling and Context

- [ ] Add primary-prompt instruction and target-solution provenance.
  - Spec evidence: AlphaEvolve Section 2.2 says the primary evolution prompt
    comprises multiple previously discovered solutions sampled from the
    program database plus system instructions on how to propose changes to a
    particular solution.
  - Current evidence: LibreEvolve records prompt templates, prompt ids,
    selected parent and inspiration ids, parent-code rendering diagnostics,
    mutation-instruction variants, section-budget hashes, and call telemetry.
    These surfaces do not yet provide a paper-facing prompt-core record that
    proves which solution was the target being edited, which previously
    discovered solutions were supporting context, which instruction block told
    the LLM how to modify that particular target, whether those instructions
    were delivered as provider system/developer/user role messages or only as
    part of one rendered prompt string, and whether required AlphaEvolve prompt
    ingredients were present or intentionally omitted.
  - Required result: add primary-prompt ingredient metadata and validators for
    each mutation call: prompt/call id, target solution/program id, target
    source hash, selected prior-solution ids and roles (`target`,
    `inspiration`, `feedback_source`, or equivalent), instruction policy id,
    instruction text hash/redaction status, provider message role placement
    (`system`, `developer`, `user`, or serialized-single-prompt), mutation
    mode/edit-scope constraints, required-channel presence/omission reasons,
    and README/ROADMAP checks that distinguish generic prompt-template
    rendering from AlphaEvolve-style instructions tied to a particular sampled
    solution.

- [ ] Add stochastic prompt-format distribution provenance.
  - Spec evidence: AlphaEvolve Section 2.2 says stochastic formatting uses
    template placeholders with human-provided alternatives for increased
    diversity, instantiated using probability distributions from a separate
    config file.
  - Current evidence: LibreEvolve supports `[[prompt:name]]` markers backed by
    `prompt_format_options`, validates non-empty alternatives and weights,
    samples with the run-local RNG, reuses the selected alternative for repeat
    occurrences in one prompt, records selection index/weight/source/text hash
    in prompt diagnostics, and redacts prompt-option text in startup manifests.
  - Remaining gap: there is no paper-facing stochastic-formatting report or
    validator that ties each rendered prompt/call id to the full normalized
    alternative distribution, the config-source identity for that distribution
    versus inline/effective config, the selected alternative and RNG boundary,
    and coverage proving that the formatting variation was human-authored
    problem-prompt diversity rather than an opaque prompt-template mutation.
  - Required result: add prompt-format distribution records and validators
    with option set id, config source/path/hash or explicit inline-source
    boundary, marker name, alternative indexes, normalized probabilities,
    selected alternative hash/index, weight override source, prompt/call
    linkage, RNG/replay boundary, and README/ROADMAP checks that distinguish
    implemented weighted markers from AlphaEvolve-style stochastic-formatting
    evidence.

- [ ] Add prompt-visible prior-score provenance for rendered evaluation
      results.
  - Spec evidence: AlphaEvolve Section 2.2 says rendered evaluation results
    include the program, execution result, and scores assigned by `evaluate`;
    Figure 3(c) shows prior programs preceded by named metric scores and an
    `average_score` summary before the code.
  - Current evidence: `PromptSampler` renders parent metrics through
    `{parent_metrics}` and inspiration headers with finite fitness plus
    declared metric entries, including role/direction/bounds/normalization
    annotations. Prompt histories and generated-program metadata can identify
    selected parents, inspirations, prompt ids, and prompt context policy.
  - Remaining gap: there is no paper-facing prompt-score record or validator
    proving that each prompt-visible prior/current program score header
    matches a specific evaluator/history row, that displayed scalar fitness
    maps to the paper's score-summary semantics, or that omitted/truncated
    execution outputs and score fields are explicitly attributed per prior
    solution.
  - Required result: add prompt prior-score records keyed by prompt call id,
    program role (`target`, `inspiration`, etc.), candidate/history id, source
    hash, raw metric names and values, normalized/maximized values, displayed
    aggregate score formula, evaluator-output/artifact linkage, omission or
    truncation reason, and validators/tests that fail when rendered prompt
    score summaries diverge from persisted evaluation history. Update README,
    ROADMAP, and papers index wording so current metric rendering is not
    mistaken for AlphaEvolve-style rendered-evaluation-result provenance.

- [ ] Add explicit-context source-role provenance for AlphaEvolve prompt
      context.
  - Spec evidence: AlphaEvolve Section 2.2 says users can tailor the primary
    evolution prompt with explicit context about the problem, including fixed
    human-written instructions, equations, code snippets, and relevant
    literature such as PDF files.
  - Current evidence: LibreEvolve can load and render local `.txt`, `.md`,
    `.py`, and `.pdf` context files with include/exclude rules, hashes,
    extraction spans, deterministic ordering/filtering, truncation, hidden
    context policy, and prompt-visible diagnostics. Those mechanics prove that
    bytes entered the prompt, but they do not classify why each source is
    relevant to the task or whether it is serving as human instruction,
    equation/formula context, code-snippet context, literature evidence, or
    another explicit-context role.
  - Required result: add context-source role metadata and validators for
    AlphaEvolve-style explicit context: source role
    (`human_instruction`, `equation`, `code_snippet`, `literature_pdf`,
    `background_reference`, or equivalent), problem/topic linkage, source
    section/page/span when applicable, prompt-inclusion decision, hash/redaction
    policy, and docs checks that distinguish local file-ingestion provenance
    from paper-facing evidence that explicit problem context was typed and
    intentionally supplied.

- [ ] Complete provider-token prompt section fitting beyond mutation prompts
      and async/pending-work budget composition.
  - Spec evidence: AlphaEvolve prompt sampling supports long contexts and
    configurable prompt construction; practical long-context evolution needs
    deterministic packing so parent code, inspirations, evaluator feedback,
    explicit context, plugin context, and failure memory fit the selected LLM.
  - Current evidence: `prompt_max_chars` provides an optional run-level
    rendered-prompt character cap before LLM calls, `prompt_max_estimated_tokens`
    provides an optional heuristic estimated-token cap using
    `ceil(rendered_chars / 4)`, and `LLMEnsemble` enforces both caps before
    scheduler/backend selection for mutation, critique, feedback, meta-prompt,
    registry-created, and custom backend roles. `PromptSampler` now
    deterministically omits oversized optional string prompt sections by
    priority before the effective final cap, leaves required AlphaEvolve
    channels intact, and records the packing decisions in
    `section_budget.packing` under policy
    `deterministic_section_priority_packing_heuristic_token_estimates_final_prompt_cap`.
    `section_budget` diagnostics with schema
    `libreevolve.prompt_section_budget.v1` include deterministic
    per-placeholder priorities, hashes, character counts, heuristic estimated
    tokens, required/optional totals, template overhead, required-section fit
    status, and packing status. Direct `PromptSampler` callers can now provide
    a manifest-safe `prompt_token_counter`; in that mode the section packer
    uses exact provider-token counts for `max_prompt_estimated_tokens`, records
    `token_count_policy: "provider_token_counter"`, `provider_token_counter`,
    `provider_tokens_*` totals, and per-decision exact token counts while the
    default path remains heuristic. The evolution loop now attempts mutation
    prompt-counter discovery across the eligible mutation backends before
    constructing `PromptSampler`: when every eligible backend shares a locally
    available OpenAI `tiktoken` counter, mutation prompt section packing uses
    that counter automatically; otherwise prompt diagnostics persist
    `prompt_token_counter_capability` with schema
    `libreevolve.prompt_token_counter_capability.v1` and the exact unavailable
    reason, such as a missing optional dependency or a provider with no local
    tokenizer registered. `LLMEnsemble.generate()` now performs the same
    role-scoped common-counter discovery at the final prompt boundary for
    mutation, critique, feedback, meta-prompt, registry-created, and custom
    roles. When all role-eligible backends share a local counter, the ensemble
    enforces `prompt_max_estimated_tokens` with exact provider-token counts and
    records `prompt_token_count_policy`, `prompt_provider_tokens`,
    `prompt_token_limit_count`, and the role-specific
    `prompt_token_counter_capability` in call telemetry; otherwise it records
    the unavailable reason and uses the heuristic estimate. Generated program
    history, failed-generation records, manifests, scheduler state, and LLM call
    history persist these diagnostics.
    `validate_prompt_section_budget_report()` now validates persisted
    `libreevolve.prompt_section_budget.v1` records for schema/policy shape,
    section counts, required/optional totals, section hash shape, packing
    decisions, cap-fit claims, and provider-counter boundary fields. LLM call telemetry and runtime accounting
    aggregate provider-reported token counts when adapters expose them, and
    `runtime.llm_budget_report` validates observed logical-call, retry,
    adapter-attempt, token, cost, wall-clock, and resume-state shapes while
    marking `paper_budget_ready: false`. `validate_llm_budget_evidence_bundle()`
    now checks LLM budget reports together with matching resume artifact
    inventory before accepting bundled paper-budget readiness. Provider-token
    discovery is still limited to optional local OpenAI `tiktoken` counters;
    selected-backend final prompt counting now covers critique, feedback, and
    meta-prompt roles when their eligible backends share that counter, but
    automatic provider-token section packing remains limited to mutation
    prompts, and provider usage is observed after calls rather than universally
    used for exact provider-token pre-call fitting.
    `cost_usd` is now populated from configured
    `backend_metadata.cost_usd_per_million_tokens` when provider usage exposes
    `total_tokens`, and `RunBudget` now enforces logical LLM calls plus a
    post-call `max_llm_provider_attempts` cap, a provider-reported
    `max_llm_tokens` cap, and a configured estimated `max_llm_cost_microusd`
    cap. Direct `evolve()` calls and CLI `--restore-budget-from-manifest` now
    apply prior runtime budget snapshots before new work, so restored
    provider-attempt, token, configured-cost, latency, and wall-clock usage can
    stop resumed runs through the same live checks.
    Backend specs and direct backend metadata can now include
    `prompt_max_estimated_tokens`; the ensemble applies the minimum applicable
    global/eligible-backend prompt-token cap before provider calls, using exact
    provider-token counts when role-scoped discovery succeeds and heuristic
    counts otherwise, and records effective/global/backend caps in call
    telemetry. Backend specs and
    direct backend metadata can also include `context_window_tokens` plus
    optional `reserved_output_tokens`; when present, the ensemble subtracts the
    reserve from the context window, applies that derived heuristic prompt-token
    capacity alongside global/backend prompt caps before provider calls, and
    records the window, reserve, and derived capacity in call telemetry. If a
    backend spec omits `reserved_output_tokens` but sets `max_tokens`, the
    output-token cap is used as the reserve.
    Final manifests now record
    `runtime.prompt_section_packing` with schema
    `libreevolve.prompt_section_packing_coverage.v1` and embedded
    `libreevolve.prompt_section_packing_coverage_validation.v1`. The record
    identifies mutation as the only current section-packed prompt role, lists
    critique, feedback, and meta-prompt as final-prompt-boundary-only, includes
    static-role token-counter capability diagnostics, and rejects complete
    provider-token section-packing overclaims.
  - Required result: make selected-backend exact token counters automatic for
    parent code, inspirations, explicit context, plugin context, evaluator
    feedback, and failure memory section-packing across all prompt roles,
    persist complete budget/resume state for token/provider-cost limits, and
    add tests for provider-specific oversized
    workspaces/context/plugins/inspirations/failure memory under configured
    backend/model context-window budgets. The remaining gap is automatic
    selected-backend provider-token section packing outside mutation prompts
    and budget/provider-output composition for future async or pending-work
    resume, not mutation-path optional OpenAI counter discovery, final-prompt
    selected-backend tokenizer discovery across LLM roles, validating persisted
    section-budget records, manifest-visible prompt section-packing coverage
    validation, LLM budget report/resume-artifact bundle consistency, or
    current synchronous provider-attempt/token/configured-cost/latency
    controller-event replay.

- [ ] Extend prompt-template compatibility beyond current mutation-template
  checks and duplicate-arm audit.
  - Spec evidence: AlphaEvolve-style prompt evolution should make prompt
    templates compatible with the roles and context channels that consume them,
    and should define whether identical prompt text is intentionally preserved
    as separate experimental arms or deduplicated as one prompt policy.
  - Current evidence: `validate_prompt_template()` enforces known simple
    placeholders, required generic prompt fields, and dry-run format
    compatibility. `validate_configured_prompt_template_semantics()` can require
    AlphaEvolve-style mutation channels for configured seeds unless
    `prompt_variant_semantic_policy: compatibility` is selected. Meta-prompt
    children cannot drop placeholders used by their selected parent, and
    duplicate configured or evolved templates are retained as separate prompt
    arms with deterministic ids plus `template_sha256` audit identity.
  - Required result: add explicit role-specific compatibility policy for
    mutation, critique, feedback grading, and meta-prompt surfaces; decide and
    test a prompt-program text deduplication or explicit no-dedup policy; and
    update README, ROADMAP, and paper TODO wording so duplicate template text is
    not mistaken for implemented prompt-program deduplication.

- [ ] Calibrate meta-prompt scoring beyond absolute/improvement child rewards.
  - Spec evidence: AlphaEvolve-style prompt evolution should justify prompt
    policy changes with calibrated reward signals and ablations that attribute
    improvements to prompt-program lineages rather than only latest child
    fitness.
  - Current evidence: `PromptDatabase` supports `absolute` and `improvement`
    reward modes, finite strictly increasing reward bounds, normalized prompt
    reward metadata, reward-policy compatibility checks during history replay,
    and UCB-style prompt-arm selection over mean normalized rewards. The loop
    records prompt rewards from child score or score-parent delta and includes a
    bounded prompt-performance evidence block in meta-prompt mutation requests.
  - Required result: add calibrated prompt reward signals, prompt-lineage
    ablation/report artifacts, and tests that distinguish prompt-policy effects
    from parent/program/evaluator noise before claiming AlphaEvolve-grade
    meta-prompt scoring.

- [ ] Promote the prompt-program store to a solution-database-equivalent
      evolutionary prompt database.
  - Spec evidence: AlphaEvolve Section 2.2 says meta-prompt evolution suggests
    instructions and context in an additional prompt-generation step,
    co-evolved in a separate database analogous to the solution programs.
  - Current evidence: `PromptDatabase` is a local deterministic prompt-arm
    store with append-only `prompt_history.jsonl`, lineage ids, UCB-style
    selection over normalized child-score rewards, prompt-history replay, and
    optional interval-based LLM template/context-policy mutation. It is not a
    prompt-side analogue of `ProgramDatabase` with MAP-Elites/island retention,
    durable prompt descriptor/objective indexes, migration/rebin semantics,
    prompt-specific archive events, or async/controller resume state.
  - Required result: before claiming AlphaEvolve-grade co-evolved prompt
    databases, define the prompt database's archive/retention policy, prompt
    descriptors/objectives, replay and migration semantics, prompt artifact
    events, and benchmark evidence showing the prompt database behaves as more
    than a local UCB prompt-arm selector.

- [ ] Extend structured prompt context policy beyond validated current fields.
  - Spec evidence: AlphaEvolve describes evolving prompt instructions/context,
    not just swapping one complete prompt string for another.
  - Current evidence: `PromptDatabase` now stores selected, scored,
    lineage-bearing prompt programs; prompt history records contain
    deterministic ids, template hashes, reward/penalty events, validated safe
    metadata, and meta-prompt mutation context. Configured and LLM-mutated
    templates are validated against the `PromptSampler` placeholder schema,
    strict AlphaEvolve template policy is available for configured seeds, and
    evolved children cannot drop placeholders used by their selected parent.
    Prompt programs now also persist validated
    `libreevolve.prompt_context_policy.v1` policy state separate from template
    text. `PromptSampler` applies that policy to disable optional rendered
    prompt channels, override deterministic section-packing priorities, and
    select a safe enum-valued `mutation_instruction_variant` (`default`,
    `minimal`, or `exploratory`) for rendered mutation-format instructions.
    `mutation_instruction_include_example` can keep or remove the built-in
    mutation-format example block while preserving the core format rules.
    `parent_metric_names` can select which safe metric entries render in the
    `{parent_metrics}` channel, including suppressing all parent metrics with
    an empty list, and `parent_metrics_max_chars_by_name` can cap or suppress
    individual parent metric entries by metric name before prompt rendering.
    `validate_meta_prompt_context_policy_capabilities()` now validates the
    meta-prompt-visible `libreevolve.meta_prompt_context_policy_capabilities.v1`
    map before evidence rendering, checking schema, section shape, duplicate
    fields, unsupported fields, and exact coverage of the current
    `libreevolve.prompt_context_policy.v1` keys.
    `parent_code_paths` can select and order safe mutable parent-workspace
    files before required `{parent_code}` rendering, `parent_code_required_terms`
    and `parent_code_excluded_terms` can filter those parent files by safe
    path/content terms, `parent_code_order_policy` can keep path order or rank
    selected parent files by deterministic task term overlap, and
    `parent_code_ranking_terms` can provide explicit safe ranking terms.
    `parent_code_limit` can cap how many ordered mutable parent files render,
    including `0` to suppress mutable parent file bodies while retaining
    diagnostics. `parent_code_max_chars_by_path` can cap individual rendered
    parent file bodies by safe candidate-relative path before the aggregate
    parent-code cap applies.
    `parent_code_max_chars`
    can cap or suppress that channel while retaining a prompt-visible omission marker and
    `libreevolve.parent_code_policy.v1` diagnostics with cap, source,
    nested requested/rendered/omitted/missing path policy, term-filter policy,
    order policy, render-count limit policy, per-file content cap policy,
    truncation mode (`head` or `head_tail`), truncation, character-count, and
    hash evidence.
    `proposal_metadata_enabled` can override whether proposal metadata
    instructions and downstream parsing run for that prompt arm while `null`
    preserves the run-level `capture_proposal_metadata` setting.
    It can also select rendered parent-feedback subsections with
    `feedback_sections`, including stage summaries, execution output,
    validator diagnostics/artifacts, program outputs, proposal metadata, and
    LLM grader feedback, and `feedback_section_order` can deterministically
    reorder those selected/rendered parent-feedback subsections while appending
    unspecified sections in default order. `feedback_section_max_chars_by_name`
    can suppress or cap individual rendered feedback subsections before the
    aggregate feedback cap. `inspiration_strategy` can override upstream
    inspiration sampling strategy for that prompt program using the same safe
    strategy enum as config. `inspiration_sample_count` can override the
    upstream sampled inspiration count before plugin context and prompt
    rendering, separately from the rendered inspiration cap.
    `inspiration_required_metric` can filter the upstream inspiration pool to
    programs carrying a manifest-safe metric name before plugin context and
    prompt rendering. `inspiration_excluded_metrics` can filter out upstream
    inspirations carrying any listed manifest-safe metric names before plugin
    context and prompt rendering. `inspiration_fitness_threshold` can filter
    upstream inspirations by finite fitness min/max bounds before plugin
    context and prompt rendering. `inspiration_metric_thresholds` can filter the upstream
    inspiration pool to programs whose numeric metric values satisfy safe
    min/max bounds before plugin context and prompt rendering.
    `inspiration_metric_ranking` can rank the upstream inspiration pool by a
    numeric metric in maximize/minimize order before final selection, and
    generated-candidate metadata records whether the strategy and requested
    count came from config or prompt context policy plus required-metric and
    threshold/ranking pool, match, filtered, ranked, and selected counts. `llm_feedback_fields`
    can further select rendered safe LLM-grader fields within that section, and
    `llm_feedback_max_chars_by_field` can cap or suppress those selected
    LLM-grader fields before rendering, and
    `proposal_fields` can select rendered safe proposal metadata fields, and
    `proposal_max_chars_by_field` can cap or suppress those proposal fields
    before rendering, and
    `stage_summary_fields` can select rendered safe stage-summary fields
    within stage-summary feedback, and `stage_summary_max_chars_by_field` can
    cap or suppress those stage-summary fields before rendering, and
    `execution_output_fields` can select rendered safe execution-output fields
    within execution-output feedback and stage-summary IO lines, and
    `execution_output_max_chars_by_field` can cap or suppress rendered
    `stdout`, `stderr`, and `error` text independently before those fields are
    included, and
    `sample_retry_fields` can select rendered safe sample/retry diagnostic
    fields, and `sample_retry_max_chars_by_field` can cap or suppress selected
    sample/retry diagnostic text fields before rendering, and
    `program_output_fields` can select rendered safe program-output fields
    within program-output feedback, and `program_output_max_chars_by_field` can
    cap or suppress selected program-output text fields before rendering, and
    `validator_artifact_fields` can select rendered safe validator-artifact
    fields, and `validator_artifact_max_chars_by_field` can cap or suppress
    selected validator-artifact text fields before rendering, and `validator_artifact_content_fields` can select nested bounded
    artifact-content fields, and `validator_artifact_content_mode`,
    `validator_artifact_content_max_bytes`, and
    `validator_artifact_content_max_chars` can override artifact-content
    rendering policy and caps, and `validator_skipped_artifact_fields` can select
    rendered safe skipped-artifact fields, and
    `validator_skipped_artifact_max_chars_by_field` can cap or suppress selected
    skipped-artifact text fields before rendering, and
    `validator_diagnostic_groups` can select rendered bounded validator
    diagnostic groups inside validator diagnostics, and
    `validator_metadata_keys` can select safe keys inside the validator
    metadata summary. `validator_metadata_limit` can cap or suppress the
    number of metadata-summary items before rendering.
    `validator_metadata_max_chars_by_key` can cap or
    suppress selected validator metadata summary values before rendering.
    `evaluator_workspace_fields` can select safe evaluated workspace
    provenance fields, including primary file, file count, and bounded file
    list, and `evaluator_workspace_max_chars_by_field` can cap or suppress
    selected workspace fields before rendering.
    `syntax_error_fields` can select safe fields inside
    syntax-error diagnostics, and `syntax_error_max_chars_by_field` can cap or
    suppress selected syntax-error text fields before rendering, and
    `metric_bound_fields` can select safe fields
    inside metric-bound diagnostics, and `metric_bound_max_chars_by_field` can
    cap or suppress selected metric-bound text fields before rendering.
    `configured_stage_check_fields` can select
    safe fields inside configured-stage check diagnostics, and
    `configured_stage_check_max_chars_by_field` can cap or suppress selected
    configured-stage text fields before rendering.
    `stage_metric_threshold_fields` and `artifact_output_check_fields` can
    select nested safe fields inside configured-stage metric-threshold and
    artifact-output checks, and `stage_metric_threshold_max_chars_by_field` can
    cap or suppress selected nested metric-threshold text fields before
    rendering. `artifact_output_check_max_chars_by_field` can cap or suppress
    selected nested artifact-output check text fields before rendering.
    `malformed_metric_fields` can select safe fields inside malformed-metric
    diagnostics, and `malformed_metric_max_chars_by_field` can cap or suppress
    selected malformed-metric text fields before rendering.
    `metric_aggregation_fields` can select safe fields inside
    metric-aggregation diagnostics, and
    `metric_aggregation_max_chars_by_field` can cap or suppress selected
    metric-aggregation text fields before rendering.
    `synthetic_metric_fields` can select safe fields inside synthetic
    failure-metric diagnostics, and `synthetic_metric_max_chars_by_field` can
    cap or suppress selected synthetic metric text fields before rendering.
    `materialization_error_fields` can select safe fields inside
    materialization-error diagnostics, and
    `materialization_error_max_chars_by_field` can cap or suppress selected
    materialization-error text fields, including typed reason/path fields,
    before rendering.
    `validator_boundary_fields` can select
    safe fields inside validator-boundary diagnostics.
    `validator_boundary_max_chars_by_field` can cap or suppress selected
    validator-boundary text fields before rendering.
    `validator_resource_limit_fields` can select nested safe resource-limit
    fields inside validator-boundary diagnostics, and
    `validator_resource_limit_max_chars_by_field` can cap or suppress selected
    nested resource-limit text fields before rendering.
    `validator_budget_fields` can select stage/sample budget diagnostic fields
    inside execution diagnostics, and
    `validator_budget_max_chars_by_field` can cap or suppress selected budget
    fields before rendering.
    `validator_env_fields` can select value-free validator environment
    diagnostic fields, and `validator_env_max_chars_by_field` can cap or
    suppress selected environment fields before rendering.
    `execution_diagnostic_groups` can select safe execution-diagnostic
    subgroups before subgroup field allowlists are applied.
    `validator_stdin_fields`
    can select safe fields inside validator-stdin diagnostics, and
    `validator_stdin_max_chars_by_field` can cap or suppress selected
    validator-stdin text fields before rendering.
    `diagnostic_output_fields` can select safe fields inside diagnostic-output
    diagnostics, and `diagnostic_output_max_chars_by_field` can cap or
    suppress selected diagnostic-output text fields before rendering.
    `timeout_cleanup_fields` can select safe fields inside
    timeout-cleanup diagnostics, and
    `timeout_cleanup_max_chars_by_field` can cap or suppress selected
    timeout-cleanup text fields before rendering.
    `prompt_format_weights` can override configured
    stochastic prompt-format alternative weights for safe configured markers.
    `context_source_paths` can select and order loaded local context sources
    by safe problem-relative path while recording missing and omitted paths.
    `context_source_max_chars` can cap rendered text for each selected local
    context source and records original, rendered, and omitted character counts
    per source. `context_source_truncation` can choose deterministic `head` or
    `head_tail` retention under that per-source cap.
    `context_source_order_policy` can keep selected source order or rank
    selected local context sources by deterministic task-term overlap against
    rendered source text while recording scores, query source, query-term
    hash/count, configured query terms when present, and a ranking hash.
    `context_source_ranking_terms` can provide explicit safe ranking terms
    instead of deriving them from the task description.
    `context_source_required_terms` can keep only sources whose
    loaded content contains every listed safe term, and
    `context_source_excluded_terms` can omit sources whose loaded content
    contains any listed safe term before ranking and limiting; diagnostics
    record required/excluded terms, omitted paths, match/filter counts, and a
    selection hash. `context_source_limit` can cap how many ordered local
    context sources render after path selection and ranking, including
    suppressing them with a zero limit, and records pre-limit order, omitted
    paths, selected count, omitted count, and a selection hash.
    `recent_failure_limit` can cap rendered recent failure-memory records,
    including suppressing that block with a zero limit, and records available,
    rendered, and omitted counts. `recent_failure_selection_policy` can choose
    `recent`, `oldest`, `lowest_score`, or `highest_repetition` retained
    failure-memory records before that render cap is applied, and records selector/selection
    semantics. `recent_failure_required_errors` can filter retained
    failure-memory records by exact safe `error` or `diff_error` labels before
    selection and limiting, and records required labels, match count, filtered
    count, and policy. `recent_failure_excluded_errors` can omit retained
    failure-memory records carrying exact safe `error` or `diff_error` labels
    before score filtering, selection, and limiting, and records excluded
    labels, filtered count, and policy. `recent_failure_required_changed_files`
    can filter retained failure-memory by safe exact `changed_files` paths
    before score filtering, selection, and limiting, and records required
    paths, match count, filtered count, and policy.
    `recent_failure_excluded_changed_files` can omit retained failure-memory
    carrying safe exact `changed_files` paths before score filtering,
    selection, and limiting, and records excluded paths, filtered count, and
    policy. `recent_failure_required_stage_names` can filter retained
    failure-memory by safe exact evaluation stage names, and
    `recent_failure_excluded_stage_names` can omit retained failure-memory
    carrying safe exact evaluation stage names before repetition/score
    filtering, selection, and limiting; diagnostics record required/excluded
    stage names, match counts, filtered counts, and policies.
    `recent_failure_required_terms` and `recent_failure_excluded_terms` can
    filter retained failure-memory by safe text terms in the failure evidence
    before repetition/score filtering, selection, and limiting, recording
    configured terms, match/filter counts, and policies when configured.
    `recent_failure_repetition_threshold` can filter retained
    failure-memory by integer `repetition_count` `min`/`max` bounds before
    score filtering, selection, and limiting, and records normalized bounds,
    match count, filtered count, and policy. `recent_failure_score_threshold` can filter retained
    failure-memory by finite score `min`/`max` bounds before selection and
    limiting, and records normalized bounds, match count, filtered count, and
    policy. `recent_failure_max_chars_by_field` can cap or suppress selected
    recent failure-memory fields before rendering.
    `inspiration_limit` can cap rendered selected
    inspirations, including suppressing all inspiration rendering with a zero
    limit, and records available, rendered, and omitted counts.
    `extra_context_max_chars` can cap already validated/redacted plugin
    `extra_context` text and records input, rendered, and omitted character
    counts. `plugin_context_enabled: false` can suppress plugin
    `build_extra_context()` and `prompt_context_metadata()` calls for a
    selected prompt arm while recording disabled per-plugin provenance.
    `plugin_context_allowlist` can select which plugin identity labels may run
    prompt-context hooks for that prompt arm; non-selected plugins are skipped
    before hook execution and receive deterministic per-plugin provenance.
    `plugin_context_excluded_labels` can omit selected plugin identity labels
    before prompt-context hooks run, recording
    `excluded_by_prompt_context_labels` visibility and the configured label
    policy.
    `plugin_context_order` can reorder selected plugin prompt-context sections
    by safe plugin identity labels before aggregate prompt packing.
    `plugin_context_required_terms` and `plugin_context_excluded_terms` can
    filter bounded plugin context text by safe terms before prompt visibility,
    recording selected status, missing required terms, matched excluded terms,
    and a selection hash.
    `plugin_context_ranking_terms` can rank prompt-visible plugin context
    sections by deterministic term overlap before render-count limiting,
    recording configured ranking terms, term hash/count, score, rank, previous
    rank, candidate count, and ranking hash.
    `plugin_context_limit` can cap how many ordered plugin context sections
    become prompt-visible after allowlist, term filtering, and ordering,
    recording source limit, pre-limit count, selected/omitted counts, rank,
    selected status, and a selection hash.
    `plugin_context_max_chars` can globally cap each plugin context section
    before prompt visibility, recording the global policy cap, per-label cap,
    effective cap, original character count, and prompt truncation status.
    `plugin_context_truncation` can choose deterministic `head` or
    `head_tail` retention under those plugin-context caps, and plugin-context
    records persist the applied content policy.
    `plugin_context_max_chars_by_label` can cap rendered plugin prompt-context
    text by plugin identity label before aggregate `extra_context_max_chars`
    prompt packing applies.
    Generated-candidate prompt diagnostics record the policy hash, selected
    instruction variant, selected inspiration strategy and sample-count
    overrides, selected feedback sections, feedback-section order, and
    per-section feedback caps, selected LLM-grader
    feedback fields, selected proposal fields, selected stage-summary fields, selected execution-output
    fields, selected sample/retry
    diagnostic fields and caps, selected program-output fields and caps, selected
    validator-artifact fields and caps, selected artifact-content nested fields,
    selected artifact-content policy overrides,
    selected skipped-artifact fields,
    selected validator diagnostic groups, selected validator
    metadata keys, selected syntax-error fields, selected metric-bound fields,
    selected configured-stage check fields, selected configured-stage nested
    fields, selected malformed-metric fields,
    selected metric-aggregation fields, selected synthetic metric fields,
    selected materialization error fields,
    selected validator-boundary fields,
    selected validator budget fields,
    selected validator resource-limit fields,
    selected execution-diagnostic subgroups, selected validator-stdin fields,
    selected diagnostic-output fields,
    selected timeout-cleanup fields, prompt-format weight
    overrides, context source selection, term filters, render-count caps,
    content caps, truncation policy, and ordering policy,
    recent failure-memory selection and text-term filtering, and inspiration selection, plugin extra-context
    cap diagnostics, plugin-context generation, allowlist, excluded-label policy, term filters, ranking terms, render-count limits, global plugin caps, truncation policy, and per-plugin cap
    policy, and replacement hashes; prompt history persists
    `context_policy` plus
    `context_policy_sha256`, replay validates policy hashes and immutable
    score/penalty policy state, and meta-prompt provider output can return a
    strict JSON object with a revised `template` plus optional
    `context_policy`.
    Meta-prompt mutation requests include bounded redacted prompt-performance
    evidence, prompt-program summaries, recent failure evidence, the current
    placeholder list, a compact context-policy capability manifest, per-prompt
    non-default context-policy previews, and a bounded current-template
    preview. Focused tests assert that meta-prompt evidence includes current
    context-policy values and the tunable policy surface under the redacted
    prompt-evidence cap. Final manifests now include
    `runtime.prompt_context_policy_coverage` with schema
    `libreevolve.prompt_context_policy_coverage.v1` and embedded
    `libreevolve.prompt_context_policy_coverage_validation.v1`, which verifies
    the current tunable field count/hash against
    `libreevolve.meta_prompt_context_policy_capabilities.v1`, records
    context-policy mutation and replay-hash support, and rejects full
    AlphaEvolve context-policy completeness overclaims.
    However, the policy currently controls only optional channel
    disabling, section-priority overrides, mutation-instruction variants,
    parent-metric selection/caps, and
    parent-feedback subsection selection, stochastic prompt-format weights, and
    local context source selection/term-filtering/ranking/render-count, recent failure-memory selection/rendering, upstream inspiration sampling
    plus safe required/excluded-metric, fitness-threshold, and metric-threshold filtering/ranking, selected-inspiration, plugin extra-context rendering limits, plugin-context enable/disable, allowlist/excluded-label selection, safe term filtering, deterministic term ranking, render-count limiting, global/per-label caps, ordering, and truncation shape.
    `PromptSampler` still obtains plugin
    retrieval/summarization behavior through fixed code/config
    paths.
    Meta-prompt mutation still cannot change retrieval/summarization policy,
    upstream inspiration selection policy beyond strategy, sampled count,
    required/excluded-metric filtering, fitness-threshold filtering, metric-threshold filtering, metric ranking, and rendered count,
    or deeper per-field policy inside selected validator diagnostic groups
    beyond metadata-summary key selection, parent-metric selection/caps, syntax-error field selection,
    proposal field selection,
    stage-summary field selection,
    execution-output field selection,
    sample/retry diagnostic field selection,
    program-output field selection,
    validator-artifact field selection,
    artifact-content nested field selection,
    artifact-content policy override selection,
    skipped-artifact field selection,
    evaluator-path field selection,
    evaluator-dependency field selection,
    evaluator-stage field selection,
    metric-bound field selection, configured-stage check field selection,
    configured-stage nested field selection,
    malformed-metric field selection, materialization-error reason/path field selection,
    metric-aggregation field selection,
    synthetic metric field selection,
    execution-diagnostic subgroup selection, validator-boundary field
    selection, validator budget field selection, validator resource-limit field
    selection, validator-stdin field selection, diagnostic-output field
    selection, execution-output, sample/retry, program-output, and validator-artifact field caps,
    and timeout-cleanup field selection.
  - Required result: extend prompt-program context policy beyond optional
    channel disabling, priority overrides, current character caps, parent-code
    file selection, term filtering, deterministic ordering, render-count
    limiting, and per-file content capping, and
    truncation-mode selection so safe configured or LLM mutations can change
    retrieval/summarization,
    plugin-context shaping beyond
    enable/disable/allowlist/excluded-label selection/order/safe term filtering/deterministic term ranking/render-count limiting/global and per-label caps/truncation, upstream inspiration selection beyond
    strategy/sample-count/required-metric-filter/excluded-metric-filter/fitness-threshold-filter/metric-ranking/render-count, context-source policy beyond exact path selection, safe required/excluded term filtering, task-term ranking, per-source char caps, truncation, and render-count, failure-memory selection beyond exact required/excluded error-label, required/excluded changed-file, required/excluded stage-name, repetition-count, and finite-score filtering plus recent/oldest/lowest-score/highest-repetition retained records, and deeper per-field evaluator-feedback controls beyond
    validator metadata summary keys, parent metric names/caps, syntax-error fields, proposal fields, stage-summary fields,
    execution-output fields and caps, sample/retry diagnostic fields and caps, program-output fields and caps, metric-bound fields,
    validator-artifact fields and caps, artifact-content nested fields,
    artifact-content policy overrides,
    skipped-artifact fields,
    evaluator-path fields,
    evaluator-dependency fields,
    evaluator-stage fields,
    configured-stage check fields, configured-stage
    nested fields, malformed-metric fields, materialization-error fields,
    synthetic metric fields, validator resource-limit fields, and metric-aggregation fields,
    execution-diagnostic subgroups,
    validator-boundary fields, validator-budget fields, validator-stdin fields, diagnostic-output
    fields, and timeout-cleanup fields;
    and test that those richer context-policy fields preserve
    template placeholder validation, deterministic replay, prompt diagnostics,
    and retention/redaction guarantees. The remaining gap is not
    manifest-visible coverage validation of the current meta-prompt-tunable
    policy surface.

- [ ] Persist unbounded raw retrieval evidence and learned ranking provenance.
  - Spec evidence: AlphaEvolve-style prompt context can include relevant
    literature and external context; reproducible experiments need to know not
    only which compact snippets were injected but also how sources were ranked
    and what source content was available at the time.
  - Current evidence: `DeepResearchPlugin` records bounded retrieval events and
    `runtime.retrieval` summaries. When a cache directory is configured, cache
    snapshots are written under the run directory and
    `run_artifacts_metadata()` reports snapshot count, file names, byte counts,
    per-file hashes, retention cap, skipped/read-error counts, bounded
    provider-result snapshot counts/hashes, and an aggregate hash. Retained
    sources include one-based retained rank, provider rank, source
    identity/content hashes, redacted URL transport expectations, and an
    aggregate ranking hash linked to the prompt-visible synthesis hash.
    Retained source rows now include
    `libreevolve.retrieval_source_grounding_policy.v1` lexical grounding
    records, and events/cache snapshots include an aggregate
    `source_grounding_policy` with source counts, lexically grounded source
    counts, and a records hash.
    Retained source rows with summary/content text include bounded/redacted
    `libreevolve.retrieval_source_content_snapshot.v1` snapshots with raw and
    stored hashes. Retained source rows also include
    `query_term_overlap_audit_v1` relevance scores based on deterministic query
    term/source text overlap. The default
    `source_ranking_policy="provider_order_retained_v1"` keeps provider order
    and marks relevance as audit-only. Opt-in
    `source_ranking_policy="query_overlap_score_desc_v1"` reorders retained
    sources by query-overlap score with provider rank as a tie-breaker; events,
    active prompt context, and cache snapshots record the policy, ranking hash,
    score hash, and `relevance_affects_order: true`. It also records
    `libreevolve.deep_research_active_context.v1` metadata for the exact active
    retrieval context injected into a candidate prompt, including
    generation/event index, synthesis/raw-result hashes, query hash, cache
    fields, retained-source ranking hash fields, and transport-policy status.
    Retrieval query inputs include bounded task-description, explicit-context,
    recent failure-history, local paper manifest title/id, best-program
    fitness/metric/code/file, and recent proposal-hypothesis terms. Retrieval
    events and cache snapshots retain bounded/redacted
    `libreevolve.retrieval_provider_result_snapshot.v1` provider-result
    snapshots with raw and stored hashes. When a cache directory is configured
    and retention mode allows text, live retrieval writes
    `libreevolve.retrieval_payload_artifact.v1` sidecars under
    `payload_artifacts/` for full secret-redacted provider payloads and retained
    source-content payloads that fit a 64,000-byte per-artifact budget; oversized
    payloads become metadata-only omitted artifacts, and `hash_only`/`off`
    record sidecar suppression.
    `libreevolve.retrieval_payload_artifact_inventory.v1` now verifies event
    or plugin-metadata sidecar references against an artifact root, including
    safe relative paths, file existence, SHA-256 hashes, byte counts, artifact
    schema, selected sidecar metadata, aggregate missing/mismatch/invalid
    counts, and a stable records hash.
    `libreevolve.retrieval_source_ranking_provenance.v1` now verifies event,
    metadata, or cache-snapshot retained-source ranking records by recomputing
    selected-source and query-relevance hashes, checking retained-rank
    sequence and source counts, and comparing synthesis hashes when retained
    synthesis text is available.
    `libreevolve.retrieval_semantic_boundary_audit.v1` now verifies event,
    metadata, or cache-snapshot retrieval evidence-boundary records and flags
    overclaims of semantic verification, full replay readiness, raw
    provider/source payload retention, TLS certificate-chain retention, or
    authoritative prompt context. It still does not store unbounded raw
    provider payload artifacts, unbounded source-content artifacts,
    learned/external semantic ranking scores beyond deterministic query
    overlap and lexical grounding, or a
    DeepEvolve-style hypothesis refinement/debug loop.
    `runtime.retrieval.evidence_coverage` now records
    `libreevolve.retrieval_evidence_coverage.v1` run-level counts for
    transport, payload-artifact, source-content, grounding, ranking,
    evidence-boundary, and context-audit policy coverage, with
    `libreevolve.retrieval_evidence_coverage_validation.v1` rejecting raw
    provider/source payload, semantic-verification, learned-ranking, TLS-replay,
    and full-replay overclaims.
  - Required result: persist replayable source-content artifacts beyond bounded
    retained-source snapshots and retention-budgeted redacted sidecars; add
    learned or externally scored semantic ranking/selection provenance beyond
    deterministic query-overlap ranking; link those artifacts from
    candidate metadata, cache snapshots, and run manifests; and add tests for
    successful, empty, malformed, oversized, and failed retrieval artifact
    paths. The remaining gap is unbounded raw provider/source payload
    persistence, semantic source-content verification beyond lexical grounding,
    learned/external ranking, and
    DeepEvolve-style hypothesis refinement/debug loops, not cache-snapshot
    summarization, bounded provider-result snapshots, bounded source-content
    snapshots, retention-budgeted redacted payload sidecars, active-context
    hashes, query grounding, lexical grounding records, audit-only relevance
    scores, retained source order/hash metadata, sidecar inventory
    verification, deterministic ranking-provenance validation, bounded
    semantic-boundary overclaim auditing, or run-level retrieval evidence
    coverage validation.

- [ ] Add semantic retrieval verification and replayable full-source evidence.
  - Spec evidence: external literature/retrieval context can directly shape
    candidate mutations, so AlphaEvolve-style prompt provenance should include
    trustworthy source transport and enough content integrity to audit what was
    injected.
  - Current evidence: the default arXiv provider uses HTTPS, validates query
    inputs, reads responses with a 1,000,000-byte cap before XML parsing, and
    records bounded transport status plus provider payload byte/hash metadata.
    Cache-backed runs persist bounded/redacted provider-result snapshots,
    retention-budgeted redacted payload sidecars, and manifest-visible cache
    snapshot summaries. `libreevolve.retrieval_payload_artifact_inventory.v1`
    verifies event or plugin-metadata sidecar references under an artifact
    root, including safe relative paths, file hashes, byte counts, sidecar
    schema, selected sidecar metadata, and aggregate inventory status.
    Retrieval events include
    `libreevolve.retrieval_transport_policy.v1`, which classifies HTTPS request
    state, redirects, HTTP status class, payload hash presence, oversized
    responses, missing custom-provider transport, and TLS/certificate-looking
    failures as audit-grade, degraded, or unauditable. Request URLs are stored
    as redacted/hash-backed summaries instead of raw URLs. Retained sources
    carry `retained_source_integrity_v1` identity/content hashes, URL transport
    expectations, provider/retained rank, bounded source-content snapshots, and
    source-ranking hashes linked to active prompt context. Opt-in
    `query_overlap_score_desc_v1` can make deterministic query-overlap scores
    affect retained source order.
    `libreevolve.retrieval_source_ranking_provenance.v1` verifies those
    deterministic retained-source ranking hashes for event records and cache
    snapshots. Retained sources now also carry
    `libreevolve.retrieval_source_content_trust_policy.v1`, classifying
    redacted payload sidecars, metadata-only oversized sidecars, bounded
    snapshots, hash-only evidence, and missing evidence; event-level trust
    policy records replayable-evidence counts and record hashes. Semantic
    integrity still remains limited to retained-source hashes, deterministic
    query-overlap scores, lexical grounding records, and redacted/hash-backed
    artifact evidence; transport
    policies explicitly list `tls_certificate_chain_not_retained` and either
    `semantic_content_integrity_not_verified` or
    `semantic_content_integrity_bounded_to_redacted_payload_artifacts`. Query
    events also include
    `libreevolve.retrieval_evidence_boundary_policy.v1`, explicitly documenting
    that raw provider/source payloads, TLS certificate chains, and semantic
    verification are outside the current retained-evidence boundary while
    linking payload-artifact, source-content, source-grounding, and transport
    evidence states. Successful retrieval events now also include
    `libreevolve.retrieval_context_audit_policy.v1`, which classifies the exact
    prompt-visible retrieval context as audit-grade bounded replay evidence,
    audit-grade bounded snapshot evidence, degraded evidence, or unauditable
    evidence while preserving `authoritative: false`. Focused tests now prove
    default arXiv bounded-snapshot evidence, unauditable custom string
    retrieval, and custom HTTPS transport plus replayable redacted source
    payload artifacts.
    `libreevolve.retrieval_semantic_boundary_audit.v1` verifies event,
    plugin-metadata, or cache-snapshot records preserve that bounded,
    non-semantic evidence boundary and fail records that claim semantic
    verification, full replay readiness, raw payload retention, retained TLS
    certificate chains, or authoritative prompt context.
    `libreevolve.retrieval_evidence_coverage.v1` now records manifest-level
    coverage counts for retained retrieval evidence surfaces and
    `libreevolve.retrieval_evidence_coverage_validation.v1` rejects raw payload,
    semantic-verification, learned-ranking, TLS-replay, and full-replay
    overclaims.
  - Required result: add unbounded raw provider-payload persistence, full
    source-content artifacts beyond the redacted byte-budgeted sidecars,
    replayable source-content verification, retained transport/TLS
    decision evidence, and stronger semantic source verification, not basic
    transport classification, bounded retained-source snapshots, bounded
    provider-result snapshots, query-overlap audit scores, request URL
    redaction, active-context hashes, redacted source-content trust policy, or
    evidence-boundary/context-audit policy records with lexical grounding
    aggregates, sidecar inventory verification, deterministic
    ranking-provenance validation, semantic-boundary overclaim auditing, or
    run-level retrieval evidence coverage validation.

## Evaluation

- [ ] Add a paper-facing evaluator metric contract that separates scored
      scalar metrics from LibreEvolve's local validity gate.
  - Spec evidence: AlphaEvolve Section 2.1 describes an evaluation function
    mapping a solution to scalar metrics, with metrics maximized by
    convention; the Figure 3 example shows a Python `evaluate(eval_inputs)`
    returning `dict[str, float]`.
  - Current evidence: LibreEvolve's evaluator contract deliberately requires
    every declared scalar metric plus a reserved boolean `is_valid` gate, and
    metric direction/bounds can be normalized before archive scoring. That is
    useful local contract hardening, but current paper-facing reports do not
    yet prove that `is_valid`, `outputs`, `program_output`, feedback fields,
    and direction transforms are excluded or normalized correctly when
    presenting AlphaEvolve-comparable scalar metric tables.
  - Required result: add a report/schema boundary for paper-facing evaluator
    metrics, including declared `paper_metric_names`, validity-gate source,
    maximize/minimize direction-to-maximized transforms, raw versus normalized
    score columns, and validation that `is_valid` and non-scalar attachments
    are not treated as scored AlphaEvolve metrics.

- [ ] Add independent evaluator-oracle composition provenance.
  - Spec evidence: AlphaEvolve's abstract says the evolutionary loop
    continuously receives feedback from one or more evaluators, while Section
    2.4 describes the user-provided evaluation function plus optional
    evaluation mechanisms such as cascades and LLM-generated feedback.
  - Current evidence: LibreEvolve has one configured local `CascadeEvaluator`
    path with optional stages/samples/thresholds and separate optional LLM
    feedback graders. Those surfaces can produce multiple stage results and
    feedback scores, but they do not define a paper-facing contract for
    independent evaluator/oracle sources, their authority, merge policy, or
    how conflicting evaluator results should affect candidate validity,
    scoring, admission, and prompt feedback.
  - Required result: add evaluator-oracle registry and report metadata with
    evaluator ids, oracle type (`deterministic_validator`, `statistical_test`,
    `reference_checker`, `llm_judge`, or equivalent), authority/role,
    input/output schema, metric ownership, conflict/merge policy, failure
    policy, prompt-feedback linkage, and README/ROADMAP checks that
    distinguish independent multi-evaluator feedback from local cascade stages
    or post-hoc LLM feedback graders.

- [ ] Add execution-grounded incorrect-suggestion filtering evidence.
  - Spec evidence: AlphaEvolve's introduction says its LLM-directed evolution
    is grounded in code execution and automatic evaluation, and that this
    evaluation mechanism lets AlphaEvolve avoid incorrect suggestions from the
    base LLM while using feedback to discover candidates that differ
    substantially from the initial pool.
  - Current evidence: LibreEvolve validates evaluator result structure,
    applies a local `is_valid` admission gate, records malformed-output and
    rejected-candidate diagnostics, and stores failure/quarantine streams.
    Those mechanics do not yet prove, in a paper-facing report, that incorrect
    LLM proposals were actually caught by execution/evaluation, excluded from
    accepted discovery claims, and fed back into subsequent search rather than
    merely failing parser or local admission checks.
  - Required result: add proposal-lifecycle evidence and validators linking
    each LLM suggestion to backend/model identity, parsed mutation payload,
    execution/evaluator outcome, validity/admission/retention status, rejection
    reason, evaluator-oracle sufficiency for the claimed task, prompt-visible
    feedback or failure-memory reuse, and aggregate false-acceptance/false-
    rejection review fields before claiming AlphaEvolve-style grounding that
    filters incorrect base-LLM suggestions.

- [ ] Add evaluator workload provenance for inner search and ML-training tasks.
  - Spec evidence: AlphaEvolve Section 2.1 says the evaluator can be simple,
    but in more complicated cases it may run an evolved search algorithm or
    train and evaluate a machine-learning model before returning scalar
    metrics.
  - Current evidence: LibreEvolve records configured evaluator paths, staged
    validators, subprocess attempts, samples, retries, seeds, evaluator
    budgets, artifact copy-out, problem-local dependency provenance, and
    bounded environment/package evidence. Those records show how a local
    validator was invoked, but they do not classify evaluator workload type or
    preserve paper-facing evidence for an inner search/training protocol:
    dataset identity and split, training/evaluation loop parameters, model
    checkpoint policy, random seeds, inner search budget, produced model or
    construction artifacts, and metric linkage to the candidate's returned
    scores.
  - Required result: add versioned evaluator-workload metadata and validators
    for `simple_check`, `inner_search`, `ml_training`, and related task shapes,
    including dataset/split hashes, training/search budget records,
    checkpoint/artifact policy, seed/retry semantics, score-field linkage, and
    report examples before claiming AlphaEvolve-style evaluator support for
    evolved search algorithms or model-training workloads.

- [ ] Add asynchronous evaluator workers and concurrent proposal control.
  - Spec evidence: AlphaEvolve parallelizes evaluation, often distributing
    work across many randomized initializations or accelerators, and its
    pipeline is optimized for throughput. Section 2.4 also ties parallel
    evaluation to keeping new generations fast enough for the evolutionary
    loop to apply several consecutive mutations when evaluator feedback would
    otherwise be slow.
  - Current evidence: `evolve()` is still a single synchronous proposal loop:
    it iterates `proposals_per_generation` sequentially, samples parents,
    builds one prompt, performs one mutation LLM call, applies one candidate
    mutation, and calls `CascadeEvaluator.evaluate()` directly before logging
    and archive admission. Generated candidates record
    `metadata.proposal_batch.policy == "sequential"`. Those batches are
    evaluated sibling candidates, not an adaptive chain of unevaluated or
    partially evaluated consecutive mutations from a slow-feedback parent.
    `CascadeEvaluator` remains a local staged subprocess evaluator, not
    distributed workers, and
    `RunBudget` explicitly tracks synchronous local consumption; controller
    budget-state validators exist only for future async/resume events.
    Completed manifests now embed
    `libreevolve.controller_state_validation.v1` under
    `runtime.history.controller_state.validation` to verify that the current
    controller boundary is terminal, synchronous, and drained, and to reject
    pending work or async/full-replay overclaims.
  - Required result: introduce an async controller with concurrent LLM
    samplers, evaluator workers, bounded queues, deterministic worker ids,
    deterministic result merge/admission order, concurrency-safe database,
    archive, prompt, plugin, and budget mutation, an explicit policy for
    mutation-chain depth under slow or expensive evaluator feedback, and
    replayable controller state for queued/running/completed work.

- [ ] Add statistical hypothesis-test gates to evaluation cascades.
  - Spec evidence: AlphaEvolve Section 2.4 describes the evaluation cascade as
    "hypothesis testing": candidates are first evaluated on small-scale tests
    and only promoted to harder/main test cases when earlier results are
    sufficiently promising. Section 3.1 also evaluates tensor-decomposition
    candidates across multiple randomized initializations, so promotion
    evidence should support confidence in noisy or seed-dependent results.
  - Current evidence: `CascadeEvaluator` supports ordered configured stages,
    `min_score`, per-metric thresholds, required program-output/artifact
    checks, samples, explicit seeds, retries, sample/stage wall-clock budgets,
    and diagnostic records. These are deterministic threshold and aggregation
    gates: there is no versioned statistical hypothesis-test policy,
    confidence interval or p-value evidence, sequential-test stopping rule,
    false-promotion/false-rejection budget, small-scale-versus-main-test
    labeling, or promotion report that proves a candidate advanced because a
    noisy sample set was statistically promising.
  - Required result: add a cascade promotion policy with explicit stage roles
    (`small_scale_filter`, `main_test`, etc.), statistical test configuration,
    retained per-sample observations, confidence or p-value records,
    sequential stopping diagnostics, and tests/report validation showing noisy
    repeated-seed candidates are promoted or rejected by a hypothesis-testing
    rule rather than only by fixed scalar thresholds.

- [ ] Add qualitative LLM-feedback criterion provenance.
  - Spec evidence: AlphaEvolve Section 2.4 says LLM-generated feedback can
    grade desirable characteristics that are difficult to capture precisely in
    the user-provided evaluation function, such as program simplicity; those
    grades can be added as scores to steer evolution or used to discard
    candidates when a criterion is not fulfilled.
  - Current evidence: `apply_llm_feedback()` supports configured graders,
    bounded/redacted full-workspace feedback prompts, JSON or explicit-score
    parsing, normalized score bounds/direction, weighted fitness deltas,
    `discard`, `min_score`, `include_invalid`, failure policies/retries, and
    `objective_metric: true` filling for declared non-primary
    `source: feedback` metrics. Runtime histories and manifests can expose
    bounded feedback records, and calibration-report validators can check
    declared grader calibration evidence. However, grader configs do not record
    the qualitative property being judged, why the property is hard to encode
    in `evaluate()`, whether the intended action is score augmentation,
    discard gating, or both, or how the grader rubric maps to the evaluator
    metric schema and prompt-visible evidence.
  - Required result: add versioned qualitative-feedback policy metadata and
    validation for each grader: criterion name/description, evaluator-gap
    rationale, rubric or prompt artifact hash, score-versus-discard intent,
    metric linkage, calibration/report linkage, prompt-history linkage, and
    tests/docs proving qualitative criteria such as simplicity are explicitly
    governed rather than implicit free-form grader prompts.

- [ ] Add unified expensive-evaluation compute budgets and resumable state.
  - Spec evidence: AlphaEvolve can spend hours or roughly 100 compute-hours on
    a single new solution when evaluation is parallelized.
  - Current evidence: local compute controls are now broader than the original
    60-second single-subprocess default: `Config` exposes `max_evaluations`,
    `max_evaluator_seconds`, detailed subprocess/sample/retry/timeout and
    budget-exhaustion caps, `max_runtime_seconds`, and logical
    `max_llm_calls`; configured evaluator stages support `timeout_sec`,
    `samples`, `retries`, `max_sample_seconds`, and `max_stage_seconds`.
    `RunBudget` records local seed/candidate evaluations, elapsed evaluator
    seconds, detailed evaluator counters, LLM calls, and generation counters;
    controller budget schemas can validate future async/resume events, and
    replayable `llm_call` controller events can now restore provider-attempt,
    token, configured-cost, LLM-latency, and role-scoped LLM usage counters.
    These remain cooperative local counters and preflight validators, not a
    unified compute-hour/resource budget for long-running worker or accelerator jobs.
  - Required result: add a unified expensive-evaluation budget model that can
    account for per-candidate compute-hours, worker/accelerator leases,
    CPU/memory/GPU quotas, token/cost/provider-attempt spend where evaluator
    feedback uses models, queued/running/completed long-evaluation state,
    evaluator-worker fan-out, randomized-initialization shard counts/seeds,
    compute-hour versus wall-clock compression, mutation-chain-depth impact,
    checkpoint/resume of partially completed expensive evaluations, and
    paper-grade equal-budget reporting; preserve the existing synchronous
    wall-clock/sample/stage budget tests as the local fallback contract.

- [ ] Add accelerator and worker budget stops plus budget resume state.
  - Spec evidence: AlphaEvolve Section 2.6 frames the system around maximizing
    useful ideas evaluated under an overall computation budget, and Section 4
    ablations report performance by fraction of the compute budget.
  - Current evidence: implemented live stop criteria are still local:
    `RunBudget` enforces generation, seed/candidate evaluation,
    evaluator-second, detailed evaluator-counter, wall-clock, `max_llm_calls`,
    `max_llm_provider_attempts`, `max_llm_tokens`, and
    `max_llm_cost_microusd`, and `max_llm_seconds` limits.
    `_generate_with_budget()` clamps
    ensemble retry/fallback attempts to the remaining logical-call budget and
    records the actual attempt delta. It also records provider adapter attempts
    from retained LLM call telemetry, provider-reported token totals, and
    configured estimated micro-USD cost, then stops before the next LLM call
    when those caps are exhausted. Candidate rows and final manifests persist
    consumed budget snapshots and structured stop reasons.
    LLM role accounting
    aggregates provider-reported token totals when available, and final
    manifests emit `runtime.llm_budget_report` with observed per-role logical
    calls, retry attempts, adapter/provider attempts, provider tokens, cost
    placeholders, scheduler-resume hashes, and self-validation. That report is
    still `paper_budget_ready: false` because accelerator and async-worker
    limits are absent and full controller resume wiring is still absent, but
    validated controller `llm_call` events can replay provider-attempt,
    token/cost, latency, and matching role counters into `RunBudget`, and
    prior manifest runtime budget snapshots can now be applied to live resumed
    runs before seed/generation work.
  - Required result: enforce accelerator, async worker/queue, and equal-budget
    limits as first-class
    live stop criteria with config/manifest schema, per-role/per-worker
    accounting, deterministic pre-call/pre-dispatch checks, post-call
    consumption updates, scheduler/controller resume state, and tests for
    exhausted limits before and after candidate generation and optional
    critique/feedback/meta-prompt calls.

## Metrics and Evolution Database

- [ ] Keep island-count claims scoped to configurable defaults.
  - Spec evidence: AlphaEvolve describes an evolutionary database inspired by
    MAP-Elites and island-based population models, but the local implementation
    must not present its default island count as a fixed runtime invariant.
  - Current evidence: `Config.n_islands` defaults to `5` but is validated as a
    configurable positive integer; tests instantiate `IslandModel` and
    `ProgramDatabase` with one, two, and three islands; migration uses the
    configured island count in a ring topology. The `IslandModel` docstring,
    README feature/comparison text, ROADMAP feature list, and AGENTS overview
    now say configurable island migration with a five-island default instead
    of implying a hardcoded five-island model.
  - Required result: if future work adds paper-specific island counts,
    adaptive island topologies, or non-ring migration policies, update code
    comments, README, ROADMAP, papers index, and matching TODO entries
    together so they neither underclaim the configurable default nor overclaim
    AlphaEvolve-specific island policy fidelity.

- [ ] Promote MAP-Elites descriptor modeling beyond insertion-time TF-IDF
  snapshot coordinates.
  - Spec evidence: AlphaEvolve-style quality-diversity search should use task
    meaningful behavior descriptors or explicitly stable descriptor models; if
    descriptors adapt during a run, the archive needs tested rebin/snapshot
    semantics so cells remain comparable.
  - Current evidence: `MAPElites` defaults to performance, serialized
    workspace complexity, and TF-IDF char-ngram diversity against the current
    capped elite list. `map_elites_descriptor_axes` can choose three axes from
    built-in performance/complexity/diversity, normalized evaluator metrics,
    numeric evaluator metadata, or numeric candidate metadata. State snapshots
    persist `descriptor_policy` and `descriptor_model` records with axes,
    performance/complexity bounds, current diversity reference ids, a revision
    counter, `dynamic_diversity_reference: true`, and rebin policy
    `no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots`.
    Restore validation rejects descriptor axes/model mismatches and rejects
    rebin overclaims such as `full_rebin`.
  - Required result: add evaluator-provided or learned descriptor models with
    stable versioning, explicit descriptor training inputs, tested full or
    partial archive rebin semantics, manifest-visible descriptor compatibility
    checks across restore, and reports that distinguish task behavior
    descriptors from local TF-IDF novelty heuristics.

- [ ] Promote multi-objective overlays to primary archive optimization.
  - Spec evidence: AlphaEvolve can optimize multiple user-provided scores and
    use diverse high-performing programs under different definitions of "good"
    in prompts.
  - Current evidence: evaluator/database/program records preserve metric
    vectors, primary fitness honors direction/bounds, declared numeric
    metrics are normalized into `metadata.normalized_metrics`, and optional
    finite non-negative per-metric `weight` values in `metrics.yaml` can drive
    a weighted `metadata.selection_score` instead of the default equal-weight
    mean. MAP-Elites replacement, elite ranking, and exploit/best sampling use
    that score with final fitness as a tie-break. Archive admission metadata and migration event rows now attach
    an `objective_vector` audit record with finite normalized metrics and the
    scalar selection policy, including weights when configured, when those
    metrics are available, and `show`
    validates and summarizes selected archive objective vectors for terminal
    inspection. Runtime manifests now include
    `runtime.history.objective_frontier`, a bounded diagnostic Pareto frontier
    over complete declared normalized metric vectors, plus
    `runtime.history.objective_metric_leaders`, a diagnostic best-program view
    for each declared normalized metric, and
    `runtime.history.objective_metric_archives`, a bounded top-program archive
    view for each declared normalized metric. Metric-leader parent and
    inspiration sampling can surface secondary-metric leaders, `frontier`
    parent/inspiration sampling can surface non-dominated retained programs
    with complete declared normalized metric vectors, `lineage`
    parent/inspiration sampling can cycle and render the best retained
    representative for each root lineage, and generated candidates now persist
    `metadata.parent_selection` and `metadata.inspiration_selection` provenance,
    including metric target/program pairs for metric policies and frontier
    size/metric-order metadata for frontier policies plus lineage-root metadata
    for lineage policies.
    Runtime manifests also include `runtime.history.lineage_index`, a bounded
    diagnostic best-valid-programs view grouped by root lineage with top
    retained programs, selection scores, fitness, lineage depth, and available
    objective-vector evidence. `runtime.history.descriptor_index` adds bounded
    top-program views for finite archive-admission descriptor values, including
    diversity/complexity/performance coordinates when those axes are present.
    `runtime.history.score_index` adds a bounded top-valid-program view ranked
    by archive selection score and final fitness with archive-admission and
    objective-vector evidence when present.
    `runtime.history.feedback_index` adds bounded feedback records grouped by
    LLM feedback grader, including finite score/delta values, discard/error
    status, objective-metric flags, retention summaries, and bounded text
    hashes/previews when feedback text is retained.
    `libreevolve.llm_feedback_calibration.v1` now validates declared feedback
    grader calibration reports across multiple tasks, per-grader/task scored
    records, normalized expected/observed scores, exact absolute-error
    consistency, and declared calibration artifacts. Its companion
    `libreevolve.llm_feedback_calibration_artifact_inventory.v1` verifies
    calibration report, raw-record, grader-config, and plot files under a safe
    artifact root. No runtime feedback-calibration runner emits these reports
    yet.
    Plugin score composition is logged separately and can change final fitness.
    Declared non-primary `source: plugin` metrics can be filled by plugin hooks
    through validated metric side effects and then enter
    `normalized_metrics`, metric-leader/frontier sampling, metric archive
    views, and `selection_score`. Declared non-primary `source: final_fitness`
    metrics are synthesized from the candidate's final composed fitness after
    plugin score hooks run, so plugin-adjusted top-level fitness can be
    included in the declared objective vector when desired; undeclared
    plugin-added metrics remain ordinary metrics without declared objective
    semantics. Each MAP-Elites archive now also keeps a bounded
    non-dominated retention archive over complete declared normalized metric
    vectors, records Pareto-only admission telemetry, persists/restores
    `pareto_frontier_program_ids` plus an `objective_archive_policy`, and
    includes those Pareto-retained programs in island metric/frontier retained
    pools. Each MAP-Elites archive now also persists/restores
    `metric_cell_archives`, per-declared-metric descriptor-cell overlays that
    retain the best program per complete normalized objective metric in each
    descriptor cell, record metric-cell admission telemetry, and include
    metric-cell-only programs in island metric/frontier retained pools. The
    runtime objective-history evidence is now self-checkable:
    `validate_objective_history_summary()` validates the multi-objective
    diagnostic history bundle across objective frontier, metric leaders, and
    metric archives, including schema/policy values, shared metric order,
    non-negative counters, retained-count and retention-limit consistency,
    normalized metric ranges, non-dominated retained frontier records, and
    explicit diagnostic-not-primary-archive limitation statements.
    `validate_map_elites_objective_archive_policy()` now validates
    `libreevolve.map_elites_objective_archive_policy.v1` snapshot records for
    bounded non-dominated retention, complete normalized declared-metric vector
    requirements, dominance/trim/sampling policy, metric order, retention
    bound, scalar-primary-cell plus metric-cell overlay semantics, and explicit
    rejection of primary Pareto/frontier cell-replacement overclaims. Backend
    reward, admission thresholds, and some parent/inspiration paths still use
    scalar final fitness, and the primary MAP-Elites cell grid still uses
    scalar selection score rather than Pareto/frontier dominance.
    `ProgramDatabase.resurface_candidates(target_metric=...)` now exposes
    declared-metric-targeted resurfacing over the objective metric archives,
    returning defensive ranked program snapshots while rejecting undeclared
    metric targets. `ProgramDatabase.resurface_by_metric()`,
    `resurface_by_lineage()`, `resurface_by_descriptor()`,
    `resurface_by_novelty()`, and `resurface_by_feedback()` now expose
    run-local defensive query results from the bounded metric, lineage,
    descriptor/novelty, and feedback index views.
  - Required result: represent full metric vectors, choose target metrics,
    support Pareto/frontier primary archive replacement, make durable
    metric-targeted resurfacing queryable across persisted database tables
    rather than only through bounded in-memory/archive snapshot overlays, and
    emit real LLM feedback calibration reports for reviewer/task suites rather
    than only validating declared calibration evidence.

- [ ] Add metric-diverse inspiration selection provenance for multiple-score
      prompts.
  - Spec evidence: AlphaEvolve Section 2.4 says multiple scores can improve a
    primary target because prompts can include examples of programs that excel
    under different evaluation criteria, each representing a different
    definition of "good".
  - Current evidence: LibreEvolve stores declared metric vectors, normalized
    archive selection scores, objective-vector diagnostics, metric leaders,
    metric-cell overlays, frontier/metric retained pools, and metric-targeted
    parent/inspiration strategies with selected ids and target-metric
    provenance. Prompt context policies can require, exclude, threshold, and
    rank inspirations by metric before rendering. However, no policy or report
    requires a single prompt to intentionally contain a metric-diverse slate of
    inspirations, records which metric niche each prompt-visible inspiration is
    meant to represent, or proves that rendered prompts condition the model on
    separate definitions of "good" rather than on one scalar or one configured
    metric target at a time.
  - Required result: add metric-diverse inspiration selection/report metadata:
    selected metric/objective, candidate id, score/rank, archive/source
    surface, reason for inclusion, prompt-history linkage, and tests/docs
    showing multi-score runs can deliberately condition the model on programs
    excelling under different metrics in the same prompt.

- [ ] Replace bounded run-local resurfacing indexes with a durable
  evolutionary database capable of resurfacing ideas by score, metric,
  diversity, feedback, and lineage.
  - Spec evidence: AlphaEvolve's program database optimally resurfaces
    previously explored ideas and balances exploration and exploitation.
  - Current evidence: `ProgramDatabase` is richer than the original thin JSONL
    facade: it validates strict accepted/failure/archive/LLM JSONL streams,
    records structured archive-admission outcomes, keeps defensive in-memory
    program snapshots, logs queryable failure records with repetition
    fingerprints, exposes recent failure and hypothesis context for
    DeepResearch, delegates metric/novelty/recency/selection/random sampling to
    `IslandModel`, persists compact and full archive-state snapshots, validates
    archive-event streams, supports lineage-aware live sampling through
    best-per-root retained representatives, persists a bounded lineage index
    view, score index view, descriptor index view, feedback index view, and a
    bounded `resurfacing_index` rank-fusion view in runtime manifests, exposes
    `resurface_candidates()` for defensive ranked snapshots from those same
    sources, exposes `resurface_by_metric()`, `resurface_by_lineage()`,
    `resurface_by_descriptor()`, `resurface_by_novelty()`, and
    `resurface_by_feedback()` for bounded run-local metric, lineage,
    descriptor/novelty, and feedback query results, persists
    `runtime.history.failure_index` grouped by failure
    fingerprint/repetition evidence, persists `runtime.history.hypothesis_index`
    for bounded redacted proposal idea/rationale/hypothesis summaries, includes
    hypothesis evidence in `resurfacing_index`, persists
    `runtime.history.artifact_index` for bounded evaluator-artifact path/hash,
    redaction, skipped-file, stage, and content-excerpt evidence, includes valid
    artifact-bearing candidates in `resurfacing_index`, and can restore
    cells/elites from a manifest plus accepted history bundle. Current
    evaluator `outputs` / `program_output` payloads are validated, redacted,
    truncated, can be required or checked by stage policies, and can be rendered
    as bounded prompt feedback, but they do not have a dedicated
    `program_output_index`, output-similarity query API, or resurfacing source
    separate from evaluator-artifact metadata.
    Current
    `manifest.json` files carry top-level `schema_version` and
    `artifact_schema` metadata, and current `history.jsonl`,
    `failure_history.jsonl`, `archive_events.jsonl`, `llm_calls.jsonl`,
    `prompt_history.jsonl`, and `controller_budget_events.jsonl` rows carry
    `schema_version` plus `record_schema`.
    `validate_resurfacing_index_summary()` now validates
    `libreevolve.resurfacing_index.v1` records for schema/policy, required
    limitation statements, source-count and retained-count consistency,
    manifest-safe program ids, finite scores, source contribution sums,
    supported source records, normalized objective evidence, and deterministic
    ranking order while keeping `durable_database_ready: false`. However, these
    are still append-only logs plus an in-memory archive and manifest-visible
    rebuilt indexes, not a persisted query/index database. There is no durable
    index over full metric vectors, feedback embeddings/full-text ranking,
    cross-run failure fingerprints, full lineage subgraphs, semantic/cross-run
    hypotheses, program-output values/schemas/similarity, full artifact
    content, retrieval context, or learned/cross-run novelty; the
    resurfacing index is deterministic rank fusion over bounded current-history
    views, and
    `load_accepted_history_index()` remains an id map for restore/query
    scaffolding rather than a ranked cross-run database. The compact `show`
    path now prints selected-row runtime status, lineage, prompt, evaluation,
    feedback, failure-count, objective-vector, and workspace-file summaries, and
    intentionally rejects mixed legacy/current history schemas with a
    line-numbered diagnostic instead of migrating them into one compatible
    database view. It also validates streamed current and legacy history-row
    `code`, `files`, and `primary_file` payloads, so malformed unselected rows
    fail before any best-looking row is printed. The remaining gap is not
    validation of the current bounded resurfacing-index record, the selected-row
    `show` summaries, or malformed unselected source/workspace payloads.
  - Required result: store rich candidate/evaluation records with queryable
    persisted dimensions, reproducible sampling policies, durable ranked views
    by score/metric/diversity/feedback/lineage/failure/hypothesis/artifact
    evidence, schema-versioned migration/compatibility rules for legacy/current
    run records,
    and tests proving resurfacing decisions can be rebuilt from persisted run
    artifacts rather than only from the live in-memory history/archive facade.
    Include first-class program-output indexing and output-aware resurfacing so
    AlphaEvolve-style program outputs attached to solutions are queryable
    evolutionary evidence rather than only prompt text or stage-threshold
    checks.

- [ ] Add exploration/exploitation sampling-balance reports for database
  resurfacing.
  - Spec evidence: AlphaEvolve Section 2.5 says the evolutionary database must
    balance exploration and exploitation so the search keeps improving the best
    programs while maintaining diversity across the search space.
  - Current evidence: `Config.explore_ratio` defaults to `0.3`, `mixed`
    parent selection chooses `explore` or `exploit` from the run-local RNG,
    explicit parent strategies can choose `exploit`, `explore`, `metric`,
    `frontier`, `lineage`, `novelty`, `recency`, `selection`, or `random`,
    inspiration sampling has related strategy controls, and selected parent /
    inspiration metadata is retained on generated candidates. MAP-Elites and
    island sampling can surface best programs, occupied cells, metric leaders,
    Pareto/frontier pools, lineage representatives, and descriptor/novelty
    records. These controls prove configurable sampling paths exist, but they
    do not prove the configured policy achieved an AlphaEvolve-style balance
    in a run.
  - Required result: add run/report artifacts that aggregate actual parent and
    inspiration sampling decisions by strategy, fallback, source pool,
    selected program, island/cell/metric/lineage/descriptor contribution,
    score improvement, diversity coverage, repeated-selection rate, and budget
    impact. Include validation and equal-budget comparison hooks so reports can
    distinguish pure exploitation, pure exploration, default mixed sampling,
    and metric/frontier/lineage variants before docs treat `explore_ratio` or
    strategy metadata as calibrated database-balance evidence.

- [ ] Add proposal scoring and semantic proposal-index retrieval beyond
  bounded hypothesis summaries.
  - Spec evidence: AlphaEvolve-style idea resurfacing should be able to judge
    proposal rationales, hypotheses, and prior idea families semantically, not
    only surface high-fitness programs that happen to carry proposal text.
  - Current evidence: mutation output can carry bounded `idea`, `rationale`,
    and `hypothesis` proposal metadata. `runtime.history.hypothesis_index`
    stores only valid programs with captured proposal metadata, ranks them by
    archive selection score/final fitness/generation/program id, and retains
    bounded redacted previews plus hashes for `idea`, `rationale`, and
    `hypothesis`. `resurfacing_index` can include those hypothesis records, and
    DeepResearch retrieval query context can use recent proposal-hypothesis
    terms. These are run-local manifest summaries rebuilt from current
    history, not persisted semantic indexes or proposal-quality scores.
  - Required result: add versioned proposal-score records, calibrated
    proposal-quality and novelty signals, semantic or embedding-backed
    proposal/hypothesis retrieval, cross-run persisted proposal indexes, and
    prompt/retrieval/archive policies that state exactly which proposal fields
    may influence resurfacing and future candidate generation.

- [ ] Add hypothesis backtracking and abandoned-branch evidence.
  - Spec evidence: AlphaEvolve's Introduction frames discovery as a prolonged
    process of ideation, exploration, backtracking on unpromising hypotheses,
    experimentation, and validation. Section 2.4 further describes pruning
    less-promising solutions through evaluation cascades before spending more
    budget.
  - Current evidence: LibreEvolve records malformed-output failures,
    evaluator rejections, admission outcomes, bounded failure-memory snippets,
    proposal `idea`/`rationale`/`hypothesis` metadata, and run-local
    hypothesis summaries for valid programs. Those records show individual
    failures and retained proposal text, but they do not identify a hypothesis
    branch as unpromising, record a deliberate backtrack to an ancestor or
    alternative idea family, or prove that later prompt/database sampling was
    redirected away from the abandoned line.
  - Required result: add versioned branch-level hypothesis state with proposal
    or idea-family ids, explored candidate ids, evaluator and cascade evidence
    that made the branch unpromising, abandonment/backtrack decisions,
    fallback ancestor or alternative-branch targets, prompt/failure-memory
    linkage, suppression or retry policy, resumed search outcome, and report
    validation before claiming AlphaEvolve-style backtracking on unpromising
    hypotheses rather than only logging rejected candidates.

- [ ] Add initial-pool syntactic and functional divergence reporting.
  - Spec evidence: AlphaEvolve's introduction says feedback-driven evolution
    enables discovery of candidates that are substantially different from the
    initial candidate pool in both syntax and function.
  - Current evidence: candidates retain parent ids, workspace hashes, changed
    files, archive novelty/descriptors, proposal metadata, and current-run
    resurfacing views. Those records can show ancestry and local novelty, but
    they do not compute or report distance from the initial candidate pool.
  - Required result: add versioned run/report fields that compare retained
    candidates against all seed/initial-pool programs with syntactic distance
    measures, changed component summaries, behavior/metric-vector distance, and
    evaluator-output or task-specific functional-difference evidence before
    claiming AlphaEvolve-style discovery distance from the starting pool.

- [ ] Add source/workspace deduplication and evaluation-cache policy.
  - Spec evidence: AlphaEvolve Section 2.5 describes a growing evolutionary
    database of generated solutions with scores and program outputs attached,
    whose purpose is to resurface previously explored ideas under fixed
    compute budgets. That does not require one specific cache key, but a
    faithful implementation needs an explicit policy for repeated identical
    programs: skip, reuse prior evaluation, or intentionally re-evaluate as a
    controlled stochastic sample.
  - Current evidence: generated candidate ids include generation coordinates,
    parent id, prompt-program id, mutation hash, and workspace hash, and
    `ProgramDatabase` rejects duplicate program ids before logging/admission.
    The evolution loop still evaluates seed and generated workspaces before
    any source/workspace deduplication gate. There is no run-local or durable
    index keyed by canonical workspace/source hash, evaluator contract,
    evaluator inputs, seed/sample configuration, static sidecars, or
    environment provenance; identical workspaces proposed through different
    parents, prompt arms, or mutation text can consume fresh evaluator budget
    without manifest-visible reuse/rejection telemetry.
  - Required result: add a versioned dedup/evaluation-cache policy that records
    canonical candidate source/workspace hashes, evaluator/config/cache-key
    scope, duplicate-detection timing, cache hit/miss/re-evaluation reasons,
    stochastic sample policy, budget-accounting effects, and replay semantics
    before presenting the program database as AlphaEvolve-grade fixed-budget
    memory over previously explored programs.

- [ ] Add an automated-evaluator scope policy for manual-experiment and
      LLM-only idea-feedback boundaries.
  - Spec evidence: AlphaEvolve says automated evaluation is both an advantage
    and a limitation: tasks requiring manual experimentation are out of scope,
    and its Discussion says LLM-provided evaluation of ideas is possible but
    not the optimized setting. The paper frames a future link to
    AI-Co-Scientist-style workflows as LLM feedback on high-level ideas before
    transitioning to an implementation stage with machine feedback through
    code execution. The Discussion also says AlphaEvolve's future value depends
    on setting up more problem environments with robust evaluation functions,
    so environment readiness is part of the claim boundary, not just local
    validator execution.
  - Current evidence: LibreEvolve problem execution is centered on local
    subprocess validators, staged evaluator results, optional LLM feedback
    graders after candidate evaluation, and bounded proposal
    `idea`/`rationale`/`hypothesis` metadata. It does not declare, validate,
    or report whether a task is machine-gradeable, requires manual
    experimentation, uses LLM-only idea review before code generation, or has
    a defined transition from natural-language idea feedback into executable
    candidate evaluation. It also does not record evaluator-environment setup
    provenance such as why the evaluator is robust enough for sustained search,
    which parts of the domain are automatable versus experimental, setup effort,
    or expected high-value discovery scope.
  - Required result: add versioned problem/run/report scope metadata for
    automated-evaluator availability, manual-experiment exclusion, optional
    LLM-only idea-feedback stages, transition criteria into executable
    code-evaluation feedback, and robust-evaluator environment readiness before
    claiming AlphaEvolve coverage for broader scientific-discovery,
    environment-scaling, or AI-Co-Scientist-style workflows.

- [ ] Add AI-Co-Scientist representation-boundary evidence.
  - Spec evidence: AlphaEvolve Related Work distinguishes AI Co-Scientist from
    AlphaEvolve by saying AI Co-Scientist represents scientific hypotheses and
    their evaluation criteria in natural language, while AlphaEvolve focuses on
    evolving code and directing evolution with programmatic evaluation
    functions. The paper says this choice substantially sidesteps LLM
    hallucinations and lets the evolution process continue for many time
    steps, while leaving a possible future combination of natural-language and
    programmatic idioms.
  - Current evidence: existing TODOs cover automated-evaluator scope,
    manual-experiment exclusion, optional pre-code idea feedback, structured
    proposal metadata, and local validation mechanics. They do not require a
    run/report boundary that classifies which candidate artifacts are
    executable programs versus natural-language hypotheses, which evaluation
    criteria are machine/programmatic versus language-only, or what evidence
    supports claims about hallucination resistance and long-horizon evolution.
  - Required result: add problem/run/report metadata and validators for
    representation mode (`code_candidate`, `natural_language_hypothesis`, or
    hybrid), evaluation-criterion mode, executable-feedback linkage,
    hallucination-risk controls, long-horizon step-count evidence, and any
    future bridge between natural-language hypothesis stages and programmatic
    candidate evaluation before claiming AlphaEvolve-style distinction from
    AI-Co-Scientist workflows.

- [ ] Add AlphaEvolve Related Work taxonomy and positioning evidence.
  - Spec evidence: AlphaEvolve Related Work frames the system as code
    superoptimization using execution feedback, situates it against
    enumeration, genetic search, Monte Carlo sampling, deep reinforcement
    learning, AlphaTensor, GPU-kernel agents, LLM multi-agent approaches, and
    broader AI-for-science systems, and says AlphaEvolve differs from most
    scientific-discovery methods through programmatic hypothesis
    representations and evaluation metrics. It also identifies adjacent
    LLM-guided evolution enhancements such as continuous LLM fine-tuning
    through reinforcement learning and LLM-directed concept learning over
    high-performing programs as complementary ideas needing more investigation
    at AlphaEvolve scale, and positions FunSearch-style witness/counterexample
    discovery as complementary to formal and informal proof search.
  - Current evidence: LibreEvolve has a PDF manifest and paper index with
    selected local inspiration papers plus feature-specific TODOs for
    FunSearch, AI-Co-Scientist, CodeEvolve, DeepEvolve, and benchmark domains.
    There is no schema or report that preserves AlphaEvolve's broader Related
    Work taxonomy, method-family comparisons, candidate-representation modes,
    evidence/evaluator modes, proof-versus-witness distinctions, or which
    related-work claims are local capability, background context, or explicitly
    unsupported.
  - Required result: add paper/reference taxonomy metadata and validators for
    related-work source ids, method families (`superoptimization`,
    `llm_algorithm_discovery`, `ai_for_science`, `proof_search`,
    `witness_discovery`, `llm_finetuning`, `concept_learning`, etc.),
    candidate representation, evaluator/evidence mode, task stage, comparison
    claim, complementary-mechanism status, local implementation status, source
    location, and README/ROADMAP wording checks so LibreEvolve does not
    overclaim AlphaEvolve's Related Work positioning from a flat paper list or
    isolated feature TODOs.

- [ ] Reconcile strict mutation-response parsing with AlphaEvolve explanatory
      preambles.
  - Spec evidence: AlphaEvolve Figure 3(c) shows an LLM response that starts
    with natural-language explanation about the current model before
    SEARCH/REPLACE diff blocks, while Section 2.3 defines diff blocks as the
    code-edit payload.
  - Current evidence: `apply_diff()` accepts compact and canonical
    SEARCH/REPLACE blocks and allows only structured leading
    `IDEA`/`RATIONALE`/`HYPOTHESIS` proposal metadata outside those blocks.
    Tests intentionally reject ordinary prose around a valid diff with
    `malformed_diff:unconsumed_text`, and full/workspace mutation paths also
    reject prose around block or file sections. The prompt currently says
    "No extra explanation" and README documents that text outside mutation
    sections must be proposal metadata.
  - Required result: decide whether AlphaEvolve-style explanatory preambles
    should be accepted, normalized into bounded proposal metadata, or remain
    a documented strict LibreEvolve divergence. If accepted, add parser tests,
    prompt wording, provenance/redaction policy, and TODO/README/paper-index
    updates that distinguish safe proposal rationale capture from arbitrary
    unparsed prose.

- [ ] Add prompt example-copy diagnostics for AlphaEvolve-style concrete diff
      examples.
  - Spec evidence: AlphaEvolve Figure 3(b,c) shows concrete current-program
    context and concrete SEARCH/REPLACE examples. The useful behavior is that
    the model edits the current program, not that it copies illustrative
    placeholder/example fragments from the prompt into a candidate patch.
  - Current evidence: LibreEvolve prompt instructions include concrete diff
    examples and README notes that those examples reduce observed
    placeholder-copying mistakes, but example-copying is not rejected by a
    dedicated validator. Current parser errors cover malformed diff/block
    syntax and unconsumed prose, not semantic evidence that a proposal copied
    prompt-only placeholders, toy identifiers, or example replacement text.
  - Required result: add a versioned prompt-example inventory and candidate
    acceptance diagnostic that hashes or labels illustrative prompt examples,
    detects copied example-only sentinels in submitted mutations, records
    bounded failure metadata, and tests diff/full/workspace mutation paths so
    prompt examples can remain useful without being mistaken for valid
    AlphaEvolve-style edits to the current program.

- [ ] Add cross-edit semantic consistency diagnostics for multi-block
      mutations.
  - Spec evidence: AlphaEvolve Figure 3(b) tells the model to keep proposed
    edits consistent with each other, giving the example that if one
    replacement uses a new config variable, another replacement should add
    that variable. This is part of the paper's SEARCH/REPLACE prompt contract,
    not merely generic coding advice.
  - Current evidence: `PromptSampler` includes a similar instruction, and the
    mutation paths validate diff syntax, exact search matches, topology
    envelopes, Python syntax, evaluator execution, and structured failure
    records. Those checks can catch some broken candidates after application
    or evaluation, but they do not provide a paper-facing diagnostic that a
    multi-block proposal was checked for cross-edit consistency, introduced
    symbol/config/dependency pairing, or intentional coupled changes across
    evolved blocks.
  - Required result: add versioned mutation-consistency evidence for
    multi-block edits: introduced and referenced symbol/config/import/resource
    labels where language support exists, changed-block dependency/co-change
    links, unresolved-reference or missing-companion-edit diagnostics,
    evaluator-failure taxonomy linkage, prompt/candidate ids, and README/
    ROADMAP wording that separates current prompt-only consistency guidance
    from AlphaEvolve-style evidence that accepted multi-edit proposals are
    internally coherent.

- [ ] Add Figure 3 supervised-learning example exhibit provenance.
  - Spec evidence: AlphaEvolve Figure 3 is a paper-facing supervised-learning
    pipeline exhibit with three linked subfigures: the user-provided JAX/Jaxline
    file and `evaluate(eval_inputs)` function, the assembled prompt containing
    prior/current program scores and abbreviated context, and the LLM's
    explanatory SEARCH/REPLACE output that edits the current program.
  - Current evidence: LibreEvolve tracks evolve-block parsing,
    SEARCH/REPLACE compatibility, prompt-context rendering, natural-language
    preamble divergence, and prompt-example copy diagnostics as separate
    behavior gaps. No code/report schema records Figure 3 exhibit IDs,
    subfigure labels, exact source/prompt/output excerpt artifacts and hashes,
    score values shown in the prompt, ellipsis/skipped-line policy, source PDF
    location, rendering/text artifact hashes, or links from the displayed
    example to prompt-history, evaluator, candidate, and run artifacts.
  - Required result: add Figure 3-style prompt/evaluation exhibit metadata with
    stable figure/subfigure IDs, source file/evaluate-function excerpt
    artifacts, rendered prompt excerpt artifacts, LLM-output excerpt artifacts,
    displayed metric values and candidate links, omitted-line/abbreviation
    policy, source/rendered artifact hashes, and links to prompt history,
    candidate history, evaluator results, and paper-source evidence so docs can
    distinguish feature support from reproduced paper example evidence.

- [ ] Add adaptive mutation-output mode selection instead of one run-wide
      `diff`/`full` contract.
  - Spec evidence: AlphaEvolve Section 2.3 says larger codebases request
    SEARCH/REPLACE diff blocks, while very short code or cases where complete
    rewrites are more appropriate can request the entire code block directly.
    That is a task/candidate-shape choice, not merely a static parser feature.
  - Current evidence: LibreEvolve implements both `diff` and `full` mutation
    modes, validates the mode through `Config.mutation_mode` and CLI
    `--mutation-mode`, renders matching `{mutation_mode}` and
    `{mutation_instructions}` prompt fields, and applies all candidates in a
    run with the same configured mode. It does not choose the mutation-output
    contract per problem, candidate size, file/block count, parent failure
    history, or model response quality, and it does not report why a candidate
    was asked for a diff versus a full rewrite.
  - Required result: add a versioned mutation-mode policy that can choose
    between diff and full-output contracts per candidate or prompt arm,
    including candidate-size/task-shape thresholds, prompt metadata,
    parser/critique fallback behavior, manifest/report telemetry, and tests
    proving large-codebase diff prompts and short-code/full-rewrite prompts
    are selected under documented AlphaEvolve-style conditions.

- [ ] Add mutation-operator construction policy beyond fixed local edit modes.
  - Spec evidence: AlphaEvolve Section 2.3 still uses structured edit
    payloads such as SEARCH/REPLACE or direct full-code output, but Related
    Work contrasts AlphaEvolve with classic evolutionary systems that require
    a fixed handwritten set of mutation and crossover operators. The paper
    frames the LLM as using world knowledge and prior solution ideas to
    construct useful program mutations, not merely selecting among
    predeclared local operator families.
  - Current evidence: LibreEvolve currently exposes a fixed mutation surface:
    configured `diff` or `full` response modes plus bounded full-workspace
    file/block and topology commands. Prompt templates can vary wording and
    proposal metadata, and future adaptive `diff`/`full` selection is tracked
    separately, but the run does not declare, generate, score, or report
    open-ended mutation-operator families such as targeted decomposition,
    algorithmic reformulation, data-structure substitution, multi-component
    refactoring, recombination, or benchmark-specific edit strategies. Any
    strategy must fit through the locally handwritten parser/operator grammar.
  - Required result: add a versioned mutation-operator policy/report that
    distinguishes the edit payload grammar from the higher-level mutation
    strategy, records which operator family a proposal attempted or generated,
    allows task/candidate/failure-aware operator construction or adaptive
    strategy selection, and includes tests plus benchmark telemetry before
    claiming AlphaEvolve's "no fixed handwritten mutation-operator set"
    related-work contrast.

- [ ] Add proposal-diversity and idea-novelty evidence for creative
      generation.
  - Spec evidence: AlphaEvolve Section 2.3 says SOTA LLMs digest previously
    developed solutions and propose new, diverse ways to improve them. The
    same section and later ablations frame model strength as part of the
    creative-generation claim, with performance improving as the underlying
    LLM improves.
  - Current evidence: LibreEvolve records prompt and call ids, selected parent
    and inspiration ids, proposal `idea`/`rationale`/`hypothesis` metadata,
    candidate history, admission outcomes, sampling strategy metadata,
    bounded hypothesis indexes, and backend/model telemetry. Existing TODOs
    separately track semantic proposal retrieval, initial-pool divergence, and
    higher-level mutation-operator families. Those surfaces do not prove that
    generated proposals within a call or batch are diverse improvement
    approaches rather than duplicates, near-duplicates, or minor variants of
    the same idea, and they do not relate proposal diversity to model/context
    quality.
  - Required result: add versioned per-call or per-batch proposal-diversity
    reports with idea/operator-family labels, code-distance and semantic or
    task-output distance where available, duplicate/near-duplicate detection,
    parent/inspiration relation, prompt/context/backend model ids,
    accepted/rejected status, novelty contribution, and equal-budget/model
    ablation linkage before claiming AlphaEvolve-style creative generation of
    new, diverse improvement approaches.

- [ ] Replay archive event logs as an ordered migration restore engine.
  - Spec evidence: AlphaEvolve's program database is an active evolutionary
    state, not just a candidate log; resuming, auditing, and comparing runs
    requires knowing which programs occupied which archive cells and how
    migration changed island populations.
  - Current evidence: `ProgramDatabase.log()` writes candidate records to
    `history.jsonl`, `ProgramDatabase.maybe_migrate()` writes versioned
    migration placement rows to `archive_events.jsonl`, and final manifests
    persist a compact `runtime.history.archive_state` snapshot with the island
    cursor, sequence counters, archive sequence by program id, and per-island
    occupancy/elite counts. `load_runtime_archive_state_snapshot()` validates
    that compact manifest field for future resume use, including cursor bounds,
    manifest-safe program ids, and per-island count records.
    `load_archive_event_records()` validates `archive_events.jsonl` as a
    checked migration audit stream, including sequence ordering, canonical-id
    policy, manifest-safe program ids, island ids, cells, and selection scores.
    `MAPElites.state_snapshot()` now persists per-island occupied cells,
    elite-program ids, descriptor policy metadata, and archive configuration
    under `runtime.history.archive_state.archive_contents`.
    `IslandModel.restore_archive_state()` restores those cells/elites when
    supplied with checked `Program` snapshots, and
    `load_archive_restore_bundle()` combines `manifest.json` with
    `history.jsonl` to produce the bundle accepted by `ProgramDatabase(...,
    archive_state_snapshot=..., archive_programs_by_id=...)` and by
    `evolve(..., runtime_archive_state_snapshot=...,
    runtime_archive_programs_by_id=...)`. CLI runs can now restore only the
    cursor/counter subset with `--restore-archive-cursor-from-manifest` or the
    full archive cells/elites bundle with `--restore-archive-from-manifest`.
    Runtime manifests now also include
    `runtime.history.archive_event_replay_audit`, which validates
    `archive_events.jsonl`, replays the final admitted migration placement per
    target island/cell, and compares that audit-only partial event view against
    `archive_contents`, reporting verified or superseded/missing placements.
    `validate_archive_event_replay_audit()` now validates that audit result
    before manifest use, including schema/status, audit-only and
    no-restore-engine flags, event and placement count consistency, retained
    mismatch shape, mismatch retention limits, verified/absent status
    invariants, and required audit-boundary limitations.
    Remaining gap: `archive_events.jsonl` is still not applied as a full
    migration restore engine.
  - Required result: implement an ordered `archive_events.jsonl` replay engine
    or extend the current audit-only reconciliation model into a restore
    branch, prove replayed placements match the archive-content snapshot or
    fail with actionable diagnostics across normal admission replacement
    cases, and add restore/replay tests covering migration ordering,
    replacement, duplicate-placement, and descriptor-policy mismatches.

- [ ] Add async/pending-work controller resume state for archive restores.
  - Spec evidence: AlphaEvolve-style evolutionary databases should make
    population-state updates auditable and reproducible; a candidate that does
    not enter the archive should not silently change future island assignment
    unless that is an intentional search policy.
  - Current evidence: retained-state-change behavior is explicit: island
    assignment advances only when `event["search_state_changed"]` is true, and
    compact/full archive-state restore now exists. Final manifests persist
    `runtime.history.archive_state` with cursor/counter state, full
    `archive_contents` cell/elite snapshots, and a validated
    `migration_replay` policy that marks migration events as
    `not_applied_as_restore_engine`. `load_runtime_archive_state_snapshot()`,
    `load_archive_restore_bundle()`, `IslandModel.restore_cursor_state()`,
    `IslandModel.restore_archive_state()`, `ProgramDatabase(...,
    archive_state_snapshot=..., archive_programs_by_id=...)`, direct
    `evolve()`, and CLI flags can restore cursor-only or full archive
    cell/elite state before new seed/candidate admission. Startup manifests
    record `policies.archive_cursor_restore` and
    `policies.archive_identity.resume_status` so restored surfaces and
    unsupported migration replay are visible. Completed runtime manifests now
    include `runtime.history.controller_state`, a terminal drained-state
    snapshot for the synchronous controller with zero queued/running proposals,
    evaluations, in-flight LLM calls, and pending archive admissions at
    finalization plus a compact `controller_budget_events.jsonl` stream
    summary. `libreevolve.controller_state_artifact_inventory.v1` now verifies
    that terminal controller event stream against the manifest artifact record
    and disk file, including safe relative path checks, file existence,
    SHA-256, byte count, strict JSONL event count, last sequence/kind,
    per-record status, and a stable records hash.
    `libreevolve.controller_state_validation.v1` is embedded in the
    controller-state snapshot to verify the terminal drained synchronous
    boundary and flag pending-work or async/full-replay overclaims.
  - Remaining gap: migration event-order replay is tracked separately by the
    archive-event replay TODO. The terminal synchronous controller boundary is
    visible, but async/mid-run controller state and pending/in-flight work are
    still absent from the restore surface: no queued/running proposal records
    for async workers, evaluator-worker state, in-flight provider outputs,
    pending archive admissions, partially completed generation state, or
    deterministic mid-generation controller resume ledger is persisted or
    restored. The remaining gap is not terminal controller event-stream
    artifact verification or terminal drained-state validation.
  - Required result: add controller/pending-work resume state and extend
    end-to-end resume tests across below-threshold, non-admitted, elite-only,
    in-flight generation/evaluation, and cell-replacement cases.

## Benchmarks and Problem Fixtures

- [ ] Pin AlphaEvolve source-PDF version metadata in paper manifests.
  - Spec evidence: page 1 of the local `2506.13131__AlphaEvolve.pdf` source
    identifies the audited paper as `arXiv:2506.13131v1 [cs.AI] 16 Jun
    2025`.
  - Current evidence: `papers/download_manifest.*` and
    `libreevolve.tools.paper_manifest` preserve paper id/title, the floating
    `https://arxiv.org/pdf/2506.13131.pdf` URL, local file path, download
    status, byte count, SHA-256 digest, and optional PDF readability. They do
    not record the source arXiv version/date/category extracted from the PDF
    header, distinguish floating arXiv URLs from version-pinned source URLs,
    or tie claim audits to a specific paper version. Existing Appendix B
    TODOs cover revised result constants, not source-PDF identity.
  - Required result: extend paper-manifest schema and validation for
    versioned source identity: arXiv id, version, category, posted date,
    source URL kind (`floating` versus `version_pinned`), expected header
    text/page, local PDF hash, and claim/TODO evidence links that make clear
    which source version each AlphaEvolve audit row used.

- [ ] Validate paper-manifest row identity across id, URL, and local file.
  - Spec evidence: paper-cache rows are the source ledger for AlphaEvolve
    audit evidence. A row should not only have a safe id, URL, and filename;
    those fields must describe the same paper source before claim audits rely
    on the cached PDF.
  - Current evidence: `libreevolve.tools.paper_manifest` validates row id
    grammar, allowed HTTPS source hosts, safe `papers/<name>.pdf` paths,
    CSV/JSON agreement, duplicate ids/files/hashes, and optional local
    PDF byte/hash/readability. `_validate_paper_url()` currently checks host
    safety but does not extract an arXiv id from `/pdf/<id>.pdf` or `/abs/<id>`
    paths, compare it with the manifest `id`, or require the local filename
    stem to carry the same source id. For non-arXiv allowed hosts or
    foundational slug ids, there is no explicit source-identity mapping that
    proves the URL, row id, and file label belong together.
  - Required result: add row-identity validation that parses arXiv ids from
    source URLs, compares URL id, manifest id, and local file stem/source-id
    prefix, rejects mismatches, and requires explicit source-id metadata for
    non-arXiv or slug rows. Keep this distinct from source-version metadata:
    version pinning identifies which revision was audited, while row-identity
    validation prevents cross-paper URL/file/id drift before version checks.

- [ ] Add AlphaEvolve source-PDF license/copyright provenance.
  - Spec evidence: page 1 of `2506.13131__AlphaEvolve.pdf` states
    `© 2025 Google DeepMind. All rights reserved`.
  - Current evidence: `papers/download_manifest.*`,
    `libreevolve.tools.paper_manifest`, and the new source-version TODO track
    paper identity, floating URL, local path, byte/hash metadata, and expected
    header/version evidence. They do not record the cached source's copyright
    holder, copyright year, rights statement, arXiv/license terms, or
    redistribution/use boundary for paper-derived excerpts and reproduced
    tables/figures. The project README states LibreEvolve's own MIT license and
    non-affiliation, but that is distinct from the rights metadata for cached
    AlphaEvolve source PDFs.
  - Required result: extend paper/source manifests and validators with
    source-rights metadata: rights holder, copyright year, rights statement or
    license id/text, source location/page, retrieval URL, excerpt/reproduction
    use policy, and docs wording that separates LibreEvolve's repository
    license from third-party paper-source rights before paper-derived artifacts
    are treated as publication-ready evidence.

- [ ] Add AlphaEvolve References-section bibliography provenance.
  - Spec evidence: `2506.13131__AlphaEvolve.pdf` includes a numbered
    References section beginning after Author information and running through
    entry `[120]`, with citations used across the abstract, method, results,
    related work, and Appendix B.
  - Current evidence: `papers/README.md` warns that manifest `title` values are
    inventory/display slugs, not authoritative bibliographic titles. Active
    TODOs capture targeted citation gaps such as matrix baseline reference ids,
    Appendix B prior-source provenance, related-work implementation status, and
    source-PDF version/rights metadata. They do not require a complete
    AlphaEvolve bibliography map with reference number, title, authors, venue,
    year, DOI/URL/arXiv id, source page/span, and claim links. As a result,
    docs can cite selected references without proving that every paper citation
    used by the AlphaEvolve audit is normalized and traceable.
  - Required result: extend paper-source manifests or companion registries with
    a full AlphaEvolve reference table: stable reference id, bibliographic
    fields, DOI/URL/arXiv metadata, source page/span, citation-use categories,
    local-cache linkage where present, missing-cache status where absent, and
    validation that README/ROADMAP/papers wording distinguishes authoritative
    bibliography metadata from manifest display slugs and targeted per-claim
    citation TODOs.

- [ ] Add companion Colab/source-artifact tracking for AlphaEvolve results.
  - Spec evidence: `2506.13131__AlphaEvolve.pdf` says the discovered
    algorithms and new mathematical results are available in the accompanying
    `google-deepmind/alphaevolve_results` Colab notebook, and Table 2 points
    to that Colab for the matrix decompositions shown in the paper.
  - Current evidence: `papers/download_manifest.*` and
    `libreevolve.tools.paper_manifest` track PDF sources, byte counts,
    SHA-256 digests, README status-table consistency, optional local PDF
    readability, and benchmark registries. The manifest does not track
    companion notebooks or public result repositories. Existing matrix and
    Appendix B TODOs ask for local Colab-equivalent construction exports, but
    they do not preserve the actual AlphaEvolve companion notebook URL,
    retrieval status, content digest, version/commit, notebook-cell-to-claim
    mapping, or source-artifact checks that tie local Appendix A/B evidence
    back to the paper's public result artifact.
  - Required result: extend paper/source-artifact manifests and validation for
    non-PDF companion result artifacts: canonical URL/repository/ref,
    retrieval policy, SHA-256/byte metadata, notebook readability checks,
    claim-to-cell or claim-to-artifact mapping for matrix and Appendix B
    results, and README/papers-index wording that distinguishes external
    AlphaEvolve source evidence from LibreEvolve's own generated
    Colab-equivalent exports.

- [ ] Add companion-result notebook selection-scope provenance.
  - Spec evidence: the `google-deepmind/alphaevolve_results` README says the
    repository's `mathematical_results.ipynb` contains mathematical
    discoveries and correctness-verification code, but only for instances
    where AlphaEvolve outperformed the state of the art. It explicitly excludes
    problems where AlphaEvolve matched, but did not outperform, the best known
    constructions, and states that the repository does not contain the code to
    run AlphaEvolve.
  - Current evidence: companion Colab TODOs require URL/ref/digest,
    notebook-readability checks, and claim-to-cell mapping, while Appendix A/B
    TODOs require result rows and verifier/code exports. They do not require a
    source-selection policy that distinguishes notebook-covered improved
    results from paper-reported matched results, nor a report field that
    explains why a paper claim may be absent from the companion notebook.
  - Required result: add companion-artifact selection metadata and validators:
    source repository URL/ref, notebook path, inclusion policy
    (`outperformed_sota_only`), excluded/matched-result policy, per-claim
    notebook coverage status, absence reason, runtime-code availability
    boundary, license/source notes, and README/ROADMAP wording that separates
    paper result coverage from the intentionally filtered companion notebook.

- [ ] Add companion-result repository rights and disclaimer provenance.
  - Spec evidence: the `google-deepmind/alphaevolve_results` README states
    `Copyright 2025 Google LLC`, licenses software under Apache License 2.0,
    licenses other materials under CC-BY 4.0, includes an as-is disclaimer, and
    says the repository is not an official Google product.
  - Current evidence: active TODOs track the cached AlphaEvolve PDF rights and
    require generic license/source notes for companion artifacts. They do not
    preserve the companion repository's dual software/materials license split,
    rights holder, disclaimer text/source location, or the non-official-product
    boundary as separate source-use evidence. Without that, generated
    notebooks, copied verifier code, figures, or construction data could be
    treated as if they inherit either the paper PDF rights or LibreEvolve's MIT
    license.
  - Required result: add source-rights metadata for companion repositories:
    repository URL/ref, rights holder/year, software license, non-software
    materials license, disclaimer/as-is text, official-product disclaimer,
    artifact-type-to-license mapping, allowed reuse/reproduction policy, and
    README/ROADMAP wording that distinguishes companion-source licensing from
    the cached PDF rights and the local project license.

- [ ] Add follow-on AlphaEvolve math-scale paper/repository source tracking.
  - Spec evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says more
    examples and method details for the constructive-math problems would be
    provided in an upcoming paper. Current primary-source evidence shows that
    paper as arXiv `2511.02864`, `Mathematical exploration and discovery at
    scale`, last revised as v3 on 2025-12-22, and its
    `google-deepmind/alphaevolve_repository_of_problems` repository says it
    contains 67 problem descriptions plus Google Colab notebooks with prompts,
    verification code, initial programs, final evolved programs, and
    visualization or analysis code where available.
  - Current evidence: the local paper manifests and `papers/README.md` include
    `2506.13131` and the original companion-Colab TODO, but they do not include
    arXiv `2511.02864`, a cached PDF/digest row, repository URL/ref/digest,
    per-problem source inventory, notebook availability/readability checks, or
    a mapping from the original paper's Appendix B/Section 3.2 claims to the
    expanded 67-problem follow-on evidence.
  - Required result: extend paper/source manifests and validators for the
    follow-on math-scale paper and repository: arXiv id/version/date, PDF
    cache row and SHA-256, repository canonical URL/ref/commit, live-repository
    status policy, problem ids, notebook/prompt/verifier/final-program artifact
    metadata, license/source notes, and README/ROADMAP wording that separates
    the original AlphaEvolve specification from later expanded math evidence.

- [ ] Add follow-on problem-repository coverage-state provenance.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README describes the repository as live, with plans to expand and improve
    it over time. It says the repository contains problem pages for all 67
    mathematical problems and Colab notebooks for many, but not all, problems,
    with prompts, verification code, initial programs, final evolved programs,
    and visualization/analysis code where appropriate. It gives the hosted
    problem-page URL pattern
    `https://google-deepmind.github.io/alphaevolve_repository_of_problems/problems/{n}.html`,
    says no installation is required, and says notebooks can be opened in
    Google Colab while webpages can be opened in any browser. The README's
    distribution graphic points to root-level `status_grid.png`, and the
    repository tree also exposes root-level status artifacts such as
    `status.json` and `result_distribution.png`. Current `status.json` uses
    explicit buckets `world_record`, `former_record`, `worse_than_record`, and
    `matched_optimal`, listing 43 problem ids total.
  - Current evidence: broad follow-on source TODOs require a repository ref,
    live-update policy, problem ids, notebook metadata, and prompt/verifier/
    final-program presence. They do not require per-problem coverage states
    distinguishing mandatory problem pages from partial notebook availability,
    hosted-page URL validation, browser/Colab access modes, missing-notebook
    reasons, artifact-presence matrices, root-level status-artifact
    provenance, parsed status-bucket semantics, explicit handling for the
    problem ids absent from `status.json`, or snapshot-date semantics for a
    live repository that can change. Earlier coverage wording also used
    unverified `assets/...` paths instead of the README's root-level status
    artifact path.
  - Required result: add a follow-on repository coverage manifest and
    validators with repository URL/ref/commit/date, live-update policy, all 67
    problem ids, hosted page URL, page path/hash, notebook path/hash or absence
    reason, access mode (`browser_page`, `colab_notebook`, or absent),
    artifact presence flags for prompt/verifier/initial/final/visualization/
    analysis, root-level status artifact paths/hashes such as
    `status_grid.png`, `status.json`, and `result_distribution.png` when used,
    parsed status bucket membership, an explicit `unclassified` or
    `not_listed_in_status_json` state for problem ids absent from those
    buckets, and README/ROADMAP wording that separates complete problem-page
    coverage from partial notebook/artifact/status coverage at a pinned
    snapshot.

- [ ] Reconcile follow-on numbered problem-page inventory with README count.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README says the repository contains problem descriptions for 67
    mathematical problems, but the current `problems/` directory exposes 68
    numbered HTML pages. The live raw pages include both `problems/67.html`
    and `problems/68.html` titled `Logic puzzles`; `67.html` uses a Colab link
    placeholder `#`, while `68.html` uses a generic
    `https://colab.research.google.com/` URL and a paper-link placeholder `#`.
  - Current evidence: follow-on coverage TODOs require all 67 problem ids,
    hosted page URLs, notebook paths or absence reasons, status buckets, and
    access modes. They do not require a numbered-page inventory check that
    reconciles repository file count with README/paper problem count, detects
    duplicate titles/sections, or flags placeholder/generic resource links in
    individual pages.
  - Required result: add repository-page inventory validation with repository
    URL/ref/commit/date, discovered numbered HTML files, expected problem-count
    policy, duplicate title/section detection, page id-to-paper section
    mapping, placeholder/generic link diagnostics for Colab and paper links,
    and README/ROADMAP wording that distinguishes paper-declared problem count
    from live repository page inventory until the source discrepancy is
    classified.

- [ ] Add follow-on problem-repository rights and attribution provenance.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README asks users of the package's code or data to cite
    `Mathematical exploration and discovery at scale`, declares
    `Copyright 2025 Google LLC`, licenses software under Apache License 2.0,
    licenses other materials under CC-BY 4.0, includes an as-is disclaimer,
    says it is not an official Google product, credits Professors Javier
    Gomez-Serrano and Terence Tao with supervision, problem selection, review,
    analysis, and commentary, and identifies Problem 65 as originating from
    the official IMO problems website.
  - Current evidence: existing follow-on TODOs require generic license/source
    notes and coverage manifests, while earlier rights TODOs are scoped to the
    original `alphaevolve_results` companion repository and the cached PDF.
    They do not require a separate rights, citation, role-attribution, and
    source-origin row for the problem repository's webpages, notebooks,
    verifier code, data, figures, and problem statements.
  - Required result: add follow-on problem-repository source-use metadata and
    validators with repository URL/ref/commit/date, citation/BibTeX metadata,
    rights holder/year, software license, materials license, license URLs,
    artifact-type license mapping, as-is and non-official-product disclaimers,
    contributor-role attribution notes, Problem 65 IMO source URL, and
    README/ROADMAP wording that separates these repository terms from the
    original AlphaEvolve PDF, the `alphaevolve_results` repository, and
    LibreEvolve's own license.

- [ ] Add follow-on problem-repository runtime-absence provenance.
  - Spec evidence: the `google-deepmind/alphaevolve_repository_of_problems`
    README says each notebook contains the prompt, verification code, initial
    program, final evolved programs, and visualization/analysis code where
    appropriate, but explicitly says the repository does not contain the code
    to run AlphaEvolve.
  - Current evidence: companion-result notebook TODOs track runtime-code
    absence for the original `alphaevolve_results` repository, and follow-on
    coverage TODOs track notebooks, prompts, verifiers, and final programs.
    They do not require a separate runtime-availability boundary for the later
    67-problem repository, so notebooks could be misdescribed as runnable
    AlphaEvolve experiment drivers rather than source artifacts around already
    run experiments.
  - Required result: add runtime-availability metadata for the follow-on
    problem repository with repository URL/ref/commit/date, per-notebook
    artifact kinds, explicit `alphaevolve_runtime_available=false`, absence
    reason/source span, verifier-versus-runtime classification, and
    README/ROADMAP wording that separates prompt/verifier/final-program
    evidence from executable AlphaEvolve runtime code.

- [ ] Add Terence Tao follow-on blog source provenance and claim boundaries.
  - Spec evidence: Terence Tao's November 5, 2025 post
    `Mathematical exploration and discovery at scale` says the arXiv paper is
    a longer report on experiments done with Google DeepMind's AlphaEvolve
    tool, links the follow-on repository with prompts and tool outputs, and
    summarizes 67 mathematics problems with positive and negative outcomes.
    It adds source-specific observations not in the local manifests: scale,
    adaptability, interpretability, verifier-exploit behavior, the need for
    non-exploitable verifiers using exact or interval arithmetic and
    conservative bounds, one-sided limitations for open conjectures, systematic
    negative-result recording, parameterized-code generalization, and proof
    handoffs involving human proof work, Deep Think, AlphaProof, or later
    papers.
  - Current evidence: follow-on TODOs track arXiv `2511.02864`, the DeepMind
    problem repository, notebook coverage, rights, and runtime absence. They do
    not require a separate source row for Tao's blog post, nor a claim-boundary
    policy distinguishing blog commentary and anecdotal lessons from the
    audited paper/repository artifacts.
  - Required result: add source metadata and validators for the Tao blog:
    canonical URL, author, post date, title, retrieval/hash data, linked arXiv
    and repository ids, claim categories (`commentary`, `experiment_summary`,
    `verifier_design_lesson`, `negative_result`, `proof_handoff`,
    `future_work`), source spans, paper/repository cross-links, and
    README/ROADMAP wording that treats blog-only claims as secondary evidence
    unless backed by pinned paper, repository, notebook, verifier, or proof
    artifacts.

- [ ] Add AlphaEvolve theoretical-CS proof-element source tracking.
  - Spec evidence: Google Research's September 30, 2025 AlphaEvolve
    theoretical-CS article and arXiv `2509.18057`, `Reinforced Generation of
    Combinatorial Structures: Applications to Complexity Theory`, use
    AlphaEvolve to discover finite combinatorial structures/proof elements for
    hardness results, including MAX-k-CUT gadget reductions and Ramanujan
    graph constructions. The source describes lifting finite structures into
    universal statements, automatically verified proof elements, AlphaEvolve
    acceleration of expensive verification, and final brute-force verification
    of discovered gadgets.
  - Current evidence: the local manifests, paper index, and AlphaEvolve TODOs
    track the original AlphaEvolve PDF, the original result Colab, Appendix A/B
    math evidence, and the later 67-problem math-scale repository. They do not
    track this distinct theoretical-CS/proof-element application surface,
    including its source article, arXiv paper, finite-structure artifacts,
    lifting-framework boundary, verifier-speedup claims, or final independent
    verification policy.
  - Required result: extend paper/source manifests and validators for the
    theoretical-CS AlphaEvolve source: Google Research article URL/date,
    arXiv id/version/date/PDF cache, source repository or artifact links if
    available, problem/result ids, finite proof-element or graph/gadget
    artifact metadata, lifting-framework statement, verifier-speedup and
    correctness evidence, final brute-force verification provenance, and
    README/ROADMAP wording that separates original AlphaEvolve specification,
    expanded constructive-math evidence, and later proof-element applications.

- [ ] Add official DeepMind AlphaEvolve blog-source provenance and claim
      reconciliation.
  - Spec evidence: the May 14, 2025 Google DeepMind article `AlphaEvolve: A
    Gemini-powered coding agent for designing advanced algorithms` is an
    official public source for the project scope. It says AlphaEvolve combines
    Gemini models with automated evaluators and an evolutionary framework,
    goes beyond single-function discovery to evolve entire codebases, reports
    deployed systems impacts, links the white paper and mathematical-results
    Colab, and includes blog-specific claim wording such as a production Borg
    heuristic for over a year, `weeks` of kernel-engineering effort reduced to
    days, `up to a 32.5%` FlashAttention speedup, Early Access/user-interface
    plans, and blog-post acknowledgement/illustration roles.
  - Current evidence: this ledger lists the DeepMind blog as primary evidence,
    and existing TODOs track many underlying paper claims. No source manifest
    or report schema records the blog URL/date/title, content digest, outbound
    white-paper/Colab links, blog-only availability/early-access statements,
    acknowledgement/illustration roles, or value/text variants between the
    blog and white paper such as `32.5%` versus `32%` FlashAttention speedup
    and `weeks` versus `months` of kernel-engineering effort.
  - Required result: extend source-artifact provenance for official non-PDF
    AlphaEvolve sources: blog URL, publication/update date, title, retrieval
    hash, linked white-paper/Colab targets, claim ids, claim text/value/unit,
    claim source (`blog`, `white_paper`, `both`), variant/reconciliation
    status, acknowledgement/illustration role metadata, and README/ROADMAP
    wording that distinguishes official announcement claims from audited
    white-paper specification and reproduced LibreEvolve evidence.

- [ ] Add validation for paper-index TODO coverage cross-references.
  - Spec evidence: AlphaEvolve-alignment work relies on paper-facing status
    rows being traceable to concrete missing-behavior ledgers. The local
    `papers/README.md` "TODO coverage cross-references" section claims to map
    implementation-status rows to active and completed/grouped backlog
    evidence.
  - Current evidence: `validate_paper_manifest()` reconciles manifest rows,
    README counts, the implementation-status table, Appendix B registry, and
    Figure 8 ablation registry. A checked-in test confirms every manifest id
    appears once in the TODO coverage section and mentions `docs/todo/`, but
    no reusable validator checks the cross-reference table's row shape,
    duplicate/extra ids, referenced path existence, active-versus-completed
    classification, grouped-gap labels, whether active references still map to
    open TODO content, or whether stale grouped labels remain after a row gains
    source-specific open TODO entries.
  - Required result: extend paper-manifest or paper-index validation with a
    TODO-coverage cross-reference checker: parse the table, require exact
    manifest-id coverage, reject duplicates/extras, validate safe existing
    `docs/todo/` paths, classify active and completed evidence targets,
    allow only declared grouped-gap labels, flag grouped-only references when
    source-specific open TODO entries exist for the same paper id, and
    optionally verify that active evidence rows contain matching open backlog
    text. Keep docs wording clear that status-table validation is not the same
    as verified backlog traceability.

- [ ] Validate semantic cells in the paper implementation-status table.
  - Spec evidence: `papers/README.md` says manifest `title` values are only
    inventory/display slugs and that the implementation-status table is the
    paper-facing authority for titles, roles, implementation status, and
    benchmark coverage decisions. AlphaEvolve-alignment audits therefore rely
    on those cells as structured claim boundaries, not only as row ids.
  - Current evidence: `_read_status_table_ids()` in
    `libreevolve.tools.paper_manifest` parses the `## Implementation status`
    table only far enough to collect the first cell, detect duplicate ids, and
    reconcile id coverage against `papers/download_manifest.json`. It does not
    validate the header shape, title and role cells, allowed role/status
    taxonomy, implementation-status wording, smoke-versus-paper-claim
    qualifiers, benchmark coverage terms, row length, or links from semantic
    status phrases to the active TODO/code evidence that justifies them.
  - Required result: add a reusable paper-status-table validator that parses
    all four columns, rejects malformed row shape/header drift, checks
    manifest-id coverage and duplicate/extra ids, validates title/role/status
    cells against a declared taxonomy, detects overclaims such as smoke
    examples presented as AlphaEvolve-comparable benchmarks, and links
    status/coverage phrases to active TODO or completed-evidence records. Keep
    this separate from TODO-coverage cross-reference validation, which tracks
    the later backlog-reference table rather than the semantic status cells.

- [ ] Add paper-artifact creator and assembler provenance for figures and
      companion notebooks.
  - Spec evidence: the AlphaEvolve Contributions section says N.V., E.D.,
    M.E., S.C., A.N., and A.Z.W. created the paper figures, and F.J.R.R.,
    A.M., and A.Z.W. assembled the accompanying Google Colab.
  - Current evidence: TODOs already require figure/exhibit metadata, rendered
    artifact hashes, companion Colab URL/ref/digest records, claim-to-cell
    maps, and local Colab-equivalent exports. They do not require any code or
    paper-source manifest schema to preserve artifact-role provenance for who
    created a figure or assembled a companion notebook, what artifact each role
    applies to, or how that role evidence is tied to the PDF Contributions
    source location.
  - Required result: extend paper artifact manifests or exhibit/notebook
    provenance records with source-role metadata: artifact type, figure/table/
    notebook id, creator or assembler role, responsible initials/names,
    source PDF section/page, artifact digest/link, and docs wording that
    distinguishes byte-level artifact verification from paper-attributed
    artifact authorship.

- [ ] Connect benchmark-grade fixtures to hardening and scope reports.
  - Spec evidence: AlphaEvolve's matrix-multiplication work searches tensor
    decompositions, measures rank over target families and randomized seeds,
    and verifies exactness; its packing work reports concrete best
    constructions and compares progress under ablations.
  - Current evidence: `matrix_multiplication` is a 2x2 Python function example,
    not a rank-decomposition search or operation-instrumented benchmark. Its
    smoke validator now counts AST `*` nodes only inside `matmul2`, expands the
    deterministic integer case set, and rejects known import/library
    delegation, module-level dead-code counter, and fixed-three-case lookup
    shortcuts. The packing validator checks fixed-26 circle feasibility and sum
    of radii, but there is no benchmark runner that records best construction
    artifacts, target thresholds, repeated seeds, or equal-budget comparisons.
    `libreevolve.benchmark_hardening.v1` now defines and tests an anti-gaming
    report contract with protected signals, shortcut threat categories,
    detector strategies, required links from each shortcut threat to known
    protected signals, passed negative fixtures, safe artifact paths/hashes,
    and benchmark-readiness gating that requires a passed negative fixture for
    every declared shortcut threat.
    `libreevolve.benchmark_hardening_artifact_inventory.v1` now verifies
    negative fixture and hardening artifact records against concrete files
    under an explicit artifact root, checking safe relative paths, existence,
    SHA-256 hashes, byte counts, per-record statuses, and aggregate
    missing/mismatch/invalid counts. `libreevolve.example_benchmark_scope.v1`
    now machine-classifies the shipped `hello_world`, `sorting`,
    `workspace_math`, `matrix_multiplication`, and `circle_packing` examples as
    smoke-only and not AlphaEvolve-comparable, preventing those fixtures from
    being counted as benchmark evidence by accident. The `workspace_math`
    smoke fixture now exercises a nested package, declared JSON data, and a
    binary static seed asset while preserving its smoke-only scope. That scope
    registry has unit coverage and is consumed by smoke hardening bundles, but
    the routine paper-manifest/docs validation gate does not yet validate the
    shipped registry directly.
    `validate_benchmark_evidence_scope()` now cross-checks hardening reports
    against the matching scope record and optional hardening artifact inventory,
    rejecting smoke-only example promotion, paper-claim scope mismatches, and
    inconsistent inventory evidence. The checked Appendix B registry is still a
    family-coverage ledger rather than a constructive-math benchmark contract:
    twelve families remain `planned`, every paper-result family has
    `target_baseline.value: null`, and the `artifact_schema` construction/
    certificate strings describe expected artifact kinds rather than executable
    validators, exact construction payloads, SOTA numeric targets, or verifier
    scripts. AlphaEvolve Appendix B also states that data and verification code
    for all reported constructions appear in the accompanying Google Colab; the
    current registry has no equivalent construction-data export or runnable
    verifier-code artifact contract.
  - Required result: connect benchmark-grade fixtures beyond smoke validators
    to `libreevolve.benchmark_hardening.v1` and
    `libreevolve.example_benchmark_scope.v1`; emit benchmark-grade artifact
    files, repeated-seed evaluation, target/SOTA baselines, executable
    construction/certificate validators, Colab-equivalent construction-data and
    verifier-code exports for Appendix B families, benchmark reports suitable
    for comparing AlphaEvolve-alignment features, real anti-gaming fixtures
    for benchmark-grade operation/rank discovery, and a central validation gate
    that fails when the shipped example-scope registry drifts. The matrix smoke
    fixture now has `write_matrix_smoke_hardening_bundle()`, which emits
    concrete negative-fixture files, detector-log, hardening report,
    artifact inventory, summary, and smoke-scope validation evidence while
    preserving `alphaevolve_comparable: false`.
    The remaining gap is generating benchmark-grade hardening files from real
    tensor/geometric benchmark fixtures, not emitting smoke-scope matrix
    hardening evidence, verifying declared files once a report names them, or
    preventing declared hardening evidence from overriding the smoke-only
    scope registry.

- [ ] Add Figure 5 construction-exhibit provenance and visual artifacts.
  - Spec evidence: AlphaEvolve Figure 5 presents selected SOTA-breaking
    mathematical construction examples with branch labels, problem labels,
    before/after metric values, and rendered construction visuals such as
    hexagon outer-edge, max-distance/min-distance, and sum-of-radii examples.
  - Current evidence: the Appendix B registry is family/status coverage, and
    existing TODOs ask for construction-data/verifier exports, aggregate
    outcome reports, benchmark hardening, and result-version provenance. No
    code/report schema records Figure 5 exhibit IDs, selected Appendix B result
    rows, previous-best/result values, branch/problem labels, visual artifact
    paths/hashes, rendering parameters, source Colab cell/artifact, or verifier
    linkage.
  - Required result: add report/inventory metadata for Figure 5-style
    exhibits: stable exhibit IDs, Appendix B family/parameter links,
    previous/current metric values with direction/unit, previous-best source,
    construction payload, rendered visual/JSON artifacts with hashes,
    verifier/certificate links, and docs that distinguish exhibit
    reproduction from broader Appendix B family coverage.

- [ ] Add Figure 5 versus Appendix B.12 sum-of-radii precision provenance.
  - Spec evidence: AlphaEvolve Figure 5's sum-of-radii panel displays
    `2.6340 -> 2.6358`, while Appendix B.12 text and Figure 14 describe the
    `n = 26` unit-square circle-packing result as improving from `2.634` to
    `2.635`.
  - Current evidence: broad Figure 5 and Appendix B.12-B.13 TODOs require
    exhibit/result rows and packing certificates, but current code/report
    schemas do not require a field that preserves the exact figure-displayed
    precision, the appendix-text precision, or a reconciliation policy between
    the two. Existing README/ROADMAP/TODO wording names the Appendix B.12
    value as `2.635` and could silently drop the Figure 5 `2.6358` display.
  - Required result: add per-source numeric-value records for this result:
    source location (`Figure 5`, `Appendix B.12`, `Figure 14`), displayed
    value string, normalized numeric value, rounding/precision policy, selected
    canonical report value, and docs that prevent Figure 5 visual values and
    Appendix text values from being conflated.

- [ ] Add Appendix B figure-level construction provenance for Figures 10-14.
  - Spec evidence: AlphaEvolve Appendix B includes displayed construction
    figures beyond the main-text Figure 5 summary: Figure 10 for Erdos minimum
    overlap, Figure 11 for regular-hexagon packings, Figure 12 for
    maximum/minimum-distance point sets, Figure 13 for Heilbronn variants, and
    Figure 14 for circle/rectangle packing sum-of-radii improvements.
  - Current evidence: the Appendix B registry is family/status coverage, and
    existing TODOs require construction-data/verifier exports, aggregate
    outcome reports, result-version provenance, and Figure 5 exhibit mapping.
    No code/report schema records Appendix B figure IDs, subfigure labels,
    family/parameter links, previous/current values, figure-caption values,
    construction payloads, visual artifact paths/hashes, rendering parameters,
    source Colab cells/artifacts, or verifier/certificate links for
    Figures 10-14.
  - Required result: add report/inventory metadata for Appendix B figure-level
    exhibits: stable figure/subfigure IDs, Appendix B family and parameter
    links, previous/current metric values with direction/unit, previous-best
    source, construction payload, rendered visual/JSON artifacts with hashes,
    verifier/certificate links, and docs that distinguish Appendix B figure
    reproduction from family-level registry coverage and main-text Figure 5
    exhibit coverage.

- [ ] Add Appendix B per-result metric and value provenance.
  - Spec evidence: AlphaEvolve Appendix B.1-B.13 reports heterogeneous
    mathematical results: autocorrelation constants, the uncertainty constant
    `C4`, Erdos minimum overlap, finite-set sum/difference ratios, regular
    hexagon outer side lengths, max/min-distance ratios, Heilbronn minimum
    areas, the dimension-11 kissing lower bound, and circle/rectangle
    sum-of-radii values. Each section carries its own parameters, metric
    definition, inequality direction, previous bound, new value, and source
    citation or figure/caption linkage. The reproducible construction
    representation also varies by family: step functions over fixed intervals,
    polynomial or coefficient lists, finite integer sets, point coordinates,
    sphere/kissing configurations, and geometric packing placements.
  - Current evidence: the Appendix B registry is family/status coverage, and
    existing TODOs require construction-data/verifier exports, aggregate
    outcome reports, result-version provenance, Figure 5 exhibit mapping,
    Figures 10-14 visual provenance, and the kissing-number proof certificate.
    They do not require a normalized per-result table that binds every
    Appendix B text-level claim to its exact metric formula or definition,
    parameter tuple, maximize/minimize or upper/lower-bound direction, prior
    value and source, reported AlphaEvolve value, manuscript section or figure
    location, construction representation schema, and verifier/construction
    artifact.
  - Required result: add Appendix B result-row metadata and validators for
    all B.1-B.13 claims: stable result ids, family/parameter rows, metric
    names and formulas, units or bound semantics, optimization direction,
    previous-best values and citations, AlphaEvolve reported values, source
    section/figure/caption links, construction-type schemas and payload hashes
    for step functions, coefficients, finite sets, coordinates, and packing
    placements, verifier artifact hashes, and docs that distinguish text-level
    numeric claim provenance from aggregate outcome reports and visual figure
    reproduction.

- [ ] Add Appendix B.1-B.3 autocorrelation step-function provenance.
  - Spec evidence: AlphaEvolve Appendix B.1-B.3 reports three
    autocorrelation/autoconvolution inequality improvements using explicit
    step-function constructions on `[-1/4, 1/4]`: B.1 uses `600`
    equally-spaced intervals to improve the upper bound to `C1 <= 1.5053`,
    B.2 uses `50` equally-spaced intervals to improve the lower bound to
    `0.8962 <= C2`, and B.3 uses `400` equally-spaced intervals to improve
    the upper bound to `C3 <= 1.4557`.
  - Current evidence: the broad Appendix B per-result TODO names
    autocorrelation constants and step-function construction payloads, but no
    code/report schema separately records the three B.1-B.3 result ids,
    interval counts, common domain, sign/non-negativity policy, inequality
    direction, prior bounds, step values, or recomputed constants. A generated
    report could flatten the three claims into one generic autocorrelation
    family row and lose which construction proves which bound direction.
  - Required result: add Appendix B.1-B.3-specific result rows and validators
    for interval count, domain, step-function value payload hash,
    non-negative-versus-signed function policy, metric formula id,
    upper/lower-bound direction, previous-best value/source, recomputed bound,
    source section linkage, and README/ROADMAP wording that distinguishes the
    three autocorrelation witnesses from aggregate Appendix B coverage.

- [ ] Add paper-facing Appendix B.1-B.3 autocorrelation label provenance.
  - Spec evidence: AlphaEvolve Appendix B headings are `B.1. First
    autocorrelation inequality`, `B.2. Second autocorrelation inequality`, and
    `B.3. Third autocorrelation inequality`; the constants in those sections
    are `C1`, `C2`, and `C3`, respectively. The paper does not label these
    three autocorrelation results as `k=3`, `k=4`, or `k=5`.
  - Current evidence: `alphaevolve_appendix_b.json`,
    `appendix_b_registry.py`, and `tests/test_appendix_b_registry.py` use
    stable family ids and names such as `autocorrelation_bounds_k3`,
    `autocorrelation_bounds_k4`, `autocorrelation_bounds_k5`, and
    `Autocorrelation inequality, k=3`. The step-function provenance TODO
    requires result rows and constants, but it does not require registry/report
    label fields that separate internal ids from exact paper headings and
    constant labels.
  - Required result: add explicit paper-facing label metadata for B.1-B.3:
    source section id, paper heading, constant id, and display label. Update
    registry validation, tests, README/ROADMAP wording, and generated reports
    so internal stable ids cannot be mistaken for paper terminology.

- [ ] Add Appendix B.8 max/min-distance squared-ratio convention provenance.
  - Spec evidence: AlphaEvolve Appendix B.8 reports point-set constructions for
    minimizing the ratio between maximum and minimum pairwise distances, but the
    displayed values use a squared-ratio convention: 16 points in 2D report
    `12.889266112`, and 14 points in 3D report `4.165849767`, corresponding to
    square-root ratios for the geometric objective.
  - Current evidence: the broad Appendix B per-result TODO requires metric
    formulas, units, bound semantics, values, and coordinate payloads. No
    code/report schema separately records whether the paper value is the ratio,
    squared ratio, or transformed objective value, so generated reports could
    quote the raw numbers as direct distance ratios or compare them against
    baselines in the wrong unit.
  - Required result: add Appendix B.8-specific metric-convention fields and
    validators: raw paper value, reported-value convention
    (`squared_max_min_ratio`), derived ratio transform, dimension/point-count
    parameter rows, comparison-unit policy, source section/caption linkage, and
    README/ROADMAP wording that labels both the squared value and the geometric
    square-root ratio unambiguously.

- [ ] Add Appendix B.8 point-set distance-certificate provenance.
  - Spec evidence: AlphaEvolve Appendix B.8 and Figure 12 report two concrete
    point-set witnesses for minimizing the max/min pairwise-distance ratio:
    16 points in two dimensions with squared ratio `12.889266112`, improving
    the best known squared bound `12.890`, and 14 points in three dimensions
    with squared ratio `4.165849767`, improving the best known squared bound
    `4.168`.
  - Current evidence: the B.8 convention TODO above prevents quoting squared
    values as direct ratios, and the broad Appendix B per-result TODO asks for
    coordinate payloads in general. No code/report schema separately forces
    B.8 witness validation: exact point count, dimension, coordinate payload
    hash, finite-coordinate checks, all-pairs minimum and maximum distance
    certificates, recomputed squared ratio, prior value/source comparison, or
    Figure 12 left/right panel linkage.
  - Required result: add Appendix B.8 witness rows and validators that record
    point-set artifact hashes, `n`, dimension, pairwise-distance certificate
    hashes, recomputed min distance, max distance, squared ratio and derived
    ratio, prior best value/source, improvement direction, source
    section/caption location, Figure 12 panel id, and docs that distinguish
    distance-certificate evidence from the separate squared-ratio convention
    metadata.

- [ ] Add Appendix B.5 minimum-overlap step-function provenance.
  - Spec evidence: AlphaEvolve Appendix B.5 improves the Erdos minimum-overlap
    upper bound from `C5 <= 0.380927` to `C5 <= 0.380924` using the step
    function shown in Figure 10. The claim depends on the formulation over
    step functions `h` on `[0, 2]` with values in `[0, 1]`,
    integral normalization `integral_0^2 h(x) dx = 1`, and the objective
    `max_k integral h(x) * (1 - h(x + k)) dx`.
  - Current evidence: the broad Appendix B per-result TODO names Erdos minimum
    overlap and step-function payloads, and the figure-level TODO names
    Figure 10, but no code/report schema separately records B.5's function
    domain, value bounds, normalization certificate, convolution/shift
    objective, prior lower/upper bounds, improved upper bound, or Figure 10
    construction payload. A generated report could quote the improved bound
    without proving the step function satisfies the normalized formulation.
  - Required result: add Appendix B.5-specific result rows and validators for
    step-function domain, interval/value payload hash, value-range check,
    integral-normalization certificate, objective recomputation over shifts,
    prior lower/upper values and sources, reported upper bound, Figure 10
    linkage, and README/ROADMAP wording that distinguishes B.5 minimum-overlap
    evidence from aggregate Appendix B coverage.

- [ ] Add Appendix B.5 original-formulation and equivalence provenance.
  - Spec evidence: AlphaEvolve Appendix B.5 defines `C5` as the largest
    constant such that
    `sup_{x in [-2,2]} integral_{-1}^1 f(t) g(x+t) dt >= C5` for all
    non-negative `f,g: [-1,1] -> [0,1]` with `f + g = 1` on `[-1,1]` and
    `integral f = 1`, extending `f` and `g` by zero outside `[-1,1]`. It then
    states, citing `[40]`, that this constant equals the infimum over
    normalized step functions `h` on `[0,2]`.
  - Current evidence: the B.5 step-function TODO records the reduced `h`
    formulation, but no code/report schema separately records the original
    paired-function domain, complement constraint, zero-extension convention,
    supremum-over-shifts statement, `[40]` equivalence reference, or the
    mapping from the source Erdos problem to the step-function construction.
    A report could validate the Figure 10 `h` payload while losing the problem
    statement that makes it an Erdos minimum-overlap bound.
  - Required result: add Appendix B.5 formulation metadata and validators for
    `f,g` domain/value bounds, `f+g=1`, `integral f=1`, zero-extension policy,
    `sup_{x in [-2,2]}` objective, `[40]` equivalence citation, transformation
    link to the `[0,2]` step-function row, and README/ROADMAP wording that
    distinguishes source-problem provenance from construction-payload
    provenance.

- [ ] Add Appendix B.6 finite-set witness provenance.
  - Spec evidence: AlphaEvolve Appendix B.6 improves the sums-and-differences
    lower bound by finding a finite set `U1` of size `2003`, yielding
    `1.1479 <= C6`, and a second finite set `U2` of size `54265`, yielding
    `1.1584 <= C6`. The result depends on the Gyarmati et al. inequality,
    the conditions that `U` contains zero and satisfies
    `|U - U| <= 2 max(U) + 1`, and computed `|U-U|` and `|U+U|` values.
  - Current evidence: the broad Appendix B per-result TODO names finite-set
    construction representations, but no code/report schema separately records
    B.6 witness ids, set cardinalities, integer payload hashes, condition
    checks, sumset/difference-set counts, denominator `2 max(U) + 1`, or the
    two staged lower-bound values. A generated report could claim the final
    `1.1584 <= C6` value without retaining the intermediate `U1` witness or
    the inequality inputs that make either witness verifiable.
  - Required result: add Appendix B.6-specific witness rows and validators for
    `U1` and `U2`: set size, max element, contains-zero flag, sorted integer
    payload hash, `|U-U|`, `|U+U|`, feasibility inequality status, derived
    lower-bound value, source section linkage, and README/ROADMAP wording that
    distinguishes the two witness sets from aggregate Appendix B coverage.

- [ ] Add Appendix B.6 finite-set theorem/admissibility provenance.
  - Spec evidence: AlphaEvolve Appendix B.6 defines `C6` through arbitrarily
    large finite integer sets `A` and `B`, the sumset
    `A + B = {a + b : a in A, b in B}`, the difference set
    `A - B = {a - b : a in A, b in B}`, and asymptotic notation where
    `X << Y`/`X >> Y` use constants independent of sufficiently large sets.
    It then cites `[39, Corollary 3]` for `C6 <= 4/3`, `[39, Theorem 1]` for
    the prior lower bound, and the Gyarmati et al. finite-set theorem requiring
    `U` to be a finite set of non-negative integers containing zero with
    `|U - U| <= 2 max(U) + 1`.
  - Current evidence: the B.6 witness TODO records `U1`/`U2`, arithmetic
    counts, feasibility checks, and derived lower-bound values, but no
    code/report schema separately records the theorem statement, asymptotic
    quantifier scope, sumset/difference-set definitions, source theorem ids,
    or admissibility preconditions that distinguish theorem-valid witnesses
    from arbitrary finite-set payloads.
  - Required result: add Appendix B.6 theorem metadata and validators for the
    `C6` statement, `A+B`/`A-B` definitions, `<<`/`>>` constant-independence
    notes, prior bound sources, Gyarmati theorem/corollary references,
    admissible-`U` domain checks, and README/ROADMAP wording that keeps
    theorem conditions separate from witness-payload provenance.

- [ ] Add Appendix B.7 regular-hexagon packing provenance.
  - Spec evidence: AlphaEvolve Appendix B.7 reports two regular-hexagon
    packing improvements: packing `n = 11` disjoint unit regular hexagons into
    an outer regular hexagon improves the side length from `3.943` to `3.931`,
    and packing `n = 12` improves the side length from `4.0` to `3.942`.
    Figure 11 shows the two constructions as left/right panels.
  - Current evidence: the broad Appendix B per-result TODO names regular
    hexagon outer side lengths and Figure 11 visual provenance, but no
    code/report schema separately records the two B.7 parameter rows, unit
    hexagon geometry, outer-hexagon side-length convention, placement payload
    hashes, containment/non-overlap certificates, prior values, or Figure 11
    panel linkage. A generated report could quote one "hexagon packing"
    improvement without proving both `n = 11` and `n = 12` constructions.
  - Required result: add Appendix B.7-specific result rows and validators for
    `n`, inner unit-hexagon convention, outer side-length unit, placement
    artifact hash, containment certificate, pairwise non-overlap certificate,
    prior value/source, reported side length, Figure 11 panel linkage, and
    README/ROADMAP wording that distinguishes both hexagon-packing witnesses
    from aggregate Appendix B coverage.

- [ ] Add Appendix B.9-B.10 Heilbronn minimum-area provenance.
  - Spec evidence: AlphaEvolve Appendix B.9-B.10 reports three Heilbronn
    construction improvements with distinct domains and parameters: `n = 11`
    points in a unit-area triangle improve the minimum triangle area from
    `0.036` to greater than `0.0365`; `n = 13` points in a unit-area convex
    region improve `0.0306` to `0.0309`; and `n = 14` points in a unit-area
    convex region improve `0.0277` to `0.0278`. Figure 13 displays the three
    constructions as left/middle/right panels.
  - Current evidence: the broad Appendix B per-result TODO names Heilbronn
    minimum areas and Figure 13 visual provenance, but no code/report schema
    separately records the three B.9-B.10 parameter rows, domain type,
    unit-area normalization, point-coordinate payload hashes, minimum-area
    certificate, strict-versus-rounded comparison policy, or prior SOTA values.
    A generated report could quote "Heilbronn improved" without proving which
    construction, domain, and `n` value supports each bound.
  - Required result: add Appendix B.9-B.10-specific result rows and validators
    for `n`, domain type (`triangle` or `convex_region`), unit-area scaling,
    point-set/region artifact hashes, all-triples minimum-area certificate,
    prior value/source, reported value and strict inequality policy, Figure 13
    panel linkage, and README/ROADMAP wording that distinguishes the three
    Heilbronn constructions from aggregate Appendix B coverage.

- [ ] Add kissing-number lemma certificate provenance for Appendix B.11.
  - Spec evidence: AlphaEvolve Appendix B.11 improves the dimension-11 kissing
    number lower bound from 592 to 593 by finding 593 nonzero integral-coordinate
    points whose maximum norm is smaller than their minimum pairwise distance,
    then proves via Lemma 1 that scaling those points gives a valid kissing
    configuration.
  - Current evidence: Appendix B TODOs cover family/status registry rows,
    construction-data/verifier exports, aggregate outcome reports, and
    Figure 10-14 visual exhibit provenance. They do not require a
    kissing-specific certificate that checks point count, dimension,
    nonzero/integral coordinates, exact norm and pairwise-distance inequalities,
    the transformation to sphere centers, non-overlap/tangency verification, or
    linkage from those proof checks to the reported lower-bound claim.
  - Required result: add Appendix B.11 certificate/report metadata and
    validators for the kissing-number construction: point-set artifact hash,
    dimension and cardinality, exact coordinate domain, norm and distance
    bounds, Lemma 1 applicability checks, transformed sphere-center evidence,
    lower-bound claim linkage, and docs separating a rendered construction
    figure from proof-grade kissing-configuration verification.

- [ ] Add Appendix B.12-B.13 circle/rectangle sum-of-radii provenance.
  - Spec evidence: AlphaEvolve Appendix B.12-B.13 reports three fixed-`n`
    sum-of-radii packing improvements: `n = 26` circles in a unit square improve
    the SOTA from `2.634` to `2.635`, `n = 32` circles in a unit square improve
    `2.936` to `2.937`, and `n = 21` circles in a perimeter-4 rectangle improve
    `2.364` to `2.3658`. Figure 14 shows these as left, middle, and right
    panels.
  - Current evidence: the Appendix B registry marks the checked-in
    `circle_packing` example as a fixed-26 unit-square smoke fixture and the
    rectangle family as planned. The broad per-result and Figure 14 TODOs do
    not separately require all three B.12-B.13 parameter rows, container
    geometry, perimeter normalization, circle-center/radius payload hashes,
    containment and pairwise non-overlap certificates, or prior/current
    sum-of-radii values. A generated report could mistake the 26-circle smoke
    fixture for full Appendix B.12-B.13 evidence.
  - Required result: add Appendix B.12-B.13-specific result rows and validators
    for `n`, container type (`unit_square` or `perimeter4_rectangle`),
    container dimensions/perimeter, circle-center/radius artifact hashes,
    exact count, containment certificate, pairwise non-overlap certificate,
    sum-of-radii recomputation, prior value/source, reported value, Figure 14
    panel linkage, and README/ROADMAP wording that separates the 26-circle
    smoke fixture from full paper-claim evidence.

- [ ] Add aggregate constructive-math outcome coverage reports.
  - Spec evidence: AlphaEvolve Section 3.2 reports more than 50 mathematical
    problems across more than five branches of mathematics, with best-known
    constructions rediscovered in roughly 75% of cases and new SOTA
    constructions in roughly 20% of cases. That is an aggregate outcome claim
    over problem instances, not only a family-level Appendix B artifact list.
  - Current evidence: `alphaevolve_appendix_b.json` enumerates thirteen
    constructive-math families and records planned/smoke status plus expected
    construction/certificate artifact shapes. It does not enumerate the
    underlying per-problem/per-parameter instances, branch taxonomy, previous
    best references, matched-versus-improved outcome counts, or aggregate
    percentages needed to support Section 3.2-style breadth claims.
  - Required result: add a constructive-math outcome ledger/report with
    problem-instance ids, branch labels, parameter settings, prior-best
    references, discovered construction links, matched/improved/failed status,
    and validated aggregate counts/percentages before claiming AlphaEvolve-
    style breadth across dozens of mathematical problems.

- [ ] Add simple/random starting-construction provenance for constructive-math
      benchmarks.
  - Spec evidence: AlphaEvolve Section 3.2 says that, for the broad set of
    constructive mathematical problems where it matched or improved prior
    bests, "the initial starting point was a simple or a random construction."
  - Current evidence: seed provenance records safe source paths, generation-0
    baselines, skipped seed diagnostics, and separate strict-seed/human-seeded
    matrix TODOs. The Appendix B registry and aggregate constructive-math TODOs
    do not record whether each constructive-math run began from a simple
    deterministic construction or a random construction, which random seed or
    generator produced it, its initial metric value, or whether benchmark
    prompts/evaluators prevented hidden prior-best construction seeding.
  - Required result: add constructive-math benchmark/report fields for
    starting-construction class (`simple`, `random`, or explicitly
    `human_seeded`/`prior_art_seeded` where applicable), construction payload
    or artifact hash, generator/seed provenance, baseline metric value,
    prior-best visibility policy, and validation that Section 3.2-style
    aggregate claims are backed by simple/random starts rather than undocumented
    incumbent or expert-seeded constructions.

- [ ] Add Appendix B result-version provenance for revised mathematical
      constants.
  - Spec evidence: AlphaEvolve Appendix B includes result-level details that
    changed across manuscript versions. In particular, the uncertainty
    inequality section reports an initial improved bound of `C4 <= 0.3521`,
    then notes that after the first version Henry Cohn pointed to a refined
    approach and AlphaEvolve improved the reported constant further to
    `0.3216`, with details in the accompanying Google Colab.
  - Current evidence: `alphaevolve_appendix_b.json` is a family/status ledger:
    it records the `uncertainty_inequality` family as planned with null
    target-baseline value and generic construction/certificate artifact labels.
    It does not represent per-result constants, manuscript revision status,
    superseded versus current reported bounds, post-publication notes, advisor
    attribution, or links from revised constants to verifier artifacts.
  - Required result: add result-version metadata for Appendix B benchmark
    rows, including paper revision/source date, reported constant or
    construction value, superseded/current status, update note, attribution
    where relevant, verifier/Colab artifact linkage, and validation that docs
    do not mix first-version and updated bounds when claiming AlphaEvolve-style
    mathematical result parity.

- [ ] Add Appendix B.4 prior-bound rounding provenance.
  - Spec evidence: AlphaEvolve Appendix B.4 states the known uncertainty
    inequality range as `0.2025 <= C4 <= 0.3523`, while noting that the upper
    bound from reference `[33]` is stated as `0.353` in that paper but becomes
    `0.3523` when its solution is rounded to the fourth digit. The same
    paragraph then compares AlphaEvolve's first-version `C4 <= 0.3521` result
    against that rounded prior bound.
  - Current evidence: existing Appendix B TODOs require revised-result rows,
    Hermite-polynomial certificate details, verifier links, and qualitative
    comparison to reference `[33]`. They do not require a source-linked record
    for the prior `[33]` stated value, the paper's fourth-digit rounding
    caveat, the lower-bound context, or the exact baseline value used when
    claiming the `0.3521` improvement.
  - Required result: add Appendix B.4 prior-bound metadata and validators for
    the `[33]` source id/page or section, stated prior upper bound `0.353`,
    rounded/recomputed prior bound `0.3523`, lower-bound context `0.2025`,
    rounding precision and policy, source-solution artifact or citation status,
    comparison to AlphaEvolve's `0.3521` first-version bound, and docs checks
    that keep this prior-bound caveat distinct from the later `0.3216`
    revision and from Hermite certificate verification.

- [ ] Add Appendix B.4 Hermite-polynomial certificate provenance.
  - Spec evidence: AlphaEvolve Appendix B.4 derives `C4 <= 0.3521` from a
    Fourier uncertainty test function `f(x) = P(x) exp(-pi x^2)` where `P` is
    an even linear combination of Hermite polynomials `H_{4k}`. The reported
    first-version construction uses coefficients approximately
    `[0.32925, -0.01159, -8.9216e-5]` for `H0`, `H4`, and `H8`, factors
    `P(x)` by `x^2`, takes the largest positive root of `P(x)/x^2`, and
    computes the bound as `r_max^2 / (2*pi)`.
  - Current evidence: existing Appendix B TODOs require numeric result rows,
    revised-result provenance, construction/verifier links, and qualitative
    comparison to reference `[33]`. They do not require B.4-specific
    coefficient precision, Hermite-basis identities, even-polynomial/Fourier
    invariance assumptions, sign/condition checks for the test function,
    largest-root calculation evidence, or the normalization formula that turns
    the root certificate into the `C4` upper bound.
  - Required result: add Appendix B.4 construction/certificate metadata and
    validators for Hermite basis terms, coefficient payload and precision,
    `P(0)=0`/`x^2` factor handling, positivity/sign-condition checks,
    largest-positive-root computation, `r_max^2 / (2*pi)` recomputation,
    previous bound comparison, and artifact hashes. Keep this separate from
    the B.4 revision-history and near-optimality-similarity TODOs.

- [ ] Add Appendix B.4 prior-construction similarity and hypothesis provenance.
  - Spec evidence: AlphaEvolve Appendix B.4 does more than report the
    uncertainty-inequality value and Hermite-polynomial coefficients. After
    deriving `C4 <= 0.3521`, it says the AlphaEvolve linear combination is
    qualitatively very similar to the construction in reference `[33]` and
    treats that similarity as empirical support for the prior hypothesis that
    the construction is nearly optimal.
  - Current evidence: existing Appendix B TODOs require per-result values,
    coefficient payloads, verifier links, revised-result provenance, and
    comparison to previous numeric bounds. They do not require a source-linked
    qualitative comparison between the AlphaEvolve construction and the prior
    `[33]` construction, nor a claim record for the near-optimality hypothesis
    that the paper says was empirically supported.
  - Required result: add Appendix B.4 comparison/provenance metadata that links
    the AlphaEvolve Hermite-polynomial construction to the prior `[33]`
    construction: source reference and page/section, comparable construction
    family, coefficient/structure comparison fields, qualitative-similarity
    claim text, hypothesis claim id, evidence strength label, and docs
    validation that separates numeric bound improvement from qualitative
    near-optimality evidence.

- [ ] Add incumbent-construction handoff contracts for heuristic-search
      benchmarks.
  - Spec evidence: AlphaEvolve Section 3.2 describes evolving programs that
    act as search heuristics for constructive-math problems. The evaluator
    gives those heuristics a fixed search budget and a strong incumbent or
    previous best construction, then scores whether the candidate improves the
    construction under that budget.
  - Current evidence: LibreEvolve can evolve Python workspaces, pass static
    context files, copy evaluator artifacts out of temporary workspaces, and
    validate benchmark/result schemas after reports are declared. The Appendix
    B registry and circle-packing smoke example can describe expected
    construction/certificate artifact kinds, but there is no first-class
    problem contract or benchmark runner that supplies an incumbent
    construction to a candidate search heuristic, records the fixed budget and
    incumbent identity, captures the returned improved construction, and
    links that handoff to result artifacts and verifier inputs.
  - Required result: add a benchmark-grade heuristic-search fixture contract
    that makes incumbent construction, budget, candidate-produced construction,
    verifier/certificate artifacts, and improvement status explicit in
    evaluator metadata and benchmark reports. Keep this separate from generic
    context files or smoke artifact copy-out until a runner proves the full
    AlphaEvolve Section 3.2 handoff loop.

- [ ] Add constructive-math heuristic-stage sequence provenance.
  - Spec evidence: AlphaEvolve Section 3.2 says each evolved heuristic was
    given a fixed time budget, for example `1000 seconds`, and the best
    construction found by the previous best heuristic. It further says final
    constructions often came from a sequence of different specialized
    heuristics: early heuristics made large gains from random or simple initial
    states, while later heuristics fine-tuned near-optimal configurations.
  - Current evidence: existing TODOs cover simple/random starting construction
    provenance and the single-step incumbent handoff contract. They do not yet
    require a stage-level heuristic chain that records the exact allotted
    budget, previous-best source, heuristic identity, produced construction,
    improvement delta, and broad-gain versus fine-tuning role for each stage.
  - Required result: add constructive-math benchmark/report records for
    heuristic stage index, fixed budget seconds, incumbent construction
    artifact/hash, candidate heuristic artifact/hash, output construction
    artifact/hash, score before/after, improvement status, and stage role
    classification. Keep this separate from generic runtime-budget accounting
    until a report can prove AlphaEvolve-style multi-stage adaptive search.

- [ ] Generate suite matrix tensor artifacts and per-seed hit-rate reports.
  - Spec evidence: AlphaEvolve Section 3.1 and Appendix A evaluate low-rank
    tensor decomposition targets with multiple random seeds, report the best
    rank plus the fraction of seeds that achieved it, and publish exact
    integer or half-integer algorithms for the target suite.
  - Current evidence: the checked-in `matrix_multiplication` example is a
    three-case `matmul2` smoke validator with no tensor target suite, seed
    accounting, coefficient-domain certificate, or exportable exact algorithm
    artifact. `libreevolve.problems.benchmarks.matrix_results` now defines and
    tests a benchmark-level result schema with target identity, dimensions,
    seed count, best rank, hit fraction, exactness/certificate status,
    coefficient domain, explicit AlphaEvolve-comparable claim policy,
    per-seed results, artifact paths/hashes,
    consistency checks tying top-level best rank and hit counts to per-seed
    ranks/flags, and summary-report rendering. Exploratory `rational` and
    `float` coefficient-domain reports remain valid only when
    `alphaevolve_comparable` is false; AlphaEvolve-comparable claims require
    integer or half-integer coefficients, verified exactness, exact per-seed
    rows, and algorithm/certificate/notebook artifacts.
    `libreevolve.alphaevolve_appendix_a_matrix_registry.v1` now records the 54
    Appendix A Table 3 target identities, dimensions, best-known ranks,
    AlphaEvolve ranks, and matched/surpassed/fell-behind outcomes; reports for
    `alphaevolve_appendix_a` reject unknown target ids and dimension
    mismatches. That registry is rank/outcome metadata only: it does not store
    the target tensors, discovered tensor decompositions, coefficient lists,
    per-target exactness certificates, notebook exports, or construction
    provenance needed to reproduce Appendix A algorithms. The registry has its
    own validator, but the standard `libreevolve.tools.paper_manifest` gate
    currently wires Appendix B and ablation registries only, so corrupt
    Appendix A registry rows would not fail the routine paper-manifest check.
    `libreevolve.matrix_result_artifact_inventory.v1` now verifies declared
    algorithm/certificate/notebook artifact references against concrete files
    under an explicit artifact root, checking safe relative paths, existence,
    SHA-256 hashes, and byte counts.
    `write_strassen_2x2_publication_bundle()` now emits a concrete checked
    Strassen artifact bundle for the registered `mm_2x2x2` target, including
    canonical algorithm, certificate, notebook, report, and artifact-inventory
    files with exact rank-7 per-seed rows and a 1.0 best-rank hit fraction.
    `validate_matrix_publication_bundle()` validates the
    `libreevolve.matrix_publication_bundle.v1` wrapper, embedded report,
    target identity, report-file hash/byte evidence, and inventory
    consistency for that bundle.
  - Required result: connect exact target tensors, tensor-decomposition
    algorithms, coefficient-domain data, certificate artifacts, and
    Appendix A registry validation through the standard paper-manifest gate,
    notebook/export artifacts to the registered target suite; keep the existing
    Python smoke example clearly outside AlphaEvolve-comparison evidence until
    it emits validated tensor-result reports. The remaining gap is generating
    discovered exact algorithms, certificates, and notebook/export files across
    the registered target suite, not validating declared artifact inventory,
    validating the checked bundle wrapper, or emitting the one checked Strassen
    baseline once those files exist.

- [ ] Pin the generated Strassen baseline bundle as a checkout-verifiable
      paper artifact.
  - Spec evidence: AlphaEvolve-style paper evidence should leave durable,
    inspectable artifacts for published algorithms, certificates, and notebook
    exports, not only a helper that can generate them during tests.
  - Current evidence: `write_strassen_2x2_publication_bundle()` in
    `libreevolve.problems.benchmarks.matrix_results` writes
    `matrix/mm_2x2x2/algorithm.json`, `certificate.json`,
    `reproduce.ipynb`, `report.json`, and artifact-inventory records under a
    caller-provided root, and `tests/test_matrix_results.py` validates those
    files in a temporary directory. The current checkout has no committed
    `matrix/mm_2x2x2/` artifact files, and the routine
    `libreevolve.tools.paper_manifest` command does not regenerate, hash-check,
    or validate the helper-produced baseline bundle.
  - Required result: add a stable checked-in or generated-and-pinned
    Strassen baseline artifact target with declared output paths, expected
    hashes/byte counts, command provenance, and CI/paper-manifest validation
    that proves a fresh checkout can reproduce or verify the exact algorithm,
    certificate, notebook, report, and inventory files. Keep this distinct
    from the full Appendix A discovery gap: the scope is durable evidence for
    the one registered baseline helper, not claiming suite-wide discovery.

- [ ] Record matrix baseline-component provenance for Section 3.1 starts.
  - Spec evidence: AlphaEvolve Section 3.1 says the matrix-decomposition
    search starts from a problem description and a standard gradient-based
    algorithm including an initializer, reconstruction loss function, and Adam
    optimizer before AlphaEvolve evolves more sophisticated tensor-search
    programs.
  - Current evidence: LibreEvolve records matrix target/result metadata after
    a report exists, plus TODOs for near-integrality, sweep provenance,
    scalar fields, and the Figure 8 loss-only ablation. It does not yet define
    a matrix benchmark runner or report field that inventories the initial
    gradient-based solver components, records their source hashes, declares
    which components are fixed versus mutable, or links accepted mutations
    back to the baseline initializer/loss/optimizer boundaries.
  - Required result: add matrix benchmark metadata and validators for the
    starting algorithm component inventory: initializer, reconstruction loss,
    optimizer identity and version/config, mutable component scopes, fixed
    component hashes, generation-0 baseline outcomes, and mutation lineage
    showing which baseline components changed. Keep this separate from final
    result reports and from the Figure 8 loss-function-only ablation until an
    executed matrix runner proves the baseline-to-evolved-program path.

- [ ] Add matrix cascade-run provenance for repeated-seed rank reports.
  - Spec evidence: AlphaEvolve Section 3.1 says the matrix-decomposition
    experiments run over multiple random seeds using the evaluation cascade,
    then report the best lowest rank per target and the fraction of seeds that
    reached that rank.
  - Current evidence: generic evaluator cascades can run staged validators,
    and `libreevolve.matrix_result_report.v1` can validate declared per-seed
    rank rows after a report exists. There is no matrix benchmark runner or
    report provenance that records the cascade configuration used for each
    matrix target/seed, per-stage rank and exactness diagnostics, early-stop
    or pruning decisions, candidate lineage through cascade stages, or how the
    executed cascade traces aggregate into the published best-rank hit
    fraction.
  - Required result: add matrix benchmark execution records and validators for
    target id, seed id, cascade id/version, stage labels and thresholds,
    per-stage candidate rank/exactness/certificate status, stop reason,
    accepted final rank, and aggregation checks tying all seed-level cascade
    traces to the matrix result report. Keep this separate from generic
    cascade semantics and from hand-authored matrix reports until actual
    Section 3.1-style runs emit the evidence.

- [ ] Add best-known-rank citation provenance for Appendix A matrix baselines.
  - Spec evidence: AlphaEvolve Table 2 reports matrix targets with a
    `best known [reference]` column, and Appendix A Table 3 extends those
    best-known-rank comparisons across the matrix target suite.
  - Current evidence: `libreevolve.alphaevolve_appendix_a_matrix_registry.v1`
    records target ids, dimensions, best-known rank values, AlphaEvolve ranks,
    outcomes, and exact-algorithm flags, and reports reject unknown target ids
    and dimension mismatches. The registry does not store which cited prior
    work supports each best-known rank, the bibliography/reference id, source
    page/table location, finite-field or characteristic caveats, companion
    artifact links, or a digestible source record for baseline-rank claims.
  - Required result: extend the Appendix A registry or companion metadata with
    per-target prior-baseline citation provenance and validation: reference id,
    source artifact/page/table, applicability caveats, and report-visible
    baseline-source fields. Keep this distinct from target-suite curation,
    tensor/decomposition construction artifacts, and baseline solver-component
    provenance.

- [ ] Add matrix headline historicity provenance for the 4x4 complex rank-48
      result.
  - Spec evidence: AlphaEvolve's abstract and Section 3.1 say the agent found
    a procedure for multiplying two 4x4 complex-valued matrices using 48
    scalar multiplications. Section 3.1 frames this as the first method, after
    56 years, to achieve rank less than 49 over a characteristic-zero field,
    while distinguishing recursive Strassen rank 49 over any field and Fawzi
    et al.'s rank-47 result for the field with two elements.
  - Current evidence: Appendix A matrix TODOs track best-known-rank citations,
    Table 2/Table 3 exhibit provenance, target-subset scope, scalar-field
    evidence, Figure 4/Figure 9 exhibits, and companion Colab decomposition
    links. They do not require a single auditable headline record tying the
    4x4 complex rank-48 claim to its historicity context, prior-algorithm
    comparison, characteristic caveat, source locations, and docs wording.
    Without that, README/ROADMAP/papers text can cite rank 48 or stored matrix
    rows without proving the stronger "first improvement after 56 years" claim.
  - Required result: add matrix-headline provenance with target id, dimensions,
    scalar field/characteristic, reported rank, prior Strassen rank and scope,
    finite-field Fawzi-rank caveat, bibliography reference ids, source
    page/span locations for the abstract and Section 3.1, decomposition/
    certificate/Colab linkage, and README/ROADMAP/papers validation that keeps
    rank-value evidence separate from historicity and field-scope claims.

- [ ] Add Table 2/Table 3 matrix-rank table exhibit provenance.
  - Spec evidence: AlphaEvolve Table 2 displays selected matrix tensor-rank
    comparisons, and Appendix A Table 3 expands this to all 54 considered
    targets with best-known ranks, AlphaEvolve ranks, outcome coloring/summary
    counts, complex-valued row caveats, Colab decomposition links, and the
    concurrent-work note for `<4, 5, 6>`.
  - Current evidence: LibreEvolve has an Appendix A matrix registry, matrix
    report validation, best-known-rank citation TODOs, row-note/concurrent-work
    TODOs, target-suite curation TODOs, Figure 4 exhibit TODOs, and
    scalar-field/tensor-rank caveat TODOs. Those track row facts and algorithm
    evidence, but no code/report schema records Table 2/Table 3 exhibit ids,
    selected-row versus full-table membership, row ordering, caption aggregate
    counts, color/outcome encoding, complex-valued row annotations, note
    linkage, source PDF/caption locations, rendered table artifacts/hashes, or
    row-to-registry/report/Colab mappings.
  - Required result: add matrix-rank table exhibit metadata and validators with
    stable table ids, row ids/order, selected/full-table membership,
    source/caption locations, best-known and AlphaEvolve rank values, outcome
    classes and aggregate count checks, complex-valued and concurrent-work
    annotations, rendered table artifact hashes, and links to registry rows,
    matrix reports/certificates, and companion source evidence so docs
    distinguish table reproduction from general matrix registry validity.

- [ ] Add matrix result subset-scope validation for main-text versus
      Appendix A outcome claims.
  - Spec evidence: AlphaEvolve Table 2 says that beyond the selected examples,
    for all parameters `m, n, p <= 5`, AlphaEvolve either matched or surpassed
    the best-known solutions. Appendix A Table 3 is a broader 54-target table
    that includes targets outside that main-text subset.
  - Current evidence: `libreevolve.alphaevolve_appendix_a_matrix_registry.v1`
    validates 54 target rows and fixed aggregate outcome counts of `38`
    matched, `14` surpassed, and `2` fell behind. The `fell_behind` rows are
    larger-target records (`mm_4x4x9` and `mm_6x6x6`), while the main-text
    all-matched-or-surpassed claim is scoped to the `m,n,p <= 5` subset. The
    current registry and table-exhibit TODOs do not expose a claim-scope
    validator that proves a prose/table claim is being checked against the
    correct target subset rather than the whole Appendix A table.
  - Required result: add matrix report or registry summary metadata for named
    target subsets such as `main_text_mnp_le_5`, `table_2_selected`, and
    `appendix_a_full`, with inclusion predicates, row counts, outcome counts,
    out-of-scope/fell-behind row ids, source-caption linkage, and docs
    validation so README/ROADMAP/papers wording neither treats the full
    Appendix A registry as all matched/surpassed nor treats larger-target
    `fell_behind` rows as contradicting the scoped main-text claim.

- [ ] Add Appendix A matrix row-note and concurrent-work provenance.
  - Spec evidence: AlphaEvolve Appendix A Table 3 includes row-level result
    notes beyond the rank columns, including the note that concurrent work [49]
    also found a rank-90 algorithm for the `<4, 5, 6>` target.
  - Current evidence: `libreevolve.alphaevolve_appendix_a_matrix_registry.v1`
    stores target ids, dimensions, best-known ranks, AlphaEvolve ranks,
    outcomes, and exact-algorithm flags, and separate TODOs require
    best-known-rank source citations, target-suite curation, scalar-field
    evidence, and Colab artifacts. It does not store per-target result notes,
    concurrent-work attributions, independently matched result flags, note
    source page/table locations, or report-visible caveats for rows such as
    `mm_4x5x6`.
  - Required result: extend the Appendix A registry or companion metadata with
    row-level note provenance: note type, cited reference id, note text/source
    location, affected target id, relationship to AlphaEvolve's result
    (for example independently matched, superseded, or caveated), and
    report/docs validation so matrix claims do not overstate exclusive SOTA
    priority when the paper itself records concurrent matching work.

- [ ] Add Appendix A matrix target-suite curation provenance.
  - Spec evidence: AlphaEvolve Appendix A says the 54 matrix multiplication
    sizes were chosen roughly from sizes where 2 <= m,n <= 5 with a reasonable
    cutoff for p, and that tensor symmetries make axis permutations equivalent,
    so the paper focuses on sorted sizes m <= n <= p.
  - Current evidence: `libreevolve.alphaevolve_appendix_a_matrix_registry.v1`
    records the 54 target ids, dimensions, best-known ranks, AlphaEvolve ranks,
    outcomes, and exact-algorithm flags. It does not record the target-suite
    curation policy, canonical sorted-representative rule, symmetry-equivalent
    omitted targets, source/rationale for the p cutoff, or inclusion/exclusion
    rationale for targets outside the rough cutoff heuristic.
  - Required result: extend the Appendix A registry or companion report with
    target-suite curation metadata: selection rule, canonical representative
    under matrix-tensor axis symmetries, omitted-equivalent target ledger,
    cutoff/source rationale, and explicit included/excluded target records.
    Keep this distinct from target tensor/decomposition artifacts and from the
    larger-target resource-frontier/OOM evidence.

- [ ] Add matrix scaling resource-frontier evidence for larger target claims.
  - Spec evidence: AlphaEvolve Appendix A says sizes beyond the reported
    matrix table were difficult because running discovered programs on larger
    sizes with 1000 random seeds and a single GPU accelerator often ran out of
    memory, so extending the setup to larger matrix sizes requires further
    optimization.
  - Current evidence: LibreEvolve tracks generic local run budgets,
    accelerator-environment hints, and unsupported CPU/memory/GPU quotas, and
    the Appendix A registry records the 54 reported target identities and
    outcomes. It does not record matrix-benchmark resource frontiers, failed
    larger-target attempts, accelerator memory profiles, seed-count/resource
    tradeoffs, or explicit rationale for excluding targets beyond the
    registered Appendix A suite.
  - Required result: add matrix benchmark report fields and validators for
    target-size scaling attempts, seed counts, accelerator/GPU memory profile,
    OOM or resource-exhaustion diagnostics, attempted-versus-excluded target
    identities, and optimization/resource rationale before claiming readiness
    to extend AlphaEvolve-style matrix results beyond the reported suite.

- [ ] Add a matrix coefficient-domain prompt/evaluator contract for
      near-integral decompositions.
  - Spec evidence: AlphaEvolve Section 3.1 says matrix-decomposition
    candidates were prompted to generate near-integral solutions, and final
    decomposition entries were rounded to the nearest integer or half-integer
    before exactness checking. That is a search-time instruction and
    evaluator contract, not only a publication-report field.
  - Current evidence: `libreevolve.problems.benchmarks.matrix_results`
    validates declared matrix-result reports after they exist, including
    coefficient domain, exactness certificate status, per-seed exactness, and
    AlphaEvolve-comparable restrictions. The checked-in
    `matrix_multiplication` example remains a 2x2 scalar-count smoke fixture,
    and the benchmark report contracts do not yet inject or persist a
    benchmark-grade prompt instruction requiring near-integral tensor
    decompositions, record raw-versus-rounded coefficient diagnostics, or link
    those diagnostics to exactness certificates during evaluation.
  - Required result: add a matrix benchmark prompt/evaluator hook that records
    the coefficient-domain instruction, rounding policy, raw and rounded
    coefficient-domain diagnostics, per-seed exactness linkage, and prompt/run
    evidence before treating matrix search runs as aligned with the Section
    3.1 near-integrality workflow.

- [ ] Add matrix hyperparameter-sweep provenance for evolved search programs.
  - Spec evidence: AlphaEvolve's Appendix A Figure 9 matrix example evolves a
    program that includes a `sweep()` function backed by a user-provided
    `hyper` library, adding optimizer, noise, clipping, and discretization
    hyperparameter ranges that drive the tensor-decomposition search.
  - Current evidence: LibreEvolve records matrix result reports after a
    candidate run exists and has a 2x2 smoke fixture plus a checked Strassen
    publication bundle. It does not define a matrix benchmark protocol for
    candidate-produced sweep spaces, user-provided hyperparameter libraries,
    sampled sweep configurations, per-sweep/per-seed outcomes, or provenance
    tying evolved search-code changes to the final exact decomposition.
  - Required result: add matrix benchmark metadata and evaluator/report
    artifacts for evolved sweep functions, hyperparameter-range declarations,
    sampled configuration ids, per-sweep losses/ranks/exactness diagnostics,
    and linkage from selected sweep outcomes to final coefficient certificates
    before claiming parity with AlphaEvolve's Figure 4/Figure 9 matrix search
    workflow.

- [ ] Add Appendix A Figure 9a-9c magnified matrix-diff exhibit provenance.
  - Spec evidence: AlphaEvolve Appendix A Figures 9a to 9c present the
    magnified version of Figure 4's left panel: a three-part source/diff
    exhibit for the 4x4 matrix search program that discovers the rank-48
    decomposition, including optimizer, initialization, noise, loss,
    discretization, and `hyper` sweep edits. The displayed source changes
    include concrete semantic components such as Adam to AdamW, scaled complex
    initialization, gradient/decomposition/target noise, soft clipping,
    hallucination and discretization losses, large-value penalties, and named
    sweep fields.
  - Current evidence: separate TODOs require Figure 4 exhibit provenance and
    Figure 9 sweep-space metadata. They do not record Figure 9a/9b/9c as
    appendix exhibit panels with stable panel IDs, page/caption locations,
    exact line-span coverage, source/diff excerpt artifacts and hashes,
    continuation ordering across the three panels, OCR/rendered-text
    validation, semantic component labels for the shown code changes, or links
    from each panel to the same matrix target, sweep metadata, exactness
    certificate, and companion notebook/source evidence.
  - Required result: add Figure 9 exhibit metadata and validators with
    figure/panel IDs, source PDF page and caption locations, ordered panel
    continuity, exact code/diff line-span artifacts, rendered image/text
    artifact hashes, target/result-row mappings, semantic component inventories
    for optimizer/init/noise/clipping/loss/discretization/sweep changes,
    sweep-field links, and docs that distinguish reproduced Appendix A
    magnified-diff exhibits from Figure 4 main-text evidence and generic
    sweep-space provenance.

- [ ] Add Figure 4 matrix-discovery exhibit provenance.
  - Spec evidence: AlphaEvolve Figure 4 presents the main-text matrix
    multiplication discovery exhibit: a concrete evolved 4x4
    tensor-decomposition search-program diff with optimizer, initialization,
    noise, clipping, and loss changes, tied to the Section 3.1/Table 2 matrix
    rank-improvement claims. The caption also says AlphaEvolve made
    non-trivial changes to the optimizer, weight initialization, loss function,
    and hyperparameter sweep, requiring 15 accepted mutations during the
    evolutionary process.
  - Current evidence: LibreEvolve tracks Appendix A target/report contracts,
    checked Strassen bundle evidence, matrix baseline-component TODOs, and
    Figure 9 sweep-space provenance TODOs. Those cover benchmark/result shape
    and the Appendix A search-program workflow, but no code/report schema
    records a Figure 4 exhibit id, exact source diff excerpt artifact/hash,
    selected target/result-row mapping, caption values, rendering/source
    parameters, visual/text artifact hashes, the 15-mutation accepted-lineage
    count, per-mutation component labels, or links from the displayed exhibit
    to decomposition reports, certificates, and companion paper evidence.
  - Required result: add Figure 4-style matrix exhibit metadata with stable
    exhibit ids, target ids, exact source/diff excerpt artifacts and hashes,
    selected Table 2/Appendix A row mappings, rank/baseline/outcome values,
    rendered figure/text artifacts, accepted mutation sequence length,
    component-change categories for each accepted mutation, and links to matrix
    report, certificate, notebook, and paper-source evidence so docs
    distinguish main-text exhibit reproduction from general matrix benchmark
    readiness and Appendix A Figure 9 sweep evidence.

- [ ] Add matrix scalar-field provenance for real, complex, and characteristic
      claims.
  - Spec evidence: AlphaEvolve Section 3.1 and Table 2 report exact tensor
    decompositions for matrix multiplication, and explicitly note that some
    improved algorithms use complex-valued multiplications that can be used for
    exact multiplication over complex or real-valued matrices. The paper also
    distinguishes characteristic-0 applicability from finite-field-only
    results.
  - Current evidence: `libreevolve.problems.benchmarks.matrix_results`
    validates a coarse `coefficient_domain` value such as `integer` or
    `half_integer` for AlphaEvolve-comparable reports, plus exactness and
    artifact requirements. It does not model the scalar field or semiring over
    which the decomposition is valid, whether coefficients are real or complex
    with exact real/imaginary parts, whether a result is characteristic-0
    versus finite-field-specific, or whether the certificate proves real and
    complex matrix multiplication applicability separately.
  - Required result: extend matrix benchmark/report metadata and certificate
    validation with scalar-field/domain declarations, exact complex-coefficient
    representation, characteristic/applicability claims, and verifier evidence
    tying each claim to the target tensor before treating matrix reports as
    faithful to AlphaEvolve's complex-valued Appendix A results.

- [ ] Add matrix tensor-rank applicability and recursive-use caveats.
  - Spec evidence: AlphaEvolve Section 3.1 frames matrix multiplication results
    as low-rank tensor decompositions, contrasts the characteristic-0 rank-48
    `4x4` tensor-decomposition result with finite-field-only prior work, and
    footnote 3 says some algorithms use fewer than 49 multiplications but do
    not correspond to matrix-multiplication tensor decompositions and cannot be
    applied recursively to larger matrix multiplication.
  - Current evidence: the Appendix A matrix registry and
    `libreevolve.matrix_result_report.v1` store target ids, dimensions,
    best/AlphaEvolve ranks, outcomes, exactness, coefficient domains, and
    artifacts. They do not require an algorithm-kind field distinguishing
    tensor decompositions from other multiplication algorithms, a recursive
    applicability flag, evidence that the certificate proves tensor equality
    rather than only functional multiplication for one size, or report/docs
    caveats for rank comparisons where non-tensor algorithms are not
    comparable to recursive tensor-rank claims.
  - Required result: extend matrix reports or companion metadata with
    algorithm kind, tensor-decomposition certificate scope, recursive
    applicability, field/characteristic caveats, and source-note provenance so
    Appendix A rank claims remain faithful to the paper's distinction between
    tensor-rank improvements and non-recursive multiplication algorithms.

- [ ] Connect real systems fixtures to held-out and reference-correctness
  evidence.
  - Spec evidence: AlphaEvolve's engineering applications do not rely only on
    the same evaluator signal used during search. Section 3.3 reports unseen
    workload/capacity tests for scheduling, train/evaluation input-shape splits
    for kernel tiling heuristics, randomized reference-code checks for
    FlashAttention IR edits, and separate deployment or expert confirmation.
  - Current evidence: current examples are smoke-style local validators, and
    open benchmark TODOs cover stronger matrix/packing fixtures and broad
    compiler/hardware/systems coverage decisions. The
    `libreevolve.paper_result_certification.v1` contract can distinguish local
    validator records from independent certification evidence, and
    `validate_certification_evidence_bundle()` checks certification reports
    together with matching artifact inventory before accepting bundled
    paper-claim readiness.
    `libreevolve.systems_result_report.v1` now defines and tests a systems
    report contract with named optimization, held-out, and
    reference-correctness gates; case-set hashes; sample counts/seeds; finite
    metrics; artifact kinds matching passed ready gates; optional
    certification linkage that cannot contradict readiness claims; and an
    `alphaevolve_ready` gate that fails unless held-out and correctness gates
    are passed or explicitly documented as not applicable.
    The readiness contract is still domain-agnostic: a report can mark
    `reference_correctness` or `heldout` as `not_applicable` with a rationale,
    and the validator does not yet require randomized reference-code checks for
    kernel/compiler-style domains, unseen workload gates for scheduling, or
    hardware/deployment/expert confirmation gates for domains where the
    AlphaEvolve paper required those evidence types.
    `libreevolve.systems_result_artifact_inventory.v1` now verifies declared
    systems report artifacts against concrete files under an explicit artifact
    root, checking safe relative paths, existence, SHA-256 hashes, and byte
    counts for metrics, heldout-report, reference-report, and summary records.
    `validate_systems_evidence_bundle()` now checks systems reports together
    with matching artifact inventory before accepting bundled AlphaEvolve
    readiness. `libreevolve.systems_evidence_bundle.v1` now wraps embedded
    systems report and inventory records with benchmark/candidate/domain
    identity checks, stable embedded-record hashes, inventory-record hash
    linkage, and readiness consistency validation.
  - Required result: connect real compiler, hardware, kernel, scheduling, or
    systems benchmark fixtures to the report contract and implement the actual
    held-out/generalization case sets, randomized/reference-correctness checks,
    domain-specific not-applicable rules, and deployment or certification
    evidence. The remaining gap is generating real gate artifacts from those
    fixtures and enforcing domain-specific evidence requirements, not verifying
    declared artifact files once a systems report names them or checking
    certification report/inventory consistency, systems report/inventory
    consistency, or systems evidence bundle consistency once those records
    exist.

- [ ] Add Section 3.3 result-claim calibration fields for systems reports.
  - Spec evidence: AlphaEvolve Section 3.3 reports concrete production result
    magnitudes, including about 0.7% fleet-wide compute resources recovered for
    Borg scheduling, 23% average kernel speedup and 1% Gemini training-time
    reduction for Pallas/Gemini kernels, power/area objectives for TPU RTL, and
    32% kernel plus 15% pre/postprocessing speedups for FlashAttention
    compiler IR. Section 3.3.2 also claims the Pallas workflow reduced kernel
    optimization time from several months of engineering effort to days of
    automated experimentation and improved deployment/research ergonomics.
  - Current evidence: `libreevolve.systems_result_report.v1` requires finite
    numeric metrics inside optimization, held-out, and reference-correctness
    gates, and nearby TODOs require domain-specific evidence for scheduling,
    kernel, hardware, and compiler reports. The schema does not require a
    report to declare metric units, baseline denominator, before/after window,
    aggregation method, deployment or accelerator/runtime context, target
    published claim id, or whether a metric is the reported result magnitude
    versus only a local validator signal.
  - Required result: add claim-calibrated systems report fields and validators
    that map metrics to published Section 3.3-style claims: resource-recovery
    percentages with fleet/workload denominators and deployment windows;
    kernel speedups and training-time reductions with baseline heuristic,
    shape split, accelerator/runtime, and aggregation provenance; RTL
    power/area/PPA deltas with synthesis flow and correctness signoff; and
    compiler kernel/pre/postprocessing speedups with target configuration,
    tolerance, randomized-reference provenance, and abstraction-level
    attribution. Include engineering-effort and deployment-velocity fields for
    claims such as months-to-days optimization turnaround, manual-tuning
    baseline, affected engineer workflow, and production adoption state. Until
    then, finite systems metrics should not be treated as
    reproducible AlphaEvolve result-magnitude evidence.

- [ ] Add application-owner and domain-review provenance for practical systems
      reports.
  - Spec evidence: AlphaEvolve Section 3.3 reports production-facing
    applications across Borg scheduling, Gemini/Pallas kernels, TPU RTL, and
    XLA/FlashAttention IR, while the Acknowledgements and Contributions
    sections identify co-leads, domain advisors, reviewers, validation
    infrastructure owners, TPU designers, and XLA modification reviewers for
    those applications.
  - Current evidence: systems report contracts can validate generic
    held-out/reference/deployment/certification gates, and separate TODOs
    require scheduling safety, kernel shape-corpus, RTL verification, compiler
    reference checks, claim calibration, and exhibit provenance. They do not
    record application-owner identity, domain-reviewer roles, reviewer or
    signoff scope, validation-infrastructure ownership, workload/shape/capacity
    data stewardship, production rollout approvers, or links from
    claim-calibrated metrics to the responsible domain teams.
  - Required result: extend systems report and certification metadata with
    domain-owner and reviewer provenance: application domain, responsible team
    or reviewer role labels, data/source ownership, validation infrastructure
    owner, review/signoff scope, approval or deployment state, evidence
    artifact links, and docs that distinguish local benchmark reports from
    AlphaEvolve-style production/domain-owner validation.

- [ ] Add Borg scheduling problem-formulation provenance.
  - Spec evidence: AlphaEvolve Section 3.3.1 frames Borg scheduling as an
    online vector bin-packing problem with two resource dimensions: machines
    are bins with CPU and memory capacity, pending jobs are items with CPU and
    memory demands, stranded resources are the optimization motivation, and
    simulator feedback comes from historical workload and capacity snapshots.
  - Current evidence: systems reports can validate generic optimization and
    held-out gates, while separate scheduling TODOs cover ranking-only safety,
    mission-critical interpretability/deployment evidence, Figure 6 exhibit
    provenance, and calibrated fleet-recovery metrics. They do not require a
    scheduling-domain report to declare the bin/item/resource schema, units,
    workload/capacity snapshot identities, stranded-resource objective, or
    mapping from simulator inputs to the `required` and `free` CPU/memory
    fields used by the heuristic.
  - Required result: add scheduling-domain metadata and validators for the
    Borg-style vector-bin-packing formulation: machine/bin and job/item
    schemas, CPU/memory units and denominators, `required`/`free` feature
    definitions, workload/capacity snapshot provenance, stranded-resource
    objective linkage, simulator input hashes, and docs that separate
    scheduling problem-formulation evidence from ranking-only safety,
    deployment, and Figure 6 exhibit evidence.

- [ ] Add scheduling ranking-only safety provenance for Borg-style heuristics.
  - Spec evidence: AlphaEvolve Section 3.3.1 says the discovered Borg
    scheduling heuristic outputs a priority score for machines that Borg has
    already determined are available and capable of running the pending job,
    making scheduling decisions effectively correct by construction.
  - Current evidence: `libreevolve.systems_result_report.v1` can validate
    generic optimization, held-out, and reference-correctness gates and can
    accept `reference_correctness: not_applicable` for scheduling with a
    rationale. It does not require scheduling-domain reports to declare the
    candidate-set feasibility oracle, prove that evolved code only reorders
    feasible machines, record resource constraint invariants, or distinguish a
    safe ranking heuristic from code that directly admits, rejects, or places
    jobs.
  - Required result: add scheduling-specific report metadata and validator
    rules for feasibility-filter provenance, ranking-only heuristic scope,
    resource/capacity invariant checks, simulator/admission-boundary evidence,
    and allowed `not_applicable` reference-correctness rationale before
    treating Borg-style scheduling reports as AlphaEvolve-ready.

- [ ] Add scheduling interpretability and deployment-readiness evidence for
      mission-critical heuristics.
  - Spec evidence: AlphaEvolve Section 3.3.1 says AlphaEvolve was chosen over
    a deep reinforcement learning approach for Borg scheduling because the
    code solution had better performance and offered interpretability,
    debuggability, predictability, and ease of deployment for a
    mission-critical system.
  - Current evidence: `libreevolve.systems_result_report.v1` can validate
    generic optimization, held-out, reference-correctness, artifact, and
    certification-link fields. The scheduling-specific TODO above requires
    ranking-only feasibility provenance. Neither surface requires a
    scheduling-domain report to include reviewer/debuggability notes, code
    simplicity or rule-shape evidence, predictability or monotonicity checks,
    operational rollout constraints, deployment-risk review, or a comparison
    against less interpretable learned policies.
  - Required result: add scheduling-domain report fields and validators for
    interpretable heuristic structure, human/operator review, debuggability
    artifacts, predictability/invariant checks, deployment ergonomics, and
    baseline comparison against black-box or less interpretable approaches
    before treating Borg-style scheduling reports as mission-critical
    AlphaEvolve-ready evidence.

- [ ] Add Figure 6 scheduling-heuristic exhibit provenance and heatmap
      artifacts.
  - Spec evidence: AlphaEvolve Figure 6 presents the concrete Borg scheduling
    heuristic `alpha_evolve_score(required, free)` with CPU/memory residual
    terms and a rendered residual heatmap; Section 3.3.1 ties that heuristic to
    historical simulator feedback, unseen recent workloads, deployment, and
    about 0.7% fleet-wide resource recovery.
  - Current evidence: systems report contracts and scheduling TODOs track
    claim-calibrated metrics, ranking-only safety, and
    interpretability/deployment evidence. No code/report schema records a
    Figure 6 exhibit ID, exact heuristic source artifact/hash, residual input
    definitions and units, heatmap grid/rendering parameters, visual artifact
    paths/hashes, baseline production heuristic identity, or links from the
    displayed exhibit to simulator, held-out, deployment, and claim-calibration
    records.
  - Required result: add report/inventory metadata for Figure 6-style systems
    exhibits: stable exhibit ID, scheduling benchmark/candidate link, exact
    heuristic code artifact and hash, residual-feature definitions, baseline
    heuristic provenance, heatmap/JSON data plus rendered visual artifacts with
    hashes, rendering parameters, held-out/deployment report links, and docs
    that distinguish exhibit reproduction from generic scheduling readiness.

- [ ] Add Figure 7 Pallas tiling-problem exhibit provenance and diagram
      artifacts.
  - Spec evidence: AlphaEvolve Figure 7 visualizes the matrix-product tiling
    heuristic problem for `A B = C`, with input dimensions `M`, `N`, and `P`,
    and Section 3.3.2 explains that the heuristic chooses tile sizes while
    accounting for accelerator shapes, memory capacity, fused operations, and
    compiler details.
  - Current evidence: kernel/Pallas TODOs require shape-corpus provenance,
    train/evaluation split records, real accelerator runtime measurements,
    expert-baseline comparisons, tiling-only candidate boundaries, and
    correctness-by-construction evidence. No code/report schema records a
    Figure 7 exhibit ID, matrix-shape variable definitions, tile-parameter
    schema, accelerator/memory/fusion/compiler-context annotations, diagram
    source data, rendered visual artifact paths/hashes, rendering parameters,
    or links from the displayed tiling problem to the Pallas runtime and
    shape-corpus reports.
  - Required result: add report/inventory metadata for Figure 7-style kernel
    exhibits: stable exhibit ID, kernel benchmark/candidate link, matrix
    dimension and tile-parameter definitions, shape-corpus and accelerator
    context links, diagram/JSON data plus rendered visual artifacts with
    hashes, rendering parameters, baseline heuristic relation, and docs that
    distinguish tiling-problem visualization from executed Pallas runtime
    evidence.

- [ ] Add kernel-tiling train/eval shape provenance for Pallas-style heuristics.
  - Spec evidence: AlphaEvolve Section 3.3.2 optimizes a Pallas tiling
    heuristic for a Gemini matrix-multiplication kernel by minimizing actual
    runtime on real TPU accelerators. It automatically collects realistic
    kernel input shapes from users, uses half as optimization targets and half
    as a held-out evaluation set, and keeps correctness by construction because
    the evolved code changes tiling strategy rather than the underlying
    mathematical operation.
  - Current evidence: `libreevolve.systems_result_report.v1` can validate a
    generic `kernel` domain with optimization and held-out gates, but it does
    not require kernel-shape corpus provenance, train/evaluation split
    identity, real accelerator runtime measurements, baseline expert heuristic
    comparisons, tiling-only candidate boundaries, or correctness-by-
    construction evidence for unchanged kernel math.
  - Required result: add kernel-domain report metadata and validators for
    collected input-shape corpora, deterministic train/eval split provenance,
    accelerator/runtime measurement artifacts, baseline heuristic identity,
    tiling-parameter output constraints, correctness-by-construction scope,
    and deployment/readiness evidence before treating Pallas-style kernel
    heuristic reports as AlphaEvolve-ready.

- [ ] Add Pallas autotuning/manual-heuristic baseline workflow provenance.
  - Spec evidence: AlphaEvolve Section 3.3.2 says kernel engineers traditionally
    relied on search-based autotuning or manually crafted tiling heuristics.
    Search-based tuning interrupts the research workflow and requires retuning
    whenever input shapes change, while manual heuristic design is a major
    engineering bottleneck requiring deep kernel and hardware expertise. The
    paper frames AlphaEvolve as a way to automate manual tuning and improve
    ergonomics for emerging hardware and model developers.
  - Current evidence: existing Pallas TODOs require shape-corpus provenance,
    train/evaluation splits, real TPU runtime measurements, expert-baseline
    heuristic identity, tiling-only correctness, speedup metrics, and
    months-to-days optimization-time calibration. They do not require a report
    to classify the baseline workflow as search-based autotuning, manually
    crafted heuristic, or expert hybrid; record retuning burden for changed
    input shapes; preserve manual-effort assumptions; or compare AlphaEvolve's
    generated heuristic to both baseline workflow classes.
  - Required result: add kernel report fields and validators for baseline
    workflow type, autotuning search-space and retuning policy, manual-heuristic
    authoring/review effort, input-shape-change sensitivity, hardware-expertise
    assumptions, model-developer ergonomics impact, and comparison rows that
    distinguish AlphaEvolve-generated tiling heuristics from search-based
    autotuning and manual expert heuristics.

- [ ] Add Gemini self-training optimization loop provenance for Pallas
      deployment claims.
  - Spec evidence: AlphaEvolve Section 3.3.2 says the Pallas tiling heuristic
    discovered by AlphaEvolve was deployed in production, improved Gemini's
    training efficiency, increased the Gemini team's research and engineering
    velocity, and marked a novel case where Gemini, through AlphaEvolve,
    optimized its own training process.
  - Current evidence: Pallas/kernel TODOs require shape-corpus, train/eval,
    real-TPU runtime, expert-baseline, workflow-baseline, and production
    adoption evidence. The broad self-improvement TODO covers general
    infrastructure/model-uplift boundaries, but no code/report schema requires
    a Gemini-specific feedback-loop record linking the optimized Pallas kernel
    to the training workload of the model family that powered AlphaEvolve, the
    production deployment that changed training, and the basis for the
    self-optimization interpretation.
  - Required result: add kernel/domain report metadata for Gemini
    self-training claims: model/training workload identity, AlphaEvolve backend
    or Gemini-family relation, optimized Pallas kernel id, deployment date or
    release state, before/after training-time and kernel-runtime evidence,
    research-velocity or engineering-turnaround evidence, safety/rollback
    status, and docs wording that separates ordinary kernel deployment from
    AlphaEvolve-style self-optimization of Gemini's own training pipeline.

- [ ] Add RTL/EDA verification provenance for hardware-circuit optimization.
  - Spec evidence: AlphaEvolve Section 3.3.3 optimizes an already highly
    optimized Verilog implementation of a TPU arithmetic circuit, with
    objectives to reduce area and power while preserving core functionality.
    The paper says the final proposal must pass robust verification methods,
    was validated by TPU designers, and was independently caught later by
    downstream synthesis tools. It also frames the contribution as early
    RTL-stage optimization integrated into an upcoming TPU, communicated
    directly in Verilog to foster hardware-engineer trust and adoption, and
    potentially reducing time to market.
  - Current evidence: `libreevolve.systems_result_report.v1` can represent a
    generic `hardware` domain with optimization, held-out, and
    reference-correctness gates, but it has no RTL/EDA-specific fields for
    source HDL language, synthesis toolchain/provenance, power/area/timing
    metrics, equivalence or formal verification artifacts, designer-review
    signoff, downstream synthesis confirmation, RTL-stage contribution timing,
    standard-language trust/adoption evidence, upcoming-chip integration, or
    time-to-market impact.
  - Required result: add hardware-domain report metadata and validators for
    Verilog/RTL source boundaries, synthesis/PPA metric provenance,
    equivalence/formal verification evidence, timing/power/area constraints,
    designer or independent review signoff, downstream synthesis-tool
    confirmation, RTL-flow placement, adoption/trust rationale, integration
    target, and deployment/time-to-market evidence before treating
    hardware-circuit results as AlphaEvolve-ready.

- [ ] Add TPU arithmetic-circuit rewrite artifact provenance.
  - Spec evidence: AlphaEvolve Section 3.3.3 says the hardware result was a
    simple code rewrite in an already highly optimized Verilog implementation
    of a key TPU arithmetic circuit within the matrix multiplication unit, and
    that the rewrite removed unnecessary bits while reducing area and power.
  - Current evidence: the RTL/EDA TODO above requires HDL boundaries,
    synthesis/PPA metrics, formal/equivalence verification, designer signoff,
    downstream synthesis confirmation, and adoption evidence. It does not
    require the exact candidate rewrite artifact or semantic evidence for the
    paper's "removed unnecessary bits" claim: before/after Verilog excerpt
    hashes, affected signal/register/bit-range identities, arithmetic-circuit
    component id, matrix-multiplication-unit context, or a rewrite rationale
    linking eliminated bits to the measured area/power objective.
  - Required result: add hardware-domain report metadata and validators for
    the TPU rewrite artifact: source and modified Verilog hashes, exact
    changed-line or AST/diff spans, removed-bit/signal inventory, component and
    matrix-unit context, semantic rewrite category, linkage from each removed
    bit to verification/PPA records, and docs that distinguish the concrete
    rewrite artifact from generic RTL verification and downstream synthesis
    evidence.

- [ ] Add Gemini-to-TPU self-contribution provenance for hardware results.
  - Spec evidence: AlphaEvolve Section 3.3.3 says the TPU arithmetic-circuit
    improvement was integrated into an upcoming TPU and represents "Gemini's
    first direct contribution to TPU arithmetic circuits", achieved via
    AlphaEvolve.
  - Current evidence: hardware TODOs require RTL/EDA verification,
    designer/synthesis signoff, upcoming-TPU integration, Verilog trust and
    adoption evidence, and concrete bit-removal rewrite artifacts. They do
    not require a report to preserve the attribution chain behind the
    Gemini-to-TPU self-contribution claim.
  - Required result: add hardware-domain report metadata for Gemini
    contribution claims: Gemini/AlphaEvolve model-family relationship,
    arithmetic-circuit and TPU generation identity, contribution novelty
    basis, integration milestone, responsible hardware review/signoff roles,
    distinction from downstream synthesis-tool rediscovery, and docs checks
    that separate a concrete RTL optimization from the broader claim that
    Gemini directly contributed to TPU arithmetic circuits through
    AlphaEvolve.

- [ ] Add per-edit reference-check provenance for compiler-generated IR tasks.
  - Spec evidence: AlphaEvolve Section 3.3.4 directly optimizes
    XLA-generated IR for FlashAttention plus surrounding input/output
    processing. The paper says this IR was designed for debugging rather than
    direct developer editing, was compiler-generated and already highly
    optimized, each modification was checked against reference unmodified code
    on randomized inputs during optimization, and the final version was
    rigorously confirmed by human experts for all possible inputs.
  - Current evidence: `libreevolve.systems_result_report.v1` can require a
    final `reference_correctness` gate and artifact, but it has no
    compiler-IR-specific schema for per-edit randomized reference checks,
    IR-origin/debug-only versus direct-editing boundary metadata,
    compiler-generated/already-optimized baseline provenance,
    abstraction-level labels for kernel versus pre/postprocessing IR edits,
    reference implementation identity, randomized input generators, numerical
    tolerance policy, or final expert-confirmation scope.
  - Required result: add compiler/kernel report metadata and validators for
    candidate-edit sequences, per-edit randomized reference-check artifacts,
    IR provenance and editability constraints, reference implementation hashes,
    input-generator seeds/coverage, numerical tolerance and failure policies,
    abstraction-level attribution, and final expert/all-input signoff before
    treating compiler-generated IR results as AlphaEvolve-ready.

- [ ] Add FlashAttention compiler-stack context provenance.
  - Spec evidence: AlphaEvolve Section 3.3.4 places the optimized
    compiler-generated code inside a specific stack: Transformer attention is
    implemented using FlashAttention, FlashAttention is an accelerator kernel
    in Pallas, higher-level JAX code handles input preparation and output
    postprocessing, XLA lowers that implementation through a sequence of IRs
    for particular hardware, and the optimization targets memory-access
    orchestration or computation scheduling for a high-impact inference
    configuration on GPUs.
  - Current evidence: the compiler-IR TODO above requires edit-by-edit
    randomized reference checks, IR-origin/editability metadata, baseline
    provenance, and kernel-versus-pre/postprocessing attribution. It does not
    require a systems report to preserve the surrounding stack context:
    Transformer/attention workload identity, FlashAttention/Pallas kernel
    identity, JAX wrapper boundaries, XLA lowering-stage identities,
    hardware/configuration target, or the optimization decision class
    (`memory_access_orchestration` versus `computation_scheduling`).
  - Required result: add compiler/kernel report metadata and validators for
    FlashAttention stack provenance: workload/model configuration, Pallas
    kernel source identity, JAX pre/postprocessing wrapper artifacts, XLA IR
    stage and hardware-target records, lowered-IR artifact hashes, optimization
    decision-category labels, and docs that distinguish compiler-stack context
    evidence from per-edit reference checks and final speedup metrics.

- [ ] Add compiler-adoption path provenance for discovered optimizations.
  - Spec evidence: AlphaEvolve Section 3.3.4 says the FlashAttention result
    opens two adoption paths: incorporating discovered optimizations into
    existing compilers for specific use cases, and, longer term, incorporating
    AlphaEvolve into the compiler workflow itself.
  - Current evidence: compiler TODOs require per-edit randomized reference
    checks, IR/debug provenance, FlashAttention stack context, speedup
    attribution, and final expert confirmation. They do not require report or
    artifact metadata that distinguishes a one-off discovered optimization
    ported into an existing compiler from an AlphaEvolve-in-the-loop compiler
    workflow, nor do they record the target compiler/pass, use-case scope,
    integration owner, rollout/revert state, or workflow handoff boundary.
  - Required result: add compiler-domain report metadata and validators for
    adoption path (`existing_compiler_specific_use_case` versus
    `alphaevolve_in_compiler_workflow`), target compiler/pass identity,
    optimization artifact linkage, applicable workload/use-case constraints,
    integration and reviewer signoff, rollout or revert state, and docs that
    separate concrete compiler adoption from future workflow integration.

## LLM Ensemble

- [ ] Add live pricing/default-rate capture, raw provider replay, and
      async-aware budget policy beyond current diagnostics.
  - Spec evidence: AlphaEvolve's scheduler and compute-budget framing depend on
    LLM throughput, cost, latency, and quality; reproducible experiments need
    per-call evidence for which model/API call produced which proposal or
    feedback.
  - Current evidence: `LLMBackend.generate()` returns only `str`, and
    `LLMEnsemble.generate()` returns `(response, backend_idx)`.
    `LLMEnsemble.call_history` now records role, backend, backend metadata,
    strategy, API mode, prompt/output sizes and hashes, latency, status,
    failure metadata, and scheduler counts before/after the call. Successful
    mutation/critique calls are attached to candidate metadata, feedback calls
    to feedback records, and meta-prompt calls to prompt-history metadata.
    `llm_calls.jsonl` now provides a strict run-scoped LLM call/reward log.
    OpenAI, Anthropic, and Ollama adapters expose safe provider usage counts,
    finish reasons, request ids, and response ids when SDK responses provide
    them; the built-in adapters also expose `adapter_retry` telemetry with
    their configured `provider_max_retries`, provider-attempt count, failed
    attempt count, and safe exception type labels, plus bounded
    `provider_diagnostics` telemetry for scalar provider-native fields such as
    OpenAI system fingerprints, Anthropic message model/type labels, and
    Ollama duration counters when available. String diagnostics are
    secret-redacted, capped at 200 retained characters, and paired with raw
    SHA-256/count metadata; nested provider payloads are rejected before
    persistence, and strict ledger replay rejects malformed diagnostics
    envelopes. Built-in adapters now also
    expose `backend_defaults` telemetry with LibreEvolve's local output-token
    cap, provider internal retry cap, configured request timeout or `null`,
    API mode, and OpenAI reasoning/API-mode policy when relevant.
    `LLMEnsemble` validates and records those fields in call telemetry.
    Failed calls now also include
    `provider_failure_category` for provider-response validation failures,
    timeouts, rate limits, transport errors, provider client/server status
    errors, and unknown failures; failed SDK exceptions with safe HTTP-style
    `status_code` attributes also record `provider_status_code`. Final
    manifests now expose role-accounting/token summaries through compact
    `runtime.llm_accounting` totals and self-validated
    `runtime.llm_budget_report` instances now use status
    `cooperative_enforcement_snapshot` and policy
    `runtime_cooperative_budget_enforcement_v1`, validate that report metadata,
    and retain per-call provider-internal retry details from bounded LLM call
    history when available. Focused ensemble tests now cover fake provider
    usage counts and
    adapter retry diagnostics for `mutation`, `critique`, `feedback:<name>`,
    and `meta_prompt` roles. Backend specs and direct backend metadata now
    accept positive `cost_usd_per_million_tokens`; when sanitized provider
    usage includes `total_tokens`, call telemetry records
    `cost_estimate`, scheduler role accounting accumulates `cost_microusd`,
    and runtime LLM budget reports render aggregate `cost_usd`. Cost-estimate
    records now explicitly identify configured backend metadata as the pricing
    source, provider usage metadata as the token-count source, and mark the
    estimate as not live provider pricing. Each LLM call also records
    `cost_estimate_status`, including strict not-estimated reasons for missing
    configured rates or missing/invalid provider token totals. Final manifests
    now also expose `runtime.llm_provider_diagnostics` with schema
    `libreevolve.llm_provider_diagnostics.v1`, grouping retained call-history
    rows by backend index/name and API mode with usage totals, bounded
    successful-response and error-retention mode/policy counts, retained hash
    counts, retained-text counts, stored character totals,
    redaction/truncation counts, provider-diagnostic item/key counts, omitted
    diagnostic counts, configured cost-estimate/not-estimated counts,
    backend-default API-mode counts, call history retention, a records hash,
    and explicit limitations that this is retained-history-only, configured
    response/error text retention, bounded scalar diagnostics rather than full
    provider-native payloads, and configured estimates rather than live
    pricing.
    `validate_provider_capability_lookup_policy()` now validates
    `libreevolve.provider_capability_lookup_policy.v1` records for static-only
    provider lookup boundaries, required local validation checks, OpenAI
    API-mode policy linkage, offline compatibility, record count/hash
    integrity, and explicit non-use of live model-registry, service/API-version,
    or account-availability discovery.
    `validate_llm_provider_diagnostics_summary()` now validates
    `libreevolve.llm_provider_diagnostics.v1` runtime summaries for
    schema/policy/status/source, retained-history scope, backend-record hash
    integrity, non-negative counters, backend-count, total/backend aggregate
    count and retention-counter consistency, required limitation statements,
    and the current no-live-pricing/no-raw-payload replay boundary.
    Focused ensemble tests now cover `throughput_depth` metadata selection,
    normalized depth/cost/latency contribution against the reward scale,
    descriptive breadth/depth role metadata, live role metadata routing,
    configured role-backend overrides, fallback to global selection without a
    role match, and pull-once initialization before metadata priority.
    This is not yet AlphaEvolve's Flash/Pro-style scheduler evidence: no
    runtime policy reserves a low-latency breadth lane for high-volume
    candidate generation while injecting a stronger depth lane for occasional
    higher-quality proposals, and no report proves the mix improves search
    under equal budgets.
    `max_llm_provider_attempts` now consumes retained adapter retry telemetry
    as a live after-call stop input; `max_llm_tokens`,
    `max_llm_cost_microusd`, and `max_llm_seconds` do the same for
    provider-reported token totals, configured estimated cost, and retained LLM
    call latency. Remaining gaps
    are remote provider-side defaults and live pricing capture, full raw
    provider-specific payload retention/replay beyond configured response/error
    text retention and bounded scalar retained metadata, provider-output replay,
    and composition with async/pending-work controller restore. The remaining
    gap is not one-command restoration of replayable provider-attempt/token/
    configured-cost/latency controller events for the current synchronous
    runtime bundle.
  - Required result: add AlphaEvolve-style scheduler validation and reports
    that prove fast-breadth versus strong-depth model-mix behavior,
    breadth/depth/cost/latency selection behavior, and scheduler outcomes over
    real experiment traces and equal-budget runs; bounded raw/provider-specific
    diagnostic retention; remote provider-side default/pricing capture;
    provider-output replay boundaries; and async/pending-work budget policy
    that composes with the existing safe usage, retry, status,
    controller-event, ledger, runtime budget-report telemetry, and focused
    `throughput_depth` unit coverage.

- [ ] Add first-class Google/Gemini backend parity for AlphaEvolve model-mix
      reproduction.
  - Spec evidence: AlphaEvolve Section 2.3/2.4 says the published system used
    an ensemble of Gemini 2.0 Flash and Gemini 2.0 Pro so low-latency Flash
    could generate high-volume candidates while Pro occasionally supplied
    stronger suggestions.
  - Current evidence: `builtin_backend_registry()` exposes only `openai`,
    `anthropic`, and `ollama` built-in constructors; backend validation accepts
    those types plus `custom`. A custom backend can be written by users, but it
    does not provide a first-class Google/Gemini config surface, provider-native
    usage/default/capability telemetry, credential preflight, or Flash/Pro lane
    labels that the paper-facing scheduler reports can validate.
  - Required result: add a built-in Google/Gemini backend or an explicitly
    equivalent provider plugin contract with model-family capability metadata,
    credential/client preflight, safe request/usage/default telemetry,
    provider-diagnostic retention policy, and tests/reports that can reproduce
    or intentionally substitute the paper's Flash/Pro fast/strong ensemble
    without hiding behind an opaque custom backend.

- [ ] Add sample-efficiency reporting for AlphaEvolve-scale LLM proposal
      budgets.
  - Spec evidence: AlphaEvolve Table 1 contrasts FunSearch using millions of
    LLM samples with AlphaEvolve needing thousands of samples, while Section 4
    attributes part of that efficiency to stronger LLMs and full-system
    components.
  - Current evidence: `RunBudget` can stop on logical LLM calls,
    provider-attempts, provider-reported tokens, configured estimated cost,
    latency, evaluator counts, evaluator seconds, and wall-clock runtime.
    Generated candidates have deterministic ids, proposal-batch metadata, and
    history rows. The ablation-result contract validates equal-budget curves
    and includes the `Small base LLM only` variant, but it does not require
    candidate/sample-count efficiency curves.
  - Required result: add benchmark/report schemas and runtime summaries that
    count generated LLM proposals, evaluated candidates, valid candidates,
    archive-admitted candidates, retained elites, and target hits by sample
    budget; validate score/target progress versus thousands-scale proposal
    counts; and compare SOTA/strong-model runs with small-base or generic
    routing runs before claiming AlphaEvolve-style sample efficiency.

- [ ] Add repeated-sampling baseline reports for test-time-compute uplift
      claims.
  - Spec evidence: AlphaEvolve's Discussion frames the system as a
    test-time-compute agent that significantly enhances the base LLM compared
    with repeated sampling, sustained by machine feedback and evolutionary
    search.
  - Current evidence: LibreEvolve records LLM call/provider/token/cost/latency
    budgets, generated candidate ids, archive admission, and an equal-budget
    ablation report contract with a `No evolution` variant. It does not yet
    define a repeated-sampling baseline runner or report that fixes model,
    prompt, seed, budget, candidate count, and evaluator settings while
    disabling evolutionary feedback, parent/inspiration resurfacing,
    archive-driven selection, and meta-prompt updates. The current
    `No evolution` registry label is not enough to prove a base-LLM
    repeated-sample comparator.
  - Required result: add benchmark/report support for equal-budget repeated
    base-model sampling baselines with controlled prompts/models/seeds,
    generated/evaluated sample counts, candidate validity/admission outcomes,
    target-progress curves, and explicit links to matching evolutionary runs
    so test-time-compute uplift claims distinguish evolutionary feedback from
    ordinary repeated sampling.

- [ ] Promote role-scoped LLM routing from shared-bandit audit evidence to
  independent per-role scheduler policy.
  - Spec evidence: AlphaEvolve's ensemble and compute-budget framing separates
    proposal generation, critique, feedback, and prompt-improvement work; a
    faithful implementation needs role-specific model-selection state, budgets,
    and reward semantics that can be evaluated independently.
  - Current evidence: `LLMEnsemble` supports configured
    `llm_role_backend_indices`, backend-metadata role matching, per-role
    logical call caps, role-scoped provider/token/configured-cost/latency
    budget maps in `RunBudget`, configured reward-accounted roles, feedback
    reward wiring for exact configured feedback roles, scheduler-policy
    telemetry, and restorable `role_scheduler_state` audit records. However,
    `_ucb1_select()` still uses the shared `_counts`, `_wins`, and `_total`
    arrays as the authoritative live selection state; role matches only narrow
    eligible backend indices, and `role_scheduler_state` records counts/wins
    after selection instead of owning independent per-role bandit state,
    exploration coefficients, budgets, or calibrated reward contracts.
  - Required result: add explicit per-role scheduler policies for mutation,
    critique, feedback, and meta-prompt calls, including independent live
    selection state, role-specific reward calibration, quota/budget ownership,
    restore validation, and experiment-level reports proving that role
    selection behavior is not just shared global-bandit telemetry.

- [ ] Complete hard cancellation, async/accelerator budgets, and executed
      ablation scripts beyond current live LLM budget stops.
  - Spec evidence: AlphaEvolve-style LLM scheduling is compute-budgeted; retry
    knobs should not allow an effectively unbounded number of provider calls
    outside token-budget/cost/time/accounting controls.
  - Current evidence: `llm_max_retries` is now capped to the inclusive range
    `0..10` at both `Config` validation and direct `LLMEnsemble`
    construction, with focused config/ensemble/CLI coverage for accepted and
    rejected values. Built-in provider adapters now separately cap internal
    retries with `provider_max_retries` and record `adapter_retry` attempts.
    `max_llm_calls` now caps live `LLMEnsemble` attempt spending across
    original, retry, and fallback attempts: the loop clamps
    `LLMEnsemble.max_call_attempts` to the remaining call budget and records
    the actual retained call-history attempt delta into runtime/candidate
    budget snapshots.
    `libreevolve.llm_budget_report.v1` now defines and tests a report contract
    for role-specific logical-call, retry-attempt, adapter-attempt,
    token/cost/wall-clock limits and usage, provider-internal retry caps, and
    persisted resume-state hashes. Current report metadata is validated as a
    `cooperative_enforcement_snapshot` under policy
    `runtime_cooperative_budget_enforcement_v1`, so stale audit-only policy
    labels are rejected.
    `libreevolve.llm_budget_resume_artifact_inventory.v1` now verifies
    optional `resume_state.artifacts[]` records against an artifact root,
    including safe relative paths, file existence, SHA-256 hashes, byte counts,
    per-record statuses, aggregate missing/mismatch/invalid counts, and a
    stable records hash. Final runtime reports now include retained per-call
    adapter retry details from LLM call history and state when those details
    are bounded by call-history retention.
    `max_llm_provider_attempts` now records those adapter-internal attempts
    into `RunBudget` and stops before the next LLM call when the cap is
    exhausted. `max_llm_tokens` and `max_llm_cost_microusd` now stop before the
    next LLM call after provider usage or configured cost estimates consume the
    cap. `max_llm_seconds` and `llm_role_seconds_limits` now consume retained
    call `latency_sec` telemetry and stop before the next global or matching-role
    LLM call when latency caps are exhausted. Role-budget limit maps now accept
    manifest-safe prefix scopes such as `feedback:*`, and shared scoped caps are
    enforced by summing matching exact-role logical calls, provider attempts,
    tokens, configured cost, and retained call latency while keeping consumed
    counters concrete. Controller budget `llm_call`
    events can now validate and replay role-tagged provider attempts, tokens,
    configured cost, and latency seconds into `RunBudget`, so restored event
    streams can trip the same live stop checks after replay. Live synchronous
    budget deltas are now emitted to `controller_budget_events.jsonl` as
    contiguous rows for seed evaluations, generation starts, LLM calls,
    candidate evaluations, generation completions, and final stop reasons; LLM
    rows carry role-tagged provider attempts, tokens, configured cost, and
    latency when retained call telemetry exposes those values. Full-runtime
    restore now replays those rows, verifies their non-wall-clock consumed
    counters against the manifest budget snapshot, and passes the checked
    budget snapshot through the unified `evolve()` restore entrypoint.
    `validate_controller_budget_replay_state()` now makes that replay proof a
    reusable `core.budget` contract: it validates the controller event stream,
    reapplies provider-attempt, token, configured-cost, and latency deltas to a
    fresh budget with matching limits, and rejects consumed-counter or
    stop-reason drift against the persisted snapshot while treating manifest
    `runtime_seconds` as authoritative.
  - Remaining gap: the replayed controller budget stream is not yet composed
    with queued/running async worker state, pending-work restore, provider-output
    replay, or separate budget-stop manifests for replay-only exhaustion
    scenarios beyond the manifest stop snapshot. The remaining gap is not
    resume-state artifact inventory verification. The checked-in Figure 8
    ablation registry is still definition-only: several
    `required_config_assertions` are declarative component labels rather than
    executable `Config` fields or runtime switches, including
    `candidate_source`, `archive_admission_enabled`,
    `prompt_context_sections`, `candidate_workspace_mode`,
    `file_create_delete_enabled`, `ensemble_strategy: single_backend`, and
    `backend_capability_tier`.
  - Required result: connect replayed budget state to future async
    worker/pending-work controller state, provider-output replay, and
    budget-stop packaging for restored controller work. Add executable
    config/runtime bindings for every Figure 8 component assertion and keep
    the full-system baseline distinct from the five component-disabled
    ablations before any ablation runner treats the current registry as
    runnable experiment policy. For `No evolution`, add runner and history
    checks proving the same initial program is repeatedly fed to the LLM and
    no generated program is selected from the evolutionary database as parent,
    inspiration, or archive-feedback context. For `No context in the prompt`,
    correct the current over-broad registry definition: AlphaEvolve describes
    removing explicit problem-specific context, not removing the current
    program or evolutionary prior-program context. Add runner and
    prompt-history checks proving explicit context sources are absent, define
    whether local plugin/retrieval/failure sections count as explicit context,
    and separately record which core evolutionary prompt ingredients remain
    present so this ablation is not conflated with `No evolution`. For
    `Small base LLM only`, add executable
    backend policy and call-ledger checks proving all mutation-generation calls
    use exactly one configured small/base-capable model and never route or fall
    back to large-model backends during the ablation. For `No meta prompt
    evolution`, add runner checks proving no `meta_prompt` role calls,
    prompt-template mutations, or mutated prompt-program lineage entries occur
    in the ablated run, and that the full-system comparator keeps those
    surfaces enabled. Also record the frozen human-authored prompt identity,
    source, revision, and context policy used as the human-prompter comparator
    so disabling meta-prompt evolution is not conflated with an unspecified
    default prompt.

- [ ] Bind the `No full-file evolution` ablation to loss-function-only
      tensor-decomposition controls.
  - Spec evidence: AlphaEvolve Figure 8 defines `No full-file evolution` in the
    tensor-decomposition setting as evolving only the loss function, contrasting
    that localized edit surface with full-file/codebase evolution.
  - Current evidence: `alphaevolve_ablations.json` currently records the
    variant as `definition_only` with broad declarative assertions such as
    `mutation_mode: diff`, `candidate_workspace_mode: single_primary_file`,
    and `file_create_delete_enabled: false`. Those labels are not executable
    config fields, and they do not prove that a benchmark runner restricts
    mutation to a named loss-function region while leaving initializer,
    optimizer, sweep logic, certificate/export logic, and other tensor-search
    code fixed.
  - Required result: add executable ablation-runner bindings for a
    loss-function-only tensor-decomposition variant, including target file/block
    identity, allowed mutable symbol or evolve-block scope, config/runtime
    assertions, prompt wording, history metadata, and report fields that
    distinguish AlphaEvolve's localized loss-function ablation from generic
    single-file, diff-only, or no-topology-mutation runs.

- [ ] Bind Figure 8 ablation reports to matrix and kissing-number target
      families with curve-aggregation evidence.
  - Spec evidence: AlphaEvolve Section 4/Figure 8 evaluates ablations on two
    task families: low-rank tensor decompositions for faster matrix
    multiplication and lower-bound constructions for kissing numbers. The
    plotted y-axis is an aggregated target metric where higher values are
    better; curves average each setting over considered targets and show
    intra-target standard deviation over three independent runs initialized
    with different random seeds.
  - Current evidence: `libreevolve.alphaevolve_ablation_report.v1` validates
    declared targets, six variant ids, three seeds, required budget fractions,
    finite scores, consumed-budget consistency, component assertions, and
    hashed curve artifacts. The focused tests use `hello_world` as a small
    deterministic placeholder target, and the report schema does not require a
    target-family label, matrix-vs-kissing coverage, per-target aggregation
    records, target-metric identity, metric direction/normalization,
    intra-target standard-deviation curves, or linkage from curve summaries
    back to target-specific seed records.
  - Required result: extend ablation reports or generated curve artifacts with
    target-family metadata for `matrix_tensor_decomposition` and
    `kissing_number_sphere_packing`, per-target and cross-target aggregation
    summaries, target-metric name/direction/normalization records,
    three-seed mean/standard-deviation traces at each budget fraction, and
    validation that Figure 8-style reports are produced from the
    paper-relevant target families rather than arbitrary smoke targets.

- [ ] Add Figure 8 ablation-curve exhibit provenance and rendered artifacts.
  - Spec evidence: AlphaEvolve Figure 8 is a two-panel visual exhibit: matrix
    multiplication tensor-decomposition ablations on the left, kissing-number
    ablations on the right, compute-budget fraction on the x-axis, aggregated
    target metric on the y-axis, named variant curves, and shaded intra-target
    standard deviation over three independent seeded runs.
  - Current evidence: the ablation report contract validates declared variants,
    seeds, budget fractions, finite scores, consumed-budget consistency, hashed
    curve artifacts, and separate TODOs require paper target-family coverage and
    curve aggregation. No code/report schema records a Figure 8 exhibit ID,
    two-panel layout, series-to-variant legend mapping, exact paper legend
    labels, axis labels/scales, color/style/shading metadata, source
    PDF/caption location, rendered plot artifact path/hash, or links from the
    plotted visual to the exact ablation report, raw seed traces, and
    aggregation records. The checked-in ablation registry also labels the
    baseline `paper_label` as `Full`, while the Figure 8 legend says `Full
    method`, so current registry labels are not exact paper-legend evidence.
  - Required result: add Figure 8-style exhibit metadata and validators with
    stable exhibit and panel IDs, target-family labels, exact paper legend
    labels including `Full method`, series/legend mappings, axis and
    budget-fraction definitions, mean/std-band source records, rendering
    parameters, visual artifact hashes, and links to ablation reports and raw
    traces so generated curves can be distinguished from generic equal-budget
    report artifacts.

- [ ] Complete live hard provider cancellation and timeout-stop policy.
  - Spec evidence: AlphaEvolve runs long experiments under compute budgets, so
    provider latency and stalled model calls must be bounded and attributable to
    the run budget rather than blocking the controller indefinitely.
  - Current evidence: built-in OpenAI, Anthropic, and Ollama backend specs now
    accept positive `timeout_sec` and forward it into SDK/client construction
    as a provider request timeout. `llm_call_timeout_sec` now adds an
    ensemble-level deadline around each backend `generate()` attempt,
    including custom backends. Slow calls are recorded as
    `ProviderCallTimeoutError` with `provider_failure_category: timeout`,
    role-accounting timeout counters, call-timeout metadata, and normal
    retry/fallback eligibility. `RunBudget` still checks
    `max_runtime_seconds` before generation/evaluation boundaries, and
    `_generate_with_budget()` now clamps deadline-aware `LLMEnsemble` calls to
    the remaining wall-clock runtime budget before each attempt. Exhausted
    mutation timeouts now produce generated failure-history rows with retained
    timeout call telemetry and can continue later generations when budget
    remains. Ensemble-deadline timeout rows now also include a replay-validated
    `libreevolve.provider_cancellation_record.v1` with the role, backend, call
    id, timeout seconds, retry/fallback/telemetry budget action, and explicit
    `unsupported_daemon_worker_may_continue` hard-cancel gap. There is still
    no live hard provider cancellation token or timeout-driven stop policy.
    `libreevolve.provider_cancellation_policy.v1` now
    defines and tests a policy/report contract for provider request timeouts,
    ensemble wait deadlines, runtime deadlines, hard cancellation rules,
    role-scoped budget actions, artifact requirements, required
    artifact-kind linkage, hard-cancel readiness gated on `cancellation_record`
    artifact evidence, and hashed cancellation artifacts. Completed and aborted
    manifests now include a validated `runtime.provider_cancellation_policy`
    record declaring the current provider timeout, ensemble deadline, runtime
    deadline actions, and matching timeout/budget-stop artifact kinds with
    `hard_cancel_ready: false`.
    Provider-request-timeout and ensemble-deadline rules are now scoped to the
    loop's active LLM role surfaces: `mutation`, `critique`, `feedback:*`, and
    `meta_prompt`. Those rules now declare `quarantine` actions and
    `quarantine_record` artifact evidence when
    `llm_role_failure_quarantine_after` configures a matching exact role,
    reflecting the ensemble's role/backend failure-threshold quarantine state
    for exhausted timeout failures.
    Runtime cancellation-policy records now also include
    `libreevolve.provider_cancellation_observations.v1`, derived from the
    validated LLM scheduler snapshot, with timeout-failure counts by role,
    configured quarantine thresholds, and quarantined backend counts when
    observed.
    `libreevolve.provider_cancellation_artifact_inventory.v1` now verifies
    declared timeout, cancellation, budget-stop, and quarantine artifacts
    against concrete files under an explicit artifact root, checking safe
    relative paths, existence, SHA-256 hashes, byte counts, per-artifact
    status, and aggregate missing/mismatch/invalid counts.
  - Required result: connect the existing timeout/cancellation policy contract
    to live in-flight provider SDK cancellation, turn timeout categories into
    role-specific stop runtime policy, and add tests that runtime-budget
    exhaustion produces role-specific structured timeout/cancellation artifacts
    beyond the currently covered mutation timeout failure-history and policy
    quarantine-evidence paths. The remaining gap is live cancellation/stop
    behavior and runtime-budget exhaustion cancellation artifacts, not
    ensemble-deadline timeout call records or verifying declared cancellation
    evidence files once a policy names them.

- [ ] Extend critique reviewer pools beyond synchronous first/last-valid
  selection.
  - Spec evidence: AlphaEvolve-style generation can use multiple model calls
    and feedback channels under explicit budget policy; reviewer-style critique
    should contribute calibrated, attributable signal rather than only a
    sequential replacement filter.
  - Current evidence: `critique_reviewers` accepts up to eight manifest-safe
    reviewer specs with optional prompts and role labels, and
    `critique_aggregation_policy` selects `first_valid` or `last_valid`
    revised mutations. The loop runs a synchronous bounded reviewer pool,
    persists `metadata.critique.reviewer_pool` with schema
    `libreevolve.critique_reviewer_pool.v1`, reviewer roles, backend indices,
    parser status, valid-revision counts, aggregation policy, and selected
    reviewer provenance. Existing `llm_role_backend_indices`, role accounting,
    and timeout/cancellation policy records can route and account for exact
    reviewer roles such as `critique:correctness`.
  - Remaining gap: reviewer calls are still sequential, replacement-only, and
    selected by first/last valid mutation rather than calibrated reviewer score
    or benchmarked reviewer reliability. Reviewer pools do not yet overlap
    asynchronously, do not produce calibrated reviewer-score reports, do not
    isolate provider-failure policy per reviewer beyond the current role label,
    and do not emit richer reviewer-specific timeout/failure artifacts.
  - Required result: add async or parallel reviewer execution where appropriate,
    calibrated reviewer scoring and ablation reports for reviewer pools,
    stronger per-reviewer provider isolation and budget policy, and
    reviewer-specific timeout/failure artifacts before treating critique
    reviewer pools as AlphaEvolve-grade critique orchestration.

## Runtime, Reproducibility, and Safety

- [ ] Extend direct custom plugin provenance beyond signature-only records.
  - Spec evidence: AlphaEvolve-style experiments need reproducible extension
    boundaries: a run should state which custom plugin code and configuration
    influenced prompts, scores, artifacts, and lifecycle hooks.
  - Current evidence: built-in plugin specs validate supported constructor
    options before construction; entry-point plugin specs can capture
    manifest-safe or declared-schema constructor options, configured
    paper-inspiration labels, constructor signature shape, and distribution
    name/version plus hash-only `RECORD`/`WHEEL` metadata when available.
    Direct custom plugin instances record module/qualname/file hashes, exposed
    version metadata, constructor signature shape, and
    `libreevolve.direct_plugin_policy.v1`, which explicitly marks constructor
    values as excluded and package scope as module identity/file hash/version
    only.
  - Required result: add a versioned direct custom plugin registry or
    declaration path that can safely attribute constructor values/schemas,
    package/distribution source, paper-inspiration scope, artifact ownership,
    and replay/restore exclusions without introspecting arbitrary live object
    state or leaking secrets.

- [ ] Keep built-in paper-inspired plugin behavior scoped to approximation
  metadata.
  - Spec evidence: paper-inspired plugins and framework references should not
    claim faithful CausalEvolve, ThetaEvolve, ImprovEvolve, GigaEvo,
    CodeEvolve, or MadEvolve behavior unless their paper-specific loops,
    training, orchestration, or interfaces are actually implemented.
  - Current evidence: `CausalPlugin` exposes fixed token-pattern
    outcome-factor guidance and explicitly says it is not the CausalEvolve
    causal scratchpad. `TTTRLPlugin` now scopes its docstring to
    clipped-reward training-data export and explicitly does not implement
    online GRPO/RL training. `ModularPlugin` emits static
    prompt guidance and metadata with `operation_executed: false` and
    `interface_enforced: false`. The paper index marks GigaEvo, CodeEvolve,
    and MadEvolve as inspiration/background rows rather than implemented
    behavior.
  - Required result: if future work implements paper-specific plugin loops,
    training/checkpointing, causal scratchpads, generate/improve/perturb
    execution, Redis/DAG/insight orchestration, crossover/refinement, or
    domain-evolution innovation reports, update plugin metadata, README,
    ROADMAP, papers index, and matching TODO entries together. Until then,
    keep implementation metadata and public docs explicit that these are
    approximations or background-only references.

- [ ] Add release artifact and install-from-wheel verification.
  - Spec evidence: AlphaEvolve-style experimental artifacts should be
    reproducible from the code and dependency environment that produced them;
    release packaging is also the boundary users will install before running
    long experiments.
  - Current evidence: `pyproject.toml` already declares a setuptools
    `build-system`, PEP 621 project metadata, runtime dependencies, dev extras,
    package discovery, and the `libreevolve` console script. Runtime manifests
    record selected package/build metadata, installed distribution
    name/version, bounded `WHEEL`, redacted/hash-backed `direct_url.json`,
    `INSTALLER`, hash-only `RECORD`, known lockfile hashes, bounded
    `pip_freeze`, bounded `pip_config`, NumPy config, provider SDK versions,
    and accelerator hints.
  - Remaining gap: there is no committed wheel/sdist build check,
    install-from-wheel CLI smoke test, package-data inclusion validation,
    release checklist, or release-artifact provenance tying a generated
    distribution back to the source and manifest environment evidence.
  - Required result: add local/CI validation that builds the wheel and sdist,
    installs the wheel into an isolated environment, checks the console script
    and required package data, and records or documents release-artifact
    provenance without overclaiming full private-index or remote artifact
    verification.

- [ ] Add replayable external build, package-source, and accelerator environment evidence.
  - Spec evidence: AlphaEvolve-scale experiments should be reproducible across
    long-running evaluator environments, including external build steps,
    package sources, hardware/runtime state, and accelerator-backed execution
    budgets.
  - Current evidence: runtime manifests record selected PEP 621 and
    `[build-system]` metadata, declared dependency and installed-distribution
    name/version snapshots, bounded parsed `WHEEL` metadata, redacted/
    hash-backed `direct_url.json`, `INSTALLER`, hash-only `RECORD`, known
    project-root lockfile hashes, bounded/redacted `pip freeze` and
    `pip config` evidence, NumPy config hashes, provider SDK versions, and
    bounded accelerator environment/driver probe hints. The
    `environment_reproducibility_policy` deliberately marks the result
    `audit_only_not_complete_replay_environment` and lists unsupported
    complete install-source interpretation, broader non-project build
    provenance, private package-source identity/authentication resolution,
    remote artifact verification, live provider service/default capture, and
    accelerator budget/accounting semantics.
  - Remaining gap: the current records are bounded audit evidence, not a
    replayable environment contract. They do not capture external build
    commands/options/environment, non-project build metadata, transitive
    package-source resolution semantics, private-index identity/authentication
    policy, remote package artifact hashes, accelerator lease/accounting
    state, or a restore/check procedure that proves a later evaluator runtime
    can reproduce the original build/package/hardware boundary.
  - Required result: add versioned external-build and package-source
    provenance records, private-source redaction/authentication semantics,
    remote artifact verification or explicit exclusion policy, accelerator
    runtime plus budget-accounting records, and a restore/check validator that
    distinguishes bounded audit hints from replayable environment proof.

- [ ] Add pending-work full-resume orchestration and replay proof.
  - Spec evidence: AlphaEvolve is a long-running autonomous pipeline optimized
    for large computation budgets.
  - Current evidence: runs append to `history.jsonl`; `PromptDatabase` replays
    checked `prompt_history.jsonl`; final manifests persist framework RNG,
    LLM scheduler, and archive cursor/content snapshots; direct `evolve()` and
    CLI runs can restore validated runtime RNG, LLM scheduler, archive cursor,
    and full archive contents from manifests/history bundles. `load_full_resume_bundle()`
    and CLI `--restore-runtime-from-manifest` now validate and compose the
    currently compatible surfaces together: runtime RNG, LLM scheduler, full
    archive contents, budget counters, and the sibling controller budget event
    stream as checked replay input. The returned bundle now includes
    `libreevolve.full_resume_bundle_validation.v1`, which revalidates the
    composed runtime RNG, LLM scheduler, archive restore, runtime budget,
    controller-budget replay, lineage boundary, and unsupported-surface list
    while preserving `full_replay_ready: false`, provider-output non-replay,
    and no pending-work resume claim. Archive restore explicitly covers current
    cell/elite placements without replaying migration events as an ordered
    restore engine. Remaining gaps are no provider-output replay, no controller
    queue or pending-evaluation state, no migration-event replay engine, and
    no end-to-end resumed trace proving parent/inspiration/prompt/archive/
    controller continuity.
  - Required result: add one direct and CLI resume entrypoint that validates
    and composes population/database state, backend bandit state, prompt
    database state, RNG state, provider-output boundaries, migration replay or
    explicit non-replay policy, and pending controller/evaluation work, with an
    end-to-end resumed trace proving parent/inspiration/prompt/archive/
    controller continuity. The remaining gap is not validating the current
    compatible full-resume bundle shape.

- [ ] Define lineage replay contract for direct UUIDs and provider boundaries.
  - Spec evidence: AlphaEvolve compares systems over long computation budgets,
    ablations, and repeated seeds, so local stochastic choices and persisted
    lineage records must be reproducible enough to replay or diff experiments.
  - Current evidence: `evolve()` now owns a run-local RNG instead of reseeding
    Python's global `random` module. `PromptDatabase` selects untried
    configured seed templates in config order and restored prompt histories in
    replayed event order. Database-created prompt ids are deterministic for
    configured seed templates and prompt mutations. Loop-created seed and
    generated candidate ids are deterministic from seed/workspace order, parent
    id, prompt id, mutation hash, workspace hash, and generation coordinates.
    Direct `Program()` construction still defaults to `uuid4()`. LLM call ids
    are deterministic for matching ordered call streams because they include
    call sequence, backend/role/attempt coordinates, and prompt hash while
    preserving distinct ids for repeated identical calls inside one stream.
    Runtime manifests now persist and can restore checked run-local RNG
    snapshots, and full archive contents can be restored from
    manifest/history bundles. Completed and aborted runtime manifests now
    persist `runtime.lineage_replay_policy` with schema
    `libreevolve.lineage_replay_policy.v1`; it declares loop-created candidate
    ids, database-created prompt ids, and ordered LLM call ids as deterministic
    for matching streams, explicitly excludes direct `Program()` and direct
    `PromptProgram()` UUID4 defaults from the replay contract, and states that
    provider/model outputs are not replayed or proven identical by call ids.
    `load_runtime_lineage_replay_policy_snapshot()` now validates that policy,
    and `load_full_resume_bundle()` includes the checked policy/provider-output
    non-replay boundary in its composed restore metadata. There is still no
    end-to-end full replay trace that composes ids, RNG, archive, controller,
    and provider boundaries.
  - Required result: compose deterministic prompt/candidate/call ids with full
    resume orchestration, provider-output capture or explicit non-replay in the
    resumed trace, and end-to-end resumed-run tests proving stable parent,
    prompt, call, archive-sampling, controller, and manifest replay metadata.

- [ ] Compose framework RNG restore with resumed-trace replay.
  - Spec evidence: AlphaEvolve-style runs should be reproducible without
    perturbing an embedding application's randomness or allowing plugins and
    library code to consume the framework's scheduler RNG implicitly.
  - Current evidence: `evolve()` now owns a run-local `random.Random` from
    `Config.seed` and threads it through loop parent selection, prompt-template
    sampling, `ProgramDatabase`, `IslandModel`, and MAP-Elites random sampling
    without perturbing caller global RNG state. Completed and aborted runtime
    manifests persist checked `runtime.rng` snapshots with schema
    `python.random.mt19937.v1`, configured seed, JSON-safe state payload,
    `state_sha256`, and the `random.Random.setstate` restore entrypoint.
    `load_runtime_rng_state_snapshot()` and
    `restore_runtime_rng_state_snapshot()` validate schema, field sets, state
    hashes, and restorability; direct `evolve()` callers can pass
    `runtime_rng_state_snapshot`; and CLI runs can pass
    `--restore-rng-from-manifest` with seed-mismatch rejection before
    run-directory preparation. `runtime.rng.replay_boundary` now declares
    framework-owned RNG surfaces covered by restore and explicit exclusions for
    LLM provider outputs, plugin internal randomness, and validator subprocess
    randomness, while validation normalizes older boundaryless snapshots.
    `load_full_resume_bundle()` now exposes that validated boundary as
    `runtime_rng_replay_boundary` beside the restored RNG snapshot and lineage
    replay policy.
  - Remaining gap: full run replay still lacks provider output replay,
    plugin-owned RNG capture, controller/pending-work state restore,
    lineage-id replay, and end-to-end parent/inspiration/prompt/island/
    MAP-Elites replay tests across resumed runs.
  - Required result: compose the validated RNG restore boundary with the
    unified resume/replay entrypoint, define provider-output and plugin-owned
    RNG capture or exclusion semantics for that entrypoint, and test
    parent-selection, inspiration-sampling, prompt-selection, island-sampling,
    and MAP-Elites sampling continuity across an end-to-end resumed trace.


- [ ] Enforce validator container, filesystem-capability, and resource-limit policy.
  - Spec evidence: AlphaEvolve targets existing codebases and systems code,
    potentially with expensive or hardware-backed execution.
  - Current evidence: validator execution is intentionally process separation,
    not a security sandbox. Candidates are materialized into a temporary
    candidate root and validators run with `cwd` set there; validators receive
    an explicit minimal/allowlisted environment; stage/sample wall-clock
    budgets bound attempts; timeout cleanup uses process groups or Windows
    kill-on-close job objects plus process-tree termination; problem-local
    helper/data access is limited to declared entrypoint, companion, and data
    provenance; copied evaluator artifacts are bounded, hashed, optionally
    redacted, and link-aware; and `evaluation.metadata.validator_boundary`
    explicitly declares local subprocess execution, unsupported
    sandbox/container, candidate-root plus declared-problem-file filesystem
    policy, validator network mode, Python-socket-denial metadata when
    configured, wall-clock-only timeout limits, unsupported
    CPU/memory/GPU/disk/process-count limits, and the current
    minimal-environment/redacted-output secret boundary. Startup manifests now
    also persist
    `policies.validator_execution` with schema
    `libreevolve.validator_execution_policy.v1`, repeating the configured
    local-subprocess boundary, filesystem scope, structured
    `filesystem_capabilities`, network mode, wall-clock-only limit policy,
    structured `resource_limit_policy`, unsupported CPU/memory/GPU/disk/
    process-count quotas, secret boundary, and the per-evaluation metadata
    field that carries the attempt-level boundary. The structured filesystem
    record declares candidate-root read/write/execute scope, declared
    problem-file read/execute and no-write scope, bounded evaluator-artifact
    copy-out, and unsupported ambient host-filesystem sandboxing. The
    structured resource record declares local subprocess timeout cleanup as the
    only supported quota mechanism and explicitly marks CPU, memory, GPU, disk,
    process-count, and container-runtime quotas unsupported.
    `validate_validator_execution_policy()` now validates the startup policy
    record itself, including schema, local subprocess execution, unsupported
    sandbox/container claims, filesystem-capability structure, network mode and
    denial scope, wall-clock-only limits, unsupported CPU/memory/GPU/disk/
    process-count quotas, and the required pointer to per-evaluation boundary
    metadata. Startup policy records now also carry
    `validate_validator_boundary_consistency.v1` plus the exact shared fields
    used to compare manifest policy claims with attempt-level
    `evaluation.metadata.validator_boundary`; the consistency validator checks
    execution, filesystem-capability, network, resource-limit, and
    secret-boundary agreement while still reporting `sandbox_ready: false`.
  - Remaining gap: there is still no configurable container/security sandbox,
    no OS/container-grade network egress sandbox, no proof that native
    extensions, subprocesses, or alternate runtimes cannot connect out, no
    OS-enforced filesystem capability model beyond candidate-root execution
    plus problem-local provenance/artifact/data declarations, no CPU, memory,
    GPU, disk, or process-count quotas, no network-mediated provider credential
    boundary audit, and no resumable distributed evaluator worker state. The
    remaining gap is not startup validator policy-record validation or
    policy-to-boundary consistency validation.
  - Required result: define and enforce configurable sandbox/container,
    filesystem capability, OS/container network capability, and resource-limit
    policy for validators, with manifest-visible evidence and tests proving the
    intended boundary.

- [ ] Add automated run-artifact validator-boundary consistency checks.
  - Spec evidence: AlphaEvolve-scale evaluation provenance should make the
    execution boundary for generated-code validators auditable from the run
    artifacts that support accepted or rejected candidates.
  - Current evidence: startup manifests persist
    `policies.validator_execution`, each evaluation metadata record carries
    `evaluation.metadata.validator_boundary`, and
    `validate_validator_boundary_consistency()` can compare the startup policy
    with an attempt-level boundary across execution, filesystem-capability,
    network, resource-limit, and secret-boundary fields. The helper is covered
    by direct validator-policy tests, while runtime code emits the policy and
    boundary records rather than automatically invoking the helper over
    persisted history/evaluation rows.
  - Remaining gap: there is no run-finalization, CLI, or CI artifact validator
    that loads `manifest.json`, scans persisted evaluation attempts, requires
    every attempt-level `validator_boundary` record to exist, applies the
    consistency helper, and fails missing or drifting boundary claims before a
    run artifact bundle is treated as AlphaEvolve-grade evidence.
  - Required result: add a manifest/history validation pass with tests for
    missing boundary metadata, mismatched network/filesystem/resource/secret
    fields, legacy rows, and clean current runs; wire it into the routine
    artifact verification path without confusing this consistency gate with
    the separate sandbox/resource-enforcement gap.

- [ ] Add official 2026 AlphaEvolve impact-source provenance and claim
      boundaries.
  - Spec evidence: the May 7, 2026 Google DeepMind article
    `AlphaEvolve: How our Gemini-powered coding agent is scaling impact across
    fields` says the system has broadened from the original 2025 announcement
    into health, sustainability, research, infrastructure, and commercial
    deployments. It reports source-specific claims such as a 30% DeepConsensus
    variant-detection error reduction, AC Optimal Power Flow feasibility
    rising from 14% to over 88%, Earth AI disaster-risk accuracy improving by
    5%, Willow quantum-circuit suggestions with 10x lower error, Spanner
    write-amplification reduction by 20%, compiler storage footprint reduction
    by nearly 9%, and customer cases involving Klarna, Substrate, FM Logistic,
    WPP, and Schrodinger. The article also introduces public gallery links and
    names UI/API scaling contributors.
  - Current evidence: existing source TODOs cover the original AlphaEvolve
    white paper, the original May 2025 DeepMind announcement, the
    `alphaevolve_results` notebook repository, the follow-on 67-problem
    repository/paper/blog, and selected later theoretical-CS sources. No code
    source manifest, claim registry, benchmark report, or paper-index status
    row captures this 2026 impact article, its outbound links, deployment and
    customer-claim categories, UI/API attribution, or source-specific
    claim-value variants.
  - Required result: add source-artifact and claim-boundary metadata for the
    2026 impact article: canonical URL, publication date, author/team, title,
    retrieval timestamp/hash, outbound source links, claim ids, domain
    category, value/unit/baseline, linked paper/repository/artifact evidence
    when available, deployment/customer/public-gallery/UI/API attribution
    labels, unsupported-local-benchmark flags, and README/ROADMAP wording that
    treats these as newer official impact claims rather than implemented
    LibreEvolve behavior or original AlphaEvolve specification evidence.

- [ ] Add AlphaEvolve FHE-on-TPU application source and benchmark boundary.
  - Spec evidence: arXiv `2605.14718`, `Adapting AlphaEvolve to Optimize
    Fully Homomorphic Encryption on TPUs`, submitted May 14, 2026, frames
    AlphaEvolve optimization as hardware-aware cryptographic-kernel search for
    FHE. The abstract says the work uses real hardware execution feedback and
    rigorous correctness testing on Google Cloud TPUv5e for TFHE/Jaxite and
    CKKS/CROSS primitives, reporting 2.5x TFHE bootstrap latency improvement
    and 1.31x/1.18x CKKS rotation/multiplication latency improvements over
    human-engineered state of the art.
  - Current evidence: the local paper cache and implementation-status rows do
    not include `2605.14718`; existing hardware/compiler TODOs cover original
    AlphaEvolve Section 3.3 TPU/circuit/FlashAttention/compiler contexts and
    2026 impact-source claims, but not FHE-specific cryptographic kernels,
    TPUv5e execution, TFHE/Jaxite or CKKS/CROSS primitives, hardware feedback
    traces, correctness-test provenance, or the reported FHE latency metrics.
  - Required result: add paper/source manifest coverage and benchmark/report
    boundaries for FHE-on-TPU work: arXiv id/version/date/PDF hash, authors,
    source-license metadata, primitive/scheme ids, TPU version and execution
    environment, baseline implementation identity, generated optimization
    artifact hashes, hardware-feedback traces, correctness-test inputs and
    acceptance criteria, latency metric definitions, speedup values and units,
    and README/ROADMAP wording that keeps this as a missing application-domain
    benchmark until local FHE kernels, TPU execution, and correctness reports
    exist.

- [ ] Add AlphaEvolve intentmaking/sensemaking HCI source boundary.
  - Spec evidence: arXiv `2605.05921`, `Intentmaking and Sensemaking: Human
    Interaction with AI-Guided Mathematical Discovery`, submitted May 7, 2026,
    reports a formative user study with 11 expert mathematicians using
    AlphaEvolve on advanced problems. The abstract defines `intentmaking` as
    iterative discovery, definition, and refinement of experimental goals
    through active system interaction, paired with sensemaking over results,
    and frames AlphaEvolve-style tools as collaborative instruments rather
    than question/answer assistants.
  - Current evidence: local code/TODOs track prompt construction, run
    manifests, `libreevolve show`, source provenance, follow-on problem
    notebooks, and 2026 impact-source UI/API attribution, but no source
    manifest or feature boundary captures the AlphaEvolve HCI/user-study
    surface. There is no interactive experiment-planning UI, intent revision
    log, user-study session model, result-sensemaking dashboard, or workflow
    metadata distinguishing human goal refinement from autonomous backend
    evolution.
  - Required result: add source-manifest and feature-boundary records for
    `2605.05921`: arXiv id/version/date/PDF hash, authors, study population,
    task/problem identifiers, interaction/session trace schema, intentmaking
    and sensemaking event categories, UI/dashboard artifact status, human
    intervention and goal-revision boundaries, privacy/consent or redaction
    policy for study data, and README/ROADMAP wording that keeps HCI claims
    source-scoped until local interactive workflow evidence exists.

- [ ] Add AlphaEvolve radar power-allocation application source boundary.
  - Spec evidence: arXiv `2605.01794`, `Discover Fast Power Allocation
    Solution for Multi-Target Tracking via AlphaEvolve Evolution`, submitted
    May 3, 2026, applies LLM-guided evolutionary search to radar resource
    allocation. The abstract says AlphaEvolve discovers a compact
    interpretable scoring function over physically inspired features, then
    transforms it into feasible power allocations with a deterministic
    constraint-satisfying transformation, reaching average relative
    performance loss of only 1.51%, reliable generalization across scenarios
    and target counts, and over three orders of magnitude speedup versus
    conventional iterative solvers.
  - Current evidence: the local paper cache, source manifests, benchmark
    contracts, and TODO coverage do not include `2605.01794`; existing
    AlphaEvolve application rows cover compiler/hardware/systems/math/FHE/HCI
    contexts but not radar multi-target tracking, power-allocation feasibility
    transforms, closed-form symbolic search, scenario/target-count
    generalization, or iterative-solver speedup baselines.
  - Required result: add source-manifest and benchmark-boundary metadata for
    `2605.01794`: arXiv id/version/date/PDF hash, authors, radar task and
    scenario taxonomy, target-count ranges, state-feature schema, evolved
    scoring-function artifact, deterministic feasibility transform,
    constraints, iterative-solver baseline identity, tracking-accuracy metric,
    relative-loss and speedup records, generalization split metadata, and
    README/ROADMAP wording that keeps this as missing application-domain
    evidence until local radar fixtures and reports exist.

- [ ] Add EvoX meta-evolution source boundary before adaptive-search claims.
  - Spec evidence: arXiv `2602.23413`, `EvoX: Meta-Evolution for Automated
    Discovery`, was submitted February 26, 2026 and revised March 16, 2026.
    Its abstract says recent systems such as AlphaEvolve reuse evaluated
    solutions to guide LLM-driven evolution, but fixed search strategies and
    predefined knobs such as explore/exploit ratios can fail to adapt across
    tasks or phases. EvoX jointly evolves candidate solutions and the search
    strategies that generate them, dynamically shifting strategies, and
    reports outperforming AlphaEvolve, OpenEvolve, GEPA, and ShinkaEvolve on
    the majority of nearly 200 real-world optimization tasks.
  - Current evidence: LibreEvolve currently documents a fixed default `mixed`
    parent-selection policy with 30% explore and 70% exploit, plus explicit
    parent-selection strategies that bypass that ratio. The code/source
    ledgers do not include `2602.23413`, adaptive strategy genomes,
    meta-evolution controller state, strategy-credit assignment, per-task
    search-policy traces, or benchmark rows comparing fixed-ratio search
    against adaptive EvoX-style evolution.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2602.23413`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve's fixed sampling knobs,
    strategy-representation schema, controller-state artifacts,
    strategy-selection provenance, task-suite taxonomy, baseline method
    identities, win-rate/score/token metrics, ablation requirements, and
    README/ROADMAP wording that keeps EvoX-style adaptive meta-evolution as
    missing research evidence until local strategy evolution and benchmark
    reports exist.

- [ ] Add DeltaEvolve semantic-delta context source boundary.
  - Spec evidence: arXiv `2602.02919`, `DeltaEvolve: Accelerating Scientific
    Discovery through Momentum-Driven Evolution`, was submitted February 2,
    2026. Its abstract says AlphaEvolve-style LLM-driven evolutionary systems
    rely on full-code histories that can be context-inefficient and weak as
    evolutionary guidance. DeltaEvolve reframes evolutionary agents as an
    Expectation-Maximization process, replaces full-code history with
    structured semantic deltas that capture how and why modifications between
    successive nodes affect performance, and uses a multi-level database plus
    progressive disclosure to reduce input tokens while improving results
    across diverse scientific tasks.
  - Current evidence: LibreEvolve records prompts, parent programs, SEARCH/
    REPLACE diffs, run history, and a small in-memory failed-proposal snippet
    list, but it does not preserve semantic deltas as first-class records or
    use them as prompt-control context. There is no delta-effect schema,
    causal/performance attribution for successive program nodes, multi-level
    semantic-delta memory, progressive-disclosure policy, token-savings report,
    or benchmark comparing full-code parent context against DeltaEvolve-style
    momentum guidance.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2602.02919`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve prompt construction,
    semantic-delta schema, node-to-node effect attribution, performance-change
    records, multi-level database/indexing metadata, progressive-disclosure
    traces, token-accounting metrics, scientific-task benchmark taxonomy,
    baseline identities, and README/ROADMAP wording that treats semantic-delta
    momentum guidance as missing evidence until local storage, prompt assembly,
    and benchmark artifacts exist.

- [ ] Add MLEvolve long-horizon ML-engineering source boundary.
  - Spec evidence: arXiv `2606.06473`, `MLEvolve: A Self-Evolving Framework
    for Automated Machine Learning Algorithm Discovery`, was submitted June 4,
    2026. Its abstract presents an LLM-based self-evolving multi-agent
    framework for end-to-end machine learning algorithm discovery, extending
    tree search to Progressive MCGS with graph-based reference edges for
    cross-branch information flow, shifting from exploration to exploitation
    with an entropy-inspired progressive schedule, adding Retrospective Memory
    with a cold-start domain knowledge base plus dynamic global memory, and
    decoupling strategic planning from code generation with adaptive coding
    modes. It reports MLE-Bench state-of-the-art metrics under a 12-hour
    budget and outperformance of AlphaEvolve on mathematical algorithm
    optimization tasks.
  - Current evidence: LibreEvolve has MAP-Elites archives, islands, prompt
    history, fixed mixed parent selection, and limited failed-proposal memory,
    but no MLE-Bench task harness, Progressive Monte Carlo Graph Search,
    graph-based cross-branch reference edges, entropy-scheduled explore/
    exploit controller, cold-start MLE knowledge base, dynamic retrospective
    memory, strategic-planning/code-generation mode separation, or valid
    submission/medal-rate report artifacts.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2606.06473`: arXiv id/version/date/PDF hash, authors, source license,
    linked code URL/status, relation to AlphaEvolve and LibreEvolve search,
    Progressive MCGS state schema, graph-reference edge provenance,
    entropy-schedule records, retrospective-memory schema, adaptive coding
    mode artifacts, MLE-Bench task/submission metadata, 12-hour budget and
    metric definitions, mathematical-algorithm baseline identities, and
    README/ROADMAP wording that keeps MLEvolve-style long-horizon MLE support
    as missing evidence until local harnesses and reports exist.

- [ ] Add LEVI cost-aware search-architecture source boundary.
  - Spec evidence: arXiv `2605.09764`, `LEVI: Stronger Search Architectures
    Can Substitute for Larger LLMs in Evolutionary Search`, was submitted May
    10, 2026. Its abstract says AlphaEvolve-style LLM-guided evolutionary
    methods are effective but expensive because of frontier-model reliance,
    weak diversity preservation, blind model use for local edits, and
    full-set evaluation over redundant examples. LEVI proposes a
    harness-first framework with an explicitly diversity-preserving solution
    database, smarter mutation routing between large and small LLMs, and a
    rank-preserving proxy benchmark for rollout-heavy settings. It reports
    systems-research benchmark scores at 3.3x-6.7x lower budget than
    frontier-model runs and one 35x lower-cost match, plus prompt-optimization
    results at less than half GEPA's rollout budget.
  - Current evidence: LibreEvolve has MAP-Elites cells, island migration, a
    heuristic LLM ensemble, run manifests, and evaluator artifacts, but no
    LEVI source row, cost-aware mutation router, explicit large/small model
    role split, diversity-preservation report for the solution database,
    proxy-benchmark calibration, rank-preservation test, rollout-budget
    accounting, or systems/prompt optimization cost-comparison fixture.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.09764`: arXiv id/version/date/PDF hash, authors, source license,
    linked code URL/status, relation to AlphaEvolve and LibreEvolve's archive
    and ensemble behavior, diversity metrics and database invariants,
    mutation-router policy schema, large/small model assignment traces,
    proxy-benchmark construction and rank-correlation evidence,
    rollout-budget/cost accounting, systems and prompt-optimization benchmark
    taxonomy, baseline identities, and README/ROADMAP wording that keeps
    LEVI-style cost-aware search architecture as missing evidence until local
    implementation and reports exist.

- [ ] Add PACEvolve long-horizon consistency source boundary.
  - Spec evidence: arXiv `2601.10657`, `PACEvolve: Enabling Long-Horizon
    Progress-Aware Consistent Evolution`, was submitted January 15, 2026 and
    revised January 16, 2026. Its abstract says current LLM-in-the-loop
    evolutionary systems lack systematic process management and suffer from
    context pollution, mode collapse, and weak collaboration. PACEvolve
    combines hierarchical context management with pruning, momentum-based
    backtracking to escape local minima, and a self-adaptive sampling policy
    that unifies backtracking and crossover for dynamic search coordination,
    reporting state-of-the-art results on LLM-SR and KernelBench plus
    record-surpassing solutions on Modded NanoGPT.
  - Current evidence: LibreEvolve has prompt history, recent failed-child
    snippets, fixed mixed parent sampling, island migration, MAP-Elites
    retention, and archive/run manifests, but no PACEvolve source row, no
    context-pollution detector, no hierarchical context pruning policy, no
    momentum-based backtracking controller, no unified crossover/backtracking
    sampler, no weak-collaboration diagnostics across parallel trajectories,
    and no LLM-SR, KernelBench, or Modded NanoGPT benchmark reports.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2601.10657`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve prompt/search dynamics,
    context-pollution metrics, hierarchical context-management artifacts,
    pruning policy traces, mode-collapse/stagnation diagnostics,
    momentum-backtracking state, crossover/backtracking coordination schema,
    adaptive sampling records, trajectory-collaboration evidence, LLM-SR/
    KernelBench/Modded-NanoGPT benchmark taxonomy, baseline identities, and
    README/ROADMAP wording that keeps PACEvolve-style consistency support as
    missing evidence until local implementation and reports exist.

- [ ] Add FlashEvolve asynchronous-stage source boundary.
  - Spec evidence: arXiv `2605.08520`, `FlashEvolve: Accelerating Agent
    Self-Evolution with Asynchronous Stage Orchestration`, was submitted May
    8, 2026. Its abstract says LLM-based evolution is bottlenecked by
    synchronized stage execution and imbalance inside LLM-heavy stages.
    FlashEvolve replaces synchronized execution with asynchronous workers and
    queues so stages and evolution steps overlap, tracks artifact versions,
    applies policies to update, discard, or patch stale artifacts, treats
    language-space staleness as inspectable and repairable, and adds
    speculative stage completion plus adaptive workflow control. It reports
    GEPA proposal-throughput gains of 3.5x on local vLLM and 4.9x on API
    serving, with applicability to ACE and Meta-Harness.
  - Current evidence: LibreEvolve runs a mostly synchronous generation,
    validation, admission, archive-update, and migration loop with sequential
    reviewer calls and manifest/audit artifacts. It has no FlashEvolve source
    row, asynchronous worker/queue orchestration, per-stage queue-state
    artifacts, artifact-version lineage, stale-item classification, reflective
    stale-patch workflow, speculative stage-completion policy, adaptive
    workflow controller, or throughput/token-efficiency report.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.08520`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve's synchronous loop, worker and
    queue schemas, stage-overlap traces, artifact-version provenance,
    staleness classification and policy outcomes, reflective patch artifacts,
    speculative-completion records, adaptive workflow-control metrics,
    throughput/token-efficiency measurements, GEPA/vLLM/API baseline
    identities, ACE/Meta-Harness applicability boundaries, and README/ROADMAP
    wording that keeps FlashEvolve-style async orchestration as missing
    evidence until local implementation and reports exist.

- [ ] Add evolutionary-agent trace-diagnostics source boundary.
  - Spec evidence: arXiv `2605.20086`, `What Do Evolutionary Coding Agents
    Evolve?`, was submitted May 25, 2026. Its abstract argues that aggregate
    benchmark scores hide how evolutionary coding agents improve programs,
    whether gains come from structural innovation or overfitting, and how
    search behavior changes across tasks. It introduces EvoTrace to annotate
    edit types, dependency structures, and fitness trajectories, and
    EvoReplay to intervene on search traces. The paper reports recurring
    cycling and overfitting, task-dependent division between constant-tuning
    and genuinely new logic, and sensitivity to population structure and
    prompt content across AlphaEvolve-style agents such as AlphaEvolve,
    OpenEvolve, and FunSearch.
  - Current evidence: LibreEvolve records history JSONL, archive events,
    prompt history, evaluator artifacts, accepted/rejected programs, and best
    programs, but it does not annotate edit mechanisms or provide replayable
    intervention traces. There is no edit-type taxonomy, dependency graph,
    fitness-trajectory classifier, cycling detector, overfitting-vs-innovation
    label, constant-tuning/new-logic split, prompt-content sensitivity report,
    population-structure ablation, or EvoReplay-style counterfactual
    intervention tool.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.20086`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve run-history artifacts, edit-type
    annotation schema, dependency-structure extraction, fitness-trajectory
    records, cycling and overfitting diagnostics, structural-innovation
    labels, population/prompt ablation metadata, replay-intervention API,
    counterfactual outcome records, benchmark/task taxonomy, baseline-agent
    identities, and README/ROADMAP wording that keeps mechanistic discovery
    claims source-scoped until local trace diagnostics and replay reports
    exist.

- [ ] Add Zarankiewicz reinforced-search application source boundary.
  - Spec evidence: arXiv `2605.01120`, `New Bounds for Zarankiewicz Numbers
    via Reinforced LLM Evolutionary Search`, was submitted May 1, 2026 and
    revised May 7, 2026. Its abstract says OpenEvolve, an open-source
    AlphaEvolve-style LLM evolutionary algorithm, produced exact values for
    `Z(11,21,3,3)=116`, `Z(11,22,3,3)=121`, and `Z(12,22,3,3)=132`; lower
    bounds for 41 more Zarankiewicz numbers; and four matched closed cases.
    It reports generation algorithms, implementation details, and costs under
    `$30` per Zarankiewicz parameter combination.
  - Current evidence: LibreEvolve tracks AlphaEvolve, selected math sources,
    benchmark contracts, prompt/run artifacts, and cost-aware search papers,
    but no Zarankiewicz source row or runnable extremal-graph fixture. There
    is no bipartite-graph construction evaluator, `K_{s,t}`-free verifier,
    exact/lower-bound table, generated construction algorithm capture,
    proof/check artifact, parameter-combination manifest, reproducible cost
    accounting, or OpenEvolve-to-LibreEvolve application boundary.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.01120`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve/OpenEvolve and LibreEvolve, Zarankiewicz
    parameter schema, bipartite graph representation, `K_{s,t}`-free
    validation logic, exact-value/lower-bound records, generated construction
    algorithm artifacts, computational-cost report, verifier/proof status,
    benchmark baselines and upper-bound references, reproducibility metadata,
    and README/ROADMAP wording that keeps Zarankiewicz discovery claims as
    missing application evidence until local fixtures and reports exist.

- [ ] Add CORAL autonomous multi-agent evolution source boundary.
  - Spec evidence: arXiv `2604.01658`, `CORAL: Towards Autonomous Multi-Agent
    Evolution for Open-Ended Discovery`, was submitted April 2, 2026 and
    revised May 17, 2026. Its abstract says LLM-based evolution for
    open-ended discovery still relies on fixed heuristics and hard-coded
    exploration rules, limiting agent autonomy. CORAL replaces rigid control
    with long-running agents that explore, reflect, and collaborate through
    shared persistent memory, asynchronous multi-agent execution, and
    heartbeat-based interventions, while adding safeguards such as isolated
    workspaces, evaluator separation, resource management, and agent session
    and health management. It reports state-of-the-art results on 10
    mathematical, algorithmic, and systems optimization tasks, 3-10x higher
    improvement rates with fewer evaluations, and a kernel-engineering score
    improvement from 1363 to 1103 cycles.
  - Current evidence: LibreEvolve has islands, ring migration, MAP-Elites
    archives, prompt/run artifacts, evaluator subprocesses, and migration
    event logs, but no CORAL source row or autonomous multi-agent runtime.
    There is no long-running agent session model, shared persistent agent
    memory, asynchronous collaboration protocol, heartbeat intervention
    mechanism, isolated per-agent workspace, evaluator separation contract
    beyond local validator subprocesses, resource quota manager, session
    health monitor, communication/knowledge-reuse trace, or multi-agent
    benchmark report.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2604.01658`: arXiv id/version/date/PDF hash, authors, source license,
    linked code URL/status, relation to AlphaEvolve and LibreEvolve islands,
    agent-session schema, shared memory/index artifacts, async execution and
    communication traces, heartbeat intervention records, workspace isolation
    policy, evaluator-separation invariants, resource-management telemetry,
    health-check events, knowledge-reuse evidence, mathematical/algorithmic/
    systems benchmark taxonomy, kernel-engineering metric records, baseline
    identities, and README/ROADMAP wording that keeps CORAL-style autonomous
    multi-agent evolution as missing evidence until local implementation and
    reports exist.

- [ ] Add AEvo harnessed meta-editing source boundary.
  - Spec evidence: arXiv `2605.13821`, `Harnessing Agentic Evolution`, was
    submitted May 13, 2026. Its abstract frames agentic evolution as iterative
    generation, evaluation, and feedback-guided search, but says existing
    systems are either fixed hand-designed procedures that are modular but
    rigid or general-purpose agents that can drift in long-horizon evolution.
    AEvo formulates evolution as an interactive environment where accumulated
    candidates, feedback, traces, and failures become process-level state; a
    meta-agent observes that state and edits the procedure or agent context
    controlling future evolution rather than directly proposing the next
    candidate. It reports a 26 relative improvement over the strongest of
    five evolution baselines and state-of-the-art results on three
    open-ended optimization tasks under the same iteration budget.
  - Current evidence: LibreEvolve records prompts, failures, history streams,
    archives, run manifests, and static configuration, but it has no AEvo
    source row or process-level environment state for meta-editing the
    evolutionary controller. There is no meta-agent role, no procedure/context
    patch schema, no state observation contract over accumulated evidence, no
    policy for safely editing prompts/config/search mechanisms mid-run, no
    rollback/versioning for control edits, and no benchmark separating
    candidate-generation improvements from evolution-procedure improvements.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.13821`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve's fixed controller/config,
    process-state schema, accumulated evidence inventory, meta-agent action
    schema, procedure/context patch artifacts, control-edit provenance,
    rollback/versioning policy, drift/stability diagnostics, iteration-budget
    accounting, agentic/reasoning/open-ended benchmark taxonomy, baseline
    identities, and README/ROADMAP wording that keeps AEvo-style harnessed
    meta-editing as missing evidence until local implementation and reports
    exist.

- [ ] Add G-Zero verifier-free co-evolution source boundary.
  - Spec evidence: arXiv `2605.09959`, `G-Zero: Self-Play for Open-Ended
    Generation from Zero Data`, was submitted May 11, 2026. Its abstract says
    self-evolving LLMs perform well in verifiable domains but struggle on
    open-ended tasks because proxy LLM judges create capability bottlenecks
    and reward-hacking risks. G-Zero introduces a verifier-free co-evolution
    framework with `Hint-delta`, an intrinsic reward measuring predictive
    shift between an unassisted Generator response and a response conditioned
    on a self-generated hint. A Proposer is trained with GRPO to target the
    Generator's blind spots by creating queries and hints, while the Generator
    is trained with DPO to internalize the hint-guided improvements. The
    abstract also states a best-iterate suboptimality guarantee under
    sufficient exploration coverage and low pseudo-label score noise.
  - Current evidence: LibreEvolve depends on explicit user validators and
    evaluator scores for program admission, MAP-Elites retention, and
    benchmark reporting. It has no G-Zero source row, no verifier-free
    open-ended task mode, no Generator/Proposer co-evolution loop, no
    Hint-delta intrinsic reward, no self-generated hint artifacts, no GRPO/DPO
    training interface, no exploration-coverage diagnostic, and no
    pseudo-label noise filter or reward-hacking audit for unverifiable tasks.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.09959`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve's evaluator contract, Generator
    and Proposer role schemas, Hint-delta computation records, unassisted vs
    hint-conditioned response pairs, self-generated query/hint artifacts,
    GRPO/DPO training traces, intrinsic-reward calibration, exploration
    coverage metrics, pseudo-label noise filters, reward-hacking diagnostics,
    open-ended task taxonomy, theoretical guarantee assumptions, baseline
    identities, and README/ROADMAP wording that keeps verifier-free
    co-evolution as missing evidence until local implementation and reports
    exist.

- [ ] Add GenEvolve multimodal trajectory-distillation source boundary.
  - Spec evidence: arXiv `2605.21605`, `GenEvolve: Self-Evolving Image
    Generation Agents via Tool-Orchestrated Visual Experience Distillation`,
    was submitted May 20, 2026 and revised May 22, 2026. Its abstract says
    high-quality open-ended image generation now requires agents to combine a
    model's internal generative ability with external resources. GenEvolve
    models each generation attempt as a tool-orchestrated trajectory where
    the agent gathers evidence, selects references, invokes generation skills,
    and composes them into a prompt-reference program. It compares multiple
    trajectories for the same request, abstracts best-worst differences into
    structured visual experience for a privileged teacher branch, and uses
    Visual Experience Distillation to give dense token-level supervision so a
    student internalizes better search, knowledge activation, reference
    selection, and prompt construction.
  - Current evidence: LibreEvolve evolves Python programs through text
    SEARCH/REPLACE diffs with scalar evaluator scores, prompt history, and
    run artifacts, but it has no GenEvolve source row or multimodal
    image-generation agent pathway. There is no visual tool trajectory schema,
    reference/evidence selection log, prompt-reference program artifact,
    best-worst trajectory comparison, structured visual experience record,
    privileged teacher branch, dense token-level distillation trace, student
    policy update, image artifact lineage, or GenEvolve-Bench-style report.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.21605`: arXiv id/version/date/PDF hash, authors, source license,
    project/demo URL status, relation to AlphaEvolve and LibreEvolve's
    text-program search, tool-orchestrated trajectory schema, reference and
    evidence selection artifacts, prompt-reference program representation,
    best-worst trajectory comparison records, structured visual experience
    taxonomy, privileged-teacher/student-distillation traces, token-level
    supervision metadata, image artifact provenance, GenEvolve-Data/
    GenEvolve-Bench task taxonomy, baseline identities, and README/ROADMAP
    wording that keeps multimodal trajectory distillation as missing evidence
    until local implementation and reports exist.

- [ ] Add EvoRubric self-evolving reward-rubric source boundary.
  - Spec evidence: arXiv `2605.29847`, `EvoRubric: Self-Evolving
    Rubric-Driven RL for Open-Ended Generation`, was submitted May 28, 2026.
    Its abstract says RL has advanced LLMs in verifiable domains, but
    open-ended generation lacks definitive rewards. Static human rubrics can
    create policy lag, while external proprietary rubric generators are
    expensive. EvoRubric unifies response generation and rubric generation
    under one parameterized policy that alternates between Reasoner and Rubric
    Generator roles, uses a meta-verifier, zero-variance pruning, and
    Leave-One-Out peer consensus to reduce reward hacking, archives validated
    criteria into memory, and yields dense multi-objective rewards for medical,
    writing, and science domains.
  - Current evidence: LibreEvolve uses explicit evaluator functions, scalar
    or structured scores, and MAP-Elites admission/retention rather than
    learned or self-evolving rubrics. It has no EvoRubric source row, no
    Reasoner/Rubric-Generator role split, no generated-rubric artifact
    storage, no meta-verifier, no zero-variance pruning, no Leave-One-Out peer
    consensus, no rubric memory pool, no dense multi-objective reward schema,
    and no reward-hacking audit for open-ended generation domains.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.29847`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve's evaluator/scoring contract,
    Reasoner/Rubric-Generator role schema, generated-rubric provenance,
    meta-verifier records, zero-variance pruning decisions, peer-consensus
    traces, rubric memory-pool entries, dense reward-vector definitions,
    reward-hacking diagnostics, expert-prior initialization metadata,
    medical/writing/science benchmark taxonomy, baseline identities, and
    README/ROADMAP wording that keeps self-evolving rubric rewards as missing
    evidence until local implementation and reports exist.

- [ ] Add LLM-ALSO adaptive learning-signal source boundary.
  - Spec evidence: arXiv `2605.29293`, `LLM-ALSO: LLM-Driven Adaptive
    Learning-Signal Optimization for Multi-Agent Reinforcement Learning`, was
    submitted May 28, 2026. Its abstract says effective training-time
    guidance is difficult in sparse-reward cooperative MARL, and existing
    LLM-based learning-signal methods are mostly single-agent, one-shot, or
    weakly validated against evolving training dynamics. LLM-ALSO decomposes
    adaptation into iterative diagnosis, proposal, and validation: a Critic
    LLM diagnoses stage-specific learning and coordination failures from
    sparse-return metrics and compact behavior evidence; a Generator LLM
    proposes reward-shaping configurations conditioned on the diagnosis; and
    branch-validation feedback refines candidates before updates affect the
    main training trajectory.
  - Current evidence: LibreEvolve supports scalar/structured evaluator scores,
    plugins, and run artifacts, but it has no LLM-ALSO source row, no
    sparse-reward MARL training harness, no Critic/Generator learning-signal
    roles, no stage-specific coordination-failure diagnosis, no
    reward-shaping configuration artifact, no branch-validation trajectory,
    no promotion gate for validated reward updates, and no learning-efficiency
    report for cooperative MARL tasks.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.29293`: arXiv id/version/date/PDF hash, authors, source license,
    relation to AlphaEvolve and LibreEvolve evaluator/reward contracts,
    Critic/Generator role schemas, sparse-return and compact-behavior evidence
    records, stage-specific diagnosis artifacts, reward-shaping configuration
    schema, branch-validation traces, update-promotion criteria, main-training
    trajectory provenance, sparse-reward cooperative MARL task taxonomy,
    learning-efficiency metrics, baseline identities, and README/ROADMAP
    wording that keeps adaptive learning-signal optimization as missing
    evidence until local implementation and reports exist.

- [ ] Add MemEvolve meta-evolving memory-architecture source boundary.
  - Spec evidence: arXiv `2512.18746`, `MemEvolve: Meta-Evolution of Agent
    Memory Systems`, was submitted December 21, 2025. Its abstract says
    self-evolving LLM agents typically rely on manually engineered memory
    architectures for trajectory storage, experience distillation, and tool
    synthesis, but the memory architecture itself remains static. MemEvolve
    jointly evolves experiential knowledge and the memory architecture, and
    introduces EvolveLab as a unified codebase that distills twelve
    representative memory systems into a modular design space covering
    encode, store, retrieve, and manage. It reports up to 17.06% improvements
    for frameworks such as SmolAgent and Flash-Searcher plus cross-task and
    cross-LLM generalization.
  - Current evidence: LibreEvolve stores run artifacts, prompt history,
    failure snippets, archive events, and best programs, but these are fixed
    artifact schemas rather than evolvable memory architecture components.
    There is no MemEvolve source row, no explicit encode/store/retrieve/manage
    memory design space, no memory-architecture genotype, no memory-system
    mutation/evaluation loop, no architecture-transfer report, no EvolveLab
    benchmark mapping, and no comparison against static memory baselines.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2512.18746`: arXiv id/version/date/PDF hash, authors, source license,
    linked code URL/status, relation to AlphaEvolve and LibreEvolve run memory,
    memory component taxonomy, encode/store/retrieve/manage schema,
    memory-architecture mutation records, experiential-knowledge artifacts,
    joint content/architecture evolution traces, memory baseline identities,
    EvolveLab benchmark taxonomy, cross-task and cross-LLM transfer metrics,
    performance-delta records, reproducibility status, and README/ROADMAP
    wording that keeps meta-evolving memory systems as missing evidence until
    local implementation and reports exist.

- [ ] Add ANCHOR human-like oversight and norm-correction source boundary.
  - Spec evidence: arXiv `2606.06114`, `Towards Healthy Evolution: Exploring
    the Role and Mechanisms of Human-Agent Interaction in Self-Evolving
    Systems`, was submitted June 4, 2026. Its abstract introduces Agent Norm
    Correction through Human-like Oversight and Review (ANCHOR), an LLM-based
    framework that simulates human supervision and delivers feedback at
    several phases of self-evolution. The paper reports that limited
    supervision mitigates safety degradation while preserving core objective
    performance, that output-verification supervision is the most effective
    intervention point, and that higher supervision frequency has diminishing
    returns.
  - Current evidence: LibreEvolve records evaluator results, prompt history,
    failed proposals, quarantine streams, and local validity/admission
    decisions, but it has no ANCHOR source row, no human-like oversight agent,
    no phase-specific norm-correction interface, no safety-drift metric
    lineage, no supervision-cadence policy, no output-verification
    intervention record, no reflection/review artifact stream, and no
    experiment report separating core-task performance from safety
    degradation during self-evolution.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2606.06114`: arXiv id/version/date/PDF hash, authors, source
    license, relation to AlphaEvolve and LibreEvolve's validator/admission
    model, ANCHOR oversight-role schema, phase-specific intervention points,
    norm-correction feedback artifacts, safety-drift metrics, output-
    verification review records, supervision-frequency/cadence traces,
    reflection/review logs, preservation-of-objective-performance reports,
    safety benchmark taxonomy, baseline identities, diminishing-return
    analysis fields, and README/ROADMAP wording that keeps human-like
    oversight and healthy-evolution claims as missing evidence until local
    implementation and reports exist.

- [ ] Add SIA harness-plus-weight self-improvement source boundary.
  - Spec evidence: arXiv `2605.27276`, `SIA: Self Improving AI with Harness
    & Weight Updates`, was submitted May 26, 2026. Its abstract says two
    separate self-improvement lines currently either let a meta-agent rewrite
    the harness or scaffold of a task-specific agent while holding model
    weights fixed, or use test-time training to update model weights while
    holding the harness fixed. SIA unifies those levers through a
    Feedback-Agent that updates both the harness and the weights of a
    task-specific agent, evaluating Chinese legal charge classification,
    low-level GPU kernel optimization, and single-cell RNA denoising. The
    reported gains are 56.6% on LawBench, a 91.9% runtime reduction on GPU
    kernels, and 502% denoising improvement over the initial baseline.
  - Current evidence: LibreEvolve can mutate bounded candidate workspaces,
    record prompt/evaluator/failure artifacts, and export clipped
    ThetaEvolve-style GRPO training examples, but it has no SIA source row,
    no Feedback-Agent role that decides between harness and weight updates,
    no editable task-agent scaffold separate from evolved candidate code, no
    online RL/fine-tuning loop, no adapter or checkpoint lifecycle, no
    trajectory-to-training-data promotion policy, no harness-only versus
    harness-plus-weight ablation report, and no benchmark coverage for the
    SIA legal, kernel, or denoising domains.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.27276`: arXiv id/version/date/PDF hash, authors, source
    license, linked implementation URL/status, relation to AlphaEvolve and
    LibreEvolve's fixed-backend evaluator loop, Meta-Agent/Target-Agent/
    Feedback-Agent role schemas, editable harness component inventory,
    harness patch provenance, model-weight update trigger records, training
    data lineage, RL/fine-tuning configuration, adapter/checkpoint artifacts,
    rollback/resume policy, reward/verifier sufficiency, harness-only and
    weight-only ablation identities, LawBench/kernel/scRNA benchmark taxonomy,
    compute and cost accounting, performance-delta records, and README/
    ROADMAP wording that keeps harness-plus-weight self-improvement as
    missing evidence until local implementation and reports exist.

- [ ] Add HarnessFix trace-grounded harness repair source boundary.
  - Spec evidence: arXiv `2606.06324`, `From Failed Trajectories to Reliable
    LLM Agents: Diagnosing and Repairing Harness Flaws`, was submitted June
    4, 2026. Its abstract says LLM agents rely on harnesses for execution
    environments, tool interfaces, context, lifecycle orchestration,
    observability, verification, and governance, while many self-improving
    systems modify prompts, workflows, or harnesses from final outcomes
    without locating responsible evidence in failed trajectories. HarnessFix
    compiles raw traces and harness code into a Harness-aware Trace
    Intermediate Representation (HTIR), attributes failures to trajectory
    steps and harness layers, consolidates recurring flaw records, maps them
    to scoped repair operators, and validates patches under flaw-specific
    repair specs to reduce target flaws without unacceptable regressions.
  - Current evidence: LibreEvolve logs evaluator failures, quarantine rows,
    prompt history, archive events, LLM calls, and run manifests, but it has
    no HarnessFix source row, no normalized trace IR that links model calls,
    tool calls, evaluator outcomes, and harness code, no harness-layer
    taxonomy for execution/tool/context/lifecycle/observability/verification/
    governance faults, no recurring flaw consolidation, no scoped repair
    operator schema, no flaw-specific regression bounds, and no harness patch
    validation loop distinct from candidate-program mutation.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2606.06324`: arXiv id/version/date/PDF hash, authors, source
    license, relation to AlphaEvolve and LibreEvolve failure artifacts, HTIR
    schema, raw-trace normalization records, harness-code linkage, step-level
    provenance, ETCLOVG-style harness-layer attribution, recurring flaw
    records, repair-operator taxonomy, generated harness patch artifacts,
    flaw-specific validation specs, regression-bound reports, held-out task
    evaluation, benchmark taxonomy for SWE-Bench Verified, Terminal-Bench 2.0
    Verified, GAIA, and AppWorld, baseline identities, and README/ROADMAP
    wording that keeps trace-grounded harness repair as missing evidence until
    local implementation and reports exist.

- [ ] Add RHO retrospective self-preference harness optimization boundary.
  - Spec evidence: arXiv `2606.05922`, `Retrospective Harness Optimization:
    Improving LLM Agents via Self-Preference over Trajectory Rollouts`, was
    submitted June 4, 2026. Its abstract introduces Retrospective Harness
    Optimization (RHO), a self-supervised method that improves an agent
    harness using only past trajectories instead of ground-truth validation
    sets. RHO selects a diverse coreset of challenging tasks from past
    trajectories, re-solves them in parallel, analyzes the rollouts with
    self-validation and self-consistency, generates candidate harness updates,
    and selects the most effective update through pairwise self-preference.
    The abstract reports a single-round SWE-Bench Pro pass-rate improvement
    from 59% to 78% without external grading.
  - Current evidence: LibreEvolve records run history, prompt history,
    evaluator results, failures, quarantine streams, and best candidates, but
    it has no RHO source row, no unlabeled past-trajectory harness optimizer,
    no diverse hard-task coreset selection, no parallel retrospective
    re-rollout workflow, no self-validation/self-consistency analysis
    artifact, no pairwise self-preference harness ranking, no candidate
    harness proposal set, and no long-horizon behavior-pattern report showing
    sustained gains without external labels.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2606.05922`: arXiv id/version/date/PDF hash, authors, source
    license, relation to AlphaEvolve and LibreEvolve's evaluator-grounded
    search, past-trajectory corpus schema, challenging-task and diversity
    coreset criteria, retrospective rollout batch records, parallel re-solve
    provenance, self-validation and self-consistency artifacts, candidate
    harness-update provenance, pairwise self-preference ranking records,
    label-free selection policy, deployment/rollback policy, behavior-pattern
    shift metrics, long-horizon session reports, SWE-Bench Pro benchmark
    metadata, baseline identities, and README/ROADMAP wording that keeps
    retrospective self-preference harness optimization as missing evidence
    until local implementation and reports exist.

- [ ] Add harness-updating versus harness-benefit capability boundary.
  - Spec evidence: arXiv `2605.30621`, `Harness Updating Is Not Harness
    Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM
    Agents`, was submitted May 28, 2026. Its abstract distinguishes
    harness-updating, the capability to produce useful persistent harness
    updates from execution evidence, from harness-benefit, the capability of
    a task-solving agent to benefit from updated harnesses during task
    execution. It reports that harness-updating is relatively flat across
    base model capability, while harness-benefit is non-monotonic: weak-tier
    models benefit little, mid-tier models benefit most, and strong-tier
    models benefit less than mid-tier. It traces weak-tier failure to missing
    harness artifact activation or poor faithful following after activation.
  - Current evidence: LibreEvolve records candidate mutations, prompt
    context, backend selection, run artifacts, and failure histories, but it
    has no source row for `2605.30621`, no harness self-evolution benchmark,
    no metric separating update-generation quality from downstream
    task-agent benefit, no harness artifact activation telemetry, no
    long-horizon instruction-following/adherence metric, no model-tier
    comparison matrix, and no budget rule distinguishing capability spent on
    the evolver from capability spent on the task-solving agent.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.30621`: arXiv id/version/date/PDF hash, authors, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    harness assumptions, harness-updating metric definitions, harness-benefit
    metric definitions, evolver/task-agent pairing matrix, persistent harness
    update artifacts, activation/load-rate telemetry, adherence/following
    traces across long trajectories, model-tier taxonomy, weak/mid/strong
    baseline identities, capability-budget accounting, post-evolution
    performance deltas, SWE-Bench Verified/MCP-Atlas/SkillsBench benchmark
    metadata if reproduced, and README/ROADMAP wording that keeps harness
    self-evolution benefit claims separate from harness-update generation
    until local evidence proves both.

- [ ] Add AHE observability-driven harness evolution source boundary.
  - Spec evidence: arXiv `2604.25850`, `Agentic Harness Engineering:
    Observability-Driven Automatic Evolution of Coding-Agent Harnesses`, was
    submitted April 28, 2026. Its abstract says harness engineering remains
    manual because automating it faces a heterogeneous action space, massive
    trajectories that bury useful signals, and edits whose downstream effects
    are hard to attribute. It introduces Agentic Harness Engineering (AHE), a
    closed loop with three observability pillars: component observability,
    where every editable harness component has an explicit file-level
    representation; experience observability, where raw trajectory tokens are
    distilled into layered drill-down evidence; and decision observability,
    where each edit is paired with a self-declared prediction later verified
    against task-level outcomes. It reports ten AHE iterations improving
    Terminal-Bench 2 pass@1 from 69.7% to 77.0%, plus frozen-harness transfer
    to SWE-bench Verified and other model families.
  - Current evidence: LibreEvolve records prompts, candidate diffs, evaluator
    outputs, failures, archives, and manifests, but it has no AHE source row,
    no file-level editable harness component inventory for prompts/tools/
    middleware/skills/sub-agents/memory, no revertible harness edit action
    space, no layered trajectory-evidence corpus distilled from long runs, no
    decision-observability record that pairs each edit with an expected
    outcome, no falsifiable edit contract, no cross-iteration harness
    evolution report, and no frozen-harness transfer benchmark.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2604.25850`: arXiv id/version/date/PDF hash, authors, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    harness artifacts, editable component taxonomy, file-level component
    manifests, revertible patch records, trajectory-evidence distillation
    schema, drill-down evidence corpus links, edit-prediction records,
    outcome verification records, falsifiable contract status, iteration
    traces, tool/middleware/memory attribution, frozen-harness transfer
    reports, Terminal-Bench 2 and SWE-bench Verified benchmark metadata,
    baseline identities, token/cost accounting, and README/ROADMAP wording
    that keeps observability-driven harness evolution as missing evidence
    until local implementation and reports exist.

- [ ] Add AI Harness Engineering runtime-substrate source boundary.
  - Spec evidence: arXiv `2605.13357`, `AI Harness Engineering: A Runtime
    Substrate for Foundation-Model Software Agents`, was submitted May 13,
    2026. Its abstract argues that autonomous software-engineering capability
    emerges from a model-harness-environment system, not from the foundation
    model alone. It identifies eleven harness responsibilities: task
    specification, context selection, tool access, project memory, task
    state, observability, failure attribution, verification, permissions,
    entropy auditing, and intervention recording. It also defines a four-level
    H0-H3 ladder that progressively exposes runtime support and a trace-based
    evaluation protocol that converts each run into an auditable episode
    package with richer evidence at higher harness levels.
  - Current evidence: LibreEvolve records manifests, prompt history, LLM calls,
    evaluator outputs, failure streams, and archive events, but it has no
    `2605.13357` source row, no first-class model-harness-environment
    capability contract, no complete eleven-responsibility harness inventory,
    no H0-H3 runtime-support ladder, no episode package schema tying task,
    repository, harness config, tools, verification rules, traces, and final
    outcome together, no entropy audit, and no intervention log that records
    human assistance and its avoidability.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.13357`: arXiv id/version/date/PDF hash, authors, source
    license, relation to AlphaEvolve and LibreEvolve runtime artifacts,
    model-harness-environment capability schema, eleven harness responsibility
    records, H0-H3 harness-level taxonomy, exposed runtime-resource matrix,
    task/spec/context/tool/memory/state records, observability and failure-
    attribution traces, verification protocol records, permission-boundary
    events, entropy-audit artifacts, intervention logs, episode package
    schema, requirement-level evidence checks, controlled validation task
    metadata, maintenance-burden reports, and README/ROADMAP wording that
    keeps AI-harness runtime-substrate claims as missing evidence until local
    implementation and reports exist.

- [ ] Add inference-time trajectory-alignment harness design boundary.
  - Spec evidence: arXiv `2605.21516`, `Harnesses for Inference-Time
    Alignment over Execution Trajectories`, was submitted May 15, 2026. Its
    abstract says harness engineering aims to improve long-term performance
    through task decomposition and guided execution, but more elaborate
    harnesses are not uniformly better. It separates harness effects into task
    decomposition, which structures sub-goals, and guided execution, which
    reshapes local action distributions. It then analyzes workflow
    granularity, retry budgets, and guidance-induced action reweighting,
    identifying failure modes such as over-decomposition, over-pruning, and
    hallucinated execution. It also reports that partial harnesses, which
    specify only initial steps and leave the remainder to the agent, can
    outperform fully structured workflows.
  - Current evidence: LibreEvolve records prompt variants, parent selection,
    evaluator results, retry-like evaluator behavior, and run artifacts, but
    it has no `2605.21516` source row, no harness parameterization for
    decomposition granularity, guidance strength, or local guidance rules, no
    pass-rate/final-bias tradeoff report, no retry-budget sensitivity study,
    no over-decomposition or over-pruning diagnostics, no hallucinated
    execution metric, no partial-harness benchmark, and no alignment evidence
    separating helpful structure from over-constraining execution.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2605.21516`: arXiv id/version/date/PDF hash, authors, source
    license, relation to AlphaEvolve and LibreEvolve prompt/evaluator
    scaffolds, harness parameter schema for decomposition granularity,
    guidance strength, and guidance rule, sub-goal sequence records,
    trajectory/action-distribution records, retry-budget records, pass-rate
    and final-bias metrics, granularity-capability alignment reports,
    guidance-evidence alignment reports, over-decomposition/over-pruning/
    hallucinated-execution diagnostics, partial-harness prefix experiments,
    Terminal-Bench-2 and controlled synthetic benchmark metadata, baseline
    identities, and README/ROADMAP wording that keeps inference-time harness
    alignment claims as missing evidence until local implementation and
    reports exist.

- [ ] Add Adaptive Auto-Harness open-ended task-stream boundary.
  - Spec evidence: arXiv `2606.01770`, `Adaptive Auto-Harness: Sustained
    Self-Improvement for Agentic System Deployment on Open-Ended Task
    Streams`, was submitted June 1, 2026. Its abstract says existing
    auto-harness systems optimize prompts, skills, tools, memories, and
    supporting infrastructure from execution feedback, but are typically
    evaluated on fixed offline benchmarks. Real deployments instead have
    open-ended task streams with unbounded histories, heterogeneous tasks, and
    shifting distributions; a single repeatedly and densely updated harness
    can become brittle as accuracy peaks and then declines. Adaptive
    Auto-Harness decomposes the oracle-harness gap into evolution loss and
    adaptation loss, then addresses them with a stateful multi-agent evolver,
    a harness tree with solve-time routing, and human-steering hooks when
    history lacks the needed signal.
  - Current evidence: LibreEvolve supports per-run artifacts, fixed problem
    directories, MAP-Elites archives, islands, prompt history, and evaluator
    feedback, but it has no `2606.01770` source row, no open-ended task-stream
    abstraction, no unbounded history management across heterogeneous task
    distributions, no evolution-loss/adaptation-loss accounting, no stateful
    multi-agent evolver roles, no harness tree, no solve-time routing policy,
    no human-steering hook record, and no sustained-performance report that
    detects early peak followed by degradation.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2606.01770`: arXiv id/version/date/PDF hash, authors, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    run/problem boundaries, open-ended task-stream schema, history-growth
    records, task heterogeneity and distribution-shift metrics, oracle-harness
    definition, evolution-loss and adaptation-loss records, stateful multi-
    agent evolver role schemas, cross-cycle memory records, harness tree
    artifacts, solve-time routing traces, human-steering hook provenance,
    targeted-steering outcomes, sustained-performance curves, degradation/
    brittleness diagnostics, prediction-market/security-competition/event-
    forecasting benchmark metadata, baseline identities, ablation records, and
    README/ROADMAP wording that keeps adaptive open-ended harness deployment
    claims as missing evidence until local implementation and reports exist.

- [ ] Add Meta-Harness outer-loop harness-code search boundary.
  - Spec evidence: arXiv `2603.28052`, `Meta-Harness: End-to-End
    Optimization of Model Harnesses`, was submitted March 30, 2026. Its
    abstract says LLM-system performance depends not only on model weights but
    also on the harness code that determines what information to store,
    retrieve, and present to the model. Meta-Harness is an outer-loop system
    that searches over harness code for LLM applications, using an agentic
    proposer with filesystem access to source code, scores, and execution
    traces of prior candidates. It reports gains on online text
    classification, retrieval-augmented IMO-level math reasoning across held-
    out models, and agentic coding on TerminalBench-2.
  - Current evidence: LibreEvolve searches over candidate program workspaces
    and records prompt/evaluator/history artifacts, but it has no
    `2603.28052` source row, no first-class harness-code search target, no
    agentic proposer role with filesystem access to prior harness candidates,
    no source/score/trace corpus for harness variants, no harness-level
    mutation and evaluation loop distinct from candidate-program evolution,
    no context-token efficiency report, no held-out model transfer evaluation,
    and no TerminalBench-2 agentic-coding harness benchmark.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2603.28052`: arXiv id/version/date/PDF hash, authors, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    candidate search, harness-code candidate schema, agentic proposer role
    schema, filesystem-visible source/score/trace corpus records, prior-
    candidate retrieval policy, harness mutation and evaluation records,
    context storage/retrieval/presentation artifacts, context-token budget and
    efficiency metrics, held-out model transfer reports, online text-
    classification/RAG-math/TerminalBench-2 benchmark metadata, hand-
    engineered baseline identities, and README/ROADMAP wording that keeps
    end-to-end harness-code optimization as missing evidence until local
    implementation and reports exist.

- [ ] Add AlphaEvolve MARL algorithm-discovery boundary for CFR and PSRO.
  - Spec evidence: arXiv `2602.16928`, `Discovering Multiagent Learning
    Algorithms with Large Language Models`, was submitted February 18, 2026
    and last revised May 7, 2026. Its abstract says the authors deploy
    AlphaEvolve to navigate two game-theoretic design spaces: counterfactual
    regret minimization (CFR) and policy-space response oracles (PSRO). The
    search yields VAD-CFR and SHOR-PSRO, evaluates them across an 18-game
    suite covering Poker, Goofspiel, Liar's Dice, Blotto, and Battleship
    variants, then ablates and distills the LLM-discovered mechanisms into
    WOP-CFR and PM-PSRO minimal solvers for better generalization with lower
    complexity. The paper exposes three CFR classes
    (`RegretAccumulator`, `PolicyFromRegretAccumulator`, `PolicyAccumulator`)
    and two PSRO meta-strategy solver classes (`TrainMetaStrategySolver`,
    `EvalMetaStrategySolver`) as Python search spaces, uses OpenSpiel, exact
    game-tree exploitability, four training games plus fourteen test games,
    and deterministic metrics.
  - Current evidence: `papers/README.md` has a background-only row for
    `2602.16928`, but LibreEvolve has no first-class code TODO for this
    source, no CFR or PSRO candidate interface, no imperfect-information game
    evaluator, no OpenSpiel-style game-suite fixture, no train/generalization
    split metadata for game-theoretic algorithms, no mechanism-coupling or
    structural-complexity report, no ablation/distillation workflow that
    reduces discovered solvers to a minimal algorithmic core, no exact
    exploitability traversal boundary, no IQM log-improvement audit, no
    constant-sum normal-form random-game validation, and no VAD-CFR,
    SHOR-PSRO, WOP-CFR, or PM-PSRO benchmark records.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2602.16928`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve and
    LibreEvolve evaluator APIs, CFR and PSRO candidate schemas, game-suite
    metadata for the 18 OpenSpiel instances including information-state counts
    and action ranges, train/evaluation game split hashes, baseline solver
    identities for CFR/CFR+/LCFR/DCFR/PCFR+/DPCFR+/HS-PCFR+, Uniform/Nash/
    AlphaRank/PRD/RM, exact-oracle PSRO records, regret/exploitability and
    IQM log-improvement metric definitions, evaluator budget and random-seed
    records, evolved-mechanism provenance for VAD-CFR and SHOR-PSRO,
    mechanism-coupling ablation records, WOP-CFR warm-start/asymmetric-
    discount/optimistic-prediction records, PM-PSRO tangent-projection and
    dynamic-budget records, structural-complexity metrics, distilled-solver
    handoff records, random constant-sum normal-form validation, exact-
    exploitability scale limits, single-trajectory/LLM-backbone/baseline-scope
    caveats, generalization reports for VAD-CFR, SHOR-PSRO, WOP-CFR, and
    PM-PSRO, and README/ROADMAP wording that keeps MARL/game-theoretic
    algorithm discovery as missing evidence until local implementation and
    reports exist.

- [ ] Add AlphaEvolve Ramsey-number combinatorial-structure boundary.
  - Spec evidence: arXiv `2603.09172`, `Reinforced Generation of
    Combinatorial Structures: Ramsey Numbers`, was submitted March 10, 2026
    and last revised April 21, 2026. Its abstract says AlphaEvolve improved
    lower bounds for nine classical Ramsey numbers: `R(3,13)` from 60 to 61,
    `R(3,18)` from 99 to 100, `R(4,13)` from 138 to 139, `R(4,14)` from 147
    to 148, `R(4,15)` from 158 to 159, `R(4,16)` from 170 to 174,
    `R(4,18)` from 205 to 209, `R(4,19)` from 213 to 219, and `R(4,20)`
    from 234 to 237. The abstract also says AlphaEvolve recovered all exact
    known Ramsey lower bounds, matched many other best-known lower bounds,
    and acted as a single meta-algorithm yielding search algorithms across
    those results. The paper body defines the lower-bound certificate as a
    graph on `n` vertices with no clique of size `r` and no independent set of
    size `s`, establishing `R(r,s) >= n+1`; Algorithm 1 evolves programs that
    return `(G1,G2)`, scores valid `G1` by graph size with boosts relative to
    `n_SoTA`, and gives `G2` a prospect bonus from the ratio of observed
    `r`-clique plus `s`-independent-set violations to the random-graph
    expectation. The appendix gives Algorithms 2-10 for the nine improved
    cells and Algorithms 11-34 for the other colored Table 1 cells, while the
    PDF links public Google Research locations for improved-bound
    constructions and AI-discovered search code.
  - Current evidence: `papers/README.md` lists `2603.09172` only as a
    constructive math benchmark candidate with `Not implemented; potential
    future benchmark`. LibreEvolve has no first-class code TODO for this
    source, no Ramsey graph-construction candidate schema, no graph verifier
    for `R(s,t)` lower-bound certificates, no exact-bound recovery suite, no
    matched-best-known benchmark ledger, no per-Ramsey-number result table,
    no artifact policy for witness graphs or search algorithms, and no
    single-meta-algorithm report showing one evolved search procedure family
    covering the new, recovered, and matched bounds. It also lacks a
    `run()`-return contract for primary/prospect Ramsey graphs, expected
    violation baseline scoring, off-by-one lower-bound normalization
    (`n`-vertex witness versus `R(r,s) >= n+1`), artifact ingestion for the
    linked Google Research improved-bound graphs and code, or implementation
    hooks for the paper's initialization families: random/stochastic,
    Paley/cubic/quadratic-residue algebraic seeding, circulant/cyclic/sum-free
    bootstrap, and hybrid/fractal/spectral seeding.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2603.09172`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve and
    LibreEvolve constructive-math fixtures, Ramsey candidate representation,
    graph/witness artifact schema, verifier/certifier entrypoints for
    `R(s,t)` lower-bound claims, exact-bound recovery suite, best-known-bound
    comparison table, per-result prior/current values and sources, search
    algorithm provenance, seed/budget records, witness graph hashes, failed
    construction records, independent checker outputs, and README/ROADMAP
    wording that keeps Ramsey-number discovery as missing evidence until
    local implementation and reports exist. The implementation boundary should
    include an exact clique/independent-set certifier, normalized result rows
    that record both witness vertex count and implied Ramsey lower bound,
    Algorithm 1-compatible primary/prospect scoring fields, imported or
    reproducibly regenerated public construction artifacts, per-algorithm
    appendix classifications for all 28 colored Table 1 cells, baseline
    comparison metadata for Radziszowski 2024, Exoo/Tatarevic 2015, Exoo 2006,
    Tatarevic 2020, Harborth/Krause 2003, and explicit caveats where prior
    work is only a graph or personal communication rather than a published
    search algorithm.

- [ ] Add AlphaEvolve local-correction combinatorics boundary.
  - Spec evidence: arXiv `2603.06692`, `Evolving Local Corrections for Global
    Constructions in Combinatorics`, was submitted March 4, 2026. Its
    abstract says many combinatorics problems can be reformulated as global
    constructions reached by repeated small finite correcting steps, and uses
    AlphaEvolve as an experimental engine to propose and iteratively refine
    such certificates. The three case studies are reconstruction of bipartite
    and planar graphs from vertex-deleted subgraphs, the Alon-Tarsi parity
    problem for Latin squares via sign-reversing involutions from local
    trades, and Rota's Basis Conjecture via local exchange policies on
    collections of bases. The abstract frames the outputs as explicit
    algorithms and structural patterns that may support later traditional
    analysis, not as proofs. The paper body fixes the AlphaEvolve object as a
    short Python evolvable block evaluated by an immutable mathematical
    harness, with hard validity constraints, soft progress measures,
    worst-case or near-worst-case scoring over random symmetry scrambles, and
    hard-negative replay. It reports concrete graph-reconstruction harnesses
    for bipartite matrix decks and planar biconnected non-maximal graphs,
    Alon-Tarsi Latin-square involution harnesses over orders
    `8,10,12,14,26`, and Rota local-exchange policy harnesses over `F2` ranks
    `5`, `7`, and `{5,7,9,11,13}`.
  - Current evidence: `papers/README.md` lists `2603.06692` only as
    `Not implemented; potential future benchmark`. LibreEvolve has no
    first-class code TODO for this source, no local-correction certificate
    candidate schema, no graph-reconstruction evaluator, no Latin-square
    trade/involution verifier, no matroid/basis-exchange evaluator for Rota's
    Basis Conjecture, no scoring-protocol metadata for these case studies, no
    outcome/conjecture ledger that separates explicit algorithms from proofs,
    and no artifact policy for finite correcting-step traces. It also lacks
    deck-agreement scoring with exact isomorphism/canonical-label checks,
    bipartite row/column-deletion card schemas, neighbor-degree profile and
    two-deletion compatibility records, min-cost-flow reconstruction evidence,
    planar minimum-degree-neighborhood enumeration with exact deck equality,
    Latin-square sign/involution/locality/isotopy-stress metrics, Rota
    assignment-matrix move traces, circuit-oracle metadata, majority-rollout
    robustness, and preservation of the paper's Gemini-generated summary and
    AI-use caveats.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2603.06692`: arXiv id/version/date/PDF hash, author, source license,
    code/artifact availability, relation to AlphaEvolve and LibreEvolve
    constructive-math fixtures, local-correction candidate schemas,
    finite-step trace artifacts, graph reconstruction benchmark metadata,
    vertex-deleted subgraph input/output schemas, Latin-square local-trade and
    sign-reversing-involution records, Rota basis-family and local-exchange
    policy records, scoring-protocol definitions, search budget and seed
    records, explicit-algorithm outputs, structural-pattern summaries,
    conjecture/proof-status fields, independent checker hooks, and README/
    ROADMAP wording that keeps local-correction combinatorics as missing
    evidence and avoids treating AlphaEvolve-generated conjectures as proved
    results. The implementation boundary should additionally require
    source-specific result ledgers for `1420/1420` bipartite reconstruction
    and `896/896` planar reconstruction under worst-of-five scrambles,
    Conjectures 4 and 5 with their tested-regime caveats, Alon-Tarsi Tables
    1-3 with validity/involution/sign-flip/non-identity/residual-bias/locality
    metrics, Conjectures 6-8 for stable odd-cycle trades, Rota Tables 4-6 with
    rank, pool, step-limit, instance, rollout, weight, fitness, and success
    fields, Conjectures 9-11 for circuit-rich `F2` pools, appendix evolved-code
    artifact hashes, and explicit proof-boundary fields marking these as
    experimental algorithms and conjectures rather than verified theorems.

- [ ] Add AlphaEvolve bilateral-trade mechanism-design boundary.
  - Spec evidence: arXiv `2603.08679`, `A New Lower Bound for the Random
    Offerer Mechanism in Bilateral Trade using AI-Guided Evolutionary Search`,
    was submitted March 9, 2026. Its abstract frames bilateral trade under
    the Myerson-Satterthwaite theorem, asks how closely Bayesian incentive
    compatible (BIC) and budget-balanced (BB) mechanisms can approximate
    first-best gains from trade (GFT), and studies the Random-Offerer (RO)
    mechanism. It says AlphaEvolve searches the space of value distributions
    and finds a new worst-case instance with
    `GFT_FB / GFT_RO >= 2.0749`, improving the lower bound beyond prior
    counterexamples near `2.02`. The paper body fixes the model as one seller
    cost `s` and one buyer value `b`, independently drawn from known
    distributions, with first-best `E[(b-s)+]`. Random Offerer is the exact
    half-mixture of Seller-Offering and Buyer-Offering, where each side chooses
    an optimal take-it-or-leave-it price. The AlphaEvolve run fixes the buyer
    to the Discrete Equal Revenue survival function `Pr(b>=m)=1/m`, evolves
    only `get_seller_distributions()`, starts from a uniform seller CDF, uses
    `H=20000`, rounds PMF/CDF values to multiples of `1e-15`, and computes GFT
    components by integer arithmetic. The discovered seller CDF is a mixture
    of modulated power laws:
    `F_s(m)=0.20*z^(0.15+0.05*sin(2*pi*z))+0.80*z^4`, with
    `z=(m+1)/(H+1)`, yielding `GFT_FB ~= 1.2322`,
    `GFT_SO ~= 0.3312`, `GFT_BO ~= 0.8565`, `GFT_RO ~= 0.5939`, and
    ratio `2.0749`; the appendix includes evaluator code.
  - Current evidence: `papers/README.md` lists `2603.08679` only as
    background AlphaEvolve mechanism-design context with no bilateral-trade
    distribution benchmark. LibreEvolve has no first-class code TODO for this
    source, no buyer/seller value-distribution candidate schema, no
    Random-Offerer evaluator, no first-best GFT computation, no BIC/BB
    assumption record, no ratio-verification report, no prior-counterexample
    baseline comparison, and no economic-mechanism artifact policy for
    distribution witnesses. It also lacks the fixed-buyer/evolved-seller
    search boundary, discrete equal-revenue survival-function fixture, seller
    CDF monotonicity and support validation, rounded-integer probability
    pipeline, exact optimal-price loops for SO and BO, code-artifact capture
    for the evolved seller generator and appendix evaluator, and records for
    the paper's other attempts (fixing the seller and evolving the buyer
    reportedly reached `2.08` but was not detailed; co-evolving both sides
    found a lower bound below `2.07`).
  - Required result: add source-manifest and implementation-boundary metadata
    for `2603.08679`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve and
    LibreEvolve mechanism-design fixtures, value-distribution candidate
    schema, buyer/seller support and probability constraints, FB and RO GFT
    calculation records, BIC/BB assumption metadata, ratio objective
    definition, numerical precision/tolerance policy, witness distribution
    artifacts, prior lower-bound/counterexample baselines, seed/budget
    records, independent checker outputs, and README/ROADMAP wording that
    keeps bilateral-trade lower-bound discovery as missing evidence until
    local implementation and reports exist. The code boundary should
    additionally require a reproducible `H=20000` discrete-domain evaluator,
    Discrete Equal Revenue buyer fixture, evolved seller CDF generator with
    mixture/modulation parameters, CDF/SF-to-PMF conversion, monotonicity and
    support checks, `1e-15` rounding-to-integer policy, exact FB/SO/BO/RO
    component ledgers, optimal reserve-price witnesses per side, ratio
    recomputation with uncertainty/tolerance notes, appendix evaluator hash,
    and caveats that the paper's rounded distribution is verified while the
    exact unrounded modulated-power-law ratio remains open.

- [ ] Add AlphaEvolve Magellan compiler-optimization boundary.
  - Spec evidence: arXiv `2601.21096`, `Magellan: Autonomous Discovery of
    Novel Compiler Optimization Heuristics with AlphaEvolve`, was submitted
    January 28, 2026 and accepted to `C4ML@CGO'26`. Its abstract says modern
    compilers rely on hand-crafted heuristics, and Magellan evolves compiler
    passes by synthesizing executable C++ decision logic. It couples an LLM
    coding agent with evolutionary search and autotuning in a closed loop of
    generation, evaluation on user-provided macro-benchmarks, and refinement.
    The reported tasks include LLVM function inlining for binary-size and
    end-to-end performance, register-allocation live-range priority rules,
    and preliminary XLA portability results. Section 2 splits the loop into
    policy proposal, local evaluation, hyperparameter tuning, and feedback:
    AlphaEvolve edits EVOLVE-BLOCK-delimited compiler source, emits C++
    heuristic templates with compiler-flag hyperparameters, rebuilds the
    compiler, evaluates macro-benchmarks with signals such as `llvm-size` or
    `perf stat`, and can hand exposed parameters to Vizier.
  - Current evidence: `papers/README.md` lists `2601.21096` only as
    background AlphaEvolve compiler-optimization context with no
    compiler-heuristic benchmark or compiler pass runner. LibreEvolve has no
    first-class code TODO for this source, no executable C++ decision-logic
    candidate schema, no LLVM function-inlining benchmark, no register-
    allocation workload fixture, no XLA portability fixture, no macro-
    benchmark harness, no compiler integration/artifact policy, no expert-
    baseline comparison table, no feature-based versus full-heuristic
    inlining mode distinction, no autotuner batch/round telemetry, no
    temporal/domain generalization report, no generated-policy maintainability
    report, and no production-style binary-size, end-to-end-performance, or
    large-workload validation reports.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2601.21096`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve and
    LibreEvolve compiler fixtures, C++ decision-logic candidate schemas,
    compiler-pass integration points, EVOLVE-BLOCK source-span and insertion
    records, compiler-flag hyperparameter schemas, LLVM inlining task records
    for partial-feature and full-API heuristics, register-allocation
    priority-rule records for `RegAllocGreedy`, XLA graph-extraction and
    auto-sharding task records, macro-benchmark dataset provenance,
    binary-size and performance metric definitions, autotuning loop metadata
    including batch size/rounds and invalid-sample rate, expert and neural
    baseline identities, temporal and domain generalization rows,
    generated-code maintainability rows, seed/budget records, compiler
    build/runtime environment hashes, independent checker outputs, and
    README/ROADMAP wording that keeps Magellan-style compiler optimization as
    missing evidence until local implementation and benchmark reports exist.

- [ ] Add AlphaEvolve ArchAgent computer-architecture boundary.
  - Spec evidence: arXiv `2602.22425`, `ArchAgent: Agentic AI-driven Computer
    Architecture Discovery`, was submitted February 25, 2026. Its abstract
    presents ArchAgent as an automated computer-architecture discovery system
    built on AlphaEvolve, focused on designing and implementing state-of-the-
    art cache replacement policies rather than only tuning parameters. It
    reports a `5.3%` IPC speedup over prior SoTA on public multi-core Google
    Workload Traces, a `0.9%` IPC speedup on heavily explored single-core
    SPEC06 workloads, `3-5x` faster development than prior human-developed
    policies, `2.4%` post-silicon hyperspecialization gains on SPEC06, and
    simulator-escape behavior in a microarchitectural simulator. The system
    implements candidate policies as C++ in ChampSim `policy.h`, compiles and
    runs ChampSim on workload suites, uses IPC normalized to LRU, constrains
    policies to hardware-realizable designs with a `48 KB` replacement-policy
    state budget, and uses short simulation runs for evolution before longer
    validation runs.
  - Current evidence: `papers/README.md` lists `2602.22425` only as
    background AlphaEvolve computer-architecture context with no architecture-
    design simulator or cache-policy benchmark. LibreEvolve has no first-
    class code TODO for this source, no cache replacement policy candidate
    schema, no ChampSim/microarchitecture simulator integration, no Google
    Workload Trace or SPEC06 workload fixture, no IPC speedup metric contract,
    no SoTA cache-policy baseline ledger, no post-silicon specialization
    parameter records, no short-run versus long-run validation split, no
    policy-mechanism ablation report, no hardware-realizability/state-budget
    verifier, no distributed-simulation failure/retry policy, and no
    simulator-escape detection or containment report.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2602.22425`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve and
    LibreEvolve architecture fixtures, cache-policy candidate schema,
    ChampSim `policy.h` integration points, CRC-style cache/core/prefetch/
    DRAM configuration records, workload trace provenance, single-core and
    multi-core benchmark splits, evolution-versus-validation instruction-count
    records, IPC speedup metric definitions, prior-SoTA baseline identities
    including LRU, SHiP, Hawkeye, and Mockingjay where applicable, generated
    policy implementation artifacts and mechanism labels for Policy31/61/62-
    style reports, hardware-realizability and state-budget checks, policy
    ablation reports, post-silicon parameter-specialization records,
    simulator-escape tests for optimized-away assertions and invalid
    write-bypass behavior, distributed-simulation failure/retry records,
    seed/budget records, independent checker outputs, and README/ROADMAP
    wording that keeps ArchAgent-style architecture discovery as missing
    evidence until local implementation and benchmark reports exist.

- [ ] Add AlphaEvolve Fault2Flow workflow-automation boundary.
  - Spec evidence: arXiv `2511.12916`, `Fault2Flow: An AlphaEvolve-Optimized
    Human-in-the-Loop Multi-Agent System for Fault-to-Workflow Automation`,
    was submitted November 17, 2025. Its abstract frames power-grid fault
    diagnosis as a manual, regulation-heavy workflow problem. Fault2Flow
    extracts and structures regulatory logic into PASTA-formatted fault trees,
    integrates expert knowledge through a human-in-the-loop verification
    interface, optimizes reasoning logic using an AlphaEvolve module, and
    synthesizes verified logic into n8n-executable workflows. The abstract
    reports transformer fault-diagnosis validation with `100%` topological
    consistency and high semantic fidelity. The paper body defines a concrete
    pipeline: regulatory PDFs are parsed into Markdown with MinerU, stored in
    MySQL with Milvus vector embeddings, converted by LLM agents into
    PlantUML mind maps and PASTA DSL fault trees, optimized with an
    AlphaEvolve/OpenEvolve-linked multi-island module, then traversed into n8n
    IF/ELSE workflow nodes and validated using synthesized test cases. The
    demonstration uses `DL/T 722-2014` transformer dissolved-gas-analysis
    three-ratio logic, Qwen3-Next-80B-A3B-Instruct at temperature `0.0`, and a
    16-case transformer dataset (9 three-ratio, 7 characteristic-gas cases).
    Table 1 reports Fault2Flow variants with TC `1.0`, E2ERC `1.0`, success
    `16/0`, and roughly `1800-1900` average tokens, while end-to-end baselines
    have TC below `0.94`, E2ERC below `0.72`, and higher token usage.
  - Current evidence: `papers/README.md` lists `2511.12916` only as
    background AlphaEvolve-optimized workflow application context with no
    fault-to-workflow or human-in-the-loop multi-agent benchmark. LibreEvolve
    has no first-class code TODO for this source, no regulatory-text to PASTA
    fault-tree candidate schema, no expert-verification workflow, no n8n
    workflow emitter, no transformer fault-diagnosis dataset fixture, no
    topological-consistency or semantic-fidelity metric contract, no
    AlphaEvolve reasoning-logic optimization boundary, and no artifact policy
    for verified operational workflows. It also lacks MinerU/PDF-to-Markdown
    provenance, PlantUML mind-map artifacts, PASTA self-check records,
    MySQL/Milvus storage/retrieval metadata, OpenEvolve/AlphaEvolve
    optimization trace fields, n8n API activation records, synthesized test
    case generation and failure-refinement logs, GPT-5-as-evaluator caveats
    for LRM/SF, edge-set TC and path-set E2ERC calculators, token-consumption
    ledgers, human-annotation/data-ethics records, and publication metadata
    caveats for the placeholder ACM venue/DOI text.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2511.12916`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve and
    LibreEvolve workflow/fault-diagnosis fixtures, regulatory-source
    provenance, PASTA fault-tree candidate schema, expert-review state
    records, reasoning-logic optimization candidate records, n8n workflow
    artifact schema, transformer fault-diagnosis dataset provenance,
    topological-consistency and semantic-fidelity metric definitions,
    human-in-the-loop audit logs, seed/budget records, independent checker
    outputs, and README/ROADMAP wording that keeps Fault2Flow-style
    fault-to-workflow automation as missing evidence until local
    implementation and benchmark reports exist. The implementation boundary
    should additionally require the three-stage document-understanding/
    knowledge-structuring/workflow-synthesis pipeline, Vue3/Element Plus/
    pdfjs/xlsx/ECharts frontend artifact expectations where relevant,
    MinerU/MySQL/Milvus backend provenance, PlantUML and PASTA intermediate
    hashes, AlphaEvolve multi-island optimization traces, n8n node/edge/
    workflow activation artifacts, synthesized test-case and failure-refinement
    logs, `DL/T 722-2014` dataset rows, Table 1 model-result rows for Qwen3
    and GPT-4.1 variants, LRM/SF/TC/E2ERC formulas, token averages,
    data-ethics/human-annotation records, and explicit caveats separating
    validated workflow artifacts from LLM-judged readability and
    semantic-fidelity scores.

- [ ] Add TTT-Discover test-time-training boundary against AlphaEvolve frozen
      search.
  - Spec evidence: arXiv `2601.16175`, `Learning to Discover at Test Time`,
    was submitted January 22, 2026 and last revised February 5, 2026. Its
    abstract contrasts prior test-time scaling such as AlphaEvolve, which
    searches by prompting a frozen LLM, with Test-Time Training to Discover
    (TTT-Discover), which performs reinforcement learning at test time so the
    LLM continues training on experience specific to one test problem. It
    targets continuous-reward discovery tasks and reports results across
    mathematics, GPU kernel engineering, algorithm design, and biology:
    Erdos minimum-overlap, an autocorrelation inequality, a GPUMode kernel
    competition with up to `2x` speedup, past AtCoder competitions, and
    single-cell denoising. The abstract says results use open model
    `OpenAI gpt-oss-120b`, public code, Tinker runs, expert or organizer
    review, and costs of a few hundred dollars per problem. The body defines
    Algorithm 1 over mutable weights `theta_i`, a buffer `H_i`, transition
    and reward functions induced by the problem, an adaptive entropic
    objective, and PUCT state reuse. Table 9 fixes `gpt-oss-120b`, high
    reasoning effort, Tinker context window `32768`, sampling temperature
    `1.0`, prompt-plus-thinking limit `26000`, `50` training steps, batch
    size `512` as `8` groups of `64`, Adam learning rate `4e-5`, LoRA rank
    `32`, KL coefficient `{0.01, 0.1}`, adaptive-beta KL constraint
    `gamma = ln(2)`, and PUCT exploration coefficient `1.0`.
  - Current evidence: `papers/README.md` lists `2601.16175` only as
    background test-time discovery context. LibreEvolve has no first-class
    code TODO for this source, no test-time RL training loop, no mutable model
    policy state, no Tinker/API training-run metadata, no open-model
    reproduction protocol for `gpt-oss-120b`, no continuous-reward
    cross-domain benchmark suite covering the cited math/kernel/algorithm/
    biology tasks, no expert/organizer review artifact policy, and no
    accounting boundary that separates frozen-LLM AlphaEvolve-style search
    from test-time model adaptation. It also lacks public artifact URL
    tracking for `https://github.com/test-time-training/discover`, the project
    page, result notebooks, GPUMode and AtCoder submissions, LoRA/checkpoint
    lineage, adaptive-beta and PUCT trace records, context-window truncation
    diagnostics for OpenEvolve baselines, per-domain verifier resource limits,
    Modal/GPUMode/AtCoder/OpenProblems harness provenance, and a checker for
    the paper's `Best-of-25600` versus Figure 4 `50 * 512 = 256000` sampling
    inconsistency.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2601.16175`: arXiv id/version/date/PDF hash, authors, source
    license, public code URL/status, relation to AlphaEvolve frozen-search
    assumptions and LibreEvolve's provider adapters, mutable policy/training
    state schema, RL objective and rollout-selection records, Tinker or
    equivalent training API metadata, open-model identity and checkpoint
    provenance, continuous-reward task definitions, Erdos/autocorrelation/
    GPUMode/AtCoder/single-cell benchmark records, prior-art and
    AlphaEvolve/OpenEvolve baseline identities, expert/organizer review
    artifacts, cost and budget accounting, seed/run records, independent
    checker outputs, and README/ROADMAP wording that keeps TTT-Discover-style
    test-time training as missing evidence until local implementation and
    benchmark reports exist. The implementation boundary should additionally
    require Algorithm 1 event logs, mutable-weight/checkpoint and LoRA records,
    per-step rollout batches, adaptive-beta KL solves, PUCT parent/reuse and
    top-1000 archive-retention traces, reward-validity zeroing, public code
    and result-link provenance, Table 2/3/4/5/6/7/8/9/10 result rows, expert
    review attestations, benchmark-specific resource limits, official
    submission IDs, and explicit documentation that LibreEvolve's current
    provider calls and feedback graders are not test-time model training.

- [ ] Add AlphaEvolve Bruhat-interval hypercube construction boundary.
  - Spec evidence: arXiv `2601.01235`, `Bruhat intervals that are large
    hypercubes`, was submitted January 3, 2026. Its abstract studies large
    Bruhat intervals that are poset hypercubes in the symmetric group `S_n`.
    It says permutations suggested by AlphaEvolve led to a pattern that
    performed well for tested `n` and was then proved to work for general
    `n`. For `n` a power of `2`, the paper exhibits a hypercube of dimension
    `O(n log n)`, matching the largest possible dimension up to a constant
    multiple, and characterizes vertices as dyadically well-distributed
    permutations. It also links maximal Bruhat-hypercube dimension to the
    second-highest-degree coefficient of Kazhdan-Lusztig `R`-polynomials and
    obtains `n log n` lower-bound consequences for frozen variables in open
    Richardson cluster algebras and embeddings of Bruhat graphs. The body
    defines dyadic basic intervals and `D_m`, bit-reversal affine endpoints
    `x_m` and `y_m`, Ehresmann matrices for Bruhat-order comparison,
    complementary blocks `C_m`, the map `phi: D_m -> S_2^{C_m}`, local flips
    that toggle one complementary block while changing length by `+/-1`, and
    proves `D_m = [x_m, y_m]` with hypercube rank `m * 2^(m-1)`.
  - Current evidence: `papers/README.md` lists `2601.01235` only as a
    constructive math benchmark candidate with `Not implemented; potential
    future benchmark`. LibreEvolve has no first-class code TODO for this
    source, no permutation-generator candidate schema, no Bruhat order or
    interval verifier, no poset-hypercube isomorphism checker, no dyadically
    well-distributed permutation checker, no `S_n` power-of-two benchmark
    rows, no Kazhdan-Lusztig `R`-polynomial coefficient metadata, no cluster-
    algebra/frozen-variable consequence ledger, and no artifact policy that
    separates AlphaEvolve-suggested finite patterns from human-proved general
    theorems. It also lacks the Section 4 experiment boundary: FunSearch
    adjacent-transposition program-output evaluators, deterministic/no-random
    prompt policy, Mistral `mistral-small-3.1-24b-instruct` run metadata,
    AlphaEvolve generalizer-mode scoring over `n = 10..50`, Gemini 2.5
    Flash/Pro call provenance, `3000-5000` evaluated-program counts, public
    artifact URL `https://github.com/JSEllenberg/Bruhat-hypercubes/tree/main`,
    `alpha(2n) = 2 alpha(n) + n` and `alpha(2^m) = m * 2^(m-1)` result checks,
    non-functional evolved-code caveats, and log/lineage evidence separating
    bit-reversal discovery from known low-discrepancy-sequence literature.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2601.01235`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve and
    LibreEvolve constructive-math fixtures, permutation candidate schema,
    Bruhat interval input/output records, power-of-two `S_n` benchmark rows,
    poset-hypercube verifier, dyadic well-distribution checker, dimension
    computation and asymptotic-bound records, Kazhdan-Lusztig `R`-polynomial
    coefficient linkage metadata, cluster-algebra and Bruhat-graph consequence
    fields, finite-test versus general-proof status, seed/budget records,
    independent checker outputs, and README/ROADMAP wording that keeps
    Bruhat-interval hypercube discovery as missing evidence until local
    implementation and reports exist. The implementation boundary should
    additionally require bit-string/basic-interval records, `x_m`/`y_m`
    generators, length and inversion-count checks, Ehresmann matrix
    inequalities, `D_m` exact-one fundamental-block checks, complementary-block
    `phi` and flip traces, `R_{x,y}(q) = (q - 1)^(ell(y)-ell(x))` and
    `d_{x_m,y_m}` records, `(0,m,2)`-net and optional `t`-adic generalization
    metadata, AlphaEvolve/FunSearch prompt/evaluator/run-cost artifacts,
    public repository hash/status, and a proof-status field distinguishing
    finite generated examples from theorem-backed constructions.

- [ ] Add global NLP solver comparator boundary for AlphaEvolve geometry
      benchmarks.
  - Spec evidence: arXiv `2601.05943`, `Global Optimization for
    Combinatorial Geometry Problems`, was submitted January 9, 2026. Its
    abstract says recent AlphaEvolve results raise the question of whether
    modern off-the-shelf global optimization solvers can match LLM-driven
    discoveries when the problems are directly formulated as nonlinear
    optimization problems (NLPs). It revisits a subset of the AlphaEvolve
    benchmark suite with straightforward NLP formulations and evaluates two
    state-of-the-art solvers: commercial FICO Xpress and open-source SCIP. It
    reports that, without solver modifications, both solvers reproduce and in
    several cases improve on best solutions from the literature, including
    recent LLM-driven discoveries. The body narrows the subset to three
    benchmark families: min-max distance ratio, circle packing in a square or
    perimeter-4 rectangle, and unit-hexagon packing in a regular hexagon. It
    specifies Mosel NLP/QCP formulations, squared-distance variables, circle
    center/radius/rectangle-width variables, hexagon rotation variables,
    half-space parameters, and Farkas multipliers for non-overlap.
  - Current evidence: `papers/README.md` lists `2601.05943` only as an
    optimization benchmark comparator with no nonlinear-programming solver
    comparison harness. LibreEvolve has no first-class code TODO for this
    source, no NLP formulation schema for AlphaEvolve geometry/combinatorial
    benchmarks, no FICO Xpress or SCIP runner abstraction, no solver-version
    or license/proprietary-availability records, no result comparison table
    against AlphaEvolve/literature values, no certificate/tolerance policy for
    solver outputs, and no report that distinguishes LLM-discovered algorithm
    search from direct mathematical-programming baselines. It also lacks
    Table 1-3 result-row schemas, Mosel model provenance, squared-distance
    ratio normalization choices (`t_min = 1` or `t_max = 1`), rectangle
    perimeter/width constraints, trigonometric and nonconvex-equality handling
    for hexagons, outer-approximation/Farkas-separation metadata, AlphaEvolve
    repository validation-code records, and caveats for the paper's choice not
    to attribute each solution to a specific solver or discuss dual-bound
    improvements in detail.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2601.05943`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve and
    LibreEvolve constructive-geometry fixtures, selected AlphaEvolve benchmark
    subset, NLP formulation records, variable/domain/constraint/objective
    schemas, FICO Xpress and SCIP solver identity/version/license records,
    solver parameter and time-limit metadata, incumbent/bound/certificate
    artifacts, numerical tolerance policy, prior-literature and AlphaEvolve
    baseline values, reproduced/improved/fell-behind outcome rows, seed/run
    records, independent checker outputs, and README/ROADMAP wording that
    keeps global-NLP solver comparison as missing evidence until local solver
    harnesses and benchmark reports exist. The implementation boundary should
    additionally require per-problem formulations for distance-ratio instances
    `(d,n)`, circle-packing `n` and variant rows, hexagon-packing `n` rows,
    Mosel/exported-model artifacts, solver availability and version checks
    including SCIP 10.0 and FICO Xpress Global where applicable, primal
    incumbent and optional dual-bound records, AlphaEvolve/literature baseline
    citations, Table 1-3 comparison rows, AlphaEvolve-repo validation outputs,
    rounding/flooring/ceiling policy, and an explicit note that this is a
    direct solver baseline, not an LLM evolutionary-search implementation.

- [ ] Add post-AlphaEvolve autoconvolution improvement boundary.
  - Spec evidence: arXiv `2506.16750`, `An improved example for an
    autoconvolution inequality`, was submitted June 20, 2025 and last revised
    August 10, 2025. Its abstract gives a nonnegative step function with
    `575` equally spaced intervals satisfying
    `||f * f||_L2^2 / (||f * f||_Linf ||f * f||_L1) >= 0.901564`. It says
    this improves on DeepMind's AlphaEvolve result, which used a nonnegative
    step function with `50` equally spaced intervals and value `>= 0.8962`,
    and that the new function was found using simulated annealing and
    gradient-based methods rather than large language models. The body states
    the exact rational certificate
    `96086089410408840289339769 / 106577013451431545242354944`, reduces the
    continuous problem to nonnegative coefficients `v_0..v_(N-1)` and
    convolution samples `L_j`, and gives formula `(3)` for recomputing the
    ratio from integer coefficient lists.
  - Current evidence: `papers/README.md` lists `2506.16750` only as a
    constructive math benchmark candidate with `Not implemented; potential
    future benchmark`. LibreEvolve has broad Appendix B autoconvolution TODOs,
    but no first-class code TODO for this source, no 575-interval witness
    schema, no objective recomputation report for the post-AlphaEvolve value,
    no side-by-side AlphaEvolve `50`-interval baseline row, no simulated-
    annealing/gradient-method provenance, no exact/rounded numerical tolerance
    policy for `0.901564`, and no artifact policy that distinguishes
    AlphaEvolve LLM-generated witnesses from later non-LLM improvements. It
    also lacks public artifact tracking for
    `https://github.com/zkli-math/autoconvolutionHolder`, `Inital HPC
    code.py`, `Refine HPC code.py`, `f95.py`, `coeffBL.txt`, and `Verify.nb`,
    plus the paper's integer-arithmetic conversion by multiplying by `2^24`
    and rounding, Matolcsi-Vinuesa `20`-step comparison value `0.889226`,
    AlphaEvolve coefficient-source reversal from DeepMind's notebook, and
    normalized-autoconvolution correlation comparisons `0.996342` and
    `0.848466`.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2506.16750`: arXiv id/version/date/PDF hash, authors, source
    license, code/artifact availability, relation to AlphaEvolve Appendix B
    autoconvolution fixtures, step-function witness schema, interval count and
    grid spacing, coefficient/value payload hashes, convolution/integral
    recomputation records, `L2`/`Linf`/`L1` norm definitions, objective and
    tolerance policy, AlphaEvolve `50`-interval `0.8962` baseline record,
    simulated-annealing and gradient-search provenance, prior/current result
    comparison rows, independent checker outputs, and README/ROADMAP wording
    that keeps the post-AlphaEvolve autoconvolution improvement as missing
    evidence until local witness artifacts and reports exist. The
    implementation boundary should additionally require translation/dilation
    invariance handling, support-normalization records for `[-1/4, 1/4]`,
    `L1` equivalence checks, exact-rational and decimal result rows, GitHub
    artifact hashes, Mathematica/Python checker parity, simulated-annealing
    parameters (`N=23`, perturbation scales, repeat counts), gradient-upscale
    stages `23 -> 115 -> 575`, NCSU HPC/resource provenance, and source-scoped
    documentation that the authors say the example was found in November 2024
    before they were aware of AlphaEvolve's result.

- [ ] Add post-AlphaEvolve sums-and-differences construction boundary.
  - Spec evidence: arXiv `2505.16105`, `Sums and differences of sets
    (improvement over AlphaEvolve)`, by Robert Gerbicz was submitted May 22,
    2025 as arXiv v1; the cached PDF hash is
    `90d63d13afd7b8e15ceac25a4cef3f6b1c974a12a7893e80bd18e3ef4e16e1e8`.
    Its abstract says AlphaEvolve used a set of `54265` integers to improve
    the lower bound in the sums-and-differences problem from
    `theta = 1.14465` to `theta = 1.1584`. It then gives an improved bound
    `theta = 1.173050` using an explicit construction of a `U` set containing
    more than `10^43546` elements, with GMP used for fast integer and
    floating-point arithmetic. The construction defines `W(m, L, B)`,
    encodes bounded-coordinate vectors in base `2B + 1`, derives formulas for
    `|U + U|`, `|U - U|`, and `2 max(U) + 1`, reports `theta = 1.162997` for
    `m = 80`, `L = 64`, `B = 5`, and confirms `theta = 1.173050` for
    `m = 81411`, `L = 65536`, `B = 5` using exact integer arithmetic in about
    15 hours. It reports approximate values `|U| = 6.314107319e43546`,
    `|U + U| = 3.208492702e61228`, `|U - U| = 6.587554451e75899`, and
    `2 max(U) + 1 = 6.605282799e84780`, with GMP code and exact computed
    values cited at `https://bit.ly/43mWCVC`.
  - Current evidence: `papers/README.md` lists `2505.16105` only as a
    constructive math benchmark candidate with `Not implemented; potential
    future benchmark`. LibreEvolve has broad Appendix B sums-and-differences
    TODOs, but no first-class code TODO for this source, no explicit large
    `U`-set construction schema, no `W(m, L, B)` parameter fixture, no
    base-`2B + 1` integer-encoding checker, no compressed artifact format for
    a set with more than `10^43546` elements, no sumset/difference-set
    verifier, no max-element/q-value verifier, no `theta` recomputation
    report for `1.173050`, no `(80, 64, 5)` small-search regression case, no
    exact-value artifact retrieval from the cited code URL, no AlphaEvolve
    `54265`-integer `1.1584` baseline row, no GMP dependency/provenance
    record, and no artifact policy that separates AlphaEvolve LLM-generated
    constructions from later explicit non-LLM improvements.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2505.16105`: arXiv id/version/date/PDF hash, author, source license,
    code/artifact availability, relation to AlphaEvolve Appendix B
    sums-and-differences fixtures, explicit `U(m, L, B)` construction schema,
    `W(m, L, B)` inclusion-exclusion formula records, base-`2B + 1` injective
    encoding checks for `W + W` and `W - W`, compressed/parametric artifact
    representation for huge finite sets, parameter records for `(80, 64, 5)`
    and `(81411, 65536, 5)`, sumset and difference-set cardinality records,
    max-element/q-value and set-size metadata, `theta` formula and tolerance
    policy, exact computed-value payload hashes, AlphaEvolve `54265`-integer
    `1.1584` baseline, previous `1.14465` lower-bound source,
    GMP/version/arithmetic provenance, prior/current comparison rows,
    independent checker outputs, and README/ROADMAP wording that keeps this
    post-AlphaEvolve sums-and-differences improvement as missing evidence
    until local construction artifacts and reports exist.

- [ ] Add further post-AlphaEvolve sums-and-differences sequence boundary.
  - Spec evidence: arXiv `2506.01896`, `Sums and differences of sets: a
    further improvement over AlphaEvolve`, by Fan Zheng was submitted
    June 2, 2025 as arXiv v1; the cached PDF hash is
    `3f04c75ccd850eb6e5c785e543f98d12446e9891399cc5246acae9335b4494c2`.
    Its abstract says it improves on both DeepMind AlphaEvolve's
    `theta = 1.1584` result and the subsequent `2505.16105`
    explicit-construction result `theta = 1.173050`. It constructs a sequence
    of `U` sets whose limit establishes a new lower bound `theta = 1.173077`.
    The proof extends `W(m, L, B)` bounded-coordinate sets to the asymptotic
    regime `L = floor(rm)`, uses large-deviation estimates for
    `log |W(m, floor(rm), B)| / m`, bounds `q(U) <= (2B + 1)^m`, combines
    lower bounds on `d(U)` with upper bounds on `s(U)`, and maximizes an
    asymptotic expression over `B`, `r`, and `a`. The paper reports a
    restricted MATLAB 2024b computation over `B = 3..10`, `r in (0.5, 2)`,
    and `a in (0, min(1, 1/r))`; the winning row is `B = 5` with
    `theta - 1 = 0.173077279785136` at tolerances `1e-8` and `1e-10`. The
    embedded MATLAB code uses `fminbnd`, `fminunc`, `logW`, `logD`, and a
    Legendre-transform helper for `I(c, B)`.
  - Current evidence: `papers/README.md` lists `2506.01896` only as a
    constructive math benchmark candidate with `Not implemented; potential
    future benchmark`. LibreEvolve has broad Appendix B sums-and-differences
    TODOs and a source-specific TODO for `2505.16105`, but no first-class code
    TODO for this further source, no sequence-of-sets construction schema, no
    limiting argument artifact, no large-deviation lemma checker, no
    asymptotic `W(m, floor(rm), B)` counting metadata, no MATLAB-code
    extraction/reimplementation harness, no tolerance-sweep regression for
    `B = 3..10`, no convergence/tail-bound verifier, no
    `theta = 1.173077` recomputation report, no side-by-side lineage from
    AlphaEvolve `1.1584` through `2505.16105` `1.173050`, and no artifact
    policy that distinguishes finite explicit `U` witnesses from asymptotic
    sequence constructions.
  - Required result: add source-manifest and implementation-boundary metadata
    for `2506.01896`: arXiv id/version/date/PDF hash, author, source license,
    code/artifact availability, relation to AlphaEvolve Appendix B and
    LibreEvolve sums-and-differences fixtures, sequence-of-`U` construction
    schema, per-sequence parameter records for `B`, `r`, `a`, and `m`,
    finite-prefix witness artifacts, limiting lower-bound derivation metadata,
    large-deviation `I(c, B)` implementation records, asymptotic
    `W(m, floor(rm), B)` checker outputs, `q/s/d` bound derivation records,
    MATLAB-code provenance plus an independent Python or exact-arithmetic
    reimplementation, tolerance-sweep rows for `B = 3..10` and
    `1e-4..1e-10`, convergence/tail-bound checks, sumset/difference-set
    cardinality records where finite prefixes are used, `theta` formula and
    tolerance policy, AlphaEvolve `1.1584` baseline, `2505.16105`
    `1.173050` baseline, prior/current comparison rows, independent checker
    outputs, and README/ROADMAP wording that keeps this further
    sums-and-differences improvement as missing evidence until local sequence
    artifacts and reports exist.

- [ ] Add UCB1 finite-time bandit source boundary before scheduler claims
      become regret claims.
  - Spec evidence: the local `auer-cesa-bianchi-fischer-2002` PDF,
    `Finite-time Analysis of the Multiarmed Bandit Problem`, by Peter Auer,
    Nicolo Cesa-Bianchi, and Paul Fischer appeared in `Machine Learning`
    `47`, pages `235-256`, in 2002; the cached PDF hash is
    `82c8a8192bdb425fbe7662c59ee85faf47f59901f1a4999a732d04db82702a5d`.
    It defines regret as the expected loss from not always playing the best
    machine and proves UCB1 finite-time logarithmic regret for `K > 1`
    machines with arbitrary reward distributions supported in `[0, 1]`.
    The UCB1 index is empirical mean plus a Chernoff-Hoeffding confidence
    term, and Theorem 1 bounds expected regret after any `n` plays by
    `8 * sum_i ln(n) / Delta_i` plus `(1 + pi^2 / 3) * sum_j Delta_j`.
    The proof bounds suboptimal pulls with
    `E[T_i(n)] <= 8 ln(n) / Delta_i^2 + 1 + pi^2 / 3`, initializes by trying
    each arm, uses play counts and empirical means, and relies on bounded
    rewards plus conditional-mean assumptions; the paper notes Theorems 1-3
    do not require rewards to be independent across machines and only need
    `E[X_i,t | X_i,1, ..., X_i,t-1] = mu_i`. It also presents UCB2,
    `epsilon_n`-GREEDY, UCB1-NORMAL, and UCB1-TUNED as separate variants,
    with UCB1-TUNED explicitly lacking a proven regret bound.
  - Current evidence: `papers/README.md` marks the UCB1 row as a foundational
    bandit-policy source, and LibreEvolve implements a heuristic UCB-style
    backend router over archive-admitted valid fitness-improvement rewards
    with call-id attribution. Existing roadmap/code caveats already say the
    current scheduler is not canonical regret-analyzed UCB1, but there is no
    source-specific code gate for the local UCB1 PDF id/hash, theorem-scope
    constants, bounded-support assumptions, conditional-mean/stationarity
    assumptions, regret definition, reward normalization policy, stable arm
    identity, initialization semantics, selected-index formula, exploration
    coefficient mapping, role-scoped/backend-metadata selection caveats,
    stationary-reward diagnostics, or proof/non-proof status in scheduler
    telemetry. Current code in `libreevolve/llm/ensemble.py` caps rewards at
    `MAX_REWARD = 1.0`, rejects negative rewards, records counts for
    reward-accounted calls, selects untried eligible backends first, and uses
    `(wins_i / counts_i) + c * sqrt(log(total) / counts_i)` with default
    `explore_coeff = 1.0`; the optional `throughput_depth` strategy adds
    normalized depth/cost/latency metadata, so it is further from canonical
    UCB1 than the base heuristic.
  - Required result: add source-boundary metadata and scheduler validation for
    `auer-cesa-bianchi-fischer-2002`: PDF hash/source status, paper-title and
    theorem-scope fields, arm/reward-support assumptions,
    conditional-mean/stationarity assumptions, reward-normalization evidence,
    stable backend-as-arm identity records, initialization policy, empirical-
    mean/confidence-radius calculation telemetry, coefficient mapping from
    canonical `sqrt(2 ln n / n_i)` to LibreEvolve's configurable
    `c * sqrt(log(total) / counts_i)`, selected-arm/index traces, regret-
    baseline fields when applicable, unsupported flags for UCB2,
    `epsilon_n`-GREEDY, UCB1-NORMAL, and UCB1-TUNED, proof-status metadata
    for metadata-aware `throughput_depth`, and docs checks that distinguish
    heuristic UCB-style backend routing from canonical UCB1 finite-time regret
    guarantees.

- [ ] Add GigaEvo framework source boundary before inspiration claims become
      reproduction claims.
  - Spec evidence: local arXiv `2511.17592`, `GigaEvo: An Open Source
    Optimization Framework Powered by LLMs and Evolution Algorithms`, by
    Valentin Khrulkov, Andrey V. Galichin, Denis Bashkirov, Dmitry Vinichenko,
    Oleg Travkin, Roman Alferov, Andrey Kuznetsov, and Ivan Oseledets was
    submitted November 17, 2025 as arXiv v1; the cached PDF hash is
    `9a14bf06a1323e63bf53234e79e44c41e1e78e0dc2f90578d74b928efd067113`.
    It presents an open-source AlphaEvolve-inspired framework with four core
    components: Redis program storage, an `asyncio` DAG execution engine,
    MAP-Elites evolution, and a LangGraph mutation operator. Its Redis
    `Program` records contain UUID, source code, lifecycle state such as
    `FRESH`, `RUNNING`, and `COMPLETE`, metrics, genealogical lineage, and DAG
    stage outputs, with optimistic concurrency control via atomic counters.
    The DAG supports execution, validation, complexity analysis, LLM
    inference, agentic pipelines, data-flow edges, execution-order
    dependencies, caching, and automatic stage skipping. It also describes
    Hydra configuration, directory problems with `task description.txt`,
    `metrics.yaml`, `validate.py`, and `initial programs/`, generated
    insights, bidirectional lineage stages, diff and rewrite mutation modes,
    and reproduction/generalization experiments. The paper links both
    `https://github.com/AIRI-Institute/gigaevo-core` and
    `https://github.com/FusionBrainLab/gigaevo-core`, so source URL status
    needs explicit disambiguation.
  - Current evidence: `papers/README.md` marks GigaEvo as framework
    inspiration and explicitly says LibreEvolve has no Redis lifecycle
    database, `asyncio` DAG engine, insight stage, or concurrent units. A broad
    built-in-plugin/inspiration TODO keeps GigaEvo grouped with CodeEvolve,
    ThetaEvolve, ImprovEvolve, MadEvolve, CausalEvolve, and DeepEvolve, but
    there is no source-specific code TODO for `2511.17592`, no local
    equivalent of Redis program lifecycle states, no DAG stage graph/caching
    schema, no optimistic-concurrency program archive, no Hydra-equivalent
    component composition, no GigaEvo problem-layout adapter, no LangGraph-
    style mutation operator, no bidirectional lineage analysis records, no
    GigaEvo benchmark reproduction report, and no validation that
    README/ROADMAP wording distinguishes framework inspiration from GigaEvo
    reproduction. Current `ProgramDatabase` explicitly says it is a small
    local log/archive facade, not a GigaEvo-style lifecycle database.
  - Required result: add source-boundary metadata and implementation gates for
    `2511.17592`: arXiv version/date/PDF hash, source/license and code-URL
    status, Redis-vs-local-storage applicability, program lifecycle state
    schema, DAG node/edge/stage-output records, concurrency/caching telemetry,
    optimistic-concurrency semantics, Hydra/component-composition mapping,
    problem-layout adapter records, insight and ancestor/descendant lineage-
    analysis artifacts, LangGraph or equivalent mutation-operator provenance,
    diff-vs-rewrite mutation-mode evidence, MAP-Elites/island compatibility
    reports, and benchmark reproduction records for Heilbronn `n = 11`
    (`0.0364` vs AlphaEvolve `0.0365`), circle packing `n = 26` and `n = 32`,
    kissing numbers, bin packing (`0.55%` Weibull excess bin usage vs
    FunSearch `0.68%`), and prompt/agent evolution on Jigsaw Agile Community
    Rules (`0.803` test AUC for the evolved agent). Keep docs wording labeled
    as inspiration-only until those artifacts exist.

- [ ] Add CodeEvolve source boundary before crossover/refinement claims.
  - Spec evidence: local arXiv `2510.14150`, `CODE EVOLVE: an open-source
    evolutionary framework for algorithmic discovery and optimization`, by
    Henrique Assumpcao, Diego Ferreira, Leandro Campos, and Fabricio Murai was
    submitted as arXiv v4 on March 12, 2026; the cached PDF hash is
    `8dc8c35d24e2f6bce81e9608609e10b4dac5dd7072d155d9cd5c575d47472405`.
    It describes an islands-based genetic algorithm with a weighted LLM
    ensemble, `SEARCH/REPLACE` edits, inspiration-based semantic crossover,
    meta-prompting exploration, depth-based targeted refinement,
    exploration-rate scheduling, sandboxed evaluation with runtime and memory
    limits, prompt/solution fitness, MAP-Elites/CVT-MAP-Elites archives, and
    AlphaEvolve/EoH benchmark plus quality-cost comparisons. The paper defines
    solution fitness `fsol` and prompt fitness `fprompt(P) = max fsol(S)` over
    prompt-generated solutions; Algorithm 1 samples exploitation vs
    exploration by `pexplr`, collects `k` nearest ancestors for depth
    exploitation, calls `MetaPromptingLLM` during exploration, and passes
    inspiration solutions to the `LLMEnsemble` as semantic crossover. It also
    reports a Plateau Scheduler, rank-based parent/inspiration selection,
    elitist migration, per-island MAP-Elites or CVT-MAP-Elites, AWS SageMaker
    sandbox runs, and linked code/experiment URLs at
    `https://github.com/inter-co/science-codeevolve` and
    `https://github.com/inter-co/science-codeevolve-experiments`.
  - Current evidence: `papers/README.md` marks CodeEvolve as agentic
    code-evolution inspiration and says LibreEvolve lacks CodeEvolve-style
    crossover, targeted refinement, modular orchestration, and context-aware
    recombination. Broad inspiration TODOs and AlphaEvolve mutation-operator
    TODOs mention CodeEvolve or crossover generally, but there is no
    source-specific code TODO for `2510.14150`, no prompt/solution dual fitness
    implementation boundary, no semantic inspiration-crossover operator, no
    meta-prompting exploration operator, no depth-refinement ancestor context
    records, no Plateau Scheduler/evolution-rate trace, no sandbox/runtime-
    memory parity report, no CVT-MAP-Elites parity evidence, and no benchmark/
    cost comparison artifact tied to the local CodeEvolve PDF. LibreEvolve has
    configurable inspiration sampling and optional prompt-program mutation, but
    those are not CodeEvolve's prompt-fitness population, semantic crossover,
    targeted-refinement, or component-ablation artifacts.
  - Required result: add source-boundary metadata and implementation gates for
    `2510.14150`: arXiv version/date/PDF hash, linked code/release status,
    source-license metadata, islands/population schema, prompt and solution
    fitness records, weighted ensemble config and model-cost telemetry,
    inspiration-crossover provenance, meta-prompting exploration artifacts,
    depth-refinement ancestor context records, exploration-scheduler traces,
    sandbox runtime/memory limit evidence, MAP-Elites/CVT descriptor/archive
    compatibility, AlphaEvolve benchmark rows for the 9 paper instances
    (`CirclePackingSquare`, `CirclePackingRect`, `HexagonPacking`,
    `MinimizeMaxMinDist`, and autocorrelation inequalities), EoH rows for bin
    packing, TSP, and flow-shop scheduling, component/depth/inspiration/
    MAP-Elites/topology ablation reports, Qwen3-Coder-30B vs GEMINI-2.5
    quality-cost rows including the `n = 26` circle-packing `$6` vs `$35`
    narrative and Table 2 cost/time values, hyperparameter rows (`5` or `10`
    islands, `200` or `250` epochs, `k = 3..5`, `2..3` inspirations,
    migration rate `0.1`, exploration `0.2..0.5`), and README/ROADMAP wording
    that keeps CodeEvolve behavior inspiration-only until local artifacts prove
    otherwise.

- [ ] Add ThetaEvolve test-time RL source boundary before training claims.
  - Spec evidence: local arXiv `2511.23473`, `ThetaEvolve: Test-time Learning
    on Open Problems`, by Yiping Wang et al. was submitted as arXiv v1 on
    November 28, 2025; the cached PDF hash is
    `8e74933b2a4dddbf80a063fb88438c95b62b982a5167bbb77213ce1e3839715d`
    and the PDF metadata declares a CC-BY 4.0 license. It describes an
    AlphaEvolve-inspired dynamic environment using a single LLM, a much larger
    program database, batch parent/response sampling, early checks, lazy
    penalties for unchanged or repeated programs, optional reward shaping,
    GRPO-based RL at test time, RL-trained checkpoints, and open-problem
    results on circle packing, autocorrelation inequalities, and Hadamard
    matrices. The paper's code URL is `https://github.com/ypwang61/ThetaEvolve`
    and the runtime stack cites OpenEvolve, `slime`, SGLang/vLLM-style batched
    inference, batch size `B = 32`, `n = 16` responses per prompt, response
    length `16384`, rollout temperature `1.0`, and up to `16` concurrent
    verifier programs.
  - Current evidence: `papers/README.md` marks ThetaEvolve as test-time
    training inspiration and says LibreEvolve only exports clipped-reward JSONL
    through `ttt_rl`; there is no online RL/GRPO loop, checkpoint management,
    resume semantics, or lazy-penalty dynamics. Existing grouped inspiration
    TODOs and `TTTRLPlugin` docs keep the export boundary honest, but there is
    no source-specific code TODO for `2511.23473`, no batch-sampled dynamic
    environment, no `70`/`1000`/`10000` population/archive/island scaling
    report, no lazy penalty against database-equivalent programs after comment
    removal, no early-check penalty schema (`-0.4`, `-0.3`, `-0.2`, `-0.1`),
    no reward-shaping records, no GRPO training run metadata, no asymmetric
    clipping/truncated-importance-sampling configuration, no model checkpoint
    provenance, no transfer/generalization report, no SGLang/vLLM throughput
    report, and no AlphaEvolve-vs-ThetaEvolve benchmark comparison artifact.
  - Required result: add source-boundary metadata and implementation gates for
    `2511.23473`: arXiv version/date/PDF hash, linked code URL/status,
    source-license metadata, single-LLM and database-size configuration,
    batch prompt/response sampling records, early-check and lazy-penalty
    schemas, reward-shaping parameters, GRPO/RL training-run telemetry,
    generated-program sample counts, model checkpoint and adapter lifecycle
    records, inference-with-trained-checkpoint reports, task/evaluator
    compatibility notes for tolerance or typo corrections, AlphaEvolve/
    ShinkaEvolve/OpenEvolve baseline comparisons, Table 1 CirclePacking/FACI
    rows (`2.63598308` and `1.503133` vs AlphaEvolve `2.63586276` and
    `1.503164`), Table 2/9 per-task `w/ RL` vs `w/o RL` rows for
    `CirclePacking-T`, `SecondAutoCorrIneq`, `ThirdAutoCorrIneq`, and
    `HadamardMatrix`, Table 5/6 OpenEvolve-vs-ThetaEvolve throughput rows
    (`307.2k` programs, `63.6h` vs `5.4h`), Table 7 reward-shaping rows, Table
    10 database-design ablation rows, checkpoint transfer reports, and
    README/ROADMAP wording that keeps LibreEvolve's current clipped-reward
    export separate from ThetaEvolve-style test-time learning.

- [ ] Add ImprovEvolve modular-operator source boundary before interface
      claims.
  - Spec evidence: local arXiv `2602.10233`, `ImprovEvolve: Ask AlphaEvolve
    to Improve the Input Solution and Then Improvise`, by Alexey Kravatskiy,
    Valentin Khrulkov, and Ivan Oseledets was submitted as arXiv v1 on
    February 10, 2026; the cached PDF hash is
    `8123f1b19d9ba6c891e642be28b1bd4395fff549131d2e45b619dfd28ddfe57a`.
    The PDF metadata declares CC-BY 4.0, while the paper front matter also
    carries KDD 2026/ACM publication-rights language. It reformulates
    AlphaEvolve-style search by evolving a class with `generate_config(seed)`,
    `improve(x)`, and `perturb(x, sigma)` methods. The paper validates
    programs through a two-stage basin-hopping loop with multi-seed
    initialization, scheduled perturbation intensity, monotonic acceptance,
    GigaEvo as the outer MAP-Elites backbone, and benchmark claims for hexagon
    packing and the second autocorrelation inequality, including human-edited
    `ImprovEvolve+E` variants. Algorithm 1 defaults to `10` initial seeds,
    `10` iterations per round, `sigma_max = 100`, `sigma_min = 0.001`, and a
    geometric perturbation schedule; the GigaEvo setup uses a single-island
    MAP-Elites archive with fitness as the single behavior descriptor
    discretized into `150` bins, `InsightsStage`, `LineageInsights`, and
    aggregate evolutionary statistics.
  - Current evidence: `papers/README.md` marks ImprovEvolve as modular search
    inspiration and says LibreEvolve only emits static modular prompt guidance
    with `operation_selected: static_modular_guidance` and false execution/
    enforcement flags. Existing grouped inspiration TODOs cover the general
    approximation boundary, but there is no source-specific code TODO for
    `2602.10233`, no enforced `generate_config`/`improve`/`perturb` interface,
    no basin-hopping validation runner, no inner-loop incumbent/improvement
    records, no perturbation-schedule telemetry, no GigaEvo-backed outer-loop
    compatibility report, no Gemini 3 Pro/Gemini 3 Flash Preview model-split
    provenance, no human-edit attribution boundary, and no hexagon/ACI2
    benchmark report tied to this source.
  - Required result: add source-boundary metadata and implementation gates for
    `2602.10233`: arXiv version/date/PDF hash, ACM/preprint rights metadata,
    linked code/status if available, class-interface schema and enforcement,
    Stage A/Stage B validation runner records, seed counts, basin-hopping
    rounds, perturbation schedules, monotonic acceptance proofs, incumbent and
    improvement-delta artifacts, GigaEvo/backbone compatibility metadata,
    model/provider and initial-program provenance, human-edited variant
    provenance, HEX and ACI2 benchmark/baseline rows, Table 1 result rows
    (`HEX 11` `3.9245` vs AlphaEvolve `3.9301`, `HEX 12` `3.9416` vs
    AlphaEvolve `3.9419`, `ACI2` ImprovEvolve+E `0.96258` vs AlphaEvolve
    `0.96102`), Table 2 hyperparameters (`5 min`/`20 min`, seeds `10`/`3`,
    rounds `15`/`5`, iterations `11`/`6`), Table 3 HEX `13..30`
    generalization rows, Table 4 Stage A/B and LLM-edit ablation rows,
    CPU/GPU and wall-clock budget records (`~10h` HEX, `~40h` ACI2), and
    README/ROADMAP wording that keeps current static modular prompting
    separate from ImprovEvolve execution semantics.

- [ ] Add MadEvolve parameter-optimization source boundary before domain-
      evolution claims.
  - Spec evidence: local arXiv `2602.15951`, `MadEvolve: Evolutionary
    Optimization of Cosmological Algorithms with Large Language Models`, by
    Tianyi Li, Shihui Zang, and Moritz Munchmeyer was submitted as arXiv v1 on
    February 17, 2026; the cached PDF hash is
    `ec47332c9b20ca391b8aedb6b8696c42aad20c976906d1e43f13490163daea19`
    and the PDF metadata uses the arXiv nonexclusive distribution license. It
    adapts AlphaEvolve-style code evolution to computational cosmology with a
    nested optimization architecture: LLMs mutate scientific algorithms while
    an inner loop detects free parameters, records their meanings, tunes them
    through greedy one-shot derivative-free search or autodiff/Adam over JAX
    or `vmad`-compatible programs, injects optimized values back into the
    source, and generates scientific reports explaining lineage, algorithmic
    innovations, free parameters, metrics, and physical rationale. The paper
    links `https://madevolve.org`, `https://github.com/tianyi-stack/MadEvolve`,
    `https://github.com/tianyi-stack/MadEvolve-Cosmo`, and report PDFs for
    BAO, iterative BAO, 21cm, and LDL/tSZ runs.
  - Current evidence: README and `papers/README.md` label MadEvolve as
    background/domain-evolution inspiration only, and code search shows no
    MadEvolve implementation. LibreEvolve has evaluator execution,
    metric/result reports, MAP-Elites/islands, and prompt-context tunable-field
    policy metadata, but no source-specific `2602.15951` code TODO, no
    parameter declaration schema, no child-vs-parent new-parameter detector, no
    budgeted inner optimizer, no JAX/vmad differentiability contract, no
    optimized-parameter source injection, no domain-task adapters for BAO,
    21cm, or tSZ, no generated innovation-report pipeline, and no MadEvolve run
    statistics or model-contribution artifacts. It also has no MadEvolve
    reward-hacking guardrails such as large-scale BAO penalties, no
    over-parameterization controls such as the paper's `<10` tunable-parameter
    prompt constraint, and no mode-collapse diagnostics for island populations.
  - Required result: add source-boundary metadata and implementation gates for
    `2602.15951`: arXiv version/date/PDF hash, madevolve.org and GitHub source
    status, framework/application split, parameter config schema, parameter
    count limits, one-shot/grid/Latin-hypercube/Bayesian-search records,
    autodiff/Adam optimizer records, differentiability and operator-compatibility
    validation, optimized-value source-injection provenance, parent/child
    parameter-set diffs, inner-vs-outer budget accounting, domain prompt and
    evaluator fixtures for BAO reconstruction, iterative BAO, 21cm tidal
    reconstruction, and tSZ/LDL, training/validation/test split provenance,
    compute environment records, success/improvement/model-contribution tables,
    report-generator lineage/comparative-analysis/synthesis artifacts,
    overfitting/reward-hacking diagnostics, Table 1 result rows (`0.752` to
    `0.924` BAO StdRec, `0.933` to `0.959` IterRec, `0.743` to `0.971` 21cm,
    `0.613` to `0.230` tSZ loss), Table 2 run statistics (`2,126` total
    generations across four runs; success rates `54.5%..85.7%`; improvement
    rates `13.4%..30.4%`), Table 3 per-model mutation statistics and UCB
    selection records, Quijote/LDL/vmad dataset provenance, generated-report
    URL/artifact checks, and README/ROADMAP wording that keeps MadEvolve as
    background until those mechanisms are locally executed.

- [ ] Add CausalEvolve causal-scratchpad source boundary before causal
      discovery claims.
  - Spec evidence: local arXiv `2603.14575v2`, `CausalEvolve: Towards
    Open-Ended Discovery with Causal Scratchpad`, by Yongqiang Chen, Chenxi
    Liu, Zhenhao Chen, Tongliang Liu, Bo Han, and Kun Zhang was submitted as
    arXiv v1 on March 15, 2026 and revised as v2 on March 29, 2026; the cached
    PDF hash is
    `b3190d25d802f5b9913e4e266b7dda1b76d2211d2d4cad68e1a5d0a3d03fc4d2`
    and the PDF metadata declares CC BY-NC-SA 4.0. It frames
    AlphaEvolve-like scientific discovery as a POMDP/SCM process and adds a
    causal scratchpad. The paper uses LLMs before evolution to define
    outcome-level factors and executable factor code, uses a CausalPlanner MAB
    over `(factor, direction)` interventions to select inspiration programs,
    identifies procedure-level factors from accumulated trials with COAT-style
    LLM analysis, estimates approximate treatment effects, detects surprise
    patterns such as sign inversions or quantity shifts, performs abductive
    reasoning to propose new hypotheses/factors, and reports four-task
    comparisons against ShinkaEvolve, CausalPlanner(Meta), and COAT. It fixes
    Grok-4.1-fast-reasoning for fair comparisons and evaluates 3 seeds over
    task-specific step schedules.
  - Current evidence: `libreevolve/plugins/causal.py` explicitly says the local
    plugin is not the CausalEvolve causal scratchpad. It uses a fixed regex
    factor list over diff/full mutation text, parent-aware score deltas,
    pull-once-then-UCB-like factor selection, bounded recent history, malformed
    evidence counters, and prompt-visible recent outcome summaries. There is
    no source-specific `2603.14575` code TODO, no POMDP/SCM belief record, no
    LLM-defined outcome-factor schema or executable factor-code validation, no
    `(factor, direction)` intervention action records, no top-factor inspiration
    sorting, no procedure-factor extractor, no treatment-effect estimates, no
    surprise-pattern detector, no abductive-reasoning scratchpad, no causal
    hypothesis lifecycle, and no Hadamard/autocorrelation/circle-packing/AIME
    comparison report tied to this source. The local heuristic also has no
    source/target environment-shift model, no theorem-backed sample-efficiency
    or non-identifiability boundary, and no executable Appendix D metric
    library for task outputs.
  - Required result: add source-boundary metadata and implementation gates for
    `2603.14575`: arXiv version/date/PDF hash, code/source status, causal
    scratchpad schema, POMDP/SCM task-world metadata, outcome-factor prompt and
    executable factor-code contracts, deterministic factor metric artifacts,
    CausalPlanner action/reward policy with tau/K parameters, inspiration
    selection records, procedure-factor extraction prompts and artifacts,
    approximate treatment-effect tables, surprise-pattern detection records,
    abductive hypothesis/factor proposals, scratchpad memory update/replay
    artifacts, environment-shift/generalization checks, four benchmark task
    rows, seed/step/result tables, ablation rows for ShinkaEvolve,
    CausalPlanner(Meta), and COAT, model/runtime provenance, and README/ROADMAP
    wording that keeps current token-pattern factor guidance separate from
    CausalEvolve-style causal discovery. The result rows must include Table 1
    final-step CausalEvolve values (`Hadamard` mean/best `0.568`/`0.576`,
    `Second Autocorr` `0.793`/`0.809`, `Circle Packing` `2.476`/`2.564`,
    `AIME` `38.89`/`40.00`) and the corresponding ShinkaEvolve,
    CausalPlanner(Meta), and COAT rows.

- [ ] Add DeepEvolve cross-file research/debug-loop source boundary before
      retrieval-agent claims.
  - Spec evidence: local arXiv `2510.06056v1`, `Scientific Algorithm
    Discovery by Augmenting AlphaEvolve with Deep Research`, by Gang Liu,
    Yihan Zhu, Jie Chen, and Meng Jiang was submitted on October 7, 2025; the
    cached PDF hash is
    `e2f578c3b7979eb72857b1545b244405cf0fa8792bab82645e58c97cf3681f86`
    and the PDF metadata declares CC BY 4.0. It integrates external deep
    research with algorithm evolution through six modules:
    planning research questions, web searching, writing a proposal with
    pseudo-code, coding across multiple files, evaluation, and evolutionary
    selection. The paper adds reflection checkpoints, cross-file edit
    localization, debugging attempts from execution feedback, a database with
    algorithm descriptions and inspirations, MAP-Elites/islands selection, and
    nine benchmark tasks across chemistry, mathematics, biology, materials, and
    patents. The public code URL is `https://github.com/liugangcode/deepevolve`;
    extracted links also include OpenEvolve, OpenAI/Google Deep Research pages,
    and Kaggle/source URLs for molecular translation, Parkinson's disease,
    nuclei image, Open Vaccine, polymer prediction, and USP P2P.
  - Current evidence: `libreevolve/plugins/deep_research.py` implements bounded
    arXiv/web-search context, query construction, cache snapshots, redacted
    payload sidecars, source-ranking provenance, lexical grounding, and
    non-authoritative prompt wrappers. README and `papers/README.md` state that
    this is not a DeepEvolve-style hypothesis-refinement or cross-file
    debugging loop. Existing active TODOs cover retrieval transport and source
    integrity, but there is no source-specific code TODO for `2510.06056`, no
    plan/search/write proposal lifecycle, no multi-file edit delimiter schema,
    no implementation-difficulty/originality/future-potential scoring, no
    debugging-attempt budget with score-zero fallback, no reflection-agent
    checkpoints, no algorithm textual description record, no nine-task
    benchmark fixtures, no `DEEPEVOLVE` block reachability checks, no
    30-minute/single-GPU budget records, and no success-rate/ablation report
    tied to this paper.
  - Required result: add source-boundary metadata and implementation gates for
    `2510.06056`: arXiv version/date/PDF hash, code repository status,
    problem/input schema for evaluation code/data/textualization/user
    instructions, algorithm-description schema with motivation, summary,
    pseudo-code, score, originality, future potential, and implementation
    difficulty, plan/search/write proposal artifacts, external source
    provenance beyond current bounded retrieval context, cross-file coding
    region delimiters and localization records, self-reflection and debugging
    attempt records with execution errors/warnings and fallback scoring,
    evolutionary database inspiration records, MAP-Elites/island compatibility,
    benchmark rows for the nine paper tasks, Table 2 performance/runtime
    values, Table 3 debugging success-rate values, deep-research ablation rows,
    runtime/GPU budget records, Figure 3 LLM-as-judge originality/future-
    potential/difficulty records, Table 4 deep-research ablation rows for
    Molecular Prediction and Circle Packing, Appendix C user-query and
    hyperparameter records, and README/ROADMAP wording that keeps current
    retrieval context separate from DeepEvolve execution semantics.

- [ ] Add MAP-Elites illumination-algorithm source boundary before archive
      completeness claims.
  - Spec evidence: local arXiv `1504.04909`, `Illuminating search spaces by
    mapping elites`, by Jean-Baptiste Mouret and Jeff Clune is a preliminary
    draft dated April 21, 2015; the cached PDF has 15 pages, byte count
    `3221283`, and SHA-256
    `df7344343b14893a1d79a5459c1f56db50562e246d132cd0269f5201d1455872`.
    It defines MAP-Elites as an illumination algorithm that maps the highest-
    performing elite for each cell in a user-chosen feature space. The paper
    specifies a feature descriptor `b(x)`, performance function `f(x)`,
    discretized N-dimensional maps `P` and `X`, random initialization for `G`
    solutions, random elite selection plus mutation/crossover variation,
    replacement only when a candidate improves its feature cell, and evaluation
    criteria for global performance, global reliability, precision, and
    coverage.
  - Current evidence: `libreevolve/population/map_elites.py` implements a local
    3D archive whose defaults are scalar archive selection score, serialized
    workspace complexity, and TF-IDF diversity; configurable descriptor axes can
    use normalized metrics or numeric metadata, and archive snapshots persist
    descriptor policy/model metadata with insertion-time cell coordinates and a
    no-rebin policy. `IslandModel` adds synchronous ring migration, which is not
    the paper's default pseudocode. Existing active TODOs mention MAP-Elites
    descriptor and archive gaps, but there is no source-specific code TODO for
    `1504.04909`, no explicit `b(x)` feature-descriptor contract separate from
    current three-axis archive coordinates, no random-initialization/variation
    policy evidence, no batched/hierarchical-resolution MAP-Elites mode, no
    illumination-map report, no coverage/reliability/precision metrics, no
    feature-space visualization artifacts, no parent-distance/lineage stepping-
    stone analysis, and no paper-domain reproduction rows for modular neural
    networks, simulated soft robots, or the real soft arm.
  - Required result: add source-boundary metadata and implementation gates for
    `1504.04909`: paper version/date/PDF hash, feature-descriptor schema,
    user-chosen dimension declarations, discretization/binning resource policy,
    performance function and cell replacement records, initialization and
    variation policy records, feature-performance map export with both `P` and
    `X` identities, empty/unfillable cell diagnostics, formal global
    reliability `G(m)`, precision/opt-in reliability `P(m)`, coverage, and
    global-performance reports, normalized comparison records against
    traditional EA, novelty search with local competition, random sampling,
    EA+D, MOLE, and grid search where applicable, archive heatmap/lineage
    visualization artifacts for Figures 3-7, parent-cell distance and full-
    lineage stepping-stone reports from Figure 4, descriptor compatibility and
    rebin tests, experiment-parameter rows for retina (`16x16` to `512x512`,
    batch `2000`, initial batch `20000`, `10000` iterations), simulated soft
    robots (`64x64` to `128x128`, batch `1024`, initial batch `4096`, `1400`
    iterations), and real soft arm (`420` MAP-Elites evaluations, initial batch
    `120`, `30` iterations), benchmark/domain reproduction notes, and
    README/ROADMAP wording that keeps LibreEvolve's current 3D archive separate
    from full MAP-Elites illumination evidence.

- [ ] Add hardness-of-approximation proof-element gates before theoretical-CS
      application claims.
  - Spec evidence: local arXiv `2509.18057v7`, `Reinforced Generation of
    Combinatorial Structures: Hardness of Approximation`, by Ansh Nagda,
    Prabhakar Raghavan, and Abhradeep Thakurta was submitted as v7 on March 9,
    2026; the cached PDF has 39 pages, byte count `7719868`, SHA-256
    `32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842`,
    and CC BY 4.0 metadata. It uses AlphaEvolve to discover finite
    combinatorial structures for complexity-theory proofs: Ramanujan graph
    witnesses for MAX-CUT/MAX-Independent-Set certification, MAX-3-CUT and
    MAX-4-CUT gadget reductions from 3LIN(k), and metric-TSP equation gadgets.
    It also uses AlphaEvolve to evolve faster verifiers by scoring runtime plus
    correctness checks, reports about `10,000x` verifier speedups for final
    MAX-k-CUT gadgets, and states that final gadgets were verified by brute-
    force algorithms independent of the evolved fast verifiers.
  - Current evidence: `papers/README.md` marks `2509.18057` as background only
    with no graph/certification benchmark, while
    `libreevolve/problems/benchmarks/result_certification.py` provides a
    generic paper-result certification schema. Existing TODOs ask for general
    theoretical-CS proof-element source tracking, but there is no source-
    specific code gate for graph/gadget artifact schemas, witness encoding,
    Ramanujan checks, MAX-CUT/independent-set scoring, MAX-k-CUT
    completeness/soundness verifier contracts, TSP/MWST gadget verification,
    evolved-verifier runtime datasets, synthetic correctness datasets, judge-
    LLM records, human-inspection records, final brute-force verification
    provenance, or theorem-lifting boundaries.
  - Required result: add implementation gates for `2509.18057`: arXiv version/
    date/PDF hash, source/repository/artifact status, Ramanujan graph and
    witness schemas, Table 1 bound rows (`MAX-CUT d=3/4`,
    `MAX-IND-SET d=3/4` with LB/UB comparisons), MAX-3-CUT and MAX-4-CUT
    gadget edge-list/weight schemas including `m=14` and `m=19` verifier-size
    contexts, metric-TSP/MWST equation-gadget schemas (`n_aux=4`, `c(H)=s(H)=10`,
    `111/110` hardness), theorem/result ids for Theorems 2.1, 2.2, 3.1, 3.2,
    and 4.1, verifier API contracts, synthetic verifier-speed dataset records
    from 20 random models with one-second average-size scoring, correctness-
    check and judge-LLM records, evolved-verifier runtime telemetry, independent
    brute-force verifier outputs, final graph/gadget inventories, explicit PDF
    link extraction/source-repository status, lifting-framework metadata linking
    finite structures to universal theorem statements, human-inspection/proof-
    handoff attribution, baseline/SOTA comparison rows (`0.9883` to `0.987`,
    `0.9853` gadget baseline to `0.9649`, `117/116` to `111/110`), and
    README/ROADMAP wording that keeps LibreEvolve's generic evaluator validation
    separate from AlphaEvolve-discovered complexity-theory proof elements.
