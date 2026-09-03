# LibreEvolve maintainability pass report

Date: 2026-09-02
Checkout: `/mnt/c/users/timot/documents/projects/domains/libreevolve.com`
Baseline: `037caa7e0e6ba9f4b60b3ae50c2c9680729c0fee` on `master`
Report status: interim; final broad-gate status pending

## Executive verdict

**Alpha-usable: supported by substantial local test and build evidence.**

**Release-ready: not established. Paper-ready: not established.** The
repository has a coherent, testable alpha implementation, but the maintainability
pass is not complete because the independent-verifier wave was stopped, the
first broad test run lost its terminal status, the replacement run is still
pending, native Windows/live-provider/live-OCI evidence is unavailable, and
repeat builds are not byte-identical.

This report deliberately separates static, build, runtime, and end-to-end
claims. It does not claim production hardening, hostile-code sandboxing,
distributed execution, provider parity, benchmark reproduction, or
AlphaEvolve parity.

## Baseline and worktree

Wave 0 recorded:

- checkout `/mnt/c/users/timot/documents/projects/domains/libreevolve.com`;
- branch `master`, exact `HEAD` `037caa7e0e6ba9f4b60b3ae50c2c9680729c0fee`;
- upstream `LibreEvolve/master`, divergence `0 0`;
- 273 tracked changed status records and one untracked orchestration prompt;
- approximately 1,221 insertions and 87 deletions in the initial semantic
  diff, with substantial inherited line-ending churn;
- 368 package Python files, 330 test Python files, and 522 active TODOs;
- Python 3.12.13 at `/home/timot/.local/bin/python3.12`; the documented
  `py -3.12` launcher is unavailable in WSL; tests use isolated `uv`;
- no commit, push, merge, reset, clean, stash, deletion, or external-system
  mutation.

The current checkout remains dirty. Existing changes are preserved; no clean
working-tree or narrow final-diff claim is made. The exact current status is
the output of `git status --short` captured at report assembly, with the
semantic summary recorded separately in `BASELINE.md`.

## Changes integrated in this pass

The root coordinator integrated only narrow, regression-backed changes:

- candidate workspace materialization uses NFC-normalized, case-folded
  relative-path collision keys and tests both path grammars;
- evaluator preflight forwards top-level declared data include/exclude policy;
- provenance executable basename extraction handles POSIX, Windows drive, and
  UNC forms portably;
- cancellation artifact validation rejects unsafe POSIX/Windows absolute,
  drive, root, traversal, redaction-changing, and in-root symlink paths;
- benchmark ablation, hardening, and matrix validators share a safe-relative
  path policy;
- authoritative Section 5 paper inventories and six sidecars were regenerated
  with exact freshness tests;
- cached-PDF extraction policy is bounded to `pypdf>=6.6,<6.11` and documented.

These changes were integrated after focused checks. Independent reviews now
cover the cancellation path policy and the paper/inventory slice, but the
verifier requirement remains incomplete for the broader integrated surface;
that process gap is recorded as `MP-015`.

## Module synthesis

| Module | Result | Confirmed evidence | Remaining gap |
|---|---|---|---|
| core | partial | candidate 265 passed; evaluator 283 passed; provenance 110 passed/1 skipped | loop/persistence/prompt refactors and independent verification |
| llm | partial | cancellation 20 passed; provider slices were isolated | live providers, broad LLM failure, verifier |
| population | isolated partial | focused program/population evidence reported | no integrated patch or complete verifier |
| plugins | isolated partial | no shared behavior change | complete plugin contract/evidence gate |
| problems | partial | benchmark/path slice 165 passed; OCI boundary checks passed | runner/Python final gates and live OCI |
| cli-packaging | partial | CLI 264 passed/2 skipped; build/install/help smoke passed | repeat-build parity, clean secret scan, metadata policy |
| docs-papers | partial | expanded paper/inventory slice 50 passed; current counts synchronized; focused independent review | complete sidecar visibility and manifest gate |
| quality-release | pending final gate | CI-focused checks 26 passed; logged broad run active | terminal full-suite result, native Windows, release evidence |

Detailed component reports and the ownership ledger are under
`planning/maintainability_pass/reports/` and
`planning/maintainability_pass/OWNERSHIP_MATRIX.json`.

## Findings ledger

Closed for the tested contract:

- `MP-001`: cross-platform candidate materialization collision semantics;
- `MP-002`: Windows-style provenance executable names;
- `MP-003`: cancellation artifact path safety;
- `MP-004`: current paper inventory/sidecar consistency;
- `MP-012`: direct evaluator declared-data preflight;
- `MP-013`: shared benchmark artifact path policy;
- `MP-014`: cached-PDF dependency extraction policy.

Open or pending:

- `MP-005`: targeted historical failures are addressed, but the complete
  logged non-integration gate still lacks a terminal result;
- `MP-006` and `MP-011`: oversized orchestration and other high-complexity
  modules/functions need measured, characterized seam extraction;
- `MP-007`: 522 TODO/sidecar records need evidence-aware ownership and
  acceptance criteria;
