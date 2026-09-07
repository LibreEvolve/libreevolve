# Backends

LibreEvolve supports configured built-in, CLI, and custom backend types through
a common `generate(prompt, **kwargs) -> str` interface:

- OpenAI
- Anthropic
- Google Gemini
- Ollama
- Codex CLI
- Custom import-path backends

The bandit router that selects among them is implemented in
[`libreevolve/llm/ensemble.py`](../libreevolve/llm/ensemble.py).

## Provider lanes

Backend support has four distinct lanes:

- Built-in SDK adapters: OpenAI, Anthropic, Google Gemini, and Ollama are constructed by
  LibreEvolve and participate in the standard credential preflight,
  request-parameter, retry, timeout, scheduler, telemetry, and manifest
  surfaces documented below.
- Built-in CLI adapters: `type: codex` delegates generation to the local
  `codex exec` command. It supports command discovery, stdin prompt transport,
  `--output-last-message` response capture, sandbox/profile/auth-home
  configuration, local timeout cleanup, optional JSON-output extraction, and
  optional redacted transcript retention. It does not expose provider-native
  token usage or cost accounting, live model availability preflight, SDK-style
  retry diagnostics, or complete manifest/report parity yet.
- Custom import-path backends: `type: custom` loads an extension-owned Python
  object by `class_path` and calls its `generate(prompt, **kwargs) -> str`
  method. This is useful for experiments, but the custom backend owns any
  provider-specific authentication, command execution, transcript retention,
  token accounting, model availability checks, and diagnostics that are not
  exposed through the common interface.
- Unsupported local CLI wrappers: a user can still write a custom wrapper
  around any other local CLI, but that wrapper is not portable provider
  support, benchmark evidence, or paper-facing model-mix parity until it has a
  documented provider lane, manifest fields, diagnostics, and smoke fixtures.

Do not use Codex CLI or custom-wrapper examples to claim benchmark- or
paper-ready local CLI provider parity in README, ROADMAP, benchmark prompts, or
paper-facing materials. Required missing pieces for that stronger claim include
credential-safe live smoke tests, live model availability preflight,
manifest/report fields, provider-attempt token/cost limitations, provider-error
classification, and parity diagnostics.

## Selection and reward

`LLMEnsemble` wraps one or more backends and chooses one backend per mutation
attempt using a UCB-style heuristic over archive-admitted valid fitness
improvements. It is not a canonical UCB1 implementation; canonical regret
assumptions are explicitly out of scope unless the scheduler is promoted beyond
heuristic routing.

Current behavior:

- `generate(prompt, role=...)` returns both the raw backend response and the
  backend index
- mutation calls are reward-accounted scheduler pulls: the scheduler's global
  `total` counter advances before mutation backend selection, and the selected
  backend's `counts` entry advances after either a successful response or the
  final exhausted failed attempt for that selected backend; retry attempts
  before exhaustion do not separately increment `counts`
- critique, feedback-grader, and meta-prompt calls are telemetry-only by
  default. They are routed with the current scheduler state and recorded in
  call telemetry, but they do not advance `total`, do not increment backend
  `counts`, and cannot be rewarded through `record_reward()`.
- rewards are recorded only after evaluation and archive-admission decisions
- the evolution loop records zero reward for invalid, below-threshold, or
  feedback-discarded candidates and otherwise clamps reward to
  `max(0.0, child.fitness - parent.fitness)`
- the ensemble reward boundary accepts only non-negative finite numeric rewards
  for valid backend indexes, caps each update to `1.0`, and links each reward
  to exactly one successful backend call id; duplicate, missing, failed-call,
  wrong-backend, and already-rewarded call ids are rejected
- `record_reward(idx, reward)` without an explicit call id consumes the oldest
  unrewarded successful call for that backend, while the evolution loop passes
  the mutation call id captured on the generated candidate
- `LLMEnsemble.call_history` records normalized call telemetry: role, backend,
  backend metadata, strategy, scheduler policy, scheduler accounting mode, API
  mode, normalized request parameters, normalized built-in adapter defaults,
  normalized client context,
  prompt/output sizes and hashes, latency, status, redacted/bounded error
  fields, and counts before/after the call
