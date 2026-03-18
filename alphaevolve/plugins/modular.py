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
