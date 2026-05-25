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
    meta-prompt evolution. Several local versions now exist, but they remain
    narrower than AlphaEvolve's flexible candidate API, async controller,
    full multi-objective search, and large-scale experiment loop.
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
    Malformed YAML and non-mapping top-level `config.yaml` files are now
    normalized into clear path-aware `ConfigError` startup diagnostics.
    Remaining runtime hardening is focused on plugin-specific config schemas
    and provider/model API capability validation.

- [ ] Add missing boolean-field validation to config hardening.
  - Evidence: AlphaEvolve-style experiments need explicit configuration
    switches for critique and meta-prompt evolution; stringly typed booleans
    can silently enable expensive or behavior-changing LLM paths.
  - Current evidence: `Config.validate()` checks booleans for
    `evaluator_artifact_redact_secrets`, `llm_fallback`, and
    `capture_proposal_metadata`, but not for `meta_prompt_evolution` or
    `critique_enabled`. A local proof accepted
    `Config(meta_prompt_evolution="false")` and
    `Config(critique_enabled="false")`; both fields remained strings and were
    truthy.
  - Required result: validate all boolean config fields, cover YAML/CLI paths
    with tests, and update configuration docs so the completed schema
    validation claim is bounded to what is actually enforced.

- [x] Add CLI/config precedence semantics to runtime hardening.
  - Evidence: `_build_config()` overwrites `config.yaml` `problem_name` with
    the problem directory name unless `--run-name` is supplied. Previously,
    `--reasoning-effort` applied only to CLI-created backend specs.
  - Current roadmap gap: the roadmap mentioned config validation but did not
    call out field-by-field precedence and effective-config override tests.
  - Status: OpenAI reasoning-effort override behavior is now deterministic and
    tested for config-file and CLI backend specs. Remaining ignored-override
    behavior for `problem_name` is tracked in the code TODO.

- [x] Add evaluator metric-contract validation to the backlog.
  - Evidence: AlphaEvolve Section 2.1 treats `evaluate` as returning scalar
    metrics, while LibreEvolve currently validates only enough of the result to
    compute primary fitness.
  - Current roadmap gap: evaluation hardening covered cascades and artifacts
    but not schema enforcement against `metrics.yaml`.
  - Required result: keep metric schema validation on the roadmap because
    multi-objective search depends on trustworthy metric vectors.

- [ ] Narrow roadmap "strict scalar validation" around reserved validity.
  - Roadmap evidence: `ROADMAP.md` current-state text says LibreEvolve has
    strict scalar evaluator-output validation against `metrics.yaml`.
  - Current evidence: scalar numeric validation is strict for declared
    non-`is_valid` metrics, but `is_valid` is a required boolean evaluator
    field that can still be declared as the primary `metrics.yaml` metric and
    used as normalized fitness.
  - Required result: either implement the reserved `is_valid` policy first, or
    update roadmap wording so strict scalar validation does not imply validity
    and optimization metrics are fully separated.

- [x] Add degenerate metric-bound validation to the backlog.
  - Evidence: `metrics.yaml` bounds drive primary fitness normalization and
    MAP-Elites performance coordinates, and `_validate_metric_schema()`
    previously accepted finite zero-width or inverted ranges.
  - Current roadmap gap: current-state bullets said strict scalar validation
    and metric direction/bounds normalization, but did not call out invalid
    bound ordering.
  - Status: implemented. Problem loading now rejects zero-width and inverted
    metric bounds with strict `[lo, hi]` ordering before metrics feed archive
    or multi-objective policy.

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
  - Status: implemented for fresh-run collision safety. The default policy
    fails if the target directory already contains known run artifacts;
    explicit `overwrite` removes only known run artifacts before a new run.
    `manifest.json` records `run_id` and the effective collision policy.
  - Remaining roadmap gap: this is not resume; saved archive/controller state,
    parent-run relationships, deterministic replay ids, and evaluator-code
    provenance remain tracked under resumability/reproducibility.