- each call's `scheduler_policy` explicitly records that backend selection is
  still a shared `global_backend_bandit` policy, while reward accounting is
  configurable by role through sorted `reward_accounted_roles`
- call-history `id` values are deterministic identifiers for linking in-run
  reward events; they are derived from the ordered call span,
  backend/role/attempt coordinates, and prompt hash, so matching deterministic
  call streams produce matching ids while repeated calls inside one stream
  remain distinct
- `LLMEnsemble.call_history` is a bounded retained in-memory window controlled
  by `llm_call_history_max` / `--llm-call-history-max` with default `500`;
  `LLMEnsemble.call_history_retention` reports policy, max records, retained
  records, total records observed, and dropped records
- `LLMEnsemble.backend_metadata`, `LLMEnsemble.counts`,
  `LLMEnsemble.wins`, `LLMEnsemble.scheduler_state`, and
  `LLMEnsemble.call_history` expose defensive copies; callers cannot corrupt
  live scheduler metadata or counters by mutating returned containers
- `load_llm_call_ledger()` validates durable `llm_calls.jsonl` call/reward
  streams for call sequence continuity, duplicate call ids, reward rows linked
  to known successful calls, backend consistency, backend name/API-mode
  telemetry safety, request-parameter/backend-default/client-context telemetry safety, backend
  metadata/diagnostic shape, scheduler-accounting mode, and scheduler counter shape before returning
  replay metadata, including a derived role-accounting summary for successful,
  failed, retry, fallback, adapter-internal provider attempts, and
  provider-reported token totals by role, plus per-role provider-failure
  category counts
- `LLMEnsemble.restore_scheduler_state()` is the supported direct restore path
  for bandit counters and validates count/win lengths, finite non-negative
  values, total-selection type/range, count/total consistency, rewarded call
  ids, unrewarded per-backend call ids, duplicate call ids, and
  rewarded/unrewarded overlap before replacing live state; when retention
  diagnostics or role-accounting counters are present, their shape and counter
  consistency are validated
- runtime backend object `name` and `api_mode` attributes are normalized before
  call-history persistence; unsafe names fall back to the backend class name,
  invalid API modes become `null`, and structured diagnostics record the reason
  without retaining the unsafe value
- `LLMEnsemble.generate()` validates prompt payloads and call-role labels
  before scheduler selection. Prompts must be non-empty text, and when
  `prompt_max_chars` or `prompt_max_estimated_tokens` is configured they must
  fit those local character/heuristic-token caps before any backend sees them.
  Secret-like prompt text is allowed as private run input, but raw prompt text
  is not stored in call telemetry; records retain prompt length, estimated
  token count, and SHA-256. Roles must match
  `[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}`, must not end with `:`, and must not look
  like secrets
- the validated call role is passed to the selected backend as
  `generate(prompt, role=role)` on every original, retry, and fallback attempt;
  bundled adapters use the role to select any configured `llm_prompt_roles`
  system/developer instructions, while custom protocol-compatible backends can
  still use the role for their own request handling
- direct `LLMEnsemble` construction validates scheduler strategy,
  non-negative finite exploration coefficients, ensemble retry counts in the
  inclusive range `0..10`, total ensemble call attempts in the inclusive range
  `1..32`, boolean fallback policy, positive integer accepted-response size
  limits, optional positive integer prompt-size limits, and one JSON-safe
  backend-metadata mapping per backend before any call telemetry can be
  produced
- mutation, critique, and feedback call spans are attached to generated
  candidate metadata, including recovered retry/fallback attempts; meta-prompt
  calls are attached to prompt-history metadata. Config-created ensembles also
  stream complete run-level call/reward rows to `llm_calls.jsonl`; the
  candidate and prompt embeds are role-local references into that telemetry.
- built-in adapters copy safe provider usage counts, request/response ids, and
  finish reasons into call telemetry when SDK responses provide them; omitted
  or unsupported provider metadata remains `null`
- built-in adapters expose `backend_defaults` with LibreEvolve's effective
  local output-token cap, provider internal retry cap, configured request
  timeout or `null`, API mode, and OpenAI reasoning/API-mode policy when
  relevant; remote provider-side SDK defaults and pricing are not inferred
