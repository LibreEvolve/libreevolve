# Plugins

LibreEvolve plugins are synchronous hook objects used by the main evolution
loop. The interface is defined in
[`libreevolve/plugins/base.py`](../libreevolve/plugins/base.py).

Configured plugin aliases must be manifest-safe labels before manifest
persistence: non-empty strings matching
`[A-Za-z0-9][A-Za-z0-9_.-]{0,127}` that do not look like secrets. `plugins`
may also contain built-in spec mappings with `name` and `options`, for example:

```yaml
plugins:
  - name: deep_research
    options:
      search_every: 2
      max_events: 25
      cache_mode: offline
```

Option names must be manifest-safe identifiers. `Config` validates built-in
plugin names and option schemas before startup returns a usable configuration,
so CLI runs reject invalid configured specs before overwrite cleanup or plugin
construction. Direct runtime manifests record `runtime.plugin_state` so
configured labels can be compared with loaded plugin instances.

## Hook contract

Plugins may override any subset of these methods:

```python
class PluginBase(ABC):
    def on_generation_start(self, gen: int, db: ProgramDatabase) -> None: ...
    def on_evaluated(self, program: Program, score: float) -> float: ...
    def on_generation_end(self, gen: int, best: Program) -> None: ...
    def build_extra_context(self, parent: Program, inspirations: list[Program]) -> str: ...
    def prompt_context_metadata(self) -> dict: ...
    def run_artifacts_metadata(self) -> dict: ...
```

Direct library calls validate explicit plugin objects before run-directory
setup. `PluginBase` subclasses are accepted. Duck-typed plugins are accepted
when any provided hook attributes are callable and the object exposes the hooks
the selected run mode will call. Mutation-capable runs require callable
`on_generation_start()`, `build_extra_context()`, `on_evaluated()`, and
`on_generation_end()` hooks. Zero-generation runs may use artifact-only plugin
objects such as an object with `run_artifacts_metadata()`. Invalid objects are
rejected before manifest/history creation or overwrite cleanup.
When `evolve()` is called without explicit `plugins=[...]`, it resolves
`Config.plugins` through the built-in registry and constructs run-scoped plugin
instances. Passing explicit plugin objects still works for custom or
preconstructed plugins and disables core config resolution for that call.

## Execution order

Plugins run in configured order, whether they come from CLI `--plugins`,
problem-local `config.yaml`, or explicit direct `plugins=[...]` objects.

Per generation, the loop calls them in this order:

1. select the parent candidate
2. `on_generation_start()`
3. select inspiration candidates
4. `build_extra_context()`
5. `prompt_context_metadata()`
6. `on_evaluated()`
7. `on_generation_end()`

At run finalization, plugins that expose `run_artifacts_metadata()` can add
artifact summaries to the runtime manifest.

Important details:

- `on_generation_start()` is pre-prompt but post-parent-selection; it can
  affect inspiration sampling and prompt construction, but not the parent
  already selected for the active generation.
- `build_extra_context()` is called before mutation generation.
- `prompt_context_metadata()` is stored with the plugin-context record for a
  generated candidate. It runs for each plugin during plugin-context
  construction even when that plugin emitted no prompt text; such records are
  marked with `emitted: false`, `context_visibility: "not_prompt_visible"`,
  and `metadata_visibility: "provenance_only"` when metadata is present. Each
  plugin-context record also includes sanitized version metadata when a plugin
  instance, class, or module exposes `__version__`, plus `plugin_spec`, using
  the same validated built-in constructor-parameter schema as
  `runtime.plugin_state.loaded_specs`; custom direct plugin instances record
  constructor signature shape only, with no constructor values captured. When
  plugin text is injected, records use `context_visibility: "prompt_visible"`
  and metadata uses `metadata_visibility: "prompt_visible_context"`. The hook
  may return `None` or `{}` to emit no metadata; any non-empty return must be a
  mapping. Metadata dictionary keys, including keys nested inside lists or
  child dictionaries, must be strings and must not contain Unicode format
  controls such as right-to-left override or zero-width joiner. Secret-like or
  oversized keys are persisted as bounded hash-suffixed labels, with
  credential-shaped keys using a neutral redacted label. Metadata values must
  be JSON-safe finite primitives, lists, or dictionaries. String values are
  bounded, reject Unicode format controls, and receive the shared versioned
  secret-pattern grammar before being persisted. Non-mapping metadata returns
  abort the run
  during plugin-context construction with plugin-failure provenance.
