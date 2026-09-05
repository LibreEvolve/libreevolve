# Refactor packet contract

Each lane packet is an internal, non-publication handoff record. It must name
the lane and primary file, baseline checkout, proposed branch (if any), exact
changed-path allowlist, scope and non-goals, dependency lanes, writer and
fresh non-authoring verifier IDs, characterization and verification commands
with exit statuses, before/after measurements, preserved contracts, risks,
rollback scope, and external publication status.

The packet is descriptive evidence, not a patch or a PR. An external branch,
PR, merge, release, or broad staging operation requires separate explicit
authorization. A packet may record `not run`, `unverified`, `no-op`, or
`conditional`; those values must not be upgraded by inference from a focused
test.

`PACKET_EVIDENCE_INDEX.jsonl` is the coordinator's normalized cross-packet
index. It repeats the authoritative matrix identity and records whether the
packet contains an exact command/result receipt, a verifier, and the current
dependency state. It intentionally exposes incomplete historical packets
instead of silently filling missing evidence.

Auxiliary lanes use the same contract. The roadmap source lane consumes the
generated sidecar lane; the sidecar has its own primary, inventory, reports,
packet, writer, and verifier.
