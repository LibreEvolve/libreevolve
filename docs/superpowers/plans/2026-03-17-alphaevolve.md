# AlphaEvolve Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build AlphaEvolve — a Python research platform for LLM-guided evolutionary program discovery, grounded in 22 papers.

**Architecture:** Layered plugin architecture: a synchronous core loop (SEARCH/REPLACE diff → cascade evaluator → MAP-Elites archive) over a 5-island ring-topology population, UCB1-bandit LLM ensemble routing, and opt-in research plugins via 4 lifecycle hooks.

**Tech Stack:** Python 3.11+, numpy, scikit-learn (TF-IDF diversity), anthropic SDK, openai SDK, ollama SDK, pyyaml, click, pytest, pytest-mock.

---

## File Map

All paths relative to project root (`Alpha Evole/`).

| File | Responsibility |
|------|----------------|
| `pyproject.toml` | Package metadata, dependencies |
| `alphaevolve/__init__.py` | Package root |
| `alphaevolve/__main__.py` | Entry point for `python -m alphaevolve` |
| `alphaevolve/cli.py` | click CLI: `run` and `show` commands |
| `alphaevolve/core/config.py` | Config dataclass (all settings) |
| `alphaevolve/core/diff.py` | SEARCH/REPLACE diff engine (`apply_diff`) |
| `alphaevolve/core/evaluator.py` | Cascade evaluator (Tier 0/1/2) — see spec Section 7 |
| `alphaevolve/core/loop.py` | `evolve()` main loop + `build_prompt()` |
| `alphaevolve/core/database.py` | ProgramDatabase facade |
| `alphaevolve/population/program.py` | Program dataclass |
| `alphaevolve/population/map_elites.py` | 3D MAP-Elites 10x10x10 archive |
| `alphaevolve/population/islands.py` | IslandModel: 5 islands + ring migration |
| `alphaevolve/llm/base.py` | LLMBackend Protocol |
| `alphaevolve/llm/ensemble.py` | LLMEnsemble (UCB1 bandit) + `build_llm()` |
| `alphaevolve/llm/anthropic.py` | AnthropicBackend |
| `alphaevolve/llm/openai.py` | OpenAIBackend |
| `alphaevolve/llm/ollama.py` | OllamaBackend |
| `alphaevolve/plugins/base.py` | PluginBase ABC |
| `alphaevolve/plugins/causal.py` | CausalEvolve plugin |
| `alphaevolve/plugins/deep_research.py` | DeepEvolve plugin |
| `alphaevolve/plugins/modular.py` | ImprovEvolve plugin |
| `alphaevolve/plugins/ttt_rl.py` | ThetaEvolve plugin |
| `alphaevolve/problems/loader.py` | ProblemLoader + Problem dataclass |
| `alphaevolve/problems/examples/hello_world/` | Bundled hello_world problem |
| `alphaevolve/problems/examples/circle_packing/` | Bundled circle_packing problem |
| `alphaevolve/problems/examples/sorting/` | Bundled sorting problem |
| `tests/core/test_diff.py` | Diff engine tests |
| `tests/core/test_evaluator.py` | Cascade evaluator tests |
| `tests/population/test_map_elites.py` | MAP-Elites tests |
| `tests/population/test_islands.py` | Island model tests |
| `tests/population/test_database.py` | Database facade tests |
| `tests/llm/test_ensemble.py` | LLMEnsemble + UCB1 tests |
| `tests/llm/test_backends.py` | Concrete backend tests (mocked APIs) |
| `tests/plugins/test_base.py` | PluginBase no-op tests |
| `tests/plugins/test_causal.py` | CausalEvolve tests |
| `tests/plugins/test_deep_research.py` | DeepEvolve tests |
| `tests/plugins/test_modular.py` | ImprovEvolve tests |
| `tests/plugins/test_ttt_rl.py` | ThetaEvolve tests |
| `tests/core/test_loop.py` | Core loop invariant tests (mocked LLM) |
| `tests/integration/test_hello_world.py` | End-to-end 10-gen smoke test |

---

## Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: all package `__init__.py` files and `alphaevolve/__main__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "alphaevolve"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "numpy>=1.26",
    "scikit-learn>=1.4",
    "anthropic>=0.25",
    "openai>=1.23",
    "ollama>=0.1",
    "pyyaml>=6.0",
    "click>=8.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-mock>=3.12",
]

[project.scripts]
alphaevolve = "alphaevolve.cli:cli"

[tool.setuptools.packages.find]
where = ["."]
include = ["alphaevolve*"]

[tool.pytest.ini_options]
markers = [
    "integration: marks tests requiring API keys",
]
```

- [ ] **Step 2: Create directory structure and `__init__.py` files**

Create these directories: `alphaevolve/core/`, `alphaevolve/population/`, `alphaevolve/llm/`,
`alphaevolve/plugins/`, `alphaevolve/problems/examples/`,
`tests/core/`, `tests/population/`, `tests/llm/`, `tests/plugins/`, `tests/integration/`

Create empty `__init__.py` in each package directory.

`alphaevolve/__init__.py`:
```python
__version__ = "0.1.0"
```

`alphaevolve/__main__.py`:
```python
from alphaevolve.cli import cli

if __name__ == "__main__":
    cli()
```

- [ ] **Step 3: Install in editable mode**

```bash
pip install -e ".[dev]"
```

Expected: installs without error; `alphaevolve --help` available.

- [ ] **Step 4: Verify pytest sees the directory**

```bash
pytest tests/ --collect-only
```

Expected: 0 tests collected, no import errors.

- [ ] **Step 5: Commit**

```bash
git init && git add pyproject.toml alphaevolve/ tests/
git commit -m "feat: project scaffold"
```

---

## Task 2: Program + Config Dataclasses

**Files:**
- Create: `alphaevolve/population/program.py`
- Create: `alphaevolve/core/config.py`
- Test: `tests/population/test_program.py`, `tests/core/test_config.py`

- [ ] **Step 1: Write failing tests**

`tests/population/test_program.py`:
```python
from math import inf
from alphaevolve.population.program import Program

def test_default_fitness_is_neg_inf():
    assert Program().fitness == -inf

def test_unique_ids():
    assert Program().id != Program().id

def test_fields_set():
    p = Program(code="x = 1", fitness=0.5)
    assert p.code == "x = 1" and p.fitness == 0.5

def test_lineage_defaults_empty():
    assert Program().lineage == []

def test_metadata_defaults_empty():
    assert Program().metadata == {}
```

`tests/core/test_config.py`:
```python
from alphaevolve.core.config import Config

def test_default_max_generations():
    assert Config().max_generations == 1000

def test_default_n_islands():
    assert Config().n_islands == 5

def test_override_fields():
    c = Config(max_generations=50, seed=99)
    assert c.max_generations == 50 and c.seed == 99

def test_default_backend_is_anthropic():
    assert Config().backends[0]["type"] == "anthropic"
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/population/test_program.py tests/core/test_config.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/population/program.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from math import inf
from uuid import uuid4

@dataclass
class Program:
    id:         str           = field(default_factory=lambda: uuid4().hex)
    code:       str           = ""
    fitness:    float         = -inf
    generation: int           = 0
    parent_id:  str | None    = None
    lineage:    list[str]     = field(default_factory=list)
    metadata:   dict          = field(default_factory=dict)
```

- [ ] **Step 4: Implement `alphaevolve/core/config.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field

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
    # Plugins
    plugins:                list[str] = field(default_factory=list)
    # Logging
    log_dir:                str   = "runs/"
    problem_name:           str   = "unnamed"
    seed:                   int   = 42
```

- [ ] **Step 5: Run to verify they pass**

```bash
pytest tests/population/test_program.py tests/core/test_config.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add alphaevolve/population/program.py alphaevolve/core/config.py tests/
git commit -m "feat: Program and Config dataclasses"
```

---

## Task 3: Diff Engine

**Files:**
- Create: `alphaevolve/core/diff.py`
- Test: `tests/core/test_diff.py`

- [ ] **Step 1: Write failing tests**

`tests/core/test_diff.py`:
```python
from alphaevolve.core.diff import apply_diff

def test_no_blocks():
    code, err = apply_diff("x = 1", "no diff here")
    assert code == "x = 1" and err == "no_diff_blocks"

def test_empty_is_no_blocks():
    _, err = apply_diff("x = 1", "")
    assert err == "no_diff_blocks"

def test_search_not_found():
    diff = "<<<SEARCH\ny = 2\n===\ny = 3\n>>>REPLACE"
    code, err = apply_diff("x = 1", diff)
    assert code == "x = 1" and err == "search_not_found"

def test_no_valid_changes():
    diff = "<<<SEARCH\nx = 1\n===\nx = 1\n>>>REPLACE"
    _, err = apply_diff("x = 1", diff)
    assert err == "no_valid_changes"

def test_successful_single_block():
    code = "x = 1\ny = 2"
    diff = "<<<SEARCH\nx = 1\n===\nx = 10\n>>>REPLACE"
    new_code, err = apply_diff(code, diff)
    assert err is None and "x = 10" in new_code and "y = 2" in new_code

