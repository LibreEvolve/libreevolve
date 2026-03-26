# Architecture

LibreEvolve is a research framework for LLM-guided program mutation. Its runtime
is deliberately small:

1. Load a filesystem-defined problem.
2. Build a `Config` from defaults, optional `config.yaml`, and CLI overrides.
3. Seed an island-based MAP-Elites population.
4. Repeatedly ask an LLM backend for a SEARCH/REPLACE diff.
5. Evaluate the mutated candidate through a three-tier cascade.
6. Log every candidate and archive only valid ones.
7. Reward the selected backend and periodically migrate elites.

## Top-level flow

The CLI entrypoint is [`libreevolve/cli.py`](../libreevolve/cli.py). The `run`
command:

- loads `.env` with `override=True`,
- loads a problem directory with `load_problem()`,
- merges problem-local `config.yaml` into the default `Config`,
- instantiates built-in plugins named on the CLI,
- calls `evolve(problem, config, plugins)`,
- writes the best program to `runs/<problem_name>/best.py`.

The `show` command reads `history.jsonl` and prints the highest-fitness record.

## Problem loading

`load_problem()` in [`libreevolve/problems/loader.py`](../libreevolve/problems/loader.py)
constructs a `Problem` dataclass from a directory containing:

- `task_description.txt`
- `metrics.yaml`
- `validate.py`
- `initial_programs/*.py`

The loader also parses:

- `primary_metric`: the first metric marked `primary: true`, or the first metric
  if none is marked primary
- `primary_bounds`: metric bounds from `metrics.yaml`, defaulting to `(0.0, 1.0)`

## Evolution loop

The core loop lives in [`libreevolve/core/loop.py`](../libreevolve/core/loop.py).

### Seeding

Each seed program is evaluated before generation 0. Seed candidates bypass diff
penalties by calling `CascadeEvaluator.evaluate(..., diff_error=None)`.

Every seed is:

- logged to `history.jsonl`
- added to the archive only if its score is at least `VALID_THRESHOLD`

`VALID_THRESHOLD` is currently `0.0`.

### Per-generation behavior

For each generation:

1. Call `plugin.on_generation_start(gen, db)` for all active plugins.
2. Pick a parent with:
   - `explore`: random occupied cell from any island
   - `exploit`: best program across islands
3. Sample `num_inspirations` diverse archive members.
4. Build prompt context from all plugins via `build_extra_context()`.
5. Construct a mutation prompt with:
   - the current best parent code,
   - inspiration programs,
   - plugin context,
   - the last 5 failed mutations, if any.
6. Ask the LLM ensemble to generate a SEARCH/REPLACE diff.
7. Apply the diff to the parent code.
8. Evaluate the resulting child code.
9. Construct a `Program` object with lineage and metadata.
10. Pass that `Program` through `plugin.on_evaluated(program, score)`.
11. Log the program.
12. Add it to the population if the final score is valid.
13. Reward the chosen backend with `max(0.0, score - parent.fitness)`.
14. Run migration when the configured interval is reached.
15. Call `plugin.on_generation_end(gen, best)`.

### Prompt shape

`build_prompt()` is intentionally simple. It uses plain string assembly rather
than a prompt templating system. The prompt includes a concrete diff-format
example and explicit instructions to avoid:

- markdown fences
- comments
- explanatory text

This is important because the diff engine performs exact substring replacement.

## Diff engine

[`libreevolve/core/diff.py`](../libreevolve/core/diff.py) implements the
SEARCH/REPLACE mutation format:

```text
<<<SEARCH
old code
===
new code
>>>REPLACE
```

Behavior to be aware of:

- markdown fences are stripped before parsing
- multiple diff blocks are supported
- replacements are applied atomically
- the search text must match exactly
- only the first occurrence of each search block is replaced

Possible diff errors are:

- `no_diff_blocks`
- `search_not_found`
- `no_valid_changes`

## Evaluation cascade

[`libreevolve/core/evaluator.py`](../libreevolve/core/evaluator.py) uses a
three-tier evaluator:

- Tier 0: diff penalties for malformed or ineffective mutations
- Tier 1: `compile()` syntax check
- Tier 2: isolated subprocess execution of `validate.py`

Current score mapping:

- `no_diff_blocks` -> `-0.4`
- `search_not_found` -> `-0.3`
- `no_valid_changes` -> `-0.3`
- syntax error, subprocess crash, timeout, or malformed JSON -> `-0.2`
- `is_valid == False` from the validator -> `-0.1`
- otherwise -> value of the problem's primary metric

Validators run in a temporary subprocess and are expected to expose
`evaluate(code: str) -> dict`.

## Population model

Population state is split across three layers:

- `Program`: a dataclass carrying code, fitness, lineage, and metadata
- `MAPElites`: a single archive
- `IslandModel`: a collection of independent archives plus migration

### MAP-Elites

[`libreevolve/population/map_elites.py`](../libreevolve/population/map_elites.py)
maps programs into a 3D grid using:

- normalized performance
- normalized code length
- TF-IDF char-4gram diversity versus the elite archive

Each occupied cell retains only the highest-fitness program for that cell.
Separately, the archive maintains a capped global elite list for best-program
queries and diversity calculations.

### Islands and migration

[`libreevolve/population/islands.py`](../libreevolve/population/islands.py)
creates `n_islands` independent archives. Adds are round-robin across islands.

Migration uses a ring topology:

- island `i` copies top elites to island `(i + 1) % n_islands`
- migrants are copied, not moved
- migration uses a snapshot of each island's elite archive, so a program cannot
  cascade across multiple islands in one migration step

## Backend selection

[`libreevolve/llm/ensemble.py`](../libreevolve/llm/ensemble.py) wraps one or
more backends in a UCB1 bandit.

- `generate(prompt)` chooses a backend index and returns `(response, idx)`
- `record_reward(idx, reward)` adds reward after evaluation
- the loop currently clamps rewards to non-negative values before recording them

On tied UCB1 scores, the ensemble prefers the less-used arm.

## Plugins

Plugins are synchronous hooks invoked directly from the evolution loop. There is
no event bus or dependency system. Hook order is the order plugins are listed on
the CLI.

See [Plugins](./plugins.md) for the extension contract.

## Logging and artifacts

[`libreevolve/core/database.py`](../libreevolve/core/database.py) logs every
candidate to `runs/<problem_name>/history.jsonl`, valid or invalid. The archive
contains only valid programs, but the JSONL log is append-only and includes:

- program identity and lineage
- code
- fitness
- generation
- metadata, including prompt and diff

The CLI writes the final best code separately to `best.py`.

## Important implementation caveats

- `Problem.primary_bounds` is parsed by the loader but is not currently passed
  into `MAPElites`. Archive performance normalization therefore still defaults
  to `(0.0, 1.0)` for all problems.
- Plugins can alter scores in `on_evaluated()`. The logged and archived score is
  the post-plugin score, not necessarily the evaluator's raw score.
- The default backend is Anthropic Sonnet unless CLI or `config.yaml` overrides
  it.
