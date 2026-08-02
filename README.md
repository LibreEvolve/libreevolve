# LibreEvolve

LibreEvolve is a Python research workbench for LLM-guided evolutionary program
discovery. It loads a problem directory, evaluates seed programs, asks
configured LLM backends for mutations, scores the candidates, and keeps useful
programs in local quality-diversity archives.

The project is inspired by AlphaEvolve, Karpathy's `autoresearch`, MAP-Elites,
and related LLM-guided program-search work. It is independent research code and
is not affiliated with or endorsed by Google DeepMind or the authors of the
cited papers.

## Current Status

LibreEvolve is alpha-stage software. The honest current shape is a local,
Python-first evolutionary-programming workbench with extensive artifact and
absence-boundary reporting. It is useful for local experiments, implementation
audits, and building small fixtures. It is not a production optimizer, not a
distributed service, and not a full AlphaEvolve reproduction.

Runnable today:

- Task-primary bounded UTF-8 text workspaces. Python seed primaries are
  autodetected by default; `initial_programs/seed_policy.yaml` can select a
  non-Python primary for a stage-bound host or digest-pinned OCI language/build
  runner.
- Opt-in strict initial-program validity reports for runs that require every
  selected seed to be evaluator-valid before mutation; multi-seed,
  provider-startup, matrix, and constructive-math strict evidence remains
  open work.
- SEARCH/REPLACE mutation diffs using canonical AlphaEvolve-style fences,
  configurable full-code replacement, and opt-in per-candidate `adaptive`
  selection between them.
- OpenAI, Anthropic, Google Gemini, Ollama, experimental Codex CLI, and custom
  import-path backend support.
- Heuristic UCB-style backend selection.
- Local MAP-Elites and island archives, with five islands by default.
- Local subprocess evaluation with optional staged validators.
- Opt-in bounded local asyncio workers for sibling LLM mutations and candidate
  evaluations, with deterministic proposal-order shared-state commit.
- Optional critique, feedback, and plugin hooks.
- Gitignored run artifacts under `runs/`.

Important limits:

- No checked-in run reproduces AlphaEvolve's published benchmark results,
  scale, model mix, distributed asynchronous topology, or systems/compiler/hardware
  application evidence.
- LibreEvolve is not the Google Cloud AlphaEvolve Service API, not a Gemini
  Enterprise managed agent, and not evidence of access to AlphaEvolve private
  preview or Pre-GA product surfaces; `papers/alphaevolve_cloud_access_boundary.json`
  records official source snapshots for those access claims only.
- Google Keyword one-year AlphaEvolve customer-impact claims are source
  reporting only; `papers/alphaevolve_keyword_customer_boundary.json` does not
  prove customer availability or local managed-service support.
- AlphaEvolve UI/API collaborator rosters are source attribution only;
  `papers/alphaevolve_ui_api_attribution_boundary.json` does not prove local
  UI, managed API, customer-engagement, or role-to-artifact evidence.
- The DeepMind AlphaEvolve product/science page reference is source context
  only; `papers/alphaevolve_product_page_boundary.json` records the current
  HTTP 404 result and does not prove product-page availability.
- `papers/alphaevolve_impact_claim_policy_boundary.json` normalizes official
  2026 impact values for review, but no row is release-note eligible without
  local fixtures, reproduction artifacts, and independent verification.
- `papers/alphaevolve_impact_verification_matrix_boundary.json` records claim
  and outbound-source absence rows; no impact row has a local benchmark report
  or independent verification.
- Many AlphaEvolve-facing JSON sidecars are validators or absence-boundary
  records. They are evidence that a claim is tracked conservatively, not proof
  that the underlying feature or benchmark has been reproduced.
- `papers/alphaevolve_source_inventory_boundary.json` verifies all 55 named
  structural spans in the pinned 44-page AlphaEvolve PDF: 38 section/front-
  matter/appendix spans, 14 numbered figures, and 3 numbered tables. This is a
  source-audit completeness boundary, not sentence-level requirement coverage,
  benchmark reproduction, production-scale evidence, or AlphaEvolve parity.
