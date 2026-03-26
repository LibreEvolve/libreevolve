# LibreEvolve — Design Specification
**Date:** 2026-03-17
**Language:** Python
**LLM Backend:** Pluggable (Anthropic, OpenAI, Ollama, Ensemble)
**Type:** Research tool — flexible experimentation platform for LLM-guided evolutionary algorithm discovery

---

## 1. Overview

LibreEvolve is a Python research tool for LLM-guided evolutionary algorithm and program discovery. It is an independent implementation inspired by AlphaEvolve, autoresearch, and adjacent literature. It combines an evolutionary computation engine with pluggable LLM backends to iteratively generate, evaluate, and evolve candidate programs. The architecture is layered: a minimal runnable core with well-defined extension slots that allow advanced research techniques from the literature to be activated as plugins.

**Grounded in:** 23 research papers. See Section 15 (References) for the full list.

---

## 2. Directory Structure

```
alphaevolve/
├── core/
│   ├── loop.py          # Main evolution loop
│   ├── database.py      # Facade over MAP-Elites + island model
│   ├── diff.py          # SEARCH/REPLACE diff engine
│   ├── evaluator.py     # Cascade evaluator (fast → authoritative)
│   └── config.py        # Dataclasses for all configuration
├── llm/
│   ├── base.py          # LLMBackend protocol (per-backend interface)
│   ├── ensemble.py      # LLMEnsemble: UCB1 bandit; returned by build_llm()
│   ├── anthropic.py     # Claude (Sonnet/Opus/Haiku)
│   ├── openai.py        # GPT-4o / o3 / o4-mini
│   └── ollama.py        # Local models via Ollama
├── population/
│   ├── program.py       # Program dataclass (code, fitness, lineage)
│   ├── map_elites.py    # 3D MAP-Elites archive
│   └── islands.py       # Island model + ring-topology migration
├── plugins/
│   ├── base.py          # PluginBase ABC with no-op default hooks
│   ├── causal.py        # CausalEvolve: scratchpad + MAB factor guidance
│   ├── deep_research.py # DeepEvolve: web search + hypothesis synthesis
│   ├── modular.py       # ImprovEvolve: generate_config/improve/perturb
│   └── ttt_rl.py        # ThetaEvolve: test-time RL with GRPO
├── problems/
│   ├── loader.py        # Loads problem spec from directory
│   └── examples/
│       ├── circle_packing/
│       ├── sorting/
│       └── hello_world/
└── cli.py               # `python -m alphaevolve run problems/my_problem`
```

**Note on `core/database.py`:** This is a facade. It imports and coordinates `population/map_elites.py` (the archive) and `population/islands.py` (the island model); it does not re-implement either.

---

## 3. Core Evolution Loop

### 3.1 Main Loop (`core/loop.py`)

```python
VALID_THRESHOLD = 0.0  # scores below this are structural failures; not archived

def evolve(problem: Problem, config: Config, plugins: list[PluginBase] = []) -> Program:
    db        = ProgramDatabase(config)
    evaluator = CascadeEvaluator(problem)
    llm       = build_llm(config)   # returns LLMEnsemble; see Section 5.2

    # Seed population (error_reason=None bypasses Tier 0; see Section 7)
    for seed_code in problem.initial_programs:
        score   = evaluator.evaluate(seed_code, diff_error=None)
        program = Program(code=seed_code, fitness=score)
        db.log(program)           # always log — seeds included
        db.add(program)

    for gen in range(config.max_generations):
        for plugin in plugins: plugin.on_generation_start(gen, db)

        parent       = db.sample(strategy="exploit")
        inspirations = db.sample_diverse(k=config.num_inspirations)

        context  = "\n".join(p.build_extra_context(parent, inspirations) for p in plugins)
        prompt   = build_prompt(parent, inspirations, problem, context)
        diff, backend_idx = llm.generate(prompt)          # LLMEnsemble returns (str, int)
        child_code, diff_error = apply_diff(parent.code, diff)

        score   = evaluator.evaluate(child_code, diff_error=diff_error)

        # Construct Program object BEFORE calling on_evaluated
        program = Program(code=child_code, fitness=score,
                          parent_id=parent.id, generation=gen)

        for plugin in plugins: score = plugin.on_evaluated(program, score)
        program.fitness = score   # update with plugin-modified score

        # Only archive structurally valid programs; always log everything
        db.log(program)           # appends to history.jsonl unconditionally
        if score >= VALID_THRESHOLD:
            db.add(program)       # adds to MAP-Elites + island + elite archive

        # UCB1 reward: clamped to non-negative to satisfy bandit assumptions
        llm.record_reward(backend_idx, max(0.0, score - parent.fitness))

        db.maybe_migrate(gen)     # ring-topology island migration

        for plugin in plugins: plugin.on_generation_end(gen, db.best())

    return db.best()
```

