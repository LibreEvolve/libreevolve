from __future__ import annotations

import subprocess
import tempfile
import shutil
import hashlib
import json
import os
import re
import signal
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from libreevolve.llm.provider_metadata import (
    copy_provider_response_metadata,
    safe_provider_response_metadata,
)
from libreevolve.llm.provider_retry import (
    provider_retry_failure,
    with_provider_retry_metadata,
)


_CODEX_JSON_MAX_EVENTS = 512
_CODEX_JSON_MAX_EVENT_CHARS = 100_000


class CodexCLIBackend:
    """Custom backend that delegates text generation to the local Codex CLI."""

    def __init__(
        self,
        model: str = "gpt-5.3-codex-spark",
        max_tokens: int = 4096,
        *,
        cwd: str = ".",
        sandbox: str = "read-only",
        timeout_sec: float = 300.0,
        reasoning_effort: str | None = None,
        transcript_dir: str | None = None,
        codex_home: str | None = None,
        auth_name: str | None = None,
        auth_homes: dict[str, object] | None = None,
        auth_registry_path: str | None = None,
        profile: str | None = None,
        approval_policy: str | None = None,
        ignore_user_config: bool = False,
        ignore_rules: bool = False,
        ephemeral: bool = False,
        output_json_field: str | None = None,
        enable_features: list[str] | str | None = None,
        disable_features: list[str] | str | None = None,
    ) -> None:
        auth = _resolve_codex_auth(
            codex_home=codex_home,
            auth_name=auth_name,
            auth_homes=auth_homes,
            auth_registry_path=auth_registry_path,
        )
        self._model = model
        self._max_tokens = max_tokens
        self._cwd = cwd
        self._sandbox = sandbox
        self._timeout_sec = timeout_sec
        self._reasoning_effort = reasoning_effort
        self._transcript_dir = transcript_dir
        self._codex_home = auth.home
        self._auth_name = auth.name
        self._auth_source = auth.source
        self._profile = profile
        self._approval_policy = approval_policy
        self._ignore_user_config = ignore_user_config
        self._ignore_rules = ignore_rules
        self._ephemeral = ephemeral
        self._output_json_field = output_json_field
        self._enable_features = tuple(_normalize_feature_list(enable_features))
        self._disable_features = tuple(_normalize_feature_list(disable_features))
        self._provider_response_metadata: dict = {}

    @property
    def name(self) -> str:
        return f"codex-cli/{self._model}"

    @property
    def provider_response_metadata(self) -> dict:
        return copy_provider_response_metadata(self._provider_response_metadata)

    def generate(self, prompt: str, **kwargs) -> str:
        return self._generate(prompt, cancel_event=None)

    def generate_cancellable(
        self, prompt: str, *, cancel_event: threading.Event, **kwargs,
    ) -> str:
        """Cooperatively stop the local CLI tree, not remote provider work."""
        return self._generate(prompt, cancel_event=cancel_event)

    def _generate(self, prompt: str, *, cancel_event: threading.Event | None) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be non-empty text")
        self._provider_response_metadata = {}
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("Codex local call cancelled before process launch")

        if self._output_json_field:
            prompt = (
                "This is a text-generation request. All necessary task information "
                "and source code are supplied below; there is no repository to inspect. "
                "Do not use tools, read files, run commands, or modify the workspace. "
                "Generate the requested text directly and return it in the JSON string "
                f"field {self._output_json_field!r} required by the output schema.\n\n"
                + prompt
            )

        cwd = Path(self._cwd).resolve()
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".txt",
            delete=False,
        ) as handle:
            output_path = Path(handle.name)
        schema_path: Path | None = None

        cmd = [
            _resolve_codex_command(),
            "exec",
            "--model",
            self._model,
            "--sandbox",
            self._sandbox,
            "--cd",
            str(cwd),
            "--skip-git-repo-check",
            "--output-last-message",
            str(output_path),
            "--color",
            "never",
            "--json",
        ]
        if self._ignore_user_config:
            cmd.append("--ignore-user-config")
        if self._ignore_rules:
            cmd.append("--ignore-rules")
        if self._ephemeral:
            cmd.append("--ephemeral")
        for feature in self._enable_features:
            cmd.extend(["--enable", _validate_feature_name(feature)])
        for feature in self._disable_features:
            cmd.extend(["--disable", _validate_feature_name(feature)])
        if self._profile:
            cmd.extend(["--profile", self._profile])
        if self._approval_policy:
            cmd.extend(["-c", f'approval_policy="{self._approval_policy}"'])
        if self._reasoning_effort:
            cmd.extend(["-c", f'model_reasoning_effort="{self._reasoning_effort}"'])
        if self._output_json_field:
            schema_path = _write_output_schema(self._output_json_field)
            cmd.extend(["--output-schema", str(schema_path)])
        cmd.append("-")
        env = os.environ.copy()
        if self._codex_home:
            env["CODEX_HOME"] = str(Path(self._codex_home).expanduser().resolve())
            env.pop("OPENAI_API_KEY", None)

        proc: subprocess.Popen[str] | None = None
        try:
            creationflags = 0
            if os.name == "nt":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(cwd),
                    env=env,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=creationflags,
                    start_new_session=os.name != "nt",
                )
            except Exception as exc:
                self._provider_response_metadata = _codex_attempt_metadata(
                    _codex_json_metadata(""),
                    failure=exc,
                )
                raise
            try:
                stdout, stderr = _communicate_cancellable(
                    proc, prompt, timeout_sec=self._timeout_sec, cancel_event=cancel_event,
                )
                returncode = proc.returncode
            except subprocess.TimeoutExpired as exc:
                _terminate_process_tree(proc)
                try:
                    stdout, stderr = proc.communicate(timeout=5.0)
                except subprocess.TimeoutExpired:
                    stdout = exc.stdout if isinstance(exc.stdout, str) else ""
                    stderr = exc.stderr if isinstance(exc.stderr, str) else ""
                completed = subprocess.CompletedProcess(
                    cmd,
                    returncode=proc.returncode if proc.returncode is not None else -9,
                    stdout=stdout or "",
                    stderr=stderr or "",
                )
                timeout_error = TimeoutError(
                    f"codex exec timed out after {self._timeout_sec:g} seconds"
                )
                self._provider_response_metadata = _codex_attempt_metadata(
                    _codex_json_metadata(_codex_text(stdout)),
                    failure=timeout_error,
                )
                try:
                    raw_output = output_path.read_text(encoding="utf-8")
                except OSError:
                    raw_output = ""
                _write_transcript(
                    self._transcript_dir,
                    cwd=cwd,
                    command=cmd,
                    prompt=prompt,
                    completed=completed,
                    final_message=raw_output,
                    raw_final_message=None,
                    model=self._model,
                    sandbox=self._sandbox,
                    timeout_sec=self._timeout_sec,
                    reasoning_effort=self._reasoning_effort,
                    codex_home=self._codex_home,
                    auth_name=self._auth_name,
                    auth_source=self._auth_source,
                    profile=self._profile,
                    approval_policy=self._approval_policy,
                    ignore_user_config=self._ignore_user_config,
                    ignore_rules=self._ignore_rules,
                    ephemeral=self._ephemeral,
                    output_json_field=self._output_json_field,
                    enable_features=list(self._enable_features),
                    disable_features=list(self._disable_features),
                )
                raise timeout_error from exc

            completed = subprocess.CompletedProcess(
                cmd,
                returncode=returncode,
                stdout=stdout or "",
                stderr=stderr or "",
            )
            self._provider_response_metadata = _codex_json_metadata(completed.stdout)
            try:
                raw_output = output_path.read_text(encoding="utf-8")
            except OSError:
                raw_output = ""
            output = raw_output
            output_error: Exception | None = None
            if completed.returncode == 0 and self._output_json_field:
                try:
                    output = _extract_json_field(raw_output, self._output_json_field)
                except Exception as exc:
                    output_error = exc
            _write_transcript(
                self._transcript_dir,
                cwd=cwd,
                command=cmd,
                prompt=prompt,
                completed=completed,
                final_message=output,
                raw_final_message=raw_output if raw_output != output else None,
                model=self._model,
                sandbox=self._sandbox,
                timeout_sec=self._timeout_sec,
                reasoning_effort=self._reasoning_effort,
                codex_home=self._codex_home,
                auth_name=self._auth_name,
                auth_source=self._auth_source,
                profile=self._profile,
                approval_policy=self._approval_policy,
                ignore_user_config=self._ignore_user_config,
                ignore_rules=self._ignore_rules,
                ephemeral=self._ephemeral,
                output_json_field=self._output_json_field,
                enable_features=list(self._enable_features),
                disable_features=list(self._disable_features),
            )
            if completed.returncode != 0:
                stderr = completed.stderr.strip() or completed.stdout.strip()
                failure = RuntimeError(
                    f"codex exec failed with exit code {completed.returncode}: "
                    f"{stderr[:2000]}"
                )
                self._provider_response_metadata = _codex_attempt_metadata(
                    self._provider_response_metadata,
                    failure=failure,
                )
                raise failure
            if output_error is not None:
                failure = RuntimeError(
                    f"codex exec returned invalid structured output: {output_error}"
                )
                self._provider_response_metadata = _codex_attempt_metadata(
                    self._provider_response_metadata,
                    failure=failure,
                )
                raise failure
            if not output.strip():
                failure = RuntimeError("codex exec returned an empty final message")
                self._provider_response_metadata = _codex_attempt_metadata(
                    self._provider_response_metadata,
                    failure=failure,
                )
                raise failure
            self._provider_response_metadata = _codex_attempt_metadata(
                self._provider_response_metadata,
            )
            return output
        finally:
            if proc is not None and proc.returncode is None:
                _terminate_process_tree(proc)
            try:
                output_path.unlink()
            except OSError:
                pass
            if schema_path is not None:
                try:
                    schema_path.unlink()
                except OSError:
                    pass