- plugin snapshot APIs return defensive copies for nested DeepResearch
  retrieval events and queued TTTRL training rows, so inspecting returned
  metadata or training data does not mutate live plugin state.
- `on_evaluated()` receives a fully constructed `Program`, including:
  - `parent_id`
  - `generation`
  - `lineage`
  - `metadata["prompt"]`
  - `metadata["diff"]`
- the return value from `on_evaluated()` becomes the program's final top-level
  fitness for threshold gating, logging, backend reward, and prompt scoring;
  backend reward uses that final score only when the candidate is
  evaluator-valid and archive-admitted.
- MAP-Elites cell competition, elite ordering, and parent sampling still use
  `metadata.selection_score`, computed from declared objective metrics before
  plugin hooks. Feedback-sourced objective metrics can contribute after their
  graders fill them; plugin-added metrics are persisted as ordinary metrics
  when valid, but they do not affect archive ranking unless a future
  plugin-metric selection policy is added.
- plugin score adjustments are recorded under `metadata.score_composition`,
  including per-plugin before/after scores, metric additions/changes, invalid
  score rejections, and whether final top-level fitness diverges from
  `evaluation.fitness`.
- archive admission is still gated by `evaluation.is_valid`; a plugin can lower
  or raise top-level fitness for threshold gating, but it cannot accidentally
  archive an evaluator-invalid candidate unless an explicit future override
  policy is added.
- `run_artifacts_metadata()` is called near manifest finalization and should
  return small JSON-compatible provenance for plugin-owned files. Metadata keys
  are validated with the same display-safe label policy as prompt-context
  metadata. The hook may return `None` or `{}` to emit no artifact entry; any
  other non-mapping return is a schema error. Manifest artifact entries are
  wrapped with runtime-derived `plugin`, `module`, `class`, `index`, and
  run-local `instance_id` fields, while plugin-supplied fields are stored
  under nested `metadata`. The same `instance_id`
  (`plugin:{index}:{module}.{qualname}` for ordinary safe labels) appears in
  startup provenance, prompt-context records, score-composition entries,
  artifacts, and plugin failures so duplicate same-class instances can be
  correlated. Runtime plugin identity labels are NFC-normalized, Unicode format
  controls are escaped, secret-like text is redacted, and changed labels carry
  hash-backed raw identity fields such as `class_hash` and `instance_id_hash`.
- completed runs abort when `run_artifacts_metadata()` raises or returns
  invalid metadata. Aborted-run finalization still attempts to collect valid
  plugin artifact summaries and records summary failures under
  `runtime.plugin_artifact_failures[]` without hiding the original abort.
- plugin hook exceptions are fatal run aborts, not ignored or retried. The
  original exception is re-raised, and the aborted runtime manifest records
  `runtime.abort.plugin_failure` plus `runtime.plugin_failures[]` with the
  redacted runtime plugin class/module/index, hook name, fatal policy, generation and
  parent/candidate ids when available, exception type/message, redaction and
  truncation diagnostics, and `continued: false`.

## What plugins can safely do

Plugins can:

- inspect the program database
- add prompt context
- maintain internal state
- modify the effective score
- write external logs or training data

Plugins should not assume:

- asynchronous execution
- thread safety
- a stable plugin dependency graph
- that other plugins have or have not modified the score already

If a plugin mutates `Program.metrics` in `on_evaluated()`, metric keys must use
the same manifest-safe metric-name grammar as `metrics.yaml` names, including
optional dotted namespaces. Unsafe metric side effects are reverted, the plugin
score change is not accepted, and `metadata.score_composition.plugins[]`
records `error: "invalid_plugin_metrics"` with a bounded validation message.
If a plugin mutates `Program.metadata`, the updated metadata must remain a
JSON-safe finite mapping with display-safe labels. Valid metadata additions are
persisted; unsafe metadata side effects are reverted, the plugin score change
is not accepted, and the score-composition entry records
`error: "invalid_plugin_metadata"` with a bounded redacted validation message.

## Built-in plugins

### `causal`

Implemented by
[`libreevolve/plugins/causal.py`](../libreevolve/plugins/causal.py).