### 3.2 Program Dataclass (`population/program.py`)

```python
@dataclass
class Program:
    id:         str   = field(default_factory=lambda: uuid4().hex)
    code:       str   = ""
    fitness:    float = -inf
    generation: int   = 0
    parent_id:  str | None = None
    lineage:    list[str]  = field(default_factory=list)
    metadata:   dict       = field(default_factory=dict)
```

### 3.3 Lazy Penalty System (ThetaEvolve)

| Condition | `diff_error` value | Score |
|-----------|-------------------|-------|
| No diff blocks in LLM output | `"no_diff_blocks"` | −0.4 |
| Diff applied but code unchanged | `"no_valid_changes"` | −0.3 |
| Search text not found in code | `"search_not_found"` | −0.3 (treated as `no_valid_changes`) |
| Python syntax error | n/a (Tier 1) | −0.2 |
| Execution error / timeout | n/a (Tier 2) | −0.2 |
| Executed but domain-invalid | n/a (Tier 2) | −0.1 |
| Valid — use primary metric | `None` | ≥ 0.0 |

Scores below `VALID_THRESHOLD = 0.0` are logged but **not added to the archive**.
Negative scores still drive UCB1 reward updates (clamped to 0 before recording).

---

## 4. Population Management

### 4.1 MAP-Elites Archive (`population/map_elites.py`)

**Behavioral dimensions** (MadEvolve / GigaEvo consensus):

| Dimension | Measurement | Normalization |
|-----------|-------------|---------------|
| **Performance** | Raw fitness score | Bounded by `metrics.yaml` bounds |
| **Complexity** | Code length in characters | Max observed across run |
| **Diversity** | Mean TF-IDF cosine distance to the global elite archive | Min–max scaled to [0, 1] |

*Diversity computation:* TF-IDF vectors use character 4-grams. The reference set is the current global elite archive (up to 50 programs), recomputed at each generation before the archive update. This lives in `map_elites.py`.

Each 10×10×10 grid cell holds the single best program for that behavioral profile. Replacement occurs only when the incoming program has strictly higher fitness than the cell's occupant.

### 4.2 Island Model (`population/islands.py`)

- **5 independent islands**, each with its own MAP-Elites archive
- **Ring topology migration**: island i → island (i+1) % n
- **Migration every 25 generations**, copying (not moving) 10% of each island's elite
- Global elite archive (top-50 by fitness) is never evicted regardless of MAP-Elites cell replacement

**Rationale:** Ring topology outperforms complete graph (diversity loss) and no migration (premature convergence) per CodeEvolve ablations.

### 4.3 Database Facade (`core/database.py`)

