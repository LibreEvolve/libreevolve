# CLI/Packaging Module Report

Date: 2026-09-02
Module: `cli-packaging`
Wave: 1 reconnaissance and bounded delegation
Status: reconnaissance complete; remediation not complete

## Executive result

All three required component assignments were made and returned:

| Component | Agent ID | Isolated worktree | Owned write scope | Result |
|---|---|---|---|---|
| `cli` | `01a06255-ee58-7072-9503-584c753fd010` | `/mnt/c/users/timot/Documents/projects/domains/libreevolve.com-cli` | `libreevolve/cli.py` | No semantic change; focused CLI tests passed |
| `package-metadata` | `01a06255-f3c5-71a3-8d77-a921e473bc60` | `/tmp/libreevolve-package-metadata-20260902` | `pyproject.toml`, `libreevolve/__init__.py` | Root later integrated the pypdf extraction policy; build/install/package tests passed |
| `developer-tooling` | `01a06255-f827-7ba0-80ad-ec46e6e8e04d` | `/tmp/libreevolve-developer-tooling-20260902` | `.pre-commit-config.yaml`, `.gitignore`, `.secrets.baseline`, `.env.example` | No semantic change; scoped tooling checks partly passed |

This module has not reached completion. The agents found no high-confidence
bounded patch within their scopes, but identified maintainability and release
policy work that requires cross-module decisions. The root coordinator later
integrated the narrow `pypdf>=6.6,<6.11` extraction policy; it was not authored
by the package component agent and has no independent verifier result. This is
`confirmed` process evidence, not verifier approval.

The module remains locally alpha-usable under the existing contract, but is not
release-ready. Native Windows evidence, the complete non-integration suite,
and live-provider evidence remain outside this wave and are `unverified` or
intentionally skipped.

## Authority and baseline

The lead read `AGENTS.md`, the attachment supplied for this task, the local
governing prompt, `BASELINE.md`, `OWNERSHIP_MATRIX.json`, and the required
README, status, development, release, roadmap, packaging, and relevant test
surfaces before delegation.

Baseline evidence:

- Checkout: `/mnt/c/users/timot/documents/projects/domains/libreevolve.com`
- Branch: `master`
- `HEAD`: `037caa7e0e6ba9f4b60b3ae50c2c9680729c0fee`
- Upstream: `LibreEvolve/master`, with zero recorded divergence at Wave 0
- Baseline status: dirty-preserved; 273 tracked changed status records and
  one untracked orchestration item were recorded in `BASELINE.md`
- Required `py` launcher: unavailable in WSL
- Equivalent runtime: `/home/timot/.local/bin/python3.12` (Python 3.12.13),
  with `/home/timot/.local/bin/uv` (0.11.7)

The owned files were already marked modified in the dirty checkout, but the
component agents independently confirmed that their normalized content had no
semantic diff from `HEAD`. The inherited changes are line-ending-only and are
classified as `pre-existing`; they must not be mixed with future behavioral
fixes. No commit, push, merge, reset, clean, stash, or shared-checkout edit was
performed by this module.

## Findings

