# LibreEvolve

LibreEvolve is a Python research workbench for LLM-guided evolutionary program
discovery. Given a problem directory, it evaluates one or more seed programs,
asks configured LLM backends to propose code mutations, evaluates the resulting
candidates, and keeps retained programs in a small quality-diversity archive.

The project is inspired by AlphaEvolve, Karpathy's `autoresearch`, MAP-Elites,
and recent work on LLM-guided program search. It is an independent project and
is not affiliated with or endorsed by Google DeepMind or the authors of the
cited papers.

## Status

This is an alpha-stage research codebase. It is useful for local experiments and
for studying implementation boundaries, but it is not a production optimizer and
not a full AlphaEvolve reproduction.

This README is the practical entry point. The detailed implementation and
absence-boundary ledger lives in [docs/status.md](docs/status.md), paper-source
evidence lives in [papers/README.md](papers/README.md), and active backlog items
live under [docs/todo/](docs/todo/).

Implemented today:

- Python-primary candidate workspaces and seed programs.
- SEARCH/REPLACE diff mutations using the AlphaEvolve fence format, plus
  configurable full-code replacement mode.
- OpenAI, Anthropic, and Ollama backend adapters with heuristic UCB-style
  backend selection.
- Synchronous MAP-Elites and island archives, with five islands by default.
- Local subprocess evaluation with staged validator support.
- Optional critique, feedback, and plugin hooks.
- Run artifacts under `runs/`, including manifests, histories, prompts,
  failures, best candidates, evaluator artifacts, and plugin artifacts.

Important limits:

- Evaluators run in local subprocesses, not hardened security sandboxes.
- The controller, archive, migration, and evaluator flow are local and
  synchronous, not a distributed asynchronous AlphaEvolve-style service.
- Built-in provider adapters are OpenAI, Anthropic, and Ollama; Google/Gemini
  provider parity remains an explicit absence boundary.
- Backend selection is a local heuristic inspired by UCB-style routing, not a
  finite-time-regret UCB1 reproduction.
- Canonical UCB1 finite-time bandit coverage is foundational source context
  only: LibreEvolve has no proof that backend rewards satisfy bounded
  `[0,1]` distribution assumptions, no conditional-mean or stationarity audit,
  no regret-definition runtime report, no Theorem 1 or suboptimal-pull-bound
  report, no canonical `sqrt(2 ln t / T_i(t))` index-equivalence claim, no
  per-selection index trace, no stable backend-as-arm audit across roles and
  runs, no calibrated exploration-coefficient mapping, no UCB2,
  `epsilon_n`-GREEDY, UCB1-NORMAL, or UCB1-TUNED support, and no regret proof
  for metadata-weighted `throughput_depth` routing; `papers/ucb1_boundary.json`
  records that absence boundary.
- MAP-Elites support is a local quality-diversity archive, not a paper-faithful
  illumination study with full map exports, coverage/reliability/precision
  reports, or domain reproductions.
- GigaEvo framework coverage is inspiration-only: LibreEvolve has no Redis
  program lifecycle database, optimistic concurrency records, `asyncio` DAG
  execution engine, DAG stage-output or caching telemetry, concurrent
  evolutionary-unit runtime, Hydra component mapping, GigaEvo problem-layout
  adapter, insight-generation artifacts, bidirectional lineage-analysis
  artifacts, LangGraph mutation-operator provenance, dual GitHub source-link
  disambiguation, or Heilbronn/circle-packing/kissing/bin-packing/Jigsaw
  reproduction rows; `papers/gigaevo_framework_boundary.json` records that
  absence boundary.
- CodeEvolve coverage is agentic code-evolution inspiration only:
  LibreEvolve has no prompt/solution dual-fitness population,
  inspiration-based semantic crossover, `MetaPromptingLLM` exploration branch,
  depth-targeted refinement using nearest ancestors, Plateau Scheduler trace,
  rank-based inspiration selection, elitist migration record, sandbox
  runtime/memory evidence, CVT-MAP-Elites archive parity, AlphaEvolve/EoH
  benchmark rows, component-ablation rows, open-framework comparison rows,
  Qwen3-Coder-30B versus GEMINI-2.5 quality-cost report, or recommended
  hyperparameter evidence; `papers/codeevolve_boundary.json` records that
  absence boundary.
- ThetaEvolve coverage is test-time-training inspiration only: LibreEvolve's
  `ttt_rl` support writes clipped-reward JSONL examples and does not implement
  a ThetaEvolve dynamic environment, single-LLM training runtime, large program
  database scaling report, batch parent/response sampling, early-check penalty
  schema, lazy penalties, reward shaping, online GRPO/RL training, asymmetric
  clipping configuration, checkpoint lifecycle, trained-checkpoint inference,
  transfer/generalization report, concurrent verifier throughput,
  SGLang/vLLM throughput report, AlphaEvolve/ShinkaEvolve/OpenEvolve
  comparison rows, open-problem benchmark rows, or database/reward ablations;
  `papers/thetaevolve_boundary.json` records that absence boundary.
- ImprovEvolve coverage is modular-search inspiration only: LibreEvolve's
  `modular` plugin is static prompt guidance and does not enforce or execute a
  `generate_config`/`improve`/`perturb` interface, Stage A initialization,
  Stage B basin-hopping validation, perturbation schedule, monotonic
  acceptance proof, incumbent/improvement-delta artifact, GigaEvo outer
  backbone, Gemini/OpenRouter model-provider provenance, human-edited
  `ImprovEvolve+E` attribution, HEX or ACI2 benchmark rows, hyperparameter or
  generalization tables, stage-ablation rows, CPU/GPU budget records, or
  wall-clock reproduction; `papers/improvevolve_boundary.json` records that
  absence boundary.
- The examples are smoke fixtures and small demos unless a fixture documents
  stronger benchmark evidence.
- Benchmark-hardening records and shipped-example scope validate smoke-scope
  anti-gaming metadata and `alphaevolve_comparable: false` boundaries, not
  benchmark-grade tensor/geometric/constructive-math runners, randomized or
  exhaustive anti-gaming evidence, executable construction/certificate
  validators, target/SOTA baselines, Colab-equivalent Appendix B construction
  data, or verifier-code artifacts.
- The checked-in `matrix_multiplication` example remains a 2x2 smoke fixture:
  its primary inverse-count metric is normalized over the reachable `1/count`
  range, but it does not provide target/SOTA catalogs, repeated-seed reports,
  or AlphaEvolve-comparable tensor-decomposition benchmark evidence.
- Matrix-publication evidence is one checked `mm_2x2x2` Strassen baseline
  bundle plus Appendix A registry/status metadata, not full-suite local target
  tensors, discovered decompositions, coefficient data, exactness
  certificates, notebooks, per-seed reports, or publication bundles for every
  registered Appendix A target.
