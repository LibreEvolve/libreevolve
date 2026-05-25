# Papers Todo: Reference and Specification Gaps

This list tracks mismatches discovered while reviewing the local `papers/`
directory and using the AlphaEvolve paper as the primary specification.

## AlphaEvolve Paper Requirements Not Yet Implemented

- [x] Task specification API with evolve-block markers.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: users mark code blocks to evolve inside a larger skeleton.
  - Status: implemented for Python single-file and local workspace candidates
    in `libreevolve/core/candidate.py`; arbitrary-language runners remain open.

- [ ] Flexible candidate abstraction API.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: AlphaEvolve lets users choose the solution abstraction, from
    raw solution strings to constructor functions, bespoke search algorithms,
    or paired solution/search representations.
  - Current gap: LibreEvolve represents candidates as text file sets with a
    primary Python code view. Validators can interpret that code flexibly, but
    candidate rendering, mutation, persistence, and materialization are not
    problem-defined abstraction hooks.
  - Required result: add first-class candidate abstraction modes or document
    code-file evolution as a deliberate divergence from AlphaEvolve.

- [x] Rich prompt sampler.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompts may include previous solutions, system instructions,
    explicit context, stochastic formatting, rendered evaluation results, and
    meta-prompt evolution.
  - Status: implemented prompt templates, deterministic local context files
    including PDF extraction, whole-template stochastic variants, compact stage
    feedback summaries, and local prompt-program selection, scoring, lineage,
    and optional LLM mutation.
  - Remaining divergence: stochastic formatting is whole-template sampling, not
    AlphaEvolve's placeholder alternatives with configured probability
    distributions; prompt mutations are not validated before insertion; prompt
    feedback rendering omits stdout/stderr, artifacts, sample-level outputs,
    and LLM grader summaries.

- [x] Output modes beyond SEARCH/REPLACE diffs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: diff blocks are default, but AlphaEvolve can ask for a complete
    code block when appropriate.
  - Status: implemented `diff` and `full` mutation modes.
  - Remaining divergence: the parser does not accept the canonical
    `<<<<<<< SEARCH` / `=======` / `>>>>>>> REPLACE` block spelling used in the
    paper; it accepts LibreEvolve's compact `<<<SEARCH` format.

- [x] Frontier model ensemble scheduling.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: combine a fast, lower-latency model for breadth with a stronger
    model for depth.
  - Status: added experimental `throughput_depth` scheduling metadata layered
    over UCB-style scores.

- [ ] Existing/custom LLM backend extension point.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 2 and Section 2.3.
  - Requirement: AlphaEvolve is model-agnostic and its setup includes a choice
    of existing or custom LLMs.
  - Current gap: LibreEvolve supports OpenAI, Anthropic, and Ollama through a
    hard-coded `build_llm()` registry. New providers require source edits
    rather than config-driven or plugin-driven backend registration.
  - Required result: add a custom backend interface/registry and tests, or
    document the fixed-provider scope as a deliberate divergence.

- [x] Configurable evaluation cascades.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: users can specify increasing-difficulty test ensembles and
    early-stage pruning.
  - Status: added configurable local validator stages with distinct entrypoints,
    thresholds, seeded samples, retries, stage context, and timeouts.
    Distributed/parallel evaluator nodes remain open.

- [ ] Strict scalar metric contract for evaluator outputs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: `evaluate` maps a solution to a dictionary of scalar
    evaluation metrics.
  - Current gap: evaluator output is only partially validated; missing
    secondary metrics, non-scalar values, non-finite numbers, and undeclared
    metrics are not consistently rejected against `metrics.yaml`.
  - Required result: enforce the scalar metric contract and preserve clear
    diagnostics for invalid evaluator outputs.

- [x] LLM-generated feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: optional LLM graders can score hard-to-capture properties or
    discard candidates.
  - Status: implemented as optional synchronous LLM graders with metrics,
    weighted score composition, discard rules, backend provenance, raw
    responses, and `history.jsonl` visibility. Parallel reviewer workers and
    calibrated grader ensembles remain open.
  - Remaining divergence: feedback scores are not validated against
    `metrics.yaml` bounds/directions and can be added directly to normalized
    fitness without calibration.