Purpose (CausalEvolve-inspired, not paper-complete):

- infer what kinds of code edits tend to help
- bias prompt context toward the most promising edit factor

Mechanics:

- inspects mutation text from `program.metadata["diff"]` and
  `program.metadata["mutation_mode"]`
- uses `program.metadata["causal_reward_baseline"]` when the evolve loop
  provides selected-parent score context, with `metadata["parent_score"]` as a
  direct-plugin fallback
- classifies changes into heuristic factors such as loop structure, constants,
  helper functions, and algorithm choice
- uses the shared compact/canonical SEARCH/REPLACE parser for diff-mode
  mutations and direct token-pattern scanning for full-mode replacement payloads
- treats missing diff evidence as no matched factors and treats non-text diff
  evidence as malformed mutation evidence, falling back to the deterministic
  default factor instead of raising from the diff parser
- selects each fixed factor once in stable order before using a UCB1-like reward
  score
- injects a short causal guidance block into future prompts
- requires finite numeric scores at the plugin hook boundary and quarantines
  malformed restored causal history before rendering prompt context
- retains at most `history_limit` recent outcome records in memory
  (`500` by default), while aggregate factor counts and rewards continue to
  cover all evaluated plugin observations
- records `baseline_score`, `baseline_source`, and `baseline_parent_id` with
  each causal-history row
- reports retained, dropped, quarantined, malformed-evidence, and total
  causal-history counts plus factor baseline and selection policies in
  `run_artifacts_metadata()`

Limitations:

- factor detection is token-pattern based, not AST-based
- there is no LLM causal scratchpad, abductive factor creation, or
  surprise-pattern inspection
- when no factor matches, it falls back to the deterministic first configured
  factor (`loop_structure`)
- reward uses selected-parent baseline metadata when the evolve loop provides
  it, but it is still not a causal counterfactual baseline; legacy direct calls
  without baseline metadata fall back to previous plugin history or zero

### `deep_research`

Implemented by
[`libreevolve/plugins/deep_research.py`](../libreevolve/plugins/deep_research.py).

Purpose (DeepEvolve-inspired, not paper-complete):

- periodically fetch external research context and add it to prompts

Mechanics:

- default search uses the public arXiv Atom API
- `on_generation_start()` runs on completed-generation counts starting at `1`;
  it searches on generation `1`, then every `search_every` generations after
  that
- `search_every` must be a positive integer; invalid constructor values fail
  before hook execution
- `max_events` defaults to `100` and bounds the plugin's in-memory retrieval
  event history; invalid values fail before hook execution
- `retrieval_body_retention_mode` defaults to `redacted` and controls
  persisted retrieval body text in provider-result snapshots and cache
  synthesis snapshots. Accepted values are `full`, `redacted`, `hash_only`,
  and `off`. Prompt-visible retrieval synthesis remains secret-redacted and
  bounded before injection; this setting controls only persisted event/cache
  bodies and sidecar hashes.
- the default query is derived from the current best fitness, manifest-safe
  metrics, bounded candidate code/file terms, bounded task-description terms,
  bounded explicit-context terms, bounded recent failure-history terms, and
  bounded local paper manifest title/id terms. Later queries can also use
  bounded terms from recent captured proposal hypotheses.
- `build_extra_context()` injects the active successful synthesis into the
  prompt; an eligible empty or error refresh clears that prompt context instead
  of silently reusing older retrieval text

Extension point:

- pass a custom `search_fn(query) -> str | dict | None` to replace arXiv with
  another provider; dict results can include bounded provenance fields such as
  `status`, `provider`, `query_url`, `sources`, `synthesis`, and provider-error
  metadata. Raw `query_url` values are converted to `request_url` summaries
  with scheme, host, path, query-parameter count, URL hashes, and an omitted raw
  URL. String and arbitrary-object returns are treated as untrusted synthesis
  text; they are redacted and bounded before prompt injection, and prompt
  headers label the provider/source kind.

Operational note:

- network failures are swallowed and only affect plugin context, not the run
- non-finite or nonnumeric best-program fitness skips retrieval and records a
  `skipped` event with `skip_reason: non_finite_best_fitness`, without calling
  the provider or persisting a non-finite `best_fitness`
