# LibreEvolve File-Parallel Maintainability Refactor Prompt

Copy this entire prompt into the coordinating agent. It orchestrates a
maintainability refactor of very large Python files. It is an execution plan,
not evidence that any refactor, test gate, or pull request has succeeded.
The existing maintainability-pass records are inputs and historical evidence;
do not overwrite them or treat this prompt as permission to mutate the shared
checkout, merge a PR, or make an external release.

## Mission

Refactor the remaining maintainability hotspots in the current LibreEvolve
checkout while preserving behavior, public contracts, serialized artifacts,
evidence boundaries, and the project's documented alpha-stage scope.

The work must be parallel by file and reviewable by pull request:

1. Start one independent file lane for every primary file in the target
   manifest below. Run independent file lanes concurrently whenever the global
   scheduler has capacity.
2. For very large files, run several read-only slice specialists for the same
   file concurrently. Slice specialists analyze different symbol/range
   boundaries and cross-check shared state; they do not edit the same file.
3. Permit only one implementation writer for a primary file at a time. The
   file lead integrates that file's design and patch in an isolated worktree.
4. Create a separate PR for each individual primary file. Never combine two
   primary files in one PR. A PR may contain only the directly required tests,
   migration shims, new seam modules, or generated support artifacts for its
   one primary file; list every support path explicitly.
5. If a refactor needs coordinated changes to another primary file, create a
   dependency edge and a separate PR for that file. Do not silently edit the
   other lane or hide a cross-file change in the first PR.
6. Do not merge any PR until its independent verifier has approved the actual
   diff and the dependency graph permits it. Opening a draft PR and merging a
   PR are separate actions; merge only when the caller has authorized merging.

The result is not complete merely because code moved or local tests passed.
Each PR must show characterization tests before movement, preserved contracts,
measured complexity/file-size deltas, focused and module-level verification,
and an independent non-authoring review.

## Authority and safety rules

Before delegating, read the following repository-local authorities:

- `AGENTS.md`, `README.md`, `docs/status.md`, `docs/development.md`,
  `docs/release-checklist.md`, `ROADMAP.md`, and `pyproject.toml`;
- `planning/maintainability_pass/BASELINE.md`;
- `planning/maintainability_pass/MAINTAINABILITY_PASS_REPORT.md`;
- `planning/maintainability_pass/OWNERSHIP_MATRIX.json` and
  `planning/maintainability_pass/findings.jsonl`;
- the existing module reports under
  `planning/maintainability_pass/reports/`;
- `docs/configuration.md`, `docs/run-artifacts.md`, `docs/problem-format.md`,
  `docs/plugins.md`, and `papers/README.md` when their contracts are touched;
- the tests that call or validate each owned file.

Treat source, executable tests, generated-artifact validators, and runtime
traces as separate authorities. Preserve the labels `confirmed`,
`test-derived`, `source-derived`, `proposed`, `inferred`, `unverified`,
`blocked`, `deferred`, and `pre-existing` in findings and reports.

The starting checkout may be dirty. The root coordinator must capture a
read-only baseline with absolute path, branch, exact `HEAD`, upstream relation,
`git status --short`, semantic diff summary, runtime versions, and available
test commands. Preserve all pre-existing changes. Never reset, clean, stash,
discard, broadly reformat, or overwrite the shared checkout. Never use
`git add -A`.

Do not read, print, copy, or retain `.env`, API keys, tokens, credentials, or
other secrets. Optional provider/integration tests remain opt-in. A WSL or
POSIX emulation of Windows paths is not native-Windows evidence. A local
subprocess is not a hostile-code security sandbox. A smoke fixture is not
benchmark reproduction or AlphaEvolve parity.

Every agent works in an isolated worktree or fresh copy. Agents may inspect
adjacent files for contracts, but may edit only their declared lane. The root
coordinator owns the shared checkout, PR index, dependency graph, and final
decision. No agent may make an unrecorded external change.

## Contracts that must remain explicit

Before proposing a seam, the file lead must write down which of these
repository-specific contracts it touches and how the characterization tests
prove preservation:

- `VALID_THRESHOLD = 0.0` is only the pre-admission validity gate. A finite
  score at or above zero may reach `ProgramDatabase.admit()`, but cell
  replacement can still reject it (for example, `not_improving_cell`); only
  retained/search-state entries are sampling-eligible.
