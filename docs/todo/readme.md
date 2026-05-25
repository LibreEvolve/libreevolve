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

- [x] Clarify migration disable semantics.
  - README/config evidence: population docs describe `migration_ratio` as a
    fraction rounded up to at least one migrant, while validation accepts
    `0.0`.
  - Status: implemented and documented. `migration_ratio=0.0` now selects no
    migrants; positive ratios still round up to at least one migrant from a
    non-empty island. `migration_interval=0` still disables scheduled migration
    calls entirely.

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

- [ ] Document or fix backend reward-state validation.
  - README/backend-doc evidence: README and backend docs describe UCB-style
    routing over observed fitness improvements and normalized ensemble
    telemetry.
  - Current evidence: `LLMEnsemble.record_reward()` accepts non-finite and
    negative values without validation. A local proof stored `nan`, `inf`, and
    `-5.0` in `wins` and subsequent generation continued from that state.
  - Required result: either enforce finite bounded reward updates before the
    scheduler mutates state, or document the current API contract and add tests
    proving invalid direct or resumed reward state is rejected.

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

- [ ] Clarify `llm_max_retries` versus provider-adapter internal retries.
  - README/config evidence: README and configuration docs describe
    `--llm-max-retries` / `llm_max_retries` as retry attempts on the same
    selected LLM backend before fallback/failure.
  - Current evidence: `LLMEnsemble.generate()` honors `llm_max_retries` at the
    ensemble layer, but `OpenAIBackend.generate()`, `AnthropicBackend.generate()`,
    and `OllamaBackend.generate()` each perform their own hard-coded three
    attempts with exponential backoff before returning an error to the
    ensemble. Therefore `llm_max_retries: 0` does not mean a single provider
    API attempt, and adapter attempts are not counted in telemetry or budgets.
  - Required result: either unify provider-adapter retries under the configured
    ensemble retry policy, or document the two retry layers clearly in README,
    backend docs, and configuration docs.

- [ ] Document that LLM provider calls are not yet bounded by run timeouts.
  - README evidence: README and `docs/run-artifacts.md` describe
    `--max-runtime-seconds` as a wall-clock run budget checked by the runtime.
  - Current evidence: `RunBudget` is checked between loop steps, but
    `LLMEnsemble.generate()` makes synchronous provider calls and the
    OpenAI/Anthropic/Ollama adapters do not accept or enforce a LibreEvolve
    request timeout/deadline. A slow mutation, critique, feedback, or
    meta-prompt provider call can exceed `max_runtime_seconds` before the loop
    can stop or write a timeout-specific artifact.
  - Required result: either implement provider-call timeouts/cancellation first
    or update README/backends/run-artifact docs so users understand that the
    current wall-clock budget is not an interrupt for in-flight LLM API calls.

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
  - Current evidence: the local non-integration suite currently has 431 passed,
    1 skipped, and 2 deselected tests under
    `py -3.12 -m pytest tests/ -m "not integration" --tb=short`, but major
    AlphaEvolve features are still absent or represented only as narrow
    prototype behavior.
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
    not validate availability. A 2026-05-25 check of the official OpenAI
    latest-model guide names `gpt-5.5`; README and configuration examples now
    avoid stale GPT-5.4 example labels.
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

- [ ] Clarify evolved prompt templates can currently drop essential prompt
  channels.
  - README-adjacent evidence: README/configuration/architecture docs describe
    prompt programs as selected, scored, logged, and optionally mutated, and
    say configured/evolved prompt templates are validated against the
    placeholder schema.
  - Current evidence: syntax/schema validation only requires `{task}`. A local
    proof admitted a mutated prompt template `Task only: {task}`, which omitted
    `{parent_code}` and `{mutation_instructions}` while still entering the
    prompt database.
  - Required result: either implement semantic placeholder-retention rules
    first, or document that current validation prevents malformed placeholders
    but does not guarantee evolved prompts retain code, feedback, inspiration,
    or mutation-format sections.

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

- [ ] Document primary-file identity fallback or enforce strict workspace
  primary validation first.
  - README/problem-format evidence: docs explain that workspace seeds choose
    `main.py`, `seed.py`, or the first `.py` file as the primary file, and
    `best.py`/legacy validators use that primary-file compatibility view.
  - Current evidence: lower-level `CandidateWorkspace` accepts an explicit
    missing `primary_file` and silently rewrites it to the first sorted file. A
    local proof passed `primary_file="missing.py"` with only `helper.py` in
    `files`; the resulting workspace used `helper.py` with no diagnostic.
  - Required result: either make constructor/deserialization strict before
    documenting primary-file identity as reliable, or document the current
    fallback behavior and its limits for future resume/history replay.

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