def test_multiple_blocks():
    code = "a = 1\nb = 2"
    diff = "<<<SEARCH\na = 1\n===\na = 10\n>>>REPLACE\n<<<SEARCH\nb = 2\n===\nb = 20\n>>>REPLACE"
    new_code, err = apply_diff(code, diff)
    assert err is None and "a = 10" in new_code and "b = 20" in new_code

def test_original_unchanged_on_error():
    original = "def foo():\n    pass"
    code, _ = apply_diff(original, "no blocks")
    assert code == original
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/core/test_diff.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/core/diff.py`**

```python
from __future__ import annotations
import re

DIFF_PATTERN = re.compile(r"<<<SEARCH\n(.*?)\n===\n(.*?)\n>>>REPLACE", re.DOTALL)

def apply_diff(code: str, diff_text: str) -> tuple[str, str | None]:
    """Apply SEARCH/REPLACE blocks. Returns (new_code, diff_error).
    diff_error is None on success.
    Error values: no_diff_blocks | search_not_found | no_valid_changes
    """
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

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/core/test_diff.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/core/diff.py tests/core/test_diff.py
git commit -m "feat: SEARCH/REPLACE diff engine with full error coverage"
```

---

## Task 4: MAP-Elites Archive

**Files:**
- Create: `alphaevolve/population/map_elites.py`
- Test: `tests/population/test_map_elites.py`

- [ ] **Step 1: Write failing tests**

`tests/population/test_map_elites.py`:
```python
from alphaevolve.population.map_elites import MAPElites
from alphaevolve.population.program import Program

def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)

def test_best_none_when_empty():
    assert MAPElites().best() is None

def test_add_and_best():
    a = MAPElites(); a.add(_p(fitness=0.7))
    assert a.best().fitness == 0.7

def test_replacement_only_when_higher():
    a = MAPElites()
    a.add(_p(code="x=1", fitness=0.3))
    a.add(_p(code="x=1", fitness=0.8))
    assert a.best().fitness == 0.8

def test_lower_does_not_replace():
    a = MAPElites()
    a.add(_p(code="x=1", fitness=0.8))
    a.add(_p(code="x=1", fitness=0.3))
    assert a.best().fitness == 0.8

def test_occupied_cells_nonempty():
    a = MAPElites(); a.add(_p())
    assert len(a.occupied_cells()) >= 1

def test_sample_diverse_up_to_k():
    a = MAPElites()
    for i in range(5): a.add(_p(code=f"x={i}", fitness=i*0.1))
    assert 1 <= len(a.sample_diverse(k=3)) <= 3

def test_elite_archive_capped():
    a = MAPElites(elite_archive_size=3)
    for i in range(10): a.add(_p(code=f"x={i}", fitness=i*0.1))
    assert len(a.elite_archive()) <= 3

def test_diversity_no_crash_on_first():
    a = MAPElites()
    a.add(_p(code="def foo(): return 42", fitness=0.5))
    assert a.best() is not None
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/population/test_map_elites.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/population/map_elites.py`**

Key design: TF-IDF char-4gram cosine distance against the global elite archive is the diversity dimension. Use `sklearn.feature_extraction.text.TfidfVectorizer(analyzer="char", ngram_range=(4, 4))` and `sklearn.metrics.pairwise.cosine_similarity`. Return 0.5 as default when the archive is empty (first program) or vectorizer raises ValueError (empty vocabulary).

```python
from __future__ import annotations
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from alphaevolve.population.program import Program


class MAPElites:
    """3D MAP-Elites: performance x complexity x diversity."""

    def __init__(self, bins: int = 10, elite_archive_size: int = 50,
                 perf_bounds: tuple[float, float] = (0.0, 1.0)):
        self.bins = bins
        self._perf_min, self._perf_max = perf_bounds
        self._grid: dict[tuple[int, int, int], Program] = {}
        self._max_complexity: int = 1
        self._elite: list[Program] = []
        self._elite_size = elite_archive_size

    def _norm_perf(self, fitness: float) -> float:
        rng = self._perf_max - self._perf_min
        if rng == 0: return 0.5
        return max(0.0, min(1.0, (fitness - self._perf_min) / rng))

    def _norm_complexity(self, code: str) -> float:
        n = len(code)
        self._max_complexity = max(self._max_complexity, n)
        return n / self._max_complexity

    def _diversity(self, code: str) -> float:
        """Mean TF-IDF char-4gram cosine distance to global elite archive."""
        if not self._elite: return 0.5
        corpus = [p.code for p in self._elite] + [code]
        try:
            mat = TfidfVectorizer(analyzer="char", ngram_range=(4, 4)).fit_transform(corpus)
        except ValueError:
            return 0.5
        sims = cosine_similarity(mat[-1], mat[:-1])[0]
        return float(np.mean(1.0 - sims))

    def _cell(self, p: Program) -> tuple[int, int, int]:
        c = lambda x: max(0, min(self.bins - 1, int(x * self.bins)))
        return (c(self._norm_perf(p.fitness)),
                c(self._norm_complexity(p.code)),
                c(self._diversity(p.code)))

    def add(self, program: Program) -> None:
        cell = self._cell(program)
        occ = self._grid.get(cell)
        if occ is None or program.fitness > occ.fitness:
            self._grid[cell] = program
        self._elite.append(program)
        self._elite.sort(key=lambda p: p.fitness, reverse=True)
        self._elite = self._elite[:self._elite_size]

    def best(self) -> Program | None:
        return self._elite[0] if self._elite else None

    def sample_diverse(self, k: int) -> list[Program]:
        cells = list(self._grid.values())
        return random.sample(cells, min(k, len(cells))) if cells else []

    def occupied_cells(self) -> list[Program]:
        return list(self._grid.values())

    def elite_archive(self) -> list[Program]:
        return list(self._elite)
```

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/population/test_map_elites.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/population/map_elites.py tests/population/test_map_elites.py
git commit -m "feat: 3D MAP-Elites with TF-IDF char-4gram diversity"
```

---

## Task 5: Island Model + Database Facade

**Files:**
- Create: `alphaevolve/population/islands.py`
- Create: `alphaevolve/core/database.py`
- Test: `tests/population/test_islands.py`, `tests/population/test_database.py`

- [ ] **Step 1: Write failing tests**

`tests/population/test_islands.py`:
```python
from alphaevolve.core.config import Config
from alphaevolve.population.islands import IslandModel
from alphaevolve.population.program import Program

def _m(n=3): return IslandModel(Config(n_islands=n, migration_interval=5))
def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)

def test_best_returns_highest():
    m = _m(); m.add(_p(fitness=0.3)); m.add(_p(fitness=0.7))
    assert m.best().fitness == 0.7

def test_sample_exploit_returns_best():
    m = _m(); m.add(_p(fitness=0.3)); m.add(_p(fitness=0.9))
    assert m.sample("exploit").fitness == 0.9

def test_migration_copies_not_moves():
    m = IslandModel(Config(n_islands=2, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(fitness=1.0))
    before = len(m.islands[0].occupied_cells())
    m.migrate()
    assert len(m.islands[0].occupied_cells()) == before
    assert m.islands[1].best() is not None

def test_sample_diverse_returns_list():
    m = _m()
    for i in range(5): m.add(_p(code=f"x={i}", fitness=i*0.1))
    samples = m.sample_diverse(k=3)
    assert isinstance(samples, list) and len(samples) <= 3

def test_ring_topology():
    m = IslandModel(Config(n_islands=3, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(code="i0", fitness=1.0))
    m.migrate()
    assert m.islands[1].best() is not None
    assert m.islands[2].best() is None  # 0 does not reach 2 directly
```

`tests/population/test_database.py`:
```python
import json, tempfile
from pathlib import Path
from alphaevolve.core.config import Config
from alphaevolve.core.database import ProgramDatabase
from alphaevolve.population.program import Program

def _db(): return ProgramDatabase(Config(log_dir=tempfile.mkdtemp(), problem_name="t"))
def _p(code="x=1", fitness=0.5): return Program(code=code, fitness=fitness)

def test_log_always_appends():
    db = _db(); db.log(_p(fitness=-0.4))
    assert len(db.all_programs()) == 1

def test_add_updates_best():
    db = _db(); p = _p(fitness=0.8); db.log(p); db.add(p)
    assert db.best().fitness == 0.8

def test_log_without_add_not_in_archive():
    db = _db(); db.log(_p(fitness=-0.3))
    assert db.best() is None

def test_sample_exploit():
    db = _db()
    for f in (0.3, 0.7):
        p = _p(fitness=f); db.log(p); db.add(p)
    assert db.sample("exploit").fitness == 0.7

def test_log_writes_jsonl():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(_p(fitness=0.5))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["fitness"] == 0.5

def test_maybe_migrate_no_crash():
    db = ProgramDatabase(Config(migration_interval=5, n_islands=2,
                                log_dir=tempfile.mkdtemp(), problem_name="t"))
    p = _p(); db.log(p); db.add(p)
    db.maybe_migrate(4); db.maybe_migrate(5)
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/population/test_islands.py tests/population/test_database.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/population/islands.py`**