- candidate metadata records provider/query/status/timestamp/result-length,
  synthesis-hash, best-program context, query policy, query input summary,
  bounded/redacted source IDs/URLs/titles/authors/timestamps/excerpts, source
  metadata retention/redaction counters, summary hashes, redacted/bounded
  provider errors, and structured error types when available.
  The default query policy combines best-program fitness, manifest-safe metric
  names, bounded code/file identifier terms, bounded task-description terms,
  bounded explicit-context terms, bounded recent failure-history terms, and
  bounded local paper manifest title/id terms. Later queries can also use
  bounded terms from recent captured proposal hypotheses. Request
  URL metadata is stored as a redacted/hash-backed `request_url` summary, not a
  raw URL. Direct arXiv
  helper calls validate non-empty safe query text and bounded integer
  `max_results` values before constructing provider URLs, and the default
  arXiv URL uses HTTPS. Live arXiv responses are read with a
  1,000,000-byte cap before XML parsing; exact-limit payloads are allowed, and
  oversized payloads become structured `oversized_response` retrieval errors
  without entering prompt context. Live responses record transport status plus
  payload limit/observed-byte/hash metadata. Retrieval events with a query also
  include `libreevolve.retrieval_transport_policy.v1`, which classifies HTTPS
  request status, redirects, HTTP status class, payload hash presence,
  oversized responses, missing custom-provider transport, and TLS/certificate
  failure-looking errors as audit-grade, degraded, or unauditable. Successful
  retrieval text is rendered as untrusted evidence with explicit begin/end
  delimiters and a prompt note that retrieved text is non-authoritative;
  retrieval metadata records `trust_policy`, `prompt_boundary`, and
  `authoritative: false`.
  Retained source metadata records one-based retained rank, original provider
  rank, a `retained_source_integrity_v1` policy, identity/content hashes,
  redacted URL transport expectations, bounded/redacted
  `libreevolve.retrieval_source_content_snapshot.v1` snapshots when source
  summary/content text is available, `query_term_overlap_audit_v1` relevance
  scores, `libreevolve.retrieval_source_content_trust_policy.v1` classifications
  for each retained source, and an aggregate source-ranking hash that links
  retained source order to the prompt-visible synthesis hash. The default
  `source_ranking_policy="provider_order_retained_v1"` keeps provider order and
  records query-overlap relevance as audit-only evidence. Direct construction or
  config can set `source_ranking_policy="query_overlap_score_desc_v1"` to rank
  retained sources by deterministic query-overlap score with provider rank as a
  tie-breaker; events, active prompt context, and cache snapshots record that
  relevance affected ordering.
  Successful synthesis metadata includes raw result length/hash plus
  redaction/truncation flags. When a synthesis is active, prompt-context
  metadata also records `active_context` using
  `libreevolve.deep_research_active_context.v1`, with the source generation and
  event index, synthesis and raw-result hashes, result source kind, query hash,
  cache snapshot fields, retained-source ranking hash fields, trust policy, and
  transport-policy status for the exact retrieval text injected into the
  prompt.
  `retrieval_retention` records the configured limit, retained/emitted counts,
  total events, dropped-event count, and `retrieval_body_retention_mode`.
- cache behavior defaults to `cache_mode="cached"`: identical query/provider
  snapshots are reused within the plugin instance; direct construction can use
  `cache_mode="live"` to always call the provider or `cache_mode="offline"` to
  use cache-only replay. When `cache_dir` is configured, snapshots are stored
  as JSON files; the CLI wires built-in `deep_research` to
  `plugin_artifacts/deep_research/`.
- completed run manifests include bounded retrieval summaries with cache mode,
  key, hit/miss, source, staleness fields, and snapshot hashes
- when `cache_dir` is configured, `run_artifacts_metadata()` reports
  DeepResearch cache snapshots as plugin artifact metadata, including snapshot
  count, retained count, skipped/read-error counts, file names, byte counts,
  per-file hashes, retention cap, provider-result snapshot counts/hashes, and
  an aggregate hash; the CLI configures this under
  `plugin_artifacts/deep_research/`
