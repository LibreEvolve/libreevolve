from __future__ import annotations

import contextlib
from email.parser import Parser
import functools
import hashlib
import importlib
import io
import ntpath
import os
from importlib import metadata
import json
import math
import platform
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from types import ModuleType
import tomllib

from packaging.requirements import InvalidRequirement, Requirement

from libreevolve.core.redaction import redact_sensitive_text

_COMMON_EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
_SOURCE_EXCLUDED_DIRS = _COMMON_EXCLUDED_DIRS | {"runs"}
_PROBLEM_EXCLUDED_DIRS = _COMMON_EXCLUDED_DIRS
_RUN_ARTIFACT_MARKER_NAMES = {
    "manifest.json",
    "history.jsonl",
    "history_invalid.jsonl",
    "failure_history.jsonl",
    "failure_history_invalid.jsonl",
    "llm_calls.jsonl",
    "llm_calls_invalid.jsonl",
    "prompt_history.jsonl",
    "prompt_history_invalid.jsonl",
    "best.py",
    "best_workspace",
    "evaluator_artifacts",
    "plugin_artifacts",
}
_TREE_PROVENANCE_MAX_FILE_BYTES = 1_000_000
_PYPROJECT_METADATA_MAX_CHARS = 512
_PYPROJECT_DIAGNOSTIC_MAX_CHARS = 512
_PYPROJECT_EXTRA_METADATA_MAX_KEYS = 50
_PYPROJECT_EXTRA_METADATA_MAX_ITEMS = 50
_PYPROJECT_EXTRA_METADATA_MAX_DEPTH = 4
_LOCKFILE_PROVENANCE_MAX_FILE_BYTES = 5_000_000
_INSTALLED_PACKAGE_SNAPSHOT_MAX_PACKAGES = 2_000
_INSTALLED_PACKAGE_WHEEL_MAX_CHARS = 100_000
_INSTALLED_PACKAGE_WHEEL_MAX_TAGS = 50
_INSTALLED_PACKAGE_SOURCE_MAX_CHARS = 100_000
_INSTALLED_PACKAGE_DIRECT_URL_MAX_KEYS = 50
_NUMERICAL_RUNTIME_CONFIG_MAX_CHARS = 4_000
_PIP_FREEZE_TIMEOUT_SECONDS = 10.0
_PIP_FREEZE_MAX_LINES = 5_000
_PIP_FREEZE_MAX_LINE_CHARS = 1_000
_PIP_CONFIG_TIMEOUT_SECONDS = 10.0
_PIP_CONFIG_MAX_LINES = 500
_PIP_CONFIG_MAX_LINE_CHARS = 1_000
_ACCELERATOR_PROBE_TIMEOUT_SECONDS = 3.0
_ACCELERATOR_PROBE_MAX_LINES = 100
_ACCELERATOR_PROBE_MAX_LINE_CHARS = 1_000
_LOCKFILE_CANDIDATES = (
    "requirements.txt",
    "requirements.lock",
    "uv.lock",
    "poetry.lock",
    "pdm.lock",
    "Pipfile.lock",
)
_LLM_PROVIDER_SDK_CANDIDATES = ()
_ACCELERATOR_ENV_CANDIDATES = (
    "CUDA_VISIBLE_DEVICES",
    "NVIDIA_VISIBLE_DEVICES",
    "CUDA_DEVICE_ORDER",
    "CUDA_HOME",
    "CUDA_PATH",
    "ROCR_VISIBLE_DEVICES",
    "HIP_VISIBLE_DEVICES",
    "ROCM_PATH",
    "ONEAPI_DEVICE_SELECTOR",
    "SYCL_DEVICE_FILTER",
    "DML_VISIBLE_DEVICES",
)
_ACCELERATOR_COMMAND_PROBES = (
    {
        "name": "nvidia_smi",
        "executable": "nvidia-smi",
        "args": [
            "--query-gpu=driver_version,cuda_version,name",
            "--format=csv,noheader",
        ],
    },
    {
        "name": "rocm_smi",
        "executable": "rocm-smi",
        "args": ["--showdriverversion"],
    },
)
_PYPROJECT_PROJECT_SELECTED_KEYS = {
    "name",
    "version",
    "requires-python",
    "license",
    "authors",
    "maintainers",
    "keywords",
    "classifiers",
    "urls",
    "scripts",
    "gui-scripts",
    "entry-points",
    "dependencies",
    "optional-dependencies",
}


def problem_provenance(problem_dir: Path, generated_roots: list[Path] | None = None) -> dict:
    return _tree_provenance(
        problem_dir,
        label="problem",
        excluded_dirs=_PROBLEM_EXCLUDED_DIRS,
        excluded_roots=generated_roots or [],
    )


def source_provenance() -> dict:
    return _tree_provenance(
        Path(__file__).resolve().parents[1],
        label="libreevolve",
        excluded_dirs=_SOURCE_EXCLUDED_DIRS,
        excluded_roots=[],
    )


def runtime_environment_provenance(project_root: Path | None = None) -> dict:
    project_root = project_root or Path(__file__).resolve().parents[2]
    pyproject = project_root / "pyproject.toml"
    package: dict = {"pyproject": _package_pyproject_record(pyproject, project_root)}
    project_metadata: dict = {}
    build_metadata: dict = {}
    dependency_records: list[dict] = []
    if pyproject.is_file() and package["pyproject"].get("status") == "ok":
        loaded = package["pyproject"].pop("_loaded")
        schema_errors = _validate_pyproject_schema(loaded)
        if schema_errors:
            package["pyproject"]["status"] = "invalid_pyproject_schema"
            package["pyproject"]["error_type"] = "InvalidPyprojectSchema"
            package["pyproject"]["errors"] = schema_errors
        else:
            project_section = loaded.get("project", {})
            build_section = loaded.get("build-system", {})
            if isinstance(project_section, dict):
                project_metadata = _pyproject_project_metadata(project_section)
                raw_dependencies = project_section.get("dependencies", [])
                if isinstance(raw_dependencies, list):
                    dependency_records = [_dependency_record(dep) for dep in raw_dependencies]
            if isinstance(build_section, dict):
                build_metadata = _pyproject_build_metadata(build_section)
    package.update(project_metadata)
    installed_version_name = str(project_metadata.get("name") or "libreevolve")
    package["installed_version_name"] = installed_version_name
    if project_metadata.get("name_redacted"):
        package["installed_version_lookup_redacted"] = True
        package["installed_version"] = None
    else:
        package["installed_version"] = _installed_version(installed_version_name)
    package["build_system"] = build_metadata
    lockfiles = _lockfile_provenance(project_root)
    installed_packages = _installed_package_snapshot()
    pip_freeze = _pip_freeze_snapshot()
    pip_config = _pip_config_snapshot()
    package_source_policy = _package_source_policy(
        lockfiles=lockfiles,
        installed_packages=installed_packages,
        pip_freeze=pip_freeze,
        pip_config=pip_config,
    )
    numerical_runtime = _numerical_runtime_provenance()
    llm_provider_sdks = _llm_provider_sdk_provenance()
    accelerator_runtime = _accelerator_runtime_provenance()

    return {
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "version_info": list(sys.version_info[:5]),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "package": package,
        "dependencies": dependency_records,
        "lockfiles": lockfiles,
        "installed_packages": installed_packages,
        "pip_freeze": pip_freeze,
        "pip_config": pip_config,
        "package_source_policy": package_source_policy,
        "environment_reproducibility_policy": _environment_reproducibility_policy(
            package=package,
            lockfiles=lockfiles,
            installed_packages=installed_packages,
            pip_freeze=pip_freeze,
            pip_config=pip_config,
            package_source_policy=package_source_policy,
            numerical_runtime=numerical_runtime,
            llm_provider_sdks=llm_provider_sdks,
            accelerator_runtime=accelerator_runtime,
        ),
        "numerical_runtime": numerical_runtime,
        "llm_provider_sdks": llm_provider_sdks,
        "accelerator_runtime": accelerator_runtime,
    }


