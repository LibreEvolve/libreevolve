# Papers Todo: Reference and Specification Gaps

This list tracks mismatches discovered while reviewing the local `papers/`
directory and using the AlphaEvolve paper as the primary specification.

## AlphaEvolve Paper Requirements Not Yet Implemented

- [x] Task specification API with evolve-block markers.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: users mark code blocks to evolve inside a larger skeleton.
  - Status: implemented for Python single-file and local workspace candidates
    in `libreevolve/core/candidate.py`; malformed marker structures are
    rejected during mutation application with explicit diagnostics.
  - Remaining divergence: arbitrary-language runners remain open; malformed
    seeds are not prevalidated during problem loading; evolve blocks are still
    a text-file convention rather than a generalized problem-defined candidate
    API.

- [ ] Flexible candidate abstraction API.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: AlphaEvolve lets users choose the solution abstraction, from
    raw solution strings to constructor functions, bespoke search algorithms,
    or paired solution/search representations.
  - Current gap: LibreEvolve represents candidates as text file sets with a
    primary Python code view. Validators can interpret that code flexibly, but
    candidate rendering, mutation, persistence, and materialization are not
    problem-defined abstraction hooks.
  - Required result: add first-class candidate abstraction modes or document
    code-file evolution as a deliberate divergence from AlphaEvolve.

- [x] Rich prompt sampler.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompts may include previous solutions, system instructions,
    explicit context, stochastic formatting, rendered evaluation results, and
    meta-prompt evolution.
  - Status: implemented prompt templates, deterministic local context files
    including PDF extraction, whole-template stochastic variants, compact stage
    feedback summaries, and local prompt-program selection, scoring, lineage,
    optional LLM mutation, plus configured/evolved prompt-template validation
    with quarantine and parent penalties for invalid meta-prompt outputs.
  - Remaining divergence: stochastic formatting is whole-template sampling, not
    AlphaEvolve's placeholder alternatives with configured probability
    distributions; prompt feedback rendering is bounded summary-only and does
    not retrieve full artifact contents or participate in a global prompt
    budget; context ingestion is extractive first-span selection rather than
    semantic ranking; prompt assembly has no global context-window budget or
    section-level packing policy.

- [x] Output modes beyond SEARCH/REPLACE diffs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: diff blocks are default, but AlphaEvolve can ask for a complete
    code block when appropriate.
  - Status: implemented `diff` and `full` mutation modes. Canonical
    AlphaEvolve SEARCH/REPLACE fences and the compact local fences are both
    accepted, including mixed-format blocks in document order. The built-in
    prompt template now renders mode-specific instructions for `diff` and
    `full` mode. Workspace file sections can now edit/create files, delete
    files, move/rename files, and change the primary file. Remaining divergence:
    operation selection is still prompt-driven text parsing rather than a
    typed mutation AST or planner.

- [ ] Make workspace topology mutation intent unambiguous.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and 2.3.
  - Requirement: evolved code/codebases should preserve the user's intended
    task representation and mutation mode without silently dropping parts of an
    LLM proposal.
  - Current gap: duplicate file edit sections, duplicate block sections, and
    several edit/delete/move collisions are rejected, but duplicate
    `<<<FILE PRIMARY ... >>>FILE` sections are accepted and the later primary
    assignment silently wins. A local proof with `PRIMARY alt.py` followed by
    `PRIMARY third.py` returned `err=None` and selected `third.py`. The lower
    level workspace constructor can also silently change identity:
    `CandidateWorkspace(files={"helper.py": "x=1\n"}, primary_file="missing.py")`
    returns a workspace whose `primary_file` is `helper.py`.
  - Required result: reject or explicitly model multiple primary-file
    reassignment operations in one mutation, reject missing explicit primary
    files at construction/deserialization boundaries, and update the paper
    index's AlphaEvolve status row so workspace topology support does not imply
    a fully unambiguous mutation grammar.

- [x] Frontier model ensemble scheduling.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: combine a fast, lower-latency model for breadth with a stronger
    model for depth.
  - Status: added experimental `throughput_depth` scheduling metadata layered
    over UCB-style scores. Remaining divergence: the scheduler uses numeric
    `cost`, `latency`, and `depth` metadata but ignores descriptive `role`
    labels, so there are no breadth/depth quotas, escalation rules, or
    role-specific routing semantics yet. Ensemble telemetry now records call
    role, backend metadata, API mode, prompt/output sizes, latency, status, and
    scheduler counts. Provider usage, adapter-internal retry counts,
    response-id, finish-reason, and raw provider diagnostics remain unavailable.
    Ensemble-level retry and fallback are configurable, but role-specific
    failure quarantine and penalties remain open.

- [ ] Existing/custom LLM backend extension point.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 2 and Section 2.3.
  - Requirement: AlphaEvolve is model-agnostic and its setup includes a choice
    of existing or custom LLMs.
  - Current gap: LibreEvolve supports OpenAI, Anthropic, and Ollama through a
    hard-coded `build_llm()` registry. New providers require source edits
    rather than config-driven or plugin-driven backend registration.
  - Required result: add a custom backend interface/registry and tests, or
    document the fixed-provider scope as a deliberate divergence.

- [x] Configurable evaluation cascades.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: users can specify increasing-difficulty test ensembles and
    early-stage pruning.
  - Status: added configurable local validator stages with distinct entrypoints,
    thresholds, seeded samples, retries, stage context, and timeouts.
    Invalid stage numeric fields such as zero samples, negative retries,
    non-positive timeouts, nonnumeric thresholds, and `samples`/`seeds`
    mismatches are now rejected at startup. Distributed/parallel evaluator
    nodes remain open. Metric-specific pass criteria and explicit sample
    aggregation policies also remain open. Retry provenance is now recorded in
    `evaluation.metadata.attempts` for pass-first, fail-then-pass, and all-fail
    retry paths. A local proof with a minimize primary metric `runtime` and
    two samples returning `0.0` and `10.0` aggregated to `runtime=5.0` /
    `fitness=0.5`, confirming that current sample aggregation is a fixed mean
    policy rather than a configurable worst-case, quantile, or all-pass policy.

