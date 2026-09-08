"""Real CLI interruption with a local fake Codex process, never a provider."""

import ctypes
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from click.testing import CliRunner
import pytest
import yaml

from libreevolve.cli import cli


@pytest.fixture
def local_child_reaper():
    """Reap this test's forcibly stopped grandchildren without relying on PID 1."""
    libc = ctypes.CDLL(None, use_errno=True)
    original = ctypes.c_int()
    assert libc.prctl(37, ctypes.byref(original), 0, 0, 0) == 0  # PR_GET_CHILD_SUBREAPER
    assert libc.prctl(36, 1, 0, 0, 0) == 0  # PR_SET_CHILD_SUBREAPER
    try:
        yield
    finally:
        assert libc.prctl(36, original.value, 0, 0, 0) == 0


def _reap_child(pid):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        waited_pid, status = os.waitpid(pid, os.WNOHANG)
        if waited_pid:
            return status
        time.sleep(0.05)
    raise AssertionError("Codex descendant survived forced group cancellation")


def _cleanup_owned_child(pid):
    """Never signal a numeric PID after it has been reaped or is not ours."""
    try:
        waited_pid, _ = os.waitpid(pid, os.WNOHANG)
        if not waited_pid:
            os.kill(pid, signal.SIGKILL)
            _reap_child(pid)
    except ChildProcessError:
        pass


@pytest.mark.skipif(sys.platform != "linux", reason="Uses Linux subreaping and nonreaping waitid")
def test_codex_cleanup_kills_group_before_reaping_already_exited_leader(tmp_path, local_child_reaper):
    from libreevolve.llm.codex_cli import _terminate_process_tree

    child_ready = tmp_path / "child-ready"
    child_pid_path = tmp_path / "child-pid"
    child_source = (
        "import pathlib, signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        f"pathlib.Path({str(child_ready)!r}).touch(); time.sleep(120)"
    )
    parent_source = (
        "import pathlib, subprocess, sys, time\n"
        f"child = subprocess.Popen([sys.executable, '-c', {child_source!r}])\n"
        f"pathlib.Path({str(child_pid_path)!r}).write_text(str(child.pid))\n"
        f"while not pathlib.Path({str(child_ready)!r}).exists(): time.sleep(0.01)\n"
    )
    proc = subprocess.Popen([sys.executable, "-c", parent_source], start_new_session=True)
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            exited = os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            if exited is not None:
                break
            time.sleep(0.01)
        else:
            pytest.fail("Fake Codex leader did not exit")
        # The leader is a zombie, deliberately not reaped via poll/wait yet.
        assert proc.returncode is None
        child_pid = int(child_pid_path.read_text(encoding="utf-8"))
        os.kill(child_pid, 0)
        _terminate_process_tree(proc)
        assert proc.returncode == 0
        status = _reap_child(child_pid)
        assert os.WIFSIGNALED(status) and os.WTERMSIG(status) == signal.SIGKILL
    finally:
        if proc.returncode is None:
            _terminate_process_tree(proc)
        if child_pid_path.exists():
            child_pid = int(child_pid_path.read_text(encoding="utf-8"))
            _cleanup_owned_child(child_pid)