```
ProgramDatabase
├── imports: IslandModel (population/islands.py)
│            └── 5 × MAPElites (population/map_elites.py)
├── elite_archive: list[Program]     # top-50 globally, never evicted
├── all_programs:  list[Program]     # full in-memory history
└── _jsonl_path:   Path              # runs/<name>/history.jsonl

Public API:
  add(program)          → insert into island model + elite archive (valid only)
  log(program)          → append to all_programs + history.jsonl (always)
  sample(strategy)      → draw from islands
  sample_diverse(k)     → draw from k different MAP-Elites cells
  best()                → top program from elite_archive
  maybe_migrate(gen)    → trigger island migration if gen % interval == 0
```

---

## 5. LLM Layer

### 5.1 Backend Protocol (`llm/base.py`)

Each concrete backend implements this interface:

```python
class LLMBackend(Protocol):
    def generate(self, prompt: str, **kwargs) -> str: ...   # returns raw text
    @property
    def name(self) -> str: ...
```

Implemented by: `AnthropicBackend`, `OpenAIBackend`, `OllamaBackend`.

### 5.2 LLMEnsemble (`llm/ensemble.py`)

`build_llm(config) -> LLMEnsemble` constructs the ensemble from `config.backends`.
The ensemble wraps one or more `LLMBackend` instances and exposes a **different** interface to the loop:

```python
class LLMEnsemble:
    def generate(self, prompt: str) -> tuple[str, int]:
        """Returns (diff_text, backend_index)."""
        idx      = self._ucb1_select()
        response = self.backends[idx].generate(prompt)
        self.counts[idx] += 1
        return response, idx

    def record_reward(self, idx: int, reward: float) -> None:
        """reward must be ≥ 0 (caller is responsible for clamping)."""
        self.wins[idx] += reward

    def _ucb1_select(self) -> int:
        self.total += 1
        scores = [
            (self.wins[i] / max(self.counts[i], 1))
            + self.c * math.sqrt(math.log(self.total) / max(self.counts[i], 1))
            for i in range(len(self.backends))
        ]
        return int(np.argmax(scores))
```

**Separation of concerns:**
- `LLMBackend.generate()` → `str` (per-backend, knows nothing about ensemble)
- `LLMEnsemble.generate()` → `tuple[str, int]` (routing layer, what the loop calls)

When only one backend is configured, `build_llm` wraps it in a single-element ensemble.

### 5.3 Prompt Structure

```
[SYSTEM]
You are an expert programmer evolving solutions for: {task_description}

[CURRENT BEST PROGRAM — score: {parent.fitness:.4f}]
```python
{parent.code}
```

[INSPIRATION PROGRAMS]
--- Inspiration 1 (score {ins[0].fitness:.4f}) ---
...

[EVALUATION FEEDBACK]
{last_evaluation_output}

[EXTRA CONTEXT]
{plugin_context}         ← empty string if no plugins active

[TASK]
Propose a targeted improvement using SEARCH/REPLACE diffs only:

<<<SEARCH
<exact lines to replace>
===
<replacement lines>
>>>REPLACE
```

### 5.4 Diff Engine (`core/diff.py`)

```python
DIFF_PATTERN = re.compile(r"<<<SEARCH\n(.*?)\n===\n(.*?)\n>>>REPLACE", re.DOTALL)

def apply_diff(code: str, diff_text: str) -> tuple[str, str | None]:
    """Returns (new_code, diff_error). diff_error is None on success."""
    blocks = DIFF_PATTERN.findall(diff_text)
    if not blocks:
        return code, "no_diff_blocks"
    result = code
    for search, replace in blocks:
        if search not in result:
            return code, "search_not_found"
        result = result.replace(search, replace, 1)
    if result == code:
        return code, "no_valid_changes"
    return result, None
```

---

## 6. Problem Specification

### 6.1 Directory Layout

```
problems/<name>/
├── task_description.txt   # natural language task for LLM context
├── metrics.yaml           # metric definitions
├── validate.py            # def evaluate(code: str) -> dict
├── config.yaml            # (optional) overrides global Config defaults
└── initial_programs/      # seed programs (at least one required)
    └── seed.py
```

