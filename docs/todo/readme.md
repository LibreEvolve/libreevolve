# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

## Feature Claims

- [ ] Keep README evaluator-contract wording scoped to local validity gating
      until paper-facing scalar metric reports exist.
  - Spec evidence: AlphaEvolve Section 2.1 describes evaluator outputs as
    scalar metrics maximized by convention, and Figure 3 shows a Python
    evaluator returning `dict[str, float]`.
  - Current evidence: README correctly documents LibreEvolve's stricter local
    contract: `evaluate()` returns every declared scalar metric plus reserved
    boolean `is_valid`, while `outputs`/`program_output` carry non-scalar
    evidence separately. README also documents metric direction/bounds
    normalization for local archive scoring. It does not yet describe a
    benchmark/report contract that strips local control fields from
    paper-facing metric tables or shows minimize-to-maximize transforms.
  - Required result: when paper-facing evaluator metric reports land, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes the implemented LibreEvolve validity gate from
    AlphaEvolve-comparable scored scalar metrics.

- [ ] Keep README candidate-language wording scoped to the Python-primary
  boundary record versus real language/build runners.
  - Spec evidence: AlphaEvolve tasks can define program artifacts and
    evaluator interfaces over codebases and task-specific solution
    representations, so README wording should distinguish the current local
    Python-primary file-set boundary from full arbitrary-language or
    problem-defined candidate abstractions.
  - Current evidence: README documents that LibreEvolve evolves bounded UTF-8
    code file sets rather than arbitrary problem-defined solution objects,
    marks that as a deliberate current divergence from AlphaEvolve's flexible
    solution-abstraction API, records `policies.candidate_language` with schema
    `libreevolve.candidate_language_policy.v1`, and says that arbitrary
    language/build-system runner surfaces are unsupported. README also states
    that seed workspaces still require a Python primary compatibility file and
    that non-Python evolve-block marker syntaxes are rejected with
    `unsupported_evolve_block_marker_syntax` instead of being treated as
    language-aware skeleton regions.
  - Required result: when configured language runners, build-system runner
    contracts, language-aware evolve-block grammars, or problem-defined
    candidate-abstraction hooks land, update README, ROADMAP, papers index,
    and code/paper TODO entries together so README neither underclaims the
    current manifest-visible boundary policy nor overclaims AlphaEvolve-grade
    arbitrary-language/codebase support.

- [ ] Keep README candidate-abstraction wording scoped to current divergence
      until abstraction-choice evidence exists.
  - Spec evidence: AlphaEvolve Section 2.1 and Discussion say users can choose
    different candidate abstractions for the same problem, and those choices
    carry biases: constructor functions can favor highly symmetric solutions,
    while customized search algorithms may work better for non-symmetric
    solutions.
  - Current evidence: README says LibreEvolve currently uses a deliberate
    code-file-set abstraction with a primary text file and lacks first-class
    non-code serializers or paired solution/search APIs. It does not describe
    benchmark metadata that records why one abstraction was selected, whether
    the problem is symmetric/non-symmetric, or how alternative abstractions
    performed under comparable budgets.
  - Required result: when abstraction-choice metadata, benchmark rationale,
    problem-structure labels, paired solution/search APIs, or equal-budget
    abstraction-comparison reports land, update README, ROADMAP, papers index,
    and code/paper TODOs so README distinguishes a documented divergence from
    AlphaEvolve-style abstraction-selection evidence.

- [ ] Keep README seed-provenance wording scoped to source identity until
      initial-program idea provenance exists.
  - Spec evidence: AlphaEvolve Section 2.1 makes the initial solution and
    optional background knowledge part of the task specification, and Section
    3.1 reports matrix targets where researchers seeded the initial program
    with their own ideas, such as stochastic evaluation or evolutionary
    approaches.
  - Current evidence: README documents seed source safety and provenance,
    including `seed_source_path`, `seed_source_kind`, `seed_index`,
    `problem.seed_sources`, skipped-seed diagnostics, inline seed labels, and
    generation-0 baselines. It does not document benchmark metadata that
    classifies initial programs by idea origin, records injected human or
    prior-art ideas, or compares simple/random and idea-seeded starts under a
    benchmark report.
  - Required result: when benchmark seed idea-origin metadata and seed-variant
    result evidence land, update README, ROADMAP, papers index, and code/paper
    TODO entries together so README does not imply source-path provenance is
    sufficient for AlphaEvolve-style human-seeded collaboration claims.

- [ ] Keep README seed-validity wording scoped to permissive examples versus
      AlphaEvolve-strict complete starts.
  - Spec evidence: AlphaEvolve Section 2.1 describes the initial implementation
    as complete but rudimentary, with the task skeleton and evaluator able to
    invoke it before evolution.
  - Current evidence: README documents valid/suboptimal seeds and deliberately
    invalid optimization-pressure seeds, including `hello_world`, and states
    that runs can record invalid seed baselines. That is useful prototype
    behavior, but it is not the same as a strict AlphaEvolve initial-program
    contract where every selected seed is complete, runnable, and validator
    valid before mutation begins.
  - Required result: when strict seed-validity policy/reporting lands, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes permissive invalid seed baselines from benchmark claims that
    require complete AlphaEvolve-style initial implementations.

- [ ] Keep README problem-formulation wording scoped until expert provenance
      exists.
  - Spec evidence: AlphaEvolve Section 3.2 reports that many mathematical
    problems were suggested by external mathematicians who advised on how to
    formulate them as AlphaEvolve inputs, while Section 2.1 treats task
    definition and optional background knowledge as human-provided setup.
  - Current evidence: README documents problem/source provenance, context file
    selection, local paper context, and seed source identity. It does not yet
    document benchmark metadata for expert contributor roles, problem-origin
    records, formulation advice, evaluator/objective rationale, or parameter
    scope decisions.
  - Required result: when expert formulation provenance and validation lands,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README distinguishes context-source artifact tracking from
    AlphaEvolve-style human expert problem-formulation evidence.

- [ ] Keep README workspace-topology diagnostics scoped to current
  materialization and command preflight coverage.
  - Spec evidence: AlphaEvolve-style codebase evolution should leave stable,
    inspectable evaluator feedback for generated invalid artifacts, especially
    as task-defined program artifacts and workspace surfaces grow beyond the
    current local file-set prototype.
  - Current evidence: README documents that collision checks are still
    incomplete while also describing rejected normalized path collisions,
    case-folded host-path materialization preflights, structured
    `materialization_error` evaluation results, bounded redacted diagnostics,
    structured materialization `reason` and `paths`, exact snapshot
    materialization, link/junction rejection, static source-copy verification,
    and workspace topology command prevalidation for duplicate sources/targets,
    edit/delete/move conflicts, chained operations, host/case-folded target
    collisions, duplicate `PRIMARY` commands, and non-empty command bodies.
  - Required result: when future topology surfaces such as bulk directory
    operations, language/build-runner generated artifacts, external
    materialization paths, or richer artifact runners land, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    neither underclaims current structured invalid-workspace feedback nor
    overclaims robust AlphaEvolve-grade codebase-scale diagnostics.

