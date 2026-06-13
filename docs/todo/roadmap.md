# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

## Missing Roadmap Items

## Existing Items That Need Tightening

- [ ] Implement post-AlphaEvolve autoconvolution improvement gates beyond
      source-boundary roadmap promotion.
  - Spec evidence: arXiv `2506.16750`, submitted June 20, 2025 and last
    revised August 10, 2025, introduces `An improved example for an
    autoconvolution inequality`. The abstract reports a nonnegative
    `575`-interval step function with autoconvolution ratio `>= 0.901564`,
    improving on AlphaEvolve's `50`-interval `>= 0.8962` result, and says the
    improvement came from simulated annealing and gradient-based methods
    rather than LLMs. The body gives a finite discrete checker using samples
    `L_j`, formula `(3)`, exact rational value
    `96086089410408840289339769 / 106577013451431545242354944`, and public
    Python/Mathematica artifacts in `autoconvolutionHolder`.
  - Current evidence: ROADMAP and `papers/autoconvolution_boundary.json` now
    keep `2506.16750` source-scoped as potential-future-benchmark status until
    local witness artifacts exist. ROADMAP still does not define a
    575-interval witness gate, post-AlphaEvolve baseline comparison, direct
    recomputation of the `0.901564` objective, simulated-annealing/gradient
    provenance records, or documentation rules that separate AlphaEvolve's
    LLM-generated witness from later non-LLM improvements. It also lacks gates
    for public GitHub artifact hashes, integer-coefficient parsing and scaling
    by `2^24`, Python/Mathematica checker parity, Matolcsi-Vinuesa `20`-step
    comparison, AlphaEvolve coefficient-source reversal, translation/dilation
    normalization, NCSU HPC provenance, and exact-rational result rows.
  - Required result: add roadmap gates for `2506.16750`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    step-function witness schema, 575-interval payload artifacts, interval
    grid/spacing records, autoconvolution/norm recomputation records,
    objective and tolerance policy, AlphaEvolve 50-interval baseline value,
    simulated-annealing and gradient-method provenance, prior/current result
    rows, independent checker outputs, and a background-only or benchmark-
    fixture status rule so roadmap claims do not outpace local
    post-AlphaEvolve autoconvolution-improvement support. Roadmap promotion
    should additionally require coefficient-table row-order tests, exact
    fraction and rounded decimal checks, `L_j` sample traces, `L1` equivalence
    checks, initial/refinement/upscale search-stage metadata, repository
    status for `Inital HPC code.py`, `Refine HPC code.py`, `f95.py`,
    `coeffBL.txt`, and `Verify.nb`, and documentation separating theorem
    certificates from search-procedure provenance.

- [ ] Implement post-AlphaEvolve sums-and-differences gates beyond
      source-boundary roadmap promotion.
  - Spec evidence: arXiv `2505.16105`, submitted May 22, 2025, introduces
    `Sums and differences of sets (improvement over AlphaEvolve)` by Robert
    Gerbicz. The abstract says AlphaEvolve used a `54265`-integer set to
    improve the known lower bound from `theta = 1.14465` to `theta = 1.1584`,
    while this paper improves the bound to `theta = 1.173050` using an
    explicit `U` set with more than `10^43546` elements and GMP arithmetic.
    The paper defines `W(m, L, B)` bounded-coordinate sets, a base-`2B + 1`
    integer encoding, sumset/difference-set/max-element formulas, a
    `theta = 1.162997` small-search case for `m = 80`, `L = 64`, `B = 5`,
    and an exact-arithmetic confirmation for `m = 81411`, `L = 65536`,
    `B = 5` with approximate reported values `|U| = 6.314107319e43546`,
    `|U + U| = 3.208492702e61228`, `|U - U| = 6.587554451e75899`, and
    `2 max(U) + 1 = 6.605282799e84780`. It cites GMP code and exact computed
    values at `https://bit.ly/43mWCVC`.
  - Current evidence: ROADMAP and `papers/sums_differences_boundary.json` now
    keep `2505.16105` source-scoped and do not promote it beyond
    potential-future-benchmark status. They still do not define a huge
    explicit `U`-set construction gate, compressed set artifact
    representation, `W(m, L, B)` formula fixture, base-`2B + 1` encoding
    checker, sumset/difference-set verifier, max-element/q-value verifier,
    `theta` recomputation report, exact-value artifact retrieval,
    AlphaEvolve `54265`-integer baseline comparison, GMP arithmetic
    provenance, or documentation rule that separates AlphaEvolve's
    LLM-generated construction from later explicit improvements.
  - Required result: add roadmap gates for `2505.16105`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    explicit `U`-set construction schema, huge-set artifact representation,
    `W(m, L, B)` inclusion-exclusion records, base-`2B + 1` encoding checks,
    `(80, 64, 5)` and `(81411, 65536, 5)` parameter rows, sumset and
    difference-set cardinality records, max-element/q-value and set-size
    metadata, `theta` formula and tolerance policy, exact computed-value
    payload hashes, AlphaEvolve `54265`-integer `1.1584` baseline value,
    previous `1.14465` lower-bound source, GMP/version/arithmetic provenance,
    prior/current result rows, independent checker outputs, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local post-AlphaEvolve sums-and-differences improvement support.

