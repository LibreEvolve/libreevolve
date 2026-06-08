# Local Paper Cache

This directory is the paper-cache index. On the working machine it contains 24
locally cached PDFs plus download manifests, but the PDFs are intentionally
gitignored; the committed repository tracks this README and the CSV/JSON
manifests. The manifests record each cached PDF's byte count and SHA-256 hash.
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
cache PDFs as repository-boundary violations. The
implementation-status table IDs below are reconciled against the committed
manifest IDs by the same validator. The validator treats the implementation-
status table as a structured public claim surface: it requires the stable
four-column header, exact four-cell rows, non-empty display-safe title, role,
and status cells, the declared role taxonomy, allowed status class prefixes,
and compatible role/status pairs. The TODO coverage cross-reference table is
validated separately for manifest-id row coverage, exact row shape, active TODO
ledger links, and completed-ledger links under `docs/todo/Completed/` that
contain completed checklist evidence. These checks keep paper-index structure
and backlog traceability honest, but they do not yet prove every long status
phrase or benchmark qualifier against a specific implementation record.
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
need; it does not claim local OOM run artifacts.
The validation command also checks
`libreevolve/problems/benchmarks/alphaevolve_appendix_b.json`, which records a
coverage decision for each AlphaEvolve Appendix B constructive-math family. The
registry currently marks only the unit-square circle-packing fixture as
`implemented_smoke`; all other Appendix B families are explicit planned entries
with objective direction, target/baseline status, construction/certificate
artifact shape, certification need, rationale, and AlphaEvolve citation
metadata. Appendix B says reported construction data and verification code
appear in an accompanying Google Colab; this registry is not that
Colab-equivalent evidence surface and does not yet store construction-data
exports or runnable verifier-code artifacts.
It also is not the Section 3.2 aggregate mathematical-outcome evidence: the
paper reports over 50 problems across more than five branches, with roughly
75% matching best known constructions and roughly 20% improving SOTA.
LibreEvolve still needs per-problem/per-parameter rows, branch labels,
previous-best references, construction/verifier links, outcome statuses, and
validated aggregate percentages before making that class of breadth claim.
It also does not record Appendix B result-version provenance. Appendix B.4
first reports an uncertainty-inequality bound of `C4 <= 0.3521`, then notes
that after the first manuscript version Henry Cohn pointed to a refined
approach and AlphaEvolve improved the reported constant further to `0.3216`.
Current registry rows do not distinguish first-version and updated constants,
superseded/current status, update attribution, or verifier/Colab artifact
linkage for revised mathematical results.
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
archive-feedback context. The `No context in the prompt` row is currently too
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
failure-history terms. Unbounded full provider payload persistence, semantic ranking
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
It can also cap already validated/redacted plugin `extra_context` with
`extra_context_max_chars`, recording input/rendered/omitted character counts.
LLM-grader prompt context can now be narrowed with `llm_feedback_fields`, a
safe allowlist over `name`, `score`, `discard`, `error`, and `feedback`.
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

