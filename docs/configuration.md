# Configuration

Configuration is assembled from three sources, in this order:

1. `Config` defaults in [`libreevolve/core/config.py`](../libreevolve/core/config.py)
2. optional problem-local `config.yaml`
3. CLI overrides from [`libreevolve/cli.py`](../libreevolve/cli.py)

The final merged effective config is validated once after CLI overrides are
applied. A higher-precedence CLI value can therefore replace an invalid
lower-precedence scalar or backend value before validation.
The CLI treats `config.yaml` as a problem-local setup source: it must be absent
or a regular file, not a symlink, Windows junction, or directory. When present,
its `path`, `status`, SHA-256 hash, and byte count are written to
`manifest.provenance.config`; when absent, the manifest records an explicit
`status: absent` config-source record.

`.env` is loaded by the `run` command during run setup with `override=True` for
provider clients, before backend preflight. Repository `.env` values therefore
take precedence over same-named parent-process environment values for evolution
runs. Importing `libreevolve.cli` and using `libreevolve show` do not load
`.env`. Run manifests record non-secret dotenv provenance under
`manifest.provenance.dotenv`, including status, override policy, source
hash/byte count, and key names without values.
Validator subprocesses do not inherit that parent environment by default.
They run with a minimal environment plus names listed in
`validator_env_allowlist`, so provider keys such as `OPENAI_API_KEY` are hidden
from `validate.py` unless explicitly allowlisted.

## `Config` fields

### Evolution

- `max_generations` (`1000`): generations to run.
- `max_evaluations` (`null`): optional cap on top-level seed/candidate
  evaluations. Configured-stage subprocess attempts and samples are reported as
  separate consumed counters and can be capped by their own run-wide limits.
- `max_evaluator_seconds` (`null`): optional cap on cumulative evaluator
  elapsed seconds recorded from `EvaluationResult.elapsed_sec`.
- `max_evaluator_subprocess_attempts` (`null`): optional cap on cumulative
  validator subprocess attempts recorded in structured evaluation accounting.
- `max_evaluator_stage_samples` (`null`): optional cap on configured-stage
  samples consumed across seed/candidate evaluations.
- `max_evaluator_retry_attempts` (`null`): optional cap on evaluator retry
  attempts consumed by configured stages.
- `max_evaluator_timeouts` (`null`): optional cap on validator timeout results.
- `max_evaluator_sample_budget_exhaustions` (`null`): optional cap on
  per-sample wall-clock budget exhaustion results.
- `max_evaluator_stage_budget_exhaustions` (`null`): optional cap on
  per-stage wall-clock budget exhaustion results.
- `max_runtime_seconds` (`null`): optional wall-clock cap checked between
  seed/candidate evaluations. It is not a hard preemptive timeout.
- `max_llm_calls` (`null`): optional cap on logical LLM `generate()` calls.
  A value of `0` evaluates seeds and stops before provider construction or
  mutation. Positive caps are cooperative: mutation calls stop before a new
  candidate, while optional critique/feedback/meta-prompt calls skip or fail
  through their existing role-specific metadata once the cap is exhausted.
- `max_llm_provider_attempts` (`null`): optional cap on run-wide provider
  adapter attempts recorded from LLM call telemetry. The cap is checked before
  each logical LLM call and after the previous call has returned, so one
  in-flight adapter retry span can consume or slightly overshoot the configured
  cap before the next LLM call is stopped.
- `max_llm_tokens` (`null`): optional cap on run-wide provider-reported
  `usage.total_tokens` recorded from LLM call telemetry. The cap is cooperative
  and after-call: a call that reports usage can consume or slightly overshoot
  the cap before the next LLM call is stopped.
- `max_llm_cost_microusd` (`null`): optional cap on run-wide configured
  estimated LLM cost in micro-USD. It is computed only when backend metadata
  supplies `cost_usd_per_million_tokens` and provider usage supplies
  `total_tokens`; missing rates or usage add zero cost.
- `llm_role_provider_attempt_limits` (`{}`), `llm_role_token_limits` (`{}`),
  `llm_role_cost_microusd_limits` (`{}`): optional per-role caps for provider
  adapter attempts, provider-reported total tokens, and configured estimated
  micro-USD cost. Role-specific caps override the matching run-wide cap for
  their role in budget-report rows and are checked before calls for that role.
- `proposals_per_generation` (`1`): number of sequential mutation proposals to
  generate, evaluate, reward, and log inside each generation. Generation start
  hooks, generation completion accounting, and migration remain once per
  generation; each generated history row records its batch position under
  `metadata.proposal_batch`.
- `num_inspirations` (`3`): archive members rendered into prompts.
- `eval_timeout_sec` (`60.0`): default validator subprocess timeout.
- `validator_env_allowlist` (`[]`): parent environment variable names to pass
  into validator subprocesses in addition to the minimal default environment.
  Names are stripped, uppercased, deduplicated, and must match the portable
  manifest-safe grammar `[A-Z_][A-Z0-9_]{0,127}`. Values are not written to
  metadata; persisted validator stdout/stderr applies the shared versioned
  secret-pattern grammar.
- `validator_network_policy` (`host`): validator subprocess network policy.
  `host` leaves Python network APIs on the inherited host network and records
  `network_egress: "host_inherited_not_sandboxed"`. `deny` installs a
  Python-level socket denial hook during validator preflight and evaluation and
  records `network_egress: "python_socket_denied_not_os_sandbox"` plus
  `network_denial: "python_socket_monkeypatch"`. This is a reproducibility and
  accidental-egress guard, not a kernel, VM, container, subprocess, or native
  extension network sandbox. Startup manifests persist the effective setting in
  `config.validator_network_policy` and summarize the boundary under
  `policies.validator_network`.
- `evaluator_artifact_include` (`[]`): glob patterns for validator-created
  files to copy from the temporary candidate workspace into
  `evaluator_artifacts/`. Empty means no artifact copy-out. Artifact patterns
  are validated as non-empty glob strings, not environment variable names, and
  reject Unicode format controls such as right-to-left override and zero-width
  joiner, plus secret-like text before those selectors can be persisted in
  run manifests. Artifact globs are workspace-relative POSIX patterns:
  traversal components, dot/empty path components, absolute or drive-style
  roots, leading backslashes, and Windows backslashes are rejected. Matching is
  path-segment aware over candidate-relative POSIX paths: `*.txt` matches only
  root files, `reports/*.json` matches one segment under `reports/`, and
  `**/*.txt` recursively matches root and nested files.
- `evaluator_data_include` (`[]`): glob patterns for declared evaluator data
  files under each validator directory. Empty means no declared data set.
  Declared data is not copied into the candidate workspace; validators should
  read it relative to their validator module or package. Matching files are
  hashed into `manifest.json` under `declared_data_sources` and exposed to
  three-argument validators as `stage["evaluator_data"]["files"]`.
- `evaluator_data_exclude` (`[]`): glob patterns, relative to the validator
  directory, to omit from the declared evaluator data set.
- `evaluator_artifact_exclude` (`[]`): glob patterns to exclude from artifact
  copy-out after include matching. The same display-safe pattern validation
  and path-segment matching semantics apply.
- `evaluator_artifact_max_files` (`20`): maximum copied files per evaluation.
- `evaluator_artifact_max_bytes` (`1000000`): maximum total copied artifact
  bytes per evaluation. Matched regular file source sizes are checked against
  the remaining byte budget before file bytes are read; files that would exceed
  the budget are skipped with `reason: max_bytes`.
- `evaluator_artifact_redact_secrets` (`true`): apply the shared versioned
  secret-pattern grammar to UTF-8 text artifacts before writing them under
  `evaluator_artifacts/`. Binary or non-UTF-8 artifacts are copied raw.
- `evaluator_output_max_chars` (`20000`): maximum persisted characters per
  validator stdout/stderr stream. Output is redacted first, then truncated, and
  truncation metadata is recorded under
  `evaluation.metadata.diagnostic_output`.
  Direct `CascadeEvaluator` construction enforces the same finite positive
  timeout, artifact pattern, artifact limit, and artifact redaction-flag
  checks for top-level evaluator options, so notebooks/tests cannot bypass
  these config-loaded validation rules.
- `evaluator_stdin_text` / `evaluator_stdin_file` (`null`): optional
  fixture-only validator stdin source. Literal text must be bounded UTF-8
  text; file paths are resolved problem-locally during evaluation. Raw literal
  text and raw configured file paths are not persisted in startup manifests;
  `manifest.json.config.evaluator_stdin` keeps only policy, size, hash,
  redaction, and retained-text/path flags, and `policies.validator_stdin`
  declares generated and interactive stdin streams unsupported.
