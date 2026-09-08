import base64
import tempfile
import hashlib
from pathlib import Path
import subprocess
import sys
import pytest, yaml
from libreevolve.core.yaml_utils import safe_load_unique
from libreevolve.problems.loader import load_problem, Problem

def _make(tmp):
    d = Path(tmp)
    (d / "task_description.txt").write_text("test task")
    (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
        {"name": "score", "direction": "maximize", "primary": True, "bounds": [0.0, 1.0]}]}))
    (d / "validate.py").write_text("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
    (d / "initial_programs").mkdir()
    (d / "initial_programs" / "seed.py").write_text("x = 1")
    return d


def _symlink_or_skip(link: Path, target: Path, *, target_is_directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")


def _junction_or_skip(link: Path, target: Path) -> None:
    if sys.platform != "win32":
        pytest.skip("Windows junctions are only available on Windows")
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")


def test_safe_load_unique_rejects_bare_yaml_alias():
    with pytest.raises(
        yaml.constructor.ConstructorError,
        match="YAML aliases are not supported",
    ):
        safe_load_unique("*missing_anchor\n")


def test_returns_problem():
    with tempfile.TemporaryDirectory() as t:
        assert isinstance(load_problem(_make(t)), Problem)

def test_reads_task_description():
    with tempfile.TemporaryDirectory() as t:
        assert load_problem(_make(t)).task_description == "test task"


def test_preserves_task_description_text_after_non_empty_validation():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        text = "  indented objective\n\nKeep this trailing blank line.\n\n"
        (d / "task_description.txt").write_text(text, encoding="utf-8")
        assert load_problem(d).task_description == text


def test_rejects_empty_task_description():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "task_description.txt").write_text("  \n\t")
        with pytest.raises(ValueError, match="non-empty task description"):
            load_problem(d)


def test_rejects_missing_task_description():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "task_description.txt").unlink()
        with pytest.raises(FileNotFoundError, match="task_description"):
            load_problem(d)


def test_rejects_task_description_directory_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "task_description.txt").unlink()
        (d / "task_description.txt").mkdir()
        with pytest.raises(ValueError, match=r"task_description\.txt.*regular file"):
            load_problem(d)


def test_rejects_invalid_task_description_encoding_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        path = d / "task_description.txt"
        path.write_bytes(b"task \xff\n")
        with pytest.raises(ValueError, match=r"task_description\.txt.*valid UTF-8"):
            load_problem(d)


def test_rejects_unreadable_task_description_with_redacted_diagnostic(monkeypatch):
    token = "sk-proj_taskreadsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        task_path = d / "task_description.txt"
        original_read_text = Path.read_text

        def fake_read_text(path, *args, **kwargs):
            if path == task_path:
                raise PermissionError(f"cannot read api_key={token}")
            return original_read_text(path, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", fake_read_text)

        with pytest.raises(ValueError, match=r"task_description\.txt.*could not be read") as exc_info:
            load_problem(d)

        message = str(exc_info.value)
        assert token not in message
        assert "[REDACTED]" in message


def test_reads_primary_metric():
    with tempfile.TemporaryDirectory() as t:
        assert load_problem(_make(t)).primary_metric == "score"

def test_reads_seeds():
    with tempfile.TemporaryDirectory() as t:
        p = load_problem(_make(t))
        assert len(p.initial_programs) == 1 and "x = 1" in p.initial_programs[0]
        assert p.initial_workspaces[0].primary_file == "seed.py"
        assert p.initial_workspace_sources == [
            {
                "seed_index": 0,
                "seed_source_path": "initial_programs/seed.py",
                "seed_source_kind": "file",
                "primary_file": "seed.py",
                "file_count": 1,
                "files": ["seed.py"],
            }
        ]


def test_allows_missing_validate_py_for_embedded_only_problem_config():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "validate.py").unlink()
        (d / "config.yaml").write_text(
            "eval_stages:\n"
            "  - name: candidate_eval\n"
            "    mode: embedded_evaluate\n"
            "    eval_inputs:\n"
            "      score: 0.5\n",
            encoding="utf-8",
        )

        p = load_problem(d)

        assert p.validate_path == d / "validate.py"
        assert not p.validate_path.exists()
        assert len(p.initial_programs) == 1


def test_requires_validate_py_when_problem_config_has_external_stage():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "validate.py").unlink()
        (d / "config.yaml").write_text(
            "eval_stages:\n"
            "  - name: external_gate\n",
            encoding="utf-8",
        )

        with pytest.raises(FileNotFoundError, match="validate.py"):
            load_problem(d)


def test_rejects_secret_like_top_level_seed_file_path_without_leak():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        secret_name = "api_key=sk-proj_seedpathsecret1234567890.py"  # pragma: allowlist secret
        (seed_root / secret_name).write_text("x = 1\n", encoding="utf-8")

        with pytest.raises(ValueError, match="secret-like text") as excinfo:
            load_problem(d)

        assert "sk-proj_seedpathsecret" not in str(excinfo.value)


def test_raises_on_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_problem("/nonexistent/problem")


