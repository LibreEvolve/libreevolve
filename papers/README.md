# Local Paper Cache

This directory is the paper-cache index. On the working machine it contains 53
locally cached PDFs plus download manifests. PDFs are intentionally gitignored
by default; the retained AlphaEvolve PDF is the explicit hash-validated source
artifact exception. The committed repository tracks this README, the CSV/JSON
manifests, sidecars, and that retained source artifact. The manifests record
each cached PDF's byte count and SHA-256 hash.
Manifest `title` values are inventory/display slugs derived from the local cache
name, not authoritative bibliographic titles; use the implementation-status
table below for paper-facing titles and roles.
The cache is used as human/project research context for LibreEvolve docs and
implementation audits; it is not automatically loaded as runtime prompt context,
and it is not a claim that every paper is fully implemented. On a fresh checkout,
rehydrate the ignored local PDF cache with
`py -3.12 -m libreevolve.tools.paper_manifest --rehydrate`; the command streams
downloads from the manifest URLs, verifies byte counts and SHA-256 hashes before
installing each file, and reports network or integrity failures explicitly.
The manifest hashes are canonical lowercase 64-hex SHA-256 digests. Validate
the committed manifest/index with `py -3.12 -m libreevolve.tools.paper_manifest`;
add `--require-local-pdfs` on machines with the ignored PDF cache to check file
presence, regular-file shape, `%PDF-` header shape, lightweight `pypdf` page
readability, byte counts, and streaming digests. Local PDF stat/read/parse
failures are returned as row-attributed, secret-redacted validation issues.
Manifest, README count, and status-table read diagnostics use
repository-relative labels plus secret-redacted exception text in both text and JSON
reports. The
validator report includes per-paper availability records so historical `ok` /
`message` download metadata is separate from current local presence and
Git-tracked status. Manifest validation now requires arXiv-style ids or
lowercase foundational-paper slugs, safe ASCII `papers/<name>.pdf` paths that
avoid Windows reserved/hidden/control-character names, unique normalized PDF
targets and digests, HTTPS URLs from the known paper source hosts, synchronized
README prose and badge counts, display-safe bounded inventory title slugs, bounded
secret-redacted download messages, a closed manifest field set,
duplicate-key-free JSON rows, and the canonical CSV header order. With
`--require-local-pdfs`, validation also requires listed PDFs to be regular
`%PDF-` files with at least one readable `pypdf` page, streams digest
verification instead of reading whole files into memory, fails historical
failed-download rows, reports unmanifested local PDFs, and treats Git-tracked
cache PDFs as repository-boundary violations unless they match the retained
AlphaEvolve source-artifact path and SHA-256 allowlist. The
implementation-status table IDs below are reconciled against the committed
manifest IDs by the same validator. The validator treats the implementation-
status table as a structured public claim surface: it requires the stable
four-column header, exact four-cell rows, non-empty display-safe title, role,
and status cells, the declared role taxonomy, allowed status class prefixes,
compatible role/status pairs, and local artifact paths named in status cells
against the row's linked active or completed TODO evidence. The TODO coverage
cross-reference table is validated separately for manifest-id row coverage,
exact row shape, active TODO ledger links, and completed-ledger links under
`docs/todo/Completed/` that contain completed checklist evidence. These checks
keep paper-index structure, backlog traceability, and local-artifact claim
linkage honest, but they do not yet prove arbitrary natural-language semantics
for every long status phrase or benchmark qualifier.
Symlink or Windows reparse-point backed PDF entries are rejected before
byte/hash validation.
The same validation command checks
`libreevolve/problems/benchmarks/alphaevolve_appendix_a_matrix.json`, which
records the 54 AlphaEvolve Appendix A Table 3 matrix target identities,
dimensions, best-known ranks, AlphaEvolve ranks, outcome categories, and
exact-algorithm flags. That registry is target/outcome coverage, not
construction or Colab evidence. The companion
`libreevolve.alphaevolve_appendix_a_matrix_curation.v1` record preserves the
paper's rough size-selection wording, sorted representative policy under
axis-permutation symmetries, included-target rationales, and the derived
omitted-equivalent target ledger; it does not provide target tensor,
decomposition, or Colab evidence. The companion
`libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1` record
preserves the paper-only Appendix A boundary for sizes beyond `<5,5,5>`, 1000
random seeds, single-GPU evaluators, frequent OOM, and further-optimization
need; it does not claim local OOM run artifacts. The companion
`libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1` record
validates that local larger-target attempts are currently absent and records
the measured-memory, OOM-diagnostic, reduced-seed, artifact, and
attempted-versus-excluded target fields required before local frontier claims.
The validation command also checks
`libreevolve/problems/benchmarks/alphaevolve_appendix_b.json`, which records a
coverage decision for each AlphaEvolve Appendix B constructive-math family. The
registry currently marks only the unit-square circle-packing fixture as
`implemented_smoke`; all other Appendix B families are explicit planned entries
with objective direction, target/baseline status, construction/certificate
artifact shape, certification need, rationale, and AlphaEvolve citation
metadata. The top-level `result_row_boundary` now records that normalized
B.1-B.13 result-row evidence remains absent: it enumerates `19` expected
result ids, including the B.4 revision row, and still requires metric
definitions, parameter tuples, prior-value attribution, source locations,
construction payload hashes, verifier artifacts, result-version status, and
recomputed values, all `not_recorded_locally`. For B.1-B.3 autocorrelation, the
registry now stores paper-facing
labels for `B.1. First autocorrelation inequality (C1)`,
`B.2. Second autocorrelation inequality (C2)`, and
`B.3. Third autocorrelation inequality (C3)` separately from internal
`autocorrelation_bounds_k*` ids. It also validates B.1-B.3 step-function
summary metadata: interval counts `600`, `50`, and `400`, the common
`[-1/4, 1/4]` domain, non-negative versus signed function policy, proof
direction, previous bound/source, and reported bound. Each B.1-B.3 row now
also has a validated `step_function_payload_boundary` that keeps the required
payload hash, domain/spacing/sign-policy certificates, verifier artifact, and
recomputed-bound fields `not_recorded_locally`. For B.8 max/min-distance
point sets, the registry now preserves the paper's squared-ratio convention:
16 points in 2D report squared value `12.889266112` with derived ratio
`3.590162407468`, and 14 points in 3D report squared value `4.165849767` with
derived ratio `2.041041343775`; both are compared against prior squared bounds
from `[29]`. Its `witness_certificate_boundary` records the future coordinate
artifact, point-count/dimension certificate, pairwise distance matrix,
min/max pair-witness certificate, squared-ratio recomputation, and Figure 12
panel artifact fields required before local witness proof can be claimed,
preserves the 16-point/2D and 14-point/3D missing-witness rows, and keeps both
B.8 witnesses and panel artifacts `not_recorded_locally`.
For B.5 Erdős minimum overlap, the registry now records the source
paired-function formulation, zero-extension convention, shift-supremum
objective, known lower/upper bounds, `[40]` equivalence, and mapping to the
normalized `[0,2]` step-function formulation. Its
`step_function_result_boundary` records the paper's Figure 10 result id,
`C5 <= 0.380924` reported upper bound, prior `0.379005 <= C5 <= 0.380927`
bounds, source figure, normalized-domain constraint, shift-objective
expression, and the step-function payload and certificate fields required
before local reproduction can be claimed. It keeps the original-formulation
mapping certificate, `[40]` equivalence-reference artifact, shift-domain
certificate, payload, value-range certificate, integral-normalization
certificate, shift-objective certificate, recomputed upper bound, and Figure
10 panel artifact `not_recorded_locally`.
For B.6 sums and differences of finite sets, the registry now records the
source `C6` theorem statement, sumset/difference-set definitions, `<<`/`>>`
notation, known `1.14465 <= C6 <= 4/3` bounds, Gyarmati admissibility
condition, and lower-bound formula. Its `finite_set_witness_boundary` records
the paper's two witness summaries, `U1` of size `2003` with
`1.1479 <= C6` and `U2` of size `54265` with `1.1584 <= C6`, plus the
integer-set payload, contains-zero, non-negative, admissibility,
sumset-cardinality, difference-set-cardinality, max-element,
lower-bound-formula substitution, and recomputation fields required before
local reproduction can be claimed, while the finite-set construction payloads,
set-algebra certificates, and formula-substitution artifacts remain absent.
For B.7 regular-hexagon packing, the registry now records the
unit-regular-hexagon objective, Figure 11 linkage, prior `[29]` values, and
two paper-reported improvements: `n = 11` from outer side length `3.943` to
`3.931` in the left panel, and `n = 12` from `4.0` to `3.942` in the right
panel. Its `packing_result_boundary` records the placement payload,
pose/orientation schema, regular-hexagon geometry-certificate, containment,
non-overlap, side-length recomputation, and Figure 11 panel artifact fields
required before local reproduction can be claimed, while those payloads and
artifacts remain absent.
For B.9-B.10 Heilbronn variants, the registry now records three result
boundaries: `n = 11` points in a unit-area triangle with minimum formed
triangle area `> 0.0365` versus prior `0.036`, `n = 13` points in a
unit-area convex region improving `0.0306` to `0.0309`, and `n = 14` points
in a unit-area convex region improving `0.0277` to `0.0278`. The
`heilbronn_result_boundary` entries preserve Figure 13 left/middle/right
links and the point-coordinate, domain, unit-area, convexity, all-triples area,
triple-count enumeration, minimum-witness-triangle, reported-value comparison,
recomputed-minimum-area, and Figure 13 panel artifact path/hash fields required
before local reproduction can be claimed, with panel artifacts explicitly
`not_recorded_locally`, while the coordinate/domain payloads, triple
enumeration, area certificates, and panel artifacts remain absent.
For B.11 kissing number in dimension 11, the registry now records the prior
lower bound `592`, reported lower bound `593`, 593 nonzero integral
11-dimensional vector witness condition, max-norm versus minimum-pairwise
distance requirement, and Lemma 1 transformation to sphere centers
`{2 x / ||x||}`. Its `kissing_result_boundary` records the vector payload and
exact certificate fields required before local reproduction can be claimed,
including count/dimension, norm/distance matrix, separate max-norm,
minimum-pairwise-distance, strict inequality, transformed unit-sphere, and
kissing-angle certificate statuses, while the vector payload and those exact
proof artifacts remain absent.
For B.12-B.13 circle and rectangle packing, the registry now records three
sum-of-radii boundaries: `n = 26` unit-square circles improving `2.634` to
`2.635`, `n = 32` unit-square circles improving `2.936` to `2.937`, and
`n = 21` perimeter-4 rectangle circles improving `2.364` to `2.3658`. Figure
14 maps these to left, middle, and right panels; the B.13 row also preserves
the caption display `sum_of_radii >= 2.365` separately from the text value
`2.3658`. The unit-square boundary keeps the checked-in 26-circle fixture
scoped as smoke-only and now preserves Figure 5's `2.6340 -> 2.6358` display
as a separate precision boundary from the Appendix B.12/Figure 14 `2.634` to
`2.635` strings, while the AlphaEvolve container artifacts, placement
payloads, Figure 14 panel artifacts, exact certificates, payload-schema
validation certificates, positive-radius certificates, sum-of-radii formula
certificates, source locators, value-extraction certificates,
value-reconciliation certificate, canonicalization policy, recomputed sum, and
companion Colab link remain absent.
Appendix B says reported construction data and verification code
appear in an accompanying Google Colab; this registry is not that
Colab-equivalent evidence surface and does not yet store construction-data
exports or runnable verifier-code artifacts. The committed
`papers/math_outcome_boundary.json`,
`papers/math_starting_construction_boundary.json`,
`papers/math_heuristic_handoff_boundary.json`, and
`papers/math_heuristic_stage_sequence_boundary.json` sidecars emit the current
Section 3.2 constructive-math absence boundaries and are validated by
`validate_paper_manifest()`.
The top-level Appendix B `figure_exhibit_boundary` now records the missing
Figures 10-14 exhibit layer separately from family/result boundaries. It
requires future figure/subfigure ids, caption values, previous/current metric
values, rendered visual artifacts, render parameters, source Colab locators,
and verifier links while keeping those rows and artifacts `not_recorded_locally`.
For Section 3.2 aggregate mathematical-outcome evidence,
`libreevolve.problems.benchmarks.math_outcomes` now records an absence boundary
for the paper's over-50-problem, more-than-five-branch, roughly 75%
best-known rediscovery, and roughly 20% SOTA-improvement source facts. The
boundary also corrects an earlier local misattribution: pinned Section 3.2 has
no blanket result-verification sentence, and its "In all these cases" clause
instead introduces the simple-or-random starting-point statement. It validates
the required future per-instance and aggregate
fields, but per-problem/per-parameter rows, branch labels, previous-best
references, construction/verifier links, outcome statuses, and recomputed
aggregate percentages remain absent. The same module now records the Section
3.2 starting-point absence boundary for the paper statement that the initial
starting point was "a simple or a random construction"; per-instance starting
construction artifacts, generator/seed records, baseline metrics, and
prior-best seeding policies remain absent. It also records the Section 3.2
heuristic-handoff absence boundary: AlphaEvolve evolved search-heuristic
programs instead of direct constructions, gave them fixed budgets such as
`1000` seconds, showed them the previous best heuristic's construction, and
selected for better produced constructions. Local heuristic program artifacts,
incumbent/produced construction artifacts, before/after metrics, scores, and
verifier evidence remain absent. A separate staged-heuristic absence boundary
preserves the paper's claim that final constructions often came from sequences
of specialized heuristics, with early broad-gain stages from random/simple
states and later fine-tuning stages near optimal configurations. Per-stage
ordering, roles, input/output construction artifacts, improvement deltas, and
verifier evidence remain absent.
For Appendix B.4 uncertainty-inequality evidence, the registry now records the
source formulation, the `[33]` prior-bound rounding distinction (`0.353`
stated versus `0.3523` rounded), the first-version Hermite-polynomial result
boundary (`C4 <= 0.3521` using coefficients
`[0.32925, -0.01159, -8.9216e-5]`), the qualitative similarity claim against
`[33]`, and the post-first-version revision note (`[18]` at `0.3284`, then
AlphaEvolve at `0.3216`). These rows are still absence boundaries: `[33]`
source locator, prior-solution rounding artifact, rounding-audit certificate,
coefficient payloads, Hermite/Fourier/root certificates, origin-condition certificates,
eventual-nonnegative certificates, coefficient-comparison artifacts including
prior/AlphaEvolve coefficient payloads, basis-alignment certificate,
similarity metric, and hypothesis-source artifact, Colab/verifier linkage,
comparison-to-`0.3284` certificates, and recomputed constants are not recorded
locally.
It also checks `libreevolve/problems/benchmarks/alphaevolve_ablations.json`,
which defines the AlphaEvolve Figure 8 ablation report contract for the full
system, `No evolution`, `No context in the prompt`, `No meta prompt evolution`,
`No full-file evolution`, and `Small base LLM only`. The registry requires
component-disable assertions, three independent seeds, target aggregation,
equal-budget fractions, required result fields, and AlphaEvolve citation
metadata, but it does not claim those reports have been run. Its
`No full-file evolution` row now carries a validated `paper_scope_boundary`
that records AlphaEvolve's tensor-decomposition loss-function-only setup and
marks the current localized single-file diff/no-topology scope as
`not_equivalent`; that boundary is still not executable proof that only the
loss function is mutable. The `No evolution` row now carries a validated
`paper_scope_boundary` that records the repeated-sampling/no-evolutionary
feedback setup and marks current zero-generation/seed-only labels as
`prompt_history_unproven`; it still has no executed prompt/history proof that
each proposal repeatedly starts from the same initial program without
evolutionary-database parent, inspiration, previous-candidate, or
archive-feedback context, nor fixed backend request parameters, fixed LLM-call
budgets, same candidate-validation pipeline, disabled critique/feedback proof,
sample-index alignment, target metric/threshold linkage, comparator artifact
hashes, or linked evolutionary-run evidence. The committed
`papers/repeated_sampling_baseline_boundary.json` sidecar preserves the same
controlled-comparator absence boundary for paper-manifest validation. The `No
context in the prompt` row is currently too
broad for the paper definition: AlphaEvolve describes removing explicit
problem-specific context, not removing the current program or evolutionary
prior-program context. The row now carries a validated
`paper_scope_boundary` that marks the current parent/inspiration/failure/plugin
section-disable scope as `over_broad_not_equivalent`, but it still needs
executed prompt-history proof that explicit context sources are absent and a
paper-facing classification of explicit context versus core evolutionary prompt
ingredients.
The `Small base LLM only` row now carries a validated `paper_scope_boundary`
that records the intended single-small-base-model generation setup and marks
the current declarative single-backend/small-base labels as
`telemetry_unproven`; it still has no backend metadata or call-ledger proof
that every mutation-generation call used a single small/base model with no
large-model routing or fallback. The `No meta prompt evolution` row now
carries a validated `paper_scope_boundary` that marks the current declarative
meta-prompt-disabled labels as `lineage_unproven`; it still has no
prompt-history, call-ledger, or prompt-program lineage proof that meta-prompt
calls and prompt-template mutations were disabled only in the ablated run. The
report contract now requires Figure 8's matrix tensor-decomposition and
kissing-number sphere-packing target families, target-metric identity,
higher-is-better direction, normalization policy, and mean/standard-deviation
curve summaries checked against the three independent seed traces.
For AlphaEvolve context-ingestion status, "deterministic selection provenance"
means path-segment-aware local context globs: `*` stays within one path
component and `**` recursively matches zero or more components.
DeepResearch prompt context now clears after empty or error refreshes instead
of silently reusing stale synthesis, and its in-memory retrieval-event history
is bounded with retention counters. Retrieval skips non-finite best-fitness
state with structured diagnostics instead of querying providers with `nan` or
`inf`, request URLs are persisted as hash-backed summaries instead of raw query
strings, and the default query includes best-program metric/code terms rather
than only generic fitness text, plus bounded task-description and
explicit-context terms plus bounded local paper manifest title/id terms. Later
queries also include bounded terms from captured proposal hypotheses. Direct
arXiv helper calls validate safe
query/result-limit parameters before HTTPS request construction. Live arXiv
responses record transport status and provider payload hashes, and oversized
payloads are rejected before XML parsing or prompt injection. Successful
retrieval text is rendered as non-authoritative evidence with explicit
delimiters and persisted trust-policy metadata. Run-local retrieval cache
snapshots, bounded/redacted provider-result snapshots, and offline cache replay
now exist for DeepResearch, and active
prompt-visible retrieval context is linked to query, cache, retained-source
ranking, transport-policy, and result hashes. Retained sources with
summary/content text include bounded/redacted source-content snapshots with raw
and stored hashes, plus audit-only query-overlap relevance scores that do not
change provider-order retention. Later queries include bounded recent
failure-history terms, and semantic-boundary audits reject source-ranking
metadata that claims semantic, learned, or external scoring evidence while
run-level coverage keeps those ranking/scoring readiness flags false.
Unbounded full provider payload persistence, semantic ranking
scores beyond
deterministic query-overlap audit metadata, full source-content trust evidence
beyond bounded trust-policy metadata,
replayable transport/failure decisions, and DeepResearch provider-output replay
integrated with full-runtime resume remain open. Treat live
retrieval metadata as best-effort provenance rather than audit-grade source
integrity evidence.

## Implementation status

Current run manifests now record final `LLMEnsemble` scheduler-state snapshots
for audit/reproducibility, including role-level call/retry/fallback/provider
attempt summaries, provider-reported token totals, and provider-failure
category counts, plus the configured reward-accounted role policy. Successful
feedback grader calls can now reward exact configured `feedback:<name>` roles
with their normalized score. Separate per-role scheduler/budget policies remain
AlphaEvolve-alignment gaps.
Prompt-program context policy can now also cap rendered recent failure-memory
records with `recent_failure_limit`; null renders all retained recent failures,
positive values render the most recent N, and zero suppresses that block while
recording available/rendered/omitted counts in prompt diagnostics.
The same policy can cap rendered selected inspirations with
`inspiration_limit`; null renders all already selected inspirations, positive
values render the first N in existing order, and zero renders none.
It can now also override upstream inspiration sampling strategy with
`inspiration_strategy`, using the same safe strategy enum as run config while
recording config-vs-policy strategy provenance.
It can also override upstream inspiration sample count with
`inspiration_sample_count`, separately from the rendered-inspiration cap, while
recording config-vs-policy count provenance.
Generated candidate metadata now includes
`metadata.inspiration_selection.metric_diversity`, which links selected
inspirations to the prompt-visible render policy, labels each visible
inspiration with a declared metric niche, records raw/normalized metric values,
and marks whether the prompt contained at least two distinct metric niches.
Completed manifests summarize this evidence in
`runtime.history.metric_diverse_inspiration_report`; its `benchmark_policy`
boundary keeps `alphaevolve_section_2_4_claim_ready` false until
benchmark-required metric-diverse prompt policies, cross-run fixtures, and
scalar/single-metric comparison reports exist. The same report now carries
`libreevolve.metric_diverse_benchmark_comparison_readiness.v1`, keeping
benchmark prompt-policy enforcement, cross-run fixtures, scalar-only
baselines, single-metric baselines, and equal-budget comparison reports false.
It also carries `libreevolve.metric_diverse_benchmark_fixture_readiness.v1`,
recording prompt-visible metric-niche evidence while keeping benchmark-required
prompt policies, cross-run fixtures, scalar/single-metric baselines,
equal-budget comparison reports, and Section 2.4 claim readiness false.
The committed `papers/metric_diverse_prompt_boundary.json` sidecar keeps this
prompt-visible-evidence-only scope machine-validated.
It can also cap already validated/redacted plugin `extra_context` with
`extra_context_max_chars`, recording input/rendered/omitted character counts.
LLM-grader prompt context can now be narrowed with `llm_feedback_fields`, a
safe allowlist over `name`, `score`, `discard`, `error`, and `feedback`.
Qualitative LLM-feedback policy can now be declared with `criterion`,
`criterion_description`, `evaluator_gap_rationale`, `rubric`,
`feedback_intent`, and `calibration_report_id`. Runtime feedback records retain
a bounded `qualitative_policy` object, and completed manifests summarize
configured/observed criteria under
`runtime.history.qualitative_feedback_policy_report`. This records the
hard-to-code criterion boundary for properties such as simplicity, but it is
not yet AlphaEvolve-grade evidence because calibration/task-suite linkage and
criterion-quality ablations remain open. Completed manifests also emit
`runtime.history.qualitative_feedback_prompt_history_audit_report` for bounded
prompt-history row joins. The committed
`papers/qualitative_feedback_boundary.json` sidecar keeps this declared-policy
and audit scope machine-validated apart from executed calibration/task-suite
evidence and independent feedback-quality validation.
The committed `papers/feedback_calibration_boundary.json` sidecar separately
preserves the feedback-calibration report-contract boundary: calibration report
and artifact-inventory schemas, grader declarations, task-suite declarations,
criterion-quality fields, safe artifact-reference validation, summary
rendering, and schema tests exist, while runtime calibration runners, executed
task-suite results, grader ablations, and independent feedback-quality
validation remain absent.
Proposal metadata prompt context can now be narrowed with `proposal_fields`, a
safe allowlist over idea, rationale, and hypothesis fields.
Stage-summary prompt context can now be narrowed with `stage_summary_fields`,
a safe allowlist over stage name, status, score, error, IO, and configured
check summaries.
Execution-output prompt context can now be narrowed with
`execution_output_fields`, a safe allowlist over stdout, stderr, and fallback
error fields.
Sample/retry diagnostics can now be narrowed with `sample_retry_fields`, a safe
allowlist over status, stage, sample, attempt, fitness, and error fields.
Program-output prompt context can now be narrowed with `program_output_fields`,
a safe allowlist over source, size, hash, redaction, preview, and value fields.
Validator-artifact prompt context can now be narrowed with
`validator_artifact_fields`, a safe allowlist over path, stored path, hash,
redaction, content excerpt/status, and bounded artifact-content fields.
Nested bounded artifact-content fields can now be narrowed with
`validator_artifact_content_fields`.
Artifact-content rendering mode and caps can now be controlled per prompt
program with `validator_artifact_content_mode`,
`validator_artifact_content_max_bytes`, and
`validator_artifact_content_max_chars`.
Skipped validator-artifact diagnostics can now be narrowed with
`validator_skipped_artifact_fields`.
Validator diagnostic prompt context can now be narrowed with
`validator_diagnostic_groups`, a safe allowlist over bounded evaluator
diagnostic group renderers.
Configured-stage diagnostic prompt context can now narrow nested metric-threshold
and artifact-output check fields with `stage_metric_threshold_fields` and
`artifact_output_check_fields`.
Validator-boundary diagnostic prompt context can now narrow nested resource-limit
fields with `validator_resource_limit_fields`.
Validator metadata summaries can now be narrowed with `validator_metadata_keys`,
an ordered safe-key allowlist inside the metadata-summary diagnostic group.
Syntax-error diagnostics can now be narrowed with `syntax_error_fields`, a safe
allowlist over `path`, `line`, `offset`, and `message`.
Metric-bound diagnostics can now be narrowed with `metric_bound_fields`, a safe
allowlist over `metric`, `value`, `bounds`, `direction`, `normalized`, and
`clamped`.
Configured-stage check diagnostics can now be narrowed with
`configured_stage_check_fields`, a safe allowlist over stage names, threshold
status fields, stop reasons, and nested metric/artifact check summaries.
Malformed-metric diagnostics can now be narrowed with
`malformed_metric_fields`, a safe allowlist over `reason` and `message`.
Metric-aggregation diagnostics can now be narrowed with
`metric_aggregation_fields`, a safe allowlist over `sample_count`,
`attempt_count`, and `metric_aggregation`.
Validator-boundary diagnostics can now be narrowed with
`validator_boundary_fields`, a safe allowlist over local-subprocess boundary,
network, secret, and resource-limit fields.
Manifest-backed run bundles now have a persisted validator-boundary consistency
gate: `validate_run_artifact_validator_boundary_consistency()` checks
`manifest.json` `policies.validator_execution` against every `history.jsonl`
and `failure_history.jsonl` evaluation boundary, and `libreevolve show`
reports stream/line diagnostics for missing, legacy, or mismatched boundary
rows.
The paper manifest also requires
`papers/validator_artifact_promotion_boundary.json` to preserve that CLI/show
inspection gate without presenting it as run-finalization, CI, release-
artifact promotion, historical-bundle batch, or archival blocking enforcement.
Execution diagnostics can now be narrowed with `execution_diagnostic_groups`,
a safe allowlist over validator boundary, stdin, diagnostic-output, and
timeout-cleanup subgroups.
Validator-stdin diagnostics can now be narrowed with `validator_stdin_fields`,
a safe allowlist over stdin policy, source, size, hash, and retention fields.
Diagnostic-output diagnostics can now be narrowed with
`diagnostic_output_fields`, a safe allowlist over decode, byte-count,
replacement-count, cap, truncation, and redaction fields.
Timeout-cleanup diagnostics can now be narrowed with
`timeout_cleanup_fields`, a safe allowlist over cleanup method, status,
process-group, job-object, child-PID, and error fields.
Local context source prompt content can now be capped per source with
`context_source_max_chars`, recording original/rendered/omitted character
counts for each selected source.
`context_source_truncation` can now choose deterministic `head` or `head_tail`
retention under that cap.

Read the status table as a maintained index, not as a proof ledger for every
sentence in each status cell. The manifest gate checks IDs, roles, status-class
boundaries, referenced local paths, and TODO cross-links. It does not yet
machine-verify every natural-language implementation phrase, benchmark
qualifier, or source-specific absence sentence against code and paper evidence.