- [x] Clarify validator subprocess environment policy.
  - README evidence: README says validators run in a temporary local
    subprocess and must state what environment boundary applies.
  - Current evidence: CLI import loads `.env` with `override=True`, but
    `CascadeEvaluator._run_subprocess()` now passes an explicit minimal
    environment plus `validator_env_allowlist` to `subprocess.run()`. README
    now says provider keys are hidden by default, persisted stdout/stderr is
    secret-redacted, and validator network access is not sandboxed.
  - Required result: keep README aligned with the implemented allowlist policy
    and continue pointing network/sandbox limits to the TODOs.

- [x] Clarify validator timeout process-tree behavior.
  - README evidence: README discussed validator subprocess execution and
    timeouts and must state whether a timed-out validator's descendant
    processes are terminated.
  - Current evidence: `CascadeEvaluator._run_subprocess()` now launches a
    killable process tree, timeout results record cleanup metadata, and tests
    prove a spawned child cannot write a marker after timeout.
  - Required result: keep README aligned with timeout cleanup while preserving
    the caveat that this is not a container or general resource sandbox.

- [x] Clarify aggregate workspace syntax diagnostics.
  - README evidence: README described the cascade evaluator's syntax filter
    but did not say whether multi-file syntax diagnostics are aggregated.
  - Status: README now says the pre-validator syntax check covers `.py` files
    and reports all Python syntax errors across the workspace with file, line,
    offset, and message metadata.

- [x] Clarify validator-generated artifact retention.
  - README evidence: README says raw metrics and diagnostics are stored with
    each candidate and should explain the configured artifact copy-out path.
  - Current evidence: `CascadeEvaluator._run_subprocess()` can now copy files
    matching `evaluator_artifact_include` from the temporary candidate
    workspace into `evaluator_artifacts/` with hashes and provenance metadata.
  - Status: README now tells users that configured matching artifacts are
    retained, while non-matching files are discarded with the temporary
    workspace.
  - Required result: keep README aligned with configured artifact collection
    and the remaining raw-content/no-outside-workspace limits.

- [ ] Document evaluator artifact copy-out confinement and limit semantics.
  - README evidence: README says matching files written under the candidate
    workspace are copied to `evaluator_artifacts/` and that non-matching files
    are discarded with the temporary workspace.
  - Current evidence: the implementation matches relative paths under
    `cand_root`, but it does not resolve artifact targets back inside
    `cand_root` before reading them. On platforms where symlinks are available,
    `Path.is_file()` and `read_bytes()` can follow symlink targets. The local
    Windows account could not create the proof symlink (`WinError 1314`), but
    the static code path lacks a symlink/path-escape guard and lacks skip
    metadata. `artifact_max_bytes` is also enforced after a full
    `read_bytes()`, so README/config docs should not imply that it bounds
    validator artifact I/O or memory until the collector is hardened.
  - Required result: either implement confinement/streaming limits first, or
    document the current caveat plainly in README and run-artifact docs.

- [x] Soften the UCB1 paper-table role.
  - README evidence: the references table described UCB1 as "Multi-armed bandit
    selection."
  - Current evidence: `LLMEnsemble` is a heuristic UCB-style router over
    unbounded fitness deltas, and canonical reward-normalization work remains
    open in `docs/todo/papers.md`.
  - Required result: describe UCB1 as inspiration for backend routing, not as a
    fully canonical implementation.

- [x] Update the failure-history feature claim.
  - README evidence: the feature table claimed the last five failed mutations
    are shown in prompts, and the workflow section said failed mutations are
    tracked and shown in later prompts.
  - Current evidence: `failure_history.jsonl` now persists failed/rejected
    mutation records with changed files, error causes, mutation text, evaluator
    summaries, parent ids, and repetition counts. A bounded recent tail is
    rendered into prompts.
  - Required result: keep README aligned with the implemented local failure
    memory and avoid implying a learned long-term retrieval policy.

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
  - Current evidence: file-section headers now pass through
    `normalize_candidate_path()`, and README documents that nested paths,
    hyphens, spaces, Unicode filename characters, and Windows-style
    backslashes are accepted when normalized safely. README now also says
    candidate workspace construction rejects raw paths that normalize to the
    same relative path and materialization preflights case-folded host paths,
    and that duplicate file edit sections fail before partial application,
    while warning that Unicode normalization and topology-operation collision
    policy remain incomplete.
  - Required result: keep README aligned with current path parser behavior
    while still warning separately about path-collision handling and partial
    whole-envelope diagnostics.

- [ ] Correct docs that imply all unsafe candidate paths are rejected.
  - README/docs evidence: README and problem-format docs say file-section
    paths are accepted when normalized safely and unsafe paths are rejected.
  - Current evidence: `normalize_candidate_path()` rejects traversal,
    drive-letter, and colon-component paths, but silently strips leading `/`.
    POSIX-style absolute-looking paths such as `/new.py` are accepted and
    materialized as relative `new.py`.
  - Required result: after implementation, document that candidate paths are a
    strictly relative grammar and include leading-slash examples in path-safety
    tests/docs; until then, avoid broad "all unsafe paths rejected" wording.

