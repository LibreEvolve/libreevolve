# Completed Papers Todo Items

Moved from `docs/todo/papers.md`. Keep this file as the archive for completed backlog items from that source; leave open items in `docs/todo/papers.md`.

## Papers Todo: Reference and Specification Gaps

## AlphaEvolve Paper Requirements Not Yet Implemented

- [x] Emit matrix tensor-rank runtime boundary sidecar.
  - Paper evidence: Section 3.1 frames matrix results as low-rank tensor
    decompositions, while footnote 3 excludes some fewer-than-49
    multiplication algorithms from recursive tensor-decomposition comparisons.
  - Status: `papers/matrix_tensor_rank_runtime_boundary.json` now carries the
    paper-facing absence/readiness boundary for algorithm kind, rank,
    recursive applicability, certificate scope, tensor identity, target tensor,
    exactness certificate, matrix-result, and artifact provenance. The
    paper-manifest gate requires and validates the sidecar at the real repo
    root.
  - Verification: `py -3.12 -m pytest tests\test_matrix_results.py
    tests\test_paper_manifest.py tests\test_agents_docs.py -q`, `py -3.12
    -m libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\matrix_results.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: emitted run artifacts for target-tensor identity,
    recursive applicability, exactness certificates, and source-note caveats
    remain open.

- [x] Emit matrix sweep-space runtime boundary sidecar.
  - Paper evidence: Appendix A Figures 9a-9c show matrix search programs
    evolving a `sweep()` function with `hyper.uniform(...)` ranges and sampled
    search outcomes, not just final tensor-decomposition artifacts.
  - Status: `papers/matrix_sweep_space_runtime_boundary.json` now carries the
    paper-facing absence/readiness boundary for search-program, `sweep`,
    hyperparameter, sampled-configuration, selected-decomposition,
    certificate, and artifact provenance. The paper-manifest gate requires and
    validates the sidecar at the real repo root.
  - Verification: `py -3.12 -m pytest tests\test_matrix_results.py
    tests\test_paper_manifest.py tests\test_agents_docs.py -q`, `py -3.12
    -m libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\matrix_results.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: emitted run artifacts for evolved sweep functions,
    hyperparameter ranges, sampled sweep outcomes, and final certificate
    linkage remain open.

- [x] Emit matrix scalar-field runtime boundary sidecar.
  - Paper evidence: Table 2 and Section 3.1 distinguish complex-valued matrix
    algorithms, exact real/complex applicability, characteristic-0 claims, and
    finite-field-only prior work.
  - Status: `papers/matrix_scalar_field_runtime_boundary.json` now carries the
    paper-facing absence/readiness boundary for scalar-field, characteristic,
    coefficient-representation, certificate, and artifact provenance. The
    paper-manifest gate requires and validates the sidecar at the real repo
    root.
  - Verification: `py -3.12 -m pytest tests\test_matrix_results.py
    tests\test_paper_manifest.py tests\test_agents_docs.py -q`, `py -3.12
    -m libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\matrix_results.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: emitted run artifacts for exact complex coefficients,
    decomposition/certificate refs, scalar-field/domain declarations, and
    characteristic-specific verifier evidence remain open.

- [x] Emit matrix near-integrality runtime boundary sidecar.
  - Paper evidence: Section 3.1 says candidates were prompted for
    near-integral matrix decompositions and rounded to integer or half-integer
    entries for exactness verification.
  - Status: `papers/matrix_near_integrality_runtime_boundary.json` now carries
    the paper-facing absence/readiness boundary for near-integrality prompt and
    rounding diagnostics. The paper-manifest gate requires and validates the
    sidecar at the real repo root.
  - Verification: `py -3.12 -m pytest tests\test_matrix_results.py
    tests\test_paper_manifest.py tests\test_agents_docs.py -q`, `py -3.12
    -m libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\matrix_results.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: emitted run artifacts for actual prompt instructions,
    raw/rounded coefficients, rounding error, and exactness-certificate links
    remain open.

- [x] Emit matrix cascade-run runtime boundary sidecar.
  - Paper evidence: Section 3.1 says matrix performance is evaluated across
    multiple random seeds using the evaluation cascade and reported as best
    rank plus fraction of seeds reaching it.
  - Status: `papers/matrix_cascade_run_runtime_boundary.json` now carries the
    paper-facing absence/readiness boundary for executed per-seed matrix
    cascade traces. The paper-manifest gate requires and validates the sidecar
    at the real repo root.
  - Verification: `py -3.12 -m pytest tests\test_matrix_results.py
    tests\test_paper_manifest.py tests\test_agents_docs.py -q`, `py -3.12
    -m libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\matrix_results.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: emitted run artifacts for actual matrix per-seed cascade
    traces, stop/pruning decisions, and candidate lineage remain open.

- [x] Emit matrix baseline-component runtime boundary sidecar.
  - Paper evidence: Section 3.1 describes the matrix workflow as starting
    from a standard gradient-based algorithm with initializer, reconstruction
    loss, and Adam optimizer.
  - Status: `papers/matrix_baseline_component_runtime_boundary.json` now
    carries the paper-facing absence/readiness boundary for baseline component
    provenance. The paper-manifest gate requires and validates the sidecar at
    the real repo root.
  - Verification: `py -3.12 -m pytest tests\test_matrix_results.py
    tests\test_paper_manifest.py tests\test_agents_docs.py -q`, `py -3.12
    -m libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\matrix_results.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: emitted run artifacts for actual baseline components,
    generation-0 outcomes, and mutation lineage remain open.

- [x] Emit Appendix A matrix resource-frontier sidecars.
  - Paper evidence: Appendix A states that larger matrix sizes beyond
    `<5,5,5>` often ran out of memory under the paper's 1000-random-seed,
    single-GPU evaluation setup.
  - Status: `papers/appendix_a_matrix_resource_frontier.json` now carries the
    paper-only resource-frontier boundary, and
    `papers/appendix_a_matrix_local_resource_frontier.json` carries the
    explicit local absence/readiness boundary for larger-target scaling
    attempts. The paper-manifest gate requires and validates both sidecars at
    the real repo root.
  - Verification: `py -3.12 -m pytest
    tests\test_appendix_a_matrix_registry.py tests\test_paper_manifest.py
    tests\test_agents_docs.py -q`, `py -3.12 -m
    libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\appendix_a_matrix_registry.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: no local larger-target attempt corpus, GPU memory profile,
    OOM diagnostics, reduced-seed tradeoff, or target inclusion/exclusion
    policy has been emitted.

- [x] Emit Appendix A matrix target-suite curation sidecars.
  - Paper evidence: Appendix A says the matrix target suite was chosen roughly
    from sizes with 2 <= m,n <= 5 and a reasonable p cutoff, and that axis
    permutations of matrix-multiplication tensors are equivalent.
  - Status: `papers/appendix_a_matrix_curation.json` now carries the
    paper-facing reported-suite curation record, and
    `papers/appendix_a_matrix_excluded_target_curation.json` carries the
    explicit `not_recorded_locally` boundary for broad excluded
    non-equivalent target justifications. The paper-manifest gate requires and
    validates both sidecars at the real repo root.
  - Verification: `py -3.12 -m pytest
    tests\test_appendix_a_matrix_registry.py tests\test_paper_manifest.py
    tests\test_agents_docs.py -q`, `py -3.12 -m
    libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\appendix_a_matrix_registry.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: paper-facing excluded-target justification records and
    local resource-frontier/OOM evidence remain open.

- [x] Emit paper artifact-role/linkage sidecars.
  - Paper evidence: the AlphaEvolve Contributions section names the initials
    responsible for creating the figures and assembling the accompanying
    Google Colab.
  - Status: `papers/paper_artifact_roles.json` now carries the paper-facing
    figure-creator and Colab-assembler records, while
    `papers/paper_artifact_linkage.json` carries the explicit
    `not_yet_linked` boundary for concrete rendered figure and companion
    notebook artifacts. The paper-manifest gate requires and validates both
    sidecars at the real repo root.
  - Verification: `py -3.12 -m pytest tests\test_paper_artifact_roles.py
    tests\test_paper_manifest.py tests\test_agents_docs.py -q`, `py -3.12
    -m libreevolve.tools.paper_manifest --require-local-pdfs`, and `py -3.12
    -m compileall -q libreevolve\problems\benchmarks\paper_artifact_roles.py
    libreevolve\tools\paper_manifest.py` passed.
  - Remaining gap: paper-facing rendered figures, notebook retrieval digests,
    cell/source maps, and concrete source-to-artifact maps remain open.

- [x] Emit Appendix A matrix baseline-citation sidecar.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 and Appendix A
    Table 3 include best-known matrix ranks with bracketed reference ids.
  - Status: `papers/appendix_a_matrix_baseline_citations.json` now carries
    paper-facing best-known-rank citation records for all 54 Appendix A matrix
    targets, including source table/page, reference ids, source artifact
    paths/hashes, caveats, and report-visible baseline-source refs. The
    paper-manifest gate validates that sidecar when Appendix A registry
    evidence is present.
  - Verification: `py -3.12 -m pytest
    tests\test_appendix_a_matrix_registry.py tests\test_paper_manifest.py -q`,
    `py -3.12 -m pytest tests\test_agents_docs.py -q`, and `py -3.12 -m
    libreevolve.tools.paper_manifest --require-local-pdfs` passed.
  - Remaining gap: paper-facing report/table exports still need automatic
    attachment of those baseline-source rows.

- [x] Emit matrix headline historicity artifact sidecar.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` reports the 4x4 complex
    rank-48 result in the abstract and Section 3.1, and distinguishes it from
    recursive Strassen rank 49 and Fawzi et al. rank 47 over the field with
    two elements.
  - Status: `papers/matrix_headline_historicity_artifacts.json` now carries
    the paper-facing `mm_4x4x4` rank-48 headline historicity artifact,
    including target/dimension/rank/field values, prior comparisons, source
    refs, evidence links, nested headline evidence, artifact path, and digest.
    The paper-manifest gate validates that sidecar when Appendix A registry
    evidence is present.
  - Verification: `py -3.12 -m pytest tests\test_matrix_results.py
    tests\test_paper_manifest.py -q`, `py -3.12 -m pytest
    tests\test_agents_docs.py -q`, and `py -3.12 -m
    libreevolve.tools.paper_manifest --require-local-pdfs` passed.
  - Remaining gap: paper-facing exports still need automatic attachment of
    that artifact.

- [x] Emit Table 2/Table 3 matrix-rank table artifact sidecar.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 is the selected
    matrix-rank comparison table, and Appendix A Table 3 is the full
    54-target version with rank values, outcome coloring/counts,
    complex-valued caveats, Colab links, and the concurrent-work note.
  - Status: `papers/matrix_rank_table_artifacts.json` now carries
    paper-facing artifacts for `table2_matrix_rank_selected` and
    `appendix_a_table3_matrix_rank_full`, including source linkage,
    source/rendered/OCR artifact records, row counts, nested table-exhibit
    evidence, artifact paths, and digests. The paper-manifest gate validates
    that sidecar when Appendix A registry evidence is present.
  - Verification: `py -3.12 -m pytest tests\test_matrix_exhibits.py
    tests\test_paper_manifest.py -q`, `py -3.12 -m pytest
    tests\test_agents_docs.py -q`, and `py -3.12 -m
    libreevolve.tools.paper_manifest --require-local-pdfs` passed.
  - Remaining gap: paper-facing report/table exports still need automatic
    attachment of those artifacts.

- [x] Emit Appendix A matrix subset-scope artifact sidecar.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 scopes the
    all-matched-or-surpassed matrix statement to `m, n, p <= 5`; Appendix A
    Table 3 is broader and includes two fell-behind rows.
  - Status: `papers/appendix_a_matrix_subset_scope_artifacts.json` now carries
    paper-facing subset-scope artifacts for `appendix_a_full`,
    `main_text_mnp_le_5`, and `table_2_selected`, including source linkage,
    inclusion predicates, counts, out-of-scope/fell-behind ids, nested subset
    evidence, artifact paths, and digests. The paper-manifest gate validates
    that sidecar when Appendix A registry evidence is present.
  - Verification: `py -3.12 -m pytest tests\test_appendix_a_matrix_registry.py
    tests\test_paper_manifest.py -q` and `py -3.12 -m
    libreevolve.tools.paper_manifest --require-local-pdfs` passed.
  - Remaining gap: rendered table/report exports still need automatic
    propagation of the subset-scope artifacts wherever rank/outcome rows are
    published.

- [x] Emit Appendix A matrix row-note caveat artifact sidecar.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A Table 3 says
    concurrent work `[49]` also found a rank-90 algorithm for `<4, 5, 6>`.
  - Status: `papers/appendix_a_matrix_row_note_artifacts.json` now carries
    the paper-facing row-note artifact for `mm_4x5x6`, including the cited
    reference, source location, matching-rank relationship, caveat text,
    nested row-note evidence, artifact path, and digest. The paper-manifest
    gate validates that sidecar when Appendix A registry evidence is present.
  - Verification: `py -3.12 -m pytest tests\test_appendix_a_matrix_registry.py
    tests\test_paper_manifest.py -q` and `py -3.12 -m
    libreevolve.tools.paper_manifest --require-local-pdfs` passed.
  - Remaining gap: rendered table/report exports still need automatic
    propagation of the caveat wherever rank/outcome rows are published.

- [x] Track stochastic prompt-format probability provenance.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 says stochastic
    formatting uses template placeholders with human-provided alternatives for
    increased diversity, instantiated using probability distributions from a
    separate config file.
  - Status: `runtime.history.stochastic_prompt_format_distribution_report`
    now records paper-facing stochastic-format evidence with prompt ids,
    marker names, option-set ids, inline/effective config source boundaries,
    alternative indexes, normalized probabilities, selected alternative
    hashes/indexes, weight override source, prompt/call linkage, RNG/replay
    boundary, and overclaim checks.
  - Verification: `py -3.12 -m pytest
    tests/core/test_loop.py::test_loop_logs_stochastic_prompt_format_selection_metadata
    -q` passed.
  - Remaining gap: separate config-file source attribution and certified
    human-authored alternatives remain non-parity boundaries.

- [x] Track primary-prompt instruction and target-solution evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 says the
    primary prompt includes previously discovered solutions sampled from the
    program database and system instructions for proposing changes to a
    particular solution.
  - Status: `runtime.history.primary_prompt_instruction_report` now records
    paper-facing prompt ingredient evidence: target program/workspace hash,
    sampled solution roles, instruction policy/hash/redaction boundary,
    provider message-role placement as serialized single prompt, edit-scope
    constraints, required-channel diagnostics, and prompt/call linkage when
    telemetry is available.
  - Verification: `py -3.12 -m pytest
    tests/core/test_loop.py::test_runtime_history_reports_primary_prompt_instruction_provenance
    -q` passed.
  - Remaining gap: role-separated provider system/developer/user messages
    remain unsupported; stochastic prompt-format distribution provenance is a
    separate open prompt TODO.

- [x] Track stale source-specific absence wording in active TODO bodies.
  - Paper evidence: the paper index uses implementation-status and TODO
    coverage tables as the source-to-backlog chain for paper-alignment audits.
  - Status: the paper-manifest gate now rejects explicit
    `no source-specific ... TODO` wording when the target active ledger already
    has an open source-specific TODO block for the same manifest id. Focused
    tests cover ignored generic examples and rejected stale source-specific
    README absence wording.
  - Remaining gap: broader stale-absence paraphrases remain separate future
    pattern additions.

- [x] Validate paper-index TODO coverage cross-references.
  - Paper evidence: the `papers/README.md` TODO coverage table is the
    paper-index source-to-backlog chain for AlphaEvolve-alignment audits.
  - Status: the paper-manifest gate validates exact manifest row coverage,
    duplicate/extra rows, safe path classes, active open source-specific TODO
    evidence, completed source-specific checklist evidence, completed-evidence
    requirements for implemented/partial status classes, and a concrete-path
    policy that rejects grouped labels until a grouped-label taxonomy exists.
  - Remaining gap: none for this bounded coverage-table slice; stale absence
    prose and deeper implementation-status semantic validation remain separate
    paper-facing work.

- [x] Track official DeepMind AlphaEvolve blog source and claim variants.
  - Paper/source evidence: the official May 14, 2025 Google DeepMind blog
    article describes the AlphaEvolve architecture, whole-codebase scope,
    deployed systems results, white-paper/Colab links, Early Access plans, and
    blog-specific values such as `32.5%` FlashAttention speedup.
  - Status: `papers/official_deepmind_blog.json` now records the source row
    with URL/date/title/team, retrieval hash, outbound links, claim ids,
    source-specific values/units, reconciliation status, blog-only availability
    statements, acknowledgement/illustration role metadata, and evidence
    policy. The paper-manifest gate requires and validates this sidecar at
    repo root.
  - Remaining gap: none for this bounded announcement-source slice; exact
    PDF/Colab claim mappings, variant reconciliation, and role-to-artifact
    evidence remain separate paper work.

- [x] Track AlphaEvolve theoretical-CS proof-element source evidence.
  - Paper/source evidence: Google Research's September 30, 2025 article and
    arXiv `2509.18057v7`, `Reinforced Generation of Combinatorial Structures:
    Hardness of Approximation`, report AlphaEvolve-discovered finite
    structures used as proof elements in complexity theory.
  - Status: `papers/theoretical_cs_sources.json` now records the article and
    arXiv source row with URL/date/authors, retrieval hashes, arXiv
    version/date/DOI/PDF-cache metadata, MAX-k-CUT, random-graph/Ramanujan,
    and metric-TSP application rows, lifting-framework and verification
    boundaries, rights/license-relevant cache metadata, docs/TODO claim links,
    and remaining artifact/verifier/code work. The paper-manifest gate
    requires and validates this sidecar at repo root.
  - Remaining gap: none for this bounded source-tracking slice; graph/gadget
    artifact inventories, source repositories, verifier/brute-force
    provenance, and local certification benchmarks remain separate paper work.

- [x] Track Terence Tao follow-on blog source and claim boundaries.
  - Paper/source evidence: Terence Tao's November 5, 2025 post links the
    follow-on arXiv paper, the AlphaEvolve tool, and the problem repository,
    describes 67 mathematics experiments, and adds commentary on verifier
    hardening, negative-result recording, generalization, and proof handoffs.
  - Status: `papers/follow_on_tao_blog.json` now records the Tao blog source
    row with canonical URL, author/date/title, WordPress API metadata,
    retrieval hashes, linked arXiv/repository/tool URLs, claim categories,
    source-line spans, and evidence policy. The paper-manifest gate requires
    and validates this sidecar at repo root.
  - Remaining gap: none for this bounded blog-source slice; theoretical-CS
    source rows, exact blog-to-paper/repository mappings, proof artifacts, and
    comment-thread claim separation remain separate paper work.

- [x] Track follow-on problem-repository runtime-absence evidence.
  - Paper/source evidence: the follow-on problem repository README says
    notebooks contain prompts, verification code, initial programs, final
    evolved programs, and visualization/analysis code where appropriate, and
    then explicitly says the repository does not contain code to run
    AlphaEvolve.
  - Status: `papers/follow_on_runtime_absence.json` now records the pinned
    runtime-absence row with repository URL/ref/commit/date, README/tree
    source URLs, 28 notebook paths, Git blob ids, byte counts, artifact-kind
    flags, explicit AlphaEvolve-runtime absence, source phrases, and
    verifier-versus-runtime classification. The paper-manifest gate requires
    and validates this sidecar at repo root.
  - Remaining gap: none for this bounded runtime-absence slice; full notebook
    cell inventory, problem-id mapping, notebook SHA-256 hashes, and Tao-blog
    evidence remain separate paper work. The cached follow-on PDF row has
    since been recorded separately.

- [x] Track follow-on problem-repository rights, citation, and attribution.
  - Paper/source evidence: the follow-on problem repository README records the
    citation instruction, Google LLC copyright, Apache-2.0 software terms,
    CC-BY-4.0 materials terms, AS-IS and non-official-product disclaimers,
    Gómez-Serrano/Tao role attribution, and Problem 65 IMO source origin.
  - Status: `papers/follow_on_repository_rights.json` now records the
    repository source-use row with pinned URL/ref/commit/date, citation/BibTeX
    fields, license URLs, artifact-type license mapping, source-origin notes,
    docs/TODO claim-surface links, and reuse policy. The paper-manifest gate
    requires and validates this sidecar at repo root.
  - Later status: notebook/runtime absence, per-problem inventory, and
    generated-artifact source-relationship templates have since been recorded;
    this bounded source-use slice remains complete.

- [x] Track follow-on AlphaEvolve mathematical-discovery paper and repository.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.2 says more
    constructive-math examples and method details would appear in an upcoming
    paper. Current source evidence identifies that follow-on as arXiv
    `2511.02864v3`, `Mathematical exploration and discovery at scale`, and the
    `google-deepmind/alphaevolve_repository_of_problems` repository.
  - Status: `papers/follow_on_sources.json` now records the follow-on
    paper/repository source row, including versioned arXiv identity, cached
    `papers/2511.02864__Mathematical_exploration_and_discovery_at_scale.pdf`
    row, pinned repository commit, README digest, declared 67-problem count,
    notebook coverage boundary, runtime-code absence, source-use licenses,
    citation boundary, and docs/TODO claim-surface links. The standard
    paper-manifest validation requires the sidecar at repo root.
  - Later status: problem inventory, notebook hash/readability matrices,
    Appendix B claim mappings, and generated-artifact rights templates have
    since been recorded; the cached `2511.02864` PDF/digest row has also been
    recorded.

- [x] Track companion-result repository rights and disclaimer evidence.
  - Paper evidence: the `google-deepmind/alphaevolve_results` README declares
    Google LLC copyright, Apache-2.0 software licensing, CC-BY-4.0 materials
    licensing, an AS-IS warranty disclaimer, and non-official-product status.
  - Status: companion artifact-rights records now attach source-rights
    metadata to generated matrix report artifacts and inventories, preserving
    companion repository source links, software/materials license split, source
    rights holder, reuse policy, source-PDF rights separation, LibreEvolve MIT
    separation, AS-IS disclaimer, non-official-product, and non-endorsement
    boundaries.
  - Remaining gap: none for this bounded paper-facing matrix artifact-rights
    slice; broader generated export surfaces remain separate future work.

- [x] Track companion-result notebook selection scope and absences.
  - Paper evidence: the `google-deepmind/alphaevolve_results` README says
    `mathematical_results.ipynb` contains mathematical discoveries and
    correctness-verification code only for instances where AlphaEvolve
    outperformed SOTA; matched-but-not-outperformed constructions are excluded,
    and AlphaEvolve runtime code is absent.
  - Status: companion selection-scope records now distinguish included
    improved-over-SOTA claims from intentionally absent matched-only claims,
    including absence reason, verifier-code availability, runtime-code absence,
    source artifact reference, and source manifest link. Matrix result/headline
    reports validate the record for the `mm_4x4x4` companion claim.
  - Remaining gap: none for this bounded paper-facing selection-scope slice;
    generated export rights and full local reproduced notebooks remain active
    paper work.

- [x] Emit AlphaEvolve companion Colab source evidence in paper artifacts.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` footnote 2 says the
    discovered algorithms and new mathematical results are available at the
    `google-deepmind/alphaevolve_results` `mathematical_results.ipynb` Colab,
    and Table 2 says shown matrix decompositions can be found in the
    accompanying Google Colab.
  - Status: `papers/companion_sources.json` now records the external
    AlphaEvolve companion-source row, including repository URL/ref, notebook
    URLs, SHA-256 digest, byte count, nbformat, cell count, readability status,
    matrix/constructive-math claim mappings, improved-results-only selection
    policy, runtime-code absence, companion repository rights/disclaimer
    metadata, docs/TODO claim-surface links, and local-cache policy.
    Paper-manifest validation checks the companion file.
  - Remaining gap: none for this bounded paper-facing source-manifest slice;
    generated notebook/export artifacts, per-claim absence reasons, and deeper
    claim-to-cell spans remain active paper work.

- [x] Normalize full AlphaEvolve References-section bibliography evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` includes a numbered
    References section after Author information, with entries through `[120]`.
  - Status: `papers/references.json` now records normalized paper-facing
    bibliography rows for all 120 references, including raw citation text,
    bibliographic fields, DOI/URL/arXiv fields where detected, source page,
    local-cache linkage, and citation-use category.
  - Remaining gap: none for this bounded paper-facing bibliography table;
    claim-specific citation mappings remain separate active paper work.

- [x] Emit AlphaEvolve source-PDF rights and license provenance.
  - Paper evidence: page 1 of `2506.13131__AlphaEvolve.pdf` states
    `© 2025 Google DeepMind. All rights reserved`.
  - Status: `papers/source_rights.json` now records cached source-PDF rights
    for the AlphaEvolve row, including rights holder/year, rights statement,
    source page/location, local PDF hash/bytes, row-identity link, and
    reproduction-policy boundaries for paper-derived artifact classes.
  - Remaining gap: none for this bounded paper-facing source-PDF rights slice;
    companion repository rights remain a separate active paper TODO.

- [x] Emit paper-manifest row identity evidence before claim artifacts.
  - Paper evidence: AlphaEvolve-alignment paper audits depend on the local
    paper cache preserving the correct source PDF for each paper-facing row.
  - Status: `papers/row_identity.json` now records source-identity evidence for
    every cached paper row: manifest row id, URL source id where applicable,
    file source prefix, validation status booleans, SHA-256, and the
    AlphaEvolve row's link to `papers/source_versions.json`.
  - Remaining gap: none for this bounded paper-facing row-identity slice;
    source-rights metadata and reproduction policies remain active paper TODOs.

- [x] Emit AlphaEvolve source-PDF arXiv version provenance in paper artifacts.
  - Paper evidence: page 1 of `2506.13131__AlphaEvolve.pdf` identifies the
    audited source as `arXiv:2506.13131v1 [cs.AI] 16 Jun 2025`.
  - Status: `papers/source_versions.json` now records the AlphaEvolve
    `2506.13131v1` source-version row with arXiv id/category/date, floating and
    version-pinned URLs, expected header page/text, cached PDF hash/bytes, and
    claim-surface links. Paper-manifest validation checks the companion file,
    row hash/bytes, and local first-page header.
  - Remaining gap: none for this bounded paper-facing source-version slice;
    source-row identity claim links and source-rights metadata remain separate
    active paper TODOs.

- [x] Track cross-run prompt-current binding table evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Figure 3(b,c) and Section
    2.3.
  - Status: paper-facing docs now cite
    `prompt_current_binding_table.jsonl`, whose schema-versioned rows carry run
    ids, candidate ids, prompt ids, hashes, row joins, and binding summaries
    for cross-run comparison.
  - Remaining gap: none for this bounded paper-facing prompt-current evidence
    item; the evidence remains diagnostic provenance rather than a hard
    semantic proof.

- [x] Track full-mode target span and block-id records in prompt-current
      binding evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Figure 3(b,c) and Section
    2.3.
  - Status: paper-facing docs now cite prompt-current binding records that
    capture full-mode whole-file and evolve-block target spans, block names,
    and parent/candidate content hashes.
  - Remaining gap: none for this bounded paper-facing prompt-current evidence item.

- [x] Track prompt-history row joins in prompt-current binding evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Figure 3(b,c) and Section
    2.3.
  - Status: paper-facing docs now cite prompt-current binding records that
    link generated candidate ids to `history.jsonl` rows and to
    `prompt_history.jsonl` add/score rows by prompt-program id and score
    metadata `last_program_id`.
  - Remaining gap: none for this bounded paper-facing prompt-current evidence item.

- [x] Track workspace file-section span records in prompt-current binding
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Figure 3(b,c) and Section
    2.3.
  - Status: paper-facing docs now cite prompt-current binding records that
    capture file-section operations, target paths, payload body hashes/sizes,
    and parent/candidate full-file span and hash evidence when available.
  - Remaining gap: none for this bounded paper-facing prompt-current evidence item.

- [x] Track evolve-block inner span mapping in prompt-current binding
      evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Figure 3(b,c) and Section
    2.3.
  - Status: paper-facing docs now cite prompt-current binding records that map
    exact SEARCH matches inside parent evolve-block content to block name,
    outer/content spans, and block-relative SEARCH span.
  - Remaining gap: none for this bounded paper-facing prompt-current evidence item.

- [x] Track normalized and skeleton prompt-example copy diagnostics.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Figure 3(b,c) and Section
    2.3.
  - Status: paper-facing docs now cite
    `runtime.history.prompt_example_copy_report` as recording exact,
    normalized file-section-region, and simple example-format skeleton copy
    signals with candidate status/admission metadata.
  - Remaining gap: custom prompt-template inventories, broader
    semantic/renamed copy detection, and hard or configurable acceptance
    policy remain active paper TODOs.

- [x] Track current-run multi-edit consistency diagnostics separately from
      prompt instructions.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Figure 3(b).
  - Status: paper-facing docs now distinguish prompt guidance from
    `runtime.history.mutation_consistency_report`, which records multi-edit
    payloads, changed edit units, co-change links, best-effort Python symbol
    scans, unresolved references, evaluator status, and archive admission.
  - Remaining gap: required companion-edit inference, language-aware
    scope/import/resource models, calibrated consistency taxonomy, and hard or
    configurable acceptance policy remain active paper TODOs.

- [x] Track bounded natural-language preambles separately from structured
      proposal metadata.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Figure 3(c) and Section
    2.3.
  - Status: generated candidates now keep structured
    `IDEA`/`RATIONALE`/`HYPOTHESIS` proposal metadata separate from bounded
    leading freeform preamble metadata. Completed manifests include
    `runtime.history.natural_language_preamble_report`, and the paper index
    lists bounded leading explanatory-preamble capture/reporting as partial
    AlphaEvolve support.
  - Remaining gap: arbitrary interleaved/trailing prose, raw full replacement
    preamble disambiguation, semantic rationale-quality scoring, and cross-run
    preamble/proposal joins remain active paper TODOs.

- [x] Track canonical AlphaEvolve diff-fence guidance separately from compact
      compatibility syntax.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.3 and Figure 3 use
    canonical SEARCH/REPLACE fences with `<<<<<<< SEARCH`, `=======`, and
    `>>>>>>> REPLACE`.
  - Status: paper-facing status can point to README, ROADMAP, prompt
    instructions, parser tests, and `AGENTS.md` all presenting canonical
    AlphaEvolve fences as the primary paper-spec syntax, with compact fences
    scoped to compatibility support.
  - Remaining gap: none for diff-fence guidance; natural-language preambles,
    prompt-example copy detection, and multi-edit consistency remain separate
    paper TODOs.
  - Verification: validation for this slice reran the paper manifest, secret
    scan, and diff checks before commit.

- [x] Add paper-visible validation for meta-prompt context-policy capabilities.
  - Paper evidence: AlphaEvolve prompt evolution includes prompt/context
    improvement, so the structured controls exposed to meta-prompt mutation
    should match the implemented prompt policy schema.
  - Status: `validate_meta_prompt_context_policy_capabilities()` now validates
    `libreevolve.meta_prompt_context_policy_capabilities.v1` before it is
    rendered as meta-prompt evidence. It checks schema, required sections,
    malformed fields, duplicate fields, unsupported fields, and exact coverage
    of the current `libreevolve.prompt_context_policy.v1` keys.
  - Remaining paper gap: this makes the advertised capability surface
    auditable, but does not provide semantic context-policy search,
    provider-aware allocation, or cross-task proof that evolved policies
    improve prompts.
  - Verification: focused loop tests cover exact field coverage and malformed,
    missing, duplicate, and unsupported advertised fields.

- [x] Add paper-visible validation for archive-event replay audits.
  - Paper evidence: AlphaEvolve-style island-model resume needs migration
    placement evidence that can be audited while clearly separating final
    archive-content restore from unsupported ordered migration replay.
  - Status: `validate_archive_event_replay_audit()` now validates
    `runtime.history.archive_event_replay_audit` summaries with schema
    `libreevolve.archive_event_replay_audit.v1`, including schema/status,
    audit-only and no-restore-engine flags, event and placement count
    consistency, retained mismatch shape, mismatch retention limits,
    verified/absent status invariants, and required audit-boundary
    limitations.
  - Remaining paper gap: this makes audit evidence checkable, but migration
    placement rows are still not a full restore engine and controller
    pending-work replay remains open.
  - Verification: focused database tests cover verified, superseded, and
    absent audit summaries plus restore-engine overclaims, count
    inconsistencies, and malformed retained mismatch records.

- [x] Add paper-visible validation for multi-objective history diagnostics.
  - Paper evidence: AlphaEvolve optimizes multiple user-provided scores and
    needs reproducible evidence for which programs excel under each declared
    metric and which retained programs are non-dominated.
  - Status: `validate_objective_history_summary()` now validates
    `runtime.history.objective_frontier`,
    `runtime.history.objective_metric_leaders`, and
    `runtime.history.objective_metric_archives` together, checking schema and
    policy values, shared metric order, non-negative counters, retained-count
    and retention-limit consistency, normalized metric ranges, non-dominated
    retained frontier records, and explicit diagnostic-not-primary-archive
    limitation statements.
  - Remaining paper gap: this is a validator for diagnostic runtime evidence,
    not a paper-faithful primary archive replacement or durable
    multi-objective database query layer.
  - Verification: focused objective-history tests cover real database
    snapshots, manifest JSON loading, frontier overclaim rejection,
    metric-order mismatch rejection, archive count/retention failures, and
    malformed program records.

- [x] Add paper-visible provider diagnostics summary validation.
  - Paper evidence: AlphaEvolve-style experiments need provider diagnostics and
    cost/latency/accounting evidence that can be inspected from run artifacts
    without implying unsupported raw-payload replay or live billing capture.
  - Status: `validate_llm_provider_diagnostics_summary()` now validates
    `runtime.llm_provider_diagnostics` summaries with schema
    `libreevolve.llm_provider_diagnostics.v1`, including retained-history
    scope, backend-record hash integrity, non-negative counters,
    backend-count and call-count consistency, required limitation statements,
    and the no-live-pricing/no-raw-payload replay boundary.
  - Remaining paper gap: this is a retained-call-history aggregate validator,
    not a live provider-pricing feed, raw provider-payload replay trace, or
    complete restored provider-output controller.
  - Verification: focused diagnostics-policy tests cover a real
    ensemble-produced summary plus JSON loading, overclaim, counter, count, and
    hash failure cases.

- [x] Add paper-visible parent-code per-file content caps.
  - Paper evidence: AlphaEvolve prompt context can include prior code, and
    prompt-context evolution should be able to budget individual required code
    files before aggregate prompt caps apply.
  - Status: prompt context policy now accepts `parent_code_max_chars_by_path`,
    mapping safe candidate-relative parent file paths to non-negative character
    caps. Direct prompt rendering applies the caps to selected mutable parent
    files and persists original/rendered/omitted character counts, truncation
    status, applied caps, and unused cap paths under
    `libreevolve.parent_code_policy.v1`.
  - Remaining paper gap: this is deterministic per-file text capping, not
    semantic parent-code compression, dependency-aware summarization, or
    provider context allocation.
  - Verification: focused prompt and meta-prompt loop tests cover validation,
    rendering, diagnostics, and accepted policy JSON.

- [x] Add paper-visible parent-code render-count limiting.
  - Paper evidence: AlphaEvolve prompt context can include prior code, and
    prompt-context evolution should have replayable controls over how many
    selected required code files are shown under prompt budgets.
  - Status: prompt context policy now accepts nullable `parent_code_limit`.
    Direct prompt rendering applies it after parent-code path selection, term
    filtering, and ordering, including `0` to suppress mutable parent file
    bodies. Diagnostics persist pre-limit order, rendered paths,
    omitted-by-limit paths, selected/omitted counts, and a selection hash under
    `libreevolve.parent_code_policy.v1`.
  - Remaining paper gap: this is deterministic file-count limiting, not
    semantic parent-code compression, provider context allocation, or learned
    source relevance.
  - Verification: focused prompt and meta-prompt loop tests cover validation,
    rendering, diagnostics, and accepted policy JSON.

- [x] Add paper-visible parent-code relevance ordering.
  - Paper evidence: AlphaEvolve prompt context can include prior code, and
    prompt-context evolution should have replayable controls for prioritizing
    relevant required code context before rendering.
  - Status: prompt context policy now accepts `parent_code_order_policy`
    (`path_order` or `task_term_ranked`) and optional
    `parent_code_ranking_terms`. Direct prompt rendering ranks parent-code
    files after path selection and term filtering, then persists query source,
    query hash/count, ranks, scores, candidate/selected counts, and a ranking
    hash in `libreevolve.parent_code_order_policy.v1` nested under
    `libreevolve.parent_code_policy.v1`.
  - Remaining paper gap: this is lexical overlap ranking, not semantic
    parent-code retrieval, dependency-aware ranking, or learned relevance.
  - Verification: focused prompt and meta-prompt loop tests cover validation,
    rendering, diagnostics, and accepted policy JSON.

- [x] Add paper-visible parent-code term filtering.
  - Paper evidence: AlphaEvolve prompt context can include prior code, and
    prompt-context evolution should have a replayable way to focus required
    code context on relevant source terms before rendering.
  - Status: prompt context policy now accepts safe
    `parent_code_required_terms` and `parent_code_excluded_terms`. Direct
    prompt rendering filters selected parent-code files by path/content terms
    and persists candidate/selected/omitted counts, omitted paths by required
    or excluded terms, and a selection hash in
    `libreevolve.parent_code_term_filter.v1` nested under
    `libreevolve.parent_code_policy.v1`.
  - Remaining paper gap: this is deterministic term matching, not semantic
    parent-code retrieval, dependency-aware ranking, or learned relevance.
  - Verification: focused prompt and meta-prompt loop tests cover validation,
    rendering, diagnostics, and accepted policy JSON.

- [x] Add paper-visible parent-code file selection policy.
  - Paper evidence: AlphaEvolve prompt context can include prior code, and
    useful prompt-context evolution should focus required code context on
    relevant files rather than always rendering the full workspace.
  - Status: prompt context policy now accepts `parent_code_paths`, a safe
    ordered parent-workspace file allowlist. Direct prompt rendering applies it
    before parent-code caps/truncation, records requested/rendered/omitted/
    missing paths in `libreevolve.parent_code_paths.v1` metadata nested inside
    `libreevolve.parent_code_policy.v1`, and exposes the field in the
    meta-prompt capability manifest.
  - Remaining paper gap: this is deterministic exact-path selection, not
    semantic parent-code retrieval, dependency-aware ranking, or learned source
    relevance.
  - Verification: focused prompt and meta-prompt loop tests cover validation,
    rendering, diagnostics, and accepted policy JSON.

- [x] Add paper-visible parent-code truncation policy.
  - Paper evidence: AlphaEvolve prompt context can include prior code; useful
    prompt-context evolution should control which parts of required code
    context survive bounded rendering.
  - Status: prompt context policy now accepts `parent_code_truncation` with
    safe `head` and `head_tail` values. Direct prompt rendering applies the
    selected mode when `parent_code_max_chars` truncates the required
    parent-code workspace channel, persists the mode in
    `libreevolve.parent_code_policy.v1`, and exposes it in the meta-prompt
    capability manifest.
  - Remaining paper gap: this remains deterministic character-level retention,
    not semantic parent-workspace summarization, provider-token allocation, or
    replayable backend context budgeting.
  - Verification: focused prompt and meta-prompt loop tests cover validation,
    rendering, diagnostics, and accepted policy JSON.

- [x] Add paper-visible parent-code context cap.
  - Paper evidence: AlphaEvolve prompt context can include prior code and
    execution-derived state; meta-prompt evolution should be able to control
    required context volume, not only optional rendered sections.
  - Status: prompt context policy now accepts nullable
    `parent_code_max_chars`, and direct prompt rendering applies it to the
    required parent-code workspace channel while preserving an explicit
    omission marker for `0`. Prompt diagnostics persist
    `libreevolve.parent_code_policy.v1` metadata with source, cap,
    truncation, character counts, and hashes, and the meta-prompt capability
    manifest exposes the field to LLM-mutated policy JSON.
  - Remaining paper gap: this is bounded character-level parent-code control,
    not semantic parent-workspace summarization, automatic tokenizer-budgeted
    backend packing, or full replayable provider budget state.
  - Verification: focused prompt and meta-prompt loop tests cover validation,
    rendering, diagnostics, and accepted policy JSON.

- [x] Add provider-token counter evidence for prompt section packing.
  - Paper evidence: AlphaEvolve prompt construction is model-context-budgeted;
    useful long-context replay evidence needs token-aware prompt packing
    diagnostics, not only character counts.
  - Status: direct `PromptSampler` callers can now pass a provider token
    counter and manifest-safe counter name. Section-priority packing then uses
    exact token counts under `max_prompt_estimated_tokens` and persists
    provider-token totals/counter provenance in prompt diagnostics and
    `libreevolve.prompt_section_budget.v1` records.
  - Remaining paper gap: this is a direct-call primitive, not automatic
    selected-backend tokenizer discovery/wiring for the normal evolution path
    or a complete provider-token/cost resume contract.
  - Verification: focused prompt tests cover exact token-counter packing and
    fail-closed invalid counter results.

- [x] Add paper-visible runtime LLM provider diagnostics aggregate.
  - Paper evidence: AlphaEvolve-style compute budgeting and provider
    orchestration require auditable evidence for which backend/API mode
    produced usage, diagnostics, retry, and cost-estimate signals.
  - Status: final runtime manifests now include
    `runtime.llm_provider_diagnostics` with schema
    `libreevolve.llm_provider_diagnostics.v1`, summarizing retained LLM call
    history by backend index/name and API mode with provider usage totals,
    bounded diagnostic key counts, omitted diagnostic counts, configured
    cost-estimate evidence, not-estimated reasons, backend-default API modes,
    retention metadata, limitations, and a records hash.
  - Remaining paper gap: this is bounded local telemetry and configured-cost
    evidence, not live provider pricing, unbounded raw provider payload
    retention, or remote provider-default discovery.
  - Verification: focused ensemble and loop tests cover aggregate contents and
    zero-generation fallback records.

- [x] Add paper-visible matrix publication artifact inventory verification.
  - Paper evidence: AlphaEvolve Appendix A publishes exact matrix algorithms
    and notebook-linked constructions, so report metadata should verify the
    files it names.
  - Status: `libreevolve.matrix_result_artifact_inventory.v1` now verifies
    declared matrix report artifacts under an explicit artifact root, checking
    safe relative paths, existence, actual SHA-256 hashes, byte counts, and
    inventory-level verified/missing/mismatch/invalid counts.
  - Remaining paper gap: this is physical artifact verification for declared
    files, not generation of exact tensor algorithms, exactness certificate
    artifacts, or Colab/notebook exports for registered Appendix A targets.
  - Verification: focused matrix-result tests cover verified inventories and
    missing, mismatched, and unsafe artifact references.

- [x] Add paper-visible retrieval source grounding records.
  - Paper evidence: retrieval-driven refinement treats external knowledge as a
    run input, so retained sources need provenance explaining why they were
    relevant to the prompt.
  - Status: DeepResearch retrieval events now attach
    `libreevolve.retrieval_source_grounding_policy.v1` records to retained
    sources, aggregate them under `source_grounding_policy`, link the aggregate
    from active prompt-context metadata, and expose the same counts/hash through
    the retrieval evidence-boundary policy.
  - Remaining paper gap: this remains deterministic lexical grounding over
    bounded retained text, not learned/external semantic ranking,
    source-content semantic verification, unbounded raw provider/source
    payload retention, or replayable transport/TLS evidence.
  - Verification: focused DeepResearch tests cover payload-artifact,
    arXiv-provider, query-overlap ranking, active-context, and boundary-policy
    grounding evidence.

- [x] Add a runtime hypothesis index for captured proposal metadata.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes a
    program database that resurfaces prior programs and ideas as inspirations
    for future LLM proposals.
  - Status: final runtime manifests now include
    `runtime.history.hypothesis_index`, a bounded redacted/hash-backed view of
    proposal idea, rationale, and hypothesis text for valid programs with
    captured proposal metadata. Hypothesis records now also participate in the
    runtime resurfacing rank-fusion index.
  - Remaining paper gap: this does not yet provide cross-run semantic
    hypothesis retrieval, learned idea ranking, or a full durable program
    database.
  - Verification: focused database and loop tests cover captured proposal
    indexing, invalid-program exclusion, resurfacing integration, and manifest
    schema persistence.

- [x] Add a runtime failure index grouped by failure fingerprint.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes a
    program database that resurfaces prior attempts; failed proposals and
    repeated failure modes are part of the evidence needed for useful future
    prompting and search steering.
  - Status: final runtime manifests now include
    `runtime.history.failure_index`, a bounded grouping of validated failure
    records by fingerprint with repetition counts, changed files, latest
    representative record, and bounded redacted evaluation summaries.
  - Remaining paper gap: this does not yet provide cross-run failure
    persistence, semantic failure clustering, learned negative-evidence
    retrieval, or a full durable program database.
  - Verification: focused database and loop tests cover repeated-fingerprint
    grouping, latest-record evidence, bounded summaries, and manifest schema
    persistence.

- [x] Add a bounded resurfacing index over existing candidate evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes a
    program database that resurfaces diverse prior programs as inspirations for
    future LLM proposals.
  - Status: final runtime manifests now include
    `runtime.history.resurfacing_index`, a deterministic rank-fusion view over
    score, objective-frontier, metric, lineage, descriptor, and feedback
    indexes. `ProgramDatabase.resurface_candidates()` exposes the same ranked
    deduplicated source mix as defensive program snapshots.
  - Remaining paper gap: this is not yet a durable persisted program database
    with learned retrieval, full lineage/failure/hypothesis/artifact indexes,
    or versioned schema migration across legacy/current run records.
  - Verification: focused database and loop tests cover rank-fusion source
    evidence, invalid-program exclusion, defensive candidate snapshots, and
    manifest persistence.

- [x] Add bounded Pareto archive retention to MAP-Elites.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes
    optimizing multiple user-provided scores and using programs that excel
    under different criteria as varied inspirations.
  - Status: MAP-Elites archives now maintain a bounded non-dominated retention
    archive over complete declared normalized metric vectors, persist/restore
    Pareto frontier program ids and the objective archive policy, and surface
    Pareto-retained programs through island metric/frontier retained pools.
  - Remaining paper gap: this does not yet make MAP-Elites cell replacement
    metric-specific or Pareto-dominance based, and it does not provide a
    durable queryable multi-objective program database.
  - Verification: focused MAP-Elites and island tests cover Pareto-only
    retention, snapshot restore, and frontier sampling from Pareto-retained
    programs.

- [x] Allow declared final-fitness objective metrics.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes
    optimizing multiple user-provided scores; plugin-adjusted final score can
    now be included as one declared objective dimension when configured.
  - Status: non-primary metrics can now declare `source: final_fitness`.
    LibreEvolve synthesizes those metrics from the candidate's final composed
    fitness after plugin score hooks run, and includes them in normalized
    objective vectors, selection score, archive-admission objective-vector
    audit records, metric leaders, metric archives, and complete-vector
    frontier views.
  - Remaining paper gap: Pareto/frontier archive replacement plus queryable
    lineage-aware resurfacing remain open.
  - Verification: focused loader and loop tests cover schema validation,
    post-plugin final-fitness objective metrics, selection-score
    participation, objective vectors, and metric archive manifest output.

- [x] Allow declared plugin-sourced objective metrics.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes
    optimizing multiple user-provided scores and using varied high-performing
    programs under different criteria.
  - Status: non-primary metrics can now declare `source: plugin`. Plugin hooks
    can fill those declared metrics through validated metric side effects, and
    the resulting values participate in normalized objective vectors,
    selection score, archive-admission objective-vector audit records, metric
    leaders, metric archives, and complete-vector frontier views.
  - Remaining paper gap: Pareto/frontier archive replacement plus queryable
    lineage-aware resurfacing remain open.
  - Verification: focused loader and loop tests cover schema validation,
    plugin-filled objective metrics, selection-score participation, objective
    vectors, and metric archive manifest output.

- [x] Add bounded metric-specific objective archive views.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes
    optimizing multiple user-provided scores and using programs that excel
    under different criteria as varied inspirations.
  - Status: final runtime manifests now include
    `runtime.history.objective_metric_archives`, a bounded
    top-program-per-declared-normalized-metric view. Each metric archive
    records considered and retained counts plus retained program ids,
    generations, normalized metric values, selection scores, and available
    declared normalized metric vectors.
  - Remaining paper gap: this is still an in-memory diagnostic view, not
    Pareto/frontier archive replacement, plugin-objective integration, or
    queryable lineage-aware resurfacing.
  - Verification: focused database and loop tests cover top-program ordering,
    invalid metric/evaluation exclusion, retention metadata, and final manifest
    persistence.

- [x] Add Pareto-frontier parent and inspiration sampling.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes
    optimizing multiple user-provided scores and using programs that excel
    under different criteria as varied inspirations.
  - Status: parent and inspiration sampling now support a `frontier` strategy
    over complete declared normalized metric vectors. Parent sampling cycles
    through non-dominated retained programs, inspiration sampling returns
    non-dominated retained programs after exclusions, and generated candidate
    metadata records frontier size and declared metric order.
  - Remaining paper gap: the policy is still heuristic and in-memory; it does
    not provide Pareto archive replacement, plugin-objective integration, or
    queryable lineage-aware resurfacing.
  - Verification: focused tests cover frontier parent cycling, frontier
    inspirations, fallback without declared objective metrics, cursor restore,
    and CLI strategy acceptance.

- [x] Add bounded fallback prompt rendering for validator metadata.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.2, says prompt
    context can include execution results and feedback from previous attempts.
  - Status: mutation prompt feedback now renders a bounded, redacted
    `validator_metadata` diagnostic line for JSON-safe validator metadata keys
    not already handled by specialized prompt renderers. It uses deterministic
    key ordering, stable JSON serialization, SHA-256 value digests, omission
    counts, and JSON escaping so delimiter-like metadata remains prompt data.
  - Remaining paper gap: prompt rendering still does not expose a
    configurable/full validator-metadata policy or exact provider-token
    context-window packing across evaluator, feedback, artifact, and context
    sections.
  - Verification: focused prompt tests cover rendered validator metadata,
    secret redaction, specialized-key exclusion, value hashes, and prompt
    delimiter safety.

- [x] Add structured prompt-program context policy hooks.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4,
    describe prompt-context and prompt-instruction improvement through the
    evolutionary system.
  - Status: prompt programs now persist and replay a structured
    `libreevolve.prompt_context_policy.v1` policy separate from template text.
    The policy can alter optional prompt-channel inclusion and section-packing
    priorities, and meta-prompt mutations can return a strict JSON object with
    a revised `template` plus optional `context_policy`.
  - Remaining paper gap: source selection, retrieval/summarization,
    inspiration policy, feedback-field policy, stochastic formatting
    distributions, and mutation-instruction variants are still broader open
    context-policy work.
  - Verification: focused prompt and meta-prompt tests cover policy rendering,
    history persistence/replay, and JSON mutation responses.

- [x] Add a runtime Pareto frontier diagnostic for declared objective metrics.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.4, describes
    optimizing multiple user-provided scores and using high-performing
    programs under different criteria as inspirations.
  - Status: final runtime manifests now include
    `runtime.history.objective_frontier`, a bounded Pareto-frontier diagnostic
    over complete declared normalized metric vectors. It records schema,
    policy, metric order, considered count, frontier size, retained limit, and
    non-dominated program metric vectors.
  - Remaining paper gap: the persisted frontier is diagnostic only;
    metric-specific archives, Pareto/frontier archive replacement,
    plugin-objective integration, and queryable lineage-aware resurfacing
    remain open.
  - Verification: focused database and loop tests cover non-dominated
    frontier selection, dominated-program exclusion, metric order, and runtime
    manifest persistence.

- [x] Apply restored runtime budget snapshots to live resumed runs.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` frames throughput and
    ablations under explicit compute budgets; resumed searches should not
    silently reset consumed budget counters.
  - Status: restored manifest runtime budget snapshots are now live inputs to
    `evolve()` and the CLI. Restored evaluation, LLM call/provider-attempt,
    token, configured-cost, latency, generation, and runtime counters are
    applied before new work, with prior runtime seconds counted against
    `max_runtime_seconds` and final manifests carrying appended resume
    segments.
  - Remaining paper gap: full controller/pending-work replay, accelerator and
    async-worker budgets, emitted controller event logs, hard provider
    cancellation, and benchmark scripts emitting equal-budget reports remain
    open.
  - Verification: focused budget and loop tests cover restored snapshot
    counter application, manifest loading, limit mismatch rejection, and
    exhausted restored-budget stop behavior before seed evaluation.

- [x] Implement MAP-Elites behavior descriptors beyond the fixed local
  workspace-text archive.
  - Paper evidence: `1504.04909__MAP_Elites.pdf` maps elites over
    user-chosen dimensions of variation to illuminate high-performing
    solutions across a behavior space.
  - Status: `Config.map_elites_descriptor_axes` now selects exactly three
    MAP-Elites axes from built-in performance/complexity/diversity,
    normalized evaluator metrics, numeric evaluator metadata, or numeric
    candidate metadata. `MAPElites`, island construction, manifest config, and
    archive snapshots persist and validate the configured axes while preserving
    the existing default archive behavior.
  - Remaining paper gap: stable learned diversity descriptor modeling,
    explicit rebinning, richer illuminated-search-space diagnostics, and
    larger AlphaEvolve-scale archive/controller semantics remain separate open
    gaps.
  - Verification: focused config, MAP-Elites, island, database manifest, docs,
    and paper-manifest tests cover configured axes, invalid axes, snapshot
    mismatch rejection, island propagation, manifest persistence, and public
    documentation.

- [x] Implement independent per-role LLM routing, quotas, and reward policy.
  - Paper: `2506.13131__AlphaEvolve.pdf`, ensemble-throughput and quality
    framing.
  - Status: LibreEvolve now has explicit per-role backend routing through
    `llm_role_backend_indices`, per-role logical/provider/token/cost/seconds
    quota maps, configurable reward-accounted roles, feedback-grader reward
    wiring for configured feedback roles, role-scoped scheduler state, durable
    call-ledger role summaries, and runtime accounting snapshots that preserve
    the effective routing and reward policies.
  - Remaining paper gap: role-specific provider quarantine/penalty behavior
    and complete live provider budget enforcement remain tracked separately.
  - Verification: config, ensemble, manifest/runtime-accounting, and docs tests
    cover explicit routing, metadata fallback, policy telemetry, restore-safe
    scheduler snapshots, and visible documentation.

- [x] Add configurable quarantine snapshot retention to paper evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Status: framework-owned quarantine record snapshots and torn JSONL
    fragment previews now support `full`, `redacted`, `hash_only`, and `off`
    through `quarantine_snapshot_retention_mode`. Quarantine diagnostics keep
    bounded secret-redacted messages, while rejected-record and torn-fragment
    snapshot text can be retained, hashed, or suppressed according to policy.
    Startup manifests expose `quarantine_record_snapshots` under
    `policies.prompt_data_retention`.
  - Remaining paper gap: replay retention remains open.
  - Verification: focused JSONL, config, ProgramDatabase, PromptDatabase, and
    manifest tests cover mode validation, hash-only/off snapshot suppression,
    torn-fragment off retention, secret-like value suppression, and manifest
    policy emission.

- [x] Add configurable explicit-context retention to paper evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Status: explicit context spans inside persisted rendered mutation prompts
    now support `full`, `redacted`, `hash_only`, and `off` through
    `explicit_context_retention_mode`. Provider-visible prompts still receive
    the rendered context, while prompt history can retain, hash, or suppress
    that context span according to policy.
  - Remaining paper gap: replay retention still needs explicit configurable
    policy.
  - Verification: focused config, loop, and manifest tests cover mode
    validation, provider-visible context preservation, hash-only/off persisted
    suppression, explicit-context hash metadata, and manifest policy emission.

- [x] Add configurable DeepResearch retrieval body retention to paper evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Status: DeepResearch retrieval provider-result snapshots and cached
    synthesis bodies now support `full`, `redacted`, `hash_only`, and `off`
    via `retrieval_body_retention_mode`. Prompt-visible retrieval context still
    receives bounded secret-redacted synthesis, while persisted event/cache
    bodies can be retained, hashed, or suppressed according to policy.
  - Remaining paper gap: replay retention still needs explicit configurable
    policy.
  - Verification: focused DeepResearch, config, loop, and manifest tests cover
    mode validation, hash-only/off persistence behavior, default retention
    metadata, runtime plugin-state capture, and manifest policy emission.

- [x] Add configurable meta-prompt evidence retention to paper evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Status: `meta_prompt_evidence_retention_mode` now supports `full`,
    `redacted`, `hash_only`, and `off`. Meta-prompt prompt-history metadata
    records `evidence_retention`; `full`/`redacted` keep bounded
    secret-redacted evidence text, `hash_only` keeps only hashes/counts by
    default, and `off` suppresses evidence text plus hashes/lengths.
  - Remaining paper gap: replay retention still needs explicit configurable
    policy.
  - Verification: focused config, loop, and manifest tests cover mode
    validation, persisted redacted/off behavior, default hash-only behavior,
    secret suppression, and manifest policy emission.

- [x] Narrow run replay/provenance paper TODO to replay, lineage, provider, and
  custom-plugin policy gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Status: the active paper TODO no longer asks for evaluator import/data
    provenance, configured plugin specs, aggregate emitted-artifact hashes, or
    run-artifact inventory hardening as generic missing work. Current evidence
    covers those surfaces through problem-local evaluator dependency
    provenance, configured plugin/entry-point specs, runtime artifact hashes,
    startup/overwrite safety, and provider-readiness preflight.
  - Remaining paper gap: full-run resume/replay semantics, deterministic
    lineage-id policy or explicit UUID exclusion, provider-output replay
    boundaries, arbitrary direct-plugin constructor value/schema policy, richer
    custom plugin package provenance, and live provider-authentication evidence
    beyond local client construction remain open.
  - Verification: focused evaluator provenance, database startup/overwrite,
    loop provider-preflight, CLI preflight, ablation, cancellation, and budget
    report tests cover the implemented evidence surfaces.

- [x] Require consistent per-seed budget units for ablation curves.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 8 and Section 4.
  - Status: `libreevolve.alphaevolve_ablation_report.v1` now validates that
    each variant/target/seed curve uses one budget unit and limit across all
    required budget fractions.
  - Remaining paper gap: real benchmark scripts still do not execute and emit
    these equal-budget reports, and broader runtime budget enforcement remains
    open.
  - Verification: focused ablation-result tests cover inconsistent seed budget
    unit/limit.

- [x] Require systems ready gates to have matching artifact kinds.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 3.3.
  - Status: `libreevolve.systems_result_report.v1` now requires
    `alphaevolve_ready` reports to include artifact kinds matching passed
    optimization, held-out, and reference-correctness gates.
  - Remaining paper gap: no real systems fixture emits held-out or randomized
    reference-correctness reports yet.
  - Verification: focused systems-result tests cover missing gate artifacts.

- [x] Require certification artifacts matching passed evidence kinds.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 3.3 and 4.
  - Status: `libreevolve.paper_result_certification.v1` now rejects
    paper-claim-ready records whose passed evidence kind lacks the matching
    artifact kind, such as verifier output without a verifier log.
  - Remaining paper gap: this is still a report contract; real independent
    verifier scripts, human-review records, deployment measurements, and exact
    certificate artifacts remain open.
  - Verification: focused certification tests cover missing evidence-artifact
    linkage for paper claims.

- [x] Validate matrix-result best-rank and hit-rate consistency against
  per-seed records.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 3.1 and Appendix A.
  - Status: `libreevolve.matrix_result_report.v1` now validates that reported
    best rank and hit-rate fields are consistent with per-seed ranks and
    `achieved_best_rank` flags.
  - Remaining paper gap: the contract still lacks real 54-target tensor
    reports, exact algorithm artifacts, and notebook/export equivalents.
  - Verification: focused matrix-result tests cover inconsistent best rank and
    missing per-seed hit flags.

- [x] Link benchmark hardening shortcut threats to protected signals.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 3 and 4.
  - Status: the benchmark-hardening contract now requires every shortcut
    threat to identify the protected benchmark signal it targets, such as
    correctness, operation count, rank, score, or construction artifact.
  - Remaining paper gap: no real benchmark-grade validator yet emits validated
    hardening reports from randomized/exhaustive anti-gaming fixtures.
  - Verification: focused benchmark-hardening tests cover known, missing,
    duplicate, unknown, and malformed protected-signal references.

- [x] Record shared-versus-role-specific LLM scheduler policy per call.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Status: LLM call telemetry now makes the scheduler boundary explicit:
    routing uses the shared `global_backend_bandit`, while sorted
    `reward_accounted_roles` state which roles can update reward accounting.
  - Remaining paper gap: this is audit evidence, not the paper-level behavior
    of independent per-role routing, quotas, or budget-coupled scheduler
    policies.
  - Verification: focused ensemble tests cover scheduler-policy telemetry for
    both throughput/depth calls and telemetry-only non-reward-accounted roles.

- [x] Link provider cancellation policy rules to required artifact kinds.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.6, and 4.
  - Status: provider cancellation policy validation now ties
    `artifact_required` timeout/cancellation rules to explicit artifact kinds
    and rejects policies whose required kinds are missing from the artifact
    list. Runtime manifests now declare timeout logs and budget-stop records as
    the evidence surfaces for the current soft-timeout policy.
  - Remaining paper gap: the policy remains an audit contract; live hard
    provider cancellation, timeout-driven role-specific stop/quarantine
    behavior, and persisted retry-budget enforcement remain open.
  - Verification: focused cancellation-policy and runtime-manifest tests cover
    artifact-kind linkage and runtime policy evidence.

- [x] Add bounded prompt-visible evaluator artifact content excerpts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Status: copied UTF-8 evaluator artifacts now retain redacted, bounded
    stored-content excerpts under policy `stored_utf8_artifact_excerpt_v1`,
    and prompt construction can render those excerpts from artifact metadata.
    Binary and non-UTF-8 artifacts record no-excerpt status instead of
    attempting unsafe prompt inclusion.
  - Remaining paper gap: prompts still do not retrieve or render full artifact
    contents, full validator metadata, or token-aware section-priority packing
    across all feedback/context sections.
  - Verification: focused evaluator and prompt tests cover UTF-8 excerpts,
    redaction, binary/non-UTF-8 status, and prompt-visible excerpt rendering.

- [x] Add package-source interpretation policy to reproducibility manifests.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.6 and 4.
  - Status: runtime environment provenance now emits an audit-only
    `package_source_policy` record tying lockfile, installed-package,
    `pip freeze`, and `pip config` evidence to explicit redaction, retention,
    unsupported source-resolution, and evidence-hash semantics.
  - Remaining paper gap: this does not verify remote package artifacts,
    private package-index identity/authentication, live provider service/API
    versions, or non-pip source managers.
  - Verification: focused provenance tests cover normal and degraded
    package-source policy evidence.

- [x] Emit runtime LLM budget-report records in paper-facing manifests.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.6, and 4.
  - Status: completed and aborted manifests can now expose a concrete
    `runtime.llm_budget_report` object using
    `libreevolve.llm_budget_report.v1`, derived from validated scheduler
    state and role accounting with observed logical calls, retries,
    provider-internal attempts, token totals, and scheduler-state hashes.
  - Remaining paper gap: the report remains non-paper-ready because live
    token, cost, wall-clock, provider-attempt, and per-role retry budgets are
    not enforced or restored as budget state.
  - Verification: focused runtime-manifest tests validate the emitted report
    with the paper-facing budget-report validator.

- [x] Restore persisted LLM ensemble scheduler state into new runs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Status: `runtime.llm_scheduler` snapshots can now be loaded from
    `manifest.json` and restored through direct `evolve()` or
    `--restore-llm-scheduler-from-manifest`; restored final manifests record
    `snapshot_restored_into_evolve`.
  - Remaining paper gap: this restores local scheduler counters, not provider
    output replay, token/cost budget state, controller queues, or independent
    per-role scheduling policies.
  - Verification: focused loop and CLI tests cover scheduler restore semantics.

- [x] Persist metric-targeted inspiration provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Status: generated candidate history now records
    `metadata.inspiration_selection` for inspiration sampling, including
    selected ids and metric target/program pairs when metric-leader inspiration
    policies are used.
  - Remaining paper gap: Pareto/frontier archive replacement and
    plugin-objective integration remain open.
  - Verification: focused island and loop tests cover metric-targeted
    inspiration metadata.

- [x] Correct paper-facing archive identity resume status.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: manifests no longer underclaim archive-state restore in
    `policies.archive_identity`; they now list restored cursor, sequence,
    MAP-Elites cell, and elite-archive surfaces while explicitly preserving the
    migration-event replay gap.
  - Remaining paper gap: one-command resumed experiment traces still lack
    migration-event replay and controller/pending-work state.
  - Verification: focused database tests cover the policy status and restored
    cursor behavior after full archive restore.

- [x] Add prompt section-budget accounting evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Status: generated mutation prompt diagnostics now persist a
    `libreevolve.prompt_section_budget.v1` report with per-placeholder
    priorities, hashes, character counts, estimated tokens, required/optional
    totals, template overhead, and required-section fit status.
  - Remaining paper gap: provider-token context-window packing and evolved
    context policy remain open.
  - Verification: focused prompt and loop tests cover section-budget evidence
    in prompt metadata and history.

- [x] Persist per-role LLM scheduler state in paper-facing manifests.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Status: runtime manifests now include per-role scheduler audit state with
    backend counts, wins, total pulls, and rewarded/unrewarded call ids, plus
    aggregate scheduler totals in `runtime.llm_accounting`.
  - Remaining paper gap: independent per-role routing/quotas, non-mutation
    reward semantics, token/cost budget stops, and live scheduler-state resume
    remain open.
  - Verification: focused LLM ensemble and runtime manifest tests cover the
    persisted per-role scheduler state.

- [x] Add replayable cell/elite archive snapshots to resume evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: final manifests now include `archive_contents` with per-island
    MAP-Elites cell and elite state. `load_archive_restore_bundle()` combines
    that manifest state with accepted history rows, and `ProgramDatabase` can
    restore live cells and elite archives from the resulting bundle.
  - Remaining paper gap: one-command resumed experiment traces and
    migration-event replay remain open.
  - Verification: focused population/database tests cover archive-content
    snapshot/restore from persisted manifest and history evidence.

- [x] Redact persisted mutation prompts while retaining prompt hashes.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Status: generated candidate histories now persist mutation prompts after a
    configurable retention policy and attach `metadata.prompt_retention` with
    mode, retention policy, stored character count, redaction/truncation flags,
    and raw rendered-prompt SHA-256/length metadata when retained by policy.
  - Remaining paper gap: complete data-retention policy across critique,
    feedback, plugin context, provider responses, and replay remains open.
  - Verification: focused loop tests cover direct context secret redaction in
    persisted prompts while preserving the raw prompt hash.

- [x] Add configurable mutation prompt logging modes to paper evidence.
  - Paper evidence: AlphaEvolve-style experiments can include private task
    context, so run artifacts need an explicit persistence policy for rendered
    mutation prompts.
  - Status: `mutation_prompt_retention_mode` now supports `full`, `redacted`,
    `hash_only`, and `off`; paper-facing docs distinguish this implemented
    generated-mutation-prompt surface from remaining per-role retention work.
  - Remaining paper gap: critique, feedback, plugin/context, provider response,
    and replay retention modes are still open.
  - Verification: focused config and loop tests cover accepted/rejected modes
    and persisted history behavior.

- [x] Add configurable critique metadata retention to paper evidence.
  - Paper evidence: AlphaEvolve-style critique/revision traces can include
    source, context, and provider-generated text, so paper artifacts need an
    explicit persistence policy for critique prompts and revised mutations.
  - Status: `critique_retention_mode` now supports `full`, `redacted`,
    `hash_only`, and `off`; paper-facing docs and manifests distinguish this
    implemented critique surface from remaining feedback/provider/plugin/
    context/retrieval/meta-prompt retention work.
  - Remaining paper gap: feedback raw/parsed outputs, provider response/error
    surfaces, plugin/context bodies, retrieval event bodies, and meta-prompt
    evidence still needed configurable retention modes at the time this item
    was completed.
  - Verification: focused config and loop tests cover accepted/rejected modes,
    hash-only/off persisted history behavior, secret suppression, and manifest
    retention-policy emission.

- [x] Add configurable LLM-feedback output retention to paper evidence.
  - Paper evidence: feedback records can echo private context and
    provider-generated analysis, so paper artifacts need an explicit
    persistence policy for raw feedback responses and parsed feedback text.
  - Status: `feedback_retention_mode` now supports `full`, `redacted`,
    `hash_only`, and `off`; paper-facing docs and manifests distinguish this
    implemented feedback surface from remaining provider/plugin/context/
    retrieval/meta-prompt retention work.
  - Remaining paper gap: provider response/error surfaces beyond feedback
    records, plugin/context bodies, retrieval event bodies, meta-prompt
    evidence, and replay retention still needed configurable retention modes at
    the time this item was completed.
  - Verification: focused config, feedback, and loop tests cover accepted/
    rejected modes, redacted default behavior, hash-only/off persisted history
    behavior, secret suppression, and manifest retention-policy emission.

- [x] Add configurable provider error retention to paper evidence.
  - Paper evidence: failed provider/backend calls can include private task
    context, SDK diagnostics, endpoint hints, or provider-generated text in
    exception messages, so paper artifacts need a configurable persistence
    policy for durable call-ledger error text.
  - Status: `provider_error_retention_mode` now supports `full`, `redacted`,
    `hash_only`, and `off`; failed LLM call records retain `error` text
    according to that mode, attach `error_retention` metadata, and expose the
    provider-error surface under manifest `policies.prompt_data_retention`.
  - Remaining paper gap: provider success-response payloads, plugin/context
    bodies, retrieval event bodies, meta-prompt evidence, and replay retention
    still needed configurable retention modes at the time this item was
    completed.
  - Verification: focused config and ensemble tests cover accepted/rejected
    modes, builder wiring, redacted default behavior, hash-only/off persisted
    call behavior, secret suppression, and ledger replay compatibility.

- [x] Add configurable provider success-output retention to paper evidence.
  - Paper evidence: successful LLM outputs can contain generated code,
    private context echoes, or provider-generated analysis, so paper-facing
    call ledgers need an explicit retention policy for success-output text.
  - Status: `provider_response_retention_mode` now supports `full`,
    `redacted`, `hash_only`, and `off`; successful LLM call records retain
    `output` text according to that mode, attach `output_retention` metadata,
    and expose the successful-output surface under manifest
    `policies.prompt_data_retention`.
  - Remaining paper gap: plugin/context bodies, retrieval event bodies,
    meta-prompt evidence, and replay retention still needed configurable
    retention modes at the time this item was completed.
  - Verification: focused config, ensemble, and manifest tests cover
    accepted/rejected modes, builder wiring, default hash-only behavior,
    full/redacted persisted call behavior, secret suppression, off mode, and
    ledger replay validation.

- [x] Add configurable plugin context retention to paper evidence.
  - Paper evidence: plugin context can carry paper-inspired guidance, retrieved
    snippets, or private task details into mutation prompts, so paper-facing
    candidate history needs an explicit retention policy for persisted
    plugin-context text.
  - Status: `plugin_context_retention_mode` now supports `full`, `redacted`,
    `hash_only`, and `off`; candidate plugin-context records retain `context`
    text according to that mode, attach `context_retention` metadata, and
    expose the plugin-context surface under manifest
    `policies.prompt_data_retention`.
  - Remaining paper gap: explicit context bodies, retrieval event bodies,
    meta-prompt evidence, and replay retention still need configurable
    retention modes.
  - Verification: focused config, loop, and manifest tests cover
    accepted/rejected modes, default redacted behavior, hash-only/off persisted
    context behavior, secret suppression, and manifest policy emission.

- [x] Add pip configuration evidence to environment provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.6 and 4.
  - Status: runtime environment provenance now records bounded/redacted
    `pip_config` evidence from `python -m pip config list`, including retained
    line hashes, a raw stdout hash, timeout/error diagnostics, and
    secret/control-character sanitization.
  - Remaining paper gap: full private package-source interpretation, complete
    install options, accelerator budget/accounting metadata, non-project build
    provenance, and live provider service/API-version evidence remain open.
  - Verification: focused provenance tests cover normal, bounded, redacted, and
    failed pip-config capture.

- [x] Expose archive cursor restore through run entrypoints.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: direct `evolve()` calls can now pass
    `runtime_archive_state_snapshot`, and CLI runs can load the compact
    `runtime.history.archive_state` snapshot from a prior manifest with
    `--restore-archive-cursor-from-manifest`. The restored state continues the
    island assignment cursor and archive/migration/metric-sampling counters
    during new run initialization.
  - Remaining paper gap: full archive snapshots, MAP-Elites cell/elite
    restoration, descriptor-normalization state, migration replay, and
    controller resume remain open.
  - Verification: focused loop/CLI tests cover restored cursor assignment and
    manifest/argument propagation.

- [x] Surface role-specific LLM accounting in runtime manifests.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3, 2.4, and 4.
  - Status: runtime manifests now include `runtime.llm_accounting`, a compact
    audit summary derived from validated ensemble role accounting. It records
    per-role counters, aggregate totals, provider-attempt/token/failure
    summaries when available, and active logical-call/retry/fallback, timeout,
    prompt, and output caps.
  - Remaining paper gap: role-specific retry budgets, token/cost/time coupling,
    equal-budget benchmark reporting, and resumable retry consumption remain
    open before the system matches AlphaEvolve-grade budgeted search.
  - Verification: focused loop tests cover completed runtime accounting
    snapshots and seed-only no-LLM manifests.

- [x] Record safe provider status codes for failed LLM calls.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3 and 2.6.
  - Status: failed LLM call telemetry now retains safe integer HTTP-style
    provider status codes when SDK exceptions expose them, and durable ledger
    replay validates the field.
  - Remaining paper gap: status codes are audit evidence only; provider
    penalties, role-specific quarantine, cost accounting, and budget-stop
    policy remain open.
  - Verification: focused ensemble tests cover status-code capture, success
    nullability, invalid replay rows, and non-status failures.

- [x] Aggregate provider-failure categories by LLM role.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3 and 2.6.
  - Status: scheduler snapshots and durable LLM-call replay now expose
    provider-response, timeout, rate-limit, transport, provider-server,
    provider-client, and unknown failure counts by call role.
  - Remaining paper gap: the counts are audit evidence only. AlphaEvolve-grade
    runtime behavior still needs role-specific quarantine, penalties,
    budget-stop policy, and resumed failure-policy state.
  - Verification: focused ensemble tests cover category-to-counter mapping and
    retry/fallback aggregation.

- [x] Persist role-level LLM scheduler accounting summaries.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3 and 2.6.
  - Status: final scheduler snapshots and durable LLM-call replay now expose
    role-level counts for successes, failures, reward-accounted calls,
    telemetry-only calls, ensemble retry/fallback attempts, and
    adapter-internal provider attempts, plus provider-reported token totals
    and provider-failure category counts.
  - Remaining paper gap: AlphaEvolve-grade scheduling still needs configurable
    per-role reward policy, quotas, provider-cost accounting, token-budget stop
    policy, and resumed scheduler state rather than audit-only summaries.
  - Verification: focused ensemble tests cover role summaries in live state,
    restored-state validation, retry/fallback counters, and ledger replay.

- [x] Add provider request-timeout configuration for built-in LLM clients.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Status: implemented as partial budget alignment. Built-in OpenAI,
    Anthropic, and Ollama backend specs accept positive `timeout_sec`, and the
    bundled adapters forward it to provider client construction.
  - Remaining paper gap: timeout/cancellation is not yet tied to hard provider
    cancellation, role-specific artifacts, or distinct timeout stop reasons.
  - Verification: focused config/backend/ensemble tests cover invalid timeout
    rejection, custom-spec rejection, direct client-constructor forwarding, and
    `build_llm()` forwarding.

- [x] Make program metadata and evaluation values Unicode format-control safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Status: `Program` metadata and evaluation string values now reject Unicode
    `Cf` format controls while preserving ordinary Unicode and multiline
    prompt/diff text; metadata/evaluation keys were already display-safe.
  - Remaining paper gap: any newly identified durable provenance labels or
    free-form provenance text still need an explicit reject/escape/hash policy.
  - Verification: focused program tests cover ordinary Unicode metadata,
    multiline values, metadata-value U+202E rejection, and evaluation-value
    zero-width joiner rejection.

- [x] Narrow hidden-file seed policy TODO after skipped-entry provenance landed.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Status: `_load_initial_workspaces()` now records skipped hidden/cache seed
    paths under `problem.seed_skipped`, skips top-level hidden/cache seed
    entries before loading, and documents the current secret-safe default in
    README seed-workspace semantics.
  - Remaining paper gap: seed-workspace hidden/cache include/exclude policy is
    still not configurable, so intentional dotfile retention is not a
    first-class setup option.
  - Verification: focused loader and loop tests cover hidden/cache seed skips,
    no-seed diagnostics for fully skipped roots, and manifest provenance for
    skipped entries.

- [x] Stop non-mutation LLM calls from counting as mutation scheduler pulls.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3 and 2.6.
  - Status: implemented as a partial scheduler-alignment step. Mutation calls
    remain reward-accounted, while critique, feedback, and meta-prompt calls
    are persisted as telemetry-only records that do not change mutation backend
    counts or rewards.
  - Verification: focused ensemble tests cover unchanged scheduler counts,
    role-preserving retries/fallbacks, non-rewardable auxiliary calls, and
    replay rejection for telemetry-only reward rows. The remaining paper-level
    gap is configurable role-specific accounting, resumable scheduler state,
    and role-specific retry/fallback/budget policy.

- [x] Capture provider response metadata for LLM call provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.3, and 2.6.
  - Status: implemented as a partial paper-alignment step. Built-in provider
    adapters now preserve safe usage counts, finish reasons, request ids, and
    response ids when SDK responses expose them, and run-level LLM call logs
    validate those fields on replay.
  - Verification: focused LLM backend and ensemble tests cover OpenAI,
    Anthropic, and Ollama extraction plus unsafe telemetry sanitization,
    including Unicode format-control rejection for provider label fields. The
    paper-level budget gap remains open for provider token/cost accounting,
    adapter-internal retries, raw provider diagnostics, and role-specific
    scheduling.

- [x] LLM provider endpoint and client-context provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.3, and 2.6.
  - Status: implemented and documented for built-in backends. LibreEvolve now
    has explicit safe client-context fields for OpenAI `base_url`,
    `organization`, and `project`, Anthropic `base_url`, and Ollama `host`.
    Accepted values are recorded in manifests via `config.backends` and in LLM
    call telemetry via `client_context`; omitted fields still inherit
    SDK/environment defaults.
  - Verification: focused config/backend/ensemble tests cover config and direct
    constructor validation, SDK/client forwarding, call telemetry,
    sanitization, and replay validation. The paper index now scopes remaining
    unconfigured SDK/environment defaults as omitted-field behavior rather than
    a missing explicit configuration surface.

- [x] Distinguish configured prompt-seed freedom from AlphaEvolve prompt
  fidelity.
  - Status: documented. The paper index now includes an AlphaEvolve
    prompt-fidelity note stating that configured prompt seed variants are
    checked for renderability and `{task}` support but may intentionally omit
    parent code/workspace, context, feedback, proposal metadata, and
    mutation-format instructions. It also states that evolved prompt children
    preserve only the placeholders present in their parent template.

- [x] Keep non-archive `show` output scoped until remaining unselected source
  fields are validated or summarized.
  - Status: documented. The paper index now includes an AlphaEvolve
    run-inspection note stating that `libreevolve show` validates streamed ids,
    metrics, evaluation shape, and archive diagnostics, including malformed
    unselected retained rows, while non-archive source/workspace display was
    limited to the chosen best row and was not whole-run source integrity
    evidence.
  - Superseded by implementation: `libreevolve show` now validates generation,
    legacy source, workspace files, and primary-file payloads for every
    streamed history row, and current docs no longer carry the selected-row
    caveat.

- [x] Add manifest-bound MAP-Elites coordinate range validation before treating
  cells as full paper-alignment evidence.
  - Status: implemented and documented. `libreevolve show` now validates
    current-history cell coordinates against
    `manifest.json.config.map_elites_bins` when present, while histories
    without manifest/bin metadata remain legacy-limited to
    arity/type/non-negative validation. The paper index includes this
    MAP-Elites cell-inspection note.
  - Verification: CLI tests cover in-range legacy behavior, out-of-range
    manifest-bound rejection, and malformed manifest bin metadata.

- [x] Tighten or remove GigaEvo-derived implementation claims.
  - Paper evidence: `2511.17592__GigaEvo.pdf` describes Redis-backed
    evolutionary units with lifecycle state, optimistic concurrency, an
    asyncio DAG execution engine, configurable stages, insights, bidirectional
    lineage, and rewrite/diff mutation modes.
  - Status: tightened. `papers/README.md` already says LibreEvolve is not
    GigaEvo as described and lacks the Redis lifecycle database, asyncio DAG
    engine, insight stage, and concurrent units; the README source table now
    also labels GigaEvo as inspiration only.
  - Verification: paper-manifest validation and full non-integration tests
    passed after the documentation update.

- [x] Tighten or remove CodeEvolve-derived implementation claims.
  - Paper evidence: `2510.14150__CodeEvolve.pdf` combines islands-based
    genetic search with modular LLM orchestration, execution feedback,
    context-aware recombination, adaptive meta-prompting, and targeted
    refinement.
  - Status: tightened. `papers/README.md` distinguishes LibreEvolve's generic
    prompt-program/template-mutation boundary from missing CodeEvolve-specific
    mechanisms, and the README source table now labels CodeEvolve as
    inspiration only with missing crossover, targeted refinement, modular
    orchestration, and context-aware recombination.
  - Verification: paper-manifest validation and full non-integration tests
    passed after the documentation update.

- [x] Keep ThetaEvolve-inspired training examples schema-stable.
  - Paper evidence: ThetaEvolve-style test-time training depends on replayable
    prompt/response/reward examples that can be fed back into training code.
  - Status: implemented. The exporter now queues only non-empty string
    prompt/response values from prompt and diff metadata, skips malformed text
    fields with diagnostic counters, and documents the stable row schema.
  - Verification: plugin tests cover non-string, empty, whitespace, and valid
    text examples.

- [x] Treat untyped ThetaEvolve score/reward export as a paper-fidelity gap.
  - Paper evidence: ThetaEvolve-style GRPO/test-time learning depends on
    numeric reward signals, with penalties and reward shaping defined as part
    of the training environment.
  - Status: implemented. Scores must be finite non-boolean numbers before
    training rows are queued, accepted raw/reward values are floats, and
    invalid score values are counted as `invalid_score` before raising.
  - Verification: plugin tests cover boolean, nonnumeric, non-finite,
    negative, zero, and positive score cases.

- [x] Make ThetaEvolve-inspired export finalization replayable.
  - Paper evidence: test-time training and reward shaping depend on durable
    datasets/checkpoints. Queued examples that are neither exported nor
    snapshotted cannot be replayed, audited, or used for later training.
  - Status: implemented. TTTRL artifact metadata collection flushes pending
    examples before returning manifest metadata, making short completed runs
    replayable even when the final generation does not meet `train_every`.
  - Verification: plugin and loop tests cover final flush policy and manifest
    metadata.

- [x] Make ThetaEvolve-inspired export robust to invalid examples.
  - Paper evidence: a training-data loop should retain valid examples and make
    rejected examples auditable; one malformed reward should not silently block
    all later data.
  - Status: implemented by queue validation. Malformed prompt/response fields
    are skipped, malformed scores raise with diagnostics before queueing, and
    later valid rows remain exportable because invalid examples do not enter
    the cursor.
  - Verification: plugin tests cover invalid-score then valid-export behavior
    and malformed-example counters.

- [x] Keep ThetaEvolve-inspired export artifacts run-scoped or explicitly
  external.
  - Paper evidence: test-time training datasets/checkpoints should be
    attributable to the experiment that produced them.
  - Status: documented. CLI-loaded TTTRL exports are run-scoped, while direct
    `TTTRLPlugin(log_dir=...)` exports are deliberate user-managed external
    artifacts whose manifest `log_dir`, path, count, hash, and byte metadata
    should be inspected for provenance.
  - Verification: README, plugin docs, run-artifact docs, and paper index
    wording describe the external-artifact policy.

- [x] Treat raw ThetaEvolve export payloads as a paper-fidelity gap.
  - Paper evidence: a training-data path should produce reusable examples with
    explicit retention and sanitization semantics; raw prompt-bearing artifacts
    can leak provider keys, private task context, or candidate code into future
    training corpora.
  - Status: implemented. The current exporter redacts common secret patterns
    and enforces per-field plus combined prompt/response character budgets
    before queueing examples, with artifact metadata counters for redaction and
    truncation.
  - Verification: plugin tests cover prompt and response secrets, oversized
    field payloads, aggregate truncation, clean payload counters, and export
    rows; README, plugin docs, run-artifact docs, and the paper index describe
    the sanitized bounded export boundary.

- [x] Keep ThetaEvolve-inspired behavior explicitly paper-limited.
  - Paper evidence: `2511.23473__ThetaEvolve.pdf` describes a single-LLM
    framework with a large program database, batch sampling, lazy penalties,
    optional reward shaping, and reinforcement learning at test time.
  - Status: README, plugin docs, architecture docs, completed roadmap items,
    and the paper index now scope `ttt_rl` as a clipped-reward JSONL exporter,
    not an online GRPO/RL trainer or optimizer-checkpoint system.
  - Remaining implementation gap: batch prompt sampling, lazy/stagnation
    penalties, online GRPO/RL training, dynamic environment integration,
    resume semantics, and training checkpoint management are not implemented.
    Those stay outside current claims unless the plugin is promoted beyond
    export-only behavior.
  - Verification: repository-wide search shows ThetaEvolve references are
    scoped to export/training-boundary wording, and TTT/RL plugin tests cover
    the implemented export schema, reward clipping, retention, restore counts,
    and finalization behavior.

- [x] Treat mutable plugin snapshot aliases as a paper-level provenance gap.
  - Requirement: paper-inspired retrieval and training-data components should
    produce durable, replayable evidence records, not live Python objects that
    external callers can mutate after observation.
  - Status: implemented. DeepResearch and TTTRL public snapshot APIs now return
    defensive deep copies for nested retrieval events and queued training rows.
  - Verification: plugin tests prove post-read caller mutations cannot alter
    retrieval source metadata or queued TTTRL examples; plugin docs state the
    defensive snapshot contract.

- [x] Define paper-inspired plugin score effects in archive policy.
  - Requirement: paper-inspired plugin scoring signals need a clear
    relationship to archive/search policy before being treated as search-quality
    evidence.
  - Status: documented. Plugin-adjusted top-level fitness is excluded from
    MAP-Elites ranking under the current policy; declared evaluator-metric
    `selection_score` remains the archive-selection signal.
  - Verification: loop tests assert plugin score composition changes final
    fitness without changing archive selection score.

- [x] Make context-selection accounting unambiguous for included versus
  excluded sources.
  - Requirement: prompt-context provenance should identify which declared
    sources shaped prompts and which were filtered out.
  - Status: fixed. Context include-pattern provenance now records pre-filter
    `matches` and post-filter `selected_matches`, and paper-facing docs define
    the selected-source boundary.
  - Verification: loader tests cover excluded, hidden, unmatched, nested, and
    selected include-pattern counts.

- [x] Harden circle-packing output-shape validation before treating it as
  paper evidence.
  - Requirement: fixed-`n` circle-packing evidence must prove exactly the
    advertised number of circles.
  - Status: fixed for the current smoke fixture. The validator now rejects
    subclass/protocol tricks and scores only a materialized plain list of 26
    plain circle triples.
  - Verification: example tests reject a spoofed list with length 26 that
    yields 100 circles.

- [x] Calibrate benchmark metric bounds before using fixtures as paper evidence.
  - Requirement: paper-facing benchmark metrics should not collapse distinct
    intended improvements before archive selection or reporting.
  - Status: fixed for the current matrix smoke fixture and documented in the
    paper index. Its primary inverse-count metric now uses `[0.0, 1.0]`, and
    `papers/README.md` states that it remains a 2x2 smoke fixture, not a
    tensor-rank decomposition benchmark.
  - Verification: example tests confirm seed and 7-multiplication Strassen
    candidates are ordered by normalized fitness without metric-bound
    diagnostics.

- [x] Treat direct evaluator default-path escapes as a paper-level evaluator
  isolation gap.
  - Requirement: direct library evaluation should not silently execute
    validators outside the problem boundary when the system claims
    problem-local evaluator provenance.
  - Status: implemented. Direct evaluator use now preflights default validator
    paths with the same problem-local containment and Python-file policy as
    startup/runtime evaluator provenance.
  - Verification: evaluator tests cover direct outside, missing, directory,
    non-Python, and symlink-to-outside default validator paths.

- [x] Treat evaluator artifact-option validation as part of the evaluator
  evidence contract.
  - Requirement: evaluation artifacts and their limits are part of the
    reproducible evidence trail for candidate assessment, so invalid artifact
    options should fail before evaluation.
  - Status: implemented. Direct evaluator construction validates artifact
    selectors, max-file/max-byte limits, and redaction flags before subprocess
    execution or artifact metadata writes.
  - Verification: evaluator tests cover invalid direct artifact options,
    normal copy-out, and configured-stage artifact overrides.

- [x] Define deterministic evaluator artifact glob semantics.
  - Requirement: evaluator-generated artifacts are experiment evidence, so
    artifact selectors need deterministic, documented root/nested/recursive
    matching semantics.
  - Status: implemented. Artifact glob matching is path-segment-aware with
    explicit `**` recursion, shared by include and exclude selectors and
    documented in README, configuration, and run-artifact docs.
  - Verification: focused evaluator tests cover root-only, one-level,
    recursive, include/exclude, and staged/direct selector behavior.

- [x] Treat unvalidated direct evaluator timeout controls as a paper-level
  budget fidelity gap.
  - Requirement: AlphaEvolve-style evaluation uses explicit compute budgets and
    timeout controls; direct evaluator paths should not silently reinterpret
    invalid budget values.
  - Status: implemented. Direct evaluator timeout controls now reject zero,
    negative, boolean, nonnumeric, NaN, and infinite values before evaluator
    execution, matching the config/stage policy.
  - Verification: evaluator tests cover invalid direct timeout values and valid
    positive int/float inputs.

- [x] Add required problem-file link tests before treating task provenance as
  hardened.
  - Requirement: the task description and metric schema define the optimization
    problem and should be reproducible from run manifests and problem
    provenance.
  - Status: implemented. The loader rejects linked problem roots before
    resolving them and rejects symlinked or junction-backed required setup-file
    paths before content reads.
  - Verification: platform-aware loader tests cover symlink/junction roots and
    linked required files; the CLI test proves linked roots stop before runtime
    evolution or artifact creation.

- [x] Treat raw synthetic diff-error reasons as evaluator-feedback fidelity
  gaps.
  - Requirement: failed mutation feedback resurfaced to the evolutionary
    database and future prompts should be structured, bounded, and safe enough
    to guide later samples.
  - Status: implemented. Synthetic diff failures now expose paper-visible
    canonical reason codes through `diff_error_v1`; unknown strings are
    redacted/bounded as `unknown_diff_error`, and non-string direct evaluator
    values are represented as `malformed_diff_error`.
  - Verification: evaluator tests cover known errors, unknown secret-like
    payloads, non-string values, and escaped/truncated control-string detail.

- [x] Treat unreadable existing run directories as a paper-level manifest
  robustness gap.
  - Requirement: AlphaEvolve-style experiment artifacts need reproducible setup
    provenance and clear run-directory lifecycle state before a run is treated
    as auditable evidence.
  - Status: implemented. Unreadable existing run directories are represented in
    manifest `run_directory.foreign_entries` as redacted unreadable-listing
    diagnostics with explicit unknown-entry semantics.
  - Verification: database tests cover unreadable listing diagnostics, redacted
    secret-like exception text, and overwrite cleanup with preserved diagnostics.

- [x] Treat untyped CausalPlugin mutation evidence as a paper-level guidance
  fidelity gap.
  - Requirement: CausalEvolve-inspired guidance should not crash on malformed
    local mutation metadata before paper comparisons treat it as robust factor
    evidence.
  - Status: implemented. Non-text mutation evidence is counted and treated as
    unsupported evidence with deterministic fallback rather than passed to the
    SEARCH/REPLACE parser. The paper status row still scopes the plugin as
    fixed token-pattern guidance, not an LLM causal scratchpad.
  - Verification: causal tests cover missing, text, and malformed non-text
    evidence plus artifact metadata counters.

- [x] Treat unsafe lower-level archive ids as an experiment-database fidelity
  gap.
  - Requirement: Lower-level archive APIs should not retain unsafe candidate
    ids, parent ids, or lineage entries before paper comparisons treat archive
    state as stable experiment-database evidence.
  - Status: implemented. `MAPElites.add()` and `IslandModel.add()` reject
    post-construction-mutated unsafe identities before live archive mutation.
  - Verification: MAP-Elites and island tests prove unsafe ids, parent ids, and
    lineage are rejected without retaining best/cell/elite state or advancing
    island sequence/current state.

- [x] Treat non-durable prompt-program add failures as a meta-prompt evolution
  provenance gap.
  - Requirement: Prompt-program archives should retain rejected direct add
    evidence for duplicate ids and unknown parents before paper comparisons
    claim faithful prompt-program provenance.
  - Status: implemented. Direct prompt add identity/reference failures now
    write durable `prompt_reference_error` rows to
    `prompt_history_invalid.jsonl` before raising.
  - Verification: meta-prompt tests prove duplicate and unknown-parent direct
    add failures are quarantined while accepted prompt history and prompt DB
    state remain unchanged.

- [x] Treat duplicate accepted-history id rejection without quarantine as an
  experiment-database provenance gap.
  - Requirement: Duplicate accepted-history ids should leave durable rejected
    record evidence before paper comparisons claim stronger experiment-database
    provenance.
  - Status: implemented. Duplicate accepted program ids are quarantined to
    `history_invalid.jsonl` before raising, and accepted history/index state is
    preserved.
  - Verification: database tests prove the rejected duplicate row is retained
    diagnostically while `history.jsonl`, `_ids`, and accepted program snapshots
    remain unchanged.

- [x] Treat unbounded plugin state retention as a paper-level runtime gap.
  - Requirement: Paper-inspired guidance and training-data plugins should have
    bounded, inspectable auxiliary state under long-running search budgets.
  - Status: implemented. Causal outcome history is capped and reported, while
    TTT retained examples are capped, overflow-exported, pruned after export,
    and reported through plugin artifact metadata. Full resumable RL
    checkpointing remains explicitly out of scope.
  - Verification: focused plugin tests cover bounded retention, overflow
    export, retained/dropped/pending/exported counters, and constructor
    validation.

- [x] Treat local PDF stat/read failures as paper-index validation gaps.
  - Requirement: Paper-aligned local cache validation should return bounded,
    redacted, row-attributed issues when ignored PDF cache files cannot be
    inspected or read.
  - Status: implemented. Local PDF `stat()` and `read_bytes()` `OSError`s are
    caught and surfaced as structured paper-manifest issues with relative file
    labels, and directory-shaped `.pdf` paths are reported before hashing.
  - Verification: paper-manifest tests cover stat errors, read errors, matching
    PDFs, missing PDFs, byte-count mismatches, directory-shaped PDFs, CLI text
    output, CLI JSON output, and secret-like error redaction.

- [x] Treat required problem-file read/stat failures as a paper-level setup
  robustness gap.
  - Requirement: Paper-aligned task setup should expose deterministic,
    redacted diagnostics for required problem files before experiments are
    treated as reproducible task packages.
  - Status: implemented. Required problem-file read/stat `OSError`s are caught
    and surfaced as path-aware redacted setup diagnostics.
  - Verification: focused loader tests cover `task_description.txt`,
    `metrics.yaml`, `validate.py`, secret-like error text, invalid encoding,
    malformed YAML, missing files, and directory-shaped files.

- [x] Treat seed-file read failures as a paper-level candidate setup
  robustness gap.
  - Requirement: Paper-aligned seed ingestion should provide path-aware,
    redacted setup diagnostics for unreadable single-file and workspace seeds.
  - Status: implemented. Seed text read `OSError`s are caught and reported as
    redacted file-scoped setup diagnostics instead of raw host exceptions.
  - Verification: focused loader tests cover top-level seed reads, workspace
    seed reads, secret-like diagnostics, invalid UTF-8 seeds, malformed seed
    markers, and successful workspace seed loading.

- [x] Treat seed-root enumeration failures as a paper-level candidate setup
  robustness gap.
  - Requirement: Paper-aligned seed/codebase ingestion should expose bounded,
    redacted diagnostics when the starting-population directory cannot be
    listed.
  - Status: implemented. `initial_programs/` listing failures are caught and
    reported as path-aware redacted setup diagnostics, preserving missing-root
    and linked-root behavior.
  - Verification: focused loader tests cover unreadable, missing, linked, and
    normal seed roots.

- [x] Treat context source stat failures as a paper-level ingestion robustness
  gap.
  - Requirement: Paper-aligned context selection should have bounded,
    inspectable behavior when source size metadata cannot be read for byte
    budget checks.
  - Status: implemented. Source stat failures are represented as skipped
    `stat_error` diagnostics with null hash/byte fields, error type, and
    redacted error text instead of raw setup exceptions.
  - Verification: focused loader tests cover selected and preclassification
    source stat failures with secret-like error text and sibling preservation.

- [x] Treat context directory-enumeration failures as a paper-level ingestion
  robustness gap.
  - Requirement: Paper-aligned local context ingestion should preserve
    deterministic evidence for the readable context subtree even when a nested
    directory cannot be listed.
  - Status: implemented. Root and nested `context/` directory listing failures
    become skipped `directory_listing_error` diagnostics with redacted error
    text, and readable sibling context remains selected.
  - Verification: focused loader tests cover root and nested directory
    enumeration failures with secret-like error text.

- [x] Treat unreadable selected context sources as a paper-level ingestion
  robustness gap.
  - Requirement: Paper-aligned literature/context ingestion should degrade
    deterministically when individual selected local sources are unreadable,
    preserving the rest of the context set and redacted provenance.
  - Status: implemented. Selected context source read failures are recorded as
    skipped `read_error` diagnostics with null hash/byte fields and redacted
    error text, while readable selected siblings remain available to prompts.
  - Verification: focused loader tests cover unreadable `.txt`, `.md`, `.py`,
    and `.pdf` selected sources.

- [x] Treat unreadable skipped context sources as a paper-level ingestion
  robustness gap.
  - Requirement: Paper-aligned context selection should preserve deterministic
    provenance for skipped sources without requiring every skipped file to be
    readable for hashing.
  - Status: implemented. Unsupported, excluded, hidden, and not-included source
    diagnostics preserve their original skip reason and add
    `read_status: read_error`, null hash/byte fields, error type, and redacted
    error text when bytes cannot be read.
  - Verification: focused loader tests cover unreadable unsupported, excluded,
    hidden-not-included, and not-included skipped sources.

- [x] Treat unreadable context manifests as a paper-level ingestion robustness
  gap.
  - Requirement: Paper-aligned literature/context ingestion should have a
    deterministic, inspectable failure mode when the problem-local manifest is
    unreadable.
  - Status: implemented for manifest setup. `context.yaml` / `context.yml`
    read failures now produce path-aware redacted setup diagnostics instead of
    raw host exceptions.
  - Verification: focused loader tests cover unreadable manifests, invalid
    UTF-8, malformed YAML, duplicate keys, and directory-shaped manifests.

- [x] Treat directory-listing provenance failures as a paper-level manifest
  robustness gap.
  - Requirement: Paper-aligned evolutionary runs should be reproducible from
    manifests even when some local input paths are unreadable, with redacted
    diagnostics rather than raw startup crashes.
  - Status: implemented for source/problem tree provenance. Directory
    enumeration failures become skipped `directory_listing_error` records with
    redacted error text, and readable sibling subtrees remain included in the
    tree hash.
  - Verification: focused provenance tests cover root and nested listing
    failures, skipped diagnostic hashes, secret redaction, and readable-subtree
    preservation.

- [x] Treat truncated failure repetition keys as a paper-level search-memory
  gap.
  - Requirement: Paper-aligned failure memory and novelty resurfacing should
    distinguish distinct failed mutations with stable fingerprints, especially
    for long multi-file/codebase edits.
  - Status: implemented for failure-history grouping. Generated and seed
    failure records include a persisted `failure_fingerprint`; repetition
    counters use the fingerprint SHA-256 and no longer collapse distinct long
    mutations through `_truncate_text(mutation_text, 500)`.
  - Verification: focused database tests cover long-mutation collision
    resistance, parent/error/changed-file separation, failed append behavior,
    redaction, and seed-failure fingerprints.

- [x] Treat unbounded context-entry counts as a paper-level ingestion gap.
  - Requirement: Paper-aligned problem-local context and literature ingestion
    should be bounded across traversal, provenance, and prompt rendering. Byte
    limits alone do not bound manifest size or startup work for large context
    trees.
  - Status: fixed for deterministic local context traversal/provenance.
    `context.yaml` can cap entries, relative path depth, retained skipped
    diagnostics, and serialized context-policy provenance. Loader diagnostics
    distinguish total skipped count from retained skipped records and record
    deterministic omission metadata.
  - Verification: focused loader tests cover count limits, depth limits,
    skipped-record retention caps, provenance-size trimming, and invalid
    context limit values.

- [x] Treat unbounded LLM call-history retention as a paper-level runtime
  accounting gap.
  - Requirement: paper-aligned long-running model ensembles need durable,
    queryable LLM-call provenance without relying on an unbounded in-memory
    list that grows with every provider attempt.
  - Status: the unbounded in-memory list gap is fixed. `LLMEnsemble` now
    retains a bounded call-history window controlled by `llm_call_history_max`
    and exposes `call_history_retention` with retained, total, and dropped
    counts. Tests cover eviction metadata, `last_call`, reward claiming for
    evicted successful calls, and loop metadata spans after eviction.
  - Remaining gap: a complete durable append-only LLM call-artifact remains a
    paper-level runtime accounting gap in `docs/todo/papers.md`.

- [x] Persist objective-schema provenance for AlphaEvolve-style reproducibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: task metrics, primary objective choice, and metric bounds are
    part of the optimization problem and must be recoverable for faithful
    analysis, archive normalization, and future resumed workers.
  - Status: implemented for startup manifests. LibreEvolve now records the
    effective objective schema under `manifest.problem.objective_schema`,
    including normalized metrics, directions, bounds, effective primary flags,
    `primary_metric`, `primary_bounds`, and `metric_count`; resume checkpoint
    restoration remains part of the broader resumability backlog.

- [x] Task specification API with evolve-block markers.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: users mark code blocks to evolve inside a larger skeleton.
  - Status: implemented for Python single-file and local workspace candidates
    in `libreevolve/core/candidate.py`; malformed marker structures are
    rejected during mutation application with explicit diagnostics.
  - Remaining divergence: arbitrary-language runners remain open; evolve
    blocks are still a text-file convention rather than a generalized
    problem-defined candidate API.

- [x] Prevalidate malformed evolve-block seeds before evaluation.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: task specifications define the valid evolvable regions before
    the evolutionary loop starts.
  - Current gap: malformed marker structures are rejected during mutation, but
    not during problem loading. A local proof with `initial_programs/seed.py`
    containing `# EVOLVE-BLOCK-START core` and no matching end marker loaded
    successfully as one initial workspace.
  - Required result: reject malformed seed evolve-block layouts at load time
    for single-file and workspace seeds, or mark delayed mutation-time
    validation as a deliberate divergence in the AlphaEvolve paper row.
  - Status: implemented. `load_problem()` rejects malformed top-level seed
    files and workspace seed files with file-scoped diagnostics before
    evaluation starts; loader tests cover both boundaries.

- [x] Reject marker-prefix typos in evolve-block task specifications.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: evolve-block markers define the exact boundary between
    skeleton code and code that AlphaEvolve may change.
  - Current gap: start-marker parsing is prefix-based. A local proof with
    `# EVOLVE-BLOCK-STARTED`, `x = 1`, and `# EVOLVE-BLOCK-END` returned no
    marker error and extracted a valid block named `ED`, so a typo or
    marker-like comment can silently change the task specification.
  - Required result: make marker parsing exact, or explicitly document this as
    a divergence from exact task-specification markers before claiming
    AlphaEvolve-style evolve-block fidelity.
  - Status: implemented for mutation validation and documented. Start markers
    must be exact with an optional whitespace-separated name, and prefix typos
    are rejected with focused candidate coverage. Seed load-time marker
    prevalidation is implemented separately above for top-level seed files and
    seed workspace files.

- [x] Make evolve-block markers robust to marker-like code literals.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: the initial program marks components to evolve while the rest
    of the source remains skeleton code; marker declarations should be
    distinguishable from ordinary program text.
  - Current gap: LibreEvolve's marker parser is line-text based rather than
    source-aware. A local proof placed `# EVOLVE-BLOCK-START literal` and
    `# EVOLVE-BLOCK-END` inside a Python triple-quoted string. The parser
    accepted those lines as a real block, protected code outside the string,
    and allowed mutation of the string body as the evolvable region.
  - Required result: make evolve-block parsing comment/source-aware for Python
    candidates, introduce an escaped marker representation, or document
    marker-like literals/docstrings as a deliberate unsupported edge case
    before claiming robust AlphaEvolve-style task-boundary fidelity.
  - Status: implemented and tested. Marker parsing now uses Python tokenizer
    comment tokens and ignores marker-like lines inside strings and docstrings,
    so literal text no longer creates protected skeleton code or a mutable block
    body. Candidate and loader tests cover the string/docstring and workspace
    seed cases.

- [x] Make initial codebase seed ingestion boundary-faithful.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: AlphaEvolve task specifications define the evolvable code and
    problem inputs. Seed codebases should be reproducible declared inputs, not
    implicit references to host-local files outside the problem package.
  - Status: implemented for the current text-file-set candidate model.
    `_load_initial_workspaces()` rejects symlinks and Windows junctions at
    top-level seed entries and inside seed workspace directories before reading
    candidate text, so initial codebase seeds cannot silently depend on
    host-local linked targets. Tests cover file-symlink rejection where
    supported and Windows junction rejection.
  - Remaining divergence: binary/static seed assets are still not first-class
    candidate files, and full candidate abstraction hooks remain tracked
    separately.

- [x] Make invalid seed-file encoding a path-aware setup failure.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: task setup failures should identify the invalid seed input
    precisely before an experiment starts.
  - Current gap: LibreEvolve's current candidate model is UTF-8 text-only, but
    seed decoding errors are not normalized.
  - Current evidence: a local CLI proof with invalid UTF-8 bytes in
    `initial_programs/seed.py` failed with a raw codec message and no seed path.
    A direct loader proof with invalid UTF-8 in
    `initial_programs/seed_a/helper.py` raised raw `UnicodeDecodeError`.
  - Required result: catch seed decode failures for top-level `.py` seeds and
    nested seed workspaces, report path-aware setup diagnostics, and update
    docs/tests so the paper-index seed-ingestion boundary does not imply robust
    diagnostics for malformed text seeds.
  - Status: implemented for the current UTF-8 text candidate model. Top-level
    and nested workspace seed reads now fail through path-aware problem-load
    diagnostics, with loader and CLI regression coverage.

- [x] Preflight task evaluator contracts before run-artifact mutation.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: task setup includes evaluator code that defines the problem's
    measurable objective. Invalid evaluator contracts should fail as task
    setup errors before an experiment begins or prior run artifacts are
    replaced.
  - Previous gap: LibreEvolve checked only that `validate.py` existed during
    problem loading. It did not preflight importability, callable `evaluate`,
    supported signatures, or configured stage validator contracts before the
    CLI run-directory overwrite path. A local proof with `validate.py` missing
    `evaluate()` and `--overwrite` replaced the old `history.jsonl`, wrote a
    new manifest/history row, logged the seed as `subprocess_error` /
    `returncode_1` with an `AttributeError`, and then failed because no valid
    program was produced.
  - Required result: make evaluator contract validation part of task setup,
    before destructive overwrite cleanup and manifest/history creation; include
    staged validators, import errors, syntax errors, callable/signature checks,
    and artifact-preservation tests.
  - Status: implemented. Evaluator contract preflight now runs before
    destructive run-directory cleanup and covers default/staged validators,
    import failures, syntax errors, missing `evaluate`, signatures that cannot
    bind to the current positional dispatch, and artifact-preservation tests.
    Fixed-shape rejection for variadic, async, generator, and extra-parameter
    validators remains tracked separately.

- [x] Validate task/objective text as part of AlphaEvolve task setup.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.2.
  - Requirement: the system prompt and task setup need an explicit problem
    statement, constraints, and optimization objective; prior solutions and
    evaluator results are conditioned on that task.
  - Current status: LibreEvolve now requires `task_description.txt` to contain
    non-whitespace text. A whitespace-only task file fails problem loading with
    a path-aware diagnostic, and loader tests cover the invalid case.
  - Required result: fail problem loading for empty or whitespace-only task
    descriptions with path-aware diagnostics, add tests for missing/empty/valid
    task files, and keep README/problem-format wording aligned with the
    enforced task contract.
  - Status: implemented for missing and empty/whitespace-only task files and
    documented in README/problem-format docs. CLI problem-load error
    normalization is tracked separately.

- [x] Preserve task/objective text exactly after validation.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.2.
  - Requirement: the task specification and prompt context should reflect the
    user's declared problem constraints and objective without undocumented
    loader rewrites.
  - Current gap: LibreEvolve validates task text as non-empty, but
    `load_problem()` stores `task_description.txt` after `.strip()`. Leading
    indentation, trailing spaces, and final blank lines therefore disappear
    before prompt construction. This is inconsistent with the newer exact
    text/code context preservation policy and is not documented as a deliberate
    divergence.
  - Required result: validate non-empty task text without altering the stored
    prompt input, or explicitly document task-text stripping in the
    AlphaEvolve paper row/problem-format docs.
  - Status: implemented and documented. The loader preserves decoded
    `task_description.txt` text exactly and validates non-empty content without
    replacing the stored prompt input.

- [x] Make invalid task-objective encoding a path-aware setup failure.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: the task objective is a required setup input; invalid encoding
    should identify the broken file before an experiment starts.
  - Current gap: `load_problem()` does not normalize UTF-8 decode failures for
    `task_description.txt`.
  - Current evidence: a local CLI proof with invalid UTF-8 in
    `task_description.txt` failed with a raw codec message and no path. A
    direct loader proof raised raw `UnicodeDecodeError`.
  - Required result: catch task-description decode failures, report a
    path-aware setup diagnostic through loader/CLI paths, and update
    paper/problem-format wording so task setup diagnostics are not overstated.
  - Status: implemented. Invalid UTF-8 in `task_description.txt` now reports
    the offending path through loader and CLI startup diagnostics.

- [x] Normalize task-setup failures at the CLI boundary.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: task definitions, metric schemas, validators, and seeds are
    part of experiment setup; invalid setup should fail before a run starts
    with inspectable diagnostics.
  - Current status: `libreevolve run` now calls `load_problem()` inside its
    startup diagnostics path and converts loader `FileNotFoundError` /
    `ValueError` failures into user-facing `ClickException` messages. CLI tests
    cover malformed metrics, empty tasks, missing validators, no seed programs,
    and invalid context manifests before `evolve()` is called.
  - Required result: report loader failures as structured/user-facing CLI
    setup diagnostics for malformed metrics, empty tasks, missing validators,
    no seeds, and context errors; test that these failures happen before
    artifact cleanup, provider construction, or evolutionary logging.
  - Status: implemented for the named task setup failures, including
    context-specific CLI coverage.

- [x] Make syntactically invalid metric files first-class task setup failures.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: the task specification includes metrics/objectives; invalid
    metric files should fail as setup diagnostics before experiment startup,
    artifact cleanup, or evaluator/LLM work.
  - Current gap: semantic metric-schema failures are normalized through the CLI,
    but YAML parser failures are not. A local temp CLI probe with
    `metrics.yaml` containing `metrics: [` returned exit code `1`, printed no
    user-facing output, and left a raw PyYAML `ParserError` as the exception.
  - Required result: catch syntactically invalid and invalidly encoded
    `metrics.yaml` in the loader, surface path-aware CLI diagnostics, and test
    that these fail before run-artifact mutation or provider/plugin
    construction.
  - Status: implemented. `metrics.yaml` decode/parser failures are normalized
    to path-aware loader diagnostics and pass through CLI startup error
    handling before run setup.

- [x] Reject duplicate YAML mapping keys in AlphaEvolve-style setup files.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.2, 2.4, and 2.6.
  - Requirement: task setup, explicit context, evaluator metrics, and runtime
    configuration should be reproducible inputs to the evolutionary process.
  - Current gap: LibreEvolve parses `metrics.yaml`, `context/context.yaml`, and
    `config.yaml` with PyYAML's default last-key-wins mapping behavior. Local
    proofs showed duplicate `bounds` changed the metric domain, duplicate
    `max_generations` changed the run budget, and duplicate `include` changed
    prompt context selection without any diagnostic.
  - Required result: add duplicate-key rejection for problem-local YAML setup
    files, persist or report the failing path/key clearly, and update the
    paper index so reproducibility claims do not imply duplicate-key-safe
    configuration until this is implemented.
  - Status: implemented for the current YAML setup files. Duplicate keys in
    metrics, config, and context manifests fail before run setup or context
    rendering, with path-aware diagnostics and tests.

- [x] Rich prompt sampler.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompts may include previous solutions, system instructions,
    explicit context, stochastic formatting, rendered evaluation results, and
    meta-prompt evolution.
  - Status: implemented prompt templates, deterministic local context files
    including PDF extraction, whole-template stochastic variants, compact stage
    feedback summaries, and local prompt-program selection, scoring, lineage,
    optional LLM mutation, plus configured/evolved prompt-template validation
    with quarantine and parent penalties for invalid meta-prompt outputs.
  - Remaining divergence: stochastic formatting is whole-template sampling, not
    AlphaEvolve's placeholder alternatives with configured probability
    distributions; prompt feedback rendering is bounded summary-only and does
    not retrieve full artifact contents or participate in a global prompt
    budget; context ingestion is extractive first-span selection rather than
    semantic ranking; prompt assembly has no global context-window budget or
    section-level packing policy.

- [x] Output modes beyond SEARCH/REPLACE diffs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: diff blocks are default, but AlphaEvolve can ask for a complete
    code block when appropriate.
  - Status: implemented `diff` and `full` mutation modes. Canonical
    AlphaEvolve SEARCH/REPLACE fences and the compact local fences are both
    accepted, including mixed-format blocks in document order. The built-in
    prompt template now renders mode-specific instructions for `diff` and
    `full` mode. Workspace file sections can now edit/create files, delete
    files, move/rename files, and change the primary file. Remaining divergence:
    operation selection is still prompt-driven text parsing rather than a
    typed mutation AST or planner.

- [x] Frontier model ensemble scheduling.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: combine a fast, lower-latency model for breadth with a stronger
    model for depth.
  - Status: added experimental `throughput_depth` scheduling metadata layered
    over UCB-style scores. Remaining divergence: the scheduler uses numeric
    `cost`, `latency`, and `depth` metadata but ignores descriptive `role`
    labels, so there are no breadth/depth quotas, escalation rules, or
    role-specific routing semantics yet. Ensemble telemetry now records call
    role, backend metadata, API mode, prompt/output sizes, latency, status, and
    scheduler counts. Provider usage, adapter-internal retry counts,
    response-id, finish-reason, and raw provider diagnostics remain unavailable.
    Failed-call scheduler accounting remains heuristic: failed provider
    selections advance ensemble `total` but do not increment backend pull
    counts, so fallback runs can leave state such as `total=2` and
    `counts=[0, 1]` for one failed backend and one successful backend.
    Provider response-shape validation is also incomplete: a local OpenAI
    Responses mock without `output_text` returned an empty string, and a Chat
    Completions mock with `message.content=None` caused the ensemble to raise
    `TypeError` before appending failed-call telemetry. Ensemble-level retry
    and fallback are configurable, but role-specific failure quarantine,
    malformed-output classification, and penalties remain open.

- [x] Redact LLM provider failure diagnostics before durable call logging.
  - Requirement: AlphaEvolve-style LLM-call accounting should expose provider
    failures, usage, and latency without turning SDK exception strings into
    unbounded or secret-bearing experiment artifacts.
  - Current evidence: `LLMEnsemble.generate()` records failed attempts with
    `error = str(exc)`. A local proof raised
    `RuntimeError("provider failed api_key=sk-proj_secret_123 ...")`; the full
    placeholder survived in `LLMEnsemble.call_history[-1]["error"]`.
  - Required result: add redacted/bounded provider-error telemetry before
    persisting run-scoped LLM call logs, keep structured provider error classes
    for scheduler policy, and test mutation, critique, feedback, and
    meta-prompt failure roles.
  - Status: implemented for the current ensemble telemetry boundary before any
    future durable call log. Failed provider attempts now store redacted,
    bounded error text in `LLMEnsemble.call_history` and preserve structured
    exception type plus retry/fallback metadata.

- [x] Configurable evaluation cascades.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: users can specify increasing-difficulty test ensembles and
    early-stage pruning.
  - Status: added configurable local validator stages with distinct entrypoints,
    thresholds, seeded samples, retries, stage context, and timeouts.
    Invalid stage numeric fields such as zero samples, negative retries,
    non-positive timeouts, nonnumeric thresholds, and `samples`/`seeds`
    mismatches are now rejected at startup. Distributed/parallel evaluator
    nodes remain open. Metric-specific pass criteria and explicit sample
    aggregation policies also remain open. Retry provenance is now recorded in
    `evaluation.metadata.attempts` for pass-first, fail-then-pass, and all-fail
    retry paths. A local proof with a minimize primary metric `runtime` and
    two samples returning `0.0` and `10.0` aggregated to `runtime=5.0` /
    `fitness=0.5`, confirming that current sample aggregation is a fixed mean
    policy rather than a configurable worst-case, quantile, or all-pass policy.
    Another proof with two samples returning `score=1.0`, one of them invalid,
    produced aggregate `fitness=-0.1` and `is_valid=False` while aggregate
    `metrics.score` stayed `1.0`, so invalid-sample penalty fitness can diverge
    from the reported aggregate metric vector. Threshold pruning has a similar
    consistency issue: a proof with `min_score: 0.5` and valid metrics
    `{"score": 0.2, "is_valid": True}` returned top-level `is_valid=False`
    and `stage_threshold_not_met`, while `metrics.is_valid` remained `True`
    and the validator stage was still marked `passed=True`.
    Stage metadata validation is now stricter: `Config.validate()` rejects
    non-string or blank configured stage names and `validate_path` entries and
    rejects non-JSON-safe `seeds[]` values before evaluator construction.

- [x] Require unambiguous evaluation-stage identity.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: staged evaluation outcomes should be attributable to the
    specific validator/test ensemble that consumed budget and accepted or
    rejected a candidate.
  - Current status: LibreEvolve now rejects blank and duplicate configured
    stage names at config load, before evaluator construction. Config tests
    cover duplicate names such as `gate` / `gate`.
  - Required result: make stage ids unique and stable, or reject duplicate
    or blank names at config load; update the paper index so
    configurable-cascade fidelity does not imply unambiguous stage provenance
    until this is done.
  - Status: implemented by rejecting blank/duplicate configured stage names.
    Richer stage-id/display-label separation remains future work.

- [x] Define evaluation-stage seed semantics for reproducible cascades.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: AlphaEvolve-style staged test ensembles should be reproducible
    under declared seeds or should explicitly delegate randomness to the
    validator.
  - Current gap: LibreEvolve records `eval_stages[].seeds[]` in each
    `stage_context`, but does not seed Python/NumPy/random process state for
    the validator subprocess. A local proof configured two samples with
    identical `seeds: [123, 123]`; a validator returning `random.random()`
    produced different scores while both sample metadata recorded `seed=123`.
  - Required result: either make stage seeds operational at the validator
    process boundary or update the paper index/config docs so "seeded samples"
    means "seed value supplied to the validator" rather than guaranteed
    framework-level deterministic sampling.
  - Status: implemented as operational stage seeding. For non-null stage
    seeds, LibreEvolve records a deterministic `stage["rng_seed"]`, sets
    subprocess `PYTHONHASHSEED`, and seeds Python `random` plus NumPy before
    validator import. Focused tests prove repeated identical seeds reproduce
    module-import random, evaluate-time random, and NumPy RNG values.

- [x] Strict scalar metric contract for evaluator outputs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Requirement: `evaluate` maps a solution to a dictionary of scalar
    evaluation metrics.
  - Status: implemented. Basic `metrics.yaml` schema validation rejects
    missing/duplicate names, invalid directions, multiple primaries,
    unsupported fields, malformed/non-finite bounds, and zero-width or inverted
    bounds. Evaluator output must include all declared metrics plus boolean
    `is_valid`, cannot include undeclared metrics, and every non-`is_valid`
    metric must be finite numeric. Invalid evaluator outputs are quarantined as
    `malformed_metrics`.

- [x] Enforce or disclose evaluator metric values outside declared task bounds.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: scalar metrics drive candidate ranking, database sampling,
    evaluator feedback, and budgeted search. If task metadata declares metric
    ranges, out-of-range measurements need a faithful policy because they can
    distort archive coordinates and multi-objective comparisons.
  - Previous gap: LibreEvolve validated metric-bound schema but did not enforce
    or disclose bounds on evaluator-returned values. A local proof declared primary
    `score` bounds `[0, 1]`, returned `{"score": 999, "is_valid": True}` from
    `evaluate()`, and received a valid result with raw `metrics.score` stored
    as `999.0`, no error, and normalized fitness silently clamped to `1.0`.
  - Required result: either treat out-of-range scalar metrics as invalid
    evaluator outputs, or document bounds as normalization hints and persist
    raw value, declared range, clamped normalized value, and clamp diagnostics
    wherever paper-index status claims metric-bound fidelity.
  - Status: implemented as disclosure. Out-of-range evaluator values remain
    valid raw measurements, while evaluator metadata records bound diagnostics
    with raw value, declared range, direction, clamped normalized value, and
    clamp status.

- [x] Reserve evaluator validity separately from scalar optimization metrics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: evaluator outputs are scalar metrics for optimization, while
    validity/pass-fail information gates candidate admission and cascade
    progression.
  - Previous gap: LibreEvolve required a boolean `is_valid` field, but the
    metric schema still allowed `is_valid` to be declared as the primary
    metric. That made boolean validity itself the normalized optimization
    score instead of a separate gate.
  - Required result: make `is_valid` a reserved evaluator field outside the
    scalar metric list, or at least reject it as primary; update the paper
    index so "strict scalar metric validation" does not imply the reserved
    validity boundary is fully enforced.
  - Status: implemented. `is_valid` is now rejected as a declared metric during
    problem loading, examples and README docs no longer teach it as a scalar
    metric, and evaluator output validation keeps it as a required boolean
    validity field.

- [x] Validate primary-metric selection flags as typed task schema.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: task setup defines optimization metrics explicitly enough for
    the evaluator and evolutionary loop to agree on the primary score.
  - Current gap: LibreEvolve's metric schema validates names, directions, and
    numeric bounds, but `load_problem()` still chooses the primary metric with
    `next((m for m in metrics if m.get("primary")), metrics[0])`. A local
    proof loaded `primary: "false"` from YAML, selected that metric as
    `Problem.primary_metric`, and preserved the string value in the schema.
    This means paper-index wording about strict scalar metric validation can
    overstate task-schema fidelity even when metric bounds are strict.
  - Required result: require `primary` to be boolean when present, reject
    non-boolean YAML values such as strings and integers, and update the paper
    index so the metric-validation status distinguishes scalar metric bounds
    from primary-metric selector typing.
  - Status: implemented. The loader now rejects non-boolean primary selectors,
    tests cover YAML string and integer cases, and problem-format docs describe
    absent-as-false primary selection.

- [x] Correct paper-index metric-validation wording.
  - Paper-index evidence: `papers/README.md` summarized AlphaEvolve status as
    "strict scalar metric validation."
  - Status: metric schema validation now rejects zero-width and inverted
    bounds, so the paper index no longer needs to list strict metric-bound
    ordering as an open AlphaEvolve-alignment gap.

- [x] LLM-generated feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: optional LLM graders can score hard-to-capture properties or
    discard candidates.
  - Status: implemented as optional synchronous LLM graders with metrics,
    weighted score composition, discard rules, backend provenance, raw
    responses, `history.jsonl` visibility, bounded full-workspace prompt
    rendering, basic redaction, and compact evaluator diagnostics. Parallel
    reviewer workers and calibrated grader ensembles remain open.
  - Remaining divergence: feedback scores are not validated against
    `metrics.yaml` bounds/directions and can be added directly to normalized
    fitness without calibration. The archive `selection_score` is still
    recomputed from declared evaluator metrics, so feedback-adjusted fitness is
    not a first-class MAP-Elites selection signal except as a downstream
    top-level-fitness tie-breaker. Feedback metric names are also not
    collision-prone anymore: feedback metrics now reject existing evaluator
    metrics, reserved fields, and duplicate feedback metrics before provider
    calls.
    Feedback response parsing is now strict enough to reject incidental
    numeric prose: scores require JSON or explicit `score: <number>` /
    `score=<number>` text, reject percentages and status-code prose, and must
    be finite values in `[0, 1]`.
    Feedback grader identifiers are now strict enough to reject empty or unsafe
    names/metrics at config and direct feedback boundaries. Grader
    ordering/discard semantics are now defined: graders run in order, invalid candidates skip
    later graders unless `include_invalid: true`, and skipped graders are
    recorded as feedback records and stages.
    Feedback outcomes now have first-class `llm_feedback:<name>` stage records
    with pass/fail, score, error/discard state, elapsed time, and provenance
    metadata. Feedback prompts also omit explicit
    problem context/literature: a local proof with
    `context_files={"constraints.md": "MUST return 42"}` produced a grader
    prompt without the context filename or constraint text. Feedback prompt
    diagnostic redaction is incomplete as well: evaluator stdout/stderr values
    such as `api_key=sk-proj_secret_1234567890` and
    `token=ghp_abcdefghijklmnop` were sent verbatim under `[EVALUATION]` even
    though workspace file contents are redacted. The `[METRICS]` section is
    also raw: a local proof passed
    `metrics={"score": 0.4, "debug_label":
    "sk-proj-metricsecretabcdefghijklmnopqrstuvwxyz"}` into
    `apply_llm_feedback()`, and the captured grader prompt sent the secret-like
    metric value verbatim.
  - Required result: represent LLM feedback/reviewer decisions as typed review
    or stage outcomes with score, discard, backend provenance, failures, and
    elapsed-time metadata; render bounded/redacted explicit problem context,
    source provenance, evaluator diagnostics, and metric payloads into reviewer
    prompts; keep validator stages and LLM-review outcomes queryable and
    visible in run artifacts.

- [x] Critique revision should not degrade valid generated mutations into
  parser failures.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: critique/review is part of the quality-improvement loop.
  - Status: implemented for the synchronous critique path. Revised mutations
    are previewed with the active parser; malformed revisions fall back to the
    original mutation when the original applies cleanly, and selection plus
    parser diagnostics are logged in `metadata.critique`.
  - Remaining divergence: this is still one synchronous self-revision call, not
    AlphaEvolve-scale reviewer pools or async reviewer workers.

- [x] Correct paper-index wording that implies critique failure isolation.
  - Paper-index evidence: `papers/README.md` groups "synchronous
    critique/feedback with full-workspace feedback prompts and failure
    isolation" in the AlphaEvolve status row.
  - Current evidence: LLM feedback grader failures are caught and recorded as
    `llm_feedback_failed`, but the critique provider path is not isolated. A
    local proof with `critique_enabled=True` and an LLM raising
    `RuntimeError("critique provider down")` for the critique role aborted
    `evolve()` after seed history existed and before failure history or
    structured candidate metadata was written.
  - Required result: either isolate critique provider/malformed-output failures
    with structured metadata and fallback policy, or update `papers/README.md`
    so failure isolation is attributed only to the currently implemented
    feedback-grader path.
  - Status: `papers/README.md` now separates "synchronous critique" from "LLM
    feedback graders with full-workspace feedback prompts and feedback-failure
    isolation" and lists critique provider isolation as an open gap.

- [x] Validate startup manifest payloads before overwrite cleanup.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: experiment provenance and run identity should be established
    before prior artifacts are destructively replaced.
  - Status: implemented. Startup manifest payloads are strictly serialized in
    memory before overwrite cleanup. Non-serializable provenance and non-finite
    startup problem/context metadata now fail without deleting existing known
    artifacts or writing a replacement manifest.

- [x] Make configured run identity manifest-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: run identity is part of experiment accounting and should be
    reproducible without leaking secrets or embedding control text in durable
    manifests.
  - Status: implemented with a manifest-safe identifier grammar:
    `[A-Za-z0-9][A-Za-z0-9_.-]{0,127}`. Unsafe configured ids are rejected at
    config validation, including CLI/YAML startup before `evolve()` or manifest
    writes.

- [x] Qualify provider preflight wording in the AlphaEvolve paper-index row.
  - Paper-index evidence: `papers/README.md` currently lists
    "built-in provider credential/client preflight" as implemented for the
    AlphaEvolve target.
  - Current evidence: the implemented preflight is a CLI startup guard for
    mutation-capable runs. `_preflight_llm_backends_if_needed()` checks only
    environment-variable presence for OpenAI/Anthropic, not non-blank values or
    live authentication, and `build_llm(config)` only constructs local SDK
    clients. The same guarantee does not apply to direct `evolve()` calls,
    where backend construction still happens lazily after `ProgramDatabase`
    startup.
  - Required result: revise `papers/README.md` to say "CLI-scoped built-in
    credential-presence and local client-construction preflight" or implement a
    core runtime provider-readiness invariant with non-blank credential checks
    and documented live-authentication limits.
  - Status: `papers/README.md` now scopes the implemented claim to
    "CLI-scoped provider credential-presence and local client-construction
    preflight for mutation-capable runs" and lists direct-runtime provider
    preflight plus non-blank/live authentication as open.

- [x] Qualify plugin preflight wording in the AlphaEvolve paper-index row.
  - Paper-index evidence: `papers/README.md` described "plugin name/cadence
    preflight" as implemented, which could read as a general core-runtime
    guarantee.
  - Current evidence: CLI startup validates built-in plugin aliases before
    run-directory preparation, and current built-in plugin constructors reject
    invalid cadence values. Direct `evolve()` plugin resolution, configured-vs-
    executed plugin provenance, custom plugin schemas, and plugin config
    persistence remain open elsewhere in this TODO.
  - Required result: make the AlphaEvolve row distinguish the implemented CLI
    alias and constructor-cadence boundaries from unresolved plugin
    configuration/provenance work.
  - Status: `papers/README.md` now says "CLI built-in plugin alias preflight"
    and "constructor-level built-in plugin cadence validation" instead of the
    broader "plugin name/cadence preflight."

- [x] Make run-name identity cross-platform safe before treating run
  directories as reproducible experiment ids.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: run identity, manifests, and artifact directories should be
    portable enough for replay and comparison across supported hosts.
  - Status: implemented. Run names now reject Windows reserved device names
    with or without extensions, leading/trailing whitespace, trailing dots,
    path separators, invalid filename characters, control characters, and
    non-NFC Unicode spellings before artifact preparation or manifest writes.

- [x] Treat invalidly encoded config files as setup diagnostics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: task configuration should be parsed or rejected before the run
    begins, with diagnostics that identify the failing setup artifact.
  - Current gap: malformed YAML after successful UTF-8 decoding is reported as
    a path-aware `ConfigError`, but invalid UTF-8 is not. A local temp CLI
    probe with `config.yaml` bytes `b"log_dir: \xff\n"` produced a generic
    codec error without the `config.yaml` path.
  - Required result: normalize config decode failures into path-aware startup
    diagnostics and prove they occur before provider/plugin construction or run
    artifact mutation.
  - Status: implemented for the CLI config-loading boundary. Invalid UTF-8 in
    problem-local `config.yaml` now raises a path-aware `ConfigError` before
    YAML parsing or run setup, and regression coverage checks the reported
    path plus UTF-8 diagnostic.

- [x] Record runtime environment and dependency provenance for experiments.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4, 2.6, and 4.
  - Requirement: long-running evaluator-heavy experiments and ablations should
    be comparable across machines and over time, which requires provenance for
    the runtime environment as well as source/problem files.
  - Status: implemented for local runtime/package metadata. Manifest
    provenance now includes Python version/implementation, platform/system
    metadata, `pyproject.toml` hash, package name/version and
    `requires-python`, build backend metadata, and installed versions for
    declared runtime dependencies.
  - Remaining divergence: no lockfile, full environment-variable snapshot,
    accelerator driver/runtime metadata, or live provider service/API-version
    provenance.

- [x] Make package metadata provenance robust to malformed local project files.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4, 2.6, and 4.
  - Requirement: runtime/package provenance should support reproducible
    experiments without turning local packaging mistakes into ambiguous startup
    crashes.
  - Status: implemented as degraded provenance. Malformed TOML, non-UTF-8
    bytes, and unreadable `pyproject.toml` files are represented by explicit
    `package.pyproject.status` values rather than raw startup crashes; readable
    files still retain hash/size provenance even when package metadata is not
    usable.

- [x] Make problem-input provenance exclusions auditable.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: problem setup and context should be reproducible from
    recorded task/evaluator/source provenance without silently omitting inputs
    that affected evaluation or prompts.
  - Status: implemented for problem tree provenance. Ordinary problem-owned
    directories named `runs` are included, and tests prove changes under
    `problem/runs/fixture.txt` affect the problem tree hash. The active
    generated run directory from the effective run config is skipped only when
    it resolves inside the problem tree, with `reason: excluded_output_root`.
    Cache-directory skips and link skips are also persisted with reasons.

- [x] Make source/problem provenance symlink behavior auditable.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: recorded task, source, and evaluator provenance should
    identify the actual experiment inputs without depending on unrecorded
    host-local paths.
  - Status: implemented as a no-follow policy. Source/problem provenance now
    skips symlinks and Windows junctions before descending or reading bytes,
    records skipped entries with `reason: link_not_followed`, and excludes
    linked targets from the tree hash. Tests cover file-symlink skipping where
    supported and Windows junction skipping.

- [x] Treat evaluator artifact pattern schemas as benchmark evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: evaluator-generated artifacts should be reproducibly selected
    by task configuration. Pattern schemas and diagnostics need to match file
    artifact semantics, not unrelated environment allowlist rules.
  - Current status: artifact include/exclude config is now validated as
    artifact glob lists, separately from environment allowlists. Tests cover
    top-level and per-stage artifact patterns containing `=`.
  - Required result: define artifact pattern grammar, validate it separately
    from environment variable names, and cover top-level/stage artifact
    patterns in tests before treating evaluator artifacts as robust benchmark
    evidence.
  - Status: implemented for non-empty glob-string schema validation.

- [x] Evolutionary database with attached outputs and feedback.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: solutions have scores and program outputs attached, and the
    database resurfaces ideas to balance exploration/exploitation.
  - Status: JSONL records include raw metrics, structured evaluation output,
    per-program archive admission events, and configurable in-memory
    score/metric/novelty/recency inspiration sampling. This covers scalar
    metrics, stdout/stderr, stage diagnostics, artifact metadata, and bounded
    structured program-output metadata through reserved `outputs` /
    `program_output` evaluator return keys. Queryable persisted feedback and
    lineage-aware sampling remain open.
    `metadata.score_composition` stores per-plugin score adjustments, and
    archive admission is now gated by evaluator/feedback validity as well as
    final composed fitness. Full MAP-Elites cell/island snapshots plus
    migration events are not persisted. Population config semantics now define
    `migration_ratio=0.0` as selecting no migrants; positive migration ratios
    still round up to at least one migrant from a non-empty island. Repeated
    migration is not idempotent: a local proof with one program and two islands
    produced four copies of the same `Program.id` in each island's
    `elite_archive()` after three migrations, even though each island had only
    one occupied grid cell.
    Admission semantics still conflate MAP-Elites grid entry/replacement with
    auxiliary elite-list retention: a local proof with one cell and a large
    elite list produced `admitted=True`, `reason="elite_only"`, and
    `entered_cell=False` for a lower-scoring same-cell candidate while the grid
    occupant did not change. A follow-up proof showed that the `elite_only`
    candidate remains in `elite_archive()` but is absent from the occupied-cell
    pools used by parent/inspiration sampling, so the persisted admitted flag
    does not mean the candidate changed the behavior map or will be resurfaced
    by the current sampling policies. Recency sampling is also
    generation-based rather than true database insertion recency: a local proof
    added an older high-scoring generation-0 program and then a newer
    low-scoring generation-0 program, and
    `IslandModel.sample("recency")` returned the older candidate because score
    broke the generation tie. There is no persisted insertion/admission
    sequence for seeds, same-generation batches, or future replay/resume.
    Island assignment cursor semantics are also not explicit: a local proof
    using `ProgramDatabase.admit()` showed a threshold-passing valid
    `not_improving_cell` candidate returning `admitted=False` on island `0`
    while still advancing the island cursor, so the next accepted candidate was
    assigned to island `1`. Inspiration `mixed` sampling is likewise not yet
    a principled mixture: `sample_diverse(strategy="mixed")` concatenates
    metric leaders, novelty order, selection order, and a random tail before
    truncation. A local proof with three occupied candidates returned the same
    deterministic prefix across five repeated calls (`metric_a` for `k=1`, and
    `metric_a, novel` for `k=2`), while only explicit `random` sampling varied.
    Plugin side effects can also corrupt the history record after evaluation:
    a local proof added
    `program.metrics["plugin_bad"] = inf` in `on_evaluated()`, after which
    `evolve()` raised `StrictJsonlError` while writing `history.jsonl`.
    Feedback response persistence is not covered by the feedback prompt
    redaction path: a local proof returned a provider-key-like placeholder
    from an LLM feedback grader, and the value remained in
    `evaluation.metadata.llm_feedback[].raw_response` and parsed `feedback`.
    Feedback-provider failure messages are also raw: a local proof raised
    `RuntimeError("feedback provider failed token=ghp_feedback_secret_1234567890")`,
    and `apply_llm_feedback()` stored the exact string under
    `evaluation.metadata.llm_feedback[].message`.
    Plugin prompt-context provenance is also not schema-validated before it
    enters candidate metadata: a local proof stored a Python `set` under
    `metadata.plugin_context[].metadata`; `ProgramDatabase.log()` raised
    `StrictJsonlError`, quarantined the candidate record, and wrote no accepted
    `history.jsonl` row. Top-level program fitness is now finite-checked before
    archive insertion through direct database/archive paths, and `show` rejects
    non-finite history fitness rows; future resume/checkpoint loading still
    needs to reuse the same predicate.
  - Required result: split persisted database fields so later analysis can tell
    whether a candidate changed a MAP-Elites behavior cell, was retained only in
    a global/auxiliary elite list, or was merely evaluated and logged; validate
    plugin-added metrics/metadata before they enter persisted program records;
    validate plugin prompt-context metadata at the hook boundary;
    reuse finite top-level fitness checks during future resume/replay;
    persist a real candidate insertion/admission sequence for recency sampling;
    define whether island round-robin assignment advances on attempted
    candidates, admitted candidates, or actual archive-state changes;
    define mixed inspiration sampling as either a documented deterministic
    cascade or a seeded weighted/stochastic policy with replay diagnostics;
    add a validated structured-output attachment channel for evaluator-returned
    non-scalar data without weakening the scalar metric contract; and define
    redaction/hash/retention policy for raw LLM feedback responses and failure
    messages before they become database records or future prompt context. Also
    cover invalid-record quarantine snapshots: `append_quarantine_record()`
    stores `repr(record)`,
    and a local proof with a non-finite history record containing
    provider-key-like placeholders in two metadata fields persisted both values
    verbatim in `history_invalid.jsonl`, outside the current validator-output
    redaction path.

- [x] Keep parent-selection exploration distinct from island migration in
  AlphaEvolve comparison docs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 2 and Section 2.5.
  - Requirement: the program database samples parent programs and inspirations,
    while island/MAP-Elites population structure is a separate archive policy.
  - Current evidence: LibreEvolve's default 70/30 exploit/explore mix lives in
    `evolve()` parent selection via `config.explore_ratio`; `IslandModel.migrate()`
    is separately controlled by `migration_interval` and `migration_ratio`.
    README currently attaches "(70% exploit / 30% explore)" to "5-island
    migration" in the feature list and tree comment, which conflates sampling
    policy with migration.
  - Required result: keep paper-alignment docs and README feature claims clear:
    parent sampling uses the default explore/exploit mix, while migration is a
    periodic ring-copy operation with separate configuration and evidence.
  - Status: fixed in README. Island migration no longer carries the 70/30
    explore/exploit parent-sampling mix in the feature list or project tree.

- [x] Preserve invalid seed diagnostics as first-class database evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: initial and evolved solutions should have evaluation scores,
    outputs, and feedback attached so the evolutionary database and run
    accounting explain what was tried under the compute budget.
  - Previous gap: invalid seeds were logged to `history.jsonl` with
    `archive_admission.reason = invalid_evaluation`, but were not written to
    `failure_history.jsonl` or another seed-diagnostic stream. With an
    all-invalid seed population, the run stopped before any LLM mutation and
    left failure memory empty even though evaluated invalid candidates existed.
  - Required result: record invalid seed evaluations with diagnostics and
    admission reasons in a queryable artifact. No-valid-seed stop accounting
    now distinguishes startup exhaustion from a real generation; the remaining
    gap is queryable invalid-seed diagnostics.
  - Status: implemented. Invalid/rejected seeds are now queryable in
    `failure_history.jsonl` with `record_type: "seed"`, evaluator diagnostics,
    archive-admission reason, and seed file deltas; the seed history row also
    references the failure record. Mixed valid/invalid seed runs render recent
    seed failures in the first mutation prompt.

- [x] Define initial-seed feedback and score-composition semantics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: evaluated programs should carry comparable score/feedback
    evidence in the program database, or the system should clearly distinguish
    baseline seed records from post-processed generated candidates.
  - Previous gap: LibreEvolve evaluated and logged initial seeds before optional
    LLM feedback graders and plugin `on_evaluated()` score composition are
    applied. A local proof with LLM feedback configured and a score-boosting
    plugin, run with `max_generations=0`, produced a seed row with
    `fitness=0.2`, no `evaluation.metadata.llm_feedback`, no
    `metadata.score_composition`, and no feedback LLM calls.
  - Required result: either run the same feedback/plugin composition pipeline
    for seeds, or persist an explicit seed-baseline policy in history/manifests
    and paper docs so seed records are not treated as fully comparable
    AlphaEvolve-style evaluated candidates.
  - Status: implemented as explicit seed-baseline semantics. Seed rows carry
    `metadata.candidate_type = "seed"` and a raw-evaluator-baseline
    post-processing policy marking LLM feedback and plugin score composition as
    not applied; generated candidates are marked separately. `manifest.json`
    records the policy, and tests cover configured LLM feedback plus plugin
    score composition without changing seed fitness or constructing an LLM.

- [x] Enforce typed validity at the validated database-admission boundary.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the evolutionary database should preserve evaluated programs
    and support archive/query decisions from faithful score and validity
    evidence.
  - Current status: `ProgramDatabase.admit()` and the loop validity helper now
    require `evaluation.is_valid is True` before archive insertion, and
    `libreevolve show` uses the same exact boolean validity requirement for
    modern history selection. Missing, string, integer, and false values are
    rejected as invalid evaluation evidence.
  - Required result: require exact boolean validity for live archive insertion,
    keep legacy-history read fallbacks separate from admission semantics, and
    test malformed validity values at database/plugin/resume/show boundaries.
  - Status: implemented for `ProgramDatabase.admit()`, plugin-corrupted loop
    records, and current `show` inspection. Raw lower-level archive insertion
    remains tracked separately below. Future resume loading must reuse the same
    typed predicate when archive checkpoints exist.

- [x] Treat unmatched explicit-context includes as task-setup diagnostics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: explicit task context and literature are part of the prompt
    evidence supplied to the LLM. A reproducible setup should not silently omit
    a declared context source because of a manifest typo.
  - Current gap: LibreEvolve's `context.yaml` include patterns are not audited
    for matches. A local proof with `include: ["missing.md"]` loaded a problem
    successfully with no selected context and, when no other context files were
    present, no skipped-source diagnostic. A second proof with `notes.md`
    present reported only `notes.md` as `not_included`, not the unmatched
    `missing.md` include rule.
  - Required result: record per-pattern match counts and unmatched include
    diagnostics, or fail problem loading for unmatched required includes; update
    paper-index wording so deterministic local context ingestion does not
    overstate context-manifest correctness.
  - Status: implemented as diagnostics rather than hard failures.
    `context_policy.include_patterns` records match counts and
    `unmatched_includes` records unmatched manifest rules; loader tests cover
    mixed and empty-context cases, and the paper index now names unmatched
    include diagnostics explicitly.

- [x] Validate explicit-context pattern identifiers before paper-level claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: explicit context/literature selection should be a reproducible
    task contract with safe, problem-local selectors.
  - Current gap: `context.yaml` include/exclude values are only validated as
    strings. A local proof accepted `../secret/*.md`, `/absolute/*.md`, and
    `api_key=sk-proj_secret_1234567890\n*.md`, then persisted those raw values
    in `problem.context_policy.include`.
  - Required result: define and enforce a safe context-pattern grammar, or
    clearly qualify paper-index wording so context-manifest provenance is not
    mistaken for validated literature/context selector fidelity.
  - Status: implemented for manifest pattern strings. Include/exclude patterns
    now use a documented problem-relative glob grammar and reject traversal,
    absolute/drive-style roots, backslashes, empty strings, and control
    characters. Source path-label redaction remains tracked separately.

- [x] Treat invalid context-manifest syntax/encoding as setup diagnostics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: explicit context and literature selection should be a
    reproducible task contract with clear setup failures.
  - Current gap: LibreEvolve catches unsupported context-manifest fields and
    duplicate manifest files, but malformed YAML or invalid UTF-8 in
    `context.yaml` / `context.yml` raises raw parser/decoder exceptions. Local
    proofs produced `ScannerError` and `UnicodeDecodeError` without a
    path-scoped context-manifest diagnostic.
  - Required result: add path-aware manifest parse/decode diagnostics and tests
    before paper-index claims treat context manifests as a robust
    AlphaEvolve-style literature/context contract.
  - Status: implemented for local explicit-context manifests. Invalid UTF-8 and
    malformed YAML now raise path-aware setup diagnostics at load time, with
    focused loader tests covering both failure modes.

- [x] Preserve formatting-sensitive explicit context or record normalization.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: explicit prompt context can contain instructions, code, math,
    or literature excerpts whose formatting may be semantically relevant.
  - Current gap: LibreEvolve hashes raw selected context files, but non-PDF
    text extraction strips the decoded text before prompt rendering. A local
    proof with `.txt` content `'  leading\nbody\n\n'` rendered as
    `'leading\nbody'`; metadata `bytes` referred to the raw file while
    `chars_original` referred to the stripped text. This makes the manifest
    source hash and prompt-visible excerpt describe different text views
    without an explicit normalization field.
  - Required result: preserve UTF-8 text/code context exactly or manifest the
    normalization policy per source, with tests for whitespace-sensitive code
    snippets, equations, and trailing-blank-line context.
  - Status: implemented and tested. Non-PDF `.txt`, `.md`, and `.py` context is
    now decoded as UTF-8 without `.strip()`, preserving leading/trailing
    whitespace, blank lines, and fenced code blocks. Loader tests cover
    whitespace-sensitive text/code context, and docs describe the policy.

- [x] Enforce problem-local boundaries for explicit context sources.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: explicit context is part of the user-provided task setup, so
    prompt-visible literature/code snippets should be attributable to the
    configured problem context.
  - Status: implemented for local explicit context ingestion. LibreEvolve now
    rejects linked `context/` directories, linked context manifests, and
    symlink/junction entries under `context/` before selection or reading, so
    prompt-visible context cannot silently come from host-local linked targets.
    Tests cover file-symlink rejection where supported, linked manifest
    rejection where supported, and Windows junction rejection.

- [x] Failed-trial and rejected-mutation memory.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figures 1-2 and Section 2.2.
  - Requirement: the program database and prompt sampler provide rich context
    containing past trials, ideas, quality scores, and feedback so future
    generations can learn from explored attempts.
  - Status: implemented as a local JSONL failure index plus bounded recent
    prompt memory. `failure_history.jsonl` records failed/rejected proposals
    with error causes, bounded evaluator output summaries, changed files,
    parent ids, mutation text, and repetition counts. Remaining divergence:
    failure retrieval is a recent-tail heuristic, not a learned or
    diversity-aware sampler over all historical negative examples. The
    prompt-rendered recent tail now includes compact bounded evaluator
    error/stdout/stderr and recent stage summaries from JSONL failure records.
    Invalid failure-history append diagnostics now use
    `failure_history_invalid.jsonl`.
  - Remaining durability gap: failure-history append failures are quarantined
    separately, but `ProgramDatabase.log_failure()` mutates in-memory
    repetition counts and candidate `failure_record` metadata before the append
    succeeds. A local proof with non-serializable `diff_error={"bad": {1, 2}}`
    wrote no accepted `failure_history.jsonl` row while `_failure_counts` and
    child metadata still reflected a logged failure.
  - Required result: make failure-history logging transactional with its
    in-memory counters/metadata, or clearly document this as best-effort
    prompt-memory state until database durability is stronger.

- [x] Robust history read/inspection path for long experiment stores.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Requirement: the program database is the durable substrate for selection,
    inspection, and future prompt context; long append-only experiment logs
    need controlled failure modes when a record is malformed.
  - Current status: `libreevolve show` now streams `history.jsonl`, fails
    malformed JSON and non-object rows with line-numbered `ClickException`
    diagnostics, preserves empty-history handling, and requires explicit
    archive admission plus boolean evaluator validity for modern history
    selection.
  - Status: implemented as a fail-fast inspection policy with tests for
    malformed JSON, non-object rows, empty histories, strict modern validity,
    large legacy histories, and no-admitted-modern histories.

- [x] Full-file/full-codebase evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 4 ablations.
  - Requirement: AlphaEvolve evolves whole code files/codebases and ablates
    "No full-file evolution" as a weaker setting.
  - Current evidence: `CandidateWorkspace` supports local text file sets,
    `<<<FILE path ... >>>FILE` mutation envelopes, full-mode file creation,
    workspace materialization for validators, and JSONL file-set logging.
  - Status: implemented for local Python/text workspaces. Remaining divergence:
    no arbitrary external repository/build-system runner and `best.py` exports
    only the primary file convenience view. Binary/static artifacts are not
    first-class candidate members yet. Validator subprocesses now run with the
    candidate root as `cwd` and import path, but there is still no arbitrary
    external repository/build-system runner. Candidate path collision handling
    is also incomplete: candidate construction rejects duplicate normalized
    paths and materialization rejects case-folded host-path collisions before
    writes, and duplicate file edit sections are rejected before partial
    application, but complex topology-operation collision policy remains
    incomplete.
    File/block envelope diagnostics now reject malformed sections before
    partial edits are applied. File-set topology changes such as delete, rename,
    move, and primary-file replacement are implemented with command file
    sections, but command-section bodies are not validated yet: non-empty
    `DELETE`, `MOVE`, or `PRIMARY` bodies are silently discarded while the
    topology operation succeeds. POSIX-style absolute candidate paths and UNC-style
    leading-backslash paths are now rejected instead of being rewritten into
    relative candidate files. Host-invalid/control-character paths are also
    rejected at the shared file-set boundary: ASCII controls, DEL,
    wildcard/quote/pipe characters, Windows reserved device-name components,
    leading/trailing spaces, and trailing dots fail during workspace
    construction or mutation parsing with unsafe-path diagnostics.

- [x] Validate serialized codebase-candidate records before replay/resume.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: evolved full-file/codebase candidates and their attached
    database records must be faithful enough to resurface, analyze, and replay
    candidate ideas.
  - Status: implemented for the in-memory/serialized workspace boundary.
    `CandidateWorkspace.from_dict()` now rejects non-mapping records,
    non-mapping `files`, non-string paths, non-string contents, non-string
    primary files, and missing primary files instead of coercing them with
    `str()`. Direct construction enforces the same string path/string content
    invariant.
  - Required result: define a strict serialized workspace schema for history
    and future resume state, enforce typed workspace contents at construction
    and restore boundaries, reject malformed records without coercion, and test
    corrupted history/replay inputs before claiming database-backed
    codebase-candidate fidelity.

- [x] Make primary-code compatibility views faithful to workspace candidates.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: full-file/codebase candidates and their database records
    should identify the same program when surfaced for inspection, sampling,
    prompt construction, and artifact export.
  - Current gap: LibreEvolve keeps a legacy `Program.code` string alongside
    `Program.files` and `primary_file`, but does not reject or reconcile
    disagreement when both are provided. A local proof constructed a candidate
    with `Program.code == 'x = "legacy"\n'` and `files["main.py"] ==
    'x = "workspace"\n'`; `best.py` was written from the legacy code while
    `best_workspace/main.py` was written from the workspace content. This
    undermines the paper-status claim that full-workspace artifacts make the
    selected codebase recoverable as one coherent candidate.
  - Status: implemented. Workspace files are canonical when present, all
    primary-code compatibility views are derived from the primary workspace
    file, and tests cover database logging, `show`, prompt rendering, and
    best-artifact export.

- [x] Full-workspace output artifacts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Section 2.1.
  - Requirement: if a candidate is a full file/codebase, the selected best
    candidate must be recoverable as a full codebase.
  - Status: implemented for local text-file candidate workspaces. The CLI
    writes `best.py` as a primary-file compatibility view and materializes the
    complete best file set under `best_workspace/`; run-artifact docs and CLI
    tests cover this behavior.
  - Remaining divergence: binary/static non-text artifacts are not first-class
    candidate members, and resume semantics remain unresolved. Run-directory
    collision policy is implemented as fail/overwrite, but it is not resume.
    The committed example run directories are legacy history-only fixtures and
    do not include `best_workspace/`, so they do not prove the current
    full-workspace artifact contract.

- [x] Canonical AlphaEvolve diff block compatibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Figure 3.
  - Requirement: support the paper's SEARCH/REPLACE fence spelling when using
    AlphaEvolve-style prompts or examples.
  - Status: implemented in `libreevolve/core/diff.py` while preserving the
    compact local format; tests cover canonical parsing for normal candidates,
    evolve-block candidates, mixed-format document order, multi-file file
    sections, and duplicate `<<<BLOCK ...>>>` rejection for multi-block full
    replacement.
  - Required result: keep accepting both canonical and compact diff formats
    without breaking existing seeds/tests.

- [x] Meta-prompt evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt instructions/context can be co-evolved in a separate
    database.
  - Current evidence: `PromptDatabase` stores prompt programs, logs
    `prompt_history.jsonl`, records prompt rewards/usages, and supports
    lineage-preserving mutation. `evolve()` uses prompt programs during prompt
    construction and can optionally ask the active LLM to mutate templates.
  - Status: implemented locally. Prompt-program reward now has an explicit
    absolute/improvement mode, bounded normalization, configurable exploration
    coefficient, and persisted reward telemetry. Initial configured prompt
    variants are now selected through untried prompt programs in config order.
    Prompt-program reward is still a scalar final-score/improvement policy rather than a
    multi-metric prompt-fitness model. Meta-prompt mutations are currently
    template-only LLM rewrites: a local proof captured the meta-prompt request
    after reward telemetry had been recorded and it contained only the generic
    improvement instruction plus the selected template, not prompt rewards,
    candidate outcomes, rejected-mutation diagnostics, competitor prompt stats,
    or evaluator/failure evidence. Mutations are syntax-checked, dry-run
    rendered, and checked for parent-placeholder retention; children that drop
    parent channels such as `{parent_code}` or `{mutation_instructions}` are
    quarantined and penalized. There is no full experiment
    AlphaEvolve-equivalent ablation harness. Prompt-program identity is also
    not content-aware: a local proof seeded two identical `DEFAULT_TEMPLATE`
    strings and `PromptDatabase` created two independent UUID4 prompt programs
    with identical templates. Invalid meta-prompt mutation penalties are now
    selection-effective parent-arm penalties: rejected prompt children count as
    one parent use with `-1.0` reward and persist updated selection statistics
    in `prompt_history.jsonl`. Rejected-template persistence is now
    metadata-safe: invalid rejection metadata writes a diagnostic quarantine row
    and leaves parent prompt selection state unchanged.

- [x] Distinguish prompt-produced candidates from seed baselines in run
  artifacts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: the program database and prompt database should provide
    auditable provenance for how candidates were generated and selected.
  - Previous gap: LibreEvolve recorded `prompt_program_id` for generated
    candidates, but initial seed evaluations entered `history.jsonl` before any
    prompt program was selected. A local zero-generation run showed a seed row
    without `metadata.prompt_program_id`, while `prompt_history.jsonl` contained
    only the initial prompt-template `add` event. Artifact docs phrased
    prompt-program linkage as if it applied to program records generally.
  - Required result: add explicit candidate-source provenance for seeds versus
    prompt-generated children, or create a baseline prompt/source record for
    seeds; update paper-index and artifact wording so prompt-database support
    is not overstated as universal candidate traceability.
  - Status: implemented. History rows now distinguish seed baselines and
    prompt-generated candidates with `metadata.candidate_type`; only generated
    rows carry `metadata.prompt_program_id`, while seed rows carry explicit
    raw-baseline policy metadata. Run-artifact and paper TODO text now state
    that prompt-program traceability is not universal for seed baselines.

- [x] Clarify prompt-template validation in the paper index.
  - Paper-index evidence: `papers/README.md` describes the AlphaEvolve status
    as having "configured/evolved prompt-template validation with quarantine
    and parent penalties for invalid meta-prompt outputs."
  - Previous evidence: `validate_prompt_template()` rejected malformed Python
    format fields and required only `{task}`. A local proof admitted a mutated
    template `Task only: {task}`, omitting `{parent_code}`,
    `{mutation_instructions}`, feedback, context, and inspiration channels.
    Render-time format-spec validation is implemented: configured and evolved
    templates are dry-run rendered with representative values, and incompatible
    specs such as `Task formatted numeric: {task:.2f}` are rejected before use.
  - Required result: either enforce semantic placeholder retention and
    render-time format-spec validation for evolved prompt templates, or update
    the paper index to say validation is currently partial syntax/schema
    validation only.
  - Status: implemented for the current prompt-program boundary.
    `PromptDatabase.mutate()` now rejects evolved prompt children that drop any
    placeholder used by their parent, quarantines the rejected mutation, and
    penalizes the parent prompt arm. Remaining paper-index gaps are higher
    level: context-policy evolution, prompt deduplication, ablation reporting,
    and stronger evidence that evolved prompt wording improves benchmark
    outcomes.

## Local Paper Corpus Issues

- [x] Refresh the local paper index after implementation passes.
  - Evidence: `papers/README.md` still listed multi-file candidates, critique,
    LLM feedback, and meta-prompt evolution as open after those local
    implementations landed.
  - Status: refreshed the AlphaEvolve row to distinguish implemented local
    behavior from remaining async, multi-objective, database, full-workspace
    export/resume, run-identity/evaluator-provenance, metric-validation,
    feedback-calibration, LLM-accounting, config-validation, and benchmark
    gaps.
  - Required result: keep the paper index aligned with current code whenever
    todo items are completed or reopened.

- [x] Remove stale implemented-gap claims from the AlphaEvolve paper-index row.
  - Evidence: `papers/README.md` still listed workspace file-topology
    mutation, full-workspace best export, full-workspace feedback grading,
    feedback failure isolation, workspace materialization plus basic candidate
    imports in local validators, strict scalar evaluator-output validation, and
    broad top-level config validation as remaining AlphaEvolve gaps even though
    current code/docs/tests cover those local implementations.
  - Status: refreshed the AlphaEvolve status row so implemented local behavior
    is not duplicated in the remaining-open list. The row still calls out
    unresolved gaps such as flexible candidate abstractions, binary/static
    artifacts, candidate path-collision handling, workspace-aware descriptors,
    async workers, provider failure policy, network/container sandboxing,
    provider token/cost/stage-sample budgets, true multi-objective search,
    queryable database, archive/resume state, reproducible ids, feedback
    calibration, role-specific LLM routing/reward policy, plugin provenance,
    and benchmark hardening.

- [x] Reconcile the AlphaEvolve paper-index open-gap list with current
  implementation evidence.
  - Evidence: `papers/README.md` still listed validator helper/candidate import
    precedence, proposal-batch generation/sibling-candidate accounting,
    external/transitive evaluator environment provenance, custom plugin
    entry-point discovery, direct-runtime provider preflight, and
    archive-state/migration persistence as broad open gaps. The
    runtime-accounting note still described `llm_calls.jsonl` call ids as UUID
    telemetry identities.
  - Status: refreshed the AlphaEvolve row so implemented surfaces are no
    longer duplicated in the remaining-open list. Current evidence now covers
    validator helper precedence checks, sequential sibling proposal batches,
    configured entry-point plugin loading with manifest-safe constructor
    options and schema validation, deterministic `llm-call-...` ids,
    CLI-scoped provider client-construction preflight, and archive-state
    snapshots with full archive-content restore.
  - Remaining paper gap: migration-event replay, controller/pending-work
    resume state, full resume and seeded lineage replay, live provider
    authentication, token/cost/time stop enforcement, provider cancellation,
    richer direct custom plugin provenance, provider-output replay, and real
    AlphaEvolve-scale benchmark/certification fixtures remain open.
  - Verification: source/test inspection covered proposal batches, entry-point
    plugin specs, deterministic call ids, and archive-restore evidence before
    the paper-index wording was patched.

- [x] Reconcile paper-index TODO coverage cross-references with actual backlog
  evidence.
  - Evidence: the `papers/README.md` TODO coverage table listed broad TODO
    files for each paper row and implied active `docs/todo/readme.md` and
    `docs/todo/roadmap.md` coverage for rows whose evidence was actually
    completed or grouped.
  - Status: replaced the single coverage column with active and
    completed/grouped evidence columns. The table now points current gaps at
    open paper/code backlog files, uses grouped labels for background and
    benchmark-candidate rows, and keeps README/ROADMAP references in completed
    evidence where there is no active row-specific work.
  - Remaining paper gap: background and benchmark-candidate rows still depend
    on grouped benchmark-fixture TODOs until real row-specific fixtures or
    certifiers are implemented.
  - Verification: the TODO ledger was checked before editing; active README and
    ROADMAP backlog counts were zero, while open paper/code items remained.

- [x] Tighten paper-index wording around validator execution boundaries.
  - Evidence: `papers/README.md` described implemented AlphaEvolve-alignment
    behavior as "validator environment isolation."
  - Current evidence: validators run in a local subprocess with an explicit
    minimal environment plus `validator_env_allowlist`, persisted stdout/stderr
    redaction, timeout process-tree cleanup, and optional artifact copy-out.
    This is not a security sandbox or full environment isolation: network
    egress policy, container isolation, and resource controls remain open.
  - Status: paper index now says "validator environment allowlisting with
    stdout/stderr redaction" and lists network/container sandboxing as an open
    gap.
  - Required result: avoid using "isolation" for current validator execution
    until the implementation provides a stronger sandbox boundary.

- [x] Treat provider-key redaction coverage as part of experiment-artifact
  safety.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: persisted prompts, evaluator diagnostics, artifacts, and
    provider telemetry are experiment evidence. Secret-redaction claims should
    be tested against realistic provider-key shapes before the paper index
    treats current artifacts as safe for broad retention.
  - Current evidence: evaluator, prompt, and feedback redaction helpers share a
    token pattern that catches underscore forms such as `sk-proj_...`,
    `ghp_...`, and `github_pat_...`. A local proof showed the hyphenated
    `sk-proj-abcdefghijklmnopqrstuvwxyz123456` form passed through all three
    helpers unchanged.
  - Required result: centralize and test secret-pattern redaction for current
    provider-key formats across evaluator stdout/stderr, text artifacts,
    prompt/history rendering, feedback prompts, and provider-error telemetry;
    keep paper-index safety wording scoped until that proof exists.
  - Status: implemented for shared local redaction paths. A centralized helper
    now covers hyphenated OpenAI project-key shapes plus existing underscore
    forms, with tests for evaluator stdout/stderr, copied text artifacts,
    prompt summaries, and feedback prompts. Provider-error telemetry remains
    explicitly open elsewhere in this paper TODO.

- [x] Decide and document the paper corpus source of truth.
  - Evidence: `papers/download_manifest.csv` lists 24 downloaded papers, while
    the README claims 23 references.
  - Required result: update README badges/text and possibly add a
    `papers/README.md` that explains why each PDF is present.

- [x] Track the paper index and manifests without committing PDFs.
  - Evidence: README points readers to `papers/README.md`, but `.gitignore`
    ignored the entire `papers/` directory.
  - Status: `.gitignore` now ignores `papers/*` while allowing
    `papers/README.md`, `download_manifest.csv`, and
    `download_manifest.json`.
  - Required result: keep small paper-index evidence in version control while
    leaving large cached PDFs local.

- [x] Add paper-index validation to CI or document manual verification.
  - Paper-index evidence: `papers/README.md` is the public status table that
    distinguishes AlphaEvolve requirements from other paper-inspired or
    background-only work, and README points readers to it for implementation
    status and benchmark coverage decisions.
  - Previous evidence: the GitHub Actions `Tests` workflow was disabled at the
    time of this item. Paper-index edits could therefore bypass the workflow's
    secret scan and test jobs unless local validation was performed, and no
    automated check currently confirmed that
    the 24 PDFs, CSV/JSON manifests, README badge count,
    paper-status rows, and benchmark coverage claims remain synchronized. The
    download manifests record URL, path, byte count, status, message, and now
    SHA-256 hashes for each cached PDF, but the hashes are stored in a
    hyphenated display form rather than canonical 64-hex lowercase/uppercase
    form, and they are not yet checked by an automated validation command.
  - Required result: add an automated paper-cache/index validation command
    covering PDF count, manifest rows, duplicate/missing IDs, per-PDF content
    hashes, canonical hash formatting or documented hyphenated formatting,
    README badge count, required AlphaEvolve status fields, and
    benchmark-coverage decisions, or document a required manual verification
    procedure for paper-index changes until such a workflow exists.
  - Partial status: `papers/download_manifest.csv` and
    `papers/download_manifest.json` now include SHA-256 hashes for all 24 local
    cached PDFs, but no automated validation command or CI path currently
    checks those hashes against the ignored local PDF cache. A local manual
    PowerShell check on 2026-05-25 confirmed that all 24 CSV manifest hashes
    match the corresponding PDFs after removing hyphens from the stored hash
    strings.
  - Status: manual verification documented. Superseded by later workflow
    hardening: README and `docs/development.md` now describe path-scoped
    `push` / `pull_request` triggers for source, docs, TODO, paper-index, and
    workflow changes, while local paper-cache verification remains documented
    for ignored local PDFs.

- [x] Make paper-index validation instructions match GitHub workflow state.
  - Paper-index evidence: paper truthfulness depends on repeatable checks for
    paper counts, manifest hashes, implementation-status rows, benchmark
    coverage, and AlphaEvolve divergence labels.
  - Current evidence: `gh workflow list --all --json id,name,path,state`
    reports the workflow state as `disabled_manually`. That leaves paper-index
    validation as local manual commands only, not a runnable GitHub workflow.
  - Required result: either re-enable manual GitHub Actions and add/trigger the
    paper-index checks there, or update paper-index/development instructions so
    they explicitly name local manual validation as the sole current authority
    while the GitHub workflow remains disabled.
  - Status: README and development docs previously documented the disabled
    workflow state. Superseded by later workflow hardening that restored
    path-scoped automatic triggers and added a regression test for the covered
    docs/papers/TODO paths.

- [x] Add a paper index with roles and implementation status.
  - Evidence: downloaded papers include system papers, domain-result papers,
    and foundational algorithm papers, but only a subset is summarized in the
    README.
  - Required result: create a table with paper id, title, role, implemented
    status, and linked todo items.
  - Status: the paper index exists with 24 manifest-backed rows and local PDF
    coverage. Per-row TODO cross-links remain open separately below.

- [x] Separate AlphaEvolve requirements from other-paper inspirations.
  - Evidence: code comments cite non-AlphaEvolve papers for local choices, such
    as TF-IDF diversity, CausalEvolve heuristics, DeepEvolve arXiv search, and
    ThetaEvolve JSONL export.
  - Required result: document which features are necessary for AlphaEvolve
  fidelity and which are optional LibreEvolve extensions.

- [x] Turn the downloaded benchmark/result papers into explicit benchmark
  coverage decisions.
  - Evidence: `papers/download_manifest.csv` includes domain-result papers for
    sums/differences, autoconvolution, hardness of approximation, Bruhat
    intervals, global NLP optimization, multiagent learning, Ramsey numbers,
    Berczy combinatorics, bilateral trade, and related AlphaEvolve-style
    mathematical results.
  - Current evidence: `libreevolve/problems/examples/` contains
    `hello_world`, `sorting`, `circle_packing`, `matrix_multiplication`, and
    `workspace_math`.
  - Required result: for each downloaded domain paper, either add a
    corresponding problem fixture/benchmark, link it to an existing benchmark,
    or mark it as background-only in a paper index.

- [x] Add AlphaEvolve-paper benchmark parity targets.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` evaluates matrix
    multiplication, many constructive math problems, data-center scheduling,
    TPU arithmetic circuits, LLM-training kernels, and FlashAttention/GPU
    instruction optimization.
  - Current evidence: checked-in AlphaEvolve-adjacent examples include
    `circle_packing` and `matrix_multiplication`.
  - Required result: choose a small reproducible subset, such as matrix
    multiplication rank search, circle/kissing packing, and one scheduling or
    kernel microbenchmark, then add validators and expected run artifacts.

- [x] Classify AlphaEvolve application-result papers precisely in the index.
  - Paper-index evidence: several rows were labeled only as generic
    "domain-result", "agent/research workflow", or "agent architecture"
    context.
  - Paper evidence: `2509.18057__Hardness_of_Approximation.pdf`,
    `2603.08679__Bilateral_Trade.pdf`,
    `2602.16928__Multiagent_Learning.pdf`, `2601.21096__Magellan.pdf`,
    `2602.22425__ArchAgent.pdf`, and `2511.12916__Fault2Flow.pdf` all describe
    AlphaEvolve or AlphaEvolve-built application/result settings.
  - Required result: distinguish these rows from generic background-only
    papers while keeping implementation status clear as absent until local
    validators/runners exist.
  - Status: `papers/README.md` now labels those rows as AlphaEvolve
    application/result context and names the missing benchmark/runner family
    for each.

- [x] Clarify the global nonlinear-optimization paper title and role.
  - Paper-index evidence: the row for `2601.05943` used "Global NLP
    Optimization", which can read as natural-language-processing optimization
    rather than nonlinear programming/global optimization.
  - Paper evidence: `2601.05943__Global_NLP_Optimization.pdf` is titled
    "Global Optimization for Combinatorial Geometry Problems Revisited in the
    Era of LLMs" and compares off-the-shelf global nonlinear optimization
    solvers against AlphaEvolve-style results.
  - Required result: make the paper-index title/role distinguish nonlinear
    optimization benchmark comparison from NLP/LLM language tasks.
  - Status: `papers/README.md` now labels the row "Global Nonlinear
    Optimization" and marks it as an optimization benchmark comparator with no
    solver-comparison harness.

- [x] Clarify paper-index benchmark wording for circle packing.
  - Paper-index evidence: `papers/README.md` listed `circle_packing` under
    implemented benchmark coverage as an AlphaEvolve-adjacent packing benchmark.
  - Current evidence: the fixture validates fixed-26 unit-square feasibility
    and summed radii, while `tests/test_examples.py` only checks seed validity
    plus simple rejection cases. There are no repeated-seed runs, SOTA/target
    thresholds, saved construction artifact schemas, visual/JSON outputs, or
    benchmark reports.
  - Required result: describe `circle_packing` as an AlphaEvolve-adjacent smoke
    fixture until benchmark hardening is implemented.

## Paper-Inspired Feature Claims Needing Correction

- [x] Redact DeepEvolve-inspired retrieval provider errors before persistence.
  - Paper evidence: DeepEvolve-style retrieval is part of the prompt/debugging
    input, but provider diagnostics should not leak credentials or sensitive
    query context into experiment artifacts.
  - Previous gap: retrieval provider errors were treated as plain metadata.
  - Current evidence: a local proof configured `DeepResearchPlugin` with a
    custom provider raising
    `RuntimeError("provider failed api_key=sk-proj_secret_1234567890")`; the
    exact secret-like placeholder was stored in `retrieval_events[].error`.
  - Required result: add redacted/bounded retrieval-error telemetry for custom
    and default providers before using DeepEvolve-inspired retrieval metadata as
    paper-fidelity evidence.
  - Status: implemented. Custom retrieval exceptions and default arXiv network
    or parse errors now pass through shared secret-pattern redaction and
    truncation before they enter retrieval events or runtime summaries.

- [x] Correct paper-index wording for retrieval manifest provenance.
  - Paper-index evidence: `papers/README.md` says DeepEvolve-inspired status
    has "candidate history and run manifests" recording bounded retrieval
    summaries "with arXiv source IDs/URLs and summary hashes."
  - Current evidence: candidate history stores the detailed
    `metadata.plugin_context[].metadata.retrieval_events[].sources` entries,
    including IDs, URLs, and summary hashes. The run-level manifest summary
    produced by `_retrieval_manifest_summary()` intentionally stores compact
    event fields such as provider, query, status, result size, synthesis hash,
    and `source_count`, but not source IDs, URLs, or per-source summary hashes.
    A local proof with one custom source printed the candidate source record
    `{'id': 'paper-1', 'url': 'https://example.test/p1',
    'summary_sha256': 'abc'}` while the corresponding manifest summary
    contained only `source_count: 1` for source provenance.
  - Required result: either include bounded source IDs/URLs/summary hashes in
    `runtime.retrieval.event_summaries`, or revise `papers/README.md` to say
    that source details live in candidate history and manifests carry compact
    counts/hashes only.
  - Status: fixed in `papers/README.md`. The DeepEvolve row now states that
    source IDs/URLs and summary hashes live in candidate history, while run
    manifests carry compact retrieval event counts, status/source counts,
    result sizes, and synthesis hashes.

- [x] Validate paper-inspired plugin cadence parameters before hooks execute.
  - Paper evidence: DeepEvolve-style retrieval and ThetaEvolve-style
    test-time-training/export loops are long-running auxiliary processes whose
    cadence should be explicit, reproducible, and safe to resume.
  - Previous evidence: `DeepResearchPlugin(search_every=0)` and
    `TTTRLPlugin(train_every=0)` could be constructed directly. A local proof
    calling `on_generation_start(1, None)` and `on_generation_end(1, None)`,
    respectively, raised `ZeroDivisionError` from modulo checks instead of a
    configuration diagnostic.
  - Required result: validate cadence fields such as `search_every` and
    `train_every` as positive integers at construction or plugin-config
    preflight, persist the effective values in run provenance, and add tests
    that invalid paper-inspired plugin cadence fails before hook execution.
  - Status: validation is implemented for current built-ins.
    `DeepResearchPlugin.__init__()` rejects invalid `search_every` values and
    `TTTRLPlugin.__init__()` rejects invalid `train_every` values; tests cover
    zero, negative, float, and boolean inputs. Effective cadence/config
    provenance for future plugin configuration remains part of the broader
    plugin registry/config/provenance work.

- [x] Clarify DeepEvolve paper-index wording around cross-file editing.
  - Paper-index evidence: `papers/README.md` says the DeepEvolve-inspired
    status has "no ranking provenance, full payloads, cross-file editing, or
    systematic debugging loop."
  - Current evidence: the core candidate system now supports multi-file
    workspace mutations, including edits, creates, deletes, moves, and
    primary-file reassignment. What remains missing is DeepEvolve-specific
    cross-file editing as part of a retrieval/debug/hypothesis loop, not
    platform-level cross-file mutation support.
  - Required result: update `papers/README.md` so the DeepEvolve row says
    "no DeepEvolve-style cross-file debugging/editing loop" or equivalent,
    avoiding a contradiction with current workspace-candidate support.
  - Status: `papers/README.md` now describes the missing behavior as
    "DeepEvolve-style cross-file debugging/editing loop" and also states that
    the current retrieval query policy is generic rather than problem-aware.

- [x] Document structured custom retrieval provider outputs.
  - Paper/docs evidence: DeepEvolve-style retrieval provenance depends on
    knowing whether a context source is plain text or structured metadata.
  - Current evidence: `DeepResearchPlugin` accepts custom `search_fn` results
    that are strings or dictionaries, but `docs/plugins.md` described only
    `search_fn(query) -> str | None`.
  - Required result: update plugin docs so structured custom retrieval results
    are not mistaken for unsupported behavior, while the broader DeepEvolve
    replay/ranking/full-payload gaps remain open.
  - Status: `docs/plugins.md` now documents `str | dict | None` custom
    providers and names the supported bounded provenance fields.

- [x] Correct paper-index wording for the MAP-Elites performance axis.
  - Paper-index evidence: `papers/README.md` currently says the local
    MAP-Elites implementation is a fixed 3D archive over "normalized fitness,
    primary-file code length, and primary-file TF-IDF diversity."
  - Current evidence: `MAPElites._cell_with_descriptors()` computes the
    `performance` descriptor from `_selection_score(program)`, not directly
    from `program.fitness`. A local proof inserted a program with
    `fitness=0.2` and `metadata.selection_score=0.9`; the archive event
    recorded `selection_score == 0.9` and
    `descriptors.performance == 0.9`.
  - Required result: revise `papers/README.md` and any matching docs to say
    the performance axis uses the current archive selection score, falling
    back to top-level fitness only when no finite selection score is present;
    keep the broader open item for problem-defined MAP-Elites descriptors.
  - Status: `papers/README.md` now describes the local MAP-Elites archive as
    using archive selection score, falling back to fitness, plus primary-file
    code length and primary-file TF-IDF diversity.

- [x] Document the MAP-Elites boundary as fixed local quality-diversity search.
  - Paper evidence: canonical MAP-Elites illuminates a behavior space chosen
    for the problem domain.
  - Current evidence: `MAPElites`'s docstring, README, architecture docs,
    roadmap, code todo, and paper index describe LibreEvolve's archive as a
    fixed local 3D heuristic over archive selection score, primary-file code
    length, and primary-file TF-IDF diversity, not a canonical
    problem-defined behavior-descriptor implementation.
  - Required result: keep the documentation boundary explicit while the
    remaining descriptor implementation work stays open.

- [x] Gate model-routing rewards on candidate validity/admission semantics.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6,
    describes using LLMs to propose useful programs under compute budgets; a
    model-routing reward should reflect proposals that pass the evaluator and
    contribute to search, not rejected artifacts.
  - Current status: LibreEvolve now rewards mutation backends only after
    archive admission. Invalid, below-threshold, feedback-discarded, and other
    non-admitted candidates receive zero backend reward; admitted valid
    candidates receive non-negative improvement over the selected parent.
  - Required result: define model-routing reward around evaluator-valid,
    admitted, or explicitly penalized outcomes; record no-reward/penalty
    provenance for invalid, feedback-discarded, below-threshold, and
    plugin-adjusted candidates; test the policy before comparing scheduler
    behavior to AlphaEvolve-style model selection.
  - Status: implemented with `metadata.backend_reward` provenance and tests for
    admitted valid improvement, plugin-raised invalid candidates, and
    LLM-feedback-discarded candidates.

- [x] Document the UCB1 boundary as heuristic rather than canonical.
  - Paper evidence: the UCB1 paper provides regret analysis under assumptions
    that LibreEvolve's backend router does not currently satisfy.
  - Current evidence: `LLMEnsemble`'s docstring, `docs/backends.md`,
    `README.md`, and `papers/README.md` all describe the backend router as a
    UCB-style heuristic or inspiration over admission-gated valid fitness
    improvements, not a canonical regret-analyzed UCB1 implementation.
  - Required result: keep the documentation boundary explicit while the
    remaining canonicalization work stays open under the bounded-reward policy
    todo.

- [x] Enforce boolean config switches for paper-inspired optional LLM paths.
  - Paper evidence: AlphaEvolve-style critique, feedback, and meta-prompt
    components are explicit configured system behaviors, not accidental truthy
    string branches.
  - Current evidence: `Config.validate()` now rejects non-boolean
    `meta_prompt_evolution` and `critique_enabled`, non-string
    `critique_prompt`, non-integer `seed`, non-path `log_dir`, and unsafe
    `problem_name` / `--run-name` values. Tests cover direct `Config`
    construction, path-like `log_dir` normalization, a quoted YAML boolean
    string, and unsafe CLI run-name rejection before `evolve()`.
  - Status: implemented for scalar, boolean, and prompt-text config fields.
    Plugin-specific config schemas, model/API capability validation, stage
    context metadata validation remain separate open gaps.

- [x] Tighten inline paper-source comments so they do not imply faithful
  implementations.
  - Evidence: source comments in the diff engine, evaluator, loop, database,
    island model, MAP-Elites, and modular plugin cited paper systems in ways
    that could be read as direct implementations.
  - Status: inline comments now use "inspired by" language or state the local
    limitation directly; the larger implementation gaps remain tracked in the
    paper-specific items above.
  - Required result: keep code comments aligned with the actual behavior, not
    just README/docs marketing language.

- [x] Re-audit backend-selection source comments for MadEvolve implication.
  - Paper evidence: `2602.15951__MadEvolve.pdf` is tracked as domain evolution
    inspiration, while LibreEvolve has no free-parameter optimization,
    innovation report, or MadEvolve-style parameter-function summary.
  - Current evidence: `libreevolve/llm/ensemble.py` still says the UCB-style
    router is "applied to LLM selection per MadEvolve", even though README,
    docs, and the paper index describe the router as a heuristic
    AlphaEvolve/MadEvolve-adjacent scheduling concept rather than a faithful
    MadEvolve implementation.
  - Required result: either rewrite that source comment to "inspired by" /
    "adjacent to" wording, or implement and document the specific MadEvolve
    behavior being claimed.
  - Status: `libreevolve/llm/ensemble.py` now describes the scheduler as
    adjacent code-evolution scheduling inspiration and explicitly says it is
    not a MadEvolve reproduction.

- [x] Decide MadEvolve remains background context unless implemented.
  - Paper evidence: `2602.15951__MadEvolve.pdf` emphasizes free parameters,
    parameter optimization, hybrid population management, LLM ensemble
    strategies, and automated report generation comparing input and evolved
    algorithms.
  - Status: README and the paper index now classify MadEvolve as background
    context rather than a LibreEvolve implementation claim. The code comment
    in `LLMEnsemble` also says the scheduler is not a MadEvolve reproduction.
  - Verification: repository-wide search finds no remaining implementation
    claim for MadEvolve free-parameter optimization, generated innovation
    reports, or parameter-function summaries.

- [x] Keep ImprovEvolve-inspired modular guidance explicitly paper-limited.
  - Paper evidence: `2602.10233__ImprovEvolve.pdf` evolves a class/interface
    with `generate_config`, `improve`, and `perturb`, then approaches optima by
    scheduled basin-hopping-style application of `improve()` and `perturb()`.
  - Status: README, plugin docs, architecture docs, and the paper index now
    describe the `modular` plugin as static prompt guidance. They explicitly
    state that LibreEvolve does not select, execute, or log a
    `generate_config`/`improve`/`perturb` operation.
  - Remaining implementation gap: a real ImprovEvolve-style interface,
    iterative improve/perturb loop, perturbation schedule, operation
    attribution, and benchmark-specific search loop are not implemented.
    Those remain outside current claims unless the plugin is promoted beyond
    static prompt-only guidance.
  - Verification: repository-wide search shows ImprovEvolve references are
    scoped to static prompt guidance or not-paper-complete wording; modular
    plugin tests cover the static guidance text.

- [x] Make YAML configuration key validation deterministic.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.3, and 2.6.
  - Requirement: task setup should reject malformed or unsupported
    configuration with actionable diagnostics before the autonomous run starts.
  - Current evidence: `config.yaml` duplicate keys were rejected, but top-level
    key types were not validated before unknown-key sorting. A local proof with
    mixed YAML keys `1: bad` and `unknown: bad` caused `_build_config()` to
    raise raw `TypeError: '<' not supported between instances of 'str' and
    'int'`; the CLI printed no normal configuration diagnostic.
  - Required result: require string top-level config keys, keep duplicate-key
    detection, make unknown-key reporting deterministic for all YAML scalar
    key types, and update paper/runtime docs so configuration validation is not
    overstated.
  - Status: implemented. `_build_config()` now requires string top-level YAML
    config keys before unknown-key sorting; duplicate-key validation remains in
    `safe_load_unique()`, and focused CLI tests cover deterministic diagnostics
    for non-string-only, mixed non-string/unknown string, duplicate, and valid
    unknown string key cases.

- [x] Make setup validation ordering side-effect safe.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4,
    treats the task/evaluator configuration as experiment setup. Invalid setup
    choices should be rejected before the system executes avoidable user code
    outside the evaluation boundary.
  - Current gap: CLI plugin alias validation ran after evaluator-contract
    preflight. Because evaluator preflight imports `validate.py` in the main
    process, an invalid plugin alias did not prevent validator import-time side
    effects.
  - Current evidence: a local `CliRunner` proof used `--plugins
    missing_plugin` and a validator module that wrote a marker file at import
    time. The CLI exited with `Unknown plugin`, but the marker existed.
  - Required result: order pure configuration validation before task-code
    import preflight, or execute validator preflight in the same constrained
    subprocess model as evaluation; keep paper-index setup/preflight claims
    scoped until invalid plugin/provider/config inputs cannot trigger
    validator import side effects first.
  - Status: implemented for plugin aliases. The CLI now validates configured
    plugin names before evaluator contract preflight imports `validate.py`, and
    the regression test proves an unknown plugin exits before validator
    import-time marker creation.

- [x] Make run identity/path labels reject every control character.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.6, emphasizes
    reproducible experiments with durable metadata. Run identity labels should
    be safe to persist in manifests, paths, logs, and future resume indexes.
  - Current gap: the current run-name component validator excluded C0 controls
    but not ASCII DEL. A local proof accepted
    `Config(problem_name="bad\x7fname")`, created the run directory, and wrote
    that value into `manifest.json.config.problem_name`.
  - Required result: define a complete control-character policy for run names
    and path labels, enforce it at config/CLI/resume boundaries, and keep
    paper-index reproducibility/provenance claims scoped until unsafe run
    labels cannot enter persisted experiment metadata.
  - Status: implemented for ASCII run-name controls. `Config.problem_name` and
    CLI `--run-name` now reject DEL as well as C0 controls before run artifacts
    are created.

- [x] Make configured log-root provenance secret-safe.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.6, emphasizes
    reproducible experiments with durable metadata and comparable run
    artifacts.
  - Requirement: experiment manifests should enable reproducible comparison
    without leaking private local directory labels or credential-like path
    components.
  - Current gap: LibreEvolve persisted `Config.log_dir` verbatim in
    `manifest.json.config.log_dir`.
  - Current evidence: a local proof used
    `log_dir=<tmp>/api_key=sk-proj_LOGDIRSECRET_1234567890/runs`; manifest
    creation succeeded and the raw secret-like folder name was retained in the
    effective config block.
  - Required result: define a redacted/hash/project-relative/opt-in raw policy
    for log-root persistence, document the data-retention boundary in
    paper/runtime docs, and test absolute paths, relative paths, secret-like
    components, and resume manifests.
  - Status: implemented for startup manifests. Absolute configured log roots
    are represented by a stable placeholder and SHA-256 metadata instead of raw
    local paths; tests cover absolute, relative, and secret-like log roots.

- [x] Make run/candidate Unicode format-control labels safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: run and candidate labels should be auditable, reproducible
    provenance fields for codebase evolution and future resume.
  - Current gap: LibreEvolve rejected many path hazards but accepted Unicode
    format controls that can be invisible or alter display order. A local proof
    used U+202E in `problem_name="rtl\u202egnp"` and candidate file
    `src/rtl\u202egnp.py`.
  - Status: implemented for run names and candidate paths. Unicode format
    controls are rejected at config and candidate-path normalization
    boundaries, and docs distinguish ordinary non-ASCII names from
    bidi/invisible controls.

- [x] Make metric/stage Unicode format-control labels safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, 2.5, and 2.6.
  - Requirement: metric identifiers and evaluation-stage labels should be
    auditable, reproducible provenance fields for task contracts and evaluator
    cascades.
  - Status: implemented for Unicode format controls. The problem loader rejects
    Unicode `Cf` characters in metric names, config validation rejects them in
    configured stage names, and tests cover right-to-left override and
    zero-width joiner.

- [x] Make plugin/feedback Unicode format-control labels safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, 2.5, and 2.6.
  - Requirement: configured extension identifiers and LLM-review labels should
    be auditable, reproducible provenance fields for experiment configuration
    and evaluator feedback.
  - Status: implemented for Unicode format controls. Config validation rejects
    Unicode `Cf` characters in configured plugin aliases and LLM feedback
    `name` / `metric` labels; tests cover right-to-left override and
    zero-width joiner.

- [x] Make artifact/context Unicode format-control labels safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: artifact selector and context-selection pattern labels should
    be auditable, reproducible provenance fields for codebase evolution and
    future resume.
  - Status: implemented for Unicode format controls. Artifact include/exclude
    globs and context manifest include/exclude patterns now reject Unicode `Cf`
    characters; tests cover right-to-left override, zero-width joiner, and
    ordinary non-ASCII path text.

- [x] Make plugin-emitted metadata labels Unicode format-control safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: plugin-provided context and artifact metadata labels should be
    auditable, reproducible provenance fields for prompts, manifests, and
    future resume.
  - Status: implemented for metadata keys. Plugin prompt-context metadata and
    run-artifact metadata reject Unicode `Cf` controls recursively in
    dictionary keys while ordinary non-ASCII key text remains supported.

- [x] Make validator environment allowlist provenance canonical.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: evaluator-environment provenance should identify the effective
    benchmark/runtime inputs intentionally exposed to validators without raw
    ambiguous labels.
  - Status: implemented with portable manifest-safe labels. Validator
    allowlists are stripped, uppercased, deduplicated, and validated before
    config manifest persistence or direct evaluator use; evaluator metadata
    records canonical allowlist names and provided environment keys without
    values.

- [x] Define paper-faithful metric identifier safety.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: metric identifiers are part of the task/evaluator contract and
    generated-program database, so they should be stable, comparable, and safe
    to persist/render.
  - Status: implemented for problem schemas. `metrics.yaml` metric names now
    use a safe ASCII identifier grammar with optional dotted namespaces and
    reject control characters, whitespace, non-ASCII names, and reserved
    `is_valid`.

- [x] Treat problem metric schemas as validated runtime objects.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: AlphaEvolve-style tasks define evaluator metrics and program
    selection objectives coherently across the evolutionary loop, database, and
    future resumed workers.
  - Status: implemented for metric schemas. Direct `Problem(...)` construction
    now applies the same metric-schema normalizer as `load_problem()`, rejects
    duplicate/conflicting schemas, and normalizes effective primary metadata
    before evaluators or databases can consume the object.

- [x] Reject unsupported async and generator evaluator contracts before
  paper-level task setup claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: evaluator code is part of the task setup and must execute
    under a clear contract so scores and validity reflect the intended
    objective.
  - Status: implemented for the current synchronous runner. Default and staged
    validator preflight now reject coroutine, generator, and async-generator
    `evaluate` functions before manifest/history mutation; tests cover direct
    preflight and CLI overwrite-preflight behavior.

- [x] Reject evaluator signatures outside the fixed task contract before
  paper-level setup claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: evaluator code is part of the task definition and should have
    a stable call contract so objective scoring, provenance, and replay are
    unambiguous.
  - Status: default and staged validator preflight now accepts only the fixed
    one-, two-, and three-argument `evaluate` forms and rejects variadic,
    keyword-only, and extra-parameter signatures.

- [x] Make evaluator-contract preflight a core runtime invariant.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: evaluator contracts are part of the task setup, so invalid
    contracts should fail before an experiment begins regardless of whether the
    run is launched through the CLI or library API.
  - Status: direct `evolve()` now enforces default/staged evaluator-contract
    preflight before `ProgramDatabase` cleanup or manifest writes, matching the
    CLI artifact-preservation boundary for evaluator contracts.

- [x] Validate default evaluator and required problem-file identities during
  task loading.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.2, 2.4, and 2.6.
  - Requirement: task description, metric schema, evaluator entrypoint, and
    prompt-context manifest are part of the reproducible task package and
    should be validated as problem files before a run begins.
  - Status: problem loading now rejects non-regular or linked
    `task_description.txt`, `metrics.yaml`, `validate.py`, and context manifest
    paths before content reads or `Problem` construction; loader and CLI tests
    cover directory-shaped inputs.

- [x] Treat metric and context schema keys as validated task-setup fields.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.2, 2.4, and 2.6.
  - Requirement: task metric definitions and prompt-context configuration are
    reproducible setup inputs and should fail deterministically on unsupported
    or malformed keys.
  - Status: `metrics.yaml` now allows only the top-level `metrics` field, and
    metric/context mappings reject non-string keys before unsupported-field
    sorting. Loader, CLI, and direct `Problem` tests cover the diagnostics.

- [x] Validate direct task objects at the evolution boundary before treating
  setup as AlphaEvolve-style.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.2, and 2.4.
  - Requirement: the task API must define objective text and initial code
    before the evolutionary loop starts.
  - Status: direct `evolve()` calls now reject empty task descriptions and
    missing seed programs/workspaces before database/manifest writes; evaluator
    path validity is covered by the direct runtime preflight boundary.

- [x] Validate evolve-block markers introduced by workspace file creation and
  across full resulting workspaces.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: codebase candidates should preserve task-defined
    skeleton/evolvable-region boundaries across the entire candidate, including
    generated or moved files.
  - Status: workspace mutation now validates all resulting files before
    success, including newly created files, untouched siblings, and topology
    moves; direct `Program` construction rejects malformed marker layouts before
    archive/log/database use.

- [x] Fail closed when evolve-block marker parsing is hidden by Python
  tokenization errors.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.3.
  - Requirement: marker-based skeleton preservation must be reliable whenever a
    task uses evolve-block boundaries.
  - Status: marker validation now returns `tokenize_error` when raw marker
    lines are present but Python tokenization fails, preventing the candidate
    from being treated as unmarked. Tests preserve the valid string/docstring
    literal behavior.

- [x] Make empty candidate/program records explicit in codebase-candidate
  fidelity.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: codebase candidate records should be internally coherent when
    persisted or replayed; a declared primary file should exist in the
    candidate file set or the record should be marked as legacy/single-string.
  - Status: empty `Program` records now canonicalize to a file-set workspace
    with an empty default primary file before logging or archive use. Tests
    cover direct construction, persistence, show, and workspace access.

- [x] Enforce candidate primary-file path safety for empty legacy records.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: codebase candidate metadata should not contain path values
    that would be unsafe or invalid when replayed, materialized, or inspected.
  - Status: `Program.__post_init__()` validates `primary_file` through
    `CandidateWorkspace` even when code/files are empty, preventing unsafe
    primary paths from being persisted.

- [x] Validate objective-schema provenance at manifest construction boundaries.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: the optimization objective, metric directions, bounds, and
    primary score choice must be durable and trustworthy for analysis,
    comparison, and future resumed workers.
  - Status: `ProgramDatabase` now requires objective-schema provenance and
    validates it with the same metric-schema rules used by `Problem`; invalid
    directions, reserved names, bad primary flags, mismatched bounds, and wrong
    metric counts fail before manifest writes.

- [x] Validate archive admission policy thresholds before database mutation.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: archive admission policy should be a typed, finite experiment
    control whose recorded value can be replayed and compared.
  - Status: `ProgramDatabase.admit()` now enforces finite non-boolean numeric
    threshold values before archive mutation, preventing threshold metadata
    from creating accepted-but-unlogged candidates.

- [x] Make failed-trial evaluation summaries schema-tolerant.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figures 1-2 and Sections 2.2 and
    2.6.
  - Requirement: AlphaEvolve-style failed-trial memory should preserve invalid
    candidate diagnostics rather than dropping them when an evaluation payload
    is malformed.
  - Status: generated and seed failure summaries now tolerate malformed
    `evaluation.stages` shapes and persist compact `stages_diagnostic`
    metadata in `failure_history.jsonl` instead of crashing before failed-trial
    persistence.

- [x] Preserve archive rejection reasons in generated failure memory.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figures 1-2 and Sections 2.2 and
    2.6.
  - Requirement: the program database should retain enough information about
    failed and rejected trials for later sampling, prompt context, and analysis.
  - Status: generated failure records now carry archive admission provenance,
    including rejection reason and threshold metadata, aligning generated
    failed-trial memory with rejected seed records.

- [x] Make history inspection expose full workspace candidates.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: AlphaEvolve evolves code artifacts in a repository context and
    uses the program database as a substrate for inspecting, resurfacing, and
    comparing candidate ideas. A codebase-candidate record must therefore be
    inspectable as more than its primary file text.
  - Status: `libreevolve show` now renders logged workspace candidates with a
    primary-file marker, file manifest, and every file's content when a history
    row contains `files` plus `primary_file`. Tests prove non-primary helper
    files and contents are visible.

- [x] Make history inspection fail-fast for malformed displayed fields.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: a durable evolutionary database should support trustworthy
    inspection; malformed records should not be presented as valid best
    programs.
  - Status: `libreevolve show` now validates the selected display record before
    emitting the best-fitness line, metrics, archive summary, or program text.
    Tests prove malformed legacy and modern rows fail with file/line
    diagnostics instead of printing bad generation values, missing code, list
    code, malformed metrics, or malformed archive summary fields.

- [x] Define mixed-schema history inspection before claiming durable database
  compatibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: a long-running program database should remain inspectable
    across schema evolution and partial migrations.
  - Status: the current compact inspector does not migrate or partition mixed
    histories; it explicitly rejects them. `libreevolve show` reports the
    schema-mixing line plus the first legacy and archive-admission row lines,
    while preserving legacy-only and current-only inspection semantics.

- [x] Make metric-leader ordering primary-aware in the multi-score heuristic.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: programs that excel under different criteria should be
    resurfaced intentionally, especially when the prompt budget is smaller than
    the metric count.
  - Status: metric-leader parent/inspiration sampling now orders leaders by
    declared primary metric first, then remaining configured metric order, then
    extra normalized metrics alphabetically. This closes the alphabetical
    ordering bug while leaving Pareto/frontier search as an explicit open gap.

- [x] Close direct MAP-Elites validity bypass before treating archive
  admission as validity-gated.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the archive/database substrate should not resurface invalid
    candidates through supported insertion paths.
  - Status: direct MAP-Elites insertion now rejects candidates unless
    `evaluation.is_valid is True`, and public database insertion inherits that
    guard. Tests prove invalid direct inserts do not mutate archive state.

- [x] Validate direct MAP-Elites archive parameters before archive-state
  claims are treated as robust.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: archive geometry, elite retention, and performance
    normalization should be well-defined for direct construction.
  - Status: direct `MAPElites` construction now rejects invalid bins,
    elite-archive sizes, and performance bounds before candidate insertion.
    Future resume/restore validation remains part of broader resumability work.

- [x] Make full-workspace best export durable before counting it as
  AlphaEvolve-grade evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: recoverable best programs/codebases should not be partial
    post-processing artifacts.
  - Status: the CLI now stages `best.py` and `best_workspace/` under temporary
    paths, swaps the pair into place only after materialization succeeds, and
    rolls back to the previous pair on replacement failure. Tests cover
    materialization failure preserving the previous export. Manifest-backed
    export hashes and failure records remain separate active run-evidence work.

- [x] Make persisted database JSON records round-trip safe, not only finite.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: the evolutionary database should preserve candidate metrics,
    metadata, feedback, and provenance as structured experiment evidence for
    future selection, analysis, and replay.
  - Status: the shared strict JSON writer now requires string object keys
    recursively, rejects lossy Python key coercion before writes, surfaces
    path-aware diagnostics, and applies to manifests, histories, prompt logs,
    plugin outputs, GRPO exports, and quarantine records.

- [x] Make invalid-record quarantine durable against hostile representations.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the evolutionary database should retain enough structured
    evidence to diagnose malformed or rejected candidates during long runs.
  - Status: quarantine diagnostics now use bounded, redacted,
    exception-safe record snapshots and preserve the original strict-JSON
    serialization error plus a snapshot-rendering diagnostic when needed.

- [x] Make malformed-record diagnostics robust to cyclic objects.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: rejected or malformed records should remain diagnosable in the
    evolutionary database instead of surfacing as unrelated runtime crashes.
  - Status: strict JSON preflight detects circular dict/list/tuple references
    and excessive nesting before serialization; manifest writes preserve the
    previous file, and JSONL append failures can write quarantine diagnostics.

- [x] Preserve which initial seed artifact produced each baseline program.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: the evolutionary database should make evaluated programs and
    their feedback traceable enough to reproduce and analyze the search,
    including baseline solutions evaluated before mutation begins.
  - Status: loaded seed files and directories now persist safe relative source
    provenance in seed history rows, seed failure rows, and
    `manifest.problem.seed_sources`, so duplicate baseline workspaces can be
    audited without relying on generated UUIDs or archive island placement.

- [x] Make materialized codebase candidates exact snapshots.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: full-codebase candidates should be replayable/exportable as the
    exact file set selected by evolution, without stale files from earlier
    candidates influencing validation or inspection.
  - Status: candidate workspace materialization now preflights paths and
    collisions before touching the target, rejects link/junction roots or
    children, removes stale non-link entries under a normal target root, and
    writes only the current candidate file set. Tests cover non-empty target
    reuse and preflight-failure preservation.

- [x] Make SEARCH/REPLACE target identity unambiguous.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Figure 3.
  - Requirement: SEARCH/REPLACE edits should identify the intended code region
    to replace while preserving the rest of the program or codebase.
  - Status: duplicate SEARCH matches now produce `ambiguous_search_match`
    before any partial edit is applied. The behavior is covered for whole-file
    candidates, a single evolve block with repeated text, and multiple evolve
    blocks with identical SEARCH text.

- [x] Make duplicate primary topology commands unambiguous.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: codebase candidates should have one accountable primary
    compatibility view for prompts, validators, and best-artifact export.
  - Status: workspace mutations now reject multiple `PRIMARY` command sections
    before applying topology changes, rather than letting a later section
    silently override earlier primary intent.

- [x] Make topology command bodies accountable.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: proposed codebase mutations should not silently discard parts
    of an LLM proposal that look like edit content.
  - Status: `DELETE`, `MOVE`/`RENAME`, and `PRIMARY` command sections now fail
    with `unexpected_command_body` when body text is present, preserving
    no-partial-apply behavior for invalid topology mutations.

- [x] Make primary topology reassignment coherent across same-mutation edits.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: codebase mutations should define one accountable final
    primary compatibility view for prompts, validation, and artifact export.
  - Status: `PRIMARY` commands are validated after same-mutation file edits,
    deletes, and moves, so targets created by the same mutation are
    order-independent. Deleting the current primary file now requires an
    explicit replacement primary instead of falling back to sorted path order.

- [x] Document sampling strategy configuration as reproducibility evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: parent and inspiration sampling from the evolutionary
    database are experiment controls and should be auditable.
  - Status: `docs/configuration.md` documents `parent_selection_strategy` and
    `inspiration_strategy`; `README.md`, CLI help, manifests, and config
    validation expose the same controls.
  - Verification: `tests/test_agents_docs.py` protects configuration-doc
    coverage for the sampling strategy fields and allowed policy names.

- [x] Treat plugin metadata value validation as implemented plugin-provenance
  hardening.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: plugin-provided context and artifact metadata used as
    experiment evidence should be attributable, display-safe, and JSON-safe.
  - Status: plugin metadata values now reject Unicode format controls and
    non-JSON-safe objects, require finite numeric values, bound string length,
    and redact secret-like strings before history or manifest persistence.
  - Verification: focused loop tests cover value validation for prompt-context
    and run-artifact metadata.

- [x] Treat malformed nested config diagnostics as implemented setup
  hardening.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: malformed evaluator, backend, and feedback configuration
    should fail with structured setup diagnostics, not unstructured Python
    errors.
  - Status: nested config mappings now reject non-string keys before
    unsupported-field sorting and report section paths for eval stages,
    backends, and LLM feedback graders.
  - Verification: focused direct `Config` tests and CLI `config.yaml` tests
    cover the malformed mixed-key cases.

- [x] Make candidate path canonicalization auditable for codebase evolution.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: codebase candidates should have stable file identities so
    generated edits, evaluation artifacts, lineage, and future resume state can
    be interpreted unambiguously.
  - Status: LibreEvolve now rejects ambiguous candidate path spellings instead
    of dropping empty or `.` path components. Full-mode generated file
    sections, topology move targets, and primary-file commands return
    `unsafe_path` diagnostics for ambiguous raw paths, and docs no longer
    imply those spellings are silently canonicalized.
  - Verification: focused candidate tests cover direct path normalization and
    mutation-envelope diagnostics.

- [x] Define hidden-file policy for generated codebase candidates.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: evolved codebase candidates should have explicit, auditable
    file-set semantics and should not silently introduce secret-bearing or
    repository-control artifacts into prompts, histories, materialized
    workspaces, or exported artifacts.
  - Status: generated dot-prefixed candidate paths are denied through the
    shared candidate path normalizer. Direct workspaces and workspace mutation
    envelopes reject `.env`, `.git/config`, and nested hidden files with
    `unsafe_path` diagnostics before evaluation/export, and the paper index
    now scopes the implemented codebase-candidate claim accordingly.
  - Verification: focused candidate tests cover direct hidden path rejection
    and file-section, move-target, and primary-target diagnostics.

- [x] Add path-length validation to codebase-candidate fidelity.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: a stored codebase candidate should be a reproducible,
    materializable file set for evaluation, archival, comparison, and future
    resume.
  - Status: candidate path normalization now rejects path components longer
    than 255 characters and normalized relative paths longer than 1024
    characters. Overlong generated files, move targets, and primary targets
    fail with `unsafe_path` diagnostics before evaluation or best export, and
    the paper index now includes overlong-path rejection in the implemented
    AlphaEvolve-alignment status.
  - Verification: focused candidate tests cover direct and mutation-envelope
    length diagnostics.

- [x] Reject unknown full-block targets in mutation envelopes.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: evolved code/codebases should preserve the user's intended
    task representation and mutation mode without silently dropping parts of an
    LLM proposal.
  - Status: full-block replacement now rejects unknown named block sections
    before applying any known section, and the paper index includes unknown
    full-block target rejection in the implemented AlphaEvolve-alignment
    status.
  - Verification: focused candidate tests cover all-unknown and mixed
    known/unknown block-section responses.

- [x] Support empty files as first-class codebase-candidate members.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: whole-codebase evolution should preserve candidate file-set
    membership independently from file content.
  - Status: full-mode workspace mutation now creates missing files even when
    the parsed replacement body is empty. Empty and blank file-section bodies
    create empty files; existing empty files still report a scoped no-change
    diagnostic.
    The paper index now lists empty-file creation through full-mode file
    sections as implemented.
  - Verification: focused candidate tests cover creation and no-op cases.

- [x] Treat absent package metadata as a typed provenance state.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: AlphaEvolve-style experiment records should distinguish
    missing local package metadata from parsed or degraded metadata states.
  - Status: missing `pyproject.toml` files now produce
    `package.pyproject.status: missing` with `path: pyproject.toml`, and the
    paper index now describes typed missing/invalid `pyproject.toml`
    provenance as implemented.
  - Verification: focused provenance tests cover missing package metadata and
    existing degraded metadata states.

- [x] Treat semantically invalid package metadata as degraded environment
  provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: AlphaEvolve-style experiment evidence should identify
    malformed package metadata instead of turning it into plausible dependency
    rows.
  - Status: dependency and build-system requirement schemas are now validated
    with PEP 508 parsing. Invalid schemas record
    `package.pyproject.status: invalid_pyproject_schema` with hash/byte
    evidence and diagnostics, and the paper index reflects the implemented
    invalid-schema provenance state.
  - Verification: focused provenance tests cover invalid dependency/build
    metadata and valid private-source dependency redaction.

- [x] Anchor Git provenance to the hashed implementation source root.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: experiment manifests should identify the implementation
    source state that produced the run, not an unrelated invocation directory.
  - Status: run manifests now derive Git metadata from the same
    `libreevolve/` source root used for source-tree hashing, and docs describe
    that interpretation. The broader runtime/provenance paper todo remains
    open for dotenv precedence, direct-runtime provider preflight,
    evaluator-helper policy, resume, and related gaps.
  - Verification: a focused loop test covers source-root Git lookup while
    launched from a non-repo temporary working directory.

- [x] Make dirty Git status provenance secret-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: experiment manifests should support reproducible comparison
    while respecting credential-safety boundaries.
  - Status: Git dirty status entries are now redacted for common secret
    patterns before persistence and paired with SHA-256 hashes of the original
    raw porcelain lines. Runtime docs distinguish this completed Git-status
    policy from the still-open source/problem tree path-retention gap.
  - Verification: a focused provenance test covers a secret-like untracked
    path together with ordinary modified/renamed Git status entries.

- [x] Make source/problem provenance paths secret-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: source/problem provenance should identify experiment inputs
    without forcing raw credential-bearing filenames into durable manifests.
  - Status: tree provenance now redacts common secret patterns in included and
    skipped source/problem paths, adding `path_hash` and `path_redacted` when
    redaction changes the visible path.
  - Verification: focused provenance tests cover secret-like nested included
    files and skipped generated roots.

- [x] Make skipped-source provenance digest semantics explicit.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: run manifests should support reproducible comparison of the
    effective task/source package and the policy for deliberately skipped
    files.
  - Status: LibreEvolve emits `tree_hash_scope: included_files`,
    `skipped_hash_scope: skipped_diagnostic_records_v2`, and
    `provenance_hash_scope: included_files_and_skipped_diagnostics_v2`.
    Excluded/skipped contents are not hashed, but full skipped diagnostic
    records and exclusion-directory policy are included in the combined
    provenance digest.
  - Verification: focused provenance tests prove the manifest digest semantics
    for excluded cache directories and changed skipped-file bytes.

- [x] Make plugin module provenance paths secret-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: experiment manifests should identify paper-inspired extension
    code without forcing raw local checkout, site-packages, or private custom
    plugin paths into durable artifacts.
  - Status: plugin provenance now stores project-local module paths relative
    to the repository and external module paths as basename-only
    `<external>/...` records. Raw resolved paths are represented by
    `path_hash`, and `path_scope` distinguishes `project_relative` from
    `external_file_name`.
  - Verification: focused provenance tests cover built-in/project-local,
    external secret-like, and no-file plugin modules.

- [x] Make persisted evaluator metadata paths secret-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, 2.5, and 2.6.
  - Requirement: evaluator provenance should make candidate scores
    reproducible without leaking raw local workspace paths into every
    evolutionary database row.
  - Status: `evaluation.metadata.validate_path` is now problem-relative and
    paired with `validate_path_hash`, `validate_path_scope`, and
    `validate_path_redacted`. Nested configured-stage and retry-attempt
    metadata use the same path display policy.
  - Verification: focused evaluator tests cover ordinary, configured-stage,
    absolute configured-stage, and secret-like problem paths.

- [x] Make active output-root provenance exclusion independent of process cwd.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Requirement: run provenance should identify problem inputs and generated
    outputs from explicit experiment paths, not from the incidental directory
    where the process was launched.
  - Status: relative generated roots are resolved from the problem root, and
    `evolve()` passes the effective run directory as an absolute generated
    root for manifest provenance.
  - Verification: focused provenance and loop tests cover cwd-independent
    helper behavior and the existing runtime path.

- [x] Bound or qualify source/problem provenance hashing cost.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: experiment provenance should identify run inputs without
    turning startup into an unbounded, unaudited scan over large source/problem
    files.
  - Status: source/problem provenance now records a `max_file_bytes` cap,
    skips over-limit regular files before reading them, records read failures
    as skipped diagnostics, and hashes binary files under the cap as raw bytes.
  - Verification: focused provenance tests cover over-limit files, binary
    files, read failures, and the manifest cap field.

- [x] Bound or qualify plugin module provenance hashing cost.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: plugin provenance should identify experiment extension code
    without making manifest startup an unbounded read of arbitrary plugin
    module files.
  - Status: plugin module provenance now records `max_file_bytes`, skips
    over-limit module files before hashing, records read failures with redacted
    diagnostics, and distinguishes successful, missing/no-file, and skipped
    module states.
  - Verification: focused provenance tests cover project-local, external,
    large, unreadable, and no-file plugin module records.

- [x] Make configured plugin names safe provenance identifiers.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: paper-inspired plugin claims need stable, auditable, and
    share-safe configured extension identifiers.
  - Status: configured plugin names now use a manifest-safe ASCII grammar and
    reject secret-like values before both normal config use and manifest
    persistence. The paper index now lists this as implemented while keeping
    broader plugin configuration/provenance and direct-runtime execution
    semantics open.
  - Verification: focused config/database/CLI tests cover direct and CLI
    boundaries, including post-construction config mutation.

- [x] Normalize paper-cache manifest SHA-256 fields.
  - Paper-index evidence: the CSV/JSON download manifests record each cached
    PDF's SHA-256 hash for local literature provenance.
  - Status: all 24 `sha256` values in `papers/download_manifest.json` and
    `.csv` are now canonical lowercase 64-character hex digests. The new
    paper-manifest validator enforces canonical format, CSV/JSON agreement,
    documented count agreement, and optional local byte/hash checks.
  - Verification: focused tests cover grouped-hash rejection and digest checks;
    the current local cache validates with 24 present PDFs.

- [x] Separate historical paper-download success from current local cache
  presence.
  - Paper-index evidence: `papers/README.md` states that PDFs are intentionally
    gitignored while committed manifests describe the cache.
  - Status: `papers/README.md` now documents the availability distinction, and
    the validator JSON report emits historical download fields separately from
    current local presence and Git-tracked status.
  - Verification: focused paper-manifest tests cover optional/required missing
    PDFs, present PDFs, and tracked PDF status.

- [x] Make LLM model identifiers manifest-safe before paper-level provenance
  claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.3, and 2.6.
  - Requirement: model choice is experiment setup metadata and should not leak
    secrets or embed control text in durable run records.
  - Status: configured backend model IDs now use a manifest-safe grammar and
    reject secret-like strings. The paper index lists this as implemented while
    keeping provider availability/capability validation as a separate open
    concern.
  - Verification: focused config/database/CLI tests cover config, manifest,
    and CLI startup boundaries.

- [x] Make evaluator-stage schema validation a core cascade invariant.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.4.
  - Requirement: staged evaluator definitions are part of the task/evaluation
    contract and should fail with reproducible setup diagnostics.
  - Status: direct `CascadeEvaluator` construction now shares the config-stage
    validator and rejects malformed stages before evaluation.
  - Verification: focused evaluator tests cover the previously raw
    `samples: 0` and `retries: -1` cases plus timeout, threshold, seed, and
    cardinality failures.

- [x] Validate evaluator-stage labels as safe persisted identifiers.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: staged evaluation outcomes need stable, safe identifiers for
    thresholds, artifacts, and prompt feedback.
  - Status: configured stage labels are explicit manifest-safe identifiers and
    reject secret-like strings at config and direct evaluator boundaries.
  - Verification: focused config/evaluator tests cover unsafe and missing
    labels.

- [x] Prevent built-in/configured stage-name collisions in evaluation
  provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: every cascade outcome should identify one distinct gate or
    test ensemble.
  - Status: configured stage names are required, removing synthesized fallback
    collisions, and `diff`, `syntax`, and `validate` are reserved built-in
    labels.
  - Verification: focused config/evaluator tests cover reserved labels and
    duplicate configured names.

- [x] Revalidate mutable runtime configuration before database/manifests.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: run manifests should describe validated experiment controls,
    not arbitrary state that bypassed setup validation after object
    construction.
  - Status: `ProgramDatabase` revalidates mutable `Config` objects before
    startup manifests or run directories are written.
  - Verification: direct database tests cover mutated path, run identity,
    scalar budget, backend, plugin, and evaluator-stage fields.

- [x] Make candidate/program identities database-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the evolutionary database should preserve candidate identity,
    lineage, parent/inspiration links, and archive records as reproducible
    experiment evidence.
  - Status: `Program.id`, `parent_id`, and lineage entries now require
    manifest-safe, secret-safe identifiers, and database persistence
    revalidates mutated identities before archive/history/failure writes.
  - Verification: focused program/database tests cover construction,
    post-construction mutation, archive admission, history, duplicate ids, and
    failure-history behavior.

- [x] Protect LLM call-history provenance from external mutation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Requirement: LLM-call telemetry used for scheduler analysis and candidate
    provenance should be stable once recorded.
  - Status: `LLMEnsemble.call_history` and `last_call` now expose deep-copied
    snapshots instead of live internal call records.
  - Verification: focused ensemble tests mutate returned top-level and nested
    telemetry and prove stored history is unchanged.

- [x] Validate LLM call-role labels before treating telemetry as durable
  scheduler evidence.
  - Paper evidence: AlphaEvolve's model orchestration separates candidate
    generation and evaluation-adjacent LLM work; persisted scheduler telemetry
    should use controlled role labels.
  - Status: `LLMEnsemble.generate()` validates call roles before scheduler
    selection, and configured backend role metadata uses the same
    manifest-safe label policy.
  - Verification: focused ensemble/config tests cover non-string, blank,
    malformed, and secret-like role labels.

- [x] Validate feedback grader and metric labels before treating reviewer
  output as paper-faithful evaluation evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.4, and
    2.6, treat evaluator/reviewer feedback and score dictionaries as
    attributable parts of the optimization process.
  - Status: `llm_feedback[].name` and `metric` values now require
    manifest-safe, secret-safe labels at config validation and direct
    `apply_llm_feedback()` boundaries.
  - Verification: focused config/feedback tests cover unsafe configured and
    direct labels.

- [x] Validate prompt payloads before treating LLM-call telemetry as durable
  scheduler evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6,
    treats prompt sampling and LLM calls as attributable parts of the
    evolutionary system.
  - Status: non-string prompt payloads are rejected before backend selection
    or scheduler-state mutation.
  - Verification: focused ensemble tests prove the backend is not called and
    scheduler counters remain unchanged for non-text prompts.

- [x] Reject unsupported ensemble strategy names below the config layer.
  - Paper evidence: AlphaEvolve-style model scheduling should be auditable as a
    named policy because strategy choice affects breadth/depth/cost behavior
    and backend reward interpretation.
  - Status: `LLMEnsemble` construction now accepts only `ucb1` and
    `throughput_depth`.
  - Verification: focused ensemble tests cover unsupported direct strategies.

- [x] Reject invalid exploration coefficients below the config layer.
  - Paper evidence: UCB1-style exploration assumes a non-negative exploration
    term.
  - Status: direct `LLMEnsemble` construction rejects negative, non-finite,
    boolean, and nonnumeric exploration coefficients.
  - Verification: focused ensemble tests cover invalid direct coefficients.

- [x] Validate scheduler backend metadata below the config layer.
  - Paper evidence: AlphaEvolve-style model-routing decisions and compute
    accounting should be attributable to the LLM/backend configuration used for
    each proposal.
  - Status: direct `LLMEnsemble` construction requires one JSON-safe metadata
    mapping per backend, validates scheduler numeric fields and role labels,
    and copies metadata into call records.
  - Verification: focused ensemble tests cover malformed metadata and copied
    successful call telemetry.

- [x] Validate scheduler retry/fallback controls below `Config`.
  - Paper evidence: model orchestration retry/fallback controls must be
    reproducible scheduler state rather than accidental Python coercions.
  - Status: direct `LLMEnsemble` construction rejects invalid retry counts and
    non-boolean fallback values.
  - Verification: focused ensemble tests cover invalid direct controls and
    existing retry/fallback behavior.

- [x] Validate prompt reward policy below `Config`.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4, require
    prompt-program fitness and selection evidence to remain comparable across
    runs and construction paths.
  - Status: direct `PromptDatabase` construction now rejects zero-width or
    inverted reward bounds, unsupported prompt reward modes, and invalid
    exploration coefficients before prompt scoring or history persistence.
  - Verification: focused prompt-database tests cover invalid reward bounds,
    reward modes, and exploration coefficients.

- [x] Preserve prompt-program identity and state before treating prompt
  archives as paper evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6,
    rely on stable program/prompt lineage and attributable selection records.
  - Status: prompt programs now validate safe ids, parent lineage, generation
    and usage counters, finite reward sums, and JSON-safe metadata. Duplicate
    prompt ids and unknown parents are rejected before prompt-history writes.
  - Verification: focused prompt tests cover invalid direct state, revalidated
    mutated state, duplicate id rejection, and unknown parent rejection.

- [x] Add missing prompt-reference handling before treating prompt history as
  replayable evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6,
    require durable and attributable prompt-program references for scoring and
    lineage evidence.
  - Status: prompt scoring and mutation now reject missing or invalid
    prompt-program ids with structured `prompt_reference_error` diagnostics in
    `prompt_history_invalid.jsonl` instead of raw dictionary lookup failures.
  - Verification: focused prompt tests cover dangling score and mutation
    references plus redaction of unsafe prompt ids.

- [x] Add evidence-conditioned meta-prompt evolution.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4, describe
    improving prompt programs using observed outcomes and prompt-fitness
    evidence from the evolutionary run.
  - Status: meta-prompt mutation requests now include bounded redacted
    prompt-performance summaries, candidate outcome, active reward policy,
    prompt-arm summaries, and recent failure evidence. Prompt-history metadata
    stores context schema, hash, length, section list, and selected/latest ids.
  - Verification: focused loop tests cover evidence-conditioned mutation
    prompts, redaction/budget behavior, and persisted provenance.

- [x] Treat blank explicit prompt templates as prompt-contract diagnostics.
  - Paper evidence: AlphaEvolve-style prompt sampling should make the selected
    prompt template explicit and reproducible; invalid explicit prompt inputs
    should not silently select a different template.
  - Status: direct prompt rendering now rejects blank explicit templates instead
    of falling back to configured/default templates, while `template=None`
    remains the explicit fallback signal.
  - Verification: focused prompt tests cover blank/whitespace rejection and
    configured-variant fallback with `None`.

- [x] Make prompt-visible PDF page citations exact, not only persisted
  metadata.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.2, uses
    literature/context to shape LLM program generation, so source attribution
    should identify the excerpt actually shown to the model.
  - Status: prompt context headers now render per-page PDF span citations from
    `excerpt_page_spans`, exact non-contiguous page groups from
    `excerpt_pages`, and coarse document-level page ranges only when excerpt
    metadata is unavailable. The paper index now describes exact PDF excerpt
    page/span citations rather than coarse page-range citations.
  - Verification: focused prompt/loader tests cover `pages=1:0-20,3:60-80`,
    `pages=1,3-4`, and fallback `pages=1-5` rendering.

- [x] Make explicit-context source labels prompt-safe.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.2, uses
    context/literature in the LLM prompt; source attribution should not leak
    credential-like local labels through prompt headers or manifests.
  - Status: selected explicit-context source paths are rejected when their
    relative labels look secret-like, before `Problem.context_files`,
    `context_sources`, prompts, or manifests are produced.
  - Verification: focused loader tests cover an `api_key=...` selected context
    source label.

- [x] Make explicit-context selection patterns secret-safe.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6,
    require reproducible task/context provenance without leaking sensitive
    local labels through durable run metadata.
  - Status: `context.yaml` include/exclude patterns are rejected when they
    contain secret-like text, before `context_policy` is retained.
  - Verification: focused loader tests cover secret-like include and exclude
    pattern labels.

- [x] Define whether hidden context files are part of AlphaEvolve-style task
  context.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.2, treats prompt
    context as deliberate task/literature input.
  - Status: dot-prefixed explicit-context sources are not task context by
    default. They are skipped with manifest diagnostics unless a
    `context.yaml` include pattern explicitly names a dot-prefixed component;
    selected hidden sources are marked with `hidden: true`.
  - Verification: focused loader tests cover default hidden-source exclusion,
    explicit hidden-source inclusion, and wildcard includes that do not opt
    hidden sources into prompts.

- [x] Define selected-context extraction failure semantics.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.2, uses prompt
    context as usable problem/literature information.
  - Status: extraction failures are skipped diagnostics rather than selected
    prompt content. Invalid text, broken PDFs, and no-text PDFs are retained in
    `context_policy.skipped` with extraction status and provenance metadata;
    `selected_count` / `usable_selected_count` count only usable prompt
    context.
  - Verification: focused loader tests cover invalid UTF-8, broken PDF, and
    no-extractable-text PDF cases.

- [x] Add resource-bounded explicit context ingestion.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.2, depends on
    context/literature ingestion that remains practical for large corpora.
  - Status: local explicit-context ingestion now has configurable source-byte,
    total-byte, PDF-page, and PDF extracted-character budgets. Over-budget
    sources are skipped with manifest diagnostics instead of being silently
    read/extracted and then prompt-truncated.
  - Verification: focused loader tests cover source byte limits, total byte
    limits, PDF page limits, PDF extracted-character limits, and invalid budget
    values.

- [x] Treat silent degradation after explicit context extraction failure as a
  context-ingestion fidelity gap.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.2, uses prompt
    context as usable problem/literature information, so explicitly selected
    context should not disappear silently.
  - Status: implemented. Explicit include-matched context extraction failures
    now default to startup failure via `on_explicit_context_failure: error`;
    `warn` is the documented opt-in degraded mode that records
    `explicit_context_failure_count` and matched include-pattern diagnostics in
    `problem.context_policy`.
  - Verification: focused loader tests cover invalid text, mixed explicit
    include sets, corrupt/no-text PDFs, PDF resource limits, invalid policy
    values, and degraded warning diagnostics. `papers/README.md` now scopes the
    AlphaEvolve row to "default-fail explicit include extraction policy with
    opt-in degraded warning diagnostics."

- [x] Qualify package-metadata coverage in paper-level reproducibility claims.
  - Paper evidence: AlphaEvolve-aligned manifest provenance should distinguish
    useful execution identity from complete reproduction evidence.
  - Status: implemented as a scoped paper-index claim. Runtime manifests record
    the selected execution-identity PEP 621 subset, build-backend metadata, and
    installed versions for declared runtime dependencies. `papers/README.md`
    now explicitly excludes license/authors/classifiers/project URLs, optional
    dependency groups, console scripts, lockfiles, full package freezes,
    transitive dependencies, dev/test tooling, numerical backend/accelerator
    details, private package-source policy, live provider service/API versions,
    and provider cost or remote provider-side default capture from the current paper-level
    environment-provenance claim.
  - Verification: focused provenance tests cover the included package/build
    metadata, dependency provenance, malformed/missing pyproject states,
    redaction/escaping, and bounded diagnostics; README/run-artifact/development
    docs describe the same narrow package-metadata boundary.

- [x] Qualify full-workspace best export as CLI happy-path behavior.
  - Paper evidence: the AlphaEvolve status row lists full-workspace best export
    as implemented, but direct `evolve()` returns the best `Program` without
    materializing `best.py` or `best_workspace/`.
  - Status: implemented as a scoped paper-level claim. `papers/README.md` and
    run-artifact docs now state that best-artifact materialization is a CLI
    post-`evolve()` export path, while direct `evolve()` calls return the best
    program without writing those files.
  - Verification: CLI tests cover complete best-workspace export and
    no-best-artifact cases; run-artifact docs and the paper-index
    best-export note describe the CLI/direct-API boundary.

- [x] Treat post-finalization best-export failures as a paper-level artifact
  provenance gap.
  - Paper evidence: AlphaEvolve-style experiment records should identify which
    selected code artifacts were actually materialized and whether durable
    best-candidate outputs exist.
  - Status: implemented for the paper-visible CLI contract. CLI best-export
    attempts write `runtime.best_artifact_export` with completed/failed status,
    paths, hashes when available, and redacted diagnostics; paper-index and
    run-artifact docs distinguish completed core evolution from post-run
    materialization success. Direct/core export ownership remains an open code
    gap rather than an overclaimed paper artifact guarantee.
  - Verification: focused CLI tests cover success on a real zero-generation run
    and forced `_write_best_artifacts()` failure after core manifest
    finalization, while docs explain that top-level runtime status remains the
    core evolution result.

- [x] Make effective task configuration precedence explicit and validated.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.3, and 2.6,
    require reproducible task setup and LLM/evaluator choices before a run.
  - Status: implemented for final effective config validation. `_build_config()`
    now merges defaults, optional problem-local `config.yaml`, and CLI
    overrides before constructing and validating the final `Config`, so
    higher-precedence CLI values can replace invalid lower-precedence scalar or
    backend fields before validation. `papers/README.md` now includes final
    effective config validation after CLI overrides in the AlphaEvolve status
    row.
  - Verification: CLI tests cover overriding invalid `max_generations` and
    `backends` values from `config.yaml`; configuration docs state the same
    final-merged-validation order.

- [x] Define deterministic explicit-context glob semantics.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Section 2.2, treats prompt
    context as deliberate task input with reproducible source selection.
  - Status: local explicit-context selection now uses deterministic
    path-segment-aware globs: `*` does not cross `/`, while `**` recursively
    matches zero or more path segments. The AlphaEvolve paper-index context row
    now describes deterministic segment-aware selection provenance.
  - Verification: focused loader tests cover root, nested, recursive, include,
    and exclude behavior.

- [x] Prevent raw database insertion from bypassing AlphaEvolve-style validity
  gates.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Status: raw `ProgramDatabase.add()` reaches `MAPElites.add()`, which now
    requires `evaluation["is_valid"] is True`, finite fitness, and finite
    selection score before changing search state. Invalid direct insertions are
    not retained as elites and are not returned by exploit sampling or `best()`.
  - Verification: a current-code proof inserted a program with
    `evaluation={"is_valid": False}` and `fitness=1.0`; the archive event
    returned `admitted=False`, `reason="invalid_evaluation"`, and both exploit
    sampling and `best()` returned no program.

- [x] Treat the workspace example's unused-helper acceptance as a paper-level
  codebase-fidelity gap.
  - Paper evidence: AlphaEvolve evolves code under task-specific evaluators and
    can operate over codebase-like candidates; workspace examples should prove
    cross-file behavior when they are used as evidence for codebase fidelity.
  - Status: implemented for the current smoke fixture. `workspace_math`
    validates the helper dependency by loading `helpers.base_value()`, injecting
    that value through a fake `helpers` module, and rerunning with `base + 1`.
    Candidates must produce `42` and then `43`, so an unused-helper constant
    solution no longer passes.
  - Verification: `tests/test_examples.py` covers both the valid multi-file
    seed and rejection of a direct constant-only `solve()`.

- [x] Persist complete explicit-context selection provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Status: deterministic local explicit-context provenance is implemented.
    Local context ingestion records selected-source hashes/excerpts for
    `.txt`, `.md`, `.py`, and `.pdf` sources. `manifest.json` persists
    `problem.context_policy` with context-manifest hash, include/exclude rules,
    source budgets, selected/skipped counts, unmatched includes, and hashed
    skipped-source diagnostics. PDF citation provenance records page-level
    character spans plus `excerpt_pages` / `excerpt_page_spans` for the actual
    rendered excerpt, and prompt context headers render exact excerpt
    page/span citations when available.
  - Verification: focused loader and prompt tests cover rendered PDF excerpt
    page spans and prompt-visible citation formatting. Remaining
    AlphaEvolve-scale semantic/ranked literature selection and summarization
    gaps remain tracked separately.

- [x] Treat partial quoted-assignment redaction as a paper-level artifact
  safety gap.
  - Requirement: Paper-comparable experiment artifacts should be safe to share
    without leaking credential-like text through prompts, logs, manifests,
    plugin metadata, or evaluator diagnostics.
  - Status: fixed in the shared redaction helper. Quoted secret assignments
    with spaces no longer leave tail fragments such as `def ghi`, `extra`, or
    `abc def` visible after `[REDACTED]`.
  - Verification: `py -3.12 -m pytest tests/core/test_redaction.py --tb=short`
    passes with regression coverage for whitespace-containing quoted
    assignment values.

- [x] Treat provider-token casing gaps as paper-level artifact safety limits.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4, 2.5, and 3.
  - Requirement: prompt, evaluation, and database artifacts used for long
    experiments should have predictable privacy and retention boundaries.
  - Status: fixed for known standalone provider-token prefixes by making the
    shared token detector case-insensitive.
  - Verification: `py -3.12 -m pytest tests/core/test_redaction.py --tb=short`
    passes with uppercase and mixed-case provider-token examples.

- [x] Treat unredacted stage-seed metadata as a paper-level cascade provenance
  gap.
  - Paper evidence: AlphaEvolve-style evaluator cascades and benchmarks rely on
    reproducible stage/sample context, but published run evidence should not
    leak credentials or private identifiers through metadata fields.
  - Status: implemented by rejecting secret-like string stage seeds before
    evaluator stage context is accepted.
  - Verification: `py -3.12 -m pytest tests/core/test_config.py
    tests/core/test_redaction.py --tb=short` passes with the original
    token-like stage-seed proof shape and broader redaction grammar fixtures.
- [x] Treat mutable post-validation evaluator stages as a cascade-fidelity
  gap.
  - Paper evidence: AlphaEvolve-style staged evaluation requires stable stage
    definitions and budgets so scores, stop reasons, artifacts, and manifests
    can be reproduced from the declared experimental setup.
  - Previous gap: `CascadeEvaluator` validated the supplied `stages` list but
    retained the caller's mutable objects. A current-code proof mutated a
    validated stage after evaluator construction and caused a raw runtime
    `ValueError` from an invalid `samples` field.
  - Status: implemented for the evaluator boundary. Stage specs are deep-copied
    before validation and the evaluator stores the validated snapshot; tests
    prove post-validation mutations of nested stage fields do not change
    execution, metadata, artifact policy, or seed payloads.
- [x] Treat mutable LLM backend arm lists as an ensemble-fidelity gap.
  - Paper evidence: AlphaEvolve-style LLM ensembles and scheduler comparisons
    depend on stable backend identities, counts, rewards, and telemetry across
    the run.
  - Previous gap: `LLMEnsemble` validated the backend metadata length at
    construction but kept the mutable backend list. A current-code proof
    mutated that list after construction, causing raw `IndexError` and
    `AssertionError` failures because scheduler arrays no longer matched the
    backend arm set.
  - Status: implemented for construction-time scheduler fidelity.
    `LLMEnsemble` snapshots backend arms with a list copy; tests prove
    append/clear/reorder mutations to the caller list cannot change selected
    arms, counts, or call telemetry.
- [x] Treat mutable candidate workspaces as a codebase-candidate fidelity gap.
  - Paper evidence: AlphaEvolve-style codebase candidates should be evaluated
    and archived as stable candidate snapshots, with safe paths, valid primary
    files, and text content invariants preserved across prompt and evaluator
    boundaries.
  - Previous gap: `CandidateWorkspace` validated file-set invariants only
    during construction. A current-code proof mutated a valid workspace
    afterward and produced raw `KeyError`, `ValueError`, and `TypeError`
    failures from primary-file lookup and materialization.
  - Status: implemented for current workspace access/materialization
    boundaries. `CandidateWorkspace` now revalidates through a normalized
    snapshot for `code`, `to_dict()`, and `materialize()`; tests cover mutated
    primary files, unsafe paths, non-text contents, and duplicate normalized
    paths.
- [x] Treat mutable prompt-program records as a meta-prompt fidelity gap.
  - Paper evidence: AlphaEvolve-style prompt evolution needs reproducible
    prompt programs with stable identity, lineage, text, reward history, and
    selection semantics across run state and prompt rendering.
  - Previous gap: `PromptDatabase.add()` and `PromptDatabase.all()` exposed live
    `PromptProgram` objects. Mutating admitted or returned programs could make
    selection return an invalid template that no longer matched the recorded
    admitted prompt.
  - Status: implemented for prompt archive boundaries. Prompt programs are
    deep-copied on admission and copied again for `select()`/`all()` results;
    tests prove caller mutation cannot change stored templates, metadata, or
    archive scoring state.
- [x] Treat trusted normalized-metric metadata as a multi-objective fidelity
  gap.
  - Paper evidence: AlphaEvolve-style metric-aware search should compare
    candidates using declared objective semantics and reproducible metric
    values, especially when metrics guide parent and inspiration selection.
  - Previous gap: metric leader sampling accepted arbitrary finite
    `metadata.normalized_metrics` values. A current-code proof selected a
    low-fitness candidate with `normalized_metrics.score=999.0` over an honest
    candidate with `score=0.9`.
  - Status: implemented for parent/inspiration metric sampling. The sampling
    path now ignores out-of-range normalized values and undeclared metric names
    when a declared metric order is configured.
- [x] Treat unvalidated direct inspiration-count inputs as a database sampling
  fidelity gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: prior-program sampling should use reproducible, typed sample
    counts when conditioning proposal prompts or future batch workers.
  - Previous gap: configured `num_inspirations` was validated, but direct
    `MAPElites` and `IslandModel` sampling calls accepted raw `k` values.
    String counts crashed with `TypeError`, while boolean and float counts
    could be accepted as one-sample requests.
  - Status: implemented for public sampling APIs. Direct database, island, and
    MAP-Elites sample counts share the same non-negative integer validation
    helper and test coverage.

- [x] Treat unvalidated sampling exclusion containers as database-state
  fidelity gaps.
  - Paper evidence: AlphaEvolve-style evolutionary databases should support
    reproducible candidate selection and inspiration retrieval from persisted
    state.
  - Previous gap: LibreEvolve's direct MAP-Elites/island sampling accepted
    arbitrary `exclude_ids` containers. Strings, lists, dictionaries, and
    custom membership objects could alter exclusion behavior according to
    Python container semantics, while integers raised raw `TypeError`.
  - Status: implemented. Exclusion-set semantics are now explicit at the
    database, island, and MAP-Elites sampling boundaries: accepted inputs are
    normalized immutable collections of manifest-safe program ids, and
    malformed restored/controller state is rejected before sampling.

- [x] Treat backend metadata key labels as LLM-provenance safety evidence.
  - Paper evidence: AlphaEvolve-style model-selection provenance should be
    durable, inspectable, and share-safe. Scheduler metadata keys are part of
    that provenance when custom/direct or restored backends are used.
  - Previous gap: `LLMEnsemble` validated backend metadata values but not
    keys, so secret-like and display-confusing metadata labels could enter
    successful call-history records.
  - Status: implemented. Paper-visible backend metadata key semantics are now
    rejection-based: only manifest-safe, secret-safe labels are accepted
    recursively, and malformed custom/direct metadata fails before scheduler
    selection or call-record construction.

- [x] Treat unvalidated `Program.metadata` shape as a paper-level database
  fidelity gap.
  - Paper evidence: AlphaEvolve's program database stores rich information
    about generated programs, scores, feedback, and lineage; LibreEvolve's
    paper-alignment claims depend on metadata being queryable structured
    evidence, not arbitrary JSON payloads.
  - Previous gap: the `Program` model and database boundary did not require
    metadata to be a mapping. Arrays could be persisted as history metadata,
    and some non-mapping values crashed archive admission.
  - Status: implemented for new/current candidates. Candidate metadata now has
    a paper-visible object-shape and JSON-safety contract at model and
    database boundaries, including display-unsafe key rejection and
    secret-like string redaction. Legacy malformed-history migration remains
    explicitly outside this completed implementation slice.

- [x] Validate persisted program metric vectors outside evaluator output.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: the evolutionary database should preserve typed score and
    metric vectors that remain meaningful for multi-objective selection,
    archive resurfacing, and replay.
  - Previous gap: direct or restored `Program.metrics` could carry
    non-JSON-native finite numeric objects such as `Fraction`, which only
    failed during strict JSON persistence.
  - Status: implemented for current program/database/plugin-style boundaries.
    Direct metric vectors now require string keys and JSON-native finite
    numeric values, with `is_valid` boolean-only. Unsupported numeric types are
    rejected before archive mutation, preserving metric-vector claims for
    direct/restored candidate records.

- [x] Treat unvalidated direct feedback numeric policy fields as a
  paper-level reviewer fidelity gap.
  - Paper evidence: AlphaEvolve-style reviewer and evaluator signals must have
    well-defined score composition and rejection semantics before they can be
    treated as reliable experimental feedback.
  - Previous gap: direct `apply_llm_feedback()` converted `weight` and
    `min_score` only after a score was parsed, so malformed direct policy
    fields raised raw `ValueError` instead of producing reviewer diagnostics.
  - Status: implemented. Direct reviewer policy fields now have a
    paper-visible finite-number contract before LLM calls or metric mutation,
    with structured invalid-config records and tested rollback semantics.

- [x] Keep feedback-reviewer diagnostic prompts finite and JSON-standard.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: LLM prompts can incorporate execution outcomes and scores from
    previous attempts as reliable structured feedback.
  - Previous gap: feedback-reviewer diagnostics serialized non-finite evaluator
    values with default JSON behavior, so prompts could contain non-standard
    `NaN`/`Infinity` tokens.
  - Status: implemented. Reviewer diagnostic prompts now normalize non-finite
    values into explicit JSON objects and use strict JSON serialization, so
    paper-level structured execution-feedback claims no longer depend on
    permissive JSON tokens for this path.

- [x] Apply redaction policy to failed-trial memory artifacts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figures 1-2 and Sections 2.2 and
    2.6.
  - Requirement: failed-trial records are part of the program database used for
    future prompt context and analysis, so retained mutation text and evaluator
    diagnostics need the same safety policy as other persisted prompts and
    outputs.
  - Previous gap: `ProgramDatabase.log_failure()` wrote bounded but raw fields
    to `failure_history.jsonl`, allowing secret-like mutation text and
    evaluator diagnostics to persist.
  - Status: implemented. Generated and seed failed-trial records now redact
    secret-like retained text before persistence and metadata mirroring, while
    preserving mutation hashes for correlation; prompt reuse of database
    failure records is covered by regression tests.

- [x] Redact structured failed-trial mutation snippets before prompt reuse.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Requirement: failed candidate memories reused by prompt sampling should not
    leak raw secrets or uncontrolled model text through mutation snippets.
  - Previous gap: structured failure records were compacted, but
    `_render_failure_line()` inserted `mutation_text` with only newline
    replacement and a 160-character slice.
  - Status: implemented. Structured failure mutation snippets now use the
    bounded/redacted prompt-summary policy, so prompt-memory reuse no longer
    exposes raw secret-like mutation text in this path.

- [x] Treat malformed failed-trial score fields as a paper-level prompt
  memory gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Requirement: failed-trial memories used as evolutionary prompt context
    should carry trustworthy, finite diagnostics rather than misleading raw
    restored values.
  - Previous gap: `_render_failure_line()` formatted booleans and non-finite
    floats as scores, producing prompt text such as `Score 1.00` and
    `Score nan`.
  - Status: implemented. Failure-memory prompt score rendering now accepts only
    finite non-boolean native numbers as display scores and marks malformed
    structured or legacy tuple scores as `unknown`.
- [x] Treat malformed failed-trial memory records as a paper-level prompt
  robustness gap.
  - Paper evidence: AlphaEvolve-style program databases reuse prior failures as
    prompt context, so malformed or restored failure-memory rows should not
    crash prompt generation without structured diagnostics.
  - Implemented evidence: prompt construction now defines a runtime
    failure-memory schema at render time: list/tuple container, structured
    mapping records, or exactly two-item legacy tuple records. Malformed rows
    are repaired into bounded diagnostics instead of raw `ValueError`/`TypeError`
    failures.
  - Verification: prompt tests prove malformed tuple, string-container, list,
    object, malformed structured, valid tuple, and valid structured records all
    render without prompt-construction crashes.
- [x] Treat brittle provider-exception formatting as an LLM-provenance gap.
  - Paper evidence: AlphaEvolve-style model ensembles need inspectable LLM-call
    provenance and failure accounting because provider choices and outages
    affect which candidate programs are generated.
  - Implemented evidence: provider error formatting now survives malformed
    exception objects by recording exception class, safe fallback message,
    retry/fallback booleans, counts before/after, and redacted bounded error
    text before the original provider exception is re-raised.
  - Verification: `tests/llm/test_ensemble.py` proves failed-call telemetry is
    present for normal, secret-like oversized, broken-stringification, and
    broken-repr provider exceptions.
- [x] Treat blank accepted LLM prompts as a paper-level sampling fidelity gap.
  - Paper evidence: AlphaEvolve-style LLM proposal sampling is driven by rich
    task, context, parent, and instruction prompts.
  - Implemented evidence: the ensemble prompt boundary now requires non-empty
    prompt text before sampling, telemetry, retry/fallback, and budget-adjacent
    scheduler accounting can proceed.
  - Verification: tests cover direct blank strings and blank prompt-template
    rendering through `PromptSampler`, while preserving successful telemetry for
    valid nonblank prompts.
- [x] Validate direct backend prompt payloads before paper-level LLM telemetry
  claims.
  - Paper evidence: AlphaEvolve's LLM calls are structured proposal-generation
    inputs, not arbitrary SDK payloads.
  - Implemented evidence: direct OpenAI, Anthropic, and Ollama adapter calls
    now enforce the shared non-empty text prompt validator before provider
    calls. Registry-created bundled backends use those same adapter classes.
  - Verification: backend tests cover the prior mocked-provider failures and
    `docs/backends.md` now states the direct adapter prompt boundary.
- [x] Validate direct backend adapter parameters before paper-level LLM
  configuration claims.
  - Paper evidence: AlphaEvolve treats model choices and sampling budgets as
    experiment controls. LibreEvolve's backend controls should not depend on
    whether a bundled backend was created through CLI config or direct adapter
    construction.
  - Implemented evidence: direct OpenAI, Anthropic, and Ollama constructors now
    enforce manifest-safe model identifiers plus positive integer token limits
    before provider calls; OpenAI direct construction also validates reasoning
    effort against the existing supported set.
  - Verification: backend tests prove the prior invalid direct constructor
    examples fail before SDK calls, and valid direct parameters remain accepted.
- [x] Account for failed-backend attempts in model-scheduler fidelity.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: model scheduling should allocate proposal work and compute
    budget intentionally across fast/deep models, including provider failures.
  - Implemented evidence: failed provider selections are no longer invisible to
    scheduler counts after retry exhaustion. They are recorded as failed call
    telemetry and counted once as zero-reward pulls before fallback or re-raise.
  - Verification: ensemble tests cover failed-call count updates and repeated
    fallback behavior; `docs/backends.md` documents remaining heuristic limits.
- [x] Treat mutable configured backend specs as LLM-provenance evidence gaps.
  - Paper evidence: AlphaEvolve-style model-selection comparisons require the
    recorded backend/model choices to match the effective model calls that
    generated candidates.
  - Implemented evidence: backend specs are revalidated and copied inside
    `build_llm()` before adapter construction, so post-validation mutation of
    configured backend specs cannot alter backend identity or poison call
    telemetry.
  - Verification: tests cover mutated type/model/token/scheduler fields and
    valid copied spec isolation before model-provenance claims rely on
    `build_llm()`.
- [x] Treat malformed or non-text provider outputs as failed LLM samples.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2-2.3.
  - Requirement: LLM sampling should produce attributable proposal text or a
    recorded failed sample; malformed provider responses should not silently
    corrupt scheduler state.
  - Implemented evidence: OpenAI Chat/Responses, Anthropic Messages, and Ollama
    Chat adapters validate extracted provider response text before returning.
    Missing, empty, whitespace-only, or non-text provider content raises
    provider-labeled failures that flow through adapter retry and ensemble
    retry/fallback handling.
  - Verification: backend tests cover OpenAI chat `None`, OpenAI Responses
    missing/empty output text, Anthropic non-text/empty content, and Ollama
    missing/empty content.

- [x] Treat whitespace-only LLM outputs as a paper-level sampling fidelity gap.
  - Paper evidence: AlphaEvolve-style proposal sampling depends on useful text
    from selected models and should account for malformed samples separately
    from successful proposal generation.
  - Implemented evidence: shared response validation now treats
    whitespace-only backend output as a failed LLM sample before scheduler
    success accounting.
  - Verification: ensemble tests cover whitespace-only provider outputs and
    confirm failed-call telemetry instead of successful call records.
- [x] Treat unbounded accepted LLM outputs as a paper-level sampling budget gap.
  - Paper evidence: AlphaEvolve-style model sampling is compute-budgeted and
    proposal outputs become inputs to mutation parsing, evaluation history, and
    future prompt context.
  - Status: accepted LLM output size is now a visible local budget knob:
    `llm_max_response_chars` defaults to `100000`, is validated in config and
    direct ensemble construction, and classifies over-limit model outputs as
    failed attempts with retry/fallback behavior before proposal parsing or
    persistence accepts them. Broader token/cost/provider-usage accounting
    remains tracked separately.
  - Verification: focused scheduler/config/CLI tests passed with
    `py -3.12 -m pytest tests/llm/test_ensemble.py tests/core/test_config.py
    tests/test_cli.py --tb=short`.

- [x] Treat mutable LLM scheduler counters as a paper-level ensemble-state gap.
  - Requirement: paper-visible LLM ensemble behavior should be based on
    reproducible finite bandit state. Counts and rewards used for routing should
    not be externally corruptible without validation.
  - Status: scheduler counts/rewards are no longer exposed as live mutable
    lists. `scheduler_state` returns a copy and `restore_scheduler_state()`
    validates restored counts, rewards, totals, lengths, and finite values
    before state replacement. Broader persisted resume semantics remain tracked
    separately.
  - Verification: focused ensemble tests cover direct mutation attempts,
    malformed restored scheduler state, and valid restored state.

- [x] Treat non-propagated LLM call roles as a paper-level backend-interface
  gap.
  - Paper evidence: AlphaEvolve-style systems distinguish proposal generation,
    critique, feedback/grading, and prompt-improvement calls. Those roles can
    require different model choices, decoding settings, output contracts, and
    budget policies at the provider boundary.
  - Status: validated call roles are now propagated through the backend
    protocol as `generate(prompt, role=role)`. Built-in adapters accept and
    ignore the role keyword, while custom protocol-compatible backends can
    consume it for role-specific request handling. Broader request-parameter
    and structured prompt-message provenance remains open.
  - Verification: focused ensemble tests cover role-aware custom backends plus
    retry and fallback role propagation.

- [x] Treat mutable backend scheduler metadata as an ensemble-fidelity gap.
  - Paper evidence: AlphaEvolve-style LLM ensembles require stable backend
    identities and scheduling controls so breadth/depth/cost/latency decisions
    and telemetry remain reproducible.
  - Status: backend scheduler metadata is now a private validated snapshot;
    public reads return deep copies, and internal selection/call-history paths
    use the private data. Broader metadata normalization and operational
    breadth/depth role semantics remain tracked separately.
  - Verification: focused ensemble tests cover mutation of returned metadata,
    JSON-safe call-history serialization, and continued `throughput_depth`
    routing.

- [x] Treat framework RNG isolation as part of AlphaEvolve reproducibility.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: long-running AlphaEvolve-style experiments should own
    framework stochastic state without resetting an embedding application's
    process-global Python RNG.
  - Status: framework-owned stochastic choices now use explicit run-local RNG
    state for loop parent selection, prompt-template sampling,
    database/island sampling, and MAP-Elites random sampling. Full RNG-state
    persistence and replay/resume restoration remain tracked separately.
  - Verification: focused loop and database tests prove `evolve()` and
    database random sampling leave caller global RNG state unchanged.

- [x] Treat malformed direct budget event kinds as paper-level accounting gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: compute-budget accounting should classify baseline/seed work
    separately from generated-candidate work when comparing runs.
  - Status: direct `RunBudget.record_evaluation()` now rejects malformed event
    kinds before counter mutation, so synchronous seed/candidate budget
    summaries no longer depend on Python truthiness of arbitrary objects.
    Restored-controller event validation remains open.
  - Verification: focused budget tests cover malformed strings, integers,
    `None`, lists, and arbitrary objects.

- [x] Keep direct runtime budget increments finite and manifest-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: compute-budget accounting should be durable, comparable, and
    machine-readable across completed and aborted runs.
  - Status: direct elapsed-time increments through `RunBudget.record_evaluation()`
    now require finite non-negative numeric elapsed seconds and fail before
    counter mutation otherwise. Restored budget-state validation remains open.
  - Verification: focused budget tests cover malformed elapsed-time values and
    valid finite seed/candidate accounting.

- [x] Treat malformed current budget snapshot fields as paper-level accounting gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: compute-budget summaries used for paper-visible comparisons
    should be typed, finite, manifest-safe records with a known stop-reason
    vocabulary.
  - Status: current budget snapshots and finalization now validate
    non-negative counters, finite consumed evaluator seconds, coherent
    seed/candidate totals, valid limits, and known stop reasons before values
    can reach runtime manifests or candidate metadata.
  - Verification: focused budget tests cover malformed current snapshot state.

- [x] Treat malformed restored budget snapshot fields as paper-level accounting gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: compute-budget summaries used for paper-visible comparisons
    should remain typed, finite, manifest-safe records with known stop-reason
    and wall-clock vocabularies even when restored from persisted artifacts.
  - Status: restored budget snapshot preflight now validates limits, consumed
    counters, finite elapsed/runtime values, coherent seed/candidate totals,
    coherent generation counters, known stop reasons, UTC timestamp metadata,
    and resume segment shape before returning a defensive copy. Full
    resume/controller state application remains a separate open runtime gap.
  - Verification: focused budget tests cover malformed restored snapshot
    fields and diagnostics.

- [x] Validate backend-object telemetry before treating LLM call logs as paper
  evidence.
  - Paper evidence: AlphaEvolve-style LLM ensemble provenance should make model
    choices and call outcomes inspectable because generated programs are shaped
    by those calls.
  - Status: direct/custom backend object `name` and `api_mode` attributes are
    normalized with structured diagnostics when unsafe, and restored
    `llm_calls.jsonl` telemetry now rejects unsafe backend names, API modes,
    metadata, and diagnostics before replay metadata can be used as paper
    evidence. Future registry/plugin backend construction remains scoped to the
    separate plugin-registry gap because that surface is not implemented.
  - Verification: focused ensemble tests cover live call-history safety,
    candidate-history serialization, and restored call-ledger telemetry
    rejection cases.

- [x] Redact aborted-run exception messages before paper-level provenance claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: experimental metadata should preserve useful failure
    diagnostics without leaking secrets or unbounded provider/plugin text into
    durable artifacts.
  - Status: aborted-run manifests now persist redacted and bounded abort
    messages with truncation/unavailable flags while preserving exception type,
    phase, and inferred role.
  - Verification: focused loop tests cover provider, plugin, and evaluator
    abort diagnostics with secret-like payloads, oversized messages, and
    unstringifiable exceptions.

- [x] Include completed-run artifact/history inventories in manifests.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: long-running experiments need durable accounting of generated
    programs, artifacts, and consumed resources for later inspection and
    comparison.
  - Status: completed runs now persist runtime history summaries and known
    artifact pointers for history, failure/quarantine, prompt-history,
    evaluator/plugin artifact roots, and core-finalization-time best exports.
  - Verification: focused loop tests cover completed seed-only, generated
    failure-history, and plugin-artifact manifest inventories.

- [x] Make runtime artifact pointers trustworthy before treating them as
  AlphaEvolve provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: run artifacts used to analyze or resume long searches should
    be attributable to the run and should not silently point outside the
    generated artifact root.
  - Status: runtime artifact pointers now report link/junction/broken-link
    state and target containment diagnostics with hashed target identifiers.
    Link-like artifacts are not summarized using followed target size/type.
  - Verification: focused loop tests cover regular, linked, broken-linked, and
    Windows-junction artifact pointers where platform support exists.

- [x] Treat abort artifact-pointer filesystem failures as a paper-level
  runtime-provenance gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: failed or interrupted long-running searches should still leave
    trustworthy diagnostics about why the run stopped and which artifacts were
    produced.
  - Status: artifact pointer inspection is now best-effort and records
    redacted, bounded, typed `inspection_errors` per artifact instead of
    masking the original abort.
  - Verification: focused loop tests cover stat-failing history, quarantine,
    evaluator-artifact, and plugin-artifact pointers with secret-like errors.

- [x] Define no-evaluation budget behavior.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: budgeted experiments should report what work was attempted
    and what candidate/evaluation evidence exists at each budget point.
  - Status: `max_evaluations=0` is treated as a dry budget point with explicit
    no-candidate runtime history diagnostics and zero consumed evaluations.
    Zero evaluator-second/runtime-second budgets are rejected by config
    validation rather than represented as dry runs.
  - Verification: focused loop tests cover dry zero-evaluation manifests and
    zero-second budget rejection.

- [x] Qualify manifest atomicity versus crash-durability in runtime evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: long-running experiment metadata should be durable enough for
    audit, resume, and comparison after failures.
  - Status: manifest writes now attempt parent-directory fsync after atomic
    replacement, and run-artifact docs state the remaining
    platform/filesystem-specific crash-durability boundary.
  - Verification: focused JSON writer tests prove parent-directory fsync is
    attempted.

- [x] Add corrupt-manifest recovery to run provenance durability.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: long-running experiments should retain enough provenance to
    diagnose and compare runs after interruption or artifact corruption.
  - Status: runtime updates now append unreadable-current-manifest diagnostics
    and rebuild from the retained startup manifest plus runtime payload when
    the replacement payload is valid.
  - Verification: focused database tests cover malformed, empty, non-UTF-8, and
    invalid-replacement manifest recovery.

- [x] Treat raw archive metric-shape crashes on invalid candidates as a
  paper-level database diagnostics gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3, 2.5, and 2.6.
  - Requirement: invalid or failed proposals should still yield structured
    evaluator/database evidence that can be reused by later prompt sampling and
    experiment analysis.
  - Status: invalid candidates now return structured `invalid_evaluation`
    archive diagnostics before malformed metric vectors are validated; failure
    history preserves invalid candidates with malformed metrics.
  - Verification: focused MAP-Elites/database tests cover malformed invalid
    candidate metrics and valid-candidate metric validation.

- [x] Treat raw archive insertion without admission metadata as a paper-level
  database provenance gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3 and 2.5.
  - Requirement: evolutionary database entries should preserve enough
    structured archive evidence to support later selection, analysis, and
    resumable/reproducible search.
  - Status: public `ProgramDatabase.add()` now routes through `admit()` and
    attaches `metadata.archive_admission` before persistence.
  - Verification: focused database tests cover public add/log persistence.

- [x] Treat raw archive threshold bypass as a paper-level database policy gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.3 and 2.5.
  - Requirement: candidate admission, archive membership, and parent selection
    should use one coherent quality/validity policy.
  - Status: public `ProgramDatabase.add()` now applies the default thresholded
    admission policy, preventing negative-fitness valid candidates from
    becoming parents/elites through that public path.
  - Verification: focused database tests cover `below_threshold` rejection
    through public `add()`.

- [x] Treat non-atomic candidate materialization as a paper-level codebase
  fidelity gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: codebase-candidate evaluation should operate on complete
    workspace snapshots; partial filesystem state after failed
    materialization is not faithful experiment evidence.
  - Status: candidate workspaces now materialize through a complete temporary
    sibling workspace before target-root installation, preserving existing
    visible roots on write failure.
  - Verification: focused candidate tests cover direct materialization failure
    preservation; evaluator and CLI tests cover validator and best-artifact
    export surfaces.

- [x] Treat non-UTF-8-encodable candidate contents as a paper-level codebase
  fidelity gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: text-based codebase candidates should have deterministic file
    encoding semantics before evaluation, export, or replay.
  - Status: direct and mutation-generated candidate file contents must be
    UTF-8 encodable before workspace state is accepted or materialized.
  - Verification: focused candidate tests cover direct workspace and mutation
    rejection for unpaired-surrogate text.

- [x] Treat linked-ancestor materialization as a paper-level codebase
  containment gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.5.
  - Requirement: paper-visible codebase candidates and evaluator workspaces
    should be attributable to the run-owned filesystem root, not silently
    redirected through host path aliases.
  - Status: materialization now rejects symlink and Windows junction ancestors
    before resolving or writing the candidate workspace.
  - Verification: focused candidate tests cover symlink/junction parent
    rejection and prove the outside target is not written.

- [x] Treat unredacted non-dict retrieval bodies as a DeepEvolve context gap.
  - Paper: DeepEvolve paper tracked in `papers/README.md`.
  - Requirement: DeepEvolve-style external research context should be bounded,
    source-attributed, and safe before it becomes prompt-visible evidence.
  - Status: custom retrieval results from strings, dict synthesis, and
    arbitrary objects are redacted and bounded before prompt rendering, with raw
    result length/hash, prompt-visible provider/source labels, and
    redaction/truncation metadata retained.
  - Verification: focused DeepResearch tests cover string/object custom
    providers, dict synthesis, oversized output, and secret-like output.

- [x] Treat unvalidated direct prompt mutation modes as a paper-level output
  contract gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: AlphaEvolve-style prompt sampling and evaluator/parser
    accounting depend on a clear code-edit output contract for each sample.
  - Status: direct `PromptSampler.build()` validates mutation modes against the
    shared `diff`/`full` enum before rendering prompt labels or instructions.
  - Verification: focused prompt/config tests cover invalid direct values and
    valid diff/full prompt output.

- [x] Treat unvalidated direct prompt-variant containers as a paper-level
  prompt-sampling gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: prompt programs and prompt variants should be part of a
    reproducible sampling policy, not arbitrary runtime objects.
  - Status: direct `PromptSampler` variants now require a list of renderable
    template strings before construction, build-time selection, or config use.
  - Verification: focused prompt/config tests cover string, generator, tuple,
    non-string item, invalid-template, mutated-state, and valid config cases.

- [x] Treat unvalidated direct proposal-metadata toggles as a paper-level
  prompt-envelope gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: prompt-visible proposal metadata and downstream selection
    evidence should be controlled by a reproducible prompt policy.
  - Status: direct prompt construction validates `capture_proposal_metadata` as
    a boolean before metadata instructions can alter the expected response
    envelope.
  - Verification: focused prompt/config tests cover true, false, string,
    numeric, container, and object values.

- [x] Treat unvalidated direct extra context as a paper-level prompt-context
  gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: prompt context should be reproducible, attributable, and
    bounded when it includes external literature, retrieval, plugins, or user
    guidance.
  - Status: direct prompt extra context now requires text input, applies shared
    secret redaction, and enforces a prompt-visible size cap before rendering.
  - Verification: focused prompt tests cover invalid direct values, valid text,
    oversized text, and secret-like text.

- [x] Treat unvalidated direct parent/inspiration prompt inputs as a
  paper-level sampling-evidence gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: prompt-visible parent/inspiration sets are part of experiment
    evidence and replayability.
  - Status: direct prompt construction requires a `Program` parent and a list
    of `Program` inspirations before rendering prompt evidence.
  - Verification: focused prompt tests cover malformed parent values,
    malformed inspiration containers/items, empty inspiration lists, and valid
    inspiration records.

- [x] Treat non-text direct mutation payloads as a paper-level parser contract
  gap.
  - Paper evidence: AlphaEvolve-style proposal generation treats model outputs
    as mutation text and records malformed proposals as failed samples.
  - Status: direct candidate/workspace mutation helpers now classify non-text
    payloads as `non_text_mutation_payload`; runtime and critique paths reuse
    the same diagnostic.
  - Verification: focused candidate tests cover direct `None`, numeric, and
    list payloads; loop tests cover runtime failure records and critique
    fallback behavior.

- [x] Treat non-text failure-history mutation payloads as database-fidelity
  gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the evolutionary database should retain and resurface failed
    attempts in a typed, inspectable form.
  - Status: failure-history records now store bounded non-text payload
    representations with type, text/non-text flag, and hash evidence before
    prompt resurfacing.
  - Verification: database tests cover `None`, numeric, list, and dict payloads;
    loop tests prove non-text failed proposals are persisted and rendered into
    subsequent prompt memory.

- [x] Make topology operations syntactically distinct from candidate file
  names.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Requirement: codebase-candidate mutation should distinguish file identity
    from mutation operation type.
  - Status: ordinary command-leading filenames now use `<<<FILE PATH ...`;
    topology operations remain explicit command sections.
  - Verification: focused candidate tests cover ordinary filenames beginning
    with `DELETE`, `MOVE`, and `PRIMARY`, plus real topology command sections
    already covered by the existing suite.

- [x] Reject malformed same-line mutation envelopes before claiming parser
  fidelity.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Figure 3.
  - Requirement: mutation languages should make intended edits unambiguous and
    surface malformed structured output as parser failures.
  - Status: same-line file/block envelopes are now rejected with structured
    diagnostics instead of being stored as program text.
  - Verification: focused candidate tests cover same-line file sections,
    same-line block sections, and mixed valid plus malformed envelopes.

- [x] Preserve exact full-replacement payload text.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: full-code/block replacement should preserve proposed program
    text unless normalization is explicit in the candidate API.
  - Status: full-file, file-section, and block-section full replacements now
    preserve final newlines and blank lines in accepted payload bodies.
  - Verification: focused candidate tests cover final newline, trailing
    blank-line, and no-final-newline variants across single-file, multi-file,
    and multi-block full replacement paths.

- [x] Treat SEARCH/REPLACE line-ending sensitivity as a paper-level mutation
  fidelity gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3.
  - Requirement: mutation application should be robust and reproducible for
    codebases authored on different platforms.
  - Status: SEARCH/REPLACE now matches through an LF-normalized view and writes
    replacements back with the matched candidate span's dominant line ending.
  - Verification: focused diff/candidate tests cover CRLF candidates with LF
    patches, mixed line endings, evolve-block-restricted diffs, and workspace
    file sections.

- [x] Make full-block replacement grammar independent of block count.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: evolvable code blocks should be targetable with an
    unambiguous output format.
  - Status: named block-section payloads now apply consistently to one-block
    and multi-block candidates; one-block raw-body shorthand remains
    backward-compatible.
  - Verification: focused candidate tests cover one-block named sections,
    unknown names, multi-block sections, and workspace file-section routing.

- [x] Disambiguate full-file versus full-block output modes inside workspaces.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: full-codebase mutation should make the requested replacement
    unit explicit.
  - Status: full-mode file sections are documented and prompted as complete
    replacements only for files without evolve blocks; evolve-blocked files use
    raw or named block payloads inside the file section.
  - Verification: focused prompt tests assert the instruction text, and
    candidate tests cover one-block and multi-block workspace file sections.

- [x] Account for the whole LLM mutation response.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.3.
  - Requirement: AlphaEvolve prompts the LLM for a concrete program edit; the
    mutation parser should know which response parts were applied or rejected.
  - Status: file-section, plain SEARCH/REPLACE, and block-section parsers now
    reject non-whitespace/non-metadata text outside recognized mutation
    sections instead of silently dropping it.
  - Validation: focused candidate and diff tests cover leading prose, trailing
    prose, stray diff/block/file payloads, accepted proposal metadata, and
    multi-block skeleton preservation.

- [x] Keep seed roots inside the problem package.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: the initial population and task setup should be reproducible
    from the declared problem package.
  - Status: linked `initial_programs/` roots are rejected before seed loading,
    matching the existing linked-child seed policy.
  - Validation: focused loader tests cover deterministic root-link detection
    and real directory symlink roots when supported by the platform.

- [x] Treat unsafe evolve-block names as a paper-level representation gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: evolvable-region labels should be stable, auditable, and safe
    to render in prompts, mutation payloads, history, and exports.
  - Status: source evolve-block names and named block-section targets reject
    secret-like and Unicode format-control labels before seed loading or
    mutation application.
  - Validation: focused candidate and loader tests cover secret-like labels,
    Unicode format controls, current ASCII-only non-ASCII policy, and safe
    marker names.

- [x] Treat workspace materialization failures as evaluated/rejected
  candidates.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Table 1 and Sections 2.1/2.5.
  - Requirement: full-codebase evolution needs robust handling for invalid
    generated codebase states with database-visible diagnostics.
  - Status: materialization failures are classified as invalid evaluations
    rather than infrastructure aborts, preserving failed generated workspaces in
    history/failure memory with bounded diagnostics.
  - Validation: focused evaluator and loop tests cover case-folded host
    collisions, failure-history persistence, completed runtime state, and run
    directory artifact boundaries.

- [x] Treat non-finite CausalPlugin state as a paper-level causal-guidance
  gap.
  - Paper evidence: CausalEvolve-style guidance should not feed malformed
    outcome evidence back into future LLM prompts.
  - Status: CausalPlugin rejects malformed/non-finite scores before state
    mutation and quarantines malformed restored history before rendering prompt
    context.
  - Validation: focused causal-plugin tests cover `nan`, infinities, strings,
    booleans, valid finite scores, non-rendering of `delta=+nan`, and
    quarantine counters for restored malformed history.

- [x] Treat direct evaluator contract-preflight bypass as a paper-level
  evaluator fidelity gap.
  - Paper evidence: AlphaEvolve-style evaluation relies on well-defined task
    evaluator contracts; unsupported evaluator signatures should not become a
    separate accepted execution path.
  - Status: direct `CascadeEvaluator.evaluate()` enforces the same default and
    staged validator preflight contract as CLI/`evolve()` evaluation before
    validator subprocess execution.
  - Validation: focused evaluator tests cover valid direct signatures,
    missing `evaluate`, variadic signatures, keyword-only required parameters,
    async/generator validators, and configured-stage contract rejection.

- [x] Preserve fence-like code literals during mutation parsing.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Figure 3.
  - Requirement: mutation parsing should preserve the intended replacement code
    while tolerating common response-envelope formatting.
  - Status: markdown fence cleanup is now boundary-aware: a single whole-response
    wrapper is stripped, while fence-like text inside replacement code remains
    candidate content.
  - Validation: focused parser tests cover full-file, file-section,
    block-section, and SEARCH/REPLACE mutations containing triple-backtick
    literals, plus an outer fenced SEARCH/REPLACE response.

- [x] Preserve marker-like code literals during file/block mutation parsing.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.3 and Table 1.
  - Requirement: full-file/full-codebase evolution should preserve arbitrary
    source text while identifying the intended edit envelope.
  - Status: file/block mutation envelopes are parsed as line-start markers, so
    marker-like strings embedded in ordinary replacement code lines no longer
    become nested/orphan envelope diagnostics.
  - Validation: focused parser tests cover literal `<<<FILE`, `>>>FILE`,
    `<<<BLOCK`, and `>>>BLOCK` text in SEARCH/REPLACE, full-file, file-section,
    and block-section replacements.

- [x] Make validator preflight obey the evaluator execution boundary.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.4.
  - Requirement: evaluator validation is part of task setup and should be
    auditable under the same safety/provenance assumptions as evaluator
    execution.
  - Status: validator preflight import/signature checks now run in a bounded
    subprocess with temporary cwd and validator env allowlist, instead of
    importing validator modules in the parent CLI/runtime process.
  - Validation: focused evaluator tests cover parent env isolation, temp-cwd
    side effects, allowlisted env visibility, slow-import timeout, and retained
    contract diagnostics for unsupported evaluator signatures.

- [x] Make evaluator result transport faithful to authoritative return values.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.5.
  - Requirement: the evaluator's score dictionary is the authoritative result
    for a candidate; program output and diagnostics should not be able to
    replace returned metrics accidentally.
  - Status: validator return values now travel through a dedicated runner-owned
    JSON result file, while stdout/stderr are retained only as diagnostics.
    Misleading validator or child-process stdout can no longer replace the
    returned score dictionary.
  - Validation: focused evaluator tests cover validator stdout JSON, inherited
    child stdout JSON printed after return, and non-JSON-serializable validator
    returns.

- [x] Preserve evaluator metric-key fidelity through result transport.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.5.
  - Requirement: evaluator-provided score dictionaries should remain faithful
    until the metric schema validates or rejects them.
  - Status: the runner now rejects top-level non-string evaluator result keys
    before JSON serialization and records a malformed-metrics diagnostic with
    reason `non_string_keys`. Malformed metric diagnostics are persisted with
    bounded redacted messages rather than relying on stdout.
  - Validation: focused evaluator tests cover direct non-string keys,
    boolean/null-like keys, configured-stage samples/retries, and serializer
    failures for object, set, bytes, NumPy scalar, and NumPy array payloads.

- [x] Redact prompt-visible parent and inspiration metric payloads.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: evolutionary database context in prompts should expose useful
    candidate score evidence without leaking arbitrary direct, plugin, or
    restored metadata.
  - Status: parent and inspiration metric rendering now redacts and bounds
    metric keys/values, orders declared metrics first, and renders non-finite
    metric values as explicit typed markers. Full declared-schema enforcement
    and metric direction/bounds semantics remain tracked as open paper-fidelity
    items.
  - Validation: focused prompt tests cover secret-like parent and inspiration
    metric keys/values, nested payloads, long strings, declared metric
    ordering, and non-finite markers.

- [x] Preserve metric semantics when rendering score feedback to prompts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.2, and 2.4.
  - Requirement: prior program scores shown to the mutation LLM should be
    interpretable evaluator feedback, including LibreEvolve's minimize metrics
    and declared bounds.
  - Status: prompt-visible declared metrics for parent and inspiration
    candidates now include primary/secondary role, direction, bounds,
    normalized value, out-of-range diagnostics, separate validity status, and
    explicit feedback-adjusted-fitness labeling.
  - Validation: focused prompt tests cover maximize/minimize directions,
    bounds, normalized values, primary and secondary metrics, out-of-range
    candidates, feedback-adjusted fitness, validity, and inspiration programs.

- [x] Keep prompt-visible parent and inspiration fitness finite.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: program scores shown to the LLM should be comparable
    evaluation evidence from the evolutionary database, or clearly marked as
    invalid legacy/restored records.
  - Status: prompt-visible parent and inspiration score fields now render
    finite normalized values when possible and typed invalid markers for
    malformed `nan`, `inf`, `-inf`, boolean, string, and `None` values without
    crashing prompt construction.
  - Validation: focused prompt tests cover parent and inspiration invalid
    score markers, valid finite scores, restored post-construction values, and
    custom parent-score numeric format specs.

- [x] Render explicit problem context in LLM feedback-grader prompts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.4, and 2.6.
  - Requirement: reviewer/evaluator feedback should judge candidates against
    the same problem-local constraints and context that shaped generation.
  - Status: LLM feedback prompts now include bounded explicit problem context
    with source provenance, redaction, truncation, and context-budget omission
    notices.
  - Validation: focused feedback tests cover context source names, hashes,
    page spans, context text, sensitive text redaction, truncation, and budget
    omission.

- [x] Preserve unknown stage status in paper-level prompt-feedback claims.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: execution feedback shown to later LLM proposals should be
    faithful evidence from the evaluator/database, not a lossy status rewrite.
  - Status: prompt-visible stage and retry/sample attempt summaries now render
    tri-state `passed`, `failed`, or `unknown` labels, preserving missing,
    restored, and malformed statuses as unknown instead of failed.
  - Validation: focused prompt tests cover missing `passed`, `passed: None`,
    malformed status values, explicit failure, and retry/sample attempt
    summaries.

- [x] Render selected inspiration-program feedback in mutation prompts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figures 1 and 2 plus Section 2.2.
  - Requirement: the prompt sampler uses programs from the program database as
    rich context, including quality scores and other feedback.
  - Status: selected inspiration programs now render bounded/redacted
    evaluator/stage/output/LLM feedback summaries when available, rather than
    only code, proposal metadata, and metric values.
  - Validation: focused prompt tests cover inspiration stage diagnostics,
    stdout/stderr, LLM grader feedback, redaction, and truncation.

- [x] Make artifact-limit diagnostics prompt-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompt feedback should faithfully communicate evaluator
    evidence and omissions without bypassing the system's prompt redaction
    policy.
  - Status: skipped evaluator-artifact diagnostics are now rendered through
    bounded/redacted prompt-safe formatting, including skipped-only events and
    copied-plus-skipped artifact events. Raw Python `repr()` rendering of
    skipped artifact lists is no longer used.
  - Validation: focused prompt tests cover copied and skipped artifact paths,
    max-file/max-byte style skip reasons, SHA summaries, redaction markers, and
    absence of secret-like path fragments in mutation prompts.

- [x] Add first character-level mutation prompt budget.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Requirement: prompt construction should remain bounded as code, evaluator
    feedback, literature, and failed-trial memory accumulate.
  - Status: `prompt_max_chars` now caps final rendered mutation prompts before
    provider calls, preserves the task/mutation-instruction section when
    possible, and records prompt-size diagnostics in generated program history
    plus the run manifest. This is a character-level fallback, not full
    token-aware context-window packing.
  - Validation: focused prompt and loop tests cover direct truncation,
    preserved mutation instructions, pre-LLM prompt size, persisted
    diagnostics, and manifest config.

- [x] Make legacy tuple failed-trial memory prompt-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.6.
  - Requirement: failed trials used as prompt context should be bounded,
    attributable, and safe to persist/render as part of the evolutionary
    database.
  - Status: legacy `(code, score)` recent-failure records now render through
    the same bounded/redacted snippet path used by prompt feedback helpers,
    covering secret-like text, newline escaping, and long snippets.
  - Validation: focused prompt tests cover legacy tuple redaction, truncation,
    newline escaping, and absence of long repeated payloads.

- [x] Preserve prompt section boundaries for candidate code containing
  delimiter-like text.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.3.
  - Requirement: prompts include prior programs that guide the next LLM
    proposal; program representation should keep code boundaries unambiguous
    even when source files contain arbitrary strings.
  - Status: parent and inspiration programs now render as typed workspace file
    records with JSON-escaped content and character counts instead of markdown
    code fences. Single-file non-Python workspaces preserve path metadata and
    are not labeled as Python code blocks.
  - Validation: focused prompt tests cover parent and inspiration workspaces,
    embedded triple backticks, fake file headers, multi-file candidates, and
    single-file non-Python candidates.

- [x] Preserve prompt section boundaries for explicit context bodies
  containing delimiter-like text.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.3.
  - Requirement: prompts include task context that guides the next LLM
    proposal; context representation should keep boundaries unambiguous even
    when source files contain arbitrary strings.
  - Status: explicit context bodies now render as character-counted JSON
    strings under source citation headers, so triple backticks, fake `[TASK]`
    headers, and fake source headers remain context payload text.
  - Validation: focused prompt tests cover delimiter-like explicit context
    bodies and preserve source citation metadata.

- [x] Treat non-deterministic direct context ordering as a prompt-fidelity gap.
  - Requirement: AlphaEvolve-style prompt construction should make the evidence
    shown to models reproducible; context ordering is part of the prompt and can
    affect model behavior.
  - Status: `_render_context()` now path-sorts direct and loader-created
    context entries before prompt rendering.
  - Validation: focused prompt tests cover direct maps with reversed insertion
    order rendering in canonical path order.

- [x] Treat unvalidated context citation metadata as a paper-level prompt
  provenance gap.
  - Paper evidence: AlphaEvolve-style prompt context and literature references
    should be reproducible and attributable; citation metadata rendered to the
    LLM is part of the experimental prompt.
  - Status: context citation headers now normalize/redact direct and
    loader-generated display metadata before prompt insertion, including source
    labels, SHA/status fields, excerpt spans, character counts, and PDF page
    spans.
  - Validation: focused prompt tests cover normal loader-style records plus
    direct/mutated records with secret-like metadata, newline status injection,
    negative offsets, and malformed page spans.

- [x] Validate rendered plugin context before treating paper-inspired guidance
  as prompt-safe evidence.
  - Paper evidence: paper-inspired retrieval, causal, modular, and training
    plugins can affect prompt context or downstream selection, so their
    prompt-visible output needs a reproducible, bounded, redacted, and
    attributable contract.
  - Status: plugin prompt guidance now accepts only text/`None`, rejects object
    returns, redacts and caps emitted text, serializes it as JSON-string prompt
    evidence, and persists exact size/hash plus redaction/truncation
    diagnostics.
  - Validation: focused loop tests cover normal guidance, object-return
    rejection, secret-like payload redaction, oversized payload truncation,
    prompt rendering, and persisted metadata consistency.

- [x] Preserve prompt section boundaries for feedback containing
  delimiter-like text.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 2.3.
  - Requirement: prompts include prior programs, proposal context, evaluator
    feedback, and local context that guide the next LLM proposal; the
    representation should keep boundaries unambiguous even when those records
    contain arbitrary strings.
  - Status: evaluator stage summaries, stdout/stderr/error snippets,
    retry/sample diagnostics, artifact diagnostics, LLM grader feedback, and
    proposal metadata now serialize dynamic values as JSON strings in prompt
    feedback sections after redaction/truncation.
  - Validation: focused prompt tests cover feedback records containing fake
    `[TASK]`, `[EXTRA CONTEXT]`, file-header, and markdown-fence delimiters.

- [x] Enforce a schema for prompt-visible program metrics.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: AlphaEvolve-style prompts use the evolutionary database as
    structured context for parent and inspiration candidates; prompt-visible
    metrics should preserve meaningful score evidence without leaking
    arbitrary metadata or malformed restored/plugin payloads.
  - Status: parent and inspiration prompt metric summaries now use the problem
    schema as the default allowlist, plus `is_valid`,
    `feedback_adjusted_fitness`, and manifest-safe LLM feedback metric names
    recorded in `evaluation.metadata.llm_feedback`. Undeclared plugin/restored
    metrics are kept out of mutation prompts until a broader runtime extension
    metric contract is implemented.
  - Validation: focused prompt tests cover filtering undeclared metric keys and
    values for both parent and inspiration candidates while preserving declared
    metric semantics and explicit feedback metrics; a loop regression verifies
    the persisted mutation prompt in `history.jsonl` follows the same policy.

- [x] Treat unsafe runtime metric names as a paper-level multi-metric
  provenance gap.
  - Paper evidence: AlphaEvolve-style multi-objective search relies on metric
    identifiers being stable, auditable, and safe to expose in prompts,
    histories, and experiment summaries.
  - Status: direct and runtime `Program.metrics` keys now use the same
    manifest-safe metric-name grammar as declared problem metrics, with
    optional dotted namespaces. Unsafe keys are rejected during direct program
    construction, quarantined before history writes, rejected before archive
    insertion, and reverted when introduced by plugin score hooks.
  - Validation: focused program tests cover secret-like metric keys, Unicode
    format controls, non-NFC Unicode, bad dotted names, and safe dotted
    namespaces; database tests cover history and archive boundaries; loop tests
    cover plugin-added metric keys.

- [x] Treat direct raw duplicate archive ids as a paper-level evolutionary
  database integrity gap.
  - Paper evidence: AlphaEvolve-style archives and evolutionary databases rely
    on candidate identity for lineage, parent selection, replay, and analysis
    of which program state occupied which search cell.
  - Status: direct raw `ProgramDatabase.add()` / `admit()` now reject duplicate
    archive ids before mutating island/MAP-Elites state, including duplicate
    ids across islands and conflicts with a different logged object.
    Migration/resume clone/reference semantics remain an open paper-level
    database fidelity item.
  - Validation: focused database tests cover duplicate raw add, duplicate
    admit across islands, logged-id conflict rejection, and the supported
    same-object log-then-admit path.

- [x] Treat invalid-encoding history inspection as a paper-level run-artifact
  provenance gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: evaluated-program histories should remain inspectable as
    experiment evidence, including when corrupted artifacts are encountered.
  - Status: the `show` reader now decodes `history.jsonl` line-by-line from
    bytes and converts invalid UTF-8 into line-numbered malformed-history
    diagnostics before JSON parsing. Resume/replay decoding remains an open
    paper-level provenance item.
  - Validation: focused CLI tests cover invalid bytes on the first line and
    after a valid history row, plus existing streaming and schema diagnostics.

- [x] Treat permissive accepted-history id inspection as a paper-level database
  identity gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: accepted program records should have unambiguous,
    manifest-safe identities for archive reconstruction, lineage, prompt reuse,
    and later experiment analysis.
  - Status: `libreevolve show` now validates streamed history ids with
    `validate_program_identity()` and rejects duplicate ids with the first-seen
    line number before best-row selection. Future resume/database restore
    policies remain open paper-level items.
  - Validation: focused CLI tests cover duplicate legacy/current ids and unsafe
    unselected current-history ids containing newline/control, secret-like, and
    Unicode format-control text.

- [x] Treat permissive `show` metric rendering as a paper-level artifact
  validation gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: experiment histories and database records should provide
    reliable, machine-readable metric evidence for selection, analysis, and
    later prompting.
  - Status: `libreevolve show` now validates every streamed history `metrics`
    object with the runtime metric policy and renders selected metrics with
    strict JSON. Non-finite values, booleans outside `is_valid`, and unsafe
    metric names fail with line-numbered diagnostics.
  - Validation: focused CLI tests cover legacy/current invalid metrics,
    unselected malformed metric rows, unsafe metric keys, and valid strict JSON
    rendering.

- [x] Make run-history inspection enforce workspace path safety before using it
  as AlphaEvolve evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: recorded programs and codebase candidates should be
    inspectable as valid task artifacts, and corrupt histories should not be
    displayed as if they were normal candidate workspaces.
  - Status: `libreevolve show` now validates selected history workspace paths
    by constructing a `CandidateWorkspace`, reusing the candidate path grammar
    before display.
  - Validation: focused CLI tests cover traversal, absolute, hidden,
    bidi-control, overlong, duplicate-normalized, and valid Unicode workspace
    paths.

- [x] Make archive-admission display enforce coherent search-state semantics
  before using it as AlphaEvolve evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Requirement: archive-admission metadata should be structured enough for
    reliable database inspection, archive reconstruction, and future resume,
    and retained rows should not be selected from contradictory flags.
  - Status: `libreevolve show` rejects non-object archive-admission payloads and
    admitted rows whose explicit archive-state flags say no cell admission, no
    elite retention, no search-state change, and no sampling eligibility.
  - Validation: focused CLI tests cover malformed archive payloads, coherent
    cell/elite rows, non-admitted rows, and contradictory admitted rows.

- [x] Treat malformed current-history evaluation payloads as paper-level
  inspection evidence gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: inspected program histories should preserve structured
    evaluator evidence, including a clear validity field, before they are used
    as AlphaEvolve-style database records.
  - Status: `libreevolve show` now rejects non-object current-history
    `evaluation` payloads and non-boolean `evaluation.is_valid` values with
    line-numbered malformed-history diagnostics.
  - Validation: focused CLI tests cover non-object evaluation payloads,
    non-boolean `is_valid`, missing-validity compatibility, and valid retained
    rows.

- [x] Surface malformed unselected archive rows before using `show` output as
  archive evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: an AlphaEvolve-style evolutionary database should support
    inspectable program histories and reliable archive provenance across the
    run, not only the final selected candidate.
  - Status: `libreevolve show` now validates current-history archive diagnostic
    fields while streaming, so malformed lower-scoring retained archive rows
    fail before selected-best output is printed.
  - Validation: focused CLI tests cover a valid selected row plus malformed
    unselected retained archive diagnostics.

- [x] Validate MAP-Elites cell coordinate shape before using displayed cells as
  paper-alignment evidence.
  - Paper: `1504.04909__MAP_Elites.pdf` and
    `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: archive diagnostics should represent real behavior-cell
    coordinate shape, not arbitrary persisted coordinate lists.
  - Status: displayed current-history cells must be exactly three non-negative
    integer coordinates. Manifest/config-derived upper-bound checks remain
    open.
  - Validation: focused CLI tests cover malformed and valid cell coordinates,
    including malformed unselected retained rows.

- [x] Treat raw archive descriptor-label display as a MAP-Elites diagnostics
  gap and close the label-safety portion.
  - Paper: `1504.04909__MAP_Elites.pdf` and
    `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: archive descriptors should be meaningful behavior metadata,
    not arbitrary persisted labels echoed as trusted diagnostics.
  - Status: `show` now validates descriptor labels with the manifest-safe
    metric-name grammar before display and rejects secret-like, control,
    malformed, and reserved descriptor labels with line-numbered diagnostics.
    Large descriptor maps are covered by the follow-on completed
    descriptor-budget item.
  - Validation: focused CLI tests cover default-style descriptors,
    intentionally user-defined dotted labels, secret-like labels, and corrupt
    unselected current-history rows.

- [x] Treat unbounded archive descriptor display as a MAP-Elites diagnostics
  gap and close the CLI display-budget portion.
  - Paper: `1504.04909__MAP_Elites.pdf` and
    `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: archive descriptor diagnostics should be compact, bounded,
    and inspectable while full vectors remain available through deliberate
    machine-readable artifacts.
  - Status: `show` now summarizes large descriptor maps and long descriptor
    labels with count, bounded preview, omitted count, and stable hash. The
    full vector remains in `history.jsonl`.
  - Validation: focused CLI tests cover normal small output, 500 descriptors,
    long descriptor labels, preview omission, and bounded terminal output.

- [x] Track paper-alignment evidence for bounded run inspection.
  - Paper evidence: AlphaEvolve-scale runs can produce large codebase
    candidates and experiment artifacts, so human inspection surfaces need
    summaries and pointers rather than unconditional source dumps.
  - Status: `show` now truncates oversized selected legacy source and workspace
    file bodies, reports truncation metadata and source hash, and points to
    `history.jsonl` for the full source retained by the run history.
  - Validation: focused CLI tests cover large single-string code plus
    multi-file candidate histories with oversized primary and secondary files.

- [x] Treat evaluator preflight diagnostic redaction as paper-level runtime
  evidence.
  - Paper evidence: AlphaEvolve-style experiments depend on repeatable,
    inspectable validator setup, but setup diagnostics should not leak local
    credential-bearing paths when shared with collaborators or CI systems.
  - Status: evaluator preflight diagnostics now use safe problem-relative or
    outside-problem path labels plus path hashes for default and configured
    validator paths.
  - Validation: focused CLI/evaluator tests cover a default validator under a
    secret-like problem root, configured-stage outside paths, and missing
    problem-local validators without leaking the raw secret-like path.

- [x] Treat run-directory containment diagnostics as paper-level artifact
  safety evidence.
  - Paper evidence: long-running AlphaEvolve-style experiments need reliable
    artifact-root containment, and shared setup diagnostics should not leak
    local credential-bearing paths.
  - Status: run-directory containment, existing-artifact, and linked-artifact
    setup failures now expose path scope and stable path hashes without printing
    raw absolute roots. The implementation preserves containment rejection
    before overwrite cleanup for symlink/junction escape cases.
  - Validation: focused database and CLI tests cover containment failures,
    symlink/junction run-directory escapes, linked run artifacts, existing
    artifacts, absolute log roots, and secret-like path redaction.

- [x] Treat seed/generated generation ambiguity as a paper-level database gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: history now distinguishes baseline seed rows from generated search
    rows: seeds persist as generation `0`, generated candidates start at
    generation `1`, and generated metadata retains the zero-based internal loop
    index. The paper index records this as implemented AlphaEvolve-alignment
    evidence while resume/archive persistence remain open separately.
  - Validation: focused loop tests cover seed-only baseline rows,
    first-generated-child rows, plugin generation hooks, prompt-result
    metadata, and generation-cadence artifact behavior.

- [x] Define ThetaEvolve-inspired export cadence relative to generation ids.
  - Paper evidence: ThetaEvolve-style training-data collection should make
    update cadence and exported-example timing explicit enough to compare runs.
  - Status: the implemented cadence is based on completed mutation-generation
    counts starting at `1`; `train_every=1` exports after the first completed
    generation, while non-multiple short runs remain pending and manifest
    visible. Pending-finalization and invalid-record progress remain separate
    open gaps.
  - Validation: focused loop/plugin tests cover `train_every=1`,
    `train_every=2`, non-multiple short runs, export cursors, and manifest
    queued/pending/exported counts.

- [x] Attribute DeepResearch prompt context across empty or failed refreshes.
  - Paper evidence: DeepEvolve-style retrieval is an input to debugging and
    refinement; injected external context should be traceable to the retrieval
    event that produced it, or explicitly cleared when no current synthesis is
    available.
  - Status: the plugin now clears prompt-visible synthesis after empty/error
    refreshes. Successful refreshes replace the active context and expose
    source generation plus synthesis hash through `active_context` metadata.
    Full retrieval cache/replay and transport-integrity work remain open.
  - Validation: focused DeepResearch tests cover ok-to-empty, ok-to-error,
    ok-to-new-result, and active-context metadata.

- [x] Keep DeepEvolve-inspired retrieval metadata finite.
  - Paper evidence: DeepEvolve-style retrieval context is part of the
    refinement trajectory, so recorded retrieval inputs should be valid
    experiment state rather than malformed scalar values.
  - Status: non-finite or nonnumeric best-program fitness now creates a
    structured skipped retrieval event without provider calls, query text, or
    non-finite `best_fitness`; valid finite fitness is persisted as a float.
    Replayable retrieval snapshots remain open.
  - Validation: focused DeepResearch tests cover `nan`, `inf`, `-inf`, string,
    bool, `None`, and valid finite best-fitness metadata.

- [x] Make DeepEvolve-inspired retrieval request URLs provenance-safe.
  - Paper evidence: retrieval-driven refinement treats provider requests and
    returned context as experiment inputs, but durable evidence should not
    preserve credentials, account identifiers, or private query parameters as
    raw prompt/run metadata.
  - Status: provider `query_url` fields are persisted as hash-backed
    `request_url` summaries with scheme, host, path, query-parameter count, and
    omission/redaction diagnostics. Raw request URLs and query values are not
    persisted in candidate history; transport integrity remains open.
  - Validation: focused DeepResearch and loop tests cover default arXiv URLs,
    custom URLs with secret query parameters, candidate history, and run
    manifest output.

- [x] Validate DeepEvolve-inspired arXiv retrieval parameters.
  - Paper evidence: paper-aligned live retrieval should expose a validated,
    reproducible provider-query contract before it is used as prompt context or
    run provenance.
  - Status: direct arXiv helper calls now validate non-empty safe query text
    plus bounded integer `max_results` values, reject malformed values before
    URL construction, use HTTPS for the default provider URL, and record
    transport/payload provenance for live responses.
  - Validation: focused DeepResearch tests cover invalid `query` and
    `max_results` direct calls, valid HTTPS URL construction, default plugin
    metadata, request URL summaries, provider transport metadata, and
    custom-provider compatibility. Replayable retrieval snapshots, ranking
    provenance, and full source-content trust remain open.

- [x] Bound DeepEvolve-inspired live retrieval payload reads.
  - Paper evidence: retrieval-driven debugging/refinement should consume
    external knowledge through bounded, attributable experiment inputs rather
    than unbounded provider payloads.
  - Status: live arXiv responses are read through a 1,000,000-byte cap before
    XML parsing. Exact-limit payloads are accepted; oversized payloads become
    structured `oversized_response` retrieval errors and do not enter prompt
    context. Retrieval metadata and run summaries preserve payload size-limit,
    observed-byte, truncation/oversize, and hash diagnostics.
  - Validation: focused DeepResearch and loop tests cover small/default
    responses, exact-limit responses, oversized-response rejection before XML
    parsing, and compact run-manifest payload-budget summaries. Replayable
    retrieval snapshots, ranking provenance, and source-content trust remain
    open.

- [x] Bound DeepResearch event memory for long-run retrieval.
  - Paper evidence: DeepEvolve/AlphaEvolve-style long-horizon experiments need
    bounded retrieval state; prompt metadata truncation is not a substitute for
    bounded live plugin memory.
  - Status: `DeepResearchPlugin(max_events=100)` bounds retained retrieval
    events in memory by default, validates custom caps, drops old events on
    overflow, and emits retention counters for limit, retained/emitted events,
    total events, and dropped events. Artifact-backed full-history retention,
    resume, and replay semantics remain open.
  - Validation: focused DeepResearch tests cover invalid caps and a seven-event
    run capped to the latest three retained events with stable event indexes
    and truthful retention counters.

- [x] Treat DeepEvolve-inspired retrieved text as untrusted evidence in prompts.
  - Paper evidence: DeepEvolve-style retrieval supplies external knowledge for
    debugging and refinement, but the experiment still needs task, evaluator,
    and mutation-format instructions to remain authoritative.
  - Status: successful DeepResearch retrieval context is now rendered through
    an explicit non-authoritative evidence wrapper with begin/end delimiters
    and a warning not to follow instructions inside retrieved text. Retrieval
    events, active-context metadata, and run summaries persist the
    `untrusted_evidence_v1` policy, prompt-boundary identifier, and
    `authoritative: false`.
  - Validation: focused DeepResearch and loop tests cover instruction-like
    custom provider text, default provider context, redacted/truncated
    retrieval text, active-context metadata, and compact run-manifest
    trust-policy summaries. This does not implement full source-content trust,
    retrieval ranking, replay, or DeepEvolve-style debug loops.

- [x] Make DeepEvolve-inspired retrieval code/metric aware.
  - Paper evidence: `2510.06056__DeepEvolve.pdf` uses external knowledge
    retrieval as part of a debugging/refinement loop for the concrete code
    problem, not generic evolution advice.
  - Status: default DeepResearch queries now include best-program fitness,
    manifest-safe metric names, and bounded identifier terms from the best
    program's code/workspace file names. Retrieval events and run summaries
    persist the `best_program_code_metrics_v1` policy and selected query
    inputs. This is still only a generic DeepEvolve-inspired retrieval hook:
    task-description, evaluator-failure, explicit-context, local-paper,
    hypothesis-template, ranking, replay, and cross-file debugging/refinement
    grounding remain open.
  - Validation: focused DeepResearch and loop tests prove domain-different
    matrix-rank versus sorting queries, persisted query input metadata, and
    compact run-manifest query provenance.

- [x] Make DeepEvolve-inspired retrieval source metadata prompt/provenance safe.
  - Paper evidence: DeepEvolve-style retrieval provenance should identify
    sources and support auditability without persisting arbitrary provider text
    as trusted experiment metadata.
  - Status: retrieval sources from default and custom providers are normalized
    into bounded, redacted provenance records with retained/dropped counts,
    field caps, source summary hashes, per-source redaction/truncation flags,
    omitted-field accounting, and compact run-summary diagnostics. Full source
    content trust, source ranking, replayable snapshots, and DeepEvolve-style
    debug/refinement behavior remain open.
  - Validation: focused DeepResearch and loop tests cover custom secret-bearing
    source metadata, truncation, dropped sources, default arXiv source metadata,
    prompt-context metadata, and runtime-summary source diagnostics.

- [x] Add replayable retrieval snapshots for DeepEvolve-inspired context.
  - Paper evidence: DeepEvolve-style external knowledge affects the debugging
    and refinement trajectory, so experiments need a replayable record of the
    context that shaped each prompt, not only a statement that a provider was
    queried.
  - Status: DeepResearch now stores normalized retrieval snapshots keyed by
    provider/query/query-policy, reuses identical cached queries, persists JSON
    snapshots when a cache directory is configured, and supports offline
    cache-only replay with structured cache-miss diagnostics. CLI-loaded
    DeepResearch uses `plugin_artifacts/deep_research/`. Full provider payload
    persistence, source-content trust, ranking provenance, full run resume, and
    DeepEvolve-style debug/refinement loops remain open.
  - Validation: focused DeepResearch and loop tests cover in-memory cache
    reuse, disk snapshot creation, offline replay without provider calls,
    offline cache misses, and compact run-manifest cache summaries.

- [x] Make paper-inspired plugin hook failures attributable in aborted runs.
  - Paper evidence: AlphaEvolve-style systems run long automated experiments;
    optional retrieval, guidance, critique, score, or export components need
    attributable failures so they do not masquerade as candidate or evaluator
    failures.
  - Status: LibreEvolve now defines current plugin hook failures as fatal run
    aborts for `on_generation_start`, `build_extra_context`,
    `prompt_context_metadata`, `on_evaluated`, `run_artifacts_metadata`, and
    `on_generation_end`. The core loop preserves and re-raises the original
    exception while persisting plugin name/module/index, hook, policy,
    generation, parent/candidate ids where available, exception type/message,
    redaction/truncation diagnostics, and `continued: false` in aborted
    manifests. This is failure attribution, not non-fatal plugin continuation.
  - Validation: focused loop tests cover every hook category, redacted bounded
    plugin abort messages, and artifact-metadata finalization failures.

- [x] Make paper-inspired plugin artifact provenance authoritative and visible
  on aborted runs.
  - Paper evidence: retrieval, training-data, and other auxiliary artifacts are
    experimental inputs/outputs for paper-inspired components; manifests should
    attribute them to the actual component implementation and preserve partial
    evidence from failed long runs.
  - Status: plugin artifact records now use runtime-derived plugin identity
    plus nested validated metadata, so plugin-supplied `plugin` fields cannot
    spoof top-level attribution. Non-mapping non-empty
    `run_artifacts_metadata()` returns are diagnosed instead of silently
    dropped. Aborted manifests attempt validated artifact summaries and record
    `plugin_artifact_failures` when summary collection fails, without hiding
    the original abort.
  - Validation: focused loop tests cover spoofed artifact metadata, malformed
    top-level returns, empty returns, valid nested mappings, TTTRL nested
    artifact summaries, partial artifacts written before abort, and malformed
    abort-finalization summaries.

- [x] Preserve partial plugin artifact provenance on aborted runs.
  - Paper evidence: AlphaEvolve-scale experiments need durable evidence from
    failed or interrupted runs, including auxiliary retrieval/training/export
    outputs that may explain why a run failed.
  - Status: aborted manifests now preserve validated wrapped
    `runtime.plugin_artifacts[]` summaries when plugin artifact metadata hooks
    succeed after an abort. If the summary hook or schema fails during abort
    finalization, the manifest records `runtime.plugin_artifact_failures[]`
    without hiding the original abort exception.
  - Validation: focused loop tests cover an artifact written before a plugin
    abort and a malformed artifact summary during abort finalization.

- [x] Treat non-mapping plugin artifact metadata drops as a paper-level
  artifact schema gap.
  - Paper evidence: AlphaEvolve-style plugin or paper-inspired extensions that
    emit artifacts need stable, inspectable run records rather than best-effort
    ad hoc metadata.
  - Status: non-mapping non-empty `run_artifacts_metadata()` returns are no
    longer silently dropped. Completed runs fail with structured plugin
    provenance, while aborted finalization records a
    `plugin_artifact_failures[]` diagnostic. `None` and `{}` are explicit
    no-artifact returns.
  - Validation: focused loop tests cover list, string, scalar, `None`, empty
    dict, and valid nested mapping returns.

- [x] Give paper-inspired plugin instances stable provenance identities.
  - Paper evidence: auxiliary components such as retrieval guidance, causal
    scoring, and training-data export can affect candidate selection and run
    artifacts; repeated or differently configured components need separable
    provenance to support paper-style ablations and replay.
  - Status: startup provenance, prompt context, score composition, artifact
    manifests, and plugin-failure records now carry a shared run-local
    `instance_id` plus plugin class/module/index identity. This distinguishes
    repeated same-class plugin instances while leaving future constructor/config
    snapshots as separate provenance work.
  - Validation: focused provenance and loop tests cover two same-class plugins
    with different score deltas and matching ids across manifest and history
    records.

- [x] Validate explicit plugin objects before treating them as paper-inspired
  extension components.
  - Paper evidence: plugin claims for CausalEvolve-, DeepEvolve-,
    ImprovEvolve-, ThetaEvolve-, and TTT/RL-inspired behavior depend on
    executing well-defined plugin hooks, not arbitrary Python objects.
  - Status: direct `evolve()` plugin lists are now validated before runtime
    setup. `PluginBase` subclasses are accepted; duck-typed plugins must expose
    callable hooks required by the run mode. Invalid objects are rejected
    before startup provenance, seed history, manifest writes, or overwrite
    cleanup can record them as executed paper-inspired components.
  - Validation: focused loop tests cover invalid objects for zero-generation
    and mutation-capable direct runs, artifact preservation, valid
    artifact-only zero-generation plugins, and rejection of artifact-only
    mutation runs.

- [x] Treat non-mapping prompt-context metadata drops as a paper-level retrieval
  provenance gap.
  - Paper evidence: paper-inspired retrieval/guidance plugins should preserve
    traceable prompt-context and retrieval evidence for generated candidates and
    run summaries.
  - Status: `prompt_context_metadata()` now has a paper-visible schema:
    `None` and `{}` are empty returns, non-empty values must be mappings, and
    recursive metadata contents are validated/redacted before candidate history
    logging. Non-mapping returns now abort with plugin-failure provenance
    instead of silently dropping retrieval/plugin metadata.
  - Validation: focused loop tests cover malformed list/string/scalar/boolean
    returns, accepted empty returns, unsafe metadata labels/values, secret
    redaction, and ordinary Unicode metadata labels.

- [x] Separate prompt-injected plugin context from plugin provenance snapshots.
  - Paper evidence: paper-inspired retrieval and guidance components should
    make clear which information was actually injected into mutation prompts
    and which information was only recorded as provenance or plugin state.
  - Status: plugin-context records now explicitly distinguish prompt-visible
    rendered context from provenance-only metadata. The metadata hook remains a
    per-generation provenance hook that can run without prompt text; records
    expose `context_visibility` and `metadata_visibility` so paper/replay tools
    do not infer prompt injection from metadata presence alone.
  - Validation: focused loop tests cover emitted prompt context,
    metadata-only empty context, absence of prompt-visible context fields, and
    retrieval-only metadata that appears in manifest summaries without being
    injected into prompts.

- [x] Treat evaluator artifact confinement as part of reproducible run
  evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: stored evaluation artifacts should be bounded and attributable
    to the evaluated candidate/workspace because they become program-database
    evidence for later analysis and inspiration.
  - Status: evaluator artifact copy-out now skips matched symlinks, confines
    matched regular files to the candidate workspace, prechecks source byte
    sizes before reads, persists explicit skip reasons for unsafe or oversized
    files, and defines artifact path roots for nested/custom artifact
    directories.
  - Validation: focused evaluator tests cover pre-read max-byte enforcement,
    symlink-capable platforms, custom/nested artifact roots, and normal
    copy-out.

- [x] Make evaluator artifact selector provenance secret-safe.
  - Paper evidence: evaluator artifact selection is part of the experimental
    evidence trail, but paper-grade manifests need retention boundaries for
    credential-like configuration fields.
  - Status: LibreEvolve now rejects secret-like artifact selector patterns
    before manifest persistence instead of retaining raw sensitive-looking
    selector text. The policy applies to top-level, staged, and direct evaluator
    artifact options.
  - Validation: focused config/evaluator/database tests cover selected,
    staged, direct, and manifest-boundary sensitive-looking selectors.

- [x] Treat path-unsafe evaluator artifact selectors as an artifact provenance
  gap.
  - Paper evidence: AlphaEvolve-style evaluation artifacts should be
    attributable to the evaluated candidate/workspace and reproducible as part
    of the experiment database.
  - Status: fixed for current artifact selectors. LibreEvolve now constrains
    evaluator artifact include/exclude selectors to safe workspace-relative
    POSIX patterns, rejecting traversal, absolute roots, drive-style roots,
    leading backslashes, Windows backslashes, dot/empty components, and padded
    values before manifest persistence.
  - Validation: focused config/evaluator/database tests cover path-unsafe
    selectors at config, staged, direct, and manifest-boundary paths.

- [x] Preserve per-stage cascade metadata through successful evaluations.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4, 2.5, and 2.6.
  - Requirement: evaluated solutions should retain the scores, outputs, and
    stage evidence needed for future database resurfacing, prompt feedback,
    and compute-budget analysis.
  - Status: configured cascades now retain every configured stage's selected
    result under `evaluation.metadata.configured_stage_results[]`, including
    metrics, outputs, attempts, samples, thresholds, artifacts, validator
    environment metadata, policy metadata, and pass/stop decisions.
  - Verification: focused evaluator tests cover a successful two-stage cascade
    with per-stage artifacts and an early threshold stop, plus existing seeded
    sample and retry tests.

- [x] Treat unbounded timeout-cleanup output as a paper-level evaluator
  diagnostics gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: evaluator timeout diagnostics should remain bounded, durable,
    and useful across long-running evolutionary databases.
  - Status: `metadata.timeout_cleanup` now applies bounded cleanup-output
    retention for stdout, stderr, and fallback error text, with redaction,
    truncation, cap, stored-length, and omitted-length diagnostics.
  - Verification: focused evaluator tests cover oversized Windows taskkill
    output, taskkill failure fallback, normal taskkill output, non-Windows
    cleanup metadata, and the evaluator timeout path.

- [x] Redact serializer diagnostics in persisted quarantine streams.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: long-running program databases and quarantine streams should
    retain malformed-record diagnostics without leaking sensitive prompt,
    plugin, evaluator, or candidate payloads.
  - Status: strict JSON serializer diagnostics now apply bounded redaction to
    exception and quarantine message fields, including inline object repr text,
    while retaining the existing bounded/redacted record snapshot.
  - Verification: focused JSONL tests cover redacted manifest exceptions,
    redacted JSONL quarantine messages, oversized diagnostic bounding, cyclic
    records, deep records, and unsafe record repr handling.

- [x] Treat Python-container coercion as a replay-fidelity gap for JSON
  artifacts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: database and run artifacts should preserve enough typed state
    for reproducible inspection and future resume.
  - Status: strict JSON artifacts now reject tuple values before persistence
    instead of coercing them into JSON arrays. The policy is documented as a
    producer responsibility to emit JSON-native list values when sequence state
    is intended for replay.
  - Verification: focused JSONL tests cover tuple rejection and quarantine
    behavior for manifest, history, and prompt-history writes.

- [x] Treat unbounded evaluator stage retries as a paper-level cascade budget
  gap.
  - Paper evidence: AlphaEvolve-style evaluation cascades operate under
    explicit compute budgets and can run expensive randomized test ensembles.
  - Status: configured evaluator stage retries are no longer unbounded. The
    shared validation layer caps `eval_stages[].retries` at `10` for config and
    direct evaluator construction, and docs describe the resulting attempt
    ceiling while preserving separate open work for wall-clock budgets,
    threshold-aware retries, artifacts, and resume.
  - Verification: focused config/evaluator tests cover excessive retry
    rejection and accepted maximum retry values for both construction paths.

- [x] Define retry/pass semantics for below-threshold valid stage samples.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: staged evaluation budgets should state whether retry attempts
    are reserved for evaluator failures only or can be used when a stochastic
    valid sample fails the stage pass threshold.
  - Status: retry attempts can now be used for stage-threshold failures. When
    `min_score` is configured, locally valid below-threshold attempts are
    retried until a valid threshold-passing attempt is selected or retry budget
    is exhausted; attempt metadata preserves local validity and threshold
    decision separately.
  - Verification: focused evaluator tests cover threshold-aware retry success,
    threshold-aware retry exhaustion, and invalid-then-valid retry behavior.

- [x] Preserve metric-contract failure reasons in evaluation records.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.5.
  - Requirement: evaluated-solution records should carry useful feedback from
    the evaluator; malformed evaluator outputs should be diagnosable by task
    authors and by future prompt/database resurfacing.
  - Status: implemented. Malformed evaluator outputs now retain bounded
    `evaluation.metadata.malformed_metrics` diagnostics with machine-readable
    reasons including `missing_declared_metrics`, `undeclared_metrics`,
    `invalid_metric_type`, `invalid_is_valid`, `non_string_keys`,
    `non_mapping_result`, and serialization failures.
  - Verification: focused evaluator tests cover missing declared metrics,
    undeclared metrics, nonnumeric metrics, nonfinite/non-JSON payloads,
    invalid `is_valid`, non-string keys, and missing secondary metrics.

- [x] Treat unvalidated feedback call telemetry as a paper-level reviewer
  provenance gap.
  - Paper evidence: AlphaEvolve-style reviewer/feedback signals should preserve
    reliable provenance for which model call produced a score or discard
    decision.
  - Status: feedback reviewer call provenance is now hardened for direct/custom
    LLMs. `llm.last_call` records are strict-JSON normalized, secret-redacted,
    bounded, summarized when oversized, and stored consistently in
    `metadata.llm_feedback[].llm_call` plus the matching
    `llm_feedback:<name>` stage metadata.
  - Verification: focused feedback tests prove unsafe object values, nested
    secret-like text, oversized strings, long containers, oversized whole-call
    records, strict JSON serialization, and stage metadata parity.

- [x] Define feedback reviewer score and weight semantics before treating LLM
  feedback as paper-faithful evaluation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.4, and
    2.6, describe evaluator signals and LLM feedback as controlled inputs to
    the evolutionary search.
  - Status: reviewer scores, `weight`, and `min_score` are now finite `[0, 1]`
    values. Raw reviewer score, configured weight, and composed
    `weighted_delta` are persisted separately, and docs scope feedback-adjusted
    fitness to top-level/prompt-reward behavior rather than MAP-Elites
    declared-metric `selection_score`.
  - Verification: focused config/feedback tests cover invalid and valid
    reviewer score, weight, and threshold policies plus composition metadata.
- [x] Distinguish candidate evaluations from validator subprocess attempts.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: compute-budget comparisons should be explicit about whether a
    unit is a candidate evaluation, a test/validator sample, a retry attempt,
    or an expensive stage.
  - Status: `max_evaluations` is documented as a seed/candidate evaluation cap,
    and evaluator work units are reported separately. Each structured
    evaluation persists `accounting` with subprocess attempts,
    configured-stage samples, retry attempts, validator timeouts, and
    sample/stage budget-exhaustion counts. Candidate budget metadata and
    runtime manifests accumulate those counters through `RunBudget`.
    Independent stop criteria for those detailed counters remain open
    paper/roadmap work.
  - Verification: focused budget/evaluator/loop tests cover sampled/retried
    cascades, direct budget-accounting validation, history row accounting, and
    runtime manifest consumed counters.
- [x] Distinguish evaluator per-attempt timeouts from stage budgets.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: evaluation cascades and compute-budget accounting should make
    the cost of stage samples and retries explicit.
  - Status: implemented for the synchronous local evaluator. `timeout_sec` is
    documented and enforced per validator subprocess attempt,
    `max_sample_seconds` and `max_stage_seconds` bound sample/stage wall-clock
    time, and evaluation accounting persists subprocess attempts,
    configured-stage samples, retries, timeouts, and sample/stage
    budget-exhaustion counters.
  - Status: run-wide evaluator counter limits are now available through
    `max_evaluator_subprocess_attempts`, `max_evaluator_stage_samples`,
    `max_evaluator_retry_attempts`, `max_evaluator_timeouts`,
    `max_evaluator_sample_budget_exhaustions`, and
    `max_evaluator_stage_budget_exhaustions`. These cooperative limits stop
    the run after the evaluation that consumes the configured counter budget.
  - Verification: focused config, budget, loop, and manifest tests cover direct
    validation, stop reasons for detailed evaluator counters, persisted
    manifest config, and a staged cascade that stops before mutation generation
    after the seed consumes the subprocess-attempt budget.
- [x] Treat secret-like configured `run_id` values as paper-level run
  provenance gaps.
  - Paper evidence: AlphaEvolve-style run manifests need durable identifiers
    that can be shared as experiment provenance without leaking credential-like
    strings.
  - Status: implemented as rejection rather than redacted fallback. Generated
    UUID4 ids and safe configured ids are shareable manifest provenance ids;
    regex-valid provider-token-shaped ids are rejected at config, CLI/config
    file, and database manifest boundaries before persistence.
  - Verification: focused config, CLI, and manifest-boundary tests reject
    `sk-proj_runidsecret_1234567890abcdef` and keep normal configured ids
    accepted.
- [x] Add config-file source provenance and local-file validation to
  AlphaEvolve setup fidelity.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.3, and 2.6.
  - Requirement: task configuration and LLM/evaluator choices should be
    reproducible and attributable to deliberate problem-local setup inputs.
  - Status: implemented for CLI-loaded `config.yaml`. The file must be absent
    or regular and local; link-like or directory-shaped paths fail as setup
    errors. Manifests now identify config-source absence or record
    `config.yaml` path, hash, and byte count when a problem-local config file
    shaped the effective configuration.
  - Verification: focused CLI tests cover config absence, directory rejection,
    malformed YAML handling, and manifest hash/byte-count persistence for a
    present config file.
  - Remaining scoped gap: shared YAML parser diagnostic redaction for
    non-config setup files remains open under a separate paper item.
- [x] Treat absolute config-loader diagnostics as setup-provenance
  shareability gaps.
  - Paper evidence: AlphaEvolve-style setup validation should produce useful
    task/configuration diagnostics without exposing private local path material
    when audit logs are shared.
  - Status: implemented for `config.yaml` loader diagnostics. CLI config
    diagnostics use the stable `config.yaml` label, redact common secret-like
    parser/key text, and do not display raw absolute problem roots for covered
    startup config failures.
  - Verification: focused CLI tests cover malformed YAML, invalid UTF-8,
    duplicate-key, unknown-key, directory-shaped, and link-like config
    diagnostics, including secret-like problem roots and config keys.
  - Remaining scoped gap: raw path/root display remains tracked separately from
    YAML parser key-text redaction.
- [x] Treat secret-bearing YAML duplicate-key errors as a setup-fidelity gap.
  - Paper evidence: AlphaEvolve-style task setup and run logs should preserve
    enough evidence to reproduce malformed setup failures without leaking
    private credentials or local secrets.
  - Status: implemented for setup YAML parser diagnostics. Config, metrics, and
    context manifest YAML parse errors now pass through shared secret-pattern
    redaction before CLI display or loader error propagation.
  - Verification: focused CLI and loader tests cover duplicate
    `api_key=sk-proj_yamldiagsecret1234567890` keys in `config.yaml`,
    `metrics.yaml`, and `context/context.yaml` without surfacing the raw key.
  - Remaining scoped gap: raw path/root display is still tracked separately
    from YAML key-text redaction.
- [x] Treat equality-only validator checks as a paper-level benchmark fidelity
  gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Requirement: evaluators should reflect the target task semantics and reject
    candidate artifacts that satisfy the harness accidentally or adversarially
    without solving the represented problem.
  - Status: implemented for the current smoke examples. `hello_world`,
    `sorting`, and `workspace_math` now enforce exact return-type contracts
    before equality scoring.
  - Verification: focused example tests reject `AlwaysEqual()` spoofing objects
    and wrong scalar/container types while preserving ordinary valid outputs.
  - Remaining scoped gap: paper-grade benchmark fidelity still requires
    stronger non-toy fixtures and independent benchmark-validation work.
- [x] Treat ignored direct primary bounds as a paper-level objective-schema
  fidelity gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.6.
  - Requirement: objective schemas and run setup should define score
    normalization and comparison semantics unambiguously, especially when those
    semantics drive archive admission, sampling, and benchmark reporting.
  - Status: implemented. Direct `Problem.primary_bounds` is no longer silently
    discarded when it conflicts with the primary metric schema; malformed,
    non-finite, boolean, descending, and mismatched direct bounds fail during
    problem construction.
  - Verification: focused loader tests cover rejected direct bounds and
    matching direct bounds; loop manifest tests confirm objective-schema
    persistence remains consistent for valid direct problems.
- [x] Treat unknown-metric default normalization as a paper-level objective
  schema gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.3, and 2.6.
  - Requirement: metric identities, directions, and bounds should be declared
    experiment setup semantics, not invented at consumer lookup time.
  - Status: implemented for public objective helpers. Undeclared names now
    raise from `Problem.metric()`, `metric_bounds()`, `metric_direction()`, and
    `normalize_metric()` instead of receiving default objective semantics.
    Prompt/history surfaces can still display undeclared feedback/plugin
    metrics without treating them as declared objective metrics.
  - Verification: focused loader tests cover declared and undeclared helper
    behavior; focused prompt tests prove undeclared extra metrics still render;
    loop/evaluator tests cover declared objective-schema consumers.
- [x] Treat mutable effective metric schemas as a paper-level objective
  provenance gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.3, and 2.6.
  - Requirement: objective definitions should remain stable enough to reproduce
    evaluation, archive admission, prompt feedback, and benchmark comparisons
    from recorded setup provenance.
  - Status: implemented for `Problem` schemas. The validated objective schema
    is stored as immutable records with immutable bounds, and manifest-facing
    `objective_schema()` returns copied JSON-friendly records.
  - Verification: focused loader tests prove caller-owned metric dictionaries,
    returned schema snapshots, and attempted direct record/bounds mutation do
    not change helper normalization; focused prompt/loop/evaluator tests cover
    frozen-schema consumers.
- [x] Treat unsafe configured `log_dir` labels as paper-level artifact
  provenance gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: experiment artifacts and run manifests should identify storage
    locations reproducibly without accepting display-confusing or invalid path
    labels as normal provenance.
  - Status: implemented for configured log roots. Path/display-unsafe
    `log_dir` values fail during config validation, and manifest retention
    keeps safe relative roots readable while representing absolute or
    secret-like roots with redacted/hash-backed metadata.
  - Verification: focused config tests cover unsafe labels; CLI tests prove
    malformed `config.yaml` log roots fail cleanly before run setup; manifest
    tests cover safe relative and secret-like retention behavior.
- [x] Deduplicate migrated island elites before treating migration as
  paper-faithful population exchange.
  - Paper evidence: `1504.04909__MAP_Elites.pdf` treats the archive as a map of
    elites over behavior cells, and island-model papers use migration to
    exchange candidate solutions rather than inflate local elite counts with
    repeated references to the same individual.
  - Status: implemented for local island migration. Migration now has explicit
    canonical-reference semantics, skips duplicate target placements, and
    records source/destination placement metadata without replacing original
    archive-admission provenance.
  - Verification: focused island tests cover repeated migration, object
    identity, placement metadata, ring topology, and sampling deduplication.
  - Remaining scoped gap: replayable persisted migration event logs and archive
    snapshots remain open separately.
- [x] Treat migration/resume duplicate candidate ids as a paper-level
  evolutionary database integrity gap.
  - Paper evidence: AlphaEvolve-style archives and evolutionary databases rely
    on candidate identity for lineage, parent selection, replay, and analysis
    of which program state occupied which search cell.
  - Status: implemented as a local identity policy. Duplicate direct archive
    ids are rejected, migration uses canonical-id references without clone ids,
    duplicate target placements are skipped, and manifests record the current
    snapshot-restore limitation.
  - Verification: focused database tests cover manifest identity policy and
    migration events; focused island tests cover repeated migration and
    placement metadata.
- [x] Preserve accepted program records as immutable archive snapshots.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the program database should retain stable evaluated programs
    and metadata for later prompting, inspection, and reproducible replay.
  - Status: implemented for current in-memory database records. Accepted
    candidates are deep-snapshotted at archive/log boundaries, and database
    accessors return snapshots so stale caller references cannot mutate stored
    candidate facts.
  - Verification: focused database tests prove post-admission mutations of the
    original program and returned database snapshots do not change archived or
    logged in-memory records.
- [x] Validate structured evaluation-record shape at database boundaries.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the evolutionary database should store structured result
    records for evaluated programs; malformed restored/direct records should be
    rejected or quarantined with diagnostics instead of crashing archive or
    failure-memory operations.
  - Status: implemented for current `Program` and `ProgramDatabase` boundaries.
    Evaluation payloads must be JSON-safe mappings, are revalidated before
    archive/history/failure use, and malformed stage arrays are retained as
    bounded diagnostics rather than raw crashes.
  - Verification: focused database tests cover construction rejection,
    direct mutation before admit/log/failure/seed-failure, exact validity
    handling, and malformed-stage diagnostics.
- [x] Treat primary-only workspace seed failure snippets as a paper-level
  codebase-candidate memory gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: evaluated program records and failed-trial memories should
    preserve the relevant candidate artifact so later search, prompting, and
    analysis can understand what was tried.
  - Status: implemented for initial seeds. Seed failure rows now preserve
    file-set evidence through deterministic all-file `mutation_text` and a
    `seed_workspace` schema containing per-file path, primary/support role,
    byte count, SHA-256, bounded/redacted snippet, and truncation metadata.
  - Verification: focused database tests prove multi-file failed seeds retain
    non-primary helper content in failure memory and still redact helper-file
    secrets before persistence.
- [x] Define zero-generation no-valid-seed behavior.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Requirement: the evolutionary database and run logs should make it clear
    whether a budget point produced an admissible program, only invalid
    evaluations, or no candidate evidence at all.
  - Status: implemented for seed-only baselines. Invalid-only
    zero-generation runs now produce seed history/failure-memory evidence,
    report `runtime.stop_reason: "no_valid_programs"`, leave best-artifact
    pointers absent, and return no best to the CLI. Mixed zero-generation runs
    still preserve the valid archived seed as best and report the generation
    limit.
  - Verification: focused loop and CLI tests cover invalid-only and mixed
    zero-generation seed baselines, manifest stop reasons, and best-artifact
    absence.
- [x] Make prompt-program records self-validating.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 4.
  - Requirement: if prompts are evolved as programs in an archive, persisted
    prompt-program records should have a validated representation before they
    can influence selection, lineage, replay, or meta-prompt mutation.
  - Status: implemented for current prompt-program state. Prompt programs now
    validate template type, allowed placeholders, and render-compatible format
    specs at construction and revalidation, so invalid template records cannot
    masquerade as valid prompt-program archive state.
  - Verification: focused meta-prompt tests cover invalid direct construction,
    explicit revalidation after template mutation, database add revalidation,
    configured-template rejection, and invalid mutation quarantine behavior.
- [x] Make rejected prompt-template artifacts bounded and redacted.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: prompt-program evolution should retain useful failure
    diagnostics without turning rejected prompt outputs into unbounded or
    sensitive durable artifacts.
  - Status: implemented. Rejected prompt mutations now persist a safe template
    preview with raw length, SHA-256, redaction, and truncation metadata instead
    of raw prompt output.
  - Verification: focused meta-prompt tests prove a rejected template with a
    fake provider key and 1200-character tail is redacted/truncated in
    `prompt_history_invalid.jsonl` while preserving raw hash and length.
- [x] Make prompt reward metadata failures paper-visible and state-consistent.
  - Paper evidence: AlphaEvolve-style prompt databases should preserve reliable
    prompt selection statistics and lineage evidence; rejected or malformed
    score updates should not create unlogged prompt-arm rewards.
  - Status: implemented for score metadata failures. Prompt reward metadata is
    validated before score-state mutation; failures write quarantine
    diagnostics and leave live prompt-arm statistics aligned with
    `prompt_history.jsonl`.
  - Verification: focused meta-prompt tests cover invalid score metadata,
    repeated failures, non-finite rewards with metadata, quarantine records,
    stable prompt selection, and unchanged prompt history after rejected score
    updates.
- [x] Make raw prompt-score metadata a paper-visible prompt-archive gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt-program archives and prompt-evolution evidence should
    be auditable, bounded, and safe to use in long-running experiments without
    leaking caller-supplied labels or diagnostic payloads.
  - Status: implemented for current prompt score metadata. Accepted metadata is
    recursively redacted and bounded before prompt archive persistence, and
    unsafe keys carry hash-backed redacted labels.
  - Verification: focused meta-prompt tests cover secret-like keys and values,
    nested/list metadata, oversized strings, live prompt state, and
    `prompt_history.jsonl` output.
- [x] Make meta-prompt template input safe and budgeted.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt evolution should operate on prompt-program evidence and
    templates through a reproducible, bounded, and auditable policy suitable
    for long-running LLM-guided search.
  - Status: implemented for current-template input. Meta-prompt calls now use a
    bounded redacted template preview plus explicit placeholder list, and
    prompt-history mutation context stores template hash/length/redaction/
    truncation provenance instead of raw template content.
  - Verification: focused loop tests prove fake provider-key text and an
    oversized template tail do not reach the meta-prompt request or metadata
    while hash and length evidence remain available.
- [x] Treat unsafe meta-prompt evidence keys as a paper-level prompt-evolution
  gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2 and 4.
  - Requirement: prompt evolution evidence should be reproducible, bounded, and
    safe to render into LLM prompts, including labels for metrics, failures,
    score metadata, and plugin-produced fields.
  - Status: implemented for provider-visible meta-prompt evidence keys.
    Mapping and metric keys are now redacted/bounded, and changed keys carry
    short SHA-256 suffixes for reproducible label comparison.
  - Verification: focused loop tests cover secret-like top-level, nested, and
    metric keys plus long and non-string key labels.
- [x] Treat raw plugin metadata keys as a paper-level provenance shareability
  gap.
  - Requirement: Paper-inspired plugins and AlphaEvolve-style experiment
    manifests should produce shareable provenance for prompt context and
    artifact summaries without leaking credential-like labels supplied by
    custom plugins.
  - Status: implemented for plugin metadata labels. Recursive keys from
    `prompt_context_metadata()` and `run_artifacts_metadata()` are now
    redacted/bounded and hash-suffixed when changed; credential-shaped labels
    use a neutral redacted stem.
  - Verification: focused loop tests cover custom plugin prompt-context
    metadata and run-artifact metadata before persistence.
- [x] Make evaluator timeout cleanup robust enough for long automated runs.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.4 and 2.6.
  - Requirement: automated evaluator-heavy runs need bounded execution and
    reliable cleanup of evaluator subprocesses and descendants.
  - Status: implemented for local subprocess containment. Windows validators
    now use Job Object kill-on-close containment when available, in addition to
    taskkill cleanup. Taskkill-reported un-terminated child PIDs receive direct
    per-PID cleanup attempts, and timeout cleanup records those diagnostics.
  - Verification: focused descendant-process timeout tests pass after the
    hardening, and full non-integration validation passed.
- [x] Treat host-dependent evaluator-output decoding as a paper-level
  reproducibility gap.
  - Requirement: Paper-aligned evaluator diagnostics and feedback records
    should preserve validator output through a deterministic, documented
    transport so repeated runs on different hosts do not change stored
    stdout/stderr text or prompt-visible feedback.
  - Status: implemented. Validator stdout/stderr is byte-captured and decoded
    with explicit UTF-8 replacement, with byte/replacement/malformed diagnostics
    persisted before redaction/truncation output metadata.
  - Verification: focused evaluator tests cover malformed stdout/stderr bytes
    and timeout stdout bytes before persistence.
- [x] Treat inherited validator stdin as a paper-level evaluator isolation gap.
  - Requirement: Paper-aligned evaluator workers should run unattended under a
    defined IO contract. Interactive standard input should either be impossible
    by construction or explicitly modeled as a benchmark input fixture.
  - Status: implemented with an unsupported-interactive policy. Validators get
    `DEVNULL` stdin, `input()` receives EOF, and direct reads return an empty
    string; fixture input remains unimplemented and separately out of scope.
  - Verification: focused evaluator tests cover interactive and direct-read
    validators plus configured-stage sample metadata.
- [x] Treat skipped-link target blindness as a paper-level provenance gap.
  - Requirement: paper-visible provenance should make materially different
    local problem/source inputs distinguishable, including unsafe or skipped
    filesystem links that may point outside the run package.
  - Status: implemented. Skipped symlink/junction records now include
    redacted/hash-backed target identity, target scope, within-root status, and
    unresolved-link diagnostics, and those records feed v2 skipped/provenance
    hashes.
  - Verification: focused provenance tests cover target-aware skipped-link
    diagnostics and target-change hash sensitivity for file symlinks and
    Windows junctions.
- [x] Treat missing-parent persistence failures as a paper-level artifact gap.
  - Requirement: paper-visible run artifacts and experiment database streams
    should have a defined creation/error contract for managed paths, including
    manifests, histories, quarantine streams, and plugin export files.
  - Status: implemented. Strict JSON/JSONL/quarantine writers now create
    missing parents for valid writes and raise bounded, secret-redacted
    `StrictJsonlError` diagnostics for invalid parent path types.
  - Verification: focused JSONL tests cover manifest, append-only stream,
    quarantine, and invalid-parent cases; TTTRL plugin tests cover plugin JSONL
    export under a missing parent.
- [x] Treat archive-admission id mismatches as a paper-level provenance gap.
  - Requirement: AlphaEvolve-style evolutionary records should preserve a
    coherent identity across candidate history, archive admission, lineage, and
    future resume/search state.
  - Status: implemented for current history inspection. `show` now enforces
    identity consistency for present `metadata.archive_admission.program_id`
    values while accepting older current-format rows that omit the field.
  - Verification: focused CLI tests cover paper-visible selected and unselected
    mismatch cases, matching ids, compatibility omissions, and unsafe admission
    ids before terminal display.
- [x] Treat raw dependency names as a paper-level manifest shareability gap.
  - Requirement: paper-visible run manifests should support reproducibility
    review without leaking private dependency names, package-source labels, or
    credential-like strings.
  - Status: implemented. Runtime dependency provenance redacts secret-like
    dependency names, stores raw-name hashes for comparison, documents lookup
    semantics, and suppresses raw installed-version lookup for unsafe names.
  - Verification: focused provenance tests cover public packages,
    private-source package specs, secret-like names, and absence of raw unsafe
    names from rendered provenance.
- [x] Treat inconsistent `__pycache__` candidate paths as a paper-level
  codebase-fidelity gap.
  - Requirement: codebase-candidate representations should have a consistent
    policy for source files versus generated/cache artifacts across seed
    ingestion, mutation, evaluation, archive history, and exported workspaces.
  - Status: implemented. Generated/direct candidate paths now reject
    `__pycache__` components through the shared path grammar, while seed
    ingestion continues to skip cache directories before workspace construction.
  - Verification: focused candidate and loader tests cover direct cache paths,
    mutation-created cache paths, and seed cache-directory handling.
- [x] Treat mutable archive-sequence recency as a paper-level search-state gap.
  - Requirement: AlphaEvolve-style search should make parent/inspiration
    selection reproducible from archive events, not from mutable metadata that
    plugins or callers can rewrite after admission.
  - Status: implemented for live search state. Recency sampling now consults an
    internal archive sequence index; persisted archive-sequence metadata remains
    provenance and can be mutated without changing live sampling order.
  - Verification: focused island tests cover parent and inspiration recency
    after direct mutation of `metadata.archive_sequence`.
- [x] Treat launcher-inconsistent CLI help as a paper-index truthfulness gap.
  - Requirement: paper-index and AlphaEvolve-alignment validation commands
    should be repeatable from the documented local Windows launcher contract.
  - Status: fixed in the module entrypoint. Click help generated through
    `py -3.12 -m libreevolve` now renders launcher-consistent root and
    subcommand usage banners.
  - Verification: subprocess CLI tests and direct help invocations cover root
    and `run` help, including checks that `Usage: python -m libreevolve` is no
    longer emitted for module execution.
- [x] Treat unsafe paper-manifest file names as paper-index provenance gaps.
  - Status: fixed. Manifest paths now require portable, display-safe
    `papers/<name>.pdf` names and reject Windows-reserved, hidden, and
    control/format-character names.
  - Verification: focused paper-manifest tests cover the unsafe-name proof
    cases.
- [x] Treat duplicate paper-cache file targets as paper-index provenance gaps.
  - Status: fixed. Paper-cache validation now distinguishes manifest rows from
    unique artifacts and rejects duplicate file targets/digests.
  - Verification: focused tests cover duplicate `papers/shared.pdf` rows and
    unique local artifact count.
- [x] Treat duplicate CSV paper-manifest ids as paper-index provenance gaps.
  - Status: fixed. Duplicate CSV row identities now receive a direct validator
    diagnostic before JSON comparison.
  - Verification: focused tests cover duplicate CSV ids.
- [x] Treat unvalidated paper-manifest row ids as paper-index provenance gaps.
  - Status: fixed. Paper ids are now constrained to arXiv ids or lowercase
    foundational-paper slugs, and secret-like ids are rejected/redacted.
  - Verification: focused CLI JSON tests cover the secret-like id proof case.
- [x] Treat unchecked README badge counts as paper-index provenance gaps.
  - Status: fixed. README paper-cache badge counts are parsed and reconciled
    with prose counts and manifest row counts.
  - Verification: focused tests cover stale and malformed badge counts.
- [x] Treat unvalidated paper-manifest URLs as paper-index provenance gaps.
  - Status: fixed. Manifest source URLs must be share-safe HTTPS URLs from
    known paper source hosts.
  - Verification: focused CLI JSON tests reject a local secret-bearing URL.
- [x] Treat raw paper-manifest download messages as paper-index provenance
  gaps.
  - Status: fixed. Manifest messages are validated, bounded, and redacted
    before availability/report output.
  - Verification: focused tests cover a long secret-bearing message and prove
    bounded redacted output.
- [x] Treat unbounded unsafe manifest titles as paper-index provenance gaps.
  - Status: fixed. Paper-manifest titles now have bounded display-safety and
    secret-like text validation.
  - Verification: focused CLI JSON tests cover the secret-like multiline title
    proof case.
- [x] Treat ignored extra manifest fields as paper-index provenance gaps.
  - Status: fixed. The manifest schema is closed and unsupported JSON fields
    or CSV headers fail validation with redacted diagnostics.
  - Verification: focused tests reject extra `api_key` metadata without
    emitting raw secret-like values.
- [x] Treat duplicate JSON object names as paper-index provenance ambiguity.
  - Status: fixed. JSON manifest loading now detects duplicate object keys.
  - Verification: focused tests reject duplicate `url` keys.
- [x] Treat duplicate CSV headers as paper-index provenance ambiguity.
  - Status: fixed. CSV manifest loading now validates unique canonical headers
    before row normalization.
  - Verification: focused tests reject duplicate `url` headers.
- [x] Treat unchecked empty-CSV headers as paper-index provenance ambiguity.
  - Status: fixed. CSV header validation runs for zero-row manifests.
  - Verification: focused tests reject an empty CSV with wrong headers.
- [x] Treat eager full-PDF hash reads as a paper-cache validation scalability
  gap.
  - Status: fixed. Local PDF hashes are now computed with streaming chunked
    reads instead of eager whole-file reads.
  - Verification: focused tests validate a large PDF while `Path.read_bytes()`
    is monkeypatched to fail.
- [x] Treat hash-matching non-PDF cache files as paper-index provenance gaps.
  - Status: fixed. Required-local validation now rejects local `.pdf` files
    whose content does not start with `%PDF-`.
  - Verification: focused tests cover matching plain-text bytes.
- [x] Treat clean validation with failed-download metadata as paper-index
  provenance ambiguity.
  - Status: fixed. `ok: false` rows now fail validation with
    `download_failed`.
  - Verification: focused tests cover failed-download metadata with a matching
    local file.
- [x] Treat unmanifested local PDFs as paper-cache provenance gaps.
  - Status: fixed. Strict local validation reports extra `papers/*.pdf`
    artifacts not listed in the manifest.
  - Verification: focused tests cover `papers/extra.pdf` in required-local
    mode.
- [x] Treat Git-tracked local PDFs as paper-cache provenance boundary gaps.
  - Status: fixed. Tracked local cache PDFs now emit `tracked_pdf` validation
    issues.
  - Verification: focused tests cover a Git-staged local PDF.
- [x] Treat unsynchronized `papers/README.md` status IDs as paper-index
  provenance gaps.
  - Status: fixed. The status table is now reconciled against manifest IDs,
    including duplicate, table-only, and manifest-only diagnostics.
  - Verification: focused tests cover stale, missing, duplicate, and exact
    status-table rows; strict validation of the real paper cache still passes.
- [x] Treat link-backed local paper PDFs as unresolved paper-cache provenance.
  - Status: fixed. The paper-cache validator now rejects symlink and Windows
    reparse-point backed PDF entries before following them.
  - Verification: focused tests simulate both link-backed cases and assert
    `linked_pdf` diagnostics.
- [x] Treat agent-facing threshold-only archive wording as a paper-fidelity
  gap.
  - Status: fixed. `AGENTS.md` no longer conflates validity, threshold checks,
    archive retention, and sampling eligibility for `ProgramDatabase.admit()`.
  - Verification: agent-doc tests assert MAP-Elites retention semantics,
    `reason="not_improving_cell"`, and `sampling_eligible` wording.
- [x] Treat unvalidated direct critique prompt inputs as a reviewer-fidelity
  gap.
  - Status: fixed. Direct critique prompt construction no longer stringifies
    arbitrary objects into reviewer instructions or mutation context.
  - Verification: feedback tests assert type/emptiness validation plus
    redaction and truncation for critique prompt sections.
- [x] Treat unvalidated direct feedback-grader prompts as reviewer-fidelity
  limits.
  - Status: fixed. Direct feedback grader prompts no longer stringify
    arbitrary objects into reviewer LLM prompt text.
  - Verification: feedback tests assert structured invalid-config diagnostics,
    default blank-prompt behavior, and redacted/bounded custom prompt text.
- [x] Treat direct feedback-grader schema gaps as paper-level reviewer
  fidelity limits.
  - Status: fixed. Direct feedback grader specs are validated before feedback
    policy and provider-call handling, including invalid-candidate paths.
  - Verification: focused feedback tests assert structured
    `invalid_feedback_config` records for malformed direct grader specs.
- [x] Treat unbounded plugin metadata as a paper-level provenance limit.
  - Status: fixed. Plugin prompt-context and run-artifact metadata now reject
    oversized aggregate payloads rather than only validating individual scalar
    values.
  - Verification: focused loop tests assert item-count, depth, and serialized
    JSON limits for plugin metadata.
- [x] Treat unbounded skipped-context hashing as a paper-level context limit.
  - Status: fixed. Skipped context diagnostics no longer read oversized skipped
    files to compute hashes before source byte budgets apply.
  - Verification: focused loader tests assert hash omission and no skipped-file
    `read_bytes()` for oversized unsupported, excluded, hidden, and
    not-included context files.
- [x] Treat unvalidated context provenance payloads as a paper-level manifest
  gap.
  - Status: fixed. Context provenance payloads are validated, bounded, and
    redacted at the manifest boundary before paper-level run provenance is
    written.
  - Verification: database and loop tests assert context-specific diagnostics
    for malformed direct payloads and safe persistence for secret-like fields.
- [x] Treat duplicate JSON names in LLM feedback as paper-level reviewer
  ambiguity.
  - Status: fixed. Feedback responses with duplicate JSON object names are now
    rejected before reviewer scores, discard flags, or feedback text can be
    treated as deterministic evaluation evidence.
  - Verification: focused feedback tests assert duplicate-key rejection for
    direct, nested, and fenced JSON and no candidate score/validity side
    effects after ambiguous reviewer output.
- [x] Treat duplicate JSON names in run manifests as paper-level artifact
  ambiguity.
  - Status: fixed. Runtime manifest updates reject duplicate JSON object names
    in the current `manifest.json` and preserve ambiguous source bytes instead
    of rewriting collapsed provenance.
  - Verification: focused database tests assert quarantine diagnostics,
    unchanged manifest bytes, and strict failure for top-level and nested
    duplicate manifest object names.
- [x] Treat duplicate JSON names in inspected histories as paper-level artifact
  ambiguity.
  - Status: fixed for `show history.jsonl`. Inspected history rows now reject
    duplicate JSON object names before candidate identities, fitness values,
    metrics, or archive-selection metadata can be reported as paper-level
    evidence.
  - Verification: focused CLI tests assert duplicate-key rejection for
    top-level, nested metric, and nested archive metadata fields.
- [x] Treat invalid-encoding CSV/JSON manifests as paper-index validation gaps.
  - Status: fixed for invalid UTF-8. The paper-manifest validator now returns
    structured unreadable-manifest issues for invalid-encoding CSV and JSON
    corpus manifests.
  - Verification: focused paper-manifest tests assert `csv_manifest_unreadable`
    and `json_manifest_unreadable` reports rather than uncaught decode errors.
- [x] Treat range-shaped `extracted_pages` as a paper-level PDF context
  provenance ambiguity.
  - Status: fixed. PDF context provenance now separates exact extracted page
    lists from page ranges, making prompt/literature attribution clearer for
    non-contiguous extracted pages.
  - Verification: focused loader tests assert exact page metadata for PDFs with
    extractable text separated by blank pages.
- [x] Treat concatenated-offset PDF citations as a paper-level context
  provenance ambiguity.
  - Status: fixed. Prompt-visible PDF citations now use page-local offsets, and
    metadata retains global concatenated offsets separately for reproducibility
    and audit.
  - Verification: focused loader, prompt, and feedback tests assert page-local
    citations across multi-page excerpts with inserted separators.
- [x] Treat unchecked cached-PDF prose counts as paper-index provenance gaps.
  - Status: fixed. The paper-manifest validator now checks cached-PDF count
    prose used by `papers/README.md` rather than ignoring stale local-corpus
    count claims.
  - Verification: focused paper-manifest tests assert stale cached-PDF wording
    produces a structured manifest count mismatch.
- [x] Treat README count-source read failures as paper-index validation gaps.
  - Status: fixed. README and `papers/README.md` read/encoding failures now
    produce structured paper-index validation issues, preserving the validator
    as a robust corpus-provenance gate.
  - Verification: focused paper-manifest tests assert invalid UTF-8 in both
    README count surfaces returns issues instead of exceptions.
- [x] Treat conflicting README count-source diagnostics as paper-index
  validation gaps.
  - Status: fixed. Conflicting README, badge, and `papers/README.md`
    paper-count claims are diagnosed as source-aware documented-count
    conflicts rather than as a synthetic expected manifest count.
  - Verification: focused paper-manifest tests assert source paths, count
    values, matched phrases, and separation from `documented_count_mismatch`.
- [x] Treat Unicode-normalized context-path collisions as a paper-level
  provenance gap.
  - Status: fixed. Prompt-visible context source identities now use NFC
    display labels, retain differing raw filesystem paths, and reject selected
    context files whose labels collide after normalization.
  - Verification: focused loader tests assert normalized include/exclude
    behavior, source metadata, skipped diagnostics, and duplicate-path
    rejection for composed/decomposed context file names.
- [x] Treat Unicode-normalized problem-provenance path collisions as a
  paper-level manifest gap.
  - Status: fixed. Problem/source provenance now has paper-visible path
    identity semantics: NFC display paths, raw filesystem spelling metadata,
    and fail-fast duplicate included records after normalization.
  - Verification: focused provenance tests assert normalized included-file
    records, skipped generated-root records, source-tree collision rejection,
    and JSON-serializable manifest records.
- [x] Treat raw plugin class/module identity labels as a paper-level
  provenance and candidate-history safety gap.
  - Status: fixed. Plugin provenance and candidate plugin-context history now
    use paper-visible identity semantics: normalized/redacted display labels,
    bounded persisted text, hash-backed raw identity fields, and missing-module
    diagnostics without leaking unsafe class/module names.
  - Verification: focused provenance and loop tests assert share-safe plugin
    startup provenance, artifact attribution, prompt-context history, and
    repeated-instance correlation.
- [x] Treat raw pyproject metadata fields as a paper-level manifest
  shareability gap.
  - Status: fixed. Package/build metadata in runtime provenance now has
    paper-visible retention semantics: safe string schemas, bounded
    redacted/hash-backed fields, escaped Unicode format controls, and raw lookup
    suppression for unsafe project names.
  - Verification: focused provenance tests assert share-safe package name,
    version, requires-python, build backend, build requirements, and installed
    version lookup behavior.
- [x] Treat unredacted pyproject diagnostics as a manifest-provenance fidelity
  gap.
  - Status: fixed. Pyproject provenance diagnostics now have paper-visible
    shareability semantics: typed status/error fields with bounded,
    secret-redacted diagnostic text for read, decode, and parse failures.
  - Verification: focused provenance tests assert secret-like and oversized
    pyproject diagnostics stay out of manifest JSON, while CLI `show` tests
    confirm runtime package diagnostics are not displayed.
- [x] Treat absolute paper-manifest loader diagnostics as paper-index
  shareability gaps.
  - Status: fixed. Paper-index validation diagnostics now use
    repository-relative labels for manifest and README/status-table sources,
    with exact filesystem paths removed from exception text before redaction.
  - Verification: focused paper-manifest tests assert malformed/missing
    manifest diagnostics and README/status-table read errors are safe in text
    and JSON CLI output under a secret-like repository root.
- [x] Treat raw provenance root fields as paper-level manifest shareability
  gaps.
  - Status: fixed. Source/problem/Git root displays in manifest-facing
    provenance now use local root labels and stable hashes instead of raw
    absolute path material.
  - Verification: focused provenance tests assert secret-like problem and Git
    roots stay out of JSON-rendered provenance, and loop tests assert manifests
    retain root labels while Git lookup still uses the real source root.
- [x] Treat incoherent parent/lineage graphs as a paper-level database gap.
  - Status: fixed. Candidate program records now enforce paper-visible lineage
    invariants before direct construction, archive/island mutation, accepted
    history persistence, or `show` inspection can treat parentage as trajectory
    evidence.
  - Verification: focused program, database, MAP-Elites, island, and CLI tests
    assert self-parenting, self-in-lineage, duplicate lineage ids, and
    parent-tail mismatches are rejected.
- [x] Treat duplicate failed-candidate ids as a paper-level database identity
  gap.
  - Status: fixed. Failed candidate `program_id` values are now unique within
    `failure_history.jsonl`; duplicate failed ids are quarantined while
    repeated failure patterns remain linked by fingerprint.
  - Verification: focused database tests assert duplicate generated and seed
    failed ids are rejected, and repeated fingerprints use distinct candidate
    ids.
- [x] Treat boolean metric bounds as a paper-level task-schema fidelity gap.
  - Status: fixed. Metric-bound semantics now reject booleans separately from
    numeric literals across problem loading, direct `Problem` construction, and
    database objective-schema validation, preserving numeric objective
    semantics for paper-visible score normalization.
  - Verification: focused loader and database tests assert boolean bounds are
    rejected while existing metric-bound validation continues to cover finite,
    strictly increasing numeric bounds.
- [x] Validate typed program-record fields before archive sampling.
  - Status: fixed. `Program` construction now requires non-negative integer
    generations, direct database logging/admission quarantines mutated invalid
    generations before accepted or failed history writes, archive/island
    mutation paths reject invalid generations before recency sampling, and
    `show` rejects malformed history generations before printing.
  - Verification: focused program, database, island, and CLI tests cover direct
    invalid generations, mutated accepted and failed rows, archive sampling
    guards, and secret-like history generation diagnostics.
- [x] Treat primary-only metric parent sampling as a multi-objective fidelity
  gap.
  - Status: fixed. Secondary metric leaders can now directly steer mutation as
    cyclic metric parent targets, while generated candidate records preserve
    the chosen target metric as provenance.
  - Verification: focused island/database tests assert secondary metric leaders
    become metric parents, and focused loop tests assert generated history rows
    record the selected metric target.
- [x] Preserve metric-vector semantics for evaluator-generated failure records.
  - Status: fixed. Internal evaluator failures now preserve the declared metric
    vector using an explicit synthetic penalty policy, so multi-metric history
    rows retain every declared score field while failure metadata distinguishes
    them from validator-produced measurements.
  - Verification: focused evaluator tests cover multi-metric synthetic failure
    records for diff, syntax, timeout, subprocess, and malformed output paths.
- [x] Define invalid-prompt mutation penalties on the prompt reward scale.
  - Status: fixed. Rejected prompt mutations now use the configured prompt
    reward lower bound and normalization policy, preserving comparable
    prompt-arm evidence while still recording rejection-specific metadata.
  - Verification: focused meta-prompt tests cover bounded penalty metadata and
    parent-arm statistics for rejected prompt children.
- [x] Treat YAML alias-shared setup records as a paper-level reproducibility
  gap.
  - Status: fixed. Setup YAML anchors and aliases are unsupported and rejected
    before setup records are constructed, removing hidden alias-shared identity
    from config, metric, context, and manifest provenance inputs.
  - Verification: focused loader and CLI tests cover anchor/alias rejection at
    the shared loader, problem setup, context manifest, and config boundaries.
- [x] Treat secret-like run names as a paper-level artifact shareability gap.
  - Status: fixed. Run identity labels now reject secret-like assignment text
    and provider-token-shaped values before they can become filesystem
    components or `manifest.json.config.problem_name` values.
  - Verification: focused config and CLI tests cover direct `problem_name` and
    `--run-name` rejection while preserving ordinary portable run names.
- [x] Treat skipped context-label leakage as a paper-level context provenance
  gap.
  - Status: fixed. Skipped context diagnostics now reject secret-like relative
    labels before they can be retained in manifest-visible context policy
    provenance.
  - Verification: focused loader tests cover all documented skipped-source
    paths for unsupported, excluded, hidden, not-included, and byte-budget
    diagnostics.
- [x] Treat candidate and seed path-label leakage as a paper-level multi-file
  provenance gap.
  - Status: fixed. Candidate and loaded seed-source path labels now reject
    secret-like values before they can be retained in prompt-visible,
    history-visible, manifest-visible, or exported candidate provenance.
  - Verification: focused candidate, loader, and program tests cover direct
    workspaces, mutation file sections, direct program file sets, and loaded
    seed provenance labels.
- [x] Treat compatibility-confusable candidate path labels as a paper-level
  codebase provenance gap.
  - Status: fixed. Candidate path labels must now be stable under Unicode
    compatibility normalization and cannot contain non-ASCII separator spaces
    or surrogate code points, preserving unambiguous file identity across
    prompts, histories, manifests, materialization, and exports.
  - Verification: focused candidate tests cover ordinary non-ASCII acceptance
    and representative compatibility-confusable rejection cases.
- [x] Treat unvalidated direct seed-source provenance as a paper-level setup
  manifest gap.
  - Status: fixed. Direct `Problem.initial_workspace_sources` and
    database-provided seed-source records are schema-validated with
    seed-specific diagnostics before manifests or seed history rows can be
    written.
  - Verification: focused database and loop tests cover malformed direct
    sources, JSON-unsafe shapes, secret-like labels, index/count consistency,
    and valid loader-shaped provenance.

- [x] Treat unvalidated direct context-file payloads as a paper-level prompt
  input gap.
  - Status: fixed. Direct and loader-created context now share a prompt-facing
    schema boundary for mapping shape, safe labels, JSON-safe rendering, and
    bounded direct values before prompts or run artifacts can use the data.
  - Verification: focused prompt tests cover malformed and unsafe direct
    context payloads, and focused loop tests prove invalid direct context is
    rejected before manifest writes or overwrite cleanup.

- [x] Treat unvalidated direct task descriptions as a paper-level task-setup
  gap.
  - Status: fixed. Direct task descriptions now share the loader's non-empty
    task contract plus explicit direct bounds and safety checks before prompt
    rendering or runtime setup; valid task text remains exact-retained
    prompt/provenance material.
  - Verification: focused prompt tests cover invalid direct task values and
    exact retention for valid text, and loop preflight tests prove malformed
    direct task text fails before manifest writes or overwrite cleanup.

- [x] Treat malformed direct inline seeds mutating run artifacts as a
  paper-level setup validation gap.
  - Status: fixed. Direct inline seeds now have a pre-manifest schema for list
    shape, string entries, UTF-8 encodability, bounded text, and evolve-block
    marker validity before any run artifacts are created or overwritten.
  - Verification: focused loop tests prove malformed direct inline seeds leave
    existing history intact and write no manifest, while valid inline seeds
    still evaluate and record inline seed provenance.

- [x] Treat malformed direct initial workspaces mutating run artifacts as a
  paper-level codebase-candidate setup gap.
  - Status: fixed. Direct initial workspaces now have a pre-manifest schema:
    each entry must normalize to a `CandidateWorkspace` with safe files,
    present primary file, UTF-8 text, and valid evolve-block markers before
    any run artifacts are created or overwritten.
  - Verification: focused loop tests prove malformed direct initial workspaces
    leave existing history intact and write no manifest, while valid mapping
    records still evaluate and record workspace seed provenance.

- [x] Treat unreachable elite-only archive programs as an AlphaEvolve database
  fidelity gap.
  - Status: fixed. Elite-only archive programs are now reachable through
    explicit retained-archive sampling routes: best/exploit, metric, novelty,
    recency, selection, mixed inspiration, and migration-retained archive
    state. They still do not claim occupied-cell explore/random eligibility
    unless they enter a MAP-Elites cell.
  - Verification: focused island and public database tests cover elite-only
    resurfacing through retained strategies and occupied-cell exclusion, while
    MAP-Elites tests continue to assert `sampling_eligible=False` for
    elite-only retention.

- [x] Treat non-Python evolve-block marker handling as a paper-level
  representation boundary.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Status: fixed as a scoped representation claim. Paper-index docs now
    describe evolve blocks as implemented with explicit Python-file marker
    boundaries and unsupported non-Python marker diagnostics, while
    language-aware evolve-block marker grammars remain open. The code rejects
    marker-like declarations in non-`.py` workspace files with
    `unsupported_evolve_block_marker_syntax`, preventing JavaScript-style
    `// EVOLVE-BLOCK-START/END` markers from being silently treated as
    unmarked full-file replacement targets.

- [x] Treat already-solved smoke seeds as paper-level benchmark evidence gaps.
  - Status: fixed by classification. The paper benchmark coverage section now
    lists `sorting` as a neutral plateau/diversity smoke fixture whose seed
    already reaches `accuracy == 1.0`, and does not use it as seed-to-best
    optimization-pressure evidence. README, problem-format guidance, and
    ROADMAP now name `hello_world`, `circle_packing`, and
    `matrix_multiplication` as the current optimization-pressure smoke
    fixtures.

- [x] Treat missing durable LLM call artifacts as a paper-level runtime
  accounting gap.
  - Status: fixed for artifact persistence. Config-created ensembles now append
    call and reward rows to `llm_calls.jsonl`, including sequence ids,
    prompt/output hashes, retry/fallback state, backend provenance, scheduler
    counters, and reward linkage by `call_id`. Paper-level runtime accounting
    gaps now focus on replay/readers, resume reconstruction, and future async
    accounting.

- [x] Treat unbounded critique prompt retention as a paper-level reviewer
  fidelity gap.
  - Status: fixed for prompt construction and history retention. Critique
    provider prompts are built from bounded redacted base prompt, proposed
    mutation, and custom instruction sections. Generated-candidate
    `metadata.critique` now stores bounded redacted retained prompt/original/
    revised mutation text with SHA-256 hashes, character counts, truncation
    flags, and retention policy metadata. Reviewer-pool design and critique
    provider isolation remain open paper-level gaps.

- [x] Treat no-valid-mutation critique selection as a paper-level reviewer
  provenance gap.
  - Status: addressed. Critique selection now has paper-index-visible
    no-valid-mutation provenance: when both the original generated mutation and
    critique revision are invalid, LibreEvolve preserves the original generated
    mutation as the selected failure payload and records
    `fallback_reason="no_valid_mutation"` with both parser diagnostics.
  - Verification: focused loop tests cover invalid original plus invalid
    revised candidates in `diff` and `full` mutation modes. The paper status
    table now mentions deterministic no-valid-mutation selection provenance.

- [x] Treat missing wall-clock manifest timestamps as a paper-level runtime
  provenance gap.
  - Status: addressed for current non-resumed runs. The AlphaEvolve paper index
    now records UTC runtime wall-clock manifest timestamps with monotonic
    elapsed-budget linkage. Runtime manifests include start/update/finish
    timestamps, completed or aborted status-specific timestamps, and an initial
    process segment that defines the extension point for future resumed runs.
  - Verification: focused budget/loop tests cover timestamp schema and both
    completed and aborted manifests. Paper manifest tests pass.

- [x] Treat history-only `show` output for aborted runs as a paper-level run
  inspection gap.
  - Status: addressed. `show` now reports manifest runtime status for
    completed runs, aborted best-so-far runs, and partial manifests without
    runtime finalization. It keeps missing-manifest runs explicitly labeled as
    legacy history-only and rejects mismatched manifest/history row counts.
  - Verification: CLI tests cover completed, aborted-after-seed,
    aborted-after-candidate, missing-runtime, missing-manifest, and
    inconsistent manifest-history cases. The paper status row now names
    manifest-runtime-aware `show` status.

- [x] Separate generated run artifacts from problem-package provenance.
  - Status: addressed. Generated run-artifact directories under `runs/` are
    excluded from problem tree hashes with
    `reason: generated_run_artifacts`, while ordinary fixtures under `runs/`
    stay included. The paper status row now calls out generated-run artifact
    classification for problem provenance.
  - Verification: provenance tests cover fixture inclusion, active run-root
    exclusion, stale generated run exclusion, and unchanged `tree_hash` after
    stale generated artifact content changes.

- [x] Persist recovered LLM fallback attempts before paper-level scheduler
  provenance claims.
  - Status: addressed in current candidate history and run-level telemetry.
    Successful generated candidates store the retained mutation/critique/
    feedback call span under `metadata.llm_calls`, including recovered failed
    retry/fallback attempts, while config-created ensembles also append
    run-scoped `llm_calls.jsonl` call/reward rows.
  - Verification: loop regression
    `test_successful_candidate_persists_recovered_llm_fallback_span` proves a
    backend-0 provider failure followed by backend-1 fallback success persists
    both the error and ok call records on the successful candidate.

- [x] Distinguish configured plugins from executed plugins in run provenance.
  - Status: addressed. Runtime manifests include `runtime.plugin_state` with
    configured plugin labels, loaded runtime plugin identities,
    configured-without-loaded diagnostics, loaded-without-configured
    diagnostics, and an explicit marker that core `evolve()` does not resolve
    `Config.plugins`.
  - Verification: focused direct API tests cover both mismatch directions.

- [x] Keep accepted archive admission consistent with strict history records.
  - Status: addressed. Accepted archive admissions now prevalidate the strict
    candidate history record before mutating the live MAP-Elites/island archive.
    Malformed accepted records, including non-serializable metadata, fail before
    becoming `db.best()` or a parent/inspiration/migration source.
  - Verification: the completed code item documents focused database tests for
    non-serializable metadata failing before archive mutation and leaving
    `db.best()` empty. The paper index now calls out the accepted-admission
    prevalidation boundary while keeping rejected malformed-record persistence
    as a separate open gap.

- [x] Treat linked best-artifact export paths as a paper-level artifact safety
  gap.
  - Status: addressed for best export. Selected-best export refuses
    symlink or Windows-junction visible, temporary, and backup artifact paths
    before replacement or cleanup. This originally covered CLI best export; a
    later core-runtime slice moved direct `evolve()` materialization onto the
    same export boundary.
  - Verification: focused CLI tests cover linked `best.py`,
    symlink-capable linked `best_workspace`, Windows-junction
    `best_workspace`, and normal replacement/preservation behavior.
  - Follow-up: direct `evolve()` now materializes selected-best artifacts via
    the same core export path; see the completed code/roadmap items for that
    later slice.

- [x] Treat best-artifact rollback failures as a paper-level run artifact gap.
  - Status: addressed for best export. Failed replacement recovery records
    original export failure, secondary rollback/cleanup diagnostics, and
    preserved backup labels in the manifest. This originally covered CLI best
    export; a later core-runtime slice moved direct `evolve()` success/failure
    accounting onto the same manifest field.
  - Verification: focused CLI tests cover rollback success, rollback failure,
    cleanup failure, preserved backups, and manifest redaction of structured
    recovery diagnostics.
  - Follow-up: direct `evolve()` now records selected-best export success or
    failure through core runtime finalization; see the completed code/roadmap
    items for that later slice.

- [x] Treat shallow candidate materialization link checks as a paper-level
  codebase-candidate safety gap.
  - Status: addressed. Candidate materialization now recursively rejects
    symlink or Windows-junction entries under existing roots before cleanup or
    replacement, so stale linked entries are not silently removed or followed.
  - Verification: focused candidate tests cover normal stale replacement,
    nested symlink rejection when supported, Windows nested-junction rejection,
    and linked ancestor rejection.

- [x] Treat CausalPlugin factor exploration as a paper-level heuristic gap.
  - Status: addressed for fixed-factor exploration. The paper index and plugin
    docs now state that local causal guidance uses pull-once initialization
    before UCB-like scoring. Later work added parent-baseline reward context;
    the separate CausalEvolve scratchpad and counterfactual-baseline gaps
    remain open.
  - Verification: focused causal plugin tests cover stable pull-once selection,
    positive reward behavior with untried factors, all-factor-observed scoring,
    and retained metadata.

- [x] Treat raw evaluator source paths as a paper-level run-provenance safety
  gap.
  - Status: addressed. Evaluator source manifest records now use redacted
    problem-relative path labels plus path hashes for default and configured
    validator entrypoints, so paper-visible run provenance separates source
    identity from raw local filesystem disclosure.
  - Verification: focused evaluator provenance tests cover secret-like default
    and configured-stage validator filenames plus absolute problem-local
    configured validator paths.

- [x] Treat evaluator entrypoint hash read behavior as paper-visible
  provenance policy.
  - Status: addressed. Evaluator source manifest records now declare streamed
    full-file hashing through `source_hash_policy` and `hash_chunk_bytes`, and
    preserve structured redacted read-error diagnostics when source hashing
    fails.
  - Verification: focused evaluator provenance tests cover large default
    validator streaming, configured-stage read failures, and multi-stage
    evaluator source records.

- [x] Treat non-serializable evaluator returns as structured contract
  diagnostics.
  - Status: addressed. The validator runner writes results through a dedicated
    envelope, classifies non-JSON-serializable returns as `malformed_metrics`,
    and records bounded `metadata.malformed_metrics` diagnostics instead of
    collapsing them into generic subprocess failures.
  - Verification: focused evaluator tests cover object, set, bytes, NumPy
    scalar, and NumPy array payloads plus valid scalar metrics.

- [x] Treat unvalidated evaluator result dataclasses as a structured-evaluation
  fidelity gap.
  - Status: addressed. `EvaluationResult` and `EvaluationStageResult` enforce
    JSON-safe finite metrics, safe diagnostics, safe metadata, and manifest-safe
    stage labels before persistence-facing `to_dict()` output.
  - Verification: focused evaluator tests cover construction-time validation,
    post-construction mutation rejection, strict JSON serialization, and
    database-compatible `Program` construction.

- [x] Make skipped or empty seed workspaces visible in setup diagnostics.
  - Status: addressed. Seed loading now records hidden/cache entries,
    unsupported top-level files, empty seed directories, and fully skipped
    seed directories as setup diagnostics, persists them under
    `manifest.problem.seed_skipped`, and includes previews in no-seed errors.
  - Verification: focused loader, database, and loop tests cover empty and
    fully skipped seed workspaces, unsupported-only seed roots, mixed roots,
    and manifest persistence.

- [x] Treat unbounded candidate workspace size as a paper-level codebase
  representation gap.
  - Status: addressed for the current text-workspace representation. LibreEvolve
    now rejects oversized workspaces using manifest-visible file-count,
    per-file, and total text limits instead of accepting unbounded source into
    history, prompts, evaluator materialization, or best exports. Spillover and
    hash-only persistence are not implemented and are stated as absent policy.
  - Verification: focused tests cover workspace model limits, mutation-created
    oversized files, configured manifest policy, database rejection, and direct
    seed/workspace preflight.

- [x] Clarify Python-primary seed workspaces versus general candidate
  abstractions.
  - Status: addressed for the current implementation scope. LibreEvolve now
    treats no-Python seed workspaces as skipped setup inputs instead of
    accidentally choosing a non-Python primary `code` value, while first-class
    non-code candidate abstractions remain an open AlphaEvolve gap.
  - Verification: focused loader tests cover text-only seed workspace
    diagnostics, and the paper index now describes Python-primary
    seed-workspace loading separately from future flexible candidate
    abstractions.

- [x] Treat multiline proposal metadata loss as a paper-level idea-capture gap.
  - Status: addressed for the current proposal-capture surface. LibreEvolve now
    preserves bounded multiline idea/rationale/hypothesis blocks as structured
    proposal metadata and rejects ambiguous wrapped colon-style metadata before
    mutation application, keeping AlphaEvolve idea-capture claims scoped to
    accounted response text.
  - Verification: focused parser and loop tests cover bounded multiline
    proposal capture, malformed wrapped continuation rejection, and failure
    diagnostics; the paper index documents the accepted proposal-capture
    envelope.

- [x] Preserve AlphaEvolve's cross-change consistency prompt contract.
  - Status: addressed for the built-in AlphaEvolve-like prompt. Default
    mutation instructions now tell the LLM to keep same-response edits
    consistent and to include any required helper/config/file/import/block
    definitions or topology changes with the edit that references them.
    Configured prompt variants remain user-responsible compatibility inputs
    and are documented as allowed to omit this contract.
  - Verification: focused prompt tests cover default diff and full-mode
    consistency wording, and the paper index scopes the claim to the built-in
    prompt rather than all configured prompt seeds.

- [x] Scope CausalEvolve-inspired factor guidance across mutation modes.
  - Status: addressed for the current token-pattern guidance surface.
    CausalPlugin now applies its fixed local factor detector to both diff-mode
    SEARCH/REPLACE payloads and full-mode replacement text, while paper docs
    continue to state that this is not an LLM causal scratchpad or
    LLM-discovered causal-variable system.
  - Verification: focused causal plugin tests cover full-mode factor detection
    and mutation-mode history metadata; the paper index describes both mutation
    paths and keeps the broader CausalEvolve limitation open.

- [x] Link paper-index rows to the authoritative TODO coverage.
  - Status: documented as a maintained `papers/README.md` mapping rather than
    widening each already-large implementation-status row. Every manifest row
    now has an explicit `docs/todo/...` coverage reference to the open and/or
    completed backlog files that support its current paper-index status.
  - Verification: a checked-in paper-manifest test reads
    `papers/download_manifest.json` and proves each manifest id has exactly one
    TODO-coverage mapping row containing a `docs/todo/` reference.

- [x] Add explicit compiler/hardware/systems benchmark coverage decisions.
  - Status: satisfied as explicit scope documentation rather than implemented
    fixtures. `papers/README.md` marks Magellan and ArchAgent as background-only
    rows and its benchmark coverage note states that compiler, hardware,
    systems, kernel, and scheduling-style AlphaEvolve targets are not yet
    represented.
  - Verification: the paper index now keeps these application families scoped
    away from supported benchmark claims while the holdout/generalization and
    representative-benchmark TODOs remain open for future fixtures.

- [x] Structured proposal idea/rationale capture.
  - Status: implemented for the AlphaEvolve-like response-envelope boundary.
    LibreEvolve can request and persist proposal idea/rationale/hypothesis
    metadata separately from patch payloads, preserve diff-only compatibility,
    render bounded prior proposal summaries for parent/inspiration candidates,
    and keep critique-selected proposal provenance tied to the chosen mutation.
  - Verification: current code and docs keep the remaining proposal
    scoring/indexed-retrieval capability open under the evolutionary-database
    resurfacing gap, while this completed item covers the response-format and
    metadata-capture requirement from the paper-level TODO.

- [x] Define plugin hook phase semantics before treating paper-inspired
  plugins as controllable search components.
  - Status: documented current ordering is the stable local plugin API. The
    start hook is intentionally post-parent and pre-prompt, so paper-inspired
    plugins can influence inspiration sampling and prompt construction for the
    active generation but not the parent that was already selected.
  - Verification: the new loop regression covers a database-mutating
    `on_generation_start()` hook, proving parent selection remains pre-hook
    while the injected high-scoring program is available to post-hook
    inspiration sampling. Existing plugin tests and docs cover prompt context,
    score composition, hook failures, and artifact provenance boundaries.

- [x] Normalize paper-manifest title metadata or rename it as a slug.
  - Status: resolved by documenting the existing compatibility semantics.
    Manifest `title` values remain inventory/display slugs derived from local
    cache names, while `papers/README.md` remains the authoritative source for
    paper-facing titles, implementation status, roles, and benchmark decisions.
  - Verification: README and `papers/README.md` now explicitly say manifest
    titles are not authoritative bibliographic metadata, and a paper-manifest
    docs regression test guards that wording.

- [x] Keep rejected database-admission diagnostics finite.
  - Status: rejected archive-admission diagnostics now remain machine-readable
    even when a hook-mutated candidate carries non-finite top-level score data.
    `ProgramDatabase.log_failure()` normalizes non-finite failure score and
    evaluation fitness values to finite JSON-safe sentinels with explicit
    diagnostics whenever a rejected admission event is attached.
  - Verification: focused database coverage persists a rejected
    invalid-evaluation candidate with `fitness=inf` and `metrics.score=inf` to
    normal `failure_history.jsonl`, while retaining the prior quarantine
    behavior for no-admission non-finite failures.

- [x] Treat missing durable LLM call replay/readers as a paper-level runtime
  accounting gap.
  - Status: the immediate paper-level reader gap is closed by
    `load_llm_call_ledger()`, which validates durable LLM call and reward
    provenance before treating it as replay/accounting evidence. The reader
    checks call sequence continuity, duplicate ids, backend consistency,
    successful-call reward linkage, duplicate rewards, prompt/output hashes,
    safe labels, and scheduler counter transitions.
  - Verification: ensemble replay-reader tests cover valid call/reward replay,
    malformed sequence, duplicate-id, unknown-call, failed-call, duplicate
    reward, backend mismatch/range, counter inconsistency, duplicate JSON-name,
    unsafe-role, reward-cap, and reward/raw-reward failures. Full async worker
    and scheduler-state resume remain future work rather than part of this
    reader gap.

- [x] Add schema-versioned run artifacts before claiming resumable experiment
  database fidelity.
  - Status: current run artifacts now have explicit local v1 schema metadata.
    `manifest.json` declares `schema_version` and `artifact_schema`, and
    current append-only rows for accepted history, failure history, LLM
    call/reward telemetry, and prompt history declare `schema_version` plus
    `record_schema`.
  - Verification: database, prompt-database, and LLM ledger tests cover v1
    schema markers, legacy missing-schema compatibility where readers support
    it, and unsupported declared-schema rejection. README/run-artifact docs and
    the paper index now describe the v1/legacy boundary while keeping full
    migration and resumable database replay open.

- [x] Treat invalid-encoding resume history readers as paper-level run-artifact
  provenance gaps.
  - Status: the immediate accepted-history resume/query reader now has the same
    line-numbered UTF-8 decoding contract as `libreevolve show`.
    `load_accepted_history_index()` rejects invalid bytes before JSON parsing
    and reports the affected `history.jsonl` row number.
  - Verification: focused database tests cover invalid UTF-8 at line 1 and
    invalid UTF-8 after a valid row, along with accepted-history schema, JSON,
    id, metric, and finite-fitness validation. Full archive/controller resume
    remains broader future work, but this paper-level decoding gap is closed.

- [x] Treat duplicate accepted-history ids in future resume loaders as a
  paper-level database identity gap.
  - Status: closed for the checked accepted-history restore/query boundary.
    `load_accepted_history_index()` rejects duplicate accepted program ids with
    the current row number and the first-seen row number instead of silently
    overwriting or versioning restored records.
  - Verification: database restore-reader tests cover identical and divergent
    duplicate accepted ids in `history.jsonl`, and existing writer/inspection
    tests cover duplicate accepted-history rejection and `show` diagnostics.

- [x] Treat unsafe accepted-history ids in future resume loaders as a
  paper-level database identity gap.
  - Status: closed for the checked accepted-history restore/query boundary.
    `load_accepted_history_index()` reuses `Program` identity validation, so
    restored ids, parent ids, and lineage entries must be manifest-safe and
    cannot contain newline characters, secret-like text, or Unicode format
    controls.
  - Verification: database restore-reader tests cover unsafe ids containing a
    newline, a provider-token-shaped secret, and a Unicode right-to-left
    override. Existing run-inspection tests cover equivalent unsafe-id
    diagnostics for `libreevolve show`.

- [x] Crash-safe append policy for JSONL experiment database streams.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: LibreEvolve now documents and implements a complete-line
    durability contract for append-only experiment streams. Managed JSONL
    appends flush and fsync accepted rows, and a later append repairs a torn
    final fragment by truncating to the previous complete line and recording a
    bounded quarantine diagnostic. README and run-artifact docs now distinguish
    strict serialization plus local complete-line durability from broader full
    checkpoint/replay work.
  - Verification: tests simulate a torn `history.jsonl` final append and prove
    the prior complete row survives, the fragment is quarantined, and the next
    valid row appends cleanly. The targeted shared-stream suite passed across
    candidate, prompt, LLM-call, plugin export, and quarantine JSONL users.

- [x] Bound ensemble-level LLM retry and fallback multiplication.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: the ensemble scheduler now has a paper-visible total-attempt cap
    for each logical LLM call. `llm_max_call_attempts` is validated in config
    and direct scheduler construction, exposed through the CLI, persisted in
    manifests, and recorded in call telemetry with the attempt index. When the
    cap is exhausted, no further same-backend retry or fallback backend is
    attempted.
  - Verification: focused tests cover constructor/config/CLI rejection above
    the cap, config-to-ensemble propagation, manifest persistence, and a failed
    first backend where the cap prevents both retry and fallback.

- [x] Keep restored runtime budget state finite and manifest-safe.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Status: restored runtime budget snapshots are checked through
    `validate_restored_budget_snapshot()`, and future controller/resume state
    now has `validate_controller_budget_state()` with a local v1 schema. The
    controller state validator reuses restored snapshot validation, rejects
    malformed consumed counters, and keeps non-finite elapsed values from
    entering budget replay through controller events.
  - Verification: focused budget tests cover malformed restored snapshots,
    malformed controller consumed state, malformed elapsed values, malformed
    accounting, defensive copies, and no active-counter mutation after invalid
    controller events.

- [x] Treat restored/controller budget event kinds as paper-level accounting gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Status: future controller budget events now have an explicit schema and
    durable event kinds. `seed_evaluation` and `candidate_evaluation` are
    validated separately before replay, preserving baseline/generated
    evaluation accounting for future resume and paper-level comparison.
  - Verification: focused budget tests cover valid event replay, malformed
    event kind, malformed sequence, malformed stop reason, unsupported fields,
    missing fields, and non-contiguous restored event sequences.

- [x] Document flexible candidate abstraction as a deliberate paper divergence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1.
  - Status: LibreEvolve still does not implement AlphaEvolve's first-class
    candidate abstraction API for raw solution strings, constructor functions,
    bespoke search algorithms, or paired solution/search representations.
    README, architecture docs, problem-format docs, ROADMAP, and the paper
    index now document the current supported abstraction as bounded UTF-8
    code-file-set evolution with a primary-file compatibility view.
  - Verification: source/docs search confirms the open code and paper TODOs
    were removed, while current docs retain the limitation as a documented
    divergence rather than an unqualified AlphaEvolve feature claim.

- [x] Treat configured prompt text as sensitive reproducibility provenance.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.3, 2.5, and 2.6.
  - Status: startup manifests now retain prompt-bearing config through a
    redacted, bounded, hash-backed policy instead of silently preserving known
    credential-shaped prompt text verbatim. `prompt_variants`,
    `prompt_format_options` alternative text, `critique_prompt`, and
    `llm_feedback[].prompt` keep reproducibility hashes and length/redaction
    metadata.
  - Verification: manifest tests prove a shared secret-like prompt string is
    absent from `manifest.json` while redacted text plus SHA-256 and length
    metadata remain; the paper index now describes this as current behavior.

- [x] AlphaEvolve-style stochastic prompt formatting.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Status: LibreEvolve now supports weighted stochastic prompt-format markers
    in configured prompt templates. `prompt_format_options` defines
    human-authored alternatives and probabilities for `[[prompt:name]]`
    markers, expansion uses the run-local RNG, repeated markers reuse the same
    selected alternative within one prompt, and prompt diagnostics persist the
    selected option index, weight, occurrence count, and text hash.
  - Verification: prompt tests cover deterministic weighted expansion,
    repeated-marker reuse, missing marker options, and invalid weights; config
    tests cover accepted/rejected schemas; loop tests prove prompt history
    includes stochastic-format diagnostics and manifests retain normalized
    `prompt_format_options`.

- [x] Add a paper-cache rehydration command for fresh checkouts.
  - Paper-index evidence: `papers/README.md` and README distinguish the local
    PDF cache from the committed manifests, while AlphaEvolve-alignment audit
    work depends on local PDFs such as
    `papers/2506.13131__AlphaEvolve.pdf`.
  - Status: `py -3.12 -m libreevolve.tools.paper_manifest --rehydrate` now
    restores the ignored local PDF cache from the committed JSON/CSV manifests.
    It downloads manifest URLs, streams bytes to a temporary file, verifies
    byte count and SHA-256 before installing, skips already matching PDFs
    unless `--force` is supplied, rejects link-backed or non-regular existing
    targets, and reports network/integrity failures in text or JSON output.
    README, `papers/README.md`, and contributor docs reference the command.
  - Verification: `tests/test_paper_manifest.py` covers missing-PDF download,
    existing-PDF skip, forced redownload, redacted network-failure reporting,
    and the existing strict manifest/local-PDF validation path.

- [x] Make workspace topology mutation intent unambiguous.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.3.
  - Status: workspace file-section parsing now distinguishes topology commands
    from ordinary command-leading filenames through the explicit
    `<<<FILE PATH ...>>>` form. Duplicate file edit sections, duplicate block
    sections, duplicate topology sources, duplicate move targets, duplicate
    `PRIMARY` sections, non-empty topology command bodies, ambiguous primary
    deletion, same-mutation primary targets, edit/delete/move collisions,
    chained move/delete sources, same-line envelopes, unknown named full-block
    targets, and explicit missing primary files are rejected before partial
    workspace replacement.
  - Verification: focused candidate tests cover command-leading ordinary
    filenames, empty `PATH` rejection, topology commands, duplicate/colliding
    topology sections, primary replacement rules, and same-line file/block
    envelope rejection; README, architecture, and problem-format docs now
    describe the current topology prevalidation policy instead of stale
    incomplete-collision caveats.

- [x] Existing/custom LLM backend extension point.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 2 and Section 2.3.
  - Status: LibreEvolve now supports configured custom LLM backends in addition
    to OpenAI, Anthropic, and Ollama. `type: custom` backend specs declare an
    importable backend class through manifest-safe `class_path`, optional
    JSON-safe `kwargs`, top-level `model`/`max_tokens`, and normal scheduler
    metadata. The imported object must implement the existing `LLMBackend`
    protocol and is invoked through the same ensemble prompt validation, call
    role propagation, retry/fallback, and telemetry boundary as built-in
    providers.
  - Verification: focused config and ensemble tests cover valid/invalid custom
    specs, import-path construction, constructor kwargs, call-role propagation,
    metadata retention, post-validation mutation revalidation, and rejection of
    objects that do not satisfy the backend protocol. README, backend docs, and
    configuration docs describe the new custom backend surface.

- [x] Validated LLM request parameters with call telemetry.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 2 and Sections 2.2-2.3.
  - Status: built-in backend specs now accept provider-supported request
    parameters for temperature, top-p, stop sequences, and request seeds.
    OpenAI, Anthropic, and Ollama adapters validate the fields before SDK
    calls, forward only supported payload keys for their provider/API mode, and
    expose normalized `request_parameters` for ensemble telemetry.
    `llm_calls.jsonl` call rows now persist the effective normalized request
    parameter object and replay validation rejects unsafe or malformed restored
    values. Structured system/developer/user prompt serialization remains an
    open prompt-fidelity gap.
  - Verification: focused config/backend/ensemble tests cover valid and invalid
    request-parameter specs, provider-specific unsupported seed/stop
    combinations, exact SDK payload kwargs for OpenAI Chat Completions,
    OpenAI Responses, Anthropic Messages, and Ollama Chat, `build_llm()`
    propagation, defensive telemetry copies, and redaction of unsafe
    request-parameter telemetry.

- [x] Persist final LLM scheduler-state snapshots for paper-level audits.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 2 and Sections 2.2-2.3.
  - Status: final manifests now expose `runtime.llm_scheduler` so paper-level
    inspection can see the terminal LLM ensemble scheduler state. Snapshot rows
    use schema `libreevolve.llm_scheduler_state.v1` and retain the defensive
    `LLMEnsemble.scheduler_state` fields needed to audit backend counts,
    rewards, rewarded/unrewarded successful call ids, and call-history
    retention after validating the snapshot against the ensemble restore
    contract. No-LLM, custom non-ensemble, unvalidated custom-state, and
    invalid-state cases are recorded explicitly instead of being silent.
  - Remaining paper gap: this does not implement full AlphaEvolve-scale
    checkpoint/resume; persisted snapshots are not loaded into resumed
    searches, and role-specific scheduler policies remain open.
  - Verification: loop tests prove zero-generation manifests mark the scheduler
    as `not_initialized`, one-generation ensemble manifests persist the
    expected final scheduler snapshot, and malformed or unvalidated exposed
    state is recorded as `invalid`.

- [x] Scope non-mutation LLM calls as telemetry-only scheduler events.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 2 and Sections 2.2-2.3.
  - Status: mutation calls are reward-accounted scheduler pulls, while
    critique, feedback, and meta-prompt calls persist as `telemetry_only`
    records. They do not increment mutation backend counts, do not advance
    `LLMEnsemble.total`, and cannot be rewarded through the call-ledger
    restore path.
  - Remaining paper gap: configurable role-specific scheduler state,
    role-specific reward/no-reward policy, restored/resumable scheduler state,
    and provider token/cost/retry budgets remain open.
  - Verification: ensemble tests cover auxiliary roles preserving mutation
    scheduler accounting, telemetry-only call rows, and rejection of rewards
    linked to telemetry-only calls.

- [x] Persist compact island cursor snapshots for paper-level audits.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: final manifests now include `runtime.history.archive_state` with
    schema `libreevolve.island_state.v1`. The snapshot records the current
    round-robin `next_island_id`, retained-state-change cursor policy,
    archive/migration/metric-sampling sequence counters, archive sequence by
    program id, and compact per-island occupancy/elite counts.
  - Remaining paper gap: persisted cursor snapshots are not restored into
    resumed searches, and full archive contents, migration events, and
    descriptor-normalization state are still not replayable checkpoints.
  - Verification: focused island, database, and loop tests prove the snapshot
    is exposed directly and in `manifest.json`, including the case where a
    non-admitted candidate does not consume the island cursor.

- [x] Persist migration placement events for paper-level audits.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: `archive_events.jsonl` now records versioned migration placement
    events emitted during scheduled ring migration. Rows use schema
    `libreevolve.archive_event.v1` and preserve source island, target island,
    canonical program id, duplicate-target skip reasons, cell placement, and
    selection score where available.
  - Remaining paper gap: the event stream is not yet a full replayable
    MAP-Elites checkpoint; archive cell/elite snapshots,
    descriptor-normalization state, and resume loaders remain open.
  - Verification: database tests prove scheduled migration writes versioned
    archive-event rows, and run-manifest schema tests advertise the stream.

- [x] Correct paper-index redaction evidence for bearer credentials.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Status: bearer credentials are no longer listed as current redaction
    failures. The shared redaction helper handles `Authorization: Bearer ...`
    and copied evaluator text artifacts use that path before persistence.
  - Remaining paper gap: this is still basic pattern redaction, not a complete
    paper-grade retention scanner or hash-only prompt/history policy.
  - Verification: focused tests cover direct bearer redaction and copied
    artifact redaction for a Hugging Face-style bearer token.

- [x] Bound persisted evaluator diagnostics for long program databases.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: validator stdout/stderr are no longer persisted as unbounded full
    strings. They pass through UTF-8 replacement, shared secret redaction, and
    the configurable `evaluator_output_max_chars` cap before they enter
    `EvaluationResult`, stage results, history, or prompt summaries. The
    default cap is `20000`, and truncation metadata is retained under
    `evaluation.metadata.diagnostic_output`.
  - Remaining paper gap: this is a diagnostic retention cap, not full
    artifact-spillover or semantic summarization for very large outputs; use
    evaluator artifact copy-out for intentionally retained large files.
  - Verification: evaluator tests cover explicit small caps, redaction-before-
    truncation, invalid UTF-8 replacement diagnostics, aggregate configured
    stage output caps, and the default persisted stdout/stderr cap.

- [x] Scope prompt-program history as telemetry-only until replay exists.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Status: the paper index, README, architecture notes, and run-artifact
    reference describe `prompt_history.jsonl` as append-only audit telemetry
    rather than a prompt-archive checkpoint. The open paper gap is now limited
    to replay/checkpoint restore before prompt-program archives are claimed as
    resumable AlphaEvolve-style experiment state.
  - Verification: meta-prompt tests cover strict current-schema history
    loading for tooling, while `PromptDatabase` construction still seeds
    configured templates instead of restoring prompt arms from the stream.

- [x] Narrow run identity/provenance paper TODO to remaining replay and
  transitive-artifact gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Status: run ids, fail/overwrite collision policy, direct evaluator
    entrypoint hashes, bounded source/problem hashes, plugin module hashes,
    evaluator-helper import precedence, plugin alias/cadence preflight, built-in
    provider credential/client preflight, direct-runtime provider preflight, and
    provider-free zero-generation baselines are no longer listed as required
    paper work.
  - Remaining paper gap: transitive evaluator import/data provenance, aggregate
    emitted-artifact hashes, true resume/replay semantics, deterministic
    lineage-id policy, live provider authentication, and stronger sandbox or
    network-egress policy.

- [x] Keep CausalEvolve-inspired factor guidance explicitly paper-limited.
  - Paper: `2603.14575__CausalEvolve.pdf`.
  - Status: README, plugin docs, the plugin docstring, and the paper index now
    scope `causal` as token-pattern outcome-factor guidance, not an LLM causal
    scratchpad or LLM-discovered causal-variable system. Parent-baseline reward
    attribution is documented as parent-aware but not a causal counterfactual.
  - Remaining implementation gap: LLM causal scratchpad, POMDP/causal framing,
    abductive factor creation, structured causal knowledge reuse, and
    counterfactual baseline attribution are not implemented and remain outside
    current claims unless the plugin is promoted beyond fixed token-pattern
    guidance.
  - Verification: repository-wide search shows CausalEvolve references are
    scoped to inspired/not-paper-complete wording, and causal plugin tests cover
    fixed-factor detection, malformed history/evidence handling, pull-once
    selection, full-mode detection, and parent-baseline metadata.

- [x] Keep DeepEvolve-inspired retrieval guidance explicitly paper-limited.
  - Paper: `2510.06056__DeepEvolve.pdf`.
  - Status: README, plugin docs, the plugin docstring, and the paper index now
    scope `deep_research` as best-effort retrieval context, not DeepEvolve's
    cross-file debugging, systematic refinement, or hypothesis loop. The docs
    also identify current provenance as best-effort rather than audit-grade
    source integrity.
  - Remaining implementation gap: task/failure/local-paper query grounding,
    ranked-source provenance, full provider-payload persistence,
    source-content trust policy, full run resume, and the DeepEvolve-style
    cross-file debugging/refinement loop are not implemented. The live
    retrieval transport/integrity gap remains open separately.
  - Verification: repository-wide search shows DeepEvolve references are
    scoped to inspired/not-paper-complete wording, and DeepResearch tests cover
    bounded retrieval metadata, request URL summaries, cache behavior,
    untrusted prompt rendering, payload bounds, and structured retrieval
    failures.

- [x] Keep UCB-style backend routing explicitly heuristic, bounded, and
  non-canonical.
  - Paper: `auer-cesa-bianchi-fischer-2002`.
  - Status: `LLMEnsemble` is documented as a heuristic UCB-style scheduler,
    not a canonical regret-analyzed UCB1 implementation. Rewards are finite,
    non-negative, capped to `1.0`, and linked to one successful rewardable call
    id; total-selection behavior and telemetry-only auxiliary roles are
    documented in backend docs and architecture notes.
  - Remaining implementation gap: role-specific auxiliary scheduler accounting,
    deterministic call identifiers, provider token/cost budgets,
    adapter-internal retry accounting, and restored scheduler replay remain
    open separately. Canonical UCB1 regret assumptions are outside current
    claims unless the scheduler is promoted beyond heuristic routing.
  - Verification: focused ensemble tests cover pull-once initialization,
    capped rewards, invalid reward rejection, reward-call ledger validation,
    scheduler-state restoration checks, normalized throughput/depth metadata,
    and effective scheduler-policy telemetry.

- [x] Track proposal-batch sampling as a paper-visible AlphaEvolve runtime gap.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Superseded status: this tracking entry identified proposal batches as a
    paper-visible runtime gap. The current loop now implements sequential
    `proposals_per_generation` batches with sibling-candidate history
    accounting, deterministic per-proposal ids, and manifest config retention.
  - Remaining implementation gap: async LLM sampler queues, parallel evaluator
    workers, and distributed throughput remain open in the paper TODOs.
  - Verification: focused loop tests prove a one-generation batch can write
    multiple generated candidate records with coherent generation counters.

- [x] Scope structured prompt-role fidelity as single-message bundled adapter
  behavior.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Figure 2 and Sections 2.2-2.3.
  - Status: the paper index, README, backend docs, and architecture notes state
    that bundled adapters send rendered mutation, critique, feedback, and
    meta-prompt text as one user message/input item. Validated call roles are
    telemetry/backend-hook labels and are not structured
    system/developer/user prompt partitions.
  - Remaining implementation gap: structured prompt-message policy,
    persisted prompt-role hashes, and tests for mutation, critique, feedback,
    and meta-prompt structured prompts remain open in code and roadmap TODOs.
  - Verification: focused search confirms the current single-message boundary
    is documented in the paper index, README, backend docs, and architecture
    notes, while code/roadmap TODOs retain the implementation work.

- [x] Narrow compute-budget paper TODO to remaining provider and benchmark
  budget gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.6 and 4.
  - Status: budget configuration, consumed evaluator counters, structured stop
    reasons, normal/aborted runtime manifests, invalid-manifest diagnostics,
    and terminal budget-exhaustion history annotations are no longer listed as
    missing paper work.
  - Remaining paper gap: adapter-internal retry accounting, token/cost budgets,
    provider-call deadlines, accelerator/async-worker counters, and
    equal-budget benchmark reports remain open.
  - Verification: focused budget/code search shows `RunBudget`, manifest
    runtime writing, detailed evaluator-counter accounting, and terminal
    budget-stop metadata exist, while provider-call timeout and retry-budget
    TODOs remain open in code and roadmap files.

- [x] Narrow paper redaction TODO after provider-token and bearer fixtures
  landed.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Status: common provider-token prefixes, key/token/secret/password
    assignments, quoted assignment values, and `Authorization: Bearer ...`
    headers are no longer listed as missing scanner fixtures. Copied evaluator
    text artifacts use the shared redaction helper by default.
  - Remaining paper gap: the project still lacks a comprehensive scanner
    contract covering exact credential classes, exclusions, false-positive
    behavior, quarantine snapshots, prompt/history persistence, and opt-in raw
    retention risk.
  - Verification: focused redaction/evaluator tests cover provider-token
    shapes, quoted assignments, uppercase variants, and bearer-header copied
    artifact redaction.

- [x] Narrow run replay/provenance paper TODO to remaining replay and
  transitive-artifact surfaces.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.4, and 2.6.
  - Status: the required-result clause no longer lists already implemented
    run ids, collision policy, direct evaluator hashes, bounded source/problem
    hashes, plugin module hashes, evaluator-helper precedence, plugin alias and
    cadence preflight, provider client preflight, provider-free zero-generation
    baselines, or conservative positive-generation provider-readiness ordering
    as missing work.
  - Remaining paper gap: true resume semantics, transitive evaluator import and
    data provenance, validated plugin specs/constructor parameters, aggregate
    emitted-artifact hashes, completed-run artifact inventory hardening,
    deterministic lineage ids or an explicit UUID replay exclusion, live
    provider authentication, and stronger sandbox/network policy remain open.
  - Verification: focused provenance, loop, and database tests cover manifest
    provenance wiring, direct evaluator/source/problem/plugin module hashes,
    archive-state snapshots, and startup/preflight ordering.

- [x] Narrow rich prompt-rendering TODO to remaining artifact content,
  metadata, and packing gaps.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.2.
  - Status: prompt construction already renders bounded/redacted parent
    summaries for stage status, stdout/stderr, retry/sample attempts,
    LLM-grader feedback, copied/skipped evaluator artifact path/hash metadata,
    and failed-trial evaluator summaries.
  - Remaining paper gap: artifact-content retrieval, fuller validator metadata,
    specialized aggregate syntax diagnostics, richer failure-memory grader
    summaries, and deterministic token-aware section-priority packing remain
    open.
  - Verification: focused prompt and loop tests cover feedback prompt sections,
    artifact path/hash summaries, skipped-artifact diagnostics, final
    `prompt_max_chars` capping, and redaction of prompt-visible diagnostics.
- [x] Treat LLM call identifiers as replayable ordered-stream evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.3, and 2.6.
  - Requirement: large-budget LLM/evaluator experiments need auditable call
    traces linking prompts, outputs, rewards, and scheduler state.
  - Status: `LLMEnsemble` now emits deterministic call ids for matching
    ordered call streams using call sequence, backend/role/attempt
    coordinates, and prompt hash. The ids remain unique for repeated identical
    calls within one stream.
  - Remaining gap: full experiment replay still needs deterministic lineage
    ids, prompt archive restore, RNG-state restore, and provider nondeterminism
    boundaries.
  - Verification: focused ensemble tests cover stable call ids across matching
    deterministic streams and distinct ids for repeated identical calls.

- [x] Make prompt-program history replayable at the prompt-archive boundary.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Requirement: the prompt database is part of the evolutionary system and
    should preserve prompt lineage, selection statistics, and prompt-fitness
    evidence across long-running or resumed experiments.
  - Status: `PromptDatabase` now restores live prompt-program state from
    non-empty `prompt_history.jsonl` files, including prompt ids, lineage,
    uses, reward sums, metadata, and invalid-mutation penalty state. Replay
    rejects unknown score references and incompatible reward policies.
  - Remaining paper gap: full AlphaEvolve-style experiment resume still needs
    archive/controller checkpoints, run-local RNG restore, deterministic
    lineage ids, and provider nondeterminism boundaries.
  - Verification: focused meta-prompt tests cover scored prompt replay,
    penalty replay, corrupt reference rejection, and reward-policy
    compatibility checks.

- [x] Persist framework RNG state for paper-level reproducibility evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Requirement: long-running evolutionary experiments should retain enough
    controller state to audit and eventually resume seeded stochastic choices.
  - Status: completed and aborted runtime manifests now persist the final
    run-local `random.Random` state under `runtime.rng` with schema
    `python.random.mt19937.v1`, the configured seed, full JSON-safe state,
    `state_sha256`, and the `random.Random.setstate` restore entrypoint.
  - Remaining paper gap: full AlphaEvolve-style experiment replay still needs
    archive/controller restore, restored RNG snapshot wiring, and
    plugin/provider nondeterminism boundaries.
  - Verification: focused loop tests cover snapshot round-trip equivalence and
    completed/aborted manifest persistence.

- [x] Add checked RNG snapshot restore boundary for seeded replay evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.6.
  - Status: `load_runtime_rng_state_snapshot()` validates manifest
    `runtime.rng` records and `restore_runtime_rng_state_snapshot()` restores a
    `random.Random` only after schema/hash/restorability checks.
  - Remaining paper gap: full experiment replay still needs resumed-loop
    integration and plugin/provider nondeterminism boundaries.
  - Verification: focused loop tests cover valid manifest loading, defensive
    validation, missing RNG snapshots, and hash mismatch rejection.

- [x] Add checked compact archive-state reader for paper-level replay evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: `load_runtime_archive_state_snapshot()` now validates
    `manifest.json.runtime.history.archive_state` before future resume use,
    including cursor bounds, sequence counters, manifest-safe program ids, and
    per-island count records.
  - Remaining paper gap: full experiment replay still needs live cursor
    application plus full archive cell/elite and descriptor-normalization
    state.
  - Verification: focused database/island tests cover valid manifest loading,
    defensive copies, missing archive state, invalid island order, and unsafe
    sequence-map ids.

- [x] Add checked migration-event reader for paper-level replay evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: `load_archive_event_records()` validates persisted
    `archive_events.jsonl` migration rows for schema, sequence order,
    canonical-id policy, program ids, island ids, cells, and selection scores.
  - Remaining paper gap: full experiment replay still needs to apply migration
    events with complete archive cell/elite and descriptor-normalization state.
  - Verification: focused database tests cover valid and malformed archive
    event streams.

- [x] Add direct compact island-cursor restore for paper-level replay evidence.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: `IslandModel.restore_cursor_state()` now applies compact
    island-assignment and sequence state from a validated snapshot to a live
    island model while explicitly leaving archive contents unrestored.
  - Remaining paper gap: full experiment replay still needs MAP-Elites
    cell/elite contents, descriptor-normalization state, migration replay, and
    resumed-loop integration.
  - Verification: focused island/database/loop tests cover restored cursor
    assignment, sequence continuation, and invalid snapshot rejection.
- [x] Add provenance path and Git status Unicode-control evidence for papers.
  - Spec evidence: paper-level provenance labels should be auditable and safe
    to render when comparing experiment artifacts.
  - Status: source/problem tree paths, skipped path diagnostics, plugin module
    path labels, and Git dirty-status entries now escape Unicode format
    controls, retain raw hashes, and are documented as protected provenance
    labels.
  - Remaining scoped gap: paper claims still need any newly identified durable
    provenance label families to receive the same explicit policy.
  - Verification: focused provenance tests cover included/skipped paths,
    external plugin module paths, Git dirty-status entries, U+202E escaping,
    and ordinary non-ASCII labels.

- [x] Add known-lockfile hash provenance to paper environment evidence.
  - Spec evidence: paper-level reproducibility claims need environment identity
    beyond direct dependency declarations.
  - Status: manifests now record hash-only metadata for known project-root
    lockfiles and paper docs scope this as direct-dependency plus
    known-lockfile hash evidence, not complete reproduction evidence.
  - Remaining paper gap: full package freeze interpretation, transitive
    dependency versions, numerical backend/accelerator details, live provider
    service/API versions, provider cost or remote provider-side default capture, and private
    package-source policy remain open.
  - Verification: focused runtime-environment provenance tests cover lockfile
    hash records, aggregate hash changes, missing and oversized lockfiles, and
    unreadable diagnostics.

- [x] Add installed-package snapshot evidence for paper environment provenance.
  - Spec evidence: paper-level reproducibility claims need package-version
    identity beyond declared direct dependencies.
  - Status: manifests now record bounded installed distribution name/version
    snapshots and an aggregate full-record hash, while paper docs still avoid
    treating this as complete reproduction evidence.
  - Remaining paper gap: complete `pip freeze` install-source/options
    semantics, broader build provenance, numerical backend/accelerator
    details, live provider service/API versions, provider
    cost or remote provider-side default capture, and private package-source policy remain
    open.
  - Verification: focused runtime-environment provenance tests cover snapshot
    inclusion, version-change hash movement, sanitization, cap behavior, and
    metadata-inspection failures.

- [x] Extend Unicode format-control safety to all current provenance labels.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1, 2.5, and 2.6.
  - Status: current persisted provenance labels used in run manifests,
    histories, LLM telemetry, prompt histories, source/problem tree snapshots,
    plugin identity records, Git status records, evaluator path records, and
    runtime environment records now reject or escape Unicode format controls
    before persistence, including the final `pyproject.toml` dependency-spec
    gap.
  - Remaining paper gap: this closes the current Unicode-control provenance
    item, but future provenance surfaces still need to use the same
    reject/escape/hash policy when they are added.
  - Verification: focused provenance tests cover U+202E escaping in dependency
    specs plus prior path, plugin, Git, evaluator, provider-metadata,
    prompt-history, metadata, metric/stage/plugin/feedback-label, and
    run/candidate-path Unicode safety cases.

- [x] Define hidden-file policy for seed codebase candidates.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.1 and 2.5.
  - Status: seed codebase loading now has an explicit hidden/cache policy:
    default skip for dot-prefixed and `__pycache__` paths, problem-local
    `initial_programs/seed_policy.yaml` include/exclude patterns for selected
    reserved seed paths, exclude precedence, and persisted
    `allowed_reserved_paths`/`workspace_path_policy` evidence in run artifacts.
  - Remaining paper gap: this closes hidden-file policy configurability for
    current text workspaces; non-text artifact handling and broader full
    codebase fidelity remain tracked separately.
  - Verification: focused tests cover opt-in dotfile/cache inclusion,
    exclusion, broad-include safety, manifest/source provenance, and history
    display behavior.

- [x] Define paper-evidence limits for secret redaction coverage.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.2, 2.5, and 2.6.
  - Status: redaction evidence is now tied to the manifest-recorded
    `libreevolve.redaction.v2` grammar. Docs define the covered credential
    classes, including PEM private-key blocks, secret-like assignments, bearer
    headers, URL userinfo passwords, common provider-token prefixes, and AWS
    access-key ids, and state the exclusions: this is a bounded
    credential-pattern scanner, not a semantic detector; it applies only on
    surfaces that call the shared helper; binary artifacts and documented raw
    retention surfaces remain outside the guarantee.
  - Remaining paper gap: broad prompt/history data-retention controls and
    raw LLM feedback-output retention remain tracked under the separate
    prompt/history retention TODO.
  - Verification: focused redaction tests cover grammar export, provider and
    environment-style fixtures, path-like token labels, private-key blocks,
    URL credentials, and false positives; manifest tests verify that the
    redaction policy is written.

- [x] Enumerate AlphaEvolve Appendix B constructive-math benchmark coverage.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix B reports thirteen
    mathematical discovery families with accompanying data/verification code.
  - Status: `libreevolve/problems/benchmarks/alphaevolve_appendix_b.json`
    records a coverage decision for all thirteen families, including objective
    direction, target/baseline status, construction and certificate artifact
    shapes, certification need, implementation status, rationale, fixture
    mapping where present, and local AlphaEvolve citation metadata. The paper
    manifest validator checks this registry when present.
  - Remaining gap: the registry is a coverage/accountability artifact; it does
    not implement planned validators, exact certificates, or AlphaEvolve
    result-publication contracts.
  - Verification: focused registry and paper-manifest tests cover complete
    enumeration and malformed advertised fixture detection.

- [x] Restore checked framework RNG snapshots into direct `evolve()` runs.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.6 frames
    long-running experiments around explicit compute and reproducibility
    boundaries.
  - Status: `runtime.rng` snapshots are no longer only passive audit records:
    direct callers can pass a validated snapshot into `evolve()`, the seed must
    match the configured run seed, and final runtime manifests record whether
    the framework RNG was fresh or restored.
  - Remaining paper gap: this does not prove full seeded replay because
    archive/controller state, lineage replay, plugin randomness, and provider
    nondeterminism remain outside the restore contract.
  - Verification: focused loop tests cover successful restore and mismatch
    rejection.

- [x] Add AlphaEvolve-style named component ablation report definitions.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 8 and Section 4
    compare against `No evolution`, `No context in the prompt`, `No meta prompt
    evolution`, `No full-file evolution`, and `Small base LLM only`, reported
    by compute-budget fraction over three independent seeds.
  - Status: `alphaevolve_ablations.json` defines the full-system baseline plus
    the five named ablations, component-disable assertions, independent seed
    count, target aggregation, budget fractions, result fields, and
    AlphaEvolve citation metadata. The paper manifest validator checks this
    registry when present.
  - Remaining paper gap: no ablation runner or result curves exist yet.
  - Verification: focused ablation-registry and paper-manifest tests validate
    exact named coverage and malformed registry diagnostics.

- [x] Make the fixed local MAP-Elites archive descriptor input workspace-aware.
  - Paper evidence: `1504.04909__MAP_Elites.pdf` describes illuminating a
    behavior space over candidate descriptors; for AlphaEvolve-style workspace
    candidates, non-primary files can change the candidate behavior.
  - Status: the fixed local archive still uses three numeric dimensions, but
    code-shape dimensions now consume serialized full-workspace text rather
    than `Program.code` alone. The paper status table now states
    serialized-workspace text length/diversity and leaves behavior descriptors
    plus stable normalization open.
  - Remaining paper gap: no user-defined behavior descriptor API,
    evaluator-provided descriptor vector, or stable persisted descriptor model
    exists yet.
  - Verification: MAP-Elites tests cover changed supporting files with
    identical primary code affecting descriptor input and diversity.

- [x] Stabilize the fixed local MAP-Elites complexity descriptor bound.
  - Paper evidence: MAP-Elites archive coordinates are intended to describe a
    behavior space; changing descriptor scale as candidates arrive makes local
    cells less comparable.
  - Status: serialized-workspace complexity now uses the configured
    `map_elites_complexity_max_chars` bound instead of an evolving in-memory
    maximum. The bound is validated, applied to every island archive, and
    written into run manifests.
  - Remaining paper gap: the TF-IDF diversity coordinate remains adaptive to
    the retained elite corpus, and LibreEvolve still lacks user/evaluator
    behavior descriptors.
  - Verification: focused archive/config/database tests prove the fixed-bound
    behavior and manifest recording.

- [x] Add direction/bounds semantics for LLM feedback score composition.
  - Paper evidence: AlphaEvolve treats evaluator and reviewer signals as
    controlled experiment inputs; reviewer metrics should not silently use raw
    arbitrary scales for fitness changes.
  - Status: feedback graders can declare raw score bounds and maximize/minimize
    direction. LibreEvolve persists raw score, normalized score, bounds,
    direction, and weighted delta, and rejects out-of-bounds or malformed
    feedback before scoring.
  - Remaining paper gap: feedback/reviewer metrics are still outside the
    declared objective schema and do not provide Pareto/frontier or
    metric-specific archive behavior.
  - Verification: focused feedback/config tests cover raw bounded score
    normalization and invalid score/bounds cases.

- [x] Enforce problem-local evaluator dependency provenance.
  - Paper evidence: AlphaEvolve run claims depend on evaluator definitions and
    reproducible evaluation code/data boundaries.
  - Status: evaluator source records now declare
    `declared_problem_local_evaluator_dependencies_v1`, and preflight/runtime
    enforce it. Problem-owned files may be imported or opened only when they
    are the configured evaluator entrypoint, captured companion sources, or
    captured declared data sources.
  - Remaining paper gap: seeded replay, external package/native data
    provenance, and stronger sandboxing remain open in the broader
    run-reproducibility checklist.
  - Verification: focused evaluator tests cover rejected undeclared
    problem-local import/data dependencies and allowed declared data.

- [x] Restore compact island cursor state through the database facade.
  - Paper evidence: AlphaEvolve Section 2.6 frames reproducibility around
    experiment state, not just candidate logs.
  - Status: direct database construction can now accept a validated compact
    archive-state snapshot and restore the island cursor, archive sequence,
    migration sequence, metric sampling cursor, and archive sequence map into
    the live `IslandModel`.
  - Remaining paper gap: full replay still needs MAP-Elites cell/elite
    snapshots, descriptor normalization state, migration replay, and `evolve()`
    resume wiring.
  - Verification: focused database tests prove restored assignment/sequence
    behavior and manifest-visible cursor-only restore policy.

- [x] Record adapter-internal provider retry attempts in LLM call telemetry.
  - Paper evidence: AlphaEvolve-scale compute budgets require retry attempts to
    be visible and bounded before they can be attributed to experimental cost.
  - Status: bundled OpenAI, Anthropic, and Ollama adapters now validate
    `provider_max_retries`, preserve the prior default as `2`, and publish
    `adapter_retry` telemetry that the run-scoped LLM call ledger validates.
  - Remaining paper gap: retry attempts are not yet charged to token/cost/time
    budgets, not role-budgeted, and not restored as consumed budget state.
  - Verification: focused backend/ensemble/config tests cover the bounded
    retry knob and ledger validation.

- [x] Add normalized provider-failure categories to LLM call logs.
  - Paper evidence: long AlphaEvolve-style runs need distinguishable timeout,
    rate-limit, transport, provider-status, and response-validation failures
    before failures can drive budget or quarantine policy.
  - Status: ensemble error call records now persist
    `provider_failure_category`, and the paper index documents the field as
    telemetry rather than completed quarantine behavior.
  - Remaining paper gap: failure categories do not yet drive role-specific
    quarantine, provider penalties, or budget-stop accounting.
  - Verification: focused ensemble tests cover classification and ledger
    validation.

- [x] Make DeepResearch cache snapshots manifest-visible plugin artifacts.
  - Status: cache-backed `DeepResearchPlugin` instances now expose snapshot
    file counts, retained counts, skipped/read-error counters, byte counts,
    per-file hashes, retention cap, and an aggregate hash through
    `run_artifacts_metadata()`, and completed run manifests include the
    runtime-derived plugin artifact wrapper.
  - Remaining paper gap: audit-grade DeepEvolve alignment still needs full
    provider/source payload persistence, ranked-source provenance,
    source-content trust policy, detailed redirect/failure policy, and
    TLS/certificate failure classification.
  - Verification: focused DeepResearch plugin and loop tests cover the
    snapshot summary and manifest artifact record.

- [x] Make ImprovEvolve-inspired modular guidance explicitly static in
  candidate metadata.
  - Status: `ModularPlugin` now records static prompt-only strategy metadata
    naming the described `generate_config`/`improve`/`perturb` operations while
    marking execution and interface enforcement false.
  - Remaining paper gap: this is still not ImprovEvolve's scheduled
    generate/improve/perturb loop, basin-hopping-style operation policy, or
    operation-result attribution.
  - Verification: focused modular plugin and loop tests cover direct and
    history-persisted metadata.

- [x] Add hash-backed retention metadata for LLM feedback artifacts.
  - Paper evidence: AlphaEvolve-scale experiments need durable, inspectable
    logs without unnecessarily preserving raw proprietary prompt/feedback text.
  - Status: successful and failed feedback records now retain redacted bounded
    `raw_response` previews, successful parsed `feedback` previews, and
    companion SHA-256/length/redaction/truncation metadata. `papers/README.md`
    documents this as a narrowed prompt-history leakage risk rather than a full
    configurable retention system.
  - Remaining paper gap: per-role full/redacted/hash-only/off prompt and
    response logging modes remain open.
  - Verification: focused feedback tests cover successful and failed grader
    output retention.

- [x] Persist built-in plugin spec attribution in candidate prompt context.
  - Paper evidence: AlphaEvolve-style experiments need to audit which prompt
    components and strategy/config choices influenced a generated candidate.
  - Status: candidate `metadata.plugin_context[]` records now include a nested
    `plugin_spec` record with validated built-in plugin constructor parameters,
    configured labels, and explicit custom-plugin introspection status. The
    paper index now treats custom plugin package-registry and constructor
    provenance beyond exposed version labels as the remaining gap.
  - Remaining paper gap: arbitrary plugin package-registry and constructor
    attribution, retrieval ranking/source provenance, and real selected
    strategy operations remain open.
  - Verification: focused loop tests cover custom and built-in plugin context
    spec records.

- [x] Count logical LLM calls in run-level budget accounting.
  - Paper evidence: AlphaEvolve reports search progress against fixed compute
    budgets; LLM sampling calls need explicit stop accounting before local
    runs can support equal-budget comparisons.
  - Status: runs now support `max_llm_calls`, increment consumed `llm_calls`
    for logical LLM `generate()` attempts, record `max_llm_calls` stop reasons,
    and expose the limit/consumption in history snapshots and runtime
    manifests.
  - Remaining paper gap: this is logical-call accounting only; provider
    adapter attempts, provider tokens, cost, accelerator resources, async
    worker queues, resumable consumed LLM budget state, and equal-budget
    benchmark reporting remain open.
  - Verification: focused budget/config/loop/CLI tests cover direct budget
    state, controller events, CLI overrides, zero-call provider-free runs, and
    optional-role exhaustion after the first logical call.

- [x] Add restored backend-spec validation evidence to the paper index.
  - Paper evidence: long-running AlphaEvolve-style experiments need consistent
    model/backend controls across live setup and any future replay/resume
    state.
  - Status: `papers/README.md` now lists restored/replay backend spec
    validation as implemented, backed by `validate_restored_backend_specs()`.
  - Remaining paper gap: full resume still lacks restored backend consumption,
    oversized/secret-like prompt policy, and custom provider/package discovery.
  - Verification: focused ensemble tests cover the restored-spec validator and
    malformed restored spec rejection.

- [x] Add backend-registry validation evidence to the paper index.
  - Paper evidence: AlphaEvolve-style LLM choices and model controls should use
    one schema across configured, restored, and registry-created constructors.
  - Status: backend registry validation now delegates to the same backend
    normalizer as live/restored specs, and registry-created custom backends are
    constructed from validated defensive copies.
  - Remaining paper gap: full resume still lacks restored backend consumption,
    oversized/secret-like prompt policy, and custom provider/package discovery.
  - Verification: focused ensemble tests cover registry validation and
    registry-created custom backend construction.

- [x] Add restored prompt validation evidence to the paper index.
  - Paper evidence: replay/resume prompt payloads should preserve the same
    text-only validation contract as live proposal generation.
  - Status: `papers/README.md` now lists restored/replay prompt validation as
    implemented, backed by `validate_restored_llm_prompt()`.
  - Remaining paper gap: oversized/secret-like prompt policy and full run
    resume remain open.
  - Verification: focused ensemble tests cover valid and malformed restored
    prompt payloads.

- [x] Add NumPy numerical-runtime provenance evidence to the paper index.
  - Paper evidence: AlphaEvolve-style result claims depend on numerical runtime
    details in addition to Python source and package names.
  - Status: `papers/README.md` now lists NumPy numerical-runtime provenance as
    implemented and scopes environment evidence to package names, lockfile
    hashes, and NumPy config metadata.
  - Remaining paper gap: accelerator/runtime-driver provenance, complete
    freeze/install-source semantics, broader build provenance, private
    package-source policy, live provider service/API versions, and provider
    cost or remote provider-side default capture remain open.
  - Verification: focused provenance tests cover the new environment record.

- [x] Add selected PEP 621 metadata evidence to the paper index.
  - Paper evidence: package metadata beyond name/version can affect build,
    invocation, and audit context for reproducible experiments.
  - Status: `papers/README.md` now lists selected PEP 621 metadata provenance
    alongside NumPy numerical-runtime provenance.
  - Remaining paper gap: accelerator/runtime-driver provenance, complete
    freeze/install-source semantics, broader non-project build metadata
    policy, private package-source policy, live provider service/API versions,
    and provider cost or remote provider-side default capture remain open.
  - Verification: focused provenance tests cover the new package metadata
    fields.

- [x] Add keyword and arbitrary entry-point evidence to the paper index.
  - Paper evidence: entry-point groups and keywords can affect packaging,
    plugin discovery, and audit context for reproducible experiments.
  - Status: `papers/README.md` now lists PEP 621 `keywords` and arbitrary
    `[project.entry-points]` groups as implemented selected package metadata.
  - Remaining paper gap: accelerator/runtime-driver provenance, complete
    freeze/install-source semantics, broader non-project build metadata
    policy, private package-source policy, live provider service/API versions,
    and provider cost or remote provider-side default capture remain open.
  - Verification: focused provenance tests cover keyword and entry-point
    capture.

- [x] Add built-in plugin registry/config evidence to the paper index.
  - Paper evidence: configured plugins are experiment components that can
    change prompt context, retrieval cadence, scoring, or emitted artifacts.
  - Status: `papers/README.md` now lists built-in plugin registry resolution,
    structured built-in option specs, and CLI alias/spec preflight as
    implemented, while leaving custom registry/version provenance open.
  - Remaining paper gap: custom plugin entry-point discovery, package/version
    attribution, arbitrary custom schema policy, and custom constructor
    introspection remain open.
  - Verification: focused config, CLI, and loop tests cover configured built-in
    plugin specs.

- [x] Add ensemble LLM timeout evidence to the paper index.
  - Paper evidence: AlphaEvolve-style compute-budgeted runs require stalled
    model calls to be bounded and auditable.
  - Status: `papers/README.md` now notes that `llm_call_timeout_sec` bounds
    each ensemble backend attempt and records timed-out built-in or custom
    calls as structured timeout failures with retry/fallback eligibility.
  - Remaining paper gap: role-specific quarantine, provider penalties,
    remaining-run deadline propagation, hard provider cancellation, and
    budget-stop policy remain open.
  - Verification: focused ensemble, config, and CLI tests cover the timeout
    boundary.

- [x] Add `pip freeze` environment evidence to the paper index.
  - Paper evidence: reproducible AlphaEvolve-style experiment claims need to
    account for transitive and direct-source package installs.
  - Status: `papers/README.md` now lists bounded/redacted `pip_freeze`
    capture with a raw `pip freeze --all` stdout hash alongside package,
    lockfile, and NumPy runtime provenance.
  - Remaining paper gap: broader build provenance, accelerator/runtime-driver
    state, non-project build metadata policy, complete private package-source
    interpretation, live provider service/API versions, provider
    cost or remote provider-side default capture, and independent reproduction gates remain
    open.
  - Verification: focused provenance tests cover the freeze record.

- [x] Add installed-distribution `WHEEL` metadata evidence to the paper index.
  - Paper evidence: reproducible AlphaEvolve-style experiment claims should
    account for wheel compatibility tags and wheel metadata that can affect
    binary/runtime behavior.
  - Status: `papers/README.md` now lists bounded parsed installed-distribution
    `WHEEL` metadata alongside package, lockfile, `pip_freeze`, and NumPy
    runtime provenance.
  - Remaining paper gap: broader build provenance, accelerator/runtime-driver
    state, non-project build metadata policy, complete private package-source
    interpretation, live provider service/API versions, provider
    cost or remote provider-side default capture, and independent reproduction gates remain
    open.
  - Verification: focused provenance tests cover wheel metadata capture, tag
    and raw metadata size bounds, redaction, missing metadata, and degraded
    read-error statuses.

- [x] Add built-in LLM provider SDK version evidence to the paper index.
  - Paper evidence: paper-level experiment claims depend on the provider
    adapter and SDK package versions used to construct model requests.
  - Status: `papers/README.md` now lists built-in OpenAI, Anthropic, and
    Ollama SDK package versions plus adapter API modes alongside package,
    lockfile, `pip_freeze`, wheel, and NumPy runtime provenance.
  - Remaining paper gap: live provider service/API versions, provider
    cost or remote provider-side default capture, direct provider authentication proof,
    nondeterminism/replay boundaries, and independent reproduction gates remain
    open.
  - Verification: focused provenance tests cover installed SDK records,
    hash movement when versions change, missing package statuses, redacted
    lookup errors, and unsafe version-label escaping.

- [x] Add bounded extra `[project]` metadata evidence to the paper index.
  - Paper evidence: paper-level experiment claims should account for project
    metadata that can affect package build, audit, invocation, or publication
    context even when the field is outside the selected execution identity
    subset.
  - Status: `papers/README.md` now lists bounded `extra_project_metadata` for
    unselected or unknown `[project]` keys alongside selected PEP 621,
    package, lockfile, `pip_freeze`, wheel, NumPy, and provider SDK
    provenance.
  - Remaining paper gap: broader non-project build provenance,
    install-source interpretation, accelerator budget/accounting state, live
    provider service/API versions, provider cost or remote provider-side default capture,
    private package-source policy, and independent reproduction gates remain
    open.
  - Verification: focused provenance tests cover extra metadata capture,
    nested tables/lists, bounds, redaction, unsafe character escaping, and hash
    movement when extra metadata changes.

- [x] Add CLI-restorable framework RNG snapshot evidence to the paper index.
  - Paper evidence: AlphaEvolve-style long-running experiments need restorable
    framework stochastic state as part of reproducibility.
  - Status: `papers/README.md` now lists persisted and CLI-restorable
    framework RNG snapshots as implemented AlphaEvolve evidence, while keeping
    full resume and seeded lineage replay open.
  - Remaining paper gap: archive/controller state restore, lineage replay,
    plugin/provider RNG boundaries, provider nondeterminism, and independent
    replay certification gates remain open.
  - Verification: focused CLI tests cover snapshot restore wiring and
    seed-mismatch rejection.

- [x] Add bounded ensemble prompt-input evidence to the paper index.
  - Paper evidence: AlphaEvolve-style LLM proposal generation depends on
    bounded text prompts before provider/custom backend calls.
  - Status: `papers/README.md` now lists ensemble prompt-size enforcement
    before registry/custom backend calls as implemented AlphaEvolve evidence.
    Secret-like prompt text is treated as private run input while LLM telemetry
    remains prompt hash/length only.
  - Remaining paper gap: token-aware context-window accounting,
    section-priority packing, per-role prompt/provider-response retention
    policy beyond generated mutation prompts, and independent result
    certification remain open.
  - Verification: focused ensemble tests cover prompt cap wiring and rejection
    before backend calls.

- [x] Record matrix smoke-validator anti-gaming hardening in paper-facing docs.
  - Paper evidence: AlphaEvolve's matrix results rely on operation/rank-aware
    exact validation, so local examples should not be mistaken for paper-grade
    evidence when they only demonstrate a small smoke objective.
  - Status: the matrix example now rejects the previously demonstrated
    hard-coded-three-case, module-level dead-code counter, and NumPy delegation
    probes. `papers/README.md`, README, ROADMAP, problem-format docs, and the
    active TODOs state that this is scoped smoke-fixture hardening rather than
    tensor-rank benchmark support.
  - Remaining paper gap: AlphaEvolve-grade matrix target suites, repeated
    seeds, best-rank hit fractions, exact coefficient certificates, and
    exportable construction artifacts remain open.
  - Verification: focused example tests cover seed validity, improvement
    ordering, and all three shortcut rejection probes.

- [x] Add remaining-runtime LLM wait-deadline evidence to the paper index.
  - Paper evidence: AlphaEvolve-style compute budgets should bound model-call
    wall-clock time as part of long-running experiment control.
  - Status: papers/TODO and user docs now state that deadline-aware
    `LLMEnsemble` calls are clamped to the remaining `max_runtime_seconds`
    budget in addition to configured provider request timeouts and
    `llm_call_timeout_sec`.
  - Remaining paper gap: hard provider cancellation, provider token/cost
    budgets, timeout-driven quarantine/stop policy, retry-attempt budget
    coupling, and equal-budget benchmark reports remain open.
  - Verification: focused loop/budget and ensemble timeout tests cover runtime
    clamping, configured timeout precedence, structured timeout telemetry, and
    fallback after timeout.

- [x] Add plugin version labels to paper-inspired prompt-guidance evidence.
  - Paper evidence: AlphaEvolve-style runs and paper-inspired plugins should
    make the components that influenced prompt context auditable across runs.
  - Status: plugin identity provenance now includes sanitized `version`
    records when a plugin exposes `__version__` on the instance, class, or
    module. The same identity flows into candidate `metadata.plugin_context`,
    runtime plugin state, plugin artifacts, and score-composition records.
  - Remaining paper gap: custom plugin package registry provenance, constructor
    schema introspection, retrieval ranking provenance, and actual selected
    plugin strategy execution remain open.
  - Verification: focused provenance and loop tests cover version-source
    priority, missing versions, secret redaction, and candidate/runtime
    propagation.

- [x] Add bounded accelerator runtime evidence to paper environment provenance.
  - Paper evidence: AlphaEvolve-style environment claims need accelerator and
    driver/runtime evidence in addition to Python, package, lockfile, and
    numerical-library records.
  - Status: manifests now include `accelerator_runtime` with selected
    CUDA/NVIDIA/ROCm/HIP/oneAPI/SYCL/DirectML environment hints, redacted
    hash-backed values, and degraded `nvidia-smi`/`rocm-smi` driver probe
    records.
  - Remaining paper gap: this does not establish full build reproducibility,
    accelerator budget accounting, live provider service/API-version capture,
    provider cost or remote provider-side default capture, or complete private package-source
    interpretation.
  - Verification: focused provenance tests cover the new accelerator evidence
    and redaction/degraded-status behavior.

- [x] Add local adapter default-parameter evidence to paper LLM telemetry.
  - Paper evidence: AlphaEvolve-style LLM-call provenance should preserve the
    local generation settings that shaped each request, including implicit
    LibreEvolve adapter defaults.
  - Status: call telemetry now includes `backend_defaults` for built-in OpenAI,
    Anthropic, and Ollama adapters, covering local output-token caps, provider
    internal retry caps, configured request timeouts, API modes, and OpenAI
    reasoning/API-mode policy.
  - Remaining paper gap: remote provider-side SDK defaults, provider cost
    accounting, token/cost budget policy, and role-specific retry/quarantine
    semantics remain open.
  - Verification: focused backend and ensemble tests cover the record shape,
    safe replay validation, and unsafe-default sanitization.

- [x] Add configurable reward-accounted role evidence to paper LLM telemetry.
  - Paper evidence: AlphaEvolve uses an LLM ensemble where scheduler feedback
    should correspond to logical call roles and outcomes.
  - Status: mutation remains the default reward-accounted role, and
    `llm_reward_accounted_roles` can opt additional manifest-safe roles into
    scheduler reward accounting. Scheduler and runtime snapshots persist the
    effective `reward_accounting_policy`.
  - Remaining paper gap: separate per-role bandit state, quotas, configured
    non-mutation reward-signal semantics, token/cost budget-stop policy,
    provider-cost accounting, role-specific retry/quarantine, and full resume
    remain open.
  - Verification: focused config, ensemble, loop, and paper-manifest/docs
    checks cover the evidence and status wording.

- [x] Add auxiliary LLM failure-isolation evidence for paper alignment.
  - Paper evidence: AlphaEvolve-style long runs need auxiliary LLM failures to
    be attributable without discarding already-completed useful candidate work.
  - Status: critique provider failures now retain the original mutation with
    bounded failure metadata, and meta-prompt provider failures now become
    rejected prompt-mutation records instead of aborting logged candidates.
  - Remaining paper gap: mutation-call quarantine, provider penalties,
    token/cost budget-stop policy, role-specific retry/quarantine, and full
    cross-adapter retry budget accounting remain open.
  - Verification: focused loop tests cover the isolated critique and
    meta-prompt failure paths.

- [x] Add feedback-sourced objective metric evidence for AlphaEvolve alignment.
  - Paper evidence: AlphaEvolve optimizes multiple user-provided scores, so
    non-evaluator score sources need explicit objective semantics before they
    can participate in archive selection.
  - Status: problem metrics can now distinguish evaluator-sourced and
    feedback-sourced objective metrics. Feedback-sourced metrics must be
    non-primary and declared in the objective schema, are not required from
    validators, and can be filled by `objective_metric: true` LLM feedback
    graders with inherited bounds/direction before joining normalized archive
    selection.
  - Remaining paper gap: this remains scalar equal-weight selection, not
    AlphaEvolve-style Pareto/frontier or metric-specific inspiration policy.
  - Verification: focused loader/evaluator/feedback/config/loop tests and the
    updated paper index cover the new paper-alignment status.

- [x] Add validator-diagnostic prompt evidence for AlphaEvolve alignment.
  - Paper evidence: AlphaEvolve prompt context includes prior execution
    results and scores, so reusable failure evidence should include compact
    validator diagnostics, not just scalar scores and raw stdout/stderr.
  - Status: parent/inspiration feedback and recent failure memory now render
    compact aggregate syntax, metric-bound, malformed-metric, and sample
    aggregation diagnostics with bounded redaction and prompt-structure
    escaping. The paper index now counts validator-diagnostic prompt summaries
    among implemented AlphaEvolve-alignment evidence.
  - Remaining paper gap: prompt rendering still lacks artifact-content
    retrieval, full validator metadata rendering, and token-aware
    section-priority packing.
  - Verification: focused prompt tests cover validator diagnostics in active
    parent feedback and failure-memory prompt context.

- [x] Add custom plugin signature provenance to paper-alignment evidence.
  - Paper evidence: paper-inspired plugins and extension behavior should be
    attributable in long AlphaEvolve-style runs without leaking private
    constructor secrets.
  - Status: runtime plugin state and plugin prompt-context records now include
    signature-only custom plugin specs for direct plugin instances. The paper
    index now counts custom constructor-signature attribution as implemented
    while preserving custom package-registry, entry-point discovery, and
    constructor-value provenance as open gaps.
  - Remaining paper gap: no general custom plugin package registry, entry-point
    discovery, captured constructor values, or richer paper-scope package
    provenance for arbitrary custom plugins.
  - Verification: focused loop tests cover custom signature records and
    absence of secret/default constructor values in manifests.

- [x] Preserve the matrix-result report contract shape.
  - Paper evidence: AlphaEvolve Section 3.1 and Appendix A publish matrix
    target identity, best ranks, random-seed hit fractions, exact coefficient
    domains, and reproducible construction artifacts.
  - Status: `libreevolve.matrix_result_report.v1` now validates matrix target
    identity, dimensions, seed count, best rank, hit fraction, coefficient
    domain, exactness certificate status/hash, per-seed exact/best-rank
    records, artifact path/hash metadata, and summary rendering. The paper
    index counts this as a report-contract implementation while still marking
    the tensor-decomposition target suite and algorithms as missing.
  - Remaining paper gap: LibreEvolve still lacks the 54-target matrix suite,
    exact tensor algorithms, certificate-generation pipeline, and notebook or
    export equivalents needed for AlphaEvolve-comparable matrix claims.
  - Verification: focused matrix-result tests cover the report contract and
    paper docs keep the smoke matrix example outside benchmark evidence.

- [x] Distinguish paper-comparable matrix results from exploratory numeric
  domains.
  - Paper evidence: AlphaEvolve Section 3.1 and Appendix A publish exact
    integer or half-integer matrix multiplication constructions, along with
    per-seed hit rates and reproducibility artifacts.
  - Status: `libreevolve.matrix_result_report.v1` now has an explicit
    `alphaevolve_comparable` policy. It allows exploratory `rational` and
    `float` coefficient domains only for non-comparable reports, and rejects
    AlphaEvolve-comparable claims unless the coefficient domain is `integer` or
    `half_integer`, exactness is verified, every seed row is exact, and
    algorithm/certificate/notebook artifacts are present.
  - Remaining paper gap: LibreEvolve still lacks the 54-target tensor suite,
    exact algorithms, generated certificates, and notebook/export pipeline
    needed to produce real AlphaEvolve-comparable matrix result reports.
  - Verification: focused matrix-result tests cover the comparable/exploratory
    split and paper docs describe the remaining target-suite/export gap.

- [x] Add a paper-result certification report contract.
  - Paper evidence: AlphaEvolve distinguishes optimization-loop scores from
    post-deployment measurements, expert confirmation, and stronger
    paper-level result evidence.
  - Status: `libreevolve.paper_result_certification.v1` now validates
    certification reports that separate local-validator records from
    paper-claim-ready independent certifications, requiring claim scope,
    verifier identity/independence, passed verdict/evidence, and hashed
    artifacts. The paper index counts the report contract as implemented while
    keeping real independent certifier execution and external records open.
  - Remaining paper gap: no benchmark currently emits these certification
    reports from an independent verifier, deployment simulator, human-review
    workflow, or exact certificate-generation pipeline.
  - Verification: focused certification tests cover readiness gating and
    paper docs keep local evaluator validity separate from confirmed-result
    evidence.

- [x] Add systems held-out/reference result report contract.
  - Paper evidence: AlphaEvolve Section 3.3 evaluates scheduling, kernel, and
    compiler-style discoveries with held-out inputs, randomized reference
    checks, deployment measurements, or expert confirmation beyond loop
    feedback.
  - Status: `libreevolve.systems_result_report.v1` now validates report
    metadata that separates optimization, held-out/generalization, and
    reference-correctness gates with case-set hashes, sample counts/seeds,
    finite metrics, artifact hashes, optional certification linkage, and
    `alphaevolve_ready` gating. The paper index can now point to this as the
    required report contract for future systems fixtures.
  - Remaining paper gap: no real compiler, hardware, kernel, scheduling, or
    systems fixture emits this report from actual held-out or randomized
    reference checks yet.
  - Verification: focused systems-result tests cover readiness gating, missing
    gates, not-applicable rationale, artifact safety, and summary rendering.

- [x] Prevent systems `alphaevolve_ready` reports from linking to pending
  certification.
  - Paper evidence: AlphaEvolve systems results distinguish optimization-loop
    evaluator feedback from stronger held-out, deployment, expert, or
    independent confirmation.
  - Status: optional certification linkage in
    `libreevolve.systems_result_report.v1` can no longer contradict readiness:
    `alphaevolve_ready` reports fail validation when the linked certification
    says `paper_claim_ready: false`, while non-ready reports may retain pending
    certification references.
  - Remaining paper gap: this is still a report-contract guard; no real
    systems fixture emits held-out, randomized reference, deployment, or
    certification reports yet.
  - Verification: focused systems-result tests cover both the contradictory
    ready-certification rejection and the non-ready pending-certification path.

- [x] Add benchmark anti-gaming hardening report contract.
  - Paper evidence: AlphaEvolve result comparisons depend on validators and
    benchmark reports that measure the intended operation, rank, construction,
    or systems behavior rather than shortcut artifacts.
  - Status: `libreevolve.benchmark_hardening.v1` now validates protected
    signal declarations, shortcut threats, detector strategies, passed negative
    fixtures, hashed hardening artifacts, and benchmark-readiness gating. The
    paper index can count the report contract while still excluding smoke
    examples from AlphaEvolve-comparable benchmark claims.
  - Remaining paper gap: real benchmark runners still need to generate these
    hardening reports from actual anti-gaming fixtures, operation/rank
    instrumentation, and construction-artifact validation.
  - Verification: focused hardening tests cover readiness gating, missing
    fixture coverage, invalid detectors/signals, artifact safety, and summary
    rendering.

- [x] Add executed equal-budget ablation result report contract.
  - Paper evidence: AlphaEvolve Figure 8 compares the full system against five
    named ablations as curves over equal compute-budget fractions and repeated
    seeds.
  - Status: `libreevolve.alphaevolve_ablation_report.v1` now validates
    executed ablation result records for all six Figure 8 variants, declared
    targets, exactly three seeds, required equal-budget fractions, finite
    scores, consumed-budget/fraction consistency, passed component assertions,
    hashed artifacts, and summary rendering. The paper index can count the
    report contract while keeping actual ablation runs open.
  - Remaining paper gap: no benchmark script currently executes these variants
    on real targets or emits the validated ablation result reports, and broader
    token/cost/accelerator budget accounting remains open.
  - Verification: focused ablation-result tests cover equal-budget coverage,
    budget mismatch rejection, component assertion failures, artifact safety,
    and summary readiness.

- [x] Require one budget axis and limit per ablation target.
  - Paper evidence: AlphaEvolve Figure 8 plots ablation performance by fraction
    of a shared compute budget, so variant curves for a target should not mix
    different budget units or limits.
  - Status: `libreevolve.alphaevolve_ablation_report.v1` now enforces
    target-level budget consistency across all variants and seeds, in addition
    to the existing per-seed fraction-curve consistency.
  - Remaining paper gap: no real benchmark script executes the ablation
    variants or emits validated reports.
  - Verification: focused ablation-result tests cover a variant/seed curve
    that keeps its own fractions consistent while changing the target-level
    budget limit.

- [x] Add paper-facing LLM role/retry budget report contract.
  - Paper evidence: AlphaEvolve-style search runs under explicit compute
    budgets, so LLM role retries, provider-internal attempts, tokens, cost, and
    elapsed time need auditable budget semantics before paper-level claims.
  - Status: `libreevolve.llm_budget_report.v1` now validates report metadata
    for mutation, critique, and feedback role budgets, provider-internal retry
    attempts, token/cost/wall-clock limits and usage, persisted resume-state
    hashes, restored-state consistency, and paper-budget readiness. The paper
    index can count this as an audit contract while leaving live enforcement
    open.
  - Remaining paper gap: runtime token/cost/time stop criteria, hard provider
    cancellation, and restored retry budget consumption are still not wired to
    the running ensemble.
  - Verification: focused LLM budget report tests cover readiness gating,
    over-limit usage, provider retry cap violations, missing roles/limits, and
    resume-state evidence.

- [x] Require persisted evidence for restored LLM budget reports.
  - Paper evidence: provider retry-budget consumption must be attributable and
    resumable before budget claims can support AlphaEvolve-style long-running
    experiments.
  - Status: `libreevolve.llm_budget_report.v1` now rejects reports that claim
    restored retry-budget state without persisted resume-state evidence.
  - Remaining paper gap: this is still report validation; live token, cost,
    wall-clock, adapter-attempt, and restored retry-budget enforcement remain
    open.
  - Verification: focused LLM budget-report tests cover restored-without-
    persisted resume state.

- [x] Add provider timeout/cancellation policy report contract.
  - Paper evidence: AlphaEvolve-style budgeted search should bound stalled
    provider calls and define whether timeout/cancellation events retry,
    fallback, quarantine candidates, or stop the run.
  - Status: `libreevolve.provider_cancellation_policy.v1` now validates policy
    metadata for provider request timeouts, ensemble wait deadlines, runtime
    deadlines, hard-cancel rules, role-scoped budget actions, artifact
    requirements, hard-cancel readiness, and hashed cancellation artifacts. The
    paper index can count this as a policy contract while leaving live
    cancellation enforcement open.
  - Remaining paper gap: provider SDK hard cancellation tokens,
    timeout-driven stop/quarantine runtime behavior, and persisted
    role-specific timeout artifacts are still not wired to the running
    ensemble.
  - Verification: focused cancellation-policy tests cover readiness gating,
    missing hard-cancel rules, invalid rules/actions, artifact safety, and
    summary rendering.

- [x] Require cancellation-record evidence for provider hard-cancel readiness.
  - Paper evidence: a hard-cancel readiness claim needs reportable
    cancellation evidence, not only a declared stop-run action.
  - Status: provider cancellation policies now reject `hard_cancel_ready: true`
    unless a hard-cancel stop-run rule requires a `cancellation_record`
    artifact kind.
  - Remaining paper gap: live provider SDK hard cancellation tokens,
    timeout-driven stop/quarantine runtime behavior, and persisted
    role-specific timeout artifacts are still not wired to the running
    ensemble.
  - Verification: focused cancellation-policy tests cover missing
    `cancellation_record` artifact evidence for hard-cancel readiness.

- [x] Add paper-facing shipped-example scope registry.
  - Paper evidence: the AlphaEvolve paper compares specific benchmark families,
    while LibreEvolve's checked-in examples are currently smoke fixtures.
  - Status: `libreevolve.example_benchmark_scope.v1` now validates that
    `hello_world`, `sorting`, `workspace_math`, `matrix_multiplication`, and
    `circle_packing` are smoke-only and not AlphaEvolve-comparable. Summary
    rendering exposes zero comparable shipped examples so paper-facing docs can
    avoid treating example fixtures as benchmark results.
  - Remaining paper gap: the registry does not produce tensor-rank, circle
    construction, systems, or ablation evidence; benchmark runners still need
    to emit real reports and artifacts before AlphaEvolve-style result claims.
  - Verification: focused example-scope tests cover smoke-only validation,
    comparable-flag rejection, unsafe paths, duplicate ids, paper-claim gating,
    and summary rendering.

- [x] Add paper-facing retrieval transport policy classification.
  - Paper evidence: DeepEvolve-style retrieval treats external knowledge as an
    experimental input, so paper-facing provenance needs to classify transport
    and failure evidence for prompt-injected context.
  - Status: `DeepResearchPlugin` retrieval events now include
    `libreevolve.retrieval_transport_policy.v1`, classifying HTTPS request
    state, redirects, HTTP status class, payload hash presence, oversized
    responses, missing custom-provider transport, and TLS/certificate-looking
    failures. Successful default arXiv retrievals with HTTPS, status, and
    payload hashes can be marked `audit_grade`; unaudited custom text is marked
    `unauditable`.
  - Remaining paper gap: this does not persist full provider/source payloads,
    source-content snapshots, semantic source verification, or ranked-source
    scoring beyond provider order.
  - Verification: focused DeepResearch tests cover policy status, redirect
    degradation, TLS/certificate classification, and unauditable custom
    provider metadata.

- [x] Add paper-facing migration replay boundary to archive-state snapshots.
  - Paper evidence: AlphaEvolve-style resumed population traces should not
    imply migration-event replay when only the resulting archive placements are
    restored.
  - Status: `runtime.history.archive_state.migration_replay` now records and
    validates `libreevolve.island_migration_replay_policy.v1`, including
    `not_applied_as_restore_engine`, no replay-engine support, archive-content
    coverage for current migrated placements, and explicit limitations for
    event order, skipped migrations, and controller pending work.
  - Remaining paper gap: resumed experiment traces still need migration
    event-order replay or a stronger replay engine plus controller/pending-work
    restore.
  - Verification: focused island/database restore tests cover the policy and
    reject replay overclaims.

- [x] Attach retained provider retry details to paper-facing LLM budget reports.
  - Paper evidence: AlphaEvolve-style budget tables need provider-internal
    retries to be visible by role and backend before paper-level compute claims
    can be audited.
  - Status: final `runtime.llm_budget_report` instances now attach retained
    per-call adapter retry records to each role usage row when bounded
    `LLMEnsemble.call_history` still contains those rows. The report preserves
    the configured provider retry cap, attempts, failed attempts, backend,
    call id, status, and safe failure labels while retaining the aggregate
    provider-attempt count from scheduler role accounting.
  - Remaining paper gap: live token/cost/time stop criteria and restored retry
    budget consumption are still not wired to the running ensemble.
  - Verification: focused runtime manifest tests and budget-report validation
    cover retained provider retry details in a self-validated report.

- [x] Add paper-facing installed-package source metadata.
  - Paper evidence: AlphaEvolve-style result claims depend on package source
    and install provenance as well as package names and versions.
  - Status: environment provenance now records bounded source/install metadata
    for retained installed distributions: redacted/hash-backed
    `direct_url.json`, installer labels, and hash-only `RECORD` evidence.
  - Remaining paper gap: complete package artifact verification, private-index
    resolution, and broader non-project build provenance remain open.
  - Verification: focused provenance tests cover the source metadata and
    source-policy retention record.

- [x] Add paper-facing objective-vector archive admission evidence.
  - Paper evidence: AlphaEvolve-style multiple-score claims need archive
    decisions to expose the underlying normalized metric vector.
  - Status: `metadata.archive_admission.objective_vector` and migration
    `archive_events.jsonl` rows now preserve finite normalized metrics plus the
    scalar selection policy when available. `show` now validates
    current-history objective vectors while streaming and prints bounded
    selected-row normalized-metric summaries.
  - Remaining paper gap: this does not implement Pareto/frontier archive
    replacement or plugin-objective integration.
  - Verification: focused loop/database/island/CLI tests cover evaluator
    metrics, feedback-filled objective metrics, objective-vector validation,
    selected `show` display, bounded summaries, and malformed unselected row
    rejection.

- [x] Add feedback-grader reward signals for configured LLM scheduler roles.
  - Paper evidence: AlphaEvolve-style LLM ensembles need quality feedback tied
    to the call role and outcome.
  - Status: successful LLM feedback grader records now include
    `scheduler_reward`; if the exact `feedback:<name>` role is reward-accounted,
    the normalized feedback score is recorded as the scheduler reward for the
    matching call.
  - Remaining paper gap: this still does not provide independent per-role
    routing/quotas, critique/meta-prompt reward semantics, provider cost
    accounting, or token/cost budget stop policy.
  - Verification: focused feedback tests cover rewarded configured feedback
    roles and telemetry-only default feedback roles.

- [x] Add active-context retrieval provenance for DeepResearch prompt evidence.
  - Paper evidence: DeepEvolve-style external knowledge should be traceable to
    the retrieval event and source-order evidence used in a prompt.
  - Status: active DeepResearch prompt context now records
    `libreevolve.deep_research_active_context.v1` with event index,
    synthesis/raw-result hashes, query hash, cache fields, retained-source
    ranking hash fields, and transport-policy status for the injected
    retrieval text.
  - Remaining paper gap: this is still compact provenance, not full provider
    payload/source-content snapshots, semantic ranking scores, or a
    DeepEvolve-style debug/refinement loop.
  - Verification: focused DeepResearch and loop tests cover active-context
    links in plugin metadata and candidate history.

- [x] Preserve bounded source-content snapshots for DeepResearch source rows.
  - Paper evidence: paper-aligned retrieval/debug records should preserve the
    source content that informed prompt-visible external context.
  - Status: retained DeepResearch source rows now include
    `libreevolve.retrieval_source_content_snapshot.v1` snapshots with
    bounded/redacted text, raw/stored hashes, count metadata, and
    redaction/truncation flags when summary/content text is available.
  - Remaining paper gap: this is not full provider payload persistence,
    semantic source verification, or ranked-source scoring beyond provider
    order.
  - Verification: focused DeepResearch and loop tests cover default arXiv and
    custom-source snapshots plus history redaction.

- [x] Add query-overlap retrieval relevance scores as paper-facing audit metadata.
  - Paper evidence: DeepEvolve-style retrieval claims need a source-selection
    rationale beyond opaque provider ordering.
  - Status: retained DeepResearch source rows now include
    `query_term_overlap_audit_v1` relevance records with query/source term
    counts, overlap count, matched terms, score, and explicit audit-only,
    no-reorder flags. `source_ranking` includes a hash over those score
    records.
  - Remaining paper gap: this is not a learned ranker, external semantic score,
    local-paper/hypothesis query grounding, or full provider payload record.
  - Verification: focused DeepResearch and loop tests cover relevance metadata
    and active-context score hashes.

- [x] Add task/context query grounding for DeepResearch retrieval.
  - Paper evidence: DeepEvolve-style retrieval should be grounded in task
    context as well as current candidate behavior.
  - Status: DeepResearch query inputs now include bounded task-description and
    explicit-context terms plus context hashes, in addition to best-program
    fitness, metric names, and code/file terms.
  - Remaining paper gap: failure-history, local-paper-corpus, and
    hypothesis-template query grounding remain open.
  - Verification: focused DeepResearch and loop tests cover task/context query
    terms and persisted query-input metadata.

- [x] Add recent-failure query grounding for DeepResearch retrieval.
  - Paper evidence: DeepEvolve-style retrieval/debug loops should use failed
    attempt evidence to guide later external-context searches.
  - Status: DeepResearch queries now include bounded terms from recent redacted
    failure summaries, with retained terms, failure count, considered character
    count, and failure-context hash recorded in `query_inputs`.
  - Remaining paper gap: local-paper-corpus and hypothesis-template query
    grounding remain open.
  - Verification: focused DeepResearch and loop tests cover recent failure
    terms and two-generation failure-to-query behavior.

- [x] Add local-paper query grounding for DeepResearch retrieval.
  - Paper evidence: DeepEvolve-style retrieval should be grounded in the local
    literature corpus available to the run, not only generic live search terms.
  - Status: DeepResearch queries now include bounded terms from local paper
    manifest title/id metadata when present, and `query_inputs` records the
    local-paper policy, row counts, selected counts, considered characters, and
    corpus/selected hashes.
  - Remaining paper gap: hypothesis-template query grounding, learned or
    externally scored semantic ranking, full provider-payload persistence, and
    source-content trust policy remain open.
  - Verification: focused DeepResearch, loop, and database tests cover manifest
    metadata query terms and strict row validation.

- [x] Add recent-hypothesis query grounding for DeepResearch retrieval.
  - Paper evidence: DeepEvolve-style retrieval/debug loops should use recent
    proposal hypotheses as search context for later retrieval, not only code,
    task, and failure text.
  - Status: DeepResearch queries now include bounded terms from recent captured
    proposal hypotheses, with retained terms, hypothesis count, considered
    character count, and hypothesis-context hash recorded in `query_inputs`.
  - Remaining paper gap: learned or externally scored semantic ranking, full
    provider-payload persistence, source-content trust policy, and full
    cross-file debugging/refinement loops remain open.
  - Verification: focused DeepResearch, loop, and database tests cover recent
    hypothesis terms and two-generation hypothesis-to-query behavior.

- [x] Add bounded provider-result snapshots for DeepResearch retrieval.
  - Paper evidence: DeepEvolve-style retrieval should retain audit evidence for
    provider outputs that shape later prompt context.
  - Status: DeepResearch retrieval events and cache snapshots now include
    bounded/redacted provider-result snapshots with raw/stored hashes and
    redaction/truncation metadata. Plugin artifact summaries report
    provider-result snapshot counts and aggregate hashes.
  - Remaining paper gap: unbounded full provider-payload persistence,
    source-content trust policy, learned/external ranking, and full
    cross-file debugging/refinement loops remain open.
  - Verification: focused DeepResearch and loop tests cover redacted provider
    snapshot persistence and manifest-visible artifact summaries.

- [x] Add declared schema evidence for configured external plugins.
  - Paper evidence: paper-inspired extension components should have
    reproducible, auditable configuration rather than opaque constructor
    kwargs.
  - Status: configured entry-point plugins can publish declared constructor
    option schemas; invalid options fail before instantiation, and runtime
    plugin specs retain the declared schema/policy with captured options.
  - Remaining paper gap: direct custom plugin objects still have signature-only
    provenance, and richer package-registry policy remains open.
  - Verification: focused CLI/plugin registry and loop provenance tests cover
    declared schema validation and manifest retention.

- [x] Add role-scoped timeout policy evidence for paper-level budgets.
  - Paper evidence: LLM timeout and cancellation policy should be attributable
    to the roles that consume budget in an AlphaEvolve-style run.
  - Status: runtime provider-cancellation policies now scope provider-timeout
    and ensemble-deadline rules to `mutation`, `critique`, `feedback:*`, and
    `meta_prompt`, while preserving `hard_cancel_ready: false`.
  - Remaining paper gap: live hard cancellation tokens, timeout-driven
    stop/quarantine runtime behavior, and cross-adapter retry accounting remain
    open.
  - Verification: focused cancellation-policy and loop manifest tests cover
    role-prefix validation and manifest rule scope.

- [x] Add restored scheduler-state coverage for all paper-visible LLM roles.
  - Paper evidence: role-specific scheduler/accounting snapshots should be
    replayable for every LLM role that can appear in paper-facing telemetry.
  - Status: focused ensemble tests now restore reward-accounted scheduler state
    for mutation, critique, feedback, and meta-prompt roles.
  - Remaining paper gap: independent per-role routing/quotas and
    critique/meta-prompt reward semantics remain open.
  - Verification: focused ensemble restore test covers counts, wins, totals,
    rewarded call ids, and restored reward-accounting policy for all current
    loop LLM roles.

- [x] Cover provider usage and adapter retry telemetry for paper-visible LLM
  roles.
  - Paper evidence: AlphaEvolve-style budget accounting should connect provider
    token usage and retry attempts to the roles that create proposals,
    critiques, feedback, and prompt updates.
  - Status: focused ensemble tests now record fake provider usage counts,
    provider identifiers, and adapter retry diagnostics for mutation, critique,
    feedback, and meta-prompt calls, with role-accounting totals checked for
    token and provider-internal attempt attribution.
  - Remaining paper gap: live token-budget/cost/time stop enforcement,
    persisted/restored retry consumption, and provider cost accounting remain
    open.
  - Verification: focused provider metadata role test covers the current
    paper-visible LLM roles.

- [x] Continue runs after exhausted mutation-provider failures.
  - Paper evidence: AlphaEvolve-style long-running searches require provider
    failure accounting that preserves search progress instead of aborting a run
    on one failed proposal call.
  - Status: exhausted mutation LLM exceptions now produce generated
    failure-history records with bounded/redacted failure metadata and retained
    LLM call telemetry, while later generations can still proceed under the
    same run budget.
  - Remaining paper gap: timeout-driven quarantine, provider penalties, live
    retry/token/cost/time budget enforcement, and cross-adapter retry
    accounting remain open.
  - Verification: focused loop test covers failed mutation logging, continued
    run completion, redaction, and role-accounting failure/success totals.

- [x] Enforce live LLM-call budgets across ensemble retry/fallback attempts.
  - Paper evidence: paper-level compute budgets should account for repeated LLM
    provider attempts caused by retry and fallback, not just successful logical
    calls.
  - Status: the loop now clamps `LLMEnsemble.max_call_attempts` to the
    remaining `max_llm_calls` budget and records actual call-history attempt
    deltas in runtime/candidate budget snapshots.
  - Remaining paper gap: provider-adapter internal retry attempts, live
    token/cost/time enforcement, and persisted/restored retry consumption
    remain open.
  - Verification: focused loop budget tests cover fallback attempt accounting
    and budget-limited fallback suppression.

- [x] Integrate adapter-internal and role-specific retry accounting with
  paper-level LLM budget reports.
  - Paper evidence: AlphaEvolve-style systems use large but explicit compute
    budgets, and provider retries should be bounded and role-attributable.
  - Status: ensemble retry/fallback attempts are capped, call telemetry records
    retry/fallback attempt indices, live logical-call accounting clamps
    remaining ensemble attempts, provider adapters expose `provider_max_retries`
    and per-call `adapter_retry` telemetry, role accounting aggregates
    provider-reported token totals, final manifests emit self-validated
    `runtime.llm_budget_report` records, and retained call-history rows provide
    role-grouped provider-internal retry records.
  - Remaining paper gap: live token/cost/wall-clock and adapter-internal
    attempt stop enforcement, plus persisted/restored retry consumption, remain
    open in the active paper backlog.
  - Verification: focused ensemble tests cover provider usage counts and
    adapter retry diagnostics for mutation, critique, feedback, and meta-prompt
    roles.

- [x] Add role-specific LLM scheduler accounting beyond mutation-only rewards.
  - Paper evidence: AlphaEvolve uses an ensemble of LLMs to balance candidate
    generation throughput and quality across the roles that shape a search.
  - Status: configured reward-accounted roles can now advance scheduler reward
    accounting, non-rewarded roles are persisted as telemetry-only records,
    role labels are validated and forwarded to backend generation hooks,
    scheduler snapshots include role accounting and per-role audit state,
    successful configured feedback graders can write scheduler rewards from
    normalized feedback scores, final manifests copy validated role scheduler
    state, and direct/CLI runs can restore validated scheduler snapshots.
  - Remaining paper gap: independent per-role selection/routing policies,
    quotas, non-mutation reward semantics for critique/meta-prompt outcomes,
    provider cost/default capture, token/cost stop policy, and role-specific
    retry/fallback/quarantine policy remain open in the active backlog.
  - Verification: focused ensemble tests cover configured reward-accounted
    roles, role scheduler-state restore, all loop LLM roles, feedback role
    rewards, and build-time reward-accounted-role propagation.

- [x] Persist mutation timeout failures for paper-level runtime accounting.
  - Paper evidence: timeout failures in long-running LLM search should leave
    auditable artifacts that identify the failed role and provider-call
    category.
  - Status: timed-out mutation calls now produce generated failure-history rows
    with retained timeout-classified LLM call telemetry and can be followed by
    later successful generations under the same run budget.
  - Remaining paper gap: live hard cancellation, timeout-driven
    stop/quarantine behavior beyond mutation failure-history logging, and
    cross-adapter retry accounting remain open.
  - Verification: focused loop test covers mutation timeout artifacts,
    role-accounting timeout totals, and continued run progress.

- [x] Narrow run-local RNG paper TODO to full replay integration.
  - Paper evidence: Section 2.6 reproducibility needs owned stochastic state
    without overclaiming full replay of provider, plugin, validator, or
    controller behavior.
  - Status: the active paper TODO now treats framework RNG persistence and
    checked restore as completed evidence, and keeps the remaining claim scoped
    to full resume/replay integration plus provider/plugin boundary semantics.
  - Remaining paper gap: full replay still lacks provider-output replay,
    plugin-owned RNG capture/exclusion policy beyond the current boundary
    statement, controller/pending-work state restore, and end-to-end lineage
    replay.
  - Verification: focused loop and CLI RNG tests cover persisted snapshots,
    checked restore, seed mismatch rejection, and replay-boundary validation.

- [x] Wire island round-robin cursor and archive-content restore into resumed
  experiment traces.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Sections 2.5 and 2.6.
  - Status: final manifests persist `runtime.history.archive_state` with the
    round-robin cursor, sequence counters, per-island occupancy/elite counts,
    archive contents, per-island MAP-Elites cells, elite-program ids,
    descriptor policy metadata, archive configuration, and explicit
    migration-replay limitations. CLI and direct `evolve()` restore paths can
    load the compact cursor snapshot or the full archive restore bundle, and
    `ProgramDatabase` restores live cells/elites from accepted history while
    preserving the next island cursor.
  - Remaining paper gap: migration placement rows are still not replayed as an
    ordered restore engine, and controller/pending-work state is not restored
    for one-command resumed experiment traces.
  - Verification: focused database/island/CLI tests cover cursor restore, full
    archive restore, restore policy manifests, migration-replay overclaim
    rejection, and mutually exclusive CLI restore flags.

- [x] Narrow environment provenance paper TODO to remaining policy gaps.
  - Paper evidence: paper-facing reproducibility claims should not imply a
    complete environment replay snapshot when manifests retain bounded selected
    evidence.
  - Status: the active paper TODO now treats bounded package, lockfile, pip,
    WHEEL, source/install, NumPy, provider-SDK, accelerator, and audit-only
    package-source evidence as implemented current-state provenance.
  - Remaining paper gap: broader build provenance, live provider service/API
    versions, provider cost or remote defaults, non-project build metadata
    policy, accelerator budget/accounting semantics, and policy-driven
    environment-change tests remain open.
  - Verification: focused provenance tests cover the implemented environment
    provenance surfaces.

- [x] Add paper-visible validator boundary evidence.
  - Paper evidence: reproducibility and evaluator-scope claims need explicit
    execution-boundary metadata, especially when validators run while provider
    credentials may be loaded elsewhere in the process.
  - Status: evaluation metadata now declares local subprocess execution,
    unsupported sandbox/container, host-inherited unsandboxed network egress,
    unsupported network denial, wall-clock-only timeout limits, unsupported
    CPU/memory/GPU/disk/process-count limits, and minimal-environment/
    redacted-diagnostic secret handling.
  - Remaining paper gap: this is still evidence of the current boundary, not
    enforcement of sandboxed network denial, generalized filesystem
    capabilities, resource quotas, distributed evaluator workers, or complete
    environment replay.
  - Verification: focused evaluator tests cover the validator-boundary record.

- [x] Add paper-visible Python validator network policy.
  - Paper evidence: evaluator-boundary claims should distinguish inherited host
    network access from an explicitly configured Python-level denial guard.
  - Status: `validator_network_policy` now records host network inheritance by
    default and can deny Python socket APIs during validator preflight and
    evaluation, with metadata preserving the Python-only denial scope.
  - Remaining paper gap: OS/container-grade validator network isolation,
    native/subprocess egress denial, and a network-mediated provider-secret
    boundary audit remain open.
  - Verification: focused config/evaluator tests cover policy validation,
    host-mode metadata, denied Python socket calls, and denied import-time
    socket calls during preflight.

- [x] Define remaining environment provenance before stronger reproducibility
  claims.
  - Paper evidence: AlphaEvolve-style experimental comparisons depend on the
    implementation, evaluator, numerical libraries, and runtime environment
    used to generate and score candidates.
  - Status: runtime environment provenance now emits
    `environment_reproducibility_policy` with schema
    `libreevolve.environment_reproducibility_policy.v1`. The policy hashes
    bounded package metadata, known lockfiles, installed-package snapshots,
    `pip freeze`, `pip config`, NumPy config, provider SDK versions,
    accelerator hints/probes, and `package_source_policy` evidence. It scopes
    private-source evidence to bounded redacted pip evidence plus raw hashes,
    scopes live-provider evidence to installed SDK versions without live
    service/account lookup, and scopes accelerator evidence to bounded
    hints/probes without budget accounting.
  - Remaining paper gap: current manifests are still not complete
    reproduction evidence. Broader non-project build provenance, live provider
    service/API versions, provider cost or remote provider-side defaults,
    complete private package-source identity/authentication resolution,
    remote package artifact verification, accelerator budget/accounting, and
    OS/container-grade validator network isolation remain open under their
    dedicated TODOs.
  - Verification: focused provenance tests assert the policy shape and prove
    the policy hash changes when covered lockfile evidence changes; README,
    run-artifact docs, architecture docs, and the paper index scope the policy
    as audit-only bounded evidence rather than a complete replay environment.

- [x] Add paper-visible deterministic retrieval source ordering provenance.
  - Paper evidence: retrieval-driven mutation context should not only list
    snippets but also identify whether provider order or a scoring policy chose
    the retained source order.
  - Status: DeepResearch now exposes provider-order and deterministic
    query-overlap source-ranking policies. The opt-in query-overlap policy can
    make retained source relevance affect order, and events, active prompt
    context, cache snapshots, cache keys, and runtime plugin state carry the
    policy and ranking hashes.
  - Remaining paper gap: deterministic lexical overlap is not learned or
    externally scored semantic relevance, and it does not make retrieval
    audit-grade without full provider/source payload artifacts, replayable
    source-content evidence, transport/TLS decision evidence, and a documented
    trust boundary.
  - Verification: focused plugin/config/runtime tests cover policy validation,
    ordering behavior, cache separation, and manifest-visible constructor
    metadata; README, plugin docs, run-artifact docs, and the paper TODO keep
    the remaining audit-grade retrieval limitations scoped.

- [x] Add paper-visible retention-budgeted retrieval payload artifacts.
  - Paper evidence: retrieval-driven mutation context needs replayable evidence
    of the provider/source payloads that were available, not only prompt-sized
    snippets and hashes.
  - Status: cache-backed live DeepResearch retrieval now writes
    `libreevolve.retrieval_payload_artifact.v1` sidecars for full
    secret-redacted provider payloads and retained source-content payloads that
    fit the per-artifact byte budget. Oversized payloads become metadata-only
    omitted artifacts, and `hash_only`/`off` retention modes explicitly suppress
    sidecars. Candidate/cache metadata and plugin artifact summaries link the
    sidecars by path, hashes, payload field, status, bytes, and retention policy.
  - Remaining paper gap: this is bounded redacted replay evidence, not unbounded
    raw source preservation, semantic trust verification, transport/TLS replay,
    learned/external source scoring, or a complete DeepEvolve-style retrieval
    loop.
  - Verification: focused DeepResearch tests cover stored provider/source
    sidecars, redaction, file-hash linkage, manifest summaries, oversized
    metadata-only artifacts, and retention-mode suppression; README,
    run-artifact docs, plugin docs, and paper TODOs scope the remaining
    audit-grade retrieval limitations.

- [x] Add paper-visible retained-source content trust classification.
  - Paper evidence: retrieval-aided experiments should distinguish replayable
    retained source evidence from bounded snippets, hash-only evidence, and
    missing content before treating the retrieval record as reproducible.
  - Status: DeepResearch now emits
    `libreevolve.retrieval_source_content_trust_policy.v1` per retained source
    and as an event-level rollup. It records whether content evidence is backed
    by a verified redacted sidecar, metadata-only oversized sidecar, bounded
    snapshot, hash-only record, or no content evidence; it also records
    replayable-evidence counts, mismatch counts, records hash, and semantic
    verification limitations.
  - Remaining paper gap: the policy is evidence classification only. It does
    not verify semantic meaning, preserve unbounded raw provider/source
    payloads, replay TLS/transport decisions, add learned/external source
    scoring, or implement a DeepEvolve retrieval-debug loop.
  - Verification: focused DeepResearch tests assert sidecar-backed trust,
    snapshot-only trust, aggregate counts, and transport limitation changes;
    docs and TODOs scope the remaining audit-grade retrieval gap.

- [x] Add paper-visible DeepResearch evidence-boundary policy.
  - Paper evidence: when retrieval provenance is intentionally secret-safe and
    bounded, the paper-facing record should state the reproducibility boundary
    rather than implying full raw-source replay.
  - Status: DeepResearch query events now emit
    `libreevolve.retrieval_evidence_boundary_policy.v1`, linking payload
    artifacts, source-content trust, and transport evidence while explicitly
    marking raw provider/source payload retention, TLS certificate-chain
    retention, and semantic verification as unsupported.
  - Remaining paper gap: this is an explicit boundary and retained-evidence
    summary, not unbounded raw payload preservation, TLS/certificate replay,
    semantic source verification, learned/external ranking, or a complete
    DeepEvolve retrieval loop.
  - Verification: focused DeepResearch tests cover the boundary policy for
    sidecar-backed, hash-only, and snapshot-only retrieval evidence; docs and
    TODOs scope the remaining audit-grade retrieval limitations.

- [x] Add paper-visible context-policy evidence to meta-prompt mutation.
  - Paper evidence: AlphaEvolve Sections 2.2 and 4 describe prompt/context
    improvement through meta-prompt evolution, so the mutation prompt should
    expose both the tunable context-policy surface and the selected arm's
    current policy values.
  - Status: meta-prompt mutation requests now carry a compact
    context-policy capability manifest plus per-prompt non-default
    context-policy previews in bounded redacted prompt-performance evidence.
    This lets a provider choosing the optional `context_policy` JSON response
    condition policy edits on the current prompt arm, competing prompt-arm
    summaries, candidate reward evidence, and recent failures.
  - Remaining paper gap: this does not add learned retrieval/summarization,
    richer upstream inspiration selection, or unbounded provider-context
    replay; those remain tracked in the open prompt-context and retrieval TODOs.
  - Verification: focused meta-prompt tests cover capability-manifest exposure,
    non-default context-policy value exposure, and preservation of redaction and
    bounded evidence behavior.

- [x] Add paper-visible required-metric inspiration filtering.
  - Paper evidence: prompt context evolution should be able to affect which
    inspirations are fed into mutation context before the LLM sees them.
  - Status: prompt context policy now includes safe
    `inspiration_required_metric` filtering. Candidate metadata records the
    strategy-ordered pool request, pre-filter pool size, required-metric
    matching count, filtered count, selected ids, and policy source, and plugin
    prompt context receives only the filtered inspirations.
  - Remaining paper gap: this is deterministic metric-presence filtering, not
    learned semantic inspiration retrieval, metric-threshold selection, or a
    full DeepEvolve-style retrieval/debug loop.
  - Verification: focused loop tests prove filtering happens before plugin
    prompt context; prompt/meta-prompt tests cover policy validation,
    persistence, parsing, and evidence exposure.

- [x] Add paper-visible metric-threshold inspiration filtering.
  - Paper evidence: prompt/context evolution should be able to tune inspiration
    selection criteria before mutation prompts are assembled, including
    performance or auxiliary-metric gates.
  - Status: prompt context policy now includes safe
    `inspiration_metric_thresholds` min/max filters over numeric program
    metrics. Candidate metadata records normalized threshold bounds, pool size,
    matching count, filtered count, selected ids, and policy source, and plugin
    prompt context receives only threshold-matching inspirations.
  - Remaining paper gap: this remains deterministic metric-value filtering,
    not learned semantic retrieval, external ranking, or adaptive threshold
    discovery.
  - Verification: focused loop tests prove filtering happens before plugin
    prompt context; prompt/meta-prompt tests cover policy validation,
    persistence, parsing, and evidence exposure.

- [x] Add paper-visible metric ranking for upstream inspirations.
  - Paper evidence: prompt/context evolution should be able to tune the
    ordering criterion for inspirations before the mutation prompt is assembled,
    not only cap the number rendered afterward.
  - Status: prompt context policy now includes safe
    `inspiration_metric_ranking` over numeric program metrics with
    `maximize`/`minimize` direction. Candidate metadata records the ranking
    policy, candidate count, selected ids, and policy source, and plugin prompt
    context receives the metric-ranked final inspirations.
  - Remaining paper gap: this is deterministic metric-value sorting, not
    learned semantic retrieval, external ranking, or adaptive ranking-policy
    discovery.
  - Verification: focused loop tests prove ranking happens before plugin prompt
    context; prompt/meta-prompt tests cover policy validation, persistence,
    parsing, and evidence exposure.

- [x] Add paper-visible plugin-context ordering policy.
  - Paper evidence: prompt/context evolution should be able to shape the order
    of auxiliary plugin context before the mutation prompt is assembled.
  - Status: prompt context policy now includes `plugin_context_order`, a safe
    plugin-identity ordering list. Plugin hooks still execute in configured
    order for deterministic side-effect/provenance behavior, but prompt-visible
    plugin context sections are reordered before aggregate prompt packing, and
    emitted plugin records retain ordering provenance.
  - Remaining paper gap: this is deterministic section ordering, not learned
    plugin context transformation, summarization, semantic routing, or
    retrieval/debug-loop control.
  - Verification: focused loop tests prove prompt-visible ordering and
    provenance; prompt/meta-prompt tests cover policy validation, persistence,
    parsing, and evidence exposure.

- [x] Add paper-visible local context-source ordering policy.
  - Paper evidence: AlphaEvolve Sections 2.2 and 4 describe prompt/context
    improvement through meta-prompt evolution, which includes improving the
    ordering of problem evidence shown to mutation prompts.
  - Status: prompt context policy now includes `context_source_order_policy`.
    The default preserves selected path order, while `task_term_ranked`
    deterministically reorders selected local context sources by task-term
    overlap against rendered source text. Prompt diagnostics retain ranks,
    scores, query-term hash/count, and ranking hash so paper-facing evidence can
    distinguish path-order prompts from relevance-ordered prompts.
  - Remaining paper gap: this is lexical local-source ordering, not learned
    semantic retrieval, source summarization, external ranker provenance, or
    mutation of context-source manifests.
  - Verification: focused prompt/meta-prompt/loop tests cover ranking behavior,
    persistence, parsed meta-prompt policy responses, and evidence exposure.

- [x] Add paper-visible execution-output field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes mutation prompts that can
    use execution results and feedback from prior attempts; prompt/context
    evolution should be able to tune the amount of such evidence.
  - Status: prompt context policy now includes
    `execution_output_max_chars_by_field` for `stdout`, `stderr`, and `error`.
    The selected prompt arm can cap or suppress each field before parent or
    inspiration feedback renders top-level execution output or stage-summary IO
    lines, and prompt diagnostics persist the normalized cap mapping.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of long traces, or full
    validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible nested stage metric-threshold field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results, scores, and feedback from prior attempts; nested
    metric-threshold checks are part of the configured-stage feedback surface.
  - Status: prompt context policy now includes
    `stage_metric_threshold_max_chars_by_field` for nested stage
    metric-threshold fields. The selected prompt arm can cap or suppress each
    prompt-visible nested threshold field before parent or inspiration feedback
    renders validator diagnostics.
  - Remaining paper gap: this is deterministic nested text capping, not
    provider-token context-window fitting, learned summarization of diagnostic
    payloads, nested artifact-output field caps, or full validator metadata
    rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible configured-stage check field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results, scores, and feedback from prior attempts; configured
    stage-threshold diagnostics are part of that bounded feedback surface.
  - Status: prompt context policy now includes
    `configured_stage_check_max_chars_by_field` for configured-stage diagnostic
    fields. The selected prompt arm can cap or suppress each prompt-visible
    configured-stage field before parent or inspiration feedback renders
    validator diagnostics.
  - Remaining paper gap: this is deterministic top-level text capping, not
    provider-token context-window fitting, learned summarization of diagnostic
    payloads, nested metric-threshold/artifact-output field caps, or full
    validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible metric-aggregation diagnostic field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results, scores, and feedback from prior attempts; aggregation
    diagnostics are part of that bounded feedback surface.
  - Status: prompt context policy now includes
    `metric_aggregation_max_chars_by_field` for metric-aggregation diagnostic
    fields. The selected prompt arm can cap or suppress each prompt-visible
    aggregation field before parent or inspiration feedback renders validator
    diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible malformed-metric diagnostic field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results, scores, and feedback from prior attempts; malformed
    metric diagnostics are part of that bounded feedback surface.
  - Status: prompt context policy now includes
    `malformed_metric_max_chars_by_field` for malformed-metric diagnostic
    fields. The selected prompt arm can cap or suppress each prompt-visible
    malformed-metric field before parent or inspiration feedback renders
    validator diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible metric-bound diagnostic field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results, scores, and feedback from prior attempts; metric-bound
    clamp diagnostics are part of that bounded feedback surface.
  - Status: prompt context policy now includes
    `metric_bound_max_chars_by_field` for metric-bound diagnostic fields. The
    selected prompt arm can cap or suppress each prompt-visible metric-bound
    field before parent or inspiration feedback renders validator diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, full
    validator metadata rendering, or real multi-objective optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible syntax-error diagnostic field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results and feedback from prior attempts; syntax-error
    diagnostics are part of that bounded feedback surface.
  - Status: prompt context policy now includes
    `syntax_error_max_chars_by_field` for syntax-error diagnostic fields. The
    selected prompt arm can cap or suppress each prompt-visible syntax-error
    field before parent or inspiration feedback renders validator diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible skipped-artifact field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results and feedback from prior attempts; skipped artifact
    diagnostics are part of that bounded feedback surface.
  - Status: prompt context policy now includes
    `validator_skipped_artifact_max_chars_by_field` for skipped-artifact
    fields. The selected prompt arm can cap or suppress each prompt-visible
    skipped-artifact text field before parent or inspiration feedback renders
    validator-artifact diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of artifact payloads, or full
    validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible sample/retry diagnostic field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results and feedback from previous attempts; retry/sample
    diagnostics are part of that prior-attempt evidence.
  - Status: prompt context policy now includes
    `sample_retry_max_chars_by_field` for sample/retry diagnostic fields. The
    selected prompt arm can cap or suppress each field before parent or
    inspiration feedback renders retry/sample diagnostics, and prompt
    diagnostics persist the normalized cap mapping.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of retry traces, or full
    validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible program-output field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results and feedback from prior attempts; program outputs are
    part of that feedback surface.
  - Status: prompt context policy now includes
    `program_output_max_chars_by_field` for program-output fields. The selected
    prompt arm can cap or suppress each text field before parent or inspiration
    feedback renders program-output diagnostics, and prompt diagnostics persist
    the normalized cap mapping.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of large program-output
    payloads, or full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible validator-artifact field caps.
  - Paper evidence: AlphaEvolve Section 2.2 describes prompt context using
    execution results and feedback from prior attempts; validator artifact
    metadata and excerpts are part of that feedback surface.
  - Status: prompt context policy now includes
    `validator_artifact_max_chars_by_field` for validator-artifact fields. The
    selected prompt arm can cap or suppress each prompt-visible artifact text
    field before parent or inspiration feedback renders validator-artifact
    diagnostics, while bounded artifact file content remains governed by the
    existing artifact-content policy.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of artifact payloads, or full
    validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for nested artifact-output check fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; configured artifact-output checks are
    one prompt-visible feedback channel for validator gates and generated
    artifacts.
  - Status: prompt context policy now includes
    `artifact_output_check_max_chars_by_field` for nested artifact-output check
    fields. The selected prompt arm can cap or suppress each prompt-visible
    artifact-output check text field before parent or inspiration feedback
    renders configured-stage diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for nested validator resource-limit fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; validator execution-boundary and
    resource-limit diagnostics are one prompt-visible feedback channel for
    execution constraints around prior attempts.
  - Status: prompt context policy now includes
    `validator_resource_limit_max_chars_by_field` for nested validator
    resource-limit fields. The selected prompt arm can cap or suppress each
    prompt-visible resource-limit text field before parent or inspiration
    feedback renders validator-boundary diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for validator-stdin diagnostic fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; validator stdin diagnostics are one
    prompt-visible feedback channel for execution setup around prior attempts.
  - Status: prompt context policy now includes
    `validator_stdin_max_chars_by_field` for validator-stdin diagnostic fields.
    The selected prompt arm can cap or suppress each prompt-visible stdin text
    field before parent or inspiration feedback renders execution diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for diagnostic-output fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; diagnostic-output metadata is one
    prompt-visible feedback channel for validator stdout/stderr handling around
    prior attempts.
  - Status: prompt context policy now includes
    `diagnostic_output_max_chars_by_field` for diagnostic-output fields. The
    selected prompt arm can cap or suppress each prompt-visible
    diagnostic-output text field before parent or inspiration feedback renders
    execution diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for timeout-cleanup diagnostic fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; timeout-cleanup metadata is one
    prompt-visible feedback channel for evaluator timeout handling around prior
    attempts.
  - Status: prompt context policy now includes
    `timeout_cleanup_max_chars_by_field` for timeout-cleanup fields. The
    selected prompt arm can cap or suppress each prompt-visible timeout-cleanup
    text field before parent or inspiration feedback renders execution
    diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for validator-boundary diagnostic fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; validator-boundary diagnostics are one
    prompt-visible feedback channel for execution constraints around prior
    attempts.
  - Status: prompt context policy now includes
    `validator_boundary_max_chars_by_field` for top-level validator-boundary
    fields. The selected prompt arm can cap or suppress each prompt-visible
    boundary text field before parent or inspiration feedback renders execution
    diagnostics.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of diagnostic payloads, or
    full validator metadata rendering.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for LLM-grader feedback fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; LLM-grader reviewer records are one
    prompt-visible feedback channel for prior attempts.
  - Status: prompt context policy now includes
    `llm_feedback_max_chars_by_field` for LLM-grader feedback fields. The
    selected prompt arm can cap or suppress each prompt-visible grader field
    before parent or inspiration feedback renders LLM-grader records.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of reviewer payloads, or full
    prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for proposal metadata fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; LibreEvolve proposal summaries are one
    prompt-visible context channel for prior parent and inspiration programs.
  - Status: prompt context policy now includes
    `proposal_max_chars_by_field` for proposal metadata fields. The selected
    prompt arm can cap or suppress each prompt-visible proposal field before
    parent or inspiration feedback renders proposal summaries.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned proposal summarization, or full
    prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for stage-summary fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; stage summaries are one prompt-visible
    feedback channel for prior attempts.
  - Status: prompt context policy now includes
    `stage_summary_max_chars_by_field` for stage-summary fields. The selected
    prompt arm can cap or suppress each prompt-visible stage-summary field
    before parent or inspiration feedback renders stage summaries.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of stage feedback, or full
    prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for validator metadata-summary keys.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; validator metadata summaries are one
    prompt-visible diagnostic feedback channel for prior attempts.
  - Status: prompt context policy now includes
    `validator_metadata_max_chars_by_key` for selected validator metadata
    summary keys. The selected prompt arm can cap or suppress each
    prompt-visible metadata value before parent or inspiration feedback renders
    validator metadata summaries.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, learned summarization of metadata payloads, or full
    prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible item-count control for validator metadata summaries.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; metadata-summary volume is part of the
    prompt-visible feedback budget for prior attempts.
  - Status: prompt context policy now includes `validator_metadata_limit` for
    validator metadata summaries. The selected prompt arm can cap or suppress
    the number of prompt-visible metadata-summary items before parent or
    inspiration feedback renders validator diagnostics.
  - Remaining paper gap: this is deterministic item-count control, not
    provider-token context-window fitting, full validator metadata rendering,
    learned summarization, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible caps for recent failure-memory fields.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; failed-attempt memory is one
    prompt-visible feedback channel for avoiding repeated bad proposals.
  - Status: prompt context policy now includes
    `recent_failure_max_chars_by_field` for rendered recent failure-memory
    fields. The selected prompt arm can cap or suppress mutation/error/diff,
    evaluation, stage, and selected feedback diagnostic fields before recent
    failure memory renders.
  - Remaining paper gap: this is deterministic text capping, not provider-token
    context-window fitting, queryable persistent failed-proposal memory, learned
    failure summarization, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible control for mutation-instruction examples.
  - Paper evidence: AlphaEvolve Sections 2.2 and 4 describe improving prompt
    instructions and context through meta-prompt evolution; mutation-format
    guidance is one instruction channel that can be tuned safely.
  - Status: prompt context policy now includes
    `mutation_instruction_include_example`, a boolean that preserves the
    built-in mutation-format example by default or removes that example block
    for a selected prompt arm while keeping the core format rules.
  - Remaining paper gap: this is deterministic instruction verbosity control,
    not arbitrary learned instruction rewriting, provider-token context-window
    fitting, retrieval/summarization evolution, or full prompt-context
    optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and evidence exposure.

- [x] Add paper-visible control for proposal metadata capture.
  - Paper evidence: AlphaEvolve Sections 2.2 and 4 describe improving prompt
    instructions and context through meta-prompt evolution; proposal metadata
    is a traceability/instruction channel for mutation attempts.
  - Status: prompt context policy now includes `proposal_metadata_enabled`, a
    nullable boolean that preserves the run-level proposal-metadata setting by
    default or enables/disables proposal metadata instructions and parsing for
    the selected prompt arm.
  - Remaining paper gap: this is deterministic proposal metadata on/off
    control, not learned proposal-schema evolution, provider-token
    context-window fitting, retrieval/summarization evolution, or full
    prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    loop-level proposal capture/stripping, validation, persistence, parsed
    policy responses, and evidence exposure.

- [x] Add paper-visible exclusion filters for inspiration metrics.
  - Paper evidence: AlphaEvolve Sections 2.2 and 2.5 frame prompt context as
    previous programs selected from the evolutionary database, so paper-facing
    prompt policy should expose safe controls for upstream inspiration
    selection.
  - Status: prompt context policy now includes `inspiration_excluded_metrics`,
    a deduplicated safe list of manifest-safe metric names. Upstream
    inspirations carrying any listed metric are filtered before plugin context
    and prompt rendering, and candidate metadata records the filter policy,
    counts, and selected ids.
  - Remaining paper gap: this is deterministic metric-absence filtering, not
    learned semantic inspiration retrieval, diversity-objective policy
    evolution, retrieval/summarization evolution, or full prompt-context
    optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover validation,
    upstream filtering before plugin context, persistence, parsed policy
    responses, and evidence exposure.

- [x] Add paper-visible fitness thresholds for inspiration selection.
  - Paper evidence: AlphaEvolve Sections 2.2 and 2.5 frame prompt context as
    previous programs selected from the evolutionary database using search
    state, so paper-facing prompt policy should expose safe quality-based
    inspiration controls.
  - Status: prompt context policy now includes `inspiration_fitness_threshold`,
    a nullable finite-fitness `{min,max}` filter. Upstream inspirations outside
    the configured fitness range are filtered before plugin context and prompt
    rendering, and candidate metadata records normalized bounds, counts, and
    selected ids.
  - Remaining paper gap: this is deterministic fitness-threshold filtering, not
    learned semantic inspiration retrieval, diversity-objective policy
    evolution, retrieval/summarization evolution, or full prompt-context
    optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover validation,
    upstream filtering before plugin context, persistence, parsed policy
    responses, and evidence exposure.

- [x] Add paper-visible selectors for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; failed-attempt memory is one
    prompt-visible feedback channel, so prompt policy should be able to choose
    which retained failures are shown.
  - Status: prompt context policy now includes
    `recent_failure_selection_policy` with safe deterministic values
    `recent`, `oldest`, and `lowest_score`. The selected prompt arm can choose
    retained failure-memory records before the render limit and per-field caps
    are applied, and prompt diagnostics record the selector and selection
    semantics.
  - Remaining paper gap: this is deterministic retained-record selection, not
    learned failure summarization, queryable persistent failed-proposal memory,
    provider-token context-window fitting, retrieval/summarization evolution,
    or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible error filters for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; failure-memory policy should be able to
    choose failure categories, not only count and crop retained records.
  - Status: prompt context policy now includes
    `recent_failure_required_errors`, a deduplicated list of safe exact-match
    labels. Retained failure-memory records are filtered by `error` or
    `diff_error` before selection, limiting, and per-field caps, and prompt
    diagnostics record required labels, matched count, filtered count, and
    filter policy.
  - Remaining paper gap: this is deterministic exact-label filtering, not
    learned failure clustering or summarization, queryable persistent
    failed-proposal memory, provider-token context-window fitting,
    retrieval/summarization evolution, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible score thresholds for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; failure-memory policy should be able to
    use score evidence when selecting which failed attempts are shown.
  - Status: prompt context policy now includes
    `recent_failure_score_threshold`, a nullable finite-score `{min,max}`
    filter. Retained failure-memory records are filtered by score bounds before
    selection, limiting, and per-field caps, and prompt diagnostics record
    normalized bounds, matched count, filtered count, and filter policy.
  - Remaining paper gap: this is deterministic finite-score filtering, not
    learned failure clustering or summarization, queryable persistent
    failed-proposal memory, provider-token context-window fitting,
    retrieval/summarization evolution, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible exclusion filters for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; failure-memory policy should be able to
    suppress retained failure categories that are not useful for the selected
    prompt arm.
  - Status: prompt context policy now includes
    `recent_failure_excluded_errors`, a deduplicated list of safe exact-match
    labels. Retained failure-memory records carrying any listed `error` or
    `diff_error` label are excluded before score filtering, selection,
    limiting, and per-field caps, and prompt diagnostics record excluded
    labels, filtered count, and policy.
  - Remaining paper gap: this is deterministic exact-label exclusion, not
    learned failure clustering or summarization, queryable persistent
    failed-proposal memory, provider-token context-window fitting,
    retrieval/summarization evolution, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible changed-file filters for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; failure-memory policy should be able to
    focus prompt context on failed edits for selected source areas.
  - Status: prompt context policy now includes
    `recent_failure_required_changed_files`, a deduplicated list of safe
    problem-relative paths. Retained failure-memory records are filtered by
    exact `changed_files` path before score filtering, selection, limiting,
    and per-field caps, and prompt diagnostics record required paths, matched
    count, filtered count, and policy.
  - Remaining paper gap: this is deterministic exact path filtering, not
    learned source-area clustering or summarization, queryable persistent
    failed-proposal memory, provider-token context-window fitting,
    retrieval/summarization evolution, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible changed-file exclusion filters for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; failure-memory policy should be able to
    omit failed edits for selected source areas as well as require them.
  - Status: prompt context policy now includes
    `recent_failure_excluded_changed_files`, a deduplicated list of safe
    problem-relative paths. Retained failure-memory records carrying any listed
    exact `changed_files` path are excluded before score filtering, selection,
    limiting, and per-field caps, and prompt diagnostics record excluded
    paths, filtered count, and policy.
  - Remaining paper gap: this is deterministic exact path exclusion, not
    learned source-area clustering or summarization, queryable persistent
    failed-proposal memory, provider-token context-window fitting,
    retrieval/summarization evolution, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible repetition thresholds for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; repeated failed attempts are useful
    prompt-context evidence for avoiding recurring invalid proposal patterns.
  - Status: prompt context policy now includes
    `recent_failure_repetition_threshold`, a nullable integer `{min,max}`
    filter over retained failure-memory `repetition_count`. Retained
    failure-memory records are filtered by repetition bounds before score
    filtering, selection, limiting, and per-field caps, and prompt diagnostics
    record normalized bounds, matched count, filtered count, and policy.
  - Remaining paper gap: this is deterministic repetition-count filtering, not
    learned failure clustering or summarization, queryable persistent
    failed-proposal memory, provider-token context-window fitting,
    retrieval/summarization evolution, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible highest-repetition selection for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; repeated failed attempts are useful
    prompt-context evidence and should be selectable as a priority.
  - Status: prompt context policy now supports
    `recent_failure_selection_policy: "highest_repetition"`. Retained
    failure-memory records can be ordered by descending valid
    `repetition_count` before render limiting, and prompt diagnostics record
    the selector and selection semantics.
  - Remaining paper gap: this is deterministic repetition sorting, not learned
    failure clustering or summarization, queryable persistent failed-proposal
    memory, provider-token context-window fitting, retrieval/summarization
    evolution, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt tests cover rendering,
    validation, parsed policy responses, and canonical metadata defaults.

- [x] Add paper-visible stage-name filters for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; evaluator-stage failures are useful
    context evidence and should be selectable for prompt arms.
  - Status: prompt context policy now includes
    `recent_failure_required_stage_names` and
    `recent_failure_excluded_stage_names`, deduplicated lists of manifest-safe
    evaluation stage labels. Retained failure-memory records are filtered by
    exact `evaluation.stages[].name` before repetition/score filtering,
    selection, limiting, and per-field caps, and prompt diagnostics record
    required/excluded stage names, matched counts, filtered counts, and policy.
  - Remaining paper gap: this is deterministic exact stage-label filtering,
    not learned failure clustering or summarization, queryable persistent
    failed-proposal memory, provider-token context-window fitting,
    retrieval/summarization evolution, or full prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible render-count caps for local context sources.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as selected
    prior/contextual evidence; prompt arms should be able to control how many
    ranked context sources consume prompt budget.
  - Status: prompt context policy now includes `context_source_limit`, a
    nullable non-negative cap applied after local context path selection and
    optional task-term ranking. Prompt diagnostics record the pre-limit order,
    omitted paths, selected/omitted counts, and a selection hash when the cap is
    configured.
  - Remaining paper gap: this is deterministic render-count capping over
    already loaded local sources, not learned semantic retrieval, source
    summarization, provider-token context-window fitting, or full retrieval
    provenance.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    evidence.

- [x] Add paper-visible content-term filters for local context sources.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as selected
    prior/contextual evidence; prompt arms should be able to steer which
    loaded context sources are eligible before ranking and prompt-budget use.
  - Status: prompt context policy now includes
    `context_source_required_terms` and `context_source_excluded_terms`,
    deduplicated safe term lists. Loaded local context sources are filtered by
    required all-term matches and excluded any-term matches before ranking,
    limiting, and rendering. Prompt diagnostics record terms, omitted paths,
    match/filter counts, selected count, and a selection hash.
  - Remaining paper gap: this is deterministic term filtering over already
    loaded local sources, not learned semantic retrieval, source
    summarization, provider-token context-window fitting, or full retrieval
    provenance.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible explicit ranking terms for local context sources.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as selected
    prior/contextual evidence; prompt arms should be able to steer the ordering
    signal for loaded context sources, not only inherit task-description terms.
  - Status: prompt context policy now includes
    `context_source_ranking_terms`, a deduplicated safe term list. When local
    context sources are task-term ranked, these terms replace task-description
    derived query terms. Prompt diagnostics record the query source,
    query-term hash/count, configured terms when present, source scores, and
    the ranking hash.
  - Remaining paper gap: this is deterministic explicit-term ordering over
    already loaded local sources, not learned semantic retrieval, source
    summarization, provider-token context-window fitting, or full retrieval
    provenance.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible content-term filters for plugin context.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as selected
    prior/contextual evidence; meta-prompt evolution should be able to steer
    which contextual plugin evidence reaches a prompt arm.
  - Status: prompt context policy now includes
    `plugin_context_required_terms` and `plugin_context_excluded_terms`,
    deduplicated safe term lists. Bounded plugin context text is filtered by
    required all-term matches and excluded any-term matches before prompt
    visibility, while hook execution and provenance remain recorded. Plugin
    diagnostics record selected status, missing required terms, matched
    excluded terms, and a selection hash.
  - Remaining paper gap: this is deterministic term filtering over already
    generated plugin context, not learned semantic retrieval, source
    summarization, provider-token context-window fitting, or full retrieval
    provenance.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible render-count caps for plugin context.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as selected
    prior/contextual evidence; prompt arms should be able to control how many
    plugin context sections consume prompt budget.
  - Status: prompt context policy now includes `plugin_context_limit`, a
    nullable non-negative cap applied after plugin allowlist filtering, safe
    content-term filtering, and plugin context ordering. Prompt diagnostics
    record source limit, pre-limit count, selected/omitted counts, rank,
    selected status, and a selection hash for limited plugin context sections.
  - Remaining paper gap: this is deterministic render-count capping over
    already generated plugin context, not learned semantic retrieval, source
    summarization, provider-token context-window fitting, or full retrieval
    provenance.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible global character caps for plugin context.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as selected
    prior/contextual evidence; prompt arms should be able to control how much
    plugin context each section can consume before prompt rendering.
  - Status: prompt context policy now includes `plugin_context_max_chars`, a
    nullable non-negative cap applied to every plugin context section before
    prompt visibility. Prompt diagnostics record the global policy cap,
    per-label cap, effective cap, original character count, and truncation
    status.
  - Remaining paper gap: this is deterministic per-section character capping
    over already generated plugin context, not learned semantic retrieval,
    source summarization, provider-token context-window fitting, or full
    retrieval provenance.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible excluded-label skips for plugin context.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as selected
    prior/contextual evidence; prompt arms should be able to suppress noisy or
    irrelevant contextual plugin channels without switching to a full allowlist.
  - Status: prompt context policy now includes
    `plugin_context_excluded_labels`, a deduplicated safe plugin identity label
    list. Matching plugins are skipped before prompt-context hooks run, and
    diagnostics record `excluded_by_prompt_context_labels` visibility plus the
    configured exclusion policy.
  - Remaining paper gap: this is deterministic plugin identity filtering, not
    learned semantic retrieval, source summarization, provider-token
    context-window fitting, or full retrieval provenance.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible explicit ranking terms for plugin context.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as selected
    prior/contextual evidence; prompt arms should be able to steer ordering of
    plugin context before prompt-budget use.
  - Status: prompt context policy now includes `plugin_context_ranking_terms`,
    a deduplicated safe term list. Prompt-visible plugin context sections can
    be ranked by deterministic term overlap before `plugin_context_limit`
    applies. Prompt diagnostics record configured terms, term hash/count,
    score, rank, previous rank, candidate count, and a ranking hash.
  - Remaining paper gap: this is deterministic explicit-term ordering over
    already generated plugin context, not learned semantic retrieval, source
    summarization, provider-token context-window fitting, or full retrieval
    provenance.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible text-term filters for recent failure memory.
  - Paper evidence: AlphaEvolve Section 2.2 frames prompt context as previous
    programs plus evaluation feedback; prompt arms should be able to steer
    which failure evidence is retained in prompt context.
  - Status: prompt context policy now includes
    `recent_failure_required_terms` and `recent_failure_excluded_terms`,
    deduplicated safe term lists. Retained failure-memory records are filtered
    by all required terms and any excluded terms found in failure evidence
    before repetition/score filtering, selection, and limiting. Prompt
    diagnostics record configured terms, match/filter counts, and policies
    when configured.
  - Remaining paper gap: this is deterministic safe-term filtering over
    retained failure evidence, not learned failure clustering, semantic
    failed-proposal retrieval, provider-token context-window fitting, or full
    prompt-context optimization.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible budget fields for validator execution diagnostics.
  - Paper evidence: AlphaEvolve Section 2.6 emphasizes compute-budgeted
    experiments, and Section 2.2 frames evaluation feedback as prompt context;
    prompt arms should be able to expose bounded stage/sample budget evidence.
  - Status: prompt context policy now includes `validator_budget_fields` and
    `validator_budget_max_chars_by_field`. Execution diagnostics can render a
    `validator_budget` subgroup from `stage_budget` and `sample_budget`
    metadata with selected fields and per-field caps.
  - Remaining paper gap: this is paper-visible prompt evidence for existing
    evaluator budget metadata, not unified AlphaEvolve-scale compute-budget
    enforcement, provider-token fitting, or full budget-resume accounting.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible synthetic failure metric diagnostics.
  - Paper evidence: AlphaEvolve Section 2.2 frames evaluation feedback as
    prompt context, while benchmark claims require distinguishing true scores
    from framework-assigned failure penalties.
  - Status: prompt context policy now includes `synthetic_metric_fields` and
    `synthetic_metric_max_chars_by_field`. Validator diagnostics can render a
    `synthetic_metrics` group from `evaluation.metadata.synthetic_metrics`,
    exposing selected policy, penalty, schema, and metric-name evidence with
    per-field caps.
  - Remaining paper gap: this is prompt-visible diagnostic evidence for
    synthetic penalties, not independent result certification, holdout
    correctness, or real multi-objective frontier accounting.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible materialization error diagnostics.
  - Paper evidence: AlphaEvolve Section 2.2 frames evaluator feedback as prompt
    context; candidate-preparation failures should have bounded, selectable
    feedback rather than disappearing into generic metadata.
  - Status: prompt context policy now includes `materialization_error_fields`
    and `materialization_error_max_chars_by_field`. Validator diagnostics can
    render a `materialization_error` group from
    `evaluation.metadata.materialization_error`, exposing selected exception
    type and message fields with per-field caps.
  - Remaining paper gap: this is prompt-visible evidence for local
    materialization failures, not a full sandbox/container execution model or
    AlphaEvolve-grade validator capability policy.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, persistence, parsed policy responses, and meta-prompt policy
    flow.

- [x] Add paper-visible evaluator path provenance diagnostics.
  - Paper evidence: AlphaEvolve Section 2.2 frames previous evaluation
    feedback as prompt context; that feedback should be attributable to the
    validator path that produced it while preserving path redaction.
  - Status: prompt context policy now includes `evaluator_path_fields` and
    `evaluator_path_max_chars_by_field`. Validator diagnostics can render an
    `evaluator_path` group from evaluation metadata, exposing selected
    redacted validate path, scope, hash, and redaction-status fields with
    per-field caps.
  - Remaining paper gap: this is prompt-visible provenance for existing
    evaluator path metadata, not a full provider-token packing policy,
    containerized validator contract, or complete validator-metadata prompt
    policy.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, parsed policy responses, and meta-prompt policy flow.

- [x] Add paper-visible evaluator dependency provenance diagnostics.
  - Paper evidence: AlphaEvolve Section 2.2 frames evaluation feedback as
    prompt context; dependency provenance should be selectable prompt evidence
    when validator behavior depends on problem-local helper or data files.
  - Status: prompt context policy now includes `evaluator_dependency_fields`
    and `evaluator_dependency_max_chars_by_field`. Validator diagnostics can
    render an `evaluator_dependency` group from
    `evaluation.metadata.evaluator_dependency_policy`, exposing selected
    policy labels, file counts, derived redacted dependency paths, hashes, and
    redaction flags with per-field caps.
  - Remaining paper gap: this is prompt-visible provenance for existing
    problem-local dependency metadata, not full filesystem capability
    enforcement, containerized validators, or provider-token context packing.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, parsed policy responses, and meta-prompt policy flow.

- [x] Add paper-visible evaluator stage-context diagnostics.
  - Paper evidence: AlphaEvolve Section 2.2 frames prior evaluation results
    and outputs as prompt context; stage/sample/attempt context should be
    selectable feedback when cascades, samples, or retries affect outcomes.
  - Status: prompt context policy now includes `evaluator_stage_fields` and
    `evaluator_stage_max_chars_by_field`. Validator diagnostics can render an
    `evaluator_stage` group from `evaluation.metadata.stage`, exposing
    selected stage name/index, sample index, attempt, seed, sanitized
    configured validate path, stdin policy, and evaluator-data counts with
    per-field caps.
  - Remaining paper gap: this is prompt-visible context for existing evaluator
    stage metadata, not provider-token section packing, learned prompt-context
    selection, or a complete validator capability model.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, parsed policy responses, and meta-prompt policy flow.

- [x] Add paper-visible validator environment diagnostics.
  - Paper evidence: AlphaEvolve Section 2.2 frames evaluator feedback as
    prompt context; prompt-visible feedback should expose the validator
    environment boundary policy without exposing environment values.
  - Status: prompt context policy now includes `validator_env_fields` and
    `validator_env_max_chars_by_field`. Execution diagnostics can render a
    `validator_env` group from `evaluation.metadata.validator_env`, exposing
    selected value-free policy, default-key, allowlist, provided-key, and
    redaction-status fields with per-field caps.
  - Remaining paper gap: this is prompt-visible evidence for the existing
    minimal environment policy, not full OS-level secret isolation,
    containerized validation, or provider-budget enforcement.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, parsed policy responses, and meta-prompt policy flow.

- [x] Add paper-visible evaluator workspace diagnostics.
  - Paper evidence: AlphaEvolve Section 2.2 frames prior evaluation results
    and outputs as prompt context; evaluated workspace provenance should be
    selectable when multi-file programs or loaded workspace files affect
    interpretation of the result.
  - Status: prompt context policy now includes `evaluator_workspace_fields`
    and `evaluator_workspace_max_chars_by_field`. Validator diagnostics can
    render an `evaluator_workspace` group from evaluator metadata, exposing
    selected primary file, file count, and bounded file list with per-field
    caps.
  - Remaining paper gap: this is prompt-visible context for existing evaluated
    workspace provenance metadata, not provider-token section packing, learned
    prompt-context selection, or a complete validator capability model.
  - Verification: focused prompt/meta-prompt/loop tests cover rendering,
    validation, parsed policy responses, and meta-prompt policy flow.

- [x] Add paper-visible wildcard LLM role budget scopes.
  - Paper evidence: AlphaEvolve-style LLM scheduling is compute-budgeted by
    role surfaces such as mutation, critique, and feedback; feedback graders
    need a grouped budget surface rather than only exact per-grader caps.
  - Status: runtime LLM role budget maps now accept manifest-safe prefix scopes
    ending in `:*`, including `feedback:*`. Logical calls, provider attempts,
    tokens, configured cost, and retained call latency share scoped limits
    across matching concrete roles, while manifests and budget reports continue
    to expose exact-role consumption rows.
  - Remaining paper gap: this is grouped live role-budget enforcement for the
    synchronous controller, not async worker budgeting, provider-output replay,
    live provider pricing, or hard SDK cancellation.
  - Verification: focused config, ensemble, and loop tests cover scope
    validation, scheduler restore rejection for over-consumed scopes, live
    scoped budget stops, and runtime budget-report rows.

- [x] Add paper-visible Appendix A matrix target registry.
  - Paper evidence: AlphaEvolve Appendix A Table 3 reports 54 sorted matrix
    multiplication target sizes with best-known rank, AlphaEvolve rank,
    exact-algorithm status, and 38 matched, 14 surpassed, and 2 fell-behind
    outcomes.
  - Status: `libreevolve.alphaevolve_appendix_a_matrix_registry.v1` records the
    54 target identities and Table 3 ranks/outcomes, validates the registry
    against the paper counts, and makes `libreevolve.matrix_result_report.v1`
    reports for `alphaevolve_appendix_a` verify `target_id` and `dimensions`
    against the registry.
  - Remaining paper gap: LibreEvolve still does not provide the tensor
    decompositions, exact certificates, generated notebooks, or benchmark
    runner needed to produce real AlphaEvolve-comparable result instances.
  - Verification: focused Appendix A registry and matrix-result tests cover
    registry counts, target lookup, malformed target rows, and report
    target/dimension mismatches.

- [x] Add paper-visible lineage resurfacing heuristics.
  - Paper evidence: AlphaEvolve's database is expected to resurface previously
    explored ideas across exploration/exploitation surfaces; the open
    multi-score/database gap specifically called out lineage-aware resurfacing.
  - Status: LibreEvolve now exposes `lineage` parent and inspiration sampling
    strategies that choose the best retained representative per root lineage,
    persist a parent-sampling cursor, and record lineage-root provenance in
    generated candidate metadata. Prompt-context policy validation accepts the
    same inspiration strategy.
  - Remaining paper gap: this remains a heuristic over live retained archive
    state, not the paper-faithful persisted evolutionary database with
    queryable lineage/feedback/metric resurfacing and replayable sampling
    decisions.
  - Verification: focused island, CLI/config, loop, prompt-policy, and docs
    tests cover the lineage strategy surfaces.

- [x] Add paper-visible lineage-index manifest evidence.
  - Paper evidence: AlphaEvolve-style program databases need auditable
    evolutionary lineage context when varied historical programs are reused as
    parents or inspirations.
  - Status: completed runs now persist `runtime.history.lineage_index`, a
    bounded best-valid-programs view grouped by root lineage, with top retained
    lineage records and available objective-vector evidence. This makes
    lineage-aware resurfacing evidence inspectable from run artifacts.
  - Remaining paper gap: this remains a bounded diagnostic manifest view, not
    the paper-faithful durable database with full lineage/feedback/metric
    indexes and replayable resurfacing decisions.
  - Verification: focused database and loop tests cover the lineage index API
    and manifest persistence.

- [x] Add paper-visible descriptor-index manifest evidence.
  - Paper evidence: AlphaEvolve's quality-diversity database should make varied
    historical programs auditable across archive descriptor surfaces, including
    diversity-like coordinates.
  - Status: completed runs now persist `runtime.history.descriptor_index`, a
    bounded top-program view for finite archive-admission descriptor values
    with lineage root, selection score, fitness, and available objective
    evidence.
  - Remaining paper gap: this remains a diagnostic view over insertion-time
    descriptor coordinates, not stable descriptor replay, learned behavior
    embeddings, or a full replayable evolutionary database.
  - Verification: focused database and loop tests cover the descriptor index
    API and manifest persistence.

- [x] Add paper-visible feedback-index manifest evidence.
  - Paper evidence: AlphaEvolve-style search can use prior execution and
    feedback signals in future prompts and database resurfacing, so those
    signals should be auditable from run artifacts.
  - Status: completed runs now persist `runtime.history.feedback_index`, a
    bounded feedback-record view grouped by LLM feedback grader with scoring,
    delta, discard/error, objective-metric, retention, and bounded text
    hash/preview evidence.
  - Remaining paper gap: this remains a diagnostic view over retained feedback
    metadata, not feedback embeddings, full-text ranking, or replayable
    feedback-driven sampling decisions.
  - Verification: focused database and loop tests cover the feedback index API
    and manifest persistence.

- [x] Add paper-visible evaluator artifact index evidence.
  - Paper evidence: AlphaEvolve-style program databases resurface previously
    explored programs using rich evidence, so evaluator-produced artifacts
    should be inspectable from completed run artifacts and available to
    resurfacing heuristics.
  - Status: completed runtime manifests now persist
    `runtime.history.artifact_index`, a bounded view over copied evaluator
    artifacts with path/hash, byte-count, redaction, skipped-file, stage, and
    bounded content-excerpt summaries. Valid artifact-bearing programs now feed
    an `artifact` source into `runtime.history.resurfacing_index`.
  - Remaining paper gap: this remains diagnostic manifest evidence, not a
    paper-faithful durable program database, full artifact-content index,
    semantic artifact search layer, or replayable artifact-driven sampling
    policy.
  - Verification: focused database and loop tests cover manifest evidence,
    artifact-index records, and resurfacing source fusion.

- [x] Add paper-visible score-index manifest evidence.
  - Paper evidence: AlphaEvolve-style databases resurface high-performing
    historical programs under exploration/exploitation policies, so ranked
    score evidence should be inspectable from completed run artifacts.
  - Status: completed runs now persist `runtime.history.score_index`, a bounded
    top-valid-programs view ranked by selection score then final fitness with
    archive-admission and objective-vector evidence when available.
  - Remaining paper gap: this remains diagnostic manifest evidence, not the
    paper-faithful durable database or replayable score-driven sampling
    decisions.
  - Verification: focused database and loop tests cover the score index API and
    manifest persistence.

- [x] Make timeout quarantine policy paper-visible in manifests.
  - Paper evidence: AlphaEvolve-style budgeted LLM systems need timeout and
    failure handling to be auditable by role and budget action.
  - Status: runtime cancellation-policy manifests now declare timeout
    `quarantine` actions and `quarantine_record` evidence for role scopes with
    configured `llm_role_failure_quarantine_after` thresholds.
  - Remaining paper gap: this remains manifest evidence for the existing
    failure-threshold quarantine mechanism, not hard provider cancellation,
    timeout-specific stop enforcement, or async controller cancellation.
  - Verification: focused loop tests cover valid default and configured
    timeout-quarantine policy records.

- [x] Add paper-visible migration replay audit evidence.
  - Paper evidence: AlphaEvolve-style island migration and resume claims need
    persisted placement events to reconcile with final archive state.
  - Status: completed runtime manifests now persist
    `runtime.history.archive_event_replay_audit`, an audit-only replay of final
    admitted migration placements compared against archive-content snapshots.
  - Remaining paper gap: this does not make migration events the restore
    engine and does not restore controller or pending worker state.
  - Verification: focused database and loop tests cover the audit helper and
    manifest field.

- [x] Add paper-visible terminal controller drained-state evidence.
  - Paper evidence: AlphaEvolve-style resume claims need explicit controller
    state boundaries, including whether queued/running work remains at a
    checkpoint.
  - Status: completed runtime manifests now persist
    `runtime.history.controller_state`, showing that the synchronous
    single-process controller is terminally drained with no queued/running
    proposals, evaluations, in-flight LLM calls, or pending archive admissions.
  - Remaining paper gap: async controller queues, mid-generation checkpoints,
    pending worker state, and provider-output replay remain open.
  - Verification: focused loop tests cover the terminal controller-state
    manifest field.

- [x] Add paper-visible plugin context truncation policy.
  - Paper evidence: AlphaEvolve describes evolving prompt instructions and
    context, so prompt-program policy should be able to alter how plugin
    context is shaped before it reaches mutation prompts.
  - Status: prompt context policy now supports `plugin_context_truncation`
    with `head` and `head_tail` modes. Generated prompt diagnostics and
    plugin-context metadata record the selected truncation plus a
    `libreevolve.plugin_context_content_policy.v1` content-policy record, and
    meta-prompt capability text exposes the knob for future mutations.
  - Remaining paper gap: this is bounded prompt-context shaping, not evolved
    retrieval/summarization transport or a learned source-ranking policy.
  - Verification: focused prompt and loop tests cover validation, prompt
    rendering, metadata persistence, and meta-prompt evidence.

- [x] Add paper-visible backend context-window prompt cap evidence.
  - Paper evidence: AlphaEvolve-style prompt construction operates under
    model context limits and output budgets, so backend/model prompt caps should
    be attributable before provider calls.
  - Status: backend specs and direct backend metadata can now declare
    `context_window_tokens` and optional `reserved_output_tokens`. The ensemble
    subtracts the reserve, applies the derived heuristic prompt capacity before
    provider calls, and records the configured window, reserve, and derived
    prompt capacity in LLM call telemetry.
  - Remaining paper gap: this is explicit heuristic budget evidence, not exact
    provider-tokenizer packing or live provider context/pricing discovery.
  - Verification: focused config and ensemble tests cover validation,
    normalized metadata, pre-call enforcement, and telemetry.

- [x] Add paper-visible retrieval context audit classification.
  - Paper evidence: external retrieval context can influence candidate
    mutations, so paper-level provenance needs to distinguish bounded
    replay/snapshot evidence from degraded or unauditable prompt context.
  - Status: successful retrieval events and active-context metadata now expose
    `libreevolve.retrieval_context_audit_policy.v1`, linking the exact
    prompt-visible retrieval synthesis to transport, source-content trust,
    evidence-boundary, and lexical-grounding states while keeping retrieval
    text non-authoritative.
  - Remaining paper gap: unbounded raw provider/source payloads, TLS
    certificate chains, semantic source-content verification, and
    DeepEvolve-style hypothesis refinement remain open.
  - Verification: focused DeepResearch tests cover default arXiv bounded
    snapshot evidence, unauditable custom string retrieval, and custom HTTPS
    transport plus replayable redacted source payload artifacts.

- [x] Add paper-visible metric-specific archive overlays.
  - Paper evidence: multi-score optimization needs retained programs that
    excel under individual objectives, not only a scalar blended archive score.
  - Status: MAP-Elites state now records `metric_cell_archives`, per-declared
    objective metric descriptor-cell overlays with the best retained program
    by normalized metric value per cell. Metric-cell-only programs enter the
    retained pool used by metric/frontier sampling and are persisted/restored
    through archive snapshots.
  - Remaining paper gap: primary MAP-Elites cell replacement is still scalar,
    Pareto/frontier dominance does not replace the primary grid, and durable
    queryable multi-objective database resurfacing remains open.
  - Verification: focused MAP-Elites, island, database, and loop tests cover
    retention, snapshot/restore validation, retained-pool inclusion, and
    manifest validation.

- [x] Add paper-visible Strassen matrix publication bundle.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 and Appendix A
    publish exact matrix multiplication algorithms with per-seed best-rank
    hit-rate evidence and reproducible construction artifacts.
  - Status: `write_strassen_2x2_publication_bundle()` writes a checked
    `mm_2x2x2` Strassen bundle with canonical algorithm, exactness
    certificate, notebook, report, and artifact inventory files. The generated
    report is AlphaEvolve-comparable for this baseline target because it uses
    integer coefficients, verified symbolic exactness, algorithm/certificate/
    notebook artifacts, and exact rank-7 rows for every configured seed.
  - Remaining paper gap: this is one canonical baseline artifact, not a
    generated-publication path for discovered algorithms across the full
    54-target Appendix A suite.
  - Verification: focused matrix-result tests cover the generated publication
    report, artifact inventory, exactness certificate, and per-seed hit-rate
    consistency.

- [x] Add paper-visible systems artifact inventory verification.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3 reports systems
    discoveries with evidence beyond the optimization loop, including
    held-out workloads, reference-code checks, deployment measurements, and
    expert confirmation.
  - Status: `libreevolve.systems_result_artifact_inventory.v1` now verifies
    that systems result reports point to concrete evidence files under a safe
    artifact root. Metrics, heldout-report, reference-report, and summary
    artifacts are checked for safe paths, existence, SHA-256 hashes, byte
    counts, and aggregate inventory status.
  - Remaining paper gap: this is report-evidence verification only; actual
    systems fixtures still need to produce unseen-workload, randomized
    reference, deployment, and certification evidence files.
  - Verification: focused systems-result tests cover valid inventories and
    missing, mismatched, and unsafe artifact references.

- [x] Add paper-visible certification evidence inventory verification.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.3 distinguishes
    local optimization/evaluation from stronger confirmation such as
    deployment measurements, reference checks, exact certificates, and expert
    review.
  - Status: `libreevolve.paper_result_certification_artifact_inventory.v1`
    now verifies certification report evidence and artifact records against
    concrete files under a safe artifact root. Verifier output, review,
    deployment, simulator, reference, certificate, and reproduction records
    can be checked for safe paths, existence, SHA-256 hashes, byte counts, and
    aggregate inventory status.
  - Remaining paper gap: this is certification evidence-file verification
    only; actual benchmark workflows still need to produce independent
    verifier, deployment, simulator, reference, exact-certificate, and human
    review evidence.
  - Verification: focused certification tests cover valid inventories and
    missing, mismatched, and unsafe evidence/artifact references.

- [x] Add paper-visible ablation artifact inventory verification.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 8 reports ablation
    curves over equal compute-budget fractions, so paper-visible reports need
    concrete result artifacts for curve summaries, raw records, variant
    outputs, and plots.
  - Status: `libreevolve.alphaevolve_ablation_artifact_inventory.v1` now
    verifies declared ablation artifacts under a safe artifact root. Variant
    reports, curve summaries, raw records, and plot artifacts are checked for
    safe paths, existence, SHA-256 hashes, byte counts, and aggregate inventory
    status.
  - Remaining paper gap: this is ablation result-file verification only; no
    benchmark runner currently executes real Figure 8-style equal-budget
    ablation experiments or emits those validated reports for real targets.
  - Verification: focused ablation-result tests cover valid inventories and
    missing, mismatched, and unsafe artifact references.

- [x] Add paper-visible benchmark hardening artifact inventory verification.
  - Paper evidence: AlphaEvolve's reported benchmark discoveries depend on
    benchmark signals that resist shortcuts, so anti-gaming evidence should be
    concrete and auditable rather than only declared as hashes.
  - Status: `libreevolve.benchmark_hardening_artifact_inventory.v1` now
    verifies negative fixtures and hardening artifacts under a safe artifact
    root. Fixture and hardening records are checked for safe paths, existence,
    SHA-256 hashes, byte counts, and aggregate inventory status.
  - Remaining paper gap: this is anti-gaming evidence-file verification only;
    real benchmark runners still need to emit hardening reports from
    randomized/exhaustive operation, rank, construction, and systems fixtures.
  - Verification: focused benchmark-hardening tests cover valid inventories
    and missing, mismatched, and unsafe fixture/artifact references.

- [x] Add paper-visible provider cancellation artifact inventory verification.
  - Paper evidence: AlphaEvolve-style compute-budgeted experiments need
    provider timeout, cancellation, quarantine, and budget-stop evidence that
    can be audited from concrete artifacts.
  - Status: `libreevolve.provider_cancellation_artifact_inventory.v1` now
    verifies timeout logs, cancellation records, budget-stop records, and
    quarantine records under a safe artifact root. Artifacts are checked for
    safe paths, existence, SHA-256 hashes, byte counts, and aggregate inventory
    status.
  - Remaining paper gap: this is cancellation evidence-file verification only;
    live provider SDK hard cancellation, timeout-driven stop policy, and richer
    runtime cancellation artifacts remain unimplemented.
  - Verification: focused cancellation-policy tests cover valid inventories
    and missing, mismatched, and unsafe cancellation artifact references.

- [x] Add paper-visible retrieval payload sidecar inventory verification.
  - Paper evidence: retrieval-driven debugging/refinement treats external
    knowledge as part of the experimental input, so provider/source payload
    evidence should be auditable from concrete retained artifacts.
  - Status: `libreevolve.retrieval_payload_artifact_inventory.v1` now verifies
    DeepResearch event or plugin-metadata payload sidecar references under a
    safe artifact root. Sidecars are checked for safe paths, existence,
    SHA-256 hashes, byte counts, payload-artifact schema, selected sidecar
    metadata, and aggregate inventory status.
  - Remaining paper gap: this is retention-budgeted redacted sidecar
    verification only; unbounded raw provider/source payload retention,
    semantic source verification, learned/external retrieval ranking, and
    replayable redirect/TLS evidence remain unimplemented.
  - Verification: focused DeepResearch tests cover valid sidecar inventories
    and missing, mismatched, and unsafe sidecar references.

- [x] Add paper-visible LLM budget resume artifact inventory verification.
  - Paper evidence: AlphaEvolve-style compute budgets need persisted retry and
    provider-usage resume evidence that can be audited from concrete artifacts.
  - Status: `libreevolve.llm_budget_resume_artifact_inventory.v1` now verifies
    optional LLM budget `resume_state.artifacts[]` records under a safe
    artifact root. Resume evidence files are checked for safe paths,
    existence, SHA-256 hashes, byte counts, and aggregate inventory status.
  - Remaining paper gap: this is LLM budget resume evidence-file verification
    only; async controller restore, pending-work queues, provider-output
    replay, and replay-only budget-stop packaging remain unimplemented.
  - Verification: focused LLM budget-report tests cover valid resume
    inventories and missing, mismatched, and unsafe resume artifact references.

- [x] Add paper-visible controller event-stream inventory verification.
  - Paper evidence: AlphaEvolve-style autonomous controllers need resume and
    budget-event evidence that can be audited from concrete retained files.
  - Status: `libreevolve.controller_state_artifact_inventory.v1` now verifies
    the terminal synchronous controller event stream under a safe artifact
    root. The event stream is checked against the manifest artifact record and
    disk file for safe path handling, existence, SHA-256 hash, byte count,
    strict JSONL event count, last sequence/kind, and aggregate inventory
    status.
  - Remaining paper gap: this is terminal event-stream evidence-file
    verification only; async controller queues, pending work, in-flight
    provider outputs, and resumed-trace controller proof remain unimplemented.
  - Verification: focused loop tests cover valid event-stream inventories and
    mismatched, missing, and unsafe controller evidence references.

- [x] Add paper-visible validator execution-policy validation.
  - Paper evidence: AlphaEvolve-style system evaluations require clear,
    reproducible execution boundaries and honest statements about unsupported
    sandbox, filesystem, network, and quota enforcement.
  - Status: `validate_validator_execution_policy()` now validates
    `libreevolve.validator_execution_policy.v1` records for local subprocess
    execution, unsupported sandbox/container claims, filesystem-capability
    structure, network mode and denial scope, wall-clock-only limits,
    unsupported CPU/memory/GPU/disk/process-count quotas, startup-manifest
    scope, and the required per-evaluation boundary pointer.
  - Remaining paper gap: this is policy-record validation only; configurable
    container/security sandboxing, OS-enforced filesystem and network
    capabilities, resource quotas, and distributed evaluator worker state
    remain unimplemented.
  - Verification: focused validator-policy tests cover valid host/deny
    policies, JSON-file loading, sandbox/resource overclaims,
    network-boundary mismatches, and missing structured records.

- [x] Add paper-visible provider capability lookup validation.
  - Paper evidence: AlphaEvolve-style provider scheduling should distinguish
    local static backend validation from live provider capability discovery.
  - Status: `validate_provider_capability_lookup_policy()` now validates
    `libreevolve.provider_capability_lookup_policy.v1` records for static-only
    provider lookup boundaries, required local validation checks, unique
    backend indices, OpenAI API-mode policy linkage, offline compatibility, and
    explicit non-use of live model-registry, service/API-version, or
    account-availability discovery.
  - Remaining paper gap: this is static policy-record validation only; live
    provider model registry, service/API-version, account availability, remote
    provider defaults, live pricing, and provider-output replay remain
    unimplemented.
  - Verification: focused provider capability-policy tests cover valid static
    records, JSON-file loading, live-lookup overclaims, malformed records, and
    missing records.

- [x] Add paper-visible provider timeout cancellation records.
  - Paper evidence: long-running AlphaEvolve-style experiments should make LLM
    timeout handling auditable at the call-record level, including whether the
    controller retried, fell back, or only retained telemetry.
  - Status: failed LLM call rows from ensemble-level timeout deadlines now
    include replay-validated `libreevolve.provider_cancellation_record.v1`
    evidence with role/backend/call-id linkage, timeout seconds,
    retry/fallback/telemetry budget action, and the explicit hard-cancel
    unsupported boundary.
  - Remaining paper gap: live provider SDK hard cancellation and
    timeout-driven stop enforcement remain unimplemented.
  - Verification: focused ensemble tests cover valid timeout cancellation
    records and replay rejection for malformed cancellation evidence.

- [x] Add paper-visible controller budget replay validation for LLM usage.
  - Paper evidence: restored AlphaEvolve-style compute budgets should prove
    provider-attempt, token, configured-cost, and latency consumption from
    event evidence rather than trusting a detached snapshot.
  - Status: `validate_controller_budget_replay_state()` now replays controller
    budget events into `RunBudget` and rejects consumed-counter or stop-reason
    drift against the persisted snapshot, with the loop restore path using the
    shared budget contract.
  - Remaining paper gap: async worker/pending-work state and provider-output
    replay are still outside the restored controller budget proof.
  - Verification: focused budget tests cover valid LLM usage replay and
    malformed snapshot drift.

- [x] Add paper-visible declared-metric targeted resurfacing.
  - Paper evidence: AlphaEvolve Section 2.4 uses multiple user-provided scores
    and can draw inspirations from programs that are strong under different
    criteria.
  - Status: `ProgramDatabase.resurface_candidates(target_metric=...)` now
    exposes run-local declared-metric queries over objective metric archives,
    returning defensive ranked program snapshots and rejecting undeclared
    metric targets.
  - Remaining paper gap: primary archive replacement is still scalar, and
    durable cross-run multi-objective database resurfacing remains absent.
  - Verification: focused database tests cover metric-targeted resurfacing and
    invalid target rejection.

- [x] Add paper-visible programmatic representation-boundary evidence.
  - Paper evidence: AlphaEvolve Related Work contrasts AI-Co-Scientist's
    natural-language hypotheses and evaluation criteria with AlphaEvolve's code
    candidates and programmatic evaluation functions.
  - Status: paper-facing docs now describe
    `runtime.history.programmatic_representation_boundary_report`, which labels
    generated candidates as executable code workspaces, proposal metadata as
    natural-language context, and declared evaluator metrics plus deterministic
    evaluator validity as programmatic criteria.
  - Remaining paper gap: hallucination-resistance claims, long-horizon
    evolution claims, and a full natural-language hypothesis-stage bridge
    remain unimplemented.
  - Verification: focused loop tests cover the report, validator, proposal
    field counts, and unready claim boundaries.

- [x] Add paper-visible mutation-operator boundary evidence.
  - Paper evidence: AlphaEvolve uses structured edit payloads but contrasts
    LLM-guided mutation with systems that require fixed handwritten mutation or
    crossover operator sets.
  - Status: paper-facing docs now cite
    `runtime.history.mutation_operator_boundary_report`, which records the
    configured run-wide mutation mode, observed fixed parser payload surfaces,
    sample generated-candidate mutation records, and the explicit unready
    boundary for LLM-constructed operator families and adaptive selection.
  - Remaining paper gap: proposal-level operator-family provenance,
    construction/selection evidence, operator scoring, and benchmark telemetry
    remain unimplemented.
  - Verification: focused loop tests cover the report, validator, payload
    surface counts, and unready claim boundaries.

- [x] Add paper-visible exact proposal-diversity evidence.
  - Paper evidence: AlphaEvolve Section 2.3 says SOTA LLMs propose new,
    diverse ways to improve prior solutions.
  - Status: paper-facing docs now cite
    `runtime.history.proposal_diversity_report`, which records exact proposal
    signature and idea-hash uniqueness/duplicate counts by generation and
    proposal batch with bounded sample records.
  - Remaining paper gap: semantic proposal diversity, near-duplicate
    detection, idea-family novelty, model-quality attribution, and benchmark
    linkage remain unimplemented.
  - Verification: focused loop tests cover the report, validator, duplicate
    idea counts, and unready claim boundaries.

- [x] Add paper-visible initial-pool divergence evidence.
  - Paper evidence: AlphaEvolve's introduction says feedback-driven evolution
    can discover candidates substantially different from the initial candidate
    pool in syntax and function.
  - Status: paper-facing docs now cite
    `runtime.history.initial_pool_divergence_report`, which compares generated
    candidates against generation-0 seed programs with canonical workspace
    hashes, bounded primary-file text distance, changed-component summaries,
    and numeric metric L1 distance over shared metric names.
  - Remaining paper gap: task-specific functional-distance artifacts,
    behavior/output-distance metrics, thresholds for substantially different
    claims, and benchmark-level discovery-distance telemetry remain
    unimplemented.
  - Verification: focused loop tests cover the report, validator,
    seed/candidate counts, distance records, and unready claim boundaries.

- [x] Add paper-visible run-local duplicate-work cache evidence.
  - Paper evidence: AlphaEvolve Section 2.5 frames the generated-program
    database as fixed-budget memory over prior evaluated solutions.
  - Status: paper-facing docs now cite
    `runtime.history.duplicate_work_policy_report` for run-local exact
    workspace evaluator-result reuse, canonical workspace plus
    evaluator-contract cache-key scope, cache-hit metadata, and replayable
    `candidate_evaluation_cache_hit` budget events.
  - Remaining paper gap: durable cross-run cache lookup, resume-spanning cache
    replay, stochastic re-evaluation semantics, semantic near-duplicate
    handling, and output/source-aware duplicate indexes remain unimplemented.
  - Verification: focused budget and loop tests cover cache-hit reporting,
    controller-event validation, and evaluator-call budget savings.

- [x] Add paper-visible bounded proposal-score evidence.
  - Paper evidence: AlphaEvolve Sections 2.2 and 2.4 frame useful prior ideas
    and hypotheses as evolutionary evidence for future search.
  - Status: paper-facing docs now cite
    `runtime.history.proposal_score_report`, which records current-run
    proposal scores from candidate outcome quality and exact proposal-signature
    first-occurrence novelty.
  - Remaining paper gap: semantic/cross-run proposal-hypothesis retrieval,
    calibrated proposal-quality models, persisted proposal-index tables, and
    policy boundaries for score-driven prompting/archive resurfacing remain
    unimplemented.
  - Verification: focused loop tests cover the report, validator, accepted/
    rejected proposal scores, and unready semantic-index boundaries.

- [x] Add paper-visible observed redirect evidence.
  - Paper evidence: AlphaEvolve Introduction and Section 2.4 describe
    backtracking on unpromising hypotheses and cascade pruning before larger
    budgets are spent.
  - Status: paper-facing docs now cite
    `runtime.history.controller_backtracking_report`, which records current-run
    branch state transitions and observed redirects from abandoned-looking
    branches to a later fallback parent or alternative branch.
  - Remaining paper gap: explicit controller-owned suppression/retry policy,
    fallback-target selection, causal resumed-search proof, and cross-run
    hypothesis branch tables remain unimplemented.
  - Verification: focused loop tests cover the report, validator, observed
    redirect records, and unready causal-proof boundaries.

- [x] Add paper-visible prompt-current binding evidence.
  - Paper evidence: AlphaEvolve Figure 3(b,c) and Section 2.3 define
    SEARCH/REPLACE payloads as edits to the current program shown in the
    prompt.
  - Status: paper-facing docs now cite
    `runtime.history.prompt_current_binding_report`, which records current-run
    prompt/current-program hashes, parent/candidate workspace hashes, LLM call
    ids, mutation payload hashes, diff SEARCH match counts/spans,
    evolve-block inner span mapping, workspace file-section target/full-file
    spans, full-mode target spans, prompt-history row joins, evaluator status,
    and archive admission.
  - Remaining paper gap: none for this bounded prompt-current evidence item.
  - Verification: focused loop tests cover diff and full-mode report records
    plus validator success.

- [x] Add paper-visible built-in prompt example-copy diagnostics.
  - Paper evidence: AlphaEvolve Figure 3(b,c) uses concrete prompt examples,
    but proposals should edit the sampled current program rather than copy
    illustrative prompt-only fragments.
  - Status: paper-facing docs now cite
    `runtime.history.prompt_example_copy_report`, which inventories built-in
    mutation-format example sentinels and records exact generated-payload
    copies with candidate status/admission metadata.
  - Remaining paper gap: configurable rejection, semantic/renamed copy
    detection, custom prompt-template inventories, and per-file-section
    normalized scanning remain unimplemented.
  - Verification: focused loop tests cover copied sentinel detection,
    disabled-example policy, and validator success.
- [x] Validate paper-index implementation-status semantics, not only ids.
  - Paper evidence: `papers/README.md` explicitly defines implementation
    status cells as the paper-facing status source for background,
    primary-specification, partial, limited, static-guidance, and unsupported
    rows.
  - Status: paper-manifest validation now goes beyond manifest-id coverage:
    `_read_status_table_ids()` and `_validate_status_evidence_links()` enforce
    table shape, role/status taxonomy, support-class boundaries, completed and
    active evidence links, source-specific completed evidence, and status-cell
    local artifact paths that must reappear in the row's linked TODO evidence.
    README, ROADMAP, and `papers/README.md` describe that this proves
    structural traceability and local-artifact claim linkage, not arbitrary
    natural-language semantic proof.
  - Verification: `py -3.12 -m pytest tests/test_paper_manifest.py -q`
    reports 123 passed.
- [x] Preserve paper-artifact role attribution separately from artifact
      availability.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` page 23 names the figure
    creators and accompanying Google Colab assemblers, while other paper
    surfaces require rendered figures, notebook URLs, digests, and claim maps
    before artifact availability can be claimed.
  - Status: `libreevolve.alphaevolve_paper_artifact_linkage.v1` now validates
    that both `paper_figures` and `accompanying_google_colab` are currently
    `not_yet_linked` and records the fields required for future rendered
    figure or companion-notebook artifacts. This keeps the existing attribution
    record from being treated as byte-level artifact evidence.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.
- [x] Track local Appendix A matrix resource-frontier absence separately from
      paper-source OOM evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A records the
    paper-side larger-target OOM boundary, not local LibreEvolve execution.
  - Status: `libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1`
    now records that no local larger-target matrix scaling attempts, measured
    memory profiles, OOM diagnostics, reduced-seed tradeoffs, or
    attempted-versus-excluded target policies exist yet. It also validates the
    fields required before such local frontier evidence can be claimed.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix near-integrality runtime-emission absence separately from
      declared evidence validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 describes the
    near-integral matrix prompt and integer/half-integer rounding workflow;
    paper-visible local claims need separate evidence that the local runner
    emitted those prompt/evaluator records.
  - Status: `libreevolve.matrix_near_integrality_runtime_boundary.v1` now
    records the current `not_emitted_by_local_runner` boundary and validates
    required future emitted-record fields for run/candidate ids, prompt hashes,
    raw and rounded coefficients, exactness-certificate links,
    matrix-result refs, artifact paths, and artifact hashes. The paper-manifest
    gate validates this boundary with the Appendix A matrix checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix scalar-field runtime-emission absence separately from
      declared evidence validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 and Table 2
    distinguish complex-valued matrix multiplication, exact real/complex
    applicability, characteristic-0 claims, and finite-field-only caveats.
  - Status: `libreevolve.matrix_scalar_field_runtime_boundary.v1` now records
    the current `not_emitted_by_local_runner` boundary and validates required
    future emitted-record fields for scalar field, characteristic,
    applicability, coefficient representation, algorithm refs, certificate
    refs, matrix-result refs, artifact paths, and artifact hashes. The
    paper-manifest gate validates this boundary with the Appendix A matrix
    checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix tensor-rank runtime-emission absence separately from
      declared evidence validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 frames matrix
    results as low-rank tensor decompositions and footnote 3 distinguishes
    non-recursive multiplication algorithms from matrix tensor decompositions.
  - Status: `libreevolve.matrix_tensor_rank_runtime_boundary.v1` now records
    the current `not_emitted_by_local_runner` boundary and validates required
    future emitted-record fields for algorithm kind, rank, recursive
    applicability, certificate scope, tensor-identity status, target-tensor
    refs, exactness-certificate refs, matrix-result refs, artifact paths, and
    artifact hashes. The paper-manifest gate validates this boundary with the
    Appendix A matrix checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix sweep-space runtime-emission absence separately from
      declared evidence validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figures 9a-9c show the
    matrix program evolving a `sweep()` function with user-provided
    `hyper.uniform(...)` ranges and sampled sweep outcomes.
  - Status: `libreevolve.matrix_sweep_space_runtime_boundary.v1` now records
    the current `not_emitted_by_local_runner` boundary and validates required
    future emitted-record fields for search-program refs, sweep function
    identity, hyper-library and hyperparameter declarations, sampled
    configurations, winning configuration, certificate/decomposition refs,
    matrix-result refs, artifact paths, and artifact hashes. The
    paper-manifest gate validates this boundary with the Appendix A matrix
    checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix headline historicity runtime-emission absence separately
      from declared evidence validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` abstract and Section 3.1
    state the 4x4 complex rank-48 headline, including the 56-year
    characteristic-zero first-below-49 framing and prior Strassen/Fawzi
    comparisons.
  - Status: `libreevolve.matrix_headline_historicity_runtime_boundary.v1` now
    records the current `not_emitted_by_local_runner` boundary and validates
    required future emitted-record fields for headline target/rank/field
    values, source refs, prior comparisons, evidence links, matrix-result refs,
    artifact paths, and artifact hashes. The paper-manifest gate validates
    this boundary with the Appendix A matrix checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix-rank table artifact-emission absence separately from
      declared table exhibit validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 and Appendix A
    Table 3 are paper-table exhibits with rendered rows, source captions,
    rank values, outcome coloring, complex-row caveats, Colab links, and the
    `<4, 5, 6>` concurrent-work note.
  - Status: `libreevolve.alphaevolve_matrix_rank_table_artifact_boundary.v1`
    now records the current `not_emitted_by_local_report_export` boundary and
    validates required future emitted-artifact fields for table identity,
    source locations, rendered/OCR/source files, artifact paths/hashes, and
    nested matrix-rank table exhibit evidence. The paper-manifest gate
    validates this boundary with the Appendix A matrix checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix subset-scope artifact-emission absence separately from
      declared subset validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 scopes the
    all-matched-or-surpassed statement to `m, n, p <= 5`, while Appendix A
    Table 3 is the full 54-target matrix table with two fell-behind rows.
  - Status: `libreevolve.alphaevolve_matrix_subset_scope_artifact_boundary.v1`
    now records the current `not_emitted_by_local_report_export` boundary and
    validates required future emitted-artifact fields for subset identity,
    inclusion predicates, source linkage, row/outcome counts, fell-behind and
    out-of-scope ids, nested subset-scope evidence, artifact paths, and hashes.
    The paper-manifest gate validates this boundary with the Appendix A matrix
    checks.
  - Later status: `papers/appendix_a_matrix_subset_scope_artifacts.json` now
    emits the subset-scope sidecar; automatic rendered table/report
    propagation remains open.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track Appendix A matrix row-note artifact-emission absence separately
      from declared row-note validation.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A Table 3 includes
    the `mm_4x5x6` concurrent-work note that reference `[49]` also found a
    rank-90 algorithm for `<4, 5, 6>`.
  - Status: `libreevolve.alphaevolve_appendix_a_matrix_row_note_artifact_boundary.v1`
    now records the current `not_emitted_by_local_report_export` boundary and
    validates required future emitted-artifact fields for note identity,
    target/rank/reference values, source text, caveat flags, nested row-note
    evidence, artifact paths, and hashes. The paper-manifest gate validates
    this boundary with the Appendix A matrix checks.
  - Later status: `papers/appendix_a_matrix_row_note_artifacts.json` now emits
    the row-note caveat sidecar; automatic rendered table/report propagation
    remains open.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track Appendix A matrix best-known-rank citation absence separately from
      registry rank values.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Table 2 and Appendix A
    Table 3 include best-known-rank comparisons with cited prior-work
    references.
  - Status: `libreevolve.alphaevolve_appendix_a_matrix_baseline_citation_boundary.v1`
    now records the current `not_recorded_locally` boundary and validates
    required future per-target citation fields for reference id, source
    table/page, source artifact path/hash, applicability caveats,
    field/characteristic scope, and report-visible baseline-source refs. The
    paper-manifest gate validates this boundary with the Appendix A matrix
    checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix cascade-run runtime absence separately from declared
      per-seed result rows.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 reports matrix
    experiments run over multiple random seeds using the evaluation cascade,
    with best rank and hit-fraction rows.
  - Status: `libreevolve.matrix_cascade_run_runtime_boundary.v1` now records
    the current `not_emitted_by_local_runner` boundary and validates required
    future emitted fields for run/target/seed ids, cascade ids and versions,
    stage traces, final rank, candidate/result refs, artifact paths, and
    hashes. The paper-manifest gate validates this boundary with the Appendix
    A matrix checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track matrix baseline-component runtime absence separately from final
      result reports.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 starts matrix
    decomposition search from a standard gradient-based algorithm with an
    initializer, reconstruction loss function, and Adam optimizer.
  - Status: `libreevolve.matrix_baseline_component_runtime_boundary.v1` now
    records the current `not_emitted_by_local_runner` boundary and validates
    required future emitted fields for baseline components, optimizer config,
    generation-0 metrics, mutation lineage, result refs, artifact paths, and
    hashes. The paper-manifest gate validates this boundary with the Appendix
    A matrix checks.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Preserve the Strassen baseline bundle as pinned paper evidence.
  - Paper evidence: AlphaEvolve's matrix section and Appendix A publish exact
    matrix-multiplication algorithms and companion artifacts as auditable
    result evidence; local baseline helpers need durable artifact files to be
    paper-index evidence.
  - Status: the `mm_2x2x2` Strassen baseline bundle is pinned under
    `libreevolve/problems/benchmarks/artifacts/strassen_2x2_publication_bundle/`
    with algorithm, certificate, notebook, report, and inventory files.
    `validate_strassen_2x2_publication_bundle()` and the paper-manifest gate
    validate hashes and regeneration parity while keeping scope limited to the
    one known baseline.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track Appendix A Figure 9 artifact-emission absence separately from
      declared panel metadata.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A Figures 9a-9c
    present the magnified source/diff panels for Figure 4's matrix program.
  - Status: `libreevolve.alphaevolve_figure9_matrix_diff_artifact_boundary.v1`
    now records the current `not_emitted_by_local_report_export` boundary and
    validates required future emitted-artifact fields for panel ids/order/pages,
    line spans, source-diff excerpts, rendered images, OCR text, aggregate
    panel-set artifacts, artifact paths/hashes, and nested Figure 9 exhibit
    metadata. The paper-manifest gate validates this boundary.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track Figure 4 artifact and 15-mutation lineage absence separately from
      declared exhibit metadata.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Figure 4 is the main-text
    matrix discovery exhibit and its caption says the example required 15
    mutations.
  - Status: `libreevolve.alphaevolve_figure4_matrix_discovery_artifact_boundary.v1`
    now records the current `not_emitted_by_local_report_export` boundary and
    validates required future fields for rendered/source artifacts, accepted
    mutation lineage, artifact paths/hashes, and nested Figure 4 exhibit
    metadata. The paper-manifest gate validates this boundary.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track Appendix A excluded-target curation absence separately from
      reported-suite curation metadata.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Appendix A gives rough
    matrix target-suite selection wording and axis-permutation symmetry, but
    not an exhaustive local justification ledger for excluded non-equivalent
    targets.
  - Status: `libreevolve.alphaevolve_appendix_a_matrix_excluded_target_curation_boundary.v1`
    now records the current `not_recorded_locally` boundary and validates
    required future fields for excluded target ids, dimensions, exclusion
    class/reason, source basis, rough-rule and `p`-cutoff relations,
    symmetry-equivalence status, local attempt/resource-frontier refs,
    artifact paths, and hashes. The paper-manifest gate validates this
    boundary.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track Appendix A suite-wide matrix publication artifact absence
      separately from the pinned Strassen baseline.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 3.1 and Appendix A
    report exact matrix decompositions, certificates, notebooks, and per-seed
    hit-rate evidence across the matrix target suite.
  - Status: `libreevolve.matrix_suite_publication_artifact_boundary.v1` now
    records the current `not_generated_locally` boundary and validates
    required future fields for one generated artifact record per registered
    Appendix A target: target tensor, algorithm, coefficient data, exactness
    certificate, notebook, per-seed report, embedded matrix-result report,
    artifact inventory, publication-bundle refs, artifact paths, and hashes.
    The paper-manifest gate validates this boundary.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Populate paper author-metadata evidence for equal contributors and
      correspondence roles.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` page 1 defines the
    equal-contribution marker, page 22 names the equal-contribution group and
    begins the Contributions section, and page 23 records manuscript writers,
    paper-input contributors, and corresponding authors.
  - Status: `libreevolve/problems/examples/matrix_multiplication/paper_authors.yaml`
    now provides reviewed representative author-metadata records with source
    page/section locators, title-page marker linkage, contact/privacy policy,
    and review status. `papers/README.md` now states that this example's
    zero-generation manifest is claim-ready for paper-author metadata parity.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Populate AlphaEvolve title-page affiliation and footnote evidence.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` page 1 lists the
    source-paper affiliation line, the affiliation footnote, the
    equal-contribution footnote, and the source-paper rights line.
  - Status: `libreevolve/problems/examples/matrix_multiplication/title_page.yaml`
    now provides reviewed title-page records with source page locators,
    footnote markers, author-marker mapping, source-rights linkage,
    privacy/redaction policy, and review status. `papers/README.md` now states
    that this example's zero-generation manifest is claim-ready for
    title-page affiliation and footnote parity.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Populate core AlphaEvolve system-development contribution provenance.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` pages 22-23 attribute
    initial design, project vision/scoping, first-benchmark iteration, final
    system development, infrastructure maintenance, code review, team
    coordination, and supervision roles.
  - Status: `libreevolve/problems/examples/matrix_multiplication/system_contributions.yaml`
    now provides reviewed representative system-contribution records with
    source page/section locators, artifact/module labels, review scopes,
    privacy/retention policy, and review status. `papers/README.md` now states
    that this example's zero-generation manifest is claim-ready for
    system-development contribution parity.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Populate acknowledgement-role evidence for review, support, and
      practical application management advice.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` pages 21-22 acknowledge
    white-paper review, early exploration, support/advice,
    practical-application management advice, application review, and
    application-specific advice.
  - Status: `libreevolve/problems/examples/matrix_multiplication/acknowledgements.yaml`
    now provides reviewed representative acknowledgement records with source
    page/section locators, scope labels, privacy/redaction policy, and review
    status. `papers/README.md` now states that this example's zero-generation
    manifest is claim-ready for acknowledgement-role parity.
  - Verification: `py -3.12 -m libreevolve.tools.paper_manifest` passes.

- [x] Track prompt-visible prior-score provenance for rendered evaluation
      results.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 says rendered
    evaluation results contain the program, execution result, and scores
    assigned by `evaluate`; Figure 3(c) shows previously discovered programs
    with named metric scores and an `average_score` before program text.
  - Status: paper-facing docs now describe
    `runtime.history.prompt_prior_score_provenance_report` and
    `prompt_prior_score_table.jsonl` as the local evidence surface for
    prompt-visible parent/inspiration score rows, score display fields,
    execution-output and stage-summary IO attribution, evaluator/history joins,
    explicit `average_score` display/formula policy, and feedback-section
    truncation policy.
  - Verification: prompt prior-score runtime tests validate the report schema,
    score display, `average_score`, execution-output, stage-summary IO, and
    feedback-section policy records.

- [x] Track explicit-context source roles for prompt sampling.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.2 lists explicit
    prompt context as fixed human-written instructions, equations, code
    snippets, and relevant literature such as PDF files.
  - Status: paper-facing docs now distinguish typed AlphaEvolve-style explicit
    context from generic local context-file ingestion. `context.yaml`
    `source_roles` metadata records source role, task/topic linkage, source
    location, and manifest-backed role provenance; startup manifests expose
    `runtime.history.explicit_context_source_role_report` with prompt
    inclusion/omission decisions, content hash scope, redaction policy,
    classified/unclassified counts, and claim-readiness checks.
  - Verification: loader and runtime report tests validate role parsing,
    invalid-role rejection, runtime report schema, role/location records, and
    validator rejection of unsupported role names.

- [x] Extend single-run evaluator-metric tables into cross-run benchmark
      reports.
  - Paper: `2506.13131__AlphaEvolve.pdf`, Section 2.1 and Figure 3.
  - Status: paper-facing docs now describe `paper_metric_cross_run_report()`
    with schema `libreevolve.paper_metric_cross_run_report.v1`. The report
    consumes multiple manifests, validates each run's evaluator metric contract
    and paper metric table export, aggregates paper metric names and per-run
    table hashes, and records metric-contract, table-column, and display-policy
    drift before treating compared runs as AlphaEvolve-comparable table
    evidence.
  - Verification: runtime tests generate two real zero-generation manifests,
    validate a claim-ready no-drift cross-run report, and verify drift
    detection when a run's metric-name set changes.

- [x] Extend Figure 3 evolve-block marker spelling source variants with source
      artifacts and final classification.
  - Paper evidence: `2506.13131__AlphaEvolve.pdf` Section 2.1 names
    `# EVOLVE-BLOCK-START` / `# EVOLVE-BLOCK-END`; local PDF text extraction
    from Figure 3(a) shows both a space variant and the canonical spelling.
  - Status: paper-facing runtime reports now attach hashed source artifacts for
    the AlphaEvolve PDF page text and Figure 3 marker-line text when the local
    PDF cache is available. The marker report links each source-location record
    to those artifacts and records a final local classification of the space
    variant as PDF text-extraction uncertainty rather than supported parser
    syntax.
  - Verification: marker provenance tests validate artifact attachment,
    artifact paths/hashes, marker-presence metadata, final classification, and
    overclaim rejection when parser compatibility is toggled.