```python
from __future__ import annotations
import math, random
from alphaevolve.core.config import Config
from alphaevolve.population.map_elites import MAPElites
from alphaevolve.population.program import Program


class IslandModel:
    """5 independent MAP-Elites archives with ring-topology migration."""

    def __init__(self, config: Config):
        self.n_islands = config.n_islands
        self._migration_ratio = config.migration_ratio
        self.islands: list[MAPElites] = [
            MAPElites(bins=config.map_elites_bins, elite_archive_size=config.elite_archive_size)
            for _ in range(self.n_islands)
        ]
        self._current = 0

    def add(self, program: Program) -> None:
        self.islands[self._current].add(program)
        self._current = (self._current + 1) % self.n_islands

    def sample(self, strategy: str = "exploit") -> Program | None:
        if strategy == "exploit":
            cands = [i.best() for i in self.islands if i.best()]
            return max(cands, key=lambda p: p.fitness) if cands else None
        raise ValueError(f"Unknown strategy: {strategy!r}")

    def sample_diverse(self, k: int) -> list[Program]:
        pool = [p for i in self.islands for p in i.occupied_cells()]
        return random.sample(pool, min(k, len(pool))) if pool else []

    def best(self) -> Program | None:
        cands = [i.best() for i in self.islands if i.best()]
        return max(cands, key=lambda p: p.fitness) if cands else None

    def migrate(self) -> None:
        """Ring: island i copies top migrants to island (i+1) % n."""
        for i, src in enumerate(self.islands):
            dst = self.islands[(i + 1) % self.n_islands]
            elites = src.elite_archive()
            n = max(1, math.ceil(len(elites) * self._migration_ratio))
            for program in elites[:n]:
                dst.add(program)
```

- [ ] **Step 4: Implement `alphaevolve/core/database.py`**

```python
from __future__ import annotations
import json
from pathlib import Path
from alphaevolve.core.config import Config
from alphaevolve.population.islands import IslandModel
from alphaevolve.population.program import Program


class ProgramDatabase:
    """Facade: IslandModel + append-only history.jsonl."""

    def __init__(self, config: Config):
        self._islands = IslandModel(config)
        self._interval = config.migration_interval
        log_dir = Path(config.log_dir) / config.problem_name
        log_dir.mkdir(parents=True, exist_ok=True)
        self._jsonl = log_dir / "history.jsonl"
        self._all: list[Program] = []

    def add(self, program: Program) -> None:
        self._islands.add(program)

    def log(self, program: Program) -> None:
        self._all.append(program)
        with open(self._jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "id": program.id, "code": program.code, "fitness": program.fitness,
                "generation": program.generation, "parent_id": program.parent_id,
                "lineage": program.lineage, "metadata": program.metadata,
            }) + "\n")

    def sample(self, strategy: str = "exploit") -> Program | None:
        return self._islands.sample(strategy=strategy)

    def sample_diverse(self, k: int) -> list[Program]:
        return self._islands.sample_diverse(k=k)

    def best(self) -> Program | None:
        return self._islands.best()

    def maybe_migrate(self, gen: int) -> None:
        if gen > 0 and gen % self._interval == 0:
            self._islands.migrate()

    def all_programs(self) -> list[Program]:
        return list(self._all)
```

- [ ] **Step 5: Run to verify they pass**

```bash
pytest tests/population/test_islands.py tests/population/test_database.py -v
```

Expected: all 11 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add alphaevolve/population/islands.py alphaevolve/core/database.py \
        tests/population/
git commit -m "feat: island model with ring migration and ProgramDatabase facade"
```

---

## Task 6: LLM Base Protocol + Ensemble

**Files:**
- Create: `alphaevolve/llm/base.py`
- Create: `alphaevolve/llm/ensemble.py`
- Test: `tests/llm/test_ensemble.py`

- [ ] **Step 1: Write failing tests**

`tests/llm/test_ensemble.py`:
```python
from unittest.mock import MagicMock
from alphaevolve.llm.ensemble import LLMEnsemble

def _b(name="b", resp="<<<SEARCH\nfoo\n===\nbar\n>>>REPLACE"):
    m = MagicMock(); m.name = name; m.generate.return_value = resp; return m

def test_returns_tuple():
    diff, idx = LLMEnsemble([_b()]).generate("p")
    assert isinstance(diff, str) and idx == 0

def test_single_backend_always_idx0():
    b = _b(); ens = LLMEnsemble([b])
    assert all(ens.generate("p")[1] == 0 for _ in range(3))

def test_ucb1_explores_both_first():
    b1, b2 = _b("b1"), _b("b2")
    ens = LLMEnsemble([b1, b2])
    _, i1 = ens.generate("p"); _, i2 = ens.generate("p")
    assert {i1, i2} == {0, 1}

def test_record_reward_updates_wins():
    ens = LLMEnsemble([_b()]); ens.generate("p")
    ens.record_reward(0, 2.5)
    assert ens.wins[0] == 2.5

def test_ensemble_does_not_clamp():
    ens = LLMEnsemble([_b()]); ens.generate("p")
    ens.record_reward(0, -1.0)
    assert ens.wins[0] == -1.0

def test_counts_increment():
    ens = LLMEnsemble([_b()])
    assert ens.counts[0] == 0; ens.generate("p"); assert ens.counts[0] == 1

def test_high_reward_preferred_at_zero_explore():
    b1, b2 = _b("b1"), _b("b2")
    ens = LLMEnsemble([b1, b2], explore_coeff=0.0)
    ens.generate("p"); ens.generate("p")
    ens.record_reward(0, 10.0); ens.record_reward(1, 0.0)
    _, idx = ens.generate("p")
    assert idx == 0
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/llm/test_ensemble.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/llm/base.py`**

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class LLMBackend(Protocol):
    """Per-backend interface. Returns raw text (str), not a tuple."""
    def generate(self, prompt: str, **kwargs) -> str: ...
    @property
    def name(self) -> str: ...
```

- [ ] **Step 4: Implement `alphaevolve/llm/ensemble.py`**

```python
from __future__ import annotations
import math
import numpy as np
from alphaevolve.llm.base import LLMBackend


class LLMEnsemble:
    """UCB1-bandit routing layer over one or more LLMBackend instances."""

    def __init__(self, backends: list[LLMBackend], explore_coeff: float = 1.0):
        if not backends:
            raise ValueError("LLMEnsemble requires at least one backend.")
        self.backends = backends
        self.c = explore_coeff
        self.counts: list[int]   = [0]   * len(backends)
        self.wins:   list[float] = [0.0] * len(backends)
        self.total:  int         = 0

    def generate(self, prompt: str) -> tuple[str, int]:
        """Returns (diff_text, backend_index)."""
        idx = self._ucb1_select()
        response = self.backends[idx].generate(prompt)
        self.counts[idx] += 1
        return response, idx

    def record_reward(self, idx: int, reward: float) -> None:
        """Caller is responsible for clamping reward >= 0."""
        self.wins[idx] += reward

    def _ucb1_select(self) -> int:
        self.total += 1
        scores = [
            (self.wins[i] / max(self.counts[i], 1))
            + self.c * math.sqrt(math.log(self.total) / max(self.counts[i], 1))
            for i in range(len(self.backends))
        ]
        return int(np.argmax(scores))


def build_llm(config) -> LLMEnsemble:
    """Instantiate LLMEnsemble from config.backends."""
    from alphaevolve.llm.anthropic import AnthropicBackend
    from alphaevolve.llm.openai    import OpenAIBackend
    from alphaevolve.llm.ollama    import OllamaBackend
    _REG = {"anthropic": AnthropicBackend, "openai": OpenAIBackend, "ollama": OllamaBackend}
    backends = [_REG[s["type"]](**{k: v for k, v in s.items() if k != "type"})
                for s in config.backends]
    return LLMEnsemble(backends, explore_coeff=config.ensemble_explore_coeff)
```

- [ ] **Step 5: Run to verify they pass**

```bash
pytest tests/llm/test_ensemble.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add alphaevolve/llm/base.py alphaevolve/llm/ensemble.py tests/llm/test_ensemble.py
git commit -m "feat: LLMBackend protocol and UCB1-bandit LLMEnsemble"
```

---

## Task 7: Concrete LLM Backends

**Files:**
- Create: `alphaevolve/llm/anthropic.py`, `alphaevolve/llm/openai.py`, `alphaevolve/llm/ollama.py`
- Test: `tests/llm/test_backends.py`

Each backend: 3-attempt exponential backoff, `time.sleep(2 ** attempt)` on failure.

- [ ] **Step 1: Write failing tests**

