from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from libreevolve.core.evaluator import CascadeEvaluator
from libreevolve.problems.loader import load_problem


EXAMPLE_DIR = (
    Path(__file__).resolve().parents[1]
    / "libreevolve"
    / "problems"
    / "examples"
    / "circle_packing"
)
MATRIX_EXAMPLE_DIR = (
    Path(__file__).resolve().parents[1]
    / "libreevolve"
    / "problems"
    / "examples"
    / "matrix_multiplication"
)
WORKSPACE_EXAMPLE_DIR = (
    Path(__file__).resolve().parents[1]
    / "libreevolve"
    / "problems"
    / "examples"
    / "workspace_math"
)
HELLO_EXAMPLE_DIR = (
    Path(__file__).resolve().parents[1]
    / "libreevolve"
    / "problems"
    / "examples"
    / "hello_world"
)
SORTING_EXAMPLE_DIR = (
    Path(__file__).resolve().parents[1]
    / "libreevolve"
    / "problems"
    / "examples"
    / "sorting"
)
EXAMPLE_RUNS_DIR = Path(__file__).resolve().parents[1] / "examples" / "runs"


def test_checked_in_example_runs_are_documented_legacy_history_fixtures():
    readme = (EXAMPLE_RUNS_DIR / "README.md").read_text(encoding="utf-8")
    legacy_runs = ("hello_world_ensemble", "sorting_ttt_rl")
    legacy_files = {"history.jsonl", "best.py"}
    modern_missing = {
        "manifest.json",
        "archive_events.jsonl",
        "llm_calls.jsonl",
        "prompt_history.jsonl",
        "failure_history.jsonl",
        "best_workspace/",
    }

    assert "legacy history fixtures" in readme
    for artifact in modern_missing:
        assert artifact in readme
    for run_name in legacy_runs:
        run_dir = EXAMPLE_RUNS_DIR / run_name
        assert {path.name for path in run_dir.iterdir()} == legacy_files
        assert (run_dir / "history.jsonl").read_text(encoding="utf-8").strip()
        assert (run_dir / "best.py").read_text(encoding="utf-8").strip()


def _load_validator():
    spec = spec_from_file_location("circle_validate", EXAMPLE_DIR / "validate.py")
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_matrix_validator():
    spec = spec_from_file_location("matrix_validate", MATRIX_EXAMPLE_DIR / "validate.py")
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_workspace_validator():
    spec = spec_from_file_location("workspace_validate", WORKSPACE_EXAMPLE_DIR / "validate.py")
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_hello_validator():
    spec = spec_from_file_location("hello_validate", HELLO_EXAMPLE_DIR / "validate.py")
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_sorting_validator():
    spec = spec_from_file_location("sorting_validate", SORTING_EXAMPLE_DIR / "validate.py")
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_hello_world_accepts_exact_string_contract():
    validate = _load_hello_validator()
    result = validate.evaluate("def greet(name):\n    return f'Hello, {name}!'\n")
    assert result == {"score": 1.0, "is_valid": True}


def test_hello_world_rejects_equality_spoofing_object():
    validate = _load_hello_validator()
    result = validate.evaluate(
        "class AlwaysEqual:\n"
        "    def __eq__(self, other): return True\n"
        "def greet(name):\n"
        "    return AlwaysEqual()\n"
    )
    assert result == {"score": 0.0, "is_valid": False}


def test_hello_world_rejects_non_string_equalish_payload():
    validate = _load_hello_validator()
    result = validate.evaluate("def greet(name):\n    return b'Hello, World!'\n")
    assert result == {"score": 0.0, "is_valid": False}


def test_sorting_seed_is_valid_with_exact_list_contract():
    validate = _load_sorting_validator()
    seed = (SORTING_EXAMPLE_DIR / "initial_programs" / "seed.py").read_text(encoding="utf-8")
    result = validate.evaluate(seed)
    assert result == {"accuracy": 1.0, "is_valid": True}


def test_example_seed_pressure_classification_is_documented():
    hello_validate = _load_hello_validator()
    circle_validate = _load_validator()
    sorting_validate = _load_sorting_validator()
    matrix_validate = _load_matrix_validator()
    root = Path(__file__).resolve().parents[1]

    hello_seed = (HELLO_EXAMPLE_DIR / "initial_programs" / "seed.py").read_text(
        encoding="utf-8"
    )
    circle_seed = (EXAMPLE_DIR / "initial_programs" / "seed.py").read_text(
        encoding="utf-8"
    )
    sorting_seed = (SORTING_EXAMPLE_DIR / "initial_programs" / "seed.py").read_text(
        encoding="utf-8"
    )
    matrix_seed = (MATRIX_EXAMPLE_DIR / "initial_programs" / "seed.py").read_text(
        encoding="utf-8"
    )
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert hello_validate.evaluate(hello_seed) == {"score": 0.0, "is_valid": False}
    circle_result = circle_validate.evaluate(circle_seed)
    assert circle_result["is_valid"] is True
    assert 0.0 < circle_result["sum_radii"] < 3.0
    assert sorting_validate.evaluate(sorting_seed) == {
        "accuracy": 1.0,
        "is_valid": True,
    }
    matrix_result = matrix_validate.evaluate(matrix_seed)
    assert matrix_result["is_valid"] is True
    assert matrix_result["multiplication_count"] == 8
    assert "Optimization-pressure seeds" in readme
    assert "neutral plateau/diversity fixtures" in readme


