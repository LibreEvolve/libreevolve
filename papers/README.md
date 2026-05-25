# Local Paper Cache

This directory contains 24 locally cached papers plus download manifests. The
cache is used as research context for LibreEvolve; it is not a claim that every
paper is fully implemented.

## Implementation status

| ID | Title | Role | Current LibreEvolve status |
|---|---|---|---|
| 2506.13131 | AlphaEvolve | Primary specification target | Partially implemented: evolve blocks, local text-workspace candidates, workspace topology mutations, full-workspace best export, workspace execution/import fidelity, mutation modes including canonical SEARCH/REPLACE diff compatibility, structured evaluator results, configurable local cascades, strict scalar evaluator-output validation, primary metric normalization for well-formed bounds, prompt sampler/context ingestion, prompt-program database and optional meta-prompt mutation, synchronous critique/feedback with full-workspace feedback prompts and failure isolation, manifests, candidate history/admission provenance, plugin score composition, circle packing, and a small matrix smoke benchmark. Flexible non-code candidate abstractions, binary/static candidate artifacts, candidate path-collision handling, strict metric-bound ordering, workspace-aware MAP-Elites descriptors, custom LLM backend registration, proposal-rationale capture, richer prompt rendering of execution outputs, async workers, LLM provider retry/fallback, validator environment/secret isolation, validator process-tree cleanup, run-wide compute-budget accounting, true multi-objective search, queryable evolutionary database, archive-state/migration persistence, resume, run-identity/evaluator-provenance hardening, seeded replay/lineage-id determinism, feedback calibration, role-specific LLM accounting, plugin config/provenance, benchmark validator hardening, equal-budget ablation reporting, and stronger AlphaEvolve-scale benchmarks remain open. |
| 1504.04909 | MAP-Elites | Foundational archive algorithm | Implemented as a fixed 3D archive over normalized fitness, code length, and TF-IDF diversity; user-defined behavior descriptors remain open. |
| auer-cesa-bianchi-fischer-2002 | UCB1 finite-time analysis | Foundational bandit policy | Implemented as a heuristic UCB-style backend router over fitness improvements; reward normalization/canonical regret assumptions are documented gaps. |
| 2511.17592 | GigaEvo | Framework inspiration | Not implemented as described: no Redis lifecycle database, asyncio DAG engine, insight stage, or concurrent units. Diff/full mutation modes are partially present. |
| 2510.14150 | CodeEvolve | Agentic code-evolution inspiration | Not implemented as described: no crossover, targeted refinement, modular orchestration, or adaptive meta-prompting. |
| 2511.23473 | ThetaEvolve | Test-time training inspiration | Only clipped-reward JSONL export exists through `ttt_rl`; no run-scoped dataset provenance or online RL/GRPO training loop. |
| 2602.10233 | ImprovEvolve | Modular search inspiration | Only static prompt guidance exists; no enforced or attributed generate/improve/perturb execution loop. |
| 2602.15951 | MadEvolve | Domain evolution inspiration | Background only; no free-parameter optimization or innovation report. |
| 2603.14575 | CausalEvolve | Causal-guidance inspiration | Only token-pattern outcome-factor guidance exists; no LLM causal scratchpad. Factor detection now uses the shared compact/canonical SEARCH/REPLACE parser, but the detected factors are still fixed local token-pattern categories rather than LLM-discovered causal variables. |
| 2510.06056 | DeepEvolve | Retrieval/debug loop inspiration | Only best-effort arXiv/web-search context exists; no persisted retrieval provenance, cross-file editing, or systematic debugging loop. |
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
