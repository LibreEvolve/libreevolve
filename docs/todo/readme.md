# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

- [x] Correct "Gemini only" in the AlphaEvolve column.
  - README evidence: `README.md:66` says AlphaEvolve uses "Gemini only."
  - Spec evidence: the AlphaEvolve paper says it is model-agnostic and shows a
    "Choice of existing or custom LLMs" in the task setup, while the published
    experiments use Gemini 2.0 Flash and Gemini 2.0 Pro.
  - Required result: change this to a precise statement such as "published
    experiments use Gemini Flash/Pro; system is described as model-agnostic."

- [x] Correct "Extensibility: None" for AlphaEvolve.
  - README evidence: `README.md:70` says AlphaEvolve has no extensibility.
  - Spec evidence: AlphaEvolve supports user-provided evaluation code,
    configurations, custom/existing LLMs, prompt customization, explicit
    context, stochastic formatting, and evolve-block markers.
  - Required result: compare the real extension surfaces rather than claiming
    AlphaEvolve has none.

- [x] Qualify "Population model: Proprietary database."
  - README evidence: `README.md:67` contrasts AlphaEvolve's proprietary
    database with LibreEvolve's MAP-Elites and islands.
  - Spec evidence: the paper states AlphaEvolve's database is inspired by
    MAP-Elites and island-based population models.
  - Required result: say AlphaEvolve has a closed evolutionary database inspired
    by MAP-Elites/island models, while LibreEvolve has a small local
    MAP-Elites/island implementation.

- [x] Qualify "Evaluation: Internal infrastructure" versus "Cascade evaluator."
  - README evidence: `README.md:69`.
  - Spec evidence: AlphaEvolve supports user-defined evaluation functions,
    optional evaluation cascades, LLM-generated feedback, and parallelized
    evaluation.
  - Required result: avoid implying LibreEvolve has equivalent cascade behavior;
    call out that LibreEvolve has a fixed three-step local subprocess cascade.

## Research References and Bundled Papers

- [x] Fix the references count.
  - README evidence: badges and text claim 23 references
    (`README.md:15`, `README.md:72`, `README.md:356`, `README.md:360`).
  - Current evidence: `papers/download_manifest.csv` has 24 downloaded entries
    excluding the header.
  - Required result: decide whether the source of truth is 24 local papers or a
    curated 23-paper list, then update badges/text/manifest accordingly.

- [x] Remove or revise "does not bundle them."
  - README evidence: `README.md:360` says the repository "does not bundle" the
    cited papers.
  - Current evidence: the checkout has a `papers/` directory with downloaded
    PDFs and a manifest.
  - Required result: either stop bundling PDFs or document that the repo
    includes a local paper cache/manifest.

- [x] Expand the research table or explain why most downloaded papers are not
  listed.
  - README evidence: `README.md:364-380` lists 10 named references.
  - Current evidence: `papers/download_manifest.csv` lists 24 downloads,
    including domain result papers and benchmark/problem papers.
  - Required result: include all referenced local papers, split them into
    "system", "benchmarks/results", and "foundational" groups, or state that
    the README table is intentionally partial.

## Feature Claims

- [x] Replace "parallel populations" wording for islands.
  - README evidence: `README.md` described 5-island migration as "Parallel
    populations."
  - Current evidence: `IslandModel` keeps multiple MAP-Elites archives but runs
    synchronously in-process; no population worker concurrency exists.
  - Status: README now says "synchronous island archives" instead of implying
    parallel execution.
  - Required result: avoid using "parallel" for islands until there are actual
    concurrent island workers.

- [x] Soften UCB1/backend-routing claims.
  - README evidence: README called the ensemble "UCB1" and said it
    "automatically learns which model produces the best mutations."
  - Current evidence: `LLMEnsemble` is a UCB-style heuristic over unnormalized
    fitness improvements, with known canonical-UCB gaps tracked in
    `docs/todo/papers.md`.
  - Status: README now uses "UCB-style" in the feature list, workflow text, and
    AlphaEvolve comparison, and describes routing as tracking observed fitness
    improvements.
  - Required result: keep marketing text aligned with the heuristic
    implementation unless canonical UCB1 is implemented and tested.

- [x] Clarify LLM provider failure handling is not production-grade.
  - README evidence: README described OpenAI/Anthropic/Ollama support and
    backend routing, but did not warn that provider call failures are not
    retried, routed to fallback models, or recorded as structured failed
    attempts.
  - Current evidence: `LLMEnsemble.generate()` calls the selected backend
    directly and only increments counts on success; `evolve()` does not isolate
    mutation, critique, feedback, or meta-prompt provider exceptions.
  - Required result: warn readers that backend failure retry/fallback and
    failed-call telemetry remain open.

