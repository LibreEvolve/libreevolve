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
    adding special comment markers around blocks to be evolved.
  - Current evidence: LibreEvolve validates Python `# EVOLVE-BLOCK-START/END`
    markers, rejects malformed or unsupported non-Python marker-like syntax,
    materializes bounded workspaces, and records candidate-language policy
    boundaries. Those mechanics prove marker parsing for local seed files, but
    they do not prove an AlphaEvolve-style integration workflow for a
    pre-existing codebase: baseline codebase identity, marker-only setup diff,
    untouched skeleton preservation, language/comment syntax, component span
    inventory, evaluator entrypoint continuity, or measured setup burden.
  - Required result: add integration metadata and validators for existing
    codebases: original codebase/artifact id, pre-marker source hashes,
    marker-added diff summary, evolved-block span ids, unchanged skeleton
    hashes, language/comment grammar, evaluator-call path before/after marker
    insertion, setup-change counts, and README/ROADMAP wording that separates
    local evolve-block parsing from paper-faithful minimal-change codebase
    integration evidence.

- [ ] Add Figure 3 evolve-block marker spelling provenance.
  - Spec evidence: AlphaEvolve Section 2.1 names the special marker comments
    as `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END`, while PDF text
    extraction from Figure 3(a) shows one opening marker as
    `# EVOLVE-BLOCK START` and another as `# EVOLVE-BLOCK-START`.
  - Current evidence: LibreEvolve deliberately enforces the local exact
    Python marker grammar `# EVOLVE-BLOCK-START/END` and rejects malformed or
    unsupported marker-like syntax. Existing Figure 3 exhibit TODOs require
    source/prompt/output excerpt artifacts, but they do not explicitly classify
    this marker-text variant as canonical section prose, rendered figure text,
    extraction/OCR uncertainty, or paper typo.
  - Required result: record marker text per paper source location and
    subfigure, preserve source artifact hashes or screenshots for the variant,
    classify the discrepancy before using it in docs, and keep parser/support
    claims scoped to the implemented local grammar unless a deliberate
    compatibility mode for the space variant is added.

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
    replacement.
  - Required result: extend topology diagnostics for future topology surfaces
    such as bulk directory operations or language/build-runner generated
    artifacts, and preserve the stable `CandidateMaterializationError`
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
    classification, grouped-gap labels, or whether active references still map
    to open TODO content.
  - Required result: extend paper-manifest or paper-index validation with a
    TODO-coverage cross-reference checker: parse the table, require exact
    manifest-id coverage, reject duplicates/extras, validate safe existing
    `docs/todo/` paths, classify active and completed evidence targets,
    allow only declared grouped-gap labels, and optionally verify that active
    evidence rows contain open backlog text. Keep docs wording clear that
    status-table validation is not the same as verified backlog traceability.

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
    binary static seed asset while preserving its smoke-only scope.
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
    for comparing AlphaEvolve-alignment features, and real anti-gaming fixtures
    for benchmark-grade operation/rank discovery. The matrix smoke
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
    provenance needed to reproduce Appendix A algorithms.
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
    notebook/export artifacts to the registered target suite; keep the existing
    Python smoke example clearly outside AlphaEvolve-comparison evidence until
    it emits validated tensor-result reports. The remaining gap is generating
    discovered exact algorithms, certificates, and notebook/export files across
    the registered target suite, not validating declared artifact inventory,
    validating the checked bundle wrapper, or emitting the one checked Strassen
    baseline once those files exist.

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