- `explore_ratio` (`0.3`): probability of exploration instead of exploitation
  when `parent_selection_strategy` is `mixed`. Explicit parent strategies
  bypass this ratio.
- `parent_selection_strategy` (`"mixed"`): parent sampling policy. Allowed
  values are `mixed`, `exploit`, `explore`, `metric`, `frontier`, `lineage`,
  `novelty`, and `recency`.
- `inspiration_strategy` (`"mixed"`): inspiration sampling policy for
  additional archive examples rendered into prompts. Allowed values are
  `mixed`, `random`, `selection`, `metric`, `frontier`, `lineage`, `novelty`,
  and `recency`.
  Metric strategies order leaders by the declared primary metric first, then
  remaining `metrics.yaml` order, then extra normalized metrics alphabetically.
  Frontier strategies use complete declared normalized metric vectors to
  surface non-dominated retained programs. Lineage strategies choose the best
  retained representative for each root lineage before cycling or filling.
  The `mixed` inspiration policy is a deterministic priority cascade:
  metric leaders, novelty-ranked candidates, selection-score leaders, then
  random fill for any remaining slots.
  Recency strategies use the in-memory archive update sequence before
  generation and score tie-breaks.
- `mutation_mode` (`"diff"`): `diff` or `full`. The built-in prompt template
  renders mode-specific mutation instructions; custom prompt variants can use
  `{mutation_mode}` and `{mutation_instructions}` or ignore them for backward
  compatibility.
- `eval_stages` (`[]`): optional configured evaluator stages with stage
  validator entrypoints, thresholds, samples, validator-managed seed values,
  metric-specific aggregation and min/max thresholds, retries, and timeouts.
  Each configured stage must have an explicit manifest-safe `name`.
- `prompt_variants` (`[]`): optional prompt templates for stochastic sampling.
- `prompt_variant_semantic_policy` (`"alphaevolve"`): validation policy for
  configured prompt seeds. The default requires `{task}`, `{parent_code}`,
  `{mutation_instructions}`, at least one evaluator-feedback channel
  (`{parent_feedback}`, `{parent_metrics}`, or `{parent_score}`), and at least
  one context/inspiration channel (`{context}`, `{inspirations}`,
  `{extra_context}`, or `{recent_failures}`). Set this to `"compatibility"` to
  allow minimal or externally managed templates such as `Task: {task}`.
- `prompt_format_options` (`{}`): optional weighted alternatives for
  AlphaEvolve-style stochastic formatting markers inside prompt templates. Use
  markers such as `[[prompt:tone]]` in `prompt_variants`; configure
  `prompt_format_options.tone` as a non-empty list of strings or
  `{text, weight}` mappings. Weights must be positive finite numbers. Selection
  uses LibreEvolve's run-local RNG, reuses one selected alternative for repeated
  occurrences of the same marker in a rendered prompt, and records selection
  hashes/indexes in `metadata.prompt_diagnostics.stochastic_formatting`.
- `prompt_max_chars` (`None`): optional global rendered mutation-prompt
  character cap. When set, LibreEvolve first deterministically omits oversized
  optional string prompt sections by priority, then applies a final
  middle-truncation guardrail before the LLM call, preferring to preserve the
  `[TASK]` mutation-instruction section. Prompt-size diagnostics are recorded in
  program history and the run manifest. Diagnostics include a `section_budget`
  report with per-placeholder priorities, hashes, character counts, estimated
  tokens, required/optional totals, template overhead, required-section fit
  status, and section-packing decisions. The same cap is also enforced at the
  `LLMEnsemble.generate()` boundary before scheduler selection, covering
  critique, feedback, meta-prompt, registry-created, and custom backends that
  run through the ensemble. This is a character budget with heuristic token
  estimates, not provider-token context-window fitting.
- `prompt_max_estimated_tokens` (`None`): optional global heuristic
  estimated-token cap for rendered mutation prompts and ensemble prompts.
  LibreEvolve estimates tokens as `ceil(rendered_chars / 4)`, converts this cap
  into an effective character budget for deterministic section-priority
  packing, records the configured token source in `section_budget`, and rejects
  over-budget ensemble prompts before scheduler/backend selection. The final
  ensemble boundary upgrades this cap to exact provider-token counting when all
  role-eligible backends share a locally available tokenizer counter; otherwise
  it records the unavailable reason and uses the character-derived heuristic.
  Individual backend specs can also set `prompt_max_estimated_tokens`; the
  ensemble combines the global cap with eligible backend/model caps and records
  the effective cap in call telemetry. Backend specs can also set
  `context_window_tokens` with optional `reserved_output_tokens` to derive a
  heuristic prompt-token capacity of `context_window_tokens -
  reserved_output_tokens`; when `reserved_output_tokens` is omitted and
  `max_tokens` is set, the backend output cap is used as the reserve. This is
  still final-prompt fitting, not full provider-tokenizer section packing for
  every rendered prompt component.
- `prompt_artifact_content_mode` (`"excerpt"`): controls validator-artifact
  content rendered into mutation prompts. `excerpt` uses the bounded
  `content_excerpt` already stored in evaluation metadata, `bounded_file`
  reopens copied UTF-8 artifacts under the run directory with the byte/char
  caps below, and `off` disables artifact-content rendering while keeping path
  and hash summaries.
- `prompt_artifact_content_max_bytes` (`4096`): maximum copied artifact bytes
  read from disk when `prompt_artifact_content_mode: bounded_file`.
- `prompt_artifact_content_max_chars` (`1000`): maximum redacted artifact
  characters rendered into prompts when `prompt_artifact_content_mode:
  bounded_file`.
- `mutation_prompt_retention_mode` (`"redacted"`): controls how generated
  candidate history persists rendered mutation prompts. Accepted values are
  `full`, `redacted`, `hash_only`, and `off`. Provider calls still receive the
  rendered prompt; this controls only `history.jsonl` `metadata.prompt` and
  `metadata.prompt_retention`.
- `explicit_context_retention_mode` (`"redacted"`): controls how explicit
  problem-context spans are retained inside persisted rendered mutation
  prompts. Accepted values are `full`, `redacted`, `hash_only`, and `off`.
  Provider mutation calls still receive the rendered explicit context; this
  setting controls only the persisted prompt text and
  `metadata.prompt_retention.explicit_context_retention`.
- `meta_prompt_evidence_retention_mode` (`"hash_only"`): controls how
  `prompt_history.jsonl` persists meta-prompt mutation evidence under
  `metadata.mutation_context`. Accepted values are `full`, `redacted`,
  `hash_only`, and `off`. Meta-prompt provider calls still receive the
  bounded, secret-redacted evidence block; this setting controls only
  persisted evidence text and sidecar hash/count metadata.
- `quarantine_snapshot_retention_mode` (`"redacted"`): controls how
  framework-owned `*_invalid.jsonl` quarantine rows retain rejected
  `record_repr` snapshots and torn JSONL fragment previews. Accepted values
  are `full`, `redacted`, `hash_only`, and `off`. Quarantine messages still
  use bounded secret-redacted diagnostics; this setting controls only the
  rejected-record or torn-fragment snapshot sidecar.
- `critique_retention_mode` (`"redacted"`): controls how candidate history
  persists critique prompt text plus original/revised mutation text under
  `metadata.critique`. Accepted values are `full`, `redacted`, `hash_only`,
  and `off`. Critique provider calls still receive the prompt and mutation
  text; this controls only persisted history metadata and manifest retention
  policy.
- `meta_prompt_evolution` (`False`): when true, periodically ask the active LLM
  backend to produce a revised prompt template. Must be boolean.
- `meta_prompt_interval` (`25`): generations between optional meta-prompt
  mutations.
- `prompt_reward_mode` (`"absolute"`): prompt-program reward input. `absolute`
  uses the final composed candidate score; `improvement` uses final composed
  child score minus parent score.
- `prompt_reward_bounds` (`[0.0, 1.0]`): `[lo, hi]` bounds used to normalize
  prompt-program rewards to `0..1` before prompt selection.
- `prompt_explore_coeff` (`1.0`): exploration coefficient for the prompt
  database's UCB-like selector.
  Direct `PromptDatabase` construction enforces the same reward-mode, strictly
  increasing reward-bound, and finite non-negative exploration-coefficient
  checks as `Config`.
- `critique_enabled` (`False`): when true, run an LLM critique/revision pass
  on the proposed mutation before applying it. The revised mutation is
  previewed with the active mutation parser; if the revision is malformed but
  the original mutation still applies cleanly, LibreEvolve falls back to the
  original and records the fallback in candidate metadata. Must be boolean.