- `papers/alphaevolve_system_requirement_inventory_boundary.json` adds a
  bounded claim-level audit of 56 implementation-bearing requirements from all
  eight Table 1 rows, Sections 2.1-2.6, and Figures 1-3. Fourteen are locally
  implemented, 31 are partial, 4 are not implemented, and 7 are not
  demonstrated; all 42 incomplete requirements have live TODO ownership. This
  does not cover the remaining paper claims or prove AlphaEvolve parity.
- `papers/alphaevolve_context_claim_inventory_boundary.json` separately audits
  45 platform, method, scope, headline-result, capability, self-improvement,
  limitation, and collaborator-context claims from the Abstract, Introduction,
  Discussion, and one Acknowledgements sentence. Six are locally implemented,
  11 are partial, 4 are not implemented, and 24 are not demonstrated; all 39
  gaps have live TODO ownership.
- `papers/alphaevolve_matrix_result_claim_inventory_boundary.json` audits 44
  claims from Section 3.1, every selected Table 2 rank row, Figure 4, and
  footnote 3. None is classified as locally implemented: 8 are partial, 3 are
  not implemented, and 33 are not demonstrated; all 44 gaps have live TODO
  ownership.
- `papers/alphaevolve_math_result_claim_inventory_boundary.json` audits 63
  claims from Section 3.2 and Figure 5, including all nine displayed result
  pairs, constructive-math search behavior, named outcomes, artifact claims,
  and mathematician-collaboration provenance. Two are locally implemented, 16
  are partial, 4 are not implemented, and 41 are not demonstrated; all 61 gaps
  have live TODO ownership. It also corrects a false local attribution of a
  blanket verification sentence that is absent from the pinned PDF.
- `papers/alphaevolve_scheduling_claim_inventory_boundary.json` audits 45
  claims from the Section 3.3 opening, Section 3.3.1, and Figure 6, including
  the scheduling problem, vector-bin-packing formulation, ranking-only safety,
  simulator/held-out/deployment claims, production and deep-RL comparisons,
  exact heuristic terms, heatmap axes, and legend semantics. Nineteen are
  partial, 14 are not implemented, and 12 are not demonstrated; all 45 gaps
  have live TODO ownership.
- `papers/alphaevolve_kernel_claim_inventory_boundary.json` audits 59 claims
  from Section 3.3.2 and Figure 7, including JAX/Pallas context, tiling
  semantics, manual and autotuning baselines, candidate/runtime evaluation,
  shape-corpus splits, measured speedups, deployment, and Gemini
  self-optimization. Six are partial, 37 are not implemented, and 16 are not
  demonstrated; all 59 gaps have live TODO ownership.
- `papers/alphaevolve_hardware_claim_inventory_boundary.json` audits 35 claims
  from Section 3.3.3, including hardware-design context, the manual RTL
  workflow, Verilog task and verification requirements, the unnecessary-bit
  rewrite, downstream-synthesis caveat, TPU integration, Gemini attribution,
  adoption, and time-to-market wording. Twelve are partial, 4 are not
  implemented, and 19 are not demonstrated; all 35 gaps have live TODO
  ownership. It also corrects objective-versus-result and required-versus-
  passed-verification overstatements in earlier hardware sidecars.
- `papers/alphaevolve_compiler_claim_inventory_boundary.json` audits 44 claims
  from Section 3.3.4, including transformer/attention context, the
  FlashAttention/Pallas/JAX/XLA stack, direct compiler-IR editing, randomized
  per-edit reference checks, expert confirmation, kernel and wrapper speedups,
  and compiler-adoption paths. Twenty-two are partial, 6 are not implemented,
  and 16 are not demonstrated; all 44 gaps have live TODO ownership. It also
  preserves "most commonly" FlashAttention wording and treats memory-access
  and scheduling decisions as potential optimization categories rather than
  attributed descriptions of every reported edit.
- `papers/alphaevolve_ablation_claim_inventory_boundary.json` audits 51 claims
  from Section 4 and Figure 8, including experiment targets, component
  definitions, equal-budget curves, target aggregation, seed and uncertainty
  semantics, exact panel membership, and the reported component-contribution
  conclusion. Two are locally implemented, 36 are partial, 6 are not
  implemented, and 7 are not demonstrated; all 49 gaps have live TODO
  ownership. It also corrects the report/exhibit contract to six matrix-panel
  series but only three kissing-number-panel series.
