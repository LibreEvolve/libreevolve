from libreevolve.plugins.base import PluginBase

_GUIDANCE = (
    "[MODULAR DECOMPOSITION]\n"
    "Structure your solution as a class with three methods:\n"
    "  - generate_config(n: int) -> dict: generate an initial configuration\n"
    "  - improve(config: dict) -> dict:   improve an existing configuration\n"
    "  - perturb(config: dict) -> dict:   perturb to escape local optima\n"
    "(From ImprovEvolve arXiv:2602.10233)\n"
)

class ModularPlugin(PluginBase):
    """ImprovEvolve-inspired modular decomposition prompt guidance.

    This does not enforce or execute ImprovEvolve's interface/search loop.
    Source: arXiv 2602.10233. Hook: build_extra_context.
    """
    def build_extra_context(self, parent, inspirations) -> str:
        return _GUIDANCE