- Appendix A matrix target-suite curation records the reported 54 sorted
  targets, rough paper selection wording, symmetry policy, and included-target
  rationales, not an exhaustive locally justified corpus for every excluded
  non-equivalent matrix size outside the reported suite.
- Appendix A matrix resource-frontier records preserve the paper-source
  statement about sizes beyond `<5,5,5>`, 1000 random seeds, single-GPU
  evaluators, frequent OOM, and further-optimization need, not local
  larger-target runs, measured accelerator-memory profiles, OOM artifacts,
  reduced-seed tradeoffs, or reproduced scaling evidence.
- Matrix per-seed reports validate declared seed rows, best rank, and hit
  fraction, and matrix cascade-run boundary records can link seed rows to stage
  traces, but local matrix runners do not yet emit AlphaEvolve Section
  3.1-style repeated-seed cascade traces, pruning decisions, or early-stop
  provenance.
- AlphaEvolve Figure 8 ablation support is a validated registry, equal-budget
  report contract, scope-boundary records, and optional exhibit/artifact
  metadata, not executed equal-budget matrix/kissing benchmark runs, proven
  component-isolated ablation setups, rendered paper-quality curves, or
  accelerator/async-worker budget evidence.
- The May 7, 2026 Google DeepMind AlphaEvolve impact article is official
  source context, not local LibreEvolve benchmark support; named
  DeepConsensus, AC OPF, Earth AI, Willow, public-gallery, TPU, cache-policy,
  Spanner, compiler-storage, customer, UI, and API claims remain bounded by
  `papers/alphaevolve_2026_impact_boundary.json`.
- FHE-on-TPU AlphaEvolve application coverage is background paper context only:
  LibreEvolve has no TFHE/Jaxite or CKKS/CROSS primitive harness, Google Cloud
  TPUv5e execution provenance, correctness-test suite, generated
  cryptographic-kernel artifact hashes, latency benchmark rows, baseline
  implementation identity, or independent reproduction for the reported 2.5x,
  1.31x, and 1.18x speedups.
- AlphaEvolve HCI/user-study coverage is background paper context only:
  LibreEvolve has no formative-study dataset, participant/session trace
  schema, intentmaking/sensemaking event taxonomy, AlphaEvolve UI/dashboard
  artifact inventory, goal-revision or human-intervention records,
  privacy/redaction protocol for study data, coded qualitative-analysis
  evidence, or collaborative scientific-discovery instrument workflow support.
- Radar/resource-allocation AlphaEvolve application coverage is background
  paper context only: LibreEvolve has no radar scenario/target-count taxonomy,
  physically inspired feature schema, deterministic constraint-satisfying
  power-allocation transform, multi-target tracking simulator, baseline
  iterative solver identity, average relative performance-loss benchmark rows,
  cross-scenario generalization evidence, three-orders speedup reproduction,
  or independent checker output.
- EvoX adaptive meta-evolution coverage is background paper context only:
  LibreEvolve has no adaptive strategy-genome schema, outer meta-evolution
  loop, strategy-credit assignment, dynamic search-policy update artifacts,
  EvoX task-suite taxonomy, baseline comparison table against AlphaEvolve,
  OpenEvolve, GEPA, and ShinkaEvolve, token-efficiency report, strategy
  ablation records, or independent reproduction output.
- DeltaEvolve semantic-delta coverage is background paper context only:
  LibreEvolve has no first-class semantic-delta schema, node-transition effect
  attribution, semantic-delta memory bank, multi-level database/index
  metadata, progressive disclosure traces, token-savings report,
  full-code-history baseline comparison, scientific-task benchmark taxonomy,
  or independent reproduction output.
- MLEvolve long-horizon ML-engineering coverage is background paper context
  only: LibreEvolve has no MLE-Bench task harness, Progressive MCGS state
  schema, graph-based reference-edge provenance, entropy-inspired progressive
  schedule, Retrospective Memory knowledge base or global memory artifacts,
  adaptive coding-mode traces, 12-hour medal-rate/valid-submission report,
  mathematical-algorithm baseline comparison, linked-code audit, or
  independent reproduction output.
- LEVI cost-aware search-architecture coverage is background paper context
  only: LibreEvolve has no LEVI-style diversity-preserving solution-database
  report, large/small model mutation-router policy, role-assignment trace,
  rank-preserving proxy benchmark, rollout/provider-cost accounting report,
  systems-research benchmark fixture, prompt-optimization budget comparison,
  linked-code audit, or independent reproduction output.
- PACEvolve long-horizon consistency coverage is background paper context
  only: LibreEvolve has no context-pollution detector, hierarchical
  context-management/pruning artifacts, mode-collapse diagnostics,
  momentum-based backtracking controller, unified crossover/backtracking
  sampler, trajectory-collaboration diagnostics, LLM-SR/KernelBench/Modded
  NanoGPT benchmark report, linked-code audit, or independent reproduction
  output.
- FlashEvolve asynchronous-stage orchestration coverage is background paper
  context only: LibreEvolve has no asynchronous worker queue, stage dependency
  scheduler, artifact-version lineage DAG, stale-artifact detector, staleness
  repair policy, speculative stage-completion records, adaptive workflow
  controller, EvolBench/ChatDev/MetaGPT benchmark report, 3.5x/4.9x
  throughput reproduction, linked-code audit, or independent reproduction
  output.
- Evolutionary-agent trace-diagnostic coverage is background paper context
  only: LibreEvolve has no EvoTrace-compatible trace schema, nine-class edit
  taxonomy annotation pipeline, LLM-as-judge edit reannotation validation,
  parent-child search graph export, prompt/context substitution replay, model
  substitution replay, component-removal intervention harness,
  constant-retuning baseline, deterministic deleted-line reintroduction/
  cycling detector, held-out generalization report, or independent
  reproduction output.
- Zarankiewicz reinforced-search coverage is background paper context only:
  LibreEvolve has no Zarankiewicz parameter manifest, bipartite graph
  construction schema, `K_{s,t}`-free verifier, exact-value/lower-bound table,
  generated-algorithm artifact hashes, OpenEvolve setup provenance,
  reward-function specification, upper-bound comparison ledger,
  per-parameter cost accounting, or independent reproduction output for the
  three exact values, 41 lower bounds, four matched closed cases, or sub-$30
  cost claim.
- CORAL autonomous multi-agent evolution coverage is background paper context
  only: LibreEvolve has no long-running autonomous agent sessions, shared
  persistent memory repository, asynchronous multi-agent execution runtime,
  heartbeat-based intervention controller, isolated per-agent workspaces,
  evaluator separation layer, resource/session/health manager,
  knowledge-reuse analysis, 10-task SOTA report, 3-10x improvement-rate
  reproduction, Anthropic kernel-engineering 1363-to-1103 cycle reproduction,
  linked-code audit, or independent reproduction output.
