# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

- [x] Refresh the roadmap date and status.
  - Evidence: `ROADMAP.md:3` says it reflects the codebase as of
    `2026-03-26`, while the current checkout has papers downloaded and newer
    docs/tests than that snapshot.
  - Required result: update the roadmap date and state which current code/docs
    were audited.

- [x] Reframe the roadmap from "mostly tightening contracts" to "closing major
  AlphaEvolve specification gaps."
  - Evidence: `ROADMAP.md:20-21` says the next phase is mostly about contracts,
    experiment control, and reproducibility.
  - Contradiction: the AlphaEvolve paper requires evolve-block APIs,
    multi-component/full-file evolution, multi-score optimization, rich prompt
    context, configurable evaluation cascades, asynchronous throughput, and
    meta-prompt evolution, none of which are present as first-class features.
  - Required result: add a top-level AlphaEvolve alignment milestone before or
    alongside the existing reliability milestones.

## Missing Roadmap Items

- [x] Add configuration/schema validation to runtime hardening.
  - Evidence: AlphaEvolve-style task setup depends on configuration for
    prompts, evaluators, LLMs, and mutation behavior.
  - Current roadmap gap: the roadmap covered manifests and reproducibility but
    not early validation of unknown/malformed config keys or backend specs.
  - Required result: make config validation a first-class prerequisite for
    reproducible AlphaEvolve-style runs.

- [x] Add evaluator metric-contract validation to the backlog.
  - Evidence: AlphaEvolve Section 2.1 treats `evaluate` as returning scalar
    metrics, while LibreEvolve currently validates only enough of the result to
    compute primary fitness.
  - Current roadmap gap: evaluation hardening covered cascades and artifacts
    but not schema enforcement against `metrics.yaml`.
  - Required result: keep metric schema validation on the roadmap because
    multi-objective search depends on trustworthy metric vectors.

- [x] Add full-workspace export and resume coverage to candidate fidelity.
  - Evidence: AlphaEvolve evolves full files/codebases, while a primary-file
    `best.py` artifact is insufficient for a multi-file candidate.
  - Current roadmap gap: candidate workspace work now explicitly includes
    preserving full workspace artifacts and migration/resume coverage.
  - Required result: keep export/resume as part of workspace fidelity, not only
    runtime hardening.

- [x] Add evolve-block and skeleton/codebase support to near-term architecture
  alignment.
  - Evidence: AlphaEvolve Section 2.1 defines an input API with marked
    evolvable blocks inside a larger code skeleton.
  - Current roadmap gap: near-term item 1 only mentions `primary_bounds`,
    README audit, and tests (`ROADMAP.md:25-32`).

- [x] Add multi-objective evaluation and metric-vector storage.
  - Evidence: AlphaEvolve Section 2.4 explicitly supports optimizing multiple
    user-provided scores.
  - Current roadmap gap: evaluator metadata is only a mid-term item
    (`ROADMAP.md:68-74`) and does not call out multi-objective archive,
    sampling, prompt, or logging behavior.

- [x] Add configurable evaluation cascades.
  - Evidence: AlphaEvolve Section 2.4 describes user-specified ensembles of
    test cases with increasing difficulty.
  - Current roadmap gap: `ROADMAP.md:68-74` mentions diagnostics and metadata,
    but not staged evaluator definitions, thresholds, budgets, or parallel
    stages.

- [x] Add async/distributed controller and worker architecture.
  - Evidence: AlphaEvolve Section 2.6 describes an asynchronous pipeline with a
    controller, LLM samplers, and evaluation nodes optimized for throughput.
  - Current roadmap gap: the roadmap mentions resumable runs and benchmark
    scripts (`ROADMAP.md:76-81`) but not async sampling/evaluation or worker
    queues.

- [x] Add prompt-sampler work: templates, stochastic formatting, explicit
  context, rendered evaluator feedback, and meta-prompt evolution.
  - Evidence: AlphaEvolve Section 2.2 lists these as prompt sampling
    capabilities.
  - Current roadmap gap: prompt evolution is absent; documentation work
    (`ROADMAP.md:50-55`) and search improvements (`ROADMAP.md:83-88`) are too
    broad to cover it.

- [x] Add prompt-template validation and context summarization hardening.
  - Evidence: AlphaEvolve prompt customization includes stochastic formatting,
    explicit context, relevant literature, and co-evolved prompts.
  - Current roadmap gap: after the implementation pass, the roadmap now tracks
    stricter placeholder validation, deterministic PDF/text context ingestion,
    and richer prompt-fitness/ablation reporting.
  - Required result: ensure prompt/context work covers malformed evolved
    templates and large context sources, not only happy-path template selection.

- [x] Add full-code/full-block mutation mode.
  - Evidence: AlphaEvolve Section 2.3 says the system can be configured to ask
    for a complete code block rather than diffs when appropriate.
  - Current roadmap gap: no item tracks non-diff mutation modes.

- [x] Add model scheduling by throughput, cost, and depth.
  - Evidence: AlphaEvolve uses a fast model for idea breadth and a stronger
    model for deeper suggestions.
  - Current roadmap gap: the roadmap only covers backend config validation
    (`ROADMAP.md:34-41`) and does not address scheduler strategy.

- [x] Add role-specific LLM call accounting to backend scheduling work.
  - Evidence: AlphaEvolve's ensemble scheduling should reflect candidate
    generation quality/throughput, while LibreEvolve currently counts
    critique/feedback/meta-prompt calls as ordinary pulls.
  - Current roadmap gap: backend scheduling work mentioned UCB reward
    normalization and breadth/depth tests but not separation of call roles.
  - Required result: track and test mutation, critique, feedback, and
    meta-prompt accounting separately.

- [x] Add rich evolutionary database work.
  - Evidence: AlphaEvolve's program database stores solutions with scores and
    outputs, then resurfaces ideas to balance exploration and exploitation.
  - Current roadmap gap: `ROADMAP.md:108-113` treats a database backend as a
    non-goal. That may remain true for services, but a stronger local
    evolutionary database is required for AlphaEvolve fidelity.

- [x] Add reproducibility hashes to run metadata work.
  - Evidence: AlphaEvolve-scale runs need exact problem, evaluator, prompt, and
    code-state provenance to support long-running comparisons.
  - Current roadmap gap: `manifest.json` existed, but the roadmap did not make
    code/problem/plugin/artifact hashes explicit.
  - Required result: track hashes/version metadata separately from basic config
    logging.

## Existing Items That Need Tightening

- [x] Expand "better diversity measures" into measurable database/sampling
  requirements.
  - Evidence: `ROADMAP.md:85-88` is too vague to guide AlphaEvolve-compatible
    parent/inspiration sampling.
  - Required result: specify candidate features, metric-vector diversity,
    lineage diversity, recency, novelty, and score-conditioned inspiration
    sampling.

- [x] Expand "training-data export" into a concrete ThetaEvolve/GRPO boundary.
  - Evidence: `ROADMAP.md:98-99` mentions downstream RL fine-tuning around
    `ttt_rl`, while the current plugin only writes JSONL and does not train.
  - Required result: define whether LibreEvolve will implement training,
    export-only datasets, or integration hooks, and document the divergence.

- [x] Move representative benchmarks earlier.
  - Evidence: `ROADMAP.md:92-95` keeps representative algorithmic benchmarks in
    longer term.
  - AlphaEvolve alignment need: benchmarks like matrix multiplication,
    circle/kissing packing, constructive math, or scheduling heuristics are
    needed to prove fidelity beyond toy examples.