| ID | Title | Role | Current LibreEvolve status |
|---|---|---|---|
| 2506.13131 | AlphaEvolve | Primary specification target | Partially implemented: `libreevolve/core/loop.py` evolves blocks with explicit Python-file marker boundaries and unsupported non-Python marker diagnostics, local task-primary text-workspace candidates with Python autodetection or explicit seed-policy primary selection, manifest-visible candidate-language policy, stage-bound host or digest-pinned OCI build/runner execution with problem-owned scoring, bounded generated-artifact capture, immutable image/runtime/provisioning identity, candidate network denial, bounded container resource flags, and ordered in-image toolchain probes, and manifest-visible size reject budgets, workspace topology mutations, empty-file creation through full-mode file sections, rejection of ambiguous, overlong, and generated dot-prefixed candidate paths, unknown full-block target rejection, CLI happy-path full-workspace best export, workspace materialization with recursive link/junction preflight and typed materialization-failure diagnostics, plus basic candidate imports in local validators, mutation modes including canonical SEARCH/REPLACE diff compatibility, proposal-rationale capture with selected parent/inspiration prompt rendering, bounded leading explanatory-preamble capture/reporting before structured mutation markers, selected post-critique proposal provenance, preamble-only proposal stripping, structured evaluator results, schema-validated evaluator result dataclasses, structured non-JSON evaluator-return diagnostics, finite explicit Program fitness semantics, schema-safe redacted synthetic diff-error diagnostics, complete declared metric vectors for synthetic framework-generated evaluator failures, stage-threshold stops that retain real validator metric vectors, configurable local cascades with manifest-safe non-colliding stage labels, aggregate workspace syntax diagnostics, evaluator contract preflight before run-artifact mutation, strict scalar evaluator-output validation with reserved boolean validity, strict metric-bound ordering plus out-of-range clamp diagnostics, primary metric normalization, equal-weight normalized declared-metric archive selection, diagnostic Pareto frontier snapshots over declared normalized metrics, feedback-sourced objective metrics filled by configured graders, workspace-aware local MAP-Elites complexity/diversity inputs, configurable in-memory parent/inspiration sampling, prompt sampler/context ingestion with deterministic selection provenance, unmatched include diagnostics, secret-safe context source/pattern labels, hidden-context opt-in policy, skipped diagnostics for context extraction failures, default-fail explicit include extraction policy with opt-in degraded warning diagnostics, resource-bounded local context ingestion, and exact PDF excerpt page/span citations. Also implemented: bounded execution-output, validator-diagnostic, validator-metadata, and grader-feedback prompt summaries, prompt-program database and optional meta-prompt mutation, structured prompt-program context-policy hooks, configurable synchronous critique reviewer pools with first/last-valid aggregation, synchronous critique with bounded/redacted prompt construction, retained critique metadata, and deterministic no-valid-mutation selection provenance, LLM feedback graders with full-workspace feedback prompts, configurable feedback-failure retries/policies, and manifest-safe grader labels, manifests, run identity/collision policy, source-root Git/source/problem provenance, generated-run artifact classification for problem provenance, bounded source/problem provenance file reads, cwd-independent generated-root provenance exclusion, final effective config validation after CLI overrides, secret-safe and bounded plugin-module provenance, source/problem included-file and skipped-diagnostics provenance digests, UTC runtime wall-clock manifest timestamps with monotonic elapsed-budget linkage, manifest-runtime-aware `show` status for completed/aborted/partial runs, typed missing/invalid/invalid-schema `pyproject.toml` provenance, direct evaluator entrypoint provenance, enforced problem-local evaluator dependency provenance, secret-safe persisted evaluator path metadata, streamed evaluator source hashing with read-error diagnostics, validator helper import precedence checks, manifest-safe candidate/program identifiers, skipped seed setup diagnostics, local run-budget accounting with stop reasons, logical LLM-call caps, and provider-attempt/token/configured-cost/latency stops, provider-free zero-generation seed baselines, run-local framework RNG isolation from process-global Python `random`, persisted and CLI-restorable framework RNG snapshots, CLI-scoped provider credential-presence and local client-construction preflight for mutation-capable runs, manifest-safe backend model identifiers, configured custom import-path LLM backends, configured entry-point plugin loading with manifest-safe constructor options and declared constructor-option schemas, restored/replay backend spec and prompt validation, ensemble prompt-size enforcement before registry/custom backend calls, selected PEP 621 metadata and NumPy numerical-runtime provenance, normalized ensemble-level LLM call telemetry with deterministic call ids, validated prompt/role labels, request parameters, client context, copied telemetry snapshots, malformed-output failure records, and redacted provider errors, candidate history/admission provenance, bounded proposal-hypothesis history indexes, typed static sidecars with bounded base64 generated/replaced static/binary members, direct raw binary workspace entries normalized into immutable static members, verified source-copy static asset materialization, policy-backed bounded-file prompt rendering for copied UTF-8 evaluator artifacts, heuristic prompt section packing under `prompt_max_chars` / `prompt_max_estimated_tokens`, explicit per-role LLM backend routing policy with role route telemetry, sequential-by-default sibling proposal batches with opt-in local worker-owned asynchronous LLM sampling and candidate evaluation, seed baseline generation 0 with generated candidates starting at generation 1, plugin score composition, built-in plugin spec attribution in prompt context, finite causal-plugin score validation, CLI built-in plugin alias preflight, manifest-safe configured plugin label validation at config and manifest boundaries, constructor-level built-in plugin cadence validation, custom plugin constructor-signature attribution, validator environment allowlisting with stdout/stderr redaction, best-effort validator timeout process-tree cleanup, opt-in evaluator artifact copy-out, archive-state snapshots with cursor plus full archive contents restore from accepted history, a circle-packing smoke fixture, a small matrix smoke benchmark, a matrix-result report contract, a paper-result certification contract, a systems held-out/reference report contract, a benchmark hardening contract, a scope-checked matrix smoke hardening bundle, an equal-budget ablation-result report contract, an LLM budget report contract, restored runtime budget snapshot consumption, controller budget-event replay, a composed full-runtime restore bundle for compatible surfaces, and a provider cancellation policy contract. Flexible non-code candidate abstractions are documented as a deliberate current code-file-set divergence. Broad real-language/compiler/package-manager runner fixtures beyond the checked expression, host C, and single digest-pinned OCI Python smoke contracts, deterministic multi-platform and remote-daemon replay, hostile-code security certification, and language-aware evolve-block marker grammars, future topology and language-runner edge-case collision policy, semantic proposal-index retrieval, calibrated proposal-quality models, cross-run proposal tables beyond bounded hypothesis and proposal-score reports, configurable natural-language preamble policies, full-replacement preamble disambiguation, rationale-quality scoring, configurable/full validator-metadata prompt policy, selected-backend provider-token section packing outside mutation prompts and exact counters across non-OpenAI provider families, distributed and cross-generation async workers, validator-wide and hostile-code-reviewed OS/container network sandboxing beyond the candidate OCI path, broader non-project build/package/accelerator/provider-output replay provenance, custom plugin package-registry and direct-object constructor-value policy beyond manifest-safe entry-point schemas, live authenticated provider request/model-registry validation beyond credential-presence and client-construction preflight, live provider pricing/default-rate capture beyond configured token-cost estimates, live provider SDK cancellation, timeout-driven stop enforcement and richer runtime cancellation artifacts beyond configured in-run quarantine observations, queued/running async or pending-work budget consumption inside `evolve()` beyond the pre-applied full-runtime restore boundary, async budget accounting, Pareto/frontier primary archive replacement, durable cross-run metric-specific optimization, stable learned/evaluator-provided descriptor models and tested archive rebin semantics beyond insertion-time TF-IDF coordinates, queryable evolutionary database beyond bounded current-run resurfacing, live/retrieval/semantic context selection and deeper per-field prompt context policy beyond the current validated structured surface, migration-event replay, async controller/pending-work resume state, full provider-output/pending-work resumed-trace proof, seeded lineage replay, executed feedback calibration reports beyond the declared report/artifact contract, critique async overlap and calibrated reviewer scoring beyond current synchronous first/last-valid reviewer pools, critique provider isolation, independent per-role live scheduler ownership beyond role-scoped backend eligibility and role budget maps, cross-run provider-failure quarantine/resume policy beyond restored scheduler failure-policy state, provider-output/raw-payload replay, and critique/meta-prompt reward calibration beyond configured reward-accounted roles, benchmark-grade hardening reports beyond the smoke-scope matrix bundle, tensor-decomposition target suites/algorithms, executable independent certifiers/deployment evidence, real systems held-out/reference fixtures, benchmark scripts that emit equal-budget ablation reports, and stronger AlphaEvolve-scale benchmarks remain open. |
| 2511.02864 | Mathematical exploration and discovery at scale | Constructive math benchmark candidate | Not implemented; potential future benchmark; cached locally as `papers/2511.02864__Mathematical_exploration_and_discovery_at_scale.pdf` and validated through `papers/follow_on_sources.json` as the later arXiv/source row for Section 3.2 mathematical-discovery handoff evidence, but no normalized Appendix B result rows, construction payloads, verifier artifacts, recomputed values, or full notebook cell inventories exist under this cache claim. |
| 1504.04909 | MAP-Elites | Foundational archive algorithm | Implemented as `libreevolve/population/map_elites.py` configurable local 3D archive whose default axes are archive selection score (falling back to fitness), fixed-bound serialized-workspace text length, and serialized-workspace TF-IDF diversity against the current elite corpus. `map_elites_descriptor_axes` can instead select normalized evaluator metrics, numeric evaluator metadata, or numeric candidate metadata as behavior descriptors, and archive snapshots persist descriptor-model revision/reference/no-rebin policy metadata plus occupied-cell, elite, Pareto-frontier, and metric-cell insertion-time descriptor values. Runtime manifests also include `runtime.history.archive_descriptor_drift_audit`, an audit-only comparison of retained snapshot descriptor values against accepted-history admission descriptors. `papers/map_elites_illumination_boundary.json` now preserves the paper-facing absence boundary for full Mouret-Clune illumination evidence, including explicit `b(x)`/`f(x)` contracts, `P`/`X` map exports, illumination metrics, visualization/lineage reports, and retina/soft-robot/real-arm reproduction. Stable learned/evaluator-provided descriptor modeling, tested archive rebin semantics, full illumination metrics, paper-domain reproductions, and AlphaEvolve-scale archive/controller semantics remain open. |
| auer-cesa-bianchi-fischer-2002 | UCB1 finite-time analysis | Foundational bandit policy | Implemented as `libreevolve/llm/ensemble.py` heuristic UCB-style backend router over archive-admitted valid fitness improvements; rewards are bounded and call-id attributed, while canonical regret assumptions are explicitly out of scope unless the scheduler is promoted beyond heuristic routing. `papers/ucb1_boundary.json` records missing bounded reward-distribution evidence, conditional-mean/stationarity checks, regret reports, canonical index equivalence, selected-index traces, UCB-family variant support, and throughput-depth proof status. |
| 2511.17592 | GigaEvo | Framework inspiration | Not implemented as described: no Redis lifecycle database, asyncio DAG engine, insight stage, concurrent units, LangGraph mutation, or benchmark reproduction. Diff/full mutation modes are partially present. `papers/gigaevo_framework_boundary.json` records the source-specific framework-parity absence boundary and dual GitHub source-disambiguation gap. |
| 2510.14150 | CodeEvolve | Agentic code-evolution inspiration | Not implemented as described: LibreEvolve has generic prompt-program selection and optional evidence-conditioned template mutation, but no CodeEvolve-style prompt/solution dual fitness, semantic crossover, meta-prompting, targeted refinement, scheduler, sandbox, CVT-MAP-Elites, benchmark, ablation, or quality-cost evidence. `papers/codeevolve_boundary.json` records this source-specific absence boundary. |
| 2511.23473 | ThetaEvolve | Test-time training inspiration | Only `libreevolve/plugins/ttt_rl.py` clipped-reward JSONL export exists through `ttt_rl`; CLI-loaded exports are run-scoped while direct `TTTRLPlugin(log_dir=...)` exports are user-managed external artifacts. Repeated flushes are deduplicated within one plugin instance, malformed examples are rejected before queueing, retained in-memory training examples are capped with overflow export, final artifact metadata flushes pending rows, and export payloads are secret-redacted plus field/aggregate bounded. There is no ThetaEvolve dynamic environment, batch sampling, lazy penalty, reward shaping, online RL/GRPO loop, checkpoint management, throughput report, or benchmark-comparison parity. `papers/thetaevolve_boundary.json` records this source-specific absence boundary. |
| 2602.10233 | ImprovEvolve | Modular search inspiration | Static prompt guidance exists in `libreevolve/plugins/modular.py` and candidate prompt-context metadata labels it as `static_prompt_only` with `operation_selected: static_modular_guidance`, described `generate_config`/`improve`/`perturb` operation names, and false execution/enforcement flags; no enforced or executed generate/improve/perturb loop, Stage A/B runner, basin hopping, GigaEvo outer loop, human-edit provenance, benchmark rows, ablations, or budget evidence exists. `papers/improvevolve_boundary.json` records this source-specific absence boundary. |
| 2602.15951 | MadEvolve | Domain evolution inspiration | Background only; no free-parameter tracking, nested optimizer, JAX/vmad compatibility, optimized source injection, BAO/21cm/tSZ task adapter, generated innovation report, run/model statistics, or reward-hacking control exists. `papers/madevolve_boundary.json` records this source-specific absence boundary. |
| 2603.14575 | CausalEvolve | Causal-guidance inspiration | Only `libreevolve/plugins/causal.py` token-pattern outcome-factor guidance exists; no LLM causal scratchpad. Factor detection uses the shared compact/canonical SEARCH/REPLACE parser for diff-mode mutations and direct token-pattern scanning for full-mode replacement payloads, fixed factors use pull-once initialization before UCB-like reward scoring, retained outcome history is capped, and malformed non-text mutation evidence is counted instead of crashing, but the detected factors are still fixed local token-pattern categories rather than LLM-discovered causal variables. `papers/causalevolve_boundary.json` records the source-specific absence boundary for POMDP/SCM framing, causal scratchpad memory, interventions, treatment effects, surprise/abduction artifacts, and benchmark rows. |
| 2510.06056 | DeepEvolve | Retrieval/debug loop inspiration | Only `libreevolve/plugins/deep_research.py` best-fitness-plus-code/metric/task/context/failure/local-paper-manifest/recent-proposal-hypothesis arXiv/web-search context exists; direct arXiv helper calls validate safe query/result-limit parameters and use HTTPS, live responses are bounded before XML parsing, successful retrieval text is rendered as non-authoritative evidence with explicit delimiters, candidate history records bounded retrieval events with query inputs/policy, bounded/redacted provider-result snapshots, bounded/redacted source metadata, bounded source-content snapshots, audit-only query-overlap relevance scores, summary hashes, redacted provider errors, request URL summaries, transport/payload hashes, trust-policy metadata, cache metadata, oversized-response diagnostics, semantic-boundary rejection of source-ranking metadata that overclaims semantic/learned/external scoring, and active-context query/cache/source-ranking/transport/result hash links, while run manifests record compact retrieval summaries with event counts, source metadata counters, status/source counts, result sizes, synthesis hashes, cache/query/trust policy, bounded transport/payload fields, and false readiness flags for semantic source ranking, learned ranking, and external source scoring. Run-local cache snapshots, offline cache replay, plugin artifact summaries for cache snapshot counts/sizes/hashes and provider-result snapshot counts/hashes, local paper manifest title/id query terms, and recent proposal hypothesis query terms exist, but there is no learned or externally scored semantic ranking beyond deterministic query-overlap audit metadata, unbounded full provider-payload persistence, full source-content trust evidence beyond bounded trust-policy metadata, DeepResearch provider-output replay integrated with full-runtime resume, or DeepEvolve-style cross-file debugging/editing loop. `papers/deepevolve_boundary.json` records the source-specific absence boundary for plan/search/write proposals, proposal pseudo-code, cross-file coding, reflection/debugging, score-zero fallback, nine-task benchmark rows, qualitative judge rows, and deep-research ablations. |
| 2601.21096 | Magellan | AlphaEvolve compiler-optimization application context | Background only; missing executable C++ decision logic, compiler-pass integration, EVOLVE-BLOCK compiler spans, compiler rebuild/macro-benchmark evaluation, Vizier-style autotuning, LLVM inlining/register-allocation/XLA task rows, baseline/generalization rows, maintainability evidence, and a dedicated Magellan runtime repository. `papers/magellan_boundary.json` records this source-specific absence boundary. |
| 2605.14718 | Adapting AlphaEvolve to Optimize Fully Homomorphic Encryption on TPUs | AlphaEvolve compiler-optimization application context | Background only; cached locally as `papers/2605.14718__FHE_on_TPU.pdf`, but LibreEvolve has no TFHE/Jaxite or CKKS/CROSS primitive harness, Google Cloud TPUv5e hardware-execution provenance, FHE correctness-test suite, generated cryptographic-kernel artifact hashes, latency benchmark rows, baseline implementation identity, or independent reproduction output for the reported 2.5x, 1.31x, and 1.18x speedups. |
| 2605.05921 | Intentmaking and Sensemaking: Human Interaction with AI-Guided Mathematical Discovery | AlphaEvolve HCI/user-study context | Background only; cached locally as `papers/2605.05921__Intentmaking_and_Sensemaking.pdf`, but LibreEvolve has no formative-study dataset, participant/session trace schema, intentmaking/sensemaking event taxonomy, AlphaEvolve UI/dashboard artifact inventory, privacy/redaction protocol for study data, coded qualitative-analysis evidence, or collaborative-instrument workflow support. |
| 2605.01794 | Discover Fast Power Allocation Solution for Multi-Target Tracking via AlphaEvolve Evolution | AlphaEvolve radar/resource-allocation application context | Background only; cached locally as `papers/2605.01794__Radar_Power_Allocation.pdf`, but LibreEvolve has no radar scenario/target-count taxonomy, physically inspired feature schema, deterministic constraint-satisfying power-allocation transform, multi-target tracking simulator, baseline iterative solver identity, average relative performance-loss benchmark rows, cross-scenario generalization evidence, three-orders speedup reproduction, or independent checker output. |
| 2602.23413 | EvoX: Meta-Evolution for Automated Discovery | Meta-evolution framework context | Background only; cached locally as `papers/2602.23413__EvoX.pdf`, but LibreEvolve has no adaptive strategy-genome schema, outer meta-evolution loop, strategy-credit assignment, dynamic search-policy update artifacts, EvoX task-suite taxonomy, baseline comparison table against AlphaEvolve/OpenEvolve/GEPA/ShinkaEvolve, token-efficiency report, strategy ablation records, or independent reproduction output. |
| 2602.02919 | DeltaEvolve: Accelerating Scientific Discovery through Momentum-Driven Evolution | Context-memory framework context | Background only; cached locally as `papers/2602.02919__DeltaEvolve.pdf`, but LibreEvolve has no first-class semantic-delta schema, node-transition effect attribution, semantic-delta memory bank, multi-level database, progressive disclosure sampler, token-savings report, full-code-history baseline comparison, scientific-task benchmark taxonomy, or independent reproduction output. |
| 2606.06473 | MLEvolve: A Self-Evolving Framework for Automated Machine Learning Algorithm Discovery | Long-horizon MLE framework context | Background only; cached locally as `papers/2606.06473__MLEvolve.pdf`, but LibreEvolve has no MLE-Bench task harness, Progressive MCGS state schema, graph-based reference-edge provenance, entropy-inspired progressive schedule, Retrospective Memory knowledge base/global memory, adaptive coding-mode artifacts, 12-hour medal-rate/valid-submission report, mathematical-algorithm baseline comparison, linked-code audit, or independent reproduction output. |
| 2605.09764 | LEVI: Stronger Search Architectures Can Substitute for Larger LLMs in Evolutionary Search | Cost-aware search-architecture context | Background only; cached locally as `papers/2605.09764__LEVI.pdf`, but LibreEvolve has no LEVI-style diversity-preserving solution-database report, large/small model mutation-router policy, role-assignment trace, rank-preserving proxy benchmark, rollout/provider-cost accounting report, systems-research benchmark fixture, prompt-optimization budget comparison, linked-code audit, or independent reproduction output. |
| 2601.10657 | PACEvolve: Enabling Long-Horizon Progress-Aware Consistent Evolution | Long-horizon consistency framework context | Background only; cached locally as `papers/2601.10657__PACEvolve.pdf`, but LibreEvolve has no context-pollution detector, hierarchical context-management/pruning artifacts, mode-collapse diagnostics, momentum-based backtracking controller, unified crossover/backtracking sampler, trajectory-collaboration diagnostics, LLM-SR/KernelBench/Modded NanoGPT benchmark report, linked-code audit, or independent reproduction output. |
| 2605.08520 | FlashEvolve: Accelerating Agent Self-Evolution with Asynchronous Stage Orchestration | Asynchronous-stage orchestration context | Background only; cached locally as `papers/2605.08520__FlashEvolve.pdf`, but LibreEvolve has no asynchronous worker queue, stage dependency scheduler, artifact-version lineage DAG, stale-artifact detector, staleness repair policy, speculative stage-completion records, adaptive workflow controller, EvolBench/ChatDev/MetaGPT benchmark report, 3.5x/4.9x throughput reproduction, linked-code audit, or independent reproduction output. |
| 2605.20086 | What Do Evolutionary Coding Agents Evolve? | Trace-diagnostic evaluation context | Background only; cached locally as `papers/2605.20086__Evolutionary_Coding_Agents.pdf`, but LibreEvolve has no EvoTrace-compatible trace schema, nine-class edit taxonomy annotation pipeline, LLM-as-judge edit reannotation validation, parent-child search graph export, prompt/context substitution replay, model substitution replay, component-removal intervention harness, constant-retuning baseline, deterministic deleted-line reintroduction/cycling detector, held-out generalization report, or independent reproduction output. |
| 2605.01120 | New Bounds for Zarankiewicz Numbers via Reinforced LLM Evolutionary Search | Constructive math benchmark candidate | Not implemented; potential future benchmark; cached locally as `papers/2605.01120__Zarankiewicz_Reinforced_Search.pdf`, but LibreEvolve has no Zarankiewicz parameter manifest, bipartite graph construction schema, `K_{s,t}`-free verifier, exact-value/lower-bound table, generated-algorithm artifact hashes, OpenEvolve setup provenance, reward-function specification, upper-bound comparison ledger, per-parameter cost accounting, or independent reproduction output for the three exact values, 41 lower bounds, four matched closed cases, or sub-$30 cost claim. |
| 2604.01658 | CORAL: Towards Autonomous Multi-Agent Evolution for Open-Ended Discovery | Autonomous multi-agent evolution context | Background only; cached locally as `papers/2604.01658__CORAL.pdf`, but LibreEvolve has no long-running autonomous agent sessions, shared persistent memory repository, asynchronous multi-agent execution runtime, heartbeat-based intervention controller, isolated per-agent workspaces, evaluator separation layer, resource/session/health manager, knowledge-reuse analysis, 10-task SOTA report, 3-10x improvement-rate reproduction, Anthropic kernel-engineering 1363-to-1103 cycle reproduction, linked-code audit, or independent reproduction output. |
| 2605.13821 | Harnessing Agentic Evolution | Harnessed meta-editing context | Background only; cached locally as `papers/2605.13821__AEvo.pdf`, but LibreEvolve has no process-level evolution state exposing accumulated candidates/feedback/traces/failures/costs, meta-agent procedure or agent-context editor, standardized editable evolution workspace, protected evaluator boundary, searchable candidate history for meta-editing, meta-editing phase/evolution-segment runner, run-plan contract, procedure-versus-agent evolution instantiation, five-baseline agentic/reasoning benchmark report, 26% relative-improvement reproduction, three-task open-ended optimization report, linked-code audit, or independent reproduction output. |
| 2605.09959 | G-Zero: Self-Play for Open-Ended Generation from Zero Data | Verifier-free co-evolution context | Background only; cached locally as `papers/2605.09959__G_Zero.pdf`, but LibreEvolve has no Hint-delta intrinsic-reward computation from unassisted versus hint-conditioned Generator responses, Proposer model, Generator model, self-generated query/hint dataset, GRPO proposer trainer, DPO generator trainer, co-evolution training loop, pseudo-label noise filter, exploration-coverage report, best-iterate suboptimality fixture, unverifiable-domain benchmark, external-judge reward-hacking comparison, linked-code audit, or independent reproduction output. |
| 2605.21605 | GenEvolve: Self-Evolving Image Generation Agents via Tool-Orchestrated Visual Experience Distillation | Multimodal trajectory-distillation context | Background only; cached locally as `papers/2605.21605__GenEvolve.pdf`, but LibreEvolve has no image-generation tool pipeline, visual-reference ingestion, prompt-rewriting/layout-planning/image-generation/refinement trajectory schema, tool-call artifact lineage, Agentic Visual Experience Distillation or Visual Experience Distillation target, dense token-level supervision record, multimodal policy-update loop, GenEvolve-Data metadata, GenEvolve-Bench task/report, baseline comparison, linked-code audit, or independent reproduction output. |
| 2605.29847 | EvoRubric: Self-Evolving Rubric-Driven RL for Open-Ended Generation | Self-evolving reward-rubric context | Background only; cached locally as `papers/2605.29847__EvoRubric.pdf`, but LibreEvolve has no single-policy Reasoner/Rubric-Generator co-evolution loop, generated-rubric provenance, meta-verifier records, zero-variance pruning records, Leave-One-Out peer-consensus traces, criteria memory pool, dense multi-objective reward vectors, expert-prior rubric expansion, medical/writing/science benchmark report, reward-hacking audit, linked-code audit, or independent reproduction output. |
| 2605.29293 | LLM-ALSO: LLM-Driven Adaptive Learning-Signal Optimization for Multi-Agent Reinforcement Learning | Learning-signal optimization context | Background only; cached locally as `papers/2605.29293__LLM_ALSO.pdf`, but LibreEvolve has no sparse-reward cooperative MARL harness, Critic LLM diagnosis role, Generator LLM reward-shaping role, compact behavior evidence record, stage-specific coordination-failure diagnosis, reward-shaping configuration artifact, branch-validation trajectory, validated-update promotion gate, main-training trajectory provenance, learning-efficiency report, linked-code audit, or independent reproduction output. |
| 2512.18746 | MemEvolve: Meta-Evolution of Agent Memory Systems | Memory-architecture evolution context | Background only; cached locally as `papers/2512.18746__MemEvolve.pdf`, but LibreEvolve has no explicit encode/store/retrieve/manage memory-component design space, memory-architecture genotype, memory-system mutation/evaluation loop, experiential-knowledge co-evolution trace, EvolveLab benchmark mapping, static-memory baseline comparison, cross-task or cross-LLM transfer report, performance-delta record, linked-code audit, or independent reproduction output. |
| 2606.06114 | Towards Healthy Evolution: Exploring the Role and Mechanisms of Human-Agent Interaction in Self-Evolving Systems | AlphaEvolve healthy-evolution oversight context | Background only; cached locally as `papers/2606.06114__ANCHOR_Healthy_Evolution.pdf`, but LibreEvolve has no ANCHOR human-like oversight agent, phase-specific norm-correction interface, safety-drift metric lineage, output-verification intervention records, reflection/review artifact stream, supervision-frequency/cadence trace, preservation-of-objective-performance report, coding/math/safety benchmark report, linked-code audit, or independent reproduction output. |
| 2605.27276 | SIA: Self Improving AI with Harness & Weight Updates | Agent harness-plus-weight self-improvement context | Background only; cached locally as `papers/2605.27276__SIA.pdf`, but LibreEvolve has no Feedback-Agent that chooses between harness and weight updates, editable task-agent harness inventory, harness patch provenance, online RL/fine-tuning loop, adapter/checkpoint lifecycle, trajectory-to-training-data promotion policy, rollback/resume policy, harness-only versus weight-only versus combined ablation report, LawBench/kernel/scRNA benchmark report, linked-code audit, or independent reproduction output. |
| 2606.06324 | From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws | Trace-grounded harness repair context | Background only; cached locally as `papers/2606.06324__HarnessFix.pdf`, but LibreEvolve has no HTIR trace-normalization schema, raw-trace normalization record, harness-code linkage, step-level provenance, execution/tool/context/lifecycle/observability/verification/governance harness-layer attribution taxonomy, recurring flaw consolidation, scoped repair operator schema, generated harness patch artifact, flaw-specific validation specification, unacceptable-regression threshold record, held-out SWE-Bench Verified/Terminal-Bench 2.0 Verified/GAIA/AppWorld benchmark report, linked-code audit, or independent reproduction output. |
| 2606.05922 | Retrospective Harness Optimization: Improving LLM Agents via Self-Preference over Trajectory Rollouts | Retrospective harness optimization context | Background only; cached locally as `papers/2606.05922__RHO.pdf`, but LibreEvolve has no unlabeled past-trajectory harness optimizer, hard/diverse coreset selector, DPP coreset record, parallel retrospective re-solve workflow, group rollout artifact, self-validation diagnostic, self-consistency diagnostic, candidate harness-update set, pairwise self-preference selector, label-free promotion policy, deployment/rollback metadata, behavior-pattern shift report, long-horizon accuracy report, SWE-Bench Pro 59%-to-78% reproduction, linked-code audit, or independent reproduction output. |
| 2605.30621 | Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents | Harness-capability disentanglement context | Background only; cached locally as `papers/2605.30621__Harness_Updating_Is_Not_Harness_Benefit.pdf`, but LibreEvolve has no harness-updating metric schema, harness-benefit metric schema, evolver-versus-task-solver model-pair matrix, capability-tier grouping record, cross-benchmark harness self-evolution report, activation-failure audit, adherence-failure audit, capability-budget recommendation report, public-code snapshot audit, or independent reproduction output. |
| 2604.25850 | Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses | Agentic harness observability context | Background only; cached locally as `papers/2604.25850__AHE.pdf`, but LibreEvolve has no file-level editable harness component graph, component-observability schema, layered drill-down trajectory evidence corpus, raw-trace-to-digest provenance, decision-observability prediction contract, next-round falsification record, per-edit rollback manifest, ten-iteration Terminal-Bench 2 report, SWE-bench-verified transfer report, cross-family transfer report, tools/middleware/memory ablation, public-code snapshot audit, or independent reproduction output. |
| 2605.13357 | AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents | AI harness runtime-substrate context | Background only; cached locally as `papers/2605.13357__AI_Harness_Engineering.pdf`, but LibreEvolve has no complete eleven-responsibility harness contract for task specification/context selection/tool access/project memory/task state/observability/failure attribution/verification/permissions/entropy auditing/intervention recording, no H0-H3 harness ladder, no trace-based episode-package schema, no controlled validation-task reproduction, no model-harness-environment capability equation record, no failure-attribution taxonomy report, no deterministic requirement-check package, no structured verification report, no public-code snapshot audit, or independent reproduction output. |
| 2605.21516 | Harnesses for Inference-Time Alignment over Execution Trajectories | Inference-time trajectory-alignment context | Background only; cached locally as `papers/2605.21516__Inference_Time_Trajectory_Alignment.pdf`, but LibreEvolve has no harness parameterization for decomposition versus guided execution, workflow-granularity sweep, retry-budget study, guidance-induced action-reweighting report, stage-level gap metric, over-decomposition failure report, over-pruning failure report, hallucinated-execution failure report, partial-harnessing stopping rule, controlled synthetic experiment, terminal-agent benchmark reproduction, linked-code audit, or independent reproduction output. |
| 2606.01770 | Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System Deployment on Open-Ended Task Streams | Adaptive auto-harness deployment context | Background only; cached locally as `papers/2606.01770__Adaptive_Auto_Harness.pdf`, but LibreEvolve has no chronological open-ended task-stream schema, history-growth record, task-heterogeneity report, distribution-shift detector, evolution-loss/adaptation-loss decomposition, stateful multi-agent evolver, harness tree, solve-time routing policy, human-steering hook, overfitting/accuracy-peak-decline report, prediction-market/security-competition/event-forecasting benchmark reproduction, five-baseline comparison, linked-code audit, or independent reproduction output. |
| 2603.28052 | Meta-Harness: End-to-End Optimization of Model Harnesses | Outer-loop harness-code optimization context | Background only; cached locally as `papers/2603.28052__Meta_Harness.pdf`, but LibreEvolve has no first-class harness-code candidate schema, filesystem-visible harness workspace, agentic proposer that edits harness code, execution-trace feedback bundle, score/provenance replay package, outer-loop harness search controller, online text-classification reproduction, 200-problem IMO-level retrieval-augmented math reproduction, TerminalBench-2 reproduction, held-out-model transfer report, linked-code audit, or independent reproduction output. |
| 2602.22425 | ArchAgent | AlphaEvolve computer-architecture application context | Background only; missing generated C++ cache replacement policies, ChampSim `policy.h` integration, CRC hardware-configuration rows, SPEC06/Google Workload Trace fixtures, IPC-over-LRU benchmark rows, Policy31/Policy31-Tuned/Policy61/Policy62 artifacts, hardware-realizability/state-budget verification, post-silicon specialization records, simulator-escape controls, and distributed simulation reliability evidence. `papers/archagent_boundary.json` records this source-specific absence boundary. |
| 2602.16928 | Multiagent Learning | AlphaEvolve MARL algorithm-discovery result context | Background only; missing CFR/PSRO candidate schemas, OpenSpiel imperfect-information game fixtures, exploitability metrics, exact-oracle PSRO records, VAD-CFR/SHOR-PSRO result rows, WOP-CFR/PM-PSRO distillation rows, IQM ablations, random normal-form validation, and generated solver artifact provenance. `papers/multiagent_learning_boundary.json` records this source-specific absence boundary. |
| 2603.09172 | Ramsey Numbers | Constructive math benchmark candidate | Not implemented; potential future benchmark; missing Ramsey graph candidate schemas, `run()` primary/prospect graph contracts, clique/independent-set verifiers, new/matched/exact lower-bound rows, graph and search-code artifact hashes, initialization-family rows, graph-size/lower-bound semantics, and independent checker outputs. `papers/ramsey_numbers_boundary.json` records this source-specific absence boundary. |
| 2509.18057 | Hardness of Approximation | AlphaEvolve complexity-theory result context | Background only; `papers/theoretical_cs_sources.json` records article/arXiv/PDF evidence and a nested proof-element artifact boundary for graph/gadget inventories, verifier code, independent brute-force outputs, theorem-lifting metadata, baseline/SOTA rows, and source-repository status, but no graph/certification benchmark. |
| 2603.06692 | Combinatorics Berczy | Constructive math benchmark candidate | Not implemented; potential future benchmark; missing bipartite and planar graph-reconstruction harnesses, Alon-Tarsi Latin-square trade/involution harnesses, Rota-basis local-exchange harnesses, local-correction certificate schemas, symmetry-scramble and hard-negative replay records, evolved-code and Gemini-summary artifact hashes, reported metric/conjecture rows, repository snapshots, and independent verifier outputs. `papers/combinatorics_berczy_boundary.json` records this source-specific absence boundary. |
| 2601.16175 | TTT Discover | Test-time discovery context | Background only; missing test-time-training policy-update loop, single-problem RL environment, continuous-reward problem contract, state-reuse/search subroutine records, Tinker runtime evidence, gpt-oss-120b backend records, math/kernel/AtCoder/biology result rows, expert/organizer review records, public-code artifact hashes, cost records, best-of-N comparator rows, and independent reproduction outputs. `papers/ttt_discover_boundary.json` records this source-specific absence boundary. |
| 2603.08679 | Bilateral Trade | AlphaEvolve mechanism-design result context | Background only; missing bilateral-trade distribution candidate schemas, fixed Discrete Equal Revenue buyer fixture, evolved seller CDF generator runtime, PMF/CDF/survival validation, first-best and Random-Offerer GFT evaluators, `1e-15` integer-rounding policy, witness distribution artifacts, evolved/evaluation code hashes, prior-baseline rows, alternate-search attempt rows, BIC/BB/IR assumptions, unrounded-mixture caveat handling, and independent checker outputs. `papers/bilateral_trade_boundary.json` records this source-specific absence boundary. |
| 2601.01235 | Bruhat Intervals | Constructive math benchmark candidate | Not implemented; potential future benchmark; missing permutation-pair candidate schemas, simple-reflection decoding, d-invariant evaluator, Bruhat order/Ehresmann matrix verifier, `x_m`/`y_m` witness generator, dyadic interval and dyadically well-distributed permutation checkers, fundamental/complementary block validators, poset-hypercube isomorphism checker, Kazhdan-Lusztig R-polynomial linkage records, cluster-algebra/Bruhat-graph consequence rows, AlphaEvolve prompt/model/budget provenance, public artifact hashes, and independent checker outputs. `papers/bruhat_intervals_boundary.json` records this source-specific absence boundary. |
| 2511.12916 | Fault2Flow | AlphaEvolve-optimized workflow application context | Background only; missing regulatory-PDF ingestion, MinerU-to-Markdown evidence, PASTA fault-tree schemas, human-in-the-loop expert review states, AlphaEvolve reasoning optimizer records, multi-island archive provenance, PlantUML mind-map/fault-tree agents, n8n workflow synthesis/activation, workflow verification/refinement traces, DL/T 722-2014 dataset snapshot, transformer fault case rows, GPT-5 judge outputs, Table 1 reproduction rows, token-usage records, human-annotation ethics records, and local workflow snapshots. `papers/fault2flow_boundary.json` records this source-specific absence boundary. |
| 2601.05943 | Global Nonlinear Optimization | Optimization benchmark comparator | Not implemented; potential future benchmark; missing direct NLP formulation schemas, Mosel model artifacts, FICO Xpress and SCIP solver runners, solver license/version records, solver parameter/time-limit metadata, incumbent/bound/certificate artifacts, numerical tolerance and rounding policy, AlphaEvolve validation-code outputs, Table 1 distance-ratio rows, Table 2 circle-packing rows, Table 3 hexagon-packing rows, solver-attribution caveat handling, dual-bound-detail caveats, and independent checker outputs. `papers/global_nlp_optimization_boundary.json` records this source-specific absence boundary. |
| 2506.16750 | Autoconvolution | Constructive math benchmark candidate | Not implemented; potential future benchmark; missing 575-interval witness schema, coefficient payload hashes, formula (3) discrete autoconvolution checker, `L_j` sequence recomputation, `L2`/`Linf`/`L1` norm checks, exact fraction validation, decimal tolerance policy, AlphaEvolve and Matolcsi-Vinuesa baseline records, simulated-annealing and gradient-refinement provenance, public GitHub artifact snapshots, Mathematica `Verify.nb` evidence, support-normalization checks, NCSU HPC resource records, and independent checker outputs. `papers/autoconvolution_boundary.json` records this source-specific absence boundary. |
| 2505.16105 | Sums and Differences | Constructive math benchmark candidate | Not implemented; potential future benchmark; missing explicit U-set construction schema, W(m,L,B) inclusion-exclusion checker, base-(2B+1) injective encoding checks, sumset/difference-set cardinality verifiers, max-element/q-value verifier, theta recomputation, GMP exact-arithmetic records, floating-point search records, small and large parameter exact rows, exact-value artifact snapshot, AlphaEvolve 54265-integer baseline, huge-set compression policy, lineage comparison rows, tolerance policy, and independent checker outputs. `papers/sums_differences_boundary.json` records this source-specific absence boundary. |
| 2506.01896 | Sums and Differences II | Constructive math benchmark candidate | Not implemented; potential future benchmark; missing sequence-of-U construction schema, large-deviation I(c,B) checker, asymptotic W(m,floor(rm),B) checker, Lemma 1/Lemma 2 verification, q/s/d bound derivation records, theta0 variational-formula recomputation, MATLAB 2024b code provenance, B=3..10 tolerance-sweep reproduction, finite-prefix artifact policy, AlphaEvolve and Gerbicz baseline rows, lineage comparison rows, convergence/tail-bound checks, and independent checker outputs. `papers/sums_differences_sequence_boundary.json` records this source-specific absence boundary. |

In the AlphaEvolve row, the remaining `async workers` shorthand means
distributed evaluator/sampler workers, a full cross-generation dependency
scheduler, and resumable pending work. Local candidate evaluator workers and a
bounded timing-proven cross-generation window are implemented behind
`async_candidate_evaluation`, `async_llm_sampling`, and
`async_generation_window` with the narrower boundary described below. Finite
detailed evaluator limits retain the generation barrier because their pending
consumption cannot be reserved exactly.
The FlashEvolve row's asynchronous-worker absence refers to its stage-
dependency orchestration runtime, which this candidate queue does not provide.

AlphaEvolve initial-program provenance note: current manifests and history
preserve safe seed source identity for generation-0 baselines, and optional
seed-source metadata can now record seed variant ids, idea-origin classes,
human/background contribution roles, prior-technique labels, and background
references. Completed manifests include
`runtime.history.initial_program_idea_provenance_report`, which links that
metadata to generation-0 history rows and declared metric names. AlphaEvolve
Section 3.1 reports matrix runs boosted by human ideas in the initial program,
such as stochastic evaluation or evolutionary approaches; LibreEvolve still
needs exact rendered prompt digests, prompt-history seed-context spans, seed
workspace hash linkage, replicate protocols, executed equal-budget
seed-variant result evidence, and contribution review/signoff before making
that class of paper claim. The committed
`papers/initial_program_idea_provenance_boundary.json` sidecar preserves this
metadata-contract-only boundary for paper-manifest validation, and
`papers/initial_program_seed_variant_matrix.json` records design-level
simple/random/researcher/stochastic/evolutionary seed-variant comparison axes
without claiming prompt-context linkage, prompt digests, benchmark result
tables, replicate protocols, or AlphaEvolve human-seeded benchmark parity.

AlphaEvolve initial-pool divergence note: completed manifests now include
`runtime.history.initial_pool_divergence_report`, which compares generated
candidates against generation-0 seed programs with canonical workspace hashes,
bounded primary-file text distance, changed-component summaries, and numeric
metric L1 distance over shared metric names, plus generic bounded
evaluator-output signature distance. This is paper-visible syntactic, metric,
and evaluator-output telemetry, not task-specific functional-distance proof;
task-specific behavior/output-distance artifacts, thresholds for
"substantially different" claims, benchmark-level discovery-distance telemetry,
cross-run discovery-distance tables, and syntax/function joint claim gates
remain open. The committed
`papers/initial_pool_divergence_boundary.json` sidecar keeps this telemetry-
only scope machine-validated.

