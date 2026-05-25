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
- `eval_stages` (`[]`): optional configured evaluator stages.
- `prompt_variants` (`[]`): optional prompt templates for stochastic sampling.
- `meta_prompt_evolution` (`False`): when true, periodically ask the active LLM
  backend to produce a revised prompt template.
- `meta_prompt_interval` (`25`): generations between optional meta-prompt
  mutations.

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
    timeout_sec: 5
    min_score: 0.1
  - name: full
    timeout_sec: 30
    min_score: 0.5
backends:
  - type: openai
    model: gpt-4o-mini
```

Unknown config keys are ignored rather than rejected.

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

## Environment variables

Common variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OLLAMA_HOST`

Provider SDKs may honor additional provider-specific variables.

## Known caveats

- The CLI does not expose every `Config` field directly; use `config.yaml` for
  migration, archive, prompt, stage, and ensemble scheduling settings.
- `eval_stages` currently repeats the same local validator with different
  thresholds/timeouts. It is not yet a distributed test-suite scheduler.
- `prompt_variants` seed the prompt-program database; set
  `meta_prompt_evolution: true` to allow interval-based LLM template mutation.
- Meta-prompt mutation uses the same backend ensemble and must preserve every
  placeholder required by `PromptSampler`.
