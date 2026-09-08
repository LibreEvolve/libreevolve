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


def test_ci_trigger_contract_keeps_hosted_workflows_automatic_without_paid_dispatch():
    tests_path = Path(".github/workflows/tests.yml")
    tests_text = tests_path.read_text(encoding="utf-8")
    tests_workflow = yaml.load(tests_text, Loader=yaml.BaseLoader)
    tests_triggers = tests_workflow.get("on", tests_workflow.get(True))

    assert {"workflow_dispatch", "pull_request", "push", "schedule"} <= set(tests_triggers)
    required_paths = {
        ".github/workflows/tests.yml",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".secrets.baseline",
        "AGENTS.md",
        "README.md",
        "ROADMAP.md",
        "docs/**",
        "libreevolve/**",
        "old/**",
        "papers/**",
        "pyproject.toml",
        "tests/**",
    }
    for trigger in ("pull_request", "push"):
        assert required_paths <= set(tests_triggers[trigger]["paths"])
    assert tests_triggers["schedule"][0]["cron"] == "17 6 * * 1"

    installed_path = Path(".github/workflows/alpha-installed.yml")
    installed_text = installed_path.read_text(encoding="utf-8")
    installed_workflow = yaml.load(installed_text, Loader=yaml.BaseLoader)
    installed_triggers = installed_workflow.get("on", installed_workflow.get(True))
    assert {"workflow_dispatch", "pull_request", "push"} <= set(installed_triggers)
    installed_required_paths = {
        "libreevolve/**",
        "pyproject.toml",
        "MANIFEST.in",
        ".github/workflows/alpha-installed.yml",
    }
    for trigger in ("pull_request", "push"):
        assert installed_required_paths <= set(installed_triggers[trigger]["paths"])
    for text in (tests_text, installed_text):
        assert "run_live_integration" not in text
        assert "paper_manifest" not in text
