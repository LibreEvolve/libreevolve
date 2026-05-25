# Example Runs

These histories are checked into Git as curated examples. They were kept because they show intended system behavior, not just raw output dumps. Fresh runs still belong under the ignored `runs/` directory.

## Kept examples

- `hello_world_ensemble/`: 11 records. Starts from a failing seed and reaches the correct greeting in generation 0. Useful for showing immediate improvement from a bad seed plus subsequent failed and successful variants.
- `sorting_ttt_rl/`: 56 records. Starts from an already-correct bubble sort and explores multiple equally valid implementations (`lst.sort()`, `sorted(lst)`, copy variants). Useful for showing neutral drift and implementation diversity at constant fitness.

## How to inspect them

```bash
py -3.12 -m libreevolve show examples/runs/hello_world_ensemble
py -3.12 -m libreevolve show examples/runs/sorting_ttt_rl
```
