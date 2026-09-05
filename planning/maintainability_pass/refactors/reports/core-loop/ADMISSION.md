# `core/loop.py` Admission and Accounting Slice

Agent: `01a069ce-af6d-7452-986f-59c9cfc553a9`
Status: Wave 1 read-only inventory complete; tests not executed; evidence
`source-observed`, `test-observed` (assertions inspected), `docs-confirmed`,
`proposed`, `unverified`.

Stable anchors include threshold/loop entry near 163/1084, candidate commit
near 1804/3034, `ProgramDatabase.admit()` near `database.py:647`, archive
decision fields in `population/map_elites.py:431-503`, and budget/reward logic
near `budget.py:248/320/461` and `loop.py:49567-49602`.

The admission state must remain three-valued: `admitted` means some retained
archive state changed; `cell_admitted` means the primary MAP-Elites cell was
entered/replaced; `sampling_eligible` means primary occupied-cell eligibility.
Validity is exact boolean `True`, fitness is finite and non-boolean, and the
threshold gate is `0.0`; cell replacement can still return
`not_improving_cell`. Invalid, below-threshold, and non-retained candidates
still have distinct history, failure, budget, backend-reward, and prompt-
reward behavior. Backend reward is admission-gated but not cell-gated;
prompt reward is recorded after history logging and is not admission-gated.

Proposed seam: a finalized-candidate commit coordinator shared by sequential
and async paths, returning admission, optional failure record, backend reward,
and prompt reward while preserving the current order: admit; attach async
ordering; conditionally log failure; compute backend reward; attach LLM calls;
`db.log()`; record prompt reward. Keep archive policy, budget ownership, and
prompt database ownership in their current modules. Current docs wording about
selection score before plugin hooks appears stale relative to source/tests and
must be reconciled before a seam changes that order.
