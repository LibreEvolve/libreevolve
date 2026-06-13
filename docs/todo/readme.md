# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

## Feature Claims

- [x] Keep README Appendix B.1-B.3 labels scoped until paper-heading
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.3 are titled `First
    autocorrelation inequality`, `Second autocorrelation inequality`, and
    `Third autocorrelation inequality`, and the constants are `C1`, `C2`, and
    `C3`. The paper does not use `k=3`, `k=4`, or `k=5` labels for these three
    autocorrelation entries.
  - Status: README now states that the Appendix B registry preserves the exact
    B.1-B.3 paper-facing labels and C1-C3 constants separately from internal
    `autocorrelation_bounds_k*` ids. The registry validator and tests reject
    missing label metadata, drifted constants, and public `k=` names.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README Appendix B.8 ratio wording scoped until squared-ratio
      convention provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.8 reports constructions for the
    max/min pairwise-distance ratio, but the numerical values `12.889266112`
    for 16 points in 2D and `4.165849767` for 14 points in 3D are reported
    under a squared-ratio convention, with the geometric ratio obtained by a
    square-root transform.
  - Status: README now states that Appendix B.8 registry evidence preserves the
    raw squared values, square-root-derived ratios, point counts, dimensions,
    prior squared bounds, and comparison policy, while leaving coordinate
    payloads and all-pairs distance certificates open.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README Appendix B.5 source-formulation wording scoped until
      equivalence evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.5 defines the source problem using
    non-negative `f,g: [-1,1] -> [0,1]`, `f + g = 1`, `integral f = 1`,
    zero extension outside `[-1,1]`, and
    `sup_{x in [-2,2]} integral_{-1}^1 f(t) g(x+t) dt`, then uses `[40]` to
    reduce the constant to an infimum over normalized step functions `h` on
    `[0,2]`.
  - Status: README now states that the Appendix B registry preserves the B.5
    source paired-function formulation, zero-extension convention,
    shift-supremum objective, known bounds, `[40]` equivalence, and mapping to
    the normalized `[0,2]` step-function formulation, while the Figure 10
    construction payload remains open.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README Appendix B.6 theorem wording scoped until admissibility
      evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.6 defines `C6` via arbitrarily large
    finite sets `A` and `B`, explicit sumset/difference-set notation,
    `X << Y` and `X >> Y` constants independent of sufficiently large sets,
    `[39, Corollary 3]` for the `4/3` upper bound, `[39, Theorem 1]` for the
    lower-bound method, and a Gyarmati finite-set admissibility condition for
    non-negative integer `U` containing zero.
  - Status: README now distinguishes B.6 theorem-condition evidence from
    witness payload provenance: it names the `C6` source theorem,
    sumset/difference-set definitions, asymptotic notation, source theorem
    anchors, admissible-`U` checks, lower-bound formula, and separate
    `finite_set_witness_boundary`.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README database-output claims scoped to prompt-visible output
      capture versus queryable output indexes.
  - Spec evidence: AlphaEvolve's evolutionary database stores generated
    solutions with evaluation results and program outputs attached, then
    resurfaces useful prior ideas in later generations.
  - Current evidence: README now describes strict evaluator `outputs` /
    `program_output` capture, redaction, truncation, stage output checks,
    bounded prompt-visible program-output summaries,
    `runtime.history.program_output_index`, and valid output-bearing
    candidates contributing to current-run `resurfacing_index`. It also
    documents `resurface_by_program_output()` as exact source-key/hash
    current-run querying, and states that these indexes are not persisted
    database tables, semantic output-similarity indexes, schema-aware output
    retrieval, or replayable sampling engines. README now ties that boundary
    to `papers/program_output_boundary.json`. README also ties bounded
    current-run artifact path/hash/redaction/skipped/stage/content-excerpt
    indexing to `papers/artifact_index_boundary.json`, while keeping durable
    full-content and semantic artifact search out of scope.
  - Required result: continue keeping README wording scoped when durable output
    query tables, schema-aware output retrieval, or semantic output search
    land.

