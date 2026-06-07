# Run Artifacts

LibreEvolve writes machine-readable run outputs under `runs/` by default.
Run JSON and JSONL writers use strict finite JSON. Candidate history, prompt
history, manifests, and the ThetaEvolve-inspired export reject `NaN`/`Infinity`,
non-string JSON object keys, tuple values, cyclic records, and
non-JSON-compatible values rather than emitting permissive Python JSON tokens or
silently normalizing Python tuples into JSON arrays. Failed candidate, prompt,
and GRPO append attempts write diagnostic quarantine records. Quarantine
records preserve the bounded, secret-redacted serialization error and include a
bounded, secret-redacted record representation, even when the malformed
record's `repr()` raises. Failure-history append failures use the separate
`failure_history_invalid.jsonl` quarantine. Manifest writes serialize first,
create missing parent directories, fsync the temporary file, atomically replace
the previous file, and then attempt a best-effort parent-directory fsync.
JSONL and quarantine append helpers also create missing parent directories
after strict serialization succeeds. If an intended parent path cannot be
prepared, the writers raise a bounded, secret-redacted `StrictJsonlError`
instead of surfacing raw filesystem exceptions. If parent-directory sync is not
supported by the platform/filesystem, the replacement remains strict and
process-visible atomic but is not a fully proven machine-crash-durable
transaction. Rejected runtime manifest updates keep the last valid manifest and
write diagnostics to `manifest_invalid.jsonl`; if the current manifest is
already malformed, empty, non-UTF-8, or otherwise unreadable during a runtime
update, LibreEvolve appends an unreadable-current-manifest diagnostic and
rewrites from the in-memory startup manifest plus the runtime payload when that
replacement payload is valid.
JSONL streams use a local complete-line durability policy. Accepted rows are
strict-serialized before append, written as newline-terminated records, flushed,
and fsynced before the append helper returns. Before appending to an existing
managed stream, LibreEvolve treats a non-empty final fragment without a
terminating newline as a torn prior append, truncates it back to the previous
complete line, and writes a bounded diagnostic with fragment byte count/hash to
the paired `*_invalid.jsonl` stream or to the same quarantine stream when the
stream repairs itself. Earlier complete lines remain the trustworthy recovery
unit after an interrupted process or host crash. The streams still do not use
temporary append spool files or line checksums on every record. Archive cell
and elite snapshots are restored through manifest/history bundles rather than
through a general checkpoint/replay engine; ordered migration replay,
controller queues, and full-run resume remain broader checkpointing concerns.
Rejected archive-admission metadata is kept JSON-safe, including non-finite
selection scores, but it does not sanitize hook-mutated/restored top-level
candidate `fitness` or metric values for accepted history. Passing such a
rejected candidate to `ProgramDatabase.log()` fails strict history validation
and writes bounded diagnostics to `history_invalid.jsonl`; use those invalid
streams for diagnosis until a dedicated finite rejected-candidate persistence
policy exists.
LLM ensemble call telemetry is attached to candidate history and prompt
history records for the calls involved in those records, and config-created
ensembles append run-scoped call/reward events to `llm_calls.jsonl`. The live
`LLMEnsemble.call_history` accessor is still a bounded in-memory retained
window controlled by `llm_call_history_max` and exposes retained/total/dropped
counts through `call_history_retention`; the durable stream is the source for
complete call accounting. `load_llm_call_ledger()` validates durable
`llm_calls.jsonl` rows for call sequence continuity, duplicate call ids, reward
rows linked to known successful calls, backend consistency, and scheduler
counter shape, including safe backend name/API-mode/request-parameter
telemetry, before returning replay metadata with derived role accounting and
provider-failure policy summaries. Full async worker and
scheduler-state resume remain future work. Final manifests also record
`runtime.llm_scheduler`: `snapshot` for real `LLMEnsemble` state,
`not_initialized` for runs that never constructed a mutation LLM, `unavailable`
for custom objects without a scheduler-state API, or `invalid` if the exposed
state is not finite JSON or cannot be validated by the `LLMEnsemble` restore
contract. Snapshot state includes backend counts, wins, total reward-accounted
pulls, rewarded/unrewarded successful call ids, and call-history retention
diagnostics. Backend metadata `role` can now scope live selection for matching
LLM call roles; per-call `scheduler_policy.selection_scope` records
`role_scoped_backend_bandit` when that routing lane is active and
`global_backend_bandit` when no backend metadata role matches. This is a
reproducibility/audit record, not a full resume
checkpoint. LLM call `id` values are deterministic for matching ordered call
streams because they are derived from per-run call sequence,
backend/role/attempt coordinates, and prompt hashes. Repeated calls inside one
stream remain distinct. Broader run-resume boundaries and provider
nondeterminism remain separate replay gaps.

Final manifests also record `runtime.rng`, a `python.random.mt19937.v1`
snapshot of LibreEvolve's run-local `random.Random` instance. The record stores
the configured seed, the JSON-safe `getstate()` payload, a SHA-256 hash over the
canonical state payload, and the restore entrypoint
`random.Random.setstate`. This captures framework-owned stochastic state for
audit and future resume work. `load_runtime_rng_state_snapshot()` validates and
loads the field from `manifest.json`, and `restore_runtime_rng_state_snapshot()`
returns a `random.Random` only after schema/hash/restorability checks.
Direct callers can pass a validated snapshot back into
`evolve(..., runtime_rng_state_snapshot=...)`; the snapshot seed must match
`Config.seed`, and the final manifest records whether the run was seeded fresh
or restored from a prior snapshot. CLI runs can load the same checked snapshot
with `--restore-rng-from-manifest`. The snapshot also records
`replay_boundary` with schema
`libreevolve.runtime_rng_replay_boundary.v1`; it identifies framework-owned
surfaces covered by restore and explicitly marks LLM provider outputs, plugin
internal randomness, and validator subprocess randomness as outside this RNG
restore contract.
The compact archive cursor/counter snapshot can be loaded separately with
`evolve(..., runtime_archive_state_snapshot=...)` or
`--restore-archive-cursor-from-manifest`; that path restores only island
assignment counters, not MAP-Elites cells, elite lists, controller state, or
provider/plugin randomness. Full archive restore passes the same archive state
plus checked `Program` snapshots reconstructed from accepted `history.jsonl`
rows: direct callers can pass `runtime_archive_programs_by_id`, and CLI runs
can use `--restore-archive-from-manifest` to load a previous `manifest.json`
with its sibling `history.jsonl`. Migration-event replay and controller queues
remain future resume work.

## Directory layout

For a run named `hello_world`:

```text
runs/
└── hello_world/
    ├── manifest.json
    ├── history.jsonl
    ├── failure_history.jsonl
    ├── archive_events.jsonl          # Migration placement events when migration runs
    ├── controller_budget_events.jsonl # Replayable synchronous controller budget events
    ├── history_invalid.jsonl          # Only when a candidate record is rejected
    ├── failure_history_invalid.jsonl  # Only when a failure record is rejected
    ├── archive_events_invalid.jsonl   # Only when an archive event is rejected
    ├── controller_budget_events_invalid.jsonl # Only when a budget event is rejected
    ├── llm_calls.jsonl
    ├── llm_calls_invalid.jsonl        # Only when an LLM call record is rejected
    ├── manifest_invalid.jsonl         # Only when a runtime manifest update is rejected
    ├── prompt_history.jsonl
    ├── prompt_history_invalid.jsonl   # Only when a prompt record is rejected
    ├── best.py
    ├── evaluator_artifacts/
    │   └── ...                        # Optional collected validator outputs
    ├── plugin_artifacts/
    │   └── ttt_rl/
    │       ├── grpo_data.jsonl         # Only when ttt_rl exports examples
    │       └── grpo_data_invalid.jsonl # Only when an export record is rejected
    └── best_workspace/
        ├── .libreevolve_static_files.json # Only when static candidate sidecars exist
        └── ...                        # Complete best candidate file set
```

The run subdirectory name comes from `--run-name`, if provided, otherwise from
the loaded problem directory name. Run names are validated as single portable
path components, not nested or parent-relative paths, and reject
Windows-reserved device names, leading/trailing whitespace, trailing dots,
invalid filename characters, control characters, non-NFC Unicode spellings,
and Unicode format controls such as right-to-left override and zero-width
joiner. Secret-like assignment strings and provider-token-shaped values are
also rejected before filesystem or manifest writes. LibreEvolve resolves the
final run directory before cleanup or writes and rejects it if it resolves
outside the resolved `log_dir`; symlink or junction run directories that escape
the log root are rejected.

`best_workspace/` materializes the best candidate's UTF-8 text members. When a
candidate also carries typed static sidecar metadata, LibreEvolve writes
`best_workspace/.libreevolve_static_files.json` with the static member path,
kind, byte count, SHA-256, source kind/path when available, and mutation
policy. Static records with bounded `content_b64` are also written as raw files
at their declared candidate paths. Static records with `source_copy_path` are
copied only after link checks plus byte-count and SHA-256 verification.
Metadata-only static records remain manifest-only and are not copied as bytes.

## `manifest.json`

`manifest.json` captures the effective run settings used by
[`ProgramDatabase`](../libreevolve/core/database.py), including:

- problem name
- generation and population settings
- run budget limits: `max_generations`, optional `max_evaluations`,
  `max_evaluator_seconds`, detailed evaluator counter limits, and
  `max_runtime_seconds`
- mutation mode
- evaluator stage config
- parent and inspiration sampling strategies
- prompt variants, meta-prompt settings, critique settings, and LLM feedback
  grader specs, plus redacted/hash-backed `llm_prompt_roles` structured
  system/developer instruction policy when configured
- backend specs
- OpenAI API routing policy under `policies.openai_api_mode`, including each
  OpenAI backend's configured `api_mode`, effective Chat Completions or
  Responses route, and whether `reasoning_effort` triggered the legacy `auto`
  policy
- provider capability lookup policy under
  `policies.provider_capability_lookup`, which records local static validation
  and explicitly states that live provider model registries, service/API
  versions, and account availability are not queried before the run
- shared redaction grammar under `policies.redaction`, including the
  versioned rule ids used by `redact_sensitive_text()`
- ensemble strategy
- LLM retry/fallback controls, accepted-response size cap, and retained
  in-memory call-history cap, including the total original/retry/fallback
  attempt cap for each logical ensemble call
- plugins
- problem context-source provenance, including selected safe relative paths,
  source hashes, extraction status, excerpt spans, PDF document page ranges,
  and rendered-excerpt PDF page spans when available; prompt headers render
  exact `page:start-end` spans when present and exact non-contiguous page lists
  when only `excerpt_pages` is available. Secret-like context source labels and
  skipped context diagnostic labels are rejected before they can enter
  manifests. Selected hidden context sources are marked with `hidden: true`.
- problem context-selection policy, including the active `context.yaml` /
  `context.yml` file hash when present, effective include/exclude patterns,
  per-source character budget, source-byte/total-byte/PDF extraction limits,
  context entry/depth/skipped-diagnostic/provenance limits, hidden-source
  policy, selected/skipped counts, usable/failed extraction counts, retained
  skipped-record counts, skipped-record truncation/omission metadata, and
  diagnostics for unsupported, not-included, hidden-not-included, over-budget,
  extraction-failed, no-text, excluded, max-entry, or max-depth context files.
  Context include/exclude patterns are path-segment-aware globs: `*` stays
  within one `/`-separated path component and `**` is recursive. Secret-like
  include/exclude pattern labels are rejected before policy persistence.
- evaluator entrypoint provenance, including problem-relative redacted path
  labels, path hashes, streamed SHA-256 source hashes, byte counts, read-error
  status when source hashing fails, stage usage metadata, and bounded sibling
  helper/data companion snapshots under each evaluator directory
- problem objective-schema provenance under `problem.objective_schema`,
  including normalized metric names, directions, bounds, weights, source labels,
  effective primary flags, `primary_metric`, `primary_bounds`, and
  `metric_count`. Direct
  database construction validates this schema before writing startup manifests;
  missing, boolean-bound, unsafe, or inconsistent schemas fail before run
  artifacts are created.
- CLI-loaded problem-local config provenance under `provenance.config`.
  `config.yaml` must be absent or a regular file, not a symlink, Windows
  junction, or directory. Present config files record `path: config.yaml`,
  `status: ok`, `sha256`, and `bytes`; absent config files record
  `status: absent`. Setup YAML rejects duplicate keys plus anchors/aliases
  before config, metric, or context records become effective run provenance.
- CLI `run` dotenv provenance under `provenance.dotenv` when the command was
  used. The record includes load status, `override=True` policy, load phase,
  source hash/byte count, and key names without values. CLI module import and
  `libreevolve show` do not load `.env`.
- run provenance, including Git `HEAD` and dirty status resolved from the
  hashed `libreevolve/` source tree when available, source-tree hashes for
  `libreevolve/`, problem-tree hashes, and plugin module file hashes. Dirty Git
  status records include `status_entry_count`, secret-redacted
  `status_entries`, SHA-256 `status_entry_hashes` for the original porcelain
  lines, `status_entries_redacted`, and
  `status_entries_unsafe_chars_redacted` when Unicode format controls were
  escaped; runtime environment provenance with
  Python/platform metadata,
  `pyproject.toml` status/hash when present, selected package metadata
  (`project.name`, `project.version`, `project.requires-python`, license,
  authors/maintainers, keywords, classifiers, project URLs, optional
  dependency groups, scripts, and arbitrary entry-point groups), build backend
  metadata, installed versions for declared runtime dependencies, bounded
  `installed_packages` name/version snapshots for
  installed distributions, NumPy numerical-runtime config hash/preview
  metadata, and known project-root lockfile hashes.
  Dependency records
  include secret-redacted and Unicode-control-escaped specs, `spec_hash` when
  the visible spec changes, safe names, `name_hash`, `name_redacted`, and
  installed-version lookup labels; redacted dependency names suppress raw
  installed-version lookup and retain only redacted/hash-backed lookup identity.
  Package/build metadata fields from `[project]` and `[build-system]` include
  `name`, `version`, `requires-python`, license, authors/maintainers,
  keywords, classifiers, project URLs, optional dependency groups, scripts,
  arbitrary entry-point groups, `build-backend`, and `build-system` `requires`,
  and are bounded/redacted strings. Unselected or unknown `[project]` keys are
  retained under bounded/redacted/hash-backed `extra_project_metadata` records.
  Secret-like text and Unicode format controls are redacted or escaped with
  hash-backed raw identity fields such as `name_hash`,
  `version_hash`, `requires_python_hash`, and `build_backend_hash`. Redacted
  package names suppress raw installed-version lookup.
  Malformed or non-UTF-8 `pyproject.toml` files are recorded as degraded package provenance with
  `package.pyproject.status: invalid_toml` or `invalid_encoding` plus the file
  hash and byte count. Syntactically valid files with invalid dependency or
  build-system requirement schemas are recorded as
  `package.pyproject.status: invalid_pyproject_schema` with bounded path-aware
  diagnostics rather than normal dependency rows. Pyproject read, decode, and
  parse error text is secret-redacted and bounded before manifest persistence.
  Missing `pyproject.toml` files are recorded as
  `package.pyproject.status: missing` with `path: pyproject.toml`; package
  metadata and dependency records are omitted, and `installed_version_name`
  records the fallback package name used for installed-version lookup.
  `policies.redaction` records the active shared redaction grammar. The current
  grammar is `libreevolve.redaction.v2`, an ordered regex substitution policy
  covering PEM private-key blocks, assignment values for keys containing
  `api_key`, `token`, `secret`, or `password`, `Authorization: Bearer` header
  values, URL userinfo passwords, standalone OpenAI/GitHub/GitLab/Hugging Face/
  Slack-like provider token prefixes, and AWS `AKIA`/`ASIA` access-key ids.
  This policy is a bounded credential-pattern scanner, not a semantic secret
  detector. It applies only on artifact, diagnostic, prompt/config, metadata,
  or display surfaces that explicitly call the shared helper; binary artifacts
  and surfaces documented as raw remain outside this redaction guarantee.
  Source/problem tree provenance skips symlinks and Windows junctions instead
  of following them. Skipped link records include
  `reason: link_not_followed`, `is_symlink`, `is_junction`,
  `target_path_redacted`, hash-backed symlink target identity when available,
  hash-backed resolved target identity when resolvable, `target_scope`, and
  `target_within_root`; unresolved targets record redacted resolution
  diagnostics instead of raw target paths.
- seed-source and log directory retention metadata. Loaded seeds record safe
  relative `initial_programs/...` source paths, source kind, seed index,
  primary file, file count, file list, and any
  `allowed_reserved_paths` under `problem.seed_sources`; loaded seed source
  labels that look like secrets are rejected before they can be persisted.
  `problem.seed_policy` records the problem-local hidden/cache seed policy,
  including `seed_policy.yaml` include/exclude patterns when configured.
  Skipped top-level hidden/cache seed entries, unsupported top-level seed
  files, empty directories, hidden/cache workspace paths, seed-policy excluded
  paths, and directories whose files are all skipped are recorded under
  `problem.seed_skipped` with redacted path labels and reasons. Seed workspace
  directories with visible files but no `.py` primary file are skipped with
  `reason: no_python_seed_primary`, keeping loaded seed workspaces
  Python-primary under the current candidate model. Direct in-memory
  `Problem(...)` seeds use `seed_source_kind: inline` plus `seed_index`; when
  `initial_workspaces` is empty, direct
  `initial_programs` is preflighted as a list of UTF-8 text seeds bounded to
  1000000 characters with valid evolve-block markers before manifest or
  history writes. Direct `initial_workspaces`, when present, is preflighted as
  a list of `CandidateWorkspace` objects or workspace record mappings; entries
  are normalized and rechecked for safe paths, UTF-8 text, primary-file
  presence, and valid evolve-block markers before manifest or history writes.
  Valid evolve-block markers are currently limited to `.py` candidate files
  using Python `# EVOLVE-BLOCK-*` comments; marker-like declarations in
  non-`.py` workspace files fail with
  `unsupported_evolve_block_marker_syntax` instead of being treated as
  unmarked full-file candidates.
  Direct `initial_workspace_sources` records are schema-validated for allowed
  fields, seed-index consistency, safe path labels, file-list shape, and
  file-count consistency before manifest or history writes. History rows carry
  `workspace_path_policy.allowed_reserved_paths` when a seed policy explicitly
  permits dot-prefixed or `__pycache__` candidate paths; generated mutations
  still cannot create arbitrary reserved paths outside that allowlist. Safe
  relative `log_dir` values such as `runs/` are recorded as
  configured. Absolute log roots are recorded as
  `<absolute-log-dir>` plus `config.log_dir_metadata` containing SHA-256,
  absolute/relative status, redaction status, and retention reason, so
  manifests do not expose private local output paths.
- run id and run-directory collision policy
- validator environment allowlist configuration, canonicalized to
  manifest-safe uppercase names

Current artifacts are explicitly marked as local v1 machine-readable formats.
`manifest.json` carries top-level `schema_version` and `artifact_schema`
fields, and current `history.jsonl`, `failure_history.jsonl`,
`archive_events.jsonl`, `llm_calls.jsonl`, and `prompt_history.jsonl` rows
carry `schema_version` plus `record_schema`. Missing schema markers are treated as legacy v0 rows by
`show`, accepted-history restore helpers, and the LLM call-ledger reader where
those readers have legacy compatibility paths. True migration and full resume
branching by schema remain open work.