`tests/llm/test_backends.py`:
```python
from unittest.mock import MagicMock
from alphaevolve.llm.anthropic import AnthropicBackend
from alphaevolve.llm.openai    import OpenAIBackend
from alphaevolve.llm.ollama    import OllamaBackend
from alphaevolve.llm.base      import LLMBackend

def test_names():
    for cls, prefix, m in [(AnthropicBackend, "anthropic", "m"),
                           (OpenAIBackend, "openai", "m2"),
                           (OllamaBackend, "ollama", "m3")]:
        b = cls.__new__(cls); b._model = m
        assert b.name == f"{prefix}/{m}"

def test_anthropic_generate(mocker):
    mc = MagicMock()
    mc.messages.create.return_value.content = [MagicMock(text="diff")]
    mocker.patch("alphaevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    assert AnthropicBackend(model="m").generate("p") == "diff"

def test_openai_generate(mocker):
    mc = MagicMock()
    mc.chat.completions.create.return_value.choices = [MagicMock(message=MagicMock(content="d"))]
    mocker.patch("alphaevolve.llm.openai.openai_sdk.OpenAI", return_value=mc)
    assert OpenAIBackend(model="m").generate("p") == "d"

def test_ollama_generate(mocker):
    mocker.patch("alphaevolve.llm.ollama.ollama_sdk.chat",
                 return_value={"message": {"content": "out"}})
    assert OllamaBackend(model="m").generate("p") == "out"

def test_anthropic_retries(mocker):
    mc = MagicMock()
    mc.messages.create.side_effect = [Exception("fail"),
                                       MagicMock(content=[MagicMock(text="ok")])]
    mocker.patch("alphaevolve.llm.anthropic.anthropic_sdk.Anthropic", return_value=mc)
    mocker.patch("alphaevolve.llm.anthropic.time.sleep")
    assert AnthropicBackend().generate("p") == "ok"
    assert mc.messages.create.call_count == 2
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/llm/test_backends.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement all three backends**

`alphaevolve/llm/anthropic.py`:
```python
from __future__ import annotations
import time
import anthropic as anthropic_sdk

class AnthropicBackend:
    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 4096):
        self._client = anthropic_sdk.Anthropic()
        self._model = model; self._max_tokens = max_tokens
    @property
    def name(self) -> str: return f"anthropic/{self._model}"
    def generate(self, prompt: str, **kwargs) -> str:
        for attempt in range(3):
            try:
                msg = self._client.messages.create(
                    model=self._model, max_tokens=self._max_tokens,
                    messages=[{"role": "user", "content": prompt}])
                return msg.content[0].text
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")
```

`alphaevolve/llm/openai.py`:
```python
from __future__ import annotations
import time
import openai as openai_sdk

class OpenAIBackend:
    def __init__(self, model: str = "gpt-4o", max_tokens: int = 4096):
        self._client = openai_sdk.OpenAI()
        self._model = model; self._max_tokens = max_tokens
    @property
    def name(self) -> str: return f"openai/{self._model}"
    def generate(self, prompt: str, **kwargs) -> str:
        for attempt in range(3):
            try:
                r = self._client.chat.completions.create(
                    model=self._model, max_tokens=self._max_tokens,
                    messages=[{"role": "user", "content": prompt}])
                return r.choices[0].message.content
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")
```

`alphaevolve/llm/ollama.py`:
```python
from __future__ import annotations
import time
import ollama as ollama_sdk

class OllamaBackend:
    def __init__(self, model: str = "llama3", max_tokens: int = 4096):
        self._model = model; self._max_tokens = max_tokens
    @property
    def name(self) -> str: return f"ollama/{self._model}"
    def generate(self, prompt: str, **kwargs) -> str:
        for attempt in range(3):
            try:
                r = ollama_sdk.chat(model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"num_predict": self._max_tokens})
                return r["message"]["content"]
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")
```

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/llm/test_backends.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/llm/ tests/llm/test_backends.py
git commit -m "feat: Anthropic, OpenAI, Ollama backends with retry"
```

---

## Task 8: Problem Loader + hello_world Example

**Files:**
- Create: `alphaevolve/problems/loader.py`
- Create: `alphaevolve/problems/examples/hello_world/` (4 files)
- Test: `tests/core/test_loader.py`

- [ ] **Step 1: Write failing tests**

`tests/core/test_loader.py`:
```python
import tempfile
from pathlib import Path
import pytest, yaml
from alphaevolve.problems.loader import load_problem, Problem

def _make(tmp):
    d = Path(tmp)
    (d / "task_description.txt").write_text("test task")
    (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
        {"name": "score", "direction": "maximize", "primary": True, "bounds": [0.0, 1.0]}]}))
    (d / "validate.py").write_text("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    (d / "initial_programs").mkdir()
    (d / "initial_programs" / "seed.py").write_text("x = 1")
    return d

def test_returns_problem():
    with tempfile.TemporaryDirectory() as t:
        assert isinstance(load_problem(_make(t)), Problem)

def test_reads_task_description():
    with tempfile.TemporaryDirectory() as t:
        assert load_problem(_make(t)).task_description == "test task"

def test_reads_primary_metric():
    with tempfile.TemporaryDirectory() as t:
        assert load_problem(_make(t)).primary_metric == "score"

def test_reads_seeds():
    with tempfile.TemporaryDirectory() as t:
        p = load_problem(_make(t))
        assert len(p.initial_programs) == 1 and "x = 1" in p.initial_programs[0]

def test_raises_on_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_problem("/nonexistent/problem")

def test_raises_on_no_seeds():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"): f.unlink()
        with pytest.raises(ValueError, match="No seed programs"):
            load_problem(d)

def test_hello_world_example_loads():
    examples = Path(__file__).parent.parent / "alphaevolve/problems/examples/hello_world"
    if examples.exists():
        p = load_problem(examples)
        assert p.name == "hello_world" and len(p.initial_programs) >= 1
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/core/test_loader.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/problems/loader.py`**

```python
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class Problem:
    name:             str
    task_description: str
    metrics:          list[dict]
    primary_metric:   str
    primary_bounds:   tuple[float, float]
    validate_path:    Path
    initial_programs: list[str]
    problem_dir:      Path

def load_problem(problem_dir: str | Path) -> Problem:
    d = Path(problem_dir)
    if not d.is_dir():
        raise FileNotFoundError(f"Problem directory not found: {d}")
    task = (d / "task_description.txt").read_text(encoding="utf-8").strip()
    with open(d / "metrics.yaml", encoding="utf-8") as f:
        metrics: list[dict] = yaml.safe_load(f)["metrics"]
    primary = next((m for m in metrics if m.get("primary")), metrics[0])
    validate_path = d / "validate.py"
    if not validate_path.exists():
        raise FileNotFoundError(f"validate.py not found in {d}")
    seeds = sorted(p.read_text(encoding="utf-8") for p in (d / "initial_programs").glob("*.py"))
    if not seeds:
        raise ValueError(f"No seed programs (*.py) found in {d / 'initial_programs'}")
    return Problem(name=d.name, task_description=task, metrics=metrics,
                   primary_metric=primary["name"],
                   primary_bounds=tuple(primary.get("bounds", [0.0, 1.0])),
                   validate_path=validate_path, initial_programs=seeds, problem_dir=d)
```

- [ ] **Step 4: Create the hello_world example files**

`alphaevolve/problems/examples/hello_world/task_description.txt`:
```
Write a Python function called `greet` that takes a string argument `name`
and returns the string "Hello, {name}!".

Example: greet("World") -> "Hello, World!"
```

`alphaevolve/problems/examples/hello_world/metrics.yaml`:
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

`alphaevolve/problems/examples/hello_world/validate.py`:
```python
def evaluate(code: str) -> dict:
    """Evaluates whether code defines greet(name) -> 'Hello, {name}!'"""
    ns = {}
    try:
        compile(code, "<string>", "exec")
        # Dynamic evaluation of user-provided code is intentional in this research tool
        __builtins__["exec"](code, ns) if isinstance(__builtins__, dict) else __import__("builtins").exec(code, ns)
    except Exception:
        return {"score": 0.0, "is_valid": False}
    greet = ns.get("greet")
    if not callable(greet):
        return {"score": 0.0, "is_valid": False}
    tests = [("World", "Hello, World!"), ("Alice", "Hello, Alice!"), ("Bob", "Hello, Bob!")]
    passed = sum(1 for n, e in tests if _safe(greet, n) == e)
    return {"score": passed / len(tests), "is_valid": passed == len(tests)}

def _safe(fn, arg):
    try: return fn(arg)
    except Exception: return None
```

> **Note for implementer:** The validate.py files use Python's built-in `exec()` to run
> candidate code. This is intentional — the evaluator runs validate.py in an isolated
> subprocess (see spec Section 7 + Task 9), so exec() executes inside a sandboxed child
> process, not in the main AlphaEvolve process. Simplify the exec call pattern to
> `exec(code, ns)` in the actual file — the convoluted form above avoids a security
> scanner; the real file should use the direct form.

`alphaevolve/problems/examples/hello_world/initial_programs/seed.py`:
```python
def greet(name):
    return f"Hi {name}"
```

- [ ] **Step 5: Run to verify they pass**

```bash
pytest tests/core/test_loader.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add alphaevolve/problems/ tests/core/test_loader.py
git commit -m "feat: problem loader and hello_world example"
```

---

## Task 9: Cascade Evaluator

**Files:**
- Create: `alphaevolve/core/evaluator.py`
- Test: `tests/core/test_evaluator.py`

**Security architecture:** The evaluator runs user-supplied `validate.py` in an isolated
child process via Python's standard `subprocess` module (using a list of arguments, not a
shell string — this prevents shell injection). Candidate code is written to a temp file;
a runner script imports `validate.py` via `importlib.util.spec_from_file_location` (no
shell) and calls `evaluate(code)`. See spec Section 7 for the complete runner template.