def _communicate_cancellable(
    proc: subprocess.Popen[str],
    prompt: str,
    *,
    timeout_sec: float,
    cancel_event: threading.Event | None,
) -> tuple[str, str]:
    if cancel_event is None:
        return proc.communicate(prompt, timeout=timeout_sec)
    deadline = time.monotonic() + timeout_sec
    pending_input: str | None = prompt
    while True:
        if cancel_event.is_set():
            # The caller's finally block owns process-tree termination.
            raise RuntimeError("Codex local call cancelled")
        try:
            return proc.communicate(
                pending_input, timeout=max(0.0, min(0.1, deadline - time.monotonic())),
            )
        except subprocess.TimeoutExpired:
            # communicate retains its buffered input/output across timeout
            # retries; resubmitting the prompt would fail or duplicate input.
            pending_input = None
            if time.monotonic() >= deadline:
                raise


def _resolve_codex_command() -> str:
    for name in ("codex.cmd", "codex.exe", "codex"):
        path = shutil.which(name)
        if path:
            return path
    ps1 = shutil.which("codex.ps1")
    if ps1:
        return ps1
    raise RuntimeError("Could not find codex CLI on PATH")


def _terminate_process_tree(proc: subprocess.Popen[str]) -> None:
    if proc.returncode is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return
    try:
        # Force-stop the whole local group before reaping its leader. A TERM
        # followed by wait/poll can reap the leader while a TERM-ignoring child
        # survives, and then signaling its old numeric group risks PID reuse.
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except OSError:
        proc.kill()
    proc.wait(timeout=5.0)