- Default `mixed` parent selection is 30% explore and 70% exploit. Explicit
  parent-selection strategies bypass that ratio.
- `async_llm_sampling` and `async_candidate_evaluation` are separate bounded
  local queues. Shared archive, history, budget, admission, and hook effects
  remain ordered by the owning main-thread reducer; optional generation
  windows do not establish distributed execution or pending-work resume.
- Candidate execution is host subprocess evidence unless the declared OCI
  path is selected. OCI records must retain image/runtime identity and bounded
  provisioning evidence, but do not imply a hostile-code sandbox, daemon
  locality, platform parity, or cross-host replay.
- Seed-workspace primary-file selection honors `initial_programs/seed_policy.yaml`
  `primary_file`, then the documented `main.py`, `seed.py`, first-Python-path
  fallback. Non-Python primaries export through `best_workspace/`; `best.py` is
  compatibility output.
- JSON/JSONL keys, schema versions, artifact names, bounded/redacted retention,
  RNG ownership, deterministic ordering, plugin hook order, and evaluator
  metric authority are compatibility contracts, not incidental implementation
  details.

## Delegation topology and scheduler

Use this bounded topology:

```text
root coordinator
  └── family/module lead
        └── file lead (one per primary file and one PR lane)
              ├── slice and contract specialists (read-only analysis)
              ├── characterization-test specialist
              ├── implementation specialist (single writer)
              └── independent verifier/red-team specialist
```

- Never exceed 50 active child slots or nesting depth 3, counting the root as
  depth 0; root → module lead → file lead → specialist is the deepest allowed
  path.
- Start all independent file leads concurrently where capacity permits. Queue
  additional slice specialists rather than skipping a file lane.
- For a file over 10,000 lines, assign at least four read-only specialists; for
  a file over 30,000 lines, assign six to eight specialists. Smaller files get
  at least two specialists when their contracts cross module boundaries.
- Specialists for one file may run simultaneously, but only one agent may
  write the primary file. The verifier must be a different agent from the
  implementation writer and must inspect a fresh copy of the actual patch.
- No file lead may declare its lane complete until all slice reports, the
  characterization report, implementation report, and verifier result exist.
- If agent capacity is unavailable, use a persistent queued worklist with the
  same ownership, evidence, and PR rules. Do not claim parallel completion
  from a plan alone.

## Primary file and slice manifest

The following are separate PR lanes even when they belong to one family. The
file lead must refine the slice anchors after AST/import/caller inventory. Use
symbol names and stable anchors rather than trusting line numbers in a file
that is changing.

This is an initial target manifest, not permission to assume that a path is a
hotspot or to edit every related file. Inventory may add a necessary adjacent
lane, but it must record the new primary path and dependency edge before any
edit. Every individual path below gets its own `FILE_MATRIX.json` row, file
lead, branch/PR identity, verifier, and changed-path allowlist. A component
grouping used for reconnaissance never authorizes a multi-file PR.

### Core orchestration family

#### `libreevolve/core/loop.py` — highest priority, approximately 49,605 lines

The current reported baseline is 49,605 physical lines, 804 functions, and an
`evolve()` symbol of about 1,196 lines; remeasure in the actual lane before
designing a seam and treat the live inventory as authoritative.

Run several specialists concurrently over these overlapping contract slices:

- **Loop setup and lifecycle:** configuration normalization, run initialization,
  seed/restore selection, generation boundaries, and shutdown/finalization.
- **Sampling and mutation:** parent selection, prompt preparation, mutation
  format selection, proposal ordering, duplicate handling, and RNG ownership.
- **Evaluation coordination:** cascade stages, async evaluation, timeouts,
  cancellation, exception propagation, and generation barriers.
- **Admission and state:** validity threshold, database admission, MAP-Elites
  replacement, sampling eligibility, budgets, and reward/accounting updates.
- **Hooks and feedback:** plugin hook ordering, feedback context, prompt
  history, failure memory, and provenance propagation.
- **Persistence and restore:** JSONL rows, run manifests, best artifacts,
  resume/restore validation, atomicity, and compatibility with old artifacts.
- **Reporting and observability:** history/failure/quarantine streams, summary
  assembly, telemetry, redaction, evidence labels, and final status.
- **Cross-cutting call graph:** all mutable state, shared helpers, imports,
  callers, public entry points, and edges between the preceding slices.

