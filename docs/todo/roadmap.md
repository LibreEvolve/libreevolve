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

- [x] Add CLI/config precedence semantics to runtime hardening.
  - Evidence: `_build_config()` currently overwrites `config.yaml`
    `problem_name` with the problem directory name and applies
    `--reasoning-effort` only to CLI-created backend specs.
  - Current roadmap gap: the roadmap mentioned config validation but did not
    call out field-by-field precedence and effective-config override tests.
  - Required result: track deterministic precedence, explicit ignored-override
    behavior, and tests for config-file plus CLI combinations.

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

- [x] Add run-directory collision policy to resumability work.
  - Evidence: `ProgramDatabase.log()` appends `history.jsonl` and
    `PromptDatabase` appends `prompt_history.jsonl`, while `manifest.json` is
    overwritten for the same run directory.
  - Current roadmap gap: resumability work covered saved state, but not the
    immediate truthfulness issue that reusing a run name can mix independent
    runs under one latest manifest.
  - Required result: track explicit overwrite/fail/new-run/resume semantics,
    run ids, and artifact consistency across history, prompt history, manifest,
    and `best.py`.

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

- [x] Add richer evaluator-output prompt rendering to prompt/context work.
  - Evidence: AlphaEvolve prompts can include execution results and scores, but
    the current prompt sampler only renders compact recent stage summaries.
  - Current roadmap gap: the roadmap said evaluator feedback without calling
    out stdout/stderr, artifacts, LLM grader summaries, or sample-level
    diagnostics.
  - Required result: keep bounded execution-output and feedback rendering on
    the roadmap as a prompt fidelity item.

- [x] Add proposal idea/rationale capture to prompt/context work.
  - Evidence: AlphaEvolve Figure 3 asks the LLM to suggest a new idea and
    describe changes with SEARCH/REPLACE blocks.
  - Current roadmap gap: prompt work covered templates/context but not a
    structured proposal artifact separate from raw patch text.
  - Required result: track response formats that can preserve proposal
    rationale for critique, logging, and future resurfacing.

- [x] Add flexible candidate abstraction modes to candidate fidelity.
  - Evidence: AlphaEvolve Section 2.1 allows user-chosen solution
    abstractions, not only code file sets.
  - Current roadmap gap: candidate workspace work covers files, blocks, and
    artifacts, but not problem-defined render/mutate/materialize abstractions
    such as raw solutions, constructor functions, or paired solution/search
    procedures.
  - Required result: either add abstraction hooks or explicitly keep
    code-file-set evolution as a documented divergence.

- [x] Add full-code/full-block mutation mode.
  - Evidence: AlphaEvolve Section 2.3 says the system can be configured to ask
    for a complete code block rather than diffs when appropriate.
  - Current roadmap gap: no item tracks non-diff mutation modes.

- [x] Add model scheduling by throughput, cost, and depth.
  - Evidence: AlphaEvolve uses a fast model for idea breadth and a stronger
    model for deeper suggestions.
  - Current roadmap gap: the roadmap only covers backend config validation
    (`ROADMAP.md:34-41`) and does not address scheduler strategy.

- [x] Add custom LLM backend extensibility to backend work.
  - Evidence: AlphaEvolve's setup includes a choice of existing or custom LLMs,
    while LibreEvolve's current backend registry is hard-coded to three
    providers in `build_llm()`.
  - Current roadmap gap: backend work covered validation and scheduling but not
    config/plugin registration for custom providers.
  - Required result: track a backend registry or plugin interface with
    validation and manifest provenance.

- [x] Add role-specific LLM call accounting to backend scheduling work.
  - Evidence: AlphaEvolve's ensemble scheduling should reflect candidate
    generation quality/throughput, while LibreEvolve currently counts
    critique/feedback/meta-prompt calls as ordinary pulls.
  - Current roadmap gap: backend scheduling work mentioned UCB reward
    normalization and breadth/depth tests but not separation of call roles.
  - Required result: track and test mutation, critique, feedback, and
    meta-prompt accounting separately.

- [x] Add reviewer-pool critique fidelity to backend/critique work.
  - Evidence: AlphaEvolve describes using LLMs to generate, critique, and
    evolve a pool of algorithms, while LibreEvolve has only a single optional
    synchronous self-revision pass.
  - Current roadmap gap: critique work did not explicitly call out reviewer
    roles, agreement/disagreement logging, or policies beyond one revision.
  - Required result: extend critique/revision toward configurable reviewer
    pools with provenance and accounting.

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

- [x] Add plugin registry/config/provenance work.
  - Evidence: built-in plugins are currently hard-coded CLI aliases with no
    per-plugin config schema, constructor options, or manifest provenance.
  - Current roadmap gap: plugin extensibility covered moving registration out of
    the CLI, but not config validation or run-provenance records for plugin
    parameters and emitted artifacts.
  - Required result: track plugin registry, configuration schema, constructor
    parameters, paper-inspiration scope, and artifact provenance.

- [x] Add evaluator path validation/provenance to runtime hardening.
  - Evidence: `eval_stages[].validate_path` can resolve to arbitrary absolute
    paths and is not prevalidated or hashed before execution.
  - Current roadmap gap: evaluator hardening covered metric contracts,
    cascades, and artifacts but not validator-code path confinement and
    provenance.
  - Required result: validate evaluator paths, define outside-problem policy,
    and include evaluator path/hash provenance in manifests.

- [x] Add run-wide compute-budget accounting to runtime work.
  - Evidence: AlphaEvolve Section 2.6 describes maximizing evaluated ideas
    under a total computation budget, and paper ablations compare progress by
    fraction of consumed budget.
  - Current roadmap gap: the roadmap mentioned per-stage budgets and
    deterministic accounting, but did not require whole-run wall-clock,
    LLM-call, token, cost, evaluator-second, sample/retry counters, stop
    reasons, or equal-budget ablation reporting.
  - Required result: make budget schemas, counters, stop reasons, manifest
    summaries, and budget-fraction benchmark reporting explicit runtime work.

- [x] Refresh current-state example list.
  - Evidence: `libreevolve/problems/examples/` includes `workspace_math`, but
    `ROADMAP.md` listed only `hello_world`, `sorting`, `circle_packing`, and
    `matrix_multiplication`.
  - Required result: include all checked-in examples when the roadmap describes
    current repository state.

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