- [ ] Add run-directory path confinement to runtime hardening.
  - Roadmap evidence: run-directory collision policy now prevents accidental
    reuse of known artifacts, but roadmap/runtime docs do not require the final
    run directory to remain under `log_dir`.
  - Current evidence: `Path(config.log_dir) / config.problem_name` is used
    directly in database, prompt, evaluator-artifact, plugin-artifact, and
    best-workspace paths. `problem_name="../escaped"` writes outside the
    configured log root.
  - Required result: validate run names and final run paths before preparing
    or overwriting artifacts, then document the confinement policy.

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

- [ ] Add POSIX absolute-path rejection to candidate path hardening.
  - Roadmap evidence: path grammar hardening now says unsafe paths are
    rejected, but the implementation accepts leading-slash paths by stripping
    the slash.
  - Current evidence: `/abs.py` normalizes to `abs.py`, `//pkg/mod.py`
    normalizes to `pkg/mod.py`, and `<<<FILE /new.py ... >>>FILE` creates
    `new.py` without an error.
  - Required result: keep the candidate path grammar strictly relative across
    loader, mutation envelopes, topology commands, and materialization helpers.

- [x] Add candidate path-collision handling to candidate fidelity.
  - Evidence: path grammar hardening rejects unsafe paths, and
    `CandidateWorkspace` now rejects distinct raw inputs that normalize to the
    same candidate path. Materialization now preflights case-folded host paths
    before writing, so case-only variants fail closed on case-insensitive
    filesystems. Duplicate file edit sections now fail before partial
    application.
  - Current roadmap gap: workspace fidelity covered safe path grammar but not
    whether the candidate file set remains one-to-one after normalization and
    host filesystem materialization.
  - Required result: continue tracking Unicode normalization and
    topology-operation collision policy with tests for loader and mutation.

- [ ] Tighten roadmap collision work around evaluator/export failure
  semantics.
  - Roadmap evidence: `ROADMAP.md` still groups candidate collision work under
    workspace fidelity, but does not explicitly call out the remaining run
    reliability problem where host-filesystem materialization collisions can
    raise from evaluator or `best_workspace` export instead of becoming
    structured candidate diagnostics.
  - Current evidence: `CandidateWorkspace.materialize()` catches
    case-folded host collisions, while `CascadeEvaluator.evaluate()` and the
    CLI best-workspace writer do not convert that `ValueError` into a rejected
    candidate/failure-history record.
  - Required result: add evaluator/export materialization-failure handling to
    the roadmap's candidate fidelity or runtime hardening section, with tests
    proving the run stays alive and preserves diagnostics.

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

- [ ] Add strict primary-file identity validation to candidate fidelity.
  - Evidence: workspace candidates now persist `primary_file`, and that field
    controls the compatibility `code` view used by prompts, legacy validators,
    history, and `best.py`.
  - Current evidence: constructing
    `CandidateWorkspace(files={"helper.py": "x=1\n"}, primary_file="missing.py")`
    silently rewrites `primary_file` to `helper.py`. Mutation-time
    `PRIMARY missing.py` is rejected, so constructor/deserialization semantics
    are looser than topology mutation semantics.
  - Required result: reject missing explicit primary files at load/deserialize
    boundaries or require a documented fallback mode; test current seed
    directories, empty defaults, and future resume/history replay paths.

- [ ] Add duplicate primary-topology rejection to candidate fidelity.
  - Roadmap evidence: workspace topology mutation support now covers delete,
    move/rename, and primary-file reassignment, but the roadmap does not call
    out ambiguous duplicate primary commands.
  - Current evidence: `apply_workspace_mutation()` accepts multiple
    `<<<FILE PRIMARY ... >>>FILE` sections in one mutation and the later
    section silently wins. This is narrower than the duplicate edit/block
    rejection policy already tracked for other mutation envelopes.
  - Required result: reject or explicitly model multiple primary reassignments
    in one mutation, and add regression tests for no partial primary changes.

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