- raw provider diagnostics, provider-cost accounting, and token/cost budget
  stop policy are still unavailable
- `llm_reward_accounted_roles` controls which validated call roles advance the
  ensemble scheduler counters and can be rewarded. The default is
  `["mutation"]`, so critique, feedback, and meta-prompt calls remain
  telemetry-only unless explicitly configured otherwise. Scheduler snapshots
  expose the effective `reward_accounting_policy`.
- `llm_role_scheduler_scope` selects the scheduler state used for
  reward-accounted role selection. `shared` preserves the global ensemble
  bandit; `role_scoped` uses each role's restorable `role_scheduler_state`.
  Startup manifests, scheduler snapshots, runtime accounting, and per-call
  `scheduler_policy` records expose the effective scope.
- `llm_role_backend_indices` can route a validated call role to an explicit
  backend-index lane before scheduler selection. Roles without an explicit
  route can still use backend metadata `role` lanes; roles without either route
  keep the global backend bandit path. Call telemetry records the selected
  route source in `scheduler_policy`, and scheduler snapshots retain a
  `role_backend_policy` audit record.
- `llm_role_failure_quarantine_after` can opt a role into deterministic
  provider-failure quarantine after a configured number of consecutive
  exhausted failures for the same backend. Quarantined backends are excluded for
  that role on later logical calls, failed rewarded-role calls record an
  explicit zero-reward scheduler penalty, and scheduler snapshots retain
  `provider_failure_policy_state` so restore preserves the quarantine counters.
- failed provider calls are recorded in ensemble telemetry with retry/fallback
  attempt indexes and secret-pattern redaction/truncation applied to exception
  text; `llm_max_retries` can retry the same backend, `llm_fallback` can try
  another backend, and `llm_max_call_attempts` caps total original, retry, and
  fallback attempts for that logical call; exhausted failed backend selections
  count as zero-reward pulls so a recovered fallback backend can be preferred
  after it receives reward. Exhausted mutation failures can still abort before
  candidate/evaluation logging; exhausted critique failures fall back to the
  original mutation with bounded failure metadata, and exhausted meta-prompt
  failures record rejected prompt mutations instead of aborting already-logged
  candidate work.
- failed provider calls also record `provider_status_code` when the raised SDK
  exception exposes a safe integer HTTP-style `status_code`; successful calls
  and non-status failures keep that field `null`
- `llm_max_retries` starts after the backend adapter raises. The built-in
  OpenAI, Anthropic, and Ollama adapters have a separate
  `provider_max_retries` cap for adapter-internal provider attempts; the
  default is `2`, preserving one original call plus two internal retries.
  Successful and failed call telemetry records `adapter_retry` with the
  configured cap, provider attempts, failed attempt count, and safe exception
  type labels. The ensemble-layer retry count is capped at `10` and total
  ensemble call attempts are capped at `32`.
- provider calls can be bounded at two layers. Built-in backend specs can set
  a positive `timeout_sec`, which is forwarded as the provider SDK/client
  request timeout where the bundled OpenAI, Anthropic, and Ollama clients
  expose one. Run-level `llm_call_timeout_sec` adds an ensemble deadline around
  each backend `generate()` attempt, including custom backends; timeout
  attempts are recorded as `ProviderCallTimeoutError` with
  `provider_failure_category: timeout` and can use the normal retry/fallback
  path. Deadline-aware `LLMEnsemble` calls are also clamped to the remaining
  `max_runtime_seconds` budget before each attempt starts. When
  `llm_role_failure_quarantine_after` is configured for a role, exhausted
  timeout failures also participate in that role/backend quarantine policy and
  runtime cancellation-policy manifests declare the matching quarantine action
  and evidence artifact. Runtime cancellation-policy manifests also summarize
  observed timeout failures and quarantined backend counts from the LLM
  scheduler snapshot. There is still no hard provider cancellation handle or
  timeout-specific stop policy.
- empty, whitespace-only, non-text, oversized, refusal, or tool-call-only
  backend response payloads are recorded as failed ensemble calls with
  `provider_response_error` categories, normalized
  `provider_failure_category`, nullable `provider_status_code`, and
  retry/fallback eligibility before mutation parsing or success counters
  advance
