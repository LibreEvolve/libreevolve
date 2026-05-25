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

## Problem and Code Representation

- [x] Add AlphaEvolve-style evolve-block markers.
  - Spec evidence: AlphaEvolve supports blocks marked with
    `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END`, while the surrounding
    code acts as a skeleton.
  - Current evidence: `libreevolve/core/candidate.py` parses evolve-block
    markers and constrains mutations to marked regions within single-file and
    workspace candidates.
  - Status: implemented in `libreevolve/core/candidate.py`; one or more marked
    regions are parsed and skeleton code is preserved during mutation when
    markers are well-formed.
  - Required result: problem loading should support one or more marked
    evolvable regions, preserve non-evolved skeleton code, and apply mutations
    only where configured.

- [x] Reject malformed evolve-block marker structures during mutation.
  - Spec evidence: AlphaEvolve's task API relies on marked evolvable blocks
    inside a skeleton; an invalid marker layout should not change which code is
    evolvable without an explicit diagnostic.
  - Current evidence: `validate_evolve_blocks()` checks marker pairing,
    nesting, block-name syntax, duplicate block names, orphan end markers, and
    malformed end markers before mutation. `apply_candidate_mutation()` fails
    closed with `malformed_evolve_blocks:<reason>`, and workspace mutation
    prefixes the target path in the diagnostic.
  - Status: implemented at mutation-application time, with tests for missing
    end markers, orphan end markers, nested blocks, duplicate names, invalid
    names, anonymous block naming, and malformed target files in workspaces.
    Problem loading still does not prevalidate seed files before the first
    evaluation/mutation path sees them.
  - Required result: validate marker pairing, nesting, names, and duplicate
    block identities during problem load or mutation application; reject or
    quarantine malformed candidates with explicit errors; add tests for missing
    end markers, orphan end markers, nested blocks, duplicate names, and mixed
    valid/invalid files in workspaces.

- [x] Support multi-component and multi-file codebase evolution.
  - Spec evidence: AlphaEvolve evolves large code pieces spanning multiple
    functions and components and can evolve an entire code file/codebase.
  - Current evidence: `CandidateWorkspace` represents text file sets,
    `Program.files` stores candidate files, loader accepts seed directories,
    file-section mutations route edits across files, and the evaluator
    materializes the whole workspace for validators.
  - Status: basic local workspace evolution is implemented and covered by
    tests. Remaining limitations: Python syntax validation only, no arbitrary
    language runners/build systems, and `best.py` is still a primary-file
    convenience artifact. Candidate paths reject traversal, drive-letter, and
    colon-component paths before materialization.
  - Required result: represent a candidate as a project/file set, apply diffs
    across marked files/components, and pass the whole candidate workspace to
    `evaluate`.

- [x] Unify file-section path parsing with workspace path normalization.
  - Spec evidence: AlphaEvolve can evolve existing code files/codebases, where
    ordinary repository filenames may contain hyphens, spaces, generated-file
    suffixes, or other characters not represented by the current parser.
  - Current evidence: `_FILE_SECTION_PATTERN` captures the full file-section
    header line and `apply_workspace_mutation()` validates it through
    `normalize_candidate_path()`. File sections now accept nested paths,
    hyphens, spaces, Unicode filename characters, and Windows-style
    backslashes when the normalized path is safe; empty paths and unsafe
    normalized paths are rejected explicitly.
  - Status: implemented for current `<<<FILE ... >>>FILE` envelopes, with
    tests for hyphenated, spaced, nested, backslash-normalized, Unicode, colon,
    and empty file-section paths.
  - Required result: use one validated relative-path grammar for loader,
    prompt envelopes, mutation parsing, normalization, and diagnostics; reject
    unsafe paths explicitly; add tests for hyphenated, spaced, nested,
    backslash, Unicode/normalization, and malformed file-section paths.

- [x] Detect normalized-path and host-filesystem path collisions.
  - Spec evidence: AlphaEvolve-style codebase evolution needs a faithful
    candidate file set. Two logical candidate files should not silently collapse
    in memory or overwrite each other when validators materialize the
    workspace.
  - Current evidence: `normalize_candidate_path()` normalizes candidate paths
    to Unicode NFC after slash normalization. `CandidateWorkspace.__post_init__()`
    rejects raw file keys that normalize to the same candidate-relative path,
    including `pkg\\helper.py` versus `pkg/helper.py` and composed/decomposed
    Unicode names. `_load_initial_workspaces()` now inherits that policy for
    seed directories. `CandidateWorkspace.materialize()` preflights
    case-folded host paths before writing any file; tests prove `Readme.md`
    and `README.md` collisions fail without partial materialization.
    Duplicate edit sections for the same `<<<FILE path ...>>>` target fail
    with `path:duplicate_file_section`. Ambiguous edit/delete, edit/move,
    duplicate move-target, and chained move sequences fail before partial
    application instead of silently dropping a candidate file.
  - Status: implemented with candidate, loader, mutation, and materialization
    regression tests.

- [x] Detect malformed or ignored mutation envelopes.
  - Spec evidence: AlphaEvolve-style codebase mutation should make every
    intended edit either apply or fail with a diagnostic; silently dropping an
    LLM-proposed file/block section can corrupt the audit trail and hide
    partial candidate changes.
  - Current evidence: `apply_workspace_mutation()` validates file-section
    envelopes before parsing sections, and multi-block full replacement
    validates block-section envelopes before applying replacements. Unmatched,
    orphaned, nested, empty-name, invalid-name, and unsafe-path sections fail
    before partial edits are applied.
  - Status: implemented for current `<<<FILE ... >>>FILE` and
    `<<<BLOCK ... >>>BLOCK` envelopes, with tests proving mixed valid plus
    malformed sections do not apply partial candidate changes.
  - Required result: parse mutation envelopes as a whole document, reject or
    record unmatched `<<<FILE`/`>>>FILE` and `<<<BLOCK`/`>>>BLOCK` spans,
    surface diagnostics for unsupported names/paths, and add tests for mixed
    valid plus malformed sections so intended edits cannot disappear silently.

- [x] Reject duplicate block sections in multi-block full replacement.
  - Spec evidence: AlphaEvolve-style skeleton preservation needs every
    evolvable block edit to be unambiguous. Multiple edits for the same named
    block should either be rejected or represented explicitly in a typed
    mutation record.
  - Previous evidence: `_apply_full_replacement()` stored parsed
    `<<<BLOCK name ... >>>BLOCK` sections in a dict, so a duplicate name
    silently overwrites the earlier body. A local proof with two `<<<BLOCK a`
    sections returned `err=None` and applied only the later `x = 99` body.
  - Status: implemented. Duplicate block-section names now fail closed with
    `malformed_block_sections:duplicate_name` before applying a multi-block
    full replacement.
  - Validation: `tests/core/test_candidate.py` covers duplicate block-section
    rejection and proves the original candidate is unchanged.

- [x] Support file deletion and rename/move operations in workspace mutations.
  - Spec evidence: AlphaEvolve can evolve whole files/codebases, not only edit
    text inside a fixed set of files. Real codebase evolution may need removing
    obsolete files, renaming modules, or moving components while preserving
    imports and validator expectations.
  - Status: implemented. `apply_workspace_mutation()` supports
    `<<<FILE DELETE path ... >>>FILE`, `<<<FILE MOVE old -> new ... >>>FILE`,
    `<<<FILE RENAME old -> new ... >>>FILE`, and
    `<<<FILE PRIMARY path ... >>>FILE`, while preserving existing
    `<<<FILE path ... >>>FILE` edit/create behavior.
  - Evidence: tests cover deleting helper files, moving/renaming modules,
    primary-file changes, missing sources, target collisions, unsafe targets,
    and no partial apply on topology errors. Topology changes persist through
    existing `Program.files`, `primary_file`, `history.jsonl`, and
    `best_workspace/` logging/export paths.

- [x] Make materialized workspace execution import- and cwd-faithful.
  - Spec evidence: AlphaEvolve can evolve whole files/codebases, so evaluators
    should be able to exercise a candidate as a normal project with local
    imports and relative data paths.
  - Current evidence: `CascadeEvaluator._run_subprocess()` materializes the
    candidate into a temporary `candidate/` directory, runs the validator
    subprocess with that directory as `cwd`, passes it as `workspace_path`, and
    adds it to `sys.path`. Tests cover candidate package imports and relative
    candidate file reads without validator-managed path edits.
  - Status: implemented for local Python workspace execution. Remaining
    divergence: this is not a container/build-system runner, environment
    isolation and artifact collection are still open, and non-Python
    workspaces remain out of scope.
  - Required result: define and test the workspace execution contract
    (`cwd`, `PYTHONPATH`/`sys.path`, environment, package entrypoints, and
    relative artifact paths); make project-local imports and relative file
    access work by default where appropriate, or document the deliberate
    validator-managed divergence.

- [x] Make problem-local evaluator imports package-faithful.
  - Spec evidence: AlphaEvolve task setup can include evaluator code and
    problem-specific test logic. Reproducible evaluation should support
    ordinary multi-file validator modules, not only a single self-contained
    `validate.py`.
  - Current evidence: `_RUNNER` adds `validate_path.parent` to `sys.path`
    before loading the validator file, so sibling helper modules beside
    `validate.py` can be imported. Tests cover a problem-local `scoring.py`
    helper imported by `validate.py`.
  - Status: implemented for sibling helper imports beside validator entrypoint
    files. Remaining divergence: problem directory is not `cwd`, package-style
    validator module loading is not a first-class API, and evaluator code/data
    hashes are not in manifests yet.
  - Required result: define evaluator import semantics for `validate.py`,
    stage validators, sibling helper modules, packages, and relative data
    files; set `cwd`/`PYTHONPATH` or use an explicit module/package loader as
    documented; include evaluator code hashes in manifests; and add tests for
    problem-local helper imports, package validators, relative data files, and
    failure diagnostics.

