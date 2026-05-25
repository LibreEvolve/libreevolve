# Configuration

Configuration is assembled from three sources, in this order:

1. `Config` defaults in [`libreevolve/core/config.py`](../libreevolve/core/config.py)
2. optional problem-local `config.yaml`
3. CLI overrides from [`libreevolve/cli.py`](../libreevolve/cli.py)

`.env` is loaded at CLI import time with `override=True` for provider clients.
Validator subprocesses do not inherit that parent environment by default.
They run with a minimal environment plus names listed in
`validator_env_allowlist`, so provider keys such as `OPENAI_API_KEY` are hidden
from `validate.py` unless explicitly allowlisted.

## `Config` fields

### Evolution

- `max_generations` (`1000`): generations to run.
- `num_inspirations` (`3`): archive members rendered into prompts.
- `eval_timeout_sec` (`60.0`): default validator subprocess timeout.
- `validator_env_allowlist` (`[]`): parent environment variable names to pass
  into validator subprocesses in addition to the minimal default environment.
  Values are not written to metadata; persisted validator stdout/stderr applies
  basic secret-pattern redaction.
- `evaluator_artifact_include` (`[]`): glob patterns for validator-created
  files to copy from the temporary candidate workspace into
  `evaluator_artifacts/`. Empty means no artifact copy-out.
- `evaluator_artifact_exclude` (`[]`): glob patterns to exclude from artifact
  copy-out after include matching.
- `evaluator_artifact_max_files` (`20`): maximum copied files per evaluation.
- `evaluator_artifact_max_bytes` (`1000000`): maximum total copied artifact
  bytes per evaluation.
- `evaluator_artifact_redact_secrets` (`true`): apply basic secret-pattern
  redaction to UTF-8 text artifacts before writing them under
  `evaluator_artifacts/`. Binary or non-UTF-8 artifacts are copied raw.
- `explore_ratio` (`0.3`): probability of exploration instead of exploitation.
- `mutation_mode` (`"diff"`): `diff` or `full`. The built-in prompt template
  renders mode-specific mutation instructions; custom prompt variants can use
  `{mutation_mode}` and `{mutation_instructions}` or ignore them for backward
  compatibility.
- `eval_stages` (`[]`): optional configured evaluator stages with stage
  validator entrypoints, thresholds, samples, seeds, retries, and timeouts.
- `prompt_variants` (`[]`): optional prompt templates for stochastic sampling.
- `meta_prompt_evolution` (`False`): when true, periodically ask the active LLM
  backend to produce a revised prompt template.
- `meta_prompt_interval` (`25`): generations between optional meta-prompt
  mutations.
- `prompt_reward_mode` (`"absolute"`): prompt-program reward input. `absolute`
  uses the final composed candidate score; `improvement` uses final composed
  child score minus parent score.
- `prompt_reward_bounds` (`[0.0, 1.0]`): `[lo, hi]` bounds used to normalize
  prompt-program rewards to `0..1` before prompt selection.
- `prompt_explore_coeff` (`1.0`): exploration coefficient for the prompt
  database's UCB-like selector.
- `critique_enabled` (`False`): when true, run an LLM critique/revision pass
  on the proposed mutation before applying it. The revised mutation is
  previewed with the active mutation parser; if the revision is malformed but
  the original mutation still applies cleanly, LibreEvolve falls back to the
  original and records the fallback in candidate metadata.
- `critique_prompt` (`""`): optional custom instruction for the critique pass.
- `llm_feedback` (`[]`): optional LLM grader specs that score or discard
  evaluated candidates after local validation.

Example LLM feedback grader config:

```yaml
critique_enabled: true
llm_feedback:
  - name: simplicity
    metric: llm_simplicity
    weight: 0.05
    min_score: 0.2
    prompt: "Grade simplicity from 0 to 1. Return JSON with score, feedback, discard."
```

Feedback scores are logged as metrics, provenance is stored in evaluation
metadata, and weighted scores adjust candidate fitness without replacing the
raw primary validator metric. Graders run only for locally valid candidates by
default; set `include_invalid: true` on a grader to review invalid candidates.
For workspace candidates, the built-in feedback prompt includes a bounded,
deterministically ordered file listing with path headers, primary-file marking,
basic secret redaction, truncation notices, and compact evaluation diagnostics.
`llm_feedback` grader specs are validated before startup: `name`, `metric`, and
`prompt` must be strings when present; `weight` and `min_score` must be finite
numbers; `include_invalid` must be boolean; and unsupported keys are rejected.
Provider failures, malformed response scores, non-finite response scores, and
non-boolean discard values are recorded as `llm_feedback_failed` metadata and
ignored for score/validity composition. There is not yet a configurable retry,
penalty, or discard policy for failed feedback graders.

### Population