def _package_pyproject_record(path: Path, root: Path) -> dict:
    if not path.is_file():
        return {
            "path": _relative_path(path, root),
            "status": "missing",
        }
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return {
            "path": _relative_path(path, root),
            "status": "unreadable",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }

    record = {
        "path": _relative_path(path, root),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        record.update(
            {
                "status": "invalid_encoding",
                "encoding": "utf-8",
                "error_type": exc.__class__.__name__,
                **_pyproject_diagnostic(str(exc)),
            }
        )
        return record
    try:
        loaded = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        record.update(
            {
                "status": "invalid_toml",
                "error_type": exc.__class__.__name__,
                **_pyproject_diagnostic(str(exc)),
            }
        )
        return record
    record["status"] = "ok"
    record["_loaded"] = loaded
    return record


def _validate_pyproject_schema(loaded: dict) -> list[dict]:
    errors: list[dict] = []
    project_section = loaded.get("project", {})
    if project_section is not None and not isinstance(project_section, dict):
        errors.append({"path": "project", "error": "expected table"})
    elif isinstance(project_section, dict):
        for key in ("name", "version", "requires-python"):
            if key in project_section and not isinstance(project_section[key], str):
                errors.append({"path": f"project.{key}", "error": "expected string"})
        if "license" in project_section:
            errors.extend(_validate_license_metadata("project.license", project_section["license"]))
        for key in ("authors", "maintainers"):
            errors.extend(_validate_people_metadata(f"project.{key}", project_section.get(key)))
        errors.extend(_validate_string_list("project.keywords", project_section.get("keywords")))
        errors.extend(_validate_string_list("project.classifiers", project_section.get("classifiers")))
        for key in ("urls", "scripts", "gui-scripts"):
            errors.extend(_validate_string_mapping(f"project.{key}", project_section.get(key)))
        errors.extend(_validate_entry_points("project.entry-points", project_section.get("entry-points")))
        raw_dependencies = project_section.get("dependencies", [])
        errors.extend(_validate_requirement_list("project.dependencies", raw_dependencies))
        errors.extend(
            _validate_optional_dependencies(
                "project.optional-dependencies",
                project_section.get("optional-dependencies"),
            )
        )

    build_section = loaded.get("build-system", {})
    if build_section is not None and not isinstance(build_section, dict):
        errors.append({"path": "build-system", "error": "expected table"})
    elif isinstance(build_section, dict):
        if "build-backend" in build_section and not isinstance(build_section["build-backend"], str):
            errors.append({"path": "build-system.build-backend", "error": "expected string"})
        raw_requires = build_section.get("requires", [])
        errors.extend(_validate_requirement_list("build-system.requires", raw_requires))
    return errors


def _pyproject_diagnostic(message: str) -> dict:
    redacted = redact_sensitive_text(message)
    safe_message = _truncate_pyproject_diagnostic(redacted)
    record = {"error": safe_message}
    if redacted != message:
        record["error_redacted"] = True
    if safe_message != redacted:
        record["error_truncated"] = True
        record["max_error_chars"] = _PYPROJECT_DIAGNOSTIC_MAX_CHARS
    return record


def _truncate_pyproject_diagnostic(value: str) -> str:
    if len(value) <= _PYPROJECT_DIAGNOSTIC_MAX_CHARS:
        return value
    suffix = "...<truncated>"
    return value[: _PYPROJECT_DIAGNOSTIC_MAX_CHARS - len(suffix)] + suffix


def _pyproject_project_metadata(project_section: dict) -> dict:
    metadata: dict = {}
    field_map = {
        "name": "name",
        "version": "version",
        "requires-python": "requires_python",
    }
    for source_key, output_key in field_map.items():
        if source_key not in project_section:
            continue
        safe_value, field_metadata = _safe_pyproject_metadata_field(
            project_section[source_key],
            output_key,
        )
        metadata[output_key] = safe_value
        metadata.update(field_metadata)
    if "license" in project_section:
        metadata["license"] = _pyproject_license_metadata(project_section["license"])
    for source_key in ("authors", "maintainers"):
        if source_key in project_section:
            metadata[source_key] = _pyproject_people_metadata(project_section[source_key])
    if "classifiers" in project_section:
        metadata["classifiers"] = _pyproject_string_list_metadata(
            project_section["classifiers"],
            "classifier",
        )
    if "keywords" in project_section:
        metadata["keywords"] = _pyproject_string_list_metadata(
            project_section["keywords"],
            "keyword",
        )
    for source_key, output_key in (
        ("urls", "urls"),
        ("scripts", "scripts"),
        ("gui-scripts", "gui_scripts"),
    ):
        if source_key in project_section:
            metadata[output_key] = _pyproject_string_mapping_metadata(
                project_section[source_key],
                output_key,
            )
    if "optional-dependencies" in project_section:
        metadata["optional_dependencies"] = _pyproject_optional_dependencies_metadata(
            project_section["optional-dependencies"]
        )
    if "entry-points" in project_section:
        metadata["entry_points"] = _pyproject_entry_points_metadata(
            project_section["entry-points"]
        )
    extra_metadata = _pyproject_extra_project_metadata(project_section)
    if extra_metadata is not None:
        metadata["extra_project_metadata"] = extra_metadata
    return metadata


def _pyproject_build_metadata(build_section: dict) -> dict:
    metadata: dict = {}
    if "build-backend" in build_section:
        safe_value, field_metadata = _safe_pyproject_metadata_field(
            build_section["build-backend"],
            "build_backend",
        )
        metadata["build_backend"] = safe_value
        metadata.update(field_metadata)
    requires = build_section.get("requires", [])
    safe_requires = []
    hashes = []
    redacted = False
    for requirement in requires:
        normalized = unicodedata.normalize("NFC", requirement)
        escaped = "".join(_safe_identity_char(char) for char in normalized)
        safe_requirement = _truncate_pyproject_metadata(redact_sensitive_text(escaped))
        safe_requires.append(safe_requirement)
        if safe_requires[-1] != requirement:
            redacted = True
        hashes.append(_hash_text(requirement))
    metadata["requires"] = safe_requires
    if redacted:
        metadata["requires_hashes"] = hashes
        metadata["requires_redacted"] = True
    return metadata


def _safe_pyproject_metadata_field(raw_value: str, field: str) -> tuple[str, dict]:
    normalized = unicodedata.normalize("NFC", raw_value)
    escaped = "".join(_safe_identity_char(char) for char in normalized)
    redacted = redact_sensitive_text(escaped)
    safe_value = _truncate_pyproject_metadata(redacted)
    metadata: dict = {}
    if safe_value != raw_value:
        metadata[f"{field}_hash"] = _hash_text(raw_value)
        metadata[f"{field}_redacted"] = True
        if normalized != raw_value:
            metadata[f"{field}_normalization"] = "NFC"
        if escaped != normalized:
            metadata[f"{field}_unsafe_chars_redacted"] = True
        if redacted != escaped:
            metadata[f"{field}_secret_redacted"] = True
        if safe_value != redacted:
            metadata[f"{field}_truncated"] = True
            metadata[f"{field}_max_chars"] = _PYPROJECT_METADATA_MAX_CHARS
    return safe_value, metadata


def _pyproject_license_metadata(value: object) -> str | dict:
    if isinstance(value, str):
        safe_value, metadata = _safe_pyproject_metadata_field(value, "license")
        if metadata:
            return {"value": safe_value, **metadata}
        return safe_value
    record: dict = {}
    if isinstance(value, dict):
        for key in ("text", "file"):
            if key in value:
                safe_value, metadata = _safe_pyproject_metadata_field(
                    value[key],
                    key,
                )
                record[key] = safe_value
                record.update(metadata)
    return record


def _pyproject_people_metadata(value: object) -> list[dict]:
    records: list[dict] = []
    if not isinstance(value, list):
        return records
    for item in value:
        if not isinstance(item, dict):
            continue
        record: dict = {}
        for key in ("name", "email"):
            if key in item:
                safe_value, metadata = _safe_pyproject_metadata_field(item[key], key)
                record[key] = safe_value
                record.update(metadata)
        records.append(record)
    return records


def _pyproject_string_list_metadata(value: object, field: str) -> list[dict]:
    records: list[dict] = []
    if not isinstance(value, list):
        return records
    for item in value:
        if not isinstance(item, str):
            continue
        safe_value, metadata = _safe_pyproject_metadata_field(item, field)
        record = {"value": safe_value, "hash": _hash_text(item)}
        record.update(metadata)
        records.append(record)
    return records


def _pyproject_string_mapping_metadata(value: object, field: str) -> list[dict]:
    records: list[dict] = []
    if not isinstance(value, dict):
        return records
    for key, item in sorted(value.items(), key=lambda pair: str(pair[0])):
        if not isinstance(key, str) or not isinstance(item, str):
            continue
        safe_label, label_metadata = _safe_pyproject_metadata_field(key, "label")
        safe_value, value_metadata = _safe_pyproject_metadata_field(item, "value")
        record = {
            "label": safe_label,
            "label_hash": _hash_text(key),
            "value": safe_value,
            "value_hash": _hash_text(item),
        }
        record.update(label_metadata)
        record.update(value_metadata)
        records.append(record)
    return records


def _pyproject_optional_dependencies_metadata(value: object) -> list[dict]:
    records: list[dict] = []
    if not isinstance(value, dict):
        return records
    for group, requirements in sorted(value.items(), key=lambda pair: str(pair[0])):
        if not isinstance(group, str) or not isinstance(requirements, list):
            continue
        safe_group, group_metadata = _safe_pyproject_metadata_field(group, "group")
        safe_requirements: list[dict] = []
        for requirement in requirements:
            if not isinstance(requirement, str):
                continue
            safe_spec, spec_metadata = _safe_pyproject_metadata_field(requirement, "spec")
            record = {"spec": safe_spec, "spec_hash": _hash_text(requirement)}
            record.update(spec_metadata)
            safe_requirements.append(record)
        group_record = {
            "group": safe_group,
            "group_hash": _hash_text(group),
            "requirements": safe_requirements,
        }
        group_record.update(group_metadata)
        records.append(group_record)
    return records


def _pyproject_entry_points_metadata(value: object) -> list[dict]:
    records: list[dict] = []
    if not isinstance(value, dict):
        return records
    for group, entries in sorted(value.items(), key=lambda pair: str(pair[0])):
        if not isinstance(group, str) or not isinstance(entries, dict):
            continue
        safe_group, group_metadata = _safe_pyproject_metadata_field(group, "group")
        entry_records = _pyproject_string_mapping_metadata(entries, "entry_point")
        group_record = {
            "group": safe_group,
            "group_hash": _hash_text(group),
            "entries": entry_records,
        }
        group_record.update(group_metadata)
        records.append(group_record)
    return records


def _pyproject_extra_project_metadata(project_section: dict) -> dict | None:
    extra_items = {
        key: value
        for key, value in project_section.items()
        if key not in _PYPROJECT_PROJECT_SELECTED_KEYS
    }
    if not extra_items:
        return None
    records = [
        _pyproject_extra_metadata_entry(key, value, depth=0)
        for key, value in sorted(extra_items.items(), key=lambda pair: str(pair[0]))
    ]
    retained = records[:_PYPROJECT_EXTRA_METADATA_MAX_KEYS]
    return {
        "policy": "bounded_pyproject_project_extra_metadata_v1",
        "key_count": len(records),
        "max_keys": _PYPROJECT_EXTRA_METADATA_MAX_KEYS,
        "omitted_key_count": max(0, len(records) - _PYPROJECT_EXTRA_METADATA_MAX_KEYS),
        "max_items": _PYPROJECT_EXTRA_METADATA_MAX_ITEMS,
        "max_depth": _PYPROJECT_EXTRA_METADATA_MAX_DEPTH,
        "entries": retained,
        "hash": _hash_text(_pyproject_extra_metadata_hash_input(extra_items)),
        "hash_scope": "raw_pyproject_project_extra_metadata_v1",
    }


def _pyproject_extra_metadata_entry(key: object, value: object, *, depth: int) -> dict:
    raw_label = str(key)
    safe_label, label_metadata = _safe_pyproject_metadata_field(raw_label, "label")
    record = {
        "label": safe_label,
        "label_hash": _hash_text(raw_label),
        "value": _pyproject_extra_metadata_value(value, depth=depth),
    }
    record.update(label_metadata)
    return record


def _pyproject_extra_metadata_value(value: object, *, depth: int) -> dict:
    if depth >= _PYPROJECT_EXTRA_METADATA_MAX_DEPTH:
        return {
            "type": type(value).__name__,
            "status": "skipped_max_depth",
        }
    if isinstance(value, str):
        safe_value, metadata = _safe_pyproject_metadata_field(value, "value")
        record = {
            "type": "string",
            "value": safe_value,
            "hash": _hash_text(value),
            "redacted": safe_value != value,
        }
        record.update(metadata)
        return record
    if isinstance(value, bool):
        return {"type": "boolean", "value": value}
    if isinstance(value, int):
        return {"type": "integer", "value": value}
    if isinstance(value, float):
        if math.isfinite(value):
            return {"type": "float", "value": value}
        return {
            "type": "float",
            "status": "non_finite",
            "value_repr_hash": _hash_text(repr(value)),
        }
    if isinstance(value, list):
        retained = value[:_PYPROJECT_EXTRA_METADATA_MAX_ITEMS]
        return {
            "type": "list",
            "item_count": len(value),
            "max_items": _PYPROJECT_EXTRA_METADATA_MAX_ITEMS,
            "omitted_item_count": max(
                0,
                len(value) - _PYPROJECT_EXTRA_METADATA_MAX_ITEMS,
            ),
            "items": [
                _pyproject_extra_metadata_value(item, depth=depth + 1)
                for item in retained
            ],
        }
    if isinstance(value, dict):
        entries = [
            _pyproject_extra_metadata_entry(key, item, depth=depth + 1)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        ]
        retained_entries = entries[:_PYPROJECT_EXTRA_METADATA_MAX_ITEMS]
        return {
            "type": "table",
            "item_count": len(entries),
            "max_items": _PYPROJECT_EXTRA_METADATA_MAX_ITEMS,
            "omitted_item_count": max(
                0,
                len(entries) - _PYPROJECT_EXTRA_METADATA_MAX_ITEMS,
            ),
            "entries": retained_entries,
        }
    raw_value = str(value)
    safe_value, metadata = _safe_pyproject_metadata_field(raw_value, "value")
    record = {
        "type": type(value).__name__,
        "value": safe_value,
        "hash": _hash_text(raw_value),
        "redacted": safe_value != raw_value,
    }
    record.update(metadata)
    return record


def _pyproject_extra_metadata_hash_input(value: object) -> str:
    return json.dumps(
        _pyproject_extra_metadata_hash_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _pyproject_extra_metadata_hash_value(value: object) -> object:
    if isinstance(value, dict):
        return {
            str(key): _pyproject_extra_metadata_hash_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_pyproject_extra_metadata_hash_value(item) for item in value]
    if isinstance(value, (str, bool, int)) or value is None:
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else {"type": "float", "repr": repr(value)}
    return {"type": type(value).__name__, "repr": str(value)}


def _truncate_pyproject_metadata(value: str) -> str:
    if len(value) <= _PYPROJECT_METADATA_MAX_CHARS:
        return value
    suffix = "...<truncated>"
    return value[: _PYPROJECT_METADATA_MAX_CHARS - len(suffix)] + suffix


def _validate_requirement_list(path: str, value: object) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list):
        return [{"path": path, "error": "expected list of requirement strings"}]
    errors: list[dict] = []
    for index, spec in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(spec, str):
            errors.append({"path": item_path, "error": "expected requirement string"})
            continue
        try:
            Requirement(spec)
        except InvalidRequirement as exc:
            errors.append(
                {
                    "path": item_path,
                    "error": "invalid requirement string",
                    "error_type": exc.__class__.__name__,
                }
            )
    return errors


def _validate_license_metadata(path: str, value: object) -> list[dict]:
    if isinstance(value, str):
        return []
    if not isinstance(value, dict):
        return [{"path": path, "error": "expected string or table"}]
    errors: list[dict] = []
    allowed = {"text", "file"}
    for key, item in value.items():
        if key not in allowed:
            errors.append({"path": f"{path}.{key}", "error": "unsupported key"})
        elif not isinstance(item, str):
            errors.append({"path": f"{path}.{key}", "error": "expected string"})
    return errors


def _validate_people_metadata(path: str, value: object) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list):
        return [{"path": path, "error": "expected list of people tables"}]
    errors: list[dict] = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            errors.append({"path": item_path, "error": "expected table"})
            continue
        for key, field_value in item.items():
            if key not in {"name", "email"}:
                errors.append({"path": f"{item_path}.{key}", "error": "unsupported key"})
            elif not isinstance(field_value, str):
                errors.append({"path": f"{item_path}.{key}", "error": "expected string"})
    return errors


