# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

## Missing Roadmap Items

## Existing Items That Need Tightening

- [ ] Implement CORAL autonomous multi-agent evolution gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2604.01658`, submitted April 2, 2026 and last
    revised May 17, 2026, introduces CORAL for autonomous multi-agent
    evolution on open-ended discovery tasks. The abstract says fixed
    heuristics and hard-coded exploration rules limit current LLM-based
    evolution, then proposes long-running collaborative agents with shared
    persistent memory, asynchronous execution, heartbeat-based interventions,
    isolated workspaces, evaluator separation, resource management, and agent
    session/health management. It reports state-of-the-art results on 10
    tasks, 3-10x higher improvement rates with fewer evaluations, and an
    Anthropic kernel-engineering improvement from 1363 to 1103 cycles.
  - Current evidence: ROADMAP, `papers/download_manifest.*`, and
    `papers/README.md` now include `2604.01658`, cached locally as
    `papers/2604.01658__CORAL.pdf` with byte count `3096184` and SHA-256
    `6baf82f122d884380dea1ce2a20a92fd4e75216f430f652819d56bb2b893085c`.
    ROADMAP tracks MAP-Elites islands, ring migration, async reviewer gaps,
    archive restore, benchmark/report contracts, and many search-source gates,
    but still has no local CORAL-style autonomous multi-agent evidence.
  - Required result: add roadmap gates beyond paper-cache coverage for
    `2604.01658`: source-license and linked-code status, agent-session and
    shared-memory schemas, async execution and communication traces, heartbeat
    intervention logs, isolated-workspace policy, evaluator-separation
    contract, resource-management telemetry, session health events,
    knowledge-reuse/mechanistic analyses, benchmark taxonomy,
    kernel-engineering metric records, baseline identities, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local CORAL-style autonomous multi-agent support.

- [ ] Implement AEvo harnessed meta-editing gates beyond paper cache coverage.
  - Spec evidence: arXiv `2605.13821`, submitted May 13, 2026, introduces
    AEvo as a harnessed meta-editing framework for agentic evolution. The
    abstract says fixed procedures are rigid, general-purpose agents can drift
    in long-horizon evolution, and both accumulate useful evidence that lacks
    a stable interface for revising the mechanism that drives future
    evolution. AEvo turns accumulated candidates, feedback, traces, and
    failures into process-level state and lets a meta-agent edit the procedure
    or agent context controlling future evolution, reporting a 26 relative
    improvement over the strongest baseline and state-of-the-art performance
    on three open-ended optimization tasks.
  - Current evidence: ROADMAP, `papers/download_manifest.*`, and
    `papers/README.md` now include `2605.13821`, cached locally as
    `papers/2605.13821__AEvo.pdf` with byte count `1450611` and SHA-256
    `40b5c2cde5b1886488a67b511d7dd780756304a5714d8b3261b8fe35e47beba0`.
    ROADMAP tracks static config, parent selection, prompt construction, run
    artifacts, benchmark contracts, and many search-source gates, but still
    has no local AEvo-style harnessed meta-editing evidence.
  - Required result: add roadmap gates beyond paper-cache coverage for
    `2605.13821`: source-license metadata, process-level state schema,
    accumulated evidence inventory, meta-agent observation and action
    contracts, procedure/context patch records, control-edit provenance,
    rollback/versioning policy, drift/stability diagnostics, iteration-budget
    accounting, benchmark taxonomy, baseline identities, and a background-only
    or benchmark-fixture status rule so roadmap claims do not outpace local
    AEvo-style harnessed meta-editing support.

- [ ] Implement G-Zero verifier-free co-evolution gates beyond paper cache
      coverage.
  - Spec evidence: arXiv `2605.09959`, submitted May 11, 2026, introduces
    G-Zero for open-ended generation from zero data. The abstract says
    self-evolving LLMs struggle outside verifiable domains because proxy LLM
    judges can cap capabilities and invite reward hacking. G-Zero replaces
    external judges with verifier-free co-evolution: `Hint-delta` measures the
    predictive shift from self-generated hints, a Proposer uses GRPO to target
    Generator blind spots with queries and hints, and the Generator uses DPO
    to internalize improvements.
  - Current evidence: ROADMAP, `papers/download_manifest.*`, and
    `papers/README.md` now include `2605.09959`, cached locally as
    `papers/2605.09959__G_Zero.pdf` with byte count `1980993` and SHA-256
    `97ba152b7208e1d8d2f0f1bcf4fe293419e485a568217a6ed8ea50214f5357c9`.
    ROADMAP tracks evaluator contracts, validator subprocesses,
    benchmark-report artifacts, reward/scoring gaps, and many self-evolution
    source gates, but still has no local verifier-free co-evolution evidence.
  - Required result: add roadmap gates beyond paper-cache coverage for
    `2605.09959`: source-license metadata, Generator/Proposer role schema,
    Hint-delta reward records, unassisted and hint-conditioned response pairs,
    query/hint artifact storage, GRPO/DPO training traces, intrinsic-reward
    calibration, exploration coverage reports, pseudo-label noise filtering,
    reward-hacking diagnostics, open-ended task taxonomy,
    theoretical-assumption records, baseline identities, and a background-only
    or benchmark-fixture status rule so roadmap claims do not outpace local
    G-Zero-style verifier-free support.

- [ ] Implement GenEvolve multimodal trajectory-distillation gates beyond
      paper cache coverage.
  - Spec evidence: arXiv `2605.21605`, submitted May 20, 2026 and last revised
    May 22, 2026, introduces GenEvolve for self-evolving image-generation
    agents. The abstract models each generation attempt as a tool-orchestrated
    trajectory that gathers evidence, selects references, invokes generation
    skills, and creates a prompt-reference program. It compares multiple
    trajectories for the same request, abstracts best-worst differences into
    structured visual experience for a privileged teacher, and distills dense
    token-level supervision into a student.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2605.21605`, cached locally as
    `papers/2605.21605__GenEvolve.pdf` with byte count `23833361` and
    SHA-256
    `2e38145ffd81f1c2f67b9fe4ee9adeec6284796739616d2778c89600b4455d5c`.
    ROADMAP tracks the paper as background multimodal trajectory-distillation
    context only. It still has no local image-generation agent, multimodal
    tool-trajectory schema, reference/evidence selection log, prompt-reference
    program artifact, best-worst comparison record, structured visual
    experience taxonomy, teacher/student distillation trace, token-supervision
    metadata, image artifact lineage, GenEvolve-Data metadata,
    GenEvolve-Bench report, or baseline comparison.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license and project URL status, multimodal tool-trajectory schema,
    reference/evidence selection logs, prompt-reference program artifacts,
    best-worst comparison records, structured visual experience taxonomy,
    privileged teacher and student distillation traces, token-supervision
    metadata, image artifact lineage, GenEvolve-Data/GenEvolve-Bench metadata,
    baseline identities, and a background-only or benchmark-fixture status
    rule so roadmap claims do not outpace local GenEvolve-style multimodal
    support.

