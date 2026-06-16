# ROADMAP Non-Goal Promotion Workflow

This workflow applies when a ROADMAP non-goal is removed, completed, or intentionally promoted into active implementation scope.

## Required Promotion Evidence

Every intentional non-goal promotion must update the stable non-goal id record
and explain why the former non-goal is now supported implementation scope.

The promotion change must update these claim surfaces in the same pull request:

- `ROADMAP.md`
- `README.md`
- `papers/README.md`
- `docs/status.md`
- `docs/todo/roadmap.md`
- `docs/todo/Completed/roadmap.md`

The promotion change must refresh these machine-readable evidence sidecars:

- `papers/roadmap_non_goal_contradiction_boundary.json`
- `papers/roadmap_non_goal_drift_boundary.json`
- `papers/roadmap_non_goal_ci_promotion_gate_boundary.json`
- `papers/roadmap_non_goal_markdown_scan_boundary.json`
- `papers/roadmap_non_goal_plugin_docstring_boundary.json`
- `papers/roadmap_non_goal_runtime_metadata_boundary.json`

The promotion change must run the paper manifest gate:

```bash
py -3.12 -m libreevolve.tools.paper_manifest --root . --require-local-pdfs --json
```

## Promotion Guardrails

A promotion is not valid if it only changes prose. It must include code,
runtime metadata, tests, paper sidecars, and TODO-ledger evidence sufficient to
make the promoted support claim true.

A promotion is not valid if it leaves contradictory support claims unresolved.
Contradictory support claims must be routed to the active TODO ledger before
the non-goal can be promoted.

This workflow is not an owner review signoff record. Owner review signoff must
be recorded separately.
