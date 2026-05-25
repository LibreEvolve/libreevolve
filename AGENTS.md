# AGENTS.md

## Project Overview

LibreEvolve is a Python research platform for LLM-guided evolutionary program discovery, inspired by AlphaEvolve, Andrej Karpathy's autoresearch, and related research. It uses SEARCH/REPLACE diffs, a cascade evaluator, MAP-Elites archives with 5-island ring migration, and a heuristic UCB-style LLM ensemble.

## Tech Stack

- Python 3.11+ (use `py -3.12` on this machine, not `python`)
- Dependencies: numpy, scikit-learn, anthropic, openai, ollama, pyyaml, click, python-dotenv, pypdf
- Testing: pytest, pytest-mock
- No framework — pure Python with dataclasses

## Architecture

```
libreevolve/
  core/       loop.py (evolve + build_prompt), evaluator.py, diff.py, database.py, config.py
  llm/        ensemble.py (UCB-style heuristic), anthropic.py, openai.py (Responses API when configured), ollama.py
  population/ program.py, map_elites.py (3D TF-IDF), islands.py (ring migration, explore/exploit)
  plugins/    base.py (ABC), causal.py, deep_research.py, modular.py, ttt_rl.py
  problems/   loader.py, examples/{hello_world,circle_packing,sorting}/
  cli.py      Click CLI with run/show commands
```

## Key Conventions

- `.env` file at project root for API keys (loaded via python-dotenv with override=True)
- `runs/` directory is gitignored — contains history.jsonl and best.py per problem
- All validate.py files run in temporary local subprocesses, not security
  sandboxes (exec/eval is intentional)
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
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends openai:gpt-4o-mini
py -3.12 -m libreevolve show runs/hello_world
```

## Common Pitfalls

- OpenAI uses the Responses API only when `reasoning_effort` is configured;
  otherwise the current adapter uses Chat Completions even for model strings
  that may support reasoning
- xhigh reasoning effort can consume entire token budget on thinking — use high or increase max_output_tokens
- Models add markdown fences around diffs — _strip_fences() handles this
- Models add comments that break diff matching — prompt says "No comments"
- The seed program should be intentionally suboptimal to give evolution room to improve
- `config.seed` is wired to random.seed() at the top of evolve()
