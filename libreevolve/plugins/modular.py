from libreevolve.plugins.base import PluginBase

_GUIDANCE = (
    "[MODULAR DECOMPOSITION]\n"
    "Structure your solution as a class with three methods:\n"
    "  - generate_config(n: int) -> dict: generate an initial configuration\n"
    "  - improve(config: dict) -> dict:   improve an existing configuration\n"
    "  - perturb(config: dict) -> dict:   perturb to escape local optima\n"
    "(Inspired by ImprovEvolve arXiv:2602.10233; interface not enforced)\n"
)

class ModularPlugin(PluginBase):
    """ImprovEvolve-inspired modular decomposition prompt guidance.

    This does not enforce or execute ImprovEvolve's interface/search loop.
    Hook: build_extra_context.
    """
    def build_extra_context(self, parent, inspirations) -> str:
        return _GUIDANCE

    def prompt_context_metadata(self) -> dict:
        return {
            "paper_inspiration": "ImprovEvolve",
            "strategy_policy": "static_prompt_only",
            "operation_selected": "static_modular_guidance",
            "operation_executed": False,
            "interface_enforced": False,
            "described_operations": ["generate_config", "improve", "perturb"],
        }
