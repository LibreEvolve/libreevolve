import hashlib
import json
import os
import shutil, tempfile
import subprocess
import sys
import time
from pathlib import Path
import libreevolve.core.evaluator as evaluator
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.config import Config, ConfigError
import pytest
from libreevolve.core.evaluator import CascadeEvaluator, EvaluationResult, EvaluationStageResult, evaluation_accounting, preflight_evaluator_contracts
from libreevolve.core.jsonl import strict_json_dumps
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem

def _problem(validate_src: str, metrics: list[dict] | None = None):
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(validate_src, encoding="utf-8")
    metric_schema = metrics or [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
    ]
    primary = next(
        (str(metric["name"]) for metric in metric_schema if metric.get("primary")),
        str(metric_schema[0]["name"]),
    )
    bounds = tuple(metric.get("bounds", [0.0, 1.0]) for metric in metric_schema if str(metric["name"]) == primary)
    primary_bounds = tuple(bounds[0]) if bounds else (0.0, 1.0)
    return Problem(name="t", task_description="t",
                   metrics=metric_schema,
                   primary_metric=primary, primary_bounds=primary_bounds,
                   validate_path=d/"validate.py", initial_programs=[], problem_dir=d), d


class _FakeTimeoutProcess:
    pid = 4242
    returncode = None

    def __init__(self):
        self.killed = False

    def poll(self):
        return None

    def kill(self):
        self.killed = True


@pytest.mark.parametrize("mode", ["external_validator", "embedded_evaluate"])
def test_evaluator_canonicalizes_internal_temp_root_before_materialization(
    tmp_path, monkeypatch, mode
):
    """Internal roots tolerate a host temporary-directory alias such as macOS /var."""
    real_root = tmp_path / "real-temp"
    linked_root = tmp_path / "linked-temp"
    real_root.mkdir()
    linked_root.symlink_to(real_root, target_is_directory=True)

    class _LinkedTemporaryDirectory:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return str(linked_root)

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(
        evaluator.tempfile,
        "TemporaryDirectory",
        _LinkedTemporaryDirectory,
    )
    validate_src = "def evaluate(c): return {'score': 0.9, 'is_valid': True}"
    p, d = _problem(validate_src)
    try:
        if mode == "embedded_evaluate":
            workspace = CandidateWorkspace(
                files={
                    "main.py": (
                        "def evaluate(eval_inputs):\n"
                        "    return {'score': 0.9, 'is_valid': True}\n"
                    )
                },
                primary_file="main.py",
            )
            evaluator_instance = CascadeEvaluator(
                p,
                stages=[{"name": "candidate_eval", "mode": mode}],
            )
        else:
            workspace = CandidateWorkspace.from_code("x = 1")
            evaluator_instance = CascadeEvaluator(p)

        result = evaluator_instance.evaluate(workspace, None)

        assert result.is_valid is True
        assert result.error is None
        assert result.fitness == 0.9
    finally:
        shutil.rmtree(d)
        if real_root.exists():
            shutil.rmtree(real_root)
        if linked_root.is_symlink():
            linked_root.unlink()


def test_direct_evaluator_rejects_unsafe_configured_stage_labels():
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    try:
        with pytest.raises(ConfigError, match="manifest-safe stage label"):
            CascadeEvaluator(
                p,
                stages=[{"name": "gate\napi_key=sk-proj_secret_1234567890"}],  # pragma: allowlist secret
            )
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_requires_configured_stage_names():
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    try:
        with pytest.raises(ConfigError, match="name is required"):
            CascadeEvaluator(p, stages=[{"min_score": 0.0}])
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_rejects_builtin_stage_name_collision():
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    try:
        with pytest.raises(ConfigError, match="reserved"):
            CascadeEvaluator(p, stages=[{"name": "syntax"}])
    finally:
        shutil.rmtree(d)


def test_evaluation_result_dataclasses_reject_non_json_safe_direct_fields():
    with pytest.raises(ValueError, match="EvaluationResult.stdout must be a string"):
        EvaluationResult(
            fitness=1.0,
            metrics={"score": 1.0, "is_valid": True},
            is_valid=True,
            stdout=object(),
        )

    with pytest.raises(ValueError, match="EvaluationStageResult.stdout must be a string"):
        EvaluationStageResult(name="validate", passed=True, stdout=object())

    with pytest.raises(ValueError, match="EvaluationResult.metadata must be JSON-safe"):
        EvaluationResult(
            fitness=1.0,
            metrics={"score": 1.0, "is_valid": True},
            is_valid=True,
            metadata={"raw": object()},
        )

    with pytest.raises(ValueError, match="EvaluationResult.fitness must be finite"):
        EvaluationResult(
            fitness=float("nan"),
            metrics={"score": 1.0, "is_valid": True},
            is_valid=True,
        )

    with pytest.raises(ValueError, match="EvaluationStageResult.elapsed_sec must be >="):
        EvaluationStageResult(name="validate", passed=True, elapsed_sec=-0.1)


def test_evaluation_result_to_dict_revalidates_plugin_mutations():
    result = EvaluationResult(
        fitness=1.0,
        metrics={"score": 1.0, "is_valid": True},
        is_valid=True,
        stages=[EvaluationStageResult(name="validate", passed=True)],
    )

    result.stdout = object()
    with pytest.raises(ValueError, match="EvaluationResult.stdout must be a string"):
        result.to_dict()

    result.stdout = ""
    result.stages[0].metadata = {"raw": object()}
    with pytest.raises(ValueError, match="EvaluationStageResult.metadata must be JSON-safe"):
        result.to_dict()

    result.stages[0].metadata = {}
    result.metadata = {"elapsed": float("inf")}
    with pytest.raises(ValueError, match="EvaluationResult.metadata must be JSON-safe"):
        result.to_dict()


def test_evaluation_result_to_dict_is_strict_json_safe_and_redacted():
    token = "sk-proj_evalresultsecret1234567890"  # pragma: allowlist secret
    result = EvaluationResult(
        fitness=1,
        metrics={"score": 1, "is_valid": True},
        is_valid=True,
        stages=[
            EvaluationStageResult(
                name="llm_feedback:critic",
                passed=False,
                score=0,
                metrics={"score": 0},
                stderr=f"token={token}",
                error=f"api_key={token}",
                metadata={"raw": f"secret={token}"},
            )
        ],
        stdout=f"token={token}",
        stderr=f"secret={token}",
        error=f"password={token}",
        elapsed_sec=0,
        metadata={"raw": f"api_key={token}"},
    )

    payload = result.to_dict()
    strict_json_dumps(payload)
    Program(code="x = 1", fitness=payload["fitness"], evaluation=payload)

    serialized = json.dumps(payload, sort_keys=True)
    assert token not in serialized
    assert "[REDACTED]" in serialized


@pytest.mark.parametrize("timeout_sec", [0, -1, True, "bad", float("inf"), float("nan")])
def test_direct_evaluator_rejects_invalid_timeout_values(timeout_sec):
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    try:
        with pytest.raises(ConfigError, match="timeout_sec"):
            CascadeEvaluator(p, timeout_sec=timeout_sec)
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize("timeout_sec", [1, 0.5])
def test_direct_evaluator_accepts_valid_timeout_values(timeout_sec):
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    try:
        ev = CascadeEvaluator(p, timeout_sec=timeout_sec)

        assert ev._timeout == float(timeout_sec)
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"artifact_include": "*.json"}, "artifact_include"),
        ({"artifact_include": [""]}, "artifact_include"),
        ({"artifact_include": ["reports\u202e/*.json"]}, "display-safe"),
        (
            {"artifact_include": ["api_key=sk-proj_DIRECT_ARTIFACT_INCLUDE_SECRET_1234567890/*.txt"]},  # pragma: allowlist secret
            "manifest-safe glob patterns",
        ),
        ({"artifact_exclude": "*.secret"}, "artifact_exclude"),
        ({"artifact_exclude": ["reports\u200d/*.json"]}, "display-safe"),
        (
            {"artifact_exclude": ["api_key=sk-proj_DIRECT_ARTIFACT_EXCLUDE_SECRET_1234567890/*.txt"]},  # pragma: allowlist secret
            "manifest-safe glob patterns",
        ),
        ({"artifact_include": ["../secret/*.txt"]}, "path-safe glob patterns"),
        ({"artifact_exclude": ["/absolute/*.txt"]}, "path-safe glob patterns"),
        ({"artifact_include": ["C:/secret/*.txt"]}, "path-safe glob patterns"),
        ({"artifact_exclude": ["..\\secret\\*.txt"]}, "path-safe glob patterns"),
        ({"artifact_include": ["nested//file.txt"]}, "path-safe glob patterns"),
        ({"artifact_max_files": -1}, "artifact_max_files"),
        ({"artifact_max_files": True}, "artifact_max_files"),
        ({"artifact_max_files": "1"}, "artifact_max_files"),
        ({"artifact_max_bytes": -1}, "artifact_max_bytes"),
        ({"artifact_max_bytes": True}, "artifact_max_bytes"),
        ({"artifact_max_bytes": "1024"}, "artifact_max_bytes"),
        ({"artifact_redact_secrets": "yes"}, "artifact_redact_secrets"),  # pragma: allowlist secret
    ],
)
def test_direct_evaluator_rejects_invalid_artifact_options(kwargs, message):
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    try:
        with pytest.raises(ConfigError, match=message):
            CascadeEvaluator(p, **kwargs)
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("stage", "message"),
    [
        ({"name": "zero", "samples": 0}, "samples"),
        ({"name": "negative", "retries": -1}, "retries"),
        ({"name": "too_many", "retries": 11}, "retries"),
        ({"name": "timeout", "timeout_sec": 0}, "timeout_sec"),
        ({"name": "budget", "max_sample_seconds": 0}, "max_sample_seconds"),
        ({"name": "budget", "max_sample_seconds": "fast"}, "max_sample_seconds"),
        ({"name": "budget", "max_stage_seconds": 0}, "max_stage_seconds"),
        ({"name": "budget", "max_stage_seconds": "fast"}, "max_stage_seconds"),
        ({"name": "threshold", "min_score": "high"}, "min_score"),
        ({"name": "bad_seed", "seeds": [Path("seed.txt")]}, "seeds"),
        ({"name": "mismatch", "samples": 2, "seeds": [1]}, "samples"),
    ],
)
def test_direct_evaluator_rejects_invalid_configured_stage_schema(stage, message):
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    try:
        with pytest.raises(ConfigError, match=message):
            CascadeEvaluator(p, stages=[stage])
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_accepts_maximum_configured_stage_retry_cap():
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "retry_cap", "retries": 10}])

        assert ev._stages[0]["retries"] == 10
    finally:
        shutil.rmtree(d)


def test_preflight_configured_stage_escape_uses_safe_path_context(tmp_path):
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    secret_dir = tmp_path / "api_key=sk-proj_preflightpath_secret_1234567890"  # pragma: allowlist secret
    secret_dir.mkdir()
    outside = secret_dir / "outside_validate.py"
    outside.write_text("def evaluate(c): return {'score': 1.0, 'is_valid': True}", encoding="utf-8")

    try:
        with pytest.raises(ValueError) as excinfo:
            preflight_evaluator_contracts(
                p,
                stages=[{"name": "outside", "validate_path": str(outside)}],
            )
    finally:
        shutil.rmtree(d)

    message = str(excinfo.value)
    assert "Evaluator validate_path escapes problem directory" in message
    assert "<outside-problem>/outside_validate.py" in message
    assert "path_scope=outside_problem" in message
    assert "path_hash=" in message
    assert str(secret_dir) not in message
    assert "sk-proj_preflightpath_secret" not in message


def test_preflight_missing_problem_local_validator_uses_safe_path_context():
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    missing = d / "missing_validate.py"
    p.validate_path = missing

    try:
        with pytest.raises(ValueError) as excinfo:
            preflight_evaluator_contracts(p)
    finally:
        shutil.rmtree(d)

    message = str(excinfo.value)
    assert "Evaluator validate_path does not exist" in message
    assert "missing_validate.py" in message
    assert "path_scope=problem_relative" in message
    assert "path_hash=" in message
    assert str(d) not in message


# Tier 0 tests
def test_t0_no_diff_blocks():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "no_diff_blocks") == -0.4
    finally: shutil.rmtree(d)

def test_t0_no_valid_changes():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "no_valid_changes") == -0.3
    finally: shutil.rmtree(d)

def test_t0_search_not_found():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("x=1", "search_not_found") == -0.3
    finally: shutil.rmtree(d)


def test_diff_error_known_reason_records_schema_metadata():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try:
        result = CascadeEvaluator(p).evaluate("x=1", "no_diff_blocks")

        assert result == -0.4
        assert result.error == "no_diff_blocks"
        assert result.stages[0].error == "no_diff_blocks"
        assert result.metadata["diff_error"] == {
            "schema": "diff_error_v1",
            "reason": "no_diff_blocks",
            "known": True,
            "value_type": "str",
            "penalty": -0.4,
        }
        assert result.stages[0].metadata["diff_error"] == result.metadata["diff_error"]
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("reason", "penalty"),
    [
        ("blank_mutation_payload", -0.4),
        ("oversized_mutation_payload", -0.4),
    ],
)
def test_diff_error_payload_schema_reasons_are_canonical(reason, penalty):
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try:
        result = CascadeEvaluator(p).evaluate("x=1", reason)

        assert result == penalty
        assert result.error == reason
        assert result.stages[0].error == reason
        assert result.metadata["diff_error"] == {
            "schema": "diff_error_v1",
            "reason": reason,
            "known": True,
            "value_type": "str",
            "penalty": penalty,
        }
    finally:
        shutil.rmtree(d)


def test_diff_error_preserves_declared_metric_vector_for_synthetic_failure():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "latency", "direction": "minimize", "bounds": [0.0, 10.0]},
    ]
    p, d = _problem("def evaluate(c): return {'score':1.0,'latency':1.0,'is_valid':True}", metrics)
    try:
        result = CascadeEvaluator(p).evaluate("x=1", "no_valid_changes")

        assert result.metrics == {"score": -0.3, "latency": -0.3, "is_valid": False}
        assert result.stages[0].metrics == result.metrics
        assert result.metadata["synthetic_metrics"] == {
            "schema": "synthetic_failure_metrics_v1",
            "policy": "declared_metric_penalty",
            "penalty": -0.3,
            "metric_names": ["score", "latency"],
        }
    finally:
        shutil.rmtree(d)


def test_diff_error_unknown_string_is_redacted_and_bounded():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    secret = "api_key=sk-proj_diffsecret1234567890"  # pragma: allowlist secret
    try:
        result = CascadeEvaluator(p).evaluate("x=1", secret)

        assert result == -0.4
        assert result.error == "unknown_diff_error"
        assert result.stages[0].error == "unknown_diff_error"
        metadata = result.metadata["diff_error"]
        assert metadata["schema"] == "diff_error_v1"
        assert metadata["reason"] == "unknown_diff_error"
        assert metadata["known"] is False
        assert metadata["value_type"] == "str"
        assert metadata["detail"] == "api_key=[REDACTED]"
        assert metadata["detail_redacted"] is True
        assert secret not in json.dumps(result.to_dict())
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    "diff_error",
    [
        7,
        True,
        ["no_diff_blocks"],
        {"error": "api_key=sk-proj_diffsecret1234567890"},  # pragma: allowlist secret
    ],
)
def test_diff_error_non_string_values_become_malformed_diagnostics(diff_error):
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try:
        result = CascadeEvaluator(p).evaluate("x=1", diff_error)

        assert result == -0.4
        assert result.error == "malformed_diff_error"
        assert result.stages[0].error == "malformed_diff_error"
        metadata = result.metadata["diff_error"]
        assert metadata["schema"] == "diff_error_v1"
        assert metadata["reason"] == "malformed_diff_error"
        assert metadata["known"] is False
        assert metadata["value_type"] == type(diff_error).__name__
        assert "sk-proj_diffsecret1234567890" not in json.dumps(result.to_dict())
    finally:
        shutil.rmtree(d)


def test_diff_error_unknown_control_string_is_escaped_and_truncated():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    raw_error = "bad\nreason\u202e" + ("x" * 600)
    try:
        result = CascadeEvaluator(p).evaluate("x=1", raw_error)

        metadata = result.metadata["diff_error"]
        assert metadata["detail_escaped"] is True
        assert metadata["detail_truncated"] is True
        assert "\\u000a" in metadata["detail"]
        assert "\\u202e" in metadata["detail"]
        assert "\n" not in metadata["detail"]
        assert "\u202e" not in metadata["detail"]
        assert len(metadata["detail"]) <= 500
    finally:
        shutil.rmtree(d)


