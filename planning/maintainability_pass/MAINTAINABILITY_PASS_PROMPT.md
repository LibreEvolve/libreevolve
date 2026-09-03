# LibreEvolve Maintainability Pass: Orchestration Prompt

Copy this entire prompt into the coordinating agent. It is an execution prompt
for a bounded, evidence-driven maintainability pass over the LibreEvolve
repository. It is not evidence that the pass has been executed.

## Mission

Perform a complete maintainability pass over the current LibreEvolve checkout.
Resolve the known defects below, discover additional defects and structural
risks, and leave behind a coherent, test-backed implementation plus a durable
report. Preserve the project's documented alpha-stage scope and its explicit
evidence boundaries. Do not turn a maintainability pass into an unsupported
claim of production hardening, hostile-code sandboxing, distributed execution,
live-provider parity, benchmark reproduction, or AlphaEvolve parity.

The pass has two deliverables:

1. Safe, reviewable code/documentation/test changes, integrated only after
   independent verification.
2. `planning/maintainability_pass/MAINTAINABILITY_PASS_REPORT.md`, together
   with machine-readable ownership and findings records, describing what is
   confirmed, what remains open, and exactly which gates passed.

## Authority and operating rules

1. Read `AGENTS.md`, `README.md`, `docs/status.md`, `docs/development.md`,
   `docs/release-checklist.md`, `ROADMAP.md`, `pyproject.toml`, and the relevant
   module tests before assigning work. Treat repository source, executable test
   results, and generated-artifact validators as separate authorities.
2. Begin with a read-only baseline. Record the absolute checkout path, current
   branch, exact `HEAD`, upstream relation, `git status --short`, semantic diff
   summary using `git diff --ignore-all-space`, Python/runtime versions, and
   available test commands. Never discard, reset, clean, stash, overwrite, or
   broadly reformat the existing worktree.
3. The starting checkout may be dirty. Preserve every pre-existing change.
   Do not assume that line-ending churn is harmless until the semantic diff has
   been measured. The known baseline has hundreds of modified tracked paths,
   mostly line-ending changes, and a small set of substantive paper-inventory
   edits. Maintain a pre-existing-versus-agent-owned path ledger.
4. Do not read, print, copy, commit, or retain secrets. Do not use `.env` as
   source material. Live provider tests require explicit credentials and must
   remain opt-in; missing credentials are an evidence state, not a reason to
   weaken tests.
5. Do not commit, push, merge, publish, delete, or alter external systems
   unless the caller separately authorizes that exact action. Use explicit path
   staging if a later human asks for a commit; never use `git add -A`.
6. Prefer narrow changes over cosmetic rewrites. Do not mix line-ending
   normalization, unrelated formatting, generated-artifact regeneration, and
   behavioral fixes in one lane. Every behavior change needs a focused
   regression test and a stated compatibility decision.
7. Preserve the distinctions `confirmed`, `test-derived`, `source-derived`,
   `proposed`, `inferred`, `unverified`, `blocked`, and `pre-existing` in every
   report. Static inspection is not runtime proof; a local subprocess is not a
   hostile-code security sandbox; a smoke fixture is not a benchmark result.
8. If the current worktree contains an intentional but incomplete change, do
   not silently revert it. Isolate it, finish its dependency chain, or report
   it as blocked with the exact conflicting contract.

## Delegation topology

Use bounded nested delegation. The intended topology is:

```text
root coordinator
  └── module lead (one per module lane)
        └── component agent (one per listed component)
              └── independent verifier or red-team agent, when needed
```

- Use no more than 50 child slots concurrently and never exceed nesting depth
  3. Keep the number of active agents below the available limit rather than
  spawning an unbounded fan-out.
- Every module lead must explicitly create or queue one component agent for
  each owned component below, even when the component is small. A module lead
  may combine only components that have no overlapping files and must document
  the combination.
- Component agents own analysis and implementation only within their declared
  paths. They may inspect adjacent modules for contracts but must not edit
  another lane's ownership without a handoff recorded in the ledger.
- A verifier must not be the same agent that authored the change. It reviews
  the actual isolated diff, reruns focused tests, and checks for regressions,
  missing tests, unsupported claims, and accidental scope expansion.