- `critique_prompt` (`""`): optional custom instruction string for the
  critique pass.
- `critique_reviewers` (`[]`): optional synchronous reviewer-pool specs. Each
  reviewer is a mapping with manifest-safe `name`, optional `prompt`, and
  optional LLM `role`. If `role` is omitted it defaults to `critique:<name>`,
  which can be routed through `llm_role_backend_indices` and accounted through
  role-specific LLM budget telemetry. If omitted entirely, the legacy single
  reviewer uses `critique_prompt` and role `critique`.
- `critique_aggregation_policy` (`"first_valid"`): selects which valid
  reviewer revision is evaluated. `first_valid` keeps the first valid
  revision; `last_valid` keeps the last valid revision. Invalid revisions and
  provider failures are logged but do not replace a valid original mutation.
- `llm_feedback` (`[]`): optional LLM grader specs that score or discard
  evaluated candidates after local validation.
- `feedback_retention_mode` (`"redacted"`): controls how candidate evaluation
  metadata persists feedback grader `raw_response` and parsed `feedback` text.
  Accepted values are `full`, `redacted`, `hash_only`, and `off`. Feedback
  provider calls still return and parse the full response; this controls only
  persisted evaluation metadata and manifest retention policy.
- `plugin_context_retention_mode` (`"redacted"`): controls how candidate
  history persists text returned by plugin `build_extra_context()` under
  `metadata.plugin_context[*].context`. Accepted values are `full`,
  `redacted`, `hash_only`, and `off`. Prompt construction still receives the
  bounded/redacted plugin context; persisted rendered mutation prompts that
  include that context are controlled separately by
  `mutation_prompt_retention_mode`.
- `provider_response_retention_mode` (`"hash_only"`): controls how successful
  LLM call records persist provider/backend output text in `llm_calls.jsonl`
  and `LLMEnsemble.call_history`. Accepted values are `full`, `redacted`,
  `hash_only`, and `off`. The call record still keeps top-level output
  hash/count telemetry for replay; this setting controls retained output text
  and the `output_retention` sidecar.
- `provider_error_retention_mode` (`"redacted"`): controls how failed LLM call
  records persist provider/backend exception text in `llm_calls.jsonl` and
  `LLMEnsemble.call_history`. Accepted values are `full`, `redacted`,
  `hash_only`, and `off`. Provider status/category metadata remains available;
  this setting controls only retained error-message text and its sidecar hash
  metadata.
- `capture_proposal_metadata` (`False`): when true, mutation prompts ask for
  short `IDEA`, `RATIONALE`, and `HYPOTHESIS` sections before the patch. Those
  sections are parsed into candidate metadata while patch extraction remains
  compatible with diff-only responses. Selected parent and inspiration
  candidates render bounded proposal summaries back into later prompts.

Example LLM feedback grader config:

```yaml
critique_enabled: true
critique_reviewers:
  - name: correctness
    prompt: "Check correctness and preserve the required mutation format."
    role: critique:correctness
  - name: simplicity
    prompt: "Prefer the simplest valid revision."
    role: critique:simplicity
critique_aggregation_policy: first_valid
llm_feedback:
  - name: simplicity
    metric: llm_simplicity
    weight: 0.05
    min_score: 0.2
    failure_policy: penalize
    failure_retries: 1
    failure_penalty: 0.05
    prompt: "Grade simplicity from 0 to 1. Return JSON with score, feedback, discard."
```

Feedback scores are logged as metrics, provenance is stored in evaluation
metadata, and weighted scores adjust candidate fitness without replacing the
raw primary validator metric. Graders run only for locally valid candidates by
default; set `include_invalid: true` on a grader to review invalid candidates.
Feedback outcomes live in `evaluation.metadata.llm_feedback`, and each applied,
skipped, failed, or invalid feedback grader appends an `llm_feedback:<name>`
entry to `evaluation.stages`.
For workspace candidates, the built-in feedback prompt includes bounded
explicit problem context with source provenance, a bounded deterministically
ordered file listing with path headers, primary-file marking, secret redaction
through the shared versioned grammar, truncation notices, and compact
evaluation diagnostics.
Feedback prompt redaction covers explicit context text, workspace file
contents, evaluator diagnostics, and metric payloads; context,
diagnostic stdout/stderr/errors, and metric keys/values are redacted before
prompt truncation. Feedback provider outputs are retained according to
`feedback_retention_mode`: `evaluation.metadata.llm_feedback` keeps
compatibility `raw_response` and parsed `feedback` fields in `full`/`redacted`
modes, suppresses text in `hash_only`/`off`, and always records
`raw_response_retention` and `feedback_retention` metadata with the selected
mode, policy, hashes when enabled, original/stored character counts, caps, and
redaction/truncation flags.
Prompt-visible evaluator stage summaries use tri-state status labels:
`passed`, `failed`, or `unknown` for missing/restored/malformed state.
`llm_feedback` grader specs are validated before startup: `name` and `metric`
must be manifest-safe labels matching
`[A-Za-z0-9][A-Za-z0-9_.-]{0,127}` and must not look like secrets; `prompt`
must be a string when present; `objective_metric`, when present, must be
boolean; `weight` and `min_score` must be finite numbers; optional `bounds`
must be a strictly increasing `[lo, hi]` pair; optional `direction` must be
`maximize` or `minimize`; `include_invalid` must be boolean; `failure_policy`
must be `ignore`, `penalize`, or `discard`;
`failure_retries` must be an integer from `0` through `3`; `failure_penalty`
must be in `[0, 1]`; and unsupported keys are rejected.
Direct feedback API calls apply the same label and policy validation before
making a reviewer LLM call.
Provider failures, malformed response scores, non-finite response scores, and
non-boolean discard values are recorded as `llm_feedback_failed` metadata. The
default failed-grader policy is `ignore`, which leaves score and validity
unchanged. `penalize` subtracts `failure_penalty` from candidate fitness after
configured retries are exhausted, and `discard` marks the candidate invalid.
Non-JSON feedback text is scored only when it contains an explicit
`score: <number>` or `score=<number>` field; incidental prose numbers,
percentages, multi-number diagnostics, and values outside configured bounds
are not accepted as scores. Raw feedback scores are stored as the configured
feedback metric. A normalized score, derived from `bounds` and `direction`, is
used for `weighted_delta` and normalized `min_score` checks.
Feedback graders run in configured order. Once a candidate becomes invalid,
whether from the evaluator or an earlier feedback discard, later graders are
skipped unless they set `include_invalid: true`.
Feedback metric names must use the same manifest-safe metric-name grammar as
`metrics.yaml` and runtime `Program.metrics`, including optional dotted
namespaces. Feedback metrics cannot use reserved fields such as
`feedback_adjusted_fitness`, cannot collide with evaluator metrics, and cannot
duplicate another feedback metric in the same configured grader list.
When a grader sets `objective_metric: true`, its `metric` must reference a
non-primary problem metric declared with `source: feedback`. The grader then
inherits that metric's `bounds` and `direction`, fills the metric after the
evaluator succeeds, and the filled value participates in declared-metric
normalization and `selection_score`. Evaluator-returned metrics cannot use
`source: feedback` names.
Prompt-bearing config values are retained in manifests with redaction,
truncation, and hash metadata. Configured `prompt_variants`,
`prompt_format_options` alternative text, `critique_prompt`, and each
`llm_feedback[].prompt` are stored under `manifest.json.config` after
secret-like text redaction and bounded truncation. Parallel metadata fields
record SHA-256 of the original text, original length, retained length,
redaction, and truncation flags so runs remain attributable without preserving
known credential-shaped strings verbatim.

### Population

- `n_islands` (`5`): number of MAP-Elites islands.
- `migration_interval` (`25`): migrate every N generations. `0` disables
  migration.
- `migration_ratio` (`0.10`): fraction of each island's elite archive copied to
  the next island. `0.0` selects no migrants; positive ratios are rounded up to
  at least one migrant when an island has elites.
- `map_elites_bins` (`10`): bins per MAP-Elites dimension.
- `map_elites_descriptor_axes`
  (`["performance", "complexity", "diversity"]`): exactly three behavior
  descriptor axes for MAP-Elites cells. Built-in axes are `performance`,
  `complexity`, and `diversity`; configured axes can also read normalized
  evaluator metrics as `metric:<name>`, numeric evaluator metadata as
  `evaluation_metadata:<path>`, or numeric candidate metadata as
  `candidate_metadata:<path>`. Missing, non-finite, or out-of-range values are
  safely mapped into the unit descriptor interval before binning.