- [ ] Document problem-local `context.yaml`, PDF context ingestion, and current
  context-selection limits in the README custom-problem section.
  - README evidence: the custom-problem tree shows only
    `context/optional_notes.md` and does not mention that `load_problem()` now
    accepts `.txt`, `.md`, `.py`, and `.pdf` files recursively, supports
    optional `context.yaml` / `context.yml` include/exclude patterns plus
    `max_chars_per_source`, and records source hashes/extraction spans for
    prompts/manifests.
  - Current evidence: `libreevolve/problems/loader.py` implements recursive
    deterministic context selection, PDF extraction through `pypdf`,
    citation-style metadata, and first-span character truncation; the
    architecture and configuration docs describe that behavior more fully.
  - Required result: update README's custom-problem example and caveats to
    show the supported context file types and `context.yaml` knobs, while
    clearly stating that large PDFs/text are still first-span truncated rather
    than semantically ranked or summarized.

- [ ] Document context provenance limits, not just supported context knobs.
  - README/docs evidence: `docs/problem-format.md` says the loader records
    source hashes and that source records are persisted in `manifest.json` for
    run provenance, while README does not yet explain the exact boundary.
  - Current evidence: `manifest.json` persists only selected
    `problem.context_sources`. It does not include the `context.yaml` file
    hash, effective include/exclude rules, skipped or excluded files, or
    unsupported-extension diagnostics, so the full context selection decision
    cannot be reconstructed from the manifest alone. A local proof showed that
    an unsupported typo key `includes:` in `context.yaml` is accepted silently,
    so README/problem-format docs should not imply the context manifest schema
    is fully validated.
  - Required result: update README/problem-format/run-artifact docs to state
    that current context provenance covers selected sources only until context
    manifest policy, unknown-key diagnostics, and skipped-source diagnostics
    are persisted.

- [ ] Stop teaching `is_valid` as an ordinary `metrics.yaml` scoring metric.
  - README evidence: the custom-problem `metrics.yaml` example declares
    `is_valid` alongside numeric scoring metrics, and the text says
    `evaluate()` returns a dict with all metric names.
  - Current evidence: `CascadeEvaluator._validate_metrics()` already requires
    boolean `is_valid` in evaluator output even when it is not declared in
    `metrics.yaml`. `load_problem()` currently allows `is_valid` to be
    declared as primary, which turns boolean validity into normalized fitness;
    that implementation gap is now tracked in `docs/todo/code.md`.
  - Required result: once the reserved-field policy is implemented or chosen,
    update README so `metrics.yaml` contains numeric optimization metrics and
    `is_valid` is documented as a required evaluator validity flag, not a
    normal optimizable metric.

- [x] Clarify malformed mutation envelope diagnostics.
  - README evidence: the custom-problem section describes file-section edits,
    but did not explain that unmatched or malformed envelope spans are not
    diagnosed as a whole response.
  - Current evidence: file and block envelope validation now rejects unmatched,
    orphaned, nested, empty-name, invalid-name, and unsafe-path sections before
    applying partial edits. README now describes that current behavior while
    noting the parser is not a complete mutation AST.
  - Required result: keep README aligned with current diagnostics and keep
    broader mutation-operation gaps, such as delete/rename/move, tracked
    separately.

- [x] Clarify multi-file topology mutation syntax.
  - README evidence: the custom-problem section describes multi-file seed
    workspaces and file-section edits, so it should state how topology changes
    are expressed.
  - Current evidence: `apply_workspace_mutation()` supports command file
    sections for delete, move/rename, and primary-file changes alongside
    ordinary file edits and full-mode creation.
  - Required result: keep README aligned with current workspace topology
    mutation behavior.

- [x] Clarify full mutation mode prompt behavior.
  - README evidence: the workflow says the LLM proposes either a SEARCH/REPLACE
    diff or configured full-block/full-code replacement.
  - Current evidence: `PromptSampler.DEFAULT_TEMPLATE` now renders
    mode-specific instructions. In `full` mode the prompt asks for full
    replacement content, including full-file `<<<FILE ... >>>FILE` sections
    and named `<<<BLOCK ... >>>BLOCK` sections where applicable. Custom prompt
    variants can still render or ignore `{mutation_mode}` and
    `{mutation_instructions}`.
  - Required result: keep README wording aligned with the active default prompt
    behavior and avoid warning that full mode is diff-oriented.

- [x] Clarify plugin score provenance limitations.
  - README evidence: the plugin hook table says `on_evaluated()` can modify
    score, so it must explain how those changes relate to evaluator validity
    and archived fitness.
  - Current evidence: `evolve()` stores per-plugin before/after score records
    in `metadata.score_composition`, and archive admission remains gated by
    evaluator/feedback validity.
  - Status: README now states that plugin score hooks can change final
    top-level fitness, that score provenance is stored in
    `metadata.score_composition`, and that archive admission is validity-gated.
  - Required result: keep README aligned with the current score-composition
    behavior and track broader plugin provenance separately.

