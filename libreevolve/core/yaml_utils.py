from __future__ import annotations

import yaml

from libreevolve.core.redaction import redact_sensitive_text


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML SafeLoader variant that rejects duplicate mapping keys."""

    def compose_node(self, parent, index):
        if self.check_event(yaml.events.AliasEvent):
            event = self.peek_event()
            raise yaml.constructor.ConstructorError(
                "while composing a YAML node",
                event.start_mark,
                "YAML aliases are not supported in setup files",
                event.start_mark,
            )
        event = self.peek_event()
        if getattr(event, "anchor", None) is not None:
            raise yaml.constructor.ConstructorError(
                "while composing a YAML node",
                event.start_mark,
                "YAML anchors are not supported in setup files",
                event.start_mark,
            )
        return super().compose_node(parent, index)


def _construct_unique_mapping(loader: UniqueKeyLoader, node, deep: bool = False):
    loader.flatten_mapping(node)
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in seen
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found unhashable key {key!r}",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        seen.add(key)
    return loader.construct_mapping(node, deep=deep)


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def safe_load_unique(text: str):
    return yaml.load(text, Loader=UniqueKeyLoader)


def redacted_yaml_error(exc: yaml.YAMLError) -> str:
    return redact_sensitive_text(str(exc))