- [ ] Parallelized evaluation and asynchronous throughput.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: expensive evaluations can be parallelized, and the whole
    pipeline runs as an async controller with LLM samplers and evaluation nodes.
  - Current gap: `evolve()` is synchronous and evaluates one candidate at a time.

- [ ] Overall compute-budget accounting and ablation support.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.6 and 4.
  - Requirement: AlphaEvolve optimizes throughput under a fixed computation
    budget, and ablations compare performance as a function of consumed budget.
  - Current gap: LibreEvolve has `max_generations` plus per-subprocess
    timeouts, but no run-wide budget object, consumed-budget counters,
    structured stop reason, token/cost/evaluator-second accounting, or
    benchmark harness that can report performance by compute-budget fraction.
  - Required result: persist budget configuration and consumption in manifests
    and history, stop deterministically on exhausted budgets, and add benchmark
    scripts/reports that can compare variants at equal budget fractions.

- [ ] Multiple-score optimization.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: optimize multiple user-provided scores and use programs that
    excel under different criteria as varied inspirations.
  - Partial status: metric vectors are stored and normalized primary fitness
    honors direction/bounds. Pareto/frontier optimization remains open.

- [x] Evolutionary database with attached outputs and feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: solutions have scores and program outputs attached, and the
    database resurfaces ideas to balance exploration/exploitation.
  - Status: JSONL records include raw metrics and structured evaluation output.
    Queryable score/metric/diversity/feedback sampling remains open.

- [ ] Rich prompt rendering of execution outputs and feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompt context can include program execution results, outputs,
    and scores from previous attempts.
  - Current gap: history records preserve stdout/stderr and LLM feedback
    provenance, but prompt construction renders only a short recent-stage
    summary.
  - Required result: add bounded prompt sections for execution outputs,
    artifacts, validator feedback, sample-level diagnostics, and grader
    feedback summaries.

- [ ] Failed-trial and rejected-mutation memory.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figures 1-2 and Section 2.2.
  - Requirement: the program database and prompt sampler provide rich context
    containing past trials, ideas, quality scores, and feedback so future
    generations can learn from explored attempts.
  - Current gap: LibreEvolve keeps a small in-memory recent-failure list and
    omits malformed/no-op/search-miss diffs from that prompt memory because no
    child code change is produced. Failed proposal text is not queryable or
    persisted as a first-class negative example for future prompts.
  - Required result: persist and sample failed/rejected proposals with their
    error causes, outputs, parent ids, and repetition counts.

- [x] Full-file/full-codebase evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 4 ablations.
  - Requirement: AlphaEvolve evolves whole code files/codebases and ablates
    "No full-file evolution" as a weaker setting.
  - Current evidence: `CandidateWorkspace` supports local text file sets,
    `<<<FILE path ... >>>FILE` mutation envelopes, full-mode file creation,
    workspace materialization for validators, and JSONL file-set logging.
  - Status: implemented for local Python/text workspaces. Remaining divergence:
    no arbitrary external repository/build-system runner and `best.py` exports
    only the primary file convenience view.

- [ ] Full-workspace output artifacts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 2.1.
  - Requirement: if a candidate is a full file/codebase, the selected best
    candidate must be recoverable as a full codebase.
  - Current gap: `history.jsonl` stores candidate file sets, but the CLI exports
    only `best.py`, the primary-file compatibility view.
  - Required result: add `best_workspace/` or equivalent archive artifacts and
    document them in run-artifact docs and tests.

- [ ] Canonical AlphaEvolve diff block compatibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Figure 3.
  - Requirement: support the paper's SEARCH/REPLACE fence spelling when using
    AlphaEvolve-style prompts or examples.
  - Current gap: local mutation parsing uses compact fences only.
  - Required result: accept both canonical and compact diff formats without
    breaking existing seeds/tests.

