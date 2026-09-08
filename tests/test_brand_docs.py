from __future__ import annotations

import re
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def _local_markdown_links(text: str):
    for target in MARKDOWN_LINK.findall(text):
        target = target.split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        yield target


def test_readme_is_benefit_first_and_does_not_duplicate_onboarding_commands():
    readme = _read("README.md")
    compact = " ".join(readme.split())
    assert "Evolve code. Show the evidence." in compact
    assert "open-source workbench for inspectable code-evolution experiments" in compact
    assert "Engineering preview: bounded Python bin-packing optimization" in compact
    assert compact.index("What is available today") < compact.index("Start with the canonical quickstart")
    assert compact.index("Start with the canonical quickstart") < compact.index("Read, contribute and release")
    assert "An approved inspectable example viewer is not included" in compact
    assert "pip install libreevolve" not in readme
    assert "alpha init" not in readme
    assert "--max-generations" not in readme


def test_quickstart_is_the_complete_command_source():
    quickstart = _read("docs/alpha-quickstart.md")
    required = (
        "git clone https://github.com/LibreEvolve/libreevolve.git",
        "python3.12 -m venv .venv",
        "py -3.12 -m venv .venv",
        ".venv/bin/python -m pip install -e '.[dev]'",
        '.\\.venv\\Scripts\\python.exe -m pip install -e ".[dev]"',
        "alpha init packing-task",
        "alpha doctor packing-task --offline",
        "--max-generations 0",
        "alpha report runs/seed-check --output seed-check.html",
        "alpha export runs/seed-check verified-seed",
        "codex login",
        "alpha doctor packing-task",
        "--source workspace",
        "--source history",
    )
    for phrase in required:
        assert phrase in quickstart
    assert ".venv/bin/python -m pip install ." not in quickstart
    assert "pip install libreevolve" not in quickstart
    assert "not optimization or evidence" in quickstart
    assert "provider access" in quickstart
    assert "not a security sandbox" in quickstart
    assert "subscription" in quickstart.lower()


def test_development_points_to_matching_venv_and_preserves_ci_boundaries():
    development = _read("docs/development.md")
    assert "[quickstart](alpha-quickstart.md)" in development
    assert ".venv/bin/python -m pytest tests/" in development
    assert ".venv/bin/python -m build --wheel --sdist" in development
    assert ".venv/bin/python -m libreevolve.tools.release_artifact_provenance" in development
    assert "python3.12 -m pytest" not in development
    assert "python3.12 -m build" not in development
    assert "manual-only" in development
    assert "Do not reset, clean, stash" in development


def test_report_uses_workspace_while_export_owns_source_selection():
    documents = (
        "docs/alpha-quickstart.md",
        "docs/results.md",
        "docs/run-artifacts.md",
    )
    for name in documents:
        text = _read(name)
        compact = " ".join(text.split())
        assert "on-disk" in compact
        assert "best_workspace" in compact
        assert "--source workspace" in compact
        assert "--source history" in compact
    quickstart = _read("docs/alpha-quickstart.md")
    results = _read("docs/results.md")
    artifacts = _read("docs/run-artifacts.md")
    for text in (quickstart, results, artifacts):
        compact = " ".join(text.split()).lower()
        assert (
            "no source selector" in compact
            or "no history/workspace source selector" in compact
        )
    assert "only `alpha export` supports" in " ".join(results.split())
    assert "selectors belong to export, not report" in " ".join(artifacts.split())


def test_support_and_result_boundaries_are_explicit():
    quickstart = _read("docs/alpha-quickstart.md")
    results = _read("docs/results.md")
    safety = _read("docs/safety.md")
    compact = " ".join(quickstart.split())
    assert ">=3.11" in compact
    assert "Python 3.12" in compact
    assert "Linux/WSL" in compact
    assert "Windows" in compact
    assert "native windows codex execution" in compact.lower()
    assert "external usability remain unvalidated" in compact
    for text in (results, safety):
        normalized = " ".join(text.split())
        assert "training" in normalized.lower()
        assert "held-out" in normalized.lower()
        assert "not a security sandbox" in normalized
        assert "not zero cost" in normalized or "not hard token or dollar" in normalized
    assert "--source workspace" in results
    assert "--source history" in results
    assert "No improvement" in results or "no improvement" in results


def test_documentation_index_links_all_authored_guides():
    index = _read("docs/README.md")
    for name in (
        "alpha-quickstart.md",
        "results.md",
        "safety.md",
        "run-artifacts.md",
        "contributing.md",
        "development.md",
        "roadmap.md",
        "release-checklist.md",
    ):
        assert f"]({name})" in index


def test_all_local_markdown_links_resolve():
    documents = [ROOT / "README.md", *sorted(DOCS.glob("*.md"))]
    missing = []
    for document in documents:
        for target in _local_markdown_links(document.read_text(encoding="utf-8")):
            resolved = (document.parent / target).resolve()
            if not resolved.is_file():
                missing.append(f"{document.relative_to(ROOT)} -> {target}")
    assert missing == []


def test_project_urls_are_existing_public_repository_targets():
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    urls = project["urls"]
    expected = "https://github.com/LibreEvolve/libreevolve"
    assert urls["Homepage"] == expected
    assert urls["Repository"] == expected
    assert urls["Issues"] == expected + "/issues"
    assert urls["Documentation"] == expected + "/tree/main/docs"
    assert "pypi.org" not in " ".join(urls.values())


def test_docs_keep_future_items_and_example_slot_unpublished():
    readme = _read("README.md")
    roadmap = _read("docs/roadmap.md")
    assert "approved inspectable example viewer is not included" in readme
    assert "private\n[experimental repository](https://github.com/LibreEvolve/libreevolve-experimental)" in readme
    assert "not capabilities of this public engineering preview" in readme
    assert "Planned or proposed work" in roadmap
    assert "not current capabilities" in roadmap
    assert "automatic upload" in roadmap.lower()