- [ ] Implement further post-AlphaEvolve sums-and-differences sequence gates
      beyond source-boundary roadmap promotion.
  - Spec evidence: arXiv `2506.01896`, submitted June 2, 2025, introduces
    `Sums and differences of sets: a further improvement over AlphaEvolve`.
    The abstract says it improves on both AlphaEvolve's `theta = 1.1584` and
    the subsequent explicit-construction result `theta = 1.173050`, by
    constructing a sequence of `U` sets whose limit establishes
    `theta = 1.173077`. The Fan Zheng paper uses large-deviation estimates
    for `W(m, floor(rm), B)`, the base-`2B + 1` bounded-coordinate integer
    construction, asymptotic bounds on `q(U)`, `s(U)`, and `d(U)`, and a
    MATLAB 2024b tolerance sweep. It reports the restricted optimization over
    `B = 3..10`, `r in (0.5, 2)`, and `a in (0, min(1, 1/r))`, with the best
    row at `B = 5` and `theta - 1 = 0.173077279785136` for `1e-8` and
    `1e-10` tolerances.
  - Current evidence: ROADMAP and
    `papers/sums_differences_sequence_boundary.json` now keep `2506.01896`
    source-scoped and do not promote it beyond potential-future-benchmark
    status. They still do not define a sequence-of-sets construction gate,
    finite-prefix artifact schema, limiting-bound derivation record,
    convergence/tail-bound checker, large-deviation proof-object gate,
    MATLAB-code extraction/reimplementation gate, tolerance-sweep
    reproducibility gate, lineage comparison from AlphaEvolve to
    `2505.16105` to `2506.01896`, or documentation rule that separates finite
    witness verification from asymptotic sequence evidence.
  - Required result: add roadmap gates for `2506.01896`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    sequence-of-`U` construction schema, per-parameter and finite-prefix
    artifacts, limiting lower-bound derivation metadata, convergence/tail-
    bound checker records, large-deviation `I(c, B)` records, asymptotic
    `W(m, floor(rm), B)` count metadata, MATLAB 2024b code provenance,
    independent reimplementation outputs, tolerance-sweep rows for
    `B = 3..10` and `1e-4..1e-10`, sumset/difference-set cardinality records,
    `theta` formula and tolerance policy, AlphaEvolve `1.1584` baseline,
    `2505.16105` `1.173050` baseline, prior/current result rows, independent
    checker outputs, and a background-only or benchmark-fixture status rule
    so roadmap claims do not outpace local further post-AlphaEvolve
    sums-and-differences sequence support.

