"""Characterization tests for the YAML parser and loader boundary."""

from pathlib import Path

import pytest
import yaml

from libreevolve.core.yaml_utils import redacted_yaml_error, safe_load_unique
from libreevolve.problems.loader import load_problem


def _make_problem(root: Path) -> Path:
    problem = root / "problem"
    seed_dir = problem / "initial_programs"
    seed_dir.mkdir(parents=True)
    (problem / "task_description.txt").write_text(
        "characterize YAML loading\n",
        encoding="utf-8",
    )
    (problem / "metrics.yaml").write_text(
        "metrics:\n"
        "  - name: score\n"
        "    primary: true\n"
        "    direction: maximize\n"
        "    bounds: [0.0, 1.0]\n",
        encoding="utf-8",
    )
    (problem / "validate.py").write_text(
        "def evaluate(code):\n"
        "    return {'score': 1.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    (seed_dir / "seed.py").write_text("value = 1\n", encoding="utf-8")
    return problem


@pytest.mark.parametrize(
    ("yaml_text", "expected"),
    [
        pytest.param("name: value\n", {"name": "value"}, id="mapping"),
        pytest.param("{}\n", {}, id="empty-mapping"),
        pytest.param("", None, id="empty-document"),
        pytest.param("\n  \n", None, id="whitespace-document"),
        pytest.param("null\n", None, id="null"),
        pytest.param("~\n", None, id="tilde-null"),
        pytest.param("[]\n", [], id="empty-list"),
        pytest.param("- alpha\n- beta\n", ["alpha", "beta"], id="list"),
        pytest.param("false\n", False, id="false"),
        pytest.param("true\n", True, id="true"),
        pytest.param("0\n", 0, id="zero"),
        pytest.param("-7\n", -7, id="negative-integer"),
        pytest.param("3.125\n", 3.125, id="float"),
    ],
)
def test_safe_load_unique_preserves_document_shape_and_scalar_types(
    yaml_text: str,
    expected: object,
):
    loaded = safe_load_unique(yaml_text)

    assert type(loaded) is type(expected)
    assert loaded == expected


def test_safe_load_unique_preserves_unicode_mapping_content():
    loaded = safe_load_unique(
        'greeting: "café 東京 🌱"\n'
        "ключ: значение\n"
    )

    assert loaded == {
        "greeting": "café 東京 🌱",
        "ключ": "значение",
    }


def test_safe_load_unique_rejects_duplicate_keys_with_exact_diagnostic():
    with pytest.raises(yaml.constructor.ConstructorError) as raised:
        safe_load_unique("name: first\nname: second\n")

    expected = (
        "while constructing a mapping\n"
        '  in "<unicode string>", line 1, column 1:\n'
        "    name: first\n"
        "    ^\n"
        "found duplicate key 'name'\n"
        '  in "<unicode string>", line 2, column 1:\n'
        "    name: second\n"
        "    ^"
    )
    assert type(raised.value) is yaml.constructor.ConstructorError
    assert str(raised.value) == expected
    assert redacted_yaml_error(raised.value) == expected


def test_safe_load_unique_rejects_malformed_yaml_with_exact_diagnostic():
    with pytest.raises(yaml.parser.ParserError) as raised:
        safe_load_unique("include: [\n")

    expected = (
        "while parsing a flow node\n"
        "expected the node content, but found '<stream end>'\n"
        '  in "<unicode string>", line 2, column 1:\n'
        "    \n"
        "    ^"
    )
    assert type(raised.value) is yaml.parser.ParserError
    assert str(raised.value) == expected
    assert redacted_yaml_error(raised.value) == expected


@pytest.mark.parametrize(
    ("yaml_text", "problem"),
    [
        pytest.param(
            "*missing_anchor\n",
            "YAML aliases are not supported in setup files",
            id="alias",
        ),
        pytest.param(
            "value: &anchor 1\n",
            "YAML anchors are not supported in setup files",
            id="anchor",
        ),
    ],
)
def test_safe_load_unique_rejects_aliases_and_anchors(
    yaml_text: str,
    problem: str,
):
    with pytest.raises(yaml.constructor.ConstructorError) as raised:
        safe_load_unique(yaml_text)

    assert type(raised.value) is yaml.constructor.ConstructorError
    assert raised.value.problem == problem
    assert str(raised.value).startswith(f"while composing a YAML node\n{problem}\n")


def test_redacted_yaml_error_redacts_secret_in_duplicate_key_diagnostic():
    secret_key = "api_key=sk-proj_yamlsecret1234"  # pragma: allowlist secret

    with pytest.raises(yaml.constructor.ConstructorError) as raised:
        safe_load_unique(f"{secret_key}: one\n{secret_key}: two\n")

    diagnostic = redacted_yaml_error(raised.value)

    assert secret_key not in diagnostic
    assert diagnostic == (
        "while constructing a mapping\n"
        '  in "<unicode string>", line 1, column 1:\n'
        "    api_key=[REDACTED] one\n"
        "    ^\n"
        "found duplicate key 'api_key=[REDACTED]'\n"
        '  in "<unicode string>", line 2, column 1:\n'
        "    api_key=[REDACTED] two\n"
        "    ^"
    )


@pytest.mark.parametrize(
    "yaml_text",
    [
        pytest.param("[]\n", id="list"),
        pytest.param("false\n", id="boolean"),
        pytest.param("0\n", id="numeric"),
        pytest.param("null\n", id="null"),
    ],
)
def test_metrics_loader_rejects_falsey_non_mapping_documents(
    tmp_path: Path,
    yaml_text: str,
):
    problem = _make_problem(tmp_path)
    metrics_path = problem / "metrics.yaml"
    metrics_path.write_text(yaml_text, encoding="utf-8")

    with pytest.raises(ValueError) as raised:
        load_problem(problem)

    expected = (
        f"metrics.yaml in {problem.resolve()} "
        "must contain a top-level 'metrics' list"
    )
    assert type(raised.value) is ValueError
    assert str(raised.value) == expected
    assert raised.value.__cause__ is None


_OPTIONAL_METADATA_BOUNDARIES = (
    ("formulation.yaml", "formulation metadata"),
    ("codebase_integration.yaml", "codebase integration metadata"),
    ("collaborator_feedback.yaml", "collaborator feedback metadata"),
    ("acknowledgements.yaml", "acknowledgement metadata"),
    ("paper_authors.yaml", "paper author metadata"),
    ("title_page.yaml", "title page metadata"),
    ("system_contributions.yaml", "system contribution metadata"),
)


def test_seed_policy_rejects_falsey_non_mapping_documents(tmp_path: Path):
    problem = _make_problem(tmp_path)
    policy_path = problem / "initial_programs" / "seed_policy.yaml"
    policy_path.write_text("false\n", encoding="utf-8")

    with pytest.raises(ValueError) as raised:
        load_problem(problem)

    expected = f"{policy_path.resolve()}: seed policy must be a mapping"
    assert type(raised.value) is ValueError
    assert str(raised.value) == expected
    assert raised.value.__cause__ is None


def test_seed_policy_null_document_is_the_default_policy(tmp_path: Path):
    problem = _make_problem(tmp_path)
    policy_path = problem / "initial_programs" / "seed_policy.yaml"
    policy_path.write_text("null\n", encoding="utf-8")

    loaded = load_problem(problem)

    assert loaded.initial_workspace_policy == {
        "policy": "skip_reserved_seed_paths_by_default",
        "reserved_components": ["dot-prefixed", "__pycache__"],
        "source": "seed_policy.yaml",
        "include": [],
        "exclude": [],
        "exclude_precedence": True,
    }