- [x] Strict scalar metric contract for evaluator outputs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: `evaluate` maps a solution to a dictionary of scalar
    evaluation metrics.
  - Status: implemented. Basic `metrics.yaml` schema validation rejects
    missing/duplicate names, invalid directions, multiple primaries,
    unsupported fields, malformed/non-finite bounds, and zero-width or inverted
    bounds. Evaluator output must include all declared metrics plus boolean
    `is_valid`, cannot include undeclared metrics, and every non-`is_valid`
    metric must be finite numeric. Invalid evaluator outputs are quarantined as
    `malformed_metrics`.

- [ ] Reserve evaluator validity separately from scalar optimization metrics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: evaluator outputs are scalar metrics for optimization, while
    validity/pass-fail information gates candidate admission and cascade
    progression.
  - Current gap: LibreEvolve requires a boolean `is_valid` field, but the
    metric schema still allows `is_valid` to be declared as the primary metric.
    That makes boolean validity itself the normalized optimization score
    instead of a separate gate.
  - Required result: make `is_valid` a reserved evaluator field outside the
    scalar metric list, or at least reject it as primary; update the paper
    index so "strict scalar metric validation" does not imply the reserved
    validity boundary is fully enforced.

- [x] Correct paper-index metric-validation wording.
  - Paper-index evidence: `papers/README.md` summarized AlphaEvolve status as
    "strict scalar metric validation."
  - Status: metric schema validation now rejects zero-width and inverted
    bounds, so the paper index no longer needs to list strict metric-bound
    ordering as an open AlphaEvolve-alignment gap.

- [x] LLM-generated feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: optional LLM graders can score hard-to-capture properties or
    discard candidates.
  - Status: implemented as optional synchronous LLM graders with metrics,
    weighted score composition, discard rules, backend provenance, raw
    responses, `history.jsonl` visibility, bounded full-workspace prompt
    rendering, basic redaction, and compact evaluator diagnostics. Parallel
    reviewer workers and calibrated grader ensembles remain open.
  - Remaining divergence: feedback scores are not validated against
    `metrics.yaml` bounds/directions and can be added directly to normalized
    fitness without calibration. The archive `selection_score` is still
    recomputed from declared evaluator metrics, so feedback-adjusted fitness is
    not a first-class MAP-Elites selection signal except as a downstream
    top-level-fitness tie-breaker. Feedback metric names are also not
    namespaced or collision-checked: a local proof configured `metric: score`
    for a grader and overwrote the evaluator's primary `metrics["score"]` from
    `0.8` to the grader score `0.1` while leaving top-level fitness at `0.8`.

- [x] Critique revision should not degrade valid generated mutations into
  parser failures.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: critique/review is part of the quality-improvement loop.
  - Status: implemented for the synchronous critique path. Revised mutations
    are previewed with the active parser; malformed revisions fall back to the
    original mutation when the original applies cleanly, and selection plus
    parser diagnostics are logged in `metadata.critique`.
  - Remaining divergence: this is still one synchronous self-revision call, not
    AlphaEvolve-scale reviewer pools or async reviewer workers.

- [ ] Parallelized evaluation and asynchronous throughput.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: expensive evaluations can be parallelized, and the whole
    pipeline runs as an async controller with LLM samplers and evaluation nodes.
  - Current gap: `evolve()` is synchronous and evaluates one candidate at a time.

- [ ] Overall compute-budget accounting and ablation support.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.6 and 4.
  - Requirement: AlphaEvolve optimizes throughput under a fixed computation
    budget, and ablations compare performance as a function of consumed budget.
  - Partial status: LibreEvolve now has a local `RunBudget` for
    `max_generations`, optional total evaluation count, optional cumulative
    evaluator seconds, and optional wall-clock seconds. Candidate history
    records include budget snapshots, and completed manifests include consumed
    budgets plus structured stop reason.
  - Current gap: token/cost accounting, LLM-call retry budgets, stage-sample
    budgets, accelerator budgets, async queue accounting, and benchmark reports
    by compute-budget fraction are still missing. Provider adapters also have
    hard-coded internal retries, so the configured ensemble retry budget does
    not fully determine or report total provider API attempts. LLM provider
    calls also lack configured request timeouts/deadlines, so a slow or hung
    mutation, critique, feedback, or meta-prompt call can exceed
    `max_runtime_seconds` before `RunBudget` is checked again.
  - Required result: persist budget configuration and consumption in manifests
    and history, stop deterministically on exhausted budgets, unify retry
    accounting across provider adapters and the ensemble, propagate runtime
    deadlines or provider-call timeouts into LLM calls, and add benchmark
    scripts/reports that can compare variants at equal budget fractions.

