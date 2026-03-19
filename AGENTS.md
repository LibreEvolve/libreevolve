# AGENTS.md

## Project Overview

AlphaEvolve is a Python research platform for LLM-guided evolutionary program discovery. It uses SEARCH/REPLACE diffs, a cascade evaluator, MAP-Elites archives with 5-island ring migration, and a UCB1-bandit LLM ensemble.

## Tech Stack

- Python 3.11+ (use `py -3.12` on this machine, not `python`)
- Dependencies: numpy, scikit-learn, anthropic, openai, ollama, pyyaml, click, python-dotenv
- Testing: pytest, pytest-mock
- No framework — pure Python with dataclasses

## Architecture

```
alphaevolve/
  core/       loop.py (evolve + build_prompt), evaluator.py, diff.py, database.py, config.py
  llm/        ensemble.py (UCB1), anthropic.py, openai.py (Responses API for reasoning), ollama.py
  population/ program.py, map_elites.py (3D TF-IDF), islands.py (ring migration, explore/exploit)
  plugins/    base.py (ABC), causal.py, deep_research.py, modular.py, ttt_rl.py
  problems/   loader.py, examples/{hello_world,circle_packing,sorting}/
  cli.py      Click CLI with run/show commands
```

## Key Conventions

- `.env` file at project root for API keys (loaded via python-dotenv with override=True)
- `runs/` directory is gitignored — contains history.jsonl and best.py per problem
- All validate.py files run in isolated subprocesses (exec/eval is intentional)
- SEARCH/REPLACE diff format: `<<<SEARCH\n...\n===\n...\n>>>REPLACE`
- Diff engine strips markdown fences automatically
- VALID_THRESHOLD = 0.0: programs with score >= 0 enter the archive
- 30% explore / 70% exploit parent sampling
- Last 5 failed mutations shown in prompt to prevent repetition

## Running Tests

```bash
py -3.12 -m pytest tests/ -m "not integration" --tb=short    # unit tests (102)
py -3.12 -m pytest tests/integration/ -m integration          # needs ANTHROPIC_API_KEY
```

## Running the Tool

```bash
py -3.12 -m alphaevolve run alphaevolve/problems/examples/hello_world --max-generations 10 --backends openai:gpt-4o-mini
py -3.12 -m alphaevolve show runs/hello_world
```

## Common Pitfalls

- OpenAI reasoning models (gpt-5.x) use the Responses API, not Chat Completions
- xhigh reasoning effort can consume entire token budget on thinking — use high or increase max_output_tokens
- Models add markdown fences around diffs — _strip_fences() handles this
- Models add comments that break diff matching — prompt says "No comments"
- The seed program should be intentionally suboptimal to give evolution room to improve
- `config.seed` field exists but is NOT wired to random.seed() in the loop (design gap)