def test_rejects_symlinked_problem_root(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    _make(target)
    link = tmp_path / "linked_problem"
    _symlink_or_skip(link, target, target_is_directory=True)

    with pytest.raises(ValueError, match="Problem directory links are not supported"):
        load_problem(link)


def test_rejects_junction_problem_root(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    _make(target)
    link = tmp_path / "linked_problem"
    _junction_or_skip(link, target)

    with pytest.raises(ValueError, match="Problem directory links are not supported"):
        load_problem(link)


def test_raises_on_no_seeds():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"): f.unlink()
        with pytest.raises(ValueError, match="No seed programs"):
            load_problem(d)


@pytest.mark.parametrize("filename", ["task_description.txt", "metrics.yaml", "validate.py"])
def test_rejects_symlinked_required_problem_files(tmp_path, filename):
    d = _make(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    target = outside / filename
    target.write_text((d / filename).read_text(encoding="utf-8"), encoding="utf-8")
    (d / filename).unlink()
    _symlink_or_skip(d / filename, target)

    escaped = filename.replace(".", r"\.")
    with pytest.raises(ValueError, match=rf"{escaped} links are not supported"):
        load_problem(d)


@pytest.mark.parametrize("filename", ["task_description.txt", "metrics.yaml", "validate.py"])
def test_rejects_junction_backed_required_problem_file_paths(tmp_path, filename):
    d = _make(tmp_path)
    target = tmp_path / f"{filename}_junction_target"
    target.mkdir()
    (d / filename).unlink()
    _junction_or_skip(d / filename, target)

    escaped = filename.replace(".", r"\.")
    with pytest.raises(ValueError, match=rf"{escaped} links are not supported"):
        load_problem(d)


def test_rejects_validate_py_directory_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "validate.py").unlink()
        (d / "validate.py").mkdir()
        with pytest.raises(ValueError, match=r"validate\.py.*regular file"):
            load_problem(d)


def test_rejects_validate_py_stat_failure_with_redacted_diagnostic(monkeypatch):
    token = "sk-proj_validatestatsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        validate = d / "validate.py"
        original_is_file = Path.is_file

        def fake_is_file(path, *args, **kwargs):
            if path == validate:
                raise PermissionError(f"cannot stat api_key={token}")
            return original_is_file(path, *args, **kwargs)

        monkeypatch.setattr(Path, "is_file", fake_is_file)

        with pytest.raises(ValueError, match=r"validate\.py.*could not be inspected") as exc_info:
            load_problem(d)

        message = str(exc_info.value)
        assert token not in message
        assert "[REDACTED]" in message


def test_bin_packing_example_loads():
    examples = Path(__file__).parent.parent.parent / "libreevolve/problems/examples/bin_packing"
    p = load_problem(examples)
    assert p.name == "bin_packing" and len(p.initial_programs) >= 1

def test_primary_bounds_default_when_missing():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
            {"name": "score", "direction": "maximize", "primary": True}
        ]}))
        p = load_problem(d)
        assert p.primary_bounds == (0.0, 1.0)

def test_raises_on_malformed_metrics_yaml():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text("not_metrics: true")
        with pytest.raises(ValueError, match="metrics"):
            load_problem(d)


def test_rejects_unsupported_top_level_metrics_yaml_keys_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(
            "metrics:\n"
            "  - name: score\n"
            "    direction: maximize\n"
            "    primary: true\n"
            "    bounds: [0, 1]\n"
            "metricz: []\n"
            "primary_metric: score\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match=r"unsupported top-level metrics\.yaml fields"):
            load_problem(d)


def test_rejects_non_string_top_level_metrics_yaml_keys_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(
            "metrics:\n"
            "  - name: score\n"
            "    direction: maximize\n"
            "    primary: true\n"
            "    bounds: [0, 1]\n"
            "1: bad\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match=r"top-level metrics\.yaml keys must be strings"):
            load_problem(d)


def test_rejects_invalid_metrics_yaml_syntax_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text("metrics: [", encoding="utf-8")
        with pytest.raises(ValueError, match=r"metrics\.yaml.*invalid metrics\.yaml YAML"):
            load_problem(d)


def test_rejects_metrics_yaml_directory_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").unlink()
        (d / "metrics.yaml").mkdir()
        with pytest.raises(ValueError, match=r"metrics\.yaml.*regular file"):
            load_problem(d)


def test_rejects_invalid_metrics_encoding_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_bytes(b"metrics: \xff\n")
        with pytest.raises(ValueError, match=r"metrics\.yaml.*valid UTF-8"):
            load_problem(d)


def test_rejects_unreadable_metrics_yaml_with_redacted_diagnostic(monkeypatch):
    token = "sk-proj_metricsreadsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        metrics_path = d / "metrics.yaml"
        original_read_text = Path.read_text

        def fake_read_text(path, *args, **kwargs):
            if path == metrics_path:
                raise PermissionError(f"cannot read api_key={token}")
            return original_read_text(path, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", fake_read_text)

        with pytest.raises(ValueError, match=r"metrics\.yaml.*could not be read") as exc_info:
            load_problem(d)

        message = str(exc_info.value)
        assert token not in message
        assert "[REDACTED]" in message


def test_rejects_duplicate_metrics_yaml_keys_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(
            "metrics:\n"
            "  - name: score\n"
            "    direction: maximize\n"
            "    primary: true\n"
            "    bounds: [0, 1]\n"
            "    bounds: [0, 10]\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match=r"duplicate key"):
            load_problem(d)


@pytest.mark.parametrize(
    ("yaml_text", "message"),
    [
        (
            "metrics: &metric_list\n"
            "  - name: score\n"
            "    direction: maximize\n"
            "    primary: true\n"
            "    bounds: [0, 1]\n",
            "YAML anchors are not supported",
        ),
        (
            "metric: &metric\n"
            "  name: score\n"
            "  direction: maximize\n"
            "  primary: true\n"
            "  bounds: [0, 1]\n"
            "metrics: [*metric]\n",
            "YAML anchors are not supported",
        ),
    ],
)
def test_rejects_metrics_yaml_anchors_and_aliases(yaml_text, message):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(yaml_text, encoding="utf-8")

        with pytest.raises(ValueError) as excinfo:
            load_problem(d)
        error = str(excinfo.value)
        assert "invalid metrics.yaml YAML" in error
        assert message in error


def test_redacts_secret_like_duplicate_metrics_yaml_key():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        secret_key = "api_key=sk-proj_yamldiagsecret1234567890"
        (d / "metrics.yaml").write_text(
            f"{secret_key}: 1\n{secret_key}: 2\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError) as excinfo:
            load_problem(d)
        message = str(excinfo.value)
        assert "invalid metrics.yaml YAML" in message
        assert "duplicate key" in message
        assert secret_key not in message
        assert "api_key=[REDACTED]" in message


def test_rejects_non_string_metric_mapping_keys_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(
            "metrics:\n"
            "  - name: score\n"
            "    1: bad\n"
            "    unknown: bad\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match=r"metric #1 keys must be strings"):
            load_problem(d)


@pytest.mark.parametrize("value", [-1, True, "1.0", float("inf")])
def test_rejects_invalid_metric_weight(value):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(
            yaml.dump({
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0, 1],
                        "weight": value,
                    }
                ]
            }),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="weight must be"):
            load_problem(d)


def test_accepts_metric_weight_in_schema():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(
            yaml.dump({
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0, 1],
                        "weight": 2.5,
                    }
                ]
            }),
            encoding="utf-8",
        )

        problem = load_problem(d)

        assert problem.metrics[0]["weight"] == 2.5


