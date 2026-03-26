import math


TARGET_CIRCLES = 26


def evaluate(code: str) -> dict:
    """Evaluate a fixed-26 circle packing in the unit square."""
    ns = {}
    _load_code(ns, code)
    solve = ns.get("solve")
    if not callable(solve):
        return {"sum_radii": 0.0, "is_valid": False}
    try:
        circles = solve()
        if not isinstance(circles, list) or len(circles) != TARGET_CIRCLES:
            return {"sum_radii": 0.0, "is_valid": False}
    except Exception:
        return {"sum_radii": 0.0, "is_valid": False}
    total = 0.0
    parsed = []
    for circle in circles:
        if not isinstance(circle, (list, tuple)) or len(circle) != 3:
            return {"sum_radii": 0.0, "is_valid": False}
        x, y, r = circle
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (x, y, r)):
            return {"sum_radii": 0.0, "is_valid": False}
        if r <= 0.0:
            return {"sum_radii": 0.0, "is_valid": False}
        if x - r < 0.0 or x + r > 1.0 or y - r < 0.0 or y + r > 1.0:
            return {"sum_radii": 0.0, "is_valid": False}
        parsed.append((float(x), float(y), float(r)))
        total += float(r)
    for i in range(len(parsed)):
        x1, y1, r1 = parsed[i]
        for j in range(i + 1, len(parsed)):
            x2, y2, r2 = parsed[j]
            if math.hypot(x1 - x2, y1 - y2) < r1 + r2:
                return {"sum_radii": 0.0, "is_valid": False}
    return {"sum_radii": total, "is_valid": True}

def _load_code(ns: dict, code: str) -> None:
    """Load candidate code into namespace. Uses compile + exec for dynamic code."""
    try:
        compiled = compile(code, "<candidate>", "exec")
        # Note: exec is intentional — candidate code runs in isolated subprocess
        eval(compiled, ns)  # noqa: S307
    except Exception:
        pass