- `papers/alphaevolve_related_work_claim_inventory_boundary.json` audits 85
  exact-page claims from Section 5. Six are locally implemented, 9 are
  partial, 4 are not implemented, 7 are not demonstrated, and 59 are
  source-context-only descriptions of cited work. All 20 implementation gaps
  have live TODO ownership; literature context is not counted as local
  implementation debt.
- `papers/alphaevolve_appendix_a_claim_inventory_boundary.json` audits 131
  exact-page claims from Appendix A, Table 3, and Figure 9: 29 prose/caption
  claims, all 54 matrix-result rows, and 48 panel-level program claims.
  Thirteen have partial metadata support and 118 are not demonstrated; all
  131 gaps have live TODO ownership. The registry is not decomposition or
  rediscovery evidence.
- `papers/alphaevolve_appendix_b_claim_inventory_boundary.json` audits 188
  exact-page and visible-panel claims from all 13 Appendix B subsections and
  Figures 10-14. Ninety-five have partial registry or method support, 24 are
  not implemented, and 69 reported constructions, results, captions, or panel
  semantics are not demonstrated; all 188 gaps have live code and paper TODO
  ownership. The inventory is not construction, verifier, rendered-exhibit,
  recomputation, or rediscovery evidence.
- `papers/alphaevolve_citation_use_inventory_boundary.json` scans the retained
  TeX input closure and inventories all 195 logical citation uses and 240 key
  links. All 120 compiled references resolve through `literature.bib`,
  `main.bbl`, and `papers/references.json`; 52 unused BibTeX entries are listed.
  Citation semantics and implementation relevance remain unclassified.
- `papers/alphaevolve_tex_source_detail_inventory_boundary.json` inventories
  all 30 retained-source caption, equation-environment, and semantic-footnote
  constructs: 22 captions, 5 equation environments, and 3 real footnotes, plus
  one excluded preamble macro template. Twenty-four constructs map to 80
  references into the existing bounded claim inventories, one maps to reviewed
  publication
  metadata, two are named-span locators, and three are decorative markers.
  Nothing is unmapped, no reference is unresolved, and the inventory adds no
  claims or implementation-parity credit.
- `papers/alphaevolve_tex_table_cell_inventory_boundary.json` inventories all
  3 retained table environments, 5 tabular blocks, 83 rows, and 240 top-level
  cells. All 78 data rows map to 78 existing bounded claims; 218 cells are
  bounded-claim components, 8 are FunSearch baseline context, and 14 are
  structural headers. Nothing is unmapped or unresolved, and no claims or
  parity credit are added. Citation semantics and Table 2/3 result reproduction
  remain open.
- `papers/alphaevolve_tex_code_listing_inventory_boundary.json` inventories all
  8 retained code-listing environments (4 `minted`, 3 `lstlisting`, and 1
  `verbatim`) and all 305 physical source lines. It maps 214 bounded-claim
  component lines through 344 line-level references to 60 existing claims and
  dispositions the remaining baseline, abbreviation, diff-marker, and
  structural lines. Nothing is unmapped or unresolved, and no claims or parity
  credit are added. Listing execution, compilation, omitted-code recovery, and
  result reproduction remain open.
- `papers/alphaevolve_tex_math_inventory_boundary.json` inventories all 309
  explicit math constructs in the retained TeX closure: 291 render inline and
  18 render as displays. Thirty-four inherit source-detail dispositions, 75
  inherit table-cell dispositions, and 200 map directly to existing bounded
  claims. Nothing is unmapped or unresolved, and the inventory adds no claims
  or parity credit. Formula correctness, proof validity, and result
  reproduction remain open.
- `papers/alphaevolve_tex_prose_inventory_boundary.json` inventories all 128
  retained body paragraphs and 402 grammatical sentences after masking the
  table, figure, equation, listing, and footnote surfaces audited separately.
  It maps 372 sentences to existing bounded claims and reviews 30 as nonclaims,
  with zero unmapped or unresolved sentences. This adds seven claims found by
  the prose walk, but complete sentence disposition is not sentence-internal
  clause/proposition exhaustiveness or independent semantic review.
