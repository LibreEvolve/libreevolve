# `core/config.py` Characterization Gate

Status: characterization complete; production seam remains blocked pending
design review and explicit ownership handoffs.

The test-only specialist added focused normalization, validation-idempotence,
CLI handoff, manifest/runtime persistence, and malformed-YAML cases. The
Windows Python 3.12 run reports `639 passed`; compilation passed.

The coupling review found Config is already the schema/policy authority and
should not absorb YAML or loader policy. A production writer must use a narrow
pure normalization seam, preserve repeated validation and CLI/direct parity,
and coordinate evaluator/candidate-runner declarations with adjacent owners.

Before extraction, test defaults and overrides; invalid top-level/nested
schemas; candidate declarations and execution environments; stages/backends,
roles/prompts, environment allowlists, paths, identifiers; in-place mutation
and repeated validation; manifest serialization and runtime revalidation; CLI
versus direct construction; malformed/duplicate/alias YAML handoffs; and
platform-specific path/encoding behavior. Preserve error types/messages where
they are public or serialized, field order, normalized values, and all private
compatibility imports.

No production writer is authorized until the baseline/after metrics and caller
handoffs with `cli.py`, `yaml_utils.py`, `loader.py`, `database.py`, and
`evaluator.py` are recorded by the file lead.