- [ ] Implement README AlphaEvolve Bruhat-interval claims beyond source-scoped
      absence.
  - Spec evidence: arXiv `2601.01235`, `Bruhat intervals that are large
    hypercubes`, says AlphaEvolve-suggested permutations revealed a pattern
    for large Bruhat intervals that are poset hypercubes in `S_n`, later
    proved for general `n`. For powers of `2`, the paper exhibits
    `O(n log n)`-dimensional hypercubes, characterizes vertices as dyadically
    well-distributed permutations, and links the result to Kazhdan-Lusztig
    `R`-polynomial coefficients and lower-bound consequences in cluster
    algebras and Bruhat-graph embeddings. The body identifies the construction
    as bit-reversal endpoints `x_m`/`y_m` whose interval equals the
    dyadically well-distributed permutations `D_m`, with verification through
    Ehresmann matrices, complementary-block flips, and a poset isomorphism to
    a rank `m * 2^(m-1)` hypercube.
  - Current evidence: README now keeps `2601.01235` source-scoped through
    `papers/bruhat_intervals_boundary.json`, which records the missing local
    Bruhat verifier evidence. README documents constructive-math gaps,
    benchmark-report contracts, paper-cache status, and smoke fixtures, but it
    still does not define permutation generators for `S_n`, verify Bruhat
    intervals, check poset-hypercube structure, compute dyadic well-
    distribution predicates, record power-of-two benchmark rows, connect
    outputs to Kazhdan-Lusztig coefficients or cluster-algebra consequences,
    or preserve finite-search versus general-proof status. README also lacks
    source-scoped boundaries for Section 4 AlphaEvolve/FunSearch experiment
    provenance, public `Bruhat-hypercubes` artifact links, model/cost/run
    metadata, bit-reversal lineage and low-discrepancy-literature caveats,
    `R`-polynomial/d-invariant checker formulas, and PDF/arXiv metadata
    caveats.
  - Required result: before README can promote Bruhat intervals, poset
    hypercubes in `S_n`, dyadically well-distributed permutations,
    AlphaEvolve-suggested
    permutation patterns, Kazhdan-Lusztig `R`-polynomials, open Richardson
    cluster-algebra frozen variables, Bruhat graph embeddings, or
    `2601.01235` beyond the source-scoped boundary, local artifacts must show
    permutation schemas, interval witness
    artifacts, hypercube verifier outputs, dyadic checker records, benchmark
    rows, proof-status fields, independent checker outputs, and benchmark
    reports. Avoid implying LibreEvolve supports AlphaEvolve-style Bruhat-
    interval hypercube discovery without those artifacts. README wording should
    also distinguish generic constructive-math search from this paper's
    specific `d`-invariant objective, FunSearch/AlphaEvolve generalizer-mode
    process, bit-reversal theorem proof, public artifact verification, and
    theorem-backed consequences.

- [ ] Implement README global-NLP solver comparison claims beyond source-scoped
      absence.
  - Spec evidence: arXiv `2601.05943`, `Global Optimization for
    Combinatorial Geometry Problems`, asks whether off-the-shelf global
    optimization solvers can match AlphaEvolve benchmark results when hard
    geometry/combinatorial problems are directly formulated as NLPs. Its
    abstract reports straightforward NLP formulations evaluated with
    commercial FICO Xpress and open-source SCIP, reproducing and sometimes
    improving best known and LLM-driven results without solver modifications.
    The body focuses on min-max distance ratio, square/rectangle circle
    packing, and regular-hexagon packing, using Mosel formulations, QCP
    squared-distance constraints, circle center/radius variables, and Farkas-
    multiplier hexagon non-overlap constraints.
  - Current evidence: README now lists `2601.05943` as source-scoped Global
    NLP Optimization comparator context and points to
    `papers/global_nlp_optimization_boundary.json`. It still does not define
    direct NLP formulations for AlphaEvolve benchmark problems, run Xpress or
    SCIP, record solver licenses/versions,
    preserve solver incumbents/bounds/certificates, compare solver outputs
    against AlphaEvolve and literature baselines, or document numerical
    tolerance and reproducibility for direct solver baselines. README also
    lacks source-scoped boundaries for Mosel model artifacts, selected
    distance/circle/hexagon benchmark rows, AlphaEvolve repository validation
    outputs, Table 1-3 comparisons, solver-attribution caveats, dual-bound
    omissions, and commercial-license handling for Xpress.
  - Required result: if README mentions global NLP solvers, FICO Xpress, SCIP,
    direct nonlinear-programming formulations of AlphaEvolve benchmarks,
    solver reproduction of AlphaEvolve discoveries, solver improvements over
    LLM-driven results, or `2601.05943`, keep the wording source-scoped until
    local artifacts can show the paper in the manifest, NLP formulation
    schemas, solver-run records, version/license metadata, incumbent/bound/
    certificate artifacts, tolerance policy, baseline comparisons,
    independent checker outputs, and benchmark reports. Avoid implying
    LibreEvolve supports global-NLP solver comparison for AlphaEvolve
    benchmarks without those artifacts. README wording should also distinguish
    LibreEvolve's LLM evolutionary code search from direct mathematical
    programming baselines unless local reports include exported NLP models,
    solver logs, solution validation, baseline citations, table-level outcome
    rows, and reproducibility/licensing status for both solvers.

