# AGENTS.md

## Project Overview

LibreEvolve is a Python research platform for LLM-guided evolutionary program discovery, inspired by AlphaEvolve, Andrej Karpathy's autoresearch, and related research. It uses SEARCH/REPLACE diffs, a cascade evaluator, configurable MAP-Elites island archives with five islands by default, and a heuristic UCB-style LLM ensemble.

## Tech Stack

- Python 3.11+ (use `py -3.12` on this machine, not `python`)
- Dependencies: numpy, scikit-learn, anthropic, openai, ollama, pyyaml, click, python-dotenv, packaging, pypdf
- Testing: pytest, pytest-mock
- No framework — pure Python with dataclasses

## Architecture

```
libreevolve/
  core/       loop.py (evolve orchestration), prompt.py (PromptSampler), evaluator.py, diff.py, database.py, config.py
  llm/        ensemble.py (UCB-style heuristic), anthropic.py, openai.py (Responses API when configured), ollama.py
  population/ program.py, map_elites.py (3D TF-IDF), islands.py (ring migration, explore/exploit)
  plugins/    base.py (ABC), causal.py, deep_research.py, modular.py, ttt_rl.py
  problems/   loader.py, examples/{hello_world,circle_packing,sorting,matrix_multiplication,workspace_math}/
  cli.py      Click CLI with run/show commands
```

## Key Conventions

- `.env` file at project root for API keys (loaded via python-dotenv with override=True)
- `runs/` directory is gitignored — contains manifest.json, history.jsonl,
  failure/quarantine JSONL streams, archive_events.jsonl, llm_calls.jsonl,
  prompt_history.jsonl, best.py, best_workspace/, evaluator_artifacts/, and
  plugin_artifacts/ per problem
- Validator execution and CLI/direct contract preflight run in temporary local
  subprocesses, not security sandboxes; validator modules are not imported in
  the parent CLI/runtime process during preflight
- SEARCH/REPLACE diff format: use canonical AlphaEvolve fences
  `<<<<<<< SEARCH\n...\n=======\n...\n>>>>>>> REPLACE`; the compact
  `<<<SEARCH\n...\n===\n...\n>>>REPLACE` spelling remains accepted as
  compatibility input.
- Diff engine strips a single outer markdown fence wrapper automatically
- VALID_THRESHOLD = 0.0 is the pre-admission eligibility gate. A valid finite
  program with score >= 0 is passed to ProgramDatabase.admit(), but MAP-Elites
  cell replacement/elite retention can still reject it (for example
  reason="not_improving_cell"), and only retained/search-state entries become
  sampling_eligible.
- Default `mixed` parent sampling uses 30% explore / 70% exploit; explicit
  parent-selection strategies bypass that ratio
- Failed/rejected candidates are persisted to `failure_history.jsonl`, and
  prompts render bounded recent failure memory with configurable filters and
  limits; durable cross-run/semantic failed-proposal memory remains open work

## Running Tests

```bash
py -3.12 -m pytest tests/ -m "not integration" --tb=short
py -3.12 -m pytest tests/integration/ -m integration          # needs ANTHROPIC_API_KEY
```

## Running the Tool

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "openai:<openai-model-id>"
py -3.12 -m libreevolve show runs/hello_world
```

Replace placeholder backend model ids with currently available provider/account
model ids before running.

## Common Pitfalls

- OpenAI uses Chat Completions by default; explicit `api_mode: responses` or
  configured `reasoning_effort` routes through the Responses API. `api_mode:
  auto` without reasoning preserves Chat Completions even for model strings
  that may support reasoning
- xhigh reasoning effort can consume entire token budget on thinking — use high or increase max_output_tokens
- Models add markdown fences around diffs — _strip_fences() handles one outer response wrapper
- Models add comments that break diff matching — prompt says "No comments"
- The seed program should be intentionally suboptimal to give evolution room to improve
- `config.seed` initializes the run-local framework `random.Random`; `evolve()`
  no longer reseeds Python's process-global `random` module
