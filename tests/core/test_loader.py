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


def test_reads_codebase_integration_metadata():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "codebase_integration.yaml").write_text(
            yaml.dump(
                {
                    "original_codebase_id": "fixture-lib-1",
                    "pre_marker_source_sha256": [
                        {
                            "path": "src/main.py",
                            "sha256": "a" * 64,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        problem = load_problem(d)

        assert problem.codebase_integration_metadata == {
            "original_codebase_id": "fixture-lib-1",
            "pre_marker_source_sha256": [
                {
                    "path": "src/main.py",
                    "sha256": "a" * 64,
                }
            ],
        }


def test_rejects_duplicate_codebase_integration_metadata_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "codebase_integration.yaml").write_text(
            "original_codebase_id: fixture-lib-1\n",
            encoding="utf-8",
        )
        (d / "codebase_integration.yml").write_text(
            "original_codebase_id: fixture-lib-2\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="use only one codebase integration"):
            load_problem(d)


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


def test_hello_world_example_loads():
    examples = Path(__file__).parent.parent.parent / "libreevolve/problems/examples/hello_world"
    if not examples.exists():
        pytest.skip("hello_world example not present")
    p = load_problem(examples)
    assert p.name == "hello_world" and len(p.initial_programs) >= 1

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


def test_reads_context_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        (d / "context" / "notes.md").write_text("important context")
        p = load_problem(d)
        assert p.context_files["notes.md"] == "important context"
        assert p.context_sources[0]["path"] == "notes.md"
        assert len(p.context_sources[0]["sha256"]) == 64
        assert p.context_sources[0]["extraction_status"] == "ok"
        assert p.context_policy["present"] is True
        assert p.context_policy["selected_count"] == 1
        assert p.context_policy["usable_selected_count"] == 1
        assert p.context_policy["skipped_count"] == 0
        assert p.context_policy["failed_extraction_count"] == 0


def test_reads_nested_context_files_with_manifest_selection():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        (context / "nested").mkdir(parents=True)
        (context / "nested" / "keep.md").write_text("abcdefghijklmnopqrstuvwxyz")
        (context / "nested" / "skip.md").write_text("skip me")
        (context / "top.py").write_text("value = 1\n")
        (context / "ignored.txt").write_text("ignored")
        (context / "context.yaml").write_text(yaml.dump({
            "include": ["nested/*.md", "top.py"],
            "exclude": ["nested/skip.md"],
            "max_chars_per_source": 10,
        }))

        p = load_problem(d)

        assert sorted(p.context_files) == ["nested/keep.md", "top.py"]
        assert "showing first 10 of 26 characters" in p.context_files["nested/keep.md"]
        source = next(s for s in p.context_sources if s["path"] == "nested/keep.md")
        assert source["truncated"] is True
        assert source["excerpt_start"] == 0
        assert source["excerpt_end"] == 10
        assert source["excerpt_policy"] == "head"
        assert source["excerpt_spans"] == [{"start": 0, "end": 10}]
        assert source["max_chars"] == 10
        assert p.context_policy["present"] is True
        assert p.context_policy["manifest"]["path"] == "context.yaml"
        assert len(p.context_policy["manifest"]["sha256"]) == 64
        assert p.context_policy["manifest"]["bytes"] > 0
        assert p.context_policy["include"] == ["nested/*.md", "top.py"]
        assert p.context_policy["exclude"] == ["nested/skip.md"]
        assert p.context_policy["max_chars_per_source"] == 10
        assert p.context_policy["excerpt_policy"] == "head"
        assert p.context_policy["selected_count"] == 2
        assert p.context_policy["include_patterns"] == [
            {"pattern": "nested/*.md", "matches": 2, "selected_matches": 1},
            {"pattern": "top.py", "matches": 1, "selected_matches": 1},
        ]
        assert p.context_policy["unmatched_includes"] == []
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped["nested/skip.md"]["reason"] == "excluded"
        assert len(skipped["nested/skip.md"]["sha256"]) == 64
        assert skipped["ignored.txt"]["reason"] == "not_included"
        assert len(skipped["ignored.txt"]["sha256"]) == 64


def test_context_manifest_records_source_roles():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("use this constraint", encoding="utf-8")
        (context / "formula.md").write_text("score = x + y", encoding="utf-8")
        (context / "context.yaml").write_text(
            yaml.dump(
                {
                    "source_roles": {
                        "notes.md": {
                            "role": "human_instruction",
                            "topic": "local constraints",
                            "section": "operator notes",
                        },
                        "formula.md": {
                            "role": "equation",
                            "topic": "objective formula",
                            "span": "full file",
                        },
                    }
                }
            ),
            encoding="utf-8",
        )

        p = load_problem(d)

        notes = next(s for s in p.context_sources if s["path"] == "notes.md")
        assert notes["source_role_status"] == "classified"
        assert notes["source_role"] == {
            "role": "human_instruction",
            "topic": "local constraints",
            "section": "operator notes",
        }
        assert p.context_policy["source_role_count"] == 2
        assert p.context_policy["source_roles"]["formula.md"]["role"] == "equation"
        selected = {
            item["path"]: item
            for item in p.context_policy["source_selection"]["selected_sources"]
        }
        assert selected["notes.md"]["source_role_status"] == "classified"
        assert selected["notes.md"]["source_role"]["topic"] == "local constraints"


@pytest.mark.parametrize(
    "source_role,expected",
    [
        (
            {"role": "memo", "topic": "x", "section": "notes"},
            r"source_roles\['notes\.md'\]\.role must be one of",
        ),
        (
            {"role": "human_instruction", "section": "notes"},
            r"source_roles\['notes\.md'\]\.topic must be a non-empty string",
        ),
        (
            {"role": "human_instruction", "topic": "x"},
            r"must include at least one source locator",
        ),
    ],
)
def test_context_manifest_rejects_invalid_source_roles(source_role, expected):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("notes", encoding="utf-8")
        (context / "context.yaml").write_text(
            yaml.dump({"source_roles": {"notes.md": source_role}}),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match=expected):
            load_problem(d)


def test_context_policy_hash_changes_when_excluded_file_changes():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "keep.md").write_text("keep")
        skipped = context / "skip.md"
        skipped.write_text("first")
        (context / "context.yaml").write_text(yaml.dump({
            "include": ["*.md"],
            "exclude": ["skip.md"],
        }))

        first = load_problem(d).context_policy["skipped"][0]["sha256"]
        skipped.write_text("second")
        second = load_problem(d).context_policy["skipped"][0]["sha256"]

        assert first != second


def test_context_policy_records_unsupported_context_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / "data.bin").write_bytes(b"binary")

        p = load_problem(d)

        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped["data.bin"]["reason"] == "unsupported_extension"
        assert skipped["data.bin"]["source_type"] == "bin"
        assert len(skipped["data.bin"]["sha256"]) == 64


@pytest.mark.parametrize(
    "name,manifest,expected_reason",
    [
        ("data.bin", {"max_bytes_per_source": 3}, "unsupported_extension"),
        ("skip.md", {"max_bytes_per_source": 3, "exclude": ["skip.md"]}, "excluded"),
        (".hidden.md", {"max_bytes_per_source": 3}, "hidden_not_included"),
        (
            "skip.md",
            {"max_bytes_per_source": 3, "include": ["keep.md"]},
            "not_included",
        ),
    ],
)
def test_context_policy_omits_hash_for_oversized_skipped_sources_before_reading(
    monkeypatch,
    name,
    manifest,
    expected_reason,
):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        keep = context / "keep.md"
        skipped_file = context / name
        keep.write_text("ok", encoding="utf-8")
        skipped_file.write_text("abcdef", encoding="utf-8")
        (context / "context.yaml").write_text(yaml.dump(manifest), encoding="utf-8")
        original_read_bytes = Path.read_bytes

        def fake_read_bytes(path):
            if path == skipped_file:
                raise AssertionError(f"{name} should not be read for skipped hash")
            return original_read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)

        p = load_problem(d)

        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        diagnostic = skipped[name]
        assert diagnostic["reason"] == expected_reason
        assert diagnostic["bytes"] == 6
        assert diagnostic["max_bytes"] == 3
        assert diagnostic["sha256"] is None
        assert diagnostic["read_status"] == "not_read"
        assert diagnostic["hash_omitted_reason"] == "max_source_bytes"


@pytest.mark.parametrize(
    "field",
    [
        "max_bytes_per_source",
        "max_total_bytes",
        "max_pdf_pages",
        "max_pdf_chars",
        "max_context_entries",
        "max_context_depth",
        "max_skipped_diagnostics",
        "max_context_provenance_chars",
    ],
)
@pytest.mark.parametrize("value", [0, -1, True, "10"])
def test_rejects_invalid_context_resource_limits(field, value):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / "context.yaml").write_text(yaml.dump({field: value}))

        with pytest.raises(ValueError, match=rf"{field} must be a positive integer"):
            load_problem(d)


@pytest.mark.parametrize("value", [0, -1, True, "10"])
def test_rejects_invalid_max_selected_context_sources(value):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / "context.yaml").write_text(
            yaml.dump({"max_selected_context_sources": value})
        )

        with pytest.raises(
            ValueError,
            match="max_selected_context_sources must be a positive integer or null",
        ):
            load_problem(d)