- [ ] Run identity, collision policy, and evaluator-code provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: task setup and evaluation code define what a run means, and
    long-running experiments need reproducible accounting for the code,
    evaluators, and generated program database.
  - Partial status: run identity and collision semantics are implemented.
    `manifest.json` records a UUID4 `run_id` and effective collision policy.
    Existing known run artifacts now fail startup by default; explicit
    `overwrite` removes only known run artifacts before the new run. Configured
    `validate_path` entries are constrained to problem-local Python files, and
    direct evaluator entrypoints are recorded in `manifest.json` with resolved
    paths, problem-relative paths, SHA-256 hashes, byte counts, source type,
    and stage usage metadata. The manifest also records Git state when
    available, `libreevolve/` source-tree hashes, problem-tree hashes, and
    plugin module file hashes. Transitive helper/data provenance, validated
    plugin constructor/config specs, and aggregate emitted-artifact hashes are
    still missing. Seeded replay is incomplete because persisted `Program` and
    `PromptProgram` lineage ids are UUID4 values rather than deterministic
    seed/run-derived identifiers. Validator subprocesses now use an explicit
    minimal environment plus `validator_env_allowlist`, so `.env` provider
    credentials are hidden by default and persisted stdout/stderr is
    secret-redacted. Network egress policy and stronger sandboxing remain
    incomplete. Validator timeouts now attempt process-tree cleanup and record
    cleanup metadata, but this is not a full resource sandbox. Problem-local
    evaluator helper modules are imported only as sibling modules beside a
    configured validator file; package-style validator entrypoints, relative
    evaluator data policy, and transitive helper/data hashes are still missing.
    Run artifact path confinement is also incomplete: `problem_name` /
    `--run-name` can contain `../` and write manifests/history/artifacts
    outside the configured `log_dir`.
  - Required result: add true resume semantics, transitive evaluator import/data
    provenance, aggregate artifact hashes, and run-directory confinement;
    define deterministic lineage-id behavior or document UUID identity as
    outside the replay contract. Run ids, fail/overwrite collision policy,
    direct evaluator hashes, source/problem hashes, and plugin module hashes
    are already implemented locally.

- [ ] Treat evaluator artifact confinement as part of reproducible run
  evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: stored evaluation artifacts should be bounded and attributable
    to the evaluated candidate/workspace, because they become part of the
    program database evidence used for later analysis and inspiration.
  - Current evidence: evaluator artifacts are copied from matching paths under
    the temporary candidate workspace, but the collector does not resolve
    matched paths back inside the workspace before reading. On platforms that
    permit symlinks, `Path.is_file()` / `read_bytes()` can follow a
    validator-created file symlink to an outside target; this Windows account
    could not create the proof symlink (`WinError 1314`), but the code lacks a
    containment guard or symlink skip record. `artifact_max_bytes` is enforced
    only after `read_bytes()`, so it does not cap read-time memory/I/O.
  - Required result: classify artifact copy-out confinement and streaming byte
    limits as required evaluation-provenance behavior, not just operational
    polish; persist skip reasons for symlink/path escapes and oversized files.

- [ ] Multiple-score optimization.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: optimize multiple user-provided scores and use programs that
    excel under different criteria as varied inspirations.
  - Partial status: metric vectors are stored, normalized primary fitness
    honors direction/bounds, and declared numeric metrics are normalized into
    an equal-weight archive `selection_score` used for MAP-Elites replacement,
    elite ordering, and exploit/best sampling. Feedback metric calibration,
    configurable weights, metric-specific elites, and Pareto/frontier
    optimization remain open. Parent and inspiration sampling can now use
    metric-leader, novelty, recency, selection-score, random, and mixed
    strategies while excluding the selected parent and deduplicating migrated
    copies by program id. Persisted/queryable feedback and lineage-aware
    resurfacing remain open. Metric bounds are now strictly ordered before they
    can be used as policy inputs.

- [x] Evolutionary database with attached outputs and feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: solutions have scores and program outputs attached, and the
    database resurfaces ideas to balance exploration/exploitation.
  - Status: JSONL records include raw metrics, structured evaluation output,
    per-program archive admission events, and configurable in-memory
    score/metric/novelty/recency inspiration sampling. Queryable persisted
    feedback and lineage-aware sampling remain open.
    `metadata.score_composition` stores per-plugin score adjustments, and
    archive admission is now gated by evaluator/feedback validity as well as
    final composed fitness. Full MAP-Elites cell/island snapshots plus
    migration events are not persisted. Population config semantics now define
    `migration_ratio=0.0` as selecting no migrants; positive migration ratios
    still round up to at least one migrant from a non-empty island.
    Admission semantics still conflate MAP-Elites grid entry/replacement with
    auxiliary elite-list retention: a local proof with one cell and a large
    elite list produced `admitted=True`, `reason="elite_only"`, and
    `entered_cell=False` for a lower-scoring same-cell candidate while the grid
    occupant did not change. Plugin side effects can also corrupt the history
    record after evaluation: a local proof added
    `program.metrics["plugin_bad"] = inf` in `on_evaluated()`, after which
    `evolve()` raised `StrictJsonlError` while writing `history.jsonl`.
  - Required result: split persisted database fields so later analysis can tell
    whether a candidate changed a MAP-Elites behavior cell, was retained only in
    a global/auxiliary elite list, or was merely evaluated and logged; validate
    plugin-added metrics/metadata before they enter persisted program records.

- [ ] Preserve invalid seed diagnostics as first-class database evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: initial and evolved solutions should have evaluation scores,
    outputs, and feedback attached so the evolutionary database and run
    accounting explain what was tried under the compute budget.
  - Current gap: invalid seeds are logged to `history.jsonl` with
    `archive_admission.reason = invalid_evaluation`, but they are not written
    to `failure_history.jsonl` or another seed-diagnostic stream. With an
    all-invalid seed population, the run stops at `no_parent` before any LLM
    mutation, leaving failure memory empty even though evaluated invalid
    candidates exist.
  - Required result: record invalid seed evaluations with diagnostics and
    admission reasons in a queryable artifact, and make no-valid-seed stop
    accounting distinguish startup exhaustion from a real generation.

- [ ] Rich prompt rendering of execution outputs and feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompt context can include program execution results, outputs,
    and scores from previous attempts.
  - Partial status: history records preserve stdout/stderr, retry-attempt
    records, aggregate syntax diagnostics, artifact metadata, and LLM feedback
    provenance. Prompt construction now renders bounded, redacted parent
    summaries for recent stage status, execution output, retry/sample attempts,
    evaluator artifact paths and hash prefixes, and LLM grader feedback.
  - Current gap: prompt construction still does not retrieve artifact file
    contents, render full validator metadata, include first-error aggregate
    syntax diagnostics in a specialized format, or enforce a global prompt-size
    budget across all feedback/context sections.
  - Required result: add bounded prompt sections for execution outputs,
    artifacts, validator feedback, sample-level diagnostics, aggregate syntax
    diagnostics, and grader feedback summaries.