- backend responses longer than `llm_max_response_chars` are also recorded as
  failed ensemble calls before success counters, output hashes, mutation
  parsing, prompt histories, or candidate metadata can treat the payload as an
  accepted proposal; the default cap is `100000` characters
- ensemble prompts longer than configured `prompt_max_chars` or heuristic
  `prompt_max_estimated_tokens` are rejected before scheduler state, call
  history, provider SDK payload construction, or custom backend invocation
  changes. Direct custom-backend calls outside `LLMEnsemble` remain
  extension-owned.
- backend specs and direct backend metadata can set
  `prompt_max_estimated_tokens`; when present, the ensemble applies the minimum
  applicable global and eligible-backend prompt-token cap before provider
  calls. When every role-eligible backend exposes the same locally available
  provider tokenizer, the ensemble uses that exact count for mutation,
  critique, feedback, meta-prompt, registry-created, and custom role labels;
  otherwise it records role-scoped token-counter capability diagnostics and
  falls back to the heuristic character-derived estimate. This is
  model/context-window evidence at the final prompt boundary, not complete
  provider-tokenizer-backed section packing.
- backend specs and direct backend metadata can set `context_window_tokens`
  plus optional `reserved_output_tokens`; the ensemble subtracts the reserve
  from the window and applies the resulting heuristic prompt-token capacity
  before provider calls. If a backend spec omits `reserved_output_tokens` but
  sets `max_tokens`, that output cap is used as the reserve; explicit reserves
  require `context_window_tokens` and must be smaller than it.
- the bundled OpenAI, Anthropic, and Ollama adapters also validate direct
  `generate(prompt)` calls with the same non-empty text prompt policy before
  constructing provider SDK payloads
- the bundled adapters validate extracted provider response text before
  returning it: OpenAI Chat/Responses, Anthropic Messages, and Ollama Chat
  missing, empty, whitespace-only, or non-text content raises a provider-labeled
  `ProviderResponseError`; OpenAI Chat/Responses and Anthropic Messages also
  categorize refusal/tool-call-only shapes when exposed by the provider payload

This means backends are rewarded for admitted valid improvement over the
selected parent, not for absolute score. Role-level call/retry/fallback counts
and provider-reported token totals are now visible in scheduler snapshots and
ledger replay. Completed and aborted runtime manifests also expose the same
role-accounting counters through compact `runtime.llm_accounting` totals
alongside the active LLM call/retry/fallback, timeout, prompt, and
accepted-output caps. Provider-failure categories are likewise summarized by
role. Per-call scheduler policy records now state whether the call's role is
reward-accounted or telemetry-only, the bounded local reward contract enforced
by `LLMEnsemble.record_reward()`, matching pre-selection logical-call quota
scopes, and whether selection state is global, role-owned, or telemetry-only.
Calibrated role-specific reward semantics, experiment-owned quotas, and
Flash/Pro-style fast/strong scheduling evidence remain known gaps.

For `ensemble_strategy: throughput_depth`, the scheduler uses numeric `cost`,
`latency`, and `depth` metadata after every non-excluded backend has been
selected once. On each selection, selectable backend metadata is min/max
normalized per field; equal-valued fields use neutral `0.5`. The fixed
metadata weights are `depth: 0.10`, `cost: -0.05`, and `latency: -0.05`, so
metadata can influence close choices without letting extreme raw values
overwhelm a full `1.0` empirical reward difference. Call telemetry records the
effective scheduler policy. The optional `role` field is preserved as
descriptive metadata but does not create breadth/depth quotas, escalation
rules, or role-specific routing. Configured role labels must be manifest-safe,
but custom labels are not interpreted by the scheduler. The persisted
`scheduler_policy.throughput_depth_lane_evidence` record lists eligible
backends, normalized cost/latency/depth values, missing metadata defaults, and
explicit fast-breadth or strong-depth lane labels when `model_lane` or `role`
metadata uses recognized values. It remains
`metadata_trace_not_experiment_report`, not proof of AlphaEvolve Flash/Pro
scheduling.

Configured backend model identifiers are persisted in run manifests and call
telemetry, so `Config` accepts only manifest-safe strings matching
`[A-Za-z0-9][A-Za-z0-9_.:/+-]{0,191}` and rejects values matching shared
secret-redaction patterns. This is a metadata-safety check, not a provider
availability or capability check.