- `n_islands` (`5`): number of MAP-Elites islands.
- `migration_interval` (`25`): migrate every N generations. `0` disables
  migration.
- `migration_ratio` (`0.10`): fraction of each island's elite archive copied to
  the next island. `0.0` selects no migrants; positive ratios are rounded up to
  at least one migrant when an island has elites.
- `map_elites_bins` (`10`): bins per MAP-Elites dimension.
- `elite_archive_size` (`50`): cap on the per-island elite list.

### LLM routing

- `backends`: backend specs. Default:

```python
[{"type": "anthropic", "model": "claude-sonnet-4-6"}]
```

- `ensemble_explore_coeff` (`1.0`): exploration coefficient for UCB-style
  routing.
- `ensemble_strategy` (`"ucb1"`): `ucb1` or experimental
  `throughput_depth`.

Backend specs may include optional scheduling metadata:

```yaml
backends:
  - type: openai
    model: gpt-4o-mini
    role: breadth
    cost: 1.0
    latency: 1.0
    depth: 1.0
  - type: openai
    model: gpt-5.4-mini
    reasoning_effort: high
    role: depth
    cost: 4.0
    latency: 4.0
    depth: 5.0
ensemble_strategy: throughput_depth
```

Backend specs are validated before a run starts. Supported backend types are
`anthropic`, `openai`, and `ollama`; `model` is required; optional
`max_tokens`, `cost`, `latency`, `depth`, and `role` are validated; and
`reasoning_effort` is accepted only for OpenAI backends with one of `low`,
`medium`, `high`, or `xhigh`. Constructor-supported keys are passed to backend
classes; scheduling metadata stays in the ensemble.

In the current scheduler, `throughput_depth` uses numeric `cost`, `latency`,
and `depth`. The `role` field is descriptive metadata only; it is not yet used
for quotas, escalation, or role-specific routing.

### Plugins and logging

- `plugins` (`[]`): list of built-in plugin names.
- `log_dir` (`"runs/"`): root output directory.
- `problem_name` (`"unnamed"`): final run subdirectory name.
- `run_id` (UUID4 hex by default): provenance identifier written to
  `manifest.json`. It is not a resume checkpoint id.
- Run provenance is generated automatically: when available, the manifest
  includes Git state, `libreevolve/` source-tree hashes, problem-tree hashes,
  direct evaluator entrypoint hashes, and plugin module file hashes.
- `run_collision_policy` (`"fail"`): what to do when the target run directory
  already contains known run artifacts. `fail` aborts before appending or
  rewriting artifacts; `overwrite` deletes known run artifacts only
  (`history*.jsonl`, `failure_history*.jsonl`, `prompt_history*.jsonl`,
  `manifest.json`, `best.py`, and `best_workspace/`) before starting.
- `seed` (`42`): random seed for Python's global `random` module. Prompt
  variants currently enter `PromptDatabase`, where initial untried selection is
  ordered by UUID4 prompt-program ids rather than this seed. It does not make
  persisted candidate or prompt-program IDs deterministic yet; those still use
  UUID4 values.

Note: although `problem_name` is a `Config` field, the current CLI resets it to
the loaded problem directory name after reading `config.yaml`. Use `--run-name`
to choose a run directory from the CLI.

## Problem-local `config.yaml`

Example:

```yaml
max_generations: 200
eval_timeout_sec: 15
mutation_mode: full
evaluator_artifact_include: ["*.json", "artifacts/**"]
evaluator_artifact_exclude: ["artifacts/tmp/**"]
eval_stages:
  - name: smoke
    validate_path: validate.py
    timeout_sec: 5
    min_score: 0.1
    samples: 2
    seeds: [1, 2]
    retries: 1
  - name: full
    timeout_sec: 30
    min_score: 0.5
    artifact_include: ["reports/*.json", "plots/*.png"]
    artifact_exclude: ["reports/tmp/**"]
    artifact_max_files: 5
    artifact_max_bytes: 2000000
    artifact_redact_secrets: true
backends:
  - type: openai
    model: gpt-4o-mini
```

Problem-local `config.yaml` keys are checked against the `Config` dataclass and
unknown keys fail at CLI startup. `Config.validate()` also rejects invalid enum
values such as `mutation_mode: typo`, invalid ensemble strategies, malformed
backend specs, and invalid top-level numeric fields before the run mutates or
evaluates candidates.

This validation still assumes `config.yaml` parses to a top-level mapping.
Malformed YAML or scalar/list top-level documents can fail before the CLI wraps
the problem in a path-aware `ConfigError` diagnostic.

Nested evaluator-stage fields are validated before a run: `samples` must be
positive, `timeout_sec` must be positive, `retries` must be non-negative,
`min_score` must be numeric, artifact include/exclude fields must be lists of
strings, artifact redaction flags must be boolean, and artifact
max-file/max-byte limits must be non-negative integers. If both `samples` and
`seeds` are provided, the counts must match so stage sampling is reproducible.
Stage `artifact_*` settings override top-level evaluator artifact settings for
that stage.