- [ ] Implement README post-AlphaEvolve autoconvolution improvement claims
      beyond source-scoped absence.
  - Spec evidence: arXiv `2506.16750`, `An improved example for an
    autoconvolution inequality`, reports a nonnegative step function with
    `575` equally spaced intervals and autoconvolution ratio `>= 0.901564`.
    Its abstract says this improves on DeepMind's AlphaEvolve `50`-interval
    witness with value `>= 0.8962`, and that the improved witness was found by
    simulated annealing and gradient methods rather than LLMs. The body gives
    an exact rational certificate, a finite coefficient-list formula using
    `L_j` convolution samples, public Python/Mathematica code, and Appendix A
    integer coefficients obtained by scaling by `2^24` and rounding.
  - Current evidence: README now lists `2506.16750` as source-scoped
    Autoconvolution context and points to `papers/autoconvolution_boundary.json`.
    It still does not store a 575-interval step-function witness, recompute the
    autoconvolution objective, compare
    the AlphaEvolve 50-interval baseline against the later result, preserve
    non-LLM search provenance, or define a rounding/tolerance rule for
    `0.901564`. README also lacks source-scoped boundaries for the public
    `autoconvolutionHolder` repository, `coeffBL.txt` and `Verify.nb`
    artifacts, row-major coefficient parsing, translation/dilation support
    normalization, Matolcsi-Vinuesa and AlphaEvolve coefficient comparisons,
    integer-arithmetic checker provenance, and NCSU HPC/resource caveats.
  - Required result: if README mentions the improved autoconvolution example,
    the 575-interval witness, the `0.901564` value, the AlphaEvolve
    `0.8962` autoconvolution baseline, simulated annealing, gradient-based
    improvement over AlphaEvolve, or `2506.16750`, keep the wording source-
    scoped until local artifacts can show the paper in the manifest, witness
    payloads, convolution/norm recomputation, objective/tolerance policy,
    baseline comparison rows, non-LLM search provenance, independent checker
    outputs, and benchmark reports. Avoid implying LibreEvolve supports this
    post-AlphaEvolve autoconvolution improvement without those artifacts.
    README wording should also distinguish AlphaEvolve's LLM-generated
    50-interval witness from this later non-LLM 575-interval certificate until
    local artifacts include exact coefficients, exact-rational/decimal checker
    outputs, GitHub artifact hashes, and reproducible Python/Mathematica
    verification.

- [ ] Implement README post-AlphaEvolve sums-and-differences improvement
      claims beyond source-scoped absence.
  - Spec evidence: arXiv `2505.16105`, `Sums and differences of sets
    (improvement over AlphaEvolve)`, by Robert Gerbicz says AlphaEvolve
    improved the lower bound from `theta = 1.14465` to `theta = 1.1584` using
    a set of `54265` integers. The paper improves the bound to
    `theta = 1.173050` with an explicit `U` set containing more than
    `10^43546` elements and uses GMP for fast integer and floating-point
    arithmetic. Its construction defines `W(m, L, B)`, encodes bounded
    coordinates in base `2B + 1`, reports a `theta = 1.162997` small-search
    case at `m = 80`, `L = 64`, `B = 5`, and confirms
    `theta = 1.173050` for `m = 81411`, `L = 65536`, `B = 5`; the paper cites
    GMP code and exact computed values at `https://bit.ly/43mWCVC`.
  - Current evidence: README now mentions `2505.16105` as source-scoped
    context and points to `papers/sums_differences_boundary.json`. It still
    does not store an explicit or compressed `U`-set construction, verify
    sumset/difference-set cardinalities, recompute `theta = 1.173050`,
    compare against the AlphaEvolve `54265`-integer `1.1584` baseline,
    preserve GMP arithmetic provenance, retrieve the cited exact-value
    artifact, preserve the `W(m, L, B)` and base-`2B + 1` construction
    details, or distinguish the later explicit construction from
    AlphaEvolve's LLM-generated witness with local implementation evidence.
  - Required result: if README mentions this sums-and-differences improvement,
    the `1.173050` bound, the huge `U` set, `10^43546`, the AlphaEvolve
    `54265`-integer construction, the `1.1584` or `1.14465` baselines, GMP
    arithmetic, `W(m, L, B)`, base-`2B + 1` encoding, the `(81411, 65536, 5)`
    parameter triple, the cited exact-value payload, or `2505.16105`, keep the
    wording source-scoped until local artifacts can show the paper in the
    manifest, construction payloads, sumset/difference-set verification,
    max-element/q-value checks, `theta` recomputation, tolerance policy,
    baseline comparison rows, arithmetic provenance, independent checker
    outputs, and benchmark reports. Avoid implying LibreEvolve supports this
    post-AlphaEvolve sums-and-differences improvement without those artifacts.