- `papers/alphaevolve_tex_proposition_inventory_boundary.json` decomposes all
  195 retained sentences from the Abstract through Section 3.3.2 Gemini kernel
  engineering into 621 atomic propositions. Five hundred seventy map through
  592 references to 253 bounded claims; 40 are source context, 2 are author
  outlook, and 9 are qualified author interpretations.
  The cumulative review
  adds the previously unbounded direct-versus-instrumental-search and expensive-
  evaluation sample-efficiency claims. The kernel slice adds no new claim or
  parity credit, but repairs sentence mappings for the reported 23-percent
  average kernel speedup, 1-percent Gemini training-time reduction, and Gemini
  team research and engineering velocity. The remaining 207
  prose sentences and independent semantic review remain open.
- Together the twelve bounded inventories cover 846 claims: 30 locally
  implemented, 278 partial, 110 not implemented, 369 not demonstrated, and 59
  source-context-only, leaving 757 implementation gaps. Across the 787
  implementation-relevant claims, strict implemented parity is 3.8%; counting
  partial claims at half credit gives 21.5%. The weighted value rises because
  Appendix B registry metadata is partial, not because its results were
  reproduced. Citation linkage is lexically complete and every retained-source
  caption, equation-environment construct, and semantic footnote has a
  construct-level disposition; all 83 table rows and 240 cells have row/cell
  dispositions; and
  all 8 retained code listings and 305 physical source lines have line-level
  dispositions; all 309 explicit TeX math constructs have delimiter-level
  dispositions; and all 128 retained prose paragraphs and 402 grammatical
  sentences have dispositions; all 195 sentences from the Abstract through
  Section 3.3.2 Gemini kernel engineering also have 621 atomic-proposition
  dispositions. Coverage still excludes proposition review for the remaining
  207 sentences,
  mathematical correctness,
  image-pixel and citation-semantic review, independent result reproduction,
  independent proof of semantic completeness, and AlphaEvolve-scale execution.
- The local paper cache is source inventory. A cached paper or `papers/README.md`
  row does not mean the paper's method or results are implemented.
- `papers/related_work_taxonomy_boundary.json` records a bounded AlphaEvolve
  Section 5 Related Work taxonomy for method family, representation,
  evaluator/evidence mode, comparison axis, proof/witness status, and local
  implementation status. It is not exhaustive reference-level coverage,
  independent positioning review, benchmark reproduction, or proof that the
  related methods are implemented.
- Paper-inspired plugins are approximations and optional hooks, not faithful
  implementations of the cited methods unless a specific plugin document says
  otherwise.
- Evaluators run in local subprocesses, not hardened security sandboxes.
- Configured evaluation cascades emit a validated adjacent-stage transition
  matrix with promotion-rule attribution, bounded candidate linkage,
  next-stage exposure counts, and denominator reconciliation. Stages can also
  declare strictly increasing difficulty/scale rationale and content-hashed
  file-backed or embedded-input test-set identities. The checked 2x2 matrix
  calibration fixture executes four pinned seeds and proves that rank 7 passes
  while rank 8 reaches the main stage and fails its pinned confidence-bound
  gate. A second checked four-seed fixture runs the normal `evolve()` pipeline,
  records parent/lineage and budget causality, and reaches rank 7 under a
  scripted Strassen mutation control. This is deterministic local pipeline
  evidence, not stochastic LLM discovery, empirical error-rate,
  cost-efficiency, target-suite, or AlphaEvolve-scale proof.
- The controller, archive, migration, LLM samplers, and evaluators remain local.
  Opt-in `async_llm_sampling` prepares sibling prompts from pre-batch archive
  state and dispatches them through a bounded Python `asyncio` queue to named,
  worker-owned LLM ensembles. Calls can finish out of order but merge in proposal
  order; rewards return through the owning worker queue. Separately,
  `async_candidate_evaluation` overlaps sibling evaluations with bounded queue
  backpressure, exact in-flight duplicate coalescing, and deterministic
  submission-order archive admission. Shared feedback, budget, history, prompt-
  database, archive, and generation-boundary mutations remain serialized.
  `async_generation_window` defaults to `1`; values above `1` allow bounded
  later-generation sampler work to overlap prior-generation evaluator work
  using explicitly stale pre-drain archive, prompt-program/reward, and sampler-
  reward state. Process-local merged task intervals
  record observed generation-pair overlap, while admissions and generation-end
  hooks remain ordered. Finite cumulative evaluator limits other than the
  exactly reservable `max_evaluations` count retain a generation barrier. This
  is not a distributed AlphaEvolve service and does
  not provide a full dependency scheduler, pending-work resume, provider-output
  replay, or worker leases.