- [x] Correct the AlphaEvolve local-model comparison row.
  - README evidence: the comparison table said AlphaEvolve local models:
    "No."
  - Spec evidence: the paper describes published experiments with Gemini
    Flash/Pro and a choice of existing/custom LLMs, but does not make a broad
    claim about local model support.
  - Status: README now says local model use is not discussed in the paper,
    while published experiments use hosted Gemini models.
  - Required result: avoid inventing a negative AlphaEvolve capability claim
    when the paper only omits or does not discuss it.

- [x] Qualify "Feed it a problem, a seed program, and any LLM."
  - README evidence: `README.md:22`.
  - Current evidence: supported backend types are hard-coded to OpenAI,
    Anthropic, and Ollama in `build_llm()`.
  - Required result: say "any configured OpenAI/Anthropic/Ollama-compatible
    backend currently supported" or add a backend plugin interface.

- [x] Qualify the plugin names as inspired approximations, not implementations
  of the cited systems.
  - README evidence: `README.md:298-302` names CausalEvolve, DeepEvolve,
    ImprovEvolve, and ThetaEvolve as built-in plugins.
  - Current evidence: plugins are lightweight heuristics/stubs:
    CausalEvolve is regex/UCB1 factor guidance, DeepEvolve is arXiv Atom search,
    ImprovEvolve is a static prompt block, and ThetaEvolve writes JSONL without
    training.
  - Required result: use names such as "CausalEvolve-inspired" and document
    what is missing from each paper.

- [x] Qualify "comprehensive test coverage."
  - README evidence: `README.md:59` claims comprehensive coverage across all
    components.
  - Current evidence: the local non-integration suite now has 168 selected
    tests, but major AlphaEvolve features are still absent or represented only
    as narrow prototype behavior.
  - Required result: keep the count but change the coverage claim to the
    current prototype surface.

- [x] Correct test commands for this machine.
  - README evidence: `README.md:327-331` uses `pytest`.
  - Project instructions: `AGENTS.md` says to use `py -3.12 -m pytest`.
  - Current evidence: tests run successfully after installing dev extras, and
    documentation now uses `py -3.12 -m pytest`.
  - Required result: document installation first and use `py -3.12 -m pytest`.

- [x] Qualify model names as examples, not guaranteed current model IDs.
  - README evidence: `README.md:31`, `README.md:51`, `README.md:99-105`,
    `README.md:212-214`.
  - Current evidence: the code forwards model strings to vendor SDKs and does
    not validate availability.
  - Required result: say model names are examples and add validation or docs for
    provider-specific availability.

- [x] Clarify OpenAI Responses API routing.
  - README evidence: README and architecture comments implied OpenAI reasoning
    models use Responses API broadly.
  - Current evidence: `OpenAIBackend.generate()` uses Responses only when
    `reasoning_effort` is set; otherwise it uses Chat Completions for whatever
    model string is configured.
  - Required result: state that Responses is selected by the current
    `reasoning_effort` configuration path and track model/API-mode validation
    as code work.

## Architecture Description

- [x] Correct prompt-evolution placeholder guarantee wording.
  - README-adjacent evidence: architecture/configuration docs described
    meta-prompt mutation as preserving placeholders.
  - Current evidence: `evolve()` asks the LLM to keep placeholders but
    `PromptDatabase.mutate()` accepts arbitrary template text without
    validation.
  - Status: architecture/configuration docs now state that placeholder
    preservation is instructed but not enforced.
  - Required result: avoid implying prompt mutation is validated until the
    placeholder-validation todo is implemented.

- [x] Add missing AlphaEvolve gap callouts to the README architecture section.
  - README evidence: `README.md:225-254` presents the package architecture.
  - Missing from README: evolve-block markers, prompt sampler, multi-objective
    metrics, evaluator result objects, async controller/workers, meta-prompt
    database, full-code mutation mode, and language/workspace runners.
  - Required result: add an "AlphaEvolve fidelity gaps" subsection or link to
    `docs/todo/code.md`.

- [x] Clarify that the current problem format is Python-only and local-workspace.
  - README evidence: `README.md:258-285` describes `validate.py`, seed files,
    and optional seed workspaces.
  - AlphaEvolve contrast: AlphaEvolve evolves marked regions inside an existing
    codebase and can evaluate complex workflows.
  - Required result: explicitly state current Python/local-workspace scope and
    remaining arbitrary-language/build-system limitations.

