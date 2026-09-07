# Early alpha delivery

Objective: install, optimize a small Python heuristic with a real model, inspect
quality and cost, and export an independently validated candidate without help.
Source objective: user attachment 303108df-80e6-4522-bfdb-951f4a3d3117/pasted-text-1.txt.
Baseline: 462443213b7391a6622d539a0564f14444e0cfce.
Branch: codex/early-alpha-20260905. Original shared checkout is preserved.
Original candidate: 8621ea69b4d8bc6c2b5aafec75b8a90056a6a338. That candidate
was merged into the private LibreEvolve/libreevolve master at
a906b53e138c5598edc40c12154f2d5f9635d6df. Current feature-branch tip:
`04b00a60c2056ef5224918e01dcc92231426e4bd` is the current packaged candidate.
Local follow-up work adds Codex cancellation hardening after a reproduced live
orphan-process fault. No further publication or CI run is requested. Older
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
| Reliability | Mill + coordinator | baseline | reproduce docs helper fault, inspect cancellation/persistence and prompt compatibility, regression tests | 496 broad loop/reliability tests pass, 2 skip |
| Report and export verification | Plato + coordinator | example, runtime inspection | baseline/best, held-out checks, diff, usage/cost/status; failure report; HTML escaping and artifact binding | 33 combined tests pass, real offline CLI smoke passes |
| Repeated real runs | coordinator | supported workflow, authorized OAuth subscription usage | all attempts retained, independent seeds, comparable baseline/export reevaluation, actual usage with unknown charges distinguished | nine optimization invocations failed/interrupted; three probes passed; no generated candidate yet; next lower-reasoning diagnostic follows cancellation fix |
| Package | coordinator + independent verifier | implementation | exact candidate commit, wheel/sdist, coverage/hashes, clean installs and CLI workflow | 04b00a60 byte coverage and Windows offline workflow passed; next source follow-up needs repackaging; CI excluded by user instruction |
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
Required incomplete gates keep the goal active. Public publication and deployment
require authorization; a local candidate commit is part of packaging evidence.