- [ ] Implement README further post-AlphaEvolve sums-and-differences claims
      beyond source-scoped absence.
  - Spec evidence: arXiv `2506.01896`, `Sums and differences of sets: a
    further improvement over AlphaEvolve`, improves on both AlphaEvolve's
    `theta = 1.1584` and the later `2505.16105` explicit-construction result
    `theta = 1.173050`. Its abstract constructs a sequence of `U` sets whose
    limit establishes `theta = 1.173077`. The paper, by Fan Zheng, uses
    large-deviation estimates for `W(m, floor(rm), B)`, a base-`2B + 1`
    integer-image construction, asymptotic bounds on `q(U)`, `s(U)`, and
    `d(U)`, and a MATLAB 2024b optimization over `B`, `r`, and `a`; the
    reported best row is `B = 5` with `theta - 1 = 0.173077279785136` at
    both `1e-8` and `1e-10` tolerances.
  - Current evidence: README now mentions `2506.01896` as source-scoped
    context and points to `papers/sums_differences_sequence_boundary.json`.
    It still does not define a sequence-of-sets construction, preserve
    finite-prefix artifacts, verify limiting lower-bound derivations, preserve
    large-deviation lemma evidence, extract or reimplement the MATLAB
    optimizer, compare against both the AlphaEvolve and `2505.16105`
    baselines, or distinguish asymptotic sequence evidence from finite
    huge-set evidence with local implementation evidence.
  - Required result: if README mentions the further sums-and-differences
    improvement, the `1.173077` bound, a sequence of `U` sets, limiting
    lower-bound constructions, the AlphaEvolve `1.1584` baseline, the
    `2505.16105` `1.173050` baseline, large-deviation estimates, MATLAB
    optimization, the `B = 5` tolerance-sweep result, or `2506.01896`, keep
    the wording source-scoped until local artifacts can show the paper in the
    manifest, sequence schemas, finite-prefix artifacts, limiting-bound
    derivation records, large-deviation checker outputs, MATLAB extraction or
    independent reimplementation, convergence/tail-bound checker outputs,
    baseline comparison rows, independent checker outputs, and benchmark
    reports. Avoid implying LibreEvolve supports this further
    post-AlphaEvolve sums-and-differences improvement without those artifacts.

- [ ] Implement README UCB-style scheduler claims beyond source-scoped
      heuristic routing.
  - Spec evidence: the local `auer-cesa-bianchi-fischer-2002` paper,
    `Finite-time Analysis of the Multiarmed Bandit Problem`, by Peter Auer,
    Nicolo Cesa-Bianchi, and Paul Fischer analyzes UCB1 for arms with reward
    distributions supported in `[0, 1]`, defines regret as expected loss from
    not always playing the best arm, and proves finite-time logarithmic regret
    bounds using empirical reward means, play counts, and a confidence-radius
    index. Theorem 1 bounds regret with the `8 ln(n) / Delta_i` constant and
    the proof uses Chernoff-Hoeffding bounds; the paper notes Theorems 1-3 do
    not need cross-machine independence and only require the per-arm
    conditional-mean condition. UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and
    UCB1-TUNED are separate variants, and UCB1-TUNED has no proven regret
    bound in the paper.
  - Current evidence: README describes LibreEvolve's backend selector as
    `UCB-style`, lists UCB1 as inspiration for heuristic backend routing, and
    points to `papers/ucb1_boundary.json`. README still does not provide local
    scheduler evidence for reward-support assumptions,
    conditional-mean/stationarity assumptions, reward-normalization policy,
    backend-as-arm stability, selected-arm/index telemetry, coefficient
    mapping from canonical UCB1 to LibreEvolve's configurable exploration
    term, metadata-aware `throughput_depth` caveats, or regret-report proof
    status.
  - Required result: when README discusses UCB1, UCB-style routing, backend
    bandits, or scheduler reward, keep wording source-scoped until manifests
    and reports record the `auer-cesa-bianchi-fischer-2002` UCB1 source row,
    bounded-reward normalization,
    conditional-mean/stationarity disclaimer, stable backend-as-arm identity,
    selected-backend/index telemetry, exploration-coefficient mapping, regret
    metrics where applicable, variant unsupported status for UCB2,
    `epsilon_n`-GREEDY, UCB1-NORMAL, and UCB1-TUNED where relevant, and a
    clear statement that heuristic backend routing is not a finite-time-
    regret UCB1 reproduction without those assumptions.

