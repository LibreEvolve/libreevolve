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
  - Current status: `Config.validate()` and `_build_config()` now reject
    unknown problem config keys, invalid mutation/ensemble enums, malformed
    backend specs, invalid evaluator-stage numbers, and invalid top-level
    runtime/population ranges. LLM feedback grader schemas are also validated.
    Remaining runtime hardening is focused on plugin-specific config schemas
    API capability validation, and converting malformed YAML or non-mapping
    top-level `config.yaml` files into clear path-aware startup diagnostics
    instead of raw parser/update exceptions.

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

- [x] Add degenerate metric-bound validation to the backlog.
  - Evidence: `metrics.yaml` bounds drive primary fitness normalization and
    MAP-Elites performance coordinates, but `_validate_metric_schema()` accepts
    finite zero-width or inverted ranges.
  - Current roadmap gap: current-state bullets said strict scalar validation
    and metric direction/bounds normalization, but did not call out invalid
    bound ordering.
  - Required result: track rejection or explicit semantics for zero-width and
    inverted bounds before metric vectors feed archive or multi-objective
    policy.

- [x] Add full-workspace export and resume coverage to candidate fidelity.
  - Evidence: AlphaEvolve evolves full files/codebases, while a primary-file
    `best.py` artifact is insufficient for a multi-file candidate. The CLI now
    also writes `best_workspace/` with the complete best candidate file set.
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
  - Evidence: `Config.seed` seeds Python `random`, but `Program.id` and
    `PromptProgram.id` use UUID4 values, and initial prompt variants are
    selected as untried prompt programs sorted by UUID4 id rather than by
    config order or seeded RNG.
  - Current roadmap gap: reproducibility work covered manifests, hashes,
    budgets, and resume state, but not stable seeded identifiers, prompt
    variant order, or RNG replay.
  - Required result: track deterministic run/candidate/prompt id policy, RNG
    state capture, prompt variant selection policy, provider nondeterminism
    boundaries, and tests proving stable local replay metadata.

- [x] Add evolve-block and skeleton/codebase support to near-term architecture
  alignment.
  - Evidence: AlphaEvolve Section 2.1 defines an input API with marked
    evolvable blocks inside a larger code skeleton.
  - Current roadmap gap: near-term item 1 only mentions `primary_bounds`,
    README audit, and tests (`ROADMAP.md:25-32`).

- [x] Add malformed evolve-block marker validation to candidate fidelity.
  - Evidence: malformed evolve-block layouts can weaken skeleton preservation
    unless mutation rejects them before deciding whether a file is fully
    evolvable. `validate_evolve_blocks()` now fails closed during mutation for
    missing end markers, orphan end markers, nested blocks, invalid names, and
    duplicate block names.
  - Current roadmap gap: candidate fidelity listed marker support but not
    marker-structure validation, even though skeleton preservation depends on
    rejecting malformed task specifications.
  - Required result: keep marker validation on the roadmap alongside
    workspace/codebase fidelity.

- [x] Add file-section path grammar hardening to candidate fidelity.
  - Evidence: `<<<FILE ... >>>FILE` headers now capture the full header line
    and pass through `normalize_candidate_path()`, so common repository
    filename shapes such as nested paths, hyphens, spaces, Unicode filename
    characters, and Windows-style backslashes are accepted when safe.
  - Current roadmap gap: workspace fidelity covered file sets and artifacts but
    not whether LLM file-section envelopes can address ordinary codebase
    filenames.
  - Required result: track unified path parsing, unsafe-path diagnostics, and
    tests for common repository filename shapes.

- [x] Add candidate path-collision handling to candidate fidelity.
  - Evidence: path grammar hardening rejects unsafe paths, and
    `CandidateWorkspace` now rejects distinct raw inputs that normalize to the
    same candidate path. Materialization now preflights case-folded host paths
    before writing, so case-only variants fail closed on case-insensitive
    filesystems.
  - Current roadmap gap: workspace fidelity covered safe path grammar but not
    whether the candidate file set remains one-to-one after normalization and
    host filesystem materialization.
  - Required result: continue tracking Unicode normalization and
    mutation-envelope collision policy with tests for loader and mutation.