- when `cache_dir` is configured and `retrieval_body_retention_mode` allows
  payload text, live retrieval writes
  `libreevolve.retrieval_payload_artifact.v1` sidecars under
  `payload_artifacts/` for the full secret-redacted provider payload and any
  retained source-content payloads that fit the 64,000-byte per-artifact budget.
  Oversized payloads are written as metadata-only omitted artifacts. Retrieval
  events, cache snapshots, source rows, and plugin artifact metadata link these
  sidecars by relative path and SHA-256. `hash_only` and `off` suppress payload
  sidecars and record that suppression in `payload_artifact_policy`.
- retained source trust policy records classify content evidence as verified
  redacted payload artifacts, metadata-only oversized payload artifacts, bounded
  content snapshots, hash-only evidence, or no content evidence. Event-level
  `source_content_trust_policy` records source counts, replayable evidence
  counts, mismatch counts, and a records hash. Transport-policy limitations
  distinguish missing semantic content evidence from bounded redacted replay
  evidence, but neither classification proves semantic correctness.
- query events include `libreevolve.retrieval_evidence_boundary_policy.v1`,
  which explicitly records the opt-out boundary for raw provider/source payload
  retention, TLS certificate-chain retention, and semantic verification. The
  policy links the current payload-artifact, source-content, and transport
  evidence states so cache snapshots can replay what was retained versus what
  remains outside the audit boundary.
- retrieval events and cache snapshots retain configurable
  `libreevolve.retrieval_provider_result_snapshot.v1` provider-result
  snapshots with raw and stored hashes, original/stored character counts, and
  redaction/truncation flags when the selected retention mode allows hashes or
  text. Cache snapshots also record `synthesis_retention`; `hash_only` and
  `off` suppress cached synthesis text, so cache-only replay cannot recover
  prompt-visible retrieval text from those snapshots.
- unbounded raw provider/source payload persistence and unbounded
  source-content artifacts are not implemented yet
- retrieval provenance is still best-effort: redirect, transport, payload, and
  TLS/certificate-looking failures are classified in event metadata, but there
  is no replayable TLS/certificate decision tree, bounded payload snapshots and
  boundary-policy records do not replace unbounded raw provider payload
  artifacts, and semantic source meaning plus learned or externally scored
  semantic ranking beyond deterministic query-overlap ranking remain unverified
- this does not implement a DeepEvolve-style cross-file debugging/editing loop,
  systematic debugging, or hypothesis refinement loops

### `modular`

Implemented by
[`libreevolve/plugins/modular.py`](../libreevolve/plugins/modular.py).

Purpose (ImprovEvolve-inspired, not paper-complete):

- bias the model toward a modular decomposition style inspired by
  ImprovEvolve

Mechanics:

- always injects the same static prompt block
- does not inspect the current parent, archive, or score
- does not alter evaluation or logging
- does not enforce or execute generate/improve/perturb interfaces
- candidate metadata records the rendered per-plugin prompt-context text and
  hash; prompt-context metadata labels the policy as `static_prompt_only`,
  records `operation_selected: static_modular_guidance`, lists the described
  `generate_config`/`improve`/`perturb` operations, and records
  `operation_executed: false` plus `interface_enforced: false`

### `ttt_rl`

Implemented by
[`libreevolve/plugins/ttt_rl.py`](../libreevolve/plugins/ttt_rl.py).

Purpose (ThetaEvolve-inspired, not paper-complete):

- accumulate `(prompt, response, raw_score, reward)` training examples for
  future RL or GRPO-style fine-tuning

Mechanics:

- records data in `on_evaluated()` when prompt and diff metadata are present
- requires both metadata fields to be non-empty strings before queueing; invalid
  prompt/response examples are skipped and counted as malformed examples
- requires finite non-boolean numeric scores before queueing; accepted
  `raw_score` and clipped `reward` values are stored as floats, while invalid
  scores are counted as `invalid_score` and raise before queueing, leaving
  later valid examples exportable
- every `train_every` generations, writes pending examples since the previous
  successful export to `grpo_data.jsonl`
- when constructed with an existing `grpo_data.jsonl`, counts valid existing
  export rows for artifact metadata and appends only new rows after them
- run-artifact metadata collection flushes any remaining pending examples, so
  short completed runs still get durable export rows before manifest summary
- `max_retained_examples` defaults to `500`; when pending in-memory examples
  exceed that cap, the plugin exports the pending overflow immediately and then
  prunes already exported records from memory
- generation-hook arguments are completed-generation counts starting at `1`, so
  `train_every=1` exports after the first completed mutation generation