- [x] Rework the "Comparison to AlphaEvolve" section so it does not overstate
  LibreEvolve as a feature superset.
  - README evidence: `README.md:61-72`.
  - Required result: present LibreEvolve as an open prototype with several
    deliberate divergences and many missing AlphaEvolve features.

- [x] Replace "isolated subprocess" wording for validators.
  - README evidence: the problem-format section said validators run in an
    isolated subprocess.
  - Current evidence: `CascadeEvaluator` executes validators in a temporary
    subprocess using the current Python interpreter and local filesystem
    access; this is process separation, not sandbox isolation.
  - Required result: call it a temporary local subprocess in README/AGENTS
    guidance and keep real sandbox/resource-limit work in `docs/todo/code.md`.

- [x] Clarify validator subprocesses inherit environment until hardened.
  - README evidence: README says validators run in a temporary local
    subprocess but did not mention that the subprocess inherits the parent
    environment, including `.env`-loaded provider variables.
  - Current evidence: CLI import loads `.env` with `override=True`, and
    `CascadeEvaluator._run_subprocess()` does not pass an explicit `env` to
    `subprocess.run()`.
  - Required result: warn users that validator environment/secret isolation is
    not implemented and point the implementation gap to the TODOs.

- [x] Soften the UCB1 paper-table role.
  - README evidence: the references table described UCB1 as "Multi-armed bandit
    selection."
  - Current evidence: `LLMEnsemble` is a heuristic UCB-style router over
    unbounded fitness deltas, and canonical reward-normalization work remains
    open in `docs/todo/papers.md`.
  - Required result: describe UCB1 as inspiration for backend routing, not as a
    fully canonical implementation.

- [x] Soften the failure-history feature claim.
  - README evidence: the feature table claimed the last five failed mutations
    are shown in prompts, and the workflow section said failed mutations are
    tracked and shown in later prompts.
  - Current evidence: `evolve()` keeps only in-memory failure hints and skips
    malformed/no-op/search-miss diffs when no changed child code is produced.
    For workspace candidates, invalid non-primary-file changes can also be
    omitted because the check compares `child_workspace.code` to `parent.code`.
  - Required result: describe the current feature as recent failure hints and
    point persistent/queryable full-workspace failed-proposal memory to the
    code TODO.

- [x] Fix stale example-run command style.
  - README-adjacent evidence: `examples/runs/README.md` used `python -m`
    commands while repository instructions and the main README use `py -3.12`.
  - Current evidence: this Windows workspace uses `py -3.12` for tests and CLI
    examples.
  - Required result: use `py -3.12 -m libreevolve show ...` in curated example
    run docs.

- [x] Correct stale README example-run snippets.
  - README evidence: the greeting example claimed `.format()` and string
    concatenation variants with score `1.00`, and the sorting example claimed a
    valid `lst.sort()` candidate at generation 0 plus early `sorted`/copy
    variants.
  - Current evidence: `examples/runs/hello_world_ensemble/history.jsonl`
    contains the solved generation 0 greeting plus rejected variants, but not
    the `.format()` or concatenation examples. `examples/runs/sorting_ttt_rl`
    has a malformed `lst.sort()` edit at generation 0, valid `lst.sort()` at
    generation 1, and later valid `sorted`/copy variants.
  - Required result: align README snippets with the checked-in JSONL histories
    or explicitly mark them as illustrative rather than curated-output
    excerpts.

- [x] Refresh README/AGENTS example directory lists.
  - README evidence: the package tree listed example problems but omitted
    `workspace_math`.
  - Current evidence: `libreevolve/problems/examples/` contains
    `hello_world`, `sorting`, `circle_packing`, `matrix_multiplication`, and
    `workspace_math`.
  - Required result: list the full current example set when documenting the
    repository layout.

- [x] Clarify multi-file mutation path limitations.
  - README evidence: the custom-problem section describes optional multi-file
    seed workspaces but did not mention that `<<<FILE ... >>>FILE` parsing is
    narrower than ordinary repository path handling.
  - Current evidence: `_FILE_SECTION_PATTERN` recognizes only a small path
    character set and can miss hyphenated or spaced filenames even though the
    workspace path normalizer can handle broader safe relative paths.
  - Required result: warn readers to keep current file-section paths simple and
    track parser hardening in the code TODO.

