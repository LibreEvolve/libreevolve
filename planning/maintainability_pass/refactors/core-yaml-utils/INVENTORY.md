# `core/yaml_utils.py` Wave 1 Inventory

Primary file: `libreevolve/core/yaml_utils.py`
Lane: `core-yaml-utils`
Agent: `01a069d1-2ef9-7e61-bb9c-d646589ed973`
Status: interim checkpoint; characterization barrier not passed

## Measurements and contracts

The module is 67 physical lines, 54 nonblank/noncomment logical lines, one
`UniqueKeyLoader` class, and four explicit definitions:
`compose_node`, `_construct_unique_mapping`, `safe_load_unique`, and
`redacted_yaml_error`. It depends on PyYAML and redaction. Direct consumers are
`problems/loader.py`, CLI, and loader tests; loader has 11 parser and 10 error
formatter call sites.

Duplicate keys, aliases/anchors, unhashable keys, unknown tags, multi-document
input, implicit types, merge keys, empty/null documents, and non-string keys
must retain their current PyYAML/custom-loader semantics. Config schema
validation belongs to `core/config.py`; file selection, hashes, top-level
mapping checks, and domain normalization belong to loader/CLI.

Child A and B completed read-only reviews and were closed. No tests were run or
files changed. A source finding is recorded: `loader.py` uses
`safe_load_unique(...) or {}` for context, so falsey non-mapping documents
(`[]`, `false`, `0`) can bypass the documented mapping check.

Proposed seam: a shared setup-YAML parsing boundary that preserves loader/error
compatibility, without moving file selection, provenance, domain schemas, or
`.env` policy. Caller handoffs to `loader.py` and `cli.py` are required.
