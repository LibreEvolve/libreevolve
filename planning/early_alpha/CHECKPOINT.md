# Current continuation checkpoint

The early-alpha goal remains active because the required real-provider and
external-usability gates are not complete. This checkpoint is the current
state, not an authorization to spend or contact participants.

## Exact candidate and repository state

- The original packaged candidate was
  `8621ea69b4d8bc6c2b5aafec75b8a90056a6a338`; the implementation and package-
  validation tip is `eb4d5eaec8fe0a460c7e121d2b9bcbf1a78a0b06`.
- Candidate branch: `codex/early-alpha-20260905`. The private remote branch
  currently points to the implementation tip; the clean local checkout has a
  later documentation-only reconciliation commit and is intentionally one
  commit ahead. It is not merged into the private repository's `master`.
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

Source commit `b2159939` is the reliability follow-up to the packaged
candidate. It synchronizes POSIX verification-worker descendant
cleanup, adds a non-reaping Darwin `kqueue` observer, fails closed when safe
exit observation is unavailable, and records group/job cleanup failures. The
five alpha regression files pass 123 tests with 1 Windows-only skip. A Windows
Python 3.12 package/provenance build from exact follow-up HEAD
`b215993954368b1d357d3e19b9b94ed0e6140b5b` is preserved under
`dist/b2159939/`; its wheel/sdist/provenance hashes and clean Windows
provider-free workflow are recorded in `EVIDENCE.md`. The follow-up is on the
private feature branch and remains unmerged into `master`.

The current exact package smoke was rebuilt from docs/CI-anchor commit
`2a472c2d231fe4157f2c6afcb3e309978ccde4f8` under `dist/2a472c2d/` and
installed into a separate clean Windows Python 3.12.10 venv. Its hashes and
the provider-free onboarding/report/export result are recorded in
`EVIDENCE.md`; the branch tip after that package build contains only the
evidence-record update.

The current local documentation tip `6fba9e27bde5738f808109d7ab9fc808b89c481c`
also passed the five alpha bin-packing/onboarding/reliability/report/workflow
files: 123 passed and 1 Windows-only skip in 814.46 seconds under an isolated
Linux Python 3.12.13 environment using `pypdf==6.10.2`. This is an additional
provider-free source regression check; it does not provide real-model or user
trial evidence.

An additional Windows Python 3.12.10 package smoke was built from local tip
`c2a0f8cade18402b75046d487ee0bf81dd449471` before this checkpoint's later
documentation edits. Artifacts are under `dist/c2a0f8ca/` with wheel SHA-256
`a3e4ac5c62f897bd8fe9f7a900877b1aa4bc6493f4c7612e471813b1c9e4d17a`, sdist
SHA-256 `6798eeb3e7cd75fa3dfee5c275411265786265fd0620d5add30f465a4d535955`,
and provenance SHA-256
`b1ba3f7631a5da6e9598d808d5350c4854ee0589bcfeb110f57d37d79d9325d9`. The
clean installed venv passed `pip check`, both CLI help entrypoints, offline
init/doctor, zero-generation run/show/report, and verified export; training and
held-out correctness remained true at `0.8016472203157172` and
`0.8121645796064401`. This is provider-free retained-seed evidence.
