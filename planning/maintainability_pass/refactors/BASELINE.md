# Maintainability Refactor Wave 0 Baseline

Captured: 2026-09-03T20:26:03-04:00
Checkout: `/mnt/c/users/timot/documents/projects/domains/libreevolve.com`
Branch: `master`
HEAD: `7983544e28e478eb6a0f5c35e4af5a86b125cea2`
Upstream: `LibreEvolve/master`
Divergence: `0 0`

## Dirty-worktree boundary

This snapshot was captured before the coordinator created the additive
`planning/maintainability_pass/refactors/` ledger. The pre-existing checkout
had 260 tracked/index status records and one untracked record: the requested
`planning/maintainability_pass/MAINTAINABILITY_REFACTOR_ORCHESTRATION_PROMPT.md`.
The normalized semantic diff was empty (`0` files, `0` additions, `0`
deletions); representation changes remain pre-existing and are not an
authorization to reformat or overwrite any path.

The exact status command for the path-level ledger was:

```text
git status --porcelain=v1 --untracked-files=all
```

The path-only snapshot is preserved in `refactors/DIRTY_PATHS.md`. It contains
261 baseline rows (260 tracked/index and one untracked prompt) and excludes
only the coordinator records created after the snapshot.

All pre-existing status records are preserved. No reset, clean, stash,
checkout, deletion, broad staging, commit, push, merge, or external release
action is part of this refactor wave. The coordinator must inspect status and
the scoped diff before and after every lane integration. Coordination files
created after this snapshot are coordinator-owned additions and must not be
confused with the pre-existing dirty baseline.

## Runtime and test commands

- Required documented launcher: `py -3.12` (not available in this WSL shell).
- Recorded equivalent: `/home/timot/.local/bin/python3.12` (Python 3.12.13).
- Recorded package runner: `/home/timot/.local/bin/uv` (0.11.7).
- Documented focused and full commands are `py -3.12 -m pytest ... --tb=short`;
  use the recorded Python 3.12 equivalent when `py` is unavailable and label
  that deviation.
- Provider/integration, native-Windows, live OCI, and cross-system runtime
  evidence remain opt-in or unavailable; they cannot be replaced by WSL,
  mocks, or local subprocess evidence.

## Coordinator gates

Wave 0 has established the checkout identity, dirty boundary, runtime
deviation, and initial file/dependency matrix. Eight read-only specialists are
active on disjoint `core/loop.py` slices. No implementation writer is
authorized until the loop slice map and characterization barrier are recorded.

Evidence labels used by this run are `confirmed`, `test-derived`,
`source-derived`, `proposed`, `inferred`, `unverified`, `blocked`, `deferred`,
and `pre-existing`.
