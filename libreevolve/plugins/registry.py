from __future__ import annotations

from dataclasses import dataclass
from email.parser import Parser
import hashlib
from importlib import metadata
import math
from pathlib import Path
import re
from weakref import WeakKeyDictionary

from libreevolve.plugins.base import PluginBase
from libreevolve.plugins import causal, deep_research, modular, ttt_rl


class PluginRegistryError(ValueError):
    """Raised when a configured plugin cannot be resolved or validated."""


@dataclass(frozen=True)
class PluginDefinition:
    label: str
    plugin_class: type
    option_schema: dict[str, dict]
    paper_inspiration: str


_POSITIVE_INT = {"type": "positive_int"}
_PATH = {"type": "path"}
_ENTRY_POINT_LABEL = "entry_point"
_PLUGIN_LABEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
_ENTRY_POINT_WHEEL_MAX_TAGS = 8
_ENTRY_POINT_SCHEMA = {
    "group": {"type": "enum", "values": {"libreevolve.plugins"}},
    "name": {"type": "plugin_label"},
    "paper_inspiration": {"type": "plugin_label"},
    "constructor_options": {"type": "constructor_options"},
}
_ENTRY_POINT_PLUGIN_SPECS: WeakKeyDictionary[object, dict] = WeakKeyDictionary()
_CONSTRUCTOR_SCHEMA_ATTRIBUTE = "libreevolve_constructor_option_schema"
_CONSTRUCTOR_SCHEMA_ALLOWED_KEYS = {"type", "values", "required"}
_CONSTRUCTOR_SCHEMA_TYPES = {
    "bool",
    "boolean",
    "enum",
    "int",
    "integer",
    "manifest_safe_json",
    "nonnegative_int",
    "number",
    "path",
    "plugin_label",
    "positive_int",
    "string",
}


def builtin_plugin_registry() -> dict[str, PluginDefinition]:
    return {
        "causal": PluginDefinition(
            label="causal",
            plugin_class=causal.CausalPlugin,
            option_schema={"history_limit": _POSITIVE_INT},
            paper_inspiration="CausalEvolve",
        ),
        "deep_research": PluginDefinition(
            label="deep_research",
            plugin_class=deep_research.DeepResearchPlugin,
            option_schema={
                "search_every": _POSITIVE_INT,
                "max_events": _POSITIVE_INT,
                "cache_mode": {"type": "enum", "values": {"live", "cached", "offline"}},
                "cache_dir": _PATH,
                "retrieval_body_retention_mode": {
                    "type": "enum",
                    "values": {"full", "redacted", "hash_only", "off"},
                },
                "source_ranking_policy": {
                    "type": "enum",
                    "values": {
                        "provider_order_retained_v1",
                        "query_overlap_score_desc_v1",
                    },
                },
            },
            paper_inspiration="DeepEvolve",
        ),
        "modular": PluginDefinition(
            label="modular",
            plugin_class=modular.ModularPlugin,
            option_schema={},
            paper_inspiration="ImprovEvolve",
        ),
        "ttt_rl": PluginDefinition(
            label="ttt_rl",
            plugin_class=ttt_rl.TTTRLPlugin,
            option_schema={
                "train_every": _POSITIVE_INT,
                "log_dir": _PATH,
                "max_retained_examples": _POSITIVE_INT,
                "max_payload_field_chars": _POSITIVE_INT,
                "max_payload_total_chars": _POSITIVE_INT,
            },
            paper_inspiration="ThetaEvolve",
        ),
    }


def available_plugin_names() -> list[str]:
    return [*builtin_plugin_registry(), _ENTRY_POINT_LABEL]


def plugin_class_registry() -> dict[str, type]:
    return {
        label: definition.plugin_class
        for label, definition in builtin_plugin_registry().items()
    }


def validate_plugin_specs(specs: list[object]) -> list[dict]:
    return [
        validate_plugin_spec(spec, index=index)
        for index, spec in enumerate(specs)
    ]


def validate_plugin_spec(spec: object, *, index: int = 0) -> dict:
    label, options = _split_plugin_spec(spec, index=index)
    registry = builtin_plugin_registry()
    if label == _ENTRY_POINT_LABEL:
        validated_options = _validate_options(label, options, _ENTRY_POINT_SCHEMA)
        entry_point = _resolve_entry_point_spec(validated_options, load_target=True)
        return {
            "label": label,
            "options": validated_options,
            "paper_inspiration": entry_point["paper_inspiration"],
            "schema": "libreevolve.plugin_config.v1",
            "entry_point": entry_point,
        }
    if label not in registry:
        raise _unknown_plugin(label, registry)
    definition = registry[label]
    return {
        "label": label,
        "options": _validate_options(label, options, definition.option_schema),
        "paper_inspiration": definition.paper_inspiration,
        "schema": "libreevolve.plugin_config.v1",
    }