- [x] Add language-agnostic candidate support or narrow the claim to Python.
  - Spec evidence: AlphaEvolve is described as being able to evolve code in any
    language.
  - Current evidence: `CascadeEvaluator.evaluate()` calls Python `compile()`
    and imports Python `validate.py` (`libreevolve/core/evaluator.py:31-38`).
  - Status: README, architecture, problem format, and roadmap now state the
    current Python-only/local-workspace scope as a deliberate divergence.
  - Required result: either introduce pluggable language runners and validators
    or document Python-only scope as a deliberate divergence.

- [x] Add direct full-code/full-block replacement mode in addition to diffs.
  - Spec evidence: AlphaEvolve can be configured to ask for a complete code
    block when a rewrite is more appropriate than a small modification.
  - Current evidence: `Config.mutation_mode` and CLI `--mutation-mode` support
    `diff` and `full`; generation now calls `apply_candidate_mutation()`.
  - Status: implemented as `Config.mutation_mode` and CLI `--mutation-mode`,
    with `diff` and `full` modes covered by tests.
  - Required result: add a per-problem/per-run mutation mode for full block,
    full file, or diff-based edits, with validator coverage for each mode.

- [x] Make prompt instructions mutation-mode aware.
  - Spec evidence: AlphaEvolve can be configured to ask the LLM for a full
    code block instead of SEARCH/REPLACE diffs; the prompt must match the
    configured parser/application mode for that run.
  - Current evidence: `PromptSampler.build()` accepts `mutation_mode`, exposes
    `{mutation_mode}` and `{mutation_instructions}` to templates, and the
    default template renders diff instructions for `diff` mode and full-file /
    full-block replacement instructions for `full` mode. `evolve()` passes
    `config.mutation_mode` into prompt construction and stores the mode in
    candidate metadata.
  - Status: implemented for the current `diff` and `full` modes, with tests
    covering direct prompt rendering, custom template compatibility, and loop
    persistence of full-mode prompt instructions.
  - Required result: render mode-specific mutation instructions and examples
    for `diff`, full-file, full-block, and multi-file full replacement modes;
    include the active mode in prompt metadata/history; add tests proving the
    default prompt changes when `mutation_mode` is `full` while preserving
    backward-compatible custom templates.

- [x] Add AlphaEvolve canonical SEARCH/REPLACE diff marker compatibility.
  - Spec evidence: AlphaEvolve Section 2.3 and Figure 3 use
    `<<<<<<< SEARCH`, `=======`, and `>>>>>>> REPLACE` blocks.
  - Status: implemented in `libreevolve/core/diff.py` via
    `parse_diff_blocks()`, which accepts both canonical AlphaEvolve fences and
    compact local fences. Tests cover low-level diff application, evolve-block
    restriction, mixed-format document order, and multi-file file-section
    routing for canonical blocks.
  - Required result: keep both formats backward-compatible in prompt docs,
    parser/apply logic, and mutation tests.

- [x] Make paper-inspired plugins consume canonical mutation formats.
  - Spec evidence: AlphaEvolve uses canonical SEARCH/REPLACE blocks, and
    plugin analyses that infer guidance from mutations should share the same
    parser contract as candidate mutation application.
  - Current evidence: `CausalPlugin._detect_factors()` now calls the shared
    `parse_diff_blocks()` parser, so compact local fences and canonical
    AlphaEvolve fences are classified through the same mutation parsing
    contract as candidate application. Empty or unparseable mutation text now
    uses a deterministic fallback factor instead of random factor guidance.
  - Status: implemented for the CausalEvolve-inspired plugin; an audit found
    no other built-in plugin directly parsing SEARCH/REPLACE blocks.
  - Required result: route plugin mutation analysis through
    `parse_diff_blocks()` or a shared mutation AST, add CausalPlugin tests for
    compact and canonical diffs, preserve deterministic fallback semantics,
    and audit other plugins for raw diff-format assumptions.

- [ ] Capture proposal ideas/rationale separately from patch application.
  - Spec evidence: AlphaEvolve Figure 3 asks the LLM to "suggest a new idea"
    and describe each change with SEARCH/REPLACE blocks; its process uses LLMs
    to generate, critique, and evolve a pool of algorithms.
  - Current evidence: `PromptSampler.DEFAULT_TEMPLATE` says "No comments. No
    markdown fences. No explanation. Just the raw diff block." The diff parser
    applies only patch blocks and the database stores the raw diff, but there
    is no structured proposal idea, rationale, or hypothesis field that can be
    inspected, critiqued, scored, or resurfaced independently.
  - Required result: allow and parse bounded proposal rationale/idea sections
    when configured, store them in candidate metadata, render useful prior
    ideas in prompts, and keep patch extraction robust for both rationale plus
    diff and diff-only compatibility modes.

- [x] Export complete best workspaces, not only the primary file.
  - Spec evidence: AlphaEvolve can evolve entire code files/codebases, so the
    output artifact must preserve all evolved components.
  - Current evidence: `libreevolve/cli.py` writes `best.py` as a primary-file
    compatibility view and materializes `best.workspace()` to
    `runs/<name>/best_workspace/`. CLI tests cover multi-file best-workspace
    export.
  - Status: implemented for text-file candidate workspaces. Remaining
    divergence: run-directory collision semantics are still undefined, and
    binary/static non-text artifacts are not first-class candidate members.
  - Required result: write a reproducible `best_workspace/` or archive with all
    candidate files, preserve `best.py` only as a compatibility convenience,
    and document/export this artifact in tests and run docs.

- [ ] Support problem-defined candidate abstraction modes or document the
  narrower code-file abstraction.
  - Spec evidence: AlphaEvolve Section 2.1 describes flexible solution
    abstractions, including raw solution strings, constructor functions,
    bespoke search algorithms, and co-evolved intermediate solutions plus
    search procedures.
  - Current evidence: `CandidateWorkspace` models candidates as local text file
    sets with a primary Python code view; validators can interpret code however
    they want, but the framework has no first-class representation for paired
    solution/search artifacts, non-code solution objects, or problem-defined
    candidate serializers.
  - Required result: either add a problem API for candidate abstraction modes,
    rendering, mutation, materialization, and validation, or clearly document
    that LibreEvolve currently evolves code file sets only.

- [ ] Define non-text artifact handling for workspace/codebase candidates.
  - Spec evidence: AlphaEvolve can operate on existing codebases and systems
    code where supporting assets, generated artifacts, fixtures, and binary
    inputs may be part of the runnable project.
  - Current evidence: `_load_initial_workspaces()` reads every non-hidden,
    non-`__pycache__` file in a seed directory with `read_text(encoding="utf-8")`.
    `CandidateWorkspace` stores `dict[str, str]`, prompt rendering assumes text,
    and `materialize()` writes text files. Binary or non-UTF-8 seed artifacts
    can fail problem load or cannot be represented without lossy conversion.
  - Required result: define text-vs-binary candidate artifact policy, support
    copied static assets or encoded artifacts where needed, record artifact
    hashes/provenance, and test binary fixture, large fixture, and generated
    artifact behavior.

## Prompt Sampling and Context

- [x] Replace the simple prompt builder with a configurable prompt sampler.
  - Spec evidence: AlphaEvolve prompt sampling supports long contexts,
    previous solutions, system instructions, explicit context, stochastic
    formatting, rendered evaluation results, and meta-prompt evolution.
  - Current evidence: `build_prompt()` delegates to
    `libreevolve/core/prompt.py::PromptSampler`, which supports configurable
    templates, explicit context files, evaluator feedback, inspirations,
    plugin context, and recent failed/rejected mutation records.
  - Status: implemented in `libreevolve/core/prompt.py` with configurable
    templates, problem context files, inspirations, metrics, evaluator feedback,
    plugin context, and recent failed/rejected mutation records.
  - Required result: introduce prompt templates, stochastic template choices,
    user-provided context files, and structured prompt sections.

- [ ] Implement AlphaEvolve-style stochastic formatting controls.
  - Spec evidence: AlphaEvolve Section 2.2 describes template placeholders with
    human-provided alternatives instantiated using probability distributions
    from a separate config file.
  - Current evidence: `PromptSampler` selects among whole prompt templates with
    a seeded RNG, but it does not parse placeholder alternatives or probability
    distributions inside templates/config.
  - Required result: add a deterministic stochastic-formatting schema,
    probability validation, seeded sampling tests, and docs that distinguish it
    from whole-template variants.

- [x] Include basic rendered evaluation stage summaries in prompts.
  - Spec evidence: AlphaEvolve prompts can include a program, the result of
    executing that program, and scores assigned by `evaluate`.
  - Current evidence: evaluator returns `EvaluationResult`; `Program` stores
    `metrics` and `evaluation`; `PromptSampler` renders the last three stage
    names, pass/fail states, scores, and errors.
  - Status: implemented as compact stage-summary rendering. Full evaluator
    output rendering remains open below.
  - Required result: return an evaluation result object, store it with the
    program, and render basic stage status/score/error feedback in future
    prompts.

- [ ] Render richer evaluator outputs and feedback records in prompts.
  - Spec evidence: AlphaEvolve prompt context can include the result of
    executing a program, program outputs, and scores so future proposals can
    learn from prior behavior.
  - Current evidence: `EvaluationResult` stores stdout, stderr, errors,
    metadata, and stage outcomes, and LLM feedback graders store raw response
    provenance, but `PromptSampler._render_feedback()` only renders a compact
    last-three-stage summary and omits stdout/stderr, sample-level outputs,
    artifacts, grader feedback, and validator-provided diagnostic metadata.
  - Required result: add bounded prompt rendering for evaluator stdout/stderr,
    validator feedback, artifacts, sample-level stage diagnostics, and LLM
    grader summaries, with redaction/truncation rules and tests proving prompts
    contain the intended evidence without exceeding configured budgets.

