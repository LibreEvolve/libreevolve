from fractions import Fraction
import copy
import hashlib
import json, math, os, subprocess, sys, tempfile
import random
from pathlib import Path
import pytest
from libreevolve.core.artifact_schema import ARCHIVE_EVENT_RECORD_SCHEMA, ARTIFACT_SCHEMA_VERSION, EVALUATOR_RESULT_RECORD_SCHEMA, FAILURE_RECORD_SCHEMA, HISTORY_RECORD_SCHEMA, LLM_CALL_RECORD_SCHEMA, LLM_REWARD_RECORD_SCHEMA, PROMPT_HISTORY_RECORD_SCHEMA, QUARANTINE_RECORD_SCHEMA, RUN_ARTIFACT_NAMES as SCHEMA_RUN_ARTIFACT_NAMES, RUN_MANIFEST_SCHEMA, generated_run_artifact_inventory, run_artifact_schema
from libreevolve.core.config import Config, ConfigError
from libreevolve.core.database import ArchiveStateRestoreError, HistoryRestoreError, RUN_ARTIFACT_NAMES, ProgramDatabase as _ProgramDatabase, load_failure_history_records, _program_from_history_record, validate_archive_state_snapshot, validate_run_directory_path
from libreevolve.core.jsonl import StrictJsonlError
from libreevolve.core.evaluator import _validator_boundary_metadata
from libreevolve.core.loop import _runtime_artifact_pointers
from libreevolve.core.prompt import PromptSampler
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem

def _objective_schema():
    return {
        "metrics": [
            {
                "name": "score",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            }
        ],
        "primary_metric": "score",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 1,
    }

def ProgramDatabase(config, **kwargs):
    kwargs.setdefault("objective_schema", _objective_schema())
    return _ProgramDatabase(config, **kwargs)


def _archive_restore_runtime(run_dir: Path, archive_state: dict) -> dict:
    return {
        "history": {"archive_state": archive_state},
        "artifacts": _runtime_artifact_pointers(run_dir),
    }


def _db():
    return ProgramDatabase(
        Config(log_dir=tempfile.mkdtemp(), problem_name="t"),
    )

def _p(code="x=1", fitness=0.5):
    return Program(code=code, fitness=fitness, evaluation={"is_valid": True})


def _problem():
    return Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["x=1"],
        problem_dir=Path("."),
    )

def test_log_always_appends():
    db = _db(); db.log(_p(fitness=-0.4))
    assert len(db.all_programs()) == 1


def test_add_updates_best():
    db = _db(); p = _p(fitness=0.8); db.log(p); db.add(p)
    assert db.best().fitness == 0.8


def test_raw_add_rejects_invalid_evaluation_without_archive_mutation():
    db = _db()
    program = _p(fitness=1.0)
    program.evaluation = {"is_valid": False}

    event = db.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert program.metadata["archive_admission"]["reason"] == "invalid_evaluation"
    assert program.metadata["archive_admission"]["threshold"] == 0.0
    assert db.best() is None


def test_public_add_records_archive_event_on_program_metadata_and_history():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = _p(fitness=0.8)

    event = db.add(program)
    db.log(program)

    assert event["admitted"] is True
    assert event["threshold"] == 0.0
    assert program.metadata["archive_admission"]["program_id"] == program.id
    assert program.metadata["archive_admission"]["threshold"] == 0.0
    [record] = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    assert record["metadata"]["archive_admission"]["program_id"] == program.id
    assert record["metadata"]["archive_admission"]["admitted"] is True


def test_archive_and_log_store_program_snapshots_not_live_aliases():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = Program(
        id="snapshot-1",
        files={"main.py": "x = 1\n", "helper.py": "VALUE = 1\n"},
        primary_file="main.py",
        fitness=0.8,
        generation=2,
        parent_id="parent-1",
        lineage=["root-1", "parent-1"],
        metadata={"note": {"value": "original"}},
        metrics={"score": 0.8},
        evaluation={"is_valid": True, "metadata": {"stage": "original"}},
    )

    db.add(program)
    db.log(program)

    program.code = "x = 999\n"
    program.files["main.py"] = "x = 999\n"
    program.metrics["score"] = 0.1
    program.metadata["note"]["value"] = "mutated"
    program.metadata["archive_admission"]["reason"] = "mutated"
    program.evaluation["is_valid"] = False
    program.evaluation["metadata"]["stage"] = "mutated"
    program.lineage.append("mutated")

    logged = db.all_programs()[0]
    best = db.best()

    assert logged.code == "x = 1\n"
    assert logged.files["main.py"] == "x = 1\n"
    assert logged.metrics["score"] == 0.8
    assert logged.metadata["note"]["value"] == "original"
    assert logged.metadata["archive_admission"]["reason"] != "mutated"
    assert logged.evaluation["is_valid"] is True
    assert logged.evaluation["metadata"]["stage"] == "original"
    assert logged.lineage == ["root-1", "parent-1"]
    assert best is not None
    assert best.code == "x = 1\n"
    assert best.files["helper.py"] == "VALUE = 1\n"
    assert best.metrics["score"] == 0.8

    logged.files["main.py"] = "changed returned log snapshot\n"
    best.metrics["score"] = 0.0
    best.metadata["archive_admission"]["reason"] = "changed returned best"

    assert db.all_programs()[0].files["main.py"] == "x = 1\n"
    assert db.best().metrics["score"] == 0.8
    assert db.best().metadata["archive_admission"]["reason"] != "changed returned best"


def test_public_add_enforces_default_admission_threshold():
    db = _db()
    program = _p(fitness=-0.25)
    program.evaluation = {"is_valid": True}

    event = db.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "below_threshold"
    assert event["threshold"] == 0.0
    assert program.metadata["archive_admission"]["reason"] == "below_threshold"
    assert db.best() is None


def test_raw_add_rejects_duplicate_archive_ids_before_island_mutation():
    db = _db()
    first = Program(id="same", code="x=1", fitness=0.8, evaluation={"is_valid": True})
    duplicate = Program(id="same", code="x=2", fitness=0.9, evaluation={"is_valid": True})

    event = db.add(first)

    assert event["admitted"] is True
    with pytest.raises(ValueError, match="duplicate archive program id"):
        db.add(duplicate)

    assert db.best().code == "x=1"
    assert "archive_admission" not in duplicate.metadata


def test_admit_rejects_duplicate_archive_ids_across_islands():
    db = ProgramDatabase(Config(log_dir=tempfile.mkdtemp(), problem_name="t", n_islands=2))
    first = Program(id="same", code="x=1", fitness=0.8, evaluation={"is_valid": True})
    duplicate = Program(id="same", code="x=2", fitness=0.9, evaluation={"is_valid": True})

    db.admit(first)

    with pytest.raises(ValueError, match="duplicate archive program id"):
        db.admit(duplicate)

    occupied = [
        program
        for island in db._islands.islands
        for program in island.occupied_cells()
    ]
    assert [program.id for program in occupied] == ["same"]
    assert occupied[0].code == "x=1"


def test_archive_rejects_different_object_with_logged_id():
    db = _db()
    logged = Program(id="same", code="x=logged", fitness=0.4, evaluation={"is_valid": True})
    duplicate = Program(id="same", code="x=archive", fitness=0.8, evaluation={"is_valid": True})

    db.log(logged)

    with pytest.raises(ValueError, match="duplicate archive program id"):
        db.add(duplicate)

    assert db.best() is None


def test_archive_allows_same_logged_object_to_be_admitted_once():
    db = _db()
    program = Program(id="same", code="x=1", fitness=0.8, evaluation={"is_valid": True})

    db.log(program)
    event = db.add(program)

    assert event["admitted"] is True
    assert db.best().id == "same"


@pytest.mark.parametrize("metrics", [{"score": "bad"}, {"score": True}, {"score": math.nan}])
def test_invalid_evaluation_with_malformed_metrics_returns_structured_rejection(metrics):
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": False, "error": "domain_invalid"}
    program.metrics = metrics

    event = db.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert event["evaluation_is_valid"] is False
    assert program.metadata["archive_admission"]["reason"] == "invalid_evaluation"
    assert db.best() is None


def test_admit_records_archive_event_on_program_metadata():
    db = _db()
    p = _p(fitness=0.8)
    p.evaluation = {"is_valid": True}
    event = db.admit(p, threshold=0.0)
    assert event["admitted"] is True
    assert event["cell_admitted"] is True
    assert event["elite_retained"] is True
    assert event["search_state_changed"] is True
    assert event["sampling_eligible"] is True
    assert p.metadata["archive_admission"]["program_id"] == p.id
    assert p.metadata["archive_admission"]["island_id"] == 0
    assert p.metadata["archive_admission"]["threshold"] == 0.0


def test_archive_event_append_failure_leaves_archive_state_ahead_of_stream(
    tmp_path, monkeypatch
):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    program = Program(
        id="failed-append",
        code="failed_append",
        fitness=0.8,
        evaluation={"is_valid": True},
    )

    def fail_archive_append(*args, **kwargs):
        raise StrictJsonlError("simulated archive event append failure")

    monkeypatch.setattr(
        "libreevolve.core.database.append_strict_jsonl",
        fail_archive_append,
    )

    with pytest.raises(StrictJsonlError, match="simulated archive event append failure"):
        db.admit(program)

    assert not (tmp_path / "t" / "archive_events.jsonl").exists()
    assert db.best().id == program.id
    assert db.archive_state_snapshot()["archive_sequence"] == 1
    assert db._archive_admission_event_sequence == 1
    assert program.metadata["archive_admission"]["admitted"] is True