- `map_elites_complexity_max_chars` (`100000`): fixed upper bound used to
  normalize the serialized-workspace complexity descriptor. Larger descriptor
  texts clamp to the maximum complexity bin instead of changing the archive
  scale during the run.
- `elite_archive_size` (`50`): cap on the per-island elite list.

### LLM routing

- `backends`: backend specs. Default:

```python
[{"type": "anthropic", "model": "claude-sonnet-4-6"}]
```

This is the code default at the time this documentation was written, not a
live provider availability guarantee.

Backend specs may include `cost_usd_per_million_tokens`, a positive local
pricing estimate used only after provider usage metadata supplies
`total_tokens`. Runtime call telemetry records the resulting cost estimate, and
role accounting/budget reports aggregate it as `cost_microusd` / `cost_usd`.
`max_llm_cost_microusd` can enforce a live run-wide stop from this configured
estimate, but LibreEvolve still does not fetch live provider prices.
Backend specs may also include `prompt_max_estimated_tokens`, a positive
prompt-token cap for that backend/model. It is enforced before provider calls
when the backend is eligible for the call role, using exact provider-token
counts when role-scoped tokenizer discovery succeeds and heuristic counts
otherwise, and is recorded in call telemetry alongside the global configured
cap. Backend specs may also
include `context_window_tokens` and optional `reserved_output_tokens`; the
ensemble subtracts the reserve from the window and applies the result as another
eligible-backend heuristic prompt-token cap. If `reserved_output_tokens` is
omitted and `max_tokens` is present, `max_tokens` is used as the output reserve.
`reserved_output_tokens` requires `context_window_tokens` and must be smaller
than it.

- `ensemble_explore_coeff` (`1.0`): exploration coefficient for UCB-style
  routing.
- `ensemble_strategy` (`"ucb1"`): `ucb1` or experimental
  `throughput_depth`.
- `llm_max_retries` (`0`): retry attempts on the same selected backend before
  trying fallback or failing the call. This is an ensemble-layer retry count
  after a backend raises; the built-in OpenAI, Anthropic, and Ollama adapters
  have a separate `provider_max_retries` cap for internal provider attempts.
  Must be between `0` and `10`.
- `llm_max_call_attempts` (`32`): maximum total original, retry, and fallback
  attempts for one logical ensemble call. This bounds retry multiplication
  across fallback backends. Must be between `1` and `32`.
- `llm_fallback` (`true`): when enabled, a failed backend is excluded for the
  current call after its retries are exhausted and the ensemble attempts another
  backend when one is available.
- `llm_max_response_chars` (`100000`): maximum accepted text characters in a
  backend response at the ensemble boundary. Larger responses are classified as
  failed attempts before success accounting, output hashing, mutation parsing,
  prompt-history retention, or candidate metadata capture, so configured
  retry/fallback behavior can handle them.
- `llm_call_history_max` (`500`): maximum retained in-memory ensemble
  call-history records. The ensemble keeps total/dropped counters in
  `call_history_retention`; config-created runs also write durable
  append-only `llm_calls.jsonl` telemetry.
- `llm_call_timeout_sec` (`null`): optional positive ensemble-level deadline
  for each backend `generate()` attempt, including custom backends. Timed-out
  attempts are recorded as timeout failures and can retry or fall back like
  other provider failures.
- `llm_role_call_limits` (`{}`): optional mapping from manifest-safe LLM role
  labels to non-negative logical `generate()` call limits. Limits are enforced
  before backend selection for the matching role and are persisted in scheduler
  snapshots as restorable logical role-call consumption. This is a role-specific
  logical-call cap, not a token, cost, provider-attempt, or wall-clock budget.
  Budget maps also accept manifest-safe prefix scopes ending in `:*`, such as
  `feedback:*`; concrete call history remains exact-role while matching roles
  share the scoped limit.
- `llm_role_backend_indices` (`{}`): optional mapping from manifest-safe LLM
  role labels to non-empty backend-index lists. When a call role is configured,
  the ensemble selects only from those backend indices for that role. Roles
  without an explicit route can still use backend `role` metadata when present,
  then fall back to the global backend bandit when no role lane matches.
- `llm_role_failure_quarantine_after` (`{}`): optional mapping from
  manifest-safe LLM role labels to positive consecutive exhausted-failure
  thresholds. When a backend reaches the configured threshold for a role, later
  logical calls for that role exclude that backend until the scheduler state is
  reset or restored from a snapshot without that quarantine. Failed
  reward-accounted calls under this policy record a zero-reward scheduler
  penalty. Scheduler snapshots persist `provider_failure_policy_state` with the
  configured thresholds and per-role/backend failure counters.
- `llm_reward_accounted_roles` (`["mutation"]`): role labels that advance
  ensemble scheduler counts and can receive rewards. Roles not listed here are
  still routed through the ensemble and persisted in call telemetry, but their
  calls are marked `scheduler_accounting: telemetry_only` and do not affect the
  bandit counters. Exact feedback grader roles such as `feedback:simplicity`
  can be listed here; successful feedback calls then reward the scheduler with
  the grader's normalized score. Labels use the same manifest-safe role grammar
  and secret-like value rejection as call roles.
- `llm_prompt_roles` (`{}`): optional mapping from LLM call role to structured
  prompt-message instructions. Each role entry may define `system` and/or
  `developer` text, capped at 4000 characters per field. Omitted roles keep
  the default single-user-message behavior. Configured role labels use the
  same manifest-safe grammar as call roles and must not look like secrets.
  Prompt-bearing instruction text is redacted/truncated with SHA-256 metadata
  in `manifest.json`; call telemetry stores only hashes, character counts,
  redaction flags, message roles, and the matched role.

Example:

```yaml
llm_prompt_roles:
  mutation:
    system: "You propose runnable SEARCH/REPLACE mutations."
    developer: "Return only the requested mutation payload."
  critique:
    system: "Review the proposed mutation for evaluator-facing defects."
```

Backend specs may include optional scheduling metadata:

```yaml
backends:
  - type: openai
    model: "<openai-model-id>"
    role: breadth
    cost: 1.0
    latency: 1.0
    depth: 1.0
  - type: openai
    model: "<openai-reasoning-model-id>"
    reasoning_effort: high
    role: depth
    cost: 4.0
    latency: 4.0
    depth: 5.0
ensemble_strategy: throughput_depth
```

Backend specs are validated before a run starts. Supported backend types are
`anthropic`, `openai`, `ollama`, and `custom`; `model` is required and must
match the manifest-safe grammar `[A-Za-z0-9][A-Za-z0-9_.:/+-]{0,191}` without
matching the shared secret-redaction patterns; optional `max_tokens`, `cost`,
`latency`, and `depth` are validated; optional `role` must match the
manifest-safe call role grammar `[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}`, must not
end with `:`, and must not look like a secret; OpenAI `api_mode` is accepted
only as `auto`, `chat_completions`, or `responses`; and `reasoning_effort` is
accepted only for OpenAI backends with one of `none`, `minimal`, `low`,
`medium`, `high`, or `xhigh` after a conservative local model-compatibility
check.
Custom backends require `class_path` in `module.path:ClassName` form. The
class is instantiated with the top-level `model`, optional `max_tokens`, and
optional JSON-safe `kwargs`; `kwargs` keys must be manifest-safe keyword labels
and cannot shadow `model` or `max_tokens`.
Constructor-supported keys are passed to backend classes; scheduling metadata
stays in the ensemble.
Restored/replay backend spec lists can be preflighted with
`validate_restored_backend_specs()`. It delegates to the same backend
normalization boundary as `build_llm()`, including model-id, token-limit,
request-parameter, client-context, custom-backend, and unsupported-field
checks, and returns a defensive normalized copy. Full run resume does not yet
consume restored backend specs.
Restored/replay prompt payloads can be preflighted with
`validate_restored_llm_prompt()`, which delegates to the same non-empty text
boundary used by live ensemble and bundled direct-adapter calls. Oversized and
secret-like prompt policy remains separate future work.
Direct `LLMEnsemble` construction applies the same strategy, exploration,
retry/fallback, role-label, backend-count, and JSON-safe metadata checks, so
lower-level callers cannot persist malformed scheduler telemetry by bypassing
`Config`. Direct scheduler metadata/state reads return defensive copies, and
`restore_scheduler_state()` validates restored counts, rewards, totals,
rewarded call ids, unrewarded per-backend call ids, and duplicate or
overlapping reward ledger entries before replacing live bandit state. If a
restored scheduler snapshot includes call-history retention diagnostics, their
shape and counter consistency are validated even though the live retained
window itself is not restored.
Validated call roles are also passed through to backend implementations as
`generate(prompt, role=role)` on original, retry, and fallback attempts. When
`llm_prompt_roles` has an entry for that role, OpenAI Chat Completions and
Responses receive configured `system`/`developer` messages before the rendered
user prompt; Anthropic receives a provider-supported `system` string composed
from configured system/developer text; and Ollama receives a system message
followed by the user prompt. Omitted roles keep the default single user
message/input item. Built-in backend specs accept validated request
parameters: `temperature` and `top_p` for OpenAI, Anthropic, and Ollama;
`stop` for Anthropic, Ollama, and OpenAI Chat Completions mode; and `seed` for
Ollama and OpenAI Chat Completions mode. `temperature` is bounded to
`0..2` for OpenAI/Ollama and `0..1` for Anthropic; `top_p` must be `> 0` and
`<= 1`; stop sequences must be non-empty secret-safe strings; and seeds must be
non-negative 32-bit integers. Custom backends should carry provider-specific
settings through their JSON-safe `kwargs` rather than these built-in top-level
fields.
Built-in OpenAI, Anthropic, and Ollama backend specs also accept positive
`timeout_sec`, which is forwarded to provider client construction as a request
timeout. Custom backends should carry provider-specific timeout settings
through JSON-safe `kwargs`. The separate run-level `llm_call_timeout_sec`
wraps each ensemble backend attempt with a local deadline and records
`ProviderCallTimeoutError` timeout telemetry when exceeded. This is not a
provider cancellation token, but deadline-aware `LLMEnsemble` calls are
clamped to the remaining `max_runtime_seconds` budget before each attempt
starts.
Those built-in specs also accept `provider_max_retries`, a non-negative
adapter-internal retry cap. The default is `2`, meaning one original provider
call plus up to two internal retries. Each recorded LLM call includes an
`adapter_retry` summary with the configured cap, provider attempts, failed
attempt count, and safe exception type labels. Completed and aborted runtime
manifests also include `runtime.llm_accounting`, which summarizes validated
role-accounting counters and current LLM-related limits for audits. It is not
a token, cost, or provider-attempt budget stop policy.