def test_direct_problem_rejects_non_string_metric_mapping_keys():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        validate = d / "validate.py"
        validate.write_text("def evaluate(c): return {'score': 1.0, 'is_valid': True}")
        with pytest.raises(ValueError, match=r"metric #1 keys must be strings"):
            Problem(
                name="t",
                task_description="t",
                metrics=[{"name": "score", 1: "bad"}],
                primary_metric="score",
                primary_bounds=(0.0, 1.0),
                validate_path=validate,
                initial_programs=["x=1"],
                problem_dir=d,
            )


@pytest.mark.parametrize(
    ("metrics", "message"),
    [
        ([{"direction": "maximize", "primary": True}], "non-empty name"),
        (
            [
                {"name": "score", "direction": "maximize", "primary": True},
                {"name": "score", "direction": "maximize"},
            ],
            "duplicate metric name",
        ),
        ([{"name": "is_valid", "direction": "maximize", "primary": True}], "reserved"),
        ([{"name": "score\u202e", "direction": "maximize", "primary": True}], "format controls"),
        ([{"name": "score\u200d", "direction": "maximize", "primary": True}], "format controls"),
        ([{"name": "score\nsecret", "direction": "maximize", "primary": True}], "safe metric name"),
        ([{"name": " score", "direction": "maximize", "primary": True}], "safe metric name"),
        ([{"name": "score ", "direction": "maximize", "primary": True}], "safe metric name"),
        ([{"name": "score-secret", "direction": "maximize", "primary": True}], "safe metric name"),
        ([{"name": "1score", "direction": "maximize", "primary": True}], "safe metric name"),
        ([{"name": "cafe\u00e9", "direction": "maximize", "primary": True}], "safe metric name"),
        ([{"name": "score.", "direction": "maximize", "primary": True}], "safe metric name"),
        ([{"name": "score", "direction": "higher", "primary": True}], "direction"),
        (
            [{"name": "score", "direction": "maximize", "primary": True, "unit": "points"}],
            "unsupported fields",
        ),
        (
            [
                {"name": "score", "direction": "maximize", "primary": True},
                {"name": "speed", "direction": "maximize", "primary": True},
            ],
            "only one metric can be primary",
        ),
        ([{"name": "score", "direction": "maximize", "primary": "false"}], "primary must be boolean"),
        ([{"name": "score", "direction": "maximize", "primary": 1}], "primary must be boolean"),
        ([{"name": "score", "direction": "maximize", "bounds": [0.0]}], "bounds"),
        (
            [{"name": "score", "direction": "maximize", "bounds": [0.0, "nan"]}],
            "finite",
        ),
        ([{"name": "score", "direction": "maximize", "bounds": [False, True]}], "numeric"),
        ([{"name": "score", "direction": "maximize", "bounds": [1.0, 1.0]}], "strictly"),
        ([{"name": "score", "direction": "maximize", "bounds": [2.0, 1.0]}], "strictly"),
    ],
)
def test_validates_metric_schema(metrics, message):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(yaml.dump({"metrics": metrics}))
        with pytest.raises(ValueError, match=message):
            load_problem(d)


def test_validates_secondary_metric_bounds():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
            {"name": "score", "direction": "maximize", "primary": True},
            {"name": "runtime", "direction": "minimize", "bounds": "fast"},
        ]}))
        with pytest.raises(ValueError, match="runtime.*bounds"):
            load_problem(d)


def test_objective_metric_helpers_require_declared_metrics():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(
            yaml.dump({
                "metrics": [
                    {"name": "score", "direction": "maximize", "primary": True},
                    {"name": "runtime", "direction": "minimize", "bounds": [0.0, 10.0]},
                ]
            })
        )
        problem = load_problem(d)

        assert problem.metric("score")["primary"] is True
        assert problem.metric_bounds("runtime") == (0.0, 10.0)
        assert problem.metric_direction("runtime") == "minimize"
        assert problem.normalize_metric("runtime", 2.0) == 0.8
        with pytest.raises(KeyError, match="Unknown metric 'unknown'"):
            problem.metric("unknown")
        with pytest.raises(KeyError, match="Unknown metric 'unknown'"):
            problem.metric_bounds("unknown")
        with pytest.raises(KeyError, match="Unknown metric 'unknown'"):
            problem.metric_direction("unknown")
        with pytest.raises(KeyError, match="Unknown metric 'unknown'"):
            problem.normalize_metric("unknown", 0.25)


def test_normalizes_minimize_metric():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
            {"name": "loss", "direction": "minimize", "primary": True, "bounds": [0.0, 10.0]}
        ]}))
        p = load_problem(d)
        assert p.fitness_from_metrics({"loss": 2.0}) == 0.8


def test_accepts_dotted_metric_namespaces():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(
            yaml.dump({
                "metrics": [
                    {
                        "name": "quality.score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0.0, 1.0],
                    },
                    {
                        "name": "runtime_ms",
                        "direction": "minimize",
                        "bounds": [0.0, 10.0],
                    },
                ]
            }),
            encoding="utf-8",
        )

        p = load_problem(d)

        assert [metric["name"] for metric in p.metrics] == ["quality.score", "runtime_ms"]
        assert p.primary_metric == "quality.score"


def test_direct_problem_rejects_duplicate_metric_schema():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        with pytest.raises(ValueError, match="duplicate metric name"):
            Problem(
                name="direct",
                task_description="task",
                metrics=[
                    {"name": "score", "direction": "maximize", "bounds": [0.0, 1.0]},
                    {"name": "score", "direction": "minimize", "bounds": [0.0, 10.0]},
                ],
                primary_metric="score",
                primary_bounds=(0.0, 1.0),
                validate_path=d / "validate.py",
                initial_programs=["x=1"],
                problem_dir=d,
            )


