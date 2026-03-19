from libreevolve.plugins.base import PluginBase
from libreevolve.population.program import Program

class _Noop(PluginBase): pass

def test_start_noop(): _Noop().on_generation_start(0, None)
def test_evaluated_passthrough(): assert _Noop().on_evaluated(Program(), 0.8) == 0.8
def test_end_noop(): _Noop().on_generation_end(0, None)
def test_context_empty(): assert _Noop().build_extra_context(None, []) == ""
def test_is_abc():
    from abc import ABC; assert issubclass(PluginBase, ABC)
