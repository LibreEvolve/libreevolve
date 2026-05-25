from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def evaluate(code: str, workspace_path: str) -> dict:
    workspace = Path(workspace_path)
    main_path = workspace / "main.py"
    helper_path = workspace / "helpers.py"
    if not main_path.exists() or not helper_path.exists():
        return {"score": 0.0, "is_valid": False}

    inserted = False
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
        inserted = True
    try:
        spec = importlib.util.spec_from_file_location("candidate_main", main_path)
        if spec is None or spec.loader is None:
            return {"score": 0.0, "is_valid": False}
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        solve = getattr(module, "solve", None)
        if not callable(solve):
            return {"score": 0.0, "is_valid": False}
        result = solve()
    except Exception:
        return {"score": 0.0, "is_valid": False}
    finally:
        if inserted:
            try:
                sys.path.remove(str(workspace))
            except ValueError:
                pass

    ok = result == 42
    return {"score": 1.0 if ok else 0.0, "is_valid": ok}
