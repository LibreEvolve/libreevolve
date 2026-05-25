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
  - Current evidence: `load_problem()` reads whole seed files from
    `initial_programs/*.py` and stores each as one code string
    (`libreevolve/problems/loader.py:33-45`). There is no marker parser or
    skeleton/evolved-region distinction.
  - Status: implemented in `libreevolve/core/candidate.py`; one or more marked
    regions are parsed and skeleton code is preserved during mutation.
  - Required result: problem loading should support one or more marked
    evolvable regions, preserve non-evolved skeleton code, and apply mutations
    only where configured.

- [ ] Support multi-component and multi-file codebase evolution.
  - Spec evidence: AlphaEvolve evolves large code pieces spanning multiple
    functions and components and can evolve an entire code file/codebase.
  - Current evidence: `Program.code` is a single string, `apply_diff()` mutates
    one string, and the evaluator writes one `_cand.py` file
    (`libreevolve/core/evaluator.py:40-50`).
  - Required result: represent a candidate as a project/file set, apply diffs
    across marked files/components, and pass the whole candidate workspace to
    `evaluate`.

- [x] Add language-agnostic candidate support or narrow the claim to Python.
  - Spec evidence: AlphaEvolve is described as being able to evolve code in any
    language.
  - Current evidence: `CascadeEvaluator.evaluate()` calls Python `compile()`
    and imports Python `validate.py` (`libreevolve/core/evaluator.py:31-38`).
  - Status: README, architecture, problem format, and roadmap now state the
    current Python-only/single-workspace scope as a deliberate divergence.
  - Required result: either introduce pluggable language runners and validators
    or document Python-only scope as a deliberate divergence.

- [x] Add direct full-code/full-block replacement mode in addition to diffs.
  - Spec evidence: AlphaEvolve can be configured to ask for a complete code
    block when a rewrite is more appropriate than a small modification.
  - Current evidence: `build_prompt()` always asks for SEARCH/REPLACE diffs
    (`libreevolve/core/loop.py:37-40`), and the generation path always calls
    `apply_diff()` (`libreevolve/core/loop.py:76-78`).
  - Status: implemented as `Config.mutation_mode` and CLI `--mutation-mode`,
    with `diff` and `full` modes covered by tests.
  - Required result: add a per-problem/per-run mutation mode for full block,
    full file, or diff-based edits, with validator coverage for each mode.

## Prompt Sampling and Context

- [x] Replace the simple prompt builder with a configurable prompt sampler.
  - Spec evidence: AlphaEvolve prompt sampling supports long contexts,
    previous solutions, system instructions, explicit context, stochastic
    formatting, rendered evaluation results, and meta-prompt evolution.
  - Current evidence: `build_prompt()` is fixed string assembly with parent
    code, random inspirations, plugin context, and recent failures only
    (`libreevolve/core/loop.py:20-40`).
  - Status: implemented in `libreevolve/core/prompt.py` with configurable
    templates, problem context files, inspirations, metrics, evaluator feedback,
    plugin context, and recent failures. Meta-prompt evolution remains separate.
  - Required result: introduce prompt templates, stochastic template choices,
    user-provided context files, and structured prompt sections.

- [x] Include rendered evaluation results and program outputs in prompts.
  - Spec evidence: AlphaEvolve prompts can include a program, the result of
    executing that program, and scores assigned by `evaluate`.
  - Current evidence: evaluator returns only a float and discards the metrics
    dict, stdout/stderr, timeout cause, and any validator output
    (`libreevolve/core/evaluator.py:57-63`).
  - Status: implemented through `EvaluationResult`, `Program.evaluation`,
    JSONL persistence, and `PromptSampler` feedback rendering.
  - Required result: return an evaluation result object, store it with the
    program, and render relevant metrics/output in future prompts.

- [ ] Implement meta-prompt evolution.
  - Spec evidence: AlphaEvolve co-evolves prompt instructions/context in a
    separate database analogous to solution programs and ablates "No meta
    prompt evolution" as a reduced system.
  - Current evidence: no prompt database exists; prompt text is static except
    plugin context (`libreevolve/core/loop.py:20-40`).
  - Required result: create a prompt-program representation, mutation path,
    scoring/selection policy, and integration into `build_prompt()`.

- [ ] Add first-class literature/context ingestion.
  - Spec evidence: AlphaEvolve supports explicit context such as instructions,
    equations, code snippets, and relevant literature, including PDF files.
  - Current evidence: only `task_description.txt` and plugin strings are
    inserted into prompts (`libreevolve/core/loop.py:30-35`). The
    `DeepResearchPlugin` searches arXiv by a generic query derived from fitness,
    not by the problem's supplied literature (`libreevolve/plugins/deep_research.py`).
  - Required result: allow problem-local context files, PDFs, equations, and
    code snippets to be selected, summarized, and rendered deterministically.

## Evaluation

- [ ] Replace the fixed three-tier evaluator with user-configurable evaluation
  cascades.
  - Spec evidence: AlphaEvolve supports ensembles of test cases of increasing
    difficulty, moving candidates to later stages only if earlier stages are
    promising.
  - Current evidence: the cascade is hard-coded to diff penalty, Python syntax,
    then one validator subprocess (`libreevolve/core/evaluator.py:31-63`).
  - Required result: support configured stages, per-stage thresholds, sample
    sizes, retry/random-seed policies, and separate metrics per stage.

- [x] Preserve full evaluator feedback, not just scalar fitness.
  - Spec evidence: AlphaEvolve stores solutions with evaluation results,
    scores, and program outputs attached.
  - Current evidence: `ProgramDatabase.log()` writes only code, one `fitness`,
    generation, lineage, and prompt/diff metadata
    (`libreevolve/core/database.py:24-34`).
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
  - Current evidence: the loader stores all metrics, but the evaluator returns
    only `primary_metric`; archive cells and backend reward use one float
    (`libreevolve/problems/loader.py:26-45`,
    `libreevolve/core/evaluator.py:57-63`,
    `libreevolve/core/loop.py:95-99`).
  - Required result: represent full metric vectors, choose target metrics,
    support Pareto/frontier or score-composition policies, and sample
    inspirations by metric-specific excellence.

- [x] Honor `metrics.yaml` direction and bounds everywhere.
  - Spec evidence: AlphaEvolve's metrics are maximized by convention; the local
    problem format adds `direction` and `bounds`, so the implementation must
    either honor them or remove the claim.
  - Current evidence: `direction` is parsed only as unused dict data; bounds are
    parsed but not passed to `MAPElites` because `IslandModel` constructs
    `MAPElites(...)` without `perf_bounds`
    (`libreevolve/problems/loader.py:36-45`,
    `libreevolve/population/islands.py:18-20`).
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
  - Current evidence: `LLMEnsemble` uses only UCB1 over scalar rewards and has
    no concept of cheap breadth model versus expensive depth model
    (`libreevolve/llm/ensemble.py`).
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
  - Current evidence: only candidate JSONL and `best.py` are written; effective
    config and backend roster are not persisted.
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