def test_rejects_invalid_context_source_selection_policy():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / "context.yaml").write_text(
            yaml.dump({"source_selection_policy": "semantic"})
        )

        with pytest.raises(ValueError, match="source_selection_policy must be one of"):
            load_problem(d)


def test_context_policy_limits_context_entry_count_with_diagnostic():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "a.md").write_text("a", encoding="utf-8")
        (context / "b.md").write_text("b", encoding="utf-8")
        (context / "c.md").write_text("c", encoding="utf-8")
        (context / "context.yaml").write_text(yaml.dump({"max_context_entries": 2}))

        p = load_problem(d)

        assert sorted(p.context_files) == ["a.md", "b.md"]
        assert p.context_policy["max_context_entries"] == 2
        assert p.context_policy["selected_count"] == 2
        assert p.context_policy["skipped_count"] == 1
        assert p.context_policy["skipped_record_count"] == 1
        skipped = p.context_policy["skipped"][0]
        assert skipped["path"] == "c.md"
        assert skipped["reason"] == "max_context_entries"
        assert skipped["max_entries"] == 2
        assert skipped["entries_before"] == 2
        assert skipped["sha256"] is None


def test_context_policy_limits_context_depth_with_diagnostic():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        nested = context / "nested"
        nested.mkdir(parents=True)
        (nested / "deep.md").write_text("deep", encoding="utf-8")
        (context / "context.yaml").write_text(yaml.dump({"max_context_depth": 1}))

        p = load_problem(d)

        assert p.context_files == {}
        assert p.context_policy["max_context_depth"] == 1
        assert p.context_policy["skipped_count"] == 1
        skipped = p.context_policy["skipped"][0]
        assert skipped["path"] == "nested/deep.md"
        assert skipped["reason"] == "max_context_depth"
        assert skipped["depth"] == 2
        assert skipped["max_depth"] == 1
        assert skipped["sha256"] is None


def test_context_policy_records_nested_directory_listing_errors(monkeypatch):
    token = "sk-proj_contextlistsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        blocked = context / "blocked"
        blocked.mkdir(parents=True)
        (context / "keep.md").write_text("keep", encoding="utf-8")
        (blocked / "secret.md").write_text("secret", encoding="utf-8")
        original_iterdir = Path.iterdir

        def fake_iterdir(path):
            if path == blocked:
                raise PermissionError(f"cannot list api_key={token}")
            return original_iterdir(path)

        monkeypatch.setattr(Path, "iterdir", fake_iterdir)

        p = load_problem(d)

        assert p.context_files == {"keep.md": "keep"}
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        diagnostic = skipped["blocked"]
        assert diagnostic["reason"] == "directory_listing_error"
        assert diagnostic["source_type"] == "directory"
        assert diagnostic["sha256"] is None
        assert diagnostic["error_type"] == "PermissionError"
        assert token not in diagnostic["error"]
        assert "[REDACTED]" in diagnostic["error"]


def test_context_policy_records_root_directory_listing_errors(monkeypatch):
    token = "sk-proj_contextrootlistsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        original_iterdir = Path.iterdir

        def fake_iterdir(path):
            if path == context:
                raise PermissionError(f"cannot list api_key={token}")
            return original_iterdir(path)

        monkeypatch.setattr(Path, "iterdir", fake_iterdir)

        p = load_problem(d)

        assert p.context_files == {}
        assert p.context_sources == []
        assert p.context_policy["selected_count"] == 0
        assert p.context_policy["skipped_count"] == 1
        diagnostic = p.context_policy["skipped"][0]
        assert diagnostic["path"] == "."
        assert diagnostic["reason"] == "directory_listing_error"
        assert diagnostic["source_type"] == "directory"
        assert diagnostic["sha256"] is None
        assert diagnostic["error_type"] == "PermissionError"
        assert token not in diagnostic["error"]
        assert "[REDACTED]" in diagnostic["error"]


