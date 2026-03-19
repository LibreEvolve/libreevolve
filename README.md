<p align="center">
  <img src="assets/logo-mark.svg" width="80" height="80" alt="LibreEvolve logo">
</p>

<h1 align="center">LibreEvolve</h1>

<p align="center">
  <strong>Open-source AlphaEvolve alternative — LLM-guided evolutionary program discovery</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-00FF41?style=flat-square" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/python-3.11+-00D4FF?style=flat-square" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/tests-115%20passed-00FF41?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/papers-23-FFB800?style=flat-square" alt="Papers">
</p>

---

LibreEvolve is an open-source Python framework for automated algorithm discovery and code optimization using large language models (LLMs) and evolutionary computation. Inspired by [AlphaEvolve](https://arxiv.org/abs/2506.13131) (Google DeepMind, 2025), it evolves better programs through LLM-generated SEARCH/REPLACE diffs evaluated in a cascade pipeline.

Feed it a problem, a seed program, and any LLM backend (OpenAI, Anthropic Claude, or local Ollama models) — LibreEvolve evolves better solutions automatically.

Built by [Timothy Gregg](https://complete.tech) at [CompleteTech](https://complete.tech). Website: [libreevolve.com](https://libreevolve.com)

## Key Features

- **Multi-LLM support** — OpenAI (GPT-4o, GPT-5.4, o-series reasoning models), Anthropic (Claude Sonnet/Opus), and Ollama (Llama, Mistral, any local model)
- **MAP-Elites quality-diversity archive** — 3D grid mapping performance, complexity, and TF-IDF diversity so evolution explores broadly, not just greedily
- **5-island ring migration** — Parallel populations with periodic migration prevent premature convergence (70% exploit best / 30% explore random)
- **UCB1 bandit LLM ensemble** — Automatically routes mutations to the best-performing LLM backend using multi-armed bandit selection
- **Cascade evaluator** — Three-tier evaluation (diff penalties → syntax check → subprocess execution) filters bad mutations cheaply before expensive evaluation
- **SEARCH/REPLACE diff engine** — LLMs propose targeted code edits, not full rewrites — enabling precise, composable mutations
- **Failure history in prompts** — Last 5 failed mutations are shown to the LLM to prevent repetitive dead-end exploration
- **Plugin system** — 4 lifecycle hooks for extending behavior (CausalEvolve, DeepEvolve, ImprovEvolve, ThetaEvolve)
- **115 unit tests** — Comprehensive test coverage across all components

## LibreEvolve vs AlphaEvolve

| Feature | AlphaEvolve (Google DeepMind) | LibreEvolve |
|---------|-------------------------------|-------------|
| Source | Closed-source | **Open-source (MIT)** |
| LLM backends | Gemini only | **OpenAI, Anthropic, Ollama (any model)** |
| Population model | Proprietary database | **MAP-Elites with 5-island migration** |
| LLM selection | Not disclosed | **UCB1 multi-armed bandit** |
| Evaluation | Internal infrastructure | **Cascade evaluator (3 tiers)** |
| Extensibility | None | **Plugin system with 4 lifecycle hooks** |
| Local models | No | **Yes (Ollama)** |
| Research basis | 1 paper | **23 papers** |

## Getting Started

### Installation

```bash
pip install -e ".[dev]"
```

### Configuration

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_HOST=http://localhost:11434
```

### Run Your First Evolution

```bash
# OpenAI GPT-4o-mini
python -m libreevolve run libreevolve/problems/examples/circle_packing \
    --max-generations 15 --backends openai:gpt-4o-mini

# OpenAI reasoning models (GPT-5.4)
python -m libreevolve run libreevolve/problems/examples/hello_world \
    --max-generations 5 --backends openai:gpt-5.4-nano --reasoning-effort high

# Anthropic Claude
python -m libreevolve run libreevolve/problems/examples/sorting \
    --max-generations 10 --backends anthropic:claude-sonnet-4-6

# Local models via Ollama
python -m libreevolve run libreevolve/problems/examples/hello_world \
    --max-generations 20 --backends ollama:llama3
```

### Inspect Results

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

## How LLM-Guided Evolution Works

```
Seed Program -> LLM generates SEARCH/REPLACE diff
             -> Cascade Evaluator (penalty -> syntax -> subprocess)
             -> MAP-Elites archive (performance x complexity x diversity)
             -> 5-island ring-topology migration
             -> UCB1 bandit selects next LLM backend
             -> Repeat
```

Each generation:
1. **Parent selection** — Sample a parent (70% exploit best, 30% explore random from MAP-Elites grid)
2. **Prompt construction** — Build a prompt with parent code, inspiration programs, and recent failure history
3. **LLM mutation** — LLM proposes a SEARCH/REPLACE diff (targeted edit, not full rewrite)
4. **Cascade evaluation** — Score the result (Tier 0: diff penalties, Tier 1: syntax check, Tier 2: subprocess execution)
5. **Archive update** — Valid programs enter the MAP-Elites archive; all programs are logged
6. **Failure tracking** — Failed mutations are tracked and shown in subsequent prompts to avoid repeats
7. **Backend reward** — UCB1 bandit rewards the LLM backend based on fitness improvement
8. **Island migration** — Periodic migration spreads good solutions across islands

## Example Runs

### Evolving a Greeting Function

Seed returns `"Hi {name}"` (0/3 tests). The LLM discovers `f"Hello, {name}!"` in generation 0, then explores alternative implementations:

```
gen  0  -0.10  def greet(name): return f"Hi {name}"                   <- seed (wrong format)
gen  0   1.00  def greet(name): return f"Hello, {name}!"              <- solved
gen  2  -0.10  def greet(name): return f"Greetings, {name}!"          <- wrong word
gen  7   1.00  def greet(name): return "Hello, {}!".format(name)      <- .format() variant
gen  8   1.00  def greet(name): return "Hello, " + name + "!"         <- concatenation variant
```

### Evolving a Sort Algorithm

Seed is a bubble sort (already passes all 8 test cases). The LLM discovers `lst.sort()` and explores multiple implementations, all scoring 1.0:

```
gen  0   1.00  bubble sort (seed)                                     <- O(n^2)
gen  0   1.00  lst.sort()                                             <- builtin in-place
gen  1   1.00  sorted(lst)                                            <- builtin new list
gen  2   1.00  lst.copy() + sorted()                                  <- copy variant
gen  3   1.00  [x for x in lst] + sorted()                            <- list comp copy
gen  4   1.00  sorted(lst, key=lambda x: (x is None, x))              <- None-safe sort
```

### Evolving Circle Packing (Optimization)

Seed places 16 circles in a 4x4 grid (spacing 2.5). The LLM evolves toward the provably optimal 25-circle 5x5 grid:

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

## Supported LLM Backends

| Provider | Models | Features |
|----------|--------|----------|
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-5.4-nano, GPT-5.4-mini, o-series | Chat Completions + Responses API for reasoning models |
| **Anthropic** | Claude Sonnet 4.6, Claude Opus 4.6, Claude Haiku 4.5 | Messages API |
| **Ollama** | Llama 3, Mistral, Qwen, any local model | Local inference, no API key needed |

Mix backends in a single run — the UCB1 bandit automatically learns which model produces the best mutations for your problem:

```bash
python -m libreevolve run my_problem/ \
    --backends openai:gpt-4o-mini \
    --backends anthropic:claude-sonnet-4-6 \
    --backends ollama:llama3
```

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

## Creating a Custom Problem

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

## Plugin System

Plugins hook into 4 lifecycle events to extend LibreEvolve's behavior:

| Hook | When | Use case |
|------|------|----------|
| `on_generation_start(gen, db)` | Before each generation | Periodic web search, state setup |
| `build_extra_context(parent, inspirations)` | During prompt construction | Inject guidance into LLM prompt |
| `on_evaluated(program, score)` | After evaluation | Modify score, accumulate data |
| `on_generation_end(gen, best)` | After each generation | Logging, training data export |

Built-in plugins:
- **CausalEvolve** — Multi-armed bandit outcome-factor guidance
- **DeepEvolve** — Pluggable web search for research-augmented evolution
- **ImprovEvolve** — Modular decomposition prompting
- **ThetaEvolve** — GRPO training data accumulation

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
  --run-name               Custom name for this run (default: problem directory name)
  --seed                   Random seed

libreevolve show RUN_DIR
  Inspect history.jsonl from a previous run
```

## Tests

```bash
# Unit tests (115 tests)
pytest tests/ -m "not integration"

# Integration test (requires API key)
pytest tests/integration/ -m integration
```

## Benchmarks and Lessons from Live Testing

**Model selection matters more than generation count:**
- gpt-4o-mini found optimal circle packing (25 circles) in 2 generations
- gpt-5.4-mini took a longer path (16 -> 23 -> 25) but explored creative hex packing strategies along the way

**Reasoning effort tradeoffs (gpt-5.4-nano on circle packing):**

| Effort | Reasoning tokens | Response tokens | Result |
|--------|-----------------|-----------------|--------|
| none   | 0               | 347             | Hex packing (invalid, floating-point boundary) |
| high   | 608             | 119             | 5x5 grid (optimal, 25 circles) |
| xhigh  | 74,729          | 99              | 5x5 grid (same answer, 124x more tokens) |

**Prompt engineering for LLM-guided evolution:**
- Models wrap diffs in markdown fences — the diff engine strips them automatically
- Models add comments that cause diff matching failures — the prompt instructs "no comments"
- Without failure history, models repeat the same bad mutation 8+ times in a row
- A concrete diff example in the prompt prevents models from using angle-bracket placeholders literally

**Seeds determine the evolutionary landscape:**
- Suboptimal seeds (hello_world, circle_packing) produce rich evolutionary trajectories
- Already-optimal seeds (sorting's bubble sort) still evolve *different implementations* at the same fitness level

## Research Papers

Grounded in 23 research papers on LLM-guided evolutionary computation, program synthesis, and quality-diversity optimization:

**Core system papers:**

- **AlphaEvolve** — Novikov et al., "AlphaEvolve: A coding agent for scientific and algorithmic discovery," Google DeepMind, 2025. [arXiv:2506.13131](https://arxiv.org/abs/2506.13131)
- **GigaEvo** — Khrulkov et al., "GigaEvo: An Open Source Optimization Framework Powered By LLMs And Evolution Algorithms," 2025. [arXiv:2511.17592](https://arxiv.org/abs/2511.17592)
- **CodeEvolve** — Assumpção et al., "CodeEvolve: An open source evolutionary coding agent for algorithmic discovery and optimization," 2025. [arXiv:2510.14150](https://arxiv.org/abs/2510.14150)
- **ThetaEvolve** — Wang et al., "ThetaEvolve: Test-time Learning on Open Problems," 2025. [arXiv:2511.23473](https://arxiv.org/abs/2511.23473)
- **ImprovEvolve** — Kravatskiy, Khrulkov & Oseledets, "ImprovEvolve: Ask AlphaEvolve to Improve the Input Solution and Then Improvise," 2026. [arXiv:2602.10233](https://arxiv.org/abs/2602.10233)
- **MadEvolve** — Li, Zang & Münchmeyer, "MadEvolve: Evolutionary Optimization of Cosmological Algorithms with Large Language Models," 2026. [arXiv:2602.15951](https://arxiv.org/abs/2602.15951)
- **CausalEvolve** — Chen et al., "CausalEvolve: Towards Open-Ended Discovery with Causal Scratchpad," 2026. [arXiv:2603.14575](https://arxiv.org/abs/2603.14575)
- **DeepEvolve** — Liu et al., "Scientific Algorithm Discovery by Augmenting AlphaEvolve with Deep Research," 2025. [arXiv:2510.06056](https://arxiv.org/abs/2510.06056)

**Foundational algorithms:**

- **MAP-Elites** — Mouret & Clune, "Illuminating search spaces by mapping elites," 2015.
- **UCB1** — Auer, Cesa-Bianchi & Fischer, "Finite-time Analysis of the Multiarmed Bandit Problem," 2002.

See `docs/superpowers/specs/2026-03-17-alphaevolve-design.md` Section 15 for the full list of all 23 papers with roles.

## Contributing

Contributions welcome. Please run `pytest tests/ -m "not integration"` before submitting PRs.

## License

[MIT](LICENSE) — [Timothy Gregg](https://complete.tech) / [CompleteTech](https://complete.tech)
