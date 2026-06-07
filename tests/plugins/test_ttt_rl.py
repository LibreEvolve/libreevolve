import json
import math
import tempfile
from pathlib import Path
import pytest
from libreevolve.plugins.ttt_rl import TTTRLPlugin
from libreevolve.population.program import Program

def _p(prompt="p", diff="d"):
    return Program(code="x=1", fitness=0.5, metadata={"prompt": prompt, "diff": diff})


class _RawMetadataProgram:
    def __init__(self, prompt, diff):
        self.metadata = {"prompt": prompt, "diff": diff}


def test_passthrough(): assert TTTRLPlugin().on_evaluated(_p(), 0.75) == 0.75


@pytest.mark.parametrize("train_every", [0, -1, 1.5, True])
def test_rejects_invalid_train_every(train_every):
    with pytest.raises(ValueError, match="train_every"):
        TTTRLPlugin(train_every=train_every)

@pytest.mark.parametrize("max_retained_examples", [0, -1, 1.5, True])
def test_rejects_invalid_max_retained_examples(max_retained_examples):
    with pytest.raises(ValueError, match="max_retained_examples"):
        TTTRLPlugin(max_retained_examples=max_retained_examples)


@pytest.mark.parametrize(
    ("kwarg", "value"),
    [
        ("max_payload_field_chars", 0),
        ("max_payload_field_chars", -1),
        ("max_payload_field_chars", 1.5),
        ("max_payload_field_chars", True),
        ("max_payload_total_chars", 0),
        ("max_payload_total_chars", -1),
        ("max_payload_total_chars", 1.5),
        ("max_payload_total_chars", True),
    ],
)
def test_rejects_invalid_payload_budgets(kwarg, value):
    with pytest.raises(ValueError, match=kwarg):
        TTTRLPlugin(**{kwarg: value})


def test_skips_without_metadata():
    p = TTTRLPlugin(); p.on_evaluated(Program(), 0.5)
    assert len(p.get_training_data()) == 0

def test_accumulates():
    p = TTTRLPlugin()
    for i in range(5): p.on_evaluated(_p(), i*0.1)
    assert len(p.get_training_data()) == 5


def test_training_data_snapshot_does_not_mutate_internal_queue():
    p = TTTRLPlugin()
    p.on_evaluated(_p("original", "diff"), 0.5)

    snapshot = p.get_training_data()
    snapshot[0]["prompt"] = "mutated"

    assert p.get_training_data()[0]["prompt"] == "original"


@pytest.mark.parametrize(
    ("prompt", "diff"),
    [
        (["prompt"], "diff"),
        ("prompt", {"diff": "value"}),
        ("", "diff"),
        ("prompt", "  "),
    ],
)
def test_skips_malformed_prompt_response_exports(prompt, diff):
    p = TTTRLPlugin()
    assert p.on_evaluated(_p(prompt, diff), 0.5) == 0.5
    assert p.get_training_data() == []
    metadata = p.run_artifacts_metadata()
    assert metadata["queued_examples"] == 0
    assert metadata["skipped_malformed_examples"] == 1
    assert metadata["malformed_example_reasons"] == {"invalid_prompt_or_response": 1}


@pytest.mark.parametrize("score", [True, False, "1.0", None, object(), math.inf, math.nan])
def test_rejects_malformed_export_scores(score):
    p = TTTRLPlugin()
    with pytest.raises(ValueError, match="finite non-boolean number"):
        p.on_evaluated(_p(), score)
    assert p.get_training_data() == []
    metadata = p.run_artifacts_metadata()
    assert metadata["skipped_malformed_examples"] == 1
    assert metadata["malformed_example_reasons"] == {"invalid_score": 1}