def test_archive_admission_flags_distinguish_retention_outcomes(tmp_path):
    flag_names = (
        "cell_admitted",
        "elite_retained",
        "search_state_changed",
        "sampling_eligible",
        "admitted",
    )
    cases = [
        (
            "elite_only",
            "elite_only",
            Config(
                log_dir=str(tmp_path / "elite_only"),
                problem_name="t",
                n_islands=1,
                map_elites_bins=1,
            ),
            [
                Program(
                    id="occupied",
                    code="occupied",
                    fitness=0.9,
                    evaluation={"is_valid": True},
                    metadata={
                        "selection_score": 0.9,
                        "normalized_metrics": {"score": 0.1},
                    },
                )
            ],
            Program(
                id="elite",
                code="elite",
                fitness=0.1,
                evaluation={"is_valid": True},
                metadata={
                    "selection_score": 0.1,
                    "normalized_metrics": {"score": 0.95},
                },
            ),
            (False, True, True, False, True),
        ),
        (
            "not_improving_cell",
            "not_improving_cell",
            Config(
                log_dir=str(tmp_path / "not_improving_cell"),
                problem_name="t",
                n_islands=1,
                map_elites_bins=1,
                elite_archive_size=1,
            ),
            [
                Program(
                    id="occupied",
                    code="occupied",
                    fitness=0.9,
                    evaluation={"is_valid": True},
                )
            ],
            Program(
                id="weak",
                code="weak",
                fitness=0.1,
                evaluation={"is_valid": True},
            ),
            (False, False, False, False, False),
        ),
        (
            "cell_replaced",
            "cell_replaced",
            Config(
                log_dir=str(tmp_path / "cell_replaced"),
                problem_name="t",
                n_islands=1,
                map_elites_bins=1,
                elite_archive_size=1,
            ),
            [
                Program(
                    id="occupied",
                    code="occupied",
                    fitness=0.5,
                    evaluation={"is_valid": True},
                )
            ],
            Program(
                id="replacement",
                code="replacement",
                fitness=0.8,
                evaluation={"is_valid": True},
            ),
            (True, True, True, True, True),
        ),
    ]

    for name, expected_reason, config, existing, candidate, expected_flags in cases:
        db = ProgramDatabase(config)
        for program in existing:
            db.admit(program)

        event = db.admit(candidate)
        record = json.loads(db._archive_events.read_text().splitlines()[-1])

        assert event["reason"] == expected_reason, name
        assert tuple(event[field] for field in flag_names) == expected_flags, name
        assert record["reason"] == expected_reason, name
        assert tuple(record[field] for field in flag_names) == expected_flags, name


def test_admit_non_improving_candidate_does_not_advance_island_cursor():
    db = ProgramDatabase(
        Config(
            log_dir=tempfile.mkdtemp(),
            problem_name="t",
            n_islands=2,
            map_elites_bins=1,
            elite_archive_size=1,
        )
    )
    first = Program(
        code="island0",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    second = Program(
        code="island1",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.8},
    )
    weak = Program(
        code="weak",
        fitness=0.1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.1},
    )
    replacement = Program(
        code="replacement",
        fitness=1.0,
        evaluation={"is_valid": True},
        metadata={"selection_score": 1.0},
    )

    first_event = db.admit(first)
    second_event = db.admit(second)
    weak_event = db.admit(weak)
    replacement_event = db.admit(replacement)

    assert first_event["island_id"] == 0
    assert second_event["island_id"] == 1
    assert weak_event["island_id"] == 0
    assert weak_event["reason"] == "not_improving_cell"
    assert weak_event["search_state_changed"] is False
    assert weak.metadata["archive_admission"]["admitted"] is False
    assert replacement_event["island_id"] == 0
    assert replacement_event["reason"] == "cell_replaced"
    assert replacement_event["previous_occupant_id"] == first.id

def test_admit_below_threshold_does_not_archive():
    db = _db()
    p = _p(fitness=-0.1)
    p.evaluation = {"is_valid": True}
    event = db.admit(p, threshold=0.0)
    assert event["admitted"] is False
    assert event["reason"] == "below_threshold"
    assert event["cell_admitted"] is False
    assert event["elite_retained"] is False
    assert event["search_state_changed"] is False
    assert event["sampling_eligible"] is False
    assert event["evaluation_is_valid"] is True
    assert event["island_id"] is None
    assert db.best() is None

def test_admit_invalid_evaluation_does_not_archive_even_with_high_fitness():
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = {"is_valid": False}
    event = db.admit(p, threshold=0.0)
    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert event["evaluation_is_valid"] is False
    assert db.best() is None


@pytest.mark.parametrize("fitness", [float("nan"), float("inf"), float("-inf")])
def test_admit_rejects_non_finite_fitness_before_archive(fitness):
    db = _db()
    p = _p(fitness=1.0)
    p.fitness = fitness
    p.evaluation = {"is_valid": True}
    p.metadata["selection_score"] = 0.5

    event = db.admit(p, threshold=0.0)

    assert event["admitted"] is False
    assert event["reason"] == "non_finite_fitness"
    assert event["evaluation_is_valid"] is True
    assert db.best() is None


@pytest.mark.parametrize("fitness", [True, False, "1.0"])
def test_admit_rejects_invalid_fitness_type_before_archive(fitness):
    db = _db()
    p = _p(fitness=1.0)
    p.fitness = fitness
    p.evaluation = {"is_valid": True}

    event = db.admit(p, threshold=0.0)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_fitness_type"
    assert event["evaluation_is_valid"] is True
    assert db.best() is None


@pytest.mark.parametrize("is_valid", [None, "false", 1])
def test_admit_requires_exact_boolean_validity(is_valid):
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = {} if is_valid is None else {"is_valid": is_valid}

    event = db.admit(p, threshold=0.0)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert event["evaluation_is_valid"] is False
    assert db.best() is None


def test_admit_cannot_receive_malformed_evolve_block_program():
    with pytest.raises(ValueError, match="main.py:malformed_evolve_blocks:orphan_end"):
        Program(
            files={"main.py": "# EVOLVE-BLOCK-END\n"},
            evaluation={"is_valid": True},
            fitness=1.0,
        )


def test_program_construction_rejects_non_mapping_evaluation():
    with pytest.raises(ValueError, match="Program evaluation must be a JSON-safe evaluation mapping"):
        Program(code="x=1", fitness=1.0, evaluation=[])


def test_admit_prevalidates_history_record_before_archive_mutation():
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = {"is_valid": True}
    p.metadata["bad"] = {"not", "json"}

    with pytest.raises(ValueError, match="Program metadata.bad must be JSON-safe metadata"):
        db.admit(p, threshold=0.0)

    assert db.best() is None
    assert db.all_programs() == []


def test_log_revalidates_mutated_program_metadata_before_history_write():
    db = _db()
    p = _p(fitness=0.5)
    p.metadata = []

    with pytest.raises(ValueError, match="Program metadata must be a JSON-safe metadata mapping"):
        db.log(p)

    assert db.all_programs() == []
    assert not Path(db._jsonl).exists() or Path(db._jsonl).read_text(encoding="utf-8") == ""


def test_admit_revalidates_mutated_program_metadata_before_archive_write():
    db = _db()
    p = _p(fitness=1.0)
    p.metadata = ["bad"]

    with pytest.raises(ValueError, match="Program metadata must be a JSON-safe metadata mapping"):
        db.admit(p, threshold=0.0)

    assert db.best() is None
    assert db.all_programs() == []
    assert "archive_admission" not in getattr(p, "metadata", {})


@pytest.mark.parametrize("evaluation", [[], {"bad": object()}])
def test_admit_revalidates_mutated_program_evaluation_before_archive_write(evaluation):
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = evaluation

    with pytest.raises(ValueError, match="Program evaluation"):
        db.admit(p, threshold=0.0)

    assert db.best() is None
    assert db.all_programs() == []
    assert "archive_admission" not in getattr(p, "metadata", {})


def test_log_failure_revalidates_mutated_program_metadata_before_side_effects():
    db = _db()
    parent = _p()
    child = _p()
    child.metadata = {"bad": object()}

    with pytest.raises(ValueError, match="Program metadata.bad must be JSON-safe metadata"):
        db.log_failure(child, parent, "mutation", diff_error="bad_diff")

    assert "failure_record" not in getattr(child, "metadata", {})


@pytest.mark.parametrize("evaluation", [[], {"bad": object()}])
def test_log_revalidates_mutated_program_evaluation_before_history_write(evaluation):
    db = _db()
    p = _p(fitness=0.5)
    p.evaluation = evaluation

    with pytest.raises(ValueError, match="Program evaluation"):
        db.log(p)

    assert db.all_programs() == []
    assert not Path(db._jsonl).exists() or Path(db._jsonl).read_text(encoding="utf-8") == ""


@pytest.mark.parametrize("evaluation", [[], {"bad": object()}])
def test_log_failure_revalidates_mutated_program_evaluation_before_side_effects(evaluation):
    db = _db()
    parent = _p()
    child = _p()
    child.evaluation = evaluation

    with pytest.raises(ValueError, match="Program evaluation"):
        db.log_failure(child, parent, "mutation", diff_error="bad_diff")

    assert "failure_record" not in child.metadata
    assert db._failure_counts == {}


@pytest.mark.parametrize("threshold", [math.nan, math.inf, "0"])
def test_admit_rejects_invalid_threshold_before_archive_mutation(threshold):
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = {"is_valid": True}

    with pytest.raises(ValueError, match="archive admission threshold"):
        db.admit(p, threshold=threshold)

    assert db.best() is None
    assert "archive_admission" not in p.metadata


def test_rejected_non_finite_selection_score_is_history_safe():
    db = _db()
    p = _p(fitness=1.0)
    p.fitness = math.inf
    p.evaluation = {"is_valid": False}

    event = db.admit(p, threshold=0.0)

    assert event["admitted"] is False
    assert event["selection_score"] is None
    assert p.metadata["archive_admission"]["selection_score"] is None


def test_log_without_add_not_in_archive():
    db = _db(); db.log(_p(fitness=-0.3))
    assert db.best() is None

def test_sample_exploit():
    db = _db()
    for f in (0.3, 0.7):
        p = _p(fitness=f); db.log(p); db.add(p)
    assert db.sample("exploit").fitness == 0.7

def test_sample_diverse_excludes_program_ids():
    db = _db()
    p = _p(fitness=0.7); db.log(p); db.add(p)
    assert db.sample_diverse(k=3, exclude_ids={p.id}) == []


def test_sample_diverse_normalizes_exclude_id_sequences():
    db = _db()
    p = _p(fitness=0.7)
    db.add(p)

    assert db.sample_diverse(k=3, exclude_ids=[p.id, p.id]) == []
    assert db.sample_diverse(k=3, exclude_ids=(p.id,)) == []


@pytest.mark.parametrize(
    "exclude_ids",
    [
        "program-id",
        {"program-id": True},
        {1},
        ["bad id"],
        ["api_key=sk-proj_exclude_secret_1234567890"],  # pragma: allowlist secret
    ],
)
def test_sample_diverse_rejects_invalid_exclude_ids(exclude_ids):
    db = _db()
    db.add(_p(fitness=0.7))

    with pytest.raises(ValueError, match="database exclude_ids"):
        db.sample_diverse(k=3, exclude_ids=exclude_ids)


def test_sample_diverse_accepts_zero_and_oversized_counts():
    db = _db()
    for index in range(2):
        program = _p(code=f"x={index}", fitness=index * 0.1)
        db.admit(program)

    assert db.sample_diverse(k=0) == []
    assert len(db.sample_diverse(k=10)) <= 2