def test_t0_none_proceeds():
    p, d = _problem("def evaluate(c): return {'score':0.9,'is_valid':True}")
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result == 0.9
        assert result.metrics["score"] == 0.9
        assert result.is_valid is True
    finally: shutil.rmtree(d)

# Tier 1
def test_t1_syntax_error():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    try: assert CascadeEvaluator(p).evaluate("def foo(:\n    pass", None) == -0.2
    finally: shutil.rmtree(d)

# Tier 2
def test_t2_domain_invalid():
    p, d = _problem("def evaluate(c): return {'score':0.0,'is_valid':False}")
    try: assert CascadeEvaluator(p).evaluate("x=1", None) == -0.1
    finally: shutil.rmtree(d)

def test_t2_crash():
    p, d = _problem("def evaluate(c): raise RuntimeError('boom')")
    try: assert CascadeEvaluator(p).evaluate("x=1", None) == -0.2
    finally: shutil.rmtree(d)

def test_t2_success():
    p, d = _problem("def evaluate(c): return {'score':0.42,'is_valid':True}")
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert abs(result - 0.42) < 1e-9
        assert result.stages[-1].name == "validate"
        assert result.metadata["validate_path"] == "validate.py"
        assert result.metadata["validate_path_scope"] == "problem_relative"
        assert result.metadata["validate_path_redacted"] is True
        assert len(result.metadata["validate_path_hash"]) == 64
    finally: shutil.rmtree(d)


def test_materialization_collision_returns_invalid_evaluation_result():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    workspace = CandidateWorkspace(
        files={"README.md": "a\n", "readme.md": "b\n"},
        primary_file="README.md",
    )
    try:
        result = CascadeEvaluator(p).evaluate(workspace, None)
        assert result.fitness == -0.2
        assert result.is_valid is False
        assert result.error == "materialization_error"
        assert result.stages[-1].error == "materialization_error"
        assert result.metrics == {"score": -0.2, "is_valid": False}
        assert result.metadata["primary_file"] == "README.md"
        assert result.metadata["files"] == ["README.md", "readme.md"]
        materialization_error = result.metadata["materialization_error"]
        assert materialization_error["exception_type"] == "CandidateMaterializationError"
        assert materialization_error["reason"] == "candidate_path_collision"
        assert materialization_error["paths"] == ["README.md", "readme.md"]
        assert "collide" in materialization_error["message"]
    finally:
        shutil.rmtree(d)


def test_static_source_copy_materialization_error_has_structured_metadata():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    source = d / "external.bin"
    source.write_bytes(b"actual")
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {
                "path": "fixtures/input.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(b"expected").hexdigest(),
                "bytes": len(b"actual"),
                "source_kind": "copied_static_asset",
                "source_copy_path": str(source),
            }
        ],
    )
    try:
        result = CascadeEvaluator(p).evaluate(workspace, None)
        assert result.error == "materialization_error"
        materialization_error = result.metadata["materialization_error"]
        assert materialization_error["exception_type"] == "CandidateMaterializationError"
        assert materialization_error["reason"] == "static_source_copy_sha256_mismatch"
        assert materialization_error["paths"] == ["fixtures/input.bin", str(source)]
        assert "source_copy_path sha256 does not match" in materialization_error["message"]
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("validate_src", "candidate", "expected_error"),
    [
        ("def evaluate(c): raise RuntimeError('boom')", "x=1", "subprocess_error"),
        (
            "def evaluate(c): return {'score': 1.0, 'is_valid': True}",
            "def broken(:\n",
            "syntax_error",
        ),
        (
            "def evaluate(c): return {'score': 1.0, 'is_valid': True}",
            "x=1",
            "malformed_metrics",
        ),
    ],
)
def test_synthetic_evaluator_failures_preserve_declared_metric_vector(
    validate_src, candidate, expected_error
):
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "latency", "direction": "minimize", "bounds": [0.0, 10.0]},
    ]
    p, d = _problem(validate_src, metrics)
    try:
        result = CascadeEvaluator(p).evaluate(candidate, None)

        assert result.error == expected_error
        assert result.metrics == {"score": -0.2, "latency": -0.2, "is_valid": False}
        assert result.stages[-1].metrics == result.metrics
        assert result.metadata["synthetic_metrics"]["metric_names"] == ["score", "latency"]
        assert result.metadata["synthetic_metrics"]["penalty"] == -0.2
    finally:
        shutil.rmtree(d)


def test_t2_timeout():
    p, d = _problem("import time\ndef evaluate(c): time.sleep(30); return {'score':1.0,'is_valid':True}")
    try:
        ev = CascadeEvaluator(p, timeout_sec=0.5)
        result = ev.evaluate("x=1", None)
        assert result == -0.2
        assert result.error == "timeout"
        assert result.metrics == {"score": -0.2, "is_valid": False}
        assert result.metadata["timeout_cleanup"]["attempted"] is True
    finally:
        shutil.rmtree(d)


def test_timeout_preserves_declared_metric_vector_for_synthetic_failure():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "latency", "direction": "minimize", "bounds": [0.0, 10.0]},
    ]
    p, d = _problem(
        "import time\ndef evaluate(c): time.sleep(30); return {'score':1.0,'latency':1.0,'is_valid':True}",
        metrics,
    )
    try:
        result = CascadeEvaluator(p, timeout_sec=0.3).evaluate("x=1", None)

        assert result.error == "timeout"
        assert result.metrics == {"score": -0.2, "latency": -0.2, "is_valid": False}
        assert result.stages[-1].metrics == result.metrics
        assert result.metadata["synthetic_metrics"]["metric_names"] == ["score", "latency"]
    finally:
        shutil.rmtree(d)


def test_timeout_terminates_validator_child_process(tmp_path):
    marker = tmp_path / "child_survived.txt"
    child_code = (
        "import pathlib,time; "
        "time.sleep(1.0); "
        f"pathlib.Path({str(marker)!r}).write_text('alive')"
    )
    p, d = _problem(
        "import subprocess, sys, time\n"
        "def evaluate(c):\n"
        f"    subprocess.Popen([sys.executable, '-c', {child_code!r}])\n"
        "    time.sleep(30)\n"
        "    return {'score':1.0,'is_valid':True}\n"
    )
    try:
        result = CascadeEvaluator(p, timeout_sec=0.3).evaluate("x=1", None)
        assert result.error == "timeout"
        assert result.metadata["timeout_cleanup"]["attempted"] is True
        time.sleep(1.5)
        assert not marker.exists()
    finally:
        shutil.rmtree(d)


def test_timeout_cleanup_records_bounded_taskkill_output(monkeypatch):
    proc = _FakeTimeoutProcess()

    def fake_run(args, **kwargs):
        assert args[:2] == ["taskkill", "/PID"]
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        return subprocess.CompletedProcess(args, 0, stdout="terminated", stderr="warning")

    monkeypatch.setattr(evaluator.os, "name", "nt")
    monkeypatch.setattr(evaluator.subprocess, "run", fake_run)

    cleanup = evaluator._terminate_process_tree(proc)

    assert cleanup["method"] == "taskkill"
    assert cleanup["returncode"] == 0
    assert cleanup["stdout"] == "terminated"
    assert cleanup["stderr"] == "warning"
    assert cleanup["output_policy"]["policy"] == "redact_then_truncate"
    assert cleanup["output_policy"]["max_chars"] == 2000
    assert cleanup["stdout_diagnostics"]["truncated"] is False
    assert cleanup["stderr_diagnostics"]["truncated"] is False


def test_timeout_cleanup_redacts_and_truncates_large_taskkill_output(monkeypatch):
    proc = _FakeTimeoutProcess()
    token = "sk-" + "proj-" + "cleanupsecret1234567890"
    large_stdout = f"before {token} " + ("x" * 3000)
    large_stderr = "e" * 3001

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args, 1, stdout=large_stdout, stderr=large_stderr)

    monkeypatch.setattr(evaluator.os, "name", "nt")
    monkeypatch.setattr(evaluator.subprocess, "run", fake_run)

    cleanup = evaluator._terminate_process_tree(proc)

    assert token not in cleanup["stdout"]
    assert "[REDACTED]" in cleanup["stdout"]
    assert len(cleanup["stdout"]) == 2000
    assert len(cleanup["stderr"]) == 2000
    assert cleanup["stdout"].endswith("...<truncated>")
    assert cleanup["stderr"].endswith("...<truncated>")
    assert cleanup["stdout_diagnostics"]["redacted"] is True
    assert cleanup["stdout_diagnostics"]["truncated"] is True
    assert cleanup["stderr_diagnostics"]["truncated"] is True
    assert cleanup["stdout_diagnostics"]["omitted_chars"] > 0


def test_timeout_cleanup_taskkill_nonzero_kills_reported_child_pids(monkeypatch):
    proc = _FakeTimeoutProcess()
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        if args == ["taskkill", "/PID", str(proc.pid), "/T", "/F"]:
            return subprocess.CompletedProcess(
                args,
                255,
                stdout=f"SUCCESS: The process with PID {proc.pid} has been terminated.\n",
                stderr=(
                    "ERROR: The process with PID 9999 could not be terminated.\n"
                    "Reason: The operation attempted is not supported.\n"
                ),
            )
        assert args == ["taskkill", "/PID", "9999", "/F"]
        return subprocess.CompletedProcess(args, 0, stdout="terminated child", stderr="")

    monkeypatch.setattr(evaluator.os, "name", "nt")
    monkeypatch.setattr(evaluator.subprocess, "run", fake_run)

    cleanup = evaluator._terminate_process_tree(proc)

    assert cleanup["method"] == "taskkill"
    assert cleanup["returncode"] == 255
    assert cleanup["reported_child_pids"] == [9999]
    assert cleanup["direct_child_kill"][0]["pid"] == 9999
    assert cleanup["direct_child_kill"][0]["returncode"] == 0
    assert cleanup["direct_child_kill"][0]["stdout"] == "terminated child"
    assert calls == [
        ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
        ["taskkill", "/PID", "9999", "/F"],
    ]


def test_timeout_cleanup_taskkill_failure_uses_bounded_error_and_kill(monkeypatch):
    proc = _FakeTimeoutProcess()
    token = "sk-" + "proj-" + "cleanupfailuresecret1234567890"

    def fake_run(args, **kwargs):
        raise FileNotFoundError(f"taskkill missing {token} {'x' * 2500}")

    monkeypatch.setattr(evaluator.os, "name", "nt")
    monkeypatch.setattr(evaluator.subprocess, "run", fake_run)

    cleanup = evaluator._terminate_process_tree(proc)

    assert cleanup["method"] == "taskkill"
    assert cleanup["fallback"] == "kill"
    assert proc.killed is True
    assert token not in cleanup["error"]
    assert "[REDACTED]" in cleanup["error"]
    assert len(cleanup["error"]) == 2000
    assert cleanup["error_diagnostics"]["redacted"] is True
    assert cleanup["error_diagnostics"]["truncated"] is True


def test_timeout_cleanup_non_windows_uses_process_group(monkeypatch):
    proc = _FakeTimeoutProcess()
    calls = []

    def fake_killpg(pid, sig):
        calls.append((pid, sig))

    monkeypatch.setattr(evaluator.os, "name", "posix")
    monkeypatch.setattr(evaluator.os, "killpg", fake_killpg, raising=False)
    monkeypatch.setattr(evaluator.signal, "SIGKILL", 9, raising=False)

    cleanup = evaluator._terminate_process_tree(proc)

    assert cleanup["method"] == "killpg"
    assert cleanup["returncode"] == 0
    assert calls == [(proc.pid, evaluator.signal.SIGKILL)]
    assert cleanup["output_policy"]["max_chars"] == 2000
    assert "stdout" not in cleanup
    assert proc.killed is False