- [x] Add mutation-envelope diagnostics for partial parses.
  - Evidence: file and block mutation envelopes now validate unmatched,
    orphaned, nested, empty-name, invalid-name, and unsafe-path sections before
    partial edits are applied.
  - Current roadmap gap: path grammar hardening covered valid filename support,
    but not detection of unmatched `<<<FILE`/`<<<BLOCK` spans that represent
    intended edits.
  - Required result: parse envelopes as a full document, reject or log
    malformed sections, and test mixed valid plus malformed file/block
    responses.

- [x] Add duplicate block-section detection to mutation-envelope work.
  - Evidence: `_apply_full_replacement()` previously stored named block
    sections in a dict, so duplicate `<<<BLOCK a ... >>>BLOCK` sections
    silently overwrote earlier bodies. A local proof returned no error and
    applied only the later duplicate block body.
  - Current roadmap gap: envelope diagnostics covered malformed spans but not
    ambiguous duplicate target sections inside an otherwise well-formed
    multi-block full replacement.
  - Status: implemented. Duplicate block-section names now return
    `malformed_block_sections:duplicate_name` before replacement, with tests
    covering duplicate names in full-block replacements.

- [x] Add workspace file-topology mutation support to candidate fidelity.
  - Evidence: `apply_workspace_mutation()` can edit existing files and create
    unknown files in `full` mode; command file sections now support deleting,
    renaming, moving, and changing the primary file in a candidate workspace.
  - Current roadmap gap: workspace fidelity covered file sets, path grammar,
    and exports, but not normal codebase topology changes.
  - Status: implemented with path validation, history/export persistence through
    `Program.files` and `primary_file`, mutation tests, and backward
    compatibility for current file-section edits.

- [x] Add workspace execution import/cwd fidelity to candidate fidelity.
  - Evidence: `CascadeEvaluator._run_subprocess()` now materializes the
    candidate workspace, runs the validator with that root as `cwd`, adds the
    candidate root to `sys.path`, and passes it as `workspace_path`.
  - Current roadmap gap: workspace fidelity covered file sets, fixtures, and
    exports, but not whether validators can execute evolved codebases with
    normal local imports and relative paths.
  - Required result: define/test evaluator workspace execution semantics for
    `cwd`, import path, environment, package/module entrypoints, and relative
    artifacts.

- [x] Add problem-local evaluator import semantics to evaluation hardening.
  - Evidence: `_RUNNER` still loads `validate.py` by file path from a temporary
    runner, but now adds `validate_path.parent` to `sys.path`, so sibling
    validator helper modules are supported by default.
  - Current roadmap gap: workspace execution work covered candidate-root
    imports, but not problem-local evaluator-code imports and relative data.
  - Required result: define validator module/package loading, problem-dir
    `cwd` or `PYTHONPATH` policy, evaluator helper/data provenance, and tests
    for sibling imports and package validators.

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

- [x] Add evaluator artifact copy-out to evaluation hardening.
  - Evidence: `CascadeEvaluator._run_subprocess()` materializes the candidate
    in a `TemporaryDirectory`, runs the validator with that directory as `cwd`,
    and deletes the directory after returning metrics/stdout/stderr. Files
    written by validators are not copied into run artifacts.
  - Current roadmap gap: evaluation hardening mentioned artifacts broadly but
    did not identify the temporary-workspace data-loss mechanism or require
    stage/sample/attempt artifact provenance.
  - Required result: track artifact include/exclude configuration, size limits,
    hashes, redaction, stage/sample/attempt provenance, and tests proving
    validator-created files are retained after subprocess cleanup.