def _validate_string_list(path: str, value: object) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list):
        return [{"path": path, "error": "expected list of strings"}]
    errors: list[dict] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            errors.append({"path": f"{path}[{index}]", "error": "expected string"})
    return errors


def _validate_string_mapping(path: str, value: object) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, dict):
        return [{"path": path, "error": "expected table of strings"}]
    errors: list[dict] = []
    for key, item in value.items():
        if not isinstance(key, str):
            errors.append({"path": path, "error": "expected string keys"})
        elif not isinstance(item, str):
            errors.append({"path": f"{path}.{key}", "error": "expected string"})
    return errors


def _validate_optional_dependencies(path: str, value: object) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, dict):
        return [{"path": path, "error": "expected table of dependency groups"}]
    errors: list[dict] = []
    for group, requirements in value.items():
        if not isinstance(group, str):
            errors.append({"path": path, "error": "expected string group names"})
            continue
        errors.extend(_validate_requirement_list(f"{path}.{group}", requirements))
    return errors


def _validate_entry_points(path: str, value: object) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, dict):
        return [{"path": path, "error": "expected table of entry-point groups"}]
    errors: list[dict] = []
    for group, entries in value.items():
        if not isinstance(group, str):
            errors.append({"path": path, "error": "expected string group names"})
            continue
        errors.extend(_validate_string_mapping(f"{path}.{group}", entries))
    return errors