- [ ] Document plugin side-effect validation limits.
  - README/plugin-doc evidence: plugin docs say plugins can modify effective
    score and maintain internal state, and README says score provenance is
    recorded under `metadata.score_composition`.
  - Current evidence: score-return validation exists, but plugin-added metrics
    and metadata are not validated before history logging. A local proof plugin
    set `program.metrics["plugin_bad"] = inf`; `evolve()` raised
    `StrictJsonlError` during `history.jsonl` write and only quarantined the
    rejected record in `history_invalid.jsonl`.
  - Required result: either implement plugin side-effect validation first, or
    document that plugins must currently keep added metrics/metadata finite and
    strict-JSON-serializable or they can abort the run after evaluation.

- [ ] Document plugin hook exception behavior or implement isolation first.
  - README evidence: README presents plugins as optional paper-inspired
    extensions for guidance, retrieval, score adjustment, and training-data
    export.
  - Current evidence: the loop does not isolate plugin hook exceptions. Calls to
    `on_generation_start`, `build_extra_context`, `prompt_context_metadata`,
    `on_evaluated`, `run_artifacts_metadata`, and `on_generation_end` can raise
    through the main run. A local proof with a plugin whose
    `build_extra_context()` raises `RuntimeError("plugin context failed")`
    aborts `evolve()` before mutation/evaluation logging. README/plugin docs do
    not warn users that a faulty optional plugin can currently terminate the
    run.
  - Required result: either implement structured plugin-failure isolation, or
    document the current fail-fast behavior in README/plugin docs until the
    runtime policy exists.

- [x] Clarify causal plugin mutation-format behavior.
  - README evidence: the plugin section labels the causal plugin as
    CausalEvolve-inspired, but did not state that its factor detector is not
    using the same canonical diff parser as candidate mutation application.
  - Current evidence: `CausalPlugin._detect_factors()` now uses
    `parse_diff_blocks()`, matching the core compact/canonical diff parser.
    README now says canonical AlphaEvolve fences are visible to factor
    guidance while the plugin remains a lightweight token-pattern heuristic,
    not CausalEvolve's causal scratchpad.
  - Required result: keep README aligned with the current parser behavior and
    continue distinguishing parser compatibility from paper-faithful causal
    reasoning.

- [ ] Fix stale causal-plugin fallback wording in plugin documentation.
  - Documentation evidence: `docs/plugins.md` says that when no causal factor
    matches, the plugin "falls back to a random factor."
  - Current evidence: `libreevolve/plugins/causal.py::_detect_factors()` now
    uses the shared `parse_diff_blocks()` parser and returns
    `self.FACTORS[0]` as a deterministic default when parsing fails or no
    factor pattern matches. `_ucb1_factor()` can choose randomly only if called
    with no observations, but `build_extra_context()` returns no guidance when
    `_history` is empty.
  - Required result: update plugin docs to describe deterministic no-match
    fallback and keep any randomness limited to the actual factor-selection
    path that can occur.

- [ ] Update plugin hook counts and hook-contract docs.
  - README/docs evidence: `README.md` advertises the plugin system as
    "4 lifecycle hooks," and `docs/plugins.md` lists only
    `on_generation_start()`, `build_extra_context()`, `on_evaluated()`, and
    `on_generation_end()` in its hook contract.
  - Current evidence: `PluginBase` also defines `prompt_context_metadata()`
    and `run_artifacts_metadata()`. These hooks are behaviorally significant:
    the loop records prompt-context attribution from
    `prompt_context_metadata()`, and completed manifests include plugin
    artifact summaries returned by `run_artifacts_metadata()`.
  - Required result: revise README and plugin docs to describe all current
    plugin hooks, distinguish lifecycle hooks from metadata/provenance hooks,
    and update any feature-count wording so the public docs do not understate
    or misclassify implemented plugin behavior.

- [x] Clarify ThetaEvolve export reward and artifact limitations.
  - README evidence: the plugin section says the ThetaEvolve-inspired plugin
    exports GRPO-style training data, but does not describe reward clipping,
    global output path, or missing manifest linkage.
  - Current evidence: `TTTRLPlugin.on_evaluated()` now stores `raw_score`,
    `reward = max(0.0, raw_score)`, and `reward_policy`. CLI-loaded `ttt_rl`
    writes under the active run's `plugin_artifacts/ttt_rl/` directory and
    completed manifests link export counts, path, bytes, hash, and quarantine
    path.
  - Required result: document that the export is a simple clipped-reward JSONL
    artifact until real training/checkpoint semantics exist.