def _write_output_schema(field_name: str) -> Path:
    if _AUTH_NAME_RE.fullmatch(field_name) is None:
        raise ValueError("output_json_field must be a manifest-safe label")
    payload = {
        "type": "object",
        "additionalProperties": False,
        "required": [field_name],
        "properties": {
            field_name: {
                "type": "string",
                "description": "Complete generated text to return to LibreEvolve.",
            }
        },
    }
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".schema.json",
        delete=False,
    ) as handle:
        json.dump(payload, handle)
        return Path(handle.name)


def _extract_json_field(text: str, field_name: str) -> str:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("expected JSON object")
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"expected non-empty string field {field_name!r}")
    return value


def _codex_json_metadata(stdout: object) -> dict:
    """Extract bounded usage data from Codex's JSONL event stream.

    Codex reports cache and reasoning counters alongside the input/output
    counters, but the shared provider metadata usage schema only has the
    normalized input/output/total fields.  Keep the extra provider counters as
    bounded scalar diagnostics rather than inventing new usage fields.
    """
    metadata: dict[str, object] = {
        "usage": None,
        "provider_diagnostics": {
            "adapter_attempt_scope": "codex_cli_process",
            "provider_internal_retry_status": "unknown",
        },
    }
    if not isinstance(stdout, str):
        return metadata

    completed_metadata: dict[str, object] | None = None
    try:
        lines = stdout.splitlines()
    except Exception:
        return metadata
    for line in lines[-_CODEX_JSON_MAX_EVENTS:]:
        if len(line) > _CODEX_JSON_MAX_EVENT_CHARS:
            continue
        try:
            event = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(event, dict) or event.get("type") != "turn.completed":
            continue
        candidate = _codex_usage_metadata(event.get("usage"))
        if candidate is not None:
            if completed_metadata is None:
                completed_metadata = {
                    "usage": None,
                    "provider_diagnostics": {},
                }
            completed_metadata["usage"] = candidate.get("usage")
            completed_metadata["provider_diagnostics"].update(
                candidate.get("provider_diagnostics") or {}
            )
    if completed_metadata is not None:
        metadata["usage"] = completed_metadata["usage"]
        metadata["provider_diagnostics"].update(
            completed_metadata["provider_diagnostics"]
        )
    return safe_provider_response_metadata(metadata)


