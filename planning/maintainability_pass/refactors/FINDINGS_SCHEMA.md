# Normalized findings schema

`FINDINGS.jsonl` is append-only. Historical rows remain intact; when a
finding's evidence or disposition changes, a superseding row is appended
instead of rewriting the source ledger. Every current-run update uses these
fields:

```text
id, supersedes, severity, state, evidence_state, owner,
path, symbol, summary, impact, acceptance, disposition,
verification, dependencies
```

`path` and `symbol` identify the concrete seam or artifact. `impact` states
the consequence, `acceptance` is the evidence gate, `disposition` is the
current action (`defer`, `no-op`, `repair-pending`, `closed`, or
`conditional`), and `verification` records exact evidence or `unverified`.
The effective record for a finding is the latest row for its ID/supersession
chain; no historical row is silently deleted.

`FINDINGS_NORMALIZED.jsonl` is a derived, machine-auditable view of every
source-ledger row. It always materializes the literal `evidence`, `path`,
`symbol`, and `disposition` fields (using `not-recorded`, `legacy`, or an
explicit evidence state where the historical row did not carry the newer
field). It is not a replacement for the append-only source ledger and does not
pretend that legacy rows have stronger evidence than they actually do.

The current run intentionally retains open/conditional findings for oversized
modules, inherited dirty state, deferred durability/safety questions, the
terminal-gate history, unmerged publication, and unavailable live/native
boundaries. A green focused test does not close a finding whose acceptance
requires build, runtime, native, provider, OCI, or end-to-end evidence.