| ID | Title | Role | Current LibreEvolve status |
|---|---|---|---|
| 2506.13131 | AlphaEvolve | Primary specification target | Partially implemented: `libreevolve/core/loop.py` evolves blocks with explicit Python-file marker boundaries and unsupported non-Python marker diagnostics, local text-workspace candidates with Python-primary seed-workspace loading, manifest-visible candidate-language policy, and manifest-visible size reject budgets, workspace topology mutations, empty-file creation through full-mode file sections, rejection of ambiguous, overlong, and generated dot-prefixed candidate paths, unknown full-block target rejection, CLI happy-path full-workspace best export, workspace materialization with recursive link/junction preflight and typed materialization-failure diagnostics, plus basic candidate imports in local validators, mutation modes including canonical SEARCH/REPLACE diff compatibility, proposal-rationale capture with selected parent/inspiration prompt rendering, selected post-critique proposal provenance, preamble-only proposal stripping, structured evaluator results, schema-validated evaluator result dataclasses, structured non-JSON evaluator-return diagnostics, finite explicit Program fitness semantics, schema-safe redacted synthetic diff-error diagnostics, complete declared metric vectors for synthetic framework-generated evaluator failures, stage-threshold stops that retain real validator metric vectors, configurable local cascades with manifest-safe non-colliding stage labels, aggregate workspace syntax diagnostics, evaluator contract preflight before run-artifact mutation, strict scalar evaluator-output validation with reserved boolean validity, strict metric-bound ordering plus out-of-range clamp diagnostics, primary metric normalization, equal-weight normalized declared-metric archive selection, diagnostic Pareto frontier snapshots over declared normalized metrics, feedback-sourced objective metrics filled by configured graders, workspace-aware local MAP-Elites complexity/diversity inputs, configurable in-memory parent/inspiration sampling, prompt sampler/context ingestion with deterministic selection provenance, unmatched include diagnostics, secret-safe context source/pattern labels, hidden-context opt-in policy, skipped diagnostics for context extraction failures, default-fail explicit include extraction policy with opt-in degraded warning diagnostics, resource-bounded local context ingestion, and exact PDF excerpt page/span citations. Also implemented: bounded execution-output, validator-diagnostic, validator-metadata, and grader-feedback prompt summaries, prompt-program database and optional meta-prompt mutation, structured prompt-program context-policy hooks, configurable synchronous critique reviewer pools with first/last-valid aggregation, synchronous critique with bounded/redacted prompt construction, retained critique metadata, and deterministic no-valid-mutation selection provenance, LLM feedback graders with full-workspace feedback prompts, configurable feedback-failure retries/policies, and manifest-safe grader labels, manifests, run identity/collision policy, source-root Git/source/problem provenance, generated-run artifact classification for problem provenance, bounded source/problem provenance file reads, cwd-independent generated-root provenance exclusion, final effective config validation after CLI overrides, secret-safe and bounded plugin-module provenance, source/problem included-file and skipped-diagnostics provenance digests, UTC runtime wall-clock manifest timestamps with monotonic elapsed-budget linkage, manifest-runtime-aware `show` status for completed/aborted/partial runs, typed missing/invalid/invalid-schema `pyproject.toml` provenance, direct evaluator entrypoint provenance, enforced problem-local evaluator dependency provenance, secret-safe persisted evaluator path metadata, streamed evaluator source hashing with read-error diagnostics, validator helper import precedence checks, manifest-safe candidate/program identifiers, skipped seed setup diagnostics, local run-budget accounting with stop reasons, logical LLM-call caps, and provider-attempt/token/configured-cost/latency stops, provider-free zero-generation seed baselines, run-local framework RNG isolation from process-global Python `random`, persisted and CLI-restorable framework RNG snapshots, CLI-scoped provider credential-presence and local client-construction preflight for mutation-capable runs, manifest-safe backend model identifiers, configured custom import-path LLM backends, configured entry-point plugin loading with manifest-safe constructor options and declared constructor-option schemas, restored/replay backend spec and prompt validation, ensemble prompt-size enforcement before registry/custom backend calls, selected PEP 621 metadata and NumPy numerical-runtime provenance, normalized ensemble-level LLM call telemetry with deterministic call ids, validated prompt/role labels, request parameters, client context, copied telemetry snapshots, malformed-output failure records, and redacted provider errors, candidate history/admission provenance, bounded proposal-hypothesis history indexes, typed static sidecars with bounded base64 generated/replaced static/binary members, direct raw binary workspace entries normalized into immutable static members, verified source-copy static asset materialization, policy-backed bounded-file prompt rendering for copied UTF-8 evaluator artifacts, heuristic prompt section packing under `prompt_max_chars` / `prompt_max_estimated_tokens`, explicit per-role LLM backend routing policy with role route telemetry, sequential sibling proposal batches with batch metadata, seed baseline generation 0 with generated candidates starting at generation 1, plugin score composition, built-in plugin spec attribution in prompt context, finite causal-plugin score validation, CLI built-in plugin alias preflight, manifest-safe configured plugin label validation at config and manifest boundaries, constructor-level built-in plugin cadence validation, custom plugin constructor-signature attribution, validator environment allowlisting with stdout/stderr redaction, best-effort validator timeout process-tree cleanup, opt-in evaluator artifact copy-out, archive-state snapshots with cursor plus full archive contents restore from accepted history, a circle-packing smoke fixture, a small matrix smoke benchmark, a matrix-result report contract, a paper-result certification contract, a systems held-out/reference report contract, a benchmark hardening contract, a scope-checked matrix smoke hardening bundle, an equal-budget ablation-result report contract, an LLM budget report contract, restored runtime budget snapshot consumption, controller budget-event replay, a composed full-runtime restore bundle for compatible surfaces, and a provider cancellation policy contract. Flexible non-code candidate abstractions are documented as a deliberate current code-file-set divergence. Arbitrary-language/build-system runners beyond the declared unsupported policy, language-aware evolve-block marker grammars, future topology and language-runner edge-case collision policy, proposal scoring, semantic proposal-index retrieval, and cross-run proposal tables beyond the bounded hypothesis index, configurable/full validator-metadata prompt policy, selected-backend provider-token section packing outside mutation prompts and exact counters across non-OpenAI provider families, async workers, OS/container-grade network sandboxing, broader non-project build/package/accelerator/provider-output replay provenance, custom plugin package-registry and direct-object constructor-value policy beyond manifest-safe entry-point schemas, live authenticated provider request/model-registry validation beyond credential-presence and client-construction preflight, live provider pricing/default-rate capture beyond configured token-cost estimates, live provider SDK cancellation, timeout-driven stop enforcement and richer runtime cancellation artifacts beyond configured in-run quarantine observations, queued/running async or pending-work budget consumption inside `evolve()` beyond the pre-applied full-runtime restore boundary, async budget accounting, Pareto/frontier primary archive replacement, durable cross-run metric-specific optimization, stable learned/evaluator-provided descriptor models and tested archive rebin semantics beyond insertion-time TF-IDF coordinates, queryable evolutionary database beyond bounded current-run resurfacing, live/retrieval/semantic context selection and deeper per-field prompt context policy beyond the current validated structured surface, migration-event replay, async controller/pending-work resume state, full provider-output/pending-work resumed-trace proof, seeded lineage replay, executed feedback calibration reports beyond the declared report/artifact contract, critique async overlap and calibrated reviewer scoring beyond current synchronous first/last-valid reviewer pools, critique provider isolation, independent per-role live scheduler ownership beyond role-scoped backend eligibility and role budget maps, cross-run provider-failure quarantine/resume policy beyond restored scheduler failure-policy state, provider-output/raw-payload replay, and critique/meta-prompt reward calibration beyond configured reward-accounted roles, benchmark-grade hardening reports beyond the smoke-scope matrix bundle, tensor-decomposition target suites/algorithms, executable independent certifiers/deployment evidence, real systems held-out/reference fixtures, benchmark scripts that emit equal-budget ablation reports, and stronger AlphaEvolve-scale benchmarks remain open. |
| 1504.04909 | MAP-Elites | Foundational archive algorithm | Implemented as `libreevolve/population/map_elites.py` configurable local 3D archive whose default axes are archive selection score (falling back to fitness), fixed-bound serialized-workspace text length, and serialized-workspace TF-IDF diversity against the current elite corpus. `map_elites_descriptor_axes` can instead select normalized evaluator metrics, numeric evaluator metadata, or numeric candidate metadata as behavior descriptors, and archive snapshots persist descriptor-model revision/reference/no-rebin policy metadata. Stable learned/evaluator-provided descriptor modeling, tested archive rebin semantics, richer archive diagnostics, and AlphaEvolve-scale archive/controller semantics remain open. |
| auer-cesa-bianchi-fischer-2002 | UCB1 finite-time analysis | Foundational bandit policy | Implemented as `libreevolve/llm/ensemble.py` heuristic UCB-style backend router over archive-admitted valid fitness improvements; rewards are bounded and call-id attributed, while canonical regret assumptions are explicitly out of scope unless the scheduler is promoted beyond heuristic routing. |
| 2511.17592 | GigaEvo | Framework inspiration | Not implemented as described: no Redis lifecycle database, asyncio DAG engine, insight stage, or concurrent units. Diff/full mutation modes are partially present. |
| 2510.14150 | CodeEvolve | Agentic code-evolution inspiration | Not implemented as described: LibreEvolve has generic prompt-program selection and optional evidence-conditioned template mutation, but no CodeEvolve-style crossover, targeted refinement, modular orchestration, or context-aware recombination. |
| 2511.23473 | ThetaEvolve | Test-time training inspiration | Only `libreevolve/plugins/ttt_rl.py` clipped-reward JSONL export exists through `ttt_rl`; CLI-loaded exports are run-scoped while direct `TTTRLPlugin(log_dir=...)` exports are user-managed external artifacts. Repeated flushes are deduplicated within one plugin instance, malformed examples are rejected before queueing, retained in-memory training examples are capped with overflow export, final artifact metadata flushes pending rows, and export payloads are secret-redacted plus field/aggregate bounded. There is no online RL/GRPO training loop, checkpoint management, resume semantics, or lazy-penalty dynamics. |
| 2602.10233 | ImprovEvolve | Modular search inspiration | Static prompt guidance exists in `libreevolve/plugins/modular.py` and candidate prompt-context metadata labels it as `static_prompt_only` with `operation_selected: static_modular_guidance`, described `generate_config`/`improve`/`perturb` operation names, and false execution/enforcement flags; no enforced or executed generate/improve/perturb loop exists. |
| 2602.15951 | MadEvolve | Domain evolution inspiration | Background only; no free-parameter optimization or innovation report. |
| 2603.14575 | CausalEvolve | Causal-guidance inspiration | Only `libreevolve/plugins/causal.py` token-pattern outcome-factor guidance exists; no LLM causal scratchpad. Factor detection uses the shared compact/canonical SEARCH/REPLACE parser for diff-mode mutations and direct token-pattern scanning for full-mode replacement payloads, fixed factors use pull-once initialization before UCB-like reward scoring, retained outcome history is capped, and malformed non-text mutation evidence is counted instead of crashing, but the detected factors are still fixed local token-pattern categories rather than LLM-discovered causal variables. |
| 2510.06056 | DeepEvolve | Retrieval/debug loop inspiration | Only `libreevolve/plugins/deep_research.py` best-fitness-plus-code/metric/task/context/failure/local-paper-manifest/recent-proposal-hypothesis arXiv/web-search context exists; direct arXiv helper calls validate safe query/result-limit parameters and use HTTPS, live responses are bounded before XML parsing, successful retrieval text is rendered as non-authoritative evidence with explicit delimiters, candidate history records bounded retrieval events with query inputs/policy, bounded/redacted provider-result snapshots, bounded/redacted source metadata, bounded source-content snapshots, audit-only query-overlap relevance scores, summary hashes, redacted provider errors, request URL summaries, transport/payload hashes, trust-policy metadata, cache metadata, oversized-response diagnostics, and active-context query/cache/source-ranking/transport/result hash links, while run manifests record compact retrieval summaries with event counts, source metadata counters, status/source counts, result sizes, synthesis hashes, cache/query/trust policy, and bounded transport/payload fields. Run-local cache snapshots, offline cache replay, plugin artifact summaries for cache snapshot counts/sizes/hashes and provider-result snapshot counts/hashes, local paper manifest title/id query terms, and recent proposal hypothesis query terms exist, but there is no learned or externally scored semantic ranking beyond deterministic query-overlap audit metadata, unbounded full provider-payload persistence, full source-content trust evidence beyond bounded trust-policy metadata, DeepResearch provider-output replay integrated with full-runtime resume, or DeepEvolve-style cross-file debugging/editing loop. |
| 2601.21096 | Magellan | AlphaEvolve compiler-optimization application context | Background only; no compiler-heuristic benchmark or compiler pass runner. |
| 2602.22425 | ArchAgent | AlphaEvolve computer-architecture application context | Background only; no architecture-design simulator or cache-policy benchmark. |
| 2602.16928 | Multiagent Learning | AlphaEvolve MARL algorithm-discovery result context | Background only; no CFR/PSRO benchmark or game-theoretic evaluator. |
| 2603.09172 | Ramsey Numbers | Constructive math benchmark candidate | Not implemented; potential future benchmark; no Ramsey construction verifier or certificate benchmark. |
| 2509.18057 | Hardness of Approximation | AlphaEvolve complexity-theory result context | Background only; no graph/certification benchmark. |
| 2603.06692 | Combinatorics Berczy | Constructive math benchmark candidate | Not implemented; potential future benchmark; no constructive-combinatorics verifier or benchmark harness. |
| 2601.16175 | TTT Discover | Test-time discovery context | Background only; no test-time discovery evaluator or adaptation benchmark. |
| 2603.08679 | Bilateral Trade | AlphaEvolve mechanism-design result context | Background only; no bilateral-trade distribution benchmark. |
| 2601.01235 | Bruhat Intervals | Constructive math benchmark candidate | Not implemented; potential future benchmark; no Bruhat-interval verifier or construction benchmark. |
| 2511.12916 | Fault2Flow | AlphaEvolve-optimized workflow application context | Background only; no fault-to-workflow or human-in-the-loop multi-agent benchmark. |
| 2601.05943 | Global Nonlinear Optimization | Optimization benchmark comparator | Not implemented; potential future benchmark; no nonlinear-programming solver comparison harness. |
| 2506.16750 | Autoconvolution | Constructive math benchmark candidate | Not implemented; potential future benchmark; no autoconvolution certificate verifier or benchmark harness. |
| 2505.16105 | Sums and Differences | Constructive math benchmark candidate | Not implemented; potential future benchmark; no sums-and-differences construction verifier or benchmark harness. |
| 2506.01896 | Sums and Differences II | Constructive math benchmark candidate | Not implemented; potential future benchmark; no second-variant sums-and-differences verifier or benchmark harness. |

