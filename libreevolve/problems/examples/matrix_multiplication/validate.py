import ast
import math


CASES = [
    (
        [[1, 2], [3, 4]],
        [[5, 6], [7, 8]],
    ),
    (
        [[0, -1], [2, 3]],
        [[4, 5], [-6, 7]],
    ),
    (
        [[2, 0], [0, 2]],
        [[-1, 3], [4, -5]],
    ),
    (
        [[-3, 5], [7, -11]],
        [[13, -17], [19, 23]],
    ),
    (
        [[6, -2], [9, 4]],
        [[-8, 1], [3, -7]],
    ),
]


def evaluate(code: str) -> dict:
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
        for a, b in CASES:
            got = fn(a, b)
            if got != _expected(a, b):
                return _invalid(count)
    except Exception:
        return _invalid(count)
    return {
        "inverse_multiplications": 1.0 / count,
        "multiplication_count": count,
        "is_valid": True,
    }


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