- [x] Add evaluator-stage numeric validation to config hardening.
  - Evidence: `Config.validate()` now checks evaluator-stage `samples`,
    `retries`, `timeout_sec`, `min_score`, `seeds`, unsupported fields, and
    explicit sample/seed count mismatches before `CascadeEvaluator` is built.
  - Status: implemented with config tests.

- [x] Add top-level evolution/population numeric validation to config
  hardening.
  - Evidence: `Config.validate()` now checks generation counts, inspiration
    counts, timeouts, exploration ratios, island counts, migration settings,
    MAP-Elites bins, elite archive sizes, and ensemble coefficients before
    `evolve()` starts.
  - Status: implemented with config range tests.

- [x] Add zero-ratio migration semantics to population config work.
  - Evidence: `Config.validate()` accepts `migration_ratio=0.0`, while
    `IslandModel.migrate()` rounds migrant count with `max(1, ...)`. A local
    proof showed `migration_ratio=0.0` still migrates one elite when migration
    is enabled.
  - Current roadmap gap: numeric validation covered bounds checking but not the
    behavioral meaning of the lower bound for migration.
  - Required result: define/test whether zero ratio disables migrant selection,
    is rejected, or remains documented as "at least one migrant per non-empty
    island whenever migration runs."

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
    stricter configured and mutated prompt-template placeholder validation,
    deterministic PDF/text context ingestion, and richer prompt-fitness/
    ablation reporting.
  - Required result: ensure prompt/context work covers malformed evolved
    templates, malformed configured variants, and large context sources, not
    only happy-path template selection.

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

- [x] Add live retrieval provenance to prompt/plugin context work.
  - Evidence: `DeepResearchPlugin` injects live arXiv search summaries into
    prompts but stores only the latest synthesis string in memory.
  - Current roadmap gap: context-source provenance covered problem-local files,
    while plugin-provided external context also needs reproducible query,
    result, citation, failure, and manifest records.
  - Required result: persist provider/query/result metadata for retrieval
    plugins, render citations in prompt context, and test successful, empty,
    malformed, and failed retrieval events.

- [x] Add plugin prompt-context attribution to prompt/plugin work.
  - Evidence: plugin `build_extra_context()` outputs are concatenated into one
    prompt string, and `ModularPlugin` always returns static
    generate/improve/perturb guidance without recording a selected strategy.
  - Current roadmap gap: plugin provenance work covered config/artifacts and
    score composition, but not the prompt-context components and strategy
    choices that influence candidate generation before evaluation.
  - Required result: log per-plugin prompt-context records with rendered hashes
    and operation/strategy metadata, or explicitly keep plugins such as
    `modular` as static prompt-only guidance with tests and docs.

- [x] Add prompt budget/context-window accounting to prompt work.
  - Evidence: `PromptSampler.build()` concatenates rendered sections without a
    global budget, and only problem context files have a first-6000-character
    local truncation.
  - Current roadmap gap: prompt/context work covered richer sections and
    summarization but not deterministic packing of the final prompt into a
    backend context window.
  - Required result: track prompt budgets, section priorities, token/character
    accounting, prompt-size diagnostics, and oversized-section tests.

- [x] Add prompt/history redaction and data-retention policy to prompt/runtime
  work.
  - Evidence: mutation prompts and critique prompts can include explicit
    context, plugin context, parent/inspiration code, and evaluator summaries,
    and they are stored under program metadata in `history.jsonl`. Only the
    LLM feedback workspace prompt path applies basic secret redaction today.
  - Current roadmap gap: safety work covered validator environment secrets, and
    prompt work covered context packing, but neither called out whether prompt
    content sent to providers and persisted in run artifacts should be full,
    redacted, hash-only, or omitted.
  - Required result: track shared redaction, prompt-log modes, data-retention
    defaults, redaction metadata/hashes, and tests for secret-like values in
    seeds/context/plugin text.

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
  - Status: implemented. Feedback prompts now render bounded candidate file
    sets and compact diagnostics with basic redaction and tests for non-primary
    files, oversized workspace truncation, and evaluator-output visibility.