- [ ] Implement UCB1 finite-time bandit gates beyond source-boundary roadmap
      promotion.
  - Spec evidence: the local `auer-cesa-bianchi-fischer-2002` PDF,
    `Finite-time Analysis of the Multiarmed Bandit Problem`, by Peter Auer,
    Nicolo Cesa-Bianchi, and Paul Fischer studies the exploration/
    exploitation dilemma for multi-armed bandits, defines regret as expected
    loss from not always playing the best arm, and proves UCB1 finite-time
    logarithmic regret for arbitrary reward distributions with support in
    `[0, 1]` using play counts, empirical reward means, and a confidence-
    radius index. Theorem 1 gives the `8 ln(n) / Delta_i` suboptimal-pull
    constant and a finite-time regret bound; the paper also says Theorems 1-3
    do not require cross-machine independence and only need a per-arm
    conditional-mean assumption. UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and
    UCB1-TUNED are separate variants, with UCB1-TUNED explicitly not given a
    regret proof.
  - Current evidence: ROADMAP and `papers/ucb1_boundary.json` now keep
    LibreEvolve's UCB-style backend routing source-scoped and warn that
    canonical UCB1 assumptions, calibrated reward scaling, and regret bounds
    are not proven. They still do not provide runtime scheduler evidence for
    bounded-support and conditional-mean/stationarity assumptions, theorem
    constants, reward normalization, stable arm identity, selected-arm/index
    telemetry, coefficient mapping, role-scoped and metadata-aware selection
    caveats, or proof-scope metadata.
  - Required result: add roadmap gates for `auer-cesa-bianchi-fischer-2002`:
    paper/source manifest entry, PDF/cache hash, source-license or mirror
    status, UCB1 theorem-scope fields, reward-support normalization,
    stable backend-as-arm identity, conditional-mean/stationarity disclaimers,
    selected-backend/index traces, canonical-index and exploration-coefficient
    mapping, regret report fields when applicable, unsupported status for
    UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and UCB1-TUNED, proof-status
    metadata for `throughput_depth`, and README/papers/code wording that keeps
    current backend scheduling heuristic until canonical UCB1 assumptions and
    finite-time-regret evidence are validated.

- [ ] Implement GigaEvo framework gates beyond source-boundary roadmap
      promotion.
  - Spec evidence: local arXiv `2511.17592`, `GigaEvo: An Open Source
    Optimization Framework Powered by LLMs and Evolution Algorithms`, by
    Valentin Khrulkov et al. presents an AlphaEvolve-inspired framework with
    Redis-backed evolutionary units, `asyncio` DAG processing, MAP-Elites
    evolution, LangGraph mutation, generated insights, bidirectional lineage
    tracking, Hydra configuration, and benchmark experiments against
    AlphaEvolve problem families. Its program records carry UUID, source,
    lifecycle state (`FRESH`, `RUNNING`, `COMPLETE`), metrics, genealogy, and
    DAG outputs; its DAG supports validation/execution/complexity/insight/
    lineage/mutation-context stages with caching and automatic stage skipping.
    It reports single-island experiments with `Qwen3-235B-A22B-Thinking-2507`,
    Heilbronn `0.0364` vs AlphaEvolve `0.0365`, circle-packing attempts for
    `n = 26` and `n = 32`, kissing-number recovery without improvements in
    most dimensions, bin-packing `0.55%` Weibull excess usage, and Jigsaw
    prompt/agent evolution with `0.803` test AUC.
  - Current evidence: ROADMAP tells readers to keep GigaEvo features labeled
    as inspired unless the paper behavior is actually implemented, and
    `papers/README.md` marks Redis lifecycle database, `asyncio` DAG engine,
    insight stage, and concurrent units as absent. The committed
    `papers/gigaevo_framework_boundary.json` sidecar now defines
    `2511.17592`-specific gates for source metadata, dual GitHub source-link
    status, architecture components, lifecycle/DAG/lineage gaps,
    Hydra/problem-layout parity, and benchmark reproduction. Roadmap still
    lacks executable code repository status, architecture-component parity,
    lifecycle-state persistence, DAG-stage dependency/caching evidence,
    lineage/insight artifacts, and benchmark-reproduction reports.
  - Required result: implement roadmap gates beyond the sidecar:
    source-license and code-artifact status, Redis-vs-local-storage boundary,
    program lifecycle state model, DAG topology/stage-output/caching records,
    concurrency telemetry, insight and
    ancestor/descendant lineage-analysis artifacts, mutation-operator
    provenance, Hydra/component-configuration mapping, MAP-Elites/island
    compatibility reports, AlphaEvolve benchmark reproduction rows plus
    bin-packing and prompt/agent rows where referenced, source-code URL
    disambiguation for the AIRI/FusionBrainLab links, and README/papers/code
    wording that keeps GigaEvo as framework inspiration until local evidence
    proves otherwise.

