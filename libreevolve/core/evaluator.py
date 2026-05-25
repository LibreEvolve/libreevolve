from __future__ import annotations
import json, math, sys, tempfile
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.problems.loader import Problem

_PENALTIES = {"no_diff_blocks": -0.4, "no_valid_changes": -0.3, "search_not_found": -0.3}

# Runner script executed in a temporary local subprocess. This is process
# separation, not a security sandbox.
# Uses importlib to load validate.py and calls evaluate(code) -> prints json.dumps(result)
_RUNNER = (
    "import sys,json,importlib.util,inspect,os\n"
    "workspace=sys.argv[3]\n"
    "validate_dir=os.path.dirname(os.path.abspath(sys.argv[1]))\n"
    "for path in (validate_dir, workspace):\n"
    "    if path and path not in sys.path: sys.path.insert(0,path)\n"
    "os.chdir(workspace)\n"
    "spec=importlib.util.spec_from_file_location('v',sys.argv[1])\n"
    "mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)\n"
    "code=open(sys.argv[2],encoding='utf-8').read()\n"
    "stage=json.loads(sys.argv[4])\n"
    "params=inspect.signature(mod.evaluate).parameters\n"
    "result=mod.evaluate(code, workspace, stage) if len(params) >= 3 else (mod.evaluate(code, workspace) if len(params) >= 2 else mod.evaluate(code))\n"
    "print(json.dumps(result))\n"
)