def test_context_policy_caps_retained_skipped_diagnostics():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        for index in range(5):
            (context / f"data-{index}.bin").write_bytes(b"x")
        (context / "context.yaml").write_text(yaml.dump({"max_skipped_diagnostics": 2}))

        p = load_problem(d)

        assert p.context_policy["skipped_count"] == 5
        assert p.context_policy["skipped_record_count"] == 2
        assert len(p.context_policy["skipped"]) == 2
        assert p.context_policy["skipped_records_truncated"] is True
        assert p.context_policy["skipped_records_omitted"] == 3
        assert p.context_policy["skipped_omitted_reasons"] == {"unsupported_extension": 3}


def test_context_policy_caps_skipped_provenance_size():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        for index in range(4):
            (context / f"very-long-unsupported-name-{index:02d}.bin").write_bytes(b"x")
        (context / "context.yaml").write_text(yaml.dump({
            "max_skipped_diagnostics": 4,
            "max_context_provenance_chars": 1,
        }))

        p = load_problem(d)

        assert p.context_policy["skipped_count"] == 4
        assert p.context_policy["skipped_record_count"] == 0
        assert p.context_policy["skipped"] == []
        assert p.context_policy["skipped_records_truncated"] is True
        assert p.context_policy["skipped_records_omitted"] == 4
        assert p.context_policy["context_provenance_truncated"] is True
        assert p.context_policy["context_provenance_over_limit"] is True


def test_context_policy_skips_sources_above_byte_limit_before_reading():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "large.md").write_text("abcdef", encoding="utf-8")
        (context / "context.yaml").write_text(yaml.dump({
            "max_bytes_per_source": 3,
        }))

        p = load_problem(d)

        assert p.context_files == {}
        assert p.context_sources == []
        assert p.context_policy["max_bytes_per_source"] == 3
        skipped = p.context_policy["skipped"][0]
        assert skipped["path"] == "large.md"
        assert skipped["reason"] == "max_source_bytes"
        assert skipped["bytes"] == 6
        assert skipped["max_bytes"] == 3
        assert skipped["sha256"] is None


def test_context_policy_skips_sources_above_total_byte_limit():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "a.md").write_text("abc", encoding="utf-8")
        (context / "b.md").write_text("def", encoding="utf-8")
        (context / "context.yaml").write_text(yaml.dump({
            "max_total_bytes": 3,
        }))

        p = load_problem(d)

        assert p.context_files == {"a.md": "abc"}
        assert [source["path"] for source in p.context_sources] == ["a.md"]
        assert p.context_policy["max_total_bytes"] == 3
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped["b.md"]["reason"] == "max_total_bytes"
        assert skipped["b.md"]["bytes"] == 3
        assert skipped["b.md"]["max_bytes"] == 3
        assert skipped["b.md"]["total_bytes_before"] == 3


def test_context_policy_records_selected_source_stat_errors(monkeypatch):
    token = "sk-proj_contextstatsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        keep = context / "keep.md"
        broken = context / "broken.md"
        keep.write_text("keep", encoding="utf-8")
        broken.write_text("broken", encoding="utf-8")
        original_stat = Path.stat
        stat_calls = {}

        def fake_stat(path, *args, **kwargs):
            if path == broken:
                stat_calls[path] = stat_calls.get(path, 0) + 1
                if stat_calls[path] > 1:
                    raise PermissionError(f"cannot stat api_key={token}")
            return original_stat(path, *args, **kwargs)

        monkeypatch.setattr(Path, "stat", fake_stat)

        p = load_problem(d)

        assert p.context_files == {"keep.md": "keep"}
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        diagnostic = skipped["broken.md"]
        assert diagnostic["reason"] == "stat_error"
        assert diagnostic["source_type"] == "md"
        assert diagnostic["sha256"] is None
        assert diagnostic["bytes"] is None
        assert diagnostic["error_type"] == "PermissionError"
        assert token not in diagnostic["error"]
        assert "[REDACTED]" in diagnostic["error"]


@pytest.mark.parametrize(
    ("name", "manifest", "expected_reason"),
    [
        ("data.bin", None, "unsupported_extension"),
        ("skip.md", {"exclude": ["skip.md"]}, "excluded"),
        (".hidden.md", None, "hidden_not_included"),
        ("skip.md", {"include": ["keep.md"]}, "not_included"),
    ],
)
def test_context_policy_records_preclassification_source_stat_errors(
    monkeypatch,
    name,
    manifest,
    expected_reason,
):
    token = "sk-proj_contextstatignoredsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        keep = context / "keep.md"
        skipped_path = context / name
        keep.write_text("keep", encoding="utf-8")
        skipped_path.write_text("skip", encoding="utf-8")
        if manifest is not None:
            (context / "context.yaml").write_text(yaml.dump(manifest), encoding="utf-8")
        original_stat = Path.stat
        stat_calls = {}

        def fake_stat(path, *args, **kwargs):
            if path == skipped_path:
                stat_calls[path] = stat_calls.get(path, 0) + 1
                if stat_calls[path] > 1:
                    raise PermissionError(f"cannot stat api_key={token}")
            return original_stat(path, *args, **kwargs)

        monkeypatch.setattr(Path, "stat", fake_stat)

        p = load_problem(d)

        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        diagnostic = skipped[name]
        assert expected_reason in {
            "unsupported_extension",
            "excluded",
            "hidden_not_included",
            "not_included",
        }
        assert diagnostic["reason"] == "stat_error"
        assert diagnostic["sha256"] is None
        assert diagnostic["bytes"] is None
        assert diagnostic["error_type"] == "PermissionError"
        assert token not in diagnostic["error"]
        assert "[REDACTED]" in diagnostic["error"]


def test_context_policy_skips_hidden_context_by_default():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / ".secret.md").write_text("hidden")

        p = load_problem(d)

        assert sorted(p.context_files) == ["notes.md"]
        assert p.context_policy["hidden_source_policy"] == "skip_unless_explicitly_included"
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped[".secret.md"]["reason"] == "hidden_not_included"
        assert skipped[".secret.md"]["hidden"] is True
        assert len(skipped[".secret.md"]["sha256"]) == 64


def test_context_policy_allows_explicitly_included_hidden_context():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("skip")
        (context / ".notes.md").write_text("intentional hidden context")
        (context / "context.yaml").write_text(yaml.dump({
            "include": [".notes.md"],
        }))

        p = load_problem(d)

        assert p.context_files == {".notes.md": "intentional hidden context"}
        assert p.context_sources[0]["path"] == ".notes.md"
        assert p.context_sources[0]["hidden"] is True
        assert p.context_policy["include_patterns"] == [
            {"pattern": ".notes.md", "matches": 1, "selected_matches": 1},
        ]
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped["notes.md"]["reason"] == "not_included"
        assert skipped["notes.md"]["hidden"] is False