- [ ] Structured proposal idea/rationale capture.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 3 and Section 2.3.
  - Requirement: AlphaEvolve asks the LLM to suggest a new idea and describe
    changes with SEARCH/REPLACE blocks; the evolutionary loop benefits from
    keeping generated ideas, critiques, and outcomes connected.
  - Current gap: LibreEvolve prompts demand raw diff only, and history stores
    the raw diff but not a separate proposal idea, rationale, or hypothesis
    artifact for later inspection, critique, or resurfacing.
  - Required result: support a configured response format that separates
    proposal rationale from patch blocks while preserving diff-only
    compatibility.

- [x] Meta-prompt evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt instructions/context can be co-evolved in a separate
    database.
  - Current evidence: `PromptDatabase` stores prompt programs, logs
    `prompt_history.jsonl`, records prompt rewards/usages, and supports
    lineage-preserving mutation. `evolve()` uses prompt programs during prompt
    construction and can optionally ask the active LLM to mutate templates.
  - Status: implemented locally. Remaining divergence: no published
    AlphaEvolve-equivalent ablation harness or advanced prompt-fitness model.

- [ ] AlphaEvolve-style stochastic prompt formatting.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: support template placeholders with human-provided alternatives
    and probabilities in configuration.
  - Current gap: prompt variation is uniform whole-template selection and does
    not implement probability-distribution placeholders.

## Local Paper Corpus Issues

- [x] Refresh the local paper index after implementation passes.
  - Evidence: `papers/README.md` still listed multi-file candidates, critique,
    LLM feedback, and meta-prompt evolution as open after those local
    implementations landed.
  - Status: refreshed the AlphaEvolve row to distinguish implemented local
    behavior from remaining async, multi-objective, database, canonical-diff,
    full-workspace export/resume, metric-validation, feedback-calibration,
    LLM-accounting, config-validation, and benchmark gaps.
  - Required result: keep the paper index aligned with current code whenever
    todo items are completed or reopened.

- [x] Decide and document the paper corpus source of truth.
  - Evidence: `papers/download_manifest.csv` lists 24 downloaded papers, while
    the README claims 23 references.
  - Required result: update README badges/text and possibly add a
    `papers/README.md` that explains why each PDF is present.

- [x] Track the paper index and manifests without committing PDFs.
  - Evidence: README points readers to `papers/README.md`, but `.gitignore`
    ignored the entire `papers/` directory.
  - Status: `.gitignore` now ignores `papers/*` while allowing
    `papers/README.md`, `download_manifest.csv`, and
    `download_manifest.json`.
  - Required result: keep small paper-index evidence in version control while
    leaving large cached PDFs local.

- [x] Add a paper index with roles and implementation status.
  - Evidence: downloaded papers include system papers, domain-result papers,
    and foundational algorithm papers, but only a subset is summarized in the
    README.
  - Required result: create a table with paper id, title, role, implemented
    status, and linked todo items.

- [x] Separate AlphaEvolve requirements from other-paper inspirations.
  - Evidence: code comments cite non-AlphaEvolve papers for local choices, such
    as TF-IDF diversity, CausalEvolve heuristics, DeepEvolve arXiv search, and
    ThetaEvolve JSONL export.
  - Required result: document which features are necessary for AlphaEvolve
  fidelity and which are optional LibreEvolve extensions.

- [x] Turn the downloaded benchmark/result papers into explicit benchmark
  coverage decisions.
  - Evidence: `papers/download_manifest.csv` includes domain-result papers for
    sums/differences, autoconvolution, hardness of approximation, Bruhat
    intervals, global NLP optimization, multiagent learning, Ramsey numbers,
    Berczy combinatorics, bilateral trade, and related AlphaEvolve-style
    mathematical results.
  - Current evidence: `libreevolve/problems/examples/` contains
    `hello_world`, `sorting`, `circle_packing`, and `matrix_multiplication`.
  - Required result: for each downloaded domain paper, either add a
    corresponding problem fixture/benchmark, link it to an existing benchmark,
    or mark it as background-only in a paper index.