The `reasoning_effort` validator encodes the current documented OpenAI effort
values and selected model-family restrictions: `gpt-5.1` accepts `none`, `low`,
`medium`, and `high`; `gpt-5-pro` accepts only `high`; known pre-`gpt-5.1`
families reject `none`; and `xhigh` is allowed only for locally recognized
eligible families such as later GPT-5 minors. Unknown future model ids still
receive the global effort enum check and may fail provider-side capability
checks. Check provider docs and your account model list before running
expensive jobs.

In the current scheduler, `throughput_depth` uses numeric `cost`, `latency`,
and `depth` after a pull-once initialization pass over non-excluded backends.
Selectable backend metadata is min/max normalized per field for each selection;
equal-valued fields use neutral `0.5`. Fixed weights are `depth: 0.10`,
`cost: -0.05`, and `latency: -0.05`, and each call record persists that
effective scheduler policy. The `role` field is descriptive metadata only; it
is not yet used for quotas, escalation, or role-specific routing. Config
validation makes role labels safe to persist, but accepted custom labels should
not be treated as operational scheduler policy.

### Plugins and logging

- `plugins` (`[]`): list of built-in plugin names or spec mappings. String
  entries must match the manifest-safe grammar
  `[A-Za-z0-9][A-Za-z0-9_.-]{0,127}` and must not look like secret assignments
  or provider tokens. Mapping entries use `name` plus optional `options`, for
  example `{name: deep_research, options: {search_every: 2}}`. Option keys must
  be manifest-safe identifiers and option values must be finite JSON-safe
  scalars/lists/mappings without secret-like text. The built-in registry
  validates supported options before plugin construction; unknown plugin names,
  unknown options, invalid cadence values, and unsafe labels fail before CLI
  overwrite cleanup. The special `{name: entry_point, options: {group:
  libreevolve.plugins, name: my_plugin, paper_inspiration:
  AlphaEvolveExtension, constructor_options: {...}}}` form resolves a Python
  entry point in the `libreevolve.plugins` group; the target must load a
  `PluginBase` subclass, optional `constructor_options` are manifest-safe JSON
  keyword arguments, and external plugin classes may publish
  `libreevolve_constructor_option_schema` to enforce declared option names and
  types before instantiation. Supported declared schema types are
  `bool`/`boolean`, `enum`, `int`/`integer`, `manifest_safe_json`,
  `nonnegative_int`, `number`, `path`, `plugin_label`, `positive_int`, and
  `string`; `required: true` marks a required option. Optional
  `paper_inspiration` labels describe the paper-facing plugin scope. When
  explicit plugin objects are not passed, core `evolve()` resolves
  `Config.plugins` into built-in or entry-point plugin instances.
- `log_dir` (`"runs/"`): root output directory. Must be a non-empty path
  string or path-like value whose components are path-safe and display-safe:
  no control characters, Unicode format controls, non-NFC spellings, invalid
  filename characters, traversal components, leading/trailing whitespace,
  trailing dots, or Windows-reserved device names. The configured value is used
  for filesystem writes, but manifest retention is share-safe: safe relative
  values such as `runs/` are recorded as configured, while absolute log roots
  are represented in `manifest.json` as `<absolute-log-dir>` plus
  `log_dir_metadata` with a SHA-256 digest and retention reason.
- `problem_name` (`"unnamed"`): final run subdirectory name for direct
  `Config`/API use. Must be a non-empty safe run-name component, not a path.
  Before cleanup or writes, the final run directory is resolved and must remain
  under the resolved `log_dir`; symlink/junction run directories that point
  outside the log root are rejected. Run names also reject Windows-reserved
  device names, leading/trailing whitespace, trailing dots, invalid filename
  characters, control characters, path separators, non-NFC Unicode spellings,
  and Unicode format controls such as right-to-left override and zero-width
  joiner. Secret-like assignment strings and provider-token-shaped values are
  rejected before filesystem or manifest writes. The CLI does not accept
  `problem_name` from problem-local `config.yaml`; use `--run-name` for CLI run
  directory overrides.
- `run_id` (UUID4 hex by default): provenance identifier written to
  `manifest.json`. It is not a resume checkpoint id. Configured ids must match
  `[A-Za-z0-9][A-Za-z0-9_.-]{0,127}`; unsafe values with control characters,
  path separators, assignment syntax, leading punctuation, or secret-like
  token patterns are rejected before `evolve()` runs.
- Run provenance is generated automatically: when available, the manifest
  includes Git state, `libreevolve/` source-tree hashes, problem-tree hashes,
  direct evaluator entrypoint hashes, and plugin module file hashes.
- `run_collision_policy` (`"fail"`): what to do when the target run directory
  already contains known run artifacts. `fail` aborts before appending or
  rewriting artifacts; `overwrite` deletes known run artifacts only
  (`history*.jsonl`, `failure_history*.jsonl`, `archive_events*.jsonl`,
  `prompt_history*.jsonl`, their invalid-record quarantine streams,
  `manifest.json`, `best.py`, `best_workspace/`, `evaluator_artifacts/`, and
  `plugin_artifacts/`) before starting. This cleanup only runs after the resolved run-directory containment
  check succeeds and after the startup manifest payload has been serialized in
  memory. If the manifest payload is not strict finite JSON, startup rejects the
  run before deleting existing known artifacts. If any known artifact path is
  itself a symlink or Windows junction, startup rejects overwrite before
  deleting any artifact. Files with other names are preserved under both
  policies and are recorded in `manifest.json` only as immediate-entry counts,
  hashed names, and entry types; treat mixed directories as outside the
  clean-run reproducibility contract.
- `seed` (`42`): integer random seed for LibreEvolve's run-local
  `random.Random` instance. Framework-owned parent selection, inspiration
  sampling, prompt-template sampling, island sampling, and MAP-Elites random
  sampling use this local RNG without reseeding or advancing the host process's
  global `random` module. Prompt variants enter `PromptDatabase`, where
  configured seed prompt ids are deterministic from config order and template
  hash, initial untried selection follows config order, and database-created
  mutation ids are deterministic from parent/generation/child order and
  template hash. Duplicate configured or evolved prompt templates remain
  separate prompt arms with independent ids, rewards, usage counts, and lineage,
  while prompt-history records include `template_sha256` for content-identity
  audits. It does not make persisted candidate IDs deterministic yet.

Note: although `problem_name` is a `Config` field for direct API use, the CLI
rejects `problem_name` in problem-local `config.yaml` to avoid silently
ignoring an output-name setting. Use `--run-name` to choose a run directory
from the CLI; the effective `manifest.json.config.problem_name` records that
CLI-selected run name.