- [ ] Implement CodeEvolve operator and benchmark gates beyond source-boundary
      roadmap promotion.
  - Spec evidence: local arXiv `2510.14150`, `CODE EVOLVE: an open-source
    evolutionary framework for algorithmic discovery and optimization`, by
    Henrique Assumpcao et al. describes islands-based genetic search, weighted
    LLM ensembles, inspiration-based semantic crossover, meta-prompting,
    depth-based targeted refinement, exploration scheduling, sandboxed
    evaluation, MAP-Elites/CVT archives, and AlphaEvolve/EoH benchmark plus
    quality-cost comparisons. It defines prompt/solution fitness, Algorithm 1
    exploitation/exploration, Plateau Scheduler, rank-based inspirations,
    elitist migration, runtime/memory-bounded evaluation, and default guidance
    including `5` or `10` islands, `200` or `250` epochs, ancestor depth
    `3..5`, `2..3` inspirations, migration rate `0.1`, and exploration rate
    `0.2..0.5`. Table 1 says CODE EVOLVE matches or surpasses AlphaEvolve on
    `5` of `9` instances, and Table 2 records Qwen3-Coder-30B vs GEMINI-2.5
    cost/time comparisons.
  - Current evidence: ROADMAP says CodeEvolve features should remain labeled
    as inspired unless the paper behavior is actually implemented, and now
    names `papers/codeevolve_boundary.json` as the source-specific gate for
    `2510.14150`. The sidecar records source metadata, license metadata,
    linked code/experiment URLs, component rows, required future evidence
    fields, and missing-evidence keys while keeping prompt/solution dual
    fitness, semantic crossover, meta-prompting, depth-refinement context,
    exploration-scheduler traces, sandbox parity, MAP-Elites/CVT archive
    behavior, benchmark rows, ablations, hyperparameter defaults,
    open-framework comparisons, and quality-cost comparison evidence as future
    gates.
  - Required result: add roadmap gates for `2510.14150`: paper/source manifest
    entry, PDF/cache hash, source-license and code-artifact status,
    islands/population metadata, prompt/solution fitness records, weighted
    ensemble and model-cost telemetry, inspiration-crossover and
    meta-prompting artifacts, targeted-refinement ancestor context,
    exploration-scheduler traces, sandbox runtime/memory evidence,
    MAP-Elites/CVT archive compatibility, AlphaEvolve/EoH benchmark and
    ablation/cost rows, OpenEvolve/ShinkaEvolve comparison rows,
    LLM-backbone sensitivity rows, hyperparameter-guidance records, and
    README/papers/code wording that keeps CodeEvolve as agentic code-evolution
    inspiration until local evidence proves operator and benchmark parity.