- If subagent creation is unavailable or a limit is reached, use a queued
  worklist with the same ownership and verification rules. Do not skip a lane
  and do not claim parallel completion from a plan alone.
- Establish quiescence barriers: no integration begins until all affected
  component reports and verifier results exist; no final readiness decision is
  made until the complete validation wave finishes or is explicitly blocked.

## Isolation and integration

The root coordinator owns the shared checkout and the ledger. Module leads and
component agents work in isolated worktrees or copies derived from the exact
current baseline, including a clearly identified representation of relevant
dirty changes. They must not edit the shared checkout directly.

Each lane must record:

- baseline `HEAD` and dirty-diff scope;
- exact owned files/directories;
- dependency assumptions and touched public contracts;
- changed paths, including tests and generated artifacts;
- commands run and their exit status;
- verifier identity/result and unresolved findings.

Integrate lanes in dependency order using explicit, path-scoped patches. Before
and after each integration, check status and inspect the diff. Stop on an
unexpected path, conflict, deleted file, secret, broad formatting change, or
unexplained generated-file change. Resolve conflicts through the owning module
lead; never choose a conflict winner silently.

## Required initial findings backlog

Treat these as starting hypotheses to verify, not as facts to paper over:

1. Workspace materialization collision handling appears to use host-POSIX
   `normcase`, which does not model case-insensitive Windows collisions on
   POSIX. Test both native Windows behavior and deterministic cross-platform
   path semantics.
2. Runtime provenance executable-name extraction appears to use POSIX `Path`
   parsing on Windows-style paths. Test drive-letter, UNC, slash, and
   backslash forms without depending on the host OS.
3. Cancellation-policy artifact validation appears not to recognize a
   Windows-drive absolute path when running on POSIX. Test path, hash, byte,
   traversal, and symlink policies independently.
4. The paper inventory update appears partially propagated: current generators
   describe Section 5, 403 prose sentences, 985 propositions, and 286 reviewed
   sentences, while dependent tests/sidecars still expect older Section 4,
   402, 812, and 244 values. Establish one authoritative source of truth and
   regenerate or intentionally revise every dependent artifact.
5. The full non-integration suite previously exposed additional failures in
   ablation results, cached-PDF header consistency, benchmark hardening, and
   matrix results. Reproduce and diagnose them independently; do not assume
   they are all caused by line endings or by the inventory update.
6. `core/loop.py` is exceptionally large and combines orchestration, state,
   reporting, persistence, and policy concerns. Measure coupling and extract
   safe seams incrementally; do not perform an untested rewrite.
7. There are hundreds of active TODO records and many boundary sidecars. Do
   not close TODOs merely because code exists, and do not treat a sidecar,
   prompt, static scan, or passing mock test as implementation/runtime proof.
8. Check for other maintainability issues: import cycles, hidden global state,
   mutable default/config leakage, inconsistent error taxonomy, path and
   encoding assumptions, nondeterministic tests, poor cleanup, duplicate
   serialization logic, stale generated artifacts, API drift, oversized
   functions/classes, weak ownership boundaries, missing negative tests, and
   documentation that overstates evidence.

## Module leads and component ownership

Create these module leads. The file lists are starting ownership boundaries;
the root coordinator must refine them after the Wave 0 import/test inventory.

### 1. Core runtime lead — `core`

Component agents:

- **Orchestration and lifecycle:** `core/loop.py`; generation ordering,
  admission, hooks, budgets, resume/restore boundaries, and report assembly.
- **Candidate/workspace/diff:** `core/candidate.py`, `core/diff.py`;
  materialization, primary-file selection, path normalization, encoding,
  collision/traversal handling, and mutation-format compatibility.
- **Evaluation and validator policy:** `core/evaluator.py`,
  `core/validator_policy.py`; cascade stages, candidate runners, timeout/error
  contracts, metrics authority, subprocess boundaries, and cleanup.
- **Persistence and artifacts:** `core/database.py`, `core/jsonl.py`,
  `core/artifact_schema.py`, `core/best_artifacts.py`, `core/budget.py`;
  durable rows, atomicity, schema evolution, deduplication, artifact promotion,
  and budget accounting.
- **Prompt and feedback:** `core/prompt.py`, `core/feedback.py`,
  `core/meta_prompt.py`; prompt assembly, bounded context, feedback ordering,
  role contracts, token limits, and prompt-history provenance.