def _codex_usage_metadata(raw_usage: object) -> dict[str, object] | None:
    if not isinstance(raw_usage, dict):
        return None

    input_tokens = _safe_nonnegative_int(raw_usage.get("input_tokens"))
    output_tokens = _safe_nonnegative_int(raw_usage.get("output_tokens"))
    total_tokens = _safe_nonnegative_int(raw_usage.get("total_tokens"))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens

    usage: dict[str, int] = {}
    if input_tokens is not None:
        usage["input_tokens"] = input_tokens
    if output_tokens is not None:
        usage["output_tokens"] = output_tokens
    if total_tokens is not None:
        usage["total_tokens"] = total_tokens

    diagnostics: dict[str, int] = {}
    for field_name in (
        "cached_input_tokens",
        "cache_write_input_tokens",
        "reasoning_output_tokens",
    ):
        value = _safe_nonnegative_int(raw_usage.get(field_name))
        if value is not None:
            diagnostics[field_name] = value

    if not usage and not diagnostics:
        return None
    return {
        "usage": usage or None,
        "provider_diagnostics": diagnostics or None,
    }


def _codex_attempt_metadata(
    metadata: object,
    *,
    failure: BaseException | None = None,
) -> dict:
    try:
        normalized = safe_provider_response_metadata(metadata)
    except Exception:
        normalized = {"usage": None}
    failures = [provider_retry_failure(0, failure)] if failure is not None else []
    return with_provider_retry_metadata(
        normalized,
        max_retries=0,
        attempts=1,
        failures=failures,
    )


def _codex_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _safe_nonnegative_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _validate_feature_name(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_.-]{1,120}", value) is None:
        raise ValueError("Codex feature name must be a manifest-safe label")
    return value


def _normalize_feature_list(value: list[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return value.split()
    if isinstance(value, list):
        return value
    raise ValueError("Codex feature list must be a list or whitespace-separated string")


@dataclass(frozen=True)
class _ResolvedCodexAuth:
    home: str | None
    name: str | None
    source: str


_AUTH_NAME_RE = re.compile(r"[A-Za-z0-9_.-]{1,80}")


def _resolve_codex_auth(
    *,
    codex_home: str | None,
    auth_name: str | None,
    auth_homes: dict[str, object] | None,
    auth_registry_path: str | None,
) -> _ResolvedCodexAuth:
    if auth_name is not None:
        auth_name = _validate_auth_name(auth_name)

    if codex_home:
        return _ResolvedCodexAuth(
            home=_expand_path(codex_home),
            name=auth_name or "direct",
            source="codex_home",
        )

    if auth_name:
        mapped_home = _lookup_auth_home(auth_name, auth_homes, auth_registry_path)
        if mapped_home:
            return _ResolvedCodexAuth(
                home=_expand_path(mapped_home),
                name=auth_name,
                source="auth_name",
            )
        if auth_name in {"default", "current"}:
            return _ResolvedCodexAuth(
                home=_expand_path("~/.codex"),
                name=auth_name,
                source="default_codex_home",
            )
        raise ValueError(
            f"Unknown Codex auth_name {auth_name!r}; configure auth_homes, "
            "auth_registry_path, or LIBREEVOLVE_CODEX_AUTH_<NAME>_HOME"
        )

    mapped_current = _lookup_auth_home("current", auth_homes, auth_registry_path)
    if mapped_current:
        return _ResolvedCodexAuth(
            home=_expand_path(mapped_current),
            name="current",
            source="registry_current",
        )

    return _ResolvedCodexAuth(home=None, name=None, source="process_environment")


def _lookup_auth_home(
    auth_name: str,
    auth_homes: dict[str, object] | None,
    auth_registry_path: str | None,
) -> str | None:
    env_key = f"LIBREEVOLVE_CODEX_AUTH_{_env_auth_name(auth_name)}_HOME"
    if os.environ.get(env_key):
        return os.environ[env_key]

    home = _auth_home_from_mapping(auth_homes or {}, auth_name)
    if home:
        return home

    registry_path = Path(
        _expand_path(auth_registry_path or "~/.codex/libreevolve_auths.json")
    )
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse Codex auth registry {registry_path}: {exc}") from exc
    if not isinstance(registry, dict):
        raise ValueError(f"Codex auth registry {registry_path} must be a mapping")
    return _auth_home_from_registry(registry, auth_name, registry_path)


def _auth_home_from_mapping(mapping: object, auth_name: str) -> str | None:
    if not isinstance(mapping, dict):
        raise ValueError("Codex auth mapping must be a mapping")
    entry = mapping.get(auth_name)
    if entry is None:
        return None
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict) and isinstance(entry.get("home"), str):
        return entry["home"]
    raise ValueError(f"Codex auth entry {auth_name!r} must be a path string or mapping with home")


def _auth_home_from_registry(
    registry: dict[str, object],
    auth_name: str,
    registry_path: Path,
) -> str | None:
    auths = registry.get("auths", {})
    direct = _auth_home_from_mapping(auths, auth_name)
    if direct:
        return direct

    alias_target: object | None = None
    if auth_name == "current":
        alias_target = registry.get("current_auth")
    aliases = registry.get("aliases", {})
    if isinstance(aliases, dict) and auth_name in aliases:
        alias_target = aliases[auth_name]

    if alias_target is None:
        return None
    if not isinstance(alias_target, str):
        raise ValueError(
            f"Codex auth registry {registry_path} alias {auth_name!r} must point to an auth name"
        )
    alias_target = _validate_auth_name(alias_target)
    if alias_target == auth_name:
        raise ValueError(
            f"Codex auth registry {registry_path} alias {auth_name!r} points to itself"
        )
    mapped = _auth_home_from_mapping(auths, alias_target)
    if not mapped:
        raise ValueError(
            f"Codex auth registry {registry_path} alias {auth_name!r} points to "
            f"unknown auth {alias_target!r}"
        )
    return mapped


def _validate_auth_name(value: str) -> str:
    if _AUTH_NAME_RE.fullmatch(value) is None:
        raise ValueError("Codex auth_name must be a manifest-safe label")
    return value


def _env_auth_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "_", value).upper()


