# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

## Missing Roadmap Items

## Existing Items That Need Tightening

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
