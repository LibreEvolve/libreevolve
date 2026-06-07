from pathlib import Path
import re

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
        "`mixed`, `exploit`, `explore`, `metric`, `novelty`, and `recency`",
        "`mixed`, `random`, `selection`, `metric`, `novelty`, and `recency`",
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
    assert "integration" in workflow["jobs"]


def test_run_artifact_docs_list_current_schema_jsonl_streams():
    readme = Path("README.md").read_text(encoding="utf-8")
    run_artifacts = Path("docs/run-artifacts.md").read_text(encoding="utf-8")
    streams = sorted(run_artifact_schema()["jsonl_records"])

    for stream in streams:
        assert f"`{stream}`" in readme
        assert f"`{stream}`" in run_artifacts