- [ ] Keep README install and CLI wording scoped to editable/local use versus
  release-artifact verification.
  - Spec evidence: AlphaEvolve-style experimental artifacts should be
    reproducible from the code and dependency environment that users actually
    install before running long experiments; local editable setup is not the
    same as a checked release distribution.
  - Current evidence: README currently instructs developers to run
    `py -3.12 -m pip install -e ".[dev]"`, invokes the CLI through
    `py -3.12 -m libreevolve ...`, documents the `libreevolve run` and
    `libreevolve show` command shapes, and documents runtime environment
    provenance over `pyproject.toml`, installed package metadata, bounded
    `WHEEL` metadata, `direct_url.json`, `INSTALLER`, hash-only `RECORD`,
    `pip freeze`, and `pip config`. Code evidence shows `pyproject.toml`
    declares setuptools metadata, runtime dependencies, dev extras, package
    discovery, and a `libreevolve` console script, while the code TODO still
    notes there is no committed wheel/sdist build check, install-from-wheel CLI
    smoke test, package-data inclusion validation, release checklist, or
    release-artifact provenance.
  - Required result: when wheel/sdist build validation, isolated
    install-from-wheel smoke tests, package-data checks, release checklists, or
    release-artifact provenance land, update README, ROADMAP, papers index, and
    code TODO entries together so README neither underclaims current
    editable/local CLI use nor overclaims verified release-distribution
    reproducibility.

- [ ] Keep README `show` and run-inspection wording scoped to selected-row
  display plus streamed-row validation.
  - Spec evidence: AlphaEvolve-scale runs need auditable generated-program
    databases and whole-run source/workspace integrity reports, not only a
    compact best-candidate view.
  - Current evidence: README documents `show` as a compact history view that
    selects the best archive-retained valid record, prints selected-row
    metrics, archive diagnostics, bounded run-inspection summaries, and
    selected-row workspace files, and validates streamed current and legacy
    history rows before printing. It also states that malformed unselected,
    invalid, or non-admitted rows fail inspection before any best-looking row
    is printed, with source/workspace paths, `files`, and `primary_file`
    checked under the runtime candidate path grammar. The paper TODO still
    requires whole-run source/workspace integrity summaries and durable
    query/report surfaces over every candidate's source payloads, workspace
    paths, source hashes, primary-file coherence, and display/truncation
    policy.
  - Required result: when whole-run source/workspace integrity reports, durable
    run-artifact query views, richer archive/prompt/failure drill-downs, or
    every-candidate source-hash summaries land, update README, ROADMAP, papers
    index, and code/paper TODO entries together so README neither underclaims
    current streamed-row validation nor overclaims AlphaEvolve-grade run
    inspection.

- [ ] Keep README provider-token prompt-packing wording scoped to implemented
  mutation and final-prompt boundaries.
  - Spec evidence: AlphaEvolve-scale prompt construction needs prompt sections
    and context surfaces to fit model-specific context windows without
    silently dropping important evaluator, parent, inspiration, or retrieval
    evidence.
  - Current evidence: README now distinguishes implemented backend
    context-window heuristic capacity, automatic mutation-path local OpenAI
    tokenizer discovery, and role-scoped final-prompt exact token counting
    from the still-open provider-token section-priority packing outside
    mutation prompts and exact counters across non-OpenAI provider families.
    Code evidence includes `core.loop.discover_prompt_token_counter(...)`
    before `PromptSampler` construction, `LLMEnsemble._prompt_token_counter_for_role(...)`
    before final prompt validation, and tests covering mutation diagnostics and
    critique-role final-prompt counter telemetry.
  - Required result: when selected-backend provider-token section packing
    covers critique, feedback, meta-prompt, registry-created, custom, and
    retrieval/context/plugin/failure-memory sections across provider families,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README neither underclaims automatic OpenAI counter discovery nor
    overclaims full AlphaEvolve-grade context-window fitting.

- [ ] Keep README ablation-report wording aligned with current LLM budget
  stops.
  - Spec evidence: AlphaEvolve Figure 8 compares executed equal-budget
    ablation curves; report-schema validation alone is not executed
    budget-controlled experimentation, but README text should not deny budget
    stops that now exist.
  - Current evidence: README now says
    `libreevolve.alphaevolve_ablation_report.v1` validates report shape only
    and does not run ablation experiments or add accelerator/async-worker
    budget stops beyond the current live provider-token and configured-cost LLM
    budget surfaces. Code evidence includes `RunBudget.max_llm_tokens`,
    `RunBudget.max_llm_cost_microusd`, role-scoped token/cost limits, and
    controller-budget event replay into restored budget snapshots. The
    checked-in Figure 8 registry is still `definition_only` and should keep
    the full-system baseline distinct from the five component-disabled
    ablations; several
    `required_config_assertions` are intended component labels rather than
    current executable config switches, including `candidate_source`,
    `archive_admission_enabled`, `prompt_context_sections`,
    `candidate_workspace_mode`, `file_create_delete_enabled`,
    `ensemble_strategy: single_backend`, and `backend_capability_tier`. The
    registry also does not yet prove the `No evolution` setup where every
    prompt is built from the same initial program without database-selected
    parents, inspirations, previous-candidate feedback, or archive admission
    feedback. It also does not yet prove the `No context in the prompt` setup
    where prompt-visible explicit context, sampled prior-program/inspiration
    context, recent failure feedback, and plugin context are actually absent in
    executed prompt history. It also does not yet prove the
    `Small base LLM only` setup where every mutation-generation call uses only
    one configured small/base-capable model and has no large-model eligibility,
    fallback, critique, or router leakage. It also does not yet prove the
    `No meta prompt evolution` setup where meta-prompt calls, prompt-template
    mutations, and prompt-program lineage updates are absent in the ablated run
    but enabled in the full-system comparator. It also does not yet prove the
    paper-specific `No full-file evolution` setup where only the tensor
    decomposition loss function is evolved; generic single-file/diff/no-topology
    labels should not be described as equivalent to that ablation.
    The report contract is also target-family generic: it validates declared
    targets but not Figure 8's matrix tensor-decomposition and kissing-number
    sphere-packing families, and it does not require per-target
    target-metric identity/direction/normalization or mean/standard-deviation
    curve summaries over three independent seeds.
  - Required result: when benchmark scripts emit executed equal-budget
    ablation reports, when component assertions are bound to supported runtime
    config controls, or when accelerator/async-worker budgets land, update
    README, ROADMAP, papers index, and code/paper TODO entries together so the
    README neither underclaims current token/configured-cost budget stops nor
    overclaims AlphaEvolve-style executed ablations. For `No full-file
    evolution`, require README wording to distinguish a real loss-function-only
    tensor-decomposition harness from broader localized-edit settings. Require
    README wording to distinguish `No evolution` registry labels from executed
    evidence that the same initial program was repeatedly prompted without
    evolutionary database feedback. Require
    README wording to distinguish `No context in the prompt` registry labels
    from executed prompt-history evidence that context sources and feedback
    sections were absent. Require README wording to distinguish generic
    `Small base LLM only` labels from executed backend telemetry proving a
    single small/base model actually handled every relevant generation call.
    Require README wording to distinguish generic
    `No meta prompt evolution` labels from executed prompt-history and
    call-ledger evidence that meta-prompt and prompt-mutation surfaces were
    disabled only for that ablation. Require README wording to distinguish
    generic
    ablation-result schemas from
    Figure 8-equivalent matrix/kissing target-family reports with validated
    target-metric identity/direction/normalization and mean/standard-deviation
    curves.

