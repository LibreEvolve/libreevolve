from __future__ import annotations
import json, sys, tempfile
import subprocess
from pathlib import Path
from libreevolve.problems.loader import Problem

_PENALTIES = {"no_diff_blocks": -0.4, "no_valid_changes": -0.3, "search_not_found": -0.3}

# Runner script executed in isolated subprocess.
# Uses importlib to load validate.py and calls evaluate(code) -> prints json.dumps(result)
_RUNNER = (
    "import sys,json,importlib.util\n"
    "spec=importlib.util.spec_from_file_location('v',sys.argv[1])\n"
    "mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)\n"
    "code=open(sys.argv[2],encoding='utf-8').read()\n"
    "print(json.dumps(mod.evaluate(code)))\n"
)


class CascadeEvaluator:
    """Tier 0 (diff penalty) -> Tier 1 (syntax) -> Tier 2 (subprocess).

    Sources: cascade eval from ArchAgent (arXiv:2602.22425) and Magellan
    (arXiv:2601.21096), lazy penalty system from ThetaEvolve (arXiv:2511.23473).
    """

    def __init__(self, problem: Problem, timeout_sec: float = 60.0):
        self._problem = problem
        self._timeout = timeout_sec

    def evaluate(self, code: str, diff_error: str | None) -> float:
        if diff_error is not None:
            return _PENALTIES.get(diff_error, -0.4)
        try:
            compile(code, "<string>", "exec")
        except SyntaxError:
            return -0.2
        return self._run_subprocess(code)

    def _run_subprocess(self, code: str) -> float:
        with tempfile.TemporaryDirectory() as tmp:
            runner = Path(tmp) / "_runner.py"
            cand   = Path(tmp) / "_cand.py"
            runner.write_text(_RUNNER, encoding="utf-8")
            cand.write_text(code, encoding="utf-8")
            try:
                # Use list form (not shell=True) to prevent injection
                res = subprocess.run(
                    [sys.executable, str(runner),
                     str(self._problem.validate_path), str(cand)],
                    capture_output=True, timeout=self._timeout, text=True,
                )
            except subprocess.TimeoutExpired:
                return -0.2
            if res.returncode != 0:
                return -0.2
            try:
                m = json.loads(res.stdout.strip())
                if not m.get("is_valid", False):
                    return -0.1
                return float(m[self._problem.primary_metric])
            except (json.JSONDecodeError, ValueError, KeyError, TypeError):
                return -0.2