def test_t2_bad_json():
    # validate.py prints non-JSON stdout but exits 0
    p, d = _problem(
        "def evaluate(c):\n"
        "    import sys; sys.stdout.write('not-json\\n'); raise SystemExit(0)"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result == -0.2
        assert result.error == "malformed_metrics"
        assert result.metadata["malformed_metrics"]["reason"] == "malformed_metrics"
        assert "result file was not written" in result.metadata["malformed_metrics"]["message"]
    finally:
        shutil.rmtree(d)


def test_validator_stdout_json_cannot_replace_returned_metrics():
    p, d = _problem(
        "def evaluate(c):\n"
        "    print('{\"score\": 0.0, \"is_valid\": false}')\n"
        "    print('diagnostic text after fake json')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.fitness == 1.0
        assert result.is_valid is True
        assert result.metrics == {"score": 1.0, "is_valid": True}
        assert '{"score": 0.0, "is_valid": false}' in result.stdout
    finally:
        shutil.rmtree(d)


def test_background_child_stdout_json_cannot_replace_returned_metrics():
    child_code = (
        "import time; "
        "time.sleep(0.2); "
        "print('{\"score\": 0.0, \"is_valid\": false}', flush=True)"
    )
    p, d = _problem(
        "import subprocess, sys\n"
        "def evaluate(c):\n"
        f"    subprocess.Popen([sys.executable, '-c', {child_code!r}])\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.fitness == 1.0
        assert result.is_valid is True
        assert result.metrics == {"score": 1.0, "is_valid": True}
        assert '{"score": 0.0, "is_valid": false}' in result.stdout
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("expression", "type_name"),
    [
        ("object()", "object"),
        ("{1, 2}", "set"),
        ("b'raw'", "bytes"),
        ("__import__('numpy').int64(1)", "int64"),
        ("__import__('numpy').array([1])", "ndarray"),
    ],
)
def test_non_json_serializable_validator_return_is_malformed_metrics(expression, type_name):
    p, d = _problem(
        "def evaluate(c):\n"
        f"    return {{'score': {expression}, 'is_valid': True}}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.fitness == -0.2
        assert result.is_valid is False
        assert result.error == "malformed_metrics"
        diagnostic = result.metadata["malformed_metrics"]
        assert diagnostic["reason"] == "not_json_serializable"
        assert type_name in diagnostic["message"]
    finally:
        shutil.rmtree(d)


def test_non_string_evaluator_result_keys_are_rejected_before_json_coercion():
    p, d = _problem(
        "def evaluate(c):\n"
        "    return {1: 0.0, 'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.fitness == -0.2
        assert result.is_valid is False
        assert result.error == "malformed_metrics"
        assert result.metrics == {"score": -0.2, "is_valid": False}
        diagnostic = result.metadata["malformed_metrics"]
        assert diagnostic["reason"] == "non_string_keys"
        assert diagnostic["exception_type"] == "ValueError"
        assert "evaluator result keys must be strings" in diagnostic["message"]
        assert "non_string_key_types=int" in diagnostic["message"]
    finally:
        shutil.rmtree(d)


def test_bool_and_none_evaluator_result_keys_are_rejected():
    p, d = _problem(
        "def evaluate(c):\n"
        "    return {False: 0.0, None: 0.1, 'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.error == "malformed_metrics"
        assert result.metadata["malformed_metrics"]["reason"] == "non_string_keys"
        message = result.metadata["malformed_metrics"]["message"]
        assert "non_string_key_types=NoneType,bool" in message
    finally:
        shutil.rmtree(d)


def test_malformed_metric_contract_diagnostic_records_validator_reason():
    p, d = _problem(
        "def evaluate(c):\n"
        "    return {'score': 1.0, 'is_valid': True, 'extra': 3}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.error == "malformed_metrics"
        diagnostic = result.metadata["malformed_metrics"]
        assert diagnostic["reason"] == "undeclared_metrics"
        assert diagnostic["exception_type"] == "ValueError"
        assert "undeclared metrics" in diagnostic["message"]
        assert "extra" in diagnostic["message"]
    finally:
        shutil.rmtree(d)


def test_evaluator_program_output_is_persisted_separately_from_metrics():
    p, d = _problem(
        "def evaluate(c):\n"
        "    return {'score': 1.0, 'is_valid': True, 'program_output': {'answer': 42}}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.metrics == {"score": 1.0, "is_valid": True}
        outputs = result.metadata["program_outputs"]
        assert outputs["source_key"] == "program_output"
        assert outputs["value"] == {"answer": 42}
        assert outputs["omitted"] is False
        assert outputs["sha256"]
    finally:
        shutil.rmtree(d)


def test_evaluator_outputs_key_redacts_and_bounds_structured_output():
    token = "sk-" + "proj-" + "programoutputsecret1234567890"
    p, d = _problem(
        "def evaluate(c):\n"
        f"    return {{'score': 1.0, 'is_valid': True, 'outputs': {{'text': {'prefix ' + token + ' suffix'!r}}}}}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)

        outputs = result.metadata["program_outputs"]
        assert outputs["source_key"] == "outputs"
        assert outputs["redacted"] is True
        assert token not in str(outputs["value"])
        assert "[REDACTED]" in outputs["value"]["text"]
        assert outputs["json_chars"] <= outputs["max_json_chars"]
    finally:
        shutil.rmtree(d)


def test_large_evaluator_program_output_keeps_bounded_preview_and_hash():
    p, d = _problem(
        "def evaluate(c):\n"
        "    return {'score': 1.0, 'is_valid': True, 'outputs': {'blob': 'x' * 8000}}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)

        outputs = result.metadata["program_outputs"]
        assert outputs["omitted"] is True
        assert outputs["value"] is None
        assert len(outputs["preview"]) <= outputs["max_json_chars"]
        assert outputs["sha256"]
        assert outputs["json_chars"] > outputs["max_json_chars"]
    finally:
        shutil.rmtree(d)


def test_malformed_evaluator_program_output_is_rejected():
    p, d = _problem(
        "def evaluate(c):\n"
        "    return {'score': 1.0, 'is_valid': True, 'program_output': ('tuple', 1)}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "malformed_metrics"
        assert result.metadata["malformed_metrics"]["reason"] == "malformed_outputs"
        assert "must use list, not tuple" in result.metadata["malformed_metrics"]["message"]
    finally:
        shutil.rmtree(d)


def test_evaluator_rejects_duplicate_program_output_channels():
    p, d = _problem(
        "def evaluate(c):\n"
        "    return {'score': 1.0, 'is_valid': True, 'program_output': {'a': 1}, 'outputs': {'b': 2}}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)

        assert result.error == "malformed_metrics"
        assert result.metadata["malformed_metrics"]["reason"] == "malformed_outputs"
        assert "either 'outputs' or 'program_output'" in result.metadata["malformed_metrics"]["message"]
    finally:
        shutil.rmtree(d)


def test_configured_stage_key_safety_applies_to_samples_and_retries():
    metrics = [{"name": "true", "primary": True, "bounds": [0.0, 1.0]}]
    p, d = _problem(
        "def evaluate(c): return {'true': 1.0, 'is_valid': True}\n",
        metrics=metrics,
    )
    (d / "stage_validate.py").write_text(
        "def evaluate(code, workspace, stage):\n"
        "    return {True: 0.0, 'true': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "gate",
                    "validate_path": "stage_validate.py",
                    "samples": 2,
                    "retries": 1,
                }
            ],
        ).evaluate("x=1", None)
        assert result.error == "malformed_metrics"
        assert result.metadata["sample_count"] == 2
        assert len(result.metadata["samples"]) == 2
        for sample in result.metadata["samples"]:
            sample_meta = sample["metadata"]
            assert sample_meta["attempt_count"] == 2
            assert sample_meta["malformed_metrics"]["reason"] == "non_string_keys"
            assert "non_string_key_types=bool" in sample_meta["malformed_metrics"]["message"]
            assert [attempt["error"] for attempt in sample_meta["attempts"]] == [
                "malformed_metrics",
                "malformed_metrics",
            ]
    finally:
        shutil.rmtree(d)


def test_validator_environment_hides_provider_keys_by_default(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj_hiddenvalidatorsecret123456")
    p, d = _problem(
        "import os\n"
        "def evaluate(c):\n"
        "    visible = os.getenv('OPENAI_API_KEY') is not None\n"
        "    return {'score': 0.0 if visible else 1.0, 'is_valid': not visible}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result == 1.0
        env_meta = result.metadata["validator_env"]
        assert env_meta["policy"] == "minimal_allowlist"
        assert "OPENAI_API_KEY" not in env_meta["provided_keys"]
    finally:
        shutil.rmtree(d)


def test_validator_boundary_declares_host_network_not_sandboxed():
    p, d = _problem("def evaluate(c):\n    return {'score': 1.0, 'is_valid': True}\n")
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        boundary = result.metadata["validator_boundary"]

        assert boundary["policy"] == "local_subprocess_boundary_v1"
        assert boundary["network_policy"] == "host"
        assert boundary["security_sandbox"] == "unsupported"
        assert boundary["container"] == "unsupported"
        assert boundary["network_egress"] == "host_inherited_not_sandboxed"
        assert boundary["network_denial"] == "unsupported"
        assert boundary["filesystem_capabilities"]["schema"] == (
            "libreevolve.validator_filesystem_capabilities.v1"
        )
        assert boundary["filesystem_capabilities"]["cwd"] == {
            "path": "materialized_candidate_root",
            "read": True,
            "write": True,
            "execute": True,
            "lifetime": "temporary_per_attempt",
        }
        assert boundary["filesystem_capabilities"]["declared_problem_files"][
            "undeclared_problem_local_reads"
        ] == "python_open_and_import_checks_denied"
        assert boundary["filesystem_capabilities"]["host_filesystem"] == {
            "os_sandbox": "unsupported",
            "ambient_access_possible": True,
            "undeclared_host_paths": "not_capability_enforced",
        }
        assert boundary["resource_limits"]["wall_clock_timeout"] == (
            "configured_stage_or_sample_timeout"
        )
        assert boundary["resource_limits"]["memory"] == "unsupported"
        assert boundary["resource_limit_policy"]["schema"] == (
            "libreevolve.validator_resource_limit_policy.v1"
        )
        assert boundary["resource_limit_policy"]["wall_clock_timeout"][
            "supported"
        ] is True
        assert boundary["resource_limit_policy"]["memory"] == {
            "supported": False,
            "quota": "unsupported",
        }
        assert boundary["resource_limit_policy"]["container_runtime_limits"] == (
            "unsupported"
        )
        assert boundary["secret_boundary"] == (
            "minimal_environment_allowlist_with_redacted_diagnostics"
        )
    finally:
        shutil.rmtree(d)


def test_validator_network_deny_blocks_python_socket_calls():
    p, d = _problem(
        "import socket\n"
        "def evaluate(c):\n"
        "    try:\n"
        "        socket.socket()\n"
        "    except OSError:\n"
        "        return {'score': 1.0, 'is_valid': True}\n"
        "    return {'score': 0.0, 'is_valid': False}\n"
    )
    try:
        result = CascadeEvaluator(p, validator_network_policy="deny").evaluate("x=1", None)
        boundary = result.metadata["validator_boundary"]

        assert result == 1.0
        assert boundary["network_policy"] == "deny"
        assert boundary["network_egress"] == "python_socket_denied_not_os_sandbox"
        assert boundary["network_denial"] == "python_socket_monkeypatch"
        assert boundary["network_denial_scope"] == (
            "python_socket_api_only_not_kernel_or_container"
        )
        assert boundary["security_sandbox"] == "unsupported"
        assert boundary["resource_limit_policy"]["gpu"]["supported"] is False
    finally:
        shutil.rmtree(d)


def test_validator_network_deny_applies_during_preflight_import():
    p, d = _problem(
        "import socket\n"
        "socket.socket()\n"
        "def evaluate(c):\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        with pytest.raises(ValueError, match="validator network egress denied"):
            CascadeEvaluator(p, validator_network_policy="deny").evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_validator_environment_allows_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("BENCHMARK_DATA_DIR", "fixtures")
    p, d = _problem(
        "import os\n"
        "def evaluate(c):\n"
        "    ok = os.getenv('BENCHMARK_DATA_DIR') == 'fixtures'\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    try:
        result = CascadeEvaluator(
            p, validator_env_allowlist=["BENCHMARK_DATA_DIR"]
        ).evaluate("x=1", None)
        assert result == 1.0
        env_meta = result.metadata["validator_env"]
        assert env_meta["allowlist"] == ["BENCHMARK_DATA_DIR"]
        assert "BENCHMARK_DATA_DIR" in env_meta["provided_keys"]
    finally:
        shutil.rmtree(d)


def test_validator_environment_canonicalizes_direct_allowlist(monkeypatch):
    monkeypatch.setenv("BENCHMARK_DATA_DIR", "fixtures")
    p, d = _problem(
        "import os\n"
        "def evaluate(c):\n"
        "    ok = os.getenv('BENCHMARK_DATA_DIR') == 'fixtures'\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    try:
        result = CascadeEvaluator(
            p, validator_env_allowlist=[" benchmark_data_dir ", "BENCHMARK_DATA_DIR"]
        ).evaluate("x=1", None)
        assert result == 1.0
        env_meta = result.metadata["validator_env"]
        assert env_meta["allowlist"] == ["BENCHMARK_DATA_DIR"]
        assert "BENCHMARK_DATA_DIR" in env_meta["provided_keys"]
    finally:
        shutil.rmtree(d)


def test_validator_environment_rejects_unsafe_direct_allowlist():
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}\n")
    try:
        with pytest.raises(ValueError, match="manifest-safe environment variable"):
            CascadeEvaluator(p, validator_env_allowlist=["BAD\nNAME"])
        with pytest.raises(ValueError, match="validator_env_allowlist"):
            CascadeEvaluator(p, validator_env_allowlist="PATH")
    finally:
        shutil.rmtree(d)


def test_validator_stdout_and_stderr_redact_secret_like_values():
    token = "sk-" + "proj-" + "validatorvalue1234567890"
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        f"    print('api_key={token}')\n"
        f"    print('token: {token}', file=sys.stderr)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result == 1.0
        assert token not in result.stdout
        assert token not in result.stderr
        assert "[REDACTED]" in result.stdout
        assert "[REDACTED]" in result.stderr
    finally:
        shutil.rmtree(d)


def test_validator_stdout_and_stderr_are_truncated_with_metadata():
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    print('o' * 200)\n"
        "    print('e' * 160, file=sys.stderr)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p, output_max_chars=40).evaluate("x=1", None)
        assert result.is_valid is True
        assert len(result.stdout) == 40
        assert len(result.stderr) == 40
        assert result.stdout.endswith("...<truncated>")
        assert result.stderr.endswith("...<truncated>")
        assert result.stages[-1].stdout == result.stdout
        assert result.stages[-1].stderr == result.stderr
        diag = result.metadata["diagnostic_output"]
        assert diag["policy"] == "decode_utf8_replace_then_redact_then_truncate"
        assert diag["max_chars"] == 40
        assert diag["stdout"]["truncated"] is True
        assert diag["stderr"]["truncated"] is True
        assert diag["stdout"]["stored_chars"] == 40
        assert diag["stderr"]["stored_chars"] == 40
    finally:
        shutil.rmtree(d)


def test_validator_stdout_and_stderr_use_default_persisted_output_cap():
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    print('o' * 50000)\n"
        "    print('e' * 50000, file=sys.stderr)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.is_valid is True
        assert len(result.stdout) == 20000
        assert len(result.stderr) == 20000
        assert result.stages[-1].stdout == result.stdout
        assert result.stages[-1].stderr == result.stderr
        diag = result.metadata["diagnostic_output"]
        assert diag["max_chars"] == 20000
        assert diag["stdout"]["truncated"] is True
        assert diag["stderr"]["truncated"] is True
        assert diag["stdout"]["stored_chars"] == 20000
        assert diag["stderr"]["stored_chars"] == 20000
        assert diag["stdout"]["redacted_chars"] > diag["stdout"]["stored_chars"]
        assert diag["stderr"]["redacted_chars"] > diag["stderr"]["stored_chars"]
        assert diag["stdout"]["omitted_chars"] > 0
        assert diag["stderr"]["omitted_chars"] > 0
    finally:
        shutil.rmtree(d)


def test_validator_output_redacts_before_truncating():
    token = "sk-" + "proj-" + "stdoutcapsecret1234567890"
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        f"    print({('prefix ' + token + ' suffix ' + 'x' * 80)!r})\n"
        f"    print({('err ' + token + ' tail ' + 'y' * 80)!r}, file=sys.stderr)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p, output_max_chars=55).evaluate("x=1", None)
        assert token not in result.stdout
        assert token not in result.stderr
        assert "[REDACTED]" in result.stdout
        assert "[REDACTED]" in result.stderr
        assert result.metadata["diagnostic_output"]["stdout"]["redacted"] is True
        assert result.metadata["diagnostic_output"]["stderr"]["redacted"] is True
        assert result.metadata["diagnostic_output"]["stdout"]["truncated"] is True
    finally:
        shutil.rmtree(d)


def test_validator_stdout_and_stderr_decode_invalid_utf8_with_metadata():
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    sys.stdout.buffer.write(b'out-\\xff\\xfe\\xfa\\n')\n"
        "    sys.stderr.buffer.write(b'err-\\xff\\n')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.is_valid is True
        assert "out-" in result.stdout
        assert "err-" in result.stderr
        assert "\ufffd" in result.stdout
        assert "\ufffd" in result.stderr
        assert result.stages[-1].stdout == result.stdout
        assert result.stages[-1].stderr == result.stderr
        decoding = result.metadata["diagnostic_output"]["stream_decoding"]
        assert decoding["policy"] == "utf-8_replace"
        assert decoding["stdout"]["source"] == "bytes"
        assert decoding["stdout"]["byte_count"] == len(b"out-\xff\xfe\xfa\n")
        assert decoding["stdout"]["malformed"] is True
        assert decoding["stdout"]["replacement_chars"] == 3
        assert decoding["stderr"]["byte_count"] == len(b"err-\xff\n")
        assert decoding["stderr"]["malformed"] is True
        assert decoding["stderr"]["replacement_chars"] == 1
    finally:
        shutil.rmtree(d)


def test_timeout_stdout_decode_invalid_utf8_with_metadata():
    p, d = _problem(
        "import sys, time\n"
        "def evaluate(c):\n"
        "    sys.stdout.buffer.write(b'timeout-\\xff\\n')\n"
        "    sys.stdout.flush()\n"
        "    time.sleep(30)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p, timeout_sec=0.3).evaluate("x=1", None)
        assert result.error == "timeout"
        assert "timeout-" in result.stdout
        assert "\ufffd" in result.stdout
        decoding = result.metadata["diagnostic_output"]["stream_decoding"]
        assert decoding["stdout"]["source"] == "bytes"
        assert decoding["stdout"]["malformed"] is True
        assert decoding["stdout"]["replacement_chars"] == 1
        assert result.metadata["timeout_cleanup"]["attempted"] is True
    finally:
        shutil.rmtree(d)


def test_validator_input_receives_eof_from_devnull_with_metadata():
    p, d = _problem(
        "def evaluate(c):\n"
        "    try:\n"
        "        input('enter value: ')\n"
        "    except EOFError:\n"
        "        return {'score': 1.0, 'is_valid': True}\n"
        "    return {'score': 0.0, 'is_valid': False}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.is_valid is True
        assert "enter value:" in result.stdout
        assert result.metadata["stdin"] == {
            "policy": "devnull",
            "interactive_input": "unsupported",
            "generated_input": "unsupported",
        }
        assert result.stages[-1].metadata == {}
    finally:
        shutil.rmtree(d)


def test_validator_stdin_read_is_empty_with_devnull_policy():
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    data = sys.stdin.read()\n"
        "    return {'score': 1.0 if data == '' else 0.0, 'is_valid': data == ''}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.is_valid is True
        assert result.metadata["stdin"]["policy"] == "devnull"
        assert result.metadata["stdin"]["generated_input"] == "unsupported"
    finally:
        shutil.rmtree(d)


def test_validator_receives_configured_stdin_text_with_hash_metadata():
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    data = sys.stdin.read()\n"
        "    return {'score': 1.0 if data == 'ready\\n' else 0.0, 'is_valid': data == 'ready\\n'}\n"
    )
    try:
        result = CascadeEvaluator(p, stdin_text="ready\n").evaluate("x=1", None)
        stdin = result.metadata["stdin"]

        assert result.is_valid is True
        assert stdin["policy"] == "configured_text"
        assert stdin["interactive_input"] == "fixture_text"
        assert stdin["generated_input"] == "unsupported"
        assert stdin["encoding"] == "utf-8"
        assert stdin["chars"] == len("ready\n")
        assert stdin["bytes"] == len("ready\n".encode("utf-8"))
        assert stdin["sha256"] == hashlib.sha256(b"ready\n").hexdigest()
        assert stdin["text_retained"] is False
        assert "ready" not in json.dumps(stdin)
    finally:
        shutil.rmtree(d)


def test_validator_configured_stdin_metadata_redacts_without_retaining_text():
    secret = "sk-proj_stdin_secret_1234567890"  # pragma: allowlist secret
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    data = sys.stdin.read()\n"
        "    return {'score': 1.0 if data else 0.0, 'is_valid': bool(data)}\n"
    )
    try:
        result = CascadeEvaluator(p, stdin_text=secret).evaluate("x=1", None)
        stdin = result.metadata["stdin"]

        assert result.is_valid is True
        assert stdin["policy"] == "configured_text"
        assert stdin["redacted"] is True
        assert secret not in json.dumps(result.metadata)
    finally:
        shutil.rmtree(d)


def test_validator_receives_problem_local_stdin_file_with_file_metadata():
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        "    data = sys.stdin.read()\n"
        "    return {'score': 1.0 if data == 'file-input\\n' else 0.0, 'is_valid': data == 'file-input\\n'}\n"
    )
    (d / "stdin.txt").write_bytes(b"file-input\n")
    try:
        result = CascadeEvaluator(p, stdin_file="stdin.txt").evaluate("x=1", None)
        stdin = result.metadata["stdin"]

        assert result.is_valid is True
        assert stdin["policy"] == "configured_file"
        assert stdin["source"] == "problem_local_file"
        assert stdin["interactive_input"] == "fixture_text"
        assert stdin["generated_input"] == "unsupported"
        assert stdin["path"] == "stdin.txt"
        assert stdin["file_sha256"] == hashlib.sha256(b"file-input\n").hexdigest()
        assert stdin["sha256"] == hashlib.sha256(b"file-input\n").hexdigest()
        assert stdin["text_retained"] is False
        assert "file-input" not in json.dumps(stdin)
    finally:
        shutil.rmtree(d)


def test_validator_rejects_stdin_file_outside_problem_directory(tmp_path):
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}\n")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    try:
        with pytest.raises(ValueError, match="escapes problem directory"):
            CascadeEvaluator(p, stdin_file=outside).evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_validator_rejects_non_utf8_stdin_file():
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}\n")
    (d / "stdin.bin").write_bytes(b"\xff\xfe")
    try:
        with pytest.raises(ValueError, match="UTF-8 text"):
            CascadeEvaluator(p, stdin_file="stdin.bin").evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_configured_stage_attempts_record_devnull_stdin_policy():
    p, d = _problem(
        "import sys\n"
        "def evaluate(c, workspace, stage):\n"
        "    data = sys.stdin.read()\n"
        "    return {'score': 1.0 if data == '' else 0.0, 'is_valid': data == ''}\n"
    )
    try:
        ev = CascadeEvaluator(
            p,
            stages=[{"name": "stdin_stage", "samples": 2, "retries": 1}],
        )
        result = ev.evaluate("x=1", None)
        assert result.is_valid is True
        sample = result.metadata["samples"][0]
        assert sample["metadata"]["stdin"]["policy"] == "devnull"
        assert sample["metadata"]["stdin"]["interactive_input"] == "unsupported"
    finally:
        shutil.rmtree(d)


def test_configured_stage_stdin_text_overrides_default_without_metadata_leak():
    secret = "sk-proj_stage_stdin_secret_1234567890"  # pragma: allowlist secret
    p, d = _problem(
        "import sys\n"
        "def evaluate(c, workspace, stage):\n"
        "    data = sys.stdin.read()\n"
        "    config = stage['config']\n"
        "    leaked = 'stdin_text' in config or 'sk-proj_stage' in repr(config)\n"
        "    return {'score': 1.0 if data.startswith('sk-proj_stage') and not leaked else 0.0, 'is_valid': data.startswith('sk-proj_stage') and not leaked}\n"
    )
    try:
        ev = CascadeEvaluator(
            p,
            stdin_text="default-value",
            stages=[
                {
                    "name": "stdin_stage",
                    "stdin_text": secret,
                }
            ],
        )
        result = ev.evaluate("x=1", None)
        metadata_text = json.dumps(result.metadata)

        assert result.is_valid is True
        assert result.metadata["stdin"]["policy"] == "configured_text"
        assert result.metadata["stage"]["config"]["stdin"]["policy"] == "configured_text"
        assert "stdin_text" not in metadata_text
        assert secret not in metadata_text
    finally:
        shutil.rmtree(d)


def test_configured_stage_stdin_file_overrides_default_without_metadata_leak():
    p, d = _problem(
        "import sys\n"
        "def evaluate(c, workspace, stage):\n"
        "    data = sys.stdin.read()\n"
        "    config = stage['config']\n"
        "    leaked = 'stdin_file' in config or 'stage-stdin' in repr(config)\n"
        "    return {'score': 1.0 if data == 'stage-stdin' and not leaked else 0.0, 'is_valid': data == 'stage-stdin' and not leaked}\n"
    )
    (d / "stage-input.txt").write_bytes(b"stage-stdin")
    try:
        ev = CascadeEvaluator(
            p,
            stdin_text="default-value",
            stages=[{"name": "stdin_stage", "stdin_file": "stage-input.txt"}],
        )
        result = ev.evaluate("x=1", None)
        metadata_text = json.dumps(result.metadata)

        assert result.is_valid is True
        assert result.metadata["stdin"]["policy"] == "configured_file"
        assert result.metadata["stage"]["config"]["stdin"]["path"] == "stage-input.txt"
        assert "stdin_file" not in metadata_text
        assert "stage-stdin" not in metadata_text
    finally:
        shutil.rmtree(d)


def test_validator_artifacts_are_copied_hashed_and_retained(tmp_path):
    artifact_dir = tmp_path / "artifacts"
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace):\n"
        "    Path(workspace, 'report.json').write_text('{\"ok\": true}', encoding='utf-8')\n"
        "    Path(workspace, 'logs').mkdir()\n"
        "    Path(workspace, 'logs', 'trace.txt').write_text('trace', encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            artifact_dir=artifact_dir,
            artifact_include=["*.json", "logs/*.txt"],
        ).evaluate("x=1", None)
        artifacts = result.metadata["artifacts"]
        assert result == 1.0
        assert artifacts["enabled"] is True
        assert artifacts["total_bytes"] == len('{"ok": true}') + len("trace")
        copied = {record["path"]: record for record in artifacts["files"]}
        assert sorted(copied) == ["logs/trace.txt", "report.json"]
        report_path = tmp_path / copied["report.json"]["artifact_path"]
        trace_path = tmp_path / copied["logs/trace.txt"]["artifact_path"]
        assert report_path.read_text(encoding="utf-8") == '{"ok": true}'
        assert trace_path.read_text(encoding="utf-8") == "trace"
        assert copied["report.json"]["sha256"] == hashlib.sha256(b'{"ok": true}').hexdigest()
        assert copied["report.json"]["redacted"] is False
        assert copied["report.json"]["redaction_status"] == "unchanged"
        assert copied["report.json"]["content_excerpt_policy"] == (
            "stored_utf8_artifact_excerpt_v1"
        )
        assert copied["report.json"]["content_excerpt_status"] == "included"
        assert copied["report.json"]["content_excerpt"] == '{"ok": true}'
        assert copied["report.json"]["content_excerpt_truncated"] is False
        assert copied["report.json"]["stage_name"] == "validate"
    finally:
        shutil.rmtree(d)


def test_validator_artifact_collection_honors_exclude_and_limits(tmp_path):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace):\n"
        "    Path(workspace, 'a.txt').write_text('aaa', encoding='utf-8')\n"
        "    Path(workspace, 'b.txt').write_text('bbbb', encoding='utf-8')\n"
        "    Path(workspace, 'secret.txt').write_text('skip', encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "artifacts",
            artifact_include=["*.txt"],
            artifact_exclude=["secret.txt"],
            artifact_max_files=1,
            artifact_max_bytes=10,
        ).evaluate("x=1", None)
        artifacts = result.metadata["artifacts"]
        assert [record["path"] for record in artifacts["files"]] == ["a.txt"]
        assert artifacts["skipped"] == [{"path": "b.txt", "reason": "max_files"}]
        assert not (tmp_path / "artifacts" / artifacts["collection_id"] / "secret.txt").exists()
    finally:
        shutil.rmtree(d)


def test_validator_artifact_globs_are_path_segment_aware(tmp_path):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace):\n"
        "    Path(workspace, 'top.txt').write_text('top', encoding='utf-8')\n"
        "    Path(workspace, 'nested').mkdir()\n"
        "    Path(workspace, 'nested', 'deep.txt').write_text('deep', encoding='utf-8')\n"
        "    Path(workspace, 'nested', 'note.md').write_text('note', encoding='utf-8')\n"
        "    Path(workspace, 'nested', 'deeper').mkdir()\n"
        "    Path(workspace, 'nested', 'deeper', 'trace.txt').write_text('trace', encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        root_only = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "root_artifacts",
            artifact_include=["*.txt"],
        ).evaluate("x=1", None)
        assert [record["path"] for record in root_only.metadata["artifacts"]["files"]] == ["top.txt"]

        one_segment = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "one_segment_artifacts",
            artifact_include=["nested/*.txt"],
        ).evaluate("x=1", None)
        assert [record["path"] for record in one_segment.metadata["artifacts"]["files"]] == [
            "nested/deep.txt",
        ]

        recursive = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "recursive_artifacts",
            artifact_include=["**/*.txt"],
            artifact_exclude=["nested/*.txt"],
        ).evaluate("x=1", None)
        assert [record["path"] for record in recursive.metadata["artifacts"]["files"]] == [
            "nested/deeper/trace.txt",
            "top.txt",
        ]
    finally:
        shutil.rmtree(d)


def test_validator_artifact_max_bytes_prechecks_before_reading(tmp_path, monkeypatch):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace):\n"
        "    Path(workspace, 'small.txt').write_text('ok', encoding='utf-8')\n"
        "    Path(workspace, 'too_big.txt').write_text('x' * 100, encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    original_read_bytes = Path.read_bytes

    def guarded_read_bytes(path):
        if path.name == "too_big.txt":
            raise AssertionError("oversized artifact should be skipped before read_bytes")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)
    try:
        result = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "artifacts",
            artifact_include=["*.txt"],
            artifact_max_bytes=10,
        ).evaluate("x=1", None)
        artifacts = result.metadata["artifacts"]
        assert [record["path"] for record in artifacts["files"]] == ["small.txt"]
        assert artifacts["skipped"] == [
            {"path": "too_big.txt", "reason": "max_bytes", "source_bytes": 100},
        ]
        assert artifacts["byte_limit_policy"] == "precheck_source_size_then_store"
    finally:
        shutil.rmtree(d)