AlphaEvolve mutation-operator note: LibreEvolve supports the edit payload
surfaces listed in the table, including SEARCH/REPLACE, configured full
replacement, file/block sections, and topology commands. Completed manifests
now include `runtime.history.mutation_operator_boundary_report`, which records
the configured mutation mode, per-candidate adaptive diff/full-format flags,
observed payload surfaces, fixed parser policy, sample generated-candidate
mutation records, and `claim_ready: false` for LLM-constructed or adaptively
selected higher-level operator families. The
AlphaEvolve Section 5 Related Work distinction from handwritten mutation/crossover
operator sets remains open until LibreEvolve records proposal-level
operator-family provenance, construction or selection evidence, and benchmark
telemetry beyond those fixed local parser surfaces. The committed
`papers/mutation_operator_boundary.json` sidecar preserves this edit-payload
format selection versus operator-family evidence boundary for paper-manifest
validation.
Completed manifests now also include
`runtime.history.prompt_example_copy_report`, which inventories the built-in
mutation-format example sentinels and records exact, normalized
file-section-region, and simple example-format skeleton copy signals for
example-only fragments. It is diagnostic-only: hard rejection, broader
semantic/renamed copy detection, and custom prompt-template example
inventories remain open.
The committed `papers/prompt_example_copy_boundary.json` sidecar keeps this
built-in-diagnostics-only scope machine-validated.
Completed manifests now also include
`runtime.history.prompt_current_binding_report`, which records current-run
prompt/current-program binding evidence: generated candidate ids, prompt
program ids, rendered prompt hashes, parent-code render hashes/path policy,
parent and candidate workspace hashes, LLM call ids, mutation payload hashes,
diff SEARCH match counts/spans for non-file-section diff payloads,
evolve-block-inner span mapping when an exact SEARCH match falls inside parent
block content, workspace file-section target records with parent/candidate
full-file span and hash evidence, full-mode whole-file and evolve-block target
span records, evaluator status, archive admission, and prompt-history row
joins to candidate history rows. Completed manifests also export
`prompt_current_binding_table.jsonl`, with schema-versioned rows carrying run
ids, candidate ids, prompt ids, hashes, and row joins for cross-run comparison.
The evidence remains diagnostic provenance rather than a hard semantic proof.

AlphaEvolve initial-program validity note: current seed handling can still
evaluate and record invalid generation-0 seeds as permissive
optimization-pressure baselines, including examples such as `hello_world`.
AlphaEvolve Section 2.1 describes the initial implementation inside evolvable
blocks as complete, though rudimentary, and runnable through the task
skeleton/evaluator. LibreEvolve now has
`initial_program_validity_policy: alphaevolve_strict` and
`runtime.history.initial_program_validity_report` for runs that require every
selected seed to be evaluator-valid and to return declared metrics before
mutation. The `embedded_evaluate_math` smoke fixture now opts into strict mode
and has CLI-path manifest evidence for a claim-ready single-seed strict report.
Benchmark suites still need multi-seed strict fixture reports,
provider-startup strict preflight evidence, matrix and constructive-math
strict seed fixtures, enforced separation of optimization-pressure seeds, and
problem-specific validity evidence before every initial seed baseline can be
treated as paper-faithful AlphaEvolve initial-solution evidence. The sidecar
`papers/initial_program_validity_boundary.json` preserves that
strict-policy-available boundary and keeps default permissive runs outside
complete initial-program parity claims.

AlphaEvolve expert-formulation note: local context-source and problem/source
provenance records identify artifacts and rendered prompt context, and
LibreEvolve now has optional `formulation.yaml` /
`Problem.formulation_metadata` records plus
`runtime.history.problem_formulation_provenance_report` for contributor roles,
problem origin, formulation notes, objective/evaluator rationale,
parameter-scope decisions, background refs, and review/signoff state. Section
3.2 reports external mathematicians suggesting problems and advising
formulation, so mathematical benchmark fixtures still need populated,
expert-reviewed formulation metadata, expert/owner identity records,
evaluator/result artifact links, parameter-scope signoff, background-reference
artifacts, review timestamps or versions, and anti-gaming review evidence
before making that class of paper claim.
The committed `papers/problem_formulation_provenance_boundary.json` sidecar
preserves that metadata-contract-only boundary for paper-manifest validation.
The committed `papers/benchmark_fixture_readiness_boundary.json` sidecar
preserves the related smoke-scope boundary while linking the checked
deterministic matrix calibration and evolution fixtures. The latter runs four
normal run-local `evolve()` pipelines with scripted rank-7 mutations and emits
causal ancestry, budget, history, final-rank, and cascade records. Non-smoke
AlphaEvolve-comparable scope, stochastic LLM discovery, full-benchmark
anti-gaming negative fixtures, and paper-claim-ready benchmark scope remain
absent.
The committed `papers/systems_result_readiness_boundary.json` sidecar
preserves the systems-result boundary: LibreEvolve has schemas and validators
for systems reports, artifact inventories, evidence bundles, domain-specific
gate policy, claim calibration, application provenance, scheduling readiness,
compiler provenance, and hardware provenance, but it does not claim real
scheduling, kernel, compiler, or hardware fixture runs, deployment
measurements, expert confirmations, or domain-specific result artifacts.

AlphaEvolve collaborator-feedback note: LibreEvolve now has optional
`collaborator_feedback.yaml` / `Problem.collaborator_feedback_metadata` records
plus `runtime.history.collaborator_feedback_provenance_report` for early-user
or collaborator cohorts, feedback event ids, affected workflow areas,
change-artifact links, validation outcomes, privacy/redaction policy, and
review/signoff state. This is separate from in-run `llm_feedback` graders.
AlphaEvolve's Acknowledgements say broad early-user and collaborator feedback
shaped robustness and versatility, so paper-facing claims still need populated
multi-cohort feedback records with source artifacts, reviewed code/docs
change evidence, validation rerun artifacts, privacy/redaction artifacts,
review/signoff versions, longitudinal follow-up, and claim-to-feedback traces.
The
committed `papers/collaborator_feedback_provenance_boundary.json` sidecar
preserves this metadata-contract-only boundary for paper-manifest validation.

AlphaEvolve acknowledgement-role note: LibreEvolve now has optional
`acknowledgements.yaml` / `Problem.acknowledgement_metadata` records plus
`runtime.history.acknowledgement_role_provenance_report` for white-paper
review, early exploration, support/advice, practical-application management
advice, application review, application-specific advice, source locators,
privacy/redaction policy, and review/signoff state. These are paper-process
and governance roles, not implementation authorship, publication-author
metadata, benchmark validation, or deployment evidence; the
`matrix_multiplication` example now provides a reviewed `acknowledgements.yaml`
fixture for AlphaEvolve pages 21-22, and its zero-generation manifest report
is claim-ready for acknowledgement-role parity. The committed
`papers/acknowledgement_role_provenance_boundary.json` sidecar preserves that
claim-ready scope while excluding technical validation, publication-author
metadata, title-page affiliation metadata, system-contribution provenance,
local endorsement, and deployment evidence.

AlphaEvolve publication-author note: LibreEvolve now has optional
`paper_authors.yaml` / `Problem.paper_author_metadata` records plus
`runtime.history.paper_author_metadata_report` for equal contributors,
manuscript writers, paper-input contributors, corresponding authors,
source-page locators, title-page marker linkage, contact/privacy policy, and
review/signoff state. These publication metadata records are separate from
technical implementation provenance, acknowledgement roles, title-page
affiliation metadata, package/project metadata, and local validation evidence;
the `matrix_multiplication` example now provides a reviewed
`paper_authors.yaml` fixture for AlphaEvolve pages 22-23 plus title-page
marker linkage, and its zero-generation manifest report is claim-ready for
paper-author metadata parity. The committed
`papers/paper_author_metadata_boundary.json` sidecar preserves that scope
while excluding technical implementation evidence, acknowledgement-role
provenance, title-page affiliation metadata, system-contribution provenance,
local LibreEvolve authorship or affiliation, and copied public contact details.

AlphaEvolve title-page affiliation note: LibreEvolve now has optional
`title_page.yaml` / `Problem.title_page_metadata` records plus
`runtime.history.title_page_affiliation_report` for source-paper affiliation
text, footnote marker definitions, author-marker mappings, source-page
locators, source-rights linkage, privacy/redaction policy, and review/signoff
state. These records are source-publication facts, not local affiliation,
endorsement, licensing, publication-author, or technical capability evidence;
the `matrix_multiplication` example now provides a reviewed `title_page.yaml`
fixture for AlphaEvolve page 1, links it to `papers/source_rights.json`, and
its zero-generation manifest report is claim-ready for title-page affiliation
and footnote parity. The committed
`papers/title_page_affiliation_boundary.json` sidecar preserves that
source-publication scope while excluding local LibreEvolve affiliation or
endorsement, publication-author metadata, technical capability, benchmark
success, system-contribution provenance, rights regrant, and copied contact
details.

AlphaEvolve system-contribution note: LibreEvolve now has optional
`system_contributions.yaml` / `Problem.system_contribution_metadata` records
plus `runtime.history.system_contribution_provenance_report` for system design,
project scoping, first-benchmark iteration, final-system, infrastructure,
code-review, coordination, and supervision role provenance. These records are
paper-attributed development facts, not generic git history, package metadata,
publication-author metadata, acknowledgement roles, or local validation
evidence; the `matrix_multiplication` example now provides a reviewed
`system_contributions.yaml` fixture for AlphaEvolve pages 22-23, and its
zero-generation manifest report is claim-ready for system-development
contribution parity. The committed
`papers/system_contribution_provenance_boundary.json` sidecar preserves that
scope while excluding generic git history or commit authorship, package
metadata or distribution authorship, publication-author metadata,
acknowledgement-role provenance, local validation or benchmark success, and
deployment or production operation evidence.

AlphaEvolve process-exhibit note: completed manifests now include
`runtime.history.alphaevolve_process_exhibit_report` with schema
`libreevolve.alphaevolve_process_exhibit_report.v1`. The report preserves
stable Figure 1/Figure 2 IDs, local PDF page/caption locations, process
node/edge mappings to LibreEvolve components, Figure 2 pseudocode-step
mappings, and run-artifact cross-links for prompt history, LLM calls,
candidate history, evaluator artifacts, archive events, controller-budget
events, and best exports. It also records generated Mermaid/text
accessibility artifacts with hashes, per-step artifact-stream validation
records, strict JSONL row summaries, generated candidate semantic traces with
durable LLM and archive-admission stream rows, and component-to-TODO links for
the remaining process gaps. It now also records hashed source-PDF page text
extracts for AlphaEvolve Figure 1/Figure 2 and links the process exhibit to the
validated current local topology boundary in
`runtime.history.distributed_pipeline_topology_report` and records a
validated current inline evaluator-pool parallelism boundary. It remains
`claim_ready: false` because exact source-diagram layout reproduction,
exact source caption/text identity, source diagram text identity, diagram
node-label source alignment, source figure image/crop hashes, visual node
coordinates, source edge geometry/routing, Figure 2 pseudocode line-number
maps, Figure 2 line-level pseudocode alignment, visual diff/fidelity checks
against the source figures, AlphaEvolve-style async controller/sampler/
evaluator implementation, and independent evaluator-pool implementation
remain open.
The committed `papers/process_exhibit_boundary.json` sidecar emits the
`process_mapping_with_source_text_boundary_without_full_parity` boundary, and
`validate_paper_manifest()` requires it at the real repo root.

AlphaEvolve distributed-pipeline topology note: completed manifests now include
`runtime.history.distributed_pipeline_topology_report` with schema
`libreevolve.distributed_pipeline_topology_report.v1`. The report names the
current LibreEvolve controller, program database, configured LLM sampler
backends, local evaluator nodes, dependency edges, and links to consumed
runtime/controller-budget counters. With `async_llm_sampling: true`, it also
names a bounded proposal queue and local worker-owned LLM ensembles, records
out-of-order completion and deterministic proposal-order merge, and routes
reward updates through the owning worker queue. With
`async_candidate_evaluation: true`, it names a separate bounded candidate queue,
local `asyncio` evaluator workers,
producer backpressure, nonblocking evaluator dispatch, worker lifecycle and
completion telemetry, deterministic submission-order merge/admission, and
serial shared-state commit. Exact duplicate work already in flight is
coalesced into one evaluator task. When
`async_generation_window` is above `1`, combined runs may prepare later-
generation sampler work from pre-drain archive, prompt-program/reward, and
sampler-reward state while prior-generation
evaluation remains in flight. Sampler and evaluator task records retain
process-local monotonic intervals; the topology merges task intervals and
reports overlap only for exact union intersections. Finite detailed evaluator
limits retain the conservative generation barrier. Eligible runs drain and
commit generations in global submission/lifecycle order. When
configured stages set `eval_stages[].sample_workers`, it also records local
configured-stage sample-worker fan-out and deterministic sample-order merge
scope. Candidate evaluations retain summed sample elapsed time, observed
wall-clock time, and compression ratio; process-exhibit evaluator-pool records
summarize that as local sample-worker wall-clock compression when observed. It
is `claim_ready: false` because this is a bounded local sampler/evaluation
pipeline, not the full AlphaEvolve pipeline. Distributed evaluator fan-out,
full dependency wait-event scheduling/telemetry, distributed cross-generation
coordination, cross-process shared state, async scheduler-state
snapshots, and pending-work checkpoints remain open before Section 2.6 topology
parity. The committed
`papers/distributed_pipeline_topology_boundary.json` sidecar preserves this
bounded local cross-generation async partial boundary for paper-manifest validation. The committed
`papers/parallel_evaluation_readiness_boundary.json` sidecar preserves the
parallel-evaluation bounded local cross-generation async partial boundary for validation,
including the still-missing order-of-100-compute-hours candidate budget and
generation-cadence evidence under slow evaluator feedback, distributed evaluator workers, randomized-initialization shard
identity, distributed dependency scheduling, mutation-depth evidence, and pending-work
resume.

AlphaEvolve evaluator-metric note: LibreEvolve now reserves boolean `is_valid`
as a local admission gate outside declared `metrics.yaml` objectives and stores
non-scalar evaluator attachments separately, while AlphaEvolve Section 2.1 and
Figure 3 describe evaluator outputs as scalar metric dictionaries maximized by
convention. Completed manifests now include
`runtime.history.paper_evaluator_metric_contract` with declared
`paper_metric_names`, validity-gate exclusion, non-scalar output/feedback
exclusions, and raw/maximized/normalized value evidence. Export-ready paper
table rows now exist under `runtime.history.paper_metric_table_export` with
stable columns, display precision policy, excluded-metric notes, and a table
hash. `paper_metric_cross_run_report()` now compares those manifest reports
across runs, validates each single-run contract/table export, aggregates metric
names and table hashes, and records drift when metric names, primary metrics,
excluded declared metrics, table columns, or display policies differ.

AlphaEvolve evaluator-oracle note: completed manifests now include
`runtime.history.evaluator_oracle_registry` with ids, oracle types, authority,
input/output schema, metric ownership, failure policy, prompt-feedback linkage,
runtime counts, merge-policy metadata, and an `arbitration_policy` authority
matrix for the default validator or configured cascade stages plus optional LLM
feedback graders. The policy labels each oracle's benchmark sufficiency,
conflict role, failure effect, independence flag, and reference/statistical
status. The report also includes bounded `disagreement_outcomes` for observed
local validator-versus-feedback cases, such as feedback discards after an
evaluator pass, while labelling them as post-evaluator feedback effects rather
than independent reference/statistical-oracle arbitration. The report also
includes `oracle_source_evidence`, which validates local evaluator source refs
and hashes when available while keeping benchmark sufficiency and independence
false. The report keeps `claim_ready: false` because this is a registry for
the current local cascade and post-evaluator grader boundary, not yet proof of
candidate-level oracle lineage through the evolutionary loop, primary
evaluator contract proof, independent reference/statistical oracles,
independent disagreement outcome evidence, or per-oracle benchmark
sufficiency. The committed
`papers/evaluator_oracle_boundary.json`
sidecar now emits that
`local_arbitration_without_independent_oracle_evidence` boundary, and
`validate_paper_manifest()` requires and validates it at the real repo root.

AlphaEvolve cascade-report note: completed manifests now include
`runtime.history.evaluation_cascade_report` with schema
`libreevolve.evaluation_cascade_report.v1`. The report aggregates configured
stage promotion and attrition counts, threshold failures, failure reasons,
sample/retry/subprocess/timeout totals, elapsed seconds, promotion rates,
main-test exposure, early-prune counts, bounded candidate-stage cross-links to
`history.jsonl`, evaluator source refs when available, denominator-policy
boundaries, `stage_evidence_summary` role/source/hash/sample/exposure counts,
and a validated `libreevolve.evaluation_cascade_transition_matrix.v1` with
promotion-rule attribution, bounded candidate linkage, next-stage exposure,
and denominator reconciliation. Configured stages can also provide strictly
increasing difficulty/scale rationale and content-hashed declared-data or
embedded-input test-set identities. Benchmark seed/sample policy, repeated-
seed fixtures, empirical error-rate proof, and cost-savings evidence remain
open before claiming AlphaEvolve cascade efficiency or
hypothesis-testing parity. The committed
`papers/evaluation_cascade_boundary.json` sidecar now emits that
`runtime_transition_and_stage_identity_without_benchmark_efficiency_evidence`
boundary, and
`validate_paper_manifest()` requires and validates it at the real repo root.
Completed manifests also include
`runtime.history.cascade_hypothesis_test_policy_report`, which names configured
or fallback-inferred small-scale-filter/intermediate/main-test roles, links
current promotion counts, sample/seed configuration, and the reconciled
runtime adjacent-stage promotion matrix, and validates that
current promotion is either deterministic thresholds/artifact checks or the configured
`one_sided_lower_confidence_bound` repeated-sample gate. Configured gates retain
confidence-bound, p-value, optional sequential-stop evidence, and configured
normal-approximation false-promotion/false-rejection budget evidence. The
`binomial_success_rate` gate adds Wilson lower-bound repeated-seed success-rate
evidence and exact binomial tail diagnostics. Benchmark-calibrated thresholds
and full AlphaEvolve Section 2.4 hypothesis-testing parity remain open. A
linked checked fixture runs four normal `evolve()` pipelines under a scripted
rank-7 mutation control and records causal ancestry, budgets, and stage
exposure; it is not stochastic discovery or empirical error-rate evidence. The
committed `papers/cascade_hypothesis_test_boundary.json` sidecar keeps this
runtime policy-and-linkage scope machine-validated apart from stochastic
benchmark calibration and empirical false-promotion/false-rejection
validation.

AlphaEvolve embedded-evaluator note: configured stages can now opt into
`mode: embedded_evaluate`, which imports the materialized candidate primary
file and invokes a candidate-owned `evaluate(eval_inputs)` callable with
JSON-safe configured inputs. Metadata records the candidate callable and
eval-input provenance plus a runtime-enforced materialized-candidate workspace
dependency policy for local reads/imports, and completed manifests now
summarize executed embedded entrypoints under
`runtime.history.embedded_evaluator_entrypoint_report`,
including per-metric candidate path/block-span link candidates without causal
attribution claims, and external-validator stage metric visibility under a
non-causal score-linkage policy.
`validate.py` remains the default problem-loading contract, but
`load_problem()` now allows missing `validate.py` for a non-empty all-
`embedded_evaluate` stage list and the `embedded_evaluate_math` fixture covers
that embedded-only path. Default candidate-owned evaluator loading as the
primary problem contract, Figure 3 codebase fixture identity, typed eval-input
contracts beyond JSON-safe config provenance, generated/interactive task-input
replay across embedded and external stages, build isolation beyond the local
subprocess/workspace guard, and broader non-static/external-validator causal
score-link resolution remain necessary before
claiming Figure 3 evaluator parity. Supported embedded
`evaluate(eval_inputs)` paths now record static AST score-field attribution
when a returned metric expression depends on an EVOLVE block.
The committed `papers/embedded_evaluator_boundary.json` sidecar now emits the
`embedded_entrypoint_without_full_figure3_parity` boundary with an explicit
task-input replay sub-boundary, and
`validate_paper_manifest()` requires and validates it at the real repo root.
The committed `papers/figure3_supervised_exhibit_boundary.json` sidecar keeps
the separate Figure 3 supervised-learning paper-example boundary explicit:
generic embedded evaluation, prompt history, candidate history,
SEARCH/REPLACE parsing, preamble handling, prompt packing, and
prompt-example-copy diagnostics are not reproduced Figure 3 source,
assembled-prompt, and LLM-output subfigure evidence with displayed scores,
rendered hashes, and concrete run-artifact links.

AlphaEvolve evaluator-workload note: configured stages can now declare
`workload.type` as `simple_check`, `inner_search`, `ml_training`, or `custom`,
with validated dataset/split hashes, budget fields, checkpoint policy,
artifact policy, and scored metric-field names. Runtime manifests summarize
executed stage workload evidence under
`runtime.history.evaluator_workload_report`, including dataset-digest
completeness, score-field-to-returned-metric linkage, observed artifact file
evidence, protocol-readiness counts, and an explicit policy that managed
`inner_search` and `ml_training` runners remain absent. This is provenance for
the Section 2.1 claim that evaluators may run inner search or train models, not
yet proof that LibreEvolve provides workload-specific training/search runners,
checkpoint completeness, stochastic re-evaluation/replay policy, or
score-field-to-artifact causality.

AlphaEvolve task-specification note: startup manifests now include
`task_specification` with schema
`libreevolve.alphaevolve_task_specification_bundle.v1`. The bundle cross-links
initial programs, evaluator code or embedded evaluator stages, prompt
template/config metadata, backend choices, optional background context,
candidate representation, and objective metrics to manifest evidence. It
records a deterministic `task_spec_id`, validation, and unsupported/incomplete
labels. The same validated bundle is emitted as the standalone run artifact
`task_specification.json`. Completed manifests now also include
`runtime.history.task_spec_artifact_resolution_report`, which validates the
task-spec manifest paths and links each task-spec field to runtime artifact
evidence such as candidate history, prompt history, LLM calls, controller
budget events, evaluator artifacts, best exports, initial evolvable component
span ids when markers are present, and embedded score-field candidate-path
links with static AST causal attribution for supported candidate-owned
`evaluate` returns. It also records bounded candidate and prompt/evaluator
JSONL row joins. The checked
`docs/examples/task_specification.embedded_evaluate_math.json` file is a
validated paper-facing standalone example; broad real-language/replayable-build
task-spec parity beyond the host and single-image candidate-runner smokes
remains open, as do standalone schema
completeness for the full user-provided Figure 2 contract, user-authored
source identity, prompt-template content identity, config artifact identity,
cross-field consistency validation, and task-spec replay preflight. The
sidecar `papers/task_specification_boundary.json` preserves that runtime-
artifact-resolution-only boundary and prevents the current task-spec bundle
from being treated as full AlphaEvolve task-spec parity.

AlphaEvolve candidate-abstraction note: completed manifests now include
`runtime.history.candidate_abstraction_choice_report` with schema
`libreevolve.candidate_abstraction_choice_report.v1`. The report links the
current selected abstraction to `policies.candidate_language`, records the
task-primary bounded text-workspace boundary, summarizes runtime candidate workspace
shape, names unsupported or not-yet-distinguished constructor-function,
bespoke-search-algorithm, and paired solution/search alternatives, and keeps
`claim_ready: false` for AlphaEvolve-style abstraction-selection fidelity. The
committed `papers/candidate_abstraction_boundary.json` sidecar now emits the
`not_configured_as_problem_defined_abstractions` boundary, and
`validate_paper_manifest()` requires and validates it at the real repo root.
The committed `papers/candidate_abstraction_bias_matrix.json` sidecar records a
design-level abstraction-family matrix for direct solutions, constructor
functions, bespoke search algorithms, and paired solution/search
representations, including expected symmetry/bias fields and comparison axes.
Problem-level populated rationale, problem-defined abstraction hooks, paired
runtime support, and executed equal-budget benchmark comparisons across
alternative formulations remain open.
Completed manifests also include
`runtime.history.candidate_language_runner_contract_report` with schema
`libreevolve.candidate_language_runner_contract_report.v1`. This report records
the task-primary candidate policy, metadata-only or executable language/build
declarations, candidate-runner stage bindings, problem-owned scoring authority,
declaration counts/status under `runner_declaration_evidence`, bounded retained-
workspace path matches, and deduplicated executed build/runner records with
command hashes, executable basenames/path and toolchain-content hashes,
normalized version-output hashes, ordered probe attempts, optional pin results,
checked dependency-lock hashes, bounded/redacted process output, timeout/return
state, generated build artifacts, and minimal-environment metadata. Host records
retain same-host replay and host-network/unsandboxed scope. OCI records retain
runtime CLI content/version identity, approved host-environment key names with
values omitted, immutable image manifest/ID observations, missing-image-only
pull evidence, candidate-network denial versus provisioning registry access,
read-only-rootfs/mount/capability/resource policy, digest-scoped replay
readiness, and environment/toolchain identity linkage. `execution_summary`
reconciles executed/successful/build/artifact/language/build-system/toolchain
counts, and
`runner_environment_provenance` links execution to startup environment
evidence. The checked `candidate_runner_expression` fixture executes the
adapter path; `candidate_runner_c` compiles and runs one C11 primary with
observed compiler identity and a verified lock hash; and
`candidate_runner_python_oci` declares one digest-pinned interpreted build/run
path with an opt-in live Docker/Podman test. Mocked runtime tests and a daemon-
dependent skip are contract evidence, not a live cross-host result. Unsupported
task candidate-abstraction hooks and the remaining package-manager breadth,
deterministic platform/daemon replay, language-aware marker, hostile-code
security, and codebase-scale gaps remain explicit. The committed
`papers/candidate_language_runner_boundary.json` sidecar now emits that
`digest_pinned_oci_candidate_execution_partial` boundary, and
`validate_paper_manifest()` requires and validates it at the real repo root.

AlphaEvolve rendered-evaluation-result prompt note: completed manifests now
include `runtime.history.prompt_prior_score_provenance_report`, which links
generated mutation prompts to target-parent and selected-inspiration score
records. It records prompt ids/hashes, program roles, source workspace hashes,
raw finite metrics, displayed aggregate score formula, history/failure-history
row joins, evaluator-result row joins, and top-level prompt-feedback
execution-output display attribution for `stdout`, `stderr`, and `error`.
It also records stage-summary IO display attribution for rendered stage
stdout/stderr/error fields, an explicit `average_score` display/formula alias
for normalized `program.fitness`, and score-display field visibility for
aggregate and metric fields, including prompt-context metric selection,
cap-driven truncation, and suppressed metric reasons. It also records
feedback-section selection, deterministic order, section caps,
source-present/suppressed sections, and the fixed global feedback-text cap.
Completed runs also write `prompt_prior_score_table.jsonl` cross-run rows.
Completed manifests also include
`runtime.history.primary_prompt_instruction_report` with schema
`libreevolve.primary_prompt_instruction_report.v1`, recording generated prompt
target solution hashes, sampled supporting inspiration roles, mutation
instruction policy/hash, required task/current-program/instruction channel
presence, mutation-mode constraints, prompt/call ids when telemetry joins are
available, and the current primary-prompt provider-placement report boundary.
This is paper-facing primary-prompt ingredient evidence. Configured backend
`llm_prompt_roles` can now send structured provider instructions and retain
hash-only `prompt_role_policy` telemetry, and this report now joins hash-only
prompt-role policy summaries when mutation-call telemetry is present. This is
not yet provider-family payload-shape audit or AlphaEvolve primary-prompt
parity evidence; `papers/primary_prompt_role_telemetry_boundary.json`
preserves that boundary.
Completed manifests also include
`runtime.history.stochastic_prompt_format_distribution_report` with schema
`libreevolve.stochastic_prompt_format_distribution_report.v1`. It links
generated prompt ids to `[[prompt:name]]` option sets, normalized option
probabilities, selected alternative hashes/indexes, weight-source or
prompt-context override source, prompt/call linkage, inline/effective-config
source boundary, and the run-local framework RNG replay boundary. Separate
config-file source attribution and certified human-authored alternative
provenance remain non-parity boundaries.

AlphaEvolve existing-codebase integration note: completed manifests now include
`runtime.history.existing_codebase_integration_report` with schema
`libreevolve.existing_codebase_integration_report.v1`. The report inventories
runtime candidate workspaces for Python `# EVOLVE-BLOCK-START/END` marker
spans, stable span ids, skeleton hashes, unmarked-file hashes, seed-source
references, and the current marker grammar. The committed
`papers/existing_codebase_integration_boundary.json` sidecar now emits the
source-setup-level
`smoke_source_setup_fixture_recorded_missing_real_upstream` boundary, and
`validate_paper_manifest()` requires and validates it at the real repo root.
The checked-in `workspace_math` fixture now has `codebase_integration.yaml`
and a `source_setup/fixture_lib_v1/` pre-marker source bundle, so completed
manifests can show smoke source-setup metadata, pre-marker source hashes,
marker-only setup counts, evaluator-call continuity declarations, and copied
static-asset identity. The runtime report remains `claim_ready: false`
because this is not a real external upstream or codebase-scale integration
fixture, and independent setup-diff artifacts plus verified before/after
evaluator-call proof remain open.

AlphaEvolve marker-spelling note: completed manifests now include
`runtime.history.marker_spelling_provenance_report` with schema
`libreevolve.marker_spelling_provenance_report.v1`. The report records the
Section 2.1 canonical `# EVOLVE-BLOCK-START/END` source locations, the Figure
3 extracted/rendered `# EVOLVE-BLOCK START` space variant, local parser probes,
and a canonical-hyphenated-only compatibility decision. When the local
AlphaEvolve PDF cache is present, completed runs attach hashed page-text and
Figure 3 marker-line artifacts under `paper_artifacts/marker_spelling/` and
classify the space variant as
`pdf_text_extraction_uncertainty_not_supported_parser_syntax`, so the local
parser grammar remains distinct from source-exhibit reproduction.

AlphaEvolve runtime-accounting note: the ensemble call-history accessor is now
a bounded retained in-memory window with retained/total/dropped counters, not
an unbounded list. Config-created ensembles also write append-only
`llm_calls.jsonl` call/reward events, and `load_llm_call_ledger()` validates
that durable stream for sequence continuity, declared schema compatibility,
reward linkage, backend consistency, scheduler counter transitions, and safe
provider metadata including adapter-internal retry summaries. Call ids in
those records are deterministic `llm-call-...` hashes derived from the ordered
call sequence, role, backend index, prompt hash, retry/fallback attempt, and
attempt index, so matching call streams can be compared while repeated
same-prompt calls in one stream remain distinct. Ordered call spans,
prompt/output hashes, and deterministic ids are the current
replay-comparison evidence. The same metadata path now retains bounded
`provider_diagnostics` for scalar provider-native details with secret-redacted
and hash-backed string retention, and strict replay rejects malformed
diagnostic envelopes. The strict replay reader also derives
role-accounting summaries for calls, successes, failures, reward-accounted
calls, telemetry-only calls, ensemble retry/fallback attempts, and
adapter-internal provider attempts plus provider-reported token totals and
failure-category counts. Runtime manifests now copy that scheduler-derived
role accounting into compact `runtime.llm_accounting` summaries with aggregate
totals, per-role scheduler audit state, configured
logical-call/retry/fallback/prompt/output limits, and the effective
reward-accounted role policy. Successful feedback grader records now include
`scheduler_reward`, using normalized feedback score as scheduler reward when
the exact feedback role is reward-accounted. These are audit summaries; live
provider-attempt/token/configured-cost/latency stop checks now exist, but live
provider pricing/default-rate capture beyond configured estimates, full async
worker accounting, role-specific backend-pool policy, role-specific
exploration parameters, reward normalization reports, outcome-attribution
datasets, async role work queues, cross-role interference analysis, calibrated
reward semantics, and experiment-owned quota/budget policy beyond opt-in
role-scoped local UCB selection and role budget maps remain open. The static
sidecar `papers/llm_role_scheduler_boundary.json` preserves that
role-scheduler evidence boundary. Live
synchronous budget deltas are now also persisted as contiguous
`controller_budget_events.jsonl` rows for seed evaluations, generation
lifecycle events, LLM calls, candidate evaluations, and terminal stop reasons.
Replaying those rows reconstructs local `RunBudget` evaluation/generation/LLM
counters; full-runtime restore pre-applies that stream to the restored
`evolve()` budget snapshot, while direct event-stream consumption inside
`evolve()` and queued/running async worker state remain open.

AlphaEvolve LLM-failure note: failed ensemble calls now record normalized
`provider_failure_category` values for provider-response validation failures,
timeouts, rate limits, transport errors, provider client/server status errors,
and unknown failures, plus safe `provider_status_code` values when provider
SDK exceptions expose HTTP-style statuses. These categories are telemetry
inputs only; role-accounting summaries now aggregate them as audit evidence.
`llm_call_timeout_sec` also bounds the ensemble wait for each built-in or
custom backend attempt and records timed-out calls as structured timeout
failures with retry/fallback eligibility. Configurable role/backend
consecutive-failure quarantine and zero-reward scheduler penalties now exist
for exhausted reward-accounted failures, and scheduler failure-policy state can
be restored. Ledger replay summarizes remaining-gap categories by role,
including the role-specific quarantine/cross-run-resume gap when that policy is
active. Cross-run provider-failure policy proof beyond restored scheduler
state, provider-output/raw-payload replay, hard provider cancellation,
timeout-driven stop behavior, and richer runtime cancellation artifacts beyond
configured in-run quarantine observations remain open. The committed
`papers/provider_cancellation_boundary.json` sidecar preserves this
policy/audit-only boundary for paper-manifest validation.

AlphaEvolve prompt-archive note: `prompt_history.jsonl` records prompt-program
selection, scoring, lineage, invalid-mutation penalties, and structured
context-policy hashes. `PromptDatabase` replays existing prompt history before
adding configured seed templates, restoring prompt arms, scores, penalties,
lineage, and immutable context policy. Prompt-program context policy can now
disable optional channels, tune section priorities, and select safe
mutation-instruction variants (`default`, `minimal`, or `exploratory`).
It can also select bounded parent-feedback subsections such as stage summaries,
execution output, validator diagnostics/artifacts, program outputs, proposal
metadata, and LLM grader feedback, and can override configured stochastic
prompt-format alternative weights for safe configured markers. It can also
select and order already-loaded local context sources by safe problem-relative
path.
Prompt-template validation covers known placeholders, dry-run formatting,
configured mutation-channel checks, parent-placeholder retention for evolved
children, and explicit duplicate-arm audit identity: duplicate configured or
evolved template text remains separate prompt programs with independent ids and
shared `template_sha256` rather than being deduplicated. Role-specific
compatibility for critique, feedback grading, and meta-prompt call surfaces
remains open; `papers/prompt_template_compatibility_boundary.json` preserves
that generic-template-validation boundary for manifest validation.
Prompt reward accounting is limited to configured `absolute` and `improvement`
child-score reward modes normalized against finite prompt reward bounds, with
UCB-style prompt-arm selection over mean normalized rewards. Prompt history
records reward-policy metadata, and meta-prompt mutation requests can include
bounded prompt-performance evidence, but calibrated prompt-specific reward
models, prompt-lineage ablation reports, and stronger prompt-policy
attribution remain open; `papers/meta_prompt_scoring_boundary.json` preserves
that child-score prompt reward boundary for manifest validation.
Broader prompt-context evolution remains open for live/external context-source
selection, retrieval/summarization, inspiration selection, and finer-grained
evaluator/LLM-feedback field policy. Prompt-database parity with AlphaEvolve's
separate co-evolved prompt database is also still open: the current
`PromptDatabase` is a local prompt-arm history/scoring store, not a prompt-side
MAP-Elites/island archive with descriptor/objective indexes, archive events,
migration/rebin semantics, or async/controller-resumable prompt work;
`papers/prompt_database_parity_boundary.json` preserves that local prompt-arm
history boundary for manifest validation.