def _dependency_record(spec: str) -> dict:
    requirement = Requirement(spec)
    name_record = _dependency_name_record(requirement.name)
    safe_spec, spec_metadata = _safe_pyproject_metadata_field(spec, "spec")
    return {
        **name_record,
        "spec": safe_spec,
        **spec_metadata,
        "installed_version": _installed_version(requirement.name)
        if not name_record["name_redacted"]
        else None,
    }


def _dependency_name_record(name: str) -> dict:
    safe_name = redact_sensitive_text(name)
    redacted = safe_name != name
    record = {
        "name": safe_name,
        "name_hash": _hash_text(name),
        "name_redacted": redacted,
    }
    if redacted:
        record["installed_version_lookup_name"] = safe_name
        record["installed_version_lookup_name_hash"] = record["name_hash"]
        record["installed_version_lookup_redacted"] = True
    else:
        record["installed_version_lookup_name"] = name
        record["installed_version_lookup_redacted"] = False
    return record


def _lockfile_provenance(project_root: Path) -> dict:
    records = []
    for name in _LOCKFILE_CANDIDATES:
        path = project_root / name
        if not path.exists():
            continue
        records.append(_lockfile_record(path, project_root))
    records.sort(key=lambda record: record["path"])
    return {
        "policy": "known_project_lockfiles_v1",
        "candidate_paths": list(_LOCKFILE_CANDIDATES),
        "max_file_bytes": _LOCKFILE_PROVENANCE_MAX_FILE_BYTES,
        "file_count": len(records),
        "files": records,
        "hash": _hash_records(records),
        "hash_scope": "known_project_lockfile_records_v1",
    }


def _lockfile_record(path: Path, project_root: Path) -> dict:
    record = {
        "path": _relative_path(path, project_root),
    }
    if _is_link(path):
        return record | {"status": "link_not_followed"} | _link_not_followed_skip(
            path,
            project_root,
        )
    if not path.is_file():
        return record | {"status": "not_regular_file"}
    try:
        size = path.stat().st_size
    except OSError as exc:
        return record | {
            "status": "unreadable",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }
    if size > _LOCKFILE_PROVENANCE_MAX_FILE_BYTES:
        return record | {
            "status": "skipped_max_file_bytes",
            "bytes": size,
            "max_bytes": _LOCKFILE_PROVENANCE_MAX_FILE_BYTES,
        }
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return record | {
            "status": "unreadable",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }
    return record | {
        "status": "ok",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _installed_package_snapshot() -> dict:
    records: list[dict] = []
    diagnostics: list[dict] = []
    try:
        distributions = list(metadata.distributions())
    except Exception as exc:
        diagnostics.append(
            {
                "status": "unavailable",
                "error_type": exc.__class__.__name__,
                **_pyproject_diagnostic(str(exc)),
            }
        )
        distributions = []
    for distribution in distributions:
        record = _installed_package_record(distribution)
        if record is not None:
            records.append(record)
    records.sort(key=lambda item: (item.get("name", ""), item.get("version", "")))
    total_count = len(records)
    omitted_count = max(0, total_count - _INSTALLED_PACKAGE_SNAPSHOT_MAX_PACKAGES)
    retained = records[:_INSTALLED_PACKAGE_SNAPSHOT_MAX_PACKAGES]
    return {
        "policy": "installed_distribution_names_versions_wheel_source_metadata_v1",
        "max_packages": _INSTALLED_PACKAGE_SNAPSHOT_MAX_PACKAGES,
        "package_count": total_count,
        "omitted_count": omitted_count,
        "packages": retained,
        "hash": _hash_records(records),
        "hash_scope": (
            "all_installed_distribution_name_version_wheel_source_metadata_records_v1"
        ),
        "diagnostics": diagnostics,
    }


def _installed_package_record(distribution: object) -> dict | None:
    raw_name = _distribution_name(distribution)
    raw_version = _distribution_version(distribution)
    if not raw_name:
        return None
    name, name_metadata = _safe_installed_package_field(raw_name, "name")
    version, version_metadata = _safe_installed_package_field(raw_version, "version")
    record = {
        "name": name,
        "name_hash": _hash_text(raw_name),
        "name_redacted": name != raw_name,
        "version": version,
        "version_hash": _hash_text(raw_version),
        "version_redacted": version != raw_version,
        "wheel_metadata": _installed_distribution_wheel_metadata(distribution),
        "source_metadata": _installed_distribution_source_metadata(distribution),
    }
    record.update(name_metadata)
    record.update(version_metadata)
    return record


def _installed_distribution_source_metadata(distribution: object) -> dict:
    return {
        "policy": "installed_distribution_source_metadata_v1",
        "direct_url": _installed_distribution_direct_url_metadata(distribution),
        "installer": _installed_distribution_installer_metadata(distribution),
        "record": _installed_distribution_record_metadata(distribution),
    }


def _installed_distribution_direct_url_metadata(distribution: object) -> dict:
    raw_text = _installed_distribution_text_metadata(
        distribution,
        "direct_url.json",
    )
    if raw_text["status"] != "ok":
        return raw_text
    text = raw_text["text"]
    if len(text) > _INSTALLED_PACKAGE_SOURCE_MAX_CHARS:
        return {
            "status": "skipped_max_chars",
            "metadata_sha256": _hash_text(text),
            "chars": len(text),
            "max_chars": _INSTALLED_PACKAGE_SOURCE_MAX_CHARS,
        }
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return {
            "status": "invalid_json",
            "metadata_sha256": _hash_text(text),
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(exc.msg),
        }
    if not isinstance(payload, dict):
        return {
            "status": "invalid_shape",
            "metadata_sha256": _hash_text(text),
            "value_type": type(payload).__name__,
        }
    record: dict[str, object] = {
        "status": "ok",
        "metadata_sha256": _hash_text(text),
        "key_count": len(payload),
        "max_keys": _INSTALLED_PACKAGE_DIRECT_URL_MAX_KEYS,
        "omitted_key_count": max(
            0,
            len(payload) - _INSTALLED_PACKAGE_DIRECT_URL_MAX_KEYS,
        ),
        "keys": sorted(str(key) for key in payload)[:_INSTALLED_PACKAGE_DIRECT_URL_MAX_KEYS],
    }
    url = payload.get("url")
    if isinstance(url, str):
        safe_url, metadata = _safe_installed_package_field(url, "url")
        record["url"] = safe_url
        record["url_hash"] = _hash_text(url)
        record["url_redacted"] = safe_url != url
        record.update(metadata)
    for object_field in ("vcs_info", "archive_info", "dir_info"):
        item = payload.get(object_field)
        if isinstance(item, dict):
            record[object_field] = _hash_json_metadata(item, object_field)
    return record


def _installed_distribution_installer_metadata(distribution: object) -> dict:
    raw_text = _installed_distribution_text_metadata(distribution, "INSTALLER")
    if raw_text["status"] != "ok":
        return raw_text
    text = raw_text["text"]
    if len(text) > _INSTALLED_PACKAGE_SOURCE_MAX_CHARS:
        return {
            "status": "skipped_max_chars",
            "metadata_sha256": _hash_text(text),
            "chars": len(text),
            "max_chars": _INSTALLED_PACKAGE_SOURCE_MAX_CHARS,
        }
    value = text.strip()
    safe_value, metadata = _safe_installed_package_field(value, "installer")
    record: dict[str, object] = {
        "status": "ok",
        "metadata_sha256": _hash_text(text),
        "installer": safe_value,
        "installer_hash": _hash_text(value),
        "installer_redacted": safe_value != value,
    }
    record.update(metadata)
    return record


def _installed_distribution_record_metadata(distribution: object) -> dict:
    raw_text = _installed_distribution_text_metadata(distribution, "RECORD")
    if raw_text["status"] != "ok":
        return raw_text
    text = raw_text["text"]
    if len(text) > _INSTALLED_PACKAGE_SOURCE_MAX_CHARS:
        return {
            "status": "skipped_max_chars",
            "metadata_sha256": _hash_text(text),
            "chars": len(text),
            "max_chars": _INSTALLED_PACKAGE_SOURCE_MAX_CHARS,
        }
    lines = text.splitlines()
    return {
        "status": "ok",
        "metadata_sha256": _hash_text(text),
        "line_count": len(lines),
        "hash_scope": "raw_installed_distribution_record_text_v1",
    }


def _installed_distribution_text_metadata(distribution: object, name: str) -> dict:
    reader = getattr(distribution, "read_text", None)
    if not callable(reader):
        return {"status": "missing"}
    try:
        raw_text = reader(name)
    except FileNotFoundError:
        return {"status": "missing"}
    except Exception as exc:
        return {
            "status": "read_error",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }
    if raw_text is None:
        return {"status": "missing"}
    if not isinstance(raw_text, str):
        return {
            "status": "invalid",
            "error": f"distribution read_text({name!r}) returned non-text metadata",
            "value_type": type(raw_text).__name__,
        }
    return {"status": "ok", "text": raw_text}


def _hash_json_metadata(value: dict, field: str) -> dict:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return {
        "status": "hash_only",
        "key_count": len(value),
        "hash": _hash_text(encoded),
        "hash_scope": f"{field}_json_object_v1",
    }


def _installed_distribution_wheel_metadata(distribution: object) -> dict:
    reader = getattr(distribution, "read_text", None)
    if not callable(reader):
        return {"status": "missing"}
    try:
        raw_text = reader("WHEEL")
    except FileNotFoundError:
        return {"status": "missing"}
    except Exception as exc:
        return {
            "status": "read_error",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }
    if raw_text is None:
        return {"status": "missing"}
    if not isinstance(raw_text, str):
        return {
            "status": "invalid",
            "error": "distribution read_text('WHEEL') returned non-text metadata",
            "value_type": type(raw_text).__name__,
        }
    if len(raw_text) > _INSTALLED_PACKAGE_WHEEL_MAX_CHARS:
        return {
            "status": "skipped_max_chars",
            "metadata_sha256": _hash_text(raw_text),
            "chars": len(raw_text),
            "max_chars": _INSTALLED_PACKAGE_WHEEL_MAX_CHARS,
        }

    message = Parser().parsestr(raw_text)
    raw_tags = message.get_all("Tag") or []
    retained_tags = raw_tags[:_INSTALLED_PACKAGE_WHEEL_MAX_TAGS]
    record = {
        "status": "ok",
        "metadata_sha256": _hash_text(raw_text),
        "tag_count": len(raw_tags),
        "max_tags": _INSTALLED_PACKAGE_WHEEL_MAX_TAGS,
        "omitted_tag_count": max(0, len(raw_tags) - _INSTALLED_PACKAGE_WHEEL_MAX_TAGS),
        "tags": [_wheel_metadata_field_record(tag, "tag") for tag in retained_tags],
    }
    for source_field, output_field in (
        ("Wheel-Version", "wheel_version"),
        ("Generator", "generator"),
    ):
        value = message.get(source_field)
        if value is not None:
            safe_value, metadata = _safe_installed_package_field(value, output_field)
            record[output_field] = safe_value
            record[f"{output_field}_hash"] = _hash_text(value)
            record[f"{output_field}_redacted"] = safe_value != value
            record.update(metadata)

    root_is_purelib = message.get("Root-Is-Purelib")
    if root_is_purelib is not None:
        normalized = root_is_purelib.strip().lower()
        if normalized in {"true", "false"}:
            record["root_is_purelib"] = normalized == "true"
            record["root_is_purelib_hash"] = _hash_text(root_is_purelib)
        else:
            root_record = _wheel_metadata_field_record(
                root_is_purelib,
                "root_is_purelib",
            )
            record["root_is_purelib"] = None
            record["root_is_purelib_raw"] = root_record["value"]
            record["root_is_purelib_hash"] = root_record["hash"]
            for key, value in root_record.items():
                if key not in {"value", "hash"}:
                    record[key] = value
    return record


def _wheel_metadata_field_record(raw_value: str, field: str) -> dict:
    safe_value, metadata = _safe_installed_package_field(raw_value, field)
    record = {
        "value": safe_value,
        "hash": _hash_text(raw_value),
        "redacted": safe_value != raw_value,
    }
    record.update(metadata)
    return record


def _distribution_name(distribution: object) -> str:
    metadata_value = getattr(distribution, "metadata", None)
    name = None
    if metadata_value is not None:
        try:
            name = metadata_value.get("Name")
        except Exception:
            name = None
    if name is None:
        name = getattr(distribution, "name", None)
    return str(name or "")


def _distribution_version(distribution: object) -> str:
    version = getattr(distribution, "version", "")
    return str(version or "")


def _safe_installed_package_field(raw_value: str, field: str) -> tuple[str, dict]:
    safe_value, metadata = _safe_pyproject_metadata_field(raw_value, field)
    return safe_value, {
        key: value
        for key, value in metadata.items()
        if key not in {f"{field}_hash", f"{field}_redacted"}
    }


def _pip_freeze_snapshot() -> dict:
    command = [sys.executable, "-m", "pip", "freeze", "--all"]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=_PIP_FREEZE_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "policy": "pip_freeze_all_redacted_bounded_v1",
            "status": "timeout",
            "timeout_sec": _PIP_FREEZE_TIMEOUT_SECONDS,
            **_pyproject_diagnostic(_subprocess_error_text(exc)),
        }
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "policy": "pip_freeze_all_redacted_bounded_v1",
            "status": "error",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if result.returncode != 0:
        record = {
            "policy": "pip_freeze_all_redacted_bounded_v1",
            "status": "error",
            "returncode": result.returncode,
            "stdout_sha256": _hash_text(stdout),
            "stderr_sha256": _hash_text(stderr),
        }
        if stderr:
            record["stderr_preview"] = _truncate_pip_freeze_line(
                redact_sensitive_text(
                    "".join(_safe_identity_char(char) for char in stderr)
                )
            )
        return record

    raw_lines = stdout.splitlines()
    retained_lines = raw_lines[:_PIP_FREEZE_MAX_LINES]
    records = [_pip_freeze_line_record(line) for line in retained_lines]
    return {
        "policy": "pip_freeze_all_redacted_bounded_v1",
        "status": "ok",
        "command": "python -m pip freeze --all",
        "timeout_sec": _PIP_FREEZE_TIMEOUT_SECONDS,
        "line_count": len(raw_lines),
        "max_lines": _PIP_FREEZE_MAX_LINES,
        "omitted_line_count": max(0, len(raw_lines) - _PIP_FREEZE_MAX_LINES),
        "max_line_chars": _PIP_FREEZE_MAX_LINE_CHARS,
        "lines": records,
        "stdout_sha256": _hash_text(stdout),
        "hash_scope": "raw_pip_freeze_stdout_text_v1",
    }


