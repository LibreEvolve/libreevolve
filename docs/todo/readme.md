# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

## Research References and Bundled Papers

## Feature Claims

- [x] Keep README Appendix B.1-B.3 labels scoped until paper-heading
      provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.1-B.3 are titled `First
    autocorrelation inequality`, `Second autocorrelation inequality`, and
    `Third autocorrelation inequality`, and the constants are `C1`, `C2`, and
    `C3`. The paper does not use `k=3`, `k=4`, or `k=5` labels for these three
    autocorrelation entries.
  - Status: README now states that the Appendix B registry preserves the exact
    B.1-B.3 paper-facing labels and C1-C3 constants separately from internal
    `autocorrelation_bounds_k*` ids. The registry validator and tests reject
    missing label metadata, drifted constants, and public `k=` names.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README Appendix B.8 ratio wording scoped until squared-ratio
      convention provenance exists.
  - Spec evidence: AlphaEvolve Appendix B.8 reports constructions for the
    max/min pairwise-distance ratio, but the numerical values `12.889266112`
    for 16 points in 2D and `4.165849767` for 14 points in 3D are reported
    under a squared-ratio convention, with the geometric ratio obtained by a
    square-root transform.
  - Status: README now states that Appendix B.8 registry evidence preserves the
    raw squared values, square-root-derived ratios, point counts, dimensions,
    prior squared bounds, and comparison policy, while leaving coordinate
    payloads and all-pairs distance certificates open.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README Appendix B.5 source-formulation wording scoped until
      equivalence evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.5 defines the source problem using
    non-negative `f,g: [-1,1] -> [0,1]`, `f + g = 1`, `integral f = 1`,
    zero extension outside `[-1,1]`, and
    `sup_{x in [-2,2]} integral_{-1}^1 f(t) g(x+t) dt`, then uses `[40]` to
    reduce the constant to an infimum over normalized step functions `h` on
    `[0,2]`.
  - Status: README now states that the Appendix B registry preserves the B.5
    source paired-function formulation, zero-extension convention,
    shift-supremum objective, known bounds, `[40]` equivalence, and mapping to
    the normalized `[0,2]` step-function formulation, while the Figure 10
    construction payload remains open.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README Appendix B.6 theorem wording scoped until admissibility
      evidence exists.
  - Spec evidence: AlphaEvolve Appendix B.6 defines `C6` via arbitrarily large
    finite sets `A` and `B`, explicit sumset/difference-set notation,
    `X << Y` and `X >> Y` constants independent of sufficiently large sets,
    `[39, Corollary 3]` for the `4/3` upper bound, `[39, Theorem 1]` for the
    lower-bound method, and a Gyarmati finite-set admissibility condition for
    non-negative integer `U` containing zero.
  - Status: README now distinguishes B.6 theorem-condition evidence from
    witness payload provenance: it names the `C6` source theorem,
    sumset/difference-set definitions, asymptotic notation, source theorem
    anchors, admissible-`U` checks, lower-bound formula, and separate
    `finite_set_witness_boundary`.
  - Verification: `py -3.12 -m pytest tests/test_appendix_b_registry.py -q`
    passes.

- [x] Keep README database-output claims scoped to prompt-visible output
      capture versus queryable output indexes.
  - Spec evidence: AlphaEvolve's evolutionary database stores generated
    solutions with evaluation results and program outputs attached, then
    resurfaces useful prior ideas in later generations.
  - Current evidence: README now describes strict evaluator `outputs` /
    `program_output` capture, redaction, truncation, stage output checks,
    bounded prompt-visible program-output summaries,
    `runtime.history.program_output_index`, and valid output-bearing
    candidates contributing to current-run `resurfacing_index`. It also
    documents `resurface_by_program_output()` as exact source-key/hash
    current-run querying, and states that these indexes are not persisted
    database tables, semantic output-similarity indexes, schema-aware output
    retrieval, or replayable sampling engines. README now ties that boundary
    to `papers/program_output_boundary.json`. README also ties bounded
    current-run artifact path/hash/redaction/skipped/stage/content-excerpt
    indexing to `papers/artifact_index_boundary.json`, while keeping durable
    full-content and semantic artifact search out of scope.
  - Required result: continue keeping README wording scoped when durable output
    query tables, schema-aware output retrieval, or semantic output search
    land.

## Architecture Description