- [ ] Persist complete explicit-context selection provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: explicit context and relevant literature can shape prompt
    sampling, so reproducible experiments need to know which context was made
    available and why.
  - Current gap: local context ingestion records hashes/excerpts for selected
    `.txt`, `.md`, `.py`, and `.pdf` sources, but does not persist the
    `context.yaml` manifest hash, include/exclude rules, skipped files, or
    unsupported/excluded source diagnostics in `manifest.json`. Unsupported
    context manifest keys are also ignored silently: a local proof with
    `includes: ["missing/*.md"]` selected `keep.md` and emitted no diagnostic
    that the intended include policy was not applied.
  - Required result: treat context selection policy as part of task
    provenance, not only selected-source metadata; reject or record unknown
    context policy keys; and update the paper index AlphaEvolve row so
    "prompt sampler/context ingestion" does not imply full context-selection
    reproducibility.

- [x] Failed-trial and rejected-mutation memory.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figures 1-2 and Section 2.2.
  - Requirement: the program database and prompt sampler provide rich context
    containing past trials, ideas, quality scores, and feedback so future
    generations can learn from explored attempts.
  - Status: implemented as a local JSONL failure index plus bounded recent
    prompt memory. `failure_history.jsonl` records failed/rejected proposals
    with error causes, bounded evaluator output summaries, changed files,
    parent ids, mutation text, and repetition counts. Remaining divergence:
    failure retrieval is a recent-tail heuristic, not a learned or
    diversity-aware sampler over all historical negative examples. Invalid
    failure-history append diagnostics now use `failure_history_invalid.jsonl`.

- [ ] Robust history read/inspection path for long experiment stores.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Requirement: the program database is the durable substrate for selection,
    inspection, and future prompt context; long append-only experiment logs
    need controlled failure modes when a record is malformed.
  - Current evidence: write paths are strict, but `libreevolve show` reads
    `history.jsonl` with raw `json.loads()` calls. A local proof with one valid
    row followed by `not-json` produced an unhandled `JSONDecodeError` and no
    CLI diagnostic. Another proof showed that a modern history row with
    `metadata.archive_admission.admitted: true` but no `evaluation` is reported
    by `show` as `archive-admitted valid`.
  - Missing: a strict read/repair/quarantine policy, file/line diagnostics,
    explicit validity requirements for current history rows, and tests proving
    partially corrupt histories are handled intentionally instead of breaking
    run inspection.

- [x] Full-file/full-codebase evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 4 ablations.
  - Requirement: AlphaEvolve evolves whole code files/codebases and ablates
    "No full-file evolution" as a weaker setting.
  - Current evidence: `CandidateWorkspace` supports local text file sets,
    `<<<FILE path ... >>>FILE` mutation envelopes, full-mode file creation,
    workspace materialization for validators, and JSONL file-set logging.
  - Status: implemented for local Python/text workspaces. Remaining divergence:
    no arbitrary external repository/build-system runner and `best.py` exports
    only the primary file convenience view. Binary/static artifacts are not
    first-class candidate members yet. Validator subprocesses now run with the
    candidate root as `cwd` and import path, but there is still no arbitrary
    external repository/build-system runner. Candidate path collision handling
    is also incomplete: candidate construction rejects duplicate normalized
    paths and materialization rejects case-folded host-path collisions before
    writes, and duplicate file edit sections are rejected before partial
    application, but complex topology-operation collision policy remains
    incomplete.
    File/block envelope diagnostics now reject malformed sections before
    partial edits are applied. File-set topology changes such as delete, rename,
    move, and primary-file replacement are implemented with command file
    sections. POSIX-style absolute candidate paths remain a path-grammar gap:
    leading slashes are stripped, so `/new.py` is treated as relative
    `new.py` instead of rejected.

- [ ] Treat workspace materialization failures as evaluated/rejected
  candidates.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Sections 2.1/2.5.
  - Requirement: full-codebase evolution needs robust handling for invalid
    generated codebase states, with database records that preserve the failed
    idea and diagnostics for future sampling.
  - Current gap: LibreEvolve rejects logical duplicate candidate paths during
    `CandidateWorkspace` construction, but host-specific materialization
    collisions are raised from `CandidateWorkspace.materialize()`. Those
    exceptions are not currently converted into structured evaluator/failure
    records, so some invalid codebase candidates can terminate a run instead
    of entering failure memory.
  - Required result: classify materialization errors as structured invalid
    evaluations or mutation failures with diagnostics, keep the run alive, and
    persist enough metadata for prompt/failure retrieval.

- [x] Full-workspace output artifacts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 2.1.
  - Requirement: if a candidate is a full file/codebase, the selected best
    candidate must be recoverable as a full codebase.
  - Status: implemented for local text-file candidate workspaces. The CLI
    writes `best.py` as a primary-file compatibility view and materializes the
    complete best file set under `best_workspace/`; run-artifact docs and CLI
    tests cover this behavior.
  - Remaining divergence: binary/static non-text artifacts are not first-class
    candidate members, and resume semantics remain unresolved. Run-directory
    collision policy is implemented as fail/overwrite, but it is not resume.
    The committed example run directories are legacy history-only fixtures and
    do not include `best_workspace/`, so they do not prove the current
    full-workspace artifact contract.