def _pip_freeze_line_record(raw_line: str) -> dict:
    normalized = unicodedata.normalize("NFC", raw_line)
    escaped = "".join(_safe_identity_char(char) for char in normalized)
    redacted = redact_sensitive_text(escaped)
    line = _truncate_pip_freeze_line(redacted)
    record = {
        "line": line,
        "line_hash": _hash_text(raw_line),
        "line_redacted": line != raw_line,
    }
    if normalized != raw_line:
        record["line_normalization"] = "NFC"
    if escaped != normalized:
        record["line_unsafe_chars_redacted"] = True
    if redacted != escaped:
        record["line_secret_redacted"] = True
    if line != redacted:
        record["line_truncated"] = True
    return record


def _truncate_pip_freeze_line(value: str) -> str:
    if len(value) <= _PIP_FREEZE_MAX_LINE_CHARS:
        return value
    suffix = "...<truncated>"
    return value[: _PIP_FREEZE_MAX_LINE_CHARS - len(suffix)] + suffix


def _pip_config_snapshot() -> dict:
    command = [sys.executable, "-m", "pip", "config", "list"]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=_PIP_CONFIG_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "policy": "pip_config_list_redacted_bounded_v1",
            "status": "timeout",
            "timeout_sec": _PIP_CONFIG_TIMEOUT_SECONDS,
            **_pyproject_diagnostic(_subprocess_error_text(exc)),
        }
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "policy": "pip_config_list_redacted_bounded_v1",
            "status": "error",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if result.returncode != 0:
        record = {
            "policy": "pip_config_list_redacted_bounded_v1",
            "status": "error",
            "returncode": result.returncode,
            "stdout_sha256": _hash_text(stdout),
            "stderr_sha256": _hash_text(stderr),
        }
        if stderr:
            record["stderr_preview"] = _truncate_pip_config_line(
                redact_sensitive_text(
                    "".join(_safe_identity_char(char) for char in stderr)
                )
            )
        return record

    raw_lines = stdout.splitlines()
    retained_lines = raw_lines[:_PIP_CONFIG_MAX_LINES]
    records = [_pip_config_line_record(line) for line in retained_lines]
    return {
        "policy": "pip_config_list_redacted_bounded_v1",
        "status": "ok",
        "command": "python -m pip config list",
        "timeout_sec": _PIP_CONFIG_TIMEOUT_SECONDS,
        "line_count": len(raw_lines),
        "max_lines": _PIP_CONFIG_MAX_LINES,
        "omitted_line_count": max(0, len(raw_lines) - _PIP_CONFIG_MAX_LINES),
        "max_line_chars": _PIP_CONFIG_MAX_LINE_CHARS,
        "lines": records,
        "stdout_sha256": _hash_text(stdout),
        "hash_scope": "raw_pip_config_list_stdout_text_v1",
    }