- Runtime restore certification is compatible-surface evidence only;
  `papers/restore_certification_boundary.json` records accepted/quarantine
  separation and overclaim rejection, but not provider raw-payload replay,
  controller pending-work replay, artifact payload reconstruction, or
  independent restore/replay audit.
- Non-JSONL run artifact schemas are tracked, but not replay-certified;
  `papers/non_jsonl_artifact_boundary.json` records current manifest schema,
  hash policies, docs anchors, and show/restore checks for artifacts such as
  `best.py`, `best_workspace/`, `plugin_artifacts/`, and `paper_artifacts/`.
- Candidate execution is Python by default, with partial task-declared host or
  digest-pinned OCI subprocess paths for text primaries. A `candidate_runner`
  stage runs validated command-token arrays without a shell, can probe an
  ordered build toolchain, enforce candidate lock-file hashes and optional
  host executable/version-output pins, capture bounded build artifacts, and
  pass a redacted process record to the problem-owned Python validator that
  remains metrics authority. OCI builds declare Docker/Podman candidates and
  an immutable `@sha256:` image; build and runner processes use the same
  verified image with network disabled, a read-only root filesystem, dropped
  capabilities, bounded CPU/memory/PIDs/tmpfs, and only the candidate workspace
  writable. An `if_missing` pull may use the host runtime's registry access,
  but candidate processes cannot. This is process isolation, not a hostile-code
  security sandbox. The expression, host C11, and OCI Python fixtures are smoke
  contracts; they do not prove broad package restoration, cross-platform or
  remote-daemon replay, language-aware marker grammars, or AlphaEvolve-scale
  arbitrary-codebase support.
- Candidate abstractions are code-file/workspace based; problem-defined direct
  solution objects, constructor-function search, bespoke search-algorithm
  candidates, paired solution/search representations, abstraction-specific
  prompts/validators/archive descriptors, migration policies, and equal-budget
  cross-abstraction reports are tracked as missing AlphaEvolve-style work.
- Prompt templates are validated for known placeholders, formatting, mutation
  channels, parent-placeholder retention, and independent duplicate-arm
  identity; `papers/prompt_template_compatibility_boundary.json` records that
  role-specific compatibility for critique, feedback grading, meta-prompt, and
  context-policy surfaces remains open.
- Primary-prompt reports join hash-only prompt-role policy telemetry when
  mutation-call telemetry is present, but provider-family payload-shape audits,
  provider-specific message transcripts, and full AlphaEvolve primary-prompt
  role-placement parity remain open in
  `papers/primary_prompt_role_telemetry_boundary.json`.
- Meta-prompt scoring is child-score reward accounting, not calibrated prompt-
  policy attribution; prompt-lineage ablations and equal-budget prompt-policy
  comparisons remain open in `papers/meta_prompt_scoring_boundary.json`.
- `PromptDatabase` is local prompt-arm history/scoring, not a prompt-side
  solution-database analogue with archive retention, descriptor/objective
  indexes, migration/rebin semantics, or async resume; that gap is tracked in
  `papers/prompt_database_parity_boundary.json`.
- Built-in SDK provider adapters are OpenAI, Anthropic, Google Gemini, and
  Ollama. The Gemini adapter provides credential preflight, GenerateContent
  request/response handling, usage/default/error telemetry, API-version
  context, and Flash/Pro lane classification. No checked live run proves that
  the paper's Gemini 2.0 models remain available to this account or that the
  resulting model mix reproduces AlphaEvolve; that boundary remains in
  `papers/gemini_provider_parity_boundary.json`.
- The built-in Codex CLI adapter (`type: codex`) is an experimental local CLI
  lane for authenticated `codex exec` sessions. It records redacted auth/session
  provenance and optional transcripts, but it is not yet benchmark- or
  paper-claim-ready because credential-safe live smoke evidence, model
  availability preflight, manifest/report integration, provider-native
  token/cost accounting, and parity diagnostics remain open work in
  [docs/todo/code.md](docs/todo/code.md).
- Custom import-path backends are extension points. A custom wrapper around a
  local CLI is not portable provider support or benchmark evidence unless it is
  promoted to a documented provider lane with its own tests and telemetry.