AlphaEvolve validator-network note: `validator_network_policy` now records host
network inheritance by default and can install a Python socket-level deny hook
for validator preflight/evaluation. This is policy evidence and an
accidental-egress guard, not OS/container-grade network isolation; the broader
network/container sandboxing gap remains open and is tracked by
`papers/validator_execution_boundary.json`.

AlphaEvolve prompt-budget note: mutation prompt diagnostics now include
`section_budget` with schema `libreevolve.prompt_section_budget.v1`. It records
per-placeholder priorities, hashes, character counts, estimated tokens,
required/optional totals, template overhead, and whether required sections fit
before final truncation. It also records deterministic section-packing
decisions for omitted optional sections. Direct `PromptSampler` callers can use
a provider token counter, and the normal mutation path can discover a shared
local OpenAI `tiktoken` counter across eligible mutation backends before
packing sections. `LLMEnsemble.generate()` also performs role-scoped common
counter discovery at the final prompt boundary for mutation, critique,
feedback, meta-prompt, registry-created, and custom roles, while backend
metadata can derive heuristic prompt-token capacity from `context_window_tokens`
minus `reserved_output_tokens`. Runtime prompt-section coverage rejects
complete and role-level provider-token section-packing overclaims for
critique, feedback, and meta-prompt, while keeping exact non-OpenAI/custom
counters, registry/custom role packing, and retrieval/context/plugin/failure-
memory packing readiness false. The remaining gap is automatic selected-backend
provider-token section packing across all prompt roles/provider
families and context surfaces, plus context-policy evolution. The committed
`papers/prompt_section_packing_boundary.json` sidecar preserves this
mutation-section-packing and bounded-validator-metadata boundary for
paper-manifest validation.

Meta-prompt mutation history stores a compact
`libreevolve.meta_prompt_context_policy_capability_summary.v1` with capability
and prompt-policy schemas, tunable field counts, field hashes, and per-section
hashes for the structured context-policy surface shown to the meta-prompt
model, with validation that rejects forged summary counts, hashes, sections, or
unsupported fields. This is audit metadata for the current validated surface,
not learned semantic context selection or retrieval/summarization policy
control. Runtime prompt-context policy coverage keeps those unsupported policy
readiness surfaces false for retrieval/summarization, semantic source
selection, non-`PromptSampler` roles, and DeepEvolve debug/refinement control.
That coverage is manifest evidence and capability-summary validation, not a
claim that prompt programs own learned retrieval/summarization, semantic source
ranking, arbitrary role prompts, or DeepEvolve-style debug/refinement loops.

AlphaEvolve MAP-Elites descriptor note: archive snapshots persist descriptor
policy and `descriptor_model` records with axes, bounds, current diversity
reference ids, a revision counter, dynamic-reference status, and the no-rebin
policy for insertion-time coordinates. Occupied-cell, elite, Pareto-frontier,
and metric-cell records now also persist the finite insertion-time descriptor
values keyed by configured descriptor axis, with restore-time validation for
finite values, unit interval bounds, record-order alignment, and axis-key
alignment. The descriptor model now also carries
`libreevolve.map_elites_descriptor_readiness.v1`, which keeps stable task
behavior descriptor contracts, learned/evaluator-provided descriptor models,
descriptor training inputs, restore-compatible descriptor revisioning, and
full/partial archive rebin engines false with restore-time overclaim
validation. Runtime manifests now include
`runtime.history.archive_descriptor_drift_audit`, which compares retained
snapshot descriptor values against accepted-history admission descriptors as
diagnostic-only evidence. This is evidence for the current local boundary, not
proof of AlphaEvolve-grade behavior descriptors or archive rebin semantics. The
committed
`papers/map_elites_descriptor_boundary.json` sidecar keeps this insertion-time
descriptor snapshot scope machine-validated.

AlphaEvolve island-state note: retained archive-state changes advance the
island round-robin assignment cursor. Non-admitted MAP-Elites attempts, such as
`not_improving_cell`, record their attempted island but do not consume the next
island slot. Final manifests now persist a compact
`runtime.history.archive_state` snapshot with the current cursor and adjacent
sequence counters, and `archive_events.jsonl` persists versioned migration
placement events. The same manifest snapshot now includes `archive_contents`
with per-island MAP-Elites cells, elite-program ids, descriptor policy, and
archive configuration, plus `topology_policy` schema
`libreevolve.island_topology_policy.v1` for configured synchronous ring
migration with a configurable island count and five-island default. That policy
keeps adaptive island counts, non-ring topologies, and AlphaEvolve-identical
policy readiness false. `load_archive_restore_bundle()` combines that manifest
state with accepted `history.jsonl` records, and
`ProgramDatabase(..., archive_state_snapshot=..., archive_programs_by_id=...)`
can restore both the cursor/counter subset and the cell/elite contents. CLI
full-runtime restore now composes that compatible archive restore bundle with
the runtime RNG, LLM scheduler, budget, and controller-budget replay surfaces;
bundle validation keeps resumed-trace proof readiness false, and ordered
migration-event replay plus async/provider-output/pending-work resume remain
part of the broader resume gap. The committed
`papers/archive_event_replay_boundary.json` sidecar keeps the current
archive-state snapshot restore plus audit-only event reconciliation scope
machine-validated apart from ordered archive-event restore-engine support.
`papers/controller_pending_work_resume_boundary.json` separately preserves the
terminal controller-state boundary for default synchronous and opt-in local
sampler/evaluator-async runs: finalization can validate zero queued/running/pending work
and checked full-resume unsupported surfaces, but runs do not checkpoint
controller queues, running evaluations, in-flight LLM calls, pending archive
admissions, provider handoff replay, or an end-to-end resumed trace.

AlphaEvolve rejected-diagnostics note: rejected archive-admission metadata is
kept JSON-safe, but hook-mutated/restored programs with non-finite top-level
fitness or metrics still cannot enter normal strict history. They are
diagnosed through invalid/quarantine streams until a finite rejected-candidate
stream or normalization policy is implemented.

AlphaEvolve execution-grounding note: completed manifests now include
`runtime.history.proposal_lifecycle_report` with schema
`libreevolve.proposal_lifecycle_report.v1`. The report merges generated
candidate history with generated failure records by candidate id and records
backend/call summaries, mutation payload hashes, evaluator validity, archive
admission or rejection, rejection reasons, execution-filtered counts, bounded
failure-memory linkage, and explicit false-acceptance/false-rejection review
status. `runtime.history.incorrect_suggestion_audit_report` also records
aggregate independent-rejudge coverage as explicit zero coverage for accepted
and rejected generated candidates. This supports a local claim that
execution/evaluation gates generated suggestions before accepted discovery
claims, while remaining short of an independent rejudge, cross-run proposal
table, sampled audit-denominator policy, candidate-family filter rates,
beyond-initial-pool novelty audit, or audited false-positive/false-negative
rate. The committed
`papers/proposal_lifecycle_audit_boundary.json`
sidecar now emits that `not_independently_audited` boundary, and
`validate_paper_manifest()` requires and validates it at the real repo root.
The committed `papers/incorrect_suggestion_audit_boundary.json` sidecar also
preserves the more specific local-execution-grounding boundary for
`runtime.history.incorrect_suggestion_audit_report`, including the same
sampled audit-denominator and beyond-initial-pool novelty gaps.

AlphaEvolve archive-history consistency note: accepted archive admissions
prevalidate their strict candidate history record before mutating the live
MAP-Elites/island archive. Malformed accepted records such as candidates with
non-serializable metadata fail before becoming best programs, parents,
inspirations, or migration sources. Rejected malformed top-level fitness or
metric records still use invalid/quarantine diagnostics as noted above.

AlphaEvolve objective-vector note: archive admission metadata and migration
events now preserve `objective_vector` records when normalized declared metrics
are available. These records expose the finite normalized metric vector and the
scalar selection policy used for `selection_score`, including per-metric
weights when configured. The
`libreevolve show` command now validates current-history objective vectors while
streaming and prints bounded normalized-metric summaries for the selected
retained row. Runtime manifests also persist
`runtime.history.objective_frontier`, a bounded diagnostic Pareto frontier over
complete declared normalized metric vectors, plus
`runtime.history.objective_metric_archives`, a bounded top-program view for
each declared normalized metric. Declared non-primary `source: plugin` metrics
can now be filled by plugin hooks as validated metric side effects before the
final objective annotation, and declared non-primary `source: final_fitness`
metrics can include the plugin-adjusted final score in the objective vector.
These records are audit evidence for the current scalar policy and
metric-specific tradeoffs, not frontier-driven archive replacement.
MAP-Elites `objective_archive_policy` snapshots now also carry
`libreevolve.map_elites_objective_archive_readiness.v1`, which keeps primary
Pareto/frontier archive replacement, durable cross-run metric databases,
metric-target persistence tables, and runtime feedback-calibration runners
false with validation that rejects overclaims. Runtime manifests also include
`runtime.history.objective_primary_archive_readiness`, an audit that counts
complete objective vectors, scalar primary archive cells, retained
Pareto/frontier programs, and metric-cell overlays while keeping those primary
archive readiness fields false. The committed
`papers/objective_archive_boundary.json` sidecar keeps this retained-overlay
and diagnostic-frontier scope machine-validated.

AlphaEvolve database-resurfacing note: bounded current-run resurfacing now exists
through `runtime.history.resurfacing_index`,
`ProgramDatabase.resurface_candidates(target_metric=...)`,
`resurface_by_metric()`, `resurface_by_lineage()`,
`resurface_by_descriptor()`, `resurface_by_novelty()`, and
`resurface_by_feedback()`. `runtime.history.hypothesis_index` also exposes
bounded redacted proposal idea/rationale/hypothesis summaries for valid
programs and can feed current-run resurfacing evidence.
`runtime.history.program_output_index` exposes bounded source/hash/preview
summaries for evaluator `outputs` / `program_output` payloads retained under
`evaluation.metadata.program_outputs`, and valid output-bearing candidates can
feed current-run resurfacing evidence. `resurface_by_program_output()` can
return defensive current-run candidates by exact output source key and/or
output hash. The committed `papers/program_output_boundary.json` sidecar keeps
this exact current-run output lookup scope machine-validated.
The committed `papers/evolutionary_database_boundary.json` sidecar now records
the broader current-run resurfacing boundary: append-only accepted/failure/
archive streams, manifest archive snapshots, bounded rank-fusion resurfacing,
and defensive current-run metric/lineage/descriptor/novelty/feedback/artifact/
hypothesis/failure/program-output query snapshots. It is not evidence of a
durable cross-run query store, schema-versioned database migrations, semantic
retrieval indexes, replayable sampling policies, cross-run failure memory,
learned novelty models, or AlphaEvolve-grade evolutionary database parity.
`runtime.history.artifact_index` exposes bounded evaluator artifact
path/hash/redaction/skipped/stage/content-excerpt evidence, and valid
artifact-bearing candidates can feed current-run resurfacing evidence. The
committed `papers/artifact_index_boundary.json` sidecar keeps this bounded
artifact metadata scope machine-validated apart from durable full-content or
semantic artifact search.
`runtime.history.hypothesis_branch_report` now groups generated candidates by
captured proposal text hashes and marks rejected/no-accepted branches as
`abandoned_evidence` with fallback-parent inference and failure-memory linkage.
`runtime.history.controller_backtracking_report` now records current-run branch
state transitions, audit-only unpromising-branch decision records, and observed
redirects from abandoned-looking branches to a later fallback parent or
alternative branch, while explicitly marking controller sampling effects and
causal controller backtracking proof as absent. The committed
`papers/controller_backtracking_boundary.json` sidecar now emits that
`observed_redirects_and_audit_decisions_without_controller_policy` boundary for
missing controller-owned unpromising-decision rules/thresholds, controller
branch-state machines, suppression/retry behavior, prompt-sampling suppression
effects, controller fallback-target selection, causal replay, and cross-run
branch tables, and `validate_paper_manifest()` requires and validates it at the
real repo root.
`runtime.history.proposal_diversity_report` also records exact proposal and
idea hash uniqueness/duplicate counts by generation and proposal batch, with
bounded sample records and an exact-text-only analysis policy. The committed
`papers/proposal_diversity_boundary.json` sidecar keeps that exact-text
duplicate-count scope machine-validated apart from semantic novelty,
near-duplicate detection, operator-family labels, distance metrics, novelty
contribution scoring, parent/inspiration relation evidence, prompt/backend
attribution, accepted/rejected status linkage, and model-ablation linkage.
`runtime.history.proposal_score_report` now records bounded outcome-linked
proposal quality plus exact proposal-signature novelty scores and deterministic
current-run lexical proposal-family diagnostics. This narrows the remaining
database gap to durable cross-run query/index tables, full
metric-vector and feedback/artifact-content/program-output ranking,
semantic output-similarity or schema-aware output retrieval, calibrated proposal
quality models, near-duplicate or semantic/cross-run novelty or hypothesis
retrieval, model-quality attribution, explicit controller-owned backtracking
policy, prompt/archive score-influence policy, suppression/retry policies,
schema migrations, and replayable sampling policies, not the absence of any
resurfacing API, proposal metadata capture, exact duplicate counts, or
branch-level abandonment, observed redirect, or proposal-score/family
diagnostic evidence. The committed `papers/proposal_score_boundary.json`
sidecar keeps this bounded current-run proposal-score and lexical-family scope
machine-validated.
`runtime.history.failure_index` groups failure records by exact fingerprint,
repetition, and recency with bounded records; the committed
`papers/failure_memory_boundary.json` sidecar keeps this run-local failure
diagnostics scope machine-validated apart from durable cross-run failure
tables, semantic failed-proposal retrieval, learned repetition avoidance,
replayable failed-mutation payloads, failure-aware sampling policy, and
cross-run failure-index migrations.

AlphaEvolve duplicate-work note: generated candidate ids include workspace-hash
identity provenance, and completed manifests now include
`runtime.history.duplicate_work_policy_report`, which groups identical
candidate workspaces and records a run-local evaluator cache for
diff-error-free exact workspace matches. Cache keys include canonical workspace
hash plus evaluator-contract hash; cache hits emit replayable
`candidate_evaluation_cache_hit` controller events and do not consume
evaluator-call budget. Completed runs also write
`duplicate_work_cache_index.jsonl`, a strict JSONL exact-workspace index with
one row per runtime program for audit and cross-run concatenation. Rows include
metric names and bounded evaluator-output signature hashes without retaining
raw evaluator payloads; the artifact is not a replay lookup engine. The
remaining gap is durable cross-run cache lookup, durable evaluator-result
storage, resume-spanning cache replay, cache invalidation/migration policy,
stochastic re-evaluation policy, semantic near-duplicate detection,
source-aware cache indexes, raw-output replay, and broader AlphaEvolve-grade
fixed-budget memory over previously explored programs. The committed
`papers/duplicate_work_policy_boundary.json` sidecar keeps this run-local
exact-cache plus durable bounded-output-signature index-export scope
machine-validated.

AlphaEvolve sampling-balance note: completed manifests now include
`runtime.history.sampling_balance_report`, which aggregates generated-candidate
parent/inspiration selection metadata into current-run explore/exploit,
strategy, metric-target, frontier, lineage, and per-generation decision counts.
It also records current-run selected-program repetition diagnostics and
fallback/source-pool provenance fields for inspiration strategy source, sample
kind, unknown-strategy counts, and excluded inspiration totals. The committed
`papers/sampling_balance_boundary.json` sidecar preserves that local telemetry
boundary. This narrows the remaining Section 2.5 database-balance gap to
island/cell/metric/lineage/descriptor coverage, repetition impact analysis,
score-improvement attribution versus diversity-effect analysis, equal-budget
strategy comparisons, and calibrated AlphaEvolve-grade database-balance policy
rather than absence of run-local sampling telemetry.

AlphaEvolve budget-accounting note: runtime manifests validate current-process
`RunBudget` counters, elapsed evaluator seconds, seed/candidate totals,
generation counters, and stop reasons before finalization. Restored-budget
loading, controller budget-event rows, and a composed runtime restore bundle
now exist for current manifests, with CLI forwarding through
`--restore-runtime-from-manifest` and controller-budget events pre-applied to
the restored `evolve()` budget snapshot. Provider-output replay, pending
controller work, direct event-stream consumption inside `evolve()`, ordered
migration-event replay, and end-to-end resumed-trace evidence remain open
before budget manifests can be treated as robust cross-process experiment
accounting. The committed
`papers/expensive_evaluation_budget_boundary.json` sidecar keeps the current
local cooperative budget scope machine-validated apart from per-candidate
compute-hour accounting, worker/accelerator lease accounting, async queue
budget accounting, partial long-evaluation resume, wall-clock versus
compute-hour compression, and equal-budget benchmark execution reports.

AlphaEvolve environment-provenance note: manifests record Python/platform
metadata, `pyproject.toml` status/hash, the selected execution-identity PEP 621
subset (`project.name`, `project.version`, `project.requires-python`, license,
authors/maintainers, keywords, classifiers, project URLs, optional dependency
groups, scripts, and arbitrary entry-point groups), bounded extra `[project]`
metadata records for unselected/unknown keys, build-backend metadata, and
installed versions for declared runtime dependencies, bounded
installed-distribution name/version snapshots with bounded parsed `WHEEL`
metadata plus redacted/hash-backed `direct_url.json`, `INSTALLER`, and
hash-only `RECORD` metadata, plus
hash-only records for known project-root lockfiles (`requirements.txt`,
`requirements.lock`, `uv.lock`, `poetry.lock`, `pdm.lock`, and `Pipfile.lock`).
They also record a bounded/redacted `pip_freeze` snapshot with a raw
`pip freeze --all` stdout hash, bounded/redacted `pip_config` evidence with a
raw `pip config list` stdout hash, NumPy availability/version and bounded,
redacted `show_config()` preview metadata with a full captured-config hash,
built-in LLM provider SDK package versions plus adapter API modes, and bounded
accelerator runtime hints/probes. The manifest-visible
`environment_reproducibility_policy` hashes those bounded evidence surfaces and
explicitly scopes unsupported surfaces, including broader non-project build
provenance, complete private package-source interpretation, live provider
service/API versions beyond false capability-readiness fields, live provider
pricing/default-rate capture beyond configured estimates, and accelerator
budget/accounting semantics. The committed
`papers/release_artifact_reproducibility_boundary.json` sidecar preserves the
CI-smoke-only release-artifact boundary: wheel/sdist build checks and
install-from-wheel CLI smoke checks exist with complete `libreevolve/`
package-tree wheel and sdist inventory inspection plus CI-generated
artifact/source hash provenance and uploaded release-smoke artifacts, while
the local release-smoke checklist is documented. Signed release provenance,
published-index verification, and maintainer-approved release readiness remain
absent.
The committed `papers/release_checklist_documentation_boundary.json` sidecar
preserves the release-checklist documentation boundary: required local smoke
bullets, out-of-scope signed/published/approved release bullets, workflow
markers, provenance-tool markers, cross-document anchors, focused tests, and
active TODO ownership are recorded. It also maps each local checklist bullet
to release-artifact workflow evidence and maps release-provenance JSON fields
to the local provenance writer, while signed release provenance,
published-index verification, maintainer release events, and owner review
signoff remain absent.
The committed `papers/ci_workflow_coverage_boundary.json` sidecar preserves
the current path-scoped GitHub Actions boundary: manual dispatch,
push/pull_request path filters, secret scan, Python 3.11/3.12 unit jobs on
Ubuntu, Windows, and macOS, optional integration tests, and a committed-manifest paper/docs job exist,
with paper-source, manifest, docs, and boundary verifier tests, plus a
release-artifact smoke job exists, while CI local-PDF paper-manifest checks,
fully semantic docs-claim verification beyond the committed verifier suite,
signed release provenance, cross-platform paper/docs, release, and integration
coverage, branch policy, and notification policy remain absent.
The committed `papers/documentation_truthfulness_boundary.json` sidecar
preserves the current cross-document documentation guard boundary: README,
ROADMAP, papers-index, TODO-ledger, path-filter, paper-manifest consistency,
TODO-coverage, stale source-specific wording, sidecar-registry, and focused
boundary-test evidence exist, including README AGENTS operational drift
inventory for example-directory and run-artifact-list mismatch evidence. The committed
`papers/documentation_claim_inventory.json` sidecar adds top-level README,
ROADMAP, and papers-index claim ids with file-offset evidence anchors, local
evidence-ref existence records, and Markdown fragment-anchor resolution records,
plus audited surface heading records and uncovered heading-to-claim gap records,
with active TODO-owner links, while complete README/ROADMAP/papers index
coverage, semantic documentation claim verification, complete implementation-
evidence mapping, stale completed-entry detection, generated alignment reports,
and full proof that every AlphaEvolve-facing claim is current remain absent.
Named AlphaEvolve source coverage is represented by
`papers/alphaevolve_source_inventory_boundary.json`, which verifies the pinned
44-page PDF hash and page count plus 55 named spans, 57 page-local anchors, 38
structural spans, 14 numbered figures, and 3 numbered tables. The bounded
`papers/alphaevolve_system_requirement_inventory_boundary.json` adds 50
PDF-anchored implementation requirements covering all eight Table 1 rows,
Sections 2.1-2.6, and Figures 1-3. It classifies 13 requirements as locally
implemented, 30 as partial, 2 as not implemented, and 5 as not demonstrated,
and verifies live domain TODO ownership for all 37 incomplete rows. The committed
`papers/alphaevolve_context_claim_inventory_boundary.json` adds 41 exact-page
claims from the Abstract, Introduction, Discussion, and one Acknowledgements
sentence. It classifies 6 as locally implemented, 11 as partial, 4 as not
implemented, and 20 as not demonstrated, with live TODO ownership for all 35
gaps. `papers/alphaevolve_matrix_result_claim_inventory_boundary.json` adds 41
exact-page claims from Section 3.1, all sixteen selected Table 2 rank rows,
Figure 4, and footnote 3. It classifies none as locally implemented, 6 as
partial, 3 as not implemented, and 32 as not demonstrated, with live TODO
ownership for all 41 gaps. The committed
`papers/alphaevolve_math_result_claim_inventory_boundary.json` adds 63 exact-
page claims from Section 3.2 and Figure 5, including all nine displayed result
pairs, constructive-math method claims, named outcomes, artifact availability,
and collaboration provenance. It classifies 2 as locally implemented, 16 as
partial, 4 as not implemented, and 41 as not demonstrated, with live TODO
ownership for all 61 gaps. It also verifies that a previously attributed
blanket result-verification sentence is absent from the pinned source and that
the actual "In all these cases" sentence concerns simple/random starts.
`papers/alphaevolve_scheduling_claim_inventory_boundary.json` adds 45 exact-page
claims from the Section 3.3 opening, Section 3.3.1, and Figure 6. It classifies
19 as partial, 14 as not implemented, and 12 as not demonstrated, with live
TODO ownership for all 45 gaps. The inventory includes the scheduling problem,
vector-bin-packing formulation, ranking-only safety, simulator/held-out/
deployment claims, incumbent and deep-RL comparisons, exact heuristic terms,
heatmap axes, and legend semantics.
`papers/alphaevolve_kernel_claim_inventory_boundary.json` adds 59 exact-page
Section 3.3.2 and Figure 7 claims. It classifies 6 as partial, 37 as not
implemented, and 16 as not demonstrated, with live TODO ownership for all 59
gaps. It covers the JAX/Pallas context, Figure 7 semantics, tiling formulation,
baseline workflows, shape collection and splits, real-TPU evaluation claims,
quantitative results, deployment, and Gemini self-optimization. Together the
six bounded inventories disposition 299 claims: 21 locally implemented, 88
partial, 64 not implemented, and 126 not demonstrated. The corrected
`papers/implementation_evidence_map_boundary.json` records six broad requirement
anchors for markers, prompt sampling/creative generation, evaluation,
evolution, distributed execution, and published benchmark coverage with 81
existence-checked source-span/module/test/sidecar/TODO references. This is not a
whole-paper sentence-, paragraph-, equation-, footnote-, citation-, or detailed
Sections 3.3.3-5/remaining-exhibit/appendix claim inventory, per-phrase evidence-link
sufficiency proof, coverage detector,
generated code-audit report, or CI exhaustiveness gate. The checked
`papers/status_claim_inventory.json` sidecar records row-level paper-index
status inventory with status text hashes, status classes, local artifact
mention source offsets and existence records, row source lines, TODO evidence
path source offsets and existence records, and status-cell phrase hashes with
source offsets plus candidate evidence-link lists and row-specific TODO content
matched source tokens, block hashes/source offsets, artifact-mention source
offsets plus phrase-local TODO block records, but it is not phrase-level semantic proof or
absence-sentence freshness proof. The checked
`papers/benchmark_coverage_inventory.json` sidecar records structural
implemented-benchmark coverage bullet entries with source lines, hashes,
file character offsets, source-token match file offsets, local-artifact mention
file offsets, artifact-existence records, limitation-signal terms/source offsets/counts, and
contradiction flags, but it
is not semantic proof that each bullet is sufficient or fresh.
Environment provenance is useful
package name/version, selected and extra `[project]` metadata, known-lockfile
hash, pip-freeze and pip-config hash/preview, installed-distribution `WHEEL`
tag and source/install metadata, NumPy config summary, provider SDK-version
evidence, bounded accelerator runtime hint/probe evidence, and audit-only
policy evidence rather than complete reproduction evidence or restore-checked
proof that a later evaluator runtime can replay the original
build/package/hardware boundary.

AlphaEvolve artifact-schema note: current `manifest.json` and JSONL run
streams are strict local machine-readable formats with explicit v1 schema
metadata. `manifest.json` carries top-level `schema_version` and
`artifact_schema` fields, and current `history.jsonl`, `failure_history.jsonl`,
`archive_events.jsonl`, `llm_calls.jsonl`, `prompt_history.jsonl`, and
`controller_budget_events.jsonl` rows carry `schema_version` plus
`record_schema`. Legacy histories without those fields remain readable for
`show` and accepted-history restore helpers, but the remaining AlphaEvolve gap
is stable resumable database compatibility: versioned migration rules,
branching/upgrade policy, and tests proving old and current run artifacts can
be safely rebuilt into durable query/resume views.
The committed `papers/jsonl_durability_boundary.json` sidecar separately
records strict JSONL append durability scope: finite strict JSON serialization,
append-side torn-final-record repair, newline-terminated writes, fsync,
quarantine diagnostics, retention modes, per-line reader validation, default
fail-closed handling for newline-missing final records, opt-in read-side
repair, and strict-reader coverage for show/archive/controller/manifest/plugin
paths. It also records helper-managed advisory interprocess append
serialization, Windows/POSIX lock selection, stable stream/quarantine lock
ordering, and a subprocess concurrent-writer test. It is not evidence of
semantic append-order ownership, crash-atomic repair/quarantine transactions,
or AlphaEvolve-grade durable async run-state parity.

AlphaEvolve best-export note: CLI runs now append a post-`evolve()` manifest
record under `runtime.best_artifact_export` after best-artifact export
succeeds or fails. The record distinguishes completed core evolution from
post-run materialization, includes redacted failure diagnostics, and refreshes
`best.py` / `best_workspace` artifact records with hashes when available.
CLI best export also refuses symlink or Windows-junction visible, temporary,
and backup artifact paths before replacement or cleanup.
When replacement recovery fails, rollback/cleanup errors are recorded as
secondary redacted diagnostics and unrestored backup paths are preserved and
listed.
Direct `evolve()` calls still return the best program without materializing
those files.

AlphaEvolve plugin-provenance note: runtime manifests now include
`runtime.plugin_state`, which separates configured plugin labels from loaded
runtime plugin identities and records direct-API mismatches. Core `evolve()`
now resolves built-in `Config.plugins` labels/spec mappings when explicit
plugin objects are omitted, and CLI runs validate those specs before overwrite
cleanup. Entry-point plugins now record configured paper-inspiration labels,
manifest-safe or declared-schema constructor options, constructor signature
shape, and distribution name/version plus hash-only RECORD/WHEEL metadata when
available. Arbitrary direct-plugin constructor value capture, direct-plugin
schema policy, versioned custom plugin registries, and richer custom package
provenance remain open; direct custom plugin constructor signature shape is
recorded without values, and direct-plugin policy readiness keeps those direct
surfaces false.

AlphaEvolve prompt-config provenance note: startup manifests retain
prompt-bearing config through a redacted, bounded, hash-backed policy.
`prompt_variants`, `prompt_format_options` alternative text, `critique_prompt`,
and feedback grader `prompt` strings redact known credential-shaped values and
record original SHA-256, length, retained length, redaction, and truncation
metadata. Safe prompt text can still appear in local manifests, so manifests
remain local reproducibility records rather than public reports.

AlphaEvolve LLM-request note: built-in OpenAI, Anthropic, and Ollama adapters
send each rendered mutation, critique, feedback, or meta-prompt as a single
user message/input item. LibreEvolve records model, output-token limit, API
mode, OpenAI `reasoning_effort`, normalized provider-supported request
parameters, prompt/output hashes, and scheduler telemetry. Built-in backend
specs validate and forward `temperature`, `top_p`, supported stop sequences,
and supported request seeds, and call telemetry persists the effective
normalized values. Those fields are request telemetry and best-effort sampling
controls, not proof of deterministic provider-output replay across backend
families, API modes, model revisions, or repeated identical calls. Call
telemetry also persists `backend_defaults` for
LibreEvolve's effective local output-token caps, provider internal retry caps,
configured request timeouts, API modes, and OpenAI reasoning/API-mode policy;
provider diagnostics reject remote default/default-rate capture overclaims, but
remote provider-side defaults and pricing are not inferred. Diagnostics also
keep live provider pricing, provider default-rate capture, and account/model-
specific pricing readiness false. The committed
`papers/provider_pricing_boundary.json` sidecar preserves the configured-cost-
estimate boundary while keeping live provider pricing, provider default-rate
capture, account/model-specific pricing, and raw provider-payload replay
absent. The committed `papers/provider_diagnostics_replay_boundary.json`
sidecar preserves the bounded provider-diagnostics boundary while keeping raw
provider-payload sidecars, provider-output replay, complete provider-call
replay, and account/model default capture absent. The committed
`papers/llm_stochastic_reproducibility_boundary.json` sidecar preserves the
request-telemetry boundary while keeping backend/API-mode seed semantics,
provider revision stability, repeated-call fixtures, output-match reports, and
deterministic provider-output replay absent. Structured
system/developer/user prompt roles, when configured, are retained as hash-only
`prompt_role_policy` metadata rather than raw instruction text, and are not
yet joined into the primary-prompt instruction report. Endpoint/client context now has an
explicit validated built-in backend surface for OpenAI `base_url`,
`organization`, and `project`, Anthropic `base_url`, Gemini `api_version`, and
Ollama `host`, and
accepted values are recorded in manifests plus call `client_context`
telemetry. Omitted fields still inherit SDK/environment defaults, so
unconfigured proxy hosts, organizations/projects, API hosts, and local Ollama
server selection remain outside self-describing artifacts. Gemini now has a
first-class `google-genai` GenerateContent adapter with environment credential
preflight, explicit API-version context, request mapping, role instructions,
usage/default/error telemetry, strict completion handling, and Flash/Pro lane
classification. This does not establish AlphaEvolve's published Gemini 2.0
Flash/Gemini 2.0 Pro model-mix parity: live capability/model-registry and
account-availability checks, a credential-safe pair run, original endpoint
availability or a current-model substitution contract, calibrated scheduler
comparisons, and substitution-equivalence justification remain absent. The
committed `papers/gemini_provider_parity_boundary.json` sidecar preserves that
partial-readiness boundary for paper-manifest validation.
The committed `papers/config_validation_boundary.json` sidecar separately
preserves that current configuration validation is local effective-config
validation only: it covers CLI override precedence, local backend/plugin spec
checks, manifest config records, and credential/client-construction preflight,
but not live provider model-registry validation, service/API-version capture,
account model-availability proof, provider default discovery, or complete
plugin-specific schemas.
AlphaEvolve's Table 1 sample-count claim is also not yet reproduced: current
budgets and ablation schemas can
account for LLM calls and provider usage, but no report yet proves useful
target progress in thousands-scale generated/evaluated proposal counts versus
FunSearch-style much larger sample budgets or small-base-model alternatives.
The missing evidence includes fixed run seed/evaluator identity, fixed compute
budget definitions, target-definition provenance, score-direction and
normalization policy, target-attainment curves by logical sample and generated
candidate, target-hit indexes, replicate seed sets, variance/confidence
reports, matched-budget run groups, and cost/latency budget curves.
The committed `papers/sample_efficiency_boundary.json` sidecar preserves that
benchmark-level absence boundary while recognizing the current single-run
`runtime.history.sample_efficiency_report`.

AlphaEvolve's fast/strong model-mix claim is also not yet reproduced as an
experiment. Current `throughput_depth` call telemetry can record backend
cost/latency/depth metadata, min/max normalization, fast-breadth and
strong-depth lane labels, eligible lane traces, and explicit
`claim_ready: false` lane evidence. The committed
`papers/fast_strong_model_mix_boundary.json` sidecar preserves that
metadata-trace-only boundary while keeping reserved lane policies,
experiment-level selection traces, candidate throughput/quality outcomes, and
equal-budget comparisons open.

Candidate-abstraction evidence is also still missing: the primary row records
LibreEvolve's code-file-set abstraction as a current divergence, but Section
2.1 and the Discussion describe choosing between direct solution search,
constructor functions, bespoke search algorithms, and paired solution/search
representations, with different biases for symmetric and non-symmetric
problems. The committed candidate-abstraction sidecar preserves this absence
boundary across per-abstraction APIs, selection policy, prompts, validators,
archive descriptor mapping, migration, and paired solution/search support;
LibreEvolve still needs benchmark metadata and equal-budget reports that
justify and compare those abstraction choices.

Code-scale evidence is separate from workspace mechanics. AlphaEvolve Table 1
reports evolving entire code files, hundreds of lines, arbitrary languages, and
multi-component algorithms. LibreEvolve currently has task-primary bounded
multi-file text workspaces, topology mutations, materialization diagnostics,
full-workspace prompt/export paths, a small `workspace_math` smoke fixture, and
a non-comparable local expression build/runner fixture, but it lacks a
paper-facing benchmark/report with hundreds-line generated programs, coupled
cross-file/component edits, dependency-graph validation, non-Python or
real-toolchain/replayable-build execution, evaluator budget evidence, validity/admission/
retention curves, retained artifact hashes, reproducibility bundles, and score
progress on a realistic codebase-scale task. The committed
`papers/codebase_scale_benchmark_boundary.json` sidecar preserves this Table 1
code-scale absence boundary for paper-manifest validation.

