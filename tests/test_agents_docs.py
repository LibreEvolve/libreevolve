from pathlib import Path
import re
import tomllib

import yaml

from libreevolve.core.artifact_schema import run_artifact_schema


def test_agents_instructions_do_not_pin_stale_test_counts():
    text = Path("AGENTS.md").read_text(encoding="utf-8")

    assert 'py -3.12 -m pytest tests/ -m "not integration" --tb=short' in text
    assert not re.search(r"\(\d+ selected\)", text)


def test_agents_instructions_track_runtime_artifacts_and_prompt_owner():
    text = Path("AGENTS.md").read_text(encoding="utf-8")

    for expected in (
        "PromptSampler",
        "failure/quarantine JSONL streams",
        "archive_events.jsonl",
        "llm_calls.jsonl",
        "best_workspace/",
        "evaluator_artifacts/",
        "plugin_artifacts/",
        "ProgramDatabase.admit()",
    ):
        assert expected in text


def test_agents_instructions_distinguish_threshold_from_archive_retention():
    text = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "VALID_THRESHOLD = 0.0 is the pre-admission eligibility gate" in text
    assert "MAP-Elites" in text
    assert 'reason="not_improving_cell"' in text
    assert "sampling_eligible" in text
    assert not re.search(
        r"score\s*>=\s*0\s+enter\s+the\s+archive\s+through\s+"
        r"ProgramDatabase\.admit\(\)",
        text,
        re.IGNORECASE,
    )


def test_configuration_docs_track_sampling_strategy_fields():
    text = Path("docs/configuration.md").read_text(encoding="utf-8")

    for expected in (
        "`explore_ratio` (`0.3`)",
        "`parent_selection_strategy` (`\"mixed\"`)",
        "`inspiration_strategy` (`\"mixed\"`)",
        "`mixed`, `exploit`, `explore`, `metric`, `frontier`, `lineage`",
        "`mixed`, `random`, `selection`, `metric`, `frontier`, `lineage`",
    ):
        assert expected in text


def test_configuration_docs_track_archive_event_cleanup_stream():
    text = Path("docs/configuration.md").read_text(encoding="utf-8")

    assert "`run_collision_policy`" in text
    assert "`archive_events*.jsonl`" in text


def test_development_docs_track_detect_secrets_baseline_workflow():
    development = Path("docs/development.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    pre_commit = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")

    for text in (development, readme):
        assert ".secrets.baseline" in text
        assert "# pragma: allowlist secret" in text
        assert "unstaged" in text
        assert "provider/API failure" in text

    assert "detect-secrets" in pre_commit
    assert "--baseline" in pre_commit
    assert ".secrets.baseline" in pre_commit


def test_readme_and_docs_route_agents_operating_contract():
    readme = Path("README.md").read_text(encoding="utf-8")
    docs_readme = Path("docs/README.md").read_text(encoding="utf-8")
    development = Path("docs/development.md").read_text(encoding="utf-8")
    agents = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "[AGENTS.md](AGENTS.md)" in readme
    assert "agent-facing operating contract" in readme
    assert "[AGENTS.md](../AGENTS.md)" in docs_readme
    assert "agent-facing operating contract" in docs_readme
    assert "agent-facing instructions such as `AGENTS.md`" in development
    assert "docs/development.md" in agents
    assert "docs/backends.md" in agents
    assert "docs/run-artifacts.md" in agents
    assert "papers/README.md" in agents