The bundled OpenAI, Anthropic, Google Gemini, and Ollama adapter constructors apply the same
manifest-safe model-id grammar and require positive integer token limits for
direct library use. OpenAI direct construction also validates `reasoning_effort`
against the current LibreEvolve/OpenAI compatibility policy.

`build_llm(config)` revalidates and copies the effective backend specs at LLM
construction time before adapter construction, so post-validation mutation of
`config.backends` cannot silently alter backend type, model id, token limits,
prompt-token caps, scheduler metadata, or role labels.
The registry facade in
[`libreevolve/llm/backend_registry.py`](../libreevolve/llm/backend_registry.py)
uses the same backend normalizer for registry-created provider constructors;
`validate_backend_registry_specs()` returns a defensive normalized spec copy
and `build_registry_backends()` constructs validated built-in or custom backend
objects plus scheduler metadata. Registry-created objects are ordinary backend
objects; when used through `LLMEnsemble`, they inherit the same prompt type,
size, role, timeout, retry/fallback, and response-size boundaries.

Google Gemini is a built-in registry provider backed by `google-genai` and the
Gemini Developer API. Completed manifests record partial readiness under
`runtime.history.gemini_provider_parity_report` with schema
`libreevolve.gemini_provider_parity_report.v1`: the report lists configured
Gemini providers, separates first-class from custom wrappers, classifies
Flash/Pro-shaped lanes, and credits local credential/client/request/telemetry
support while keeping `claim_ready: false`. The report does not prove live
account/model availability, current availability of the paper's Gemini 2.0
Flash and Pro endpoints, a credential-safe live pair run, a model-registry
snapshot, calibrated fast/strong scheduling, or substitution equivalence.
The paper-facing partial-readiness boundary is preserved in
`papers/gemini_provider_parity_boundary.json` for manifest validation.

Built-in backend specs expose a small validated request-parameter surface:
`temperature` and `top_p` for OpenAI, Anthropic, Gemini, and Ollama; `stop` for
Anthropic, Gemini, Ollama, and OpenAI Chat Completions mode; and `seed` for
Gemini, Ollama, and OpenAI Chat Completions mode. OpenAI Responses mode forwards only
`temperature` and `top_p`. Omitted fields use provider SDK defaults.

`llm_prompt_roles` is a run-level structured prompt-message policy keyed by
call role. Each role can provide bounded `system` and/or `developer` text.
When a role is configured, OpenAI Chat Completions and Responses receive those
messages/input items before the rendered user prompt, Anthropic receives the
provider-supported `system` field, Gemini receives `system_instruction`, and
Ollama receives a system message followed by the user prompt. Omitted roles
use the default single user message/input item. Call telemetry records the
matched role, message-role list, instruction field names, and hash/length
metadata, not the raw configured instruction text.
Custom backends should put provider-specific request settings in their
JSON-safe `kwargs`; the built-in top-level request-parameter fields are
rejected for `type: custom` and `type: codex`.

Built-in SDK backend specs also accept positive `timeout_sec`. LibreEvolve
passes that value to the bundled provider client constructors as a request
timeout: OpenAI and Anthropic receive `timeout=...`; Gemini converts seconds
to the Gen AI SDK `HttpOptions.timeout` millisecond field; Ollama constructs an
`ollama.Client(..., timeout=...)`, with or without a configured `host`. The
Codex CLI backend uses `timeout_sec` as a local process deadline for
`codex exec`, then attempts process-tree cleanup and writes a transcript when
configured. Custom backends should carry provider-specific timeout settings
through their JSON-safe `kwargs`. Separately, run-level
`llm_call_timeout_sec` wraps each ensemble backend attempt with a local
deadline and structured timeout telemetry. Deadline-aware `LLMEnsemble` calls
are also clamped to the remaining `max_runtime_seconds` budget before each
attempt starts, but this is not a hard provider cancellation contract.

Built-in backend specs also accept `provider_max_retries`, a non-negative
adapter-internal retry cap. The default `2` preserves the historical three
provider attempts. Custom backends should carry provider-specific retry
settings through their JSON-safe `kwargs` and expose safe telemetry through
`provider_response_metadata` if they want it copied into `llm_calls.jsonl`.

