def evaluate(code: str) -> dict:
    """Evaluates whether code defines greet(name) -> 'Hello, {name}!'"""
    ns = {}
    try:
        compiled = compile(code, "<string>", "exec")
        exec(compiled, ns)
    except Exception:
        return {"score": 0.0, "is_valid": False}
    greet = ns.get("greet")
    if not callable(greet):
        return {"score": 0.0, "is_valid": False}
    tests = [("World", "Hello, World!"), ("Alice", "Hello, Alice!"), ("Bob", "Hello, Bob!")]
    passed = sum(1 for n, e in tests if _safe(greet, n) == e)
    return {"score": passed / len(tests), "is_valid": passed == len(tests)}

def _safe(fn, arg):
    try: return fn(arg)
    except Exception: return None