`config.yaml` is optional. If present, its values override global `Config` defaults and are themselves overridden by CLI flags. Priority: CLI flags > `config.yaml` > `Config` defaults.

### 6.2 `metrics.yaml`

```yaml
metrics:
  - name: total_radius
    direction: maximize      # or "minimize"
    primary: true            # exactly one metric must be primary
    bounds: [0.0, 10.0]      # used for MAP-Elites normalization
  - name: is_valid
    direction: maximize
    primary: false
```

### 6.3 `validate.py` contract

User implements exactly one function:

```python
def evaluate(code: str) -> dict:
    """
    Execute the candidate program and return a metrics dict.
    Must include: the primary metric key and 'is_valid' (bool).
    """
    ...
```

**Framework responsibilities** (user does not implement these):
- Timeout enforcement (subprocess kill after `eval_timeout_sec`)
- Syntax checking (Tier 1)
- Penalty score assignment
- Metric normalization for MAP-Elites
- Exception catching around the call to `evaluate()`

`validate.py` is **never called** when a Tier 0 or Tier 1 penalty applies (see Section 7).

---

## 7. Cascade Evaluator (`core/evaluator.py`)

```
Tier 0 (free)     — diff_error is not None → return penalty immediately
                    diff_error=None         → proceed to Tier 1
                    (seed programs use diff_error=None, bypassing Tier 0)

Tier 1 (cheap)    — compile(code, "<string>", "exec") syntax check
                    SyntaxError             → return -0.2

Tier 2 (full)     — run validate.py in subprocess with timeout
                    timeout / crash         → return -0.2
                    result["is_valid"]=False → return -0.1
                    success                 → return result[primary_metric]
```

`validate.py` is invoked only if both Tier 0 and Tier 1 pass without penalty.
`eval_timeout_sec` governs Tier 2 only and is independent of the syntax check.

---

## 8. Plugin System

### 8.1 `PluginBase` ABC (`plugins/base.py`)

`Plugin` uses `ABC` (not `Protocol`) so that concrete no-op default method bodies can be provided. Plugins inherit from `PluginBase` and override only what they need.

```python
from abc import ABC

class PluginBase(ABC):
    def on_generation_start(self, gen: int, db: "ProgramDatabase") -> None:
        pass

    def on_evaluated(self, program: "Program", score: float) -> float:
        return score   # default: pass score through unchanged

    def on_generation_end(self, gen: int, best: "Program") -> None:
        pass

    def build_extra_context(self, parent: "Program",
                            inspirations: list["Program"]) -> str:
        return ""      # default: contribute nothing to prompt
```

`on_evaluated` receives a fully constructed `Program` object (with `id`, `code`, `lineage`, `metadata` populated) and may return a modified score. The loop updates `program.fitness` with the returned value before archiving.

### 8.2 Bundled Plugins

| Plugin | Source Paper | Hook(s) used | What it adds |
|--------|-------------|--------------|--------------|
| `causal` | CausalEvolve (2603.14575) | `build_extra_context`, `on_evaluated` | Scratchpad memory + MAB outcome-factor guidance; 100×–1000× sample efficiency on some tasks |
| `deep_research` | DeepEvolve (2510.06056) | `on_generation_start` | Web search (arXiv/PubMed) + hypothesis synthesis before each generation; escapes domain plateaus |
| `modular` | ImprovEvolve (2602.10233) | `build_extra_context` | Shapes prompt to evolve `generate_config / improve / perturb` class; enables cross-instance transfer |
| `ttt_rl` | ThetaEvolve (2511.23473) | `on_generation_end` | GRPO test-time RL training on accumulated history; small open models match frontier ensembles at scale |

---

## 9. Configuration (`core/config.py`)

