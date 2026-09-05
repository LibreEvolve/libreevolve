# Roadmap non-goal Markdown sidecar inventory

Lane: `roadmap-non-goal-sidecar`
Primary: `papers/roadmap_non_goal_markdown_scan_boundary.json`
Writer: `01a07060-9573-70f0-937d-4d0cf4b9abff`
Verifier: `01a07064-4df3-7441-a5e4-0030d92383b4`

This generated artifact is the exact sidecar projection of the source scanner
record. Its contract consists of the source-record status, the ordered
non-planning Markdown inventory, readability/error records, non-goal and
forbidden-phrase findings, contradiction count, and explicit unrecorded
broader-evidence fields. It has no independent discovery or mutation logic.

Current inventory measurements are 27 non-planning files, 27 readable, 0
unreadable, 3 non-goals, 17 forbidden-phrase records, and 0 contradictions.
The sidecar is downstream of the scanner source lane and must be regenerated
when the scanner's corpus policy changes. It is intentionally not evidence for
runtime metadata, plugin docstrings, CI promotion, workflow intent, scope
joins, remediation, or owner sign-off.

Characterization and verification are recorded in the sibling reports. The
sidecar writer changed only the status and claim-boundary fields; no external
branch, PR, commit, or publication was created.
