# Roadmap non-goal Markdown sidecar characterization

Lane: `roadmap-non-goal-sidecar`
Primary: `papers/roadmap_non_goal_markdown_scan_boundary.json`
Writer: `01a07060-9573-70f0-937d-4d0cf4b9abff`

The source scanner now excludes planning/coordination Markdown from the
product claim surface. The generated sidecar must therefore report the
non-planning corpus, retain its exact inventory and line-level records, and
keep all broader promotion evidence explicitly unrecorded.

Before the lane, the sidecar's semantic contract was stale: it said
`all_repo_markdown_files_scanned` and claimed every repository Markdown file.
The isolated characterization retained the current counts: 27 non-planning
Markdown files, 27 readable, 0 unreadable, 3 non-goals, 17 forbidden phrases,
and 0 contradictions.

Required behavior:

- `markdown_corpus_status` is
  `all_non_planning_repo_markdown_files_scanned`;
- `markdown_files` contains no `planning/` path;
- the claim boundary says planning/coordination Markdown is excluded;
- runtime metadata, plugin docstrings, CI promotion, intentional workflow,
  scope join, remediation, and owner-signoff evidence remain
  `not_recorded_locally` and are not claimed.
