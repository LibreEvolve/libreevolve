# Configuration

Configuration is assembled from three sources, in this order:

1. `Config` defaults in [`libreevolve/core/config.py`](../libreevolve/core/config.py)
2. optional problem-local `config.yaml`
3. CLI overrides from [`libreevolve/cli.py`](../libreevolve/cli.py)

`.env` is loaded at CLI import time with `override=True`.

## `Config` fields

### Evolution

- `max_generations` (`1000`): generations to run.
- `num_inspirations` (`3`): archive members rendered into prompts.
- `eval_timeout_sec` (`60.0`): default validator subprocess timeout.
- `explore_ratio` (`0.3`): probability of exploration instead of exploitation.
- `mutation_mode` (`"diff"`): `diff` or `full`.
- `eval_stages` (`[]`): optional configured evaluator stages with stage
  validator entrypoints, thresholds, samples, seeds, retries, and timeouts.
- `prompt_variants` (`[]`): optional prompt templates for stochastic sampling.
- `meta_prompt_evolution` (`False`): when true, periodically ask the active LLM
  backend to produce a revised prompt template.
- `meta_prompt_interval` (`25`): generations between optional meta-prompt
  mutations.
- `critique_enabled` (`False`): when true, run an LLM critique/revision pass
  on the proposed mutation before applying it.
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

### Population

- `n_islands` (`5`): number of MAP-Elites islands.
- `migration_interval` (`25`): migrate every N generations. `<= 0` disables
  migration.
- `migration_ratio` (`0.10`): fraction of each island's elite archive copied to
  the next island, rounded up to at least one migrant.
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

Only constructor-supported keys are passed to backend classes; scheduling
metadata stays in the ensemble.

### Plugins and logging

- `plugins` (`[]`): list of built-in plugin names.
- `log_dir` (`"runs/"`): root output directory.
- `problem_name` (`"unnamed"`): final run subdirectory name.
- `seed` (`42`): random seed for Python's global `random` module and prompt
  variant sampling.

## Problem-local `config.yaml`

Example:

```yaml
max_generations: 200
eval_timeout_sec: 15
mutation_mode: full
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
backends:
  - type: openai
    model: gpt-4o-mini
```

Unknown config keys are currently ignored rather than rejected. This is a known
reproducibility gap for AlphaEvolve-style runs because spelling mistakes can
silently leave defaults in effect.

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

CLI `--plugins` and `--backends` replace, rather than merge with, config-file
lists.

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

## Environment variables

Common variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OLLAMA_HOST`

Provider SDKs may honor additional provider-specific variables.

## Known caveats

- The CLI does not expose every `Config` field directly; use `config.yaml` for
  migration, archive, prompt, stage, LLM feedback, critique, and ensemble
  scheduling settings.
- Config validation is incomplete: unknown problem-local keys are ignored, and
  nested backend/stage/feedback fields are only partially validated.
- Run-wide budget configuration is not implemented yet. `max_generations` and
  per-validator timeouts are the only hard stop controls; there are no
  wall-clock, LLM-call, token, cost, evaluator-second, sample, retry, or
  accelerator budget counters.
- `eval_stages` is still local subprocess execution. It is not yet a
  distributed evaluator-worker scheduler.
- `prompt_variants` seed the prompt-program database; set
  `meta_prompt_evolution: true` to allow interval-based LLM template mutation.
- Meta-prompt mutation uses the same backend ensemble and must preserve every
  placeholder required by `PromptSampler`. The current implementation instructs
  the LLM to preserve placeholders but does not reject malformed prompt
  templates yet.
- Critique and LLM feedback use the same backend ensemble as mutation
  generation. They are synchronous and optional, not parallel reviewer workers.