- The included examples are smoke fixtures unless they explicitly document
  stronger benchmark evidence.
- The default initial-program policy is permissive; AlphaEvolve-style complete
  initial-solution parity requires explicit strict-mode evidence.
- Adaptive mutation mode uses configured workspace character/file/evolve-block
  thresholds, an optional task preference, recent same-parent selected-mode
  failures, and opposite-format parser fallback. These are local heuristics,
  not benchmark-calibrated rewrite judgments, learned response-quality policy,
  or equal-budget AlphaEvolve reproduction evidence.
- Human-seeded initial-program claims require exact prompt/context linkage,
  seed workspace hashes, replicate protocols, equal-budget seed-variant
  tables, and contribution review evidence; current reports are metadata
  contracts only.
- Expert-guided mathematical benchmark formulation claims require populated
  expert/owner identity, evaluator/report artifact linkage, signoff versions,
  background-reference artifacts, and anti-gaming review evidence; current
  formulation reports are metadata contracts only.
- Collaborator-feedback robustness claims require multi-cohort source
  artifacts, workflow diffs, validation reruns, privacy/redaction artifacts,
  review versions, follow-up, and claim-to-feedback traces; current feedback
  reports are metadata contracts only.
- Self-improvement and distillation claims require optimized component
  identity, before/after execution-path measurements, deployment/adoption,
  rollback/safety review, and distillation dataset/training/evaluation
  artifacts; `papers/self_improvement_distillation_boundary.json` records
  that this evidence is not implemented.
- Feedback-loop cadence and environment-ROI claims require loop IDs,
  elapsed-month timelines, moderate-gain calibration, evaluator-environment
  setup/maintenance costs, expected-versus-realized discovery value, and
  expansion decision evidence; `papers/self_improvement_cadence_boundary.json`
  records that this evidence is not implemented.
- Workspace materialization diagnostics are local file-workspace evidence, not
  proof for bulk directory operations, language/build-runner artifacts,
  dependency graphs, portable static-asset source identity, or remote/container
  mounts.
- Paper-derived claims are tracked conservatively in `papers/README.md`,
  sidecar JSON records, `ROADMAP.md`, and `docs/todo/`; the TODO ledgers are
  active work queues, not just historical notes.

For the full implemented-versus-missing ledger, read
[docs/status.md](docs/status.md). For paper/source coverage, read
[papers/README.md](papers/README.md).

## Requirements

- Python 3.11 or newer.
- On this Windows machine, use `py -3.12`, not `python`.
- Optional provider credentials in `.env` for provider-backed runs.

Install for local development:

```bash
py -3.12 -m pip install -e ".[dev]"
```

## Quick Start

Verify the CLI and artifact writer without making provider calls:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --run-name readme_smoke_sorting --max-llm-calls 0 --overwrite
py -3.12 -m libreevolve show runs/readme_smoke_sorting
```

That evaluates the bundled sorting seed, writes normal run artifacts, and stops
before constructing LLM providers. It is a smoke check, not an evolution run.

Exercise the task-declared non-Python build/runner contract without a provider:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/candidate_runner_expression --run-name readme_smoke_candidate_runner --max-generations 0 --overwrite
py -3.12 -m libreevolve show runs/readme_smoke_candidate_runner
```

This fixture builds and runs a small `.expr` primary, then lets the
problem-owned Python validator score the bounded process record. The commands
inherit the host network and run as ordinary local subprocesses; this is a
contract smoke test, not a security sandbox or real-language benchmark.

Exercise the real C compiler path when `clang`, `gcc`, or `cc` is installed:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/candidate_runner_c --run-name readme_smoke_candidate_runner_c --max-generations 0 --overwrite
py -3.12 -m libreevolve show runs/readme_smoke_candidate_runner_c
```

This fixture compiles and runs a small C11 primary, records the selected
compiler executable and version-output hashes, and verifies a checked build-
contract lock. Exact compiler pins are intentionally unset, so the resulting
run does not claim portable replay.

Run a provider-backed evolution after choosing a model that is available in
your account or local Ollama install:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "openai:<openai-model-id>"
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --max-generations 10 --backends "anthropic:<anthropic-model-id>"
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "gemini:<gemini-model-id>"
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "ollama:<installed-ollama-model>"
```

