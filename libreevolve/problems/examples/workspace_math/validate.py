from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


def _load_helper_base_value(helper_path: Path):
    spec = importlib.util.spec_from_file_location("candidate_helpers_contract", helper_path)
    if spec is None or spec.loader is None:
        raise ValueError("helpers.py is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    base_value = getattr(module, "base_value", None)
    if not callable(base_value):
        raise ValueError("helpers.py must expose base_value()")
    return base_value()


def _run_main_with_helper(main_path: Path, workspace: Path, helper_value):
    fake_helpers = types.ModuleType("helpers")
    fake_helpers.base_value = lambda: helper_value
    sentinel = object()
    previous = sys.modules.get("helpers", sentinel)
    sys.modules["helpers"] = fake_helpers

    inserted = False
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
        inserted = True
    try:
        spec = importlib.util.spec_from_file_location("candidate_main", main_path)
        if spec is None or spec.loader is None:
            raise ValueError("main.py is not importable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        solve = getattr(module, "solve", None)
        if not callable(solve):
            raise ValueError("main.py must expose solve()")
        return solve()
    finally:
        if previous is sentinel:
            sys.modules.pop("helpers", None)
        else:
            sys.modules["helpers"] = previous
        if inserted:
            try:
                sys.path.remove(str(workspace))
            except ValueError:
                pass


def evaluate(code: str, workspace_path: str) -> dict:
    workspace = Path(workspace_path)
    main_path = workspace / "main.py"
    helper_path = workspace / "helpers.py"
    if not main_path.exists() or not helper_path.exists():
        return {"score": 0.0, "is_valid": False}

    try:
        base = _load_helper_base_value(helper_path)
        result = _run_main_with_helper(main_path, workspace, base)
        perturbed = _run_main_with_helper(main_path, workspace, base + 1)
    except Exception:
        return {"score": 0.0, "is_valid": False}

    ok = (
        type(result) is int
        and type(perturbed) is int
        and result == 42
        and perturbed == 43
    )
    return {"score": 1.0 if ok else 0.0, "is_valid": ok}