Prompt-bearing configuration is retained as redacted, bounded effective config
plus provenance metadata. `manifest.json.config.prompt_variants`,
`manifest.json.config.prompt_format_options`,
`manifest.json.config.critique_prompt`, and
`manifest.json.config.llm_feedback[].prompt` redact known credential-shaped
strings and truncate oversized values before manifest persistence. Parallel
metadata fields, such as `prompt_variants_metadata`,
`prompt_format_options_metadata`, `critique_prompt_metadata`, and
`llm_feedback_metadata`, record SHA-256 of the original text, original length,
retained length, redaction, and truncation flags. The active policy is recorded
under `manifest.json.policies.prompt_config_retention`.
`manifest.json.policies.prompt_data_retention` records the broader
prompt/response retention boundary with schema
`libreevolve.prompt_data_retention.v1`: mutation prompt retention is
configurable, critique prompt/mutation text, feedback fields, successful LLM
output text, provider error text, plugin context text, and meta-prompt
evidence are configurable surfaces. DeepResearch retrieval bodies are
plugin-configurable through `retrieval_body_retention_mode`, with selected
values recorded in `runtime.plugin_state.loaded_specs`. LLM call prompt text
is hash/count-only telemetry. Framework-owned quarantine record snapshots are
controlled by `quarantine_snapshot_retention_mode`.

This is a reproducibility aid. It is not yet a full resume checkpoint.
Source tree hashes exclude `.git`, `runs/`, `__pycache__`, and local test/cache
directories. Problem tree hashes exclude `.git` and cache directories, and they
also classify generated run-artifact directories under `runs/` separately from
ordinary problem fixtures. A directory under `runs/` that contains known
LibreEvolve run-artifact markers such as `manifest.json`, `history.jsonl`,
`prompt_history.jsonl`, `best.py`, or `best_workspace/` is recorded in
`skipped` with `reason: generated_run_artifacts` and excluded from the problem
tree hash; ordinary fixture files such as `runs/fixture.txt` remain included.
If the active generated run directory resolves inside the problem tree, that
exact run root is recorded in `skipped` with `reason: excluded_output_root` and
excluded from the problem tree hash. Direct `problem_provenance()` callers may
pass absolute generated roots or problem-relative generated roots; relative
generated roots are resolved from the problem root, not the process cwd. The
main evolution loop passes its effective run directory as an absolute root.
`generated_run_artifact_markers` records the exact marker names used by this
classification policy, and those marker names are included in the provenance
policy hash.
Source/problem tree provenance stores root identity as a local label
(`root: <libreevolve-root>` or `root: <problem-root>`) plus `root_scope:
local_root_label`, `root_hash`, and `root_redacted`; it does not persist raw
absolute source or problem roots. Git provenance uses the same pattern with
`root: <git-root>` and a hash of the raw Git top-level path.
Linked files or directories are also recorded in
`skipped` and excluded with `reason: link_not_followed`, symlink/junction
flags, redacted/hash-backed target identity, target resolution status,
`target_scope`, and `target_within_root` when resolvable. Source/problem file
records use NFC-normalized relative display paths; if the host filesystem
spelling differs, records include `filesystem_path`, `filesystem_path_hash`,
`path_normalization: NFC`, and `path_normalized: true`. Duplicate included file
paths after Unicode normalization or unsafe-character escaping are rejected
before manifest writing. Unicode format controls in included and skipped path
labels are escaped as `[U+....]`, backed by `filesystem_path_hash`, and marked
with `path_unsafe_chars_redacted`. Plugin
provenance hashes the Python module file for each plugin instance. Built-in/project plugin
paths are stored relative to the project root with `path_scope:
project_relative`; external plugin paths store only `<external>/<filename>`
with `path_scope: external_file_name`. All file-backed plugin records include
`path_hash` for the raw resolved path and `path_redacted` to show whether the
raw absolute path was omitted. Plugin path labels also escape Unicode format
controls and set `path_unsafe_chars_redacted` when the visible path label was
changed. They also include `max_file_bytes`; over-limit
plugin module files are recorded with `status: skipped_max_file_bytes` and
read failures with `status: read_error` plus redacted diagnostics. Constructor
arguments, validated plugin config schemas, emitted plugin artifacts, and
provider-side retrieval context are still separate gaps. Git provenance is
looked up from the same source root used for the `libreevolve/` tree hash, so
launching the CLI from another directory does not by itself make source Git
metadata unavailable. Dirty Git status path strings are redacted for common
secret patterns before persistence, while `status_entry_hashes` keep a stable
comparison signal for the original raw porcelain lines. Unicode format controls
in dirty status entries are escaped before persistence and reported through
`status_entries_unsafe_chars_redacted`. Source/problem tree
paths and skipped paths use the same secret-pattern redaction policy: ordinary
relative paths remain visible, but secret-like path text is redacted and paired
with `path_hash` plus `path_redacted`. `tree_hash` is explicitly scoped to
included file records and carries `tree_hash_scope: included_files`; skipped
diagnostic records are hashed separately in `skipped_hash` with
`skipped_hash_scope: skipped_diagnostic_records_v2`. `provenance_hash`
combines the included-file digest, skipped-diagnostics digest, and
exclusion-directory policy under `provenance_hash_scope:
included_files_and_skipped_diagnostics_v2` without hashing excluded file
contents. Regular source/problem files larger than `max_file_bytes` are skipped
before reading with `reason: max_file_bytes`, `bytes`, and `max_bytes`.
Read failures are recorded as skipped diagnostics with `reason: read_error`
and redacted error text. Directory enumeration failures are recorded as skipped
diagnostics with `reason: directory_listing_error` and redacted error text,
while readable sibling subtrees are still hashed. Binary files within the byte
limit are hashed as raw bytes and do not need to decode as text.
Environment provenance records Python/platform metadata, `pyproject.toml`
status/hash, selected package metadata (`project.name`, `project.version`,
`project.requires-python`, license, authors/maintainers, keywords,
classifiers, project URLs, optional dependency groups, scripts, and arbitrary
entry-point groups), build backend metadata, installed versions for declared
runtime dependencies, NumPy numerical-runtime
config hash/preview metadata, and hash-only records for known project-root lockfiles
(`requirements.txt`, `requirements.lock`, `uv.lock`, `poetry.lock`,
`pdm.lock`, and `Pipfile.lock`). The `installed_packages` snapshot records
installed distribution names, versions, and parsed `WHEEL` metadata, including
wheel versions, generators, `Root-Is-Purelib`, bounded tag records,
oversized metadata skips, redacted/escaped labels, capped retention metadata,
and an aggregate hash over the full uncapped record set.
`pip_freeze` records a bounded, redacted `python -m pip freeze --all`
snapshot with retained line hashes, a SHA-256 hash over the raw stdout text,
and degraded timeout/error statuses when freeze capture is unavailable.
`pip_config` records a bounded, redacted `python -m pip config list` snapshot
with retained line hashes, a SHA-256 hash over the raw stdout text, and
degraded timeout/error statuses when config capture is unavailable.
`numerical_runtime.numpy` records NumPy availability/version and, when
`numpy.show_config()` is available, a redacted bounded preview plus SHA-256 hash
of the full captured configuration text.
`llm_provider_sdks` records installed `openai`, `anthropic`, and `ollama`
package versions when present, plus the built-in adapter module and adapter API
modes; missing or failed version lookups are recorded with degraded statuses.
`accelerator_runtime` records selected CUDA/NVIDIA/ROCm/HIP/oneAPI/SYCL/
DirectML environment hints as bounded redacted values plus hashes, and records
degraded `nvidia-smi`/`rocm-smi` driver probe results when those tools are
available.
Readable in-budget lockfiles record path,
status, bytes, SHA-256, and an aggregate `lockfiles.hash`; unreadable,
over-limit, non-regular, or linked candidates are recorded with degraded
statuses without copying lockfile contents into the manifest.
`environment_reproducibility_policy` records the manifest-visible policy for
these environment surfaces. Its hash covers package metadata, lockfile hashes,
installed-package snapshot hashes, `pip freeze` and `pip config` stdout hashes,
NumPy config hashes, provider SDK-version hashes, and accelerator probe hashes.
It also explicitly lists unsupported complete install-source interpretation,
broader non-project build provenance, live provider service/API-version
capture, provider cost, remote provider-side defaults, accelerator budget
accounting, private package-source identity/authentication resolution, and
remote package artifact verification.
It is a bounded
package-name/version plus installed-distribution `WHEEL` tag metadata,
known-lockfile hash, `pip freeze` hash/preview, `pip config` hash/preview,
NumPy config summary, built-in LLM provider SDK-version summary, and bounded
accelerator runtime hint/probe summary, not a complete build-provenance record,
full environment-variable snapshot, private package-index/source
interpretation policy beyond redacted config evidence, live provider
service/API-version capture, provider cost or remote provider-side default capture, or
accelerator budget/accounting record.
Package/build metadata fields include
`name`, `version`, `requires-python`, license, authors/maintainers,
keywords, classifiers, project URLs, optional dependency groups, scripts,
arbitrary entry-point groups, `build-backend`, and `build-system` `requires`;
extra `[project]` metadata is captured separately as bounded scalar/list/table
records with raw-value hashes, while broader non-project build metadata is not
captured as package metadata.
Package/build metadata is normalized into bounded, redacted/hash-backed
manifest fields. If package metadata is missing, cannot be decoded, cannot be
parsed, or has invalid dependency schema, package
name/version/build/dependency fields are omitted and the degraded
`package.pyproject` status explains the local metadata failure.
Evaluator provenance currently covers the Python files directly configured as
`validate.py` or `eval_stages[].validate_path`, package validator `__init__.py`
entrypoints when a configured path points at a package directory, plus a
bounded `companion_sources` snapshot of sibling `.py`, `.json`, `.jsonl`,
`.yaml`, `.yml`, `.txt`, `.csv`, `.tsv`, and `.md` files under each evaluator
directory. Companion records use problem-relative redacted path labels,
streamed SHA-256 source hashes, byte counts, a deterministic aggregate hash,
file/count byte caps, and skipped-file diagnostics for links, path escapes,
oversized files, and read/resolve/stat errors. This is a manifest provenance
policy rather than dynamic tracing: the validator subprocess enforces that
problem-local imports and file reads must target the configured entrypoint,
captured `companion_sources`, or captured `declared_data_sources`. Undeclared
or over-budget problem-local helper/data access fails during preflight or
evaluation instead of running outside the evaluator-source hash scope.
Evaluator source records use problem-relative path labels plus `path_hash` /
`relative_path_hash` fields, and secret-like path segments are redacted before
manifest persistence. Direct evaluator source hashes use a `streamed_full_file`
policy with `hash_chunk_bytes` metadata; when source hashing raises an
`OSError`, the record stores `status: read_error`, redacted error metadata, and
omits `sha256`. Opt-in collected evaluator artifacts carry their own hashes in
per-evaluation metadata rather than the run-start manifest.
When `evaluator_data_include` or stage-level `data_include` is configured,
each evaluator source also carries `declared_data_sources` with globs relative
to the evaluator directory, matching problem-relative file labels, data-relative
paths, streamed hashes, byte/count caps, skipped diagnostics, and an aggregate
hash. The same declared data file list is passed to three-argument validators
as `stage["evaluator_data"]`; the validator subprocess `cwd` remains the
candidate workspace.
Context policy provenance covers deterministic local file selection, not
learned semantic ranking or global prompt packing. `max_chars_per_source` is a rendered
prompt-excerpt limit; `excerpt_policy` records whether selected local sources
use default `head` prefix excerpts, deterministic `head_tail` first/last
spans, or deterministic `term_ranked` task-term-overlap windows under that
cap. Term-ranked source metadata records ranking policy, query-term hash/count,
selected chunks, omitted chunk count, and excerpt spans; `max_bytes_per_source`,
`max_total_bytes`,
`max_pdf_pages`, `max_pdf_chars`, `max_context_entries`, `max_context_depth`,
`max_skipped_diagnostics`, and `max_context_provenance_chars` bound local
context ingestion and retained skipped-source provenance. Successfully
extracted PDFs include page-level character spans plus `excerpt_pages` /
`excerpt_page_spans` for the rendered excerpt. Failed text/PDF extraction and
no-text PDFs are excluded from prompt context and retained as skipped
diagnostics with `extraction_status`, hash/byte metadata, and available error
or document-page metadata.
Context manifest entries matched by an explicit `include` pattern use
`on_explicit_context_failure: "error"` by default: read errors, invalid UTF-8,
corrupt PDFs, no-text PDFs, and PDF resource-limit failures abort problem
loading before run artifacts are written. If the manifest sets
`on_explicit_context_failure: "warn"`, the run can proceed with degraded
context and `problem.context_policy` records `explicit_context_failure_count`
plus compact `explicit_context_failures` entries with matched include patterns.
For context manifests with `include`, each
`problem.context_policy.include_patterns[]` record stores pre-filter `matches`
and post-filter `selected_matches`, so excluded, hidden, unreadable, and
over-budget files remain distinguishable from files that entered prompt
context.
For valid `.txt`, `.md`, and `.py` context, `chars_original` and
`chars_rendered` describe the decoded UTF-8 text without trimming
leading/trailing whitespace.

Reusing an existing run directory is intentionally not treated as resume.
Before a run starts, LibreEvolve checks the target run directory for known run
artifacts: `history.jsonl`, `history_invalid.jsonl`, `failure_history.jsonl`,
`failure_history_invalid.jsonl`, `archive_events.jsonl`,
`archive_events_invalid.jsonl`, `prompt_history.jsonl`,
`prompt_history_invalid.jsonl`, `manifest.json`, `manifest_invalid.jsonl`,
`best.py`, `best_workspace/`, `evaluator_artifacts/`, and `plugin_artifacts/`.

The default collision policy is `fail`: if any of those artifacts already
exist, startup fails before appending new history or rewriting the manifest.
Use a fresh `--run-name` for independent runs, or pass `--overwrite` / set
`run_collision_policy: overwrite` to delete only those known artifacts before
the new run begins. The resolved run-directory containment check runs before
this cleanup, so overwrite does not follow an escaping symlink/junction run
directory outside `log_dir`. The startup manifest payload is also serialized in
memory before cleanup, so non-serializable or non-finite config/problem/
provenance payloads fail without deleting old known artifacts. If any known
artifact path is itself a symlink or Windows junction, including
`best_workspace/`, `evaluator_artifacts/`, or `plugin_artifacts/`, overwrite
startup rejects the run before deleting any artifact. Arbitrary files in the
run directory are left alone and are not enumerated as run-owned artifacts.
Containment failures, existing-artifact failures, and linked-artifact cleanup
failures display scoped path labels and stable path hashes instead of raw
absolute roots.
They are summarized under `run_directory.foreign_entries` using immediate entry
type plus SHA-256 of the entry name, not raw filenames, so a directory with
foreign files is visible but should not be treated as a clean reproducible run
directory. If the existing run directory cannot be listed, the manifest records
a single redacted `status: "unreadable"` / `policy: "preserved_unlisted"`
foreign-entry diagnostic with the exception type and redacted error text.
`manifest.json` records `run_id` and `run_collision_policy`. `run_id` is
provenance metadata, not a resume handle. Configured run ids must match
`[A-Za-z0-9][A-Za-z0-9_.-]{0,127}` before manifest writes; values with control
characters, path separators, assignment syntax, leading punctuation, or
secret-like token patterns are rejected.

Before overwrite cleanup runs, the CLI and direct `evolve()` calls preflight
evaluator entrypoints. Missing `evaluate`, unsupported fixed-shape signatures,
import failures, syntax errors, async or generator `evaluate` functions,
variadic or keyword-only parameters, extra parameters, and invalid staged
`validate_path` entries fail as startup errors without deleting existing known
run artifacts or writing a replacement manifest. These preflight
import/signature checks run in a bounded subprocess with a temporary working
directory and the configured validator environment allowlist, not by importing
validator modules in the parent CLI/runtime process.
Preflight and evaluator-path validation diagnostics display problem-local
validator paths as problem-relative labels and outside paths as outside-problem
labels, with a stable path hash. They do not echo raw absolute problem roots in
missing-callable, import, syntax, unsupported-signature, missing-file, escape,
or configured-stage path failures.
Direct `CascadeEvaluator.evaluate()` calls do not own run artifacts, but they
now run the same validator-contract preflight once after diff/syntax checks and
before the first validator subprocess. Unsupported direct default or configured
stage validator signatures therefore fail before subprocess execution instead
of becoming a separate accepted library path.
Configured plugin names and built-in plugin spec mappings are also validated
before overwrite cleanup; whitespace, control-character, secret-like, unknown
plugin aliases, unknown plugin options, and invalid option values fail without
deleting existing artifacts. The manifest writer revalidates the same
manifest-safe plugin-label/spec policy before writing `config.plugins`, so
direct API callers cannot persist unsafe mutated labels or option records.
Configured backend model identifiers are likewise validated as manifest-safe
strings before run startup and revalidated by the manifest writer.
Configured evaluator stage names are explicit manifest-safe identifiers, and
the built-in `diff`, `syntax`, and `validate` labels are reserved so configured
stage records cannot collide with evaluator-generated stages.
The database manifest boundary revalidates the full mutable `Config` before
run-directory preparation and startup manifest writes. Direct callers that
mutate run identity, scalar budget fields, backend specs, plugin labels, or
evaluator stages after construction fail before replacement run artifacts are
created.
Direct `Problem.task_description` is validated before prompt rendering and
run-directory preparation. It must be non-empty text bounded to 20000
characters, with no secret-like text, unsafe ASCII controls, or Unicode
surrogates. Valid task text is kept exactly rather than redacted, so task
content remains prompt/provenance material and should not contain secrets.
Direct `Problem.context_files` mappings are also validated before run-directory
preparation. Prompt-facing labels must be safe problem-relative paths using
forward slashes, with no absolute/drive roots, traversal, empty segments,
unsafe control or Unicode compatibility characters, or secret-like text; values
must be text bounded to 6000 characters. Malformed direct context therefore
fails before overwrite cleanup or manifest writes rather than producing partial
prompt/history artifacts.
When `initial_workspaces` is empty, direct inline seeds are validated before
run-directory preparation as a list of UTF-8-encodable strings with valid
evolve-block markers and a 1000000-character per-seed limit. Malformed direct
inline seeds fail before overwrite cleanup or manifest writes.
When direct `initial_workspaces` is supplied, entries are validated and
normalized before run-directory preparation as `CandidateWorkspace` objects or
workspace record mappings with safe paths, UTF-8 text, present primary files,
and valid evolve-block markers. Byte-valued entries are normalized into
immutable binary static members with byte count, SHA-256, and bounded
`content_b64` provenance; the primary file remains a UTF-8 text member.
Malformed direct workspaces fail before overwrite cleanup or manifest writes.
Marker validation is fail-closed for non-Python marker-looking files:
JavaScript/C-style, HTML-style, or `# EVOLVE-BLOCK-*` declarations in
non-`.py` candidate files produce `unsupported_evolve_block_marker_syntax`
before mutation or persistence.
For runs that can perform mutation LLM calls, backend client construction is
preflighted before overwrite cleanup in the core runtime. The CLI also checks
OpenAI and Anthropic credentials as non-blank after trimming. Seed-only runs
that cannot call an LLM skip provider construction.

