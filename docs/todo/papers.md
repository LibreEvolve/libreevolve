# Papers Todo: Reference and Specification Gaps

This list tracks mismatches discovered while reviewing the local `papers/`
directory and using the AlphaEvolve paper as the primary specification.

## AlphaEvolve Paper Requirements Not Yet Implemented

- [x] Task specification API with evolve-block markers.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: users mark code blocks to evolve inside a larger skeleton.
  - Status: implemented for Python single-file and local workspace candidates
    in `libreevolve/core/candidate.py`; arbitrary-language runners remain open.

- [x] Rich prompt sampler.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompts may include previous solutions, system instructions,
    explicit context, stochastic formatting, rendered evaluation results, and
    meta-prompt evolution.
  - Status: implemented prompt templates, deterministic local context files
    including PDF extraction, stochastic variants, rendered evaluator output,
    and local prompt-program selection, scoring, lineage, and optional LLM
    mutation.

- [x] Output modes beyond SEARCH/REPLACE diffs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: diff blocks are default, but AlphaEvolve can ask for a complete
    code block when appropriate.
  - Status: implemented `diff` and `full` mutation modes.

- [x] Frontier model ensemble scheduling.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: combine a fast, lower-latency model for breadth with a stronger
    model for depth.
  - Status: added experimental `throughput_depth` scheduling metadata layered
    over UCB-style scores.

- [x] Configurable evaluation cascades.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: users can specify increasing-difficulty test ensembles and
    early-stage pruning.
  - Status: added configurable local validator stages with distinct entrypoints,
    thresholds, seeded samples, retries, stage context, and timeouts.
    Distributed/parallel evaluator nodes remain open.

- [ ] LLM-generated feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: optional LLM graders can score hard-to-capture properties or
    discard candidates.
  - Current gap: there is no standard LLM feedback evaluator interface.

- [ ] Parallelized evaluation and asynchronous throughput.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: expensive evaluations can be parallelized, and the whole
    pipeline runs as an async controller with LLM samplers and evaluation nodes.
  - Current gap: `evolve()` is synchronous and evaluates one candidate at a time.

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

## Local Paper Corpus Issues

- [x] Decide and document the paper corpus source of truth.
  - Evidence: `papers/download_manifest.csv` lists 24 downloaded papers, while
    the README claims 23 references.
  - Required result: update README badges/text and possibly add a
    `papers/README.md` that explains why each PDF is present.

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

## Paper-Inspired Feature Claims Needing Correction

- [ ] Rename the current CausalEvolve plugin or implement the paper's causal
  scratchpad.
  - Paper evidence: `2603.14575__CausalEvolve.pdf` describes LLM-assisted
    causal factor identification, outcome-level factors, surprise-pattern
    inspection, and abductive reasoning to hypothesize new factors during
    evolution.
  - Current evidence: `libreevolve/plugins/causal.py` uses regex factor
    detection over changed diff tokens and UCB1-like reward accounting.
  - Missing: LLM causal scratchpad, POMDP/causal framing, initial factor
    discovery, surprise-pattern inspection, abductive factor creation, and
    structured causal knowledge reuse.

- [ ] Rename the current DeepEvolve plugin or implement DeepEvolve's retrieval,
  cross-file editing, and debugging loop.
  - Paper evidence: `2510.06056__DeepEvolve.pdf` integrates external knowledge
    retrieval, cross-file code editing, systematic debugging, hypothesis
    refinement, implementation, and testing in each iteration.
  - Current evidence: `libreevolve/plugins/deep_research.py` performs a generic
    arXiv Atom search every N generations and injects short summaries into the
    prompt.
  - Missing: broad external retrieval, source ranking, hypothesis synthesis,
    implementation/refinement loop, systematic debugging, cross-file editing,
    and benchmark-grounded result validation.

- [ ] Rename the current ImprovEvolve plugin or implement the actual
  generate/improve/perturb parameterization and search dynamics.
  - Paper evidence: `2602.10233__ImprovEvolve.pdf` evolves a class/interface
    with `generate_config`, `improve`, and `perturb`, then approaches optima by
    scheduled basin-hopping-style application of `improve()` and `perturb()`.
  - Current evidence: `libreevolve/plugins/modular.py` injects a static prompt
    block asking for those method names.
  - Missing: enforced interface, evaluator support for the interface,
    iterative improve/perturb execution, perturbation-intensity scheduling, and
    benchmark-specific search loop.

- [ ] Rename the current ThetaEvolve plugin or implement batch sampling,
  dynamic RL training, and reward shaping.
  - Paper evidence: `2511.23473__ThetaEvolve.pdf` describes a single-LLM
    framework with a large program database, batch sampling, lazy penalties,
    optional reward shaping, and reinforcement learning at test time.
  - Current evidence: `libreevolve/plugins/ttt_rl.py` writes
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
