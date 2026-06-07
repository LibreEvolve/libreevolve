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
manifest IDs by the same validator, and symlink or Windows reparse-point backed
PDF entries are rejected before byte/hash validation.
The same validation command checks
`libreevolve/problems/benchmarks/alphaevolve_appendix_b.json`, which records a
coverage decision for each AlphaEvolve Appendix B constructive-math family. The
registry currently marks only the unit-square circle-packing fixture as
`implemented_smoke`; all other Appendix B families are explicit planned entries
with objective direction, target/baseline status, construction/certificate
artifact shape, certification need, rationale, and AlphaEvolve citation
metadata.
It also checks `libreevolve/problems/benchmarks/alphaevolve_ablations.json`,
which defines the AlphaEvolve Figure 8 ablation report contract for the full
system, `No evolution`, `No context in the prompt`, `No meta prompt evolution`,
`No full-file evolution`, and `Small base LLM only`. The registry requires
component-disable assertions, three independent seeds, target aggregation,
equal-budget fractions, required result fields, and AlphaEvolve citation
metadata, but it does not claim those reports have been run.
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
deterministic query-overlap audit metadata, full source-content trust policy,
replayable transport/failure decisions, and full run resume remain open. Treat live
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
| 2506.13131 | AlphaEvolve | Primary specification target | Partially implemented: evolve blocks with explicit Python-file marker boundaries and unsupported non-Python marker diagnostics, local text-workspace candidates with Python-primary seed-workspace loading, manifest-visible candidate-language policy, and manifest-visible size reject budgets, workspace topology mutations, empty-file creation through full-mode file sections, rejection of ambiguous, overlong, and generated dot-prefixed candidate paths, unknown full-block target rejection, CLI happy-path full-workspace best export, workspace materialization with recursive link/junction preflight and typed materialization-failure diagnostics, plus basic candidate imports in local validators, mutation modes including canonical SEARCH/REPLACE diff compatibility, proposal-rationale capture with selected parent/inspiration prompt rendering, selected post-critique proposal provenance, preamble-only proposal stripping, structured evaluator results, schema-validated evaluator result dataclasses, structured non-JSON evaluator-return diagnostics, finite explicit Program fitness semantics, schema-safe redacted synthetic diff-error diagnostics, complete declared metric vectors for synthetic framework-generated evaluator failures, stage-threshold stops that retain real validator metric vectors, configurable local cascades with manifest-safe non-colliding stage labels, aggregate workspace syntax diagnostics, evaluator contract preflight before run-artifact mutation, strict scalar evaluator-output validation with reserved boolean validity, strict metric-bound ordering plus out-of-range clamp diagnostics, primary metric normalization, equal-weight normalized declared-metric archive selection, diagnostic Pareto frontier snapshots over declared normalized metrics, feedback-sourced objective metrics filled by configured graders, workspace-aware local MAP-Elites complexity/diversity inputs, configurable in-memory parent/inspiration sampling, prompt sampler/context ingestion with deterministic selection provenance, unmatched include diagnostics, secret-safe context source/pattern labels, hidden-context opt-in policy, skipped diagnostics for context extraction failures, default-fail explicit include extraction policy with opt-in degraded warning diagnostics, resource-bounded local context ingestion, and exact PDF excerpt page/span citations. Also implemented: bounded execution-output, validator-diagnostic, validator-metadata, and grader-feedback prompt summaries, prompt-program database and optional meta-prompt mutation, structured prompt-program context-policy hooks, configurable synchronous critique reviewer pools with first/last-valid aggregation, synchronous critique with bounded/redacted prompt construction, retained critique metadata, and deterministic no-valid-mutation selection provenance, LLM feedback graders with full-workspace feedback prompts, configurable feedback-failure retries/policies, and manifest-safe grader labels, manifests, run identity/collision policy, source-root Git/source/problem provenance, generated-run artifact classification for problem provenance, bounded source/problem provenance file reads, cwd-independent generated-root provenance exclusion, final effective config validation after CLI overrides, secret-safe and bounded plugin-module provenance, source/problem included-file and skipped-diagnostics provenance digests, UTC runtime wall-clock manifest timestamps with monotonic elapsed-budget linkage, manifest-runtime-aware `show` status for completed/aborted/partial runs, typed missing/invalid/invalid-schema `pyproject.toml` provenance, direct evaluator entrypoint provenance, enforced problem-local evaluator dependency provenance, secret-safe persisted evaluator path metadata, streamed evaluator source hashing with read-error diagnostics, validator helper import precedence checks, manifest-safe candidate/program identifiers, skipped seed setup diagnostics, local run-budget accounting with stop reasons, logical LLM-call caps, and provider-attempt/token/configured-cost/latency stops, provider-free zero-generation seed baselines, run-local framework RNG isolation from process-global Python `random`, persisted and CLI-restorable framework RNG snapshots, CLI-scoped provider credential-presence and local client-construction preflight for mutation-capable runs, manifest-safe backend model identifiers, configured custom import-path LLM backends, configured entry-point plugin loading with manifest-safe constructor options and declared constructor-option schemas, restored/replay backend spec and prompt validation, ensemble prompt-size enforcement before registry/custom backend calls, selected PEP 621 metadata and NumPy numerical-runtime provenance, normalized ensemble-level LLM call telemetry with deterministic call ids, validated prompt/role labels, request parameters, client context, copied telemetry snapshots, malformed-output failure records, and redacted provider errors, candidate history/admission provenance, bounded proposal-hypothesis history indexes, typed static sidecars with bounded base64 generated/replaced static/binary members, direct raw binary workspace entries normalized into immutable static members, verified source-copy static asset materialization, policy-backed bounded-file prompt rendering for copied UTF-8 evaluator artifacts, heuristic prompt section packing under `prompt_max_chars` / `prompt_max_estimated_tokens`, explicit per-role LLM backend routing policy with role route telemetry, sequential sibling proposal batches with batch metadata, seed baseline generation 0 with generated candidates starting at generation 1, plugin score composition, built-in plugin spec attribution in prompt context, finite causal-plugin score validation, CLI built-in plugin alias preflight, manifest-safe configured plugin label validation at config and manifest boundaries, constructor-level built-in plugin cadence validation, custom plugin constructor-signature attribution, validator environment allowlisting with stdout/stderr redaction, best-effort validator timeout process-tree cleanup, opt-in evaluator artifact copy-out, archive-state snapshots with cursor plus full archive contents restore from accepted history, circle packing, a small matrix smoke benchmark, a matrix-result report contract, a paper-result certification contract, a systems held-out/reference report contract, a benchmark hardening contract, an executed ablation-result contract, an LLM budget report contract, restored runtime budget snapshot consumption, and a provider cancellation policy contract. Flexible non-code candidate abstractions are documented as a deliberate current code-file-set divergence. Arbitrary-language/build-system runners beyond the declared unsupported policy, language-aware evolve-block marker grammars, future topology and language-runner edge-case collision policy, proposal scoring and semantic proposal-index retrieval beyond the bounded hypothesis index, configurable/full validator-metadata prompt policy, provider-token tokenizer-backed prompt section fitting, async workers, OS/container-grade network sandboxing, broader non-project build/package/accelerator/provider-output replay provenance, custom plugin package-registry and direct-object constructor-value policy beyond manifest-safe entry-point schemas, live provider authentication, live provider pricing/cost capture, live provider SDK cancellation, timeout-driven stop/quarantine enforcement, direct event-stream budget consumption inside `evolve()`, async budget accounting, frontier-driven or metric-specific multi-objective search, queryable evolutionary database, richer prompt context policy, migration-event replay, controller/pending-work resume state, full resume, seeded lineage replay, feedback calibration, critique async overlap and calibrated reviewer scoring, critique provider isolation, cross-run provider-failure quarantine/resume policy, provider-output replay, and critique/meta-prompt reward calibration beyond configured reward-accounted roles, emitted hardening reports from real benchmark fixtures, tensor-decomposition target suites/algorithms, executable independent certifiers/deployment evidence, real systems held-out/reference fixtures, benchmark scripts that emit equal-budget ablation reports, and stronger AlphaEvolve-scale benchmarks remain open. |
| 1504.04909 | MAP-Elites | Foundational archive algorithm | Implemented as a configurable local 3D archive whose default axes are archive selection score (falling back to fitness), fixed-bound serialized-workspace text length, and serialized-workspace TF-IDF diversity against the current elite corpus. `map_elites_descriptor_axes` can instead select normalized evaluator metrics, numeric evaluator metadata, or numeric candidate metadata as behavior descriptors. Stable learned diversity descriptor modeling or rebinning, richer archive diagnostics, and AlphaEvolve-scale archive/controller semantics remain open. |
| auer-cesa-bianchi-fischer-2002 | UCB1 finite-time analysis | Foundational bandit policy | Implemented as a heuristic UCB-style backend router over archive-admitted valid fitness improvements; rewards are bounded and call-id attributed, while canonical regret assumptions are explicitly out of scope unless the scheduler is promoted beyond heuristic routing. |
| 2511.17592 | GigaEvo | Framework inspiration | Not implemented as described: no Redis lifecycle database, asyncio DAG engine, insight stage, or concurrent units. Diff/full mutation modes are partially present. |
| 2510.14150 | CodeEvolve | Agentic code-evolution inspiration | Not implemented as described: LibreEvolve has generic prompt-program selection and optional evidence-conditioned template mutation, but no CodeEvolve-style crossover, targeted refinement, modular orchestration, or context-aware recombination. |
| 2511.23473 | ThetaEvolve | Test-time training inspiration | Only clipped-reward JSONL export exists through `ttt_rl`; CLI-loaded exports are run-scoped while direct `TTTRLPlugin(log_dir=...)` exports are user-managed external artifacts. Repeated flushes are deduplicated within one plugin instance, malformed examples are rejected before queueing, retained in-memory training examples are capped with overflow export, final artifact metadata flushes pending rows, and export payloads are secret-redacted plus field/aggregate bounded. There is no online RL/GRPO training loop, checkpoint management, resume semantics, or lazy-penalty dynamics. |
| 2602.10233 | ImprovEvolve | Modular search inspiration | Static prompt guidance exists and candidate prompt-context metadata labels it as `static_prompt_only` with `operation_selected: static_modular_guidance`, described `generate_config`/`improve`/`perturb` operation names, and false execution/enforcement flags; no enforced or executed generate/improve/perturb loop exists. |
| 2602.15951 | MadEvolve | Domain evolution inspiration | Background only; no free-parameter optimization or innovation report. |

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
provider pricing, full async worker accounting, independent per-role
routing/quotas, and critique/meta-prompt reward semantics remain open. Live
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
for exhausted reward-accounted failures. Cross-run provider-failure policy,
provider-output replay, remaining-run deadline propagation, hard provider
cancellation, and timeout-driven stop/artifact behavior remain open.

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
evaluator/LLM-feedback field policy.

