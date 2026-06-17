from __future__ import annotations

import json
import subprocess

import pytest

from libreevolve.llm.codex_cli import CodexCLIBackend, _resolve_codex_auth


class _FakeCodexProcess:
    returncode = 0

    def __init__(self, cmd, *args, output_text="OK", seen=None, **kwargs):
        self.cmd = cmd
        self.output_text = output_text
        self.seen = seen if seen is not None else {}
        self.seen["cmd"] = cmd
        self.seen["env"] = kwargs["env"]
        self.seen["cwd"] = kwargs["cwd"]
        self.seen["stdin_text"] = None

    def communicate(self, prompt, timeout=None):
        self.seen["stdin_text"] = prompt
        output_path = self.cmd[self.cmd.index("--output-last-message") + 1]
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(self.output_text)
        return "codex stdout", "codex stderr"

    def poll(self):
        return 0


def test_codex_auth_name_resolves_from_mapping(tmp_path):
    auth_home = tmp_path / "auth-a"
    auth = _resolve_codex_auth(
        codex_home=None,
        auth_name="account_a",
        auth_homes={"account_a": {"home": str(auth_home)}},
        auth_registry_path=None,
    )

    assert auth.home == str(auth_home.resolve())
    assert auth.name == "account_a"
    assert auth.source == "auth_name"


def test_codex_auth_name_resolves_from_registry(tmp_path):
    auth_home = tmp_path / "auth-b"
    registry_path = tmp_path / "auths.json"
    registry_path.write_text(
        json.dumps({"auths": {"account_b": str(auth_home)}}),
        encoding="utf-8",
    )

    auth = _resolve_codex_auth(
        codex_home=None,
        auth_name="account_b",
        auth_homes=None,
        auth_registry_path=str(registry_path),
    )

    assert auth.home == str(auth_home.resolve())
    assert auth.name == "account_b"
    assert auth.source == "auth_name"


def test_codex_current_auth_resolves_from_registry_pointer(tmp_path):
    auth_home = tmp_path / "active-auth"
    registry_path = tmp_path / "auths.json"
    registry_path.write_text(
        json.dumps(
            {
                "current_auth": "account_active",
                "auths": {"account_active": {"home": str(auth_home)}},
            }
        ),
        encoding="utf-8",
    )

    auth = _resolve_codex_auth(
        codex_home=None,
        auth_name="current",
        auth_homes=None,
        auth_registry_path=str(registry_path),
    )

    assert auth.home == str(auth_home.resolve())
    assert auth.name == "current"
    assert auth.source == "auth_name"


def test_codex_auth_defaults_to_registry_current(tmp_path):
    auth_home = tmp_path / "active-auth"
    registry_path = tmp_path / "auths.json"
    registry_path.write_text(
        json.dumps(
            {
                "current_auth": "account_active",
                "auths": {"account_active": {"home": str(auth_home)}},
            }
        ),
        encoding="utf-8",
    )

    auth = _resolve_codex_auth(
        codex_home=None,
        auth_name=None,
        auth_homes=None,
        auth_registry_path=str(registry_path),
    )

    assert auth.home == str(auth_home.resolve())
    assert auth.name == "current"
    assert auth.source == "registry_current"


def test_codex_auth_alias_resolves_from_registry(tmp_path):
    auth_home = tmp_path / "auth-home"
    registry_path = tmp_path / "auths.json"
    registry_path.write_text(
        json.dumps(
            {
                "aliases": {"benchmark": "account_d"},
                "auths": {"account_d": str(auth_home)},
            }
        ),
        encoding="utf-8",
    )

    auth = _resolve_codex_auth(
        codex_home=None,
        auth_name="benchmark",
        auth_homes=None,
        auth_registry_path=str(registry_path),
    )

    assert auth.home == str(auth_home.resolve())
    assert auth.name == "benchmark"
    assert auth.source == "auth_name"


def test_codex_auth_name_resolves_from_environment(tmp_path, monkeypatch):
    auth_home = tmp_path / "auth-c"
    monkeypatch.setenv("LIBREEVOLVE_CODEX_AUTH_ACCOUNT_C_HOME", str(auth_home))

    auth = _resolve_codex_auth(
        codex_home=None,
        auth_name="account-c",
        auth_homes=None,
        auth_registry_path=str(tmp_path / "missing.json"),
    )

    assert auth.home == str(auth_home.resolve())
    assert auth.name == "account-c"
    assert auth.source == "auth_name"


def test_codex_auth_name_rejects_unknown_label(tmp_path):
    with pytest.raises(ValueError, match="Unknown Codex auth_name"):
        _resolve_codex_auth(
            codex_home=None,
            auth_name="missing",
            auth_homes=None,
            auth_registry_path=str(tmp_path / "missing.json"),
        )


