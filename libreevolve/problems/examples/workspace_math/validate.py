from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path


def _load_helper_base_value(helper_path: Path):
    spec = importlib.util.spec_from_file_location(
        "candidate_pkg_helpers_contract",
        helper_path,
    )
    if spec is None or spec.loader is None:
        raise ValueError("pkg/helpers.py is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    base_value = getattr(module, "base_value", None)
    if not callable(base_value):
        raise ValueError("pkg/helpers.py must expose base_value()")
    return base_value()


def _run_main_with_helper(main_path: Path, workspace: Path, helper_value):
    fake_pkg = types.ModuleType("pkg")
    fake_pkg.__path__ = [str(workspace / "pkg")]
    fake_helpers = types.ModuleType("pkg.helpers")
    fake_helpers.base_value = lambda: helper_value
    sentinel = object()
    previous_pkg = sys.modules.get("pkg", sentinel)
    previous_helpers = sys.modules.get("pkg.helpers", sentinel)
    sys.modules["pkg"] = fake_pkg
    sys.modules["pkg.helpers"] = fake_helpers

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
        if previous_helpers is sentinel:
            sys.modules.pop("pkg.helpers", None)
        else:
            sys.modules["pkg.helpers"] = previous_helpers
        if previous_pkg is sentinel:
            sys.modules.pop("pkg", None)
        else:
            sys.modules["pkg"] = previous_pkg
        if inserted:
            try:
                sys.path.remove(str(workspace))
            except ValueError:
                pass


def evaluate(code: str, workspace_path: str) -> dict:
    workspace = Path(workspace_path)
    main_path = workspace / "main.py"
    helper_path = workspace / "pkg" / "helpers.py"
    config_path = workspace / "data" / "config.json"
    asset_path = workspace / "assets" / "offset.bin"
    if not (
        main_path.exists()
        and helper_path.exists()
        and config_path.exists()
        and asset_path.exists()
    ):
        return {"score": 0.0, "is_valid": False}

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if config.get("label") != "workspace_math":
            return {"score": 0.0, "is_valid": False}
        if asset_path.read_bytes() != b"\xffLESTATIC\n":
            return {"score": 0.0, "is_valid": False}
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