- [ ] Implement ThetaEvolve test-time learning gates beyond source-boundary
      roadmap promotion.
  - Spec evidence: local arXiv `2511.23473`, `ThetaEvolve: Test-time Learning
    on Open Problems`, by Yiping Wang et al. was submitted as arXiv v1 on
    November 28, 2025 and describes a dynamic program-evolution environment
    with a single LLM, large program database, batch sampling, early checks,
    lazy penalties, optional reward shaping, GRPO/RL training at test time,
    RL-trained checkpoints, and AlphaEvolve-related open-problem benchmark
    claims. It reports OpenEvolve-based evaluation with `slime` RL training,
    `B = 32`, `n = 16`, `16384` response tokens, rollout temperature `1.0`,
    `16` concurrent verifier programs, GRPO with asymmetric clipping
    (`0.2`/`0.28`), learning rate `1e-6`, weight decay `0.1`, and no KL or
    entropy regularization.
  - Current evidence: ROADMAP says ThetaEvolve features should remain labeled
    as inspired unless the paper behavior is actually implemented, and now
    names `papers/thetaevolve_boundary.json` as the source-specific gate for
    `2511.23473`. The sidecar records source metadata, CC-BY license metadata,
    linked code URL, dynamic-environment component rows, required future
    evidence fields, and missing-evidence keys while keeping batch-sampling
    evidence, database-scaling reports, lazy-penalty and reward-shaping
    semantics, GRPO training telemetry, checkpoint lifecycle,
    transfer/generalization reports, SGLang/vLLM-style throughput reports,
    evaluator caveats, and benchmark comparisons as future gates.
  - Required result: add roadmap gates for `2511.23473`: paper/source manifest
    entry, PDF/cache hash, source-license and code-artifact status,
    single-LLM/database/batch-sampling metadata, early-check and lazy-penalty
    schemas, reward-shaping parameters, GRPO/RL training-run records,
    generated-sample and compute-budget telemetry, checkpoint/adaptor
    lifecycle, inference-with-trained-checkpoint and transfer reports,
    task/evaluator compatibility notes, AlphaEvolve/ShinkaEvolve/OpenEvolve
    comparison rows, Table 1/2/9 main benchmark rows, Table 3 static/format
    reward baselines, Table 4/10 database ablations, Table 5/6 pipeline
    throughput rows, Table 7/8 reward-shaping configuration rows, and
    README/papers/code wording that keeps ThetaEvolve as test-time-training
    inspiration until local evidence proves actual test-time learning support.

- [ ] Implement ImprovEvolve modular-operator gates beyond source-boundary
      roadmap promotion.
  - Spec evidence: local arXiv `2602.10233`, `ImprovEvolve: Ask AlphaEvolve
    to Improve the Input Solution and Then Improvise`, by Kravatskiy,
    Khrulkov, and Oseledets was submitted as arXiv v1 on February 10, 2026 and
    replaces direct solution-generation with an evolved
    `generate_config`/`improve`/`perturb` class executed by a two-stage
    basin-hopping validation loop with multi-seed initialization, scheduled
    perturbations, monotonic acceptance, GigaEvo outer evolution, and HEX/ACI2
    benchmark claims including `ImprovEvolve+E`. It uses Gemini 3 Pro to
    generate/refine `5` initial programs, Gemini 3 Flash Preview through
    OpenRouter for evolution, GigaEvo default prompts/stages, a single-island
    MAP-Elites archive with `150` fitness bins, `elites = 6`, `parents = 2`,
    `offspring = 10`, and CPU-parallel program execution during evolution.
  - Current evidence: ROADMAP says ImprovEvolve features remain inspired unless
    paper behavior is implemented, and now names
    `papers/improvevolve_boundary.json` as the source-specific gate for
    `2602.10233`. The sidecar records source metadata, rights metadata,
    linked-code status, component rows, required future evidence fields, and
    missing-evidence keys while keeping interface enforcement, validation-loop
    execution, perturbation schedules, inner/outer loop separation, human-edit
    provenance, GigaEvo dependency/backbone status, model/provider provenance,
    HEX/ACI2 benchmark rows, ablations, and budget evidence as future gates.
  - Required result: add roadmap gates for `2602.10233`: paper/source manifest
    entry, PDF/cache hash, ACM/preprint rights and linked-code status,
    `generate_config`/`improve`/`perturb` interface schema, Stage A/B runner,
    seed counts, basin-hopping rounds, perturbation schedules, monotonic
    acceptance/incremental improvement records, GigaEvo/backbone metadata,
    Gemini/OpenRouter model provenance, human-edited variant attribution, HEX
    and ACI2 benchmark/baseline/result rows, Table 2 hyperparameter rows,
    Table 3 generalization rows, Table 4 Stage A/B and LLM-edit ablation rows,
    CPU/GPU timeout/compute budgets, wall-clock budget rows (`~10h` HEX,
    `~40h` ACI2), and README/papers/code wording that keeps ImprovEvolve as
    modular-search inspiration until local execution semantics and benchmark
    evidence are validated.

