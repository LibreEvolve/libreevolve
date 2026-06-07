from decimal import Decimal
from fractions import Fraction
from math import inf
import pytest
from libreevolve.population.program import Program

def test_default_fitness_is_neg_inf():
    assert Program().fitness == -inf


@pytest.mark.parametrize("fitness", [True, False, "1.0", None])
def test_rejects_non_numeric_fitness(fitness):
    with pytest.raises(ValueError, match="Program fitness must be numeric"):
        Program(fitness=fitness)


@pytest.mark.parametrize("fitness", [float("nan"), float("inf"), float("-inf")])
def test_rejects_explicit_non_finite_fitness(fitness):
    with pytest.raises(ValueError, match="Program fitness must be finite when provided"):
        Program(fitness=fitness)


@pytest.mark.parametrize("generation", [True, False, -1, 1.0, "1", None])
def test_rejects_invalid_generation(generation):
    with pytest.raises(
        ValueError, match="Program generation must be a non-negative integer"
    ):
        Program(generation=generation)


def test_accepts_numeric_metrics_and_boolean_is_valid_metric():
    p = Program(
        metrics={
            "score": 1,
            "latency": 0.25,
            "plugin.quality_score": 0.75,
            "is_valid": True,
        }
    )

    assert p.metrics == {
        "score": 1,
        "latency": 0.25,
        "plugin.quality_score": 0.75,
        "is_valid": True,
    }


@pytest.mark.parametrize(
    ("metrics", "message"),
    [
        ([], "Program metrics must be a dictionary"),
        ({1: 0.2}, "Program metric names must be non-empty strings"),
        ({"": 0.2}, "Program metric names must be non-empty strings"),
        ({"api_key=sk-proj_metric_key_secret_1234567890": 0.2}, "manifest-safe metric names"),  # pragma: allowlist secret
        ({"score\u202e": 0.2}, "manifest-safe metric names"),
        ({"cafe\u0301": 0.2}, "manifest-safe metric names"),
        ({"score-secret": 0.2}, "manifest-safe metric names"),
        ({"score.": 0.2}, "manifest-safe metric names"),
        ({"1score": 0.2}, "manifest-safe metric names"),
        ({"score": "bad"}, "Program metric values must be JSON-native finite numbers"),
        ({"score": True}, "Program metric values must be JSON-native finite numbers"),
        ({"score": inf}, "Program metric values must be JSON-native finite numbers"),
        ({"score": Fraction(1, 2)}, "Program metric values must be JSON-native finite numbers"),
        ({"score": Decimal("0.5")}, "Program metric values must be JSON-native finite numbers"),
        ({"is_valid": 1.0}, "Program metric 'is_valid' must be boolean"),
    ],
)
def test_rejects_invalid_metric_vectors(metrics, message):
    with pytest.raises(ValueError, match=message):
        Program(metrics=metrics)


def test_unique_ids():
    assert Program().id != Program().id


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"id": ""}, "Program id"),
        ({"id": "api_key=sk-proj_candidate_secret_1234567890\nnext"}, "Program id"),  # pragma: allowlist secret
        ({"id": "bad id"}, "Program id"),
        ({"id": 7}, "Program id"),
        ({"parent_id": "parent\nnext"}, "Program parent_id"),
        ({"parent_id": "api_key=sk-proj_parent_secret_1234567890"}, "Program parent_id"),  # pragma: allowlist secret
        ({"lineage": "parent"}, "Program lineage"),
        ({"lineage": ["ok", "bad\nid"]}, "Program lineage\\[1\\]"),
        ({"id": "same", "parent_id": "same"}, "Program parent_id must not match program id"),
        ({"id": "child", "lineage": ["root", "child"]}, "Program lineage must not contain the program id"),
        ({"lineage": ["root", "root"]}, "Program lineage must not contain duplicate ids"),
        (
            {"id": "child", "parent_id": "parent", "lineage": ["root", "other"]},
            "Program lineage tail must match parent_id",
        ),
    ],
)
def test_rejects_unsafe_program_identity(kwargs, message):
    with pytest.raises(ValueError, match=message):
        Program(**kwargs)


def test_accepts_manifest_safe_program_identity():
    program = Program(id="candidate-1", parent_id="seed_0", lineage=["root", "seed_0"])

    assert program.id == "candidate-1"
    assert program.parent_id == "seed_0"
    assert program.lineage == ["root", "seed_0"]

def test_fields_set():
    p = Program(code="x = 1", fitness=0.5)
    assert p.code == "x = 1" and p.fitness == 0.5