def test_validator_artifact_collection_skips_file_symlinks(tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    p, d = _problem(
        "from pathlib import Path\n"
        "import os\n"
        "def evaluate(c, workspace):\n"
        f"    os.symlink({str(outside)!r}, Path(workspace, 'linked.txt'))\n"
        "    Path(workspace, 'real.txt').write_text('real', encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "artifacts",
            artifact_include=["*.txt"],
        ).evaluate("x=1", None)
        if result.error == "subprocess_error" and "WinError 1314" in result.stderr:
            pytest.skip("symlink creation is unavailable")
    except NotImplementedError:
        shutil.rmtree(d)
        pytest.skip("symlink creation is unavailable")

    try:
        artifacts = result.metadata["artifacts"]
        assert [record["path"] for record in artifacts["files"]] == ["real.txt"]
        assert {"path": "linked.txt", "reason": "link_not_followed"} in artifacts["skipped"]
        assert not (tmp_path / "artifacts" / artifacts["collection_id"] / "linked.txt").exists()
    finally:
        shutil.rmtree(d)


def test_validator_artifact_metadata_defines_custom_artifact_root(tmp_path):
    artifact_dir = tmp_path / "run" / "nested" / "eval_artifacts"
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace):\n"
        "    Path(workspace, 'report.txt').write_text('report', encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            artifact_dir=artifact_dir,
            artifact_include=["*.txt"],
        ).evaluate("x=1", None)
        artifacts = result.metadata["artifacts"]
        artifact = artifacts["files"][0]

        assert artifacts["path_root"] == "artifact_dir_parent"
        assert artifacts["artifact_dir_name"] == "eval_artifacts"
        assert artifact["artifact_path_root"] == "artifact_dir_parent"
        assert artifact["artifact_path"].startswith("eval_artifacts/")
        assert artifact["artifact_relative_path"].endswith("/report.txt")
        assert (artifact_dir.parent / artifact["artifact_path"]).read_text(encoding="utf-8") == "report"
        assert (artifact_dir / artifact["artifact_relative_path"]).read_text(encoding="utf-8") == "report"
    finally:
        shutil.rmtree(d)


def test_configured_stage_overrides_artifact_policy(tmp_path):
    artifact_dir = tmp_path / "artifacts"
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace, stage):\n"
        "    Path(workspace, 'global.json').write_text('global', encoding='utf-8')\n"
        "    Path(workspace, 'stage.txt').write_text(stage['name'], encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "hard",
                    "artifact_include": ["*.txt"],
                    "artifact_max_files": 1,
                }
            ],
            artifact_dir=artifact_dir,
            artifact_include=["*.json"],
        ).evaluate("x=1", None)
        artifacts = result.metadata["artifacts"]
        assert [record["path"] for record in artifacts["files"]] == ["stage.txt"]
        assert artifacts["include"] == ["*.txt"]
        assert artifacts["max_files"] == 1
        copied = tmp_path / artifacts["files"][0]["artifact_path"]
        assert copied.read_text(encoding="utf-8") == "hard"
        assert not any(artifact_dir.rglob("global.json"))
    finally:
        shutil.rmtree(d)


def test_validator_text_artifacts_redact_secret_like_values_by_default(tmp_path):
    token = "sk-" + "proj-" + "artifactvalue1234567890"
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace):\n"
        f"    Path(workspace, 'secret.txt').write_text('token={token}', encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "artifacts",
            artifact_include=["*.txt"],
        ).evaluate("x=1", None)
        artifact = result.metadata["artifacts"]["files"][0]
        copied = tmp_path / artifact["artifact_path"]
        assert token not in copied.read_text(encoding="utf-8")
        assert "[REDACTED]" in copied.read_text(encoding="utf-8")
        assert artifact["redacted"] is True
        assert artifact["redaction_status"] == "redacted"
        assert artifact["source_bytes"] > artifact["bytes"]
        assert artifact["sha256"] == hashlib.sha256(copied.read_bytes()).hexdigest()
        assert artifact["content_excerpt"] == "token=[REDACTED]"
        assert token not in artifact["content_excerpt"]
    finally:
        shutil.rmtree(d)


def test_validator_binary_artifact_records_no_prompt_excerpt(tmp_path):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace):\n"
        "    Path(workspace, 'image.bin').write_bytes(bytes([0xff, 0xfe, 0xfd]))\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "artifacts",
            artifact_include=["*.bin"],
        ).evaluate("x=1", None)
        artifact = result.metadata["artifacts"]["files"][0]
        assert artifact["content_excerpt_policy"] == "stored_utf8_artifact_excerpt_v1"
        assert artifact["content_excerpt_status"] == "binary_or_non_utf8"
        assert "content_excerpt" not in artifact
    finally:
        shutil.rmtree(d)


def test_validator_text_artifacts_redact_bearer_credentials_by_default(tmp_path):
    secret = "hf_abcdefghijklmnopqrstuvwxyz1234567890"
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace):\n"
        f"    Path(workspace, 'auth.txt').write_text('Authorization: Bearer {secret}', encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            artifact_dir=tmp_path / "artifacts",
            artifact_include=["*.txt"],
        ).evaluate("x=1", None)
        artifact = result.metadata["artifacts"]["files"][0]
        copied = tmp_path / artifact["artifact_path"]
        stored = copied.read_text(encoding="utf-8")
        assert secret not in stored
        assert stored == "Authorization: Bearer [REDACTED]"
        assert artifact["redacted"] is True
        assert artifact["redaction_status"] == "redacted"
        assert artifact["sha256"] == hashlib.sha256(copied.read_bytes()).hexdigest()
    finally:
        shutil.rmtree(d)


def test_stage_artifact_redaction_can_be_disabled(tmp_path):
    token = "sk-" + "proj_" + "artifactraw1234567890"
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(c, workspace, stage):\n"
        f"    Path(workspace, 'raw.txt').write_text('token={token}', encoding='utf-8')\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "raw",
                    "artifact_include": ["*.txt"],
                    "artifact_redact_secrets": False,
                }
            ],
            artifact_dir=tmp_path / "artifacts",
        ).evaluate("x=1", None)
        artifact = result.metadata["artifacts"]["files"][0]
        copied = tmp_path / artifact["artifact_path"]
        assert token in copied.read_text(encoding="utf-8")
        assert artifact["redacted"] is False
        assert artifact["redaction_status"] == "disabled"
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("validate_src", "message", "reason"),
    [
        (
            "def evaluate(c): return {'score': 1.0}",
            "missing declared metrics",
            "missing_declared_metrics",
        ),
        (
            "def evaluate(c): return {'score': 1.0, 'is_valid': True, 'extra': 3}",
            "undeclared metrics",
            "undeclared_metrics",
        ),
        (
            "def evaluate(c): return {'score': 'good', 'is_valid': True}",
            "must be numeric",
            "invalid_metric_type",
        ),
        (
            "def evaluate(c): return {'score': float('nan'), 'is_valid': True}",
            "Out of range float values",
            "not_json_serializable",
        ),
        (
            "def evaluate(c): return {'score': 1.0, 'is_valid': 1}",
            "is_valid",
            "invalid_is_valid",
        ),
    ],
)
def test_rejects_malformed_metric_contract(validate_src, message, reason):
    p, d = _problem(validate_src)
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result == -0.2
        assert result.error == "malformed_metrics"
        assert result.stages[-1].error == "malformed_metrics"
        assert result.metadata["malformed_metrics"]["reason"] == reason
        assert message in result.metadata["malformed_metrics"]["message"]
    finally:
        shutil.rmtree(d)


