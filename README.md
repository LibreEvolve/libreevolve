# AlphaEvolve

LLM-guided evolutionary program discovery. Feed it a problem, a seed program, and an LLM backend — it evolves better solutions using SEARCH/REPLACE diffs evaluated in a cascade pipeline.

Grounded in 22 research papers. Built as a research platform, not a production tool.

## Quick Start

```bash
pip install -e ".[dev]"
```

Create a `.env` file:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_HOST=http://localhost:11434
```

Run on a bundled problem:

```bash
# OpenAI
python -m alphaevolve run alphaevolve/problems/examples/circle_packing \
    --max-generations 15 --backends openai:gpt-4o-mini

# With reasoning (OpenAI reasoning models)
python -m alphaevolve run alphaevolve/problems/examples/hello_world \
    --max-generations 5 --backends openai:gpt-5.4-nano --reasoning-effort high

# Anthropic
python -m alphaevolve run alphaevolve/problems/examples/sorting \
    --max-generations 10 --backends anthropic:claude-sonnet-4-6

# Ollama (local)
python -m alphaevolve run alphaevolve/problems/examples/hello_world \
    --max-generations 20 --backends ollama:llama3
```

Inspect results:

```bash
python -m alphaevolve show runs/circle_packing
```

## How It Works

```
Seed Program → LLM generates SEARCH/REPLACE diff
             → Cascade Evaluator (penalty → syntax → subprocess)
             → MAP-Elites archive (performance × complexity × diversity)
             → 5-island ring-topology migration
             → UCB1 bandit selects next LLM backend
             → Repeat
```

Each generation:
1. Sample a parent from the population (exploit strategy)
2. Build a prompt with parent code + inspiration programs
3. LLM proposes a SEARCH/REPLACE diff
4. Cascade evaluator scores the result (Tier 0: diff penalties → Tier 1: syntax check → Tier 2: subprocess execution)
5. Valid programs enter the MAP-Elites archive; all programs are logged
6. UCB1 bandit rewards the backend based on fitness improvement
7. Periodic island migration spreads good solutions

## Architecture

```
alphaevolve/
├── core/
│   ├── loop.py          # evolve() main loop + build_prompt()
│   ├── evaluator.py     # Cascade evaluator (Tier 0/1/2)
│   ├── diff.py          # SEARCH/REPLACE diff engine
│   ├── database.py      # ProgramDatabase facade
│   └── config.py        # Config dataclass
├── llm/
│   ├── ensemble.py      # UCB1-bandit LLM ensemble
│   ├── anthropic.py     # Claude backend
│   ├── openai.py        # OpenAI backend (+ Responses API for reasoning models)
│   └── ollama.py        # Ollama backend
├── population/
│   ├── program.py       # Program dataclass
│   ├── map_elites.py    # 3D MAP-Elites (TF-IDF char-4gram diversity)
│   └── islands.py       # 5-island ring migration
├── plugins/
│   ├── base.py          # PluginBase ABC (4 lifecycle hooks)
│   ├── causal.py        # CausalEvolve — MAB outcome-factor guidance
│   ├── deep_research.py # DeepEvolve — pluggable web search
│   ├── modular.py       # ImprovEvolve — modular decomposition prompting
│   └── ttt_rl.py        # ThetaEvolve — GRPO training data accumulation
└── problems/
    ├── loader.py         # load_problem() + Problem dataclass
    └── examples/         # hello_world, circle_packing, sorting
```

## Creating a Problem

A problem is a directory with four files:

```
my_problem/
├── task_description.txt          # What the LLM should optimize
├── metrics.yaml                  # Scoring metrics
├── validate.py                   # evaluate(code: str) -> dict
└── initial_programs/
    └── seed.py                   # Starting program
```

**metrics.yaml:**
```yaml
metrics:
  - name: score
    direction: maximize
    primary: true
    bounds: [0.0, 1.0]
  - name: is_valid
    direction: maximize
    primary: false
```

**validate.py** must define `evaluate(code: str) -> dict` returning a dict with all metric names. It runs in an isolated subprocess.

## Plugins

Plugins hook into 4 lifecycle events:

| Hook | When | Use case |
|------|------|----------|
| `on_generation_start(gen, db)` | Before each generation | Periodic web search, state setup |
| `build_extra_context(parent, inspirations)` | During prompt construction | Inject guidance into LLM prompt |
| `on_evaluated(program, score)` | After evaluation | Modify score, accumulate data |
| `on_generation_end(gen, best)` | After each generation | Logging, training data export |

```bash
python -m alphaevolve run my_problem/ --plugins causal --plugins deep_research
```

## CLI Reference

```
alphaevolve run PROBLEM_DIR [OPTIONS]
  --max-generations, -g    Number of generations (default: 1000)
  --backends, -b           LLM backend as type:model (repeatable)
  --plugins, -p            Plugin name (repeatable)
  --reasoning-effort, -r   Reasoning effort for OpenAI models (low/medium/high/xhigh)
  --seed                   Random seed

alphaevolve show RUN_DIR
  Inspect history.jsonl from a previous run
```

## Tests

```bash
# Unit tests
pytest tests/ -m "not integration"

# Integration test (requires API key)
pytest tests/integration/ -m integration
```

## Lessons from Live Testing

- **gpt-4o-mini** found optimal circle packing (25 circles) in 2 generations
- **gpt-5.4-nano with xhigh reasoning** consumed 75k tokens thinking, produced the same answer that `high` found in 608 tokens
- **Reasoning models with no thinking** tried creative hex packing but failed on floating-point boundary conditions
- **Token budget matters** — reasoning models need `max_output_tokens` large enough for both thinking and response
- Seeds that are already optimal (like the bubble sort) leave nothing to evolve

## References

Based on 22 papers including AlphaEvolve (Google DeepMind), MAP-Elites, CausalEvolve, ImprovEvolve, ThetaEvolve, and others. See `docs/superpowers/specs/2026-03-17-alphaevolve-design.md` Section 15 for the full list.