Built-in backend specs also expose validated client-context fields when a run
needs explicit endpoint provenance instead of provider SDK/environment
defaults. OpenAI accepts `base_url`, `organization`, and `project`; Anthropic
accepts `base_url`; Gemini accepts `api_version` as `v1`, `v1alpha`, or
`v1beta`; Ollama accepts `host` and uses `ollama.Client(host=...)`
when configured. Endpoint URLs must be `http` or `https` URLs with hosts and
no credentials, params, query, or fragment; organization/project labels must
be manifest-safe and non-secret. Accepted values are copied into
`client_context` call telemetry. Omitted fields still use provider SDK
defaults.

## Google Gemini backend

Implemented in [`libreevolve/llm/gemini.py`](../libreevolve/llm/gemini.py)
with the official `google-genai` SDK and Gemini Developer API
`models.generate_content` surface.

Constructor fields:

- `model`
- `max_tokens`
- `temperature`
- `top_p`
- `stop`
- `seed`
- `timeout_sec`
- `api_version` (`v1beta` by default; `v1` and `v1alpha` are also accepted)
- `provider_max_retries`

Credential behavior:

- `GOOGLE_API_KEY` and `GEMINI_API_KEY` are accepted from the environment
- `GOOGLE_API_KEY` takes precedence when both are set, matching the SDK policy
- API keys are passed to the SDK client but are never copied into config,
  client-context, call telemetry, or manifests
- CLI and direct backend construction fail before a provider call when neither
  variable contains a nonblank value

Generation behavior:

- sends the rendered prompt as the user `contents`
- maps `max_tokens` to `max_output_tokens`
- maps `stop` to `stop_sequences` and forwards configured `temperature`,
  `top_p`, and `seed`
- composes configured system/developer role instructions into
  `system_instruction`
- concatenates all text parts from the first candidate only when its finish
  reason is `STOP`
- rejects prompt blocks, safety/recitation/prohibited-content outcomes,
  `MAX_TOKENS` and other incomplete states, tool-only output, mixed text/tool
  output, absent candidates, and empty text before mutation parsing
- records prompt/candidate/total token counts, response id, finish reason,
  model version, candidate/part counts, tool/text part counts, thinking-token
  count, API version, local defaults, and bounded retry diagnostics

The adapter classifies model ids containing `flash` or `pro` for runtime lane
reports, and normal ensemble selection/routing can schedule both configured
lanes. This is provider plumbing, not proof that the original Gemini 2.0
endpoints remain available, that an account can access both models, or that
LibreEvolve reproduces AlphaEvolve's throughput/quality balance. Live model
lookup, model-registry snapshots, credential-safe pair-run evidence,
equal-budget scheduling experiments, and substitution policy remain open.

## OpenAI backend

Implemented in [`libreevolve/llm/openai.py`](../libreevolve/llm/openai.py).

Constructor fields:

- `model`
- `max_tokens`
- `reasoning_effort`
- `api_mode`
- `temperature`
- `top_p`
- `stop` (Chat Completions mode only)
- `seed` (Chat Completions mode only)
- `timeout_sec`
- `base_url`
- `organization`
- `project`
- `provider_max_retries`

Behavior:

- `api_mode="auto"` preserves legacy routing: Chat Completions unless
  `reasoning_effort` is set, otherwise Responses
- `api_mode="responses"` forces the Responses API even without
  `reasoning_effort`
- `api_mode="chat_completions"` forces Chat Completions and is rejected when
  `reasoning_effort` is set
- both code paths retry up to `provider_max_retries + 1` provider attempts
  with exponential backoff between failed attempts
- direct calls require `prompt` to be non-empty text before SDK payload
  construction
- `Config` and direct construction accept `none`, `minimal`, `low`, `medium`,
  `high`, and `xhigh` only after the local model-aware compatibility check
- there is no automatic model-capability detection; a reasoning-capable model
  with `api_mode` omitted or set to `auto` and without `reasoning_effort` still
  follows the Chat Completions path
- startup manifests record `policies.provider_capability_lookup` with
  `local_static_validation_no_live_provider_lookup`; LibreEvolve does not query
  live provider model registries, provider service/API versions, or account
  availability before a run