| ID | Severity | Evidence state | Finding and disposition |
|---|---:|---|---|
| `CLI-MAINT-001` | P2 | `confirmed`, `source-derived`, `proposed` | `libreevolve/cli.py` is 2,842 lines with 103 functions. It combines command parsing, configuration, restore validation, artifact policy, history validation, and presentation. Broad extraction is deferred until characterization tests and a safe seam plan exist. |
| `CLI-EOL-001` | P3 | `confirmed`, `pre-existing` | The owned CLI path is dirty only through line-ending representation; normalized semantic diff is empty. Quality/release owns the repository-wide EOL policy. |
| `PKGMETA-001` | P2 | `source-derived`, `test-derived`, `proposed` | `pyproject.toml` and `libreevolve.__version__` contain duplicated version literals. They currently agree, but no canonical source or consistency policy prevents drift. Deferred to root/quality-release. |
| `PKGMETA-002` | P2 | `confirmed`, `source-derived` | Runtime and dev requirements are lower-bounded without a lock or constraints contract. Exact environment replay is not established. Root/quality-release must choose and document the policy before metadata changes. |
| `PKGMETA-003` | P3 | `source-derived`, `test-derived`, `proposed` | Package metadata has no `readme` or `project.urls` fields. Index discoverability is weaker, but this is not a current runtime defect. Docs-papers and quality-release must define the public metadata contract. |
| `PKGMETA-004` | P2 | `confirmed` | The ownership matrix still has null `agent_id`/`verifier_id` for this completed component, preventing durable traceability. Root coordinator owns the matrix update; verifier remains explicitly null with the no-code-change reason. |
| `DEVTOOLS-001` | P2 | `confirmed`, `test-derived`, `pre-existing` | The detect-secrets hook rejects the dirty all-files state because the inherited `.secrets.baseline` is unstaged, despite normalized content matching `HEAD`. Preserve this staging guard; quality-release owns EOL/dirty-state policy. |
| `DEVTOOLS-002` | P2 | `source-derived`, `test-derived` | `.gitignore` ignores `/papers/*`, so newly generated JSON sidecars are silently hidden while existing tracked sidecars remain visible. Docs-papers and quality-release must choose an explicit allowlist/exception and freshness gate. No change was safe without that decision. |
| `DEVTOOLS-003` | P3 | `source-derived`, `inferred`, `unverified` | Only the repository-root `.env` is ignored. This is consistent with current documentation, but alternate dotenv filenames would need a narrowly scoped policy if they become supported. |
| `DEVTOOLS-004` | P3 | `source-derived`, `unverified` | An older revision ignored `/.tmp/`, but no current workflow or documentation requires it. No restoration is justified without current evidence. |
| `DEVTOOLS-005` | P2 | `source-derived`, `unverified` | The secrets baseline contains Windows-style paths. A clean POSIX focused scan passed, but repository-wide clean and native-Windows scans were not captured. |

## Component evidence

### CLI

The agent ran, in Python 3.12.13 with an isolated `uv` dependency
environment:

```text
uv run --no-project --with pytest>=8.0 --with pytest-mock>=3.12
  --with numpy>=1.26 --with scikit-learn>=1.4 --with anthropic>=0.25
  --with openai>=1.23 --with ollama>=0.1 --with google-genai>=2.11
  --with pyyaml>=6.0 --with click>=8.1 --with python-dotenv>=1.0
  --with packaging>=24.0 --with pypdf>=6.6,<6.11
  python -m pytest tests/test_cli.py --maxfail=1 --tb=short -q
```

Result: exit `0`; `264 passed, 2 skipped` in 240.44 seconds. CLI import and
`python -m libreevolve --help`, `run --help`, and `show --help` smoke checks
also exited `0`. No CLI source or test path changed. Native Windows execution,
full suite, live providers, and direct no-provider runtime execution were not
run by this component and remain `unverified`.

### Package metadata

The agent established the following `test-derived` and build-derived results:

- TOML and package AST parsing exited `0`.
- `python -m build --wheel --sdist` exited `0`, producing the 0.1.0 wheel and
  source distribution.
- A package-tree inventory found all 437 tracked `libreevolve/` files in both
  artifacts; the sdist contained 490 paths overall.
- Wheel, sdist, and editable installs exited `0` in isolated Python 3.12
  environments.
- Console and module CLI help, package-version equality, and a no-provider
  sorting run/show smoke exited `0`.
- Focused packaging/docs tests exited `0`: `15 passed in 6.53s`.

These are local static, build, install, and smoke results. They are not signed
provenance, package-index publication verification, native-Windows evidence,
or maintainer release approval.

### Developer tooling

The agent recorded:

| Command/check | Result |
|---|---|
| `uv run --no-project --with pre-commit>=4.5 --with detect-secrets>=1.5 python -m pre_commit validate-config` | Exit `0` |
| Dirty focused detect-secrets hook over the four owned files | Exit `1`; baseline reported unstaged |
| Clean focused detect-secrets scan of `.env.example` | Exit `0` |
| Normalized comparison of four owned files against `HEAD` | Exit `0`; all equal after CRLF normalization |
| `git diff --check` over owned files | Exit `2`; 114 EOL/trailing-whitespace diagnostics |
| `git check-ignore` for root env, runs, build/dist/egg-info, and paper paths | Intended root/build/run paths ignored; new paper JSON ignored |
| Repository-wide clean all-files secret scan | `unverified`; interrupted before final status |