## Problem-local `config.yaml`

Example:

```yaml
max_generations: 200
max_evaluations: 1000
max_evaluator_seconds: 7200
max_evaluator_subprocess_attempts: 5000
max_evaluator_stage_samples: 2000
max_evaluator_retry_attempts: 500
max_evaluator_timeouts: 50
max_evaluator_sample_budget_exhaustions: 25
max_evaluator_stage_budget_exhaustions: 10
max_runtime_seconds: 14400
eval_timeout_sec: 15
mutation_mode: full
evaluator_artifact_include: ["*.json", "artifacts/**"]
evaluator_artifact_exclude: ["artifacts/tmp/**"]
evaluator_data_include: ["fixtures/*.json"]
evaluator_data_exclude: ["fixtures/tmp/**"]
eval_stages:
  - name: smoke
    validate_path: validate.py
    timeout_sec: 5
    max_sample_seconds: 3
    max_stage_seconds: 8
    min_score: 0.1
    samples: 2
    seeds: [1, 2]
    retries: 1
    data_include: ["smoke-fixtures/*.json"]
  - name: full
    timeout_sec: 30
    min_score: 0.5
    require_program_output: true
    min_artifacts: 1
    required_artifacts: ["reports/*.json"]
    program_output_checks:
      - path: certificate.status
        equals: ok
    metric_aggregation:
      score: min
      runtime: max
      stability:
        policy: quantile
        q: 0.1
      is_valid: all
    metric_thresholds:
      score:
        min: 0.5
      runtime:
        max: 2.0
    artifact_include: ["reports/*.json", "plots/*.png"]
    artifact_exclude: ["reports/tmp/**"]
    artifact_max_files: 5
    artifact_max_bytes: 2000000
    artifact_redact_secrets: true
backends:
  - type: openai
    model: "<openai-model-id>"
```

`eval_stages[].timeout_sec` is enforced per subprocess attempt: with
`samples: 2` and `retries: 1`, each sample can run up to two validator
subprocess attempts. Use `eval_stages[].max_sample_seconds` to add a per-sample
wall-clock budget across retries, and `eval_stages[].max_stage_seconds` to add
a stage-level wall-clock budget across samples and retries. When set, each
attempt is clipped to the smallest remaining attempt, sample, or stage budget;
later retries or samples stop after exhaustion; and the result records
`sample_budget_exhausted` or `stage_budget_exhausted` plus
`evaluation.metadata.sample_budget` / `evaluation.metadata.stage_budget`.
`eval_stages[].retries` is capped at `10`; configured stages therefore have an
explicit retry ceiling. When `min_score` or `metric_thresholds` is configured,
retries are threshold-aware: a locally valid attempt below a minimum threshold
or above a maximum threshold can be retried until a passing attempt is selected
or retry budget is exhausted. `metric_thresholds` maps declared metric names to
`min` and/or `max` finite numeric bounds. Problem metrics default to
`source: evaluator`, meaning validators must return them. Non-primary metrics
may use `source: feedback`, `source: plugin`, or `source: final_fitness`; those
names are omitted from evaluator-required metric checks. Feedback-sourced
metrics can be filled by `llm_feedback` graders with `objective_metric: true`;
plugin-sourced metrics can be filled by plugin hooks as validated metric side
effects; final-fitness metrics are synthesized from the candidate's final
composed fitness after plugin score hooks run.
`metric_aggregation` maps metric
names to `mean`, `min`, `max`, `last`, `all`, `any`, or a quantile mapping
such as `{policy: quantile, q: 0.9}`. Numeric metrics use `mean` by default,
boolean metrics use `all` by default, and non-numeric JSON-compatible values
use `last` by default. Quantile `q` values are finite numbers from `0` through
`1` and use deterministic linear interpolation over sorted sample values.
Metric names use the same manifest-safe metric-label validation as
validator-returned metrics.
Configured stage names must be explicit, unique, and manifest-safe:
`[A-Za-z0-9][A-Za-z0-9_.-]{0,127}`. They must not match shared secret-redaction
patterns, and the built-in `diff`, `syntax`, and `validate` labels are
reserved for evaluator-generated stages.
Multi-sample aggregation is explicit per metric when `metric_aggregation` is
configured. `require_program_output: true` requires validators to return a
retained `outputs` or `program_output` payload, and `min_artifacts` requires at
least that many copied evaluator artifacts after include/exclude/budget policy.
`required_artifacts` requires each listed artifact glob to match at least one
copied artifact path. `program_output_checks` compares retained output values
at dotted manifest-safe JSON paths against JSON-safe scalar `equals` values.
Arbitrary task-specific predicates remain the validator's responsibility
through `is_valid`, declared metrics, retained program outputs, and copied
artifacts; stage config is intentionally a manifest-safe policy layer rather
than an arbitrary code hook surface. Invalid samples and threshold failures can
make the top-level evaluation invalid while raw aggregate metric values and
local stage rows still reflect the underlying validator outputs. Retry-attempt
metadata stores local validity and threshold pass/fail separately.
Every configured stage's selected result is retained under
`evaluation.metadata.configured_stage_results[]`. Each entry records the stage
name/index, local validity, legacy score `threshold`, full `threshold_result`
with per-metric threshold checks and artifact/output checks, pass/stop
decision, metrics, elapsed time, stdout/stderr/error, flattened stage rows, and
that stage's own metadata including metric aggregation policy, attempts,
samples, artifact records, validator environment, and stage policy. Top-level
`evaluation.metadata.stage` and
`evaluation.metadata.artifacts` continue to describe only the final selected
stage, or the stage where the cascade stopped.

Problem-local `config.yaml` keys are checked against the `Config` dataclass and
unknown keys fail at CLI startup. `Config.validate()` also rejects invalid enum
values such as `mutation_mode: typo`, invalid ensemble strategies, malformed
backend specs, and invalid top-level numeric fields before the run mutates or
evaluates candidates.

Nested mapping keys in configured evaluator stages, backend specs, and LLM
feedback grader specs must also be strings. Mixed non-string and unknown string
keys fail with `config.yaml`-labeled `ConfigError` diagnostics before unsupported-field
sorting, both for direct `Config(...)` construction and problem-local
`config.yaml`.

Invalid UTF-8, malformed YAML, duplicate mapping keys, and scalar/list
top-level documents fail at CLI startup with `config.yaml`-labeled
`ConfigError` diagnostics before the run mutates or evaluates candidates.
Those CLI config diagnostics redact common secret-like patterns from parser and
key text instead of printing raw absolute problem roots.
The shared setup YAML parser formatter also redacts common secret-like key text
from duplicate-key diagnostics in `metrics.yaml` and context manifests.

Nested evaluator-stage fields are validated before a run: `name` is required,
must be manifest-safe, must be unique, and cannot be `diff`, `syntax`, or
`validate`; `validate_path`, when present, must be a non-empty string;
`samples` must be positive; `timeout_sec`, `max_sample_seconds`, and
`max_stage_seconds` must be positive; `retries` must be an integer from `0`
through `10`; `min_score` must be numeric; `min_artifacts` must be a
non-negative integer; `require_program_output` must be boolean;
`program_output_checks` must be a list of `{path, equals}` mappings with
manifest-safe dotted paths and JSON-safe scalar expected values;
`required_artifacts` plus artifact include/exclude fields must be lists of
non-empty display-safe path-segment-aware glob strings with no Unicode format controls;
artifact redaction flags must be boolean; and artifact max-file/max-byte
limits must be non-negative integers. Stage `seeds` must be JSON-safe scalar
values, and if both `samples` and `seeds` are provided, the counts must match.
Stage-level `stdin_text` and `stdin_file` override the top-level validator
stdin fixture; startup manifests replace those raw fields with a `stdin`
metadata object, while evaluation metadata records the resolved problem-local
file provenance when a file source is used.
Stage seeds are passed to validators as `stage["seed"]`. When the seed is not
`null`, LibreEvolve also derives a deterministic 32-bit `stage["rng_seed"]`,
sets subprocess `PYTHONHASHSEED` before launch, and seeds Python `random` plus
NumPy before importing the validator module. Stage `artifact_*` settings
override top-level evaluator artifact settings for that stage.
Each `validate_path` must resolve inside the problem directory to either a
Python file or a package directory containing `__init__.py`. Package validators
are imported as packages, so relative imports such as `from .helper import X`
work during preflight and evaluation. Preflight and evaluation enforce
problem-local evaluator dependency provenance: problem-owned imports and file
reads must target the configured entrypoint, captured companion files, or
captured declared data files.
Top-level `evaluator_data_*` settings define declared data globs relative to
each evaluator directory; stage-level `data_include` and `data_exclude`
override those top-level patterns for that configured stage.

