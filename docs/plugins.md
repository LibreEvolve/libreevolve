# Plugins

LibreEvolve plugins are synchronous hook objects used by the main evolution
loop. The interface is defined in
[`libreevolve/plugins/base.py`](../libreevolve/plugins/base.py).

## Hook contract

Plugins may override any subset of these methods:

```python
class PluginBase(ABC):
    def on_generation_start(self, gen: int, db: ProgramDatabase) -> None: ...
    def on_evaluated(self, program: Program, score: float) -> float: ...
    def on_generation_end(self, gen: int, best: Program) -> None: ...
    def build_extra_context(self, parent: Program, inspirations: list[Program]) -> str: ...
```

## Execution order

Plugins run in the order they are listed on the CLI.

Per generation, the loop calls them in this order:

1. `on_generation_start()`
2. `build_extra_context()`
3. `on_evaluated()`
4. `on_generation_end()`

Important details:

- `build_extra_context()` is called before mutation generation.
- `on_evaluated()` receives a fully constructed `Program`, including:
  - `parent_id`
  - `generation`
  - `lineage`
  - `metadata["prompt"]`
  - `metadata["diff"]`
- the return value from `on_evaluated()` becomes the program's final top-level
  fitness for logging, prompt scoring, and backend reward computation.
- plugin score adjustments are recorded under `metadata.score_composition`,
  including per-plugin before/after scores, metric additions/changes, invalid
  score rejections, and whether final top-level fitness diverges from
  `evaluation.fitness`.
- archive admission is still gated by `evaluation.is_valid`; a plugin can lower
  or raise fitness, but it cannot accidentally archive an evaluator-invalid
  candidate unless an explicit future override policy is added.

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

## Built-in plugins

### `causal`

Implemented by
[`libreevolve/plugins/causal.py`](../libreevolve/plugins/causal.py).

Purpose (CausalEvolve-inspired, not paper-complete):

- infer what kinds of code edits tend to help
- bias prompt context toward the most promising edit factor

Mechanics:

- inspects diff text from `program.metadata["diff"]`
- classifies changes into heuristic factors such as loop structure, constants,
  helper functions, and algorithm choice
- tracks reward per factor with a UCB1-like score
- injects a short causal guidance block into future prompts

Limitations:

- factor detection is token-pattern based, not AST-based
- there is no LLM causal scratchpad, abductive factor creation, or
  surprise-pattern inspection
- when no factor matches, it falls back to a random factor
- reward is based on change relative to the plugin's own running history

### `deep_research`

Implemented by
[`libreevolve/plugins/deep_research.py`](../libreevolve/plugins/deep_research.py).

Purpose (DeepEvolve-inspired, not paper-complete):

- periodically fetch external research context and add it to prompts

Mechanics:

- default search uses the public arXiv Atom API
- `on_generation_start()` runs a search every `search_every` generations
- the query is derived from the current best fitness
- `build_extra_context()` injects the latest synthesis into the prompt

Extension point:

- pass a custom `search_fn(query) -> str | None` to replace arXiv with another
  provider

Operational note:

- network failures are swallowed and only affect plugin context, not the run
- query/result provenance, arXiv IDs/URLs, timestamps, source hashes, and
  failure diagnostics are not persisted in run artifacts yet
- this does not implement cross-file editing, systematic debugging, or
  hypothesis refinement loops

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
  hash, but no selected operation is recorded because the plugin is static
  prompt guidance

### `ttt_rl`

Implemented by
[`libreevolve/plugins/ttt_rl.py`](../libreevolve/plugins/ttt_rl.py).

Purpose (ThetaEvolve-inspired, not paper-complete):

- accumulate `(prompt, response, reward)` training examples for future RL or
  GRPO-style fine-tuning

Mechanics:

- records data in `on_evaluated()` when prompt and diff metadata are present
- every `train_every` generations, writes the latest batch to
  `grpo_data.jsonl`
- stores `reward = max(0.0, score)`, so negative scores are clipped to zero
  rather than exported as penalties

Operational note:

- the default output path is `runs/grpo_data.jsonl`, not a per-run subdirectory
- the export file is not linked or hashed from `manifest.json` yet
- `_maybe_train()` is currently just a JSONL writer, not an actual trainer

## Adding a custom plugin

The current CLI only resolves built-in plugin names. To add a new custom plugin
without changing the loading mechanism, edit `_load_plugins()` in
[`libreevolve/cli.py`](../libreevolve/cli.py) and register it in the `reg`
dictionary.

Minimal example:

```python
from libreevolve.plugins.base import PluginBase

class LoggingPlugin(PluginBase):
    def on_generation_end(self, gen, best):
        if best is not None:
            print(f"gen={gen} best={best.fitness:.4f}")
```

If you need constructor arguments, you will also need to update the CLI or add a
problem-local configuration convention for that plugin.
