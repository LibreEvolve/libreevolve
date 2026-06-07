from libreevolve.plugins.modular import ModularPlugin
from libreevolve.population.program import Program

def _p(): return Program(code="x=1", fitness=0.5)

def test_includes_method_names():
    ctx = ModularPlugin().build_extra_context(_p(), [])
    assert "generate_config" in ctx and "improve" in ctx and "perturb" in ctx

def test_deterministic():
    p = ModularPlugin()
    assert p.build_extra_context(_p(), []) == p.build_extra_context(_p(), [])

def test_prompt_context_metadata_labels_static_guidance():
    metadata = ModularPlugin().prompt_context_metadata()
    assert metadata == {
        "paper_inspiration": "ImprovEvolve",
        "strategy_policy": "static_prompt_only",
        "operation_selected": "static_modular_guidance",
        "operation_executed": False,
        "interface_enforced": False,
        "described_operations": ["generate_config", "improve", "perturb"],
    }