- **Async execution:** `core/async_sampler.py`, `core/async_evaluator.py`;
  queue bounds, cancellation, ordering, generation barriers, exception
  propagation, and the explicit non-distributed boundary.
- **Configuration and loading:** `core/config.py`, `core/yaml_utils.py`,
  `problems/loader.py` only for shared configuration contracts; defaults,
  validation, path resolution, schema drift, and error messages.
- **Provenance and redaction:** `core/provenance.py`, `core/redaction.py`;
  cross-platform identity, secret-safe telemetry, stable serialization, and
  evidence labels.

### 2. LLM/control-plane lead — `llm`

Component agents:

- **Provider base and registry:** `llm/base.py`, `backend_registry.py`,
  `client_context.py`, `provider_metadata.py`.
- **Provider adapters:** `anthropic.py`, `openai.py`, `openai_compat.py`,
  `gemini.py`, `ollama.py`, `codex_cli.py`; request/response normalization,
  capability declarations, cancellation, errors, and credential boundaries.
- **Ensemble and scheduling:** `ensemble.py`, `provider_retry.py`,
  `feedback_calibration.py`; UCB accounting, retries, stochasticity, budget
  fairness, and deterministic fake-provider tests.
- **Policy and safety:** `capability_policy.py`, `cancellation_policy.py`,
  `diagnostics_policy.py`, `budget_report.py`; artifact validation, redaction,
  retry/cancel safety, and no-credential leakage.
- **Token/request contracts:** `tokenization.py`, `request_params.py`,
  `prompt_roles.py`; provider-specific limits, reasoning controls, and
  compatibility validation.

### 3. Population lead — `population`

Component agents:

- **Program model:** `population/program.py`; identity, lineage, fitness,
  serialization, and mutation metadata.
- **MAP-Elites:** `population/map_elites.py`; descriptors, cells, replacement,
  archive invariants, and boundary conditions.
- **Islands/migration:** `population/islands.py`; explore/exploit balance,
  migration order, isolation, and reproducibility.
- **Sampling/objectives:** `population/sampling.py`,
  `population/objective_history.py`; selection policies, RNG ownership,
  multi-objective semantics, and stale-state behavior.

### 4. Plugin lead — `plugins`

Component agents:

- **Plugin contract and registry:** `plugins/base.py`, `plugins/registry.py`;
  lifecycle, optional hooks, failure policy, discovery, and compatibility.
- **Causal plugin:** `plugins/causal.py`.
- **Deep-research plugin:** `plugins/deep_research.py`.
- **Modular plugin:** `plugins/modular.py`.
- **TTT/RL plugin:** `plugins/ttt_rl.py`.
- **Shared plugin evidence:** plugin context, artifacts, configuration,
  failure isolation, and documentation/tests crossing plugin boundaries.

### 5. Problems and execution environments lead — `problems`

Component agents:

- **Problem loader and contracts:** `problems/loader.py` and task/config
  loaders; path safety, validator loading, schema errors, and ownership.
- **Python/example problems:** `problems/examples/*`; seed policy, metrics,
  validators, examples, and truthful scope labels.
- **Candidate-runner commands:** expression/C runner declarations, build and
  toolchain probes, shell-free invocation, output limits, and error records.
- **OCI path:** `candidate_runner_python_oci`, Docker/Podman detection,
  digest/runtime identity, network/resource flags, and the explicit boundary
  between process isolation and hostile-code sandboxing.
- **Benchmark fixtures:** matrix, sorting-network, circle-packing, and related
  fixtures; determinism, calibration labels, fixture drift, and result claims.
  The paper-inventory generator files owned by `docs-papers` are read-only
  dependencies for this component and require an explicit handoff for edits.

### 6. User interface and packaging lead — `cli-packaging`

Component agents:

- **CLI:** `libreevolve/cli.py`; command contracts, diagnostics, exit codes,
  path handling, output stability, and `show`/`run` behavior.
- **Package metadata:** `pyproject.toml`, package exports, build inclusion,
  Python-version/dependency declarations, and reproducible install behavior.
- **Developer tooling:** `.pre-commit-config.yaml`, `.gitignore`,
  `.secrets.baseline`, and local development commands; keep checks scoped and
  compatible with the documented workflow.

