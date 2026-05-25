from __future__ import annotations
import json, sys, tempfile
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.problems.loader import Problem

_PENALTIES = {"no_diff_blocks": -0.4, "no_valid_changes": -0.3, "search_not_found": -0.3}

# Runner script executed in isolated subprocess.
# Uses importlib to load validate.py and calls evaluate(code) -> prints json.dumps(result)
_RUNNER = (
    "import sys,json,importlib.util,inspect\n"
    "spec=importlib.util.spec_from_file_location('v',sys.argv[1])\n"
    "mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)\n"
    "code=open(sys.argv[2],encoding='utf-8').read()\n"
    "workspace=sys.argv[3]\n"
    "params=inspect.signature(mod.evaluate).parameters\n"
    "result=mod.evaluate(code, workspace) if len(params) >= 2 else mod.evaluate(code)\n"
    "print(json.dumps(result))\n"
)


class CascadeEvaluator:
    """Tier 0 (diff penalty) -> Tier 1 (syntax) -> Tier 2 (subprocess).

    Sources: cascade eval from ArchAgent (arXiv:2602.22425) and Magellan
    (arXiv:2601.21096), lazy penalty system from ThetaEvolve (arXiv:2511.23473).
    """

    def __init__(
        self,
        problem: Problem,
        timeout_sec: float = 60.0,
        stages: list[dict] | None = None,
    ):
        self._problem = problem
        self._timeout = timeout_sec
        self._stages = stages or []

    def evaluate(
        self, code: str | CandidateWorkspace, diff_error: str | None
    ) -> "EvaluationResult":
        workspace = code if isinstance(code, CandidateWorkspace) else CandidateWorkspace.from_code(code)
        if diff_error is not None:
            score = _PENALTIES.get(diff_error, -0.4)
            return EvaluationResult(
                fitness=score,
                metrics={self._problem.primary_metric: score, "is_valid": False},
                is_valid=False,
                stages=[
                    EvaluationStageResult(
                        name="diff",
                        passed=False,
                        score=score,
                        error=diff_error,
                    )
                ],
                error=diff_error,
                metadata={"primary_file": workspace.primary_file, "files": sorted(workspace.files)},
            )
        syntax_error = _syntax_error(workspace)
        if syntax_error is not None:
            return EvaluationResult(
                fitness=-0.2,
                metrics={self._problem.primary_metric: -0.2, "is_valid": False},
                is_valid=False,
                stages=[
                    EvaluationStageResult(
                        name="syntax",
                        passed=False,
                        score=-0.2,
                        error=syntax_error,
                    )
                ],
                error="syntax_error",
                metadata={"primary_file": workspace.primary_file, "files": sorted(workspace.files)},
            )
        syntax_stage = EvaluationStageResult(name="syntax", passed=True)
        if self._stages:
            return self._run_configured_stages(workspace, syntax_stage)
        result = self._run_subprocess(workspace, stage_name="validate", timeout_sec=self._timeout)
        result.stages.insert(0, syntax_stage)
        return result

    def _run_configured_stages(
        self, workspace: CandidateWorkspace, syntax_stage: "EvaluationStageResult"
    ) -> "EvaluationResult":
        stages = [syntax_stage]
        last: EvaluationResult | None = None
        for index, stage in enumerate(self._stages):
            name = str(stage.get("name", f"stage_{index}"))
            timeout = float(stage.get("timeout_sec", self._timeout))
            result = self._run_subprocess(workspace, stage_name=name, timeout_sec=timeout)
            stages.extend(result.stages)
            last = result
            min_score = stage.get("min_score")
            if not result.is_valid or (min_score is not None and result.fitness < float(min_score)):
                return EvaluationResult(
                    fitness=result.fitness,
                    metrics=result.metrics,
                    is_valid=False,
                    stages=stages,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    error=result.error or "stage_threshold_not_met",
                    elapsed_sec=sum(s.elapsed_sec for s in stages),
                    metadata={"stopped_at": name},
                )
        assert last is not None
        last.stages = stages
        last.elapsed_sec = sum(s.elapsed_sec for s in stages)
        return last

    def _run_subprocess(
        self, workspace: CandidateWorkspace, stage_name: str, timeout_sec: float
    ) -> "EvaluationResult":
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner = tmp_path / "_runner.py"
            cand_root = tmp_path / "candidate"
            runner.write_text(_RUNNER, encoding="utf-8")
            primary = workspace.materialize(cand_root)
            started = time.perf_counter()
            try:
                # Use list form (not shell=True) to prevent injection
                res = subprocess.run(
                    [sys.executable, str(runner),
                     str(self._problem.validate_path), str(primary), str(cand_root)],
                    capture_output=True, timeout=timeout_sec, text=True,
                )
            except subprocess.TimeoutExpired:
                elapsed = time.perf_counter() - started
                return EvaluationResult(
                    fitness=-0.2,
                    metrics={self._problem.primary_metric: -0.2, "is_valid": False},
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            error="timeout",
                            elapsed_sec=elapsed,
                        )
                    ],
                    error="timeout",
                    elapsed_sec=elapsed,
                    metadata={"primary_file": workspace.primary_file, "files": sorted(workspace.files)},
                )
            elapsed = time.perf_counter() - started
            if res.returncode != 0:
                return EvaluationResult(
                    fitness=-0.2,
                    metrics={self._problem.primary_metric: -0.2, "is_valid": False},
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            stdout=res.stdout,
                            stderr=res.stderr,
                            error=f"returncode_{res.returncode}",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=res.stdout,
                    stderr=res.stderr,
                    error="subprocess_error",
                    elapsed_sec=elapsed,
                    metadata={"primary_file": workspace.primary_file, "files": sorted(workspace.files)},
                )
            try:
                lines = [line for line in res.stdout.splitlines() if line.strip()]
                m = json.loads(lines[-1] if lines else "")
                if not m.get("is_valid", False):
                    return EvaluationResult(
                        fitness=-0.1,
                        metrics=m,
                        is_valid=False,
                        stages=[
                            EvaluationStageResult(
                                name=stage_name,
                                passed=False,
                                score=-0.1,
                                metrics=m,
                                stdout=res.stdout,
                                stderr=res.stderr,
                                error="domain_invalid",
                                elapsed_sec=elapsed,
                            )
                        ],
                        stdout=res.stdout,
                        stderr=res.stderr,
                        error="domain_invalid",
                        elapsed_sec=elapsed,
                    )
                fitness = self._problem.fitness_from_metrics(m)
                return EvaluationResult(
                    fitness=fitness,
                    metrics=m,
                    is_valid=True,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=True,
                            score=fitness,
                            metrics=m,
                            stdout=res.stdout,
                            stderr=res.stderr,
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=res.stdout,
                    stderr=res.stderr,
                    elapsed_sec=elapsed,
                    metadata={"primary_file": workspace.primary_file, "files": sorted(workspace.files)},
                )
            except (json.JSONDecodeError, ValueError, KeyError, TypeError):
                return EvaluationResult(
                    fitness=-0.2,
                    metrics={self._problem.primary_metric: -0.2, "is_valid": False},
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            stdout=res.stdout,
                            stderr=res.stderr,
                            error="malformed_metrics",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=res.stdout,
                    stderr=res.stderr,
                    error="malformed_metrics",
                    elapsed_sec=elapsed,
                    metadata={"primary_file": workspace.primary_file, "files": sorted(workspace.files)},
                )


