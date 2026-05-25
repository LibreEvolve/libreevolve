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

## Prompt Sampling and Context

- [x] Replace the simple prompt builder with a configurable prompt sampler.
  - Spec evidence: AlphaEvolve prompt sampling supports long contexts,
    previous solutions, system instructions, explicit context, stochastic
    formatting, rendered evaluation results, and meta-prompt evolution.
  - Current evidence: `build_prompt()` delegates to
    `libreevolve/core/prompt.py::PromptSampler`, which supports configurable
    templates, explicit context files, evaluator feedback, inspirations,
    plugin context, and recent failures.
  - Status: implemented in `libreevolve/core/prompt.py` with configurable
    templates, problem context files, inspirations, metrics, evaluator feedback,
    plugin context, and recent failures.
  - Required result: introduce prompt templates, stochastic template choices,
    user-provided context files, and structured prompt sections.

- [x] Include rendered evaluation results and program outputs in prompts.
  - Spec evidence: AlphaEvolve prompts can include a program, the result of
    executing that program, and scores assigned by `evaluate`.
  - Current evidence: evaluator returns `EvaluationResult`; `Program` stores
    `metrics` and `evaluation`; `PromptSampler` renders recent stage feedback.
  - Status: implemented through `EvaluationResult`, `Program.evaluation`,
    JSONL persistence, and `PromptSampler` feedback rendering.
  - Required result: return an evaluation result object, store it with the
    program, and render relevant metrics/output in future prompts.

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

## Evaluation

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

- [ ] Add LLM-generated feedback as an optional evaluation signal.
  - Spec evidence: AlphaEvolve can grade hard-to-code properties, such as
    simplicity, using separate LLM calls and either add scores or discard
    solutions.
  - Current evidence: plugins can alter final score, but there is no standard
    feedback evaluator interface or LLM-feedback result schema
    (`libreevolve/plugins/base.py`).
  - Required result: add optional feedback graders with clear provenance,
    score-composition rules, and archive/log visibility.

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

## LLM Ensemble

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

- [ ] Add critique/review generation stage.
  - Spec evidence: the AlphaEvolve paper describes using LLMs to generate,
    critique, and evolve a pool of algorithms.
  - Current evidence: there is one generation call per mutation
    (`libreevolve/core/loop.py:76`) and no critique/refinement stage.
  - Required result: support optional critique, self-revision, or reviewer
    passes before evaluation.

## Runtime, Reproducibility, and Safety

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

- [ ] Improve isolation beyond a temporary Python subprocess.
  - Spec evidence: AlphaEvolve targets existing codebases and systems code,
    potentially with expensive or hardware-backed execution.
  - Current evidence: validator subprocesses run with the current Python
    interpreter and local filesystem access (`libreevolve/core/evaluator.py`).
  - Required result: add configurable sandbox/container/working-directory
    isolation, resource limits, and artifact collection.
