import tempfile
from pathlib import Path
import pytest, yaml
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

def test_returns_problem():
    with tempfile.TemporaryDirectory() as t:
        assert isinstance(load_problem(_make(t)), Problem)

def test_reads_task_description():
    with tempfile.TemporaryDirectory() as t:
        assert load_problem(_make(t)).task_description == "test task"

def test_reads_primary_metric():
    with tempfile.TemporaryDirectory() as t:
        assert load_problem(_make(t)).primary_metric == "score"

def test_reads_seeds():
    with tempfile.TemporaryDirectory() as t:
        p = load_problem(_make(t))
        assert len(p.initial_programs) == 1 and "x = 1" in p.initial_programs[0]
        assert p.initial_workspaces[0].primary_file == "seed.py"

def test_raises_on_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_problem("/nonexistent/problem")

def test_raises_on_no_seeds():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        for f in (d / "initial_programs").glob("*.py"): f.unlink()
        with pytest.raises(ValueError, match="No seed programs"):
            load_problem(d)

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
        ([{"name": "score", "direction": "maximize", "bounds": [0.0]}], "bounds"),
        (
            [{"name": "score", "direction": "maximize", "bounds": [0.0, "nan"]}],
            "finite",
        ),
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
        assert source["max_chars"] == 10


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
        assert p.context_files["paper.pdf"] == "(no extractable text)"
        assert p.context_sources[0]["extraction_status"] == "no_extractable_text"
        assert p.context_sources[0]["pages"] == [1, 1]


def test_records_pdf_context_extraction_failures():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        (d / "context" / "broken.pdf").write_bytes(b"not a pdf")

        p = load_problem(d)

        assert "PDF extraction failed" in p.context_files["broken.pdf"]
        assert p.context_sources[0]["extraction_status"] == "failed"
        assert p.context_sources[0]["path"] == "broken.pdf"


def test_truncates_long_context_files():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "context").mkdir()
        (d / "context" / "long.txt").write_text("x" * 7000)
        p = load_problem(d)
        assert "showing first 6000 of 7000 characters" in p.context_files["long.txt"]
        assert len(p.context_files["long.txt"]) < 6100
        assert p.context_sources[0]["truncated"] is True


def test_normalizes_minimize_metric():
    with tempfile.TemporaryDirectory() as t:
        d = _make(t)
        (d / "metrics.yaml").write_text(yaml.dump({"metrics": [
            {"name": "loss", "direction": "minimize", "primary": True, "bounds": [0.0, 10.0]}
        ]}))
        p = load_problem(d)
        assert p.fitness_from_metrics({"loss": 2.0}) == 0.8


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