- `MP-008`: additional cross-module maintainability audit remains incomplete;
- `MP-009` and `MP-010`: naive static-cycle reports were explained as
  function-local lazy-import artifacts; module-level and fresh-process import
  checks passed;
- `MP-015`: independent verifier evidence is incomplete; two focused scopes
  now have non-authoring review, but most integrated components remain without
  a completed verifier.
- `MP-016`: repeated builds were not byte-identical;
- `MP-017`: `/papers/*` ignore behavior can hide generated sidecars;
- `MP-018`: version/dependency replay policy is not canonicalized;
- `MP-019`: no verified coordinator-to-MCP-to-gateway-to-mod-to-effect-witness
  runtime trace exists.

## Measurements

The static baseline found:

| Path | Measurement |
|---|---:|
| `core/loop.py` | 49,605 lines; 804 functions; `evolve()` about 1,196 lines |
| `tools/paper_manifest.py` | 15,430 lines; largest function about 527 lines |
| `core/prompt.py` | 11,952 lines; largest function about 807 lines |
| `core/database.py` | 11,841 lines; largest class about 1,008 lines |
| `problems/benchmarks/matrix_results.py` | 7,550 lines |
| active TODOs | 522 |

No large refactor was integrated, so there is no honest before/after
complexity reduction to report. File movement without characterization tests
would not satisfy the pass.

## Verification evidence

### Static

- AST parsing of all 368 package Python files: 0 parse errors.
- A naive all-import static analysis reported two multi-module cycles. A
  module-level graph reports zero SCCs, and a fresh process imported all 15
  affected modules successfully; the lazy imports are retained intentionally.
- Focused JSON/sidecar freshness and validator checks passed as listed in the
  module reports.

### Focused and module slices

- candidate/diff/evaluator slice: `265 passed in 3.60s`;
- evaluator/validator-policy slice: `283 passed in 28.75s`;
- provenance: `110 passed, 1 skipped in 50.09s`;
- cancellation policy: `20 passed in 1.31s`; an independent recheck also
  passed `20 passed in 1.37s`;
- benchmark/path remediation slice: `165 passed in 12.65s`;
- paper/inventory boundary/freshness slice: `50 passed in 55.62s`; an
  independent paper review confirmed exact counts and source/sidecar scope;
  sidecar semantics remain unverified;
- CLI: `264 passed, 2 skipped`;
- configuration/loader and population/plugin slices are recorded in their
  component reports and were not complete independent gates.

### Build and packaging

Local wheel, sdist, editable-install, package-inventory, version, and CLI-help
smokes passed in isolated Python 3.12 environments. Repeat builds were not
byte-identical. This is local build evidence, not signed/public release
verification.

### Broad non-integration suite

The first run collected 6,334 items, selected 6,331, and lost its process
handle before a recoverable terminal summary; it is `interrupted/unverified`.
A replacement run started at `2026-09-02T20:28:29-04:00`, collected the same
6,331 selected tests, and is durably logged under
`/tmp/libreevolve-maintainability-full-OcdAeH/`; it was interrupted at 28%
after a verifier found an embedded-NUL cancellation-path defect. It has no
terminal gate result and is not evidence of a pass. A corrected run is now
active under `/tmp/libreevolve-maintainability-full-corrected-2DyZG7/`; it
collected 6,337 items, selected 6,334 after the same three deselections, and
had reached 28% with no logged failure at report refresh. Its terminal status
remains pending.

### Runtime and end-to-end

- Native Windows execution: `unverified` (WSL only).
- Live provider/integration tests: intentionally skipped without explicit
  credentials and authorization.
- Live OCI daemon fixture: `unverified`; opt-in only.
- Coordinator → MCP → gateway → mod → effect-witness trace: missing.
- Host subprocess and OCI process isolation: not a hostile-code security
  sandbox claim.

## Unsupported or deferred claims

This pass does not promote the documented non-goals: hostile-code sandboxing,
distributed scheduling, pending-work resume, provider-output replay, live
Gemini Flash/Pro parity, benchmark reproduction, signed publication, or
AlphaEvolve-scale evidence.

## Follow-up work

1. Quality-release: capture the terminal status of the logged full suite and
   rerun it after any subsequent source change.
2. Quality-release: execute native Windows path/subprocess/encoding tests and a
   clean repository-wide secret scan in a clean representation of the checkout.
3. Root plus module owners: obtain independent verifier reviews for every
   integrated patch and record them in the matrix.
4. Core: add characterization tests, then extract loop orchestration, state,
   persistence, reporting, and policy seams with measured complexity deltas.
5. Docs/quality: define the `/papers/*` allowlist/freshness policy and
   reconcile TODO ownership without mechanical closure.
6. Packaging/release: define version-source and lock/constraints policy and
   explain or eliminate non-deterministic build outputs.
7. Runtime owners: produce an authorized, repeatable boundary trace or mark
   the runtime integration gap as an explicit accepted non-goal.

## Current Git/result status

No commit or push was performed. The checkout is intentionally left dirty with
pre-existing and pass-owned changes intermingled; no destructive cleanup was
used. The broad gate is not yet a pass, so this report must not be read as a
release approval or as a statement that the maintainability pass is complete.