def test_context_policy_broad_include_does_not_opt_into_hidden_context():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / ".secret.md").write_text("hidden")
        (context / "context.yaml").write_text(yaml.dump({
            "include": ["*.md"],
        }))

        p = load_problem(d)

        assert sorted(p.context_files) == ["notes.md"]
        assert p.context_policy["include_patterns"] == [
            {"pattern": "*.md", "matches": 2, "selected_matches": 1},
        ]
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped[".secret.md"]["reason"] == "hidden_not_included"


def test_context_manifest_globs_are_path_segment_aware():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        (context / "nested").mkdir(parents=True)
        (context / "top.md").write_text("top")
        (context / "nested" / "deep.md").write_text("deep")
        (context / "context.yaml").write_text(yaml.dump({
            "include": ["*.md"],
        }))

        p = load_problem(d)

        assert p.context_files == {"top.md": "top"}
        assert p.context_policy["include_patterns"] == [
            {"pattern": "*.md", "matches": 1, "selected_matches": 1},
        ]
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped["nested/deep.md"]["reason"] == "not_included"


def test_context_manifest_globstar_matches_recursive_context():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        (context / "nested").mkdir(parents=True)
        (context / "top.md").write_text("top")
        (context / "nested" / "deep.md").write_text("deep")
        (context / "context.yaml").write_text(yaml.dump({
            "include": ["**/*.md"],
            "exclude": ["nested/*.md"],
        }))

        p = load_problem(d)

        assert p.context_files == {"top.md": "top"}
        assert p.context_policy["include_patterns"] == [
            {"pattern": "**/*.md", "matches": 2, "selected_matches": 1},
        ]
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped["nested/deep.md"]["reason"] == "excluded"


def test_context_policy_records_unmatched_include_patterns():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / "context.yaml").write_text(yaml.dump({
            "include": ["notes.md", "missing.md"],
        }))

        p = load_problem(d)

        assert sorted(p.context_files) == ["notes.md"]
        assert p.context_policy["include_patterns"] == [
            {"pattern": "notes.md", "matches": 1, "selected_matches": 1},
            {"pattern": "missing.md", "matches": 0, "selected_matches": 0},
        ]
        assert p.context_policy["unmatched_includes"] == ["missing.md"]


def test_context_policy_records_unmatched_include_with_empty_context():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "context.yaml").write_text(yaml.dump({"include": ["missing.md"]}))

        p = load_problem(d)

        assert p.context_files == {}
        assert p.context_policy["selected_count"] == 0
        assert p.context_policy["skipped_count"] == 0
        assert p.context_policy["include_patterns"] == [
            {"pattern": "missing.md", "matches": 0, "selected_matches": 0},
        ]
        assert p.context_policy["unmatched_includes"] == ["missing.md"]


@pytest.mark.parametrize("field", ["include", "exclude"])
@pytest.mark.parametrize(
    "pattern",
    [
        "../secret/*.md",
        "/absolute/*.md",
        "C:/absolute/*.md",
        r"nested\*.md",
        "api_key=sk-proj_secret_1234567890\n*.md",
        "notes\u202e.md",
        "notes\u200d.md",
        "",
    ],
)
def test_rejects_unsafe_context_manifest_patterns(field, pattern):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / "context.yaml").write_text(yaml.dump({field: [pattern]}))

        with pytest.raises(
            ValueError,
            match=rf"context {field} pattern must be a safe problem-relative glob",
        ):
            load_problem(d)


@pytest.mark.parametrize("field", ["include", "exclude"])
def test_rejects_secret_like_context_manifest_patterns(field):
    token = "sk-" + "proj_contextpatternsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("keep")
        (context / "context.yaml").write_text(
            yaml.dump({field: [f"api_key={token}.md"]})
        )

        with pytest.raises(
            ValueError,
            match=rf"context {field} pattern must be a safe problem-relative glob",
        ):
            load_problem(d)


def test_context_manifest_patterns_allow_ordinary_unicode_names():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "cafe\u00e9.md").write_text("keep")
        (context / "notes.md").write_text("skip")
        (context / "context.yaml").write_text(yaml.dump({
            "include": ["cafe\u00e9.md"],
            "exclude": ["notes.md"],
        }))

        p = load_problem(d)

        assert sorted(p.context_files) == ["cafe\u00e9.md"]
        assert p.context_policy["include"] == ["cafe\u00e9.md"]
        assert p.context_policy["exclude"] == ["notes.md"]


def test_context_manifest_patterns_match_unicode_normalized_source_paths():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        decomposed_name = "cafe\u0301.md"
        canonical_name = "caf\u00e9.md"
        path = context / decomposed_name
        path.write_text("keep", encoding="utf-8")
        if path.name != decomposed_name:
            pytest.skip("filesystem normalizes Unicode filenames")
        (context / "notes.md").write_text("skip", encoding="utf-8")
        (context / "context.yaml").write_text(
            yaml.dump({"include": [canonical_name], "exclude": ["notes.md"]}),
            encoding="utf-8",
        )

        p = load_problem(d)

        assert p.context_files == {canonical_name: "keep"}
        assert p.context_sources[0]["path"] == canonical_name
        assert p.context_sources[0]["filesystem_path"] == decomposed_name
        assert p.context_policy["include_patterns"] == [
            {"pattern": canonical_name, "matches": 1, "selected_matches": 1}
        ]


def test_context_manifest_excludes_unicode_normalized_source_paths():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        decomposed_name = "cafe\u0301.md"
        canonical_name = "caf\u00e9.md"
        path = context / decomposed_name
        path.write_text("skip", encoding="utf-8")
        if path.name != decomposed_name:
            pytest.skip("filesystem normalizes Unicode filenames")
        (context / "keep.md").write_text("keep", encoding="utf-8")
        (context / "context.yaml").write_text(
            yaml.dump({"exclude": [canonical_name]}),
            encoding="utf-8",
        )

        p = load_problem(d)

        assert p.context_files == {"keep.md": "keep"}
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert decomposed_name in skipped
        assert skipped[decomposed_name]["reason"] == "excluded"
        assert skipped[decomposed_name]["display_path"] == canonical_name


def test_rejects_unicode_equivalent_context_source_paths():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "caf\u00e9.md").write_text("one", encoding="utf-8")
        (context / "cafe\u0301.md").write_text("two", encoding="utf-8")
        if len([path for path in context.iterdir() if path.is_file()]) < 2:
            pytest.skip("filesystem normalizes Unicode filenames")

        with pytest.raises(
            ValueError,
            match="duplicate context source path after Unicode normalization",
        ):
            load_problem(d)