- [ ] Keep README matrix-publication wording scoped to one checked Strassen
  baseline versus full Appendix A discovery.
  - Spec evidence: AlphaEvolve Appendix A reports a matrix-multiplication
    target suite with discovered algorithms, exact constructions, and
    accompanying export/notebook artifacts; a single checked baseline bundle is
    not evidence that LibreEvolve discovered or exported the full suite.
  - Current evidence: README now says
    `write_strassen_2x2_publication_bundle()` emits a concrete checked
    Strassen bundle for registered `mm_2x2x2` with canonical algorithm,
    certificate, notebook, report, and artifact-inventory files, while also
    stating that this is a reproducible baseline artifact and not evidence that
    LibreEvolve discovered or exported the full Appendix A target suite. The
    54-target Appendix A registry is rank/outcome metadata, not stored target
    tensors, discovered decompositions, coefficient lists, per-target
    certificates, notebook exports, or construction provenance.
    Matching paper TODO and paper-index entries now make the same distinction.
  - Required result: when real tensor-decomposition benchmark runs emit
    target tensors, discovered algorithms, coefficient data, certificates,
    notebooks, or publication bundles across Appendix A targets, update
    README, ROADMAP, papers index, and code/paper TODO entries together so
    README neither underclaims the checked Strassen baseline nor overclaims
    AlphaEvolve-comparable discovery coverage.

- [ ] Keep README matrix-scaling wording scoped until resource-frontier
      reports exist.
  - Spec evidence: AlphaEvolve Appendix A notes that runs on matrix sizes
    beyond the reported suite often ran out of memory with 1000 random seeds
    on a single GPU accelerator, and that larger-size extension needs further
    optimization.
  - Current evidence: README documents matrix report contracts, Appendix A
    registry checks, one checked Strassen baseline bundle, generic runtime
    budget surfaces, and unsupported resource quotas. It does not document
    matrix-specific scaling attempts, accelerator-memory profiles,
    OOM/resource-exhaustion diagnostics, or target-exclusion rationale for
    sizes beyond the reported suite.
  - Required result: when matrix resource-frontier reports land, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes generic budget/resource metadata from AlphaEvolve Appendix
    A-style evidence about larger matrix target scaling limits.

- [ ] Keep README matrix wording scoped to result contracts until
      near-integrality prompt/evaluator evidence exists.
  - Spec evidence: AlphaEvolve Section 3.1 says the matrix prompt requested
    near-integral solutions and the reported decompositions were rounded to
    the nearest integer or half-integer before exactness verification.
  - Current evidence: README describes the matrix-result report contract,
    Appendix A registry, and checked Strassen baseline bundle, including
    coefficient-domain and exactness restrictions for AlphaEvolve-comparable
    reports. It does not yet document a matrix benchmark prompt/evaluator path
    that injects the near-integrality instruction, records raw-versus-rounded
    coefficient diagnostics, or links those diagnostics to per-seed exactness
    certificates produced during search.
  - Required result: when that benchmark prompt/evaluator evidence lands,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README distinguishes report-schema validation from AlphaEvolve Section
    3.1 search-workflow parity.

- [ ] Keep README matrix wording scoped to final artifacts until sweep-space
      provenance exists.
  - Spec evidence: AlphaEvolve Figures 9a-9c show the 4x4 matrix program
    evolving a `sweep()` function that declares user-provided `hyper` ranges
    for optimizer, noise, clipping, discretization, and related search
    parameters.
  - Current evidence: README documents matrix result reports, Appendix A
    registry checks, the checked Strassen baseline bundle, and open
    near-integrality/scalar-field gaps. It does not yet document a matrix
    benchmark path that preserves candidate-produced sweep spaces, sampled
    configuration ids, per-sweep outcomes, or linkage from the selected sweep
    configuration to the final exact decomposition certificate.
  - Required result: when sweep-space provenance lands, update README,
    ROADMAP, papers index, and matching TODOs so README does not imply final
    matrix artifacts alone prove AlphaEvolve Figure 4/Figure 9 search-program
    parity.

- [ ] Keep README matrix wording scoped to coefficient-domain validation until
      scalar-field evidence exists.
  - Spec evidence: AlphaEvolve Table 2 notes that some improved matrix
    algorithms use complex-valued multiplications and can be used for exact
    multiplication of complex or real-valued matrices, while Section 3.1
    contrasts characteristic-0 and finite-field-only results.
  - Current evidence: README describes matrix-result fields for coefficient
    domain and exactness, plus Appendix A target identity and checked Strassen
    baseline artifacts. It does not yet document scalar-field metadata,
    exact complex coefficient representation, characteristic/applicability
    claims, or certificate scope for real-versus-complex multiplication.
  - Required result: when matrix reports and certificates record scalar field,
    complex coefficient data, characteristic, and applicability evidence,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README does not imply coefficient-domain validation is sufficient for
    AlphaEvolve-style complex-valued matrix result claims.

- [ ] Keep README certification and systems-result wording scoped to report
  contracts versus executed independent evidence.
  - Spec evidence: AlphaEvolve Section 3.3 reports confirmation beyond local
    optimizer feedback, including post-deployment fleet measurements, held-out
    kernel-shape evaluation, randomized reference-code checks, and human expert
    confirmation for final FlashAttention changes.
  - Current evidence: README now says
    `libreevolve.paper_result_certification.v1` distinguishes local validator
    records from paper-claim-ready independent certifications, and that the
    accompanying artifact inventory proves named evidence files are present,
    not that independent verifiers, deployment measurements, or human review
    have been performed. README also says
    `libreevolve.systems_result_report.v1` is a readiness/report schema only,
    while `libreevolve.systems_result_artifact_inventory.v1` proves artifact
    availability, not unseen workloads, reference-code checks, deployment
    evidence, or independent certification. Matching paper/code TODOs still
    require real verifier scripts, reviewer/deployment provenance, systems
    fixtures, held-out case sets, randomized/reference-correctness checks, and
    domain-specific rules for when a held-out or reference-correctness gate may
    be marked `not_applicable`.
  - Required result: when benchmark runs emit real certification reports,
    deployment/reviewer evidence, held-out systems reports, or reference-code
    checks, and when systems reports enforce domain-specific readiness gates,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so README neither underclaims the current report and inventory contracts
    nor overclaims AlphaEvolve-style confirmed result evidence.

- [ ] Keep README scheduling wording scoped to generic systems reports until
      ranking-only safety provenance exists.
  - Spec evidence: AlphaEvolve Section 3.3.1 says the Borg scheduling
    heuristic scores only machines already determined by Borg to be available
    and capable of running the pending job, so correctness is effectively by
    construction.
  - Current evidence: README documents systems result reports and artifact
    inventories, and notes that deployment evidence and domain-specific
    readiness gates remain open. It does not yet document scheduling-specific
    evidence that a heuristic only reorders feasible machines, preserves
    resource/capacity constraints, and cannot directly admit, reject, or place
    jobs outside the scheduler's feasibility boundary.
  - Required result: once scheduling report metadata captures feasibility
    filter provenance, ranking-only scope, resource invariants, and
    simulator/admission-boundary evidence, update README, ROADMAP, papers
    index, and matching TODOs so README does not imply generic systems report
    readiness proves Borg-style scheduling safety.

- [ ] Keep README scheduling wording scoped to generic systems reports until
      interpretability/deployment-readiness evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.1 says the Borg scheduling
    heuristic was chosen over deep reinforcement learning because the code
    solution offered interpretability, debuggability, predictability, and ease
    of deployment, which were essential for a mission-critical system.
  - Current evidence: README documents generic systems result reports,
    deployment evidence gaps, and scheduling ranking-only safety gaps. It does
    not yet document scheduling-specific evidence for human-readable heuristic
    structure, operator/debug review, predictable behavior under edge cases,
    deployment-risk controls, or comparison against less interpretable learned
    policies.
  - Required result: once scheduling report metadata captures
    interpretability/debuggability review, predictability checks, deployment
    ergonomics, rollout-risk evidence, and baseline comparison against
    black-box approaches, update README, ROADMAP, papers index, and matching
    TODOs so README does not imply generic systems report readiness proves
    AlphaEvolve-style mission-critical deployment suitability.