- [ ] Keep README GigaEvo wording scoped until framework-parity evidence
      exists.
  - Spec evidence: local arXiv `2511.17592`, `GigaEvo: An Open Source
    Optimization Framework Powered by LLMs and Evolution Algorithms`, by
    Valentin Khrulkov et al. describes Redis-backed program storage with UUID,
    source code, lifecycle states (`FRESH`, `RUNNING`, `COMPLETE`), metrics,
    genealogical lineage, DAG stage outputs, and optimistic concurrency;
    an `asyncio` DAG execution engine with data-flow and execution-order
    dependencies, caching, and automatic stage skipping; MAP-Elites evolution;
    LangGraph mutation operators; insight generation; bidirectional lineage
    tracking; Hydra configuration; diff and rewrite mutation modes; and
    AlphaEvolve benchmark reproduction experiments. The paper reports
    Heilbronn `n = 11` at `0.0364` vs AlphaEvolve `0.0365`, circle-packing
    reproduction attempts, kissing-number recovery without improvements in
    most dimensions, bin-packing Weibull excess bin usage `0.55%`, and Jigsaw
    prompt/agent evolution with `0.803` test AUC for the evolved agent.
  - Current evidence: README and `papers/README.md` mark GigaEvo as framework
    inspiration only and say Redis lifecycle database, `asyncio` DAG engine,
    insight stage, and concurrent units are not implemented. README now points
    at `papers/gigaevo_framework_boundary.json`, which records source
    metadata, dual GitHub source-link ambiguity, architecture-component rows,
    lifecycle/DAG/lineage missing-evidence keys, Hydra mapping gaps, and
    benchmark-reproduction absence. README still must not imply those artifacts
    exist locally.
  - Required result: if README mentions GigaEvo, Redis lifecycle storage,
    DAG-based evaluation, concurrent units, insight stages, bidirectional
    lineage tracking, LangGraph mutation, or GigaEvo benchmark reproduction,
    keep the wording source-scoped until local manifests and reports include
    executable evidence beyond the `2511.17592` source row and sidecar:
    PDF/code hashes, lifecycle-state schema,
    DAG-stage/dependency records, concurrency/caching telemetry, insight and
    lineage artifacts, Hydra/component-layout mapping, benchmark reproduction
    rows for the named paper tasks, and a clear distinction between
    LibreEvolve's current local runner and GigaEvo framework parity.

- [ ] Keep README CodeEvolve wording scoped until operator and benchmark
      evidence exists.
  - Spec evidence: local arXiv `2510.14150`, `CODE EVOLVE: an open-source
    evolutionary framework for algorithmic discovery and optimization`, by
    Henrique Assumpcao et al. describes islands-based evolution with weighted
    LLM ensembles, inspiration-based semantic crossover, meta-prompting
    exploration, depth-based targeted refinement with `k` nearest ancestors,
    exploration scheduling, sandboxed evaluation, MAP-Elites/CVT-MAP-Elites
    archives, and AlphaEvolve/EoH benchmark plus quality-cost comparisons. It
    defines separate solution and prompt fitness (`fsol`/`fprompt`), reports
    that CODE EVOLVE matches or surpasses AlphaEvolve on `5` of `9`
    AlphaEvolve benchmark instances, shows `CirclePackingSquare(n = 26)`
    `2.63598` vs AlphaEvolve `2.63586` and `n = 32` `2.93956` vs
    AlphaEvolve `2.93794`, and reports Qwen3-Coder-30B cost advantages over
    GEMINI-2.5 such as roughly `$6` vs just under `$35` for the `n = 26`
    circle-packing run.
  - Current evidence: README and `papers/README.md` mark CodeEvolve as
    agentic code-evolution inspiration only, and README now points at
    `papers/codeevolve_boundary.json` for the `2510.14150` source-specific
    boundary. That sidecar keeps prompt/solution fitness, semantic crossover,
    meta-prompting exploration, depth-refinement ancestor context, Plateau
    Scheduler behavior, sandbox parity, MAP-Elites/CVT archive parity,
    benchmark rows, ablations, hyperparameter guidance, and cost-comparison
    claims unavailable until local artifacts prove them.
  - Required result: if README mentions CodeEvolve, inspiration crossover,
    meta-prompting, targeted refinement, modular orchestration,
    context-aware recombination, open-weight cost comparisons, or CodeEvolve
    benchmark results, keep wording source-scoped until manifests and reports
    include the `2510.14150` source row, PDF/code hashes, operator artifacts,
    scheduler traces, prompt/solution fitness metadata, sandbox/runtime-memory
    evidence, MAP-Elites/CVT compatibility reports, AlphaEvolve/EoH benchmark
    rows, ablation/cost reports, hyperparameter defaults, and a clear
    distinction between LibreEvolve's current prompt-program features and
    CodeEvolve framework parity.

