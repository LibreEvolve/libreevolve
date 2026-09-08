# Reading a saved result

LibreEvolve keeps several questions separate. A run can finish without
retaining an improved candidate, and a candidate can pass named checks without
being universally correct or optimal.

| Dimension | Read it as | Do not infer |
| --- | --- | --- |
| Run status | Whether the local run completed, was cancelled, or is incomplete. | Candidate validity or improvement. |
| Validity | Whether the candidate passed the named finite checks. | Universal correctness or safety. |
| Training quality | Quality on the training corpus used for search. | Accuracy, speed, or held-out quality. |
| Held-out quality | A separate check after selection is frozen. | A secret benchmark or protection from tuning. |
| Retention | Whether the candidate was retained in search state. | That it is the best possible program. |
| Usage | What local/provider usage was recorded. | Provider billing, remaining quota, or zero cost when data is missing. |
| Export | A newly verified local artifact. | Public publication, authenticity, or independent certification. |

## Inspecting a run

`show` reads the persisted history and manifest. A modern run reports its
runtime status and archive-retained selection. A legacy history-only directory
may still be displayed, but it is not a completed or verified preview run.
Missing artifacts, malformed JSON, unsafe paths, inconsistent policy records and
unfinished exports are errors, not evidence of success.

Use a fresh report path when calling `alpha report`. The command builds a new
report by reevaluating the baseline and the on-disk
`RUN/best_workspace/seed.py` candidate in timed local subprocesses, then
renders escaped HTML. It does not request a provider response or substitute a
candidate from saved history. If the workspace is missing or corrupt, the
report records that state rather than silently changing source.
Candidate execution still has host access and is not a security sandbox;
opening a local report is not a security review of arbitrary candidate source.

## Comparing outcomes

Compare valid baseline and candidate results on identical cases within one
split. Keep training and held-out results separate, and freeze selection before
the held-out check. The bin-packing quality score describes the named corpus;
it is not an accuracy or speed percentage. Invalid zero placeholders are not
zero-bin wins.

Possible honest outcomes include:

- no improvement on the checked split;
- fewer or more bins on the checked split when both results are valid;
- unchanged selected source;
- an invalid candidate;
- an incomplete or cancelled run; or
- no comparable result when required evidence is missing or inconsistent.

Do not turn a missing usage field into a zero-cost claim; missing usage is not
zero cost. Local call and runtime
limits are bounds on work, not hard token or dollar caps. Cancellation attempts
local cleanup and persistence; it does not prove that remote provider work or
subscription usage stopped.

## Export authority

Export freshly verifies the selected single-file candidate on named training and
held-out cases and records its SHA-256, source kind and source-run status. The
hash identifies bytes; it is not a signature, independent attestation,
optimality proof or permission to publish the source.

If `best_workspace/` differs from the saved history candidate, only
`alpha export` supports choosing `--source workspace` or `--source history`
explicitly. `alpha report` has no source selector and always checks the
on-disk workspace. Do not edit saved metadata to force an export. Existing
report files and export destinations are protected; choose new paths.

See [the saved artifact contract](run-artifacts.md) for the persisted file
inventory and [the quickstart](alpha-quickstart.md) for the canonical command
sequence.
