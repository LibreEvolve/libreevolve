from __future__ import annotations
import hashlib
import json, math, sys, tempfile
import os
import re
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
import fnmatch
import shutil
from uuid import uuid4
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.problems.loader import Problem

_PENALTIES = {"no_diff_blocks": -0.4, "no_valid_changes": -0.3, "search_not_found": -0.3}
_DEFAULT_VALIDATOR_ENV_NAMES = ("SYSTEMROOT", "WINDIR", "TEMP", "TMP")
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(api[_-]?key|token|secret|password)(\s*[:=]\s*)(['\"]?)[^\s,'\"]+"
)
_SECRET_TOKEN = re.compile(r"\b(?:sk|sk-proj|ghp|gho|github_pat)_[A-Za-z0-9_\-]{12,}\b")

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
        validator_env_allowlist: list[str] | None = None,
        artifact_dir: Path | None = None,
        artifact_include: list[str] | None = None,
        artifact_exclude: list[str] | None = None,
        artifact_max_files: int = 20,
        artifact_max_bytes: int = 1_000_000,
    ):
        self._problem = problem
        self._timeout = timeout_sec
        self._stages = stages or []
        self._validator_env_allowlist = list(validator_env_allowlist or [])
        self._artifact_dir = artifact_dir
        self._artifact_include = list(artifact_include or [])
        self._artifact_exclude = list(artifact_exclude or [])
        self._artifact_max_files = artifact_max_files
        self._artifact_max_bytes = artifact_max_bytes

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
        syntax_errors = _syntax_errors(workspace)
        if syntax_errors:
            syntax_error = "; ".join(error["summary"] for error in syntax_errors)
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
                metadata={
                    "primary_file": workspace.primary_file,
                    "files": sorted(workspace.files),
                    "syntax_errors": syntax_errors,
                },
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
        artifact_policy = self._artifact_policy(stage)
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
                artifact_policy=artifact_policy,
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
        artifact_policy: dict,
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
                artifact_policy=artifact_policy,
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
        artifact_policy: dict | None = None,
    ) -> "EvaluationResult":
        validate_path = validate_path or self._problem.validate_path
        stage_context = stage_context or {"name": stage_name}
        artifact_policy = artifact_policy or self._artifact_policy({})
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner = tmp_path / "_runner.py"
            cand_root = tmp_path / "candidate"
            runner.write_text(_RUNNER, encoding="utf-8")
            primary = workspace.materialize(cand_root)
            validator_env = _validator_env(self._validator_env_allowlist)
            validator_env_meta = _validator_env_metadata(
                validator_env, self._validator_env_allowlist
            )
            started = time.perf_counter()
            # Use list form (not shell=True) to prevent injection.
            res = _run_validator_process(
                [sys.executable, str(runner),
                 str(validate_path), str(primary), str(cand_root),
                 json.dumps(stage_context)],
                cwd=cand_root,
                timeout_sec=timeout_sec,
                env=validator_env,
            )
            stdout = _redact_secrets(res.stdout)
            stderr = _redact_secrets(res.stderr)
            artifact_metadata = _collect_evaluator_artifacts(
                cand_root,
                artifact_policy["dir"],
                include=artifact_policy["include"],
                exclude=artifact_policy["exclude"],
                max_files=artifact_policy["max_files"],
                max_bytes=artifact_policy["max_bytes"],
                stage_context=stage_context,
            )
            if res.timed_out:
                elapsed = time.perf_counter() - started
                metadata = _eval_metadata(
                    workspace, validate_path, stage_context, validator_env_meta
                )
                metadata["timeout_cleanup"] = res.cleanup
                metadata["artifacts"] = artifact_metadata
                return EvaluationResult(
                    fitness=-0.2,
                    metrics={self._problem.primary_metric: -0.2, "is_valid": False},
                    is_valid=False,
                    stages=[
                        EvaluationStageResult(
                            name=stage_name,
                            passed=False,
                            score=-0.2,
                            stdout=stdout,
                            stderr=stderr,
                            error="timeout",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="timeout",
                    elapsed_sec=elapsed,
                    metadata=metadata,
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
                            stdout=stdout,
                            stderr=stderr,
                            error=f"returncode_{res.returncode}",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="subprocess_error",
                    elapsed_sec=elapsed,
                    metadata=_eval_metadata(
                        workspace,
                        validate_path,
                        stage_context,
                        validator_env_meta,
                        artifact_metadata,
                    ),
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
                                stdout=stdout,
                                stderr=stderr,
                                error="domain_invalid",
                                elapsed_sec=elapsed,
                            )
                        ],
                        stdout=stdout,
                        stderr=stderr,
                        error="domain_invalid",
                        elapsed_sec=elapsed,
                        metadata=_eval_metadata(
                            workspace,
                            validate_path,
                            stage_context,
                            validator_env_meta,
                            artifact_metadata,
                        ),
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
                            stdout=stdout,
                            stderr=stderr,
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    elapsed_sec=elapsed,
                    metadata=_eval_metadata(
                        workspace,
                        validate_path,
                        stage_context,
                        validator_env_meta,
                        artifact_metadata,
                    ),
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
                            stdout=stdout,
                            stderr=stderr,
                            error="malformed_metrics",
                            elapsed_sec=elapsed,
                        )
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    error="malformed_metrics",
                    elapsed_sec=elapsed,
                    metadata=_eval_metadata(
                        workspace,
                        validate_path,
                        stage_context,
                        validator_env_meta,
                        artifact_metadata,
                    ),
                )

    def _resolve_validate_path(self, raw: object) -> Path:
        if raw is None:
            path = self._problem.validate_path
        else:
            path = Path(str(raw))
            if not path.is_absolute():
                path = self._problem.problem_dir / path
        return _validate_problem_local_evaluator_path(path, self._problem.problem_dir)

    def _artifact_policy(self, stage: dict) -> dict:
        return {
            "dir": self._artifact_dir,
            "include": list(stage.get("artifact_include", self._artifact_include)),
            "exclude": list(stage.get("artifact_exclude", self._artifact_exclude)),
            "max_files": int(stage.get("artifact_max_files", self._artifact_max_files)),
            "max_bytes": int(stage.get("artifact_max_bytes", self._artifact_max_bytes)),
        }

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