Table 1 exhibit evidence is also separate from capability parity. LibreEvolve
can preserve the FunSearch-versus-AlphaEvolve comparison table as a runtime
source-table exhibit with stable row ids, source location, cell text,
row-to-gap mappings, and rendered artifact hashes. The committed
`papers/table1_capability_exhibit_boundary.json` sidecar records that this is
not benchmark proof for the individual code-scale, language, evaluator,
sample-efficiency, model-scale, rich-context, or multi-metric rows.

Workspace materialization diagnostics are also scoped: typed
`CandidateMaterializationError` reasons, bounded paths, casefold collisions,
recursive link preflight, and static source-copy hash checks are local
file-workspace evidence. The committed
`papers/workspace_materialization_boundary.json` sidecar preserves the missing
portable static source-copy identity, bulk directory operation diagnostics,
generated dependency graph diagnostics, language/build-runner artifact
diagnostics, remote/container mount diagnostics, paper-facing invalid-workspace
fixture rows, and future-surface reason/path contract proof.

LLM feedback artifact note: successful and failed feedback records can keep
compatibility `raw_response` and parsed `feedback` previews, suppress them to
hashes, or suppress text and hashes according to `feedback_retention_mode`.
Companion retention metadata records mode, policy, SHA-256 hashes when enabled,
original/stored character counts, caps, and redaction/truncation flags. This
narrows prompt-history leakage risk. Generated mutation prompts,
critique prompt/mutation metadata, feedback raw/parsed outputs, successful
provider output text, provider error text, and plugin context text now have
configurable history retention modes (`full`, `redacted`, `hash_only`, or
`off`). Meta-prompt mutation evidence and DeepResearch retrieval bodies now
have the same configurable retention mode family; meta-prompt evidence
defaults to `hash_only`, while DeepResearch retrieval bodies default to
`redacted`. Framework-owned quarantine record snapshots now follow
`quarantine_snapshot_retention_mode`; replay retention remains open.

AlphaEvolve prompt-fidelity note: configured prompt seed variants are validated
for renderability and `{task}` support, but they can intentionally omit parent
code/workspace, inspiration or failure context, feedback, proposal metadata,
and mutation-format instructions. That compatibility path should be treated as
user-responsible prompt engineering, not evidence that every configured seed is
AlphaEvolve-faithful. The built-in mutation instructions now include the
AlphaEvolve-style same-response consistency contract for multi-edit proposals,
but configured prompt variants can still omit it. Evolved prompt children retain
the placeholders used by their parent template, so the current retention policy
preserves only the channels present in the selected parent prompt.
`runtime.history.prompt_example_copy_report` also inventories built-in mutation
example sentinels and records exact, normalized file-section-region, and simple
example-format skeleton copy signals from generated payloads. This keeps
concrete examples usable while exposing copied illustrative fragments as
diagnostic evidence; custom-template inventories, broader semantic/renamed
copy detection, and hard or configurable acceptance policy remain open. The
paper-facing boundary is tracked by `papers/prompt_example_copy_boundary.json`.

AlphaEvolve proposal-capture note: LibreEvolve treats leading proposal metadata
as a structured mutation-response preamble. Short `IDEA:`, `RATIONALE:`, and
`HYPOTHESIS:` fields and bounded multiline `[IDEA]...[/IDEA]`,
`[RATIONALE]...[/RATIONALE]`, and `[HYPOTHESIS]...[/HYPOTHESIS]` blocks are
stored as proposal metadata, while ambiguous wrapped colon-style metadata
before later proposal markers is rejected before mutation application rather
than silently becoming candidate code. LibreEvolve also captures bounded,
redacted natural-language explanation before the first structured mutation
marker as separate explanatory-preamble metadata; when it follows structured
proposal metadata, a blank line separates the two surfaces. Prose between or
after mutation sections remains rejected. The committed
`papers/natural_language_preamble_boundary.json` sidecar preserves the
bounded-leading-capture-only scope, so raw full-replacement disambiguation and
broader rationale-quality/proposal-memory handling remain open.

AlphaEvolve mutation-mode note: LibreEvolve implements canonical diff parsing,
configured `full` replacement, and opt-in `adaptive` per-candidate selection.
The adaptive policy resolves the prompt contract from workspace characters,
text-file count, Python evolve-block count, explicit task preference, and recent
same-parent selected-mode failures; critique validation and opposite-format
parser fallback use the selected contract. Candidate/failure metadata and
`runtime.history.adaptive_mutation_mode_report` retain selection reasons,
selected/effective modes, shape, failure, fallback, and mixed-mode evidence.
The committed `papers/adaptive_mutation_mode_boundary.json` sidecar classifies
this as partial Section 2.3 support: benchmark-calibrated thresholds, semantic
rewrite appropriateness, response-quality-aware policy, and equal-budget
diff/full/adaptive ablation remain absent.

AlphaEvolve multi-edit consistency note: LibreEvolve prompt instructions ask
models to keep same-response edits consistent, including matching new helpers,
config values, files, imports, and blocks with their definitions or topology
changes. Completed manifests now include
`runtime.history.mutation_consistency_report`, which records multi-edit
payloads, changed edit units, diagnostic co-change links, best-effort Python
AST symbol/reference summaries, unresolved-reference diagnostics, evaluator
status, and archive admission. This is current-run diagnostic evidence, not a
complete semantic verifier: language-aware scope resolution, config/resource
dependency models, required-companion-edit inference, cross-file dataflow, and
benchmark-calibrated consistency gates remain open. The committed
`papers/mutation_consistency_boundary.json` sidecar keeps this diagnostic-only
scope machine-validated.

AlphaEvolve scope-boundary note: the paper explicitly treats automated
evaluation as both a core advantage and a limitation, keeping tasks that require
manual experimentation out of scope and describing LLM-provided evaluation of
ideas as possible but not the optimized AlphaEvolve setting. LibreEvolve's
completed manifests now include
`runtime.history.automated_evaluator_scope_report`, which labels deterministic
machine evaluators as the candidate-validity owner, records optional LLM
feedback as post-evaluator feedback rather than a primary gate, excludes manual
experiment outcomes from candidate admission, and requires transition into
executable code feedback before scoring. The committed
`papers/automated_evaluator_scope_boundary.json` sidecar preserves that
machine-gradeable local-scope boundary. The runtime report now also includes
`libreevolve.automated_evaluator_environment_fixture_matrix.v1`, which records
observed local evaluator/runtime evidence and keeps robust-environment
criteria explicit as missing. Paper-facing scientific-discovery claims should
remain scoped to machine-gradeable evaluator workflows until robust
evaluator-environment fixtures, automatable-domain boundaries, setup/cost and
expected discovery-value evidence, manual-to-code transition policies, and
AI-Co-Scientist-style idea-stage contracts are implemented.

AlphaEvolve representation-boundary note: Related Work contrasts
AI-Co-Scientist's natural-language hypotheses and evaluation criteria with
AlphaEvolve's code candidates and programmatic evaluation functions.
LibreEvolve's completed manifests now include
`runtime.history.programmatic_representation_boundary_report`, which records
generated candidates as executable code workspaces, labels captured proposal
`idea`/`rationale`/`hypothesis` fields as natural-language context metadata,
and keeps declared evaluator metrics plus deterministic evaluator validity as
the programmatic criteria owner. The committed
`papers/programmatic_representation_boundary.json` sidecar preserves this
structural boundary. The report now also includes
`libreevolve.programmatic_representation_claim_matrix.v1`, separating observed
structural evidence from missing measured hallucination-risk, long-horizon,
natural-language-to-programmatic bridge, and proposal-truth evidence. The
report remains `claim_ready: false` for hallucination-resistance claims,
long-horizon evolution claims, and any full natural-language hypothesis stage
bridged into programmatic candidate evaluation.

AlphaEvolve run-inspection note: `libreevolve show` streams history rows and
validates ids, metrics, current-history evaluation shape, and archive
diagnostics, including malformed unselected retained rows. Its non-archive
source/workspace display path remains selected-row scope, but streamed
current and legacy history rows now validate `code`, `files`, and
`primary_file` payload shape before any best-looking row is printed. It still
does not summarize every unselected row's source/workspace payloads as
whole-run source integrity evidence. The committed
`papers/whole_run_source_workspace_integrity_boundary.json` sidecar preserves
the bounded retained-program integrity boundary for paper-manifest validation.

MAP-Elites cell-inspection note: `libreevolve show` rejects malformed current
history cells by arity/type/non-negativity and, when
`manifest.json.config.map_elites_bins` is present, rejects coordinates outside
that configured per-axis bin range. Histories without manifest/bin metadata
remain legacy-limited to arity/type/non-negative validation.

## TODO coverage cross-references

This maintained map ties each implementation-status row to backlog evidence.
The active column points only at currently open backlog files; grouped labels
are intentionally not accepted until a grouped-label taxonomy exists. Completed
files preserve implemented decisions and prior paper-index cleanups, and each
completed path is checked for source-specific completed checklist evidence.
The committed `papers/related_work_taxonomy_boundary.json` sidecar records the
separate Section 5 Related Work boundary: bounded taxonomy rows now cover
method family, representation, feedback/evidence mode, task stage, comparison
axis, proof/witness status, complementary-mechanism status, and local
implementation status. This remains non-ready for exhaustive reference-level
coverage, independent positioning review, local implementation parity,
benchmark reproduction, or release-ready AlphaEvolve positioning claims.
Source-specific active gaps now appear across
`docs/todo/code.md`, `docs/todo/papers.md`, `docs/todo/roadmap.md`, and
`docs/todo/readme.md`; completed evidence remains split by the completed-ledger
files listed below. This table is backlog traceability evidence, not a claim
that implementation-status prose is semantically complete.
The same manifest gate also checks active TODO bodies for a narrow stale
absence phrase family: a manifest-id-scoped claim such as `no source-specific
README TODO` is rejected when the referenced active ledger already has an open
TODO block for that paper id. This distinguishes missing implementation,
report, artifact, or evidence work from missing source-specific TODO coverage.

| ID | Active gap evidence | Completed evidence |
|---|---|---|
| 2506.13131 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2511.02864 | `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 1504.04909 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| auer-cesa-bianchi-fischer-2002 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |
| 2511.17592 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2510.14150 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2511.23473 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2602.10233 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2602.15951 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2603.14575 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2510.06056 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2601.21096 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.14718 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.05921 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.01794 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2602.23413 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2602.02919 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2606.06473 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.09764 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2601.10657 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.08520 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.20086 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.01120 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2604.01658 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.13821 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.09959 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.21605 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.29847 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.29293 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2512.18746 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2606.06114 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.27276 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2606.06324 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2606.05922 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.30621 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2604.25850 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.13357 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2605.21516 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2606.01770 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2603.28052 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2602.22425 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2602.16928 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2603.09172 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2509.18057 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2603.06692 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |
| 2601.16175 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |
| 2603.08679 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |
| 2601.01235 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |
| 2511.12916 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2601.05943 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2506.16750 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/roadmap.md` |
| 2505.16105 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |
| 2506.01896 | `docs/todo/code.md`; `docs/todo/papers.md` | `docs/todo/Completed/code.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |

## Benchmark coverage decisions

Implemented:

- `libreevolve/problems/examples/circle_packing`: AlphaEvolve-adjacent
  fixed-26 packing smoke fixture. It validates feasibility and optimizes summed
  radii, but it is not yet a repeated-seed benchmark with SOTA thresholds,
  construction artifact schemas, or report generation.
- `libreevolve/problems/examples/matrix_multiplication`: small reproducible
  2x2 multiplication-count smoke benchmark with evolve-block seed and
  validator. Its primary inverse-count metric is normalized across the full
  `1/count` range for counted scalar multiplications, and the validator rejects
  known import/library delegation, module-level dead-code counter, and fixed
  three-case lookup shortcuts. It is still not a tensor-rank decomposition
  benchmark.
- `libreevolve/problems/examples/workspace_math`: multi-file workspace smoke
  fixture with a nested Python package, declared JSON data, and a binary static
  seed asset. Its validator checks the workspace artifact shape and exact
  integer result while keeping the example smoke-only.
- `libreevolve/problems/examples/candidate_runner_expression`: non-comparable
  task-primary candidate-runner contract fixture. It selects a `.expr` primary,
  executes a local copy-build and expression adapter, captures the generated
  build artifact, and delegates metrics to the problem-owned Python validator.
  It is not a real-language/compiler/package-manager benchmark.
- `libreevolve/problems/examples/candidate_runner_c`: non-comparable host C
  compiler contract fixture. It resolves and probes `clang`, `gcc`, or `cc`,
  verifies a checked build-contract lock, compiles and executes one C11 seed,
  and retains toolchain/build provenance. It is not a compiler-optimization,
  hermetic-replay, or codebase-scale benchmark.
- `libreevolve/problems/examples/candidate_runner_python_oci`: non-comparable
  digest-pinned OCI interpreted-runner contract fixture. It verifies a checked
  lock, compiles and runs one Python seed in one immutable official image, and
  requires candidate network denial, read-only image rootfs, dropped
  capabilities, bounded resources, and runtime/image/provisioning identity
  evidence. Its live integration test is opt-in and is not multi-platform,
  remote-daemon, hostile-code, package-restoration, or benchmark certification.
- `libreevolve/problems/benchmarks/example_scope.py`: shipped-example scope
  registry that keeps `hello_world`, `sorting`, `workspace_math`,
  `embedded_evaluate_math`, `candidate_runner_expression`, `candidate_runner_c`,
  `candidate_runner_python_oci`, `matrix_multiplication`, and `circle_packing`
  smoke-only, while
  `sorting_network_8` and `sorting_network_9` remain non-comparable benchmark
  candidates. The standard paper-manifest validator checks these
  records through the committed `papers/example_benchmark_scope.json` sidecar.
- `libreevolve/problems/benchmarks/matrix_results.py`: AlphaEvolve-style
  matrix-result report contract. It validates target identity, dimensions,
  seed count, best rank, hit fraction, exactness-certificate status,
  coefficient domain, per-seed best-rank hits, top-level hit/best-rank
  consistency against per-seed records, artifact path/hash records, and an
  explicit `alphaevolve_comparable` policy that restricts paper-comparable
  claims to integer or half-integer coefficients with verified exactness,
  exact per-seed rows, and algorithm/certificate/notebook artifacts.
  `appendix_a_matrix_registry.py` adds the 54 AlphaEvolve Appendix A Table 3
  target identities and dimensions, and matrix reports for
  `alphaevolve_appendix_a` must match that registry.
  The same module now adds
  `libreevolve.alphaevolve_appendix_a_matrix_curation.v1`, a target-suite
  curation contract for the paper's rough size-selection wording, sorted
  representative policy, axis-permutation equivalent omissions, included-target
  rationales, and unspecified `p` cutoff. It still does not justify every
  possible excluded non-equivalent target.
  `papers/appendix_a_matrix_curation.json` emits that reported-suite curation
  record as a committed sidecar.
  `libreevolve.alphaevolve_appendix_a_matrix_excluded_target_curation_boundary.v1`
  records the current `not_recorded_locally` boundary for excluded
  non-equivalent target justifications and validates required future fields for
  excluded target ids, dimensions, exclusion class/reason, source basis,
  rough-rule and `p`-cutoff relations, symmetry-equivalence status, local
  attempt/resource-frontier refs, artifact paths, and hashes.
  `papers/appendix_a_matrix_excluded_target_curation.json` emits that boundary
  as a committed sidecar.
  `appendix_a_matrix_excluded_target_curation_boundary_from_records()` can
  build a recorded boundary from supplied excluded-target justifications and a
  declared coverage scope, but no broad excluded-target justification corpus is
  emitted yet.
  `libreevolve.alphaevolve_appendix_a_matrix_baseline_citation_boundary.v1`
  records the committed `papers/appendix_a_matrix_baseline_citations.json`
  sidecar for per-target best-known-rank citation provenance and validates
  cited reference id, source table/page, source artifact path/hash,
  applicability caveats, field/characteristic scope, and report-visible
  baseline-source refs.
  `appendix_a_matrix_baseline_citation_boundary_from_citations()` can build a
  recorded boundary from supplied citation rows and validates registry/source
  linkage. Local matrix reports still do not automatically attach those
  baseline-source rows.
  `libreevolve.alphaevolve_matrix_subset_scope.v1` records the paper-facing
  matrix subset boundary between `appendix_a_full` (`54` rows: `38` matched,
  `14` surpassed, `2` fell behind), `main_text_mnp_le_5` (`20` rows: `17`
  matched, `3` surpassed, `0` fell behind), and `table_2_selected` (`16`
  displayed rows: `2` matched, `14` surpassed, `0` fell behind). It validates
  inclusion predicates, target ids, outcome counts, out-of-scope rows, and
  Table 2/Table 3 source linkage.
  `papers/appendix_a_matrix_subset_scope_artifacts.json` now emits the three
  subset-scope artifacts with nested subset evidence, artifact path, and
  SHA-256 digests.
  `libreevolve.alphaevolve_matrix_subset_scope_artifact_boundary.v1` records
  the emitted sidecar and validates required artifact fields for subset
  identity, inclusion predicates, source linkage, counts, fell-behind/
  out-of-scope ids, nested subset-scope evidence, artifact paths, and hashes.
  `appendix_a_matrix_subset_scope_artifact_boundary_from_records()` can build
  emitted artifacts from subset evidence and validates nested linkage, but
  local report/table exports still need automatic subset-scope attachment.
  `libreevolve.alphaevolve_appendix_a_matrix_row_notes.v1` records the
  Appendix A Table 3 concurrent-work note for `mm_4x5x6`: reference `[49]`
  also found a rank-90 algorithm for `<4, 5, 6>`, independently matching
  AlphaEvolve's rank. It validates the target, source page/table, note text,
  relationship, and non-exclusive-priority docs caveat.
  `papers/appendix_a_matrix_row_note_artifacts.json` now emits the row-note
  caveat artifact for `concurrent_work_rank90_mm_4x5x6`, with nested row-note
  evidence, artifact path, and SHA-256 digest.
  `libreevolve.alphaevolve_appendix_a_matrix_row_note_artifact_boundary.v1`
  validates the emitted sidecar and required artifact fields for note identity,
  target/rank/reference values, source text, caveat flags, nested row-note
  evidence, artifact paths, and hashes.
  `appendix_a_matrix_row_note_artifact_boundary_from_records()` can build
  emitted artifacts from row-note evidence and validates nested linkage, but
  local report/table exports still need automatic row-note attachment.
  `libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1` records the
  paper-source larger-target boundary for sizes beyond `<5,5,5>`, 1000 random
  seeds, single-GPU evaluators, frequent OOM, and further-optimization need.
  `papers/appendix_a_matrix_resource_frontier.json` emits that paper-only
  boundary as a committed sidecar.
  `libreevolve.alphaevolve_appendix_a_matrix_local_resource_frontier.v1`
  separately records the current absence of local matrix scaling attempts plus
  the fields required for measured GPU memory, OOM artifacts, reduced-seed
  tradeoffs, and exclusion rationale; it does not provide those local attempts
  or artifacts.
  `papers/appendix_a_matrix_local_resource_frontier.json` emits that local
  absence/readiness boundary as a committed sidecar.
  `appendix_a_matrix_local_resource_frontier_from_attempts()` can build an
  `attempts_recorded` boundary from supplied local attempt diagnostics, but no
  checked local larger-target attempt corpus is emitted yet.
  `write_strassen_2x2_publication_bundle()` provides one checked Strassen
  baseline for `mm_2x2x2` with canonical algorithm, certificate, notebook,
  report, and artifact inventory files. Those files are now pinned under
  `libreevolve/problems/benchmarks/artifacts/strassen_2x2_publication_bundle/`;
  `validate_strassen_2x2_publication_bundle()` and the paper-manifest gate
  verify the report/inventory hashes and regeneration parity against fresh
  helper output. This still does not provide discovered tensor-decomposition
  algorithms, certificates, or notebook exports across the full Appendix A
  target suite.
  `libreevolve.matrix_suite_publication_artifact_boundary.v1` records the
  current `not_generated_locally` boundary for suite-wide publication
  artifacts and validates required future fields for one generated record per
  registered Appendix A target: target tensor, algorithm, coefficient data,
  exactness certificate, notebook, per-seed report, embedded matrix-result
  report, artifact inventory, publication-bundle refs, artifact paths, and
  hashes. The paper-manifest gate validates this boundary.
  `papers/matrix_suite_publication_artifacts.json` emits that
  absence/readiness boundary as a committed sidecar.
  `matrix_suite_publication_artifact_boundary_from_artifacts()` can build the
  generated boundary from one record per registered target, with nested
  matrix-result report linkage checks, but no local process generates the full
  suite artifacts yet.
  `libreevolve.matrix_baseline_component_runtime_boundary.v1` now records the
  current `not_emitted_by_local_runner` boundary for Section 3.1-style
  starting-algorithm provenance and required future emitted fields for
  run/target ids, baseline program ids, initializer/reconstruction-loss/
  optimizer component records, Adam optimizer name/version/config, mutable
  component scopes, fixed component hashes, generation-0 metrics, mutation
  lineage, matrix-result refs, artifact paths, and artifact hashes.
  `papers/matrix_baseline_component_runtime_boundary.json` emits that
  absence/readiness boundary as a committed sidecar.
  `matrix_baseline_component_runtime_boundary_from_components()` can build an
  emitted boundary from a component inventory and validates ref/scope/hash
  linkage, but local matrix runs still do not emit those baseline component
  records automatically.
  `libreevolve.matrix_cascade_run_runtime_boundary.v1` now validates
  emitted Section 3.1-style repeated-seed matrix cascade traces for
  run/target/seed ids, cascade ids and versions, stage traces with
  threshold/rank/exactness/stop diagnostics, accepted final rank, candidate and
  matrix-result refs, artifact paths, and artifact hashes.
  `papers/matrix_cascade_run_runtime_boundary.json` emits four checked rank-7
  normal-pipeline traces as a committed sidecar.
  `matrix_cascade_run_runtime_boundary_from_matrix_result()` can build emitted
  records from declared seed rows plus per-seed stage traces, with final-stage
  linkage checks and aggregate best-rank/hit-fraction recomputation. The
  checked `libreevolve.matrix_cascade_fixture_report.v1` bundle executes a
  two-stage, four-seed 2x2 fixture with content-hashed test sets, promotes the
  rank-7 Strassen control, and rejects the rank-8 control at the main
  confidence-bound gate. The separate checked
  `libreevolve.matrix_evolution_fixture_report.v1` bundle runs four independent
  run-local `evolve()` calls, links every final candidate to its seed parent,
  records generation/evaluation/LLM-call budgets and compact histories, and
  reaches rank 7 through a scripted canonical mutation. This proves normal
  pipeline and report integration, not stochastic LLM rediscovery, empirical
  false-decision measurement, AlphaEvolve's tensor formulation, comparable
  search budgets, or Section 3.1 target-suite scale.
  `libreevolve.matrix_near_integrality_evidence.v1` now
  validates declared search-time evidence that candidates were instructed to
  produce near-integral decompositions, rounded to integer or half-integer
  coefficients, and linked to exactness certificates as in AlphaEvolve Section
  3.1. `libreevolve.matrix_near_integrality_runtime_boundary.v1` now records
  the current `not_emitted_by_local_runner` boundary and validates emitted
  records for run/target/candidate ids, seeds, prompt hashes/instructions, raw
  and rounded coefficients, rounding error, exactness-certificate links,
  matrix-result refs, artifact paths, and artifact hashes.
  `papers/matrix_near_integrality_runtime_boundary.json` emits that
  absence/readiness boundary as a committed sidecar.
  `matrix_near_integrality_runtime_boundary_from_evidence()` builds runtime
  rows from validated near-integrality evidence and checks row linkage back to
  nested target, prompt, candidate, rounding, and certificate evidence, but no
  local matrix benchmark runner emits those records yet.
  `libreevolve.matrix_scalar_field_evidence.v1` contract now validates declared
  scalar-field provenance for complex-valued algorithms, field characteristic,
  exact coefficient representation, finite-field caveats, and certificate scope
  for exact real/complex applicability.
  `libreevolve.matrix_scalar_field_runtime_boundary.v1` now records the
  current `not_emitted_by_local_runner` boundary and validates emitted records
  for run/target/candidate ids, seeds, scalar field, characteristic,
  applicability, coefficient representation, algorithm refs, certificate refs,
  matrix-result refs, artifact paths, and artifact hashes.
  `papers/matrix_scalar_field_runtime_boundary.json` emits that
  absence/readiness boundary as a committed sidecar.
  `matrix_scalar_field_runtime_boundary_from_evidence()` builds a runtime row
  from validated scalar-field evidence and checks linkage back to nested
  target, field claim, applicability, coefficient representation, algorithm,
  and certificate evidence, but no local matrix benchmark runner emits exact
  complex decomposition/certificate artifacts for those claims yet.
  `libreevolve.matrix_tensor_rank_evidence.v1` now validates declared rank
  claims that distinguish matrix-multiplication tensor decompositions from
  non-tensor multiplication algorithms, including tensor-identity certificate
  scope, recursive applicability, target-tensor links, exactness-certificate
  links, and source-note caveats for non-recursive algorithms.
  `libreevolve.matrix_tensor_rank_runtime_boundary.v1` now records the current
  `not_emitted_by_local_runner` boundary and validates emitted records for
  run/target/candidate ids, seeds, algorithm kind, rank, recursive
  applicability, certificate scope, tensor-identity status, target-tensor refs,
  exactness-certificate refs, matrix-result refs, artifact paths, and artifact
  hashes. `papers/matrix_tensor_rank_runtime_boundary.json` emits that
  absence/readiness boundary as a committed sidecar.
  `matrix_tensor_rank_runtime_boundary_from_evidence()` builds a
  runtime row from validated tensor-rank evidence and checks linkage back to
  nested target, rank claim, recursive-applicability, tensor-identity,
  target-tensor, and certificate evidence, but no local matrix benchmark
  runner emits those target-tensor/certificate artifacts yet.
  `libreevolve.matrix_headline_historicity_evidence.v1` validates declared
  provenance for the `mm_4x4x4` complex rank-48 headline, including
  characteristic-zero scope, 56-year first-below-49 wording flags, recursive
  Strassen rank-49 comparison, finite-field-only Fawzi rank-47 caveat, source
  refs, and links to result, scalar-field, tensor-rank, Figure 4, Figure 9,
  and companion Colab evidence.
  `papers/matrix_headline_historicity_artifacts.json` now emits the
  paper-facing rank-48 headline historicity sidecar with nested evidence,
  source refs, prior comparisons, evidence links, artifact path, and digest.
  `libreevolve.matrix_headline_historicity_runtime_boundary.v1` now records the
  emitted sidecar and validates emitted records for run/target/candidate ids,
  dimensions, headline rank/field values, source refs, prior comparisons,
  evidence links, matrix-result refs, artifact paths, and artifact hashes.
  `matrix_headline_historicity_runtime_boundary_from_evidence()` builds a
  runtime row from validated headline evidence and checks linkage back to
  nested target, dimensions, headline claim, source refs, prior comparisons,
  evidence links, and matrix-result provenance. Local matrix benchmark runners
  still do not automatically attach those headline/source/decomposition/
  certificate artifacts to run outputs.
  `libreevolve.alphaevolve_matrix_rank_table_exhibit.v1` validates declared
  Table 2 and Appendix A Table 3 matrix-rank table exhibits, including stable
  table ids, source page/caption links, selected/full-table membership, row
  order, rank values, outcome counts and color semantics, complex-valued row
  annotations, concurrent-note linkage, rendered table/source/OCR artifact
  hashes, and links to registry, subset, row-note, scalar-field, result, and
  companion Colab evidence. `papers/matrix_rank_table_artifacts.json` now
  emits the paper-facing Table 2/Table 3 artifact sidecar.
  `libreevolve.alphaevolve_matrix_rank_table_artifact_boundary.v1` validates
  that emitted sidecar and required artifact fields for table identity, source
  locations, rendered/OCR/source files, artifact paths/hashes, and nested
  table-exhibit evidence.
  `matrix_rank_table_artifact_boundary_from_exhibit()` can build emitted table
  artifacts from validated Table 2/Table 3 exhibit metadata and validates
  nested table linkage. Local report/export code still does not automatically
  attach the rendered table/OCR/source files to runtime outputs.
  `libreevolve.matrix_sweep_space_evidence.v1`
  now validates declared Figure 9-style sweep provenance for the evolved
  `sweep` function, user-provided `hyper` library identity, hyperparameter
  range declarations, sampled configuration ids, per-sweep losses/ranks, and
  linkage from selected sweep configurations to final decomposition and
  exactness-certificate artifacts. No local matrix benchmark runner emits
  those sweep-space records yet.
  `libreevolve.matrix_sweep_space_runtime_boundary.v1` now records the current
  `not_emitted_by_local_runner` boundary and validates emitted records for
  run/target/candidate ids, seeds, search-program refs, sweep function
  identity, hyper-library and hyperparameter declarations, sampled
  configurations, winning configuration, certificate/decomposition refs,
  matrix-result refs, artifact paths, and artifact hashes.
  `papers/matrix_sweep_space_runtime_boundary.json` emits that
  absence/readiness boundary as a committed sidecar.
  `matrix_sweep_space_runtime_boundary_from_evidence()` builds a runtime row
  from validated sweep-space evidence and checks linkage back to nested target,
  search program, `sweep` function, hyper-library, hyperparameters, sampled
  configurations, winner, and selected certificate/decomposition evidence.
  It also does not yet emit local Appendix A resource-frontier runs for larger
  targets: attempted sizes beyond the table, reduced-seed policies if any,
  measured accelerator/GPU memory profile, OOM/resource-exhaustion diagnostics,
  and explicit target-exclusion rationale.
- `libreevolve/problems/benchmarks/result_certification.py`: paper-result
  certification report contract. It separates local-validator records from
  paper-claim-ready independent certifications with claim scope, verifier
  independence, verdict, passed evidence, evidence-kind-specific artifact
  requirements, and hashed artifact records, but it does not execute
  independent certifiers or create deployment/reviewer evidence.
- `libreevolve/problems/benchmarks/systems_results.py`: systems held-out and
  reference-correctness report contract. It validates separate optimization,
  held-out, and reference-correctness gates with case-set hashes, sample
  counts/seeds, finite metrics, artifact hashes, passed-gate artifact-kind
  requirements, optional certification linkage that cannot contradict
  `alphaevolve_ready`, and readiness gating. Ready systems reports now also
  require `claim_calibration` records that map finite gate metrics to
  Section 3.3-style claim ids with metric names, units, baselines,
  denominators, comparison windows, aggregation methods, runtime/deployment/
  synthesis context, artifact refs, and source refs. They also require
  `application_provenance` records for application co-leads or domain advisors,
  domain reviewers, validation-infrastructure or data owners, production
  approvers, approval/deployment state, claim links, artifact refs, and an
  explicit boundary between local benchmark evidence and domain-owner validated
  production claims. Ready scheduling reports now also require
  `scheduling_formulation` records for online vector-bin-packing setup,
  CPU/memory resource dimensions, workload/capacity snapshots,
  stranded-resource objective, feature mapping, simulator input hashes, and
  artifact refs. They also require `scheduling_safety` records for feasible
  candidate-set source, ranking-only scope, external simulator/admission/
  placement boundaries, resource invariants, and artifact refs proving that
  evolved code only ranks machines already deemed feasible. They also require
  `scheduling_deployment_readiness` records for interpretable heuristic
  structure, debuggability/operator review, predictability checks, deployment
  ergonomics, rollout-risk controls, and comparison against less interpretable
  learned-policy baselines. The contract still does not provide real compiler,
  hardware, kernel, scheduling, or systems fixtures.
  `papers/systems_result_readiness_boundary.json` now also records Figure 6
  scheduling-heuristic exhibit artifacts and Figure 7 Pallas-tiling exhibit
  artifacts as required but missing Section 3.3 evidence. For kernel reports,
  it does not yet
  require Pallas/Gemini-style input-shape corpus provenance, deterministic
  train/eval split records, real TPU runtime measurement artifacts, baseline
  tiling-heuristic identity, or unchanged-operation correctness-by-construction
  evidence. They also do not yet preserve Pallas workflow-baseline evidence
  that distinguishes search-based autotuning, manual heuristics, and
  expert-hybrid baselines; retuning burden for input-shape changes; manual
  authoring/review effort; hardware-expertise assumptions; or model-developer
  ergonomics comparisons. They also do not yet prove the Gemini self-training
  interpretation of the deployed Pallas heuristic: no evidence row ties an
  optimized kernel to the same Gemini-family training workload that powered
  AlphaEvolve, a production rollout state, before/after training-time and
  kernel-runtime measurements, team-velocity evidence, or rollback/safety
  status. For hardware, ready hardware reports now require
  `hardware_rtl_eda_provenance` metadata for Verilog/SystemVerilog source
  boundaries, arithmetic-circuit identity, synthesis/PPA provenance, timing,
  power, and area constraints, equivalence and formal-verification evidence,
  designer validation, downstream synthesis-tool confirmation, RTL-stage
  workflow placement, standard-language trust/adoption rationale,
  integration target, and time-to-market impact. They also require
  `hardware_rewrite_provenance` metadata for the concrete TPU arithmetic-
  circuit rewrite: source/modified Verilog hashes, rewrite diff hash,
  component and matrix-unit context, semantic rewrite category, changed spans,
  removed-bit inventory, rewrite rationale, PPA linkage, verification linkage,
  and artifact refs. They also require `hardware_contribution_provenance`
  metadata for the broader Gemini-to-TPU claim: model-family relationship,
  AlphaEvolve run/backend identity, TPU generation, arithmetic-circuit
  identity, novelty basis, first-direct-contribution scope, integration
  milestone, hardware review signoff scope, synthesis-tool rediscovery caveat,
  confirmation flags, and artifact refs. The contract still does not emit real
  RTL source, before/after Verilog files, diff/AST artifacts, removed-signal
  inventories, synthesis/PPA, verification, designer-signoff,
  downstream-synthesis, upcoming-chip integration, Gemini attribution review,
  firstness/novelty evidence, or deployment-impact artifacts. For compiler-generated
  IR tasks, ready compiler reports now require `compiler_ir_provenance` and
  `compiler_stack_provenance` metadata for IR origin/editability constraints,
  compiler-generated/already-optimized baseline provenance, reference and
  input-generator hashes, numerical tolerance policy, per-edit reference-check
  records, final expert all-input signoff scope, workload/model configuration,
  FlashAttention/Pallas kernel identity, JAX pre/postprocessing boundaries,
  XLA lowering stage, hardware target, lowered-IR hash, optimization decision
  category, and artifact refs. They also require
  `compiler_adoption_provenance` metadata for existing-compiler bounded-use
  case adoption versus AlphaEvolve-in-the-compiler-workflow integration,
  target compiler/pass identity, use-case scope, optimization artifact hash,
  integration owner, reviewer scope, adoption state, rollout/revert state, and
  workflow handoff boundary. The contract still does not emit real
  FlashAttention/Pallas/JAX/XLA artifacts, lowered-IR files, randomized
  reference-check outputs, compiler integration patches, rollout evidence, or
  calibrated result-claim records mapping finite metrics to
  AlphaEvolve Section 3.3 magnitudes such as scheduling resource-recovery
  percentages, kernel speedups and training-time reductions, RTL PPA deltas,
  or compiler kernel/pre/postprocessing speedups with explicit units,
  denominators, baselines, aggregation windows, and runtime/deployment/
  synthesis context.
- `libreevolve/problems/benchmarks/benchmark_hardening.py`: anti-gaming
  hardening report contract. It validates protected benchmark signals,
  shortcut threats, protected-signal links for each shortcut threat, detector
  strategies, passed negative fixtures, and hashed hardening artifacts, but
  real benchmark runners still need to emit these reports from actual
  anti-gaming fixtures.
- `libreevolve/core/evaluator.py`: evaluation-cascade status. Configured
  stages support deterministic scalar and metric thresholds, samples, explicit
  seeds, retries, and stage/sample budgets. Completed manifests include
  `runtime.history.cascade_hypothesis_test_policy_report`, which records
  configured or fallback-inferred small-scale-filter/main-test roles and
  validates the current promotion boundary plus adjacent-stage candidate and
  denominator linkage. Stages can now opt into
  `one_sided_lower_confidence_bound` promotion tests that apply confidence-bound
  and p-value evidence to repeated samples, with optional sequential stopping
  and configured normal-approximation error-budget evidence. Stages can also
  opt into `binomial_success_rate` gates for Wilson-bound pass/fail repeated-
  seed evidence. They are still not complete AlphaEvolve Section 2.4
  hypothesis-testing cascades: benchmark-calibrated thresholds and
  repeated-seed fixtures remain open.
- `libreevolve/problems/benchmarks/ablation_results.py`: equal-budget
  ablation-result report contract. It validates the AlphaEvolve Figure 8
  full-system baseline plus the five component ablations, declared targets,
  exactly three seeds, required equal-budget fractions,
  finite scores, consumed-budget consistency, consistent budget unit/limit per
  seed curve and across all variants/seeds for each target, passed component
  assertions, hashed curve artifacts, Figure 8 target-family coverage for
  `matrix_tensor_decomposition` and `kissing_number_sphere_packing`,
  target-metric identity/direction/normalization, and per-target/variant/
  fraction mean/std curve summaries checked against the three seed records.
  The checked-in `No full-file
  evolution` variant records a validated non-equivalence boundary against
  AlphaEvolve's tensor-decomposition loss-function-only setup, and the
  `No evolution` variant records a validated prompt-history-unproven boundary
  for repeated same-seed prompting without evolutionary feedback. The
  `No context in the prompt` variant records a validated over-broad
  non-equivalence boundary against AlphaEvolve's explicit-context ablation, and
  the `Small base LLM only` variant records a validated telemetry-unproven
  boundary for single-small-base-model generation. The
  `No meta prompt evolution` variant records a validated lineage-unproven
  boundary for prompt-template and prompt-program mutation evidence, but no
  benchmark script emits these reports yet.
- `libreevolve/problems/benchmarks/ablation_exhibits.py`: AlphaEvolve Figure 8
  visual-exhibit metadata contract. It validates the stable exhibit id, the
  matrix and kissing-number panel ids, target-family mappings, exact paper
  legend labels including `Full method`, axis metadata, standard-deviation band
  style declarations, rendered artifact hashes, and links to ablation report,
  curve-summary, and raw-seed-trace artifacts.
  `figure8_exhibit_from_ablation_report()` builds that two-panel exhibit from
  a validated equal-budget ablation report plus declared rendered/source
  artifacts. It does not render plots or prove that benchmark scripts emitted
  those artifacts. The committed `papers/figure8_ablation_artifacts.json`
  sidecar emits the current Figure 8 rendered-artifact absence boundary, and
  `validate_paper_manifest()` requires and validates it at the real repo root.
- `libreevolve/problems/benchmarks/matrix_exhibits.py`: AlphaEvolve main-text
  Figure 4 matrix-discovery metadata contract. It validates the main-text
  exhibit id, paper page 11, caption linkage, 15-mutation caption count,
  `mm_4x4x4` rank-48 target mapping, left diff outline plus the top-right
  optimizer/initialization, middle-right loss, and bottom-right
  hyperparameter-sweep highlight regions, source-diff/rendered-region artifact
  hashes, semantic component coverage, and links to Figure 9, matrix result,
  sweep-space, exactness-certificate, and companion notebook evidence. It does
  not render or commit the Figure 4 artifacts, and it does not prove the
  accepted 15-mutation lineage.
  `libreevolve.alphaevolve_figure4_matrix_discovery_artifact_boundary.v1` now
  records the current `not_emitted_by_local_report_export` boundary and
  validates required future artifact/lineage fields for rendered Figure 4
  image, left diff outline, highlighted excerpts, paper text excerpt, region
  renders, source-diff artifacts, accepted 15-mutation lineage, artifact
  paths/hashes, and nested Figure 4 exhibit metadata.
  `papers/figure4_matrix_discovery_artifacts.json` emits that
  absence/readiness boundary as a committed sidecar.
  `figure4_matrix_discovery_artifact_boundary_from_exhibit()` can build emitted
  artifacts from Figure 4 exhibit metadata plus supplied accepted-mutation
  lineage and validates nested exhibit linkage, but local report exports still
  do not render or check in those artifacts.
- `libreevolve/problems/benchmarks/matrix_exhibits.py`: AlphaEvolve Appendix A
  Figure 9a-9c magnified matrix-diff metadata contract. It validates the three
  panel ids, paper pages 35-37, Figure 4 caption linkage, `mm_4x4x4` rank-48
  target mapping, ordered line spans, source-diff/rendered-image/OCR artifact
  hashes, semantic component coverage for optimizer, initialization, noise,
  clipping, loss, discretization, and sweep changes, and links to matrix
  result, sweep-space, exactness-certificate, and companion notebook evidence.
  It does not render or commit the appendix panel artifacts.
  `libreevolve.alphaevolve_figure9_matrix_diff_artifact_boundary.v1` now
  records the current `not_emitted_by_local_report_export` boundary and
  validates required future artifact fields for panel ids/order/pages, line
  spans, source-diff excerpts, rendered images, OCR text, panel-set artifacts,
  artifact paths/hashes, and nested Figure 9 exhibit metadata.
  `papers/figure9_matrix_diff_artifacts.json` emits that absence/readiness
  boundary as a committed sidecar.
  `figure9_matrix_diff_artifact_boundary_from_exhibit()` can build emitted
  artifacts from Figure 9 exhibit metadata and validates nested panel linkage,
  but local report exports still do not render or check in those panel
  artifacts.
- `libreevolve/problems/benchmarks/paper_artifact_roles.py`: AlphaEvolve paper
  artifact-role attribution and linkage-boundary contract, but concrete
  rendered figure and notebook artifacts are not yet linked. It validates the
  PDF page 23 contribution records for the paper-figure creator initials and
  the accompanying Google Colab assembler initials, with stable artifact ids,
  artifact types, creator/assembler roles, exact initials and ordering, source
  section/page metadata, and source phrases. `papers/paper_artifact_roles.json`
  emits those records as a committed paper-facing sidecar. The companion
  `libreevolve.alphaevolve_paper_artifact_linkage.v1` record is emitted in
  `papers/paper_artifact_linkage.json`; it marks rendered figure files and
  companion notebook/export artifacts as `not_yet_linked` while validating the
  digest/link/source-map fields required before artifact availability can be
  claimed. The paper-manifest gate requires both sidecars at the real repo
  root.
- `libreevolve/problems/benchmarks/paper_source_versions.py`: AlphaEvolve
  source-PDF version contract. It validates the cached `2506.13131` source row
  against the audited first-page header `arXiv:2506.13131v1 [cs.AI] 16 Jun
  2025`, including arXiv id, version, category, posted date, subject classes,
  submitted timestamp, DOI, author count, TeX source URL, arXiv license URL,
  floating and versioned URLs, expected header page/text, byte count,
  SHA-256 digest, and the policy that paper-claim audits must identify the
  source version.
  `papers/source_versions.json` emits that `2506.13131v1` row as a committed
  companion source-version manifest with docs/TODO claim-surface links, and
  the paper-manifest command validates both the companion file and the cached
  PDF header. The download manifests remain legacy PDF cache ledgers rather
  than widened source-version row schemas; row-identity and source-rights
  layers are emitted by `papers/row_identity.json` and `papers/source_rights.json`.
  It remains source-version evidence, not full bibliography normalization,
  source-use rights review, or publication-grade source metadata parity. The
  companion `papers/arxiv_abstract_snapshot.json` now pins the current
  abstract-page byte count, SHA-256 digest, retained HTML artifact path,
  normalized author list, subject classes, DOI URL, submitted timestamp,
  TeX-source URL, license URL, and submission-history entry.
  `papers/alphaevolve_datacite_doi_boundary.json`
  now pins a bounded DataCite API response summary with response byte count,
  SHA-256 digest, DOI, landing URL, title, creator count, publisher,
  publication year, resource type, schema version, registered timestamp, and
  version. `papers/alphaevolve_tex_source_boundary.json` now pins the arXiv
  e-print endpoint, retrieval date, HTTP status, gzip content type,
  content-disposition filename, byte count, SHA-256 digest, and
  `2506.13131v1` linkage.
  `papers/alphaevolve_current_version_boundary.json` now pins the floating
  abstract URL status/content/digest, confirms current version `2506.13131v1`,
  and records that the retained floating PDF artifact bytes/hash match the
  cached PDF.
  `papers/alphaevolve_cached_pdf_header_consistency_boundary.json` now pins
  cached-PDF first-page header extraction hashes and arXiv/title/rights
  markers for the retained AlphaEvolve PDF.
  `papers/alphaevolve_raw_http_headers_boundary.json` now preserves pinned raw
  HTTP response header lines for the versioned abstract, floating abstract,
  floating PDF, DataCite API, e-print archive, and license page.
  `papers/alphaevolve_doi_landing_resolution_boundary.json` now pins the DOI
  resolver `302` headers, redirect location, and final arXiv landing-page
  headers. `papers/alphaevolve_datacite_full_response_boundary.json` now
  retains the complete 15,905-byte DataCite API response body and validates its
  parsed DOI metadata fields.
  `papers/alphaevolve_tex_archive_retention_boundary.json` now retains the
  2,635,462-byte TeX/e-print archive artifact and validates its 58-entry member
  inventory. `papers/alphaevolve_license_page_html_retention_boundary.json`
  now retains the Creative Commons license-page HTML artifact and validates its
  bytes, hash, and key content markers.
  `papers/alphaevolve_metadata_extraction_script_boundary.json` now pins the
  reusable offline extraction script path, byte count, SHA-256 digest,
  import entrypoint, CLI command, and retained source artifact coverage for
  abstract HTML, cached PDF, DataCite full response, license HTML, and TeX
  archive inputs. `papers/alphaevolve_source_refresh_gate_boundary.json` now
  pins the deterministic/live refresh-gate script and the scheduled/manual
  GitHub Actions `source_refresh_gate` job that compares live
  arXiv/DataCite/e-print/license responses against committed source
  boundaries. `papers/alphaevolve_source_refresh_run_2026-06-14.json` now
  archives one successful manual live-network refresh run with six matched
  source responses and a canonical run-report hash. The scheduled/manual
  workflow now writes `alphaevolve_source_refresh_report.json` and uploads it
  as the `alphaevolve-source-refresh-report` artifact.
  `papers/alphaevolve_source_refresh_promotion_boundary.json` now records the
  decision not to relabel older per-source snapshot sidecars as standalone
  refresh-ready evidence, mapping each central-gate source id to the paper
  sidecars it covers. Scheduled CI refresh-run history remains open.
  `papers/alphaevolve_license_page_boundary.json` now pins the Creative
  Commons BY-NC-ND 4.0 license URL, retrieval date, HTTP status, content type,
  byte count, SHA-256 digest, title, license family, and version while keeping
  automated license-page refresh open.
- `libreevolve/problems/benchmarks/paper_source_identity.py`: paper-cache row
  identity evidence. It validates `papers/row_identity.json`, whose 24 source
  records emit manifest row id, URL source id where available, local filename
  source prefix, identity-check booleans, and the AlphaEvolve row's link to
  `papers/source_versions.json` and source-rights layers. It remains base
  id/URL/file identity evidence, not source-use rights review or bibliography
  normalization.
- `libreevolve/problems/benchmarks/paper_source_rights.py`: AlphaEvolve source-
  PDF rights contract. It validates the cached PDF page 1 rights line
  `© 2025 Google DeepMind. All rights reserved`, rights holder/year, source
  page/location, manifest row hash/bytes, lack of an open-license declaration
  in the cached PDF, the fact that the arXiv license URL is recorded in
  `papers/source_versions.json`, the bounded license-page digest now in
  `papers/alphaevolve_license_page_boundary.json`, and the retained
  license-page HTML artifact in
  `papers/alphaevolve_license_page_html_retention_boundary.json`. It keeps
  boundaries separating third-party paper-source
  rights from LibreEvolve's MIT license and the companion repository's
  Apache/CC licensing.
  `papers/source_rights.json` emits that source-rights row with
  reproduction-policy requirements for excerpts, tables, figures, quotes, and
  appendix claims, and the paper-manifest command validates the companion file
  against the current cached PDF text.
- `libreevolve/problems/benchmarks/paper_bibliography.py`: AlphaEvolve
  References-section inventory and normalized bibliography contract. It
  validates the cached PDF marker inventory for pages 23-32 and
  `papers/references.json`, whose 120 rows use the PDF References text through
  the reference 120 continuation on page 33, preserving raw citation text,
  author/title/venue/year fields, DOI/URL/arXiv fields where detected,
  local-cache linkage, and citation-use categories. It is normalized
  bibliography metadata, not complete per-claim citation linkage.
- `libreevolve/problems/benchmarks/companion_sources.py`: AlphaEvolve companion
  Colab source-evidence contract. It validates the pinned
  `google-deepmind/alphaevolve_results` commit, `mathematical_results.ipynb`
  raw/Colab URLs, SHA-256 digest, byte count, nbformat, cell count, readability
  status, matrix and constructive-math claim mappings, the official notebook's
  Appendix B `result_row_boundary` inventory of `19` expected result ids,
  improved-results-only selection policy, matched-result exclusions, runtime
  AlphaEvolve-code absence, and the companion repository's Apache-2.0 software /
  CC-BY-4.0 materials licensing plus disclaimer boundary.
  `papers/companion_sources.json` emits this committed external source row with
  docs/TODO claim-surface links and local-cache policy, and the paper-manifest
  gate validates it. Companion selection-scope records distinguish included
  improved-over-SOTA claims from matched-but-not-outperformed companion
  absences, preserve verifier-code availability and runtime-code absence, and
  are validated by matrix result/headline reports for the `mm_4x4x4` companion
  claim. Companion artifact-rights rows attach to generated matrix artifact
  reports and inventories, distinguishing local generated artifacts from
  copied/adapted companion notebook code, verifier code, or construction data
  with Apache-2.0 / CC-BY-4.0 / local-project reuse policy, AS-IS disclaimer,
  non-official-product, and non-endorsement boundaries. It is external source
  evidence, not a local generated notebook or reproduced-result export.
- `libreevolve/problems/benchmarks/follow_on_sources.py`: follow-on
  AlphaEvolve mathematical-discovery source contract. It validates arXiv
  `2511.02864v3`, `Mathematical exploration and discovery at scale`, the
  2025-12-22 revision date, and the pinned
  `google-deepmind/alphaevolve_repository_of_problems` snapshot at commit
  `bfd224d0e7763f89eb4a8efe93ac126091f85ed9`, including README digest, live
  repository policy, declared 67-problem count, many-but-not-all notebook
  coverage, prompt/verifier/initial/final artifact kinds, runtime-code absence,
  source-use licenses, and citation boundary. `papers/follow_on_sources.json`
  emits this committed follow-on source row with docs/TODO claim-surface links,
  the cached
  `papers/2511.02864__Mathematical_exploration_and_discovery_at_scale.pdf` row
  (`12141713` bytes,
  SHA-256 `77b43844077c98c26dfc76ad391cadbbd53d48a1d290ddae575ff4d1bcdef9d2`),
  linked problem-coverage evidence for the declared-67 versus observed-68
  numbered-page boundary, and an Appendix B crosswalk mapping `19` original
  result ids across `13` families to follow-on problem pages and notebook-link
  statuses. It is later math-source evidence, not the original `2506.13131`
  specification, not a normalized Appendix B result ledger, and not a full
  notebook cell inventory.
- `papers/follow_on_repository_rights.json`: follow-on problem-repository
  source-use sidecar. It records the pinned repository's citation/BibTeX
  requirement, Google LLC copyright, Apache-2.0 software / CC-BY-4.0 materials
  split, artifact-type license mapping, AS-IS and non-official-product
  disclaimers, Gómez-Serrano/Tao role attribution, Problem 65's official IMO
  origin, docs/TODO claim-surface links, reuse policy, and validated
  artifact-rights templates for local generated outputs, adapted verification
  code, and copied problem statements. It is source-use provenance for the
  later problem repository, not original AlphaEvolve PDF rights,
  `alphaevolve_results` companion rights, or LibreEvolve licensing, and it
  records zero current copied/adapted follow-on repository material in
  LibreEvolve generated artifacts.
- `papers/follow_on_runtime_absence.json`: follow-on problem-repository
  runtime-absence sidecar. It records the pinned README/tree evidence for 28
  notebook paths, Git blob ids, byte counts, raw SHA-256 hashes,
  artifact-kind flags, scoped observed artifact presence flags from notebook
  cell titles, explicit AlphaEvolve-runtime absence, verifier-versus-runtime
  classification, and docs/TODO claim-surface links. It is runtime-availability
  provenance for the later problem repository, not evidence that the notebooks
  contain a runnable AlphaEvolve implementation or a full notebook cell
  inventory.
- `papers/follow_on_tao_blog.json`: Terence Tao follow-on blog source
  sidecar, not implementation-parity evidence. It records the November 5,
  2025 WordPress post URL, API post
  metadata, retrieval hashes, linked arXiv/repository/tool URLs, claim
  categories, source-line spans, and the evidence policy that blog-only
  commentary remains secondary until backed by pinned paper, repository,
  notebook, verifier, or proof artifacts.
- `papers/theoretical_cs_sources.json`: theoretical-CS AlphaEvolve
  proof-element source sidecar, not a local graph/certification benchmark. It
  records the September 30, 2025 Google Research article, arXiv
  `2509.18057v7`, cached PDF metadata, MAX-k-CUT gadget, random-graph/
  Ramanujan, and metric-TSP application rows, lifting-framework boundaries,
  verifier-speedup and final-brute-force-verification claims, and a
  `proof_element_artifact_boundary` with missing graph/gadget inventories,
  evolved verifier code, synthetic correctness datasets, judge-LLM/human
  inspection records, independent brute-force outputs, theorem-lifting
  metadata, baseline/SOTA rows, and source-repository status.
- `papers/official_deepmind_blog.json`: official DeepMind AlphaEvolve
  announcement sidecar, not white-paper specification or reproduced local
  evidence. It records the May 14, 2025 blog URL/date/title/team, retrieval
  hash, outbound white-paper/Colab/Early Access links, claim ids and
  blog-versus-paper value variants, blog-only availability statements, and
  announcement/illustration role metadata.
- `papers/alphaevolve_2026_impact_boundary.json`: official DeepMind
  AlphaEvolve 2026 impact sidecar, not original white-paper specification or
  reproduced local benchmark evidence. It records the May 7, 2026 impact
  article URL/date/title/team, retrieval hash, outbound source links, claim
  ids and values for DeepConsensus, AC OPF, Earth AI, Willow quantum circuits,
  public-gallery/math examples, TPU design, cache replacement, Spanner,
  compiler storage, Google Cloud customer cases, and UI/API attribution. It
  also records unsupported-local-benchmark flags for the named domains and
  keeps customer/deployment claims source-scoped until linked source snapshots,
  local fixtures, benchmark reports, independent verification, and operational
  lifecycle evidence for pilot-to-core adoption, regular-tool use, Google
  Cloud/commercial scope, UI/API artifacts, rollout owners, and release-note
  claim gates exist.
- `papers/alphaevolve_cloud_access_boundary.json`: official Google Cloud,
  Gemini Enterprise, and Google Keyword product/access sidecar, not local
  LibreEvolve provider support or original white-paper parity. It records the
  Google Cloud AlphaEvolve private-preview launch post, the AlphaEvolve Service
  API Early Access access model, Gemini Enterprise Preview/Pre-GA restricted
  access docs, account-team documentation boundary, and Keyword customer-impact
  context with retrieval byte counts and SHA-256 hashes. It keeps Cloud/API/
  Gemini claims source-scoped until Service API endpoint/schema and auth
  documentation, console/API/billing artifacts, customer availability, external
  account availability, security/data-use terms, managed-agent execution
  evidence, and a local Cloud AlphaEvolve provider adapter exist.
- `papers/alphaevolve_keyword_customer_boundary.json`: official Google
  Keyword one-year AlphaEvolve customer-impact sidecar, not Google Cloud
  customer availability or local managed-service support. It records the
  Keyword article URL/authors, retrieval byte count and SHA-256 hash, relation
  to the DeepMind impact article and Cloud private-preview post, science and
  Google-infrastructure claim separation, and four source-reported Google
  Cloud customer-impact rows for ML models, drug discovery, supply chains, and
  warehouse design. It keeps those claims source-scoped until named-customer
  source crosswalks, account-access evidence, UI/API/console/billing
  artifacts, geography/access-tier notes, rollout owners, independent
  availability checks, local customer-case fixtures, and local managed-service
  support exist.
- `papers/alphaevolve_ui_api_attribution_boundary.json`: official DeepMind
  AlphaEvolve impact-article UI/API attribution sidecar, not local UI or
  managed API support. It records the impact article URL/date/team, retrieval
  byte count and SHA-256 hash, the 13-person AlphaEvolve UI collaborator roster,
  the 14-person API and Google Cloud customer-engagement collaborator roster,
  role-category definitions, and artifact policy boundaries. It keeps the
  claims source-scoped until UI screenshots or source snapshots, interaction
  flows, API endpoint/schema inventories, Cloud customer-engagement artifacts,
  role-to-artifact links, public/private access status, privacy/contact
  redaction policy, independent artifact verification, and local UI/managed-
  API/customer-engagement adapters exist.
- `papers/alphaevolve_product_page_boundary.json`: DeepMind AlphaEvolve
  product/science page sidecar, not product availability or implementation
  evidence. It records the outbound `https://deepmind.google/science/alphaevolve/`
  reference from the impact boundary, the June 17, 2026 retrieval attempt, and
  the current HTTP 404/Not Found result. It keeps title/subtitle snapshots,
  navigation placement, outbound links, media assets, access or availability
  statements, product-page snapshot verification, independent availability
  checks, local LibreEvolve support, and managed AlphaEvolve compatibility
  claims open until a reachable source snapshot exists.