def test_rejects_secret_like_context_source_path():
    token = "sk-" + "proj_contextpathsecret1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / f"api_key={token}.md").write_text("keep")

        with pytest.raises(
            ValueError,
            match="context source path must not contain secret-like text",
        ):
            load_problem(d)


@pytest.mark.parametrize(
    ("reason", "filename", "manifest", "contents"),
    [
        ("unsupported_extension", "api_key=sk-proj_contextskippedunsupported1234567890.bin", None, "x"),
        ("excluded", "api_key=sk-proj_contextskippedexcluded1234567890.md", {"exclude": ["*.md"]}, "x"),
        ("hidden_not_included", ".api_key=sk-proj_contextskippedhidden1234567890.md", None, "x"),
        ("not_included", "api_key=sk-proj_contextskippednotincluded1234567890.md", {"include": ["keep.md"]}, "x"),
        (
            "max_source_bytes",
            "api_key=sk-proj_contextskippedsourcebytes1234567890.md",
            {"max_bytes_per_source": 1},
            "xx",
        ),
        (
            "max_total_bytes",
            "api_key=sk-proj_contextskippedtotalbytes1234567890.md",
            {"max_total_bytes": 1},
            "x",
        ),
    ],
)
def test_rejects_secret_like_skipped_context_source_paths(reason, filename, manifest, contents):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        if reason == "max_total_bytes":
            (context / "a.md").write_text("x", encoding="utf-8")
        (context / filename).write_text(contents, encoding="utf-8")
        if manifest is not None:
            (context / "context.yaml").write_text(yaml.dump(manifest), encoding="utf-8")

        with pytest.raises(
            ValueError,
            match="skipped context source path must not contain secret-like text",
        ) as excinfo:
            load_problem(d)

        assert "sk-proj_" not in str(excinfo.value)


def test_rejects_unknown_context_manifest_fields():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "keep.md").write_text("keep")
        (context / "context.yaml").write_text(yaml.dump({
            "includes": ["missing/*.md"],
        }))

        with pytest.raises(ValueError, match="unsupported context manifest fields"):
            load_problem(d)


def test_rejects_invalid_explicit_context_failure_policy():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "keep.md").write_text("keep")
        (context / "context.yaml").write_text(
            yaml.dump({"on_explicit_context_failure": "ignore"}),
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match="on_explicit_context_failure must be one of",
        ):
            load_problem(d)


def test_rejects_invalid_context_excerpt_policy():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "keep.md").write_text("keep")
        (context / "context.yaml").write_text(
            yaml.dump({"excerpt_policy": "middle"}),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="excerpt_policy must be one of"):
            load_problem(d)


def test_rejects_non_string_context_manifest_keys():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "keep.md").write_text("keep")
        (context / "context.yaml").write_text(
            "1: bad\n"
            "unknown: bad\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="context manifest keys must be strings"):
            load_problem(d)


def test_rejects_malformed_context_manifest_yaml_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        manifest = context / "context.yaml"
        manifest.write_text("include: [*")

        with pytest.raises(
            ValueError,
            match=r"context\.yaml: invalid context manifest YAML",
        ):
            load_problem(d)


def test_rejects_invalid_utf8_context_manifest_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        manifest = context / "context.yaml"
        manifest.write_bytes(b"\xff\xfe\xfa")

        with pytest.raises(ValueError, match=r"context\.yaml: context manifest must be valid UTF-8"):
            load_problem(d)


def test_rejects_unreadable_context_manifest_with_redacted_path_diagnostic(monkeypatch):
    token = "sk-" + "proj_contextmanifestsecret1234567890"  # pragma: allowlist secret
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        manifest = context / "context.yaml"
        manifest.write_text("include: []\n", encoding="utf-8")
        original_read_bytes = Path.read_bytes

        def fake_read_bytes(path):
            if path == manifest:
                raise PermissionError(f"cannot read api_key={token}")
            return original_read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)

        with pytest.raises(
            ValueError,
            match=r"context\.yaml: context manifest could not be read",
        ) as exc_info:
            load_problem(d)

        message = str(exc_info.value)
        assert token not in message
        assert "[REDACTED]" in message


def test_rejects_context_manifest_directory_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "context.yaml").mkdir()

        with pytest.raises(ValueError, match=r"context\.yaml.*regular file"):
            load_problem(d)


def test_rejects_duplicate_context_manifest_keys_with_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "a.md").write_text("a", encoding="utf-8")
        (context / "b.md").write_text("b", encoding="utf-8")
        (context / "context.yaml").write_text(
            "include: ['a.md']\ninclude: ['b.md']\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError) as excinfo:
            load_problem(d)
        message = str(excinfo.value)
        assert "context.yaml: invalid context manifest YAML" in message
        assert "duplicate key" in message


def test_redacts_secret_like_duplicate_context_manifest_key():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        secret_key = "api_key=sk-proj_yamldiagsecret1234567890"
        (context / "context.yaml").write_text(
            f"{secret_key}: 1\n{secret_key}: 2\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError) as excinfo:
            load_problem(d)
        message = str(excinfo.value)
        assert "context.yaml: invalid context manifest YAML" in message
        assert "duplicate key" in message
        assert secret_key not in message
        assert "api_key=[REDACTED]" in message


@pytest.mark.parametrize(
    ("yaml_text", "message"),
    [
        ("include: &includes ['a.md']\n", "YAML anchors are not supported"),
        (
            "common: &common ['a.md']\ninclude: *common\n",
            "YAML anchors are not supported",
        ),
    ],
)
def test_rejects_context_manifest_anchors_and_aliases(yaml_text, message):
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "a.md").write_text("a", encoding="utf-8")
        (context / "context.yaml").write_text(yaml_text, encoding="utf-8")

        with pytest.raises(ValueError) as excinfo:
            load_problem(d)
        error = str(excinfo.value)
        assert "context.yaml: invalid context manifest YAML" in error
        assert message in error


def test_rejects_conflicting_context_manifest_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "a.md").write_text("a")
        (context / "context.yaml").write_text(yaml.dump({"include": ["a.md"]}))
        (context / "context.yml").write_text(yaml.dump({"include": ["missing.md"]}))

        with pytest.raises(ValueError, match="use only one context manifest"):
            load_problem(d)