Top-level evolution and population numeric fields are validated. Use
non-negative `max_generations`, `num_inspirations`, `migration_interval`, and
`ensemble_explore_coeff`; positive `eval_timeout_sec`, `n_islands`,
`map_elites_bins`, and `elite_archive_size`; and keep `explore_ratio` and
`migration_ratio` between 0 and 1.

## CLI overrides

The `run` command exposes:

- `--max-generations`, `-g`
- `--plugins`, `-p` (repeatable)
- `--backends`, `-b` as `type:model` (repeatable)
- `--mutation-mode` (`diff` or `full`)
- `--seed`
- `--reasoning-effort`, `-r`
- `--explore-ratio`, `-e`
- `--run-name`
- `--overwrite`

CLI `--plugins` and `--backends` replace, rather than merge with, config-file
lists. CLI `--overwrite` sets the effective run collision policy to
`overwrite` for the current invocation.

## Backend spec format

CLI backend specs use:

```text
openai:gpt-4o-mini
anthropic:claude-sonnet-4-6
ollama:llama3
```

The code forwards model names to provider SDKs and does not verify current
provider availability.

For OpenAI, `reasoning_effort` also controls API routing: if it is omitted,
LibreEvolve uses Chat Completions; if it is present, LibreEvolve uses the
Responses API and forwards the configured reasoning effort. The current code
does not detect model capabilities or validate reasoning-effort compatibility.
The CLI `--reasoning-effort` option applies to OpenAI backend specs from either
`config.yaml` or the same `--backends` invocation. It is ignored for non-OpenAI
backends.

## Environment variables

Common variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OLLAMA_HOST`

Provider SDKs may honor additional provider-specific variables.

LLM provider failures are not retried or routed to fallback backends today.
Mutation, critique, feedback, and meta-prompt provider exceptions can abort a
run rather than being recorded as structured failed LLM-call attempts.

## Known caveats

- The CLI does not expose every `Config` field directly; use `config.yaml` for
  migration, archive, prompt, stage, LLM feedback, critique, and ensemble
  scheduling settings.
- Config validation is still incomplete for plugin-specific schemas and
  provider/model API compatibility. Malformed YAML and non-mapping top-level
  `config.yaml` files also need normalized startup errors. Top-level numeric
  fields, mutation/ensemble enums, backend specs, unknown problem-local keys,
  evaluator-stage numeric fields, and LLM feedback grader specs are checked
  before a run starts when the config file parses to a mapping.
- CLI override semantics are incomplete: `config.yaml` `problem_name` is
  overwritten by the problem directory name unless `--run-name` is supplied.
- Run-wide budget configuration is not implemented yet. `max_generations` and
  per-validator timeouts are the only hard stop controls; there are no
  wall-clock, LLM-call, token, cost, evaluator-second, sample, retry, or
  accelerator budget counters.
- Seeded replay is incomplete: `Config.seed` controls local Python `random`
  choices, but prompt variant ordering is mediated by UUID4 prompt-program ids,
  `Program` and `PromptProgram` IDs are UUID4 values, and provider/model
  nondeterminism is not captured as a replay contract.
- `eval_stages` is still local subprocess execution. It is not yet a
  distributed evaluator-worker scheduler.
- Validator entrypoints are loaded by file path from a temporary runner. The
  validator directory is added to `sys.path`; the candidate root is used as
  subprocess `cwd` and added to `sys.path`.
- Validator subprocess environment isolation is a local allowlist, not a
  container or network sandbox. LibreEvolve does not yet enforce network
  egress policy for validator code.
- `prompt_variants` populate the prompt-program database; set
  `meta_prompt_evolution: true` to allow interval-based LLM template mutation.
- Configured prompt variants and meta-prompt mutations are validated against
  the `PromptSampler` placeholder schema before use. Templates must include the
  required `{task}` placeholder and may use the documented context, parent,
  inspiration, failure, and mutation-mode placeholders. Unknown placeholders,
  malformed braces, empty placeholders, and attribute/index placeholders are
  rejected. Invalid LLM-mutated templates are written to
  `prompt_history_invalid.jsonl`, penalize the parent prompt program, and do
  not enter the prompt population.
- Prompt-program reward telemetry is written into `prompt_history.jsonl` under
  `program.metadata.last_prompt_reward`, including reward mode, raw reward,
  normalized reward, and bounds. The same effective prompt reward policy is
  recorded in `manifest.json`.
- Critique and LLM feedback use the same backend ensemble as mutation
  generation. They are synchronous and optional, not parallel reviewer workers.