def test_direct_problem_rejects_missing_primary_metric():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        with pytest.raises(ValueError, match="primary_metric must reference"):
            Problem(
                name="direct",
                task_description="task",
                metrics=[{"name": "score", "direction": "maximize", "bounds": [0.0, 1.0]}],
                primary_metric="missing_score",
                primary_bounds=(0.0, 1.0),
                validate_path=d / "validate.py",
                initial_programs=["x=1"],
                problem_dir=d,
            )


def test_direct_problem_rejects_conflicting_primary_metric_flags():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        with pytest.raises(ValueError, match="conflicts with primary metric"):
            Problem(
                name="direct",
                task_description="task",
                metrics=[
                    {"name": "score", "direction": "maximize", "primary": True},
                    {"name": "runtime", "direction": "minimize"},
                ],
                primary_metric="runtime",
                primary_bounds=(0.0, 1.0),
                validate_path=d / "validate.py",
                initial_programs=["x=1"],
                problem_dir=d,
            )


def test_direct_problem_normalizes_effective_metric_schema():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        problem = Problem(
            name="direct",
            task_description="task",
            metrics=[
                {"name": "score", "direction": "maximize", "bounds": [0.0, 1.0]},
                {"name": "runtime", "direction": "minimize", "bounds": [0.0, 10.0]},
            ],
            primary_metric="runtime",
            primary_bounds=(0.0, 10.0),
            validate_path=d / "validate.py",
            initial_programs=["x=1"],
            problem_dir=d,
        )

        assert problem.primary_metric == "runtime"
        assert problem.primary_bounds == (0.0, 10.0)
        assert [metric["primary"] for metric in problem.metrics] == [False, True]
        assert problem.validate_path == d / "validate.py"


def test_effective_metric_schema_is_immutable_after_construction():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        source_metrics = [
            {"name": "score", "direction": "maximize", "bounds": [0.0, 1.0]},
            {"name": "runtime", "direction": "minimize", "bounds": [0.0, 10.0]},
        ]
        problem = Problem(
            name="direct",
            task_description="task",
            metrics=source_metrics,
            primary_metric="score",
            primary_bounds=(0.0, 1.0),
            validate_path=d / "validate.py",
            initial_programs=["x=1"],
            problem_dir=d,
        )

        source_metrics[0]["bounds"] = [False, True]
        source_metrics[0]["direction"] = "minimize"
        assert problem.metric_bounds("score") == (0.0, 1.0)
        assert problem.metric_direction("score") == "maximize"
        assert problem.normalize_metric("score", 0.25) == 0.25

        with pytest.raises(AttributeError):
            problem.metrics.append({"name": "bonus"})  # type: ignore[attr-defined]
        with pytest.raises(TypeError):
            problem.metrics[0]["direction"] = "minimize"  # type: ignore[index]
        with pytest.raises(TypeError):
            problem.metrics[0]["bounds"][0] = 999.0  # type: ignore[index]

        schema = problem.objective_schema()
        assert schema["metrics"][0]["bounds"] == [0.0, 1.0]
        schema["metrics"][0]["bounds"][0] = 999.0
        assert problem.metric_bounds("score") == (0.0, 1.0)


def test_problem_metric_schema_supports_non_evaluator_sourced_secondary_metrics():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        problem = Problem(
            name="direct",
            task_description="task",
            metrics=[
                {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
                {
                    "name": "final_quality",
                    "bounds": [0.0, 1.0],
                    "source": "final_fitness",
                },
            ],
            primary_metric="score",
            primary_bounds=(0.0, 1.0),
            validate_path=d / "validate.py",
            initial_programs=["x=1"],
            problem_dir=d,
        )

        assert problem.metric("score")["source"] == "evaluator"
        assert problem.metric("final_quality")["source"] == "final_fitness"
        assert problem.objective_schema()["metrics"][1] == {
            "name": "final_quality",
            "direction": "maximize",
            "bounds": [0.0, 1.0],
            "source": "final_fitness",
            "weight": 1.0,
            "primary": False,
        }


@pytest.mark.parametrize(
    ("metric", "message"),
    [
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": "feedback"},
            "source must be 'evaluator' or 'final_fitness'",
        ),
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": "plugin"},
            "source must be 'evaluator' or 'final_fitness'",
        ),
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": "final_fitness"},
            "primary metric .* source 'evaluator'",
        ),
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": "grader"},
            "source must be 'evaluator' or 'final_fitness'",
        ),
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": 7},
            "source must be 'evaluator' or 'final_fitness'",
        ),
    ],
)
def test_problem_metric_schema_rejects_invalid_metric_source(metric, message):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        with pytest.raises(ValueError, match=message):
            Problem(
                name="direct",
                task_description="task",
                metrics=[metric],
                primary_metric="score",
                primary_bounds=(0.0, 1.0),
                validate_path=d / "validate.py",
                initial_programs=["x=1"],
                problem_dir=d,
            )


@pytest.mark.parametrize(
    ("primary_bounds", "message"),
    [
        ((999.0, 1000.0), "primary_bounds must match declared primary metric bounds"),
        ((float("nan"), 1.0), "primary_bounds must be numeric finite"),
        ((0.0, float("inf")), "primary_bounds must be numeric finite"),
        ("not-bounds", "primary_bounds must be numeric finite"),
        ([False, True], "primary_bounds must be numeric finite"),
        ((1.0, 0.0), "primary_bounds must be strictly increasing"),
    ],
)
def test_direct_problem_rejects_invalid_primary_bounds(primary_bounds, message):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        with pytest.raises(ValueError, match=message):
            Problem(
                name="direct",
                task_description="task",
                metrics=[
                    {"name": "score", "direction": "maximize", "bounds": [0.0, 1.0]},
                ],
                primary_metric="score",
                primary_bounds=primary_bounds,
                validate_path=d / "validate.py",
                initial_programs=["x=1"],
                problem_dir=d,
            )


def test_direct_problem_rejects_boolean_metric_bounds():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        with pytest.raises(ValueError, match="Metric 'score' bounds must be numeric"):
            Problem(
                name="direct",
                task_description="task",
                metrics=[
                    {"name": "score", "direction": "maximize", "bounds": [False, True]},
                ],
                primary_metric="score",
                primary_bounds=(0.0, 1.0),
                validate_path=d / "validate.py",
                initial_programs=["x=1"],
                problem_dir=d,
            )