- [x] Canonical AlphaEvolve diff block compatibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Figure 3.
  - Requirement: support the paper's SEARCH/REPLACE fence spelling when using
    AlphaEvolve-style prompts or examples.
  - Status: implemented in `libreevolve/core/diff.py` while preserving the
    compact local format; tests cover canonical parsing for normal candidates,
    evolve-block candidates, mixed-format document order, multi-file file
    sections, and duplicate `<<<BLOCK ...>>>` rejection for multi-block full
    replacement.
  - Required result: keep accepting both canonical and compact diff formats
    without breaking existing seeds/tests.

- [ ] Structured proposal idea/rationale capture.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 3 and Section 2.3.
  - Requirement: AlphaEvolve asks the LLM to suggest a new idea and describe
    changes with SEARCH/REPLACE blocks; the evolutionary loop benefits from
    keeping generated ideas, critiques, and outcomes connected.
  - Current status: `capture_proposal_metadata` can request short `IDEA`,
    `RATIONALE`, and `HYPOTHESIS` sections and stores parsed fields under
    `metadata.proposal` while preserving diff-only compatibility. Selected
    parent and inspiration candidates now render bounded proposal summaries in
    prompts. Remaining gap: those proposal artifacts are not yet scored,
    critiqued independently, searched, or used as an indexed retrieval signal
    for resurfacing.
  - Required result: support a configured response format that separates
    proposal rationale from patch blocks while preserving diff-only
    compatibility.

- [x] Meta-prompt evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt instructions/context can be co-evolved in a separate
    database.
  - Current evidence: `PromptDatabase` stores prompt programs, logs
    `prompt_history.jsonl`, records prompt rewards/usages, and supports
    lineage-preserving mutation. `evolve()` uses prompt programs during prompt
    construction and can optionally ask the active LLM to mutate templates.
  - Status: implemented locally. Prompt-program reward now has an explicit
    absolute/improvement mode, bounded normalization, configurable exploration
    coefficient, and persisted reward telemetry. Remaining divergence: initial
    configured prompt variants are selected through UUID4-ordered untried
    prompt programs rather than a seeded/config-order policy. Prompt-program
    reward is still a scalar final-score/improvement policy rather than a
    multi-metric prompt-fitness model. Meta-prompt mutations are syntax-checked
    but can still drop essential channels: a local proof admitted
    `Task only: {task}` as an evolved child template, omitting `{parent_code}`
    and `{mutation_instructions}`. There is no full experiment
    AlphaEvolve-equivalent ablation harness.

- [ ] Context-policy side of meta-prompt evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt instructions and prompt context can be improved through
    meta-prompt evolution.
  - Current evidence: LibreEvolve's meta-prompt path mutates only full prompt
    template strings. Context rendering remains fixed in `PromptSampler` and
    related code: problem context files, plugin context, inspirations, recent
    failures, evaluator feedback, and mutation-mode instructions are selected
    and budgeted by static code/config rather than prompt-program state.
  - Required result: extend prompt programs to include structured context
    selection/rendering/budget policy, persist and score those policies, and
    test that meta-prompt evolution can alter context behavior while preserving
    safe template rendering and auditability.

- [ ] AlphaEvolve-style stochastic prompt formatting.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: support template placeholders with human-provided alternatives
    and probabilities in configuration.
  - Current gap: prompt variation is uniform whole-template selection and does
    not implement probability-distribution placeholders.

## Local Paper Corpus Issues

- [x] Refresh the local paper index after implementation passes.
  - Evidence: `papers/README.md` still listed multi-file candidates, critique,
    LLM feedback, and meta-prompt evolution as open after those local
    implementations landed.
  - Status: refreshed the AlphaEvolve row to distinguish implemented local
    behavior from remaining async, multi-objective, database, full-workspace
    export/resume, run-identity/evaluator-provenance, metric-validation,
    feedback-calibration, LLM-accounting, config-validation, and benchmark
    gaps.
  - Required result: keep the paper index aligned with current code whenever
    todo items are completed or reopened.

- [x] Remove stale implemented-gap claims from the AlphaEvolve paper-index row.
  - Evidence: `papers/README.md` still listed workspace file-topology
    mutation, full-workspace best export, full-workspace feedback grading,
    feedback failure isolation, workspace execution/import fidelity, strict
    scalar evaluator-output validation, and broad top-level config validation
    as remaining AlphaEvolve gaps even though current code/docs/tests cover
    those local implementations.
  - Status: refreshed the AlphaEvolve status row so implemented local behavior
    is not duplicated in the remaining-open list. The row still calls out
    unresolved gaps such as flexible candidate abstractions, binary/static
    artifacts, candidate path-collision handling, strict metric-bound ordering,
    workspace-aware descriptors, custom backend registration, async workers,
    provider failure policy, network/container sandboxing, provider token/cost/
    stage-sample budgets, true multi-objective search, queryable database,
    archive/resume state, reproducible ids, feedback calibration,
    role-specific LLM routing/reward policy, plugin provenance, and benchmark
    hardening.

- [x] Tighten paper-index wording around validator execution boundaries.
  - Evidence: `papers/README.md` described implemented AlphaEvolve-alignment
    behavior as "validator environment isolation."
  - Current evidence: validators run in a local subprocess with an explicit
    minimal environment plus `validator_env_allowlist`, persisted stdout/stderr
    redaction, timeout process-tree cleanup, and optional artifact copy-out.
    This is not a security sandbox or full environment isolation: network
    egress policy, container isolation, and resource controls remain open.
  - Status: paper index now says "validator environment allowlisting with
    stdout/stderr redaction" and lists network/container sandboxing as an open
    gap.
  - Required result: avoid using "isolation" for current validator execution
    until the implementation provides a stronger sandbox boundary.

- [x] Decide and document the paper corpus source of truth.
  - Evidence: `papers/download_manifest.csv` lists 24 downloaded papers, while
    the README claims 23 references.
  - Required result: update README badges/text and possibly add a
    `papers/README.md` that explains why each PDF is present.