- [ ] Keep README ThetaEvolve wording scoped until test-time learning evidence
      exists.
  - Spec evidence: local arXiv `2511.23473`, `ThetaEvolve: Test-time Learning
    on Open Problems`, by Yiping Wang et al. describes an
    AlphaEvolve-inspired dynamic environment with a single LLM, large program
    database, batch sampling, early checks, lazy penalties, reward shaping,
    optional GRPO/RL training at test time, RL-trained checkpoints, and
    open-problem benchmark claims. It reports DeepSeek-R1-0528-Qwen3-8B
    improving `CirclePacking` and `FirstAutoCorrIneq` bounds mentioned in
    AlphaEvolve, including Table 1 rows `2.63598308` vs AlphaEvolve
    `2.63586276` for circle packing and `1.503133` vs AlphaEvolve `1.503164`
    for FACI, plus a `3` second circle-packing program vs ShinkaEvolve's
    roughly `75` second program.
  - Current evidence: README says the ThetaEvolve-inspired `ttt_rl` plugin
    writes clipped-reward training data and is not a real GRPO/RL trainer, and
    now points at `papers/thetaevolve_boundary.json` for the `2511.23473`
    source-specific boundary. That sidecar keeps batch-sampled dynamic
    environments, large database scaling, lazy penalties, reward-shaping
    parameters, GRPO telemetry, checkpoint provenance, evaluator caveats,
    transfer reports, throughput reports, and benchmark comparison claims
    unavailable until local artifacts prove them.
  - Required result: if README mentions ThetaEvolve, test-time learning,
    GRPO/RL training, lazy penalties, reward shaping, batch sampling, large
    program databases, trained checkpoints, or ThetaEvolve benchmark results,
    keep wording source-scoped until manifests and reports include the
    `2511.23473` source row, PDF/code hashes, dynamic-environment metadata,
    batch-sampling records, lazy-penalty and reward-shaping schemas, training
    and checkpoint artifacts, evaluator-compatibility caveats,
    AlphaEvolve/ShinkaEvolve/OpenEvolve comparison rows, database-size and
    batch-throughput ablations, checkpoint-transfer rows, and a clear
    distinction between clipped-reward JSONL export and actual test-time RL.

- [ ] Keep README ImprovEvolve wording scoped until modular-operator execution
      evidence exists.
  - Spec evidence: local arXiv `2602.10233`, `ImprovEvolve: Ask AlphaEvolve
    to Improve the Input Solution and Then Improvise`, by Kravatskiy,
    Khrulkov, and Oseledets evolves a class with `generate_config`, `improve`,
    and `perturb` methods, then executes those methods through a two-stage
    basin-hopping validation loop with scheduled perturbation intensity,
    monotonic acceptance, GigaEvo outer evolution, and benchmark claims for
    hexagon packing and the second autocorrelation inequality. It reports
    Table 1 values including `HEX 11` `3.9245` vs AlphaEvolve `3.9301`,
    `HEX 12` `3.9416` vs AlphaEvolve `3.9419`, and human-edited ACI2
    `0.96258` vs AlphaEvolve `0.96102`; Table 3 additionally tracks HEX
    `13..30` generalization and human-edited variants.
  - Current evidence: README describes the ImprovEvolve-inspired modular
    plugin as static prompt guidance and now points at
    `papers/improvevolve_boundary.json` for the `2602.10233` source-specific
    boundary. That sidecar keeps interface enforcement, basin-hopping records,
    perturbation schedules, human-edited variants, GigaEvo-backbone relation,
    HEX/ACI2 benchmark results, ablations, model/provider provenance, and
    compute-budget claims unavailable until local artifacts prove them.
  - Required result: if README mentions ImprovEvolve, modular search,
    `generate_config`, `improve`, `perturb`, basin-hopping validation,
    scheduled perturbations, `ImprovEvolve+E`, hexagon-packing improvements,
    ACI2 improvements, or GigaEvo-backed modular execution, keep wording
    source-scoped until manifests and reports include the `2602.10233` source
    row, PDF/code hashes, interface schemas, executed validation-loop
    artifacts, perturbation and seed records, human-edit provenance,
    benchmark/baseline rows, ablation and budget reports, model/provider
    provenance, and a clear distinction between static prompt guidance and
    ImprovEvolve execution.

- [ ] Keep README MadEvolve wording scoped until parameter-optimization and
      innovation-report evidence exists.
  - Spec evidence: local arXiv `2602.15951`, `MadEvolve: Evolutionary
    Optimization of Cosmological Algorithms with Large Language Models`,
    presents AlphaEvolve-like scientific algorithm evolution with explicit
    free-parameter tracking, greedy one-shot and autodiff/Adam inner
    optimization, JAX/`vmad` differentiability constraints, hybrid
    MAP-Elites/island/elite population management, UCB-style model routing,
    generated scientific reports, and BAO, 21cm, and tSZ cosmology results.
    It reports Table 1 improvements from `0.752` to `0.924` for standard BAO
    reconstruction, `0.933` to `0.959` for iterative BAO reconstruction,
    `0.743` to `0.971` for 21cm tidal reconstruction, and tSZ loss reduction
    from `0.613` to `0.230`, plus Table 2/3 run and model-contribution
    statistics across `2,126` generated programs.
  - Current evidence: README labels MadEvolve as domain-evolution inspiration
    and now points at `papers/madevolve_boundary.json` for the `2602.15951`
    source-specific boundary. That sidecar keeps parameter schemas, inner
    optimizer records, optimized-value source injection,
    differentiability/operator validation, generated report sections, per-task
    benchmark rows, run statistics, model-contribution statistics, compute
    budgets, overfitting/reward-hacking caveats, hosted report artifacts, and
    public code/source status unavailable until local artifacts prove them.
  - Required result: if README mentions MadEvolve, domain evolution,
    free-parameter optimization, nested optimization, autodiff/JAX/vmad
    support, generated innovation reports, BAO/21cm/tSZ MadEvolve results,
    UCB model-contribution statistics, or MadEvolve public code availability,
    keep wording source-scoped until manifests and reports include the
    `2602.15951` source row, PDF/code hashes, parameter and optimizer schemas,
    executed inner-loop artifacts, differentiability checks, report-generator
    artifacts, benchmark/baseline/result rows, success/improvement/model
    contribution tables, compute environment, task prompts/evaluators,
    reward-hacking and over-parameterization caveats, madevolve.org report
    links, and a clear distinction between LibreEvolve's current generic
    evolution surfaces and MadEvolve execution semantics.