- AEvo harnessed meta-editing coverage is background paper context only:
  LibreEvolve has no process-level evolution state exposing accumulated
  candidates, feedback, traces, failures, or costs, meta-agent procedure or
  agent-context editor, standardized editable evolution workspace, protected
  evaluator boundary, searchable candidate history for meta-editing,
  meta-editing phase/evolution-segment runner, run-plan contract,
  procedure-versus-agent evolution instantiation, five-baseline
  agentic/reasoning benchmark report, 26% relative-improvement reproduction,
  three-task open-ended optimization report, linked-code audit, or independent
  reproduction output.
- G-Zero verifier-free co-evolution coverage is background paper context only:
  LibreEvolve has no Hint-delta intrinsic-reward computation from unassisted
  versus hint-conditioned Generator responses, Proposer model, Generator
  model, self-generated query/hint dataset, GRPO proposer trainer, DPO
  generator trainer, co-evolution training loop, pseudo-label noise filter,
  exploration-coverage report, best-iterate suboptimality fixture,
  unverifiable-domain benchmark, external-judge reward-hacking comparison,
  linked-code audit, or independent reproduction output.
- GenEvolve multimodal trajectory-distillation coverage is background paper
  context only: LibreEvolve has no image-generation tool pipeline,
  visual-reference ingestion, prompt-rewriting/layout-planning/image-
  generation/refinement trajectory schema, tool-call artifact lineage,
  Agentic Visual Experience Distillation or Visual Experience Distillation
  target, dense token-level supervision record, multimodal policy-update
  loop, GenEvolve-Data metadata, GenEvolve-Bench task/report, baseline
  comparison, linked-code audit, or independent reproduction output.
- EvoRubric self-evolving reward-rubric coverage is background paper context
  only: LibreEvolve has no single-policy Reasoner/Rubric-Generator
  co-evolution loop, generated-rubric provenance, meta-verifier records,
  zero-variance pruning records, Leave-One-Out peer-consensus traces, criteria
  memory pool, dense multi-objective reward vectors, expert-prior rubric
  expansion, medical/writing/science benchmark report, reward-hacking audit,
  linked-code audit, or independent reproduction output.
- LLM-ALSO adaptive learning-signal coverage is background paper context only:
  LibreEvolve has no sparse-reward cooperative MARL harness, Critic LLM
  diagnosis role, Generator LLM reward-shaping role, compact behavior evidence
  record, stage-specific coordination-failure diagnosis, reward-shaping
  configuration artifact, branch-validation trajectory, validated-update
  promotion gate, main-training trajectory provenance, learning-efficiency
  report, linked-code audit, or independent reproduction output.
- MemEvolve memory-architecture evolution coverage is background paper context
  only: LibreEvolve has no explicit encode/store/retrieve/manage
  memory-component design space, memory-architecture genotype,
  memory-system mutation/evaluation loop, experiential-knowledge
  co-evolution trace, EvolveLab benchmark mapping, static-memory baseline
  comparison, cross-task or cross-LLM transfer report, performance-delta
  record, linked-code audit, or independent reproduction output.
- ANCHOR healthy-evolution oversight coverage is background paper context
  only: LibreEvolve has no ANCHOR human-like oversight agent, phase-specific
  norm-correction interface, safety-drift metric lineage,
  output-verification intervention records, reflection/review artifact stream,
  supervision-frequency/cadence trace, preservation-of-objective-performance
  report, coding/math/safety benchmark report, linked-code audit, or
  independent reproduction output.
- SIA harness-plus-weight self-improvement coverage is background paper
  context only: LibreEvolve has no Feedback-Agent that chooses between harness
  and weight updates, editable task-agent harness inventory, harness patch
  provenance, online RL/fine-tuning loop, adapter/checkpoint lifecycle,
  trajectory-to-training-data promotion policy, rollback/resume policy,
  harness-only versus weight-only versus combined ablation report,
  LawBench/kernel/scRNA benchmark report, linked-code audit, or independent
  reproduction output.
- HarnessFix trace-grounded harness-repair coverage is background paper
  context only: LibreEvolve has no HTIR trace-normalization schema, raw-trace
  normalization record, harness-code linkage, step-level provenance,
  execution/tool/context/lifecycle/observability/verification/governance
  harness-layer attribution taxonomy, recurring flaw consolidation, scoped
  repair operator schema, generated harness patch artifact, flaw-specific
  validation specification, unacceptable-regression threshold record,
  held-out SWE-Bench Verified/Terminal-Bench 2.0 Verified/GAIA/AppWorld
  benchmark report, linked-code audit, or independent reproduction output.
- RHO retrospective harness-optimization coverage is background paper context
  only: LibreEvolve has no unlabeled past-trajectory harness optimizer,
  hard/diverse coreset selector, DPP coreset record, parallel retrospective
  re-solve workflow, group rollout artifact, self-validation diagnostic,
  self-consistency diagnostic, candidate harness-update set, pairwise
  self-preference selector, label-free promotion policy, deployment/rollback
  metadata, behavior-pattern shift report, long-horizon accuracy report,
  SWE-Bench Pro 59%-to-78% reproduction, linked-code audit, or independent
  reproduction output.
- Harness-updating versus harness-benefit coverage is background paper context
  only: LibreEvolve has no harness-updating metric schema, harness-benefit
  metric schema, evolver-versus-task-solver model-pair matrix,
  capability-tier grouping record, cross-benchmark harness self-evolution
  report, activation-failure audit, adherence-failure audit,
  capability-budget recommendation report, public-code snapshot audit, or
  independent reproduction output.
- AHE observability-driven harness-evolution coverage is background paper
  context only: LibreEvolve has no file-level editable harness component
  graph, component-observability schema, layered drill-down trajectory
  evidence corpus, raw-trace-to-digest provenance, decision-observability
  prediction contract, next-round falsification record, per-edit rollback
  manifest, ten-iteration Terminal-Bench 2 report, SWE-bench-verified
  transfer report, cross-family transfer report, tools/middleware/memory
  ablation, public-code snapshot audit, or independent reproduction output.
- AI Harness Engineering runtime-substrate coverage is background paper
  context only: LibreEvolve has no complete eleven-responsibility harness
  contract, H0-H3 harness-ladder fixture, trace-based episode-package schema,
  controlled validation-task reproduction, model-harness-environment
  capability equation record, failure-attribution taxonomy report,
  deterministic requirement-check package, structured verification report,
  public-code snapshot audit, or independent reproduction output.
- Inference-time trajectory-alignment coverage is background paper context
  only: LibreEvolve has no harness parameterization for decomposition versus
  guided execution, workflow-granularity sweep, retry-budget study,
  guidance-induced action-reweighting report, stage-level gap metric,
  over-decomposition failure report, over-pruning failure report,
  hallucinated-execution failure report, partial-harnessing stopping rule,
  controlled synthetic experiment, terminal-agent benchmark reproduction,
  linked-code audit, or independent reproduction output.
