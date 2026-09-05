# core/yaml_utils.py characterization

Evidence state: characterization complete; no production extraction is
recommended because the module is already small and pure.

The test-only specialist added
`tests/core/test_yaml_utils_characterization.py`, covering parser shapes/types,
Unicode, duplicate keys, malformed YAML, anchors/aliases, redaction, metrics,
context manifests, optional metadata, and falsey/null seed-policy behavior.
It reports `54 passed`; the combined loader/boundary suite reports `339
passed, 8 skipped`, with compilation passing.

The coupling review confirmed that `yaml_utils.py` should remain the pure
parser façade and that schema/file policy belongs to Config and Problem. The
former falsey-loader hazard is no longer present in the extracted context
loader. No YAML production writer is authorized or needed. Missing edge cases
include unhashable keys, unknown tags, multi-document input, merge-key
semantics, and explicit CLI falsey cases.