- [ ] Keep README CausalEvolve wording scoped until causal-scratchpad evidence
      exists.
  - Spec evidence: local arXiv `2603.14575v2`, `CausalEvolve: Towards
    Open-Ended Discovery with Causal Scratchpad`, adds causal memory to
    AlphaEvolve-like search: LLM-generated outcome-level factors and executable
    factor code, CausalPlanner MAB interventions over factor directions,
    procedure-level factor discovery from accumulated trials, approximate
    treatment-effect estimates, surprise-pattern detection, abductive reasoning
    for new factors/hypotheses, and four-task comparisons against
    ShinkaEvolve, CausalPlanner(Meta), and COAT. Table 1 reports final-step
    CausalEvolve mean/best values of `0.568`/`0.576` on Hadamard,
    `0.793`/`0.809` on second autocorrelation, `2.476`/`2.564` on circle
    packing, and `38.89`/`40.00` on AIME with Grok-4.1-fast-reasoning.
  - Current evidence: README says the causal plugin is a lightweight
    token-pattern heuristic, not CausalEvolve's causal scratchpad, and now
    points at `papers/causalevolve_boundary.json` for the `2603.14575`
    source-specific boundary. That sidecar keeps POMDP/SCM framing,
    executable outcome factors, directional interventions, procedure factors,
    treatment effects, surprise patterns, abductive hypotheses, benchmark
    rows, ablations, seed/step schedules, and model provenance unavailable
    until local artifacts prove them.
  - Required result: if README mentions CausalEvolve, causal scratchpads,
    outcome-level factors, procedure-level factors, causal planning,
    treatment-effect guidance, surprise-pattern reasoning, abductive causal
    hypotheses, or CausalEvolve benchmark improvements, keep wording
    source-scoped until manifests and reports include the `2603.14575` source
    row, PDF/code hashes, factor-generation prompts, executable factor metrics,
    intervention/action records, scratchpad memory artifacts, procedure-factor
    and treatment-effect tables, abduction outputs, benchmark/baseline/result
    rows, model/seed/step provenance, paper license and code/source status,
    and a clear distinction between fixed token-pattern factor guidance and
    CausalEvolve causal-scratchpad execution.

- [ ] Keep README DeepEvolve wording scoped until cross-file research/debug
      loop evidence exists.
  - Spec evidence: local arXiv `2510.06056v1`, `Scientific Algorithm Discovery
    by Augmenting AlphaEvolve with Deep Research`, augments algorithm evolution
    with deep research through planning, searching, writing proposals with
    pseudo-code, cross-file coding, evaluation, evolutionary selection,
    reflection checkpoints, debugging attempts, and nine benchmark tasks with
    performance/runtime and execution-success tables. Table 2 reports score
    gains such as Molecular Translation `0.1885` to `0.2562`, Circle Packing
    `0.3891` to `2.9806`, and Polymer Prediction `0.6770` to `0.7714`, while
    Table 3 reports debugging success-rate gains such as Open Vaccine `0.130`
    to `0.990` and Circle Packing `0.540` to `1.000`.
  - Current evidence: README says the DeepEvolve-inspired retrieval plugin
    injects best-effort arXiv/web-search summaries and explicitly states that
    it is not a full hypothesis-refinement loop, semantic literature selector,
    source-content verification system, or systematic DeepEvolve-style
    debug/refinement loop. README and the paper index now name
    `papers/deepevolve_boundary.json`, which preserves the `2510.06056`
    source-specific boundary for plan/search/write artifacts, proposal
    pseudo-code, cross-file edit localization, debugging attempts, reflection
    agents, algorithm-description records, nine-task benchmark rows, runtime
    budgets, execution-success ablations, and qualitative idea-scoring claims.
  - Required result: if README mentions DeepEvolve, deep research, proposal
    writing, cross-file code editing, automatic debugging, reflection,
    hypothesis refinement, external research-guided evolution, or DeepEvolve
    benchmark improvements, keep wording source-scoped until runtime manifests
    and reports include plan/search/write proposal artifacts, retrieved-source
    evidence, cross-file coding and debugging records, algorithm-description
    fields, benchmark/baseline/result rows, execution-success and ablation
    tables, runtime/GPU budgets, idea-quality judge records, and a clear
    distinction between bounded retrieval context and DeepEvolve execution
    semantics.