`manifest.json` receives a `runtime` section on normal loop exits and on
unhandled aborts after the startup manifest has been created. Normal exits
record `status: "completed"` plus a structured stop reason and consumed local
budgets: seed/candidate/total evaluation counts, cumulative evaluator elapsed
seconds, evaluator subprocess-attempt counts, configured-stage sample counts,
retry-attempt counts, evaluator timeout and sample/stage budget-exhaustion
counts, logical LLM-call counts, provider adapter-attempt counts, wall-clock
runtime seconds, and generation counts. Completed and aborted records also
include `runtime.llm_accounting`,
an audit-only summary copied from validated scheduler role-accounting counters
with aggregate totals and the configured logical-call, retry/fallback, timeout,
prompt, and accepted-output caps. The runtime budget snapshot remains the
authoritative stop-policy record for logical-call, provider-attempt, token, and
configured estimated-cost caps. Completed and aborted records also include
`runtime.provider_cancellation_policy`, a validated
`libreevolve.provider_cancellation_policy.v1` declaration for the current
provider request timeout, ensemble wait-deadline, and runtime-deadline
semantics. The default runtime record has `hard_cancel_ready: false`: it
documents retry/fallback/stop actions and artifact locations for timeout
telemetry, with role-scoped timeout rules for `mutation`, `critique`,
`feedback:*`, and `meta_prompt`. When
`llm_role_failure_quarantine_after` configures matching exact roles, those
timeout rules also declare `quarantine` actions and `quarantine_record`
artifact evidence. The record is still not an SDK cancellation token or a
timeout-specific stop policy. Completed runtime and aborted runtime records include
`runtime.wall_clock` with
`schema: "utc_run_timestamps_v1"`, UTC `started_at`, `updated_at`,
`finished_at`, and status-specific `completed_at` or `aborted_at` fields.
`runtime.wall_clock.runtime_seconds_source` points to
`consumed.runtime_seconds`, which remains the process-local monotonic budget
counter derived from `time.monotonic`; wall-clock timestamps are audit
provenance and are not used for budget enforcement. Current non-resumed runs
record one `resume_segments[]` entry for the initial process. Direct
`evolve(..., runtime_budget_state_snapshot=...)` calls and CLI
`--restore-budget-from-manifest` runs preserve the original `started_at`, apply
the previous consumed budget counters before new seed/generation work, and
append a `resumed_process` segment with its own start/update/finish timestamps.
Completed runtime
records also include `history.programs_logged`,
`history.history_partially_written`, and `artifacts` pointers for known
history, failure/quarantine, prompt-history, evaluator/plugin artifact,
LLM telemetry, `best.py`, and `best_workspace` paths. Regular file pointers
record byte counts plus SHA-256 hashes of file bytes, and directory pointers
record deterministic tree hashes over relative file paths and per-file
SHA-256 hashes while skipping link-like entries. These are aggregate artifact
summaries for audit/replay planning, not full archive checkpoints. For
completed runs with a selected best program, core-loop finalization writes
`best.py` plus `best_workspace/` before recording those pointers, then
attaches `runtime.best_artifact_export`. It records
`status: "completed"` or `status: "failed"`, bounded/redacted failure
diagnostics, best-artifact paths, file/workspace hashes when available, and
refreshes `runtime.artifacts.best.py` plus
`runtime.artifacts.best_workspace`. The top-level runtime status remains the
core evolution result, so use `runtime.best_artifact_export` to distinguish a
completed evolution from a successful best-artifact export. The CLI reads this
runtime record after `evolve()` returns and reports or fails the command from it.
Runtime artifact pointers are diagnostic records, not
ownership proofs: they use non-following inspection for known artifact paths,
record `present`, `exists`, `kind`, `is_symlink`, `is_junction`,
`broken_link`, and, for link-like entries, redacted target-containment
diagnostics such as `target_scope`, `target_within_run_dir`, and target
hashes. Link-like artifacts are reported as `kind: "link"` and do not receive
target file sizes or directory kinds. Filesystem inspection errors are retained
as bounded, secret-redacted `inspection_errors` entries so artifact pointer
collection does not replace the original abort diagnostic. Current normal stop
reasons include `max_generations`,
`max_evaluations`,
`max_evaluator_seconds`, `max_evaluator_subprocess_attempts`,
`max_evaluator_stage_samples`, `max_evaluator_retry_attempts`,
`max_evaluator_timeouts`, `max_evaluator_sample_budget_exhaustions`,
`max_evaluator_stage_budget_exhaustions`, `max_llm_calls`,
`max_llm_provider_attempts`, `max_llm_tokens`, `max_llm_cost_microusd`,
`max_runtime_seconds`, `no_parent`, `no_valid_programs`, and `completed`.
`no_valid_programs` is used when seed
evaluation leaves no archive-retained parent; that startup stop does not count
as a started generation and does not construct a mutation LLM. For
`max_generations=0` seed-only runs, this means invalid-only seeds produce
history and failure-history diagnostics, no best artifacts, a completed
manifest with `stop_reason: "no_valid_programs"`, and a nonzero CLI exit
because there is no selected best program to export. The wall-clock
runtime budget is cooperative: it is checked after control returns to the run
loop, not as an interrupt for in-flight mutation, critique, feedback, or
meta-prompt provider calls.
`max_evaluations=0` is an accepted dry budget point. It completes with
`stop_reason: "max_evaluations"`, zero consumed evaluations, no best program,
and `runtime.history.no_candidates_evaluated: true` plus
`candidate_absence_reason` / `history_absent_reason` explaining that seed
evaluation was skipped by the evaluation budget. `max_evaluator_seconds=0` and
`max_runtime_seconds=0` are not dry-run modes; config validation rejects them
because those limits must be positive when provided.
Budget evaluation events are typed at the `RunBudget.record_evaluation()`
boundary: elapsed time must be a finite non-negative number and the `seed` flag
must be an exact boolean, so malformed direct or future controller calls fail
before elapsed-time or seed/candidate counters are mutated.
Budget snapshots, limit checks, and finalization validate non-negative integer
evaluation/generation counters, finite non-negative evaluator seconds, coherent
seed/candidate totals, and stop reasons from the documented enum before those
values are returned for manifests or candidate metadata.
That validation covers the current in-memory `RunBudget` object and restored
runtime budget snapshots. `validate_restored_budget_snapshot()` preflights
persisted runtime-budget snapshots before restore, including limits, consumed
counters, wall-clock metadata, resume segments, and stop reasons.
`validate_controller_budget_state()` validates the future controller/resume
wrapper around those snapshots. Controller state must declare
`libreevolve.controller_budget_state.v1`, include a checked runtime snapshot,
and carry contiguous `libreevolve.controller_budget_event.v1` rows.
`validate_controller_budget_event()` rejects malformed event kind, sequence,
elapsed time, evaluator accounting, unsupported fields, and stop reasons before
`apply_controller_budget_event()` mutates an in-memory budget. Evaluation
events are explicitly split into `seed_evaluation` and
`candidate_evaluation`, which preserves seed/candidate counter provenance for
future restored controllers. Live synchronous budget consumption now appends
contiguous rows to `controller_budget_events.jsonl` for seed evaluations,
generation starts, LLM calls, candidate evaluations, generation completions,
and final stop reasons. LLM rows carry role-tagged logical calls plus retained
provider-attempt, token, configured-cost, and latency deltas when call
telemetry exposes them, and `apply_controller_budget_event()` can replay the
emitted sequence into a fresh `RunBudget`. LibreEvolve applies restored budget
snapshots from prior manifests to live resumed runs. `load_full_resume_bundle()`
and CLI `--restore-runtime-from-manifest` now package validated budget
snapshots and contiguous controller budget event rows together with runtime
RNG, LLM scheduler, full archive restore inputs, the checked runtime RNG replay
boundary, and the checked lineage-policy provider-output boundary. The
controller event rows are replayed and their non-wall-clock consumed counters
must match the manifest budget snapshot before the bundle passes that budget
snapshot into `evolve()`. Completed runtime history also records
`runtime.history.controller_state`, a terminal drained-state snapshot for the
synchronous controller with zero queued/running proposals, evaluations,
in-flight LLM calls, and pending archive admissions plus a compact
`controller_budget_events.jsonl` summary. Queued/running async worker state,
provider-output replay, and end-to-end lineage replay proof remain separate
resume work.
Malformed evaluator accounting passed directly to `RunBudget.record_evaluation()`
is rejected before local evaluation counters mutate. The current
`max_evaluations` limit is still a seed/candidate evaluation cap rather than a
subprocess-attempt or stage-sample cap. Separate
`max_evaluator_subprocess_attempts`, `max_evaluator_stage_samples`,
`max_evaluator_retry_attempts`, `max_evaluator_timeouts`,
`max_evaluator_sample_budget_exhaustions`, and
`max_evaluator_stage_budget_exhaustions` limits cap those detailed counters.
Those caps are cooperative: the evaluation that consumes the final allowed
counter is recorded, then the run loop stops before the next seed/candidate
evaluation or LLM generation.
Unhandled provider, plugin, evaluator, materialization, serialization, and
keyboard-interrupt failures record `status: "aborted"`, `stop_reason:
"aborted"`, exception type, redacted/bounded message, message character count,
message-truncation and message-unavailable flags, the current loop phase, the
inferred role, artifact/quarantine pointers, and whether candidate history had
been written, then re-raise the original exception. Abort message redaction
uses the same secret-pattern masking applied to plugin metadata. Messages over
2048 characters are truncated with an explicit suffix; exceptions whose
`__str__` raises are recorded with a safe placeholder rather than blocking
manifest finalization.
Runtime manifest updates use strict finite JSON and atomic replacement. If a
runtime payload contains a non-JSON-compatible object or non-finite number, the
previous valid `manifest.json` remains in place and `manifest_invalid.jsonl`
records a diagnostic quarantine row.
If retrieval plugins emitted candidate metadata, `runtime.retrieval` records a
bounded run-level summary with total deduplicated retrieval events, per-plugin
status/source counts, and compact event summaries. It intentionally omits full
source payloads.
`max_llm_calls` caps logical LLM `generate()` invocations. A zero cap evaluates
seeds without constructing providers, and positive caps are checked
cooperatively before mutation, critique, feedback, and meta-prompt calls.
`max_llm_provider_attempts` caps provider adapter attempts reported through LLM
call telemetry; it is checked before the next logical LLM call and therefore
cannot interrupt a provider adapter's internal retry loop mid-call.
`max_llm_tokens` caps provider-reported `usage.total_tokens`, and
`max_llm_cost_microusd` caps configured estimated micro-USD cost when backend
metadata includes a local `cost_usd_per_million_tokens` rate. Accelerator and
async queue budgets are not first-class counters yet. Evaluator
subprocess-attempt, configured-stage sample, retry, timeout, sample/stage
budget-exhaustion, logical LLM-call, provider-attempt, token, and configured
cost counters are reported and can be capped by independent run-stop policies.
The current synchronous runtime can write multiple generated child candidates
per generation when `proposals_per_generation` is greater than `1`. Those
proposal batches are sequential and produce sibling-candidate accounting in
history rows; parallel LLM/evaluator worker artifacts remain future runtime
work.
When `max_generations` is `0` or local budgets stop before the first mutation,
LibreEvolve evaluates seeds and writes normal history/manifest/best artifacts
without constructing configured LLM provider clients.
Provider preflight runs before seed evaluation for positive-generation runs
where a mutation LLM could execute, so provider setup failures can stop such a
run before all-invalid seeds are recorded.

When plugins expose run artifact metadata, `runtime.plugin_artifacts` records
wrapped summaries with authoritative runtime plugin identity:

```json
{
  "plugin": "TTTRLPlugin",
  "module": "libreevolve.plugins.ttt_rl",
  "class": "libreevolve.plugins.ttt_rl.TTTRLPlugin",
  "index": 0,
  "instance_id": "plugin:0:libreevolve.plugins.ttt_rl.TTTRLPlugin",
  "metadata": {
    "reward_policy": "max(0.0, raw_score)",
    "queued_examples": 1,
    "skipped_malformed_examples": 0,
    "malformed_example_reasons": {},
    "payload_policy": "redact_sensitive_text_then_truncate_field_and_total_chars",
    "redacted_payload_examples": 0,
    "truncated_payload_examples": 0,
    "aggregate_truncated_payload_examples": 0,
    "redacted_payload_fields": 0,
    "truncated_payload_fields": 0,
    "payload_original_chars": 10,
    "payload_stored_chars": 10,
    "max_payload_field_chars": 20000,
    "max_payload_total_chars": 40000,
    "finalization_policy": "flush_pending_examples_before_artifact_metadata",
    "restored_exported_examples": 0,
    "restore_invalid_lines": 0,
    "restore_policy": "count_existing_grpo_jsonl_rows_without_reexport",
    "exported_examples": 1
  }
}
```

`runtime.plugin_state` records plugin configuration and execution state for
both CLI and direct API runs. `configured` lists configured plugin labels;
`loaded` contains runtime plugin identities equivalent to
`manifest.provenance.plugins`, including sanitized `version` records when a
plugin instance, class, or module exposes `__version__`; `loaded_specs` records
`libreevolve.plugin_spec.v1` constructor-parameter snapshots for built-in
loaded plugin instances, including `CausalPlugin`, `ModularPlugin`,
`DeepResearchPlugin`, and `TTTRLPlugin`. Path-valued constructor parameters are
stored as scoped records with hashes and only expose a relative path when the
target is inside the run directory. Configured entry-point plugins receive
`entry_point_plugin_signature_recorded` with the entry-point group/name/value,
distribution name/version plus hashes when available, configured
paper-inspiration label, hash-only distribution `RECORD` / `WHEEL` metadata
when available, captured manifest-safe constructor options, and constructor
signature shape.
Custom/direct plugins receive
`custom_plugin_signature_recorded` with constructor parameter names, kinds,
required flags, and default/annotation presence, but no constructor values or
instance attributes. Non-built-in direct and entry-point plugin specs also
include `direct_plugin_policy` with schema
`libreevolve.direct_plugin_policy.v1`, explicitly recording whether
constructor values are captured, how constructor schemas are handled, whether
instance attributes are excluded, and the package/paper-scope attribution
policy. `configured_without_loaded_instances` is
non-empty when a direct caller set `Config.plugins` but did not pass matching
plugin objects to `evolve()`; and `loaded_without_configured_labels` is
non-empty when direct plugin objects ran without configured labels. When
`evolve()` receives no explicit plugin objects, it resolves `Config.plugins`
through the built-in/entry-point registry and records
`core_resolves_config_plugins: true`.
Explicit direct plugin objects keep `core_resolves_config_plugins: false`.

`runtime.llm_scheduler` records the mutation LLM scheduler state observed at
finalization. A `snapshot` row has schema
`libreevolve.llm_scheduler_state.v1` and stores the same defensive-copy state
accepted by `LLMEnsemble.restore_scheduler_state()` after validating it against
the current backend count, plus a `resume_status` marker documenting that
persisted restore is supported or that a snapshot was restored into `evolve()`.
`load_runtime_llm_scheduler_state_snapshot()` validates this field from
`manifest.json`; direct callers can pass the result to
`evolve(..., runtime_llm_scheduler_state_snapshot=...)`, and CLI runs can use
`--restore-llm-scheduler-from-manifest`. Runs with no mutation-capable generation record
`not_initialized`; custom LLM objects without a `scheduler_state` dict record
`unavailable` with a manifest-safe type label; non-finite, non-JSON,
non-ensemble, or otherwise malformed state records `invalid` instead of
corrupting the manifest.

`runtime.llm_accounting` records the compact accounting view used for
run-level audits. A `snapshot` row has schema `libreevolve.llm_accounting.v1`,
policy `audit_summary_not_budget_enforced`, source
`llm_scheduler_state.role_accounting_and_role_scheduler_state`, a
`role_accounting` copy, aggregate `totals`, a `role_scheduler_state` copy,
aggregate `scheduler_totals`, and current LLM-related limits such as
`max_llm_calls`, `llm_role_call_limits`, `max_llm_provider_attempts`,
`max_llm_tokens`, `max_llm_cost_microusd`,
`llm_role_provider_attempt_limits`, `llm_role_token_limits`,
`llm_role_cost_microusd_limits`,
`llm_max_retries`, `llm_max_call_attempts`, `llm_fallback`,
`llm_call_timeout_sec`, `llm_max_response_chars`, `prompt_max_chars`,
`prompt_max_estimated_tokens`, `llm_reward_accounted_roles`, and
`llm_role_backend_indices`. Snapshot rows also copy the scheduler
`reward_accounting_policy`, which records the configured reward-accounted roles
separately from telemetry-only roles, and `role_call_limits`, which records
configured per-role logical-call limits plus consumed logical calls by role.
They also copy `role_backend_policy`, which records explicit configured
role-to-backend lanes, backend metadata role lanes, and the fallback policy.
Runtime budget `limits` also include the configured per-role provider-attempt,
token, and configured-cost maps, while `consumed` includes matching
`*_by_role` counters. Role-budget limits may be exact roles or prefix scopes
such as `feedback:*`; consumed counters remain exact concrete roles, and scoped
limits are enforced by summing matching exact-role consumption.
Role-scheduler records use
`selection_policy: "backend_metadata_role_scoped_when_configured_else_global"`;
older restored snapshots with the prior global-only marker are accepted and
normalized to this value.
When no scheduler snapshot exists, the accounting row mirrors the scheduler
status and reason so seed-only and malformed-custom-LLM runs remain explicit.
When a backend spec or direct backend metadata provides
`cost_usd_per_million_tokens` and provider usage includes `total_tokens`, call
telemetry records a `cost_estimate`, `role_accounting` accumulates
`cost_microusd`, and `runtime.llm_budget_report.role_usage[].cost_usd` renders
the aggregate estimate. Missing rates or missing token usage produce zero cost
usage and do not claim provider calls were free.
When a backend spec or direct backend metadata provides
`prompt_max_estimated_tokens`, the ensemble applies that backend/model
heuristic prompt-token cap together with any global cap before provider calls.
Call telemetry records the effective `max_prompt_estimated_tokens`, the global
`configured_max_prompt_estimated_tokens`, and the selected backend's
`backend_prompt_max_estimated_tokens`.

`runtime.rng` records the run-local Python RNG state observed at finalization.
A `snapshot` row has schema `python.random.mt19937.v1`, includes the configured
seed, stores a JSON-safe `random.Random.getstate()` payload and
`state_sha256`, and names `random.Random.setstate` as the restore entrypoint.
`load_runtime_rng_state_snapshot()` validates the field from `manifest.json`,
and `restore_runtime_rng_state_snapshot()` performs direct checked restore into
a `random.Random` instance. `runtime.rng.resume_status` distinguishes fresh
seeded snapshots from snapshots restored into direct `evolve()` calls or CLI
runs. `runtime.rng.replay_boundary` documents that this restores framework RNG
surfaces only, not provider outputs or plugin-owned randomness. This is not a
full run checkpoint; controller state, provider replay state, and plugin
internal replay state remain separate gaps.
`load_full_resume_bundle()` exposes the validated replay boundary as
`runtime_rng_replay_boundary`, making the RNG-owned and external non-replay
surfaces inspectable alongside the other restore metadata.

`runtime.lineage_replay_policy` records schema
`libreevolve.lineage_replay_policy.v1` for the loop-owned replay boundary. It
declares deterministic loop-created seed and generated candidate ids,
database-created prompt ids, and ordered LLM call telemetry ids as replay-stable
for matching streams. It also declares the direct `Program()` and
`PromptProgram()` UUID4 defaults outside the replay contract, states that
provider/model outputs are not replayed, and keeps `full_replay_ready=false`
until a resumed trace composes RNG, scheduler, archive, prompt history,
controller state, and provider-output semantics end to end.
`load_runtime_lineage_replay_policy_snapshot()` validates that manifest policy
and `load_full_resume_bundle()` packages the checked copy as explicit restore
metadata; any unsupported field, missing field, or claim that provider outputs
were replayed is rejected before the bundle is accepted.