API split:

- Chat Completions call:
  - `chat.completions.create(...)`
  - uses `max_completion_tokens`
  - passes configured `temperature`, `top_p`, `stop`, and `seed` when present
  - sends `messages=[{"role": "user", "content": prompt}]`
- Responses call:
  - `responses.create(...)`
  - uses `max_output_tokens`
  - passes configured `temperature` and `top_p` when present
  - passes `reasoning={"effort": ...}`
  - sends `input=[{"role": "user", "content": prompt}]`

OpenAI currently recommends Responses for new projects, and its docs describe a
richer experience for reasoning models through Responses. LibreEvolve has not
made Responses the default OpenAI path, but the route is now an explicit
`api_mode` policy. Run manifests record configured and effective OpenAI routes
under `policies.openai_api_mode.records[]`. LibreEvolve also validates
configured reasoning effort against documented current values and selected
model-family limits before provider calls. The local policy rejects known
incompatible combinations such as `none` on known pre-`gpt-5.1` families,
non-`high` effort on `gpt-5-pro`, and `xhigh` on unrecognized or ineligible
families. Unknown future model ids still receive only the global effort enum
check. This local static policy is manifest-visible under
`policies.provider_capability_lookup` and is intentionally offline-compatible;
live provider capability evidence remains call-time/provider-side behavior.

## Anthropic backend

Implemented in [`libreevolve/llm/anthropic.py`](../libreevolve/llm/anthropic.py).

Constructor fields:

- `model`
- `max_tokens`
- `temperature`
- `top_p`
- `stop`
- `timeout_sec`
- `base_url`
- `provider_max_retries`

Behavior:

- uses `messages.create(...)`
- sends `messages=[{"role": "user", "content": prompt}]`
- passes configured `temperature`, `top_p`, and `stop_sequences` when present
- returns the first text block from `msg.content`
- retries up to `provider_max_retries + 1` provider attempts with exponential
  backoff between failed attempts
- direct calls require `prompt` to be non-empty text before SDK payload
  construction

## Ollama backend

Implemented in [`libreevolve/llm/ollama.py`](../libreevolve/llm/ollama.py).

Constructor fields:

- `model`
- `max_tokens`
- `temperature`
- `top_p`
- `stop`
- `seed`
- `timeout_sec`
- `host`
- `provider_max_retries`

Behavior:

- uses `ollama.chat(...)` by default, or `ollama.Client(host=...).chat(...)`
  when `host` is configured
- sends `messages=[{"role": "user", "content": prompt}]`
- passes `num_predict` as the output token limit
- passes configured `temperature`, `top_p`, `stop`, and `seed` in `options`
  when present
- retries up to `provider_max_retries + 1` provider attempts with exponential
  backoff between failed attempts
- direct calls require `prompt` to be non-empty text before SDK payload
  construction

This backend is useful for local experimentation where API cost or offline work
matters more than peak model quality.

## Codex CLI backend

Implemented in [`libreevolve/llm/codex_cli.py`](../libreevolve/llm/codex_cli.py).

Constructor fields:

- `model`
- `max_tokens` (stored as LibreEvolve metadata only; the current `codex exec`
  help exposes no direct max-output-token flag for this invocation)
- `cwd`
- `sandbox`
- `timeout_sec`
- `reasoning_effort`
- `transcript_dir`
- `codex_home`
- `auth_name`
- `auth_homes`
- `auth_registry_path`
- `profile`
- `approval_policy`
- `ignore_user_config`
- `ignore_rules`
- `ephemeral`
- `output_json_field`
- `enable_features`
- `disable_features`

Behavior:

- runs `codex exec` from the local PATH with the prompt on stdin and captures
  the final message through `--output-last-message`
- reads `--json` completion events for reported input/output/total tokens;
  cached and reasoning counters are retained as bounded diagnostics when present
- passes `--model`, `--sandbox`, `--cd`, `--profile`, `--ignore-user-config`,
  `--ignore-rules`, `--ephemeral`, repeated `--enable`/`--disable` flags, and
  selected `-c` config overrides when configured
