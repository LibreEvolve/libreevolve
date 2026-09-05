# core/yaml_utils.py refactor record

Evidence state: confirmed no-production-change decision; this lane does not
propose an extraction.

## Scope and measured shape

Primary file: `libreevolve/core/yaml_utils.py`.

The existing inventory measures the module at approximately 67 physical lines,
with one class and four functions. It is already a small, pure parsing facade:

- `UniqueKeyLoader` extends `yaml.SafeLoader` and rejects YAML aliases and
  anchors used in setup files.
- `_construct_unique_mapping` constructs mappings while rejecting duplicate and
  unhashable keys.
- `safe_load_unique` is the public decoding entry point.
- `redacted_yaml_error` converts YAML errors to redacted diagnostic text.

The module has no configuration schema, problem-file policy, filesystem
ownership, evaluator metric authority, or mutable search state. Introducing a
new production seam would add indirection without reducing a material hotspot.

## Decision

No production code is changed. Keep `yaml_utils.py` as the narrow, reusable
parser boundary. Do not move configuration defaults or schema policy into it,
and do not move problem metadata, seed-policy, context-file, or workspace
selection rules into it.

This is a deliberate no-op refactor outcome, not evidence that the broader
configuration or problem-loading surfaces are fully verified. The former
falsey-loader hazard is addressed at the context-loader boundary; it does not
justify widening this utility's ownership.

## Contract ownership

- `yaml_utils.py`: safe YAML decoding, duplicate-key rejection, anchor/alias
  rejection, unhashable-key diagnostics, and redaction of YAML error text.
- `libreevolve/core/config.py`: configuration schema, defaults, coercion, and
  semantic validation.
- `libreevolve/problems/loader.py` and its context-loading support: file names,
  required versus optional metadata, mapping validation, seed policy, and
  workspace/problem ownership.
- CLI/reporting layers: user-facing formatting and exit-code policy.

The boundary must preserve exception behavior, decoded value shapes, Unicode
handling, and diagnostic redaction. No serialized artifact or runtime behavior
is intentionally changed by this lane.

## Characterization coverage

The test-only characterization record reports 54 passing focused tests for
parser shapes and types, Unicode, duplicate keys, malformed YAML,
anchors/aliases, redaction, metrics, context manifests, optional metadata, and
falsey/null seed-policy behavior. The combined loader/boundary suite reports
339 passed and 8 skipped, with compilation passing.

Remaining characterization gaps are explicit: unhashable keys, unknown YAML
tags, multi-document input, merge-key semantics, and explicit CLI falsey
cases. These are follow-up coverage items; they are not silently treated as
covered by the existing 54 tests.

## Lane disposition

There is no implementation patch, support module, migration shim, dependency
edge, or rollback operation for this lane. A separate production writer is not
authorized or needed unless a future call-graph review identifies a concrete
parser responsibility that can be extracted without moving policy authority.