AlphaEvolve validator-network note: `validator_network_policy` now records host
network inheritance by default and can install a Python socket-level deny hook
for validator preflight/evaluation. This is policy evidence and an
accidental-egress guard, not OS/container-grade network isolation; the broader
network/container sandboxing gap remains open.

AlphaEvolve prompt-budget note: mutation prompt diagnostics now include
`section_budget` with schema `libreevolve.prompt_section_budget.v1`. It records
per-placeholder priorities, hashes, character counts, estimated tokens,
required/optional totals, template overhead, and whether required sections fit
the configured character cap before final truncation. It also records
deterministic heuristic character-budget packing decisions for omitted optional
sections. This is not a provider-token section packer; real provider-token
fitting and context-policy evolution remain open.

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
full-resume wiring and migration-event replay remain part of the broader resume
gap.

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
service/API versions, provider cost or remote provider-side default capture,
and accelerator budget/accounting evidence. Environment provenance is useful
package name/version, selected and extra `[project]` metadata, known-lockfile
hash, pip-freeze and pip-config hash/preview, installed-distribution `WHEEL`
tag and source/install metadata, NumPy config summary, provider SDK-version
evidence, bounded accelerator runtime hint/probe evidence, and audit-only
policy evidence rather than complete reproduction evidence.

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
schema policy, and richer custom package-registry semantics remain open; direct
custom plugin constructor signature shape is recorded without values.

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
server selection remain outside self-describing artifacts.

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
than silently becoming candidate code.

