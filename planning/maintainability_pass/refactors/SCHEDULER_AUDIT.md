# Scheduler and quiescence audit

Captured: `2026-09-05T03:40:10-04:00`
Sources: `FILE_MATRIX.json`, `AGENT_REGISTRY.jsonl`, and the derived
`SCHEDULER_EVENTS.jsonl`.

## Assertions

- Matrix lanes: 17 unique IDs; PR-index rows: 17 unique IDs; no duplicate lane
  IDs or primary-file writer conflicts.
- Configured child capacity is 50 and configured maximum nesting depth is 3.
  All recorded lifecycle projections are direct root dispatches at
  `execution_depth: 1`; observed maximum depth is 1.
- Replaying the append-only lifecycle projection in event order gives a peak
  of 15 active agent IDs and zero active IDs at this audit's quiescence point.
  The latest row for every registered agent is closed; this is the scheduler
  closure assertion, not a claim that the historical event stream has no
  duplicate lifecycle rows.
- Every matrix lane has at most one writer agent for its primary path. The
  source and generated-sidecar roadmap lanes have distinct primary files and
  the source lane depends on the sidecar lane.
- `SCHEDULER_EVENTS.jsonl` contains 170 append-history projections. Its
  `observed_at` value is coordination-derived at capture time because the
  registry rows do not carry native tool timestamps; it must not be read as
  per-agent wall-clock telemetry.

## Temporal limitation

The registry proves ownership, lifecycle closure, and the observed direct
dispatch hierarchy, but it does not contain scheduler event timestamps or a
distributed lock trace. Therefore temporal non-overlap of historical writers
is supported by disjoint matrix ownership and lifecycle order, not certified
by a native scheduler trace. No writer was left active at quiescence, and all
new large-file reviews were read-only.

## Reproduction receipts

```text
jq -c '{lanes:(.lanes|length),duplicate_lane_ids:(.lanes|map(.lane_id)|group_by(.)|map(select(length>1)|.[0])),writer_conflicts:(.lanes|map(select(.writer_agent_id!=null)|{primary_path,writer_agent_id})|group_by(.primary_path)|map(select(length>1)))}' planning/maintainability_pass/refactors/FILE_MATRIX.json
jq -s '{rows:length,unique_lane_ids:(map(.lane_id)|unique|length),duplicate_lanes:(map(.lane_id)|group_by(.)|map(select(length>1)|.[0])),not_opened:(map(select(.pr_status=="not-opened"))|length)}' planning/maintainability_pass/refactors/PR_INDEX.jsonl
jq -s 'reduce .[] as $e ({active:{},peak:0}; if $e.status=="active" then .active[$e.agent_id]=true elif ($e.status|startswith("closed")) then .active[$e.agent_id]=false else . end | .n=(.active|map(select(.==true))|length) | .peak=(if .n>.peak then .n else .peak end) | .active_at_end=(.active|map(select(.==true))|length)) | {peak_active_observed:.peak,quiescent_active:.active_at_end}' planning/maintainability_pass/refactors/SCHEDULER_EVENTS.jsonl
```