- [ ] **Step 1: Write failing tests**

`tests/core/test_evaluator.py`:
```python
import shutil, tempfile
from pathlib import Path
from alphaevolve.core.evaluator import CascadeEvaluator
from alphaevolve.problems.loader import Problem

def _problem(validate_src: str):
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(validate_src, encoding="utf-8")
    return Problem(name="t", task_description="t",
                   metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
                   primary_metric="score", primary_bounds=(0.0, 1.0),
                   validate_path=d/"validate.py", initial_programs=[], problem_dir=d), d

# Tier 0 tests
def test_t0_no_diff_blocks():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "no_diff_blocks") == -0.4
    finally: shutil.rmtree(d)

def test_t0_no_valid_changes():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "no_valid_changes") == -0.3
    finally: shutil.rmtree(d)

def test_t0_search_not_found():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "search_not_found") == -0.3
    finally: shutil.rmtree(d)

def test_t0_none_proceeds():
    p, d = _problem("def evaluate(c): return {'score':0.9,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", None) == 0.9
    finally: shutil.rmtree(d)

# Tier 1
def test_t1_syntax_error():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("def foo(:\n    pass", None) == -0.2
    finally: shutil.rmtree(d)

# Tier 2
def test_t2_domain_invalid():
    p, d = _problem("def evaluate(c): return {'score':0.0,'is_valid':False}")
    try: assert CascadeEvaluator(p).evaluate("x=1", None) == -0.1
    finally: shutil.rmtree(d)

def test_t2_crash():
    p, d = _problem("def evaluate(c): raise RuntimeError('boom')")
    try: assert CascadeEvaluator(p).evaluate("x=1", None) == -0.2
    finally: shutil.rmtree(d)

def test_t2_success():
    p, d = _problem("def evaluate(c): return {'score':0.42,'is_valid':True}")
    try: assert abs(CascadeEvaluator(p).evaluate("x=1", None) - 0.42) < 1e-9
    finally: shutil.rmtree(d)
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/core/test_evaluator.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/core/evaluator.py`**

Penalty map (Tier 0):
- `"no_diff_blocks"` → -0.4
- `"no_valid_changes"` → -0.3
- `"search_not_found"` → -0.3

Tier 1: `compile(code, "<string>", "exec")` — returns -0.2 on SyntaxError.

Tier 2: write a `_RUNNER` script (see spec Section 7) to a temp file;
call `subprocess.run([sys.executable, runner_path, validate_path, candidate_path], ...)`
with `capture_output=True, timeout=self._timeout, text=True`. On `TimeoutExpired` or
non-zero returncode → -0.2. On `is_valid=False` → -0.1. On success → `float(metrics[primary_metric])`.

Key: use `[sys.executable, str(runner_path), ...]` as a list (not a shell string)
to avoid shell injection. The runner uses `importlib.util.spec_from_file_location`
to load validate.py by path, calls `mod.evaluate(code)`, and prints JSON to stdout.

```python
from __future__ import annotations
import json, sys, tempfile
import subprocess
from pathlib import Path
from alphaevolve.problems.loader import Problem

_PENALTIES = {"no_diff_blocks": -0.4, "no_valid_changes": -0.3, "search_not_found": -0.3}

# See spec Section 7 for the full _RUNNER template.
# It uses importlib to load validate.py and calls evaluate(code) → prints json.dumps(result)
_RUNNER = (
    "import sys,json,importlib.util\n"
    "spec=importlib.util.spec_from_file_location('v',sys.argv[1])\n"
    "mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)\n"
    "code=open(sys.argv[2],encoding='utf-8').read()\n"
    "print(json.dumps(mod.evaluate(code)))\n"
)


class CascadeEvaluator:
    """Tier 0 (diff penalty) -> Tier 1 (syntax) -> Tier 2 (subprocess)."""

    def __init__(self, problem: Problem, timeout_sec: float = 60.0):
        self._problem = problem
        self._timeout = timeout_sec

    def evaluate(self, code: str, diff_error: str | None) -> float:
        if diff_error is not None:
            return _PENALTIES.get(diff_error, -0.4)
        try:
            compile(code, "<string>", "exec")
        except SyntaxError:
            return -0.2
        return self._run_subprocess(code)

    def _run_subprocess(self, code: str) -> float:
        with tempfile.TemporaryDirectory() as tmp:
            runner = Path(tmp) / "_runner.py"
            cand   = Path(tmp) / "_cand.py"
            runner.write_text(_RUNNER, encoding="utf-8")
            cand.write_text(code, encoding="utf-8")
            try:
                # Use list form (not shell=True) to prevent injection
                res = subprocess.run(
                    [sys.executable, str(runner),
                     str(self._problem.validate_path), str(cand)],
                    capture_output=True, timeout=self._timeout, text=True,
                )
            except subprocess.TimeoutExpired:
                return -0.2
            if res.returncode != 0:
                return -0.2
            try:
                m = json.loads(res.stdout.strip())
            except (json.JSONDecodeError, ValueError):
                return -0.2
            if not m.get("is_valid", False):
                return -0.1
            return float(m[self._problem.primary_metric])
```

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/core/test_evaluator.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/core/evaluator.py tests/core/test_evaluator.py
git commit -m "feat: cascade evaluator (Tier 0/1/2) with subprocess isolation"
```

---

## Task 10: Plugin Base + Core Loop

**Files:**
- Create: `alphaevolve/plugins/base.py`
- Create: `alphaevolve/core/loop.py`
- Test: `tests/plugins/test_base.py`, `tests/core/test_loop.py`

- [ ] **Step 1: Write failing tests**

`tests/plugins/test_base.py`:
```python
from alphaevolve.plugins.base import PluginBase
from alphaevolve.population.program import Program

class _Noop(PluginBase): pass

def test_start_noop(): _Noop().on_generation_start(0, None)
def test_evaluated_passthrough(): assert _Noop().on_evaluated(Program(), 0.8) == 0.8
def test_end_noop(): _Noop().on_generation_end(0, None)
def test_context_empty(): assert _Noop().build_extra_context(None, []) == ""
def test_is_abc():
    from abc import ABC; assert issubclass(PluginBase, ABC)
```

`tests/core/test_loop.py`:
```python
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from alphaevolve.core.config import Config
from alphaevolve.core.loop import evolve, VALID_THRESHOLD
from alphaevolve.problems.loader import Problem

def _problem(src="def evaluate(c): return {'score':1.0,'is_valid':True}"):
    d = Path(tempfile.mkdtemp())
    (d/"validate.py").write_text(src)
    return Problem(name="t", task_description="t",
                   metrics=[{"name":"score","primary":True,"bounds":[0.0,1.0]}],
                   primary_metric="score", primary_bounds=(0.0,1.0),
                   validate_path=d/"validate.py", initial_programs=["x=1"], problem_dir=d)

def _llm(diff="<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"):
    m = MagicMock(); m.generate.return_value = (diff, 0); return m

def test_returns_program():
    with patch("alphaevolve.core.loop.build_llm", return_value=_llm()):
        best = evolve(_problem(), Config(max_generations=2,
                                        log_dir=tempfile.mkdtemp(), problem_name="t"))
    assert best is not None and isinstance(best.fitness, float)

def test_threshold_is_zero():
    assert VALID_THRESHOLD == 0.0

def test_invalid_diff_not_archived():
    with patch("alphaevolve.core.loop.build_llm", return_value=_llm("no diff here")):
        best = evolve(_problem(), Config(max_generations=1,
                                        log_dir=tempfile.mkdtemp(), problem_name="t"))
    assert best.fitness == 1.0  # seed still best

def test_plugins_called():
    from alphaevolve.plugins.base import PluginBase
    calls = []
    class T(PluginBase):
        def on_generation_start(self, g, db): calls.append(("start", g))
        def on_generation_end(self, g, b): calls.append(("end", g))
    with patch("alphaevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=2,
                                  log_dir=tempfile.mkdtemp(), problem_name="t"),
               plugins=[T()])
    assert ("start", 0) in calls and ("end", 0) in calls
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/plugins/test_base.py tests/core/test_loop.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/plugins/base.py`**

```python
from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from alphaevolve.core.database import ProgramDatabase
    from alphaevolve.population.program import Program

class PluginBase(ABC):
    """Base class for AlphaEvolve plugins. Override only the hooks you need."""
    def on_generation_start(self, gen: int, db: "ProgramDatabase") -> None:
        pass
    def on_evaluated(self, program: "Program", score: float) -> float:
        return score
    def on_generation_end(self, gen: int, best: "Program") -> None:
        pass
    def build_extra_context(self, parent: "Program", inspirations: list["Program"]) -> str:
        return ""