- [ ] Implement EvoRubric self-evolving reward-rubric gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2605.29847`, submitted May 28, 2026, introduces
    EvoRubric for rubric-driven RL in open-ended generation. The abstract says
    static human rubrics cause policy lag and external dynamic rubric
    generators are expensive; EvoRubric instead alternates a single policy
    between Reasoner and Rubric Generator roles, validates criteria with a
    meta-verifier, zero-variance pruning, and Leave-One-Out peer consensus,
    archives validated criteria into memory, and produces dense
    multi-objective rewards.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2605.29847`, cached locally as
    `papers/2605.29847__EvoRubric.pdf` with byte count `1089746` and
    SHA-256
    `3579085619610d97a03019d495a584c6dfce76f4ea951dda3103f02395bec1d5`.
    ROADMAP tracks the paper as background self-evolving reward-rubric
    context only. It still has no Reasoner/Rubric-Generator role schema,
    generated-rubric provenance, meta-verifier or peer-consensus records,
    zero-variance pruning outcomes, criteria memory-pool artifacts, dense
    reward-vector definitions, reward-hacking diagnostics, expert-prior
    initialization records, medical/writing/science benchmark metadata, or
    baseline identities.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license metadata, linked-code or project URL status, Reasoner/
    Rubric-Generator role schema, generated-rubric provenance, meta-verifier
    and peer-consensus records, zero-variance pruning outcomes, criteria
    memory-pool artifacts, dense reward-vector definitions, reward-hacking
    diagnostics, expert-prior initialization records, medical/writing/science
    benchmark metadata, baseline identities, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    EvoRubric-style reward-rubric support.

- [ ] Implement LLM-ALSO adaptive learning-signal gates beyond paper cache
      coverage.
  - Spec evidence: arXiv `2605.29293`, submitted May 28, 2026, introduces
    LLM-ALSO for LLM-driven adaptive learning-signal optimization in
    sparse-reward cooperative multi-agent reinforcement learning. The abstract
    says it decomposes reward adaptation into iterative diagnosis, proposal,
    and validation: a Critic LLM diagnoses stage-specific learning and
    coordination failures from sparse-return metrics and compact behavior
    evidence, a Generator LLM proposes reward-shaping configurations, and
    branch-validation feedback refines candidates before they affect the main
    training trajectory.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2605.29293`, cached locally as
    `papers/2605.29293__LLM_ALSO.pdf` with byte count `712323` and SHA-256
    `06b9bcb459f40437119f2c95153985a0e8682e0509ca12be9bd5f32147c888f5`.
    ROADMAP tracks the paper as background learning-signal optimization
    context only. It still has no sparse-reward MARL learning-signal gate,
    Critic/Generator role schema, sparse-return and compact-behavior evidence
    records, stage-specific diagnosis artifacts, reward-shaping configuration
    records, branch-validation traces, update-promotion criteria,
    main-training trajectory provenance, sparse-reward cooperative MARL
    benchmark metadata, learning-efficiency metrics, or baseline identities.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license metadata, linked-code or project URL status,
    Critic/Generator role schema, sparse-return and compact-behavior evidence
    records, stage-specific diagnosis artifacts, reward-shaping configuration
    records, branch-validation traces, update-promotion criteria,
    main-training trajectory provenance, sparse-reward cooperative MARL
    benchmark metadata, learning-efficiency metrics, baseline identities, and
    a background-only or benchmark-fixture status rule so roadmap claims do
    not outpace local LLM-ALSO-style learning-signal support.

- [ ] Implement MemEvolve meta-evolving memory-architecture gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2512.18746`, submitted December 21, 2025, introduces
    MemEvolve for meta-evolution of agent memory systems. The abstract says
    memory enables agents to store trajectories, distill experience, and
    synthesize reusable tools, but existing systems keep the memory
    architecture itself static. MemEvolve jointly evolves experiential
    knowledge and memory architecture, and EvolveLab defines a modular
    encode/store/retrieve/manage design space distilled from twelve memory
    systems, with up to 17.06% framework improvements and cross-task/cross-LLM
    generalization.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2512.18746`, cached locally as
    `papers/2512.18746__MemEvolve.pdf` with byte count `10951239` and
    SHA-256
    `51ca8a0ca349b7ad111b5380148c6dd34fa4d16f933ac58677fc2246b1566dd5`.
    ROADMAP tracks the paper as background memory-architecture evolution
    context only. It still has no meta-memory architecture gate, encode/store/
    retrieve/manage component schema, memory-architecture genotype,
    experiential-knowledge records, joint content/architecture evolution
    traces, memory mutation/evaluation policy, static-memory baseline
    identities, EvolveLab benchmark metadata, cross-task/cross-LLM transfer
    reports, or performance-delta records.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license and linked-code status, encode/store/retrieve/manage
    component schema, memory-architecture genotype, experiential-knowledge
    records, joint content/architecture evolution traces, memory
    mutation/evaluation policy, static-memory baseline identities, EvolveLab
    benchmark metadata, cross-task/cross-LLM transfer reports,
    performance-delta records, and a background-only or benchmark-fixture
    status rule so roadmap claims do not outpace local MemEvolve-style memory
    support.

- [ ] Implement ANCHOR healthy-evolution oversight gates beyond paper cache
      coverage.
  - Spec evidence: arXiv `2606.06114`, submitted June 4, 2026, introduces
    Agent Norm Correction through Human-like Oversight and Review (ANCHOR) in
    `Towards Healthy Evolution: Exploring the Role and Mechanisms of
    Human-Agent Interaction in Self-Evolving Systems`. The abstract says
    autonomous self-evolving agents can suffer capability degradation and
    safety drift, and that simulated human supervision at different phases of
    self-evolution can mitigate safety degradation while preserving core
    evolutionary-objective performance. It also reports that supervising the
    output verification phase is most effective and that increasing
    supervision frequency yields diminishing returns.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2606.06114`, cached locally as
    `papers/2606.06114__ANCHOR_Healthy_Evolution.pdf` with byte count
    `2711376` and SHA-256
    `0d54f3a598c56fa69137ed4f35d8527734dff851de4a5248a777b5abfb822414`.
    ROADMAP tracks the paper as background healthy-evolution oversight context
    only. It still has no ANCHOR gate, human-like oversight records, phase-
    specific norm-correction feedback, safety-drift measurement,
    output-verification intervention logs, supervision-cadence evidence,
    objective-preservation reports, coding/math/safety benchmark metadata, or
    baseline identities.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license metadata, linked-code or project URL status, ANCHOR
    oversight role schema, phase-specific supervision taxonomy,
    norm-correction feedback artifacts, output-verification intervention logs,
    safety-drift and capability-degradation metrics, objective-preservation
    reports, supervision-frequency/cadence experiment records,
    coding/math/safety benchmark metadata, baseline identities, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local ANCHOR-style human-like oversight support.