- [x] Add AlphaEvolve-paper benchmark parity targets.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` evaluates matrix
    multiplication, many constructive math problems, data-center scheduling,
    TPU arithmetic circuits, LLM-training kernels, and FlashAttention/GPU
    instruction optimization.
  - Current evidence: checked-in AlphaEvolve-adjacent examples include
    `circle_packing` and `matrix_multiplication`.
  - Required result: choose a small reproducible subset, such as matrix
    multiplication rank search, circle/kissing packing, and one scheduling or
    kernel microbenchmark, then add validators and expected run artifacts.

- [ ] Harden benchmark implementations beyond smoke-example fidelity.
  - Paper evidence: the AlphaEvolve paper's matrix task searches low-rank tensor
    decompositions with randomized initializations and exact verification;
    Appendix B.12 reports circle packing in the unit square for `n = 26` and
    `n = 32`; Figure 8 compares ablations by compute-budget fraction.
  - Current evidence: the checked-in matrix example validates only a 2x2 Python
    `matmul2` function on three deterministic cases and counts AST
    multiplication nodes. The circle example matches the fixed-26 unit-square
    objective family, but there is no benchmark harness for repeated seeds,
    SOTA thresholds, saved construction artifacts, visual/JSON outputs, or
    equal-budget ablation curves.
  - Required result: distinguish smoke examples from benchmark fixtures in docs,
    add operation/rank-aware matrix validation, add artifact schemas for
    geometric constructions, and create repeatable benchmark reports tied to
    AlphaEvolve target families.

## Paper-Inspired Feature Claims Needing Correction

- [ ] Keep CausalEvolve-inspired behavior explicitly paper-limited or implement
  the paper's causal scratchpad.
  - Paper evidence: `2603.14575__CausalEvolve.pdf` describes LLM-assisted
    causal factor identification, outcome-level factors, surprise-pattern
    inspection, and abductive reasoning to hypothesize new factors during
    evolution.
  - Current evidence: the CLI alias is paper-neutral (`causal`) and docs label
    it CausalEvolve-inspired, but `libreevolve/plugins/causal.py` still uses
    regex factor detection over changed diff tokens and UCB1-like reward
    accounting.
  - Missing: LLM causal scratchpad, POMDP/causal framing, initial factor
    discovery, surprise-pattern inspection, abductive factor creation, and
    structured causal knowledge reuse.

- [ ] Keep DeepEvolve-inspired behavior explicitly paper-limited or implement
  DeepEvolve's retrieval, cross-file editing, and debugging loop.
  - Paper evidence: `2510.06056__DeepEvolve.pdf` integrates external knowledge
    retrieval, cross-file code editing, systematic debugging, hypothesis
    refinement, implementation, and testing in each iteration.
  - Current evidence: the CLI alias is paper-neutral (`deep_research`) and docs
    label it DeepEvolve-inspired, but `libreevolve/plugins/deep_research.py`
    performs a generic arXiv Atom search every N generations and injects short
    summaries into the prompt.
  - Missing: broad external retrieval, source ranking, hypothesis synthesis,
    implementation/refinement loop, systematic debugging, cross-file editing,
    and benchmark-grounded result validation.

- [ ] Keep ImprovEvolve-inspired behavior explicitly paper-limited or implement
  the actual generate/improve/perturb parameterization and search dynamics.
  - Paper evidence: `2602.10233__ImprovEvolve.pdf` evolves a class/interface
    with `generate_config`, `improve`, and `perturb`, then approaches optima by
    scheduled basin-hopping-style application of `improve()` and `perturb()`.
  - Current evidence: the CLI alias is paper-neutral (`modular`) and docs label
    it ImprovEvolve-inspired, but `libreevolve/plugins/modular.py` injects a
    static prompt block asking for those method names.
  - Missing: enforced interface, evaluator support for the interface,
    iterative improve/perturb execution, perturbation-intensity scheduling, and
    benchmark-specific search loop.

- [ ] Keep ThetaEvolve-inspired behavior explicitly paper-limited or implement
  batch sampling, dynamic RL training, and reward shaping.
  - Paper evidence: `2511.23473__ThetaEvolve.pdf` describes a single-LLM
    framework with a large program database, batch sampling, lazy penalties,
    optional reward shaping, and reinforcement learning at test time.
  - Current evidence: the CLI alias is paper-neutral (`ttt_rl`) and docs label
    it ThetaEvolve-inspired, but `libreevolve/plugins/ttt_rl.py` writes
    `(prompt, response, reward)` JSONL and does not train.
  - Missing: batch prompt sampling, lazy/stagnation penalties, reward shaping,
    online GRPO/RL training loop, dynamic environment integration, and training
    checkpoint management.

- [ ] Tighten or remove GigaEvo-derived implementation claims.
  - Paper evidence: `2511.17592__GigaEvo.pdf` describes Redis-backed
    evolutionary units with lifecycle state, optimistic concurrency, an
    asyncio DAG execution engine, configurable stages, insights, bidirectional
    lineage, and rewrite/diff mutation modes.
  - Current evidence: comments cite append-only JSONL lineage and multi-island
    exchange, but `ProgramDatabase` is a thin JSONL facade and `IslandModel` is
    synchronous.
  - Missing: persistent concurrent database, lifecycle states, async DAG
    stages, bidirectional lineage, insight generation, and rewrite mutation
    mode.

- [ ] Tighten or remove CodeEvolve-derived implementation claims.
  - Paper evidence: `2510.14150__CodeEvolve.pdf` combines islands-based
    genetic search with modular LLM orchestration, execution feedback,
    context-aware recombination, adaptive meta-prompting, and targeted
    refinement.
  - Current evidence: `IslandModel` has no crossover/recombination, no adaptive
    meta-prompting, and no targeted refinement stage.
  - Missing: recombination/crossover, modular orchestration, adaptive
    meta-prompts, targeted refinement, and cost/performance ablation support.

- [ ] Decide whether MadEvolve-inspired features are in scope.
  - Paper evidence: `2602.15951__MadEvolve.pdf` emphasizes free parameters,
    parameter optimization, hybrid population management, LLM ensemble
    strategies, and automated report generation comparing input and evolved
    algorithms.
  - Current evidence: README cites MadEvolve as domain-specific evolution, but
    there is no parameter tracking/optimization layer or generated innovation
    report.
  - Missing: free-parameter extraction, gradient or gradient-free parameter
    optimization, algorithm comparison report, and parameter-function summary.

- [ ] Document which MAP-Elites behavior is canonical and which is
  LibreEvolve-specific.
  - Paper evidence: `1504.04909__MAP_Elites.pdf` maps elites over
    user-chosen dimensions of variation to illuminate high-performing
    solutions across a behavior space.
  - Current evidence: `MAPElites` hard-codes performance, code length, and
    TF-IDF char-4gram diversity as dimensions.
  - Missing: user-configurable behavior descriptors, phenotype/behavior
    descriptors from evaluator metadata, and diagnostics that show the
    illuminated search space rather than only best/archive cells.

- [ ] Document UCB1 as a heuristic adaptation or adjust it toward canonical
  UCB1.
  - Paper evidence: the UCB1 paper assumes bounded reward distributions and
    analyzes regret using empirical rewards plus an upper-confidence term.
  - Current evidence: `LLMEnsemble` records non-negative fitness deltas, does
    not normalize rewards to a bounded interval, uses a configurable coefficient
    rather than the canonical constant, and increments `total` before
    selection.
  - Missing: reward normalization, explicit initialization/pull-once policy,
    documented coefficient choice, and tests that the implementation matches
    the intended UCB variant.

- [ ] Account for non-mutation LLM calls in ensemble scheduling.
  - Paper evidence: AlphaEvolve uses an ensemble of LLMs to balance candidate
    generation throughput and quality.
  - Current evidence: critique, feedback, and meta-prompt calls share the same
    `LLMEnsemble.generate()` accounting as mutation calls, but only mutation
    calls receive a candidate-improvement reward.
  - Missing: role-specific routing/accounting for generation, critique,
    grading, and meta-prompt calls, plus persisted scheduler diagnostics.

- [x] Tighten inline paper-source comments so they do not imply faithful
  implementations.
  - Evidence: source comments in the diff engine, evaluator, loop, database,
    island model, MAP-Elites, and modular plugin cited paper systems in ways
    that could be read as direct implementations.
  - Status: inline comments now use "inspired by" language or state the local
    limitation directly; the larger implementation gaps remain tracked in the
    paper-specific items above.
  - Required result: keep code comments aligned with the actual behavior, not
    just README/docs marketing language.
