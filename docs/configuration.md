# Configuration

Configuration is assembled from three sources, in this order:

1. `Config` defaults in [`libreevolve/core/config.py`](../libreevolve/core/config.py)
2. optional problem-local `config.yaml`
3. CLI overrides from [`libreevolve/cli.py`](../libreevolve/cli.py)

`.env` is loaded at CLI import time with `override=True`, so environment values
from `.env` replace existing process variables of the same name.

## `Config` fields

### Evolution

- `max_generations` (`1000`): number of generations to run.
- `num_inspirations` (`3`): number of sampled archive members inserted into the
  prompt as inspirations.
- `eval_timeout_sec` (`60.0`): timeout for validator subprocess execution.
- `explore_ratio` (`0.3`): probability of exploration instead of exploitation.

### Population

- `n_islands` (`5`): number of MAP-Elites islands.
- `migration_interval` (`25`): migrate every N generations. `<= 0` disables
  migration.
- `migration_ratio` (`0.10`): fraction of each island's elite archive copied to
  the next island during migration, rounded up to at least one migrant.
- `map_elites_bins` (`10`): bins per MAP-Elites dimension.
- `elite_archive_size` (`50`): cap on the per-island elite list.

### LLM routing

- `backends`: list of backend specs. Default is:

```python
[{"type": "anthropic", "model": "claude-sonnet-4-6"}]
```

- `ensemble_explore_coeff` (`1.0`): exploration coefficient used by UCB1.

### Plugins

- `plugins` (`[]`): list of built-in plugin names.

### Logging

- `log_dir` (`"runs/"`): root output directory.
- `problem_name` (`"unnamed"`): final run subdirectory name.
- `seed` (`42`): random seed for Python's global `random` module.

## Problem-local `config.yaml`

If `<problem_dir>/config.yaml` exists, the CLI reads it and applies only keys
that match fields on `Config`. Unknown keys are ignored rather than rejected.

Example:

```yaml
max_generations: 200
eval_timeout_sec: 15
explore_ratio: 0.4
n_islands: 8
migration_interval: 10
backends:
  - type: openai
    model: gpt-4o-mini
```

This file is a convenient place to store per-problem defaults without forcing
all users onto the same CLI flags.

## CLI overrides

The `run` command currently exposes these overrides:

- `--max-generations`, `-g`
- `--plugins`, `-p` (repeatable)
- `--backends`, `-b` as `type:model` (repeatable)
- `--seed`
- `--reasoning-effort`, `-r`
- `--explore-ratio`, `-e`
- `--run-name`

Override behavior:

- CLI `--plugins` replaces the `plugins` list from config rather than merging it.
- CLI `--backends` replaces the `backends` list from config rather than merging
  it.
- `--reasoning-effort` is attached to every backend spec produced by
  `--backends`.
- `--run-name` replaces `problem_name`; otherwise the loaded problem directory
  name becomes the run name.

## Backend spec format

The CLI expects backend specs of the form:

```text
openai:gpt-4o-mini
anthropic:claude-sonnet-4-6
ollama:llama3
```

They are converted into dicts like:

```python
{"type": "openai", "model": "gpt-4o-mini"}
```

When `--reasoning-effort high` is provided, the resulting dict becomes:

```python
{"type": "openai", "model": "gpt-5.4-mini", "reasoning_effort": "high"}
```

The code does not currently validate whether a given backend type actually
supports that field. In practice, only the OpenAI backend consumes it.

## Environment variables

Common environment variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OLLAMA_HOST`

The backends rely on their vendor SDK defaults, so additional provider-specific
environment variables may also be honored.

## Known caveats

- `problem.primary_bounds` is not wired into `MAPElites` yet, so changing metric
  bounds does not currently change archive performance normalization.
- The CLI does not expose every `Config` field directly. For parameters like
  `migration_interval` or `ensemble_explore_coeff`, use `config.yaml`.