- [ ] Implement SIA harness-plus-weight self-improvement gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2605.27276`, submitted May 26, 2026, introduces
    `SIA: Self Improving AI with Harness & Weight Updates`. The abstract says
    previous self-improvement work often separates harness/scaffold updates
    from model-weight updates, then proposes a Feedback-Agent that updates
    both the harness and weights of a task-specific agent. It evaluates
    Chinese legal charge classification, low-level GPU kernel optimization,
    and single-cell RNA denoising, and reports that combining both levers
    outperforms scaffold iteration alone on all three benchmarks.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2605.27276`, cached locally as `papers/2605.27276__SIA.pdf`
    with byte count `993538` and SHA-256
    `3f75a62487a5fb3fc2db8d06b78e6f6d598fc46b446cdfa9e205c33fb41de265`.
    ROADMAP tracks the paper as background harness-plus-weight
    self-improvement context only. It still has no SIA gates,
    Feedback-Agent decision log, editable harness components for
    task-specific agents, online model-weight updates, adapter/checkpoint
    provenance, or ablations separating harness-only, weight-only, and
    combined improvement loops.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license and linked-code status, Meta-Agent/Target-Agent/
    Feedback-Agent schemas, editable harness component inventory, harness
    patch/version records, weight-update trigger and training records,
    adapter/checkpoint lifecycle, training-data lineage, verifier/reward
    sufficiency checks, rollback/resume policy, harness-only versus
    weight-only versus combined ablation metadata, LawBench/kernel/scRNA
    benchmark records, compute/cost telemetry, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    SIA-style harness-plus-weight self-improvement support.

- [ ] Implement HarnessFix trace-grounded harness repair gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2606.06324`, submitted June 4, 2026, introduces
    HarnessFix in `From Failed Trajectories to Reliable LLM Agents:
    Diagnosing and Repairing Harness Flaws`. The abstract frames harnesses as
    the substrate for execution environments, tool interfaces, context,
    lifecycle orchestration, observability, verification, and governance, then
    argues that final-outcome-only self-improvement can make broad or poorly
    scoped harness changes. HarnessFix normalizes failed trajectories and
    harness code into HTIR, attributes failures to responsible steps and
    harness layers, consolidates flaw records, maps them to scoped repair
    operators, and validates patches with regression constraints.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO
    coverage now include `2606.06324`, cached locally as
    `papers/2606.06324__HarnessFix.pdf` with byte count `2363715` and
    SHA-256
    `00a4236ba8ab24925e3b0409b4c003bd22c57d76faabc888f20734fba5e4cafd`.
    ROADMAP tracks the paper as background trace-grounded harness repair
    context only. It still has no trace-grounded harness repair gate, HTIR-
    like trace normalization, failure-to-harness-layer attribution, recurring
    flaw records, scoped harness repairs, or validation of harness patches
    against target-flaw reduction and unacceptable-regression bounds.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license metadata, linked-code or project URL status, HTIR schema,
    raw-trace normalization, harness-code linkage, step-level provenance,
    harness-layer attribution taxonomy, recurring flaw records, repair
    operator definitions, harness patch/version artifacts, flaw-specific
    validation specs, regression-bound telemetry, held-out benchmark records,
    SWE-Bench/Terminal-Bench/GAIA/AppWorld metadata, baseline identities, and
    a background-only or benchmark-fixture status rule so roadmap claims do
    not outpace local HarnessFix-style trace-grounded harness repair support.

- [ ] Implement RHO retrospective self-preference harness optimization gates
      beyond paper cache coverage.
  - Spec evidence: arXiv `2606.05922`, submitted June 4, 2026, introduces
    Retrospective Harness Optimization (RHO) in `Improving LLM Agents via
    Self-Preference over Trajectory Rollouts`. The abstract says RHO improves
    an agent harness without ground-truth validation labels by selecting a
    diverse coreset of challenging past-trajectory tasks, re-solving them in
    parallel, analyzing rollouts with self-validation and self-consistency,
    generating candidate harness updates, and selecting the most effective
    update through pairwise self-preference.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2606.05922`, cached locally as
    `papers/2606.05922__RHO.pdf` with byte count `1267774` and SHA-256
    `75b126a2a6350e8ff58c0e6c7f3366894e23f0610f533ac533fc3e3214aa7cd4`.
    ROADMAP tracks the paper as background retrospective harness optimization
    context only. It still has no retrospective label-free harness optimizer
    gate, hard/diverse coreset selection from past trajectories, parallel re-
    rollout batches for harness comparison, self-validation or self-
    consistency analyses, pairwise self-preference ranking for candidate
    harness updates, or long-horizon behavior-pattern evidence before
    promoting self-supervised harness optimization claims.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license metadata, linked-code and project URL status, past-
    trajectory corpus schema, coreset difficulty/diversity criteria, DPP
    coreset records, retrospective rollout batch records, parallel re-solve
    provenance, self-validation and self-consistency evidence, candidate
    harness-update artifacts, pairwise self-preference ranking, label-free
    selection policy, deployment/rollback metadata, long-horizon behavior-
    pattern reports, SWE-Bench Pro benchmark records, baseline identities,
    and a background-only or benchmark-fixture status rule so roadmap claims
    do not outpace local RHO-style retrospective harness optimization support.

- [ ] Implement harness-updating versus harness-benefit gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2605.30621`, submitted May 28, 2026, introduces
    `Harness Updating Is Not Harness Benefit: Disentangling Evolution
    Capabilities in Self-Evolving LLM Agents`. The abstract distinguishes
    generating useful persistent harness updates from actually benefiting
    from those updates during task solving. It reports flat harness-updating
    across base capability tiers, non-monotonic harness-benefit with mid-tier
    agents benefiting most, and weak-agent failure modes around harness
    artifact activation and faithful long-horizon following.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2605.30621`, cached locally as
    `papers/2605.30621__Harness_Updating_Is_Not_Harness_Benefit.pdf` with
    byte count `2463998` and SHA-256
    `a3a09f90dc278f1c6ceee5a3f7bf807b5a92b642cbcb0123d20b824a0e880d6b`.
    ROADMAP tracks the paper as background harness-capability
    disentanglement context only. It still has no separate harness-updating
    and harness-benefit readiness gates, artifact activation metrics,
    adherence measurement for updated harness instructions over long
    trajectories, model-tier comparison for evolver versus task-solving
    roles, or capability-budget evidence before promoting harness self-
    evolution gains.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license and linked-code status, harness-updating metric schema,
    harness-benefit metric schema, evolver/task-agent pairing matrix,
    persistent harness update records, harness artifact activation/load
    telemetry, adherence/following traces, long-horizon instruction-following
    reports, model-tier taxonomy, weak/mid/strong baseline identities,
    capability-budget accounting, benchmark records for SWE-Bench Verified,
    MCP-Atlas, and SkillsBench if reproduced, and a background-only or
    benchmark-fixture status rule so roadmap claims do not conflate harness
    update generation with downstream harness benefit.