def test_recursive_context_preserves_duplicate_basenames_by_relative_path():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context" / "a").mkdir(parents=True)
        (d / "context" / "b").mkdir(parents=True)
        (d / "context" / "a" / "notes.md").write_text("a")
        (d / "context" / "b" / "notes.md").write_text("b")

        p = load_problem(d)

        assert p.context_files["a/notes.md"] == "a"
        assert p.context_files["b/notes.md"] == "b"
        assert [s["path"] for s in p.context_sources] == ["a/notes.md", "b/notes.md"]


def test_context_source_hash_changes_when_file_changes():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        source = d / "context" / "notes.md"
        source.write_text("first")
        first = load_problem(d).context_sources[0]["sha256"]

        source.write_text("second")
        second = load_problem(d).context_sources[0]["sha256"]

        assert first != second


@pytest.mark.parametrize(
    ("name", "source_type"),
    [
        ("notes.txt", "txt"),
        ("notes.md", "md"),
        ("script.py", "py"),
        ("paper.pdf", "pdf"),
    ],
)
def test_context_policy_records_selected_source_read_errors(
    monkeypatch,
    name,
    source_type,
):
    token = f"sk-proj_contextsourcesecret{name.replace('.', '')}1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        keep = context / "keep.md"
        unreadable = context / name
        keep.write_text("keep", encoding="utf-8")
        unreadable.write_text("secret", encoding="utf-8")
        original_read_bytes = Path.read_bytes

        def fake_read_bytes(path):
            if path == unreadable:
                raise PermissionError(f"cannot read api_key={token}")
            return original_read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)

        p = load_problem(d)

        assert p.context_files == {"keep.md": "keep"}
        assert [source["path"] for source in p.context_sources] == ["keep.md"]
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        diagnostic = skipped[name]
        assert diagnostic["reason"] == "read_error"
        assert diagnostic["source_type"] == source_type
        assert diagnostic["sha256"] is None
        assert diagnostic["bytes"] is None
        assert diagnostic["extraction_status"] == "read_error"
        assert diagnostic["error_type"] == "PermissionError"
        assert token not in diagnostic["error"]
        assert "[REDACTED]" in diagnostic["error"]


@pytest.mark.parametrize(
    ("name", "manifest", "expected_reason"),
    [
        ("data.bin", None, "unsupported_extension"),
        ("skip.md", {"exclude": ["skip.md"]}, "excluded"),
        (".hidden.md", None, "hidden_not_included"),
        ("skip.md", {"include": ["keep.md"]}, "not_included"),
    ],
)
def test_context_policy_records_skipped_source_read_errors(
    monkeypatch,
    name,
    manifest,
    expected_reason,
):
    token = f"sk-proj_skippedcontextsecret{name.replace('.', '')}1234567890"
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        keep = context / "keep.md"
        unreadable = context / name
        keep.write_text("keep", encoding="utf-8")
        unreadable.write_text("secret", encoding="utf-8")
        if manifest is not None:
            (context / "context.yaml").write_text(yaml.dump(manifest), encoding="utf-8")
        original_read_bytes = Path.read_bytes

        def fake_read_bytes(path):
            if path == unreadable:
                raise PermissionError(f"cannot read api_key={token}")
            return original_read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)

        p = load_problem(d)

        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        diagnostic = skipped[name]
        assert diagnostic["reason"] == expected_reason
        assert diagnostic["sha256"] is None
        assert diagnostic["bytes"] is None
        assert diagnostic["read_status"] == "read_error"
        assert diagnostic["error_type"] == "PermissionError"
        assert token not in diagnostic["error"]
        assert "[REDACTED]" in diagnostic["error"]


def test_preserves_text_context_whitespace():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        text = "  leading\n\n```python\nx = 1\n```\n\n"
        (d / "context" / "notes.txt").write_text(text, encoding="utf-8")

        p = load_problem(d)

        assert p.context_files["notes.txt"] == text
        source = p.context_sources[0]
        assert source["chars_original"] == len(text)
        assert source["chars_rendered"] == len(text)
        assert source["truncated"] is False


def test_reads_pdf_context_files():
    from pypdf import PdfWriter

    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(d / "context" / "paper.pdf", "wb") as f:
            writer.write(f)
        p = load_problem(d)
        assert p.context_files == {}
        assert p.context_sources == []
        assert p.context_policy["selected_count"] == 0
        assert p.context_policy["usable_selected_count"] == 0
        assert p.context_policy["failed_extraction_count"] == 1
        skipped = p.context_policy["skipped"][0]
        assert skipped["path"] == "paper.pdf"
        assert skipped["reason"] == "no_extractable_text"
        assert skipped["extraction_status"] == "no_extractable_text"
        assert skipped["pages"] == [1, 1]


def test_pdf_context_records_rendered_excerpt_page_span(monkeypatch):
    import pypdf

    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        pages = [
            FakePage("abcdef"),
            FakePage(""),
            FakePage("mnop"),
            FakePage(""),
            FakePage("qrst"),
        ]

    monkeypatch.setattr(pypdf, "PdfReader", lambda _: FakeReader())

    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "paper.pdf").write_bytes(b"%PDF fake")
        (context / "context.yaml").write_text(yaml.dump({"max_chars_per_source": 8}))

        p = load_problem(d)

        source = p.context_sources[0]
        assert source["pages"] == [1, 5]
        assert source["extracted_pages"] == [1, 3, 5]
        assert source["extracted_page_range"] == [1, 5]
        assert source["page_char_spans"] == [
            {"page": 1, "start": 0, "end": 6},
            {"page": 3, "start": 7, "end": 11},
            {"page": 5, "start": 12, "end": 16},
        ]
        assert source["excerpt_start"] == 0
        assert source["excerpt_end"] == 8
        assert source["excerpt_pages"] == [1, 3]
        assert source["excerpt_page_spans"] == [
            {
                "page": 1,
                "excerpt_start": 0,
                "excerpt_end": 6,
                "page_excerpt_start": 0,
                "page_excerpt_end": 6,
            },
            {
                "page": 3,
                "excerpt_start": 7,
                "excerpt_end": 8,
                "page_excerpt_start": 0,
                "page_excerpt_end": 1,
            },
        ]


def test_pdf_context_respects_page_extraction_limit(monkeypatch):
    import pypdf

    class FakePage:
        def extract_text(self):
            return "page"

    class FakeReader:
        pages = [FakePage(), FakePage(), FakePage()]

    monkeypatch.setattr(pypdf, "PdfReader", lambda _: FakeReader())

    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "paper.pdf").write_bytes(b"%PDF fake")
        (context / "context.yaml").write_text(yaml.dump({"max_pdf_pages": 2}))

        p = load_problem(d)

        assert p.context_files == {}
        assert p.context_sources == []
        assert p.context_policy["failed_extraction_count"] == 1
        skipped = p.context_policy["skipped"][0]
        assert skipped["path"] == "paper.pdf"
        assert skipped["reason"] == "extraction_resource_limit"
        assert skipped["max_pdf_pages"] == 2
        assert skipped["pages"] == [1, 3]