def test_writes_jsonl(tmp_path):
    p = TTTRLPlugin(train_every=5, log_dir=str(tmp_path))
    for i in range(12): p.on_evaluated(_p(f"p{i}", f"d{i}"), i*0.1)
    p.on_generation_end(5, None)
    assert (tmp_path/"grpo_data.jsonl").exists()
    lines = (tmp_path/"grpo_data.jsonl").read_text().splitlines()
    assert len(lines) == 12
    record = json.loads(lines[0])
    assert record["raw_score"] == 0.0
    assert record["reward"] == 0.0
    assert record["reward_policy"] == "max(0.0, raw_score)"
    metadata = p.run_artifacts_metadata()
    assert metadata["exported_examples"] == 12
    assert metadata["queued_examples"] == 12
    assert metadata["pending_examples"] == 0
    assert metadata["skipped_malformed_examples"] == 0
    assert metadata["malformed_example_reasons"] == {}
    assert metadata["redacted_payload_examples"] == 0
    assert metadata["truncated_payload_examples"] == 0
    assert metadata["aggregate_truncated_payload_examples"] == 0
    assert metadata["redacted_payload_fields"] == 0
    assert metadata["truncated_payload_fields"] == 0
    assert metadata["payload_original_chars"] > 0
    assert metadata["payload_stored_chars"] == metadata["payload_original_chars"]
    assert metadata["payload_policy"] == "redact_sensitive_text_then_truncate_field_and_total_chars"
    assert metadata["path"] == str(tmp_path / "grpo_data.jsonl")
    assert metadata["sha256"]
    assert metadata["bytes"] > 0


