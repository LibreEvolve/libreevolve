# Roadmap non-goal Markdown boundary refactor

Design: make the scanner's governed corpus boundary explicit by excluding the
`planning` directory alongside generated/cache directories. Preserve all
existing phrase scanning, line-level records, source-boundary fields, and
non-promotion limitations. Add only the direct regression needed to prove
planning files are not included.

Writer: `01a07049-c76f-7020-9816-c6e3aed63c4f`.
Dependent sidecar lane: `roadmap-non-goal-sidecar`, independently verified by
`01a07064-4df3-7441-a5e4-0030d92383b4`.
Source/test verifier: `01a07071-1c53-78b2-80e0-32690ebcc5d9`, PASS with
EOL-attribution qualification; the broad paper-manifest validation remains
unverified.
No external branch, PR, commit, or merge exists.
