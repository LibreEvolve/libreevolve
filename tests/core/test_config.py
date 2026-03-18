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