@dataclass
class _ValidatorProcessResult:
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool = False
    cleanup: dict = field(default_factory=dict)


def _syntax_errors(workspace: CandidateWorkspace) -> list[dict]:
    errors: list[dict] = []
    for rel_path, content in sorted(workspace.files.items()):
        if not rel_path.endswith(".py"):
            continue
        try:
            compile(content, rel_path, "exec")
        except SyntaxError as exc:
            errors.append(
                {
                    "path": rel_path,
                    "line": exc.lineno,
                    "offset": exc.offset,
                    "message": exc.msg,
                    "summary": f"{rel_path}: {exc.__class__.__name__}: {exc}",
                }
            )
    return errors


def _run_validator_process(
    args: list[str],
    cwd: Path,
    timeout_sec: float,
    env: dict[str, str],
) -> _ValidatorProcessResult:
    kwargs = {
        "cwd": str(cwd),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "env": env,
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(args, **kwargs)
    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
        return _ValidatorProcessResult(proc.returncode, stdout or "", stderr or "")
    except subprocess.TimeoutExpired:
        cleanup = _terminate_process_tree(proc)
        try:
            stdout, stderr = proc.communicate(timeout=2.0)
        except subprocess.TimeoutExpired:
            cleanup["direct_kill_after_tree_timeout"] = True
            proc.kill()
            stdout, stderr = proc.communicate(timeout=2.0)
        return _ValidatorProcessResult(
            proc.returncode,
            stdout or "",
            stderr or "",
            timed_out=True,
            cleanup=cleanup,
        )


def _terminate_process_tree(proc: subprocess.Popen) -> dict:
    result = {"pid": proc.pid, "attempted": True}
    if proc.poll() is not None:
        result.update({"method": "already_exited", "returncode": proc.returncode})
        return result
    if os.name == "nt":
        result["method"] = "taskkill"
        try:
            completed = subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )
            result.update(
                {
                    "returncode": completed.returncode,
                    "stdout": _redact_secrets(completed.stdout),
                    "stderr": _redact_secrets(completed.stderr),
                }
            )
        except (FileNotFoundError, subprocess.SubprocessError) as exc:
            result.update({"fallback": "kill", "error": f"{exc.__class__.__name__}: {exc}"})
            proc.kill()
    else:
        result["method"] = "killpg"
        try:
            os.killpg(proc.pid, signal.SIGKILL)
            result["returncode"] = 0
        except ProcessLookupError:
            result.update({"returncode": 0, "already_exited": True})
        except OSError as exc:
            result.update({"fallback": "kill", "error": f"{exc.__class__.__name__}: {exc}"})
            proc.kill()
    return result


def _eval_metadata(
    workspace: CandidateWorkspace,
    validate_path: Path,
    stage_context: dict,
    validator_env: dict | None = None,
    artifacts: dict | None = None,
) -> dict:
    metadata = {
        "primary_file": workspace.primary_file,
        "files": sorted(workspace.files),
        "validate_path": str(validate_path),
        "stage": stage_context,
    }
    if validator_env is not None:
        metadata["validator_env"] = validator_env
    if artifacts is not None:
        metadata["artifacts"] = artifacts
    return metadata


def _validate_problem_local_evaluator_path(path: Path, problem_dir: Path) -> Path:
    resolved_root = problem_dir.resolve()
    resolved = path.resolve(strict=False)
    if resolved_root != resolved and resolved_root not in resolved.parents:
        raise ValueError(f"Evaluator validate_path escapes problem directory: {path}")
    if not resolved.exists():
        raise ValueError(f"Evaluator validate_path does not exist: {path}")
    if not resolved.is_file():
        raise ValueError(f"Evaluator validate_path is not a file: {path}")
    if resolved.suffix != ".py":
        raise ValueError(f"Evaluator validate_path must be a Python file: {path}")
    return resolved