- [ ] Keep README kernel wording scoped to generic systems reports until
      Pallas shape-split/runtime evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.2 optimizes Gemini Pallas
    matrix-multiplication tiling heuristics on real TPU accelerators, using
    realistic user-collected input shapes split into training and evaluation
    halves, with correctness preserved by changing tiling strategy rather than
    the underlying operation.
  - Current evidence: README documents generic systems result reports and
    held-out/reference gates, but it does not yet document kernel-specific
    shape-corpus provenance, train/eval split hashes, accelerator runtime
    artifacts, expert-baseline heuristic identity, tiling-only output
    constraints, or correctness-by-construction scope.
  - Required result: once kernel report metadata captures shape-corpus,
    train/eval split, TPU runtime, expert-baseline comparison, tiling
    constraints, and unchanged-operation evidence, update README, ROADMAP,
    papers index, and matching TODOs so README does not imply generic systems
    report readiness proves AlphaEvolve-style Pallas kernel optimization.

- [ ] Keep README hardware wording scoped to generic systems reports until
      RTL/EDA verification evidence exists.
  - Spec evidence: AlphaEvolve Section 3.3.3 optimizes Verilog RTL for a TPU
    arithmetic circuit, tracks power/area objectives, requires robust
    functional verification, and reports TPU-designer plus downstream
    synthesis-tool confirmation.
  - Current evidence: README documents systems result reports and artifact
    inventories as generic readiness/report contracts. It does not yet
    document hardware-specific evidence for HDL source boundaries,
    synthesis/PPA metrics, equivalence or formal verification, timing/power/
    area constraints, designer signoff, or downstream synthesis confirmation.
  - Required result: when RTL/EDA report metadata and validators land, update
    README, ROADMAP, papers index, and matching TODOs so README does not imply
    generic systems report readiness proves AlphaEvolve-style TPU-circuit
    optimization evidence.

- [ ] Keep README compiler-IR wording scoped to final reference gates until
      per-edit randomized checks exist.
  - Spec evidence: AlphaEvolve Section 3.3.4 checked each FlashAttention
    compiler-IR modification against reference code on randomized inputs and
    then separately had the final code confirmed by human experts for all
    possible inputs.
  - Current evidence: README documents generic systems result reports and
    reference-correctness gates, but it does not yet describe per-edit
    randomized reference-check traces, reference implementation hashes,
    randomized input generator provenance, numerical tolerance policy, or
    kernel-versus-pre/postprocessing attribution.
  - Required result: once compiler/kernel report metadata captures per-edit
    reference checks, randomized input coverage, tolerance/failure policy,
    abstraction-level attribution, and final expert signoff scope, update
    README, ROADMAP, papers index, and matching TODOs so README does not imply
    final reference-gate artifacts prove AlphaEvolve-style compiler-IR traces.

- [ ] Keep README benchmark-hardening wording scoped to smoke evidence versus
  benchmark-grade anti-gaming fixtures.
  - Spec evidence: AlphaEvolve-comparable benchmark claims require robust target
    suites whose reported improvements cannot be explained by hardcoded cases,
    shortcut access to reference answers, artifact spoofing, or local smoke
    validator quirks.
  - Current evidence: README now says
    `libreevolve.benchmark_hardening.v1` validates protected signals, shortcut
    threats, detector strategy, negative fixtures, and hashed hardening
    artifacts; it also says the artifact inventory proves named anti-gaming
    evidence files exist, not that a real benchmark runner generated them.
    Matching roadmap/paper/code TODOs distinguish the checked matrix smoke
    hardening bundle, which preserves `alphaevolve_comparable: false`, from
    still-missing benchmark-grade tensor/geometric/compiler/systems fixtures
    with real randomized or exhaustive anti-gaming evidence. Matching paper and
    code TODOs also mark the Appendix B registry as a family/status ledger:
    paper-result families still have null target-baseline values, and
    construction/certificate artifact-schema strings are not executable
    validators, reported constructions, SOTA thresholds, or verifier scripts.
    AlphaEvolve Appendix B says the reported construction data and verification
    code are available in an accompanying Google Colab; README should not imply
    the registry has that Colab-equivalent verifier-data surface yet.
  - Required result: when real target-family benchmark runners emit
    benchmark-grade hardening reports, negative fixtures, detector logs, and
    artifact inventories, and when Appendix B families gain executable
    construction/certificate validators, target baselines, construction-data
    exports, and verifier-code artifacts, update README, ROADMAP, papers index,
    and code/paper TODO entries together so README neither underclaims the
    checked smoke hardening evidence nor overclaims AlphaEvolve-comparable
    benchmark hardening.

- [ ] Keep README constructive-math wording scoped to static context/artifacts
      versus AlphaEvolve-style incumbent handoff.
  - Spec evidence: AlphaEvolve Section 3.2 evolved heuristic search programs
    that use a fixed budget and a strong previously discovered construction as
    input, then return an improved construction for verification.
  - Current evidence: README can accurately describe workspace seeds, static
    context, evaluator artifacts, Appendix B coverage/status records, and
    smoke examples. It should not imply current constructive-math support
    includes a benchmark runner that passes incumbent constructions to
    candidate heuristics, records the fixed search budget, or verifies
    candidate-produced construction improvements as a Section 3.2-style loop.
  - Required result: when real heuristic-search handoff support lands, update
    README, ROADMAP, papers index, and code/paper TODO entries together so
    README distinguishes static problem context and post-run artifacts from
    first-class incumbent-construction benchmark handoff evidence.

- [ ] Keep README constructive-math coverage wording scoped to Appendix B
      family status until aggregate outcome reports exist.
  - Spec evidence: AlphaEvolve Section 3.2 reports over 50 mathematical
    problems across more than five branches, with roughly 75% matching best
    known constructions and roughly 20% improving SOTA.
  - Current evidence: README describes the Appendix B registry as thirteen
    constructive-math families with one smoke fixture and planned entries for
    the rest. That is a family/status and expected-artifact ledger, not a
    per-problem/per-parameter outcome report with branch taxonomy, previous
    best references, construction links, and matched/improved aggregate
    percentages.
  - Required result: when constructive-math outcome reports land, update
    README, ROADMAP, papers index, and code/paper TODOs together so README
    distinguishes Appendix B family coverage from AlphaEvolve-style aggregate
    mathematical breadth and SOTA-rate claims.

- [ ] Keep README feedback-calibration wording scoped to report contracts
  versus executed calibration experiments.
  - Spec evidence: AlphaEvolve-style feedback and reviewer channels need
    calibrated evidence from real reviewer/task suites and ablations, not only
    validators for declared calibration records.
  - Current evidence: README now says
    `libreevolve.llm_feedback_calibration.v1` validates declared graders,
    at least two calibrated tasks for readiness, per-grader/task scored
    records, normalized expected/observed scores, exact absolute-error
    consistency, and declared calibration artifacts. It also says the
    artifact-inventory contract verifies calibration report, raw-record,
    grader-config, and plot artifacts under a safe root, and that the current
    code does not run feedback-grader calibration experiments. Matching
    roadmap/paper/code TODOs still require real feedback-calibration fixtures
    and grader ablation reports.
  - Required result: when runtime fixtures or benchmark scripts emit real
    feedback-calibration reports, reviewer/task suites, or grader ablation
    evidence, update README, ROADMAP, papers index, and code/paper TODO entries
    together so README neither underclaims the report and inventory contracts
    nor overclaims executed AlphaEvolve-style calibration evidence.