- [ ] Add global prompt budget and context-window accounting.
  - Spec evidence: AlphaEvolve prompt sampling supports long contexts and
    configurable prompt construction; practical long-context evolution needs
    deterministic packing so parent code, inspirations, evaluator feedback,
    explicit context, plugin context, and failure memory fit the selected LLM.
  - Current evidence: `PromptSampler.build()` formats the selected template
    with full rendered context, parent files, inspirations, plugin context, and
    recent failures. Only individual problem context files are character-bounded
    by `_summarize_context_text()`; parent/inspiration workspaces, plugin
    output, feedback sections, and the final rendered prompt have no global
    token/character budget, truncation policy, priority order, or prompt-size
    metadata in history/manifests.
  - Required result: add configurable prompt budgets per backend/run, a
    deterministic section-priority packing policy, token estimation or provider
    usage accounting, prompt-size diagnostics in history, tests for oversized
    workspaces/context/plugins/inspirations, and clear behavior when required
    sections cannot fit.

- [ ] Add prompt/history redaction and context data-retention controls.
  - Spec evidence: AlphaEvolve-style task setup can include existing codebases,
    evaluator outputs, explicit context files, and literature. When those
    sources are sent to external LLMs and stored for future database sampling,
    the experiment needs explicit data-retention, redaction, and audit
    boundaries.
  - Current evidence: `PromptSampler._render_context()` renders problem
    context text directly, `_render_program_files()` renders full parent and
    inspiration file contents, `evolve()` stores the rendered mutation prompt
    under `Program.metadata["prompt"]`, stores critique prompts under
    `metadata.critique.prompt`, and `ProgramDatabase.log()` writes metadata
    verbatim to `history.jsonl`. `build_critique_prompt()` embeds the full
    original prompt. Basic secret redaction exists only for LLM feedback
    workspace rendering in `libreevolve/core/feedback.py`; mutation prompts,
    critique prompts, plugin context, explicit context files, failure mutation
    text, and persisted run history are not redacted or covered by a retention
    policy.
  - Required result: define per-role prompt logging modes
    (full/redacted/hash-only/off), apply shared secret redaction to mutation,
    critique, feedback, plugin, and context prompt sections before provider
    calls and/or before persistence as configured, record redaction metadata
    and hashes, document data-retention defaults, and add tests proving
    secret-like values in seeds/context/plugin text do not appear in persisted
    artifacts when redaction is enabled.

- [x] Make failed/rejected mutation memory complete and queryable.
  - Spec evidence: AlphaEvolve prompt context and database are built around
    past trials, ideas, evaluation results, and feedback, including enough
    history to avoid repeating unproductive proposals.
  - Status: implemented. `ProgramDatabase.log_failure()` writes
    `failure_history.jsonl` records and mirrors the same bounded failure record
    into candidate metadata. The loop logs every post-plugin candidate with
    `fitness < VALID_THRESHOLD`, including malformed/no-op/search-miss diffs
    that leave code unchanged and workspace failures that modify only
    non-primary files.
  - Evidence: failure records include mutation text, diff error, parent id,
    changed file paths, file deltas, evaluator diagnostics, and repetition
    counts. `PromptSampler` renders bounded structured failure summaries in
    later prompts. Tests cover malformed diff persistence, next-prompt failure
    rendering, queryable failure-history records, repetition counts, and
    non-primary-file workspace failures.

- [x] Implement meta-prompt evolution.
  - Spec evidence: AlphaEvolve co-evolves prompt instructions/context in a
    separate database analogous to solution programs and ablates "No meta
    prompt evolution" as a reduced system.
  - Current evidence: `PromptDatabase` stores prompt templates as prompt
    programs with lineage, selection, scoring, mutation, and append-only
    `prompt_history.jsonl`. The loop records `prompt_program_id` per candidate
    and can optionally ask the active LLM to mutate the prompt template at
    `meta_prompt_interval`.
  - Status: implemented as a local prompt-program database and optional
    interval-based LLM template mutation. Remaining hardening: richer prompt
    fitness and ablation reporting.
  - Required result: create a prompt-program representation, mutation path,
    scoring/selection policy, and integration into `build_prompt()`.

- [x] Define prompt-program reward normalization and selection policy.
  - Spec evidence: AlphaEvolve treats meta-prompt evolution as a system
    component that can be ablated, so prompt-program fitness should be
    reproducible, comparable across runs, and separate enough from candidate
    scoring to support prompt-lineage analysis.
  - Current evidence: `Config` now exposes `prompt_reward_mode`
    (`absolute` final composed child score or `improvement` over parent score),
    `prompt_reward_bounds`, and `prompt_explore_coeff`. `PromptDatabase`
    normalizes raw prompt rewards to `0..1`, clamps out-of-range values, uses
    the configured exploration coefficient in selection, and records reward
    telemetry under `program.metadata.last_prompt_reward`. `evolve()` records
    parent score, final candidate score, and prompt reward policy in
    `prompt_history.jsonl`; `manifest.json` includes the effective policy.
    Tests cover negative/out-of-range rewards, plugin-adjusted scores,
    multiple metrics, deterministic selection with zero exploration, and
    improvement-mode telemetry.
  - Status: implemented for a documented bounded scalar prompt-reward policy.
    Broader experiment ablation reporting remains tracked with compute-budget
    and run-manifest work.

- [x] Validate configured and mutated prompt templates before use.
  - Spec evidence: AlphaEvolve's prompt evolution must keep prompts usable by
    the evolutionary loop; malformed seed or evolved instructions should not
    break future generations.
  - Current evidence: `validate_prompt_template()` defines the allowed
    `PromptSampler` placeholder schema and requires `{task}` as the minimal
    configured/evolved template anchor. `Config.validate()` rejects malformed
    configured `prompt_variants` at startup. `PromptDatabase.__init__()`
    validates seed prompt programs, and `PromptDatabase.mutate()` validates LLM
    meta-prompt outputs before insertion. Rejected prompt mutations are written
    to `prompt_history_invalid.jsonl`, the parent prompt program receives a
    penalty event in `prompt_history.jsonl`, and the invalid template is not
    added to the prompt population. `PromptSampler.build()` also validates the
    selected template before formatting as a final guard.
  - Status: implemented with tests for unknown placeholders, malformed braces,
    empty placeholders, attribute/index placeholders, missing required fields,
    invalid configured variants, invalid configured prompt database seeds, and
    invalid LLM-mutated prompt templates in the evolution loop.

- [x] Add first-class literature/context ingestion.
  - Spec evidence: AlphaEvolve supports explicit context such as instructions,
    equations, code snippets, and relevant literature, including PDF files.
  - Current evidence: `load_problem()` reads problem-local `.txt`, `.md`,
    `.py`, and `.pdf` files from `context/`; text/code files are direct,
    PDFs are extracted with `pypdf`, long context is deterministically bounded,
    and `PromptSampler` renders source headers. `DeepResearchPlugin` remains a
    separate arXiv-search plugin, not the local literature ingestion path.
  - Status: implemented for deterministic local context ingestion and PDF text
    extraction with documented limits. Remaining hardening: semantic
    summarization/ranking for very large corpora.
  - Required result: allow problem-local context files, PDFs, equations, and
    code snippets to be selected, summarized, and rendered deterministically.

- [x] Add context-source manifests, recursive selection, and provenance.
  - Spec evidence: AlphaEvolve task setup can include explicit instructions,
    equations, code snippets, and literature; reproducible runs need to know
    exactly which context sources and excerpts were available to the prompt
    sampler.
  - Current evidence: `_load_context_files()` now walks `context/`
    recursively, honors optional `context.yaml` `include`, `exclude`, and
    `max_chars_per_source` fields, keys content by relative source path, and
    records per-source hashes, byte counts, original/rendered character counts,
    truncation spans, extraction status, and PDF page ranges where available.
    `PromptSampler` renders citation-style context headers with hash prefixes,
    excerpt spans, and extraction status. `ProgramDatabase._write_manifest()`
    persists `problem.context_sources` for run provenance. Tests cover nested
    context directories, duplicate basenames, changed source hashes, PDF
    no-text and extraction-failure metadata, manifest provenance, and prompt
    citation rendering.
  - Status: implemented for deterministic recursive local context provenance.
    Remaining context scale work is tracked separately under prompt budget and
    summarization/ranking tasks.

- [ ] Persist live retrieval/plugin context provenance.
  - Spec evidence: AlphaEvolve-style prompt sampling can include relevant
    literature and external context, but reproducible experiments need the
    source, query, retrieval time, selected excerpts, and failures that shaped
    a prompt.
  - Current evidence: `DeepResearchPlugin.on_generation_start()` derives a live
    query from the current best fitness, stores only `_synthesis`, and
    `build_extra_context()` injects that text into prompts. `arxiv_search()`
    returns only title/summary lines, discarding arXiv IDs, links, authors,
    update timestamps, query URL, provider metadata, and parse/network failure
    details. None of that retrieval state is written to `history.jsonl`,
    prompt history, plugin artifacts, or `manifest.json`.
  - Required result: store retrieval events with provider, query, generation,
    parent/best ids, result IDs/URLs, timestamps, selected snippets, failures,
    and hashes; render citations in prompt context; include plugin retrieval
    artifacts or summaries in run manifests; and test successful, empty,
    malformed, and failed retrieval paths.

- [ ] Attribute plugin prompt guidance and strategy choices.
  - Spec evidence: AlphaEvolve-style prompt assembly and paper-inspired
    plugins should make it possible to audit which prompt/context components
    influenced a candidate, especially when a plugin claims a specific search
    strategy such as ImprovEvolve's generate/improve/perturb loop.
  - Current evidence: `evolve()` builds plugin context with
    `"\n".join(p.build_extra_context(...))` and stores only the final rendered
    prompt in `Program.metadata["prompt"]`. There is no structured per-plugin
    context record, prompt-context hash, selected strategy, or plugin version.
    `ModularPlugin.build_extra_context()` always returns the same static
    `generate_config`/`improve`/`perturb` guidance and does not choose,
    execute, or log an ImprovEvolve operation for the candidate.
  - Required result: record per-plugin prompt-context events with plugin name,
    version/config, rendered text hash, parent/inspiration ids, and any chosen
    strategy or operation; for modular/ImprovEvolve-inspired guidance, either
    enforce and log generate/improve/perturb execution or label and test it as
    static prompt-only guidance.

