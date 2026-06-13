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