```python
@dataclass
class Config:
    # Evolution
    max_generations:        int   = 1000
    num_inspirations:       int   = 3
    eval_timeout_sec:       float = 60.0

    # Population
    n_islands:              int   = 5
    migration_interval:     int   = 25
    migration_ratio:        float = 0.10
    map_elites_bins:        int   = 10
    elite_archive_size:     int   = 50

    # LLM
    backends:               list[dict] = field(default_factory=lambda: [
                                {"type": "anthropic", "model": "claude-sonnet-4-6"}
                            ])
    ensemble_explore_coeff: float = 1.0

    # Plugins (opt-in by name)
    plugins:                list[str] = field(default_factory=list)

    # Logging
    log_dir:                str   = "runs/"
    seed:                   int   = 42
```

Priority: **CLI flags > `config.yaml` in problem dir > `Config` dataclass defaults**.

`build_llm(config) -> LLMEnsemble` (in `llm/ensemble.py`) reads `config.backends`,
instantiates one `LLMBackend` per entry, and wraps them in a single `LLMEnsemble`.

---

## 10. CLI (`cli.py`)

```bash
# Minimal run
python -m alphaevolve run problems/circle_packing

# Override generations, add plugins, multi-backend ensemble
python -m alphaevolve run problems/circle_packing \
    --max-generations 500 \
    --plugins causal deep_research \
    --backends anthropic:claude-sonnet-4-6 ollama:llama3

# Inspect a previous run
python -m alphaevolve show runs/circle_packing_20260317/
```

---

## 11. Data Flow

```
problem dir
    │
    ▼
ProblemLoader ──► Problem (task_description, metrics, evaluate fn, seeds)
    │
    ▼
evolve(problem, config, plugins)
    │
    ├── for each seed:
    │       CascadeEvaluator.evaluate(code, diff_error=None)   # Tier 0 skipped
    │       ProgramDatabase.log(program)
    │       ProgramDatabase.add(program)                       # score ≥ 0 guaranteed for seeds
    │
    └── for each generation:
            ProgramDatabase.sample()          → parent
            ProgramDatabase.sample_diverse()  → inspirations
            Plugin.build_extra_context()      → extra_context
            build_prompt()                    → prompt
            LLMEnsemble.generate()            → (diff, backend_idx)
            apply_diff()                      → (child_code, diff_error)
            CascadeEvaluator.evaluate()       → score
            Program(...)                      → program object constructed here
            Plugin.on_evaluated(program, score) → score (possibly modified)
            program.fitness = score
            ProgramDatabase.log(program)      → always written to history.jsonl
            if score ≥ 0: ProgramDatabase.add(program)
            LLMEnsemble.record_reward(idx, max(0.0, score - parent.fitness))
            ProgramDatabase.maybe_migrate(gen)
            Plugin.on_generation_end()
```

---

## 12. Error Handling

| Failure | Behaviour |
|---------|-----------|
| Invalid diff (no blocks / no change) | Lazy penalty score; logged but not archived |
| `search_not_found` in diff | Treated as `no_valid_changes`; −0.3 penalty |
| Python syntax error | Tier 1 penalty −0.2; logged with diff |
| Execution timeout | Subprocess killed; −0.2 returned |
| Domain-invalid result | −0.1 returned; full result logged |
| LLM API failure | Exponential backoff, 3 retries; generation skipped on final failure |
| Empty elite archive | Cannot occur if at least one valid seed exists; CLI validates this at startup |

---

## 13. Testing Strategy

- `tests/core/` — unit tests for diff engine (all error cases), MAP-Elites cell assignment, cascade evaluator (all tiers)
- `tests/llm/` — mock `LLMBackend`; assert prompt structure, UCB1 arm selection, reward clamping
- `tests/integration/` — run `hello_world` example for 10 generations; assert fitness strictly improves at least once
- `tests/plugins/` — each plugin tested in isolation with a mock `ProgramDatabase`
- `validate.py` execution in integration tests uses real subprocess (no mocking)

---

