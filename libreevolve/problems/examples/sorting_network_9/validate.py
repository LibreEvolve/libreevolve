import ast
from itertools import product


WIRE_COUNT = 9
TARGET_COMPARATORS = 25
MAX_COMPARATORS = 81
TOTAL_BINARY_INPUTS = 2 ** WIRE_COUNT


def evaluate(code: str) -> dict:
    """Evaluate a 9-input sorting network by exhaustive binary-input checks."""

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _invalid()
    if _has_forbidden_constructs(tree):
        return _invalid()
    ns = {}
    try:
        exec(compile(tree, "<candidate>", "exec"), ns)  # noqa: S102
    except Exception:
        return _invalid()
    network = ns.get("network")
    if not callable(network):
        return _invalid()
    try:
        raw_comparators = network()
    except Exception:
        return _invalid()
    comparators = _normalize_comparators(raw_comparators)
    if comparators is None:
        return _invalid()
    count = len(comparators)
    if count > MAX_COMPARATORS:
        return _metrics(0, count, _network_depth(comparators), False)
    sorted_count = 0
    for values in product((0, 1), repeat=WIRE_COUNT):
        result = _apply_network(values, comparators)
        if result == tuple(sorted(values)):
            sorted_count += 1
    valid = sorted_count == TOTAL_BINARY_INPUTS
    return _metrics(sorted_count, count, _network_depth(comparators), valid)


def _has_forbidden_constructs(tree: ast.AST) -> bool:
    forbidden_calls = {"__import__", "eval", "exec", "compile", "open"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in forbidden_calls:
                return True
    return False


def _normalize_comparators(raw_comparators):
    if type(raw_comparators) is not list:
        return None
    normalized = []
    for item in raw_comparators:
        if type(item) not in (tuple, list) or len(item) != 2:
            return None
        left, right = item
        if type(left) is not int or type(right) is not int:
            return None
        if left == right:
            return None
        if not (0 <= left < WIRE_COUNT and 0 <= right < WIRE_COUNT):
            return None
        normalized.append((min(left, right), max(left, right)))
    return normalized


def _apply_network(values, comparators):
    wires = list(values)
    for left, right in comparators:
        if wires[left] > wires[right]:
            wires[left], wires[right] = wires[right], wires[left]
    return tuple(wires)


def _network_depth(comparators) -> int:
    last_layer_by_wire = [0] * WIRE_COUNT
    max_layer = 0
    for left, right in comparators:
        layer = max(last_layer_by_wire[left], last_layer_by_wire[right]) + 1
        last_layer_by_wire[left] = layer
        last_layer_by_wire[right] = layer
        max_layer = max(max_layer, layer)
    return max_layer


def _metrics(sorted_count: int, comparator_count: int, depth: int, valid: bool) -> dict:
    coverage = sorted_count / TOTAL_BINARY_INPUTS
    inverse_count = 1.0 / comparator_count if comparator_count > 0 else 0.0
    count_quality = max(0.0, 1.0 - min(comparator_count, MAX_COMPARATORS) / MAX_COMPARATORS)
    target = valid and comparator_count <= TARGET_COMPARATORS
    network_score = 0.9 * coverage + 0.1 * count_quality
    return {
        "network_score": network_score,
        "sorted_input_coverage": coverage,
        "inverse_comparator_count": inverse_count,
        "comparator_count": comparator_count,
        "depth": depth,
        "target_achieved": 1.0 if target else 0.0,
        "is_valid": valid,
    }


def _invalid() -> dict:
    return {
        "network_score": 0.0,
        "sorted_input_coverage": 0.0,
        "inverse_comparator_count": 0.0,
        "comparator_count": 0,
        "depth": 0,
        "target_achieved": 0.0,
        "is_valid": False,
    }