AlphaEvolve run-inspection note: `libreevolve show` streams history rows and
validates ids, metrics, current-history evaluation shape, and archive
diagnostics, including malformed unselected retained rows. Its non-archive
source/workspace display path remains selected-row scope; it does not yet
validate or summarize every unselected row's `code`, `files`, or
`primary_file` payloads as whole-run source integrity evidence.

MAP-Elites cell-inspection note: `libreevolve show` rejects malformed current
history cells by arity/type/non-negativity and, when
`manifest.json.config.map_elites_bins` is present, rejects coordinates outside
that configured per-axis bin range. Histories without manifest/bin metadata
remain legacy-limited to arity/type/non-negative validation.
| 2603.14575 | CausalEvolve | Causal-guidance inspiration | Only token-pattern outcome-factor guidance exists; no LLM causal scratchpad. Factor detection uses the shared compact/canonical SEARCH/REPLACE parser for diff-mode mutations and direct token-pattern scanning for full-mode replacement payloads, fixed factors use pull-once initialization before UCB-like reward scoring, retained outcome history is capped, and malformed non-text mutation evidence is counted instead of crashing, but the detected factors are still fixed local token-pattern categories rather than LLM-discovered causal variables. |
| 2510.06056 | DeepEvolve | Retrieval/debug loop inspiration | Only best-fitness-plus-code/metric/task/context/failure/local-paper-manifest/recent-proposal-hypothesis arXiv/web-search context exists; direct arXiv helper calls validate safe query/result-limit parameters and use HTTPS, live responses are bounded before XML parsing, successful retrieval text is rendered as non-authoritative evidence with explicit delimiters, candidate history records bounded retrieval events with query inputs/policy, bounded/redacted provider-result snapshots, bounded/redacted source metadata, bounded source-content snapshots, audit-only query-overlap relevance scores, summary hashes, redacted provider errors, request URL summaries, transport/payload hashes, trust-policy metadata, cache metadata, oversized-response diagnostics, and active-context query/cache/source-ranking/transport/result hash links, while run manifests record compact retrieval summaries with event counts, source metadata counters, status/source counts, result sizes, synthesis hashes, cache/query/trust policy, and bounded transport/payload fields. Run-local cache snapshots, offline cache replay, plugin artifact summaries for cache snapshot counts/sizes/hashes and provider-result snapshot counts/hashes, local paper manifest title/id query terms, and recent proposal hypothesis query terms exist, but there is no learned or externally scored semantic ranking beyond deterministic query-overlap audit metadata, unbounded full provider-payload persistence, full source-content trust policy, full run resume, or DeepEvolve-style cross-file debugging/editing loop. |
| 2601.21096 | Magellan | AlphaEvolve compiler-optimization application context | Background only; no compiler-heuristic benchmark or compiler pass runner. |
| 2602.22425 | ArchAgent | AlphaEvolve computer-architecture application context | Background only; no architecture-design simulator or cache-policy benchmark. |
| 2602.16928 | Multiagent Learning | AlphaEvolve MARL algorithm-discovery result context | Background only; no CFR/PSRO benchmark or game-theoretic evaluator. |
| 2603.09172 | Ramsey Numbers | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2509.18057 | Hardness of Approximation | AlphaEvolve complexity-theory result context | Background only; no graph/certification benchmark. |
| 2603.06692 | Combinatorics Berczy | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2601.16175 | TTT Discover | Test-time discovery context | Background only. |
| 2603.08679 | Bilateral Trade | AlphaEvolve mechanism-design result context | Background only; no bilateral-trade distribution benchmark. |
| 2601.01235 | Bruhat Intervals | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2511.12916 | Fault2Flow | AlphaEvolve-optimized workflow application context | Background only; no fault-to-workflow or human-in-the-loop multi-agent benchmark. |
| 2601.05943 | Global Nonlinear Optimization | Optimization benchmark comparator | Not implemented; potential future benchmark; no nonlinear-programming solver comparison harness. |
| 2506.16750 | Autoconvolution | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2505.16105 | Sums and Differences | Constructive math benchmark candidate | Not implemented; potential future benchmark. |
| 2506.01896 | Sums and Differences II | Constructive math benchmark candidate | Not implemented; potential future benchmark. |