- [ ] Replace context truncation with deterministic summarization/ranking for
  large literature corpora.
  - Spec evidence: AlphaEvolve Section 2.2 allows relevant literature, such as
    PDF files, as explicit context; for large corpora this requires selection
    and compression rather than simply dropping the tail.
  - Current evidence: `load_problem()` extracts `.pdf` text with `pypdf` and
    `_summarize_context_text()` keeps the first 6000 characters. This is
    deterministic, but it is not semantic summarization or relevance ranking.
  - Required result: add deterministic source selection and summarization
    metadata, preserve citations/source names in prompts, and test long
    multi-file context behavior.

## Evaluation

- [x] Enforce evaluator scalar outputs against declared metrics.
  - Spec evidence: AlphaEvolve task specification requires `evaluate` to
    return a dictionary of scalar evaluation metrics, and those metrics drive
    database selection, prompting, and multi-score optimization.
  - Current evidence: `load_problem()` now rejects missing metric names,
    duplicate names, invalid `direction` values, multiple primaries, and
    malformed/non-finite/non-increasing bounds for all declared metrics, and
    unsupported metric schema fields. `CascadeEvaluator._run_subprocess()`
    validates the last stdout JSON object against `metrics.yaml`: declared
    metrics must be present, undeclared metrics are rejected, `is_valid` must
    be boolean, and every non-`is_valid` metric must be finite numeric.
  - Status: implemented with loader and evaluator tests for unsupported schema
    fields, missing secondary outputs, non-scalar values, NaN/Infinity, and
    undeclared metrics. Multi-objective use of those metric vectors remains
    tracked separately.

- [x] Reject degenerate or inverted metric bounds.
  - Spec evidence: AlphaEvolve-style scoring depends on meaningful scalar
    metrics and comparable score normalization; local `metrics.yaml` bounds
    become part of primary fitness, archive performance coordinates, and future
    metric-vector policy.
  - Previous evidence: `_validate_metric_schema()` checked that bounds are a
    finite numeric pair, but it accepts `[1.0, 1.0]` and inverted ranges such
    as `[10.0, 0.0]`. `Problem.normalize_metric()` returns `0.5` for a
    zero-width range and otherwise computes with the negative range, producing
    plausible-looking normalized scores from an invalid schema.
  - Status: implemented. `metrics.yaml` bounds must now be finite, strictly
    increasing `[lo, hi]` pairs at problem-load time, so primary fitness and
    MAP-Elites performance normalization cannot inherit zero-width or inverted
    metric ranges.
  - Validation: loader tests cover zero-width and inverted metric bounds.

- [x] Enforce strict finite JSON serialization for run records.
  - Spec evidence: AlphaEvolve's program database is a machine-readable store
    of candidates, metrics, outputs, and feedback; downstream selection,
    replay, and analysis require valid finite scalar records.
  - Current evidence: `ProgramDatabase.log()`, `PromptDatabase._write()`,
    `ProgramDatabase._write_manifest()`, and `TTTRLPlugin._maybe_train()` now
    use strict JSON helpers with `allow_nan=False`. Invalid append records are
    not written to the primary stream; a diagnostic entry is written to
    `history_invalid.jsonl`, `prompt_history_invalid.jsonl`, or
    `grpo_data_invalid.jsonl`.
  - Status: implemented with tests for non-finite candidate fitness,
    non-finite prompt rewards with rollback, and non-finite GRPO export
    records. Broader queryable database/resume work remains tracked separately.

- [x] Give failure-history writes their own quarantine stream.
  - Spec evidence: AlphaEvolve-style run records should be machine-readable and
    stream-specific enough to audit which artifact failed to serialize without
    conflating candidate and failure-memory records.
  - Status: implemented. `ProgramDatabase.log_failure()` now uses
    `failure_history_invalid.jsonl` as a stream-specific quarantine path, while
    candidate-history append failures continue to use `history_invalid.jsonl`.
  - Validation: database tests prove invalid failure-history records are
    quarantined separately and do not create `history_invalid.jsonl`.

- [x] Expand the local configurable cascade into AlphaEvolve-grade evaluation
  cascades.
  - Spec evidence: AlphaEvolve supports ensembles of test cases of increasing
    difficulty, moving candidates to later stages only if earlier stages are
    promising.
  - Current evidence: `Config.eval_stages` supports local staged validators
    with distinct `validate_path` entrypoints, per-stage timeout and
    `min_score` thresholds, seeded samples, retries, stage context, and
    aggregated numeric metrics. It does not yet support distributed evaluator
    nodes or rich artifact collection beyond stdout/stderr.
  - Status: implemented for local AlphaEvolve-style hypothesis-test cascades;
    distributed/parallel evaluator workers remain a separate runtime item.
  - Required result: support configured stages, per-stage thresholds, sample
    sizes, retry/random-seed policies, and separate metrics per stage.

- [x] Aggregate syntax diagnostics across workspace files.
  - Spec evidence: AlphaEvolve-style codebase evolution needs actionable
    evaluator feedback for whole candidates, not only the first failing
    component encountered by a cheap prefilter.
  - Status: implemented. The syntax prefilter collects every Python
    `SyntaxError` across workspace `.py` files, returns an aggregate stage
    error string, and stores structured `metadata.syntax_errors` records with
    file path, line, offset, message, and summary. Non-Python text files are
    intentionally skipped by this Python-only syntax pass.
  - Validation: evaluator tests cover multiple invalid files, mixed
    valid/invalid files, and non-Python files.
  - Remaining prompt gap: `PromptSampler` still renders only compact recent
    stage summaries instead of dedicated syntax-diagnostic sections.

- [ ] Add metric-specific stage thresholds and explicit aggregation policies.
  - Spec evidence: AlphaEvolve evaluation cascades can use task-specific test
    ensembles of increasing difficulty, where pass/fail decisions may depend
    on different metrics, outputs, or sample distributions at each stage.
  - Current evidence: `eval_stages[].min_score` is a single threshold on
    normalized primary fitness. `_aggregate_metrics()` averages numeric metrics,
    `all()`s boolean metrics, and uses the last non-numeric value; this policy
    is hard-coded and does not let a stage require per-metric thresholds,
    quantiles, all-samples-pass, artifact checks, or custom aggregators.
  - Required result: add configured stage pass criteria by metric name,
    direction, bound, sample aggregation policy, and artifact/output checks;
    document defaults and test average/min/max/quantile/all-pass behavior.

- [x] Preserve retry-attempt outcomes in evaluation records.
  - Spec evidence: AlphaEvolve-style expensive evaluation depends on
    reproducible evidence about which tests, samples, retries, outputs, and
    failures led to accepting or rejecting a candidate.
  - Status: implemented for structured evaluation records and history.
    `_run_sample_with_retries()` now records `metadata.attempts` with attempt
    index, pass/fail, fitness, metrics, stdout, stderr, error, elapsed time,
    stage context, and per-stage diagnostics. The first valid attempt still
    determines pass decisions; all-fail retries return the final failed attempt
    while retaining all earlier attempts.
  - Validation: evaluator tests cover fail-then-pass, pass-first, and all-fail
    retry paths.
  - Remaining prompt gap: `PromptSampler` still renders only compact recent
    stage summaries rather than bounded retry-attempt details.

- [x] Capture validator-generated artifacts before temporary workspaces are
  deleted.
  - Spec evidence: AlphaEvolve stores programs with evaluation outputs, and
    benchmark-style tasks such as packing, scheduling, and kernels often need
    construction files, plots, traces, logs, or compiled artifacts to inspect
    and compare results.
  - Status: implemented as opt-in candidate-workspace artifact copy-out.
    `Config` now exposes `evaluator_artifact_include`,
    `evaluator_artifact_exclude`, `evaluator_artifact_max_files`, and
    `evaluator_artifact_max_bytes`, with per-stage overrides via
    `artifact_include`, `artifact_exclude`, `artifact_max_files`, and
    `artifact_max_bytes`. Matching files are copied to
    `runs/<run>/evaluator_artifacts/<collection_id>/...` before the temporary
    workspace is deleted. Evaluation metadata records effective patterns,
    limits, skipped files, copied file paths, byte counts, SHA-256 hashes,
    stage name, sample index, and attempt. Tests prove validator-created files
    are copied, bounded, hashed, retained after subprocess cleanup, and can use
    stage-specific artifact policy.
  - Remaining gap: artifact content is copied raw rather than redacted, files
    outside the candidate workspace are not collected, and richer artifact
    schemas remain future work.

- [x] Validate evaluator-stage numeric fields before running cascades.
  - Spec evidence: AlphaEvolve-style cascades are explicit experiment
    configuration; invalid stage budgets, sample counts, retry counts, and
    thresholds should fail before evaluation with reproducible diagnostics.
  - Current evidence: `Config.validate()` now rejects non-positive
    `eval_stages[].samples`, negative retries, non-positive timeouts,
    nonnumeric `min_score`, unsupported stage fields, non-list `seeds`, and
    explicit `samples`/`seeds` length mismatches. `evolve()` and the CLI call
    `config.validate()` before building the evaluator or archiving seeds.
  - Status: implemented with config tests proving bad stage configs fail at
    construction/startup rather than during candidate evaluation.

