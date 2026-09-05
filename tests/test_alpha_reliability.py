"""Offline alpha regressions and explicit characterizations of open defects."""

import asyncio
import inspect
import json
from pathlib import Path

import pytest

from libreevolve.core import loop, prompt, prompt_context_policy, run_inspection
from libreevolve.core.artifact_schema import validate_paper_artifact_lifecycle_manifest
from libreevolve.plugins.base import PluginBase
from tests.core.test_loop_characterization import _FakeLLM, _config, _problem, _rows


def test_mr014_reads_repository_run_artifacts_guide():
    expected = Path(__file__).resolve().parents[1] / "docs" / "run-artifacts.md"
    assert run_inspection.run_artifacts_doc_text() == expected.read_text(encoding="utf-8")


def test_mr014_uses_root_docs_even_when_package_docs_exist(tmp_path, monkeypatch):
    module = tmp_path / "libreevolve" / "core" / "run_inspection.py"
    module.parent.mkdir(parents=True)
    module.touch()
    for directory, text in [(tmp_path, "root guide"), (module.parents[1], "wrong guide")]:
        (directory / "docs").mkdir()
        (directory / "docs" / "run-artifacts.md").write_text(text, encoding="utf-8")
    monkeypatch.setattr(run_inspection, "__file__", str(module))
    assert run_inspection.run_artifacts_doc_text() == "root guide"