def test_files_are_canonical_when_code_disagrees():
    p = Program(
        code='x = "legacy"\n',
        files={"main.py": 'x = "workspace"\n', "helper.py": "value = 2\n"},
        primary_file="main.py",
    )

    assert p.code == 'x = "workspace"\n'
    assert p.workspace().code == 'x = "workspace"\n'
    assert p.files["helper.py"] == "value = 2\n"


def test_program_preserves_static_file_metadata():
    p = Program(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 8}
        ],
    )

    assert p.static_files == (
        {
            "path": "fixture.bin",
            "kind": "binary",
            "sha256": "a" * 64,
            "bytes": 8,
            "source_kind": "unknown",
            "mutation_policy": "immutable",
        },
    )
    assert p.workspace().static_files == p.static_files


def test_rejects_secret_like_direct_program_file_paths_without_echoing_value():
    path = "api_key=sk-proj_programfilepathsecret1234567890.py"  # pragma: allowlist secret

    with pytest.raises(ValueError, match="secret-like text") as excinfo:
        Program(files={path: "x = 1\n"}, primary_file=path)

    assert "sk-proj_programfilepathsecret" not in str(excinfo.value)


def test_empty_program_canonicalizes_default_workspace():
    p = Program()

    assert p.code == ""
    assert p.primary_file == "main.py"
    assert p.files == {"main.py": ""}
    assert p.workspace().files == {"main.py": ""}


def test_empty_program_rejects_unsafe_primary_file():
    with pytest.raises(ValueError, match="Unsafe candidate path"):
        Program(primary_file="../escape.py")


def test_lineage_defaults_empty():
    assert Program().lineage == []

def test_metadata_defaults_empty():
    assert Program().metadata == {}


def test_metadata_accepts_nested_json_mapping_and_copies_values():
    secret = "sk-" + "proj-" + "abcdefghijklmnopqrstuvwxyz123456"
    metadata = {
        "source": "seed",
        "café label": "ok",
        "notes": "ordinary café value\nwith multiline prompt text",
        "nested": {"values": [1, 2.5, True, None, f"api_key={secret}"]},
    }

    program = Program(metadata=metadata)
    metadata["nested"]["values"].append("mutated")

    assert program.metadata == {
        "source": "seed",
        "café label": "ok",
        "notes": "ordinary café value\nwith multiline prompt text",
        "nested": {"values": [1, 2.5, True, None, "api_key=[REDACTED]"]},
    }


@pytest.mark.parametrize(
    ("metadata", "message"),
    [
        ([], "Program metadata must be a JSON-safe metadata mapping"),
        ("bad", "Program metadata must be a JSON-safe metadata mapping"),
        ({1: "bad"}, "Program metadata keys must be non-empty strings"),
        ({"": "bad"}, "Program metadata keys must be non-empty strings"),
        (
            {"api_key=sk-proj_metadata_key_secret_1234567890": "value"},  # pragma: allowlist secret
            "Program metadata keys must be display-safe metadata labels",
        ),
        ({"backend\u202emeta": "value"}, "Program metadata keys must be display-safe metadata labels"),
        ({"bad": {"not", "json"}}, "Program metadata.bad must be JSON-safe metadata"),
        ({"bad": object()}, "Program metadata.bad must be JSON-safe metadata"),
        ({"bad": inf}, "Program metadata.bad must be finite"),
        ({"nested": {"bad\nkey": "value"}}, "Program metadata.nested keys"),
        ({"nested": {"value": "bad\u202evalue"}}, "Program metadata.nested.value"),
    ],
)
def test_rejects_invalid_metadata(metadata, message):
    with pytest.raises(ValueError, match=message):
        Program(metadata=metadata)


def test_rejects_format_controls_in_evaluation_metadata_values():
    with pytest.raises(ValueError, match="Program evaluation.metadata.label"):
        Program(
            evaluation={
                "metadata": {
                    "label": "safe prefix\u200dhidden suffix",
                }
            }
        )


def test_program_rejects_malformed_evolve_blocks_in_files():
    with pytest.raises(ValueError, match="helper.py:malformed_evolve_blocks:orphan_end"):
        Program(
            files={"main.py": "x = 1\n", "helper.py": "# EVOLVE-BLOCK-END\n"},
            primary_file="main.py",
        )


def test_program_rejects_malformed_evolve_blocks_in_legacy_code():
    with pytest.raises(ValueError, match="main.py:malformed_evolve_blocks:invalid_name"):
        Program(code="# EVOLVE-BLOCK-START bad name\nx = 1\n# EVOLVE-BLOCK-END\n")