- [ ] Add explicit sample aggregation and per-metric stage pass policies to
  evaluation roadmap.
  - Evidence: current configured stages can run multiple seeded samples, but
    `_aggregate_metrics()` hard-codes numeric means. A local proof with a
    minimize primary metric `runtime` over seeds returning `0.0` and `10.0`
    produced aggregated `runtime=5.0` and `fitness=0.5`; there is no roadmap
    requirement for worst-case, quantile, all-samples-pass, or per-metric
    threshold semantics.
  - Required result: require stage configs to declare aggregation/pass policies
    per metric or document the fixed mean policy as a deliberate limitation.

- [x] Add evaluator artifact copy-out to evaluation hardening.
  - Evidence: `CascadeEvaluator._run_subprocess()` materializes the candidate
    in a `TemporaryDirectory`, runs the validator with that directory as `cwd`,
    and deletes the directory after returning metrics/stdout/stderr. Files
    written by validators are not copied into run artifacts.
  - Current roadmap gap: evaluation hardening mentioned artifacts broadly but
    did not identify the temporary-workspace data-loss mechanism or require
    stage/sample/attempt artifact provenance.
  - Status: implemented as opt-in artifact copy-out from the candidate
    workspace. Top-level and per-stage include/exclude patterns, size/count
    limits, text-artifact redaction policy, copied file hashes, skipped-file
    reasons, stage/sample/attempt provenance, and run-directory artifact paths
    are recorded, with tests proving files are retained after subprocess
    cleanup, stage overrides are honored, and secret-like text artifacts are
    redacted by default.
  - Remaining gap: files outside the candidate workspace are not retained.

- [ ] Add artifact copy-out confinement and streaming limits to evaluation
  hardening.
  - Evidence: `_matching_artifact_paths()` selects artifact paths with
    `Path.is_file()` under `cand_root`, and `_collect_evaluator_artifacts()`
    reads each matched file with `read_bytes()` before applying
    `artifact_max_bytes`. That makes the configured byte limit a retained-byte
    limit, not an I/O or memory limit. On platforms where symlinks are
    available, file symlinks under the candidate workspace can also resolve to
    targets outside the workspace unless the collector checks resolved targets
    or skips symlinks. This Windows account could not create a local symlink
    proof (`WinError 1314`), but the code does not contain the containment
    guard or skip metadata the roadmap should require.
  - Required result: make evaluator artifact collection stream or precheck file
    sizes before reading content, reject or explicitly skip symlink/path-escape
    artifacts, and record those skips in evaluation metadata.

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
    `IslandModel.migrate()` previously rounded migrant count with
    `max(1, ...)`, so zero still migrated one elite.
  - Current roadmap gap: numeric validation covered bounds checking but not the
    behavioral meaning of the lower bound for migration.
  - Status: implemented. Zero ratio selects no migrants; positive ratios still
    round up to one migrant per non-empty island when migration runs.

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

- [ ] Add semantic placeholder-retention rules to prompt-template validation.
  - Evidence: AlphaEvolve-style meta-prompt evolution should preserve the
    prompt channels required for candidate generation while improving wording
    or context policy.
  - Current evidence: `PromptDatabase.mutate()` validates syntax and known
    placeholders, but the only required placeholder is `{task}`. A local proof
    accepted an evolved template of `Task only: {task}`, dropping
    `{parent_code}` and `{mutation_instructions}` despite the meta-prompt
    instruction asking the LLM to keep placeholders intact.
  - Required result: extend prompt validation with mode-specific required
    placeholder/channel sets, quarantine semantic regressions, and cover
    configured variants plus evolved templates in tests.

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