def test_codex_backend_exposes_resolved_auth_metadata(tmp_path):
    backend = CodexCLIBackend(
        model="gpt-5.3-codex-spark",
        auth_name="named",
        auth_homes={"named": str(tmp_path / "auth-home")},
    )

    assert backend.name == "codex-cli/gpt-5.3-codex-spark"
    assert backend._auth_name == "named"
    assert backend._auth_source == "auth_name"


def test_codex_backend_normalizes_feature_strings(tmp_path):
    backend = CodexCLIBackend(
        model="gpt-5.5",
        auth_name="named",
        auth_homes={"named": str(tmp_path / "auth-home")},
        enable_features="one two",
        disable_features="shell_tool browser_use",
    )

    assert backend._enable_features == ("one", "two")
    assert backend._disable_features == ("shell_tool", "browser_use")


def test_codex_backend_invokes_codex_exec_and_writes_transcript(tmp_path, monkeypatch):
    seen = {}

    def fake_popen(cmd, *args, **kwargs):
        return _FakeCodexProcess(cmd, *args, seen=seen, **kwargs)

    transcript_dir = tmp_path / "transcripts"
    monkeypatch.setattr("libreevolve.llm.codex_cli._resolve_codex_command", lambda: "codex")
    monkeypatch.setattr("libreevolve.llm.codex_cli.subprocess.Popen", fake_popen)

    backend = CodexCLIBackend(
        model="gpt-5.5",
        codex_home=str(tmp_path / "auth-home"),
        cwd=str(tmp_path),
        sandbox="workspace-write",
        timeout_sec=12,
        reasoning_effort="high",
        transcript_dir=str(transcript_dir),
        approval_policy="never",
        ignore_user_config=True,
        ignore_rules=True,
        ephemeral=True,
        enable_features="alpha",
        disable_features=["beta"],
    )

    assert backend.generate("Return OK") == "OK"

    cmd = seen["cmd"]
    assert cmd[:2] == ["codex", "exec"]
    assert cmd[-1] == "-"
    assert ["--model", "gpt-5.5"] == cmd[2:4]
    assert "--ignore-user-config" in cmd
    assert "--ignore-rules" in cmd
    assert "--ephemeral" in cmd
    assert ["--enable", "alpha"] == cmd[cmd.index("--enable") : cmd.index("--enable") + 2]
    assert ["--disable", "beta"] == cmd[cmd.index("--disable") : cmd.index("--disable") + 2]
    assert '-c' in cmd
    assert 'model_reasoning_effort="high"' in cmd
    assert 'approval_policy="never"' in cmd
    assert seen["stdin_text"] == "Return OK"

    transcript_path = next(transcript_dir.glob("codex_cli_*.json"))
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    assert transcript["schema"] == "libreevolve.codex_cli_transcript.v1"
    assert transcript["model"] == "gpt-5.5"
    assert transcript["sandbox"] == "workspace-write"
    assert transcript["final_message"] == "OK"
    assert transcript["raw_final_message"] is None
    assert transcript["auth_source"] == "codex_home"
    assert transcript["codex_home"]["configured"] is True


def test_codex_backend_extracts_configured_json_output_field(tmp_path, monkeypatch):
    seen = {}

    def fake_popen(cmd, *args, **kwargs):
        return _FakeCodexProcess(
            cmd,
            *args,
            output_text=json.dumps({"candidate": "PATCH"}),
            seen=seen,
            **kwargs,
        )

    monkeypatch.setattr("libreevolve.llm.codex_cli._resolve_codex_command", lambda: "codex")
    monkeypatch.setattr("libreevolve.llm.codex_cli.subprocess.Popen", fake_popen)

    backend = CodexCLIBackend(
        model="gpt-5.5",
        cwd=str(tmp_path),
        output_json_field="candidate",
    )

    assert backend.generate("Return JSON") == "PATCH"
    assert "--output-schema" in seen["cmd"]


def test_codex_backend_strips_openai_api_key_when_using_codex_home(tmp_path, monkeypatch):
    seen = {}

    def fake_popen(cmd, *args, **kwargs):
        return _FakeCodexProcess(cmd, *args, seen=seen, **kwargs)

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-secret")
    monkeypatch.setattr("libreevolve.llm.codex_cli._resolve_codex_command", lambda: "codex")
    monkeypatch.setattr("libreevolve.llm.codex_cli.subprocess.Popen", fake_popen)

    backend = CodexCLIBackend(
        model="gpt-5.5",
        codex_home=str(tmp_path / "auth-home"),
        cwd=str(tmp_path),
    )

    assert backend.generate("Return OK") == "OK"

    assert "OPENAI_API_KEY" not in seen["env"]