def test_database_random_sampling_uses_local_rng_not_process_global():
    db = ProgramDatabase(
        Config(log_dir=tempfile.mkdtemp(), problem_name="t", n_islands=1),
        rng=random.Random(42),
    )
    for index in range(3):
        db.admit(_p(code=f"x={index}", fitness=0.4 + index * 0.1))

    random.seed(123)
    expected_after_sampling = random.Random(123).random()

    assert db.sample("explore") is not None
    assert db.sample_diverse(k=2, strategy="random")
    assert random.random() == expected_after_sampling


@pytest.mark.parametrize("k", ["2", True, 1.5, -1])
def test_sample_diverse_rejects_invalid_counts(k):
    db = _db()
    p = _p(fitness=0.7)
    db.add(p)

    with pytest.raises(ValueError, match="database sample count"):
        db.sample_diverse(k=k)


def test_metric_sampling_cycles_objective_schema_metric_targets_primary_first():
    tmpdir = tempfile.mkdtemp()
    schema = {
        "metrics": [
            {
                "name": "latency",
                "direction": "maximize",
                "primary": False,
                "bounds": [0.0, 1.0],
            },
            {
                "name": "primary",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            },
        ],
        "primary_metric": "primary",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 2,
    }
    db = ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t", n_islands=1),
        objective_schema=schema,
    )
    latency_leader = Program(
        code="latency",
        fitness=0.1,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.1,
            "normalized_metrics": {"primary": 0.1, "latency": 0.95},
        },
    )
    primary_leader = Program(
        code="primary",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.9,
            "normalized_metrics": {"primary": 0.9, "latency": 0.1},
        },
    )
    db.admit(latency_leader)
    db.admit(primary_leader)

    assert db.sample("metric").id == primary_leader.id
    assert db.last_sample_metadata() == {
        "strategy": "metric",
        "selected_program_id": primary_leader.id,
        "target_metric": "primary",
        "metric_target_index": 0,
        "metric_target_count": 2,
    }
    assert db.sample("metric").id == latency_leader.id
    assert db.last_sample_metadata()["target_metric"] == "latency"
    assert db.sample("metric").id == primary_leader.id
    assert [p.id for p in db.sample_diverse(k=1, strategy="metric")] == [
        primary_leader.id
    ]


def test_elite_only_archive_rows_resurface_through_public_retained_strategies():
    db = ProgramDatabase(
        Config(
            log_dir=tempfile.mkdtemp(),
            problem_name="t",
            n_islands=1,
            map_elites_bins=1,
        )
    )
    occupied = Program(
        code="occupied",
        fitness=0.9,
        generation=1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9, "normalized_metrics": {"score": 0.1}},
    )
    elite_only = Program(
        code="elite_only",
        fitness=0.1,
        generation=9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.1, "normalized_metrics": {"score": 0.95}},
    )

    occupied_event = db.admit(occupied)
    elite_event = db.admit(elite_only)

    assert occupied_event["sampling_eligible"] is True
    assert elite_event["reason"] == "elite_only"
    assert elite_event["elite_retained"] is True
    assert elite_event["sampling_eligible"] is False
    assert db.sample("explore").id == occupied.id
    assert db.sample("metric").id == elite_only.id
    assert db.sample("recency").id == elite_only.id
    assert [p.id for p in db.sample_diverse(k=1, strategy="metric")] == [
        elite_only.id
    ]
    assert [p.id for p in db.sample_diverse(k=2, strategy="selection")] == [
        occupied.id,
        elite_only.id,
    ]
    assert [p.id for p in db.sample_diverse(k=2, strategy="random")] == [
        occupied.id
    ]


def test_archive_sequence_is_persisted_and_drives_recency_sampling():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t", n_islands=1))
    older_high_score = Program(
        code="older",
        fitness=0.9,
        generation=0,
        evaluation={"is_valid": True},
    )
    newer_low_score = Program(
        code="newer",
        fitness=0.1,
        generation=0,
        evaluation={"is_valid": True},
    )

    db.admit(older_high_score)
    db.log(older_high_score)
    db.admit(newer_low_score)
    db.log(newer_low_score)

    assert db.sample("recency").id == newer_low_score.id
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    assert records[0]["metadata"]["archive_sequence"] == 1
    assert records[0]["metadata"]["archive_admission"]["archive_sequence"] == 1
    assert records[1]["metadata"]["archive_sequence"] == 2
    assert records[1]["metadata"]["archive_admission"]["archive_sequence"] == 2


def test_archive_state_snapshot_exposes_island_cursor_for_runtime_manifest():
    db = ProgramDatabase(
        Config(
            log_dir=tempfile.mkdtemp(),
            problem_name="t",
            n_islands=2,
            map_elites_bins=1,
            elite_archive_size=1,
        )
    )
    first = Program(
        code="island0",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    second = Program(
        code="island1",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.8},
    )
    weak = Program(
        code="weak",
        fitness=0.1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.1},
    )

    db.admit(first)
    db.admit(second)
    weak_event = db.admit(weak)

    snapshot = db.archive_state_snapshot()
    assert weak_event["search_state_changed"] is False
    assert snapshot["schema"] == "libreevolve.island_state.v1"
    assert snapshot["resume_status"] == (
        "snapshot_persisted_cursor_and_full_archive_restore_supported"
    )
    assert snapshot["next_island_id"] == 0
    assert snapshot["archive_sequence"] == 3
    assert snapshot["frontier_sample_index"] == 0
    assert snapshot["archive_sequence_by_program_id"] == {
        first.id: 1,
        second.id: 2,
    }
    assert snapshot["topology_policy"]["schema"] == "libreevolve.island_topology_policy.v1"
    assert snapshot["topology_policy"]["configured_n_islands"] == 2
    assert snapshot["topology_policy"]["default_n_islands"] == 5
    assert snapshot["topology_policy"]["island_count_configurable"] is True
    assert snapshot["topology_policy"]["migration_topology"] == "ring"
    assert snapshot["topology_policy"]["adaptive_island_count_supported"] is False
    assert snapshot["topology_policy"]["non_ring_topologies_supported"] is False
    assert snapshot["topology_policy"]["alphaevolve_policy_ready"] is False
    assert snapshot["migration_replay"]["status"] == "not_applied_as_restore_engine"
    assert snapshot["migration_replay"]["replay_engine_supported"] is False
    assert snapshot["migration_replay"]["migration_sequence"] == 0
    assert snapshot["islands"] == [
        {
            "island_id": 0,
            "occupied_cell_count": 1,
            "elite_count": 1,
            "pareto_frontier_count": 0,
            "metric_cell_archive_count": 0,
        },
        {
            "island_id": 1,
            "occupied_cell_count": 1,
            "elite_count": 1,
            "pareto_frontier_count": 0,
            "metric_cell_archive_count": 0,
        },
    ]


def test_log_quarantines_mutated_invalid_generation():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = _p(fitness=0.5)
    program.generation = "api_key=sk-proj_secret_1234567890"

    with pytest.raises(StrictJsonlError, match="generation must be"):
        db.log(program)

    run_dir = Path(tmpdir) / "t"
    assert not (run_dir / "history.jsonl").exists()
    assert "generation must be" in (run_dir / "history_invalid.jsonl").read_text()


@pytest.mark.parametrize("metrics", [{"score": "bad"}, {"score": True}, {"score": Fraction(1, 2)}])
def test_log_quarantines_mutated_invalid_metrics(metrics):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = _p(fitness=0.5)
    program.metrics = metrics

    with pytest.raises(StrictJsonlError, match="Program metric values"):
        db.log(program)

    run_dir = Path(tmpdir) / "t"
    assert not (run_dir / "history.jsonl").exists()
    assert "Program metric values" in (run_dir / "history_invalid.jsonl").read_text()


@pytest.mark.parametrize(
    "metrics",
    [
        {"api_key=sk-proj_metric_key_secret_1234567890": 0.2},  # pragma: allowlist secret
        {"score\u202e": 0.2},
        {"score-secret": 0.2},
    ],
)
def test_log_quarantines_mutated_unsafe_metric_names(metrics):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = _p(fitness=0.5)
    program.metrics = metrics

    with pytest.raises(StrictJsonlError, match="Program metric names"):
        db.log(program)

    run_dir = Path(tmpdir) / "t"
    assert not (run_dir / "history.jsonl").exists()
    text = (run_dir / "history_invalid.jsonl").read_text()
    assert "Program metric names" in text
    assert "sk-proj_metric_key_secret" not in text


def test_admit_rejects_mutated_invalid_generation_before_archive():
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    program.generation = -10

    with pytest.raises(StrictJsonlError, match="generation must be"):
        db.admit(program)

    assert db.best() is None


def test_admit_rejects_mutated_invalid_metrics_before_archive():
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    program.metrics = {"score": True}

    with pytest.raises(ValueError, match="Program metric values"):
        db.admit(program)

    assert db.best() is None


def test_admit_rejects_mutated_unsafe_metric_names_before_archive():
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    program.metrics = {"score\u202e": 0.2}

    with pytest.raises(ValueError, match="Program metric names"):
        db.admit(program)

    assert db.best() is None
    assert db.all_programs() == []


def test_admit_rejects_non_json_native_metrics_before_archive():
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    program.metrics = {"score": Fraction(1, 2), "is_valid": True}

    with pytest.raises(ValueError, match="JSON-native finite numbers"):
        db.admit(program)

    assert db.best() is None
    assert db.all_programs() == []


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda program: setattr(program, "id", "api_key=sk-proj_candidate_secret_1234567890\nnext"), "Program id"),  # pragma: allowlist secret
        (lambda program: setattr(program, "parent_id", "parent\nnext"), "Program parent_id"),
        (lambda program: setattr(program, "lineage", ["root", "bad\nnext"]), r"Program lineage\[1\]"),
    ],
)
def test_admit_rejects_mutated_unsafe_program_identity_before_archive(mutate, message):
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    mutate(program)

    with pytest.raises(StrictJsonlError, match=message):
        db.admit(program)

    assert db.best() is None


def test_log_quarantines_mutated_unsafe_program_identity():
    db = _db()
    program = _p(fitness=0.5)
    program.id = "api_key=sk-proj_candidate_secret_1234567890\nnext"  # pragma: allowlist secret

    with pytest.raises(StrictJsonlError, match="Program id"):
        db.log(program)

    run_dir = Path(db._jsonl).parent
    assert not (run_dir / "history.jsonl").exists()
    assert "Program id" in (run_dir / "history_invalid.jsonl").read_text()