def _pip_config_line_record(raw_line: str) -> dict:
    normalized = unicodedata.normalize("NFC", raw_line)
    escaped = "".join(_safe_identity_char(char) for char in normalized)
    redacted = redact_sensitive_text(escaped)
    line = _truncate_pip_config_line(redacted)
    record = {
        "line": line,
        "line_hash": _hash_text(raw_line),
        "line_redacted": line != raw_line,
    }
    if normalized != raw_line:
        record["line_normalization"] = "NFC"
    if escaped != normalized:
        record["line_unsafe_chars_redacted"] = True
    if redacted != escaped:
        record["line_secret_redacted"] = True
    if line != redacted:
        record["line_truncated"] = True
    return record


def _truncate_pip_config_line(value: str) -> str:
    if len(value) <= _PIP_CONFIG_MAX_LINE_CHARS:
        return value
    suffix = "...<truncated>"
    return value[: _PIP_CONFIG_MAX_LINE_CHARS - len(suffix)] + suffix


def _package_source_policy(
    *,
    lockfiles: dict,
    installed_packages: dict,
    pip_freeze: dict,
    pip_config: dict,
) -> dict:
    evidence = {
        "lockfiles": {
            "policy": lockfiles.get("policy"),
            "file_count": lockfiles.get("file_count", 0),
            "hash_scope": lockfiles.get("hash_scope"),
            "hash_present": isinstance(lockfiles.get("hash"), str),
        },
        "installed_packages": {
            "policy": installed_packages.get("policy"),
            "package_count": installed_packages.get("package_count", 0),
            "omitted_count": installed_packages.get("omitted_count", 0),
            "hash_scope": installed_packages.get("hash_scope"),
            "hash_present": isinstance(installed_packages.get("hash"), str),
        },
        "pip_freeze": {
            "policy": pip_freeze.get("policy"),
            "status": pip_freeze.get("status"),
            "line_count": pip_freeze.get("line_count", 0),
            "omitted_line_count": pip_freeze.get("omitted_line_count", 0),
            "hash_scope": pip_freeze.get("hash_scope"),
            "stdout_sha256_present": isinstance(pip_freeze.get("stdout_sha256"), str),
        },
        "pip_config": {
            "policy": pip_config.get("policy"),
            "status": pip_config.get("status"),
            "line_count": pip_config.get("line_count", 0),
            "omitted_line_count": pip_config.get("omitted_line_count", 0),
            "hash_scope": pip_config.get("hash_scope"),
            "stdout_sha256_present": isinstance(pip_config.get("stdout_sha256"), str),
        },
    }
    record = {
        "policy": "bounded_redacted_package_source_evidence_v1",
        "status": "audit_only",
        "evidence": evidence,
        "private_source_interpretation": (
            "redacted_retained_lines_plus_raw_stdout_hashes_only"
        ),
        "retention": {
            "lockfiles": "hash_only_known_project_root_files",
            "pip_freeze": "bounded_redacted_lines_with_raw_stdout_hash",
            "pip_config": "bounded_redacted_lines_with_raw_stdout_hash",
            "installed_packages": (
                "bounded_name_version_wheel_and_source_metadata_snapshot"
            ),
        },
        "unsupported": [
            "private_index_identity_resolution",
            "credential_retention",
            "remote_package_artifact_hash_verification",
            "live_index_availability_or_authentication_check",
            "non_pip_package_manager_source_interpretation",
        ],
        "hash_scope": "package_source_policy_evidence_v1",
    }
    record["hash"] = _hash_records([evidence])
    return record


def _environment_reproducibility_policy(
    *,
    package: dict,
    lockfiles: dict,
    installed_packages: dict,
    pip_freeze: dict,
    pip_config: dict,
    package_source_policy: dict,
    numerical_runtime: dict,
    llm_provider_sdks: dict,
    accelerator_runtime: dict,
) -> dict:
    numpy_record = numerical_runtime.get("numpy", {})
    evidence = {
        "package_pyproject": {
            "status": package.get("pyproject", {}).get("status"),
            "sha256": package.get("pyproject", {}).get("sha256"),
            "selected_project_metadata": "bounded_redacted_hash_backed",
            "extra_project_metadata": package.get("extra_project_metadata", {}).get(
                "policy"
            ),
            "build_system": package.get("build_system", {}).get("policy"),
        },
        "lockfiles": {
            "policy": lockfiles.get("policy"),
            "hash": lockfiles.get("hash"),
            "file_count": lockfiles.get("file_count", 0),
        },
        "installed_packages": {
            "policy": installed_packages.get("policy"),
            "hash": installed_packages.get("hash"),
            "package_count": installed_packages.get("package_count", 0),
            "omitted_count": installed_packages.get("omitted_count", 0),
        },
        "pip_freeze": {
            "policy": pip_freeze.get("policy"),
            "status": pip_freeze.get("status"),
            "stdout_sha256": pip_freeze.get("stdout_sha256"),
            "line_count": pip_freeze.get("line_count", 0),
            "omitted_line_count": pip_freeze.get("omitted_line_count", 0),
        },
        "pip_config": {
            "policy": pip_config.get("policy"),
            "status": pip_config.get("status"),
            "stdout_sha256": pip_config.get("stdout_sha256"),
            "line_count": pip_config.get("line_count", 0),
            "omitted_line_count": pip_config.get("omitted_line_count", 0),
        },
        "package_source_policy": {
            "policy": package_source_policy.get("policy"),
            "status": package_source_policy.get("status"),
            "hash": package_source_policy.get("hash"),
        },
        "numerical_runtime": {
            "numpy": {
                "status": numpy_record.get("status"),
                "version": numpy_record.get("version"),
                "show_config_sha256": numpy_record.get("show_config", {}).get(
                    "sha256"
                ),
            },
        },
        "llm_provider_sdks": {
            "policy": llm_provider_sdks.get("policy"),
            "hash": llm_provider_sdks.get("hash"),
        },
        "accelerator_runtime": {
            "policy": accelerator_runtime.get("policy"),
            "hash": accelerator_runtime.get("hash"),
        },
    }
    record = {
        "schema": "libreevolve.environment_reproducibility_policy.v1",
        "policy": "bounded_environment_evidence_with_explicit_unsupported_surfaces",
        "status": "audit_only_not_complete_replay_environment",
        "evidence": evidence,
        "covered_surfaces": [
            "project_pyproject_metadata",
            "known_project_root_lockfile_hashes",
            "installed_distribution_name_version_wheel_source_metadata",
            "pip_freeze_stdout_hash_and_bounded_redacted_preview",
            "pip_config_stdout_hash_and_bounded_redacted_preview",
            "numpy_version_and_show_config_hash",
            "builtin_llm_provider_sdk_package_versions",
            "bounded_accelerator_environment_and_driver_probe_evidence",
        ],
        "unsupported_surfaces": [
            "complete_install_source_options_interpretation",
            "broader_non_project_build_provenance",
            "live_provider_service_api_version_capture",
            "provider_cost_capture",
            "remote_provider_side_default_capture",
            "accelerator_budget_accounting_semantics",
            "private_package_source_identity_or_authentication_resolution",
            "remote_package_artifact_hash_verification",
        ],
        "private_source_policy": (
            "bounded_redacted_pip_config_and_freeze_evidence_with_raw_hashes_only"
        ),
        "live_provider_policy": (
            "installed_sdk_versions_only_no_live_service_or_account_lookup"
        ),
        "accelerator_policy": (
            "bounded_runtime_hints_and_driver_probes_no_budget_accounting"
        ),
        "hash_scope": "environment_reproducibility_policy_evidence_v1",
    }
    record["hash"] = _hash_records([evidence])
    return record


def _subprocess_error_text(exc: subprocess.TimeoutExpired) -> str:
    parts = [str(exc)]
    for value in (exc.stdout, exc.stderr):
        if isinstance(value, bytes):
            parts.append(value.decode("utf-8", errors="replace"))
        elif isinstance(value, str):
            parts.append(value)
    return "\n".join(part for part in parts if part)


def _llm_provider_sdk_provenance() -> dict:
    records = [_llm_provider_sdk_record(candidate) for candidate in _LLM_PROVIDER_SDK_CANDIDATES]
    return {
        "policy": "llm_provider_sdk_versions_v1",
        "providers": records,
        "hash": _hash_records(records),
        "hash_scope": "configured_builtin_llm_provider_sdk_version_records_v1",
    }