## TODO coverage cross-references

This maintained map ties each implementation-status row to backlog evidence.
The active column points only at currently open backlog files or grouped open
gap families; completed files preserve implemented decisions and prior
paper-index cleanups. `docs/todo/readme.md` and `docs/todo/roadmap.md`
currently have no active paper-row-specific items, so they appear only in
completed evidence where relevant.

| ID | Active gap evidence | Completed/grouped evidence |
|---|---|---|
| 2506.13131 | `docs/todo/papers.md`; `docs/todo/code.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/code.md` |
| 1504.04909 | `docs/todo/papers.md` | `docs/todo/Completed/archive_policy.md`; `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |
| auer-cesa-bianchi-fischer-2002 | None active | `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/code.md` |
| 2511.17592 | `docs/todo/papers.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2510.14150 | `docs/todo/papers.md` | `docs/todo/Completed/readme.md` |
| 2511.23473 | None active | `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md` |
| 2602.10233 | None active | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2602.15951 | None active | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2603.14575 | None active | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2510.06056 | `docs/todo/papers.md`; `docs/todo/code.md` | `docs/todo/Completed/papers.md`; `docs/todo/Completed/roadmap.md`; `docs/todo/Completed/readme.md`; `docs/todo/Completed/code.md` |
| 2601.21096 | `docs/todo/papers.md` grouped background benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2602.22425 | `docs/todo/papers.md` grouped background benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2602.16928 | `docs/todo/papers.md` grouped background benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2603.09172 | `docs/todo/papers.md` grouped Appendix B / benchmark-fixture gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2509.18057 | `docs/todo/papers.md` grouped background certification gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2603.06692 | `docs/todo/papers.md` grouped Appendix B / benchmark-fixture gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2601.16175 | `docs/todo/papers.md` grouped constructive-math benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2603.08679 | `docs/todo/papers.md` grouped background benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2601.01235 | `docs/todo/papers.md` grouped constructive-math benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2511.12916 | `docs/todo/papers.md` grouped background benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2601.05943 | `docs/todo/papers.md` grouped comparator benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2506.16750 | `docs/todo/papers.md` grouped constructive-math benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2505.16105 | `docs/todo/papers.md` grouped constructive-math benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |
| 2506.01896 | `docs/todo/papers.md` grouped constructive-math benchmark gap | `docs/todo/Completed/papers.md`; `docs/todo/Completed/readme.md` |

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
  `alphaevolve_appendix_a` must match that registry. It still does not provide
  tensor-decomposition algorithms, certificates, or notebook exports.
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
  compiler, hardware, kernel, scheduling, or systems fixtures.
