# Current continuation checkpoint

The early-alpha goal remains active because the required real-provider and
external-usability gates are not complete. This checkpoint is the current
state, not an authorization to spend or contact participants.

## Exact candidate and repository state

- Candidate source commit: `8621ea69b4d8bc6c2b5aafec75b8a90056a6a338`.
- Candidate branch: `codex/early-alpha-20260905`, clean and pushed to the
  private `LibreEvolve/libreevolve` repository.
- Merge commit: `a906b53e138c5598edc40c12154f2d5f9635d6df` on that repository's
  `master`; PR #1 is `MERGED`.
- The shared `CompleteTech-LLC-AI-Research/libreevolve` checkout is a separate,
  heavily dirty checkout and was not modified.

## Verified offline and packaging evidence

- Exact-candidate local non-integration suite: 6,640 passed, 27 skipped,
  3 deselected, exit 0. This is source-checkout evidence.
- Exact-candidate alpha workflow and reliability/report tests were previously
  recorded passing; no provider calls were made.
- Windows Python 3.12 build from the exact candidate produced:
  - wheel SHA-256: `8271db759a94a5a637539a65d2d9138966a6958c520feaf4f0801e9a3ba7871f`
  - sdist SHA-256: `b5626d897273527e2378236a4fc432d4a8448ebc14fc6559884fee2d905a830d`
  - provenance SHA-256: `bc35ef56f6c50ff234e01d4d7783bbe91188dc7fb27d05924b284fe43a876548`
- The wheel and sdist each contain all 455 files under `libreevolve/`; both
  `libreevolve --help` and `python -m libreevolve --help` passed in the
  isolated venv.
- A fresh Windows Python 3.12 venv without system packages installed the
  exact wheel; `pip check` passed. The documented offline init, doctor, seed
  run, show, HTML report, and verified export all exited 0.
- Fresh installed export SHA-256:
  `a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507`.
  Independent training and held-out correctness both passed; scores were
  `0.8016472203157172` and `0.8121645796064401`. This is seed evidence, not
  evidence of LLM-guided improvement.

## External gates

- Post-merge GitHub runs `34019445028` (Tests) and `34019445056` (Installed
  Alpha) completed before executing jobs because the account has a payment or
  spending-limit failure. They are failures, not green CI or code evidence.
- Automatic `push`, `pull_request`, and scheduled CI triggers are now paused
  temporarily in the follow-up commit; both workflows remain manually
  dispatchable. Restore those triggers after billing is resolved.
- Real-model validation remains pending an explicitly authorized aggregate
  spending cap, a currently available model, and credential access. The
  three-run protocol uses independent seeds 17, 29, and 43 and retains every
  attempt.
- The 3–5 developer usability trial is prepared but no participants were
  contacted and no feedback was collected.

## Classification and next actions

The candidate is an engineering preview, not a trial-ready or release-ready
alpha. Resume only after the external state changes: resolve GitHub billing,
authorize a bounded provider cohort, and authorize participant contact. Then
rerun the exact-head CI, execute the three documented provider trials, and
collect the usability records before revisiting completion.

## Local follow-up after the merged candidate

Source commit `2b7b7e30` is a local, unpushed reliability follow-up to the
packaged candidate. It synchronizes POSIX verification-worker descendant
cleanup; the focused cleanup parameters pass 3/3 and the combined report /
reliability subset passes 62 tests with 1 Windows-only skip. A Linux Python
3.12 wheel/sdist/provenance build from follow-up HEAD `aa973ff3` is preserved
under `dist/aa973ff3/`; its wheel/sdist/provenance hashes are recorded in
`EVIDENCE.md`. The recorded Windows artifacts still identify `8621ea69`, and
the follow-up has not been pushed or installed on the declared Windows
reference environment.