def load_plugins(specs: list[object], run_dir: Path | None = None) -> list:
    resolved = validate_plugin_specs(specs)
    registry = builtin_plugin_registry()
    plugins = []
    for spec in resolved:
        label = spec["label"]
        if label == _ENTRY_POINT_LABEL:
            plugins.append(_load_entry_point_plugin(spec["entry_point"]))
            continue
        kwargs = dict(spec["options"])
        _apply_run_scoped_defaults(label, kwargs, run_dir)
        plugins.append(registry[label].plugin_class(**kwargs))
    return plugins


def configured_plugin_labels(specs: list[object]) -> list[str]:
    labels: list[str] = []
    for index, spec in enumerate(specs):
        label, _ = _split_plugin_spec(spec, index=index)
        labels.append(label)
    return labels


def plugin_entry_point_spec(plugin: object) -> dict | None:
    spec = getattr(plugin, "_libreevolve_entry_point_spec", None)
    if isinstance(spec, dict):
        return dict(spec)
    try:
        mapped = _ENTRY_POINT_PLUGIN_SPECS.get(plugin)
    except TypeError:
        return None
    return dict(mapped) if isinstance(mapped, dict) else None


def _split_plugin_spec(spec: object, *, index: int) -> tuple[str, dict]:
    if isinstance(spec, str):
        return spec, {}
    if not isinstance(spec, dict):
        raise PluginRegistryError(
            f"plugins[{index}] must be a plugin label or plugin spec mapping"
        )
    label = spec.get("name")
    if not isinstance(label, str):
        raise PluginRegistryError(f"plugins[{index}].name must be a string")
    options = spec.get("options", {})
    if not isinstance(options, dict):
        raise PluginRegistryError(f"plugins[{index}].options must be a mapping")
    return label, dict(options)


def _validate_options(label: str, options: dict, schema: dict[str, dict]) -> dict:
    unknown = sorted(set(options) - set(schema))
    if unknown:
        raise PluginRegistryError(
            f"Plugin {label!r} has unknown option(s): {unknown}. "
            f"Available options: {list(schema)}"
        )
    validated = {}
    for name, value in options.items():
        validated[name] = _validate_option(label, name, value, schema[name])
    return validated


def _validate_option(label: str, name: str, value: object, schema: dict) -> object:
    kind = schema["type"]
    if kind == "positive_int":
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a positive integer"
            )
        return value
    if kind == "enum":
        values = schema["values"]
        if value not in values:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be one of: {sorted(values)}"
            )
        return value
    if kind == "path":
        if not isinstance(value, str) or not value:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a non-empty path string"
            )
        return value
    if kind == "plugin_label":
        if not isinstance(value, str) or not value:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a plugin label"
            )
        if _PLUGIN_LABEL_RE.fullmatch(value) is None:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a manifest-safe plugin label"
            )
        return value
    if kind == "constructor_options":
        return _validate_constructor_options(label, name, value)
    raise AssertionError(f"Unhandled plugin option schema: {kind}")


def _resolve_entry_point_spec(options: dict, *, load_target: bool) -> dict:
    group = options["group"]
    name = options["name"]
    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        matches = list(entry_points.select(group=group, name=name))
    else:
        matches = [
            item
            for item in entry_points.get(group, [])
            if getattr(item, "name", None) == name
        ]
    if not matches:
        raise PluginRegistryError(
            f"Plugin entry point {group!r}:{name!r} was not found"
        )
    if len(matches) > 1:
        raise PluginRegistryError(
            f"Plugin entry point {group!r}:{name!r} resolved to multiple targets"
        )
    entry_point = matches[0]
    constructor_options = dict(options.get("constructor_options", {}))
    constructor_schema = None
    if load_target:
        target = _load_entry_point_target(entry_point, group=group, name=name)
        constructor_schema = _entry_point_constructor_option_schema(
            target,
            label=f"Plugin entry point {group!r}:{name!r}",
        )
        if constructor_schema is not None:
            constructor_options = _validate_constructor_options(
                _ENTRY_POINT_LABEL,
                "constructor_options",
                constructor_options,
                schema=constructor_schema,
            )
    record = {
        "schema": "libreevolve.plugin_entry_point.v1",
        "group": group,
        "name": name,
        "value": str(getattr(entry_point, "value", "")),
        "paper_inspiration": options.get(
            "paper_inspiration",
            "external_plugin_entry_point",
        ),
        "distribution": _entry_point_distribution(entry_point),
        "constructor_options_captured": "constructor_options" in options,
        "constructor_option_policy": (
            "declared_constructor_option_schema_v1"
            if constructor_schema is not None
            else "manifest_safe_json_values"
        ),
    }
    if constructor_schema is not None:
        record["constructor_option_schema"] = constructor_schema
    if "constructor_options" in options:
        record["constructor_options"] = constructor_options
    if load_target:
        record["loaded"] = True
    return record