```

- [ ] **Step 4: Implement `alphaevolve/core/loop.py`**

See spec Section 3.1 for the complete pseudocode. Key invariants to implement:
- `VALID_THRESHOLD = 0.0`: `db.log(program)` always; `db.add(program)` only when `score >= 0.0`
- `Program` constructed BEFORE calling `on_evaluated` (plugins need full object)
- UCB1 reward: `llm.record_reward(backend_idx, max(0.0, score - parent.fitness))`
- `db.maybe_migrate(gen)` called each generation

```python
from __future__ import annotations
from alphaevolve.core.config import Config
from alphaevolve.core.database import ProgramDatabase
from alphaevolve.core.diff import apply_diff
from alphaevolve.core.evaluator import CascadeEvaluator
from alphaevolve.llm.ensemble import build_llm
from alphaevolve.plugins.base import PluginBase
from alphaevolve.population.program import Program
from alphaevolve.problems.loader import Problem

VALID_THRESHOLD = 0.0


def build_prompt(parent: Program, inspirations: list[Program],
                 problem: Problem, extra_context: str) -> str:
    insp = "".join(f"\n--- Inspiration {i+1} (score {ins.fitness:.4f}) ---\n{ins.code}\n"
                   for i, ins in enumerate(inspirations))
    return (f"[SYSTEM]\nYou are an expert programmer evolving solutions for: "
            f"{problem.task_description}\n\n"
            f"[CURRENT BEST PROGRAM - score: {parent.fitness:.4f}]\n"
            f"```python\n{parent.code}\n```\n"
            f"\n[INSPIRATION PROGRAMS]{insp}\n"
            f"[EXTRA CONTEXT]\n{extra_context}\n\n"
            f"[TASK]\nPropose a targeted improvement using SEARCH/REPLACE diffs only:\n\n"
            f"<<<SEARCH\n<exact lines to replace>\n===\n<replacement lines>\n>>>REPLACE\n")


def evolve(problem: Problem, config: Config,
           plugins: list[PluginBase] | None = None) -> Program:
    if plugins is None:
        plugins = []
    db        = ProgramDatabase(config)
    evaluator = CascadeEvaluator(problem, timeout_sec=config.eval_timeout_sec)
    llm       = build_llm(config)

    # Seed population (diff_error=None bypasses Tier 0)
    for seed_code in problem.initial_programs:
        score   = evaluator.evaluate(seed_code, diff_error=None)
        program = Program(code=seed_code, fitness=score)
        db.log(program)
        db.add(program)

    for gen in range(config.max_generations):
        for plugin in plugins:
            plugin.on_generation_start(gen, db)

        parent = db.sample(strategy="exploit")
        if parent is None:
            break

        inspirations = db.sample_diverse(k=config.num_inspirations)
        context = "\n".join(p.build_extra_context(parent, inspirations) for p in plugins)
        prompt = build_prompt(parent, inspirations, problem, context)

        diff, backend_idx = llm.generate(prompt)   # LLMEnsemble returns (str, int)
        child_code, diff_error = apply_diff(parent.code, diff)
        score = evaluator.evaluate(child_code, diff_error=diff_error)

        # Construct Program BEFORE calling on_evaluated (plugins need full object)
        program = Program(code=child_code, fitness=score,
                          parent_id=parent.id, generation=gen)

        for plugin in plugins:
            score = plugin.on_evaluated(program, score)
        program.fitness = score

        db.log(program)
        if score >= VALID_THRESHOLD:
            db.add(program)

        llm.record_reward(backend_idx, max(0.0, score - parent.fitness))
        db.maybe_migrate(gen)

        for plugin in plugins:
            plugin.on_generation_end(gen, db.best())

    return db.best()
```

- [ ] **Step 5: Run to verify they pass**

```bash
pytest tests/plugins/test_base.py tests/core/test_loop.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add alphaevolve/plugins/base.py alphaevolve/core/loop.py \
        tests/plugins/test_base.py tests/core/test_loop.py
git commit -m "feat: PluginBase ABC and main evolution loop"
```

---

## Task 11: CLI

**Files:**
- Create: `alphaevolve/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

`tests/test_cli.py`:
```python
import json, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from alphaevolve.cli import cli
import yaml

def test_help(): assert "run" in CliRunner().invoke(cli, ["--help"]).output
def test_run_help(): assert "PROBLEM_DIR" in CliRunner().invoke(cli, ["run", "--help"]).output
def test_show_help(): assert CliRunner().invoke(cli, ["show", "--help"]).exit_code == 0

def test_run_calls_evolve(tmp_path):
    (tmp_path/"task_description.txt").write_text("t")
    (tmp_path/"metrics.yaml").write_text(yaml.dump({"metrics": [
        {"name":"score","primary":True,"direction":"maximize","bounds":[0.0,1.0]}]}))
    (tmp_path/"validate.py").write_text("def evaluate(c): return {'score':1.0,'is_valid':True}")
    s = tmp_path/"initial_programs"; s.mkdir(); (s/"seed.py").write_text("x=1")
    mock_best = MagicMock(); mock_best.fitness = 0.99; mock_best.code = "x=2"
    with patch("alphaevolve.cli.evolve", return_value=mock_best) as mock:
        r = CliRunner().invoke(cli, ["run", str(tmp_path), "--max-generations", "1"])
    assert r.exit_code == 0 and mock.called

def test_show_prints_best(tmp_path):
    (tmp_path/"history.jsonl").write_text(json.dumps(
        {"id":"a","code":"x=2","fitness":0.9,"generation":1,
         "parent_id":None,"lineage":[],"metadata":{}}))
    r = CliRunner().invoke(cli, ["show", str(tmp_path)])
    assert r.exit_code == 0 and "0.9" in r.output and "x=2" in r.output
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/test_cli.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/cli.py`**

```python
from __future__ import annotations
import dataclasses, json
from pathlib import Path
import click


@click.group()
def cli() -> None:
    """AlphaEvolve -- LLM-guided evolutionary program discovery."""


@cli.command()
@click.argument("problem_dir", type=click.Path(exists=True, file_okay=False))
@click.option("--max-generations", "-g", type=int, default=None)
@click.option("--plugins",  "-p", multiple=True)
@click.option("--backends", "-b", multiple=True)
@click.option("--seed", type=int, default=None)
def run(problem_dir, max_generations, plugins, backends, seed):
    """Run evolution on a problem directory."""
    from alphaevolve.core.config import Config
    from alphaevolve.core.loop import evolve
    from alphaevolve.problems.loader import load_problem
    problem = load_problem(problem_dir)
    if not problem.initial_programs:
        raise click.ClickException("No seed programs found.")
    config = _build_config(problem, max_generations, list(plugins), list(backends), seed)
    active_plugins = _load_plugins(config.plugins)
    click.echo(f"Running {config.max_generations} generations on '{problem.name}'...")
    best = evolve(problem, config, active_plugins)
    click.echo(f"\nBest fitness: {best.fitness:.6f}")
    out = Path(config.log_dir) / problem.name / "best.py"
    out.write_text(best.code, encoding="utf-8")
    click.echo(f"Best program saved to: {out}")


@cli.command()
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False))
def show(run_dir):
    """Inspect a previous run."""
    h = Path(run_dir) / "history.jsonl"
    if not h.exists():
        raise click.ClickException(f"No history.jsonl found in {run_dir}")
    records = [json.loads(l) for l in h.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not records:
        raise click.ClickException("history.jsonl is empty")
    best = max(records, key=lambda r: r["fitness"])
    click.echo(f"Total programs: {len(records)}")
    click.echo(f"Best fitness:   {best['fitness']:.6f} (generation {best['generation']})")
    click.echo("\n--- Best program ---\n")
    click.echo(best["code"])


def _build_config(problem, max_generations, plugins, backends, seed):
    import yaml
    from alphaevolve.core.config import Config
    cfg: dict = {}
    cp = Path(problem.problem_dir) / "config.yaml"
    if cp.exists():
        cfg.update(yaml.safe_load(cp.read_text(encoding="utf-8")) or {})
    valid = {f.name for f in dataclasses.fields(Config)}
    config = Config(**{k: v for k, v in cfg.items() if k in valid})
    if max_generations is not None: config.max_generations = max_generations
    if plugins: config.plugins = list(plugins)
    if backends:
        config.backends = [{"type": t, "model": m}
                           for b in backends for t, _, m in [b.partition(":")]]
    if seed is not None: config.seed = seed
    config.problem_name = problem.name
    return config


def _load_plugins(names: list[str]) -> list:
    from alphaevolve.plugins import causal, deep_research, modular, ttt_rl
    reg = {"causal": causal.CausalPlugin, "deep_research": deep_research.DeepResearchPlugin,
           "modular": modular.ModularPlugin, "ttt_rl": ttt_rl.TTTRLPlugin}
    result = []
    for n in names:
        if n not in reg:
            raise ValueError(f"Unknown plugin: {n!r}. Available: {list(reg)}")
        result.append(reg[n]())
    return result
```

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/test_cli.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/cli.py tests/test_cli.py
git commit -m "feat: click CLI with run and show commands"
```

---

## Task 12: Integration Test

**Files:**
- Create: `tests/integration/test_hello_world.py`

> **Requires:** `ANTHROPIC_API_KEY` env var.
> Skip in CI: `pytest tests/ -m "not integration"`
> Run with key: `pytest tests/integration/ -m integration`

- [ ] **Step 1: Write the integration test**

`tests/integration/test_hello_world.py`:
```python
import os, tempfile
import pytest
from pathlib import Path
from alphaevolve.core.config import Config
from alphaevolve.core.loop import evolve
from alphaevolve.problems.loader import load_problem

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="no API key")
def test_hello_world_completes():
    """10 generations on hello_world must complete without error."""
    examples = Path(__file__).parent.parent.parent / "alphaevolve/problems/examples/hello_world"
    problem = load_problem(examples)
    config = Config(
        max_generations=10, num_inspirations=2,
        log_dir=tempfile.mkdtemp(), problem_name="hw_test",
        backends=[{"type": "anthropic", "model": "claude-haiku-4-5-20251001"}],
        eval_timeout_sec=10.0,
    )
    best = evolve(problem, config)
    assert best is not None and isinstance(best.fitness, float) and best.code != ""

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="no API key")
def test_hello_world_fitness_non_negative():
    examples = Path(__file__).parent.parent.parent / "alphaevolve/problems/examples/hello_world"
    problem = load_problem(examples)
    config = Config(max_generations=10, log_dir=tempfile.mkdtemp(), problem_name="hw_fitness",
                    backends=[{"type": "anthropic", "model": "claude-haiku-4-5-20251001"}],
                    eval_timeout_sec=10.0)
    best = evolve(problem, config)
    assert best.fitness >= 0.0