- [ ] Implement MadEvolve parameter-optimization gates beyond source-boundary
      roadmap promotion.
  - Spec evidence: local arXiv `2602.15951`, `MadEvolve: Evolutionary
    Optimization of Cosmological Algorithms with Large Language Models`, by
    Tianyi Li, Shihui Zang, and Moritz Munchmeyer was submitted as arXiv v1 on
    February 17, 2026 and adapts AlphaEvolve-style evolution to scientific
    algorithms with nested free-parameter optimization, greedy one-shot
    derivative-free search, autodiff/Adam tuning for differentiable JAX/`vmad`
    programs, hybrid MAP-Elites/island/elite population management, UCB model
    routing, diff/full/synthesis mutation modes, automated scientific reports,
    and BAO, iterative BAO, 21cm, and tSZ benchmark claims. It describes a
    three-stage report generator (`lineage extraction`, `comparative analysis`,
    and `synthesis`) and a five-island heterogeneous LLM ensemble with UCB
    model selection.
  - Current evidence: ROADMAP says MadEvolve features remain inspired unless
    paper behavior is implemented, and now names `papers/madevolve_boundary.json`
    as the source-specific gate for `2602.15951`. The sidecar records source
    metadata, madevolve.org/GitHub link status, component rows, required future
    evidence fields, and missing-evidence keys while keeping parameter schemas,
    inner optimizer execution, differentiability/operator constraints,
    optimized-value source injection, per-task cosmology fixtures, generated
    reports, run statistics, model-contribution statistics, compute
    environment, reward-hacking diagnostics, hosted report-link validation,
    and over-parameterization/generalization evidence as future gates.
  - Required result: add roadmap gates for `2602.15951`: paper/source manifest
    entry, PDF/cache hash, madevolve.org and GitHub source status,
    framework-vs-application split, parameter-declaration and parameter-meaning
    schemas, one-shot/grid/Latin-hypercube/Bayesian and autodiff/Adam optimizer
    records, inner/outer budget accounting, JAX/vmad differentiability
    validation, optimized-value source-injection provenance, BAO/iterative
    BAO/21cm/tSZ task prompts and evaluator fixtures, training/validation/test
    split provenance, generated lineage/comparative-analysis/synthesis report
    artifacts, Table 1 benchmark rows, Table 2 success/improvement statistics,
    Table 3 model-contribution statistics, compute environment, reward-hacking
    and mode-collapse diagnostics, Quijote/LDL/vmad provenance, hosted
    report-artifact checks, and README/papers/code wording that keeps
    MadEvolve as background until local evidence proves those semantics.

- [ ] Implement CausalEvolve causal-scratchpad gates beyond source-boundary
      roadmap promotion.
  - Spec evidence: local arXiv `2603.14575v2`, `CausalEvolve: Towards
    Open-Ended Discovery with Causal Scratchpad`, by Yongqiang Chen et al. was
    submitted as arXiv v1 on March 15, 2026 and revised as v2 on March 29,
    2026. It models evolve-based scientific discovery as a POMDP over hidden
    scientific knowledge, uses SCM intervention language for program
    evaluation, and introduces a causal scratchpad with LLM-generated
    outcome-level factors, CausalPlanner factor-direction interventions,
    procedure-level factor discovery, approximate treatment effects,
    surprise-pattern detection, abductive hypothesis generation, and four-task
    benchmark comparisons. The CausalPlanner action space is `(factor, +1)` or
    `(factor, -1)`, inspiration programs are sorted by selected factor
    direction, rewards use `(child_score - tau * best_so_far)+`, and random
    actions are alternated for `K` iterations with currently best actions for
    the next `K` iterations.
  - Current evidence: ROADMAP says CausalEvolve features remain inspired unless
    paper behavior is implemented, and now names
    `papers/causalevolve_boundary.json` as the source-specific gate for
    `2603.14575`. The sidecar records source metadata, CC BY-NC-SA license,
    no-dedicated-code status, component rows, required future evidence fields,
    and missing-evidence keys while keeping POMDP/SCM-scoped task records, LLM
    factor-generation prompts, executable outcome-factor code, intervention
    actions, inspiration-sorting traces, procedure-factor extraction,
    treatment-effect estimates, surprise-pattern and abductive-reasoning
    artifacts, benchmark rows, ablations, seed/step schedules, model
    provenance, and environment-shift/generalization caveats as future gates.
  - Required result: add roadmap gates for `2603.14575`: paper/source manifest
    entry, PDF/cache hash, code/source status, causal scratchpad schema,
    POMDP/SCM and environment metadata, outcome-factor and executable
    factor-code contracts, CausalPlanner action/reward policy with tau and K
    parameters, inspiration-selection records, procedure-factor extraction
    artifacts, approximate treatment-effect reports, surprise-pattern detector
    outputs, abductive hypothesis/factor lifecycle, scratchpad replay
    artifacts, Hadamard/autocorrelation/circle-packing/AIME benchmark rows,
    ShinkaEvolve/CausalPlanner(Meta)/COAT comparison rows, Grok-4.1-FR model
    provenance, seed and step schedules, and README/papers/code wording that
    keeps CausalEvolve as causal-guidance inspiration until local evidence
    proves causal-scratchpad semantics. Roadmap result rows must include
    Table 1 final-step comparisons for Hadamard, second autocorrelation,
    circle packing, and AIME, plus CC BY-NC-SA license and no-dedicated-code-
    link status.