def test_log_rejects_duplicate_program_ids():
    db = _db()
    first = _p(fitness=0.5)
    second = _p(code="x=2", fitness=0.4)
    second.id = first.id
    db.log(first)

    with pytest.raises(StrictJsonlError, match="duplicate program id"):
        db.log(second)

    run_dir = Path(db._jsonl).parent
    accepted = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    quarantine = [
        json.loads(line)
        for line in (run_dir / "history_invalid.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [record["id"] for record in accepted] == [first.id]
    assert len(quarantine) == 1
    assert "duplicate program id" in quarantine[0]["message"]
    assert second.code in quarantine[0]["record_repr"]
    assert db._ids == {first.id}
    assert [program.code for program in db.all_programs()] == [first.code]


def test_log_honors_quarantine_snapshot_hash_only_retention():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(
            log_dir=tmpdir,
            problem_name="t",
            quarantine_snapshot_retention_mode="hash_only",
        )
    )
    first = _p(code="x=1", fitness=0.5)
    second = _p(
        code="api_key=sk-proj_quarantine_snapshot_secret_123456",
        fitness=0.4,
    )
    second.id = first.id
    db.log(first)

    with pytest.raises(StrictJsonlError, match="duplicate program id"):
        db.log(second)

    run_dir = Path(tmpdir) / "t"
    [record] = [
        json.loads(line)
        for line in (run_dir / "history_invalid.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    assert "record_repr" not in record
    assert "record_repr_truncated" not in record
    retention = record["record_repr_retention"]
    assert retention["retention_mode"] == "hash_only"
    assert retention["sha256"]
    assert retention["stored_chars"] == 0
    assert "sk-proj_" not in json.dumps(record)


def test_failure_history_quarantines_mutated_unsafe_program_identity():
    db = _db()
    parent = _p(fitness=0.5)
    child = _p(fitness=-0.1)
    child.id = "api_key=sk-proj_candidate_secret_1234567890\nnext"  # pragma: allowlist secret

    with pytest.raises(StrictJsonlError, match="Program id"):
        db.log_failure(child, parent, "mutation", "diff failed")

    run_dir = Path(db._jsonl).parent
    assert not (run_dir / "failure_history.jsonl").exists()
    assert "Program id" in (run_dir / "failure_history_invalid.jsonl").read_text()


def test_failure_history_quarantines_mutated_invalid_generation():
    db = _db()
    parent = _p(fitness=0.5)
    child = _p(fitness=-0.1)
    child.generation = "bad"

    with pytest.raises(StrictJsonlError, match="generation must be"):
        db.log_failure(child, parent, "mutation", "diff failed")

    run_dir = Path(db._jsonl).parent
    assert not (run_dir / "failure_history.jsonl").exists()
    assert "generation must be" in (run_dir / "failure_history_invalid.jsonl").read_text()


def test_log_writes_jsonl():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(_p(fitness=0.5))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["fitness"] == 0.5


def test_run_artifacts_include_current_schema_markers():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=0.5)
    child = _p(fitness=-0.1)
    db.log(parent)
    db.log_failure(child, parent, "mutation", "diff failed")
    db.log_llm_call(
        {
            "id": "call-1",
            "sequence_id": 1,
            "role": "mutation",
            "backend_idx": 0,
            "backend_name": "backend",
            "prompt_chars": 1,
            "prompt_sha256": "0" * 64,
            "status": "ok",
            "output_chars": 1,
            "output_sha256": "1" * 64,
            "counts_before": [0],
            "counts_after": [1],
            "will_retry": False,
            "will_fallback": False,
        }
    )
    db.log_llm_call(
        {
            "record_type": "reward",
            "call_id": "call-1",
            "backend_idx": 0,
            "reward": 0.5,
            "reward_raw": 0.5,
            "rewarded": True,
        }
    )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    history = json.loads((run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()[0])
    failure = json.loads(
        (run_dir / "failure_history.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    llm_call, llm_reward = [
        json.loads(line)
        for line in (run_dir / "llm_calls.jsonl").read_text(encoding="utf-8").splitlines()
    ]

    assert manifest["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert manifest["artifact_schema"]["name"] == RUN_MANIFEST_SCHEMA
    assert manifest["artifact_schema"]["jsonl_records"]["history.jsonl"] == HISTORY_RECORD_SCHEMA
    assert (
        manifest["artifact_schema"]["jsonl_records"]["evaluator_results.jsonl"]
        == EVALUATOR_RESULT_RECORD_SCHEMA
    )
    assert (
        manifest["artifact_schema"]["jsonl_records"]["archive_events.jsonl"]
        == ARCHIVE_EVENT_RECORD_SCHEMA
    )
    quarantine_schema = manifest["artifact_schema"]["quarantine_jsonl_records"]
    assert sorted(quarantine_schema) == [
        "archive_events_invalid.jsonl",
        "controller_budget_events_invalid.jsonl",
        "failure_history_invalid.jsonl",
        "history_invalid.jsonl",
        "llm_calls_invalid.jsonl",
        "manifest_invalid.jsonl",
        "prompt_history_invalid.jsonl",
    ]
    assert quarantine_schema["history_invalid.jsonl"] == {
        "source_stream": "history.jsonl",
        "source_record_schema": HISTORY_RECORD_SCHEMA,
        "diagnostic_record_schema": QUARANTINE_RECORD_SCHEMA,
        "diagnostic_fields": {
            "error": "exception class name",
            "message": "bounded redacted serialization or repair diagnostic",
            "record_type": "original record Python type label",
            "record_repr_retention": "redacted|hash_only|off",
            "record_repr": "optional retained rejected-record snapshot",
            "record_repr_truncated": "optional retained snapshot truncation flag",
            "record_repr_error": "optional safe snapshot-construction diagnostic",
        },
        "retention_mode_field": "config.quarantine_snapshot_retention_mode",
        "lifecycle_status": "optional_diagnostic_lifecycle_managed",
    }
    assert (
        quarantine_schema["prompt_history_invalid.jsonl"]["source_record_schema"]
        == PROMPT_HISTORY_RECORD_SCHEMA
    )
    assert (
        quarantine_schema["manifest_invalid.jsonl"]["source_record_schema"]
        == RUN_MANIFEST_SCHEMA
    )
    assert quarantine_schema["llm_calls_invalid.jsonl"]["source_record_schema"] == {
        "call": LLM_CALL_RECORD_SCHEMA,
        "reward": LLM_REWARD_RECORD_SCHEMA,
    }
    non_jsonl_schema = manifest["artifact_schema"]["non_jsonl_artifacts"]
    assert sorted(non_jsonl_schema) == [
        "best.py",
        "best_workspace",
        "evaluator_artifacts",
        "manifest.json",
    ]
    assert set(non_jsonl_schema) <= RUN_ARTIFACT_NAMES
    assert non_jsonl_schema["manifest.json"]["runtime_pointer_location"] == "self"
    assert non_jsonl_schema["best.py"]["kind"] == "file"
    assert non_jsonl_schema["best.py"]["hash_policy"] == "file_sha256_when_present"
    assert (
        non_jsonl_schema["best.py"]["runtime_pointer_location"]
        == 'runtime.artifacts["best.py"]'
    )
    for artifact_name in (
        "best_workspace",
        "evaluator_artifacts",
    ):
        artifact = non_jsonl_schema[artifact_name]
        assert artifact["kind"] == "directory"
        assert artifact["hash_policy"] == "tree_hash_when_present"
        assert (
            artifact["lifecycle_status"]
            == "known_artifact_collision_checked_and_overwrite_managed"
        )
    assert history["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert history["record_schema"] == HISTORY_RECORD_SCHEMA
    assert failure["record_schema"] == FAILURE_RECORD_SCHEMA
    assert llm_call["record_schema"] == LLM_CALL_RECORD_SCHEMA
    assert llm_reward["record_schema"] == LLM_REWARD_RECORD_SCHEMA


def test_log_writes_metrics_and_evaluation():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(_p(fitness=0.5))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert "metrics" in records[0]
    assert "evaluation" in records[0]

def test_log_writes_candidate_files():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(Program(
        files={"main.py": "x=1", "helper.py": "y=2"},
        primary_file="main.py",
        fitness=0.0,
    ))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["primary_file"] == "main.py"
    assert records[0]["files"]["helper.py"] == "y=2"


def test_log_writes_canonical_empty_candidate_files():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(Program(fitness=0.0))

    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["primary_file"] == "main.py"
    assert records[0]["files"] == {"main.py": ""}
    assert records[0]["code"] == ""


def test_log_writes_workspace_primary_as_code_when_legacy_code_disagrees():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(Program(
        code='x = "legacy"\n',
        files={"main.py": 'x = "workspace"\n', "helper.py": "y = 2\n"},
        primary_file="main.py",
        fitness=0.0,
    ))

    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["code"] == 'x = "workspace"\n'
    assert records[0]["files"]["main.py"] == 'x = "workspace"\n'

def test_log_failure_writes_queryable_failure_record():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = Program(
        id="parent",
        files={"main.py": "from helper import value\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
        fitness=1.0,
    )
    child = Program(
        files={"main.py": "from helper import value\n", "helper.py": "value = 0\n"},
        primary_file="main.py",
        parent_id=parent.id,
        fitness=-0.4,
        metadata={
            "mutation_mode": "diff",
            "mutation_mode_selection": {
                "schema": "libreevolve.mutation_mode_selection.v1",
                "selected_mode": "diff",
                "effective_mode": "diff",
            },
        },
        evaluation={
            "is_valid": False,
            "error": "wrong",
            "stdout": "bad",
            "metadata": {
                "validator_boundary": _validator_boundary_metadata("host")
            },
        },
    )

    record = db.log_failure(child, parent, "<<<FILE helper.py\nvalue = 0\n>>>FILE", None)

    assert record["changed_files"] == ["helper.py"]
    assert record["file_deltas"] == [{"path": "helper.py", "change": "modified"}]
    assert record["failure_fingerprint"]["schema"] == "failure_fingerprint_v1"
    assert record["failure_fingerprint"]["record_type"] == "generated"
    assert record["failure_fingerprint"]["parent_id"] == "parent"
    assert record["failure_fingerprint"]["mutation_sha256"] == record["mutation_sha256"]
    assert record["failure_fingerprint"]["changed_files"] == ["helper.py"]
    assert len(record["failure_fingerprint"]["sha256"]) == 64
    assert record["repetition_count"] == 1
    assert record["mutation_mode"] == "diff"
    assert record["mutation_mode_selection"]["selected_mode"] == "diff"
    assert child.metadata["failure_record"]["program_id"] == child.id
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert records[0]["evaluation"]["stdout"] == "bad"
    assert records[0]["evaluation"]["metadata"]["validator_boundary"]["network_policy"] == "host"


@pytest.mark.parametrize(
    ("payload", "payload_type", "rendered"),
    [
        (None, "NoneType", "None"),
        (7, "int", "7"),
        (["bad"], "list", "['bad']"),
        ({"patch": "bad"}, "dict", "{'patch': 'bad'}"),
    ],
)
def test_log_failure_records_non_text_mutation_payload_schema(payload, payload_type, rendered):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = _p(fitness=-0.4)
    child.evaluation = {"is_valid": False, "error": "mutation rejected"}

    record = db.log_failure(child, parent, payload, "non_text_mutation_payload")

    assert record["mutation_text"] == rendered
    assert record["mutation_payload_type"] == payload_type
    assert record["mutation_payload_text"] is False
    assert record["diff_error"] == "non_text_mutation_payload"
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert records[0]["mutation_payload_type"] == payload_type
    assert records[0]["mutation_payload_text"] is False


def test_log_failure_redacts_persisted_snippets_and_evaluator_summaries():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = _p(fitness=-0.4)
    child.evaluation = {
        "is_valid": False,
        "error": "api_key=sk-proj_failure_error_secret_1234567890",  # pragma: allowlist secret
        "stdout": "token=ghp_abcdefghijklmnopqrstuvwxyz123456",
        "stderr": "Authorization: Bearer hf_abcdefghijklmnopqrstuvwxyz",
        "stages": [
            {
                "name": "validate",
                "passed": False,
                "score": 0.0,
                "error": "password=sk-proj_stage_error_secret_1234567890",  # pragma: allowlist secret
            }
        ],
        "metadata": {
            "llm_feedback": [
                {
                    "name": "reviewer",
                    "score": 0.1,
                    "normalized_score": 0.1,
                    "discard": True,
                    "error": "llm_feedback_discard",
                    "feedback": "reject api_key=sk-proj_feedback_failure_secret_1234567890",  # pragma: allowlist secret
                    "raw_response": '{"score": 0.1, "feedback": "reject"}',
                    "feedback_retention": {
                        "retention_mode": "redacted",
                        "sha256": "a" * 64,
                        "chars": 57,
                        "stored_chars": 17,
                    },
                    "llm_call": {
                        "call_id": "call-1",
                        "role": "feedback:reviewer",
                        "backend_idx": 0,
                        "provider_attempts": 1,
                        "total_tokens": 12,
                        "latency_sec": 0.5,
                    },
                }
            ]
        },
    }
    mutation = "mutate token sk-proj-mutationsecret1234567890\nprint(1)"  # pragma: allowlist secret

    record = db.log_failure(child, parent, mutation, "diff token=ghp_diffsecret1234567890")  # pragma: allowlist secret

    persisted = json.loads(
        (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()[0]
    )
    serialized = json.dumps(persisted, sort_keys=True)
    assert "sk-proj_failure_error_secret_1234567890" not in serialized
    assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in serialized
    assert "hf_abcdefghijklmnopqrstuvwxyz" not in serialized
    assert "sk-proj_stage_error_secret_1234567890" not in serialized
    assert "sk-proj_feedback_failure_secret_1234567890" not in serialized
    assert "sk-proj-mutationsecret1234567890" not in serialized
    assert "ghp_diffsecret1234567890" not in serialized
    assert serialized.count("[REDACTED]") >= 5
    feedback = persisted["evaluation"]["llm_feedback"][0]
    assert feedback["name"] == "reviewer"
    assert feedback["score"] == 0.1
    assert feedback["normalized_score"] == 0.1
    assert feedback["discard"] is True
    assert feedback["feedback"] == "reject api_key=[REDACTED]"
    assert feedback["raw_response"] == '{"score": 0.1, "feedback": "reject"}'
    assert feedback["retention"]["feedback_retention"]["sha256"] == "a" * 64
    assert feedback["llm_call"]["role"] == "feedback:reviewer"
    assert feedback["llm_call"]["total_tokens"] == 12
    assert persisted["mutation_sha256"]
    assert record == persisted
    assert child.metadata["failure_record"] == persisted
    prompt = PromptSampler().build(
        parent,
        [],
        _problem(),
        extra_context="",
        recent_failures=[persisted],
    )
    assert "sk-proj-mutationsecret1234567890" not in prompt
    assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in prompt
    assert "sk-proj_feedback_failure_secret_1234567890" not in prompt
    assert "llm_feedback=" in prompt
    assert 'name="reviewer"' in prompt
    assert "[REDACTED]" in prompt


def test_log_failure_writes_archive_admission_when_available():
    db = _db()
    parent = _p(fitness=1.0)
    child = Program(
        files={"main.py": "x=2\n"},
        primary_file="main.py",
        parent_id=parent.id,
        fitness=-0.1,
        evaluation={"is_valid": True},
    )
    admission = db.admit(child, threshold=0.0)

    record = db.log_failure(child, parent, "bad diff", None, admission)

    assert record["admission_reason"] == "below_threshold"
    assert record["archive_admission"]["threshold"] == 0.0
    assert child.metadata["failure_record"]["admission_reason"] == "below_threshold"


def test_log_failure_preserves_invalid_candidate_with_malformed_metrics():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(code="x=1", fitness=1.0)
    db.admit(parent)
    child = _p(code="x=2", fitness=-1.0)
    child.evaluation = {"is_valid": False, "error": "domain_invalid"}
    child.metrics = {"score": "bad"}
    admission = db.admit(child, threshold=0.0)

    record = db.log_failure(child, parent, "bad diff", "domain_invalid", admission)

    assert admission["reason"] == "invalid_evaluation"
    assert record["admission_reason"] == "invalid_evaluation"
    assert record["archive_admission"]["reason"] == "invalid_evaluation"
    assert child.metadata["failure_record"]["admission_reason"] == "invalid_evaluation"
    persisted = json.loads(
        (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()[0]
    )
    assert persisted["archive_admission"]["reason"] == "invalid_evaluation"


def test_log_failure_counts_repetitions():
    db = _db()
    parent = _p(fitness=1.0)
    first_child = Program(id="failed-1", code="x=1", fitness=-0.4)
    second_child = Program(id="failed-2", code="x=1", fitness=-0.4)
    first = db.log_failure(first_child, parent, "bad diff", "no_diff_blocks")
    second = db.log_failure(second_child, parent, "bad diff", "no_diff_blocks")
    assert first["repetition_count"] == 1
    assert second["repetition_count"] == 2


def test_failure_index_snapshot_groups_repeated_failure_fingerprints():
    db = _db()
    parent = Program(
        id="parent",
        files={"main.py": "from helper import value\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
        fitness=1.0,
    )
    first_child = Program(
        id="failed-1",
        files={"main.py": "from helper import value\n", "helper.py": "value = 0\n"},
        primary_file="main.py",
        parent_id=parent.id,
        generation=1,
        fitness=-0.4,
        evaluation={
            "is_valid": False,
            "error": "wrong answer",
            "stdout": "bad output",
            "stages": [{"error": "stage failed"}],
        },
    )
    second_child = Program(
        id="failed-2",
        files={"main.py": "from helper import value\n", "helper.py": "value = 0\n"},
        primary_file="main.py",
        parent_id=parent.id,
        generation=2,
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "wrong answer"},
    )
    first = db.log_failure(first_child, parent, "bad diff", "no_diff_blocks")
    second = db.log_failure(second_child, parent, "bad diff", "no_diff_blocks")

    snapshot = db.failure_index_snapshot()

    assert snapshot["schema"] == "libreevolve.failure_index.v1"
    assert snapshot["policy"] == "failure_records_grouped_by_fingerprint_repetition_and_recency"
    assert snapshot["failure_record_count"] == 2
    assert snapshot["fingerprint_count"] == 1
    assert snapshot["retained_fingerprint_count"] == 1
    [fingerprint] = snapshot["fingerprints"]
    assert fingerprint["fingerprint_sha256"] == first["failure_fingerprint"]["sha256"]
    assert fingerprint["fingerprint_sha256"] == second["failure_fingerprint"]["sha256"]
    assert fingerprint["occurrence_count"] == 2
    assert fingerprint["max_repetition_count"] == 2
    assert fingerprint["changed_files"] == ["helper.py"]
    assert fingerprint["latest_record"]["program_id"] == second_child.id
    assert fingerprint["latest_record"]["repetition_count"] == 2
    assert fingerprint["records"][1]["program_id"] == first_child.id
    assert fingerprint["records"][1]["evaluation"]["stage_errors"] == [
        "stage failed"
    ]
    assert snapshot["limitations"] == [
        "runtime_manifest_failure_index_not_cross_run_database_table",
        "groups_by_failure_fingerprint_without_semantic_similarity",
        "retains_bounded_records_per_fingerprint",
        "rebuilt_from_current_runtime_failure_records",
    ]


def test_log_failure_quarantines_duplicate_failed_program_ids():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    first_child = Program(id="dupchild", code="x=2", fitness=-0.4)
    second_child = Program(id="dupchild", code="x=3", fitness=-0.5)

    db.log_failure(first_child, parent, "bad diff", "no_diff_blocks")
    with pytest.raises(StrictJsonlError, match="duplicate failed program id 'dupchild'"):
        db.log_failure(second_child, parent, "other diff", "different")

    run_dir = Path(tmpdir) / "t"
    assert len((run_dir / "failure_history.jsonl").read_text().splitlines()) == 1
    quarantine = (run_dir / "failure_history_invalid.jsonl").read_text()
    assert "duplicate failed program id 'dupchild'" in quarantine


def test_log_failure_repetition_key_uses_full_mutation_fingerprint():
    db = _db()
    parent = _p(fitness=1.0)
    child_a = _p(code="x=2", fitness=-0.4)
    child_a.parent_id = parent.id
    child_a.evaluation = {"is_valid": False, "error": "same"}
    child_b = _p(code="x=2", fitness=-0.4)
    child_b.parent_id = parent.id
    child_b.evaluation = {"is_valid": False, "error": "same"}
    mutation_a = "x" * 500 + "a"
    mutation_b = "x" * 500 + "b"

    first = db.log_failure(child_a, parent, mutation_a, "no_diff_blocks")
    second = db.log_failure(child_b, parent, mutation_b, "no_diff_blocks")

    assert first["mutation_text"] != second["mutation_text"]
    assert first["mutation_sha256"] != second["mutation_sha256"]
    assert first["failure_fingerprint"]["sha256"] != second["failure_fingerprint"]["sha256"]
    assert first["repetition_count"] == 1
    assert second["repetition_count"] == 1


def test_log_failure_repetition_key_separates_parent_error_and_changed_files():
    db = _db()
    parent_a = Program(id="parent-a", code="x=1", fitness=1.0)
    parent_b = Program(id="parent-b", code="x=1", fitness=1.0)
    base_child = Program(
        id="child-base",
        code="x=2",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "same"},
    )

    first = db.log_failure(base_child, parent_a, "bad diff", "no_diff_blocks")
    parent_child = Program(
        id="child-parent",
        code="x=2",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "same"},
    )
    parent_changed = db.log_failure(parent_child, parent_b, "bad diff", "no_diff_blocks")
    error_changed = Program(
        id="child-error",
        code="x=2",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "different"},
    )
    error_record = db.log_failure(error_changed, parent_a, "bad diff", "no_diff_blocks")
    files_changed = Program(
        id="child-files",
        files={"main.py": "x=2", "helper.py": "value = 1"},
        primary_file="main.py",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "same"},
    )
    files_record = db.log_failure(files_changed, parent_a, "bad diff", "no_diff_blocks")

    assert first["repetition_count"] == 1
    assert parent_changed["repetition_count"] == 1
    assert error_record["repetition_count"] == 1
    assert files_record["repetition_count"] == 1
    fingerprints = {
        first["failure_fingerprint"]["sha256"],
        parent_changed["failure_fingerprint"]["sha256"],
        error_record["failure_fingerprint"]["sha256"],
        files_record["failure_fingerprint"]["sha256"],
    }
    assert len(fingerprints) == 4


def test_log_seed_failure_writes_queryable_seed_record():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    helper_code = "value = 12345\n"
    seed = Program(
        files={"main.py": "from helper import value\n", "helper.py": helper_code},
        primary_file="main.py",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed", "stdout": "nope"},
    )
    admission = db.admit(seed, threshold=0.0)

    record = db.log_seed_failure(seed, admission)

    assert record["record_type"] == "seed"
    assert record["parent_id"] is None
    assert record["admission_reason"] == "invalid_evaluation"
    assert record["changed_files"] == ["helper.py", "main.py"]
    assert record["file_deltas"] == [
        {"path": "helper.py", "change": "seed"},
        {"path": "main.py", "change": "seed"},
    ]
    assert record["failure_fingerprint"]["schema"] == "failure_fingerprint_v1"
    assert record["failure_fingerprint"]["record_type"] == "seed"
    assert record["failure_fingerprint"]["parent_id"] is None
    assert record["failure_fingerprint"]["mutation_sha256"] == record["mutation_sha256"]
    assert record["failure_fingerprint"]["changed_files"] == ["helper.py", "main.py"]
    assert len(record["failure_fingerprint"]["sha256"]) == 64
    assert record["mutation_text"].startswith("[initial seed workspace]")
    assert "--- helper.py (support) ---" in record["mutation_text"]
    assert helper_code.strip() in record["mutation_text"]
    assert record["seed_workspace"]["primary_file"] == "main.py"
    assert record["seed_workspace"]["file_count"] == 2
    assert record["seed_workspace"]["files"] == [
        {
            "path": "helper.py",
            "role": "support",
            "bytes": len(helper_code.encode("utf-8")),
            "sha256": hashlib.sha256(helper_code.encode("utf-8")).hexdigest(),
            "snippet": helper_code,
            "snippet_truncated": False,
        },
        {
            "path": "main.py",
            "role": "primary",
            "bytes": len("from helper import value\n".encode("utf-8")),
            "sha256": hashlib.sha256(
                "from helper import value\n".encode("utf-8")
            ).hexdigest(),
            "snippet": "from helper import value\n",
            "snippet_truncated": False,
        },
    ]
    assert seed.metadata["failure_record"]["record_type"] == "seed"
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert records[0]["evaluation"]["stdout"] == "nope"
    assert records[0]["seed_workspace"] == record["seed_workspace"]


def test_log_seed_failure_quarantines_duplicate_failed_program_ids():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    first = Program(
        id="seed-dup",
        code="x=1",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed"},
    )
    second = Program(
        id="seed-dup",
        code="x=2",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "different seed"},
    )
    first_admission = db.admit(first, threshold=0.0)
    second_admission = db.admit(second, threshold=0.0)

    db.log_seed_failure(first, first_admission)
    with pytest.raises(StrictJsonlError, match="duplicate failed program id 'seed-dup'"):
        db.log_seed_failure(second, second_admission)

    run_dir = Path(tmpdir) / "t"
    assert len((run_dir / "failure_history.jsonl").read_text().splitlines()) == 1
    quarantine = (run_dir / "failure_history_invalid.jsonl").read_text()
    assert "duplicate failed program id 'seed-dup'" in quarantine


def test_log_seed_failure_preserves_invalid_seed_with_malformed_metrics():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = _p(fitness=-1.0)
    seed.evaluation = {"is_valid": False, "error": "domain_invalid"}
    seed.metrics = {"score": "bad"}
    admission = db.admit(seed, threshold=0.0)

    record = db.log_seed_failure(seed, admission)

    assert admission["reason"] == "invalid_evaluation"
    assert record["admission_reason"] == "invalid_evaluation"
    assert seed.metadata["failure_record"]["admission_reason"] == "invalid_evaluation"


def test_log_seed_failure_redacts_seed_code_and_evaluator_summaries():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = Program(
        files={
            "main.py": 'OPENAI_API_KEY="sk-proj_seed_code_secret_1234567890"\n',  # pragma: allowlist secret
            "helper.py": 'token="ghp_seed_helper_secret_1234567890"\n',
        },
        primary_file="main.py",
        fitness=-1.0,
        evaluation={
            "is_valid": False,
            "error": "secret=sk-proj_seed_error_secret_1234567890",  # pragma: allowlist secret
            "stdout": "token=ghp_seedstdoutsecret1234567890",
            "stderr": "api_key=sk-proj_seed_stderr_secret_1234567890",  # pragma: allowlist secret
            "stages": [
                {
                    "name": "validate",
                    "passed": False,
                    "score": 0.0,
                    "error": "token=ghp_seedstagesecret1234567890",
                }
            ],
        },
    )
    admission = db.admit(seed, threshold=0.0)

    record = db.log_seed_failure(seed, admission)

    persisted = json.loads(
        (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()[0]
    )
    serialized = json.dumps(persisted, sort_keys=True)
    assert "sk-proj_seed_code_secret_1234567890" not in serialized
    assert "sk-proj_seed_error_secret_1234567890" not in serialized
    assert "ghp_seedstdoutsecret1234567890" not in serialized
    assert "sk-proj_seed_stderr_secret_1234567890" not in serialized
    assert "ghp_seedstagesecret1234567890" not in serialized
    assert "ghp_seed_helper_secret_1234567890" not in serialized
    assert persisted["seed_workspace"]["files"][0]["snippet"] == 'token="[REDACTED]"\n'
    assert serialized.count("[REDACTED]") >= 6
    assert persisted["mutation_sha256"]
    assert record == persisted
    assert seed.metadata["failure_record"] == persisted


def test_log_rejects_non_finite_records_with_quarantine():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    p = _p(fitness=1.0)
    p.fitness = math.inf
    with pytest.raises(StrictJsonlError):
        db.log(p)
    assert db.all_programs() == []
    assert not (Path(tmpdir)/"t"/"history.jsonl").exists()
    quarantine = Path(tmpdir)/"t"/"history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "inf" in record["message"]


@pytest.mark.parametrize("fitness", [True, False, "1.0"])
def test_log_rejects_invalid_fitness_types_with_quarantine(fitness):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    p = _p(fitness=1.0)
    p.fitness = fitness

    with pytest.raises(StrictJsonlError, match="fitness must be a finite"):
        db.log(p)

    assert db.all_programs() == []
    assert not (Path(tmpdir)/"t"/"history.jsonl").exists()
    quarantine = Path(tmpdir)/"t"/"history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "fitness must be a finite" in record["message"]


def test_log_failure_uses_failure_history_quarantine():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = _p(fitness=1.0)
    child.fitness = math.inf
    with pytest.raises(StrictJsonlError):
        db.log_failure(child, parent, "bad diff", "no_diff_blocks")
    run_dir = Path(tmpdir) / "t"
    assert not (run_dir / "failure_history.jsonl").exists()
    assert not (run_dir / "history_invalid.jsonl").exists()
    quarantine = run_dir / "failure_history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "inf" in record["message"]
    assert "failure_record" not in child.metadata
    assert db._failure_counts == {}


def test_log_failure_normalizes_rejected_non_finite_score_with_admission():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    db.admit(parent)
    child = _p(code="x=2", fitness=1.0)
    child.fitness = math.inf
    child.metrics = {"score": math.inf}
    child.evaluation = {"is_valid": False, "error": "domain_invalid"}
    admission = db.admit(child, threshold=0.0)

    record = db.log_failure(child, parent, "bad diff", "domain_invalid", admission)

    run_dir = Path(tmpdir) / "t"
    assert admission["reason"] == "invalid_evaluation"
    assert admission["selection_score"] is None
    assert record["score"] is None
    assert record["score_diagnostic"] == {
        "reason": "non_finite_or_invalid_number",
        "value_type": "float",
        "value_repr": "inf",
    }
    assert record["evaluation"]["fitness"] is None
    assert record["evaluation"]["fitness_diagnostic"] == {
        "reason": "non_finite_or_invalid_number",
        "value_type": "float",
        "value_repr": "inf",
    }
    assert record["archive_admission"]["reason"] == "invalid_evaluation"
    persisted = json.loads((run_dir / "failure_history.jsonl").read_text())
    assert persisted == record
    assert not (run_dir / "failure_history_invalid.jsonl").exists()


def test_log_failure_failed_append_does_not_advance_repetition_count():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = _p(fitness=-0.4)

    with pytest.raises(StrictJsonlError):
        db.log_failure(child, parent, "bad diff", {"bad": {1, 2}})

    assert "failure_record" not in child.metadata
    assert db._failure_counts == {}

    record = db.log_failure(child, parent, "bad diff", "no_diff_blocks")

    assert record["repetition_count"] == 1
    assert child.metadata["failure_record"]["repetition_count"] == 1


@pytest.mark.parametrize("stages", [{"name": "bad"}, "bad", 1])
def test_log_failure_tolerates_malformed_evaluation_stages(stages):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = Program(
        code="x=1",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "bad", "stages": stages},
    )

    record = db.log_failure(child, parent, "bad diff", "no_diff_blocks")

    assert record["evaluation"]["stages"] == []
    assert record["evaluation"]["stages_diagnostic"]["reason"] == "malformed_stages"
    assert record["evaluation"]["stages_diagnostic"]["actual_type"] == type(stages).__name__
    persisted = json.loads(
        (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()[0]
    )
    assert persisted["evaluation"]["stages_diagnostic"]["reason"] == "malformed_stages"


def test_log_failure_skips_malformed_stage_entries_with_diagnostic():
    db = _db()
    parent = _p(fitness=1.0)
    child = Program(
        code="x=1",
        fitness=-0.4,
        evaluation={
            "is_valid": False,
            "stages": [
                {"name": "syntax", "passed": False, "score": -0.2, "error": "bad"},
                "bad-stage",
            ],
        },
    )

    record = db.log_failure(child, parent, "bad diff", "no_diff_blocks")

    assert record["evaluation"]["stages"] == [
        {"name": "syntax", "passed": False, "score": -0.2, "error": "bad"}
    ]
    assert record["evaluation"]["stages_diagnostic"] == {
        "reason": "malformed_stage_entries",
        "skipped_count": 1,
    }


def test_log_seed_failure_failed_append_does_not_mutate_metadata_or_counts():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = Program(
        files={"main.py": "x=1\n"},
        primary_file="main.py",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed"},
    )
    bad_admission = {"reason": "invalid_evaluation", "bad": {1, 2}}

    with pytest.raises(StrictJsonlError):
        db.log_seed_failure(seed, bad_admission)

    assert "failure_record" not in seed.metadata
    assert db._failure_counts == {}

    record = db.log_seed_failure(seed, {"reason": "invalid_evaluation"})

    assert record["repetition_count"] == 1
    assert seed.metadata["failure_record"]["repetition_count"] == 1


@pytest.mark.parametrize("evaluation", [[], {"bad": object()}])
def test_log_seed_failure_revalidates_mutated_program_evaluation_before_side_effects(evaluation):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = Program(
        files={"main.py": "x=1\n"},
        primary_file="main.py",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed"},
    )
    seed.evaluation = evaluation

    with pytest.raises(ValueError, match="Program evaluation"):
        db.log_seed_failure(seed, {"reason": "invalid_evaluation"})

    assert "failure_record" not in seed.metadata
    assert db._failure_counts == {}
    assert not (Path(tmpdir) / "t" / "failure_history.jsonl").exists()


def test_log_seed_failure_tolerates_malformed_evaluation_stages():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = Program(
        files={"main.py": "x=1\n"},
        primary_file="main.py",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed", "stages": {"name": "bad"}},
    )

    record = db.log_seed_failure(seed, {"reason": "invalid_evaluation"})

    assert record["evaluation"]["stages"] == []
    assert record["evaluation"]["stages_diagnostic"] == {
        "reason": "malformed_stages",
        "expected": "list",
        "actual_type": "dict",
    }


def test_database_rejects_programs_exceeding_configured_workspace_budget():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t", max_candidate_total_chars=5)
    )
    program = Program(code="x = 1\n", fitness=1.0, metrics={"score": 1.0})

    with pytest.raises(ValueError, match="max_candidate_total_chars"):
        db.admit(program)


def test_database_rejects_programs_exceeding_configured_static_workspace_budget():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t", max_candidate_static_file_bytes=3)
    )
    program = Program(
        code="x = 1\n",
        fitness=1.0,
        metrics={"score": 1.0},
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 4}
        ],
    )

    with pytest.raises(ValueError, match="max_candidate_static_file_bytes"):
        db.admit(program)


def test_secret_like_artifact_selectors_fail_before_manifest_write(tmp_path):
    with pytest.raises(ConfigError, match="manifest-safe glob patterns"):
        Config(
            log_dir=tmp_path,
            problem_name="t",
            evaluator_artifact_include=[
                "api_key=sk-proj_ARTIFACT_INCLUDE_SECRET_1234567890/*.txt"  # pragma: allowlist secret
            ],
        )

    assert not (tmp_path / "t" / "manifest.json").exists()


def test_path_unsafe_artifact_selectors_fail_before_manifest_write(tmp_path):
    with pytest.raises(ConfigError, match="path-safe glob patterns"):
        Config(
            log_dir=tmp_path,
            problem_name="t",
            evaluator_artifact_include=["../secret/*.txt"],
        )

    assert not (tmp_path / "t" / "manifest.json").exists()


def test_manifest_requires_objective_schema_before_write():
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(ValueError, match="objective_schema is required"):
        _ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


@pytest.mark.parametrize(
    ("schema", "message"),
    [
        ({}, "missing required fields"),
        (
            {
                "metrics": [
                    {
                        "name": "is_valid",
                        "direction": "sideways",
                        "primary": "yes",
                        "bounds": [1.0, 0.0],
                    }
                ],
                "primary_metric": "missing",
                "primary_bounds": [1.0, 0.0],
                "metric_count": 99,
            },
            "direction|reserved|primary_metric|primary must be boolean|bounds",
        ),
        (
            {
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0.0, 1.0],
                    }
                ],
                "primary_metric": "score",
                "primary_bounds": [1.0, 2.0],
                "metric_count": 1,
            },
            "primary_bounds must match",
        ),
        (
            {
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [False, True],
                    }
                ],
                "primary_metric": "score",
                "primary_bounds": [0.0, 1.0],
                "metric_count": 1,
            },
            "bounds must be numeric",
        ),
        (
            {
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0.0, 1.0],
                    }
                ],
                "primary_metric": "score",
                "primary_bounds": [False, True],
                "metric_count": 1,
            },
            "primary_bounds must be numeric",
        ),
        (
            {
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0.0, 1.0],
                    }
                ],
                "primary_metric": "score",
                "primary_bounds": [0.0, 1.0],
                "metric_count": 2,
            },
            "metric_count must match",
        ),
    ],
)
def test_manifest_rejects_invalid_objective_schema_before_write(schema, message):
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(ValueError, match=message):
        _ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t"),
            objective_schema=schema,
        )

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_manifest_normalizes_objective_schema_at_database_boundary():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        objective_schema={
            "metrics": [
                {
                    "name": "quality",
                    "direction": "maximize",
                    "bounds": (0, 10),
                },
                {
                    "name": "runtime_ms",
                    "direction": "minimize",
                    "primary": True,
                    "bounds": [0, 100],
                },
            ],
            "primary_metric": "runtime_ms",
            "primary_bounds": (0, 100),
            "metric_count": 2,
        },
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["objective_schema"] == {
        "metrics": [
            {
                "name": "quality",
                "direction": "maximize",
                "bounds": [0.0, 10.0],
                "primary": False,
                "source": "evaluator",
                "weight": 1.0,
            },
            {
                "name": "runtime_ms",
                "direction": "minimize",
                "primary": True,
                "bounds": [0.0, 100.0],
                "source": "evaluator",
                "weight": 1.0,
            },
        ],
        "primary_metric": "runtime_ms",
        "primary_bounds": [0.0, 100.0],
        "metric_count": 2,
    }