def test_rejects_missing_declared_secondary_metric():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "runtime", "primary": False, "bounds": [0.0, 10.0]},
    ]
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}", metrics=metrics)
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.error == "malformed_metrics"
        assert result.metadata["malformed_metrics"]["reason"] == "missing_declared_metrics"
        assert "missing declared metrics" in result.metadata["malformed_metrics"]["message"]
        assert "runtime" in result.metadata["malformed_metrics"]["message"]
    finally:
        shutil.rmtree(d)


def test_final_fitness_source_metric_is_not_required_from_evaluator_output():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {
            "name": "final_quality",
            "primary": False,
            "direction": "minimize",
            "bounds": [0.0, 100.0],
            "source": "final_fitness",
        },
    ]
    p, d = _problem("def evaluate(c): return {'score': 0.8, 'is_valid': True}", metrics=metrics)
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.error is None
        assert result.metrics == {"score": 0.8, "is_valid": True}
    finally:
        shutil.rmtree(d)


def test_rejects_final_fitness_source_metric_returned_by_evaluator():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {
            "name": "final_quality",
            "primary": False,
            "direction": "minimize",
            "bounds": [0.0, 100.0],
            "source": "final_fitness",
        },
    ]
    p, d = _problem(
        "def evaluate(c): return {'score': 0.8, 'final_quality': 25.0, 'is_valid': True}",
        metrics=metrics,
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.error == "malformed_metrics"
        assert result.metadata["malformed_metrics"]["reason"] == "undeclared_metrics"
        assert "final_quality" in result.metadata["malformed_metrics"]["message"]
    finally:
        shutil.rmtree(d)


def test_records_out_of_bounds_metric_diagnostics():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "runtime", "primary": False, "direction": "minimize", "bounds": [0.0, 10.0]},
    ]
    p, d = _problem(
        "def evaluate(c): return {'score': 999, 'runtime': -5, 'is_valid': True}",
        metrics=metrics,
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.is_valid is True
        assert result.fitness == 1.0
        diagnostics = result.metadata["metric_bound_diagnostics"]
        assert diagnostics == [
            {
                "metric": "score",
                "value": 999.0,
                "bounds": [0.0, 1.0],
                "direction": "maximize",
                "normalized": 1.0,
                "clamped": True,
            },
            {
                "metric": "runtime",
                "value": -5.0,
                "bounds": [0.0, 10.0],
                "direction": "minimize",
                "normalized": 1.0,
                "clamped": True,
            },
        ]
    finally:
        shutil.rmtree(d)


def test_records_out_of_bounds_diagnostics_for_staged_samples():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[{"name": "sampled", "samples": 2, "seeds": [2.0, 3.0]}],
        ).evaluate("x=1", None)
        assert result.is_valid is True
        assert result.metadata["metric_bound_diagnostics"][0]["value"] == 2.5
        samples = result.metadata["samples"]
        assert samples[0]["metadata"]["metric_bound_diagnostics"][0]["value"] == 2.0
        assert samples[1]["metadata"]["metric_bound_diagnostics"][0]["value"] == 3.0
    finally:
        shutil.rmtree(d)


def test_configured_stage_metric_aggregation_can_use_worst_primary_metric():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "sampled",
                    "samples": 2,
                    "seeds": [1.0, 0.2],
                    "metric_aggregation": {"score": "min"},
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.metrics["score"] == 0.2
        assert result.fitness == 0.2
        assert result.metadata["metric_aggregation"] == {"score": "min"}
    finally:
        shutil.rmtree(d)


def test_configured_stage_hypothesis_test_can_promote_repeated_samples():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "stat_gate",
                    "samples": 3,
                    "seeds": [0.8, 0.85, 0.9],
                    "min_score": 0.7,
                    "hypothesis_test": {
                        "type": "one_sided_lower_confidence_bound",
                        "metric": "score",
                        "min": 0.7,
                        "confidence": 0.8,
                        "min_samples": 3,
                        "error_budget": {
                            "max_false_promotion_rate": 0.25,
                            "max_false_rejection_rate": 0.05,
                            "min_effect_size": 0.2,
                        },
                    },
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        stage = result.metadata["configured_stage_results"][0]
        hypothesis = stage["hypothesis_test_result"]
        assert stage["passed"] is True
        assert hypothesis["configured"] is True
        assert hypothesis["test_name"] == "one_sided_lower_confidence_bound"
        assert hypothesis["sample_count"] == 3
        assert hypothesis["observations"] == [
            {"sample_index": 0, "value": 0.8},
            {"sample_index": 1, "value": 0.85},
            {"sample_index": 2, "value": 0.9},
        ]
        assert hypothesis["lower_bound"] >= 0.7
        assert 0.0 <= hypothesis["p_value"] <= 1.0
        assert hypothesis["confidence_interval"]["kind"] == "one_sided_lower"
        assert hypothesis["error_budget"]["configured"] is True
        assert hypothesis["error_budget"]["passed"] is True
        assert hypothesis["error_budget"]["false_promotion"] == {
            "configured": True,
            "max_rate": 0.25,
            "estimated_rate": pytest.approx(0.2),
            "passed": True,
            "basis": "one_sided_confidence_level",
        }
        assert hypothesis["error_budget"]["false_rejection"]["configured"] is True
        assert hypothesis["error_budget"]["false_rejection"]["passed"] is True
        assert hypothesis["error_budget"]["false_rejection"]["max_rate"] == 0.05
        assert hypothesis["error_budget"]["false_rejection"]["min_effect_size"] == 0.2
    finally:
        shutil.rmtree(d)


def test_configured_stage_hypothesis_test_rejects_noisy_samples():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "stat_gate",
                    "samples": 3,
                    "seeds": [0.6, 0.8, 1.0],
                    "min_score": 0.5,
                    "hypothesis_test": {
                        "type": "one_sided_lower_confidence_bound",
                        "metric": "score",
                        "min": 0.7,
                        "confidence": 0.95,
                        "min_samples": 3,
                    },
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "hypothesis_test_not_met"
        stage = result.metadata["configured_stage_results"][0]
        hypothesis = stage["hypothesis_test_result"]
        assert stage["threshold_passed"] is True
        assert stage["passed"] is False
        assert hypothesis["passed"] is False
        assert hypothesis["reason"] == "lower_confidence_bound_below_min"
        assert hypothesis["mean"] == pytest.approx(0.8)
        assert hypothesis["lower_bound"] < 0.7
    finally:
        shutil.rmtree(d)


def test_configured_stage_hypothesis_test_can_stop_samples_early():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "stat_gate",
                    "samples": 5,
                    "seeds": [0.9, 0.92, 0.94, 0.1, 0.1],
                    "hypothesis_test": {
                        "type": "one_sided_lower_confidence_bound",
                        "metric": "score",
                        "min": 0.8,
                        "confidence": 0.8,
                        "min_samples": 3,
                        "sequential_stopping": True,
                    },
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.metadata["sample_count"] == 3
        assert result.metadata["planned_sample_count"] == 5
        decision = result.metadata["hypothesis_test_sequential_stopping"]
        assert decision["stopped_early"] is True
        assert decision["evaluated_samples"] == 3
        assert decision["planned_samples"] == 5
        stage = result.metadata["configured_stage_results"][0]
        hypothesis = stage["hypothesis_test_result"]
        assert hypothesis["passed"] is True
        assert hypothesis["sequential_stopping"] is True
        assert hypothesis["sequential_stop"] == {
            "enabled": True,
            "stopped_early": True,
            "stop_reason": "hypothesis_test_passed_after_min_samples",
            "evaluated_samples": 3,
            "planned_samples": 5,
        }
    finally:
        shutil.rmtree(d)


def test_configured_stage_binomial_hypothesis_test_can_promote_success_rate():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "success_gate",
                    "samples": 5,
                    "seeds": [1.0, 1.0, 1.0, 1.0, 0.0],
                    "hypothesis_test": {
                        "type": "binomial_success_rate",
                        "metric": "score",
                        "success_threshold": 0.5,
                        "min_success_rate": 0.5,
                        "confidence": 0.8,
                        "min_samples": 5,
                        "error_budget": {
                            "max_false_promotion_rate": 0.25,
                            "max_false_rejection_rate": 0.1,
                            "min_effect_size": 0.4,
                        },
                    },
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        stage = result.metadata["configured_stage_results"][0]
        hypothesis = stage["hypothesis_test_result"]
        assert hypothesis["test_name"] == "binomial_success_rate"
        assert hypothesis["passed"] is True
        assert hypothesis["success_count"] == 4
        assert hypothesis["failure_count"] == 1
        assert hypothesis["success_rate"] == 0.8
        assert hypothesis["lower_bound"] >= 0.5
        assert hypothesis["confidence_interval"]["kind"] == "one_sided_wilson_lower"
        assert 0.0 <= hypothesis["p_value"] <= 1.0
        assert hypothesis["error_budget"]["configured"] is True
        assert hypothesis["error_budget"]["passed"] is True
        assert hypothesis["error_budget"]["false_promotion"]["basis"] == (
            "one_sided_wilson_confidence_level"
        )
        assert hypothesis["error_budget"]["false_rejection"]["basis"] == (
            "exact_binomial_min_effect_size"
        )
    finally:
        shutil.rmtree(d)


def test_configured_stage_binomial_hypothesis_test_rejects_low_success_rate():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "success_gate",
                    "samples": 5,
                    "seeds": [1.0, 1.0, 0.0, 0.0, 0.0],
                    "hypothesis_test": {
                        "type": "binomial_success_rate",
                        "metric": "score",
                        "success_threshold": 0.5,
                        "min_success_rate": 0.5,
                        "confidence": 0.8,
                        "min_samples": 5,
                    },
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "hypothesis_test_not_met"
        stage = result.metadata["configured_stage_results"][0]
        hypothesis = stage["hypothesis_test_result"]
        assert hypothesis["passed"] is False
        assert hypothesis["success_count"] == 2
        assert hypothesis["reason"] == "success_rate_lower_bound_below_min"
        assert hypothesis["lower_bound"] < 0.5
    finally:
        shutil.rmtree(d)


def test_configured_stage_metric_aggregation_can_use_worst_minimized_metric():
    metrics = [
        {"name": "runtime", "primary": True, "bounds": [0.0, 10.0], "direction": "minimize"},
    ]
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'runtime': stage['seed'], 'is_valid': True}",
        metrics=metrics,
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "sampled",
                    "samples": 2,
                    "seeds": [0.0, 10.0],
                    "metric_aggregation": {"runtime": "max"},
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.metrics["runtime"] == 10.0
        assert result.fitness == 0.0
    finally:
        shutil.rmtree(d)


def test_configured_stage_metric_aggregation_can_use_quantile_primary_metric():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "sampled",
                    "samples": 5,
                    "seeds": [0.0, 0.25, 0.5, 0.75, 1.0],
                    "metric_aggregation": {
                        "score": {"policy": "quantile", "q": 0.75},
                    },
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.metrics["score"] == 0.75
        assert result.fitness == 0.75
        assert result.metadata["metric_aggregation"] == {
            "score": {"policy": "quantile", "q": 0.75}
        }
    finally:
        shutil.rmtree(d)


def test_configured_stage_metric_aggregation_quantile_interpolates():
    p, d = _problem(
        "def evaluate(code, workspace, stage): return {'score': stage['seed'], 'is_valid': True}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "sampled",
                    "samples": 3,
                    "seeds": [0.0, 0.5, 1.0],
                    "metric_aggregation": {
                        "score": {"policy": "quantile", "q": 0.25},
                    },
                }
            ],
        ).evaluate("x=1", None)

        assert result.metrics["score"] == 0.25
    finally:
        shutil.rmtree(d)


def test_configured_stage_metric_aggregation_keeps_boolean_all_policy():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    return {'score': 1.0, 'is_valid': stage['sample_index'] == 0}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "sampled",
                    "samples": 2,
                    "metric_aggregation": {"is_valid": "all"},
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is False
        assert result.metrics["is_valid"] is False
        assert result.metadata["metric_aggregation"] == {"is_valid": "all"}
    finally:
        shutil.rmtree(d)


def test_configured_stage_aggregate_stdout_stderr_are_truncated():
    p, d = _problem(
        "import sys\n"
        "def evaluate(code, workspace, stage):\n"
        "    print(f\"sample={stage['sample_index']} \" + 'o' * 80)\n"
        "    print(f\"err={stage['sample_index']} \" + 'e' * 80, file=sys.stderr)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[{"name": "sampled", "samples": 3}],
            output_max_chars=70,
        ).evaluate("x=1", None)
        assert result.is_valid is True
        assert len(result.stdout) == 70
        assert len(result.stderr) == 70
        assert result.metadata["diagnostic_output"]["policy"] == "aggregate_sample_outputs_then_truncate"
        assert result.metadata["diagnostic_output"]["stdout"]["truncated"] is True
        assert len(result.metadata["samples"]) == 3
        assert all(
            sample["metadata"]["diagnostic_output"]["stdout"]["stored_chars"] <= 70
            for sample in result.metadata["samples"]
        )
    finally:
        shutil.rmtree(d)


def test_configured_stage_threshold_stops_candidate():
    p, d = _problem("def evaluate(c): return {'score':0.2,'is_valid':True}")
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "small", "min_score": 0.5}])
        result = ev.evaluate("x=1", None)
        assert result.is_valid is False
        assert result.error == "stage_threshold_not_met"
        assert result.metadata["stopped_at"] == "small"
        stage_results = result.metadata["configured_stage_results"]
        assert len(stage_results) == 1
        assert stage_results[0]["name"] == "small"
        assert stage_results[0]["local_valid"] is True
        assert stage_results[0]["threshold"] == 0.5
        assert stage_results[0]["threshold_passed"] is False
        assert stage_results[0]["passed"] is False
        assert stage_results[0]["stop_reason"] == "stage_threshold_not_met"
        assert stage_results[0]["metadata"]["stage"]["name"] == "small"
    finally:
        shutil.rmtree(d)


