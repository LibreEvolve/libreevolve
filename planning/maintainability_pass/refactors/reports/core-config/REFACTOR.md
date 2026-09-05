# core/config.py refactor record

Evidence state: characterization-backed; no semantic production seam was
completed or authorized for this lane.

## Scope and current checkout

Primary path: `libreevolve/core/config.py`.

The inventory measures the current module at 2,776 physical lines, 2,592
nonblank lines, 2,587 token-line proxy, two classes, and 86 module-level
functions. `Config.validate` and the nested evaluator, backend,
candidate-build, execution-environment, hypothesis-test, and feedback
validators are the principal measured hotspots. These are source-derived
measurements; there is no after-extraction measurement and no claim of
complexity or LOC reduction.

The Wave 0 baseline already listed `libreevolve/core/config.py` as a dirty
path. The current checkout still reports it as modified. A scoped comparison
with `git diff --ignore-space-at-eol` produces no remaining hunk; the current
file has 2,776 lines with five CRLF lines while the `HEAD` blob is LF-only.
The five representation changes are at the population/LLM section around
lines 174 and 184-187. `git diff --check` reports them as trailing
whitespace because of the mixed line endings. This is hygiene evidence and
unattributed representation churn within the pre-existing dirty baseline,
not a config refactor and not an ownership transfer to this lane. The
baseline records paths/status, so it does not provide a semantic attribution
for those individual bytes; they must remain preserved.

## Decision

No production config seam, support module, or config-specific test change was
completed or authorized by this record. In particular, there is no
`libreevolve/core/config_contract.py` implementation to verify. `config.py`
remains the configuration authority and the current dirty representation is
left untouched.

This is a deliberate documentation-only/no-op refactor outcome. It must not
be reported as a completed config extraction, a clean working-tree result, or
a full-suite result.

## Possible future pure seam

The inventory and coupling review identify a possible future
`libreevolve/core/config_contract.py` containing only pure contract
normalization/validation helpers. Any such seam would need to leave the
following in `config.py`:

- `Config`, `ConfigError`, defaults, constants, compatibility exports, and
  private compatibility symbols;
- configuration policy ownership and the observable `Config.validate()`
  mutation/normalization boundary;
- CLI `.env` loading and YAML parsing/problem-loading policy, which belong to
  their adjacent owners.

The seam is not ready for implementation without additional handoffs and a
writer allowlist. The main dependency risks are:

- `Config.validate()` mutates `log_dir` and nested mappings/lists; moving
  helpers can change mutation order, repeated-validation idempotence, or
  exception identity/messages.
- Database manifests and runtime revalidation make field names, ordering, and
  normalized values durable contracts.
- CLI, loop, evaluator, database, budget, async controllers, ensemble,
  island, and matrix-fixture callers import or consume configuration
  surfaces. CLI `.env` behavior and YAML/loader boundaries must not be pulled
  into the seam.
- Evaluator stages, backend/role declarations, candidate-runner toolchains,
  execution environments, paths, allowlists, and platform/encoding behavior
  cross adjacent ownership boundaries.

Before a future writer, record caller-by-caller ownership, exact before/after
metrics, private import anchors, field order, normalized values, and the
complete mutation/error contract. A future writer must be limited to
`config.py`, the proposed pure support module, and explicitly approved
focused tests; no caller changes are implied.

## Existing characterization evidence

The test-only characterization record reports a focused Windows Python 3.12
run of `639 passed`; compilation also passed. The exercised evidence covers
normalization, validation idempotence, CLI handoff, manifest/runtime
persistence, and malformed-YAML cases. This is current-tree focused evidence
and does not prove an extraction or attribute every dirty-worktree behavior
to this lane.

Required future characterization remains explicit: defaults and overrides;
invalid top-level and nested schemas; candidate declarations and execution
environments; stages/backends and roles/prompts; environment allowlists,
paths, and identifiers; in-place mutation and repeated validation; manifest
serialization and runtime revalidation; CLI/direct parity; malformed,
duplicate, and alias YAML handoffs; and platform-specific path/encoding
behavior.

## Rollback and no-op disposition

There is no semantic config patch to roll back. The rollback for this lane is
a no-op: preserve `config.py` and its pre-existing dirty-path attribution,
and do not normalize or revert the five mixed-ending lines. If a future seam
is explicitly authorized, rollback must remove only that seam and its approved
support/tests while preserving unrelated dirty work and the baseline
representation.

## Unverified gates

The focused result does not establish:

- the required repository suite,
  `py -3.12 -m pytest tests/ -m "not integration" --tb=short`;
- package/build/install, CLI smoke/exit-code, paper, documentation,
  artifact-freshness, or repository-wide diff-hygiene gates;
- independent verification of an implementation, after-extraction metrics,
  or exact byte/field-order compatibility;
- native-Windows, provider/integration, OCI, runtime, end-to-end,
  distributed, or hostile-code-sandbox behavior.

No config refactor, full-suite pass, or runtime claim is made by this report.