def _load_entry_point_plugin(entry_point_spec: dict) -> PluginBase:
    group = entry_point_spec["group"]
    name = entry_point_spec["name"]
    constructor_options = entry_point_spec.get("constructor_options", {})
    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        matches = list(entry_points.select(group=group, name=name))
    else:
        matches = [
            item
            for item in entry_points.get(group, [])
            if getattr(item, "name", None) == name
        ]
    if len(matches) != 1:
        raise PluginRegistryError(
            f"Plugin entry point {group!r}:{name!r} is no longer uniquely available"
        )
    entry_point = matches[0]
    target = _load_entry_point_target(entry_point, group=group, name=name)
    try:
        plugin = target(**constructor_options)
    except Exception as exc:
        raise PluginRegistryError(
            f"Plugin entry point {group!r}:{name!r} failed to instantiate: {exc}"
        ) from exc
    spec = dict(entry_point_spec)
    spec["loaded"] = True
    try:
        setattr(plugin, "_libreevolve_entry_point_spec", spec)
    except Exception:
        try:
            _ENTRY_POINT_PLUGIN_SPECS[plugin] = spec
        except TypeError:
            pass
    return plugin


def _load_entry_point_target(entry_point: object, *, group: str, name: str) -> type[PluginBase]:
    try:
        target = entry_point.load()
    except Exception as exc:
        raise PluginRegistryError(
            f"Plugin entry point {group!r}:{name!r} failed to load: {exc}"
        ) from exc
    if not isinstance(target, type) or not issubclass(target, PluginBase):
        raise PluginRegistryError(
            f"Plugin entry point {group!r}:{name!r} must load a PluginBase subclass"
        )
    return target


def _entry_point_constructor_option_schema(target: type, *, label: str) -> dict | None:
    schema = getattr(target, _CONSTRUCTOR_SCHEMA_ATTRIBUTE, None)
    if schema is None:
        return None
    return _validate_constructor_option_schema(label, schema)


def _validate_constructor_option_schema(label: str, schema: object) -> dict:
    if not isinstance(schema, dict):
        raise PluginRegistryError(
            f"{label} {_CONSTRUCTOR_SCHEMA_ATTRIBUTE} must be a mapping"
        )
    validated: dict[str, dict] = {}
    for name, spec in schema.items():
        if not isinstance(name, str) or _PLUGIN_LABEL_RE.fullmatch(name) is None:
            raise PluginRegistryError(
                f"{label} constructor schema keys must be manifest-safe plugin labels"
            )
        if not isinstance(spec, dict):
            raise PluginRegistryError(
                f"{label} constructor schema {name!r} must be a mapping"
            )
        unknown = sorted(set(spec) - _CONSTRUCTOR_SCHEMA_ALLOWED_KEYS)
        if unknown:
            raise PluginRegistryError(
                f"{label} constructor schema {name!r} has unsupported fields {unknown}"
            )
        kind = spec.get("type")
        if kind not in _CONSTRUCTOR_SCHEMA_TYPES:
            raise PluginRegistryError(
                f"{label} constructor schema {name!r}.type must be one of: "
                f"{sorted(_CONSTRUCTOR_SCHEMA_TYPES)}"
            )
        required = spec.get("required", False)
        if not isinstance(required, bool):
            raise PluginRegistryError(
                f"{label} constructor schema {name!r}.required must be boolean"
            )
        record = {"type": kind}
        if required:
            record["required"] = True
        if kind == "enum":
            values = _validate_constructor_schema_enum_values(label, name, spec.get("values"))
            record["values"] = values
        elif "values" in spec:
            raise PluginRegistryError(
                f"{label} constructor schema {name!r}.values is only supported for enum"
            )
        validated[name] = record
    return validated