### 7. Documentation and evidence lead — `docs-papers`

Component agents:

- **User/developer docs:** `README.md`, `docs/README.md`, `docs/status.md`,
  `docs/development.md`, `docs/backends.md`, `docs/run-artifacts.md`, and
  plugin/problem guides; remove ambiguity and evidence overclaims.
- **Roadmap/TODO ledgers:** `ROADMAP.md`, `docs/todo/*`; deduplicate, assign
  ownership, distinguish implemented work from readiness gaps, and avoid
  mechanically closing records.
- **Paper source/inventory generators:** `papers/` and benchmark inventory
  generators; source spans, schema versions, cached source/PDF consistency,
  generated outputs, and reproducible regeneration.
- **Boundary sidecars and claim policy:** ensure sidecars state exact scope,
  evidence state, missing gates, and non-goals without implying completeness.

### 8. Tests, CI, and release lead — `quality-release`

Component agents:

- **Test architecture:** test ownership, collection speed, fixtures, platform
  assumptions, isolation, flaky/nondeterministic tests, and missing negative
  coverage.
- **Cross-platform contract testing:** Windows/POSIX path semantics, newline
  and encoding behavior, subprocess commands, native-vs-emulated evidence,
  and CI matrix coverage.
- **CI workflows:** `.github/workflows/tests.yml`; unit, paper/docs, release,
  secret-scan, optional integration, caching, failure visibility, and scope.
- **Release/reproducibility:** wheel/sdist smoke, artifact inventories,
  provenance, dependency lower bounds/lock strategy, and the distinction
  between local release smoke and signed/published release verification.

The quality-release lead is the final independent gatekeeper and may not mark
the project complete solely because other module leads report success.

## Component-agent contract

Every component agent must complete the following sequence:

1. Inventory public symbols, import relationships, callers, serialized
   formats, configuration inputs, tests, docs, and generated artifacts.
2. Establish a small baseline with the narrowest relevant tests before editing.
   If the baseline fails, capture the failure exactly and determine whether it
   is pre-existing, caused by the current dirty diff, environment-specific, or
   a true regression.
3. Review maintainability dimensions: cohesion, coupling, complexity, naming,
   side effects, error handling, resource cleanup, path/OS portability,
   determinism, serialization, observability, testability, and documentation
   truthfulness.
4. Turn each finding into a record with: stable ID, severity, evidence state,
   owner, exact path/line or symbol, reproduction, impact, proposed fix,
   dependencies, acceptance test, and whether it is in this pass's scope.
5. Implement only fixes that are safe within the component boundary. Add or
   update focused tests, including negative and cross-platform cases where
   relevant. For a large refactor, first introduce a seam and preserve the
   public contract; do not combine behavior changes with wholesale movement.
6. Run focused static/build/tests, inspect the actual diff, and request an
   independent verifier. Record skipped tests and why they were skipped.
7. Return a concise component report and a patch that the module lead can
   integrate without guessing.

## Module-lead contract

Each module lead must:

- maintain the module ownership map and dependency graph;
- ensure every component has a report and independent verification;
- review cross-component API and schema changes;
- prevent duplicate fixes and conflicting generated artifacts;
- run the module-level test slice after component integration;
- identify findings that require another module and create a handoff;
- classify residual risks as accepted, deferred, blocked, or out of scope;
- produce a module report with changed paths, test evidence, and open gaps.

## Required remediation priorities

Address these in this order unless the dependency graph proves otherwise:

### P0 — correctness and test health

- Fix the three diagnosed Windows/POSIX path-contract failures without making
  host-dependent tests lie. Add tests for both path grammars and run them on
  native Windows CI where applicable.
- Reproduce and resolve the ablation, cached-PDF, benchmark-hardening, and
  matrix-results failures from the prior full-suite run.
- Restore a complete, repeatable non-integration test gate. Do not report a
  final pass from a partial or interrupted run.

### P1 — contract and artifact consistency

- Establish the canonical source for paper inventory counts and section scope.
- Regenerate or intentionally revise all dependent tests, sidecars, manifests,
  and reports together. Add a stale-artifact consistency test so a future
  Section 4/Section 5 or count mismatch fails close to its source.
- Audit import cycles, API boundaries, schema versions, JSONL durability,
  config defaults, and error taxonomy across module seams.