- [x] Validate evolution and population numeric config ranges.
  - Spec evidence: AlphaEvolve-style experiments depend on explicit,
    reproducible population and budget settings; invalid archive/sampling
    parameters should fail before the run mutates or evaluates programs.
  - Current evidence: `Config.validate()` now rejects negative
    `max_generations`, negative `num_inspirations`, non-positive
    `eval_timeout_sec`, `explore_ratio` outside `[0, 1]`, zero islands,
    negative migration intervals, `migration_ratio` outside `[0, 1]`,
    non-positive MAP-Elites bins, non-positive elite archive sizes, and
    negative ensemble exploration coefficients.
  - Status: implemented with top-level config range tests. Broader run-wide
    budget counters remain tracked separately.

- [x] Define zero-ratio migration semantics.
  - Spec evidence: AlphaEvolve-style population settings should have
    reproducible, unsurprising semantics; disabling or reducing migration is an
    experimental control.
  - Previous evidence: `Config.validate()` accepted `migration_ratio=0.0`, but
    `IslandModel.migrate()` computes `n = max(1, ceil(len(elites) *
    migration_ratio))`. A local proof with `migration_ratio=0.0` and migration
    enabled still copied one elite to the next island.
  - Status: implemented. `migration_ratio=0.0` now selects no migrants, while
    positive ratios still round up to at least one migrant when an island has
    elites. `migration_interval=0` remains the scheduled-migration disable
    switch.
  - Validation: island tests cover zero-ratio no-migrant behavior; existing
    migration tests cover positive ratios and scheduled migration intervals.

- [x] Preserve full evaluator feedback, not just scalar fitness.
  - Spec evidence: AlphaEvolve stores solutions with evaluation results,
    scores, and program outputs attached.
  - Current evidence: `ProgramDatabase.log()` writes raw metrics and structured
    evaluation results, including stage outcomes and process diagnostics.
  - Status: implemented in `EvaluationResult` and `history.jsonl` records.
  - Required result: persist raw metrics dicts, stage outcomes, stdout/stderr,
    error causes, elapsed time, and validator-provided feedback.

- [x] Add LLM-generated feedback as an optional evaluation signal.
  - Spec evidence: AlphaEvolve can grade hard-to-code properties, such as
    simplicity, using separate LLM calls and either add scores or discard
    solutions.
  - Current evidence: `Config.llm_feedback` runs optional LLM graders after
    local evaluation; `libreevolve/core/feedback.py` parses grader responses,
    logs backend provenance and raw responses, adds feedback metrics, composes
    weighted fitness, and supports discard rules.
  - Status: implemented as a synchronous optional feedback pass. Remaining
    limitations: no parallel reviewer workers, no calibrated grader ensemble,
    and no ablation harness.
  - Required result: add optional feedback graders with clear provenance,
    score-composition rules, and archive/log visibility.

- [x] Render full workspace context to LLM feedback graders.
  - Spec evidence: AlphaEvolve can evolve whole files/codebases and use LLM
    graders for properties that are difficult to encode locally; those graders
    must see the relevant candidate components to judge codebase-level
    properties.
  - Status: implemented. `_build_feedback_prompt()` renders `[WORKSPACE]`
    sections from deterministically sorted candidate files, marks the primary
    file, includes path headers and fenced content, applies basic secret
    redaction, enforces per-file and whole-workspace character budgets with
    truncation notices, and includes compact evaluator diagnostics under
    `[EVALUATION]`.
  - Evidence: `tests/core/test_feedback.py` covers non-primary file rendering,
    evaluator stdout visibility, secret redaction, and oversized-workspace
    truncation.

- [x] Isolate malformed or failing LLM feedback graders.
  - Spec evidence: AlphaEvolve treats LLM-generated feedback as an optional
    evaluation/scoring signal; grader failures should be diagnosable evaluation
    outcomes, not unstructured run crashes or silent misclassifications.
  - Current evidence: `apply_llm_feedback()` now catches provider exceptions,
    malformed response scores, non-finite response scores, and non-boolean
    discard values as `llm_feedback_failed` records under
    `evaluation.metadata.llm_feedback`; failed graders are ignored for
    score/validity composition. `Config.validate()` rejects invalid grader
    schema fields before startup.
  - Status: implemented with tests for backend errors, malformed response
    scores, string discard values, and non-finite response values. Richer
    configurable retry/penalty/discard policies remain future work.

- [ ] Add configurable LLM feedback failure policies.
  - Spec evidence: AlphaEvolve-style optional feedback should support explicit
    experiment policy for how failed reviewer/grader calls affect selection and
    diagnostics.
  - Current evidence: failed feedback graders are currently isolated with one
    hard-coded policy: record failure metadata and ignore the failed grader for
    score and validity. There is no config option for retry, penalize, discard,
    stop-run, or fallback-reviewer behavior.
  - Required result: add a feedback failure-policy config schema, implement
    retry/penalty/discard/ignore behavior as configured, record policy decisions
    in history, and test each policy.

- [ ] Calibrate LLM feedback scores against metric schema and fitness
  composition.
  - Spec evidence: AlphaEvolve treats evaluation outputs as scalar metrics and
    can add LLM-graded properties to the score dictionary; those scores should
    remain comparable and usable by database/prompt selection.
  - Current evidence: `apply_llm_feedback()` accepts undeclared grader metrics,
    converts `score` directly to `float`, and adds `weight * score` directly to
    normalized fitness without checking metric direction, bounds, finite range,
    or whether the grader score should be part of primary fitness.
  - Required result: define feedback metric schemas, normalize or bound grader
    outputs, preserve raw grader scores separately from composed fitness, and
    add tests for out-of-range, non-finite, minimizing, and discard-only
    feedback signals.

- [ ] Implement parallel/asynchronous evaluation.
  - Spec evidence: AlphaEvolve parallelizes evaluation, often distributing
    work across many randomized initializations or accelerators, and its
    pipeline is optimized for throughput.
  - Current evidence: `evolve()` is synchronous and handles one LLM call and
    one subprocess evaluation at a time (`libreevolve/core/loop.py:62-104`).
  - Required result: introduce an async controller, concurrent LLM samplers,
    evaluator workers, bounded queues, and deterministic run accounting.

- [ ] Support expensive evaluations and compute budgets.
  - Spec evidence: AlphaEvolve can spend hours or roughly 100 compute-hours on
    a single new solution when evaluation is parallelized.
  - Current evidence: `eval_timeout_sec` defaults to 60 seconds and one
    subprocess (`libreevolve/core/config.py`, `libreevolve/core/evaluator.py`).
  - Required result: add wall-clock, sample, accelerator, and per-stage budget
    controls, plus resumable evaluation state.

- [ ] Add run-wide compute budget accounting and stop criteria.
  - Spec evidence: AlphaEvolve Section 2.6 frames the system around maximizing
    useful ideas evaluated under an overall computation budget, and Section 4
    ablations report performance by fraction of the compute budget.
  - Current evidence: `Config` exposes `max_generations` and per-validator
    timeouts only. The loop has no wall-clock, LLM-call, token, cost,
    evaluator-second, sample, or retry budget; `manifest.json` does not record
    consumed budget; runs stop because the generation loop ends or no parent is
    available, without a structured stop reason.
  - Required result: add a budget schema, deterministic counters for LLM
    calls/tokens/cost/evaluator elapsed time/stage samples/retries, structured
    stop reasons, manifest/history budget summaries, and tests that budget
    exhaustion stops runs reproducibly.

## Metrics and Evolution Database

- [ ] Implement real multi-objective optimization.
  - Spec evidence: AlphaEvolve can optimize multiple user-provided scores and
    use diverse high-performing programs under different definitions of "good"
    in prompts.
  - Current evidence: evaluator/database/program records preserve metric
    vectors, and primary fitness honors direction/bounds. Archive comparisons,
    backend reward, and parent selection still collapse behavior to normalized
    primary fitness.
  - Required result: represent full metric vectors, choose target metrics,
    support Pareto/frontier or score-composition policies, and sample
    inspirations by metric-specific excellence.

- [x] Honor `metrics.yaml` direction and bounds for primary fitness and archive
  performance.
  - Spec evidence: AlphaEvolve's metrics are maximized by convention; the local
    problem format adds `direction` and `bounds`, so the implementation must
    either honor them or remove the claim.
  - Current evidence: `Problem.normalize_metric()` honors direction and bounds;
    evaluator fitness is normalized; `ProgramDatabase` and `IslandModel` pass
    normalized performance bounds into `MAPElites`.
  - Status: implemented via `Problem.normalize_metric()` and normalized archive
    performance cells for the primary metric; non-[0, 1] and minimize primary
    metrics have tests.
  - Required result: normalize metrics through declared bounds and directions,
    pass bounds into population archives, and test non-[0, 1] metrics.

- [ ] Honor metric direction/bounds for secondary metrics, feedback metrics,
  and future multi-objective policies.
  - Spec evidence: AlphaEvolve supports optimizing multiple scalar metrics,
    and all metrics used for selection, prompting, or feedback composition need
    consistent semantics.
  - Current evidence: secondary metrics are preserved raw in `Program.metrics`
    and `history.jsonl`; `apply_llm_feedback()` adds grader scores and
    `weight * score` directly to normalized fitness without checking declared
    bounds/directions or normalizing the feedback metric. The current archive
    policy ignores secondary metrics except as logged context.
  - Required result: validate every declared metric against schema, normalize
    metric vectors when they affect selection/prompting/archive policy,
    define feedback metric schemas, and test minimize/out-of-range/non-finite
    secondary and feedback metrics.