- `papers/alphaevolve_impact_claim_policy_boundary.json`: official 2026
  AlphaEvolve impact-claim normalization and release-note gate sidecar, not
  reproduction or release evidence. It emits one normalized row for each of the
  22 impact claim ids, carrying source URL/hash, raw value, value type, unit,
  baseline, comparison direction, approximation wording, result class, local
  fixture status, independent-verification status, downgrade wording, and
  `release_note_eligible=false`. It keeps every claim source-scoped until
  linked source snapshots, local fixtures, reproduction artifacts, customer
  confirmation where relevant, and independent verification exist.
- `papers/alphaevolve_impact_verification_matrix_boundary.json`: aggregate
  2026 AlphaEvolve impact verification/report matrix sidecar, not local
  benchmark or independent-verification evidence. It emits 22 impact-claim rows
  and 12 outbound-source rows with source URL, source artifact status, missing
  fixture/report paths, missing benchmark-report hashes, missing verifier/date/
  outcome evidence, customer-confirmation status, unsupported-local-benchmark
  flags, downgrade wording, and `release_note_eligible=false`.
- `libreevolve/problems/benchmarks/follow_on_coverage.py`: follow-on
  AlphaEvolve problem-repository coverage-state contract. It validates the
  pinned root-level status artifacts (`status.json`, `status_grid.png`, and
  `result_distribution.png`), parses the four explicit status buckets into 43
  listed problem ids, preserves 24 `not_listed_in_status_json` ids, records
  browser-page and many-but-not-all Colab access modes, and keeps the declared
  67-problem count separate from the observed 68 numbered HTML pages. It is
  status-artifact and bucket-membership evidence. It now classifies page 68 as
  an extra numbered duplicate-title `Logic puzzles` page outside the declared
  67-page navigation range, records all-page resource-link diagnostics (`36`
  GitHub notebook blob URLs, `6` direct Google Colab URLs, `25`
  under-construction Colab placeholders, `1` generic Colab landing URL, and
  `1` paper-link placeholder), pins raw-page byte counts and SHA-256 hashes
  for all 68 numbered HTML pages, emits per-page source rows with titles,
  paper sections, page URLs, hashes, link-status diagnostics,
  status-bucket labels, notebook-link mappings, notebook absence reasons,
  notebook SHA-256 hashes, and scoped artifact flags, and links to the
  runtime-absence record's 28 pinned notebook paths, but it is not a full
  notebook cell inventory.
- `libreevolve/llm/budget_report.py`: LLM role/retry budget report contract.
  It validates mutation, critique, and feedback role budgets, provider-internal
  retry attempts, token/cost/wall-clock limits and usage, persisted
  resume-state hashes, restored-state consistency, and paper-budget readiness.
  Runtime manifests now emit self-validated report instances with observed
  per-role usage and retained per-call provider retry details when LLM
  call-history rows are available. Runtime token/cost/time stop enforcement,
  restored runtime budget snapshot consumption, and emitted controller
  budget-event logs are wired, while queued/running async or pending-work
  budget consumption inside `evolve()`, provider-output replay composition, and
  hard provider cancellation remain open. The committed
  `papers/llm_budget_policy_boundary.json` sidecar preserves that cooperative
  budget snapshot boundary.
- `papers/llm_budget_policy_boundary.json`: LLM budget policy sidecar for
  AlphaEvolve Sections 2.2, 2.4, 2.6, and 4. It records
  `llm_budget_report` schema linkage, cooperative runtime budget policy,
  role-scheduler scope metadata, logical-call/retry/adapter-attempt usage,
  provider-token usage, configured-cost usage, retained-latency usage,
  controller budget-event replay, full-runtime restore budget pre-application,
  and resume-artifact inventory checks. It is not evidence of async role work
  queue budget accounting, queued/running/pending-work budget state, hard
  provider-cancellation budget state, provider-output replay for budget resume,
  accelerator or worker lease budget accounting, or experiment-owned quota
  policy.
- `papers/controller_pending_work_resume_boundary.json`: controller
  pending-work resume sidecar for AlphaEvolve Sections 2.5 and 2.6. It records
  the current `runtime.history.controller_state` terminal drained snapshot for
  default synchronous or opt-in local sampler/evaluator-async execution,
  zero pending-work validation, `controller_budget_events.jsonl` stream checks,
  controller-state artifact inventory, full-resume bundle validation,
  CLI/direct restore entrypoints, and unsupported-surface listing. It is not
  evidence of controller queue checkpoint schemas, queued proposal state,
  running evaluation state, in-flight LLM call state, pending archive admission
  state, partial-generation replay traces, async controller graph checkpoints,
  provider-output handoff replay, or end-to-end resumed trace proof.
- `papers/lineage_replay_boundary.json`: lineage replay sidecar for
  AlphaEvolve Sections 2.5, 2.6, and 4. It records validated
  `runtime.lineage_replay_policy` evidence for deterministic loop-created seed
  and generated candidate ids, deterministic PromptDatabase ids, ordered LLM
  call ids, direct `Program()` / `PromptProgram()` UUID4 exclusions,
  provider-output non-replay metadata, runtime RNG, LLM scheduler, archive
  snapshot, prompt-history replay linkage, and full-resume bundle policy
  validation. It is not evidence of provider-output replay in resumed traces,
  controller pending-work lineage state, ordered migration lineage replay,
  plugin or validator RNG state linkage, or end-to-end resumed lineage trace
  proof.
- `papers/runtime_rng_replay_boundary.json`: framework RNG replay sidecar for
  AlphaEvolve Sections 2.6 and 4. It records checked
  `python.random.mt19937.v1` runtime RNG snapshots, state hashes,
  `random.Random.setstate` restore, direct and CLI RNG restore entrypoints,
  seed-mismatch rejection, the runtime RNG replay-boundary schema, explicit
  framework-owned parent/prompt/database/island/MAP-Elites sampling surfaces,
  process-global RNG isolation, and full-resume bundle linkage. It is not
  evidence of LLM provider-output replay or resumed-trace exclusion, plugin
  internal RNG capture or resumed-trace exclusion, validator subprocess RNG
  capture or resumed-trace exclusion, controller pending-work RNG linkage, or
  end-to-end sampling continuity trace proof.
- `papers/validator_execution_boundary.json`: validator execution sidecar for
  AlphaEvolve Sections 2.4, 2.6, and 4. It records startup
  `policies.validator_execution`, per-attempt
  `evaluation.metadata.validator_boundary`, validator-boundary consistency,
  run-artifact boundary scans, local subprocess execution, candidate-root and
  declared-problem-file access policy, filesystem-capability metadata,
  validator network policy, Python socket-denial metadata, minimal environment
  and redacted-output secret boundaries, wall-clock timeout cleanup, and
  resource-limit metadata. It is not evidence of OS/container sandbox
  enforcement, kernel/container network egress control, OS-enforced filesystem
  capabilities, CPU/memory/GPU/disk/process quotas, native-extension network
  denial proof, or distributed evaluator-worker resume state.
- `papers/validator_artifact_promotion_boundary.json`: validator artifact
  promotion sidecar for AlphaEvolve Sections 2.4, 2.6, and 4. It records
  run-artifact validator-boundary consistency schema, manifest policy checks,
  history/failure stream scans, missing/mismatched/legacy row rejection,
  `libreevolve show` gate coverage, and stream/line diagnostics. It is not
  evidence of run-finalization enforcement, CI artifact-promotion enforcement,
  release-artifact promotion enforcement, historical bundle batch enforcement,
  or archival blocking policy.
- `papers/llm_role_scheduler_boundary.json`: LLM role-scheduler sidecar for
  AlphaEvolve Sections 2.1 and 2.6. It records configured role-backend
  routing, backend metadata role matching, reward-accounted roles, feedback
  reward wiring, role logical-call/provider/token/configured-cost/latency
  budget maps, per-call scheduler policy telemetry, opt-in role-scoped local
  UCB selection, role scheduler snapshots, restore validation, runtime LLM
  accounting summaries, and LLM budget report role budgets. It is not evidence
  of role-specific backend-pool policy, role-specific exploration parameters,
  reward normalization reports, outcome-attribution datasets, async role work
  queues, cross-role interference analysis, calibrated role reward policy,
  experiment-owned quota policy, fast/strong model-mix reports, resume replay
  experiment reports, or role-specific budget behavior reports.
- `papers/fast_strong_model_mix_boundary.json`: fast/strong model-mix
  sidecar for AlphaEvolve Section 2.3. It records the current
  `throughput_depth` metadata evidence: backend cost/latency/depth metadata,
  metadata normalization, metadata weights, neutral missing-metadata defaults,
  backend role/model-lane labels, fast-breadth and strong-depth lane detection,
  eligible-backend lane traces, per-call scheduler policy records, and
  explicit false claim-readiness lane evidence. It is not evidence of
  experiment-level selection traces, fixed compute budget identity, matched
  problem/seed/evaluator controls, provider-model identity for the fast and
  strong lanes, lane quota schedules, per-lane token/cost/latency accounting,
  lane switching traces, breadth-volume attribution, breakthrough-quality
  attribution, reserved fast-breadth or strong-depth lane policies, candidate
  throughput outcomes, candidate quality/depth outcomes, or equal-budget
  scheduler comparisons.
- `papers/adaptive_mutation_mode_boundary.json`: adaptive mutation-mode
  sidecar for AlphaEvolve Section 2.3. It records configured run-wide modes and
  partial adaptive per-candidate support: shape thresholds, task preference,
  selected-mode failure switching, parser/critique fallback, prompt/history
  metadata, selection telemetry, and short-full/large-diff executable tests. It
  is not evidence of benchmark-calibrated thresholds, semantic full-rewrite
  appropriateness, response-quality-aware selection, or equal-budget adaptive
  advantage.
- `papers/mutation_operator_boundary.json`: mutation-operator sidecar for
  AlphaEvolve Section 2.3 and Section 5 Related Work. It records the mutation-operator
  runtime report schema, fixed local parser surfaces, configured mutation
  mode, per-candidate adaptive diff/full flags, payload-surface counts, sample generated-candidate records, proposal
  metadata fields, and fixed edit grammar policy. It is not evidence of
  proposal-level operator-family provenance, LLM-constructed operator
  families, task/failure-aware operator construction, adaptive operator-family
  selection, operator-family scoring, or benchmark operator telemetry.
- `libreevolve/llm/cancellation_policy.py`: provider timeout/cancellation
  policy contract. It validates timeout/cancellation rules, role-scoped budget
  actions, artifact requirements, hard-cancel readiness gated on
  `cancellation_record` artifact evidence, and hashed cancellation artifacts,
  plus false runtime-readiness fields for live provider SDK cancellation,
  timeout-driven stop enforcement, and cross-run provider quarantine resume,
  but those runtime surfaces and richer cancellation artifacts beyond
  configured in-run quarantine observations remain open.
- `papers/provider_cancellation_boundary.json`: provider cancellation sidecar
  for AlphaEvolve Sections 2.4 and 2.6. It records validated provider request
  timeout rules, ensemble wait deadline rules, runtime deadline rules, declared
  hard-cancellation rules, role-scoped budget actions, artifact-kind
  requirements, cancellation-record artifact gates, hashed artifact inventory
  checks, runtime-readiness false fields, provider-cancellation observations,
  timeout failure call records, cancellation-record ledger replay,
  role/backend quarantine observations, and provider failure-policy summaries.
  It is not evidence of live provider SDK cancellation, in-flight cancellation
  handles, timeout-driven stop enforcement, cross-run provider quarantine
  resume, richer role-specific timeout artifacts, or provider-output
  raw-payload replay.
- `papers/provider_pricing_boundary.json`: provider pricing sidecar for
  AlphaEvolve Sections 2.6 and 4 fixed-compute-budget evidence. It records
  configured
  `cost_usd_per_million_tokens` backend metadata, provider usage
  `total_tokens`, per-call configured `cost_estimate` records,
  `cost_estimate_status` records, runtime configured-cost accounting, LLM
  budget report configured-cost totals, provider diagnostics summaries,
  pricing-readiness false fields, configured-pricing aggregate checks,
  cost-status reason checks, remote default-rate overclaim checks,
  backend-default count checks, and raw-payload replay overclaim checks. It is
  not evidence of live provider pricing, provider default-rate capture,
  account/model-specific pricing, or raw provider-payload replay.