- [x] Clarify DeepEvolve retrieval provenance limitations.
  - README evidence: the plugin section labels `deep_research` as
    DeepEvolve-inspired web/retrieval context, but did not state that live
    retrieval events are not persisted.
  - Current evidence: `DeepResearchPlugin` keeps only `_synthesis` in memory
    for prompt rendering, and `arxiv_search()` returns title/summary text
    through a compatibility wrapper. Candidate metadata now records bounded
    retrieval query, status, timestamp, result-length, synthesis-hash, arXiv
    source IDs/URLs, source timestamps/authors, summary hashes, and available
    provider errors plus structured error types when available. Completed
    manifests now include bounded run-level retrieval summaries, but full
    result payloads are not preserved.
  - Required result: document that live retrieval context is best-effort and
    only partially reproducible until full result payload policy is persisted.

- [x] Clarify ImprovEvolve guidance is static and only context-attributed.
  - README evidence: the plugin section labels `modular` as
    ImprovEvolve-inspired modular decomposition prompting, but does not state
    that it always injects the same block and does not log a selected
    generate/improve/perturb operation.
  - Current evidence: `ModularPlugin.build_extra_context()` returns a constant
    prompt block. `evolve()` now records per-plugin rendered context text,
    hashes, and parent/inspiration ids in candidate metadata, but it still does
    not choose or log a real ImprovEvolve generate/improve/perturb operation.
  - Required result: document that modular guidance is static prompt-only until
    real ImprovEvolve operations exist.

- [x] Clarify missing per-call backend telemetry.
  - README evidence: the backend section says the router tracks observed
    fitness improvements, but did not distinguish that from provider-level call
    telemetry.
  - Current evidence: `LLMBackend.generate()` returns raw text only.
    `LLMEnsemble` now wraps calls with role, backend, API mode, prompt/output
    size and hash, latency, status, and scheduler-count telemetry. Provider
    token usage, adapter-internal retry counts, response ids, finish reasons,
    and raw provider diagnostics remain unavailable.
  - Status: README now distinguishes implemented ensemble-level call telemetry
    and retry/fallback routing from missing provider-level telemetry and
    role-specific quarantine policy.
  - Required result: note that deeper provider telemetry remains backend
    provenance work.

- [x] Clarify seed/replay limits.
  - README evidence: the CLI section exposed `--seed` only as "Random seed,"
    which could imply full replay stability.
  - Current evidence: `Config.seed` seeds local Python `random` choices and
    `PromptSampler`'s RNG, but `evolve()` selects configured prompt variants
    through `PromptDatabase`. Untried prompt programs are sorted by UUID4 id,
    and `Program.id`/`PromptProgram.id` also use UUID4 values. Provider outputs
    are not captured as a deterministic replay boundary.
  - Required result: tell readers that seeded local choices are controlled but
    persisted candidate/prompt IDs and provider outputs are not fully
    replay-stable yet.

- [x] Clarify workspace validator import/cwd behavior.
  - README evidence: the custom-problem section said validators can accept
    `workspace_path`, but did not explain that the evaluator does not
    automatically run with that path as `cwd` or `sys.path`.
  - Current evidence: `CascadeEvaluator._run_subprocess()` now runs with the
    materialized candidate root as `cwd`, adds that root to `sys.path`, and
    passes it as `workspace_path`. README now states that candidate-local
    imports and relative file reads work by default.
  - Required result: keep README aligned with the current workspace execution
    contract and track remaining sandbox/build-system gaps separately.

- [x] Clarify problem-local validator helper imports.
  - README evidence: the problem-format section says `validate.py` defines
    `evaluate(...)`, but did not warn that `validate.py` is loaded by file path
    from a temporary runner rather than as a normal problem-local package.
  - Current evidence: `_RUNNER` still uses `spec_from_file_location()`, but it
    now adds `validate_path.parent` to `sys.path`, allowing sibling helper
    modules beside `validate.py` to import normally. README now documents that
    behavior.
  - Required result: keep README aligned with current sibling-helper import
    behavior and track richer package-style evaluator APIs separately.

- [x] Clarify that MAP-Elites archive state is not persisted.
  - README evidence: the feature list and flow describe a MAP-Elites archive
    and island migration, but did not distinguish runtime archive state from
    append-only candidate history.
  - Current evidence: `history.jsonl` records candidates, while
    `MAPElites._grid`, elite lists, island assignment, descriptor values, and
    `IslandModel.migrate()` events remain in memory only.
  - Required result: warn readers that current run history is not a replayable
    archive checkpoint or migration event log.

- [x] Clarify candidate archive admission status.
  - README evidence: the flow says valid programs enter the MAP-Elites archive
    and all programs are logged, so it should say what admission status is
    visible per row.
  - Current evidence: `ProgramDatabase.admit()` now stores
    `metadata.archive_admission` before `history.jsonl` rows are written.
  - Required result: keep README aligned with per-candidate admission events
    while distinguishing them from full archive snapshots.