Top-level evolution and population numeric fields are validated. Use
non-negative `max_generations`, `num_inspirations`, `migration_interval`, and
`ensemble_explore_coeff`; positive `proposals_per_generation`,
`eval_timeout_sec`, `n_islands`, `map_elites_bins`, and `elite_archive_size`;
and keep `explore_ratio` and `migration_ratio` between 0 and 1. Boolean runtime switches such as
`meta_prompt_evolution`, `critique_enabled`, `capture_proposal_metadata`, and
`llm_fallback` must be real booleans. `llm_max_retries` must be an integer
between `0` and `10`; `llm_max_call_attempts` must be an integer between `1`
and `32`. `llm_max_response_chars` and `llm_call_history_max` must be positive
integers. `llm_call_timeout_sec`, when set, must be a positive finite number.
`max_llm_calls`, `max_llm_provider_attempts`, `max_llm_tokens`, and
`max_llm_cost_microusd`, when set, must be non-negative integers. LLM role
budget maps must map manifest-safe role labels to non-negative integers.
`prompt_max_chars` and `prompt_max_estimated_tokens`, when set, must be
positive integers.
`prompt_artifact_content_mode` must be one of `excerpt`, `bounded_file`, or
`off`; `prompt_artifact_content_max_bytes` and
`prompt_artifact_content_max_chars` must be positive integers.
`mutation_prompt_retention_mode`, `explicit_context_retention_mode`,
`meta_prompt_evidence_retention_mode`, `quarantine_snapshot_retention_mode`,
`critique_retention_mode`, `feedback_retention_mode`,
`plugin_context_retention_mode`, `provider_response_retention_mode`, and
`provider_error_retention_mode` must be one of `full`, `redacted`,
`hash_only`, or `off`. `seed` must be an integer, `log_dir` must be a non-empty path string or path-like value,
`problem_name`/`--run-name` must be a safe portable and secret-safe run-name
component, and `critique_prompt` must be a string.

## CLI overrides

The `run` command exposes:

- `--max-generations`, `-g`
- `--max-evaluations`
- `--max-evaluator-seconds`
- `--max-runtime-seconds`
- `--max-llm-calls`
- `--plugins`, `-p` (repeatable)
- `--backends`, `-b` as `type:model` (repeatable)
- `--mutation-mode` (`diff` or `full`)
- `--seed`
- `--reasoning-effort`, `-r`
- `--llm-max-retries`
- `--llm-max-call-attempts`
- `--llm-fallback` / `--no-llm-fallback`
- `--llm-max-response-chars`
- `--llm-call-history-max`
- `--prompt-max-chars`
- `--prompt-max-estimated-tokens`
- `--explore-ratio`, `-e`
- `--parent-selection-strategy`
- `--inspiration-strategy`
- `--run-name`
- `--restore-rng-from-manifest`
- `--restore-llm-scheduler-from-manifest`
- `--restore-archive-cursor-from-manifest`
- `--restore-archive-from-manifest`
- `--restore-budget-from-manifest`
- `--overwrite`

CLI `--plugins` and `--backends` replace, rather than merge with, config-file
lists. CLI `--overwrite` sets the effective run collision policy to
`overwrite` for the current invocation. CLI scalar strategy overrides replace
the corresponding `config.yaml` values for the current run.

## Backend spec format

CLI backend specs use:

```text
openai:<openai-model-id>
anthropic:<anthropic-model-id>
ollama:<installed-ollama-model>
```

The placeholders above are not valid model ids until replaced. LibreEvolve
forwards model names to provider SDKs and does not verify current provider or
account availability. Check provider docs, your account's model list, or
installed Ollama tags before running longer experiments; these docs do not pin
to a provider model catalog. Startup manifests record this as
`policies.provider_capability_lookup` with
`local_static_validation_no_live_provider_lookup`: backend schemas, manifest-safe
model identifiers, client-context fields, and OpenAI static reasoning/API-mode
compatibility are checked locally, but live model registries, provider
service/API versions, and account availability are not queried before the run.

For OpenAI, optional `api_mode` controls the API route. `auto` is the default
policy and preserves legacy behavior: if `reasoning_effort` is omitted,
LibreEvolve uses Chat Completions; if it is present, LibreEvolve uses the
Responses API and forwards the configured reasoning effort. `responses` can be
set explicitly even without `reasoning_effort`; `chat_completions` cannot be
combined with `reasoning_effort`. The current code does not auto-route
reasoning-capable models to Responses when `api_mode` is omitted or `auto`, but
configured reasoning effort is validated against the local compatibility policy
before a run starts. Run manifests record
`policies.openai_api_mode.records[]` with the configured and effective route
for each OpenAI backend, and `policies.provider_capability_lookup.records[]`
links OpenAI records back to that route policy.
The CLI `--reasoning-effort` option applies to OpenAI backend specs from either
`config.yaml` or the same `--backends` invocation. It is ignored for non-OpenAI
backends.

## Environment variables

