# Maintainability refactor orchestration — final handoff

Captured: 2026-09-05
Checkout: `/mnt/c/users/timot/documents/projects/domains/libreevolve.com`
Branch: `master`
Baseline HEAD: `7983544e28e478eb6a0f5c35e4af5a86b125cea2`

## Outcome

The refactor was orchestrated as isolated, scoped lanes with one writer per
primary file, read-only slice reviews, fresh non-authoring verification, and
durable coordination records. The outcome is conditional and unmerged. It is
not a claim of repository-wide production readiness.

There are 15 original lanes and two explicitly recorded auxiliary roadmap
lanes. The three oversized targets have four read-only reviews each, including
the inventory review. There are 33 slice records and 17 internal PR packets.
No commit, push, branch creation, external PR, merge, reset, clean, stash, or
broad staging occurred. All 17 PR-index rows remain `pr_status: "not-opened"`.

## Lane disposition

| lane | disposition | evidence / production change |
| --- | --- | --- |
| `core-loop` | PASS | 465 passed, 2 skipped; frozen value-record seam in `loop_models.py` |
| `core-database` | NO-OP | 292 passed, 3 skipped; four reviews retain archive/restore/transaction coupling |
| `core-jsonl` | CONDITIONAL | 62 passed; raw append seam only; MR-009 remains open |
| `core-artifact-schema` | PASS | 86 focused passes; record-family declaration seam |
| `core-best-artifacts` | NO-OP / NOT READY | 5 passed, 2 skipped; exporter/rollback ownership remains coupled |
| `core-budget` | CONDITIONAL | 150 passed; contract seam; WSL/untracked mode qualification remains |
| `core-prompt` | PASS | 390 passed; context-policy seam; four reviews retain renderer/RNG boundaries |
| `core-feedback` | DEFERRED | 85 target passes; retention and sync/async ownership remain coupled |
| `core-meta-prompt` | BLOCKED / NO-OP | 94 passed; lifecycle and persistence handoff unresolved |
| `paper-manifest` | CONDITIONAL REPAIR | 717 module passes; MR-007 repair verified, later extraction deferred |
| `cli` | CONDITIONAL | 271 passed, 6 skipped and README boundary 4 passed; MR-014 remains open |
| `benchmark-matrix` | CONDITIONAL | 145 passed; dirty-tree attribution retained |
| `core-config` | NO-OP | 639 passed; validation/serialization policy kept together |
| `core-yaml-utils` | NO-OP | 54 focused passes; small pure parser kept in place |
| `problem-loader` | PASS | 279 passed, 8 skipped; context-loader seam verified |
| `roadmap-non-goal-boundary` | PASS, EOL-qualified | 5 focused tests, direct validator, compile and fresh source verification passed |
| `roadmap-non-goal-sidecar` | PASS, EOL-qualified | 27-file sidecar validator and 5 focused tests passed |

The authoritative records are [`FILE_MATRIX.json`](FILE_MATRIX.json),
[`PR_INDEX.jsonl`](PR_INDEX.jsonl), [`SLICES.jsonl`](SLICES.jsonl), the
internal packets, and the per-lane reports. The roadmap source lane consumes
the generated sidecar lane; they have separate primary paths and verifiers.

## Implemented seams

The verified local changes are narrow delegations: loop frozen value records;
CLI read-only run inspection; problem context loading; matrix artifact
identity; one serialized JSONL append primitive; artifact record-family
declarations; budget contract declarations; and prompt context-policy
validation. Mutable orchestration, archive/admission, RNG, feedback/failure
rendering, artifact replacement, schema validation, and paper authority remain
in their façades. The roadmap auxiliary change makes the non-planning Markdown
corpus boundary explicit and updates its generated sidecar.

## Measurements

These are source-shape measurements, not runtime or maintainability claims.

| primary | physical/nonblank before → current | support current |
| --- | ---: | ---: |
| `core/loop.py` | 49,605/47,918 → 49,548/47,867 | `loop_models.py` 77/67 |
| `cli.py` | 2,842/2,622 → 1,571/1,437 | `run_inspection.py` 1,469/1,342 |
| `matrix_results.py` | 7,534/7,164 → 7,443/7,079 | identity 132/119 |
| `loader.py` | 3,005/2,802 → 1,418/1,305 | context loader 1,658/1,550 |
| `jsonl.py` | 971/871 → 977/877 | storage 39/33 |
| `artifact_schema.py` | 2,158/2,096 → 2,138/2,076 | declarations 97/89 |
| `budget.py` | 1,497/1,385 → 548/510 | contract 1,070/984 |
| `prompt.py` | 11,952/11,251 → 8,134/7,683 | policy 4,260/3,997 |
| `paper_manifest.py` | 15,430/14,634 → 15,441/14,645 | no extraction claimed |