The first implementation should introduce characterization seams around
ordering, admission, hooks, budgets, restore, artifact promotion, feedback
bounds, cancellation, and report assembly. Extract cohesive helpers or modules
incrementally; do not rewrite `evolve()` wholesale.

### Persistence and artifact family

Each file below has its own file lead and PR. The family lead coordinates
schema and dependency edges without combining their PRs.

- `libreevolve/core/database.py`: archive model, admission/replacement,
  lineage, cell identity, sampling eligibility, serialization, and restore.
- `libreevolve/core/jsonl.py`: append/flush/atomicity, malformed-row policy,
  schema/version handling, recovery, and durable ordering.
- `libreevolve/core/artifact_schema.py`: schema definitions, validation,
  compatibility, migrations, redaction, and error taxonomy.
- `libreevolve/core/best_artifacts.py`: promotion, workspace export,
  primary-file selection, collision/path policy, and provenance.
- `libreevolve/core/budget.py`: budget reservation, cumulative limits,
  retries, asynchronous accounting, cancellation, and reporting.

### Prompt and feedback family

Each file below has its own file lead and PR. Specialists must trace the
contract into callers and providers before movement.

- `libreevolve/core/prompt.py`: prompt assembly, bounded context, failure
  memory, token budgeting, role contracts, and prompt-history provenance.
- `libreevolve/core/feedback.py`: feedback ordering, metric/diagnostic
  rendering, truncation/redaction, and evaluator-to-LLM boundaries.
- `libreevolve/core/meta_prompt.py`: meta-prompt construction, provider
  context, scoring metadata, and compatibility with prompt templates.

### Evidence, tooling, and user-interface family

- `libreevolve/tools/paper_manifest.py`: source inventory extraction, cached
  source/PDF handling, source-span validation, sidecar freshness/schema checks,
  claim evidence, and report generation.
- `libreevolve/cli.py`: command parsing, configuration/preflight, restore and
  history validation, artifact policy, diagnostics/exit codes, output
  formatting, and `run`/`show` presentation.

### Secondary benchmark and contract family

- `libreevolve/problems/benchmarks/matrix_results.py`: result schema,
  fixture orchestration, artifact inventory, source/rights evidence,
  serialization, and validation boundaries.
- Related benchmark fixture files discovered by the inventory: each newly
  selected primary file receives its own PR and its own verifier.
- `libreevolve/core/config.py`: defaults, schema validation, path resolution,
  environment loading, error messages, and compatibility.
- `libreevolve/core/yaml_utils.py`: YAML parsing, normalization, schema/error
  behavior, and shared configuration boundaries.
- `libreevolve/problems/loader.py`: problem/task loading, validator loading,
  path safety, ownership, and cross-module configuration contracts.

The root coordinator must add file lanes for any adjacent file that is proven
necessary by the call graph. Such additions must be recorded before editing,
with one primary file and one PR per added lane. “Related” does not authorize
a combined multi-file PR. Existing dirty changes and already-integrated fixes
are baseline inputs to classify, not silent support paths for a refactor.

## Large-file slicing protocol

For every large file, the file lead must create a slice map before edits. Each
slice record contains:

- `slice_id`, primary path, stable symbol/range anchors, and approximate lines;
- assigned specialist and read-only status;
- inbound callers, outbound calls, imports, mutable state, schemas, and tests;
- public/serialized/error contracts touched;
- neighboring slices that must be reviewed together;
- characterization tests required before movement;
- proposed seam and dependency direction;
- unresolved questions and evidence state.

Partition on AST symbols, classes, methods, and phases—not arbitrary line
chunks. Include one overlapping boundary review for every adjacent pair. For
the 1,000+ line `evolve()` orchestration path, map phases and state transitions
explicitly before proposing extraction. No specialist may conclude that a
slice is independent merely because its functions are far apart in the file.

The cross-cutting specialist must build a symbol/caller/state graph and look
for hidden coupling: module globals, mutable defaults, closure state, implicit
ordering, monkeypatch seams, serialized keys, exception types, environment
variables, filesystem assumptions, and lazy imports.

## File-lane contract

Every file lead must complete these gates in order:

1. **Inventory:** record symbols, callers, imports, public entry points,
   serialized formats, configuration inputs, docs, generated artifacts, and
   existing tests. Measure physical lines, logical lines, function/class
   counts, largest symbols, complexity proxies, import fan-in/fan-out, and
   duplicated responsibilities.