def test_configured_stage_metric_threshold_stops_candidate():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "runtime", "bounds": [0.0, 10.0], "direction": "minimize"},
    ]
    p, d = _problem(
        "def evaluate(c): return {'score':0.9,'runtime':7.5,'is_valid':True}",
        metrics=metrics,
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "latency",
                    "metric_thresholds": {"runtime": {"max": 5.0}},
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "stage_threshold_not_met"
        assert result.metrics == {"score": 0.9, "runtime": 7.5, "is_valid": True}
        assert "synthetic_metrics" not in result.metadata
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["local_valid"] is True
        assert stage_result["threshold_passed"] is False
        assert stage_result["metric_thresholds"] == [
            {
                "metric": "runtime",
                "value": 7.5,
                "min": None,
                "max": 5.0,
                "passed": False,
                "reason": "above_max",
            }
        ]
        assert stage_result["threshold_result"]["passed"] is False
        assert result.metrics["is_valid"] is True
    finally:
        shutil.rmtree(d)


def test_configured_stage_requires_program_output():
    p, d = _problem("def evaluate(c): return {'score':0.9,'is_valid':True}")
    try:
        result = CascadeEvaluator(
            p,
            stages=[{"name": "output_gate", "require_program_output": True}],
        ).evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "stage_threshold_not_met"
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["threshold_passed"] is False
        assert stage_result["artifact_output_checks"] == [
            {
                "type": "program_output",
                "required": True,
                "present": False,
                "passed": False,
                "reason": "missing_or_omitted_program_output",
            }
        ]
    finally:
        shutil.rmtree(d)


def test_configured_stage_program_output_check_passes_when_output_is_retained():
    p, d = _problem(
        "def evaluate(c): return {'score':0.9,'is_valid':True,'outputs': {'certificate': 'ok'}}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[{"name": "output_gate", "require_program_output": True}],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["artifact_output_checks"][0]["passed"] is True
    finally:
        shutil.rmtree(d)


def test_configured_stage_program_output_value_check_stops_candidate():
    p, d = _problem(
        "def evaluate(c): return {'score':0.9,'is_valid':True,'outputs': {'certificate': {'status': 'bad'}}}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "output_gate",
                    "program_output_checks": [
                        {"path": "certificate.status", "equals": "ok"}
                    ],
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is False
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["artifact_output_checks"] == [
            {
                "type": "program_output_equals",
                "path": "certificate.status",
                "expected": "ok",
                "actual": "bad",
                "passed": False,
                "reason": "value_mismatch",
            }
        ]
    finally:
        shutil.rmtree(d)


def test_configured_stage_program_output_value_check_passes():
    p, d = _problem(
        "def evaluate(c): return {'score':0.9,'is_valid':True,'outputs': {'certificate': {'status': 'ok'}}}"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "output_gate",
                    "program_output_checks": [
                        {"path": "certificate.status", "equals": "ok"}
                    ],
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["artifact_output_checks"][0]["passed"] is True
    finally:
        shutil.rmtree(d)


def test_configured_stage_min_artifacts_stops_candidate(tmp_path):
    p, d = _problem("def evaluate(c): return {'score':0.9,'is_valid':True}")
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "artifact_gate",
                    "artifact_include": ["*.txt"],
                    "min_artifacts": 1,
                }
            ],
            artifact_dir=tmp_path / "artifacts",
        ).evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "stage_threshold_not_met"
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["artifact_output_checks"] == [
            {
                "type": "artifacts",
                "count": 0,
                "min": 1,
                "passed": False,
                "reason": "below_min_artifacts",
            }
        ]
    finally:
        shutil.rmtree(d)


def test_configured_stage_required_artifact_stops_candidate(tmp_path):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(code, workspace, stage):\n"
        "    Path(workspace, 'other.txt').write_text('ok', encoding='utf-8')\n"
        "    return {'score':0.9,'is_valid':True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "artifact_gate",
                    "artifact_include": ["*.txt"],
                    "required_artifacts": ["report.txt"],
                }
            ],
            artifact_dir=tmp_path / "artifacts",
        ).evaluate("x=1", None)

        assert result.is_valid is False
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["artifact_output_checks"] == [
            {
                "type": "required_artifact",
                "pattern": "report.txt",
                "matched": False,
                "passed": False,
                "reason": "missing_required_artifact",
            }
        ]
    finally:
        shutil.rmtree(d)


def test_configured_stage_required_artifact_passes_with_glob(tmp_path):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(code, workspace, stage):\n"
        "    Path(workspace, 'reports').mkdir()\n"
        "    Path(workspace, 'reports/report.txt').write_text('ok', encoding='utf-8')\n"
        "    return {'score':0.9,'is_valid':True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "artifact_gate",
                    "artifact_include": ["reports/*.txt"],
                    "required_artifacts": ["reports/*.txt"],
                }
            ],
            artifact_dir=tmp_path / "artifacts",
        ).evaluate("x=1", None)

        assert result.is_valid is True
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["artifact_output_checks"][0]["passed"] is True
    finally:
        shutil.rmtree(d)


def test_configured_stage_min_artifacts_passes_when_artifact_is_collected(tmp_path):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(code, workspace, stage):\n"
        "    Path(workspace, 'report.txt').write_text('ok', encoding='utf-8')\n"
        "    return {'score':0.9,'is_valid':True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "artifact_gate",
                    "artifact_include": ["*.txt"],
                    "min_artifacts": 1,
                }
            ],
            artifact_dir=tmp_path / "artifacts",
        ).evaluate("x=1", None)

        assert result.is_valid is True
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["artifact_output_checks"][0]["passed"] is True
        assert stage_result["artifact_output_checks"][0]["count"] == 1
    finally:
        shutil.rmtree(d)


def test_configured_stage_metric_thresholds_can_pass_multiple_metrics():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "runtime", "bounds": [0.0, 10.0], "direction": "minimize"},
    ]
    p, d = _problem(
        "def evaluate(c): return {'score':0.9,'runtime':4.5,'is_valid':True}",
        metrics=metrics,
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "quality",
                    "metric_thresholds": {
                        "score": {"min": 0.8},
                        "runtime": {"max": 5.0},
                    },
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        stage_result = result.metadata["configured_stage_results"][0]
        assert stage_result["threshold_passed"] is True
        assert [item["passed"] for item in stage_result["metric_thresholds"]] == [
            True,
            True,
        ]
    finally:
        shutil.rmtree(d)


def test_configured_stage_retries_below_metric_threshold_valid_sample():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    value = 0.4 if stage['attempt'] == 0 else 0.9\n"
        "    return {'score': value, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "metric_retry",
                    "retries": 1,
                    "metric_thresholds": {"score": {"min": 0.5}},
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        attempts = result.metadata["attempts"]
        assert [attempt["threshold_passed"] for attempt in attempts] == [False, True]
        assert attempts[0]["metric_thresholds"][0]["reason"] == "below_min"
        assert attempts[1]["metric_thresholds"][0]["passed"] is True
    finally:
        shutil.rmtree(d)


def test_configured_stage_results_preserve_each_stage_metadata_and_artifacts(tmp_path):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(code, workspace, stage):\n"
        "    Path(workspace, f\"{stage['name']}.txt\").write_text(stage['name'], encoding='utf-8')\n"
        "    return {'score': 1.0 if stage['name'] == 'hard' else 0.6, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {"name": "cheap", "artifact_include": ["*.txt"], "min_score": 0.5},
                {"name": "hard", "artifact_include": ["*.txt"], "min_score": 0.9},
            ],
            artifact_dir=tmp_path / "artifacts",
        ).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.metadata["stage"]["name"] == "hard"
        assert [stage.name for stage in result.stages] == ["syntax", "cheap", "hard"]
        assert [item["path"] for item in result.metadata["artifacts"]["files"]] == ["hard.txt"]

        stage_results = result.metadata["configured_stage_results"]
        assert [item["name"] for item in stage_results] == ["cheap", "hard"]
        assert all(item["passed"] is True for item in stage_results)
        assert [item["threshold"] for item in stage_results] == [0.5, 0.9]
        assert [item["metadata"]["stage"]["name"] for item in stage_results] == ["cheap", "hard"]
        assert [item["metadata"]["artifacts"]["files"][0]["path"] for item in stage_results] == [
            "cheap.txt",
            "hard.txt",
        ]
    finally:
        shutil.rmtree(d)


def test_configured_stage_uses_distinct_validator_entrypoint():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        stage_validator = d / "stage_validate.py"
        stage_validator.write_text(
            "def evaluate(code, workspace, stage):\n"
            "    return {'score': 0.8 if stage['name'] == 'hard' else 0.0, 'is_valid': True}\n",
            encoding="utf-8",
        )
        ev = CascadeEvaluator(p, stages=[{"name": "hard", "validate_path": "stage_validate.py"}])
        result = ev.evaluate("x=1", None)
        assert result == 0.8
        assert result.metadata["validate_path"] == "stage_validate.py"
        assert result.metadata["stage"]["config"]["validate_path"] == "stage_validate.py"
        assert len(result.metadata["validate_path_hash"]) == 64
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_passes_declared_data_context_to_validator():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    files = stage['evaluator_data']['files']\n"
        "    ok = stage['evaluator_data']['enabled'] and files[0]['path'] == 'data/input.json'\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    try:
        data_dir = d / "data"
        data_dir.mkdir()
        (data_dir / "input.json").write_text('{"target": 1}\n', encoding="utf-8")

        result = CascadeEvaluator(p, data_include=["data/*.json"]).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.fitness == 1.0
        assert result.metadata["stage"]["evaluator_data"]["files"] == [
            {
                "path": "data/input.json",
                "problem_relative_path": "data/input.json",
            }
        ]
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_preflight_allows_top_level_declared_data_import():
    p, d = _problem("def evaluate(c): return {'score': 0.1, 'is_valid': True}")
    try:
        validators = d / "validators"
        validators.mkdir()
        data_dir = validators / "data"
        data_dir.mkdir()
        (data_dir / "input.bin").write_bytes(b"expected")
        validator_path = validators / "stage_validate.py"
        validator_path.write_text(
            "from pathlib import Path\n"
            "IMPORTED = Path(__file__).parent.joinpath('data/input.bin').read_bytes()\n"
            "def evaluate(code, workspace, stage):\n"
            "    ok = IMPORTED == b'expected'\n"
            "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n",
            encoding="utf-8",
        )
        p.validate_path = validator_path

        result = CascadeEvaluator(
            p,
            stages=[{"name": "stage", "validate_path": "validators/stage_validate.py"}],
            data_include=["data/*.bin"],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.fitness == 1.0
        assert result.metadata["stage"]["evaluator_data"]["files"] == [
            {
                "path": "data/input.bin",
                "problem_relative_path": "validators/data/input.bin",
            }
        ]
    finally:
        shutil.rmtree(d)


def test_preflight_evaluator_contracts_accepts_configured_stage_validators():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        stage_validator = d / "stage_validate.py"
        stage_validator.write_text(
            "def evaluate(code, workspace, stage):\n"
            "    return {'score': 0.8, 'is_valid': True}\n",
            encoding="utf-8",
        )
        records = preflight_evaluator_contracts(
            p,
            [
                {"name": "smoke"},
                {"name": "hard", "validate_path": "stage_validate.py"},
            ],
        )
        assert [record["relative_path"] for record in records] == [
            "validate.py",
            "stage_validate.py",
        ]
    finally:
        shutil.rmtree(d)


def test_preflight_evaluator_contracts_does_not_mutate_parent_environment(monkeypatch):
    env_name = "LIBREEVOLVE_PREFLIGHT_PARENT_MUTATION"
    monkeypatch.delenv(env_name, raising=False)
    p, d = _problem(
        "import os\n"
        f"os.environ[{env_name!r}] = 'changed'\n"
        "def evaluate(code): return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        preflight_evaluator_contracts(p)
        assert env_name not in os.environ
    finally:
        shutil.rmtree(d)


def test_preflight_evaluator_contracts_runs_import_from_temporary_cwd():
    p, d = _problem(
        "from pathlib import Path\n"
        "Path('preflight_side_effect.txt').write_text('created', encoding='utf-8')\n"
        "def evaluate(code): return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        preflight_evaluator_contracts(p)
        assert not (d / "preflight_side_effect.txt").exists()
    finally:
        shutil.rmtree(d)


def test_preflight_evaluator_contracts_respects_env_allowlist(monkeypatch):
    env_name = "LIBREEVOLVE_ALLOWED_PREFLIGHT"
    monkeypatch.setenv(env_name, "yes")
    p, d = _problem(
        "import os\n"
        f"if os.environ.get({env_name!r}) != 'yes':\n"
        "    raise RuntimeError('missing allowed env')\n"
        "def evaluate(code): return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        with pytest.raises(ValueError, match="import failed: missing allowed env"):
            preflight_evaluator_contracts(p)
        records = preflight_evaluator_contracts(
            p,
            validator_env_allowlist=[env_name],
        )
        assert records[0]["relative_path"] == "validate.py"
    finally:
        shutil.rmtree(d)


def test_preflight_evaluator_contracts_times_out_slow_import(monkeypatch):
    import libreevolve.core.evaluator as evaluator_mod

    monkeypatch.setattr(evaluator_mod, "_PREFLIGHT_TIMEOUT_SEC", 0.1)
    p, d = _problem(
        "import time\n"
        "time.sleep(30)\n"
        "def evaluate(code): return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        with pytest.raises(ValueError, match="timeout"):
            preflight_evaluator_contracts(p)
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("BROKEN = True\n", "missing callable evaluate"),
        ("def evaluate(): return {'score': 1.0, 'is_valid': True}\n", "unsupported"),
        (
            "def evaluate(code, *, required): return {'score': 1.0, 'is_valid': True}\n",
            "unsupported",
        ),
        (
            "def evaluate(*args): return {'score': 1.0, 'is_valid': True}\n",
            "unsupported",
        ),
        (
            "def evaluate(code, workspace, stage, optional_extra=None):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            "unsupported",
        ),
        (
            "def evaluate(code, **kwargs): return {'score': 1.0, 'is_valid': True}\n",
            "unsupported",
        ),
        ("def evaluate(code):\n    return\n  nope\n", "syntax error"),
        (
            "raise RuntimeError('boom')\n"
            "def evaluate(code): return {'score': 1.0, 'is_valid': True}\n",
            "import failed",
        ),
        (
            "async def evaluate(code):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            "async evaluate functions are unsupported",
        ),
        (
            "def evaluate(code):\n"
            "    yield {'score': 1.0, 'is_valid': True}\n",
            "generator evaluate functions are unsupported",
        ),
        (
            "async def evaluate(code):\n"
            "    yield {'score': 1.0, 'is_valid': True}\n",
            "generator evaluate functions are unsupported",
        ),
    ],
)
def test_preflight_evaluator_contracts_rejects_bad_validator_contracts(source, message):
    p, d = _problem(source)
    try:
        with pytest.raises(ValueError, match=message):
            preflight_evaluator_contracts(p)
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "def evaluate(code): return {'score': 0.25, 'is_valid': True}\n",
            0.25,
        ),
        (
            "def evaluate(code, workspace): return {'score': 0.5, 'is_valid': True}\n",
            0.5,
        ),
        (
            "def evaluate(code, workspace, stage): return {'score': 0.75, 'is_valid': True}\n",
            0.75,
        ),
    ],
)
def test_direct_evaluator_preflight_accepts_supported_default_signatures(source, expected):
    p, d = _problem(source)
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.is_valid is True
        assert result.fitness == expected
    finally:
        shutil.rmtree(d)


def test_preflight_rejects_problem_local_import_outside_evaluator_provenance():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        package = d / "validators"
        package.mkdir()
        (package / "__init__.py").write_text(
            "import root_helper\n"
            "def evaluate(code):\n"
            "    return {'score': root_helper.VALUE, 'is_valid': True}\n",
            encoding="utf-8",
        )
        (d / "root_helper.py").write_text("VALUE = 1.0\n", encoding="utf-8")

        with pytest.raises(ValueError, match="declared provenance"):
            preflight_evaluator_contracts(
                p,
                [{"name": "package", "validate_path": "validators"}],
            )
    finally:
        shutil.rmtree(d)


def test_evaluator_rejects_undeclared_problem_local_data_read():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        validators = d / "validators"
        validators.mkdir()
        (validators / "stage_validate.py").write_text(
            "from pathlib import Path\n"
            "def evaluate(code, workspace, stage):\n"
            "    (Path(__file__).parent / 'fixture.bin').read_bytes()\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            encoding="utf-8",
        )
        (validators / "fixture.bin").write_bytes(b"not declared")

        result = CascadeEvaluator(
            p,
            stages=[{"name": "hard", "validate_path": "validators/stage_validate.py"}],
        ).evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "subprocess_error"
        assert "declared provenance" in result.stderr
        policy = result.metadata["evaluator_dependency_policy"]
        assert policy["policy"] == "declared_problem_local_evaluator_dependencies_v1"
        assert [item["path"] for item in policy["files"]] == [
            "validators/stage_validate.py"
        ]
    finally:
        shutil.rmtree(d)


