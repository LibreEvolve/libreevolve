# ROADMAP Todo: AlphaEvolve Alignment Corrections

This list tracks issues found while reading `ROADMAP.md` after the code audit.
It focuses on roadmap statements that are incomplete, stale, or too narrow for
the stated goal of bringing LibreEvolve toward AlphaEvolve's specification.

## Staleness and Scope

## Missing Roadmap Items

## Existing Items That Need Tightening

- [ ] Implement hardness-of-approximation proof-element gates beyond
      source-boundary roadmap promotion.
  - Spec evidence: local arXiv `2509.18057v7`, `Reinforced Generation of
    Combinatorial Structures: Hardness of Approximation`, by Ansh Nagda,
    Prabhakar Raghavan, and Abhradeep Thakurta was submitted as v7 on March 9,
    2026 with cached SHA-256
    `32eb8c787527bf8674ec22fd08ee6e1108179e88d97300e110286270c041e842`
    and CC BY 4.0 metadata. It reports AlphaEvolve-discovered Ramanujan graph
    witnesses, MAX-3-CUT/MAX-4-CUT gadget reductions, metric-TSP equation
    gadgets, evolved faster verifier code, final brute-force verification of
    discovered gadgets, and mathematical lifting from finite structures to
    theorem statements.
  - Current evidence: ROADMAP has a theoretical-CS source-tracking note and
    `papers/README.md` labels `2509.18057` background-only with no graph/
    certification benchmark. `papers/theoretical_cs_sources.json` now includes
    a nested `proof_element_artifact_boundary` for the `2509.18057` graph/
    gadget/verifier/theorem-lifting evidence still missing. Roadmap still lacks
    executable graph/gadget artifact schemas, witness inventories, verifier
    APIs, synthetic correctness datasets, evolved-verifier runtime telemetry,
    judge-LLM/human-inspection records, brute-force final verification outputs,
    theorem/lemma/proof cross-links, proof-lifting metadata, source/artifact
    status, and SOTA comparison rows.
  - Required result: implement roadmap gates beyond the source sidecar:
    code/artifact availability, Ramanujan graph witness schema and Table 1
    certification rows, MAX-k-CUT gadget schema with
    Appendix C edge lists, TSP/MWST equation-gadget schema with Appendix D edge
    lists, verifier contracts, evolved-verifier speedup reports, synthetic
    correctness-check dataset provenance, judge-LLM and human-inspection
    attribution, independent brute-force verifier artifacts, theorem/result/
    lifting metadata, baseline/SOTA comparison rows for MAX-4-CUT, MAX-3-CUT,
    and metric TSP, proof-handoff status, extracted-link/source-repository
    status, and README/papers/code wording that keeps hardness-of-approximation
    proof-element support background-only until local execution, artifact, and
    verification evidence proves those semantics.