- [ ] Implement AHE observability-driven harness evolution gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2604.25850`, submitted April 28, 2026, introduces
    `Agentic Harness Engineering: Observability-Driven Automatic Evolution of
    Coding-Agent Harnesses`. The abstract describes a closed loop with
    component observability, experience observability, and decision
    observability: editable harness components are file-level and revertible,
    raw trajectories are distilled into layered evidence, and each edit is
    paired with a prediction verified against later task outcomes.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2604.25850`, cached locally as
    `papers/2604.25850__AHE.pdf` with byte count `1432986` and SHA-256
    `299f2633b4c13db7bed52434b4db7c48ea621993581014d30e7bcd036d3464df`.
    ROADMAP tracks the paper as background agentic harness observability
    context only. It still has no AHE readiness gates, file-level harness
    component inventories, layered trajectory evidence corpora, edit
    prediction records, next-round outcome verification, component-class gain
    attribution, or frozen-harness transfer reports before promoting
    autonomous harness evolution claims.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license and linked-code status, editable component taxonomy, file-
    level harness component manifests, revertible edit records, experience-
    evidence distillation schema, drill-down trajectory corpus links,
    decision-observability records, edit-prediction and outcome-verification
    telemetry, falsifiable contract status, iteration traces,
    tool/middleware/memory attribution reports, frozen-harness transfer
    benchmark records, Terminal-Bench 2 and SWE-bench Verified metadata,
    baseline identities, token/cost accounting, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local AHE-
    style observability-driven harness evolution.

- [ ] Implement AI Harness Engineering runtime-substrate gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2605.13357`, submitted May 13, 2026, introduces
    `AI Harness Engineering: A Runtime Substrate for Foundation-Model Software
    Agents`. The abstract reframes software-engineering capability as emerging
    from a model-harness-environment system and names eleven harness
    responsibilities: task specification, context selection, tool access,
    project memory, task state, observability, failure attribution,
    verification, permissions, entropy auditing, and intervention recording.
    It proposes an H0-H3 ladder and an auditable episode-package protocol.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2605.13357`, cached locally as
    `papers/2605.13357__AI_Harness_Engineering.pdf` with byte count `263956`
    and SHA-256
    `a1e2d7ce307c662411ca6bd5f833d7dae7f122ce6ef1ddd6d2370e82575b2fb9`.
    ROADMAP tracks the paper as background AI harness runtime-substrate
    context only. It still has no general runtime-substrate gate, all-eleven-
    responsibility harness contract, H0-H3 maturity levels, episode packages,
    maintenance-entropy audit, human-intervention logs, or structured
    requirement-level verification evidence tied to task completion.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license metadata, model-harness-environment schema, eleven
    responsibility records, H0-H3 harness-level taxonomy, runtime-resource
    exposure matrix, task/context/tool/memory/state records, observability
    traces, failure-attribution logs, verification protocol/report artifacts,
    permission-boundary events, entropy audits, intervention logs, episode-
    package records, deterministic requirement-check evidence, maintenance-
    burden reports, controlled validation metadata, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local AI-
    harness runtime-substrate support.

- [ ] Implement inference-time trajectory-alignment harness gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2605.21516`, submitted May 15, 2026, introduces
    `Harnesses for Inference-Time Alignment over Execution Trajectories`. The
    abstract says more decomposition or guidance can improve execution but can
    also reduce final task success. It separates harness design into task
    decomposition and guided execution, analyzes workflow granularity, retry
    budgets, and guidance-induced action reweighting, and identifies
    over-decomposition, over-pruning, hallucinated execution, and partial
    harnessing tradeoffs.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2605.21516`, cached locally as
    `papers/2605.21516__Inference_Time_Trajectory_Alignment.pdf` with byte
    count `2323632` and SHA-256
    `5458d316fd5edbfda5cf7355592d41e0c5f3f889e31c92855728c47452f6ca32`.
    ROADMAP tracks the paper as background inference-time trajectory-
    alignment context only. It still has no decomposition/guidance parameter
    gates, pass-rate plus final-bias reporting, retry-budget sensitivity
    measurement, over-structured workflow failure-mode inventory, partial
    versus fully structured harness comparison, or alignment evidence before
    promoting increasingly structured harness workflows.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license metadata, harness parameter schema, decomposition-
    granularity records, guidance-strength and guidance-rule records, sub-
    goal sequence artifacts, trajectory/action distribution records, retry-
    budget sensitivity reports, pass-rate and final-bias metrics,
    granularity-capability alignment reports, guidance-evidence alignment
    reports, over-decomposition/over-pruning/hallucinated-execution
    diagnostics, partial-harness benchmark records, Terminal-Bench-2 and
    synthetic task metadata, baseline identities, and a background-only or
    benchmark-fixture status rule so roadmap claims do not treat more harness
    structure as automatically better.

- [ ] Implement Adaptive Auto-Harness open-ended task-stream gates beyond
      paper cache coverage.
  - Spec evidence: arXiv `2606.01770`, submitted June 1, 2026, introduces
    `Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System
    Deployment on Open-Ended Task Streams`. The abstract says fixed offline
    benchmarks miss deployment conditions where histories grow, tasks are
    heterogeneous, and distributions shift. It warns that a single densely
    updated harness can become brittle, decomposes the oracle-harness gap into
    evolution loss and adaptation loss, and uses a stateful multi-agent
    evolver, harness tree, solve-time routing, and human-steering hooks for
    task-wise adaptation.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO coverage
    now include `2606.01770`, cached locally as
    `papers/2606.01770__Adaptive_Auto_Harness.pdf` with byte count `1895729`
    and SHA-256
    `50454c1eec069b668b515c6d322e4c5ac55f24655298b3381f91f461a9c39b3e`.
    ROADMAP tracks the paper as background adaptive auto-harness deployment
    context only. It still has no open-ended task-stream deployment gates,
    history-growth or distribution-shift evidence, evolution/adaptation loss
    separation, harness tree, solve-time routing to harness variants, or human
    steering records for cases where historical evidence is insufficient.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license and linked-code status, open-ended task-stream schema,
    history-growth records, task-heterogeneity and distribution-shift
    telemetry, oracle-harness definition, evolution-loss/adaptation-loss
    metrics, stateful multi-agent evolver schemas, cross-cycle memory, harness
    tree records, solve-time routing telemetry, human-steering hook records,
    targeted-steering outcomes, sustained-performance and degradation curves,
    prediction-market/security-competition/event-forecasting benchmark
    records, baseline/ablation identities, and a background-only or benchmark-
    fixture status rule so roadmap claims do not outpace local Adaptive Auto-
    Harness-style sustained deployment support.