- [ ] Remove implemented context-source manifest work from open roadmap
  wording.
  - Roadmap evidence: `ROADMAP.md` still says to "Add context-source manifests
    with recursive selection, include/exclude rules, source hashes, extraction
    diagnostics, and page/span citations" under prompt/context work.
  - Current evidence: `load_problem()` already supports recursive
    `.txt`/`.md`/`.py`/`.pdf` context ingestion, optional `context.yaml` /
    `context.yml` include/exclude rules, per-source SHA-256, extraction
    status, excerpt spans, and PDF page metadata for selected sources in
    `context_sources`. The remaining gap is not the existence of source
    records; it is recording the selection policy itself, skipped/excluded
    source diagnostics, better summarization/ranking, and prompt-budget
    packing. A local proof also showed that an unsupported typo key
    `includes:` in `context.yaml` is silently ignored, so the intended include
    policy can be lost without a startup diagnostic.
  - Required result: update ROADMAP so the open item is narrowed to the real
    remaining work, such as context-manifest file provenance, effective
    include/exclude policy, unknown-key diagnostics, skipped-source
    diagnostics, semantic ranking/summarization, global prompt budgets,
    artifact-content retrieval, and docs/tests for current context knobs.

- [x] Add live retrieval provenance to prompt/plugin context work.
  - Evidence: `DeepResearchPlugin` injects live arXiv search summaries into
    prompts. It now records bounded provider/query/status/timestamp/result
    length/synthesis-hash retrieval events plus arXiv source IDs/URLs,
    timestamps/authors, and summary hashes in candidate plugin-context
    metadata, while full result payloads, ranking provenance, source-content
    hashes, and richer artifact-level retrieval records remain open. Completed
    manifests include bounded `runtime.retrieval` summaries.
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
    earlier prompt feedback rendering only included compact recent stage
    summaries.
  - Current roadmap gap: the roadmap said evaluator feedback without calling
    out stdout/stderr, artifacts, LLM grader summaries, or sample-level
    diagnostics.
  - Status: implemented as bounded, redacted parent-feedback summaries for
    recent stage status, stdout/stderr, retry/sample attempts, artifact paths
    and hash prefixes, and LLM grader feedback. Full artifact-content retrieval
    and global prompt-size budgeting remain open.
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

- [ ] Add LLM feedback metric namespace/collision rules to evaluation and
  metrics work.
  - Evidence: `apply_llm_feedback()` writes grader scores directly into
    `updated.metrics[metric_name]`. A local proof configured a feedback grader
    with `metric: score` against an evaluator result whose primary metric was
    `score=0.8`; the feedback pass overwrote `metrics["score"]` with `0.1`
    while leaving `fitness=0.8`. This contradicts docs that say the raw primary
    validator metric remains intact and can corrupt declared metric vectors used
    for archive selection.
  - Required result: reserve evaluator metric names and fields, namespace
    feedback metrics or validate explicit overwrite policy, and test collisions
    with primary, secondary, `is_valid`, and `feedback_adjusted_fitness`.

- [x] Add proposal idea/rationale capture to prompt/context work.
  - Evidence: AlphaEvolve Figure 3 asks the LLM to suggest a new idea and
    describe changes with SEARCH/REPLACE blocks.
  - Current roadmap gap: prompt work covered templates/context but not a
    structured proposal artifact separate from raw patch text.
  - Status: partially implemented. `capture_proposal_metadata` asks for and
    stores bounded idea/rationale/hypothesis fields, and selected parent/
    inspiration candidates render bounded proposal summaries into prompts.
    Indexed historical resurfacing and proposal scoring remain open.
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
  - Status: implemented for normalized call telemetry and persisted call-role
    records on successful mutation, critique, feedback, and meta-prompt calls.
    Role-specific routing/reward policy remains open.
  - Required result: track and test mutation, critique, feedback, and
    meta-prompt accounting separately.