class CascadeEvaluator:
    """Tier 0 (diff penalty) -> Tier 1 (syntax) -> Tier 2 (subprocess).

    Inspired by staged evaluation and lazy-penalty ideas in adjacent systems.
    This local implementation is not a reproduction of those papers.
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
            result = self._run_stage(workspace, stage, stage_index=index, stage_name=name)
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
                    metadata={**result.metadata, "stopped_at": name},
                )
        assert last is not None
        last.stages = stages
        last.elapsed_sec = sum(s.elapsed_sec for s in stages)
        return last

    def _run_stage(
        self,
        workspace: CandidateWorkspace,
        stage: dict,
        stage_index: int,
        stage_name: str,
    ) -> "EvaluationResult":
        timeout = float(stage.get("timeout_sec", self._timeout))
        validate_path = self._resolve_validate_path(stage.get("validate_path"))
        seeds = list(stage.get("seeds", []))
        samples = int(stage.get("samples", len(seeds) or 1))
        retries = int(stage.get("retries", 0))
        results: list[EvaluationResult] = []
        for sample_index in range(samples):
            seed = seeds[sample_index] if sample_index < len(seeds) else None
            context = {
                "name": stage_name,
                "stage_index": stage_index,
                "sample_index": sample_index,
                "seed": seed,
                "config": stage,
            }
            result = self._run_sample_with_retries(
                workspace=workspace,
                validate_path=validate_path,
                stage_name=f"{stage_name}[{sample_index}]" if samples > 1 else stage_name,
                timeout_sec=timeout,
                stage_context=context,
                retries=retries,
            )
            results.append(result)
        if len(results) == 1:
            return results[0]
        return self._aggregate_sample_results(stage_name, results, validate_path)

    def _run_sample_with_retries(
        self,
        workspace: CandidateWorkspace,
        validate_path: Path,
        stage_name: str,
        timeout_sec: float,
        stage_context: dict,
        retries: int,
    ) -> "EvaluationResult":
        last: EvaluationResult | None = None
        attempts: list[dict] = []
        for attempt in range(retries + 1):
            context = dict(stage_context)
            context["attempt"] = attempt
            result = self._run_subprocess(
                workspace=workspace,
                stage_name=stage_name,
                timeout_sec=timeout_sec,
                validate_path=validate_path,
                stage_context=context,
            )
            result.metadata["attempt"] = attempt
            attempts.append(_retry_attempt_record(result, attempt, context))
            last = result
            if result.is_valid:
                result.metadata["attempts"] = attempts
                result.metadata["attempt_count"] = len(attempts)
                return result
        assert last is not None
        last.metadata["attempts"] = attempts
        last.metadata["attempt_count"] = len(attempts)
        return last

    def _run_subprocess(
        self,
        workspace: CandidateWorkspace,
        stage_name: str,
        timeout_sec: float,
        validate_path: Path | None = None,
        stage_context: dict | None = None,
    ) -> "EvaluationResult":
        validate_path = validate_path or self._problem.validate_path
        stage_context = stage_context or {"name": stage_name}
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
                     str(validate_path), str(primary), str(cand_root),
                     json.dumps(stage_context)],
                    cwd=str(cand_root),
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
                    metadata=_eval_metadata(workspace, validate_path, stage_context),
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
                    metadata=_eval_metadata(workspace, validate_path, stage_context),
                )
            try:
                lines = [line for line in res.stdout.splitlines() if line.strip()]
                m = _validate_metrics(
                    json.loads(lines[-1] if lines else ""), self._problem
                )
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
                        metadata=_eval_metadata(workspace, validate_path, stage_context),
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
                    metadata=_eval_metadata(workspace, validate_path, stage_context),
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
                    metadata=_eval_metadata(workspace, validate_path, stage_context),
                )

    def _resolve_validate_path(self, raw: object) -> Path:
        if raw is None:
            return self._problem.validate_path
        path = Path(str(raw))
        if not path.is_absolute():
            path = self._problem.problem_dir / path
        return path

    def _aggregate_sample_results(
        self, stage_name: str, results: list["EvaluationResult"], validate_path: Path
    ) -> "EvaluationResult":
        valid = all(r.is_valid for r in results)
        metrics = _aggregate_metrics([r.metrics for r in results])
        if self._problem.primary_metric in metrics:
            fitness = self._problem.fitness_from_metrics(metrics)
        else:
            fitness = sum(r.fitness for r in results) / len(results)
        if not valid:
            fitness = min(r.fitness for r in results)
            metrics.setdefault(self._problem.primary_metric, fitness)
            metrics["is_valid"] = False
        stages = [stage for result in results for stage in result.stages]
        return EvaluationResult(
            fitness=fitness,
            metrics=metrics,
            is_valid=valid,
            stages=stages,
            stdout="\n".join(r.stdout for r in results if r.stdout),
            stderr="\n".join(r.stderr for r in results if r.stderr),
            error=None if valid else next((r.error for r in results if r.error), "sample_invalid"),
            elapsed_sec=sum(r.elapsed_sec for r in results),
            metadata={
                "stage": stage_name,
                "sample_count": len(results),
                "validate_path": str(validate_path),
                "samples": [r.to_dict() for r in results],
            },
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


def _eval_metadata(
    workspace: CandidateWorkspace, validate_path: Path, stage_context: dict
) -> dict:
    return {
        "primary_file": workspace.primary_file,
        "files": sorted(workspace.files),
        "validate_path": str(validate_path),
        "stage": stage_context,
    }


def _retry_attempt_record(result: EvaluationResult, attempt: int, context: dict) -> dict:
    return {
        "attempt": attempt,
        "passed": result.is_valid,
        "fitness": result.fitness,
        "metrics": dict(result.metrics),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "error": result.error,
        "elapsed_sec": result.elapsed_sec,
        "stage": dict(context),
        "stages": [stage.to_dict() for stage in result.stages],
    }


def _validate_metrics(raw: object, problem: Problem) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("evaluator output must be a metrics dictionary")
    metrics = dict(raw)
    declared = {str(metric["name"]) for metric in problem.metrics}
    declared.add("is_valid")
    missing = sorted(declared - set(metrics))
    if missing:
        raise ValueError(f"evaluator output missing declared metrics: {missing}")
    undeclared = sorted(set(metrics) - declared)
    if undeclared:
        raise ValueError(f"evaluator output included undeclared metrics: {undeclared}")
    if not isinstance(metrics.get("is_valid"), bool):
        raise ValueError("evaluator output metric 'is_valid' must be boolean")
    for name in sorted(declared - {"is_valid"}):
        value = metrics[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"evaluator output metric {name!r} must be numeric")
        if not math.isfinite(float(value)):
            raise ValueError(f"evaluator output metric {name!r} must be finite")
        metrics[name] = float(value)
    return metrics


def _aggregate_metrics(metrics_list: list[dict]) -> dict:
    if not metrics_list:
        return {}
    keys = sorted({key for metrics in metrics_list for key in metrics})
    result: dict = {}
    for key in keys:
        values = [metrics[key] for metrics in metrics_list if key in metrics]
        if values and all(isinstance(v, bool) for v in values):
            result[key] = all(values)
        elif values and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
            result[key] = sum(float(v) for v in values) / len(values)
        elif values:
            result[key] = values[-1]
    if "is_valid" in result:
        result["is_valid"] = bool(result["is_valid"])
    return result