@dataclass
class EvaluationStageResult:
    name: str
    passed: bool
    score: float | None = None
    metrics: dict = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    elapsed_sec: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "score": self.score,
            "metrics": self.metrics,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "elapsed_sec": self.elapsed_sec,
        }


@dataclass
class EvaluationResult:
    fitness: float
    metrics: dict
    is_valid: bool
    stages: list[EvaluationStageResult] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    elapsed_sec: float = 0.0
    metadata: dict = field(default_factory=dict)

    def __float__(self) -> float:
        return self.fitness

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (int, float)):
            return self.fitness == float(other)
        return super().__eq__(other)

    def __sub__(self, other: object) -> float:
        if isinstance(other, (int, float)):
            return self.fitness - float(other)
        return NotImplemented

    def __rsub__(self, other: object) -> float:
        if isinstance(other, (int, float)):
            return float(other) - self.fitness
        return NotImplemented

    def to_dict(self) -> dict:
        return {
            "fitness": self.fitness,
            "metrics": self.metrics,
            "is_valid": self.is_valid,
            "stages": [stage.to_dict() for stage in self.stages],
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "elapsed_sec": self.elapsed_sec,
            "metadata": self.metadata,
        }


def _syntax_error(workspace: CandidateWorkspace) -> str | None:
    for rel_path, content in sorted(workspace.files.items()):
        if not rel_path.endswith(".py"):
            continue
        try:
            compile(content, rel_path, "exec")
        except SyntaxError as exc:
            return f"{rel_path}: {exc.__class__.__name__}: {exc}"
    return None