### P1 — maintainability structure

- Measure `loop.py` and other oversized modules/functions before refactoring.
- Extract cohesive seams for orchestration, state/admission, evaluation,
  persistence, reporting, and policy while preserving behavior and provenance.
- Add characterization tests before each extraction and a module-level contract
  test after it. Record complexity/file-size deltas rather than claiming that
  movement alone improved maintainability.

### P2 — reproducibility and release hygiene

- Make the documented Python 3.12 test/install path reproducible in the
  supported environments available to CI. Assess whether a lock or an
  explicitly documented lower-bound policy is appropriate; do not invent a
  lockfile without checking project conventions.
- Separate line-ending cleanup from semantic changes and document the chosen
  policy. Keep generated artifacts reproducible and secrets scans clean.
- Strengthen CI only where it reflects an actual contract; do not make live
  provider calls mandatory or pretend that optional integration coverage is
  complete.

### P2 — explicit remaining boundaries

Review, but do not silently implement, the currently documented non-goals:
hostile-code sandboxing, distributed scheduling, pending-work resume,
provider-output replay, live Gemini Flash/Pro parity, benchmark reproduction,
signed publication, and AlphaEvolve-scale evidence. Convert unclear wording
into explicit status/roadmap entries with owners and acceptance criteria.

## Verification gates

The root coordinator must run and record, using the repository's documented
Python 3.12 command or a clearly equivalent environment:

1. Syntax/import gate for the package and changed modules.
2. Focused tests for every changed component.
3. Module-level tests after each module lane is integrated.
4. Full non-integration suite:

   ```bash
   py -3.12 -m pytest tests/ -m "not integration" --tb=short
   ```

5. Integration tests only when credentials and explicit authorization exist;
   otherwise record them as `unverified`, not passed:

   ```bash
   py -3.12 -m pytest tests/integration/ -m integration
   ```

6. Package/build and CLI smoke gates described by `docs/development.md`,
   `.github/workflows/tests.yml`, and `docs/release-checklist.md`.
7. Paper/docs/manifest validators, including generated-artifact freshness and
   source-span consistency.
8. Diff hygiene: no unexpected files, no secrets, no accidental broad
   line-ending rewrite, no deleted user work, and no unsupported evidence
   claims.

If the documented `py` launcher is unavailable, use the closest Python 3.12
interpreter only after recording the deviation. A WSL/POSIX emulation of a
Windows path test does not replace native Windows evidence.

## Durable output contract

Create these files under `planning/maintainability_pass/` as the pass proceeds:

- `BASELINE.md` — exact starting state, environment, dirty-diff classification,
  and known failures;
- `OWNERSHIP_MATRIX.json` — module/component ownership, paths, dependencies,
  agent IDs, status, and verifier IDs;
- `findings.jsonl` — one normalized record per finding, including closed and
  deferred findings;
- `reports/<module>/<component>.md` — component reports;
- `reports/<module>/MODULE_REPORT.md` — module-level synthesis;
- `MAINTAINABILITY_PASS_REPORT.md` — final lead report.

The final report must contain:

- an executive verdict: alpha-usable, release-ready, paper-ready, or blocked,
  with separate labels where those differ;
- baseline and changed-path summary;
- a module-by-module table of findings, fixes, tests, and residual risks;
- exact commands, environment, durations where useful, and exit statuses;
- a closed/open/deferred/blocked finding ledger;
- maintainability measurements before and after any refactor;
- test and CI evidence separated into static, build, runtime, and end-to-end;
- explicit unsupported claims and remaining non-goals;
- follow-up work with owner, dependency, and acceptance criterion;
- the exact final Git status and whether any commit/push was performed.

Do not write “complete” unless the applicable gates actually passed. If the
full suite is interrupted, if a verifier is missing, or if a live/runtime gate
is unavailable, say so plainly and preserve the evidence state.

## Root coordinator start instruction

Start now with Wave 0 only: read the governing documents, capture the baseline,
build the ownership/dependency matrix, and identify conflicts caused by the
dirty checkout. Then spawn the eight module leads and require each lead to
spawn its component agents according to the topology above. Report progress by
wave and evidence state, not by agent count. Do not integrate code until the
first component reports and independent verification results are complete.
