# Maintainability Pass Baseline

Captured: 2026-09-02T09:32:58-04:00

## Scope

This is the Wave 0 baseline for the LibreEvolve maintainability pass. It is a
snapshot of the current checkout, not a completion claim. Existing changes are
preserved and must be classified before integration.

## Git state

- Checkout: `/mnt/c/users/timot/documents/projects/domains/libreevolve.com`
- Branch: `master`
- `HEAD`: `037caa7e0e6ba9f4b60b3ae50c2c9680729c0fee`
- Upstream: `LibreEvolve/master`
- Divergence: `0 0` (`HEAD...@{upstream}`)
- Tracked changed status records: `273`
- Untracked status records: `1` — the maintainability orchestration prompt
- No commit, push, merge, reset, clean, stash, or deletion was performed

The existing worktree is dirty before the maintainability implementation wave.
The seven substantive paths currently visible with
`git diff --ignore-space-at-eol --stat` are:

- `libreevolve/problems/benchmarks/alphaevolve_tex_proposition_inventory_boundary.py`
- `libreevolve/problems/benchmarks/alphaevolve_tex_prose_inventory_boundary.py`
- `libreevolve/problems/benchmarks/implementation_evidence_map_boundary.py`
- `libreevolve/problems/benchmarks/roadmap_source_span_coverage_boundary.py`
- `libreevolve/problems/benchmarks/roadmap_source_span_disposition_boundary.py`
- `tests/test_alphaevolve_tex_proposition_inventory_boundary.py`
- `tests/test_alphaevolve_tex_prose_inventory_boundary.py`

That semantic diff is approximately `1,221` insertions and `87` deletions.
The remaining tracked modifications require preservation and EOL-aware review;
the current index/worktree EOL summary is `193 lf/crlf`, `825 lf/lf`, and
`73 lf/mixed` entries, plus non-text entries.

## Runtime and test environment

- Required launcher `py`: unavailable in this WSL shell.
- Available interpreter: `/home/timot/.local/bin/python3.12` — Python 3.12.13.
- Available package runner: `/home/timot/.local/bin/uv`.
- `pytest` and `pytest-mock` are not installed in the ambient Python 3.12
  environment. An isolated `uv run --no-project --with ...` environment is
  required for test execution and must be recorded by each test wave.
- Package Python files: `368`.
- Test Python files: `330`.
- Active unchecked TODO records: `522` (`code=222`, `papers=252`,
  `readme=32`, `roadmap=16`).

## Prior observations requiring re-verification

The preceding assessment observed, but did not complete a final current full
suite, the following hypotheses:

- workspace materialization case-collision behavior is host-POSIX dependent;
- Windows-style executable paths are parsed with POSIX path semantics in
  provenance;
- Windows drive-letter artifact paths are not rejected by cancellation policy
  when running on POSIX;
- paper inventory generators and dependent tests/sidecars disagree over
  Section 5 versus Section 4 and counts `403/985/286` versus `402/812/244`;
- additional full-suite failures were seen in ablation results, cached-PDF
  headers, benchmark hardening, and matrix results.

These are `pre-existing`/`unverified` until a component agent reproduces them
against this baseline. They must not be masked by broad test expectation edits.

## Initial evidence boundaries

The repository documents itself as alpha-stage and explicitly does not claim a
hostile-code security sandbox, distributed execution, pending-work resume,
live Gemini model parity, checked-in published AlphaEvolve benchmark
reproduction, or signed/published release verification. The maintainability
pass may clarify these boundaries but must not promote them without their own
authoritative evidence.
