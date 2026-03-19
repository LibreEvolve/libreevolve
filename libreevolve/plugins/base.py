from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from libreevolve.core.database import ProgramDatabase
    from libreevolve.population.program import Program

class PluginBase(ABC):
    """Base class for LibreEvolve plugins. Override only the hooks you need."""
    def on_generation_start(self, gen: int, db: "ProgramDatabase") -> None:
        pass
    def on_evaluated(self, program: "Program", score: float) -> float:
        return score
    def on_generation_end(self, gen: int, best: "Program") -> None:
        pass
    def build_extra_context(self, parent: "Program", inspirations: list["Program"]) -> str:
        return ""