Plugin-supplied fields live under nested `metadata`; top-level `plugin`,
`module`, `class`, `index`, and `instance_id` are derived from the runtime
plugin object and are not trusted from hook output. The `instance_id` format is
`plugin:{index}:{module}.{qualname}` for ordinary safe labels and is shared by
startup plugin provenance, prompt-context records, score-composition records,
artifact records, and plugin-failure records. Runtime plugin identity labels
are NFC-normalized, Unicode format controls are escaped, secret-like text is
redacted, and changed labels carry hash-backed raw identity fields such as
`plugin_hash`, `module_hash`, `class_hash`, and `instance_id_hash`. The `ttt_rl` export reports the reward
policy, queued, retained, pending, exported, and dropped-retained example
counts, skipped malformed-example counts/reasons, the in-memory retention cap,
payload policy/caps/counters, finalization policy, JSONL path, byte count,
SHA-256 hash, and quarantine path when available.
The `deep_research` cache artifact summary reports configured cache mode,
schema, cache-directory name and path hash, snapshot count, retained snapshot
count, skipped/read-error counts, per-snapshot file names, byte counts,
SHA-256 hashes, the retention cap, and an aggregate hash. This summarizes the
run-local cache snapshot files written under `plugin_artifacts/deep_research/`
when a cache directory is configured; it is not full provider/source payload or
ranked-source provenance.
Plugin artifact metadata keys
are recursively validated as display-safe labels: keys must be strings and
must not contain Unicode format controls such as right-to-left override or
zero-width joiner. Secret-like or oversized keys are persisted as bounded
hash-suffixed labels, using a neutral redacted label for credential-shaped
keys. Plugin metadata values are also validated before persistence: they must
be JSON-safe finite primitives, lists, or dictionaries. String values are
bounded, reject Unicode format controls, and receive the shared versioned
secret-pattern grammar. `run_artifacts_metadata()` may return `None` or `{}` to emit no
entry; other non-mapping returns abort completed runs. Aborted-run finalization
attempts to collect valid plugin artifact summaries and records schema or hook
failures under `runtime.plugin_artifact_failures[]` without hiding the original
abort exception.

## `history.jsonl`

Each line is one candidate record. Current fields:

- `id`
- `code`
- `files`
- `primary_file`
- `fitness` (finite non-boolean number for persisted accepted rows; direct
  `Program` construction uses the legacy `-inf` sentinel only when fitness is
  omitted, and rejects explicit non-finite fitness values)
- `generation`
- `parent_id`
- `lineage`
- `metadata`
- `metrics`
- `evaluation`

Important behavior:

- every evaluated candidate is logged, including invalid candidates
- the log is append-only
- the archive and the log are distinct
- `metadata.candidate_type` distinguishes `seed` baselines from `generated`
  candidates
- seed baselines use `generation: 0`; generated candidates use completed
  generation counts starting at `1`. Generated rows also persist the
  zero-based internal loop index as `metadata.loop_generation_index`. When
  `proposals_per_generation` is greater than `1`, sibling generated rows share
  the same generation and record `metadata.proposal_batch` with policy,
  zero-based proposal index, one-based proposal number, configured batch size,
  and global loop proposal index.
- loop-created seed and generated candidate ids are deterministic for current
  runs. Seed ids use seed order plus workspace hash; generated ids use
  generation coordinates, proposal index, parent id, prompt id, mutation hash,
  and workspace hash. Database-created prompt-program ids are deterministic for
  configured seeds and mutations. Direct `Program` ids, prompt ids,
  `parent_id`, and lineage entries must still be manifest-safe identifiers matching
  `[A-Za-z0-9][A-Za-z0-9_.-]{0,127}` and must not look like secrets
- direct archive admission rejects duplicate archive ids before mutating the
  live MAP-Elites/island archive, including a different object with an id that
  was already logged in the same run
- candidate workspace paths are NFC-normalized, must be stable under Unicode
  compatibility normalization, and reject Unicode format controls, surrogate
  code points, non-ASCII separator spaces, and secret-like labels before they
  can be persisted in accepted or failed history rows
- accepted-history logging rejects duplicate program ids by writing the
  rejected record to `history_invalid.jsonl` before raising `StrictJsonlError`;
  the accepted `history.jsonl` stream, accepted-id set, and in-memory accepted
  program list remain unchanged
- migration uses canonical-id references rather than clone ids: the same
  candidate id can be placed in multiple islands, repeated migration skips a
  target island that already contains the id, migration placement events are
  persisted in `archive_events.jsonl`, `load_archive_event_records()` validates
  those rows as an audit stream, and manifest archive snapshots can restore
  current cursor/cell/elite placements from checked accepted-history rows.
  Ordered migration-event replay and controller resume remain open.
- raw metrics and evaluator diagnostics are preserved for later inspection
- accepted program objects are defensively snapshotted at archive/log
  boundaries; public database accessors return snapshots, so caller-side
  mutation after admission/logging cannot rewrite in-memory archive or history
  facts
- `Program.evaluation` records are JSON-safe mappings at construction and are
  revalidated before archive admission, accepted-history logging, and
  failure-history logging; malformed stage arrays are summarized with
  diagnostics rather than crashing failure-memory rendering
- `EvaluationResult` and `EvaluationStageResult` objects validate direct and
  post-construction-mutated values before `to_dict()` emits prompt/history
  payloads; fitness, scores, elapsed seconds, metrics, stdout/stderr/error,
  stage labels, and metadata must be finite, typed, redacted, and JSON-safe
- declared numeric metrics normalized through `metrics.yaml` are stored under
  `metadata.normalized_metrics`; the first-pass multi-objective archive
  policy stores its scalar as `metadata.selection_score` and its policy
  description as `metadata.selection_policy`. The default policy is an
  equal-weight mean; optional finite non-negative metric `weight` values in
  `metrics.yaml` produce a `weighted_normalized_declared_metrics` policy with
  per-metric weights.
- `runtime.history.objective_frontier` stores a bounded diagnostic Pareto
  frontier over complete declared normalized metric vectors. This is an
  inspection artifact, not the MAP-Elites replacement policy. The live
  `frontier` parent/inspiration strategy computes its own non-dominated
  retained-program pool from the same declared normalized metric semantics.
- `runtime.history.objective_metric_leaders` stores a diagnostic
  best-program-per-declared-normalized-metric view with leader program ids,
  generations, metric values, selection scores, and available normalized
  metric vectors. This is an inspection artifact, not a metric-specific archive
  replacement policy.
- `runtime.history.objective_metric_archives` stores a bounded
  top-program-per-declared-normalized-metric view with retained program ids,
  generations, metric values, selection scores, and available declared
  normalized metric vectors. This is an inspection artifact, not a MAP-Elites
  replacement policy.
- `runtime.history.score_index` stores a bounded diagnostic top-valid-programs
  view ranked by archive selection score, then final fitness. Records include
  program id, generation, lineage root, selection score, fitness, archive
  admission summary, and available objective-vector evidence. This is an
  inspection artifact, not a replayable sampling policy.
- `runtime.history.lineage_index` stores a bounded diagnostic
  best-valid-programs view grouped by root lineage. Each retained root records
  the best representative, selected top lineage programs, generation,
  lineage-depth, selection score, fitness, and available normalized objective
  evidence. This is an inspection artifact, not a persisted sampling replay
  engine.
- `runtime.history.descriptor_index` stores bounded diagnostic top-program
  views for finite values found in `metadata.archive_admission.descriptors`.
  Each descriptor record includes descriptor value, generation, lineage root,
  selection score, fitness, and available objective evidence. Descriptor values
  are insertion-time archive coordinates, not stable learned descriptor
  normalization replay.
- `runtime.history.feedback_index` stores bounded diagnostic feedback records
  grouped by LLM feedback grader name. Each retained record includes program
  id, generation, lineage root, validity, score/normalized-score/weighted-delta
  values when finite, discard/error/objective-metric flags, retention summaries,
  and bounded redacted feedback text hashes/previews when feedback text is
  retained by policy. This is not a feedback embedding store or replayable
  sampling policy.
- `runtime.history.failure_index` stores bounded failure records grouped by
  `failure_fingerprint.sha256`. Each group records occurrence/repetition
  counts, record type, parent id, changed files, latest failure record, and
  bounded representative records with mutation payload hashes, failure reasons,
  file deltas, and redacted evaluation summaries. This makes failure
  repetition evidence manifest-visible, but it is not a cross-run failure
  database or semantic failure-similarity index.
- `runtime.history.resurfacing_index` stores a bounded deterministic
  rank-fusion view over the score, objective-frontier, metric, lineage,
  descriptor, feedback, hypothesis, and artifact indexes. Records deduplicate
  by program id and include source ranks/contributions, lineage root, selection
  score, fitness, archive-admission summary, and available objective evidence.
  This makes
  resurfacing decisions manifest-visible, but it is still rebuilt from current
  history records and is not a persisted database table, embedding search
  engine, or schema-migration layer.
- `runtime.history.hypothesis_index` stores bounded proposal
  idea/rationale/hypothesis summaries for valid programs with captured
  proposal metadata. Text fields are redacted, hashed, and capped before
  manifest persistence. This makes proposal-hypothesis evidence queryable from
  run artifacts, but it is not a cross-run hypothesis database or semantic
  hypothesis search layer.
- `runtime.history.artifact_index` stores bounded evaluator-artifact evidence
  for programs whose `evaluation.metadata.artifacts.files` retained copied
  files. Records include program id, lineage root, validity, generation,
  selection score, fitness, collection/stage metadata, retained artifact paths,
  byte counts, stored SHA-256 hashes, redaction status, skipped-artifact
  diagnostics, and bounded redacted content-excerpt summaries for UTF-8 copied
  artifacts. This makes artifact-bearing candidates manifest-visible and
  available to the resurfacing rank-fusion view, but it is not a full artifact
  content index, cross-run artifact database, or semantic artifact search
  layer.
- optional critique metadata is stored under `metadata.critique`
- optional proposal idea/rationale/hypothesis sections are stored under
  `metadata.proposal` when `capture_proposal_metadata` is enabled; when critique
  is enabled this reflects the selected post-critique mutation
- the mutation backend index is stored under `metadata.backend_idx`
- inspiration sampling provenance is stored under
  `metadata.inspiration_selection`; metric leader policies include target
  metric/program pairs so metric-specific inspiration choices are auditable,
  frontier policies include frontier size and declared metric order, and
  lineage policies include lineage-root/program pairs
- normalized LLM call telemetry is stored under `metadata.llm_calls` as the
  candidate-linked mutation/critique/feedback call span, including recovered
  retry or fallback attempts that led to a successful candidate
- archive admission metadata is stored under `metadata.archive_admission`
- optional LLM feedback grader records are stored under
  `evaluation.metadata.llm_feedback`
- each applied feedback grader also appends an `llm_feedback:<name>` stage to
  `evaluation.stages` with pass/fail, score, error/discard state, elapsed
  time, and provenance metadata pointing back to the feedback record
- feedback grader prompts include bounded explicit problem context with source
  provenance, candidate workspace files, evaluator diagnostics, and metrics
- mutation prompt feedback summaries use `passed`, `failed`, or `unknown`
  stage status labels instead of treating missing status as failure
- selected inspiration programs include bounded evaluator/stage/output/LLM
  feedback summaries when available, not just code and metric values
- mutation prompts render parent and inspiration candidate workspaces as
  typed, length-counted, JSON-escaped file records with primary/support roles
  instead of markdown code fences
- explicit context bodies in mutation prompts render as character-counted
  JSON strings under context source citation headers, and context entries are
  path-sorted for deterministic prompt assembly. Citation headers use
  bounded/redacted display metadata for source labels, hashes, excerpt spans,
  page spans, character counts, and extraction status. Duplicate
  `context_sources` records for the same path are selected canonically rather
  than by insertion order; generated program `metadata.prompt_diagnostics`
  stores `context_order`, context source missing/extra/duplicate path lists,
  and a rendered-prompt `prompt_sha256` for replay comparison.
- generated program `metadata.prompt` stores the persisted mutation prompt
  according to `mutation_prompt_retention_mode`: `redacted` keeps the
  secret-redacted prompt, `full` keeps the full rendered prompt subject to
  shared persisted-metadata secret redaction, and `hash_only`/`off` store no
  prompt text. `metadata.prompt_retention` records the configured mode,
  retention policy, stored character count, redaction flag when applicable,
  and raw rendered-prompt hash/count metadata when the selected mode retains
  it. The LLM call still receives the rendered prompt; these fields document
  only the persistence boundary.
- `prompt_history.jsonl` records prompt programs only after reward-policy and
  prompt-state validation; direct prompt programs must have manifest-safe ids,
  non-negative integer generation/use counters, finite reward sums, and
  JSON-safe metadata. Accepted prompt records include `template_sha256`;
  duplicate configured variants or duplicate evolved templates remain separate
  prompt arms with independent ids/rewards/lineage but can be grouped by this
  content hash.
- missing or invalid prompt ids supplied to prompt scoring or mutation, plus
  duplicate prompt ids or unknown parent ids supplied to direct prompt-program
  adds, are written to `prompt_history_invalid.jsonl` as bounded
  `prompt_reference_error` rows before `StrictJsonlError` is raised
- evaluator metadata stores validator entrypoints as problem-relative
  `evaluation.metadata.validate_path` values with
  `validate_path_scope: problem_relative`, `validate_path_hash` for the raw
  resolved path, and `validate_path_redacted` showing whether the absolute path
  was omitted. Nested stage configs and retry-attempt metadata apply the same
  `validate_path` display policy. Unicode format controls in visible evaluator
  path labels are escaped, while ordinary non-ASCII path text remains visible.
- `metadata.budget` stores the run-budget snapshot after that candidate's
  evaluation and post-evaluation budget check. If the candidate consumes a
  run-wide evaluation or evaluator-counter limit, the row's
  `metadata.budget.stop_reason` matches the final runtime stop reason.

Archive admission prevalidates accepted candidate history records before
mutating the live MAP-Elites/island archive. Direct admission thresholds must be
finite non-boolean numbers before they can affect archive insertion or
`metadata.archive_admission.threshold`.
Archive events split the overloaded admission concept into
`cell_admitted` for MAP-Elites behavior-cell entry/replacement,
`elite_retained` for auxiliary elite-list retention, `search_state_changed` for
any retained archive-state change, and `sampling_eligible` for occupied-cell
explore/inspiration eligibility. `admitted` remains a compatibility flag
meaning the candidate changed either retained archive state, not necessarily
that it occupies a MAP-Elites cell.
The island round-robin cursor advances only on `search_state_changed`; a
threshold-passing but non-retained candidate such as `reason:
"not_improving_cell"` records its attempted island but does not consume the
next island assignment. Runtime manifests persist the cursor and adjacent
archive counters under `runtime.history.archive_state` with schema
`libreevolve.island_state.v1`; the snapshot records `next_island_id`,
`archive_sequence`, `migration_sequence`, `metric_sample_index`,
`frontier_sample_index`, `lineage_sample_index`,
`archive_sequence_by_program_id`, and compact per-island occupancy/elite
counts. Current snapshots use `resume_status:
"snapshot_persisted_cursor_and_full_archive_restore_supported"`; manifests with
the legacy cursor-only status remain accepted for backward-compatible restore.
New snapshots also include
`archive_contents`, a per-island MAP-Elites state payload with occupied cells,
elite-program ids, descriptor policy metadata, descriptor-model revision and
reference ids, and archive configuration, plus
`migration_replay`, which records
`status: not_applied_as_restore_engine`,
`replay_engine_supported: false`, and that archive-content restore covers
current migrated placements without replaying migration event order.
`runtime.history.archive_event_replay_audit` separately validates
`archive_events.jsonl`, replays the last admitted migration placement per
target island/cell, and compares that partial event-derived view with
`archive_contents`. Its statuses distinguish absent streams, no migration
placements, verified placements, and superseded or missing placements. The
audit is not a restore engine because normal archive admissions and controller
pending work are not reconstructed from migration rows.
The descriptor model explicitly records dynamic TF-IDF diversity references
and the no-rebin policy
`no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots`;
restored snapshots must match the configured performance bounds,
complexity bound, elite reference ids, and no-rebin policy.
`IslandModel.restore_cursor_state()` can still apply only the cursor/counter
subset to a live island model. `IslandModel.restore_archive_state()` restores
the cursor plus cells/elites when the caller supplies checked `Program`
snapshots. `load_archive_restore_bundle(manifest.json, history.jsonl)` loads
the manifest archive state and reconstructs those program snapshots from
accepted history records. `ProgramDatabase(..., archive_state_snapshot=...,
archive_programs_by_id=...)` uses that bundle during database construction and
records `policies.archive_cursor_restore`; the policy reports whether
`archive_contents_restored` is true.
Startup manifests also record `policies.archive_identity.resume_status:
manifest_archive_state_restore_supported`, list the restored archive surfaces
(`round_robin_cursor`, `archive_sequence_counters`, `map_elites_cells`, and
`elite_archives`), and explicitly mark `migration_event_replay:
audit_only_not_restore_engine`.
`evolve(..., runtime_archive_state_snapshot=...)` passes this validated
snapshot into the run database for cursor restore. Supplying
`runtime_archive_programs_by_id` as well restores the persisted MAP-Elites
cells and elite lists. CLI runs can load the cursor-only snapshot from a prior
`manifest.json` with `--restore-archive-cursor-from-manifest`, or load the full
archive bundle from a prior manifest plus sibling `history.jsonl` with
`--restore-archive-from-manifest`.
`load_runtime_archive_state_snapshot()` validates this compact manifest field
for future resume use, including schema/status, cursor bounds, manifest-safe
program ids in `archive_sequence_by_program_id`, and per-island count records.
`runtime.history.controller_state` records the terminal synchronous controller
boundary beside this archive state, but does not reconstruct async worker
queues or partially completed generation work.
Retained elite-only candidates can still resurface through best/exploit,
metric, novelty, recency, selection, mixed inspiration, and migration paths.
They remain excluded from occupied-cell explore and random inspiration pools
unless they also enter or replace a MAP-Elites cell.
Accepted archive updates also include a monotonic `archive_sequence` in both
`metadata.archive_sequence` and `metadata.archive_admission.archive_sequence`
for audit/provenance. Live recency sampling uses the archive's internal
insertion sequence before generation and score tie-breaks, so later mutations to
the persisted metadata field do not change sampling order.

Initial seed rows are raw evaluator baselines. They record
`metadata.post_processing.policy = raw_evaluator_baseline`; loaded seeds also
record `metadata.seed_source_path`, `metadata.seed_source_kind`, and
`metadata.seed_index` so duplicate-content seed files or directories can be
audited without relying on generated UUIDs. LLM feedback graders and plugin
score-composition hooks are not applied to seed rows, even when those features
are configured. Generated candidates use
`metadata.candidate_type = generated` and can include prompt ids, LLM call
telemetry, parent-selection records, critique records, feedback grader records,
and plugin `metadata.score_composition`. Parent-selection records include the
effective strategy, selected parent id, and, for metric parent sampling, the
target metric plus target index/count.

