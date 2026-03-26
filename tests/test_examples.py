from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


EXAMPLE_DIR = (
    Path(__file__).resolve().parents[1]
    / "libreevolve"
    / "problems"
    / "examples"
    / "circle_packing"
)


def _load_validator():
    spec = spec_from_file_location("circle_validate", EXAMPLE_DIR / "validate.py")
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_circle_packing_seed_is_valid_and_nontrivial():
    validate = _load_validator()
    seed = (EXAMPLE_DIR / "initial_programs" / "seed.py").read_text(encoding="utf-8")
    result = validate.evaluate(seed)
    assert result["is_valid"] is True
    assert result["sum_radii"] > 2.0


def test_circle_packing_rejects_wrong_circle_count():
    validate = _load_validator()
    result = validate.evaluate(
        "def solve():\n"
        "    return [(0.5, 0.5, 0.1)]\n"
    )
    assert result == {"sum_radii": 0.0, "is_valid": False}


def test_circle_packing_rejects_overlapping_circles():
    validate = _load_validator()
    circles = ",\n        ".join(["(0.5, 0.5, 0.05)"] * 26)
    result = validate.evaluate(
        "def solve():\n"
        "    return [\n"
        f"        {circles}\n"
        "    ]\n"
    )
    assert result == {"sum_radii": 0.0, "is_valid": False}
