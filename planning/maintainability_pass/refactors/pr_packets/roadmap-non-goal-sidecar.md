# PR packet — roadmap non-goal Markdown sidecar

- Lane: `roadmap-non-goal-sidecar`
- Primary file: `papers/roadmap_non_goal_markdown_scan_boundary.json`
- Writer: `01a07060-9573-70f0-937d-4d0cf4b9abff`
- Independent verifier: `01a07064-4df3-7441-a5e4-0030d92383b4` — PASS
- External PR: none opened; publication was not authorized.
- Changed-path allowlist: the primary sidecar only.
- Dependency: `roadmap-non-goal-boundary` consumes this generated contract.

## Evidence

- Direct validator: exit `0`.
- Focused sidecar/roadmap tests: `5 passed`, exit `0`.
- Counts: 27 non-planning files, 27 readable, 0 unreadable, 3 non-goals,
  17 forbidden phrases, 0 contradictions.
- `git -c core.whitespace=cr-at-eol diff --check`: exit `0`.
- Plain `git diff --check`: exit `2` due inherited CRLF representation; no
  line-ending normalization was performed.

## Rollback and residual risk

Rollback is limited to restoring this sidecar's two semantic fields while
preserving unrelated EOL-only dirtiness. The scanner's path-component
exclusion intentionally keeps planning coordination out of the product claim
surface; future authoritative Markdown under `planning/` would require a
separate scope decision and regenerated sidecar.