def test_tests_workflow_covers_docs_papers_and_todo_changes():
    workflow = yaml.safe_load(Path(".github/workflows/tests.yml").read_text(encoding="utf-8"))
    triggers = workflow.get("on", workflow.get(True))

    assert "workflow_dispatch" in triggers
    assert "pull_request" in triggers
    assert "push" in triggers

    required_paths = {
        "AGENTS.md",
        "README.md",
        "ROADMAP.md",
        "docs/**",
        "libreevolve/**",
        "papers/**",
        "tests/**",
        ".secrets.baseline",
    }
    for trigger in ("pull_request", "push"):
        assert required_paths <= set(triggers[trigger]["paths"])

    assert "secrets" in workflow["jobs"]
    assert "unit" in workflow["jobs"]
    assert "paper_docs" in workflow["jobs"]
    assert "release_artifact" in workflow["jobs"]
    assert "integration" in workflow["jobs"]

    unit = workflow["jobs"]["unit"]
    assert unit["name"] == "Unit Tests (${{ matrix.os }}, Python ${{ matrix.python-version }})"
    assert unit["runs-on"] == "${{ matrix.os }}"
    assert set(unit["strategy"]["matrix"]["os"]) == {
        "ubuntu-latest",
        "windows-latest",
        "macos-latest",
    }
    assert set(unit["strategy"]["matrix"]["python-version"]) == {"3.11", "3.12"}

    paper_docs = workflow["jobs"]["paper_docs"]
    assert paper_docs["name"] == "Paper and Docs Checks"
    paper_doc_commands = "\n".join(
        step.get("run", "") for step in paper_docs.get("steps", [])
    )
    assert "python -m libreevolve.tools.paper_manifest --root ." in paper_doc_commands
    assert 'Path("tests").glob("test_paper_*.py")' in paper_doc_commands
    assert 'Path("tests").glob("test_*boundary.py")' in paper_doc_commands
    assert 'Path("tests/test_agents_docs.py")' in paper_doc_commands
    assert 'subprocess.call(command)' in paper_doc_commands
    assert "--require-local-pdfs" not in paper_doc_commands

    release_artifact = workflow["jobs"]["release_artifact"]
    assert release_artifact["name"] == "Release Artifact Smoke"
    release_commands = "\n".join(
        step.get("run", "") for step in release_artifact.get("steps", [])
    )
    assert 'python -m pip install -e ".[dev]"' in release_commands
    assert "python -m build --wheel --sdist" in release_commands
    assert "zipfile.ZipFile" in release_commands
    assert "tarfile.open" in release_commands
    assert 'Path("libreevolve").rglob("*")' in release_commands
    assert "wheel is missing package files" in release_commands
    assert "sdist is missing package files" in release_commands
    assert "python -m libreevolve.tools.release_artifact_provenance --root ." in release_commands
    upload_steps = [
        step
        for step in release_artifact.get("steps", [])
        if step.get("uses") == "actions/upload-artifact@v4"
    ]
    assert upload_steps
    assert upload_steps[0]["with"]["name"] == "libreevolve-release-smoke-artifacts"
    assert upload_steps[0]["with"]["path"] == "dist/*"
    assert "python -m venv .venv-wheel-smoke" in release_commands
    assert "python -m pip install dist/*.whl" in release_commands
    assert "libreevolve --help" in release_commands
    assert "python -m libreevolve --help" in release_commands


def test_dev_dependencies_include_release_build_tooling():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert "build>=1.2" in pyproject["project"]["optional-dependencies"]["dev"]
    assert pyproject["tool"]["setuptools"]["include-package-data"] is True


def test_manifest_includes_package_data():
    manifest = Path("MANIFEST.in").read_text(encoding="utf-8")

    assert "recursive-include libreevolve/problems/examples" in manifest
    for pattern in ("*.yaml", "*.txt", "*.json", "*.bin", "*.md"):
        assert pattern in manifest
    assert "recursive-include libreevolve/problems/benchmarks" in manifest
    assert "*.ipynb" in manifest


def test_release_checklist_documents_smoke_and_remaining_release_gates():
    checklist = Path("docs/release-checklist.md").read_text(encoding="utf-8")

    for expected in (
        "py -3.12 -m build --wheel --sdist",
        "`libreevolve/` package tree",
        "isolated virtual environment",
        "libreevolve --help",
        "python -m libreevolve --help",
        "dist/release_artifact_provenance.json",
        "Signed release provenance",
        "Published-index or private-index artifact verification",
    ):
        assert expected in checklist


def test_run_artifact_docs_list_current_schema_jsonl_streams():
    readme = Path("README.md").read_text(encoding="utf-8")
    run_artifacts = Path("docs/run-artifacts.md").read_text(encoding="utf-8")
    streams = sorted(run_artifact_schema()["jsonl_records"])

    for stream in streams:
        assert f"`{stream}`" in readme
        assert f"`{stream}`" in run_artifacts


def test_run_artifact_docs_list_schema_quarantine_streams():
    run_artifacts = Path("docs/run-artifacts.md").read_text(encoding="utf-8")
    schema = run_artifact_schema()
    streams = sorted(schema["quarantine_jsonl_records"])

    for stream in streams:
        record = schema["quarantine_jsonl_records"][stream]
        assert f"`{stream}`" in run_artifacts
        assert record["source_stream"] in schema["jsonl_records"] or record[
            "source_stream"
        ] == "manifest.json"
        assert record["diagnostic_record_schema"].startswith(
            "libreevolve.strict_jsonl_quarantine"
        )
        assert (
            record["retention_mode_field"]
            == "config.quarantine_snapshot_retention_mode"
        )