- `papers/provider_diagnostics_replay_boundary.json`: provider diagnostics
  replay sidecar for AlphaEvolve Sections 2.2, 2.3, 2.4, and 4. It records
  provider usage
  metadata, request/response ids, finish reasons, adapter retry metadata,
  provider failure categories, provider status codes, bounded provider
  diagnostics, backend defaults metadata, retained call-history windows,
  provider-diagnostics summary schema, records hashes, raw-payload replay
  overclaim checks, remote provider-default overclaim checks, and
  backend-default count checks, plus an OpenAI Responses extraction
  sub-boundary for first-`output_text` extraction and status-as-finish-reason
  metadata and an Anthropic Messages extraction sub-boundary for first-text-
  block extraction and stop-reason-as-finish-reason metadata, plus an Ollama
  Chat extraction sub-boundary for non-empty `message.content` extraction with
  `done` and `done_reason` retained as metadata. It is not evidence of raw
  provider-payload sidecars, provider-output replay, complete provider-call
  replay, account/model default capture, OpenAI Responses multi-part text
  aggregation, non-completed status admission gates, incomplete-details
  classification, SDK output_text helper parity, Anthropic Messages multi-
  block text aggregation, stop-reason admission gates, mixed content-block
  classification, Ollama Chat done/done_reason admission gates, or Ollama
  response-shape validation.
- `papers/llm_stochastic_reproducibility_boundary.json`: stochastic
  LLM-generation reproducibility sidecar for AlphaEvolve Sections 2.2, 2.3,
  2.4, and 4. It records normalized request parameters, prompt/output hashes,
  backend/model/API-mode telemetry, supported sampling-control telemetry,
  provider-diagnostics boundaries, and provider-output replay boundaries. It
  is not evidence of a backend/API-mode seed-support matrix, provider model or
  system-fingerprint stability records, repeated identical-call fixtures,
  deterministic output replay, same-prompt same-parameter output-match reports,
  or cross-provider seed-semantics reports.
- `papers/feedback_calibration_boundary.json`: feedback-calibration sidecar
  for AlphaEvolve Section 2.4. It records the feedback calibration report
  schema, artifact-inventory schema, grader declarations, task-suite
  declarations, criterion-quality fields, safe artifact-reference validation,
  summary renderer, and schema validation tests. It is not evidence of runtime
  calibration runners, executed task-suite results, grader ablation results,
  or independent feedback-quality validation.
- `papers/critique_reviewer_pool_boundary.json`: critique reviewer-pool
  sidecar for AlphaEvolve front-overview critique wording plus Sections 2.4
  and 2.6 feedback/budget evidence. It records configured reviewer specs,
  manifest-safe reviewer names, optional reviewer prompts, reviewer role
  labels, role backend-routing and budget-accounting compatibility, bounded
  synchronous pool execution, first/last-valid aggregation, reviewer parser
  status, valid revision counts, selected reviewer provenance, reviewer
  elapsed seconds, reviewer outcome status, and inline runtime artifact policy.
  It is not evidence of async reviewer overlap, independent reviewer task
  definitions, reviewer/generator role separation proof,
  critique-to-revision attribution, reviewer score-to-selection policy,
  reviewer budget quota policy, reviewer failure-isolation reports,
  equal-budget no-reviewer comparisons, calibrated reviewer-score reports,
  reviewer reliability ablations, per-reviewer provider isolation, or external
  reviewer timeout artifacts.
- `papers/gemini_provider_parity_boundary.json`: Google/Gemini provider
  parity sidecar for AlphaEvolve Section 2.3. It records the first-class Gen AI
  SDK adapter, credential/API-version/request/role/completion contract,
  provider usage/default/error telemetry, Gemini-like custom-model detection,
  Flash/Pro lane classification, generic scheduler configuration, and false
  provider-parity readiness. It is not live capability or model-registry
  evidence, an account/model availability check, a credential-safe Flash/Pro
  pair run, proof that the original Gemini 2.0 models remain available,
  calibrated AlphaEvolve scheduling evidence, a paper-level substitution
  contract, or substitution-equivalence justification.
- `papers/prompt_section_packing_boundary.json`: prompt section-packing
  sidecar for AlphaEvolve Sections 2.2, 2.3, and 2.4 prompt-context,
  output-format, and multi-score prompt-diversity evidence. It records prompt
  caps, heuristic token estimates, provider token-counter hooks, mutation
  common-counter discovery, final-prompt role-counter discovery, prompt
  section-budget records, section-priority packing decisions, required-section
  fit status, provider-counter boundary fields, runtime prompt-section-packing
  coverage, mutation as the only current section-packed prompt role,
  critique/feedback/meta-prompt as final-prompt-boundary-only roles, bounded
  validator metadata summaries, and bounded evaluator artifact excerpts. It is
  not evidence of all-role provider-token section packing, exact non-OpenAI
  provider counters, registry/custom role section packing, retrieval/context/
  plugin/failure-memory section packing, or full validator-metadata prompt
  policy.
- `papers/stochastic_prompt_format_boundary.json`: stochastic prompt-format
  sidecar for AlphaEvolve Section 2.2. It records runtime evidence for
  stochastic prompt markers, configured `prompt_format_options`, normalized
  probabilities, selected alternative hashes, prompt/call linkage,
  weight-source boundaries, prompt-context override source, and run-local RNG
  replay. It is not evidence of separate distribution config source paths,
  source hashes, byte-count provenance, config precedence records,
  human-authored alternative provenance, author/reviewer metadata, revision
  history, or a paper-facing separate-file validator.
- `papers/systems_result_readiness_boundary.json`: systems-result readiness
  sidecar for AlphaEvolve Section 3.3. It records the systems-result report
  schema, artifact-inventory schema, evidence-bundle schema, optimization,
  held-out, reference-correctness, passed-artifact, domain-gate,
  claim-calibration, application-provenance, scheduling, compiler, and
  hardware readiness surfaces. It is not evidence of real scheduling, kernel,
  compiler, or hardware fixture runs, deployment measurements, expert
  confirmation, or domain-specific result artifacts.
- `papers/figure6_scheduling_exhibit_boundary.json`: Figure 6 scheduling
  exhibit sidecar for AlphaEvolve Figure 6 and Section 3.3.1. It records the
  required contract for stable exhibit rows, scheduling benchmark/candidate
  links, exact heuristic source artifacts and hashes, code identity maps,
  residual feature/unit definitions, residual grids, heatmap data, rendering
  parameters, rendered heatmap hashes, baseline heuristic identity,
  simulator/held-out/deployment report links, resource-recovery denominator
  windows, claim calibration, and scheduling-readiness linkages. It is not
  evidence that those artifacts have been emitted.
- `papers/figure7_pallas_tiling_exhibit_boundary.json`: Figure 7 Pallas
  tiling exhibit sidecar for AlphaEvolve Figure 7 and Section 3.3.2. It
  records the required contract for stable exhibit rows, kernel benchmark/
  candidate links, matrix product and dimension definitions, tile-parameter
  schemas, Pallas kernel identity, accelerator/memory/fusion/compiler context,
  shape-corpus and runtime report links, diagram source data, rendering
  parameters, rendered diagram hashes, baseline tiling heuristic identity,
  tiling-only correctness links, train/eval split linkage, claim calibration,
  and systems-readiness linkage. It is not evidence that those artifacts have
  been emitted.
- `papers/kernel_tiling_shape_corpus_boundary.json`: Pallas/Gemini kernel
  shape-corpus sidecar for AlphaEvolve Section 3.3.2. It records that generic
  kernel gates, claim-calibration records, application provenance, and
  certification references are not enough to claim Pallas parity. It is not
  evidence of collected input-shape corpora, source provenance, deterministic
  train/eval splits, shape-set hashes, real accelerator runtime artifacts,
  Pallas kernel source identity, expert baseline tiling heuristics,
  tiling-only candidate boundaries, unchanged-kernel-math evidence,
  correctness-by-construction scope, training-time linkage, deployment
  readiness, or shape-corpus-to-runtime joins.
- `papers/pallas_workflow_baseline_boundary.json`: Pallas workflow-baseline
  sidecar for AlphaEvolve Section 3.3.2. It records that kernel runtime and
  shape-corpus boundaries are prerequisites, but not evidence of baseline
  workflow classes, search-autotuning records, manual-heuristic records,
  hybrid-expert baselines, autotuning search-space or retuning policy,
  input-shape-change sensitivity, manual authoring/review effort,
  hardware-expertise assumptions, kernel-engineer workflow impact,
  model-developer ergonomics impact, baseline comparison artifacts,
  workflow-interruption evidence, or optimization-time reduction evidence.
- `papers/gemini_self_training_loop_boundary.json`: Gemini self-training loop
  sidecar for AlphaEvolve Section 3.3.2 and the Discussion. It records that
  Pallas deployment and kernel-runtime evidence are prerequisites, but not
  evidence of Gemini model-family identity, Gemini training workload identity,
  AlphaEvolve/Gemini relation, optimized Pallas kernel id, production rollout
  state, before/after training-time and kernel-runtime measurements,
  training-efficiency deltas, research or engineering velocity evidence,
  causal linkage to Gemini's training pipeline, rollback/safety status, or
  owner confirmation.
- `papers/hardware_rtl_eda_evidence_boundary.json`: hardware RTL/EDA evidence
  sidecar for AlphaEvolve Section 3.3.3. It records that hardware-domain
  report metadata is not evidence of exact RTL/circuit identity, source and
  modified Verilog/RTL artifacts, synthesis/PPA outputs, timing/power/area
  constraints, equivalence and formal-verification logs, designer signoff,
  downstream synthesis confirmation, RTL-stage timing, adoption rationale,
  integration target, deployment/time-to-market evidence, or artifact refs.
- `papers/hardware_rewrite_artifact_boundary.json`: TPU arithmetic-circuit
  rewrite sidecar for AlphaEvolve Section 3.3.3. It records that
  `hardware_rewrite_provenance` metadata is not evidence of exact circuit and
  matrix-unit identity, source and modified Verilog files, rewrite diff/AST
  artifacts, changed-span artifacts, removed-bit or signal inventories,
  per-bit PPA and verification linkages, PPA deltas, functional verification
  outputs, component review/signoff, or complete artifact refs.
- `papers/hardware_contribution_attribution_boundary.json`: Gemini-to-TPU
  attribution sidecar for AlphaEvolve Section 3.3.3. It records that
  `hardware_contribution_provenance` metadata is not evidence of Gemini
  model-family identity, AlphaEvolve run identity, producing backend identity,
  reviewed TPU generation or circuit identifiers, firstness/novelty review,
  integration milestone confirmation, hardware signoff files, synthesis
  rediscovery audit artifacts, mediation confirmations, or complete artifact
  refs.
- `papers/compiler_ir_reference_check_boundary.json`: compiler-generated IR
  reference-check sidecar for AlphaEvolve Section 3.3.4. It records that
  `compiler_ir_provenance` metadata is not evidence of real reference
  implementation artifacts, randomized input-generator artifacts, candidate
  edit sequences, per-edit reference-check outputs, randomized input coverage,
  tolerance/failure-policy artifacts, kernel/pre/postprocessing attribution,
  final expert all-input confirmation, or expert/owner signoff files.
- `papers/compiler_adoption_path_boundary.json`: compiler-adoption path
  sidecar for AlphaEvolve Section 3.3.4. It records that
  `compiler_adoption_provenance` metadata is not evidence of compiler patch or
  pass artifacts, bounded use-case integration records, integration-owner
  records, reviewer signoff files, adoption-state records, deployment or
  rollback logs, workflow-handoff artifacts, concrete existing-compiler
  adoption evidence, AlphaEvolve-in-compiler-workflow integration evidence, or
  complete adoption artifact refs.
- `papers/compiler_stack_context_boundary.json`: FlashAttention compiler-stack
  context sidecar for AlphaEvolve Section 3.3.4. It records that
  `compiler_stack_provenance` metadata is not evidence of workload/model
  records, FlashAttention/Pallas source artifacts, JAX pre/postprocessing
  wrappers, XLA lowering-stage outputs, hardware-target records, lowered-IR
  artifacts, memory-access/scheduling decision evidence, or complete stack
  artifact refs.
- `papers/documentation_truthfulness_boundary.json`: documentation
  truthfulness sidecar for the AlphaEvolve-alignment docs process. It records
  README, ROADMAP, papers-index, active/completed TODO-ledger, docs/README
  routing, GitHub Actions docs path-filter, paper-manifest consistency,
  TODO-coverage, stale source-specific wording, sidecar-registry, top-level
  README/ROADMAP/papers-index claim-inventory, backend CLI-provider guardrail
  inventory, backend-guide contract drift inventory, plugin-guide contract
  drift inventory, README Problem Layout inventory, problem-format loader-
  contract inventory, README Example Scope inventory, README example-runs
  inventory, README Run Artifacts inventory, README Testing inventory,
  README contributor-gate inventory, README license inventory,
  README ignore-policy inventory, README provider-example matrix
  inventory, README CLI-provider guardrail inventory, development-guide
  provider-example inventory, development-guide workflow inventory,
  configuration-guide inventory, and focused boundary-test evidence. It is not evidence of
  semantic documentation-claim verification, complete implementation-evidence
  mapping, stale completed-entry detection, generated alignment reports, or
  full proof that every AlphaEvolve-facing claim is current.
- `papers/docs_index_reader_path_boundary.json`: docs-index reader-path
  sidecar. It records `docs/README.md` reader paths, operational-guide routes,
  documentation-boundary markers, route target existence checks, target
  heading marker checks, and the whole-documentation AlphaEvolve-alignment
  cleanup marker. It is not semantic route-purpose verification,
  target-scope agreement verification, new-major-doc detection,
  misplaced-claim detection, or owner review signoff.
- `papers/docs_status_ledger_boundary.json`: docs-status ledger sidecar. It
  records the `docs/status.md` heading, implemented-today and important-limits
  bullet counts, status-signal terms, local backtick path existence checks,
  README/docs-index/papers-index/TODO route markers,
  `papers/documentation_claim_inventory.json` status-ledger fields, and
  `papers/status_claim_inventory.json` summary fields. It is not a per-bullet
  source/test/sidecar/TODO map, stale status prose detector, orphan status
  bullet detector, or owner review signoff.
- `papers/docs_architecture_runtime_flow_boundary.json`: docs-architecture
  runtime-flow sidecar. It records ten `docs/architecture.md` sections,
  runtime-flow markers, source path checks, README/docs-index route markers,
  the active TODO owner anchor, known-gap markers, the local sampler/evaluator-async
  runtime boundary, and the AlphaEvolve provider-parity boundary. It is not semantic
  flow-order verification, source-function semantic verification, runtime
  manifest field verification, architecture limitation freshness, or owner
  review signoff.
- `papers/development_provider_example_boundary.json`: development-guide
  provider-example sidecar. It records the two provider-backed
  `docs/development.md` commands, placeholder model-id guidance, explicit
  development run-name/overwrite markers, paired `show` commands for both
  examples, README provider model/failure wording, docs-index/backend/status/
  paper anchors, provider-matrix/auth/Gemini sidecar references, and active
  TODO ownership. It is not live OpenAI/Anthropic model availability proof,
  credential-safe development provider smoke, account-specific model-id
  provenance, a CI development provider matrix, or owner review signoff.
- `papers/development_workflow_boundary.json`: development-guide workflow
  sidecar. It records static `docs/development.md` workflow markers for
  Python launcher guidance, editable install, pre-commit setup, `.env`
  behavior, test/pre-commit/diff/paper-manifest commands, CI scope,
  release-checklist routing, dependency lists, repository conventions,
  suggested contributor docs, `pyproject.toml`, `.pre-commit-config.yaml`,
  GitHub Actions, focused agent-doc tests, and active TODO ownership. It is
  not per-command executable transcripts, dependency-version semantic parity,
  CI path-filter semantic proof, fresh-checkout paper-manifest transcripts,
  release-smoke transcripts, repository-convention source mapping, or owner
  review signoff.
- `papers/configuration_guide_boundary.json`: configuration-guide sidecar. It
  records static `docs/configuration.md` markers for precedence,
  `config.yaml` provenance, `.env` behavior, validator environment/network
  policy, representative `Config` fields, CLI override markers,
  backend/provider capability policy, OpenAI API-mode policy, focused
  agent-doc tests, status/paper sidecar anchors, active TODO ownership,
  resolved CLI-option records for the current `run` command surface, and
  resolved `runtime.llm_accounting` wording that routes live stop enforcement
  to `runtime.budget`. It is not a complete field/default map, complete CLI
  option-to-config map, YAML validation semantic map, manifest provenance
  field map, restore capability semantic map, CI configuration-doc drift gate,
  or owner review signoff.
- `papers/backend_cli_provider_guardrail_boundary.json`: backend
  CLI-provider guardrail sidecar. It records the `docs/backends.md`
  provider-lane taxonomy, built-in SDK adapter wording, custom import-path
  backend wording, subprocess/CLI-authenticated provider guardrail wording,
  custom CLI-wrapper limitation wording, the subprocess/CLI backend contract
  TODO link, missing CLI contract field markers, README TODO ownership, and a
  narrow scan for unsupported positive Codex/local CLI provider-support claims
  across backend, configuration, README, ROADMAP, and papers-index claim
  surfaces. It is not a first-class CLI backend contract, CLI backend manifest
  schema, credential-safe CLI backend smoke, CLI provider attempt accounting,
  or CLI provider diagnostics.
- `papers/backend_guide_contract_drift_boundary.json`: backend-guide contract
  drift sidecar. It records `docs/backends.md` section and claim markers for
  provider lanes, scheduler/reward accounting, call-history and
  `llm_calls.jsonl` replay, scheduler restore, prompt validation, provider
  metadata, role routing, provider failures, timeouts, OpenAI API-mode policy,
  credential preflight, custom backends, and CLI-provider guardrails, plus
  source-module, focused-test, sidecar, and active TODO anchors. It is not
  semantic backend-claim verification, a per-constructor-field evidence map, a
  per-telemetry-field evidence map, a backend-docs CI drift gate, or owner
  review signoff.
- `papers/plugin_guide_contract_drift_boundary.json`: plugin-guide contract
  drift sidecar. It records `docs/plugins.md` section, hook, execution-order,
  score/admission, artifact, fatal-failure, built-in plugin, entry-point,
  constructor-schema, package-provenance, and direct-plugin policy markers,
  plus `PluginBase`, registry, loop, config, built-in plugin, focused-test,
  sidecar, and active TODO anchors. It separates local synchronous hook support
  from AlphaEvolve-style plugin or agent parity, but is not semantic hook-
  contract verification, per-hook executable traces, a per-built-in plugin
  capability matrix, a plugin-docs CI drift gate, or owner review signoff.
- `papers/tracked_legacy_surface_boundary.json`: tracked legacy-surface
  sidecar for `old/**` planning material. It records the committed legacy
  Markdown inventory, archival/non-authoritative classification, self-
  classification banner, obsolete `alphaevolve/*` path signals, legacy
  checkbox-plan signals, README/docs routing, and `old/**` GitHub Actions
  path-filter coverage. It is not owner review signoff or evidence that
  archival plans are current implementation evidence.
- `papers/readme_agent_routing_boundary.json`: README AGENTS routing sidecar.
  It records the root README route, docs-index route, development-guide CI
  path scope, AGENTS.md operating-contract surface, `tests/test_agents_docs.py`
  coverage, GitHub Actions `AGENTS.md` path-filter coverage, and bounded
  command, test, backend, artifact, and AlphaEvolve instruction links. It is not a
  complete AGENTS instruction-drift map or owner review signoff.
- `papers/readme_agents_operational_boundary.json`: README AGENTS operational
  sidecar. It records current AGENTS.md drift for example problem directories
  and run-artifact names, plus README routing, run-artifacts guide anchors,
  backend/configuration/paper doc anchors, `tests/test_agents_docs.py`
  anchors, GitHub Actions AGENTS.md path-filter coverage, and active TODO
  ownership. It is not a complete instruction-to-source map, dependency-list
  semantic check, provider-guidance semantic check, full AlphaEvolve-scope
  semantic check, or owner review signoff.
- `papers/readme_documentation_map_boundary.json`: README Documentation Map
  sidecar. It records 11 README route records, target-existence checks, route
  summary marker checks, target heading marker checks, docs-index delegation,
  archival `old/` routing, and AGENTS.md routing. It is not semantic
  route-purpose verification, new-major-doc detection, misplaced-claim
  detection, or owner review signoff.
- `papers/readme_repository_layout_boundary.json`: README Repository Layout
  sidecar. It records 13 README layout entries, layout-entry path existence
  checks, summary marker checks, module evidence path checks, the `llm/`
  custom-backend marker, archival `old/` scope, and gitignored `runs/` scope.
  It is not semantic module-role verification, new top-level detection, new
  major-doc detection, AlphaEvolve-parity placeholder classification, or
  owner review signoff.
- `papers/readme_problem_layout_boundary.json`: README Problem Layout
  sidecar. It records the root README problem-layout block, required/optional
  file markers, the `docs/problem-format.md` route, loader/config/evaluator
  anchors, example problem path checks, focused loader/example test anchors,
  AlphaEvolve problem-surface sidecar anchors, and active TODO ownership. It
  is not semantic loader-contract verification, a dedicated minimal-problem
  smoke fixture, full problem-format long-contract drift validation, a new
  problem-surface detector, or owner review signoff.
- `papers/problem_format_loader_contract_boundary.json`: problem-format
  loader-contract sidecar. It records `docs/problem-format.md` section and
  claim markers for required layout, context manifests, codebase-integration
  metadata, task and metrics files, validator signatures, configured evaluator
  stages, candidate runner declarations, evaluation semantics, seed
  workspaces, seed policy, mutation modes, and unsupported runner scope, plus
  loader/config/evaluator, focused loader/evaluator/example test, example
  path, sidecar, and TODO anchors. It is not semantic problem-format claim
  verification, per-manifest-key executable traces, a docs CI drift gate, new
  problem-surface detection, or owner review signoff.
- `papers/readme_example_scope_boundary.json`: README Example Scope sidecar.
  It records README section markers, the shipped-example scope registry, the
  committed example-scope JSON sidecar, example path existence, smoke and
  benchmark-candidate classifications, sorting-network boundary anchors,
  benchmark fixture-readiness anchors, hardening and validator test anchors,
  status/papers index anchors, and active TODO ownership. It is not semantic
  scope-claim verification, runtime metadata comparison, a paper-comparable
  certification gate, new example-surface detection, or owner review signoff.
- `papers/readme_example_runs_boundary.json`: README example-runs sidecar. It
  records `examples/runs/README.md` markers, checked-in fixture history row
  counts, best-program markers, legacy artifact presence, modern artifact
  absence, documented `show` commands, CLI legacy-show anchors, run-artifacts
  guide anchors, focused CLI show test anchors, and active TODO ownership. It
  is not retained show-command transcript evidence, per-fixture behavior
  semantic verification, current run-artifact parity, AlphaEvolve-level
  reproducibility evidence, or owner review signoff.
- `papers/readme_run_artifacts_boundary.json`: README Run Artifacts sidecar.
  It records README section markers, the 14 common-output entries,
  run-artifacts guide anchors, the `RUN_ARTIFACT_NAMES` cleanup set,
  README-vs-cleanup mismatch lists, documented scope omissions for
  `task_specification.json`, invalid/quarantine streams, and
  `paper_artifacts/`, overwrite-cleanup test anchors, quick-start smoke
  artifact anchors, sidecar anchors, and active TODO ownership. It is not a
  fresh smoke-run artifact presence matrix, complete writer/reader/schema
  mapping, restore/show lifecycle proof, optional artifact classification
  gating, or owner review signoff.
- `papers/readme_testing_boundary.json`: README Testing sidecar. It records
  README non-integration and credential-gated integration command markers,
  pytest testpaths and integration marker registration, GitHub Actions non-
  integration and integration commands, Anthropic-key skip wiring, integration-
  test skip decorators, AGENTS.md command anchors, CI workflow sidecar anchors,
  and active TODO ownership. It is not Python/pytest version transcript
  evidence, selected or skipped test counts, credential-skip transcript proof,
  a failure-attribution matrix, or owner review signoff.
- `papers/readme_contributor_gate_boundary.json`: README contributor-gate
  sidecar. It records README Contributing markers, docs/papers/ROADMAP/TODO
  routing markers, focused-test and paper-manifest guidance, secret-scan
  baseline policy, allowlist-pragma policy, baseline-staging policy,
  development-guide secret-scan anchors, the pre-commit detect-secrets hook,
  `.secrets.baseline` detector inventory markers, GitHub Actions secret-scan
  and paper/docs jobs, existing agent-doc drift assertions, CI workflow
  sidecar anchors, active TODO ownership, and a bounded README contributing
  sentence-to-artifact map. It is not a pre-commit drift gate,
  source-boundary file-change detector, semantic secret-policy verifier, or
  owner review signoff.
- `papers/readme_license_boundary.json`: README license sidecar. It records
  the README License heading and MIT sentence, `LICENSE` file MIT text markers,
  pyproject license metadata, `papers/source_rights.json` policy markers,
  paper-source-rights module validators, paper-source-rights tests, and active
  TODO ownership while keeping third-party paper/source rights separate from
  LibreEvolve's MIT repository license. It also records a bounded
  source-rights claim-surface map from `papers/source_rights.json`. It is not
  packaged license-file verification, license metadata drift gating,
  paper-rights policy drift gating, or owner review signoff.
- `papers/readme_ignore_policy_boundary.json`: README ignore-policy sidecar.
  It records `.gitignore` ignore rules, paper-manifest allowlist rules, run-
  artifact local-only policy, paper-PDF local-only policy, README Repository
  Layout ignore markers, papers-index ignore-policy markers, GitHub Actions
  README/docs/papers/tests/pyproject/`.gitignore` path filters, existing agent-doc workflow
  assertions, active TODO ownership, and a rationale map for every expected
  ignore and allowlist rule. It also records resolved `.gitignore` workflow
  path-filter coverage. It is not tracked-vs-ignored sidecar inventory,
  retention-policy drift gating, or owner review signoff.
- `papers/readme_quick_start_smoke_boundary.json`: README quick-start smoke
  sidecar. It records the no-provider README command markers, focused smoke-
  test markers, expected `readme_smoke_sorting` run name, sorting example
  path, `max_llm_calls` stop reason, `Best fitness` output, and provider-
  preflight skip policy. The focused test executes the documented no-provider
  path, but this is not CI job integration, cross-platform shell transcript
  retention, fresh-checkout transcript retention, or owner review signoff.
- `papers/readme_install_smoke_boundary.json`: README install-smoke sidecar.
  It records the README editable-install command, Python launcher guidance,
  pyproject Python/dev-extra markers, GitHub Actions Python 3.12 setup,
  CI editable-install commands, and the development-guide editable-install
  command. It is not a clean-environment install transcript, Python and pip
  version record, dev-dependency import smoke, install-failure classifier, or
  owner review signoff.
- `papers/readme_provider_auth_boundary.json`: README provider-auth setup
  sidecar. It records the `.env.example` provider variables, placeholder
  safety, README provider-auth guidance, backend/configuration/development
  dotenv markers, CLI dotenv override and credential-preflight markers,
  integration-test credential skip markers, GitHub Actions Anthropic secret
  markers, and the secret-scan baseline marker. It is not complete
  backend-registry auth reflection, live provider account probes, a
  provider-auth drift CI gate, or owner review signoff.
- `papers/readme_provider_example_matrix_boundary.json`: README provider-
  example matrix sidecar. It records the README OpenAI, Anthropic, and Ollama
  placeholder command markers, account/local-model guidance, provider failure
  scope, `.env.example` provider placeholders, CLI `type:model` shorthand and
  built-in credential-preflight markers, custom-backend `class_path`/`kwargs`
  contract markers, configuration-guide shorthand markers, and the
  Anthropic-only credential-gated integration-test skip marker. It is not live
  OpenAI/Anthropic model availability proof, local Ollama inventory, a
  credential-safe provider smoke matrix, account-specific model-id provenance,
  a CI provider matrix, or Google/Gemini provider parity.
- `papers/readme_cli_provider_guardrail_boundary.json`: README CLI-provider
  guardrail sidecar. It records the README built-in/custom backend feature
  bullet, the wording separating custom import-path extension points from
  first-class Codex-authenticated or other local CLI provider support, the
  link to the subprocess/CLI backend contract TODO, code-TODO contract
  markers, backend-doc built-in/custom lane markers, and a narrow scan for
  unsupported positive Codex/local CLI provider-support claims in README,
  ROADMAP, and papers/README. It is not a first-class CLI backend contract,
  CLI backend manifest schema, credential-safe CLI backend smoke, provider
  budget accounting for CLI backends, or provider diagnostics for CLI backends.
- `papers/readme_paper_cache_topic_boundary.json`: README paper-cache topic
  sidecar. It records the README paper-cache topic sentence,
  download-manifest row count, papers-index implementation-status row count,
  papers-index role inventory, and bounded heuristic topic-family signals for
  LLM-guided evolution, program synthesis, quality-diversity optimization, and
  related benchmarks. It is not a row-level reviewed topic taxonomy, taxonomy
  reviewer signoff, semantic verification of the README topic phrase, a
  new-paper out-of-scope detector, or owner review signoff.
- `papers/readme_paper_cache_rehydrate_boundary.json`: README paper-cache
  rehydrate sidecar. It records the README and papers-index rehydrate
  commands, manifest row count, paper-manifest CLI flags, rehydrate report
  fields, missing-PDF download test, existing-PDF skip test, force-redownload
  test, and redacted network-failure test. It is not a clean-checkout
  absent-cache transcript, live network outcome matrix, full
  hash-verification transcript, or owner review signoff.
- `papers/release_checklist_documentation_boundary.json`: release-checklist
  documentation sidecar. It records `docs/release-checklist.md` required
  local smoke bullets, out-of-scope signed/published/approved release bullets,
  GitHub Actions release-artifact workflow markers,
  `libreevolve/tools/release_artifact_provenance.py` markers, release
  reproducibility and CI sidecar anchors, cross-document anchors, focused
  tests, active TODO ownership, a per-checklist-bullet workflow-step map, and
  a provenance schema field map. It is not signed release provenance,
  published-index verification, maintainer release event, or owner review
  signoff.
- `papers/documentation_claim_inventory.json`: top-level README/ROADMAP/
  papers-index claim inventory sidecar with stable claim ids, document
  sections, file-offset source anchors, local evidence-ref existence records,
  Markdown fragment-anchor resolution records, audited surface heading records,
  uncovered heading-to-claim gap records, active TODO-owner links, and explicit
  missing-evidence fields for complete coverage and semantic proof.
- `papers/evolutionary_database_boundary.json`: AlphaEvolve evolutionary
  database sidecar for current-run resurfacing versus durable database parity.
  It records append-only accepted/failure/archive streams, archive-state
  snapshots, bounded rank-fusion resurfacing summaries, and defensive
  current-run query snapshots by metric, lineage, descriptor, novelty,
  feedback, artifact, hypothesis, failure, and exact program-output evidence.
  It is not a durable cross-run query store, schema-versioned database
  migration proof, semantic retrieval index, replayable sampling policy,
  cross-run failure memory, learned novelty model, or AlphaEvolve-grade
  evolutionary database.
- `papers/jsonl_durability_boundary.json`: strict JSONL durability sidecar for
  append-side stream safety versus read-side repair and async writer parity. It
  records strict JSON serialization, finite record validation, append-side torn
  final-record repair, newline-terminated writes, fsync, quarantine
  diagnostics, retention modes, strict per-line reader validation, default
  fail-closed handling for newline-missing final records, opt-in read-side
  repair, and strict-reader coverage for show/archive/controller/manifest/
  plugin paths. It also records helper-managed advisory interprocess append
  serialization, Windows/POSIX lock selection, stable stream/quarantine lock
  ordering, and a subprocess concurrent-writer test. It is not evidence of
  semantic append ordering ownership, crash-atomic repair/quarantine
  transactions, or AlphaEvolve-grade durable async run-state parity.
- `papers/non_jsonl_artifact_boundary.json`: non-JSONL run-artifact schema
  sidecar for standalone JSON files, exported files, workspace directories,
  plugin/evaluator artifact directories, and `paper_artifacts/`. It records
  the current `artifact_schema.non_jsonl_artifacts` map, generated inventory
  linkage, implementation anchors, documentation anchors, behavior-test
  anchors, hash policies, lifecycle status, show/restore policy validation,
  and the paper-artifact subpath schema. It is not evidence of full restored-
  run payload replay, artifact payload carry-forward, cross-run payload
  reconstruction, independent bundle audit, or paper-artifact replay
  certification.
- `papers/restore_certification_boundary.json`: restore-certification sidecar
  for compatible local manifest restore surfaces versus full replay proof. It
  records the current `runtime.restore_certification` and
  `runtime.run_artifact_bundle_report` schemas, accepted-stream and quarantine
  diagnostic validation, show/CLI/direct-loader overclaim rejection, and the
  explicit accepted-state/quarantine-diagnostic boundary. It is not evidence of
  full replay proof, provider raw-payload replay, controller pending-work
  checkpoint replay, artifact payload reconstruction hashes, cross-run
  restore/replay evidence, or independent restore/replay audit.
- `papers/roadmap_readiness_boundary.json`: ROADMAP readiness taxonomy
  sidecar with stable readiness categories, weights summing to 100,
  per-category TODO-ledger counts, raw TODO-ledger completion, and weighted
  TODO-ledger completion. It is not semantic AlphaEvolve implementation
  readiness, canonical underlying-gap deduplication, source-span disposition
  completeness, per-category test-gate coverage, benchmark reproduction
  certification, or operational release readiness.
- `papers/roadmap_readiness_publication_boundary.json`: ROADMAP readiness
  publication sidecar with eight criteria for semantic requirement source
  mapping, canonical gap completion policy, per-category evidence gates,
  benchmark reproduction certification, operational release readiness,
  uncertainty/percentage labels, stale-count detection, and
  publication-claim scoping. It is not evidence that readiness percentages can
  be published as semantic AlphaEvolve implementation parity.
- `papers/roadmap_claim_evidence_boundary.json`: ROADMAP current-state and
  priority claim-evidence sidecar with six claim surfaces, parsed
  current-state bullet count, parsed good-first item count, sidecar refs,
  active TODO refs, validation-gate labels, and readiness labels. It is not
  evidence of complete per-bullet claim ids, per-bullet code/test/runtime
  evidence maps, semantic evidence-sufficiency verification, stale
  current-state detection, stale-priority detection, cross-document claim
  freshness, a generated alignment report, a CI semantic claim gate, or owner
  review signoff.
- `papers/todo_ledger_ownership_boundary.json`: TODO-ledger ownership sidecar
  with the four owner files, active/completed counts, active-ledger checked
  marker drift, raw checklist completion, and exact normalized-title duplicate
  groups. It now also records a bounded exact-title raw-count inflation
  estimate: 123 exact duplicate-title groups, 246 duplicate records, 123
  inflated raw checklist rows, and a 5166 collapsed exact-title total
  estimate. It also records an exact duplicate owner/status profile: all 123
  exact-title duplicate groups are completed-only, 122 groups are cross-owner,
  one group is same-owner, and zero groups involve active TODO rows. It also
  records one exact same-owner completed duplicate in
  `docs/todo/Completed/roadmap.md`, for "Add bounded ROADMAP
  evaluation-cascade readiness matrix." at lines 15460 and 15778. It also
  records a bounded exact stale-completed duplicate detector with zero
  active/completed title twins. It is not evidence of canonical underlying-gap
  ids,
  derivative/documentation relationships, rollup rules, source/paper anchor
  mappings, implementation evidence links, semantic stale duplicate detection,
  same-owner duplicate cleanup beyond exact title matches, orphan derivative
  detection, or canonical-gap completion percentages.