- [ ] Implement DeepEvolve cross-file research/debug-loop gates before
      roadmap promotion.
  - Spec evidence: local arXiv `2510.06056v1`, `Scientific Algorithm Discovery
    by Augmenting AlphaEvolve with Deep Research`, by Gang Liu et al. was
    submitted on October 7, 2025 and combines algorithmic deep research and
    evolution through planning, searching, writing, cross-file coding,
    evaluation, and evolutionary selection. It also adds reflection, debugging
    attempts from execution feedback, algorithm-description records,
    evolutionary database inspirations, MAP-Elites/island sampling, and
    effectiveness/runtime/debugging ablations over nine scientific benchmark
    tasks. The workflow explicitly uses a debugger template for multi-file
    Python codebases, `DEEPEVOLVE` edit blocks, score-zero fallback after a
    debugging budget, and 30-minute single-GPU constraints on several tasks.
  - Current evidence: ROADMAP tracks DeepEvolve-inspired retrieval only as
    bounded provenance moving toward audit-grade source integrity, README says
    the plugin is best-effort retrieval context rather than a systematic
    DeepEvolve debug/refinement loop, and `papers/deepevolve_boundary.json`
    now carries the source-specific absence boundary for the six-module
    workflow, proposal writing, cross-file coding, debugging-budget execution
    traces, reflection checkpoints, algorithm-description metadata,
    source/repository status, nine-task benchmark reports, runtime/GPU budgets,
    qualitative idea-scoring records, and deep-research ablations.
  - Required result: implement roadmap gates for `2510.06056`: problem/input
    and user-instruction schemas, plan/search/write proposal records,
    pseudo-code artifacts, retrieved-source provenance, cross-file
    delimiter/localization policy, self-reflection and debugging attempt
    records, execution warning/error traces, score-zero fallback semantics,
    evolutionary database and inspiration/MAP-Elites compatibility reports,
    Table 1 task/metric rows, Table 2 performance/runtime rows, Table 3
    debugging success-rate rows, Figure 3 idea-quality judge records,
    30-minute/single-GPU budget evidence, Table 4 deep-research ablation rows,
    Appendix C user-query/hyperparameter records, and README/papers/code
    wording that keeps DeepEvolve as retrieval/debug-loop inspiration until
    local execution evidence proves those semantics.