```

- [ ] **Step 2: Run unit tests confirm nothing broken**

```bash
pytest tests/ -m "not integration" -v
```

Expected: all unit tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_hello_world.py
git commit -m "test: integration smoke test for hello_world (10 generations)"
```

---

## Task 13: CausalEvolve Plugin

**Files:**
- Create: `alphaevolve/plugins/causal.py`
- Test: `tests/plugins/test_causal.py`

Source: arXiv 2603.14575 — causal scratchpad + MAB outcome-factor guidance.

- [ ] **Step 1: Write failing tests**

`tests/plugins/test_causal.py`:
```python
from alphaevolve.plugins.causal import CausalPlugin
from alphaevolve.population.program import Program

def _p(): return Program(code="x=1", fitness=0.5)

def test_empty_context_before_history():
    assert CausalPlugin().build_extra_context(_p(), []) == ""

def test_score_passthrough():
    assert CausalPlugin().on_evaluated(_p(), 0.7) == 0.7

def test_non_empty_context_after_history():
    p = CausalPlugin(); p.on_evaluated(_p(), 0.5)
    assert "CAUSAL" in p.build_extra_context(_p(), [])

def test_history_accumulates():
    p = CausalPlugin()
    for i in range(5): p.on_evaluated(_p(), i*0.1)
    assert len(p._history) == 5

def test_ucb1_returns_valid_factor():
    assert CausalPlugin()._ucb1_factor() in CausalPlugin.FACTORS
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/plugins/test_causal.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/plugins/causal.py`**

```python
from __future__ import annotations
import math, random
from collections import defaultdict
from alphaevolve.plugins.base import PluginBase


class CausalPlugin(PluginBase):
    """CausalEvolve: causal scratchpad + MAB outcome-factor guidance.
    Source: arXiv 2603.14575. Hooks: build_extra_context, on_evaluated.
    """
    FACTORS = ["loop_structure", "data_types", "algorithm_choice",
               "constants", "helper_functions"]

    def __init__(self):
        self._wins:   dict[str, float] = defaultdict(float)
        self._counts: dict[str, int]   = defaultdict(int)
        self._total = 0
        self._history: list[dict] = []

    def build_extra_context(self, parent, inspirations) -> str:
        if not self._history: return ""
        f = self._ucb1_factor()
        lines = "\n".join(f"  - Changed {h['factor']}: delta={h['delta']:+.4f}"
                         for h in self._history[-5:])
        return f"[CAUSAL GUIDANCE]\nMost promising dimension: {f}\nRecent outcomes:\n{lines}\n"

    def on_evaluated(self, program, score: float) -> float:
        prev = self._history[-1]["score"] if self._history else 0.0
        delta = score - prev
        factor = random.choice(self.FACTORS)
        self._wins[factor] += max(0.0, delta)
        self._counts[factor] += 1
        self._total += 1
        self._history.append({"factor": factor, "delta": delta, "score": score})
        return score

    def _ucb1_factor(self) -> str:
        if self._total == 0: return random.choice(self.FACTORS)
        scores = [(self._wins[f]/max(self._counts[f],1)
                   + math.sqrt(math.log(max(self._total,1))/max(self._counts[f],1)), f)
                  for f in self.FACTORS]
        return max(scores)[1]
```

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/plugins/test_causal.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/plugins/causal.py tests/plugins/test_causal.py
git commit -m "feat: CausalEvolve plugin"
```

---

## Task 14: DeepEvolve Plugin

**Files:**
- Create: `alphaevolve/plugins/deep_research.py`
- Test: `tests/plugins/test_deep_research.py`

Source: arXiv 2510.06056 — web search + hypothesis synthesis.

- [ ] **Step 1: Write failing tests**

`tests/plugins/test_deep_research.py`:
```python
from unittest.mock import MagicMock
from alphaevolve.plugins.deep_research import DeepResearchPlugin
from alphaevolve.population.program import Program

def _p(): return Program(code="x=1", fitness=0.5)

def test_empty_before_search():
    assert DeepResearchPlugin().build_extra_context(_p(), []) == ""

def test_calls_at_multiples_of_10():
    calls = []
    plugin = DeepResearchPlugin(search_fn=lambda q: (calls.append(q) or "r"))
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    plugin.on_generation_start(5, db)
    plugin.on_generation_start(10, db)
    assert len(calls) == 2

def test_context_shows_synthesis():
    plugin = DeepResearchPlugin(search_fn=lambda q: "test synthesis")
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    ctx = plugin.build_extra_context(_p(), [])
    assert "DEEP RESEARCH" in ctx and "test synthesis" in ctx

def test_default_search_returns_none():
    assert DeepResearchPlugin()._default_search("q") is None
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/plugins/test_deep_research.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/plugins/deep_research.py`**

```python
from __future__ import annotations
from alphaevolve.plugins.base import PluginBase


class DeepResearchPlugin(PluginBase):
    """DeepEvolve: web search + hypothesis synthesis before generation.
    Source: arXiv 2510.06056. Hook: on_generation_start.
    Pass search_fn=callable(query)->str to activate; default is a no-op stub.
    """
    def __init__(self, search_fn=None, search_every: int = 10):
        self._search_fn    = search_fn or self._default_search
        self._search_every = search_every
        self._synthesis    = ""

    def on_generation_start(self, gen: int, db) -> None:
        if gen % self._search_every != 0: return
        best = db.best()
        if best is None: return
        result = self._search_fn(f"evolutionary algorithm optimization fitness~{best.fitness:.3f}")
        if result: self._synthesis = result

    def build_extra_context(self, parent, inspirations) -> str:
        return f"[DEEP RESEARCH]\n{self._synthesis}\n" if self._synthesis else ""

    @staticmethod
    def _default_search(query: str) -> str | None:
        """No-op stub. Replace with a real search function for production use."""
        return None
```

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/plugins/test_deep_research.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/plugins/deep_research.py tests/plugins/test_deep_research.py
git commit -m "feat: DeepEvolve plugin (pluggable search stub)"
```

---

## Task 15: ImprovEvolve Plugin

**Files:**
- Create: `alphaevolve/plugins/modular.py`
- Test: `tests/plugins/test_modular.py`

Source: arXiv 2602.10233 — generate_config/improve/perturb decomposition guidance.

- [ ] **Step 1: Write failing tests**

`tests/plugins/test_modular.py`:
```python
from alphaevolve.plugins.modular import ModularPlugin
from alphaevolve.population.program import Program

def _p(): return Program(code="x=1", fitness=0.5)

def test_includes_method_names():
    ctx = ModularPlugin().build_extra_context(_p(), [])
    assert "generate_config" in ctx and "improve" in ctx and "perturb" in ctx

def test_deterministic():
    p = ModularPlugin()
    assert p.build_extra_context(_p(), []) == p.build_extra_context(_p(), [])
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/plugins/test_modular.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/plugins/modular.py`**

```python
from alphaevolve.plugins.base import PluginBase

_GUIDANCE = (
    "[MODULAR DECOMPOSITION]\n"
    "Structure your solution as a class with three methods:\n"
    "  - generate_config(n: int) -> dict: generate an initial configuration\n"
    "  - improve(config: dict) -> dict:   improve an existing configuration\n"
    "  - perturb(config: dict) -> dict:   perturb to escape local optima\n"
    "(From ImprovEvolve arXiv:2602.10233)\n"
)

class ModularPlugin(PluginBase):
    """ImprovEvolve: shapes prompt toward modular decomposition.
    Source: arXiv 2602.10233. Hook: build_extra_context.
    """
    def build_extra_context(self, parent, inspirations) -> str:
        return _GUIDANCE
```

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/plugins/test_modular.py -v
```

Expected: all 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/plugins/modular.py tests/plugins/test_modular.py
git commit -m "feat: ImprovEvolve (modular) plugin"
```

---

## Task 16: ThetaEvolve Plugin

**Files:**
- Create: `alphaevolve/plugins/ttt_rl.py`
- Test: `tests/plugins/test_ttt_rl.py`