- [ ] Keep README provider-cancellation wording scoped to timeout policy and
  observation evidence versus live hard cancellation.
  - Spec evidence: AlphaEvolve-scale runs need bounded provider latency,
    attributable stop behavior, and cancellation semantics that prevent stalled
    model calls from blocking long budgeted experiments.
  - Current evidence: README now says
    `libreevolve.provider_cancellation_policy.v1` validates provider
    request-timeout, ensemble-deadline, runtime-deadline, and hard-cancel
    policy rules by role, including artifact requirements and hard-cancel
    readiness gated on cancellation-record evidence. It also says runtime
    manifests currently scope provider timeout/deadline rules to active LLM
    role surfaces and attach scheduler-derived timeout/quarantine observations,
    but that this is policy and observation evidence only. The README further
    says provider SDK hard cancellation and timeout-driven stop enforcement
    remain runtime work, and that artifact inventory proves named cancellation
    evidence files exist rather than proving in-flight SDK calls can be
    hard-cancelled.
  - Required result: when live provider SDK cancellation, timeout-driven
    stop-run behavior, richer timeout/cancellation artifacts, or cross-run
    quarantine/resume proof lands, update README, ROADMAP, papers index, and
    code/paper TODO entries together so README neither underclaims current
    timeout-policy evidence nor overclaims AlphaEvolve-style hard cancellation.

- [ ] Keep README validator sandbox/resource-limit wording scoped to local
  subprocess audit evidence versus OS/container enforcement.
  - Spec evidence: AlphaEvolve-scale systems and codebase experiments need
    trustworthy execution isolation, filesystem capability boundaries, network
    egress control, and resource quotas when evaluating generated code.
  - Current evidence: README now says validator execution records expose
    `libreevolve.validator_execution_policy.v1`,
    `evaluation.metadata.validator_boundary`, `filesystem_capabilities`, and
    `resource_limit_policy` with local-subprocess execution,
    `security_sandbox: "unsupported"`, `container: "unsupported"`, Python
    socket-denial metadata when configured, wall-clock-only timeout policy,
    unsupported CPU/memory/GPU/disk/process-count quotas, and a
    minimal-environment/redacted-diagnostic secret boundary. The README also
    says the filesystem and resource records are audit evidence for the current
    local runner, not an OS/container security sandbox. Matching code/paper
    TODOs still require configurable sandbox/container enforcement,
    OS/container-grade network egress isolation, OS-enforced filesystem
    capability policy, CPU/memory/GPU/disk/process quotas, and distributed
    evaluator worker state.
  - Required result: when real sandbox/container, filesystem capability,
    network isolation, or resource-quota enforcement lands, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    neither underclaims the current manifest-visible boundary audit nor
    overclaims AlphaEvolve-grade execution isolation.

- [ ] Keep README and agent-facing OpenAI API-mode wording aligned with adapter
  routing.
  - Spec evidence: AlphaEvolve-style runs should make provider request
    surfaces explicit enough for reproducibility; local docs should not imply a
    different API route than the configured adapter will use.
  - Current evidence: README correctly states that OpenAI defaults to Chat
    Completions and uses Responses API when `api_mode: responses` or
    `reasoning_effort` is configured. `OpenAIBackend` resolves explicit
    `api_mode: responses` without reasoning into Responses mode, while
    `api_mode: auto` without reasoning preserves Chat Completions. `AGENTS.md`
    has been updated to match that boundary.
  - Required result: when OpenAI API-mode routing, supported request
    parameters, or static compatibility checks change, update README,
    `AGENTS.md`, code TODOs, and paper TODOs together so docs neither
    underclaim explicit Responses support nor overclaim live provider
    capability discovery.

- [ ] Keep README provider capability lookup wording scoped to static local
  validation versus live model-registry evidence.
  - Spec evidence: AlphaEvolve-scale model orchestration should preserve enough
    provider/account capability evidence to explain which backend model ids and
    API modes were available for a run, especially as provider registries,
    service API versions, and account entitlements change.
  - Current evidence: README says LibreEvolve forwards configured model strings
    to provider SDKs, validates only manifest-safe identifier syntax/secret
    shape, records `policies.provider_capability_lookup`, and performs no live
    model-registry, service/API-version, or account-availability lookup before
    the run. Code and paper TODO entries already scope the remaining provider
    auth gap to live authenticated request/model-registry validation rather
    than credential-presence and local client-construction preflight.
  - Required result: when live provider model-registry discovery,
    service/API-version capture, account-availability validation, or provider
    capability evidence lands, update README, ROADMAP, papers index, and
    code/paper TODO entries together so README neither underclaims the current
    static manifest policy nor overclaims AlphaEvolve-grade provider
    reproducibility evidence.

- [ ] Keep README paper-inspired plugin claims scoped to approximation status.
  - Spec evidence: citing CausalEvolve, DeepEvolve, ImprovEvolve,
    ThetaEvolve, GigaEvo, CodeEvolve, or MadEvolve should not imply faithful
    reproduction unless paper-specific behavior is implemented.
  - Current evidence: README says built-in plugins are paper-inspired
    approximations, not full reproductions; it labels CausalEvolve as
    token-pattern outcome-factor guidance, DeepEvolve as pluggable
    arXiv/web-search context, ImprovEvolve as modular decomposition prompting,
    and ThetaEvolve as clipped-reward JSONL export, not training. The README
    paper table also marks GigaEvo and CodeEvolve as inspiration only and
    MadEvolve as background context.
  - Required result: when paper-specific plugin/framework behavior lands,
    update README, ROADMAP, papers index, code TODO, and paper TODO entries
    together so the README neither underclaims current approximation metadata
    nor overclaims faithful paper implementations.

- [ ] Keep README custom-plugin provenance claims scoped to entry-point specs
  versus direct instances.
  - Spec evidence: AlphaEvolve-grade plugin extensibility should make custom
    hook code and configuration reproducible without hiding arbitrary
    constructor state.
  - Current evidence: README now documents entry-point plugin specs with
    manifest-safe or declared-schema constructor options, paper-inspiration
    labels, distribution name/version and hash metadata, while direct custom
    plugin instances record constructor signature shape only and explicitly
    exclude constructor values and instance attributes.
  - Required result: once direct custom plugin registries, safe constructor
    value/schema attribution, or richer package provenance land, update README
    and matching code/paper TODO entries so the README neither underclaims
    entry-point provenance nor overclaims direct-instance replayability.

- [ ] Keep README proposal-memory claims scoped to bounded hypothesis indexes.
  - Spec evidence: AlphaEvolve-style evolutionary memory should be able to
    reuse prior proposal ideas, rationales, and hypotheses through scored and
    semantically searchable idea memory.
  - Current evidence: README now documents `runtime.history.hypothesis_index`
    as bounded redacted proposal `idea`/`rationale`/`hypothesis` summaries for
    valid programs that can feed current-run `resurfacing_index`, while noting
    that proposal scoring, semantic proposal retrieval, and persisted cross-run
    hypothesis tables remain open.
  - Required result: once proposal scoring, semantic/cross-run proposal
    indexes, or stricter proposal-field influence policy lands, update the
    README and matching code/paper TODO entries together so the README neither
    underclaims current proposal metadata capture nor overclaims
    AlphaEvolve-grade idea memory.

