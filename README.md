# LibreEvolve

Open-source LLM-guided evolutionary program discovery, inspired by [AlphaEvolve](https://arxiv.org/abs/2506.13131) (Google DeepMind). Feed it a problem, a seed program, and an LLM backend — it evolves better solutions using SEARCH/REPLACE diffs evaluated in a cascade pipeline.

Grounded in 23 research papers. Built as a research platform, not a production tool.

Built by [CompleteTech](https://complete.tech).

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
python -m libreevolve run libreevolve/problems/examples/circle_packing \
    --max-generations 15 --backends openai:gpt-4o-mini

# With reasoning (OpenAI reasoning models)
python -m libreevolve run libreevolve/problems/examples/hello_world \
    --max-generations 5 --backends openai:gpt-5.4-nano --reasoning-effort high

# Anthropic
python -m libreevolve run libreevolve/problems/examples/sorting \
    --max-generations 10 --backends anthropic:claude-sonnet-4-6

# Ollama (local)
python -m libreevolve run libreevolve/problems/examples/hello_world \
    --max-generations 20 --backends ollama:llama3
```

Inspect results:

```bash
python -m libreevolve show runs/circle_packing
```

```
Total programs: 16
Best fitness:   25.000000 (generation 5)

--- Best program ---

def solve():
    return [(1.0 + i * 2.0, 1.0 + j * 2.0) for i in range(5) for j in range(5)]
```

## How It Works

```
Seed Program -> LLM generates SEARCH/REPLACE diff
             -> Cascade Evaluator (penalty -> syntax -> subprocess)
             -> MAP-Elites archive (performance x complexity x diversity)
             -> 5-island ring-topology migration
             -> UCB1 bandit selects next LLM backend
             -> Repeat
```

Each generation:
1. Sample a parent (70% exploit best, 30% explore random from MAP-Elites grid)
2. Build a prompt with parent code, inspiration programs, and recent failure history
3. LLM proposes a SEARCH/REPLACE diff
4. Cascade evaluator scores the result (Tier 0: diff penalties, Tier 1: syntax check, Tier 2: subprocess execution)
5. Valid programs enter the MAP-Elites archive; all programs are logged
6. Failed mutations are tracked and shown in subsequent prompts to avoid repeats
7. UCB1 bandit rewards the backend based on fitness improvement
8. Periodic island migration spreads good solutions

## Example Runs

### hello_world — Evolving a greeting function

Seed returns `"Hi {name}"` (0/3 tests). The LLM discovers `f"Hello, {name}!"` in generation 0, then explores alternative implementations:

```
gen  0  -0.10  def greet(name): return f"Hi {name}"                   <- seed (wrong format)
gen  0   1.00  def greet(name): return f"Hello, {name}!"              <- solved
gen  2  -0.10  def greet(name): return f"Greetings, {name}!"          <- wrong word
gen  7   1.00  def greet(name): return "Hello, {}!".format(name)      <- .format() variant
gen  8   1.00  def greet(name): return "Hello, " + name + "!"         <- concatenation variant
```

### sorting — Evolving a sort algorithm

Seed is a bubble sort (already passes all 8 test cases). The LLM discovers `lst.sort()` and explores multiple implementations, all scoring 1.0:

```
gen  0   1.00  bubble sort (seed)                                     <- O(n^2)
gen  0   1.00  lst.sort()                                             <- builtin in-place
gen  1   1.00  sorted(lst)                                            <- builtin new list
gen  2   1.00  lst.copy() + sorted()                                  <- copy variant
gen  3   1.00  [x for x in lst] + sorted()                            <- list comp copy
gen  4   1.00  sorted(lst, key=lambda x: (x is None, x))              <- None-safe sort
```

### circle_packing — Packing circles in a 10x10 square

Seed places 16 circles in a 4x4 grid (spacing 2.5). The LLM evolves toward the optimal 25-circle 5x5 grid:

```
gen  0  16.00  4x4 grid, spacing 2.5                                 <- seed
gen  0  16.00  4x4 grid, spacing 2.0 (tighter but same count)
gen  5  25.00  5x5 grid, spacing 2.0                                 <- optimal (proven)
gen  7  -0.10  6x4 grid (out of bounds)
gen  9  -0.10  diagonal offset (overlap)
gen 10  -0.10  hex stagger with (j%2) offset (overlap)
gen 13  16.00  4x4 grid, offset 1.5 (exploring from non-best parent)
```

25 circles is provably optimal for this geometry ([1.0, 9.0]^2, min distance 2.0).

## Architecture

```
libreevolve/
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
│   └── islands.py       # 5-island ring migration (30% explore / 70% exploit)
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

**Tip:** Make your seed program intentionally suboptimal. If the seed already scores perfectly, there's nothing to evolve.

## Plugins

Plugins hook into 4 lifecycle events:

| Hook | When | Use case |
|------|------|----------|
| `on_generation_start(gen, db)` | Before each generation | Periodic web search, state setup |
| `build_extra_context(parent, inspirations)` | During prompt construction | Inject guidance into LLM prompt |
| `on_evaluated(program, score)` | After evaluation | Modify score, accumulate data |
| `on_generation_end(gen, best)` | After each generation | Logging, training data export |

```bash
python -m libreevolve run my_problem/ --plugins causal --plugins deep_research
```

## CLI Reference

```
libreevolve run PROBLEM_DIR [OPTIONS]
  --max-generations, -g    Number of generations (default: 1000)
  --backends, -b           LLM backend as type:model (repeatable)
  --plugins, -p            Plugin name (repeatable)
  --reasoning-effort, -r   Reasoning effort for OpenAI models (none/low/medium/high/xhigh)
  --seed                   Random seed

libreevolve show RUN_DIR
  Inspect history.jsonl from a previous run
```

## Tests

```bash
# Unit tests (102 tests)
pytest tests/ -m "not integration"

# Integration test (requires API key)
pytest tests/integration/ -m integration
```

## Lessons from Live Testing

**Model selection matters more than generation count:**
- gpt-4o-mini found optimal circle packing (25 circles) in 2 generations
- gpt-5.4-mini took a longer path (16 -> 23 -> 25) but explored creative hex packing strategies along the way

**Reasoning effort tradeoffs (gpt-5.4-nano on circle packing):**

| Effort | Reasoning tokens | Response tokens | Result |
|--------|-----------------|-----------------|--------|
| none   | 0               | 347             | Hex packing (invalid, floating-point boundary) |
| high   | 608             | 119             | 5x5 grid (optimal, 25 circles) |
| xhigh  | 74,729          | 99              | 5x5 grid (same answer, 124x more tokens) |

**Prompt engineering for evolution:**
- Models wrap diffs in markdown fences — the diff engine strips them automatically
- Models add comments that cause diff matching failures — the prompt instructs "no comments"
- Without failure history, models repeat the same bad mutation 8+ times in a row
- A concrete diff example in the prompt prevents models from using angle-bracket placeholders literally

**Seeds determine the evolutionary landscape:**
- Suboptimal seeds (hello_world, circle_packing) produce rich evolutionary trajectories
- Already-optimal seeds (sorting's bubble sort) still evolve *different implementations* at the same fitness level

## References

Grounded in 23 research papers. Core system papers:

- **AlphaEvolve** — Novikov et al., "AlphaEvolve: A coding agent for scientific and algorithmic discovery," Google DeepMind, 2025. [arXiv:2506.13131](https://arxiv.org/abs/2506.13131)
- **GigaEvo** — Khrulkov et al., "GigaEvo: An Open Source Optimization Framework Powered By LLMs And Evolution Algorithms," 2025. [arXiv:2511.17592](https://arxiv.org/abs/2511.17592)
- **CodeEvolve** — Assumpção et al., "CodeEvolve: An open source evolutionary coding agent for algorithmic discovery and optimization," 2025. [arXiv:2510.14150](https://arxiv.org/abs/2510.14150)
- **ThetaEvolve** — Wang et al., "ThetaEvolve: Test-time Learning on Open Problems," 2025. [arXiv:2511.23473](https://arxiv.org/abs/2511.23473)
- **ImprovEvolve** — Kravatskiy, Khrulkov & Oseledets, "ImprovEvolve: Ask AlphaEvolve to Improve the Input Solution and Then Improvise," 2026. [arXiv:2602.10233](https://arxiv.org/abs/2602.10233)
- **MadEvolve** — Li, Zang & Münchmeyer, "MadEvolve: Evolutionary Optimization of Cosmological Algorithms with Large Language Models," 2026. [arXiv:2602.15951](https://arxiv.org/abs/2602.15951)
- **CausalEvolve** — Chen et al., "CausalEvolve: Towards Open-Ended Discovery with Causal Scratchpad," 2026. [arXiv:2603.14575](https://arxiv.org/abs/2603.14575)
- **DeepEvolve** — Liu et al., "Scientific Algorithm Discovery by Augmenting AlphaEvolve with Deep Research," 2025. [arXiv:2510.06056](https://arxiv.org/abs/2510.06056)

Foundational algorithms:

- **MAP-Elites** — Mouret & Clune, "Illuminating search spaces by mapping elites," 2015.
- **UCB1** — Auer, Cesa-Bianchi & Fischer, "Finite-time Analysis of the Multiarmed Bandit Problem," 2002.

See `docs/superpowers/specs/2026-03-17-alphaevolve-design.md` Section 15 for the full list of all 23 papers with roles.

## License

[MIT](LICENSE) — Timothy Gregg / [CompleteTech](https://complete.tech)
