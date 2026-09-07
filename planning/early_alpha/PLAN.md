# Early alpha delivery

Objective: install, optimize a small Python heuristic with a real model, inspect
quality and cost, and export an independently validated candidate without help.
Source objective: user attachment 303108df-80e6-4522-bfdb-951f4a3d3117/pasted-text-1.txt.
Baseline: 462443213b7391a6622d539a0564f14444e0cfce.
Branch: codex/early-alpha-20260905. Original shared checkout is preserved.
Original candidate: 8621ea69b4d8bc6c2b5aafec75b8a90056a6a338. That candidate
was merged into the private LibreEvolve/libreevolve master at
a906b53e138c5598edc40c12154f2d5f9635d6df. Final packaged source:
`8fdbf5132ed24b2960bde4c9f7acf14b28aadf59`; subsequent changes record validation
evidence and documentation only. The local workflow is trial-ready on the
Linux/WSL Luna/high reference route, not release-ready. No further publication
or CI run is requested. Older
remote-state statements are historical, not current-head synchronization claims.
Reliability follow-up commit
`b2159939` synchronizes POSIX verification-worker descendant cleanup, adds
Darwin `kqueue` observation, and fails closed when safe cleanup evidence is
unavailable. Its exact package artifacts and Windows Python 3.12.10
clean-install smoke are recorded in `EVIDENCE.md`.

## Milestones and acceptance evidence

| Milestone | Owner | Dependencies | Required evidence | State |
| --- | --- | --- | --- | --- |
| Bin-packing example | Galileo | baseline | valid next-fit seed, deterministic training/held-out corpora, negative correctness tests, measured positive calibration | local evaluator passed |
| Init and preflight | coordinator | example | clean template creation, bounded config, useful failures, no network during offline checks | local workflow passed |
| Reliability | Mill + coordinator + independent verifier | baseline | reproduce docs helper fault, inspect cancellation/persistence and prompt compatibility, regression tests | final six alpha/Codex/ensemble suites: 508 passed, 1 platform skip; meaningful cancellation/descendant/persistence faults covered |
| Report and export verification | Plato + coordinator + independent verifier | example, runtime inspection | baseline/best, held-out checks, diff, usage/cost/status; failure report; HTML escaping and artifact binding | completed cohort, diagnostic and final-smoke exports independently passed 55 training / 30 holdout cases; cancelled/failed/partial controls distinguished |
| Repeated real runs | coordinator | supported workflow, authorized OAuth subscription usage | all attempts retained, independent seeds, comparable baseline/export reevaluation, actual usage with unknown charges distinguished | three completed Luna/high comparison runs improved; all 11 optimization run attempts + 3 probes retained; 261,796 known tokens, incomplete usage/unknown charges |
| Package | coordinator + independent verifier | implementation | exact candidate commit, wheel/sdist, coverage/hashes, clean installs and CLI workflow | final 8fdbf513 archives + installed Linux package byte-match 455 files; Linux real workflow and Windows 13-command offline workflow passed; CI excluded |
| External usability | coordinator + participants | installed workflow | 3–5 users, time/errors/help/export comprehension, approximately 30 minutes | trial materials prepared; participant evidence pending |

Initial declared reference environment: Windows with Python 3.12. Additional
platform support requires its own installed-package evidence. The initial
provider path was OpenAI with caller-supplied pricing. The authorized live lane
is now Codex OAuth with Luna; Linux/WSL Python 3.12.13 installed-package probes
passed. Native Windows currently has offline package evidence, not a live
Codex run. Model access and charges are not inferred from local login alone.

## Evidence rules

Use the existing engine, budget controls, run/show commands, and exporters.
Evaluator and held-out inputs remain outside candidate editable workspaces.
Local subprocess evaluation is not a hostile-code security sandbox.
Paper retrieval is outside onboarding; no hosted service or pending-work resume
claim. User trial materials can be prepared without contacting participants.

No live call is authorized by a default config. The user authorized Luna through
Codex OAuth; the additional API allocation is $0, subscription use is permitted,
and charges/quota are not exposed by the CLI. The protocol and all attempts are
in `CODEX_OAUTH_TRIAL.md` and `OAUTH_ATTEMPTS.json`. API-key billing fallback is
not authorized. Estimated token-price budgets are not billing guarantees.

The release checklist, complete relevant regressions, interruption tests,
installed-package runs, real-model attempts and independent user trials are
separate evidence classes. CI is explicitly excluded; external user-trial
results are explicitly pending as allowed by the objective. Do not substitute
scripted mutations for real-model evidence.
Final acceptance, exact artifact hashes, test failures excluded under the CI
instruction, model outcomes and limits are in [FINAL_HANDOFF.md](FINAL_HANDOFF.md).
Local engineering gates are satisfied under the revised scope. Public
publication, deployment and participant contact require separate authority.