- [ ] Make MAP-Elites descriptors workspace-aware.
  - Spec evidence: AlphaEvolve can evolve whole files/codebases, and
    MAP-Elites-style quality-diversity search should map the candidate being
    evolved, not just a compatibility projection of one primary file.
  - Current evidence: `MAPElites._norm_complexity()` and `_diversity()` accept
    `code: str`; `_cell()` passes `Program.code`, which is the primary-file
    compatibility view. For multi-file candidates, helper modules, generated
    support files, and non-primary evolved components do not affect complexity
    or TF-IDF diversity cells, and `sample_diverse()` can treat candidates with
    very different workspaces as equivalent if their primary files match.
  - Required result: define workspace-level descriptor inputs, such as
    canonicalized file paths plus contents and evaluator-provided behavior
    descriptors; compute complexity/diversity over the full candidate or
    configured descriptor set; persist descriptor values; and add tests where
    non-primary file changes alter archive cells and inspiration sampling.

- [ ] Stabilize MAP-Elites descriptor normalization and rebinning semantics.
  - Spec evidence: MAP-Elites illuminates a behavior space whose dimensions
    are meaningful across the archive. Descriptor coordinates should be
    reproducible, comparable across runs, and not silently invalidated by later
    candidates.
  - Current evidence: `MAPElites._norm_complexity()` updates
    `self._max_complexity` while computing the candidate cell, so a later
    longer program changes the normalization denominator for future candidates
    without recomputing or moving programs already stored in `_grid`.
    `_diversity()` computes distance against the current capped elite list, so
    diversity coordinates also depend on current archive contents rather than
    a persisted descriptor model. `history.jsonl` records per-candidate
    descriptor values after admission, but the archive does not persist the
    normalization state or rebin cells when descriptor scales change.
  - Required result: define fixed descriptor bounds, evaluator-provided
    behavior descriptors, or an explicit dynamic-normalization/rebinning
    policy; persist descriptor normalization state in run artifacts; add tests
    proving that candidate insertion order either does not change existing
    cells or triggers a documented rebin/snapshot event.

- [ ] Replace the current thin JSONL facade with an evolutionary database
  capable of resurfacing ideas by score, metric, diversity, feedback, and
  lineage.
  - Spec evidence: AlphaEvolve's program database optimally resurfaces
    previously explored ideas and balances exploration and exploitation.
  - Current evidence: `ProgramDatabase` delegates to `IslandModel`, logs JSONL,
    and has no query/index layer beyond `sample`, `sample_diverse`, and `best`
    (`libreevolve/core/database.py:13-47`).
  - Required result: store rich candidate/evaluation records with queryable
    dimensions and reproducible sampling policies.

- [ ] Persist archive cell/island state and migration events.
  - Spec evidence: AlphaEvolve's program database is an active evolutionary
    state, not just a candidate log; resuming, auditing, and comparing runs
    requires knowing which programs occupied which archive cells and how
    migration changed island populations.
  - Current evidence: `ProgramDatabase.log()` writes candidate records to
    `history.jsonl`, but `MAPElites._grid`, `_elite`, `_max_complexity`,
    per-cell coordinates, diversity values, island assignment, and migration
    events are kept only in memory. `ProgramDatabase.maybe_migrate()` mutates
    islands without writing a history event, and `manifest.json` records only
    population configuration, not archive state.
  - Required result: persist archive snapshots or event logs containing island
    ids, MAP-Elites cell coordinates/descriptors, cell replacements, elite
    archive contents, migration source/destination/events, and normalization
    state; add tests that a run's archive state can be inspected and eventually
    resumed from persisted artifacts.

- [x] Persist archive admission outcomes per program.
  - Spec evidence: AlphaEvolve's database stores explored programs with scores
    and enough evolutionary state to resurface useful ideas; auditing a run
    should distinguish evaluated-but-rejected candidates from candidates that
    entered an archive cell or elite list.
  - Status: implemented. `MAPElites.add()` and `IslandModel.add()` return
    structured admission events, and `ProgramDatabase.admit()` records
    below-threshold rejection without mutating the archive. `evolve()` stores
    the event under `metadata.archive_admission` before writing
    `history.jsonl`.
  - Evidence: archive admission records include admitted/rejected status,
    threshold, island id, cell coordinates/descriptors, previous occupant id,
    cell replacement status, elite-list entry, and displaced elite ids. Tests
    cover below-threshold rejection, valid archive entry, lower-fitness
    nonreplacement, cell replacement, elite displacement, island assignment, and
    seed/child history records.

- [ ] Review and improve parent/inspiration sampling.
  - Spec evidence: AlphaEvolve samples parent programs and inspirations from a
    database using an evolutionary algorithm inspired by MAP-Elites and island
    populations.
  - Current evidence: exploit always picks global best; explore picks a random
    occupied cell; inspirations are random occupied cells
    (`libreevolve/population/islands.py:28-53`). Implemented improvement:
    `evolve()` passes the selected parent id as an inspiration exclusion,
    `sample_diverse()` accepts `exclude_ids`, and island-level inspiration pools
    deduplicate migrated copies by `Program.id`. Tests cover MAP-Elites
    exclusion, database forwarding, migrated duplicate collapse, and loop-level
    parent-as-inspiration avoidance.
  - Required result: add configurable sampling strategies, metric-aware
    inspiration choice, recency/novelty weighting, and tests for exploration
    pressure. Parent exclusion and duplicate-id filtering are implemented.

- [ ] Improve run inspection and archive diagnostics.
  - Spec evidence: AlphaEvolve's evolutionary database attaches scores and
    outputs to programs so explored ideas can be inspected and resurfaced.
  - Current evidence: `libreevolve show` now detects current histories with
    `metadata.archive_admission`, selects only archive-admitted records whose
    evaluation is valid, prints its selection mode, and prints selected metrics
    when present. It preserves a legacy highest-fitness fallback for old
    history fixtures that lack archive metadata. It still prints only the
    selected primary-file code and does not expose full file sets, stage
    failures, prompt lineage, archive cells, novelty/diversity signals,
    feedback records, or parent/child lineage.
  - Required result: extend `show` and/or machine-readable summaries with
    stage diagnostics, full-workspace pointers, lineage, prompt ids, archive
    diagnostics, and failure statistics; keep tests where an invalid or
    non-admitted high-fitness row is not reported as the archived best.

## Benchmarks and Problem Fixtures

- [ ] Harden AlphaEvolve-style benchmark validators against toy shortcuts.
  - Spec evidence: AlphaEvolve's matrix-multiplication work searches tensor
    decompositions, measures rank over target families and randomized seeds,
    and verifies exactness; its packing work reports concrete best
    constructions and compares progress under ablations.
  - Current evidence: `matrix_multiplication` is a 2x2 Python function example
    scored by counting AST `*` nodes across three deterministic cases, not a
    rank-decomposition search or operation-instrumented benchmark. The packing
    validator checks fixed-26 circle feasibility and sum of radii, but there is
    no benchmark runner that records best construction artifacts, target
    thresholds, repeated seeds, or equal-budget comparisons.
  - Required result: add stronger validators or clearly separate smoke examples
    from benchmark fixtures; include anti-gaming tests, expected artifact
    schemas, repeated-seed evaluation, target/SOTA baselines, and benchmark
    reports suitable for comparing AlphaEvolve-alignment features.

## LLM Ensemble

- [ ] Add a custom LLM backend registry or plugin interface.
  - Spec evidence: AlphaEvolve's task setup includes a choice of existing or
    custom LLMs, and the system is described as model-agnostic.
  - Current evidence: `build_llm()` in `libreevolve/llm/ensemble.py` hard-codes
    backend type strings for `anthropic`, `openai`, and `ollama`; adding a new
    provider requires editing source code and constructor-key allowlists rather
    than declaring a backend module/class in `config.yaml`.
  - Required result: add a backend registry or plugin loading mechanism with
    validated backend specs, constructor/config schemas, provenance in
    manifests, docs, and tests for a custom in-repo or problem-local backend.

- [ ] Separate backend accounting for mutation, critique, feedback, and
  meta-prompt calls.
  - Spec evidence: AlphaEvolve's LLM ensemble is used to generate candidates
    for an evolutionary loop optimized for throughput and quality; scheduler
    feedback should correspond to the role and outcome of each LLM call.
  - Current evidence: every `llm.generate()` increments `LLMEnsemble.counts`,
    including critique, LLM feedback, and meta-prompt mutation calls, but only
    the original mutation `backend_idx` receives `record_reward()`. Mutation
    candidates now log `metadata.backend_idx`, but auxiliary calls still affect
    routing state as apparent zero-reward pulls and the scheduler state is not
    persisted.
  - Required result: track call role/provenance, define reward or no-reward
    accounting per role, persist bandit state in run artifacts, and add tests
    proving critique/feedback/meta-prompt calls do not distort mutation routing.

- [ ] Persist normalized LLM call telemetry and provider response provenance.
  - Spec evidence: AlphaEvolve's scheduler and compute-budget framing depend on
    LLM throughput, cost, latency, and quality; reproducible experiments need
    per-call evidence for which model/API call produced which proposal or
    feedback.
  - Current evidence: `LLMBackend.generate()` returns only `str`, and
    `LLMEnsemble.generate()` returns `(response, backend_idx)`. OpenAI,
    Anthropic, and Ollama adapters discard provider response ids, usage/token
    counts, finish reasons, latency, retry counts, API mode, raw error metadata,
    and request parameters. `history.jsonl` stores `metadata.backend_idx` for
    mutation calls and limited feedback/critique metadata, but there is no
    normalized LLM call log or per-call telemetry attached to run artifacts.
  - Required result: introduce a call result/telemetry object, record role,
    backend spec, model, API mode, prompt size, output size, usage tokens,
    latency, retries, finish reason, request/response ids, raw-provider
    diagnostics, and failure metadata; persist it in history or a separate call
    log; update scheduler/budget accounting from this telemetry; add tests with
    fake provider usage for mutation, critique, feedback, and meta-prompt calls.