- [x] Add LLM feedback failure isolation to evaluation hardening.
  - Evidence: `apply_llm_feedback()` lets provider exceptions, malformed
    `score` values and loose `discard` truthiness propagate or misclassify
    candidates outside the structured evaluation-stage contract. Invalid
    grader config fields are now rejected by `Config.validate()`.
  - Current roadmap gap: feedback calibration and config validation were
    tracked, but the roadmap did not call out failure isolation for optional
    feedback graders as an evaluation hardening item.
  - Status: implemented as an ignore-and-record policy. Provider failures,
    malformed response scores, non-finite response scores, and non-boolean
    discard values are recorded as `llm_feedback_failed` metadata and ignored
    for score/validity composition.

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

- [x] Add backend role semantics to scheduler work.
  - Evidence: config examples accept `role: breadth` and `role: depth`, and
    `build_llm()` carries role metadata into `LLMEnsemble`, but
    `_throughput_depth_select()` currently reads only numeric `cost`,
    `latency`, and `depth`.
  - Current roadmap gap: breadth/depth scheduling work covered cost/latency/
    depth tests but did not specify whether the role field is operational or
    descriptive.
  - Required result: either implement per-role quotas, escalation, and
    role-specific routing/accounting, or document role as descriptive metadata
    only with tests for the chosen behavior.

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
    while `LLMEnsemble._ucb1_select()` advances the global attempt counter
    before the provider call and `LLMEnsemble.generate()` increments backend
    counts only after a successful return.
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

- [x] Add deterministic critique-revision fallback behavior.
  - Evidence: a malformed synchronous critique response could previously
    replace an applicable mutation and be evaluated as a parser failure.
  - Status: implemented. Critique revisions are previewed before selection;
    malformed revisions fall back to the original mutation when it still
    applies cleanly, with parser diagnostics and selection metadata recorded in
    `metadata.critique`.
  - Remaining roadmap gap: reviewer pools, role routing, agreement policies,
    and async critique workers are still tracked separately.

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

- [x] Add per-program archive admission outcomes to database work.
  - Evidence: `evolve()` logs a program before calling `db.add()`, and archive
    insertion does not return whether a candidate entered a cell, replaced an
    occupant, was ignored by MAP-Elites competition, or was rejected by
    threshold.
  - Current roadmap gap: archive-state persistence covered snapshots and
    migration events, but not a per-history-record admission status that lets
    users understand which evaluated programs actually affected the archive.
  - Status: implemented. `history.jsonl` records
    `metadata.archive_admission` with threshold reason, island id, cell
    descriptors, replacement status, previous occupant ids, elite-list effects,
    and displaced elite ids.

- [x] Add validity/archive-aware run inspection to operational work.
  - Evidence: `cli.show()` selects the highest top-level `fitness` row from
    `history.jsonl` and prints only its primary-file `code`; it does not
    filter by `evaluation.is_valid`, `metadata.archive_admission.admitted`, or
    archived best workspace artifacts.
  - Current roadmap gap: run-inspection work mentioned summaries, lineage,
    metrics, and failure statistics, but not the correctness problem that
    "Best program" can mean highest logged row rather than best archived
    candidate.
  - Required result: make `show` validity-aware and archive-aware, report
    full-workspace artifacts and admission status, and add tests where invalid
    or non-admitted high-fitness rows do not win the displayed best.

- [x] Add aggregate workspace syntax diagnostics to evaluator feedback work.
  - Evidence: `_syntax_error()` checks candidate `.py` files in sorted order
    and returns on the first `SyntaxError`; a local proof with invalid `a.py`
    and `b.py` reported only the `a.py` failure while metadata listed both
    files.
  - Current roadmap gap: evaluator diagnostics covered structured results,
    stdout/stderr, retries, and artifacts, but not first-error-only syntax
    feedback in multi-file candidates.
  - Required result: report all Python syntax failures across a candidate
    workspace with file/line/offset/message details and carry them into
    history and prompt feedback.