- [ ] Implement MAP-Elites illumination-algorithm gates beyond source-boundary
      roadmap promotion.
  - Spec evidence: local arXiv `1504.04909`, `Illuminating search spaces by
    mapping elites`, by Jean-Baptiste Mouret and Jeff Clune is a preliminary
    draft dated April 21, 2015 with cached SHA-256
    `df7344343b14893a1d79a5459c1f56db50562e246d132cd0269f5201d1455872`.
    It defines MAP-Elites as a feature-performance map over user-chosen
    dimensions of variation. The simple algorithm maintains maps `P` and `X`,
    initializes with random solutions, repeatedly selects an elite from the map,
    applies random variation, computes feature descriptor `b(x)` and
    performance `f(x)`, and replaces a cell occupant only when the new
    candidate improves that cell. The paper evaluates illumination with global
    performance, global reliability, precision, and coverage over neural
    networks, simulated soft robots, and a physical soft arm.
  - Current evidence: ROADMAP describes a configurable local MAP-Elites archive
    and tracks stable descriptor/rebin gaps, while `papers/README.md` says the
    default local axes are selection score, serialized-workspace complexity,
    and TF-IDF diversity. The committed
    `papers/map_elites_illumination_boundary.json` sidecar now records the
    `1504.04909` source metadata, local PDF hash, preliminary-draft/cache
    status, paper pseudocode variables, local archive schemas, and false
    readiness for full map exports, illumination metrics, and paper-domain
    reproduction. Roadmap still lacks executable gates for explicit
    feature-descriptor schemas, user-chosen dimension semantics,
    initialization/variation evidence, full feature-performance map exports,
    unfilled-cell diagnostics, illumination metric reports, visualization
    artifacts, parent-distance/lineage stepping-stone analysis,
    benchmark/domain reproduction, and descriptor compatibility tests.
  - Required result: implement roadmap gates for `1504.04909` beyond the
    sidecar: executable `b(x)`/`f(x)` contracts, dimension declaration and
    discretization policy, random-initialization and variation policy,
    per-cell replacement records, `P`/`X` feature-
    performance map exports, empty/unfillable cell diagnostics, coverage/global
    reliability/precision/global-performance reports, heatmap/visualization
    artifacts, lineage parent-cell distance reports, retina and robot
    experiment schedules, descriptor-model compatibility and rebin validation,
    NS+LC/MOLE/random/traditional-EA/EA+D/grid-search comparison context,
    benchmark-domain notes, preliminary-draft caveat, and README/papers/code
    wording that keeps current 3D archive support separate from full
    MAP-Elites illumination evidence.

- [ ] Implement hardness-of-approximation proof-element gates beyond
      source-boundary roadmap promotion.
  - Spec evidence: local arXiv `2509.18057v7`, `Reinforced Generation of
    Combinatorial Structures: Hardness of Approximation`, by Ansh Nagda,
    Prabhakar Raghavan, and Abhradeep Thakurta was submitted as v7 on March 9,
    2026 with cached SHA-256
    `32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842`
    and CC BY 4.0 metadata. It reports AlphaEvolve-discovered Ramanujan graph
    witnesses, MAX-3-CUT/MAX-4-CUT gadget reductions, metric-TSP equation
    gadgets, evolved faster verifier code, final brute-force verification of
    discovered gadgets, and mathematical lifting from finite structures to
    theorem statements.
  - Current evidence: ROADMAP has a theoretical-CS source-tracking note and
    `papers/README.md` labels `2509.18057` background-only with no graph/
    certification benchmark. `papers/theoretical_cs_sources.json` now includes
    a nested `proof_element_artifact_boundary` for the `2509.18057` graph/
    gadget/verifier/theorem-lifting evidence still missing. Roadmap still lacks
    executable graph/gadget artifact schemas, witness inventories, verifier
    APIs, synthetic correctness datasets, evolved-verifier runtime telemetry,
    judge-LLM/human-inspection records, brute-force final verification outputs,
    theorem/lemma/proof cross-links, proof-lifting metadata, source/artifact
    status, and SOTA comparison rows.
  - Required result: implement roadmap gates beyond the source sidecar:
    code/artifact availability, Ramanujan graph witness schema and Table 1
    certification rows, MAX-k-CUT gadget schema with
    Appendix C edge lists, TSP/MWST equation-gadget schema with Appendix D edge
    lists, verifier contracts, evolved-verifier speedup reports, synthetic
    correctness-check dataset provenance, judge-LLM and human-inspection
    attribution, independent brute-force verifier artifacts, theorem/result/
    lifting metadata, baseline/SOTA comparison rows for MAX-4-CUT, MAX-3-CUT,
    and metric TSP, proof-handoff status, extracted-link/source-repository
    status, and README/papers/code wording that keeps hardness-of-approximation
    proof-element support background-only until local execution, artifact, and
    verification evidence proves those semantics.