def test_manifest_does_not_persist_secret_like_log_dir(tmp_path):
    secret = "sk-proj_LOGDIRSECRET_1234567890"
    log_dir = tmp_path / f"api_key={secret}" / "runs"

    ProgramDatabase(Config(log_dir=str(log_dir), problem_name="t"))

    manifest_text = (log_dir / "t" / "manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    assert secret not in manifest_text
    assert str(log_dir) not in manifest_text
    assert manifest["config"]["log_dir"] == "<absolute-log-dir>"
    assert manifest["config"]["log_dir_metadata"]["reason"] == "absolute_path"
    assert manifest["config"]["log_dir_metadata"]["sha256"]


def test_manifest_keeps_safe_relative_log_dir():
    tmpdir = tempfile.mkdtemp()
    cwd = Path.cwd()
    try:
        os.chdir(tmpdir)
        ProgramDatabase(Config(log_dir="runs", problem_name="t"))
        manifest = json.loads((Path("runs") / "t" / "manifest.json").read_text())
    finally:
        os.chdir(cwd)

    assert manifest["config"]["log_dir"] == "runs"
    assert manifest["config"]["log_dir_metadata"]["redacted"] is False
    assert manifest["config"]["log_dir_metadata"]["reason"] == "as_configured"


def test_manifest_writes_valid_seed_source_provenance():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        seed_sources=[
            {
                "seed_index": 0,
                "seed_source_kind": "file",
                "seed_source_path": "initial_programs/seed.py",
                "primary_file": "seed.py",
                "file_count": 1,
                "files": ["seed.py"],
            }
        ],
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["seed_sources"] == [
        {
            "seed_index": 0,
            "seed_source_kind": "file",
            "seed_source_path": "initial_programs/seed.py",
            "primary_file": "seed.py",
            "file_count": 1,
            "files": ["seed.py"],
        }
    ]
    assert manifest["problem"]["seed_skipped"] == []


def _accepted_history_row(program_id: str, fitness: float = 1.0, **extra) -> dict:
    row = {
        "id": program_id,
        "code": "x=1\n",
        "fitness": fitness,
        "generation": 0,
        "metrics": {"score": fitness},
        "evaluation": {"is_valid": True},
    }
    row.update(extra)
    return row


def _write_accepted_history(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def _archive_state_snapshot() -> dict:
    return {
        "schema": "libreevolve.island_state.v1",
        "resume_status": "snapshot_persisted_cursor_restore_available_full_archive_restore_not_implemented",
        "cursor_policy": "advance_only_on_search_state_changed",
        "n_islands": 2,
        "next_island_id": 1,
        "archive_sequence": 3,
        "migration_sequence": 1,
        "metric_sample_index": 2,
        "frontier_sample_index": 4,
        "archive_sequence_by_program_id": {"p1": 1, "p2": 3},
        "islands": [
            {
                "island_id": 0,
                "occupied_cell_count": 1,
                "elite_count": 2,
                "pareto_frontier_count": 0,
                "metric_cell_archive_count": 0,
            },
            {
                "island_id": 1,
                "occupied_cell_count": 0,
                "elite_count": 0,
                "pareto_frontier_count": 0,
                "metric_cell_archive_count": 0,
            },
        ],
    }


def _archive_state_snapshot_with_contents(
    *,
    island0_cells: list[dict] | None = None,
    island1_cells: list[dict] | None = None,
) -> dict:
    snapshot = _archive_state_snapshot()
    snapshot["resume_status"] = "snapshot_persisted_cursor_and_full_archive_restore_supported"
    snapshot["archive_contents"] = {
        "schema": "libreevolve.island_archive_contents.v1",
        "restore_status": "snapshot_persisted_full_archive_restore_supported",
        "islands": [
            {"island_id": 0, "archive": _map_elites_snapshot(island0_cells or [])},
            {"island_id": 1, "archive": _map_elites_snapshot(island1_cells or [])},
        ],
    }
    return snapshot


def _map_elites_snapshot(cells: list[dict]) -> dict:
    return {
        "schema": "libreevolve.map_elites_state.v1",
        "bins": 10,
        "elite_archive_size": 50,
        "perf_bounds": [0.0, 1.0],
        "complexity_max_chars": 100000,
        "descriptor_axes": ["performance", "complexity", "diversity"],
        "cells": cells,
        "elite_program_ids": [cell["program_id"] for cell in cells],
        "descriptor_policy": {
            "schema": "libreevolve.map_elites_descriptor_policy.v1",
            "axes": ["performance", "complexity", "diversity"],
            "performance": "selection_score_normalized_by_fixed_perf_bounds",
            "complexity": "workspace_descriptor_chars_clamped_to_configured_bound",
            "diversity": "tfidf_char_ngram_distance_to_current_elite_archive",
            "metric": "normalized_metrics_axis_else_raw_metric_clamped_to_unit_interval",
            "evaluation_metadata": "numeric_evaluation_metadata_path_clamped_to_unit_interval",
            "candidate_metadata": "numeric_candidate_metadata_path_clamped_to_unit_interval",
            "diversity_reference_program_ids": [],
            "diversity_update_policy": "reference_updates_after_search_state_change",
            "rebin_policy": "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots",
        },
        "descriptor_model": {
            "schema": "libreevolve.map_elites_descriptor_model.v1",
            "revision": 0,
            "revision_policy": "increments_on_search_state_change",
            "axes": ["performance", "complexity", "diversity"],
            "performance_bounds": [0.0, 1.0],
            "complexity_max_chars": 100000,
            "diversity_reference_program_ids": [],
            "dynamic_diversity_reference": True,
            "rebin_policy": "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots",
        },
    }


def _archive_event_row(program_id: str = "p1", **extra) -> dict:
    row = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "record_schema": ARCHIVE_EVENT_RECORD_SCHEMA,
        "event_type": "migration",
        "migration_sequence": 1,
        "program_id": program_id,
        "canonical_program_id": program_id,
        "source_island": 0,
        "target_island": 1,
        "identity_policy": "canonical_id_reference",
        "clone_id": None,
        "admitted": True,
        "reason": "empty_cell",
        "cell": [0, 1, 2],
        "selection_score": 0.5,
        "objective_vector": {
            "policy": "normalized_declared_metric_vector_v1",
            "normalized_metrics": {"score": 0.5},
            "selection_policy": {
                "type": "mean_normalized_declared_metrics",
                "metrics": ["score"],
            },
        },
    }
    row.update(extra)
    return row


def _archive_admission_event_row(program_id: str = "p1", **extra) -> dict:
    row = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "record_schema": ARCHIVE_EVENT_RECORD_SCHEMA,
        "event_type": "admission",
        "admission_sequence": 1,
        "program_id": program_id,
        "canonical_program_id": program_id,
        "archive_sequence": 1,
        "island_id": 0,
        "admitted": True,
        "reason": "empty_cell",
        "cell": [0, 1, 2],
        "selection_score": 0.5,
        "threshold": 0.0,
        "evaluation_is_valid": True,
        "cell_admitted": True,
        "elite_retained": True,
        "sampling_eligible": True,
        "search_state_changed": True,
        "descriptors": {"performance": 0.5},
        "previous_occupant_id": None,
        "objective_vector": {
            "policy": "normalized_declared_metric_vector_v1",
            "normalized_metrics": {"score": 0.5},
            "selection_policy": {
                "type": "mean_normalized_declared_metrics",
                "metrics": ["score"],
            },
        },
    }
    row.update(extra)
    return row


