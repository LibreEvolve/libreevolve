# problems/benchmarks/matrix_results.py characterization

Evidence state: focused characterization gate passed; artifact-identity seam
implemented; independent verification is conditional on shared-checkout
attribution.

The test-only wave added 195 lines to `tests/test_matrix_results.py` covering
load errors, scalar/dimension boundaries, caller-input isolation, duplicate
artifact paths, cross-platform unsafe paths, deterministic publication bytes,
and suite duplicate rejection. Root Windows verification reports `145 passed
in 2.38s`. Native Windows/macOS filesystem behavior, partial-write cleanup,
failed-generation residue, and external-source retrieval remain unverified.

The implementation writer touched only `matrix_results.py` and the neutral
`matrix_artifact_identity.py` helper. The verifier reports `145 passed` plus
AST, compile, import, public-signature, determinism, duplicate, path-safety,
and source-rights checks. Because the checkout contains unrelated pre-existing
dirty paths, the verifier labels the result CONDITIONAL for exact fresh-diff
attribution; no artifacts, docs, rights authority, or package exports moved.
