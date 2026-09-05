# `matrix_results.py` refactor

Primary path: `libreevolve/problems/benchmarks/matrix_results.py`.
Support paths: `libreevolve/problems/benchmarks/matrix_artifact_identity.py`,
`tests/test_matrix_results.py`.

Design: extract deterministic canonical JSON writing, file digest/size,
stable JSON identity, safe relative artifact paths, and one concrete artifact
inventory record. Keep result schemas, suite policy, rights authority,
fixture orchestration, validators, and public façade signatures in the
primary module.

| metric | before (`HEAD`) | after primary | after with support |
|---|---:|---:|---:|
| physical LOC | 7,534 | 7,443 | 7,575 |
| logical non-comment LOC | 7,164 | 7,079 | 7,198 |
| functions | 160 | 157 | 162 |
| classes | 16 | 16 | 16 |
| decision proxy | 1,300 | 1,275 | 1,301 |
| largest function | `_validate_matrix_publication_inventory`, 150 | same, 150 | same, 150 |

The combined support-module increase is the cost of a neutral identity seam;
schema and rights policy ownership did not move. The current helper is used
only by the façade. Native filesystem, partial-write, external-source,
provider, and end-to-end evidence remain unverified.

Evidence: `145 passed`; independent verifier
`01a06a07-ad4d-7641-aa55-fe6b0e6690c9` CONDITIONAL because the checkout is
shared and dirty, while AST/signature/determinism/source-rights checks passed.
No PR was opened.