- [ ] Implement Meta-Harness outer-loop harness-code search gates beyond paper
      cache coverage.
  - Spec evidence: arXiv `2603.28052`, submitted March 30, 2026, introduces
    `Meta-Harness: End-to-End Optimization of Model Harnesses`. The abstract
    frames harness code as the mechanism controlling what information an LLM
    system stores, retrieves, and presents, then searches over that harness
    code with an agentic proposer that inspects prior source code, scores, and
    execution traces through a filesystem.
  - Current evidence: ROADMAP, `papers/download_manifest.*`,
    `papers/row_identity.json`, `papers/README.md`, README, and TODO
    coverage now include `2603.28052`, cached locally as
    `papers/2603.28052__Meta_Harness.pdf` with byte count `1078140` and
    SHA-256
    `7d9b90f53a9f4801a090f1a4acb843340cde81e4f865f97d53fff2a6a570eb73`.
    ROADMAP tracks the paper as background outer-loop harness-code
    optimization context only. It still has no harness-code candidate
    schema, filesystem-visible harness workspace, agentic proposer trace,
    execution-trace feedback bundle, multi-objective harness search
    controller, cross-task benchmark, or generalization/overfit gate before
    promoting end-to-end harness optimization claims.
  - Required result: implement roadmap gates beyond paper-cache evidence:
    source-license and linked-code status, harness-code candidate schema,
    filesystem-visible harness workspace layout, agentic proposer trace
    records, candidate harness edit provenance, execution-trace feedback
    bundles, score/provenance replay packages, multi-objective harness
    search controller, cross-task task-distribution splits, generalization/
    overfit reports, GSM8K/GPQA/InteractiveQA/ToolQA/TruthfulQA/LLF-Bench
    benchmark records, baseline identities, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    Meta-Harness-style end-to-end harness optimization support.

- [ ] Add AlphaEvolve MARL algorithm-discovery gates before roadmap
      promotion.
  - Spec evidence: arXiv `2602.16928`, submitted February 18, 2026 and last
    revised May 7, 2026, introduces `Discovering Multiagent Learning
    Algorithms with Large Language Models`. The abstract says AlphaEvolve is
    deployed over CFR and PSRO design spaces, producing VAD-CFR and SHOR-PSRO,
    evaluating them on an 18-game suite across Poker, Goofspiel, Liar's Dice,
    Blotto, and Battleship variants, and distilling them through systematic
    ablations into WOP-CFR and PM-PSRO minimal solvers with improved
    generalization and reduced complexity. The paper uses OpenSpiel, exact
    exploitability by full game-tree traversal, deterministic metrics, and
    separate CFR/PSRO Python class skeletons as the AlphaEvolve search space.
  - Current evidence: ROADMAP now names
    `papers/multiagent_learning_boundary.json` as the source-specific
    boundary for CFR/PSRO candidate schemas, OpenSpiel imperfect-information
    game fixtures, exploitability metrics, exact-oracle PSRO records,
    VAD-CFR/SHOR-PSRO rows, WOP-CFR/PM-PSRO distillation rows, IQM ablation
    audits, random normal-form validation, generated solver artifacts, and
    runtime-repository status. It still does not define CFR or PSRO candidate
    schemas, require an imperfect-information game evaluator, preserve
    train/evaluation game splits, track VAD-CFR or SHOR-PSRO mechanism
    provenance, require mechanism-coupling ablations, or define
    distilled-solver handoff and generalization gates for WOP-CFR and PM-PSRO.
  - Required result: implement roadmap gates for `2602.16928`: CFR and PSRO
    candidate schemas, game-suite taxonomy, train/evaluation split hashes,
    evaluator protocol and metric definitions, exact exploitability and exact
    best-response oracle records, random-seed and budget records, baseline
    solver identities, VAD-CFR and SHOR-PSRO result tables, mechanism-coupling
    IQM ablation records, structural-complexity metrics, distilled
    WOP-CFR/PM-PSRO solver records, random normal-form validation rows,
    limitation/caveat records for scale, LLM trajectory, and baseline scope,
    generalization reports, and benchmark-fixture status rules before roadmap
    claims promote MARL algorithm-discovery support.

- [ ] Add AlphaEvolve Ramsey-number discovery gates before roadmap promotion.
  - Spec evidence: arXiv `2603.09172`, submitted March 10, 2026 and last
    revised April 21, 2026, introduces `Reinforced Generation of
    Combinatorial Structures: Ramsey Numbers`. The abstract says AlphaEvolve
    improved lower bounds for nine Ramsey numbers, recovered all exact known
    lower bounds, matched many other best-known lower bounds, and served as a
    single meta-algorithm yielding search algorithms across those cases. The
    paper body defines the roadmap target as constructive lower-bound
    witnesses: an `n`-vertex graph free of `r`-cliques and `s`-independent
    sets proves `R(r,s) >= n+1`; Algorithm 1 evolves programs from an empty
    baseline that emit `G1` and prospect `G2`, scoring size and low violations
    against an expected random-graph baseline; Table 1 covers 28 colored
    cells; Table 2 groups initialization families; and the PDF links public
    Google Research construction and search-code artifacts.
  - Current evidence: ROADMAP now names `papers/ramsey_numbers_boundary.json`
    as the source-specific boundary for graph candidate schemas, `run()`
    primary/prospect graph contracts, clique/independent-set verifiers,
    new/matched/exact lower-bound rows, Google Research construction/code
    links, graph and algorithm artifact hashes, initialization-family records,
    graph-size-to-lower-bound semantics, and independent checker outputs. It
    still does not define Ramsey graph witness schemas, require `R(s,t)`
    lower-bound verifier artifacts, store exact-bound recovery records,
    compare matched best-known bounds, or require a result table that
    attributes the nine prior/current lower-bound improvements.
  - Required result: implement roadmap gates for `2603.09172`: Ramsey
    candidate representation, graph/witness artifact schema,
    verifier/certifier entrypoints, parameterized `R(s,t)` result rows,
    exact-bound recovery suite, best-known-bound comparison table,
    prior/current value provenance, search-algorithm provenance, seed/budget
    records, witness graph hashes, independent checker outputs, failure and
    negative-result records, and benchmark-fixture status rules before roadmap
    claims promote Ramsey discovery support. Roadmap promotion should
    additionally require exact
    `R(r,s) >= n+1` witness semantics, primary/prospect graph run artifacts,
    expected-violation formula inputs, imported or reproducibly regenerated
    Google Research construction/code artifacts, 28-cell Table 1 and
    34-algorithm appendix traceability, initialization-family coverage, and
    comparison rows for Radziszowski 2024, Exoo/Tatarevic 2015, Exoo 2006,
    Tatarevic 2020, Exoo 2012, Harborth/Krause 2003, plus explicit
    graph-only/personal-communication limitations.