- Adaptive Auto-Harness deployment coverage is background paper context only:
  LibreEvolve has no chronological open-ended task-stream schema,
  history-growth record, task-heterogeneity report, distribution-shift
  detector, evolution-loss/adaptation-loss decomposition, stateful
  multi-agent evolver, harness tree, solve-time routing policy,
  human-steering hook, overfitting/accuracy-peak-decline report,
  prediction-market/security-competition/event-forecasting benchmark
  reproduction, five-baseline comparison, linked-code audit, or independent
  reproduction output.
- Meta-Harness outer-loop harness-code optimization coverage is background
  paper context only: LibreEvolve has no first-class harness-code candidate
  schema, filesystem-visible harness workspace, agentic proposer that edits
  harness code, candidate harness edit provenance, execution-trace feedback
  bundle, score/provenance replay package, outer-loop harness search
  controller, online text-classification reproduction, 200-problem
  IMO-level retrieval-augmented math reproduction, TerminalBench-2
  reproduction, held-out-model transfer report, linked-code audit, or
  independent reproduction output.
- AlphaEvolve MARL algorithm-discovery coverage is background paper context
  only: LibreEvolve has no CFR candidate schema, PSRO candidate schema,
  OpenSpiel imperfect-information game fixture, game-suite split record,
  exact exploitability metric record, exact best-response oracle record,
  VAD-CFR result row, SHOR-PSRO result row, WOP-CFR distillation row, PM-PSRO
  distillation row, IQM ablation audit, random normal-form validation row,
  generated solver artifact hash, or reproducible CFR/PSRO runtime evidence;
  `papers/multiagent_learning_boundary.json` records that absence boundary.
- AlphaEvolve Ramsey-number coverage is background paper context only:
  LibreEvolve has no Ramsey graph candidate schema, `run()` primary/prospect
  graph contract, graph witness artifact schema, clique/independent-set
  verifier, Ramsey parameter row, new lower-bound row, matched-best-known
  row, exact-known-bound recovery row, graph vertex-count record, implied
  lower-bound record, Google Research construction/code snapshot hash,
  initialization-family record, search-budget record, random-seed record,
  algorithm-summary audit, or independent checker output;
  `papers/ramsey_numbers_boundary.json` records that absence boundary.
- AlphaEvolve-assisted local-correction combinatorics coverage is background
  paper context only: LibreEvolve has no bipartite graph-reconstruction
  harness, planar graph-reconstruction harness, Alon-Tarsi Latin-square
  involution harness, Rota-basis linear-matroid exchange harness, candidate
  certificate schema, local-correction policy API, symmetry-scramble record,
  hard-negative replay buffer, evolved code-block artifact hash,
  Gemini-summary artifact hash, reported metric row, conjecture/proof-status
  ledger, repository snapshot, or independent verifier output;
  `papers/combinatorics_berczy_boundary.json` records that absence boundary.
- AlphaEvolve bilateral-trade mechanism-design coverage is background paper
  context only: LibreEvolve has no bilateral-trade distribution candidate
  schema, fixed Discrete Equal Revenue buyer fixture, evolved seller CDF
  generator runtime, PMF/CDF/survival validator, first-best GFT evaluator,
  seller-offering GFT evaluator, buyer-offering GFT evaluator,
  Random-Offerer ratio evaluator, `1e-15` integer-rounding precision policy,
  witness distribution artifact, evolved/evaluation code hash, prior-baseline
  row, alternate-search attempt row, BIC/BB/IR assumption record,
  unrounded-mixture caveat handling, or independent checker output;
  `papers/bilateral_trade_boundary.json` records that absence boundary.
- AlphaEvolve Magellan compiler-optimization coverage is background paper
  context only: LibreEvolve has no executable C++ decision-logic candidate
  schema, LLVM/XLA compiler-pass integration, EVOLVE-BLOCK compiler-source
  span record, compiler-flag hyperparameter schema, local compiler rebuild
  record, macro-benchmark harness, Vizier-style autotuning record, LLVM
  function-inlining result row, register-allocation result row, XLA
  graph-extraction or auto-sharding row, expert/neural baseline comparison,
  temporal/domain generalization report, generated-policy maintainability
  evidence, compiler environment hash, or independent checker output;
  `papers/magellan_boundary.json` records that absence boundary.
- AlphaEvolve ArchAgent computer-architecture coverage is background paper
  context only: LibreEvolve has no cache replacement policy candidate schema,
  ChampSim `policy.h` integration, CRC cache/core/prefetch/DRAM
  configuration record, SPEC06 or Google Workload Trace fixture,
  IPC-over-LRU metric row, short-run/long-run validation split,
  Policy31/Policy31-Tuned/Policy61/Policy62 generated-policy artifact,
  hardware-realizability or state-budget check, post-silicon specialization
  record, simulator-escape or write-bypass containment policy,
  distributed-simulation reliability record, or independent checker output;
  `papers/archagent_boundary.json` records that absence boundary.
- AlphaEvolve Fault2Flow workflow-automation coverage is background paper
  context only: LibreEvolve has no regulatory-PDF ingestion runtime,
  MinerU-to-Markdown extraction record, PlantUML mind-map artifact, PASTA
  fault-tree schema, human-in-the-loop expert-review state, AlphaEvolve or
  OpenEvolve reasoning-optimizer trace, n8n workflow synthesis or activation
  record, workflow verification/refinement loop, `DL/T 722-2014` dataset
  snapshot, transformer fault-case row, GPT-5 judge output, Table 1
  reproduction row, token ledger, human-annotation ethics record, or local
  Fault2Flow repository/runtime snapshot; `papers/fault2flow_boundary.json`
  records that absence boundary.
- TTT-Discover test-time-training coverage is background paper context only:
  LibreEvolve has no mutable policy-weight update loop, single-problem RL
  environment, continuous-reward problem contract, candidate-state schema,
  PUCT state-reuse trace, adaptive entropic objective execution, Tinker API
  training-run record, OpenAI `gpt-oss-120b` LoRA backend record,
  Best-of-25600 or OpenEvolve matched-budget comparator row,
  Erdos/autocorrelation/GPUMode/AtCoder/single-cell benchmark row,
  expert or organizer review artifact, public-code artifact hash, cost
  record, or independent reproduction output; `papers/ttt_discover_boundary.json`
  records that absence boundary.
- Bruhat Intervals constructive-math coverage is background paper context
  only: LibreEvolve has no permutation-pair candidate schema,
  simple-reflection decoder, Kazhdan-Lusztig d-invariant evaluator, Bruhat
  order or Ehresmann matrix verifier, `x_m`/`y_m` witness generator, dyadic
  basic-interval checker, dyadically well-distributed permutation checker,
  fundamental or complementary block validator, poset-hypercube isomorphism
  checker, Kazhdan-Lusztig R-polynomial linkage row, cluster-algebra or
  Bruhat-graph consequence row, AlphaEvolve/FunSearch prompt/model/budget
  provenance, public artifact hash, finite-test versus general-proof status,
  or independent checker output; `papers/bruhat_intervals_boundary.json`
  records that absence boundary.