2. **Baseline:** run the narrowest relevant tests in an isolated environment.
   Classify failures as pre-existing, dirty-diff-related, environment-specific,
   or regression. Do not repair a baseline failure by weakening its assertion.
3. **Characterization:** add or identify tests for externally observable
   behavior before moving code. Cover normal, negative, boundary, error,
   cleanup, deterministic, and cross-platform cases relevant to the file.
4. **Design:** produce a seam plan with invariants, ownership, dependency
   direction, API compatibility, migration strategy, and rollback point.
   Prefer one cohesive seam per PR phase over a cosmetic split.
5. **Implementation:** one writer makes a narrow refactor in the file lane.
   Preserve names or add compatibility shims where needed. Do not combine
   unrelated behavior changes, line-ending conversion, generated-artifact
   churn, or broad formatting with the extraction.
6. **Verification:** run syntax/import, focused, module-level, and relevant
   build/CLI/artifact checks. Inspect the actual diff for unexpected paths,
   deleted user work, imports cycles, schema drift, and evidence overclaims.
7. **Independent review:** a non-authoring verifier reruns the focused tests,
   checks characterization coverage and before/after measurements, reviews
   public/serialized contracts, and performs a red-team pass for hidden
   coupling, behavior changes, cleanup failures, and unsupported claims.
8. **PR packet:** return one PR packet for this primary file only. It must
   include the patch, changed-path allowlist, dependency edges, exact commands
   and exit statuses, measurements, verifier identity/result, residual risks,
   and rollback instructions.

## Refactor design rules

- Preserve public APIs, CLI exit codes, serialized keys/schema versions,
  artifact paths, plugin hook ordering, evaluator metric authority, and
  provenance/redaction behavior unless a separate approved behavior change is
  explicitly recorded.
- Keep dependency direction explicit. New seam modules must not create import
  cycles or move policy authority into a lower-level utility accidentally.
- Keep ownership of mutable state visible. Pass state through narrow objects or
  explicit parameters rather than introducing new hidden globals.
- Preserve deterministic ordering and RNG ownership. Characterize async and
  cancellation behavior before extracting it.
- Keep filesystem/path grammar and encoding decisions platform-independent
  where the contract is cross-platform. Native-Windows evidence remains a
  separate gate.
- Preserve bounded/redacted prompt, telemetry, failure-history, and artifact
  records. Never use a test secret or `.env` content as fixture material.
- Do not close TODOs, roadmap items, or evidence-boundary sidecars merely
  because code moved. Change their status only with an owner, exact acceptance
  evidence, and a disposition that preserves unresolved scope.
- Avoid “god object” replacement: a large function moved into a large class is
  not a maintainability improvement without measured cohesion/coupling gains.
- Record before/after physical LOC, logical LOC, largest symbol, complexity
  proxy, import fan-in/fan-out, and test coverage for the touched seam. Explain
  any metric that worsens.
- If a design requires behavior changes in another file, stop at a handoff,
  create that file's separate PR lane, and document the dependency rather than
  editing across ownership boundaries.

## PR contract: one individual file per PR

Use a branch and PR identity that names exactly one primary file, for example:

```text
refactor/core-loop
refactor/core-database
refactor/core-prompt
refactor/paper-manifest
refactor/cli
```

For staged phases on the same huge file, use a numbered branch/PR sequence and
make later PRs depend on earlier ones; never create simultaneous competing
writes to that file. Each PR description must contain:

- primary file and exact support paths;
- slice IDs and responsibilities addressed;
- baseline and post-refactor measurements;
- preserved behavior and compatibility decisions;
- characterization and regression tests;
- commands, environment, duration where useful, and exit statuses;
- independent verifier identity, clean/fresh checkout, and result;
- dependency PRs, risks, rollback plan, and explicitly unverified evidence;
- a statement that no unrelated dirty paths were staged.

Open a draft PR only after the file-lane quiescence barrier passes. Do not
merge it until required dependent PRs, the independent verifier, and the
root-selected validation wave pass. Never force-push, rewrite another lane's
branch, or close an unresolved finding to make a PR mergeable.

## Verification waves

The root coordinator must run and record these waves:

### Wave 0 — baseline and ownership

- capture exact Git/runtime state and preserve the dirty-path ledger;
- build `FILE_MATRIX.json`, `SLICES.jsonl`, and a dependency graph;
- verify that every primary file has a file lead and a queued specialist set;
- identify pre-existing edits that overlap proposed support paths.