- [ ] Add AlphaEvolve local-correction combinatorics gates before roadmap
      promotion.
  - Spec evidence: arXiv `2603.06692`, submitted March 4, 2026, introduces
    `Evolving Local Corrections for Global Constructions in Combinatorics`.
    The abstract uses AlphaEvolve to propose and refine finite correcting-step
    certificates for graph reconstruction, Latin-square Alon-Tarsi parity via
    local trades and sign-reversing involutions, and Rota's Basis Conjecture
    through local exchange policies. It reports experimental setups, scoring
    protocols, and outcomes that suggest conjectures, not completed proofs.
    The body defines fixed mathematical harnesses, short Python evolvable
    blocks, random symmetry-scramble robust scoring, hard constraints plus soft
    progress, hard-negative replay, and appendix evolved-code/Gemini-summary
    artifacts across the three case studies.
  - Current evidence: ROADMAP now names
    `papers/combinatorics_berczy_boundary.json` as the source-specific
    absence boundary for Berczy local-correction combinatorics. It still does
    not promote `2603.06692` beyond potential-future-benchmark status, define a
    local-correction certificate abstraction, require finite correcting-step
    traces, provide graph reconstruction, Latin-square trade, or Rota
    basis-exchange fixtures, preserve scoring protocols, or distinguish
    AlphaEvolve-suggested conjectures from verified/proved mathematical
    results. It also lacks promotion gates for the paper's exact result
    surfaces: bipartite `1420/1420` and planar `896/896` reconstruction
    ledgers, Alon-Tarsi validity/involution/sign-flip/locality/isotopy tables,
    Rota rank-5/rank-7/variable-rank `F2` circuit-rich pool benchmarks,
    appendix evolved-code traceability, AI-summary provenance, and explicit
    evaluator-hardening records for WL-surrogate-to-exact-isomorphism
    transitions.
  - Required result: implement roadmap promotion gates for `2603.06692`:
    local-correction candidate schema, finite-step trace artifacts,
    graph-reconstruction benchmark records, vertex-deleted subgraph schemas,
    Latin-square local-trade and sign-reversing-involution records, Rota
    basis-family and local-exchange-policy records, scoring protocols,
    seed/budget records, generated-algorithm artifacts, structural-pattern
    summaries, conjecture/proof-status fields, independent checker hooks, and
    a background-only or benchmark-fixture status rule so roadmap claims do
    not outpace local AlphaEvolve-style local-correction combinatorics
    support. Roadmap promotion should additionally require Conjectures 4-11
    and Tables 1-6 to map to local benchmark schemas; exact graph deck
    equality, Latin-square involution/sign, and Rota circuit-oracle validators;
    result rows for experiment IDs `0_9751`, `0_9774`, and `0_7176`; majority
    rollout and symmetry-scramble robustness reports; appendix-code artifact
    hashes; and documentation gates that keep AI-generated summaries and
    experimental conjectures separate from proof-grade claims.

- [ ] Add AlphaEvolve bilateral-trade mechanism-design gates before roadmap
      promotion.
  - Spec evidence: arXiv `2603.08679`, submitted March 9, 2026, introduces
    `A New Lower Bound for the Random Offerer Mechanism in Bilateral Trade
    using AI-Guided Evolutionary Search`. The abstract uses AlphaEvolve to
    search value distributions for a worst-case Random-Offerer instance and
    reports `GFT_FB / GFT_RO >= 2.0749`, widening the known gap between
    first-best efficiency and Random-Offerer gains from trade. The body
    specifies the roadmap target as a discrete bilateral-trade witness:
    independent seller and buyer distributions, first-best `E[(b-s)+]`, RO as
    equal randomization between optimal seller-offering and buyer-offering
    prices, fixed Discrete Equal Revenue buyer, evolved seller CDF over
    `H=20000`, `1e-15` rounded integer arithmetic, exact GFT computation, and
    a modulated-power-law seller distribution yielding the reported component
    values and ratio.
  - Current evidence: ROADMAP now names `papers/bilateral_trade_boundary.json`
    as the source-specific absence boundary for Bilateral Trade
    mechanism-design evidence. It still does not promote `2603.08679` beyond
    background-only status, define a
    bilateral-trade distribution benchmark, compute first-best versus
    Random-Offerer GFT, preserve BIC/BB assumptions, compare prior
    counterexample baselines, or verify lower-bound witness distributions. It
    also lacks gates for fixed-buyer/evolved-seller search, equal-revenue buyer
    survival-function fixtures, CDF/SF/PMF rounding validation, SO/BO
    optimal-price records, appendix evaluator traceability, and the
    rounded-versus-unrounded result caveat.
  - Required result: implement roadmap promotion gates for `2603.08679`:
    value-distribution candidate schema, buyer/seller support and probability
    constraints, FB and RO GFT evaluator records, BIC/BB assumption metadata,
    ratio objective and tolerance policy, witness distribution artifacts,
    prior lower-bound/counterexample baselines, seed/budget records,
    independent checker outputs, and a background-only or benchmark-fixture
    status rule so roadmap claims do not outpace local AlphaEvolve-style
    bilateral-trade lower-bound support. Roadmap promotion should additionally
    require the `H=20000` discrete evaluator, Discrete Equal Revenue buyer,
    evolved seller CDF formula and code artifact, exact FB/SO/BO/RO component
    rows, reserve-price witness logs, `1e-15` rounding policy, appendix
    evaluator hash, comparison to the `2` conjecture and Babaioff et al.
    `~2.02` baseline, source-scoped handling of the not-detailed `2.08`
    alternating-search result, and documentation that the verified claim is
    for the rounded distribution while the exact unrounded-mixture ratio is
    open.

- [ ] Add AlphaEvolve Magellan compiler-optimization gates before roadmap
      promotion.
  - Spec evidence: arXiv `2601.21096`, submitted January 28, 2026 and
    accepted to `C4ML@CGO'26`, introduces `Magellan: Autonomous Discovery of
    Novel Compiler Optimization Heuristics with AlphaEvolve`. The abstract
    says Magellan synthesizes executable C++ decision logic for compiler
    passes, couples an LLM coding agent with evolutionary search and
    autotuning, evaluates candidates on user-provided macro-benchmarks, and
    reports LLVM function-inlining, register-allocation, and preliminary XLA
    results. The design section specifies policy proposal, local evaluation,
    hyperparameter tuning, and feedback incorporation around compiler rebuilds
    and end-to-end macro-benchmark rewards.
  - Current evidence: ROADMAP now names `papers/magellan_boundary.json` as the
    source-specific boundary for executable C++ decision logic,
    compiler-pass integration, EVOLVE-BLOCK compiler spans, compiler
    rebuild/macro-benchmark evaluation, autotuning, LLVM/register-allocation/
    XLA rows, baselines, generalization, maintainability, and runtime-
    repository status. It still does not define a compiler-heuristic candidate
    schema, compiler pass runner, macro-benchmark dataset contract, LLVM
    inlining benchmark, register-allocation benchmark, XLA portability
    benchmark, autotuning loop report, expert-baseline comparison, or
    production-style metric report for binary size and end-to-end performance.
  - Required result: add roadmap gates for `2601.21096`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    executable C++ decision-logic candidate schema, compiler-pass integration
    records, EVOLVE-BLOCK compiler-source provenance, compiler-flag
    hyperparameter schema, LLVM function-inlining benchmark with partial/full
    heuristic modes, register-allocation priority-rule benchmark, XLA graph-
    extraction and auto-sharding benchmarks, macro-benchmark provenance,
    binary-size and performance metric definitions, autotuning loop records
    including tuner identity, batch/round counts, and invalid-sample metrics,
    expert/neural baseline identities, temporal/domain generalization reports,
    generated-code maintainability caveats, seed/budget records, compiler
    environment hashes, independent checker outputs, and a background-only or
    benchmark-fixture status rule so roadmap claims do not outpace local
    AlphaEvolve-style Magellan compiler-optimization support.