def _expand_path(path: str) -> str:
    return str(Path(os.path.expandvars(path)).expanduser().resolve())


def _write_transcript(
    transcript_dir: str | None,
    *,
    cwd: Path,
    command: list[str],
    prompt: str,
    completed: subprocess.CompletedProcess[str],
    final_message: str,
    model: str,
    sandbox: str,
    timeout_sec: float,
    reasoning_effort: str | None,
    codex_home: str | None,
    auth_name: str | None,
    auth_source: str,
    profile: str | None,
    approval_policy: str | None,
    ignore_user_config: bool,
    ignore_rules: bool,
    ephemeral: bool,
    output_json_field: str | None,
    raw_final_message: str | None,
    enable_features: list[str],
    disable_features: list[str],
) -> None:
    if not transcript_dir:
        return
    root = Path(transcript_dir)
    if not root.is_absolute():
        root = cwd / root
    root.mkdir(parents=True, exist_ok=True)
    now_ns = time.time_ns()
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    final_sha = hashlib.sha256(final_message.encode("utf-8")).hexdigest()
    path = root / f"codex_cli_{now_ns}_{prompt_sha[:12]}.json"
    payload = {
        "schema": "libreevolve.codex_cli_transcript.v1",
        "created_time_ns": now_ns,
        "backend": "codex-cli",
        "model": model,
        "sandbox": sandbox,
        "timeout_sec": timeout_sec,
        "reasoning_effort": reasoning_effort,
        "auth_name": auth_name,
        "auth_source": auth_source,
        "codex_home": _redacted_path(codex_home),
        "profile": profile,
        "approval_policy": approval_policy,
        "ignore_user_config": ignore_user_config,
        "ignore_rules": ignore_rules,
        "ephemeral": ephemeral,
        "output_json_field": output_json_field,
        "enable_features": enable_features,
        "disable_features": disable_features,
        "temperature": None,
        "temperature_note": "codex exec help exposes no temperature flag for this invocation",
        "cwd": str(cwd),
        "command": command,
        "returncode": completed.returncode,
        "prompt_sha256": prompt_sha,
        "final_message_sha256": final_sha,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
        "prompt": prompt,
        "final_message": final_message,
        "raw_final_message": raw_final_message,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _redacted_path(path: str | None) -> dict | None:
    if not path:
        return None
    text = str(Path(path).expanduser())
    return {
        "configured": True,
        "basename": Path(text).name,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
