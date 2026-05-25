import pytest

from libreevolve.core.config import Config, ConfigError

def test_default_max_generations():
    assert Config().max_generations == 1000

def test_default_n_islands():
    assert Config().n_islands == 5

def test_override_fields():
    c = Config(max_generations=50, seed=99)
    assert c.max_generations == 50 and c.seed == 99

def test_default_backend_is_anthropic():
    assert Config().backends[0]["type"] == "anthropic"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"max_generations": -1}, "max_generations"),
        ({"num_inspirations": -1}, "num_inspirations"),
        ({"eval_timeout_sec": 0}, "eval_timeout_sec"),
        ({"explore_ratio": 1.5}, "explore_ratio"),
        ({"mutation_mode": "rewrite"}, "mutation_mode"),
        ({"n_islands": 0}, "n_islands"),
        ({"migration_interval": -1}, "migration_interval"),
        ({"migration_ratio": -0.1}, "migration_ratio"),
        ({"map_elites_bins": 0}, "map_elites_bins"),
        ({"elite_archive_size": 0}, "elite_archive_size"),
        ({"ensemble_explore_coeff": -1.0}, "ensemble_explore_coeff"),
        ({"ensemble_strategy": "random"}, "ensemble_strategy"),
    ],
)
def test_rejects_invalid_top_level_config(kwargs, message):
    with pytest.raises(ConfigError, match=message):
        Config(**kwargs)


@pytest.mark.parametrize(
    ("stage", "message"),
    [
        ({"samples": 0}, "samples"),
        ({"retries": -1}, "retries"),
        ({"timeout_sec": 0}, "timeout_sec"),
        ({"min_score": "high"}, "min_score"),
        ({"samples": 1, "seeds": [1, 2]}, "samples"),
        ({"unknown": True}, "unsupported"),
    ],
)
def test_rejects_invalid_eval_stage_config(stage, message):
    with pytest.raises(ConfigError, match=message):
        Config(eval_stages=[stage])


@pytest.mark.parametrize(
    ("backend", "message"),
    [
        ({"type": "openai"}, "model"),
        ({"type": "bad", "model": "m"}, "type"),
        ({"type": "openai", "model": ""}, "model"),
        ({"type": "anthropic", "model": "m", "reasoning_effort": "high"}, "unsupported"),
        ({"type": "openai", "model": "m", "reasoning_effort": "extreme"}, "reasoning_effort"),
        ({"type": "openai", "model": "m", "cost": 0}, "cost"),
        ({"type": "openai", "model": "m", "extra": True}, "unsupported"),
    ],
)
def test_rejects_invalid_backend_config(backend, message):
    with pytest.raises(ConfigError, match=message):
        Config(backends=[backend])
