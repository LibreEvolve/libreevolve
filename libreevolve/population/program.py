from __future__ import annotations
from collections.abc import Mapping
from dataclasses import dataclass, field
from math import inf, isfinite
from numbers import Real
import re
import unicodedata
from uuid import uuid4
from libreevolve.core.candidate import CandidateWorkspace, validate_workspace_evolve_blocks
from libreevolve.core.redaction import redact_sensitive_text

_METRIC_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){0,7}")
_UNEVALUATED_FITNESS = object()

@dataclass
class Program:
    id:         str           = field(default_factory=lambda: uuid4().hex)
    code:       str           = ""
    fitness:    float         = field(default=_UNEVALUATED_FITNESS)
    generation: int           = 0
    parent_id:  str | None    = None
    lineage:    list[str]     = field(default_factory=list)
    metadata:   dict          = field(default_factory=dict)
    metrics:    dict[str, float | bool | str | int] = field(default_factory=dict)
    evaluation: dict          = field(default_factory=dict)
    files:      dict[str, str] = field(default_factory=dict)
    primary_file: str          = "main.py"
    allowed_reserved_paths: frozenset[str] = field(default_factory=frozenset)
    static_files: tuple[dict[str, str | int], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_program_identity(self.id, self.parent_id, self.lineage)
        if self.fitness is _UNEVALUATED_FITNESS:
            self.fitness = -inf
        elif isinstance(self.fitness, bool) or not isinstance(self.fitness, Real):
            raise ValueError("Program fitness must be numeric")
        elif not isfinite(self.fitness):
            raise ValueError("Program fitness must be finite when provided")
        else:
            self.fitness = float(self.fitness)
        if (
            isinstance(self.generation, bool)
            or not isinstance(self.generation, int)
            or self.generation < 0
        ):
            raise ValueError("Program generation must be a non-negative integer")
        self.metrics = validate_program_metrics(self.metrics)
        self.metadata = validate_program_metadata(self.metadata)
        self.evaluation = validate_program_evaluation(self.evaluation)
        if self.files:
            ws = CandidateWorkspace(
                self.files,
                self.primary_file,
                allowed_reserved_paths=self.allowed_reserved_paths,
                static_files=self.static_files,
            )
        elif self.code and not self.files:
            ws = CandidateWorkspace(
                {self.primary_file: self.code},
                self.primary_file,
                allowed_reserved_paths=self.allowed_reserved_paths,
                static_files=self.static_files,
            )
        else:
            ws = CandidateWorkspace(
                {},
                self.primary_file,
                allowed_reserved_paths=self.allowed_reserved_paths,
                static_files=self.static_files,
            )
        marker_error = validate_workspace_evolve_blocks(ws.files)
        if marker_error is not None:
            raise ValueError(f"Malformed evolve-block markers: {marker_error}")
        self.files = dict(ws.files)
        self.primary_file = ws.primary_file
        self.allowed_reserved_paths = ws.allowed_reserved_paths
        self.static_files = ws.static_files
        self.code = ws.code

    def workspace(self) -> CandidateWorkspace:
        if self.files:
            return CandidateWorkspace(
                self.files,
                self.primary_file,
                allowed_reserved_paths=self.allowed_reserved_paths,
                static_files=self.static_files,
            )
        return CandidateWorkspace(
            {self.primary_file: self.code},
            self.primary_file,
            allowed_reserved_paths=self.allowed_reserved_paths,
            static_files=self.static_files,
        )


def validate_program_metrics(metrics: object) -> dict[str, float | bool | int]:
    if not isinstance(metrics, dict):
        raise ValueError("Program metrics must be a dictionary")
    normalized: dict[str, float | bool | int] = {}
    for name, value in metrics.items():
        _validate_metric_name(name)
        if name == "is_valid":
            if not isinstance(value, bool):
                raise ValueError("Program metric 'is_valid' must be boolean")
            normalized[name] = value
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Program metric values must be JSON-native finite numbers")
        if isinstance(value, float) and not isfinite(value):
            raise ValueError("Program metric values must be JSON-native finite numbers")
        normalized[name] = value
    return normalized


def _validate_metric_name(name: object) -> None:
    if not isinstance(name, str) or not name:
        raise ValueError("Program metric names must be non-empty strings")
    if redact_sensitive_text(name) != name:
        raise ValueError("Program metric names must be manifest-safe metric names")
    if _has_control_character(name):
        raise ValueError("Program metric names must be manifest-safe metric names")
    if _METRIC_NAME_RE.fullmatch(name) is None:
        raise ValueError("Program metric names must be manifest-safe metric names")


def validate_program_metadata(metadata: object, label: str = "Program metadata") -> dict:
    value = _validate_program_metadata_value(metadata, label, root=True)
    assert isinstance(value, dict)
    return value


def validate_program_evaluation(evaluation: object) -> dict:
    if not isinstance(evaluation, Mapping):
        raise ValueError("Program evaluation must be a JSON-safe evaluation mapping")
    value = _validate_program_metadata_value(
        evaluation,
        "Program evaluation",
        root=True,
    )
    assert isinstance(value, dict)
    return value


def _validate_program_metadata_value(
    value: object,
    label: str,
    *,
    root: bool = False,
) -> object:
    if isinstance(value, Mapping):
        normalized: dict = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"{label} keys must be non-empty strings")
            if redact_sensitive_text(key) != key:
                raise ValueError(f"{label} keys must be display-safe metadata labels")
            if _has_control_character(key):
                raise ValueError(f"{label} keys must be display-safe metadata labels")
            normalized[key] = _validate_program_metadata_value(item, f"{label}.{key}")
        return normalized
    if root:
        raise ValueError(f"{label} must be a JSON-safe metadata mapping")
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        if _has_format_control(value):
            raise ValueError(f"{label} must be a display-safe metadata value")
        return redact_sensitive_text(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError(f"{label} must be finite")
        return value
    if isinstance(value, list):
        return [
            _validate_program_metadata_value(item, f"{label}[{index}]")
            for index, item in enumerate(value)
        ]
    raise ValueError(f"{label} must be JSON-safe metadata")


def _has_control_character(value: str) -> bool:
    return any(unicodedata.category(char).startswith("C") for char in value)


def _has_format_control(value: str) -> bool:
    return any(unicodedata.category(char) == "Cf" for char in value)


def validate_program_identity(
    program_id: object,
    parent_id: object | None = None,
    lineage: object | None = None,
) -> None:
    _validate_program_id("Program id", program_id)
    if parent_id is not None:
        _validate_program_id("Program parent_id", parent_id)
    if parent_id == program_id:
        raise ValueError("Program parent_id must not match program id")
    if lineage is None:
        return
    if not isinstance(lineage, list):
        raise ValueError("Program lineage must be a list of manifest-safe identifiers")
    seen: set[str] = set()
    for index, item in enumerate(lineage):
        _validate_program_id(f"Program lineage[{index}]", item)
        assert isinstance(item, str)
        if item == program_id:
            raise ValueError("Program lineage must not contain the program id")
        if item in seen:
            raise ValueError("Program lineage must not contain duplicate ids")
        seen.add(item)
    if parent_id is not None and lineage and lineage[-1] != parent_id:
        raise ValueError("Program lineage tail must match parent_id")


def _validate_program_id(label: str, value: object) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a manifest-safe identifier")
    if redact_sensitive_text(value) != value:
        raise ValueError(f"{label} must be a manifest-safe identifier")
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value) is None:
        raise ValueError(f"{label} must be a manifest-safe identifier")