- [ ] Add backend reward-state validation to scheduler hardening.
  - Evidence: UCB-style scheduling assumes rewards are valid comparable
    scalars; AlphaEvolve-style backend routing should not allow invalid reward
    state to survive into long-running selection or future resume checkpoints.
  - Current evidence: `LLMEnsemble.record_reward()` accepts raw values without
    checking finiteness, sign, or bounds. A local proof injected `nan`, `inf`,
    and `-5.0` rewards; `wins` stored those values and later `generate()` calls
    continued from the corrupted scheduler state.
  - Required result: validate and normalize scheduler rewards at the ensemble
    boundary, define invalid-reward diagnostics/quarantine behavior, and test
    direct updates plus any future persisted/resumed bandit state.

- [x] Add normalized LLM call telemetry to backend scheduling work.
  - Evidence: backend adapters return plain text and discard provider usage,
    latency, retry counts, request ids, finish reasons, API mode, and raw
    provider diagnostics.
  - Current roadmap gap: backend work covered scheduling and role accounting
    but not the per-call telemetry needed to prove cost/latency/budget claims.
  - Status: implemented at the ensemble boundary for role, backend, backend
    metadata, strategy, API mode, prompt/output sizes and hashes, latency,
    status/error fields, and scheduler counts. Provider token usage,
    request/response ids, finish reasons, adapter-internal retry counts, and a
    separate run-scoped call log remain open.
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
  - Status: partially implemented at the ensemble boundary. `llm_max_retries`
    retries the same backend, `llm_fallback` can route to another backend, and
    call telemetry records retry/fallback attempt indexes plus retry/fallback
    decisions. The provider adapters still have their own hard-coded three
    attempts before the ensemble observes a failure, so configured retry
    budgets do not currently control total provider API attempts. Role-specific
    quarantine, timeout/rate-limit classification, and penalties remain open.
  - Required result: track per-role LLM retry budgets, fallback routing, failed
    attempt accounting, unified adapter/ensemble retry semantics, structured
    error logs, and tests for mutation, critique, feedback, and meta-prompt
    failures.

- [ ] Add provider-call timeout/cancellation policy to backend runtime work.
  - Evidence: `RunBudget` enforces `max_runtime_seconds` only when the loop
    checks limits before a generation or evaluation. `LLMEnsemble.generate()`
    then performs synchronous `backend.generate(prompt)` calls, and the
    OpenAI/Anthropic/Ollama adapters do not receive a LibreEvolve timeout or
    deadline. A slow or hung mutation, critique, feedback, or meta-prompt
    provider call can run past the configured runtime budget before the loop
    regains control.
  - Required result: define per-backend/per-role LLM request timeouts, pass
    remaining run deadlines into provider calls where SDKs allow it, classify
    timeout/cancellation separately from other provider errors, and persist
    structured timeout records in the LLM call log or role-specific artifacts.

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

- [ ] Disambiguate archive admission from cell-grid changes in database and
  reporting work.
  - Evidence: `MAPElites.add()` marks a program as admitted when it either
    enters/replaces a MAP-Elites grid cell or merely remains in the capped
    auxiliary `_elite` ranking list. A local proof with one bin and a large
    elite list showed a lower-scoring same-cell program returning
    `admitted=True`, `reason="elite_only"`, and `entered_cell=False` while the
    grid occupant stayed unchanged. Current `show` wording says
    "archive-admitted valid" based on that combined flag.
  - Required result: split cell-entry, cell-replacement, auxiliary-elite
    retention, and search-state-change fields; update `show` and run-artifact
    docs to report the distinction; and decide which pools are eligible for
    parent and inspiration sampling.

- [x] Add validity/archive-aware run inspection to operational work.
  - Evidence: `cli.show()` now filters modern histories by
    `metadata.archive_admission.admitted` and `evaluation.is_valid`, reports
    its selection mode, and prints selected metrics when present. Legacy
    histories without archive metadata still use highest-fitness fallback. It
    still prints only the selected primary-file `code` and not archived best
    workspace artifacts.
  - Current roadmap gap: run-inspection work mentioned summaries, lineage,
    metrics, and failure statistics, but not the correctness problem that
    "Best program" can mean highest logged row rather than best archived
    candidate.
  - Required result: keep the implemented validity/archive-aware best
    selection tests, then add full-workspace artifacts and richer admission,
    stage, lineage, archive, prompt, feedback, and failure diagnostics.