def test_reads_seed_directory_as_workspace():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"):
            f.unlink()
        seed = d / "initial_programs" / "seed_a"
        seed.mkdir()
        (seed / "main.py").write_text("from helper import value\n")
        (seed / "helper.py").write_text("value = 1\n")
        p = load_problem(d)
        assert p.initial_workspaces[0].primary_file == "main.py"
        assert sorted(p.initial_workspaces[0].files) == ["helper.py", "main.py"]
        assert p.initial_workspace_sources == [
            {
                "seed_index": 0,
                "seed_source_path": "initial_programs/seed_a",
                "seed_source_kind": "directory",
                "primary_file": "main.py",
                "file_count": 2,
                "files": ["helper.py", "main.py"],
            }
        ]


def test_skips_non_utf8_file_inside_seed_workspace_with_hash_provenance():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"):
            f.unlink()
        seed = d / "initial_programs" / "seed_a"
        seed.mkdir()
        payload = b"\xff\x00fixture"
        (seed / "main.py").write_text("x = 1\n", encoding="utf-8")
        (seed / "fixture.bin").write_bytes(payload)

        p = load_problem(d)

        assert p.initial_workspaces[0].files == {"main.py": "x = 1\n"}
        assert p.initial_workspaces[0].static_files == (
            {
                "path": "fixture.bin",
                "kind": "binary",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "source_kind": "seed_workspace_file",
                "source_path": "initial_programs/seed_a/fixture.bin",
                "mutation_policy": "immutable",
                "content_b64": base64.b64encode(payload).decode("ascii"),
            },
        )
        assert p.initial_workspace_sources == [
            {
                "seed_index": 0,
                "seed_source_path": "initial_programs/seed_a",
                "seed_source_kind": "directory",
                "primary_file": "main.py",
                "file_count": 1,
                "files": ["main.py"],
                "static_file_count": 1,
                "static_files": ["fixture.bin"],
            }
        ]
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/seed_a/fixture.bin",
                "reason": "non_utf8_seed_workspace_file",
                "entry_type": "file",
                "source_type": "bin",
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "hash_scope": "file_bytes",
            }
        ]


def test_non_utf8_only_seed_workspace_does_not_count_as_seed():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"):
            f.unlink()
        seed = d / "initial_programs" / "binary_only"
        seed.mkdir()
        (seed / "fixture.bin").write_bytes(b"\xff\x00fixture")

        with pytest.raises(ValueError, match="skipped seed entries") as excinfo:
            load_problem(d)

        message = str(excinfo.value)
        assert "initial_programs/binary_only/fixture.bin:non_utf8_seed_workspace_file" in message
        assert "initial_programs/binary_only:all_seed_workspace_files_skipped" in message


def test_rejects_secret_like_seed_workspace_directory_path_without_leak():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"):
            f.unlink()
        seed = d / "initial_programs" / "api_key=sk-proj_seedworkspacepathsecret1234567890"  # pragma: allowlist secret
        seed.mkdir()
        (seed / "main.py").write_text("x = 1\n", encoding="utf-8")

        with pytest.raises(ValueError, match="Seed source path must not contain secret-like text") as excinfo:
            load_problem(d)

        assert "sk-proj_seedworkspacepathsecret" not in str(excinfo.value)


def test_skips_hidden_top_level_seed_file():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / ".secret.py").write_text("secret_seed = True\n", encoding="utf-8")
        (seed_root / "visible.py").write_text("visible_seed = True\n", encoding="utf-8")

        p = load_problem(d)

        assert len(p.initial_workspaces) == 1
        assert p.initial_workspaces[0].files == {"visible.py": "visible_seed = True\n"}
        assert p.initial_workspace_sources[0]["seed_source_path"] == "initial_programs/visible.py"
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/.secret.py",
                "reason": "top_level_hidden_seed_entry",
                "entry_type": "file",
            }
        ]


def test_skips_hidden_and_cache_seed_directories():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        hidden = seed_root / ".secret_seed"
        hidden.mkdir()
        (hidden / "main.py").write_text("hidden_seed = True\n", encoding="utf-8")
        cache = seed_root / "__pycache__"
        cache.mkdir()
        (cache / "main.py").write_text("cache_seed = True\n", encoding="utf-8")
        visible = seed_root / "visible_seed"
        visible.mkdir()
        (visible / "main.py").write_text("visible_seed = True\n", encoding="utf-8")

        p = load_problem(d)

        assert len(p.initial_workspaces) == 1
        assert p.initial_workspaces[0].files == {"main.py": "visible_seed = True\n"}
        assert p.initial_workspace_sources[0]["seed_source_path"] == "initial_programs/visible_seed"
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/.secret_seed",
                "reason": "top_level_hidden_seed_entry",
                "entry_type": "directory",
            },
            {
                "seed_source_path": "initial_programs/__pycache__",
                "reason": "top_level_seed_cache",
                "entry_type": "directory",
            },
        ]


def test_hidden_or_cache_only_seed_directories_do_not_count_as_seeds():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        hidden = seed_root / ".secret_seed"
        hidden.mkdir()
        (hidden / "main.py").write_text("hidden_seed = True\n", encoding="utf-8")
        cache = seed_root / "__pycache__"
        cache.mkdir()
        (cache / "main.py").write_text("cache_seed = True\n", encoding="utf-8")

        with pytest.raises(ValueError, match="skipped seed entries") as excinfo:
            load_problem(d)

        message = str(excinfo.value)
        assert "initial_programs/.secret_seed:top_level_hidden_seed_entry" in message
        assert "initial_programs/__pycache__:top_level_seed_cache" in message


def test_records_hidden_files_skipped_inside_visible_seed_workspace():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        seed = seed_root / "visible_seed"
        seed.mkdir()
        (seed / "main.py").write_text("visible_seed = True\n", encoding="utf-8")
        (seed / ".config.py").write_text("hidden_config = True\n", encoding="utf-8")
        cache = seed / "__pycache__"
        cache.mkdir()
        (cache / "cached.py").write_text("cached = True\n", encoding="utf-8")

        p = load_problem(d)

        assert p.initial_workspaces[0].files == {"main.py": "visible_seed = True\n"}
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/visible_seed/.config.py",
                "reason": "hidden_seed_workspace_path",
                "entry_type": "file",
            },
            {
                "seed_source_path": "initial_programs/visible_seed/__pycache__",
                "reason": "seed_workspace_cache_path",
                "entry_type": "directory",
            },
            {
                "seed_source_path": "initial_programs/visible_seed/__pycache__/cached.py",
                "reason": "seed_workspace_cache_path",
                "entry_type": "file",
            },
        ]