- [x] Add strict JSONL serialization hardening to database work.
  - Evidence: `ProgramDatabase.log()`, `PromptDatabase._write()`, manifests,
    and `TTTRLPlugin._maybe_train()` now use strict finite JSON writers and
    quarantine invalid append records.
  - Current roadmap gap: database work covered queryability and sampling, but
    not the validity of persisted JSONL for strict downstream analysis.
  - Status: roadmap updated to treat strict finite JSONL as current coverage
    for candidate, prompt, manifest, and GRPO-export writers, while future
    artifact writers still need the same policy.

- [x] Add failure-history quarantine separation to database hardening.
  - Evidence: `ProgramDatabase.log_failure()` writes invalid
    `failure_history.jsonl` records to the shared `history_invalid.jsonl`
    quarantine. A local proof with a non-finite failed score created
    `history_invalid.jsonl` and no `failure_history_invalid.jsonl`.
  - Current roadmap gap: strict JSONL work covered candidate, prompt,
    manifest, and GRPO append writers, but not whether failure-memory records
    have a stream-specific quarantine/audit path.
  - Required result: define and test a separate failure-history quarantine or
    document the shared candidate/failure quarantine policy explicitly.

- [x] Add reproducibility hashes to run metadata work.
  - Evidence: AlphaEvolve-scale runs need exact problem, evaluator, prompt, and
    code-state provenance to support long-running comparisons.
  - Current roadmap gap: `manifest.json` existed, but the roadmap did not make
    code/problem/plugin/artifact hashes explicit.
  - Required result: track hashes/version metadata separately from basic config
    logging.

- [x] Add curated example artifact refresh to run-metadata work.
  - Evidence: `examples/runs/hello_world_ensemble` and
    `examples/runs/sorting_ttt_rl` contain `history.jsonl` and `best.py` only,
    while current CLI runs and artifact docs include `manifest.json`,
    `prompt_history.jsonl`, `failure_history.jsonl`, and `best_workspace/`.
  - Current roadmap gap: artifact work covered new run outputs but not whether
    committed examples still prove the documented artifact contract.
  - Required result: refresh curated examples to the current artifact schema,
    or clearly keep them as legacy history-only fixtures and test/document that
    boundary.

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

- [x] Add canonical mutation parsing to plugin truthfulness work.
  - Evidence: the core mutation path accepts both canonical AlphaEvolve
    SEARCH/REPLACE fences and the compact local form. `CausalPlugin` now uses
    that shared `parse_diff_blocks()` path for mutation factor detection, and
    tests cover compact, canonical, and mixed diff blocks.
  - Current roadmap gap: plugin extensibility/truthfulness work covered
    registration, config, artifacts, provenance, and score composition, but not
    shared mutation parsing semantics for plugins that inspect LLM patches.
  - Required result: require plugin mutation analysis to use the shared diff
    parser or mutation AST, and add compact/canonical parser tests for the
    CausalEvolve-inspired plugin before treating its guidance as format-stable.

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

- [x] Add evaluator process-tree cleanup to runtime hardening.
  - Evidence: `CascadeEvaluator._run_subprocess()` relies on
    `subprocess.run(..., timeout=...)` and does not create a process group, Job
    Object, or descendant-cleanup policy. A validator-spawned child process can
    outlive a timed-out direct validator process.
  - Current roadmap gap: runtime hardening covered timeouts, sandbox/resource
    limits, and environment secrets, but not cleanup of subprocess descendants
    created by evaluator code.
  - Required result: track process-group/job-object cleanup, timeout metadata,
    and tests showing validator children are terminated on timeout or failure.

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