When critique is enabled, `metadata.critique` stores retained text for the
original mutation, revised mutation, and critique prompt, plus the critique
backend index, parser diagnostics for the revised and original mutations, and
whether the revision or the original mutation was selected for evaluation.
If `critique_reviewers` is configured, `metadata.critique.reviewer_pool`
records schema `libreevolve.critique_reviewer_pool.v1`, aggregation policy,
reviewer count, completed review count, valid revision count, selected
reviewer name/role, and one bounded reviewer record per attempted reviewer.
Reviewer records include their manifest-safe role, backend index, retained
prompt/mutation hashes, provider failure or parser fallback details, and
selection status. The selected reviewer record is also mirrored at the top of
`metadata.critique` for compatibility with single-reviewer readers.
The selector accepts a valid critique revision, falls back to a valid original
mutation when the revision is malformed, and preserves the original generated
mutation as the selected failure payload with
`fallback_reason="no_valid_mutation"` when neither candidate validates.
When proposal capture is enabled, critique metadata also stores
`original_proposal`, `revised_proposal`, and `proposal_source` so the selected
candidate proposal can be distinguished from the initial mutation proposal.
Proposal metadata is stripped only from the leading contiguous mutation-response
preamble; marker-like proposal lines inside the selected candidate payload are
preserved. Proposal fields can be one-line `IDEA:`, `RATIONALE:`, or
`HYPOTHESIS:` entries, or bounded multiline `[IDEA]...[/IDEA]`,
`[RATIONALE]...[/RATIONALE]`, and `[HYPOTHESIS]...[/HYPOTHESIS]` blocks.
Wrapped colon-style continuation text before a later proposal marker is
recorded as a malformed proposal-metadata mutation failure instead of being
applied as full-mode candidate code.
The retained critique text is redacted and prefix-bounded before history
persistence; sibling fields store SHA-256 hashes, original character counts,
retained character counts, truncation flags, and the retention policy. Set
`critique_retention_mode` to `full`, `redacted`, `hash_only`, or `off` to
control persisted critique prompt and mutation text; provider critique calls
still receive their prompt and mutation payloads.

Synthetic diff/mutation failures persist schema-safe diagnostics under
`evaluation.metadata.diff_error` and the diff stage's metadata. Known parser
or runtime mutation reasons such as `no_diff_blocks`,
`non_text_mutation_payload`, `no_valid_changes`, `search_not_found`, and
`ambiguous_search_match` remain the top-level/stage error codes. Unknown string
reasons are recorded as `unknown_diff_error` with bounded/redacted detail, while
non-string direct evaluator inputs are recorded as `malformed_diff_error`.
Validator-returned JSON must include every declared evaluator-sourced metric
and must not include feedback-sourced objective metrics. Internal synthetic
evaluator failures fill every declared metric with the finite failure penalty,
set `is_valid=False`, and persist
`evaluation.metadata.synthetic_metrics` with schema
`synthetic_failure_metrics_v1`, policy `declared_metric_penalty`, penalty, and
metric names. Diff, syntax, timeout, subprocess, malformed-output, budget, and
related framework-generated failure rows therefore retain metric-vector shape
while remaining distinguishable from real validator scores through
`evaluation.error`, `evaluation.stages`, and failure metadata.

Prompt metadata is stored for auditability. Mutation prompts are persisted
according to `mutation_prompt_retention_mode`: `redacted` by default, with
`full`, `hash_only`, and `off` also supported. Generated rows record
`metadata.prompt_retention`, and manifests record
`policies.prompt_data_retention` for the current mixed configurable/fixed
retention boundary. Critique prompt/mutation retention is controlled by
`critique_retention_mode` with the same `full`, `redacted`, `hash_only`, and
`off` modes, and is hash-backed under `metadata.critique` when the selected
mode retains hashes. Parent and inspiration metric summaries
rendered into mutation prompts are limited to problem-declared metrics,
`is_valid`, `feedback_adjusted_fitness`, and manifest-safe feedback metrics
explicitly recorded by LLM graders. Declared metrics include primary/secondary
role, direction, bounds, normalized value, out-of-range status, and separate
validity status. Prompt-visible parent and inspiration fitness values render
as finite normalized scores when possible and typed invalid markers such as
`<invalid_fitness:nan>` for malformed restored/direct records. The general
rendered-prompt history can still persist raw seed code, plugin context,
candidate code, and critique content.
LLM feedback workspace prompts use the shared versioned secret-pattern grammar
before provider calls. Prompt history and quarantine streams still contain
some fixed-policy retention surfaces. Feedback provider outputs are retained according to
`feedback_retention_mode`: `evaluation.metadata.llm_feedback[].raw_response`
and parsed `feedback` text remain present in `full`/`redacted` modes and are
suppressed in `hash_only`/`off`, with retention metadata recording the selected
mode, policy, SHA-256 hashes when enabled, original/stored character counts,
caps, and redaction/truncation flags.
Feedback scores are parsed only from JSON objects or explicit
`score: <number>` / `score=<number>` text, and scores must be finite values in
`[0, 1]`; incidental numbers in prose, provider status text, percentages, and
multi-number text are recorded as `llm_feedback_failed` rather than composed
into fitness.

The `*_invalid.jsonl` quarantine streams are strict-JSON diagnostics, not
fully sanitized logs. Framework-owned candidate, failure, prompt, LLM-call,
archive-event, and manifest quarantine rows include bounded, secret-redacted
serializer messages. Rejected `record_repr` snapshots and torn JSONL fragment
previews follow `quarantine_snapshot_retention_mode`: `redacted` keeps a
bounded secret-redacted preview plus raw SHA-256/count metadata, `full` keeps
the full secret-redacted preview plus raw SHA-256/count metadata, `hash_only`
keeps no preview text, and `off` keeps neither preview text nor snapshot hash
metadata. Plugin-owned quarantine writers that do not receive run config keep
the shared default redacted behavior. Missing quarantine parent directories
are created before writing diagnostics; invalid parent paths fail with
bounded, secret-redacted persistence errors. Treat these files as sensitive run
artifacts unless snapshot retention is explicitly set to `off`.

When plugins render extra prompt context for a generated candidate,
`metadata.plugin_context` records one entry per plugin with the plugin class,
module, parent id, inspiration ids, rendered JSON-string prompt section,
original/stored character counts, SHA-256 hash of the exact persisted section,
redaction/truncation flags, configured context cap, and whether non-empty
context was emitted. Plugin identity fields use the same redacted/hash-backed
runtime identity and version policy as startup plugin provenance and artifact
records.
Records also include `plugin_spec` with the same built-in plugin constructor
parameter schema used by `runtime.plugin_state.loaded_specs`; custom direct
plugins record signature shape without constructor values. `context_visibility`
and `metadata_visibility` distinguish prompt-visible injected text from
provenance-only plugin state. `build_extra_context()` must return `str` or
`None`; unsupported return objects abort the run during plugin-context
construction.
Plugin prompt-context metadata must be a mapping, `{}`, or `None`.
Non-mapping non-empty returns abort during plugin-context construction with
`runtime.abort.plugin_failure` attribution. Valid metadata is recursively
validated for display-safe keys, JSON-safe finite values, bounded strings, and
the shared versioned secret-pattern grammar before candidate history logging.
Plugin hook exceptions are fatal. Aborted runtime manifests add
`runtime.abort.plugin_failure` and `runtime.plugin_failures[]` records with the
redacted plugin class, module, index, hook name, fatal policy, generation, parent and
candidate ids when available, exception type, bounded/redacted message
diagnostics, and `continued: false`.
If the abort happens after plugin-owned files were written,
`runtime.plugin_artifacts` can include the same wrapped, validated summaries as
completed runs; malformed artifact-summary hooks are instead reported in
`runtime.plugin_artifact_failures[]`.
Plugins can also attach plugin-specific metadata. The DeepEvolve-inspired retrieval plugin stores
bounded retrieval events there with provider, query, generation, best id and
fitness, query policy, query input summary, timestamp, status, result length,
synthesis hash, bounded/redacted source IDs/URLs/titles/authors/timestamps and
excerpts, source metadata retention/redaction counters, summary hashes,
available provider errors, and structured error types such as `network_error`,
`parse_error`, and `provider_exception` when available. If the current best candidate has
non-finite or nonnumeric fitness, retrieval is skipped with
`skip_reason: non_finite_best_fitness` and no provider query or non-finite
`best_fitness` is recorded. The default query policy combines best-program
fitness, manifest-safe metric names, bounded code/file identifier terms,
bounded task-description and explicit-context terms, bounded recent
failure-history terms, bounded local paper manifest title/id terms, and bounded
recent proposal-hypothesis terms. Provider request URLs are represented as
`request_url` summaries with scheme, host, path, query-parameter count, URL
hashes, and omitted raw URL text. The default arXiv helper validates non-empty
safe query text and bounded integer `max_results` values before URL
construction, uses HTTPS for live requests, and records transport status plus
provider payload byte-count/hash metadata. Live arXiv responses are read with a
1,000,000-byte cap before XML parsing; exact-limit payloads are allowed, and
oversized payloads are recorded as structured `oversized_response` retrieval
errors without prompt injection. Run-level retrieval summaries carry bounded
transport fields such as authenticated-transport status, request/final scheme
and host, HTTP status, redirect status, payload byte-limit/observed-byte
diagnostics, truncation/oversize flags, and payload hash when available.
Retrieval events and cache snapshots now also retain bounded/redacted
`libreevolve.retrieval_provider_result_snapshot.v1` provider-result snapshots
with raw and stored hashes, original/stored character counts, and
redaction/truncation flags.
When `cache_dir` is configured and retrieval-body retention allows text,
DeepResearch writes `libreevolve.retrieval_payload_artifact.v1` sidecars under
`plugin_artifacts/deep_research/payload_artifacts/`. These sidecars retain the
full secret-redacted provider payload and retained source-content payloads only
when the redacted payload fits the 64,000-byte per-artifact budget; oversized
payloads are represented by metadata-only omitted artifacts with raw hashes and
counts. Retrieval events, cache snapshots, retained source rows, and
`runtime.plugin_artifacts[].metadata` link the sidecars by relative path,
SHA-256, artifact kind, payload field, raw/stored hashes, and retention policy.
`hash_only` and `off` retrieval-body retention modes suppress payload sidecars
and record the suppression in `payload_artifact_policy`.
Retained source rows include provider rank, current retained rank, source
integrity hashes, bounded source-content snapshots when available, and
`query_term_overlap_audit_v1` relevance scores. Retained rows also include
`libreevolve.retrieval_source_grounding_policy.v1` records that state whether
bounded retained source text is lexically grounded by deterministic query-term
overlap, plus an event-level `source_grounding_policy` aggregate with source
counts, grounded-source counts, and a records hash. This is lexical provenance,
not semantic verification.
Retained rows also include
`libreevolve.retrieval_source_content_trust_policy.v1` records that classify
content evidence as verified redacted payload artifacts, metadata-only oversized
payload artifacts, bounded content snapshots, hash-only content evidence, or no
content evidence. Event-level `source_content_trust_policy` rolls those records
up with source counts, replayable-evidence counts, mismatch counts, and a
records hash. Transport-policy limitations distinguish bounded redacted payload
evidence from missing semantic content evidence, but neither status proves
semantic correctness. Query events also include
`libreevolve.retrieval_evidence_boundary_policy.v1`, which records the explicit
retention boundary for raw provider/source payloads, TLS certificate chains, and
semantic verification. It links the payload-artifact, source-content, and
source-grounding, and transport evidence states so cache snapshots preserve
what evidence was retained versus what remains outside the audit boundary. The default
`source_ranking_policy` keeps provider order; opt-in
`query_overlap_score_desc_v1` reorders retained sources by deterministic
query-overlap score with provider rank as a tie-breaker, and records
`relevance_affects_order: true` in retrieval events, active prompt context, and
cache snapshots. The cache key includes the source-ranking policy so cached and
offline replay do not mix differently ordered source metadata for the same
query.
Successful retrieval text is rendered into prompts as non-authoritative
evidence with explicit `BEGIN_UNTRUSTED_RETRIEVAL_EVIDENCE` /
`END_UNTRUSTED_RETRIEVAL_EVIDENCE` delimiters. Candidate history and
run-level retrieval summaries record the trust policy, prompt-boundary policy,
and `authoritative: false` for successful retrieval context.
These retrieval records are best-effort provenance, not audit-grade source
integrity evidence: unbounded raw provider payloads, learned or externally
scored semantic ranking, semantic source-content verification beyond lexical
grounding, and a replayable transport/TLS decision tree are still not persisted.
DeepResearch cache metadata records mode, cache key, hit/miss, source
(`memory`, `disk`, or `none`), no-expiry staleness fields, and snapshot hash.
When the CLI loads the built-in `deep_research` plugin, cache snapshots are
stored as JSON under `plugin_artifacts/deep_research/`; direct plugin
construction can choose `cached`, `live`, or `offline` cache modes and a custom
cache directory. Plugin artifact metadata summarizes those configured cache
snapshot files with counts, byte sizes, SHA-256 hashes, retention/skipped
counters, provider-result snapshot counts/hashes, payload-artifact
counts/bytes/hashes, and aggregate hashes.
Empty/error refreshes clear prompt-visible retrieval context; when a successful synthesis is active,
`metadata.plugin_context[*].metadata.active_context` records its generation,
event index, status, synthesis hash, and trust policy. DeepResearch also records
`metadata.plugin_context[*].metadata.retrieval_retention` with its configured
event limit, retained/emitted counts, total events, and dropped-event count.
Provider error text is redacted for common
secret patterns and truncated before metadata persistence. DeepResearch
provider-result snapshot and cached synthesis bodies follow
`retrieval_body_retention_mode`: `redacted` stores bounded secret-redacted text
by default, `full` stores secret-redacted full body text, `hash_only` stores
only hashes/counts, and `off` stores no body text or hashes. The modular plugin
uses the same prompt-context metadata field to record
`strategy_policy: static_prompt_only`,
`operation_selected: static_modular_guidance`, the described operation names,
and false `operation_executed` / `interface_enforced` flags. The record does
not yet include custom plugin package-registry provenance, constructor-schema
attribution beyond exposed `__version__` labels, unbounded full result
payloads, ranking provenance, source-content trust policy, or real selected
strategy operations.

Benchmark publication helpers use separate report schemas rather than making
smoke examples paper-comparable by default.
`libreevolve.matrix_result_report.v1` validates matrix target identity,
dimensions, best rank, seed count, best-rank hit fraction, coefficient domain,
exactness certificate status, per-seed exactness rows, and declared
algorithm/certificate/notebook artifact metadata.
`libreevolve.matrix_result_artifact_inventory.v1` verifies those declared
artifact paths against concrete files under an explicit artifact root: paths
must stay safe and relative, files must exist, and actual SHA-256 hashes and
byte counts must match the report. This inventory is publication evidence for
report artifacts, not a tensor-decomposition algorithm generator or proof that
the shipped smoke validator is AlphaEvolve-comparable.

`code` is the primary file content for backward compatibility. `files` contains
the full candidate file set for workspace candidates. When `files` is present,
the file set is canonical and `code` is derived from `files[primary_file]`.

`metadata.archive_admission.selection_score` records the score used for
MAP-Elites cell competition and elite/exploit ordering when present. Threshold
rejection still uses final top-level `fitness`, so plugin penalties and
feedback composition can invalidate candidates even when their declared metric
normalization remains high.

