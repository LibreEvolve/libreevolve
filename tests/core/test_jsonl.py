import hashlib
import json
import math
import os
from pathlib import Path

import pytest

from libreevolve.core.jsonl import (
    StrictJsonlError,
    append_strict_jsonl,
    iter_strict_jsonl_objects,
    load_strict_json_object,
    repair_trailing_partial_jsonl,
    strict_json_dump,
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

    assert fsync_calls == 1
    assert path.read_text(encoding="utf-8") == '{"ok": true}\n'


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