- [ ] Keep README MAP-Elites wording scoped until illumination evidence exists.
  - Spec evidence: local arXiv `1504.04909`, `Illuminating search spaces by
    mapping elites`, by Jean-Baptiste Mouret and Jeff Clune is a preliminary
    draft dated April 21, 2015 with cached SHA-256
    `df7344343b14893a1d79a5459c1f56db50562e246d132cd0269f5201d1455872`.
    It defines MAP-Elites as an illumination algorithm that returns a feature-
    performance map of elites across user-chosen behavior dimensions, with
    explicit feature descriptors, discretized cells, random initialization,
    variation from selected elites, per-cell replacement, and reports for
    global performance, global reliability, precision, and coverage. Its
    experiments include modular neural-network retina maps, simulated soft-
    robot morphology maps, and a real soft-arm map.
  - Current evidence: README describes LibreEvolve's MAP-Elites archive as a
    local 3D quality-diversity grid plus retained elite list, with default
    axes based on archive selection score, complexity, and TF-IDF diversity,
    and configurable descriptor axes over metrics/metadata. Existing README
    TODOs scope descriptor claims to insertion-time coordinates, and README now
    points to `papers/map_elites_illumination_boundary.json` for the
    `1504.04909` source-specific boundary. That sidecar records paper
    pseudocode variables, local archive schemas, and false readiness for full
    `P`/`X` map exports, illumination metrics, visualization/lineage artifacts,
    and domain reproduction. It does not yet prove user-chosen feature
    descriptor contracts, illumination metric reports, feature-performance map
    exports, visualization artifacts, unfilled-cell diagnostics,
    lineage/stepping-stone analysis, benchmark/domain reproduction, or
    descriptor rebin compatibility evidence.
  - Required result: if README mentions MAP-Elites, illumination, behavior
    descriptors, feature-performance maps, archive coverage, reliability,
    precision, elite maps, or paper-faithful quality-diversity behavior, keep
    wording source-scoped until manifests and reports include the executable
    `1504.04909` evidence beyond the sidecar: `b(x)`/`f(x)` schemas,
    dimension/discretization
    records, initialization/variation/replacement records, full map exports,
    coverage/reliability/precision/global-performance reports, visualization
    artifacts for Figures 3-7 style maps, lineage/parent-distance evidence,
    retina/simulated-soft-robot/physical-soft-arm benchmark schedules,
    descriptor compatibility tests, and a clear distinction between
    LibreEvolve's current 3D archive and MAP-Elites illumination semantics.

- [ ] Keep README hardness-of-approximation wording scoped until proof-element
      artifacts exist.
  - Spec evidence: local arXiv `2509.18057v7`, `Reinforced Generation of
    Combinatorial Structures: Hardness of Approximation`, by Ansh Nagda,
    Prabhakar Raghavan, and Abhradeep Thakurta was submitted as v7 on March 9,
    2026 with cached SHA-256
    `32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842`
    and CC BY 4.0 metadata. It uses AlphaEvolve to produce finite proof
    elements for complexity theory, including Ramanujan graph witnesses,
    MAX-k-CUT gadgets, and metric-TSP equation gadgets. It reports
    AlphaEvolve-evolved verifier speedups around `10,000x`, uses judge-LLM plus
    synthetic correctness checks plus human inspection for fast verifiers, and
    separates proxy search scores, independent brute-force verification, human
    inspection, and mathematical lifting/proof arguments.
  - Current evidence: README and `papers/README.md` mark `2509.18057` as
    background only with no graph/certification benchmark.
    `papers/theoretical_cs_sources.json` now includes
    `proof_element_artifact_boundary` for graph/gadget inventories, verifier
    runtime/correctness artifacts, final brute-force verifier outputs,
    theorem/proof cross-links, lifting-framework metadata, human-inspection
    attribution, SOTA/baseline comparison rows, and source-repository status.
    README wording still must not imply those artifacts exist locally.
  - Required result: if README mentions AlphaEvolve complexity-theory results,
    hardness of approximation, MAX-k-CUT, metric TSP, random regular graph
    certification, Ramanujan graph witnesses, proof elements, verifier speedups,
    or theorem-lifting applications, keep wording source-scoped until manifests
    and reports include executable evidence beyond the `2509.18057` source row
    and proof-element boundary: PDF/artifact hashes,
    graph/gadget schemas, verifier-speed and correctness records, judge-LLM and
    human-inspection records, brute-force verification outputs, theorem/proof
    cross-links, baseline/SOTA rows for `0.987`, `0.9649`, and `111/110`,
    source/repository status, human/proof-handoff attribution, and a clear
    distinction between generic LibreEvolve evaluator validation and
    AlphaEvolve-discovered complexity-theory proof elements.

## Architecture Description
