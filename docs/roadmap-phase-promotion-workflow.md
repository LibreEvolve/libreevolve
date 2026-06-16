# ROADMAP Phase Promotion/Demotion Workflow

This workflow applies when a major ROADMAP phase section is promoted, demoted,
deferred, or replaced across Near Term, Mid Term, and Longer Term scope.

## Required Phase-Change Evidence

Every phase change must preserve the stable ROADMAP phase section id and
explain why the previous phase label no longer matches current implementation
and evidence state.

The phase change must update these claim surfaces in the same pull request:

- `ROADMAP.md`
- `README.md`
- `papers/README.md`
- `docs/status.md`
- `docs/todo/roadmap.md`
- `docs/todo/Completed/roadmap.md`

The phase change must refresh these machine-readable evidence sidecars:

- `papers/roadmap_phase_sequence_boundary.json`
- `papers/roadmap_phase_dependency_graph_boundary.json`
- `papers/roadmap_phase_staleness_boundary.json`
- `papers/roadmap_phase_freshness_boundary.json`
- `papers/roadmap_claim_evidence_boundary.json`
- `papers/documentation_claim_inventory.json`
- `papers/status_claim_inventory.json`

The phase change must refresh the phase dependency graph and clear or route any
stale phase records before the phase move can be treated as current.

The phase change must run the paper manifest gate:

```bash
py -3.12 -m libreevolve.tools.paper_manifest --root . --require-local-pdfs --json
```

## Phase-Change Guardrails

A phase promotion or demotion is not valid if it only changes prose. It must
include ROADMAP, README, papers, status, TODO-ledger, and sidecar evidence
sufficient to make the new phase label true.

A phase promotion or demotion is not valid if prerequisite edges, active
blocking TODO refs, or stale phase records remain unresolved. Unresolved phase
evidence must stay in the active TODO ledger before the phase label can move.

This workflow is not a CI phase freshness gate, not an evidence-status refresh
report, and not an owner review signoff record. Those records must be produced
separately.