def test_sorting_rejects_equality_spoofing_object():
    validate = _load_sorting_validator()
    result = validate.evaluate(
        "class AlwaysEqual:\n"
        "    def __eq__(self, other): return True\n"
        "def sort_list(lst):\n"
        "    return AlwaysEqual()\n"
    )
    assert result == {"accuracy": 0.0, "is_valid": False}


def test_sorting_rejects_tuple_even_when_values_are_sorted():
    validate = _load_sorting_validator()
    result = validate.evaluate("def sort_list(lst):\n    return tuple(sorted(lst))\n")
    assert result == {"accuracy": 0.0, "is_valid": False}


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


def test_circle_packing_rejects_spoofed_list_count():
    validate = _load_validator()
    result = validate.evaluate(
        "class SpoofedCircles(list):\n"
        "    def __len__(self):\n"
        "        return 26\n"
        "    def __iter__(self):\n"
        "        for row in range(10):\n"
        "            for col in range(10):\n"
        "                yield (0.05 + col * 0.1, 0.05 + row * 0.1, 0.04)\n"
        "def solve():\n"
        "    return SpoofedCircles()\n"
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


def test_matrix_multiplication_seed_is_valid_and_marked():
    validate = _load_matrix_validator()
    seed = (MATRIX_EXAMPLE_DIR / "initial_programs" / "seed.py").read_text(encoding="utf-8")
    result = validate.evaluate(seed)
    assert "# EVOLVE-BLOCK-START" in seed
    assert result["is_valid"] is True
    assert result["multiplication_count"] == 8


def test_matrix_multiplication_metric_bounds_preserve_improvement_order():
    problem = load_problem(MATRIX_EXAMPLE_DIR)
    evaluator = CascadeEvaluator(problem)
    seed = (MATRIX_EXAMPLE_DIR / "initial_programs" / "seed.py").read_text(encoding="utf-8")
    strassen = (
        "def matmul2(a, b):\n"
        "    m1 = (a[0][0] + a[1][1]) * (b[0][0] + b[1][1])\n"
        "    m2 = (a[1][0] + a[1][1]) * b[0][0]\n"
        "    m3 = a[0][0] * (b[0][1] - b[1][1])\n"
        "    m4 = a[1][1] * (b[1][0] - b[0][0])\n"
        "    m5 = (a[0][0] + a[0][1]) * b[1][1]\n"
        "    m6 = (a[1][0] - a[0][0]) * (b[0][0] + b[0][1])\n"
        "    m7 = (a[0][1] - a[1][1]) * (b[1][0] + b[1][1])\n"
        "    return [[m1 + m4 - m5 + m7, m3 + m5], [m2 + m4, m1 - m2 + m3 + m6]]\n"
    )

    seed_result = evaluator.evaluate(seed, diff_error=None)
    improved_result = evaluator.evaluate(strassen, diff_error=None)

    assert seed_result.metrics["multiplication_count"] == 8
    assert improved_result.metrics["multiplication_count"] == 7
    assert improved_result.fitness > seed_result.fitness
    assert "metric_bound_diagnostics" not in seed_result.metadata
    assert "metric_bound_diagnostics" not in improved_result.metadata


def test_matrix_multiplication_rejects_wrong_result():
    validate = _load_matrix_validator()
    result = validate.evaluate("def matmul2(a, b):\n    return [[0, 0], [0, 0]]\n")
    assert result["is_valid"] is False


def test_matrix_multiplication_counts_only_function_body_multiplications():
    validate = _load_matrix_validator()
    result = validate.evaluate(
        "dummy = 1 * 1\n"
        "def matmul2(a, b):\n"
        "    return [[0, 0], [0, 0]]\n"
    )

    assert result["is_valid"] is False
    assert result["multiplication_count"] == 0


def test_matrix_multiplication_rejects_import_delegation():
    validate = _load_matrix_validator()
    result = validate.evaluate(
        "import numpy as np\n"
        "def matmul2(a, b):\n"
        "    _dummy = 1 * 1\n"
        "    return np.matmul(a, b).tolist()\n"
    )

    assert result["is_valid"] is False
    assert result["multiplication_count"] == 0


def test_matrix_multiplication_rejects_three_case_lookup_shortcut():
    validate = _load_matrix_validator()
    result = validate.evaluate(
        "def matmul2(a, b):\n"
        "    _dummy = 1 * 1\n"
        "    if a == [[1, 2], [3, 4]] and b == [[5, 6], [7, 8]]:\n"
        "        return [[19, 22], [43, 50]]\n"
        "    if a == [[0, -1], [2, 3]] and b == [[4, 5], [-6, 7]]:\n"
        "        return [[6, -7], [-10, 31]]\n"
        "    if a == [[2, 0], [0, 2]] and b == [[-1, 3], [4, -5]]:\n"
        "        return [[-2, 6], [8, -10]]\n"
        "    return [[0, 0], [0, 0]]\n"
    )

    assert result["is_valid"] is False
    assert result["multiplication_count"] == 1


def test_workspace_math_seed_is_valid(tmp_path):
    validate = _load_workspace_validator()
    seed_dir = WORKSPACE_EXAMPLE_DIR / "initial_programs" / "baseline"
    for path in seed_dir.rglob("*"):
        if not path.is_file():
            continue
        target = tmp_path / path.relative_to(seed_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    code = (tmp_path / "main.py").read_text(encoding="utf-8")

    result = validate.evaluate(code, str(tmp_path))

    assert result == {"score": 1.0, "is_valid": True}


def test_workspace_math_loader_records_nested_static_seed_workspace():
    problem = load_problem(WORKSPACE_EXAMPLE_DIR)

    assert len(problem.initial_workspaces) == 1
    workspace = problem.initial_workspaces[0]
    assert workspace.primary_file == "main.py"
    assert set(workspace.files) == {
        "data/config.json",
        "main.py",
        "pkg/__init__.py",
        "pkg/helpers.py",
    }
    assert workspace.static_files == (
        {
            "path": "assets/offset.bin",
            "kind": "binary",
            "sha256": "c3afce6b353535458babb7126b512b57309862bae6c8fe361e20854270e6c5b7",
            "bytes": 10,
            "source_kind": "seed_workspace_file",
            "source_path": "initial_programs/baseline/assets/offset.bin",
            "mutation_policy": "immutable",
            "content_b64": "/0xFU1RBVElDCg==",
        },
    )


def _write_workspace_math_support_files(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "helpers.py").write_text(
        "import json\n"
        "from pathlib import Path\n"
        "def base_value():\n"
        "    root = Path(__file__).resolve().parents[1]\n"
        "    config = json.loads((root / 'data' / 'config.json').read_text(encoding='utf-8'))\n"
        "    return int(config['base']) + int(config['asset_offset'])\n",
        encoding="utf-8",
    )
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "config.json").write_text(
        '{"label": "workspace_math", "base": 40, "asset_offset": 1}',
        encoding="utf-8",
    )
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "offset.bin").write_bytes(b"\xffLESTATIC\n")