- [ ] Keep README scientific-discovery wording scoped to automated evaluators
      versus manual-experiment and LLM-only idea-review workflows.
  - Spec evidence: AlphaEvolve states that automated evaluation is a core
    advantage and limitation: tasks requiring manual experimentation are out
    of scope, and LLM-provided evaluation of ideas is possible but not the
    optimized setting. The paper's future bridge is high-level idea feedback
    before transitioning to an implementation stage with machine feedback
    through code execution.
  - Current evidence: README describes automated algorithm discovery, local
    subprocess evaluators, staged validator cascades, optional LLM feedback,
    and proposal metadata, but it does not yet state a clear AlphaEvolve scope
    boundary for machine-gradeable tasks versus manual-experiment scientific
    workflows or pre-code LLM-only idea review.
  - Required result: once scope metadata/reporting exists, update README,
    ROADMAP, papers index, and matching TODOs so public wording neither
    underclaims the current executable-evaluator workflow nor overclaims
    manual-experiment or AI-Co-Scientist-style idea-feedback support.

- [ ] Keep README cascade wording scoped to staged threshold gates until
      statistical hypothesis-test promotion is implemented.
  - Spec evidence: AlphaEvolve Section 2.4 presents evaluation cascades as
    hypothesis testing: candidates are tried on small-scale tests before main
    test cases, and only sufficiently promising candidates advance. Section
    3.1 uses multiple randomized initializations for matrix tensor targets.
  - Current evidence: README describes cascade evaluation, staged validators,
    samples, retries, thresholds, stage/sample budgets, and prompt-visible
    diagnostics. It does not yet document a statistical cascade policy with
    confidence intervals, p-values, sequential stopping, false-promotion/
    false-rejection budgets, or explicit small-scale/main-test stage roles.
  - Required result: when statistical cascade promotion reports and validation
    land, update README, ROADMAP, papers index, and code/paper TODOs so README
    distinguishes current deterministic staged threshold gates from
    AlphaEvolve-style hypothesis-testing cascades.

- [ ] Keep README mutation-response wording scoped to structured proposal
      metadata versus natural-language preambles.
  - Spec evidence: AlphaEvolve Figure 3(c) shows explanatory natural-language
    text before a SEARCH/REPLACE diff example.
  - Current evidence: README accurately says text outside mutation payload
    sections must be proposal metadata; code accepts bounded structured fields
    and rejects ordinary prose around valid diff/block/workspace-file sections.
  - Required result: if LibreEvolve later accepts explanatory preambles, update
    README, ROADMAP, papers index, and code/paper TODOs with the exact parser
    boundary, redaction/provenance behavior, and distinction between safe
    proposal metadata and arbitrary unparsed prose.

- [ ] Keep README mutation-mode wording scoped to configured `diff`/`full`
      support versus adaptive prompting.
  - Spec evidence: AlphaEvolve Section 2.3 requests diff blocks for larger
    codebases and direct full-code output when code is very short or a rewrite
    is more suitable.
  - Current evidence: README correctly says LLM mutations use SEARCH/REPLACE
    diffs by default and full-block/full-code replacements when
    `mutation_mode: full` is configured. It should not imply that LibreEvolve
    currently chooses that output contract per candidate size, workspace shape,
    or prior failure mode.
  - Required result: when adaptive mutation-mode selection lands, update
    README, ROADMAP, papers index, and code/paper TODOs with the selection
    policy, per-candidate telemetry, and examples that prove diff prompts and
    full-rewrite prompts are selected under documented AlphaEvolve-style
    conditions.

- [ ] Keep README database-output claims scoped to prompt-visible output
      capture versus queryable output indexes.
  - Spec evidence: AlphaEvolve's evolutionary database stores generated
    solutions with evaluation results and program outputs attached, then
    resurfaces useful prior ideas in later generations.
  - Current evidence: README can describe strict evaluator `outputs` /
    `program_output` capture, redaction, truncation, stage output checks, and
    bounded prompt-visible program-output summaries. It should not imply those
    outputs are yet indexed as a durable database dimension or used for
    output-similarity/query-based resurfacing.
  - Required result: when `program_output_index` records, output-aware
    resurfacing APIs, durable output query tables, or semantic output
    retrieval land, update README, ROADMAP, papers index, and code/paper TODO
    entries together so README distinguishes prompt-visible program outputs
    from AlphaEvolve-style queryable output-attached database evidence.

- [ ] Keep README/AGENTS failure-memory claims scoped to run-local diagnostics.
  - Spec evidence: AlphaEvolve-style repeated-mutation avoidance should be able
    to reuse failed-proposal evidence across runs through durable, searchable,
    and semantically meaningful memory rather than only bounded display
    snippets.
  - Current evidence: README documents `failure_history.jsonl`,
    `load_failure_history_records()`, persisted failure fingerprints,
    repetition counts, and diagnostic-only mutation payload replay policy.
    Prompt context policy supports `recent_failure_limit`, selection modes,
    required/excluded error labels, changed files, stage names, text terms,
    repetition/score thresholds, and per-field caps. Runtime manifests include
    a bounded failure index grouped by fingerprint/repetition/recency.
    `AGENTS.md` now scopes this as persisted run-local failure diagnostics and
    bounded prompt-visible failure memory, not durable cross-run semantic
    failed-proposal memory.
  - Required result: when cross-run failure tables, semantic failed-proposal
    retrieval, learned repetition avoidance, replayable failed-mutation
    payloads, or durable failure-aware sampling policies land, update README,
    AGENTS.md, ROADMAP, papers index, and code/paper TODO entries together so
    docs neither underclaim current run-local failure memory nor overclaim
    AlphaEvolve-grade failed-proposal memory.

- [ ] Keep README meta-prompt context-policy wording scoped to validated
  current fields.
  - Spec evidence: AlphaEvolve-style meta-prompt evolution should improve
    prompt instructions and context policy, not only mutate whole prompt text
    or a fixed subset of locally known rendering controls.
  - Current evidence: README now documents prompt-program selection, scoring,
    lineage, prompt-history replay, rejected mutation diagnostics, bounded
    meta-prompt evidence, accepted JSON meta-prompt responses with optional
    `context_policy`, and validated `libreevolve.prompt_context_policy.v1`
    controls for optional channels, section priorities, mutation-instruction
    variants, parent-code selection/filtering/ranking/caps/truncation,
    proposal metadata enablement, feedback subsection selection/order/caps,
    inspiration sampling controls, and related diagnostics. It also documents
    `validate_meta_prompt_context_policy_capabilities()` checking the
    meta-prompt-visible capability map against the current structured policy
    fields.
  - Required result: when prompt-program policy can control retrieval or
    summarization behavior, learned/semantic context selection, arbitrary
    instruction channels, broader per-role retention, or other prompt surfaces
    beyond the currently validated field set, update README, ROADMAP, papers
    index, and code/paper TODO entries together so README neither underclaims
    current structured policy mutation nor overclaims full AlphaEvolve-grade
    prompt evolution.

- [ ] Keep README prompt-template compatibility and duplicate-arm wording
  scoped to current mutation-template validation.
  - Spec evidence: AlphaEvolve-style prompt evolution should distinguish
    prompt-template compatibility for each model-call role from generic
    mutation-template rendering checks, and should make duplicate prompt-arm
    semantics explicit.
  - Current evidence: README documents prompt-program selection, scoring,
    lineage, history replay, invalid-mutation diagnostics, configured
    `prompt_variant_semantic_policy`, stochastic `prompt_format_options`, and
    duplicate configured/evolved prompt templates retained as separate prompt
    arms with deterministic ids and `template_sha256` audit identity. Code
    validates known placeholders, dry-run formatting, AlphaEvolve-style
    configured mutation channels, and parent-placeholder retention for evolved
    children, but does not implement role-specific compatibility policy or
    prompt-program text deduplication.
  - Required result: when role-specific prompt-template compatibility,
    prompt-program deduplication, or an explicit validated no-dedup policy
    lands, update README, ROADMAP, papers index, and code/paper TODO entries
    together so README neither underclaims current template validation nor
    overclaims AlphaEvolve-grade prompt-policy management.