def test_pdf_context_respects_extracted_character_limit(monkeypatch):
    import pypdf

    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        pages = [FakePage("abc"), FakePage("def")]

    monkeypatch.setattr(pypdf, "PdfReader", lambda _: FakeReader())

    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "paper.pdf").write_bytes(b"%PDF fake")
        (context / "context.yaml").write_text(yaml.dump({"max_pdf_chars": 4}))

        p = load_problem(d)

        assert p.context_files == {}
        assert p.context_sources == []
        skipped = p.context_policy["skipped"][0]
        assert skipped["reason"] == "extraction_resource_limit"
        assert skipped["max_pdf_chars"] == 4
        assert skipped["extracted_chars"] == 6


def test_records_pdf_context_extraction_failures():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        (d / "context" / "broken.pdf").write_bytes(b"not a pdf")

        p = load_problem(d)

        assert p.context_files == {}
        assert p.context_sources == []
        assert p.context_policy["selected_count"] == 0
        assert p.context_policy["failed_extraction_count"] == 1
        skipped = p.context_policy["skipped"][0]
        assert skipped["path"] == "broken.pdf"
        assert skipped["reason"] == "extraction_failed"
        assert skipped["extraction_status"] == "failed"
        assert "PDF extraction failed" not in str(p.context_files)
        assert "PdfStreamError" in skipped["error"]


def test_records_invalid_text_context_as_extraction_diagnostic():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "bad.md").write_bytes(b"\xff\xfe\xfd")
        (context / "notes.md").write_text("usable", encoding="utf-8")

        p = load_problem(d)

        assert p.context_files == {"notes.md": "usable"}
        assert [source["path"] for source in p.context_sources] == ["notes.md"]
        assert p.context_policy["selected_count"] == 1
        assert p.context_policy["usable_selected_count"] == 1
        assert p.context_policy["failed_extraction_count"] == 1
        skipped = {item["path"]: item for item in p.context_policy["skipped"]}
        assert skipped["bad.md"]["reason"] == "extraction_failed"
        assert skipped["bad.md"]["extraction_status"] == "failed"
        assert "UnicodeDecodeError" in skipped["bad.md"]["error"]
        assert "text extraction failed" not in str(p.context_files)


def test_explicit_invalid_text_context_fails_by_default():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "must_use.md").write_bytes(b"\xff\xfe\xfd")
        (context / "context.yaml").write_text(
            yaml.dump({"include": ["must_use.md"]}),
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match=r"explicit context extraction failed.*must_use\.md",
        ):
            load_problem(d)


def test_explicit_mixed_context_failure_fails_before_partial_load():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "good.md").write_text("usable", encoding="utf-8")
        (context / "bad.md").write_bytes(b"\xff")
        (context / "context.yaml").write_text(
            yaml.dump({"include": ["*.md"]}),
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match=r"explicit context extraction failed.*bad\.md",
        ):
            load_problem(d)


def test_explicit_context_failure_warn_allows_degraded_context_with_diagnostics():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "bad.md").write_bytes(b"\xff")
        (context / "context.yaml").write_text(
            yaml.dump(
                {
                    "include": ["bad.md"],
                    "on_explicit_context_failure": "warn",
                }
            ),
            encoding="utf-8",
        )

        p = load_problem(d)

        assert p.context_files == {}
        assert p.context_policy["on_explicit_context_failure"] == "warn"
        assert p.context_policy["explicit_context_failure_count"] == 1
        assert p.context_policy["explicit_context_failures"][0]["path"] == "bad.md"
        assert p.context_policy["explicit_context_failures"][0][
            "matched_include_patterns"
        ] == ["bad.md"]
        skipped = p.context_policy["skipped"][0]
        assert skipped["path"] == "bad.md"
        assert skipped["explicit_include"] is True
        assert skipped["matched_include_patterns"] == ["bad.md"]


def test_explicit_corrupt_pdf_context_fails_by_default():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "broken.pdf").write_bytes(b"not a pdf")
        (context / "context.yaml").write_text(
            yaml.dump({"include": ["broken.pdf"]}),
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match=r"explicit context extraction failed.*broken\.pdf",
        ):
            load_problem(d)


def test_explicit_no_text_pdf_context_fails_by_default():
    from pypdf import PdfWriter

    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(context / "paper.pdf", "wb") as handle:
            writer.write(handle)
        (context / "context.yaml").write_text(
            yaml.dump({"include": ["paper.pdf"]}),
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match=r"explicit context extraction failed.*paper\.pdf",
        ):
            load_problem(d)


def test_explicit_pdf_resource_limit_context_fails_by_default(monkeypatch):
    import pypdf

    class FakePage:
        def extract_text(self):
            return "page"

    class FakeReader:
        pages = [FakePage(), FakePage(), FakePage()]

    monkeypatch.setattr(pypdf, "PdfReader", lambda _: FakeReader())

    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "paper.pdf").write_bytes(b"%PDF fake")
        (context / "context.yaml").write_text(
            yaml.dump({"include": ["paper.pdf"], "max_pdf_pages": 2}),
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match=r"explicit context extraction failed.*paper\.pdf",
        ):
            load_problem(d)


def test_truncates_long_context_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        (d / "context" / "long.txt").write_text("x" * 7000)
        p = load_problem(d)
        assert "showing first 6000 of 7000 characters" in p.context_files["long.txt"]
        assert len(p.context_files["long.txt"]) < 6100
        assert p.context_sources[0]["truncated"] is True


def test_context_manifest_head_tail_excerpt_policy_keeps_later_context():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("abcdefghij")
        (context / "context.yaml").write_text(
            yaml.dump({
                "include": ["notes.md"],
                "max_chars_per_source": 6,
                "excerpt_policy": "head_tail",
            }),
            encoding="utf-8",
        )

        p = load_problem(d)

        rendered = p.context_files["notes.md"]
        assert "showing first 3 and last 3 of 10 characters" in rendered
        assert "abc" in rendered
        assert "hij" in rendered
        assert "defg" not in rendered
        source = p.context_sources[0]
        assert source["excerpt_policy"] == "head_tail"
        assert source["excerpt_start"] == 0
        assert source["excerpt_end"] == 10
        assert source["excerpt_spans"] == [
            {"start": 0, "end": 3},
            {"start": 7, "end": 10},
        ]
        assert source["omitted_chars"] == 4
        assert p.context_policy["excerpt_policy"] == "head_tail"