- [x] Refresh current-state and near-term lists after workspace/evaluator
  implementation passes.
  - Evidence: `ROADMAP.md` still treated unified file-section path parsing,
    workspace topology mutation, workspace execution import/cwd semantics,
    full-workspace best export, strict scalar evaluator-output validation, and plugin
    score-composition provenance as near-term or open work after those local
    behaviors were implemented and documented.
  - Status: roadmap current-state bullets now include topology mutation,
    strict evaluator-output validation, archive admission events, and
    `best_workspace/`.
    Near-term bullets now focus on remaining gaps: load-time seed marker
    validation, binary/static artifacts, package-style validators, relative
    evaluator data, and workspace migration/resume.
  - Required result: keep roadmap work items phrased around the remaining
    AlphaEvolve divergences rather than stale already-implemented behavior.

## Existing Items That Need Tightening

- [x] Expand "better diversity measures" into measurable database/sampling
  requirements.
  - Evidence: `ROADMAP.md:85-88` is too vague to guide AlphaEvolve-compatible
    parent/inspiration sampling.
  - Required result: specify candidate features, metric-vector diversity,
    lineage diversity, recency, novelty, and score-conditioned inspiration
    sampling.

- [x] Add workspace-aware MAP-Elites descriptors to diversity/search work.
  - Evidence: `MAPElites._cell()` computes complexity and TF-IDF diversity from
    `Program.code`, which is only the primary-file view for workspace
    candidates.
  - Current roadmap gap: diversity work called for better measures generally,
    but not the distinct mismatch that multi-file candidates are archived by a
    single-file projection.
  - Required result: compute descriptors from canonical workspace contents or
    evaluator-provided behavior descriptors, persist descriptor values, and
    test non-primary file changes affecting cells and inspiration sampling.

- [x] Add stable MAP-Elites descriptor normalization/rebinning to diversity
  work.
  - Evidence: `MAPElites._norm_complexity()` mutates `_max_complexity` while
    assigning a candidate cell, and `_diversity()` uses the current capped
    elite list as its TF-IDF reference corpus. Existing grid occupants are not
    re-binned when either reference state changes.
  - Current roadmap gap: workspace-aware descriptors were tracked, but not the
    separate issue that even primary-file descriptor coordinates are
    insertion-order dependent unless normalization bounds or rebinning
    semantics are defined.
  - Required result: track fixed descriptor bounds, evaluator-provided behavior
    descriptors, persisted normalization state, or explicit rebin/snapshot
    events with tests for insertion-order stability.

- [x] Expand "training-data export" into a concrete ThetaEvolve/GRPO boundary.
  - Evidence: `ROADMAP.md:98-99` mentions downstream RL fine-tuning around
    `ttt_rl`, while the current plugin only writes JSONL and does not train.
  - Required result: define whether LibreEvolve will implement training,
    export-only datasets, or integration hooks, and document the divergence.

- [x] Add reward/export provenance to the ThetaEvolve boundary.
  - Evidence: `TTTRLPlugin` exports `reward = max(0.0, score)` and appends to
    a default `runs/grpo_data.jsonl` file outside the active per-run directory.
  - Current roadmap gap: the ThetaEvolve boundary distinguished export from
    training, but did not require explicit reward-shaping semantics, per-run
    dataset scoping, manifest linkage, or dataset hashes.
  - Required result: track raw score and shaped reward fields, document clipping
    or penalties, persist run-scoped dataset provenance, and add tests for
    negative rewards and repeated flush/resume behavior.

- [x] Move representative benchmarks earlier.
  - Evidence: `ROADMAP.md:92-95` keeps representative algorithmic benchmarks in
    longer term.
  - AlphaEvolve alignment need: benchmarks like matrix multiplication,
    circle/kissing packing, constructive math, or scheduling heuristics are
    needed to prove fidelity beyond toy examples.