def test_evaluator_allows_declared_problem_local_data_read():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        validators = d / "validators"
        validators.mkdir()
        (validators / "stage_validate.py").write_text(
            "from pathlib import Path\n"
            "def evaluate(code, workspace, stage):\n"
            "    payload = (Path(__file__).parent / 'fixture.bin').read_bytes()\n"
            "    return {'score': 1.0 if payload == b'declared' else 0.0, 'is_valid': True}\n",
            encoding="utf-8",
        )
        (validators / "fixture.bin").write_bytes(b"declared")

        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "hard",
                    "validate_path": "validators/stage_validate.py",
                    "data_include": ["*.bin"],
                }
            ],
        ).evaluate("x=1", None)

        assert result.is_valid is True
        assert result.fitness == 1.0
        assert [
            item["path"] for item in result.metadata["evaluator_dependency_policy"]["files"]
        ] == ["validators/fixture.bin", "validators/stage_validate.py"]
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("BROKEN = True\n", "missing callable evaluate"),
        (
            "def evaluate(code, *, required): return {'score': 1.0, 'is_valid': True}\n",
            "unsupported",
        ),
        (
            "def evaluate(*args): return {'score': 1.0, 'is_valid': True}\n",
            "unsupported",
        ),
        (
            "async def evaluate(code):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            "async evaluate functions are unsupported",
        ),
        (
            "def evaluate(code):\n"
            "    yield {'score': 1.0, 'is_valid': True}\n",
            "generator evaluate functions are unsupported",
        ),
    ],
)
def test_direct_evaluator_preflights_bad_default_validator_contracts(source, message):
    p, d = _problem(source)
    try:
        with pytest.raises(ValueError, match=message):
            CascadeEvaluator(p).evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_rejects_outside_default_validator_path(tmp_path):
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        outside = tmp_path / "outside_validate.py"
        outside.write_text("def evaluate(c): return {'score':1.0,'is_valid':True}", encoding="utf-8")
        p.validate_path = outside

        with pytest.raises(ValueError, match="escapes problem directory"):
            CascadeEvaluator(p).evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_rejects_missing_default_validator_path():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        p.validate_path = d / "missing.py"

        with pytest.raises(ValueError, match="does not exist"):
            CascadeEvaluator(p).evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_rejects_default_validator_directory():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        validator_dir = d / "validators"
        validator_dir.mkdir()
        p.validate_path = validator_dir

        with pytest.raises(ValueError, match="missing __init__\\.py"):
            CascadeEvaluator(p).evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_rejects_non_python_default_validator_path():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        text_validator = d / "validate.txt"
        text_validator.write_text("not python", encoding="utf-8")
        p.validate_path = text_validator

        with pytest.raises(ValueError, match="Python file"):
            CascadeEvaluator(p).evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_rejects_symlink_to_outside_default_validator(tmp_path):
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        outside = tmp_path / "outside_validate.py"
        outside.write_text("def evaluate(c): return {'score':1.0,'is_valid':True}", encoding="utf-8")
        link = d / "linked_validate.py"
        try:
            link.symlink_to(outside)
        except OSError:
            pytest.skip("symlink creation is unavailable")
        p.validate_path = link

        with pytest.raises(ValueError, match="escapes problem directory"):
            CascadeEvaluator(p).evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            "async def evaluate(code, workspace, stage):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            "async evaluate functions are unsupported",
        ),
        (
            "def evaluate(code, workspace, stage):\n"
            "    yield {'score': 1.0, 'is_valid': True}\n",
            "generator evaluate functions are unsupported",
        ),
        (
            "def evaluate(code, workspace, *args):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            "unsupported",
        ),
        (
            "def evaluate(code, workspace, stage, optional_extra=None):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            "unsupported",
        ),
    ],
)
def test_preflight_evaluator_contracts_rejects_unsupported_stage_callables(
    source,
    message,
):
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        (d / "stage_validate.py").write_text(source, encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            preflight_evaluator_contracts(p, [{"name": "hard", "validate_path": "stage_validate.py"}])
    finally:
        shutil.rmtree(d)


def test_direct_evaluator_preflights_bad_configured_stage_validator_contract():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        (d / "stage_validate.py").write_text(
            "def evaluate(code, workspace, *args):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            encoding="utf-8",
        )
        evaluator = CascadeEvaluator(
            p,
            stages=[{"name": "hard", "validate_path": "stage_validate.py"}],
        )
        with pytest.raises(ValueError, match="unsupported"):
            evaluator.evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_configured_stage_allows_absolute_problem_local_validator():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        stage_validator = d / "stage_validate.py"
        stage_validator.write_text(
            "def evaluate(code, workspace, stage):\n"
            "    return {'score': 0.9, 'is_valid': True}\n",
            encoding="utf-8",
        )
        ev = CascadeEvaluator(p, stages=[{"name": "hard", "validate_path": str(stage_validator)}])
        result = ev.evaluate("x=1", None)
        assert result == 0.9
        assert result.metadata["validate_path"] == "stage_validate.py"
        assert result.metadata["validate_path_scope"] == "problem_relative"
        assert result.metadata["validate_path_redacted"] is True
        assert len(result.metadata["validate_path_hash"]) == 64
        assert result.metadata["stage"]["config"]["validate_path"] == "stage_validate.py"
    finally:
        shutil.rmtree(d)


def test_evaluator_metadata_redacts_secret_like_problem_paths(tmp_path):
    token = "sk-" + "proj_" + "evalpathsecret1234567890"  # pragma: allowlist secret
    d = tmp_path / f"api_key={token}_problem"
    d.mkdir()
    validate_path = d / "validate.py"
    validate_path.write_text(
        "def evaluate(c): return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    p = Problem(
        name="secret-path",
        task_description="t",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=validate_path,
        initial_programs=[],
        problem_dir=d,
    )

    result = CascadeEvaluator(
        p,
        stages=[{"name": "absolute", "validate_path": str(validate_path)}],
    ).evaluate("x=1", None)

    rendered = repr(result.to_dict())
    assert result.metadata["validate_path"] == "validate.py"
    assert result.metadata["stage"]["config"]["validate_path"] == "validate.py"
    assert result.metadata["validate_path_redacted"] is True
    assert token not in rendered
    assert str(d) not in rendered


def test_configured_stage_rejects_missing_validator_path():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "missing", "validate_path": "missing.py"}])
        with pytest.raises(ValueError, match="does not exist"):
            ev.evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_configured_stage_rejects_validator_directory():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        validator_dir = d / "validators"
        validator_dir.mkdir()
        ev = CascadeEvaluator(p, stages=[{"name": "dir", "validate_path": "validators"}])
        with pytest.raises(ValueError, match="missing __init__\\.py"):
            ev.evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_configured_stage_rejects_non_python_validator_path():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        text_validator = d / "stage_validate.txt"
        text_validator.write_text("not python", encoding="utf-8")
        ev = CascadeEvaluator(p, stages=[{"name": "text", "validate_path": "stage_validate.txt"}])
        with pytest.raises(ValueError, match="Python file"):
            ev.evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_configured_stage_rejects_outside_validator_path(tmp_path):
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        outside = tmp_path / "outside_validate.py"
        outside.write_text("def evaluate(c): return {'score':1.0,'is_valid':True}", encoding="utf-8")
        ev = CascadeEvaluator(p, stages=[{"name": "outside", "validate_path": str(outside)}])
        with pytest.raises(ValueError, match="escapes problem directory"):
            ev.evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_configured_stage_rejects_relative_validator_escape():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        outside = d.parent / "outside_validate.py"
        outside.write_text("def evaluate(c): return {'score':1.0,'is_valid':True}", encoding="utf-8")
        ev = CascadeEvaluator(p, stages=[{"name": "outside", "validate_path": "../outside_validate.py"}])
        with pytest.raises(ValueError, match="escapes problem directory"):
            ev.evaluate("x=1", None)
    finally:
        if "outside" in locals() and outside.exists():
            outside.unlink()
        shutil.rmtree(d)


def test_configured_stage_rejects_symlink_to_outside_validator(tmp_path):
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        outside = tmp_path / "outside_validate.py"
        outside.write_text("def evaluate(c): return {'score':1.0,'is_valid':True}", encoding="utf-8")
        link = d / "linked_validate.py"
        try:
            link.symlink_to(outside)
        except OSError:
            pytest.skip("symlink creation is unavailable")
        ev = CascadeEvaluator(p, stages=[{"name": "linked", "validate_path": "linked_validate.py"}])
        with pytest.raises(ValueError, match="escapes problem directory"):
            ev.evaluate("x=1", None)
    finally:
        shutil.rmtree(d)


def test_configured_stage_aggregates_seeded_samples():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    return {'score': stage['seed'] / 10, 'is_valid': True}\n"
    )
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "sampled", "seeds": [2, 4]}])
        result = ev.evaluate("x=1", None)
        assert abs(result - 0.3) < 1e-9
        assert result.metadata["sample_count"] == 2
        assert [stage.name for stage in result.stages[-2:]] == ["sampled[0]", "sampled[1]"]
    finally:
        shutil.rmtree(d)


def test_configured_stage_parallel_sample_workers_preserve_sample_order():
    p, d = _problem(
        "import time\n"
        "def evaluate(code, workspace, stage):\n"
        "    time.sleep(0.25)\n"
        "    return {'score': stage['sample_index'] / 10, 'is_valid': True}\n"
    )
    try:
        serial = CascadeEvaluator(
            p,
            stages=[{"name": "serial", "samples": 3}],
        )
        serial_started = time.perf_counter()
        serial_result = serial.evaluate("x=1", None)
        serial_elapsed = time.perf_counter() - serial_started

        parallel = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "parallel",
                    "samples": 3,
                    "sample_workers": 3,
                }
            ],
        )
        parallel_started = time.perf_counter()
        parallel_result = parallel.evaluate("x=1", None)
        parallel_elapsed = time.perf_counter() - parallel_started

        assert serial_result.is_valid is True
        assert parallel_result.is_valid is True
        assert parallel_elapsed < serial_elapsed * 0.85
        sample_execution = parallel_result.metadata["sample_execution"]
        assert {
            key: sample_execution[key]
            for key in (
                "mode",
                "requested_workers",
                "effective_workers",
                "planned_samples",
                "completed_samples",
                "deterministic_result_order",
            )
        } == {
            "mode": "thread_pool",
            "requested_workers": 3,
            "effective_workers": 3,
            "planned_samples": 3,
            "completed_samples": 3,
            "deterministic_result_order": "sample_index",
        }
        assert sample_execution["sample_elapsed_sec_sum"] >= 0.6
        assert sample_execution["wall_clock_elapsed_sec"] < serial_elapsed
        assert sample_execution["wall_clock_compression_ratio"] > 1.5
        assert sample_execution["wall_clock_compression_observed"] is True
        assert [
            sample["metadata"]["stage"]["sample_index"]
            for sample in parallel_result.metadata["samples"]
        ] == [0, 1, 2]
        assert [
            sample["metrics"]["score"]
            for sample in parallel_result.metadata["samples"]
        ] == [0.0, 0.1, 0.2]
    finally:
        shutil.rmtree(d)


def test_configured_stage_seed_controls_validator_rng_state():
    p, d = _problem(
        "import os, random\n"
        "import numpy as np\n"
        "MODULE_RANDOM = random.random()\n"
        "def evaluate(code, workspace, stage):\n"
        "    return {\n"
        "        'score': MODULE_RANDOM,\n"
        "        'sample_random': random.random(),\n"
        "        'numpy_random': float(np.random.random()),\n"
        "        'hash_seed_match': 1.0 if os.environ.get('PYTHONHASHSEED') == str(stage['rng_seed']) else 0.0,\n"
        "        'is_valid': True,\n"
        "    }\n",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {"name": "sample_random", "bounds": [0.0, 1.0]},
            {"name": "numpy_random", "bounds": [0.0, 1.0]},
            {"name": "hash_seed_match", "bounds": [0.0, 1.0]},
        ],
    )
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "seeded", "samples": 2, "seeds": [123, 123]}])
        result = ev.evaluate("x=1", None)

        assert result.is_valid is True
        samples = result.metadata["samples"]
        first_metrics = samples[0]["metrics"]
        second_metrics = samples[1]["metrics"]
        assert first_metrics["score"] == second_metrics["score"]
        assert first_metrics["sample_random"] == second_metrics["sample_random"]
        assert first_metrics["numpy_random"] == second_metrics["numpy_random"]
        assert first_metrics["hash_seed_match"] == 1.0
        assert second_metrics["hash_seed_match"] == 1.0
        assert samples[0]["metadata"]["stage"]["rng_seed"] == 123
        assert samples[1]["metadata"]["stage"]["rng_seed"] == 123
        assert "PYTHONHASHSEED" in samples[0]["metadata"]["validator_env"]["provided_keys"]
    finally:
        shutil.rmtree(d)


def test_configured_stage_specs_are_snapshotted_after_validation(tmp_path):
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(code, workspace, stage):\n"
        "    Path(workspace, 'kept.txt').write_text(str(stage['seed']), encoding='utf-8')\n"
        "    return {'score': stage['seed'] / 10, 'is_valid': True}\n"
    )
    try:
        stage = {
            "name": "kept",
            "samples": 1,
            "seeds": [8],
            "retries": 0,
            "min_score": 0.5,
            "artifact_include": ["kept.txt"],
            "artifact_max_files": 1,
        }
        stages = [stage]
        ev = CascadeEvaluator(
            p,
            stages=stages,
            artifact_dir=tmp_path / "artifacts",
            artifact_include=["*.json"],
        )

        stage["name"] = "mutated"
        stage["samples"] = "not-an-int"
        stage["seeds"][0] = 0
        stage["retries"] = 999
        stage["min_score"] = 0.95
        stage["artifact_include"][0] = "mutated.txt"
        stage["artifact_max_files"] = 0
        stages.append({"name": "late", "samples": 1})

        result = ev.evaluate("x=1", None)
        assert result == 0.8
        assert result.is_valid is True
        assert result.metadata["stage"]["name"] == "kept"
        assert result.metadata["stage"]["seed"] == 8
        assert result.metadata["stage"]["config"]["samples"] == 1
        assert result.metadata["stage"]["config"]["seeds"] == [8]
        assert result.metadata["stage"]["config"]["retries"] == 0
        assert result.metadata["stage"]["config"]["min_score"] == 0.5
        assert result.metadata["artifacts"]["include"] == ["kept.txt"]
        assert result.metadata["artifacts"]["max_files"] == 1
        assert [item["path"] for item in result.metadata["artifacts"]["files"]] == [
            "kept.txt"
        ]
    finally:
        shutil.rmtree(d)


def test_configured_stage_retries_failed_sample():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    ok = stage['attempt'] == 1\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "retry", "retries": 1}])
        result = ev.evaluate("x=1", None)
        assert result == 1.0
        assert result.metadata["attempt"] == 1
        assert result.metadata["attempt_count"] == 2
        assert [attempt["passed"] for attempt in result.metadata["attempts"]] == [False, True]
        assert [attempt["attempt"] for attempt in result.metadata["attempts"]] == [0, 1]
        assert result.metadata["attempts"][0]["error"] == "domain_invalid"
    finally:
        shutil.rmtree(d)


def test_configured_stage_wall_clock_budget_limits_long_attempt():
    p, d = _problem(
        "import time\n"
        "def evaluate(code, workspace, stage):\n"
        "    time.sleep(30)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        ev = CascadeEvaluator(
            p,
            stages=[{"name": "budgeted", "timeout_sec": 5.0, "max_stage_seconds": 0.2}],
        )
        started = time.perf_counter()
        result = ev.evaluate("x=1", None)

        assert time.perf_counter() - started < 2.0
        assert result.is_valid is False
        assert result.error == "stage_budget_exhausted"
        assert result.metadata["stopped_at"] == "budgeted"
        assert result.metadata["stage_budget"]["policy"] == "max_stage_seconds"
        assert result.metadata["stage_budget"]["max_stage_seconds"] == 0.2
        assert result.metadata["attempt_count"] == 1
        assert result.metadata["attempts"][0]["error"] == "stage_budget_exhausted"
        assert result.stages[-1].error == "stage_budget_exhausted"
        assert result.stages[-1].metadata["stage_budget"]["policy"] == "max_stage_seconds"
        configured = result.metadata["configured_stage_results"][0]
        assert configured["stop_reason"] == "stage_budget_exhausted"
        assert configured["metadata"]["stage_budget"]["policy"] == "max_stage_seconds"
    finally:
        shutil.rmtree(d)


def test_configured_sample_wall_clock_budget_limits_long_attempt():
    p, d = _problem(
        "import time\n"
        "def evaluate(code, workspace, stage):\n"
        "    time.sleep(30)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        ev = CascadeEvaluator(
            p,
            stages=[{"name": "budgeted", "timeout_sec": 5.0, "max_sample_seconds": 0.2}],
        )
        started = time.perf_counter()
        result = ev.evaluate("x=1", None)

        assert time.perf_counter() - started < 2.0
        assert result.is_valid is False
        assert result.error == "sample_budget_exhausted"
        assert result.metadata["stopped_at"] == "budgeted"
        assert result.metadata["sample_budget"]["policy"] == "max_sample_seconds"
        assert result.metadata["sample_budget"]["max_sample_seconds"] == 0.2
        assert result.metadata["attempt_count"] == 1
        assert result.metadata["attempts"][0]["error"] == "sample_budget_exhausted"
        assert result.stages[-1].error == "sample_budget_exhausted"
        assert result.stages[-1].metadata["sample_budget"]["policy"] == "max_sample_seconds"
        configured = result.metadata["configured_stage_results"][0]
        assert configured["stop_reason"] == "sample_budget_exhausted"
        assert configured["metadata"]["sample_budget"]["policy"] == "max_sample_seconds"
    finally:
        shutil.rmtree(d)