def test_installed_layout_without_docs_skips_only_documentation_checks(tmp_path, monkeypatch):
    # Simulate site-packages layout; this is not a wheel installation test.
    module = tmp_path / "site-packages" / "libreevolve" / "core" / "run_inspection.py"
    module.parent.mkdir(parents=True)
    module.touch()
    monkeypatch.setattr(run_inspection, "__file__", str(module))
    # An unrelated working-directory guide must not become validation authority.
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "run-artifacts.md").write_text("unrelated", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    text = run_inspection.run_artifacts_doc_text()
    assert text is None
    absent = validate_paper_artifact_lifecycle_manifest({}, run_artifacts_doc_text=text)
    empty = validate_paper_artifact_lifecycle_manifest({}, run_artifacts_doc_text="")
    assert absent["ok"] is False  # Missing docs do not certify an invalid manifest.
    assert absent["documented_refs"] == absent["missing_doc_paths"] == []
    absent_codes = {issue["code"] for issue in absent["issues"]}
    empty_codes = {issue["code"] for issue in empty["issues"]}
    assert "missing_paper_artifact_doc_paths" not in absent_codes
    assert empty_codes == absent_codes | {"missing_paper_artifact_doc_paths"}
    assert empty["missing_doc_paths"]


def test_mr012_export_signature_exception_identity_and_keyword_contract():
    validate = prompt.validate_prompt_context_policy
    assert validate is prompt_context_policy.validate_prompt_context_policy
    assert prompt.PromptTemplateError is prompt_context_policy.PromptTemplateError
    parameters = inspect.signature(validate).parameters
    assert list(parameters) == [
        "value", "validated_context_source_paths",
        "validated_recent_failure_required_changed_files",
        "validated_recent_failure_excluded_changed_files",
    ]
    assert parameters["value"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in list(parameters.values())[1:])
    assert validate(None)["schema"] == prompt.PROMPT_CONTEXT_POLICY_SCHEMA
    assert validate(
        {"context_source_paths": ["notes.md"]},
        validated_context_source_paths=["notes.md"],
    )["context_source_paths"] == ["notes.md"]
    with pytest.raises(prompt.PromptTemplateError, match="must be a mapping"):
        validate([])
    with pytest.raises(TypeError):
        validate(None, [])


def test_mr012_duplicated_policy_constants_currently_agree():
    names = [name for name in prompt_context_policy.__all__ if name.startswith("PROMPT_CONTEXT_POLICY_")]
    assert names
    for name in names:
        assert getattr(prompt, name) == getattr(prompt_context_policy, name), name
    assert prompt.PROMPT_TEMPLATE_FIELDS == prompt_context_policy._PROMPT_POLICY_TEMPLATE_FIELDS
    assert prompt.PROMPT_TEMPLATE_FIELDS is not prompt_context_policy._PROMPT_POLICY_TEMPLATE_FIELDS


@pytest.mark.parametrize("exception_type", [KeyboardInterrupt, asyncio.CancelledError, SystemExit])
@pytest.mark.parametrize("async_sampling", [False, True])
def test_worker_cancellation_aborts_sync_and_async(tmp_path, monkeypatch, exception_type, async_sampling):
    original = exception_type("synthetic worker cancellation")

    class CancelLLM(_FakeLLM):
        def generate(self, prompt, role="mutation"):
            raise original

    monkeypatch.setattr(loop, "build_llm", lambda config: CancelLLM())
    config = _config(tmp_path, "worker_cancel", async_llm_sampling=async_sampling)
    problem = _problem(tmp_path)
    with pytest.raises(exception_type) as caught:
        loop.evolve(problem, config)
    assert caught.value is original
    run_dir = tmp_path / "runs" / "worker_cancel"
    runtime = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["runtime"]
    assert runtime["status"] == "aborted"
    failures = _rows(run_dir, "failure_history.jsonl")
    assert failures == []
    assert runtime["abort"]["exception_type"] == exception_type.__name__
    assert runtime["abort"]["keyboard_interrupt"] is (exception_type is KeyboardInterrupt)
    assert runtime["best_artifact_export"]["status"] == "completed"
    assert (run_dir / "best_workspace" / "main.py").read_text(encoding="utf-8") == "x=1\n"
    assert "aborted best-so-far" in run_inspection.inspect_run(run_dir).runtime_status


@pytest.mark.parametrize("exception_type", [KeyboardInterrupt, asyncio.CancelledError, SystemExit])
@pytest.mark.parametrize("async_evaluation", [False, True])
def test_cancellation_persists_abort_and_seed_before_reraising(tmp_path, monkeypatch, exception_type, async_evaluation):
    original = exception_type("synthetic cancellation")

    class CancelPlugin(PluginBase):
        def on_generation_start(self, generation, db):
            raise original

    monkeypatch.setattr(loop, "build_llm", lambda config: _FakeLLM())
    config = _config(tmp_path, "cancel", async_candidate_evaluation=async_evaluation)
    with pytest.raises(exception_type) as caught:
        loop.evolve(_problem(tmp_path), config, plugins=[CancelPlugin()])
    assert caught.value is original
    run_dir = tmp_path / "runs" / "cancel"
    runtime = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["runtime"]
    assert runtime["status"] == runtime["stop_reason"] == "aborted"
    assert runtime["abort"]["exception_type"] == exception_type.__name__
    assert runtime["abort"]["keyboard_interrupt"] is (exception_type is KeyboardInterrupt)
    assert len(_rows(run_dir, "history.jsonl")) == 1
    assert runtime["best_artifact_export"]["status"] == "completed"
    assert (run_dir / "best_workspace" / "main.py").read_text(encoding="utf-8") == "x=1\n"
    assert _rows(run_dir, "controller_budget_events.jsonl")[-1]["stop_reason"] == "aborted"
    assert "aborted best-so-far" in run_inspection.inspect_run(run_dir).runtime_status
    if async_evaluation:
        pending = runtime["history"]["async_candidate_evaluation_controller"]["pending_work"]
        assert all(value == 0 for value in pending.values())


@pytest.mark.parametrize("fault_site", [
    "log_controller_budget_event", "_runtime_history_summary", "_runtime_rng_state",
    "export_best_artifacts", "update_manifest_runtime",
])
def test_abort_assembly_failure_must_preserve_original_cancellation(tmp_path, monkeypatch, fault_site):
    original = asyncio.CancelledError("original cancellation")
    secret = "sk-proj_synthetic_abort_failure_1234567890"  # pragma: allowlist secret

    class CancelPlugin(PluginBase):
        def on_generation_start(self, generation, db):
            def fail(*args, **kwargs):
                raise OSError(f"secondary persistence fault token={secret}")

            target = db if fault_site in {"log_controller_budget_event", "update_manifest_runtime"} else loop
            monkeypatch.setattr(target, fault_site, fail)
            raise original

    monkeypatch.setattr(loop, "build_llm", lambda config: _FakeLLM())
    with pytest.raises(asyncio.CancelledError) as caught:
        loop.evolve(_problem(tmp_path), _config(tmp_path, "abort_fault"), plugins=[CancelPlugin()])
    assert caught.value is original
    notes = "\n".join(original.__notes__)
    assert "OSError" in notes and "secondary persistence fault" in notes
    assert secret not in notes
    assert "[REDACTED]" in notes
    run_dir = tmp_path / "runs" / "abort_fault"
    runtime = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8")).get("runtime", {})
    assert runtime.get("status") != "completed"
    if fault_site != "update_manifest_runtime":
        assert runtime["status"] == "aborted"
        assert runtime["abort"]["exception_type"] == "CancelledError"
        assert runtime["abort"]["keyboard_interrupt"] is False
    if fault_site != "export_best_artifacts":
        assert (run_dir / "best_workspace" / "main.py").read_text(encoding="utf-8") == "x=1\n"


@pytest.mark.parametrize("controller_name", ["AsyncCandidateEvaluationController", "AsyncLLMSamplerController"])
@pytest.mark.parametrize("snapshot_fails", [False, True])
def test_shutdown_control_exception_cannot_mask_original_or_skip_abort(tmp_path, monkeypatch, controller_name, snapshot_fails):
    original = KeyboardInterrupt("original interrupt")
    controller_type = getattr(loop, controller_name)
    real_close = controller_type.close

    def fail_snapshot():
        raise SystemExit("secondary snapshot failure")

    def close_then_fail(controller):
        real_close(controller)  # Actually drain and stop the test's worker threads.
        if snapshot_fails:
            monkeypatch.setattr(controller, "snapshot", fail_snapshot)
        raise asyncio.CancelledError("secondary shutdown failure")

    class CancelPlugin(PluginBase):
        def on_generation_start(self, generation, db):
            raise original

    monkeypatch.setattr(controller_type, "close", close_then_fail)
    monkeypatch.setattr(loop, "build_llm", lambda config: _FakeLLM())
    config = _config(
        tmp_path, "shutdown_fault",
        async_candidate_evaluation=controller_name == "AsyncCandidateEvaluationController",
        async_llm_sampling=controller_name == "AsyncLLMSamplerController",
    )
    with pytest.raises(KeyboardInterrupt) as caught:
        loop.evolve(_problem(tmp_path), config, plugins=[CancelPlugin()])
    assert caught.value is original
    assert "secondary shutdown failure" in "\n".join(original.__notes__)
    if snapshot_fails:
        assert "secondary snapshot failure" in "\n".join(original.__notes__)
    run_dir = tmp_path / "runs" / "shutdown_fault"
    runtime = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["keyboard_interrupt"] is True
    assert runtime["best_artifact_export"]["status"] == "completed"


def test_abort_exports_latest_retained_child(tmp_path, monkeypatch):
    original = KeyboardInterrupt("after child admission")

    class CancelPlugin(PluginBase):
        def on_generation_end(self, generation, best):
            raise original

    monkeypatch.setattr(loop, "build_llm", lambda config: _FakeLLM())
    with pytest.raises(KeyboardInterrupt) as caught:
        loop.evolve(_problem(tmp_path), _config(tmp_path, "child_abort"), plugins=[CancelPlugin()])
    assert caught.value is original
    run_dir = tmp_path / "runs" / "child_abort"
    assert len(_rows(run_dir, "history.jsonl")) == 2
    assert (run_dir / "best_workspace" / "main.py").read_text(encoding="utf-8").strip() == "x=2"
    assert (run_dir / "best.py").read_text(encoding="utf-8").strip() == "x=2"
    result = run_inspection.inspect_run(run_dir)
    assert result.best["code"].strip() == "x=2"
    assert "aborted best-so-far" in result.runtime_status


def test_abort_before_seed_admission_has_no_best_export(tmp_path, monkeypatch):
    original = KeyboardInterrupt("seed evaluation interrupted")
    monkeypatch.setattr(loop, "build_llm", lambda config: _FakeLLM())

    def cancel(*args, **kwargs):
        raise original

    monkeypatch.setattr(loop.CascadeEvaluator, "evaluate", cancel)
    with pytest.raises(KeyboardInterrupt) as caught:
        loop.evolve(_problem(tmp_path), _config(tmp_path, "no_best"))
    assert caught.value is original
    run_dir = tmp_path / "runs" / "no_best"
    runtime = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["keyboard_interrupt"] is True
    assert "best_artifact_export" not in runtime
    assert not (run_dir / "best_workspace").exists()


def test_finalization_note_tolerates_unstringifiable_secondary_exception():
    class BrokenError(BaseException):
        def __str__(self):
            raise KeyboardInterrupt("broken formatter")

    original = KeyboardInterrupt("original")
    loop._note_abort_finalization_failure(original, BrokenError())
    assert "message unavailable" in original.__notes__[0]


def test_abort_export_io_failure_is_recorded_without_masking_cancellation(tmp_path, monkeypatch):
    from libreevolve.core import best_artifacts

    original = KeyboardInterrupt("original cancellation")
    secret = "sk-proj_synthetic_export_failure_1234567890"  # pragma: allowlist secret

    class CancelPlugin(PluginBase):
        def on_generation_start(self, generation, db):
            raise original

    def fail_export(*args, **kwargs):
        raise OSError(f"export unavailable token={secret}")

    monkeypatch.setattr(best_artifacts, "_write_best_artifacts", fail_export)
    monkeypatch.setattr(loop, "build_llm", lambda config: _FakeLLM())
    with pytest.raises(KeyboardInterrupt) as caught:
        loop.evolve(_problem(tmp_path), _config(tmp_path, "export_io"), plugins=[CancelPlugin()])
    assert caught.value is original
    run_dir = tmp_path / "runs" / "export_io"
    manifest_text = (run_dir / "manifest.json").read_text(encoding="utf-8")
    runtime = json.loads(manifest_text)["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["keyboard_interrupt"] is True
    assert runtime["best_artifact_export"]["status"] == "failed"
    assert not (run_dir / "best_workspace").exists()
    notes = "\n".join(original.__notes__)
    assert "Best artifact export failed" in notes
    assert secret not in notes + manifest_text
    assert "[REDACTED]" in notes


def test_evolve_preserves_original_if_abort_writer_itself_fails(tmp_path, monkeypatch):
    original = KeyboardInterrupt("original cancellation")

    class CancelPlugin(PluginBase):
        def on_generation_start(self, generation, db):
            raise original

    def fail(*args, **kwargs):
        raise SystemExit("secondary abort writer failure")

    monkeypatch.setattr(loop, "_write_aborted_runtime", fail)
    monkeypatch.setattr(loop, "build_llm", lambda config: _FakeLLM())
    with pytest.raises(KeyboardInterrupt) as caught:
        loop.evolve(_problem(tmp_path), _config(tmp_path, "writer_failure"), plugins=[CancelPlugin()])
    assert caught.value is original
    assert "secondary abort writer failure" in "\n".join(original.__notes__)