- [ ] Keep README meta-prompt scoring wording scoped to absolute/improvement
  reward modes and UCB-style prompt-arm selection.
  - Spec evidence: AlphaEvolve-style prompt evolution needs calibrated reward
    signals and ablation evidence for prompt-program lineages, not only direct
    child fitness or immediate score improvement.
  - Current evidence: README documents prompt-program selection, scoring,
    lineage, reward bounds/modes, normalized prompt reward metadata,
    reward-policy-compatible history replay, bounded prompt-performance
    evidence in meta-prompt requests, and UCB-style prompt-arm selection. Code
    currently supports `absolute` and `improvement` prompt reward modes rather
    than calibrated prompt-specific reward models or lineage ablation reports.
  - Required result: when calibrated meta-prompt rewards,
    prompt-lineage ablation reporting, or stronger prompt-policy attribution
    lands, update README, ROADMAP, papers index, and code/paper TODO entries
    together so README neither underclaims current prompt reward accounting nor
    overclaims AlphaEvolve-grade prompt evolution scoring.

- [ ] Keep README prompt-program database wording scoped to local prompt-arm
  history versus a solution-database analogue.
  - Spec evidence: AlphaEvolve Section 2.2 says meta-prompt instructions and
    context are co-evolved in a separate database analogous to solution
    programs.
  - Current evidence: README documents prompt-program selection, scoring,
    logging, duplicate-arm retention, prompt-history replay, and optional
    meta-prompt mutation. Current code implements that as a deterministic
    local prompt-arm store, not a prompt-side MAP-Elites/island database with
    descriptor/objective retention, archive events, migration/rebin semantics,
    or async/controller resume state.
  - Required result: when prompt-side archive semantics or benchmark evidence
    for a solution-database-equivalent prompt database land, update README,
    ROADMAP, papers index, and code/paper TODOs so README distinguishes the
    current prompt-history selector from AlphaEvolve's separate co-evolved
    prompt database.

- [ ] Keep README MAP-Elites descriptor claims scoped to insertion-time
  TF-IDF coordinates.
  - Spec evidence: AlphaEvolve-grade quality-diversity search should use
    task-meaningful behavior descriptors or stable learned descriptor models,
    with explicit archive compatibility when descriptors change.
  - Current evidence: README now documents that workspace complexity/diversity
    use stable text-workspace serialization, that `map_elites_descriptor_axes`
    can select configured metric/metadata axes, and that archive snapshots
    persist a `descriptor_model` with current diversity reference ids plus
    no-rebin insertion-time coordinate policy. It also says existing cells are
    not re-binned and diversity coordinates are local heuristic coordinates
    rather than stable learned descriptors.
  - Required result: once evaluator-provided behavior descriptors, learned
    descriptor models, or tested archive rebin semantics land, update the
    README and matching code/paper TODO entries together so the README neither
    underclaims descriptor-policy snapshots nor overclaims AlphaEvolve-grade
    behavior descriptors.

- [ ] Keep README island-count claims scoped to configurable defaults.
  - Spec evidence: AlphaEvolve describes an island-inspired evolutionary
    database, while LibreEvolve's local implementation exposes island count as
    configuration rather than a fixed paper-derived constant.
  - Current evidence: README now describes configurable ring-topology island
    migration with a five-island default, matching `Config.n_islands` and the
    tests that instantiate one-, two-, and three-island models.
  - Required result: when future topology or migration-policy work lands,
    update README, ROADMAP, papers index, and code/paper TODO entries together
    so the README does not imply a hardcoded five-island runtime or overclaim
    AlphaEvolve-specific island-policy fidelity.

- [ ] Keep README per-role LLM scheduler claims scoped to current role routing
  and budget maps.
  - Spec evidence: AlphaEvolve-style LLM orchestration needs role-specific
    scheduling and reward semantics for proposal generation, critique,
    feedback, and prompt improvement, not only role labels on shared telemetry.
    Its Section 2.4 model mix also uses a fast model for high-volume
    candidate generation and a stronger model for occasional higher-quality
    suggestions.
  - Current evidence: README now says `role_scheduler_state` is an
    audit/restoration record, while role routing can narrow eligible backends
    and role budget maps can stop matching roles before later calls. It also
    states that the global ensemble state remains authoritative and that
    independent per-role scheduler configuration, reward calibration, and
    quota/budget ownership remain open. README should likewise avoid implying
    that backend metadata or `throughput_depth` unit coverage proves a
    Flash/Pro-style fast-breadth plus strong-depth scheduling policy.
  - Required result: once independent per-role live scheduler state, calibrated
    reward semantics, quota/budget ownership, and experiment-backed fast/
    strong model-mix scheduling land, update the README and matching
    code/paper TODO entries together so the README neither underclaims current
    role-scoped backend eligibility nor overclaims AlphaEvolve-style role or
    model-mix scheduling.

- [ ] Keep README provider claims explicit about missing Google/Gemini
      first-class support.
  - Spec evidence: AlphaEvolve's published model mix uses Gemini 2.0 Flash and
    Gemini 2.0 Pro for fast/strong scheduling.
  - Current evidence: README can accurately describe OpenAI, Anthropic,
    Ollama, and custom backend support, but the built-in registry does not
    include a Google/Gemini backend. A custom backend is not the same as
    first-class provider telemetry, credential preflight, capability evidence,
    or Flash/Pro lane labeling.
  - Required result: if Gemini support or an equivalent provider-plugin
    contract lands, update README, ROADMAP, papers index, and code/paper TODOs
    so provider claims distinguish generic extensibility from reproducing or
    deliberately substituting AlphaEvolve's Gemini Flash/Pro ensemble.

- [ ] Keep README sample-efficiency claims scoped to budget telemetry until
      proposal-count evidence exists.
  - Spec evidence: AlphaEvolve Table 1 contrasts FunSearch's millions of LLM
    samples with AlphaEvolve's thousands of samples, and Section 4 ties
    performance to stronger model/full-system components under fixed compute
    budgets.
  - Current evidence: README documents logical LLM call caps, provider-attempt,
    token, configured-cost, and latency stops, sequential
    `proposals_per_generation` batches, equal-budget ablation report schemas,
    and the `Small base LLM only` registry variant. It does not document
    benchmark evidence that useful target progress is achieved in
    thousands-scale generated/evaluated proposal counts.
  - Required result: once benchmark reports track generated proposals,
    evaluated candidates, admitted/retained candidates, target hits, and
    score/target progress versus LLM sample budgets, update README, ROADMAP,
    papers index, and code/paper TODOs so README does not imply that budget
    caps or small-base labels prove AlphaEvolve-style sample efficiency.

