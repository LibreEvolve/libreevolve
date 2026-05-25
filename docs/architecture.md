# Architecture

LibreEvolve is a Python research framework for LLM-guided program mutation. It
is AlphaEvolve-inspired, but intentionally smaller: the current runtime is
synchronous, Python-only, and filesystem-backed.

## Top-level flow

The CLI entrypoint is [`libreevolve/cli.py`](../libreevolve/cli.py). The `run`
command:

- loads `.env` with `override=True`
- loads a problem directory with `load_problem()`
- merges problem-local `config.yaml` into the default `Config`
- instantiates built-in plugins named on the CLI
- calls `evolve(problem, config, plugins)`
- writes the best archived program to `runs/<problem_name>/best.py`

## Problem loading

`load_problem()` in [`libreevolve/problems/loader.py`](../libreevolve/problems/loader.py)
constructs a `Problem` from:

- `task_description.txt`
- `metrics.yaml`
- `validate.py`
- `initial_programs/*.py` or seed directories under `initial_programs/`
- optional `context/*.{txt,md,py}`

The loader keeps all declared metrics, picks a primary metric, and exposes
metric direction/bounds helpers. Fitness is the normalized primary metric:
`maximize` maps low-to-high bounds to `0..1`; `minimize` inverts that scale.

## Candidate representation

Candidates use `CandidateWorkspace`: a text file set with a `primary_file`.
`Program.code` remains as a compatibility view of the primary file, so existing
single-file seeds, validators, prompts, and `best.py` workflows still work.
Seed files may mark evolvable regions:

```python
# EVOLVE-BLOCK-START main
def solve():
    return 1
# EVOLVE-BLOCK-END
```

Mutation application lives in [`libreevolve/core/candidate.py`](../libreevolve/core/candidate.py).
When markers are present, surrounding skeleton code is preserved and mutations
are constrained to marked regions. Multiple blocks are supported. Existing
unmarked `initial_programs/*.py` remain valid.

Two mutation modes are supported:

- `diff`: default SEARCH/REPLACE blocks
- `full`: complete replacement of the whole unmarked program, the single marked
  block, or named multi-block replacements with `<<<BLOCK name ... >>>BLOCK`

For multi-file candidates, LLM responses can wrap edits in file sections:

```text
<<<FILE package/module.py
<<<SEARCH
old code
===
new code
>>>REPLACE
>>>FILE
```

`full` mode can replace existing files or create new files with the same
`<<<FILE path ... >>>FILE` envelope. Candidate paths are normalized and cannot
escape the candidate workspace.

## Evolution loop

The core loop lives in [`libreevolve/core/loop.py`](../libreevolve/core/loop.py).
For each generation it:

1. runs plugin start hooks
2. samples a parent from the island model
3. samples diverse inspirations
4. builds prompt context through `PromptSampler`
5. calls the LLM ensemble
6. applies the configured mutation mode
7. evaluates the child
8. constructs a `Program` with metrics and structured evaluation data
9. runs plugin score hooks
10. logs the candidate and archives valid programs
11. rewards the selected backend with non-negative fitness improvement
12. migrates elites at the configured interval

`VALID_THRESHOLD` is currently `0.0`.

## Prompt sampling

[`libreevolve/core/prompt.py`](../libreevolve/core/prompt.py) provides
`PromptSampler`. It renders:

- task description
- explicit problem context files
- parent code, normalized fitness, metrics, and recent stage feedback
- multi-file parent/inspiration contents when present
- inspiration programs with metrics
- plugin-provided context
- recent failed mutations

`Config.prompt_variants` can supply alternate templates. There is not yet a
meta-prompt database or prompt-evolution controller.

## Evaluation

[`libreevolve/core/evaluator.py`](../libreevolve/core/evaluator.py) returns an
`EvaluationResult` instead of a bare float. It includes:

- normalized primary `fitness`
- raw validator `metrics`
- `is_valid`
- per-stage outcomes
- stdout, stderr, error, elapsed time, and metadata

For compatibility, `EvaluationResult` can still be compared/subtracted like a
numeric fitness in existing tests and callers.

The default cascade is:

- mutation/diff penalty
- Python syntax check across all candidate `.py` files
- subprocess execution of `validate.py` with the candidate workspace

`Config.eval_stages` can configure repeated validator stages with per-stage
timeouts and `min_score` thresholds. Validators may keep the old
`evaluate(code)` signature or opt into `evaluate(code, workspace_path)`.
This is an initial local cascade model, not AlphaEvolve's full parallel
evaluator-worker architecture.

## Population model

Population state is split across:

- `Program`: primary code, candidate files, fitness, lineage, metadata,
  metrics, and evaluation summary
- `MAPElites`: one quality-diversity archive
- `IslandModel`: multiple archives plus ring migration

`MAPElites` maps programs into a 3D grid using normalized performance, code
length, and TF-IDF char-4gram diversity. Performance bounds now use the
problem's normalized `0..1` fitness scale.

LibreEvolve stores metric vectors, but its multi-objective policy is still a
first pass: archive comparison and backend rewards use normalized primary
fitness. Richer Pareto/frontier sampling remains open.

## Backend selection

[`libreevolve/llm/ensemble.py`](../libreevolve/llm/ensemble.py) wraps one or
more backends. The default `ensemble_strategy` is `ucb1`, implemented as a
heuristic adaptation of UCB1 over observed fitness improvements.

An experimental `throughput_depth` strategy layers optional backend metadata
(`cost`, `latency`, `depth`, `role`) over UCB scores so configs can distinguish
cheap breadth models from deeper models. This is a scheduling concept, not a
verified reproduction of AlphaEvolve's Gemini Flash/Pro policy.

## Logging and artifacts

[`libreevolve/core/database.py`](../libreevolve/core/database.py) writes:

- `manifest.json`: effective run configuration and runtime metadata
- `history.jsonl`: append-only candidate records
- `best.py`: final best archived program

Each history record includes primary code, candidate files, primary file,
fitness, lineage, metadata, metrics, and the structured evaluation summary.

## Known gaps

- Candidate workspaces are local text file sets, not arbitrary-language build
  systems or external repositories.
- The loop is synchronous; async LLM/evaluator workers are not implemented.
- There is no LLM critique stage or LLM-generated feedback evaluator.
- Prompt evolution is architected only at the template boundary.
- Plugin names are paper-inspired approximations unless documented otherwise.
