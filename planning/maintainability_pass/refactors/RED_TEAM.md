# Independent red-team review

Captured: 2026-09-05
Scope: integrated implementation seams, coordination evidence, packet
completeness, and release-boundary claims.

## Reviewers

### Bernoulli — implementation/seam review

Agent `01a0705b-70f9-7000-8923-b4ec0e5667fd` performed a read-only integrated
review and reported `closed-conditional`. Twelve focused boundary tests passed.
No production or test files were changed by the reviewer.

Findings:

- `MR-014` (high): `libreevolve/core/run_inspection.py:440-445` resolves the
  documentation root from `parents[1]` instead of `parents[2]`. The resulting
  `run_artifacts_doc_text()` value can be `None`, so artifact-schema
  documentation checks are skipped. This is a separate follow-up repair.
- `MR-011` (high): paper rehydration constructs an unsafe `file` target before
  path validation. The finding remains open and overlaps the paper safety
  boundary.
- `MR-016` (high): the former final-report lane/count snapshot was stale after
  the two auxiliary roadmap lanes and must be reconciled before handoff.
- `MR-015` (medium): the roadmap scanner's path filter can exclude any path
  containing `planning`, and `errors="ignore"` can hide invalid UTF-8. The
  corpus and decoding boundary need a separate decision.
- `MR-012` (medium): the prompt policy API signature in the source differs from
  an earlier report. The public signature must be characterized before more
  extraction.
- Archive mutation/event persistence and JSONL append durability remain
  residual integrated seam risks; these are retained by `MR-013` and `MR-009`.

Coordinator disposition: record the concrete findings in `FINDINGS.jsonl`,
keep `MR-011`, `MR-012`, `MR-013`, and `MR-009` open/deferred, add the docs
helper and scanner-boundary findings, and do not authorize another production
writer in this pass.

### Lagrange — evidence/coordination review

Agent `01a0705b-74bc-7aa1-84fc-3af0b386c6ca` performed a read-only evidence
review and reported `closed-conditional`. No repository source or test files
were changed by the reviewer.

The review identified these coordination gaps, all retained as conditional
handoff work:

- the authority log initially lacked root `README.md` and `ROADMAP.md`
  receipts, timestamps, hashes, and command evidence;
- topology and temporal exclusivity needed explicit assertions rather than
  only prose; registry lifecycle rows needed depth/timestamp provenance;
- the normalized slice ledger lacked literal imports, schemas,
  characterization-test, and test-result fields, and large-file reviews had
  fewer than the required four specialists;
- verifier freshness, source-lane reconciliation, and report-to-agent
  coverage were incomplete;
- packet fields were inconsistent, several packets lacked exact executable
  commands/results, and the roadmap sidecar lacked an inventory report;
- findings needed normalized path/symbol/evidence/disposition fields and an
  effective-record policy;
- secret, diff, build, and terminal claims needed explicit conditional
  boundaries; the terminal run needed a preserved final exit status;
- the final report had stale 15-lane, count, and corpus claims.

Coordinator actions: root-document receipts, a scheduler audit, literal slice
schema fields, three additional large-file specialists, a sidecar inventory,
packet evidence indexing, normalized findings, and the preserved exact
terminal run are being completed before final reconciliation. These actions
repair evidence bookkeeping only; they do not turn focused/static evidence
into runtime, native, provider, OCI, or end-to-end proof.

## Gate disposition

The orchestration remains `conditional-unmerged`. The red-team reviews do not
authorize publication, merging, broad staging, or additional production
extraction. Open findings and any unverified gate remain visible in
`FINAL_REPORT.md` and `PR_INDEX.jsonl`.