def _validate_constructor_schema_enum_values(label: str, name: str, values: object) -> list[str]:
    if not isinstance(values, (list, tuple, set)) or not values:
        raise PluginRegistryError(
            f"{label} constructor schema {name!r}.values must be a non-empty list"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value:
            raise PluginRegistryError(
                f"{label} constructor schema {name!r}.values[{index}] must be a non-empty string"
            )
        if any(ord(ch) < 32 for ch in value):
            raise PluginRegistryError(
                f"{label} constructor schema {name!r}.values[{index}] must be manifest-safe"
            )
        if value not in seen:
            seen.add(value)
            normalized.append(value)
    return sorted(normalized)


def _entry_point_distribution(entry_point: object) -> dict:
    distribution = getattr(entry_point, "dist", None)
    if distribution is None:
        return {"status": "unavailable"}
    metadata_value = getattr(distribution, "metadata", None)
    name = None
    if metadata_value is not None:
        try:
            name = metadata_value.get("Name")
        except Exception:
            name = None
    if name is None:
        name = getattr(distribution, "name", None)
    version = getattr(distribution, "version", None)
    name_text = str(name or "")
    version_text = str(version or "")
    return {
        "status": "available",
        "policy": "entry_point_distribution_name_version_hash_v1",
        "name": name_text,
        "name_sha256": _hash_text(name_text),
        "version": version_text,
        "version_sha256": _hash_text(version_text),
        "record_metadata": _entry_point_distribution_record_metadata(distribution),
        "wheel_metadata": _entry_point_distribution_wheel_metadata(distribution),
    }


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _entry_point_distribution_record_metadata(distribution: object) -> dict:
    reader = getattr(distribution, "read_text", None)
    if not callable(reader):
        return {"status": "unavailable", "reason": "distribution_read_text_missing"}
    try:
        record_text = reader("RECORD")
    except FileNotFoundError:
        return {"status": "missing"}
    except Exception as exc:
        return {
            "status": "read_error",
            "error_type": exc.__class__.__name__,
            "error": str(exc)[:200],
        }
    if record_text is None:
        return {"status": "missing"}
    if not isinstance(record_text, str):
        return {
            "status": "invalid",
            "reason": "distribution_record_not_text",
            "value_type": type(record_text).__name__,
        }
    lines = record_text.splitlines()
    return {
        "status": "available",
        "policy": "distribution_record_hash_only_v1",
        "record_sha256": _hash_text(record_text),
        "line_count": len(lines),
        "bytes": len(record_text.encode("utf-8")),
    }


def _entry_point_distribution_wheel_metadata(distribution: object) -> dict:
    reader = getattr(distribution, "read_text", None)
    if not callable(reader):
        return {"status": "unavailable", "reason": "distribution_read_text_missing"}
    try:
        wheel_text = reader("WHEEL")
    except FileNotFoundError:
        return {"status": "missing"}
    except Exception as exc:
        return {
            "status": "read_error",
            "error_type": exc.__class__.__name__,
            "error": str(exc)[:200],
        }
    if wheel_text is None:
        return {"status": "missing"}
    if not isinstance(wheel_text, str):
        return {
            "status": "invalid",
            "reason": "distribution_wheel_not_text",
            "value_type": type(wheel_text).__name__,
        }
    message = Parser().parsestr(wheel_text)
    tags = message.get_all("Tag") or []
    return {
        "status": "available",
        "policy": "distribution_wheel_bounded_metadata_v1",
        "wheel_sha256": _hash_text(wheel_text),
        "bytes": len(wheel_text.encode("utf-8")),
        "tag_count": len(tags),
        "max_retained_tags": _ENTRY_POINT_WHEEL_MAX_TAGS,
        "retained_tags": [
            _wheel_field_record(tag)
            for tag in tags[:_ENTRY_POINT_WHEEL_MAX_TAGS]
        ],
        "omitted_tag_count": max(0, len(tags) - _ENTRY_POINT_WHEEL_MAX_TAGS),
        "wheel_version_present": message.get("Wheel-Version") is not None,
        "generator_present": message.get("Generator") is not None,
        "root_is_purelib_present": message.get("Root-Is-Purelib") is not None,
        "wheel_version": _optional_wheel_field_record(message.get("Wheel-Version")),
        "generator": _optional_wheel_field_record(message.get("Generator")),
        "root_is_purelib": _optional_wheel_field_record(
            message.get("Root-Is-Purelib")
        ),
    }


def _optional_wheel_field_record(value: str | None) -> dict | None:
    if value is None:
        return None
    return _wheel_field_record(value)


def _wheel_field_record(value: str) -> dict:
    return {"value": value, "sha256": _hash_text(value)}


def _validate_constructor_options(
    label: str,
    name: str,
    value: object,
    *,
    schema: dict | None = None,
) -> dict:
    if not isinstance(value, dict):
        raise PluginRegistryError(
            f"Plugin {label!r} option {name!r} must be a mapping"
        )
    if schema is not None:
        unknown = sorted(set(value) - set(schema))
        if unknown:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} has unknown option(s): {unknown}. "
                f"Available options: {list(schema)}"
            )
        missing = sorted(
            option_name
            for option_name, option_schema in schema.items()
            if option_schema.get("required") and option_name not in value
        )
        if missing:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} is missing required option(s): {missing}"
            )
        return {
            key: _validate_schema_constructor_option_value(
                label,
                f"{name}.{key}",
                item,
                schema[key],
            )
            for key, item in value.items()
        }
    validated: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str) or _PLUGIN_LABEL_RE.fullmatch(key) is None:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} keys must be manifest-safe plugin labels"
            )
        validated[key] = _validate_constructor_option_value(
            label,
            f"{name}.{key}",
            item,
        )
    return validated