- [ ] Clarify "archive-admitted" wording for MAP-Elites cell versus elite-list
  retention.
  - README evidence: README says `show` selects the best
    "archive-admitted valid" record and describes `metadata.archive_admission`
    as archive evidence with cell coordinates/descriptors and elite-list
    effects.
  - Current evidence: `MAPElites.add()` sets `admitted=True` for either
    `entered_cell` or `entered_elite`. A local proof with a one-cell archive and
    large elite list showed a lower-fitness same-cell program reported as
    `admitted=True`, `reason="elite_only"`, `entered_cell=False`, while the
    MAP-Elites grid occupant remained the earlier higher-fitness program.
    Current README/run-artifact wording does not explain that this admitted flag
    can mean auxiliary retention rather than a MAP-Elites cell update.
  - Required result: update README and run-artifact docs after the runtime
    fields are split, or document the current combined meaning plainly so users
    do not mistake elite-list retention for behavior-cell admission.

- [x] Clarify `show` archive-aware selection and remaining compact-view limits.
  - README evidence: the inspect-results section prints "Best fitness" and
    "Best program" from `libreevolve show`, which can imply the same archived
    best output as a completed run.
  - Current evidence: `cli.show()` now checks
    `metadata.archive_admission.admitted` and `evaluation.is_valid` for modern
    histories, prints the selection mode, and prints selected metrics when
    present. It falls back to highest-fitness selection for legacy histories
    without archive metadata and still prints only `best["code"]`.
  - Status: README now calls `show` a compact history view, documents the
    archive-admitted valid selection for current histories, documents the
    legacy fallback for checked-in fixtures, and tells users to use
    `best.py`/`best_workspace/` from the original run for exact archived output
    and full workspace.
  - Required result: keep the README distinction until `show` is made
    workspace-aware and richer stage/lineage/archive diagnostics exist.

- [x] Clarify checked-in example runs are legacy history fixtures.
  - README evidence: README points readers to `examples/runs/*` immediately
    after describing current run inspection and then says to use
    `best_workspace/` from the original run for archived best output.
  - Current evidence: the committed example run directories contain only
    `history.jsonl` and `best.py`; they do not include `manifest.json`,
    `prompt_history.jsonl`, `failure_history.jsonl`, or `best_workspace/`.
  - Required result: tell readers that checked-in example runs are useful
    history fixtures, not complete current run-artifact directories.

- [x] Clarify MAP-Elites descriptors use the primary-file view for workspaces.
  - README evidence: README advertises workspace candidates and a MAP-Elites
    archive, but did not state that archive complexity/diversity descriptors
    are still based on `Program.code`.
  - Current evidence: `MAPElites._cell()` uses `Program.code`; for multi-file
    candidates this is the primary-file compatibility view, so non-primary
    helper files do not affect code length or TF-IDF diversity cells.
  - Required result: warn readers that current quality-diversity descriptors
    are not yet full-workspace aware.

- [x] Clarify feedback grader workspace scope.
  - README evidence: the feature list says feedback graders can add metrics or
    discard candidates, so it should describe what candidate context graders
    see.
  - Current evidence: `_build_feedback_prompt()` now renders bounded full
    workspace sections with file paths, primary-file marking, truncation
    notices, basic secret redaction, and compact evaluator diagnostics.
  - Required result: keep README caveats aligned with current feedback-grader
    prompt behavior.

- [x] Clarify feedback grader failure-isolation limits.
  - README evidence: optional feedback graders are described as able to add
    metrics or discard candidates; the caveats previously said malformed
    output/config was not isolated.
  - Current evidence: `Config.validate()` now rejects invalid feedback grader
    config, and `apply_llm_feedback()` now records provider failures, malformed
    numeric response scores, non-finite response scores, and string discard
    flags as feedback-failure metadata without changing score/validity.
  - Required result: warn readers that richer retry/penalty/discard policy and
    score calibration remain open.

- [ ] Correct LLM feedback metric-collision documentation.
  - README/run-artifact evidence: `docs/run-artifacts.md` says the composed
    feedback score appears as `feedback_adjusted_fitness` while the raw primary
    validator metric remains intact.
  - Current evidence: `apply_llm_feedback()` accepts any configured grader
    metric name and writes it directly into `updated.metrics`. A local proof
    configured `metric: score` for a feedback grader; the evaluator's primary
    metric `score=0.8` was overwritten to `score=0.1` while top-level
    `fitness` stayed `0.8`.
  - Required result: either implement metric-name collision rejection/namespacing
    first, or update README/run-artifact docs to avoid claiming raw declared
    metrics are preserved when feedback graders can overwrite them.