- Global NLP Optimization coverage is direct-solver comparator context only:
  LibreEvolve has no nonlinear-optimization formulation schema, Mosel model
  artifact, min-max distance-ratio fixture, square or perimeter-4 rectangle
  circle-packing fixture, unit-hexagon packing fixture, Farkas non-overlap
  certificate, FICO Xpress or SCIP runner, solver identity/version/license
  record, solver parameter or time-limit record, incumbent/bound/certificate
  artifact, numerical tolerance and rounding policy, AlphaEvolve validation-
  code output, Table 1-3 reproduction row, solver log, solver-attribution
  evidence, dual-bound improvement record, or independent checker output;
  `papers/global_nlp_optimization_boundary.json` records that absence
  boundary.
- Post-AlphaEvolve autoconvolution coverage is constructive-math context only:
  LibreEvolve has no 575-interval step-function witness schema, coefficient
  payload hash, formula (3) checker, `L_j` recomputation trace,
  `L2`/`Linf`/`L1` norm recomputation, exact-rational verification,
  AlphaEvolve 50-interval baseline record, Matolcsi-Vinuesa 20-step baseline
  record, simulated-annealing or gradient-search provenance, public GitHub
  snapshot for `Inital HPC code.py`, `Refine HPC code.py`, `f95.py`,
  `coeffBL.txt`, or `Verify.nb`, coefficient row-order test, support-
  normalization checker, NCSU HPC resource record, or independent checker
  output; `papers/autoconvolution_boundary.json` records that absence
  boundary.
- Post-AlphaEvolve sums-and-differences coverage is constructive-math context
  only: LibreEvolve has no explicit `U`-set construction schema,
  `W(m,L,B)` inclusion-exclusion checker, base-`2B+1` injective encoding
  verifier, sumset or difference-set cardinality checker, max-element or
  q-value verifier, `theta` recomputation, huge-set compression artifact,
  exact GMP arithmetic record, floating-point search record,
  `(80,64,5)` or `(81411,65536,5)` exact result row, bit.ly exact-value
  artifact snapshot, AlphaEvolve `54265`-integer baseline record, prior
  `1.14465` baseline row, tolerance policy, lineage comparison row, or
  independent checker output; `papers/sums_differences_boundary.json`
  records that absence boundary.
- Post-AlphaEvolve sums-and-differences sequence coverage is asymptotic
  constructive-math context only: LibreEvolve has no sequence-of-`U`
  construction schema, large-deviation `I(c,B)` checker, asymptotic
  `W(m,floor(rm),B)` checker, Lemma 1 or Lemma 2 verifier, q/s/d bound
  derivation record, `theta0` variational-formula recomputation, MATLAB 2024b
  code provenance, tolerance-sweep reproduction for `B=3..10` or
  `1e-4..1e-10`, independent Python or exact reimplementation,
  finite-prefix artifact policy, convergence or tail-bound check,
  AlphaEvolve `1.1584` baseline row, Gerbicz `1.173050` baseline row,
  lineage comparison row, or independent checker output;
  `papers/sums_differences_sequence_boundary.json` records that absence
  boundary.
- Matrix near-integrality records validate declared prompt instructions,
  integer/half-integer rounding policy, raw-versus-rounded coefficient
  diagnostics, and exactness-certificate links, not a local matrix runner that
  emits AlphaEvolve Section 3.1 near-integral prompt/evaluator evidence during
  search.
- Matrix sweep-space records validate declared Figure 9-style `sweep()`
  provenance, user-provided `hyper` ranges, sampled configurations, selected
  winners, final decompositions, and exactness-certificate links, not a local
  matrix runner that emits AlphaEvolve Figure 4/Figure 9 search-program sweep
  evidence during search.
- Appendix A Figure 9 matrix-diff records validate panel ids, pages, line
  spans, semantic components, source/diff hashes, rendered/OCR artifact
  metadata, and links to matrix result, sweep-space, certificate, and companion
  notebook evidence, not local report/export output that emits rendered panel
  images, OCR text, or source-diff artifacts for Figures 9a-9c.
- Figure 4 matrix-discovery records validate main-text exhibit metadata,
  caption linkage, the 15-mutation caption count, `mm_4x4x4` rank-48 target
  mapping, highlighted component categories, source/diff artifact metadata,
  and links to Figure 9, matrix-result, certificate, and notebook evidence, not
  local report/export output that emits rendered Figure 4 artifacts or accepted
  15-mutation lineage.
- Matrix baseline-component records validate Section 3.1 starting-algorithm
  provenance fields for baseline program ids, initializer, reconstruction
  loss, Adam optimizer metadata, mutable scopes, fixed hashes, generation-0
  metrics, mutation lineage, and matrix-result links, not local matrix-runner
  output that emits the initializer/loss/optimizer provenance during search.
- Matrix scalar-field records validate complex/finite-field metadata,
  characteristic and applicability claims, exact coefficient representation,
  algorithm and certificate refs, and matrix-result links, not local matrix
  runners that emit exact complex decomposition/certificate artifacts for
  AlphaEvolve Section 3.1 scalar-field claims.
- Matrix tensor-rank records validate tensor-decomposition versus non-tensor
  algorithm claims, rank, recursive applicability, certificate scope,
  tensor-identity status, target-tensor refs, exactness-certificate refs, and
  matrix-result links, not local matrix runners that emit AlphaEvolve Section
  3.1 target-tensor/certificate artifacts during search.
- Constructive-math heuristic-handoff records preserve the Section 3.2 claim
  that search-heuristic programs run under fixed budgets from strong
  previous-best construction inputs toward improved constructions, not local
  heuristic-program artifacts, incumbent or produced construction payloads,
  fixed-budget execution records, before/after metric rows, scores, or
  verifier evidence.
- Constructive-math stage-sequence records preserve the Section 3.2 claim that
  final constructions often came from multiple specialized heuristics,
  including early broad-gain stages from random/simple starts and later
  fine-tuning near optimal configurations, not local per-stage heuristic
  artifacts, ordered construction transitions, stage-role rows, improvement
  deltas, budget rows, or verifier evidence.
- Constructive-math aggregate-outcome records preserve the Section 3.2 source
  claim of over 50 mathematical problems across more than five branches, about
  75% best-known rediscovery, about 20% SOTA improvement, and definition-based
  verification, not local per-problem rows, branch taxonomy rows, prior-best
  references, construction/verifier artifacts, aggregate counts, or percentage
  recomputation.
- Constructive-math starting-construction records preserve the Section 3.2
  source claim that the initial starting point was a simple or random
  construction, not local per-instance starting construction payloads,
  generator or random-seed records, baseline metric rows, prior-best visibility
  policy, or prior-best seeding policy evidence.
