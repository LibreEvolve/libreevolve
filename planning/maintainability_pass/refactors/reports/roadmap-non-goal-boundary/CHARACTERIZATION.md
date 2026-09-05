# Roadmap non-goal Markdown boundary characterization

Baseline evidence:

- Pre-fix focused roadmap command: two roadmap tests passed and two roadmap
  tests failed because the observed count was 174 instead of 27. The combined
  README boundary command separately passed all four README tests.
- Clean `HEAD` archive attribution: 77 total Markdown files, 50 under
  `planning/`, and 27 outside `planning/`; the stale count is present before
  this orchestration's planning artifacts.
- The scanner's existing temporary corpus test still proves `build`, `dist`,
  and egg-info generated Markdown are excluded.

The characterization invariant is that planning/coordination Markdown is not a
product claim surface, while the 27 non-planning files remain scanned with the
same phrase, contradiction, and missing-evidence semantics. The isolated
writer's post-change run observes 27 files and passes the focused boundary
tests. The final exact non-integration run also returned exit 0 with 6,555
passed, 27 skipped, and 3 deselected.
