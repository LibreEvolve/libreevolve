import random

def evaluate(code: str) -> dict:
    """Evaluate sorting solution."""
    ns = {}
    _load_code(ns, code)
    sort_list = ns.get("sort_list")
    if not callable(sort_list):
        return {"accuracy": 0.0, "is_valid": False}
    random.seed(42)
    cases = [[], [1], [3,1,2], [5,3,1,4,2], [-3,0,5,-1,2], [1,1,1,2,1],
             list(range(10,0,-1)), [random.randint(-100,100) for _ in range(20)]]
    passed = 0
    for tc in cases:
        result = _safe(sort_list, list(tc))
        if type(result) is list and result == sorted(tc):
            passed += 1
    acc = passed / len(cases)
    return {"accuracy": acc, "is_valid": acc == 1.0}

def _safe(fn, arg):
    try: return fn(arg)
    except Exception: return None

def _load_code(ns: dict, code: str) -> None:
    """Load candidate code into namespace. Uses compile + eval for dynamic code."""
    try:
        compiled = compile(code, "<candidate>", "exec")
        # Note: eval is intentional; the evaluator calls this in a subprocess.
        eval(compiled, ns)  # noqa: S307
    except Exception:
        pass
