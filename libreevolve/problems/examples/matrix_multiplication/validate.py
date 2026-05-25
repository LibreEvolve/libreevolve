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
]


def evaluate(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _invalid()
    count = _multiplication_count(tree)
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