AlphaEvolve initial-program provenance note: current manifests and history
preserve safe seed source identity for generation-0 baselines, but they do not
record whether a benchmark seed was simple/random, researcher-idea-seeded,
prior-art-derived, or collaboration-enhanced. AlphaEvolve Section 3.1 reports
matrix runs boosted by human ideas in the initial program, such as stochastic
evaluation or evolutionary approaches; LibreEvolve needs structured
idea-origin metadata and equal-budget seed-variant evidence before making that
class of paper claim.

AlphaEvolve mutation-operator note: LibreEvolve supports the edit payload
surfaces listed in the table, including SEARCH/REPLACE, configured full
replacement, file/block sections, and topology commands. It does not yet have
paper-visible evidence that LLMs construct or adapt higher-level mutation
operator families beyond those fixed local parser surfaces, so the
AlphaEvolve Related Work distinction from handwritten mutation/crossover
operator sets remains an open evidence gap.

AlphaEvolve initial-program validity note: current seed handling can evaluate
and record invalid generation-0 seeds as permissive optimization-pressure
baselines, including examples such as `hello_world`. AlphaEvolve Section 2.1
describes the initial implementation inside evolvable blocks as complete,
though rudimentary, and runnable through the task skeleton/evaluator. LibreEvolve
needs an explicit strict seed-validity policy and benchmark/report evidence
before treating every initial seed baseline as paper-faithful AlphaEvolve
initial-solution evidence.

