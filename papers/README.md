# Local Paper Cache

This directory contains 24 locally cached papers plus download manifests. The
cache is used as research context for LibreEvolve; it is not a claim that every
paper is fully implemented.

## Implementation status

| ID | Title | Role | Current LibreEvolve status |
|---|---|---|---|
| 2506.13131 | AlphaEvolve | Primary specification target | Partially implemented: evolve blocks, local workspace candidates, mutation modes including canonical SEARCH/REPLACE diff compatibility, structured evaluator results, local evaluation cascades, metric normalization, prompt sampler/context ingestion, meta-prompt templates, synchronous critique/feedback, manifests, circle packing, and a small matrix smoke benchmark. Flexible non-code candidate abstractions, custom LLM backend registration, proposal-rationale capture, failed-trial memory, richer prompt rendering of execution outputs, async workers, run-wide compute-budget accounting, true multi-objective search, queryable evolutionary database, full-workspace export/resume, run-identity/evaluator-provenance hardening, seeded replay/lineage-id determinism, strict scalar metric validation, feedback calibration, role-specific LLM accounting, config validation, benchmark validator hardening, equal-budget ablation reporting, and stronger AlphaEvolve-scale benchmarks remain open. |
| 1504.04909 | MAP-Elites | Foundational archive algorithm | Implemented as a fixed 3D archive over normalized fitness, code length, and TF-IDF diversity; user-defined behavior descriptors remain open. |
| auer-cesa-bianchi-fischer-2002 | UCB1 finite-time analysis | Foundational bandit policy | Implemented as a heuristic UCB-style backend router over fitness improvements; reward normalization/canonical regret assumptions are documented gaps. |
| 2511.17592 | GigaEvo | Framework inspiration | Not implemented as described: no Redis lifecycle database, asyncio DAG engine, insight stage, or concurrent units. Diff/full mutation modes are partially present. |
| 2510.14150 | CodeEvolve | Agentic code-evolution inspiration | Not implemented as described: no crossover, targeted refinement, modular orchestration, or adaptive meta-prompting. |
| 2511.23473 | ThetaEvolve | Test-time training inspiration | Only inspired export exists through `ttt_rl`; no online RL/GRPO training loop. |
| 2602.10233 | ImprovEvolve | Modular search inspiration | Only inspired prompt guidance exists; no enforced generate/improve/perturb execution loop. |
| 2602.15951 | MadEvolve | Domain evolution inspiration | Background only; no free-parameter optimization or innovation report. |
| 2603.14575 | CausalEvolve | Causal-guidance inspiration | Only token-pattern outcome-factor guidance exists; no LLM causal scratchpad. |
| 2510.06056 | DeepEvolve | Retrieval/debug loop inspiration | Only simple arXiv/web-search context exists; no cross-file editing or systematic debugging loop. |
| 2601.21096 | Magellan | Agent/research workflow context | Background only. |
| 2602.22425 | ArchAgent | Agent architecture context | Background only. |
| 2602.16928 | Multiagent Learning | Domain-result context | Background only. |
| 2603.09172 | Ramsey Numbers | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2509.18057 | Hardness of Approximation | Domain-result context | Background only. |
| 2603.06692 | Combinatorics Berczy | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2601.16175 | TTT Discover | Test-time discovery context | Background only. |
| 2603.08679 | Bilateral Trade | Domain-result context | Background only. |
| 2601.01235 | Bruhat Intervals | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2511.12916 | Fault2Flow | Domain-result context | Background only. |
| 2601.05943 | Global NLP Optimization | Optimization benchmark candidate | Not implemented; potential future benchmark. |
| 2506.16750 | Autoconvolution | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2505.16105 | Sums and Differences | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2506.01896 | Sums and Differences II | Constructive math benchmark candidate | Not implemented; potential future benchmark. |

## Benchmark coverage decisions

Implemented:

- `libreevolve/problems/examples/circle_packing`: AlphaEvolve-adjacent packing
  benchmark.
- `libreevolve/problems/examples/matrix_multiplication`: small reproducible
  2x2 multiplication-count smoke benchmark with evolve-block seed and
  validator. It is not a tensor-rank decomposition benchmark.

Planned or background-only:

- Constructive math papers are retained as benchmark candidates until validators
  are added.
- Systems/kernel/scheduling-style AlphaEvolve targets are not yet represented;
  they need safer local fixtures before they should be advertised as supported.
