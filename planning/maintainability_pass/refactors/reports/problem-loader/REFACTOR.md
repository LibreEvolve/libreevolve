# `loader.py` refactor

Primary path: `libreevolve/problems/loader.py`.
Support path: `libreevolve/problems/context_loader.py`.

Design: extract context selection/loading, manifest diagnostics, excerpts,
hashing, and lazy PDF normalization behind a context-loader module. Keep
`Problem`, `load_problem`, metric normalization, validator policy, seed/workspace
selection, public/private compatibility names, and the literal context source
anchors in `loader.py`.

Measurements compare current source with `HEAD`; `loader.py` was pre-existing
dirty at Wave 0, so attribution is paired with the preserved baseline ledger.

| metric | before (`HEAD`) | after primary | after with support |
|---|---:|---:|---:|
| physical LOC | 3,005 | 1,418 | 3,076 |
| logical non-comment LOC | 2,802 | 1,305 | 2,855 |
| functions | 101 | 55 | 106 |
| classes | 2 | 1 | 2 |
| decision proxy | 579 | 348 | 591 |
| largest function | `_load_context_manifest`, 181 | `_load_initial_workspaces`, 174 | same, 174 |

The combined increase reflects explicit module boundaries and compatibility
wrappers; the extracted module has no runtime-orchestration imports and keeps
PDF loading lazy. The former falsey context-manifest hazard is covered by
negative tests and is resolved at the loader boundary.

Evidence: loader plus boundaries `285 passed, 8 skipped`; independent verifier
`01a069f4-5cec-7bc2-bb61-dc6d2204337a` PASS. No PR was opened.