`evaluation` includes normalized fitness, validity, per-stage outcomes, stdout,
stderr, error, elapsed time, and metadata such as the primary file and file
list. Directly constructed or hook-mutated evaluator result objects are
revalidated before serialization, so non-finite numbers, non-string diagnostic
fields, unsafe metrics, malformed stage labels, and non-JSON-safe metadata are
rejected before they become prompt input or durable run evidence. Subprocess
metadata records the validator environment policy, provided
environment keys, and canonical allowlist names, but never environment values.
Timeout results also include `evaluation.metadata.timeout_cleanup` with the
attempted process-tree cleanup method and outcome. On Windows, validator
subprocesses are also assigned to a kill-on-close Job Object when supported;
`timeout_cleanup.job_object` records whether assignment was attempted,
accepted, closed, or failed before/alongside the `taskkill /T /F` fallback.
When Windows `taskkill /T /F` reports child PIDs it could not terminate,
`timeout_cleanup.reported_child_pids` and `timeout_cleanup.direct_child_kill`
record direct per-PID cleanup attempts with the same bounded diagnostic policy.
`evaluation.metadata.validator_boundary` declares this as
`local_subprocess_boundary_v1`: temporary local subprocess execution,
unsupported security sandbox/container, candidate-root plus declared
problem-file filesystem policy, the effective validator `network_policy`,
network egress/denial status, wall-clock-only timeout limits, unsupported
CPU/memory/GPU/disk/process-count limits, and a
minimal-environment/redacted-diagnostic secret boundary. This is still local
subprocess containment, not a full resource sandbox. Startup manifests also
persist `policies.validator_execution` with schema
`libreevolve.validator_execution_policy.v1`; it records the same configured
local-subprocess boundary before any evaluation row exists, including
unsupported sandbox/container status, candidate-root plus declared-problem-file
filesystem scope, the effective network policy, wall-clock-only timeout limits,
unsupported CPU/memory/GPU/disk/process-count quotas, the secret boundary, and
`per_evaluation_metadata: "evaluation.metadata.validator_boundary"`. Startup
manifests also persist the effective `config.validator_network_policy` and
`policies.validator_network`, so allowed host/deny modes and the remaining
OS/container network-sandbox gap are visible before individual evaluation
records are inspected. With
`validator_network_policy: host`, validator Python network APIs use the
inherited host network. With `validator_network_policy: deny`, preflight and
evaluation install a Python socket denial hook and record
`network_denial_scope: "python_socket_api_only_not_kernel_or_container"`.
Cleanup command stdout/stderr/error fields are redacted and truncated at 2,000
characters before persistence; `timeout_cleanup.output_policy` plus per-field
diagnostics record the policy, cap, stored length, omitted length, and whether
redaction/truncation occurred. Persisted validator stdout/stderr is captured as
bytes, decoded with explicit UTF-8 replacement, redacted with the shared
versioned secret-pattern grammar, then truncated to `evaluator_output_max_chars` characters before
storing it in result, stage, retry, sample, and history records. The default
validator-output cap is `20000`; `evaluation.metadata.diagnostic_output`
records the decode policy, byte counts, replacement counts,
malformed-stream flags, cap, stored length, omitted length, redaction, and
truncation flags. Validator standard input defaults to `subprocess.DEVNULL`;
`evaluation.metadata.stdin` records `policy: "devnull"` and
`interactive_input: "unsupported"` plus `generated_input: "unsupported"`.
Direct stdin reads therefore see EOF/empty input by default. Problem config may
set `evaluator_stdin_text`, `evaluator_stdin_file`, or per-stage `stdin_text` /
`stdin_file`, to pass bounded UTF-8 fixture input into validator stdin.
Configured fixture metadata records policy, byte and character counts, SHA-256
hashes, redaction status, `text_retained: false`, and problem-local source-file
provenance when applicable. Startup manifests record the same fixture-only
boundary under `policies.validator_stdin`, and
`manifest.json.config.evaluator_stdin` plus configured-stage `stdin` metadata
replace raw `evaluator_stdin_text`, `stdin_text`, and `stdin_file` values with
hash/count-only metadata. Generated and interactive stdin streams are
explicitly unsupported by the current fixture-only policy.
Malformed evaluator result contracts use `error: "malformed_metrics"` and add
`evaluation.metadata.malformed_metrics` with a bounded redacted message,
exception type, and reason such as `non_string_keys`,
`missing_declared_metrics`, `undeclared_metrics`, `invalid_metric_type`,
`invalid_is_valid`, `not_json_serializable`, or `non_mapping_result`.
Candidate workspace materialization failures, including host-specific
case-folded path collisions, are recorded as invalid evaluations with
`error: "materialization_error"` and bounded redacted diagnostics under
`evaluation.metadata.materialization_error`.
Prompt-visible summaries are bounded separately.
Use `evaluator_artifact_include` for large diagnostics that should be retained
as separate files with hashes. Metric schemas reject boolean bounds before run
artifacts are created. If scalar validator metrics fall outside declared
`metrics.yaml` bounds, `evaluation.metadata.metric_bound_diagnostics` records
the metric name, raw value, declared bounds, direction, and clamped normalized
value used for selection. If feedback graders are enabled, their
scores appear in `metrics`, and the composed score appears as
`feedback_adjusted_fitness`. Feedback scores, `weight`, and `min_score` are
bounded to finite `[0, 1]` values before composition. Successful feedback
records preserve raw `score`, configured `weight`, and composed
`weighted_delta`; `feedback_adjusted_fitness` is a top-level fitness and prompt
reward signal, while MAP-Elites `selection_score` continues to use declared
evaluator metrics. Feedback metric names must use the same
manifest-safe metric-name grammar as `metrics.yaml` and runtime
`Program.metrics`; they cannot use reserved fields such as
`feedback_adjusted_fitness` and cannot collide with evaluator metrics or
another feedback metric in the same grader list. Collisions are recorded as
`invalid_feedback_config` before provider calls. Feedback grader outcomes are stored in
`evaluation.metadata.llm_feedback`; provider `raw_response` and parsed
`feedback` fields in those records follow `feedback_retention_mode`, with
`raw_response_retention` / `feedback_retention` metadata recording the selected
mode, retention policy, original text hash when enabled, original/stored
character counts, configured cap, and redaction/truncation flags. Each applied feedback
grader also appends an `llm_feedback:<name>` stage with pass/fail, score,
elapsed time, `llm_feedback_failed` or `llm_feedback_discard` errors when
applicable, and `metadata.kind="llm_feedback"` plus the feedback record index,
metric, backend id, discard flag, min score, weight, and normalized LLM call
provenance. Feedback `llm_call` telemetry from direct/custom LLM objects is
normalized before storage: keys are converted to bounded strings, secret-like
text is redacted, unknown objects and non-finite floats become typed
strict-JSON-safe values, long strings/containers are capped, oversized call
records are replaced with a bounded preview, and `telemetry_safety` records the
redaction/truncation/stringification/omission policy. Feedback graders run in
configured order: once a candidate is invalid, whether from evaluator failure
or an earlier feedback discard, later graders are skipped unless
`include_invalid: true`; skipped graders are recorded with
`llm_feedback_skipped_invalid` feedback records and stages without provider
calls. Feedback grader failures can be retried with `failure_retries` up to
`3`. After retries are exhausted, `failure_policy` controls the experiment
effect: `ignore` records the failure without changing fitness or validity,
`penalize` subtracts `failure_penalty` from fitness and records
`failure_delta`, and `discard` marks the candidate invalid. Each exhausted
failure record stores the policy, retry count, attempt records, final
exception/message, redacted bounded response preview, backend id, normalized
LLM call telemetry, and discard/penalty decision; the corresponding
`llm_feedback:<name>` stage stores
the same policy summary under metadata. Runtime
`Program.metrics` keys must match the same manifest-safe
metric-name grammar as declared `metrics.yaml` names, including optional dotted
namespaces. Unsafe plugin-added metric side effects are reverted and recorded
as `invalid_plugin_metrics` in `metadata.score_composition.plugins[]`.
Configured evaluator retry attempts are stored under
`evaluation.metadata.attempts`; each attempt record includes attempt index,
pass/fail status, fitness, metrics, stdout, stderr, error, elapsed time, stage
context, and per-stage diagnostics. The selected attempt still determines the
sample/stage result. Stage `timeout_sec` applies to each such subprocess
attempt. Configured stages can additionally set `max_sample_seconds` as a
per-sample wall-clock budget and `max_stage_seconds` as a stage-level
wall-clock budget; attempts are clipped to the smallest remaining budget, later
retries/samples are skipped after exhaustion, and budget stops are recorded as
`sample_budget_exhausted` or `stage_budget_exhausted` with
`metadata.sample_budget` / `metadata.stage_budget` describing the policy,
configured seconds, elapsed time, remaining time, and exhausted state.
Every structured evaluation also includes `evaluation.accounting` with schema
`evaluator_accounting_v1`, summarizing subprocess attempts, configured-stage
samples, retry attempts, validator timeouts, and sample/stage budget
exhaustions. The same counters are accumulated into
`metadata.budget.consumed` for candidate history rows and
`manifest.runtime.consumed` at finalization. The terminal history row that
consumes a configured evaluation or detailed evaluator-counter limit records
the exhausted `metadata.budget.stop_reason`; final manifests remain the
authoritative summary for completed and aborted run status.
Configured stage retry counts are capped at `10`, so a stage can request at
most `samples * 11` subprocess attempts before early success/stop.
When a stage has `min_score` or `metric_thresholds`, retry selection is
threshold-aware: valid attempts below minimum thresholds or above maximum
thresholds are retained in `evaluation.metadata.attempts` and can be retried.
Each attempt record stores `local_valid`, legacy score `threshold`, full
`threshold_result` including per-metric checks, `threshold_passed`, and final
`passed` separately.
Configured stage seeds are recorded as `stage.seed`. For non-null seeds,
LibreEvolve records a derived 32-bit `stage.rng_seed`, sets
`PYTHONHASHSEED` in the validator subprocess environment, and seeds Python
`random` plus NumPy before validator import. `validator_env.provided_keys`
therefore includes `PYTHONHASHSEED` for seeded stage attempts.
For multi-sample stages, `evaluation.metadata.samples` stores each selected
sample result. Aggregate metrics use fixed defaults unless
`metric_aggregation` overrides a metric: numeric values use `mean`, boolean
values use `all`, and other values use `last`. Numeric metrics can also use
`min`, `max`, `last`, or `{policy: quantile, q: <0..1>}`; boolean metrics can
also use `any`. Quantiles use deterministic linear interpolation over sorted
sample values, and the normalized aggregation policy is persisted under
`evaluation.metadata.metric_aggregation`. If any selected sample is invalid,
top-level `evaluation.is_valid` is false and fitness is penalized even when
averaged raw metrics remain high. If a stage passes locally but fails
`min_score` or `metric_thresholds`, the enclosing evaluation is marked invalid
with `stage_threshold_not_met` after threshold-aware retries are exhausted; the
local stage row can still show `passed: true` because the validator subprocess
itself returned valid output.
Configured stages can also require evaluator evidence. `require_program_output`
adds an artifact/output check that passes only when `program_outputs.value` is
retained rather than missing or omitted, and `min_artifacts` checks the count of
copied evaluator artifact file records across the selected result.
`program_output_checks` records `program_output_equals` checks with path,
expected value, actual value, and reason, while `required_artifacts` records one
`required_artifact` check per required artifact glob.
Configured cascades also write
`evaluation.metadata.configured_stage_results[]`, preserving each configured
stage's selected result even when a later stage passes. Each record includes
stage name/index, local validity, legacy score threshold, full
`threshold_result` with per-metric and artifact/output checks, pass/stop
decision, metrics, elapsed time, stdout/stderr/error, flattened stage rows, and
that stage's own metadata such as metric aggregation policy, retry attempts,
sample aggregates, copied artifact records, validator environment, and stage
policy. The top-level
`evaluation.metadata.stage` and `evaluation.metadata.artifacts` entries remain
the compatibility view for the selected final stage or the stage where the
cascade stopped.
Evaluator-returned structured program outputs are stored as first-class
evaluation metadata when `evaluate()` returns the reserved `outputs` or
`program_output` key beside declared scalar metrics plus boolean `is_valid`.
The evaluator validates these attachments as strict JSON before subprocess
transport, redacts common secret patterns, records `source_key`, `json_chars`,
`max_json_chars`, `sha256`, redaction state, and omission state under
`evaluation.metadata.program_outputs`, and persists inline `value` only when
the redacted JSON is at or below the 4,000-character cap. Larger outputs keep a
bounded `preview` plus digest instead of the full value. Prompt feedback renders
a bounded `[program outputs]` summary from that metadata. Other undeclared
return keys remain malformed metrics.

Validator-generated files are collected only when
`evaluator_artifact_include` is configured. Matching candidate-workspace files
are copied to `evaluator_artifacts/<collection_id>/...` before the temporary
workspace is deleted. Each copied artifact record in
`evaluation.metadata.artifacts.files` includes the original relative path,
stored artifact path, stored byte count, source byte count, SHA-256 hash of the
stored content, redaction flag/status, stage name, sample index, and attempt.
UTF-8 copied artifacts also include a bounded `content_excerpt` under
`stored_utf8_artifact_excerpt_v1` metadata after any configured redaction;
binary or non-UTF-8 artifacts record
`content_excerpt_status: binary_or_non_utf8` and no excerpt text.
The collection metadata also records the effective include/exclude patterns,
redaction policy, max-file and max-byte limits, skipped files, total copied
bytes, and collection id. UTF-8 text artifacts receive the shared versioned
secret-pattern grammar by default; binary or non-UTF-8 artifacts are copied raw. Artifact
include/exclude patterns are validated as display-safe glob strings and reject
Unicode format controls before they can be persisted in manifests or artifact
metadata; secret-like selector text is rejected rather than retained raw as
run configuration. Selectors are workspace-relative POSIX patterns: traversal
components, dot/empty path components, absolute or drive-style roots, leading
backslashes, and Windows backslashes are rejected. Matching is
path-segment aware over candidate-relative POSIX paths: `*.txt` matches only
root files, `reports/*.json` matches one segment under `reports/`, and
`**/*.txt` recursively matches root and nested files. The same top-level
artifact pattern, limit, and redaction-flag validation runs for direct
`CascadeEvaluator` construction before any validator subprocess can create
artifact metadata. Matched symlinks are skipped with
`reason: link_not_followed` before target resolution or reads, and regular
artifact source sizes are checked against the remaining `max_bytes` budget
before file bytes are read. Copied file records expose `artifact_path` with
`artifact_path_root: "artifact_dir_parent"` for the existing run-relative view,
plus `artifact_relative_path` for paths rooted directly at the configured
artifact directory.
`eval_stages[]` can override the top-level artifact policy for that stage.
Non-matching files and files written outside the candidate workspace are not
retained.

Plugin `on_evaluated()` hooks can also modify the final top-level `fitness`.
That score-composition path is stored under `metadata.score_composition` with
evaluator fitness, optional feedback-adjusted fitness, per-plugin before/after
scores, metric additions/changes, metadata additions/changes, invalid score
or side-effect rejections, runtime plugin identity (`plugin`, `module`,
`class`, `index`, `instance_id`, plus hash fields when labels were redacted),
final fitness, and whether the final score
diverged from `evaluation.fitness`. Plugin-added metrics must remain finite
manifest-safe metric values, and plugin-added metadata must remain JSON-safe
finite metadata with display-safe labels. Unsafe side effects are reverted and
recorded as `invalid_plugin_metrics` or `invalid_plugin_metadata` with bounded
redacted diagnostics before archive admission/history logging. Archive
admission uses the final top-level fitness threshold but remains gated by
`evaluation.is_valid`, so plugin score changes do not accidentally archive
evaluator-invalid candidates. MAP-Elites cell replacement, elite ordering, and
parent sampling continue to use `metadata.selection_score`, computed from
declared objective metrics before plugin hooks, including feedback-sourced
objective metrics after their graders fill them; plugin-adjusted top-level
fitness is logged and used for threshold/prompt/backend reward policy, not
archive ranking.

Archive state is only partially serialized. `history.jsonl` contains evaluated
candidates and per-candidate archive admission events, `archive_events.jsonl`
contains versioned migration placement events, and the run manifest records
canonical-id migration policy plus final archive cursor state and per-island
MAP-Elites cell/elite snapshots plus bounded Pareto-frontier archive ids over
complete declared normalized metric vectors. Those snapshots are restore inputs for
`ProgramDatabase`, direct `evolve()` calls, and CLI runs when paired with
checked accepted-history `Program` snapshots. They still do not provide
restore-ready ordered migration replay, controller queues, pending-work state,
or descriptor-normalization replay.
`load_archive_event_records()` validates the archive event stream for future
query/replay use, including migration sequence ordering, canonical-id policy,
manifest-safe program ids, island ids, cell coordinates, and finite/null
selection scores. It does not apply those events back into an archive.
`metadata.archive_admission` records threshold rejection, island id, cell
coordinates, descriptor values, previous occupant id, cell replacement status,
elite-list entry, displaced elite ids, and Pareto-frontier retention fields for
each program.
`archive_contents[].descriptor_axes`, `descriptor_policy.axes`, and
`descriptor_model.axes` record the configured MAP-Elites descriptor axes.
MAP-Elites defaults to performance, serialized-workspace complexity, and
adaptive TF-IDF diversity, but configured axes can also read normalized metrics,
numeric evaluator metadata, or numeric candidate metadata. Complexity uses the
configured `map_elites_complexity_max_chars` bound over serialized workspace
text. Diversity uses adaptive TF-IDF character n-grams up to length 4 against
the current capped elite corpus. Existing cells are not rebinned when that
diversity reference corpus changes. `objective_archive_policy` records the
bounded non-dominated Pareto retention policy, declared metric order, complete
normalized-vector requirement, and the fact that MAP-Elites cell replacement
still uses scalar selection score rather than Pareto dominance.
Rejected non-admitted candidates also leave the island assignment cursor on the
same island for the next retained archive-state change. The final runtime
archive-state snapshot records that cursor for inspection and restore. Full
cell/elite restore is available from archive snapshots plus checked accepted
history, but ordered migration-event replay and controller/pending-work resume
remain future work.
Rejected admission events use finite JSON-safe diagnostic fields, but malformed
top-level candidate records can still be quarantined by strict history logging.

## `prompt_history.jsonl`

This file records prompt-program events:

- `add`: a seed or mutated prompt template entered the prompt database
- `score`: a prompt template was used for a candidate and received reward
- `penalty`: an invalid meta-prompt mutation was rejected and penalized its
  parent prompt program

It is an append-only prompt-archive stream. When `PromptDatabase` starts with a
non-empty `prompt_history.jsonl`, it replays accepted `add`, `score`, and
`penalty` rows before seeding configured templates, restoring prompt ids,
lineage, uses, reward sums, metadata, invalid-mutation penalties, and
selection state. Replay validates row schemas, parent references, immutable
template/lineage fields, template hashes, context-policy hashes, mean rewards,
monotonic counters, and reward-policy compatibility. Whole-run resume still depends on separate
archive/controller, restored-RNG integration, candidate-id, and provider-output
restore work.