def _llm_provider_sdk_record(candidate: dict) -> dict:
    package_name = candidate["package"]
    record = {
        "provider": candidate["provider"],
        "package": package_name,
        "adapter_module": candidate["adapter_module"],
        "api_modes": list(candidate["api_modes"]),
    }
    try:
        raw_version = metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return record | {"status": "missing"}
    except Exception as exc:
        return record | {
            "status": "lookup_error",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }
    safe_version, version_metadata = _safe_installed_package_field(
        str(raw_version),
        "version",
    )
    record.update(
        {
            "status": "installed",
            "version": safe_version,
            "version_hash": _hash_text(str(raw_version)),
            "version_redacted": safe_version != str(raw_version),
        }
    )
    record.update(version_metadata)
    return record


def _accelerator_runtime_provenance() -> dict:
    environment = [_accelerator_env_record(name) for name in _ACCELERATOR_ENV_CANDIDATES]
    probes = [_accelerator_probe_record(probe) for probe in _ACCELERATOR_COMMAND_PROBES]
    records = {
        "environment": environment,
        "probes": probes,
    }
    return {
        "policy": "accelerator_runtime_env_and_driver_probe_v1",
        "environment_candidates": list(_ACCELERATOR_ENV_CANDIDATES),
        "environment": environment,
        "probes": probes,
        "hash": _hash_records([records]),
        "hash_scope": "accelerator_environment_and_driver_probe_records_v1",
    }


def _accelerator_env_record(name: str) -> dict:
    record = {"name": name, "present": name in os.environ}
    if name not in os.environ:
        return record
    raw_value = os.environ.get(name, "")
    value, metadata = _safe_accelerator_runtime_line(raw_value)
    record.update(
        {
            "value": value,
            "value_hash": _hash_text(raw_value),
            "value_redacted": value != raw_value,
        }
    )
    record.update({f"value_{key}": item for key, item in metadata.items()})
    return record


def _accelerator_probe_record(probe: dict) -> dict:
    return _accelerator_probe_record_cached(
        probe["name"],
        probe["executable"],
        tuple(probe["args"]),
    )


