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
    regions are parsed and skeleton code is preserved during mutation.
  - Required result: problem loading should support one or more marked
    evolvable regions, preserve non-evolved skeleton code, and apply mutations
    only where configured.

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
    convenience artifact.
  - Required result: represent a candidate as a project/file set, apply diffs
    across marked files/components, and pass the whole candidate workspace to
    `evaluate`.

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

- [x] Add AlphaEvolve canonical SEARCH/REPLACE diff marker compatibility.
  - Spec evidence: AlphaEvolve Section 2.3 and Figure 3 use
    `<<<<<<< SEARCH`, `=======`, and `>>>>>>> REPLACE` blocks.
  - Status: implemented in `libreevolve/core/diff.py` via
    `parse_diff_blocks()`, which accepts both canonical AlphaEvolve fences and
    compact local fences. Tests cover low-level diff application, evolve-block
    restriction, and multi-file file-section routing for canonical blocks.
  - Required result: keep both formats backward-compatible in prompt docs,
    parser/apply logic, and mutation tests.

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

- [ ] Export complete best workspaces, not only the primary file.
  - Spec evidence: AlphaEvolve can evolve entire code files/codebases, so the
    output artifact must preserve all evolved components.
  - Current evidence: `libreevolve/cli.py` writes only `best.code` to
    `runs/<name>/best.py`; `history.jsonl` contains `files`, but there is no
    best-workspace directory or archive for direct reuse.
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

## Prompt Sampling and Context

- [x] Replace the simple prompt builder with a configurable prompt sampler.
  - Spec evidence: AlphaEvolve prompt sampling supports long contexts,
    previous solutions, system instructions, explicit context, stochastic
    formatting, rendered evaluation results, and meta-prompt evolution.
  - Current evidence: `build_prompt()` delegates to
    `libreevolve/core/prompt.py::PromptSampler`, which supports configurable
    templates, explicit context files, evaluator feedback, inspirations,
    plugin context, and recent in-memory failure hints.
  - Status: implemented in `libreevolve/core/prompt.py` with configurable
    templates, problem context files, inspirations, metrics, evaluator feedback,
    plugin context, and recent in-memory failure hints.
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

- [ ] Make failed/rejected mutation memory complete and queryable.
  - Spec evidence: AlphaEvolve prompt context and database are built around
    past trials, ideas, evaluation results, and feedback, including enough
    history to avoid repeating unproductive proposals.
  - Current evidence: `evolve()` keeps only an in-memory list of up to five
    recent failures, and it appends only when `score < VALID_THRESHOLD` and
    `child_code != parent.code`. Malformed diffs, `search_not_found`,
    `no_diff_blocks`, and no-op mutations typically leave the child code equal
    to the parent, so the failed mutation text/error is not rendered in later
    prompts even though the candidate is logged in `history.jsonl`.
  - Required result: store failed mutation text, diff error, parent id,
    evaluator diagnostics, and retry/repetition counts in candidate metadata or
    a queryable failure index; render bounded failure examples in prompts; add
    tests for malformed diff, search miss, no-op, invalid-domain, and
    validator-crash failures.

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
    interval-based LLM template mutation. Remaining hardening: placeholder
    validation, richer prompt fitness, and ablation reporting.
  - Required result: create a prompt-program representation, mutation path,
    scoring/selection policy, and integration into `build_prompt()`.

- [ ] Validate mutated prompt templates before adding them to the prompt
  database.
  - Spec evidence: AlphaEvolve's prompt evolution must keep prompts usable by
    the evolutionary loop; malformed evolved instructions should not break
    future generations.
  - Current evidence: `PromptDatabase.mutate()` accepts any returned string and
    `PromptSampler.build()` later formats it with required placeholders. There
    is no placeholder preservation check, rollback, or penalty for malformed
    prompt mutations.
  - Required result: validate required placeholders before insertion, log and
    penalize rejected prompt mutations, and add tests for missing/renamed
    placeholders.

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

- [ ] Enforce evaluator metric schema and scalar outputs.
  - Spec evidence: AlphaEvolve task specification requires `evaluate` to
    return a dictionary of scalar evaluation metrics, and those metrics drive
    database selection, prompting, and multi-score optimization.
  - Current evidence: `CascadeEvaluator._run_subprocess()` parses the last
    stdout line as JSON and requires `is_valid` plus the primary metric for
    fitness normalization, but it does not verify that every declared
    `metrics.yaml` metric is present, scalar, finite, or direction/bounds
    compatible.
  - Required result: validate evaluator outputs against `metrics.yaml`, reject
    or quarantine malformed/non-finite metrics with diagnostics, and add tests
    for missing secondary metrics, non-scalar values, NaN/Infinity, and
    undeclared metrics.

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