def _write_archive_events(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def _failure_history_row(program_id: str = "p1", **extra) -> dict:
    mutation_text = extra.pop("mutation_text", "bad mutation")
    mutation_sha256 = extra.pop(
        "mutation_sha256",
        hashlib.sha256(mutation_text.encode("utf-8")).hexdigest(),
    )
    parent_id = extra.pop("parent_id", "parent")
    changed_files = extra.pop("changed_files", ["main.py"])
    payload_text = extra.pop("mutation_payload_text", True)
    payload_type = extra.pop("mutation_payload_type", "str")
    row = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "record_schema": FAILURE_RECORD_SCHEMA,
        "program_id": program_id,
        "parent_id": parent_id,
        "generation": 1,
        "score": None,
        "is_valid": False,
        "error": "mutation_failed",
        "diff_error": "no_diff_blocks",
        "changed_files": changed_files,
        "file_deltas": [{"path": path, "change": "modified"} for path in changed_files],
        "mutation_text": mutation_text,
        "mutation_truncated": False,
        "mutation_sha256": mutation_sha256,
        "mutation_payload_type": payload_type,
        "mutation_payload_text": payload_text,
        "failure_fingerprint": {
            "schema": "failure_fingerprint_v1",
            "record_type": "generated",
            "parent_id": parent_id,
            "diff_error_sha256": hashlib.sha256(b"no_diff_blocks").hexdigest(),
            "evaluator_error_sha256": hashlib.sha256(b"mutation_failed").hexdigest(),
            "mutation_sha256": mutation_sha256,
            "mutation_payload_type": payload_type,
            "mutation_payload_text": payload_text,
            "changed_files": changed_files,
            "file_deltas_sha256": hashlib.sha256(b"file_deltas").hexdigest(),
            "sha256": hashlib.sha256(b"fingerprint").hexdigest(),
        },
        "evaluation": {"is_valid": False, "error": "mutation_failed", "stages": []},
        "repetition_count": 1,
    }
    row.update(extra)
    return row


