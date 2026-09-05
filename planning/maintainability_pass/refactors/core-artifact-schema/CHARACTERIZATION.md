# `core/artifact_schema.py` Characterization Gate

Status: `blocked` for this lane's current wave; not a project-wide blocker.

Before movement, characterize schema factory/deep-copy/versioned-record
behavior; generated inventory completeness and deterministic ordering; invalid
manifests, pointers, hashes, quarantine rows, bundle/restore overclaims;
legacy missing markers; optional paper artifacts; exact artifact-name equality;
cleanup preserving foreign files; path/link policy; and retention/redaction
handoffs for `full`, `redacted`, `hash_only`, and `off`. Use the existing
database, CLI, loop, JSONL, redaction, and meta-prompt contract tests plus a
dedicated `tests/core/test_artifact_schema.py` only where coverage is missing.

The focused suite is green as reported, but the required independent child
review and characterization-test strengthening did not occur. Do not treat the
focused result as permission to extract production code.