No tooling configuration changed. The staging guard was not weakened and no
credential or `.env` content was read.

## Changed paths and artifacts

Agent-authored semantic changes: none. The root coordinator integrated the
documented pypdf extraction-range policy after the component report.

The only durable path authored by this module is this report:

```text
planning/maintainability_pass/reports/cli-packaging/MODULE_REPORT.md
```

The package agent created validation-only artifacts in its isolated worktree
(`dist/`, `build/`, `libreevolve.egg-info/`, and a smoke-run directory); none
are module changes or candidates for integration. The CLI and developer-tooling
agents did not leave durable component reports in this checkout; their final
messages are the source of the evidence summarized here.

## Conflicts and handoffs

No write-scope conflict occurred among the three component lanes. The following
handoffs are required before any integration decision:

1. **Root/quality-release:** record the three component agent IDs and report
   linkage in `OWNERSHIP_MATRIX.json`; keep verifier IDs null with the explicit
   no-code-change rationale. The matrix is coordinator-owned and was not edited
   here.
2. **Quality-release:** define repository EOL handling separately from
   semantic patches, retain the detect-secrets staging guard, capture clean
   POSIX and native Windows secret-scan evidence, and assess the 114
   line-ending diagnostics.
3. **Docs-papers plus quality-release:** decide the `/papers/*` allowlist or
   exception policy so newly generated sidecars cannot disappear silently;
   add a freshness check under the owning lane.
4. **Root/quality-release:** choose a version-source consistency policy and a
   lower-bound versus lock/constraints reproducibility policy before changing
   `pyproject.toml`.
5. **Docs-papers plus quality-release:** decide whether README and project URLs
   are part of the supported package-index metadata contract.
6. **Core/LLM/problems/quality-release:** the CLI agent handed off the known
   Windows/POSIX path and cancellation-policy defects, full-suite failures,
   and native-platform evidence gaps. This lane did not edit those modules.
7. **Docs-papers/problems:** the CLI agent handed off the Section 4/Section 5
   paper-inventory mismatch; the benchmark generator files remain read-only to
   this lane.
8. **Quality-release/root:** `MANIFEST.in` was audited read-only by packaging;
   any package-data policy change requires an explicit owner because it is not
   in this module's declared write scope.

## Gate ledger and residual work

| Gate | State | Evidence |
|---|---|---|
| Component assignment coverage | `confirmed` | Three required components have distinct agent IDs and disjoint scopes. |
| Static CLI/package checks | `test-derived` | CLI import/help, TOML/AST parsing passed. |
| Package build and install | `test-derived` | Wheel, sdist, editable install, artifact inventory, and local smoke passed. |
| Focused CLI tests | `test-derived` | 264 passed, 2 skipped. |
| Focused packaging/docs tests | `test-derived` | 15 passed. |
| Developer-tooling configuration validation | `test-derived` | `pre_commit validate-config` and clean focused scan passed. |
| Dirty-worktree all-files secret scan | `blocked`/`unverified` | Staging/EOL state caused failure; clean repository-wide result was not captured. |
| Independent verifier evidence | `not complete` | The root-integrated dependency policy has no independent verifier result. |
| Module-wide post-integration test | `pending` | A logged root-level rerun is active after the dependency policy integration. |
| Full non-integration suite | `pending` | The first run lost its terminal status; a replacement logged run is active. |
| Native Windows tests | `unverified` | WSL only. |
| Live provider/integration tests | `skipped` | No credentials or authorization. |
| Signed/public release verification | `unverified` | Outside local release-smoke contract. |

Residual module work is therefore policy and integration work, not an
unreviewed patch: canonicalize version ownership, decide reproducibility and
index metadata contracts, resolve paper-sidecar visibility, establish EOL and
cross-platform secret-scan gates, and split the oversized CLI only after
characterization tests identify safe seams. Root/quality-release should then
rerun the complete non-integration gate and native-platform checks. The module
must not be marked complete from the focused green checks above.