- [ ] Add AlphaEvolve ArchAgent computer-architecture gates before roadmap
      promotion.
  - Spec evidence: arXiv `2602.22425`, submitted February 25, 2026,
    introduces `ArchAgent: Agentic AI-driven Computer Architecture Discovery`.
    The abstract says ArchAgent is built on AlphaEvolve to design and
    implement cache replacement policies, not merely tune parameters, and
    reports IPC speedup results on public multi-core Google Workload Traces
    and single-core SPEC06, post-silicon hyperspecialization gains, faster
    policy development than prior human SoTA, and simulator-escape behavior.
    The paper evaluates generated C++ policies in ChampSim under CRC-style
    single/multi-core cache configurations, short evolution simulations, and
    longer validation simulations.
  - Current evidence: ROADMAP now names `papers/archagent_boundary.json` as
    the source-specific boundary for generated C++ cache policies, ChampSim
    `policy.h` integration, CRC hardware configurations, SPEC06/Google
    Workload Trace fixtures, IPC-over-LRU metrics, Policy31/Policy31-Tuned/
    Policy61/Policy62 artifacts, hardware-realizability and state-budget
    checks, post-silicon specialization, simulator-escape controls,
    distributed simulation reliability, and runtime-repository status. It
    still does not define a cache replacement policy candidate schema,
    ChampSim simulator runner, CRC-style hardware configuration, Google
    Workload Trace or SPEC06 workload suite, IPC speedup metric,
    short-run/long-run validation split, SoTA policy baseline ledger,
    hardware-realizability/state-budget verifier, post-silicon specialization
    gate, or simulator-escape control policy.
  - Required result: implement roadmap gates for `2602.22425`: cache
    replacement policy candidate schema, ChampSim `policy.h` integration
    records, CRC cache/core/prefetch/DRAM configuration records, workload
    trace provenance, single-core and multi-core benchmark splits,
    evolution-versus-validation instruction-count protocols, IPC speedup
    metric definitions, prior-SoTA baseline identities, Policy31/61/62
    generated-policy artifacts and mechanism labels, state-budget and
    hardware-realizability checks, ablation records, post-silicon
    specialization parameter records, simulator-escape and write-bypass
    containment policy, distributed-simulation failure/retry records,
    seed/budget records, independent checker outputs, and benchmark-fixture
    status rules before roadmap claims promote ArchAgent support.

- [ ] Implement AlphaEvolve Fault2Flow workflow-automation gates beyond
      source-boundary roadmap promotion.
  - Spec evidence: arXiv `2511.12916`, submitted November 17, 2025,
    introduces `Fault2Flow: An AlphaEvolve-Optimized Human-in-the-Loop
    Multi-Agent System for Fault-to-Workflow Automation`. The abstract says
    Fault2Flow extracts regulatory logic into PASTA-formatted fault trees,
    integrates expert verification, optimizes reasoning logic with an
    AlphaEvolve module, synthesizes n8n-executable workflows, and validates on
    transformer fault-diagnosis datasets with `100%` topological consistency
    and high semantic fidelity. The body specifies a frontend/backend
    architecture with Vue3/Element Plus/pdfjs/xlsx/ECharts, MinerU PDF
    extraction, MySQL/Milvus storage, LLM agents for PlantUML mind maps and
    PASTA fault trees, OpenEvolve-linked AlphaEvolve multi-island optimization,
    n8n workflow construction/activation, synthesized workflow verification
    tests, and a `DL/T 722-2014` transformer DGA case study over 16
    expert-designed cases.
  - Current evidence: ROADMAP and `papers/fault2flow_boundary.json` now keep
    `2511.12916` source-scoped and background-only until local artifacts exist.
    ROADMAP still does not define a regulatory-text ingestion gate, PASTA
    fault-tree schema, expert-verification workflow, reasoning-
    logic optimization record, n8n workflow emitter, transformer fault-
    diagnosis dataset contract, topological-consistency metric, semantic-
    fidelity metric, or operational workflow artifact policy. It also lacks
    promotion gates for PlantUML intermediates, PASTA self-checks, n8n API
    activation evidence, synthesized test-case verification loops, GPT-5 judge
    usage, Table 1 model/baseline comparisons, average-token records, and
    placeholder ACM metadata caveats.
  - Required result: add roadmap gates for `2511.12916`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    regulatory-source provenance, PASTA fault-tree candidate schema,
    human-in-the-loop expert-review state records, reasoning-logic
    optimization candidate records, n8n workflow artifact schema, transformer
    fault-diagnosis dataset provenance, topological-consistency and semantic-
    fidelity metric definitions, seed/budget records, independent checker
    outputs, and a background-only or benchmark-fixture status rule so
    roadmap claims do not outpace local AlphaEvolve-style Fault2Flow
    automation support. Roadmap promotion should additionally require the
    three-stage document-understanding/knowledge-structuring/workflow-
    synthesis architecture, MinerU/MySQL/Milvus provenance, PlantUML and PASTA
    artifact hashes, OpenEvolve/AlphaEvolve optimization traces, n8n activation
    logs, synthesized verification samples and failure-refinement loops,
    DL/T 722-2014 dataset rows, Table 1 `16/0` Fault2Flow success and baseline
    failure rows, GPT-5 evaluator caveats, human-annotation/data-ethics
    records, and explicit documentation that Fault2Flow is not a supported
    LibreEvolve workflow until those local artifacts exist.

- [ ] Implement TTT-Discover gates beyond source-boundary roadmap promotion.
  - Spec evidence: arXiv `2601.16175`, submitted January 22, 2026 and last
    revised February 5, 2026, introduces `Learning to Discover at Test Time`.
    The abstract contrasts AlphaEvolve's frozen-LLM prompting search with
    reinforcement learning at test time, where the model continues training
    on experience specific to the test problem. It reports continuous-reward
    discovery results across math, GPU kernels, algorithm design, and biology,
    including Erdos minimum overlap, autocorrelation, GPUMode, AtCoder, and
    single-cell denoising tasks, using open model `OpenAI gpt-oss-120b`,
    public code, Tinker runs, expert or organizer review, and low per-problem
    costs. The body specifies a mutable-policy loop with Algorithm 1,
    adaptive entropic objective, PUCT reuse, `50` training steps, `512`
    rollouts per step, LoRA rank `32`, Tinker `32768`-token context window,
    fixed Table 9 hyperparameters, and result tables for math, GPUMode
    kernels, AtCoder, denoising, ablations, and MLA Triton-filtered variants.
  - Current evidence: ROADMAP now keeps `2601.16175` behind the committed
    `papers/ttt_discover_boundary.json` source-specific absence boundary. It
    tracks AlphaEvolve frozen-search gaps, provider routing, feedback graders,
    budget accounting, and broad background paper rows, but it still does not
    define a mutable model-policy state gate, test-time RL loop,
    Tinker/API training-run provenance, open-model checkpoint record,
    continuous-reward cross-domain benchmark suite, expert/organizer review
    artifact rule, or cost-per-problem accounting boundary. It also lacks
    promotion gates for public code/result URLs, LoRA/checkpoint lineage,
    adaptive-beta and PUCT traceability, OpenEvolve context-window truncation
    caveats, Modal/GPUMode/AtCoder/OpenProblems harness provenance, official
    submission IDs, Table 2-10 result rows, and the paper's sampling-budget
    inconsistency.
  - Required result: implement roadmap promotion gates beyond the source-boundary
    sidecar for `2601.16175`: mutable policy/training-state schema, RL objective
    and rollout-selection metadata, training API and checkpoint provenance, open-model identity,
    continuous-reward task definitions, Erdos/autocorrelation/GPUMode/AtCoder/
    single-cell benchmark records, prior-art and AlphaEvolve/OpenEvolve
    baseline identities, expert/organizer review artifacts, seed/run records,
    cost and budget accounting, independent checker outputs, and a
    background-only or benchmark-fixture status rule so roadmap claims do not
    outpace local TTT-Discover-style test-time-training support. Roadmap
    promotion should additionally require Algorithm 1 event logs, per-step
    rollout batches, mutable checkpoint and LoRA artifact policies, adaptive-
    beta KL and PUCT archive records, benchmark resource-limit contracts,
    public result-link verification, table-level result reproduction, official
    leaderboard/submission artifacts, expert-review attestations, and explicit
    documentation that TTT-Discover is not supported by LibreEvolve until
    weight-updating test-time-training artifacts exist locally.