AlphaEvolve expert-formulation note: local context-source and problem/source
provenance records identify artifacts and rendered prompt context, but they do
not yet capture expert contributor roles, problem-origin notes, formulation
advice, objective/evaluator rationale, or parameter-scope decisions. Section
3.2 reports external mathematicians suggesting problems and advising
formulation, so LibreEvolve needs explicit expert-formulation provenance before
making that class of mathematical benchmark claim.

AlphaEvolve evaluator-metric note: LibreEvolve now reserves boolean `is_valid`
as a local admission gate outside declared `metrics.yaml` objectives and stores
non-scalar evaluator attachments separately, while AlphaEvolve Section 2.1 and
Figure 3 describe evaluator outputs as scalar metric dictionaries maximized by
convention. Paper-facing reports still need explicit metric-name, validity-gate,
and direction-transform evidence before LibreEvolve run outputs can be treated
as AlphaEvolve-comparable scored metric tables.

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
provider pricing/default-rate capture beyond configured estimates, full async worker accounting, independent per-role
live scheduler state, calibrated reward semantics, and quota/budget ownership
beyond role-scoped backend eligibility and role budget maps remain open. Live
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
be restored. Cross-run provider-failure policy proof beyond restored scheduler
state, provider-output/raw-payload replay, hard provider cancellation,
timeout-driven stop behavior, and richer runtime cancellation artifacts beyond
configured in-run quarantine observations remain open.

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
Broader prompt-context evolution remains open for live/external context-source
selection, retrieval/summarization, inspiration selection, and finer-grained
evaluator/LLM-feedback field policy. Prompt-database parity with the solution
program database is also still open: the current `PromptDatabase` is a local
prompt-arm history/scoring store, not a prompt-side MAP-Elites/island archive
with descriptor/objective indexes, archive events, migration/rebin semantics,
or async/controller-resumable prompt work.

