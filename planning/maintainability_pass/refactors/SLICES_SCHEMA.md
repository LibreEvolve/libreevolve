# Slice record schema and boundary policy

`SLICES.jsonl` contains 33 unique AST/symbol-oriented records: the original
loop/persistence/prompt/evidence/configuration/loader inventory plus the six
large-file specialist slices, three additional large-file specialist slices
(bringing database, prompt, and paper-manifest coverage to four reviews each
including the inventory review), and the two roadmap artifact/source slices
added in this continuation. Records are additive coordination data, not
permission to edit a primary file.

Every record carries:

- stable `slice_id`, `primary_path`, and symbol/range `anchors`;
- `callers`, `mutable_state`, `serialized_contracts`, `seam`, and
  `dependency_direction`;
- `neighbors`, `unresolved_questions`, and an explicit
  `boundary_overlap_review`;
- specialist identity, `read_only`, status/evidence, and characterization
  requirements;
- literal `imports`, `schemas`, `characterization_tests`, `tests_executed`,
  and `test_result` fields, with non-execution stated explicitly where a
  source-only review relied on lane-level evidence;
- implementation readiness and report paths, with writer/verifier identities
  where known.

Empty arrays/null paths are deliberate only where the current source/report
pass did not establish the fact; the corresponding unresolved question keeps
that absence visible. A generic overlap sentence means the adjacent review is
still pending and the slice is not extraction-ready. The detailed six
specialist records and lane reports provide concrete callers, state, schemas,
seams, and unresolved questions for the currently highest-risk files.

Adjacent slices must be reviewed together before implementation. In
particular, loop admission/persistence, database admission/restore,
prompt-policy/feedback, paper inventory/rehydration, and roadmap source/sidecar
boundaries are not independent merely because their symbols occupy separate
ranges.
