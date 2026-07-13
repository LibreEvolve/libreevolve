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

- Python-primary seed programs and bounded text workspaces.
- Opt-in strict initial-program validity reports for runs that require every
  selected seed to be evaluator-valid before mutation; multi-seed,
  provider-startup, matrix, and constructive-math strict evidence remains
  open work.
- SEARCH/REPLACE mutation diffs using canonical AlphaEvolve-style fences, plus
  configurable full-code replacement mode.
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
  database, archive, and generation-boundary mutations remain serialized. This
  is not a distributed AlphaEvolve service and does not provide cross-generation
  overlap, pending-work resume, provider-output replay, or worker leases.
- Runtime restore certification is compatible-surface evidence only;
  `papers/restore_certification_boundary.json` records accepted/quarantine
  separation and overclaim rejection, but not provider raw-payload replay,
  controller pending-work replay, artifact payload reconstruction, or
  independent restore/replay audit.
- Non-JSONL run artifact schemas are tracked, but not replay-certified;
  `papers/non_jsonl_artifact_boundary.json` records current manifest schema,
  hash policies, docs anchors, and show/restore checks for artifacts such as
  `best.py`, `best_workspace/`, `plugin_artifacts/`, and `paper_artifacts/`.
- Candidate execution is Python-primary. Non-Python files can be workspace
  members, metadata-only runner/build declarations can be recorded, and the
  current Python runner links to bounded environment provenance, but
  arbitrary-language runners and build-system runners are not implemented.
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

See [docs/problem-format.md](docs/problem-format.md) for the full contract.

## Example Scope

The bundled examples are intentionally small:

- Optimization-pressure seeds may be valid-but-weak or intentionally invalid
  baselines that leave room for measurable improvement.
- Neutral plateau/diversity fixtures mainly exercise loading, validation,
  artifact writing, or archive behavior.
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