def test_seed_policy_allows_explicit_hidden_workspace_file():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / "seed_policy.yaml").write_text(
            yaml.dump({"include": ["visible_seed/.config.py"]}),
            encoding="utf-8",
        )
        seed = seed_root / "visible_seed"
        seed.mkdir()
        (seed / "main.py").write_text("visible_seed = True\n", encoding="utf-8")
        (seed / ".config.py").write_text("hidden_config = True\n", encoding="utf-8")

        p = load_problem(d)

        workspace = p.initial_workspaces[0]
        assert workspace.files == {
            ".config.py": "hidden_config = True\n",
            "main.py": "visible_seed = True\n",
        }
        assert workspace.allowed_reserved_paths == frozenset({".config.py"})
        assert p.initial_workspace_sources == [
            {
                "seed_index": 0,
                "seed_source_path": "initial_programs/visible_seed",
                "seed_source_kind": "directory",
                "primary_file": "main.py",
                "file_count": 2,
                "files": [".config.py", "main.py"],
                "allowed_reserved_paths": [".config.py"],
            }
        ]
        assert p.initial_workspace_skipped == []
        assert p.initial_workspace_policy == {
            "policy": "skip_reserved_seed_paths_by_default",
            "reserved_components": ["dot-prefixed", "__pycache__"],
            "source": "seed_policy.yaml",
            "include": ["visible_seed/.config.py"],
            "exclude": [],
            "exclude_precedence": True,
        }


def test_seed_policy_selects_non_python_primary_file_for_workspace():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / "seed_policy.yaml").write_text(
            yaml.dump({"primary_file": "solution.expr"}),
            encoding="utf-8",
        )
        seed = seed_root / "expression_seed"
        seed.mkdir()
        (seed / "solution.expr").write_text("1 + 1\n", encoding="utf-8")
        (seed / "README.txt").write_text("expression fixture\n", encoding="utf-8")

        problem = load_problem(d)

        workspace = problem.initial_workspaces[0]
        assert workspace.primary_file == "solution.expr"
        assert workspace.code == "1 + 1\n"
        assert problem.initial_workspace_policy["primary_file"] == "solution.expr"


def test_seed_policy_rejects_missing_configured_primary_file():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / "seed_policy.yaml").write_text(
            yaml.dump({"primary_file": "solution.expr"}),
            encoding="utf-8",
        )
        seed = seed_root / "expression_seed"
        seed.mkdir()
        (seed / "other.txt").write_text("missing primary\n", encoding="utf-8")

        with pytest.raises(ValueError, match="primary_file is not present"):
            load_problem(d)


def test_seed_policy_allows_top_level_hidden_seed_file():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / "seed_policy.yaml").write_text(
            yaml.dump({"include": [".seed.py"]}),
            encoding="utf-8",
        )
        (seed_root / ".seed.py").write_text("hidden_seed = True\n", encoding="utf-8")

        p = load_problem(d)

        workspace = p.initial_workspaces[0]
        assert workspace.files == {".seed.py": "hidden_seed = True\n"}
        assert workspace.primary_file == ".seed.py"
        assert workspace.allowed_reserved_paths == frozenset({".seed.py"})
        assert p.initial_workspace_sources[0]["seed_source_path"] == "initial_programs/.seed.py"
        assert p.initial_workspace_sources[0]["allowed_reserved_paths"] == [".seed.py"]


def test_seed_policy_allows_explicit_cache_workspace_file():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / "seed_policy.yaml").write_text(
            yaml.dump({"include": ["visible_seed/__pycache__/cached.py"]}),
            encoding="utf-8",
        )
        seed = seed_root / "visible_seed"
        seed.mkdir()
        (seed / "main.py").write_text("visible_seed = True\n", encoding="utf-8")
        cache = seed / "__pycache__"
        cache.mkdir()
        (cache / "cached.py").write_text("cached = True\n", encoding="utf-8")

        p = load_problem(d)

        workspace = p.initial_workspaces[0]
        assert sorted(workspace.files) == ["__pycache__/cached.py", "main.py"]
        assert workspace.allowed_reserved_paths == frozenset({"__pycache__/cached.py"})
        assert p.initial_workspace_sources[0]["allowed_reserved_paths"] == [
            "__pycache__/cached.py"
        ]
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/visible_seed/__pycache__",
                "reason": "seed_workspace_cache_path",
                "entry_type": "directory",
            }
        ]


def test_seed_policy_exclude_takes_precedence_over_include():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / "seed_policy.yaml").write_text(
            yaml.dump(
                {
                    "include": ["visible_seed/.config.py"],
                    "exclude": ["visible_seed/.config.py"],
                }
            ),
            encoding="utf-8",
        )
        seed = seed_root / "visible_seed"
        seed.mkdir()
        (seed / "main.py").write_text("visible_seed = True\n", encoding="utf-8")
        (seed / ".config.py").write_text("hidden_config = True\n", encoding="utf-8")

        p = load_problem(d)

        assert p.initial_workspaces[0].files == {"main.py": "visible_seed = True\n"}
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/visible_seed/.config.py",
                "reason": "seed_policy_excluded",
                "entry_type": "file",
            }
        ]


def test_seed_policy_broad_include_does_not_opt_into_reserved_paths():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / "seed_policy.yaml").write_text(
            yaml.dump({"include": ["visible_seed/**"]}),
            encoding="utf-8",
        )
        seed = seed_root / "visible_seed"
        seed.mkdir()
        (seed / "main.py").write_text("visible_seed = True\n", encoding="utf-8")
        (seed / ".config.py").write_text("hidden_config = True\n", encoding="utf-8")

        p = load_problem(d)

        assert p.initial_workspaces[0].files == {"main.py": "visible_seed = True\n"}
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/visible_seed/.config.py",
                "reason": "hidden_seed_workspace_path",
                "entry_type": "file",
            }
        ]


