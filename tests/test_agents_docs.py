"""Keep preview documentation and package declarations aligned."""

from pathlib import Path
import re
import tomllib

import yaml

from libreevolve.llm.backend_registry import builtin_backend_registry


def test_preview_scope_and_honest_limits_are_documented():
    for path in ("README.md", "AGENTS.md", "docs/alpha-quickstart.md"):
        text = " ".join(Path(path).read_text(encoding="utf-8").lower().split())
        assert "engineering preview" in text
        assert "gpt-5.6-luna" in text
        assert "high" in text
        assert "not a security sandbox" in text
        assert "unknown" in text
    assert "experimental" in Path("README.md").read_text()
    assert "external usability" in Path("README.md").read_text()


def test_local_documentation_links_resolve():
    files = [Path("README.md"), Path("AGENTS.md"), *Path("docs").glob("*.md")]
    for path in files:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            relative = target.split("#", 1)[0]
            assert (path.parent / relative).exists(), (str(path), target)


def test_package_has_only_preview_provider_and_example():
    assert set(builtin_backend_registry()) == {"codex"}
    examples = Path("libreevolve/problems/examples")
    assert {p.name for p in examples.iterdir() if p.is_dir() and p.name != "__pycache__"
            and any(f.is_file() and "__pycache__" not in f.parts for f in p.rglob("*"))} == {"bin_packing"}
    project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
    dependencies = " ".join(project["dependencies"]).lower()
    for removed in ("anthropic", "openai", "google-genai", "ollama", "pypdf", "dotenv"):
        assert removed not in dependencies


def test_ci_pause_remains_manual_and_has_no_paid_test_dispatch():
    for path in Path(".github/workflows").glob("*.yml"):
        workflow = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        assert set(workflow["on"]) == {"workflow_dispatch"}
        assert "run_live_integration" not in path.read_text()
        assert "paper_manifest" not in path.read_text()