- [x] Add aggregate workspace syntax diagnostics to evaluator feedback work.
  - Evidence: `_syntax_errors()` now checks candidate `.py` files in sorted
    order and aggregates every `SyntaxError` into structured metadata.
  - Current roadmap gap: evaluator diagnostics covered structured results,
    stdout/stderr, retries, and artifacts, but not first-error-only syntax
    feedback in multi-file candidates.
  - Status: implemented for evaluation records/history. Python syntax failures
    across a candidate workspace now include file/line/offset/message details.
    Dedicated prompt rendering remains covered by the broader prompt-feedback
    gap.

- [x] Add strict JSONL serialization hardening to database work.
  - Evidence: `ProgramDatabase.log()`, `PromptDatabase._write()`, manifests,
    and `TTTRLPlugin._maybe_train()` now use strict finite JSON writers and
    quarantine invalid append records.
  - Current roadmap gap: database work covered queryability and sampling, but
    not the validity of persisted JSONL for strict downstream analysis.
  - Status: roadmap updated to treat strict finite JSONL as current coverage
    for candidate, prompt, manifest, and GRPO-export writers, while future
    artifact writers still need the same policy.

- [ ] Add malformed-history read diagnostics to operational/database work.
  - Evidence: strict JSONL hardening currently covers write paths, but
    AlphaEvolve-scale run inspection also needs robust read paths for long
    append-only histories.
  - Current evidence: `cli.show()` parses `history.jsonl` with raw
    `json.loads()` calls. A local proof with one valid line followed by
    `not-json` exited with an unhandled `JSONDecodeError` and no CLI output.
    Another proof showed that a modern record with archive-admission metadata
    but no `evaluation` is still labeled `archive-admitted valid`.
  - Required result: define strict read behavior for current and legacy
    histories, report file/line parse errors through normalized CLI
    diagnostics, require explicit validity evidence for current histories, and
    add tests for malformed, partially valid, and missing-evaluation histories.

- [x] Add failure-history quarantine separation to database hardening.
  - Evidence: `ProgramDatabase.log_failure()` previously wrote invalid
    `failure_history.jsonl` records to the shared `history_invalid.jsonl`
    quarantine.
  - Current roadmap gap: strict JSONL work covered candidate, prompt,
    manifest, and GRPO append writers, but not whether failure-memory records
    have a stream-specific quarantine/audit path.
  - Status: implemented. Failure-history append failures now use
    `failure_history_invalid.jsonl`, with tests proving they do not mix with
    candidate-history quarantine records.

- [x] Add reproducibility hashes to run metadata work.
  - Evidence: AlphaEvolve-scale runs need exact problem, evaluator, prompt, and
    code-state provenance to support long-running comparisons.
  - Current roadmap gap: `manifest.json` existed, but the roadmap did not make
    code/problem/plugin/artifact hashes explicit.
  - Status: implemented for Git state, `libreevolve/` source-tree hashes,
    problem-tree hashes, direct evaluator entrypoint hashes, and plugin module
    file hashes in `manifest.json`. Aggregate hashes for artifacts emitted
    after startup and validated plugin constructor/config specs remain open.
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

- [ ] Add plugin hook failure isolation to runtime/plugin hardening.
  - Evidence: the main loop invokes `on_generation_start`,
    `build_extra_context`, `prompt_context_metadata`, `on_evaluated`,
    `run_artifacts_metadata`, and `on_generation_end` directly. A local proof
    with a plugin whose `build_extra_context()` raises `RuntimeError` aborts the
    run before the candidate is mutated/evaluated or a plugin-failure artifact is
    written.
  - Required result: define structured plugin failure records, continuation vs
    abort policy per hook, score/failure quarantine behavior where appropriate,
    and tests for each hook category.

