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

- [x] Add seeded replay determinism to reproducibility work.
  - Evidence: `Config.seed` seeds Python `random` and prompt variant sampling,
    but `Program.id` and `PromptProgram.id` use UUID4 values, so persisted
    candidate/prompt lineage differs across repeated deterministic local runs.
  - Current roadmap gap: reproducibility work covered manifests, hashes,
    budgets, and resume state, but not stable seeded identifiers/RNG replay.
  - Required result: track deterministic run/candidate/prompt id policy, RNG
    state capture, provider nondeterminism boundaries, and tests proving stable
    local replay metadata.

- [x] Add evolve-block and skeleton/codebase support to near-term architecture
  alignment.
  - Evidence: AlphaEvolve Section 2.1 defines an input API with marked
    evolvable blocks inside a larger code skeleton.
  - Current roadmap gap: near-term item 1 only mentions `primary_bounds`,
    README audit, and tests (`ROADMAP.md:25-32`).

- [x] Add malformed evolve-block marker validation to candidate fidelity.
  - Evidence: `extract_evolve_blocks()` silently stops when it cannot find a
    matching end marker and mutation can fall back to whole-file behavior when
    no complete blocks are parsed.
  - Current roadmap gap: candidate fidelity listed marker support but not
    marker-structure validation, even though skeleton preservation depends on
    rejecting malformed task specifications.
  - Required result: keep marker validation on the roadmap alongside
    workspace/codebase fidelity.

- [x] Add file-section path grammar hardening to candidate fidelity.
  - Evidence: `_FILE_SECTION_PATTERN` captures only
    `[A-Za-z0-9_./\\:-]+`, while real repository filenames and
    `normalize_candidate_path()` can require broader safe relative paths.
  - Current roadmap gap: workspace fidelity covered file sets and artifacts but
    not whether LLM file-section envelopes can address ordinary codebase
    filenames.
  - Required result: track unified path parsing, unsafe-path diagnostics, and
    tests for common repository filename shapes.

- [x] Add workspace file-topology mutation support to candidate fidelity.
  - Evidence: `apply_workspace_mutation()` can edit existing files and create
    unknown files in `full` mode, but there is no mutation syntax or state
    transition for deleting, renaming, moving, or changing the primary file in
    a candidate workspace.
  - Current roadmap gap: workspace fidelity covered file sets, path grammar,
    and exports, but not normal codebase topology changes.
  - Required result: track delete/rename/move/primary-file operations with path
    validation, history persistence, materialization tests, and backward
    compatibility for current file-section edits.

- [x] Add workspace execution import/cwd fidelity to candidate fidelity.
  - Evidence: `CascadeEvaluator._run_subprocess()` materializes the candidate
    workspace and passes its path to the validator, but does not run the
    validator with the candidate root as `cwd` or place that root on
    `sys.path`; `workspace_math/validate.py` manually inserts the workspace
    path before importing candidate modules.
  - Current roadmap gap: workspace fidelity covered file sets, fixtures, and
    exports, but not whether validators can execute evolved codebases with
    normal local imports and relative paths.
  - Required result: define/test evaluator workspace execution semantics for
    `cwd`, import path, environment, package/module entrypoints, and relative
    artifacts.

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

- [x] Add context-source manifest/provenance work.
  - Evidence: `_load_context_files()` reads only immediate files in `context/`
    into a filename-to-text dictionary and does not preserve hashes, recursive
    paths, PDF page spans, extraction metadata, or include/exclude selection.
  - Current roadmap gap: prompt/context work covered summarization and ranking
    but not source-selection provenance needed to reproduce AlphaEvolve-style
    task context.
  - Required result: track recursive source selection, context manifests,
    source hashes, extraction diagnostics, page/span citations, and prompt/run
    provenance.

- [x] Add prompt budget/context-window accounting to prompt work.
  - Evidence: `PromptSampler.build()` concatenates rendered sections without a
    global budget, and only problem context files have a first-6000-character
    local truncation.
  - Current roadmap gap: prompt/context work covered richer sections and
    summarization but not deterministic packing of the final prompt into a
    backend context window.
  - Required result: track prompt budgets, section priorities, token/character
    accounting, prompt-size diagnostics, and oversized-section tests.

- [x] Add richer evaluator-output prompt rendering to prompt/context work.
  - Evidence: AlphaEvolve prompts can include execution results and scores, but
    the current prompt sampler only renders compact recent stage summaries.
  - Current roadmap gap: the roadmap said evaluator feedback without calling
    out stdout/stderr, artifacts, LLM grader summaries, or sample-level
    diagnostics.
  - Required result: keep bounded execution-output and feedback rendering on
    the roadmap as a prompt fidelity item.