## 14. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SEARCH/REPLACE diff format | Universal consensus across all 8 core system papers; prevents wholesale rewrites; surgically precise |
| Synchronous core loop | Research friendliness; async is a performance optimisation, not a correctness requirement |
| Separate `LLMBackend` (str) and `LLMEnsemble` (tuple) interfaces | Backends stay simple; routing logic is isolated to the ensemble layer |
| `PluginBase` as ABC (not Protocol) | ABCs support concrete default method bodies; Protocol cannot |
| `Program` constructed before `on_evaluated` | Plugins (especially CausalEvolve) need full object with id/lineage/metadata |
| Score < 0 → logged but not archived | Keeps archive clean; full history still available for RL replay and debugging |
| UCB1 reward clamped to `max(0, delta)` | UCB1 assumes bounded non-negative rewards; negative rewards violate mathematical guarantees |
| `maybe_migrate(gen)` in loop | Island migration is part of the core loop, not an optional plugin |
| Directory-based problem spec with optional `config.yaml` | Clean convention from GigaEvo + ArchAgent; no framework lock-in |
| MAP-Elites + ring-topology islands | Outperforms both single-population and fully-connected topologies per CodeEvolve ablations |
| TF-IDF char-4gram for diversity | Lightweight, no model dependency, captures code structure without execution |
| Lazy penalty system | Dual purpose: RL training stability (ThetaEvolve) + immediate debugging signal (CodeEvolve) |
| `history.jsonl` append-only log | Zero-dependency persistence; supports RL replay (ThetaEvolve) and lineage analysis (GigaEvo) |

---

## 15. References

All 23 papers read during design:

### Foundational algorithms

- **MAP-Elites**: Mouret & Clune, "Illuminating search spaces by mapping elites," 2015.
- **UCB1**: Auer, Cesa-Bianchi & Fischer, "Finite-time Analysis of the Multiarmed Bandit Problem," *Machine Learning* 47(2-3), 2002.

### Core system papers