def test_context_manifest_term_ranked_excerpt_policy_selects_relevant_later_chunk():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "task_description.txt").write_text(
            "Improve handling of target scoring.",
            encoding="utf-8",
        )
        context = d / "context"
        context.mkdir()
        (context / "notes.md").write_text("aaaa bbbb target ok")
        (context / "context.yaml").write_text(
            yaml.dump({
                "include": ["notes.md"],
                "max_chars_per_source": 10,
                "excerpt_policy": "term_ranked",
            }),
            encoding="utf-8",
        )

        p = load_problem(d)

        rendered = p.context_files["notes.md"]
        assert "term-ranked chunk 1 (10:19)" in rendered
        assert "target ok" in rendered
        assert "aaaa bbbb" not in rendered
        source = p.context_sources[0]
        assert source["excerpt_policy"] == "term_ranked"
        assert source["excerpt_ranking_policy"] == "term_overlap_fixed_window_v1"
        assert source["excerpt_query_term_count"] > 0
        assert len(source["excerpt_query_terms_sha256"]) == 64
        assert source["excerpt_start"] == 10
        assert source["excerpt_end"] == 19
        assert source["excerpt_spans"] == [{"start": 10, "end": 19}]
        assert source["excerpt_selected_chunks"] == [
            {"index": 1, "start": 10, "end": 19, "score": 1}
        ]
        assert source["excerpt_omitted_chunk_count"] == 1
        assert p.context_policy["excerpt_policy"] == "term_ranked"


def test_context_manifest_term_ranked_source_selection_omits_irrelevant_sources():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "task_description.txt").write_text(
            "Improve target scoring for latency fairness.",
            encoding="utf-8",
        )
        context = d / "context"
        context.mkdir()
        (context / "a_prefix.md").write_text("alpha beta gamma delta")
        (context / "b_relevant.md").write_text(
            "aaaa bbbb cccc target scoring latency fairness"
        )
        (context / "c_unrelated.md").write_text("queue memory cache vector")
        (context / "context.yaml").write_text(
            yaml.dump({
                "include": ["*.md"],
                "max_chars_per_source": 24,
                "excerpt_policy": "term_ranked",
                "source_selection_policy": "term_ranked",
                "max_selected_context_sources": 1,
            }),
            encoding="utf-8",
        )

        p = load_problem(d)

        assert list(p.context_files) == ["b_relevant.md"]
        assert "latency fairness" in p.context_files["b_relevant.md"]
        assert "a_prefix.md" not in p.context_files
        assert "c_unrelated.md" not in p.context_files
        source = p.context_sources[0]
        assert source["path"] == "b_relevant.md"
        assert source["source_selection_policy"] == "term_ranked"
        assert source["source_selection_rank"] == 1
        assert source["source_selection_score"] >= 2
        assert len(source["source_selection_query_terms_sha256"]) == 64
        selection = p.context_policy["source_selection"]
        assert selection["schema"] == "libreevolve.context_source_selection_policy.v1"
        assert selection["policy"] == "term_ranked"
        assert selection["ranking_policy"] == "term_overlap_selected_excerpt_v1"
        assert selection["candidate_count"] == 3
        assert selection["selected_count"] == 1
        assert selection["omitted_count"] == 2
        assert selection["selected_sources"] == [
            {
                "path": "b_relevant.md",
                "sha256": source["sha256"],
                "chars_rendered": source["chars_rendered"],
                "excerpt_policy": "term_ranked",
                "score": source["source_selection_score"],
                "rank": 1,
            }
        ]
        omitted = {item["path"]: item for item in selection["omitted_sources"]}
        assert omitted["a_prefix.md"]["reason"] == "max_selected_context_sources"
        assert omitted["c_unrelated.md"]["reason"] == "max_selected_context_sources"
        assert p.context_policy["max_selected_context_sources"] == 1
        assert p.context_policy["source_selection_policy"] == "term_ranked"


def test_rejects_context_file_symlink_escape(tmp_path):
    d = _make(tmp_path)
    context = d / "context"
    context.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("secret context\n", encoding="utf-8")
    link = context / "outside.md"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"file symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError, match="Context links are not supported"):
        load_problem(d)


def test_rejects_context_manifest_symlink(tmp_path):
    d = _make(tmp_path)
    context = d / "context"
    context.mkdir()
    outside = tmp_path / "context.yaml"
    outside.write_text("include: ['*.md']\n", encoding="utf-8")
    link = context / "context.yaml"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"file symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError, match="Context links are not supported"):
        load_problem(d)


def test_rejects_windows_junction_in_context(tmp_path):
    if sys.platform != "win32":
        pytest.skip("Windows junction test")

    d = _make(tmp_path)
    context = d / "context"
    context.mkdir()
    outside = tmp_path / "outside_context"
    outside.mkdir()
    (outside / "secret.md").write_text("secret context\n", encoding="utf-8")
    link = context / "linked"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")

    with pytest.raises(ValueError, match="Context links are not supported"):
        load_problem(d)


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
                    "name": "review_latency_ms",
                    "direction": "minimize",
                    "bounds": [0.0, 100.0],
                    "source": "feedback",
                },
                {
                    "name": "plugin_quality",
                    "bounds": [0.0, 10.0],
                    "source": "plugin",
                },
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
        assert problem.metric("review_latency_ms")["source"] == "feedback"
        assert problem.metric("plugin_quality")["source"] == "plugin"
        assert problem.metric("final_quality")["source"] == "final_fitness"
        assert problem.objective_schema()["metrics"][1] == {
            "name": "review_latency_ms",
            "direction": "minimize",
            "bounds": [0.0, 100.0],
            "source": "feedback",
            "weight": 1.0,
            "primary": False,
        }
        assert problem.objective_schema()["metrics"][2] == {
            "name": "plugin_quality",
            "direction": "maximize",
            "bounds": [0.0, 10.0],
            "source": "plugin",
            "weight": 1.0,
            "primary": False,
        }
        assert problem.objective_schema()["metrics"][3] == {
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
            "primary metric .* source 'evaluator'",
        ),
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": "plugin"},
            "primary metric .* source 'evaluator'",
        ),
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": "final_fitness"},
            "primary metric .* source 'evaluator'",
        ),
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": "grader"},
            "source must be 'evaluator', 'feedback', 'plugin', or 'final_fitness'",
        ),
        (
            {"name": "score", "primary": True, "bounds": [0.0, 1.0], "source": 7},
            "source must be 'evaluator', 'feedback', 'plugin', or 'final_fitness'",
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