def _collect_evaluator_artifacts(
    cand_root: Path,
    artifact_dir: Path | None,
    *,
    include: list[str],
    exclude: list[str],
    max_files: int,
    max_bytes: int,
    stage_context: dict,
) -> dict:
    metadata = {
        "enabled": bool(artifact_dir and include),
        "include": include,
        "exclude": exclude,
        "max_files": max_files,
        "max_bytes": max_bytes,
        "files": [],
        "skipped": [],
        "total_bytes": 0,
    }
    if not artifact_dir or not include:
        return metadata
    collection_id = uuid4().hex
    metadata["collection_id"] = collection_id
    stage_name = str(stage_context.get("name", "stage"))
    sample_index = stage_context.get("sample_index")
    attempt = stage_context.get("attempt")
    metadata["stage"] = {
        "name": stage_name,
        "sample_index": sample_index,
        "attempt": attempt,
    }
    target_root = artifact_dir / collection_id
    matched = _matching_artifact_paths(cand_root, include, exclude)
    for path in matched:
        rel = path.relative_to(cand_root).as_posix()
        if len(metadata["files"]) >= max_files:
            metadata["skipped"].append({"path": rel, "reason": "max_files"})
            continue
        size = path.stat().st_size
        if metadata["total_bytes"] + size > max_bytes:
            metadata["skipped"].append({"path": rel, "reason": "max_bytes", "bytes": size})
            continue
        raw = path.read_bytes()
        dest = target_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        metadata["total_bytes"] += size
        metadata["files"].append(
            {
                "path": rel,
                "artifact_path": (Path(artifact_dir.name) / collection_id / rel).as_posix(),
                "bytes": size,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "stage_name": stage_name,
                "sample_index": sample_index,
                "attempt": attempt,
            }
        )
    return metadata


def _matching_artifact_paths(cand_root: Path, include: list[str], exclude: list[str]) -> list[Path]:
    paths = []
    for path in sorted((p for p in cand_root.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        rel = path.relative_to(cand_root).as_posix()
        if not any(fnmatch.fnmatchcase(rel, pattern) for pattern in include):
            continue
        if any(fnmatch.fnmatchcase(rel, pattern) for pattern in exclude):
            continue
        paths.append(path)
    return paths


def _validator_env(allowlist: list[str]) -> dict[str, str]:
    env = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    for name in [*_DEFAULT_VALIDATOR_ENV_NAMES, *allowlist]:
        found = _find_env(name)
        if found is not None:
            key, value = found
            env[key] = value
    return env


def _validator_env_metadata(env: dict[str, str], allowlist: list[str]) -> dict:
    return {
        "policy": "minimal_allowlist",
        "default_keys": sorted(
            key for key in env if key.upper() in set(_DEFAULT_VALIDATOR_ENV_NAMES)
        ),
        "allowlist": sorted(allowlist),
        "provided_keys": sorted(env),
        "values_redacted": True,
    }


def _find_env(name: str) -> tuple[str, str] | None:
    if name in os.environ:
        return name, os.environ[name]
    upper = name.upper()
    for key, value in os.environ.items():
        if key.upper() == upper:
            return key, value
    return None


def _redact_secrets(text: str) -> str:
    if not text:
        return text
    text = _SECRET_ASSIGNMENT.sub(r"\1\2\3[REDACTED]", text)
    return _SECRET_TOKEN.sub("[REDACTED]", text)


def evaluator_entrypoint_provenance(problem: Problem, stages: list[dict] | None = None) -> list[dict]:
    """Return manifest-ready hashes for evaluator Python entrypoints.

    This records the explicit evaluator files LibreEvolve will call. It does
    not claim transitive helper/data provenance.
    """
    stage_configs = stages or []
    if not stage_configs:
        path = _validate_problem_local_evaluator_path(problem.validate_path, problem.problem_dir)
        return [_evaluator_source_record(path, problem.problem_dir, role="default")]

    records: list[dict] = []
    for index, stage in enumerate(stage_configs):
        raw_path = stage.get("validate_path")
        if raw_path is None:
            path = problem.validate_path
        else:
            path = Path(str(raw_path))
            if not path.is_absolute():
                path = problem.problem_dir / path
        resolved = _validate_problem_local_evaluator_path(path, problem.problem_dir)
        records.append(
            _evaluator_source_record(
                resolved,
                problem.problem_dir,
                role="stage",
                stage_name=str(stage.get("name", f"stage_{index}")),
                stage_index=index,
                configured_validate_path=None if raw_path is None else str(raw_path),
            )
        )
    return records


def _evaluator_source_record(
    path: Path,
    problem_dir: Path,
    *,
    role: str,
    stage_name: str | None = None,
    stage_index: int | None = None,
    configured_validate_path: str | None = None,
) -> dict:
    raw = path.read_bytes()
    record = {
        "role": role,
        "path": str(path),
        "relative_path": path.relative_to(problem_dir.resolve()).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "source_type": "python",
    }
    if stage_name is not None:
        record["stage_name"] = stage_name
    if stage_index is not None:
        record["stage_index"] = stage_index
    if configured_validate_path is not None:
        record["configured_validate_path"] = configured_validate_path
    return record


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