- Figure 5 constructive-math exhibit provenance remains absent: README
  describes Appendix B family/status coverage, smoke-fixture boundaries, and
  constructive-math absence boundaries, not main-text Figure 5 exhibit ids,
  selected result-row links, branch/problem label mappings, before/after metric
  values, previous-best sources, rendered visual artifact paths or hashes,
  rendering parameters, source Colab cells/artifacts, or verifier links.
- Figure 5 versus Appendix B.12 sum-of-radii precision remains unreconciled:
  the registry preserves Figure 5's `2.6340 -> 2.6358` display separately from
  the Appendix B.12/Figure 14 `2.634 -> 2.635` strings, not source-specific
  locators, Figure 5 panel artifacts, value-extraction certificates,
  normalized values, rounding or canonicalization policy, value-reconciliation
  certificate, recomputed sum, or companion Colab link.
- Appendix B Figures 10-14 figure-exhibit provenance remains absent: the
  registry names Erdos minimum overlap, regular-hexagon packing,
  maximum/minimum-distance point sets, Heilbronn variants, and
  circle/rectangle sum-of-radii packing figure scopes, not normalized
  figure-exhibit rows, subfigure ids, caption-value extraction,
  previous/current metric rows, construction payload artifacts, rendered panel
  artifacts, rendering parameters, source Colab cells/artifacts, or verifier
  links.
- Appendix B numeric-result provenance remains absent: the registry enumerates
  B.1-B.13 family/status metadata and the `19` expected future result ids,
  including the B.4 revision row, not normalized per-result metric/value rows,
  parameter tuples, inequality or optimization direction records, previous-best
  values/sources, AlphaEvolve reported-value rows, source locations,
  construction-representation schemas, construction/verifier artifact hashes,
  result-version status, recomputed values, or recomputation status.
- Appendix B.1-B.3 autocorrelation step-function provenance remains absent:
  the registry preserves the paper-facing C1-C3 labels, interval counts,
  shared `[-1/4, 1/4]` domain, sign policy, bound direction, previous
  bound/source, and reported bounds (`C1 <= 1.5053`, `0.8962 <= C2`, and
  `C3 <= 1.4557`), not local step-function payload hashes,
  domain/spacing/sign-policy certificates, verifier artifacts, recomputed
  bound rows, or recomputation certificates.
- Appendix B.8 max/min-distance point-set witness provenance remains absent:
  the registry preserves the squared-ratio convention, Figure 12 left/right
  linkage, 16-point/2D and 14-point/3D metadata, prior squared bounds
  (`12.890`, `4.168`), and reported squared ratios (`12.889266112`,
  `4.165849767`), not coordinate payload hashes, point-count/dimension
  certificates, all-pairs distance matrix artifacts, min/max pair-witness
  certificates, recomputed squared-ratio rows, or Figure 12 panel artifacts.
- Appendix B.5 Erdos minimum-overlap step-function provenance remains absent:
  the registry preserves the source formulation, `[40]` equivalence,
  normalized `[0, 2]` step-function reduction, Figure 10 result id, prior
  `0.379005 <= C5 <= 0.380927` bounds, and reported `C5 <= 0.380924` upper
  bound, not a step-function payload hash, original-formulation mapping
  certificate, `[40]` equivalence-reference artifact, shift-domain
  certificate, value-range or integral-normalization certificates,
  shift-objective recomputation, recomputed upper bound, or Figure 10 panel
  artifact.
- Appendix B.6 finite-set witness provenance remains absent: the registry
  preserves the `C6` theorem/admissibility statement, `U1`/`U2` witness labels,
  set sizes `2003` and `54265`, reported lower bounds `1.1479 <= C6` and
  `1.1584 <= C6`, and required future finite-set fields, not sorted integer
  payload hashes, contains-zero or non-negative certificates,
  `|U - U| <= 2 max(U) + 1` admissibility certificates, `|U-U|`/`|U+U|`
  cardinality certificates, max-element certificates, formula-substitution
  certificates, or recomputed lower-bound rows.
- Appendix B.7 regular-hexagon packing provenance remains absent: the registry
  preserves the unit-regular-hexagon objective, Figure 11 left/right linkage,
  prior `[29]` values, `n = 11` and `n = 12` witness summaries, and reported
  outer-side improvements (`3.943 -> 3.931` and `4.0 -> 3.942`), not placement
  payload hashes, pose/orientation schemas, inner/outer regular-hexagon
  geometry certificates, containment or non-overlap certificates, side-length
  recomputation certificates, recomputed side lengths, or Figure 11 panel
  artifacts.
- Appendix B.9-B.10 Heilbronn minimum-area provenance remains absent: the
  registry preserves Figure 13 left/middle/right linkage, B.9 triangle and
  B.10 convex-region domains, the `n = 11`, `n = 13`, and `n = 14` witness
  summaries, prior values (`0.036`, `0.0306`, `0.0277`), and reported values
  (`minimum_area > 0.0365`, `0.0309`, `0.0278`), not point-coordinate or
  domain artifact hashes, domain-membership proofs, unit-area or convexity
  certificates, triple-count enumeration, all-triples minimum-area
  certificates, minimum-witness-triangle certificates, reported-value
  comparison certificates, recomputed minimum areas, or Figure 13 panel
  artifacts.
- Appendix B.11 kissing-number proof provenance remains absent: the registry
  preserves dimension `11`, prior lower bound `592`, reported lower bound
  `593`, the 593 nonzero integral-coordinate witness count, the max-norm
  versus minimum-pairwise-distance condition, Lemma 1, and the
  `{2 x / ||x||}` sphere-center transform, not a 593-vector payload hash,
  count/dimension or exact-coordinate certificates, norm and
  pairwise-distance matrix artifacts, exact max-norm or
  minimum-pairwise-distance certificates, witness vectors/pairs, strict
  norm-distance inequality proof, Lemma 1 applicability certificate,
  transformed-center and unit-sphere certificates, kissing-angle certificate,
  or recomputed lower-bound row.
- Appendix B.12-B.13 circle/rectangle sum-of-radii provenance remains absent:
  the registry preserves Figure 14 left/middle/right linkage, `n = 26` and
  `n = 32` unit-square rows, the `n = 21` perimeter-4 rectangle row, prior
  sums (`2.634`, `2.936`, `2.364`), reported sums (`2.635`, `2.937`,
  `2.3658`), the B.13 caption display, and the checked-in 26-circle fixture
  as smoke-only, not AlphaEvolve container hashes, circle placement payloads,
  exact-count checks, payload-schema validation certificates, positive-radius
  certificates, containment or pairwise non-overlap certificates, rectangle
  dimensions, rectangle-perimeter proof, sum-of-radii formula certificates,
  recomputed sums, or Figure 14 panel artifacts.