- [ ] Implement AlphaEvolve Bruhat-interval hypercube gates beyond
      source-boundary roadmap promotion.
  - Spec evidence: arXiv `2601.01235`, submitted January 3, 2026, introduces
    `Bruhat intervals that are large hypercubes`. The abstract says
    AlphaEvolve-suggested permutations led to a pattern that worked for tested
    `n` and was then proved for general `n`; for powers of `2`, it exhibits
    `S_n` Bruhat intervals that are hypercubes of dimension `O(n log n)`,
    characterizes vertices as dyadically well-distributed permutations, and
    connects maximal Bruhat-hypercube dimension to Kazhdan-Lusztig
    `R`-polynomial coefficients, frozen variables in open Richardson cluster
    algebras, and embeddings of Bruhat graphs. The body proves this through
    dyadic basic intervals, bit-reversal endpoints `x_m` and `y_m`, Ehresmann
    Bruhat-order matrices, complementary blocks and flips, a poset isomorphism
    `phi: D_m -> S_2^{C_m}`, and Theorem 2.21's `D_m = [x_m, y_m]` rank
    `m * 2^(m-1)` hypercube.
  - Current evidence: ROADMAP now keeps `2601.01235` behind the committed
    `papers/bruhat_intervals_boundary.json` source-specific absence boundary.
    It tracks broad constructive-math and Appendix B fixture gaps plus
    background paper-index rows, but it still does not define permutation
    candidate schemas, Bruhat order/interval verifiers, poset-
    hypercube isomorphism checks, dyadic well-distribution predicates, power-
    of-two `S_n` benchmark rows, Kazhdan-Lusztig coefficient linkage, cluster-
    algebra consequence records, or finite-pattern versus proof-status gates.
    It also lacks gates for the Section 4 search protocol: FunSearch
    deterministic program-search baseline, AlphaEvolve generalizer-mode
    scoring across `n = 10..50`, Gemini 2.5 Flash/Pro model-call provenance,
    evaluated-program counts, public repository artifact status, and
    recurrence/proof checks for `alpha(2n)=2 alpha(n)+n`.
  - Required result: implement roadmap promotion gates beyond the
    source-boundary sidecar for `2601.01235`: permutation candidate schema,
    Bruhat interval witness artifacts, poset-
    hypercube verifier, dyadic well-distribution checker, power-of-two `S_n`
    benchmark records, dimension and asymptotic-bound calculations,
    Kazhdan-Lusztig `R`-polynomial coefficient metadata, cluster-algebra and
    Bruhat-graph consequence fields, finite-test/general-proof status,
    seed/budget records, independent checker outputs, and a background-only
    or benchmark-fixture status rule so roadmap claims do not outpace local
    AlphaEvolve-style Bruhat-interval hypercube support. Roadmap promotion
    should additionally require `x_m`/`y_m` generator fixtures, Ehresmann and
    fundamental/complementary-block verifier outputs, `d`-invariant and
    `R`-polynomial calculators, FunSearch/AlphaEvolve prompt/evaluator/run
    artifacts, public repo hash/status, low-discrepancy and `t`-adic
    extension metadata, proof-status records, and documentation separating
    finite AlphaEvolve-discovered examples from human-proved all-`m`
    constructions.

- [ ] Implement global NLP solver comparator gates beyond source-boundary
      roadmap promotion.
  - Spec evidence: arXiv `2601.05943`, submitted January 9, 2026, introduces
    `Global Optimization for Combinatorial Geometry Problems`. The abstract
    frames AlphaEvolve's geometric/combinatorial discoveries as a benchmark
    for modern off-the-shelf global optimization solvers, reformulates a
    subset of those problems as nonlinear optimization problems, evaluates
    FICO Xpress and SCIP without solver modifications, and reports reproduced
    and sometimes improved best-known solutions including recent LLM-driven
    results. The body covers min-max distance ratio, square/rectangle circle
    packing, and regular-hexagon packing with explicit nonlinear
    formulations, Mosel implementations, squared-distance QCPs, and Farkas-
    multiplier separation for hexagon non-overlap.
  - Current evidence: ROADMAP and `papers/global_nlp_optimization_boundary.json`
    now keep `2601.05943` source-scoped as potential-future-benchmark status
    until local solver artifacts exist. ROADMAP still does not define a direct NLP
    formulation gate, Xpress/SCIP runner abstraction, solver license/status
    handling, selected benchmark subset, solver parameter/time-limit policy,
    incumbent/bound/certificate artifact records, numerical tolerance policy,
    or side-by-side result table versus AlphaEvolve and literature baselines.
    It also lacks gates for Mosel/exported model artifacts, AlphaEvolve
    validation-code outputs, Table 1-3 value rows, rounding policy, source-link
    provenance for prior packing data and OpenEvolve/SciPy/SCIP, commercial
    Xpress availability handling, solver-attribution caveats, and dual-bound
    reporting expectations.
  - Required result: add roadmap gates for `2601.05943`: paper/source
    manifest entry, PDF/cache hash, source-license and code-artifact status,
    selected AlphaEvolve benchmark subset, NLP formulation schema,
    variable/domain/constraint/objective records, FICO Xpress and SCIP solver
    identity/version/license records, solver parameter and resource-limit
    metadata, incumbent/bound/certificate artifacts, numerical tolerance
    policy, prior-literature and AlphaEvolve baseline values,
    reproduced/improved/fell-behind outcome rows, seed/run records,
    independent checker outputs, and a background-only or benchmark-fixture
    status rule so roadmap claims do not outpace local global-NLP solver
    comparison support. Roadmap promotion should additionally require per-
    family distance-ratio/circle/hexagon formulation fixtures, solver logs,
    primal incumbent and optional dual-bound records, AlphaEvolve/literature
    baseline citations, AlphaEvolve repository validation artifacts, Table 1-3
    reproduction reports, license/reproducibility status, and documentation
    that direct NLP solver baselines complement but do not implement
    AlphaEvolve's LLM evolutionary-search mechanism.

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
