import hashlib
import shutil, tempfile
import time
from pathlib import Path
from libreevolve.core.candidate import CandidateWorkspace
import pytest
from libreevolve.core.evaluator import CascadeEvaluator, evaluator_entrypoint_provenance
from libreevolve.problems.loader import Problem

def _problem(validate_src: str, metrics: list[dict] | None = None):
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(validate_src, encoding="utf-8")
    return Problem(name="t", task_description="t",
                   metrics=metrics or [
                       {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
                       {"name": "is_valid", "primary": False, "bounds": [0.0, 1.0]},
                   ],
                   primary_metric="score", primary_bounds=(0.0, 1.0),
                   validate_path=d/"validate.py", initial_programs=[], problem_dir=d), d

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
    finally: shutil.rmtree(d)

def test_t2_timeout():
    p, d = _problem("import time\ndef evaluate(c): time.sleep(30); return {'score':1.0,'is_valid':True}")
    try:
        ev = CascadeEvaluator(p, timeout_sec=0.5)
        result = ev.evaluate("x=1", None)
        assert result == -0.2
        assert result.error == "timeout"
        assert result.metadata["timeout_cleanup"]["attempted"] is True
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

def test_t2_bad_json():
    # validate.py prints non-JSON stdout but exits 0
    p, d = _problem(
        "def evaluate(c):\n"
        "    import sys; sys.stdout.write('not-json\\n'); raise SystemExit(0)"
    )
    try:
        assert CascadeEvaluator(p).evaluate("x=1", None) == -0.2
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


def test_validator_stdout_and_stderr_redact_secret_like_values():
    secret = "sk-proj_validatorsecret1234567890"
    p, d = _problem(
        "import sys\n"
        "def evaluate(c):\n"
        f"    print('api_key={secret}')\n"
        f"    print('token: {secret}', file=sys.stderr)\n"
        "    return {'score': 1.0, 'is_valid': True}\n"
    )
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result == 1.0
        assert secret not in result.stdout
        assert secret not in result.stderr
        assert "[REDACTED]" in result.stdout
        assert "[REDACTED]" in result.stderr
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


@pytest.mark.parametrize(
    "validate_src",
    [
        "def evaluate(c): return {'score': 1.0}",
        "def evaluate(c): return {'score': 1.0, 'is_valid': True, 'extra': 3}",
        "def evaluate(c): return {'score': 'good', 'is_valid': True}",
        "def evaluate(c): return {'score': float('nan'), 'is_valid': True}",
        "def evaluate(c): return {'score': 1.0, 'is_valid': 1}",
    ],
)
def test_rejects_malformed_metric_contract(validate_src):
    p, d = _problem(validate_src)
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result == -0.2
        assert result.error == "malformed_metrics"
        assert result.stages[-1].error == "malformed_metrics"
    finally:
        shutil.rmtree(d)


def test_rejects_missing_declared_secondary_metric():
    metrics = [
        {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
        {"name": "runtime", "primary": False, "bounds": [0.0, 10.0]},
        {"name": "is_valid", "primary": False, "bounds": [0.0, 1.0]},
    ]
    p, d = _problem("def evaluate(c): return {'score': 1.0, 'is_valid': True}", metrics=metrics)
    try:
        result = CascadeEvaluator(p).evaluate("x=1", None)
        assert result.error == "malformed_metrics"
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
        assert result.metadata["validate_path"].endswith("stage_validate.py")
    finally:
        shutil.rmtree(d)


def test_evaluator_entrypoint_provenance_hashes_default_validator():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        records = evaluator_entrypoint_provenance(p)
        assert len(records) == 1
        record = records[0]
        raw = (d / "validate.py").read_bytes()
        assert record["role"] == "default"
        assert record["relative_path"] == "validate.py"
        assert record["sha256"] == hashlib.sha256(raw).hexdigest()
        assert record["bytes"] == len(raw)
        assert record["source_type"] == "python"
    finally:
        shutil.rmtree(d)


def test_evaluator_entrypoint_provenance_hashes_configured_stage_validators():
    p, d = _problem("def evaluate(c): return {'score':0.1,'is_valid':True}")
    try:
        stage_validator = d / "stage_validate.py"
        stage_validator.write_text(
            "def evaluate(code, workspace, stage):\n"
            "    return {'score': 0.8, 'is_valid': True}\n",
            encoding="utf-8",
        )
        records = evaluator_entrypoint_provenance(
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
        assert [record["stage_name"] for record in records] == ["smoke", "hard"]
        assert records[0]["stage_index"] == 0
        assert records[1]["stage_index"] == 1
        assert records[1]["configured_validate_path"] == "stage_validate.py"
        assert records[1]["sha256"] == hashlib.sha256(stage_validator.read_bytes()).hexdigest()
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
        assert result.metadata["validate_path"] == str(stage_validator.resolve())
    finally:
        shutil.rmtree(d)


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
        with pytest.raises(ValueError, match="not a file"):
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


def test_candidate_import_path_precedes_validator_directory():
    p, d = _problem(
        "def evaluate(code, workspace):\n"
        "    from pkg.helper import VALUE\n"
        "    return {'score': 1.0 if VALUE == 7 else 0.0, 'is_valid': VALUE == 7}\n"
    )
    (d / "pkg").mkdir()
    (d / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (d / "pkg" / "helper.py").write_text("VALUE = 0\n", encoding="utf-8")
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