def test_configured_sample_wall_clock_budget_resets_for_each_sample():
    p, d = _problem(
        "import time\n"
        "def evaluate(code, workspace, stage):\n"
        "    time.sleep(0.55)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        # Each sample fits its own budget; their combined sleep exceeds it.
        ev = CascadeEvaluator(
            p,
            stages=[{"name": "sample_budget", "samples": 2, "timeout_sec": 2.0, "max_sample_seconds": 1.0}],
        )
        result = ev.evaluate("x=1", None)

        assert result.is_valid is True
        assert result.error is None
        assert result.metadata["sample_count"] == 2
        assert [sample["error"] for sample in result.metadata["samples"]] == [None, None]
        assert [stage.name for stage in result.stages[-2:]] == [
            "sample_budget[0]",
            "sample_budget[1]",
        ]
    finally:
        shutil.rmtree(d)


def test_configured_stage_wall_clock_budget_limits_retry_attempt_timeout():
    p, d = _problem(
        "import time\n"
        "def evaluate(code, workspace, stage):\n"
        "    time.sleep(0.08)\n"
        "    return {'score': 0.0, 'is_valid': False}\n"
    )
    try:
        ev = CascadeEvaluator(
            p,
            stages=[{"name": "budgeted", "timeout_sec": 1.0, "max_stage_seconds": 0.05, "retries": 2}],
        )
        result = ev.evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "stage_budget_exhausted"
        assert result.metadata["attempt_count"] == 1
        assert [attempt["attempt"] for attempt in result.metadata["attempts"]] == [0]
        assert result.metadata["attempts"][0]["error"] == "stage_budget_exhausted"
    finally:
        shutil.rmtree(d)


def test_configured_stage_retries_below_threshold_valid_sample():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    score = 0.1 if stage['attempt'] == 0 else 0.9\n"
        "    return {'score': score, 'is_valid': True}\n"
    )
    try:
        ev = CascadeEvaluator(
            p,
            stages=[{"name": "threshold_retry", "retries": 1, "min_score": 0.5}],
        )
        result = ev.evaluate("x=1", None)

        assert result.is_valid is True
        assert result == 0.9
        assert result.metadata["attempt"] == 1
        assert result.metadata["attempt_count"] == 2
        attempts = result.metadata["attempts"]
        assert [attempt["attempt"] for attempt in attempts] == [0, 1]
        assert [attempt["local_valid"] for attempt in attempts] == [True, True]
        assert [attempt["threshold_passed"] for attempt in attempts] == [False, True]
        assert [attempt["passed"] for attempt in attempts] == [False, True]
        assert [attempt["threshold"] for attempt in attempts] == [0.5, 0.5]
    finally:
        shutil.rmtree(d)


def test_configured_stage_exhausts_retries_for_below_threshold_valid_samples():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    return {'score': 0.1 + (stage['attempt'] * 0.1), 'is_valid': True}\n"
    )
    try:
        ev = CascadeEvaluator(
            p,
            stages=[{"name": "threshold_retry", "retries": 1, "min_score": 0.5}],
        )
        result = ev.evaluate("x=1", None)

        assert result.is_valid is False
        assert result.error == "stage_threshold_not_met"
        assert result.metadata["attempt_count"] == 2
        attempts = result.metadata["attempts"]
        assert [attempt["attempt"] for attempt in attempts] == [0, 1]
        assert [attempt["local_valid"] for attempt in attempts] == [True, True]
        assert [attempt["threshold_passed"] for attempt in attempts] == [False, False]
        assert [attempt["passed"] for attempt in attempts] == [False, False]
        stage_results = result.metadata["configured_stage_results"]
        assert stage_results[0]["threshold_passed"] is False
        assert stage_results[0]["stop_reason"] == "stage_threshold_not_met"
    finally:
        shutil.rmtree(d)


def test_configured_stage_seed_controls_retry_attempt_rng_state():
    p, d = _problem(
        "import random\n"
        "def evaluate(code, workspace, stage):\n"
        "    value = random.random()\n"
        "    ok = stage['attempt'] == 1\n"
        "    return {'score': value, 'is_valid': ok}\n"
    )
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "retry_seeded", "seeds": [987], "retries": 1}])
        result = ev.evaluate("x=1", None)

        assert result.is_valid is True
        assert result.metadata["attempt_count"] == 2
        attempts = result.metadata["attempts"]
        assert attempts[0]["metrics"]["score"] == attempts[1]["metrics"]["score"]
        assert attempts[0]["stage"]["seed"] == 987
        assert attempts[0]["stage"]["rng_seed"] == 987
        assert attempts[1]["stage"]["rng_seed"] == 987
    finally:
        shutil.rmtree(d)


def test_configured_stage_records_pass_first_retry_attempt():
    p, d = _problem("def evaluate(code, workspace, stage): return {'score': 1.0, 'is_valid': True}")
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "retry", "retries": 2}])
        result = ev.evaluate("x=1", None)
        assert result == 1.0
        assert result.metadata["attempt_count"] == 1
        assert [attempt["attempt"] for attempt in result.metadata["attempts"]] == [0]
        assert result.metadata["attempts"][0]["passed"] is True
    finally:
        shutil.rmtree(d)


def test_configured_stage_records_all_failed_retry_attempts():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    print(f'attempt={stage[\"attempt\"]}')\n"
        "    return {'score': 0.0, 'is_valid': False}\n"
    )
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "retry", "retries": 2}])
        result = ev.evaluate("x=1", None)
        assert result.is_valid is False
        assert result.metadata["attempt_count"] == 3
        assert [attempt["attempt"] for attempt in result.metadata["attempts"]] == [0, 1, 2]
        assert [attempt["passed"] for attempt in result.metadata["attempts"]] == [
            False,
            False,
            False,
        ]
        assert "attempt=0" in result.metadata["attempts"][0]["stdout"]
        assert "attempt=2" in result.metadata["attempts"][2]["stdout"]
    finally:
        shutil.rmtree(d)


def test_evaluation_accounting_summarizes_configured_samples_and_retries():
    p, d = _problem(
        "def evaluate(code, workspace, stage):\n"
        "    ok = stage['attempt'] == 1\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    try:
        ev = CascadeEvaluator(p, stages=[{"name": "accounted", "samples": 2, "retries": 1}])
        result = ev.evaluate("x=1", None)

        accounting = evaluation_accounting(result)
        assert accounting["schema"] == "evaluator_accounting_v1"
        assert accounting["configured_stage_samples"] == 2
        assert accounting["subprocess_attempts"] == 4
        assert accounting["retry_attempts"] == 2
        assert accounting["timeout_count"] == 0
        assert result.to_dict()["accounting"] == accounting
        assert all(
            sample["accounting"]["subprocess_attempts"] == 2
            for sample in result.to_dict()["metadata"]["samples"]
        )
    finally:
        shutil.rmtree(d)


def test_evaluation_accounting_counts_budget_exhaustion_errors():
    p, d = _problem(
        "import time\n"
        "def evaluate(code, workspace, stage):\n"
        "    time.sleep(30)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        sample_result = CascadeEvaluator(
            p,
            stages=[{"name": "sample_budget", "timeout_sec": 5.0, "max_sample_seconds": 0.1}],
        ).evaluate("x=1", None)
        stage_result = CascadeEvaluator(
            p,
            stages=[{"name": "stage_budget", "timeout_sec": 5.0, "max_stage_seconds": 0.1}],
        ).evaluate("x=1", None)

        sample_accounting = evaluation_accounting(sample_result)
        stage_accounting = evaluation_accounting(stage_result)
        assert sample_accounting["subprocess_attempts"] == 1
        assert sample_accounting["sample_budget_exhaustions"] == 1
        assert sample_accounting["stage_budget_exhaustions"] == 0
        assert stage_accounting["subprocess_attempts"] == 1
        assert stage_accounting["sample_budget_exhaustions"] == 0
        assert stage_accounting["stage_budget_exhaustions"] == 1
    finally:
        shutil.rmtree(d)


def test_workspace_validator_receives_materialized_files():
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(code, workspace):\n"
        "    helper = Path(workspace) / 'pkg' / 'helper.py'\n"
        "    ok = helper.read_text().strip() == 'VALUE = 7'\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    workspace = CandidateWorkspace(
        files={"main.py": "from pkg.helper import VALUE\n", "pkg/helper.py": "VALUE = 7\n"},
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(p).evaluate(workspace, None)
        assert result == 1.0
        assert result.metadata["files"] == ["main.py", "pkg/helper.py"]
    finally:
        shutil.rmtree(d)


def test_embedded_evaluate_stage_calls_candidate_eval_inputs():
    p, d = _problem(
        "def evaluate(code):\n"
        "    return {'score': 0.0, 'is_valid': False}\n"
    )
    workspace = CandidateWorkspace(
        files={
            "main.py": (
                "def evaluate(eval_inputs):\n"
                "    values = eval_inputs['values']\n"
                "    return {'score': sum(values) / 10.0, 'is_valid': True}\n"
            )
        },
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "candidate_eval",
                    "mode": "embedded_evaluate",
                    "eval_inputs": {"values": [2, 3, 4]},
                }
            ],
        ).evaluate(workspace, None)

        assert result == 0.9
        assert result.metadata["evaluator_mode"] == "embedded_evaluate"
        assert result.metadata["candidate_evaluator"]["entrypoint"] == "main.py"
        assert result.metadata["candidate_evaluator"]["eval_inputs"]["retained"] is False
        assert len(result.metadata["candidate_evaluator"]["eval_inputs"]["sha256"]) == 64
        assert result.metadata["evaluator_dependency_policy"] == {
            "policy": "candidate_primary_module_embedded_evaluate_v1",
            "allowed_scope": "materialized_candidate_workspace",
            "workspace_dependency_policy": (
                "materialized_candidate_files_only_for_workspace_local_modules_and_reads"
            ),
            "runtime_enforced": True,
            "file_count": 1,
            "problem_local_dependency_policy": "not_used",
            "outside_problem_policy": "not_constrained_by_this_policy",
        }
        assert "validate_path" not in result.metadata
    finally:
        shutil.rmtree(d)


def test_embedded_evaluate_stage_allows_materialized_workspace_helpers():
    p, d = _problem("def evaluate(code): return {'score': 0.0, 'is_valid': False}")
    workspace = CandidateWorkspace(
        files={
            "main.py": (
                "from pkg.helper import score\n"
                "def evaluate(eval_inputs):\n"
                "    return {'score': score(eval_inputs['x']), 'is_valid': True}\n"
            ),
            "pkg/__init__.py": "",
            "pkg/helper.py": "def score(x): return x / 10.0\n",
        },
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[
                {
                    "name": "candidate_eval",
                    "mode": "embedded_evaluate",
                    "eval_inputs": {"x": 8},
                }
            ],
        ).evaluate(workspace, None)

        assert result == 0.8
        assert result.metadata["evaluator_dependency_policy"]["runtime_enforced"] is True
        assert result.metadata["evaluator_dependency_policy"]["file_count"] == 3
    finally:
        shutil.rmtree(d)


def test_embedded_evaluate_stage_blocks_unmaterialized_workspace_imports():
    p, d = _problem("def evaluate(code): return {'score': 0.0, 'is_valid': False}")
    workspace = CandidateWorkspace(
        files={
            "main.py": (
                "from pathlib import Path\n"
                "def evaluate(eval_inputs):\n"
                "    Path('late_helper.py').write_text('VALUE = 1\\n', encoding='utf-8')\n"
                "    import late_helper\n"
                "    return {'score': late_helper.VALUE, 'is_valid': True}\n"
            )
        },
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[{"name": "candidate_eval", "mode": "embedded_evaluate"}],
        ).evaluate(workspace, None)

        assert result == -0.2
        assert result.error == "malformed_metrics"
        assert "materialized candidate manifest" in result.metadata["malformed_metrics"]["message"]
        assert result.metadata["evaluator_dependency_policy"]["runtime_enforced"] is True
    finally:
        shutil.rmtree(d)


def test_embedded_evaluate_stage_reports_missing_candidate_callable():
    p, d = _problem("def evaluate(code): return {'score': 0.0, 'is_valid': False}")
    workspace = CandidateWorkspace(files={"main.py": "x = 1\n"}, primary_file="main.py")
    try:
        result = CascadeEvaluator(
            p,
            stages=[{"name": "candidate_eval", "mode": "embedded_evaluate"}],
        ).evaluate(workspace, None)

        assert result == -0.2
        assert result.error == "malformed_metrics"
        assert result.metadata["malformed_metrics"]["message"] == (
            "candidate primary module must define callable evaluate(eval_inputs)"
        )
    finally:
        shutil.rmtree(d)


def test_embedded_evaluate_stage_reports_unsupported_candidate_signature():
    p, d = _problem("def evaluate(code): return {'score': 0.0, 'is_valid': False}")
    workspace = CandidateWorkspace(
        files={"main.py": "def evaluate(code, workspace):\n    return {}\n"},
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(
            p,
            stages=[{"name": "candidate_eval", "mode": "embedded_evaluate"}],
        ).evaluate(workspace, None)

        assert result == -0.2
        assert result.error == "malformed_metrics"
        assert "evaluate(eval_inputs)" in result.metadata["malformed_metrics"]["message"]
    finally:
        shutil.rmtree(d)


def test_workspace_imports_work_from_candidate_root_by_default():
    p, d = _problem(
        "def evaluate(code, workspace):\n"
        "    from pkg.helper import VALUE\n"
        "    return {'score': 1.0 if VALUE == 7 else 0.0, 'is_valid': VALUE == 7}\n"
    )
    workspace = CandidateWorkspace(
        files={
            "main.py": "from pkg.helper import VALUE\n",
            "pkg/__init__.py": "",
            "pkg/helper.py": "VALUE = 7\n",
        },
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(p).evaluate(workspace, None)
        assert result == 1.0
    finally:
        shutil.rmtree(d)


def test_validator_directory_precedes_candidate_import_path_on_helper_collision():
    p, d = _problem(
        "def evaluate(code, workspace):\n"
        "    from pkg.helper import VALUE\n"
        "    return {'score': 1.0 if VALUE == 7 else 0.0, 'is_valid': VALUE == 7}\n"
    )
    (d / "pkg").mkdir()
    (d / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (d / "pkg" / "helper.py").write_text("VALUE = 7\n", encoding="utf-8")
    workspace = CandidateWorkspace(
        files={
            "main.py": "from pkg.helper import VALUE\n",
            "pkg/__init__.py": "",
            "pkg/helper.py": "VALUE = 0\n",
        },
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(p).evaluate(workspace, None)
        assert result == 1.0
    finally:
        shutil.rmtree(d)


def test_workspace_relative_file_access_uses_candidate_root_by_default():
    p, d = _problem(
        "from pathlib import Path\n"
        "def evaluate(code, workspace):\n"
        "    ok = Path('data/input.txt').read_text() == 'ready'\n"
        "    return {'score': 1.0 if ok else 0.0, 'is_valid': ok}\n"
    )
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "data/input.txt": "ready"},
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(p).evaluate(workspace, None)
        assert result == 1.0
    finally:
        shutil.rmtree(d)


def test_problem_local_validator_imports_work_from_validate_directory():
    p, d = _problem(
        "from scoring import score\n"
        "def evaluate(code, workspace):\n"
        "    return {'score': score(code), 'is_valid': True}\n"
    )
    (d / "scoring.py").write_text(
        "def score(code):\n"
        "    return 0.75 if 'x = 1' in code else 0.0\n",
        encoding="utf-8",
    )
    try:
        result = CascadeEvaluator(p).evaluate("x = 1\n", None)
        assert result == 0.75
    finally:
        shutil.rmtree(d)


def test_workspace_syntax_checks_all_python_files():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    workspace = CandidateWorkspace(
        files={"main.py": "x = 1\n", "helper.py": "def bad(:\n    pass\n"},
        primary_file="main.py",
    )
    try:
        result = CascadeEvaluator(p).evaluate(workspace, None)
        assert result == -0.2
        assert "helper.py" in result.stages[0].error
    finally:
        shutil.rmtree(d)


def test_workspace_syntax_aggregates_all_python_errors_and_skips_text_files():
    p, d = _problem("def evaluate(c): return {'score':1.0,'is_valid':True}")
    workspace = CandidateWorkspace(
        files={
            "a.py": "def bad_a(:\n    pass\n",
            "b.py": "def bad_b(:\n    pass\n",
            "notes.txt": "def not_python(:\n",
            "ok.py": "x = 1\n",
        },
        primary_file="ok.py",
    )
    try:
        result = CascadeEvaluator(p).evaluate(workspace, None)
        assert result == -0.2
        assert result.error == "syntax_error"
        assert "a.py" in result.stages[0].error
        assert "b.py" in result.stages[0].error
        assert "notes.txt" not in result.stages[0].error
        syntax_errors = result.metadata["syntax_errors"]
        assert [error["path"] for error in syntax_errors] == ["a.py", "b.py"]
        assert all(error["line"] == 1 for error in syntax_errors)
        assert all(error["offset"] is not None for error in syntax_errors)
        assert all("message" in error for error in syntax_errors)
    finally:
        shutil.rmtree(d)