def _validate_schema_constructor_option_value(
    label: str,
    name: str,
    value: object,
    schema: dict,
) -> object:
    kind = schema["type"]
    if kind in {"bool", "boolean"}:
        if not isinstance(value, bool):
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be boolean"
            )
        return value
    if kind in {"int", "integer"}:
        if isinstance(value, bool) or not isinstance(value, int):
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be an integer"
            )
        return value
    if kind == "nonnegative_int":
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a non-negative integer"
            )
        return value
    if kind == "positive_int":
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a positive integer"
            )
        return value
    if kind == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a finite number"
            )
        return value
    if kind == "string":
        if not isinstance(value, str) or any(ord(ch) < 32 for ch in value):
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a manifest-safe string"
            )
        return value
    if kind == "path":
        if not isinstance(value, str) or not value:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a non-empty path string"
            )
        return value
    if kind == "plugin_label":
        if not isinstance(value, str) or _PLUGIN_LABEL_RE.fullmatch(value) is None:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be a manifest-safe plugin label"
            )
        return value
    if kind == "enum":
        if value not in schema["values"]:
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be one of: {schema['values']}"
            )
        return value
    if kind == "manifest_safe_json":
        return _validate_constructor_option_value(label, name, value)
    raise AssertionError(f"Unhandled constructor option schema: {kind}")


def _validate_constructor_option_value(
    label: str,
    name: str,
    value: object,
) -> object:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be finite JSON"
            )
        return value
    if isinstance(value, str):
        if any(ord(ch) < 32 for ch in value):
            raise PluginRegistryError(
                f"Plugin {label!r} option {name!r} must be manifest-safe JSON"
            )
        return value
    if isinstance(value, list):
        return [
            _validate_constructor_option_value(label, f"{name}[{index}]", item)
            for index, item in enumerate(value)
        ]
    if isinstance(value, dict):
        nested: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str) or _PLUGIN_LABEL_RE.fullmatch(key) is None:
                raise PluginRegistryError(
                    f"Plugin {label!r} option {name!r} keys must be manifest-safe plugin labels"
                )
            nested[key] = _validate_constructor_option_value(
                label,
                f"{name}.{key}",
                item,
            )
        return nested
    raise PluginRegistryError(
        f"Plugin {label!r} option {name!r} must be JSON-safe"
    )


def _apply_run_scoped_defaults(label: str, kwargs: dict, run_dir: Path | None) -> None:
    if run_dir is None:
        return
    if label == "ttt_rl" and "log_dir" not in kwargs:
        kwargs["log_dir"] = str(run_dir / "plugin_artifacts" / "ttt_rl")
    elif label == "deep_research" and "cache_dir" not in kwargs:
        kwargs["cache_dir"] = run_dir / "plugin_artifacts" / "deep_research"


def _unknown_plugin(name: str, registry: dict) -> PluginRegistryError:
    return PluginRegistryError(
        f"Unknown plugin: {name!r}. Available: {available_plugin_names()}"
    )