### Wave 1 — parallel inventory and characterization

- run all independent file lanes concurrently where capacity permits;
- complete slice maps, call/state graphs, complexity measurements, and baseline
  tests;
- add characterization tests in isolated branches before any extraction;
- stop and hand off conflicts instead of allowing two writers to guess.

### Wave 2 — parallel seam implementation

- implement only after the file's characterization barrier passes;
- respect dependency order for shared schemas/configuration while keeping PRs
  separate;
- run focused tests after every seam and preserve a rollback point;
- maintain one writer per primary file.

### Wave 3 — independent verification and PR packets

- assign a fresh non-authoring verifier to every PR;
- rerun focused and module-level checks from the actual PR diff;
- perform red-team review for hidden coupling and unsupported evidence;
- open separate draft PRs only for lanes that pass their local gate.

### Wave 4 — root integration and final evidence

- integrate only through explicit, path-scoped PR merges after authorization;
- check status and diff before/after each merge;
- run the complete non-integration suite after the final dependency wave;
- run package/build, CLI, paper/docs, artifact-freshness, and diff-hygiene
  gates;
- record native-Windows, provider, OCI, and end-to-end boundaries separately.

## Required test and evidence gates

Use the documented Python 3.12 command, or record an exact equivalent if the
launcher is unavailable:

```bash
py -3.12 -m pytest <focused-tests> --tb=short
py -3.12 -m pytest <module-tests> --tb=short
py -3.12 -m pytest tests/ -m "not integration" --tb=short
```

For every PR, record at minimum:

- syntax/import checks for changed modules;
- characterization and focused regression tests;
- module-level contract tests;
- schema/serialization/artifact freshness tests where applicable;
- `git diff --check`, changed-path review, and secret-scan result without
  reading `.env`;
- package/build/CLI checks when the file affects packaging or user interface.

Run integration/provider tests only with explicit credentials and authorization.
Record unavailable native-Windows, live-provider, OCI, or runtime-trace gates
as `unverified`; do not convert them into passes with mocks or WSL emulation.

The full suite is a terminal gate, not a progress percentage. If it is
interrupted, loses its process handle, lacks an exit status, or runs against a
different source state, classify it `interrupted/unverified` and rerun it.

## Durable coordination artifacts

Maintain these files under `planning/maintainability_pass/refactors/`:

These are additive execution records for this refactor. Do not overwrite the
parent pass files in `planning/maintainability_pass/` (especially its baseline,
ownership matrix, findings ledger, reports, or final report); link or copy
only sanitized, scoped evidence when a new record needs it.

- `BASELINE.md` — exact Wave 0 state and dirty-path classification;
- `FILE_MATRIX.json` — family/file ownership, agent IDs, branch/PR, status,
  dependencies, changed-path allowlist, verifier ID, and evidence state;
- `SLICES.jsonl` — symbol/range maps, cross-slice edges, and characterization
  requirements;
- `FINDINGS.jsonl` — normalized findings with severity, evidence state, owner,
  path/symbol, impact, acceptance test, and disposition;
- `reports/<file-slug>/INVENTORY.md` — file and slice analysis;
- `reports/<file-slug>/CHARACTERIZATION.md` — behavior contract and tests;
- `reports/<file-slug>/REFACTOR.md` — design, measurements, and changed paths;
- `reports/<file-slug>/VERIFICATION.md` — independent review and commands;
- `PR_INDEX.jsonl` — one record per individual-file PR;
- `FINAL_REPORT.md` — final readiness and unresolved boundaries.

The final report must distinguish static, build, runtime, and end-to-end
evidence; include before/after measurements; list every PR and dependency;
identify all open/deferred/blocked findings; and state the exact final Git
status. Do not claim a refactor is complete when a verifier is missing, a
required test gate is interrupted, or the evidence scope is narrower than the
claim.

## Root coordinator start instruction

Start with Wave 0 only. Read the governing documents, capture the baseline,
create the family/file matrix and queued slice worklist, and report the dirty
path conflicts. Then start every independent file lead concurrently where the
50-slot scheduler permits. For `core/loop.py`, immediately queue six to eight
read-only slice specialists plus a cross-cutting reviewer. Do not allow any
implementation writer to edit until that file's characterization and seam
barriers are recorded. Do not combine primary files in a PR, and do not call
the project or any file lane complete until the required independent
verification and terminal validation evidence exists.
