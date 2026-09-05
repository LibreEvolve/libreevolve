# core/database.py inventory

Evidence state: measured/read-only Wave 1 report; characterization and
coupling review completed, with no production writer authorized in this wave.

Measured shape: 11,841 physical LOC, 11,137 logical/nonblank LOC, 309 module
functions, six classes and 47 methods. `ProgramDatabase` spans about 1,008
LOC. High-complexity hotspots include candidate-runner declaration validation
(389 LOC), startup manifest assembly (319), language-policy validation (266),
and archive/restore summary validators. The module has 11 direct importers and
115 distinct `config.<attribute>` references across 154 uses.

Ownership is distributed: `ProgramDatabase` is the compatibility façade;
`population/islands.py` owns cursors, migration, and sampling;
`population/map_elites.py` owns cell identity/replacement/eligibility; and
`population/program.py` owns identity, lineage, and workspace normalization.
Database also owns history/archive persistence, restore audits, manifests, and
cleanup, so a seam must not silently move those contracts.

Contract anchors include `VALID_THRESHOLD = 0.0` as pre-admission only,
distinct `cell_admitted`/`elite_retained`/`search_state_changed`/
`sampling_eligible` flags, cursor advancement only after search-state change,
canonical migration IDs, and audit-only archive replay.

Proposed seam: an `archive_boundary.py` adapter/codecs layer retaining
`ProgramDatabase` as façade, delegating island and MAP-Elites semantics to
their existing owners, and centralizing admission-result normalization,
immutable snapshots, archive events, and archive-state restore validation.
Generic history/failure/LLM/budget/manifest responsibilities remain in the
database façade or their current owners.