- [x] Clarify malformed mutation envelopes can be ignored.
  - README evidence: the custom-problem section describes file-section edits,
    but did not explain that unmatched or malformed envelope spans are not
    diagnosed as a whole response.
  - Current evidence: `_parse_file_sections()` and multi-block full replacement
    use regex `findall()` calls. A response with one valid file/block section
    and one unsupported or malformed envelope can apply the valid section while
    ignoring the unmatched intended edit.
  - Required result: warn readers that current multi-file/block mutation
    parsing is partial and track full-envelope diagnostics in the code TODO.

- [x] Clarify multi-file mutations cannot delete or rename files yet.
  - README evidence: the custom-problem section describes multi-file seed
    workspaces and file-section edits, but did not state that workspace
    topology changes are not expressible.
  - Current evidence: `apply_workspace_mutation()` only updates a file's text
    or creates an unknown file in `full` mode; no delete, rename, move, or
    primary-file change syntax exists.
  - Required result: warn readers that current multi-file mutation supports
    edits and limited file creation, not full repository topology evolution.

- [x] Clarify plugin score provenance limitations.
  - README evidence: the plugin hook table says `on_evaluated()` can modify
    score, but did not say that per-plugin score-composition provenance is not
    yet persisted.
  - Current evidence: `evolve()` applies plugin score returns sequentially and
    stores the final `Program.fitness`; no structured before/after plugin score
    chain is written to `history.jsonl`.
  - Required result: tell readers that plugin score hooks can affect archived
    fitness and point structured provenance to the roadmap/TODO.

- [x] Clarify causal plugin mutation-format limitations.
  - README evidence: the plugin section labels the causal plugin as
    CausalEvolve-inspired, but did not state that its factor detector is not
    using the same canonical diff parser as candidate mutation application.
  - Current evidence: `CausalPlugin._detect_factors()` parses only the compact
    local `DIFF_PATTERN`; canonical AlphaEvolve SEARCH/REPLACE fences can
    produce no factor matches and fall back to random guidance.
  - Required result: document that causal guidance is compact-diff-only until
    plugin mutation analysis is unified with the core parser.

- [x] Clarify ThetaEvolve export reward and artifact limitations.
  - README evidence: the plugin section says the ThetaEvolve-inspired plugin
    exports GRPO-style training data, but does not describe reward clipping,
    global output path, or missing manifest linkage.
  - Current evidence: `TTTRLPlugin.on_evaluated()` stores
    `reward = max(0.0, score)` and `_maybe_train()` appends to
    `runs/grpo_data.jsonl` by default. That dataset is not nested under the
    active run directory and is not hashed or linked from `manifest.json`.
  - Required result: document that the export is a simple clipped-reward JSONL
    side file until run-scoped dataset provenance and real training exist.

- [x] Clarify DeepEvolve retrieval provenance limitations.
  - README evidence: the plugin section labels `deep_research` as
    DeepEvolve-inspired web/retrieval context, but did not state that live
    retrieval events are not persisted.
  - Current evidence: `DeepResearchPlugin` keeps only `_synthesis` in memory
    and `arxiv_search()` returns title/summary text without arXiv IDs, URLs,
    timestamps, query metadata, or failure records. Prompt-injected retrieval
    context is not linked from history or `manifest.json`.
  - Required result: document that live retrieval context is best-effort and
    non-reproducible until provider/query/result provenance is persisted.

- [x] Clarify ImprovEvolve guidance is static and unattributed.
  - README evidence: the plugin section labels `modular` as
    ImprovEvolve-inspired modular decomposition prompting, but does not state
    that it always injects the same block and does not log a selected
    generate/improve/perturb operation.
  - Current evidence: `ModularPlugin.build_extra_context()` returns a constant
    prompt block, and `evolve()` concatenates plugin context into the prompt
    without a structured per-plugin context/provenance record.
  - Required result: document that modular guidance is static prompt-only until
    plugin prompt-context attribution or real ImprovEvolve operations exist.

- [x] Clarify missing per-call backend telemetry.
  - README evidence: the backend section says the router tracks observed
    fitness improvements, but did not distinguish that from provider-level call
    telemetry.
  - Current evidence: `LLMBackend.generate()` returns raw text only, and the
    loop stores backend indexes without token usage, latency, retry counts,
    response ids, finish reasons, or API-mode provenance.
  - Required result: note that per-call provider telemetry remains backend
    provenance work.