@functools.lru_cache(maxsize=None)
def _accelerator_probe_record_cached(name: str, executable: str, args: tuple[str, ...]) -> dict:
    args_list = list(args)
    command = [executable, *args_list]
    base = {
        "name": name,
        "executable": executable,
        "args": args_list,
        "timeout_sec": _ACCELERATOR_PROBE_TIMEOUT_SECONDS,
    }
    executable_path = shutil.which(executable)
    if executable_path is None:
        return base | {"status": "executable_missing"}
    base["executable_path_hash"] = _hash_text(executable_path)
    base["executable_basename"] = _portable_executable_basename(executable_path)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=_ACCELERATOR_PROBE_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return base | {
            "status": "timeout",
            **_pyproject_diagnostic(_subprocess_error_text(exc)),
        }
    except (OSError, subprocess.SubprocessError) as exc:
        return base | {
            "status": "error",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    record = base | {
        "returncode": result.returncode,
        "stdout_sha256": _hash_text(stdout),
        "stderr_sha256": _hash_text(stderr),
    }
    if result.returncode != 0:
        record["status"] = "error"
        if stderr:
            preview, metadata = _safe_accelerator_runtime_line(stderr)
            record["stderr_preview"] = preview
            record.update({f"stderr_{key}": value for key, value in metadata.items()})
        return record

    raw_lines = stdout.splitlines()
    retained_lines = raw_lines[:_ACCELERATOR_PROBE_MAX_LINES]
    record.update(
        {
            "status": "ok",
            "line_count": len(raw_lines),
            "max_lines": _ACCELERATOR_PROBE_MAX_LINES,
            "omitted_line_count": max(
                0,
                len(raw_lines) - _ACCELERATOR_PROBE_MAX_LINES,
            ),
            "max_line_chars": _ACCELERATOR_PROBE_MAX_LINE_CHARS,
            "lines": [_accelerator_probe_line_record(line) for line in retained_lines],
            "hash_scope": "raw_accelerator_probe_stdout_text_v1",
        }
    )
    return record


def _accelerator_probe_line_record(raw_line: str) -> dict:
    line, metadata = _safe_accelerator_runtime_line(raw_line)
    record = {
        "line": line,
        "line_hash": _hash_text(raw_line),
        "line_redacted": line != raw_line,
    }
    record.update({f"line_{key}": value for key, value in metadata.items()})
    return record


def _portable_executable_basename(executable_path: str) -> str:
    """Extract an executable name from POSIX or Windows path spelling."""
    return ntpath.basename(executable_path)


def _safe_accelerator_runtime_line(raw_value: str) -> tuple[str, dict]:
    normalized = unicodedata.normalize("NFC", raw_value)
    escaped = "".join(_safe_identity_char(char) for char in normalized)
    redacted = redact_sensitive_text(escaped)
    value = _truncate_accelerator_probe_line(redacted)
    metadata: dict[str, object] = {}
    if normalized != raw_value:
        metadata["normalization"] = "NFC"
    if escaped != normalized:
        metadata["unsafe_chars_redacted"] = True
    if redacted != escaped:
        metadata["secret_redacted"] = True
    if value != redacted:
        metadata["truncated"] = True
    return value, metadata


def _truncate_accelerator_probe_line(value: str) -> str:
    if len(value) <= _ACCELERATOR_PROBE_MAX_LINE_CHARS:
        return value
    suffix = "...<truncated>"
    return value[: _ACCELERATOR_PROBE_MAX_LINE_CHARS - len(suffix)] + suffix


def _numerical_runtime_provenance() -> dict:
    return {
        "policy": "numpy_show_config_hash_v1",
        "numpy": _numpy_runtime_record(),
    }


def _numpy_runtime_record() -> dict:
    try:
        numpy = importlib.import_module("numpy")
    except ModuleNotFoundError:
        return {
            "status": "unavailable",
            "module": "numpy",
            "reason": "module_not_installed",
        }
    except Exception as exc:
        return {
            "status": "import_error",
            "module": "numpy",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }

    raw_version = str(getattr(numpy, "__version__", ""))
    version, version_metadata = _safe_installed_package_field(raw_version, "version")
    record = {
        "status": "ok",
        "module": "numpy",
        "version": version,
        "version_hash": _hash_text(raw_version),
        "version_redacted": version != raw_version,
    }
    record.update(version_metadata)
    record["show_config"] = _numpy_show_config_record(numpy)
    return record


def _numpy_show_config_record(numpy: object) -> dict:
    show_config = getattr(numpy, "show_config", None)
    if not callable(show_config):
        config_module = getattr(numpy, "__config__", None)
        show_config = getattr(config_module, "show", None)
    if not callable(show_config):
        return {
            "status": "unavailable",
            "reason": "show_config_not_available",
        }

    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            show_config()
    except Exception as exc:
        return {
            "status": "error",
            "error_type": exc.__class__.__name__,
            **_pyproject_diagnostic(str(exc)),
        }
    raw = buffer.getvalue()
    redacted = redact_sensitive_text(raw)
    preview = _truncate_numerical_runtime_config(redacted)
    return {
        "status": "ok",
        "sha256": _hash_text(raw),
        "chars": len(raw),
        "preview": preview,
        "preview_chars": len(preview),
        "max_preview_chars": _NUMERICAL_RUNTIME_CONFIG_MAX_CHARS,
        "redacted": redacted != raw,
        "truncated": preview != redacted,
    }


def _truncate_numerical_runtime_config(value: str) -> str:
    if len(value) <= _NUMERICAL_RUNTIME_CONFIG_MAX_CHARS:
        return value
    suffix = "...<truncated>"
    return value[: _NUMERICAL_RUNTIME_CONFIG_MAX_CHARS - len(suffix)] + suffix


def _safe_identity_char(char: str) -> str:
    category = unicodedata.category(char)
    if ord(char) < 32 or ord(char) == 127 or category == "Cf":
        return f"[U+{ord(char):04X}]"
    return char


def git_state(cwd: Path | None = None) -> dict:
    cwd = cwd or Path.cwd()
    root = _git(["rev-parse", "--show-toplevel"], cwd)
    if root is None:
        return {"available": False}
    head = _git(["rev-parse", "HEAD"], Path(root))
    status = _git(["status", "--porcelain"], Path(root))
    status_entries = [] if not status else status.splitlines()
    safe_status_entries = []
    status_entries_unsafe_chars_redacted = False
    for entry in status_entries:
        escaped = _escape_unsafe_display_chars(entry)
        safe_status_entries.append(redact_sensitive_text(escaped))
        if escaped != entry:
            status_entries_unsafe_chars_redacted = True
    return {
        "available": True,
        **_root_record(Path(root), "git"),
        "head": head,
        "dirty": bool(status),
        "status_entry_count": len(status_entries),
        "status_entries": safe_status_entries,
        "status_entry_hashes": [_hash_text(entry) for entry in status_entries],
        "status_entries_redacted": safe_status_entries != status_entries,
        "status_entries_unsafe_chars_redacted": status_entries_unsafe_chars_redacted,
    }


def _tree_provenance(
    root: Path,
    label: str,
    excluded_dirs: set[str],
    excluded_roots: list[Path],
) -> dict:
    root = root.resolve()
    resolved_excluded_roots = _resolve_excluded_roots(root, excluded_roots)
    paths, skipped = _iter_files(root, excluded_dirs, resolved_excluded_roots)
    _reject_normalized_tree_path_collisions(paths, root, label)
    files = []
    for path in paths:
        record, skipped_record = _file_record_or_skip(
            path,
            root,
            max_file_bytes=_TREE_PROVENANCE_MAX_FILE_BYTES,
        )
        if record is not None:
            files.append(record)
        elif skipped_record is not None:
            skipped.append(skipped_record)
    tree_hash = _hash_records(files)
    skipped_hash = _hash_records(skipped)
    provenance_hash = _hash_records(
        [
            {
                "schema": "tree_provenance_v2",
                "tree_hash": tree_hash,
                "skipped_hash": skipped_hash,
                "excluded_dirs": sorted(excluded_dirs),
                "generated_run_artifact_markers": sorted(_RUN_ARTIFACT_MARKER_NAMES),
                "max_file_bytes": _TREE_PROVENANCE_MAX_FILE_BYTES,
            }
        ]
    )
    return {
        "label": label,
        **_root_record(root, label),
        "tree_hash": tree_hash,
        "tree_hash_scope": "included_files",
        "skipped_hash": skipped_hash,
        "skipped_hash_scope": "skipped_diagnostic_records_v2",
        "provenance_hash": provenance_hash,
        "provenance_hash_scope": "included_files_and_skipped_diagnostics_v2",
        "max_file_bytes": _TREE_PROVENANCE_MAX_FILE_BYTES,
        "generated_run_artifact_markers": sorted(_RUN_ARTIFACT_MARKER_NAMES),
        "file_count": len(files),
        "files": files,
        "skipped_count": len(skipped),
        "skipped": skipped,
    }


def _iter_files(
    root: Path,
    excluded_dirs: set[str],
    excluded_roots: set[Path],
) -> tuple[list[Path], list[dict]]:
    paths: list[Path] = []
    skipped: list[dict] = []
    _collect_files(root, root, paths, skipped, excluded_dirs, excluded_roots)
    return sorted(paths, key=lambda p: p.relative_to(root).as_posix()), skipped


def _resolve_excluded_roots(root: Path, excluded_roots: list[Path]) -> set[Path]:
    resolved: set[Path] = set()
    for raw in excluded_roots:
        path = Path(raw)
        if not path.is_absolute():
            path = root / path
        candidate = path.resolve(strict=False)
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        resolved.add(candidate)
    return resolved


def _collect_files(
    root: Path,
    current: Path,
    paths: list[Path],
    skipped: list[dict],
    excluded_dirs: set[str],
    excluded_roots: set[Path],
) -> None:
    try:
        children = sorted(current.iterdir(), key=lambda p: p.as_posix())
    except OSError as exc:
        skipped.append(
            _path_record(_relative_path(current, root))
            | _directory_listing_error_skip(exc)
        )
        return
    for path in children:
        resolved_path = path.resolve(strict=False)
        if resolved_path in excluded_roots:
            skipped.append(
                _path_record(path.relative_to(root).as_posix())
                | {"reason": "excluded_output_root"}
            )
            continue
        if path.is_dir() and path.name in excluded_dirs:
            skipped.append(
                _path_record(path.relative_to(root).as_posix())
                | {"reason": "excluded_directory"}
            )
            continue
        if _is_link(path):
            skipped.append(
                _path_record(path.relative_to(root).as_posix())
                | _link_not_followed_skip(path, root)
            )
            continue
        if path.is_dir():
            if _is_generated_run_artifact_root(path, root):
                skipped.append(
                    _path_record(path.relative_to(root).as_posix())
                    | {"reason": "generated_run_artifacts"}
                )
                continue
            _collect_files(root, path, paths, skipped, excluded_dirs, excluded_roots)
        elif path.is_file():
            paths.append(path)


def _is_generated_run_artifact_root(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    if "runs" not in rel.parts:
        return False
    try:
        child_names = {child.name for child in path.iterdir()}
    except OSError:
        return False
    return bool(child_names & _RUN_ARTIFACT_MARKER_NAMES)


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (is_junction is not None and is_junction())


def _link_not_followed_skip(path: Path, root: Path) -> dict:
    record = {
        "reason": "link_not_followed",
        "is_symlink": path.is_symlink(),
        "is_junction": _path_is_junction(path),
        "target_path_redacted": True,
    }
    if path.is_symlink():
        try:
            raw_target = str(path.readlink())
        except OSError as exc:
            record["link_target_status"] = "read_error"
            record["link_target_error_type"] = exc.__class__.__name__
            record["link_target_error"] = redact_sensitive_text(str(exc))
        else:
            record["link_target_hash"] = _hash_text(raw_target)
            record["link_target_status"] = "ok"
    try:
        resolved_target = path.resolve(strict=True)
    except OSError as exc:
        record["target_scope"] = "unresolved"
        record["target_within_root"] = None
        record["target_resolve_error_type"] = exc.__class__.__name__
        record["target_resolve_error"] = redact_sensitive_text(str(exc))
        return record
    target_text = str(resolved_target)
    record["target_resolved_hash"] = _hash_text(target_text)
    within_root = _path_within(resolved_target, root)
    record["target_within_root"] = within_root
    record["target_scope"] = "within_root" if within_root else "outside_root"
    return record


def _path_is_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction()) if callable(is_junction) else False


def _path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _file_record_or_skip(
    path: Path,
    root: Path,
    *,
    max_file_bytes: int,
) -> tuple[dict | None, dict | None]:
    path_record = _path_record(_relative_path(path, root))
    try:
        size = path.stat().st_size
    except OSError as exc:
        return None, path_record | _read_error_skip(exc)
    if size > max_file_bytes:
        return None, path_record | {
            "reason": "max_file_bytes",
            "bytes": size,
            "max_bytes": max_file_bytes,
        }
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return None, path_record | _read_error_skip(exc)
    return (
        path_record
        | {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        },
        None,
    )


def _reject_normalized_tree_path_collisions(
    paths: list[Path], root: Path, label: str
) -> None:
    seen: dict[str, str] = {}
    for path in paths:
        raw_path = _relative_path(path, root)
        display_path = _display_path(raw_path)
        previous = seen.get(display_path)
        if previous is not None and previous != raw_path:
            raise ValueError(
                f"{root}: duplicate {label} provenance path after Unicode "
                f"normalization: {previous!r} and {raw_path!r} -> {display_path!r}"
            )
        seen[display_path] = raw_path


def _read_error_skip(exc: OSError) -> dict:
    return {
        "reason": "read_error",
        "error_type": exc.__class__.__name__,
        "error": redact_sensitive_text(str(exc)),
    }


def _directory_listing_error_skip(exc: OSError) -> dict:
    return {
        "reason": "directory_listing_error",
        "error_type": exc.__class__.__name__,
        "error": redact_sensitive_text(str(exc)),
    }


def _path_record(raw_path: str) -> dict:
    normalized_path = unicodedata.normalize("NFC", raw_path)
    display_path = _escape_unsafe_display_chars(normalized_path)
    raw_display_path = _escape_unsafe_display_chars(raw_path)
    safe_path = redact_sensitive_text(display_path)
    record = {"path": safe_path}
    if display_path != raw_path:
        safe_raw_path = redact_sensitive_text(raw_display_path)
        record["filesystem_path"] = safe_raw_path
        record["filesystem_path_hash"] = _hash_text(raw_path)
        if normalized_path != raw_path:
            record["path_normalization"] = "NFC"
            record["path_normalized"] = True
        if safe_raw_path != raw_display_path:
            record["filesystem_path_redacted"] = True
    if display_path != normalized_path or raw_display_path != raw_path:
        record["path_unsafe_chars_redacted"] = True
    if safe_path != display_path:
        record["path_hash"] = _hash_text(display_path)
        record["path_redacted"] = True
    return record


def _root_record(root: Path, label: str) -> dict:
    raw_root = str(root.resolve(strict=False))
    return {
        "root": f"<{label}-root>",
        "root_scope": "local_root_label",
        "root_hash": _hash_text(raw_root),
        "root_redacted": True,
    }


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path.resolve(strict=False))


def _display_path(raw_path: str) -> str:
    return _escape_unsafe_display_chars(unicodedata.normalize("NFC", raw_path))


def _escape_unsafe_display_chars(value: str) -> str:
    return "".join(_safe_identity_char(char) for char in value)


def _installed_version(name: str) -> str | None:
    if not name:
        return None
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def _hash_records(records: list[dict]) -> str:
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()