No before/after extraction measurement is claimed for no-op/deferred lanes.
The shared dirty checkout limits causal attribution; support files absent at
HEAD are not comparable before/after artifacts.

## Evidence gates

Evidence classes remain separate:

- Static: coordination JSON/JSONL parsed; changed production/support modules
  imported/compiled with Windows Python 3.12; fresh source/sidecar hash and
  semantic checks passed with EOL qualification.
- Focused: the recorded adjacent-lane command produced `2,485 passed, 17
  skipped`; `tests/test_agents_docs.py` produced `14 passed`; roadmap focused
  tests produced `5 passed`; the sidecar validator exited 0.
- CLI: `py -3.12 -m libreevolve --help` and `show --help` exited 0.
- Package/build: a sanitized Windows-native temporary copy passed
  `py -3.12 -m build --wheel --sdist` with wheel/sdist integrity checks.
  The checkout-local build probe was dependency-unavailable, so installation
  and runtime claims remain separate.
- Diff hygiene: conditional. Plain `git diff --check` exits 2 on inherited
  CRLF/trailing-whitespace representation; the EOL-aware check uses
  `git -c core.whitespace=cr-at-eol diff --check`.
- Secret scan: conditional/fail. The recorded detect-secrets pre-commit run
  exited 1 (hook exit 3) on known fixture/status candidates in
  `tests/core/test_feedback.py` and `papers/status_claim_inventory.json`; no
  secret values were printed and no baseline semantic change was retained.
- Terminal non-integration suite: PASS. The preserved exit-status run used the
  final source state and returned exit 0 with `6,555 passed, 27 skipped, 3
  deselected` in 1:31:27. An earlier complete green run was not used as the
  status authority because its wrapper exit field was not retained.
- Provider/integration: NOT RUN; credentials and authorization were not
  supplied.
- Native host, OCI, hostile-code security, distributed/resume, live runtime,
  and end-to-end coordinator/provider behavior: UNVERIFIED or NOT RUN.

## Findings and dependencies

Open or conditional findings are retained in [`FINDINGS.jsonl`](FINDINGS.jsonl)
and the all-field derived view [`FINDINGS_NORMALIZED.jsonl`](FINDINGS_NORMALIZED.jsonl):

- `MR-009`: JSONL repair/quarantine append is not one crash-atomic transaction.
- `MR-011`: paper rehydration needs fail-closed unsafe-path validation before
  target construction.
- `MR-012`: prompt-policy public signature and constant ownership need a
  compatibility decision.
- `MR-013`: archive mutation, event append, and history append have separate
  fault boundaries.
- `MR-014`: CLI artifact-document helper uses the wrong parent depth and can
  skip documentation validation.
- `MR-015`: roadmap corpus path filtering and `errors="ignore"` need an
  explicit corpus/decoding policy.
- `MR-010` and `MR-016` now have closed resolution rows after the source-state
  terminal pass and final report reconciliation.
- `MP-006`, `MP-011`, `MR-001`, `MR-002`, `MR-004`, and `MR-005` retain their
  measured seam, attribution, documentation, and publication boundaries.

Future dependency order is JSONL durability and artifact ownership before
best-artifact extraction; prompt/feedback retention before feedback or
meta-prompt extraction; config/YAML/loader ownership before broader
configuration movement; and paper cache path/transaction safety before paper
manifest extraction. Red-team conclusions and coordinator dispositions are in
[`RED_TEAM.md`](RED_TEAM.md).

## Terminal gate and exact Git state

Command:

```text
PYTHONDONTWRITEBYTECODE=1 /mnt/c/Windows/py.exe -3.12 -m pytest tests/ -m "not integration" --tb=short
```

Final terminal receipt: session `49390`, exit `0`, `6,555 passed, 27 skipped,
3 deselected`, duration `5487.20s (1:31:27)`. No claim is made from progress
output alone.

Final exact Git-status snapshot: `409` records: `275` tracked/index records,
`134` untracked records, and `0` staged paths. The status includes pre-existing
user-owned dirt and additive coordinator artifacts, so it is not an attribution
claim.

No external PR or release artifact exists. This handoff does not authorize
publication, merging, release, provider use, live execution, or security
certification.
