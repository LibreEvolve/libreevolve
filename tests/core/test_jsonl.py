import collections
import builtins
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

import libreevolve.core.jsonl as jsonl_module
from libreevolve.core.jsonl import (
    StrictJsonlError,
    append_strict_jsonl,
    iter_quarantine_records,
    iter_strict_jsonl_objects,
    load_strict_json_object,
    repair_trailing_partial_jsonl,
    strict_json_dump,
    validate_quarantine_record,
)
from libreevolve.core.meta_prompt import PromptDatabase


def test_strict_json_dump_replaces_valid_payload_atomically(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text('{"old": true}', encoding="utf-8")

    strict_json_dump({"new": {"value": 1}}, path, indent=2)

    assert json.loads(path.read_text(encoding="utf-8")) == {"new": {"value": 1}}
    assert list(tmp_path.glob(".manifest.json.*.tmp")) == []


def test_load_strict_json_object_rejects_duplicate_names(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(
        '{"runtime":{"status":"completed","status":"failed"}}',
        encoding="utf-8",
    )

    with pytest.raises(StrictJsonlError, match="duplicate JSON object name 'status'"):
        load_strict_json_object(path, source="manifest.json")


def test_iter_strict_jsonl_objects_rejects_nested_duplicate_names_with_line(tmp_path):
    path = tmp_path / "failure_history.jsonl"
    path.write_text(
        '{"ok": true}\n{"metadata":{"reason":"a","reason":"b"}}\n',
        encoding="utf-8",
    )

    rows = iter_strict_jsonl_objects(path, stream_name="failure_history.jsonl")
    assert next(rows) == {"ok": True}
    with pytest.raises(
        StrictJsonlError,
        match=r"Malformed failure_history\.jsonl at line 2: duplicate JSON object name 'reason'",
    ):
        next(rows)


def test_iter_strict_jsonl_objects_rejects_unterminated_final_record(tmp_path):
    path = tmp_path / "history.jsonl"
    path.write_text('{"id": "complete-but-unterminated"}', encoding="utf-8")

    with pytest.raises(
        StrictJsonlError,
        match=r"Malformed history\.jsonl at line 1: unterminated final JSONL record",
    ):
        list(iter_strict_jsonl_objects(path, stream_name="history.jsonl"))


def test_iter_strict_jsonl_objects_can_repair_unterminated_final_record(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    path.write_bytes(b'{"id": "safe"}\n{"id": "complete-but-torn"}')

    records = list(
        iter_strict_jsonl_objects(
            path,
            stream_name="history.jsonl",
            repair_torn_final_record=True,
            quarantine_path=quarantine,
        )
    )

    assert records == [{"id": "safe"}]
    assert path.read_bytes() == b'{"id": "safe"}\n'
    [diagnostic] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert diagnostic["event"] == "jsonl_torn_final_record_repaired"
    assert diagnostic["stream"] == "history.jsonl"
    assert diagnostic["repair_policy"] == "truncate_unterminated_final_line"
    assert diagnostic["fragment_preview"] == '{"id": "complete-but-torn"}'
    assert validate_quarantine_record(diagnostic) == diagnostic


def test_strict_json_dump_best_effort_fsyncs_parent_directory(monkeypatch, tmp_path):
    path = tmp_path / "manifest.json"
    calls = []
    original_open = os.open
    original_fsync = os.fsync
    original_close = os.close
    fake_fd = 987654

    def fake_open(target, flags, *args, **kwargs):
        if Path(target) == tmp_path:
            calls.append(("open", target, flags))
            return fake_fd
        return original_open(target, flags, *args, **kwargs)

    def fake_fsync(fd):
        if fd == fake_fd:
            calls.append(("fsync", fd))
            return None
        return original_fsync(fd)

    def fake_close(fd):
        if fd == fake_fd:
            calls.append(("close", fd))
            return None
        return original_close(fd)

    monkeypatch.setattr(os, "open", fake_open)
    monkeypatch.setattr(os, "fsync", fake_fsync)
    monkeypatch.setattr(os, "close", fake_close)

    strict_json_dump({"ok": True}, path, indent=2)

    assert json.loads(path.read_text(encoding="utf-8")) == {"ok": True}
    assert calls == [
        ("open", tmp_path, os.O_RDONLY),
        ("fsync", fake_fd),
        ("close", fake_fd),
    ]


def test_strict_json_dump_creates_missing_parent_directory(tmp_path):
    path = tmp_path / "missing" / "manifest.json"

    strict_json_dump({"ok": True}, path)

    assert json.loads(path.read_text(encoding="utf-8")) == {"ok": True}


def test_strict_json_dump_reports_invalid_parent_as_strict_error(tmp_path):
    parent = tmp_path / "api_key=sk-proj_jsonl_parent_secret_123456"
    parent.write_text("not a directory", encoding="utf-8")
    path = parent / "manifest.json"

    with pytest.raises(StrictJsonlError) as raised:
        strict_json_dump({"ok": True}, path)

    message = str(raised.value)
    assert "Could not prepare parent directory for strict JSON file" in message
    assert "FileExistsError" in message
    assert "api_key=" not in message
    assert "sk-proj_" not in message
    assert "[REDACTED]" in message


def test_strict_json_dump_preserves_existing_file_on_non_serializable_payload(tmp_path):
    path = tmp_path / "manifest.json"
    original = '{"config": {"run_id": "abc"}}'
    path.write_text(original, encoding="utf-8")

    with pytest.raises(StrictJsonlError, match="Could not serialize strict JSON"):
        strict_json_dump({"runtime": {"bad": object()}}, path, indent=2)

    assert path.read_text(encoding="utf-8") == original
    assert json.loads(path.read_text(encoding="utf-8")) == {"config": {"run_id": "abc"}}
    assert list(tmp_path.glob(".manifest.json.*.tmp")) == []


def test_strict_json_dump_preserves_existing_file_on_non_finite_payload(tmp_path):
    path = tmp_path / "manifest.json"
    original = '{"config": {"run_id": "abc"}}'
    path.write_text(original, encoding="utf-8")

    with pytest.raises(StrictJsonlError, match=r"non-finite values: \$.runtime.elapsed"):
        strict_json_dump({"runtime": {"elapsed": math.inf}}, path, indent=2)

    assert path.read_text(encoding="utf-8") == original
    assert json.loads(path.read_text(encoding="utf-8")) == {"config": {"run_id": "abc"}}
    assert list(tmp_path.glob(".manifest.json.*.tmp")) == []


def test_strict_json_dump_rejects_non_string_object_keys_before_coercion(tmp_path):
    path = tmp_path / "manifest.json"
    original = '{"config": {"run_id": "abc"}}'
    path.write_text(original, encoding="utf-8")

    with pytest.raises(
        StrictJsonlError,
        match=r"JSON object key at \$.runtime.metrics must be a string: int 1",
    ):
        strict_json_dump({"runtime": {"metrics": {1: "numeric", "1": "string"}}}, path)

    assert path.read_text(encoding="utf-8") == original
    assert list(tmp_path.glob(".manifest.json.*.tmp")) == []


@pytest.mark.parametrize("bad_key", [True, None, 1.5])
def test_strict_json_dump_rejects_other_json_unsafe_object_keys(tmp_path, bad_key):
    path = tmp_path / "manifest.json"
    path.write_text('{"old": true}', encoding="utf-8")

    with pytest.raises(StrictJsonlError, match="JSON object key"):
        strict_json_dump({"runtime": {"metadata": {bad_key: "bad"}}}, path)

    assert json.loads(path.read_text(encoding="utf-8")) == {"old": True}


def test_append_strict_jsonl_quarantines_non_string_object_keys(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"

    with pytest.raises(StrictJsonlError, match="JSON object key"):
        append_strict_jsonl(
            path,
            {"metadata": {"metrics": {1: "numeric", "1": "string"}}},
            quarantine_path=quarantine,
        )

    assert not path.exists()
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert record["error"] == "TypeError"
    assert "JSON object key" in record["message"]
    assert record["record_repr_truncated"] is False
    assert validate_quarantine_record(record) == record
    assert list(iter_quarantine_records(quarantine)) == [record]


def test_append_strict_jsonl_creates_missing_parent_directory(tmp_path):
    path = tmp_path / "missing" / "history.jsonl"

    append_strict_jsonl(path, {"ok": True})

    assert [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] == [
        {"ok": True}
    ]


def test_append_strict_jsonl_fsyncs_written_line(monkeypatch, tmp_path):
    path = tmp_path / "history.jsonl"
    fsync_calls = 0
    original_fsync = os.fsync

    def fake_fsync(fd):
        nonlocal fsync_calls
        fsync_calls += 1
        return original_fsync(fd)

    monkeypatch.setattr(os, "fsync", fake_fsync)

    append_strict_jsonl(path, {"ok": True})

    assert fsync_calls >= 1
    assert path.read_text(encoding="utf-8") == '{"ok": true}\n'


def test_append_strict_jsonl_serializes_concurrent_process_writers(tmp_path):
    path = tmp_path / "history.jsonl"
    repo_root = Path(__file__).resolve().parents[2]
    script = (
        "from pathlib import Path\n"
        "import sys\n"
        "from libreevolve.core.jsonl import append_strict_jsonl\n"
        "path = Path(sys.argv[1])\n"
        "writer = sys.argv[2]\n"
        "for index in range(20):\n"
        "    append_strict_jsonl(path, {'writer': writer, 'index': index})\n"
    )
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", script, str(path), f"writer-{index}"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for index in range(4)
    ]

    failures = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=30)
        if process.returncode != 0:
            failures.append((process.returncode, stdout, stderr))
    assert failures == []
    rows = list(iter_strict_jsonl_objects(path, stream_name="history.jsonl"))
    assert len(rows) == 80
    counts = collections.Counter(row["writer"] for row in rows)
    assert counts == {
        "writer-0": 20,
        "writer-1": 20,
        "writer-2": 20,
        "writer-3": 20,
    }
    assert path.read_bytes().endswith(b"\n")
    assert (tmp_path / ".history.jsonl.lock").exists()


def test_append_strict_jsonl_repairs_torn_final_line_before_append(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    path.write_bytes(b'{"id": "first", "fitness": 1.0}\n{"id":')

    append_strict_jsonl(
        path,
        {"id": "after", "fitness": 2.0},
        quarantine_path=quarantine,
    )

    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    assert records == [
        {"id": "first", "fitness": 1.0},
        {"id": "after", "fitness": 2.0},
    ]
    [diagnostic] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert diagnostic["event"] == "jsonl_torn_final_record_repaired"
    assert diagnostic["stream"] == "history.jsonl"
    assert diagnostic["repair_policy"] == "truncate_unterminated_final_line"
    assert diagnostic["complete_bytes_preserved"] == len(
        b'{"id": "first", "fitness": 1.0}\n'
    )
    assert diagnostic["fragment_bytes"] == len(b'{"id":')
    assert diagnostic["fragment_utf8_valid"] is True
    assert diagnostic["fragment_preview"] == '{"id":'
    assert validate_quarantine_record(diagnostic) == diagnostic


def test_repair_trailing_partial_jsonl_can_self_quarantine(tmp_path):
    path = tmp_path / "prompt_history_invalid.jsonl"
    path.write_bytes(b'{"old": true}\n{"event":')

    result = repair_trailing_partial_jsonl(path)

    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    assert result["status"] == "repaired"
    assert records[0] == {"old": True}
    assert records[1]["event"] == "jsonl_torn_final_record_repaired"
    assert records[1]["stream"] == "prompt_history_invalid.jsonl"
    assert validate_quarantine_record(records[1]) == records[1]


def test_validate_quarantine_record_rejects_unknown_shape():
    with pytest.raises(StrictJsonlError, match="unsupported quarantine event"):
        validate_quarantine_record({"event": "unexpected"})


def test_validate_quarantine_record_rejects_missing_serializer_fields():
    with pytest.raises(
        StrictJsonlError,
        match="record_repr_retention must be an object",
    ):
        validate_quarantine_record(
            {
                "error": "TypeError",
                "message": "bad",
                "record_type": "dict",
            }
        )


def test_validate_quarantine_record_rejects_hash_only_snapshot_text(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"

    with pytest.raises(StrictJsonlError):
        append_strict_jsonl(
            path,
            {"metadata": {"bad": object()}},
            quarantine_path=quarantine,
            quarantine_snapshot_retention_mode="hash_only",
        )

    [record] = list(iter_quarantine_records(quarantine))
    forged = dict(record)
    forged["record_repr"] = "{'metadata': {'bad': <object object>}}"

    with pytest.raises(StrictJsonlError, match="record_repr is not allowed"):
        validate_quarantine_record(forged)


def test_validate_quarantine_record_rejects_off_fragment_snapshot(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    path.write_bytes(b'{"ok": true}\n{"id":')

    repair_trailing_partial_jsonl(
        path,
        quarantine_path=quarantine,
        quarantine_snapshot_retention_mode="off",
    )

    [record] = list(iter_quarantine_records(quarantine))
    forged = dict(record)
    forged["fragment_preview"] = '{"id":'

    with pytest.raises(StrictJsonlError, match="fragment_preview is not allowed"):
        validate_quarantine_record(forged)


def test_append_strict_jsonl_creates_missing_quarantine_parent_directory(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "missing" / "history_invalid.jsonl"

    with pytest.raises(StrictJsonlError, match="JSON object key"):
        append_strict_jsonl(
            path,
            {"metadata": {1: "numeric"}},
            quarantine_path=quarantine,
        )

    assert not path.exists()
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert record["error"] == "TypeError"
    assert "JSON object key" in record["message"]


def test_append_strict_jsonl_reports_invalid_parent_as_strict_error(tmp_path):
    parent = tmp_path / "api_key=sk-proj_jsonl_append_parent_secret_123456"
    parent.write_text("not a directory", encoding="utf-8")
    path = parent / "history.jsonl"

    with pytest.raises(StrictJsonlError) as raised:
        append_strict_jsonl(path, {"ok": True})

    message = str(raised.value)
    assert "Could not prepare parent directory for strict JSONL file" in message
    assert "FileExistsError" in message
    assert "api_key=" not in message
    assert "sk-proj_" not in message
    assert "[REDACTED]" in message


def test_strict_json_dump_rejects_cyclic_payload_with_strict_error(tmp_path):
    path = tmp_path / "manifest.json"
    original = '{"old": true}'
    path.write_text(original, encoding="utf-8")
    cyclic = {"runtime": {}}
    cyclic["runtime"]["self"] = cyclic

    with pytest.raises(StrictJsonlError, match=r"Circular reference detected"):
        strict_json_dump(cyclic, path)

    assert path.read_text(encoding="utf-8") == original
    assert list(tmp_path.glob(".manifest.json.*.tmp")) == []


def test_append_strict_jsonl_quarantines_cyclic_payload(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    cyclic = {"metadata": {}}
    cyclic["metadata"]["self"] = cyclic

    with pytest.raises(StrictJsonlError, match=r"Circular reference detected"):
        append_strict_jsonl(path, cyclic, quarantine_path=quarantine)

    assert not path.exists()
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert record["error"] == "ValueError"
    assert "Circular reference detected" in record["message"]


def test_append_strict_jsonl_quarantines_excessively_deep_payload(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    payload = "leaf"
    for _ in range(105):
        payload = [payload]

    with pytest.raises(StrictJsonlError, match="JSON nesting exceeds maximum depth"):
        append_strict_jsonl(path, {"metadata": payload}, quarantine_path=quarantine)

    assert not path.exists()
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert record["error"] == "ValueError"
    assert "JSON nesting exceeds maximum depth" in record["message"]


def test_append_quarantine_record_survives_unsafe_record_repr(tmp_path):
    class BadRepr:
        def __repr__(self):
            raise RuntimeError("repr boom")

    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"

    with pytest.raises(StrictJsonlError, match="not JSON serializable"):
        append_strict_jsonl(
            path,
            {"metadata": {"bad": BadRepr()}},
            quarantine_path=quarantine,
        )

    assert not path.exists()
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert record["error"] == "TypeError"
    assert record["record_repr"] == "<repr failed>"
    assert "RuntimeError" in record["record_repr_error"]


def test_append_quarantine_record_bounds_and_redacts_record_repr(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    secret = "api_key=sk-proj_abcdefghijklmnopqrstuvwxyz123456"
    record_payload = secret + " " + ("x" * 5000)

    with pytest.raises(StrictJsonlError, match="not JSON serializable"):
        append_strict_jsonl(
            path,
            {"metadata": {"payload": record_payload, "bad": object()}},
            quarantine_path=quarantine,
        )

    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert "[REDACTED]" in record["record_repr"]
    assert "sk-proj_" not in record["record_repr"]
    assert record["record_repr_truncated"] is True
    assert len(record["record_repr"]) <= 4000


def test_append_quarantine_record_supports_hash_only_record_repr_retention(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    secret = "api_key=sk-proj_quarantine_hash_only_secret_123456"
    payload = {"metadata": {"payload": secret, "bad": object()}}
    expected_repr_hash = hashlib.sha256(
        repr(payload).encode("utf-8", errors="replace")
    ).hexdigest()

    with pytest.raises(StrictJsonlError, match="not JSON serializable"):
        append_strict_jsonl(
            path,
            payload,
            quarantine_path=quarantine,
            quarantine_snapshot_retention_mode="hash_only",
        )

    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert "record_repr" not in record
    assert "record_repr_truncated" not in record
    retention = record["record_repr_retention"]
    assert retention["retention_mode"] == "hash_only"
    assert retention["sha256"] == expected_repr_hash
    assert retention["chars"] == len(repr(payload))
    assert "sk-proj_" not in json.dumps(record)


def test_append_quarantine_record_supports_off_record_repr_retention(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    secret = "api_key=sk-proj_quarantine_off_secret_123456"

    with pytest.raises(StrictJsonlError, match="not JSON serializable"):
        append_strict_jsonl(
            path,
            {"metadata": {"payload": secret, "bad": object()}},
            quarantine_path=quarantine,
            quarantine_snapshot_retention_mode="off",
        )

    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert "record_repr" not in record
    assert "record_repr_truncated" not in record
    retention = record["record_repr_retention"]
    assert retention["retention_mode"] == "off"
    assert retention["sha256"] is None
    assert retention["chars"] is None
    assert "sk-proj_" not in json.dumps(record)


def test_repair_trailing_partial_jsonl_honors_off_snapshot_retention(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    path.write_bytes(b'{"ok": true}\n{"api_key":"sk-proj_torn_secret_123456"')

    repair_trailing_partial_jsonl(
        path,
        quarantine_path=quarantine,
        quarantine_snapshot_retention_mode="off",
    )

    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert "fragment_preview" not in record
    assert "fragment_sha256" not in record
    assert record["fragment_retention"]["retention_mode"] == "off"
    assert "sk-proj_" not in json.dumps(record)


def test_strict_json_diagnostic_messages_redact_secret_key_repr(tmp_path):
    class SecretKey:
        def __repr__(self):
            return "api_key=sk-proj_jsonl_key_secret_1234567890"

    path = tmp_path / "manifest.json"
    path.write_text('{"old": true}', encoding="utf-8")
    key = SecretKey()

    with pytest.raises(StrictJsonlError) as raised:
        strict_json_dump({"metadata": {key: "value"}}, path)

    message = str(raised.value)
    assert "JSON object key" in message
    assert "api_key=" not in message
    assert "sk-proj_" not in message
    assert "[REDACTED]" in message
    assert path.read_text(encoding="utf-8") == '{"old": true}'


def test_quarantine_message_redacts_secret_key_repr(tmp_path):
    class SecretKey:
        def __repr__(self):
            return "api_key=sk-proj_quarantine_key_secret_1234567890"

    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    key = SecretKey()

    with pytest.raises(StrictJsonlError) as raised:
        append_strict_jsonl(
            path,
            {"metadata": {key: "value"}},
            quarantine_path=quarantine,
        )

    assert "sk-proj_" not in str(raised.value)
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert record["error"] == "TypeError"
    assert "JSON object key" in record["message"]
    assert "api_key=" not in record["message"]
    assert "sk-proj_" not in record["message"]
    assert "[REDACTED]" in record["message"]
    assert "sk-proj_" not in record["record_repr"]
    assert not path.exists()


def test_strict_json_diagnostic_messages_are_bounded(tmp_path):
    class LongKey:
        def __repr__(self):
            return "prefix " + ("x" * 5000)

    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"

    with pytest.raises(StrictJsonlError) as raised:
        append_strict_jsonl(
            path,
            {"metadata": {LongKey(): "value"}},
            quarantine_path=quarantine,
        )

    message = str(raised.value)
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert len(message) <= 1100
    assert len(record["message"]) <= 1000
    assert record["message"].endswith("...<truncated>")


def test_strict_json_dump_rejects_tuple_values_before_array_coercion(tmp_path):
    path = tmp_path / "manifest.json"
    original = '{"old": true}'
    path.write_text(original, encoding="utf-8")

    with pytest.raises(StrictJsonlError, match=r"JSON value at \$.metadata.lineage_tuple must use list, not tuple"):
        strict_json_dump(
            {"metadata": {"lineage_tuple": ("parent", 1, None)}},
            path,
            indent=2,
        )

    assert path.read_text(encoding="utf-8") == original
    assert list(tmp_path.glob(".manifest.json.*.tmp")) == []


def test_append_strict_jsonl_quarantines_tuple_values_without_array_coercion(tmp_path):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"

    with pytest.raises(StrictJsonlError, match=r"JSON value at \$.metadata.lineage_tuple must use list, not tuple"):
        append_strict_jsonl(
            path,
            {"metadata": {"lineage_tuple": ("parent", 1, None)}},
            quarantine_path=quarantine,
        )

    assert not path.exists()
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert record["error"] == "TypeError"
    assert "must use list, not tuple" in record["message"]
    assert "lineage_tuple" in record["record_repr"]


def test_prompt_history_quarantines_tuple_metadata_without_state_mutation(tmp_path):
    db = PromptDatabase(tmp_path, templates=["a {task}"])
    parent = db.select()
    parent.metadata = {"lineage_tuple": ("parent", 1, None)}

    with pytest.raises(StrictJsonlError, match=r"must use list, not tuple"):
        db._write("corrupt", parent)

    assert len(db.all()) == 1
    quarantine = tmp_path / "prompt_history_invalid.jsonl"
    [record] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert record["error"] == "TypeError"
    assert "must use list, not tuple" in record["message"]


def test_strict_json_dump_replace_failure_preserves_exact_prior_bytes(tmp_path, monkeypatch):
    path = tmp_path / "manifest.json"
    prior_bytes = b'{"prior": true}\r\nprior trailing bytes\x00\n'
    path.write_bytes(prior_bytes)
    replace_calls = []

    def fail_replace(source, destination):
        replace_calls.append((Path(source), Path(destination)))
        raise OSError("replace injected")

    monkeypatch.setattr(jsonl_module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace injected"):
        strict_json_dump({"new": True}, path)

    assert path.read_bytes() == prior_bytes
    assert len(replace_calls) == 1
    assert replace_calls[0][1] == path
    assert replace_calls[0][0].parent == path.parent
    assert replace_calls[0][0].name.startswith(f".{path.name}.")
    assert replace_calls[0][0].name.endswith(".tmp")
    assert list(tmp_path.glob(f".{path.name}.*.tmp")) == []


def test_strict_json_dump_temp_fsync_failure_preserves_exact_prior_bytes(
    tmp_path, monkeypatch
):
    path = tmp_path / "manifest.json"
    prior_bytes = b"prior manifest bytes\r\n"
    path.write_bytes(prior_bytes)
    fsync_calls = []

    def fail_fsync(fd):
        fsync_calls.append(fd)
        raise OSError("temporary-file fsync injected")

    monkeypatch.setattr(jsonl_module.os, "fsync", fail_fsync)

    with pytest.raises(OSError, match="temporary-file fsync injected"):
        strict_json_dump({"new": True}, path)

    assert len(fsync_calls) == 1
    assert path.read_bytes() == prior_bytes
    assert list(tmp_path.glob(f".{path.name}.*.tmp")) == []


def test_strict_json_dump_parent_directory_fsync_failure_is_best_effort(
    tmp_path, monkeypatch
):
    path = tmp_path / "manifest.json"
    fake_directory_fd = 246801
    calls = []
    original_open = os.open
    original_fsync = os.fsync
    original_close = os.close

    def fake_open(target, flags, *args, **kwargs):
        if Path(target) == tmp_path:
            calls.append(("open", Path(target), flags))
            return fake_directory_fd
        return original_open(target, flags, *args, **kwargs)

    def fake_fsync(fd):
        if fd == fake_directory_fd:
            calls.append(("fsync", fd))
            raise OSError("parent-directory fsync injected")
        return original_fsync(fd)

    def fake_close(fd):
        if fd == fake_directory_fd:
            calls.append(("close", fd))
            return None
        return original_close(fd)

    monkeypatch.setattr(jsonl_module.os, "open", fake_open)
    monkeypatch.setattr(jsonl_module.os, "fsync", fake_fsync)
    monkeypatch.setattr(jsonl_module.os, "close", fake_close)

    strict_json_dump({"new": True}, path)

    assert json.loads(path.read_text(encoding="utf-8")) == {"new": True}
    assert calls == [
        ("open", tmp_path, os.O_RDONLY),
        ("fsync", fake_directory_fd),
        ("close", fake_directory_fd),
    ]


class _WrappedJsonlFile:
    def __init__(
        self,
        handle,
        *,
        fail_write=False,
        fail_flush=False,
        fail_truncate=False,
        partial_write_chars=None,
    ):
        self._handle = handle
        self._fail_write = fail_write
        self._fail_flush = fail_flush
        self._fail_truncate = fail_truncate
        self._partial_write_chars = partial_write_chars

    def __enter__(self):
        self._handle.__enter__()
        return self

    def __exit__(self, *args):
        return self._handle.__exit__(*args)

    def write(self, data):
        if self._fail_write:
            raise OSError("append write injected")
        if self._partial_write_chars is not None:
            self._handle.write(data[: self._partial_write_chars])
            raise OSError("append partial write injected")
        return self._handle.write(data)

    def flush(self):
        if self._fail_flush:
            self._handle.flush()
            raise OSError("append flush injected")
        return self._handle.flush()

    def truncate(self, *args):
        if self._fail_truncate:
            raise OSError("repair truncate injected")
        return self._handle.truncate(*args)

    def __getattr__(self, name):
        return getattr(self._handle, name)


def _seed_jsonl_lock(path):
    path.with_name(f".{path.name}.lock").write_bytes(b"\0")


def test_append_strict_jsonl_write_failure_preserves_exact_prior_bytes(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    prior_bytes = b'{"prior": true}\r\n'
    path.write_bytes(prior_bytes)
    _seed_jsonl_lock(path)
    original_open = builtins.open

    def failing_open(target, mode="r", *args, **kwargs):
        handle = original_open(target, mode, *args, **kwargs)
        if Path(target) == path and mode == "a":
            return _WrappedJsonlFile(handle, fail_write=True)
        return handle

    monkeypatch.setattr(jsonl_module, "open", failing_open, raising=False)

    with pytest.raises(OSError, match="append write injected"):
        append_strict_jsonl(path, {"new": True})

    assert path.read_bytes() == prior_bytes


def test_append_strict_jsonl_flush_failure_preserves_prefix_and_records_written_line(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    prior_bytes = b'{"prior": true}\n'
    path.write_bytes(prior_bytes)
    _seed_jsonl_lock(path)
    original_open = builtins.open

    def failing_open(target, mode="r", *args, **kwargs):
        handle = original_open(target, mode, *args, **kwargs)
        if Path(target) == path and mode == "a":
            return _WrappedJsonlFile(handle, fail_flush=True)
        return handle

    monkeypatch.setattr(jsonl_module, "open", failing_open, raising=False)

    with pytest.raises(OSError, match="append flush injected"):
        append_strict_jsonl(path, {"new": True})

    assert path.read_bytes() == prior_bytes + b'{"new": true}' + os.linesep.encode()


def test_append_strict_jsonl_fsync_failure_preserves_prefix_and_records_written_line(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    prior_bytes = b'{"prior": true}\n'
    path.write_bytes(prior_bytes)
    _seed_jsonl_lock(path)
    fsync_calls = []

    def fail_fsync(fd):
        fsync_calls.append(fd)
        raise OSError("append fsync injected")

    monkeypatch.setattr(jsonl_module.os, "fsync", fail_fsync)

    with pytest.raises(OSError, match="append fsync injected"):
        append_strict_jsonl(path, {"new": True})

    assert len(fsync_calls) == 1
    assert path.read_bytes() == prior_bytes + b'{"new": true}' + os.linesep.encode()


def test_append_strict_jsonl_lock_acquire_failure_preserves_exact_prior_bytes(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    prior_bytes = b'{"prior": true}\n'
    path.write_bytes(prior_bytes)
    lock_calls = []

    def fail_acquire(handle, lock_path):
        lock_calls.append(Path(lock_path))
        raise StrictJsonlError("lock acquire injected")

    monkeypatch.setattr(jsonl_module, "_acquire_jsonl_file_lock", fail_acquire)

    with pytest.raises(StrictJsonlError, match="lock acquire injected"):
        append_strict_jsonl(path, {"new": True})

    assert lock_calls == [path.with_name(f".{path.name}.lock")]
    assert path.read_bytes() == prior_bytes


def test_append_strict_jsonl_lock_release_failure_is_reported_after_append(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    prior_bytes = b'{"prior": true}\n'
    path.write_bytes(prior_bytes)
    _seed_jsonl_lock(path)
    release_calls = []

    def fail_release(handle, lock_path):
        release_calls.append(Path(lock_path))
        raise StrictJsonlError("lock release injected")

    monkeypatch.setattr(jsonl_module, "_release_jsonl_file_lock", fail_release)

    with pytest.raises(StrictJsonlError, match="lock release injected"):
        append_strict_jsonl(path, {"new": True})

    assert release_calls == [path.with_name(f".{path.name}.lock")]
    assert path.read_bytes() == prior_bytes + b'{"new": true}' + os.linesep.encode()


def test_append_repairs_before_quarantine_and_accepted_append_under_ordered_locks(
    tmp_path, monkeypatch
):
    accepted = tmp_path / "z_history.jsonl"
    quarantine = tmp_path / "a_history_invalid.jsonl"
    complete_prefix = b'{"prior": true}\n'
    accepted.write_bytes(complete_prefix + b'{"torn":')
    quarantine_prior = b'{"previous": true}\n'
    quarantine.write_bytes(quarantine_prior)
    events = []
    original_repair = jsonl_module.repair_trailing_partial_jsonl
    original_append = jsonl_module._append_serialized_jsonl_line

    def trace_acquire(handle, lock_path):
        events.append(("acquire", Path(lock_path).name))

    def trace_release(handle, lock_path):
        events.append(("release", Path(lock_path).name))

    def trace_repair(path, *args, **kwargs):
        events.append(("repair", Path(path).name))
        return original_repair(path, *args, **kwargs)

    def trace_append(path, line):
        events.append(("append", Path(path).name))
        return original_append(path, line)

    monkeypatch.setattr(jsonl_module, "_acquire_jsonl_file_lock", trace_acquire)
    monkeypatch.setattr(jsonl_module, "_release_jsonl_file_lock", trace_release)
    monkeypatch.setattr(jsonl_module, "repair_trailing_partial_jsonl", trace_repair)
    monkeypatch.setattr(jsonl_module, "_append_serialized_jsonl_line", trace_append)

    append_strict_jsonl(
        accepted,
        {"after": True},
        quarantine_path=quarantine,
    )

    accepted_lock = f".{accepted.name}.lock"
    quarantine_lock = f".{quarantine.name}.lock"
    assert events == [
        ("acquire", quarantine_lock),
        ("acquire", accepted_lock),
        ("repair", accepted.name),
        ("append", quarantine.name),
        ("append", accepted.name),
        ("release", accepted_lock),
        ("release", quarantine_lock),
    ]
    assert accepted.read_bytes() == (
        complete_prefix + b'{"after": true}' + os.linesep.encode()
    )
    assert quarantine.read_bytes().startswith(quarantine_prior)
    [previous, diagnostic] = [
        json.loads(line)
        for line in quarantine.read_text(encoding="utf-8").splitlines()
    ]
    assert previous == {"previous": True}
    assert diagnostic["event"] == "jsonl_torn_final_record_repaired"


def test_repair_truncate_failure_preserves_exact_prior_bytes_and_skips_quarantine(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    prior_bytes = b'{"prior": true}\n{"torn":'
    path.write_bytes(prior_bytes)
    original_path_open = jsonl_module.Path.open

    def failing_path_open(target, mode="r", *args, **kwargs):
        handle = original_path_open(target, mode, *args, **kwargs)
        if Path(target) == path and mode == "r+b":
            return _WrappedJsonlFile(handle, fail_truncate=True)
        return handle

    monkeypatch.setattr(jsonl_module.Path, "open", failing_path_open)

    with pytest.raises(OSError, match="repair truncate injected"):
        repair_trailing_partial_jsonl(path, quarantine_path=quarantine)

    assert path.read_bytes() == prior_bytes
    assert not quarantine.exists()


def test_repair_fsync_failure_leaves_only_complete_prefix_without_quarantine(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    complete_prefix = b'{"prior": true}\n'
    path.write_bytes(complete_prefix + b'{"torn":')
    _seed_jsonl_lock(path)
    _seed_jsonl_lock(quarantine)

    def fail_fsync(fd):
        raise OSError("repair fsync injected")

    monkeypatch.setattr(jsonl_module.os, "fsync", fail_fsync)

    with pytest.raises(OSError, match="repair fsync injected"):
        repair_trailing_partial_jsonl(path, quarantine_path=quarantine)

    assert path.read_bytes() == complete_prefix
    assert not quarantine.exists()


def test_iter_strict_jsonl_objects_rejects_invalid_utf8_with_line_and_preserves_bytes(
    tmp_path,
):
    path = tmp_path / "history.jsonl"
    prior_bytes = b'{"ok": true}\n{"bad":"\xff"}\n'
    path.write_bytes(prior_bytes)

    with pytest.raises(
        StrictJsonlError,
        match=r"Malformed history\.jsonl at line 2: invalid UTF-8",
    ):
        list(iter_strict_jsonl_objects(path, stream_name="history.jsonl"))

    assert path.read_bytes() == prior_bytes


def test_repair_invalid_utf8_fragment_preserves_prefix_and_records_hex_diagnostic(
    tmp_path,
):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    complete_prefix = b'{"ok": true}\n'
    fragment = b'{"payload":\xff\xfe'
    path.write_bytes(complete_prefix + fragment)

    result = repair_trailing_partial_jsonl(path, quarantine_path=quarantine)

    assert result["status"] == "repaired"
    assert path.read_bytes() == complete_prefix
    [diagnostic] = list(iter_quarantine_records(quarantine))
    assert diagnostic["fragment_utf8_valid"] is False
    assert diagnostic["fragment_bytes"] == len(fragment)
    assert diagnostic["fragment_preview"] == fragment.hex()
    assert diagnostic["fragment_sha256"] == hashlib.sha256(fragment).hexdigest()
    assert diagnostic["complete_bytes_preserved"] == len(complete_prefix)
    assert validate_quarantine_record(diagnostic) == diagnostic


@pytest.mark.parametrize(
    ("repr_length", "truncated"),
    [(4000, False), (4001, True)],
)
def test_quarantine_record_repr_retention_boundary_is_explicit(
    tmp_path, repr_length, truncated
):
    class FixedRepr:
        def __repr__(self):
            return "x" * repr_length

    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"

    with pytest.raises(StrictJsonlError, match="not JSON serializable"):
        append_strict_jsonl(path, FixedRepr(), quarantine_path=quarantine)

    [record] = list(iter_quarantine_records(quarantine))
    assert record["record_repr_retention"]["max_chars"] == 4000
    assert record["record_repr_retention"]["chars"] == repr_length
    assert record["record_repr_truncated"] is truncated
    if truncated:
        assert record["record_repr"].endswith("...<truncated>")
        assert len(record["record_repr"]) <= 4000
    else:
        assert record["record_repr"] == "x" * repr_length
        assert record["record_repr_retention"]["stored_chars"] == repr_length


def test_quarantine_full_retention_keeps_text_beyond_redacted_boundary(tmp_path):
    class FixedRepr:
        def __repr__(self):
            return "x" * 4001

    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"

    with pytest.raises(StrictJsonlError, match="not JSON serializable"):
        append_strict_jsonl(
            path,
            FixedRepr(),
            quarantine_path=quarantine,
            quarantine_snapshot_retention_mode="full",
        )

    [record] = list(iter_quarantine_records(quarantine))
    assert record["record_repr"] == "x" * 4001
    assert record["record_repr_retention"] == {
        "retention_mode": "full",
        "retention_policy": "full_secret_redacted_text_with_raw_sha256",
        "sha256": hashlib.sha256(("x" * 4001).encode()).hexdigest(),
        "chars": 4001,
        "stored_chars": 4001,
        "max_chars": 4000,
        "redacted": False,
        "truncated": False,
    }


@pytest.mark.parametrize(
    ("fragment_length", "truncated"),
    [(500, False), (501, True)],
)
def test_repair_fragment_retention_boundary_is_explicit(
    tmp_path, fragment_length, truncated
):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    complete_prefix = b'{"ok": true}\n'
    fragment = b"x" * fragment_length
    path.write_bytes(complete_prefix + fragment)

    repair_trailing_partial_jsonl(path, quarantine_path=quarantine)

    [diagnostic] = list(iter_quarantine_records(quarantine))
    retention = diagnostic["fragment_retention"]
    assert retention["max_chars"] == 500
    assert retention["chars"] == fragment_length
    assert retention["truncated"] is truncated
    assert diagnostic["fragment_utf8_valid"] is True
    if truncated:
        assert diagnostic["fragment_preview"].endswith("...<truncated>")
        assert len(diagnostic["fragment_preview"]) <= 500
    else:
        assert diagnostic["fragment_preview"] == "x" * fragment_length
        assert retention["stored_chars"] == fragment_length


def test_append_strict_jsonl_quarantine_append_failure_after_repair_preserves_repair(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    complete_prefix = b'{"prior": true}\n'
    quarantine_prior = b'{"previous": true}\n'
    path.write_bytes(complete_prefix + b'{"torn":')
    quarantine.write_bytes(quarantine_prior)
    original_open = builtins.open
    failed_targets = []

    def failing_open(target, mode="r", *args, **kwargs):
        handle = original_open(target, mode, *args, **kwargs)
        if Path(target) == quarantine and mode == "a":
            failed_targets.append(Path(target))
            return _WrappedJsonlFile(handle, fail_write=True)
        return handle

    monkeypatch.setattr(jsonl_module, "open", failing_open, raising=False)

    with pytest.raises(OSError, match="append write injected"):
        append_strict_jsonl(
            path,
            {"after": True},
            quarantine_path=quarantine,
        )

    assert failed_targets == [quarantine]
    assert path.read_bytes() == complete_prefix
    assert quarantine.read_bytes() == quarantine_prior


def test_append_strict_jsonl_accepted_append_failure_after_repair_preserves_diagnostic(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    quarantine = tmp_path / "history_invalid.jsonl"
    complete_prefix = b'{"prior": true}\n'
    path.write_bytes(complete_prefix + b'{"torn":')
    original_open = builtins.open
    failed_targets = []

    def failing_open(target, mode="r", *args, **kwargs):
        handle = original_open(target, mode, *args, **kwargs)
        if Path(target) == path and mode == "a":
            failed_targets.append(Path(target))
            return _WrappedJsonlFile(handle, fail_write=True)
        return handle

    monkeypatch.setattr(jsonl_module, "open", failing_open, raising=False)

    with pytest.raises(OSError, match="append write injected"):
        append_strict_jsonl(
            path,
            {"after": True},
            quarantine_path=quarantine,
        )

    assert failed_targets == [path]
    assert path.read_bytes() == complete_prefix
    [diagnostic] = list(iter_quarantine_records(quarantine))
    assert diagnostic["event"] == "jsonl_torn_final_record_repaired"
    assert diagnostic["fragment_preview"] == '{"torn":'


def test_append_strict_jsonl_body_and_release_failure_prioritizes_release(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    prior_bytes = b'{"prior": true}\n'
    path.write_bytes(prior_bytes)
    body_error = OSError("body append injected")
    release_error = StrictJsonlError("lock release injected")

    def fail_append(path, line):
        raise body_error

    def fail_release(handle, lock_path):
        raise release_error

    monkeypatch.setattr(jsonl_module, "_append_serialized_jsonl_line", fail_append)
    monkeypatch.setattr(jsonl_module, "_release_jsonl_file_lock", fail_release)

    with pytest.raises(StrictJsonlError, match="lock release injected") as raised:
        append_strict_jsonl(path, {"new": True})

    assert raised.value is release_error
    assert raised.value.__context__ is body_error
    assert path.read_bytes() == prior_bytes


def test_append_strict_jsonl_partial_write_preserves_bytes_written_before_failure(
    tmp_path, monkeypatch
):
    path = tmp_path / "history.jsonl"
    prior_bytes = b'{"prior": true}\n'
    partial_line = '{"new'
    path.write_bytes(prior_bytes)
    _seed_jsonl_lock(path)
    original_open = builtins.open

    def partially_writing_open(target, mode="r", *args, **kwargs):
        handle = original_open(target, mode, *args, **kwargs)
        if Path(target) == path and mode == "a":
            return _WrappedJsonlFile(
                handle,
                partial_write_chars=len(partial_line),
            )
        return handle

    monkeypatch.setattr(
        jsonl_module,
        "open",
        partially_writing_open,
        raising=False,
    )

    with pytest.raises(OSError, match="append partial write injected"):
        append_strict_jsonl(path, {"new": True})

    assert path.read_bytes() == prior_bytes + partial_line.encode("utf-8")