- [x] Add plugin score-composition provenance to plugin extensibility work.
  - Evidence: `evolve()` lets each plugin return a modified score and stores
    only the final `program.fitness`, while `evaluation.fitness` remains the
    evaluator/feedback result.
  - Current roadmap gap: plugin work mentioned registration, configuration, and
    artifacts but not the provenance of score-changing hook chains.
  - Required result: track per-plugin before/after scores, reasons, validation,
    and the relationship between raw evaluator fitness and composed archive
    fitness.

- [ ] Add plugin side-effect schema validation to database/plugin hardening.
  - Evidence: plugin score-return validation is not enough if plugins can also
    mutate `program.metrics` and `program.metadata` before archive admission
    and history logging.
  - Current evidence: a local proof plugin added
    `program.metrics["plugin_bad"] = inf` while returning a valid score.
    `evolve()` accepted the hook result until `ProgramDatabase.log()` raised
    `StrictJsonlError`; the rejected record appeared only in
    `history_invalid.jsonl`.
  - Required result: validate plugin-added metrics/metadata at the hook
    boundary, define quarantine or candidate-rejection semantics, and cover
    non-finite metrics plus non-serializable metadata in tests.

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
  - Evidence: `eval_stages[].validate_path` previously could resolve to
    arbitrary absolute paths and was not prevalidated or hashed before
    execution.
  - Current roadmap gap: evaluator hardening covered metric contracts,
    cascades, and artifacts but not validator-code path confinement and
    provenance.
  - Status: path confinement and direct entrypoint provenance are implemented.
    Stage validators must resolve to problem-local Python files; missing,
    directory, non-Python, outside-root, and symlink-escape paths are rejected.
    `manifest.json` records direct evaluator entrypoints with resolved path,
    problem-relative path, SHA-256 hash, byte count, source type, and stage
    usage metadata.
  - Remaining gap: transitive helper/data provenance and package-style
    evaluator semantics are not yet included in manifests.

- [x] Add validator environment/secret isolation to runtime hardening.
  - Evidence: `.env` is loaded into the parent process, and
    `CascadeEvaluator._run_subprocess()` calls `subprocess.run()` without an
    `env=` allowlist, so validators inherit provider keys and host environment
    variables by default.
  - Current roadmap gap: sandbox/resource-limit and evaluator-path work covered
    filesystem/process boundaries, but not inherited secrets, environment
    reproducibility, redaction, or network expectations.
  - Status: validator subprocesses now run with an explicit minimal
    environment plus `validator_env_allowlist`, metadata records environment
    keys without values, stdout/stderr is secret-redacted before persistence,
    and tests prove provider keys are hidden by default while opt-in variables
    are available.
  - Remaining gap: network egress policy and stronger sandbox/resource
    isolation remain open.

- [x] Add evaluator process-tree cleanup to runtime hardening.
  - Evidence: `CascadeEvaluator._run_subprocess()` relies on
    `subprocess.run(..., timeout=...)` and does not create a process group, Job
    Object, or descendant-cleanup policy. A validator-spawned child process can
    outlive a timed-out direct validator process.
  - Current roadmap gap: runtime hardening covered timeouts, sandbox/resource
    limits, and environment secrets, but not cleanup of subprocess descendants
    created by evaluator code.
  - Status: implemented for timeouts. Validators now run in a killable process
    tree, timeout results include cleanup metadata, and tests prove a spawned
    child cannot outlive a timeout and write a marker after evaluation returns.
  - Remaining gap: this is not full container/resource sandboxing or a general
    policy for detached work left by successful validators.