Provider-backed runs can spend API credits and may fail during preflight if
credentials, model IDs, local Ollama state, or account access are unavailable.

Use a fresh `--run-name` for repeat runs, or pass `--overwrite` when replacing
an existing run directory intentionally.

## Problem Layout

Problem directories live under `libreevolve/problems/examples/`. A minimal
problem usually contains:

- `initial_programs/`: one or more seed programs.
- `validate.py`: evaluator entrypoint.
- `metrics.yaml`: metric names, directions, bounds, and primary metric.
- `task_description.txt`: task instructions for the mutation prompt.
- optional `config.yaml`: backend, archive, prompt, and evaluator settings.
- optional `initial_programs/seed_policy.yaml`: hidden/cache path policy and an
  explicit workspace `primary_file` when Python autodetection is not desired.

See [docs/problem-format.md](docs/problem-format.md) for the full contract.

## Example Scope

The bundled examples are intentionally small:

- Optimization-pressure seeds may be valid-but-weak or intentionally invalid
  baselines that leave room for measurable improvement.
- Neutral plateau/diversity fixtures mainly exercise loading, validation,
  artifact writing, or archive behavior.
- `candidate_runner_expression` is a non-comparable contract smoke fixture. It
  exercises an explicit non-Python primary, local build and runner commands,
  generated-artifact capture, and problem-owned scoring; it is not evidence
  for a real language, compiler, package manager, or codebase-scale benchmark.
- `candidate_runner_c` is a non-comparable real-compiler contract smoke fixture.
  It compiles one toy C11 program with a discovered host compiler, records
  toolchain identity, verifies a lock hash, and runs the generated executable;
  it is not hermetic replay or codebase-scale benchmark evidence.
- `candidate_runner_python_oci` is a non-comparable interpreted-language OCI
  contract fixture. It compiles and runs one toy Python file in an official
  digest-pinned image, verifies an in-workspace lock hash, and requires
  network-disabled/read-only-rootfs/resource-bounded execution evidence. Its
  real Docker/Podman integration test is opt-in with
  `LIBREEVOLVE_RUN_OCI_FIXTURE=1` and skips when no local daemon is healthy; the
  default mocked contract tests are not live cross-host certification.
- `sorting_network_8` and `sorting_network_9` are bounded benchmark candidates
  with exhaustive zero-one validation and known comparator targets, but they
  are not paper-comparable evidence until repeated runs and certification are
  added. Their hardening bundle helper emits generic
  negative-fixture, inventory, summary, and scope-validation evidence; it is
  not a certified rediscovery result. `sorting_network_9/run_contract.json`
  records the clean-checkout Codex CLI invocation, auth expectations,
  evaluator budget, expected artifacts, manifest checks, and skip/failure
  modes for an authenticated experimental run; the `benchmark_run_contract`
  validator checks the reusable contract shape against local fixture paths,
  config/auth settings, validator constants, linked prompt provenance,
  artifact expectations, and overclaim boundaries. The paired
  `sorting_network_9/benchmark_goal_prompt.json` records the under-4000
  character external-agent handoff prompt for that run, and the
  `benchmark_goal_prompt` validator checks the prompt count, model/auth
  linkage, overclaim boundary, and the run contract's emitted
  `runtime.benchmark_goal_prompt.prompt_id` provenance requirement. The paired
  `sorting_network_9/benchmark_provider_profile.json` records the experimental
  Codex provider lane, local-auth support status, budget, transcript/redaction
  policy, expected artifacts, and result-linkage boundary; the
  `benchmark_provider_profile` validator checks it against the config, run
  contract, and prompt artifact. These are still protocol inputs, not a
  successful rediscovery transcript. The checked
  `papers/sorting_network_source_citation_boundary.json` sidecar records the
  zero-one-principle and comparator-target citations used to calibrate these
  fixtures, and `papers/sorting_network_source_snapshot_boundary.json`
  records live response metadata and hashes for those citation URLs without
  retaining full raw source bodies. `papers/sorting_network_source_refresh_gate_boundary.json`
  records the deterministic source-refresh gate for those citation snapshots,
  and `papers/sorting_network_source_refresh_run_2026-06-18.json` archives a
  live refresh run that detected Codish publication source drift; that drift
  is triaged in `papers/sorting_network_source_drift_triage_boundary.json` as
  full-page hash instability with citation markers still present.
  `papers/sorting_network_normalized_marker_snapshot_boundary.json` records a
  stable normalized marker snapshot for those citation facts; source snapshot
  metadata still needs to be updated before source freshness can be claimed.
  `papers/sorting_network_rediscovery_boundary.json` preserves the remaining
  non-certified run-evidence scope.