- [ ] Add LLM provider failure retry, fallback, and quarantine policy.
  - Spec evidence: AlphaEvolve runs an LLM/evaluator pipeline optimized for
    long-running throughput. Provider failures, rate limits, invalid responses,
    and transient transport errors need deterministic accounting and retry or
    fallback behavior so one failed call does not corrupt scheduler state or
    crash unrelated run progress.
  - Current evidence: `evolve()` calls `llm.generate()` for mutation, optional
    critique, optional feedback, and meta-prompt mutation with no try/except or
    retry policy. `LLMEnsemble.generate()` selects a backend, calls
    `self.backends[idx].generate(prompt)`, increments the global `total`
    counter before that provider call, and increments `counts[idx]` only after
    a successful return. Failed provider calls can therefore advance the UCB
    attempt counter without a matching backend count, structured failure
    record, or alternate-backend attempt. A mutation-call exception aborts the
    run before candidate/evaluation logging, while critique, feedback, or
    meta-prompt exceptions can abort after useful work has already completed.
  - Required result: define per-role LLM failure policy with bounded retries,
    timeout/rate-limit classification, optional backend fallback, scheduler
    accounting for failed attempts, structured call/error logs, candidate-level
    quarantine where appropriate, and tests for mutation, critique, feedback,
    and meta-prompt provider failures.

- [ ] Make OpenAI API routing explicit and validate reasoning-model options.
  - Spec evidence: AlphaEvolve's task setup includes LLM choices and
    configurations; backend behavior must be reproducible and match configured
    model capabilities.
  - Current evidence: `OpenAIBackend.generate()` selects Chat Completions unless
    `reasoning_effort` is set, and selects Responses only when that field is
    non-empty. Documentation previously implied reasoning models use Responses
    broadly, but the adapter does not detect reasoning-capable model names,
    validate supported reasoning values, choose `store`/statefulness policy, or
    persist API-mode provenance per call.
  - Required result: add an explicit `api_mode` or model-capability policy,
    validate OpenAI model/parameter combinations before a run, record API mode
    in call metadata/manifests, and test Chat Completions vs Responses routing.

- [x] Model AlphaEvolve's throughput/depth ensemble strategy explicitly.
  - Spec evidence: AlphaEvolve combines Gemini Flash for breadth with Gemini
    Pro for occasional deeper, higher-quality suggestions.
  - Current evidence: `LLMEnsemble` supports default `ucb1` and experimental
    `throughput_depth` scheduling metadata (`cost`, `latency`, `depth`, `role`).
    The policy is still heuristic and not a faithful reproduction of the
    AlphaEvolve production scheduler.
  - Status: implemented as an experimental `throughput_depth` ensemble strategy
    using backend `cost`, `latency`, and `depth` metadata. This remains a
    heuristic, not a reproduction of AlphaEvolve's production scheduler.
  - Required result: add scheduling modes that can allocate proposal volume by
    cost/latency/capability, not only reward.

- [ ] Make backend role metadata operational or document it as descriptive.
  - Spec evidence: AlphaEvolve's LLM ensemble separates breadth-oriented fast
    generation from deeper higher-quality suggestions. If local backend specs
    expose roles such as `breadth` and `depth`, those roles should influence
    scheduling or be clearly marked as labels.
  - Current evidence: `Config._validate_backends()` accepts a string `role`,
    `build_llm()` stores it in `backend_metadata`, and docs show `role:
    breadth` / `role: depth` examples. `LLMEnsemble._throughput_depth_select()`
    reads only `cost`, `latency`, and `depth`; it ignores `role`, and the
    default `ucb1` strategy ignores all backend metadata. There is no policy
    that reserves proposal volume for breadth models, escalates selected
    candidates to depth models, or routes critique/feedback/meta-prompt calls
    by role.
  - Required result: either make `role` operational through explicit per-role
    scheduling quotas/routing rules and tests, or document it as descriptive
    manifest metadata only; add tests proving the chosen role semantics.

- [x] Add critique/review generation stage.
  - Spec evidence: the AlphaEvolve paper describes using LLMs to generate,
    critique, and evolve a pool of algorithms.
  - Current evidence: `Config.critique_enabled` triggers an optional LLM
    critique/revision call before mutation application; the loop logs the
    original diff, revised diff, critique prompt, and backend index in
    candidate metadata.
  - Status: implemented as an optional synchronous self-revision pass. It is
    not yet a pool of independent critics or async reviewers.
  - Required result: support optional critique, self-revision, or reviewer
    passes before evaluation.

- [x] Validate critique revisions before replacing the original mutation.
  - Spec evidence: critique should improve candidate quality, not silently
    discard an otherwise applicable generated mutation.
  - Previous gap: `evolve()` replaced the generated mutation with the critique
    response unconditionally, so a malformed critique response could turn a
    valid mutation into `no_diff_blocks` or another parser error.
  - Status: implemented. The loop previews the revised mutation with
    `apply_workspace_mutation()`, falls back to the original mutation when the
    revision is malformed and the original applies cleanly, and records
    `selected_diff`, `accepted_revision`, parser diagnostics, and fallback
    reason in `metadata.critique`.
  - Validation: `tests/core/test_loop.py` covers accepted critique revisions
    and malformed critique fallback.

- [ ] Extend critique from single self-revision to configurable reviewer pools.
  - Spec evidence: AlphaEvolve describes using a set of LLMs to generate,
    critique, and evolve a pool of algorithms, and its system is optimized for
    throughput with separate LLM samplers/evaluators.
  - Current evidence: `evolve()` can make one synchronous critique call after
    the mutation response. There is no reviewer pool, no independent critique
    selection policy, no agreement/disagreement logging, no critique score, and
    no async overlap with generation or evaluation.
  - Required result: add configurable reviewer roles/backends, provenance,
    score or accept/reject/revise policies, prompt/log visibility, and tests
    that critique behavior does not corrupt mutation backend accounting.

## Runtime, Reproducibility, and Safety

- [ ] Validate configuration schema and backend specs instead of silently
  ignoring mistakes.
  - Spec evidence: AlphaEvolve task setup includes prompt templates,
    configurations, LLM choices, and evaluator settings; reproducible runs need
    configuration mistakes to fail early with clear diagnostics.
  - Current evidence: `_build_config()` now rejects unknown `config.yaml` keys,
    empty CLI backend models fail backend-spec validation, config-file
    `mutation_mode` and `ensemble_strategy` are enum-validated, backend specs
    are checked for supported keys/types/models/metadata, and evaluator-stage
    numeric fields and LLM feedback grader specs are validated before a run
    starts. Remaining gaps: malformed YAML and non-mapping top-level
    `config.yaml` files can still raise raw `yaml`/`dict.update()` exceptions
    before `ConfigError`, plugin-specific configuration schemas do not exist,
    and model/API capability validation is not implemented. CLI
    `--reasoning-effort` now applies to OpenAI backends loaded from
    `config.yaml` or `--backends`, and is ignored for non-OpenAI backends.
  - Required result: add plugin config schemas, document or fix remaining CLI
    override semantics, add model/API-mode compatibility validation where
    feasible, normalize config-file parse/type failures into path-aware startup
    diagnostics, and test malformed top-level and nested config cases beyond
    backend/stage/feedback metadata.

- [ ] Fix CLI/config override semantics and document precedence with tests.
  - Spec evidence: AlphaEvolve-style task setup depends on explicit,
    reproducible configuration for LLM choices, prompt behavior, evaluator
    settings, and run metadata.
  - Current evidence: `_build_config()` loads `problem_name` from
    `config.yaml`, then unconditionally overwrites it with `problem.name`;
    only `--run-name` changes the output directory.
  - Partial status: OpenAI reasoning options now override consistently for
    both config-file and CLI-specified OpenAI backends, do not attach to
    non-OpenAI backends, and are covered by CLI tests.
  - Required result: define and test remaining field-by-field precedence for
    defaults, config files, and CLI options; make ignored overrides explicit;
    and reflect effective values in `manifest.json`.

- [ ] Add resumable runs.
  - Spec evidence: AlphaEvolve is a long-running autonomous pipeline optimized
    for large computation budgets.
  - Current evidence: runs append to `history.jsonl`, but `evolve()` always
    starts from seeds and does not resume archive/controller state.
  - Required result: persist and reload population/database state, backend bandit
    state, prompt database state, and pending evaluations.

- [x] Define run-directory collision and append semantics.
  - Spec evidence: AlphaEvolve-style experiments need reproducible run identity,
    clean provenance, and intentional resume behavior for long-running runs.
  - Status: implemented. `Config` now has a UUID4 `run_id` and explicit
    `run_collision_policy` with validated `fail` and `overwrite` modes. CLI
    startup and `ProgramDatabase` both preflight known run artifacts; the
    default fails before appending to `history.jsonl`/`prompt_history.jsonl` or
    rewriting `manifest.json`, while `--overwrite` /
    `run_collision_policy: overwrite` removes only known run artifacts
    (`history*.jsonl`, `failure_history*.jsonl`, `prompt_history*.jsonl`,
    `manifest.json`, `best.py`, and `best_workspace/`) before the new run.
    `manifest.json` records `run_id` and the effective collision policy.
  - Verified by: `tests/test_cli.py`, `tests/population/test_database.py`, and
    `tests/core/test_config.py` cover CLI preflight, overwrite cleanup,
    manifest metadata, and config validation.
  - Remaining divergence: true resume, parent-run relationships, deterministic
    lineage ids, archive/controller reload, and evaluator-code provenance are
    tracked separately.

