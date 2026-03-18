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