- [x] Honor `metrics.yaml` direction and bounds everywhere.
  - Spec evidence: AlphaEvolve's metrics are maximized by convention; the local
    problem format adds `direction` and `bounds`, so the implementation must
    either honor them or remove the claim.
  - Current evidence: `Problem.normalize_metric()` honors direction and bounds;
    evaluator fitness is normalized; `ProgramDatabase` and `IslandModel` pass
    normalized performance bounds into `MAPElites`.
  - Status: implemented via `Problem.normalize_metric()` and normalized archive
    performance cells; non-[0, 1] and minimize metrics have tests.
  - Required result: normalize metrics through declared bounds and directions,
    pass bounds into population archives, and test non-[0, 1] metrics.

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

- [ ] Review and improve parent/inspiration sampling.
  - Spec evidence: AlphaEvolve samples parent programs and inspirations from a
    database using an evolutionary algorithm inspired by MAP-Elites and island
    populations.
  - Current evidence: exploit always picks global best; explore picks a random
    occupied cell; inspirations are random occupied cells
    (`libreevolve/population/islands.py:28-39`).
  - Required result: add configurable sampling strategies, metric-aware
    inspiration choice, recency/novelty weighting, and tests for exploration
    pressure.

- [ ] Improve run inspection and archive diagnostics.
  - Spec evidence: AlphaEvolve's evolutionary database attaches scores and
    outputs to programs so explored ideas can be inspected and resurfaced.
  - Current evidence: `libreevolve show` prints total records, best primary
    fitness, and the best primary-file code only. It does not expose full file
    sets, metric vectors, stage failures, prompt lineage, archive cells,
    novelty/diversity signals, feedback records, or parent/child lineage.
  - Required result: extend `show` and/or machine-readable summaries with
    metrics, stage diagnostics, full-workspace pointers, lineage, prompt ids,
    archive diagnostics, and failure statistics.

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
    the original mutation `backend_idx` receives `record_reward()`. Auxiliary
    calls therefore affect routing state as apparent zero-reward pulls.
  - Required result: track call role/provenance, define reward or no-reward
    accounting per role, persist bandit state in run artifacts, and add tests
    proving critique/feedback/meta-prompt calls do not distort mutation routing.

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
  - Current evidence: `_build_config()` drops unknown `config.yaml` keys,
    backend specs from CLI are parsed with `partition(":")` without requiring a
    non-empty type/model, and many nested stage/feedback/backend fields are
    unvalidated until a later runtime path fails or silently ignores them.
  - Required result: add config schema validation with unknown-key errors or
    explicit warning policy, validate CLI backend specs, validate nested
    `eval_stages`/`llm_feedback`/backend metadata, and test malformed configs.

- [ ] Fix CLI/config override semantics and document precedence with tests.
  - Spec evidence: AlphaEvolve-style task setup depends on explicit,
    reproducible configuration for LLM choices, prompt behavior, evaluator
    settings, and run metadata.
  - Current evidence: `_build_config()` loads `problem_name` from
    `config.yaml`, then unconditionally overwrites it with `problem.name`;
    only `--run-name` changes the output directory. `--reasoning-effort` is
    applied only when `--backends` is also supplied, so it does not update
    OpenAI backend specs loaded from `config.yaml`.
  - Required result: define and test field-by-field precedence for defaults,
    config files, and CLI options; make ignored overrides explicit; ensure
    OpenAI reasoning options can be set or overridden consistently; and reflect
    the effective values in `manifest.json`.

- [ ] Add resumable runs.
  - Spec evidence: AlphaEvolve is a long-running autonomous pipeline optimized
    for large computation budgets.
  - Current evidence: runs append to `history.jsonl`, but `evolve()` always
    starts from seeds and does not resume archive/controller state.
  - Required result: persist and reload population/database state, backend bandit
    state, prompt database state, and pending evaluations.

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

- [ ] Improve isolation beyond a temporary Python subprocess.
  - Spec evidence: AlphaEvolve targets existing codebases and systems code,
    potentially with expensive or hardware-backed execution.
  - Current evidence: validator subprocesses run with the current Python
    interpreter and local filesystem access (`libreevolve/core/evaluator.py`).
  - Required result: add configurable sandbox/container/working-directory
    isolation, resource limits, and artifact collection.

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