Prompt templates are validated for known simple placeholders and dry-run
rendered with representative prompt values before entering the prompt database
or being used. Incompatible format specs, such as applying a float format code
to the string `task` field, are rejected before mutation prompts render.
`PromptProgram` construction and state revalidation use the same template
validator, so selected/scored prompt-program records cannot represent
non-string or syntactically invalid templates as valid archive state.
Prompt programs also persist `context_policy` with schema
`libreevolve.prompt_context_policy.v1` plus `context_policy_sha256`. The policy
can disable optional prompt-rendering channels, override section priorities
used by prompt packing, and select the safe enum-valued
`mutation_instruction_variant` used to render mutation-format instructions.
`mutation_instruction_include_example` can keep or remove the built-in
mutation-format example block while preserving the core format rules.
`proposal_metadata_enabled` can override whether proposal metadata
instructions and downstream parsing run for that prompt arm; `null` preserves
the run-level `capture_proposal_metadata` setting. It can
also set `feedback_sections`, a validated allowlist over bounded
parent-feedback subsections such as stage summaries, execution output,
validator diagnostics/artifacts, program outputs, proposal metadata, and LLM
grader feedback. `feedback_section_order` can deterministically reorder those
rendered parent-feedback subsections while appending unspecified sections in
the safe default order. `feedback_section_max_chars_by_name` can suppress or
cap individual feedback subsections before the final aggregate feedback cap.
`inspiration_strategy` can override the upstream inspiration
sampling strategy for that prompt program using the same safe strategy enum as
config, and generated-candidate metadata records whether the strategy came
from config or prompt context policy. `inspiration_sample_count` can override
how many inspirations are sampled upstream before plugin context and prompt
rendering, and candidate metadata records whether the requested count came
from config or prompt context policy. `inspiration_required_metric` can filter
the upstream inspiration pool to programs carrying a manifest-safe metric name
before plugin context and prompt rendering; candidate metadata records the
pool size, matching count, filtered count, selected ids, and policy source.
`inspiration_excluded_metrics` can filter out upstream inspirations carrying
any listed manifest-safe metric names before plugin context and prompt
rendering; candidate metadata records the exclusion list, matching count,
filtered count, selected ids, and policy source.
`inspiration_fitness_threshold` can filter upstream inspirations by finite
fitness min/max bounds before plugin context and prompt rendering; candidate
metadata records the normalized bounds, matching count, filtered count,
selected ids, and policy source.
`inspiration_metric_thresholds` can require numeric inspiration metrics to
satisfy safe min/max bounds before plugin context and prompt rendering;
candidate metadata records normalized threshold bounds, matching count,
filtered count, selected ids, and policy source.
`inspiration_metric_ranking` can rank the upstream pool by a numeric metric in
`maximize` or `minimize` order before final inspiration selection; candidate
metadata records the ranking policy, candidate count, selected ids, and policy
source.
`llm_feedback_fields` can further select which safe
LLM-grader fields render inside that section, and
`llm_feedback_max_chars_by_field` can cap or suppress those selected
LLM-grader fields before rendering. `proposal_fields` can select safe
fields inside proposal metadata feedback, and `proposal_max_chars_by_field`
can cap or suppress those proposal fields before rendering. `stage_summary_fields` can
select safe fields inside stage-summary feedback, and
`stage_summary_max_chars_by_field` can cap or suppress those stage-summary
fields before rendering. `execution_output_fields`
can select safe fields inside execution-output feedback and stage-summary IO
lines. `execution_output_max_chars_by_field` can cap or suppress `stdout`,
`stderr`, and `error` text independently before those fields are rendered.
`sample_retry_fields` can
select safe fields inside sample/retry diagnostics.
`sample_retry_max_chars_by_field` can cap or suppress selected sample/retry
diagnostic text fields before rendering. `program_output_fields` can
select safe fields inside program-output feedback.
`program_output_max_chars_by_field` can cap or suppress selected
program-output text fields before rendering. `validator_artifact_fields`
can select safe fields inside validator-artifact feedback, and
`validator_artifact_content_fields` can select nested bounded artifact-content
fields when artifact content rendering is enabled.
`validator_artifact_max_chars_by_field` can cap or suppress selected
validator-artifact text fields before rendering.
`validator_artifact_content_mode`, `validator_artifact_content_max_bytes`, and
`validator_artifact_content_max_chars` can override the configured
artifact-content rendering policy for that prompt program.
`validator_skipped_artifact_fields` can select safe fields inside skipped
artifact diagnostics, and `validator_skipped_artifact_max_chars_by_field` can
cap or suppress selected skipped-artifact text fields before rendering.
`validator_diagnostic_groups`
can select which bounded validator diagnostic groups render inside validator
diagnostics, and `validator_metadata_keys` can select safe keys inside the
validator metadata summary. `validator_metadata_limit` can cap or suppress the
number of metadata-summary items before rendering.
`validator_metadata_max_chars_by_key` can cap or
suppress selected validator metadata summary values before rendering.
`syntax_error_fields` can select safe fields
inside syntax-error diagnostics, and `syntax_error_max_chars_by_field` can cap
or suppress selected syntax-error text fields before rendering.
`metric_bound_fields` can select safe fields inside metric-bound diagnostics,
and `metric_bound_max_chars_by_field` can cap or suppress selected metric-bound
text fields before rendering. `configured_stage_check_fields` can
select safe fields inside configured-stage check diagnostics, and
`configured_stage_check_max_chars_by_field` can cap or suppress selected
configured-stage text fields before rendering.
`stage_metric_threshold_fields` and `artifact_output_check_fields` can select
nested fields inside configured-stage metric-threshold and artifact-output
checks. `stage_metric_threshold_max_chars_by_field` can cap or suppress
selected nested metric-threshold text fields before rendering, and
`artifact_output_check_max_chars_by_field` can cap or suppress selected nested
artifact-output check text fields before rendering.
`evaluator_path_fields` can select safe validator path provenance fields, and
`evaluator_path_max_chars_by_field` can cap or suppress selected path fields
before rendering. `evaluator_dependency_fields` can select safe validator
dependency-policy fields, including derived file paths, hashes, and redaction
flags, and `evaluator_dependency_max_chars_by_field` can cap or suppress
selected dependency fields before rendering. `evaluator_stage_fields` can
select safe derived stage-context fields, and
`evaluator_stage_max_chars_by_field` can cap or suppress selected stage fields
before rendering. `evaluator_workspace_fields` can select safe evaluated
workspace provenance fields, including primary file, file count, and bounded
file list, and `evaluator_workspace_max_chars_by_field` can cap or suppress
selected workspace fields before rendering.
`malformed_metric_fields` can select safe fields inside malformed-metric
diagnostics. `malformed_metric_max_chars_by_field` can cap or suppress selected
malformed-metric text fields before rendering. `metric_aggregation_fields` can
select safe fields inside metric-aggregation diagnostics, and
`metric_aggregation_max_chars_by_field` can cap or suppress selected
metric-aggregation text fields before rendering. `synthetic_metric_fields` can
select safe fields inside synthetic failure-metric diagnostics, and
`synthetic_metric_max_chars_by_field` can cap or suppress selected synthetic
metric text fields before rendering. `materialization_error_fields` can select
safe fields inside materialization-error diagnostics, and
`materialization_error_max_chars_by_field` can cap or suppress selected
materialization-error text fields before rendering. `validator_boundary_fields` can select safe
fields inside validator-boundary diagnostics, and
`validator_boundary_max_chars_by_field` can cap or suppress selected
validator-boundary text fields before rendering.
`validator_resource_limit_fields` can select nested resource-limit fields
inside that boundary diagnostic. `validator_resource_limit_max_chars_by_field`
can cap or suppress selected nested resource-limit text fields before
rendering. `validator_budget_fields` can select stage/sample budget diagnostic
fields inside execution diagnostics, and
`validator_budget_max_chars_by_field` can cap or suppress selected budget
fields before rendering. `validator_env_fields` can select value-free
validator environment diagnostic fields, and
`validator_env_max_chars_by_field` can cap or suppress selected environment
fields before rendering. `execution_diagnostic_groups` can
select safe execution-diagnostic subgroups before subgroup field allowlists are
applied. `validator_stdin_fields` can
select safe fields inside validator-stdin diagnostics, and
`validator_stdin_max_chars_by_field` can cap or suppress selected
validator-stdin text fields before rendering. `diagnostic_output_fields`
can select safe fields inside diagnostic-output diagnostics, and
`diagnostic_output_max_chars_by_field` can cap or suppress selected
diagnostic-output text fields before rendering.
`timeout_cleanup_fields` can select safe fields inside timeout-cleanup
diagnostics, and `timeout_cleanup_max_chars_by_field` can cap or suppress
selected timeout-cleanup text fields before rendering.
`prompt_format_weights` can override configured stochastic prompt-format
alternative weights for safe
configured markers, and accepted prompt diagnostics record whether selected
weights came from config or prompt context policy. `context_source_paths` can
select and order already-loaded local context sources by safe problem-relative
path; prompt metadata records the selected order plus missing and omitted
policy paths. `context_source_max_chars` can cap rendered text for each
selected local context source; prompt metadata records original, rendered, and
omitted character counts per source. `context_source_truncation` can choose
deterministic `head` or `head_tail` truncation under that cap.
`context_source_order_policy` can keep the selected source order or rank
selected sources by deterministic task-term overlap against rendered source
text; prompt metadata records candidate count, selected count, scores, query
source, query-term hash/count, configured terms when present, and ranking hash.
`context_source_ranking_terms` can provide explicit safe ranking terms instead
of deriving them from the task description. `context_source_required_terms` can keep
only sources whose loaded content contains every listed safe term, and
`context_source_excluded_terms` can omit sources whose loaded content contains
any listed safe term before ranking and limiting; prompt metadata records
required/excluded terms, omitted paths, match/filter counts, and a selection
hash. `context_source_limit` can cap how many
ordered local context sources render after path selection and ranking,
including `0` to suppress them for a prompt arm; prompt metadata records the
pre-limit order, omitted paths, selected count, omitted count, and a selection
hash when the limit is configured.
`recent_failure_limit`
can cap rendered recent failure-memory records, including `0` to suppress that
block; prompt diagnostics record the limit, available count, rendered count,
omitted count, field caps, and selection policy.
`recent_failure_selection_policy` can choose `recent`, `oldest`,
`lowest_score`, or `highest_repetition` retained failure-memory records before
that render cap is applied; prompt diagnostics record both the configured
selector and selection semantics. `recent_failure_required_errors` can filter retained failure-memory
records by exact safe `error` or `diff_error` labels before selection and
limiting; prompt diagnostics record the required labels, match count, filtered
count, and filter policy. `recent_failure_excluded_errors` can omit retained
failure-memory records carrying exact safe `error` or `diff_error` labels
before score filtering, selection, and limiting; prompt diagnostics record the
excluded labels, filtered count, and policy. `recent_failure_required_changed_files`
can filter retained failure-memory by safe exact `changed_files` paths before
score filtering, selection, and limiting; prompt diagnostics record the
required paths, matched count, filtered count, and policy.
`recent_failure_excluded_changed_files` can omit retained failure-memory
carrying safe exact `changed_files` paths before score filtering, selection,
and limiting; prompt diagnostics record the excluded paths, filtered count,
and policy. `recent_failure_required_stage_names` can filter retained
failure-memory by safe exact evaluation stage names, and
`recent_failure_excluded_stage_names` can omit retained failure-memory carrying
safe exact evaluation stage names before repetition/score filtering, selection,
and limiting; prompt diagnostics record required/excluded stage names, match
counts, filtered counts, and policies. `recent_failure_required_terms` and
`recent_failure_excluded_terms` can filter retained failure-memory by safe text
terms in the failure evidence before repetition/score filtering, selection,
and limiting; prompt diagnostics record configured terms, match/filter counts,
and policies when either term list is configured. `recent_failure_repetition_threshold` can filter retained
failure-memory by integer `repetition_count` `min`/`max` bounds before score
filtering, selection, and limiting; prompt diagnostics record normalized
bounds, match count, filtered count, and policy.
`recent_failure_score_threshold` can filter retained
failure-memory by finite score `min`/`max` bounds before selection and
limiting; prompt diagnostics record normalized bounds, match count, filtered
count, and filter policy. `recent_failure_max_chars_by_field` can cap or
suppress selected recent failure-memory fields before rendering. `inspiration_limit` can cap rendered
selected inspirations, including `0` to render none; prompt diagnostics record
the same count and selection-policy fields for inspiration rendering. This
render cap is separate from upstream `inspiration_sample_count` and
`inspiration_required_metric`/`inspiration_metric_thresholds`/
`inspiration_metric_ranking`.
`extra_context_max_chars` can cap already validated/redacted plugin
`extra_context` text before rendering; prompt diagnostics record input,
rendered, and omitted character counts plus whether the policy truncated the
text. `plugin_context_enabled: false` can suppress plugin
`build_extra_context()` and `prompt_context_metadata()` calls for the selected
prompt arm while preserving per-plugin identity/spec provenance with
`context_visibility: disabled_by_prompt_context_policy`.
`plugin_context_excluded_labels` can omit selected plugin identity labels
before prompt-context hooks run; skipped plugin records include
`context_visibility: excluded_by_prompt_context_labels` and the configured
excluded-label policy.
`plugin_context_order` can reorder selected plugin prompt-context sections by
safe plugin identity labels before aggregate prompt packing; emitted plugin
records include the configured order, source, and matched position.
`plugin_context_required_terms` and `plugin_context_excluded_terms` can filter
bounded plugin context text before prompt visibility; plugin records include
required/excluded terms, missing required terms, matched excluded terms,
selection status, and a selection hash when the term policy is configured.
`plugin_context_ranking_terms` can rank prompt-visible plugin context sections
by deterministic term overlap before render-count limiting; plugin records
include configured ranking terms, term hash/count, score, rank, previous rank,
candidate count, and ranking hash when ranking is configured.
`plugin_context_limit` can cap how many ordered plugin context sections become
prompt-visible after allowlist, term filtering, and ordering; plugin records
include source limit, pre-limit count, selected/omitted counts, rank, selected
status, and a selection hash when the limit is configured.
`plugin_context_max_chars` can globally cap each plugin context section before
prompt visibility; plugin records include the global policy cap, per-label cap,
effective cap, original character count, and prompt truncation status.
Score and penalty replay rejects rows that change the policy after the `add`
event.
Configured prompt seeds also record
`config.prompt_variant_semantic_policy`; the default `alphaevolve` policy
requires task, parent code/workspace, mutation instructions, evaluator-feedback,
and context/inspiration channels before templates enter the prompt database.
The explicit `compatibility` policy admits minimal externally managed templates
while preserving the same renderability checks.
Mutated prompt templates must also retain every placeholder used by their
parent prompt program; semantic regressions that drop code, feedback,
inspiration, or mutation-format channels are written to
`prompt_history_invalid.jsonl` and penalize the parent prompt arm.

Score events store prompt-program reward telemetry in
`program.metadata.last_prompt_reward`: reward mode, raw reward, normalized
reward, and normalization bounds. In `absolute` mode the raw reward is the final
composed candidate score; in `improvement` mode it is child score minus parent
score. Score metadata is validated before prompt-arm counters mutate; invalid
metadata writes a bounded quarantine diagnostic to
`prompt_history_invalid.jsonl` and leaves `uses`, `reward_sum`, metadata, and
selection order unchanged. Accepted score metadata is recursively
strict-JSON-normalized, secret-redacted, and string-bounded before persistence.
Metadata keys that are redacted or truncated carry a short SHA-256 suffix so
the stored label remains stable without preserving the raw key.
Penalty events treat an invalid prompt child as one use of the parent prompt
arm with the configured lower-bound reward normalized through the same prompt
reward policy as score events. The parent prompt program records
`program.metadata.last_prompt_penalty` with mode, raw lower-bound reward,
normalized reward, bounds, generation, and error, and the updated `uses`,
`reward_sum`, and `mean_reward` fields are persisted in the penalty event.

Rejected meta-prompt mutations are written to `prompt_history_invalid.jsonl`
with the parent prompt id, generation, bounded/redacted rejected-template
preview, template raw character count, SHA-256 hash, redaction/truncation
flags, error, and metadata.
If a rejection record itself is not strict JSON-serializable, a diagnostic
quarantine row is written instead and the parent prompt program is not
penalized.

Successful LLM-generated prompt children include
`program.metadata.mutation_context` with schema
`meta_prompt_mutation_context_v1`, the included section names, selected/latest
program ids, and `evidence_retention` metadata. By default,
`meta_prompt_evidence_retention_mode="hash_only"` stores no evidence text and
keeps only raw-evidence and prompt-visible evidence hashes/counts. `full` and
`redacted` persist bounded secret-redacted evidence under
`mutation_context.evidence`; `off` suppresses evidence text, hashes, and
lengths. The evidence renderer also redacts/bounds dynamic dictionary keys,
including metric and score-composition labels; changed keys include short
SHA-256 suffixes for stable comparison. The same metadata also records
`current_template.sha256`, raw character count, prompt-visible character count,
redaction/truncation flags, and the enforced template character limit. The
prompt-visible evidence block contains reward policy, selected prompt
statistics, latest candidate outcome, prompt-arm summaries, and recent failure
summaries. The current template section sent to the meta-prompt backend is
secret-redacted and capped, with a separate placeholder list rendered before
it so truncation does not hide the required format fields.
Meta-prompt provider output remains backward compatible with plain revised
template text. If the output is a strict JSON object with schema
`libreevolve.prompt_mutation_response.v1`, `template`, and optional
`context_policy`, the accepted child prompt records both the revised template
and revised context policy; mutation metadata records the parsed response
format and policy source.

Dangling prompt-program references supplied to prompt scoring, mutation, or
direct add parent ids are also written to `prompt_history_invalid.jsonl` as
`prompt_reference_error` rows. Duplicate direct add ids use the same invalid
stream. Those records include the operation, redacted prompt id, error, and
bounded parent id, reward, generation, template, or metadata context when
supplied.

Generated program records in `history.jsonl` include
`metadata.prompt_program_id` so they can be traced back to the prompt program
that produced them. Generated rows also include
`metadata.prompt_diagnostics.prompt_context_policy` with the applied policy
hash, disabled sections, priority overrides, LLM-grader feedback fields,
validator diagnostic groups, validator metadata keys, recent failure-memory
limit, syntax-error fields, inspiration limit, context source content cap,
plugin extra-context cap, and replacement hashes for disabled optional
channels. Seed rows are not
prompt-produced; they use
`metadata.candidate_type = seed` and the raw-baseline post-processing policy
described above instead of a prompt-program id.

## `failure_history.jsonl`

This append-only stream records failed or rejected mutations and rejected seed
evaluations. Each record includes:

- `program_id`, `parent_id`, and `generation`
- final failed score and validity
- archive admission reason and metadata when the failure was evaluated against
  the archive admission policy
- evaluator `error` and mutation `diff_error`; duplicate SEARCH matches are
  reported as `ambiguous_search_match` rather than silently applying the first
  occurrence
- materialization failures reported by the evaluator as
  `materialization_error`, including bounded diagnostics copied from the
  candidate evaluation
- topology mutation diagnostics such as `unexpected_command_body` or
  `primary:duplicate_primary_section` when command file sections are ambiguous
  before workspace mutation
- `primary_deleted_requires_primary` when a topology mutation deletes the
  current primary file without an explicit replacement primary
- changed file paths and file-delta kinds
- bounded mutation text
- compact evaluator stdout/stderr/stage summaries. Malformed stage containers
  are recorded with `evaluation.stages_diagnostic` instead of aborting failure
  persistence.
- `failure_fingerprint` and `repetition_count` for repeated failures with the
  same parent, diff/evaluator error, full mutation payload, changed files, and
  file-delta shape

`program_id` values in `failure_history.jsonl` are run-local unique within the
failure stream. The same candidate id can also appear in `history.jsonl` for
the evaluated candidate record. Repeated failure patterns therefore use
distinct failed candidate ids with shared `failure_fingerprint` values and
increasing `repetition_count`; duplicate failed ids are quarantined in
`failure_history_invalid.jsonl`.

Rejected seed rows use `record_type: "seed"`, `parent_id: null`, file deltas
marked as `seed`, seed-source fields copied from the seed program metadata,
and an `admission_reason` copied from archive admission. Workspace seed rows
render every seed file in deterministic path order into bounded `mutation_text`
and include `seed_workspace` metadata with the primary file, file count, and
per-file path, primary/support role, byte count, SHA-256, bounded snippet, and
snippet-truncation flag.
When a valid parent exists, recent rejected seed records can appear in the
first mutation prompt's failure-memory section.
Failure-history repetition counters and `metadata.failure_record` mirrors are
updated only after the strict JSONL append succeeds; rejected failure records
go to `failure_history_invalid.jsonl` without advancing in-memory failed-trial
state.

The evolution loop renders a bounded recent tail of these records into later
prompts, including compact evaluator error/stdout/stderr and recent stage
summaries when present. The file is queryable as JSONL, but there is not yet a
scored long-term retrieval policy over all historical failures.
Accepted failure-history records bound and redact persisted mutation snippets,
seed snippets, evaluator summaries, changed paths, and error strings. Non-text
mutation payloads are stored as bounded textual representations with
`mutation_payload_type`, `mutation_payload_text`, and `mutation_sha256`
evidence. `load_failure_history_records()` is the checked replay/query reader
for this stream: it rejects unsafe or duplicate failed ids, invalid generation,
unsafe changed-file/file-delta paths, malformed mutation SHA-256 fields,
inconsistent mutation-payload text/type metadata, and inconsistent
`failure_fingerprint` links. Non-text payload rows are retained for query and
prompt-memory analysis, but restored records are annotated with
`mutation_payload_replay.policy = diagnostic_only_do_not_reapply` because
`mutation_text` is a bounded/redacted diagnostic snippet, not an exact payload
for resume-time reapplication. Retention policy and richer long-term query
controls remain open work.

Prompt feedback for the selected parent also renders bounded, redacted
summaries from the candidate's persisted evaluation record: recent stage
status, stdout/stderr, retry/sample attempts, and LLM grader feedback. It also
renders bounded/redacted evaluator artifact path/hash summaries, skipped
artifact diagnostics, aggregate syntax diagnostics, metric-bound clamp
diagnostics, malformed metric diagnostics, and sample aggregation
counts/policies. It also renders bounded validator execution details when
present, including `validator_boundary`, stdin policy, diagnostic-output
decode/cap/redaction metadata, resource-limit policy, and timeout-cleanup
context. Configured-stage `threshold_result`, metric-threshold checks, and
artifact/output checks are rendered as compact prompt diagnostics when present.
JSON-safe validator metadata keys not already covered by specialized renderers
are also rendered through a bounded `validator_metadata` fallback with
deterministic key ordering, stable JSON serialization, value hashes, and
omission counts.
For copied UTF-8 artifacts, prompt rendering includes the bounded stored
`content_excerpt` by default. When `prompt_artifact_content_mode:
bounded_file`, runtime prompts can also reopen copied artifacts under the run
directory, read at most `prompt_artifact_content_max_bytes`, redact secret-like
text, and render at most `prompt_artifact_content_max_chars`; absolute paths,
path escapes, links, missing files, oversized files, and binary/non-UTF-8
content are reported with `artifact_content_status` instead of being rendered.
Dynamic proposal, evaluator, retry, artifact, diagnostic, and
LLM grader-feedback fields render as JSON strings after redaction/truncation so
delimiter-like text is prompt data, not a new prompt section. These sections
are governed by a deterministic section-priority packer when `prompt_max_chars`
or `prompt_max_estimated_tokens` is set: oversized optional string sections are
omitted by priority before the final rendered mutation prompt is capped by the
effective character budget. Generated program metadata
records `prompt_diagnostics` with original length, rendered length, estimated
tokens, truncation status, strategy, deterministic context ordering metadata,
the rendered prompt SHA-256 hash, and `section_budget`. The section-budget
record has schema
`libreevolve.prompt_section_budget.v1` and stores per-placeholder section
priorities, hashes, character counts, estimated tokens, required/optional
totals, template overhead, a `required_sections_fit` flag, and
`packing.decisions` for omitted optional sections. Its policy is
`deterministic_section_priority_packing_heuristic_token_estimates_final_prompt_cap`;
it is still character-budget packing with heuristic token estimates, not
provider-token context-window fitting.
The configured `prompt_max_chars` and `prompt_max_estimated_tokens` values are
also enforced at the `LLMEnsemble.generate()` boundary before backend selection
for all ensemble roles. Oversized ensemble prompts therefore do not produce
call-history rows or provider/custom backend attempts.