| arXiv ID | Authors | Full title | Role in this design |
|----------|---------|------------|---------------------|
| [2506.13131](https://arxiv.org/abs/2506.13131) | Novikov et al. (Google DeepMind) | AlphaEvolve: A coding agent for scientific and algorithmic discovery | Core loop, diff format, MAP-Elites + islands, LLM ensemble, cascade eval |
| [2511.17592](https://arxiv.org/abs/2511.17592) | Khrulkov et al. | GigaEvo: An Open Source Optimization Framework Powered By LLMs And Evolution Algorithms | Redis/JSONL persistence, bidirectional lineage, rewrite vs diff, Hydra config, problem dir convention |
| [2510.14150](https://arxiv.org/abs/2510.14150) | Assumpção et al. | CodeEvolve: An open source evolutionary coding agent for algorithmic discovery and optimization | Island ring topology ablations, depth exploitation, meta-prompting, plateau scheduler |
| [2511.23473](https://arxiv.org/abs/2511.23473) | Wang et al. | ThetaEvolve: Test-time Learning on Open Problems | Lazy penalty system, large database sizing, batch sampling, test-time RL |
| [2602.10233](https://arxiv.org/abs/2602.10233) | Kravatskiy, Khrulkov & Oseledets | ImprovEvolve: Ask AlphaEvolve to Improve the Input Solution and Then Improvise | Modular decomposition plugin, basin-hopping, two-tier LLM strategy |
| [2602.15951](https://arxiv.org/abs/2602.15951) | Li, Zang & Münchmeyer | MadEvolve: Evolutionary Optimization of Cosmological Algorithms with Large Language Models | UCB1 bandit LLM selection, 3D MAP-Elites dimensions, autodiff parameter opt |
| [2603.14575](https://arxiv.org/abs/2603.14575) | Chen et al. | CausalEvolve: Towards Open-Ended Discovery with Causal Scratchpad | Causal scratchpad plugin, MAB outcome-factor guidance, abductive reasoning |
| [2510.06056](https://arxiv.org/abs/2510.06056) | Liu et al. | Scientific Algorithm Discovery by Augmenting AlphaEvolve with Deep Research | Deep research plugin, automatic debugging, MAP-Elites 3D behavioral archive |

### Application & evaluation papers

| arXiv ID | Authors | Full title | Role in this design |
|----------|---------|------------|---------------------|
| [2601.21096](https://arxiv.org/abs/2601.21096) | Chen et al. (Google DeepMind) | Magellan: Autonomous Discovery of Novel Compiler Optimization Heuristics with AlphaEvolve | EVOLVE-BLOCK comments, continuation strategy, cascaded eval timing |
| [2602.22425](https://arxiv.org/abs/2602.22425) | Gupta et al. | ArchAgent: Agentic AI-driven Computer Architecture Discovery | Rich prompt engineering, cascaded eval (fast/authoritative), constraint enforcement |
| [2602.16928](https://arxiv.org/abs/2602.16928) | Li, Schultz, Hennes & Lanctot | Discovering Multiagent Learning Algorithms with Large Language Models | Constrained search spaces, multi-game fitness, semantic mutation |
| [2603.09172](https://arxiv.org/abs/2603.09172) | Nagda, Raghavan & Thakurta | Reinforced Generation of Combinatorial Structures: Ramsey Numbers | Two-graph execution pattern, prospect bonus, meta-level algorithm discovery |
| [2509.18057](https://arxiv.org/abs/2509.18057) | (Google DeepMind) | Reinforced Generation of Combinatorial Structures: Hardness of Approximation | Code-level evolution of verifiers, smooth scoring landscapes, GA for prompt selection |
| [2603.06692](https://arxiv.org/abs/2603.06692) | Bérczi | Evolving Local Corrections for Global Constructions in Combinatorics | Harness design principles, symmetry-robust aggregation, AI summaries |
| [2601.16175](https://arxiv.org/abs/2601.16175) | Yuksekgonul et al. | Learning to Discover at Test Time | PUCT state reuse, entropic RL objective, dynamic environments |
| [2603.08679](https://arxiv.org/abs/2603.08679) | Cai, Gupta, Li & Mehta | A New Lower Bound for the Random Offerer Mechanism in Bilateral Trade using AI-Guided Evolutionary Search | Program synthesis over numerical opt, precision arithmetic |
| [2601.01235](https://arxiv.org/abs/2601.01235) | Ellenberg, Libedinsky, Plaza, Simental & Williamson | Bruhat intervals that are large hypercubes | Prompt engineering with mathematical hints, generalizer mode |
| [2511.02864](https://arxiv.org/abs/2511.02864) | Georgiev, Gómez-Serrano, Tao & Wagner | Mathematical exploration and discovery at scale | Broad landscape of AI-assisted mathematical discovery; framing and motivation |
| [2511.12916](https://arxiv.org/abs/2511.12916) | Wang et al. | Fault2Flow: An AlphaEvolve-Optimized Human-in-the-Loop Multi-Agent System for Fault-to-Workflow Automation | Multi-island elite exchange, structured output evolution |
| [2601.05943](https://arxiv.org/abs/2601.05943) | Berthold, Kamp, Mexi, Pokutta & Pólik | Global Optimization for Combinatorial Geometry Problems Revisited in the Era of LLMs | Complementary solver approach; informed harness design section |
| [2506.16750](https://arxiv.org/abs/2506.16750) | Boyer & Li | An improved example for an autoconvolution inequality | AlphaEvolve used as benchmark; gradient-based complement |
| [2505.16105](https://arxiv.org/abs/2505.16105) | Gerbicz | Sums and differences of sets (improvement over AlphaEvolve) | Two-stage eval (float screen + exact verify), parametric construction |
| [2506.01896](https://arxiv.org/abs/2506.01896) | Zheng | Sums and differences of sets: a further improvement over AlphaEvolve | Large-deviation asymptotic analysis; injectivity constraint design |