- [x] Clarify prompt/history redaction limits.
  - README evidence: README described basic secret redaction for LLM feedback
    graders, but did not distinguish that from mutation prompts, critique
    prompts, explicit context, plugin context, and persisted run history.
  - Current evidence: feedback workspace rendering calls
    `_redact_sensitive_text()`, while `PromptSampler` renders context and
    program files directly, `evolve()` stores `metadata.prompt` and
    `metadata.critique.prompt`, and `ProgramDatabase.log()` writes metadata
    verbatim to `history.jsonl`.
  - Status: README now warns that mutation/critique prompt history is persisted
    without a general redaction or data-retention policy and advises keeping
    seeds/context/plugin text free of secrets.
  - Required result: keep user-facing docs clear about which prompt paths are
    redacted and which are still raw until the implementation gap in
    `docs/todo/code.md` is closed.

- [x] Clarify evaluator-stage numeric config validation.
  - README evidence: the evaluation and configuration docs show staged
    validators with `samples`, `retries`, `timeout_sec`, and `min_score`; the
    caveat previously warned that bad numeric values could fail at runtime.
  - Current evidence: `Config.validate()` now checks stage numeric fields before
    evaluation. Previously, `_run_stage()` cast stage numeric fields during
    evaluation; `samples <= 0` can reach aggregation with no sample results,
    and `retries < 0` can skip all attempts before an assertion.
  - Required result: keep README/config docs aligned with startup validation
    behavior while broader cascade semantics remain separately tracked.

- [x] Remove stale malformed-config caveats from architecture/configuration
  docs.
  - README-adjacent evidence: architecture and configuration docs still said
    malformed YAML or scalar/list top-level `config.yaml` files could fail
    before normalized startup diagnostics.
  - Current evidence: `_build_config()` catches `yaml.YAMLError` and raises a
    path-aware `ConfigError`, rejects non-mapping top-level YAML with a
    path-aware `ConfigError`, and CLI tests cover both paths.
  - Required result: keep docs clear that malformed and non-mapping config
    files now fail cleanly, while plugin-specific schemas and provider/model
    API compatibility remain open.

- [ ] Correct boolean config-validation claims for critique and meta-prompt
  switches.
  - README/config evidence: `docs/configuration.md` documents
    `meta_prompt_evolution` and `critique_enabled` as boolean switches, and
    adjacent docs say broad top-level config validation is now implemented.
  - Current evidence: `Config.validate()` does not call `_require_bool()` for
    either field. A local proof accepted
    `Config(meta_prompt_evolution="false")` and
    `Config(critique_enabled="false")`; both values stayed as strings and are
    truthy in the evolution loop.
  - Required result: either implement boolean validation for these switches
    before claiming broad config-schema enforcement, or document the current
    limitation clearly in README/configuration docs.

- [x] Clarify plugin config schema validation boundary.
  - README-adjacent evidence: architecture/configuration caveats implied
    plugin-specific schemas were partially validated.
  - Current evidence: `Config.validate()` only checks `plugins` is a list of
    strings, while `_load_plugins()` resolves those names through the CLI's
    hard-coded built-in registry and creates plugin instances with default
    constructors except for the run-scoped `ttt_rl` artifact path.
  - Required result: document that plugin-specific schemas and constructor
    parameters are not validated or configurable yet, while the separate
    plugin registry/config/provenance todo remains open.

- [x] Refresh README Anthropic model-name examples.
  - README evidence: the supported-backends table named "Claude Opus 4.6" as a
    current Anthropic model example.
  - Current evidence: Anthropic's model overview
    (`https://platform.claude.com/docs/en/about-claude/models/overview`)
    checked on 2026-05-25 lists current comparison models including Claude
    Opus 4.7, Claude Sonnet 4.6, and Claude Haiku 4.5, while LibreEvolve only
    forwards configured provider model IDs and does not validate provider
    availability.
  - Required result: avoid stale exhaustive-looking Anthropic model lists in
    README and present examples as provider-specific model IDs.

- [x] Clarify README benchmark-fixture wording.
  - README evidence: the example section and "Benchmarks and Lessons from Live
    Testing" heading could imply a benchmark suite rather than smoke examples.
  - Current evidence: `tests/test_examples.py` checks seed validity and simple
    validator rejection behavior; `matrix_multiplication` validates a small 2x2
    Python function and `circle_packing` validates fixed-26 feasibility, while
    `docs/todo/papers.md` still tracks AlphaEvolve-scale benchmark hardening.
  - Required result: label the examples as smoke/teaching fixtures and point to
    the paper todo for benchmark hardening.

- [x] Refresh documented run-artifact collision list.
  - README-adjacent evidence: configuration and run-artifact docs described
    fail/overwrite semantics but listed only the older history/prompt/manifest
    and best-output files.
  - Current evidence: `libreevolve/core/database.py::RUN_ARTIFACT_NAMES`
    includes candidate, failure, and prompt quarantine JSONL files plus
    `evaluator_artifacts/` and `plugin_artifacts/`.
  - Required result: keep docs aligned with the exact artifact set that
    preflight collision checks and overwrite cleanup use.

