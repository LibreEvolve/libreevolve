import math

def evaluate(code: str) -> dict:
    """Evaluates circle packing solution. Runs in isolated subprocess."""
    ns = {}
    _load_code(ns, code)
    solve = ns.get("solve")
    if not callable(solve):
        return {"n_circles": 0.0, "is_valid": False}
    try:
        circles = solve()
        if not isinstance(circles, list) or not circles:
            return {"n_circles": 0.0, "is_valid": False}
    except Exception:
        return {"n_circles": 0.0, "is_valid": False}
    for x, y in circles:
        if not (1.0 <= x <= 9.0 and 1.0 <= y <= 9.0):
            return {"n_circles": 0.0, "is_valid": False}
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            if math.hypot(circles[i][0]-circles[j][0], circles[i][1]-circles[j][1]) < 2.0:
                return {"n_circles": 0.0, "is_valid": False}
    return {"n_circles": float(len(circles)), "is_valid": True}

def _load_code(ns: dict, code: str) -> None:
    """Load candidate code into namespace. Uses compile + exec for dynamic code."""
    try:
        compiled = compile(code, "<candidate>", "exec")
        # Note: exec is intentional — candidate code runs in isolated subprocess
        eval(compiled, ns)  # noqa: S307
    except Exception:
        pass