def test_seed_policy_rejects_unsupported_fields():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed_policy.yaml").write_text(
            yaml.dump({"include": ["seed.py"], "mode": "unsafe"}),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="unsupported seed policy fields"):
            load_problem(d)


def test_records_empty_and_fully_skipped_visible_seed_directories():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").write_text("x = 1\n", encoding="utf-8")
        empty = seed_root / "empty_seed"
        empty.mkdir()
        hidden_only = seed_root / "hidden_only"
        hidden_only.mkdir()
        (hidden_only / ".config.py").write_text("hidden = True\n", encoding="utf-8")

        p = load_problem(d)

        skipped = {
            record["seed_source_path"]: record
            for record in p.initial_workspace_skipped
        }
        assert skipped["initial_programs/empty_seed"]["reason"] == (
            "empty_seed_workspace"
        )
        assert skipped["initial_programs/hidden_only/.config.py"]["reason"] == (
            "hidden_seed_workspace_path"
        )
        assert skipped["initial_programs/hidden_only"]["reason"] == (
            "all_seed_workspace_files_skipped"
        )
        assert skipped["initial_programs/hidden_only"]["skipped_file_count"] == 1


def test_records_unsupported_top_level_seed_files_and_no_seed_error():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        (seed_root / "notes.txt").write_text("not python\n", encoding="utf-8")

        with pytest.raises(ValueError, match="unsupported_top_level_seed_file") as excinfo:
            load_problem(d)

        assert "initial_programs/notes.txt:unsupported_top_level_seed_file" in str(
            excinfo.value
        )


def test_records_text_only_seed_workspace_without_python_primary():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        text_only = seed_root / "text_only"
        text_only.mkdir()
        (text_only / "README.md").write_text("# not python\n", encoding="utf-8")
        (text_only / "data.txt").write_text("data\n", encoding="utf-8")
        (seed_root / "visible.py").write_text("x = 1\n", encoding="utf-8")

        p = load_problem(d)

        assert len(p.initial_workspaces) == 1
        assert p.initial_workspaces[0].primary_file == "visible.py"
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/text_only",
                "reason": "no_python_seed_primary",
                "entry_type": "directory",
                "file_count": 2,
            }
        ]


def test_no_python_seed_workspace_does_not_count_as_seed():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed_root = d / "initial_programs"
        (seed_root / "seed.py").unlink()
        text_only = seed_root / "text_only"
        text_only.mkdir()
        (text_only / "README.md").write_text("# not python\n", encoding="utf-8")
        (text_only / "data.txt").write_text("data\n", encoding="utf-8")

        with pytest.raises(ValueError, match="skipped seed entries") as excinfo:
            load_problem(d)

        message = str(excinfo.value)
        assert "initial_programs/text_only:no_python_seed_primary" in message


def test_rejects_unicode_equivalent_seed_workspace_paths():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"):
            f.unlink()
        seed = d / "initial_programs" / "seed_a"
        seed.mkdir()
        (seed / "café.py").write_text("value = 1\n", encoding="utf-8")
        (seed / "cafe\u0301.py").write_text("value = 2\n", encoding="utf-8")
        if len([p for p in seed.iterdir() if p.is_file()]) < 2:
            pytest.skip("filesystem normalizes Unicode filenames")

        with pytest.raises(ValueError, match="Duplicate candidate path after normalization"):
            load_problem(d)


def test_rejects_malformed_top_level_seed_evolve_blocks():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed = d / "initial_programs" / "seed.py"
        seed.write_text("# EVOLVE-BLOCK-START core\nvalue = 1\n", encoding="utf-8")

        with pytest.raises(
            ValueError,
            match=r"seed\.py: malformed evolve-block markers: missing_end",
        ):
            load_problem(d)


def test_rejects_secret_like_seed_evolve_block_names():
    token = "sk-proj_seedblocksecret_1234567890"  # pragma: allowlist secret
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed = d / "initial_programs" / "seed.py"
        seed.write_text(
            f"# EVOLVE-BLOCK-START {token}\nvalue = 1\n# EVOLVE-BLOCK-END\n",
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match=r"seed\.py: malformed evolve-block markers: unsafe_name",
        ):
            load_problem(d)


def test_rejects_invalid_top_level_seed_encoding_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed = d / "initial_programs" / "seed.py"
        seed.write_bytes(b"x = \xff\n")

        with pytest.raises(ValueError, match=r"seed\.py.*valid UTF-8"):
            load_problem(d)