Common variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OLLAMA_HOST`

Provider SDKs may honor additional provider-specific variables.
LibreEvolve backend config accepts a small explicit endpoint/client-context
surface for built-in providers: OpenAI accepts `base_url`, `organization`, and
`project`; Anthropic accepts `base_url`; Ollama accepts `host`. Endpoint URLs
must be `http` or `https` URLs with a host and no credentials, params, query,
or fragment, while OpenAI organization/project labels must be manifest-safe
non-secret strings. Accepted values are persisted in `config.backends` and
copied into `client_context` call telemetry. Omitted fields still use provider
SDK/environment defaults.

LLM provider failures are recorded as structured call attempts. The ensemble can
retry the same backend with `llm_max_retries` and can route to another backend
when `llm_fallback` is enabled. If all attempts fail, exhausted mutation calls
can still abort before candidate/evaluation logging, while exhausted critique
calls fall back to the original mutation and exhausted meta-prompt calls record
rejected prompt mutations after already-logged candidate work. Feedback graders
use their configured failure policy. Ensemble telemetry keeps the exception
type separately, stores redacted/truncated error text, and records a normalized
`provider_failure_category` such as `provider_response`, `timeout`,
`rate_limit`, `transport`, provider client/server status categories, or
`unknown`. `llm_role_failure_quarantine_after` can quarantine a backend for a
configured exact role after exhausted consecutive failures, including timeout
failures, and runtime cancellation-policy manifests expose those quarantine
actions for timeout rules when configured. Built-in backend `timeout_sec`
values bound provider SDK requests where the SDK exposes that setting, and
`llm_call_timeout_sec` bounds the ensemble attempt wait for built-in or custom
backends. Remaining runtime budget is not propagated as a provider cancellation
token, but deadline-aware `LLMEnsemble` calls are clamped to the remaining
`max_runtime_seconds` budget before each attempt starts.
The ensemble-layer `llm_max_retries` value is capped at `10`, and
`llm_max_call_attempts` caps total original/retry/fallback attempts for each
logical ensemble call. Separate adapter-internal `provider_max_retries` caps
still mean these ensemble caps are not complete provider API request budgets.
The separate `llm_max_response_chars` control is a local accepted-output cap:
over-limit backend text is treated as a failed call before scheduler success
accounting and downstream mutation or persistence paths.
`prompt_max_chars` and `prompt_max_estimated_tokens` are the corresponding
local prompt-input caps for ensemble calls: when set, oversized prompts fail
before backend selection, call-history mutation, or provider/custom backend
invocation. The estimated-token cap uses the same deterministic four-character
heuristic as prompt section packing unless every role-eligible backend exposes
a common local provider-token counter, in which case the ensemble validates the
final prompt with that exact count and records
`prompt_token_counter_capability`, `prompt_token_count_policy`, and
`prompt_provider_tokens` in call telemetry.
Backend specs can set their own `prompt_max_estimated_tokens`; the same
role-scoped exact-or-heuristic policy is applied to the minimum eligible
backend/global cap.
Secret-like prompt text is not rejected at this boundary because private tasks
may include private context, but raw prompt text is not retained in LLM call
telemetry.
Generated-candidate mutation prompt persistence is controlled separately by
`mutation_prompt_retention_mode`: `redacted` stores the secret-redacted prompt
plus raw SHA-256/length metadata, `full` stores the full rendered prompt
subject to shared persisted-metadata secret redaction plus raw hash metadata,
`hash_only` stores no prompt text and keeps only raw hash/length metadata, and
`off` stores neither prompt text nor raw hash/length metadata.
Startup manifests expose the broader current-state policy under
`policies.prompt_data_retention` with schema
`libreevolve.prompt_data_retention.v1`. That record identifies mutation prompt
retention, critique prompt/mutation retention, and feedback raw/parsed output
retention, explicit context text, plugin context text, provider response/error text, meta-prompt
evidence, quarantine record snapshots, and DeepResearch retrieval bodies as configurable surfaces. The
DeepResearch surface is configured per plugin instance with
`retrieval_body_retention_mode`; selected values appear in
`runtime.plugin_state.loaded_specs`. LLM call prompt text remains
hash/count-only telemetry.
Final runtime manifests summarize these caps, explicit role backend lanes, and
per-role call/accounting counters under `runtime.llm_accounting` with policy
`audit_summary_not_budget_enforced`; the summary is for inspection and future
resume/budget design, not for live stop enforcement.
`llm_call_history_max` caps the in-memory `LLMEnsemble.call_history` retained
window. `LLMEnsemble.call_history_retention` records retained, total, and
dropped counts for diagnostics and loop-side span reconstruction; config-created
runs also write the durable `llm_calls.jsonl` call/reward stream.

## Known caveats

- The CLI does not expose every `Config` field directly; use `config.yaml` for
  migration, archive, prompt, stage, LLM feedback, critique, and ensemble
  scheduling settings.
- Config validation supports built-in plugin spec mappings and plugin-specific
  constructor schemas plus the bounded `libreevolve.plugins` entry-point spec
  with paper-scope labels plus manifest-safe or declared-schema constructor
  options. Runtime plugin specs now record
  `libreevolve.direct_plugin_policy.v1`: entry-point constructor options are
  captured from manifest-safe or declared-schema config, while direct-instance
  constructor values and instance attributes are explicitly excluded and scoped
  to module identity/file-hash/version-only package evidence. Provider/model API
  compatibility remains open. Invalid UTF-8, malformed YAML, duplicate
  mapping keys, and non-mapping top-level `config.yaml` files fail with
  path-aware startup errors. Top-level numeric fields,
  mutation/ensemble enums, backend specs, unknown problem-local keys,
  evaluator-stage numeric fields, and LLM feedback grader specs are checked
  before a run starts.
- CLI output-name semantics are intentionally separate from most config
  precedence: problem-local `config.yaml` cannot set `problem_name`; use
  `--run-name` to choose the output directory and effective manifest
  `problem_name`.
- Run-wide budget configuration is local and synchronous. `max_generations`,
  `max_evaluations`, `max_evaluator_seconds`, the detailed evaluator counter
  limits, `max_runtime_seconds`, `max_llm_calls`,
  `max_llm_provider_attempts`, `max_llm_tokens`, `max_llm_cost_microusd`, and
  per-role provider-attempt/token/configured-cost LLM limits are available.
  Runtime snapshots now report
  subprocess-attempt, configured-stage sample, retry, timeout, and sample/stage
  budget-exhaustion counters plus logical LLM-call, provider-attempt,
  provider-token, and configured estimated-cost counts. Detailed evaluator,
  LLM-call, provider-attempt, token, and configured-cost limits are cooperative
  and checked between safe runtime boundaries after counters are recorded;
  there are still no accelerator or async queue limits.
- Seeded replay is incomplete: `Config.seed` controls framework-owned local
  Python-random choices without mutating process-global RNG state, and
  configured prompt variants are selected in config order with deterministic
  database-created prompt ids. Loop-created seed and generated candidate ids
  are deterministic; direct `Program()` construction still defaults to UUID4.
  Runtime manifests persist the final run-local RNG state, direct callers can
  pass a validated snapshot back into `evolve()`, and CLI runs can restore that
  framework RNG snapshot with `--restore-rng-from-manifest`. Direct callers and
  CLI runs can also restore the compact archive cursor/counter snapshot with
  `runtime_archive_state_snapshot` or
  `--restore-archive-cursor-from-manifest`. Full archive restore additionally
  requires accepted `history.jsonl` rows: direct callers pass both
  `runtime_archive_state_snapshot` and `runtime_archive_programs_by_id`, while
  CLI runs can use `--restore-archive-from-manifest` to load the previous
  manifest plus sibling `history.jsonl`. Direct callers can pass
  `runtime_budget_state_snapshot`, and CLI runs can use
  `--restore-budget-from-manifest`, to apply prior consumed runtime budget
  counters before new work while appending a new wall-clock resume segment.
  Migration-event replay, async controller pending-work state, provider/model
  output replay, and plugin-owned RNG capture are still not a replay contract.
  Completed manifests do record a terminal drained synchronous controller state
  under `runtime.history.controller_state`.
  `runtime.rng.replay_boundary` records the current framework-owned RNG
  boundary and explicit external exclusions.
- `eval_stages` is still local subprocess execution. It is not yet a
  distributed evaluator-worker scheduler.
- Validator entrypoints are loaded from a temporary runner as either direct
  Python files or package `__init__.py` files. The validator directory is added
  to `sys.path`; package validators also add the problem root so package
  imports resolve. The candidate root is used as subprocess `cwd` and added to
  `sys.path`.
- Validator subprocess environment isolation is a local allowlist, not a
  container sandbox. `validator_network_policy: deny` blocks Python socket APIs
  during preflight/evaluation and records the boundary, but LibreEvolve still
  does not provide OS/container-level network isolation for validator code.
- Validator boundary metadata and startup `policies.validator_execution` include
  `filesystem_capabilities` and `resource_limit_policy` records. These declare
  the temporary candidate-root workspace, declared-problem-file provenance
  checks, bounded artifact copy-out, unsupported host-filesystem sandboxing,
  wall-clock timeout cleanup, and unsupported CPU/memory/GPU/disk/process-count
  quotas. They are audit evidence for the local runner, not enforcement of a
  configurable container or OS resource sandbox.
  `validate_validator_boundary_consistency.v1` compares the startup policy to
  attempt-level `evaluation.metadata.validator_boundary` records for the shared
  execution, filesystem, network, resource, and secret-boundary claims.
- `prompt_variants` populate the prompt-program database; set
  `meta_prompt_evolution: true` to allow interval-based LLM template mutation.
  Identical configured variants are intentionally admitted as separate prompt
  arms for compatibility with existing configurations; compare their
  `template_sha256` values in `prompt_history.jsonl` to detect content
  duplicates.
- Configured prompt variants and meta-prompt mutations are validated against
  the `PromptSampler` placeholder schema before use. Templates must include the
  required `{task}` placeholder and may use the documented context, parent,
  inspiration, failure, and mutation-mode placeholders. Unknown placeholders,
  malformed braces, empty placeholders, attribute/index placeholders, and
  blank templates or format specs that are incompatible with representative
  render-time values are rejected. Direct `PromptSampler(variants=...)`
  construction and build-time state use the same list-of-renderable-templates
  validation, so strings, generators, non-string items, and invalid templates
  fail before random selection. Direct `PromptSampler.build(..., template=...)`
  calls only fall back to configured/default templates when `template is None`;
  explicit blank strings are validation errors. Direct
  `PromptSampler(prompt_format_options=...)` construction validates the same
  weighted marker schema as `Config`. Stochastic marker names must match
  `[A-Za-z][A-Za-z0-9_-]{0,63}`, every `[[prompt:name]]` marker in a configured
  or direct template must have configured alternatives, nested stochastic
  markers inside alternative text are rejected, and alternative text is
  dry-run-rendered against the normal prompt placeholder schema before use.
  Direct `capture_proposal_metadata` values must be booleans before they can alter the
  expected prompt/output envelope. By default, configured seed variants also
  use `prompt_variant_semantic_policy: alphaevolve`, requiring core code-edit
  channels for task, parent code/workspace, mutation instructions, evaluator
  feedback, and context/inspiration. `prompt_variant_semantic_policy:
  compatibility` is the explicit degraded-template mode for minimal or
  externally managed prompts. Mutated prompt templates must also retain every
  placeholder used by their parent prompt program, so evolved
  children cannot silently drop existing code, feedback, inspiration, or
  mutation-format channels relative to that parent. Invalid
  LLM-mutated templates are written to
  `prompt_history_invalid.jsonl`, penalize the parent prompt program, and do
  not enter the prompt population.
- Prompt-program reward telemetry is written into `prompt_history.jsonl` under
  `program.metadata.last_prompt_reward`, including reward mode, raw reward,
  normalized reward, and bounds. The same effective prompt reward policy is
  recorded in `manifest.json`.
- Critique and LLM feedback use the same backend ensemble as mutation
  generation. They are synchronous and optional, not parallel reviewer workers.