- [ ] Keep README critique-reviewer wording scoped to synchronous first/last
  valid mutation selection.
  - Spec evidence: AlphaEvolve-style critique/reviewer channels need calibrated
    signal, explicit budget policy, and robust provider isolation beyond a
    sequential mutation-replacement filter.
  - Current evidence: README now says `critique_reviewers` runs a synchronous
    bounded reviewer pool with manifest-safe reviewer names, optional prompts,
    role labels such as `critique:correctness`, existing backend routing and
    role budget telemetry, `first_valid` or `last_valid` aggregation, and
    retained `metadata.critique.reviewer_pool.reviewers[]` records with parser
    status and selected-reviewer provenance. Matching code/roadmap TODOs still
    say reviewer calls are sequential, replacement-only, and selected by
    first/last valid mutation rather than calibrated reviewer score or
    benchmarked reviewer reliability.
  - Required result: when async reviewer overlap, calibrated reviewer scoring,
    reviewer-pool ablations, stronger per-reviewer provider isolation, or
    richer reviewer-specific timeout/failure artifacts land, update README,
    ROADMAP, papers index, and code/paper TODO entries together so README
    neither underclaims the current synchronous reviewer-pool metadata nor
    overclaims AlphaEvolve-grade critique orchestration.

- [ ] Keep README LLM budget/replay claims scoped to current synchronous
  restore boundaries.
  - Spec evidence: AlphaEvolve-scale reproduction needs compute-budgeted model
    scheduling, replayable run accounting, and enough provider evidence to
    distinguish resumed controller state from replayed provider outputs. It
    also needs a clear boundary between sequential sibling proposal batches and
    any future consecutive-mutation-depth policy used to keep search deep when
    evaluator feedback is slow.
  - Current evidence: README now documents live synchronous
    provider-attempt/token/configured-cost/latency stops, restorable runtime
    budget snapshots, `controller_budget_events.jsonl` replay, and
    full-runtime restore validation. It also documents strict call-ledger
    provider-failure summaries and restorable scheduler failure-policy state,
    and it correctly states that `proposals_per_generation` is sequential
    batch sampling/accounting rather than parallel LLM/evaluator execution.
    while still marking live provider pricing/default-rate capture beyond
    configured estimates, provider-output/raw-payload replay, cross-run
    provider-failure policy proof, async/pending-work budget composition, and
    mutation-chain-depth policy for slow evaluator feedback as open.
  - Required result: once provider-output replay, async/pending-work budget
    composition, live pricing/default-rate capture beyond configured
    estimates, cross-run provider-failure quarantine/resume proof, or
    consecutive-mutation-depth control lands, update the README and matching
    code/paper TODO entries together so the README neither underclaims current
    synchronous budget replay and provider failure-policy evidence nor
    overclaims full AlphaEvolve-style replay.

- [ ] Keep README lineage replay wording scoped to loop-owned deterministic
  ids and provider-output non-replay boundaries.
  - Spec evidence: AlphaEvolve-scale ablations and repeated-seed comparisons
    need reproducible lineage records that distinguish deterministic framework
    ids from stochastic provider/plugin/validator behavior.
  - Current evidence: README now documents run-local RNG restore,
    `load_full_resume_bundle(manifest.json)`,
    `--restore-runtime-from-manifest`, `runtime.lineage_replay_policy`,
    deterministic loop-owned candidate, prompt, and LLM call id policy,
    explicit exclusion of direct `Program()` and `PromptProgram()` UUID4
    defaults from the replay contract, and the fact that replay-stable LLM call
    ids do not prove identical provider outputs. `AGENTS.md` now also states
    that `config.seed` initializes the run-local framework RNG rather than
    reseeding Python's process-global `random` module. Code TODO evidence still
    says direct UUID boundaries, plugin/provider RNG boundaries,
    provider-output replay, and end-to-end resumed-trace lineage proof remain
    open.
  - Required result: when provider/plugin output replay, direct UUID replay
    contracts, plugin/provider RNG capture, ordered migration replay, or
    resumed-trace lineage proof lands, update README, AGENTS.md, ROADMAP,
    papers index, and code/paper TODO entries together so README and
    agent-facing instructions neither underclaim current loop-owned
    deterministic id policy nor overclaim full AlphaEvolve-grade lineage
    replay.

- [ ] Keep README DeepResearch retrieval evidence scoped to bounded redacted
  sidecars and non-semantic provenance.
  - Spec evidence: retrieval-driven AlphaEvolve-style runs should identify the
    external knowledge injected into prompts while distinguishing replayable
    retained artifacts from unbounded raw provider/source availability, TLS
    transport replay, and semantic source correctness.
  - Current evidence: README now documents
    `libreevolve.retrieval_payload_artifact.v1` sidecars,
    `libreevolve.retrieval_payload_artifact_inventory.v1`,
    `libreevolve.retrieval_source_ranking_provenance.v1`,
    `libreevolve.retrieval_source_content_trust_policy.v1`,
    `libreevolve.retrieval_transport_policy.v1`,
    `libreevolve.retrieval_source_grounding_policy.v1`,
    `libreevolve.retrieval_evidence_boundary_policy.v1`,
    `libreevolve.retrieval_context_audit_policy.v1`,
    `libreevolve.retrieval_semantic_boundary_audit.v1`, and
    `libreevolve.retrieval_evidence_coverage.v1`. It states that retained
    under-budget payloads can be checked through secret-redacted sidecar
    artifacts and inventory hashes; active prompt context links to bounded
    transport, source-content, lexical-grounding, and evidence-boundary states;
    semantic-boundary audits and run-level coverage validation reject raw
    payload, semantic-verification, learned-ranking, TLS-replay, full-replay,
    and authoritative-context overclaims. Unbounded raw payload availability,
    semantic source correctness, learned/external ranking, and replayable
    transport/TLS decision evidence remain open.
  - Required result: when retrieval payload retention, learned/external source
    ranking, semantic verification, or transport/TLS replay evidence changes,
    update README, code TODOs, and paper TODOs together so the README neither
    underclaims bounded redacted sidecar replay nor overclaims DeepEvolve-grade
    auditability.

- [ ] Keep README environment-provenance claims scoped to bounded audit
  evidence.
  - Spec evidence: AlphaEvolve-scale experimental results should be
    reproducible against the evaluator environment, including external build
    steps, package sources, accelerator runtime, and compute-budget evidence.
  - Current evidence: README now documents selected project/build metadata,
    known lockfile hashes, installed-distribution metadata, bounded/redacted
    `pip freeze` and `pip config` evidence, NumPy config hashes, provider SDK
    versions, and bounded accelerator environment/driver probe hints. It also
    states that the policy is audit-only and excludes complete install-source
    interpretation, broader non-project build provenance, private package
    source identity/authentication resolution, remote package artifact
    verification, live provider service/default capture, and accelerator
    budget/accounting evidence.
  - Required result: once replayable external-build records, package-source
    resolution policy, remote artifact verification, accelerator budget
    accounting, or environment restore/check validators land, update README,
    roadmap, papers index, and code/paper TODO entries together so the README
    neither underclaims current bounded environment evidence nor overclaims a
    reproducible AlphaEvolve-grade runtime environment.

- [ ] Keep README archive restore claims scoped to current archive-content
  restore.
  - Spec evidence: AlphaEvolve-style long-running evolutionary search needs
    reproducible population state and clear boundaries for migration-order
    replay versus snapshot restore.
  - Current evidence: README now says full archive cell/island contents can be
    restored from manifest snapshots plus checked accepted-history rows, while
    ordered migration-event replay remains audit-only rather than a MAP-Elites
    restore engine. Both the early runtime-provenance section and the archive
    section now distinguish cursor-only restore from
    `--restore-archive-from-manifest` full archive bundle restore.
  - Required result: when ordered migration-event replay or async
    controller/pending-work resume lands, update README archive sections,
    roadmap, papers index, and code/paper TODO entries together so they do not
    underclaim archive-content restore or overclaim migration replay.

## Architecture Description
