# `core/artifact_schema.py` Wave 1 Inventory

Primary file: `libreevolve/core/artifact_schema.py`
Lane: `core-artifact-schema`
Agent: `01a069d0-976e-7423-836d-d80aa4c39372`
Status: inventory complete; characterization barrier not passed

## Measurements and contracts

The module is 2,158 physical/logical-scale lines with 23 top-level functions,
29 declarations, 412 statement nodes, and a module complexity proxy of 166
(188 summed across functions). It defines 24 generated artifact names, 10
accepted JSONL streams, 7 quarantine streams, 7 non-JSONL artifacts, and 11
paper-artifact paths. The largest functions are
`validate_run_artifact_bundle_report` (243 lines),
`validate_paper_artifact_lifecycle_manifest` (191),
`_runtime_restore_certification_issues` (121), and
`_validate_non_jsonl_pointer_policy` (102).

Responsibilities combine declarative schemas, schema assembly, generated
inventory, paper lifecycle validation, restore certification, and artifact
policy validation. `RUN_ARTIFACT_NAMES` drives cleanup and runtime pointers.
Consumers include database, loop, meta-prompt, ensemble, CLI, benchmarks, and
tests. Redaction/quarantine serialization remains owned by `jsonl.py` and
`redaction.py`; `versioned_record` overwrites markers but is not a migration.
Mutable schema/anchor globals are generally copied before return but remain
patchable compatibility data.

Existing focused evidence reported by the agent was 188 passed, 2 skipped,
zero failures across artifact/database/runtime/CLI/meta-prompt/docs/JSONL/
redaction/LLM slices in an isolated environment. This is focused test evidence
only, not a current full-suite or independent-verifier result.

## Proposed seam and boundary

Proposed new pure `libreevolve/core/artifact_contracts.py` for schema IDs,
artifact sets, anchor maps, paper subpaths, and registry assembly. Keep
validators and compatibility-facing APIs in `artifact_schema.py` as a facade;
preserve all consumer imports. The direction is
`artifact_contracts -> artifact_schema -> database/loop/cli`, with JSONL and
redaction remaining lower-level owners.

No child reviewers were schedulable: the agent recorded
`collab spawn failed: agent thread limit reached`. No source/test/docs/Git
changes were made. The implementation writer remains prohibited.