def test_workspace_math_rejects_direct_constant_without_helper_dependency(tmp_path):
    validate = _load_workspace_validator()
    (tmp_path / "main.py").write_text("def solve():\n    return 42\n", encoding="utf-8")
    _write_workspace_math_support_files(tmp_path)

    result = validate.evaluate((tmp_path / "main.py").read_text(encoding="utf-8"), str(tmp_path))

    assert result == {"score": 0.0, "is_valid": False}


def test_workspace_math_rejects_equality_spoofing_result(tmp_path):
    validate = _load_workspace_validator()
    (tmp_path / "main.py").write_text(
        "from pkg.helpers import base_value\n"
        "class AlwaysEqual:\n"
        "    def __eq__(self, other): return True\n"
        "def solve():\n"
        "    base_value()\n"
        "    return AlwaysEqual()\n",
        encoding="utf-8",
    )
    _write_workspace_math_support_files(tmp_path)

    result = validate.evaluate((tmp_path / "main.py").read_text(encoding="utf-8"), str(tmp_path))

    assert result == {"score": 0.0, "is_valid": False}


def test_workspace_math_rejects_float_result(tmp_path):
    validate = _load_workspace_validator()
    (tmp_path / "main.py").write_text(
        "from pkg.helpers import base_value\n"
        "def solve():\n"
        "    return float(base_value() + 1)\n",
        encoding="utf-8",
    )
    _write_workspace_math_support_files(tmp_path)

    result = validate.evaluate((tmp_path / "main.py").read_text(encoding="utf-8"), str(tmp_path))

    assert result == {"score": 0.0, "is_valid": False}
