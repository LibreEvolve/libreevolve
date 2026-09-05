# `roadmap_non_goal_markdown_scan_boundary.py` auxiliary gate packet

Primary path: `libreevolve/problems/benchmarks/roadmap_non_goal_markdown_scan_boundary.py`.
This is a separate auxiliary docs/evidence-boundary lane discovered during
Wave 4 terminal validation; it is not combined with any of the 15 original
maintainability primary-file lanes.

## Scope

- Support/test paths: `tests/test_roadmap_non_goal_markdown_scan_boundary.py` and
  the separately authorized generated sidecar
  `papers/roadmap_non_goal_markdown_scan_boundary.json`.
- Proposed branch: `refactor/roadmap-non-goal-boundary` (not created).
- External PR: not opened; publication was not authorized.
- Changed-path allowlist contains only the primary scanner and its direct test;
  the sidecar is a dependency lane with its own packet and verifier.
- The governed product-document corpus is the 27 Markdown files outside
  `planning/`; coordination Markdown is evidence, not a product claim surface.

## Evidence and implementation

- Prior terminal result before this lane: `6,552 passed, 27 skipped, 2
  failed, 3 deselected`, exit 1; both failures asserted 27 while the scanner
  included coordination Markdown. The current source scanner excludes
  `planning/`, and the sidecar now records the 27-file non-planning corpus.
- Final terminal receipt: `PYTHONDONTWRITEBYTECODE=1 /mnt/c/Windows/py.exe
  -3.12 -m pytest tests/ -m "not integration" --tb=short` returned exit `0`
  with `6,555 passed, 27 skipped, 3 deselected` in `1:31:27`.
- Clean `HEAD` contains 77 Markdown files, of which 27 are outside `planning/`.
- Writer: `01a07049-c76f-7020-9816-c6e3aed63c4f` in an isolated fork.
- Writer result: add `planning` to the existing exclusion set, make the
  non-planning status/claim boundary explicit, and add a planning-directory
  regression; post-change scanner count is 27 and focused roadmap tests pass.
- Sidecar independent verifier: `01a07064-4df3-7441-a5e4-0030d92383b4`, PASS
  for the generated artifact. Source/test independent verifier:
  `01a07071-1c53-78b2-80e0-32690ebcc5d9`, PASS with EOL-attribution
  qualification after matching the baseline and all three current hashes;
  the broad paper-manifest validation was not used as source-lane proof.

## Risks and rollback

The boundary wording must remain explicit about excluded planning/coordination
evidence, while preserving the existing generated-output exclusions. Rollback
is limited to the two allowed paths; no unrelated docs, tests, branches, or
external state may be changed.