- [ ] Make seeded replay and persisted lineage identifiers reproducible.
  - Spec evidence: AlphaEvolve compares systems over long computation budgets,
    ablations, and repeated seeds, so local stochastic choices and persisted
    lineage records must be reproducible enough to replay or diff experiments.
  - Current evidence: `evolve()` seeds Python's global `random` module and
    constructs `PromptSampler` with `random.Random(config.seed)`, but
    `evolve()` always passes `template=prompt_program.template`, so the
    sampler's seeded variant RNG is bypassed for configured variants.
    `PromptDatabase` seeds templates as `PromptProgram`s with UUID4 ids and
    selects untried programs by sorting those ids, so initial prompt-variant
    order can differ across repeated runs. `Program.id` and `PromptProgram.id`
    are also generated with `uuid4()`. The history and `prompt_history.jsonl`
    lineage ids therefore differ across repeated runs even when local sampling
    choices and fake LLM responses are otherwise deterministic. Provider/model
    nondeterminism is also not recorded as part of a replay contract.
  - Required result: define deterministic run/candidate/prompt id policy for
    seeded local replay and a deterministic prompt-variant order policy
    (config-order, seeded shuffle, or bandit initialization), or explicitly
    mark UUID-based identity and UUID-ordered variants as non-replayable;
    persist RNG state and provider nondeterminism boundaries where needed; add
    tests that repeated deterministic runs produce stable lineage ids, prompt
    ids, prompt variant sequence, archive sampling, and manifest replay
    metadata.

- [x] Add structured run metadata.
  - Spec evidence: AlphaEvolve experiments depend on prompt templates, LLM
    choices, evaluator stages, compute budgets, and configurations.
  - Current evidence: `manifest.json` records effective local config and
    backend roster. It does not yet include code version, problem hash, plugin
    specs, artifact hashes, or resumable controller state.
  - Status: `manifest.json` now records effective local config and backend
    settings. Code version/problem hash/plugin specs are still future
    hardening.
  - Required result: write a manifest with effective config, code version,
    problem hash, evaluator stages, backend specs, plugin specs, seed, and
    budget.

- [ ] Refresh committed example runs to the current artifact schema.
  - Spec evidence: AlphaEvolve-style result inspection should make evaluated
    programs, prompts, manifests, and best artifacts reproducible from saved
    run outputs.
  - Current evidence: current CLI runs write `manifest.json`,
    `prompt_history.jsonl`, `failure_history.jsonl` when failures occur,
    `best.py`, and `best_workspace/`, but the committed
    `examples/runs/hello_world_ensemble` and `examples/runs/sorting_ttt_rl`
    fixtures contain only `history.jsonl` and `best.py`. They cannot exercise
    current manifest, prompt-history, failure-history, or full-workspace
    artifact inspection.
  - Required result: regenerate or migrate curated examples with the current
    artifact layout, or keep them explicitly labeled as legacy history-only
    fixtures; add smoke/tests that example artifacts match the documented run
    contract.

- [ ] Add code/problem/plugin hashes and artifact hashes to the run manifest.
  - Spec evidence: AlphaEvolve experiments depend on prompt templates, LLM
    choices, evaluator code, problem context, and compute budget; reproducing a
    run requires identifying the exact code/problem state.
  - Current evidence: `ProgramDatabase._write_manifest()` records effective
    config values, but not the Git commit, dirty-worktree state, problem file
    hashes, validator hash, context hashes, plugin implementation/spec hashes,
    or emitted artifact hashes.
  - Required result: include reproducibility hashes/version metadata in
    `manifest.json`, document which files are covered, and add tests that a
    changed problem file changes the manifest hash.

- [ ] Add a plugin registry, configuration schema, and plugin provenance.
  - Spec evidence: AlphaEvolve-style task setup depends on explicit
    configuration and reproducible extension behavior; paper-inspired plugins
    should be clearly scoped and configurable without source edits.
  - Current evidence: `_load_plugins()` hard-codes four CLI aliases and creates
    plugins with default constructors. Problem-local `config.yaml` can list
    names only; it cannot pass plugin options such as search cadence, output
    path, prompt text, or provider function. Run manifests store plugin names
    but not plugin versions, constructor parameters, paper-inspiration scope, or
    emitted plugin artifacts.
  - Required result: add a plugin registry or entry-point interface, validate
    per-plugin config schemas, record plugin specs/provenance/artifacts in
    manifests, and test configured plugin behavior without editing the CLI.

- [x] Persist plugin score-composition provenance.
  - Spec evidence: AlphaEvolve stores programs with evaluation scores and
    outputs attached; when local extension hooks change fitness, the database
    must preserve how the final selection score was produced.
  - Status: implemented. `evolve()` records `metadata.score_composition` with
    evaluator fitness, optional feedback-adjusted fitness, initial/final
    top-level fitness, per-plugin before/after/delta values, metric additions
    and changes, invalid plugin-score rejections, and divergence from raw
    evaluator fitness.
  - Evidence: tests cover multiple plugins, metric additions, non-finite plugin
    scores being rejected, final score preservation, and raw
    `evaluation.fitness` remaining visible.

- [x] Keep evaluator validity separate from plugin-adjusted fitness.
  - Spec evidence: AlphaEvolve's program database is populated by evaluated
    solutions whose quality and validity are determined by user-provided
    evaluators. Extensions may add scoring signals, but they should not
    accidentally override evaluator invalidity without an explicit policy.
  - Status: implemented. Archive admission checks `evaluation.is_valid` before
    threshold/cell insertion and records `reason=invalid_evaluation` with
    `evaluation_is_valid=false` when a plugin raises an invalid candidate above
    `VALID_THRESHOLD`.
  - Evidence: tests cover a plugin boosting an invalid candidate, a plugin
    penalizing a valid candidate below threshold, non-finite plugin scores, and
    validity-aware archive admission records.

- [ ] Define plugin training-data reward and artifact semantics.
  - Spec evidence: AlphaEvolve-style and ThetaEvolve-style experiments require
    reproducible training/evaluation artifacts with clear reward definitions;
    reward shaping should be explicit, not an implicit side effect.
  - Current evidence: `TTTRLPlugin.on_evaluated()` writes only prompt/diff
    pairs and stores `reward = max(0.0, score)`, clipping negative scores to
    zero without a documented reward-shaping policy. `_maybe_train()` appends
    batches to `runs/grpo_data.jsonl` by default, outside the active
    per-problem run directory, and `manifest.json` does not link or hash that
    emitted dataset.
  - Required result: define raw-score vs shaped-reward export fields, document
    clipping/penalty behavior, scope plugin datasets under run artifacts or
    record global artifact provenance, include hashes/counts in manifests, and
    add tests for negative scores, repeated flushes, run scoping, and resume
    behavior.

- [ ] Improve isolation beyond a temporary Python subprocess.
  - Spec evidence: AlphaEvolve targets existing codebases and systems code,
    potentially with expensive or hardware-backed execution.
  - Current evidence: validator subprocesses run with the current Python
    interpreter and local filesystem access (`libreevolve/core/evaluator.py`).
  - Required result: add configurable sandbox/container/working-directory
    isolation, resource limits, and artifact collection.

- [x] Clean up validator process trees on timeout.
  - Spec evidence: AlphaEvolve-style automated evaluation needs bounded,
    reproducible execution. A timeout should terminate not only the immediate
    validator runner but also subprocesses spawned by validator code.
  - Status: implemented for evaluator timeouts. `CascadeEvaluator` now launches
    validators as a killable process tree (`taskkill /T /F` on Windows and
    process-group `SIGKILL` on POSIX), returns redacted stdout/stderr on
    timeout where available, and records `timeout_cleanup` metadata. Tests
    prove a validator-spawned delayed child cannot outlive the evaluation
    timeout and write a marker after timeout.
  - Remaining gap: this is not a container, network sandbox, memory/CPU limit,
    or general cleanup policy for successful validators that intentionally
    leave detached work behind.

- [ ] Isolate validator environment, secrets, and network access.
  - Spec evidence: AlphaEvolve evaluates generated code at scale, so evaluator
    execution boundaries must be explicit and reproducible. Generated or
    user-supplied validators should not implicitly inherit unrelated host
    secrets or network capability when runs load provider credentials.
  - Partial status: validator subprocesses now receive an explicit minimal
    environment instead of inheriting the parent process environment. Optional
    `validator_env_allowlist` names can opt variables into validators, metadata
    records provided keys and allowlist names without values, and persisted
    stdout/stderr is passed through basic secret-pattern redaction. Tests prove
    `OPENAI_API_KEY` is hidden by default and that explicit opt-in variables
    are visible.
  - Remaining gap: there is still no network egress policy, container sandbox,
    or stronger resource isolation for validator code.
  - Required result: define and enforce validator network expectations and
    sandbox/resource policy, with tests proving the intended boundary.

- [ ] Validate and constrain configured evaluator paths.
  - Spec evidence: AlphaEvolve task setup depends on explicit evaluator
    definitions and reproducible provenance for evaluation code.
  - Partial status: `_resolve_validate_path()` now requires stage validators to
    resolve to problem-local `.py` files before execution. Missing paths,
    directories, non-Python files, relative/absolute outside-root paths, and
    symlinks that resolve outside the problem directory are rejected. Absolute
    paths are allowed only when they resolve inside the problem directory.
    `manifest.json` now records direct evaluator entrypoints with resolved
    path, problem-relative path, SHA-256 hash, byte count, source type, and
    configured stage usage metadata. Tests cover default and configured-stage
    hash stability plus loop/database manifest wiring.
  - Remaining gap: transitive evaluator helper/data provenance, package-style
    validator entrypoints, and relative evaluator data policy are not defined
    or hashed in `manifest.json`.
  - Required result: define evaluator helper/data provenance and add tests for
    helper/data hash stability and package-style evaluator semantics.

- [x] Remove wording that implies the validator subprocess is a security
  sandbox.
  - Spec evidence: AlphaEvolve evaluates generated code, so local docs must be
    precise about execution safety boundaries.
  - Current evidence: README and evaluator comments referred to an "isolated"
    subprocess even though validators execute under the current interpreter
    with local filesystem access and only temporary workspace/process
    separation.
  - Status: README, AGENTS.md, and evaluator comments now call this a temporary
    local subprocess/process separation, while the sandbox/resource-limit work
    remains open above.
  - Required result: avoid using "isolated" or "sandboxed" for the current
    evaluator until real sandbox/resource controls exist.
