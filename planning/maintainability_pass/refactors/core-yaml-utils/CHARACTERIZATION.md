# `core/yaml_utils.py` Characterization Gate

Status: `unverified` / not passed.

Characterize normal mappings, empty/null, nested and semantically colliding
keys, merges, malformed syntax, aliases/anchors, unhashable keys, implicit
types, UTF-8 failures, redaction, non-mapping documents, file/link errors,
deterministic provenance, and native-Windows junction behavior. Add a focused
parser test only after confirming the current loader tests do not already own
the behavior. The falsey non-mapping loader path must be separately diagnosed
and handed to `problems/loader.py`; do not silently fix it in this primary lane.