def _write_failure_history(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def _write_non_jsonl_policy_drift_manifest(path: Path) -> Path:
    schema = run_artifact_schema()
    manifest = {
        "artifact_schema": schema,
        "runtime": {
            "artifacts": {
                name: {
                    "path": artifact["path"],
                    "exists": False,
                    "present": False,
                }
                for name, artifact in schema["non_jsonl_artifacts"].items()
            }
        },
    }
    manifest["runtime"]["artifacts"]["task_specification.json"] = {
        "path": "task_specification.json",
        "exists": True,
        "present": True,
        "kind": "file",
        "hash_scope": "file_bytes",
    }
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def _write_quarantine_policy_drift_manifest(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "artifact_schema": {
                    "quarantine_jsonl_records": run_artifact_schema()[
                        "quarantine_jsonl_records"
                    ],
                },
                "runtime": {},
            }
        ),
        encoding="utf-8",
    )
    (path.parent / "history_invalid.jsonl").write_text(
        json.dumps({"error": "ValueError"}) + "\n",
        encoding="utf-8",
    )
    return path


def _run_artifact_bundle_report_overclaim() -> dict:
    return {
        "schema": "libreevolve.run_artifact_bundle_report.v1",
        "source": "runtime_artifact_schema_pointers_and_quarantine_diagnostics",
        "accepted_stream_count": 0,
        "accepted_streams": [],
        "quarantine_stream_count": 0,
        "quarantine_record_count": 0,
        "quarantine_streams": [],
        "quarantine_validation_ok": True,
        "non_jsonl_checked_artifact_count": 0,
        "non_jsonl_validation_ok": True,
        "paper_artifact_lifecycle_checked": False,
        "paper_artifact_emitted_path_count": 0,
        "paper_artifact_validation_ok": None,
        "issue_codes": [],
        "accepted_state_boundary": {
            "quarantine_rows_are_diagnostics": True,
            "quarantine_rows_replayed_as_state": False,
            "non_jsonl_artifacts_are_policy_checked": True,
            "provider_output_replay": True,
            "pending_controller_work_replay": False,
        },
        "claim_ready": False,
        "claim_readiness": {
            "accepted_streams_counted": True,
            "quarantine_diagnostics_validated": True,
            "non_jsonl_policy_validated": True,
            "paper_artifact_lifecycle_validated": False,
            "persisted_manifest_report": True,
            "full_restore_replay_certification": False,
            "remaining_gap": [],
        },
    }


