# Wave 1 changed-path ledger

Captured during the 2026-09-03 coordination run. This ledger separates
authorized characterization additions and the first production seam from the
260 tracked/index status records captured before this refactor.

## Coordination-owned additions

- `tests/core/test_budget.py`: characterization-only additions; root Windows
  focused result `150 passed`.
- `tests/core/test_meta_prompt.py`: characterization-only additions plus two
  expectation corrections; root Windows focused result `94 passed`.
- `tests/test_cli_characterization.py`: new characterization-only test module;
  root focused result `9 passed, 2 skipped`.
- `libreevolve/problems/loader.py`: production compatibility façade changed by
  the loader writer; root focused result `279 passed, 8 skipped`.
- `libreevolve/problems/context_loader.py`: new production support module for
  context ingestion, manifests, diagnostics, excerpts, hashing, and lazy PDF
  normalization.
- `libreevolve/core/loop.py`: compatibility imports for the extracted immutable
  loop records; orchestration and side effects remain in place.
- `libreevolve/core/loop_models.py`: new data-only module containing the four
  frozen private loop value records. Independent verification passed; full
  loop regression remains a separate gate.
- `libreevolve/core/run_inspection.py`: new Click-free read-only inspection
  seam for the CLI `show` path. The CLI retains parsing, formatting, export,
  rollback, and compatibility source anchors.
- `libreevolve/cli.py`: current production seam includes thin legacy wrappers
  required by the generated artifact inventory; combined CLI tests report
  `271 passed, 6 skipped`.
- `libreevolve/core/jsonl.py`: delegates only the serialized-line append
  primitive to `libreevolve/core/jsonl_storage.py`; JSONL validation, locking,
  repair, quarantine, redaction, and durability policy remain in the façade.
- `libreevolve/core/artifact_schema.py`: delegates only JSONL/quarantine record
  family declarations to `libreevolve/core/artifact_schema_record_contracts.py`;
  schema validation, redaction, quarantine materialization, and inventory
  ownership remain in the façade.
- `libreevolve/core/budget.py`: delegates the synchronous contract kernel to
  `libreevolve/core/budget_contract.py`; `RunBudget`, clocks, replay,
  persistence, async concerns, and provider/evaluator accounting remain in the
  façade. Focused evidence is `150 passed`, with a WSL untracked-mode
  qualification.
- `libreevolve/core/prompt.py`: delegates context-policy validation to
  `libreevolve/core/prompt_context_policy.py`; rendering, RNG, mutable
  `last_*` state, feedback/failure rendering, and prompt history remain in the
  façade. Independent focused verification is `390 passed` and PASS.
- `libreevolve/problems/benchmarks/matrix_results.py`: façade now delegates
  low-level artifact identity and canonical JSON operations.
- `libreevolve/problems/benchmarks/matrix_artifact_identity.py`: new neutral
  helper for deterministic serialization, file identity, safe paths, and one
  artifact inventory record.
- `tests/core/test_loop_characterization.py`: new loop characterization tests;
  root result `11 passed`; full `tests/core/test_loop.py` regression reports
  `465 passed, 2 skipped`.
- `tests/test_matrix_results.py`: characterization additions; root result
  `145 passed`.
- `tests/population/test_database.py`: characterization additions; current
  focused result `292 passed, 3 skipped`.
- `planning/maintainability_pass/refactors/reports/**`: per-lane inventory,
  characterization, verification, and orchestration evidence.

Database, best-artifacts, feedback, meta-prompt, config, and YAML utilities
remain characterization/no-op or deferred lanes with no production writer.
The JSONL lane remains conditional on its known repair atomicity boundary; the
artifact-schema lane is PASS; the budget lane is conditional only for the
WSL/untracked mode observation; and the prompt lane is PASS. The CLI, loader,
matrix, and loop seams were each kept to their locked write scopes and reviewed
by independent non-authoring verifiers; CLI and matrix verdicts retain a
shared-dirty-checkout attribution qualification.

## Pre-existing dirty paths preserved

`tests/core/test_loader.py` was already a tracked dirty path in `DIRTY_PATHS.md`
before this run. Its mixed line endings and `177/25` diff are not attributed to
the loader writer; the writer was instructed not to edit or normalize it.
Other tracked/index and untracked paths outside the coordination directory
remain user-owned and untouched.

## Integration policy

There were no commits, pushes, resets, cleans, broad stages, merges, or PRs.
Every production change remains subject to a fresh diff audit, an independent
non-authoring verifier, focused tests, and later module/full-suite checks. Test
passes here do not establish native-Windows CI, provider, OCI, distributed, or
end-to-end runtime evidence.