- [x] Track the paper index and manifests without committing PDFs.
  - Evidence: README points readers to `papers/README.md`, but `.gitignore`
    ignored the entire `papers/` directory.
  - Status: `.gitignore` now ignores `papers/*` while allowing
    `papers/README.md`, `download_manifest.csv`, and
    `download_manifest.json`.
  - Required result: keep small paper-index evidence in version control while
    leaving large cached PDFs local.

- [x] Add a paper index with roles and implementation status.
  - Evidence: downloaded papers include system papers, domain-result papers,
    and foundational algorithm papers, but only a subset is summarized in the
    README.
  - Required result: create a table with paper id, title, role, implemented
    status, and linked todo items.

- [x] Separate AlphaEvolve requirements from other-paper inspirations.
  - Evidence: code comments cite non-AlphaEvolve papers for local choices, such
    as TF-IDF diversity, CausalEvolve heuristics, DeepEvolve arXiv search, and
    ThetaEvolve JSONL export.
  - Required result: document which features are necessary for AlphaEvolve
  fidelity and which are optional LibreEvolve extensions.

- [x] Turn the downloaded benchmark/result papers into explicit benchmark
  coverage decisions.
  - Evidence: `papers/download_manifest.csv` includes domain-result papers for
    sums/differences, autoconvolution, hardness of approximation, Bruhat
    intervals, global NLP optimization, multiagent learning, Ramsey numbers,
    Berczy combinatorics, bilateral trade, and related AlphaEvolve-style
    mathematical results.
  - Current evidence: `libreevolve/problems/examples/` contains
    `hello_world`, `sorting`, `circle_packing`, and `matrix_multiplication`.
  - Required result: for each downloaded domain paper, either add a
    corresponding problem fixture/benchmark, link it to an existing benchmark,
    or mark it as background-only in a paper index.