def test_writes_jsonl_with_missing_export_parent(tmp_path):
    log_dir = tmp_path / "missing" / "plugin_artifacts" / "ttt_rl"
    p = TTTRLPlugin(train_every=1, log_dir=str(log_dir))

    p.on_evaluated(_p("prompt", "diff"), 0.5)
    p.on_generation_end(1, None)

    records = [
        json.loads(line)
        for line in (log_dir / "grpo_data.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert records[0]["prompt"] == "prompt"
    assert records[0]["response"] == "diff"


def test_redacts_secret_like_payloads_before_queueing_and_export(tmp_path):
    secret = "sk-proj_tttsecret1234567890"  # pragma: allowlist secret
    p = TTTRLPlugin(train_every=1, log_dir=str(tmp_path))
    p.on_evaluated(_RawMetadataProgram(f"use {secret}", f"diff {secret}"), 0.5)

    record = p.get_training_data()[0]
    assert secret not in json.dumps(record)
    assert record["prompt"] == "use [REDACTED]"
    assert record["response"] == "diff [REDACTED]"
    p.on_generation_end(1, None)
    export_text = (tmp_path / "grpo_data.jsonl").read_text(encoding="utf-8")
    assert secret not in export_text
    metadata = p.run_artifacts_metadata()
    assert metadata["redacted_payload_examples"] == 1
    assert metadata["redacted_payload_fields"] == 2
    assert metadata["truncated_payload_examples"] == 0


def test_truncates_payload_fields_and_records_metadata(tmp_path):
    p = TTTRLPlugin(
        log_dir=str(tmp_path),
        max_payload_field_chars=20,
        max_payload_total_chars=50,
    )
    p.on_evaluated(_p("p" * 30, "response"), 0.5)

    record = p.get_training_data()[0]
    assert len(record["prompt"]) == 20
    assert record["prompt"].endswith("...[truncated]")
    assert record["response"] == "response"
    metadata = p.run_artifacts_metadata()
    assert metadata["truncated_payload_examples"] == 1
    assert metadata["aggregate_truncated_payload_examples"] == 0
    assert metadata["truncated_payload_fields"] == 1
    assert metadata["payload_original_chars"] == 38
    assert metadata["payload_stored_chars"] == 28
    assert metadata["max_payload_field_chars"] == 20
    assert metadata["max_payload_total_chars"] == 50


def test_truncates_payload_pair_to_aggregate_budget(tmp_path):
    p = TTTRLPlugin(
        log_dir=str(tmp_path),
        max_payload_field_chars=100,
        max_payload_total_chars=12,
    )
    p.on_evaluated(_p("prompt", "response" * 3), 0.5)

    record = p.get_training_data()[0]
    assert len(record["prompt"]) + len(record["response"]) == 12
    assert record["prompt"] == "prompt"
    assert record["response"] == "respon"
    metadata = p.run_artifacts_metadata()
    assert metadata["truncated_payload_examples"] == 1
    assert metadata["aggregate_truncated_payload_examples"] == 1
    assert metadata["truncated_payload_fields"] == 1
    assert metadata["payload_stored_chars"] == 12


def test_run_artifacts_metadata_flushes_pending_examples(tmp_path):
    p = TTTRLPlugin(train_every=50, log_dir=str(tmp_path))
    p.on_evaluated(_p("pending", "diff"), 0.5)

    metadata = p.run_artifacts_metadata()

    assert metadata["queued_examples"] == 1
    assert metadata["exported_examples"] == 1
    assert metadata["pending_examples"] == 0
    assert metadata["finalization_policy"] == "flush_pending_examples_before_artifact_metadata"
    assert metadata["path"] == str(tmp_path / "grpo_data.jsonl")
    lines = (tmp_path / "grpo_data.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["prompt"] == "pending"


def test_repeated_flush_does_not_duplicate_exports(tmp_path):
    p = TTTRLPlugin(train_every=1, log_dir=str(tmp_path))
    p.on_evaluated(_p("p0", "d0"), 0.25)
    p.on_generation_end(1, None)
    p.on_generation_end(1, None)
    assert len((tmp_path / "grpo_data.jsonl").read_text().splitlines()) == 1
    metadata = p.run_artifacts_metadata()
    assert metadata["exported_examples"] == 1
    assert metadata["queued_examples"] == 1
    assert metadata["pending_examples"] == 0

    p.on_evaluated(_p("p1", "d1"), 0.5)
    p.on_generation_end(2, None)
    lines = (tmp_path / "grpo_data.jsonl").read_text().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1])["prompt"] == "p1"
    assert p.run_artifacts_metadata()["pending_examples"] == 0


def test_restores_existing_export_counts_without_reexporting(tmp_path):
    existing = [
        {
            "prompt": "old0",
            "response": "d0",
            "raw_score": 0.25,
            "reward": 0.25,
            "reward_policy": "max(0.0, raw_score)",
        },
        {
            "prompt": "old1",
            "response": "d1",
            "raw_score": -0.25,
            "reward": 0.0,
            "reward_policy": "max(0.0, raw_score)",
        },
    ]
    (tmp_path / "grpo_data.jsonl").write_text(
        "\n".join(json.dumps(record) for record in existing) + "\n",
        encoding="utf-8",
    )
    p = TTTRLPlugin(train_every=1, log_dir=str(tmp_path))

    metadata = p.run_artifacts_metadata()

    assert metadata["exported_examples"] == 2
    assert metadata["restored_exported_examples"] == 2
    assert metadata["restore_invalid_lines"] == 0
    assert metadata["restore_policy"] == "count_existing_grpo_jsonl_rows_without_reexport"
    assert metadata["queued_examples"] == 0
    assert metadata["pending_examples"] == 0
    p.on_evaluated(_p("new", "diff"), 0.5)
    p.on_generation_end(1, None)
    lines = (tmp_path / "grpo_data.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["prompt"] for line in lines] == ["old0", "old1", "new"]
    assert p.run_artifacts_metadata()["exported_examples"] == 3


def test_restored_export_metadata_reports_invalid_existing_lines(tmp_path):
    (tmp_path / "grpo_data.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "prompt": "valid",
                        "response": "d",
                        "raw_score": 0.25,
                        "reward": 0.25,
                        "reward_policy": "max(0.0, raw_score)",
                    }
                ),
                "{not json",
                json.dumps({"prompt": "missing reward"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    metadata = TTTRLPlugin(log_dir=str(tmp_path)).run_artifacts_metadata()

    assert metadata["exported_examples"] == 1
    assert metadata["restored_exported_examples"] == 1
    assert metadata["restore_invalid_lines"] == 2


def test_restored_export_metadata_counts_duplicate_json_keys_as_invalid(tmp_path):
    (tmp_path / "grpo_data.jsonl").write_text(
        (
            '{"prompt":"valid","response":"d","raw_score":0.25,'
            '"reward":0.25,"reward_policy":"max(0.0, raw_score)"}\n'
            '{"prompt":"first","prompt":"second","response":"d",'
            '"raw_score":0.25,"reward":0.25,'
            '"reward_policy":"max(0.0, raw_score)"}\n'
        ),
        encoding="utf-8",
    )

    metadata = TTTRLPlugin(log_dir=str(tmp_path)).run_artifacts_metadata()

    assert metadata["exported_examples"] == 1
    assert metadata["restored_exported_examples"] == 1
    assert metadata["restore_invalid_lines"] == 1


def test_auto_exports_and_prunes_when_retention_limit_is_exceeded(tmp_path):
    p = TTTRLPlugin(train_every=100, log_dir=str(tmp_path), max_retained_examples=3)
    for i in range(8):
        p.on_evaluated(_p(f"p{i}", f"d{i}"), i * 0.1)

    lines = (tmp_path / "grpo_data.jsonl").read_text(encoding="utf-8").splitlines()
    retained = p.get_training_data()
    metadata = p.run_artifacts_metadata()
    assert len(lines) == 8
    assert [json.loads(line)["prompt"] for line in lines] == [f"p{i}" for i in range(8)]
    assert [record["prompt"] for record in retained] == ["p5", "p6", "p7"]
    assert metadata["queued_examples"] == 8
    assert metadata["exported_examples"] == 8
    assert metadata["pending_examples"] == 0
    assert metadata["retained_examples"] == 3
    assert metadata["max_retained_examples"] == 3
    assert metadata["dropped_retained_examples"] == 5


def test_records_clipped_reward_policy():
    p = TTTRLPlugin()
    p.on_evaluated(_p(), -0.5)
    p.on_evaluated(_p("positive", "diff"), 1)
    record = p.get_training_data()[0]
    assert record["raw_score"] == -0.5
    assert record["reward"] == 0.0
    assert record["reward_policy"] == "max(0.0, raw_score)"
    positive_record = p.get_training_data()[1]
    assert positive_record["raw_score"] == 1.0
    assert positive_record["reward"] == 1.0

def test_rejects_non_finite_jsonl_export(tmp_path):
    p = TTTRLPlugin(train_every=1, log_dir=str(tmp_path))
    with pytest.raises(ValueError, match="finite non-boolean number"):
        p.on_evaluated(_p(), math.inf)
    p.on_generation_end(1, None)
    assert not (tmp_path / "grpo_data.jsonl").exists()
    assert not (tmp_path / "grpo_data_invalid.jsonl").exists()


def test_invalid_score_does_not_block_later_valid_export(tmp_path):
    p = TTTRLPlugin(train_every=1, log_dir=str(tmp_path))
    with pytest.raises(ValueError, match="finite non-boolean number"):
        p.on_evaluated(_p("bad", "diff"), math.nan)

    p.on_evaluated(_p("good", "diff"), 0.75)
    p.on_generation_end(1, None)

    lines = (tmp_path / "grpo_data.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["prompt"] == "good"
    assert not (tmp_path / "grpo_data_invalid.jsonl").exists()
    metadata = p.run_artifacts_metadata()
    assert metadata["pending_examples"] == 0
    assert metadata["exported_examples"] == 1
    assert metadata["malformed_example_reasons"] == {"invalid_score": 1}
