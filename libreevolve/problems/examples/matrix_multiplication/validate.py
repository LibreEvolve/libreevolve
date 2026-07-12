import ast
import json
import math
from pathlib import Path


DEFAULT_CASE_SET_ID = "main_cases"
CASE_SET_IDS = frozenset({"smoke_cases", "main_cases"})
FIXTURE_ROOT = Path(__file__).with_name("fixtures")


def evaluate(code: str, workspace: str | None = None, stage: dict | None = None) -> dict:
    del workspace
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _invalid()
    if _has_forbidden_constructs(tree):
        return _invalid()
    fn_node = _find_matmul2_function(tree)
    if fn_node is None:
        return _invalid()
    count = _multiplication_count(fn_node)
    if count <= 0:
        return _invalid()
    ns = {}
    try:
        exec(compile(tree, "<candidate>", "exec"), ns)  # noqa: S102
    except Exception:
        return _invalid(count)
    fn = ns.get("matmul2")
    if not callable(fn):
        return _invalid(count)
    try:
        case_set_id, cases, seed = _load_cases(stage)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return _invalid(count)
    try:
        for a, b in _seed_ordered_cases(cases, seed):
            got = fn(a, b)
            if got != _expected(a, b):
                return _invalid(count)
    except Exception:
        return _invalid(count)
    return {
        "inverse_multiplications": 1.0 / count,
        "multiplication_count": count,
        "is_valid": True,
        "outputs": {
            "case_set_id": case_set_id,
            "case_count": len(cases),
            "seed": seed,
        },
    }


def _load_cases(stage: dict | None) -> tuple[str, list[tuple[list, list]], int | None]:
    case_set_id = DEFAULT_CASE_SET_ID
    seed = None
    if isinstance(stage, dict):
        raw_seed = stage.get("seed")
        if isinstance(raw_seed, int) and not isinstance(raw_seed, bool):
            seed = raw_seed
        config = stage.get("config")
        test_set = config.get("test_set") if isinstance(config, dict) else None
        if isinstance(test_set, dict):
            case_set_id = str(test_set.get("id", DEFAULT_CASE_SET_ID))
    if case_set_id not in CASE_SET_IDS:
        raise ValueError(f"unknown matrix case set: {case_set_id}")
    payload = json.loads(
        (FIXTURE_ROOT / f"{case_set_id}.json").read_text(encoding="utf-8")
    )
    if payload.get("schema") != "libreevolve.matrix_2x2_case_set.v1":
        raise ValueError("unsupported matrix case-set schema")
    if payload.get("id") != case_set_id:
        raise ValueError("matrix case-set id mismatch")
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("matrix case set must contain cases")
    cases: list[tuple[list, list]] = []
    for item in raw_cases:
        if not isinstance(item, dict) or not _is_2x2_matrix(item.get("a")) or not _is_2x2_matrix(item.get("b")):
            raise ValueError("matrix case entries must contain 2x2 matrices")
        cases.append((item["a"], item["b"]))
    return case_set_id, cases, seed


def _is_2x2_matrix(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(row, list) and len(row) == 2 for row in value)
        and all(
            isinstance(item, (int, float)) and not isinstance(item, bool)
            for row in value
            for item in row
        )
    )


def _seed_ordered_cases(
    cases: list[tuple[list, list]], seed: int | None
) -> list[tuple[list, list]]:
    if seed is None:
        return cases
    offset = seed % len(cases)
    return cases[offset:] + cases[:offset]


def _find_matmul2_function(tree: ast.AST) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "matmul2":
            return node
    return None


def _has_forbidden_constructs(tree: ast.AST) -> bool:
    forbidden_calls = {"__import__", "eval", "exec", "compile", "open"}
    forbidden_modules = {"numpy", "np", "torch", "jax"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in forbidden_calls:
                return True
        if isinstance(node, ast.Name) and node.id in forbidden_modules:
            return True
    return False


def _multiplication_count(tree: ast.AST) -> int:
    return sum(isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult) for node in ast.walk(tree))


def _expected(a, b):
    return [
        [
            a[0][0] * b[0][0] + a[0][1] * b[1][0],
            a[0][0] * b[0][1] + a[0][1] * b[1][1],
        ],
        [
            a[1][0] * b[0][0] + a[1][1] * b[1][0],
            a[1][0] * b[0][1] + a[1][1] * b[1][1],
        ],
    ]


def _invalid(count: int = 0) -> dict:
    return {
        "inverse_multiplications": 0.0,
        "multiplication_count": count,
        "is_valid": False,
    }