LLM call telemetry is normalized at the ensemble boundary. Records include
role, backend index/name, backend metadata, strategy, effective scheduler
policy, scheduler accounting mode, API mode, normalized request parameters,
normalized client context, prompt/output sizes and
hashes, latency, success/error status, total attempt index, configured attempt
cap, retry/fallback attempt indexes, retry/fallback decisions, normalized
provider failure categories, and scheduler counts before/after the call.
Failed calls also include nullable `provider_status_code` when the raised SDK
exception exposes a safe integer HTTP-style status code.
Each call's `scheduler_policy` records the scheduler boundary: backend
selection uses the shared `global_backend_bandit`, role selection is not
independent per role, and sorted `reward_accounted_roles` state which roles can
advance scheduler reward accounting.
Built-in provider adapters also add
`adapter_retry` with their configured `provider_max_retries`, actual provider
attempts, failed attempt count, and safe exception type labels for failed
internal attempts. The final scheduler snapshot and strict ledger replay also
derive `role_accounting` counters for calls, successes, failures,
reward-accounted calls, telemetry-only calls, ensemble retry/fallback
attempts, adapter-internal provider attempts, and provider-reported token
totals by role, plus per-role provider-failure category counts.
Strict ledger replay also derives `provider_failure_policy_summary`, an
audit-only summary of failed-call policy records grouped by role, provider
failure category, retry/fallback decision, and quarantine/penalty decision.
Config-created ensembles append these strict
finite JSON records to `llm_calls.jsonl` with `record_type: "call"` and
monotonic `sequence_id` values plus v1 schema markers. Backend reward
accounting appends `record_type: "reward"` rows that link `call_id`, backend
index, raw reward, capped reward, and v1 reward-record schema markers.
`load_llm_call_ledger()` is the strict replay reader for this stream: it
rejects non-contiguous call sequence ids, duplicate call ids, reward rows for
unknown or non-successful calls, duplicate rewards, unsupported declared
schemas, backend mismatches, malformed SHA-256 digests, and inconsistent
scheduler counts-before/after vectors, including telemetry-only auxiliary
calls that do not change scheduler counters. It also validates restored backend
name/API-mode telemetry, request-parameter telemetry, client-context telemetry,
backend metadata, scheduler-accounting mode, and telemetry diagnostics before
returning replay metadata with the derived role-accounting and
provider-failure-policy summaries. Call `id` values are
deterministic ordered-call-stream identities used to link in-run rewards back to successful calls;
matching deterministic call streams produce matching ids while repeated calls
inside one stream remain distinct.
Provider error text is retained according to `provider_error_retention_mode`:
`redacted` stores secret-redacted bounded text by default, `full` stores the
secret-redacted full message, `hash_only` stores no text with raw SHA-256 and
length metadata, and `off` stores neither text nor hash/length metadata.
Successful provider/backend output text is retained according to
`provider_response_retention_mode`: `hash_only` is the default and stores no
raw output text beyond top-level output hash/count telemetry, `full` and
`redacted` store secret-redacted output text in `output`, and `off` suppresses
the output-retention sidecar hash/length while preserving the top-level call
telemetry hash used for replay.
Failed calls also record
`provider_failure_category` values for provider-response validation failures,
timeouts, rate limits, transport errors, provider client/server status errors,
and unknown failures, plus `provider_status_code` when SDK exceptions expose a
safe HTTP-style status. Role-accounting summaries aggregate those categories
for audit, but they are not quarantine or penalty decisions. Prompt payloads and call-role labels are validated before
scheduler selection, and empty, non-text, oversized, refusal, or tool-call-only
backend outputs are recorded as failed call records with
`provider_response_error` categories rather than successful pulls. Provider
usage counts, request/response ids, and finish reasons are copied from
built-in adapter SDK responses when available; omitted or unsupported provider
metadata is recorded as empty fields. Adapter-internal retry telemetry is
available through `adapter_retry`. Bounded scalar provider-native diagnostics
are available through `provider_diagnostics`; retained string values are
secret-redacted, capped at 200 characters, and paired with raw SHA-256/count
metadata, while nested provider payloads are rejected before persistence.
Live provider pricing/default capture and full restored token/cost budget
replay are not available yet. Backend/model `prompt_max_estimated_tokens`
limits are enforced as heuristic pre-call caps, but provider-tokenizer-backed
section packing is not available yet.
Runtime manifests also include a validated `runtime.provider_cancellation_policy`
record. The policy declares provider request timeout, ensemble wait-deadline,
and runtime-deadline rules, records configured `llm_call_timeout_sec`,
`max_runtime_seconds`, and the per-backend `timeout_sec` surface, and points to
`llm_calls.jsonl` / `manifest.json` as timeout and budget-stop artifact
locations. Rules that require artifacts declare matching `artifact_kinds`, and
policy validation rejects required rule artifacts whose kinds are absent from
the artifact list. Provider-request and ensemble-deadline rules are scoped to
the loop's current LLM role surfaces: `mutation`, `critique`, `feedback:*`,
and `meta_prompt`. Rules for scopes with configured
`llm_role_failure_quarantine_after` thresholds also declare quarantine action
and `quarantine_record` evidence. The record deliberately reports
`hard_cancel_ready: false` until provider SDK cancellation tokens and
timeout-driven stop policies are implemented.
Bundled adapters use configured `llm_prompt_roles` entries to add structured
role instructions before the rendered user prompt: OpenAI receives
system/developer messages or input items, Anthropic receives a composed
system field, and Ollama receives a system message. Omitted roles keep the
default single user message/input item. Each call record's
`prompt_role_policy` stores the matched role, message roles, instruction
fields, and SHA-256/character/redaction metadata for configured instruction
text without retaining that text. Built-in backend specs accept validated
sampling/request fields for provider-supported `temperature`, `top_p`, `stop`,
and `seed`; normalized effective values are recorded in `request_parameters`,
while omitted fields use provider SDK defaults. Each call also records
`backend_defaults` for LibreEvolve's effective local output-token cap, provider
internal retry cap, configured request timeout or `null`, API mode, and OpenAI
reasoning/API-mode policy when relevant; remote provider SDK defaults and
pricing are not inferred. Built-in backend specs also accept
`prompt_max_estimated_tokens` as a heuristic model/context-window cap; the
selected backend cap is copied into each call record as
`backend_prompt_max_estimated_tokens`. Built-in backend specs also
accept explicit endpoint/client-context fields: OpenAI `base_url`,
`organization`, and `project`; Anthropic `base_url`; and Ollama `host`.
Accepted safe values are recorded in the manifest backend spec and copied into
each call record as `client_context`; omitted fields still use
SDK/environment defaults.
Generated candidate history
still embeds the mutation/critique/feedback call span, including recovered
retry/fallback attempts, and meta-prompt call records are embedded in
`prompt_history.jsonl`; `llm_calls.jsonl` is the append-only run-level stream
for config-created ensemble calls.

## `best.py` and `best_workspace/`

After a run completes, the CLI writes the best archived program's primary-file
content to `best.py` and materializes the complete best candidate file set
under `best_workspace/`. For workspace candidates, both views are produced from
the same canonical file set.
The CLI stages both artifacts under temporary paths first, then swaps the
artifact pair into place only after the workspace materializes successfully.
Before writing, replacing, or cleanup, direct best export rejects linked
visible, temporary, and backup best-artifact paths (`best.py`,
`best_workspace/`, `.best-*.tmp`, and `.best-*.bak`), including symlinks and
Windows junctions. Startup overwrite already rejects linked known artifacts;
the direct exporter applies the same run-owned-artifact boundary to its
post-run replacement path.
If export fails while replacing an existing pair, it rolls back to the previous
`best.py` plus `best_workspace/` pair and removes temporary export paths.
If rollback or cleanup also fails, the exporter keeps the original export
failure as the primary diagnostic, records rollback/cleanup failures as
secondary redacted diagnostics, and preserves backup paths that could not be
restored instead of deleting them during cleanup.
The export attempt is reflected in `manifest.json` as
`runtime.best_artifact_export`; failed exports keep
`runtime.status: "completed"` when core evolution completed, but set
`runtime.best_artifact_export.status: "failed"` with redacted error diagnostics
current artifact presence records, optional `rollback_errors`,
`cleanup_errors`, and `preserved_backups` labels.

`best.py` is a compatibility convenience artifact:

- it is not used for resume
- it is not necessarily the last candidate evaluated
- it reflects the best fitness seen in the archive

For workspace candidates, `best_workspace/` is the direct reusable output. It
is regenerated on each successful invocation from exact candidate-workspace
materialization: files are written to a temporary sibling workspace first, then
the target root is swapped after path preflight and all file writes succeed.
Link or junction roots, ancestors, and existing nested entries are rejected,
and existing visible roots are preserved if a file write fails. If earlier best
artifacts already exist, startup fails by default with the run-directory
collision policy described above, or removes the previous artifacts first when
`overwrite` is explicitly selected.
Candidate workspace contents are bounded by a reject policy before they become
history, prompt, validator, or best-export inputs. The default model/run
limits are `max_candidate_workspace_files: 256`,
`max_candidate_file_chars: 1000000`, and
`max_candidate_total_chars: 2000000`; static sidecars also enforce
`max_candidate_static_file_bytes: 2000000` and
`max_candidate_total_static_bytes: 10000000`. `max_candidate_workspace_files`
counts text files plus static sidecars. Manifests record the configured values
under `config` and the effective behavior under
`policies.candidate_workspace_size`. Oversized text or static workspaces are
rejected; there is still no blob-store spillover or summary-only persistence
path for oversized candidates.

## Example histories committed to the repo

The repository includes curated examples under
[`examples/runs/`](../examples/runs/README.md). Use:

```bash
py -3.12 -m libreevolve show examples/runs/hello_world_ensemble
py -3.12 -m libreevolve show examples/runs/sorting_ttt_rl
```

Those checked-in examples are legacy history fixtures. They do not contain the
complete current artifact layout shown above, including `manifest.json`,
`archive_events.jsonl`, `llm_calls.jsonl`, `prompt_history.jsonl`,
`failure_history.jsonl`, or `best_workspace/`.

`show` is a compact compatibility view. For current histories that include
`metadata.archive_admission`, it selects the best archive-retained valid record
from `history.jsonl` by archive selection score with fitness as the tie-break,
then prints metrics and archive cell/retention/descriptor diagnostics when
present. When `metadata.archive_admission.objective_vector` is present, it also
prints finite normalized objective metrics and the manifest-safe
selection-policy type, summarizing large vectors with a bounded preview and
stable hash. `cell_admitted`, `elite_retained`, `search_state_changed`, and
`sampling_eligible` distinguish MAP-Elites cell entry from auxiliary elite-list
retention. For legacy histories without archive metadata, including the
checked-in fixtures above, it falls back to the highest top-level `fitness`
row. Use
`best.py`/`best_workspace/` from the original run as the exact archived output.
For the selected current-format row, `show` also prints bounded inspection
summaries when the corresponding fields exist: parent id, lineage depth/tail,
prompt program id, parent-selection strategy/selected parent/target metric,
evaluator stage failure counts, evaluator accounting counters, LLM feedback
success/failure counts plus aggregate weighted delta, and run-level
`failure_history.jsonl` totals bucketed by admission reason and error. These
summaries intentionally avoid raw prompts, raw feedback prose, stdout/stderr,
and mutation payload text.
When `manifest.json` is present, `show` also reports `manifest.runtime.status`
as completed, aborted best-so-far, or partial best-so-far when runtime
finalization is missing. Missing manifests keep legacy history-only
compatibility. If `runtime.history.programs_logged` disagrees with the number
of streamed `history.jsonl` rows, `show` fails the inspection instead of
presenting an inconsistent completed-looking result.
When the selected history row contains `files` plus `primary_file`, `show`
prints the logged workspace file manifest and every file's content, with the
primary file marked.
Mixed legacy/current histories are intentionally unsupported for this compact
view and fail with a line-numbered schema-mixing diagnostic.
`show` streams the history file as strict UTF-8 and fails the inspection with a
line-numbered diagnostic when the stream contains invalid UTF-8 bytes, a row is
malformed JSON, not a JSON object, or lacks a finite numeric `fitness`. It also
requires every streamed history `id` to be a manifest-safe program identifier
and rejects duplicate ids with the first-seen line number. Every streamed
`metrics` object must use manifest-safe metric names and JSON-native finite
numeric values, except boolean `is_valid`; printed metric summaries use strict
JSON. While streaming, it also validates `generation`, legacy `code`,
workspace file paths/contents, and `primary_file` for every row; malformed
unselected, invalid, or non-admitted rows fail the inspection before any
best-looking row is printed. Workspace file paths are normalized and validated
with the same candidate path grammar used for runtime workspaces before they
are printed. Displayed archive summary fields remain validated while streaming
current-format histories.
`load_accepted_history_index()` provides a checked accepted-history reader for
future restore/query code. It validates UTF-8/JSON shape, duplicate JSON object
names, finite fitness, manifest-safe ids, metrics, and duplicate program ids
before returning an id-indexed map. `load_failure_history_records()` exposes
the same duplicate-object-name strictness plus checked failure-row identity,
generation, mutation-payload metadata, changed-path, and fingerprint
consistency validation while keeping malformed/non-text mutation payload
evidence queryable as diagnostics. `load_prompt_history_records()` exposes
duplicate-object-name strictness for prompt telemetry replay. Current
plugin/retrieval artifact readers also reject duplicate JSON object names
before restoring TTT/RL export counts or DeepResearch disk-cache snapshots.
Archive cells and elite lists can be restored from manifest archive snapshots
plus checked accepted-history rows; controller resume, ordered migration-event
replay, and provider/plugin output replay remain future work.
Rows with `metadata.archive_admission` are current-format history records only
when the archive-admission payload is an object. If an admitted row includes
explicit archive-state flags, at least one retention or search-state flag must
be true before `show` can present that row as retained. Present
current-history `evaluation` payloads must be objects, and any
`evaluation.is_valid` field must be boolean. Archive diagnostic fields are
validated while streaming current histories, so malformed unselected retained
rows cannot be hidden by a valid selected row. If
`metadata.archive_admission.program_id` is present, it must be manifest-safe
and match the history row `id`; missing `program_id` remains compatible with
older current-format rows. Current MAP-Elites `cell`
diagnostics must be three non-negative integer coordinates. When
`manifest.json.config.map_elites_bins` is present, `show` also rejects any
coordinate greater than or equal to that positive integer bin count; missing
manifest/bin metadata keeps legacy arity/type/non-negative validation only.
Rows rejected from archive admission because a restored or hook-mutated program
contains non-finite top-level `fitness` or metrics are not repaired by `show`;
they should be inspected through `history_invalid.jsonl` or future
rejected-candidate diagnostics instead of normal `history.jsonl`.
Archive descriptor labels are validated with the same manifest-safe metric-name
grammar used for runtime metrics before display; secret-like labels, control
characters, reserved `is_valid`, and non-identifier names fail with a
line-numbered diagnostic instead of being echoed by `show`. Large descriptor maps or long
descriptor labels are summarized with descriptor count, bounded preview,
omitted count, and a stable hash rather than printed in full. Archive
objective-vector rows use the same manifest-safe metric-name validation plus
finite `[0, 1]` normalized score validation, and malformed unselected rows fail
before any best row is printed. Large selected legacy source or workspace file
bodies are truncated in terminal output with source length, rendered length,
displayed length, omitted character count, source hash, and a `history.jsonl`
full-source pointer. The default terminal body cap is 4,096 displayed characters
per source body; `--source-display-chars`
sets a different per-body cap, `--full-source` prints the complete selected
source bodies, and `--redact-source` redacts secret-like source text before
display-budget accounting.
Direct `Program` construction and history persistence require non-negative
integer generations, reject self-parenting, reject duplicated lineage entries,
reject the program id appearing in its own lineage, and require a present
`parent_id` to match the lineage tail when lineage is provided. Omitted
`Program.fitness` keeps the legacy `-inf` unevaluated sentinel, but explicitly
provided fitness values must be finite, numeric, and non-boolean. Restored or
hook-mutated objects with invalid fitness are still rejected by archive
admission, accepted-history persistence, and `show`, or rendered as explicit
invalid-fitness markers before prompt use.
Malformed direct/restored records are rejected before recency sampling or
accepted JSONL persistence. Program metric vectors require
non-empty string keys; `is_valid` is the only boolean metric field, and all
other values must be finite numbers before archive insertion or history
persistence. Raw MAP-Elites/island/database archive insertion also requires
`evaluation.is_valid is True`, so validity-gated admission is not bypassed by
lower-level archive APIs. Raw MAP-Elites and island insertion also revalidate
program ids, parent ids, and lineage entries before mutating archive state.
Direct MAP-Elites construction validates positive integer `bins`, positive
integer `elite_archive_size`, and finite ordered `perf_bounds`.
Richer stage, lineage, prompt, feedback, and failure-summary diagnostics are
tracked as follow-up work.

## Related plugin artifact

The `ttt_rl` plugin writes training examples to:

```text
runs/<run-name>/plugin_artifacts/ttt_rl/grpo_data.jsonl
runs/<run-name>/plugin_artifacts/ttt_rl/grpo_data_invalid.jsonl   # Only when an export record is rejected
```

When loaded by the CLI, this file is scoped under the active run directory. It
exports both `raw_score` and clipped rewards
(`reward = max(0.0, raw_score)`) and is linked from `manifest.json` through
`runtime.plugin_artifacts`. Examples are queued only when both source metadata
fields are non-empty strings: `metadata["prompt"]` becomes `prompt`, and
`metadata["diff"]` becomes `response`. Malformed prompt/response metadata is
skipped before queueing and reported through
`skipped_malformed_examples`/`malformed_example_reasons`; malformed scores must
be finite non-boolean numbers and raise before a row is queued, so invalid
direct hook calls do not park the export cursor or block later valid examples.
Accepted `raw_score` and `reward` fields are JSON-native floats. Each flush
appends examples that have not already been exported by that plugin instance,
so repeated generation-end hooks do not duplicate JSONL rows. If pending
examples exceed `max_retained_examples`
(`500` by default), the plugin immediately exports the pending overflow and
then prunes already exported records from memory. Run-artifact metadata
collection also flushes remaining pending examples before returning manifest
metadata, which makes short completed runs durable even when their final
generation is not a `train_every` multiple. On construction, the plugin counts
valid rows already present in `grpo_data.jsonl`, reports
`restored_exported_examples`, `restore_invalid_lines`, and `restore_policy`,
and appends only new rows after the existing file contents. That restored
export metadata is replay/artifact continuity, not a GRPO model or optimizer
checkpoint. Direct in-code plugin construction
can still choose a custom `log_dir`, including directories outside a run; those
exports are user-managed external artifacts, and the `log_dir`, path, count,
hash, and byte fields under `runtime.plugin_artifacts[].metadata` are the
provenance to inspect. Prompt and response payloads pass through shared
secret-pattern redaction and are capped by both per-field and combined
prompt/response character budgets before queueing. Metadata reports
`payload_policy`, `max_payload_field_chars`, `max_payload_total_chars`,
original/stored character counts, and redacted/truncated/aggregate-truncated
payload counters.