- supports `auth_name` resolution through explicit `auth_homes`, a JSON auth
  registry, `LIBREEVOLVE_CODEX_AUTH_<NAME>_HOME`, or the default/current
  `~/.codex` home without recording secret material
- when `codex_home` is configured, sets `CODEX_HOME` and removes
  `OPENAI_API_KEY` from the child process environment so Codex CLI auth remains
  separate from OpenAI SDK credentials
- optionally writes transcript JSON records with schema
  `libreevolve.codex_cli_transcript.v1`, including hashes, redacted auth-home
  metadata, command settings, stdout/stderr, and the captured final message
- optionally asks Codex for a JSON-shaped final response and extracts one
  configured string field
- treats non-zero exit codes, empty final messages, invalid structured output,
  and local process timeouts as generation failures

Current limitations:

- no credential-safe live smoke test is committed
- no live Codex model availability preflight is performed before a run
- dollar cost, finish reason, request id, and internal provider retry counts
  are not reported; attempt accounting counts local CLI invocations
- no run-manifest/report integration promotes Codex CLI runs to
  benchmark-claim-ready provider evidence
- cancellation is local process cleanup, not a provider-side cancellation
  guarantee

## Environment setup

Typical environment variables:

```text
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
OLLAMA_HOST=http://localhost:11434
```

Endpoint/client context can either be inherited from provider SDKs and
environment or configured explicitly in backend specs. OpenAI accepts
`base_url`, `organization`, and `project`; Anthropic accepts `base_url`; Gemini
accepts `api_version`; Ollama
accepts `host`. Explicit endpoint URLs are validated as safe `http`/`https`
URLs without credentials, params, query, or fragment, and accepted values are
recorded in manifests and copied into `client_context` call telemetry.

The `run` command loads `.env` during run setup with `override=True`, before
backend preflight, so `.env` values override same-named parent-process
environment variables for evolution runs. Importing `libreevolve.cli` and
running `libreevolve show` do not load `.env`. Run manifests record non-secret
dotenv provenance under `manifest.provenance.dotenv`, including load status,
override policy, source hash/byte count, and key names without values.
For runs where a mutation LLM can run, startup checks required credentials for
OpenAI (`OPENAI_API_KEY`), Anthropic (`ANTHROPIC_API_KEY`), and Gemini
(`GOOGLE_API_KEY` or `GEMINI_API_KEY`) as non-blank
after trimming, then constructs the configured backend clients before
run-directory overwrite cleanup. Seed-only runs such as `--max-generations 0`
skip provider construction.

## Adding a new backend

Configured custom backends use `type: custom` plus an importable
`class_path` in `module.path:ClassName` form. The class is constructed with
the top-level `model`, optional `max_tokens`, and optional JSON-safe `kwargs`.
It must return an object that satisfies the `LLMBackend` protocol:

- `generate(prompt, **kwargs) -> str`
- `name` property

The ensemble passes validated call roles as `generate(prompt, role=...)`, so
custom backends should accept `**kwargs` even if they ignore the role.
`class_path` must be manifest-safe, and `kwargs` must be JSON-safe with
manifest-safe keyword labels. `model` and `max_tokens` are reserved top-level
backend fields and cannot be shadowed inside `kwargs`.

Example `config.yaml`:

```yaml
backends:
  - type: custom
    model: my-model
    class_path: mypackage.backends:MyBackend
    max_tokens: 4096
    kwargs:
      endpoint_label: local_lab
    role: depth
    cost: 1.0
    latency: 1.0
    depth: 2.0
```

Minimal skeleton:

```python
class MyBackend:
    def __init__(self, model: str = "my-model", max_tokens: int = 4096):
        self._model = model
        self._max_tokens = max_tokens

    @property
    def name(self) -> str:
        return f"mybackend/{self._model}"

    def generate(self, prompt: str, **kwargs) -> str:
        ...
```

Adding a first-class built-in provider still requires source edits, but
experiment-specific providers no longer require editing `build_llm()`.

## Practical guidance

- Prefer non-reasoning OpenAI or Anthropic models when you want cheaper, shorter
  mutations.
- Use `reasoning_effort` sparingly. Long internal reasoning can consume output
  budget and reduce useful diff text.
- Mix backends when exploring a new problem. The ensemble tracks which backend
  has produced useful mutations for that task.