- [ ] Document `show` behavior for malformed or partially corrupt histories.
  - README/run-artifact evidence: README and `docs/run-artifacts.md` present
    `libreevolve show` as the compact inspection path for current and legacy
    `history.jsonl` files.
  - Current evidence: `show` does not catch `json.JSONDecodeError`. A local
    proof with one valid history row and one `not-json` row exited with a raw
    `JSONDecodeError` and no user-facing output, despite write-time JSONL
    quarantine docs being present elsewhere. A second proof showed a record
    with `metadata.archive_admission.admitted: true` and no `evaluation` is
    printed as `archive-admitted valid`, so the README claim about valid-record
    selection is stronger than the current predicate.
  - Required result: after implementing read-path diagnostics, document whether
    malformed history rows fail the whole inspection, are skipped with a
    warning, or are surfaced through a quarantine/repair workflow, and state
    the exact validity requirement used for current history records.

- [ ] Document and enforce run-name path confinement.
  - README/docs evidence: README and `docs/run-artifacts.md` describe
    `--run-name` as selecting a matching run directory under `runs/`, and
    `docs/configuration.md` describes `problem_name` as the final run
    subdirectory name.
  - Current evidence: the implementation does not validate `problem_name` or
    `--run-name` as a subdirectory name. A local proof with
    `log_dir=<tmp>/runs` and `problem_name="../escaped"` wrote artifacts under
    `<tmp>/escaped` outside the configured log root.
  - Required result: update docs after implementation to state the accepted
    run-name grammar and confinement policy, and warn accurately until the path
    validation gap is closed.

- [x] Add plugin artifacts to the run-artifact layout.
  - README-adjacent evidence: `docs/run-artifacts.md` documented
    `runtime.plugin_artifacts` and the `ttt_rl` export path, but the top-level
    directory tree omitted `plugin_artifacts/`.
  - Current evidence: the CLI scopes `ttt_rl` to
    `runs/<run-name>/plugin_artifacts/ttt_rl/`, `TTTRLPlugin` writes
    `grpo_data.jsonl` and `grpo_data_invalid.jsonl` there, and tests cover the
    scoped path plus manifest summaries.
  - Required result: show plugin artifact directories in the canonical run
    layout so docs match the runtime artifact surface.

- [x] Refresh README CLI reference for budget and overwrite options.
  - README evidence: the CLI reference listed core run options but omitted
    `--max-evaluations`, `--max-evaluator-seconds`, `--max-runtime-seconds`,
    and `--overwrite`.
  - Current evidence: `libreevolve/cli.py` exposes all four options, and
    `py -3.12 -m libreevolve run --help` shows them.
  - Required result: keep README's compact CLI reference aligned with live
    Click options that affect run budget accounting and artifact collision
    semantics.

- [ ] Clarify run stop-reason semantics for all-invalid seed populations.
  - README-adjacent evidence: `docs/run-artifacts.md` lists
    `no_parent` and `no_valid_programs` as current stop reasons, but does not
    explain which one applies when initial seed evaluation produces no
    archive-admitted parent.
  - Current evidence: a local all-invalid-seed run stops with
    `runtime.stop_reason == "no_parent"` and `generations_started == 1`; it
    does not use `no_valid_programs` and does not create failure history.
    `no_valid_programs` appears to be a fallback in `RunBudget.finish()` rather
    than the observed startup/no-parent path for normal loaded problems.
  - Required result: either change the runtime to emit a precise
    all-invalid-seed/no-valid-programs stop reason before incrementing
    generation counters, or document the current `no_parent` semantics and
    remove unreachable or misleading stop-reason descriptions.

- [x] Refresh evaluator labels beyond the original three-tier cascade.
  - README evidence: the feature list and architecture tree still described
    the evaluator as only Tier 0/1/2 or diff/syntax/subprocess filtering.
  - Current evidence: `CascadeEvaluator` keeps that default path but also
    supports configured validator stages with distinct entrypoints, timeouts,
    thresholds, samples, seeds, retries, stage context, and artifact policy.
  - Required result: describe the evaluator as a local staged cascade with
    configurable validator stages, while keeping distributed evaluator workers
    tracked separately.

- [ ] Document multi-sample evaluator aggregation limits.
  - README evidence: README describes configurable validator stages with
    thresholds, samples, seeds, retries, stage context, and artifact policy.
  - Current evidence: `_aggregate_metrics()` averages numeric metrics across
    samples. A local proof using a minimize primary metric `runtime` with two
    seeded samples returning `0.0` and `10.0` produced aggregated
    `runtime=5.0` and normalized `fitness=0.5`. README does not state that
    multi-sample numeric metrics currently use mean aggregation, nor that users
    cannot request worst-case, quantile, all-samples-pass, or per-metric
    threshold behavior.
  - Required result: either implement explicit aggregation/pass policy config
    first, or document the current fixed mean/all-booleans behavior and its
    limits in README/run-artifact docs.