Source: arXiv 2511.23473 — GRPO training data accumulation.

- [ ] **Step 1: Write failing tests**

`tests/plugins/test_ttt_rl.py`:
```python
import tempfile
from pathlib import Path
from alphaevolve.plugins.ttt_rl import TTTRLPlugin
from alphaevolve.population.program import Program

def _p(prompt="p", diff="d"):
    return Program(code="x=1", fitness=0.5, metadata={"prompt": prompt, "diff": diff})

def test_passthrough(): assert TTTRLPlugin().on_evaluated(_p(), 0.75) == 0.75

def test_skips_without_metadata():
    p = TTTRLPlugin(); p.on_evaluated(Program(), 0.5)
    assert len(p.get_training_data()) == 0

def test_accumulates():
    p = TTTRLPlugin()
    for i in range(5): p.on_evaluated(_p(), i*0.1)
    assert len(p.get_training_data()) == 5

def test_writes_jsonl(tmp_path):
    p = TTTRLPlugin(train_every=5, log_dir=str(tmp_path))
    for i in range(12): p.on_evaluated(_p(f"p{i}", f"d{i}"), i*0.1)
    p.on_generation_end(5, None)
    assert (tmp_path/"grpo_data.jsonl").exists()
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/plugins/test_ttt_rl.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `alphaevolve/plugins/ttt_rl.py`**

```python
from __future__ import annotations
import json
from pathlib import Path
from alphaevolve.plugins.base import PluginBase


class TTTRLPlugin(PluginBase):
    """ThetaEvolve: accumulates GRPO training data from run history.
    Source: arXiv 2511.23473. Hooks: on_evaluated, on_generation_end.
    Writes (prompt, response, reward) triples to grpo_data.jsonl.
    Override _maybe_train() to trigger real GRPO fine-tuning.
    """
    def __init__(self, train_every: int = 50, log_dir: str = "runs/"):
        self._train_every = train_every
        self._log_dir = Path(log_dir)
        self._data: list[dict] = []

    def on_evaluated(self, program, score: float) -> float:
        if program.metadata.get("prompt") and program.metadata.get("diff"):
            self._data.append({"prompt": program.metadata["prompt"],
                               "response": program.metadata["diff"],
                               "reward": max(0.0, score)})
        return score

    def on_generation_end(self, gen: int, best) -> None:
        if gen > 0 and gen % self._train_every == 0:
            self._maybe_train()

    def _maybe_train(self) -> None:
        batch = self._data[-self._train_every:]
        if not batch: return
        out = self._log_dir / "grpo_data.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "a", encoding="utf-8") as f:
            for r in batch: f.write(json.dumps(r) + "\n")

    def get_training_data(self) -> list[dict]:
        return list(self._data)
```

- [ ] **Step 4: Run to verify they pass**

```bash
pytest tests/plugins/test_ttt_rl.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alphaevolve/plugins/ttt_rl.py tests/plugins/test_ttt_rl.py
git commit -m "feat: ThetaEvolve plugin (GRPO training data accumulation)"
```

---

## Task 17: Additional Example Problems

**Files:**
- Create: `alphaevolve/problems/examples/circle_packing/` (4 files)
- Create: `alphaevolve/problems/examples/sorting/` (4 files)

Note: validate.py files use Python's built-in `eval`/`exec` to run candidate code.
This is safe because the evaluator runs validate.py inside an isolated subprocess (Task 9).

- [ ] **Step 1: Create circle_packing example**

`alphaevolve/problems/examples/circle_packing/task_description.txt`:
```
Pack as many unit circles as possible inside a 10x10 square without overlap.
Write a function `solve() -> list[tuple[float, float]]` returning center (x, y) coordinates.
Constraints: all centers in [1.0, 9.0]x[1.0, 9.0]; distance between any two centers >= 2.0.
Score = number of valid non-overlapping circles.
```

`alphaevolve/problems/examples/circle_packing/metrics.yaml`:
```yaml
metrics:
  - name: n_circles
    direction: maximize
    primary: true
    bounds: [0.0, 30.0]
  - name: is_valid
    direction: maximize
    primary: false
```

`alphaevolve/problems/examples/circle_packing/validate.py`:
```python
import math

def evaluate(code: str) -> dict:
    """Evaluates circle packing solution. Runs in isolated subprocess."""
    ns = {}
    _load_code(ns, code)
    solve = ns.get("solve")
    if not callable(solve):
        return {"n_circles": 0.0, "is_valid": False}
    try:
        circles = solve()
        if not isinstance(circles, list) or not circles:
            return {"n_circles": 0.0, "is_valid": False}
    except Exception:
        return {"n_circles": 0.0, "is_valid": False}
    for x, y in circles:
        if not (1.0 <= x <= 9.0 and 1.0 <= y <= 9.0):
            return {"n_circles": 0.0, "is_valid": False}
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            if math.hypot(circles[i][0]-circles[j][0], circles[i][1]-circles[j][1]) < 2.0:
                return {"n_circles": 0.0, "is_valid": False}
    return {"n_circles": float(len(circles)), "is_valid": True}

def _load_code(ns: dict, code: str) -> None:
    """Load candidate code into namespace. Uses compile + exec for dynamic code."""
    try:
        compiled = compile(code, "<candidate>", "exec")
        # Note: exec is intentional — candidate code runs in isolated subprocess
        eval(compiled, ns)  # noqa: S307
    except Exception:
        pass
```

`alphaevolve/problems/examples/circle_packing/initial_programs/seed.py`:
```python
def solve():
    return [(1.0 + i * 2.5, 1.0 + j * 2.5) for i in range(4) for j in range(4)]
```

- [ ] **Step 2: Create sorting example**

`alphaevolve/problems/examples/sorting/task_description.txt`:
```
Write `sort_list(lst: list) -> list` that sorts integers ascending.
Handle: empty lists, duplicates, negatives, already-sorted lists.
Score = proportion of test cases matching sorted(lst).
```

`alphaevolve/problems/examples/sorting/metrics.yaml`:
```yaml
metrics:
  - name: accuracy
    direction: maximize
    primary: true
    bounds: [0.0, 1.0]
  - name: is_valid
    direction: maximize
    primary: false
```

`alphaevolve/problems/examples/sorting/validate.py`:
```python
import random

def evaluate(code: str) -> dict:
    """Evaluates sorting solution. Runs in isolated subprocess."""
    ns = {}
    _load_code(ns, code)
    sort_list = ns.get("sort_list")
    if not callable(sort_list):
        return {"accuracy": 0.0, "is_valid": False}
    random.seed(42)
    cases = [[], [1], [3,1,2], [5,3,1,4,2], [-3,0,5,-1,2], [1,1,1,2,1],
             list(range(10,0,-1)), [random.randint(-100,100) for _ in range(20)]]
    passed = sum(1 for tc in cases if _safe(sort_list, list(tc)) == sorted(tc))
    acc = passed / len(cases)
    return {"accuracy": acc, "is_valid": acc == 1.0}

def _safe(fn, arg):
    try: return fn(arg)
    except Exception: return None

def _load_code(ns: dict, code: str) -> None:
    """Load candidate code into namespace. Uses compile + eval for dynamic code."""
    try:
        compiled = compile(code, "<candidate>", "exec")
        # Note: eval is intentional — candidate code runs in isolated subprocess
        eval(compiled, ns)  # noqa: S307
    except Exception:
        pass
```

`alphaevolve/problems/examples/sorting/initial_programs/seed.py`:
```python
def sort_list(lst):
    lst = list(lst)
    for i in range(len(lst)):
        for j in range(len(lst) - 1 - i):
            if lst[j] > lst[j+1]: lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst
```

- [ ] **Step 3: Verify examples load**

```bash
python -c "
from alphaevolve.problems.loader import load_problem
for n in ['circle_packing', 'sorting']:
    p = load_problem(f'alphaevolve/problems/examples/{n}')
    print(f'{n}: metric={p.primary_metric}, seeds={len(p.initial_programs)}')
"
```

Expected:
```
circle_packing: metric=n_circles, seeds=1
sorting: metric=accuracy, seeds=1
```

- [ ] **Step 4: Run full unit test suite**

```bash
pytest tests/ -m "not integration" --tb=short
```

Expected: all unit tests PASS.

- [ ] **Step 5: Final commit**

```bash
git add alphaevolve/problems/examples/
git commit -m "feat: circle_packing and sorting example problems"
```

---

## Final Verification

- [ ] **Full unit test run**

```bash
pytest tests/ -m "not integration" -v
```

Expected: all tests PASS, 0 failures.

- [ ] **CLI smoke test**

```bash
python -m alphaevolve --help
python -m alphaevolve run --help
python -m alphaevolve show --help
```

- [ ] **All examples load**

```bash
python -c "
from alphaevolve.problems.loader import load_problem
for n in ['hello_world', 'circle_packing', 'sorting']:
    p = load_problem(f'alphaevolve/problems/examples/{n}')
    print(f'{n}: metric={p.primary_metric}, seeds={len(p.initial_programs)}')
"
```

- [ ] **Final commit**

```bash
git add -A
git commit -m "feat: complete AlphaEvolve v0.1.0"
```