AlphaEvolve validator-network note: `validator_network_policy` now records host
network inheritance by default and can install a Python socket-level deny hook
for validator preflight/evaluation. This is policy evidence and an
accidental-egress guard, not OS/container-grade network isolation; the broader
network/container sandboxing gap remains open.

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
minus `reserved_output_tokens`. The remaining gap is automatic selected-backend
provider-token section packing across all prompt roles/provider families and
context surfaces, plus context-policy evolution.

AlphaEvolve island-state note: retained archive-state changes advance the
island round-robin assignment cursor. Non-admitted MAP-Elites attempts, such as
`not_improving_cell`, record their attempted island but do not consume the next
island slot. Final manifests now persist a compact
`runtime.history.archive_state` snapshot with the current cursor and adjacent
sequence counters, and `archive_events.jsonl` persists versioned migration
placement events. The same manifest snapshot now includes `archive_contents`
with per-island MAP-Elites cells, elite-program ids, descriptor policy, and
archive configuration. `load_archive_restore_bundle()` combines that manifest
state with accepted `history.jsonl` records, and
`ProgramDatabase(..., archive_state_snapshot=..., archive_programs_by_id=...)`
can restore both the cursor/counter subset and the cell/elite contents. CLI
full-runtime restore now composes that compatible archive restore bundle with
the runtime RNG, LLM scheduler, budget, and controller-budget replay surfaces;
ordered migration-event replay plus async/provider-output/pending-work resume
remain part of the broader resume gap.

AlphaEvolve rejected-diagnostics note: rejected archive-admission metadata is
kept JSON-safe, but hook-mutated/restored programs with non-finite top-level
fitness or metrics still cannot enter normal strict history. They are
diagnosed through invalid/quarantine streams until a finite rejected-candidate
stream or normalization policy is implemented.

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

AlphaEvolve database-resurfacing note: bounded current-run resurfacing now exists
through `runtime.history.resurfacing_index`,
`ProgramDatabase.resurface_candidates(target_metric=...)`,
`resurface_by_metric()`, `resurface_by_lineage()`,
`resurface_by_descriptor()`, `resurface_by_novelty()`, and
`resurface_by_feedback()`. `runtime.history.hypothesis_index` also exposes
bounded redacted proposal idea/rationale/hypothesis summaries for valid
programs and can feed current-run resurfacing evidence. This narrows the
remaining database gap to durable cross-run query/index tables, full
metric-vector and feedback/artifact-content ranking, proposal scoring,
semantic/cross-run novelty or hypothesis retrieval, schema migrations, and
replayable sampling policies, not the absence of any resurfacing API or
proposal metadata capture.