Treat an example as benchmark evidence only when its own docs or paper sidecar
says so.

## Run Artifacts

Runs write to `runs/<run-name>/`, which is gitignored. Common outputs include:

- `manifest.json`
- `archive_events.jsonl`
- `controller_budget_events.jsonl`
- `duplicate_work_cache_index.jsonl`
- `evaluator_results.jsonl`
- `failure_history.jsonl`
- `history.jsonl`
- `llm_calls.jsonl`
- `prompt_current_binding_table.jsonl`
- `prompt_history.jsonl`
- `prompt_prior_score_table.jsonl`
- `best.py`
- `best_workspace/`
- `evaluator_artifacts/`
- `plugin_artifacts/`

See [docs/run-artifacts.md](docs/run-artifacts.md) for schemas, quarantine
streams, restore behavior, and inspection details.

## Documentation Map

- [docs/README.md](docs/README.md): reader paths and documentation boundaries.
- [docs/architecture.md](docs/architecture.md): runtime architecture.
- [docs/configuration.md](docs/configuration.md): config fields and CLI
  overrides.
- [docs/backends.md](docs/backends.md): provider adapters and custom backends.
- [docs/plugins.md](docs/plugins.md): plugin hooks and built-in plugins.
- [docs/run-artifacts.md](docs/run-artifacts.md): files written under `runs/`.
- [docs/status.md](docs/status.md): detailed implementation and absence ledger.
- [ROADMAP.md](ROADMAP.md): practical implementation priorities.
- [papers/README.md](papers/README.md): paper cache, status rows, and claim
  boundaries.
- [docs/todo/](docs/todo/): active and completed gap ledgers.
- [AGENTS.md](AGENTS.md): agent-facing operating contract for local coding
  agents.

The docs are split by purpose. Setup and first-run usage belongs here;
operational details belong in `docs/`; paper-derived claim evidence belongs in
`papers/`; active and completed gap tracking belongs in `docs/todo/` and
`ROADMAP.md`. Tracked material under `old/` is archival and non-authoritative;
it is retained for historical context, not current implementation evidence.

## Research Sources

The local paper cache contains 53 PDFs on LLM-guided evolution, program
synthesis, quality-diversity optimization, and related benchmarks. The PDFs are
gitignored; committed manifests record download URLs, byte counts, and SHA-256
hashes.

Rehydrate the ignored PDF cache on a fresh checkout:

```bash
py -3.12 -m libreevolve.tools.paper_manifest --rehydrate
```

Validate the committed paper index:

```bash
py -3.12 -m libreevolve.tools.paper_manifest
py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs
```

Manifest `title` values are inventory/display slugs derived from local cache
names, not authoritative bibliographic titles. Use `papers/README.md` for
paper-facing titles, implementation status, and benchmark coverage decisions.

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
  llm/           OpenAI, Anthropic, Gemini, Ollama, custom backends, and ensemble routing
  population/    program records, MAP-Elites, island migration
  plugins/       optional lifecycle hooks and paper-inspired plugins
  problems/      examples and problem loading
  tools/         paper/source manifest validation
docs/            architecture, configuration, backend, plugin, and artifact docs
papers/          tracked manifests plus ignored PDF cache and retained source artifacts
old/             archival, non-authoritative historical planning material
runs/            gitignored run outputs
tests/           unit and integration tests
AGENTS.md        agent-facing operating contract for local coding agents
```

## Contributing

Keep the root README practical and short. Detailed behavior belongs in `docs/`,
paper-boundary evidence belongs in `papers/README.md` and JSON sidecars, and
long-term implementation status belongs in `ROADMAP.md` or `docs/todo/`.

Before opening a change, run focused tests for touched code and the paper
manifest check when source-boundary files change.
The secret scan uses `.secrets.baseline`; intentional synthetic provider/API failure
examples should use `# pragma: allowlist secret`, and regenerated baselines
must be staged with the code that needs them rather than left unstaged.

## License

MIT. See [LICENSE](LICENSE).