@pytest.mark.skipif(sys.platform != "linux", reason="Uses Linux subreaping and POSIX signals")
@pytest.mark.parametrize("interruption", ["sigint", "deadline"])
def test_codex_alpha_interruption_reaps_child_and_saves_run(tmp_path, interruption, local_child_reaper):
    task = tmp_path / "task"
    created = CliRunner().invoke(cli, [
        "alpha", "init", str(task), "--model", "gpt-5.6-luna",
    ])
    assert created.exit_code == 0, created.output
    config_path = task / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["log_dir"] = str(tmp_path / "runs")
    config["backends"][0]["codex_home"] = str(tmp_path / "fake-auth")
    if interruption == "deadline":
        config.update(llm_call_timeout_sec=1, max_generations=1,
                      max_llm_calls=1, max_llm_provider_attempts=1)
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    executable = fake_bin / "codex"
    pids_path = tmp_path / "pids.json"
    ready_path = tmp_path / "ready"
    child_ready_path = tmp_path / "child-ready"
    # The descendant deliberately ignores TERM. A leader-only stop or a TERM
    # followed by reaping the leader would leave it alive in the detached group.
    child_source = (
        "import pathlib, signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        f"pathlib.Path({str(child_ready_path)!r}).touch(); time.sleep(120)"
    )
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, pathlib, signal, subprocess, sys, time\n"
        "assert sys.argv[1] == 'exec'\n"
        "assert sys.stdin.read()\n"
        f"child = subprocess.Popen([sys.executable, '-c', {child_source!r}])\n"
        "record = {'parent': os.getpid(), 'child': child.pid,\n"
        "          'output': sys.argv[sys.argv.index('--output-last-message') + 1],\n"
        "          'schema': sys.argv[sys.argv.index('--output-schema') + 1]}\n"
        f"pathlib.Path({str(pids_path)!r}).write_text(json.dumps(record))\n"
        f"while not pathlib.Path({str(child_ready_path)!r}).exists(): time.sleep(0.01)\n"
        f"pathlib.Path({str(ready_path)!r}).touch()\n"
        "while True: time.sleep(1)\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    env = os.environ.copy()
    # A fake-only PATH also excludes Windows codex.cmd/codex.exe shims, which
    # the resolver otherwise prioritizes over the POSIX executable.
    env["PATH"] = str(fake_bin)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    env["PYTHON_DOTENV_DISABLED"] = "1"
    env.pop("OPENAI_API_KEY", None)
    proc = subprocess.Popen(
        [sys.executable, "-m", "libreevolve", "run", str(task), "--run-name", "cancelled"],
        cwd=tmp_path, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, start_new_session=True,
    )
    try:
        deadline = time.monotonic() + 30
        while not ready_path.exists() and proc.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        if not ready_path.exists():
            pytest.fail(f"Fake Codex did not start; CLI exit={proc.poll()}")
        record = json.loads(pids_path.read_text(encoding="utf-8"))
        for key in ("parent", "child"):
            os.kill(record[key], 0)
            assert os.getpgid(record[key]) == record["parent"]
        assert record["parent"] != proc.pid

        if interruption == "sigint":
            # Signal only the CLI, not the detached Codex group. Cleanup must
            # be initiated by the interrupted backend's finally block.
            proc.send_signal(signal.SIGINT)
        output, _ = proc.communicate(timeout=15)
        if interruption == "sigint":
            assert proc.returncode == 130, output
            assert "Cancelled" in output
            assert "may be incomplete" in output
        else:
            assert proc.returncode == 0, output
        status = _reap_child(record["child"])
        assert os.WIFSIGNALED(status)
        assert os.WTERMSIG(status) == signal.SIGKILL
        for key in ("parent", "child"):
            with pytest.raises(ProcessLookupError):
                os.kill(record[key], 0)
        assert not Path(record["output"]).exists()
        assert not Path(record["schema"]).exists()

        run_dir = tmp_path / "runs" / "cancelled"
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        runtime = manifest["runtime"]
        if interruption == "sigint":
            assert runtime["status"] == "aborted"
            assert runtime["stop_reason"] == "aborted"
            assert runtime["abort"]["exception_type"] == "KeyboardInterrupt"
            assert runtime["abort"]["keyboard_interrupt"] is True
        else:
            assert runtime["status"] == "completed"
            calls = [json.loads(line) for line in
                     (run_dir / "llm_calls.jsonl").read_text(encoding="utf-8").splitlines()]
            assert len(calls) == 1
            assert calls[0]["error_type"] == "ProviderCallTimeoutError"
            cancellation = calls[0]["cancellation_record"]
            assert cancellation["in_flight_cancellation"] == "cooperative_backend_worker_finished"
            assert cancellation["hard_cancel_ready"] is False
            assert cancellation["remaining_gap"] == "remote_provider_cancellation_unverified"
        assert (run_dir / "best.py").is_file()
        assert (run_dir / "best_workspace").is_dir()
        assert (run_dir / "history.jsonl").read_text(encoding="utf-8").strip()
    finally:
        # Clean up even if this test catches the old orphaning behavior.
        if proc.poll() is None:
            proc.kill()
        proc.communicate(timeout=10)
        if pids_path.exists():
            record = json.loads(pids_path.read_text(encoding="utf-8"))
            _cleanup_owned_child(record["parent"])
            _cleanup_owned_child(record["child"])