- [x] Add full-workspace rendering for LLM feedback graders.
  - Evidence: `_build_feedback_prompt()` passes only the primary-file content
    (`workspace.code`) to feedback graders, so multi-file candidates can be
    graded without helper files or other evolved components.
  - Current roadmap gap: feedback calibration and richer prompt rendering were
    tracked, but not the distinct issue that feedback-grader prompts are
    primary-file-only despite workspace candidates.
  - Required result: render bounded candidate file sets and diagnostics to
    graders with budget/redaction controls and tests for non-primary files.

- [x] Add LLM feedback failure isolation to evaluation hardening.
  - Evidence: `apply_llm_feedback()` lets provider exceptions, malformed
    `score` values, invalid `weight`/`min_score` config, and loose
    `discard` truthiness propagate or misclassify candidates outside the
    structured evaluation-stage contract.
  - Current roadmap gap: feedback calibration and config validation were
    tracked, but the roadmap did not call out failure isolation for optional
    feedback graders as an evaluation hardening item.
  - Required result: validate feedback grader schemas before runs, quarantine
    grader call/parse failures as structured metadata or stage outcomes, and
    test backend errors, malformed responses, invalid config, and discard
    parsing.

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

- [x] Add normalized LLM call telemetry to backend scheduling work.
  - Evidence: backend adapters return plain text and discard provider usage,
    latency, retry counts, request ids, finish reasons, API mode, and raw
    provider diagnostics.
  - Current roadmap gap: backend work covered scheduling and role accounting
    but not the per-call telemetry needed to prove cost/latency/budget claims.
  - Required result: track call-result objects, provider usage, prompt/output
    size, retries, latency, API mode, request/response ids, failure metadata,
    and scheduler/budget updates from that telemetry.

- [x] Add LLM provider failure policy to backend/runtime work.
  - Evidence: `evolve()` calls `llm.generate()` for mutation, critique,
    feedback, and meta-prompt mutation without retries or exception handling,
    while `LLMEnsemble.generate()` only increments backend counts after a
    successful return.
  - Current roadmap gap: backend scheduling and telemetry work covered
    throughput, usage, and failure metadata, but did not require deterministic
    retry/fallback/quarantine behavior for failed provider calls.
  - Required result: track per-role LLM retry budgets, fallback routing, failed
    attempt accounting, structured error logs, and tests for mutation,
    critique, feedback, and meta-prompt failures.

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

- [x] Add archive-state and migration-event persistence to database work.
  - Evidence: `ProgramDatabase.log()` writes candidate JSONL records, but
    `MAPElites` cell grids, elite lists, diversity/complexity normalization
    state, island assignment, and migration events remain in memory only.
  - Current roadmap gap: resumability and database work covered queryability
    and saved state broadly, but not the concrete MAP-Elites/island state
    needed to inspect or resume the actual archive used by sampling.
  - Required result: persist archive cell/event snapshots with island ids,
    descriptors, replacements, elite contents, migration events, and
    normalization state.

- [x] Add strict JSONL serialization hardening to database work.
  - Evidence: `ProgramDatabase.log()` and `PromptDatabase._write()` use
    `json.dumps(...)` defaults, which permit `NaN`/`Infinity` tokens if
    non-finite values reach records.
  - Current roadmap gap: database work covered queryability and sampling, but
    not the validity of persisted JSONL for strict downstream analysis.
  - Required result: make finite JSON serialization and invalid-record
    quarantine part of runtime/database hardening.

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

- [x] Add plugin score-composition provenance to plugin extensibility work.
  - Evidence: `evolve()` lets each plugin return a modified score and stores
    only the final `program.fitness`, while `evaluation.fitness` remains the
    evaluator/feedback result.
  - Current roadmap gap: plugin work mentioned registration, configuration, and
    artifacts but not the provenance of score-changing hook chains.
  - Required result: track per-plugin before/after scores, reasons, validation,
    and the relationship between raw evaluator fitness and composed archive
    fitness.

- [x] Add evaluator path validation/provenance to runtime hardening.
  - Evidence: `eval_stages[].validate_path` can resolve to arbitrary absolute
    paths and is not prevalidated or hashed before execution.
  - Current roadmap gap: evaluator hardening covered metric contracts,
    cascades, and artifacts but not validator-code path confinement and
    provenance.
  - Required result: validate evaluator paths, define outside-problem policy,
    and include evaluator path/hash provenance in manifests.

- [x] Add validator environment/secret isolation to runtime hardening.
  - Evidence: `.env` is loaded into the parent process, and
    `CascadeEvaluator._run_subprocess()` calls `subprocess.run()` without an
    `env=` allowlist, so validators inherit provider keys and host environment
    variables by default.
  - Current roadmap gap: sandbox/resource-limit and evaluator-path work covered
    filesystem/process boundaries, but not inherited secrets, environment
    reproducibility, redaction, or network expectations.
  - Required result: specify a minimal validator environment, explicit opt-ins,
    secret redaction, network policy, and tests proving provider keys are not
    visible to validators by default.

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
