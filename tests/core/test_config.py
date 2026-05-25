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
        ({"prompt_reward_mode": "delta"}, "prompt_reward_mode"),
        ({"prompt_reward_bounds": [1.0, 1.0]}, "prompt_reward_bounds"),
        ({"prompt_reward_bounds": [1.0]}, "prompt_reward_bounds"),
        ({"prompt_explore_coeff": -1.0}, "prompt_explore_coeff"),
        ({"run_id": ""}, "run_id"),
        ({"run_collision_policy": "append"}, "run_collision_policy"),
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


@pytest.mark.parametrize(
    ("grader", "message"),
    [
        ("simplicity", "llm_feedback"),
        ({"name": 7}, "name"),
        ({"metric": 7}, "metric"),
        ({"prompt": 7}, "prompt"),
        ({"weight": "heavy"}, "weight"),
        ({"min_score": "low"}, "min_score"),
        ({"include_invalid": "yes"}, "include_invalid"),
        ({"extra": True}, "unsupported"),
    ],
)
def test_rejects_invalid_llm_feedback_config(grader, message):
    with pytest.raises(ConfigError, match=message):
        Config(llm_feedback=[grader])


def test_accepts_valid_llm_feedback_config():
    config = Config(llm_feedback=[{
        "name": "simplicity",
        "metric": "llm_simplicity",
        "weight": 0.2,
        "min_score": 0.1,
        "prompt": "Return JSON",
        "include_invalid": True,
    }])
    assert config.llm_feedback[0]["name"] == "simplicity"


@pytest.mark.parametrize(
    ("template", "message"),
    [
        ("Task: {missing_field}", "unknown"),
        ("No task field", "missing required"),
        ("Task: {task", "malformed"),
    ],
)
def test_rejects_invalid_prompt_variant_templates(template, message):
    with pytest.raises(ConfigError, match=message):
        Config(prompt_variants=[template])


def test_accepts_minimal_prompt_variant_template():
    assert Config(prompt_variants=["Task: {task}"]).prompt_variants == ["Task: {task}"]


def test_accepts_prompt_reward_policy_config():
    config = Config(
        prompt_reward_mode="improvement",
        prompt_reward_bounds=[-1.0, 1.0],
        prompt_explore_coeff=0.25,
    )
    assert config.prompt_reward_mode == "improvement"
    assert config.prompt_reward_bounds == [-1.0, 1.0]
    assert config.prompt_explore_coeff == 0.25