- [x] Add AlphaEvolve-paper benchmark parity targets.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` evaluates matrix
    multiplication, many constructive math problems, data-center scheduling,
    TPU arithmetic circuits, LLM-training kernels, and FlashAttention/GPU
    instruction optimization.
  - Current evidence: checked-in AlphaEvolve-adjacent examples include
    `circle_packing` and `matrix_multiplication`.
  - Required result: choose a small reproducible subset, such as matrix
    multiplication rank search, circle/kissing packing, and one scheduling or
    kernel microbenchmark, then add validators and expected run artifacts.

- [ ] Harden benchmark implementations beyond smoke-example fidelity.
  - Paper evidence: the AlphaEvolve paper's matrix task searches low-rank tensor
    decompositions with randomized initializations and exact verification;
    Appendix B.12 reports circle packing in the unit square for `n = 26` and
    `n = 32`; Figure 8 compares ablations by compute-budget fraction.
  - Current evidence: the checked-in matrix example validates only a 2x2 Python
    `matmul2` function on three deterministic cases and counts AST
    multiplication nodes. The circle example matches the fixed-26 unit-square
    objective family, but there is no benchmark harness for repeated seeds,
    SOTA thresholds, saved construction artifacts, visual/JSON outputs, or
    equal-budget ablation curves.
  - Required result: distinguish smoke examples from benchmark fixtures in docs,
    add operation/rank-aware matrix validation, add artifact schemas for
    geometric constructions, and create repeatable benchmark reports tied to
    AlphaEvolve target families.

- [x] Clarify paper-index benchmark wording for circle packing.
  - Paper-index evidence: `papers/README.md` listed `circle_packing` under
    implemented benchmark coverage as an AlphaEvolve-adjacent packing benchmark.
  - Current evidence: the fixture validates fixed-26 unit-square feasibility
    and summed radii, while `tests/test_examples.py` only checks seed validity
    plus simple rejection cases. There are no repeated-seed runs, SOTA/target
    thresholds, saved construction artifact schemas, visual/JSON outputs, or
    benchmark reports.
  - Required result: describe `circle_packing` as an AlphaEvolve-adjacent smoke
    fixture until benchmark hardening is implemented.

## Paper-Inspired Feature Claims Needing Correction

- [ ] Keep CausalEvolve-inspired behavior explicitly paper-limited or implement
  the paper's causal scratchpad.
  - Paper evidence: `2603.14575__CausalEvolve.pdf` describes LLM-assisted
    causal factor identification, outcome-level factors, surprise-pattern
    inspection, and abductive reasoning to hypothesize new factors during
    evolution.
  - Current evidence: the CLI alias is paper-neutral (`causal`) and docs label
    it CausalEvolve-inspired, but `libreevolve/plugins/causal.py` still uses
    regex factor detection over changed diff tokens and UCB1-like reward
    accounting. Its factor detector now uses the shared compact/canonical
    SEARCH/REPLACE parser, but the detected factors are still fixed local
    token-pattern categories rather than LLM-discovered causal variables.
  - Missing: LLM causal scratchpad, POMDP/causal framing, initial factor
    discovery, surprise-pattern inspection, abductive factor creation,
    and structured causal knowledge reuse.

- [ ] Keep DeepEvolve-inspired behavior explicitly paper-limited or implement
  DeepEvolve's retrieval, cross-file editing, and debugging loop.
  - Paper evidence: `2510.06056__DeepEvolve.pdf` integrates external knowledge
    retrieval, cross-file code editing, systematic debugging, hypothesis
    refinement, implementation, and testing in each iteration.
  - Current evidence: the CLI alias is paper-neutral (`deep_research`) and docs
    label it DeepEvolve-inspired, but `libreevolve/plugins/deep_research.py`
    performs a generic arXiv Atom search every N generations and injects short
    summaries into the prompt. Candidate metadata records bounded retrieval
    events with provider, query, timestamp, status, result length, synthesis
    hash, best-program context, arXiv source IDs/URLs, source
    timestamps/authors, summary hashes, available provider errors, and
    structured error types when available. The run manifest records bounded
    retrieval summaries. The plugin does not persist full result payloads,
    ranking provenance, or source-content hashes for the injected context.
  - Missing: broad external retrieval, source ranking, hypothesis synthesis,
    full retrieval payload/artifact retention, source-content hashes,
    implementation/refinement loop, systematic debugging, cross-file editing,
    and benchmark-grounded result validation.

- [ ] Isolate paper-inspired plugin failures from the core evolutionary loop.
  - Paper evidence: AlphaEvolve-style systems run long automated experiments;
    optional retrieval, guidance, critique, or training-data components need
    attributable failures so they do not masquerade as candidate or evaluator
    failures.
  - Current evidence: built-in plugins are explicitly paper-limited, but the
    loop calls plugin hooks directly. A local proof with a plugin whose
    `build_extra_context()` raises `RuntimeError("plugin context failed")`
    aborts `evolve()` before mutation/evaluation logging. `DeepResearchPlugin`
    handles its own provider exceptions, but there is no general hook-level
    failure record for custom or future paper-inspired plugins.
  - Required result: define whether plugin hook failures are ignored,
    quarantined, penalized, or fatal per hook; persist plugin name/hook/error
    provenance; and avoid presenting optional paper-inspired plugins as robust
    run components until that policy exists.

- [ ] Clarify DeepEvolve paper-index wording around cross-file editing.
  - Paper-index evidence: `papers/README.md` says the DeepEvolve-inspired
    status has "no ranking provenance, full payloads, cross-file editing, or
    systematic debugging loop."
  - Current evidence: the core candidate system now supports multi-file
    workspace mutations, including edits, creates, deletes, moves, and
    primary-file reassignment. What remains missing is DeepEvolve-specific
    cross-file editing as part of a retrieval/debug/hypothesis loop, not
    platform-level cross-file mutation support.
  - Required result: update `papers/README.md` so the DeepEvolve row says
    "no DeepEvolve-style cross-file debugging/editing loop" or equivalent,
    avoiding a contradiction with current workspace-candidate support.

- [ ] Keep ImprovEvolve-inspired behavior explicitly paper-limited or implement
  the actual generate/improve/perturb parameterization and search dynamics.
  - Paper evidence: `2602.10233__ImprovEvolve.pdf` evolves a class/interface
    with `generate_config`, `improve`, and `perturb`, then approaches optima by
    scheduled basin-hopping-style application of `improve()` and `perturb()`.
  - Current evidence: the CLI alias is paper-neutral (`modular`) and docs label
    it ImprovEvolve-inspired, but `libreevolve/plugins/modular.py` injects a
    static prompt block asking for those method names. Candidate metadata now
    records that the plugin supplied rendered prompt context, including text,
    hash, parent id, and inspiration ids, but no generate/improve/perturb
    operation is selected or executed.
  - Missing: enforced interface, evaluator support for the interface,
    iterative improve/perturb execution, perturbation-intensity scheduling,
    operation attribution/provenance beyond static context attribution, and
    benchmark-specific search loop.

- [ ] Keep ThetaEvolve-inspired behavior explicitly paper-limited or implement
  batch sampling, dynamic RL training, and reward shaping.
  - Paper evidence: `2511.23473__ThetaEvolve.pdf` describes a single-LLM
    framework with a large program database, batch sampling, lazy penalties,
    optional reward shaping, and reinforcement learning at test time.
  - Current evidence: the CLI alias is paper-neutral (`ttt_rl`) and docs label
    it ThetaEvolve-inspired, but `libreevolve/plugins/ttt_rl.py` writes JSONL
    and does not train. It exports prompt, response, raw score, clipped reward,
    and reward policy. CLI-loaded runs scope the dataset under
    `plugin_artifacts/ttt_rl/` and link counts/path/hash metadata from the
    manifest.
  - Missing: batch prompt sampling, lazy/stagnation penalties, reward shaping,
    online GRPO/RL training loop, dynamic environment integration, resume
    semantics, and training checkpoint management.

- [ ] Tighten or remove GigaEvo-derived implementation claims.
  - Paper evidence: `2511.17592__GigaEvo.pdf` describes Redis-backed
    evolutionary units with lifecycle state, optimistic concurrency, an
    asyncio DAG execution engine, configurable stages, insights, bidirectional
    lineage, and rewrite/diff mutation modes.
  - Current evidence: comments cite append-only JSONL lineage and multi-island
    exchange, but `ProgramDatabase` is a thin JSONL facade and `IslandModel` is
    synchronous.
  - Missing: persistent concurrent database, lifecycle states, async DAG
    stages, bidirectional lineage, insight generation, and rewrite mutation
    mode.

- [ ] Tighten or remove CodeEvolve-derived implementation claims.
  - Paper evidence: `2510.14150__CodeEvolve.pdf` combines islands-based
    genetic search with modular LLM orchestration, execution feedback,
    context-aware recombination, adaptive meta-prompting, and targeted
    refinement.
  - Current evidence: `IslandModel` has no crossover/recombination, no adaptive
    meta-prompting, and no targeted refinement stage.
  - Missing: recombination/crossover, modular orchestration, adaptive
    meta-prompts, targeted refinement, and cost/performance ablation support.

- [ ] Decide whether MadEvolve-inspired features are in scope.
  - Paper evidence: `2602.15951__MadEvolve.pdf` emphasizes free parameters,
    parameter optimization, hybrid population management, LLM ensemble
    strategies, and automated report generation comparing input and evolved
    algorithms.
  - Current evidence: README cites MadEvolve as domain-specific evolution, but
    there is no parameter tracking/optimization layer or generated innovation
    report.
  - Missing: free-parameter extraction, gradient or gradient-free parameter
    optimization, algorithm comparison report, and parameter-function summary.

- [ ] Implement MAP-Elites behavior descriptors beyond the fixed local
  primary-file archive.
  - Paper evidence: `1504.04909__MAP_Elites.pdf` maps elites over
    user-chosen dimensions of variation to illuminate high-performing
    solutions across a behavior space.
  - Current evidence: `MAPElites` hard-codes performance, code length, and
    TF-IDF char-4gram diversity as dimensions. For multi-file candidates, code
    length and diversity are computed from `Program.code`, the primary-file
    compatibility view, not the full candidate workspace. Complexity
    normalization updates its maximum length while candidates are inserted, and
    TF-IDF diversity is recomputed against the current capped elite list, so
    descriptor coordinates are history-dependent and existing cells are not
    re-binned when normalization reference state changes.
  - Missing: user-configurable behavior descriptors, phenotype/behavior
    descriptors from evaluator metadata, workspace-aware descriptors, stable
    descriptor normalization or explicit rebinning, and diagnostics that show
    the illuminated search space rather than only best/archive cells.

- [x] Document the MAP-Elites boundary as fixed local quality-diversity search.
  - Paper evidence: canonical MAP-Elites illuminates a behavior space chosen
    for the problem domain.
  - Current evidence: `MAPElites`'s docstring, README, architecture docs,
    roadmap, code todo, and paper index describe LibreEvolve's archive as a
    fixed local 3D heuristic over normalized performance, primary-file code
    length, and primary-file TF-IDF diversity, not a canonical
    problem-defined behavior-descriptor implementation.
  - Required result: keep the documentation boundary explicit while the
    remaining descriptor implementation work stays open.

- [ ] Bound and normalize the UCB-style backend reward policy, or adjust it
  toward canonical UCB1.
  - Paper evidence: the UCB1 paper assumes bounded reward distributions and
    analyzes regret using empirical rewards plus an upper-confidence term.
  - Current evidence: `LLMEnsemble` records non-negative fitness deltas, does
    not normalize rewards to a bounded interval, uses a configurable coefficient
    rather than the canonical constant, and increments `total` before
    selection. The reward API does not enforce even the local non-negative
    finite contract: a local proof called `record_reward()` with `nan`, `inf`,
    and `-5.0`, and those values were stored in scheduler `wins` before later
    generation continued.
  - Missing: reward validation, reward normalization, explicit
    initialization/pull-once policy, documented coefficient choice, invalid
    reward diagnostics, and tests that the implementation matches the intended
    UCB variant.

- [x] Document the UCB1 boundary as heuristic rather than canonical.
  - Paper evidence: the UCB1 paper provides regret analysis under assumptions
    that LibreEvolve's backend router does not currently satisfy.
  - Current evidence: `LLMEnsemble`'s docstring, `docs/backends.md`,
    `README.md`, and `papers/README.md` all describe the backend router as a
    UCB-style heuristic or inspiration over observed fitness improvements, not
    a canonical regret-analyzed UCB1 implementation.
  - Required result: keep the documentation boundary explicit while the
    remaining canonicalization work stays open under the bounded-reward policy
    todo.

- [ ] Account for non-mutation LLM calls in ensemble scheduling.
  - Paper evidence: AlphaEvolve uses an ensemble of LLMs to balance candidate
    generation throughput and quality.
  - Current evidence: critique, feedback, and meta-prompt calls share the same
    `LLMEnsemble.generate()` accounting as mutation calls, but only mutation
    calls receive a candidate-improvement reward. Call telemetry now records
    roles and is persisted in candidate/feedback/prompt metadata for successful
    synchronous calls.
  - Missing: role-specific routing/accounting for generation, critique,
    grading, and meta-prompt calls, persisted resumable scheduler state, a
    separate run-scoped call log, provider token/usage fields, and retry/fallback
    policy.

- [ ] Enforce boolean config switches for paper-inspired optional LLM paths.
  - Paper evidence: AlphaEvolve-style critique, feedback, and meta-prompt
    components are explicit configured system behaviors, not accidental truthy
    string branches.
  - Current evidence: `Config.validate()` accepts
    `meta_prompt_evolution="false"` and `critique_enabled="false"` as strings.
    Because both fields are used in truth checks in `evolve()`, malformed YAML
    or programmatic config can enable meta-prompt mutation or critique despite
    looking disabled.
  - Missing: boolean validation tests for critique/meta-prompt switches across
    direct `Config` construction and problem-local `config.yaml`, plus updated
    docs that stop implying broad config validation covers these paper-inspired
    optional LLM paths.

- [x] Tighten inline paper-source comments so they do not imply faithful
  implementations.
  - Evidence: source comments in the diff engine, evaluator, loop, database,
    island model, MAP-Elites, and modular plugin cited paper systems in ways
    that could be read as direct implementations.
  - Status: inline comments now use "inspired by" language or state the local
    limitation directly; the larger implementation gaps remain tracked in the
    paper-specific items above.
  - Required result: keep code comments aligned with the actual behavior, not
    just README/docs marketing language.

- [ ] Re-audit backend-selection source comments for MadEvolve implication.
  - Paper evidence: `2602.15951__MadEvolve.pdf` is tracked as domain evolution
    inspiration, while LibreEvolve has no free-parameter optimization,
    innovation report, or MadEvolve-style parameter-function summary.
  - Current evidence: `libreevolve/llm/ensemble.py` still says the UCB-style
    router is "applied to LLM selection per MadEvolve", even though README,
    docs, and the paper index describe the router as a heuristic
    AlphaEvolve/MadEvolve-adjacent scheduling concept rather than a faithful
    MadEvolve implementation.
  - Required result: either rewrite that source comment to "inspired by" /
    "adjacent to" wording, or implement and document the specific MadEvolve
    behavior being claimed.