- Appendix B.4 revised-result provenance remains absent: the registry
  preserves the first-version `C4 <= 0.3521` uncertainty-inequality result,
  Henry Cohn's pointer to the `[18]` refinement, the external `0.3284`
  constant, and AlphaEvolve's revised `0.3216` note, not local revision
  artifacts, Colab or verifier linkage, comparison-to-`0.3284` certificates,
  recomputed revised constants, artifact hashes, or proof that the current
  Appendix B value has been locally reproduced.
- Appendix B.4 prior-bound rounding provenance remains absent: the registry
  preserves the `[33]` lower bound `0.2025`, source-stated upper bound `0.353`,
  rounded comparison baseline `0.3523`, and policy that AlphaEvolve's
  first-version `C4 <= 0.3521` is compared against the rounded baseline, not a
  `[33]` page or section locator, source-solution artifact, prior-solution
  rounding artifact, rounding-audit certificate, or locally reproduced
  certificate for the `0.353` to `0.3523` distinction.
- Appendix B.4 Hermite-polynomial certificate provenance remains absent: the
  registry preserves the first-version `C4 <= 0.3521` uncertainty-inequality
  result from the Hermite basis, approximate coefficients
  `[0.32925, -0.01159, -8.9216e-5]`, `P(x)/x^2` largest-root computation, and
  `r_max^2 / (2*pi)` formula, not local coefficient payloads,
  Hermite/Fourier/root certificates, origin-condition certificates,
  eventual-nonnegative certificates, or recomputed-bound evidence.
- Appendix B.4 prior-construction similarity provenance remains absent: the
  registry preserves the paper's qualitative statement that AlphaEvolve's
  linear combination is very similar to reference `[33]` and that this supports
  a near-optimality hypothesis, not local prior/AlphaEvolve coefficient
  payloads, basis-alignment certificates, coefficient-similarity metrics,
  hypothesis-source artifacts, or proof that the near-optimality hypothesis is
  locally verified.
- Follow-on problem-repository coverage records validate pinned snapshot
  problem-page, status-bucket, link, hash, notebook-link, absence-reason,
  notebook-hash, scoped artifact-flag, Appendix B crosswalk, and
  artifact-rights-template evidence, not live repository completeness, full
  notebook cell inventories, normalized result rows, construction payloads,
  verifier artifacts, recomputed values, or copied/adapted generated artifacts.
- Follow-on problem-count wording remains snapshot-scoped: the source
  README/paper declares 67 mathematical problems, pinned diagnostics observe
  68 numbered HTML pages, and page 68 is classified as an extra duplicate-title
  `Logic puzzles` page outside the declared navigation range with a generic
  Colab landing URL and placeholder paper link.
- Paper artifact-role records validate AlphaEvolve PDF page 23 figure-creator
  and companion Google Colab assembler attribution with stable artifact ids,
  exact contributor initials, source section/page metadata, and source phrases,
  not linked rendered figure files, caption/source maps, figure-region
  artifacts, companion notebook URLs or digests, retrieved notebook exports,
  cell maps, or source-to-artifact maps.
- Systems-result schemas and readiness sidecars are report contracts only; they
  do not yet emit real scheduling, Pallas/kernel, compiler, or hardware fixture
  runs, deployment measurements, expert confirmations, or domain-specific
  result artifacts.
- Kernel report contracts do not yet prove AlphaEvolve-style Pallas/Gemini
  input-shape corpus provenance, deterministic train/eval split hashes, real
  TPU runtime artifacts, expert-baseline tiling heuristic identity, tiling-only
  candidate boundaries, unchanged-operation correctness, engineering-effort
  calibration, or production/workflow adoption.
- Pallas workflow documentation does not yet prove AlphaEvolve-style automation
  of search-based autotuning or manual tiling-heuristic work: baseline workflow
  class, retuning burden, manual review effort, hardware-expertise assumptions,
  and model-developer ergonomics remain active code and paper TODOs.
- Gemini self-training wording remains bounded: the docs do not yet prove that
  a deployed Pallas kernel optimization affected the same Gemini-family
  training workload that powered AlphaEvolve, nor before/after training metrics,
  rollout state, team-velocity evidence, or rollback/safety records.
- Hardware RTL/EDA records validate metadata only: they do not yet provide real
  Verilog/RTL source, synthesis or PPA runs, verification logs, designer
  signoff, downstream-synthesis artifacts, upcoming-chip integration, or
  deployment/time-to-market evidence.
- Hardware rewrite records are also metadata only: they do not yet provide real
  before/after Verilog files, exact diff or AST artifacts, removed-bit
  inventories, component review files, or per-bit functional and PPA evidence
  for the TPU arithmetic-circuit rewrite.
- Hardware contribution records are metadata only: they do not yet provide real
  model/run/backend records, reviewed TPU/circuit identifiers,
  novelty/firstness evidence, integration records, hardware signoff files, or
  synthesis-rediscovery audit artifacts for the Gemini-to-TPU attribution claim.
- Compiler IR records validate metadata only: they do not yet provide real
  XLA/FlashAttention edit artifacts, randomized input coverage,
  reference-check outputs, tolerance/failure logs, or expert all-input signoff.
- Compiler stack records validate metadata only: they do not yet provide real
  Transformer/inference configuration records, Pallas source snapshots, JAX
  wrapper artifacts, XLA stage outputs, hardware-target records, lowered-IR
  files, or optimization-decision evidence.
- Compiler adoption records validate metadata only: they do not yet provide
  real compiler patch/pass artifacts, use-case integration records, reviewer
  signoff files, deployment or rollback logs, or AlphaEvolve-in-compiler-loop
  evidence.
- The docs do not yet reproduce AlphaEvolve Figure 6 or Figure 7 exhibits:
  scheduling heuristic source/heatmap provenance and Pallas tiling-problem
  diagram/source-data/render hashes remain active code and paper TODOs.
- Paper-result reproduction, benchmark-scale claims, release packaging, and
  broader CI/platform guarantees remain tracked in `docs/status.md`,
  `papers/README.md`, `ROADMAP.md`, and `docs/todo/` rather than promised here.

## Install

Use Python 3.11 or newer. On this Windows machine, use `py -3.12`.

```bash
py -3.12 -m pip install -e ".[dev]"
```

Create a `.env` file at the project root for provider keys you plan to use:

```dotenv
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_HOST=http://localhost:11434
```

`.env` is loaded for `libreevolve run` with `override=True`. Do not commit API
keys.

## Quick Start

First verify the CLI and artifact writer without making any provider calls:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --run-name readme_smoke_sorting --max-llm-calls 0 --overwrite
py -3.12 -m libreevolve show runs/readme_smoke_sorting
```

That command evaluates the bundled sorting seed, writes the normal run
artifacts, and stops before constructing LLM providers. It is a smoke check, not
an evolution run.

To run evolution, choose a backend that is actually available in your
environment and account:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "openai:<openai-model-id>"
```