def test_rejects_unreadable_top_level_seed_with_redacted_diagnostic(monkeypatch):
    token = "sk-proj_seedreadsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        seed = d / "initial_programs" / "seed.py"
        original_read_text = Path.read_text

        def fake_read_text(path, *args, **kwargs):
            if path == seed:
                raise PermissionError(f"cannot read api_key={token}")
            return original_read_text(path, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", fake_read_text)

        with pytest.raises(ValueError, match=r"seed\.py.*could not be read") as exc_info:
            load_problem(d)

        message = str(exc_info.value)
        assert token not in message
        assert "[REDACTED]" in message


def test_rejects_malformed_workspace_seed_evolve_blocks():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for seed in (d / "initial_programs").glob("*.py"):
            seed.unlink()
        workspace = d / "initial_programs" / "baseline"
        workspace.mkdir()
        (workspace / "main.py").write_text("value = 1\n", encoding="utf-8")
        (workspace / "helper.py").write_text("# EVOLVE-BLOCK-END\n", encoding="utf-8")

        with pytest.raises(
            ValueError,
            match=r"helper\.py: malformed evolve-block markers: orphan_end",
        ):
            load_problem(d)


def test_skips_invalid_workspace_seed_encoding_with_hash_provenance():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for seed in (d / "initial_programs").glob("*.py"):
            seed.unlink()
        workspace = d / "initial_programs" / "baseline"
        workspace.mkdir()
        (workspace / "main.py").write_text("value = 1\n", encoding="utf-8")
        payload = b"value = \xff\n"
        (workspace / "helper.py").write_bytes(payload)

        p = load_problem(d)

        assert p.initial_workspaces[0].files == {"main.py": "value = 1\n"}
        assert p.initial_workspace_skipped == [
            {
                "seed_source_path": "initial_programs/baseline/helper.py",
                "reason": "non_utf8_seed_workspace_file",
                "entry_type": "file",
                "source_type": "py",
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "hash_scope": "file_bytes",
            }
        ]


def test_rejects_unreadable_workspace_seed_file_with_redacted_diagnostic(monkeypatch):
    token = "sk-proj_seedworkspacereadsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for seed in (d / "initial_programs").glob("*.py"):
            seed.unlink()
        workspace = d / "initial_programs" / "baseline"
        workspace.mkdir()
        main = workspace / "main.py"
        helper = workspace / "helper.py"
        main.write_text("from helper import value\n", encoding="utf-8")
        helper.write_text("value = 1\n", encoding="utf-8")
        original_read_text = Path.read_text

        def fake_read_text(path, *args, **kwargs):
            if path == main:
                raise PermissionError(f"cannot read api_key={token}")
            return original_read_text(path, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", fake_read_text)

        with pytest.raises(ValueError, match=r"main\.py.*could not be read") as exc_info:
            load_problem(d)

        message = str(exc_info.value)
        assert token not in message
        assert "[REDACTED]" in message


def test_rejects_linked_initial_programs_root_before_seed_loading(tmp_path, monkeypatch):
    d = _make(tmp_path)
    seed_root = d / "initial_programs"

    def fake_is_link(path):
        return Path(path) == seed_root

    monkeypatch.setattr("libreevolve.problems.loader._is_link", fake_is_link)

    with pytest.raises(ValueError, match="Seed root links are not supported"):
        load_problem(d)


def test_rejects_unreadable_initial_programs_root_with_redacted_diagnostic(
    tmp_path,
    monkeypatch,
):
    token = "sk-proj_seedlistsecret1234567890"
    d = _make(tmp_path)
    seed_root = d / "initial_programs"
    original_iterdir = Path.iterdir

    def fake_iterdir(path):
        if path == seed_root:
            raise PermissionError(f"cannot list api_key={token}")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    with pytest.raises(
        ValueError,
        match=r"initial_programs.*could not be listed",
    ) as exc_info:
        load_problem(d)

    message = str(exc_info.value)
    assert token not in message
    assert "[REDACTED]" in message


def test_missing_initial_programs_root_preserves_no_seed_diagnostic(tmp_path):
    d = _make(tmp_path)
    seed_root = d / "initial_programs"
    for seed in seed_root.glob("*.py"):
        seed.unlink()
    seed_root.rmdir()

    with pytest.raises(ValueError, match="No seed programs"):
        load_problem(d)


def test_rejects_initial_programs_directory_symlink_root(tmp_path):
    d = _make(tmp_path)
    seed_root = d / "initial_programs"
    for seed in seed_root.glob("*.py"):
        seed.unlink()
    seed_root.rmdir()
    outside = tmp_path / "outside_seeds"
    outside.mkdir()
    (outside / "seed.py").write_text("outside_seed = True\n", encoding="utf-8")
    try:
        seed_root.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError, match="Seed root links are not supported"):
        load_problem(d)


def test_allows_marker_like_literals_in_workspace_seed_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for seed in (d / "initial_programs").glob("*.py"):
            seed.unlink()
        workspace = d / "initial_programs" / "baseline"
        workspace.mkdir()
        (workspace / "main.py").write_text(
            'template = """\n'
            "# EVOLVE-BLOCK-START literal\n"
            "string body\n"
            "# EVOLVE-BLOCK-END\n"
            '"""\n'
            "value = 1\n",
            encoding="utf-8",
        )

        p = load_problem(d)

        assert p.initial_workspaces[0].files["main.py"].endswith("value = 1\n")


def test_rejects_seed_workspace_file_symlink_escape(tmp_path):
    d = _make(tmp_path)
    for f in (d / "initial_programs").glob("*.py"):
        f.unlink()
    seed = d / "initial_programs" / "seed_a"
    seed.mkdir()
    (seed / "main.py").write_text("value = 1\n", encoding="utf-8")
    outside = tmp_path / "outside.py"
    outside.write_text("secret = True\n", encoding="utf-8")
    link = seed / "outside.py"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"file symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError, match="Seed workspace links are not supported"):
        load_problem(d)


def test_embedded_only_validator_exemption_requires_every_stage_to_be_embedded():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "validate.py").unlink()
        (d / "config.yaml").write_text(
            "eval_stages:\n"
            "  - name: embedded_gate\n"
            "    mode: embedded_evaluate\n"
            "  - name: external_gate\n"
            "    mode: candidate_runner\n",
            encoding="utf-8",
        )

        with pytest.raises(FileNotFoundError, match="validate.py"):
            load_problem(d)


def test_required_file_error_precedence_keeps_task_description_first():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "task_description.txt").unlink()
        (d / "metrics.yaml").unlink()

        with pytest.raises(FileNotFoundError, match="task_description.txt"):
            load_problem(d)


def _problem_tree_snapshot(root: Path) -> dict[str, tuple[str, bytes | None]]:
    snapshot = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot[relative] = ("directory", None)
        elif path.is_file():
            snapshot[relative] = ("file", path.read_bytes())
        else:
            snapshot[relative] = ("other", None)
    return snapshot


def test_failed_load_has_no_problem_tree_write_side_effects():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text("broken: [", encoding="utf-8")
        before = _problem_tree_snapshot(d)

        with pytest.raises(ValueError, match="metrics.yaml"):
            load_problem(d)

        assert _problem_tree_snapshot(d) == before


def test_rejects_windows_junction_in_seed_workspace(tmp_path):
    if sys.platform != "win32":
        pytest.skip("Windows junction test")

    d = _make(tmp_path)
    for f in (d / "initial_programs").glob("*.py"):
        f.unlink()
    seed = d / "initial_programs" / "seed_a"
    seed.mkdir()
    (seed / "main.py").write_text("value = 1\n", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.py").write_text("secret = True\n", encoding="utf-8")
    link = seed / "linked"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")

    with pytest.raises(ValueError, match="Seed workspace links are not supported"):
        load_problem(d)