- [x] Clarify seed/replay limits.
  - README evidence: the CLI section exposed `--seed` only as "Random seed,"
    which could imply full replay stability.
  - Current evidence: `Config.seed` seeds local Python `random` choices and
    prompt variant sampling, but `Program.id` and `PromptProgram.id` use UUID4
    values, and provider outputs are not captured as a deterministic replay
    boundary.
  - Required result: tell readers that seeded local choices are controlled but
    persisted candidate/prompt IDs and provider outputs are not fully
    replay-stable yet.

- [x] Clarify workspace validator import/cwd limits.
  - README evidence: the custom-problem section said validators can accept
    `workspace_path`, but did not explain that the evaluator does not
    automatically run with that path as `cwd` or `sys.path`.
  - Current evidence: `CascadeEvaluator._run_subprocess()` passes the
    materialized candidate root as an argument only, and the `workspace_math`
    example manually inserts it into `sys.path`.
  - Required result: tell problem authors to use `workspace_path` explicitly for
    local imports/files until workspace execution semantics are hardened.

- [x] Clarify problem-local validator helper imports are not automatic.
  - README evidence: the problem-format section says `validate.py` defines
    `evaluate(...)`, but did not warn that `validate.py` is loaded by file path
    from a temporary runner rather than as a normal problem-local package.
  - Current evidence: `_RUNNER` uses `spec_from_file_location()` and
    `subprocess.run()` does not set `cwd` to the problem directory or add the
    validator directory to `sys.path`.
  - Required result: warn authors that sibling validator helpers/package
    imports need manual path handling until evaluator import semantics are
    hardened.

- [x] Clarify that MAP-Elites archive state is not persisted.
  - README evidence: the feature list and flow describe a MAP-Elites archive
    and island migration, but did not distinguish runtime archive state from
    append-only candidate history.
  - Current evidence: `history.jsonl` records candidates, while
    `MAPElites._grid`, elite lists, island assignment, descriptor values, and
    `IslandModel.migrate()` events remain in memory only.
  - Required result: warn readers that current run history is not a replayable
    archive checkpoint or migration event log.

- [x] Clarify candidate history lacks archive admission status.
  - README evidence: the flow says valid programs enter the MAP-Elites archive
    and all programs are logged, but did not say history records do not mark
    which logged programs were admitted, ignored, or displaced.
  - Current evidence: `evolve()` logs a `Program` before `db.add()`, and
    `MAPElites.add()` returns no insertion result. `history.jsonl` does not
    include threshold reason, island id, cell coordinates, replacement status,
    or previous occupant id.
  - Required result: warn readers that current candidate history is not an
    archive-admission event stream.

- [x] Clarify MAP-Elites descriptors use the primary-file view for workspaces.
  - README evidence: README advertises workspace candidates and a MAP-Elites
    archive, but did not state that archive complexity/diversity descriptors
    are still based on `Program.code`.
  - Current evidence: `MAPElites._cell()` uses `Program.code`; for multi-file
    candidates this is the primary-file compatibility view, so non-primary
    helper files do not affect code length or TF-IDF diversity cells.
  - Required result: warn readers that current quality-diversity descriptors
    are not yet full-workspace aware.

- [x] Clarify feedback graders are primary-file-only for workspaces.
  - README evidence: the feature list says feedback graders can add metrics or
    discard candidates, but did not mention the current prompt only includes
    the primary-file view.
  - Current evidence: `_build_feedback_prompt()` renders `workspace.primary_file`
    and `workspace.code` under `[CODE]`; non-primary workspace files are not
    included.
  - Required result: warn readers that multi-file feedback grading is not yet
    full-workspace aware.

- [x] Clarify feedback grader failure-isolation limits.
  - README evidence: optional feedback graders are described as able to add
    metrics or discard candidates, but the current caveats did not explain that
    malformed grader output or config can still fail outside structured
    evaluation diagnostics.
  - Current evidence: `apply_llm_feedback()` does not isolate `llm.generate()`
    failures, malformed numeric scores, invalid `weight`/`min_score` values, or
    string discard flags.
  - Required result: warn readers that LLM feedback failure handling is not yet
    AlphaEvolve-grade structured evaluation behavior.

- [x] Clarify evaluator-stage numeric config is not fully validated.
  - README evidence: the evaluation and configuration docs show staged
    validators with `samples`, `retries`, `timeout_sec`, and `min_score`, but
    did not warn that bad numeric values can fail at runtime.
  - Current evidence: `_run_stage()` casts stage numeric fields during
    evaluation; `samples <= 0` can reach aggregation with no sample results,
    and `retries < 0` can skip all attempts before an assertion.
  - Required result: document the current limitation and track startup schema
    validation for evaluator stage ranges in the code TODO.