- [x] Add run-wide compute-budget accounting to runtime work.
  - Evidence: AlphaEvolve Section 2.6 describes maximizing evaluated ideas
    under a total computation budget, and paper ablations compare progress by
    fraction of consumed budget.
  - Current roadmap gap: the roadmap mentioned per-stage budgets and
    deterministic accounting, but did not require whole-run wall-clock,
    LLM-call, token, cost, evaluator-second, sample/retry counters, stop
    reasons, or equal-budget ablation reporting.
  - Status: implemented for local synchronous generation/evaluation budgets:
    `max_evaluations`, `max_evaluator_seconds`, `max_runtime_seconds`,
    per-candidate `metadata.budget`, and completed-manifest `runtime` stop
    summaries. LLM-call/token/cost, stage-sample/retry, accelerator, async
    queue, and equal-budget benchmark reporting remain open. The current loop
    can also count a generation as started before parent sampling; an
    all-invalid-seed run stops with `no_parent` and `generations_started: 1`
    despite doing no mutation-generation work.
  - Required result: make budget schemas, counters, stop reasons, manifest
    summaries, and budget-fraction benchmark reporting explicit runtime work,
    including startup/no-parent accounting.

- [ ] Add invalid-seed diagnostics to runtime/database hardening.
  - Roadmap evidence: current runtime/database work tracks candidate history,
    failure history, archive admission, and run stop reasons, but not the
    startup case where every initial seed evaluates invalid.
  - Current evidence: `evolve()` logs invalid seeds to `history.jsonl` with
    archive-admission rejection, but does not call `log_failure()` for seeds.
    A run with no valid seed stops at `no_parent` with no `failure_history.jsonl`
    and no prompt-visible failed-trial memory.
  - Required result: add a seed failure/diagnostic artifact or include invalid
    seeds in failure history, then update run accounting so all-invalid
    startup is explicit and queryable.

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

- [x] Refresh stale evaluation/runtime roadmap bullets after artifact,
  retry-attempt, environment, and budget hardening landed.
  - Evidence: `ROADMAP.md` still listed evaluator artifact collection,
    run-wide wall-clock/evaluator-second/stop-reason accounting, retry-attempt
    preservation, validator environment allowlisting, and degenerate metric
    bound rejection as near-term missing work.
  - Current evidence: `CascadeEvaluator` now collects configured artifacts,
    records retry attempts, uses a minimal validator environment with an
    allowlist, redacts persisted validator output, and records timeout cleanup
    metadata. `RunBudget` and completed manifests record generation,
    evaluation, evaluator-second, wall-clock, and stop-reason accounting.
    `load_problem()` rejects zero-width or inverted metric bounds.
  - Status: roadmap current-state bullets now include these implemented local
    behaviors. Near-term/mid-term bullets now focus on the remaining gaps:
    outside-workspace artifacts, aggregate artifact hashes, provider
    token/cost budgets, stage sample/retry totals, network/container
    sandboxing, transitive evaluator provenance, and benchmark artifact
    schemas.
  - Required result: keep roadmap bullets scoped to missing behavior, not work
    already proven by code and tests.

- [x] Refresh operational roadmap bullets after config-error and `show`
  hardening landed.
  - Evidence: `ROADMAP.md` still listed malformed/non-mapping `config.yaml`
    path-aware errors and validity/archive-aware `show` selection as missing
    operational work.
  - Current evidence: `_build_config()` catches YAML parse errors with the
    config path, rejects non-mapping top-level YAML with a path-aware
    `ConfigError`, and has CLI tests for both cases. `cli.show()` detects
    modern archive-admission metadata, selects archive-admitted valid records,
    prints the selection mode, and emits archive/metric summaries while keeping
    legacy highest-fitness fallback for old histories.
  - Status: roadmap operational work now keeps plugin/provider validation as
    the remaining config gap and describes `show` work as richer inspection
    beyond the current compact archive-aware view.
  - Required result: avoid listing already implemented operational hardening as
    future AlphaEvolve-alignment work.

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
  - Evidence: `TTTRLPlugin` exports raw score plus
    `reward = max(0.0, raw_score)`. CLI-loaded runs write under
    `plugin_artifacts/ttt_rl/` and completed manifests include path/hash/count
    metadata.
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
