# Papers Todo: Reference and Specification Gaps

This list tracks mismatches discovered while reviewing the local `papers/`
directory and using the AlphaEvolve paper as the primary specification.

## AlphaEvolve Paper Requirements Not Yet Implemented

- [ ] Add paper-facing evaluator-metric evidence separate from local
      `is_valid` admission policy.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and Figure 3.
  - Requirement: AlphaEvolve's evaluator maps a solution to scalar metrics,
    metrics are maximized by convention, and the paper's Python example
    returns `dict[str, float]`.
  - Partial status: LibreEvolve validates structured evaluator results,
    requires all declared scalar metrics, reserves boolean `is_valid` outside
    `metrics.yaml`, stores non-scalar `outputs`/`program_output` attachments
    separately, and normalizes declared metric directions/bounds for local
    archive scoring.
  - Current gap: benchmark and paper-result reports do not yet include an
    explicit AlphaEvolve-facing metric contract proving which returned fields
    are scored scalar objectives, how local minimize metrics are transformed
    into maximized paper metrics, and that `is_valid` is only an admission
    gate rather than a reported optimization metric.
  - Required result: add paper-metric report fields and validators for
    `paper_metric_names`, validity-gate source, raw and maximized score
    columns, excluded local-control fields, and claim readiness before
    treating LibreEvolve evaluator outputs as AlphaEvolve-comparable metric
    evidence.

- [ ] Track independent evaluator-oracle composition evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` states that AlphaEvolve
    iteratively improves algorithms by continuously receiving feedback from one
    or more evaluators, then Section 2.4 distinguishes the user-provided
    evaluation function from optional cascades and LLM-generated feedback.
  - Current gap: paper/status records can show one local cascade validator,
    configured stages/samples, and optional LLM feedback graders. They do not
    preserve paper-facing evidence for multiple independent evaluator/oracle
    sources, evaluator authority, metric ownership, merge/conflict rules, or
    how evaluator disagreements affect validity, score reporting, database
    admission, and prompt-visible feedback.
  - Required result: add paper-facing evaluator-composition records before
    claiming AlphaEvolve-style "one or more evaluators" feedback: evaluator
    ids, oracle type, task authority, input/output schema, metric ownership,
    merge/conflict policy, failure handling, prompt-feedback linkage, and
    wording that separates independent evaluator composition from local
    cascade stages or post-evaluation LLM graders.

- [ ] Track execution-grounded filtering of incorrect base-LLM suggestions.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Introduction and Table 1 context.
  - Requirement: AlphaEvolve says code execution and automatic evaluation
    ground the LLM-directed evolution process, allowing the system to avoid
    incorrect suggestions from the base LLM and use feedback to move beyond
    the initial candidate pool.
  - Partial status: LibreEvolve records structured evaluator results,
    malformed-output failures, rejected candidates, admission decisions,
    quarantine streams, and prompt-visible diagnostics for bounded recent
    failures.
  - Current gap: paper-facing reports do not yet connect each generated LLM
    suggestion through parsing, execution, evaluator judgment, validity,
    admission, retention, rejection reason, and subsequent feedback reuse.
    Current validity/admission logs are useful local mechanics, but they do
    not by themselves prove the AlphaEvolve claim that automatic evaluation
    filtered incorrect base-model suggestions before accepted discoveries were
    reported.
  - Required result: add paper/report evidence for proposal lifecycle
    filtering: backend/model id, suggestion/proposal id, mutation payload hash,
    execution/evaluator outcome, validity/admission/retention status,
    rejection reason taxonomy, evaluator-oracle sufficiency for the benchmark,
    prompt feedback or failure-memory linkage, aggregate false-acceptance/
    false-rejection review fields, and claim-readiness checks before describing
    LibreEvolve as AlphaEvolve-style grounded against incorrect base-LLM
    suggestions.

- [ ] Track hypothesis backtracking and abandoned-branch evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Introduction and Section 2.4.
  - Requirement: AlphaEvolve frames scientific/program discovery as ideation,
    exploration, backtracking on unpromising hypotheses, experimentation, and
    validation, with cascades pruning less-promising solutions before larger
    budget is spent.
  - Partial status: LibreEvolve records candidate failures, evaluator
    rejections, admission outcomes, quarantine streams, proposal
    `idea`/`rationale`/`hypothesis` metadata, bounded failure-memory snippets,
    and run-local hypothesis summaries for valid programs.
  - Current gap: paper-facing reports do not identify a proposal/hypothesis
    branch, track when evidence made that branch unpromising, record a
    backtrack or abandonment decision, or show that subsequent prompt/database
    sampling redirected to an ancestor, sibling, or different idea family.
    Individual rejection logs and failure snippets are not enough to prove the
    AlphaEvolve process claim about backtracking during discovery.
  - Required result: add paper-visible hypothesis-branch reports with branch
    id, proposal/idea-family labels, candidate ids explored, evaluator/cascade
    evidence, abandonment or backtrack reason, fallback target, prompt and
    failure-memory linkage, suppression/retry policy, resumed-search outcome,
    and claim-readiness validation before using AlphaEvolve-style
    backtracking wording.

- [ ] Track candidate-embedded evaluator entrypoint parity.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and Figure 3.
  - Requirement: AlphaEvolve's example codebase contains an
    `evaluate(eval_inputs) -> dict[str, float]` function that invokes the
    evolved skeleton and returns the scores for the generated program. In the
    local PDF, page 4 describes the evaluator as a Python `evaluate` function
    with a fixed input/output signature, and Figure 3 on page 6 says the
    evaluators invoke the Figure 3(a) `evaluate` function to score the modified
    program.
  - Partial status: LibreEvolve records structured results from problem-local
    validators, validates direct evaluator entrypoint provenance, enforces
    problem-local validator dependency policy, and can import candidate modules
    from external validators.
  - Current gap: paper-facing evidence does not show candidate-owned
    `evaluate` functions, `eval_inputs` provenance, skeleton-to-evolved-block
    invocation paths, or a clear distinction between embedded AlphaEvolve-style
    evaluation and external `validate.py`-style problem validators. Current
    runtime evidence shows the subprocess runner materializes candidate files,
    imports the configured problem validator, and calls that validator's
    `evaluate(code[, workspace[, stage]])`; `_eval_metadata()` records
    `validate_path` plus candidate files, not candidate-owned callable
    provenance. A local probe with candidate `main.py` defining
    `evaluate(eval_inputs)` still followed the external `validate.py`
    invalid result and reported `validate_path=validate.py`.
  - Required result: add report fields or runtime mode proving embedded
    candidate evaluator entrypoints, eval-input datasets, callable isolation,
    callable discovery diagnostics, skeleton/block invocation evidence, and
    score-field mapping before treating local validator execution as
    AlphaEvolve Figure 3 evaluator parity.

- [ ] Parallelized evaluation and asynchronous throughput.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: expensive evaluations can be parallelized, and the whole
    pipeline runs as an async controller with LLM samplers and evaluation
    nodes. Section 2.4 also frames parallel evaluation as a way to keep
    generation feedback fast enough for several consecutive mutations rather
    than stalling evolutionary depth behind slow evaluator wall-clock time.
  - Partial status: `proposals_per_generation` can now create, evaluate,
    reward, and log multiple sequential sibling candidates inside one
    generation with per-proposal batch metadata and deterministic ids.
    Completed manifests also embed
    `libreevolve.controller_state_validation.v1` to verify the current
    controller boundary is terminal, synchronous, and drained rather than an
    async queue checkpoint.
  - Current gap: `evolve()` is still synchronous and evaluates one candidate at
    a time; there are no async LLM sampler queues, parallel evaluator nodes, or
    explicit mutation-chain-depth policy for expensive/slow-feedback
    evaluations. Sequential sibling proposal batches are accounting evidence,
    not AlphaEvolve-style throughput depth.
  - Required result: add paper-visible parallel-evaluation reports and
    validators that record per-candidate compute-hour budget, wall-clock
    duration, evaluator-worker fan-out, randomized-initialization shard
    counts/seeds, queued/running/completed evaluator-node state, cluster or
    local fallback identity, mutation-chain-depth impact, and resumed
    pending-work behavior before treating LibreEvolve's synchronous evaluator
    loop or sequential sibling batches as AlphaEvolve-style parallelized
    evaluation evidence.

- [ ] Track Figure 1/Figure 2 architecture-process exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 1 shows the
    high-level AlphaEvolve overview from human-defined problem inputs through
    LLMs, prompt sampler, evaluator pool, and program database to an improved
    solution on local PDF page 3. Figure 2 on page 4 expands the discovery
    loop with `database.sample()`, `prompt_sampler.build(...)`,
    `llm.generate(...)`, `apply_diff(...)`, `evaluator.execute(...)`, and
    `database.add(...)`.
  - Current gap: paper-facing TODOs cover individual behavior gaps for
    evaluators, prompt context, LLM scheduling, async throughput, and the
    program database. Current runtime artifacts can support a partial local
    mapping because `evolve()` samples parents, builds prompts, calls the LLM,
    applies workspace mutations, evaluates candidates, admits/logs programs,
    and writes history, archive, LLM-call, prompt-history, controller-budget,
    evaluator-artifact, and manifest records. They do not preserve the Figure
    1/Figure 2 diagrams as paper exhibits with stable figure IDs, node/edge
    mappings to LibreEvolve components, implemented/unsupported status per
    node, Figure 2 pseudocode-line mappings, source PDF page and caption
    locations, rendered diagram/text artifacts and hashes, or links from each
    displayed controller step to run artifacts and validators.
  - Required result: add paper-facing Figure 1/Figure 2 process-diagram records
    and validation: figure IDs, node/edge labels, component mappings,
    Figure 2 pseudocode-line mappings, implemented/divergent status, source and
    rendered artifact hashes, links to prompt-history, LLM-call, evaluator,
    candidate-history, database, and controller-state evidence, plus
    README/ROADMAP wording that separates local workflow diagrams from
    reproduced AlphaEvolve architecture evidence.

- [ ] Track unified task-specification provenance separately from per-field
      run metadata.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and Figure 2.
  - Requirement: AlphaEvolve's task specification is a coherent user-provided
    input bundle: initial program/components to evolve, evaluation code,
    prompt template and configuration, choice of existing or custom LLMs, and
    optional background knowledge. In the local PDF, Figure 2 on page 4 labels
    those inputs and its caption says the user provides an initial program,
    evaluation code, and optional configurations before the evolutionary loop.
  - Partial status: LibreEvolve records problem/source provenance, seed source
    rows, evaluator source hashes, backend specs, prompt variants,
    redacted/hash-backed effective config, and context-source diagnostics. The
    current startup manifest persists these across `config`, `problem`,
    `policies`, and `provenance`: prompt variants/metadata, backends and
    role-backend routes, objective schema, context sources/policy, evaluator
    sources, seed sources/policy, candidate-language policy, and source/plugin/
    environment provenance.
  - Current gap: paper-facing evidence does not yet assemble those records
    into one validated task-spec artifact with AlphaEvolve field names,
    source hashes, redaction status, field presence/omission diagnostics, and
    links from each input field to the run, prompt, evaluator, and candidate
    evidence it controls. It also does not mark which AlphaEvolve task-spec
    fields are unsupported or represented only by local divergence records such
    as the Python-primary candidate-language policy.
  - Required result: add paper-facing task-spec bundle records with input-field
    ids for initial code/workspace, evolvable spans, evaluator code,
    prompt-template/config, LLM choices, and optional background knowledge;
    include source hashes/redaction, unsupported/missing-field diagnostics,
    artifact cross-links, validation that each id resolves to current manifest
    evidence, and README/ROADMAP wording that separates a coherent
    AlphaEvolve task-spec artifact from scattered local manifest provenance.

- [ ] Independent per-role LLM scheduler state and reward policy.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: AlphaEvolve-style model orchestration should be able to
    schedule proposal generation, critique, feedback, and prompt-improvement
    calls as distinct work classes with separately auditable budgets, reward
    semantics, and model-selection behavior.
  - Partial status: LibreEvolve now has configured role-backend indices,
    backend-metadata role matching, configured reward-accounted roles,
    per-role logical call limits, role-scoped provider/token/configured-cost/
    latency budget maps, feedback reward wiring for exact configured feedback
    roles, scheduler-policy telemetry, and restorable per-role scheduler audit
    records.
  - Current gap: the live selection state is still the shared ensemble bandit;
    role routing only narrows eligible backend indices, and
    `role_scheduler_state` is audit/restore evidence rather than independent
    per-role scheduler ownership with calibrated rewards and quotas.
  - Required result: add independent per-role scheduler policies for mutation,
    critique, feedback, and meta-prompt calls, plus restore validation and
    experiment reports proving role-specific selection and budget behavior.

- [ ] Validate fast/strong model-mix scheduling beyond local metadata tests.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4, "Models used".
  - Requirement: AlphaEvolve's LLM ensemble mixes Gemini Flash for low-latency,
    high-volume candidate generation with Gemini Pro for occasional stronger
    suggestions that can advance search depth. A faithful implementation needs
    evidence for that throughput/quality tradeoff under a fixed compute
    budget, not only a generic list of interchangeable backends.
  - Partial status: `LLMEnsemble` supports multiple providers, backend
    metadata, role-backend eligibility, UCB-style selection, and a
    `throughput_depth` strategy with focused metadata/unit coverage for
    normalized depth/cost/latency contribution and breadth/depth role labels.
  - Current gap: there is no runtime scheduler policy or experiment report
    proving a reserved fast-breadth lane plus occasional strong-depth lane,
    no equal-budget comparison against single-model or generic UCB routing,
    and no paper-level evidence that the configured mix increases evaluated
    idea volume while preserving breakthrough-quality proposals.
  - Required result: add scheduler-validation fixtures and reports that record
    model lane roles, selection traces, consumed budget, candidate throughput,
    quality/depth outcomes, and equal-budget comparisons for fast/strong
    model mixes before treating LibreEvolve's ensemble as AlphaEvolve-style
    Flash/Pro scheduling evidence.

- [ ] Track Google/Gemini provider-parity evidence separately from generic
      custom-backend extensibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4, "Models used".
  - Requirement: the concrete AlphaEvolve implementation used Gemini 2.0 Flash
    and Gemini 2.0 Pro. Paper-facing provider parity therefore needs a
    self-describing Google/Gemini provider surface, or an explicit substitute
    policy, not only a generic custom backend slot.
  - Partial status: LibreEvolve has built-in OpenAI, Anthropic, and Ollama
    adapters, configured custom import-path backends, role-backend eligibility,
    provider usage/default telemetry for supported adapters, and backend
    metadata that can label breadth/depth behavior.
  - Current gap: a custom backend can wrap Gemini externally, but the paper
    ledger has no first-class evidence for Gemini credential preflight,
    provider-native usage/default/capability telemetry, safe provider
    diagnostics, model-family labels, Flash/Pro lane identity, or an explicit
    paper-level substitution rule that keeps Gemini absence distinct from
    fast/strong scheduling experiments.
  - Required result: add a built-in Google/Gemini adapter or versioned
    provider-plugin/substitution contract with model-family capability
    metadata, credential/client preflight, request/usage/default telemetry,
    diagnostic retention policy, and report fields proving whether a run
    reproduced or intentionally substituted AlphaEvolve's Flash/Pro provider
    mix before claiming provider-parity evidence.

- [ ] Track AlphaEvolve sample-efficiency evidence separately from call caps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 4.
  - Requirement: AlphaEvolve contrasts FunSearch-scale millions of LLM samples
    with AlphaEvolve-style thousands of samples that benefit from SOTA LLMs.
    Paper-facing reproduction claims need evidence for useful search progress
    under bounded candidate counts, not only configurable LLM call limits or
    provider budget telemetry.
  - Partial status: LibreEvolve records logical LLM calls, provider attempts,
    provider-reported token totals, configured estimated cost, latency,
    generated candidate ids, sequential sibling proposal batches, and
    equal-budget ablation report shapes.
  - Current gap: no benchmark report ties final score or target attainment to
    the number of generated/evaluated LLM proposals, compares thousands-scale
    runs against much larger or smaller sample budgets, or separates
    sample-efficiency gains from generic budget stopping, fast/strong routing,
    and the `Small base LLM only` ablation label.
  - Required result: add sample-efficiency report fields and validation for
    generated proposals, evaluated candidates, admitted candidates, retained
    elites, LLM-call/sample budgets, target attainment versus sample count,
    and equal-budget model-size comparisons before claiming AlphaEvolve-style
    "thousands of samples suffice" behavior.

- [ ] Track repeated-sampling baselines for test-time-compute uplift claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Discussion.
  - Requirement: AlphaEvolve is described as a test-time-compute agent that
    enhances base-LLM capability compared with repeated sampling by using
    machine feedback inside an evolutionary loop.
  - Partial status: LibreEvolve has LLM budget telemetry, generated candidate
    ids, admission/failure records, equal-budget ablation report schemas, and a
    `No evolution` ablation variant label.
  - Current gap: paper-facing reports do not define an equal-budget repeated
    base-model sampling comparator with fixed prompt/model/seed/evaluator
    conditions, generated/evaluated sample counts, disabled archive feedback,
    disabled parent/inspiration resurfacing, disabled meta-prompt updates, and
    target-progress curves linked to the matching evolutionary run.
  - Required result: add repeated-sampling baseline report fields and
    validation for controlled base-model sampling runs, sample counts,
    validity/admission outcomes, target attainment, budget parity, and links
    to evolutionary comparator runs before claiming AlphaEvolve-style
    test-time-compute uplift over repeated sampling.

- [ ] Track Google/Gemini provider parity separately from generic backend
      configurability.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3/2.4, "Models used".
  - Requirement: the published AlphaEvolve ensemble used Gemini 2.0 Flash and
    Gemini 2.0 Pro; a reproduction-oriented implementation should either
    provide a first-class Google/Gemini backend surface or explicitly document
    an equivalent substitute with comparable capability and telemetry evidence.
  - Partial status: LibreEvolve supports multiple built-in providers through
    OpenAI, Anthropic, and Ollama, plus custom backend class paths.
  - Current gap: no built-in Google/Gemini backend exists, and `custom`
    backends do not by themselves supply provider-native usage/default
    telemetry, account/model capability evidence, credential preflight, or
    Flash/Pro lane labels for scheduler-validation reports.
  - Required result: add a Gemini backend or provider-plugin contract with
    safe request metadata, usage/default diagnostics, model-family capability
    policy, credential/client preflight, and paper-facing evidence that the
    fast/strong model mix is reproduced or intentionally substituted.

- [ ] Add AlphaEvolve-grade candidate language, build, and runner contracts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.2.
  - Requirement: tasks define the program artifact and evaluator interface; a
    faithful system should be able to operate on codebases and task-specific
    solution representations rather than only one Python-primary workspace
    shape.
  - Partial status: startup manifests now include
    `libreevolve.candidate_language_policy.v1`, declaring the current
    `python_primary_text_workspace_v1` boundary, bounded UTF-8 workspace plus
    typed static members, fail-closed non-Python marker handling, Python
    subprocess validator runner, and unsupported arbitrary-language,
    build-system, and problem-defined solution-abstraction surfaces.
    `validate_candidate_language_policy()` rejects overclaims that those
    surfaces are ready.
  - Current gap: this is an honest boundary record, not non-Python or
    arbitrary-codebase support. There are no configured language runners,
    build-system contracts, language-aware marker grammars, or task-defined
    candidate abstraction hooks.

- [ ] Track existing-codebase minimal-marker integration evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.1 says the input
    API facilitates integration with existing codebases while requiring only
    minimal changes, simply by adding special markers as comments into the
    code. In the local PDF, this appears on page 4; Figure 3 on page 6 shows
    the marked blocks together with the special `evaluate(eval_inputs) ->
    dict[str, float]` function that the evaluators invoke.
  - Current gap: paper/status records can show Python evolve-block marker
    parsing, unsupported non-Python marker diagnostics, workspace
    materialization, seed workspace source paths, static-file hashes, and
    candidate-language boundaries. They do not preserve evidence that a real
    pre-existing codebase was integrated with a marker-only or minimal setup
    diff, that non-evolved skeleton code remained unchanged across an upstream
    tree, that evaluator invocation still worked through the existing codebase
    structure, or that copied static assets have portable source-root/release
    identities.
  - Required result: add paper-facing integration records with original
    codebase id, pre-marker source hashes, marker-added diff summary,
    evolved-block span ids, skeleton-preservation hashes, language/comment
    syntax, evaluator invocation path, setup-change counts, and wording that
    distinguishes evolve-block parser support and local workspace smoke tests
    from AlphaEvolve-style minimal-change integration evidence.

- [ ] Track Figure 3 evolve-block marker spelling source variants.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.1 names the marker
    comments as `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END` on local PDF
    page 4, while PDF text extraction from Figure 3(a) on page 6 shows one
    opening marker as `# EVOLVE-BLOCK START` and another as
    `# EVOLVE-BLOCK-START`.
  - Current gap: paper/status records can cite local Python marker validation
    and unsupported marker diagnostics, and the Figure 3 exhibit TODOs require
    exact excerpt artifacts. They do not require a paper-facing classification
    of the marker-text variant before docs decide whether it is canonical
    paper prose, rendered figure text, extraction/OCR uncertainty, or a paper
    typo. They also do not record the current parser fact that the space
    variant is unsupported and paired `# EVOLVE-BLOCK-END` makes it fail as
    `orphan_end`.
  - Required result: add paper-facing source-location records for each marker
    spelling, attach source artifact hashes or screenshots, classify the
    discrepancy, capture the implemented parser/compatibility decision, and
    keep documentation claims scoped so local parser grammar is not mistaken
    for full reproduction of every Figure 3 marker rendering.

- [ ] Track candidate-abstraction choice and bias evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and Discussion.
  - Requirement: AlphaEvolve treats the candidate representation as a
    problem-dependent choice: direct solution search, constructor functions,
    bespoke search algorithms, or co-evolved intermediate solution/search
    pairs. The paper says these choices carry different biases, including
    constructor functions being advantageous for highly symmetric solutions and
    customized search algorithms for non-symmetric solutions. In the local PDF,
    page 5 describes flexibility in choosing the abstraction and page 21 says
    direct search, constructor functions, and search algorithms come with
    different biases.
  - Partial status: the papers index and README state that LibreEvolve's
    current boundary is a Python-primary code-file-set abstraction and that
    flexible non-code or paired solution/search abstractions are unsupported.
    Current manifests record this through
    `libreevolve.candidate_language_policy.v1`: `python_primary_text_workspace_v1`,
    bounded UTF-8 text workspace plus typed static members, primary language
    `python`, `problem_defined_solution_abstractions: unsupported`, and
    `language_runner_ready: False`.
  - Current gap: no paper-facing report records abstraction choice, problem
    structure rationale, symmetry assumptions, or equal-budget comparisons
    across direct-solution, constructor-function, and search-algorithm
    formulations. It also does not record unsupported alternative abstraction
    diagnostics as part of a benchmark claim-readiness check.
  - Required result: add benchmark/report metadata for candidate abstraction
    family, rationale, expected problem bias, serializer/runner contract,
    unsupported alternatives, paired solution/search linkage, and comparable
    results for alternative abstractions before claiming AlphaEvolve-style
    abstraction-selection evidence.

- [ ] Track explicit-context source roles for prompt sampling.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 lists explicit
    prompt context as fixed human-written instructions, equations, code
    snippets, and relevant literature such as PDF files.
  - Current gap: paper/status records and prompt diagnostics can show which
    local files were selected, hashed, extracted, truncated, ranked, or omitted
    before prompt rendering. They do not preserve a paper-facing role for each
    explicit-context source, so docs could conflate generic local file
    ingestion, background retrieval, plugin context, and task-specific
    problem-formulation evidence.
  - Required result: add paper-facing explicit-context records with source
    role, problem/topic linkage, source location, prompt-inclusion/omission
    status, content hash/redaction policy, and wording that distinguishes
    AlphaEvolve-style typed problem context from generic context-file loading
    or retrieval-augmented background evidence.

- [ ] Track primary-prompt instruction and target-solution evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 says the
    primary prompt includes previously discovered solutions sampled from the
    program database and system instructions for proposing changes to a
    particular solution.
  - Current gap: paper/status records can show prompt ids, template hashes,
    selected parent/inspiration ids, prompt-context policy, and prompt-size
    diagnostics. They do not preserve a paper-facing prompt-core record that
    identifies the current target solution, the role of each sampled prior
    solution, the instruction block/version/hash used for that target, whether
    that instruction was delivered through provider system/developer/user role
    messages or through a serialized single prompt, or required-channel
    presence/omission status.
  - Required result: add paper-facing prompt ingredient records with prompt
    call id, target program/source hash, sampled solution roles, instruction
    policy id, instruction text hash/redaction policy, provider message-role
    placement, edit-scope or mutation mode constraints, required-channel
    diagnostics, prompt-history linkage, and wording that separates
    AlphaEvolve-style target-specific prompt instructions from generic
    prompt-template compatibility.

- [ ] Track stochastic prompt-format probability provenance.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 says stochastic
    formatting uses template placeholders with human-provided alternatives for
    increased diversity, instantiated using probability distributions from a
    separate config file.
  - Partial status: LibreEvolve supports weighted `[[prompt:name]]` markers,
    validates `prompt_format_options`, samples alternatives with the run-local
    RNG, records selection index/weight/source/text hash in prompt
    diagnostics, and persists redacted prompt-option values plus metadata in
    the startup manifest.
  - Current gap: paper/status records do not yet preserve the full
    probability distribution used for each marker, the option-set source
    identity and hash, whether it came from a separate config file or the
    effective inline run config, the selected alternative per prompt/call, or
    validation that stochastic formatting provided human-authored prompt
    diversity rather than opaque template mutation.
  - Required result: add paper-facing stochastic-format records with prompt
    id/call id, marker name, option set id, config source/path/hash or explicit
    inline-source boundary, alternative indexes and normalized probabilities,
    selected alternative hash/index, weight override source, RNG/replay
    boundary, and claim checks before treating local `prompt_format_options`
    as AlphaEvolve-style stochastic-formatting evidence.

- [ ] Track prompt-visible prior-score provenance for rendered evaluation
      results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 says rendered
    evaluation results contain the program, execution result, and scores
    assigned by `evaluate`; Figure 3(c) shows previously discovered programs
    with named metric scores and an `average_score` before the program text.
  - Partial status: LibreEvolve renders current-parent metrics and inspiration
    fitness/metric summaries in mutation prompts, including declared metric
    role, direction, bounds, normalization, and range diagnostics where a
    problem manifest defines them.
  - Current gap: paper/status records do not yet preserve a prompt-call-linked
    score-summary record proving that each prompt-visible prior/current
    program's displayed metric values and aggregate fitness came from the
    persisted evaluator result, how the displayed aggregate maps to the paper's
    score-summary semantics, or why any execution result or score field was
    omitted/truncated.
  - Required result: add paper-facing rendered-evaluation-result score records
    with prompt id/call id, program role, candidate/history id, source hash,
    raw and normalized metric values, aggregate formula/display label,
    evaluator output/artifact linkage, omission/truncation policy, and claim
    checks before treating prompt metric headers as AlphaEvolve-style rendered
    evaluation-result evidence.

- [ ] Track early-user and collaborator feedback provenance as paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Acknowledgements thank early
    users and collaborators for diverse use cases and insightful feedback,
    stating that this feedback shaped AlphaEvolve into a more robust and
    versatile tool. This is a broad external-feedback and system-shaping claim,
    separate from AlphaEvolve's machine feedback/evaluator loop.
  - Current gap: paper/status records track local problem/source provenance,
    expert mathematical formulation gaps, application owner/reviewer gaps, and
    benchmark/report artifacts. They do not preserve a feedback-provenance
    layer for early users or collaborators: use-case family, contributor role,
    feedback event/source, affected system surface, resulting change,
    validation evidence, privacy/redaction policy, or linkage from feedback to
    robustness and versatility claims. Current paper-facing implementation
    notes can describe LLM-grader feedback retention, feedback indexes,
    feedback-sourced metrics, and calibration-report contracts; those are
    search/evaluation telemetry, not evidence that external collaborator
    feedback shaped the system.
  - Required result: add paper-facing use-case feedback records with safe
    cohort/role labels, feedback event IDs, use-case taxonomy, affected
    workflow and artifact links, change/result validation, privacy/redaction
    metadata, and README/ROADMAP wording that separates documented local
    breadth from AlphaEvolve-style broad collaborator-feedback evidence.

- [ ] Track acknowledgement-role evidence for review, support, and practical
      application management advice.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Acknowledgements separately
    thank contributors for reviewing the white paper, early explorations and
    insightful discussions, support and advice, helpful advice on managing the
    practical applications, and reviewing application-specific work. Local PDF
    extraction places the general paper-process acknowledgement text on page 21
    and additional application-specific advice/review acknowledgement text on
    page 22.
  - Current gap: paper/status records track early-user feedback, expert
    formulation, application owner/reviewer roles, and core contribution
    provenance. They do not preserve acknowledgement-role records for these
    paper-process and governance contributions, so docs could conflate paper
    review/support/advice with implementation authorship, benchmark
    formulation, publication-author metadata, domain validation, or deployment
    signoff. Existing package/project metadata and technical provenance records
    also do not establish acknowledgement-process roles.
  - Required result: add paper-facing acknowledgement records with safe
    contributor labels, role category, affected white-paper or application
    scope, source page/section, privacy/redaction policy, and README/ROADMAP
    wording that distinguishes acknowledgement-process evidence from technical
    validation, benchmark formulation, deployment, publication-author metadata,
    and system-development provenance.

- [ ] Track paper author-metadata evidence for equal contributors and
      correspondence roles.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Author information says a
    named group contributed equally, the Contributions section identifies the
    people who wrote the paper and contributors who supplied input, and the
    Author information section lists corresponding authors. Page 1 defines the
    equal-contribution marker, page 22 begins Author information and
    Contributions, and page 23 lists corresponding authors.
  - Current gap: paper/status TODOs track system-development contribution
    roles, figure/Colab creator roles, and acknowledgement review/support
    roles. They do not preserve publication-author metadata for equal
    contribution, manuscript writing, paper input, or correspondence. A paper
    provenance report could therefore conflate author metadata with technical
    implementation, artifact creation, title-page affiliation, package/project
    metadata, review, or domain-validation roles.
  - Required result: add paper-facing author-metadata records with safe
    contributor labels, role category, source page/section, title-page marker
    linkage, publication or artifact scope, contact/privacy redaction policy,
    and README/ROADMAP wording that distinguishes publication-author metadata
    from technical system provenance, figure/notebook artifact authorship,
    title-page affiliation, package metadata, and acknowledgement roles.

- [ ] Track AlphaEvolve title-page affiliation and footnote evidence.
  - Paper evidence: page 1 of `2506.13131__AlphaEvolve.pdf` lists the authors,
    then gives the source affiliation line `Google DeepMind1`. The page also
    defines footnote `1` as `See Acknowledgments and Author information
    section.` and `*` as `Equal contributions.` The same page includes
    `© 2025 Google DeepMind. All rights reserved`, which must be linked as
    source-rights evidence rather than treated as local project licensing.
  - Current gap: paper/status TODOs track publication-author metadata,
    contribution roles, acknowledgement roles, and source-PDF version/rights
    metadata. They do not preserve title-page affiliation or footnote
    provenance: organization/affiliation text, marker ids, source page,
    author-to-marker mapping, or the boundary between paper-source affiliation
    and LibreEvolve's independent/non-endorsed project status. Manifest checks
    prove local PDF presence, hash, and readability; they do not extract or
    validate title-page organization, marker definitions, or affiliation
    semantics.
  - Required result: add paper-facing title-page metadata records with
    affiliation/organization text, marker ids, footnote text, source page/span,
    author-to-marker mapping for equal-contribution markers, source-rights
    linkage, privacy/redaction handling, and README/ROADMAP/papers wording that
    distinguishes source-paper affiliation evidence from local project
    affiliation, endorsement, publication-author metadata, source-rights
    metadata, and technical system provenance.

- [ ] Track core AlphaEvolve system-development contribution provenance.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Contributions says the
    initial version of AlphaEvolve was designed and implemented by specific
    contributors; project vision and problem scoping, first benchmark problem
    for iterating on AlphaEvolve, final version development, infrastructure
    maintenance, code reviews, team coordination, and research-program
    supervision are all separately attributed. Local PDF page 22 contains the
    implementation, scoping, first-benchmark, final-system, and infrastructure
    categories; page 23 contains code-review, team-coordination, and
    supervision categories.
  - Current gap: paper/status records preserve selected application owner
    roles, figure/Colab artifact roles, early-user feedback gaps, and general
    source/build provenance. They do not preserve paper-facing provenance for
    core system-development phases or responsible roles, so local docs cannot
    distinguish implementation authorship, infrastructure maintenance,
    benchmark-iteration ownership, review responsibility, and coordination
    claims from generic repository history, package authors/maintainers, or
    source-control metadata.
  - Required result: add paper-facing contribution records for core
    AlphaEvolve-style system development: role label, responsible person/team
    label where safe, development phase, artifact/module/report linkage,
    source page/section, review or approval scope, and README/ROADMAP wording
    that separates local contributor history, package metadata, and source
    hashes from paper-attributed system-development provenance.

- [ ] Add replayable evaluator environment, package-source, and accelerator
  provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.4, 2.6, and 4.
  - Requirement: AlphaEvolve-style evaluator results should be attributable to
    a reproducible runtime environment, including build execution, package
    source resolution, accelerator/runtime state, and budget-accounting
    evidence for hardware-backed or distributed evaluation.
  - Partial status: LibreEvolve manifests record selected project/build
    metadata, declared dependency and installed-distribution snapshots,
    bounded `WHEEL`/`direct_url.json`/`INSTALLER`/`RECORD` evidence,
    known-lockfile hashes, bounded/redacted `pip freeze` and `pip config`
    snapshots, NumPy config hashes, provider SDK versions, and bounded
    accelerator environment/driver probe hints. The
    `environment_reproducibility_policy` is explicitly audit-only and lists
    unsupported complete install-source interpretation, broader non-project
    build provenance, private package-source identity/authentication
    resolution, remote package artifact verification, live provider
    service/default capture, and accelerator budget/accounting semantics.
  - Current gap: these records do not form a replayable environment contract:
    external build commands/options/environment, non-project build metadata,
    transitive package-source resolution, private-index policy, remote package
    artifact hashes, accelerator lease/accounting state, and restore/check
    validation remain absent.
  - Required result: add versioned external-build/package-source/accelerator
    provenance schemas plus restore/check validators and paper-facing evidence
    that clearly separates bounded audit hints from reproducible evaluator
    environment proof.

- [ ] Stable behavior descriptor models and archive rebin semantics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3 and 2.4.
  - Requirement: a quality-diversity archive should use task-meaningful
    behavior descriptors or explicitly stable descriptor models; adaptive
    descriptors need clear compatibility and rebin semantics.
  - Partial status: MAP-Elites defaults to selection score, serialized
    workspace complexity, and TF-IDF char-ngram diversity against the current
    capped elite list. `map_elites_descriptor_axes` can select normalized
    evaluator metrics, numeric evaluator metadata, or numeric candidate
    metadata as descriptor axes. Archive snapshots persist descriptor policy
    and descriptor-model records with axes, bounds, diversity reference ids,
    revision, dynamic-reference status, and explicit no-rebin policy.
  - Current gap: existing cell coordinates are insertion-time snapshots under
    a local adaptive TF-IDF novelty heuristic. There is no learned descriptor
    model, evaluator-provided descriptor contract with compatibility rules, or
    tested archive rebin engine.
  - Required result: add stable task behavior descriptor contracts or learned
    descriptor models, tested rebin/snapshot compatibility semantics, restore
    validation across descriptor revisions, and paper-facing reports that do
    not confuse insertion-time TF-IDF coordinates with AlphaEvolve-grade
    behavior descriptors.

- [ ] Keep island-count and topology claims scoped to configurable defaults.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: AlphaEvolve describes an evolutionary database inspired by
    MAP-Elites and island-based population models; paper-facing LibreEvolve
    claims should state the local island topology honestly without implying an
    unsupported fixed or paper-identical island policy.
  - Partial status: LibreEvolve's island count is configurable through
    `Config.n_islands`, defaults to five, and migration uses the configured
    island count in a synchronous ring topology. README, ROADMAP, AGENTS, and
    the `IslandModel` docstring now describe configurable island migration
    with a five-island default instead of hardcoding all claims to five
    islands.
  - Current gap: this is a truthful local topology boundary, not proof of a
    paper-identical AlphaEvolve evolutionary database. Adaptive island counts,
    non-ring topologies, topology-specific ablations, and paper-facing
    migration-policy reports remain absent.
  - Required result: if future work adds adaptive island topology or
    AlphaEvolve-specific migration policy fidelity, update the papers index,
    README, ROADMAP, and code TODO entries together so they neither underclaim
    current configurability nor overclaim fixed five-island policy.

- [ ] Tighten remaining invalid-workspace topology diagnostics for codebase-scale
  artifact failures.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.2.
  - Requirement: AlphaEvolve-style tasks mutate program artifacts under
    automated evaluator feedback; generated invalid artifacts should leave
    stable, inspectable diagnostics that can steer future proposals.
  - Partial status: typed `CandidateMaterializationError` records now cover
    materialized candidate-path collisions, linked target roots or ancestors,
    linked nested root entries, file target roots, parent/temp root creation,
    candidate text/static write failures, existing-root backup failures, final
    swap failures, backup restore failures, cleanup deletion failures, and
    static source-copy link/read/not-file/hash/byte-count failures. Evaluations
    persist `materialization_error` metadata with bounded message text plus
    structured `reason` and relevant bounded `paths`, and prompt context policy
    can select/cap those fields for failure-memory feedback. Topology sections
    are prevalidated for duplicate source/target operations, host/case-folded
    file or move-target collisions, non-empty command bodies, and primary-file
    deletion without replacement.
  - Current gap: future topology surfaces such as bulk directory operations or
    language/build-runner generated artifacts must preserve stable diagnostics,
    copied static assets still need portable source-root or release-artifact
    identity beyond local `source_copy_path` labels, and future materialization
    filesystem paths must preserve the stable reason/path diagnostic contract
    before LibreEvolve can claim robust codebase-scale invalid-artifact
    feedback.

- [ ] Track Table 1 code-scale benchmark evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 2.1.
  - Requirement: AlphaEvolve reports evolving entire code files, hundreds of
    lines of code, any language, and complex algorithms spanning multiple
    functions and components.
  - Partial status: LibreEvolve has Python-primary workspaces, multi-file seed
    loading, file-topology mutations, materialization diagnostics, full-workspace
    prompt/export paths, and a small multi-file smoke fixture.
  - Current gap: there is no paper-facing benchmark or report that demonstrates
    hundreds-line generated programs, coupled multi-component edits, non-Python
    or build-runner execution, realistic codebase dependency edits, evaluator
    throughput, or quality progress on a large codebase-scale task.
  - Required result: add codebase-scale benchmark fixtures and reports with
    generated/changed line counts, component/file counts, dependency-edit
    evidence, evaluator/runtime budgets, valid/admitted/retained rates, and
    score progress before treating current workspace support as AlphaEvolve
    Table 1 code-scale parity.

- [ ] Track Table 1 capability-comparison exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 1 compares FunSearch
    and AlphaEvolve across capability and behavior rows: function/file
    evolution, code length, programming language scope, evaluator duration and
    accelerator/parallelism support, LLM sample counts, model scale, prompt
    context and feedback, and single versus multiple metrics.
  - Current gap: paper TODOs already split out several Table 1 row claims such
    as code-scale behavior, sample efficiency, model mix, rich context,
    evaluator workload, and multi-metric optimization. They do not preserve
    Table 1 as a table exhibit with stable table/row ids, source page/caption
    location, exact comparison text, row ordering, row-to-implementation
    status, row-to-TODO/report mappings, rendered table artifact hashes, or
    validation that docs do not treat partial row coverage as full Table 1
    parity.
  - Required result: add paper-facing Table 1 exhibit records with row ids,
    FunSearch/AlphaEvolve comparison text, source location, per-row status and
    evidence links, rendered artifact paths/hashes, and README/ROADMAP wording
    that separates reproducing the Table 1 comparison artifact from satisfying
    the individual behavioral capability rows.

- [ ] Track Figure 1 and Figure 2 process-overview exhibit provenance as
      paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 1 shows the
    high-level AlphaEvolve workflow: human-provided evaluation criteria,
    initial solution, optional background knowledge, LLM ensemble, prompt
    sampler, evaluator pool, program database, rich context, proposals, and
    quality scores/feedback. Figure 2 expands the discovery process with
    user-provided initial program, evaluation code, optional configuration,
    parent/inspiration sampling, prompt construction, diff generation, diff
    application, evaluator execution, and database registration of promising
    solutions.
  - Current gap: paper TODOs track Table 1 and Figure 3+ exhibit provenance
    plus many individual Figure 1/2 component behaviors, but they do not
    preserve Figures 1 and 2 as their own process exhibits with stable
    figure IDs, diagram-node labels, edge/process-flow ordering,
    pseudocode-line mappings, source/caption locations, rendered diagram
    artifact hashes, or row/linkage from each displayed process step to
    implementation status and remaining TODOs.
  - Required result: add paper-facing Figure 1/2 exhibit records with figure
    and step IDs, exact diagram text, source page/caption locations,
    pseudocode-line mapping for Figure 2, rendered/text artifact paths and
    hashes, component-to-evidence/TODO links, and README/ROADMAP wording that
    separates reproducing the paper process diagrams from implementing each
    underlying AlphaEvolve workflow capability.

- [ ] Track evaluator workload provenance for inner-search and ML-training
      evaluators.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: AlphaEvolve's evaluation function may run a simple property
    check, an evolved search algorithm, or train and evaluate a
    machine-learning model before returning scalar metrics.
  - Partial status: LibreEvolve records evaluator entrypoint paths, configured
    stages, samples, retries, seeds, subprocess attempts, budgets, problem-local
    dependency provenance, copied evaluator artifacts, and bounded environment
    evidence.
  - Current gap: paper-facing evidence does not identify the evaluator workload
    type or preserve the protocol needed for search/training-style evaluators:
    dataset and split provenance, model-training configuration, checkpoint or
    artifact policy, inner-search budget, randomized initialization policy, and
    linkage from produced artifacts to returned scores.
  - Required result: add report/manifest evidence for evaluator workload
    classes such as `simple_check`, `inner_search`, and `ml_training`, with
    dataset/split hashes, training/search budget records, checkpoint/artifact
    linkage, seed/retry semantics, score-field mapping, and examples that keep
    quick validators distinct from AlphaEvolve-style evaluator workloads that
    train models or run search.

- [ ] Complete accelerator/async budgets and executed ablation support.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.6 and 4.
  - Requirement: AlphaEvolve optimizes throughput under a fixed computation
    budget, and ablations compare performance as a function of consumed budget.
  - Partial status: LibreEvolve now has a local `RunBudget` for
    `max_generations`, optional total evaluation count, optional cumulative
    evaluator seconds, optional detailed evaluator counter limits, and optional
    wall-clock seconds. It also has an optional `max_llm_calls` cap on logical
    LLM `generate()` calls plus an optional `max_llm_provider_attempts` cap on
    recorded provider adapter attempts, `max_llm_tokens` for provider-reported
    token totals, `max_llm_cost_microusd` for configured estimated cost, and
    `max_llm_seconds` for retained LLM call latency.
    Candidate history records include budget snapshots, and completed
    manifests include consumed budgets plus structured stop reason.
  - Current gap: provider-reported token totals are now audit telemetry, and
    configured `cost_usd_per_million_tokens` rates can estimate provider cost
    from those token totals. Per-call cost estimates now declare configured
    backend metadata as the pricing source, provider usage metadata as the
    token-count source, and explicitly avoid claiming live provider pricing.
    Per-call `cost_estimate_status` records now preserve not-estimated reasons
    for missing configured rates or missing/invalid provider token totals.
    Live global token and configured-cost stop
    criteria now exist, and full-runtime restore now pre-applies replayed
    provider-attempt/token/configured-cost/latency controller events to the
    restored `evolve()` budget snapshot. Accelerator budgets, async queue
    accounting, live provider pricing/default-rate capture beyond configured
    token-cost estimates, and executed equal-budget benchmark scripts are still
    missing.
    `libreevolve.alphaevolve_ablation_report.v1` now defines and tests an
    equal-budget ablation-result report contract for reports produced by
    executed runs: the Figure 8 full-system baseline plus five component
    ablations, declared targets, exactly three seeds, required equal-budget
    fractions, finite scores,
    consumed-budget/fraction consistency, consistent budget unit/limit per seed
    curve and across all variants/seeds for each target, passed component
    assertions, and hashed curve artifacts.
    That report contract remains target-family generic: it does not require the
    two Figure 8 task families, low-rank matrix tensor decomposition and
    kissing-number sphere packing, and it does not validate per-target
    mean/standard-deviation curve summaries against the underlying three
    independent seed traces.
    `libreevolve.alphaevolve_ablation_artifact_inventory.v1` now verifies
    declared ablation report artifacts under an explicit artifact root,
    checking safe relative paths, existence, SHA-256 hashes, byte counts,
    per-artifact statuses, and aggregate missing/mismatch/invalid counts. No
    benchmark script emits those reports yet.
    `alphaevolve_ablations.json` defines the Figure 8 variant names and
    intended component assertions, but the registry is still
    `definition_only`: several assertion fields are declarative labels rather
    than executable `Config` switches, including `candidate_source`,
    `archive_admission_enabled`, `prompt_context_sections`,
    `candidate_workspace_mode`, `file_create_delete_enabled`,
    `ensemble_strategy: single_backend`, and `backend_capability_tier`.
    The `No full-file evolution` variant is also broader than the paper's
    tensor-decomposition ablation: AlphaEvolve restricted that alternative to
    evolving only the loss function, while the current registry does not bind a
    target file, evolve block, symbol, or report field proving
    loss-function-only mutation.
    `libreevolve.llm_feedback_calibration.v1` now defines and tests a feedback
    grader calibration-report contract with declared graders, at least two
    calibrated tasks for readiness, per-grader/task scored records, finite
    normalized expected and observed scores, exact absolute-error consistency,
    and declared calibration artifacts.
    `libreevolve.llm_feedback_calibration_artifact_inventory.v1` verifies those
    calibration report, raw-record, grader-config, and plot artifacts against a
    safe artifact root. No runtime feedback-calibration fixture emits those
    reports yet.

    Evaluator subprocess-attempt, configured-stage sample, retry, timeout, and
    sample/stage budget-exhaustion counters now persist in evaluation
    accounting and runtime manifests, and optional run-wide limits can stop on
    those detailed evaluator counters. Provider adapters now expose configured
    internal retry caps and per-call adapter retry telemetry, and
    `max_llm_provider_attempts` can stop before the next LLM call after those
    provider-internal attempts are recorded. `max_llm_tokens` and
    `max_llm_cost_microusd` can also stop before the next LLM call after
    provider usage or configured cost telemetry consumes those caps. LLM provider
    calls now have configured request timeouts/deadlines, and deadline-aware
    `LLMEnsemble` calls are clamped to the remaining `max_runtime_seconds`
    wall-clock budget before each attempt starts. Aborted runs
    after startup manifest creation now write runtime status, exception
    metadata, phase/role, budget snapshot, history-written status, and
    artifact/quarantine pointers before re-raising. Manifest writes are also
    serialization-safe and atomic for normal manifest creation/final runtime
    updates: rejected runtime payloads preserve the last valid `manifest.json`
    and append diagnostics to `manifest_invalid.jsonl`. Terminal
    seed/generated rows that consume evaluation or detailed evaluator-counter
    budgets now record the exhausted `metadata.budget.stop_reason`. Exhausted
    mutation-provider failures now write generated failure-history rows with
    bounded/redacted provider-failure metadata and retained LLM call telemetry,
    then continue later generations when budget remains. Built-in provider
    clients now accept configured request timeouts.
    `libreevolve.provider_cancellation_policy.v1` now defines and tests a
    policy/report contract for provider request timeouts, ensemble wait
    deadlines, runtime deadlines, hard cancellation rules, role-scoped budget
    actions, artifact requirements, required artifact-kind linkage,
    hard-cancel readiness gated on `cancellation_record` artifact evidence, and
    hashed cancellation artifacts. Runtime manifests now scope provider-timeout
    and ensemble-deadline rules to `mutation`, `critique`, `feedback:*`, and
    `meta_prompt`. Rules for scopes with configured
    `llm_role_failure_quarantine_after` now declare timeout-driven
    `quarantine` actions and `quarantine_record` evidence, matching the
    ensemble's role/backend failure-threshold quarantine state. Runtime
    cancellation-policy records now also include
    `libreevolve.provider_cancellation_observations.v1`, derived from the
    validated LLM scheduler snapshot, with timeout-failure counts by role,
    configured quarantine thresholds, and quarantined backend counts when
    observed. `libreevolve.provider_cancellation_artifact_inventory.v1` now
    verifies declared timeout, cancellation, budget-stop, and quarantine
    artifacts against concrete files under an explicit artifact root, checking
    safe relative paths, existence, SHA-256 hashes, byte counts, per-artifact
    status, and aggregate missing/mismatch/invalid counts. Exhausted
    mutation timeout failures now write generated failure-history rows with
    retained timeout telemetry and can continue later generations when budget
    remains. Failed LLM call rows now record
    `provider_failure_policy` with retry/fallback decisions plus explicit
    quarantine/penalty decisions; configured
    `llm_role_failure_quarantine_after` roles can now quarantine exhausted
    failing role/backend pairs and apply zero-reward scheduler penalties to
    reward-accounted failures. Strict ledger replay now derives
    `provider_failure_policy_summary` for audit-only role/category/decision
    evidence. Ensemble-deadline timeout rows now also include a
    replay-validated `libreevolve.provider_cancellation_record.v1` with the
    role, backend, call id, timeout seconds, retry/fallback/telemetry budget
    action, and explicit `unsupported_daemon_worker_may_continue` hard-cancel
    gap. Remaining budget/runtime gaps are live hard cancellation handles,
    timeout-driven stop enforcement beyond audit observations, richer
    role-specific timeout/cancellation artifacts beyond configured in-run
    quarantine observations, accelerator/worker budget enforcement, live
    provider pricing/default-rate capture beyond configured token-cost
    estimates, provider-output/raw-payload replay beyond bounded retained
    diagnostics, and async/pending-work controller restore. The remaining gap
    is not in-run role/backend failure quarantine state, strict
    provider-failure ledger summaries, restorable scheduler failure-policy
    state, remaining-runtime wait-deadline propagation, timeout call telemetry,
    mutation timeout failure-history logging, or one-command restoration of
    replayable provider-attempt/token/configured-cost/latency controller events
    for the current synchronous runtime bundle.
  - Required result: unify retry accounting across provider adapters and the
    ensemble, add accelerator/async-worker budget counters,
    connect hard cancellation semantics to runtime behavior beyond the current
    configured provider request timeout, ensemble `llm_call_timeout_sec`, and
    remaining-runtime wait deadlines, and add benchmark scripts that emit
    equal-budget ablation reports for real targets plus feedback-grader
    calibration reports for real reviewer/task suites. Those scripts must bind
    Figure 8 component assertions to actual supported config/runtime controls
    or fail when a named assertion is only declarative. For the `No full-file
    evolution` variant, require loss-function-only tensor-decomposition scope
    evidence rather than treating generic single-file/diff/no-topology settings
    as equivalent. For the `No evolution` variant, require executed prompt and
    history proof that each candidate is generated from the same initial
    program with no database-selected parent/inspiration programs, archive
    admission feedback, or previous-candidate resurfacing, rather than relying
    on declarative `candidate_source` or `archive_admission_enabled` labels.
    For the `No context in the prompt` variant, correct the registry's
    over-broad semantics: the paper describes removing explicit
    problem-specific context, not removing the current program or evolutionary
    prior-program context. Require executed prompt-history and
    prompt-diagnostic proof that explicit context sources were absent, require
    a paper-facing classification of local plugin/retrieval/failure sections
    as explicit context or core prompt ingredients, and separately record which
    current-program, parent, inspiration, and rendered-result sections remained
    present so this ablation is not conflated with `No evolution`. For the
    `Small base LLM only` variant, require executed backend telemetry proving
    that every mutation-generation call used one configured small/base-capable
    model with no large-model backend eligibility, fallback, critique, or
    router leakage, rather than relying on declarative `single_backend`,
    `backend_count`, or `backend_capability_tier` labels. For the
    `No meta prompt evolution` variant, require executed prompt-history and
    call-ledger proof that meta-prompt calls, prompt-template mutations, and
    prompt-program lineage updates were disabled for the ablation while the
    full-system baseline had meta-prompt evolution enabled and mutable prompt
    variants. Also require the paper-facing result bundle to identify the
    frozen human-authored prompt source, revision, and context policy used for
    the human-prompter comparator, because Figure 8 motivates the ablation as
    testing whether meta prompts can surpass a human prompter rather than only
    whether a local meta-prompt role was toggled off. The
    remaining ablation and calibration gap is executing and
    emitting real reports from runnable variants over the Figure 8 matrix and
    kissing-number target families, with curve summaries that expose
    target-metric identity, higher-is-better direction, normalization policy,
    and per-target and cross-target mean/standard-deviation evidence. The gap
    is not validating declared result or feedback-calibration artifacts once a
    report names them.
    The remaining provider cancellation gap is live cancellation/stop behavior,
    cross-run quarantine/resume behavior, and richer runtime artifact
    generation, not configured in-run role/backend quarantine observations or
    verifying declared cancellation evidence files once a policy names them.

- [ ] Track Figure 8 ablation-curve exhibit provenance as paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 8 shows two ablation
    plots: matrix multiplication tensor decomposition and the kissing-number
    problem. Each plot uses compute-budget fraction on the x-axis, aggregated
    target metric on the y-axis, named full/ablated method curves, and shaded
    intra-target standard deviation averaged over three independent seeded runs.
  - Current gap: paper-facing ablation TODOs require executable benchmark
    scripts, component-assertion bindings, target-family coverage,
    per-target aggregation, and three-seed traces. They do not preserve the
    Figure 8 visual as its own paper exhibit with stable exhibit/panel IDs,
    series-to-variant legend mapping, exact paper legend labels,
    axis labels/scales, color/style/shading metadata, source PDF page/caption
    location, rendered plot artifacts and hashes, or links from each plotted
    curve to exact report rows, raw seed traces, and aggregation records. The
    current ablation registry uses `paper_label: "Full"` for the baseline, but
    Figure 8's legend labels that curve `Full method`, so the registry is not
    yet exact legend-label provenance.
  - Required result: add Figure 8 exhibit records and validation: exhibit and
    panel IDs, matrix/kissing target-family mapping, exact paper legend labels
    including `Full method`, curve/legend definitions, budget-fraction axis
    metadata, target-metric aggregation and std-band source records, rendering
    parameters, rendered visual artifact hashes, and docs wording that separates
    reproduced Figure 8 visual evidence from generic ablation-report validation.

- [ ] Connect LLM budget reports to async/pending-work resume and
  provider-output replay.
  - Paper evidence: AlphaEvolve-style systems use large but explicit compute
    budgets; provider retry settings should be bounded, attributable, and
    resumable rather than open-ended integers.
  - Current evidence: ensemble-layer retry counts are now capped at `10`, total
    original/retry/fallback attempts per logical ensemble call are capped by
    `llm_max_call_attempts`, and call telemetry records attempt index plus the
    configured cap. Live `max_llm_calls` accounting now clamps
    `LLMEnsemble.max_call_attempts` to the remaining call budget and records
    actual retry/fallback call-history attempt deltas into runtime/candidate
    budget snapshots. Provider adapters now expose `provider_max_retries` and
    `adapter_retry` telemetry for internal attempts, and role accounting now
    aggregates provider-reported token totals. `max_llm_provider_attempts` now
    consumes recorded adapter attempts as a live after-call stop input, while
    `max_llm_tokens`, `max_llm_cost_microusd`, and `max_llm_seconds` do the
    same for token, configured-cost, and retained LLM call-latency consumption.
    Per-role seconds limits use `llm_role_seconds_limits` and are surfaced in
    runtime budget snapshots and LLM budget-report rows. Role-budget limit maps
    now accept manifest-safe prefix scopes such as `feedback:*`, and shared
    scoped caps are enforced by summing matching exact-role logical calls,
    provider attempts, tokens, configured cost, and retained call latency while
    keeping consumed counters concrete. Runtime manifests now persist a
    compact `runtime.llm_accounting` summary with role totals plus active
    logical-call, retry/fallback, timeout, prompt, and accepted-output caps,
    `libreevolve.llm_budget_report.v1` now defines and tests paper-index-visible
    retry-budget report semantics for mutation, critique, and feedback roles,
    adapter-internal attempts, token/cost/wall-clock limits and usage, and
    persisted resume-state hashes. Current reports use status
    `cooperative_enforcement_snapshot` and policy
    `runtime_cooperative_budget_enforcement_v1`, and the validator rejects
    stale audit-only policy labels.
    `libreevolve.llm_budget_resume_artifact_inventory.v1` now verifies
    optional LLM budget `resume_state.artifacts[]` records against an artifact
    root, including safe relative paths, file existence, SHA-256 hashes, byte
    counts, per-record statuses, aggregate missing/mismatch/invalid counts, and
    a stable records hash. `validate_llm_budget_evidence_bundle()` now checks
    LLM budget reports together with resume artifact inventory, requiring
    matching run id, report schema, resume-state hash, inventory status,
    aggregate counts, zero missing/mismatch/invalid records, and inventory
    record-hash consistency before accepting bundled paper-budget readiness.
    Final manifests now emit `runtime.llm_budget_report`
    instances with observed per-role logical-call, retry, provider-attempt,
    usage counters, configured estimated cost, retained LLM latency, and
    scheduler-resume-hash evidence plus self-validation, and retained LLM
    call-history rows now provide per-call provider-internal retry records
    grouped by role plus configured-cost source metadata. Final
    manifests also emit `runtime.llm_provider_diagnostics` using
    `libreevolve.llm_provider_diagnostics.v1`, a retained-call-history
    aggregate that groups backend/API-mode usage, bounded provider diagnostic
    keys and omitted counts, provider response/error retention modes and
    policies, retained hash/text/character counts, redaction/truncation
    counts, configured cost-estimate evidence, not-estimated reasons, backend
    defaults, call-history retention, and a records hash while explicitly
    avoiding full raw provider-payload and live-pricing claims.
    `validate_provider_capability_lookup_policy()` now validates
    `libreevolve.provider_capability_lookup_policy.v1` records for static-only
    provider lookup boundaries, OpenAI API-mode policy linkage, offline
    compatibility, record count/hash integrity, and explicit non-use of live
    model-registry, service/API-version, or account-availability discovery.
    `validate_llm_provider_diagnostics_summary()` now validates the provider
    diagnostics summary contract, including record-hash integrity,
    non-negative counters, backend-count, total/backend aggregate count and
    retention-counter consistency, required limitation statements, and the
    no-live-pricing/no-raw-payload replay boundary. The budget report contract
    now rejects restored-state claims that lack persisted resume-state
    evidence. Focused ensemble tests now cover fake provider usage counts and
    adapter retry diagnostics for mutation, critique, feedback, and
    meta-prompt roles. Controller budget `llm_call` events now validate and
    replay role-tagged provider attempts, tokens, configured cost, and latency
    seconds into `RunBudget`, and full-runtime restore now replays contiguous
    controller budget events, verifies non-wall-clock consumed counters against
    the manifest budget snapshot, and passes that checked budget snapshot into
    `evolve()`. `validate_controller_budget_replay_state()` now exposes that
    provider-attempt/token/configured-cost/latency replay proof as a reusable
    budget contract and rejects snapshot drift before restored consumption is
    trusted.
  - Current gap: runtime enforcement is still incomplete for full restored
    controller state. LLM budget reports now describe cooperative live
    enforcement snapshots rather than audit-only evidence. LLM budget deltas
    are replayable through validated
    controller events, and prior manifest runtime budget snapshots can now be
    restored through direct `evolve()` calls or CLI
    `--restore-budget-from-manifest` before new work. Exhausted restored
    provider-attempt, token, configured-cost, latency, or wall-clock usage can
    therefore trip the same live stop checks in the resumed run. However,
    restored controller state is not yet connected to pending-work queues,
    async worker state, or provider-output replay. The remaining gap is not
    LLM budget resume artifact inventory, bundle-consistency verification, or
    current-report policy/status validation.
  - Required result: connect restored LLM budget state to async controller
    queues, pending-work restore, provider-output replay boundaries, and
    executed equal-budget ablation runs before treating local LLM ensemble
    scheduling as AlphaEvolve-grade budgeted search. The remaining gap is not
    provider-attempt/token/configured-cost/latency replay through the current
    synchronous controller budget stream.

- [ ] Add remaining full-run replay, lineage, provider, and custom-plugin
  provenance policy.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: task setup and evaluation code define what a run means, and
    long-running experiments need reproducible accounting for the code,
    evaluators, and generated program database.
  - Partial status: run identity and collision semantics are implemented.
    `manifest.json` records a UUID4 `run_id` and effective collision policy.
    Existing known run artifacts now fail startup by default; explicit
    `overwrite` removes only known run artifacts before the new run. Configured
    `validate_path` entries are constrained to problem-local Python files, and
    direct evaluator entrypoints are recorded in `manifest.json` with redacted
    problem-relative path labels, path hashes, streamed SHA-256 source hashes,
    byte counts, source type, source-hash policy/status, and stage usage
    metadata, plus bounded sibling helper/data `companion_sources` under each
    evaluator directory with streamed hashes, byte/count caps, skipped-file
    diagnostics, and a deterministic aggregate hash. Package-style evaluator
    directories containing `__init__.py` are imported as packages and hashed as
    package entrypoints. Declared evaluator data globs are hashed under
    `declared_data_sources` and passed to validators through
    `stage["evaluator_data"]`. The manifest also records Git state when
    available, `libreevolve/` source-tree hashes, problem-tree hashes, and
    plugin module file hashes. Runtime finalization now records aggregate
    emitted-artifact hashes for known artifact files/directories and
    `runtime.plugin_state.loaded_specs` records validated constructor
    parameters for built-in loaded plugin instances. Built-in plugin config
    specs now validate supported constructor options before construction, and
    configured entry-point plugin classes can publish declared constructor
    option schemas that reject unknown or malformed options before
    instantiation. Entry-point plugin specs also record configured paper-
    inspiration labels and distribution name/version plus hash-only RECORD/WHEEL
    metadata when available. Custom direct plugin specs record constructor
    signature shape without parameter values. Captured direct-plugin
    constructor values, arbitrary direct-plugin schemas, and richer custom
    package policy beyond entry-point distribution records remain part of the
    broader plugin registry gap. Problem-local evaluator
    helper/data access is now governed by an enforced declared-dependency
    policy: validator imports and file reads may touch only the configured
    entrypoint, captured companion sources, or captured declared data sources.
    Seeded replay is still incomplete, but the identity gap is narrower than
    the older paper-audit wording: loop-created seed and generated candidate
    ids are deterministic, and `PromptDatabase` creates deterministic ids for
    configured seed templates and prompt mutations. Direct `Program()` and
    direct `PromptProgram()` construction still default to UUID4 values unless
    callers provide ids, and the deterministic ids are not yet composed with a
    full run-resume/replay contract across provider outputs, archive restore,
    controller state, and migration ordering. Runtime manifests now declare
    `runtime.lineage_replay_policy`, and full-runtime restore validates and
    packages that provider-output non-replay boundary as checked metadata.
    Full-runtime restore now also emits
    `libreevolve.full_resume_bundle_validation.v1`, validating the composed
    runtime RNG, LLM scheduler, archive restore, runtime budget,
    controller-budget replay, lineage boundary, and unsupported-surface list
    while keeping full replay, provider-output replay, and pending-work resume
    marked unavailable. But
    this still stops short of an end-to-end replay trace that proves identical
    provider outputs or resumed lineage. Validator subprocesses now use an
    explicit
    minimal environment plus `validator_env_allowlist`, so `.env` provider
    credentials are hidden by default and persisted stdout/stderr is
    secret-redacted. Network egress policy and stronger sandboxing remain
    incomplete. Validator timeouts now attempt process-tree cleanup and record
    cleanup metadata, but this is not a full resource sandbox.
    `validate_validator_execution_policy()` now validates startup
    `libreevolve.validator_execution_policy.v1` records for honest local
    subprocess execution, unsupported sandbox/container claims,
    filesystem-capability structure, network mode and denial scope,
    wall-clock-only limits, unsupported CPU/memory/GPU/disk/process-count
    quotas, and the required per-evaluation boundary pointer.
    `validate_validator_boundary_consistency.v1` now checks that attempt-level
    `evaluation.metadata.validator_boundary` records match the startup policy
    across execution, filesystem-capability, network, resource-limit, and
    secret-boundary claims while still marking the full sandbox unavailable.
    Problem-local
    evaluator helper modules are imported as sibling modules beside a
    configured validator file or through package-relative imports for package
    validators; declared evaluator data files are hashed and exposed through
    stage context. Undeclared or over-budget problem-local helper/data access
    now fails during preflight or evaluation instead of running outside
    manifest provenance.
    Validator helper import precedence is now explicit: the validator directory
    precedes the materialized candidate workspace on `sys.path`, so
    problem-local evaluator helpers win same-name import collisions while
    candidate-local imports still work when they do not collide.
    Run artifact path confinement now rejects unsafe scalar run names and
    validates the resolved run directory before cleanup or writes, so
    symlink/junction escapes outside the resolved `log_dir` fail instead of
    being followed during overwrite startup.
    Known artifact directories inside a valid run directory are now
    individually link-checked before overwrite cleanup: `ProgramDatabase(...,
    overwrite)` rejects symlink or Windows-junction entries such as
    `best_workspace/`, `evaluator_artifacts/`, or `plugin_artifacts/` before
    deleting any artifact, with tests for symlink-capable platforms and Windows
    junctions.
    Unknown run-directory entries are now an explicit preserve-and-diagnose
    policy. Startup preserves unknown immediate files/directories under both
    `fail` and `overwrite`, treats them as outside the run-owned artifact set,
    and records count, entry type, and hashed immediate names in
    `manifest.json` without exposing raw filenames.
    Run names now share the runtime identity secret-safety policy: assignment-
    style secret strings and provider-token-shaped values are rejected before
    filesystem or manifest writes, while ordinary portable run names remain
    valid.
    CLI plugin preflight now validates built-in plugin aliases before
    run-directory preparation, rejects empty and whitespace-only plugin
    identifiers in config, and validates TTTRL/DeepResearch cadence constructor
    values before hook execution. Built-in OpenAI/Anthropic credential checks
    and backend client construction now run before destructive cleanup when a
    mutation LLM can execute. Zero-generation baseline runs are provider-free:
    LLM backends are constructed lazily only when a mutation LLM call is needed,
    and CLI tests cover `--max-generations 0` with an OpenAI backend and no
    provider credentials.
    Dotenv/provider environment precedence is now isolated from import:
    `libreevolve.cli` imports do not load `.env`, `show` remains provider-free
    while selecting candidates from streamed history and reading bounded
    manifest runtime/export status, and the `run` command loads `.env` with
    `override=True` during provider setup while recording non-secret source
    metadata in the run manifest.
    The backend preflight guarantee is now a core runtime invariant for
    mutation-capable runs: direct `evolve()` constructs configured backend
    clients before run-directory preparation, and tests prove missing OpenAI
    credentials preserve existing overwrite-mode history and write no
    replacement manifest.
  - Required result: add true full-run resume/replay semantics, deterministic
    lineage-id behavior or an explicit UUID identity exclusion from the replay
    contract, provider-output replay boundaries, arbitrary direct-plugin
    constructor value/schema policy, richer custom plugin package provenance
    beyond entry-point distribution records, and live authenticated provider
    request/model-registry evidence beyond credential-presence and local client
    construction.
    Startup ordering for positive-generation all-invalid seeds is now
    documented and tested as a conservative provider-readiness contract: if a
    mutation LLM could execute, provider preflight runs before seed evaluation
    in both CLI and direct runtime. This protects artifacts but intentionally
    prevents provider-free startup diagnostics for all-invalid seeds in
    mutation-capable runs.
    Credential presence now requires non-blank OpenAI/Anthropic environment
    variables after trimming before CLI mutation runs can reach overwrite
    cleanup or `evolve()`. Remaining provider-readiness gaps are that local
    preflight still does not prove live provider authentication, and the
    explicit non-blank credential trim check is CLI-scoped while core runtime
    preflight relies on backend client construction. The AlphaEvolve table now
    scopes the open provider-auth gap to live authenticated request/model-registry
    validation rather than implying credential-presence and client-construction
    preflight are absent.

- [ ] Add paper-facing validator-boundary consistency artifact evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: run artifacts that support generated-program evaluation
    claims should preserve and verify the validator execution boundary used by
    each candidate attempt.
  - Partial status: `manifest.json` records
    `policies.validator_execution`; evaluator metadata records include
    `evaluation.metadata.validator_boundary`; and
    `validate_validator_boundary_consistency()` can compare the manifest policy
    with an attempt boundary across execution, filesystem-capability, network,
    resource-limit, and secret-boundary claims. Direct validator-policy tests
    cover matching and mismatched records.
  - Current gap: the paper-facing artifact surface still lacks an automated
    manifest/history validator that applies the consistency contract to every
    persisted evaluation attempt and reports missing, legacy, or drifting
    boundary metadata before run artifacts are promoted as evidence.
  - Required result: add paper-facing validation/report evidence for
    policy-to-attempt boundary consistency, including clean-run, mismatch,
    missing-boundary, and legacy-row diagnostics, while keeping this artifact
    gate separate from the broader missing OS/container sandbox and
    resource-quota enforcement.

- [ ] Integrate restored run-local RNG with full AlphaEvolve replay claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: long-running AlphaEvolve-style experiments should own and
    persist their stochastic state without resetting an embedding application's
    process-global Python RNG.
  - Current evidence: framework-owned parent selection, inspiration sampling,
    prompt-template sampling, island sampling, and MAP-Elites random sampling
    use an explicit run-local RNG without perturbing caller process-global RNG
    state. Completed and aborted runtime manifests persist checked
    `runtime.rng` snapshots with schema `python.random.mt19937.v1`, configured
    seed, JSON-safe `random.Random.getstate()` state, `state_sha256`, and the
    `random.Random.setstate` restore entrypoint.
    `load_runtime_rng_state_snapshot()` and
    `restore_runtime_rng_state_snapshot()` validate persisted snapshots; direct
    `evolve()` callers can pass `runtime_rng_state_snapshot`; CLI runs can pass
    `--restore-rng-from-manifest`; and seed mismatches are rejected before
    `evolve()`. `runtime.rng.replay_boundary` records the framework-owned RNG
    surfaces covered by restore plus explicit exclusions for LLM provider
    outputs, plugin internal randomness, and validator subprocess randomness,
    while validation normalizes older boundaryless snapshots.
    `load_full_resume_bundle()` now surfaces the validated replay boundary as
    explicit restore metadata beside the RNG snapshot and lineage replay policy.
  - Current gap: full run replay still lacks provider output replay,
    plugin-owned RNG capture, controller/pending-work state restore, and
    lineage replay.
  - Required result: compose persisted RNG restore with full resume/replay,
    define provider-output and plugin-owned RNG capture or exclusion semantics,
    and keep paper-index seeded-replay claims scoped so they do not imply full
    replayability until this is true.

- [ ] Promote multiple-score overlays to primary archive optimization.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: optimize multiple user-provided scores and use programs that
    excel under different criteria as varied inspirations.
  - Partial status: metric vectors are stored, normalized primary fitness
    honors direction/bounds, and declared numeric metrics are normalized into
    a configurable archive `selection_score` used for MAP-Elites replacement,
    elite ordering, and exploit/best sampling. The default selection score is
    an equal-weight normalized-metric mean, and optional finite non-negative
    `metrics.yaml` metric `weight` values switch it to a weighted normalized
    declared-metric policy. Archive admission metadata and migration event rows
    now carry an `objective_vector` audit record with the finite normalized
    metric vector plus selection policy when available, and `show`
    validates/prints bounded selected objective-vector summaries.
    Runtime manifests now include `runtime.history.objective_frontier`, a
    bounded diagnostic Pareto frontier over complete declared normalized metric
    vectors, plus `runtime.history.objective_metric_leaders`, a diagnostic
    best-program view for each declared normalized metric, and
    `runtime.history.objective_metric_archives`, a bounded top-program view for
    each declared normalized metric. Runtime manifests now also include
    `runtime.history.lineage_index`, a bounded diagnostic best-valid-programs
    view grouped by root lineage, and `runtime.history.descriptor_index`, a
    bounded diagnostic top-program view for finite archive-admission descriptor
    values. Runtime manifests now also include `runtime.history.score_index`, a
    bounded diagnostic top-valid-program view ranked by selection score and
    final fitness. Runtime manifests now also include `runtime.history.feedback_index`,
    a bounded diagnostic feedback-record view grouped by LLM feedback grader.
    LLM
    feedback graders now support
    bounded raw scores, maximize/minimize direction, normalized fitness-delta
    composition, and `objective_metric: true` filling for declared non-primary
    `source: feedback` objective metrics. Declared non-primary
    `source: plugin` metrics can be filled by plugin hooks through validated
    metric side effects and then participate in normalized objective selection
    and metric-specific views. Declared non-primary `source: final_fitness`
    metrics are synthesized from the candidate's final composed fitness after
    plugin score hooks run, so plugin-adjusted top-level fitness can be included
    in the declared objective vector when desired. Metric-specific archive replacement and
    Pareto/frontier optimization remain open because the frontier and
    metric-specific views are diagnostic and not archive replacement policies.
    Parent and inspiration sampling can now use
    metric-leader, frontier, lineage, novelty, recency, selection-score, random, and mixed
    strategies while excluding the selected parent and deduplicating migrated
    copies by program id. Bounded score-ranked manifest evidence is now
    available. Durable persisted feedback ranking and full cross-run
    database resurfacing remain open. Metric bounds are now strictly ordered before they
    can be used as policy inputs. Metric-leader parent sampling now cycles
    through primary and secondary metric targets in configured order and
    persists target-metric provenance. Metric-leader inspiration sampling now
    persists selected ids plus metric target/program pairs in generated
    candidate metadata. Frontier parent/inspiration sampling uses complete
    declared normalized metric vectors to surface non-dominated retained
    programs and persists frontier size/metric-order provenance. Lineage
    parent/inspiration sampling uses root lineage metadata to surface the best
    retained representative per root, persists lineage-root provenance, and
    exposes bounded lineage-index evidence in final manifests. Descriptor-index
    evidence makes insertion-time diversity/complexity/performance coordinates
    inspectable from run artifacts, and feedback-index evidence makes
    grader-specific scores, deltas, retention summaries, and failure/discard
    status inspectable. MAP-Elites archives now retain a bounded
    non-dominated Pareto archive over complete declared normalized metric
    vectors, persist/restore Pareto frontier program ids and the objective
    archive policy, and allow island metric/frontier retained pools to sample
    Pareto-only programs that lost scalar cell/elite placement. MAP-Elites
    archives now also persist/restore `metric_cell_archives`, per-declared
    objective metric descriptor-cell overlays that retain best programs by each
    normalized metric and feed metric/frontier retained pools, so programs can
    survive for excelling in a specific metric even when they lose scalar
    primary-cell placement. The AlphaEvolve table now scopes the open
    multi-objective search gap to Pareto/frontier primary archive replacement
    and durable cross-run metric-specific optimization rather than claiming all
    frontier or metric-specific search remains absent. Runtime
    manifests now include `runtime.history.resurfacing_index`, a bounded
    deterministic rank-fusion view over score, metric, frontier, lineage,
    descriptor, and feedback indexes, and `ProgramDatabase.resurface_candidates()`
    returns defensive ranked snapshots from that same source mix.
    `ProgramDatabase.resurface_candidates(target_metric=...)` now exposes
    declared-metric-targeted resurfacing over the objective metric archives and
    rejects undeclared metric targets. `ProgramDatabase.resurface_by_metric()`,
    `resurface_by_lineage()`, `resurface_by_descriptor()`,
    `resurface_by_novelty()`, and `resurface_by_feedback()` now expose
    defensive run-local query results from the bounded metric, lineage,
    descriptor/novelty, and feedback views.
    `validate_resurfacing_index_summary()` now validates that
    `libreevolve.resurfacing_index.v1` record for schema/policy, required
    limitations, counts, source contributions, source records, normalized
    objective evidence, and deterministic rank order while preserving
    `durable_database_ready: false`.
    The paper index now includes a dedicated database-resurfacing note that
    lists the bounded current-run resurfacing APIs and narrows the remaining
    AlphaEvolve gap to durable cross-run query/index tables, full
    metric-vector and feedback/artifact-content ranking, semantic/cross-run
    novelty or hypothesis retrieval, schema migrations, and replayable
    sampling policies.
    `validate_objective_history_summary()` now validates the runtime
    multi-objective diagnostic history bundle across objective frontier,
    metric leaders, and metric archives, including schema/policy values,
    shared metric order, non-negative counters, retained-count and
    retention-limit consistency, normalized metric ranges, non-dominated
    retained frontier records, and explicit diagnostic-not-primary-archive
    limitation statements.
    `validate_map_elites_objective_archive_policy()` now validates
    `libreevolve.map_elites_objective_archive_policy.v1` snapshot policy
    records and rejects overclaims that bounded Pareto/frontier retention has
    replaced the primary scalar MAP-Elites cell policy.
    `runtime.history.failure_index` now groups failure records by fingerprint
    with bounded repetition/latest-record evidence. `runtime.history.hypothesis_index`
    now exposes bounded redacted proposal idea/rationale/hypothesis evidence
    and feeds hypothesis records into `resurfacing_index`. This remains a
    heuristic rather than a paper-faithful multi-score database policy:
    primary MAP-Elites cell replacement is still scalar, Pareto/frontier
    dominance does not replace the primary grid, and durable queryable
    multi-objective resurfacing across persisted database tables, embeddings,
    cross-run failure and hypothesis indexes, full artifact-content indexes,
    program-output value/schema indexes, full lineage subgraphs,
    learned/cross-run novelty indexes, and schema migrations remains open.
    Current evaluator outputs/program outputs can be captured, redacted,
    checked, and rendered to prompts, but they are not a durable resurfacing
    dimension despite AlphaEvolve's database storing solutions with attached
    evaluation results and program outputs. `runtime.history.artifact_index`
    now exposes bounded evaluator-artifact path/hash, redaction, skipped-file,
    stage, and content-excerpt evidence, and valid artifact-bearing candidates
    feed into `resurfacing_index`.
  - Required result: add Pareto/frontier archive replacement and durable
    persisted lineage-aware resurfacing for programs that excel under different
    metrics, including output-aware indexes for attached program outputs.

- [ ] Track multiple-score prompt-diversity evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: AlphaEvolve says multiple scores can help even when one target
    metric matters because prompts include programs with different structures
    and logic that excel under different evaluation criteria, each representing
    a different definition of "good".
  - Partial status: LibreEvolve records declared metric vectors, metric leaders,
    objective frontiers, metric-cell overlays, metric-targeted resurfacing, and
    selected parent/inspiration target-metric provenance. Prompt context policy
    can filter and rank inspirations by metric, and prompt histories retain
    selected parent/inspiration ids.
  - Current gap: the paper/status surfaces do not yet require evidence that a
    rendered prompt intentionally contained inspirations from distinct
    metric/objective niches, labelled each prompt-visible inspiration by the
    metric it represents, or distinguished one-at-a-time metric-targeted
    sampling from AlphaEvolve-style diverse-metric prompt context.
  - Required result: add report/manifest evidence for metric-diverse prompt
    conditioning: metric/objective labels, per-metric rank/score, inspiration
    selection reason, prompt-history linkage, and validation that multi-score
    benchmark runs can distinguish scalar archive sampling from prompts that
    show different definitions of "good" at once.

- [ ] Proposal scoring and semantic hypothesis retrieval.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.4.
  - Requirement: prior ideas and hypotheses should be reusable as searchable
    evolutionary evidence, with proposal quality and novelty reflected in
    future selection rather than only attached as candidate metadata.
  - Partial status: mutation outputs can include bounded `IDEA`, `RATIONALE`,
    and `HYPOTHESIS` proposal metadata. `runtime.history.hypothesis_index`
    exposes bounded redacted proposal idea/rationale/hypothesis summaries for
    valid programs, sorted by scalar selection score/final fitness/generation,
    and feeds hypothesis evidence into the run-local resurfacing index. Recent
    proposal-hypothesis terms can also feed DeepResearch retrieval queries.
  - Current gap: there is no versioned proposal score, calibrated hypothesis
    quality or novelty signal, embedding/semantic proposal index, cross-run
    persisted proposal table, or policy that fully governs which proposal
    fields can influence retrieval, prompting, and archive resurfacing.
  - Required result: add proposal scoring, semantic/cross-run
    proposal-hypothesis retrieval, persisted proposal-index tables, and
    prompt/retrieval/archive policy boundaries before treating proposal
    metadata as AlphaEvolve-grade idea memory.

- [ ] Track initial-pool syntactic and functional divergence evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Introduction.
  - Requirement: AlphaEvolve says LLMs responding to feedback can discover
    candidates substantially different from the initial candidate pool in both
    syntax and function.
  - Partial status: LibreEvolve records parent lineage, workspace hashes,
    changed files, proposal metadata, archive descriptors/novelty, and retained
    candidate metrics.
  - Current gap: paper-facing reports do not compare final or retained
    candidates against the seed/initial-pool programs. There is no syntactic
    distance, component-change, behavior-vector distance, evaluator-output
    distance, or task-specific functional-difference evidence proving that
    accepted candidates moved substantially away from the starting pool.
  - Required result: add paper-visible divergence reports with initial-pool
    baselines, syntax/code distance, changed-component summaries,
    metric/behavioral distance, and functional-difference artifacts before
    using AlphaEvolve-style discovery-distance wording.

- [ ] Track source/workspace deduplication and evaluation-cache evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: AlphaEvolve's generated-program database stores previously
    explored programs with evaluation results and program outputs under fixed
    search budgets, so repeated identical programs need an explicit
    resurfacing/reuse/re-evaluation policy.
  - Partial status: generated candidate ids include a workspace hash, and
    database/history restore paths validate unique program ids.
  - Current gap: the workspace hash is used for identity provenance, not for a
    pre-evaluation duplicate gate or evaluation-cache lookup. The paper index
    has no evidence for canonical source/workspace hash indexes, evaluator
    cache-key scope, cache hit/miss telemetry, stochastic re-evaluation policy,
    or replayable budget accounting for duplicate proposals.
  - Required result: add paper-visible run reports or manifest fields proving
    whether identical source/workspace proposals are skipped, reuse prior
    evaluation results, or are intentionally re-evaluated as new stochastic
    samples with documented budget effects.

- [ ] Track exploration/exploitation sampling-balance evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: AlphaEvolve's evolutionary database balances exploration and
    exploitation, improving the best programs while maintaining enough
    diversity to explore the search space.
  - Partial status: LibreEvolve exposes `explore_ratio`, `mixed` parent
    selection, explicit parent and inspiration strategies, MAP-Elites cells,
    island pools, metric/frontier/lineage/novelty/recency sampling paths, and
    selected parent/inspiration metadata in candidate history.
  - Current gap: paper-facing reports do not aggregate actual sampling
    decisions by explore/exploit branch, strategy fallback, source pool,
    island/cell/metric/lineage/descriptor contribution, repeated-selection
    rate, score improvement, diversity coverage, or budget impact. The paper
    index therefore cannot distinguish configurable sampling controls from
    measured AlphaEvolve-style balance under equal budgets.
  - Required result: add manifest/report evidence and validators for
    sampling-balance summaries, including per-run and per-generation decision
    counts, selected-program provenance, diversity and exploitation metrics,
    fallback accounting, and equal-budget comparisons of pure exploit, pure
    explore, default mixed, and metric/frontier/lineage variants.

- [ ] Record AlphaEvolve's automated-evaluator scope boundary.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 context, Related Work, and
    Discussion.
  - Requirement: AlphaEvolve explicitly scopes its main capability to problems
    with automated evaluators; it treats manual-experiment-heavy domains as
    out of scope and says LLM-provided idea evaluation is possible but not its
    optimized setting. The future bridge to AI Co-Scientist-style workflows is
    high-level idea feedback followed by an implementation stage where code
    execution provides machine feedback. The Discussion also says future
    progress depends on setting up more environments or problems with robust
    evaluation functions, making evaluator-environment readiness a paper-facing
    scope claim.
  - Current gap: the paper index and TODOs describe local validators,
    cascades, optional LLM feedback graders, proposal metadata, and
    DeepEvolve-style retrieval, but they do not yet require a paper-facing
    scope record that separates machine-gradeable executable evaluation from
    manual experimentation or pre-code natural-language idea review. They also
    do not require environment-setup evidence for robust evaluator design,
    automatable-domain boundaries, setup effort, or expected discovery value.
  - Required result: add benchmark/report metadata and documentation checks
    that label automated-evaluator readiness, manual-experiment exclusion,
    LLM-only idea-feedback stages, transition criteria into executable
    candidate evaluation, and robust-evaluator environment readiness before
    broad scientific-discovery, environment-scaling, or AI-Co-Scientist-style
    claims appear in paper-facing docs.

- [ ] Track AI-Co-Scientist representation boundary and hallucination claim.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Related Work.
  - Requirement: AlphaEvolve contrasts AI Co-Scientist's natural-language
    hypotheses and natural-language evaluation criteria with AlphaEvolve's
    code evolution and programmatic evaluation functions. The paper says this
    code/programmatic choice lets AlphaEvolve substantially sidestep LLM
    hallucinations and continue evolution for many time steps, while noting
    that the two approaches could be combined in future systems.
  - Current gap: paper-facing TODOs track automated-evaluator scope,
    machine-gradeable versus manual-experiment boundaries, optional LLM-only
    idea feedback, and structured proposal metadata. They do not yet require
    paper evidence that labels candidate representation mode, separates
    natural-language hypothesis criteria from executable programmatic
    criteria, or supports hallucination-resistance and long-horizon evolution
    claims with lifecycle evidence.
  - Required result: add paper/report evidence for representation mode,
    evaluation-criterion mode, executable-feedback linkage, hallucination-risk
    controls, long-horizon step counts, natural-language-to-programmatic bridge
    status, and README/ROADMAP wording that does not conflate generic idea
    metadata or LLM feedback graders with AlphaEvolve's Related Work
    distinction from AI-Co-Scientist.

- [ ] Track AlphaEvolve Related Work taxonomy and positioning evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Related Work.
  - Requirement: AlphaEvolve positions itself as execution-feedback code
    superoptimization and algorithm discovery, contrasts with pre-LLM
    enumeration/genetic-search/Monte-Carlo/deep-RL approaches, AlphaTensor,
    GPU-kernel and other LLM-agent optimizers, and broader AI-for-science
    systems. It says AlphaEvolve differs from most scientific-discovery
    methods by using programmatic hypothesis representations and evaluation
    metrics, calls continuous LLM fine-tuning through reinforcement learning
    and LLM-directed concept learning over high-performing programs adjacent
    ideas needing more investigation at AlphaEvolve scale, and frames
    mathematical witness/counterexample discovery as complementary to formal
    and informal proof discovery.
  - Current gap: the local paper index lists PDFs and selected inspiration
    relationships, while TODOs cover individual gaps such as FunSearch,
    AI-Co-Scientist, CodeEvolve, DeepEvolve, and domain benchmarks. It does
    not preserve the paper's Related Work taxonomy as evidence: source
    reference ids, method family, task stage, candidate representation,
    evaluator/evidence mode, proof-versus-witness status, comparison claim,
    complementary-mechanism status, and whether LibreEvolve implements,
    partially implements, or only cites the related approach as background.
  - Required result: add paper-facing related-work taxonomy records and
    validation for each relevant source/category, including method family,
    representation mode, evaluation/evidence mode, discovery stage, comparison
    text, complementary-mechanism status, local status, source page/section,
    and README/ROADMAP claim checks so the papers index distinguishes
    AlphaEvolve positioning evidence from flat bundled-paper availability.

- [ ] Track statistical hypothesis-testing semantics for evaluation cascades.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 3.1.
  - Requirement: the evaluation cascade is described as hypothesis testing:
    candidates should pass small-scale filters before main test cases only
    when earlier results are sufficiently promising, and repeated randomized
    initializations should provide evidence for noisy benchmark decisions.
  - Partial status: LibreEvolve has ordered staged validators with scalar and
    metric thresholds, samples, explicit seeds, retries, stage/sample budgets,
    and prompt-visible diagnostics.
  - Current gap: paper-facing evidence does not define statistical
    hypothesis-test policies, confidence intervals, p-values, sequential
    stopping rules, false-promotion/false-rejection budgets, or explicit
    small-scale-versus-main-test stage roles. Current cascades can be accurate
    threshold gates without proving AlphaEvolve-style hypothesis-testing
    promotion semantics.
  - Required result: add report/schema evidence for statistical cascade
    promotion decisions, including per-sample observations, test parameters,
    confidence or p-value outputs, sequential stopping diagnostics, and
    promotion/rejection linkage from small-scale filters to main test cases.

- [ ] Track qualitative LLM-feedback criterion provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: LLM-generated feedback can grade solution characteristics that
    are difficult to capture precisely in the user-provided evaluator, such as
    simplicity, and can either add those grades to the score dictionary or
    discard candidates that fail the criterion.
  - Partial status: LibreEvolve has optional LLM feedback graders with bounded
    prompts, parsed scores, normalized bounds/direction, weighted fitness
    deltas, discard/min-score behavior, failure policies, objective
    feedback-sourced metrics, feedback-index summaries, and calibration-report
    validators.
  - Current gap: paper-facing status does not require each grader to declare
    the qualitative property it represents, why that property is outside or
    impractical for the evaluator, whether it is intended as a score,
    discard gate, or both, or how the rubric/prompt, metric linkage,
    calibration evidence, and prompt-history rows prove AlphaEvolve-style
    qualitative feedback rather than generic post-evaluation LLM scoring.
  - Required result: add report/manifest evidence for qualitative feedback
    criteria: criterion label and rationale, rubric/prompt artifact hash,
    score-or-discard intent, metric linkage, calibration/task-suite linkage,
    prompt-history linkage, and validation examples for hard-to-code properties
    such as simplicity.

- [ ] Track natural-language proposal preambles separately from structured
      proposal metadata.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 3(c) and Section 2.3.
  - Requirement: AlphaEvolve examples can include explanatory natural-language
    reasoning before the SEARCH/REPLACE edit payload, while the edit itself is
    still carried by structured diff blocks.
  - Partial status: LibreEvolve captures bounded structured `IDEA`,
    `RATIONALE`, and `HYPOTHESIS` proposal metadata before mutation payloads.
  - Current gap: ordinary prose around valid diff/block/workspace-file
    sections is rejected with `malformed_diff:unconsumed_text`; this is stricter
    than the explanatory preamble shown before the Figure 3(c) diff example.
  - Required result: either support bounded explanatory preambles with
    redaction/provenance and tests, or keep the paper index, README, ROADMAP,
    and code TODOs explicit that LibreEvolve requires structured proposal
    metadata rather than arbitrary natural-language patch rationale.

- [ ] Track prompt example-copy diagnostics separately from diff syntax
      compatibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 3(b,c) and Section 2.3.
  - Requirement: AlphaEvolve prompts can include concrete current-program
    context and concrete SEARCH/REPLACE demonstrations, but accepted proposals
    should be edits to the sampled current program rather than copied
    illustrative prompt examples.
  - Partial status: LibreEvolve supports canonical SEARCH/REPLACE blocks,
    concrete prompt examples, and strict malformed-diff diagnostics.
  - Current gap: the paper index does not yet distinguish syntactic diff
    compatibility from evidence that prompt-only example fragments were not
    copied into accepted candidates. README says concrete examples reduce
    placeholder-copying mistakes, but no validator/report records prompt
    example labels, hashes, or copy-detection outcomes.
  - Required result: add paper-facing evidence for prompt-example inventories
    and acceptance diagnostics that detect copied placeholder/example
    sentinels across diff, full, and workspace mutations before treating
    prompt-example compatibility as AlphaEvolve-style current-program editing
    fidelity.

- [ ] Track multi-edit semantic consistency evidence separately from prompt
      instructions.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 3(b).
  - Requirement: the assembled AlphaEvolve prompt tells the model to make
    proposed SEARCH/REPLACE edits consistent with each other, including adding
    a newly referenced config variable when another edit uses it.
  - Partial status: LibreEvolve prompt instructions include comparable
    consistency guidance, and mutation/evaluation records can show parse
    errors, exact-match failures, syntax failures, evaluator failures, and
    rejection/admission outcomes.
  - Current gap: paper-facing evidence does not show that a multi-block
    proposal was analyzed for cross-edit coherence before accepted-result
    claims: newly introduced references, companion declaration/config/import
    edits, coupled evolved-block changes, unresolved symbols, missing
    dependency/resource edits, or evaluator failures classified as
    consistency-breakage rather than generic validation failure.
  - Required result: add report/schema evidence for multi-edit consistency:
    proposal id, prompt id, changed block/file ids, introduced/reference labels
    where analyzers exist, required companion-edit links, unresolved-reference
    diagnostics, evaluator-failure taxonomy linkage, accepted/rejected status,
    and README/ROADMAP wording that distinguishes prompt-only consistency
    instructions from checked AlphaEvolve-style coherent multi-edit proposals.

- [ ] Track Figure 3 supervised-learning example exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 3 presents a
    supervised-learning pipeline example with three abbreviated subfigures: a
    user-provided JAX/Jaxline file with evolve blocks and `evaluate`, an
    assembled prompt showing prior/current programs and scores, and an LLM
    response containing explanatory prose plus SEARCH/REPLACE edits.
  - Current gap: paper-facing TODOs track mutation parsing, prompt-context
    policy, preamble handling, and prompt-example-copy diagnostics. They do not
    preserve Figure 3 as its own paper exhibit with stable figure/subfigure IDs,
    exact source/prompt/output excerpt artifacts and hashes, displayed metric
    values, omitted-line/ellipsis policy, source PDF page/caption location,
    rendering/text artifact paths, or links from the displayed snippets to
    prompt-history, evaluator, candidate-history, and run artifacts.
  - Required result: add paper-facing Figure 3 exhibit records and validation:
    figure/subfigure IDs, source file and `evaluate` excerpt artifacts,
    rendered prompt excerpt artifact, LLM-output excerpt artifact, prompt score
    values, candidate/evaluator/run links, ellipsis/skipped-content policy,
    source/rendered artifact hashes, and README/ROADMAP wording that separates
    reproduced supervised-learning example evidence from generic prompt,
    mutation, and evaluator support.

- [ ] Track adaptive diff-versus-full mutation prompting.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: AlphaEvolve asks for SEARCH/REPLACE blocks for larger
    codebases, but for very short code or cases where a complete rewrite is
    more appropriate it can ask the model to output the full code block.
  - Partial status: LibreEvolve supports canonical diff parsing and a
    configured `full` mutation mode with full-file, file-section, and
    full-block replacement semantics.
  - Current gap: `Config.mutation_mode` is a run-wide enum. The prompt and
    parser contract do not adapt per candidate, code size, workspace shape, or
    observed failure mode, and paper-facing telemetry does not explain why a
    given proposal was requested as a diff or a full rewrite.
  - Required result: add paper-visible mutation-mode policy evidence for
    candidate-shape or task-shape selection, per-candidate prompt/output mode
    records, fallback/critique behavior, and benchmark examples proving the
    diff/full choice follows documented AlphaEvolve-style conditions rather
    than a fixed run configuration.

- [ ] Track LLM-constructed mutation-operator evidence beyond fixed edit
      modes.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Related Work.
  - Requirement: AlphaEvolve uses structured edit payloads, but the paper
    contrasts its LLM-guided mutation with evolutionary systems that depend on
    handwritten mutation/crossover operator sets.
  - Partial status: LibreEvolve supports canonical SEARCH/REPLACE diffs,
    configured full replacement modes, workspace file sections, and bounded
    topology commands.
  - Current gap: those are still fixed local edit surfaces selected by
    configuration and parser grammar. The paper index has no evidence that
    LibreEvolve declares, generates, selects, scores, or reports higher-level
    LLM-constructed operator families such as decomposition, algorithmic
    reformulation, recombination, multi-component refactoring, or
    benchmark-specific edit strategies.
  - Required result: add a paper-visible mutation-operator policy/report with
    proposal-level operator-family provenance, adaptive operator construction
    or selection evidence, parser/edit-grammar separation, and benchmark
    telemetry before claiming AlphaEvolve parity for replacing handwritten
    mutation operators with LLM-generated program mutations.

- [ ] Track creative-generation proposal diversity evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Section 4
    ablations.
  - Requirement: AlphaEvolve says SOTA LLMs digest previous solutions and
    propose new, diverse ways to improve them, and reports that stronger
    underlying LLMs improve system performance.
  - Partial status: LibreEvolve records selected parents and inspirations,
    prompt/call ids, proposal `idea`/`rationale`/`hypothesis` metadata,
    candidate outcomes, sampling strategies, bounded hypothesis summaries, and
    backend/model telemetry.
  - Current gap: the paper index has no evidence that generated proposals are
    diverse improvement approaches within a call, generation, batch, prompt
    context, or model/backend comparison. Existing proposal-scoring,
    initial-pool divergence, and mutation-operator TODOs do not require
    duplicate or near-duplicate proposal detection, idea-family diversity,
    semantic/task-output distances, or ablation linkage between proposal
    diversity and model quality.
  - Required result: add paper-visible proposal-diversity reports with
    proposal id, prompt/call id, parent/inspiration ids, backend model id,
    idea/operator-family labels, duplicate/near-duplicate status, code and
    semantic/task-output distance measures where available, accepted/rejected
    outcome, novelty contribution, and equal-budget/model ablation linkage
    before claiming AlphaEvolve-style creative generation from SOTA LLMs.

- [ ] Complete full validator-metadata rendering and provider-token prompt
  packing.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompt context can include program execution results, outputs,
    and scores from previous attempts.
  - Partial status: history records preserve stdout/stderr, retry-attempt
    records, aggregate syntax diagnostics, artifact metadata, and LLM feedback
    provenance. Prompt construction now renders bounded, redacted parent
    summaries for recent stage status, execution output, retry/sample attempts,
    and LLM grader feedback, plus bounded/redacted evaluator artifact path/hash
    summaries, skipped-artifact diagnostics, bounded stored-content excerpts
    for copied UTF-8 evaluator artifacts, opt-in bounded-file prompt rendering
    for copied UTF-8 artifact contents under the run directory, aggregate syntax
    diagnostics, metric-bound clamp diagnostics, malformed metric diagnostics,
    sample aggregation counts/policies, bounded general JSON-safe validator
    metadata fields not already covered by specialized renderers, and selected
    persisted LLM-grader failure-memory provenance. Binary and non-UTF-8
    artifacts are explicitly marked as having no prompt excerpt or renderable
    artifact content.
  - Current gap: prompt construction still renders only bounded selected
    validator metadata rather than full validator metadata and does not enforce
    provider-token section-priority prompt packing across all feedback/context
    sections. A
    run-level `prompt_max_chars` cap and heuristic
    `prompt_max_estimated_tokens` cap now bound final rendered mutation prompts
    and ensemble prompts before backend selection, and record prompt-size
    diagnostics. Those diagnostics now include
    `section_budget` with deterministic per-placeholder priorities, hashes,
    character counts, estimated tokens, required/optional totals, template
    overhead, required-section fit status, and heuristic character/token-budget
    packing decisions for omitted optional sections. Direct `PromptSampler`
    callers can now provide a manifest-safe provider token counter so the
    packer uses exact counts under `max_prompt_estimated_tokens` and records
    provider-token totals/counter provenance. The normal mutation path now
    discovers a common eligible-backend counter before constructing
    `PromptSampler`; this currently enables automatic exact counting only when
    every eligible mutation backend can use a locally installed OpenAI
    `tiktoken` counter, and otherwise persists
    `libreevolve.prompt_token_counter_capability.v1` diagnostics with the
    precise unavailable reason. The ensemble boundary now repeats that
    role-scoped common-counter discovery for mutation, critique, feedback,
    meta-prompt, registry-created, and custom role labels; when all eligible
    backends for a role share the local counter, the final prompt cap is
    enforced with exact provider-token counts and call telemetry records
    `prompt_token_count_policy`, `prompt_provider_tokens`,
    `prompt_token_limit_count`, and the role-specific capability record.
    `validate_prompt_section_budget_report()` now validates persisted
    `libreevolve.prompt_section_budget.v1` records for schema/policy shape,
    section counts, required/optional totals, section hash shape, packing
    decisions, cap-fit claims, and provider-counter boundary fields, but full
    provider-token section packing across all provider families and prompt
    roles is still absent from the normal evolution path. The AlphaEvolve table
    now scopes the prompt-token gap to selected-backend
    provider-token section packing outside mutation prompts plus exact counters
    across non-OpenAI provider families, rather than implying all tokenizer-aware
    fitting is absent. Backend specs and
    backend metadata can now carry
    `context_window_tokens` plus optional `reserved_output_tokens`; the
    ensemble subtracts the reserve, applies the derived heuristic prompt-token
    capacity before provider calls, and records the window, reserve, and
    derived capacity in call telemetry. Final manifests now record
    `runtime.prompt_section_packing` with schema
    `libreevolve.prompt_section_packing_coverage.v1` and embedded validation,
    making the mutation-only section-packing boundary and critique/feedback/
    meta-prompt final-boundary-only roles explicit.
  - Required result: add configurable/full validator-metadata prompt policy
    and automatic selected-backend provider-token section-priority packing
    across evaluator, feedback, artifact, and context prompt sections. The
    remaining paper gap is not persisted section-budget validation or
    role-scoped final-prompt exact token counting, and not manifest validation
    of current prompt section-packing role coverage.

- [ ] Model migration replay and async/pending-work controller resume for
  one-command archive resume.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: island-model population state should be reproducible enough
    that resumed AlphaEvolve-style searches continue from the same assignment
    policy, not only from the same retained programs.
  - Current evidence: live island assignment now advances only when
    `search_state_changed` is true, and the paper index documents that
    non-admitted `not_improving_cell` attempts do not consume island slots.
    Final manifests persist a compact `runtime.history.archive_state` snapshot
    with the current round-robin cursor, sequence counters, and per-island
    occupancy/elite counts, and `load_runtime_archive_state_snapshot()`
    validates that compact manifest field before future resume use.
    `load_archive_event_records()` now validates persisted migration event rows
    as checked audit data.
    `IslandModel.restore_cursor_state()` now applies the compact cursor/counter
    subset to a live island model. `ProgramDatabase(...,
    archive_state_snapshot=...)` now applies that validated cursor/counter
    subset during database construction and records a cursor-only restore
    policy in the startup manifest.
    Direct `evolve()` calls now accept `runtime_archive_state_snapshot`, and
    CLI runs can load the same compact cursor/counter snapshot with
    `--restore-archive-cursor-from-manifest`.
    Manifest snapshots now also persist `archive_contents` with per-island
    MAP-Elites cells, elite-program ids, descriptor policy metadata, and archive
    configuration. `load_archive_restore_bundle()` combines that manifest state
    with accepted `history.jsonl` records, and `ProgramDatabase(...,
    archive_state_snapshot=..., archive_programs_by_id=...)` restores live
    cells and elite archives from the resulting bundle.
    New archive-state snapshots now advertise
    `snapshot_persisted_cursor_and_full_archive_restore_supported`, while
    validators still accept the earlier cursor-only status for legacy manifest
    restore.
    The paper index now reflects that CLI full-runtime restore composes the
    compatible archive restore bundle with runtime RNG, LLM scheduler, budget,
    and controller-budget replay surfaces; it no longer treats generic
    full-resume wiring as open for these synchronous checked surfaces.
    `policies.archive_identity.resume_status` now advertises
    `manifest_archive_state_restore_supported`, lists restored archive
    surfaces, and explicitly marks migration-event replay as
    `audit_only_not_restore_engine`. Focused database tests prove full archive
    restore uses the restored round-robin cursor for the next admission.
    Archive snapshots now include validated `migration_replay` metadata that
    states migration events are not replayed as a restore engine, archive
    contents cover current migrated placements, and controller pending work is
    not restored. Final manifests now include
    `runtime.history.archive_event_replay_audit`, which validates migration
    rows, replays final admitted migration placements, and compares that
    audit-only partial event view with `archive_contents`. The validators
    reject replay-engine overclaims.
    `validate_archive_event_replay_audit()` now validates the audit result,
    including schema/status, audit-only and no-restore-engine flags, event and
    placement count consistency, retained mismatch shape, mismatch retention
    limits, verified/absent status invariants, and required audit-boundary
    limitations.
  - Current gap: cursor and archive-content restore are implemented, but
    migration placement rows are reconciled only as audit evidence rather than
    replayed as an ordered restore engine. Completed manifests now include
    `runtime.history.controller_state`, a terminal drained-state snapshot for
    the synchronous controller with zero queued/running proposals, evaluations,
    in-flight LLM calls, and pending archive admissions at finalization plus a
    compact controller-budget event-stream summary. Async or mid-generation
    controller/pending-work state is still absent from one-command resumed
    experiment traces.
    `libreevolve.controller_state_artifact_inventory.v1` now verifies the
    terminal synchronous controller event stream against the manifest artifact
    record and disk file, including safe relative path checks, file existence,
    SHA-256, byte count, strict JSONL event count, last sequence/kind,
    per-record status, and a stable records hash.
    `libreevolve.controller_state_validation.v1` now verifies the terminal
    drained synchronous boundary and reports pending-work or async/full-replay
    overclaims as manifest validation failures.
  - Required result: apply or explicitly model migration-event replay, add
    controller/pending-work resume state, and add paper-visible resume/replay
    tests covering below-threshold, non-admitted, elite-only, and
    cell-replacement cases. The remaining paper gap is not terminal controller
    event-stream artifact verification or terminal drained-state validation.

- [ ] Extend meta-prompt context policy beyond validated current fields.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt instructions and prompt context can be improved through
    meta-prompt evolution.
  - Current evidence: prompt programs now persist validated
    `libreevolve.prompt_context_policy.v1` state separate from template text.
    The policy can disable optional prompt channels and override deterministic
    prompt-packing section priorities, and it can select safe enum-valued
    mutation-instruction variants for rendered mutation-format guidance.
    `mutation_instruction_include_example` can keep or remove the built-in
    mutation-format example block while preserving the core format rules. It
    can select safe parent metric names for the `{parent_metrics}` channel and
    cap or suppress individual parent metric entries by metric name before
    rendering. It
    now validates the meta-prompt-visible
    `libreevolve.meta_prompt_context_policy_capabilities.v1` map against the
    actual `libreevolve.prompt_context_policy.v1` keys before rendering
    evidence, rejecting duplicate, missing, malformed, or unsupported
    advertised fields. It
    can also set `parent_code_paths` to select/order safe mutable
    parent-workspace files, `parent_code_required_terms` and
    `parent_code_excluded_terms` to filter them by safe path/content terms, and
    `parent_code_order_policy` with optional `parent_code_ranking_terms` to
    rank selected parent files by deterministic term overlap before rendering.
    `parent_code_limit` can cap how many ordered mutable parent files render,
    including `0` to suppress mutable parent file bodies while retaining
    diagnostics. `parent_code_max_chars_by_path` can cap individual rendered
    parent file bodies by safe candidate-relative path before the aggregate
    parent-code cap applies.
    `parent_code_max_chars` to cap or suppress the
    required parent-code channel while retaining an explicit omission marker and
    `libreevolve.parent_code_policy.v1` diagnostics for source,
    requested/rendered/omitted/missing path policy, term-filter policy,
    order policy, render-count limit policy, per-file content cap policy, cap,
    truncation mode (`head` or `head_tail`), character counts, and hashes. It
    can also set `proposal_metadata_enabled` to override whether proposal
    metadata instructions and parsing run for the selected prompt arm while
    preserving run-level defaults when unset. It
    can also select which parent-feedback subsections render, including stage
    summaries, execution output, validator diagnostics/artifacts, program
    outputs, proposal metadata, and LLM grader feedback, and
    `feedback_section_order` can deterministically reorder those
    selected/rendered parent-feedback subsections while appending unspecified
    sections in default order. `feedback_section_max_chars_by_name` can suppress
    or cap individual feedback subsections before the aggregate feedback cap.
    `llm_feedback_fields`
    can further select rendered safe LLM-grader fields within that section, and
    `llm_feedback_max_chars_by_field` can cap or suppress those selected
    LLM-grader fields before rendering.
    `inspiration_strategy` can override upstream inspiration sampling strategy
    for that prompt program using the same safe strategy enum as config.
    `inspiration_sample_count` can override the upstream sampled inspiration
    count before plugin context and prompt rendering, separately from the
    rendered inspiration cap. `inspiration_required_metric` can filter the
    upstream inspiration pool to programs carrying a manifest-safe metric name
    before plugin context and prompt rendering. `inspiration_excluded_metrics`
    can filter out upstream inspirations carrying any listed manifest-safe
    metric names before plugin context and prompt rendering.
    `inspiration_fitness_threshold` can filter upstream inspirations by finite
    fitness min/max bounds before plugin context and prompt rendering.
    `inspiration_metric_thresholds` can filter upstream inspirations to programs whose numeric metric values
    satisfy safe min/max bounds before plugin context and prompt rendering.
    `inspiration_metric_ranking` can rank the upstream inspiration pool by a
    numeric metric in maximize/minimize order before final selection.
    `validator_diagnostic_groups` can select rendered bounded validator
    diagnostic groups inside validator diagnostics, and `proposal_fields` can
    select rendered safe proposal metadata fields, and
    `proposal_max_chars_by_field` can cap or suppress those proposal fields
    before rendering, and `stage_summary_fields`
    can select rendered safe stage-summary fields within stage-summary
    feedback, and `stage_summary_max_chars_by_field` can cap or suppress those
    stage-summary fields before rendering, and `execution_output_fields` can select rendered safe
    execution-output fields within execution-output feedback and stage-summary
    IO lines, and `execution_output_max_chars_by_field` can cap or suppress
    rendered `stdout`, `stderr`, and `error` text independently before those
    fields are included, and `sample_retry_fields` can select rendered safe sample/retry
    diagnostic fields, and `sample_retry_max_chars_by_field` can cap or
    suppress selected sample/retry diagnostic text fields before rendering, and `program_output_fields`
    can select rendered safe program-output fields within program-output
    feedback, and `program_output_max_chars_by_field` can cap or suppress
    selected program-output text fields before rendering, and `validator_artifact_fields` can select rendered safe
    validator-artifact fields, and `validator_artifact_max_chars_by_field` can
    cap or suppress selected validator-artifact text fields before rendering, and `validator_artifact_content_fields` can
    select nested bounded artifact-content fields, and
    `validator_artifact_content_mode`,
    `validator_artifact_content_max_bytes`, and
    `validator_artifact_content_max_chars` can override artifact-content
    rendering policy and caps, and
    `validator_skipped_artifact_fields` can select rendered safe
    skipped-artifact fields, and
    `validator_skipped_artifact_max_chars_by_field` can cap or suppress selected
    skipped-artifact text fields before rendering, and
    `validator_metadata_keys` can select safe keys inside the validator
    metadata summary. `validator_metadata_limit` can cap or suppress the
    number of metadata-summary items before rendering.
    `validator_metadata_max_chars_by_key` can cap or
    suppress selected validator metadata summary values before rendering.
    `evaluator_path_fields` can select safe validator path provenance fields,
    and `evaluator_path_max_chars_by_field` can cap or suppress selected path
    fields before rendering.
    `evaluator_dependency_fields` can select safe validator dependency-policy
    fields, including derived file paths, hashes, and redaction flags, and
    `evaluator_dependency_max_chars_by_field` can cap or suppress selected
    dependency fields before rendering.
    `evaluator_stage_fields` can select safe derived stage-context fields, and
    `evaluator_stage_max_chars_by_field` can cap or suppress selected stage
    fields before rendering.
    `evaluator_workspace_fields` can select safe evaluated workspace
    provenance fields, including primary file, file count, and bounded file
    list, and `evaluator_workspace_max_chars_by_field` can cap or suppress
    selected workspace fields before rendering.
    `syntax_error_fields` can select safe fields inside
    syntax-error diagnostics, and `syntax_error_max_chars_by_field` can cap or
    suppress selected syntax-error text fields before rendering, and
    `metric_bound_fields` can select safe fields
    inside metric-bound diagnostics, and `metric_bound_max_chars_by_field` can
    cap or suppress selected metric-bound text fields before rendering.
    `configured_stage_check_fields` can select
    safe fields inside configured-stage check diagnostics, and
    `configured_stage_check_max_chars_by_field` can cap or suppress selected
    configured-stage text fields before rendering.
    `stage_metric_threshold_fields` and `artifact_output_check_fields` can
    select nested safe fields inside configured-stage metric-threshold and
    artifact-output checks, and `stage_metric_threshold_max_chars_by_field` can
    cap or suppress selected nested metric-threshold text fields before
    rendering. `artifact_output_check_max_chars_by_field` can cap or suppress
    selected nested artifact-output check text fields before rendering.
    `malformed_metric_fields` can select safe fields inside malformed-metric
    diagnostics, and `malformed_metric_max_chars_by_field` can cap or suppress
    selected malformed-metric text fields before rendering.
    `metric_aggregation_fields` can select safe fields inside
    metric-aggregation diagnostics, and
    `metric_aggregation_max_chars_by_field` can cap or suppress selected
    metric-aggregation text fields before rendering.
    `synthetic_metric_fields` can select safe fields inside synthetic
    failure-metric diagnostics, and `synthetic_metric_max_chars_by_field` can
    cap or suppress selected synthetic metric text fields before rendering.
    `materialization_error_fields` can select safe fields inside
    materialization-error diagnostics, and
    `materialization_error_max_chars_by_field` can cap or suppress selected
    materialization-error text fields, including typed reason/path fields,
    before rendering.
    `validator_boundary_fields` can select
    safe fields inside validator-boundary diagnostics.
    `validator_boundary_max_chars_by_field` can cap or suppress selected
    validator-boundary text fields before rendering.
    `validator_resource_limit_fields` can select nested safe resource-limit
    fields inside validator-boundary diagnostics, and
    `validator_resource_limit_max_chars_by_field` can cap or suppress selected
    nested resource-limit text fields before rendering.
    `validator_budget_fields` can select stage/sample budget diagnostic fields
    inside execution diagnostics, and
    `validator_budget_max_chars_by_field` can cap or suppress selected budget
    fields before rendering.
    `validator_env_fields` can select value-free validator environment
    diagnostic fields, and `validator_env_max_chars_by_field` can cap or
    suppress selected environment fields before rendering.
    `execution_diagnostic_groups` can select safe execution-diagnostic
    subgroups before subgroup field allowlists are applied.
    `validator_stdin_fields`
    can select safe fields inside validator-stdin diagnostics, and
    `validator_stdin_max_chars_by_field` can cap or suppress selected
    validator-stdin text fields before rendering.
    `diagnostic_output_fields` can select safe fields inside diagnostic-output
    diagnostics, and `diagnostic_output_max_chars_by_field` can cap or
    suppress selected diagnostic-output text fields before rendering.
    `timeout_cleanup_fields` can select safe fields inside
    timeout-cleanup diagnostics, and
    `timeout_cleanup_max_chars_by_field` can cap or suppress selected
    timeout-cleanup text fields before rendering.
    `prompt_format_weights` can override configured stochastic prompt-format
    alternative weights for safe configured markers, and `context_source_paths` can select and order
    loaded local context sources by safe problem-relative path.
    `context_source_max_chars` can cap rendered text for each selected local
    context source and records original, rendered, and omitted character counts
    per source. `context_source_truncation` can choose deterministic `head` or
    `head_tail` retention under that per-source cap.
    `context_source_order_policy` can keep selected source order or rank
    selected local context sources by deterministic task-term overlap against
    rendered source text while recording scores, query source, query-term
    hash/count, configured query terms when present, and a ranking hash.
    `context_source_ranking_terms` can provide explicit safe ranking terms
    instead of deriving them from the task description.
    `context_source_required_terms` can keep only sources whose
    loaded content contains every listed safe term, and
    `context_source_excluded_terms` can omit sources whose loaded content
    contains any listed safe term before ranking and limiting; diagnostics
    record required/excluded terms, omitted paths, match/filter counts, and a
    selection hash. `context_source_limit` can cap how many ordered local
    context sources render after path selection and ranking, including
    suppressing them with a zero limit, and records pre-limit order, omitted
    paths, selected count, omitted count, and a selection hash.
    `recent_failure_limit` can cap rendered recent failure-memory records,
    including suppressing that block with a zero limit, and records available,
    rendered, and omitted counts. `recent_failure_selection_policy` can choose
    `recent`, `oldest`, `lowest_score`, or `highest_repetition` retained
    failure-memory records before that render cap is applied, and records selector/selection
    semantics. `recent_failure_required_errors` can filter retained
    failure-memory records by exact safe `error` or `diff_error` labels before
    selection and limiting, and records required labels, match count, filtered
    count, and policy. `recent_failure_excluded_errors` can omit retained
    failure-memory records carrying exact safe `error` or `diff_error` labels
    before score filtering, selection, and limiting, and records excluded
    labels, filtered count, and policy. `recent_failure_required_changed_files`
    can filter retained failure-memory by safe exact `changed_files` paths
    before score filtering, selection, and limiting, and records required
    paths, match count, filtered count, and policy.
    `recent_failure_excluded_changed_files` can omit retained failure-memory
    carrying safe exact `changed_files` paths before score filtering,
    selection, and limiting, and records excluded paths, filtered count, and
    policy. `recent_failure_required_stage_names` can filter retained
    failure-memory by safe exact evaluation stage names, and
    `recent_failure_excluded_stage_names` can omit retained failure-memory
    carrying safe exact evaluation stage names before repetition/score
    filtering, selection, and limiting; diagnostics record required/excluded
    stage names, match counts, filtered counts, and policies.
    `recent_failure_required_terms` and `recent_failure_excluded_terms` can
    filter retained failure-memory by safe text terms in the failure evidence
    before repetition/score filtering, selection, and limiting, recording
    configured terms, match/filter counts, and policies when configured.
    `recent_failure_repetition_threshold` can filter retained
    failure-memory by integer `repetition_count` `min`/`max` bounds before
    score filtering, selection, and limiting, and records normalized bounds,
    match count, filtered count, and policy. `recent_failure_score_threshold` can filter retained
    failure-memory by finite score `min`/`max` bounds before selection and
    limiting, and records normalized bounds, match count, filtered count, and
    policy. `recent_failure_max_chars_by_field` can cap or suppress selected
    recent failure-memory fields before rendering.
    `inspiration_limit` can cap rendered selected
    inspirations, including suppressing all inspiration rendering with a zero
    limit, and records available, rendered, and omitted counts.
    `extra_context_max_chars` can cap already validated/redacted plugin
    `extra_context` text and records input, rendered, and omitted character
    counts. `plugin_context_enabled: false` can suppress plugin
    `build_extra_context()` and `prompt_context_metadata()` calls for a selected
    prompt arm while recording disabled per-plugin provenance.
    `plugin_context_allowlist` can select which plugin identity labels may run
    prompt-context hooks for that prompt arm, while non-selected plugins are
    skipped with deterministic provenance before hook execution.
    `plugin_context_excluded_labels` can omit selected plugin identity labels
    before prompt-context hooks run, recording
    `excluded_by_prompt_context_labels` visibility and the configured label
    policy.
    `plugin_context_order` can reorder selected plugin prompt-context sections
    by safe plugin identity labels before aggregate prompt packing.
    `plugin_context_required_terms` and `plugin_context_excluded_terms` can
    filter bounded plugin context text by safe terms before prompt visibility,
    recording selected status, missing required terms, matched excluded terms,
    and a selection hash.
    `plugin_context_ranking_terms` can rank prompt-visible plugin context
    sections by deterministic term overlap before render-count limiting,
    recording configured ranking terms, term hash/count, score, rank, previous
    rank, candidate count, and ranking hash.
    `plugin_context_limit` can cap how many ordered plugin context sections
    become prompt-visible after allowlist, term filtering, and ordering,
    recording source limit, pre-limit count, selected/omitted counts, rank,
    selected status, and a selection hash.
    `plugin_context_max_chars` can globally cap each plugin context section
    before prompt visibility, recording the global policy cap, per-label cap,
    effective cap, original character count, and prompt truncation status.
    `plugin_context_truncation` can choose deterministic `head` or
    `head_tail` retention under those plugin-context caps, and plugin-context
    records persist the applied content policy.
    `plugin_context_max_chars_by_label` can cap rendered plugin prompt-context
    text by plugin identity label before aggregate prompt packing applies.
    Generated prompt diagnostics record the applied policy hash, selected
    instruction variant, selected inspiration strategy and sample-count
    overrides, selected feedback sections, selected LLM-grader
    feedback fields, selected proposal fields, selected stage-summary fields, selected execution-output
    fields, selected sample/retry
    diagnostic fields and caps, selected program-output fields and caps, selected
    validator-artifact fields and caps, selected artifact-content nested fields,
    selected artifact-content policy overrides,
    selected skipped-artifact fields,
    selected validator diagnostic groups, selected validator
    metadata keys, selected parent metric names/caps, selected syntax-error fields, selected metric-bound fields,
    selected configured-stage check fields, selected configured-stage nested
    fields, selected malformed-metric fields,
    selected metric-aggregation fields, selected synthetic metric fields,
    selected materialization error reason/path fields,
    selected validator-boundary fields,
    selected validator budget fields, selected validator resource-limit fields,
    selected execution-diagnostic subgroups, selected validator-stdin fields,
    selected diagnostic-output fields,
    selected timeout-cleanup fields, prompt-format weight
    overrides, context source selection, term filters, render-count caps,
    content caps, truncation policy, and ordering policy,
    recent failure-memory selection and text-term filtering, and inspiration selection, plugin extra-context
    cap diagnostics, plugin-context generation, excluded-label policy, term filters, ranking terms, render-count limits, global plugin caps, truncation policy, and ordering policy, and replacement hashes;
    generated-candidate metadata records required-metric inspiration filtering
    plus metric-threshold inspiration filtering with pool, matching, filtered,
    threshold-bound, ranking-policy, ranked, and selected counts;
    `prompt_history.jsonl` persists `context_policy` plus `context_policy_sha256`; replay validates
    immutable policy state; meta-prompt provider output can return a strict
    JSON object with a revised `template` plus optional `context_policy`; and
    meta-prompt mutation requests now include a compact context-policy
    capability manifest plus per-prompt non-default context-policy previews in
    the bounded redacted prompt-performance evidence. Final manifests now
    include `runtime.prompt_context_policy_coverage` with schema
    `libreevolve.prompt_context_policy_coverage.v1` and embedded validation
    against the current policy schema/capability map, while keeping
    `alphaevolve_context_policy_complete` false and listing unsupported
    retrieval/summarization, learned ranking, and semantic context-selection
    surfaces. The AlphaEvolve table now scopes the remaining prompt-context
    gap to live/retrieval/semantic context selection and deeper per-field policy
    beyond the current validated structured context-policy surface rather than
    implying that structured prompt-context policy is absent.
    Remaining context rendering is still mostly fixed in `PromptSampler` and related
    code: plugin context shaping beyond enable/disable, allowlist/excluded-label
    selection, ordering, safe term filtering, deterministic term ranking,
    render-count limiting, global/per-label caps, truncation, parent-metric selection/caps, and required parent-code file selection/term filtering/deterministic ordering/render-count limiting/per-file content capping/character capping/truncation-mode selection,
    retrieval/summarization beyond deterministic source selection/ranking/count caps, and deeper
    per-field policy inside selected validator diagnostic groups beyond
    metadata-summary key selection, parent-metric selection/caps, syntax-error field selection, and
    proposal field selection, and
    stage-summary field selection, and
    execution-output field selection, and
    sample/retry diagnostic field selection, and
    program-output field selection, and
    validator-artifact field selection, and
    artifact-content nested field selection, and
    artifact-content policy override selection, and
    skipped-artifact field selection, and
    metric-bound field selection, configured-stage check field selection, and
    configured-stage nested field selection, and malformed-metric field
    selection, and materialization-error field selection, and
    metric-aggregation field selection, and synthetic metric
    field selection
    and execution-diagnostic subgroup selection, and validator-boundary field
    selection, and validator budget field selection, and validator resource-limit field
    selection, and validator-stdin field selection, diagnostic-output field
    selection, execution-output, sample/retry, program-output, and validator-artifact field caps,
    and timeout-cleanup field selection are
    not yet owned by prompt-program policy. Prompt-program policy can override
    upstream inspiration strategy, sampled inspiration count, safe
    required/excluded-metric filtering, fitness-threshold filtering, metric-threshold filtering, metric ranking, and rendered
    inspiration count, but not richer upstream inspiration selection policy.
  - Required result: extend prompt-program context policy beyond optional
    channel disabling, packing-priority overrides, current character caps,
    parent-code file selection, term filtering, deterministic ordering, render-count limiting, and per-file content capping, and truncation-mode selection so meta-prompt evolution
    can safely alter source selection, retrieval/summarization, inspiration and
    feedback field policy, and additional instruction/context controls while preserving
    safe template rendering and auditability. The remaining paper gap is not
    manifest-visible validation of the current meta-prompt-tunable context
    policy surface.

- [ ] Calibrate meta-prompt rewards and add prompt-lineage ablation evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.6, and 4.
  - Requirement: prompt-improvement claims should be backed by reward signals
    and ablation evidence that separate prompt-program lineage effects from
    candidate, evaluator, model, and stochastic search noise.
  - Current evidence: prompt programs have deterministic ids, lineage, usage
    counts, reward sums, normalized mean rewards, `absolute` and `improvement`
    child-score reward modes, reward-policy compatibility checks during
    history replay, and UCB-style prompt-arm selection. Meta-prompt mutation
    requests include bounded prompt-performance evidence with reward policy,
    selected prompt statistics, latest candidate outcome, prompt-arm summaries,
    and recent failure summaries.
  - Required result: add calibrated prompt-specific reward signals,
    prompt-lineage ablation/report artifacts, and tests showing prompt-policy
    attribution across comparable runs before claiming AlphaEvolve-grade
    meta-prompt scoring or prompt-improvement evidence.

- [ ] Separate prompt-database parity from local prompt-arm selection.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 describes meta
    prompt evolution as an additional prompt-generation step whose
    instructions/context are co-evolved in a separate database analogous to the
    solution programs.
  - Current evidence: LibreEvolve has `PromptDatabase`, `prompt_history.jsonl`,
    lineage-bearing prompt programs, UCB-style prompt selection, prompt-score
    replay checks, and optional LLM template/context-policy mutation. The
    current prompt database does not share the solution database's MAP-Elites
    archive semantics, island/migration policy, descriptor/objective indexes,
    archive-event stream, or async/pending-work resume surface.
  - Required result: add paper-facing evidence for a prompt database policy
    that is explicitly solution-database-equivalent, or keep prompt-program
    claims scoped to local prompt-arm selection plus history/reward tracking
    rather than AlphaEvolve's separate co-evolved prompt database.

## Local Paper Corpus Issues

- [ ] Harden benchmark implementations beyond smoke-example fidelity.
  - Paper evidence: the AlphaEvolve paper's matrix task searches low-rank tensor
    decompositions with randomized initializations and exact verification;
    Appendix B.12 reports circle packing in the unit square for `n = 26` and
    `n = 32`; Figure 8 compares ablations by compute-budget fraction.
  - Current evidence: the checked-in matrix example validates only a 2x2 Python
    `matmul2` function and counts AST multiplication nodes inside that
    function. It now rejects known import/library delegation, module-level
    dead-code counters, and fixed-three-case lookup shortcuts, but it remains a
    smoke fixture rather than an operation/rank-faithful tensor benchmark. The
    circle example matches the fixed-26 unit-square objective family, but there
    is no benchmark harness for repeated seeds, SOTA thresholds, saved
    construction artifacts, visual/JSON outputs, or equal-budget ablation
    curves. `libreevolve.benchmark_hardening.v1` now defines a hardening
    contract for protected signals, shortcut threats linked to protected
    signals, detector strategies, passed negative fixtures, and hashed
    hardening artifacts.
    `libreevolve.benchmark_hardening_artifact_inventory.v1` now verifies
    negative fixture and hardening artifact records against concrete files
    under an explicit artifact root, checking safe relative paths, existence,
    SHA-256 hashes, byte counts, per-record statuses, and aggregate
    missing/mismatch/invalid counts, but no real benchmark runner emits those
    reports yet.
    `libreevolve.example_benchmark_scope.v1` now validates a shipped-example
    scope registry that labels `hello_world`, `sorting`, `workspace_math`,
    `matrix_multiplication`, and `circle_packing` as smoke-only and not
    AlphaEvolve-comparable, but it is an exclusion boundary rather than a real
    benchmark harness. The `workspace_math` smoke fixture now covers a nested
    package, declared JSON data, and a binary static seed asset without making
    benchmark claims. The scope registry is validated in focused tests and by
    smoke hardening evidence, but not yet by the routine paper-manifest/docs
    validation gate that reviewers run for paper-facing evidence.
    `validate_benchmark_evidence_scope()` now cross-checks
    hardening reports against the matching scope record and optional hardening
    artifact inventory, rejecting smoke-only example promotion, paper-claim
    scope mismatches, and inconsistent inventory evidence.
    The AlphaEvolve paper-index row now describes the checked-in circle task as
    a circle-packing smoke fixture, matching the Appendix B registry's
    `implemented_smoke` status rather than treating it as a benchmark-grade
    packing result.
    `write_matrix_smoke_hardening_bundle()` now emits real hardening files for
    the shipped `matrix_multiplication` smoke fixture: negative-fixture JSON,
    detector log, hardening report, artifact inventory, summary, and
    smoke-scope validation, all while preserving `alphaevolve_comparable:
    false`. `alphaevolve_appendix_b.json` enumerates the thirteen Appendix B
    constructive-math families, but it is still a coverage/status registry:
    twelve families are `planned`, every paper-result family keeps
    `target_baseline.value` null, and its construction/certificate artifact
    schemas are labels for expected evidence rather than executable validators,
    reported construction payloads, SOTA numeric thresholds, or verification
    scripts. Appendix B says the data and verification code for all reported
    constructions appear in the accompanying Google Colab, so a status ledger
    without construction-data exports and runnable verifier-code artifacts is
    still below the paper's publication-evidence surface.
  - Required result: distinguish smoke examples from benchmark fixtures in docs,
    add operation/rank-aware matrix benchmark validation beyond the current
    2x2 smoke checks, connect hardening reports and executable artifact/
    certificate validators for geometric and constructive-math constructions,
    add Colab-equivalent construction-data and verifier-code exports for the
    Appendix B families, validate the shipped example-scope registry in the
    standard paper-facing gate, and create repeatable benchmark reports tied to
    AlphaEvolve target families. The remaining paper gap is generating those
    anti-gaming and verification-data evidence files from benchmark-grade
    tensor/geometric/constructive-math fixtures, not emitting matrix smoke
    hardening evidence, verifying declared hardening files once a report names
    them, or preventing declared hardening evidence from overriding the
    smoke-only scope registry.

- [ ] Track Figure 5 construction-exhibit provenance as paper evidence.
  - Paper evidence: AlphaEvolve Figure 5 presents selected SOTA-breaking
    mathematical construction examples with branch labels, problem labels,
    before/after metric values, and rendered construction visuals such as
    hexagon outer-edge, max-distance/min-distance, and sum-of-radii examples.
  - Current gap: the paper-facing Appendix B registry is family/status
    coverage, and existing TODOs ask for construction-data/verifier exports,
    aggregate outcome reports, benchmark hardening, and result-version
    provenance. There is no paper-evidence row or report schema that maps
    Figure 5 exhibits to selected Appendix B results, previous-best/result
    values, branch/problem labels, visual artifact paths/hashes, rendering
    parameters, source Colab cells/artifacts, or verifier links.
  - Required result: add Figure 5-style exhibit metadata with stable exhibit
    IDs, Appendix B family/parameter links, previous/current metric values with
    direction/unit, previous-best source, construction payload, rendered
    visual/JSON artifacts with hashes, verifier/certificate links, and
    documentation that separates reproduced paper exhibits from broader
    Appendix B family coverage.

- [ ] Track Figure 5 versus Appendix B.12 sum-of-radii precision evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 5 displays the
    sum-of-radii improvement as `2.6340 -> 2.6358`. Appendix B.12 and
    Figure 14 describe the `n = 26` unit-square circle-packing improvement as
    `2.634` to `2.635`.
  - Current gap: paper-facing TODOs track broad Figure 5 exhibit provenance
    and B.12-B.13 packing rows, but they do not force reports to preserve
    source-specific numeric strings or reconcile the Figure 5 precision against
    the appendix text/caption precision. README/ROADMAP wording currently
    follows the Appendix B.12 `2.635` value and could lose the Figure 5
    `2.6358` display.
  - Required result: add paper/report evidence for this packing result with
    per-source value records: source section/figure id, displayed previous and
    current value strings, normalized numeric values, rounding or truncation
    policy, chosen canonical claim value, and README/ROADMAP wording that keeps
    Figure 5 display precision separate from Appendix B.12/Figure 14 wording.

- [ ] Track Appendix B figure-level construction provenance for Figures 10-14.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B presents
    displayed construction figures beyond Figure 5: Figure 10 for Erdos
    minimum overlap, Figure 11 for regular-hexagon packings, Figure 12 for
    maximum/minimum-distance point sets, Figure 13 for Heilbronn variants, and
    Figure 14 for circle and rectangle packing sum-of-radii improvements.
  - Current gap: paper-facing Appendix B status is family/status coverage, and
    existing TODOs require construction-data/verifier exports, aggregate
    outcome reports, result-version provenance, and Figure 5 exhibit mapping.
    There is no evidence row or report schema mapping Figures 10-14 to
    figure/subfigure labels, family/parameter rows, previous/current values,
    figure-caption values, construction payloads, visual artifact paths/hashes,
    rendering parameters, source Colab cells/artifacts, or verifier links.
  - Required result: add Appendix B figure-exhibit metadata with stable
    figure/subfigure IDs, family and parameter links, previous/current metric
    values with direction/unit, previous-best source, construction payload,
    rendered visual/JSON artifacts with hashes, verifier/certificate links,
    and documentation that separates appendix figure reproduction from broad
    Appendix B family coverage and main-text Figure 5 exhibit coverage.

- [ ] Track Appendix B per-result metric and value evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.1-B.13 reports
    heterogeneous result claims: autocorrelation constants, the uncertainty
    constant `C4`, Erdos minimum overlap, finite-set sum/difference ratios,
    regular-hexagon outer side lengths, max/min-distance ratios, Heilbronn
    minimum areas, the dimension-11 kissing lower bound, and circle/rectangle
    sum-of-radii values. These claims use different parameter tuples, metric
    definitions, inequality directions, previous bounds, reported values, and
    source citations or figure/caption links. They also require different
    construction representations, including step functions, polynomial or
    coefficient lists, finite integer sets, point coordinates, kissing
    configurations, and geometric packing placements.
  - Current gap: paper-facing Appendix B status is family/status coverage, and
    existing TODOs ask for construction-data/verifier exports, aggregate
    outcomes, result-version rows, Figure 5 and Figures 10-14 exhibit
    mappings, and the kissing-number proof certificate. There is no normalized
    paper-evidence table that maps each text-level Appendix B claim to its
    metric formula or definition, parameter tuple, upper/lower or
    maximize/minimize semantics, previous-best value and source, reported
    AlphaEvolve value, manuscript section/figure location, and linked
    construction representation schema plus construction/verifier artifact.
  - Required result: add paper/report evidence for Appendix B.1-B.13 result
    rows with stable result ids, family and parameter metadata, exact metric
    names/formulas, units or bound semantics, optimization direction,
    previous-best citations and values, AlphaEvolve reported values, source
    section/figure/caption links, construction-type schemas and payload hashes
    for step functions, coefficients, finite sets, coordinates, and packing
    placements, verifier artifact hashes, and README/ROADMAP wording that
    separates text-level numeric claim provenance from aggregate coverage and
    figure reproduction.

- [ ] Track Appendix B.1-B.3 autocorrelation step-function evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.1-B.3 gives
    three separate autocorrelation/autoconvolution claims with different
    constants and proof directions: a `600`-interval step function on
    `[-1/4, 1/4]` proving `C1 <= 1.5053`, a `50`-interval step function on the
    same domain proving `0.8962 <= C2`, and a `400`-interval step function on
    the same domain proving `C3 <= 1.4557`.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows
    and step-function payloads in general, but they do not force B.1-B.3
    reports to retain the interval counts, non-negative versus signed function
    assumptions, prior bounds, upper/lower-bound direction, or individual
    recomputation evidence for each of the three autocorrelation witnesses.
  - Required result: add paper/report evidence for Appendix B.1-B.3 rows:
    result id, constant id, metric formula id, domain, interval count,
    step-function payload hash, sign policy, prior bound and source,
    reported/recomputed value, bound direction, source section linkage, and
    README/ROADMAP text that keeps the three autocorrelation claims distinct
    from broad Appendix B family coverage.

- [ ] Track Appendix B.1-B.3 paper-heading and constant-label evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B names the three
    sections `B.1. First autocorrelation inequality`, `B.2. Second
    autocorrelation inequality`, and `B.3. Third autocorrelation inequality`.
    Their mathematical constants are `C1`, `C2`, and `C3`; no paper heading or
    caption labels them as `k=3`, `k=4`, or `k=5`.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows,
    but the checked Appendix B registry and its tests use internal labels such
    as `autocorrelation_bounds_k3` and `Autocorrelation inequality, k=3`.
    Without explicit paper-heading and constant-label evidence, future reports
    could expose those internal ids as if they were AlphaEvolve terminology.
  - Required result: add paper/report evidence for each B.1-B.3 row with exact
    source section id, paper heading, constant label, internal family id, and
    display-label policy. Update README/ROADMAP text so public claims use the
    paper's B.1-B.3 and C1-C3 labels, not the current k-number convention.

- [ ] Track Appendix B.8 squared-ratio convention evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.8 gives point-set
    constructions for minimizing the ratio of maximum to minimum pairwise
    distances. The values shown for 16 points in 2D and 14 points in 3D are
    `12.889266112` and `4.165849767`, respectively, under the paper's squared
    ratio reporting convention rather than direct square-root distance ratios.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows,
    metric formulas, units or bound semantics, and coordinate payloads, but they
    do not force B.8 reports to preserve the raw paper convention separately
    from the geometric ratio interpretation. A generated paper summary could
    therefore compare `12.889266112` as a direct max/min distance ratio instead
    of as a squared value.
  - Required result: add B.8 evidence fields for raw reported value,
    convention label, square-root-derived ratio, point count, dimension,
    coordinate artifact linkage, comparison-unit policy, and source location;
    update README/ROADMAP wording so claims about Appendix B.8 name the
    squared-ratio convention explicitly.

- [ ] Track Appendix B.8 point-set distance-certificate evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.8 and Figure 12
    report two distance-ratio point-set witnesses: 16 points in 2D with
    squared ratio `12.889266112`, improving the best known squared bound
    `12.890`, and 14 points in 3D with squared ratio `4.165849767`, improving
    the best known squared bound `4.168`.
  - Current gap: paper-facing Appendix B TODOs require broad normalized result
    rows, coordinate payloads, Figure 12 provenance, and the B.8
    squared-ratio convention. They do not require B.8 reports to prove the
    actual coordinate witnesses: exact point count and dimension, finite
    coordinate payload hash, all-pairs minimum/maximum distance certificate,
    recomputed squared ratio and derived geometric ratio, prior value/source
    comparison, or left/right Figure 12 panel linkage.
  - Required result: add paper/report evidence for Appendix B.8 witness rows:
    result id, `n`, dimension, coordinate artifact hash, pairwise-distance
    certificate hash, recomputed min and max distances, squared-ratio value,
    square-root-derived ratio, prior best value/source, improvement direction,
    Figure 12 panel id, source section/caption location, and README/ROADMAP
    wording that separates witness-certification evidence from metric-unit
    convention evidence.

- [ ] Track Appendix B.5 minimum-overlap step-function evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.5 reports that
    the Erdos minimum-overlap constant has known bounds
    `0.379005 <= C5 <= 0.380927`, and that the Figure 10 step function
    slightly improves the upper bound to `C5 <= 0.380924`. The step-function
    formulation uses `h: [0, 2] -> [0, 1]`, requires
    `integral_0^2 h(x) dx = 1`, and minimizes
    `max_k integral h(x) * (1 - h(x + k)) dx`.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows,
    step-function payloads, and Figure 10 exhibit provenance in general, but
    they do not force B.5 reports to retain the normalized `[0, 2]`
    step-function formulation, value-range and integral certificates,
    shift-objective recomputation, prior lower/upper values, or the improved
    upper-bound comparison.
  - Required result: add paper/report evidence for Appendix B.5 rows: result
    id, constant id, function domain and value range, step-function payload
    hash, integral-normalization certificate, shift/objective recomputation,
    prior lower/upper values and sources, reported upper bound, Figure 10
    linkage, source section location, and README/ROADMAP text that keeps the
    minimum-overlap witness distinct from broad Appendix B family coverage.

- [ ] Track Appendix B.5 source-formulation and equivalence evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.5 defines the
    Erdos minimum-overlap constant using paired functions
    `f,g: [-1,1] -> [0,1]`, the complement constraint `f + g = 1`,
    `integral f = 1`, zero extension outside `[-1,1]`, and the objective
    `sup_{x in [-2,2]} integral_{-1}^1 f(t) g(x+t) dt`. The appendix then
    cites `[40]` for equality with the infimum over normalized step functions
    `h` on `[0,2]`.
  - Current gap: paper-facing B.5 TODOs force retention of the reduced
    step-function payload and Figure 10 evidence, but they do not require
    reports to retain the original `f,g` formulation, the zero-extension and
    normalization conventions, the supremum domain, or the `[40]` equivalence
    that justifies using the step-function construction for `C5`.
  - Required result: add paper/report evidence for B.5 formulation rows:
    original problem statement id, `f,g` domain and value range, complement
    and integral constraints, zero-extension convention, supremum/objective
    domain, `[40]` equivalence source, mapping to the `h` construction row, and
    README/ROADMAP text that separates source-formulation evidence from
    Figure 10 step-function evidence.

- [ ] Track Appendix B.6 finite-set witness evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.6 improves the
    sums-and-differences lower bound using two finite integer-set witnesses:
    a set `U1` of size `2003` giving `1.1479 <= C6`, and a set `U2` of size
    `54265` giving `1.1584 <= C6`. The paper cites the Gyarmati et al.
    inequality, requiring `U` to contain zero and satisfy
    `|U - U| <= 2 max(U) + 1`, with the lower bound derived from
    `|U-U|`, `|U+U|`, and `2 max(U) + 1`.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows
    and finite-set construction payloads in general, but they do not force B.6
    reports to retain both witness identities, the two cardinalities, the
    intermediate and final lower-bound values, or the set-specific arithmetic
    evidence needed to recompute the Gyarmati-bound expression.
  - Required result: add paper/report evidence for Appendix B.6 witness rows:
    `U1`/`U2` ids, set cardinality, max element, contains-zero and feasibility
    checks, sorted integer payload hash, `|U-U|`, `|U+U|`, denominator,
    derived lower-bound value, source section linkage, and README/ROADMAP text
    that separates the two finite-set witnesses from broad Appendix B family
    coverage.

- [ ] Track Appendix B.6 theorem-condition evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.6 first defines
    `C6` using arbitrarily large finite integer sets `A` and `B`, with
    `A+B` and `A-B` explicitly defined as sumset and difference set. The
    appendix states that `X << Y` and `X >> Y` use constants independent of
    sufficiently large sets, cites `[39, Corollary 3]` for `C6 <= 4/3` and
    `[39, Theorem 1]` for the lower-bound framework, then applies the
    Gyarmati et al. result for finite `U` consisting of non-negative integers
    containing zero and satisfying `|U - U| <= 2 max(U) + 1`.
  - Current gap: paper-facing B.6 TODOs retain witness identities and
    recomputation inputs, but they do not require reports to preserve the
    theorem-level definitions, asymptotic constant scope, cited theorem and
    corollary anchors, or admissible-`U` domain statement. A report could
    recompute `U1`/`U2` values while omitting the source theorem conditions
    that justify using those finite sets for `C6`.
  - Required result: add paper/report evidence for B.6 theorem rows:
    theorem id, source location, sumset/difference-set definitions,
    `<<`/`>>` semantics, lower/upper source references, admissible-`U`
    conditions, formula linkage to witness rows, and README/ROADMAP text that
    separates theorem-condition evidence from witness arithmetic.

- [ ] Track Appendix B.7 regular-hexagon packing evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.7 improves two
    regular-hexagon packing bounds: for `n = 11`, the outer regular-hexagon
    side length improves from `3.943` to `3.931`; for `n = 12`, it improves
    from `4.0` to `3.942`. Figure 11 maps these to left and right
    construction panels.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows,
    geometric packing payloads, and Figure 11 exhibit provenance in general,
    but they do not force B.7 reports to retain the two separate `n` rows,
    unit-hexagon side convention, outer side-length convention, containment
    and pairwise-disjointness certificates, prior/current values, or Figure 11
    panel linkage.
  - Required result: add paper/report evidence for Appendix B.7 rows: result
    id, `n`, inner and outer hexagon geometry conventions, placement artifact
    hash, containment certificate, non-overlap certificate, prior value/source,
    reported side length, comparison policy, Figure 11 panel linkage, source
    section location, and README/ROADMAP text that separates the two hexagon
    witnesses from broad Appendix B family coverage.

- [ ] Track Appendix B.9-B.10 Heilbronn minimum-area evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.9-B.10 gives
    three Heilbronn construction claims: `n = 11` points in a unit-area
    triangle with minimum formed-triangle area greater than `0.0365` versus
    prior `0.036`; `n = 13` points in a unit-area convex region improving
    `0.0306` to `0.0309`; and `n = 14` points in a unit-area convex region
    improving `0.0277` to `0.0278`. Figure 13 maps these to left, middle, and
    right panels.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows,
    point-coordinate payloads, and Figure 13 exhibit provenance in general, but
    they do not force B.9-B.10 reports to preserve the three separate
    parameter/domain rows, unit-area scaling, all-triples minimum-area
    certificates, prior/current values, or strict inequality/rounding policy.
  - Required result: add paper/report evidence for Appendix B.9-B.10 rows:
    result id, `n`, domain type, unit-area normalization proof, point and
    region artifact hashes, minimum triangle area certificate over all triples,
    prior value/source, reported value, comparison policy, Figure 13 panel
    linkage, source section location, and README/ROADMAP text that separates
    the three Heilbronn witnesses from broad Appendix B family coverage.

- [ ] Track kissing-number lemma certificate evidence for Appendix B.11.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.11 reports 593
    nonzero integral-coordinate points in dimension 11, with maximum norm
    smaller than minimum pairwise distance, and uses Lemma 1 to derive a valid
    kissing configuration and lower bound of at least 593.
  - Current gap: paper-facing Appendix B coverage records family/status
    entries, expected construction/certificate artifact shapes, Colab/verifier
    export gaps, aggregate outcomes, and construction figures. It does not
    require the proof-grade certificate specific to the kissing-number claim:
    point count, coordinate domain, dimension, exact norm and distance
    inequalities, Lemma 1 applicability, transformed sphere centers,
    tangency/non-overlap checks, or claim linkage from the point-set artifact
    to the lower-bound statement.
  - Required result: add paper/report evidence for Appendix B.11 with a
    point-set artifact hash, exact coordinate and dimension metadata,
    cardinality check, norm/distance certificate, Lemma 1 proof-step record,
    transformed sphere-center verification, lower-bound claim id, and README/
    ROADMAP wording that distinguishes visual construction evidence from
    proof-grade kissing-configuration certification.

- [ ] Track Appendix B.12-B.13 circle/rectangle sum-of-radii evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.12-B.13 gives
    three packing claims: for `n = 26` circles in a unit square, the sum of
    radii improves from `2.634` to `2.635`; for `n = 32` circles in a unit
    square, it improves from `2.936` to `2.937`; and for `n = 21` circles in a
    rectangle of perimeter `4`, it improves from `2.364` to `2.3658`.
    Figure 14 maps these to left, middle, and right panels.
  - Current gap: paper-facing Appendix B TODOs require normalized result rows,
    geometric packing payloads, and Figure 14 exhibit provenance in general,
    and the checked-in `circle_packing` fixture is explicitly smoke-only. They
    do not force B.12-B.13 reports to preserve all three parameter/container
    rows, the rectangle perimeter convention, exact circle counts,
    containment/non-overlap certificates, prior/current sum-of-radii values,
    or Figure 14 panel linkage.
  - Required result: add paper/report evidence for Appendix B.12-B.13 rows:
    result id, `n`, container type and dimensions/perimeter, circle
    center/radius artifact hash, exact-count check, containment certificate,
    pairwise non-overlap certificate, recomputed sum of radii, prior
    value/source, reported value, Figure 14 panel linkage, source section
    location, and README/ROADMAP text that keeps the smoke fixture distinct
    from full Appendix B packing evidence.

- [ ] Track initial-program idea provenance for human-seeded benchmark claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.1 identifies the
    initial solution and optional background knowledge as user inputs, and
    Section 3.1 says some matrix-multiplication runs were seeded with
    researchers' own ideas, including adding stochasticity to the evaluation
    function or using evolutionary approaches, which boosted performance for
    some parameters. In the local PDF, this appears on page 10, which also
    says most Table 2 results used a simple initial program.
  - Current evidence: paper-facing status already distinguishes seed baselines
    from generated candidates and preserves safe seed source paths/kinds in
    manifests and history. Current seed-source records are limited to source
    identity/workspace-shape fields such as index, kind, path, primary file,
    file count, and file list; inline seeds get only index plus kind. That is
    artifact provenance, not paper-ready experiment provenance: it does not
    state whether a benchmark seed was simple/random versus
    researcher-idea-seeded, what prior idea or background knowledge was
    injected, which seed variant was used, or whether results are comparable
    across seed variants under equal budgets.
  - Required result: add paper/report evidence for initial-program idea class,
    human/background-knowledge contribution, prior-art or injected-idea label,
    seed-variant id, prompt/evaluator linkage, and equal-budget seed-variant
    outcomes before claiming AlphaEvolve-style scientific-collaboration or
    human-seeded matrix result parity.

- [ ] Track strict completeness of initial programs separately from
      optimization-pressure seeds.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.1 describes the
    initial implementation inside code blocks as complete, even if
    rudimentary, with the broader skeleton used by the evaluator to run the
    evolving solution. In the local PDF, page 5 says user-provided code inside
    evolution blocks serves as the initial solution, and Figure 2 on page 4
    places the initial program before the discovery loop.
  - Current evidence: LibreEvolve can evaluate and record invalid generation-0
    seeds as failed baselines, and README explicitly names examples such as
    `hello_world` as invalid greeting seeds used for seed-to-best optimization
    pressure. Current seed provenance and evaluator-contract records prove
    where a seed came from and how it evaluated; the runtime can also log an
    all-invalid seed-only run as completed with `no_valid_programs`. Those
    records do not prove that every initial implementation is a complete
    runnable AlphaEvolve-style starting point.
  - Required result: add paper-facing evidence and configuration/report fields
    that distinguish strict complete/runnable initial programs from permissive
    invalid or deliberately failing optimization-pressure seeds, require
    strict-seed validity for AlphaEvolve-parity benchmarks, and keep seed
    failure logs from being treated as paper-ready initial-solution evidence.

- [ ] Track expert problem-formulation provenance for mathematical benchmarks.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 1 separates
    human-defined problem setup from AlphaEvolve's search, naming evaluation
    criteria, initial solution, and optional background knowledge as human
    inputs. Section 3.2 says most mathematical discoveries came from open
    problems suggested by external mathematicians Javier Gomez Serrano and
    Terence Tao, who advised on how to best formulate them as AlphaEvolve
    inputs.
  - Current evidence: paper-facing status records problem/source provenance,
    local context-source selection, local paper context, retrieval grounding,
    and seed source identity. Those are artifact and prompt-context records,
    not paper-ready evidence of who selected a benchmark problem, what expert
    formulation advice shaped the task, why a parameter range/objective was
    chosen, what review/signoff state exists, or how that advice is linked to
    evaluator and report artifacts. Runtime provenance can hash the problem
    tree and source checkout, but it cannot by itself establish expert
    formulation authority.
  - Required result: add paper/report evidence for expert contributor roles,
    problem-origin and formulation notes, objective/evaluator rationale,
    parameter-scope decisions, background-knowledge linkage, and run/report
    provenance with review/signoff state before claiming AlphaEvolve-style
    expert-guided mathematical discovery setup.

- [ ] Track Section 3.2 incumbent-construction handoff evidence separately
      from generic benchmark artifacts.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says many
    mathematical applications evolved search heuristics that receive a time
    budget and a strong previously found construction, then search for an
    improved construction. This differs from only validating a final
    construction artifact after the fact.
  - Current evidence: the paper TODOs already require benchmark-grade
    constructive-math fixtures, construction/certificate validators, target
    baselines, and saved artifacts. Current code/docs also support static
    context and evaluator artifact copy-out. They do not yet define paper
    evidence for an AlphaEvolve-style handoff where the evaluator provides the
    incumbent construction and budget to the candidate heuristic, records the
    candidate's improved construction, and verifies the improvement as part of
    the benchmark result.
  - Required result: before claiming Section 3.2-style constructive-math
    alignment, add paper/report evidence for incumbent identity, budget,
    heuristic output construction, verifier/certificate inputs, and improvement
    status for at least one constructive-math benchmark family.

- [ ] Track Section 3.2 heuristic-stage sequence evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says the evolved
    heuristic receives a fixed time budget, for example `1000 seconds`, and the
    best construction from the previous best heuristic. It then says final
    constructions were often produced by a sequence of different specialized
    heuristics, with early stages making large gains from random/simple initial
    states and later stages fine-tuning near-optimal configurations.
  - Current gap: paper-facing TODOs already require single-step incumbent
    handoff evidence, simple/random starting construction provenance, and
    aggregate outcome rows. They do not require stage-by-stage evidence that a
    constructive-math result came from multiple heuristic generations with
    explicit budgets, incumbent lineage, stage roles, and per-stage improvement
    deltas.
  - Required result: add paper/report evidence for heuristic stage index,
    allotted budget seconds, previous-best construction id, candidate heuristic
    id, produced construction id, score before/after, improvement delta, stage
    role (`early_broad_gain` or `late_fine_tuning`), and verifier links before
    describing LibreEvolve results as AlphaEvolve-style multi-stage adaptive
    search.

- [ ] Track aggregate constructive-math breadth and outcome-rate evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says
    AlphaEvolve was applied to a curated set of over 50 mathematical problems
    spanning more than five branches, rediscovered the best known
    constructions in about 75% of cases, and improved the SOTA in about 20%.
  - Current evidence: the Appendix B registry is a thirteen-family coverage
    ledger with planned/smoke statuses, expected artifact kinds, and citation
    metadata. Existing TODOs require construction-data exports, verifier code,
    target baselines, incumbent handoff, and expert-formulation provenance.
    They do not yet require a per-problem/per-parameter outcome ledger whose
    branch labels and matched/improved/failed counts reproduce the Section 3.2
    aggregate claims.
  - Required result: add paper/report evidence for constructive-math problem
    instances, branch taxonomy, parameter settings, previous-best references,
    AlphaEvolve/LibreEvolve result status, construction/verifier links, and
    validated aggregate percentages before claiming Section 3.2-style
    mathematical breadth or SOTA-improvement rates.

- [ ] Track simple/random starting-construction evidence for constructive math.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says that in
    the constructive-math cases summarized by the best-known rediscovery and
    SOTA-improvement percentages, "the initial starting point was a simple or a
    random construction."
  - Current gap: paper-facing seed status preserves generation-0 source
    identity and separately tracks strict seed validity plus human-seeded
    matrix-result provenance. The Appendix B registry and aggregate outcome
    TODOs still do not require per-instance starting-construction class,
    random-generator/seed provenance, initial construction payload or hash,
    baseline metric value, or a policy proving that prior-best/incumbent
    constructions were not silently embedded as the starting point.
  - Required result: add paper/report evidence for each constructive-math
    problem instance: starting-construction class (`simple`, `random`,
    `human_seeded`, or `prior_art_seeded`), construction artifact/hash,
    generator and random seed where relevant, baseline value, prior-best
    visibility/seeding policy, and aggregate validation that Section 3.2-style
    breadth claims are supported by simple/random starts unless explicitly
    labeled otherwise.

- [ ] Track Appendix B result-version provenance for revised constants.
  - Paper evidence: Appendix B.4 reports an uncertainty-inequality construction
    with `C4 <= 0.3521`, then adds a note that after the first manuscript
    version Henry Cohn identified a refined approach and AlphaEvolve improved
    the reported constant further to `0.3216`, with details delegated to the
    accompanying Google Colab.
  - Current gap: paper-facing status treats Appendix B as thirteen families
    with planned/smoke statuses and expected artifact shapes. It does not
    distinguish first-version versus updated constants, superseded bounds,
    post-publication notes, contributor/advisor attribution for the revision,
    or which verifier artifact corresponds to each reported value.
  - Required result: add paper/report evidence for result revision identity,
    manuscript/source version, reported constant or construction value,
    previous and superseding values, update note, attribution, and verifier/
    Colab linkage before claiming Appendix B result parity. README, ROADMAP,
    papers index, and code TODOs should keep Appendix B wording scoped until
    versioned result rows prevent mixing stale and current mathematical
    claims.

- [ ] Track Appendix B.4 prior-bound rounding evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.4 gives the known
    uncertainty-inequality range as `0.2025 <= C4 <= 0.3523`. It notes that
    reference `[33]` states the prior upper bound as `0.353`, but that rounding
    the referenced solution to the fourth digit gives `0.3523`, which is the
    comparison baseline for AlphaEvolve's first-version `C4 <= 0.3521` result.
  - Current gap: paper-facing Appendix B TODOs track revised constants,
    Hermite/coefficient payloads, verifier/Colab links, previous-bound
    comparisons, and qualitative similarity to reference `[33]`. They do not
    preserve the prior source's stated value versus rounded value, the
    fourth-digit rounding policy, lower-bound context, or the precise baseline
    value that makes the `0.3521` improvement meaningful.
  - Required result: add B.4 paper-evidence records for the prior `[33]`
    bound: source id and page/section, stated value `0.353`,
    rounded/recomputed value `0.3523`, lower bound `0.2025`, rounding
    precision/policy, source-solution artifact or citation status, comparison
    against AlphaEvolve's `0.3521` first-version bound, and README/ROADMAP
    wording that separates this prior-bound caveat from the later `0.3216`
    revision and from Hermite-polynomial certificate evidence.

- [ ] Track Appendix B.4 Hermite-polynomial certificate evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.4 derives
    `C4 <= 0.3521` from a Fourier test function
    `f(x) = P(x) exp(-pi x^2)`, with `P` an even linear combination of Hermite
    polynomials `H_{4k}`. The paper reports approximate coefficients
    `[0.32925, -0.01159, -8.9216e-5]` for `H0`, `H4`, and `H8`, then computes
    the upper bound from the largest positive root of `P(x)/x^2` using
    `r_max^2 / (2*pi)`.
  - Current gap: paper-facing Appendix B TODOs track numeric result rows,
    revised constants, verifier/Colab links, and qualitative similarity to
    reference `[33]`. They do not require B.4-specific evidence for coefficient
    precision, Hermite-basis identities, the `P(0)=0` and `x^2` factor step,
    sign/condition checks, largest-root computation, or recomputation of the
    reported bound from the root certificate.
  - Required result: add paper/report evidence for B.4 Hermite basis terms,
    coefficient payload and precision, Fourier/test-function assumptions,
    `P(0)=0`/factor handling, largest-positive-root calculation, bound
    recomputation via `r_max^2 / (2*pi)`, previous-bound comparison, verifier
    artifacts, and documentation that separates this certificate from B.4
    revision-history and near-optimality interpretation evidence.

- [ ] Track Appendix B.4 prior-construction similarity and hypothesis evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B.4 reports the
    uncertainty-inequality construction and then says the AlphaEvolve linear
    combination is qualitatively very similar to the construction in reference
    `[33]`, which the paper presents as empirical confirmation of the
    hypothesis that the construction is nearly optimal.
  - Current gap: paper-facing Appendix B TODOs track numeric result rows,
    Hermite/coefficient payloads, prior-best values, revised constants, and
    verifier/Colab links. They do not preserve the qualitative
    construction-to-prior comparison or the near-optimality hypothesis as a
    distinct paper-evidence claim.
  - Required result: add B.4 paper-evidence records for the comparison to
    reference `[33]`: prior construction identifier, comparable structure or
    coefficient fields, qualitative-similarity claim, near-optimality
    hypothesis claim id, source page/section, evidence-strength label, and
    README/ROADMAP wording that does not conflate numerical improvement with
    qualitative hypothesis support.

- [ ] Generate AlphaEvolve-suite matrix-result publication artifacts.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 and Appendix A
    report matrix multiplication over 54 target sizes, measure both the best
    rank and the fraction of random seeds achieving that rank, provide exact
    algorithms with integer or half-integer entries, and point readers to an
    accompanying Google Colab for the constructions.
  - Current evidence: the active benchmark-hardening TODOs require stronger
    matrix validation, repeated seeds, exact verification, target/SOTA
    thresholds, and benchmark reports. A new
    `libreevolve.matrix_result_report.v1` contract validates target identity,
    dimensions, best rank, seed count, fraction of seeds achieving the best
    rank, exact coefficient domain, exactness certificate status, per-seed
    results, artifact paths/hashes, top-level best-rank and hit-fraction
    consistency against per-seed ranks/flags, summary rendering, and an
    explicit `alphaevolve_comparable` policy. Exploratory `rational` and
    `float` coefficient-domain reports remain valid only when
    `alphaevolve_comparable` is false; AlphaEvolve-comparable claims require
    integer or half-integer coefficients, verified exactness, exact per-seed
    rows, and algorithm/certificate/notebook artifacts. The report contract
    now uses `libreevolve.alphaevolve_appendix_a_matrix_registry.v1` to record
    the 54 Appendix A Table 3 target identities, dimensions, best-known ranks,
    AlphaEvolve ranks, and matched/surpassed/fell-behind outcomes; reports for
    `alphaevolve_appendix_a` reject unknown target ids and dimension
    mismatches. The registry is not itself construction evidence: it does not
    store target tensors, discovered tensor decompositions, coefficient lists,
    per-target exactness certificates, notebook exports, or construction
    provenance for reproducing Appendix A algorithms. The Appendix A registry
    validator is separate from the standard `paper_manifest` command, whose
    current central gate validates Appendix B and ablation registries but not
    Appendix A registry integrity.
    `libreevolve.matrix_result_artifact_inventory.v1` now verifies
    declared algorithm/certificate/notebook artifact paths against concrete
    files under an explicit artifact root, checking safe relative paths,
    existence, SHA-256 hashes, and byte counts.
    `write_strassen_2x2_publication_bundle()` now provides a concrete checked
    Strassen baseline for the registered `mm_2x2x2` target, with canonical
    algorithm, certificate, notebook, report, and artifact-inventory files and
    exact rank-7 per-seed rows. `validate_matrix_publication_bundle()` now
    checks the `libreevolve.matrix_publication_bundle.v1` wrapper, embedded
    report, target identity, report-file hash/byte evidence, and inventory
    consistency for that baseline. The paper index now distinguishes that one
    checked Strassen baseline from the still-missing generated notebook/export
    equivalents for reproducing discovered algorithms across the full Appendix
    A suite.
  - Required result: connect real matrix target tensors, exact algorithm
    artifacts, coefficient-domain data, certificate-generation artifacts, and
    generated export/notebook links to real report instances; also route
    Appendix A registry validation through the routine paper-manifest gate
    before treating LibreEvolve matrix results as AlphaEvolve-comparable
    evidence. The remaining gap is producing those discovered tensor artifacts
    for the suite, not verifying declared report artifacts, validating the
    checked bundle wrapper, or emitting one checked Strassen baseline once
    those files exist.

- [ ] Track best-known-rank citation provenance for Appendix A comparisons.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 presents matrix
    targets with a `best known [reference]` column, and Appendix A Table 3
    extends the matrix target-suite rank comparisons.
  - Current evidence: the checked Appendix A matrix registry records
    best-known rank numbers, AlphaEvolve ranks, outcomes, and exact-algorithm
    flags, and matrix reports can validate target identities and dimensions
    against that registry. The paper-facing evidence does not yet preserve the
    cited prior-work source for each best-known baseline rank, source
    page/table, reference id, source artifact digest, finite-field or
    characteristic caveat, or baseline-source field in generated result
    reports.
  - Required result: add paper-facing baseline-rank provenance before using
    Appendix A best-known-rank comparisons as fully traceable evidence:
    per-target cited-source metadata, manifest/companion-artifact validation,
    report-visible baseline-source fields, and docs that distinguish cited
    prior baselines from LibreEvolve-generated constructions.

- [ ] Track matrix cascade-run evidence behind repeated-seed rank claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 says the matrix
    experiments run over multiple random seeds using the evaluation cascade,
    and paper-visible performance is the best rank plus the fraction of seeds
    that reached it.
  - Current gap: the paper-facing matrix report contract validates declared
    seed rows and aggregate hit fractions, while generic cascade TODOs track
    cascade semantics. It does not preserve matrix-specific executed cascade
    traces: target/seed ids, cascade configuration, stage thresholds,
    per-stage ranks and exactness diagnostics, pruning or early-stop reasons,
    final accepted rank, or aggregation evidence linking those traces to the
    published Table 2/Appendix A rank and hit-fraction rows.
  - Required result: add paper/report evidence for matrix cascade runs before
    treating per-seed matrix result reports as AlphaEvolve Section 3.1 search
    evidence: one trace per target/seed, stage-level diagnostics and stop
    reasons, candidate/result artifact links, and summary validation that the
    reported best-rank and hit fraction are computed from those executed
    cascade traces.

- [ ] Track Table 2/Table 3 matrix-rank table exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 is the main-text
    selected matrix-rank comparison table, and Appendix A Table 3 is the full
    54-target version with best-known ranks, AlphaEvolve ranks, outcome
    coloring/summary counts, complex-valued row caveats, Colab decomposition
    links, and the concurrent-work note for `<4, 5, 6>`.
  - Current gap: the paper TODOs track baseline-rank citations, row notes,
    target-suite curation, companion Colab evidence, Figure 4 exhibit
    provenance, scalar-field caveats, tensor-rank caveats, and result
    artifacts. They do not yet preserve Table 2/Table 3 as table exhibits with
    stable ids, selected-row versus full-table relation, row ordering, caption
    aggregate checks, color/outcome encoding, complex-valued annotations, note
    linkage, source PDF/caption locations, rendered table artifact hashes, or
    row-to-registry/report/Colab mappings.
  - Required result: add paper-facing table exhibit records for Table 2 and
    Appendix A Table 3: source PDF page/caption locations, table ids, row
    ids/order, selected/full-table membership, rank values, outcome classes and
    aggregate count validation, complex-valued and concurrent-work annotations,
    rendered table artifacts/hashes, and links to Appendix A registry rows,
    matrix reports/certificates, and companion source evidence.

- [ ] Track matrix result subset-scope evidence for Table 2 versus Appendix A
      outcome claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 states that for all
    parameters `m, n, p <= 5`, AlphaEvolve matched or surpassed the best-known
    solutions. Appendix A Table 3 is the full 54-target table and includes
    rows outside that main-text subset.
  - Current gap: the checked Appendix A matrix registry validates total rows
    and aggregate outcomes (`38` matched, `14` surpassed, `2` fell behind),
    but it does not provide paper-facing subset summaries that prove which
    rows belong to the `m,n,p <= 5` main-text claim, which rows are only in
    the broader Appendix A table, or why larger-target `fell_behind` rows do
    not contradict the scoped Table 2 statement.
  - Required result: add paper-facing subset-scope records for named target
    sets such as `main_text_mnp_le_5`, `table_2_selected`, and
    `appendix_a_full`, including inclusion predicates, row counts, outcome
    counts, out-of-scope row ids, source-caption/table linkage, and
    README/ROADMAP validation that keeps scoped main-text claims distinct from
    full Appendix A aggregate outcomes.

- [ ] Track matrix headline historicity evidence for the 4x4 complex rank-48
      result.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` abstract reports a procedure
    for multiplying two 4x4 complex-valued matrices using 48 scalar
    multiplications. Section 3.1 adds that recursive Strassen gives rank 49
    over any field, Fawzi et al. found rank 47 only over the field with two
    elements, and AlphaEvolve is the first method in 56 years to find rank
    below 49 over a characteristic-zero field.
  - Current gap: paper TODOs track Appendix A best-known-rank citations,
    scalar-field evidence, Table 2/Table 3 exhibits, target-subset scope,
    Figure 4/Figure 9 provenance, and companion Colab evidence. They do not
    preserve the abstract/Section 3.1 headline as its own auditable claim with
    prior-algorithm comparison, field caveat, historicity wording, and source
    locations. A table row or scalar-field record alone would not prove the
    "first improvement after 56 years" claim.
  - Required result: add paper-facing matrix-headline provenance: target id,
    dimensions, scalar field/characteristic, reported rank, Strassen baseline
    rank and scope, finite-field Fawzi caveat, bibliography reference ids,
    abstract and Section 3.1 page/span locations, decomposition/certificate/
    Colab links, and validation that docs distinguish rank/certificate evidence
    from historicity and field-scope claims.

- [ ] Track Appendix A matrix row-note and concurrent-work provenance.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A Table 3 includes
    a note that concurrent work [49] also found a rank-90 algorithm for the
    `<4, 5, 6>` target.
  - Current gap: the paper-facing Appendix A registry/status stores target
    ids, dimensions, best-known ranks, AlphaEvolve ranks, outcomes, and
    exact-algorithm flags, while separate TODOs require baseline citations,
    target-suite curation, scalar-field evidence, and companion Colab links.
    It does not preserve row-level notes, concurrent-work attribution,
    independently matched result flags, note source location, or docs caveats
    for matrix rows such as `mm_4x5x6`.
  - Required result: add paper-facing row-note metadata for Appendix A matrix
    targets: affected target id, note type, cited reference id, note text/source
    location, relationship to the AlphaEvolve result, and validation that
    README/ROADMAP/papers wording qualifies SOTA-priority claims when the
    paper records concurrent matching work.

- [ ] Track AlphaEvolve companion Colab as paper source evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` footnote 2 says the
    discovered algorithms and new mathematical results are available at the
    `google-deepmind/alphaevolve_results` `mathematical_results.ipynb` Colab,
    and Table 2 says the shown matrix decompositions can be found in the
    accompanying Google Colab.
  - Current evidence: the committed paper manifest tracks PDF rows only. The
    paper index and TODOs require local Appendix A/B result artifacts,
    notebooks, verifier code, and Colab-equivalent exports once LibreEvolve
    emits them, but they do not preserve the actual AlphaEvolve companion
    notebook as a versioned source artifact. There is no URL/ref/digest record,
    notebook readability check, cell-to-claim map, or distinction between
    external source evidence from DeepMind's notebook and future LibreEvolve
    generated notebook/export artifacts.
  - Required result: add paper-facing companion-artifact provenance for the
    AlphaEvolve Colab: canonical notebook URL and repository/ref, retrieval and
    integrity metadata, optional local cache validation, claim-to-cell or
    claim-to-artifact links for Appendix A matrix and Appendix B constructive
    results, and docs wording that separates source-artifact verification from
    LibreEvolve reproducing those results.

- [ ] Track companion-result notebook selection scope and absences.
  - Paper evidence: the `google-deepmind/alphaevolve_results` README says
    `mathematical_results.ipynb` contains the mathematical discoveries from
    Section 3 and corresponding correctness-verification code, but only for
    instances where AlphaEvolve outperformed the state of the art. It says
    matched-but-not-outperformed constructions are excluded to avoid clutter,
    and that the repository does not contain the code to run AlphaEvolve.
  - Current gap: paper-facing companion-artifact TODOs require the actual
    notebook URL/ref/digest and claim-to-cell mapping, but they do not require
    a notebook selection-scope record. Without that record, a matrix or
    Appendix B claim missing from the companion notebook could be misread as a
    source-tracking failure instead of an intentional
    outperformed-results-only repository policy.
  - Required result: add source evidence for companion-notebook selection:
    repository URL/ref/commit, notebook path, inclusion rule, excluded/matched
    result rule, per-claim coverage or absence reason, verifier-code presence,
    runtime-code absence, license/source notes, and docs checks that
    distinguish paper-reported matched results from companion-notebook
    improved-result artifacts.

- [ ] Track companion-result repository rights and disclaimer evidence.
  - Paper evidence: the `google-deepmind/alphaevolve_results` README states
    `Copyright 2025 Google LLC`, licenses all software under Apache License
    2.0, licenses all other materials under Creative Commons Attribution 4.0
    International, includes an as-is warranty disclaimer, and says the
    repository is not an official Google product.
  - Current gap: paper-facing source-rights TODOs cover the cached
    AlphaEvolve PDF, and companion-artifact TODOs mention generic
    license/source notes. They do not require a source-rights row for the
    result repository itself, nor artifact-type license mapping for notebook
    code, verifier software, construction data, figures, or other materials.
  - Required result: add companion-repository rights evidence with repository
    URL/ref/commit, rights holder/year, software license, materials license,
    source line or README span, as-is disclaimer, non-official-product
    disclaimer, artifact-type license mapping, reuse/reproduction policy, and
    README/ROADMAP checks that separate companion repository rights from
    source-PDF rights and LibreEvolve's repository license.

- [ ] Track AlphaEvolve source-PDF arXiv version provenance.
  - Paper evidence: page 1 of `2506.13131__AlphaEvolve.pdf` identifies the
    audited source as `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`.
  - Current evidence: `papers/download_manifest.csv` and
    `papers/download_manifest.json` list `2506.13131`, the title
    `AlphaEvolve`, a floating `https://arxiv.org/pdf/2506.13131.pdf` URL,
    the local PDF path, byte count, SHA-256 hash, and status. The manifest and
    paper index do not persist the paper-source version/date/category,
    expected header text, or source URL kind, so future arXiv rehydration could
    silently move claim audits from v1 to a later source without a ledger
    change. Existing result-version TODOs cover Appendix B revised constants,
    not the manuscript/PDF identity used for all AlphaEvolve claims.
  - Required result: add paper-facing provenance rows for source PDF identity:
    arXiv id, version, category, posted date, canonical floating and
    version-pinned URLs where available, expected header page/text, PDF hash,
    and claim-audit links that identify the source version behind every
    AlphaEvolve table, figure, and appendix TODO.

- [ ] Validate paper-manifest row identity before trusting cached PDFs.
  - Paper evidence: AlphaEvolve-alignment paper audits depend on the local
    paper cache preserving the correct source PDF for each paper-facing row.
    The row id, source URL, and local PDF label should agree on the source
    identity before later version, rights, citation, or claim-excerpt evidence
    is attached.
  - Current gap: the committed manifests list `id`, `url`, and `file`, and
    the validator checks safe row ids, allowed HTTPS hosts, safe PDF paths,
    CSV/JSON synchronization, duplicate targets, hashes, and optional local
    PDF integrity. It does not check that an arXiv URL's embedded paper id
    matches the manifest id, that the local filename source prefix matches the
    same id, or that non-arXiv/slug rows carry an explicit source-identity
    mapping. A row could drift to a different allowed arXiv URL while retaining
    a valid id and safe filename without the manifest-index gate flagging the
    identity mismatch.
  - Required result: add paper-index source-identity validation for manifest
    rows: parse arXiv ids from source URLs, compare URL id with row id and
    local file stem/source-id prefix, reject mismatches, and require declared
    canonical source ids for non-arXiv or slug rows. Keep this separate from
    arXiv version provenance, which pins a specific revision after the base
    source identity is proven.

- [ ] Track AlphaEvolve source-PDF rights and license provenance.
  - Paper evidence: page 1 of `2506.13131__AlphaEvolve.pdf` states
    `© 2025 Google DeepMind. All rights reserved`.
  - Current gap: the committed paper manifest and paper index record the local
    PDF file, URL, byte count, SHA-256 digest, and paper status. Active TODOs
    now require source-PDF version metadata and companion/source-artifact
    tracking, but they do not preserve source rights metadata for the cached
    AlphaEvolve PDF: copyright holder/year, rights statement, arXiv/license
    terms, excerpt/reproduction policy, or distinction between LibreEvolve's
    MIT repository license and third-party paper-source rights.
  - Required result: add paper-facing source-rights provenance for cached PDFs:
    rights holder, copyright year, rights statement or license identifier/text,
    source page/header location, retrieval URL, local PDF hash, allowed
    excerpt/reproduction policy for tables/figures/quotes, and README/ROADMAP/
    papers wording that prevents paper-derived artifacts from being presented
    as publication-ready without verified source-use boundaries.

- [ ] Track full AlphaEvolve References-section bibliography evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` includes a numbered
    References section after Author information, with entries through `[120]`
    covering cited works used by the abstract, method, results, related work,
    and appendices.
  - Current gap: paper/status TODOs track selected source-reference gaps such
    as Appendix A matrix baseline references, Appendix B prior sources,
    related-work rows, paper-source versioning, source rights, and companion
    artifacts. They do not preserve a complete paper-facing bibliography table
    for AlphaEvolve itself. The committed paper manifest only stores
    id/title/url/file/status/bytes/hash, and `papers/README.md` explicitly says
    manifest titles are not authoritative bibliographic titles.
  - Required result: add paper-facing bibliography provenance for the
    AlphaEvolve References section: reference number, authors, title, venue,
    year, DOI/URL/arXiv id where present, source page/span, citation-use
    category, local-cache linkage or absent-cache status, and docs validation
    that distinguishes full bibliography evidence from manifest display slugs
    and narrower per-claim citation TODOs.

- [ ] Track follow-on AlphaEvolve mathematical-discovery paper and repository.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says more
    examples and details on the mathematical construction problems and methods
    would appear in an upcoming paper. Current primary-source evidence
    identifies that follow-on as arXiv `2511.02864`, `Mathematical exploration
    and discovery at scale`, by Bogdan Georgiev, Javier Gomez-Serrano, Terence
    Tao, and Adam Zsolt Wagner, with arXiv v3 dated 2025-12-22. The associated
    `google-deepmind/alphaevolve_repository_of_problems` repository states
    that it contains 67 problem pages and Colab notebooks for many problems,
    including prompts, verification code, initial programs, final evolved
    programs, and visualization/analysis code where appropriate.
  - Current gap: the local `papers/` cache, download manifests, paper index,
    and AlphaEvolve TODOs still treat `2506.13131` plus its original companion
    Colab as the only AlphaEvolve primary-source surface. They do not preserve
    the follow-on paper PDF/version, repository ref, problem inventory,
    notebook availability, or mapping from original Appendix B claims to the
    expanded 67-problem source set.
  - Required result: add paper/source evidence rows for arXiv `2511.02864` and
    the DeepMind problem repository: PDF URL/cache/digest, arXiv version/date,
    repository URL/ref/commit and live-update policy, problem ids, notebook
    artifact metadata, prompt/verifier/initial/final-program presence, license
    notes, claim mappings to the original AlphaEvolve math results, and
    README/ROADMAP wording that makes the original-paper versus follow-on
    source boundary explicit.

- [ ] Track follow-on problem-repository coverage-state evidence.
  - Paper/source evidence: the
    `google-deepmind/alphaevolve_repository_of_problems` README describes a
    live repository that will expand and improve over time. It says every one
    of the 67 mathematical problems has a problem page, while Colab notebooks
    exist for many but not all problems and may contain prompts, verification
    code, initial programs, final evolved programs, and visualization/analysis
    code where appropriate. It gives the hosted problem-page URL pattern
    `https://google-deepmind.github.io/alphaevolve_repository_of_problems/problems/{n}.html`,
    says no installation is required, and says notebooks can be opened in
    Google Colab while webpages can be opened in any browser. The README's
    distribution graphic points to root-level `status_grid.png`, and the
    repository tree also exposes root-level status artifacts such as
    `status.json` and `result_distribution.png`. Current `status.json` uses
    explicit buckets `world_record`, `former_record`, `worse_than_record`, and
    `matched_optimal`, listing 43 problem ids total.
  - Current gap: existing paper TODOs require a repository ref and broad
    notebook artifact metadata, but they do not preserve source-state
    distinctions between all problem pages, partial notebook availability,
    hosted-page URLs, browser/Colab access modes, artifact-presence variants,
    missing-notebook reasons, root-level status-artifact provenance, and
    live-repository snapshot dates. They also do not parse status-bucket
    membership or preserve explicit `unclassified`/absent-status states for
    problem ids not listed in `status.json`. Earlier coverage wording also
    used unverified `assets/...` status paths instead of the README's
    root-level status artifact path.
  - Required result: add source-manifest rows and checks for the problem
    repository snapshot: repository URL/ref/commit/date, live-update policy,
    all 67 problem ids, hosted page URL, page path/hash, notebook path/hash or
    explicit absence reason, access mode, prompt/verifier/initial/final/
    visualization/analysis presence flags, root-level status artifact paths/
    hashes such as `status_grid.png`, `status.json`, and
    `result_distribution.png` when used, parsed status bucket membership,
    explicit state for problem ids absent from `status.json`, and citation
    wording that avoids implying notebook or status coverage is complete when
    only problem-page coverage is complete.

- [ ] Track follow-on numbered problem-page inventory and source-count
      discrepancy.
  - Paper/source evidence: the
    `google-deepmind/alphaevolve_repository_of_problems` README says the
    repository contains problem descriptions for 67 mathematical problems, but
    the current repository `problems/` directory exposes 68 numbered HTML
    pages. Raw pages `problems/67.html` and `problems/68.html` are both titled
    `Logic puzzles`; page 67 has a Colab placeholder `#`, while page 68 has a
    generic Colab URL and a paper-link placeholder `#`.
  - Current gap: follow-on paper/source TODOs require problem ids, hosted URLs,
    notebook availability, access modes, status buckets, and live snapshot
    policy. They do not require a source-count reconciliation between the
    README/paper claim and live numbered HTML inventory, nor diagnostics for
    duplicate titles, repeated paper-section mappings, under-construction
    links, generic Colab links, or placeholder paper links.
  - Required result: add source-manifest validation for numbered problem pages:
    expected count from paper/README, discovered page files, page id/title,
    paper section mapping, duplicate-title/section diagnostics, resource-link
    status (`valid`, `placeholder`, `generic`, `under_construction`, or
    absent), classification of the 67-versus-68 discrepancy, and README/
    ROADMAP/papers wording that keeps problem-count claims snapshot-scoped.

- [ ] Track follow-on problem-repository rights, citation, and attribution.
  - Paper/source evidence: the
    `google-deepmind/alphaevolve_repository_of_problems` README says users of
    the code or data should cite `Mathematical exploration and discovery at
    scale`. Its license/disclaimer section declares `Copyright 2025 Google
    LLC`, Apache 2.0 for software, CC-BY 4.0 for other materials, an as-is
    warranty disclaimer, and that the repository is not an official Google
    product. The same section credits Professors Javier Gomez-Serrano and
    Terence Tao with supervision, problem selection, review, analysis, and
    commentary, and says Problem 65 originates from the official IMO problems
    website.
  - Current gap: active paper TODOs require the follow-on paper/repository and
    coverage-state manifests, but they do not preserve the problem
    repository's specific source-use terms, citation instruction, contributor
    role note, or third-party source-origin note. The existing companion-rights
    TODO is specific to `alphaevolve_results`, not this later repository.
  - Required result: add paper/source metadata for the problem repository's
    citation and source-use boundary: repository URL/ref/commit/date,
    citation/BibTeX fields, rights holder/year, software license, materials
    license, license URLs, artifact-type license mapping, as-is disclaimer,
    non-official-product disclaimer, role-attribution note, Problem 65 IMO
    source URL, and README/ROADMAP/papers wording that distinguishes these
    terms from the original AlphaEvolve PDF and result companion repository.

- [ ] Track follow-on problem-repository runtime-absence evidence.
  - Paper/source evidence: the
    `google-deepmind/alphaevolve_repository_of_problems` README says notebooks
    contain prompts, verification code, initial programs, final evolved
    programs, and visualization/analysis code where appropriate, and then
    explicitly says the repository does not contain code to run AlphaEvolve.
  - Current gap: existing paper TODOs require follow-on notebook availability
    and artifact-presence flags, while companion-result TODOs track runtime
    absence for `alphaevolve_results`. They do not preserve this same runtime
    absence boundary for the later problem repository, which could make
    paper/source claims imply the notebooks are executable AlphaEvolve runtime
    harnesses rather than source evidence for prompts, verifiers, and evolved
    outputs.
  - Required result: add source-manifest metadata and checks for follow-on
    runtime availability: repository URL/ref/commit/date, notebook path/hash,
    artifact-kind flags, explicit AlphaEvolve-runtime absence, source span for
    the absence statement, verifier-versus-runtime classification, and README/
    ROADMAP/papers wording that does not treat problem-repository notebooks as
    containing the AlphaEvolve implementation.

- [ ] Track Terence Tao follow-on blog source and claim boundaries.
  - Paper/source evidence: Terence Tao's November 5, 2025 post
    `Mathematical exploration and discovery at scale` links the arXiv paper,
    the AlphaEvolve tool, and the follow-on problem repository, describes 67
    mathematics experiments with both positive and negative outcomes, and adds
    commentary on scale, adaptability, interpretability, verifier exploits,
    exact/interval-arithmetic verifier hardening, one-sided open-conjecture
    bounds, systematic negative-result recording, parameterized-code
    generalization, and proof handoffs involving human proof work, Deep Think,
    AlphaProof, or later papers.
  - Current gap: the paper index and TODOs track the original AlphaEvolve PDF,
    the follow-on arXiv paper, the DeepMind problem repository, official
    DeepMind/Google articles, and source rights. They do not preserve this
    linked Tao blog as a separate source surface, nor classify which blog-only
    claims are commentary, anecdotal lessons, future work, or evidence that
    must be backed by pinned repository/notebook/proof artifacts before being
    used in README or roadmap claims.
  - Required result: add source rows for the Tao blog with canonical URL,
    author, date, title, retrieval timestamp/hash, linked arXiv/repository
    references, source spans, claim category, paper/repository cross-links,
    and docs checks that keep blog commentary secondary to paper/repository
    evidence for verifier-hardening, negative-result, generalization, and
    proof-handoff claims.

- [ ] Track AlphaEvolve theoretical-CS proof-element source evidence.
  - Paper evidence: Google Research's September 30, 2025 article
    `AI as a research partner: Advancing theoretical computer science with
    AlphaEvolve` and arXiv `2509.18057`, `Reinforced Generation of
    Combinatorial Structures: Applications to Complexity Theory`, report
    AlphaEvolve-discovered finite combinatorial proof elements for complexity
    theory: MAX-k-CUT gadget reductions and Ramanujan-graph constructions. The
    sources describe lifting finite structures into universal theorem
    statements, computer-verified proof elements, AlphaEvolve-accelerated
    verifier code, and final verification with the original brute-force
    algorithm.
  - Current gap: the paper cache and AlphaEvolve ledgers track `2506.13131`,
    the original companion Colab, Appendix A/B result surfaces, and the
    `2511.02864` math-scale follow-on paper/repository. They do not preserve
    the separate theoretical-CS article/paper as paper-facing source evidence,
    nor do they require graph/gadget artifact inventories, lifting-framework
    boundaries, verification-speedup claims, or final independent-verifier
    provenance.
  - Required result: add source rows for the Google Research article and arXiv
    `2509.18057`: URL/date, arXiv version/date/PDF cache/digest, source
    artifact or repository links if available, problem/result ids, graph/gadget
    artifact metadata, verifier and original brute-force verifier provenance,
    lifting-framework statement, rights/license notes, and README/ROADMAP
    wording that keeps theoretical-CS proof-element applications distinct from
    the original AlphaEvolve specification and the 67-problem constructive-math
    follow-on.

- [ ] Track official DeepMind AlphaEvolve blog source and claim variants.
  - Paper evidence: the official Google DeepMind blog article dated May 14,
    2025, `AlphaEvolve: A Gemini-powered coding agent for designing advanced
    algorithms`, is cited by the local TODO ledgers as public AlphaEvolve
    evidence. It describes the Gemini/evaluator/evolutionary-framework
    combination, entire-codebase evolution, systems deployments, the white
    paper and mathematical-results Colab links, Early Access/user-interface
    plans, and blog-specific values or wording such as `up to a 32.5%`
    FlashAttention speedup and kernel-optimization effort reduced from
    `weeks` to days.
  - Current gap: the paper cache and AlphaEvolve TODOs track PDF sources,
    companion Colab gaps, follow-on papers/repositories, Section 3.3 metric
    calibration, and paper acknowledgements. They do not preserve the official
    blog as a source artifact with URL/date/title/digest, outbound links,
    claim-to-white-paper mappings, blog-only availability statements,
    acknowledgement/illustration roles, or variant handling where the blog and
    white paper differ in value or wording.
  - Required result: add paper/source evidence rows for official DeepMind blog
    sources: URL, publication/update date, title, retrieval digest, linked
    white-paper and Colab targets, claim ids, source-specific text/value/unit,
    reconciliation status against the white paper, blog-only availability or
    Early Access statements, acknowledgement/illustration role metadata, and
    README/ROADMAP wording that separates announcement-source evidence from
    white-paper specification and LibreEvolve reproduction evidence.

- [ ] Validate paper-index TODO coverage cross-references.
  - Paper evidence: `papers/README.md` includes a "TODO coverage
    cross-references" table that says each implementation-status row is tied
    to backlog evidence, with active and completed/grouped evidence columns.
    AlphaEvolve-alignment audits depend on this source-to-backlog chain so
    paper status rows do not become disconnected from the TODO ledgers that
    state missing or unsupported behavior.
  - Current gap: checked-in tests only assert that each manifest id appears
    once in the section and that the row mentions `docs/todo/`. The
    `libreevolve.tools.paper_manifest` validator checks the implementation
    status table against manifest ids, but it does not validate the TODO
    coverage table, referenced file existence, grouped-gap labels,
    active-versus-completed target semantics, whether every listed active
    evidence target still contains a matching open gap, or whether grouped
    labels are stale after later source-specific TODO entries are added for
    rows such as the AlphaEvolve application/context papers.
  - Required result: add paper-index cross-reference validation with manifest
    id coverage, duplicate/extra row checks, safe and existing backlog paths,
    allowed grouped-gap labels, active/completed target classification, and
    optional checks that active references point to matching open TODO text.
    Add stale-grouped-label detection so a row with source-specific open TODOs
    is not left pointing only at a broad grouped gap. Update README/ROADMAP/
    code TODO wording so the paper index distinguishes implementation-status
    validation from verified backlog traceability.

- [ ] Validate paper-index implementation-status semantics, not only ids.
  - Paper evidence: `papers/README.md` explicitly makes the implementation
    status table the source for paper-facing titles, roles, implementation
    status, and benchmark coverage decisions because manifest titles are only
    cache-display slugs. Those cells define whether a paper row is background,
    a primary AlphaEvolve specification target, partially implemented, smoke
    scoped, or unsupported.
  - Current gap: `libreevolve.tools.paper_manifest` reconciles manifest ids
    against the implementation-status table and tests missing, duplicate, and
    extra ids. It does not parse or validate the remaining cells: paper-facing
    title, role, status taxonomy, coverage qualifiers, "implemented" versus
    "not implemented" language, or whether a row's semantic claim is backed by
    the cited code/TODO evidence. A row could keep the same id while drifting
    from smoke-scoped wording to paper-claim wording without the manifest gate
    noticing.
  - Required result: add paper-index status-cell validation with stable
    headers, exact four-column row shape, allowed role/status classes,
    title/role non-empty checks, smoke/partial/planned/unsupported qualifier
    rules, and evidence links from semantic status claims to TODO or completed
    implementation records. Keep this validator distinct from the TODO
    coverage cross-reference checker, which verifies backlog pointers after
    the implementation-status table.

- [ ] Track paper-artifact creator and assembler roles for figures and Colab.
  - Paper evidence: the Contributions section of
    `2506.13131__AlphaEvolve.pdf` states that N.V., E.D., M.E., S.C., A.N.,
    and A.Z.W. created the figures, while F.J.R.R., A.M., and A.Z.W. assembled
    the accompanying Google Colab.
  - Current gap: paper-facing TODOs require exhibit ids, source/caption
    locations, rendered artifact hashes, companion Colab URL/ref/digest
    records, and claim-to-cell mappings. They do not require a paper-source
    role record that attributes figure creation or notebook assembly to the
    responsible contributors, ties those roles to a figure/table/notebook id,
    or validates the source location for the role claim.
  - Required result: add paper-facing artifact-role provenance for figures,
    tables, and companion notebooks: artifact id/type, creator or assembler
    role, responsible initials/names, source section/page, artifact hash/link,
    and README/ROADMAP wording that separates artifact availability from
    paper-attributed artifact authorship.

- [ ] Track Appendix A matrix target-suite curation provenance.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A says the 54
    matrix sizes were chosen roughly from dimensions with 2 <= m,n <= 5 and a
    reasonable cutoff for p, and that symmetries of the matrix multiplication
    tensor make axis permutations equivalent, so the reported suite focuses on
    sorted sizes m <= n <= p.
  - Current gap: the Appendix A registry records the 54 reported target ids,
    dimensions, ranks, and outcomes, but it does not preserve the paper's
    target-suite selection rule, canonical sorted-representative policy,
    omitted symmetry-equivalent targets, p-cutoff/source rationale, or why
    targets outside the rough rank/size heuristic are included or excluded.
  - Required result: add paper-facing curation records for the Appendix A
    matrix suite: selection criteria, symmetry class/canonical representative,
    omitted-equivalent target ledger, cutoff rationale, and included/excluded
    target justifications. Keep this separate from construction artifacts and
    from larger-target resource-frontier/OOM evidence.

- [ ] Track matrix target-scaling resource frontier and OOM evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A says the authors
    often ran out of memory when trying discovered programs on sizes beyond
    the reported table with 1000 random seeds on evaluators with a single GPU
    accelerator, and that extending to larger matrix sizes requires further
    optimization.
  - Current evidence: matrix registries and result reports cover the reported
    Appendix A target identities, rank outcomes, per-seed hit fractions, and
    artifact links once present. Generic runtime docs also track evaluator
    seconds, LLM budgets, accelerator environment hints, and unsupported
    CPU/memory/GPU quota enforcement. They do not provide matrix-specific
    resource-frontier evidence for larger target attempts, GPU memory
    exhaustion, seed-count scaling, or target-exclusion rationale.
  - Required result: add paper/report evidence for attempted larger matrix
    targets, configured seed counts, accelerator/memory profile, resource
    exhaustion or OOM diagnostics, reduced-seed tradeoffs if used, and
    explicit inclusion/exclusion policy before claiming LibreEvolve can extend
    AlphaEvolve-style matrix search beyond the Appendix A target suite.

- [ ] Track matrix near-integrality prompt/evaluator evidence separately from
      publication-result validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 states that the
    natural-language prompt asked AlphaEvolve to generate near-integral matrix
    solutions, then the reported tensor-decomposition entries were rounded to
    the nearest integer or half-integer to verify exactness. Paper-visible
    evidence should show that this instruction and rounding/evaluation policy
    were part of the search workflow.
  - Current evidence: the matrix-result report contract validates declared
    coefficient-domain fields, exactness certificates, per-seed results,
    artifact hashes, Appendix A target identities, and the checked Strassen
    baseline bundle. Those checks prove that a report is internally
    consistent once produced; they do not prove that candidate prompts carried
    the near-integrality instruction, that evaluators recorded raw-versus-
    rounded coefficients, or that exactness certificates were generated from
    the rounded candidate outputs during the search.
  - Required result: add paper/report evidence fields or artifacts for the
    matrix prompt instruction, rounding policy, raw and rounded coefficient
    diagnostics, per-seed exactness linkage, and prompt/run provenance before
    claiming AlphaEvolve Section 3.1 matrix-search parity.

- [ ] Track matrix sweep-space provenance for AlphaEvolve Figure 9 workflows.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figures 9a-9c show the
    matrix-search program evolving not only tensor update code but also a
    `sweep()` function with `hyper.uniform(...)` ranges for optimizer,
    discretization, noise, clipping, and related search parameters.
  - Current evidence: the matrix-result report contract validates finished
    result metadata and artifact references, but it does not require
    candidate-produced sweep-space declarations, user-provided hyper-library
    identity, sampled configuration records, per-sweep losses/ranks, or
    linkage from the winning sweep configuration to the published exact
    decomposition/certificate.
  - Required result: add paper-facing matrix benchmark artifacts for evolved
    sweep functions, hyperparameter range provenance, sampled sweep ids,
    per-sweep/per-seed outcomes, and final certificate linkage before treating
    LibreEvolve matrix runs as faithful to AlphaEvolve's Figure 4/Figure 9
    tensor-decomposition search workflow.

- [ ] Preserve the Strassen baseline bundle as pinned paper evidence.
  - Paper evidence: AlphaEvolve's matrix section and Appendix A publish exact
    matrix-multiplication algorithms and companion artifacts as auditable
    result evidence. A local baseline helper is useful only if the generated
    algorithm, certificate, report, inventory, and notebook are durable enough
    for paper-index readers to inspect or reproduce from a fresh checkout.
  - Current gap: `write_strassen_2x2_publication_bundle()` is tested and can
    emit a checked `mm_2x2x2` Strassen bundle under a temporary or
    caller-provided root, but the repository does not contain committed
    `matrix/mm_2x2x2/` output files and the paper-manifest gate does not
    regenerate or validate that bundle. `papers/README.md` can describe the
    helper, but the paper index has no pinned artifact digest set proving the
    helper-generated baseline files are present, reproducible, or unchanged.
  - Required result: add paper-facing Strassen baseline artifact provenance:
    generation command, output root, report path, algorithm/certificate/
    notebook/inventory paths, expected SHA-256 hashes and byte counts,
    validation command, and README/ROADMAP wording that distinguishes
    helper-generated evidence from committed or CI-regenerated artifacts. This
    should remain scoped to the one known baseline and not imply Appendix A
    suite discovery.

- [ ] Track Appendix A Figure 9a-9c magnified matrix-diff exhibits as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A says Figures 9a
    to 9c are the magnified version of Figure 4's left panel and show the
    program that discovers a rank-48 decomposition for multiplying two 4x4
    matrices, split across three source/diff panels. The panels show concrete
    code-change components: Adam to AdamW, scaled complex initialization,
    gradient/decomposition/target noise, soft clipping, hallucination and
    discretization losses, large-value penalties, and named `hyper` sweep
    fields.
  - Current gap: paper-facing TODOs cover the main Figure 4 exhibit and the
    Figure 9 sweep-space workflow, but they do not require Figure 9a/9b/9c
    exhibit records: panel IDs, PDF page/caption locations, exact code line
    spans, source/diff excerpt artifacts and hashes, rendered/OCR text
    validation, ordered continuity across the three panels, semantic
    component labels for the source changes, or links from each panel to matrix
    target rows, sweep metadata, certificates, and companion notebook/source
    evidence.
  - Required result: add paper-facing Figure 9 exhibit records and validation
    for each panel, including figure/panel id, source location, ordered
    line-span coverage, exact source/diff artifact hashes, rendered visual/text
    hashes, target/result-row mapping, semantic component inventories for the
    displayed optimizer/init/noise/clipping/loss/discretization/sweep changes,
    sweep-field linkage, certificate/notebook links, and README/ROADMAP wording
    that separates reproduced Appendix A magnified-diff exhibits from Figure 4
    main-text evidence and generic sweep-space provenance.

- [ ] Track Figure 4 matrix-discovery exhibit provenance as paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 4 presents the
    main-text matrix multiplication discovery exhibit, including a concrete
    4x4 tensor-decomposition search-program diff and the surrounding
    Section 3.1/Table 2 matrix rank-improvement context. Its caption says the
    displayed discovery required 15 mutations and made non-trivial changes to
    the optimizer, weight initialization, loss function, and hyperparameter
    sweep.
  - Current gap: matrix paper evidence tracks Appendix A target identities,
    report validation, companion Colab TODOs, near-integrality, scalar-field,
    baseline, and Figure 9 sweep-space gaps. It does not preserve the
    paper-facing Figure 4 exhibit as its own evidence object with stable
    exhibit id, exact source diff excerpt artifact/hash, selected matrix target
    and result-row links, caption values, visual/text artifact hashes,
    rendering/source parameters, the accepted 15-mutation sequence, component
    labels for optimizer/initialization/loss/sweep changes, or links from the
    displayed figure to report, certificate, notebook, and source-paper
    artifacts.
  - Required result: add paper-facing Figure 4 exhibit records and validation:
    figure/exhibit id, source PDF page/caption location, target ids, exact diff
    excerpt artifact and hash, Table 2/Appendix A row mappings, rank/baseline
    values, rendered artifact paths/hashes, accepted mutation count and
    component lineage, and links to decomposition reports, exactness
    certificates, companion notebook/source evidence, and README/ROADMAP
    wording that separates main-text exhibit reproduction from general matrix
    benchmark coverage.

- [ ] Track matrix baseline-component provenance for Section 3.1 workflows.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 says the
    matrix-decomposition work starts from the problem description and a
    standard gradient-based algorithm including an initializer, reconstruction
    loss function, and Adam optimizer, then evolves increasingly sophisticated
    tensor-decomposition algorithms.
  - Current evidence: the paper-facing matrix TODOs track result reports,
    Appendix A target curation, near-integrality prompt/evaluator evidence,
    sweep-space provenance, scalar-field evidence, resource-frontier records,
    and final artifact/certificate availability. They do not require a
    paper-facing run record for the generation-0 matrix solver components,
    their source hashes/configuration, fixed-versus-mutable boundaries, or
    mutation lineage showing how later accepted candidates changed the
    initializer, loss, optimizer, or surrounding search program.
  - Required result: add paper-facing matrix run artifacts that inventory the
    initial gradient-based algorithm, record initializer/loss/optimizer
    configuration and hashes, declare mutable and fixed scopes, include
    generation-0 baseline outcomes, and link accepted mutations to changed
    baseline components before claiming Section 3.1 workflow parity.

- [ ] Track matrix scalar-field evidence for complex-valued Appendix A claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 says some improved
    matrix algorithms, including selected Appendix A targets, use
    complex-valued multiplications and can be used for exact multiplication of
    complex or real-valued matrices. Section 3.1 also contrasts the
    characteristic-0 rank-48 result with finite-field-only prior work.
  - Current evidence: the matrix-result report contract validates target
    identity, dimensions, best rank, seed hit fraction, exactness status,
    coefficient domain, and algorithm/certificate/notebook artifacts. Its
    `coefficient_domain` values do not record scalar field, complex
    coefficient representation, field characteristic, real-versus-complex
    applicability, or certificate scope for those claims.
  - Required result: add paper/report evidence for scalar field, exact complex
    coefficient data, characteristic/applicability claims, and certificate
    verification scope before claiming AlphaEvolve-comparable complex-valued
    matrix results.

- [ ] Track matrix tensor-rank applicability and recursive-use caveats.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 reports matrix
    results as low-rank tensor decompositions and footnote 3 says that some
    algorithms use fewer than 49 multiplications but do not correspond to
    decompositions of the matrix multiplication tensor and cannot be applied
    recursively to larger matrix multiplication.
  - Current gap: the paper-facing Appendix A registry/status and matrix result
    contract store target ids, dimensions, rank values, outcomes, exactness,
    coefficient domain, and artifacts, but not whether an algorithm is a
    tensor decomposition versus another multiplication algorithm, whether the
    construction is recursively applicable, whether the certificate proves the
    target tensor identity, or whether docs should qualify comparisons against
    non-tensor or finite-field-only prior algorithms.
  - Required result: add paper-facing metadata for matrix rank claims:
    algorithm kind, tensor-decomposition certificate scope, recursive
    applicability, source note/page or footnote locator, and docs validation
    that rank/outcome wording does not treat non-recursive multiplication
    algorithms as comparable tensor-rank baselines.

- [ ] Generate independent certification evidence for paper-level result
  claims.
  - Paper evidence: the AlphaEvolve paper distinguishes evaluator scores from
    stronger confirmation for deployed or claimed discoveries. Section 3.3.1
    reports post-deployment fleet measurements confirming a scheduling
    heuristic, and Section 3.3.4 states that the final FlashAttention changes
    were confirmed by human experts for all possible inputs.
  - Current evidence: `papers/README.md` correctly scopes the checked-in
    `circle_packing` and `matrix_multiplication` examples as smoke fixtures,
    and the active benchmark TODOs require harder validators, SOTA thresholds,
    artifacts, and equal-budget reports.
    `libreevolve.paper_result_certification.v1` now defines and tests a
    certification-report contract that separates local-validator records from
    paper-claim-ready independent certifications, requires verifier
    identity/independence, claim scope, verdict, passed evidence,
    evidence-kind-specific artifact requirements, and hashed artifact records,
    and renders summary readiness.
    `libreevolve.paper_result_certification_artifact_inventory.v1` now
    verifies the certification report's evidence and artifact records against
    concrete files under an explicit artifact root, checking safe relative
    paths, existence, SHA-256 hashes, byte counts, per-record status, and
    aggregate missing/mismatch/invalid counts. `validate_certification_evidence_bundle()`
    now validates certification reports together with their artifact inventory,
    requiring matching claim, benchmark, candidate, report schema, record hash,
    and zero missing/mismatch/invalid evidence before paper-claim readiness is
    accepted as a bundle. It still does not provide independent verifier
    scripts, external/human-review records,
    deployment/simulator confirmation records, or generated signed/exact
    certificate artifacts for actual benchmark claims.
  - Required result: connect benchmark outputs to real independent verifier
    scripts, exact certificate generation, reviewer/deployment provenance, and
    external confirmation artifacts before treating local evaluator validity as
    AlphaEvolve-style confirmed result evidence. The remaining gap is
    producing those independent evidence files from real verification
    workflows, not checking declared files or bundle consistency once a
    certification report names them.

- [ ] Connect systems-style benchmarks to held-out and reference-correctness
  evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3 evaluates
    production-oriented discoveries beyond the optimization loop: the Borg
    scheduling heuristic is optimized with historical simulator feedback, then
    measured on unseen recent workloads and post-deployment fleet data; the
    Gemini kernel heuristic is trained on collected input shapes and evaluated
    on held-out shapes; the FlashAttention IR task checks each modification
    against reference code on randomized inputs before expert confirmation.
  - Current evidence: the active benchmark and certification TODOs require
    stronger validators, artifacts, SOTA thresholds, and independent
    certification. `libreevolve.systems_result_report.v1` now defines and
    tests a report contract that separates optimization inputs from
    held-out/generalization gates and reference-correctness gates, persists
    case-set hashes, sample counts/seeds, finite metrics, artifact hashes,
    passed-gate artifact-kind requirements, and optional certification linkage
    that cannot contradict readiness claims. It rejects `alphaevolve_ready`
    claims unless held-out and reference gates passed or are explicitly
    documented as not applicable. That not-applicable policy is still
    domain-agnostic: the validator does not yet require randomized
    reference-code checks for kernel/compiler-style reports, unseen workload
    gates for scheduling reports, or deployment/hardware/expert confirmation
    gates for domains where Section 3.3 used those evidence types.
    `libreevolve.systems_result_artifact_inventory.v1` now verifies declared
    systems report artifacts against concrete files under an explicit artifact
    root, checking safe relative paths, existence, SHA-256 hashes, and byte
    counts for the metrics, heldout-report, reference-report, and summary
    evidence files. `validate_systems_evidence_bundle()` now validates systems
    reports together with their artifact inventory, requiring matching
    benchmark, candidate, domain, report schema, inventory status, record hash,
    and zero missing/mismatch/invalid evidence before accepting bundled
    AlphaEvolve readiness. `libreevolve.systems_evidence_bundle.v1` now wraps
    embedded systems report and inventory records with stable embedded-record
    hashes, inventory-record hash linkage, benchmark/candidate/domain identity
    checks, and readiness consistency validation.
  - Required result: connect compiler, hardware, kernel, scheduling, or systems
    fixtures to this report format, implement real unseen evaluation cases and
    randomized/reference-correctness checks, add domain-specific rules for when
    `not_applicable` gates are allowed, and emit report artifacts that
    distinguish loop feedback from held-out, deployment, and certification
    evidence. The remaining paper gap is producing those evidence files from
    real fixture runs and enforcing domain-specific readiness gates, not
    verifying the declared files, report/inventory consistency, or
    evidence-bundle consistency once a report names them.

- [ ] Record Section 3.3 result-claim metric calibration for systems reports.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3 reports specific
    claim magnitudes and units for engineering outcomes: Borg scheduling
    recovered about 0.7% fleet-wide compute resources, Gemini/Pallas kernels
    achieved 23% average kernel speedup and 1% Gemini training-time reduction,
    hardware RTL optimization targeted power and area, and FlashAttention IR
    changes delivered 32% kernel and 15% pre/postprocessing speedups. The
    Gemini/Pallas section also reports reducing kernel optimization time from
    several months of dedicated engineering effort to days of automated
    experimentation, plus deployment and research/engineering-velocity impact.
  - Current gap: current paper/status wording and
    `libreevolve.systems_result_report.v1` can require finite metrics, case
    hashes, artifacts, and domain readiness evidence, but they do not require
    paper-facing records that identify which finite metric is the published
    claim, what unit and denominator it uses, which baseline and before/after
    window it compares against, how repeated measurements are aggregated, or
    what deployment/runtime/synthesis context makes the value comparable to
    the AlphaEvolve claim.
  - Required result: add paper-facing claim calibration records for systems
    results before treating finite metrics as reproduced Section 3.3 outcomes:
    scheduling resource-recovery denominator/window; kernel speedup and
    training-time reduction baseline/runtime/shape-split aggregation; RTL
    power/area/PPA units and synthesis flow; and compiler kernel versus
    pre/postprocessing speedup attribution with randomized-reference and
    tolerance provenance. Also capture paper-facing engineering-effort and
    deployment-velocity calibration for kernel claims, including manual-tuning
    baseline duration, automated-experiment duration, workflow affected, and
    production adoption status.

- [ ] Track practical-application owner and reviewer provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3 presents
    practical systems discoveries as production-facing work in Borg scheduling,
    Gemini/Pallas kernels, TPU RTL, and XLA/FlashAttention IR. The
    Acknowledgements and Contributions sections also identify application
    co-leads, domain advisors, reviewers, validation infrastructure owners,
    TPU designers, and XLA modification reviewers tied to those systems
    results.
  - Current gap: paper/status records and
    `libreevolve.systems_result_report.v1` can track metrics, artifacts,
    held-out gates, reference-correctness gates, and domain-readiness evidence,
    but they do not preserve paper-facing provenance for the domain owners and
    reviewers behind a practical result: owner role, reviewer scope,
    validation-infrastructure owner, workload/shape/capacity data steward,
    production approver, approval state, or how each responsible role maps to
    a calibrated Section 3.3-style claim.
  - Required result: add paper-facing owner/reviewer provenance records for
    systems results before presenting local reports as AlphaEvolve-style
    practical-application evidence, including domain, responsible team or role
    labels, review/signoff scope, validation/source ownership, deployment or
    approval state, artifact links, and wording that separates local benchmark
    evidence from domain-owner validated production claims.

- [ ] Track self-improvement and distillation evidence for Discussion claims.
  - Paper evidence: AlphaEvolve's Discussion says practical discoveries can
    improve its own infrastructure and future base LLMs, while distilling
    AlphaEvolve-augmented performance into the next generation of base models
    is a natural next step.
  - Current gap: `papers/README.md`, benchmark reports, and runtime manifests
    do not yet identify any LibreEvolve infrastructure component as an evolved
    optimization target, do not connect an evolved candidate to measured
    improvements in the tool's own runtime/provider/compiler/benchmark
    infrastructure, and do not define distillation datasets, training runs, or
    model-evaluation artifacts derived from evolved programs.
  - Required result: add paper-facing evidence boundaries for self-improving
    infrastructure and model-uplift claims: component identity, optimization
    objective, before/after measurements, deployment or adoption status,
    rollback/safety review, provenance linking the candidate to LibreEvolve's
    own execution path, and any distillation dataset/training/evaluation
    artifacts. Until then, keep Discussion-style self-improvement and
    distillation wording scoped as AlphaEvolve context rather than LibreEvolve
    capability.

- [ ] Track self-improvement feedback-loop cadence and environment-expansion
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Discussion says current
    gains from improving AlphaEvolve's own infrastructure and future base LLMs
    are moderate, that feedback loops for improving the next AlphaEvolve
    version are on the order of months, and that these improvements should
    make the value of setting up more robust-evaluator environments more
    widely recognized.
  - Current gap: paper-facing self-improvement TODOs require component
    identity, before/after measurements, deployment/adoption, rollback/safety,
    and distillation artifacts. They do not preserve cadence or return-on-
    environment evidence: which improvement loop affected a next version, how
    long that loop took, how moderate the gain was, or how the gain changed
    the expected value of creating more robust evaluation environments.
  - Required result: add paper/report evidence for self-improvement loop
    cadence and environment expansion with loop ids, optimized component,
    next-version target, start/end dates or elapsed months, measured gain,
    environment setup/maintenance cost, expected and realized discovery value,
    robust-evaluator readiness, and README/ROADMAP wording that separates
    months-scale feedback-loop economics from generic self-improvement or
    distillation capability.

- [ ] Record Borg scheduling problem-formulation evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.1 frames Google
    Borg scheduling as an online vector bin-packing problem: machines are bins
    with CPU and memory capacity, pending jobs are items with CPU and memory
    requirements, stranded resources motivate the objective, and AlphaEvolve
    receives simulator feedback from historical workload and capacity
    snapshots.
  - Current gap: paper-facing systems TODOs cover generic systems reports,
    claim-calibrated metrics, domain owners, ranking-only scheduling safety,
    mission-critical deployment evidence, and Figure 6 exhibit provenance.
    They do not require a scheduling report to preserve the actual problem
    formulation: bin/item schema, resource units, historical workload/capacity
    source identities, stranded-resource objective, simulator input hashes, or
    the mapping from those inputs to the heuristic's `required` and `free`
    CPU/memory features.
  - Required result: add paper/report evidence for Borg-style scheduling
    formulation: vector-bin-packing domain label, machine/bin and job/item
    records, CPU/memory unit definitions and denominators, workload/capacity
    snapshot provenance, stranded-resource objective linkage, simulator input
    artifact hashes, and README/ROADMAP wording that separates problem
    formulation from ranking-only safety, deployment metrics, and Figure 6
    exhibit reproduction.

- [ ] Record scheduling feasibility-boundary evidence for Borg-style results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.1 states that
    AlphaEvolve's scheduling heuristic scores machines after Borg has already
    determined that they are available and capable of running the pending job;
    the heuristic only influences ranking among feasible machines, so
    decisions are effectively correct by construction.
  - Current gap: current systems report contracts are domain-agnostic and can
    accept scheduling reference-correctness as `not_applicable` with a
    rationale. They do not require paper-facing evidence for the external
    feasibility filter, ranking-only scope, resource/capacity invariants, or
    proof that the candidate did not alter job admission or placement
    constraints directly.
  - Required result: add scheduling report fields and validation for feasible
    candidate-set provenance, ranking-only function boundaries, resource
    invariant checks, simulator/admission-boundary artifacts, and
    deployment/simulator confirmation before claiming AlphaEvolve-comparable
    Borg-style scheduling evidence.

- [ ] Record scheduling interpretability and mission-critical deployment
      evidence for Borg-style results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.1 says
    AlphaEvolve was chosen over deep reinforcement learning for scheduling
    because its code solution performed better and had advantages in
    interpretability, debuggability, predictability, and ease of deployment,
    which the paper calls essential for a mission-critical system.
  - Current gap: current systems report contracts can record optimization,
    held-out, reference-correctness, artifact, and certification-link
    evidence, and the feasibility-boundary TODO above tracks ranking-only
    safety. They do not require paper-facing evidence for heuristic
    interpretability, operator/debug review, predictable behavior under
    capacity edge cases, deployment ergonomics, or a comparison against a
    less interpretable learned-policy baseline.
  - Required result: add scheduling report fields and validation for
    interpretable code/rule structure, debuggability and operator-review
    artifacts, predictability or monotonicity checks, rollout/deployment-risk
    evidence, and black-box-baseline comparison before claiming
    AlphaEvolve-comparable mission-critical scheduling readiness.

- [ ] Track Figure 6 scheduling-heuristic exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 6 shows the concrete
    Borg scheduling heuristic `alpha_evolve_score(required, free)` with
    CPU/memory residual terms and a rendered residual heatmap. Section 3.3.1
    connects that heuristic to historical simulator feedback, unseen recent
    workload measurements, deployment, and about 0.7% fleet-wide compute
    resource recovery.
  - Current gap: paper-facing systems TODOs require claim-calibrated metrics,
    ranking-only scheduling safety, and interpretability/deployment evidence,
    but no evidence row or report schema maps a Figure 6 exhibit to exact
    heuristic code, residual-feature definitions and units, heatmap data,
    rendering parameters, visual artifact paths/hashes, baseline production
    heuristic identity, simulator/held-out/deployment reports, or a
    Section 3.3 claim-calibration record.
  - Required result: add Figure 6-style exhibit metadata with a stable exhibit
    ID, scheduling benchmark/candidate link, exact heuristic source artifact
    and hash, residual grid/units, baseline heuristic provenance, heatmap data
    and rendered visual artifacts with hashes, rendering parameters,
    simulator/held-out/deployment report links, and documentation that
    separates reproduced systems figures from generic scheduling readiness.

- [ ] Track Figure 7 Pallas tiling-problem exhibit provenance as paper
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 7 visualizes the
    tiling heuristic problem for a matrix product `A B = C`, with dimensions
    `M`, `N`, and `P`. Section 3.3.2 says the heuristic must choose tile sizes
    while accounting for accelerator optimal shapes, memory capacity, fused
    operations, and compiler intricacies.
  - Current gap: paper-facing Pallas/kernel TODOs require shape-corpus
    provenance, train/evaluation split evidence, real TPU runtime artifacts,
    baseline heuristic identity, tiling-only boundaries, and
    correctness-by-construction scope. They do not map Figure 7 to an exhibit
    record with matrix-shape variable definitions, tile-parameter schema,
    accelerator/memory/fusion/compiler-context annotations, diagram source
    data, visual artifact paths/hashes, rendering parameters, or links to the
    runtime/shape-corpus reports.
  - Required result: add Figure 7-style exhibit metadata with a stable exhibit
    ID, kernel benchmark/candidate link, matrix dimension and tile-parameter
    definitions, accelerator and shape-corpus context links, diagram/JSON data
    plus rendered visual artifacts with hashes, rendering parameters, baseline
    heuristic relation, and documentation that separates reproduced Pallas
    figures from executed kernel-runtime evidence.

- [ ] Record kernel-tiling shape-corpus evidence for Gemini/Pallas results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.2 says
    AlphaEvolve optimized Pallas matrix-multiplication tiling heuristics by
    minimizing actual runtime on real TPU accelerators. It collected realistic
    input shapes from kernel users, split them into training and evaluation
    halves, compared against an expert-designed heuristic, and preserved
    correctness by construction by changing tiling strategy rather than the
    underlying mathematical operation.
  - Current gap: current systems report contracts can name a `kernel` domain
    and final held-out gate, but they do not require paper-facing input-shape
    corpus provenance, deterministic train/eval split evidence, real
    accelerator runtime artifacts, baseline heuristic identity, tiling-only
    output constraints, or correctness-by-construction scope.
  - Required result: add kernel report fields and validation for collected
    input-shape corpora, train/eval split hashes, real accelerator runtime
    measurements, expert-baseline comparison, tiling-parameter constraints,
    unchanged-kernel-math evidence, and deployment/readiness provenance before
    claiming AlphaEvolve-comparable Gemini/Pallas kernel optimization results.

- [ ] Record Pallas autotuning/manual-heuristic baseline workflow evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.2 says
    traditional kernel engineers use search-based autotuning or manually
    crafted heuristics for tiling. Search-based tuning interrupts research
    workflows and must be repeated when input shapes change; manual heuristic
    design is a major bottleneck requiring deep understanding of kernel
    behavior and hardware intricacies. The paper says AlphaEvolve offers a path
    toward automating manual tuning and improving Gemini kernel ergonomics.
  - Current gap: paper-facing Pallas TODOs require input-shape corpus evidence,
    train/eval split hashes, real TPU runtime artifacts, expert-baseline
    comparison, tiling-only correctness, speedup and training-time calibration,
    and production adoption state. They do not require paper/report evidence
    that distinguishes search-based autotuning from manually crafted heuristic
    baselines, records retuning burden for changed shapes, or captures the
    manual-engineering bottleneck and model-developer ergonomics comparison.
  - Required result: add paper/report fields for baseline workflow class
    (`search_autotuning`, `manual_heuristic`, or `hybrid_expert`), autotuning
    search-space and retuning policy, manual authoring/review effort, input
    shape-change sensitivity, hardware-expertise assumptions, ergonomics impact,
    and comparison evidence before describing LibreEvolve kernel reports as
    AlphaEvolve-style automation of Pallas tiling-heuristic work.

- [ ] Record Gemini self-training optimization loop evidence for Pallas
      deployment claims.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.2 states that
    the AlphaEvolve-discovered Pallas tiling heuristic was deployed in
    production, directly enhanced Gemini training efficiency and the Gemini
    team's research and engineering velocity, and was a novel instance where
    Gemini, through AlphaEvolve, optimized its own training process.
  - Current gap: paper-facing Pallas TODOs require runtime speedups, train/eval
    shape evidence, workflow baselines, and production adoption state, while
    a broader Discussion TODO covers generic self-improvement and distillation.
    They do not require a Gemini-specific evidence row tying the evolved kernel
    heuristic to the training workload of the Gemini model family, the
    AlphaEvolve/Gemini relationship, deployment state, before/after training
    metrics, and the self-optimization interpretation.
  - Required result: add paper/report evidence for Gemini self-training loop
    claims: Gemini model/training workload id, AlphaEvolve backend/model-family
    relation, optimized Pallas kernel id, production deployment or rollout
    state, before/after training-time and kernel-runtime measurements,
    engineering-velocity evidence, rollback/safety status, and README/ROADMAP
    wording that distinguishes regular kernel deployment evidence from
    AlphaEvolve-style self-optimization of Gemini's training pipeline.

- [ ] Record RTL/EDA verification evidence for hardware-circuit results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.3 describes
    optimizing Verilog RTL for a TPU arithmetic circuit, reducing power and
    area while preserving functionality. It says the final proposal must pass
    robust verification, was validated by TPU designers, and was also found by
    downstream synthesis tools. It also says the contribution was useful at
    the RTL stage before downstream synthesis, was integrated into an upcoming
    TPU, communicated changes directly in Verilog, fostered trust and simpler
    adoption, and could reduce time to market.
  - Current gap: current systems report contracts do not distinguish generic
    hardware metrics from RTL/EDA evidence. They do not require HDL language
    identity, synthesis or place-and-route tool provenance, PPA metric units,
    equivalence/formal verification artifacts, timing constraints, designer
    signoff, downstream synthesis confirmation, RTL-stage versus synthesis
    workflow placement, standard-language adoption evidence, upcoming-TPU
    integration, or time-to-market impact.
  - Required result: add hardware-domain paper/report fields for Verilog/RTL
    source boundaries, synthesis/PPA provenance, functional equivalence or
    formal verification evidence, timing/power/area constraints, designer or
    independent review signoff, synthesis-tool confirmation, RTL-flow
    contribution timing, hardware-engineer trust/adoption rationale,
    integration target, and deployment/time-to-market evidence before making
    AlphaEvolve-comparable TPU-circuit optimization claims.

- [ ] Record TPU arithmetic-circuit rewrite artifact evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.3 says
    AlphaEvolve optimized an already highly optimized Verilog implementation of
    a key TPU arithmetic circuit within the matrix multiplication unit, and
    found a simple code rewrite that removed unnecessary bits while reducing
    area and power.
  - Current gap: paper-facing hardware TODOs require RTL source boundaries,
    synthesis/PPA provenance, equivalence/formal verification, TPU-designer
    signoff, downstream synthesis confirmation, and adoption/integration
    evidence. They do not require a paper report to preserve the concrete
    rewrite artifact behind the claim: before/after Verilog hashes, changed
    spans, eliminated bit or signal identities, arithmetic-circuit component
    context, matrix-multiplication-unit context, or a semantic link from
    removed bits to PPA and verification records.
  - Required result: add paper/report evidence for the TPU arithmetic-circuit
    rewrite: source and modified Verilog artifact hashes, exact diff or AST
    span records, removed-bit inventory, component and matrix-unit identifiers,
    rewrite-category labels, linkage from eliminated bits to functional
    verification and PPA records, and README/ROADMAP wording that separates
    concrete rewrite provenance from broader RTL/EDA validation evidence.

- [ ] Record Gemini-to-TPU self-contribution evidence for hardware results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.3 says the
    hardware improvement was integrated into an upcoming TPU and represents
    "Gemini's first direct contribution to TPU arithmetic circuits", achieved
    via AlphaEvolve.
  - Current gap: paper-facing hardware TODOs track RTL/EDA verification,
    designer and synthesis-tool signoff, upcoming-TPU integration, Verilog
    adoption, and concrete bit-removal artifacts. They do not separately
    preserve the attribution evidence for the Gemini-to-TPU contribution
    claim: which Gemini/AlphaEvolve model-family produced the edit, which TPU
    arithmetic circuit and TPU generation received it, why it qualifies as a
    first direct contribution, and how that differs from the downstream
    synthesis-tool rediscovery note.
  - Required result: add paper/report evidence for Gemini hardware
    self-contribution claims with model-family/backend identity, TPU and
    arithmetic-circuit identifiers, integration milestone, novelty/firstness
    basis, hardware review/signoff roles, synthesis-tool rediscovery caveat,
    and README/ROADMAP wording that separates RTL optimization evidence from
    the broader claim that Gemini directly contributed to TPU arithmetic
    circuits through AlphaEvolve.

- [ ] Record per-edit reference checks for compiler-generated IR results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.4 says
    AlphaEvolve optimized XLA-generated IR for FlashAttention and surrounding
    pre/postprocessing code; the IR was designed for debugging rather than
    direct developer editing, was compiler-generated and already highly
    optimized, every modification was checked against the reference unmodified
    code on randomized inputs, and the final code was confirmed by human
    experts for all possible inputs.
  - Current gap: current systems result contracts can name a final
    `reference_correctness` gate, but they do not require paper-facing
    per-edit reference-check traces, randomized input generator provenance,
    reference implementation identity, IR-origin/debug-only versus direct-edit
    boundary metadata, compiler-generated/already-optimized baseline
    provenance, numerical tolerance policy, attribution to kernel versus
    pre/postprocessing abstraction levels, or separate final expert signoff
    scope.
  - Required result: add compiler/kernel report fields and validation for
    edit-by-edit randomized reference checks, reference-code hashes,
    input-generator seeds and coverage, IR provenance and editability
    constraints, numerical tolerance/failure policy, abstraction-level
    attribution, and final expert/all-input confirmation before claiming
    AlphaEvolve-comparable compiler-generated IR evidence.

- [ ] Record FlashAttention compiler-stack context evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.4 explains that
    Transformer attention is implemented using FlashAttention; FlashAttention
    is an accelerator kernel in Pallas; higher-level JAX code handles input
    preparation and output postprocessing; XLA translates the implementation
    through multiple IR stages for particular hardware; and AlphaEvolve
    optimizes memory access orchestration or computation scheduling for a
    high-impact inference configuration on GPUs.
  - Current gap: paper-facing compiler TODOs require per-edit randomized
    reference checks, IR-origin/editability metadata, expert signoff, and
    kernel-versus-pre/postprocessing speedup attribution. They do not require
    the report to preserve the stack context that makes the claim specific:
    workload/model configuration, FlashAttention/Pallas kernel identity, JAX
    wrapper boundaries, XLA lowering stage identities, hardware target,
    lowered-IR artifacts, or optimization decision category.
  - Required result: add paper/report evidence for FlashAttention compiler
    stack context: Transformer/model or inference configuration id,
    FlashAttention/Pallas kernel source hash, JAX pre/postprocessing wrapper
    artifact hashes, XLA IR-stage and hardware-target records, lowered-IR
    artifact hashes, memory-orchestration versus scheduling decision labels,
    and README/ROADMAP wording that separates compiler-stack provenance from
    per-edit reference-check evidence and final runtime-speedup claims.

- [ ] Record compiler-adoption path evidence for discovered optimizations.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3.4 says future
    compiler use could involve incorporating discovered optimizations into
    existing compilers for specific use cases, or, longer term, incorporating
    AlphaEvolve into the compiler workflow itself.
  - Current gap: paper-facing compiler TODOs require per-edit reference checks,
    IR provenance, expert signoff, FlashAttention stack context, and speedup
    attribution. They do not require a report to distinguish the paper's two
    adoption paths: a discovered optimization transferred into a conventional
    compiler/pass for a bounded use case versus AlphaEvolve becoming part of
    the compiler workflow. There is no field for target compiler/pass, use-case
    boundary, integration owner, reviewer signoff, rollout/revert state, or
    workflow-handoff semantics.
  - Required result: add paper/report evidence for compiler adoption paths:
    adoption-path enum, target compiler/pass and version, optimization artifact
    hashes, workload/use-case constraints, integration-review records,
    deployment or rollback status, and README/ROADMAP wording that separates
    concrete compiler optimization adoption from longer-term AlphaEvolve
    workflow integration.

- [ ] Keep named AlphaEvolve application-context rows background-only until
  benchmark fixtures exist.
  - Paper evidence: the local paper index includes AlphaEvolve application
    context rows for compiler optimization, computer architecture, multi-agent
    learning, complexity-theory/graph certification, mechanism design, and
    workflow optimization.
  - Current evidence: `papers/README.md` marks Magellan, ArchAgent,
    Multiagent Learning, Hardness of Approximation, Bilateral Trade, and
    Fault2Flow as background-only, with no compiler-heuristic runner,
    architecture-design simulator, CFR/PSRO/game-theoretic evaluator,
    graph/certification benchmark, bilateral-trade distribution benchmark, or
    fault-to-workflow/human-in-the-loop multi-agent benchmark. The roadmap
    requires each local domain paper to either gain a benchmark, link to an
    existing benchmark, or remain background-only, and the systems report
    contracts only validate declared reports once real fixtures emit them.
  - Current gap: the named rows are honest inventory boundaries, not
    AlphaEvolve-style application coverage. There are no runnable fixtures,
    evaluator protocols, target baselines, held-out/reference gates, artifact
    emission workflows, or report instances for those application domains.
  - Required result: either implement and validate concrete fixtures for each
    named application-context row, linking them to benchmark-hardening,
    systems-result, certification, and artifact-inventory reports as
    appropriate, or keep the rows explicitly background-only in
    `papers/README.md` and avoid promoting them in README/ROADMAP claims.

## Paper-Inspired Feature Claims Needing Correction

- [ ] Keep framework and plugin inspiration rows scoped to partial or
  background status.
  - Paper evidence: the local paper index includes GigaEvo, CodeEvolve,
    ThetaEvolve, ImprovEvolve, MadEvolve, CausalEvolve, and DeepEvolve as
    framework/plugin inspiration rows adjacent to the AlphaEvolve target.
  - Current evidence: `papers/README.md` says GigaEvo lacks Redis lifecycle
    database, asyncio DAG engine, insight stage, and concurrent units;
    CodeEvolve lacks crossover, targeted refinement, modular orchestration,
    and context-aware recombination; ThetaEvolve has clipped-reward export but
    no online RL/GRPO training loop, checkpointing, resume, or lazy-penalty
    dynamics; ImprovEvolve has static prompt guidance with false
    execution/enforcement flags; MadEvolve is background only; CausalEvolve is
    fixed token-pattern guidance rather than LLM-discovered causal variables;
    and DeepEvolve remains bounded retrieval context rather than a full
    cross-file debugging loop.
  - Current gap: these rows are honest implementation-status boundaries, not
    completed paper reproductions. The missing systems are paper-specific
    orchestration, training, interface execution, causal reasoning,
    recombination/refinement, domain-evolution reporting, and debug-loop
    behavior.
  - Required result: either implement the paper-specific behavior with
    matching tests/artifacts/metadata for each row, or keep `papers/README.md`,
    README, ROADMAP, and code TODO wording explicit that the current features
    are inspiration-only, approximation, or background-only references.

- [ ] Add whole-run source/workspace integrity reports for run inspection.
  - Paper evidence: AlphaEvolve-scale runs need auditable generated program
    databases, not only a selected best-program display.
  - Current evidence: `libreevolve show` now streams current and legacy
    `history.jsonl` rows and validates source/workspace payload shape for every
    row before printing a best-looking candidate: legacy `code` must be text,
    workspace `files` must map safe candidate paths to text, and `primary_file`
    must be a safe path present in `files`. This prevents malformed unselected,
    invalid, or non-admitted rows from being hidden by the selected row.
  - Required result: add whole-run source/workspace integrity summaries and
    durable query/report surfaces over every candidate's source payloads,
    workspace paths, source hashes, primary-file coherence, and display/truncation
    policy. The remaining gap is not malformed unselected source-payload
    validation or selected-row workspace display.

- [ ] Make DeepEvolve-inspired live retrieval transport audit-grade.
  - Paper evidence: retrieval-driven debugging/refinement treats external
    knowledge as part of the experimental input; the paper-aligned record
    should identify and protect the actual source content used.
  - Current evidence: the local DeepResearch default now uses HTTPS and records
    bounded transport status plus provider payload byte/hash metadata.
    Cache-backed runs can write replay snapshots under
    `plugin_artifacts/deep_research/`, and plugin artifact metadata now
    summarizes those snapshot files with counts, sizes, per-file hashes,
    retention/skipped counters, and an aggregate hash. Candidate/run metadata
    now records retained source rank, provider rank, source identity/content
    hashes, redacted URL transport expectations, and an aggregate selected
    source hash linked to the prompt-visible synthesis. Retained source rows
    with summary/content text now include bounded/redacted
    `libreevolve.retrieval_source_content_snapshot.v1` snapshots with raw and
    stored hashes. Retained source rows also include
    `query_term_overlap_audit_v1` relevance scores derived from deterministic
    query term/source text overlap. Provider order remains the default
    retained-source order, while opt-in
    `source_ranking_policy="query_overlap_score_desc_v1"` reorders retained
    sources by query-overlap score with provider rank as a tie-breaker. Events,
    active prompt context, and cache snapshots record the policy, ranking hash,
    score hash, and whether relevance affected ordering. Active prompt-visible
    DeepResearch context now records
    `libreevolve.deep_research_active_context.v1` metadata with the exact event
    index, synthesis/raw-result hashes, query hash, cache fields,
    retained-source ranking hash fields, and transport-policy status. It still
    lacks unbounded raw provider/source payload persistence, unbounded
    source-content artifacts, and learned or externally scored ranked-source
    scoring/selection rationale beyond deterministic query-overlap ranking.
    Retrieval events and cache snapshots now retain bounded/redacted
    provider-result snapshots with raw and stored hashes. When a cache directory
    is configured and retention allows text, live retrieval also writes
    `libreevolve.retrieval_payload_artifact.v1` sidecars for full
    secret-redacted provider payloads and retained source-content payloads that
    fit a 64,000-byte per-artifact budget; oversized payloads become
    metadata-only omitted artifacts, and plugin artifact metadata reports
    provider-result snapshot and payload-artifact counts and hashes.
    `libreevolve.retrieval_payload_artifact_inventory.v1` now verifies event
    or plugin-metadata sidecar references against an artifact root, including
    safe relative paths, file existence, SHA-256 hashes, byte counts, artifact
    schema, selected sidecar metadata, aggregate missing/mismatch/invalid
    counts, and a stable records hash.
    `libreevolve.retrieval_source_ranking_provenance.v1` now verifies event,
    metadata, or cache-snapshot retained-source ranking records by recomputing
    selected-source and query-relevance hashes, checking retained-rank
    sequence and source counts, and comparing synthesis hashes when retained
    synthesis text is available. Retained sources and event metadata now
    include `libreevolve.retrieval_source_content_trust_policy.v1`, which
    classifies redacted sidecar, metadata-only oversized sidecar, bounded
    snapshot, hash-only, and missing content evidence, plus replayable-evidence
    counts and record hashes. Query events now also include
    `libreevolve.retrieval_evidence_boundary_policy.v1`, which explicitly
    records that raw provider/source payloads, TLS certificate chains, and
    semantic verification are outside the current retained-evidence boundary,
    while linking the retained payload, source-content, and transport evidence
    states.
    `libreevolve.retrieval_transport_policy.v1` now classifies HTTPS request
    state, redirects, HTTP status class, payload hash presence, oversized
    responses, missing custom-provider transport, and TLS/certificate-looking
    failures as audit-grade, degraded, or unauditable, but it is still a
    bounded event policy rather than a replayable transport decision tree.
    Retained source rows now include
    `libreevolve.retrieval_source_grounding_policy.v1` lexical grounding
    records, and event/cache snapshots include an aggregate
    `source_grounding_policy` with source counts, lexically grounded source
    counts, and a records hash. Active prompt context links to the same
    grounding aggregate. This is deterministic lexical provenance, not semantic
    source verification. Query events now also include
    `libreevolve.retrieval_context_audit_policy.v1`, which ties the exact
    prompt-visible retrieval context to the retained transport,
    source-content, evidence-boundary, and grounding states and classifies it
    as audit-grade bounded replay evidence, audit-grade bounded snapshot
    evidence, degraded evidence, or unauditable evidence while still marking it
    as untrusted, non-authoritative prompt context. Focused tests cover default
    arXiv bounded-snapshot evidence, unauditable custom string retrieval, and a
    custom HTTPS provider with replayable redacted source payload artifacts.
    `libreevolve.retrieval_semantic_boundary_audit.v1` now verifies event,
    plugin-metadata, or cache-snapshot records preserve the current bounded,
    non-semantic evidence boundary and reports overclaims of semantic
    verification, full replay readiness, raw provider/source payload retention,
    TLS certificate-chain retention, or authoritative prompt context.
    `runtime.retrieval.evidence_coverage` now records
    `libreevolve.retrieval_evidence_coverage.v1` run-level coverage counts for
    retained retrieval evidence surfaces and
    `libreevolve.retrieval_evidence_coverage_validation.v1` rejects raw
    provider/source payload, semantic-verification, learned-ranking,
    TLS-replay, and full-replay overclaims.
    Retrieval query inputs now include bounded task-description,
    explicit-context, recent failure-history, local paper manifest title/id, and
    recent proposal-hypothesis terms as well as best-program fitness, metrics,
    and code/file terms. The remaining replay gap is DeepResearch-specific
    provider-output/transport replay integrated with resumed runtime state, not
    the current core full-runtime restore bundle for compatible RNG,
    scheduler, archive, and budget surfaces.
  - Required result: persist unbounded raw provider payload snapshots or a
    stronger raw-evidence preservation model, define
    learned or externally scored ranked-source scoring/selection checks beyond
    deterministic query-overlap ranking, semantic source-content verification
    beyond lexical grounding, and
    replayable redirect/TLS decision evidence before
    claiming DeepEvolve-style retrieval is reproducible and audit-grade. The
    remaining paper gap is not retrieval payload sidecar inventory
    verification, deterministic retained-source ranking-provenance
    validation, semantic-boundary overclaim auditing, run-level retrieval
    evidence coverage validation, or the core full-runtime restore bundle that
    deliberately excludes provider-output replay.

- [ ] Track official 2026 AlphaEvolve impact article as a separate source
      surface.
  - Paper/source evidence: Google DeepMind published
    `AlphaEvolve: How our Gemini-powered coding agent is scaling impact across
    fields` on May 7, 2026. The article describes AlphaEvolve impact after the
    original 2025 launch and names domains and claims not covered by the
    original white paper alone: DeepConsensus error reduction, AC Optimal Power
    Flow feasibility improvement, Earth AI accuracy gain, Willow
    quantum-circuit optimization, public gallery examples, next-generation TPU
    design, cache replacement policies, Spanner write amplification, compiler
    storage footprint, Google Cloud/customer deployments, and UI/API scaling
    contributors.
  - Current gap: the paper cache and TODOs track `2506.13131`, the original
    companion Colab/repository, the May 2025 DeepMind announcement, follow-on
    mathematical-problem sources, and selected later theoretical-CS papers.
    They do not preserve this 2026 official impact article as a source row,
    claim surface, outbound-link inventory, customer/deployment evidence
    boundary, or attribution record.
  - Required result: extend paper/source manifests with the 2026 impact
    article URL, publication date, author/team, title, retrieval digest,
    linked sources, claim ids and categories, values/units/baselines, evidence
    status for each linked paper/repository/customer source, public-gallery
    and UI/API attribution metadata, and docs checks that keep impact-article
    claims separate from original specification, reproduced benchmark
    evidence, and LibreEvolve feature support.

- [ ] Track AlphaEvolve FHE-on-TPU paper and application evidence.
  - Paper/source evidence: arXiv `2605.14718`, submitted May 14, 2026, is
    titled `Adapting AlphaEvolve to Optimize Fully Homomorphic Encryption on
    TPUs`. Its abstract says FHE deployment is limited by computational
    overhead; AlphaEvolve is used to automate hardware-aware cryptographic
    kernel optimization; real-world hardware execution and correctness tests
    guide the search; and TFHE/Jaxite plus CKKS/CROSS primitives are evaluated
    on Google Cloud TPUv5e with reported 2.5x, 1.31x, and 1.18x latency
    improvements over human-engineered state of the art.
  - Current gap: the paper manifest, paper index, and TODO coverage do not
    include `2605.14718`. Existing AlphaEvolve application rows include
    compiler, architecture, systems, mechanism-design, workflow, and
    theoretical-CS contexts, but no FHE/cryptography-on-accelerator row, no
    cached PDF/hash, no source-status table entry, and no benchmark/report
    boundary for TPU-executed cryptographic kernels.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.14718`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve, FHE scheme and primitive taxonomy, TPUv5e
    hardware-execution evidence, correctness-test and benchmark metadata,
    reported latency-speedup claims, linked code/artifact availability if any,
    and TODO/README/ROADMAP wording that treats it as a missing application
    benchmark rather than existing LibreEvolve support.

- [ ] Track AlphaEvolve intentmaking/sensemaking HCI paper evidence.
  - Paper/source evidence: arXiv `2605.05921`, submitted May 7, 2026, is
    titled `Intentmaking and Sensemaking: Human Interaction with AI-Guided
    Mathematical Discovery`. Its abstract reports a formative user study with
    11 expert mathematicians who used AlphaEvolve to tackle advanced problems,
    introduces intentmaking as iterative discovery/refinement of experimental
    goals through active system interaction, pairs it with sensemaking over
    results, and argues for AI scientific-discovery tools as collaborative
    instruments.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.05921`. Existing source rows cover the original
    AlphaEvolve specification, follow-on math repositories, impact articles,
    and application-domain papers, but not the human-interaction/user-study
    evidence surface, intentmaking taxonomy, session-trace requirements,
    dashboard/UI artifacts, or privacy/redaction boundaries for study data.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.05921`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve, study-design metadata, participant-count and
    problem-domain records, intentmaking/sensemaking taxonomy, UI/session
    artifact availability, privacy/redaction policy, and TODO/README/ROADMAP
    wording that treats it as HCI/source evidence rather than implemented
    LibreEvolve interaction support.

- [ ] Track AlphaEvolve radar power-allocation paper evidence.
  - Paper/source evidence: arXiv `2605.01794`, submitted May 3, 2026, is
    titled `Discover Fast Power Allocation Solution for Multi-Target Tracking
    via AlphaEvolve Evolution`. Its abstract proposes an AlphaEvolve-driven
    paradigm for efficient radar resource allocation, evolving an
    interpretable scoring function from physically inspired features and
    converting it into feasible power allocations through a deterministic
    constraint-satisfying transformation. It reports 1.51% average relative
    performance loss, generalization across diverse scenarios and target
    counts, and more than three orders of magnitude speedup over conventional
    iterative solvers.
  - Current gap: the paper manifest, paper index, and TODO coverage do not
    include `2605.01794`. Existing AlphaEvolve application-source rows do not
    capture radar tracking, real-time resource allocation, power-allocation
    constraints, physically inspired feature encodings, symbolic closed-form
    policy artifacts, generalization splits, or iterative-solver baselines.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.01794`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve, radar task taxonomy, scenario and target-count
    metadata, evolved scoring-function and feasibility-transform artifacts,
    baseline solver identities, tracking-performance and speedup metrics,
    code/artifact availability if any, and README/ROADMAP wording that treats
    it as missing application evidence rather than implemented LibreEvolve
    support.

- [ ] Track EvoX adaptive meta-evolution paper evidence.
  - Paper/source evidence: arXiv `2602.23413`, submitted February 26, 2026 and
    last revised March 16, 2026, is titled `EvoX: Meta-Evolution for
    Automated Discovery`. Its abstract says AlphaEvolve and related
    LLM-driven evolutionary systems depend on search strategy choices over
    prior evaluated solutions; fixed strategies with predefined knobs such as
    explore/exploit ratios may fail to adapt; and EvoX jointly evolves
    candidate solutions and the search strategies used to generate them,
    reporting majority-task wins over AlphaEvolve, OpenEvolve, GEPA, and
    ShinkaEvolve across nearly 200 real-world optimization tasks.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2602.23413`. Existing source rows cover AlphaEvolve, selected
    application papers, follow-on math/problem repositories, and original
    LibreEvolve fixed-strategy behavior, but not adaptive meta-evolution,
    strategy self-optimization, strategy-state traces, cross-task dynamic
    search-policy adaptation, or benchmark comparisons against EvoX.
  - Required result: add paper-manifest and paper-index coverage for
    `2602.23413`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve fixed mixed parent selection,
    adaptive strategy representation, controller/provenance artifacts, task
    taxonomy, baseline method identities, metric definitions, win-rate and
    token-efficiency claims, ablation evidence, code/artifact availability if
    any, and README/ROADMAP wording that treats EvoX as missing paper evidence
    rather than implemented LibreEvolve support.

- [ ] Track DeltaEvolve semantic-delta context paper evidence.
  - Paper/source evidence: arXiv `2602.02919`, submitted February 2, 2026, is
    titled `DeltaEvolve: Accelerating Scientific Discovery through
    Momentum-Driven Evolution`. Its abstract says AlphaEvolve and similar
    LLM-driven evolutionary systems use full-code histories that are
    context-inefficient and may dilute core algorithmic ideas; DeltaEvolve
    replaces that context with structured semantic deltas explaining how and
    why modifications between successive nodes affect performance, organized
    through a multi-level database and progressive disclosure mechanism.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2602.02919`. Existing source rows cover AlphaEvolve,
    prompt/history artifacts, failed-proposal snippets, EvoX adaptive strategy
    gates, and selected application papers, but not semantic-delta memory,
    node-transition effect attribution, progressive context disclosure, or
    token-efficiency comparisons against full-code histories.
  - Required result: add paper-manifest and paper-index coverage for
    `2602.02919`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve prompt/context policy,
    semantic-delta schema, node-transition provenance, performance-effect
    attribution, multi-level database/index metadata, progressive-disclosure
    policy, token-accounting metrics, scientific-task benchmark taxonomy,
    baseline method identities, code/artifact availability if any, and
    README/ROADMAP wording that treats DeltaEvolve as missing paper evidence
    rather than implemented LibreEvolve support.

- [ ] Track MLEvolve long-horizon ML-engineering paper evidence.
  - Paper/source evidence: arXiv `2606.06473`, submitted June 4, 2026, is
    titled `MLEvolve: A Self-Evolving Framework for Automated Machine
    Learning Algorithm Discovery`. Its abstract says long-horizon MLE agents
    suffer from inter-branch information isolation, memoryless search, and
    lack of hierarchical control; MLEvolve addresses this with Progressive
    MCGS, graph-based reference edges, entropy-inspired progressive
    scheduling, Retrospective Memory, and adaptive coding modes; and it
    reports MLE-Bench state-of-the-art performance under a 12-hour budget plus
    outperformance of AlphaEvolve on mathematical algorithm optimization
    tasks. The arXiv page links code at `https://github.com/InternScience/MLEvolve`.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2606.06473`. Existing rows cover AlphaEvolve, MAP-Elites,
    UCB/reviewer logic, prompt/history artifacts, DeltaEvolve context memory,
    EvoX adaptive search, and selected application papers, but not MLE-Bench,
    Progressive MCGS, cross-branch graph references, retrospective MLE memory,
    adaptive coding modes, or long-horizon ML-engineering evaluation budgets.
  - Required result: add paper-manifest and paper-index coverage for
    `2606.06473`: title/authors/arXiv version/date/PDF digest, source license,
    linked-code URL/status, relation to AlphaEvolve and LibreEvolve,
    Progressive MCGS and graph-reference schema, entropy-schedule metadata,
    retrospective-memory taxonomy, adaptive coding-mode artifacts, MLE-Bench
    task/submission records, 12-hour budget and metric definitions,
    mathematical-algorithm baseline identities, code/artifact reproducibility
    status, and README/ROADMAP wording that treats MLEvolve as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Track LEVI cost-aware search-architecture paper evidence.
  - Paper/source evidence: arXiv `2605.09764`, submitted May 10, 2026, is
    titled `LEVI: Stronger Search Architectures Can Substitute for Larger LLMs
    in Evolutionary Search`. Its abstract says AlphaEvolve-style LLM-guided
    evolutionary methods work across math, systems research, and algorithmic
    discovery but are expensive because search allocation often fails to
    preserve solution diversity, uses frontier models blindly for local edits,
    and evaluates redundant examples. LEVI proposes a harness-first framework
    with a diversity-preserving solution database, smarter mutation routing
    between large and small LLMs, and rank-preserving proxy benchmarks; it
    reports systems-research wins at 3.3x-6.7x lower budget, one 35x
    lower-cost match, and prompt-optimization results at less than half GEPA's
    rollout budget. The arXiv page links code at `https://github.com/ttanv/levi`.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.09764`. Existing rows cover AlphaEvolve, MAP-Elites,
    UCB-style ensemble selection, evaluator artifacts, EvoX adaptive search,
    DeltaEvolve context memory, and MLEvolve long-horizon MLE, but not
    LEVI-style diversity preservation, cost-aware mutation routing,
    proxy-benchmark rank preservation, provider-budget accounting, or
    systems/prompt optimization cost comparisons.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.09764`: title/authors/arXiv version/date/PDF digest, source license,
    linked-code URL/status, relation to AlphaEvolve and LibreEvolve archive/
    ensemble behavior, diversity metrics, solution-database invariants,
    mutation-router policy, large/small model assignment traces,
    proxy-benchmark construction and rank-correlation evidence, rollout and
    provider-cost accounting, systems/prompt benchmark taxonomy, baseline
    method identities, code/artifact reproducibility status, and README/
    ROADMAP wording that treats LEVI as missing paper evidence rather than
    implemented LibreEvolve support.

- [ ] Track PACEvolve long-horizon consistency paper evidence.
  - Paper/source evidence: arXiv `2601.10657`, submitted January 15, 2026 and
    last revised January 16, 2026, is titled `PACEvolve: Enabling Long-Horizon
    Progress-Aware Consistent Evolution`. Its abstract says LLM-in-the-loop
    evolutionary systems lack systematic process management and identifies
    context pollution, mode collapse, and weak collaboration as failure
    modes. PACEvolve combines hierarchical context management with pruning,
    momentum-based backtracking, and a self-adaptive sampling policy that
    unifies backtracking and crossover, reporting state-of-the-art LLM-SR and
    KernelBench results plus record-surpassing Modded NanoGPT solutions.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2601.10657`. Existing rows cover AlphaEvolve, MAP-Elites,
    prompt/history artifacts, DeltaEvolve semantic context, EvoX adaptive
    search, MLEvolve long-horizon MLE, and LEVI cost-aware routing, but not
    PACEvolve's context-pollution controls, hierarchical pruning,
    momentum-backtracking state, crossover/backtracking coordination, or
    LLM-SR/KernelBench/Modded-NanoGPT evidence.
  - Required result: add paper-manifest and paper-index coverage for
    `2601.10657`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve prompt/search policy,
    context-pollution and mode-collapse metrics, hierarchical context schema,
    pruning and momentum-backtracking artifacts, adaptive sampling and
    crossover/backtracking coordination records, trajectory-collaboration
    diagnostics, LLM-SR/KernelBench/Modded-NanoGPT benchmark metadata,
    baseline method identities, code/artifact availability if any, and README/
    ROADMAP wording that treats PACEvolve as missing paper evidence rather
    than implemented LibreEvolve support.

- [ ] Track FlashEvolve asynchronous-stage paper evidence.
  - Paper/source evidence: arXiv `2605.08520`, submitted May 8, 2026, is
    titled `FlashEvolve: Accelerating Agent Self-Evolution with Asynchronous
    Stage Orchestration`. Its abstract says synchronized stage execution and
    imbalance inside LLM-heavy stages create wall-clock bottlenecks in
    LLM-based evolution. FlashEvolve replaces synchronized execution with
    asynchronous workers and queues so different stages and evolution steps
    overlap; tracks artifact versions; updates, discards, or patches stale
    artifacts; treats language-space staleness as inspectable and repairable;
    adds speculative stage completion and adaptive workflow control; and
    reports 3.5x local-vLLM and 4.9x API proposal-throughput gains over
    synchronous GEPA, with the design also applying to ACE and Meta-Harness.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.08520`. Existing rows cover AlphaEvolve, prompt/history
    artifacts, reviewer metadata, async reviewer gaps, archive restore,
    PACEvolve consistency, LEVI cost-aware routing, and MLEvolve long-horizon
    MLE, but not asynchronous stage orchestration, queue overlap, artifact
    versioning, stale-language-artifact repair, speculative completion, or
    throughput/token-efficiency measurements.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.08520`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve's synchronous loop, worker/queue
    schema, stage-overlap traces, artifact-version lineage, stale-artifact
    update/discard/patch policies, reflective patch artifacts,
    speculative-completion metrics, adaptive workflow telemetry,
    throughput/token-efficiency records, GEPA/vLLM/API baseline identities,
    ACE/Meta-Harness applicability status, code/artifact availability if any,
    and README/ROADMAP wording that treats FlashEvolve as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Track evolutionary-agent trace-diagnostics paper evidence.
  - Paper/source evidence: arXiv `2605.20086`, submitted May 25, 2026, is
    titled `What Do Evolutionary Coding Agents Evolve?`. Its abstract says
    aggregate benchmark scores hide how evolutionary coding agents improve
    programs, whether improvements reflect structural innovation or
    overfitting, and how search behavior changes across tasks. It introduces
    EvoTrace for annotation of edit types, dependencies, and fitness
    trajectories, and EvoReplay for interventions on search traces, reporting
    recurring cycling and overfitting, task-dependent constant tuning versus
    new logic, and sensitivity to population structure and prompt content
    across AlphaEvolve-style agents such as AlphaEvolve, OpenEvolve, and
    FunSearch.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.20086`. Existing rows cover AlphaEvolve, benchmark/report
    contracts, prompt/history artifacts, archive events, async orchestration,
    context memory, adaptive search, and cost-aware routing, but not
    mechanistic trace annotation, replay interventions, cycling/overfitting
    diagnostics, structural-innovation labels, or prompt/population
    sensitivity evidence.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.20086`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve run artifacts, EvoTrace edit-type
    taxonomy, dependency extraction, fitness-trajectory labels,
    EvoReplay-intervention schema, cycling and overfitting diagnostics,
    constant-tuning versus new-logic classification, prompt/population
    sensitivity metadata, benchmark/task taxonomy, baseline-agent identities,
    code/artifact availability if any, and README/ROADMAP wording that treats
    mechanistic trace diagnostics as missing paper evidence rather than
    implemented LibreEvolve support.

- [ ] Track Zarankiewicz reinforced-search paper evidence.
  - Paper/source evidence: arXiv `2605.01120`, submitted May 1, 2026 and last
    revised May 7, 2026, is titled `New Bounds for Zarankiewicz Numbers via
    Reinforced LLM Evolutionary Search`. Its abstract says OpenEvolve, an
    open-source evolutionary algorithm based on LLMs, produced the first exact
    values for `Z(11,21,3,3)=116`, `Z(11,22,3,3)=121`, and
    `Z(12,22,3,3)=132`; lower bounds for 41 more Zarankiewicz numbers; and
    four matched closed cases. The paper also reports generated construction
    algorithms, implementation details, and computational costs under `$30`
    per Zarankiewicz parameter combination.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.01120`. Existing rows cover AlphaEvolve, mathematical
    follow-on problem sources, combinatorics examples, cost-aware routing, and
    trace diagnostics, but not Zarankiewicz parameter manifests,
    bipartite-graph construction artifacts, `K_{s,t}`-free validation,
    exact/lower-bound tables, generated construction algorithms, cost records,
    or OpenEvolve-to-LibreEvolve application boundaries.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.01120`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve/OpenEvolve and LibreEvolve, Zarankiewicz parameter
    schema, graph representation, `K_{s,t}`-free verifier metadata,
    exact-value and lower-bound records, generated construction algorithm
    artifacts, proof/check status, computational-cost records, upper-bound and
    baseline references, code/artifact availability if any, reproducibility
    status, and README/ROADMAP wording that treats the paper as missing
    application evidence rather than implemented LibreEvolve support.

- [ ] Track CORAL autonomous multi-agent evolution paper evidence.
  - Paper/source evidence: arXiv `2604.01658`, submitted April 2, 2026 and
    last revised May 17, 2026, is titled `CORAL: Towards Autonomous
    Multi-Agent Evolution for Open-Ended Discovery`. Its abstract says
    LLM-based evolution for open-ended discovery needs sustained search and
    knowledge accumulation, but existing methods rely on fixed heuristics and
    hard-coded exploration rules. CORAL replaces rigid control with
    long-running agents that explore, reflect, and collaborate through shared
    persistent memory, asynchronous multi-agent execution, and heartbeat-based
    interventions, plus safeguards for isolated workspaces, evaluator
    separation, resource management, and agent session and health management.
    It reports state-of-the-art results on 10 mathematical, algorithmic, and
    systems optimization tasks, 3-10x higher improvement rates with fewer
    evaluations, and a kernel-engineering score improvement from 1363 to 1103
    cycles. The arXiv page links code at `https://github.com/YangLabHKUST/CORAL`.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2604.01658`. Existing rows cover AlphaEvolve, MAP-Elites,
    islands, migration, async orchestration, trace diagnostics, cost-aware
    routing, and application papers, but not CORAL-style long-running agent
    sessions, shared persistent memory, asynchronous agent collaboration,
    heartbeat interventions, isolated workspaces, evaluator separation,
    resource and health management, or multi-agent benchmark/mechanism
    evidence.
  - Required result: add paper-manifest and paper-index coverage for
    `2604.01658`: title/authors/arXiv version/date/PDF digest, source license,
    linked-code URL/status, relation to AlphaEvolve and LibreEvolve islands,
    agent-session schema, shared-memory/index metadata, asynchronous
    execution and communication traces, heartbeat intervention records,
    workspace-isolation and evaluator-separation policies, resource and
    health telemetry, knowledge-reuse/mechanistic analysis artifacts,
    mathematical/algorithmic/systems benchmark taxonomy, kernel-engineering
    metric records, baseline identities, code/artifact reproducibility status,
    and README/ROADMAP wording that treats CORAL as missing paper evidence
    rather than implemented LibreEvolve support.

- [ ] Track AEvo harnessed meta-editing paper evidence.
  - Paper/source evidence: arXiv `2605.13821`, submitted May 13, 2026, is
    titled `Harnessing Agentic Evolution`. Its abstract says agentic evolution
    improves programs, workflows, and scientific solutions by iteratively
    generating candidates, evaluating them, and using feedback to guide future
    search, but existing systems are either fixed modular procedures that are
    rigid or general-purpose agents that can drift in long-horizon evolution.
    AEvo treats accumulated candidates, feedback, traces, and failures as
    process-level state and uses a meta-agent to edit the procedure or agent
    context controlling future evolution, reporting a 26 relative improvement
    over the strongest of five baselines and state-of-the-art results on three
    open-ended optimization tasks under the same iteration budget.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.13821`. Existing rows cover AlphaEvolve, static prompt/run
    artifacts, failures, trace diagnostics, adaptive search, async
    orchestration, and CORAL multi-agent autonomy, but not AEvo-style
    process-level state, meta-agent procedure/context edits, controller
    self-modification, control-edit rollback/versioning, drift diagnostics, or
    benchmark boundaries separating candidate generation from mechanism edits.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.13821`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve, process-state schema,
    accumulated-evidence inventory, meta-agent observation/action schema,
    procedure/context patch artifacts, control-edit provenance,
    rollback/versioning metadata, drift/stability diagnostics,
    iteration-budget accounting, agentic/reasoning/open-ended benchmark
    taxonomy, baseline identities, code/artifact availability if any,
    reproducibility status, and README/ROADMAP wording that treats AEvo as
    missing paper evidence rather than implemented LibreEvolve support.

- [ ] Track G-Zero verifier-free co-evolution paper evidence.
  - Paper/source evidence: arXiv `2605.09959`, submitted May 11, 2026, is
    titled `G-Zero: Self-Play for Open-Ended Generation from Zero Data`. Its
    abstract says self-evolving LLMs struggle on open-ended tasks because
    proxy LLM judges introduce capability bottlenecks and reward hacking.
    G-Zero introduces a verifier-free co-evolutionary framework with
    `Hint-delta`, an intrinsic reward measuring predictive shift between a
    Generator model's unassisted response and its response conditioned on a
    self-generated hint. A Proposer is trained with GRPO to target Generator
    blind spots by generating queries and hints, while the Generator is
    trained with DPO to internalize improvements. The paper also states a
    best-iterate suboptimality guarantee under sufficient exploration coverage
    and low pseudo-label score noise.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.09959`. Existing rows cover AlphaEvolve's explicit
    evaluator loop, verifier-backed tasks, cost-aware routing, AEvo
    meta-editing, CORAL multi-agent autonomy, and trace diagnostics, but not
    verifier-free co-evolution, Hint-delta intrinsic rewards, self-generated
    query/hint data, GRPO/DPO self-training, exploration coverage guarantees,
    or pseudo-label noise filtering for open-ended domains.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.09959`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve evaluator assumptions, Generator/
    Proposer role schema, Hint-delta reward definition, unassisted vs
    hint-conditioned response artifacts, self-generated query/hint records,
    GRPO/DPO training metadata, intrinsic-reward calibration, exploration
    coverage evidence, pseudo-label score-noise filters, reward-hacking
    diagnostics, open-ended task taxonomy, theoretical guarantee assumptions,
    baseline identities, code/artifact availability if any, reproducibility
    status, and README/ROADMAP wording that treats G-Zero as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Track GenEvolve multimodal trajectory-distillation paper evidence.
  - Paper/source evidence: arXiv `2605.21605`, submitted May 20, 2026 and
    last revised May 22, 2026, is titled `GenEvolve: Self-Evolving Image
    Generation Agents via Tool-Orchestrated Visual Experience Distillation`.
    Its abstract says open-ended image generation is no longer a simple
    prompt-to-image problem and often requires agents to combine internal
    generative ability with external resources. GenEvolve models each
    generation attempt as a tool-orchestrated trajectory in which the agent
    gathers evidence, selects references, invokes generation skills, and
    composes them into a prompt-reference program. It compares multiple
    trajectories for the same request, abstracts best-worst differences into
    structured visual experience for a privileged teacher branch, and uses
    Visual Experience Distillation to provide dense token-level supervision
    so the student internalizes better search, knowledge activation, reference
    selection, and prompt construction.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.21605`. Existing rows cover AlphaEvolve, text-program
    evolution, evaluator-backed tasks, verifier-free self-play, autonomous
    multi-agent search, and application papers, but not multimodal
    image-generation agents, visual tool trajectories, prompt-reference
    programs, structured visual experience, privileged teacher branches, dense
    token-level distillation, image artifact lineage, or GenEvolve-Bench.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.21605`: title/authors/arXiv version/date/PDF digest, source license,
    project/demo URL status, relation to AlphaEvolve and LibreEvolve,
    tool-orchestrated visual trajectory schema, evidence/reference selection
    metadata, prompt-reference program representation, best-worst comparison
    records, structured visual experience taxonomy, privileged teacher/student
    distillation traces, token-level supervision artifacts, image artifact
    provenance, GenEvolve-Data/GenEvolve-Bench metadata, baseline identities,
    code/artifact availability if any, reproducibility status, and README/
    ROADMAP wording that treats GenEvolve as missing paper evidence rather
    than implemented LibreEvolve support.

- [ ] Track EvoRubric self-evolving reward-rubric paper evidence.
  - Paper/source evidence: arXiv `2605.29847`, submitted May 28, 2026, is
    titled `EvoRubric: Self-Evolving Rubric-Driven RL for Open-Ended
    Generation`. Its abstract says RL has advanced LLMs in verifiable domains,
    but open-ended generation lacks definitive rewards. Existing rubric-based
    RL uses static human annotations, which can cause policy lag, or expensive
    external proprietary rubric generators. EvoRubric unifies response and
    rubric generation under a single policy that alternates between Reasoner
    and Rubric Generator roles; validates generated criteria through a
    meta-verifier, zero-variance pruning, and Leave-One-Out peer consensus;
    stores validated criteria in memory; and yields dense multi-objective
    rewards across medical, writing, and science domains.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.29847`. Existing rows cover AlphaEvolve's evaluator-driven
    scoring, verifier-free self-play, trace diagnostics, multimodal
    trajectory distillation, and open-ended source gates, but not
    self-evolving rubric generation, criteria verification, peer consensus,
    criteria memory pools, dense rubric reward vectors, expert-prior rubric
    expansion, or reward-hacking diagnostics for open-ended generation.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.29847`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve evaluator assumptions,
    Reasoner/Rubric-Generator role schema, generated-rubric provenance,
    meta-verifier artifacts, zero-variance pruning records, Leave-One-Out peer
    consensus traces, criteria memory-pool metadata, dense reward-vector
    definitions, reward-hacking diagnostics, expert-prior initialization
    status, medical/writing/science benchmark taxonomy, baseline identities,
    code/artifact availability if any, reproducibility status, and README/
    ROADMAP wording that treats EvoRubric as missing paper evidence rather
    than implemented LibreEvolve support.

- [ ] Track LLM-ALSO adaptive learning-signal paper evidence.
  - Paper/source evidence: arXiv `2605.29293`, submitted May 28, 2026, is
    titled `LLM-ALSO: LLM-Driven Adaptive Learning-Signal Optimization for
    Multi-Agent Reinforcement Learning`. Its abstract says effective
    training-time guidance is difficult in sparse-reward MARL, while existing
    LLM-based learning-signal design is largely single-agent-oriented,
    one-shot, or weakly validated for evolving cooperative training dynamics.
    LLM-ALSO decomposes adaptation into iterative diagnosis, proposal, and
    validation: a Critic LLM diagnoses stage-specific learning and
    coordination failures from sparse-return metrics and compact behavior
    evidence, a Generator LLM proposes reward-shaping configurations
    conditioned on the diagnosis, and branch-validation feedback refines
    candidates before updates affect the main training trajectory.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.29293`. Existing rows cover AlphaEvolve evaluator scoring,
    plugin hooks, verifier-free self-play, self-evolving rubrics, and
    multi-agent autonomy, but not sparse-reward cooperative MARL, adaptive
    learning-signal diagnosis, reward-shaping configuration generation,
    branch validation, or promotion of validated reward updates into a main
    training trajectory.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.29293`: title/authors/arXiv version/date/PDF digest, source license,
    relation to AlphaEvolve and LibreEvolve reward/evaluator assumptions,
    Critic/Generator role schema, sparse-return and compact-behavior evidence
    metadata, stage-specific diagnosis artifacts, reward-shaping configuration
    schema, branch-validation records, promotion criteria, main-training
    trajectory provenance, sparse-reward cooperative MARL task taxonomy,
    learning-efficiency metrics, baseline identities, code/artifact
    availability if any, reproducibility status, and README/ROADMAP wording
    that treats LLM-ALSO as missing paper evidence rather than implemented
    LibreEvolve support.

- [ ] Track MemEvolve meta-evolving memory-architecture paper evidence.
  - Paper/source evidence: arXiv `2512.18746`, submitted December 21, 2025, is
    titled `MemEvolve: Meta-Evolution of Agent Memory Systems`. Its abstract
    says self-evolving memory systems are reshaping LLM-agent evolution, but
    prior work relies on manually engineered memory architectures to store
    trajectories, distill experience, and synthesize reusable tools. MemEvolve
    jointly evolves experiential knowledge and memory architecture, allowing
    agents to refine how they learn from experience. It introduces EvolveLab,
    a unified self-evolving memory codebase that distills twelve memory
    systems into a modular encode/store/retrieve/manage design space, and
    reports up to 17.06% improvements for frameworks such as SmolAgent and
    Flash-Searcher plus cross-task and cross-LLM generalization.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2512.18746`. Existing rows cover AlphaEvolve run artifacts,
    prompt history, failed-proposal snippets, DeltaEvolve semantic context,
    CORAL shared memory, and several open-ended source gates, but not
    meta-evolution of the memory architecture itself, EvolveLab's modular
    memory substrate, encode/store/retrieve/manage component mutations, or
    transfer evidence across tasks and backbone models.
  - Required result: add paper-manifest and paper-index coverage for
    `2512.18746`: title/authors/arXiv version/date/PDF digest, source license,
    linked-code URL/status, relation to AlphaEvolve and LibreEvolve run
    memory, memory-component taxonomy, encode/store/retrieve/manage schema,
    memory-architecture mutation records, experiential-knowledge artifacts,
    joint content/architecture evolution traces, static-memory baseline
    identities, EvolveLab benchmark metadata, cross-task and cross-LLM
    transfer metrics, performance-delta records, code/artifact availability
    if any, reproducibility status, and README/ROADMAP wording that treats
    MemEvolve as missing paper evidence rather than implemented LibreEvolve
    support.

- [ ] Track ANCHOR healthy-evolution oversight paper evidence.
  - Paper/source evidence: arXiv `2606.06114`, submitted June 4, 2026, is
    titled `Towards Healthy Evolution: Exploring the Role and Mechanisms of
    Human-Agent Interaction in Self-Evolving Systems`. Its abstract says
    autonomous self-evolution can cause capability degradation and safety
    drift, and introduces Agent Norm Correction through Human-like Oversight
    and Review (ANCHOR), an LLM-based framework that simulates human
    supervision across phases of self-evolution. It evaluates two
    representative open-source self-evolving agent systems across coding,
    mathematical reasoning, and safety, reports that limited supervision
    mitigates safety degradation while preserving core performance, identifies
    output-verification supervision as the strongest intervention point, and
    finds diminishing returns from increasing supervision frequency.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2606.06114`. Existing rows cover AlphaEvolve evaluator-backed
    search, open-ended reward/rubric sources, multi-agent autonomy, trace
    diagnostics, and memory architecture evolution, but not human-like
    oversight, phase-specific norm correction, safety-drift tracking,
    output-verification interventions, supervision-frequency tradeoffs, or
    healthy-evolution reporting for self-evolving agents.
  - Required result: add paper-manifest and paper-index coverage for
    `2606.06114`: title/authors/arXiv version/date/PDF digest, source
    license, relation to AlphaEvolve and LibreEvolve safety assumptions,
    ANCHOR role and feedback schema, supervised phase taxonomy, norm-
    correction artifact records, output-verification intervention evidence,
    safety degradation metrics, coding/math/safety benchmark taxonomy,
    supervision-frequency experiment records, objective-preservation
    measurements, baseline identities, code/artifact availability if any,
    reproducibility status, and README/ROADMAP wording that treats ANCHOR as
    missing paper evidence rather than implemented LibreEvolve support.

- [ ] Track SIA harness-plus-weight self-improvement paper evidence.
  - Paper/source evidence: arXiv `2605.27276`, submitted May 26, 2026, is
    titled `SIA: Self Improving AI with Harness & Weight Updates`. Its
    abstract says AI improvement remains bottlenecked by humans who write,
    tune, and correct both models and agent wrappers. It contrasts a
    harness-update line, where a meta-agent rewrites tools, prompts, retry
    logic, and search procedures while weights remain fixed, with a test-time
    training line, where model weights are updated from task feedback while
    the harness remains fixed. SIA proposes a Feedback-Agent loop that
    updates both the harness and weights of a task-specific agent, evaluated
    on Chinese legal charge classification, low-level GPU kernel
    optimization, and single-cell RNA denoising. The abstract reports 56.6%
    LawBench gain, 91.9% GPU-kernel runtime reduction, and 502% denoising
    improvement over the initial baseline.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.27276`. Existing rows cover AlphaEvolve evaluator-backed
    program search, ThetaEvolve-style clipped training-data export,
    harnessed meta-editing, adaptive learning signals, and open-ended reward
    gates, but not a unified loop where a Feedback-Agent chooses between
    editable harness updates and actual model-weight updates, nor the
    corresponding checkpoint, adapter, training-data, ablation, and benchmark
    evidence.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.27276`: title/authors/arXiv version/date/PDF digest, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    training assumptions, Meta-Agent/Target-Agent/Feedback-Agent role schema,
    editable-harness taxonomy, harness patch records, weight-update records,
    training-data provenance, RL/fine-tuning configuration, adapter/
    checkpoint artifacts, verifier/reward definitions, harness-only,
    weight-only, and combined-loop ablation records, LawBench/kernel/scRNA
    benchmark metadata, compute/cost accounting, performance-delta records,
    code/artifact availability if any, reproducibility status, and README/
    ROADMAP wording that treats SIA as missing paper evidence rather than
    implemented LibreEvolve support.

- [ ] Track HarnessFix trace-grounded harness repair paper evidence.
  - Paper/source evidence: arXiv `2606.06324`, submitted June 4, 2026, is
    titled `From Failed Trajectories to Reliable LLM Agents: Diagnosing and
    Repairing Harness Flaws`. Its abstract says agent harnesses provide
    execution environments, tool interfaces, context, lifecycle
    orchestration, observability, verification, and governance, but existing
    self-improvement and automatic harness-evolution methods often make broad
    changes from final outcomes instead of diagnosing the responsible
    evidence in failed trajectories. HarnessFix compiles raw traces and
    harness code into a Harness-aware Trace Intermediate Representation
    (HTIR), attributes failures to responsible trajectory steps and harness
    layers, consolidates recurring flaw records, maps them to scoped repair
    operators, and validates harness patches under flaw-specific repair specs.
    It reports 15.2% to 50.0% held-out improvements on SWE-Bench Verified,
    Terminal-Bench 2.0 Verified, GAIA, and AppWorld.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2606.06324`. Existing rows cover AlphaEvolve evaluator-backed
    program search, failed-proposal snippets, trace diagnostics, SIA harness
    and weight updates, and AEvo process meta-editing, but not
    trace-normalized harness diagnosis, HTIR, harness-layer attribution,
    recurring flaw records, scoped repair operators, regression-bounded patch
    validation, or held-out harness reliability reports.
  - Required result: add paper-manifest and paper-index coverage for
    `2606.06324`: title/authors/arXiv version/date/PDF digest, source
    license, relation to AlphaEvolve and LibreEvolve harness/failure
    assumptions, HTIR schema, trace-to-harness-code linkage, step-level
    provenance, harness-layer taxonomy, failure-attribution records,
    recurring flaw consolidation, repair-operator definitions, harness patch
    artifacts, flaw-specific validation specifications, unacceptable-
    regression thresholds, held-out benchmark results, SWE-Bench/Terminal-
    Bench/GAIA/AppWorld metadata, baseline identities, code/artifact
    availability if any, reproducibility status, and README/ROADMAP wording
    that treats HarnessFix as missing paper evidence rather than implemented
    LibreEvolve support.

- [ ] Track RHO retrospective self-preference harness optimization evidence.
  - Paper/source evidence: arXiv `2606.05922`, submitted June 4, 2026, is
    titled `Retrospective Harness Optimization: Improving LLM Agents via
    Self-Preference over Trajectory Rollouts`. Its abstract says continually
    improving an agent harness is essential for adapting to new tasks, but
    ground-truth validation labels are often unavailable in practical
    deployments. RHO optimizes a harness using only past trajectories by
    selecting a diverse coreset of challenging tasks, re-solving them in
    parallel, analyzing rollouts with self-validation and self-consistency,
    generating candidate harness updates, and selecting the best update via
    pairwise self-preference. It reports a single optimization round improving
    SWE-Bench Pro pass rate from 59% to 78% without external grading, and says
    the optimized harness sustains higher accuracy in long-horizon sessions.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2606.05922`. Existing rows cover AlphaEvolve evaluator-backed
    search, failure traces, HarnessFix trace-grounded repair, SIA harness and
    weight updates, and AEvo process meta-editing, but not label-free
    retrospective coreset selection, parallel re-rollouts from past
    trajectories, self-validation/self-consistency analysis, pairwise
    self-preference ranking, or harness deployment evidence without external
    labels.
  - Required result: add paper-manifest and paper-index coverage for
    `2606.05922`: title/authors/arXiv version/date/PDF digest, source
    license, relation to AlphaEvolve and LibreEvolve evaluator assumptions,
    past-trajectory corpus metadata, hard-task/diversity coreset selection,
    retrospective rollout batch records, parallel re-solve provenance,
    self-validation and self-consistency artifacts, candidate harness-update
    records, pairwise self-preference comparisons, label-free selection
    policy, deployment and rollback metadata, behavior-pattern shift reports,
    long-horizon accuracy records, SWE-Bench Pro benchmark metadata, baseline
    identities, code/artifact availability if any, reproducibility status, and
    README/ROADMAP wording that treats RHO as missing paper evidence rather
    than implemented LibreEvolve support.

- [ ] Track harness-updating versus harness-benefit paper evidence.
  - Paper/source evidence: arXiv `2605.30621`, submitted May 28, 2026, is
    titled `Harness Updating Is Not Harness Benefit: Disentangling Evolution
    Capabilities in Self-Evolving LLM Agents`. Its abstract says LLM agents
    are increasingly built around editable external harnesses such as prompts,
    skills, memories, and tools. It analyzes two separable capabilities:
    harness-updating, the ability to produce useful persistent harness updates
    from execution evidence, and harness-benefit, the ability to benefit from
    updated harnesses during task solving. The abstract reports that
    harness-updating is flat across model capability tiers, while
    harness-benefit is non-monotonic: weak-tier models benefit little,
    mid-tier models benefit most, and strong-tier models benefit less than
    mid-tier. It traces weak-tier failures to failing to activate relevant
    harness artifacts or failing to follow them faithfully.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.30621`. Existing rows cover AlphaEvolve search, SIA
    harness-plus-weight updates, HarnessFix diagnosis/repair, RHO
    retrospective optimization, and AEvo meta-editing, but not the empirical
    separation between harness update generation and actual downstream
    harness benefit, model-tier benefit curves, activation failures,
    adherence failures, or capability-budget guidance for evolver versus
    task-solving agent selection.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.30621`: title/authors/arXiv version/date/PDF digest, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    harness assumptions, harness-updating and harness-benefit metric
    definitions, evolver/task-agent pairing records, persistent harness
    update artifacts, activation telemetry, adherence and instruction-
    following traces, model-tier taxonomy, weak/mid/strong baseline identities,
    capability-budget analysis, post-evolution performance deltas, SWE-Bench
    Verified/MCP-Atlas/SkillsBench metadata if used, code/artifact
    availability if any, reproducibility status, and README/ROADMAP wording
    that treats harness-update benefit as missing paper evidence rather than
    implemented LibreEvolve support.

- [ ] Track AHE observability-driven harness evolution paper evidence.
  - Paper/source evidence: arXiv `2604.25850`, submitted April 28, 2026, is
    titled `Agentic Harness Engineering: Observability-Driven Automatic
    Evolution of Coding-Agent Harnesses`. Its abstract says harnesses mediate
    how models interact with tools and execution environments, but automating
    harness engineering is hard because of heterogeneous editable components,
    very large trajectories, sparse/noisy signals, and edits whose effects are
    hard to attribute. AHE adds component observability through explicit
    file-level editable components, experience observability through layered
    drill-down trajectory evidence, and decision observability by pairing each
    edit with a self-declared prediction that is later checked against
    task-level outcomes. It reports ten iterations improving Terminal-Bench 2
    pass@1 from 69.7% to 77.0%, surpassing Codex-CLI and self-evolving
    baselines, plus frozen-harness transfer to SWE-bench Verified and cross-
    family Terminal-Bench gains.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2604.25850`. Existing rows cover AlphaEvolve search, SIA,
    HarnessFix, RHO, harness-benefit disentanglement, and AEvo meta-editing,
    but not component/experience/decision observability as a harness evolution
    contract, file-level harness component action spaces, layered trajectory
    evidence corpora, edit-prediction verification, frozen-harness transfer,
    or attribution of gains to tools, middleware, and long-term memory rather
    than system prompts.
  - Required result: add paper-manifest and paper-index coverage for
    `2604.25850`: title/authors/arXiv version/date/PDF digest, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    harness assumptions, editable component taxonomy, file-level component
    manifests, component edit/revert records, trajectory-evidence corpus
    schema, drill-down evidence links, edit-prediction records, task-outcome
    verification records, falsifiable edit-contract status, iteration traces,
    component-attribution reports, frozen-harness transfer results,
    Terminal-Bench 2 and SWE-bench Verified metadata, baseline identities,
    token/cost accounting, code/artifact availability if any, reproducibility
    status, and README/ROADMAP wording that treats AHE as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Track AI Harness Engineering runtime-substrate paper evidence.
  - Paper/source evidence: arXiv `2605.13357`, submitted May 13, 2026, is
    titled `AI Harness Engineering: A Runtime Substrate for Foundation-Model
    Software Agents`. Its abstract says autonomous software-engineering
    reliability should be explained through a model-harness-environment
    system, where the harness mediates how a foundation-model agent observes a
    project, acts on it, receives feedback, and establishes that a change is
    complete. The paper identifies eleven component responsibilities: task
    specification, context selection, tool access, project memory, task state,
    observability, failure attribution, verification, permissions, entropy
    auditing, and intervention recording. It operationalizes the harness
    through an H0-H3 ladder and converts each run into an auditable episode
    package; higher levels produce reproduction logs, failure attributions,
    deterministic requirement checks, and structured verification reports.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.13357`. Existing rows cover AlphaEvolve search, AHE
    observability-driven evolution, HarnessFix, RHO, SIA, and AEvo, but not a
    general AI-harness runtime-substrate contract, eleven responsibility
    records, H0-H3 support-level comparisons, episode-package trace bundles,
    entropy auditing, intervention logging, or requirement-level verification
    as a harness maturity artifact.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.13357`: title/authors/arXiv version/date/PDF digest, source
    license, relation to AlphaEvolve and LibreEvolve harness assumptions,
    model-harness-environment schema, eleven responsibility taxonomy,
    H0-H3 harness-level records, runtime-resource exposure matrix, task/
    context/tool/memory/state artifact records, observability traces,
    failure-attribution logs, verification protocol and report records,
    permission events, entropy audits, intervention logs, episode package
    schema, deterministic requirement-check metadata, controlled validation
    task evidence, maintenance-burden analysis, code/artifact availability if
    any, reproducibility status, and README/ROADMAP wording that treats AI
    Harness Engineering as missing paper evidence rather than implemented
    LibreEvolve support.

- [ ] Track inference-time trajectory-alignment harness paper evidence.
  - Paper/source evidence: arXiv `2605.21516`, submitted May 15, 2026, is
    titled `Harnesses for Inference-Time Alignment over Execution
    Trajectories`. Its abstract says harness engineering improves agent
    performance through task decomposition and guided execution, but more
    elaborate harnesses can reduce final task success. It separates harness
    mechanisms into decomposition and guided execution, then quantifies how
    workflow granularity, retry budgets, and guidance-induced action
    reweighting affect performance limits. It identifies over-decomposition,
    over-pruning, and hallucinated execution as failure modes, validates the
    predictions with controlled synthetic experiments and real terminal-agent
    benchmarks, and shows that partial harnesses can outperform fully
    structured workflows.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2605.21516`. Existing rows cover AlphaEvolve search, AHE, AI
    Harness Engineering, HarnessFix, RHO, SIA, and harness-benefit
    disentanglement, but not theoretical or empirical evidence for when
    decomposition/guidance helps or harms, retry-budget sensitivity,
    guidance-evidence alignment, partial harnessing, final-bias metrics, or
    over-structured workflow failure modes.
  - Required result: add paper-manifest and paper-index coverage for
    `2605.21516`: title/authors/arXiv version/date/PDF digest, source
    license, relation to AlphaEvolve and LibreEvolve harness assumptions,
    harness parameter schema, decomposition-granularity records, guidance-
    strength and guidance-rule records, sub-goal and trajectory records,
    retry-budget experiment metadata, pass-rate/final-bias metrics,
    granularity-capability alignment evidence, guidance-evidence alignment
    evidence, over-decomposition/over-pruning/hallucinated-execution
    diagnostics, partial-harness prefix experiment records, Terminal-Bench-2
    and controlled synthetic benchmark metadata, baseline identities,
    code/artifact availability if any, reproducibility status, and README/
    ROADMAP wording that treats inference-time trajectory alignment as
    missing paper evidence rather than implemented LibreEvolve support.

- [ ] Track Adaptive Auto-Harness open-ended task-stream paper evidence.
  - Paper/source evidence: arXiv `2606.01770`, submitted June 1, 2026, is
    titled `Adaptive Auto-Harness: Sustained Self-Improvement for Agentic
    System Deployment on Open-Ended Task Streams`. Its abstract says
    auto-harness systems such as A-Evolve, GEPA, and Meta-Harness improve
    agents by optimizing prompts, skills, tools, memories, and infrastructure
    from execution feedback, but are usually tested on fixed offline
    benchmarks. Open-ended deployments have growing histories, heterogeneous
    tasks, and shifting distributions; a single densely updated harness can
    become brittle as accuracy peaks and declines. Adaptive Auto-Harness
    decomposes the gap to an oracle harness into evolution loss and adaptation
    loss, and addresses those losses with a stateful multi-agent evolver, a
    harness tree with solve-time routing, and human-steering hooks. It reports
    gains across prediction-market, security-competition, and event-
    forecasting streams over five auto-harness baselines.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2606.01770`. Existing rows cover AlphaEvolve search, AHE, AI
    Harness Engineering, inference-time harness alignment, HarnessFix, RHO,
    SIA, and harness-benefit disentanglement, but not sustained deployment on
    open-ended task streams, history-growth management, task-wise harness
    adaptation, harness trees, solve-time routing, evolution/adaptation loss
    decomposition, or targeted human steering when history lacks signal.
  - Required result: add paper-manifest and paper-index coverage for
    `2606.01770`: title/authors/arXiv version/date/PDF digest, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    deployment assumptions, open-ended task-stream schema, history-growth
    records, task-heterogeneity metadata, distribution-shift metrics, oracle-
    harness definition, evolution-loss and adaptation-loss records, stateful
    multi-agent evolver roles, cross-cycle memory, harness tree artifacts,
    solve-time routing records, human-steering hook provenance, targeted
    steering outcomes, sustained-performance/degradation curves, prediction-
    market/security-competition/event-forecasting benchmark metadata,
    baseline identities, ablation records, code/artifact availability if any,
    reproducibility status, and README/ROADMAP wording that treats Adaptive
    Auto-Harness as missing paper evidence rather than implemented LibreEvolve
    support.

- [ ] Track Meta-Harness outer-loop harness-code search paper evidence.
  - Paper/source evidence: arXiv `2603.28052`, submitted March 30, 2026, is
    titled `Meta-Harness: End-to-End Optimization of Model Harnesses`. Its
    abstract says LLM systems depend on harness code that decides what
    information to store, retrieve, and present to the model, and that text
    optimizers are poorly matched to harness optimization because they
    compress feedback too aggressively. Meta-Harness searches over harness
    code with an agentic proposer that accesses source code, scores, and
    execution traces for prior candidates through a filesystem. The abstract
    reports a 7.7 point online text-classification gain using 4x fewer context
    tokens, a 4.7 point average gain on 200 IMO-level retrieval-augmented math
    problems across five held-out models, and harnesses that surpass hand-
    engineered baselines on TerminalBench-2.
  - Current gap: the paper cache, paper index, and TODO coverage do not
    include `2603.28052` as its own source. Existing rows mention
    Meta-Harness only as a related baseline or applicability boundary while
    covering AHE, AI Harness Engineering, Adaptive Auto-Harness, RHO,
    HarnessFix, and SIA. They do not track Meta-Harness-specific harness-code
    search, agentic proposer filesystem access, prior source/score/trace
    corpora, context-token efficiency, held-out model transfer, or
    TerminalBench-2 harness benchmark evidence.
  - Required result: add paper-manifest and paper-index coverage for
    `2603.28052`: title/authors/arXiv version/date/PDF digest, source
    license, linked-code URL/status, relation to AlphaEvolve and LibreEvolve
    harness assumptions, harness-code candidate schema, agentic proposer
    records, filesystem corpus layout, prior source/score/trace metadata,
    candidate retrieval policy, harness mutation/evaluation records,
    information storage/retrieval/presentation artifacts, context-token
    efficiency reports, online text-classification metadata, RAG math and
    held-out model transfer records, TerminalBench-2 benchmark metadata, hand-
    engineered baseline identities, code/artifact availability if any,
    reproducibility status, and README/ROADMAP wording that treats
    Meta-Harness as missing paper evidence rather than implemented LibreEvolve
    support.

- [ ] Track AlphaEvolve MARL algorithm-discovery paper evidence.
  - Paper/source evidence: arXiv `2602.16928`, submitted February 18, 2026
    and last revised May 7, 2026, is titled `Discovering Multiagent Learning
    Algorithms with Large Language Models`. Its abstract says AlphaEvolve is
    used to search two game-theoretic algorithm families, CFR and PSRO,
    yielding VAD-CFR and SHOR-PSRO. The paper evaluates those solvers against
    human-designed baselines across an 18-game suite spanning Poker,
    Goofspiel, Liar's Dice, Blotto, and Battleship variants, then uses
    systematic ablations and distillation to identify minimal solvers WOP-CFR
    and PM-PSRO that generalize with reduced structural complexity. It uses
    OpenSpiel, exact game-tree exploitability, deterministic algorithms, and a
    four-game training split plus fourteen-game test split.
  - Current gap: `papers/README.md` lists `2602.16928` only as
    `Background only; no CFR/PSRO benchmark or game-theoretic evaluator`.
    The active TODO coverage does not yet track a first-class paper/source
    boundary for CFR/PSRO candidate schemas, imperfect-information game
    evaluator protocols, train/generalization game splits, baseline solver
    identities, mechanism-coupling ablations, structural complexity, or
    distilled-solver handoff evidence. It also does not preserve paper-facing
    rows for the CFR/PSRO skeleton class names, exact-oracle PSRO, IQM
    log-improvement scores, 1000 random constant-sum normal-form games per
    `(N, A)` configuration, exact-exploitability scale limits below `350K`
    information states, or the single-AlphaEvolve-trajectory and tabular-
    baseline caveats.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2602.16928`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve problem/evaluator assumptions, CFR/PSRO candidate schemas,
    game-suite taxonomy with information-state/action metadata, train/
    evaluation split metadata, game-specific metric definitions, exact
    exploitability traversal records, random-seed and budget records, VAD-CFR
    and SHOR-PSRO result tables, human-designed baseline identities, IQM
    ablation and distillation records, WOP-CFR and PM-PSRO generalization
    reports, structural-complexity measures, exact-oracle and exact-payoff
    PSRO records, random normal-form validation rows, limitation/caveat
    records, reproducibility status, and README/ROADMAP wording that treats
    MARL algorithm discovery as missing paper evidence rather than implemented
    LibreEvolve support.

- [ ] Track AlphaEvolve Ramsey-number paper evidence.
  - Paper/source evidence: arXiv `2603.09172`, submitted March 10, 2026 and
    last revised April 21, 2026, is titled `Reinforced Generation of
    Combinatorial Structures: Ramsey Numbers`. Its abstract says AlphaEvolve
    improved lower bounds for nine classical Ramsey numbers, including
    `R(3,13)`, `R(3,18)`, `R(4,13)`, `R(4,14)`, `R(4,15)`, `R(4,16)`,
    `R(4,18)`, `R(4,19)`, and `R(4,20)`. It also reports recovering all
    exact known Ramsey lower bounds, matching many other best-known lower
    bounds, and using AlphaEvolve as a single meta-algorithm that yields
    search algorithms for those results. In the introduction, the certificate
    semantics are explicit: a graph with `n` vertices, no `r`-clique, and no
    `s`-independent set proves `R(r,s) >= n+1`. Algorithm 1 defines the
    AlphaEvolve Ramsey setup as evolving code from an empty baseline; each
    program returns a valid primary graph `G1` and a larger prospect graph
    `G2`; `G1` is size-scored with boosts for matching or exceeding `n_SoTA`;
    and `G2` receives a bonus from low `r`-clique plus `s`-independent-set
    violations relative to a random-graph expectation. Table 1 reports 28
    colored lower-bound cells, Table 2 groups search algorithms by
    initialization family, and the appendix summarizes Algorithms 2-34. The
    PDF embeds public Google Research links for the nine improved-bound graph
    constructions and the AI-discovered search algorithms.
  - Current gap: `papers/README.md` lists `2603.09172` as a constructive math
    benchmark candidate with `Not implemented; potential future benchmark`,
    and the active TODO coverage does not yet track this paper-specific
    evidence. Existing Appendix B and constructive-math gaps cover broad
    family/status registries, but not Ramsey-specific graph witness schemas,
    `R(s,t)` lower-bound verifier contracts, exact-bound recovery records,
    matched-best-known result rows, or per-result prior/current attribution
    for the nine reported improvements. They also do not preserve the
    off-by-one distinction between graph size and implied Ramsey lower bound,
    Algorithm 1's primary/prospect graph scoring evidence, artifact URLs for
    improved-bound constructions and generated code, the 28-cell Table 1
    coverage boundary, Gemini-3 summary/provenance caveats for Table 2, or the
    paper's source distinction between public references, graph-only prior
    evidence, and personal-communication baselines.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2603.09172`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve constructive-math assumptions, Ramsey-number parameter rows,
    graph witness artifact schema, verifier/certifier metadata, exact-bound
    recovery suite records, best-known-bound comparison rows, prior/current
    value provenance for all reported improvements, search-algorithm
    provenance, seed/budget records, witness graph hashes, independent checker
    outputs, reproducibility status, and README/ROADMAP wording that treats
    Ramsey-number discovery as missing paper evidence rather than implemented
    LibreEvolve support. Paper evidence should additionally capture the
    `R(r,s) >= n+1` witness semantics, primary/prospect graph output schema,
    expected-violation scoring formula inputs, Table 1 status classes
    (exact-match, best-known-match, and new-result), Table 2 initialization
    taxonomy, appendix algorithm identifiers 2-34, public Google Research
    construction/code links, and baseline-reference caveats for Radziszowski
    2024, Exoo/Tatarevic 2015, Exoo 2006, Tatarevic 2020, Exoo 2012,
    Harborth/Krause 2003, and graph-only or personal-communication sources.

- [ ] Track AlphaEvolve local-correction combinatorics paper evidence.
  - Paper/source evidence: arXiv `2603.06692`, submitted March 4, 2026, is
    titled `Evolving Local Corrections for Global Constructions in
    Combinatorics`. Its abstract says AlphaEvolve is used as an experimental
    engine for proposing and iteratively refining finite correcting-step
    certificates. It studies graph reconstruction from vertex-deleted
    subgraphs, Alon-Tarsi parity for Latin squares via sign-reversing
    involutions built from local trades, and Rota's Basis Conjecture via local
    exchange policies on collections of bases. It describes experimental
    setups, scoring protocols, and search outcomes leading to concrete
    conjectures, while explicitly not claiming proofs. Section 2 defines the
    paper's AlphaEvolve setup as fixed mathematical harnesses plus short
    Python evolvable blocks, hard validity constraints, shaped soft progress
    scores, robust aggregation over random symmetry actions, and
    Gemini-generated summaries of 15-24 hour runs with more than 5000
    candidate results. The graph section reports `1420/1420` bipartite and
    `896/896` planar reconstructions under worst-of-five scrambles; the
    Alon-Tarsi section reports Tables 1-3 for orders `8,10,12,14,26`; and the
    Rota section reports Tables 4-6 for circuit-rich `F2` rank-5, rank-7, and
    variable-rank `5,7,9,11,13` benchmarks.
  - Current gap: `papers/README.md` lists `2603.06692` as `Not implemented;
    potential future benchmark`, and the active TODO coverage does not yet
    track this paper-specific evidence. Broad constructive-math TODOs do not
    capture local-correction certificate schemas, graph reconstruction from
    vertex-deleted subgraphs, Latin-square local trade/involution evidence,
    Rota basis-exchange policies, scoring protocols, explicit algorithm
    outputs, or proof-status boundaries for generated conjectures. They also
    omit the paper's tested-regime details: bipartite matrix decks with
    independently permuted row/column cards, planar connected biconnected
    minimum-degree-at-least-3 non-maximal graph buckets, exact deck equality
    hardening after Weisfeiler-Lehman surrogate risk, Latin-square residual
    bias and isotopy anti-overfitting metrics, Rota insert/repair move
    formalism, circuit-oracle limitations, majority-rollout success, and
    appendix evolved-code/Gemini-summary provenance.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2603.06692`: title/author/arXiv version/date/PDF digest, source license,
    code/artifact URL/status, relation to AlphaEvolve and LibreEvolve
    constructive-math assumptions, local-correction certificate schemas,
    finite-step trace artifacts, graph/Latin-square/Rota case-study metadata,
    scoring protocol records, seed/budget records, explicit generated
    algorithms, structural-pattern summaries, conjecture statements,
    proof-status and traditional-analysis handoff fields, checker/verifier
    hooks, reproducibility status, and README/ROADMAP wording that treats
    local-correction combinatorics as missing paper evidence rather than
    implemented LibreEvolve support. Paper evidence should also preserve
    Conjectures 4-11, Tables 1-6, benchmark sizes and success metrics,
    AlphaEvolve experiment IDs where reported (`0_9751`, `0_9774`, `0_7176`),
    graph exact-isomorphism/canonical-label verification, Latin trade support
    and isotopy-stability metrics, Rota fitness weights and circuit-rich pool
    definitions, appendix evolved-code artifact status, AI-summary/AI-use
    declaration provenance, and caveats that these are experimental
    conjecture-generating results rather than proof certificates.

- [ ] Track AlphaEvolve bilateral-trade lower-bound paper evidence.
  - Paper/source evidence: arXiv `2603.08679`, submitted March 9, 2026, is
    titled `A New Lower Bound for the Random Offerer Mechanism in Bilateral
    Trade using AI-Guided Evolutionary Search`. Its abstract invokes the
    Myerson-Satterthwaite setting for bilateral trade, contrasts first-best
    GFT with BIC and BB mechanisms, focuses on the Random-Offerer mechanism,
    and says AlphaEvolve searches value distributions to find a worst-case
    instance with `GFT_FB / GFT_RO >= 2.0749`, improving on prior
    counterexamples including an explicit example near `2.02`. Sections 3-5
    define the exact benchmark: one seller cost and one buyer value from
    independent known distributions; first-best GFT is `E[(b-s)+]`; Random
    Offerer is `0.5*GFT_SO + 0.5*GFT_BO` using optimal seller-offering and
    buyer-offering take-it-or-leave-it prices; the objective is the supremum
    of `GFT_FB/GFT_RO`. The search fixes the buyer to the Discrete Equal
    Revenue distribution, evolves the seller CDF over `{0,...,H}` with
    `H=20000`, and reports a rounded mixture-of-modulated-power-laws seller
    CDF with `GFT_FB ~= 1.2322`, `GFT_SO ~= 0.3312`,
    `GFT_BO ~= 0.8565`, `GFT_RO ~= 0.5939`, and ratio `2.0749`. Section 4.3
    and Appendix A describe rounding probabilities to `1e-15` multiples and
    exact integer GFT computation.
  - Current gap: `papers/README.md` lists `2603.08679` as background-only
    mechanism-design context with no bilateral-trade distribution benchmark,
    and the active TODO coverage does not yet track this paper-specific
    evidence. Broad benchmark gaps do not capture value-distribution witness
    schemas, FB/RO GFT calculations, economic mechanism assumptions, ratio
    tolerance, or lower-bound baseline attribution. They also omit the fixed
    Discrete Equal Revenue buyer fixture, evolved seller-generator code
    artifact, mixture/modulated-power-law parameter ledger, exact SO/BO
    reserve-price evaluation, rounded-versus-unrounded distribution caveat,
    appendix evaluator code, and the paper's undocumented alternate searches
    that reportedly reached `2.08` when evolving the buyer after fixing the
    seller and below `2.07` when co-evolving both sides.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2603.08679`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve economic-mechanism assumptions, value-distribution candidate
    schemas, buyer/seller support and probability constraints, FB and RO GFT
    calculation metadata, BIC/BB assumption records, ratio objective and
    tolerance policy, witness distribution artifacts, prior `2` conjecture
    and `~2.02` counterexample baselines, seed/budget records, independent
    checker outputs, reproducibility status, and README/ROADMAP wording that
    treats bilateral-trade lower-bound search as missing paper evidence rather
    than implemented LibreEvolve support. Paper evidence should additionally
    preserve the `H=20000` support limit, fixed buyer survival function,
    evolved seller CDF formula and code listing, monotonicity/rounding
    validation, exact FB/SO/BO/RO component rows, optimal-price witness policy,
    ratio comparison to the original `2` conjecture and Babaioff et al. `~2.02`
    example, appendix evaluator hash, unrounded-mixture open-status caveat,
    and source-scoped status for the not-detailed `2.08` alternating-search
    observation.

- [ ] Track AlphaEvolve Magellan compiler-optimization paper evidence.
  - Paper/source evidence: arXiv `2601.21096`, submitted January 28, 2026 and
    accepted to `C4ML@CGO'26`, is titled `Magellan: Autonomous Discovery of
    Novel Compiler Optimization Heuristics with AlphaEvolve`. Its abstract
    presents Magellan as an agentic framework that evolves compiler passes by
    synthesizing executable C++ decision logic, coupling an LLM coding agent
    with evolutionary search and autotuning. It reports closed-loop
    generation, macro-benchmark evaluation, and refinement across production
    optimization tasks, including LLVM function inlining, register allocation,
    and preliminary XLA portability. Its method section records policy
    proposal in EVOLVE-BLOCK-delimited compiler source, local compiler rebuild
    and macro-benchmark evaluation, hyperparameter tuning, and feedback
    incorporation.
  - Current gap: `papers/README.md` lists `2601.21096` as background-only
    compiler-optimization application context with no compiler-heuristic
    benchmark or compiler pass runner, and the active TODO coverage does not
    yet track this paper-specific evidence. Broad systems and compiler gaps
    do not capture Magellan's C++ decision-logic candidates, macro-benchmark
    datasets, compiler-pass integration points, binary-size and end-to-end
    performance metrics, register-allocation priority rules, XLA portability
    records, or expert-baseline comparison evidence. They also do not require
    paper-facing rows for feature-based versus full-API inlining,
    Vizier-style autotuning, invalid-sample-rate reduction, temporal/domain
    generalization, generated-code maintainability caveats, XLA e-graph
    extraction, or auto-sharding contest split/protocol limits.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2601.21096`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve compiler assumptions, executable C++ decision-logic candidate
    schemas, compiler-pass integration metadata, LLVM inlining task records,
    register-allocation task records, XLA e-graph extraction and
    auto-sharding task records, macro-benchmark provenance, metric definitions
    for binary-size and end-to-end performance, autotuning loop records with
    tuner identity and batch/round counts, feature/full heuristic mode labels,
    temporal/domain generalization rows, generated-policy size and
    maintainability caveats, expert/neural baseline identities, seed/budget
    records, compiler build/runtime environment metadata, independent checker
    outputs, reproducibility status, and README/ROADMAP wording that treats
    Magellan-style compiler optimization as missing paper evidence rather
    than implemented LibreEvolve support.

- [ ] Track AlphaEvolve ArchAgent computer-architecture paper evidence.
  - Paper/source evidence: arXiv `2602.22425`, submitted February 25, 2026, is
    titled `ArchAgent: Agentic AI-driven Computer Architecture Discovery`.
    Its abstract presents ArchAgent as an automated architecture-discovery
    system built on AlphaEvolve. It designs and implements cache replacement
    policies within an established policy-design competition, reports `5.3%`
    IPC speedup over prior SoTA on public multi-core Google Workload Traces,
    `0.9%` IPC speedup over existing SoTA on single-core SPEC06, `3-5x`
    faster development than prior human-developed policies, `2.4%` IPC
    improvement from post-silicon hyperspecialization on SPEC06, and
    simulator-escape behavior in a popular microarchitectural simulator. The
    paper grounds the result in ChampSim C++ cache-policy code, CRC-style
    single/multi-core configurations, IPC normalized to LRU, short feedback
    simulations and longer validation simulations, and manual/rule-based
    checks for hardware realism.
  - Current gap: `papers/README.md` lists `2602.22425` as background-only
    computer-architecture application context with no architecture-design
    simulator or cache-policy benchmark, and the active TODO coverage does
    not yet track this paper-specific evidence. Broad systems gaps do not
    capture cache replacement policy schemas, simulator integration,
    workload-trace provenance, single-core/multi-core benchmark splits, IPC
    speedup objectives, SoTA policy baselines, post-silicon specialization
    metadata, or simulator-escape risk controls. They also do not preserve
    paper-facing rows for the `48 KB` policy-state limit, prefetch/no-prefetch
    CRC tracks, 100M/1B and 20M/50M/75M instruction-count protocols,
    Policy31/61/62 mechanism descriptions, ablation studies, distributed
    simulation cancellation/failure handling, or the Policy12 write-bypass
    simulator escape.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2602.22425`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve architecture assumptions, cache replacement policy candidate
    schemas, ChampSim integration metadata, CRC hardware/prefetch
    configuration rows, Google Workload Trace and SPEC06 dataset provenance,
    single-core/multi-core benchmark splits, evolution and validation
    instruction-count protocols, IPC metric definitions, prior-SoTA baseline
    identities, generated policy artifacts and mechanism labels, state-budget
    and hardware-realizability checks, ablation rows, post-silicon
    specialization parameter records, simulator-escape evidence and
    containment policy, distributed-simulation reliability records,
    seed/budget records, independent checker outputs, reproducibility status,
    and README/ROADMAP wording that treats ArchAgent-style computer-
    architecture discovery as missing paper evidence rather than implemented
    LibreEvolve support.

- [ ] Track AlphaEvolve Fault2Flow workflow-automation paper evidence.
  - Paper/source evidence: arXiv `2511.12916`, submitted November 17, 2025, is
    titled `Fault2Flow: An AlphaEvolve-Optimized Human-in-the-Loop Multi-Agent
    System for Fault-to-Workflow Automation`. Its abstract says Fault2Flow
    addresses power-grid fault diagnosis by extracting regulatory logic into
    PASTA-formatted fault trees, adding expert knowledge through a human-in-
    the-loop verification interface, optimizing reasoning logic with a novel
    AlphaEvolve module, and synthesizing final verified logic into n8n-
    executable workflows. It reports transformer fault-diagnosis validation
    with `100%` topological consistency and high semantic fidelity. The PDF
    body specifies a decoupled frontend/backend system, regulatory-PDF
    extraction to Markdown with MinerU, MySQL plus Milvus storage, PlantUML
    mind-map generation, PASTA fault-tree translation, OpenEvolve-linked
    AlphaEvolve structural optimization, n8n workflow construction and
    activation, and iterative workflow verification from synthesized test
    samples. Its case study uses the national standard `DL/T 722-2014` for
    dissolved-gas transformer diagnosis, focusing on three-ratio logic, and
    evaluates 16 expert-designed transformer fault-tree cases. Table 1 reports
    LRM, SF, TC, E2ERC, success/failure, and average-token rows for Qwen3-80B
    and GPT-4.1 end-to-end baselines plus Qwen3-14B/32B/80B and GPT-4.1
    Fault2Flow variants.
  - Current gap: `papers/README.md` lists `2511.12916` as background-only
    AlphaEvolve-optimized workflow application context with no fault-to-
    workflow or human-in-the-loop multi-agent benchmark, and the active TODO
    coverage does not yet track this paper-specific evidence. Broad
    framework/plugin gaps do not capture regulatory-source provenance, PASTA
    fault-tree schemas, expert verification states, reasoning-logic
    optimization records, n8n workflow artifacts, transformer fault-diagnosis
    datasets, or topology/semantic metrics. They also omit the paper's
    placeholder ACM/conference/DOI metadata, frontend library stack,
    MinerU/MySQL/Milvus backend, PlantUML intermediate format, PASTA
    self-check status, synthesized verification samples, GPT-5 evaluator usage
    for LRM/SF, exact TC and E2ERC formulas, token-efficiency comparison, and
    the 16-case dataset split between three-ratio and characteristic-gas
    methods.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2511.12916`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve workflow assumptions, regulatory-text source provenance,
    PASTA fault-tree candidate schemas, expert-review/human-in-the-loop state
    records, reasoning-logic optimization metadata, n8n workflow artifact
    schema, transformer fault-diagnosis dataset provenance, topological-
    consistency and semantic-fidelity metric definitions, seed/budget
    records, independent checker outputs, reproducibility status, and
    README/ROADMAP wording that treats Fault2Flow-style fault-to-workflow
    automation as missing paper evidence rather than implemented LibreEvolve
    support. Paper evidence should additionally preserve DL/T 722-2014 source
    scope, three-ratio and characteristic-gas case counts,
    Qwen3-Next-80B-A3B-Instruct configuration, PlantUML and PASTA intermediate
    artifacts, AlphaEvolve/OpenEvolve multi-island optimization claims, n8n API
    activation and verification-loop records, Table 1 values including `16/0`
    Fault2Flow success and end-to-end baseline failures, GPT-5 judge caveats,
    human-annotation/data-ethics records, placeholder ACM metadata caveats,
    and source-scoped status until executable workflow artifacts are locally
    reproduced.

- [ ] Track TTT-Discover test-time-training paper evidence.
  - Paper/source evidence: arXiv `2601.16175`, submitted January 22, 2026 and
    last revised February 5, 2026, is titled `Learning to Discover at Test
    Time`. Its abstract contrasts AlphaEvolve-style frozen-LLM prompting with
    reinforcement learning at test time, where the model continues training
    on experience from one specific test problem. It defines Test-Time
    Training to Discover (TTT-Discover), focuses on continuous rewards, and
    reports attempted-problem results across mathematics, GPU kernel
    engineering, algorithm design, and biology, including Erdos minimum
    overlap, an autocorrelation inequality, a GPUMode kernel competition with
    up to `2x` faster results, AtCoder competitions, and single-cell
    denoising. The abstract states results use open model `OpenAI
    gpt-oss-120b`, public code, Tinker test-time-training runs, expert or
    organizer review, and costs of only a few hundred dollars per problem.
    The paper body formalizes discovery as finding a state `s` with
    `R(s) > r_sota`, defines Algorithm 1 with mutable weights `theta_i`,
    buffer `H_i`, train/reuse subroutines, an adaptive entropic objective, and
    PUCT reuse, and reports fixed hyperparameters in Table 9: `50` steps,
    `512` rollouts per step, LoRA rank `32`, Tinker context window `32768`,
    prompt-plus-thinking limit `26000`, Adam `4e-5`, and `gamma = ln(2)`.
  - Current gap: `papers/README.md` lists `2601.16175` as background-only
    test-time discovery context, and the active TODO coverage does not yet
    track this paper-specific evidence. Existing AlphaEvolve and framework
    gaps do not capture mutable model-policy state, RL-at-test-time training
    records, Tinker run provenance, open-model checkpoint identity, continuous-
    reward task definitions, cross-domain benchmark rows, expert/organizer
    review artifacts, or cost-per-problem accounting. They also omit the
    public GitHub/project/result links, Table 2 math comparisons against
    AlphaEvolve, AlphaEvolve V2, ThetaEvolve, OpenEvolve, and Best-of-25600,
    Table 4/5 GPUMode runtime rows, Table 6 AtCoder official-score rows,
    Table 7 OpenProblems denoising rows, Table 8 ablations, Table 9
    hyperparameters, Table 10 Triton-filtered MLA results, OpenEvolve
    context-window truncation caveats, and the `Best-of-25600` versus Figure 4
    `50 * 512 = 256000` inconsistency.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2601.16175`: title/authors/arXiv version/date/PDF digest, source
    license, public code URL/status, relation to AlphaEvolve frozen-search and
    LibreEvolve provider assumptions, mutable policy/training-state schema,
    RL objective and rollout-selection metadata, Tinker/API training-run
    records, open-model/checkpoint provenance, continuous-reward task
    definitions, Erdos/autocorrelation/GPUMode/AtCoder/single-cell benchmark
    records, prior-art and AlphaEvolve/OpenEvolve baseline identities, expert
    or organizer review artifacts, cost/budget accounting, seed/run records,
    independent checker outputs, reproducibility status, and README/ROADMAP
    wording that treats TTT-Discover-style test-time training as missing
    paper evidence rather than implemented LibreEvolve support. Paper evidence
    should additionally preserve the exact public URLs, result notebook paths,
    GPUMode and AtCoder submission links, Modal and OpenProblems harness
    provenance, per-domain verifier limits, LoRA/checkpoint lineage, adaptive-
    beta and PUCT formulas, table-level result rows, expert-review identities,
    official/retrospective evaluation status, and source-scoped caveats for
    any internally inconsistent sampling-budget text.

- [ ] Track AlphaEvolve Bruhat-interval hypercube paper evidence.
  - Paper/source evidence: arXiv `2601.01235`, submitted January 3, 2026, is
    titled `Bruhat intervals that are large hypercubes`. Its abstract studies
    big Bruhat intervals that are poset hypercubes in the symmetric group
    `S_n`, says AlphaEvolve-suggested permutations revealed a pattern that
    performed well for tested `n` and was proved for general `n`, exhibits
    for powers of `2` a hypercube of dimension `O(n log n)`, characterizes
    vertices as dyadically well-distributed permutations, and connects the
    construction to Kazhdan-Lusztig `R`-polynomial coefficients plus lower
    bounds for frozen variables in open Richardson cluster algebras and for
    embeddings of Bruhat graphs. The paper body gives the actual witness
    machinery: Definition 2.1's dyadic basic intervals and exact-one condition,
    bit-reversal endpoints `x_m`/`y_m`, Ehresmann matrix Bruhat comparisons,
    complementary blocks, the order-preserving map `phi` to `S_2^{C_m}`, local
    flips, Proposition 2.20's poset isomorphism, and Theorem 2.21's
    `D_m = [x_m, y_m]` hypercube of rank `m * 2^(m-1)`.
  - Current gap: `papers/README.md` lists `2601.01235` as a constructive math
    benchmark candidate with `Not implemented; potential future benchmark`,
    and the active TODO coverage does not yet track this paper-specific
    evidence. Broad Appendix B and constructive-math gaps do not capture
    permutation generator schemas, Bruhat interval verification, hypercube
    isomorphism checks, dyadic well-distribution predicates, `S_n` power-of-
    two benchmark rows, Kazhdan-Lusztig coefficient linkage, cluster-algebra
    consequence fields, or the boundary between AlphaEvolve-suggested finite
    evidence and human-written general proofs. They also omit Section 4's
    experimental record: FunSearch as a Python-program search over permutation
    pairs maximizing `d_{x,y}`, adjacent-transposition output encoding,
    deterministic prompt rule, Mistral model and roughly `$10` FunSearch cost,
    AlphaEvolve generalizer-mode scoring over `n = 10..50`, Gemini 2.5
    Flash/Pro calls, `3000-5000` programs and roughly `$70` public-rate cost,
    public code/prompt/output URL, the observed recurrence
    `alpha(2n)=2 alpha(n)+n`, and the note that the evolved program contained
    likely unused simulated-annealing/search code.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2601.01235`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve constructive-math assumptions, permutation candidate schemas,
    Bruhat interval records, poset-hypercube witness artifacts, dyadic well-
    distribution checker metadata, dimension/asymptotic-bound records,
    Kazhdan-Lusztig `R`-polynomial coefficient metadata, cluster-algebra and
    Bruhat-graph consequence records, finite-test versus general-proof status,
    seed/budget records, independent checker outputs, reproducibility status,
    and README/ROADMAP wording that treats Bruhat-interval hypercube discovery
    as missing paper evidence rather than implemented LibreEvolve support.
    Paper evidence should additionally preserve the PDF date/arXiv date
    distinction, Adam Zsolt Wagner acknowledgement/contribution caveat,
    FunSearch/AlphaEvolve prompt and evaluator text, model/cost/run-count
    metadata, public repository artifact status, low-discrepancy `(0,m,2)`-net
    and `t`-adic extension notes, `R`-polynomial/d-invariant formulas,
    cluster-frozen-variable and good-embedding consequences, and source-scoped
    proof-status caveats before any benchmark claim is promoted.

- [ ] Track global NLP solver comparator paper evidence.
  - Paper/source evidence: arXiv `2601.05943`, submitted January 9, 2026, is
    titled `Global Optimization for Combinatorial Geometry Problems`. Its
    abstract says AlphaEvolve produced new best-known solutions for hard
    geometric and combinatorial problems, then asks whether modern off-the-
    shelf global optimization solvers can match those results when the same
    problems are directly formulated as NLPs. It evaluates straightforward NLP
    formulations on a subset of the AlphaEvolve benchmark suite using
    commercial FICO Xpress and open-source SCIP, and reports that without
    solver modifications both solvers reproduce and sometimes improve on
    best solutions from the literature, including recent LLM-driven
    discoveries. The body selects three AlphaEvolve-related families: min-max
    distance ratio, circle packing in a square or perimeter-4 rectangle, and
    regular-hexagon packing. It defines the generic NLP form, Mosel
    implementations, QCP distance/circle formulations, and a hexagon model
    with rotation, half-space coefficients, and Farkas multipliers.
  - Current gap: `papers/README.md` lists `2601.05943` as an optimization
    benchmark comparator with no nonlinear-programming solver comparison
    harness, and the active TODO coverage does not yet track this paper-
    specific evidence. Broad constructive-math and benchmark gaps do not
    capture direct NLP formulation artifacts, solver identity/license
    provenance, solver-run parameters, incumbent/bound/certificate records,
    numerical tolerances, or result tables comparing Xpress/SCIP outcomes
    against AlphaEvolve and prior-literature baselines. They also omit the
    paper's arXiv `v2`/January 15, 2026 metadata, Mosel modeling-language
    detail, AlphaEvolve-repository validation-code claim, Table 1 improving
    squared-ratio rows, Table 2 circle-packing rows, Table 3 hexagon-packing
    rows, source links for Friedman packing pages/OpenEvolve/SciPy/SCIP, and
    the caveat that the paper does not separate which solver found which
    reported solution.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2601.05943`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve and
    LibreEvolve constructive-geometry assumptions, selected benchmark subset,
    NLP formulation schemas, variable/domain/constraint/objective records,
    FICO Xpress and SCIP solver identity/version/license metadata, solver
    parameter and time-limit records, incumbent/bound/certificate artifacts,
    numerical tolerance policy, prior-literature and AlphaEvolve baseline
    values, reproduced/improved/fell-behind outcome rows, seed/run records,
    independent checker outputs, reproducibility status, and README/ROADMAP
    wording that treats global-NLP solver comparison as missing paper evidence
    rather than implemented LibreEvolve support. Paper evidence should
    additionally preserve the selected problem subset, exact formulation
    variables and constraints, instance-size records such as `7` variables/
    `10` constraints through `91` variables/`876` constraints for distance
    ratio, all Table 1-3 values and rounding directions, solver-attribution and
    dual-bound-detail caveats, validation-code provenance, and the conclusion's
    distinction between direct optimization baselines and complementary
    LLM-driven model/prototype generation.

- [ ] Track post-AlphaEvolve autoconvolution improvement paper evidence.
  - Paper/source evidence: arXiv `2506.16750`, submitted June 20, 2025 and
    last revised August 10, 2025, is titled `An improved example for an
    autoconvolution inequality`. Its abstract gives a nonnegative step
    function with `575` equally spaced intervals whose autoconvolution ratio
    is at least `0.901564`. It explicitly improves on DeepMind's AlphaEvolve
    result, which used a `50`-interval nonnegative step function with value at
    least `0.8962`, and says the new function was found using simulated
    annealing and gradient-based methods instead of large language models.
    Theorem 1 gives the exact rational value
    `96086089410408840289339769 / 106577013451431545242354944` for
    `f = sum_{n=0}^{574} v_n 1_[n,n+1)`, with coefficients in Appendix A.
    Section 2 defines convolution samples `L_j` and formula `(3)`, which is
    the direct finite checker for any coefficient list.
  - Current gap: `papers/README.md` lists `2506.16750` as a constructive math
    benchmark candidate with `Not implemented; potential future benchmark`,
    and the active TODO coverage does not yet track this paper-specific
    evidence. Existing Appendix B.1-B.3 autoconvolution gaps cover the
    AlphaEvolve result family, but not this later 575-interval witness,
    non-LLM search provenance, objective recomputation, side-by-side
    AlphaEvolve baseline comparison, or rounded-value/tolerance policy. They
    also omit the public repository URL, `Inital HPC code.py`, `Refine HPC
    code.py`, `f95.py`, `coeffBL.txt`, `Verify.nb`, Mathematica verification
    snippet, row-major coefficient-table reading rule, referee-suggested
    integer-arithmetic modification, NCSU HPC resource acknowledgement, and
    comparison values against Matolcsi-Vinuesa `0.889226` and AlphaEvolve
    `0.89628`.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2506.16750`: title/authors/arXiv version/date/PDF digest, source
    license, code/artifact URL/status, relation to AlphaEvolve Appendix B and
    LibreEvolve autoconvolution assumptions, 575-interval step-function
    witness schema, coefficient/value artifact hashes, convolution and norm
    recomputation metadata, objective definition and tolerance policy,
    AlphaEvolve 50-interval `0.8962` baseline record, simulated-annealing and
    gradient-method provenance, prior/current result rows, independent checker
    outputs, reproducibility status, and README/ROADMAP wording that treats
    this post-AlphaEvolve autoconvolution improvement as missing paper evidence
    rather than implemented LibreEvolve support. Paper evidence should
    additionally preserve the arXiv `v2`/August 10, 2025 version, the claim
    that the example was found in November 2024 before the authors knew about
    AlphaEvolve's example, translation/dilation invariance, support
    normalization to `[-1/4, 1/4]`, AlphaEvolve coefficient reversal from the
    DeepMind notebook, normalized graph/correlation comparisons, exact
    coefficient payload hashes, and checker parity between Python and
    Mathematica artifacts.

- [ ] Track post-AlphaEvolve sums-and-differences construction paper evidence.
  - Paper/source evidence: arXiv `2505.16105`, submitted May 22, 2025, is
    titled `Sums and differences of sets (improvement over AlphaEvolve)` and
    authored by Robert Gerbicz; the cached PDF hash is
    `90d63d13afd7b8e15ceac25a4cef3f6b1c974a12a7893e80bd18e3ef4e16e1e8`.
    Its abstract says AlphaEvolve used a set of `54265` integers to improve
    the known lower bound from `theta = 1.14465` to `theta = 1.1584`. The
    paper improves this to `theta = 1.173050` with an explicit `U` set
    containing more than `10^43546` elements, and uses the free GMP library
    for fast integer and floating-point arithmetic. The main construction uses
    `W(m, L, B)` bounded-coordinate sets and a base-`2B + 1` integer map,
    derives formulas for `|U + U|`, `|U - U|`, and `2 max(U) + 1`, reports
    `theta = 1.162997` for `m = 80`, `L = 64`, `B = 5`, and confirms
    `theta = 1.173050` for `m = 81411`, `L = 65536`, `B = 5` after about
    15 hours of exact integer arithmetic. It reports approximate values
    `|U| = 6.314107319e43546`, `|U + U| = 3.208492702e61228`,
    `|U - U| = 6.587554451e75899`, and `2 max(U) + 1 =
    6.605282799e84780`, with GMP code and exact computed values cited at
    `https://bit.ly/43mWCVC`.
  - Current gap: `papers/README.md` lists `2505.16105` as a constructive math
    benchmark candidate with `Not implemented; potential future benchmark`,
    and the active TODO coverage does not yet track this paper-specific
    evidence. Existing Appendix B sums-and-differences gaps do not capture
    this later explicit `U` construction, compressed representation needs for
    extremely large sets, `W(m, L, B)` formula evidence, base-`2B + 1`
    injectivity evidence, the `(80, 64, 5)` small-search result, exact
    computed-value retrieval from the cited code URL, GMP arithmetic
    provenance, `theta = 1.173050` recomputation, or side-by-side comparison
    against AlphaEvolve's `54265`-integer `1.1584` construction and the
    earlier `1.14465` bound.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2505.16105`: title/author/arXiv version/date/PDF digest, source license,
    code/artifact URL/status, relation to AlphaEvolve Appendix B and
    LibreEvolve sums-and-differences assumptions, explicit `U`-set
    construction schema, `W(m, L, B)` formula records, base-`2B + 1` encoding
    and injectivity evidence, huge-set compression/parametrization metadata,
    parameter records for `(80, 64, 5)` and `(81411, 65536, 5)`,
    sumset/difference-set cardinality records, max-element/q-value and
    set-size records, `theta` formula and tolerance policy, exact computed
    value payload hashes, AlphaEvolve `54265`-integer `1.1584` baseline
    record, previous `1.14465` bound attribution, GMP/version/arithmetic
    provenance, prior/current result rows, independent checker outputs,
    reproducibility status, and README/ROADMAP wording that treats this
    post-AlphaEvolve sums-and-differences improvement as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Track further post-AlphaEvolve sums-and-differences sequence paper
      evidence.
  - Paper/source evidence: arXiv `2506.01896`, submitted June 2, 2025, is
    titled `Sums and differences of sets: a further improvement over
    AlphaEvolve` and authored by Fan Zheng; the cached PDF hash is
    `3f04c75ccd850eb6e5c785e543f98d12446e9891399cc5246acae9335b4494c2`.
    Its abstract says it improves on DeepMind AlphaEvolve's
    `theta = 1.1584` and the later explicit-construction result
    `theta = 1.173050`, by constructing a sequence of `U` sets that in the
    limit establishes `theta = 1.173077`. The proof uses large-deviation
    estimates for `W(m, floor(rm), B)`, builds the same base-`2B + 1`
    integer-image construction as the prior sums-and-differences paper,
    bounds `q(U)`, `s(U)`, and `d(U)` asymptotically, and maximizes a limiting
    expression over `B`, `r`, and `a`. The numerical evidence is a MATLAB
    2024b tolerance sweep over `B = 3..10`, `r in (0.5, 2)`, and
    `a in (0, min(1, 1/r))`; the best row is `B = 5`, where
    `theta - 1 = 0.173077279785136` for both `1e-8` and `1e-10` tolerances.
    The paper embeds MATLAB code using `fminbnd`, `fminunc`, `logD`, `logW`,
    and a Legendre-transform objective for `I(c, B)`.
  - Current gap: `papers/README.md` lists `2506.01896` as a constructive math
    benchmark candidate with `Not implemented; potential future benchmark`,
    and the active TODO coverage does not yet track this paper-specific
    evidence. Existing sums-and-differences TODOs do not capture this
    sequence-of-sets construction, limiting lower-bound proof artifact,
    large-deviation lemma evidence, MATLAB-code provenance, tolerance-sweep
    reproducibility, convergence/tail-bound verification, or lineage
    comparison against both AlphaEvolve's `1.1584` finite witness and
    `2505.16105`'s `1.173050` explicit huge-set witness.
  - Required result: add paper-manifest and paper-index coverage updates for
    `2506.01896`: title/author/arXiv version/date/PDF digest, source license,
    code/artifact URL/status, relation to AlphaEvolve Appendix B and
    LibreEvolve sums-and-differences assumptions, sequence-of-`U` construction
    schema, parameter records for `B`, `r`, `a`, and finite-prefix `m`,
    finite-prefix artifacts, limiting-bound derivation metadata,
    large-deviation `I(c, B)` records, asymptotic `W(m, floor(rm), B)` count
    metadata, MATLAB-code extraction and independent reimplementation status,
    tolerance-sweep rows for `B = 3..10` and `1e-4..1e-10`,
    convergence/tail-bound checker records, sumset/difference-set cardinality
    records for finite prefixes, `theta` formula and tolerance policy,
    AlphaEvolve `1.1584` baseline, `2505.16105` `1.173050` baseline,
    prior/current result rows, independent checker outputs, reproducibility
    status, and README/ROADMAP wording that treats this further
    post-AlphaEvolve sums-and-differences improvement as missing paper
    evidence rather than implemented LibreEvolve support.

- [ ] Track UCB1 finite-time bandit paper evidence before backend-routing
      claims imply regret guarantees.
  - Paper/source evidence: the local
    `auer-cesa-bianchi-fischer-2002__UCB1_Finite_Time_Analysis_Multiarmed_Bandit.pdf`
    is `Finite-time Analysis of the Multiarmed Bandit Problem` by Peter Auer,
    Nicolo Cesa-Bianchi, and Paul Fischer, published in `Machine Learning`
    `47`, pages `235-256`, in 2002; the cached PDF hash is
    `82c8a8192bdb425fbe7662c59ee85faf47f59901f1a4999a732d04db82702a5d`.
    The paper presents UCB1 for `K > 1` arms with unknown reward distributions
    supported in `[0, 1]`, defines regret as expected loss from not always
    playing the best arm, and proves logarithmic finite-time regret bounds.
    Theorem 1 bounds regret by `8 * sum_i ln(n) / Delta_i` plus
    `(1 + pi^2 / 3) * sum_j Delta_j`, with the suboptimal-pull bound
    `E[T_i(n)] <= 8 ln(n) / Delta_i^2 + 1 + pi^2 / 3`. The proof uses
    empirical reward means, play counts, Chernoff-Hoeffding bounds, and a
    confidence-index policy; the paper later notes Theorems 1-3 do not
    require cross-machine reward independence and only need the per-arm
    conditional-mean condition `E[X_i,t | X_i,1, ..., X_i,t-1] = mu_i`. It
    also gives adjacent UCB2, `epsilon_n`-GREEDY, UCB1-NORMAL, and
    UCB1-TUNED variants under separate assumptions, with UCB1-TUNED reported
    as empirically stronger but without a proven regret bound.
  - Current gap: `papers/README.md` lists `auer-cesa-bianchi-fischer-2002` as
    the foundational bandit-policy source for LibreEvolve's heuristic
    UCB-style backend router, and README/ROADMAP/code wording says the router
    is heuristic. The paper TODOs do not yet preserve this UCB1 source row as
    a paper-facing evidence boundary with the bounded-support, iid-arm,
    conditional-mean/stationarity, regret-definition, reward-normalization,
    theorem-constant, and proof-scope assumptions needed to prevent backend-
    routing telemetry from being read as canonical UCB1 finite-time analysis.
    It also does not require variant-level status rows showing that UCB2,
    `epsilon_n`-GREEDY, UCB1-NORMAL, and UCB1-TUNED are unsupported unless
    separately implemented and validated.
  - Required result: add paper-manifest and paper-index coverage for
    `auer-cesa-bianchi-fischer-2002`: source URL/cache/hash, title/authors/
    venue/year, source-license or mirror status, UCB1 theorem-scope metadata,
    reward-support and conditional-mean/stationarity assumptions,
    regret-definition fields, theorem-constant records, scheduler-linkage
    records, canonical-index formula metadata, variant support matrix,
    UCB1-TUNED no-proof status, and README/ROADMAP wording that treats
    LibreEvolve's backend scheduler as heuristic unless those assumptions and
    regret reports are explicitly validated.

- [ ] Track GigaEvo framework paper evidence as a source-specific boundary.
  - Paper/source evidence: local arXiv `2511.17592`, `GigaEvo: An Open Source
    Optimization Framework Powered by LLMs and Evolution Algorithms`, by
    Valentin Khrulkov, Andrey V. Galichin, Denis Bashkirov, Dmitry Vinichenko,
    Oleg Travkin, Roman Alferov, Andrey Kuznetsov, and Ivan Oseledets was
    submitted November 17, 2025 as arXiv v1; the cached PDF hash is
    `9a14bf06a1323e63bf53234e79e44c41e1e78e0dc2f90578d74b928efd067113`.
    It describes an AlphaEvolve-inspired open-source framework with Redis
    program storage, an `asyncio` DAG execution engine, MAP-Elites
    quality-diversity evolution, LangGraph-based mutation, insight generation,
    bidirectional lineage tracking, flexible Hydra configuration, and
    reproduction experiments on AlphaEvolve benchmark problems. The paper
    defines Redis `Program` records with UUID, source, lifecycle state
    (`FRESH`, `RUNNING`, `COMPLETE`), metrics, genealogy, and DAG stage
    outputs; DAG stages include validation, execution, validator calls,
    complexity, insights, lineage analysis, ancestor/descendant collectors,
    and mutation-context assembly. It links both
    `https://github.com/AIRI-Institute/gigaevo-core` and
    `https://github.com/FusionBrainLab/gigaevo-core`.
  - Current gap: `papers/README.md` lists `2511.17592` as framework
    inspiration and says Redis lifecycle database, `asyncio` DAG engine,
    insight stage, and concurrent units are not implemented. Existing paper
    TODOs group GigaEvo with other inspiration rows, but do not preserve the
    GigaEvo PDF itself as a source-specific evidence boundary with
    architecture-component rows, lifecycle-state semantics, DAG-stage
    topology, insight/lineage artifacts, benchmark-reproduction claims, code
    repository status, Hydra problem-layout requirements, or validation that
    docs do not conflate grouped inspiration status with GigaEvo framework
    parity.
  - Required result: add paper-manifest and paper-index coverage for
    `2511.17592`: title/authors/arXiv version/date/PDF digest, source license,
    linked code URL/status, architecture-component inventory, Redis program
    lifecycle schema, DAG stage/dependency/caching metadata, insight and
    lineage-analysis records, mutation-operator mode/source details,
    Hydra/problem-layout metadata, benchmark-problem and reproduction-result
    rows for Heilbronn `n = 11`, circle packing `n = 26`/`n = 32`, kissing
    numbers, bin packing, and prompt/agent evolution, linked-model rows for
    Qwen3/Gemini/Qwen embedding/GPT-OSS usage where claimed, relation to
    AlphaEvolve and LibreEvolve, and README/ROADMAP/code wording that keeps
    GigaEvo framework behavior marked missing unless local implementation
    artifacts and reports prove it.

- [ ] Track CodeEvolve paper evidence as a source-specific boundary.
  - Paper/source evidence: local arXiv `2510.14150`, `CODE EVOLVE: an
    open-source evolutionary framework for algorithmic discovery and
    optimization`, by Henrique Assumpcao, Diego Ferreira, Leandro Campos, and
    Fabricio Murai was submitted as arXiv v4 on March 12, 2026; the cached PDF
    hash is
    `8dc8c35d24e2f6bce81e9608609e10b4dac5dd7072d155d9cd5c575d47472405`.
    It presents an islands-based genetic algorithm with weighted LLM
    ensembles, `SEARCH/REPLACE` edits, inspiration-based crossover,
    meta-prompting, depth-based targeted refinement, exploration scheduling,
    sandboxed evaluation, MAP-Elites/CVT-MAP-Elites archives, and
    AlphaEvolve/EoH benchmark and cost-efficiency comparisons. It defines
    solution fitness `fsol` and prompt fitness `fprompt`, uses Algorithm 1 for
    exploitation/exploration with ancestor depth `k`, inspirations, and
    `MetaPromptingLLM`, and reports Plateau Scheduler, elitist migration,
    runtime/memory-bounded AWS SageMaker evaluation, weighted
    GEMINI-2.5/Qwen3-Coder-30B ensembles, and code/results links at
    `https://github.com/inter-co/science-codeevolve` and
    `https://github.com/inter-co/science-codeevolve-experiments`.
  - Current gap: `papers/README.md` lists `2510.14150` as agentic
    code-evolution inspiration and says CodeEvolve-style crossover, targeted
    refinement, modular orchestration, and context-aware recombination are not
    implemented. Existing paper TODOs group CodeEvolve with other inspiration
    rows and mention mutation/crossover operator gaps generally, but do not
    preserve the CodeEvolve PDF itself as a source-specific evidence boundary
    with architecture rows, prompt/solution fitness definitions,
    operator-level claims, scheduler semantics, sandbox requirements,
    benchmark-result rows, ablation/cost claims, linked-code status,
    hyperparameter recommendations, or validation that docs avoid conflating
    LibreEvolve's prompt-program support with CodeEvolve framework parity.
  - Required result: add paper-manifest and paper-index coverage for
    `2510.14150`: title/authors/arXiv version/date/PDF digest, source license,
    linked code URL/status, island/population and prompt/solution fitness
    schemas, weighted ensemble and model-cost metadata, inspiration-crossover,
    meta-prompting, depth-refinement, and exploration-scheduler records,
    sandbox/runtime/memory-limit evidence, MAP-Elites/CVT archive metadata,
    AlphaEvolve benchmark rows for all 9 Table 1 instances, EoH benchmark rows
    for online bin packing/TSP/flow-shop scheduling, component/depth/
    inspiration/MAP-Elites/topology ablation rows, Qwen3-Coder-30B vs
    GEMINI-2.5 cost/runtime rows from Table 2, open-framework comparisons with
    OpenEvolve and ShinkaEvolve, LLM-backbone sensitivity rows, recommended
    hyperparameter defaults, relation to LibreEvolve, and README/ROADMAP/code
    wording that keeps CodeEvolve-specific behavior marked missing unless
    implementation artifacts and reports prove it.

- [ ] Track ThetaEvolve test-time learning paper evidence as a source-specific
      boundary.
  - Paper/source evidence: local arXiv `2511.23473`, `ThetaEvolve:
    Test-time Learning on Open Problems`, by Yiping Wang, Shao-Rong Su,
    Zhiyuan Zeng, Eva Xu, Liliang Ren, Xinyu Yang, Zeyi Huang, Xuehai He,
    Luyao Ma, Baolin Peng, Hao Cheng, Pengcheng He, Weizhu Chen, Shuohang
    Wang, Simon Shaolei Du, and Yelong Shen was submitted as arXiv v1 on
    November 28, 2025; the cached PDF hash is
    `8e74933b2a4dddbf80a063fb88438c95b62b982a5167bbb77213ce1e3839715d`
    and the PDF metadata declares CC-BY 4.0. It presents an
    AlphaEvolve-inspired dynamic environment using a single LLM, large program
    database, batch sampling over parents and responses, early checks, lazy
    penalties, reward shaping, optional GRPO/RL training at test time,
    checkpoint evaluation, and benchmark claims on circle packing,
    autocorrelation inequalities, and Hadamard matrices. It links public code
    at `https://github.com/ypwang61/ThetaEvolve`, builds on OpenEvolve and
    `slime`, and records batch size `B = 32`, `n = 16`, response length
    `16384`, rollout temperature `1.0`, and `16` concurrent verifier programs.
  - Current gap: `papers/README.md` lists `2511.23473` as test-time training
    inspiration and explicitly scopes LibreEvolve to clipped-reward JSONL
    export without online RL/GRPO training, checkpointing, resume semantics, or
    lazy-penalty dynamics. Existing paper TODOs group ThetaEvolve with other
    inspiration rows and separately track broader TTT-Discover work, but they
    do not preserve the ThetaEvolve PDF itself as a source-specific evidence
    boundary with dynamic-environment components, batch-sampling semantics,
    lazy-penalty/reward-shaping formulas, GRPO configuration, checkpoint
    provenance, evaluator-compatibility caveats, database-size/throughput
    ablations, benchmark rows, or comparison claims.
  - Required result: add paper-manifest and paper-index coverage for
    `2511.23473`: title/authors/arXiv version/date/PDF digest, source license,
    linked code URL/status, dynamic-environment architecture rows,
    single-LLM/database-size/batch-sampling metadata, early-check and
    lazy-penalty schemas, reward-shaping parameters, GRPO/RL training
    configuration, checkpoint and inference-transfer records, generated-sample
    counts, task/evaluator caveats for tolerance and corrected typos,
    AlphaEvolve/ShinkaEvolve/OpenEvolve baseline rows, Table 1 open-problem
    bound rows, Table 2/9 main `w/ RL` vs `w/o RL` rows, Table 3 static/format
    reward baseline rows, Table 4/10 database-size and database-design rows,
    Table 5/6 pipeline/throughput rows, Table 7 reward-shaping rows, Table 8
    timeout/reward-shaping configuration rows, relation to LibreEvolve's
    `ttt_rl` export, and README/ROADMAP/code wording that keeps
    ThetaEvolve-style test-time learning marked missing until implementation
    artifacts and reports prove it.

- [ ] Track ImprovEvolve modular-operator paper evidence as a source-specific
      boundary.
  - Paper/source evidence: local arXiv `2602.10233`, `ImprovEvolve: Ask
    AlphaEvolve to Improve the Input Solution and Then Improvise`, by Alexey
    Kravatskiy, Valentin Khrulkov, and Ivan Oseledets was submitted as arXiv
    v1 on February 10, 2026; the cached PDF hash is
    `8123f1b19d9ba6c891e642be28b1bd4395fff549131d2e45b619dfd28ddfe57a`.
    The PDF metadata declares CC-BY 4.0 and the front matter includes
    KDD 2026/ACM publication-rights language. It proposes evolving a class
    with `generate_config(seed)`, `improve(x)`, and `perturb(x, sigma)` rather
    than a direct solution generator. It combines those methods through a
    two-stage basin-hopping validation scheme, uses GigaEvo as the outer
    evolutionary backbone, reports hexagon-packing and second-autocorrelation
    results, and separates automated ImprovEvolve outputs from lightly
    human-edited `ImprovEvolve+E` variants. The PDF links GigaEvo at
    `https://github.com/FusionBrainLab/gigaevo-core`, OpenEvolve, AI Studio,
    and OpenRouter, but no ImprovEvolve-specific code URL appears in the
    extracted links.
  - Current gap: `papers/README.md` lists `2602.10233` as modular search
    inspiration and says LibreEvolve only has static modular guidance, not an
    enforced or executed `generate_config`/`improve`/`perturb` loop. Existing
    paper TODOs group ImprovEvolve with other inspiration rows, but do not
    preserve the ImprovEvolve PDF itself as a source-specific evidence
    boundary with interface semantics, basin-hopping validation parameters,
    GigaEvo dependency/backbone status, human-edit provenance, benchmark rows,
    ablations, model/provider provenance, compute budgets, or
    result-comparison claims.
  - Required result: add paper-manifest and paper-index coverage for
    `2602.10233`: title/authors/arXiv version/date/PDF digest, ACM/preprint
    rights metadata, linked code URL/status, class-interface schema,
    validation-scheme parameters, seed and perturbation schedules,
    monotonic-acceptance and basin-hopping records, GigaEvo relation, HEX and
    ACI2 benchmark/baseline/result rows, Gemini 3 Pro initial-program and
    Gemini 3 Flash Preview evolution provenance, common evolution parameters
    (`elites = 6`, `parents = 2`, `offspring = 10`, temperature `1`), human-
    edited variant attribution, CPU/GPU timeout budgets, Table 1/2/3 result
    and hyperparameter rows, Table 4 validation-scheme ablation rows,
    relation to LibreEvolve's `ModularPlugin`, and README/ROADMAP/code wording
    that keeps ImprovEvolve-style execution marked missing unless
    implementation artifacts and reports prove it.

- [ ] Track MadEvolve parameter-optimization paper evidence as a source-
      specific boundary.
  - Paper/source evidence: local arXiv `2602.15951`, `MadEvolve:
    Evolutionary Optimization of Cosmological Algorithms with Large Language
    Models`, by Tianyi Li, Shihui Zang, and Moritz Munchmeyer was submitted as
    arXiv v1 on February 17, 2026; the cached PDF hash is
    `ec47332c9b20ca391b8aedb6b8696c42aad20c976906d1e43f13490163daea19`
    and the PDF metadata uses the arXiv nonexclusive distribution license. It
    describes a framework similar to AlphaEvolve but focused on scientific
    algorithms with explicit free-parameter tracking and nested parameter
    optimization. It reports greedy one-shot derivative-free tuning,
    autodiff/Adam tuning for differentiable JAX/`vmad` programs, hybrid
    MAP-Elites/island/elite population management, UCB-style model selection,
    diff/full/synthesis mutation modes, automated lineage/comparison/report
    generation, and cosmology applications for BAO reconstruction, 21cm tidal
    reconstruction, and tSZ prediction. The PDF links `madevolve.org`,
    `tianyi-stack/MadEvolve`, `tianyi-stack/MadEvolve-Cosmo`, `biweidai/LDL`,
    `rainwoodman/vmad`, and four generated report PDFs.
  - Current gap: `papers/README.md` lists `2602.15951` as background only with
    no free-parameter optimization or innovation report, and completed TODOs
    only preserve that scoping. There is no source-specific active paper TODO
    for MadEvolve's PDF evidence, public framework/application repositories,
    parameter schemas, optimization budgets, differentiability requirements,
    per-task prompts/evaluators, report sections, run statistics, model
    contribution table, compute environment, reward-hacking caveats, or
    generalization claims. Existing docs also do not distinguish the framework
    repository from the cosmology application repository or the hosted report
    artifacts.
  - Required result: add paper-manifest and paper-index coverage for
    `2602.15951`: title/authors/arXiv version/date/PDF digest, source/license
    and public code status for madevolve.org, `tianyi-stack/MadEvolve`, and
    `tianyi-stack/MadEvolve-Cosmo`, parameter-declaration schema, free-parameter
    meaning/function records, one-shot and autodiff optimizer descriptions,
    JAX/vmad operator constraints, outer-loop population and LLM-scheduler
    details, diff/full/synthesis mutation-mode rows, generated-report section
    schema, BAO/iterative-BAO/21cm/tSZ benchmark rows, Table 1 result values,
    Table 2 success/improvement statistics, Table 3 model-contribution
    statistics, compute environment, prompt/evaluator artifact links,
    reward-hacking and over-parameterization caveats, Quijote/LDL/vmad dataset
    and dependency provenance, training/validation/test split records,
    madevolve.org report-link checks, and README/ROADMAP/code wording that
    keeps MadEvolve behavior marked missing unless local artifacts prove it.

- [ ] Track CausalEvolve causal-scratchpad paper evidence as a source-specific
      boundary.
  - Paper/source evidence: local arXiv `2603.14575v2`, `CausalEvolve: Towards
    Open-Ended Discovery with Causal Scratchpad`, by Yongqiang Chen, Chenxi
    Liu, Zhenhao Chen, Tongliang Liu, Bo Han, and Kun Zhang was submitted as
    arXiv v1 on March 15, 2026 and revised as v2 on March 29, 2026; the cached
    PDF hash is
    `b3190d25d802f5b9913e4e266b7dda1b76d2211d2d4cad68e1a5d0a3d03fc4d2`
    and the PDF metadata declares CC BY-NC-SA 4.0. It argues that
    evolve-based AI scientists need causal knowledge to avoid inefficient or
    oscillatory search. It formulates scientific discovery as a POMDP over
    hidden scientific knowledge, models evaluation as intervention on an SCM,
    defines outcome-level factors generated by LLMs from task/output
    descriptions, introduces CausalPlanner actions over factor direction, adds
    procedure-level factors from trial histories, estimates treatment effects,
    detects surprise patterns, and uses abductive reasoning to create new
    factors/hypotheses during evolution. Extracted PDF links include the arXiv
    v2 URL, OpenEvolve, Grok-4.1-fast, and causality/COAT references, but no
    dedicated CausalEvolve code repository URL.
  - Current gap: `papers/README.md` says LibreEvolve only has token-pattern
    outcome-factor guidance and no LLM causal scratchpad. Existing paper TODOs
    and completed entries preserve that broad scoping, but there is no active
    `2603.14575` source-specific evidence boundary for the paper version,
    theoretical claims, factor-generation prompts, executable outcome metrics,
    CausalPlanner intervention policy, procedure-factor extraction, treatment
    effects, surprise-pattern/abduction artifacts, benchmark tasks, seeds,
    step schedules, baseline/ablation rows, or result tables.
  - Required result: add paper-manifest and paper-index coverage for
    `2603.14575`: title/authors/arXiv version/date/PDF digest, code/source
    status, POMDP/SCM notation and theorem boundary, outcome-level factor
    schema, Appendix D metric definitions for Hadamard, second autocorrelation,
    circle packing, and AIME, executable factor-code provenance,
    CausalPlanner action/reward schedule, procedure-factor/COAT relation,
    approximate treatment-effect records, surprise-pattern definitions,
    abductive reasoning outputs, scratchpad memory update semantics, Table 1
    result rows, seed and step schedules, baseline/ablation method rows,
    Grok-4.1-fast-reasoning model provenance, environment-shift/generalization
    caveats, CC BY-NC-SA license metadata, no-code-link status, and
    README/ROADMAP/code wording that keeps local fixed regex factor guidance
    marked missing for CausalEvolve causal-scratchpad claims.

- [ ] Track DeepEvolve deep-research/debug-loop paper evidence as a source-
      specific boundary.
  - Paper/source evidence: local arXiv `2510.06056v1`, `Scientific Algorithm
    Discovery by Augmenting AlphaEvolve with Deep Research`, by Gang Liu,
    Yihan Zhu, Jie Chen, and Meng Jiang was submitted on October 7, 2025; the
    cached PDF hash is
    `e2f578c3b7979eb72857b1545b244405cf0fa8792bab82645e58c97cf3681f86`
    and the PDF metadata declares CC BY 4.0. It presents DeepEvolve as a
    workflow that combines algorithmic deep research with AlphaEvolve-style
    selection. It defines a plan/search/write/code/evaluation/
    evolutionary-selection loop, uses external online research to generate
    proposals with pseudo-code, implements them through cross-file code edits,
    performs automatic debugging from execution feedback, stores algorithms in
    an evolutionary database for next/inspiration sampling, and evaluates nine
    tasks spanning molecular prediction, molecular translation, circle packing,
    Burgers equation, Parkinson's disease, nuclei image segmentation, Open
    Vaccine, polymer prediction, and USP P2P. The public code URL is
    `https://github.com/liugangcode/deepevolve`.
  - Current gap: `papers/README.md` describes LibreEvolve's DeepResearch row as
    bounded retrieval context with cache/provenance surfaces, while explicitly
    excluding a DeepEvolve-style cross-file debugging/editing loop. Existing
    active TODOs focus on transport, replay, and source-integrity evidence, but
    do not preserve the full DeepEvolve PDF as a source-specific boundary with
    six-module workflow semantics, algorithm-description fields, cross-file
    coding, reflection, debugging counts, nine-task benchmarks, runtime
    budgets, execution-success ablations, qualitative idea scoring, or
    repository/source status.
  - Required result: add paper-manifest and paper-index coverage for
    `2510.06056`: title/authors/arXiv version/date/PDF digest, source/license
    status for `liugangcode/deepevolve`, task/input schema, textualization
    function, user-instruction fields, plan/search/write proposal artifacts,
    retrieved-source provenance, pseudo-code proposal schema, cross-file code
    delimiter/localization records, reflection and debugging policies, score-
    zero fallback semantics, evolutionary database and inspiration/MAP-Elites
    relation, Table 1 task/metric rows, Table 2 performance/runtime rows, Table
    3 debugging success-rate rows, Figure 3 originality/future-potential/
    difficulty judge records, deep-research ablation rows, 30-minute/single-GPU
    budget evidence, Table 4 ablation rows (`Molecule` best `0.797` without
    deep research vs `0.815` with deep research; `Circle Packing` `2.735` vs
    `2.981`), Appendix C user-query/hyperparameter rows, source/license
    metadata, and README/ROADMAP/code wording that keeps current DeepResearch
    retrieval context marked missing for DeepEvolve execution claims.

- [ ] Track MAP-Elites illumination-algorithm paper evidence as a source-
      specific boundary.
  - Paper/source evidence: local arXiv `1504.04909`, `Illuminating search
    spaces by mapping elites`, by Jean-Baptiste Mouret and Jeff Clune is a
    preliminary draft dated April 21, 2015; the local cache row points to
    `https://arxiv.org/pdf/1504.04909.pdf`, byte count `3221283`, and SHA-256
    `df7344343b14893a1d79a5459c1f56db50562e246d132cd0269f5201d1455872`.
    It introduces the Multi-dimensional Archive of Phenotypic Elites as an
    illumination algorithm. It searches a high-dimensional genotype/search
    space while filling a low-dimensional, user-chosen feature space with the
    best elite found per cell, using feature descriptors, performance scores,
    random initialization, mutation or crossover variation from existing elites,
    and per-cell replacement by local performance.
  - Current gap: `papers/README.md` lists `1504.04909` as foundational and
    describes LibreEvolve's current configurable 3D archive plus open stable
    descriptor/rebin/diagnostic gaps. Existing active paper TODOs discuss
    descriptor modeling generally, but none preserve the MAP-Elites PDF itself
    as a source-specific evidence boundary with the pseudocode variables,
    algorithm assumptions, feature-space discretization policy, illumination
    metrics, visualization outputs, lineage/stepping-stone analysis, benchmark
    domains, paper-draft caveat, or experiment-parameter schedules.
  - Required result: add paper-manifest and paper-index coverage for
    `1504.04909`: title/authors/date/PDF digest, preliminary-draft status,
    feature descriptor `b(x)`, performance function `f(x)`, map variables
    `P`/`X`, initialization count `G`, iteration budget `I`, random selection
    and variation policy, cell replacement condition, user-chosen dimension and
    discretization records, empty/unfillable cell notes, global performance,
    global reliability, precision, and coverage metric definitions, feature-
    performance visualization requirements, parent/lineage stepping-stone
    evidence, retina feature axes and resolution schedule, simulated soft-robot
    feature axes and resolution schedule, physical soft-arm MAP-Elites/grid-
    search/random-sampling evaluation counts, modular-neural-network and soft-
    robot benchmark context, relation to NS+LC/MOLE/novelty search/EA+D/grid
    search, and README/ROADMAP/code wording that keeps current local archive
    support distinct from full illumination-algorithm reproduction.

- [ ] Track hardness-of-approximation proof-element paper evidence as a
      source-specific boundary.
  - Paper/source evidence: local arXiv `2509.18057v7`, `Reinforced Generation
    of Combinatorial Structures: Hardness of Approximation`, by Ansh Nagda,
    Prabhakar Raghavan, and Abhradeep Thakurta was submitted as v7 on March 9,
    2026; the local cache row points to
    `https://arxiv.org/pdf/2509.18057.pdf`, byte count `7719868`, SHA-256
    `32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842`,
    and the PDF metadata declares CC BY 4.0. It reports AlphaEvolve-discovered
    finite proof elements for three complexity-theory settings: average-case
    certification lower bounds for random regular graph MAX-CUT/MAX-
    Independent-Set, gadget-based NP-hardness improvements for MAX-3-CUT and
    MAX-4-CUT, and metric-TSP hardness via a new equation gadget. It
    distinguishes proxy scores from theorem constants, uses evolved fast
    verifiers to search larger gadgets, and requires final brute-force
    verification plus human/proof arguments before theorem claims.
  - Current gap: the paper index labels `2509.18057` as AlphaEvolve
    complexity-theory result context and background-only, while an active
    theoretical-CS TODO asks for general source tracking. It does not preserve
    this PDF as a detailed source-specific boundary with arXiv versioning,
    result ids, graph/gadget artifact inventories, verifier-speedup evidence,
    correctness-check records, final brute-force verification, proof-lifting
    metadata, extracted-link/source-repository status, or claim boundaries
    between finite constructions and universal theorem statements.
  - Required result: add paper-manifest and paper-index coverage for
    `2509.18057`: title/authors/arXiv version/date/PDF digest, source/artifact
    availability and rights, result table for MAX-CUT, MAX-Independent-Set,
    MAX-k-CUT, and metric TSP, Table 1 LB/UB values, Ramanujan graph witness
    metadata for graphs up to 163 vertices, MAX-k-CUT gadget schemas and
    Appendix C edge lists, TSP equation-gadget schemas and Appendix D edge
    lists, verifier API and runtime records, synthetic correctness dataset
    provenance from 20 random MAX-k-CUT models, judge-LLM and human-inspection
    attribution, final brute-force verification outputs, theorem/lemma/proof
    appendix cross-links, baseline/SOTA comparison values, extracted links plus
    absence/presence of code-repository URLs, lifting-framework statements, and
    README/ROADMAP/code wording that keeps complexity-theory proof-element
    support missing unless those artifacts are locally represented and verified.