AlphaEvolve duplicate-work note: generated candidate ids include workspace-hash
identity provenance, but LibreEvolve does not yet expose paper-visible evidence
for source/workspace deduplication, evaluation-cache reuse, or documented
stochastic re-evaluation of identical proposals. The remaining gap is a
canonical hash/evaluator-cache scope with cache hit/miss/re-evaluation
telemetry and budget accounting for repeated previously explored programs.

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
accounting.

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
service/API versions, live provider pricing/default-rate capture beyond configured estimates,
and accelerator budget/accounting evidence. Environment provenance is useful
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
recorded without values.

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
normalized values. Call telemetry also persists `backend_defaults` for
LibreEvolve's effective local output-token caps, provider internal retry caps,
configured request timeouts, API modes, and OpenAI reasoning/API-mode policy;
remote provider-side defaults and pricing are not inferred. Structured
system/developer/user prompt roles are serialized as hash-only
`prompt_role_policy` metadata, not raw instruction text. Endpoint/client context now has an
explicit validated built-in backend surface for OpenAI `base_url`,
`organization`, and `project`, Anthropic `base_url`, and Ollama `host`, and
accepted values are recorded in manifests plus call `client_context`
telemetry. Omitted fields still inherit SDK/environment defaults, so
unconfigured proxy hosts, organizations/projects, API hosts, and local Ollama
server selection remain outside self-describing artifacts. There is also no
first-class Google/Gemini backend yet, so AlphaEvolve's published Gemini 2.0
Flash/Gemini 2.0 Pro model mix currently requires either a custom backend with
separate evidence or a future provider/plugin contract before it can be treated
as provider-parity reproduction evidence. AlphaEvolve's Table 1 sample-count
claim is also not yet reproduced: current budgets and ablation schemas can
account for LLM calls and provider usage, but no report yet proves useful
target progress in thousands-scale generated/evaluated proposal counts versus
FunSearch-style much larger sample budgets or small-base-model alternatives.

Candidate-abstraction evidence is also still missing: the primary row records
LibreEvolve's code-file-set abstraction as a current divergence, but Section
2.1 and the Discussion describe choosing between direct solution search,
constructor functions, bespoke search algorithms, and paired solution/search
representations, with different biases for symmetric and non-symmetric
problems. LibreEvolve still needs benchmark metadata and equal-budget reports
that justify and compare those abstraction choices.

Code-scale evidence is separate from workspace mechanics. AlphaEvolve Table 1
reports evolving entire code files, hundreds of lines, arbitrary languages, and
multi-component algorithms. LibreEvolve currently has Python-primary multi-file
workspaces, topology mutations, materialization diagnostics, full-workspace
prompt/export paths, and a small `workspace_math` smoke fixture, but it lacks a
paper-facing benchmark/report with hundreds-line generated programs, coupled
cross-file/component edits, non-Python or build-runner execution, evaluator
budget evidence, validity/admission rates, and score progress on a realistic
codebase-scale task.

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

AlphaEvolve proposal-capture note: LibreEvolve treats leading proposal metadata
as a structured mutation-response preamble. Short `IDEA:`, `RATIONALE:`, and
`HYPOTHESIS:` fields and bounded multiline `[IDEA]...[/IDEA]`,
`[RATIONALE]...[/RATIONALE]`, and `[HYPOTHESIS]...[/HYPOTHESIS]` blocks are
stored as proposal metadata, while ambiguous wrapped colon-style metadata
before later proposal markers is rejected before mutation application rather
than silently becoming candidate code. Ordinary natural-language explanation
before or after mutation sections is still rejected unless it uses those
structured proposal fields, which is stricter than the explanatory preamble
shown before the Figure 3(c) AlphaEvolve diff example.

AlphaEvolve mutation-mode note: LibreEvolve implements canonical diff parsing
and configured `full` replacement mode, but `Config.mutation_mode` is currently
a run-wide prompt/parser contract. AlphaEvolve Section 2.3 distinguishes
diff-block output for larger codebases from direct full-code output for very
short code or rewrite-friendly cases, so LibreEvolve still needs adaptive
per-candidate mutation-mode policy and telemetry before claiming that
diff-versus-full prompting follows the paper's conditions.

AlphaEvolve scope-boundary note: the paper explicitly treats automated
evaluation as both a core advantage and a limitation, keeping tasks that require
manual experimentation out of scope and describing LLM-provided evaluation of
ideas as possible but not the optimized AlphaEvolve setting. LibreEvolve's
current feedback graders run around executable candidate evaluation and its
proposal metadata captures bounded idea/rationale/hypothesis text; there is no
separate AI-Co-Scientist-style stage that evaluates high-level ideas before
transitioning into code execution. Paper-facing scientific-discovery claims
should remain scoped to machine-gradeable evaluator workflows until
problem/run/report metadata labels manual-experiment exclusion, LLM-only idea
feedback, and transition criteria into executable evaluation.