- `train_every` must be a positive integer; invalid constructor values fail
  before hook execution
- `max_retained_examples` must also be a positive integer
- stores `raw_score` plus `reward = max(0.0, raw_score)`, so negative scores
  are clipped to zero rather than exported as penalties

Operational note:

- when loaded by the CLI, output is scoped under
  `runs/<run-name>/plugin_artifacts/ttt_rl/`
- direct in-code `TTTRLPlugin(log_dir=...)` construction is user-managed and
  can intentionally write outside a run directory; use the manifest
  `log_dir`/`path` metadata as provenance for those external artifacts
- prompt and response payloads are secret-redacted and capped by per-field and
  combined prompt/response character budgets before queueing
- completed manifests include queued, retained, pending, exported, and
  dropped-retained counts, restored export counts, invalid restored-line
  counts, malformed-example counts/reasons, the retention cap, payload
  policy/caps/counters, finalization policy, restore policy, path, byte count,
  hash, and reward policy in
  `runtime.plugin_artifacts[].metadata`
- `_maybe_train()` is currently just a JSONL writer, not an actual trainer; the
  restored export metadata is replay/artifact continuity, not a model or
  optimizer checkpoint

## Adding a custom plugin

The current registry resolves built-in plugin names and structured built-in
specs from [`libreevolve/plugins/registry.py`](../libreevolve/plugins/registry.py).
To add another built-in plugin, add it to that registry with an explicit option
schema. CLI startup validates configured plugin names and options before
run-directory overwrite cleanup. Configured plugin labels must match
`[A-Za-z0-9][A-Za-z0-9_.-]{0,127}` and must not match the shared secret
redaction patterns; the manifest writer revalidates the same policy before
persisting `config.plugins`.

External packages can expose a `PluginBase` subclass through the
`libreevolve.plugins` Python entry-point group and configure it with:

```yaml
plugins:
  - name: entry_point
    options:
      group: libreevolve.plugins
      name: my_plugin
      paper_inspiration: AlphaEvolveExtension
      constructor_options:
        mode: audit
        limit: 5
```

Entry-point specs are validated before run-directory overwrite cleanup, the
target must load a `PluginBase` subclass, and optional
`constructor_options` are manifest-safe JSON keyword arguments passed to the
plugin constructor. External plugin classes can additionally publish a
`libreevolve_constructor_option_schema` class attribute to reject unknown or
malformed constructor options before plugin instantiation:

```python
class LoggingPlugin(PluginBase):
    libreevolve_constructor_option_schema = {
        "mode": {"type": "enum", "values": ["audit", "dry_run"]},
        "limit": {"type": "positive_int"},
    }
```

Supported declared schema types are `bool`/`boolean`, `enum`, `int`/`integer`,
`manifest_safe_json`, `nonnegative_int`, `number`, `path`, `plugin_label`,
`positive_int`, and `string`; add `required: true` to require an option.
Runtime manifests record the entry-point group/name/value, distribution
name/version plus hashes when available, configured `paper_inspiration`,
captured constructor options, the constructor option policy/schema when
declared, and hash-only distribution `RECORD` / `WHEEL` summaries when
available. Package-registry policy beyond entry-point distribution metadata
remains future work.

Minimal example:

```python
from libreevolve.plugins.base import PluginBase

class LoggingPlugin(PluginBase):
    def on_generation_end(self, gen, best):
        if best is not None:
            print(f"gen={gen} best={best.fitness:.4f}")
```

Runtime manifests record built-in loaded-plugin constructor snapshots under
`runtime.plugin_state.loaded_specs`. This covers the current built-in plugin
classes, records entry-point provenance plus manifest-safe or declared-schema
constructor options for configured external plugins, and records signature-only
constructor shape for custom direct plugins; it does not capture arbitrary
direct-plugin constructor values or instance state. Non-built-in loaded specs
also include `libreevolve.direct_plugin_policy.v1`, making the constructor
value, constructor schema, instance-attribute, package-scope, and paper-scope
policy explicit for entry-point versus direct-instance plugins. Loaded plugin
identities also
include sanitized `version` records sourced from plugin instance, class, or
module `__version__` attributes when present. If you need new constructor
arguments, you will also need to update the CLI or add a problem-local
configuration convention for that plugin.