- `papers/todo_canonical_gap_boundary.json`: TODO canonical-gap readiness
  sidecar with nine criteria for canonical gap ids, canonical owner ledgers,
  derivative relationships, source/paper anchor mapping, implementation
  evidence links, cross-document rollup rules, semantic duplicate detection,
  stale duplicate/orphan detection, and raw-count inflation reporting. It now
  records active TODO coverage for all 12 missing evidence keys. It is not
  evidence of canonical gap ids, canonical owner assignments, derivative
  documentation relationships, source or paper anchor mappings,
  implementation evidence links, cross-document rollup rules, semantic
  duplicate detection, stale completed duplicate detection beyond exact title
  matches, orphaned derivative detection, canonical raw-count inflation
  reporting beyond exact title matches, canonical gap completion percentages,
  or owner review signoff.
- `papers/todo_canonical_gap_rollup_boundary.json`: TODO canonical-gap rollup
  sidecar with eight criteria for canonical gap registry, canonical owner
  policy, derivative relationships, source and implementation evidence links,
  cross-document rollup policy, duplicate/orphan detection, canonical
  completion reporting, and owner-reviewed publication scoping. It also
  records active TODO coverage for all 12 missing evidence keys, with each
  coverage row scoped to an active `docs/todo/roadmap.md` phrase. It is not
  evidence that raw checklist completion is canonical underlying-gap
  completion or that the missing canonical-readiness fields are implemented.
- `papers/roadmap_source_span_disposition_boundary.json`: ROADMAP source-span
  disposition sidecar for the six core AlphaEvolve anchors already present in
  `papers/implementation_evidence_map_boundary.json`. It records source refs,
  local status, ROADMAP section ids, phase buckets, sidecars, TODO links, 53
  paper-index rows, and only the AlphaEvolve source row dispositioned by this
  matrix. It is not evidence of an exhaustive retained-PDF section walk,
  figure/table/appendix/application-result matrix, complete paper-index row to
  ROADMAP disposition map, missing/partial TODO proof, or CI source-span
  exhaustiveness gate.
- `papers/roadmap_source_span_coverage_boundary.json`: ROADMAP AlphaEvolve
  source-span coverage sidecar with eight coverage surfaces for main-text
  sections, figures, tables, Appendix A, Appendix B, application-result
  claims, paper-status rows, and TODO/non-goal/phase proof. It records current
  sidecar refs, active TODO refs, validation gates, readiness labels, core
  anchor disposition counts, and paper-status row counts. It is not evidence
  of an exhaustive PDF section walk, complete figure/table/appendix matrix,
  complete application-result claim matrix, status-row to ROADMAP disposition
  map, missing/partial TODO proof, non-goal decision map, phase-priority map,
  CI source-span exhaustiveness gate, or owner review signoff.
- `papers/roadmap_source_span_exhaustiveness_boundary.json`: ROADMAP
  source-span exhaustiveness sidecar with eight criteria for PDF section walk,
  figure/table/appendix matrix, application-result claim matrix, status-row
  disposition map, span status classification, missing/partial TODO proof,
  phase-priority map, and CI/owner signoff. It is not evidence of an
  exhaustive retained AlphaEvolve source-span walk.
- `papers/roadmap_non_goal_contradiction_boundary.json`: ROADMAP non-goal
  contradiction sidecar with stable ids for the three current non-goals, nine
  constrained documentation surfaces, required safe-scope phrase checks, and
  zero exact forbidden support-claim phrase matches for that bounded set. It
  links the full Markdown corpus scan sidecar, but it is not evidence of a
  runtime metadata scan, plugin docstring scan, CI promotion gate, or
  intentional non-goal promotion workflow.
- `papers/roadmap_non_goal_drift_boundary.json`: ROADMAP non-goal drift and
  promotion readiness sidecar with seven criteria for runtime metadata scans,
  plugin docstring scans, exhaustive Markdown corpus scans, CI promotion
  gates, intentional-promotion workflow, contradiction remediation, and joined
  runtime/plugin/docs/paper scope maps. It now points to separate runtime
  metadata, Markdown corpus, plugin docstring, CI promotion-gate, and
  intentional-promotion workflow and remediation sidecars, but it is not
  evidence that scope joins or owner review signoff are implemented.
- `papers/roadmap_non_goal_ci_promotion_gate_boundary.json`: ROADMAP non-goal
  CI promotion gate sidecar with committed GitHub Actions path-filter,
  paper-manifest, and boundary-test evidence for ROADMAP non-goal
  contradiction, drift, Markdown, plugin docstring, and runtime metadata
  checks. It is not evidence of an intentional promotion workflow,
  contradiction-remediation report, joined runtime/plugin/docs/paper scope
  proof, or owner-reviewed signoff.
- `papers/roadmap_non_goal_promotion_workflow_boundary.json`: ROADMAP
  non-goal intentional promotion workflow sidecar with the committed workflow
  document, required claim surfaces, required non-goal sidecars, and paper
  manifest gate. It is not evidence of a contradiction-remediation report,
  joined runtime/plugin/docs/paper scope proof, or owner-reviewed signoff.
- `papers/roadmap_non_goal_remediation_boundary.json`: ROADMAP non-goal
  contradiction-remediation sidecar that aggregates the bounded documentation
  inventory, Markdown corpus scan, plugin docstring scan, and runtime metadata
  scan; requires zero unresolved contradiction hits; and routes future hits to
  TODO ownership plus claim-update surfaces. It is not evidence of
  owner-reviewed signoff.
- `papers/roadmap_non_goal_scope_join_boundary.json`: ROADMAP non-goal
  runtime/plugin/docs/paper scope-join sidecar that joins the three stable
  non-goal ids across bounded documentation surfaces, the full Markdown corpus
  scan, runtime metadata source scans, built-in plugin docstring and registry
  scans, paper sidecar records, `docs/status.md` references, and
  remediation-route ownership with zero joined contradictions. It is not
  evidence of owner-reviewed signoff or a complete future-proof non-goal
  lifecycle gate.
- `papers/roadmap_non_goal_markdown_scan_boundary.json`: ROADMAP non-goal
  Markdown corpus scan sidecar with the repository Markdown file inventory,
  stable non-goal ids, forbidden support-claim phrases, line-level hit records,
  and zero detected Markdown contradiction hits. It is not evidence of runtime
  metadata scanning, plugin docstring scanning, CI promotion enforcement,
  intentional promotion workflow, joined runtime/plugin/docs/paper scope proof,
  or owner-reviewed remediation readiness.
- `papers/roadmap_non_goal_plugin_docstring_boundary.json`: ROADMAP non-goal
  plugin docstring scan sidecar with built-in plugin source-file inventory,
  AST docstring records, registry labels, paper-inspiration labels, forbidden
  faithful-claim phrase checks, zero faithful-overclaim hits, and no missing
  non-faithful disclaimers for paper-inspired built-ins. It is not evidence of
  runtime metadata scanning, CI promotion enforcement, intentional promotion
  workflow, joined runtime/plugin/docs/paper scope proof, or owner-reviewed
  remediation readiness.
- `papers/roadmap_non_goal_runtime_metadata_boundary.json`: ROADMAP non-goal
  runtime metadata scan sidecar with source-defined runtime metadata surfaces
  for startup manifest plugin/config fields, candidate-language runner policy,
  runtime plugin state, runtime plugin artifact metadata, and built-in plugin
  registry paper-inspiration labels. It records required safe-scope phrases,
  zero missing safe phrases at the repo root, and zero contradictory
  support-claim hits. It is not evidence of intentional promotion workflow,
  joined runtime/plugin/docs/paper scope proof, or owner-reviewed remediation
  readiness.
- `papers/roadmap_good_first_followups_boundary.json`: ROADMAP Good First
  Follow-Ups priority sidecar with the four current priority items, active
  TODO refs, priority rationale, dependency-readiness labels, validation gates,
  and AlphaEvolve impact labels. Dependency-state refresh and stale-priority
  detection plus priority scoring are recorded separately. It is not evidence
  of owner review signoff.
- `papers/roadmap_good_first_dependency_refresh_boundary.json`: ROADMAP Good
  First Follow-Ups dependency-refresh sidecar that rechecks the four current
  priority items against live active TODO dependency refs, current blocker
  labels, validation gate expectations, and AlphaEvolve impact labels, with
  zero stale dependency refs. Stale-priority detection is recorded separately.
  Priority scoring, CI freshness gating, and validation-artifact reporting are
  recorded separately. It is not evidence of owner review signoff.
- `papers/roadmap_good_first_stale_priority_boundary.json`: ROADMAP Good
  First Follow-Ups stale-priority detector sidecar that joins the static
  priority map to dependency-refresh records, ordinal order, live dependency
  refs, blocker labels, and ROADMAP phrase checks, with zero stale priority
  records. Priority scoring, CI freshness gating, and validation-artifact
  reporting are recorded separately. It is not evidence of owner review
  signoff.
- `papers/roadmap_good_first_priority_score_boundary.json`: ROADMAP Good
  First Follow-Ups priority-score sidecar with deterministic feature weights,
  dependency-readiness scores, AlphaEvolve-impact scores, per-item score
  records, ranked item ids, and zero rank mismatches for the current Good
  First ordering. CI freshness gating and validation-artifact reporting are
  recorded separately. It is not evidence of owner review signoff.
- `papers/roadmap_good_first_ci_priority_gate_boundary.json`: ROADMAP Good
  First Follow-Ups CI priority freshness gate sidecar with committed sidecar
  checks, paper-manifest validator markers, and docs/paper/boundary GitHub
  Actions workflow markers, with zero missing gate records. It is not evidence
  of owner review signoff.
- `papers/roadmap_good_first_validation_artifact_boundary.json`: ROADMAP Good
  First Follow-Ups validation-artifact sidecar that joins each expected
  validation gate to artifact-family labels, committed sidecar refs, active
  TODO anchors, and the CI priority freshness gate, with zero stale
  validation-artifact records. It is not evidence of completed underlying
  implementations or owner review signoff.
- `papers/roadmap_good_first_freshness_boundary.json`: ROADMAP Good First
  Follow-Ups freshness readiness sidecar with six criteria for dependency-
  state refresh, stale-priority detection, calibrated priority scoring, CI
  freshness gating, validation-artifact report, and owner review signoff. It
  is not evidence that signoff is implemented.
- `papers/roadmap_phase_sequence_boundary.json`: ROADMAP phase-sequencing
  sidecar with the current Near Term, Mid Term, and Longer Term sequence for
  ten major ROADMAP sections, active blocker TODO refs, validation-gate labels,
  and promotion criteria. The dependency graph and stale-phase detector are
  recorded separately, and the phase promotion/demotion workflow is recorded
  separately. It is not evidence of an evidence-status refresh report or owner
  review signoff.
- `papers/roadmap_phase_dependency_graph_boundary.json`: ROADMAP phase
  dependency-graph sidecar with ten section nodes, prerequisite section edges,
  section evidence sidecars, active blocker TODO refs, and zero stale
  dependency edges. The stale-phase detector and phase promotion/demotion
  workflow are recorded separately. It is not evidence of an evidence-status
  refresh report or owner review signoff.
- `papers/roadmap_phase_staleness_boundary.json`: ROADMAP phase staleness
  sidecar with ten detector records joined to phase sequence status,
  dependency graph status, active blocker TODO refs, section sidecar presence,
  dependency edge status, and zero stale phase records. It is not evidence of
  an evidence-status refresh report or owner review signoff.
- `papers/roadmap_phase_promotion_workflow_boundary.json`: ROADMAP phase
  promotion/demotion workflow sidecar with the committed workflow doc, claim
  surface refs, phase sidecar refs, dependency graph refresh requirement,
  stale phase record resolution requirement, and paper-manifest gate. It is
  not evidence of an evidence-status refresh report or owner review signoff.
- `papers/roadmap_phase_ci_freshness_gate_boundary.json`: ROADMAP phase CI
  freshness gate sidecar with committed phase sidecars, paper-manifest
  validator markers, docs/libreevolve/papers/tests path filters, and
  docs/paper/boundary GitHub Actions workflow markers, with zero missing gate
  records. It is not evidence of an evidence-status refresh report or owner
  review signoff.
- `papers/roadmap_phase_freshness_boundary.json`: ROADMAP phase freshness
  readiness sidecar with six criteria for the dependency graph,
  stale-phase detector, promotion/demotion workflow, CI phase freshness gate,
  evidence-status refresh, and owner review signoff. It is not evidence that
  those refresh-report or signoff mechanisms are implemented.
- `papers/roadmap_operational_maturity_boundary.json`: ROADMAP operational
  maturity sidecar with six section-level criteria, risk classes, current
  sidecar refs, active TODO refs, and acceptance-gate labels. It is not
  evidence of a global acceptance threshold, unified run-artifact lifecycle
  inventory, semantic docs verification, signed release provenance,
  cross-platform CI policy, or owner review signoff.
- `papers/roadmap_operational_readiness_boundary.json`: ROADMAP operational
  readiness sidecar with six criteria for the global acceptance threshold,
  unified generated-artifact lifecycle inventory, semantic docs verification,
  signed release provenance, cross-platform CI policy, and owner review
  signoff, plus a per-surface operational maturity claim guard. It is not
  evidence that those threshold, lifecycle, semantic-docs, release, CI-policy,
  or signoff mechanisms are implemented.
- `papers/roadmap_representative_benchmark_portfolio_boundary.json`: ROADMAP
  representative-benchmark portfolio sidecar with five portfolio families,
  domains, validator-strength labels, current sidecar refs, active TODO refs,
  baseline/SOTA target labels, artifact-output requirements, and
  readiness-status labels. It is not evidence of a domain-coverage matrix,
  benchmark admission checklist, repeated-seed run matrix, anti-gaming
  certification, SOTA/baseline citation sufficiency proof, portfolio-balance
  score, CI freshness gate, or owner review signoff.
- `papers/roadmap_benchmark_portfolio_readiness_boundary.json`: ROADMAP
  representative-benchmark readiness sidecar with six criteria for domain
  coverage, benchmark admission, repeated-seed run evidence, anti-gaming
  certification, SOTA/baseline citation sufficiency, and portfolio-balance/CI
  freshness, plus a per-surface benchmark-portfolio claim guard. It is not
  evidence that those matrix, checklist, run, certification, citation,
  balance, CI, or signoff mechanisms are implemented.
- `papers/roadmap_plugin_extensibility_boundary.json`: ROADMAP
  plugin-extensibility sidecar with six plugin surfaces, configuration shape,
  package/source identity, constructor provenance, artifact hashing,
  trust-boundary, paper-scope attribution, validation-gate, code-ref,
  sidecar-ref, active-TODO, and readiness labels. It is not evidence of a
  plugin trust-boundary matrix, plugin admission checklist, direct constructor
  value/schema registry, versioned custom plugin registry, artifact lifecycle
  hash policy, runtime isolation policy, paper-scope attribution policy,
  stale-readiness detector, or owner review signoff.
- `papers/roadmap_plugin_readiness_boundary.json`: ROADMAP plugin readiness
  sidecar with seven criteria for trust boundaries, admission, direct
  constructor value/schema registry, versioned custom registry, artifact
  lifecycle hashes, runtime isolation, and paper-scope/staleness guards, plus
  a per-surface plugin claim guard. It is not evidence that those
  external-plugin readiness mechanisms are implemented.
- `papers/roadmap_backend_scheduling_critique_boundary.json`: ROADMAP
  backend-scheduling and critique sidecar with nine tracks, selection-policy,
  reward-assumption, budget/quota, pricing/default-rate, diagnostics/replay,
  cancellation, resume, equal-budget, reviewer-isolation,
  Gemini-substitution, sidecar-ref, active-TODO, validation-gate, and
  readiness labels, plus an explicit backend-role capability inventory derived
  from those tracks, reward-assumption, role budget/quota, and provider
  pricing/default-rate evidence maps, diagnostics/replay and
  cancellation/resume policy maps, bounded equal-budget comparator and Gemini
  substitution policy maps, and a structural critique-control checklist for the
  synchronous reviewer surface. It is not evidence of calibrated reward
  policy, role quota ownership, live provider pricing/default evidence, raw
  provider replay, live hard cancellation, equal-budget scheduler comparator,
  live Gemini Flash/Pro pair evidence or substitution equivalence, async reviewer isolation,
  stale-readiness detector, owner review signoff, or full backend scheduler
  parity.
- `papers/roadmap_backend_control_plane_readiness_boundary.json`: ROADMAP
  backend control-plane readiness sidecar with eight criteria for backend-role
  capability, calibrated reward/quota policy, live pricing/default and raw
  replay, hard cancellation/resume, equal-budget scheduler comparison, Gemini
  lane/substitution, critique reviewer isolation, and stale readiness/owner
  signoff. It records the backend-role capability matrix as resolved structural
  evidence from the scheduling sidecar, and records the critique-control
  checklist as resolved structural evidence from that same source, plus a
  per-surface backend control-plane claim guard, but is not evidence that the
  scheduler, provider, Gemini, or reviewer-readiness mechanisms are
  implemented.
- `papers/roadmap_async_resumable_runtime_boundary.json`: ROADMAP
  async/resumable-runtime sidecar with nine criteria for topology, parallel
  evaluation, controller pending work, archive-event replay, RNG/lineage
  replay, provider/plugin nondeterminism, budget resume, environment replay,
  and resumed-trace proof, with current scope, missing-readiness,
  sidecar-ref, active-TODO, validation-gate, and readiness labels. It is not
  evidence of an async-state inventory, replay-resume acceptance checklist,
  controller queue checkpoint, LLM sampler task state, evaluator pending-work
  state, deterministic async merge/admission replay, ordered migration restore
  engine, provider-output replay, plugin RNG replay, async budget accounting,
  external environment replay, end-to-end resumed trace proof,
  stale-readiness detector, or owner review signoff.
- `papers/roadmap_async_runtime_readiness_boundary.json`: ROADMAP async runtime
  readiness sidecar with eight criteria for async-state inventory,
  replay-resume acceptance, controller/sampler task checkpoints, evaluator
  pending work and merge order, archive/migration restore, provider/plugin
  replay, async budget/environment replay, and stale readiness/owner signoff.
  It is not evidence that those async, replay, provider, plugin, or
  environment-readiness mechanisms are implemented.
- `papers/roadmap_prompt_context_system_boundary.json`: ROADMAP
  prompt/context-system sidecar with nine criteria for role-template
  compatibility, context-source selection, token section packing, stochastic
  prompt-format provenance, retention/replay policy, retrieval integrity,
  proposal-memory semantics, meta-prompt reward evidence, and prompt-database
  lifecycle, with current scope, missing-readiness, sidecar-ref, active-TODO,
  validation-gate, and readiness labels. It is not evidence of a prompt-role
  capability matrix, deterministic context summarization, all-role
  provider-token section packing, separate prompt-format source provenance,
  full prompt replay-retention policy, audit-grade retrieval source integrity,
  semantic proposal memory, calibrated meta-prompt rewards,
  prompt-database archive lifecycle, prompt/context benchmark evidence,
  stale-readiness detector, or owner review signoff.
- `papers/roadmap_prompt_context_readiness_boundary.json`: ROADMAP
  prompt/context readiness sidecar with eight criteria for prompt-role
  capability, context selection/summarization, all-role token section packing,
  prompt-format and replay retention, retrieval/proposal-memory integrity,
  meta-prompt and prompt-database lifecycle, prompt/context benchmark
  evidence, and stale readiness/owner signoff, plus a per-surface
  prompt/context claim guard. It is not evidence that those prompt-system
  readiness mechanisms are implemented.
- `papers/roadmap_evaluation_cascade_boundary.json`: ROADMAP
  evaluation-cascade sidecar with ten criteria for cascade transition
  artifacts, artifact schema/hash coverage, budget ownership, feedback
  calibration, statistical promotion policy, oracle independence, workload
  execution contracts, automated scope and programmatic boundaries, validator
  sandbox dependency boundaries, and environment/release reproducibility, with
  current scope, missing-readiness, sidecar-ref, active-TODO, validation-gate,
  and readiness labels. It is not evidence of a validator-authority matrix,
  complete artifact schema/hash coverage, accelerator/async budget ownership,
  executed feedback calibration, benchmark-calibrated statistical promotion,
  independent oracle disagreement records, workload-specific execution
  contracts, robust automated environment fixtures, OS/container resource
  sandboxing, replayable environment/release bundles, benchmark-sufficiency
  signoff, stale-readiness detector, or owner review signoff.
- `papers/roadmap_evaluation_cascade_readiness_boundary.json`: ROADMAP
  evaluation-cascade readiness sidecar with eight criteria for validator
  authority, artifact/budget sufficiency, feedback/statistical promotion,
  oracle/workload contracts, automated environment/sandbox policy,
  release/environment reproducibility, benchmark sufficiency, and stale
  readiness/owner signoff, plus a per-surface evaluation-cascade claim guard.
  It is not evidence that those cascade-readiness mechanisms are implemented.
- `papers/roadmap_multi_objective_search_boundary.json`: ROADMAP
  multi-objective search sidecar with eight criteria for paper metric bundles,
  objective-archive policy, metric-diverse sampling balance, duplicate-work
  memory, descriptor authority, MAP-Elites illumination, metric-specific
  drill-downs, and benchmark comparison evidence, with current scope,
  missing-readiness, sidecar-ref, active-TODO, validation-gate, and readiness
  labels. It is not evidence of primary Pareto/frontier archive replacement,
  durable cross-run metric databases, calibrated parent/inspiration balance,
  stable behavior descriptor contracts, learned or evaluator-provided
  descriptor models, tested archive rebin semantics, durable duplicate-work
  memory, semantic near-duplicate detection, metric-specific CLI drill-downs,
  equal-budget multi-objective benchmarks, stale-readiness detector, or owner
  review signoff.
- `papers/roadmap_multi_objective_readiness_boundary.json`: ROADMAP
  multi-objective readiness sidecar with eight criteria for primary archive
  policy, durable metric storage, sampling/metric policy, descriptor
  authority and rebin semantics, duplicate-work memory semantics, metric
  drill-down/CLI policy, equal-budget benchmark evidence, and stale
  readiness/owner signoff, plus a per-surface multi-objective claim guard. It
  is not evidence that those multi-objective readiness mechanisms are
  implemented.
- `papers/roadmap_candidate_workspace_fidelity_boundary.json`: ROADMAP
  candidate-workspace fidelity sidecar with ten criteria for language/build
  runner support, candidate abstraction API, marker/materialization policy,
  embedded evaluator boundaries, codebase-scale fixtures, mutation-mode/
  operator provenance, prompt-example-copy guards, cross-file consistency,
  initial-pool/static-binary handling, and source/workspace resume integrity,
  with current scope, missing-readiness, sidecar-ref, active-TODO,
  validation-gate, and readiness labels. It is not evidence of configured
  language/build runners, a flexible solution abstraction API,
  candidate-embedded evaluator contracts, realistic codebase fixtures,
  benchmark-calibrated adaptive mutation-mode policy, mutation-operator family provenance,
  semantic prompt-example-copy detection, cross-file consistency benchmark
  evidence, initial-pool divergence benchmark evidence, static/binary replay
  policy, topology resume replay proof, stale-readiness detector, or owner
  review signoff.
- `papers/roadmap_candidate_workspace_readiness_boundary.json`: ROADMAP
  candidate-workspace readiness sidecar with eight criteria for language/build
  runner and candidate API readiness, embedded evaluator and codebase-scale
  readiness, materialization/topology readiness, mutation-mode and operator
  provenance, prompt-copy and cross-file consistency, initial-pool/static-
  binary policy, resume replay and manifest/workspace-doc policy, and stale
  readiness/owner signoff, plus a per-surface candidate-workspace claim guard.
  It is not evidence that those candidate-workspace readiness mechanisms are
  implemented.
- `papers/implementation_evidence_map_boundary.json`: core AlphaEvolve
  implementation-evidence map boundary with requirement ids, module/test/
  sidecar/TODO anchors, and explicit missing-evidence fields for exhaustive
  audit coverage, per-phrase evidence-link sufficiency, status-cell semantic
  verification, implemented-benchmark bullet semantic verification, and absence-sentence
  freshness checks.
- `papers/benchmark_coverage_inventory.json`: structural inventory for
  `papers/README.md` Implemented benchmark coverage bullets. It records bullet
  source spans, file character offsets, summary/body hashes, source-token
  match file offsets, local artifact mention file offsets, artifact-existence records, limitation-signal
  terms/source offsets/counts, and contradiction flags. The current inventory
  records 3 referenced manifest source IDs across 15 source-token match
  records, 116 unique referenced local artifact paths, and zero missing
  referenced local artifacts. It is not
  benchmark-result reproduction evidence, semantic verification, or freshness
  proof.
- `papers/status_claim_inventory.json`: row-level paper-index
  implementation-status inventory with one record per status row, status text
  hash, role/status class, manifest-file link, source line, local artifact
  mention source offsets and existence records, active/completed TODO evidence
  path source offsets and existence records, and status-cell phrase hashes with
  source offsets plus candidate evidence-link lists. The current inventory records 60
  unique referenced local artifact paths, 60 row-level artifact mention
  records, 60 phrase-level artifact mention records, and zero missing
  referenced local artifacts, plus 6 unique referenced TODO evidence paths,
  289 TODO evidence path mention records, and zero missing referenced TODO
  evidence paths, 175 matched TODO content source tokens, 950 row-specific
  TODO block hashes/source offsets, 291 TODO content artifact mention
  source-offset records, and zero status-row local artifact paths missing from
  linked row-specific TODO evidence. It also records zero
  status-phrase local artifact paths missing from linked row-specific TODO
  evidence, 286 phrase-level TODO block records, and structurally classifies 87 status-cell
  absence-signal phrases with 99 source-offset records. It is not status-cell
  phrase-level semantic verification, evidence-link sufficiency proof, or
  absence-sentence freshness evidence.
- `papers/arxiv_abstract_snapshot.json`: AlphaEvolve arXiv abstract-page
  snapshot sidecar with the pinned `2506.13131v1` HTML byte count/digest,
  retained HTML artifact path, normalized source metadata, and explicit
  remaining automated refresh evidence. It is not full
  publication-grade source evidence or a live refresh gate.
- `papers/alphaevolve_datacite_doi_boundary.json`: AlphaEvolve DOI/DataCite
  sidecar with the pinned DataCite API URL, retrieval date, status, response
  byte count, SHA-256 digest, DOI, landing URL, title, creator count,
  publisher, publication year, resource type, schema version, registered
  timestamp, and version. It is not a DataCite refresh gate.
- `papers/alphaevolve_datacite_full_response_boundary.json`: AlphaEvolve
  DataCite full-response sidecar with the retained raw DataCite API response
  body, byte count, SHA-256 digest, parsed DOI, landing URL, title, creator
  count, publisher, publication year, resource type, schema version, registered
  timestamp, and version. It is not an automated DataCite refresh gate.
- `papers/alphaevolve_doi_landing_resolution_boundary.json`: AlphaEvolve DOI
  landing-resolution sidecar with the pinned DOI URL, retrieval timestamp,
  resolver `302` status, redirect location, raw resolver header lines, final
  arXiv landing URL/status/content type, final raw header lines, and final
  landing response bytes/hash. It is not full DOI redirect body retention, an
  automated DOI resolution refresh gate.
- `papers/alphaevolve_tex_source_boundary.json`: AlphaEvolve arXiv TeX/e-print
  sidecar with the pinned e-print URL, retrieval date, status, content type,
  content-disposition filename, response byte count, SHA-256 digest, and
  `2506.13131v1` linkage. It is not a TeX-source refresh gate and is paired
  with the metadata extraction-script sidecar.
- `papers/alphaevolve_tex_archive_retention_boundary.json`: AlphaEvolve
  TeX/e-print archive-retention sidecar with the retained
  `papers/alphaevolve_tex_source_archive.tar.gz` artifact, archive bytes/hash,
  `2506.13131v1` linkage, 58-member inventory, per-file sizes, and per-file
  SHA-256 digests. It is not an automated TeX-source refresh gate and is paired
  with the metadata extraction-script sidecar.
- `papers/alphaevolve_current_version_boundary.json`: AlphaEvolve
  current-version/floating-PDF sidecar with pinned current abstract URL,
  retrieval date, status, content type, byte count, SHA-256 digest, title,
  resolved version, expected source version, floating PDF URL, status, content
  type, bytes/hash, retained PDF artifact path, cached-PDF bytes/hash, and
  match flag. It is not full current-abstract HTML retention, automated
  current-version refresh evidence.
- `papers/alphaevolve_cached_pdf_header_consistency_boundary.json`:
  AlphaEvolve cached-PDF header consistency sidecar with retained-PDF
  bytes/hash, first-page text extraction hashes, and arXiv version/title/rights
  markers. It is paired with the metadata extraction-script sidecar and is not
  an automated cached-PDF header refresh gate.
- `papers/alphaevolve_metadata_extraction_script_boundary.json`: AlphaEvolve
  offline metadata extraction-script sidecar with the pinned script path, byte
  count, SHA-256 digest, import entrypoint, CLI command, and retained artifact
  coverage for abstract HTML, cached PDF, DataCite full response, license HTML,
  and TeX archive inputs. It is not an automated live refresh CI gate.
- `papers/alphaevolve_source_refresh_gate_boundary.json`: AlphaEvolve source
  refresh-gate sidecar with the pinned deterministic/live refresh script, six
  expected source ids, scheduled/manual GitHub Actions wiring, and linkage to
  the archived manual live-run outcome. The workflow writes
  `alphaevolve_source_refresh_report.json` and uploads it as
  `alphaevolve-source-refresh-report`. It is not proof that scheduled CI
  refresh-run history has been archived.
- `papers/alphaevolve_source_refresh_run_2026-06-14.json`: AlphaEvolve source
  refresh-run sidecar with one archived manual live-network run, six matched
  source responses, a canonical run-report hash, and explicit missing evidence
  for scheduled CI refresh-run history. It is not recurring freshness evidence.
- `papers/alphaevolve_source_refresh_promotion_boundary.json`: AlphaEvolve
  source refresh-promotion policy sidecar mapping each central-gate source id
  to covered paper sidecars and recording the decision not to relabel older
  per-source snapshot sidecars as standalone refresh-ready evidence. It is not
  scheduled CI refresh-run history.
- `papers/alphaevolve_raw_http_headers_boundary.json`: AlphaEvolve source-URL
  raw HTTP headers sidecar with pinned header lines for the versioned abstract,
  floating abstract, floating PDF, DataCite API, e-print archive, and Creative
  Commons license page, linked to the already-pinned response bytes and
  SHA-256 digests. It is not full raw response body retention, an automated
  header refresh gate.
- `papers/alphaevolve_license_page_boundary.json`: AlphaEvolve
  source-license page sidecar with the pinned Creative Commons BY-NC-ND 4.0
  URL, retrieval date, status, content type, response byte count, SHA-256
  digest, page title, license family, license version, and normalized URL. It
  is paired with the raw-header and retained-HTML sidecars, but is not an
  automated license-page refresh gate.
- `papers/alphaevolve_license_page_html_retention_boundary.json`: retained
  Creative Commons license-page HTML sidecar with the committed HTML artifact
  path, byte count, SHA-256 digest, and key content markers. It is not an
  automated license-page refresh gate.
- `papers/candidate_abstraction_bias_matrix.json`: design-level candidate
  abstraction bias matrix for direct-solution, constructor-function,
  bespoke-search, and paired solution/search families. It is not executed
  benchmark evidence or support for problem-defined abstraction hooks.
- `libreevolve/problems/examples/sorting`: neutral plateau/diversity smoke
  fixture. The bubble-sort seed already reaches `accuracy == 1.0`, so this
  example can demonstrate mutation handling and same-score implementation
  variety but is not seed-to-best optimization-pressure evidence.
- `libreevolve/problems/examples/sorting_network_8` and
  `libreevolve/problems/examples/sorting_network_9`: bounded benchmark
  candidates with exhaustive zero-one validation, valid 28- and 36-comparator
  seeds, and checked 19- and 25-comparator targets. They are not
  paper-comparable evidence until repeated runs and certification artifacts are
  added. Their hardening bundle helper emits
  generic negative-fixture, inventory, summary, and scope-validation evidence,
  and `sorting_network_9` now has reusable run-contract, goal-prompt, and
  provider-profile validators for the clean-checkout Codex protocol. The
  provider profile records the experimental Codex lane, budget,
  transcript/redaction policy, artifact expectations, and non-evidence result
  linkage, but that is not a run-certified rediscovery record. The committed
  `papers/sorting_network_source_citation_boundary.json` sidecar records the
  zero-one-principle and known comparator-target citations, the committed
  `papers/sorting_network_source_snapshot_boundary.json` sidecar records live
  response metadata and hashes for those citation URLs without retaining full
  raw source bodies, the committed
  `papers/sorting_network_source_refresh_gate_boundary.json` sidecar records
  the deterministic source-refresh gate for those citation snapshots, the
  committed `papers/sorting_network_source_refresh_run_2026-06-18.json`
  sidecar archives a live refresh run that detected Codish publication source
  drift, the committed `papers/sorting_network_source_drift_triage_boundary.json`
  sidecar classifies that drift as dynamic full-page hash instability with
  citation markers still present, the committed
  `papers/sorting_network_normalized_marker_snapshot_boundary.json` sidecar
  records the stable marker-level citation facts while source snapshot
  metadata promotion remains pending, and
  `papers/sorting_network_rediscovery_boundary.json` preserves the remaining
  executable-candidate-only run-evidence boundary.

Planned or background-only:

- Constructive math papers are retained as benchmark candidates until validators
  are added.
- Compiler, hardware, systems, kernel, and scheduling-style AlphaEvolve targets
  are not yet represented; they need safer local fixtures before they should be
  advertised as supported.
- Self-improvement/distillation evidence is not implemented. AlphaEvolve's
  Discussion describes practical discoveries that can improve its own
  infrastructure and future base LLMs, plus possible distillation of
  AlphaEvolve-augmented performance into next-generation base models.
  LibreEvolve currently has no report linking an evolved candidate to measured
  improvements in LibreEvolve's own runtime/provider/evaluator/compiler/
  benchmark infrastructure, no deployment/adoption or rollback/safety-review
  evidence for such a change, and no distillation dataset, training run, or
  model-evaluation artifact derived from evolved programs. The committed
  `papers/self_improvement_distillation_boundary.json` sidecar keeps these
  Discussion claims scoped as absent local evidence.
  `papers/self_improvement_cadence_boundary.json` separately records that
  elapsed-month loop cadence, moderate-gain calibration, robust-evaluator
  environment setup/maintenance costs, expected-versus-realized discovery
  value, and environment-expansion decisions are not recorded locally.