AlphaEvolve run-inspection note: `libreevolve show` streams history rows and
validates ids, metrics, current-history evaluation shape, and archive
diagnostics, including malformed unselected retained rows. Its non-archive
source/workspace display path remains selected-row scope, but streamed
current and legacy history rows now validate `code`, `files`, and
`primary_file` payload shape before any best-looking row is printed. It still
does not summarize every unselected row's source/workspace payloads as
whole-run source integrity evidence.

MAP-Elites cell-inspection note: `libreevolve show` rejects malformed current
history cells by arity/type/non-negativity and, when
`manifest.json.config.map_elites_bins` is present, rejects coordinates outside
that configured per-axis bin range. Histories without manifest/bin metadata
remain legacy-limited to arity/type/non-negative validation.

## TODO coverage cross-references

This maintained map ties each implementation-status row to backlog evidence.
The active column points only at currently open backlog files or grouped open
gap families; completed files preserve implemented decisions and prior
paper-index cleanups. Source-specific active gaps now appear across
`docs/todo/code.md`, `docs/todo/papers.md`, `docs/todo/roadmap.md`, and
`docs/todo/readme.md`; completed evidence remains split by the older
completed-ledger files listed below.

| ID | Active gap evidence | Completed/grouped evidence |
|---|---|---|
| 2506.13131 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 1504.04909 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| auer-cesa-bianchi-fischer-2002 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2511.17592 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2510.14150 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` |  |
| 2511.23473 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2602.10233 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2602.15951 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2603.14575 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2510.06056 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2601.21096 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2602.22425 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2602.16928 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2603.09172 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` |  |
| 2509.18057 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2603.06692 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` |  |
| 2601.16175 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` |  |
| 2603.08679 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2601.01235 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` |  |
| 2511.12916 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2601.05943 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` | `docs/todo/Completed/papers.md` |
| 2506.16750 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` |  |
| 2505.16105 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` |  |
| 2506.01896 | `docs/todo/code.md`; `docs/todo/papers.md`; `docs/todo/roadmap.md`; `docs/todo/readme.md` |  |

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
- `libreevolve/problems/benchmarks/example_scope.py`: shipped-example scope
  registry that keeps `hello_world`, `sorting`, `workspace_math`,
  `matrix_multiplication`, and `circle_packing` marked as smoke-only and not
  AlphaEvolve-comparable. The standard paper-manifest validator checks these
  records directly.
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
  `libreevolve.alphaevolve_matrix_subset_scope.v1` records the paper-facing
  matrix subset boundary between `appendix_a_full` (`54` rows: `38` matched,
  `14` surpassed, `2` fell behind), `main_text_mnp_le_5` (`20` rows: `17`
  matched, `3` surpassed, `0` fell behind), and `table_2_selected` (`16`
  displayed rows: `2` matched, `14` surpassed, `0` fell behind). It validates
  inclusion predicates, target ids, outcome counts, out-of-scope rows, and
  Table 2/Table 3 source linkage, but no local report/export emits those
  subset-scope records yet.
  `libreevolve.alphaevolve_appendix_a_matrix_resource_frontier.v1` records the
  paper-source larger-target boundary for sizes beyond `<5,5,5>`, 1000 random
  seeds, single-GPU evaluators, frequent OOM, and further-optimization need.
  It does not provide local matrix scaling attempts, measured GPU memory, OOM
  artifacts, reduced-seed tradeoffs, or exclusion rationale.
  `write_strassen_2x2_publication_bundle()` provides one checked Strassen
  baseline for `mm_2x2x2` with canonical algorithm, certificate, notebook,
  report, and artifact inventory files. It still does not provide discovered
  tensor-decomposition algorithms, certificates, or notebook exports across the
  full Appendix A target suite. It also validates matrix result metadata after
  the report exists. `libreevolve.matrix_near_integrality_evidence.v1` now
  validates declared search-time evidence that candidates were instructed to
  produce near-integral decompositions, rounded to integer or half-integer
  coefficients, and linked to exactness certificates as in AlphaEvolve Section
  3.1, but no local matrix benchmark runner emits those records yet. Its
  `libreevolve.matrix_scalar_field_evidence.v1` contract now validates declared
  scalar-field provenance for complex-valued algorithms, field characteristic,
  exact coefficient representation, finite-field caveats, and certificate scope
  for exact real/complex applicability, but no local matrix benchmark runner
  emits exact complex decomposition/certificate artifacts for those claims yet.
  `libreevolve.matrix_tensor_rank_evidence.v1` now validates declared rank
  claims that distinguish matrix-multiplication tensor decompositions from
  non-tensor multiplication algorithms, including tensor-identity certificate
  scope, recursive applicability, target-tensor links, exactness-certificate
  links, and source-note caveats for non-recursive algorithms, but no local
  matrix benchmark runner emits those target-tensor/certificate artifacts yet.
  `libreevolve.matrix_headline_historicity_evidence.v1` validates declared
  provenance for the `mm_4x4x4` complex rank-48 headline, including
  characteristic-zero scope, 56-year first-below-49 wording flags, recursive
  Strassen rank-49 comparison, finite-field-only Fawzi rank-47 caveat, source
  refs, and links to result, scalar-field, tensor-rank, Figure 4, Figure 9,
  and companion Colab evidence. No local matrix benchmark runner emits those
  headline/source/decomposition/certificate artifacts yet.
  `libreevolve.matrix_sweep_space_evidence.v1`
  now validates declared Figure 9-style sweep provenance for the evolved
  `sweep` function, user-provided `hyper` library identity, hyperparameter
  range declarations, sampled configuration ids, per-sweep losses/ranks, and
  linkage from selected sweep configurations to final decomposition and
  exactness-certificate artifacts. No local matrix benchmark runner emits
  those sweep-space records yet.
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
  `alphaevolve_ready`, and readiness gating, but it does not provide real
  compiler, hardware, kernel, scheduling, or systems fixtures. For scheduling,
  it also does not yet require Borg-style feasibility-boundary evidence that
  an evolved heuristic only ranks machines already deemed feasible by an
  external scheduler and cannot directly alter admission or placement
  constraints, nor does it require mission-critical deployment evidence such
  as interpretable heuristic structure, debuggability/operator review,
  predictability checks, rollout-risk evidence, or comparison against less
  interpretable learned-policy baselines. For kernel reports, it does not yet
  require Pallas/Gemini-style input-shape corpus provenance, deterministic
  train/eval split records, real TPU runtime measurement artifacts, baseline
  tiling-heuristic identity, or unchanged-operation correctness-by-construction
  evidence. For hardware, it
  does not yet require RTL/EDA evidence such as
  Verilog source boundaries, synthesis/PPA metric provenance, equivalence or
  formal verification artifacts, timing constraints, designer signoff, or
  downstream synthesis-tool confirmation, nor hardware adoption evidence such
  as RTL-stage workflow placement, standard-Verilog trust/adoption rationale,
  upcoming-chip integration, or time-to-market impact. For compiler-generated
  IR tasks, it
  does not yet require per-edit randomized reference-check traces, reference
  implementation hashes, input-generator provenance, IR-origin/editability
  constraints, compiler-generated/already-optimized baseline provenance,
  numerical tolerance policy, kernel versus pre/postprocessing attribution,
  final expert all-input signoff scope, or calibrated result-claim records
  mapping finite metrics to
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
  seeds, retries, and stage/sample budgets. They are not yet AlphaEvolve
  Section 2.4 hypothesis-testing cascades: no report/schema records
  statistical test parameters, confidence intervals, p-values, sequential
  stopping, false-promotion/false-rejection budgets, or explicit
  small-scale-filter versus main-test promotion roles.
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
  curve-summary, and raw-seed-trace artifacts. It does not render plots or
  prove that benchmark scripts emitted those artifacts.
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
- `libreevolve/problems/benchmarks/matrix_exhibits.py`: AlphaEvolve Appendix A
  Figure 9a-9c magnified matrix-diff metadata contract. It validates the three
  panel ids, paper pages 35-37, Figure 4 caption linkage, `mm_4x4x4` rank-48
  target mapping, ordered line spans, source-diff/rendered-image/OCR artifact
  hashes, semantic component coverage for optimizer, initialization, noise,
  clipping, loss, discretization, and sweep changes, and links to matrix
  result, sweep-space, exactness-certificate, and companion notebook evidence.
  It does not render or commit the appendix panel artifacts.
- `libreevolve/problems/benchmarks/paper_artifact_roles.py`: AlphaEvolve paper
  artifact-role attribution contract. It validates the PDF page 23 contribution
  records for the paper-figure creator initials and the accompanying Google
  Colab assembler initials, with stable artifact ids, artifact types,
  creator/assembler roles, exact initials and ordering, source section/page
  metadata, and source phrases. It does not verify rendered figure files or a
  retrieved companion-notebook artifact.
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
  hard provider cancellation remain open.
- `libreevolve/llm/cancellation_policy.py`: provider timeout/cancellation
  policy contract. It validates timeout/cancellation rules, role-scoped budget
  actions, artifact requirements, hard-cancel readiness gated on
  `cancellation_record` artifact evidence, and hashed cancellation artifacts,
  but live provider SDK cancellation, timeout-driven stop enforcement, and
  richer runtime cancellation artifacts beyond configured in-run quarantine
  observations remain open.
- `libreevolve/problems/examples/sorting`: neutral plateau/diversity smoke
  fixture. The bubble-sort seed already reaches `accuracy == 1.0`, so this
  example can demonstrate mutation handling and same-score implementation
  variety but is not seed-to-best optimization-pressure evidence.

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
  model-evaluation artifact derived from evolved programs.