def _restore_certification_overclaim() -> dict:
    return {
        "schema": "libreevolve.full_resume_restore_certification.v1",
        "status": "compatible_surfaces_certified",
        "scope": "local_manifest_restore_inputs_only",
        "certified_surfaces": [
            "runtime_rng_state_snapshot",
            "runtime_llm_scheduler_state_snapshot",
            "runtime_archive_state_snapshot",
            "runtime_archive_programs_by_id",
            "runtime_budget_state_snapshot",
            "controller_budget_event_replay",
            "lineage_provider_boundary",
            "run_artifact_bundle_report",
        ],
        "run_artifact_bundle_report": {
            "status": "absent",
            "validation_ok": None,
            "promotion_gate_status": None,
        },
        "accepted_quarantine_boundary": {
            "quarantine_rows_replayed_as_state": False,
            "quarantine_rows_are_diagnostics": True,
        },
        "compatible_resume_ready": True,
        "full_replay_ready": False,
        "provider_output_replay_ready": True,
        "pending_work_resume_ready": False,
        "resumed_trace_proof_ready": False,
        "remaining_gap": [
            "provider_output_replay_or_exclusion_in_resumed_trace",
            "pending_controller_work_resume",
            "migration_event_replay_engine",
            "end_to_end_resumed_trace_proof",
        ],
    }


def test_maybe_migrate_triggers_on_interval():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(migration_interval=5, n_islands=2, log_dir=tmpdir, problem_name="t")
    )
    p = _p(); db.log(p); db.add(p)
    # Before interval: island 1 has nothing
    assert db._islands.islands[1].best() is None
    assert db.maybe_migrate(4) == []  # not a multiple of 5 — no migration
    assert db._islands.islands[1].best() is None
    events = db.maybe_migrate(5)  # multiple of 5 — migration fires
    assert db._islands.islands[1].best() is not None
    assert events[0]["program_id"] == p.id
    assert events[0]["identity_policy"] == "canonical_id_reference"
    assert db.best().metadata["migration_placements"] == events
    archive_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "archive_events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    [record] = [
        row for row in archive_records if row.get("event_type") == "migration"
    ]
    [admission_record] = [
        row for row in archive_records if row.get("event_type") == "admission"
    ]
    assert admission_record["program_id"] == p.id
    assert record["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert record["record_schema"] == ARCHIVE_EVENT_RECORD_SCHEMA
    assert record["event_type"] == "migration"
    assert record["program_id"] == p.id
    assert record["migration_sequence"] == events[0]["migration_sequence"]
    assert record["source_island"] == events[0]["source_island"]
    assert record["target_island"] == events[0]["target_island"]