For Anthropic:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --max-generations 10 --backends "anthropic:<anthropic-model-id>"
```

For a local Ollama model:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "ollama:<installed-ollama-model>"
```

Inspect a run:

```bash
py -3.12 -m libreevolve show runs/hello_world
```

Use a fresh `--run-name` for repeat runs, or pass `--overwrite` when you
intentionally want to replace the existing run directory.

Provider-backed runs can spend API credits and may fail during backend preflight
if credentials, model ids, local Ollama state, or account access are not
available.

## Run Artifacts

Runs write to `runs/<run-name>/`, which is gitignored. The main outputs are
`manifest.json`, `best.py`, `best_workspace/`, evaluator/plugin artifact
folders, and the current JSONL streams:

- `archive_events.jsonl`
- `controller_budget_events.jsonl`
- `evaluator_results.jsonl`
- `failure_history.jsonl`
- `history.jsonl`
- `llm_calls.jsonl`
- `prompt_current_binding_table.jsonl`
- `prompt_history.jsonl`
- `prompt_prior_score_table.jsonl`

See [docs/run-artifacts.md](docs/run-artifacts.md) for schemas, invalid-record
quarantine streams, restore behavior, and inspection details. Archive restore
is split between cursor/counter resume via
`--restore-archive-cursor-from-manifest` and checked full archive cell/elite
snapshot restore via `--restore-archive-from-manifest`; neither path replays
`archive_events.jsonl` as an ordered MAP-Elites migration engine. Whole-run
source/workspace integrity is bounded by
`papers/whole_run_source_workspace_integrity_boundary.json`.

## How It Works

1. Load a problem directory with seed code, objective text, optional config, and
   a validator.
2. Evaluate the seed candidate.
3. Select parent programs from the archive.
4. Render a mutation prompt and call an LLM backend.
5. Parse the response as SEARCH/REPLACE diffs or full replacement code.
6. Evaluate the candidate in a subprocess and apply any configured stages.
7. Admit valid finite-scoring candidates into the program database and
   MAP-Elites archive.
8. Persist run artifacts for inspection and later analysis.

## Problem Layout

Problem directories live under `libreevolve/problems/examples/`. A minimal
problem usually includes:

- `seed.py`: initial program to evolve.
- `evaluator.py`: validator entrypoint.
- `prompt.txt` or problem metadata: task instructions for the LLM.
- optional `config.yaml`: backend, archive, prompt, and evaluator settings.

See [docs/problem-format.md](docs/problem-format.md) for the full contract.

## CLI

```bash
py -3.12 -m libreevolve --help
py -3.12 -m libreevolve run --help
py -3.12 -m libreevolve show --help
```

Common run options:

- `--max-generations`
- `--max-evaluations`
- `--max-runtime-seconds`
- `--backends`
- `--plugins`
- `--mutation-mode diff|full`
- `--parent-selection-strategy`
- `--overwrite`

## Where To Read Next

- [docs/README.md](docs/README.md): complete documentation map.
- [docs/architecture.md](docs/architecture.md): runtime architecture.
- [docs/configuration.md](docs/configuration.md): config fields and CLI
  overrides.
- [docs/backends.md](docs/backends.md): OpenAI, Anthropic, and Ollama behavior.
- [docs/plugins.md](docs/plugins.md): plugin hooks and built-in plugins.
- [docs/run-artifacts.md](docs/run-artifacts.md): files written under `runs/`.
- [docs/status.md](docs/status.md): detailed implementation and absence-boundary
  ledger.
- [ROADMAP.md](ROADMAP.md): implementation status and remaining work.
- [papers/README.md](papers/README.md): source papers, status rows, and
  claim-boundary records.

The docs are intentionally split by purpose. Setup and first-run usage belongs
here; operational details belong in `docs/`; paper-derived claim evidence
belongs in `papers/`; backlog and truthfulness checks belong in `docs/todo/`
and `ROADMAP.md`.

## Research Sources

LibreEvolve is informed by a local cache of 53 papers on LLM-guided evolution,
program synthesis, quality-diversity optimization, and related benchmarks. The
PDF cache lives locally under `papers/`, but the PDFs themselves are gitignored.
The committed repository tracks `papers/README.md`, download manifests, and
JSON source-boundary artifacts.

Manifest `title` fields are inventory/display slugs derived from cache names,
not authoritative bibliographic titles. Use `papers/README.md` for paper-facing
titles, implementation status, and benchmark coverage decisions.

`papers/README.md` is the complete implementation-status index for all 53
manifest rows. It separates implemented behavior, inspiration-only sources,
candidate benchmark ideas, and source-boundary records so the root README does
not have to carry the full research ledger.

Rehydrate the ignored local PDF cache on a fresh checkout:

```bash
py -3.12 -m libreevolve.tools.paper_manifest --rehydrate
```

Validate the paper index:

```bash
py -3.12 -m libreevolve.tools.paper_manifest
py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs
```

## Testing

Run the non-integration tests:

```bash
py -3.12 -m pytest tests/ -m "not integration" --tb=short
```

Run integration tests only when the required provider credentials are present:

```bash
py -3.12 -m pytest tests/integration/ -m integration --tb=short
```

## Repository Layout

```text
libreevolve/
  core/          orchestration, prompting, evaluation, diffing, database, config
  llm/           OpenAI, Anthropic, Ollama, and ensemble routing
  population/    program records, MAP-Elites, island migration
  plugins/       optional lifecycle hooks and paper-inspired plugins
  problems/      examples and problem loading
  tools/         paper/source manifest validation
docs/            architecture, configuration, backend, plugin, and artifact docs
papers/          tracked manifests plus ignored local PDF cache
runs/            gitignored run outputs
tests/           unit and integration tests
```

## Contributing

Keep root README changes practical and short. Detailed behavior belongs in
`docs/`, source-boundary evidence belongs in `papers/README.md` and JSON
sidecars, and long-term implementation status belongs in `ROADMAP.md` or
`docs/todo/`.

Before opening a change, run focused tests for touched code and the paper
manifest check when source-boundary files change.

GitHub Actions currently provide path-scoped Ubuntu validation for secret
scanning, Python 3.11/3.12 non-integration tests, and optional credential-gated
integration tests. Broader paper/docs CI, wheel/sdist smoke checks,
cross-platform matrices, and branch/notification policy are tracked by
`papers/ci_workflow_coverage_boundary.json`.

The secret scan uses `.secrets.baseline`. If you intentionally add synthetic
provider-looking tokens in tests or TODO evidence, use a narrow fixture marker
such as `# pragma: allowlist secret` where appropriate, or regenerate and stage
the resulting `.secrets.baseline` change. A detect-secrets report about an
unstaged baseline is a validation issue to review and stage, not a
`provider/API failure`.

## License

MIT. See [LICENSE](LICENSE).