- `libreevolve/problems/benchmarks/benchmark_hardening.py`: anti-gaming
  hardening report contract. It validates protected benchmark signals,
  shortcut threats, protected-signal links for each shortcut threat, detector
  strategies, passed negative fixtures, and hashed hardening artifacts, but
  real benchmark runners still need to emit these reports from actual
  anti-gaming fixtures.
- `libreevolve/problems/benchmarks/ablation_results.py`: executed ablation
  result report contract. It validates all six AlphaEvolve Figure 8 variants,
  declared targets, exactly three seeds, required equal-budget fractions,
  finite scores, consumed-budget consistency, consistent budget unit/limit per
  seed curve and across all variants/seeds for each target, passed component
  assertions, and hashed curve artifacts, but no benchmark script emits these
  reports yet.
- `libreevolve/llm/budget_report.py`: LLM role/retry budget report contract.
  It validates mutation, critique, and feedback role budgets, provider-internal
  retry attempts, token/cost/wall-clock limits and usage, persisted
  resume-state hashes, restored-state consistency, and paper-budget readiness.
  Runtime manifests now emit self-validated report instances with observed
  per-role usage and retained per-call provider retry details when LLM
  call-history rows are available. Runtime token/cost/time stop enforcement,
  restored runtime budget snapshot consumption, and emitted controller
  budget-event logs are wired, while direct event-stream budget consumption
  inside `evolve()`, async/pending-work composition, and hard provider
  cancellation remain open.
- `libreevolve/llm/cancellation_policy.py`: provider timeout/cancellation
  policy contract. It validates timeout/cancellation rules, role-scoped budget
  actions, artifact requirements, hard-cancel readiness gated on
  `cancellation_record` artifact evidence, and hashed cancellation artifacts,
  but live provider SDK cancellation and timeout-driven stop/quarantine
  enforcement remain open.
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
